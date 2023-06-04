<?php
namespace App\Utils;

class Storage {
    /**
     * Get path to sample file
     *
     * @param  string $digest Sample digest
     * @return string         Path to sample
     */
    public static function getPathToSample(string $digest): string {
        return getenv('SAMPLES_DATA_DIR') . '/' . substr($digest, 0, 2) . '/' . substr($digest, 2, 2) . "/$digest.zip";
    }
}
