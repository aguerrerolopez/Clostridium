<?php
// Configure application
date_default_timezone_set('UTC');

// Define constants
const APP_NAME = 'Untitled Project';

const ACCOUNT_FIRSTNAME_MAX_LENGTH = 100;
const ACCOUNT_LASTNAME_MAX_LENGTH = 100;
const ACCOUNT_EMAIL_MAX_LENGTH = 300;
const ACCOUNT_PASSWORD_MIN_LENGTH = 8;

const SESSION_COOKIE_NAME = 'sess';
const SESSION_REFRESH_LIFETIME = 60*60*24*7; // 7 days
const SESSION_EXPIRATION_LIFETIME = 60*60*24*30; // 30 days

// Load dependencies
require __DIR__ . '/vendor/autoload.php';
