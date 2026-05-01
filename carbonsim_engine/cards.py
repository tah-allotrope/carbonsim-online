from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .engine import apply_shock

_EFFECT_TYPES = frozenset({
    "emissions_spike", "allowance_withdrawal", "cost_shock",
    "offset_supply_change", "tech_unlock", "fdi_proposal",
    "cbam_threat", "election_pressure", "allowance_boost",
    "cash_boost", "none",
})


class CardDeck:
    def __init__(self, cards: list[dict[str, Any]], rng: random.Random | None = None):
        self._cards = list(cards)
        self._discard: list[dict[str, Any]] = []
        self._rng = rng or random.Random()

    @classmethod
    def from_json(cls, path_or_str: str | Path, rng: random.Random | None = None) -> CardDeck:
        p = Path(path_or_str)
        if p.exists():
            with open(p) as f:
                data = json.load(f)
        else:
            data = json.loads(str(path_or_str))
        cards = data if isinstance(data, list) else data.get("cards", data.get("deck", data))
        return cls(cards, rng)

    @classmethod
    def from_paths(
        cls,
        *paths: str | Path,
        rng: random.Random | None = None,
    ) -> CardDeck:
        cards: list[dict[str, Any]] = []
        for path in paths:
            deck = cls.from_json(path, rng=random.Random(0))
            cards.extend(deck._cards)
        return cls(cards, rng)

    def draw(self, count: int = 3, state: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        eligible = [c for c in self._cards if _prereqs_met(c, state)]
        if len(eligible) < count:
            self._reshuffle()
            eligible = [c for c in self._cards if _prereqs_met(c, state)]

        weights = [max(c.get("weight", 1), 0.1) for c in eligible]
        drawn: list[dict[str, Any]] = []
        used_indices: set[int] = set()

        for _ in range(min(count, len(eligible))):
            idx = _weighted_choice(weights, used_indices, self._rng)
            if idx is None:
                break
            used_indices.add(idx)
            drawn.append(eligible[idx])

        for card in drawn:
            self._cards.remove(card)
            self._discard.append(card)

        return drawn

    def _reshuffle(self) -> None:
        self._cards.extend(self._discard)
        self._discard.clear()
        self._rng.shuffle(self._cards)

    @property
    def remaining(self) -> int:
        return len(self._cards)

    @property
    def discarded(self) -> int:
        return len(self._discard)


def _prereqs_met(card: dict[str, Any], state: dict[str, Any] | None) -> bool:
    if state is None:
        return True
    prereqs = card.get("prerequisites", {})
    year = state.get("current_year", 0)
    if "min_year" in prereqs and year < prereqs["min_year"]:
        return False
    if "max_year" in prereqs and year > prereqs["max_year"]:
        return False
    if "min_cash" in prereqs:
        cash_values = [c.get("cash", 0) for c in state.get("companies", [])]
        if max(cash_values) < prereqs["min_cash"]:
            return False
    if "max_penalties" in prereqs:
        penalty_count = sum(
            1 for c in state.get("companies", []) if c.get("cumulative_penalties", 0) > 0
        )
        if penalty_count > prereqs["max_penalties"]:
            return False
    if "min_offset_cap" in prereqs and state.get("offset_usage_cap", 0) < prereqs["min_offset_cap"]:
        return False
    if "required_scenario" in prereqs and state.get("scenario") != prereqs["required_scenario"]:
        return False
    return True


def _weighted_choice(weights: list[float], excluded: set[int], rng: random.Random) -> int | None:
    total = sum(w for i, w in enumerate(weights) if i not in excluded)
    if total <= 0:
        return None
    r = rng.uniform(0, total)
    running = 0.0
    for i, w in enumerate(weights):
        if i in excluded:
            continue
        running += w
        if r <= running:
            return i
    return None


def resolve_card(
    state: dict[str, Any],
    card: dict[str, Any],
    choice_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)

    effect_type = card.get("effect_type", "none")
    effect_params = dict(card.get("effect_params", {}))

    if choice_id and card.get("choices"):
        match = [c for c in card["choices"] if c["id"] == choice_id]
        if match:
            chosen = match[0]
            chosen_effect = chosen.get("effect_type", "none")
            if chosen_effect != "none":
                effect_type = chosen_effect
                effect_params = dict(chosen.get("effect_params", {}))

    if effect_type != "none":
        magnitude = effect_params.get("magnitude", 0.1)
        shock_params = {k: v for k, v in effect_params.items() if k != "magnitude"}
        state = apply_shock(
            state,
            shock_type=effect_type,
            magnitude=magnitude,
            shock_params=shock_params,
            now=now,
        )

    _append_event(state, "card_resolved", now, {
        "card_id": card["card_id"],
        "title": card["title"],
        "category": card["category"],
        "choice_id": choice_id,
        "effect_type": effect_type,
        "year": state.get("current_year", 0),
    })

    return state


def draw_cards(
    state: dict[str, Any],
    deck: CardDeck,
    count: int = 3,
    now: datetime | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    now = now or datetime.now(timezone.utc)
    drawn = deck.draw(count=count, state=state)
    for card in drawn:
        _append_event(state, "card_drawn", now, {
            "card_id": card["card_id"],
            "title": card["title"],
            "category": card["category"],
            "year": state.get("current_year", 0),
        })
    return state, drawn


def _append_event(
    state: dict[str, Any],
    event_type: str,
    timestamp: datetime,
    details: dict[str, Any],
) -> None:
    from .engine import _event_summary, _serialize_time
    state.setdefault("audit_log", []).append({
        "timestamp": _serialize_time(timestamp),
        "year": state.get("current_year", 0),
        "event_type": event_type,
        "details": details,
        "summary": _event_summary(event_type, details),
    })
