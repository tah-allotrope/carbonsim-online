from __future__ import annotations

import tempfile
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
from carbonsim_engine.achievements import compute_achievements
from carbonsim_engine.cards import CardDeck, draw_cards, resolve_card
from carbonsim_engine.playtest import run_playtest_batch
from carbonsim_engine.solo import create_solo_game, solo_player_company
from carbonsim_engine.tutorial import TUTORIAL_CARDS, tutorial_notes_for_year

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
    FastForwardRequest,
    GameListItem,
    GameStateResponse,
    PlaytestResponse,
    ResolveCardRequest,
    SaveGameRequest,
    SaveListItem,
    SummaryResponse,
)

router = APIRouter(prefix="/api/games", tags=["games"])

STARTER_DECK_PATH = None
EXPANSION_DECK_PATH = None
try:
    from pathlib import Path
    _p = Path(__file__).parent.parent.parent / "carbonsim_engine" / "data" / "starter_deck.json"
    if _p.exists():
        STARTER_DECK_PATH = str(_p)
    _exp = Path(__file__).parent.parent.parent / "carbonsim_engine" / "data" / "expansion_deck.json"
    if _exp.exists():
        EXPANSION_DECK_PATH = str(_exp)
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
        actions.append("fast_forward")
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
        tutorial_mode=req.tutorial_mode,
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
        drawn_cards=state.get("drawn_cards", []),
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
    if phase == "decision_window":
        import random
        if state.get("tutorial_mode"):
            drawn_cards = [
                card
                for card in TUTORIAL_CARDS
                if card.get("prerequisites", {}).get("min_year") == state.get("current_year")
            ]
        elif STARTER_DECK_PATH:
            if EXPANSION_DECK_PATH:
                deck = CardDeck.from_paths(
                    STARTER_DECK_PATH,
                    EXPANSION_DECK_PATH,
                    rng=random.Random(hash((game_id, state.get("current_year", 0)))),
                )
            else:
                deck = CardDeck.from_json(
                    STARTER_DECK_PATH,
                    rng=random.Random(hash((game_id, state.get("current_year", 0)))),
                )
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
        "tutorial_note": tutorial_notes_for_year(state.get("current_year", 0)) if state.get("tutorial_mode") else None,
    }


@router.post("/{game_id}/fast-forward")
async def fast_forward(game_id: str, req: FastForwardRequest):
    row = db_get_game(game_id)
    if not row:
        raise HTTPException(404, "Game not found")
    state = decompress_state(row["state_json"])

    for _ in range(req.years):
        if state.get("phase") == "complete":
            break

        now = _utc()
        while state.get("phase") == "compliance":
            state = force_advance_phase(state, now=now)
        if state.get("phase") == "complete":
            state["game_status"] = "completed"
            break

        if state.get("phase") == "year_start":
            state = force_advance_phase(state, now=now)

        if state.get("phase") == "decision_window":
            player = solo_player_company(state)
            if not player:
                raise HTTPException(400, "No player company found")

            available = [
                measure
                for measure in player.get("abatement_menu", [])
                if measure["measure_id"] not in player.get("active_abatement_ids", [])
                and measure["measure_id"] not in player.get("pending_abatement_ids", [])
            ]
            if available:
                cheapest = sorted(
                    available,
                    key=lambda m: m["cost"] / max(m["abatement_amount"], 0.01),
                )[0]
                try:
                    state = apply_company_decision(
                        state,
                        company_id=player["company_id"],
                        action="activate_abatement",
                        payload={"measure_id": cheapest["measure_id"]},
                        now=now,
                    )
                except Exception:
                    pass

            player = solo_player_company(state)
            gap = max(0.0, player.get("compliance_gap", 0)) if player else 0.0
            if gap > 0:
                qty = round(gap * 0.25, 2)
                if qty > 0:
                    try:
                        state = apply_company_decision(
                            state,
                            company_id=player["company_id"],
                            action="buy_offsets",
                            payload={"quantity": qty},
                            now=now,
                        )
                    except Exception:
                        pass

        state["drawn_cards"] = []
        state = run_bot_turns(state, now=now)
        while state.get("phase") not in ("year_start", "complete"):
            state = force_advance_phase(state, now=now)
        if state.get("phase") == "complete":
            state["game_status"] = "completed"
            break

    db_update_game_state(game_id, state)
    return {
        "status": "fast_forwarded",
        "current_year": state.get("current_year", 0),
        "phase": state.get("phase"),
        "snapshot": _snapshot(state),
    }


@router.post("/playtest", response_model=PlaytestResponse)
async def playtest_route():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as report_file:
        report_path = report_file.name
    try:
        aggregate = run_playtest_batch(report_path, runs_per_difficulty=4)
    finally:
        from pathlib import Path

        Path(report_path).unlink(missing_ok=True)
    return PlaytestResponse(aggregate=aggregate)


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
        achievements=compute_achievements(state),
    )


@router.delete("/{game_id}")
async def delete_game_route(game_id: str):
    if not db_delete_game(game_id):
        raise HTTPException(404, "Game not found")
    return {"status": "deleted"}
