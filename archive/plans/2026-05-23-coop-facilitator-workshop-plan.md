---
title: "Fix Co-op Multiplayer & Build Facilitator Dashboard (GAP-04/05)"
date: "2026-05-23"
status: "draft"
request: "Fix co-op multiplayer for workshop use (GAP-04) and build minimal facilitator dashboard (GAP-05). The co-op mode has the same phase gate bug as solo (fixed in Sprint 1), plus it lacks year-advance mechanism, lobby screen, room codes, and facilitator controls."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md"
---

# Plan: Fix Co-op Multiplayer & Build Facilitator Dashboard

## Objective

Make Climate Mayor co-op mode workshop-ready for 2-4 participants with a facilitator. Right now co-op has the same phase gate bug as solo (decisions silently rejected in `year_start`), no year-advance mechanism (ready-check only does one `force_advance_phase`), no lobby/room-code flow for easy participant onboarding, and no facilitator dashboard despite the engine having all facilitator features fully built. This sprint wires up the existing engine capabilities to API routes and frontend pages.

## Context Snapshot

- **Current state:** Co-op mode creates games, adds participants, shows a basic UI with ready-check and abatement activation, and has WebSocket real-time sync. But decisions are silently rejected (same phase bug as solo GAP-02), there's no way to advance years (ready-check only transitions `year_start` → `decision_window`, never closes a year), participants join via raw UUID (no room codes), and there's no facilitator view despite `build_facilitator_snapshot()`, `build_session_analytics()`, `export_session_data()`, `pause_session()`, `resume_session()`, and `apply_shock()` all being fully implemented in the engine.
- **Desired state:** A facilitator creates a co-op game, gets a short room code, shares it with 2-4 participants who join via a lobby screen, all participants make decisions (abatement, offsets) that actually take effect, a ready-check triggers year-advance, the facilitator monitors progress and can pause/apply shocks/export data, and the game plays through multiple years to completion.
- **Key repo surfaces:**
  - `carbonsim_engine/coop.py` — co-op game creation, participant management, ready-check
  - `mayor_api/routes/coop.py` — co-op API routes (create, join, decision, ready, summary)
  - `mayor_web/coop.html` — co-op participant UI
  - `mayor_api/ws.py` — WebSocket connection manager
  - `mayor_api/main.py` — FastAPI app, mounts routers, WebSocket endpoint
  - `mayor_api/models.py` — Pydantic request models
  - `carbonsim_engine/engine.py:815-891` — `build_facilitator_snapshot()` (fully built)
  - `carbonsim_engine/engine.py:933-1111` — `build_session_analytics()` (fully built)
  - `carbonsim_engine/engine.py:1114-1180` — `export_session_data()` (fully built)
  - `carbonsim_engine/engine.py:517-552` — `pause_session()` / `resume_session()` (fully built)
  - `carbonsim_engine/engine.py:1323-1453` — `apply_shock()` (fully built, 10 shock types)
  - `carbonsim_engine/engine.py:555-617` — `force_advance_phase()` (general-purpose phase transitions)
- **Out of scope:** Solo mode fixes (Sprint 1), game balance tuning, mobile-responsive CSS, data visualization/charting in facilitator dashboard, authentication beyond simple facilitator tokens, production deployment.

## Research Inputs

No applicable research briefs were found in `research/`. The gap analysis at `reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md` provides all necessary context for GAP-04 and GAP-05.

## Assumptions and Constraints

