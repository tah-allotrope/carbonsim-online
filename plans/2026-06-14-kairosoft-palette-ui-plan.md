---
title: "Kairosoft Sprint 1 — Bright Palette & Rounded UI/Font (GAP-03)"
date: "2026-06-14"
status: "draft"
request: "Multiple multi-phase plans from reports/2026-06-14-kairosoft-visual-style-gap-analysis.md — Sprint 1: bright palette + rounded UI/font."
plan_type: "multi-phase"
research_inputs:
  - "research/2026-06-14_kairosoft-visual-style.md"
  - "reports/2026-06-14-kairosoft-visual-style-gap-analysis.md"
---

# Plan: Kairosoft Sprint 1 — Bright Palette & Rounded UI/Font

## Objective
Shift CarbonSim's whole-app mood to bright, cheerful Kairosoft by retuning the CSS palette and replacing the beveled/blocky chrome with rounded, gradient, friendly UI. This is the cheapest, highest-visibility step and sets the target palette every later art sprint must match.

## Context Snapshot
- **Current state:** `web/css/style.css` `:root` is a muted retro-earth scheme (`--bg:#f7f1e7`, `--accent:#3b6f76`, `--green:#5a8f4e`), components use hard **beveled** edges (`--bevel-light/dark/shadow`), and the display font is the blocky **Press Start 2P** (`@font-face`, `/assets/fonts/PressStart2P-Regular.ttf`).
- **Desired state:** A brighter, more saturated, cheerful token palette; **rounded** panels/buttons/badges with subtle gradients, cute iconography, and notification-bubble styling; a friendlier rounded pixel display font. `docs/design-language.md` updated.
- **Key repo surfaces:** `web/css/style.css`, `web/css/animations.css`, `docs/design-language.md`, the four screens (`web/index.html`, `web/game.html`, `web/coop.html`, `web/summary.html`) which consume the tokens.
- **Out of scope:** Sprite/building art (Sprint 2), citizens (Sprint 3), feedback juice (Sprint 4), the isometric canvas rendering itself.

## Research Inputs
- `research/2026-06-14_kairosoft-visual-style.md` — Kairosoft = bright/saturated palette + rounded friendly UI; current scheme is the wrong (muted) mood; CSS is fully tokenized so a value swap propagates everywhere.
- `reports/2026-06-14-kairosoft-visual-style-gap-analysis.md` — GAP-03 (HIGH); cheapest high-impact lever; pure CSS.

## Assumptions and Constraints
- **ASM-001:** Token names stay stable (`--bg`, `--accent`, `--green`, `--red`, `--orange`, `--radius`, `--font`, `--mono`, etc.) so no consumer markup changes — only values + a few additions (e.g. `--radius-lg`, gradient stops).
- **CON-001:** Maintain accessibility: contrast ≥ 4.5:1 body / 3:1 large; keep `:focus-visible` states; color never the sole indicator (badges keep text).
- **CON-002:** No new build step (vanilla CSS); a new font must be a self-hosted `@font-face` served from `/assets/fonts` (the `/assets` mount already serves with `no-cache`).
- **DEC-001:** Full reskin, not a theme toggle (consistent with the existing single design system).

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Bright Kairosoft palette tokens | None | Retuned `:root` values |
| PHASE-02 | Rounded UI chrome + friendly font | PHASE-01 | Reskinned components + `@font-face` |
| PHASE-03 | Update design doc + cross-screen check | PHASE-02 | Accurate `docs/design-language.md` |

## Detailed Phases

### PHASE-01 - Bright Palette Tokens
**Goal**
Retune `:root` to a saturated, cheerful palette while preserving semantic roles.

**Tasks**
- [ ] TASK-01-01: Replace muted values in `web/css/style.css` `:root` with brighter Kairosoft-ish hues (sky/grass/sun accents) keeping `--bg`, `--accent`, `--green`, `--red`, `--orange`, `--text`, `--muted` semantics.
- [ ] TASK-01-02: Add `--radius-lg` (rounded panels) and gradient-stop tokens for panel/button fills.
- [ ] TASK-01-03: Spot-check contrast (≥4.5:1 body / 3:1 large) and adjust.

