import { Pool, RowDataPacket } from 'mysql2/promise'

interface DatabaseRevision {
    number: number
    name: string
}

/**
 * Get current database revision
 * @return Database revision
 */
export async function getDatabaseRevision(db: Pool): Promise<DatabaseRevision | null> {
    try {
        let number = 0
        let name = ''
        const [rows] = await db.query<RowDataPacket[]>(
            'SELECT * FROM _metadata WHERE field IN (?, ?)',
            ['rev_number', 'rev_name']
        )
        for (const row of rows) {
            if (row.field === 'rev_number') {
                number = Number(row.value)
            } else {
                name = row.value
            }
        }
        return {name, number}
    } catch (_) {
        // No revision data
    }
    return null
}
