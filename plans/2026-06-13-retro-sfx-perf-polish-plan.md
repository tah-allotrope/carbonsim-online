---
title: "Sprint 5 — Retro SFX Re-voice & Iso Renderer Perf/A11y Polish (GAP-06 + GAP-07)"
date: "2026-06-13"
status: "draft"
request: "Create multiple multi-phase plans from reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md — one per recommended sprint. This is Sprint 5: SFX + perf/a11y polish."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md"
---

# Plan: Sprint 5 — Retro SFX Re-voice & Iso Renderer Perf/A11y Polish

## Objective
Finish the retro step-change: re-voice the procedural Web-Audio SFX to a chiptune register and turn the DOM particle bursts into pixel-style bursts, then harden the heavier isometric renderer for performance (frame budget, tile/particle caps, mobile scaling) and accessibility (reduced-motion static city, contrast, focus). This makes the experience feel and run like a polished retro tycoon game, not just look like one.

## Context Snapshot
- **Current state:** `web/js/audio.js` (406 lines) is already procedural Web-Audio synth (oscillators at lines 81-165) — well-suited to chiptune but voiced for the neon theme. `web/js/effects.js` (191 lines) spawns DOM glow particles (`particleBurst`, line 80). The Sprint-3 iso renderer is heavier than the old `fillRect` skyline and is now the default across all modes (Sprint 4).
- **Desired state:** Chiptune-flavored SFX, pixel-style effect bursts, and an iso renderer that holds ~30fps with bounded resource use on low-end/mobile, with a clean reduced-motion static-city fallback and verified contrast/focus.
- **Key repo surfaces:** `web/js/audio.js` (synth voices), `web/js/effects.js` (particle API), `web/js/isocity.js` (Sprint 3 renderer: throttle, DPR, particle caps, `drawStatic`), `web/css/style.css` retro tokens.
- **Out of scope:** New gameplay, new screens, new renderer features beyond perf/a11y.

## Research Inputs
- `reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md` — GAP-06 (MEDIUM, re-voice SFX + pixel-ify effects; `audio.js` is re-voiceable synth, `effects.js` particle API reusable) and GAP-07 (LOW, iso renderer perf & a11y parity; `isocity.js` already carries throttle + DPR + `drawStatic` reduced-motion path).

## Assumptions and Constraints
- **ASM-001:** `audio.js` stays synth-based (no sample assets) — chiptune is achieved by tuning oscillator type/envelope/arpeggio, not by adding audio files.
- **ASM-002:** `isocity.js` from Sprint 3 already implements the 30fps throttle, DPR `resize`, particle cap, and a `drawStatic()` path — this sprint tunes and verifies them, not re-implements.
- **CON-001:** Maintain the existing mute control (`game.html:31` `toggleMute()`) and audio-context-on-gesture init (`audio.js:21-35`).
- **CON-002:** Reduced-motion must yield a fully static but still legible isometric city (no animation, no particles), reusing the `drawStatic()` branch.
- **DEC-001:** Accessibility floor from `docs/design-language.md` holds: contrast ≥4.5:1 body / 3:1 large; color never the sole indicator; `:focus-visible` on all interactive elements.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Chiptune SFX + pixel-style effects | Sprints 2-4 | Re-voiced `audio.js`, pixel-ified `effects.js` |
| PHASE-02 | Iso renderer performance hardening | Sprint 3 | Frame budget + caps + mobile scaling tuned |
| PHASE-03 | Accessibility parity & sign-off | PHASE-02 | Reduced-motion static city, contrast/focus verified |

## Detailed Phases

### PHASE-01 - Chiptune SFX & Pixel Effects
**Goal**
Make sound and micro-effects read as retro.

**Tasks**
- [ ] TASK-01-01: Re-voice the `audio.js` oscillator cues (lines 81-165) to chiptune — square/triangle waves, short attack/decay envelopes, simple arpeggios for positive events; keep the existing event hooks (abatement/offset/year/error) and mute behavior.
- [ ] TASK-01-02: Restyle `effects.js` `particleBurst` (line 80) to pixel-style bursts (blocky particles / stepped motion / palette from Sprint-2 tokens) instead of soft glows.
- [ ] TASK-01-03: Confirm the iso renderer's own particle effects (Sprint 3 triggers) visually match the new pixel style.

