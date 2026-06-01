# Active Context

## Current Sprint

Sprint 2 — Repository Reorganization & Clutter Purge

## Plan

- [x] PHASE-01: Purge clutter (worktree dup, obsolete reports, runtime DBs, .gitignore)
- [x] PHASE-02: Adopt src/-style layout (engine/, server/, web/) & fix all paths/imports
- [x] PHASE-03: Document the new layout and conventions

## Goal

Give the single-product game repo a conventional, navigable layout and remove accumulated clutter.

## Progress

### Done

- PHASE-01: Removed duplicate worktree, archived 18 obsolete reports, deleted runtime DBs, extended .gitignore.
- PHASE-02: Renamed carbonsim_engine/ → engine/, mayor_api/ → server/, mayor_web/ → web/. Updated 26 import sites, packaging config, web-dir resolution, and docs. 83 tests passing.
- PHASE-03: Updated README project layout, created docs/STRUCTURE.md, cross-linked from AGENTS.md.

### In Progress

- None.

### Blocked

- None.

## Key Decisions

- Q-001: Adopted src/-style grouping (engine/, server/, web/).
- Q-002: Archive (not delete) obsolete reports — kept in archive/reports/.

## Relevant Files

- `docs/STRUCTURE.md` — new directory layout guide
- `README.md` — updated project layout table
- `AGENTS.md` — cross-linked to docs/STRUCTURE.md

## Next Sprint

Sprint 3 — Engine Trim, Modularization & Test Unification (`plans/2026-05-29-engine-trim-test-unification-plan.md`)
