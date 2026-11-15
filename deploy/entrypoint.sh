#!/bin/sh
set -e

mkdir -p /data/media /data/staticfiles
chown -R appuser:appgroup /data

runuser -u appuser -- python manage.py migrate --noinput
runuser -u appuser -- python manage.py collectstatic --noinput

exec runuser -u appuser -- gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 60
