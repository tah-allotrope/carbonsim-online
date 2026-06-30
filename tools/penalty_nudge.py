"""Per-pack penalty nudge experiment for PHASE-05.

The plan's recommended mitigation is "per-pack penalty_rate nudge (per-tonne,
FX-scaled) rather than a wholesale re-tune". This script tries several
penalty multipliers on solo_standard and reports the resulting sweep
distribution, to confirm or refute whether the nudge can close the
structural break documented in PHASE-01 finding F-1.
"""
from engine import scenarios
from engine.playtest import run_strategy_sweep

base_penalty = scenarios.SCENARIO_PACKS["solo_standard"]["penalty_rate"]
print(f"Base penalty (post-FX): {base_penalty:,.0f} d/tCO2e")
print()

for multiplier in [1, 2, 5, 10, 20, 50]:
    pack = dict(scenarios.SCENARIO_PACKS["solo_standard"])
    pack["penalty_rate"] = base_penalty * multiplier
    # We bypass the normal create_initial_state path by patching the
    # scenario lookup via a runtime monkey-patch.
    scenarios.SCENARIO_PACKS["solo_standard"] = pack
    try:
        r = run_strategy_sweep(range(20))
        rows_str = " ".join(f"{row['strategy'][:3]}={row['win_rate']:.2f}" for row in r["rows"])
        dominant = ",".join(r["dominant_strategies"]) or "none"
        print(f"penalty x{multiplier:>2}  dominant={dominant:<11}  {rows_str}")
    finally:
        scenarios.SCENARIO_PACKS["solo_standard"] = dict(pack)
        scenarios.SCENARIO_PACKS["solo_standard"]["penalty_rate"] = base_penalty
