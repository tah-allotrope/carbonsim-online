---
title: "Climate Mayor — Single-Player Narrative Tycoon"
date: "2026-04-30"
status: "draft"
request: "Take the Climate Mayor idea from idea markdown and create a multiphase implementation plan"
plan_type: "multi-phase"
research_inputs:
  - "research/2026-04-26_carbon-game-ideas.md"
---

# Plan: Climate Mayor — Single-Player Narrative Tycoon

## Objective

Build a single-player, save/resume narrative game where the player manages a Vietnamese province's industrial portfolio across 10-20 virtual years, making abatement, trading, and investment decisions to hit Drawdown without going bankrupt. The game reuses the existing `engine.py` compliance math (2,265 lines, 30+ pure-Python functions over a state dict, 92 passing tests) and wraps it in a new FastAPI backend with persistent state and a modern web frontend. This extends CarbonSim Online from a facilitator-led workshop tool to a self-directed experience for lay public and policy makers.

## Context Snapshot

- **Current state:** CarbonSim Online is a live multiplayer workshop simulation running on oTree. The engine (`platform/carbonsim_phase12/engine.py`) is fully decoupled from oTree — all 30+ public functions operate on a `state: dict` with no oTree imports. The engine includes scenario packs (`vietnam_pilot`, `high_pressure`), a shock system (4 shock types: `emissions_spike`, `allowance_withdrawal`, `cost_shock`, `offset_supply_change`), bot heuristics (`run_bot_turns` with configurable strategies), and comprehensive analytics/replay/export functions. 92 tests pass independently of oTree.
- **Desired state:** A standalone web application where a solo player can start a new game (selecting a province and difficulty), play through year-by-year cycles with event cards and narrative beats, save/resume sessions, and share end-of-run summaries. NPC companies run on existing bot heuristics. The original oTree workshop mode remains untouched.
- **Key repo surfaces:**
  - `platform/carbonsim_phase12/engine.py` — core compliance engine to extract and extend
  - `platform/carbonsim_phase12/engine.py:30-117` — `SCENARIO_PACKS` dict (company libraries, abatement catalogs, allocation factors)
  - `platform/carbonsim_phase12/engine.py:384-491` — `create_initial_state()` (scenario initialization, company setup, bot injection)
  - `platform/carbonsim_phase12/engine.py:1741-1838` — `apply_shock()` (4 shock types — becomes event-card payload system)
  - `platform/carbonsim_phase12/engine.py:1841-1951` — `run_bot_turns()` (3 bot strategies — becomes NPC behavior)
  - `platform/carbonsim_phase12/engine.py:1224-1262` — `build_session_replay()` (adapt for end-of-run summary)
  - `platform/carbonsim_phase12/engine.py:1529-1605` — `build_session_summary()` (adapt for shareable score card)
  - `platform/tests/test_engine.py` — existing test suite to preserve and extend
- **Out of scope:** Modifying the existing oTree workshop mode. Mobile-native apps. Multiplayer co-op (deferred to Phase 6). Internationalization beyond English. User authentication beyond simple session tokens.

## Research Inputs

- `research/2026-04-26_carbon-game-ideas.md` — Idea 1 (Climate Mayor) defines the pitch, audience, core loop, and reuse map. Key findings incorporated: (1) the engine's state-dict pattern enables direct reuse without oTree; (2) Daybreak's tag/combo mechanics are the design lineage for the event-card system; (3) peer-reviewed literature says to target engagement and conceptual learning, not attitude shift (IOP systematic review); (4) the suggested 5-phase breakdown is adopted with refinements from codebase analysis; (5) a 6th co-op phase is deferred but architecturally accommodated.

## Assumptions and Constraints

