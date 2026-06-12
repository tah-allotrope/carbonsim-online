# Active Context

## Current Sprint

Sprint 3 — Isometric Renderer & State Mapping (`plans/2026-06-13-isometric-renderer-plan.md`)

## Retro Isometric Tycoon Roadmap

| Sprint | Title | Status |
|---|---|---|
| 1 | Retro Asset Pipeline & Static Serving | ✅ complete |
| 2 | Retro Design Token System & Chrome | ✅ complete |
| 3 | Isometric Renderer & State Mapping | ✅ complete |
| 4 | Retro Reskin Across All Screens | 🔒 |
| 5 | Retro SFX & Perf/A11y Polish | 🔒 |

## Plan

- [x] PHASE-01: Iso projection + grid + sprite blitting scaffold
- [x] PHASE-02: Deterministic engine-state → city mapping (cap 16 + district tile)
- [x] PHASE-03: Depth/overlay layering + triggers/particles
- [x] PHASE-04: Feature-flagged swap + parity check in screens

## Sprint 3 Results

- 92 tests passing (unchanged — renderer addition)
- `web/js/isocity.js` isometric renderer implemented
- 2:1 diamond projection, 6x6 grid, deterministic company_id hash to plot position
- MAX_PLOTS=16 individual plots; overflow aggregated into district tile
- Visual encodings: dirty/clean factory sprite by abatement, smog alpha by emissions, red tint by compliance gap, player marker
- Particle system: smog puffs + abatement green burst + offset teal sparkle + year parchment flash
- Feature flag `?renderer=isocity` wired in `game.html`, `coop.html`, `summary.html`; default remains skyline
- District sprite added to manifest and attribution
- Phase reports: `reports/2026-06-13-isometric-renderer-phase-01/02/03/04.html`

## Next Sprint

Sprint 4 — Retro Reskin Across All Screens (`plans/2026-06-13-retro-reskin-all-screens-plan.md`)

## Notes

- Q-001 answered: render all companies up to 16 plots, aggregate remainder into district tile.
- Derived from `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md`
- Aesthetic: isometric tycoon (SimCity 2000 / Theme Hospital register)
- Tech: vanilla JS + canvas + FastAPI; no new frontend framework
