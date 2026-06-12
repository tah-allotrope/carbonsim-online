# Gap Analysis: Retro Isometric Tycoon Interface for CarbonSim

**Date:** 2026-06-13
**Scope:** Reskin the existing carbon-market game (solo + multiplayer + co-op) into a playable retro **isometric tycoon** browser experience — SimCity 2000 / Theme Hospital visual register — using free assets (CC-BY/attribution acceptable) and the current vanilla-JS + canvas + FastAPI stack. No new frontend framework.
**Status:** Draft for Review

---

## Executive Summary

The product underneath is strong and finished: a working carbon-market engine, a FastAPI backend serving solo/multiplayer/co-op, four playable HTML screens, procedural Web-Audio SFX, a gamification layer, and a canvas-based signature visual with a proper animation loop and reduced-motion fallback. **What does not exist is anything isometric, any pixel/retro art, or any asset pipeline** — the current look is a deliberately *opposite* aesthetic (dark cyberpunk neon). This is a reskin-and-renderer effort, not a rebuild: the data plumbing, game loop, audio, and screen structure all carry over. There are **2 CRITICAL gaps** (isometric renderer; retro visual identity) and **2 HIGH gaps** (asset pipeline; engine-state→tile mapping). One-line recommendation: land the asset pipeline first (cheap, unblocks all), then the retro token system, then build the isometric renderer by extending — not replacing — `skyline.js`.

---

## Current Capabilities (What We Have)

| Capability | Status | Key Surfaces |
|---|---|---|
| Carbon-market game engine | Mature | `engine/engine.py`, `engine/constants.py`, `engine/solo.py` |
| Backend API (solo + multiplayer + co-op) | Mature | `server/main.py`, `server/routes/game.py`, `server/routes/coop.py` |
| Playable frontend screens (4) | Working | `web/index.html`, `web/game.html`, `web/coop.html`, `web/summary.html` |
| Signature canvas visual (animation loop, particles, reduced-motion) | Working | `web/js/skyline.js` (312 lines) |
| Design system (dark cyberpunk neon) | Mature | `docs/design-language.md`, `web/css/style.css` (518 lines), `web/css/animations.css` |
| Procedural audio SFX (Web Audio oscillators) | Working | `web/js/audio.js` (406 lines, synth-based) |
| Visual effects (DOM particle bursts) | Working | `web/js/effects.js` |
| Gamification (XP, levels, streaks) | Working | `web/js/progression.js`, XP HUD in `game.html` |
| Static asset serving | Partial | `server/main.py:49-51` mounts **only** `/css` and `/js` |
| **Isometric rendering** | **Missing** | — (current skyline is side-elevation 2D) |
| **Pixel-art / tileset assets** | **Missing** | no `web/assets`, `web/img`, `web/fonts`, or `web/tiles` directory exists |
| **Retro UI chrome / skin** | **Missing** | tokens are neon-on-black, not tycoon-era |

---

## Target State

> A browser-playable carbon-market game whose primary view is an **isometric pixel-art city** (companies as plots/factories, abatement as visible building upgrades, emissions as smog over tiles) wrapped in a **retro tycoon HUD** — chunky beveled panels, a pixel/bitmap font, chiptune-flavored SFX. The retro look is THE look across **all** screens and modes (solo game, multiplayer lobby, co-op, summary). Built on the existing vanilla-JS + canvas frontend and FastAPI backend; free assets with attribution tracked in-repo.

---

## Gap Analysis

### GAP-01: No isometric renderer — current signature visual is side-elevation 2D

**Severity:** CRITICAL — the defining feature of the target (an isometric tycoon city) does not exist in any form. Without it, the result is not "isometric tycoon," just a recolored dashboard.

**Current state:** `web/js/skyline.js` draws a **flat front-on skyline**: buildings are axis-aligned `fillRect`s (`drawBuildings()`, lines 154-190) standing on a 1-D ground line (`drawGround()`, 213-226). There is no tile grid, no `(row,col)→screen` isometric projection, no depth sorting beyond a height sort (line 69), and no sprite blitting (everything is procedural `fillRect`/`arc`).

