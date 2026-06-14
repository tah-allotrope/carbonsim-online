---
title: "Kairosoft Sprint 3 — Animated Chibi Citizens & Frame-Animation Core (GAP-02)"
date: "2026-06-14"
status: "draft"
request: "Multiple multi-phase plans from reports/2026-06-14-kairosoft-visual-style-gap-analysis.md — Sprint 3: animated chibi citizens + frame-animation core."
plan_type: "multi-phase"
research_inputs:
  - "research/2026-06-14_kairosoft-visual-style.md"
  - "reports/2026-06-14-kairosoft-visual-style-gap-analysis.md"
---

# Plan: Kairosoft Sprint 3 — Animated Chibi Citizens & Frame-Animation Core

## Objective
Add the signature Kairosoft "life" — little animated chibi citizens wandering the city and reacting to game state — which requires first giving the renderer a sprite-sheet frame-animation capability it currently lacks.

## Context Snapshot
- **Current state:** `web/js/isocity.js` only blits **single static images** (`ctx.drawImage` of one frame); no character sprites, no frame stepping. The RAF loop (30fps throttle, DPR cap, `prefers-reduced-motion` → `drawStatic`) drives only particles + tint.
- **Desired state:** A lightweight sprite-sheet animation system; chibi citizen sprites with walk/idle/reaction frames moving around plots/paths, with density/behavior tied to game state (lively when thriving; coughing/fleeing under high smog).
- **Key repo surfaces:** `web/js/isocity.js` (RAF `loop`, `tileToScreen`, particle update pattern, `draw` layering, caps, reduced-motion), `web/assets/manifest.json` + `web/js/assets.js`, `docs/design-language.md`.
- **Out of scope:** Building art (Sprint 2 — citizens populate finished buildings), feedback pop-ups (Sprint 4), projection change.

## Research Inputs
- `research/2026-06-14_kairosoft-visual-style.md` — chibi citizens are the most glaring miss; oblique needs ~3 sprite sets (side mirrored / front / back); renderer needs frame animation (it has none).
- `reports/2026-06-14-kairosoft-visual-style-gap-analysis.md` — GAP-02 (CRITICAL); reuse RAF loop, particle update pattern, caps, reduced-motion fallback.

## Assumptions and Constraints
- **ASM-001:** Citizen art is delivered as sprite **sheets** (rows = direction, cols = frames) registered in the manifest; ~3 directions per the oblique sprite-economy finding.
- **CON-001:** Preserve the existing 30fps throttle, DPR cap, particle cap, and the `drawStatic` reduced-motion path (citizens must freeze/hide under reduced motion).
- **CON-002:** `AssetLoader` preloads `type:image`; sheets register the same way (frame metadata in the manifest entry or in `isocity.js`).
- **DEC-001:** Citizens are decorative/ambient (the canvas is `aria-hidden`); they reflect state but don't add interactive controls.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Sprite-sheet frame-animation core | Sprint 2 art pipeline | Frame-stepping draw helper in `isocity.js` |
| PHASE-02 | Citizen sprites + movement | PHASE-01 | Wandering chibi citizens |
| PHASE-03 | State-reactive behavior + perf/a11y | PHASE-02 | Smog/compliance-reactive citizens, caps, reduced-motion |

## Detailed Phases

### PHASE-01 - Frame-Animation Core
**Goal**
Teach `isocity.js` to draw animated sprite sheets.

**Tasks**
- [ ] TASK-01-01: Add a `drawSprite(sheet, frameW, frameH, col, row, x, y)` helper using `ctx.drawImage` 9-arg form (source rect → dest).
- [ ] TASK-01-02: Add a frame clock derived from elapsed time (reuse the `loop` timestamp) → current frame index per animation speed.
- [ ] TASK-01-03: Define a manifest convention for sheets (frame size, frame count, directions) and load via `AssetLoader`.

**Files / Surfaces**
- `web/js/isocity.js` — new draw/clock helpers.
- `web/assets/manifest.json`, `web/js/assets.js` — sheet entries.

**Dependencies**
- Sprint 2 (asset pipeline conventions)

**Exit Criteria**
- [ ] A test sheet animates on-canvas at a stable frame rate within the 30fps loop.

**Phase Risks**
- **RISK-01-01:** Frame timing tied to RAF delta can stutter when throttled → derive frame index from accumulated time, not frame count.

### PHASE-02 - Citizen Sprites & Movement
**Goal**
Populate the city with wandering chibi citizens.

**Tasks**
- [ ] TASK-02-01: Add chibi citizen sheets (walk + idle, ~3 directions) to assets/manifest (style-inspired originals or CC0/CC-BY; record in `ATTRIBUTIONS.md`).
- [ ] TASK-02-02: Spawn a citizen pool; move them along plot edges/paths using a wander/seek update (reuse the particle update loop pattern), pick the direction sprite from velocity.
- [ ] TASK-02-03: Depth-sort citizens with plots (painter order by screen-y) so they pass in front of/behind buildings correctly.

**Files / Surfaces**
- `web/js/isocity.js` — citizen pool, update, draw, depth sort.
- `web/assets/sprites/**`, `web/assets/manifest.json`, `ATTRIBUTIONS.md`.

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] Several citizens visibly walk around the city, correctly layered with buildings.

**Phase Risks**
- **RISK-02-01:** Citizens drawn over/under wrong buildings → integrate into the existing back-to-front sort, not a separate pass.

### PHASE-03 - State-Reactive Behavior + Perf/A11y
**Goal**
Make citizens reflect the game and stay performant/accessible.

**Tasks**
- [ ] TASK-03-01: Tie citizen count/behavior to state — lively when compliant/thriving, sparse/coughing/fleeing under high smog (read the same snapshot fields `update()` already uses).
- [ ] TASK-03-02: Cap citizen count and scale by plot count (mirror the existing particle cap); profile to hold ~30fps on a mobile viewport.
- [ ] TASK-03-03: Ensure `prefers-reduced-motion` hides/freezes citizens via the `drawStatic` path.

**Files / Surfaces**
- `web/js/isocity.js` — behavior, caps, reduced-motion.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] Citizen liveliness tracks compliance/smog; ~30fps on mobile; citizens absent/static under reduced motion.

**Phase Risks**
- **RISK-03-01:** Too many animated sprites tank low-end devices → hard cap + scale; reduced-motion floor.

## Verification Strategy
- **MANUAL-001:** Play a game; confirm citizens wander, layer correctly, and react to smog/compliance changes.
- **OBS-001:** Devtools performance trace on a throttled/mobile profile: sustained ~30fps, no unbounded allocation.
- **MANUAL-002:** Toggle OS reduced-motion; confirm citizens freeze/hide.

## Risks and Alternatives
- **RISK-001:** Scope (animation system + art) underestimated → land the frame-core (PHASE-01) and a minimal citizen set first; richness is incremental.
- **ALT-001:** CSS/DOM sprites instead of canvas — rejected; citizens must depth-sort with canvas buildings.

## Grill Me
No open clarification questions. (Citizen art follows the Sprint-2 sourcing decision; ambient/decorative scope is fixed.)

## Suggested Next Step
Execute PHASE-01 → PHASE-03; proceed to Sprint 4 (`2026-06-14-kairosoft-feedback-juice-plan.md`).
