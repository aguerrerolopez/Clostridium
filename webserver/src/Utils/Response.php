<?php
namespace App\Utils;

use League\Plates\Engine;

class Response {
    /**
     * Return HTTP status response without body
     *
     * @param int $code Status code
     */
    public static function status(int $code): never {
        http_response_code($code);
        exit;
    }

    /**
     * Redirection response
     *
     * @param string  $url       Redirection URL
     * @param boolean $permanent Whether is a permanent or a temporary redirect
     */
    public static function redirect(string $url, bool $permanent = false): never {
        header("Location: $url", true, $permanent ? 301 : 302);
        exit;
    }

    /**
     * HTML response
     *
     * @param string              $template Template name
     * @param array<string,mixed> $data     Data for template
     */
    public static function html(string $template, array $data = []): never {
        $engine = new Engine(__DIR__ . '/../../templates', 'phtml');
        echo $engine->render($template, $data);
        exit;
    }
}
