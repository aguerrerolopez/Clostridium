<?php
use App\Http;
use App\Response;

require __DIR__ . '/../bootstrap.php';

// Get page name to load
$uri = Http::getUri();
$pageName = match ($uri) {
    '/'                  => 'homepage',
    '/login'             => 'login',
    '/signup'            => 'signup',
    '/logout'            => 'logout',
    '/password-recovery' => 'password-recovery',
    '/account'           => 'account',
    '/verify-email'      => 'verify-email',
    default              => 'not-found',
};

// Load page contents
header_remove('x-powered-by');
try {
    Response::html($pageName);
} catch (Exception $e) {
    error_log($e);
    Response::html('crash');
}
