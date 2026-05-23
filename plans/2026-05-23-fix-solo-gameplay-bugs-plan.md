---
title: "Fix Critical Solo Gameplay Bugs (GAP-01/02/03/06)"
date: "2026-05-23"
status: "draft"
request: "Fix the 2 critical bugs that make solo play unplayable, the frontend display bug, and weak test assertions — Sprint 1 from the workshop demo gap analysis."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md"
---

# Plan: Fix Critical Solo Gameplay Bugs

## Objective

Make Climate Mayor solo play fully functional end-to-end. Right now the game is completely unplayable: player decisions are silently rejected (phase gate), the advance-year route skips the decision window entirely (double `force_advance_phase`), and the frontend never shows which abatements are active (wrong snapshot fields). This sprint fixes all three plus hardens the test suite to prevent regression.

## Context Snapshot

- **Current state:** Game creates successfully, UI renders, but every player action (activate abatement, buy offsets) is silently ignored. Clicking "Advance Year" closes the year immediately without giving the player a decision window. All 25 API tests pass, but decision tests don't verify state changes, so the suite gives false confidence.
- **Desired state:** A player can create a game, activate abatements and buy offsets that visibly affect their compliance position, advance years with cards drawn and actionable, and complete a full game. Tests catch regressions on all of these.
- **Key repo surfaces:**
  - `carbonsim_engine/engine.py` — phase gate at line 178, `force_advance_phase` at line 555, `_company_snapshot` at line 1554
  - `mayor_api/routes/game.py` — `advance_year` route at line 156 (double `force_advance_phase` at lines 199, 205)
  - `mayor_web/game.html` — frontend reads `active_abatement_ids` / `pending_abatement_ids` at lines 196-197 instead of `m.active` / `m.pending`
  - `mayor_api/tests/test_api.py` — decision tests at lines 122-144
  - `carbonsim_engine/solo.py` — `create_solo_game` starts state in `year_start` phase
- **Out of scope:** Co-op mode fixes (GAP-04), facilitator dashboard (GAP-05), data export route (GAP-07), compliance gap consistency (GAP-08), balance tuning, UI/CSS changes beyond the abatement status display fix.

## Research Inputs

No applicable research briefs were found in `research/`. The gap analysis at `reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md` provides all necessary context.

## Assumptions and Constraints

- **ASM-001:** The intended solo game flow is: game creates in `decision_window` phase (or at least allows decisions in `year_start`) → player makes decisions → player clicks "Advance Year" → year closes → next year opens in decision-ready phase → repeat. This matches the frontend rendering logic which shows the decision UI in both `year_start` and `decision_window`.
- **ASM-002:** The fix for GAP-01 (advance-year) and GAP-02 (phase gate) should be coordinated. The cleanest approach is: (a) widen the phase gate in `apply_company_decision` to accept both `year_start` and `decision_window`, and (b) restructure `advance_year` to close the current year and open the next year's decision window in one step — removing the second `force_advance_phase`.
- **CON-001:** The fix must not break the existing 25 API tests or 58 engine tests.
- **CON-002:** The `force_advance_phase` function in the engine should not be modified — it is a general-purpose phase transition used by multiple consumers (advance-year, end-year, fast-forward, co-op ready). The fix should be in the route and the phase gate only.
- **DEC-001:** The `_company_snapshot` function's menu-item format (with `active`/`pending` booleans per item) is the correct data shape. The frontend should read those fields rather than expecting top-level arrays.

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Fix the advance-year route and phase gate so decisions are accepted and the decision window is not skipped | None | Modified `engine.py`, `game.py`; all existing tests still pass |
| PHASE-02 | Fix frontend abatement status display | PHASE-01 | Modified `game.html`; abatement active/pending badges render correctly |
| PHASE-03 | Strengthen test assertions and add end-to-end gameplay test | PHASE-01, PHASE-02 | Modified `test_api.py`; new tests that catch the bugs this plan fixes |
| PHASE-04 | Manual verification and smoke test | PHASE-01, PHASE-02, PHASE-03 | Verified solo game playthrough works end-to-end |

## Detailed Phases

### PHASE-01 — Fix Backend Phase Gate and Advance-Year Route

**Goal**

Make `apply_company_decision` accept decisions in `year_start` phase (not just `decision_window`) and restructure the `advance_year` route so it closes the current year and opens the next without skipping the decision window.

**Tasks**

