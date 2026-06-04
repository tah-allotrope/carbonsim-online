from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from engine import (
    add_competitive_participant,
    all_participants_ready,
    apply_company_decision,
    build_leaderboard,
    build_session_summary,
    close_auction,
    create_competitive_game,
    force_advance_phase,
    lobby_snapshot,
    open_auction,
    participant_snapshot,
    pause_session,
    reset_ready_check,
    resume_session,
    run_bot_turns,
    set_participant_ready,
    start_competitive_game,
    submit_auction_bid,
)
from engine.cards import CardDeck, draw_cards, resolve_card

from ..db import create_game as db_create_game, decompress_state, get_game as db_get_game, list_games as db_list_games, update_game_state as db_update_game_state
from ..models import CreateCoopGameRequest, HostActionRequest, JoinByRoomCodeRequest, JoinCoopRequest, ReadyRequest
from .game import _utc
from ..ws import manager as ws_manager

router = APIRouter(prefix="/api/coop", tags=["coop"])

STARTER_DECK_PATH = None
EXPANSION_DECK_PATH = None
try:
    from pathlib import Path
    _p = Path(__file__).parent.parent.parent / "engine" / "data" / "starter_deck.json"
    if _p.exists():
        STARTER_DECK_PATH = str(_p)
    _exp = Path(__file__).parent.parent.parent / "engine" / "data" / "expansion_deck.json"
    if _exp.exists():
        EXPANSION_DECK_PATH = str(_exp)
except Exception:
    pass


def _state_or_404(game_id: str) -> dict[str, Any]:
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    return decompress_state(row["state_json"])


def _find_game_by_room_code(room_code: str) -> str | None:
    games = db_list_games()
    for game in games:
        row = db_get_game(game["game_id"])
        if not row:
            continue
        state = decompress_state(row["state_json"])
        if state.get("room_code", "").upper() == room_code.upper() and state.get("game_status") == "lobby":
            return game["game_id"]
    return None


def _verify_host(state: dict[str, Any], participant_id: str) -> None:
    participant = next((p for p in state.get("participants", []) if p["participant_id"] == participant_id), None)
    if not participant:
        raise HTTPException(404, "Participant not found")
    if not participant.get("is_host"):
        raise HTTPException(403, "Only the host can perform this action")


@router.post("")
async def create_coop_route(req: CreateCoopGameRequest):
    import uuid

    game_id = str(uuid.uuid4())
    state = create_competitive_game(
        host_name=req.host_name,
        province_name=req.province_name,
        player_count=req.player_count,
        difficulty=req.difficulty,
        num_years=req.num_years,
    )
    state["game_id"] = game_id
    db_create_game(
        game_id,
        req.host_name,
        req.province_name,
        req.difficulty,
        state.get("num_years", req.num_years or 15),
        state,
    )
    participant = state["participants"][0]
    return {
        "game_id": game_id,
        "room_code": state["room_code"],
        "participant_id": participant["participant_id"],
        "player_count": req.player_count,
        "snapshot": participant_snapshot(state, participant_id=participant["participant_id"]),
    }


@router.post("/{game_id}/join")
async def join_coop_route(game_id: str, req: JoinCoopRequest):
    state = _state_or_404(game_id)
    if not state.get("coop_mode"):
        raise HTTPException(400, "Game is not a multiplayer session")
    if state.get("game_status") != "lobby":
        raise HTTPException(400, "Game has already started")
    try:
        participant = add_competitive_participant(state, player_name=req.player_name)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {
        "game_id": game_id,
        "room_code": state.get("room_code", ""),
        "participant_id": participant["participant_id"],
        "snapshot": participant_snapshot(state, participant_id=participant["participant_id"]),
    }


