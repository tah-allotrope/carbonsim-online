# Gap Analysis: Climate Mayor Workshop Demo Readiness

**Date:** 2026-05-23
**Scope:** Solo and multiplayer gameplay must be functional for a live workshop demo with 10-20 participants.
**Status:** Draft for Review

---

## Executive Summary

The Climate Mayor game has strong foundational architecture (engine, scenarios, abatement/offset/compliance logic, card system, UI polish) but **two critical bugs in the game loop make solo play completely non-functional**: player decisions are silently rejected because the backend only accepts actions in a phase the player never reaches, and the advance-year endpoint immediately skips through the decision window. Co-op/multiplayer is a minimal scaffold that shares the same phase bug and lacks facilitator controls entirely. Fixing the 2 critical bugs unblocks solo play; workshop multiplayer requires additional sprint work.

---

## Current Capabilities (What We Have)

| Capability | Status | Key Surfaces |
|---|---|---|
| Solo game creation & difficulty tiers | Working | `carbonsim_engine/solo.py`, `mayor_api/routes/game.py:106-128`, `mayor_web/index.html` |
| Compliance engine (allocation, penalties, banking) | Working | `carbonsim_engine/engine.py:1669-1760` (`_close_current_year`) |
| Abatement activation logic | Working (engine) | `carbonsim_engine/engine.py:181-208` |
| Offset purchase logic | Working (engine) | `carbonsim_engine/engine.py:210-231` |
| Event card system (50+ cards, draw/resolve) | Working (engine) | `carbonsim_engine/cards.py`, `carbonsim_engine/data/starter_deck.json`, `expansion_deck.json` |
| Scenario packs (solo_easy/standard/hard/tutorial) | Mature | `carbonsim_engine/scenarios.py` |
| Shock system (10 shock types) | Working | `carbonsim_engine/engine.py:1323-1453` |
| Game save/load | Working | `mayor_api/routes/game.py:388-410` |
| UI with animations, audio, XP/progression | Working | `mayor_web/game.html`, `mayor_web/js/`, `mayor_web/css/` |
| Tutorial mode (3-year guided) | Partial — has same phase bug | `carbonsim_engine/tutorial.py`, `mayor_api/routes/game.py:184-191` |
| Co-op mode (create/join/ready-check/WebSocket) | Partial — scaffold only | `carbonsim_engine/coop.py`, `mayor_api/routes/coop.py`, `mayor_web/coop.html` |
| Game phase state machine | Working (engine) | `carbonsim_engine/engine.py:555-617` (`force_advance_phase`) |
| Player decision routing (API) | **Broken** — phase mismatch | `mayor_api/routes/game.py:236-261` |
| Advance-year flow (API) | **Broken** — skips decision window | `mayor_api/routes/game.py:156-214` |
| Facilitator dashboard | Missing | — |
| Room/session join flow for workshops | Missing | — |
| Data export route | Missing (engine exists) | `carbonsim_engine/engine.py:1114-1180` (no route) |
| Bot participants | Working | `carbonsim_engine/engine.py:1456-1551` |
| Auction system | Working (engine) | `carbonsim_engine/engine.py:377-504` |
| Trade system | Working (engine) | `carbonsim_engine/engine.py:256-374` |
| Achievement system | Working | `carbonsim_engine/achievements.py` |
| API test suite | Working (25 pass) — weak assertions | `mayor_api/tests/test_api.py` |
| Engine test suite | Working (58 pass) | `carbonsim_engine/tests/` |

---

## Target State

> A workshop-ready Climate Mayor game where:
> 1. **Solo play works end-to-end**: a single player can create a game, make meaningful decisions (activate abatement, buy offsets), see those decisions affect their compliance position, advance years, and reach game completion.
> 2. **Tutorial mode guides first-time players** through the core ETS compliance loop.
> 3. **Multiplayer/co-op supports a live workshop** with 2+ participants making decisions, a facilitator controlling session flow, and real-time state synchronization.
> 4. The game is stable enough that a facilitator can confidently demo it without hitting silent failures or broken flows.

