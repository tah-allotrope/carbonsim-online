"""Standalone strategy sweep for PHASE-05 verification."""
from engine.playtest import run_strategy_sweep

r = run_strategy_sweep(range(20))
print("Scenario:", r["scenario"])
print("Seeds:", r["seeds"])
print()
print(f"{'strategy':<14} {'win_rate':>10} {'wins':>5}")
print("-" * 35)
for row in r["rows"]:
    print(f"{row['strategy']:<14} {row['win_rate']:>10.3f} {row['wins']:>5}")
print()
print("Dominant:", r["dominant_strategies"])
