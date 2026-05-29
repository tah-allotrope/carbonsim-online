---
title: "Sprint 3 — Engine Trim, Modularization & Test Unification"
date: "2026-05-29"
status: "draft"
request: "Sequenced multiphase plans from reports/2026-05-29-single-multiplayer-game-gap-analysis.md — cluster (3): GAP-03 + GAP-08 (engine inventory/trim, modularization, unify tests, fix the 2 failing tests)."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-05-29-single-multiplayer-game-gap-analysis.md"
---

# Plan: Sprint 3 — Engine Trim, Modularization & Test Unification

## Objective
Turn the 1,943-line `carbonsim_engine/engine.py` from a dual-purpose (workshop + game) monolith into a clean, well-tested core for the game, by inventorying real usage, deciding keep/trim/modularize per surface, unifying the now-fragmented test suites, and fixing the 2 long-carried failing tests. This gives Sprints 4 (multiplayer) and 5 (visuals) a stable foundation to build on.

## Context Snapshot
- **Current state:** `carbonsim_engine/engine.py` (1,943 LOC) bundles game-loop logic (year cycle, abatement, offsets, banking, penalties) with workshop-platform constructs built for the now-removed oTree product: `build_facilitator_snapshot()` (`engine.py:815-891`), `build_session_analytics()` (`engine.py:933-1111`), `export_session_data()` (`engine.py:1114-1180`), multi-company auctions (`engine.py:377-504`), bot strategies (`engine.py:1456-1551`), replay timelines. Tests are split across `carbonsim_engine/tests/` and (pre-Sprint-1) `platform/tests/`, with a stale duplicate `test_engine.py`. Two engine tests are known-failing: `test_start_simulation_initializes_year_one_allocations` and `test_trade_transfers_allowances_and_cash` (`carbonsim_engine/tests/test_engine.py`). API tests have weak assertions (prior GAP-06).
- **Desired state:** A documented engine surface map (game-used / multiplayer-candidate / dead); dead code removed or quarantined; optionally the monolith split into cohesive modules (e.g., `engine_core`, `market`, `analytics`); one unified, runnable test suite; the 2 failing tests fixed; balance unchanged (verified via `playtest.py`).
- **Key repo surfaces:** `carbonsim_engine/engine.py`, `carbonsim_engine/solo.py`, `carbonsim_engine/coop.py`, `carbonsim_engine/cards.py`, `carbonsim_engine/playtest.py`, `carbonsim_engine/tests/test_engine.py`, `carbonsim_engine/tests/test_cards.py`, `mayor_api/routes/game.py`, `mayor_api/routes/coop.py`, `mayor_api/tests/test_api.py`.
- **Out of scope:** New multiplayer features (Sprint 4) and visual work (Sprint 5). Trimming must not change observable game behavior; this is a refactor + test plan.

## Research Inputs
- `reports/2026-05-29-single-multiplayer-game-gap-analysis.md` — Source of GAP-03/08. Lists the workshop-only engine surfaces, the 2 failing tests, weak API assertions, and the requirement to lock behavior with `playtest.py` before/after.

## Assumptions and Constraints
- **ASM-001:** Sprints 1-2 are complete: `platform/` is gone (so `platform/tests/` no longer exists) and the tree is reorganized; engine import path is stable.
- **ASM-002:** Some workshop surfaces (auctions, facilitator snapshot, analytics, exports) are candidates for the multiplayer game (Sprint 4), so "trim" means quarantine-or-keep with intent, not blanket deletion.
- **CON-001:** `playtest.py` provides a deterministic harness; tuned balance metrics in `activeContext.md` are the behavioral baseline to preserve.
- **DEC-001:** Behavior-preserving refactor only — no scenario/balance changes in this plan.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Inventory engine surface vs. real game usage | None (post-Sprint 2) | `docs/engine-surface-map.md` classifying every public function |
| PHASE-02 | Lock behavior, then fix the 2 failing tests and harden assertions | PHASE-01 | Green baseline, fixed tests, state-asserting API tests, unified suite |
| PHASE-03 | Trim dead code and (optionally) modularize the monolith | PHASE-02 | Removed/quarantined dead surfaces; optional `market.py`/`analytics.py` split; tests still green |

