---
title: "Sprint 3 — Isometric Renderer & Engine-State City Mapping (GAP-01 + GAP-04)"
date: "2026-06-13"
status: "draft"
request: "Create multiple multi-phase plans from reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md — one per recommended sprint. This is Sprint 3: the isometric renderer + state mapping."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md"
---

# Plan: Sprint 3 — Isometric Renderer & Engine-State City Mapping

## Objective
Build the defining feature of the target: an **isometric pixel-art city** rendered on canvas that deterministically reflects live game state (companies as plots/factories, abatement as building upgrades, emissions as smog). Implement it as a sibling module (`web/js/isocity.js`) that reuses the proven `skyline.js` runtime scaffold, then feature-flag the swap so the shipped skyline is never regressed before parity.

## Context Snapshot
- **Current state:** `web/js/skyline.js` (312 lines) draws a **flat front-on** skyline: axis-aligned `fillRect` buildings (`drawBuildings` 154-190) on a 1-D ground line (`drawGround` 213-226); geometry is `Math.random()`-seeded (`generateBuildings` 44-70); `update(snapshot)` (72-96) reads real engine fields but only drives sky hue + one building's smoke. No isometric projection, tile grid, sprite blitting, or deterministic per-company plot.
- **Desired state:** An isometric tile city in `isocity.js` with `(col,row)→screen` 2:1 projection, sprite blitting from the Sprint-1 manifest, back-to-front draw order, a deterministic seeded plot per company, and visual encodings for emissions/abatement/compliance. Reuses `skyline.js`'s RAF loop, throttle, DPR resize, particle system, reduced-motion fallback, and public trigger API.
- **Key repo surfaces:** `web/js/skyline.js` (scaffold to reuse), `web/assets/manifest.json` + preloader (Sprint 1), `web/css/style.css` retro tokens (Sprint 2), `web/game.html:56-62` (`#skylineCanvas` container + init call), `engine/engine.py` snapshot fields.
- **Out of scope:** Per-screen retro HTML sweep (Sprint 4), chiptune SFX (Sprint 5). This sprint wires the canvas only.

## Research Inputs
- `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md` — GAP-01 (CRITICAL, no iso renderer) and GAP-04 (HIGH, no deterministic state→city mapping). Names the reusable `skyline.js` scaffold (loop/throttle/DPR/particles/reduced-motion/trigger API) and the engine field contract (`projected_emissions`, `allowances`, `compliance_gap`, `active_abatement_ids`, `abatement_menu`, `leaderboard`/`companies`, `player_company.company_id`). Recommends building a sibling module + feature flag.

## Assumptions and Constraints
- **ASM-001:** Sprint 1 manifest exposes `ground`, `factory_dirty`, `factory_clean`, `smog`, `player_marker` tiles; Sprint 2 tokens provide the palette for HUD/overlays.
- **ASM-002:** The snapshot shape consumed by `skyline.js:72-96` is the authoritative state contract; reuse the same field reads, replacing random geometry with deterministic mapping.
- **CON-001:** Keep the existing public API surface — `init`, `update`, `destroy`, `triggerAbatementEffect`, `triggerOffsetEffect`, `triggerYearTransition` — so callers in `game.html`/`coop.html`/`summary.html` swap with minimal change.
- **CON-002:** Preserve the 30fps throttle (`skyline.js:13,98-105`), DPR-aware `resize` (32-42), and the `prefers-reduced-motion` → static-draw branch (24-29, 119-124).
- **DEC-001:** Per-company plot position is seeded by `company_id` (stable across frames and reconnects), not `Math.random()`.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Iso projection + grid + sprite blitting scaffold | Sprints 1-2 | `web/js/isocity.js` core renderer |
| PHASE-02 | Deterministic engine-state → city mapping | PHASE-01 | Seeded plots + emission/abatement/compliance encodings |
| PHASE-03 | Depth/overlay layering + triggers/particles | PHASE-02 | Painter's-order draw + wired effect triggers |
| PHASE-04 | Feature-flagged swap + parity check | PHASE-03 | `isocity` wired into screens behind a flag |

## Detailed Phases

### PHASE-01 - Isometric Renderer Scaffold
**Goal**
Stand up `isocity.js` with isometric math, a tile grid, and sprite blitting — reusing the `skyline.js` lifecycle.

**Tasks**
- [ ] TASK-01-01: Create `web/js/isocity.js` cloning the `skyline.js` module shell: same IIFE/public API, RAF `loop()` with 30fps throttle, DPR `resize()`, reduced-motion branch + `drawStatic()`.
- [ ] TASK-01-02: Add `tileToScreen(col,row)` 2:1 diamond projection and a tile-grid model sized to company count.
- [ ] TASK-01-03: Replace procedural `fillRect` drawing with `drawImage` blitting of ground tiles from the Sprint-1 preloaded `Image` set; render a flat ground grid first.
- [ ] TASK-01-04: Integrate the manifest/image preloader from Sprint 1; gate `init()` until images are loaded (with a static placeholder while loading).

**Files / Surfaces**
- `web/js/isocity.js` — new renderer.
- `web/js/skyline.js` — reference scaffold (do not modify yet).
- `web/assets/manifest.json` + preloader — image source.

**Dependencies**
- Sprint 1 (assets/manifest), Sprint 2 (tokens)

**Exit Criteria**
- [ ] A standalone test page renders an isometric ground grid from real tile sprites at a stable 30fps with correct DPR scaling.

**Phase Risks**
- **RISK-01-01:** Iso math off-by-one causes tile gaps/overlap → unit-verify `tileToScreen` against known coordinates before layering buildings.

