from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routes.game import router as game_router
from .routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Climate Mayor API",
        description="Single-player carbon compliance game backend",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    init_db()

    app.include_router(health_router)
    app.include_router(game_router)

    web_dir = Path(__file__).parent.parent / "mayor_web"
    css_dir = web_dir / "css"
    js_dir = web_dir / "js"

    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file_path = web_dir / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        index_path = web_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return FileResponse(str(index_path)) if index_path.exists() else None

    return app


app = create_app()
