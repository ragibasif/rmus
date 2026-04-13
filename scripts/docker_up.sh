#!/usr/bin/env bash

set -e
mkdir -p data templates

# Ensure uv.lock exists
if [ ! -f uv.lock ]; then uv lock; fi

docker compose build

echo "Initializing Database ..."
docker compose run --rm db

echo "Starting Server..."
docker compose up -d server

echo "http://localhost:4040"
