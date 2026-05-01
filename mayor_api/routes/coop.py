from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from carbonsim_engine import (
    add_coop_participant,
    all_participants_ready,
    apply_company_decision,
    build_session_summary,
    create_coop_game,
    force_advance_phase,
    participant_snapshot,
    reset_ready_check,
    set_participant_ready,
)

from ..db import create_game as db_create_game, decompress_state, get_game as db_get_game, update_game_state as db_update_game_state
from ..models import CreateCoopGameRequest, JoinCoopRequest, ReadyRequest
from .game import _utc
from ..ws import manager as ws_manager

router = APIRouter(prefix="/api/coop", tags=["coop"])


def _state_or_404(game_id: str) -> dict[str, Any]:
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    return decompress_state(row["state_json"])


@router.post("")
async def create_coop_route(req: CreateCoopGameRequest):
    import uuid

    game_id = str(uuid.uuid4())
    state = create_coop_game(
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
        "participant_id": participant["participant_id"],
        "player_count": req.player_count,
        "snapshot": participant_snapshot(state, participant_id=participant["participant_id"]),
    }


@router.post("/{game_id}/join")
async def join_coop_route(game_id: str, req: JoinCoopRequest):
    state = _state_or_404(game_id)
    if not state.get("coop_mode"):
        raise HTTPException(400, "Game is not a co-op session")
    try:
        participant = add_coop_participant(state, player_name=req.player_name)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {
        "game_id": game_id,
        "participant_id": participant["participant_id"],
        "snapshot": participant_snapshot(state, participant_id=participant["participant_id"]),
    }


@router.post("/{game_id}/decision/{participant_id}")
async def coop_decision(game_id: str, participant_id: str, payload: dict[str, Any]):
    state = _state_or_404(game_id)
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


@router.post("/{game_id}/ready")
async def coop_ready(game_id: str, req: ReadyRequest):
    state = _state_or_404(game_id)
    try:
        set_participant_ready(state, participant_id=req.participant_id, ready=req.ready)
    except ValueError as exc:
        raise HTTPException(404, str(exc))

    advanced = False
    if all_participants_ready(state):
        state = force_advance_phase(state, now=_utc())
        reset_ready_check(state)
        advanced = True

    db_update_game_state(game_id, state)
    await ws_manager.broadcast_snapshot(game_id)
    return {
        "status": "ready_recorded",
        "advanced": advanced,
        "phase": state.get("phase"),
        "ready_check": state.get("ready_check", {}),
    }


@router.get("/{game_id}/summary")
async def coop_summary(game_id: str):
    state = _state_or_404(game_id)
    summary = build_session_summary(state)
    participant_rows = []
    participant_by_company = {
        participant["company_id"]: participant for participant in state.get("participants", [])
    }
    for company in state.get("companies", []):
        participant = participant_by_company.get(company["company_id"])
        participant_rows.append(
            {
                "participant_id": participant["participant_id"] if participant else None,
                "player_name": participant["player_name"] if participant else company["company_name"],
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "cash": company.get("cash", 0),
                "cumulative_penalties": company.get("cumulative_penalties", 0),
                "compliance_gap": company.get("compliance_gap", 0),
            }
        )
    mvp = min(participant_rows, key=lambda row: (row["cumulative_penalties"], row["compliance_gap"], -row["cash"])) if participant_rows else None
    return {
        "game_id": game_id,
        "summary": summary,
        "participants": participant_rows,
        "mvp": mvp,
    }


@router.get("/{game_id}/{participant_id}")
async def get_coop_state(game_id: str, participant_id: str):
    state = _state_or_404(game_id)
    return {
        "game_id": game_id,
        "participant_id": participant_id,
        "snapshot": participant_snapshot(state, participant_id=participant_id),
    }
