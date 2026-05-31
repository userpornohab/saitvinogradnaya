#!/bin/sh
set -e

mkdir -p /app/static/uploads /app/static/icons /app/data

if [ -d /app/static-default ]; then
  cp -an /app/static-default/. /app/static/
fi

exec "$@"
