---
title: "Sprint 2 — Retro Design Token System & Chrome (GAP-02)"
date: "2026-06-13"
status: "draft"
request: "Create multiple multi-phase plans from reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md — one per recommended sprint. This is Sprint 2: retro design tokens & chrome."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md"
---

# Plan: Sprint 2 — Retro Design Token System & Chrome

## Objective
Replace the current dark cyberpunk-neon visual identity with a retro **isometric tycoon** identity — bright/earthy palette, pixel display font, chunky beveled chrome — by swapping the `:root` token values and reskinning the shared component classes. Because the CSS is already fully tokenized, this propagates across every screen without touching markup, establishing the look the renderer (Sprint 3) will match.

## Context Snapshot
- **Current state:** `web/css/style.css:1-8` defines neon tokens (`--bg:#0d0d0d`, `--accent:#00f5ff`, `--green:#39ff14`, `--glow` glow shadow, `Segoe UI`/`Cascadia Code` fonts). `docs/design-language.md` codifies a "Dark cyberpunk-inflected dashboard." Components (`.card`, `.btn`, `.badge`, `.input`, XP HUD) use translucent panels + glow + cubic-bezier lifts — none of the beveled tycoon chrome the target needs.
- **Desired state:** `:root` carries a retro tycoon palette + pixel font; `.card`/`.btn`/`.badge`/`.input` and the HUD render as raised/inset beveled panels and buttons; `docs/design-language.md` describes the retro system accurately.
- **Key repo surfaces:** `web/css/style.css` (518 lines, `:root` at 1-8), `web/css/animations.css` (347 lines), `docs/design-language.md`, the pixel font delivered by Sprint 1 (`/assets/fonts`).
- **Out of scope:** Per-screen HTML edits and inline styles (Sprint 4), the isometric canvas itself (Sprint 3), SFX (Sprint 5).

## Research Inputs
- `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md` — GAP-02 (CRITICAL): visual identity is the opposite of the target; notes the CSS is fully tokenized on `:root`, so swapping values + ~6 component classes propagates everywhere. Depends on the pixel font from Sprint 1.

## Assumptions and Constraints
- **ASM-001:** The pixel/bitmap display font ships from Sprint 1 at `/assets/fonts`; the body/stat font stays readable (pixel font for headers/labels only, to protect dense-stat legibility per gap-analysis RISK).
- **ASM-002:** Token names stay the same (`--bg`, `--accent`, `--green`, `--red`, `--orange`, `--radius`, `--font`, `--mono`, `--glow`) so no consumer markup changes; only values + a few new tokens (e.g. `--bevel-light`, `--bevel-dark`) are added.
- **CON-001:** Maintain accessibility: contrast ≥ 4.5:1 body / 3:1 large; keep `:focus-visible` rules (`style.css:53,62`); color never the sole indicator (badges keep text).
- **CON-002:** No CSS framework; hand-rolled beveled edges via layered `box-shadow`/`border` (raised vs. pressed), not images where avoidable.
- **DEC-001:** `--glow` is repurposed/neutralized rather than deleted, since consumers reference it (`style.css:49`, etc.).

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Retro token palette + font wired into `:root` | Sprint 1 font | New `:root` values + `@font-face` |
| PHASE-02 | Reskin shared components to beveled retro | PHASE-01 | Updated `.card`/`.btn`/`.badge`/`.input`/HUD styles |
| PHASE-03 | Rewrite design-language doc | PHASE-02 | Accurate `docs/design-language.md` |

## Detailed Phases

### PHASE-01 - Retro Tokens & Font
**Goal**
Establish the retro palette and typography at the token layer so the whole app shifts identity at once.

