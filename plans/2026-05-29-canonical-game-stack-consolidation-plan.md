---
title: "Sprint 1 — Canonical Game Stack Consolidation"
date: "2026-05-29"
status: "draft"
request: "Sequenced multiphase plans from reports/2026-05-29-single-multiplayer-game-gap-analysis.md — cluster (1): GAP-01 + GAP-02 + GAP-07 (declare game stack canonical, salvage from platform/, remove oTree, rewrite context docs and consolidate plans)."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-05-29-single-multiplayer-game-gap-analysis.md"
---

# Plan: Sprint 1 — Canonical Game Stack Consolidation

## Objective
Declare the Climate Mayor game stack (`carbonsim_engine` + `mayor_api` + `mayor_web`) the single canonical product, salvage any reusable multiplayer/facilitator patterns from the orphaned oTree `platform/` stack, remove that stack, and rewrite the top-level context/docs so they describe the game rather than the abandoned workshop platform. This is Sprint 1 of a 5-plan sequence and unblocks every later plan by establishing one source of truth.

## Context Snapshot
- **Current state:** Two parallel product stacks share one engine. `platform/` (oTree workshop product, 21 tracked files) is orphaned — its engine is a 1-line shim `from carbonsim_engine.engine import *` and nothing in the game stack imports `platform`. The game stack receives 100% of recent commits. `README.md`, `AGENTS.md`, and `plans/project-plan.md` still describe the oTree platform and mandate the oTree stack; `plans/` also contains a separate game concept ("Carbon Crunch Daily") and workshop-only plans.
- **Desired state:** One canonical game stack. `platform/` removed (after salvage). `README.md`, `AGENTS.md`, `activeContext.md`, and the roadmap accurately describe the single+multiplayer game and its real stack (Python/FastAPI engine + static JS frontend + WebSocket). Divergent plans archived. A root dependency manifest exists for the game.
- **Key repo surfaces:** `platform/` (all), `README.md`, `AGENTS.md`, `activeContext.md`, `plans/project-plan.md`, `plans/2026-04-25-free-tier-deployment-plan.md`, `plans/2026-04-26-vietnam-market-testing-plan.md`, `plans/2026-04-29-carbon-crunch-daily-plan.md`, `carbonsim_engine/pyproject.toml`, `mayor_api/main.py`.
- **Out of scope:** Engine trimming/modularization (Sprint 3), tree reorganization into src/server/web (Sprint 2), multiplayer feature build-out (Sprint 4), visual work (Sprint 5). This plan does not move `carbonsim_engine`/`mayor_api`/`mayor_web` directories — only removes `platform/` and rewrites docs.

## Research Inputs
- `reports/2026-05-29-single-multiplayer-game-gap-analysis.md` — Source of GAP-01/02/07. Confirms `platform/` is cleanly severable (no inbound deps from the game stack), that docs actively misdirect agents, and the dependency-ordered sprint sequencing that makes this plan first.

