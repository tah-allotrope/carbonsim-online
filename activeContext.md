# Active Context

## Current Sprint

Sprint 3 — Isometric Renderer & State Mapping (`plans/2026-06-13-isometric-renderer-plan.md`)

## Retro Isometric Tycoon Roadmap

| Sprint | Title | Status |
|---|---|---|
| 1 | Retro Asset Pipeline & Static Serving | ✅ complete |
| 2 | Retro Design Token System & Chrome | ✅ complete |
| 3 | Isometric Renderer & State Mapping | ⏳ in progress |
| 4 | Retro Reskin Across All Screens | 🔒 |
| 5 | Retro SFX & Perf/A11y Polish | 🔒 |

## Plan

- [ ] PHASE-01: Iso projection + grid + sprite blitting scaffold
- [ ] PHASE-02: Deterministic engine-state → city mapping (cap 16 + district tile)
- [ ] PHASE-03: Depth/overlay layering + triggers/particles
- [ ] PHASE-04: Feature-flagged swap + parity check in screens

## Notes

- Q-001 answered: render all companies up to 16 plots, aggregate remainder into district tile.
- Derived from `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md`

## Notes

- Derived from `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md`
- Aesthetic: isometric tycoon (SimCity 2000 / Theme Hospital register)
- Tech: vanilla JS + canvas + FastAPI; no new frontend framework