- [ ] TASK-01-01: In `carbonsim_engine/engine.py` line 178, widen the phase gate from `if state["phase"] != PHASE_DECISION_WINDOW` to `if state["phase"] not in (PHASE_YEAR_START, PHASE_DECISION_WINDOW)`. This allows player actions in both phases where the frontend shows decision UI.
- [ ] TASK-01-02: In `mayor_api/routes/game.py` lines 156-214, restructure `advance_year` to perform: (1) if phase is `year_start` or `decision_window`, close the current year via `force_advance_phase` calls until `compliance` is reached; (2) run bot turns; (3) advance from `compliance` to the next year's `year_start`; (4) then immediately advance to `decision_window` and draw cards; (5) stop — do NOT call `force_advance_phase` again after drawing cards. The key change: remove the unconditional second `force_advance_phase` call at line 205 and instead use targeted transitions.
- [ ] TASK-01-03: Run `pytest mayor_api/tests/test_api.py -q` and `pytest carbonsim_engine/tests/ -q` to verify no regressions. All 83 tests must still pass.

**Files / Surfaces**

- `carbonsim_engine/engine.py:178` — widen phase gate in `apply_company_decision`
- `mayor_api/routes/game.py:156-214` — restructure `advance_year` route

**Dependencies**

- None

**Exit Criteria**

- [ ] `apply_company_decision` returns a modified state (with changed cash and active_abatement_ids) when called in `year_start` phase
- [ ] After calling the advance-year endpoint, the game state phase is `decision_window` (not `compliance`)
- [ ] `drawn_cards` are populated in the returned state after advance-year
- [ ] All 83 existing tests pass

**Phase Risks**

- **RISK-01-01:** Widening the phase gate could allow decisions during `year_start` in multiplayer/facilitator flows where `year_start` is supposed to be a read-only announcement phase. **Mitigation:** The `year_start` phase in solo mode is functionally identical to `decision_window` (the UI already renders it identically). For the workshop-oriented multiplayer flow, facilitators use `force_advance_phase` to explicitly open the decision window, which is unaffected by this change.
- **RISK-01-02:** Restructuring `advance_year` could break the fast-forward route or end-year route. **Mitigation:** Fast-forward (`game.py:294-372`) and end-year (`game.py:263-291`) have their own phase transition logic and do not call `advance_year`. They will be unaffected.

---

### PHASE-02 — Fix Frontend Abatement Status Display

**Goal**

Make the game UI correctly show which abatements are "Active" (green badge) or "Pending" (orange badge) by reading the per-menu-item `active`/`pending` booleans from the snapshot instead of the non-existent top-level arrays.

**Tasks**

- [ ] TASK-02-01: In `mayor_web/game.html` lines 196-197, remove `const activeIds = player.active_abatement_ids || [];` and `const pendingIds = player.pending_abatement_ids || [];`.
- [ ] TASK-02-02: In the abatement menu rendering loop (`game.html` ~line 335), change `const isActive = activeIds.includes(m.measure_id);` to `const isActive = m.active;` and `const isPending = pendingIds.includes(m.measure_id);` to `const isPending = m.pending;`.

**Files / Surfaces**

- `mayor_web/game.html:196-197` — remove stale variable declarations
- `mayor_web/game.html:335-336` — use `m.active` / `m.pending` instead of array lookups

**Dependencies**

- PHASE-01 (decisions must actually work for the status display to be meaningful)

**Exit Criteria**

- [ ] After activating an abatement via the UI, the measure's row shows a green "Active" badge instead of an "Activate" button
- [ ] Pending abatements (next-year timing) show an orange "Pending" badge

**Phase Risks**

- **RISK-02-01:** None — this is a straightforward field-name fix with no side effects.

---

### PHASE-03 — Strengthen Test Assertions and Add End-to-End Test

**Goal**

Modify existing tests to verify state changes (not just HTTP 200), and add a new end-to-end test that exercises the full gameplay loop: create → decide → advance → verify compliance impact.

**Tasks**

- [ ] TASK-03-01: In `test_decision_activate_abatement`, after calling the decision endpoint, GET the game state and verify: (a) the player's cash decreased by the abatement cost, (b) the snapshot's abatement menu shows the activated measure with `active: true`, (c) the player's `projected_emissions` decreased by the abatement amount.
- [ ] TASK-03-02: In `test_advance_year`, assert the returned `phase` is `"decision_window"` (not `"compliance"` or any other phase). Assert `drawn_cards` is a non-empty list.
- [ ] TASK-03-03: Add `test_decision_buy_offsets`: create a game, buy offsets via the decision endpoint, GET state, verify offset_holdings increased and cash decreased by `quantity * offset_price`.
- [ ] TASK-03-04: Add `test_full_solo_gameplay_loop`: create a standard game, activate an abatement, buy offsets, advance year (verify phase is `decision_window`), verify the previous year's compliance result reflects the abatement and offset decisions, repeat for 2 more years, then verify the game reaches completion.
- [ ] TASK-03-05: Run the full test suite and confirm all tests pass including the new ones.

**Files / Surfaces**

- `mayor_api/tests/test_api.py` — modify existing tests, add 2 new test functions