- **ASM-001:** Sprint 1 (GAP-01/02/03/06) has been completed before this sprint begins. The phase gate in `apply_company_decision` already accepts both `year_start` and `decision_window`, and the solo `advance_year` route is fixed. This sprint inherits the phase-gate fix for co-op automatically since co-op uses the same `apply_company_decision` function.
- **ASM-002:** The co-op year-advance mechanism should be triggered by all-participants-ready, not by a single facilitator button. The facilitator can force-advance as an override, but the normal flow is collaborative ready-check. This matches the existing `all_participants_ready()` function in `coop.py`.
- **ASM-003:** Room codes should be short (6 alphanumeric characters) and human-readable for workshop use. Participants type the code on the join screen rather than sharing a full URL with a UUID.
- **ASM-004:** The facilitator dashboard is a separate page (`/facilitator.html?id=GAME_ID`) that polls the facilitator snapshot endpoint. WebSocket push is nice-to-have but not required — polling every 3-5 seconds is sufficient for a workshop with 2-4 participants.
- **ASM-005:** The `player_count` limit of 2-4 in `CreateCoopGameRequest` is appropriate for workshop use and should not change.
- **CON-001:** The `force_advance_phase` function in the engine must not be modified — it is a general-purpose phase transition used by multiple consumers.
- **CON-002:** The existing WebSocket infrastructure (`CoopConnectionManager` in `ws.py`) should be reused and extended, not replaced.
- **CON-003:** All existing API and engine tests must continue to pass.
- **DEC-001:** The facilitator dashboard will use the existing engine functions directly — no new engine logic is needed. All six facilitator functions (`build_facilitator_snapshot`, `build_session_analytics`, `export_session_data`, `pause_session`, `resume_session`, `apply_shock`) are fully implemented and tested.

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Add year-advance to co-op ready-check and verify phase-gate fix carries over | Sprint 1 complete | Modified `coop.py`, `routes/coop.py`; co-op decisions work, ready-check advances years |
| PHASE-02 | Add lobby screen with room codes and participant onboarding | PHASE-01 | Modified `coop.py`, `routes/coop.py`, `models.py`, `coop.html`; new `lobby.html` |
| PHASE-03 | Build facilitator dashboard with API routes and frontend | PHASE-01 | New `routes/facilitator.py`, `facilitator.html`; facilitator can monitor, pause, shock, export |
| PHASE-04 | Add co-op and facilitator tests, manual verification | PHASE-01, PHASE-02, PHASE-03 | New test functions in `test_api.py`; verified workshop flow |

## Detailed Phases

### PHASE-01 — Fix Co-op Year-Advance and Verify Phase-Gate Fix

**Goal**

Make co-op decisions actually take effect (inherited from Sprint 1 phase-gate fix) and implement a full year-advance cycle triggered by all-participants-ready, so co-op games can progress through multiple years.

**Tasks**

- [ ] TASK-01-01: Verify that the Sprint 1 phase-gate fix in `engine.py:178` (widening `apply_company_decision` to accept `year_start`) automatically fixes co-op decisions. Run a quick manual test: create co-op game, add participant, call decision endpoint, verify state changed.
- [ ] TASK-01-02: In `mayor_api/routes/coop.py`, modify the ready-check endpoint (lines 112-137) to perform a full year-advance cycle when `all_participants_ready()` returns `True`. Current behavior: calls `force_advance_phase` once (`year_start` → `decision_window`). New behavior: (1) call `force_advance_phase` repeatedly until phase reaches `compliance` (closing the current year), (2) run bot turns if any bots exist, (3) call `force_advance_phase` to advance from `compliance` to next `year_start`, (4) call `force_advance_phase` once more to reach `decision_window`, (5) draw event cards via `draw_event_cards`, (6) reset ready-check via `reset_ready_check`, (7) broadcast updated snapshot via WebSocket.
- [ ] TASK-01-03: In `carbonsim_engine/coop.py`, add a `advance_coop_year(state)` helper function that encapsulates the year-advance logic from TASK-01-02 (force-advance through compliance, start next year, open decision window, draw cards). This keeps the route handler clean and makes the logic reusable for facilitator force-advance.
- [ ] TASK-01-04: Handle the edge case where ready-check is triggered but the game is already in `compliance` or `complete` phase — the year-advance should be a no-op or return appropriate status.
- [ ] TASK-01-05: Update the co-op decision endpoint (`routes/coop.py:82-100`) to return the actual engine result in the response (not just `{"status": "applied"}`) so the frontend can show feedback on decision success/failure.
- [ ] TASK-01-06: Run `pytest mayor_api/tests/test_api.py -q` and `pytest carbonsim_engine/tests/ -q` to verify no regressions. All existing tests must pass.

**Files / Surfaces**

- `carbonsim_engine/coop.py` — add `advance_coop_year()` helper
- `mayor_api/routes/coop.py:82-100` — improve decision response
- `mayor_api/routes/coop.py:112-137` — implement year-advance on all-ready
- `carbonsim_engine/engine.py:178` — verify phase-gate fix (read-only)

**Dependencies**

