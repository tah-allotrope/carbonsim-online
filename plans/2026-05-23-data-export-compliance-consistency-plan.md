---
title: "Add Data Export Route & Fix Compliance Gap Consistency (GAP-07/08)"
date: "2026-05-23"
status: "draft"
request: "Sprint 3: Add API route for the existing export_session_data() engine function (GAP-07) and fix the compliance gap calculation inconsistency between engine and frontend (GAP-08)."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md"
---

# Plan: Add Data Export Route & Fix Compliance Gap Consistency

## Objective

Expose the existing `export_session_data()` engine function via an API route so workshop facilitators and researchers can download session data after a game. Fix the compliance gap calculation inconsistency where the engine ignores the offset usage cap but the frontend applies it, causing the displayed gap to disagree with the engine's internal number.

## Context Snapshot

- **Current state:** `export_session_data()` is fully implemented in the engine (`engine.py:1114-1180`) but has no API route — the data is inaccessible without direct Python access. The engine's `_recalculate_company_projection` (`engine.py:1894-1905`) calculates `compliance_gap` as `projected_emissions - allowances - offset_holdings` (full offset holdings, no cap). The frontend (`game.html:192`) calculates the displayed gap as `projected - allowances - usableOffsets` where `usableOffsets = min(offsetHoldings, projected * offsetCapPercent)` — applying the offset usage cap. These two numbers diverge whenever a player holds more offsets than the cap allows.
- **Desired state:** A `GET /api/games/{id}/export` route returns session data as JSON. The compliance gap is calculated consistently — the engine applies the offset usage cap in its `compliance_gap` field so the frontend and engine agree.
- **Key repo surfaces:**
  - `carbonsim_engine/engine.py:1114-1180` — `export_session_data()` (fully built, no route)
  - `carbonsim_engine/engine.py:1894-1905` — `_recalculate_company_projection()` (compliance gap without offset cap)
  - `carbonsim_engine/engine.py:1669-1760` — `_close_current_year()` (compliance calculation at year-end, applies offset cap correctly)
  - `mayor_web/game.html:189-192` — frontend compliance gap calculation (applies offset cap)
  - `mayor_api/routes/game.py` — solo game routes (where the export route will be added)
- **Out of scope:** CSV/Excel export formats (JSON only for Sprint 3), data visualization, historical data warehousing, export from facilitator dashboard (covered in Sprint 2 plan).

## Research Inputs

No applicable research briefs were found in `research/`. The gap analysis at `reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md` provides context for GAP-07 and GAP-08.

## Assumptions and Constraints

- **ASM-001:** The frontend's compliance gap calculation (with offset cap) is the correct behavior. The year-end compliance function `_close_current_year()` already applies the offset cap when calculating actual compliance — the projection should match.
- **ASM-002:** The export route should work for both solo and co-op games. The `export_session_data()` function operates on the game state dict, which has the same structure regardless of game mode.
- **ASM-003:** The data export route does not require authentication for Sprint 3. If the facilitator dashboard (Sprint 2) adds a facilitator token, the export route on the facilitator side will use that token, but the solo export route is open.
- **CON-001:** The `_recalculate_company_projection` function is called from multiple places (after decisions, after shocks, after year-start). The fix must not break any of these call sites.
- **CON-002:** All existing 83+ tests must continue to pass after the compliance gap fix.
- **DEC-001:** The compliance gap fix changes the semantics of `company["compliance_gap"]` from "gap ignoring offset cap" to "gap applying offset cap". Any code that reads `compliance_gap` from the state dict will see the new (cap-aware) value. This is the correct behavior since the cap is always enforced at year-end.

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Add data export API route for solo games | None | New endpoint in `game.py`; JSON export accessible via API |
| PHASE-02 | Fix compliance gap calculation consistency | None | Modified `engine.py`; engine and frontend agree on compliance gap |
| PHASE-03 | Tests and verification | PHASE-01, PHASE-02 | New tests in `test_api.py`; verified export and gap consistency |

## Detailed Phases

### PHASE-01 — Add Data Export API Route

**Goal**

Expose `export_session_data()` via a `GET /api/games/{game_id}/export` endpoint so session data can be downloaded as JSON after a game.

**Tasks**