- **ASM-001:** The engine remains backward-compatible — extraction creates a new importable package without breaking the existing oTree app's `from .engine import ...` pattern.
- **ASM-002:** The game targets 10-20 virtual years per playthrough (vs. the current 3-year workshop sessions), requiring `num_years` scaling and new allocation factor curves.
- **ASM-003:** Event cards are the primary intrinsic-motivation mechanism; they map to the existing shock system plus new card types (technology unlocks, political events, FDI proposals, CBAM threats).
- **ASM-004:** NPC companies use the existing `run_bot_turns()` with strategy variants. The player controls one company; 2-5 NPCs provide the market.
- **CON-001:** No budget for commercial game art — UI uses a clean data-dashboard aesthetic with lightweight illustrations (open-source or AI-generated).
- **CON-002:** Backend must support save/resume across browser sessions — requires persistent storage (SQLite for MVP, upgradeable to PostgreSQL).
- **DEC-001:** FastAPI for the backend API layer (lightweight, async, good Python ecosystem fit). Next.js or SvelteKit for the frontend (decision deferred to Phase 4 — either works).
- **DEC-002:** The engine package is extracted in-repo as `carbonsim_engine/` rather than published to PyPI (simpler for now; PyPI is a future option).

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Extract engine to standalone package | None | `carbonsim_engine/` package, tests green, oTree app unchanged |
| PHASE-02 | Design and implement event-card system | PHASE-01 | Event-card schema, 50-card starter deck, card-draw + resolution engine |
| PHASE-03 | Solo session backend with persistent state | PHASE-01 | FastAPI app, SQLite persistence, save/load/resume API, NPC orchestration |
| PHASE-04 | Frontend with year-cycle UI and end-of-run summary | PHASE-02, PHASE-03 | Playable web app, year-cycle interaction, shareable summary |
| PHASE-05 | Playtest, balance, and content expansion | PHASE-04 | Balanced difficulty curves, 20+ additional cards, tutorial flow |
| PHASE-06 | Co-op mode (2-4 players) | PHASE-05 | WebSocket multiplayer, shared province, role selection |

## Detailed Phases

### PHASE-01 — Engine Extraction

**Goal**
Extract `engine.py` and its test suite into a standalone `carbonsim_engine/` Python package within the repo. The oTree app continues to import from the package. No functional changes to the engine — only structural reorganization.

**Tasks**
- [ ] TASK-01-01: Create `carbonsim_engine/` directory at repo root with `__init__.py`, `engine.py` (moved), `scenarios.py` (extracted `SCENARIO_PACKS`), and `constants.py` (extracted constants/defaults).
- [ ] TASK-01-02: Create `carbonsim_engine/pyproject.toml` with package metadata, Python >=3.10 requirement, and no external dependencies (the engine is pure stdlib).
- [ ] TASK-01-03: Move `platform/tests/test_engine.py` to `carbonsim_engine/tests/test_engine.py`. Update imports to `from carbonsim_engine.engine import ...`.
- [ ] TASK-01-04: Update `platform/carbonsim_phase12/__init__.py` to import from `carbonsim_engine` instead of `.engine`. Verify all existing oTree function calls resolve.
- [ ] TASK-01-05: Run the full test suite (`pytest carbonsim_engine/tests/ platform/tests/`) and confirm all 92+ tests pass.
- [ ] TASK-01-06: Add a `carbonsim_engine/solo.py` stub module with a `create_solo_game()` function signature that wraps `create_initial_state()` with solo-mode defaults (1 human + N bots, extended year count). No implementation yet — just the interface contract.

**Files / Surfaces**
- `carbonsim_engine/__init__.py` — new package root; re-exports public API
- `carbonsim_engine/engine.py` — moved from `platform/carbonsim_phase12/engine.py`
- `carbonsim_engine/scenarios.py` — extracted `SCENARIO_PACKS` dict
- `carbonsim_engine/constants.py` — extracted `DEFAULT_*` constants and `PHASE_*` constants
- `carbonsim_engine/solo.py` — new stub for solo-mode wrappers
- `platform/carbonsim_phase12/__init__.py` — updated imports
- `platform/carbonsim_phase12/engine.py` — replaced with re-export shim for backward compat

**Dependencies**
- None

**Exit Criteria**
- [ ] `pytest carbonsim_engine/tests/` passes all existing engine tests
- [ ] `pytest platform/tests/` passes all existing deployment/integration tests
- [ ] `from carbonsim_engine import create_initial_state, apply_company_decision, run_bot_turns, apply_shock` works from a standalone Python script
- [ ] The oTree app starts and runs a workshop session without errors

**Phase Risks**
- **RISK-01-01:** Circular import between shim and package. Mitigation: the shim file at `platform/carbonsim_phase12/engine.py` does only `from carbonsim_engine.engine import *` — no logic.
- **RISK-01-02:** Relative import assumptions in test fixtures. Mitigation: run tests from repo root with package installed in editable mode (`pip install -e carbonsim_engine/`).

---

### PHASE-02 — Event-Card System

