---
title: "Sprint 1 — Retro Asset Pipeline & Static Serving (GAP-03)"
date: "2026-06-13"
status: "draft"
request: "Create multiple multi-phase plans from reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md — one per recommended sprint. This is Sprint 1: the free-asset pipeline."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md"
---

# Plan: Sprint 1 — Retro Asset Pipeline & Static Serving

## Objective
Source, license-vet, and make servable the free isometric tilesets, building sprites, and pixel/bitmap font that every later retro-reskin sprint depends on. After this sprint the repo can serve `/assets/*`, has a manifest the renderer can consume, and tracks every asset's license in-repo. This is the cheapest, highest-leverage gap — nothing visual can be built until it lands.

## Context Snapshot
- **Current state:** No `web/assets`, `web/img`, `web/tiles`, or `web/fonts` directory exists. `server/main.py:49-51` mounts only `/css` and `/js` as `StaticFiles` — there is nowhere to serve images/fonts from. No attributions file exists.
- **Desired state:** `web/assets/` exists with vetted isometric tiles, building sprites, and a pixel font; FastAPI serves it at `/assets`; a JSON manifest maps logical names → files/atlas coordinates; `ATTRIBUTIONS.md` records each asset's license and author.
- **Key repo surfaces:** `server/main.py:49-51` (StaticFiles mounts), `web/js/api.js` (fetch conventions), `engine/engine.py` (company/abatement vocabulary the sprites must cover).
- **Out of scope:** Writing the isometric renderer (Sprint 3), changing the design tokens (Sprint 2), authoring original pixel art (decision: use free packs with attribution).

## Research Inputs
- `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md` — defines GAP-03 (no asset pipeline / no `/assets` mount / no pixel font) as a HIGH prerequisite for GAP-01/02, and fixes the decisions: isometric tycoon look, free+attribution (CC-BY acceptable) assets, vanilla JS + canvas.

## Assumptions and Constraints
- **ASM-001:** CC-BY (attribution) assets are acceptable; CC0 (e.g. Kenney isometric packs) is preferred to minimize attribution burden.
- **ASM-002:** The sprite vocabulary needed mirrors the engine: a base ground/plot tile, a "factory/company" building with at least a dirty vs. cleaned (post-abatement) variant, smog overlay tiles, and a player-highlight marker.
- **CON-001:** No new runtime frontend dependency — assets are static files plus a plain JSON manifest loaded via `fetch` (the `web/js/api.js` pattern).
- **CON-002:** The `/assets` mount must follow the exact `StaticFiles` pattern already used at `server/main.py:49-51` and must not break the existing SPA fallback (`FileResponse` at `server/main.py:57-61`).
- **DEC-001:** Assets live under `web/assets/` (siblings: `web/css`, `web/js`) so the existing path-resolution logic in `server/main.py` extends naturally.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Source & license-vet the asset set | None | Downloaded tiles/sprites/font + license records |
| PHASE-02 | Serve assets via FastAPI | PHASE-01 | `web/assets/` tree + `/assets` mount in `server/main.py` |
| PHASE-03 | Manifest + attributions | PHASE-02 | `web/assets/manifest.json`, `ATTRIBUTIONS.md`, smoke test |

## Detailed Phases

### PHASE-01 - Source & License-Vet Assets
**Goal**
Assemble a complete, legally clean set of isometric tiles, building sprites, and a pixel font covering the game vocabulary.

**Tasks**
- [ ] TASK-01-01: Identify candidate free isometric tilesets/sprites (Kenney isometric packs [CC0], OpenGameArt isometric tiles, itch.io free packs) covering: ground tile, factory/company building (≥2 variants: high-emission vs. abated/clean), smog overlay, player-highlight marker.
- [ ] TASK-01-02: Select a free pixel/bitmap display font (e.g. Press Start 2P [OFL], or a public-domain VGA font) plus confirm a readable body font remains for dense stats.
- [ ] TASK-01-03: Record each asset's source URL, author, and license at selection time (raw notes feeding `ATTRIBUTIONS.md` in PHASE-03).
- [ ] TASK-01-04: Normalize formats — PNG for sprites/tiles, WOFF2/TTF for the font; keep an isometric tile footprint convention (2:1 diamond) consistent across the set.

