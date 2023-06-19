#!/bin/bash

# Second stage
if [ "$1" = "migrate" ]; then
    run-script migrate || exit 1
    touch /var/tmp/ready.status
    exit 0
fi

# Reset status
rm -f /var/tmp/ready.status

# Execute migrations
echo "Started migrations job in the background"
nohup "$0" migrate >/dev/stdout 2>&1 &

# Start MySQL server
exec docker-entrypoint.sh --skip-innodb --default-storage-engine=Aria
