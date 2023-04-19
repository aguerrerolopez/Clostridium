import { Pool } from 'mysql2/promise'

export async function apply(db: Pool): Promise<void> {
    if (process.env.MYSQL_DATABASE) { // Only if running inside container
        await db.query('CREATE USER ?@? IDENTIFIED BY ?', ['appuser', '%', ''])
        await db.query('GRANT SELECT, INSERT, UPDATE, DELETE ON appdb.* TO ?@?', ['appuser', '%'])

        await db.query('CREATE USER ?@? IDENTIFIED BY ?', ['appuser_ro', '%', ''])
        await db.query('GRANT SELECT ON appdb.* TO ?@?', ['appuser_ro', '%'])
    }
}
