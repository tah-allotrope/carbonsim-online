from __future__ import annotations

import json
import sys
from pathlib import Path

VALID_CATEGORIES = {"crisis", "opportunity", "policy", "market"}

VALID_EFFECT_TYPES = {
    "emissions_spike", "allowance_withdrawal", "cost_shock",
    "offset_supply_change", "tech_unlock", "fdi_proposal",
    "cbam_threat", "election_pressure", "allowance_boost",
    "cash_boost", "none",
}

REQUIRED_FIELDS = {"card_id", "title", "description", "category", "effect_type", "effect_params", "prerequisites", "weight"}


def validate_card(card: dict, index: int) -> list[str]:
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in card:
            errors.append(f"Card #{index}: missing required field '{field}'")

    if "card_id" in card:
        cid = card["card_id"]
        parts = cid.split("_")
        if len(parts) != 2 or parts[0] not in VALID_CATEGORIES:
            errors.append(f"Card #{index}: card_id '{cid}' should be category_XXX (e.g. crisis_001)")

    cat = card.get("category", "")
    if cat not in VALID_CATEGORIES:
        errors.append(f"Card #{index}: invalid category '{cat}' (valid: {VALID_CATEGORIES})")

    etype = card.get("effect_type", "")
    if etype not in VALID_EFFECT_TYPES:
        errors.append(f"Card #{index}: invalid effect_type '{etype}' (valid: {VALID_EFFECT_TYPES})")

    if not isinstance(card.get("effect_params", None), dict):
        errors.append(f"Card #{index}: effect_params must be a dict")

    prereqs = card.get("prerequisites", {})
    if not isinstance(prereqs, dict):
        errors.append(f"Card #{index}: prerequisites must be a dict")
    else:
        for key in prereqs:
            if key not in {"min_year", "max_year", "min_cash", "max_penalties"}:
                errors.append(f"Card #{index}: unknown prerequisite '{key}'")

    weight = card.get("weight", 1)
    if not isinstance(weight, (int, float)) or weight <= 0:
        errors.append(f"Card #{index}: weight must be a positive number")

    if "title" in card and (len(card["title"]) < 3 or len(card["title"]) > 80):
        errors.append(f"Card #{index}: title length must be 3-80 chars")

    if "description" in card and len(card["description"]) < 20:
        errors.append(f"Card #{index}: description too short ({len(card['description'])} chars, min 20)")

    choices = card.get("choices", [])
    if not isinstance(choices, list):
        errors.append(f"Card #{index}: choices must be a list")
    else:
        for ci, choice in enumerate(choices):
            if "id" not in choice or "label" not in choice or "description" not in choice:
                errors.append(f"Card #{index} choice #{ci}: missing id/label/description")
            ce = choice.get("effect_type", "")
            if ce not in VALID_EFFECT_TYPES:
                errors.append(f"Card #{index} choice #{ci}: invalid effect_type '{ce}'")

    return errors


def validate_deck(filepath: str) -> int:
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: File not found: {filepath}")
        return 1

    with open(path) as f:
        data = json.load(f)

    cards = data if isinstance(data, list) else data.get("cards", data.get("deck", []))
    if not isinstance(cards, list):
        print("ERROR: Deck must be a JSON array or have a 'cards' key")
        return 1

    print(f"Loaded {len(cards)} card(s) from {filepath}")
    print()

    total_errors = 0
    categories: dict[str, int] = {}
    effect_types: dict[str, int] = {}
    card_ids: set[str] = set()

    for i, card in enumerate(cards):
        cid = card.get("card_id", f"card_{i}")
        if cid in card_ids:
            print(f"  WARNING: Duplicate card_id '{cid}'")
        card_ids.add(cid)

        cat = card.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

        etype = card.get("effect_type", "unknown")
        effect_types[etype] = effect_types.get(etype, 0) + 1

        errors = validate_card(card, i)
        if errors:
            total_errors += len(errors)
            for err in errors:
                print(f"  FAIL: {err}")

    print()
    print("--- Category Distribution ---")
    for cat in sorted(categories):
        print(f"  {cat}: {categories[cat]}")

    print()
    print("--- Effect Type Distribution ---")
    for etype in sorted(effect_types):
        print(f"  {etype}: {effect_types[etype]}")

    print()
    if total_errors == 0:
        print(f"RESULT: {len(cards)} valid cards, 0 errors")
        return 0
    else:
        print(f"RESULT: {total_errors} error(s) found in {len(cards)} cards")
        return 1


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m carbonsim_engine.scripts.validate_deck <deck.json>")
        sys.exit(1)
    rc = validate_deck(sys.argv[1])
    sys.exit(rc)


if __name__ == "__main__":
    main()
