---
title: "Sprint 2 — Repository Reorganization & Clutter Purge"
date: "2026-05-29"
status: "draft"
request: "Sequenced multiphase plans from reports/2026-05-29-single-multiplayer-game-gap-analysis.md — cluster (2): GAP-06 (repo reorganization and clutter purge)."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-05-29-single-multiplayer-game-gap-analysis.md"
---

# Plan: Sprint 2 — Repository Reorganization & Clutter Purge

## Objective
Give the single-product game repo a conventional, navigable layout and remove accumulated clutter (a 2.3 MB duplicate worktree, ~25 obsolete oTree phase reports, build artifacts, stray runtime DBs). This is Sprint 2; it runs after the oTree stack is gone (Sprint 1) so the move is one-directional and import-path churn happens only once.

## Context Snapshot
- **Current state:** Three sibling top-level code dirs (`carbonsim_engine/`, `mayor_api/`, `mayor_web/`) with no grouping; `.claude/worktrees/hardcore-wu-70aa3d/` is a 2.3 MB full duplicate of the repo (untracked); `reports/` holds 25 files, mostly obsolete oTree phase HTML reports plus `phase_report.html`/`.md` duplicates; `carbonsim_engine.egg-info/` build artifact on disk; `db.sqlite3` (root) and `mayor_api/mayor.db` runtime files present.
- **Desired state:** A conventional layout (decision in Grill Me), clutter removed, obsolete docs archived, import paths updated in one mechanical pass with a green test run, and `.gitignore` extended to keep the tree clean going forward.
- **Key repo surfaces:** `carbonsim_engine/`, `mayor_api/`, `mayor_web/`, `mayor_api/main.py` (computes `web_dir = parent.parent / "mayor_web"`), `carbonsim_engine/pyproject.toml`, root manifest (from Sprint 1), `.gitignore`, `reports/`, `.claude/worktrees/`.
- **Out of scope:** Engine internal modularization (Sprint 3), any behavior change. This plan is moves + deletions + path fixes only.

## Research Inputs
- `reports/2026-05-29-single-multiplayer-game-gap-analysis.md` — Source of GAP-06. Lists the specific clutter (worktree dup, obsolete reports, egg-info, runtime DBs) and the `plan/`→`plans/` doc drift, and sequences reorg after stack removal.

## Assumptions and Constraints
- **ASM-001:** Sprint 1 is complete: `platform/` is gone and a root dependency manifest exists.
- **CON-001:** `mayor_api/main.py` resolves `mayor_web` via a relative path (`Path(__file__).parent.parent / "mayor_web"`); any directory move must update this resolution or preserve the relative relationship.
- **CON-002:** `carbonsim_engine` is imported as a top-level package by `mayor_api` and is pip-installed (egg-info); a rename/move requires updating `pyproject.toml` packaging and reinstalling.
- **DEC-001:** Reorg is mechanical and reversible via git; it must land in a single PR/commit range with a passing test suite to avoid a half-migrated tree.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Purge non-code clutter (no import impact) | None (post-Sprint 1) | Worktree dup gone, obsolete reports archived, artifacts/DBs cleaned, `.gitignore` extended |
| PHASE-02 | Adopt the target directory layout and fix all paths | PHASE-01 | Code dirs grouped per chosen layout, imports + path resolution + packaging updated, tests green |
| PHASE-03 | Document the new layout and conventions | PHASE-02 | README "Project layout" + a short CONTRIBUTING/structure note matching reality |

## Detailed Phases

### PHASE-01 - Purge Clutter
**Goal**
Remove everything that adds noise but not code, so the subsequent move operates on a clean tree.

**Tasks**
- [ ] TASK-01-01: Delete `.claude/worktrees/hardcore-wu-70aa3d/` (2.3 MB untracked full duplicate). Verify it is not an active git worktree (`git worktree list`); if listed, `git worktree remove` it.
- [ ] TASK-01-02: Triage `reports/`: move obsolete oTree phase reports (`2026-04-17-*`, `2026-04-19-*`, `2026-04-24-*` phase HTML, `phase_report.html`, `phase_report.md`) to `archive/reports/`; keep game reports (`2026-04-30-*`, `2026-05-01-*`) and the two gap analyses.
- [ ] TASK-01-03: Remove the `carbonsim_engine.egg-info/` build artifact from the working tree (regenerated on install) and confirm `*.egg-info/` is gitignored.
- [ ] TASK-01-04: Remove stray runtime DBs from the working tree (`db.sqlite3` at root, `mayor_api/mayor.db`); confirm both are gitignored and document the clean-reset path for local dev.
- [ ] TASK-01-05: Extend `.gitignore` for any newly observed runtime/build noise; remove the now-dead `platform/*` rules if Sprint 1 missed them.

**Files / Surfaces**
- `.claude/worktrees/hardcore-wu-70aa3d/` - delete.
- `reports/*` - partial move to `archive/reports/`.
- `carbonsim_engine.egg-info/`, `db.sqlite3`, `mayor_api/mayor.db` - remove from working tree.
- `.gitignore` - extend.

**Dependencies**
- None beyond Sprint 1 completion.

**Exit Criteria**
- [ ] No duplicate repo under `.claude/worktrees/`.
- [ ] `reports/` contains only game-relevant reports; obsolete ones live in `archive/reports/`.
- [ ] No build artifacts or runtime DBs tracked or dirty in `git status`.

