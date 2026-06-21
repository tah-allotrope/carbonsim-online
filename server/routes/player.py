from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..db import get_player_profile, upsert_player_profile

router = APIRouter(prefix="/api/players", tags=["players"])


class PlayerXPRequest(BaseModel):
    xp: int = Field(ge=0)
    unlocks: list[str] = Field(default_factory=list)


@router.get("/{player_name}/xp")
async def get_player_xp(player_name: str):
    """Persistent lifetime XP + unlocks for a player (TASK-05-07)."""
    return get_player_profile(player_name)


@router.post("/{player_name}/xp")
async def save_player_xp(player_name: str, req: PlayerXPRequest):
    """Persist a player's XP / unlocks. XP is stored monotonically."""
    return upsert_player_profile(player_name, req.xp, req.unlocks)
