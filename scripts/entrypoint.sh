#!/bin/bash
set -e

echo "Starting Backend..."
uv run python -m axionara.main &

echo "Starting Nginx..."
exec nginx -g "daemon off;"
