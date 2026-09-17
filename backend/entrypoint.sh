#!/bin/sh
# Prepare the database once, then hand off to gunicorn. Doing this here rather
# than at import time keeps the workers from racing to create the schema.
set -e

echo "==> Preparing database"
python -c "from app_factory import create_app, init_db; init_db(create_app())"

echo "==> Starting gunicorn"
exec gunicorn --bind 0.0.0.0:8000 --workers 2 run:app
