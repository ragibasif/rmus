import os
import sqlite3
import hashlib
import acoustid
from pathlib import Path
from dotenv import load_dotenv
from mutagen.easyid3 import EasyID3


load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/music.db")
MUSIC_DIR = Path(os.getenv("MUSIC_DIR", "/music")).expanduser()
ACOUSTID_API_KEY = os.getenv("ACOUSTID_API_KEY")


def generate_id(file_path: Path) -> str:
    """Creates a stable MD5 hash based on the relative path to MUSIC_DIR."""
    try:
        relative_path = file_path.relative_to(MUSIC_DIR)
    except ValueError:
        relative_path = file_path
    return hashlib.md5(str(relative_path).encode("utf-8")).hexdigest()


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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


def get_metadata(path: Path):
    try:
        audio = EasyID3(str(path))
        title = audio.get("title", [None])[0]
        artist = audio.get("artist", [None])[0]
        album = audio.get("album", ["Unknown"])[0]

        if (not title or not artist) and ACOUSTID_API_KEY:
            results = acoustid.match(ACOUSTID_API_KEY, str(path))
            for res_score, res_recording_id, res_title, res_artist in results:
                if res_score > 0.8:
                    return res_title, res_artist, album
        return title or path.stem, artist or "Unknown", album
    except Exception:
        return path.stem, "Unknown", "Unknown"


def scan():
    conn = init_db()
    for fp in MUSIC_DIR.rglob("*.mp3"):
        track_id = generate_id(fp)
        current_mtime = fp.stat().st_mtime

        # check if updated
        row = conn.execute(
            "SELECT last_mtime FROM tracks WHERE id = ?", (track_id,)
        ).fetchone()

        if row is None or row[0] < current_mtime:
            title, artist, album = get_metadata(fp)
            conn.execute(
                """
            INSERT OR REPLACE INTO tracks (id, path, title, artist, album, last_mtime)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
                (track_id, str(fp), title, artist, album, current_mtime),
            )
        conn.commit()
    conn.close()


if __name__ == "__main__":
    scan()