- Sprint 1 (GAP-01/02 phase-gate fix) must be complete

**Exit Criteria**

- [ ] Co-op decision endpoint modifies game state (cash decreases, abatement activates) when called in `year_start` phase
- [ ] When all participants set ready, game advances to next year's `decision_window` phase with cards drawn
- [ ] Ready-check resets after year advance so participants can ready-up again for the next year
- [ ] WebSocket broadcasts updated snapshot after year advance
- [ ] All existing tests pass

**Phase Risks**

- **RISK-01-01:** The year-advance logic in co-op must handle the case where bots exist in the game (co-op games can have bot companies). **Mitigation:** The solo `advance_year` route already runs bot turns via `run_bot_company_turns` — reuse the same pattern in `advance_coop_year`.
- **RISK-01-02:** Multiple participants hitting ready simultaneously could trigger duplicate year-advances due to race conditions. **Mitigation:** Add a guard that checks the current phase before advancing — if already past `decision_window`, skip the advance. The in-memory game store is single-threaded in the current architecture (no async database), so true race conditions are unlikely.

---

### PHASE-02 — Lobby Screen with Room Codes and Participant Onboarding

**Goal**

Replace the raw UUID join flow with a short room code and a lobby screen where participants can see who has joined, their assigned company, and wait for the facilitator to start the game.

**Tasks**

- [ ] TASK-02-01: In `carbonsim_engine/coop.py`, add a `generate_room_code()` function that produces a 6-character alphanumeric code (uppercase, no ambiguous characters like O/0/I/1). Store a mapping from room code to game ID in the game state under `state["room_code"]`.
- [ ] TASK-02-02: In `mayor_api/routes/coop.py`, modify the create-coop endpoint to generate and return a room code alongside the game ID. Add a new `GET /api/coop/join/{room_code}` endpoint that resolves a room code to a game ID and participant assignment.
- [ ] TASK-02-03: In `mayor_api/routes/coop.py`, add a `POST /api/coop/join` endpoint that accepts `{ room_code, player_name }`, resolves the room code to a game ID, calls `add_coop_participant()`, and returns `{ game_id, participant_id, company_name }`.
- [ ] TASK-02-04: In `mayor_api/models.py`, add `JoinCoopByCodeRequest` Pydantic model with `room_code: str` and `player_name: str` fields.
- [ ] TASK-02-05: Create `mayor_web/lobby.html` — a waiting room page that: (a) shows the room code prominently for sharing, (b) lists all connected participants with their company names and ready status, (c) polls the co-op state endpoint every 3 seconds to update the participant list, (d) has a "Join Game" form for participants who arrive via the room code, (e) transitions to `coop.html` when the facilitator starts the game or when the game phase leaves `lobby`/`year_start`.
- [ ] TASK-02-06: Update `mayor_web/coop.html` to show the room code in the session info card and add a "Copy Room Code" button for easy sharing.
- [ ] TASK-02-07: Update the co-op creation flow in `mayor_web/index.html` (if applicable) or the existing co-op creation UI to redirect to `lobby.html` after creating a co-op game, displaying the room code.

**Files / Surfaces**

- `carbonsim_engine/coop.py` — add `generate_room_code()`, store code in state
- `mayor_api/routes/coop.py` — new join-by-code endpoint, modify create endpoint
- `mayor_api/models.py` — add `JoinCoopByCodeRequest`
- `mayor_web/lobby.html` — new lobby/waiting-room page
- `mayor_web/coop.html` — show room code
- `mayor_web/index.html` — update co-op creation flow redirect

**Dependencies**

- PHASE-01 (co-op decisions and year-advance must work for the lobby-to-game transition to be meaningful)

**Exit Criteria**

- [ ] Creating a co-op game returns a 6-character room code
- [ ] Participants can join by entering the room code and their name
- [ ] The lobby page shows all connected participants in real-time
- [ ] The lobby transitions to the game page when the game starts
- [ ] The room code is visible and copyable during gameplay

**Phase Risks**

- **RISK-02-01:** Room code collisions are theoretically possible with 6 alphanumeric chars (~1.5B combinations). **Mitigation:** For a workshop with <100 games, collision probability is negligible. Add a simple collision check on generation — regenerate if the code is already in use.
- **RISK-02-02:** The room-code-to-game-ID mapping is in-memory (no database). If the server restarts, room codes are lost. **Mitigation:** Acceptable for a workshop demo. The game save/load feature preserves game state but room codes would need to be re-generated on reload — document this limitation.

