# Gap Analysis: Kairosoft-Style Visual Upgrade

**Date:** 2026-06-14
**Scope:** Upgrade CarbonSim's in-game visuals to read like a Kairosoft cute pixel-art tycoon — bright saturated palette, characterful/varied outlined building sprites, animated chibi citizens, floating feedback juice (coins/emotes/pop-ups), and rounded Kairosoft-style UI chrome — building on the existing isometric renderer, asset pipeline, `effects.js`, and `style.css`. Projection stays isometric for now (oblique optional).
**Status:** Draft for Review

---

## Executive Summary

CarbonSim already has the *plumbing* for this — a working isometric renderer with an animation loop, a manifest-driven asset loader, a pixel-particle effects module, and a fully tokenized CSS system — so this is an **art-and-juice upgrade, not an engine rewrite**, and it's frontend-only (no engine/test risk). The gap is that the current art is **plain, static, muted, and people-less**, the opposite of Kairosoft's bright, busy, character-driven charm (per `research/2026-06-14_kairosoft-visual-style.md`). **2 CRITICAL gaps** (characterful sprite art; animated chibi citizens) and **2 HIGH** (bright palette + rounded UI/font; floating feedback juice). Recommendation: ship the cheap high-impact palette/UI restyle first, then the building re-art, then citizens, then juice.

---

## Current Capabilities (What We Have)

| Capability | Status | Key Surfaces |
|---|---|---|
| Isometric renderer with RAF loop, plots, layering | Working | `web/js/isocity.js` (`tileToScreen` 2:1 diamond, `TILE_W=64`/`TILE_H=32`, `draw()`, painter order) |
| Manifest-driven asset pipeline | Working | `web/assets/manifest.json`, `web/js/assets.js` (`AssetLoader.load/getImage`) |
| Static building/tile sprites | Partial | `web/assets/tiles/ground.png`, `sprites/{factory_dirty,factory_clean,smog,player_marker,district}.png` (6 flat 64² PNGs) |
| Pixel-style particle effects | Working | `web/js/effects.js` (`particleBurst`, `screenFlash`, `glowPulse`); `isocity.js` `triggerAbatementEffect/OffsetEffect/YearTransition` |
| Tokenized design system | Working | `web/css/style.css` (`:root` tokens, beveled components), `@font-face` Press Start 2P |
| Reactive feedback (smog∝emissions, compliance tint) | Working | `isocity.js` `drawPlotStructure`, sky/tint |
| **Bright, saturated Kairosoft palette** | **Missing** | current tokens muted-earth (`--bg:#f7f1e7`, `--accent:#3b6f76`) |
| **Characterful / varied building sprites** | **Missing** | only dirty/clean factory + district; flat, low personality |
| **Animated chibi citizens / characters** | **Missing** | no people, no frame animation (only `drawImage` of single frames) |
| **Floating feedback juice (coins/emotes/pop-ups)** | **Missing** | only particle bursts; no number/emote popups |
| **Rounded Kairosoft UI chrome + rounded pixel font** | **Missing** | beveled panels + blocky Press Start 2P |
| Sprite-sheet frame animation capability | Missing | renderer blits single static images |

---

## Target State

> An in-game scene that reads unmistakably as a **Kairosoft-style cute tycoon**: a bright, saturated, cheerful city on the (isometric) grid, with **outlined, characterful, varied buildings**; **little animated chibi citizens/workers** milling around and reacting; **floating feedback** (coins on income, reaction emotes/😊😡 over buildings, "+XP"/"-penalty" pop-ups) on every meaningful event; and a **rounded, friendly UI** (gradient panels, cute icons, notification bubbles, a rounded pixel font). Built on the current isometric renderer and asset/effects/CSS systems.

---

## Gap Analysis

### GAP-01: No characterful / varied building sprite set

**Severity:** CRITICAL — Kairosoft's identity *is* its cute, outlined, personable buildings; the current flat tiles can't read as Kairosoft no matter the palette.

**Current state:** `web/assets/sprites/` has 6 plain 64² PNGs (`factory_dirty/clean`, `smog`, `player_marker`, `district`, `ground`); `isocity.js` `drawPlotStructure` swaps dirty↔clean only. No building variety, weak outlines, low detail.

**What's needed:**
- A re-arted, **outlined, saturated, charming** building set with **variety** (multiple sector/company building types, upgrade tiers, decorations) sized for the 64×32 iso footprint.
- Manifest entries for the new sprites; `drawPlotStructure` selects by company/sector/state.

**Existing assets to reuse:**
- `web/assets/manifest.json` + `AssetLoader` — drop in new sprites, no loader change.
- `isocity.js` `drawPlotStructure` (sprite-selection point) and `buildPlots` (per-company plot data).

**Effort estimate:** 1 multi-phase plan (3 phases): source/author art → manifest+wiring → variety/upgrade logic.

---

### GAP-02: No animated chibi citizens / characters (and no frame-animation capability)

**Severity:** CRITICAL — the signature Kairosoft "life" is little people walking and emoting; their absence is the most glaring miss, and the renderer can't animate sprites yet.

**Current state:** `isocity.js` only blits **single static images** (`ctx.drawImage` of one frame); there are no character sprites and no sprite-sheet/frame stepping. The RAF loop exists but drives only particles + tint, not sprite animation.

**What's needed:**
- A lightweight **sprite-sheet frame-animation** capability in `isocity.js` (frame index from `time`/elapsed; row/col from a sheet).
- **Chibi citizen sprites** (walk cycles, idle, reaction) wandering plots/paths; density/behavior tied to game state (busy when thriving, fleeing/coughing under high smog).

