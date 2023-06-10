<?php
namespace App\Utils;

class Http {
    /**
     * Get IP address
     * @return string IP Address
     */
    public static function getIpAddress(): string {
        return $_SERVER['REMOTE_ADDR'] ?? '0.0.0.0';
    }

    /**
     * Get user agent
     * @return string User agent
     */
    public static function getUserAgent(): string {
        return $_SERVER['HTTP_USER_AGENT'] ?? '';
    }

    /**
     * Get URI
     * @param  boolean $withQuery Whether to include query params or not
     * @return string             Request URI
     */
    public static function getUri(bool $withQuery = false): string {
        return $withQuery ? $_SERVER['REQUEST_URI'] : strtok($_SERVER['REQUEST_URI'], '?');
    }

    /**
     * Get server base URL
     * @return string Base URL
     */
    public static function getBaseUrl(): string {
        return (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http') . '://' . $_SERVER['SERVER_NAME'];
    }

    /**
     * Build URI with parameters
     * @param  string              $uri    URI
     * @param  array<string,mixed> $params Query parameters
     * @return string                      Built URI
     */
    public static function buildUri(string $uri, array $params = []): string {
        foreach ($params as $key=>$value) {
            if ($value === null || $value === '') {
                unset($params[$key]);
            }
        }
        return $uri . (empty($params) ? '' : '?' . http_build_query($params));
    }
}