## Detailed Phases

### PHASE-01 - Engine Surface Inventory
**Goal**
Produce a definitive map of what the game actually calls, what is a multiplayer candidate, and what is dead, so trimming decisions are evidence-based.

**Tasks**
- [ ] TASK-01-01: Enumerate public functions/classes in `carbonsim_engine/engine.py` and the wrapper modules (`solo.py`, `coop.py`, `cards.py`, `tutorial.py`, `achievements.py`, `playtest.py`).
- [ ] TASK-01-02: Grep all callers in `mayor_api/` (`routes/game.py`, `routes/coop.py`, `ws.py`) and `mayor_web/js/` API calls; map each engine surface to its caller(s) or mark uncalled.
- [ ] TASK-01-03: Classify each surface: GAME-USED (solo/coop loop), MULTIPLAYER-CANDIDATE (auctions/facilitator/analytics/export/bots — referenced by Sprint 4), or DEAD (no caller, no planned use).
- [ ] TASK-01-04: Write `docs/engine-surface-map.md` with the classification table and proposed action per surface.

**Files / Surfaces**
- `carbonsim_engine/engine.py` and wrapper modules - read for inventory.
- `mayor_api/routes/*.py`, `mayor_api/ws.py`, `mayor_web/js/api.js` - caller analysis.
- `docs/engine-surface-map.md` (new) - output.

**Dependencies**
- None beyond Sprint 2.

**Exit Criteria**
- [ ] Every public engine surface is classified GAME-USED / MULTIPLAYER-CANDIDATE / DEAD with its callers listed.

**Phase Risks**
- **RISK-01-01:** Dynamic dispatch (`from ... import *`, getattr) hides callers. Mitigation: include string/route-name searches and the card-effect dispatch in the grep.

### PHASE-02 - Lock Behavior & Fix Tests
**Goal**
Establish a green, meaningful baseline before any code is removed: capture playtest metrics, fix the 2 failing tests, and replace weak API assertions with state checks.

**Tasks**
- [ ] TASK-02-01: Run `playtest.py` and record baseline metrics (completion, avg final cash, avg penalties per difficulty) as the behavioral lock.
- [ ] TASK-02-02: Diagnose and fix `test_start_simulation_initializes_year_one_allocations` and `test_trade_transfers_allowances_and_cash` in `carbonsim_engine/tests/test_engine.py` — determine whether the test or the engine is wrong (consult the surface map and the year-start/allocation logic) and fix at the root.
- [ ] TASK-02-03: Strengthen `mayor_api/tests/test_api.py`: decision tests must assert cash/emissions/active-abatement state changes (not just `status == applied`); lifecycle tests must assert phase/year transitions. Add one end-to-end test: create game → make decision → advance year → verify the decision affected compliance.
- [ ] TASK-02-04: Unify test invocation: a single command/config (e.g., root `pytest` config) discovers engine + API suites; remove any duplicate `test_engine.py` left from the old `platform/tests/`.

**Files / Surfaces**
- `carbonsim_engine/tests/test_engine.py` - fix 2 failing tests.
- `mayor_api/tests/test_api.py` - state assertions + e2e test.
- `pyproject.toml`/`pytest.ini` (root) - unified discovery.
- `carbonsim_engine/playtest.py` - baseline metrics.

**Dependencies**
- PHASE-01 (surface map informs the allocation/trade test fixes).

**Exit Criteria**
- [ ] Full suite green with 0 known failures (the 2 are fixed).
- [ ] Decision/lifecycle API tests fail if the engine silently ignores an action (proves they assert real state).
- [ ] One command runs all tests.

**Phase Risks**
- **RISK-02-01:** Fixing the allocation/trade tests reveals a real engine bug affecting balance. Mitigation: re-run `playtest.py`; if metrics shift, decide explicitly (this is the one allowed behavior change, documented) vs. fix-the-test.