**Existing assets to reuse:**
- `isocity.js` RAF loop, `tileToScreen`, particle update pattern (reuse for citizen movement), reduced-motion fallback, DPR handling.
- `AssetLoader`/manifest for the new sheets.

**Effort estimate:** 1 multi-phase plan (3–4 phases): frame-anim core → citizen sprites/movement → state-reactive behavior.

---

### GAP-03: Muted palette + beveled UI/blocky font (not bright Kairosoft chrome)

**Severity:** HIGH — palette and UI tone are half the Kairosoft read; current scheme is deliberately muted-retro, the wrong mood.

**Current state:** `web/css/style.css` `:root` is earthy/muted (`--bg:#f7f1e7`, `--accent:#3b6f76`, `--green:#5a8f4e`), components are **beveled** (hard 3-D edges), font is **Press Start 2P** (blocky). Kairosoft is bright/saturated with **rounded** gradient panels, cute icons, and a softer rounded pixel font.

**What's needed:**
- Retune tokens to a brighter, more saturated, cheerful palette (keep semantic roles).
- Restyle components to **rounded** panels with subtle gradients + cute iconography + notification bubbles; swap/keep a friendlier rounded pixel font.
- Update `docs/design-language.md`.

**Existing assets to reuse:**
- Fully tokenized `:root` (swap values → propagates everywhere); existing component classes; `@font-face` mechanism; `docs/design-language.md`.

**Effort estimate:** 1 multi-phase plan (2–3 phases): tokens → component/font restyle → doc.

---

### GAP-04: No floating feedback juice (coins / reaction emotes / pop-ups)

**Severity:** HIGH — Kairosoft game-feel is constant little payoffs; CarbonSim only emits abstract particle bursts.

**Current state:** `effects.js` does `particleBurst`/`screenFlash`/`glowPulse`; `isocity.js` triggers green/cyan bursts on abatement/offset. No floating numbers, coins, or emote bubbles over plots.

**What's needed:**
- A **floating-feedback layer**: rising coin/number pop-ups on income/cost, reaction emotes (😊/😡/💢/💚) over buildings on compliance/abatement/penalty events, toast-style "+XP"/"+level" flourishes.
- Hook into existing decision/year events (`doDecision`, `doAdvanceYear`, compliance changes in `game.html`).

**Existing assets to reuse:**
- `effects.js` particle/DOM-overlay machinery; `isocity.js` `triggerAbatementEffect/OffsetEffect/YearTransition` (extend); existing toast system in `game.html`.

**Effort estimate:** 1 multi-phase plan (2–3 phases): floating-number/coin layer → emote bubbles → wire to events.

---

## Second-Tier Gaps

| Gap | Severity | Summary | Existing Assets |
|---|---|---|---|
| GAP-05: Asset sourcing & licensing (Kairosoft-*style*, not Kairosoft assets) | MEDIUM | Source/author CC0/CC-BY cute-iso art that evokes the style **without copying Kairosoft's IP**; track in `ATTRIBUTIONS.md` | existing `ATTRIBUTIONS.md`, manifest pipeline |
| GAP-06: Optional 3/4 oblique reprojection | LOW | Authentic Kairosoft is oblique, not true iso; reproject `tileToScreen` + redraw sprites if desired later | `isocity.js` `tileToScreen` |
| GAP-07: Performance with many animated citizens | MEDIUM | Cap/scale citizen + particle counts; preserve 30fps + reduced-motion | `isocity.js` DPR cap, particle cap, `drawStatic` fallback |
| GAP-08: Cross-screen consistency (coop/summary) | LOW | Apply new art/juice to `coop.html`/`summary.html`, not just `game.html` | shared `isocity.js`, `style.css` |

---

## Recommended Sprint Sequencing

| Priority | Gap | Rationale |
|---|---|---|
| Sprint 1 | GAP-03 (palette + rounded UI/font) | Cheapest, highest-visibility — pure CSS token/component restyle instantly shifts the whole app to the bright Kairosoft mood and sets the target palette for the art. |
| Sprint 2 | GAP-01 (characterful building art) + GAP-05 (sourcing) | The biggest single visual lever; needs the Sprint-1 palette to match against. Source/author art under the right license. |
| Sprint 3 | GAP-02 (animated citizens + frame-anim core) | The signature "life"; depends on the frame-animation capability and benefits from finished buildings to populate. |
| Sprint 4 | GAP-04 (floating feedback juice) + GAP-07/08 | Game-feel payoffs + perf hardening + apply across all screens. |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| IP: copying Kairosoft's actual sprites/look-too-closely | Legal/originality issue | M | Build a *style-inspired* original set under CC0/CC-BY; track in `ATTRIBUTIONS.md`; don't reuse Kairosoft assets |
| Art consistency across a larger sprite set | Visual incoherence | M | Define a sprite spec (palette, outline, light angle, 64×32 footprint) in `docs/design-language.md` before mass production |
| Performance with many animated citizens | Jank on mobile/low-end | M | Reuse `isocity.js` particle/DPR caps; cap citizen count; honor reduced-motion (`drawStatic`) |
| Projection authenticity (true iso vs Kairosoft oblique) | Slightly "off" feel | L | Accept iso for now (GAP-06 optional); draw buildings slightly front-facing to approximate |
| Scope/art effort underestimated | Slips | M | Sprint-gate; palette/UI (S1) delivers value even if art slips; consider asset packs to reduce authoring |

---

## Suggested Next Step

Review this report, then invoke `/plan` per sprint — start with **GAP-03 (palette + rounded UI/font)** for an immediate, low-risk Kairosoft mood shift, then **GAP-01 (building art)**. Decide the asset strategy (author vs. CC0/CC-BY packs) up front (GAP-05) since it gates the art sprints. Grounding research: `research/2026-06-14_kairosoft-visual-style.md`.
