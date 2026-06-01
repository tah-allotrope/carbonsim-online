from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .engine import build_player_snapshot, create_initial_state, start_simulation


def create_coop_game(
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
    state = start_simulation(state, _utc())
    state["province_name"] = province_name
    state["difficulty"] = difficulty
    state["game_status"] = "active"
    state["coop_mode"] = True
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
    state["ready_check"] = {"year": state.get("current_year", 0), "participants": {"P01": False}}
    return state


def add_coop_participant(state: dict[str, Any], *, player_name: str) -> dict[str, Any]:
    participants = state.setdefault("participants", [])
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
    state.setdefault("ready_check", {"year": state.get("current_year", 0), "participants": {}})
    state["ready_check"]["participants"][participant_id] = False
    return participant


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
    return snapshot


def _participant(state: dict[str, Any], participant_id: str) -> dict[str, Any]:
    for participant in state.get("participants", []):
        if participant["participant_id"] == participant_id:
            return participant
    raise ValueError(f"Participant not found: {participant_id}")


def _utc() -> datetime:
    return datetime.now(timezone.utc)