---

### PHASE-03 — Facilitator Dashboard with API Routes

**Goal**

Build a facilitator dashboard that exposes all existing engine facilitator capabilities through API routes and a dedicated frontend page. The facilitator can monitor participant progress, pause/resume the session, apply shocks, force-advance phases, and export session data.

**Tasks**

- [ ] TASK-03-01: Create `mayor_api/routes/facilitator.py` with the following endpoints:
  - `GET /api/facilitator/{game_id}/snapshot` — calls `build_facilitator_snapshot(state)` and returns the result. Includes participant rows, auction log, analytics summary, and replay data.
  - `GET /api/facilitator/{game_id}/analytics` — calls `build_session_analytics(state)` and returns detailed session analytics.
  - `POST /api/facilitator/{game_id}/pause` — calls `pause_session(state)` and saves updated state.
  - `POST /api/facilitator/{game_id}/resume` — calls `resume_session(state)` and saves updated state.
  - `POST /api/facilitator/{game_id}/advance-phase` — calls `force_advance_phase(state)` and saves updated state. Broadcasts via WebSocket.
  - `POST /api/facilitator/{game_id}/advance-year` — calls the same `advance_coop_year()` helper from PHASE-01 to perform a full year-advance cycle. Resets ready-check. Broadcasts via WebSocket.
  - `POST /api/facilitator/{game_id}/shock` — accepts `{ shock_type, params }`, calls `apply_shock(state, shock_type, **params)` and saves updated state. Broadcasts via WebSocket.
  - `GET /api/facilitator/{game_id}/export` — calls `export_session_data(state)` and returns JSON (or CSV if format param is specified).
