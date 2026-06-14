---
title: "Kairosoft Sprint 2 — Characterful Building Sprite Art & Sourcing (GAP-01/05)"
date: "2026-06-14"
status: "draft"
request: "Multiple multi-phase plans from reports/2026-06-14-kairosoft-visual-style-gap-analysis.md — Sprint 2: characterful building sprite art + asset sourcing."
plan_type: "multi-phase"
research_inputs:
  - "research/2026-06-14_kairosoft-visual-style.md"
  - "reports/2026-06-14-kairosoft-visual-style-gap-analysis.md"
---

# Plan: Kairosoft Sprint 2 — Characterful Building Sprite Art & Sourcing

## Objective
Replace CarbonSim's plain flat tiles with an outlined, saturated, **characterful and varied** building sprite set that reads as Kairosoft — the single biggest visual lever — and wire the renderer to pick sprites by company/sector/state.

## Context Snapshot
- **Current state:** `web/assets/sprites/` has 6 plain 64² PNGs (`factory_dirty/clean`, `smog`, `player_marker`, `district`) + `tiles/ground.png`; `web/js/isocity.js` `drawPlotStructure` only swaps dirty↔clean. No variety, weak outlines, low personality.
- **Desired state:** A re-arted set with strong outlines, saturated fills, and **variety** (multiple building types + upgrade tiers + decorations), authored to the 64×32 iso footprint and the Sprint-1 palette; manifest + renderer select by company/sector/state.
- **Key repo surfaces:** `web/assets/manifest.json`, `web/js/assets.js` (`AssetLoader`), `web/js/isocity.js` (`drawPlotStructure`, `buildPlots`, `drawPlotGround`), `docs/design-language.md` (sprite spec), `ATTRIBUTIONS.md`.
- **Out of scope:** Animated citizens (Sprint 3), feedback juice (Sprint 4), projection change (kept isometric).

## Research Inputs
- `research/2026-06-14_kairosoft-visual-style.md` — defining trait is cute outlined characterful buildings; **must be style-inspired originals, not Kairosoft's IP**; keep iso, invest in art.
- `reports/2026-06-14-kairosoft-visual-style-gap-analysis.md` — GAP-01 (CRITICAL) + GAP-05 (sourcing/licensing); reuse manifest pipeline + `drawPlotStructure`.

## Assumptions and Constraints
- **ASM-001:** Sprites stay 64×64 PNG on the existing 64×32 iso footprint (no renderer geometry change); buildings may extend taller than the tile (drawn with a vertical offset, as `drawPlotStructure` already does with `pos.y - 36`).
- **ASM-002:** The Sprint-1 palette + sprite spec exist in `docs/design-language.md` to keep art consistent.
- **CON-001:** Assets are **style-inspired originals or CC0/CC-BY** — never Kairosoft's actual assets; every asset tracked in `ATTRIBUTIONS.md`.
- **CON-002:** `AssetLoader` only preloads manifest entries of `type: "image"` — new sprites must be registered there.
- **DEC-001:** Mapping is by the player/company `sector_label` and abatement/compliance state already present in the engine snapshot.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Asset strategy, sprite spec, sourcing | Sprint 1 palette | Sprite spec in design-language; sourced/authored art; attributions |
| PHASE-02 | Register sprites in manifest + loader | PHASE-01 | Expanded `manifest.json`, preloaded images |
| PHASE-03 | Wire renderer selection + verify | PHASE-02 | `drawPlotStructure` variety logic, browser check |

## Detailed Phases

### PHASE-01 - Strategy, Spec & Sourcing
**Goal**
Decide author-vs-pack, define a sprite spec, and produce the art legally.