**Files / Surfaces**
- `engine/engine.py` / `engine/constants.py` — inspect to confirm the abatement/company vocabulary the sprite variants must represent.

**Dependencies**
- None

**Exit Criteria**
- [ ] A local asset set exists covering all vocabulary items above, each with a recorded source + license that is CC0/CC-BY/OFL or equivalently redistributable.

**Phase Risks**
- **RISK-01-01:** A pack mixes incompatible licenses → prefer single-source CC0 packs (Kenney) and reject anything without an explicit redistributable license.

### PHASE-02 - Serve Assets via FastAPI
**Goal**
Make the asset directory reachable in the browser without breaking existing routing.

**Tasks**
- [ ] TASK-02-01: Create `web/assets/` with subdirs `tiles/`, `sprites/`, `fonts/` and place vetted assets from PHASE-01.
- [ ] TASK-02-02: Add an `app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")` line in `server/main.py` adjacent to the existing `/css` and `/js` mounts (lines 49-51), resolving `assets_dir` the same way `css_dir`/`js_dir` are resolved.
- [ ] TASK-02-03: Confirm the SPA fallback `FileResponse` logic (`server/main.py:57-61`) still serves HTML routes and does not intercept `/assets/*`.

**Files / Surfaces**
- `server/main.py:49-61` — add mount; verify fallback ordering.
- `web/assets/**` — new asset tree.

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] `GET /assets/fonts/<font>` and `GET /assets/tiles/<tile>.png` return 200 with correct content-type when the server runs.
- [ ] Existing screens (`/`, `/game.html`, etc.) still load (fallback unbroken).

**Phase Risks**
- **RISK-02-01:** Mount ordering causes the catch-all fallback to shadow `/assets` → mount `/assets` before the fallback, mirroring how `/css` and `/js` are ordered.

### PHASE-03 - Manifest & Attributions
**Goal**
Give the future renderer a stable data contract and satisfy attribution obligations.

**Tasks**
- [ ] TASK-03-01: Author `web/assets/manifest.json` mapping logical names (e.g. `ground`, `factory_dirty`, `factory_clean`, `smog`, `player_marker`) → file paths (and atlas x/y/w/h if a packed atlas is used).
- [ ] TASK-03-02: Add a tiny manifest-load helper (extend `web/js/api.js` conventions or a small `assets.js`) that fetches `/assets/manifest.json` and preloads `Image` objects — exposed for Sprint 3 to consume. (Helper only; no rendering.)
- [ ] TASK-03-03: Create root `ATTRIBUTIONS.md` listing each asset: name, author, source URL, license; link it from `README.md`.

**Files / Surfaces**
- `web/assets/manifest.json` — new contract.
- `web/js/assets.js` (or extension of `web/js/api.js`) — manifest/image preloader.
- `ATTRIBUTIONS.md`, `README.md` — credits.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] `manifest.json` validates as JSON and references only files that exist under `web/assets/`.
- [ ] The preloader resolves all manifest images without 404s in the browser console.
- [ ] `ATTRIBUTIONS.md` covers every shipped asset.

**Phase Risks**
- **RISK-03-01:** Manifest drifts from files on disk → add a trivial check (script or test) asserting every manifest path exists.

## Verification Strategy
- **TEST-001:** Add/extend a server test asserting `GET /assets/manifest.json` returns 200 (mirrors existing `server/tests/test_api.py` patterns).
- **MANUAL-001:** Run the server, open devtools Network tab on a page that calls the preloader, confirm font + all manifest images load 200.
- **OBS-001:** Browser console shows zero 404s for `/assets/*` after preload.

## Risks and Alternatives
- **RISK-001:** Attribution drift over time → `ATTRIBUTIONS.md` is the single source; PR checklist item to update it when assets change.
- **ALT-001:** Authoring original pixel art in-repo (no license tracking) was rejected per the user's decision to use free+attribution packs — faster to ship, broader coverage.

## Grill Me
No open clarification questions. (Aesthetic, scope, licensing, and tech approach were fixed during the gap analysis: isometric tycoon, full reskin all modes, free+attribution assets, vanilla JS + canvas.)

## Suggested Next Step
Execute PHASE-01 → PHASE-03 in order; on completion, proceed to Sprint 2 (`2026-06-13-retro-design-tokens-plan.md`). Keep `activeContext.md` pointed at the active phase.
