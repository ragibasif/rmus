#!/usr/bin/env bash

# 1. Force uv to sync and lock based on Python 3.13
uv lock

# 2. Kill everything and wipe cache
docker compose down --remove-orphans
docker builder prune -f

# 3. Rebuild with a clean slate
docker compose build --no-cache
docker compose up -d
