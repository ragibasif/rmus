import hashlib
import os
import sqlite3
from pathlib import Path
from mutagen.easyid3 import EasyID3
from dotenv import load_dotenv

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


def generate_id(file_path:str)->str:
    """Creates a stable 32-character MD5 hash of the path."""
    return hashlib.md5(file_path.encode('utf-8')).hexdigest()


def init_db():
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id TEXT PRIMARY KEY,
            path TEXT UNIQUE,
            title TEXT,
            artist TEXT,
            album TEXT,
            last_mtime REAL
        )
     """)
    conn.commit()
    return conn


def index_db():
    conn = init_db()
    for fp in music_path.rglob("*.mp3"):
        try:
            path_str = str(fp)
            track_id = generate_id(path_str)    # Generate MD5
            current_mtime = fp.stat().st_mtime

            # check if updated
            row = conn.execute("SELECT last_mtime FROM tracks WHERE id = ?", (track_id,)).fetchone()

            if row is None or row[0] < current_mtime:
                audio = EasyID3(path_str)
                title = audio.get('title', [fp.stem])[0]
                artist = audio.get('artist', ['Unknown'])[0]
                album = audio.get('album', ['Unknown'])[0]
                conn.execute("""
                INSERT OR REPLACE INTO tracks (id, path, title, artist, album, last_mtime)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (track_id, path_str, title, artist, album, current_mtime))
            conn.commit()
        except Exception as e:
            print(f"Skipping {fp.name}: {e}")
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
    index_db()
    print("Library indexed.")
