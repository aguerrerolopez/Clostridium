<?php
namespace App\Utils;

class Storage {
    const RESERVED_FILENAMES = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7',
        'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'];

    /**
     * Is directory empty
     *
     * @param  string  $path Path to directory
     * @return boolean       Whether directory is empty or not
     */
    public static function isDirectoryEmpty(string $path): bool {
        return (count(scandir($path)) === 2);
    }

    /**
     * Get path to sample file
     *
     * @param  string $digest Sample digest in lowercase hexadecimal
     * @return string         Path to sample
     */
    public static function getPathToSample(string $digest): string {
        return getenv('SAMPLES_DATA_DIR') . '/' . substr($digest, 0, 2) . '/' . substr($digest, 2, 2) . "/$digest.zip";
    }

    /**
     * Delete sample file
     *
     * @param string $digest Sample digest in lowercase hexadecimal
     */
    public static function deleteSample(string $digest): void {
        $path = self::getPathToSample($digest);
        unlink($path);

        // Delete parent directories if empty
        $parentPaths = [dirname($path), dirname($path, 2)];
        foreach ($parentPaths as $parentPath) {
            if (!self::isDirectoryEmpty($parentPath)) {
                break;
            }
            rmdir($parentPath);
        }
    }

    /**
     * Sanitize path part
     *
     * @param  string $part Unsafe path part
     * @return string       Sanitized path part
     */
    public static function sanitizePathPart(string $part): string {
        // Remove non-printable characters
        $part = preg_replace('/[\x00-\x1F\x7F]/u', '', $part);

        // Replace forbidden characters in Linux and Windows
        $part = str_replace(
            ['/', '\\', '<', '>', ':', '"', '|', '?', '*'],
            ['_', '_',  '-', '-', '-', "'", '-', '-', '-'],
            $part
        );

        // Block reserved Windows filenames
        $partWithoutExtension = pathinfo($part, PATHINFO_FILENAME);
        if (in_array($partWithoutExtension, self::RESERVED_FILENAMES, true)) {
            $part = "_$part";
        }

        return $part;
    }
}
