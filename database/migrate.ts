import fs from 'fs'
import { createDatabaseConnection, waitForDatabase } from './src/database'
import { getDatabaseRevision } from './src/revisions'

(async () => {
    const MIGRATIONS_DIR = `${__dirname}/migrations`

    // Initialize script
    console.log('[i] Waiting for database to be ready...')
    await waitForDatabase()
    const db = createDatabaseConnection()

    // Get current migration
    const current = await getDatabaseRevision(db)
    if (current) {
        console.log(`[i] Database schema is currently at "${current.name}" (rev. ${current.number})`)
    } else {
        console.log('[i] Database has not been initialized yet')
    }

    // Get pending migrations
    const migrations = fs.readdirSync(MIGRATIONS_DIR)
        .filter(filename => filename.endsWith('.ts'))
        .filter(filename => Number(filename.split('-', 1)[0]) > (current?.number || -1))
        .sort()

    // Apply pending migrations
    for (const filename of migrations) {
        const migration = await import(`${MIGRATIONS_DIR}/${filename}`)
        console.log(`[i] Applying pending migration "${filename}"...`)
        await migration.apply(db)
    }

    // Update metadata
    if (migrations.length > 0) {
        const latestRevision = migrations[migrations.length-1].replace(/\.ts$/, '').split('-')
        await db.query(
            `CREATE TABLE IF NOT EXISTS _metadata (
                field VARCHAR(50) NOT NULL,
                value VARCHAR(100) NOT NULL,
                PRIMARY KEY (field)
             )`
        )
        await db.query(
            `INSERT INTO _metadata (field, value)
             VALUES (?, ?), (?, ?)
             ON DUPLICATE KEY UPDATE value=VALUES(value)`,
            [
                'rev_number', latestRevision[0],
                'rev_name', latestRevision.slice(1).join('-'),
            ]
        )
    }

    // Stop script execution
    console.log('[i] Finished applying pending migrations')
    await db.end()
})()
