from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routes.coop import router as coop_router
from .routes.game import router as game_router
from .routes.health import router as health_router
from .ws import coop_ws_endpoint


class NoCacheStaticFiles(StaticFiles):
    """StaticFiles that asks browsers to revalidate (via ETag) on every load.

    The frontend is a no-build vanilla bundle, so without this browsers
    heuristic-cache app JS/CSS and keep running stale code after a deploy.
    """

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title="CarbonSim Online API",
        description="Single-player and multiplayer carbon compliance game backend",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=500)

    init_db()

    app.include_router(health_router)
    app.include_router(game_router)
    app.include_router(coop_router)

    @app.websocket("/ws/games/{game_id}/{participant_id}")
    async def coop_ws(websocket: WebSocket, game_id: str, participant_id: str):
        await coop_ws_endpoint(websocket, game_id, participant_id)

    web_dir = Path(__file__).parent.parent / "web"
    css_dir = web_dir / "css"
    js_dir = web_dir / "js"
    assets_dir = web_dir / "assets"

    if css_dir.exists():
        app.mount("/css", NoCacheStaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", NoCacheStaticFiles(directory=str(js_dir)), name="js")
    if assets_dir.exists():
        app.mount("/assets", NoCacheStaticFiles(directory=str(assets_dir)), name="assets")

    web_root = web_dir.resolve()
    index_path = web_root / "index.html"

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        # Resolve the requested path and confirm it stays inside web/ before
        # serving — guards against traversal (e.g. "..%2frequirements.txt").
        candidate = (web_dir / path).resolve()
        if (
            candidate.is_file()
            and candidate.is_relative_to(web_root)
        ):
            return FileResponse(str(candidate))
        return FileResponse(str(index_path))

    return app


app = create_app()
