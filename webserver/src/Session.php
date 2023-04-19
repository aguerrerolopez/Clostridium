<?php
namespace App;

use RuntimeException;

class Session {
    /**
     * Logged account ID, `false` if unauthenticated or `null` if not initialized
     */
    private static string|null|false $accountId = null;

    /**
     * Initialize session (if needed)
     * @throws RuntimeException if failed to initialize session
     */
    private static function initialize(): void {
        if (self::$accountId !== null) {
            // Already initialized
            return;
        }
        $now = time();

        // Get account details from token
        $token = $_COOKIE[SESSION_COOKIE_NAME] ?? '';
        $account = DB::getRow(
            'SELECT account, refreshes_at FROM `sessions` WHERE token=?s AND expires_at>?s',
            $token,
            gmdate('Y-m-d H:i:s', $now)
        );
        self::$accountId = ($account === null) ? false : $account['account'];
        if (self::$accountId === null) {
            throw new RuntimeException("Received NULL account ID from database for session token '$token'");
        }
        if (self::$accountId === false) {
            // No account found
            return;
        }

        // Update session metadata
        DB::query(
            'UPDATE `sessions` SET ip_address=?s, user_agent=?s, last_seen_at=?s WHERE token=?s',
            Http::getIpAddress(),
            Http::getUserAgent(),
            gmdate('Y-m-d H:i:s', $now),
            $token
        );

        // Update account metadata
        DB::query(
            'UPDATE accounts SET last_seen_at=?s WHERE id=?i',
            gmdate('Y-m-d H:i:s', $now),
            self::$accountId
        );

        // Refresh session token if (needed)
        $refreshesAt = strtotime($account['refreshes_at']);
        if ($now >= $refreshesAt) {
            $newToken = self::generateToken();
            $refreshesAt = $now + SESSION_REFRESH_LIFETIME;
            $expiresAt = $now + SESSION_EXPIRATION_LIFETIME;
            DB::query(
                'UPDATE `sessions` SET token=?s, refreshes_at=?s, expires_at=?s WHERE token=?s',
                $newToken,
                gmdate('Y-m-d H:i:s', $refreshesAt),
                gmdate('Y-m-d H:i:s', $expiresAt),
                $token
            );
            setcookie(SESSION_COOKIE_NAME, $newToken, $expiresAt, '/', '', true, true);
        }
    }

    /**
     * Generate session token
     * @return string Session token
     */
    private static function generateToken(): string {
        return strtr(base64_encode(random_bytes(42)), '+/', '-_');
    }

    /**
     * Get logged account ID
     *
     * @return int Account ID
     * @throws RuntimeException if unauthenticated
     */
    public static function getAccountId(): int {
        self::initialize();
        if (self::$accountId === false) {
            throw new RuntimeException('Unauthenticated request');
        }
        return self::$accountId;
    }

    /**
     * Is authenticated request
     *
     * @return boolean Whether request is authenticated or not
     */
    public static function isAuthed(): bool {
        self::initialize();
        return (self::$accountId !== false);
    }

    /**
     * Require authentication to continue execution
     */
    public static function requireAuth(): void {
        if (!self::isAuthed()) {
            $fullUri = Http::getUri(true);
            Response::redirect('/login?redirect=' . urlencode($fullUri));
        }
    }

    /**
     * Login as account
     *
     * Inserts a new session into the database and sends the session cookie to the client.
     *
     * @param string $accountId Account ID
     */
    public static function login(string $accountId): void {
        $token = self::generateToken();
        $now = time();
        $refreshesAt = $now + SESSION_REFRESH_LIFETIME;
        $expiresAt = $now + SESSION_EXPIRATION_LIFETIME;
        DB::query(
            'INSERT INTO `sessions` (token, account, ip_address, user_agent, created_at, last_seen_at,
               refreshes_at, expires_at)
             VALUES (?s, ?i, ?s, ?s, ?s, ?s, ?s, ?s)',
            $token,
            $accountId,
            Http::getIpAddress(),
            Http::getUserAgent(),
            gmdate('Y-m-d H:i:s', $now),
            gmdate('Y-m-d H:i:s', $now),
            gmdate('Y-m-d H:i:s', $refreshesAt),
            gmdate('Y-m-d H:i:s', $expiresAt)
        );
        setcookie(SESSION_COOKIE_NAME, $token, $expiresAt, '/', '', true, true);
    }

    /**
     * Logout (if possible)
     *
     * Clears the session from the database and unsets the cookie from the client.
     */
    public static function logout(): void {
        if (self::isAuthed()) {
            $token = $_COOKIE[SESSION_COOKIE_NAME] ?? '';
            DB::query('DELETE FROM `sessions` WHERE token=?s', $token);
        }
        setcookie(SESSION_COOKIE_NAME, '', 0, '/', '', true, true);
    }
}
