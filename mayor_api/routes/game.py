from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from carbonsim_engine import (
    apply_company_decision,
    apply_shock,
    build_player_snapshot,
    build_session_replay,
    build_session_summary,
    close_auction,
    force_advance_phase,
    open_auction,
    respond_to_trade,
    run_bot_turns,
    start_simulation,
)
from carbonsim_engine.cards import CardDeck, draw_cards, resolve_card
from carbonsim_engine.solo import create_solo_game, solo_player_company

from ..db import (
    create_game as db_create_game,
    create_save as db_create_save,
    delete_game as db_delete_game,
    get_game as db_get_game,
    list_games as db_list_games,
    list_saves as db_list_saves,
    load_save as db_load_save,
    update_game_state as db_update_game_state,
    decompress_state,
)
from ..models import (
    AdvanceYearResponse,
    CreateGameRequest,
    CreateGameResponse,
    DecisionRequest,
    ErrorResponse,
    GameListItem,
    GameStateResponse,
    ResolveCardRequest,
    SaveGameRequest,
    SaveListItem,
    SummaryResponse,
)

router = APIRouter(prefix="/api/games", tags=["games"])

STARTER_DECK_PATH = None
try:
    from pathlib import Path
    _p = Path(__file__).parent.parent.parent / "carbonsim_engine" / "data" / "starter_deck.json"
    if _p.exists():
        STARTER_DECK_PATH = str(_p)
except Exception:
    pass


def _utc() -> datetime:
    return datetime.now(timezone.utc)


def _snapshot(state: dict[str, Any]) -> dict[str, Any]:
    player = solo_player_company(state)
    if player:
        return build_player_snapshot(
            state,
            company_id=player["company_id"],
            is_facilitator=False,
            participant_label=player.get("company_name", "Player"),
            now=_utc(),
        )
    return {"companies": state.get("companies", [])}


def _available_actions(state: dict[str, Any]) -> list[str]:
    phase = state.get("phase", "")
    actions = []
    if phase in ("year_start", "decision_window"):
        actions.append("advance_phase")
    if phase == "decision_window":
        actions.append("activate_abatement")
        actions.append("buy_offsets")
        actions.append("submit_auction_bid")
        actions.append("propose_trade")
        actions.append("respond_to_trade")
    if phase == "compliance":
        actions.append("end_year")
    return actions


@router.post("", response_model=CreateGameResponse)
async def create_game_route(req: CreateGameRequest):
    game_id = str(uuid.uuid4())
    num_years = req.num_years or {"easy": 20, "standard": 15, "hard": 10}.get(req.difficulty, 15)
    state = create_solo_game(
        player_name=req.player_name,
        province_name=req.province_name,
        difficulty=req.difficulty,
        num_years=num_years,
    )
    state["game_id"] = game_id
    db_create_game(game_id, req.player_name, req.province_name, req.difficulty, num_years, state)
    return CreateGameResponse(
        game_id=game_id,
        player_name=req.player_name,
        province_name=req.province_name,
        difficulty=req.difficulty,
        status="active",
        current_year=state.get("current_year", 1),
        total_years=num_years,
        snapshot=_snapshot(state),
    )


@router.get("", response_model=list[GameListItem])
async def list_games_route():
    return db_list_games()


@router.get("/{game_id}", response_model=GameStateResponse)
async def get_game_route(game_id: str):
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    state = decompress_state(row["state_json"])
    return GameStateResponse(
        game_id=game_id,
        player_name=row["player_name"],
        province_name=row["province_name"],
        difficulty=row["difficulty"],
        status=row["status"],
        current_year=state.get("current_year", 0),
        total_years=row["total_years"],
        snapshot=_snapshot(state),
        available_actions=_available_actions(state),
    )