### PHASE-02 - Deterministic State → City Mapping
**Goal**
Bind the grid to live game state so the city is legible and stable.

**Tasks**
- [ ] TASK-02-01: Assign each company a fixed plot via a deterministic hash of `company_id` → `(col,row)`; highlight the local player using `player_marker` (reuse the `isPlayer` logic from `skyline.js:55`).
- [ ] TASK-02-02: Encode emissions → smog overlay density per plot (drive from `projected_emissions`); compliance shortfall (`compliance_gap > 0`) → distressed plot tint using Sprint-2 semantic colors.
- [ ] TASK-02-03: Encode active abatement → swap `factory_dirty`→`factory_clean` sprite per measure in `active_abatement_ids` relative to `abatement_menu`.
- [ ] TASK-02-04: Port the `update(snapshot)` field reads from `skyline.js:72-96` and confirm multiplayer/co-op render N plots from `leaderboard`/`companies`.

**Files / Surfaces**
- `web/js/isocity.js` — mapping + `update(snapshot)`.
- `engine/engine.py` — confirm field names/availability.

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] With a real snapshot, each company occupies a stable plot across frames; emissions/abatement/compliance changes are visibly reflected.

**Phase Risks**
- **RISK-02-01:** Snapshot field missing for some modes → keep the defensive defaults already present in `skyline.js:72-96`.

### PHASE-03 - Depth Layering + Effect Triggers
**Goal**
Make the scene read correctly (no z-fighting) and reactive to player actions.

**Tasks**
- [ ] TASK-03-01: Implement back-to-front painter's draw order (sort by `col+row`) for ground → structure → overlay.
- [ ] TASK-03-02: Reuse the `skyline.js` particle system (`spawnParticles`/`updateParticles`/`drawParticles` 228-264) anchored to plot tops for smog.
- [ ] TASK-03-03: Implement `triggerAbatementEffect`/`triggerOffsetEffect`/`triggerYearTransition` for the iso scene (green burst on abatement, sparkle on offset, dawn/dusk on year change) preserving the existing API signatures.

**Files / Surfaces**
- `web/js/isocity.js` — layering + triggers + particles.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] Buildings never draw over nearer tiles; abatement/offset/year triggers produce correct visible effects.

**Phase Risks**
- **RISK-03-01:** Particle/tile counts spike with many companies → cap counts (carry the `particles.length > 150` guard from `skyline.js:243`); finer tuning deferred to Sprint 5.

### PHASE-04 - Feature-Flagged Swap & Parity
**Goal**
Wire `isocity` into the screens without regressing the shipped skyline until parity is confirmed.

**Tasks**
- [ ] TASK-04-01: Introduce a flag (query param or config constant) selecting `Skyline` vs `Isocity` for the `#skylineCanvas` init in `game.html:103-` (and the analogous init in `coop.html`/`summary.html`).
- [ ] TASK-04-02: Verify the iso renderer drives the same overlay labels (`#skylineLabel`, `#skylineCompliance`, `game.html:58-60`).
- [ ] TASK-04-03: Confirm parity across solo, multiplayer, and co-op; once confirmed, default the flag to `isocity` and mark `skyline.js` for removal (removal/cleanup tracked, executed in Sprint 4 sweep).

**Files / Surfaces**
- `web/game.html`, `web/coop.html`, `web/summary.html` — init call + flag.

**Dependencies**
- PHASE-03

**Exit Criteria**
- [ ] All three modes render the iso city behind the flag; flipping the default shows the iso view everywhere with overlays intact.

**Phase Risks**
- **RISK-04-01:** Co-op/multiplayer init differs from solo → audit each screen's init call rather than assuming `game.html`'s pattern is universal.

## Verification Strategy
- **TEST-001:** Pure-function unit check of `tileToScreen` and the `company_id`→plot hash (deterministic outputs for fixed inputs).
- **MANUAL-001:** Run the server, play a solo game with the flag on; confirm plots are stable, smog tracks emissions, abatement cleans a building, year transition animates.
- **MANUAL-002:** Start a multiplayer/co-op session; confirm N plots render and the local player is highlighted; reconnect and confirm plots stay put (determinism).
- **OBS-001:** Devtools performance: sustained ~30fps, no runaway particle/image allocation; zero `/assets` 404s.

## Risks and Alternatives
- **RISK-001:** Replacing the shipped skyline wholesale risks regressing a working feature → mitigated by the sibling module + feature flag (RISK from gap analysis).
- **RISK-002:** Engine-snapshot coupling breaks on field changes → bind through the existing field contract with defensive defaults.
- **ALT-001:** A WebGL/tilemap library was rejected per the vanilla-JS+canvas decision; canvas `drawImage` with a painter's algorithm is sufficient for this scene scale.

## Grill Me
1. **Q-001:** Should the isometric city show **all** market companies as plots, or only a representative subset when company count is large (e.g. big multiplayer rooms)?
   - **Recommended default:** Render all companies up to a cap (e.g. 16 plots), then aggregate the remainder into a "district" tile.
   - **Why this matters:** Drives grid sizing, the `company_id`→plot hash range, and PHASE-02/03 performance.
   - **If answered differently:** "All, always" enlarges the grid and raises the Sprint-5 perf budget; "fixed N" simplifies layout but needs an aggregation rule.

## Suggested Next Step
Answer Q-001, update PHASE-02 grid sizing, then execute PHASE-01 → PHASE-04. Proceed to Sprint 4 (`2026-06-13-retro-reskin-all-screens-plan.md`).
