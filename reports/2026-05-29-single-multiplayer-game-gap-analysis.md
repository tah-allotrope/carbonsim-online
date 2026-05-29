# Gap Analysis: Focused Single + Multiplayer CarbonSim Game

**Date:** 2026-05-29
**Scope:** Refocus the repository onto **one** product — a visually polished single-player and multiplayer carbon-market game built on the CarbonSim engine — by removing the redundant second stack, updating the now-misleading context/docs files, and reorganizing the file tree for clarity.
**Status:** Draft for Review

---

## Executive Summary

The repo carries **two parallel product stacks** built on a shared engine: the original oTree workshop platform (`platform/`, now reduced to a 1-line engine shim) and the active "Climate Mayor" game (`carbonsim_engine` + `mayor_api` FastAPI + `mayor_web` static frontend). All momentum for the last ~6 weeks is on the game stack, yet the top-level context files (`README.md`, `AGENTS.md`, `plans/project-plan.md`) still describe the oTree platform as *the* product and mandate the oTree stack — actively misdirecting any future agent. The engine logic, gameplay loop, and a working solo/co-op flow are genuinely strong assets; the gaps are **strategic clarity, redundancy removal, documentation truth, and a deliberate visual layer** — not missing game logic. Recommended path: declare the game stack canonical, archive/delete the oTree stack and stale plans, rewrite the context files around the game, reorganize the tree, then invest in the visual + multiplayer polish that the "improved upon CarbonSim" goal requires.

---

## Current Capabilities (What We Have)

| Capability | Status | Key Surfaces |
|---|---|---|
| Core ETS engine (allocation, abatement, offsets, banking, surrender, penalties) | Mature | `carbonsim_engine/engine.py` (1,943 LOC) |
| Auction + bilateral trading + bots + shocks | Working | `carbonsim_engine/engine.py:256-504,1323-1551` |
| Event-card system (50+ card decks) | Mature | `carbonsim_engine/cards.py`, `carbonsim_engine/data/*.json` |
| Solo game (difficulty tiers, scenarios) | Working | `carbonsim_engine/solo.py`, `carbonsim_engine/scenarios.py`, `mayor_api/routes/game.py` |
| Co-op / multiplayer (create/join/ready/WebSocket) | Partial — scaffold | `carbonsim_engine/coop.py`, `mayor_api/routes/coop.py`, `mayor_api/ws.py`, `mayor_web/coop.html` |
| Game frontend (DOM/CSS, animations, audio, XP) | Working — modest visuals | `mayor_web/` (3,287 LOC HTML/JS/CSS) |
| Tutorial, achievements, fast-forward, playtest harness | Working | `carbonsim_engine/tutorial.py`, `achievements.py`, `playtest.py` |
| oTree workshop platform (rooms, facilitator, exports) | **Legacy / orphaned** | `platform/` (21 files); `platform/carbonsim_phase12/engine.py` is now `from carbonsim_engine.engine import *` |
| Engine test suite | Working (with 2 known failures) | `carbonsim_engine/tests/`, `mayor_api/tests/test_api.py` |
| Context / product docs | **Stale — describe oTree platform** | `README.md`, `AGENTS.md`, `plans/project-plan.md`, `activeContext.md` |

---

## Target State

> One clearly-defined product: a **single-player and multiplayer carbon-market game** on the CarbonSim engine, with **visuals that are a deliberate step up** from the current DOM-form UI. The repository should contain exactly one runnable game stack, context/docs that accurately describe that stack and direct future work, and a clean, conventional file layout. No second abandoned stack, no contradictory product docs, no duplicate worktrees or obsolete artifacts.

---

## Gap Analysis

### GAP-01: Two Parallel Product Stacks (oTree platform vs. Climate Mayor game)

**Severity:** CRITICAL — A split codebase blocks "focus on a single game." Every future change risks touching the wrong stack, and the engine is being pulled in two directions.