@router.post("/join-by-code")
async def join_by_room_code(req: JoinByRoomCodeRequest):
    game_id = _find_game_by_room_code(req.room_code)
    if not game_id:
        raise HTTPException(404, "No open lobby found with that room code")
    state = _state_or_404(game_id)
    try:
        participant = add_competitive_participant(state, player_name=req.player_name)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {
        "game_id": game_id,
        "room_code": state.get("room_code", ""),
        "participant_id": participant["participant_id"],
        "snapshot": participant_snapshot(state, participant_id=participant["participant_id"]),
    }


@router.post("/{game_id}/start")
async def start_game(game_id: str, req: HostActionRequest):
    state = _state_or_404(game_id)
    _verify_host(state, req.participant_id)
    try:
        state = start_competitive_game(state, now=_utc())
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    now = _utc()
    drawn_cards = []
    if state.get("phase") == "decision_window":
        if STARTER_DECK_PATH:
            deck = CardDeck.from_paths(
                STARTER_DECK_PATH,
                EXPANSION_DECK_PATH,
                rng=random.Random(hash((game_id, state.get("current_year", 0)))),
            ) if EXPANSION_DECK_PATH else CardDeck.from_json(
                STARTER_DECK_PATH,
                rng=random.Random(hash((game_id, state.get("current_year", 0)))),
            )
            state, drawn_cards = draw_cards(state, deck, count=3, now=now)
        state["drawn_cards"] = drawn_cards

    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {
        "status": "started",
        "year": state.get("current_year", 1),
        "phase": state.get("phase", ""),
        "drawn_cards": drawn_cards,
    }


@router.post("/{game_id}/advance-year")
async def host_advance_year(game_id: str, req: HostActionRequest):
    state = _state_or_404(game_id)
    _verify_host(state, req.participant_id)
    if state.get("game_status") not in ("active",):
        raise HTTPException(400, "Game is not active")

    now = _utc()
    phase = state.get("phase", "")

    state["drawn_cards"] = []
    state = run_bot_turns(state, now=now)

    while phase not in ("complete", "year_start", "decision_window"):
        state = force_advance_phase(state, now=now)
        phase = state.get("phase", "")

    if phase in ("year_start", "decision_window"):
        state = force_advance_phase(state, now=now)
        phase = state.get("phase", "")

    while phase not in ("complete", "decision_window"):
        state = force_advance_phase(state, now=now)
        phase = state.get("phase", "")

    if phase == "decision_window":
        drawn_cards = []
        if STARTER_DECK_PATH:
            deck = CardDeck.from_paths(
                STARTER_DECK_PATH,
                EXPANSION_DECK_PATH,
                rng=random.Random(hash((game_id, state.get("current_year", 0)))),
            ) if EXPANSION_DECK_PATH else CardDeck.from_json(
                STARTER_DECK_PATH,
                rng=random.Random(hash((game_id, state.get("current_year", 0)))),
            )
            state, drawn_cards = draw_cards(state, deck, count=3, now=now)
        state["drawn_cards"] = drawn_cards

    if phase == "complete":
        state["game_status"] = "completed"

    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {
        "status": "year_advanced",
        "year": state.get("current_year", 0),
        "phase": state.get("phase", ""),
        "game_status": state.get("game_status", "active"),
    }


@router.post("/{game_id}/pause")
async def host_pause(game_id: str, req: HostActionRequest):
    state = _state_or_404(game_id)
    _verify_host(state, req.participant_id)
    state = pause_session(state, now=_utc())
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {"status": "paused", "phase": state.get("phase")}


@router.post("/{game_id}/resume")
async def host_resume(game_id: str, req: HostActionRequest):
    state = _state_or_404(game_id)
    _verify_host(state, req.participant_id)
    state = resume_session(state, now=_utc())
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {"status": "resumed", "phase": state.get("phase")}


