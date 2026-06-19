"""One-shot content tool: add a two-option dilemma to every event card.

Every card gains exactly two choices:

* an "accept" choice with ``effect_type: none`` — resolve_card falls back to the
  card's own base effect, so the designer-authored effect/sign is preserved
  untouched;
* an "alternative" choice that uses a different, sign-unambiguous effect type so
  the player faces a real trade-off (cash vs. compliance, liquidity vs.
  capability) without us having to second-guess each card's base magnitude sign.

Run from the repo root:  python scripts/seed_card_choices.py
Re-runnable and idempotent (it overwrites any existing ``choices``).
"""
from __future__ import annotations

import json
from pathlib import Path

DECKS = ["engine/data/starter_deck.json", "engine/data/expansion_deck.json"]

UPSIDE = {"cash_boost", "allowance_boost", "fdi_proposal", "tech_unlock"}

ACCEPT_LABEL_BY_CATEGORY = {
    "crisis": "Absorb the impact",
    "policy": "Comply with the ruling",
    "market": "Ride it out",
    "opportunity": "Proceed as planned",
}

# Alternative path keyed by base effect_type: (label, description, effect_type, params)
ALT_BY_EFFECT = {
    "emissions_spike": (
        "Throttle production",
        "Cut output to keep emissions down — protecting compliance at a cash cost.",
        "cost_shock", {"magnitude": 0.06},
    ),
    "cost_shock": (
        "Defer the cost",
        "Postpone the spending, but cutting corners pushes emissions higher this year.",
        "emissions_spike", {"magnitude": 0.06},
    ),
    "allowance_withdrawal": (
        "Buy back on the market",
        "Replace the withdrawn allowances by purchasing instead of taking the cut.",
        "cost_shock", {"magnitude": 0.05},
    ),
    "cbam_threat": (
        "Pre-comply early",
        "Invest now to meet the border standard and blunt the penalty escalation.",
        "cost_shock", {"magnitude": 0.05},
    ),
    "election_pressure": (
        "Fund the campaign",
        "Spend politically to steer the outcome rather than accept the allocation drift.",
        "cost_shock", {"magnitude": 0.05},
    ),
    "offset_supply_change": (
        "Hedge with spending",
        "Spend to insulate operations from the shifting offset market.",
        "cost_shock", {"magnitude": 0.04},
    ),
    "cash_boost": (
        "Reinvest in clean tech",
        "Forgo the cash and channel it into a new abatement option instead.",
        "tech_unlock", {},
    ),
    "allowance_boost": (
        "Sell the surplus",
        "Convert the extra allowances into cash rather than banking them.",
        "cash_boost", {"magnitude": 0.06},
    ),
    "fdi_proposal": (
        "Demand tech transfer",
        "Trade the cash injection for a clause that unlocks a new abatement option.",
        "tech_unlock", {},
    ),
    "tech_unlock": (
        "License it for cash",
        "Sell the technology rights for an immediate cash boost instead of deploying it.",
        "cash_boost", {"magnitude": 0.06},
    ),
}

# Opportunity cards stay upside-flavoured even when the base is offset_supply_change.
OPPORTUNITY_OVERRIDE = {
    "offset_supply_change": (
        "Take a cash grant instead",
        "Decline the expanded offset access in exchange for an immediate cash grant.",
        "cash_boost", {"magnitude": 0.05},
    ),
}


def build_choices(card: dict) -> list[dict]:
    etype = card["effect_type"]
    category = card["category"]

    if etype in UPSIDE:
        accept_label = "Accept the offer"
        accept_desc = "Take the opportunity as presented."
    else:
        accept_label = ACCEPT_LABEL_BY_CATEGORY.get(category, "Proceed")
        accept_desc = "Let the situation play out and take the consequences as they come."

    alt = None
    if category == "opportunity" and etype in OPPORTUNITY_OVERRIDE:
        alt = OPPORTUNITY_OVERRIDE[etype]
    elif etype in ALT_BY_EFFECT:
        alt = ALT_BY_EFFECT[etype]

    choices = [
        {
            "id": "accept",
            "label": accept_label,
            "description": accept_desc,
            "effect_type": "none",
            "effect_params": {},
        }
    ]
    if alt:
        label, desc, alt_type, alt_params = alt
        choices.append(
            {
                "id": "alt",
                "label": label,
                "description": desc,
                "effect_type": alt_type,
                "effect_params": alt_params,
            }
        )
    return choices


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    for rel in DECKS:
        path = root / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        cards = data["cards"] if isinstance(data, dict) else data
        for card in cards:
            card["choices"] = build_choices(card)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{rel}: added choices to {len(cards)} cards")


if __name__ == "__main__":
    main()
