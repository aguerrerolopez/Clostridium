<?php
// Configure application
date_default_timezone_set('UTC');

// Define constants
const APP_NAME = 'AutoCdiff';

const ACCOUNT_FIRSTNAME_MAX_LENGTH = 100;
const ACCOUNT_LASTNAME_MAX_LENGTH = 100;
const ACCOUNT_EMAIL_MAX_LENGTH = 300;
const ACCOUNT_PASSWORD_MIN_LENGTH = 8;

const EMAIL_VERIFICATION_DELAY = 60*60*3; // 3 hours (before requesting a new one)
const EMAIL_VERIFICATION_LIFETIME = 60*60*24; // 1 day (before it expires)

const PASSWORD_RESET_LIFETIME = 60*60*5; // 5 hours (before it expires and requesting a new one)

const UPLOAD_NAME_MAX_LENGTH = 200;
const UPLOAD_MAX_ERRORS = 20; // Maximum errors to show in upload page

const RESULTS_ALLOWED_LIMITS = [20, 50, 100, 500];
const RESULTS_DEFAULT_LIMIT = 20;
const RESULTS_ALLOWED_RIBOTYPES = ['RT027'];

const SESSION_COOKIE_NAME = 'sess';
const SESSION_REFRESH_LIFETIME = 60*60*24*7; // 7 days
const SESSION_EXPIRATION_LIFETIME = 60*60*24*30; // 30 days

// Load dependencies
require __DIR__ . '/vendor/autoload.php';
