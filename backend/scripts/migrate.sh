#!/bin/bash
set -e

MESSAGE="${1:?Usage: ./scripts/migrate.sh \"migration message\"}"

echo "Generating migration: $MESSAGE"
alembic revision --autogenerate -m "$MESSAGE"

echo "Applying migration..."
alembic upgrade head

echo "Migration complete."
