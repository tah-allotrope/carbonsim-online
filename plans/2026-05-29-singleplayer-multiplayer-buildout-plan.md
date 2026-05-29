---
title: "Sprint 4 — Single-Player Polish & Multiplayer Build-Out"
date: "2026-05-29"
status: "draft"
request: "Sequenced multiphase plans from reports/2026-05-29-single-multiplayer-game-gap-analysis.md — cluster (4): GAP-05 (build out single + multiplayer in the game stack)."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-05-29-single-multiplayer-game-gap-analysis.md"
  - "reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md"
---

# Plan: Sprint 4 — Single-Player Polish & Multiplayer Build-Out

## Objective
Promote multiplayer from an acknowledged scaffold to a real, playable mode in the game stack — lobby, room codes, host controls, a server-authoritative year cycle over WebSocket, and reconnection — while confirming single-player is solid end-to-end. This delivers the "single AND multiplayer" half of the product goal on the now-consolidated, trimmed codebase.

## Context Snapshot
- **Current state:** Single-player works after the GAP-01/02/03 fixes (recent commits `0809cba`, `464e227`, `4cc3cac`). Multiplayer/co-op is a minimal scaffold: `carbonsim_engine/coop.py` (participant/ready/snapshot logic), `mayor_api/routes/coop.py` (create/join/decision/ready/summary), `mayor_api/ws.py` (WebSocket snapshot broadcast via `coop_ws_endpoint`, wired in `mayor_api/main.py` at `/ws/games/{game_id}/{participant_id}`), and `mayor_web/coop.html`. Per the 2026-05-23 gap report it lacks: lobby/waiting screen, shareable room code, host/facilitator controls, a full year-advance cycle (ready-check only does one `force_advance_phase`), year-end compliance sync, and reconnection. Mature room/facilitator patterns from the removed oTree platform were archived in Sprint 1 (`archive/otree-platform/`).
- **Desired state:** A chosen multiplayer shape (Grill Me Q-001) fully playable: players join via room code into a lobby, a host starts/advances the session, the server authoritatively runs the year cycle and broadcasts state, players make decisions that affect their compliance, year-end results sync across all participants, and dropped clients can reconnect and resume.
- **Key repo surfaces:** `carbonsim_engine/coop.py`, `carbonsim_engine/engine.py` (year cycle, auctions/trades if competitive shape), `mayor_api/routes/coop.py`, `mayor_api/ws.py`, `mayor_api/main.py`, `mayor_web/coop.html`, `mayor_web/js/api.js`, `archive/otree-platform/SALVAGE-NOTES.md`.
- **Out of scope:** Visual step-change (Sprint 5) — this plan builds functional multiplayer with the existing UI idiom; rich visuals come next. Engine refactor (Sprint 3) is assumed done.

## Research Inputs
- `reports/2026-05-29-single-multiplayer-game-gap-analysis.md` — GAP-05: multiplayer is a scaffold; mature multiplayer lived in the doomed stack; salvage-first.
- `reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md` — Its GAP-04 enumerates the exact missing multiplayer pieces (lobby, room code, host controls, year-advance, reconnection) and the existing co-op assets to reuse.

## Assumptions and Constraints
- **ASM-001:** Sprints 1-3 complete: single product, clean tree, trimmed/tested engine; auction/facilitator surfaces are available (kept as MULTIPLAYER-CANDIDATE) if the competitive/facilitated shape is chosen.
- **ASM-002:** `mayor_api/main.py` already hosts a WebSocket endpoint and serves the static frontend, so multiplayer extends an existing real-time path rather than introducing new infra.
- **CON-001:** State must be server-authoritative (timers, year cycle, compliance, results) — a retained architecture principle from `AGENTS.md`.
- **CON-002:** Co-op games currently start in a phase where decisions are accepted only after the year-cycle fix; reuse the corrected single-player phase flow for multiplayer.
- **DEC-001:** Reuse the existing `ws.py` connection manager and `coop.py` participant model rather than introducing a new realtime framework (Colyseus/Empirica), per `AGENTS.md`.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Confirm single-player end-to-end and pick multiplayer shape | None (post-Sprint 3) | Verified solo loop; documented multiplayer shape decision |
| PHASE-02 | Lobby + room code + join flow | PHASE-01 | Room-coded create/join, lobby with participant list, host designation |
| PHASE-03 | Server-authoritative year cycle + host controls over WebSocket | PHASE-02 | Host-driven year advance, synced decisions/compliance, broadcast state machine |
| PHASE-04 | Reconnection & resilience | PHASE-03 | Reconnect/resume, drop handling, multiplayer tests |

