import os
import sqlite3
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_db():
    conn = sqlite3.connect(os.getenv("DB_PATH", "data/music.db"))
    conn.row_factory = sqlite3.Row
    return conn


def subsonic_wrapper(data_key: str, data: Any):
    """Wraps data in the standard Subsonic response format"""
    return {
        "subsonic-response": {
            "status": "ok",
            "version": "1.16.1",
            "type": "server",
            "openSubsonic": True,
            data_key: data,
        }
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    db = get_db()
    try:
        tracks = db.execute(
            "SELECT id, title, artist, album FROM tracks ORDER BY artist, album, title"
        ).fetchall()
        return templates.TemplateResponse(
            request=request, name="index.html", context={"tracks": tracks}
        )
    finally:
        db.close()


@app.get("/rest/ping.view")
async def ping():
    return subsonic_wrapper("ping", {})


@app.get("/rest/stream.view")
async def stream(id: str):
    db = get_db()
    try:
        track = db.execute("SELECT path FROM tracks WHERE id = ?", (id,)).fetchone()
    finally:
        db.close()

    if not track:
        raise HTTPException(status_code=404, detail="Track ID not in database")

    file_path = track["path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(file_path, media_type="audio/mpeg")


@app.get("/admin/db")
async def view_db():
    if os.getenv("ADMIN_DB_ENABLED", "").lower() not in {"1", "true", "yes"}:
        raise HTTPException(status_code=404, detail="Not found")

    db = get_db()
    try:
        rows = db.execute("SELECT * FROM tracks").fetchall()
        return {"count": len(rows), "data": [dict(r) for r in rows]}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=4040)