**Goal**
Design and build a content-driven event-card system that injects narrative variety into each virtual year. Cards map to engine actions (shocks, abatement unlocks, market shifts, political events) and are the primary source of replayability and intrinsic motivation.

**Tasks**
- [ ] TASK-02-01: Define the event-card JSON schema. Each card has: `card_id`, `title`, `description` (narrative text), `category` (crisis | opportunity | policy | market), `effect_type` (maps to engine action), `effect_params` (arguments for the engine action), `prerequisites` (year range, sector, prior cards), `weight` (draw probability), `choices` (optional player choices with different outcomes).
- [ ] TASK-02-02: Implement `carbonsim_engine/cards.py` with: `CardDeck` class (loads cards from JSON, supports weighted random draw with prerequisites filtering), `draw_cards(state, count=3, rng=None)` function, `resolve_card(state, card, choice=None)` function that dispatches to engine actions.
- [ ] TASK-02-03: Extend `apply_shock()` with new shock types needed by cards: `tech_unlock` (adds a new abatement measure to a sector's catalog mid-game), `fdi_proposal` (adds a new company/facility to the player's portfolio), `cbam_threat` (increases export cost for specific sectors), `election_pressure` (modifies allocation factors for next year).
- [ ] TASK-02-04: Write the 50-card starter deck as `carbonsim_engine/data/starter_deck.json`. Distribution: ~12 crisis cards, ~12 opportunity cards, ~12 policy cards, ~14 market cards. Each card tested against the schema.
- [ ] TASK-02-05: Write unit tests for card draw (deterministic with seeded RNG), prerequisite filtering, card resolution (each effect type), and deck exhaustion/reshuffle behavior.
- [ ] TASK-02-06: Write a card validation CLI script (`carbonsim_engine/scripts/validate_deck.py`) that loads a deck JSON, validates schema, checks all `effect_type` values map to implemented resolvers, and reports coverage of categories/year ranges.

**Files / Surfaces**
- `carbonsim_engine/cards.py` — card system implementation
- `carbonsim_engine/data/starter_deck.json` — 50-card starter deck
- `carbonsim_engine/data/card_schema.json` — JSON Schema for card validation
- `carbonsim_engine/engine.py` — extended `apply_shock()` with new shock types
- `carbonsim_engine/scripts/validate_deck.py` — deck validation CLI
- `carbonsim_engine/tests/test_cards.py` — card system tests

**Dependencies**
- PHASE-01 (engine must be an importable package)

**Exit Criteria**
- [ ] `pytest carbonsim_engine/tests/test_cards.py` passes with 100% of card effect types covered
- [ ] `python -m carbonsim_engine.scripts.validate_deck` reports 50 valid cards, 0 errors
- [ ] A scripted 20-year solo game run (using `create_initial_state` + loop of `draw_cards` → `resolve_card` → `run_bot_turns` → `advance_state`) completes without errors and produces distinct card sequences across 3 different seeds
- [ ] Existing engine tests still pass (no regressions from new shock types)

**Phase Risks**
- **RISK-02-01:** Card balance — some cards may be too powerful or trivial. Mitigation: this is a content problem solved in Phase 5 (playtest). Phase 2 aims for mechanical correctness, not balance.
- **RISK-02-02:** Choice-based cards add branching complexity. Mitigation: limit Phase 2 choices to binary (accept/reject) with deterministic outcomes; richer branching in Phase 5.

---

### PHASE-03 — Solo Session Backend

**Goal**
Build a FastAPI application that wraps the engine and card system into a stateful, save/resume solo game API. The API manages game lifecycle (new game, advance year, make decisions, save, load, resume) and orchestrates NPC turns automatically.

**Tasks**
- [ ] TASK-03-01: Create `mayor_api/` directory with FastAPI app structure: `main.py` (app factory), `routes/game.py` (game CRUD + actions), `routes/health.py`, `models.py` (Pydantic request/response models), `db.py` (SQLite via SQLAlchemy or raw sqlite3).
- [ ] TASK-03-02: Implement SQLite persistence layer. Tables: `games` (game_id, player_name, state_json, created_at, updated_at, status, current_year, total_years), `game_saves` (save_id, game_id, save_name, state_json, saved_at). State is stored as compressed JSON blob.
- [ ] TASK-03-03: Implement game lifecycle API endpoints:
  - `POST /api/games` — create new game (params: player_name, province_name, difficulty, num_years)
  - `GET /api/games/{game_id}` — get current game state (player snapshot, not raw state)
  - `POST /api/games/{game_id}/advance-year` — trigger year start, draw event cards, return cards to player
  - `POST /api/games/{game_id}/resolve-card` — player resolves a drawn card (with optional choice)
  - `POST /api/games/{game_id}/decision` — player makes abatement/trading/offset decision
  - `POST /api/games/{game_id}/end-year` — close current year, run NPC turns, calculate compliance, return scorecard
  - `POST /api/games/{game_id}/save` — save current state
  - `GET /api/games/{game_id}/saves` — list saves
  - `POST /api/games/{game_id}/load/{save_id}` — load a save
  - `GET /api/games/{game_id}/summary` — end-of-run summary (reuses `build_session_summary`)
