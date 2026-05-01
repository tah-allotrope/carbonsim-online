from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class CreateGameRequest(BaseModel):
    player_name: str = Field(default="Player", min_length=1, max_length=100)
    province_name: str = Field(default="default", max_length=100)
    difficulty: str = Field(default="standard", pattern=r"^(easy|standard|hard)$")
    num_years: int | None = Field(default=None, ge=5, le=25)


class CreateGameResponse(BaseModel):
    game_id: str
    player_name: str
    province_name: str
    difficulty: str
    status: str
    current_year: int
    total_years: int
    snapshot: dict[str, Any]


class GameListItem(BaseModel):
    game_id: str
    player_name: str
    difficulty: str
    status: str
    current_year: int
    total_years: int
    created_at: str
    updated_at: str


class GameStateResponse(BaseModel):
    game_id: str
    player_name: str
    province_name: str
    difficulty: str
    status: str
    current_year: int
    total_years: int
    snapshot: dict[str, Any]
    available_actions: list[str] = []


class AdvanceYearResponse(BaseModel):
    game_id: str
    year: int
    phase: str
    drawn_cards: list[dict[str, Any]]
    snapshot: dict[str, Any]


class ResolveCardRequest(BaseModel):
    card_id: str
    choice_id: str | None = None


class DecisionRequest(BaseModel):
    action: str = Field(pattern=r"^(activate_abatement|buy_offsets|propose_trade|respond_to_trade|submit_auction_bid)$")
    payload: dict[str, Any] = Field(default_factory=dict)


class SaveGameRequest(BaseModel):
    save_name: str = Field(default="Quick Save", min_length=1, max_length=100)


class SaveListItem(BaseModel):
    save_id: str
    game_id: str
    save_name: str
    saved_at: str


class SummaryResponse(BaseModel):
    game_id: str
    player_name: str
    difficulty: str
    total_years: int
    completed_years: int
    snapshot: dict[str, Any]


class ErrorResponse(BaseModel):
    detail: str
