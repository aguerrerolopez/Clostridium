<?php
namespace App\Utils;

class Crypto {
    const DEFAULT_KEYSPACE = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

    /**
     * Get random string
     *
     * @param  int    $length   Length in characters
     * @param  string $keyspace Allowed characters
     * @return string           Random string
     */
    public static function getRandomString(int $length, string $keyspace = self::DEFAULT_KEYSPACE): string {
        $max = strlen($keyspace) - 1;
        $res = '';
        while ($length--) {
            $res .= $keyspace[random_int(0, $max)];
        }
        return $res;
    }

    /**
     * Get random hexadecimal string
     *
     * @param  int    $length Length in bytes
     * @return string         Random hexadecimal string
     */
    public static function getRandomHexString(int $length): string {
        return bin2hex(random_bytes($length));
    }
}