- [ ] TASK-03-02: In `mayor_api/models.py`, add Pydantic models: `ApplyShockRequest` with `shock_type: str` and `params: dict`, and `ExportRequest` with optional `format: str`.
- [ ] TASK-03-03: In `mayor_api/main.py`, import and mount the facilitator router: `app.include_router(facilitator_router, prefix="/api/facilitator", tags=["facilitator"])`.
- [ ] TASK-03-04: Create `mayor_web/facilitator.html` — a dashboard page that:
  - Shows the game overview: current year, phase, room code, participant count
  - Displays a participant table with company name, cash, emissions, compliance gap, ready status (from `build_facilitator_snapshot` participant_rows)
  - Has control buttons: Pause/Resume (toggle), Force Advance Phase, Force Advance Year
  - Has a shock panel: dropdown of available shock types (from engine's `SHOCK_TYPES`), parameter inputs, "Apply Shock" button
  - Has an export button that downloads session data as JSON
  - Auto-refreshes every 3-5 seconds by polling the snapshot endpoint
  - Uses the same CSS framework (`style.css`, `animations.css`) as the rest of the app
- [ ] TASK-03-05: Add a facilitator link to the co-op creation response and lobby page so the game creator can easily open the facilitator view.
- [ ] TASK-03-06: Add basic facilitator token authorization: the create-coop endpoint generates a `facilitator_token` (UUID) stored in state, and facilitator endpoints require this token as a query parameter or header. This prevents participants from accessing facilitator controls.

**Files / Surfaces**

- `mayor_api/routes/facilitator.py` — new file, 8 API endpoints
- `mayor_api/models.py` — add shock and export request models
- `mayor_api/main.py` — mount facilitator router
- `mayor_web/facilitator.html` — new file, facilitator dashboard page
- `carbonsim_engine/engine.py:815-891` — `build_facilitator_snapshot()` (called, not modified)
- `carbonsim_engine/engine.py:933-1111` — `build_session_analytics()` (called, not modified)
- `carbonsim_engine/engine.py:1114-1180` — `export_session_data()` (called, not modified)
- `carbonsim_engine/engine.py:517-552` — `pause_session()` / `resume_session()` (called, not modified)
- `carbonsim_engine/engine.py:1323-1453` — `apply_shock()` (called, not modified)

**Dependencies**

- PHASE-01 (the `advance_coop_year()` helper is reused for facilitator force-advance-year)

**Exit Criteria**

- [ ] All 8 facilitator API endpoints return correct data from the engine functions
- [ ] The facilitator dashboard page loads and displays participant progress
- [ ] Pause/resume toggles session state and is reflected in participant UI
- [ ] Applying a shock (e.g., `demand_shock`) modifies game state and is broadcast to participants
- [ ] Export endpoint returns complete session data as JSON
- [ ] Facilitator endpoints reject requests without a valid facilitator token
- [ ] All existing tests still pass

**Phase Risks**

- **RISK-03-01:** The `apply_shock` function accepts 10 different shock types with varying parameters. The facilitator UI needs to dynamically render appropriate input fields for each shock type. **Mitigation:** Start with a simple JSON textarea for shock params. If time permits, add type-specific forms for the most common shocks (demand_shock, supply_shock, policy_shock).
- **RISK-03-02:** The facilitator token is a simple UUID with no expiry or rotation. **Mitigation:** Acceptable for a workshop demo. For production, upgrade to JWT or session-based auth.
- **RISK-03-03:** Polling every 3-5 seconds creates N+1 requests per dashboard. **Mitigation:** For 2-4 participants this is negligible. The facilitator snapshot is lightweight (no heavy computation). If needed, upgrade to WebSocket push in a future sprint.

---

### PHASE-04 — Tests and Manual Verification

**Goal**

Add automated tests for co-op year-advance, room-code join flow, and facilitator endpoints. Manually verify a complete workshop simulation: create game with room code → participants join via lobby → make decisions → ready-check advances year → facilitator monitors and applies shock → export data.

**Tasks**

- [ ] TASK-04-01: Add `test_coop_decision_works` to `test_api.py`: create co-op game, add participant, call decision endpoint, GET state, verify cash decreased and abatement activated.
- [ ] TASK-04-02: Add `test_coop_ready_advances_year` to `test_api.py`: create co-op game with 2 participants, set both ready, verify game phase advances to `decision_window` of next year with cards drawn.
- [ ] TASK-04-03: Add `test_coop_room_code_join` to `test_api.py`: create co-op game, verify room code is returned, join by room code with a player name, verify participant is added.
- [ ] TASK-04-04: Add `test_facilitator_snapshot` to `test_api.py`: create co-op game, call facilitator snapshot endpoint, verify it returns participant_rows, analytics, and replay data.
- [ ] TASK-04-05: Add `test_facilitator_pause_resume` to `test_api.py`: create co-op game, call pause endpoint, verify state is paused, call resume, verify state is resumed.
- [ ] TASK-04-06: Add `test_facilitator_apply_shock` to `test_api.py`: create co-op game, apply a `demand_shock`, verify game state reflects the shock effect.
- [ ] TASK-04-07: Add `test_facilitator_export` to `test_api.py`: create co-op game, advance through 1-2 years, call export endpoint, verify it returns complete session data with year-by-year results.
- [ ] TASK-04-08: Add `test_facilitator_token_required` to `test_api.py`: verify facilitator endpoints return 403 without a valid token.
- [ ] TASK-04-09: Run the full test suite: `pytest mayor_api/tests/test_api.py -q` and `pytest carbonsim_engine/tests/ -q`. All tests must pass.
- [ ] TASK-04-10: Manual verification — start the dev server, simulate a workshop flow:
  1. Create a co-op game via the UI, note the room code
  2. Open the facilitator dashboard in another tab
  3. Join as 2 participants using the room code via the lobby page
  4. As each participant: activate an abatement, buy offsets
  5. Set both participants ready, verify year advances
  6. On facilitator dashboard: verify participant progress is visible, apply a demand_shock, verify participants see the effect
  7. Play through 2-3 years
  8. Export session data from facilitator dashboard

**Files / Surfaces**

- `mayor_api/tests/test_api.py` — add 8 new test functions
- Browser at `http://localhost:8000` — manual workshop simulation

**Dependencies**

- PHASE-01, PHASE-02, PHASE-03 all complete

**Exit Criteria**

- [ ] All 8 new tests pass
- [ ] All existing tests still pass (total: 83 existing + 8 new = 91 minimum)
- [ ] A complete workshop simulation (create → lobby → join → decide → advance → shock → export) works end-to-end in the browser
- [ ] WebSocket broadcasts update all participant views when the facilitator acts
- [ ] No JavaScript console errors during the workshop simulation
- [ ] No HTTP 4xx/5xx errors in the server log during the workshop simulation

**Phase Risks**

- **RISK-04-01:** WebSocket broadcast during year-advance or shock application could fail silently if participants have disconnected. **Mitigation:** The existing `CoopConnectionManager.broadcast_snapshot` already handles disconnected clients gracefully (removes them from the room). Add a try/except around broadcast calls in new code.

## Verification Strategy

- **TEST-001:** `pytest mayor_api/tests/test_api.py -q` — all tests pass including 8 new co-op/facilitator tests
- **TEST-002:** `pytest carbonsim_engine/tests/ -q` — all 58 engine tests still pass (no engine modifications in this sprint)
- **MANUAL-001:** Simulate a 2-participant workshop: create co-op game with room code, join via lobby, make decisions, ready-check advances year, play 3 years
- **MANUAL-002:** Facilitator dashboard: monitor progress, pause/resume, apply shock, export data — verify all controls work
- **MANUAL-003:** Verify WebSocket real-time sync: participant A activates abatement, participant B's view updates within 3 seconds

## Risks and Alternatives

- **RISK-001:** The in-memory game store means all state is lost on server restart. Workshop games that take >1 hour could be at risk if the server crashes. **Mitigation:** The existing save/load feature (`game.py:388-410`) persists to SQLite. The facilitator could manually save periodically, or auto-save could be added on each year-advance.
- **RISK-002:** The WebSocket implementation in `ws.py` uses a simple dict-of-lists pattern. Under load (many rapid state changes), message ordering could become an issue. **Mitigation:** For 2-4 participants, this is not a concern. The snapshot-based approach (send full state, not deltas) means any single message is self-contained.
- **ALT-001:** Instead of room codes, we could use shareable URLs with game IDs. This was not chosen because workshop participants often join from different devices and typing a short code is easier than sharing/scanning a URL. Room codes are more workshop-friendly.
- **ALT-002:** Instead of a polling-based facilitator dashboard, we could use WebSocket push. This was not chosen for Sprint 2 because the polling approach is simpler to implement and debug, and the 3-5 second refresh is acceptable for a workshop with 2-4 participants. WebSocket push can be added in a future sprint if needed.
- **ALT-003:** Instead of a separate facilitator page, we could add facilitator controls to the existing co-op page conditionally. This was not chosen because the facilitator view is fundamentally different (overview of all participants, admin controls) and mixing it into the participant view would make both harder to maintain.

## Grill Me

1. **Q-001:** Should the facilitator be able to force-advance the year even if not all participants are ready?
   - **Recommended default:** Yes — the facilitator should have a "Force Advance Year" button that bypasses the ready-check. This is important for workshops where a participant may be AFK or confused.
   - **Why this matters:** Without this, a single unresponsive participant blocks the entire session.
   - **If answered differently:** Remove the force-advance-year endpoint and rely solely on the all-ready mechanism. Add a facilitator "kick participant" button as an alternative.

2. **Q-002:** Should the lobby page support late-joining participants (joining after the game has started)?
   - **Recommended default:** Yes, allow late joins until `player_count` is reached. The `add_coop_participant()` function in `coop.py` already supports this — it assigns the next available company regardless of game phase.
   - **Why this matters:** In a workshop, participants may arrive late or need to rejoin after a connection issue.
   - **If answered differently:** Lock participant list after the first year-advance. Late arrivals watch or wait for the next game.

3. **Q-003:** What shock types should be prominently featured in the facilitator dashboard UI?
   - **Recommended default:** Show all 10 shock types in a dropdown, but feature the 3 most workshop-relevant ones (demand_shock, supply_shock, policy_shock) with pre-filled parameter forms. Other shocks use a generic JSON params input.
   - **Why this matters:** The facilitator needs to apply shocks quickly during a live session. Too many options cause decision paralysis; too few limit the simulation's educational value.
   - **If answered differently:** Show only the 3 featured shocks with a toggle to reveal advanced options.

## Suggested Next Step

Accept the defaults for Q-001 through Q-003 (or provide alternatives), then begin PHASE-01 implementation. This sprint depends on Sprint 1 (GAP-01/02/03/06) being complete first.
