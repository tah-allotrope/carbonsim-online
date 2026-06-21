# Active Context — Sprint 3: AI Goal-Driven Agents

Plan: `plans/2026-06-21-carbonsim-elevation-plan.md` → PHASE-03
Cadence: implement fully → commit + push master → `/report Sprint 3`.

## Tasks
- [ ] TASK-03-01: `CompanyAgent` dataclass in `engine/agents.py` (company_id, sector, risk_appetite, horizon_years, cash_target_fraction, preferred_instruments).
- [ ] TASK-03-02: `CompanyAgent.plan_year(state) -> list[Action]` — horizon-aware gap projection, abatement ranking, offset/forward/VCM/auction budgeting, OTC proposal. Uses `project_outcome`.
- [ ] TASK-03-03: Replace `run_bot_turns` internals with agent dispatch. Preserve `bot_strategy` field as risk_appetite. Add bot OTC trade responses.
- [ ] TASK-03-04: Two new strategy profiles in `constants.py`: `opportunistic`, `speculator`. Extend all 5 profiles with horizon/appetite fields. Total 5.
- [ ] TASK-03-05: AI-initiated OTC proposals (cap 1/bot/year; bot uses own projected state, reads peer compliance_gap only).
- [ ] TASK-03-06: `run_strategy_sweep(seeds)` in `playtest.py` — head-to-head 5-strategy games; win_rate/mean_cash/mean_penalties; flag >60% win rate.
- [ ] TASK-03-07: Run sweep 20 seeds; tune constants until no strategy >60% win rate. Document final constants.
- [ ] TASK-03-08: `GET /api/games/{id}/ai-signals` endpoint — competitor postures. Assign varied strategies to solo bots.
- [ ] Tests: `engine/tests/test_agents.py`.

## Verification
- `python -m pytest engine/tests/` all pass.
- `run_strategy_sweep(range(20))` → no strategy >60% win rate.
- Determinism check still passes.

## Review (complete)
- **All 8 tasks done.** 67 tests pass (was 60; +7 in `test_agents.py`). Determinism holds.
- `engine/agents.py` — `CompanyAgent` dataclass + near-pure `plan_year` (abatement→forward→VCM→offsets→auction→OTC), `respond_to_trade`, `_estimate_future_gap` horizon lookahead.
- `run_bot_turns` rewritten to dispatch agents (pass 1 plan/act, pass 2 OTC responses). `ai_market_signals()` added + `GET /api/games/{id}/ai-signals`.
- 5 strategy profiles in `constants.py` (added opportunistic, speculator; extended all with horizon/appetite fields).
- `run_strategy_sweep` / `print_strategy_sweep` in `playtest.py`. Head-to-head, ranked by liquidation net worth.
- Solo games now seed a varied bot strategy mix per difficulty.
- **Balance finding (TASK-03-07):** at penalty_rate=325 a pure under-complier dominated (paying penalties cheaper than abating) → defeats carbon mechanics. Raised solo_standard penalty_rate 325→1000. Final 20-seed sweep: moderate 0.45, conservative 0.40, opportunistic 0.10, aggressive 0.05, speculator 0.0 — no strategy >60%.
- **Latent bug fixed:** `state["allocation_factors"]` aliased the shared `SCENARIO_PACKS` dict; `apply_shock(election_pressure)` mutated it in place, corrupting later games in the same process. Now deep-copied in `create_initial_state`. Sweep is now stable across repeated calls.
