import os
import sqlite3
from fastapi import FastAPI, Request
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


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    db = get_db()
    tracks = db.execute("SELECT id, title, artist, album FROM tracks").fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "tracks": tracks})


@app.get("/rest/ping.view")
async def ping():
    return subsonic_wrapper("ping", {})


@app.get("/rest/stream.view")
async def stream(id: str):
    db = get_db()
    track = db.execute("SELECT path FROM tracks WHERE id = ?", (id,)).fetchone()
    if track:
        return FileResponse(track["path"])
    return {"error": "Not found"}


@app.get("/admin/db")
async def view_db():
    db = get_db()
    # This fetches everything and converts it to a list of dicts for easy display
    rows = db.execute("SELECT * FROM tracks").fetchall()
    return {"count": len(rows), "data": [dict(r) for r in rows]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4040)
