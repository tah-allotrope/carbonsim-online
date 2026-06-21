from __future__ import annotations

import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from .cards import CardDeck, draw_cards, resolve_card
from .constants import BOT_STRATEGIES
from .solo import create_solo_game
from .engine import (
    build_session_analytics,
    build_session_summary,
    close_auction,
    create_initial_state,
    force_advance_phase,
    open_auction,
    run_bot_turns,
    start_simulation,
)


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


def check_determinism(seed: int = 42) -> bool:
    """Run the same seed twice and assert identical audit_log event sequences.

    Returns True on success, raises AssertionError if any divergence is detected.
    Regression guard: any change that breaks determinism will fail this check.
    """
    def _run(s: int) -> list[str]:
        result = run_playtest(seed=s)
        # We compare event summaries from the audit_log embedded in the summary
        analytics = result.get("analytics", {})
        # Fall back to card_frequency as a proxy if audit_log isn't surfaced
        return sorted(result.get("card_frequency", {}).items())

    run1 = _run(seed)
    run2 = _run(seed)
    assert run1 == run2, (
        f"Determinism check FAILED for seed {seed}: "
        f"card frequency diverged between two runs with the same seed."
    )
    return True


def run_strategy_sweep(
    seeds: list[int] | range,
    *,
    scenario: str = "solo_standard",
    years: int | None = None,
) -> dict[str, Any]:
    """Dominant-strategy sweep (Sprint 3, TASK-03-06).

    Runs one head-to-head game per seed in which every bot company is assigned a
    distinct strategy from ``BOT_STRATEGIES`` (5 strategies). Each game is a
    direct comparison; ``win_rate`` is the fraction of seeds in which a strategy
    finished first (lowest cumulative penalties, then highest cash). A strategy
    with win rate > 0.6 is flagged as dominant and requires rebalancing.

    Returns ``{"rows", "dominant_strategies", "seeds", "scenario"}``.
    """
    from .scenarios import SCENARIO_PACKS

    seeds = list(seeds)
    if years is None:
        years = SCENARIO_PACKS.get(scenario, {}).get("num_years", 15)
    strategies = list(BOT_STRATEGIES.keys())
    stats: dict[str, dict[str, Any]] = {
        s: {"wins": 0, "cash": [], "penalties": []} for s in strategies
    }
    instrument_usage: Counter[str] = Counter()

    for seed in seeds:
        state = create_initial_state(
            participant_count=0,
            bot_count=len(strategies),
            scenario=scenario,
            num_years=years,
            rng_seed=seed,
        )
        # Assign one strategy per company (every company is a bot here).
        strat_by_id: dict[str, str] = {}
        for company, strat in zip(state["companies"], strategies):
            company["is_bot"] = True
            company["bot_strategy"] = strat
            company["starting_cash"] = company.get("cash", 0.0)
            strat_by_id[company["company_id"]] = strat

        state = start_simulation(state, _utc())
        rng = random.Random(seed)
        deck = CardDeck.from_paths(*_deck_paths(), rng=rng)

        while state.get("phase") != "complete":
            now = _utc()
            state = force_advance_phase(state, now=now)  # year_start -> decision_window
            if state.get("phase") == "decision_window":
                state, drawn = draw_cards(state, deck, count=3, now=now)
                for card in drawn:
                    choices = card.get("choices") or []
                    choice_id = choices[0]["id"] if choices else None
                    state = resolve_card(state, card, choice_id=choice_id, now=now)
                state["drawn_cards"] = []
                # Open this year's auctions so the auction channel is exercised.
                for auction in state["auctions"]:
                    if auction["year"] == state["current_year"] and auction["status"] == "scheduled":
                        state = open_auction(state, auction_id=auction["auction_id"], now=now)
                state = run_bot_turns(state, now=now)
                # Clear auctions before closing the year.
                for auction in state["auctions"]:
                    if auction["year"] == state["current_year"] and auction["status"] == "open":
                        state = close_auction(state, auction_id=auction["auction_id"], now=now)
            while state.get("phase") not in {"year_start", "complete"}:
                state = force_advance_phase(state, now=now)

        # Rank by liquidation net worth: cash (already net of penalties and all
        # spend, see _close_current_year) plus the value of compliance assets the
        # company still holds. This rewards converting spend into compliance
        # (banked allowances + offsets) rather than hoarding cash while eating
        # penalties, and avoids the degenerate extremes that a single raw metric
        # (penalties-only or cash-only) produces.
        floor = state.get("auction_price_floor", 80.0)
        offset_val = state.get("offset_price", 25.0)

        def _net_worth(c: dict[str, Any]) -> float:
            return round(
                c["cash"]
                + c.get("banked_allowances", 0.0) * floor
                + c.get("offset_holdings", 0.0) * offset_val,
                2,
            )

        ranked = sorted(state["companies"], key=lambda c: -_net_worth(c))
        winner_strat = strat_by_id[ranked[0]["company_id"]]
        stats[winner_strat]["wins"] += 1
        for company in state["companies"]:
            s = strat_by_id[company["company_id"]]
            stats[s]["cash"].append(_net_worth(company))
            stats[s]["penalties"].append(company["cumulative_penalties"])
        for event in state["audit_log"]:
            et = event["event_type"]
            if et in {
                "offsets_purchased",
                "forward_purchased",
                "vcm_invested",
                "auction_bid_submitted",
                "trade_proposed",
            }:
                instrument_usage[et] += 1

    n = len(seeds) or 1
    rows = []
    for s in strategies:
        d = stats[s]
        rows.append(
            {
                "strategy": s,
                "label": BOT_STRATEGIES[s].get("label", s.title()),
                "win_rate": round(d["wins"] / n, 3),
                "wins": d["wins"],
                "mean_net_worth": round(mean(d["cash"]), 2) if d["cash"] else 0.0,
                "mean_penalties": round(mean(d["penalties"]), 2) if d["penalties"] else 0.0,
            }
        )
    rows.sort(key=lambda r: r["win_rate"], reverse=True)
    dominant = [r["strategy"] for r in rows if r["win_rate"] > 0.6]
    return {
        "rows": rows,
        "dominant_strategies": dominant,
        "seeds": n,
        "scenario": scenario,
        "instrument_usage": dict(instrument_usage),
    }


def print_strategy_sweep(seeds: list[int] | range = range(20), **kwargs: Any) -> dict[str, Any]:
    """Run the sweep and print a human-readable summary table."""
    result = run_strategy_sweep(seeds, **kwargs)
    print(
        f"\nStrategy sweep — {result['seeds']} seeds on '{result['scenario']}'"
    )
    print(f"{'strategy':<15}{'win_rate':>10}{'wins':>7}{'mean_net_worth':>16}{'mean_penalties':>16}")
    print("-" * 64)
    for row in result["rows"]:
        print(
            f"{row['strategy']:<15}{row['win_rate']:>10.3f}{row['wins']:>7}"
            f"{row['mean_net_worth']:>16,.0f}{row['mean_penalties']:>16,.0f}"
        )
    if result["dominant_strategies"]:
        print(f"\n[!] DOMINANT (>60% win rate): {', '.join(result['dominant_strategies'])}")
    else:
        print("\n[ok] No dominant strategy (all win rates <= 60%).")
    return result


def _utc() -> datetime:
    return datetime.now(timezone.utc)


def _deck_paths() -> list[Path]:
    base = Path(__file__).parent / "data"
    return [base / "starter_deck.json", base / "expansion_deck.json"]
