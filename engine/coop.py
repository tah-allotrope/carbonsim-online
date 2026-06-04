from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from typing import Any

from .engine import build_player_snapshot, create_initial_state, start_simulation

_LOBBY_CODE_CHARS = "".join(c for c in string.ascii_uppercase + string.digits if c not in "OI01")


def generate_room_code(length: int = 6) -> str:
    return "".join(random.choices(_LOBBY_CODE_CHARS, k=length))


def create_competitive_game(
    *,
    host_name: str,
    province_name: str = "default",
    player_count: int = 2,
    difficulty: str = "standard",
    num_years: int | None = None,
) -> dict[str, Any]:
    scenario_map = {
        "easy": "solo_easy",
        "standard": "solo_standard",
        "hard": "solo_hard",
    }
    scenario = scenario_map.get(difficulty, "solo_standard")
    state = create_initial_state(
        participant_count=player_count,
        num_years=num_years or {"easy": 20, "standard": 15, "hard": 10}.get(difficulty, 15),
        scenario=scenario,
        bot_count=0,
    )
    state["province_name"] = province_name
    state["difficulty"] = difficulty
    state["game_status"] = "lobby"
    state["phase"] = "lobby"
    state["coop_mode"] = True
    state["competitive_mode"] = True
    state["max_players"] = player_count
    state["room_code"] = generate_room_code()
    state["participants"] = [
        {
            "participant_id": "P01",
            "player_name": host_name,
            "company_id": state["companies"][0]["company_id"],
            "is_host": True,
            "connected": False,
            "ready": False,
        }
    ]
    for idx, company in enumerate(state["companies"], start=1):
        company["starting_cash"] = company.get("cash", 0)
        company["controller_participant_id"] = f"P{idx:02d}" if idx == 1 else None
    state["ready_check"] = {"year": 0, "participants": {"P01": False}}
    state["year_results_history"] = []
    return state


create_coop_game = create_competitive_game


def add_competitive_participant(state: dict[str, Any], *, player_name: str) -> dict[str, Any]:
    if state.get("game_status") != "lobby":
        raise ValueError("Game is not in lobby state")
    participants = state.setdefault("participants", [])
    max_players = state.get("max_players", len(state.get("companies", [])))
    if len(participants) >= max_players:
        raise ValueError("Game is full")
    if len(participants) >= len(state.get("companies", [])):
        raise ValueError("No available company slots")
    next_index = len(participants) + 1
    available_company = next(
        (company for company in state.get("companies", []) if not company.get("controller_participant_id")),
        None,
    )
    if not available_company:
        raise ValueError("No available company slots")
    participant_id = f"P{next_index:02d}"
    available_company["controller_participant_id"] = participant_id
    participant = {
        "participant_id": participant_id,
        "player_name": player_name,
        "company_id": available_company["company_id"],
        "is_host": False,
        "connected": False,
        "ready": False,
    }
    participants.append(participant)
    state.setdefault("ready_check", {"year": 0, "participants": {}})
    state["ready_check"]["participants"][participant_id] = False
    return participant


add_coop_participant = add_competitive_participant


def set_participant_connection(state: dict[str, Any], *, participant_id: str, connected: bool) -> None:
    participant = _participant(state, participant_id)
    participant["connected"] = connected


def set_participant_ready(state: dict[str, Any], *, participant_id: str, ready: bool) -> None:
    participant = _participant(state, participant_id)
    participant["ready"] = ready
    ready_check = state.setdefault("ready_check", {"year": state.get("current_year", 0), "participants": {}})
    ready_check["year"] = state.get("current_year", 0)
    ready_check.setdefault("participants", {})[participant_id] = ready


def all_participants_ready(state: dict[str, Any]) -> bool:
    participants = state.get("participants", [])
    if not participants:
        return False
    ready_check = state.get("ready_check", {}).get("participants", {})
    return all(ready_check.get(participant["participant_id"], False) for participant in participants)


def reset_ready_check(state: dict[str, Any]) -> None:
    participants = state.get("participants", [])
    for participant in participants:
        participant["ready"] = False
    state["ready_check"] = {
        "year": state.get("current_year", 0),
        "participants": {participant["participant_id"]: False for participant in participants},
    }


def start_competitive_game(state: dict[str, Any], *, now: datetime) -> dict[str, Any]:
    if state.get("game_status") != "lobby":
        raise ValueError("Game is not in lobby state")
    participants = state.get("participants", [])
    if len(participants) < 2:
        raise ValueError("Need at least 2 players to start")
    state = start_simulation(state, now)
    state["game_status"] = "active"
    return state


def build_leaderboard(state: dict[str, Any]) -> list[dict[str, Any]]:
    participant_by_company = {
        p["company_id"]: p for p in state.get("participants", [])
    }
    rows = []
    for company in state.get("companies", []):
        participant = participant_by_company.get(company["company_id"])
        rows.append({
            "participant_id": participant["participant_id"] if participant else None,
            "player_name": participant["player_name"] if participant else company["company_name"],
            "company_id": company["company_id"],
            "company_name": company["company_name"],
            "cash": company.get("cash", 0),
            "banked_allowances": company.get("banked_allowances", 0),
            "cumulative_penalties": company.get("cumulative_penalties", 0),
            "compliance_gap": company.get("compliance_gap", 0),
            "is_bot": company.get("is_bot", False),
        })
    rows.sort(key=lambda r: (r["cumulative_penalties"], r["compliance_gap"], -r["cash"]))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows


def participant_snapshot(state: dict[str, Any], *, participant_id: str) -> dict[str, Any]:
    participant = _participant(state, participant_id)
    snapshot = build_player_snapshot(
        state,
        company_id=participant["company_id"],
        is_facilitator=False,
        participant_label=participant["player_name"],
        now=_utc(),
    )
    snapshot["coop_mode"] = True
    snapshot["competitive_mode"] = state.get("competitive_mode", False)
    snapshot["game_status"] = state.get("game_status", "lobby")
    snapshot["room_code"] = state.get("room_code", "")
    snapshot["participants"] = [
        {
            "participant_id": item["participant_id"],
            "player_name": item["player_name"],
            "company_id": item["company_id"],
            "is_host": item["is_host"],
            "connected": item["connected"],
            "ready": item["ready"],
        }
        for item in state.get("participants", [])
    ]
    snapshot["ready_check"] = state.get("ready_check", {})
    snapshot["your_participant_id"] = participant_id
    snapshot["is_host"] = participant.get("is_host", False)
    snapshot["max_players"] = state.get("max_players", 0)
    snapshot["leaderboard"] = build_leaderboard(state)
    return snapshot


def lobby_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "lobby",
        "game_id": state.get("game_id", ""),
        "room_code": state.get("room_code", ""),
        "province_name": state.get("province_name", ""),
        "difficulty": state.get("difficulty", ""),
        "max_players": state.get("max_players", 0),
        "game_status": state.get("game_status", "lobby"),
        "participants": [
            {
                "participant_id": p["participant_id"],
                "player_name": p["player_name"],
                "is_host": p["is_host"],
                "connected": p["connected"],
                "ready": p["ready"],
            }
            for p in state.get("participants", [])
        ],
    }


def _participant(state: dict[str, Any], participant_id: str) -> dict[str, Any]:
    for participant in state.get("participants", []):
        if participant["participant_id"] == participant_id:
            return participant
    raise ValueError(f"Participant not found: {participant_id}")


def _utc() -> datetime:
    return datetime.now(timezone.utc)
