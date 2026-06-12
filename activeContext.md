# Active Context

## Current Sprint

Sprint 1 — Retro Asset Pipeline & Static Serving (`plans/2026-06-13-retro-asset-pipeline-plan.md`)

## Retro Isometric Tycoon Roadmap

| Sprint | Title | Status |
|---|---|---|
| 1 | Retro Asset Pipeline & Static Serving | ✅ complete |
| 2 | Retro Design Token System & Chrome | 🔒 |
| 3 | Isometric Renderer & State Mapping | 🔒 |
| 4 | Retro Reskin Across All Screens | 🔒 |
| 5 | Retro SFX & Perf/A11y Polish | 🔒 |

## Plan

- [x] PHASE-01: Source & license-vet isometric tilesets, building sprites, pixel font
- [x] PHASE-02: Create `web/assets/` tree and add `/assets` FastAPI mount
- [x] PHASE-03: Author `manifest.json`, image preloader, `ATTRIBUTIONS.md`, server test

## Sprint 1 Results

- 92 tests passing (35 server + 57 engine)
- `web/assets/` tree created: `tiles/`, `sprites/`, `fonts/`
- `/assets` StaticFiles mount added to `server/main.py`
- `web/assets/manifest.json` maps logical asset names to paths
- `web/js/assets.js` preloads images and exposes `AssetLoader.getImage(name)`
- `ATTRIBUTIONS.md` tracks font (OFL) and generated image (CC0) licenses
- `README.md` links to `ATTRIBUTIONS.md`
- Phase reports: `reports/2026-06-13-retro-asset-pipeline-phase-01/02/03.html`

## Next Sprint

Sprint 2 — Retro Design Token System & Chrome (`plans/2026-06-13-retro-design-tokens-plan.md`)

## Notes

- Derived from `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md`
- Aesthetic: isometric tycoon (SimCity 2000 / Theme Hospital register)
- Tech: vanilla JS + canvas + FastAPI; no new frontend framework