- [ ] TASK-01-01: In `mayor_api/routes/game.py`, add a `GET /api/games/{game_id}/export` endpoint that: (1) loads the game state from the store, (2) calls `export_session_data(state)`, (3) returns the result as JSON. Import `export_session_data` from `carbonsim_engine.engine`.
- [ ] TASK-01-02: Add error handling: return 404 if game ID not found, return 400 if game has no year_results yet (no data to export).
- [ ] TASK-01-03: Add an "Export Data" button to `mayor_web/game.html` in the header or summary section that calls the export endpoint and triggers a browser download of the JSON file (using `window.open` or creating a blob download link).
- [ ] TASK-01-04: Run existing tests to verify no regressions.

**Files / Surfaces**

- `mayor_api/routes/game.py` — add export endpoint
- `mayor_web/game.html` — add export button
- `carbonsim_engine/engine.py:1114-1180` — `export_session_data()` (called, not modified)

**Dependencies**

- None

**Exit Criteria**

- [ ] `GET /api/games/{game_id}/export` returns complete session data as JSON
- [ ] Response includes `session_meta`, `companies` (with `year_results`), `auctions`, `trades`, and `audit_log`
- [ ] The export button in the game UI triggers a download
- [ ] Returns 404 for non-existent game IDs
- [ ] All existing tests pass

**Phase Risks**

- **RISK-01-01:** The `audit_log` in the export can be very large for long games (every state mutation is logged). **Mitigation:** For Sprint 3, return the full log. If size becomes an issue, add pagination or filtering in a future sprint.

---

### PHASE-02 — Fix Compliance Gap Calculation Consistency

**Goal**

Make the engine's `compliance_gap` field apply the offset usage cap, matching the frontend's calculation and the year-end compliance logic.

**Tasks**

- [ ] TASK-02-01: In `carbonsim_engine/engine.py`, modify `_recalculate_company_projection()` (lines 1894-1905) to apply the offset usage cap when calculating `compliance_gap`:
  ```python
  def _recalculate_company_projection(state, company):
      year = state["current_year"]
      company["projected_emissions"] = _projected_emissions(company, year)
      offset_cap = state.get("offset_usage_cap", 0.1)
      max_usable = company["projected_emissions"] * offset_cap
      usable_offsets = min(company["offset_holdings"], max_usable)
      company["compliance_gap"] = round(
          company["projected_emissions"]
          - company["allowances"]
          - usable_offsets,
          2,
      )
  ```
- [ ] TASK-02-02: Verify that `_close_current_year()` (lines 1669-1760) already applies the offset cap correctly in its compliance calculation. Confirm the year-end `compliance_gap` in `year_results` is consistent with the new projection calculation.
- [ ] TASK-02-03: Update the frontend (`game.html:192`) comment (if any) to note that the gap now comes directly from the engine and the frontend calculation is a display-time backup.
- [ ] TASK-02-04: Run all engine tests (`pytest carbonsim_engine/tests/ -q`) to verify no regressions. If any tests assert specific `compliance_gap` values, update them to reflect the cap-aware calculation.

**Files / Surfaces**

- `carbonsim_engine/engine.py:1894-1905` — modify `_recalculate_company_projection()` to apply offset cap
- `carbonsim_engine/engine.py:1669-1760` — verify `_close_current_year()` consistency (read-only)
- `mayor_web/game.html:192` — verify frontend gap calculation matches (read-only or minor comment update)

**Dependencies**

- None (independent of PHASE-01)

**Exit Criteria**

- [ ] `company["compliance_gap"]` in the engine state equals `projected_emissions - allowances - min(offset_holdings, projected_emissions * offset_usage_cap)`
- [ ] The frontend-displayed gap matches the engine's `compliance_gap` field
- [ ] Year-end compliance results are consistent with the projection
- [ ] All 58 engine tests pass (with updated assertions if needed)

**Phase Risks**

- **RISK-02-01:** Changing `compliance_gap` semantics could affect bot decision-making if bots use `compliance_gap` to decide whether to buy offsets or abatement. **Mitigation:** Review `_run_single_bot_turn()` to check if it reads `compliance_gap`. If so, verify the bot logic still makes sensible decisions with the cap-aware value. The cap-aware value is more realistic, so bot decisions should improve.
- **RISK-02-02:** Some engine tests may assert exact `compliance_gap` values that change with this fix. **Mitigation:** Update those assertions to the new correct values. The change is small (only affects cases where `offset_holdings > projected_emissions * offset_cap`).

