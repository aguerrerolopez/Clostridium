<?php
namespace App\Utils;

use UMySQL\Exceptions\ParseException;
use UMySQL\Result;
use UMySQL\UMySQL;

class DB {
    /** @var UMySQL */
    private static $instance = null;

    /**
     * Initialize database instance
     */
    private static function initialize(): void {
        if (self::$instance === null) {
            self::$instance = new UMySQL([
                'hostname' => getenv('DB_HOST'),
                'username' => getenv('DB_USER'),
                'password' => getenv('DB_PASS'),
                'database' => getenv('DB_NAME'),
            ]);
        }
    }

    /**
     * Close connection to database
     */
    public static function disconnect(): void {
        if (self::$instance !== null) {
            self::$instance->disconnect();
            self::$instance = null;
        }
    }

    /**
     * Parse query with placeholders
     *
     * @param  string $query     Query with placeholders
     * @param  mixed  ...$params Values for placeholders
     * @return string            Parsed query
     * @throws ParseException if failed to bind parameters to placeholders
     */
    public static function parse(string $query, ...$params): string {
        self::initialize();
        return self::$instance->parse($query, ...$params);
    }

    /**
     * Execute query
     *
     * @param  string $query     Query with placeholders
     * @param  mixed  ...$params Values for placeholders
     * @return Result            Query result instance
     * @throws ParseException if failed to bind parameters to placeholders
     * @throws QueryException if failed to execute query
     */
    public static function query(string $query, ...$params): Result {
        self::initialize();
        return self::$instance->query($query, ...$params);
    }

    /**
     * Get all result rows
     *
     * @param  string                      $query     Query with placeholders
     * @param  mixed                       ...$params Values for placeholders
     * @return array<string,string|null>[]            Result rows
     * @throws ParseException if failed to bind parameters to placeholders
     * @throws QueryException if failed to execute query
     */
    public static function getAll(string $query, ...$params): array {
        self::initialize();
        return self::$instance->getAll($query, ...$params);
    }

    /**
     * Get first result row
     *
     * @param  string                         $query     Query with placeholders
     * @param  mixed                          ...$params Values for placeholders
     * @return array<string,string|null>|null            First result row or `null` if no rows found
     * @throws ParseException if failed to bind parameters to placeholders
     * @throws QueryException if failed to execute query
     */
    public static function getRow(string $query, ...$params): ?array {
        self::initialize();
        return self::$instance->getRow($query, ...$params);
    }

    /**
     * Get first column of result rows
     *
     * @param  string          $query     Query with placeholders
     * @param  mixed           ...$params Values for placeholders
     * @return (string|null)[]            First column of result rows
     * @throws ParseException if failed to bind parameters to placeholders
     * @throws QueryException if failed to execute query
     */
    public static function getCol(string $query, ...$params): array {
        self::initialize();
        return self::$instance->getCol($query, ...$params);
    }

    /**
     * Get first scalar from result rows
     *
     * @param  string            $query     Query with placeholders
     * @param  mixed             ...$params Values for placeholders
     * @return string|null|false            First column of the first result row or `false` if no rows found
     * @throws ParseException if failed to bind parameters to placeholders
     * @throws QueryException if failed to execute query
     */
    public static function getOne(string $query, ...$params): string|null|false {
        self::initialize();
        return self::$instance->getOne($query, ...$params);
    }
}