**What's needed:**
- An isometric projection helper (`tileToScreen(col,row)` with 2:1 diamond math) and a tile grid model.
- A draw order that paints back-to-front (painter's algorithm by `col+row`).
- Sprite/tile blitting from loaded images (`drawImage`) rather than only procedural shapes.
- Tile/building layering: ground tile → structure sprite → overlay (smog/upgrade icon).

**Existing assets to reuse:**
- `skyline.js`'s whole runtime scaffold is reusable as-is: the `requestAnimationFrame` loop with 30fps throttle (`loop()`, 98-105), DPR-aware `resize()` (32-42), `prefers-reduced-motion` branch + `drawStatic()` fallback (24-29, 119-124), the particle system (`spawnParticles`/`updateParticles`/`drawParticles`, 228-264), and the public trigger API (`triggerAbatementEffect`, `triggerOffsetEffect`, `triggerYearTransition`). Build the iso renderer as a sibling module (e.g. `web/js/isocity.js`) that keeps this loop/particle/lifecycle structure and swaps the draw functions.

**Effort estimate:** 1 multi-phase plan (3-4 phases): projection + grid → sprite blitting → depth/overlay layering → wire triggers/particles to tiles.

---

### GAP-02: Visual identity is the opposite of retro tycoon

**Severity:** CRITICAL — every screen currently reads as dark neon cyberpunk; the target is bright, chunky, tycoon-era. This is a wholesale identity change, not a tweak.

**Current state:** `web/css/style.css:1-8` defines the token palette as `--bg:#0d0d0d`, `--accent:#00f5ff` (cyan), `--green:#39ff14`, neon `--glow` shadows, with `Segoe UI` / `Cascadia Code` fonts. `docs/design-language.md` codifies this as "Dark cyberpunk-inflected dashboard." Components (cards, buttons, badges — `style.css:20-70+`) use translucent panels, glow shadows, and cubic-bezier lifts — none of the beveled/raised tycoon chrome the target calls for.

**What's needed:**
- A new token set: tycoon palette (earthy/saturated, not neon), a pixel/bitmap display font + readable body font, removal of neon glow in favor of hard beveled borders (raised/inset 3-D edges via box-shadow tricks or border-image).
- Retro component variants: beveled panels, raised buttons with pressed states, a HUD bar styled as a control panel.
- A rewritten `docs/design-language.md` describing the retro system (the current doc actively misdescribes the target).

**Existing assets to reuse:**
- The CSS is **already fully tokenized** via CSS custom properties on `:root` — the entire app reads from `--bg`, `--accent`, `--radius`, `--font`, etc. Swapping token *values* and restyling ~6 component classes propagates everywhere without touching markup. The token architecture is the reusable asset; only the values and component skins change.
- `animations.css` and the existing focus-visible/accessibility rules (`style.css:53,62`) carry over.

**Effort estimate:** 1 multi-phase plan (3-4 phases): token swap → component reskin (cards/buttons/badges/HUD) → font integration → design-language doc rewrite.

---

### GAP-03: No free-asset pipeline (no assets, no `/assets` mount, no pixel font)

**Severity:** HIGH — isometric tiles, building sprites, and a pixel font are prerequisites for GAP-01/02, and there is currently nowhere to put them or serve them from.

**Current state:** No `web/assets`, `web/img`, `web/tiles`, or `web/fonts` directory exists (verified). `server/main.py:49-51` mounts only `/css` and `/js` as `StaticFiles`; there is no `/assets` route, so even if assets were added they would not be served. No attributions/credits file exists.

**What's needed:**
- Source free isometric tilesets + building sprites + a pixel/bitmap font (CC-BY acceptable per decision) — e.g. Kenney isometric packs (CC0), OpenGameArt isometric tiles, a free bitmap font (Press Start 2P / public-domain VGA font).
- Add a `web/assets/` directory and mount it: `app.mount("/assets", StaticFiles(directory=...))` in `server/main.py` next to the existing mounts.
- A sprite atlas/manifest (JSON mapping tile names → coordinates) for the renderer to consume.
- An `ATTRIBUTIONS.md` / credits file tracking each asset's license + author.

**Existing assets to reuse:**
- The `StaticFiles` mount pattern at `server/main.py:49-51` is the exact template — add one line.
- `web/js/api.js` (44 lines) shows the existing fetch/loading conventions for wiring a manifest load.

**Effort estimate:** 1 short plan (2-3 phases): source + license-vet assets → add mount + directory + manifest → attributions file.

---

### GAP-04: No mapping from engine state to an isometric city

**Severity:** HIGH — a tycoon view is only meaningful if it reflects game state. The current skyline binds state loosely and partly randomly; an iso city needs deterministic, legible mapping.

**Current state:** `skyline.js:44-70` (`generateBuildings`) assigns building width/height/position with `Math.random()` and only loosely ties a building to the player. `update(snapshot)` (72-96) reads real engine fields (`projected_emissions`, `allowances`, `compliance_gap`, `active_abatement_ids`, `abatement_menu`) but only to drive sky hue and one building's smoke. There is no stable per-company plot, no representation of abatement-as-upgrade, no offset/penalty/cash visualization on the map.

**What's needed:**
- A deterministic layout: each company → a fixed plot/tile (seeded by `company_id`, not `Math.random()`), stable across frames and reconnects.
- Visual encodings: emissions → smog tiles/density over a plot; active abatement → upgraded/cleaner building sprite; compliance shortfall → distressed plot; offsets/cash → HUD or plot badges.
- Multiplayer/co-op: render N players' plots and highlight the local player (the snapshot already exposes `leaderboard`/`companies`).

**Existing assets to reuse:**
- The `update(snapshot)` data-binding contract (`skyline.js:72-96`) already pulls the correct engine fields — reuse the field list and binding approach, replacing random geometry with a seeded deterministic map.
- `engine/engine.py` `export_session_data()` / company snapshot fields define the available state surface.

**Effort estimate:** Fold into GAP-01's plan as a dedicated phase, or 1 small standalone plan (2 phases) if scheduled separately.

---

## Second-Tier Gaps

| Gap | Severity | Summary | Existing Assets |
|---|---|---|---|
| GAP-05: Reskin breadth across all 4 screens + 3 modes | MEDIUM | `index.html`, `coop.html`, `summary.html` carry inline styles + cyberpunk classes; retro must reach lobby/co-op/summary, not just `game.html`. Largely propagates via GAP-02 tokens but each screen needs review. | Shared `style.css` tokens; consistent class usage across screens |
| GAP-06: Retro-ify SFX + effects | MEDIUM | `audio.js` is already procedural Web-Audio synth (perfect for chiptune) but voiced for the neon theme; `effects.js` uses DOM glow particles that should read as pixel bursts. | `web/js/audio.js` (oscillator synth, re-voiceable), `web/js/effects.js` particle API |
| GAP-07: Iso-renderer performance & a11y parity | LOW | An isometric sprite scene is heavier than `fillRect`s; must preserve the existing 30fps throttle, DPR handling, and reduced-motion static fallback, and keep mobile scaling sane. | `skyline.js` already implements throttle + DPR + `drawStatic()` reduced-motion path |

---

## Recommended Sprint Sequencing

| Priority | Gap | Rationale |
|---|---|---|
| Sprint 1 | GAP-03 (asset pipeline + `/assets` mount) | Cheapest, unblocks everything. Nothing visual can be built until tiles, sprites, and a pixel font are sourced, license-vetted, and servable. |
| Sprint 2 | GAP-02 (retro token system + chrome) | Establishes the visual identity via token swap; immediately visible across all screens, and sets the palette the renderer will match. Depends only on the pixel font from Sprint 1. |
| Sprint 3 | GAP-01 + GAP-04 (isometric renderer + state mapping) | The hard core. Build `isocity.js` reusing the `skyline.js` loop/particle/lifecycle scaffold; bind deterministically to engine snapshot. Depends on assets (S1) and palette (S2). |
| Sprint 4 | GAP-05 (reskin all screens/modes) | With tokens + renderer in place, sweep lobby/co-op/summary for consistency and wire the iso view into multiplayer/co-op. |
| Sprint 5 | GAP-06 + GAP-07 (SFX/effects re-voice + perf/a11y hardening) | Polish: chiptune SFX, pixel-burst effects, verify throttle/reduced-motion/mobile on the heavier renderer. |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Asset license drift (CC-BY attribution missed) | Legal/redistribution risk | M | Maintain `ATTRIBUTIONS.md` from Sprint 1; vet each asset's license before adding; prefer CC0 (Kenney) where possible |
| Isometric renderer perf on low-end/mobile | Jank, dropped frames | M | Reuse `skyline.js` 30fps throttle + DPR scaling; cap tile/particle counts; keep `drawStatic()` reduced-motion fallback as the floor |
| Scope creep — replacing the working skyline wholesale | Regression of a shipped feature | M | Build `isocity.js` as a sibling and feature-flag the swap; keep `skyline.js` until the iso view reaches parity |
| Engine-snapshot coupling breaks on field changes | Blank/incorrect city | L | Bind through the existing `update(snapshot)` field contract; add a defensive fallback when fields are absent (the current code already defaults) |
| Pixel font hurts readability of dense stats | Usability drop | M | Use pixel font for display/headers only; keep a readable body font for stats/tables; verify contrast ≥ 4.5:1 |
| Reskin diverges across the 4 screens | Inconsistent look | M | Drive everything from `:root` tokens (GAP-02); audit all four HTML files in Sprint 4 |

---

## Suggested Next Step

Review this report, then invoke `/plan` per sprint — start with **GAP-03 (asset pipeline)** since it unblocks the rest, then **GAP-02 (retro tokens)**, then the combined **GAP-01 + GAP-04 (isometric renderer + state mapping)** plan. Keep `activeContext.md` pointed at the active sprint as execution proceeds.
