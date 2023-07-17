#!/bin/sh
chown caddy:caddy /config
exec /usr/bin/supervisord -c /app/supervisord.conf