**Dependencies**

- PHASE-01 (tests rely on decisions actually working)
- PHASE-02 (the snapshot fields must be correct for assertions)

**Exit Criteria**

- [ ] `test_decision_activate_abatement` fails if the phase gate bug is reintroduced
- [ ] `test_advance_year` fails if the double-force_advance bug is reintroduced
- [ ] `test_full_solo_gameplay_loop` completes a multi-year game with verified state changes
- [ ] All tests pass: `pytest mayor_api/tests/test_api.py -q` shows 0 failures

**Phase Risks**

- **RISK-03-01:** The new end-to-end test depends on specific scenario numbers (abatement costs, emission amounts). **Mitigation:** Use relative assertions (`cash < original_cash`) rather than exact values, or read the scenario values from the snapshot dynamically.

---

### PHASE-04 — Manual Verification and Smoke Test

**Goal**

Start the dev server and manually play through a solo game to confirm the full loop works in the browser — not just in tests.

**Tasks**

- [ ] TASK-04-01: Start the FastAPI dev server with `python -m uvicorn mayor_api.main:app --reload` (or equivalent).
- [ ] TASK-04-02: Open the game in a browser, create a new Standard difficulty game.
- [ ] TASK-04-03: Verify: abatement menu is visible, clicking "Activate" on a measure shows a green "Active" badge, cash decreases, projected emissions decrease.
- [ ] TASK-04-04: Buy offsets and verify offset holdings increase.
- [ ] TASK-04-05: Click "Advance Year" and verify: year increments, event cards appear, the compliance position reflects prior decisions.
- [ ] TASK-04-06: Play through at least 3 years to confirm the loop is stable.
- [ ] TASK-04-07: Create a Tutorial mode game and verify tutorial cards appear and guidance text renders.

**Files / Surfaces**

- `mayor_api/main.py` — dev server entry point
- Browser at `http://localhost:8000`

**Dependencies**

- PHASE-01, PHASE-02, PHASE-03 all complete

**Exit Criteria**

- [ ] A solo game can be played from creation to at least year 3 with visible state changes from player decisions
- [ ] Tutorial mode displays guided cards and notes
- [ ] No JavaScript console errors during gameplay
- [ ] No HTTP 4xx/5xx errors in the server log during gameplay

**Phase Risks**

- **RISK-04-01:** Game balance may feel different now that decisions actually take effect — playtest metrics from `activeContext.md` were generated via the fast-forward route which has its own decision logic. **Mitigation:** This is expected and acceptable for the demo. Balance tuning is a separate backlog item.

## Verification Strategy

- **TEST-001:** `pytest mayor_api/tests/test_api.py -q` — all tests pass including new PHASE-03 tests
- **TEST-002:** `pytest carbonsim_engine/tests/ -q` — all 58 engine tests still pass (no engine regressions)
- **MANUAL-001:** Play a solo Standard game in the browser for 3+ years, verifying abatement, offsets, and year-advance each change the compliance position
- **MANUAL-002:** Play a solo Tutorial game and verify guided cards appear in years 1-3

## Risks and Alternatives

- **RISK-001:** Widening the phase gate to include `year_start` is the simplest fix but it changes the semantics of `year_start` from "read-only review" to "decisions allowed." **Mitigation:** In solo mode, `year_start` was never read-only (the UI already rendered decision buttons). For multiplayer, the facilitator controls when to advance to `decision_window`, and this change doesn't affect that flow.
- **ALT-001:** Instead of widening the phase gate, we could have `create_solo_game` transition the state to `decision_window` immediately after `start_simulation`. This was not chosen because it would require also changing the advance-year route to handle the `decision_window` → close → next `decision_window` transition, which is more complex. Widening the gate is simpler and aligned with the frontend's existing behavior.
- **ALT-002:** Instead of restructuring `advance_year`, we could simply delete the second `force_advance_phase` call at line 205. This is the simplest mechanical fix but leaves the route's intent unclear and doesn't handle the case where advance-year is called from `year_start` (which now needs to transition through `decision_window` → close → next year → `decision_window`). The restructured approach is more explicit.

## Grill Me

1. **Q-001:** Should the "Advance Year" button close the *current* year and open the *next* year's decision window in one click, or should there be separate "Close Year" and "Start Next Year" steps?
   - **Recommended default:** One click does both (close current year, open next year's decision window). This is simpler for solo play and matches the current UI which has a single "Advance Year" button.
   - **Why this matters:** Two-step flow would require a new "Close Year" button and different frontend state handling.
   - **If answered differently:** Add a second button and an intermediate compliance-review screen between years. More realistic but adds UI complexity.

## Suggested Next Step

Answer Q-001 (or accept the default), then begin PHASE-01 implementation. The entire sprint is small enough to complete in a single session.