---

## Gap Analysis

### GAP-01: Decision Window Is Skipped — Player Actions Never Take Effect

**Severity:** CRITICAL — Blocks solo and multiplayer gameplay entirely

**Current state:**

The advance-year API route (`mayor_api/routes/game.py:156-214`) calls `force_advance_phase()` **twice** in sequence (lines 199 and 205). The first call moves the state from `year_start` → `decision_window`. The second call immediately moves from `decision_window` → `compliance`, closing the year and applying penalties. The player never has an opportunity to make decisions during the `decision_window` phase.

Verified by running the actual engine code:

```
After FIRST force_advance_phase: phase = decision_window
After SECOND force_advance_phase: phase = compliance
```

**What's needed:**
- Remove the second `force_advance_phase()` call from the advance-year route, so the route stops after entering `decision_window` (where the player can then act)
- OR restructure the advance-year route to represent the intended solo flow: close the current year and open the next year's decision window in one step
- Ensure the advance-year button in the frontend triggers the correct sequence: close current year → open next year → stay in `decision_window`

**Existing assets to reuse:**
- `force_advance_phase()` already handles all phase transitions correctly (`carbonsim_engine/engine.py:555-617`)
- `_close_current_year()` correctly calculates compliance, penalties, and banking (`engine.py:1669-1760`)
- `_start_year()` correctly sets up allocation, auctions, and emissions for the next year (`engine.py:1589-1666`)
- The `end-year` route (`game.py:263-291`) already implements a "close year and advance" pattern that could be adapted

**Effort estimate:** Small fix — 1 function change in `game.py`, ~10 lines

---

### GAP-02: Decisions Rejected in year_start Phase

**Severity:** CRITICAL — Blocks all player actions after game creation and after each year transition

**Current state:**

`apply_company_decision()` in `carbonsim_engine/engine.py:178` has a hard guard:

```python
if state["phase"] != PHASE_DECISION_WINDOW:
    return state  # silently ignores the decision
```

But `create_solo_game()` starts the game in `year_start` phase (via `start_simulation()` → `_start_year()`). The frontend renders the abatement menu and offset market for both `year_start` and `decision_window` phases (`game.html:328`), so the player sees active buttons that silently do nothing.

Verified:
```
Phase: year_start
Tried activate_abatement → Cash changed? False
Active abatement IDs: []
```

**What's needed:**
- Either: extend `apply_company_decision` to also accept decisions in `year_start` phase (since the UI already allows it)
- Or: have `create_solo_game` start the game directly in `decision_window` phase (or immediately transition to it)
- The fix must be coordinated with GAP-01 so the player has a consistent phase to make decisions in

**Existing assets to reuse:**
- `apply_company_decision` logic is fully correct — the only issue is the phase gate at line 178
- `_set_phase()` can be called to set the initial phase to `decision_window` if needed

**Effort estimate:** Small fix — 1-2 line change in `engine.py` or `solo.py`

---

### GAP-03: Frontend Abatement Status Display Uses Missing Fields

**Severity:** HIGH — Player cannot see which abatements are active even after fixing GAP-01/02

**Current state:**

The frontend (`mayor_web/game.html:197-198`) reads:
```javascript
const activeIds = player.active_abatement_ids || [];
const pendingIds = player.pending_abatement_ids || [];
```

But `_company_snapshot()` in `engine.py:1554-1586` does **not** include `active_abatement_ids` or `pending_abatement_ids` in the returned dict. Instead, each menu item has `"active"` and `"pending"` boolean flags. The frontend's `activeIds` array is always empty, so all abatements always show "Activate" buttons even when already activated.

**What's needed:**
- Change `game.html:197-198` to derive active/pending status from the menu item flags: `const isActive = m.active;` instead of `activeIds.includes(m.measure_id)`
- OR add `active_abatement_ids` and `pending_abatement_ids` to `_company_snapshot()` return dict