**Tasks**
- [ ] TASK-01-01: Add an `@font-face` for the Sprint-1 pixel font (served from `/assets/fonts`) and a fallback body font; introduce `--font-display` for the pixel face while keeping `--font`/`--mono` readable.
- [ ] TASK-01-02: Replace neon palette values in `web/css/style.css:1-8` with a tycoon palette (warmer/earthier bg, saturated-but-not-neon accent, distinct compliant/shortfall/warning hues that still satisfy the semantic color rules in `design-language.md`).
- [ ] TASK-01-03: Add bevel tokens (`--bevel-light`, `--bevel-dark`, `--radius` reduced for chunkier corners) for raised/inset chrome.
- [ ] TASK-01-04: Repurpose `--glow` to a subtle/neutral value (don't delete — consumers reference it).

**Files / Surfaces**
- `web/css/style.css:1-8` — token block.
- `web/assets/fonts/*` — provided by Sprint 1.

**Dependencies**
- Sprint 1 (pixel font + `/assets` mount)

**Exit Criteria**
- [ ] Loading any screen shows the new palette + pixel display font on headings with no markup edits.
- [ ] Contrast spot-checks pass (≥4.5:1 body / 3:1 large).

**Phase Risks**
- **RISK-01-01:** Pixel font hurts stat readability → restrict `--font-display` to headers/labels; keep stats on the readable body/mono font.

### PHASE-02 - Beveled Component Reskin
**Goal**
Turn the shared components from neon-translucent into chunky tycoon chrome.

**Tasks**
- [ ] TASK-02-01: Reskin `.card` (`style.css:20-30`) to raised beveled panels (layered light/dark borders), drop the glow hover for a pressed/raised feel.
- [ ] TASK-02-02: Reskin `.btn`/`.btn-primary`/`.btn-danger` (`style.css:32-53`) as raised buttons with an inset pressed `:active` state; preserve `:disabled` and `:focus-visible`.
- [ ] TASK-02-03: Reskin `.badge` (`style.css:66+`), `.input`/`select` (`style.css:55-63`), and the XP HUD (in `game.html` inline + classes) to match.
- [ ] TASK-02-04: Reconcile `web/css/animations.css` — keep transitions that read as retro; tone down neon-specific glow animations.

**Files / Surfaces**
- `web/css/style.css:20-70+` — component classes.
- `web/css/animations.css` — animation reconciliation.

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] Cards, buttons, badges, inputs, and HUD render as beveled retro chrome across existing screens.
- [ ] `:focus-visible` and `:disabled` states remain visually clear.

**Phase Risks**
- **RISK-02-01:** Bevel box-shadows look noisy at small sizes → standardize one raised + one inset recipe via tokens and reuse.

### PHASE-03 - Rewrite Design Language Doc
**Goal**
Make the canonical design doc describe the retro system (it currently misdescribes the product).

**Tasks**
- [ ] TASK-03-01: Rewrite `docs/design-language.md` Visual Direction, Color Tokens, Typography, and Component Library sections for the retro tycoon system; update the Signature Visual section to reference the isometric city (forward-link to Sprint 3).
- [ ] TASK-03-02: Keep the Accessibility and Semantic Color Rules sections, updated to the new palette values.

**Files / Surfaces**
- `docs/design-language.md` — full rewrite of style sections.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] `docs/design-language.md` matches the shipped tokens/components and no longer says "cyberpunk."

**Phase Risks**
- **RISK-03-01:** Doc drifts from code again → reference actual token names/values so it's checkable against `style.css`.

## Verification Strategy
- **MANUAL-001:** Load `/`, `/game.html`, `/coop.html`, `/summary.html` and confirm the retro identity is consistent (tokens propagate); no neon remnants on shared components.
- **MANUAL-002:** Toggle keyboard focus through buttons/inputs to confirm `:focus-visible` and contrast.
- **OBS-001:** Run an accessibility contrast check (axe/Lighthouse) on the new palette; record results in the design doc.

## Risks and Alternatives
- **RISK-001:** Inline styles in the HTML files (e.g. `game.html:9-13`, XP HUD) override tokens and look off → flagged for Sprint 4's per-screen sweep; note any blockers here.
- **ALT-001:** A separate `retro.css` layered over `style.css` was rejected — editing the single tokenized source is cleaner and avoids dual-skin maintenance (the full-reskin decision, not a theme toggle).

## Grill Me
No open clarification questions. (Full reskin across all modes and the tycoon aesthetic were fixed in the gap analysis.)

## Suggested Next Step
Execute PHASE-01 → PHASE-03; then proceed to Sprint 3 (`2026-06-13-isometric-renderer-plan.md`).
