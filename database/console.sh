#!/bin/bash
cmd="mysql --default-character-set=utf8mb4 --binary-as-hex -u${DB_USER@Q} --password=${DB_PASS@Q} ${DB_NAME@Q}"
if [ $# -eq 1 ]; then
    cmd="$cmd -e ${1@Q}"
fi
eval "$cmd"
