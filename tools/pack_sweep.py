"""Sweep across all VN packs to characterize the post-rescale balance shift.

The plan's Q-001 was answered "reuse the harness, ~5pp drift tolerance".
This script runs the sweep on every Vietnam pack to map out which ones
are within tolerance and which drift.
"""
from engine.playtest import run_strategy_sweep

PACKS = ["vietnam_pilot", "high_pressure", "generous", "solo_easy", "solo_standard", "solo_hard", "solo_tutorial"]

print(f"{'pack':<18} {'max_strat':<14} {'max_wr':>8}  {'distribution'}")
print("-" * 80)
for pack in PACKS:
    r = run_strategy_sweep(range(10), scenario=pack)
    if r["rows"]:
        top = r["rows"][0]
        dist = " ".join(f"{row['strategy'][:3]}={row['win_rate']:.2f}" for row in r["rows"])
        print(f"{pack:<18} {top['strategy']:<14} {top['win_rate']:>8.2f}  {dist}")
