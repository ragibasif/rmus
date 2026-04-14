# rmus

A lightweight, Dockerized music streaming server built with **FastAPI**, **SQLite**, and **AcoustID**. It provides a simple web frontend and a Subsonic-compatible streaming endpoint.

## Quick Start

### 1. Prerequisites
* [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
* [uv](https://github.com/astral-sh/uv) (for local dependency management)
* An [AcoustID API Key](https://acoustid.org/login) (optional, for metadata fingerprinting)

### 2. Configuration
Create a `.env` file in the root directory:

```env
MUSIC_DIR=/Users/yourname/path/to/mp3s
DB_PATH=/app/data/music.db
ACOUSTID_API_KEY=your_key_here
ADMIN_DB_ENABLED=false
```

### 3. Deploy
Run the included setup script to build the environment, scan your library, and start the server:

```bash
chmod +x scripts/docker_up.sh
./scripts/docker_up.sh
```

The server will be available at: **http://localhost:4040**


## Architecture

- **Backend:** FastAPI (Python 3.13)
- **Database:** SQLite
- **ID Strategy:** Stable MD5 hashes based on file paths (Relative to `/music`).
- **Scanning:** Recursive directory walking using `pathlib` and metadata extraction via `mutagen`.
- **Dockerized:** Multi-stage build using `uv` for minimal image size and fast dependency resolution.


## Management Commands

### Scanning for New Music
The scanner (in `db.py`) must be run inside the Docker environment to ensure file paths are recorded correctly relative to the container:
```bash
docker compose run --rm db
```

### Shutting Down
To stop the server and cleanup resources:
```bash
docker compose down
```

### Checking the Database
To view your indexed tracks directly from the terminal:
```bash
docker exec -it music_server sqlite3 /app/data/music.db "SELECT title, artist FROM tracks LIMIT 10;"
```

### Viewing Logs
If music isn't playing or the UI isn't loading:
```bash
docker compose logs -f server
```

---

## Project Structure
```text
rmus/
├── data/               # Persistent SQLite database
├── templates/          # Jinja2 HTML frontend
├── server.py           # FastAPI application logic
├── db.py               # Metadata indexing script
├── Dockerfile          # Multi-stage Python 3.13 build
├── docker-compose.yml  # Service orchestration
├── pyproject.toml      # Dependency definitions
├── Makefile            # uv rules
└── scripts/            # Docker helper scripts
```

## Important Note on Pathing
This project mounts your music directory as a **Read-Only** volume (`:ro`).
**Crucial:** Always run the `db` via `docker compose`. Running `db.py` directly on your host OS will record host-specific paths (e.g., `/Users/...`), which the Linux-based server container will not be able to resolve, resulting in `FileNotFound` errors during streaming.
