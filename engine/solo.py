from __future__ import annotations

from .constants import (
    BOT_STRATEGY_AGGRESSIVE,
    BOT_STRATEGY_CONSERVATIVE,
    BOT_STRATEGY_MODERATE,
    BOT_STRATEGY_OPPORTUNISTIC,
    BOT_STRATEGY_SPECULATOR,
)
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

# Deterministic strategy mix so a solo player faces a varied field of opponents
# rather than a wall of identical moderate bots. Harder difficulties skew toward
# the more demanding opportunistic/speculator profiles.
SOLO_STRATEGY_ROTATION = {
    "easy": [BOT_STRATEGY_CONSERVATIVE, BOT_STRATEGY_MODERATE],
    "standard": [
        BOT_STRATEGY_MODERATE,
        BOT_STRATEGY_AGGRESSIVE,
        BOT_STRATEGY_OPPORTUNISTIC,
    ],
    "hard": [
        BOT_STRATEGY_AGGRESSIVE,
        BOT_STRATEGY_OPPORTUNISTIC,
        BOT_STRATEGY_SPECULATOR,
        BOT_STRATEGY_MODERATE,
        BOT_STRATEGY_CONSERVATIVE,
    ],
}


def create_solo_game(
    player_name: str = "Player",
    province_name: str = "default",
    difficulty: str = "standard",
    num_years: int | None = None,
    tutorial_mode: bool = False,
    jurisdiction: str | None = None,
) -> dict:
    scenario_key = "solo_tutorial" if tutorial_mode else SOLO_SCENARIO_MAP.get(difficulty, "solo_standard")
    bot_count = BOT_COUNT_MAP.get(difficulty, 3)
    pack = SCENARIO_PACKS.get(scenario_key, SCENARIO_PACKS["solo_standard"])

    if num_years is None:
        num_years = pack.get("num_years", 15)

    state = create_initial_state(
        participant_count=1,
        num_years=num_years,
        scenario=scenario_key,
        bot_count=bot_count,
        jurisdiction=jurisdiction,
    )

    # Assign a varied strategy mix across the bot field (Sprint 3). Done before
    # start_simulation so agents read their strategy from year 1.
    rotation = SOLO_STRATEGY_ROTATION.get(difficulty, SOLO_STRATEGY_ROTATION["standard"])
    bot_index = 0
    for company in state.get("companies", []):
        if company.get("is_bot"):
            company["bot_strategy"] = rotation[bot_index % len(rotation)]
            bot_index += 1

    state = start_simulation(state, _utc_now())
    state["player_name"] = player_name
    state["province_name"] = province_name
    state["difficulty"] = difficulty
    state["game_status"] = "active"
    state["drawn_cards"] = []
    state["starting_year"] = 1
    for company in state.get("companies", []):
        company["starting_cash"] = company.get("cash", 0)
    if tutorial_mode:
        state["tutorial_mode"] = True
        state["tutorial_completed"] = False

    return state


def solo_player_company(state: dict) -> dict | None:
    for company in state.get("companies", []):
        if not company.get("is_bot"):
            return company
    return None


def _utc_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