## Detailed Phases

### PHASE-01 - Single-Player Confirmation & Multiplayer Shape
**Goal**
Lock the solo loop as the reference behavior and decide the multiplayer shape so PHASE-02+ build the right thing.

**Tasks**
- [ ] TASK-01-01: Run a full solo playthrough (create → decisions → advance years → completion → summary) and confirm decisions affect compliance; record any residual solo bugs as fast fixes.
- [ ] TASK-01-02: Decide the multiplayer shape (Grill Me Q-001): co-op shared-city, competitive shared-market (auctions/trades), or facilitator-led workshop. Document the decision and which engine surfaces it needs.
- [ ] TASK-01-03: Review `archive/otree-platform/SALVAGE-NOTES.md` and pull the relevant room/host/sync patterns into the multiplayer design.

**Files / Surfaces**
- `mayor_api/routes/game.py`, `mayor_web/game.html` - solo confirmation.
- `carbonsim_engine/coop.py`, `archive/otree-platform/` - shape design inputs.

**Dependencies**
- None beyond Sprint 3.

**Exit Criteria**
- [ ] Solo loop verified end-to-end.
- [ ] Multiplayer shape documented with the engine surfaces it requires.

**Phase Risks**
- **RISK-01-01:** Choosing competitive shape pulls in auction/trade complexity Sprint 3 may have quarantined. Mitigation: confirm those surfaces are kept (Sprint 3 Q-002) before committing to competitive.

### PHASE-02 - Lobby, Room Code & Join Flow
**Goal**
Let players gather before the game starts via a human-friendly room code, with a visible participant list and a designated host.

**Tasks**
- [ ] TASK-02-01: Add a short room-code generator and map codes → game IDs in `mayor_api/routes/coop.py` (replace raw-UUID join).
- [ ] TASK-02-02: Add a lobby state to `coop.py`: participants list, ready flags, host designation (first joiner or creator).
- [ ] TASK-02-03: Broadcast lobby state over `ws.py` so joins/leaves update all clients live.
- [ ] TASK-02-04: Build a lobby screen in `mayor_web/coop.html`: enter/display room code, participant list, host "Start" button gated on min players.

**Files / Surfaces**
- `mayor_api/routes/coop.py`, `carbonsim_engine/coop.py`, `mayor_api/ws.py`, `mayor_web/coop.html`, `mayor_web/js/api.js`.

**Dependencies**
- PHASE-01.

**Exit Criteria**
- [ ] Two browser clients join the same room via code and see each other in the lobby in real time.
- [ ] Host can start the game; non-hosts cannot.

**Phase Risks**
- **RISK-02-01:** Room-code collisions. Mitigation: check uniqueness against active games on generation; regenerate on collision.

### PHASE-03 - Server-Authoritative Year Cycle & Host Controls
**Goal**
Run the full multi-year game across participants with the server owning all transitions and the host controlling pacing.

