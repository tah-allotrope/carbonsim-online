from __future__ import annotations

from typing import Any


ACHIEVEMENTS = {
    "drawdown_pioneer": {
        "title": "Drawdown Pioneer",
        "description": "Finish with net-zero or better compliance gap.",
    },
    "budget_hawk": {
        "title": "Budget Hawk",
        "description": "Finish with more than 50% of starting cash intact.",
    },
    "clean_sweep": {
        "title": "Clean Sweep",
        "description": "Complete the game with zero cumulative penalties.",
    },
    "market_maker": {
        "title": "Market Maker",
        "description": "Win 10 or more auction lots over the course of the game.",
    },
}


def compute_achievements(state: dict[str, Any]) -> list[dict[str, str]]:
    player = next((company for company in state.get("companies", []) if not company.get("is_bot")), None)
    if not player:
        return []

    achievements: list[dict[str, str]] = []
    if player.get("compliance_gap", 1) <= 0:
        achievements.append({"id": "drawdown_pioneer", **ACHIEVEMENTS["drawdown_pioneer"]})

    starting_cash = player.get("starting_cash", player.get("cash", 0))
    if starting_cash and player.get("cash", 0) >= starting_cash * 0.5:
        achievements.append({"id": "budget_hawk", **ACHIEVEMENTS["budget_hawk"]})

    if player.get("cumulative_penalties", 0) <= 0:
        achievements.append({"id": "clean_sweep", **ACHIEVEMENTS["clean_sweep"]})

    lots_won = sum(
        1
        for auction in state.get("auctions", [])
        for result in auction.get("results", [])
        if result.get("company_id") == player.get("company_id") and result.get("quantity_awarded", 0) > 0
    )
    if lots_won >= 10:
        achievements.append({"id": "market_maker", **ACHIEVEMENTS["market_maker"]})

    return achievements
