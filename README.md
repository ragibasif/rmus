# rmus

## Back End

Framework: https://github.com/fastapi/fastapi
API: https://github.com/opensubsonic/open-subsonic-api
Database: https://github.com/sqlite/sqlite

## Docker

```bash
# clear the docker cache and rebuild
docker compose build --no-cache
```

## Nuclear Reset

```bash
# clear local uv lock:
rm uv.lock && uv lock

# prune docker build cache
docker builder prune -f

# build from scratch
docker compose build --no-cache
```