**Phase Risks**
- **RISK-01-01:** The worktree is an active git worktree with uncommitted work. Mitigation: check `git worktree list` and `git -C <path> status` before deleting; preserve any unique commits first.

### PHASE-02 - Adopt Target Layout & Fix Paths
**Goal**
Group the code into a conventional structure and update every path/import/packaging reference in one pass, proven by a green test run.

**Tasks**
- [ ] TASK-02-01: Apply the chosen layout (see Grill Me Q-001). Example for `src/`-style: `engine/` (from `carbonsim_engine/`), `server/` (from `mayor_api/`), `web/` (from `mayor_web/`), plus `docs/`, `archive/`, `plans/`, `research/`. Use `git mv` to preserve history.
- [ ] TASK-02-02: Update `carbonsim_engine/pyproject.toml` (or root `pyproject.toml`) packaging `packages.find` / `where` to the new location; reinstall the package in the venv.
- [ ] TASK-02-03: Update all `from carbonsim_engine...` / `import carbonsim_engine` and `from .routes...` / relative imports affected by the move (search across `server`/`mayor_api`, tests, and scripts).
- [ ] TASK-02-04: Update `mayor_api/main.py` web-dir resolution to point at the new web directory location; update the static `/css` and `/js` mounts accordingly.
- [ ] TASK-02-05: Update test discovery paths and any `scripts/` references; move `scripts/validate_deck.py` and `carbonsim_engine/scripts/` under the new structure if appropriate.
- [ ] TASK-02-06: Run the full test suite and a manual server boot to confirm imports, packaging, and static serving all resolve.

**Files / Surfaces**
- `carbonsim_engine/`, `mayor_api/`, `mayor_web/` - moved per chosen layout.
- `*/pyproject.toml` - packaging config.
- `mayor_api/main.py` - web-dir + static mount paths.
- All Python imports referencing moved packages; `tests/`.

**Dependencies**
- PHASE-01.

**Exit Criteria**
- [ ] `pytest` for engine + API suites passes (≤ 2 known engine failures, fixed in Sprint 3).
- [ ] Server boots and serves `index.html`, `/css`, `/js`, and a solo game from the new layout.
- [ ] `git mv` preserved file history (spot-check `git log --follow` on a moved file).

**Phase Risks**
- **RISK-02-01:** A missed import leaves a half-migrated tree. Mitigation: do the move + all path fixes in one commit; gate on a green full test run before committing.
- **RISK-02-02:** Packaging/egg-info points at the old path after move. Mitigation: uninstall + reinstall the package; clear stale egg-info.

### PHASE-03 - Document the Layout
**Goal**
Make the new structure self-explaining so it doesn't drift back.

**Tasks**
- [ ] TASK-03-01: Update the README "Project layout" section to match the new tree exactly (fixing the prior `plan/`→`plans/` drift).
- [ ] TASK-03-02: Add a short `docs/STRUCTURE.md` (or a section in CONTRIBUTING) describing each top-level dir's purpose and where new code belongs.
- [ ] TASK-03-03: Cross-link the structure doc from `AGENTS.md` so future agents land on it.

**Files / Surfaces**
- `README.md`, `docs/STRUCTURE.md` (new), `AGENTS.md`.

**Dependencies**
- PHASE-02.

**Exit Criteria**
- [ ] README layout section matches `ls` of the repo root.
- [ ] A new contributor can locate engine, server, web, docs, and archive from the structure doc alone.

**Phase Risks**
- **RISK-03-01:** Docs drift again. Mitigation: keep the structure doc short and link it from `AGENTS.md` source-of-truth order.

## Verification Strategy
- **TEST-001:** Full engine + API test suites green after PHASE-02.
- **MANUAL-001:** Boot the server from a fresh venv install and load a solo game + static assets from the new layout.
- **OBS-001:** `git status` is clean (no stray artifacts/DBs); `git grep` finds no references to old directory names outside `archive/`.

## Risks and Alternatives
- **RISK-001:** Reorg breaks import paths repo-wide. Mitigation: single mechanical pass, `git mv`, green-test gate.
- **ALT-001:** Leave the flat layout and only purge clutter. Rejected: the user explicitly asked for files reorg, and a grouped layout makes Sprints 3-5 easier to navigate.

## Grill Me
1. **Q-001:** Which target layout — `src/`-style grouping (`engine/`, `server/`, `web/`) or keep current top-level names and just add `docs/`+`archive/`?
   - **Recommended default:** Group into `engine/`, `server/`, `web/`, `docs/`, `archive/`, keeping `plans/` and `research/`.
   - **Why this matters:** Determines the scope of import/path churn in PHASE-02.
   - **If answered differently:** If keeping current names, PHASE-02 shrinks to clutter-only + minor path fixes; skip the renames.
2. **Q-002:** Should obsolete reports/plans be archived in-repo (`archive/`) or deleted (recoverable via git history)?
   - **Recommended default:** Archive in-repo under `archive/` for one release, then prune later.
   - **Why this matters:** Affects whether PHASE-01 moves or deletes ~25 report files.
   - **If answered differently:** If delete, replace the moves with `git rm` and note recovery via history.

## Suggested Next Step
Answer Q-001/Q-002, execute PHASE-01 → PHASE-03, then proceed to `plans/2026-05-29-engine-trim-test-unification-plan.md` (Sprint 3).
