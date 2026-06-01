from __future__ import annotations

import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .cards import CardDeck, draw_cards, resolve_card
from .solo import create_solo_game
from .engine import force_advance_phase, run_bot_turns, build_session_summary, build_session_analytics


def run_playtest(seed: int, difficulty: str = "standard", years: int | None = None) -> dict[str, Any]:
    state = create_solo_game(player_name=f"bot-{seed}", difficulty=difficulty, num_years=years)
    rng = random.Random(seed)
    deck_paths = _deck_paths()
    deck = CardDeck.from_paths(*deck_paths, rng=rng)
    card_counter: Counter[str] = Counter()

    while state.get("phase") != "complete":
        now = datetime.now(timezone.utc)
        state = force_advance_phase(state, now=now)
        if state.get("phase") == "decision_window":
            state, drawn = draw_cards(state, deck, count=3, now=now)
            for card in drawn:
                card_counter[card["card_id"]] += 1
                choice_id = None
                choices = card.get("choices") or []
                if choices:
                    choice_id = choices[0]["id"]
                state = resolve_card(state, card, choice_id=choice_id, now=now)
            state["drawn_cards"] = []
        state = run_bot_turns(state, now=now)
        while state.get("phase") not in {"year_start", "complete"}:
            state = force_advance_phase(state, now=now)

    summary = build_session_summary(state)
    analytics = build_session_analytics(state)
    player = next(company for company in state["companies"] if not company.get("is_bot"))
    return {
        "seed": seed,
        "difficulty": difficulty,
        "completed_years": state.get("current_year", 0),
        "final_cash": player.get("cash", 0),
        "total_penalties": player.get("cumulative_penalties", 0),
        "compliance_gap": player.get("compliance_gap", 0),
        "card_frequency": dict(card_counter),
        "summary": summary,
        "analytics": analytics,
    }


def run_playtest_batch(output_path: str | Path, runs_per_difficulty: int = 4) -> dict[str, Any]:
    results = []
    seed = 1
    for difficulty in ("easy", "standard", "hard"):
        for _ in range(runs_per_difficulty):
            results.append(run_playtest(seed=seed, difficulty=difficulty))
            seed += 1

    aggregate = summarize_playtests(results)
    Path(output_path).write_text(json.dumps({"results": results, "aggregate": aggregate}, indent=2), encoding="utf-8")
    return aggregate


def summarize_playtests(results: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {"by_difficulty": {}, "card_frequency": {}}
    card_counter: Counter[str] = Counter()
    for result in results:
        bucket = aggregate["by_difficulty"].setdefault(result["difficulty"], {
            "runs": 0,
            "completed": 0,
            "avg_final_cash": 0.0,
            "avg_penalties": 0.0,
        })
        bucket["runs"] += 1
        bucket["completed"] += 1 if result["completed_years"] > 0 else 0
        bucket["avg_final_cash"] += result["final_cash"]
        bucket["avg_penalties"] += result["total_penalties"]
        card_counter.update(result.get("card_frequency", {}))

    for bucket in aggregate["by_difficulty"].values():
        if bucket["runs"]:
            bucket["avg_final_cash"] = round(bucket["avg_final_cash"] / bucket["runs"], 2)
            bucket["avg_penalties"] = round(bucket["avg_penalties"] / bucket["runs"], 2)
            bucket["completion_rate"] = round(bucket["completed"] / bucket["runs"], 2)

    aggregate["card_frequency"] = dict(card_counter)
    aggregate["dead_cards"] = [card_id for card_id, count in card_counter.items() if count == 0]
    return aggregate


def _deck_paths() -> list[Path]:
    base = Path(__file__).parent / "data"
    return [base / "starter_deck.json", base / "expansion_deck.json"]