**Tasks**
- [ ] TASK-03-01: Implement the full year-advance cycle for multiplayer (close current year → compliance/penalties → start next year → open decision window), reusing the corrected solo flow rather than the single `force_advance_phase` the scaffold uses.
- [ ] TASK-03-02: Add host controls (advance year/phase, pause/resume, and — if facilitated shape — apply shock) as host-only routes; reuse the kept engine surfaces (`pause_session`/`resume_session`/`apply_shock`) from Sprint 3.
- [ ] TASK-03-03: Ensure all participant decisions route through the corrected phase gate and broadcast updated snapshots; sync year-end compliance results to every client.
- [ ] TASK-03-04: Add a session progress indicator (current year / phase / who's ready) to the broadcast snapshot and `coop.html`.

**Files / Surfaces**
- `carbonsim_engine/coop.py`, `carbonsim_engine/engine.py` (year cycle), `mayor_api/routes/coop.py`, `mayor_api/ws.py`, `mayor_web/coop.html`.

**Dependencies**
- PHASE-02.

**Exit Criteria**
- [ ] A multi-client session plays all years to completion with synced compliance results.
- [ ] Only the host can advance/pause; participant decisions take effect and broadcast.

**Phase Risks**
- **RISK-03-01:** Decision/advance race conditions across clients. Mitigation: server-authoritative single source of truth; serialize state mutations per game; broadcast after each committed change.

### PHASE-04 - Reconnection & Resilience
**Goal**
Make the session survive dropped connections and refreshes.

**Tasks**
- [ ] TASK-04-01: On WebSocket reconnect, re-associate the participant (by participant_id) and push the current full snapshot so a refreshed client resumes seamlessly.
- [ ] TASK-04-02: Handle host disconnect (reassign host or pause) and participant disconnect (mark away, allow rejoin).
- [ ] TASK-04-03: Add multiplayer tests in `mayor_api/tests/`: room create/join, lobby broadcast, full multi-client year cycle, and a reconnect-resume case.

**Files / Surfaces**
- `mayor_api/ws.py`, `mayor_api/routes/coop.py`, `carbonsim_engine/coop.py`, `mayor_api/tests/test_api.py` (or new `test_coop.py`).

**Dependencies**
- PHASE-03.

**Exit Criteria**
- [ ] A client can refresh/reconnect mid-game and resume with correct state.
- [ ] Multiplayer tests cover join, full cycle, and reconnect, and pass.

**Phase Risks**
- **RISK-04-01:** Reconnect leaks stale connections in the manager. Mitigation: dedupe by participant_id on connect; clean up on disconnect.

## Verification Strategy
- **TEST-001:** New multiplayer tests (room/join/cycle/reconnect) pass in the unified suite.
- **MANUAL-001:** Two-to-three browser clients play a full game via room code with host pacing; verify synced compliance and reconnection by refreshing a client mid-game.
- **OBS-001:** Server logs show server-authoritative transitions and clean connect/disconnect lifecycle with no orphaned connections.

## Risks and Alternatives
- **RISK-001:** Multiplayer shape is under-specified and players get stuck. Mitigation: PHASE-01 shape decision + host-driven pacing; reuse archived oTree room patterns.
- **ALT-001:** Adopt a dedicated realtime framework (Colyseus/Empirica). Rejected for now: existing `ws.py` + `coop.py` foundation is sufficient and avoids re-introducing a heavy stack.

## Grill Me
1. **Q-001:** What is the multiplayer shape — co-op (shared city/budget), competitive (shared market with auctions/trades and a leaderboard), or facilitator-led workshop?
   - **Recommended default:** Co-op shared-session with host controls (simplest extension of the current scaffold; competitive can layer on later).
   - **Why this matters:** Determines which engine surfaces PHASE-03 reuses and the entire UI/host model.
   - **If answered differently:** Competitive needs the kept auction/trade surfaces and a leaderboard; facilitator-led needs the facilitator snapshot/analytics/export surfaces and a separate host dashboard.
2. **Q-002:** Target concurrent players per session (drives lobby min/max and broadcast load)?
   - **Recommended default:** 2-8 for the game; up to ~20 only if the facilitator-led shape is chosen.
   - **Why this matters:** Affects room sizing, broadcast batching, and test fixtures.
   - **If answered differently:** Larger sessions need broadcast throttling/batching in `ws.py`.
3. **Q-003:** Is authentication/identity needed (named players, persistence) or are ephemeral per-session identities fine?
   - **Recommended default:** Ephemeral participant_id per session; display name entered at join. No accounts.
   - **Why this matters:** Affects reconnection keying and any persistence in `mayor_api/db.py`.
   - **If answered differently:** Accounts add a users table + auth and change reconnect/identity logic.

## Suggested Next Step
Answer Q-001-Q-003, execute PHASE-01 → PHASE-04, then proceed to `plans/2026-05-29-visual-step-change-plan.md` (Sprint 5).
