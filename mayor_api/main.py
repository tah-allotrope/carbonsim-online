from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    return app


app = create_app()