**Existing assets to reuse:**
- The snapshot already contains the correct data — just in `menu[i].active` / `menu[i].pending` fields

**Effort estimate:** Small fix — 4 lines in `game.html`

---

### GAP-04: Co-op Mode Has Same Phase Bug and Lacks Workshop Features

**Severity:** HIGH — Co-op is not usable for a workshop demo

**Current state:**

Co-op decisions (`mayor_api/routes/coop.py:82-100`) call the same `apply_company_decision()` that has the phase gate. Co-op games also start in `year_start` phase, so co-op decisions are equally rejected.

Beyond the phase bug, the co-op mode is acknowledged as "an early but working co-op scaffold" (`activeContext.md:36`). It lacks:
- A way to advance years (the ready-check only does one `force_advance_phase`, which moves from `year_start` → `decision_window` but doesn't handle the full year-close cycle)
- Facilitator controls (start session, pause, advance phase, apply shocks)
- Room code or shareable join link
- Lobby screen showing connected participants before game starts
- Year-end compliance display synchronized across participants
- Any indication of which year the game is on, or timeline/progress

**What's needed:**
- Fix the phase bug (same as GAP-01/02)
- Add a year-advance mechanism for co-op (either facilitator-triggered or all-ready-check)
- Add a lobby/waiting screen with participant list
- Add a shareable room code or join link
- Add facilitator controls (at minimum: advance year, pause)

**Existing assets to reuse:**
- `carbonsim_engine/coop.py` has working participant management, ready-check, and snapshot logic
- `mayor_api/routes/coop.py` has working create/join/decision/ready/summary endpoints
- `mayor_web/coop.html` has a functional (if basic) co-op UI with ready-check and abatement activation
- `mayor_api/ws.py` has WebSocket connection management that broadcasts snapshots

**Effort estimate:** 1 multi-phase plan (2-3 phases): phase-bug fix + year-advance mechanism (1 phase), facilitator controls + lobby (1 phase), polish (1 phase)

---

### GAP-05: No Facilitator Dashboard

**Severity:** MEDIUM — Limits workshop usability but not solo demo

**Current state:**

The engine has `build_facilitator_snapshot()` (`engine.py:815-891`) with participant monitoring, auction logs, session analytics, and replay data. But there is no API route or frontend page that uses it. Workshop facilitators have no way to:
- Monitor participant progress
- Force-advance phases
- Apply shocks mid-game
- View session analytics
- Export session data

**What's needed:**
- A facilitator dashboard page (HTML + JS)
- API routes for facilitator actions (advance phase, apply shock, pause/resume, export)
- Authentication or role-based access (even a simple facilitator token)

**Existing assets to reuse:**
- `build_facilitator_snapshot()` in `engine.py:815-891` — fully built
- `build_session_analytics()` in `engine.py:933-1111` — fully built
- `export_session_data()` in `engine.py:1114-1180` — fully built
- `pause_session()` / `resume_session()` in `engine.py:517-552` — fully built
- `apply_shock()` in `engine.py:1323-1453` — fully built

**Effort estimate:** 1 multi-phase plan (2 phases): routes + basic HTML (1 phase), polish + export (1 phase)

---

### GAP-06: Test Assertions Don't Verify State Changes

**Severity:** MEDIUM — False confidence in test suite masks bugs

**Current state:**

`test_decision_activate_abatement` (`test_api.py:122-144`) calls the decision endpoint after `advance-year` and only checks `resp.status_code == 200` and `resp.json()["status"] == "applied"`. It does not verify that the player's cash decreased, emissions changed, or `active_abatement_ids` was updated. Because the decision endpoint always returns `{"status": "applied"}` even when the engine silently ignores the action (wrong phase), the test passes without the decision having any effect.

Similarly, `test_advance_year` only checks `data["year"] >= 1` without verifying the phase or that the game state meaningfully advanced.

**What's needed:**
- Add state-change assertions to decision tests (verify cash, emissions, active IDs changed)
- Add phase assertions to lifecycle tests
- Add an end-to-end test that creates a game, makes a decision, advances year, and verifies the decision affected compliance outcomes

**Existing assets to reuse:**
- The test client and fixtures are solid (`test_api.py:1-31`)
- `GET /api/games/{id}` returns full snapshots with all necessary fields

**Effort estimate:** Small — add 10-15 assertion lines to existing tests, plus 1 new end-to-end test

---

## Second-Tier Gaps

| Gap | Severity | Summary | Existing Assets |
|---|---|---|---|
| GAP-07 | MEDIUM | No data export API route — `export_session_data()` exists in engine but no endpoint exposes it | `engine.py:1114-1180` |
| GAP-08 | MEDIUM | Compliance gap calculation inconsistency — engine `compliance_gap` doesn't factor offset cap; frontend recalculates with cap | `engine.py:1894-1905` vs `game.html:192-193` |
| GAP-09 | LOW | Event cards drawn but immediately consumed by year-close due to GAP-01 — cards never give player time to act | Resolves automatically when GAP-01 is fixed |
| GAP-10 | LOW | No mobile-responsive testing evidence for workshop tablet use | CSS framework exists in `mayor_web/css/style.css` |
| GAP-11 | LOW | Summary page completeness — `summary.html` exists but may not render all data correctly without a working game loop | `mayor_web/summary.html` |
| GAP-12 | LOW | No room code or shareable link for workshop participant onboarding | Co-op uses raw UUID game IDs |

---

## Recommended Sprint Sequencing

| Priority | Gap | Rationale |
|---|---|---|
| Sprint 1 (Immediate) | GAP-01, GAP-02, GAP-03 | These 3 fixes together unblock solo play. ~30 minutes of work. Without these, the game is completely non-functional. |
| Sprint 1 (Immediate) | GAP-06 | Fix test assertions so they catch regressions. Should be done alongside GAP-01/02/03 to verify the fixes. |
| Sprint 2 (Before workshop) | GAP-04 | Fix co-op phase bug and add year-advance mechanism. Required for any multiplayer demo. |
| Sprint 2 (Before workshop) | GAP-05 | Build minimal facilitator dashboard. Required for facilitator-led workshops. |
| Sprint 3 (If time permits) | GAP-07, GAP-08 | Data export route and compliance gap consistency. Nice-to-have for post-workshop analysis. |
| Backlog | GAP-09-12 | Polish items that resolve automatically (GAP-09), or are nice-to-have for a first demo. |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Fixing GAP-01/02 changes game balance assumptions | Playtest metrics from `activeContext.md` were generated with the broken flow (fast-forward route has its own decision logic) — real player-driven balance may differ | Medium | Run a manual playthrough after fixing; adjust scenario parameters if needed |
| Co-op year-advance mechanism is under-designed | Workshop participants could get stuck if the year-advance flow isn't intuitive | Medium | Use the ready-check mechanism already built in `coop.py`; all-ready triggers year advance |
| No facilitator auth means anyone can access admin controls | Could disrupt a live workshop if participants find the facilitator routes | Low | Use a simple facilitator token or route prefix; not critical for first demo |
| Event cards may overwhelm new players in standard mode | 3 cards per year with complex effects could confuse workshop participants | Low | Use tutorial mode for first-time demos; reduce card count in standard scenario if needed |

---

## Suggested Next Step

Review this report, then invoke `/plan` targeting GAP-01 + GAP-02 + GAP-03 + GAP-06 as a single sprint — these are small, tightly coupled fixes that unblock solo gameplay in under an hour. After verifying solo play works end-to-end, plan a second sprint for GAP-04 + GAP-05 (co-op fix + facilitator dashboard) to prepare for multiplayer workshop use.
