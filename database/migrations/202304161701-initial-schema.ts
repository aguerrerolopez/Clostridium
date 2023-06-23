import { Pool } from 'mysql2/promise'

export async function apply(db: Pool): Promise<void> {
    await db.query(
        `CREATE TABLE accounts (
            id                     INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            email                  VARCHAR(300) CHARACTER SET utf8mb4 NOT NULL,
            firstname              VARCHAR(100) CHARACTER SET utf8mb4 NOT NULL,
            lastname               VARCHAR(100) CHARACTER SET utf8mb4 NOT NULL,
            \`password\`           VARCHAR(255) CHARACTER SET ascii NOT NULL,
            verification_token     CHAR(40) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'Token sent to verify email address',
            password_reset_token   CHAR(40) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'Token sent to reset password',
            created_at             DATETIME NOT NULL,
            updated_at             DATETIME NOT NULL,
            last_seen_at           DATETIME NOT NULL,
            verification_sent_at   DATETIME DEFAULT NULL COMMENT 'When email verification token was last sent',
            verified_at            DATETIME DEFAULT NULL COMMENT 'When email address was verified',
            password_reset_sent_at DATETIME DEFAULT NULL COMMENT 'When password reset token was last sent',
            UNIQUE (email),
            UNIQUE (verification_token)
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
    await db.query(
        `CREATE TABLE uploads (
            id          CHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL PRIMARY KEY,
            batch_id    CHAR(16) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
            account     INT UNSIGNED NOT NULL,
            sample      BINARY(32) NOT NULL COMMENT 'samples.digest',
            name        VARCHAR(200) CHARACTER SET utf8mb4 NOT NULL,
            label       ENUM('027', '181', 'other') CHARACTER SET ascii DEFAULT NULL,
            uploaded_at DATETIME NOT NULL,
            labeled_at  DATETIME DEFAULT NULL,
            UNIQUE (account, sample),
            INDEX (account),
            INDEX (label),
            INDEX (uploaded_at)
        ) ENGINE=Aria DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin`
    )
    await db.query(
        `CREATE TABLE samples (
            digest                   BINARY(32) NOT NULL PRIMARY KEY COMMENT 'Custom SHA-256 digest of contents',
            sample_id                BINARY(16) NOT NULL COMMENT 'External, as reported by the sample',
            target_id                BINARY(16) NOT NULL,
            position                 CHAR(3) CHARACTER SET ascii NOT NULL,
            spectrum_size            SMALLINT UNSIGNED NOT NULL COMMENT 'In number of measured time periods',
            instrument_serial_number VARCHAR(20) CHARACTER SET ascii NOT NULL,
            instrument_type          TINYINT UNSIGNED NOT NULL,
            digitizer_type           TINYINT UNSIGNED NOT NULL,
            flexcontrol_version      VARCHAR(20) CHARACTER SET ascii NOT NULL,
            aida_version             VARCHAR(20) CHARACTER SET ascii NOT NULL,
            size                     INT UNSIGNED NOT NULL COMMENT 'In bytes, of the ZIP archive',
            acquired_at              DATETIME(3) NOT NULL,
            calibrated_at            DATETIME(3) NOT NULL,
            analyzed_at              DATETIME DEFAULT NULL,
            analyzer_version         SMALLINT UNSIGNED DEFAULT NULL,
            dblfs_result             ENUM('027', '181', 'other') CHARACTER SET ascii DEFAULT NULL,
            dblfs_confidence         DECIMAL(7,6) UNSIGNED DEFAULT NULL,
            dt_result                ENUM('027', '181', 'other') CHARACTER SET ascii DEFAULT NULL,
            dt_confidence            DECIMAL(7,6) UNSIGNED DEFAULT NULL,
            lr_result                ENUM('027', '181', 'other') CHARACTER SET ascii DEFAULT NULL,
            lr_confidence            DECIMAL(7,6) UNSIGNED DEFAULT NULL,
            rf_result                ENUM('027', '181', 'other') CHARACTER SET ascii DEFAULT NULL,
            rf_confidence            DECIMAL(7,6) UNSIGNED DEFAULT NULL,
            INDEX (instrument_serial_number),
            INDEX (acquired_at),
            INDEX (analyzer_version)
        ) ENGINE=Aria DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin`
    )
}
