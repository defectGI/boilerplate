#!/bin/sh

sqlite3 /data/database.db < /app/db/migrations/001_init.sql

exec "$@"
