from __future__ import annotations

from .engine import create_initial_state, start_simulation
from .scenarios import SCENARIO_PACKS

SOLO_SCENARIO_MAP = {
    "easy": "solo_easy",
    "standard": "solo_standard",
    "hard": "solo_hard",
}

BOT_COUNT_MAP = {
    "easy": 2,
    "standard": 3,
    "hard": 5,
}


def create_solo_game(
    player_name: str = "Player",
    province_name: str = "default",
    difficulty: str = "standard",
    num_years: int | None = None,
) -> dict:
    scenario_key = SOLO_SCENARIO_MAP.get(difficulty, "solo_standard")
    bot_count = BOT_COUNT_MAP.get(difficulty, 3)
    pack = SCENARIO_PACKS.get(scenario_key, SCENARIO_PACKS["solo_standard"])

    if num_years is None:
        num_years = pack.get("num_years", 15)

    state = create_initial_state(
        participant_count=1,
        num_years=num_years,
        scenario=scenario_key,
        bot_count=bot_count,
    )

    state = start_simulation(state, _utc_now())
    state["player_name"] = player_name
    state["province_name"] = province_name
    state["difficulty"] = difficulty
    state["game_status"] = "active"
    state["drawn_cards"] = []

    return state


def solo_player_company(state: dict) -> dict | None:
    for company in state.get("companies", []):
        if not company.get("is_bot"):
            return company
    return None


def _utc_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
