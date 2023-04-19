import { createConnection, createPool, Pool } from 'mysql2/promise'
import { wait } from './misc'

/**
 * Create database connection
 * @return Database connection
 * @throws Will throw an error if a required environment variable is missing
 */
export function createDatabaseConnection(): Pool {
    for (const name of ['DB_HOST', 'DB_USER', 'DB_NAME']) {
        if (typeof process.env[name] === 'undefined') {
            throw new Error(`Missing required environment variable "${name}"`)
        }
    }
    return createPool({
        host: process.env.DB_HOST,
        user: process.env.DB_USER,
        password: process.env.DB_PASS,
        database: process.env.DB_NAME,
        waitForConnections: true,
        connectionLimit: 10,
        queueLimit: 0,
        timezone: 'Z',
    })
}

/**
 * Wait for database to be ready
 * @return Callback when ready
 */
export async function waitForDatabase(): Promise<void> {
    while (true) {
        try {
            const conn = await createConnection({
                host: process.env.DB_HOST,
                user: process.env.DB_USER,
                password: process.env.DB_PASS,
                database: process.env.DB_NAME,
            })
            await conn.end()
            break
        } catch (_) {
            // Database is not ready yet
        }
        await wait(5000)
    }
}
