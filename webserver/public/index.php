<?php
use App\Utils\Http;
use App\Utils\Response;

require __DIR__ . '/../bootstrap.php';

// Get page name to load
$uri = Http::getUri();
$pageName = match ($uri) {
    '/'                       => 'homepage',
    '/login'                  => 'login',
    '/signup'                 => 'signup',
    '/logout'                 => 'logout',
    '/reset-password'         => 'reset-password',
    '/reset-password-confirm' => 'reset-password-confirm',
    '/upload'                 => 'upload',
    '/results'                => 'results',
    '/account'                => 'account',
    '/verify-email'           => 'verify-email',
    default                   => null,
};
if ($pageName === null) {
    $pageName = match (1) {
        preg_match('/^\/results\/[a-zA-Z0-9]+$/',     $uri) => 'result',
        preg_match('/^\/download(\/[a-zA-Z0-9]+)?$/', $uri) => 'download',
        default                                             => 'not-found',
    };
}

// Load page contents
header_remove('x-powered-by');
try {
    Response::html($pageName);
} catch (Exception $e) {
    error_log($e);
    Response::html('crash');
}