**Current state:**
- `platform/` is the original oTree workshop product (21 tracked files: `settings.py`, `carbonsim_phase12/` pages, `deployment.py`, Docker/Caddy/fly artifacts, `tests/`). Its engine has already been hollowed out — `platform/carbonsim_phase12/engine.py` is a single line: `from carbonsim_engine.engine import *`.
- The game stack — `carbonsim_engine/` + `mayor_api/` (FastAPI) + `mayor_web/` (static) — is where 100% of recent commits land (`c9d6798`, `0809cba`, `4cc3cac`, etc.).
- Dependency direction is clean and severable: `platform/` imports `carbonsim_engine`, but **nothing in `mayor_api`/`mayor_web`/`carbonsim_engine` imports `platform`** (verified by grep). The game stack does not need the platform at all.

**What's needed:**
- A product decision: the game stack is canonical (strongly implied by momentum and the user's stated goal).
- Archive or delete `platform/` and its deployment artifacts (`Dockerfile`, `Caddyfile`, `fly.toml`, `docker-compose.yml`, `Procfile`, `settings.py`, `otree_server.log`) — or move to an `archive/otree-platform/` if any workshop multiplayer logic is worth porting.
- Remove `oTree` from `platform/requirements.txt` dependency surface; converge on one requirements/pyproject.

**Existing assets to reuse:**
- `platform/carbonsim_phase12/deployment.py`, `FacilitatorPanel.html`, `WorkshopHub.html` contain workshop multiplayer/facilitator patterns that may inform the game's multiplayer host UI (see GAP-05) before deletion.
- Deployment artifacts (Docker/fly/Caddy) can be adapted to deploy the FastAPI game rather than oTree.

**Effort estimate:** 1 plan (1-2 phases): decision + extraction of anything worth keeping, then removal and dependency cleanup.

---

### GAP-02: Context & Product Docs Describe the Abandoned Stack

**Severity:** CRITICAL — These files are the first thing any agent (and `AGENTS.md` is explicitly an agent contract) reads. They currently point the entire effort at the wrong product and stack.

**Current state:**
- `README.md` "What is implemented" lists oTree Phases 1-10 only; says "built on oTree"; "Project layout" references `plan/` (which doesn't exist — the dir is `plans/`). Zero mention of Climate Mayor, `mayor_api`, or `mayor_web`.
- `AGENTS.md` mandates `Default Stack: oTree`, says "Do not move to Empirica, Colyseus, or a custom real-time stack," and frames the mission as "not a generic carbon game" — all in direct conflict with the FastAPI + custom-frontend game that now exists and the user's "build a game" goal.
- `plans/project-plan.md` is the oTree workshop roadmap ("V1 uses oTree unless a concrete blocker is found").
- `activeContext.md` is game-relevant but frozen mid-task on Phase 5/6 ("Preparing commit and push") — needs to reflect the new consolidation goal.

**What's needed:**
- Rewrite `README.md` around the game: what it is, the `carbonsim_engine` + `mayor_api` + `mayor_web` architecture, how to run the FastAPI server and open the web client, how to run tests.
- Rewrite `AGENTS.md` to declare the game stack canonical, set the real stack (Python/FastAPI engine + static/JS frontend + WebSocket multiplayer), and update guardrails (visual polish is now in-scope; oTree is retired).
- Replace/retire `plans/project-plan.md` with a game-focused roadmap; reset `activeContext.md` to the consolidation effort.

**Existing assets to reuse:**
- The architecture principles in `AGENTS.md` (server-authoritative state, deterministic year flow, auditability) are sound and transfer directly to the game — keep the principles, swap the stack/product framing.
- `reports/2026-05-23-climate-mayor-workshop-demo-gap-analysis.md` already documents the game's real surfaces and can seed the new README's capability list.

**Effort estimate:** 1 plan (1 phase): three doc rewrites + one roadmap replacement.

---

### GAP-03: Engine Mixes Game-Core and Orphaned Workshop-Platform Logic

**Severity:** HIGH — `carbonsim_engine/engine.py` (1,943 LOC) serves both stacks. Once oTree is gone, a chunk of multi-company auction/facilitator/replay code may be dead or only partially used by the game, making the core harder to evolve and visually re-skin.

**Current state:**
- The engine bundles single-player/co-op game needs (year cycle, abatement, offsets, cards via `solo.py`/`coop.py`/`cards.py`) **and** workshop-platform constructs: `build_facilitator_snapshot()`, `build_session_analytics()`, `export_session_data()`, multi-company auctions, bot strategies, replay timelines (`engine.py:815-1180,1456-1551`).
- The prior gap analysis flagged these as "exists in engine, no route" — i.e., built for the workshop product, not yet surfaced in the game. After GAP-01 some become candidates for either game adoption (multiplayer) or removal.
- Two engine tests are known-failing and carried as out-of-scope debt (`test_start_simulation_initializes_year_one_allocations`, `test_trade_transfers_allowances_and_cash`, per `activeContext.md:56-57,87-90`).

**What's needed:**
- Inventory engine surface area against actual game usage (`mayor_api` + `mayor_web` callers); mark each function game-used / multiplayer-candidate / dead.
- Decide: keep auction/trading/facilitator logic for the multiplayer game, or trim to the game's real loop. Fix or delete the 2 failing tests.
- Optionally split the monolith (e.g., `engine_core.py`, `market.py`, `analytics.py`) for maintainability before the visual layer is built on top.

**Existing assets to reuse:**
- `mayor_api/tests/test_api.py` + `carbonsim_engine/tests/` define the contract that must keep passing through any refactor.
- `playtest.py` gives a deterministic harness to confirm balance is unchanged after trimming.

**Effort estimate:** 1 plan (2 phases): usage inventory + test fix (1), optional modularization (1).

---

### GAP-04: Visual Layer Is DOM/CSS Forms, Not "Improved Upon CarbonSim"

**Severity:** HIGH — The explicit goal is "decent visuals improved upon CarbonSim." Current frontend is functional DOM tables/buttons with CSS animations and audio; there is no rendering/scene layer, cohesive art direction, or reusable component system to build a step-change on.

**Current state:**
- `mayor_web/` is hand-rolled static HTML + vanilla JS (`api.js`, `effects.js`, `audio.js`, `progression.js`, `shortcuts.js`) + `css/style.css` + `animations.css` (3,287 LOC total). The Climate Mayor gamification pass (`c9d6798`) added game-feel but within the DOM-form paradigm.
- No build tooling, component framework, canvas/WebGL, or design-token system. Adding richer visuals (a city/map view, animated market, charts) means either a heavier DOM approach or introducing a frontend stack.

**What's needed:**
- A visual direction decision: (a) stay vanilla but add a design system + canvas/SVG scene for the "mayor city" metaphor, or (b) adopt a lightweight framework/build (e.g., Vite + a component lib, or a canvas game lib) — note this requires updating `AGENTS.md` guardrails (GAP-02) which currently forbid "heavy custom front-end."
- A small design language: tokens (color/spacing/type), reusable components, consistent iconography, and one signature visual (animated compliance gauge, city skyline reacting to emissions, or live market chart).
- Keep the static-served + FastAPI delivery model unless a build step is justified.

**Existing assets to reuse:**
- `mayor_web/css/animations.css`, `js/effects.js`, `js/audio.js`, `js/progression.js` already provide game-feel primitives to build the design system around.
- `engine.py` already emits rich snapshots (emissions, gap, market path, replay data) — the data needed to drive richer visuals already exists.

**Effort estimate:** 1 plan (3+ phases): direction + design tokens (1), signature visual + component refactor (1), polish/responsive (1).

---

### GAP-05: Multiplayer Is a Scaffold; the Mature Multiplayer Lives in the Doomed Stack

**Severity:** HIGH — "Single AND multiplayer" is a core target, but the game's co-op is explicitly "an early but working scaffold" (`activeContext.md:86`), while the mature room/facilitator/auction multiplayer sits in the oTree `platform/` being retired (GAP-01).

**Current state:**
- Game multiplayer = `coop.py` + `routes/coop.py` + `ws.py` + `coop.html`: create/join, ready-check, WebSocket snapshot broadcast. Per the prior gap report it lacks lobby, shareable room codes, host/facilitator controls, year-advance cycle, and reconnection (`reports/2026-05-23-...md` GAP-04).
- oTree `platform/` *had* mature rooms, synchronized timing, facilitator panel, and exports — but that's the stack being removed.

**What's needed:**
- Decide the multiplayer shape for the game (co-op shared city vs. competitive market vs. facilitator-led) — one shape, not three.
- Build it out in the game stack: lobby + room code, host controls, server-authoritative year cycle over WebSocket, reconnection/state recovery.
- Salvage relevant patterns from `platform/` before deletion (see GAP-01).

**Existing assets to reuse:**
- `mayor_api/ws.py` connection manager + `coop.py` participant/ready/snapshot logic are the working foundation.
- Engine auction/trade/bot logic (`engine.py`) supports a competitive multiplayer market if that's the chosen shape.
- `platform/carbonsim_phase12/FacilitatorPanel.html` / `deployment.py` as a reference for host controls.

**Effort estimate:** 1 plan (2-3 phases): multiplayer shape decision + lobby/room (1), server-authoritative cycle + host controls (1), reconnection/polish (1). Depends on GAP-01.

---

### GAP-06: Repository Clutter & Non-Standard Layout

**Severity:** MEDIUM — Limits the "files reorg" goal and slows navigation, but doesn't block functionality.

**Current state:**
- Root sprawl: three sibling top-level code dirs (`carbonsim_engine/`, `mayor_api/`, `mayor_web/`) plus the legacy `platform/`, with no `src/`/`server/`/`web/` grouping.
- `.claude/worktrees/hardcore-wu-70aa3d/` is a **2.3 MB full duplicate** of the entire repo (its own `AGENTS.md`, `research/`, `plans/`, `README.md`) — stale worktree clutter (untracked).
- `reports/` holds 25 files, mostly **obsolete oTree phase reports** (`2026-04-17/19/24-phase-*.html`) irrelevant to the game; plus `phase_report.html`/`.md` duplicates.
- `plans/` mixes products: oTree (`project-plan.md`, `2026-04-25-free-tier-deployment`, `2026-04-26-vietnam-market-testing`), a *different* game (`2026-04-29-carbon-crunch-daily`), and Climate Mayor plans.
- Doc/path drift: `README.md` references `plan/` but the dir is `plans/`; `carbonsim_engine.egg-info/` build artifact present on disk.
- `db.sqlite3` (root) and `mayor_api/mayor.db` exist on disk (gitignore covers them, but they signal a runtime-file hygiene need).

**What's needed:**
- Adopt a conventional layout, e.g. `engine/` (or keep `carbonsim_engine`), `server/` (= `mayor_api`), `web/` (= `mayor_web`), `docs/`, `archive/`, `plans/`, `research/`.
- Delete the `.claude/worktrees/` duplicate; move obsolete oTree reports/plans to `archive/` or delete; fix the `plan/`→`plans/` doc reference.
- Establish a `docs/reports/` vs active-`reports/` convention (the `/gap` and `/report` skills already prefer `reports/`).

**Existing assets to reuse:**
- `.gitignore` is already mostly correct (ignores `__pycache__`, `*.egg-info`, dbs, logs) — extend it rather than rewrite.

**Effort estimate:** 1 plan (1-2 phases): tree reorg + import-path updates (1), archive/delete obsolete docs (1).

---

## Second-Tier Gaps

| Gap | Severity | Summary | Existing Assets |
|---|---|---|---|
| GAP-07 | MEDIUM | Divergent product concepts in `plans/` ("Carbon Crunch Daily" is a separate game; Vietnam-testing/workshop plans target the retired product) — pick one product vision and archive the rest | `plans/2026-04-29-carbon-crunch-daily-plan.md`, `research/2026-04-26_carbon-game-ideas.md` |
| GAP-08 | MEDIUM | Fragmented tests across `platform/tests`, `carbonsim_engine/tests`, `mayor_api/tests` with 2 known failures and weak API assertions (prior GAP-06) — consolidate into one runnable suite after stack removal | existing test files |
| GAP-09 | MEDIUM | No single documented run/build entrypoint for the game (README documents oTree); contributor cannot start the game from docs | `mayor_api/main.py`, `mayor_web/index.html` |
| GAP-10 | LOW | No CI to guard the engine contract during the refactor/reorg | none — greenfield |
| GAP-11 | LOW | Runtime DB files (`db.sqlite3`, `mayor_api/mayor.db`) committed-adjacent; confirm clean dev reset path | `.gitignore`, `mayor_api/db.py` |

---

## Recommended Sprint Sequencing

| Priority | Gap | Rationale |
|---|---|---|
| Sprint 1 | GAP-01 + GAP-02 | Declare the game canonical, extract anything worth keeping from `platform/`, then update `README`/`AGENTS`/`activeContext`. This sets the single source of truth so all later work targets the right product. Cheap and unblocking. |
| Sprint 1 | GAP-07 | Consolidate plans to one product vision alongside the doc rewrite (same context-cleanup motion). |
| Sprint 2 | GAP-06 | Reorganize the tree and purge clutter (worktree dup, obsolete reports) *after* the stack decision so the move is one-directional. |
| Sprint 2 | GAP-03 + GAP-08 | Inventory/trim the engine and unify tests once `platform/` is gone, fixing the 2 failing tests. Establishes a clean core for the visual layer. |
| Sprint 3 | GAP-05 | Build out multiplayer in the game stack (depends on GAP-01 salvage + GAP-03 clean engine). |
| Sprint 3 | GAP-04 | Visual step-change — best done on a stable, consolidated codebase so polish isn't thrown away. |
| Backlog | GAP-09, GAP-10, GAP-11 | Entry-point docs, CI, and runtime-file hygiene — fold into the sprints above as they touch those areas. |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Deleting `platform/` discards reusable multiplayer/facilitator logic | Re-implementing multiplayer (GAP-05) costs more | Medium | Extract patterns to `archive/` first; do GAP-01 salvage step before deletion |
| Doc rewrite (`AGENTS.md`) loosens guardrails and invites over-engineering | Scope creep on visuals/frontend | Medium | Keep the sound architecture principles; change only stack/product framing and the specific "no heavy frontend" guardrail with an explicit, bounded visual scope |
| Engine refactor (GAP-03) changes game balance | Playtested tuning regresses | Medium | Lock behavior with `playtest.py` baselines and the existing test suites before/after |
| Reorg breaks import paths (`carbonsim_engine` is imported by both stacks + packaged via egg-info) | Game stops running | Medium | Do reorg in one mechanical pass with a full test run; update `pyproject.toml`/imports together |
| "Single product" decision is premature if the workshop business still needs oTree | Lost workshop capability | Low | Confirm with stakeholder that the game (not the workshop platform) is the go-forward product before deleting `platform/` |

---

## Suggested Next Step

This consolidation has a strict dependency order, so start at the top: invoke `/plan` on **GAP-01 + GAP-02** together (declare the game canonical, salvage from `platform/`, rewrite `README`/`AGENTS`/`activeContext`, consolidate `plans/`). Once the single source of truth is established and the tree is reorganized (GAP-06), plan the engine cleanup (GAP-03), then the multiplayer (GAP-05) and visual (GAP-04) investments that deliver the "improved upon CarbonSim" game.
