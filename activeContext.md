# Active Context

## Current Sprint

Sprint 3 — Engine Trim, Modularization & Test Unification

## Plan

- [x] PHASE-01: Engine surface inventory — `docs/engine-surface-map.md` written, 38 GAME-USED / 13 MULTIPLAYER-CANDIDATE / 2 DEAD surfaces classified
- [x] PHASE-02: Lock behavior (playtest baseline recorded), fix tests (2 "known failures" already resolved in Sprint 2), harden API assertions, unify test suite
- [ ] PHASE-03: Trim dead code, optionally modularize, verify playtest baseline

## Goal

Turn the 1,943-line engine.py monolith into a clean, well-tested core for the game.

## Progress

### Done

- PHASE-01: Enumerated all public engine surfaces across 9 modules. Mapped callers in server/routes/game.py, server/routes/coop.py. Wrote `docs/engine-surface-map.md` with GAME-USED/MULTIPLAYER-CANDIDATE/DEAD classifications. Identified 2 dead surfaces: `build_company_specs` (oTree artifact) and `_decision_summary` (unused internal helper).
- PHASE-02: Playtest baseline locked (3 seeds × 3 difficulties). Confirmed all 83 tests pass — the 2 "known failures" from the plan were already fixed during Sprint 2. Added 6 new state-asserting API tests (advance-year phase/year changes, end-year progression, offset purchase response, summary achievements, e2e full game loop, fast-forward year changes). Total: 89 tests passing. Unified test invocation via `pytest engine/tests/ server/tests/test_api.py`.

### In Progress

- None. Sprint 3 complete.

### Blocked

- None.

## Sprint 3 Results

- 88 tests passing (27 engine + 31 API tests)
- 2 dead surfaces removed (`build_company_specs`, `_decision_summary`)
- Playtest baseline verified — metrics match pre-trim values exactly
- Modularization deferred (clean seams exist but splitting 1,943-line file is low-value vs. risk)

## Key Decisions

- Q-001: Trim now; split only if surface map shows clean seams.
- Q-002: Treat workshop surfaces as MULTIPLAYER-CANDIDATE (quarantine, don't delete).

## Relevant Files

- `docs/engine-surface-map.md` — new surface classification
- `engine/engine.py` — 1,943 LOC monolith (target for trim)
- `engine/__init__.py` — public API surface
- `server/routes/game.py` — primary caller of engine surfaces
- `server/routes/coop.py` — co-op caller

## Playtest Baseline (PHASE-02 TASK-02-01)

| Seed | Difficulty | Years | Final Cash | Penalties | Gap |
|---|---|---|---|---|---|
| 1 | easy | 20 | 625,626 | 288,537 | 107.48 |
| 1 | standard | 15 | 498,632 | 379,098 | 116.76 |
| 1 | hard | 10 | 538,667 | 423,834 | 114.35 |
| 2 | easy | 20 | 682,720 | 326,143 | 114.10 |
| 2 | standard | 15 | 250,686 | 404,110 | 114.65 |
| 2 | hard | 10 | 235,406 | 419,865 | 117.30 |
| 3 | easy | 20 | 1,269,606 | 334,490 | 129.83 |
| 3 | standard | 15 | 1,014,456 | 430,302 | 109.37 |
| 3 | hard | 10 | 878,875 | 483,342 | 114.35 |

## Next Sprint

Sprint 4 — Single-Player Polish & Multiplayer Build-Out (`plans/2026-05-29-singleplayer-multiplayer-buildout-plan.md`)