**Files / Surfaces**
- `web/js/audio.js:81-165` — voice tuning.
- `web/js/effects.js` — particle styling.

**Dependencies**
- Sprints 2-4 (tokens + iso default)

**Exit Criteria**
- [ ] Action SFX sound chiptune; effect bursts read as pixel art; mute still works.

**Phase Risks**
- **RISK-01-01:** Chiptune SFX become grating on repeat → keep durations short and volumes modest; reuse existing gain envelopes.

### PHASE-02 - Iso Renderer Performance Hardening
**Goal**
Keep the heavier isometric scene smooth on low-end/mobile.

**Tasks**
- [ ] TASK-02-01: Profile `isocity.js` on a throttled CPU + mobile viewport; confirm sustained ~30fps and no growing allocation.
- [ ] TASK-02-02: Tune tile/particle caps (carry/extend the `particles.length` guard pattern from `skyline.js:243`); scale particle budget by company/plot count.
- [ ] TASK-02-03: Verify DPR-aware `resize` produces crisp tiles without over-rendering on high-DPR mobile; cap effective DPR if needed.
- [ ] TASK-02-04: Ensure off-focus/background tabs throttle correctly (the FPS-interval gate).

**Files / Surfaces**
- `web/js/isocity.js` — caps, scaling, throttle verification.

**Dependencies**
- Sprint 3

**Exit Criteria**
- [ ] ~30fps sustained on a mid-range mobile profile with the largest expected plot count; no unbounded particle/image growth.

**Phase Risks**
- **RISK-02-01:** High-DPR mobile over-renders → cap effective devicePixelRatio for the canvas.

### PHASE-03 - Accessibility Parity & Sign-off
**Goal**
Guarantee the retro look doesn't regress accessibility.

**Tasks**
- [ ] TASK-03-01: Verify `prefers-reduced-motion` yields a static, legible isometric city (no RAF loop, no particles) via the `drawStatic()` path; fix gaps.
- [ ] TASK-03-02: Run contrast checks (axe/Lighthouse) on the retro palette across all four screens; adjust tokens if any text fails.
- [ ] TASK-03-03: Keyboard-only pass: `:focus-visible` visible on every interactive element; canvas remains `aria-hidden` decorative with state also available as text/overlay.
- [ ] TASK-03-04: Update `docs/design-language.md` Accessibility section with the verified results.

**Files / Surfaces**
- `web/js/isocity.js` — reduced-motion path.
- `web/css/style.css`, all four HTML screens — contrast/focus.
- `docs/design-language.md` — record results.

**Dependencies**
- PHASE-02

**Exit Criteria**
- [ ] Reduced-motion shows a static city; contrast and focus checks pass on all screens; design doc reflects verified a11y.

**Phase Risks**
- **RISK-03-01:** Retro palette dips below contrast in places → treat token values as adjustable; re-verify after any change.

## Verification Strategy
- **MANUAL-001:** Play through all modes with sound on; confirm chiptune SFX + pixel bursts; toggle mute.
- **OBS-001:** Devtools performance trace on throttled CPU/mobile: sustained ~30fps, flat memory.
- **MANUAL-002:** Enable OS reduced-motion; confirm static legible city and no animation anywhere.
- **TEST-001:** Lighthouse/axe accessibility pass on each screen; record scores in `docs/design-language.md`.

## Risks and Alternatives
- **RISK-001:** Perf tuning and a11y can conflict with visual richness → prioritize the 30fps floor and contrast minimums over decorative density.
- **ALT-001:** Adding sampled chiptune audio files was rejected — the existing synth is sufficient and avoids new assets/licensing.

## Grill Me
No open clarification questions. (Synth-based SFX, vanilla canvas, and the a11y floor are all fixed by prior sprints and the design doc.)

## Suggested Next Step
Execute PHASE-01 → PHASE-03. This completes the retro isometric-tycoon roadmap; write a final `/report` summarizing the five sprints.