**Files / Surfaces**
- `web/css/style.css` `:root` block — token values.

**Dependencies**
- None

**Exit Criteria**
- [ ] All four screens visibly shift to the brighter palette with no markup edits; contrast checks pass.

**Phase Risks**
- **RISK-01-01:** Over-saturation hurts text legibility → keep text/background contrast within thresholds; reserve the loudest hues for accents/buttons.

### PHASE-02 - Rounded Chrome + Friendly Font
**Goal**
Make components read as cute/rounded Kairosoft UI.

**Tasks**
- [ ] TASK-02-01: Restyle `.card`/`.btn`/`.badge`/`.input` to **rounded** corners + subtle gradients; replace hard bevel shadows with soft rounded shadows.
- [ ] TASK-02-02: Add a rounded pixel **display** font via `@font-face` (served from `/assets/fonts`); apply to headers/labels only; keep a readable body/mono font for dense stats.
- [ ] TASK-02-03: Add a reusable "notification bubble" style (speech-bubble pill) for in-game pop-ups (used by Sprint 4).
- [ ] TASK-02-04: Reconcile `web/css/animations.css` so transitions feel bouncy/cheerful, not neon.

**Files / Surfaces**
- `web/css/style.css` — component classes, `@font-face`.
- `web/assets/fonts/` — new font (track license in `ATTRIBUTIONS.md`).
- `web/css/animations.css` — transition reconciliation.

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] Cards/buttons/badges/inputs render rounded with gradients; display font applied to headers; `:focus-visible`/`:disabled` intact.

**Phase Risks**
- **RISK-02-01:** New font hurts stat readability → display font for headers/labels only; stats stay on readable mono.

### PHASE-03 - Design Doc + Cross-Screen Check
**Goal**
Document the Kairosoft system and confirm consistency.

**Tasks**
- [ ] TASK-03-01: Rewrite the relevant `docs/design-language.md` sections (palette, typography, components) for the Kairosoft system; define the **sprite spec placeholder** (palette/outline/light angle/64×32) that Sprint 2 will fill.
- [ ] TASK-03-02: Walk `index`/`game`/`coop`/`summary`, fixing any inline styles that fight the tokens.

**Files / Surfaces**
- `docs/design-language.md`; the four HTML screens.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] Doc matches shipped tokens/components; all four screens visually consistent.

**Phase Risks**
- **RISK-03-01:** Inline neon/earth hex in HTML overrides tokens → grep each screen's `<style>`/`style=` for hardcoded hex.

## Verification Strategy
- **MANUAL-001:** Load all four screens; confirm bright rounded Kairosoft mood and consistency.
- **MANUAL-002:** Keyboard-focus pass + axe/Lighthouse contrast check on the new palette.
- **TEST-001:** Run `pytest` (should be unaffected — frontend-only) to confirm no accidental breakage.

## Risks and Alternatives
- **RISK-001:** Palette set now may clash with Sprint-2 sprite art → define the sprite color spec in PHASE-03 so art is authored to the palette.
- **ALT-001:** A separate `kairosoft.css` overlay was rejected — editing the single tokenized source avoids dual-skin maintenance.

## Grill Me
1. **Q-001:** Keep Press Start 2P or adopt a rounded pixel display font (e.g. a CC/OFL face)?
   - **Recommended default:** Add a softer rounded pixel font for display/headers; keep a readable mono for stats.
   - **Why this matters:** Drives PHASE-02 font work + an asset/license entry.
   - **If answered differently:** "Keep Press Start 2P" removes TASK-02-02's font swap (rounding via CSS only).

## Suggested Next Step
Answer Q-001, then execute PHASE-01 → PHASE-03; proceed to Sprint 2 (`2026-06-14-kairosoft-building-art-plan.md`).