@router.post("/{game_id}/advance-year", response_model=AdvanceYearResponse)
async def advance_year(game_id: str):
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    state = decompress_state(row["state_json"])

    now = _utc()
    phase = state.get("phase", "")
    year = state.get("current_year", 0)

    if year >= state.get("num_years", 15) and phase == "complete":
        raise HTTPException(400, "Game already completed")

    if phase in ("lobby", "complete"):
        if phase == "lobby":
            state = start_simulation(state, now=now)
        if state.get("phase") == "complete":
            state["game_status"] = "completed"
            db_update_game_state(game_id, state)
            raise HTTPException(400, "Game already completed")

    state = force_advance_phase(state, now=now)
    phase = state.get("phase", "")

    drawn_cards = []
    if phase == "decision_window" and STARTER_DECK_PATH:
        import random
        deck = CardDeck.from_json(STARTER_DECK_PATH, rng=random.Random())
        state, drawn_cards = draw_cards(state, deck, count=3, now=now)
        state["drawn_cards"] = drawn_cards

    state = force_advance_phase(state, now=now)

    db_update_game_state(game_id, state)
    return AdvanceYearResponse(
        game_id=game_id,
        year=state.get("current_year", year + 1),
        phase=state.get("phase", ""),
        drawn_cards=drawn_cards,
        snapshot=_snapshot(state),
    )


@router.post("/{game_id}/resolve-card")
async def resolve_card_route(game_id: str, req: ResolveCardRequest):
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    state = decompress_state(row["state_json"])

    drawn = state.get("drawn_cards", [])
    card = next((c for c in drawn if c["card_id"] == req.card_id), None)
    if not card:
        raise HTTPException(400, f"Card {req.card_id} not in drawn cards")

    state = resolve_card(state, card, choice_id=req.choice_id, now=_utc())
    state["drawn_cards"] = [c for c in drawn if c["card_id"] != req.card_id]

    db_update_game_state(game_id, state)
    return {"status": "resolved", "card_id": req.card_id}


@router.post("/{game_id}/decision")
async def decision_route(game_id: str, req: DecisionRequest):
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    state = decompress_state(row["state_json"])

    player = solo_player_company(state)
    if not player:
        raise HTTPException(400, "No player company found")

    now = _utc()
    try:
        state = apply_company_decision(
            state,
            company_id=player["company_id"],
            action=req.action,
            payload=req.payload,
            now=now,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(400, str(e))

    db_update_game_state(game_id, state)
    return {"status": "applied", "snapshot": _snapshot(state)}


@router.post("/{game_id}/end-year")
async def end_year(game_id: str):
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    state = decompress_state(row["state_json"])

    now = _utc()

    state["drawn_cards"] = []

    state = run_bot_turns(state, now=now)

    phase = state.get("phase", "")
    while phase not in ("complete", "year_start"):
        state = force_advance_phase(state, now=now)
        phase = state.get("phase", "")

    if phase == "complete":
        state["game_status"] = "completed"

    db_update_game_state(game_id, state)
    return {
        "status": "year_ended",
        "year": state.get("current_year", 0),
        "phase": phase,
        "snapshot": _snapshot(state),
    }


@router.post("/{game_id}/save", response_model=SaveListItem)
async def save_game(game_id: str, req: SaveGameRequest):
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    state = decompress_state(row["state_json"])
    save_id = str(uuid.uuid4())
    save = db_create_save(save_id, game_id, req.save_name, state)
    return SaveListItem(save_id=save["save_id"], game_id=save["game_id"], save_name=save["save_name"], saved_at=save["saved_at"])


@router.get("/{game_id}/saves", response_model=list[SaveListItem])
async def list_saves_route(game_id: str):
    return db_list_saves(game_id)


@router.post("/{game_id}/load/{save_id}")
async def load_save_route(game_id: str, save_id: str):
    state = db_load_save(save_id)
    if not state:
        raise HTTPException(404, "Save not found")
    db_update_game_state(game_id, state)
    return {"status": "loaded", "snapshot": _snapshot(state)}


@router.get("/{game_id}/summary", response_model=SummaryResponse)
async def summary(game_id: str):
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    state = decompress_state(row["state_json"])
    return SummaryResponse(
        game_id=game_id,
        player_name=row["player_name"],
        difficulty=row["difficulty"],
        total_years=row["total_years"],
        completed_years=state.get("current_year", 0),
        snapshot=_snapshot(state),
    )


@router.delete("/{game_id}")
async def delete_game_route(game_id: str):
    if not db_delete_game(game_id):
        raise HTTPException(404, "Game not found")
    return {"status": "deleted"}
