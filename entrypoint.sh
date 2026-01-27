#!/bin/sh

# Run all migration SQL files in order
for f in /app/migrations/*.sql; do
  if [ -f "$f" ]; then
    echo "Running migration: $f"
    sqlite3 /app/data/database.db < "$f"
  fi
done

exec "$@"
