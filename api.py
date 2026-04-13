from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

# This script crawls the library and populates a SQLite database.
# Using EasyID3 ensures it gets the most common tags without complex
# frame logic.

load_dotenv()

MUSIC_DIR = os.getenv("MUSIC_DIR")
if not MUSIC_DIR:
    raise RuntimeError("MUSIC_DIR not set in .env")

DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    raise RuntimeError("DB_PATH not set in .env")

music_path = Path(str(MUSIC_DIR)).expanduser()
db_path = Path(str(DB_PATH))

music_path.parent.mkdir(parents=True, exist_ok=True)
db_path.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI()

def get_db():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def subsonic_wrapper(data_key: str, data: any):
    """Wraps data in the standard Subsonic response format"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "type": "server",
            "openSubsonic": True,
            data_key: data
        }
    }

@app.get("/rest/ping.view")
async def ping():
    return subsonic_wrapper("ping", {})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4040)