- [ ] TASK-03-04: Implement `carbonsim_engine/solo.py` fully: `create_solo_game()` that calls `create_initial_state(participant_count=1, bot_count=N, num_years=M)` with solo-mode scenario packs. Add new scenario packs for solo mode with 10/15/20-year allocation factor curves and expanded company libraries.
- [ ] TASK-03-05: Implement NPC orchestration in the year-end flow: after the player submits decisions, the backend calls `run_bot_turns()` for all NPC companies, then `advance_state()` to close the year. NPCs act deterministically based on their strategy.
- [ ] TASK-03-06: Add solo-mode scenario packs to `carbonsim_engine/scenarios.py`: `solo_easy` (20 years, generous allocation, low penalty), `solo_standard` (15 years, moderate), `solo_hard` (10 years, aggressive cap decline, high penalty). Each with 5-8 companies in the library.
- [ ] TASK-03-07: Write API integration tests using `httpx.AsyncClient` + `pytest-asyncio`. Cover: create game, play through 3 years with decisions and card resolutions, save/load round-trip, end-of-run summary generation.
- [ ] TASK-03-08: Add CORS middleware configured for the frontend origin. Add rate limiting middleware.

**Files / Surfaces**
- `mayor_api/main.py` — FastAPI app factory
- `mayor_api/routes/game.py` — game endpoints
- `mayor_api/models.py` — Pydantic models for API I/O
- `mayor_api/db.py` — SQLite persistence
- `carbonsim_engine/solo.py` — solo-mode game creation
- `carbonsim_engine/scenarios.py` — new solo scenario packs
- `mayor_api/tests/` — API integration tests

**Dependencies**
- PHASE-01 (importable engine)
- PHASE-02 (card system for `advance-year` endpoint, but can stub cards initially)

**Exit Criteria**
- [ ] `pytest mayor_api/tests/` passes all integration tests
- [ ] A full 15-year game can be played via `curl`/httpie against the running API: create → (advance-year → resolve-cards → decision → end-year) × 15 → summary
- [ ] Save/load round-trip preserves game state exactly (JSON diff is empty)
- [ ] API responds in <200ms for all endpoints on a single-user local server
- [ ] The API serves the end-of-run summary in the format needed for the frontend share card