@router.post("/{game_id}/decision/{participant_id}")
async def coop_decision(game_id: str, participant_id: str, payload: dict[str, Any]):
    state = _state_or_404(game_id)
    if state.get("game_status") != "active":
        raise HTTPException(400, "Game is not active")
    participant = next((item for item in state.get("participants", []) if item["participant_id"] == participant_id), None)
    if not participant:
        raise HTTPException(404, "Participant not found")
    try:
        state = apply_company_decision(
            state,
            company_id=participant["company_id"],
            action=payload["action"],
            payload=payload.get("payload", {}),
            now=_utc(),
        )
    except (ValueError, KeyError) as exc:
        raise HTTPException(400, str(exc))
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {"status": "applied", "snapshot": participant_snapshot(state, participant_id=participant_id)}


@router.post("/{game_id}/auction/open")
async def open_auction_route(game_id: str, req: HostActionRequest):
    state = _state_or_404(game_id)
    _verify_host(state, req.participant_id)
    auctions = [a for a in state.get("auctions", []) if a["year"] == state.get("current_year") and a["status"] == "scheduled"]
    if not auctions:
        raise HTTPException(400, "No scheduled auctions for this year")
    auction = auctions[0]
    state = open_auction(state, auction_id=auction["auction_id"], now=_utc())
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {"status": "auction_opened", "auction_id": auction["auction_id"]}


@router.post("/{game_id}/auction/{auction_id}/bid")
async def submit_bid(game_id: str, auction_id: str, participant_id: str, payload: dict[str, Any]):
    state = _state_or_404(game_id)
    participant = next((p for p in state.get("participants", []) if p["participant_id"] == participant_id), None)
    if not participant:
        raise HTTPException(404, "Participant not found")
    try:
        state = submit_auction_bid(
            state,
            company_id=participant["company_id"],
            auction_id=auction_id,
            quantity=float(payload.get("quantity", 0)),
            price=float(payload.get("price", 0)),
            now=_utc(),
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {"status": "bid_submitted", "snapshot": participant_snapshot(state, participant_id=participant_id)}


@router.post("/{game_id}/auction/{auction_id}/close")
async def close_auction_route(game_id: str, auction_id: str, req: HostActionRequest):
    state = _state_or_404(game_id)
    _verify_host(state, req.participant_id)
    state = close_auction(state, auction_id=auction_id, now=_utc())
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {"status": "auction_closed", "auction_id": auction_id}


@router.post("/{game_id}/ready")
async def coop_ready(game_id: str, req: ReadyRequest):
    state = _state_or_404(game_id)
    try:
        set_participant_ready(state, participant_id=req.participant_id, ready=req.ready)
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {
        "status": "ready_recorded",
        "ready_check": state.get("ready_check", {}),
    }


@router.get("/{game_id}/leaderboard")
async def get_leaderboard(game_id: str):
    state = _state_or_404(game_id)
    return {
        "game_id": game_id,
        "year": state.get("current_year", 0),
        "phase": state.get("phase", ""),
        "leaderboard": build_leaderboard(state),
    }


@router.get("/{game_id}/summary")
async def coop_summary(game_id: str):
    state = _state_or_404(game_id)
    summary = build_session_summary(state)
    leaderboard = build_leaderboard(state)
    human_rows = [r for r in leaderboard if not r.get("is_bot")]
    mvp = human_rows[0] if human_rows else None
    return {
        "game_id": game_id,
        "summary": summary,
        "participants": leaderboard,
        "leaderboard": leaderboard,
        "mvp": mvp,
    }


@router.get("/{game_id}/lobby")
async def get_lobby(game_id: str):
    state = _state_or_404(game_id)
    return lobby_snapshot(state)


@router.get("/{game_id}/{participant_id}")
async def get_coop_state(game_id: str, participant_id: str):
    state = _state_or_404(game_id)
    return {
        "game_id": game_id,
        "participant_id": participant_id,
        "room_code": state.get("room_code", ""),
        "game_status": state.get("game_status", "lobby"),
        "snapshot": participant_snapshot(state, participant_id=participant_id),
    }
