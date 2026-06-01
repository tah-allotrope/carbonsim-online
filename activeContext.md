# Active Context

## Current Sprint

Sprint 1 — Canonical Game Stack Consolidation

## Plan

- [x] PHASE-01: Salvage reusable patterns from platform/ into archive/
- [x] PHASE-02: Move platform/ to archive, create requirements.txt, clean .gitignore
- [x] PHASE-03: Rewrite context docs and consolidate plans

## Goal

Declare the Climate Mayor game stack (`carbonsim_engine` + `mayor_api` + `mayor_web`) the single canonical product, archive the orphaned oTree platform, and rewrite the top-level context docs so they describe the game rather than the abandoned workshop platform.

## Progress

### Done

- PHASE-01: Archived deployment artifacts and wrote SALVAGE-NOTES.md mapping 6 pattern categories to Sprint 4.
- PHASE-02: Moved platform/ to archive/otree-platform/runnable/, created root requirements.txt, cleaned .gitignore, updated engine keywords. 83 tests passing.
- PHASE-03: Rewrote README.md, AGENTS.md, activeContext.md. Replaced project-plan.md with game roadmap index. Archived divergent plans.

### In Progress

- None.

### Blocked

- None.

## Key Decisions

- Q-001: Archive (not delete) the oTree platform — keep it runnable for Sprint 4 reference.
- Q-002: Use requirements.txt (not pyproject.toml) for the root dependency manifest.

## Relevant Files

- `README.md` — rewritten for game stack
- `AGENTS.md` — rewritten for game stack
- `plans/2026-05-29-game-focus-roadmap-index.md` — sprint roadmap index
- `archive/otree-platform/SALVAGE-NOTES.md` — pattern mapping for Sprint 4
- `archive/otree-platform/runnable/` — archived oTree platform

## Next Sprint

Sprint 2 — Repository Reorganization & Clutter Purge (`plans/2026-05-29-repo-reorganization-cleanup-plan.md`)
