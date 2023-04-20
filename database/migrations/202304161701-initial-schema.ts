import { Pool } from 'mysql2/promise'

export async function apply(db: Pool): Promise<void> {
    await db.query(
        `CREATE TABLE accounts (
            id           INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            email        VARCHAR(300) CHARACTER SET utf8mb4 NOT NULL,
            firstname    VARCHAR(100) CHARACTER SET utf8mb4 NOT NULL,
            lastname     VARCHAR(100) CHARACTER SET utf8mb4 NOT NULL,
            \`password\` VARCHAR(255) CHARACTER SET ascii NOT NULL,
            created_at   DATETIME NOT NULL,
            updated_at   DATETIME NOT NULL,
            last_seen_at DATETIME NOT NULL,
            verified_at  DATETIME DEFAULT NULL COMMENT 'When email address was verified',
            UNIQUE (email)
        ) ENGINE=Aria DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin`
    )
    await db.query(
        `CREATE TABLE \`sessions\` (
            token        CHAR(56) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
            account      INT UNSIGNED NOT NULL,
            ip_address   VARCHAR(45) CHARACTER SET ascii NOT NULL,
            user_agent   VARCHAR(300) CHARACTER SET ascii NOT NULL,
            created_at   DATETIME NOT NULL,
            last_seen_at DATETIME NOT NULL,
            refreshes_at DATETIME NOT NULL,
            expires_at   DATETIME NOT NULL
        ) ENGINE=Aria DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin`
    )
}