<?php
namespace App;

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
}