**Tasks**
- [ ] TASK-01-01: Define the sprite spec in `docs/design-language.md` — palette (from Sprint 1), outline weight/color, light angle, 64×32 footprint, max height, anti-alias rules.
- [ ] TASK-01-02: Choose asset strategy (author original pixel art vs. CC0/CC-BY cute-iso packs) — see Grill Me; avoid Kairosoft IP.
- [ ] TASK-01-03: Produce/collect the building set: ≥4 sector building types (e.g. thermal, steel/cement, generation, generic industry), each with **clean vs. dirty/high-emission** and at least one **upgrade/abated** variant, plus decorations (trees/roads).
- [ ] TASK-01-04: Record every asset (source, author, license) in `ATTRIBUTIONS.md`.

**Files / Surfaces**
- `docs/design-language.md` — sprite spec.
- `web/assets/sprites/**` — new art.
- `ATTRIBUTIONS.md` — credits.

**Dependencies**
- Sprint 1 (palette/spec)

**Exit Criteria**
- [ ] A coherent, license-clean building set exists matching the spec; attributions recorded.

**Phase Risks**
- **RISK-01-01:** Art inconsistency across many sprites → enforce the spec; produce one reference building first and match to it.

### PHASE-02 - Manifest & Loader Registration
**Goal**
Make the new sprites loadable through the existing pipeline.

**Tasks**
- [ ] TASK-02-01: Add each sprite to `web/assets/manifest.json` with logical names (e.g. `bldg_thermal_dirty`, `bldg_thermal_clean`, `bldg_steel_dirty`, …, `decor_tree`).
- [ ] TASK-02-02: Confirm `AssetLoader.load()` preloads them (type `image`); add a manifest-vs-disk existence check.

**Files / Surfaces**
- `web/assets/manifest.json`; `web/js/assets.js` (verify, likely no change).

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] All new sprites resolve with zero 404s in the browser console.

**Phase Risks**
- **RISK-02-01:** Manifest drift → assert every manifest path exists (extend the existing static-asset test pattern).

### PHASE-03 - Renderer Selection & Verification
**Goal**
Render the right building per company/sector/state.

**Tasks**
- [ ] TASK-03-01: Extend `isocity.js` `drawPlotStructure` to choose a sprite by `company.sector_label` + abatement/compliance state (currently only dirty↔clean).
- [ ] TASK-03-02: Optionally vary `buildPlots`/`drawPlotGround` with decorations for empty tiles.
- [ ] TASK-03-03: Verify in-browser across solo + co-op that sectors render distinct, characterful buildings; smog/compliance overlays still apply.

**Files / Surfaces**
- `web/js/isocity.js` — `drawPlotStructure`, `buildPlots`, `drawPlotGround`.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] Different sectors show different buildings; abated buildings visibly upgrade; city reads as Kairosoft-cute.

**Phase Risks**
- **RISK-03-01:** Taller buildings break painter ordering/overlap → keep back-to-front sort; tune vertical offset per sprite.

## Verification Strategy
- **MANUAL-001:** Play solo + co-op; confirm sector-distinct, characterful buildings and correct dirty/clean/upgrade states.
- **OBS-001:** Browser console shows zero `/assets` 404s after preload.
- **TEST-001:** Extend the static-asset test to assert all manifest sprite paths return 200.

## Risks and Alternatives
- **RISK-001:** IP — accidentally copying Kairosoft → originals/CC only; document provenance.
- **ALT-001:** Procedural (code-drawn) buildings instead of sprites — rejected; sprites give the characterful Kairosoft look the gap analysis calls for.

## Grill Me
1. **Q-001:** Author original pixel art, or assemble from CC0/CC-BY cute-iso packs?
   - **Recommended default:** Start from CC0 packs (e.g. Kenney/OpenGameArt) to move fast, supplement with light original edits for sector specificity; track licenses.
   - **Why this matters:** Drives PHASE-01 effort, timeline, and `ATTRIBUTIONS.md`.
   - **If answered differently:** "Author all" raises art effort/quality ceiling; "packs only" may limit sector specificity.

## Suggested Next Step
Answer Q-001, execute PHASE-01 → PHASE-03; proceed to Sprint 3 (`2026-06-14-kairosoft-citizens-plan.md`).
