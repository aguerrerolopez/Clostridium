<?php
namespace App;

use RuntimeException;

class Session {
    /**
     * Logged account details, `null` if unauthenticated or `false` if not initialized
     * @var array<string,string|null>|null|false
     */
    private static array|null|false $account = false;

    /**
     * Initialize session (if needed)
     * @throws RuntimeException if failed to initialize session
     */
    private static function initialize(): void {
        if (self::$account !== false) {
            // Already initialized
            return;
        }
        $now = time();

        // Get account details from token
        $token = $_COOKIE[SESSION_COOKIE_NAME] ?? '';
        self::$account = DB::getRow(
            'SELECT a.id, a.email, a.firstname, a.lastname, a.verified_at, s.refreshes_at
             FROM `sessions` s
             LEFT JOIN accounts a ON s.account=a.id
             WHERE s.token=?s AND s.expires_at>?s',
            $token,
            gmdate('Y-m-d H:i:s', $now)
        );
        if (self::$account === null) {
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
            self::$account['id']
        );

        // Refresh session token if (needed)
        $refreshesAt = strtotime(self::$account['refreshes_at']);
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
     * Is authenticated request
     *
     * @return boolean Whether request is authenticated or not
     */
    public static function isAuthed(): bool {
        self::initialize();
        return (self::$account !== null);
    }

    /**
     * Get account field value
     *
     * @param  string      $field Field name
     * @return string|null        Field value
     * @throws RuntimeException if unauthenticated
     */
    private static function get(string $field): ?string {
        self::initialize();
        if (self::$account === null) {
            throw new RuntimeException('Unauthenticated request');
        }
        return self::$account[$field] ?? null;
    }

    /**
     * Get logged account ID
     *
     * @return string Account ID
     * @throws RuntimeException if unauthenticated
     */
    public static function getAccountId(): string {
        return self::get('id');
    }

    /**
     * Get logged account email address
     *
     * @return string Account email address
     * @throws RuntimeException if unauthenticated
     */
    public static function getEmail(): string {
        return self::get('email');
    }

    /**
     * Get logged account firstname
     *
     * @return string Account firstname
     * @throws RuntimeException if unauthenticated
     */
    public static function getFirstname(): string {
        return self::get('firstname');
    }

    /**
     * Get logged account lastname
     *
     * @return string Account lastname
     * @throws RuntimeException if unauthenticated
     */
    public static function getLastname(): string {
        return self::get('lastname');
    }

    /**
     * Is logged account verified
     *
     * @return boolean Whether account is verified
     * @throws RuntimeException if unauthenticated
     */
    public static function isVerified(): bool {
        return (self::get('verified_at') !== null);
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
