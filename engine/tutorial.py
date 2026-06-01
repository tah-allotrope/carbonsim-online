from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


TUTORIAL_CARDS = [
    {
        "card_id": "tutorial_001",
        "title": "Welcome to Climate Mayor",
        "description": "This 3-year guided tutorial introduces the core loop: review your compliance gap, activate abatement, and understand what happens when you advance the year.",
        "category": "policy",
        "effect_type": "none",
        "effect_params": {},
        "prerequisites": {"min_year": 1, "max_year": 1, "required_scenario": "solo_tutorial"},
        "weight": 99,
        "choices": [
            {
                "id": "continue",
                "label": "Continue",
                "description": "Start the tutorial.",
                "effect_type": "none",
                "effect_params": {},
            }
        ],
    },
    {
        "card_id": "tutorial_002",
        "title": "Activate Your First Abatement",
        "description": "Cheap immediate abatement is usually your safest first move. Activate one measure before closing the year.",
        "category": "opportunity",
        "effect_type": "cash_boost",
        "effect_params": {"magnitude": 0.01},
        "prerequisites": {"min_year": 2, "max_year": 2, "required_scenario": "solo_tutorial"},
        "weight": 99,
        "choices": [
            {
                "id": "got_it",
                "label": "Got it",
                "description": "Proceed with a small tutorial subsidy.",
                "effect_type": "cash_boost",
                "effect_params": {"magnitude": 0.01},
            }
        ],
    },
    {
        "card_id": "tutorial_003",
        "title": "Offsets Are A Backstop",
        "description": "Offsets help close small remaining gaps, but they are capped. Use them carefully rather than relying on them for everything.",
        "category": "market",
        "effect_type": "offset_supply_change",
        "effect_params": {"magnitude": 0.05},
        "prerequisites": {"min_year": 3, "max_year": 3, "required_scenario": "solo_tutorial"},
        "weight": 99,
        "choices": [
            {
                "id": "understood",
                "label": "Understood",
                "description": "Proceed with a slight offset supply boost.",
                "effect_type": "offset_supply_change",
                "effect_params": {"magnitude": 0.05},
            }
        ],
    },
]


def mark_tutorial_state(state: dict[str, Any]) -> dict[str, Any]:
    state["tutorial_mode"] = True
    state.setdefault("tutorial_steps", [])
    return state


def tutorial_notes_for_year(year: int) -> str:
    notes = {
        1: "Review the compliance gap and what your current allowances cover.",
        2: "Activate one cheap immediate abatement measure before advancing.",
        3: "Notice how offsets can help but do not remove the need for real abatement.",
    }
    return notes.get(year, "Tutorial complete.")
