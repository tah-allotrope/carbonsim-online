---
title: "Kairosoft Sprint 4 — Floating Feedback Juice + Perf & Cross-Screen (GAP-04/07/08)"
date: "2026-06-14"
status: "draft"
request: "Multiple multi-phase plans from reports/2026-06-14-kairosoft-visual-style-gap-analysis.md — Sprint 4: floating feedback juice + perf/cross-screen."
plan_type: "multi-phase"
research_inputs:
  - "research/2026-06-14_kairosoft-visual-style.md"
  - "reports/2026-06-14-kairosoft-visual-style-gap-analysis.md"
---

# Plan: Kairosoft Sprint 4 — Floating Feedback Juice + Perf & Cross-Screen

## Objective
Add the constant little payoffs that define Kairosoft game-feel — floating coins/numbers, reaction emote bubbles, and pop-up flourishes on every meaningful event — then harden performance and apply the whole visual upgrade across all screens.

## Context Snapshot
- **Current state:** `web/js/effects.js` provides `particleBurst`/`screenFlash`/`glowPulse` (DOM/canvas particles); `web/js/isocity.js` fires green/cyan bursts via `triggerAbatementEffect/OffsetEffect/YearTransition`; `web/game.html` has a toast system and `doDecision`/`doAdvanceYear` event hooks. No floating numbers, coins, or emote bubbles over plots.
- **Desired state:** A floating-feedback layer (rising coin/number pop-ups on income/cost; reaction emotes 😊/😡/💢/💚 over buildings on compliance/abatement/penalty; "+XP"/level flourishes), wired to game events, performant, and present on `game`/`coop`/`summary`.
- **Key repo surfaces:** `web/js/effects.js`, `web/js/isocity.js` (triggers, `tileToScreen`, caps), `web/game.html`/`web/coop.html`/`web/summary.html` (event hooks, toast, notification-bubble style from Sprint 1), `web/css/style.css`.
- **Out of scope:** New building/citizen art (Sprints 2–3), engine changes.

## Research Inputs
- `research/2026-06-14_kairosoft-visual-style.md` — Kairosoft game-feel = constant floating coins/emotes/pop-ups; CarbonSim only emits abstract bursts.
- `reports/2026-06-14-kairosoft-visual-style-gap-analysis.md` — GAP-04 (HIGH) + GAP-07 (perf) + GAP-08 (cross-screen); reuse `effects.js`, isocity triggers, toast, notification-bubble style.

## Assumptions and Constraints
- **ASM-001:** Feedback anchors to plot screen positions via `isocity.tileToScreen` (player plot for player events) or fixed HUD anchors for global events.
- **CON-001:** Respect `prefers-reduced-motion` (reduce/disable floaters) and the existing 30fps/particle caps.
- **CON-002:** Reuse the Sprint-1 "notification bubble" CSS for emote/pop-up styling; reuse the existing toast for non-spatial messages.
- **DEC-001:** Feedback is cosmetic — it reflects engine events already surfaced (cash delta, compliance change, XP), no new engine state.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Floating number/coin layer | Sprints 1–3 | Rising pop-up renderer |
| PHASE-02 | Reaction emotes + event wiring | PHASE-01 | Emote bubbles tied to events |
| PHASE-03 | Perf hardening + cross-screen rollout | PHASE-02 | Capped, reduced-motion-safe, on all screens |

## Detailed Phases

### PHASE-01 - Floating Number / Coin Layer
**Goal**
Render rising, fading pop-ups (coins, +$, +XP, -penalty) at a screen point.

**Tasks**
- [ ] TASK-01-01: Add a `floatText(x, y, text, kind)` to `web/js/effects.js` (or `isocity.js`) — a rising/fading canvas or DOM pop-up with kind-based color/icon.
- [ ] TASK-01-02: Expose an isocity helper to anchor pop-ups to a plot via `tileToScreen` (e.g. above the player's building).
- [ ] TASK-01-03: Cap concurrent floaters and recycle (mirror particle cap).

**Files / Surfaces**
- `web/js/effects.js` and/or `web/js/isocity.js` — floater layer.

**Dependencies**
- Sprints 1–3 (palette/bubble style, plot anchors)

**Exit Criteria**
- [ ] Calling the helper shows a rising, fading coin/number pop-up at the right spot.

**Phase Risks**
- **RISK-01-01:** Floater spam on rapid actions → cap + debounce per event type.

### PHASE-02 - Reaction Emotes & Event Wiring
**Goal**
Surface emotes/pop-ups on the events players care about.

**Tasks**
- [ ] TASK-02-01: Add reaction-emote bubbles (😊 compliant, 💚 abatement, 😡/💢 penalty/shortfall) over the relevant plot using the Sprint-1 bubble style.
- [ ] TASK-02-02: Wire to events in `web/game.html`: `doDecision` (abatement→💚+cost coin; offsets→coin), `doAdvanceYear`/compliance change (😊 or 😡 + penalty number), XP/level-up (`progression.js`) → +XP flourish.
- [ ] TASK-02-03: Keep non-spatial confirmations on the existing toast; avoid double-signaling.

**Files / Surfaces**
- `web/game.html` — event hooks; `web/js/isocity.js` triggers; `web/js/effects.js`.

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] Abatement, offset, compliance, penalty, and level-up events each produce the right floater/emote.

**Phase Risks**
- **RISK-02-01:** Visual noise → reserve emotes for meaningful state changes, not every click.

### PHASE-03 - Perf Hardening & Cross-Screen Rollout
**Goal**
Keep it smooth and apply everywhere.

**Tasks**
- [ ] TASK-03-01: Profile with citizens (Sprint 3) + floaters together; tune caps to hold ~30fps on mobile.
- [ ] TASK-03-02: Ensure `prefers-reduced-motion` reduces/disables floaters and emotes.
- [ ] TASK-03-03: Apply the feedback layer (and confirm Sprints 1–3 visuals) on `web/coop.html` and `web/summary.html`, not just `game.html`.

**Files / Surfaces**
- `web/js/isocity.js`, `web/js/effects.js`; `web/coop.html`, `web/summary.html`.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] ~30fps with citizens + floaters on mobile; reduced-motion safe; all three in-game screens show the full Kairosoft visual stack.

**Phase Risks**
- **RISK-03-01:** Co-op/summary init differs from solo → verify each screen's renderer/event wiring independently.

## Verification Strategy
- **MANUAL-001:** Play solo + co-op; confirm coins/emotes/pop-ups fire on the right events and feel good (not spammy).
- **OBS-001:** Performance trace with citizens + floaters: sustained ~30fps, flat memory.
- **MANUAL-002:** Reduced-motion pass across all three screens.

## Risks and Alternatives
- **RISK-001:** Combined animation load (citizens + floaters + particles) janks low-end → unified caps + reduced-motion floor.
- **ALT-001:** Pure-toast feedback (no spatial floaters) — rejected; spatial coins/emotes are the Kairosoft hallmark.

## Grill Me
No open clarification questions. (Feedback is cosmetic over existing engine events; styling reuses Sprint-1 bubbles.)

## Suggested Next Step
Execute PHASE-01 → PHASE-03. This completes the Kairosoft visual roadmap; write a final `/report` summarizing the four sprints.
