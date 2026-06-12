---
title: "Sprint 4 — Retro Reskin Across All Screens & Modes (GAP-05)"
date: "2026-06-13"
status: "draft"
request: "Create multiple multi-phase plans from reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md — one per recommended sprint. This is Sprint 4: reskin all screens & modes."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md"
---

# Plan: Sprint 4 — Retro Reskin Across All Screens & Modes

## Objective
Make the retro tycoon look consistent end-to-end. Sprint 2's token swap propagates the palette automatically, but each of the four screens carries inline styles and bespoke markup that must be swept by hand, and the isometric view (Sprint 3) must be wired into multiplayer/co-op — not just solo. After this sprint, landing page, solo game, co-op, and summary all read as one coherent retro product, and the legacy `skyline.js` is removed.

## Context Snapshot
- **Current state:** Four screens with inline `<style>` blocks and cyberpunk classes — `web/index.html` (196 lines), `web/game.html` (756 lines, inline skyline styles at 9-13, XP HUD inline at 41-54), `web/coop.html` (434 lines), `web/summary.html` (271 lines). Sprint 3 leaves the iso renderer behind a feature flag and `skyline.js` pending removal.
- **Desired state:** All four screens audited and consistent in the retro system; inline styles reconciled with tokens; iso city wired into every mode by default; `skyline.js` deleted.
- **Key repo surfaces:** `web/index.html`, `web/game.html`, `web/coop.html`, `web/summary.html`, `web/css/style.css` (retro tokens), `web/js/isocity.js` (Sprint 3), `web/js/skyline.js` (to remove).
- **Out of scope:** New iso-renderer features (Sprint 3 scope), SFX/perf hardening (Sprint 5).

## Research Inputs
- `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md` — GAP-05 (MEDIUM): reskin breadth across all 4 screens + 3 modes; largely propagates via Sprint-2 tokens but each screen needs review for inline styles and per-mode wiring.

## Assumptions and Constraints
- **ASM-001:** Sprint 2 tokens are live; most visual shift is already applied — this sprint is a consistency sweep plus per-mode iso wiring, not a re-design.
- **ASM-002:** Sprint 3 delivered `isocity.js` behind a flag with confirmed parity; flipping the default is safe here.
- **CON-001:** Preserve existing functional wiring (game IDs, WebSocket/lobby flows in `coop.html`, save/load modals in `game.html:69-96`, summary rankings) — visual-only changes.
- **CON-002:** Keep `prefers-reduced-motion`, `:focus-visible`, and aria attributes (e.g. `aria-hidden` on the canvas, `game.html:57`) intact.
- **DEC-001:** `skyline.js` is removed once `isocity` is the default everywhere (full reskin, not a dual-skin toggle).

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Landing/lobby retro sweep | Sprints 2-3 | `index.html` consistent |
| PHASE-02 | Game + co-op sweep, iso wired per mode | PHASE-01 | `game.html`, `coop.html` consistent + iso default |
| PHASE-03 | Summary sweep + cross-screen audit + skyline removal | PHASE-02 | `summary.html` consistent, `skyline.js` deleted |

## Detailed Phases

### PHASE-01 - Landing & Lobby Sweep
**Goal**
Bring the entry screen fully into the retro system.

**Tasks**
- [ ] TASK-01-01: Audit `web/index.html` inline `<style>` and classes; replace neon-specific values with tokens; apply pixel display font to the title/branding.
- [ ] TASK-01-02: Reskin landing controls (start solo, create/join room) using the Sprint-2 beveled `.btn`/`.input` chrome.
- [ ] TASK-01-03: Verify any join/create-room flow markup still functions (IDs/handlers unchanged).

**Files / Surfaces**
- `web/index.html` — sweep.

**Dependencies**
- Sprint 2 (tokens), Sprint 3 (renderer available)

**Exit Criteria**
- [ ] `index.html` shows no neon remnants and matches the retro chrome; entry flows still work.

**Phase Risks**
- **RISK-01-01:** Inline overrides silently beat tokens → grep each file's `<style>`/`style=` for hardcoded neon hex and replace with `var(--*)`.

### PHASE-02 - Game & Co-op Sweep + Per-Mode Iso
**Goal**
Make the two gameplay screens consistent and run the iso city by default in solo, multiplayer, and co-op.

**Tasks**
- [ ] TASK-02-01: Sweep `web/game.html` — reconcile inline skyline-container styles (9-13) and the XP HUD inline styles (41-54) with tokens; pixel font on headers/badges.
- [ ] TASK-02-02: Sweep `web/coop.html` (434 lines) — lobby, participant list, host controls into retro chrome; preserve WebSocket-driven elements.
- [ ] TASK-02-03: Flip the Sprint-3 feature flag default to `isocity` in `game.html` and `coop.html`; confirm overlays (`#skylineLabel`, `#skylineCompliance`) and triggers fire in each mode.
- [ ] TASK-02-04: Confirm modals (save/load/card in `game.html:69-96`) render correctly in retro chrome.

**Files / Surfaces**
- `web/game.html`, `web/coop.html` — sweep + iso default.

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] Solo, multiplayer, and co-op all render the iso city by default in retro chrome; gameplay/lobby functions unaffected.

**Phase Risks**
- **RISK-02-01:** Co-op init differs from solo → verify `coop.html`'s renderer init independently rather than copying `game.html` assumptions.

### PHASE-03 - Summary Sweep, Cross-Screen Audit & Cleanup
**Goal**
Finish the summary screen, prove consistency across all four, and remove the legacy renderer.

**Tasks**
- [ ] TASK-03-01: Sweep `web/summary.html` (271 lines) — rankings/leaderboard and end-game stats into retro chrome; pixel font on headline.
- [ ] TASK-03-02: Cross-screen consistency audit: same tokens, fonts, button styles, spacing across `index`/`game`/`coop`/`summary`.
- [ ] TASK-03-03: Delete `web/js/skyline.js` and remove its `<script src>` references; confirm no remaining importers.

**Files / Surfaces**
- `web/summary.html` — sweep.
- `web/js/skyline.js` — delete; all four HTML files — remove references.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] All four screens are visually consistent; `skyline.js` is gone and nothing references it; app runs clean.

**Phase Risks**
- **RISK-03-01:** A screen still references `skyline.js` after deletion → grep all HTML for `skyline` before removing.

## Verification Strategy
- **MANUAL-001:** Walk the full flow — landing → start/create → solo game → co-op lobby+game → summary — confirming one coherent retro look and the iso city in every mode.
- **MANUAL-002:** Reduced-motion + keyboard-focus pass on all four screens.
- **TEST-001:** Run the existing suite (`engine/tests`, `server/tests`) to confirm visual-only changes didn't break API/engine behavior; grep confirms zero `skyline` references remain.

## Risks and Alternatives
- **RISK-001:** Hidden inline neon styles cause one-off inconsistencies → systematic per-file grep for hardcoded hex during each sweep.
- **ALT-001:** Keeping `skyline.js` as a fallback toggle was rejected — the decision is a single full reskin, and dual renderers add maintenance.

## Grill Me
No open clarification questions. (Full reskin across all modes was fixed in the gap analysis; iso parity and flag come from Sprint 3.)

## Suggested Next Step
Execute PHASE-01 → PHASE-03; then proceed to Sprint 5 (`2026-06-13-retro-sfx-perf-polish-plan.md`).