### PHASE-03 - Trim & Modularize
**Goal**
Remove or quarantine dead surfaces and optionally split the monolith into cohesive modules, keeping the suite green throughout.

**Tasks**
- [ ] TASK-03-01: Remove DEAD surfaces (per the surface map) or move MULTIPLAYER-CANDIDATE code behind a clearly-named module so Sprint 4 can adopt it deliberately.
- [ ] TASK-03-02: (Optional, gated by Q-001) Split `engine.py` into cohesive modules — e.g., `engine_core.py` (year cycle/compliance), `market.py` (auctions/trades/bots), `analytics.py` (facilitator snapshot/session analytics/export) — preserving the public import surface (`carbonsim_engine` re-exports) so callers don't break.
- [ ] TASK-03-03: Update `carbonsim_engine/pyproject.toml` keywords/description to reflect the game (drop "workshop-only" framing) if not already done in Sprint 1.
- [ ] TASK-03-04: Re-run the unified suite and `playtest.py`; confirm metrics match the PHASE-02 baseline.

**Files / Surfaces**
- `carbonsim_engine/engine.py` - trim/split.
- `carbonsim_engine/market.py`, `carbonsim_engine/analytics.py` (new, optional).
- `carbonsim_engine/__init__.py` - preserve re-exports.

**Dependencies**
- PHASE-02 (green baseline before refactor).

**Exit Criteria**
- [ ] No DEAD code remains in the core; MULTIPLAYER-CANDIDATE code is clearly delineated.
- [ ] Public import surface unchanged for `mayor_api` callers (no import breakage).
- [ ] Suite green and `playtest.py` metrics match the baseline.

**Phase Risks**
- **RISK-03-01:** Splitting modules breaks `from carbonsim_engine.engine import *` consumers (e.g., re-export expectations). Mitigation: keep `__init__.py` re-exporting the public API; run the API suite after each move.

## Verification Strategy
- **TEST-001:** Unified `pytest` run green (engine + API), 0 known failures, after PHASE-02 and PHASE-03.
- **TEST-002:** `playtest.py` metrics within tolerance of the PHASE-02 baseline (behavior preserved).
- **MANUAL-001:** Boot the server and play one solo year end-to-end; confirm abatement/offset/compliance still behave.
- **OBS-001:** Coverage or call-graph spot-check that removed surfaces truly have no callers.

## Risks and Alternatives
- **RISK-001:** Engine refactor regresses tuned balance. Mitigation: `playtest.py` before/after lock.
- **ALT-001:** Skip modularization, trim only. Acceptable fallback if Q-001 says no — the monolith stays but dead code is removed and tests unified.

## Grill Me
1. **Q-001:** Split the engine monolith into modules now, or just trim dead code and defer the split?
   - **Recommended default:** Trim now; do the split only if the surface map shows clean seams (market vs. core vs. analytics).
   - **Why this matters:** Determines whether PHASE-03 TASK-03-02 runs and how much import-surface care is needed.
   - **If answered differently:** If "split now," allocate extra time and add re-export regression tests; if "trim only," skip TASK-03-02.
2. **Q-002:** Are the workshop-only surfaces (facilitator snapshot, session analytics, export, multi-company auctions) wanted for the Sprint 4 multiplayer game, or truly dead?
   - **Recommended default:** Treat as MULTIPLAYER-CANDIDATE (quarantine, don't delete) — Sprint 4 likely reuses auctions/facilitator/export.
   - **Why this matters:** Determines delete vs. quarantine in PHASE-03 and what Sprint 4 inherits.
   - **If answered differently:** If truly dead, delete them in TASK-03-01 and Sprint 4 rebuilds multiplayer market/host logic from scratch.

## Suggested Next Step
Answer Q-001/Q-002, execute PHASE-01 → PHASE-03, then proceed to `plans/2026-05-29-singleplayer-multiplayer-buildout-plan.md` (Sprint 4).