**Phase Risks**
- **RISK-03-01:** State blob size grows large over 20 years with full audit logs. Mitigation: compress JSON with zlib before SQLite storage; optionally trim audit_log to last 3 years in the active state while archiving full log separately.
- **RISK-03-02:** Year-end NPC orchestration may take >1s for 8 companies. Mitigation: profile `run_bot_turns()` under solo load; optimize inner loops if needed (the current implementation breaks after first abatement per company, so it's already bounded).

---

### PHASE-04 — Frontend: Year-Cycle UI and End-of-Run Summary

**Goal**
Build a web frontend that delivers the Climate Mayor experience: province dashboard, year-cycle interaction (review → cards → decisions → scorecard), and a shareable end-of-run summary. The UI should feel like a polished data dashboard with narrative flavor, not a spreadsheet.

**Tasks**
- [ ] TASK-04-01: Initialize frontend project in `mayor_web/` using Next.js (App Router) or SvelteKit. Configure TypeScript, Tailwind CSS, and API client pointing at the FastAPI backend.
- [ ] TASK-04-02: Build the **New Game** screen: province name input, difficulty selector (Easy/Standard/Hard with descriptions), "Start Game" button. Calls `POST /api/games`.
- [ ] TASK-04-03: Build the **Province Dashboard** — the main game screen. Sections: province stats (total emissions, budget, compliance status), facility cards (one per company in portfolio), year indicator with progress bar, action buttons (Advance Year, Save Game). Updates via `GET /api/games/{game_id}`.
- [ ] TASK-04-04: Build the **Event Card** modal/panel. When `advance-year` returns drawn cards: display each card with title, narrative description, category icon, and choice buttons (if applicable). Player resolves each card before proceeding. Calls `POST /api/games/{game_id}/resolve-card` per card.
- [ ] TASK-04-05: Build the **Decision Phase** UI. Show the player's company with: compliance gap indicator, abatement menu (activate buttons with cost/impact), offset purchase slider, auction bid form (if auctions are open). Each action calls `POST /api/games/{game_id}/decision`. Show running totals updating in real-time.
- [ ] TASK-04-06: Build the **Year-End Scorecard** screen. After `end-year`: show compliance result (pass/fail/penalty), cost breakdown (abatement + offsets + auctions + penalties), NPC comparison table, cumulative emissions chart, narrative beat text. "Continue to Next Year" button.
- [ ] TASK-04-07: Build the **End-of-Run Summary** screen. After final year: overall score (composite of financial health + emissions reduction + compliance record), province trajectory chart (20 years of emissions vs. cap), comparison to NPC performance, achievement badges, and a "Share" button that generates an Open Graph image / copy-paste text summary.
- [ ] TASK-04-08: Build the **Save/Load** UI. Save modal with name input. Load screen showing saved games with timestamps and year progress. Delete save confirmation.
- [ ] TASK-04-09: Implement client-side state management for in-flight game state (React Context or Svelte stores). Handle API errors with user-friendly messages and retry.
- [ ] TASK-04-10: Add responsive layout for tablet/desktop (mobile is a stretch goal, not required for MVP).

**Files / Surfaces**
- `mayor_web/` — entire frontend project
- `mayor_web/src/app/` or `mayor_web/src/routes/` — page components
- `mayor_web/src/components/` — reusable UI components (FacilityCard, EventCard, ScoreCard, etc.)
- `mayor_web/src/lib/api.ts` — API client wrapper
- `mayor_web/public/` — static assets, OG image template

**Dependencies**
- PHASE-02 (card data drives the Event Card UI)
- PHASE-03 (all UI interactions go through the API)

**Exit Criteria**
- [ ] A complete 10-year game can be played in the browser from new-game to end-of-run summary without errors
- [ ] Event cards display correctly with narrative text and choices
- [ ] Save/load works across browser sessions (close tab, reopen, load game, continue)
- [ ] End-of-run share card generates a copyable text summary and/or downloadable image
- [ ] UI is responsive on screens >= 768px wide
- [ ] Lighthouse accessibility score >= 80

**Phase Risks**
- **RISK-04-01:** Frontend framework choice affects development speed. Mitigation: both Next.js and SvelteKit are viable; decide at task start based on team familiarity. The API contract is framework-agnostic.
- **RISK-04-02:** Year-cycle UX may feel tedious over 20 years. Mitigation: add a "fast-forward" mode in Phase 5 that auto-resolves years with default decisions. Phase 4 focuses on getting the full loop working.

---

### PHASE-05 — Playtest, Balance, and Content Expansion

**Goal**
Playtest the complete game loop, tune difficulty curves and card balance, add tutorial/onboarding, and expand the card deck. This is the phase where the game becomes *fun*, not just functional.

**Tasks**
- [ ] TASK-05-01: Run 10+ complete playthroughs across all three difficulty levels. Log: completion rate, average playtime per year, final score distribution, card frequency, and frustration points (years where the player has no meaningful choice).
- [ ] TASK-05-02: Tune allocation factor curves for solo scenario packs based on playtest data. Target: Easy should be completable by a first-time player; Hard should require strategic card play and market timing.
- [ ] TASK-05-03: Adjust card weights and prerequisites based on playtest data. Cards that never appear or always appear should be rebalanced. Cards with choices should have meaningfully different outcomes.
- [ ] TASK-05-04: Write 20+ additional event cards expanding coverage: renewable energy breakthroughs, international carbon border adjustments, provincial elections with policy platforms, natural disasters, supply chain disruptions, technology failures.
- [ ] TASK-05-05: Build a **Tutorial Flow** for first-time players: a guided 3-year mini-game with fixed cards and annotated UI that teaches compliance basics, abatement decisions, and offset purchasing before the full game begins.
- [ ] TASK-05-06: Add **achievement badges**: "Drawdown Pioneer" (hit net-zero), "Budget Hawk" (finish with >50% starting cash), "Clean Sweep" (zero penalties all game), "Market Maker" (win 10+ auction lots). Display on end-of-run summary.
- [ ] TASK-05-07: Add a **Year Fast-Forward** option: skip the card/decision UI and auto-resolve with conservative defaults (activate cheapest abatement, buy minimal offsets). Useful for experienced players who want to focus on specific years.
- [ ] TASK-05-08: Performance optimization: lazy-load event card images, prefetch next year's data, compress API responses.

**Files / Surfaces**
- `carbonsim_engine/data/starter_deck.json` — rebalanced card weights
- `carbonsim_engine/data/expansion_deck.json` — 20+ new cards
- `carbonsim_engine/scenarios.py` — retuned allocation factors and difficulty parameters
- `mayor_web/src/components/Tutorial.tsx` — tutorial flow
- `mayor_web/src/components/Achievements.tsx` — badge system

**Dependencies**
- PHASE-04 (playable game required for playtesting)

**Exit Criteria**
- [ ] 5 external playtesters (non-developers) complete at least one full game each without getting stuck
- [ ] Average completion time for a Standard 15-year game is 30-60 minutes
- [ ] All three difficulty levels are completable (Easy: >90% completion, Standard: >60%, Hard: >30%)
- [ ] Tutorial flow takes <5 minutes and playtesters report understanding the core mechanics afterward
- [ ] Card deck has 70+ cards with no dead cards (every card drawn at least once in 10 playthroughs)

**Phase Risks**
- **RISK-05-01:** Balance tuning is iterative and hard to predict timeline. Mitigation: set a time-box (2 weeks) and ship with "good enough" balance, plan a post-launch balance patch.
- **RISK-05-02:** External playtester recruitment. Mitigation: use the existing workshop network from `research/20250418_Final_20Report_EN.md` — participants who played the workshop version are ideal testers.

---

### PHASE-06 — Co-op Mode (2-4 Players)

**Goal**
Add cooperative multiplayer where 2-4 human players share a province, each controlling a subset of facilities, coordinating on shared resources (budget, allowance pool) and collectively pursuing Drawdown. This extends the solo architecture with WebSocket real-time sync.

**Tasks**
- [ ] TASK-06-01: Design co-op session model: shared province state, per-player facility assignment, shared budget with individual spending limits, collective compliance score.
- [ ] TASK-06-02: Add WebSocket support to FastAPI backend (`/ws/games/{game_id}`) for real-time state sync between players. Events: player_joined, year_started, card_drawn, decision_made, year_ended.
- [ ] TASK-06-03: Implement turn coordination: all players must submit decisions before year-end triggers. Add a ready-check mechanism and configurable decision timer.
- [ ] TASK-06-04: Add co-op-specific event cards that require inter-player negotiation (e.g., "Province budget cut — players must collectively reduce spending by 20%").
- [ ] TASK-06-05: Build lobby/invite UI: create co-op game → get invite link → share → players join → host starts.
- [ ] TASK-06-06: Update end-of-run summary for co-op: per-player contributions, collective score, MVP badge.
- [ ] TASK-06-07: Write integration tests for 2-player and 4-player co-op flows.

**Files / Surfaces**
- `mayor_api/routes/coop.py` — co-op game endpoints
- `mayor_api/ws.py` — WebSocket handler
- `carbonsim_engine/coop.py` — co-op state management
- `mayor_web/src/app/coop/` — co-op lobby and in-game UI

**Dependencies**
- PHASE-05 (balanced solo game is prerequisite for meaningful co-op)

**Exit Criteria**
- [ ] Two browser tabs can play a complete co-op game on the same machine
- [ ] State is consistent across all connected clients after every year-end
- [ ] A disconnected player can rejoin and resume from current state
- [ ] Co-op end-of-run summary shows per-player breakdown

**Phase Risks**
- **RISK-06-01:** WebSocket state sync complexity. Mitigation: the state-dict pattern means the server is the single source of truth — clients only send actions and receive snapshots, no client-side state merging.
- **RISK-06-02:** Player drop-off mid-game. Mitigation: dropped players' facilities auto-pilot via `run_bot_turns()` until they rejoin.

## Verification Strategy

- **TEST-001:** `pytest carbonsim_engine/tests/` — all engine + card tests pass on every phase commit. CI gate.
- **TEST-002:** `pytest mayor_api/tests/` — API integration tests covering full game lifecycle. CI gate from Phase 3 onward.
- **TEST-003:** Scripted 20-year playthrough via API (`mayor_api/tests/test_full_game.py`) — proves the complete loop works end-to-end without UI.
- **MANUAL-001:** Play a complete game in the browser after Phase 4. Verify: new game → 15 years of play → save/load mid-game → end-of-run summary → share card works.
- **MANUAL-002:** Phase 5 external playtesting with 5+ non-developer users. Collect completion rates, playtime, and qualitative feedback.
- **OBS-001:** API response time logging (middleware) — flag any endpoint consistently >500ms.
- **OBS-002:** Game completion funnel tracking — what year do players stop? How many save? How many share?

## Risks and Alternatives

- **RISK-001:** Scope creep from narrative content ambitions. Mitigation: Phase 2 ships with exactly 50 cards; Phase 5 adds 20 more. Card writing is explicitly bounded per phase.
- **RISK-002:** The 20-year game length may feel too long for casual players. Mitigation: Phase 5 adds year fast-forward; solo scenario packs include a 10-year "Hard" mode that's shorter but more intense.
- **RISK-003:** Engine performance at 20-year scale with 8 companies. Mitigation: profiled in Phase 3; the engine is O(companies × years) with small constants — unlikely to be an issue but measured.
- **ALT-001:** JS port of the engine instead of Python API. Rejected because: (a) 2,265 lines of Python with 92 tests is significant porting effort; (b) a Python backend enables save/resume and future co-op without duplicating state logic; (c) the engine is the hardest part to get right and it already works.
- **ALT-002:** Build on oTree instead of FastAPI. Rejected because: oTree's session model assumes synchronized multiplayer with a facilitator — retrofitting save/resume, solo play, and async year cycles would fight the framework rather than leverage it.

## Grill Me

1. **Q-001:** Should the player control a single company or an entire portfolio of facilities?
   - **Recommended default:** Single company (consistent with the existing engine's per-company decision model). The province framing is narrative — the player is "Director of Industry" but makes decisions for one flagship facility, while NPCs represent other provincial industries.
   - **Why this matters:** Portfolio control requires a new multi-company decision aggregation layer on top of the engine. Single company reuses the existing `apply_company_decision()` interface unchanged.
   - **If answered differently:** If portfolio, Phase 3 needs a `portfolio_decision()` wrapper that fans out to multiple `apply_company_decision()` calls, and the frontend needs a facility-switching UI.

2. **Q-002:** What is the target deployment platform for the MVP?
   - **Recommended default:** Single-server deployment (e.g., Railway, Render, or a VPS) with FastAPI serving both API and static frontend assets.
   - **Why this matters:** Affects Phase 3 architecture (SQLite works for single-server; multi-server needs PostgreSQL) and Phase 4 build pipeline.
   - **If answered differently:** If expecting >100 concurrent users, switch to PostgreSQL in Phase 3 and add a CDN for frontend assets.

3. **Q-003:** Should the event-card narrative be Vietnam-specific (matching the existing scenario packs) or geographically abstract?
   - **Recommended default:** Vietnam-specific — the existing scenario packs, company names, and research brief are all Vietnam-contextualized. This gives the narrative authenticity and educational specificity.
   - **Why this matters:** Card content in Phase 2 references real policy contexts (Vietnam's pilot ETS, CBAM exposure, FDI patterns). Abstract cards would lose this grounding.
   - **If answered differently:** If abstract, the 50-card deck needs generic industry/policy language and the scenario packs need geographical neutralization.

4. **Q-004:** Is there a measurement plan for engagement and learning outcomes, per the research brief's recommendation?
   - **Recommended default:** Add lightweight telemetry in Phase 4 (game completion rate, playtime per year, share rate) and a voluntary post-game survey in Phase 5. No formal RCT or pre/post assessment for MVP.
   - **Why this matters:** The research literature (IOP systematic review, ScienceDirect 2026) emphasizes that most climate-game studies lack rigorous evaluation. Even basic telemetry positions the project ahead of the field.
   - **If answered differently:** If formal evaluation is wanted, Phase 5 needs a pre/post knowledge assessment instrument and IRB-equivalent ethics review, adding 4-6 weeks.

## Suggested Next Step

Answer the Grill Me questions (especially Q-001 on single vs. portfolio control — it affects engine reuse significantly). Then begin PHASE-01 (engine extraction), which is unblocked and has no open questions.