## Assumptions and Constraints
- **ASM-001:** The workshop/oTree business is being retired in favor of the game. (Flagged for confirmation — see Grill Me Q-001; if false, salvage scope in PHASE-01 expands and PHASE-02 deletion is deferred.)
- **ASM-002:** `mayor_api/main.py` already serves both the API and the static `mayor_web` frontend, so removing `platform/` removes no runtime capability the game depends on.
- **CON-001:** `carbonsim_engine` is consumed by both stacks today and is installed as a package (egg-info present); its import path must remain `carbonsim_engine` through this plan (no rename here).
- **DEC-001:** The game stack is the go-forward product (established by the user's request and 6 weeks of momentum).

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Salvage reusable workshop/multiplayer patterns from `platform/` into an archive | None | `archive/otree-platform/` with extracted reference patterns + a salvage notes doc |
| PHASE-02 | Remove the oTree stack and its dependency surface | PHASE-01 | `platform/` deleted, oTree deps removed, root game dependency manifest added |
| PHASE-03 | Rewrite context/docs and consolidate plans around the game | PHASE-02 | New `README.md`, `AGENTS.md`, `activeContext.md`, game roadmap; divergent plans archived |

## Detailed Phases

### PHASE-01 - Salvage From the oTree Platform
**Goal**
Before deletion, capture any multiplayer, facilitator, room, or deployment patterns from `platform/` that will inform Sprint 4 (multiplayer) and deployment, so nothing reusable is lost.

**Tasks**
- [ ] TASK-01-01: Read `platform/carbonsim_phase12/FacilitatorPanel.html`, `WorkshopHub.html`, `Welcome.html`, `deployment.py`, and `settings.py`; note patterns worth porting (room/session flow, facilitator controls, synchronized timing, exports).
- [ ] TASK-01-02: Create `archive/otree-platform/` and copy the deployment artifacts worth adapting for the FastAPI game: `platform/Dockerfile`, `platform/Caddyfile`, `platform/fly.toml`, `platform/docker-compose.yml`, `platform/Procfile`.
- [ ] TASK-01-03: Write `archive/otree-platform/SALVAGE-NOTES.md` summarizing which oTree patterns map to which future plan (cite Sprint 4 multiplayer GAP-05), so the archive is self-explaining.
- [ ] TASK-01-04: Confirm via grep that no game-stack file imports `platform` or `carbonsim_phase12` (expected: none), recording the result in the salvage notes.

**Files / Surfaces**
- `platform/carbonsim_phase12/*.html`, `platform/carbonsim_phase12/deployment.py`, `platform/settings.py` - reference patterns to extract.
- `platform/Dockerfile`, `platform/Caddyfile`, `platform/fly.toml`, `platform/docker-compose.yml`, `platform/Procfile` - deployment artifacts to adapt later.
- `archive/otree-platform/` (new) - destination for salvaged material.

**Dependencies**
- None.

**Exit Criteria**
- [ ] `archive/otree-platform/SALVAGE-NOTES.md` exists and references concrete future-use mappings.
- [ ] Grep confirms zero inbound imports from the game stack to `platform/`.

**Phase Risks**
- **RISK-01-01:** Over-salvaging recreates the redundancy. Mitigation: archive only documented patterns + deployment files, not the running oTree app.

### PHASE-02 - Remove the oTree Stack
**Goal**
Delete `platform/` and its oTree dependency surface, and give the game stack a first-class dependency manifest so it can be installed/run without `platform/requirements.txt`.

**Tasks**
- [ ] TASK-02-01: Delete the `platform/` directory in full (it contains only the orphaned oTree app, its tests, the engine shim, and deployment artifacts already archived in PHASE-01).
- [ ] TASK-02-02: Create a root dependency manifest for the game (`requirements.txt` or `pyproject.toml` at repo root) listing the FastAPI runtime deps actually used by `mayor_api` (fastapi, uvicorn, the WebSocket/server deps) and the `carbonsim_engine` install; remove reliance on `platform/requirements.txt`.
- [ ] TASK-02-03: Remove oTree from the dependency set entirely; confirm `carbonsim_engine/pyproject.toml` keywords/description no longer imply "workshop-only" if it conflicts with the game framing (light touch — full engine rework is Sprint 3).
- [ ] TASK-02-04: Update `.gitignore` to drop now-irrelevant `platform/*` rules (`platform/db.sqlite3`, `platform/otree_*.log`, `platform/otree_*.pid`).
- [ ] TASK-02-05: Run the game test suites to prove nothing broke: `pytest mayor_api/tests/test_api.py carbonsim_engine/tests/ -q`.

**Files / Surfaces**
- `platform/` - deleted.
- `requirements.txt` or `pyproject.toml` (root, new) - game dependency manifest.
- `.gitignore` - remove platform-specific rules.
- `carbonsim_engine/pyproject.toml` - light metadata touch only.

**Dependencies**
- PHASE-01 (salvage complete).

**Exit Criteria**
- [ ] `platform/` no longer exists in the tree.
- [ ] Game server importable and `pytest mayor_api/tests/test_api.py carbonsim_engine/tests/ -q` runs with no new failures beyond the 2 pre-existing engine failures (those are fixed in Sprint 3).
- [ ] A root dependency manifest exists and installs the game stack cleanly in a fresh venv.

**Phase Risks**
- **RISK-02-01:** A hidden import or doc link references `platform/`. Mitigation: grep the whole repo for `platform`/`otree`/`carbonsim_phase12` before and after deletion; fix references in PHASE-03.

### PHASE-03 - Rewrite Context Docs and Consolidate Plans
**Goal**
Make the first files any agent reads tell the truth: the product is the single+multiplayer game on the FastAPI stack. Archive divergent product plans so `plans/` reflects one vision.

**Tasks**
- [ ] TASK-03-01: Rewrite `README.md` around the game — what it is, the `carbonsim_engine` + `mayor_api` (FastAPI) + `mayor_web` (static) architecture, how to install (root manifest), how to run the server (`uvicorn mayor_api.main:create_app --factory` or the project's actual entry), how to open the web client, and how to run tests. Remove all oTree Phase 1-10 content and the broken `plan/` path reference (correct dir is `plans/`).
- [ ] TASK-03-02: Rewrite `AGENTS.md` — keep the sound architecture principles (server-authoritative state, deterministic year flow, auditability, simplicity-first) but replace `Default Stack: oTree` and the "do not move to a custom real-time stack" / "not a generic carbon game" framing with the real stack and the explicit goal of a polished single+multiplayer game. Update the Source-Of-Truth order to list this gap report and the game plans. Relax the "no heavy front-end" guardrail into a bounded visual-scope statement that points to Sprint 5.
- [ ] TASK-03-03: Reset `activeContext.md` to track the consolidation effort and the 5-plan sequence (replace the frozen Phase 5/6 "preparing commit" content).
- [ ] TASK-03-04: Replace `plans/project-plan.md` (oTree roadmap) with a game-focused roadmap index that links the five Sprint plans in dependency order.
- [ ] TASK-03-05: Move divergent/obsolete plans to `archive/plans/`: `plans/2026-04-25-free-tier-deployment-plan.md`, `plans/2026-04-26-vietnam-market-testing-plan.md`, `plans/2026-04-29-carbon-crunch-daily-plan.md`, and any other workshop-only or alternate-product plan. Keep Climate Mayor plans and the five new Sprint plans.
- [ ] TASK-03-06: Grep the repo for residual `oTree`/`platform`/`carbonsim_phase12` references in docs and fix them.

**Files / Surfaces**
- `README.md`, `AGENTS.md`, `activeContext.md` - full rewrites.
- `plans/project-plan.md` - replaced with game roadmap index.
- `plans/2026-04-25-*.md`, `plans/2026-04-26-*.md`, `plans/2026-04-29-*.md` - moved to `archive/plans/`.

**Dependencies**
- PHASE-02 (stack decision is real before docs claim it).

**Exit Criteria**
- [ ] `README.md` lets a zero-context engineer install, run, and test the game without mentioning oTree.
- [ ] `AGENTS.md` names the FastAPI game stack as canonical and no longer forbids the visual work in Sprint 5.
- [ ] `plans/` contains only the one product's roadmap + Sprint plans; divergent plans live under `archive/plans/`.
- [ ] Zero stale `oTree`/`platform` references remain in tracked docs.

**Phase Risks**
- **RISK-03-01:** Rewriting `AGENTS.md` loosens guardrails and invites scope creep. Mitigation: keep all architecture principles; change only stack/product framing and bound the visual scope to Sprint 5's plan.

## Verification Strategy
- **TEST-001:** `pytest mayor_api/tests/test_api.py carbonsim_engine/tests/ -q` passes (≤ the 2 known pre-existing engine failures) after PHASE-02 and again after PHASE-03.
- **MANUAL-001:** Fresh-clone dry run: in a clean venv, install from the new root manifest and start the server; confirm `index.html` and a solo game load via the FastAPI app with `platform/` gone.
- **OBS-001:** `git grep -in "otree\|platform/\|carbonsim_phase12"` returns only `archive/` hits.

## Risks and Alternatives
- **RISK-001:** Deleting `platform/` discards reusable multiplayer/facilitator logic needed in Sprint 4. Mitigation: PHASE-01 salvage-first gate with documented mappings.
- **ALT-001:** Keep both stacks and just fix docs. Rejected: the redundancy is the core problem the user named; a dormant second stack keeps splitting the engine and confusing agents.

## Grill Me
1. **Q-001:** Is the oTree workshop/facilitator product definitively retired, or must it remain runnable for live workshops in parallel with the game?
   - **Recommended default:** Retired — delete `platform/` after salvage.
   - **Why this matters:** Determines whether PHASE-02 deletes the stack or only quarantines it.
   - **If answered differently:** Skip TASK-02-01 deletion; instead move `platform/` to `archive/otree-platform/runnable/` intact, and PHASE-03 docs describe two products with the game primary.
2. **Q-002:** For the root dependency manifest, prefer `pyproject.toml` (single packaged project incl. engine) or a simple `requirements.txt`?
   - **Recommended default:** `pyproject.toml` at root that depends on the local `carbonsim_engine` and the FastAPI runtime.
   - **Why this matters:** Affects install/run instructions in README and the Sprint 2 reorg.
   - **If answered differently:** Use `requirements.txt`; adjust TASK-02-02 and TASK-03-01 commands accordingly.

## Suggested Next Step
Answer Q-001 and Q-002, then execute PHASE-01 → PHASE-03 in order. On completion, proceed to `plans/2026-05-29-repo-reorganization-cleanup-plan.md` (Sprint 2).
