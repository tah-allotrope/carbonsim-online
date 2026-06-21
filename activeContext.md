# Active Context — Sprint 5: Meta (Capex Abatement + XP Unlock Tree + Jurisdiction Skins)

Plan: `plans/2026-06-21-carbonsim-elevation-plan.md` → PHASE-05 (final)
Cadence: implement fully → commit + push master → `/report Sprint 5` → `/report final`.

## Design guardrail
Keep `_projected_emissions` / penalty math defaults unchanged so Sprint 1–4 balance holds. Capex/opex/loans/tech-failure are ADDITIVE ledgers; `active_abatement_ids` stays the emissions source of truth.

## Tasks
- [ ] TASK-05-01: Abatement schema +capex/annual_opex/asset_life_years/tech_risk_pct (defaults: capex=cost, opex=0, life=large, risk=0); `break_even_year` helper.
- [ ] TASK-05-02: `active_abatement_assets` ledger on activation; deduct annual_opex in `_start_year`.
- [ ] TASK-05-03: `finance_abatement` action (pay cash OR loan); `active_loans`; deduct annual_payment in `_start_year`.
- [ ] TASK-05-04: `tech_failure` roll in `_start_year` (seeded RNG vs tech_risk_pct) → 1-year 50% impairment via `tech_impaired_ids`.
- [ ] TASK-05-05: XP engine in `achievements.py` (`award_xp`); `xp`/`xp_level` in state; thresholds [0,200,500,1000,2000,4000]; hook at year close.
- [ ] TASK-05-06: `engine/data/unlock_tree.json` + loader; expose unlocked nodes in snapshot by level.
- [ ] TASK-05-07: `player_profiles` table in `db.py`; `GET/POST /api/players/{name}/xp`; load on game start.
- [ ] TASK-05-08: `jurisdiction` field + `eu_ets.json` / `california_arb.json`; merge over base in `create_initial_state`.
- [ ] TASK-05-09: XP HUD (already client-wired) + canonical server XP in snapshot.
- [ ] TASK-05-10: Unlock Tree modal in `web/game.html`.
- [ ] TASK-05-11: Final sweep across Vietnam + EU ETS; no strategy >60%.
- [ ] Tests: `engine/tests/test_meta.py`.

## Verification
- `python -m pytest engine/tests/ server/tests/` all pass.
- Loan creates active_loans + deducts annual_payment; tech_failure impairs then restores.
- XP accrues + level increments at thresholds. EU ETS jurisdiction loads its names/constants.
- Sweep: no strategy >60% in either jurisdiction. Determinism holds.

## Review (complete)
- **All 11 tasks done.** 152 tests pass (+14 `test_meta.py`); determinism holds; frontend (Unlock Tree modal) browser-verified.
- Abatement schema enriched at build time (capex=cost, opex 0, life 8, risk 0 — balance-neutral) + `break_even_year`. `active_abatement_ids` stays emissions source of truth, so Sprint 1–4 balance is untouched.
- `active_abatement_assets` / `active_loans` / `tech_impaired_ids` ledgers; `finance_abatement` loan action (amortized); `_service_abatement_assets` deducts opex + loan payments and rolls seeded tech-failures (1-year 50% impairment) each year.
- XP engine: `award_xp` + `XP_EVENT_POINTS` (achievements.py) + `XP_LEVEL_THRESHOLDS` [0,200,500,1000,2000,4000]; awarded at year close; in snapshot.
- `unlock_tree.json` (7 nodes) + `load_unlock_tree`; surfaced in snapshot; Unlock Tree modal in game.html.
- `player_profiles` SQLite table + `GET/POST /api/players/{name}/xp`; XP loaded at game create, persisted monotonically on year advance.
- Jurisdiction skins: `eu_ets.json` / `california_arb.json` + `load_jurisdiction` merge over base pack; `jurisdiction` param threaded create_initial_state → create_solo_game → CreateGameRequest.
- **Final sweep (TASK-05-11):** no dominant strategy in any jurisdiction — Vietnam 0.40, EU ETS 0.55, California 0.50. Tuned EU penalty 1100→950 and California 850→1100 to balance (each jurisdiction's offset cost shifts the balance point).

## 5-sprint plan COMPLETE
Foundation → Market → AI → Story → Meta all delivered. Final plan report to follow.