---

### PHASE-03 — Tests and Verification

**Goal**

Add automated tests for the export endpoint and compliance gap consistency. Verify both features work correctly in the browser.

**Tasks**

- [ ] TASK-03-01: Add `test_export_session_data_route` to `test_api.py`: create a solo game, advance 1-2 years, call `GET /api/games/{id}/export`, verify the response contains `session_meta`, `companies`, `auctions`, `trades`, `audit_log`. Verify `session_meta.scenario` is correct and `companies[0].year_results` is non-empty.
- [ ] TASK-03-02: Add `test_export_nonexistent_game` to `test_api.py`: call export on a fake game ID, verify 404.
- [ ] TASK-03-03: Add `test_compliance_gap_applies_offset_cap` to engine tests: create a game state where a company has more offsets than the cap allows, call `_recalculate_company_projection`, verify `compliance_gap` uses the capped offset amount (not full holdings).
- [ ] TASK-03-04: Add `test_compliance_gap_consistency_with_frontend` to `test_api.py`: create a game, buy enough offsets to exceed the cap, GET the game state via API, calculate the expected gap using the frontend formula (`projected - allowances - min(holdings, projected * cap)`), verify it matches the `compliance_gap` field in the response.
- [ ] TASK-03-05: Run the full test suite: `pytest mayor_api/tests/test_api.py -q` and `pytest carbonsim_engine/tests/ -q`. All tests must pass.
- [ ] TASK-03-06: Manual verification — start the dev server, play a solo game, buy enough offsets to exceed the cap, verify the compliance gap displayed in the UI matches the value from the API response.

**Files / Surfaces**

- `mayor_api/tests/test_api.py` — add 4 new test functions
- `carbonsim_engine/tests/` — add 1 new test function (or add to existing test file)

**Dependencies**

- PHASE-01 (export route exists for testing)
- PHASE-02 (compliance gap fix exists for testing)

**Exit Criteria**

- [ ] All 4 new tests pass
- [ ] All existing tests still pass
- [ ] Manual verification confirms frontend gap matches API gap when offsets exceed cap
- [ ] Export JSON file downloads correctly from the game UI

**Phase Risks**

- **RISK-03-01:** None — straightforward test additions.

## Verification Strategy

- **TEST-001:** `pytest mayor_api/tests/test_api.py -q` — all tests pass including new export and gap tests
- **TEST-002:** `pytest carbonsim_engine/tests/ -q` — all engine tests pass with updated gap assertions
- **MANUAL-001:** Download export JSON from a solo game with 2+ years played, verify data completeness
- **MANUAL-002:** Play a game with offset holdings exceeding cap, verify UI gap matches engine gap

## Risks and Alternatives

- **RISK-001:** Changing `compliance_gap` semantics is a subtle behavioral change that could affect downstream consumers (bot logic, analytics, facilitator snapshot). **Mitigation:** The cap-aware value is strictly more correct — it matches what actually happens at year-end. Any consumer that was using the uncapped value was getting an inaccurate projection.
- **ALT-001:** Instead of fixing `_recalculate_company_projection`, we could add a separate `projected_compliance_gap` field that applies the cap, leaving `compliance_gap` unchanged. This was not chosen because having two gap fields is confusing and the uncapped value has no legitimate use — the cap is always enforced at compliance time.
- **ALT-002:** Instead of a simple JSON export endpoint, we could build a CSV/Excel export with formatted worksheets. This was not chosen for Sprint 3 because JSON is sufficient for immediate workshop analysis needs. CSV/Excel can be added later as a format parameter.

## Grill Me

1. **Q-001:** Should the export endpoint also be available for in-progress games (before completion), or only for completed games?
   - **Recommended default:** Available for all games regardless of phase. Facilitators may want to export mid-session data for analysis. The `export_session_data()` function already works on any game state.
   - **Why this matters:** If restricted to completed games, facilitators can't export data if a workshop session is cut short.
   - **If answered differently:** Add a phase check that only allows export when `phase == "complete"`. Add a `force=true` query parameter to override.

## Suggested Next Step

This sprint has no open blockers and can begin implementation immediately. PHASE-01 and PHASE-02 are independent and can be worked in parallel.
