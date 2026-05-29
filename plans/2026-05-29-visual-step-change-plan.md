---
title: "Sprint 5 — Visual Step-Change"
date: "2026-05-29"
status: "draft"
request: "Sequenced multiphase plans from reports/2026-05-29-single-multiplayer-game-gap-analysis.md — cluster (5): GAP-04 (visual step-change — decent visuals improved upon CarbonSim)."
plan_type: "multi-phase"
research_inputs:
  - "reports/2026-05-29-single-multiplayer-game-gap-analysis.md"
---

# Plan: Sprint 5 — Visual Step-Change

## Objective
Deliver the "decent visuals improved upon CarbonSim" half of the goal: turn the functional DOM/form frontend into a cohesive, game-feeling experience with a design system and at least one signature animated visual, on top of the consolidated single+multiplayer game. This is the final Sprint and depends on a stable codebase from Sprints 1-4.

## Context Snapshot
- **Current state:** `mayor_web/` is hand-rolled static HTML + vanilla JS (`api.js`, `effects.js`, `audio.js`, `progression.js`, `shortcuts.js`) + `css/style.css` + `css/animations.css` (~3,287 LOC). It has game-feel primitives (animations, audio, XP/progression) but no rendering/scene layer, no design-token system, no reusable component model, and no build tooling. The engine already emits rich snapshots (emissions, compliance gap, market path, replay data) that are under-used visually. Served statically by `mayor_api/main.py` (mounts `/css`, `/js`; catch-all serves `mayor_web`).
- **Desired state:** A documented design language (tokens, components, iconography), a refactor of the existing screens onto it, and a signature visual that makes the carbon-market state legible and alive (candidates: an animated city skyline reacting to emissions/compliance, a live compliance gauge, or an animated market/price chart). Visuals must be a clear step up from CarbonSim's tables while staying performant and (per AGENTS.md) not over-engineered.
- **Key repo surfaces:** `mayor_web/index.html`, `mayor_web/game.html`, `mayor_web/coop.html`, `mayor_web/summary.html`, `mayor_web/css/style.css`, `mayor_web/css/animations.css`, `mayor_web/js/*.js`, `mayor_api/main.py` (static serving), engine snapshot shape from `carbonsim_engine`.
- **Out of scope:** New gameplay mechanics, engine changes, multiplayer features (Sprints 3-4). This plan re-skins and enriches presentation of existing state.

## Research Inputs
- `reports/2026-05-29-single-multiplayer-game-gap-analysis.md` — GAP-04: current visuals are DOM forms with no scene/design system; the data to drive richer visuals already exists in engine snapshots; the AGENTS.md "no heavy front-end" guardrail must be relaxed (done in Sprint 1) to a bounded visual scope.

## Assumptions and Constraints
- **ASM-001:** Sprints 1-4 complete: single product, clean tree, trimmed engine, working single + multiplayer. `AGENTS.md` now permits bounded visual work.
- **ASM-002:** Engine snapshots already contain the fields needed for visualization (emissions, allocation, gap, market path, year/phase); no backend changes required for the core visuals.
- **CON-001:** Keep the static-served + FastAPI delivery model unless a build step is explicitly justified (Grill Me Q-002); any framework/build must not break `mayor_api/main.py` static mounts.
- **CON-002:** Visuals must remain legible and performant for the workshop/desktop-first audience; mobile/tablet usability acceptable.
- **DEC-001:** Reuse existing game-feel primitives (`animations.css`, `effects.js`, `audio.js`, `progression.js`) as the foundation rather than discarding them.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Decide visual direction & establish a design system | None (post-Sprint 4) | Art direction doc, design tokens, base component styles |
| PHASE-02 | Refactor existing screens onto the design system | PHASE-01 | `index/game/coop/summary` re-skinned consistently |
| PHASE-03 | Build the signature visual driven by engine snapshots | PHASE-02 | Animated scene/gauge/chart reflecting live game state |
| PHASE-04 | Polish, responsiveness & performance pass | PHASE-03 | Transitions, responsive layout, perf budget met |

## Detailed Phases

### PHASE-01 - Visual Direction & Design System
**Goal**
Pick a direction and lay down the reusable visual vocabulary everything else builds on.

**Tasks**
- [ ] TASK-01-01: Decide the visual approach (Grill Me Q-001): (a) vanilla + canvas/SVG scene, or (b) a lightweight framework/build (e.g., Vite + component lib or a canvas game lib).
- [ ] TASK-01-02: Define design tokens (color palette incl. compliance/penalty semantics, spacing scale, typography, elevation) as CSS custom properties extending `css/style.css`.
- [ ] TASK-01-03: Establish a small component set (cards/panels, buttons, gauges, stat tiles, toasts) and consistent iconography for emissions/allocation/offsets/cash/compliance.
- [ ] TASK-01-04: Write `docs/design-language.md` capturing the direction, tokens, and components so screens are reskinned consistently.

**Files / Surfaces**
- `mayor_web/css/style.css`, `mayor_web/css/animations.css` - token + component base.
- `docs/design-language.md` (new).

**Dependencies**
- None beyond Sprint 4.

**Exit Criteria**
- [ ] Tokens + base components exist and are documented.
- [ ] A direction is chosen and recorded with rationale.

**Phase Risks**
- **RISK-01-01:** Introducing a build/framework balloons scope. Mitigation: default to vanilla + canvas; only adopt a build if Q-002 justifies it.

### PHASE-02 - Reskin Existing Screens
**Goal**
Make every screen consistent with the design system before adding the signature visual.

**Tasks**
- [ ] TASK-02-01: Refactor `index.html` (entry/difficulty/room) onto tokens + components.
- [ ] TASK-02-02: Refactor `game.html` (the core loop: abatement menu, offset market, compliance position, year/phase) — the highest-value surface.
- [ ] TASK-02-03: Refactor `coop.html` (lobby + multiplayer session) to match, reusing the lobby/host UI from Sprint 4.
- [ ] TASK-02-04: Refactor `summary.html` (end-of-game results) to a polished outcome screen.
- [ ] TASK-02-05: Ensure `mayor_api/main.py` static mounts still resolve all assets after any file moves.

**Files / Surfaces**
- `mayor_web/index.html`, `game.html`, `coop.html`, `summary.html`, `mayor_web/css/*`, `mayor_web/js/*`.

**Dependencies**
- PHASE-01.

**Exit Criteria**
- [ ] All four screens share one consistent visual language.
- [ ] No functional regressions (solo + multiplayer still play through).

**Phase Risks**
- **RISK-02-01:** Reskin breaks JS hooks (IDs/classes referenced in `js/*`). Mitigation: preserve or update selectors deliberately; smoke-test each screen after refactor.

### PHASE-03 - Signature Visual
**Goal**
Add the one visual that makes the game feel "improved upon CarbonSim" — a live, animated representation of the carbon-market state.

**Tasks**
- [ ] TASK-03-01: Implement the chosen signature visual (Grill Me Q-003) driven by the existing engine snapshot — e.g., a city skyline whose smog/skyline reacts to emissions vs. allocation, an animated compliance gauge, or a live market/price chart over the year cycle.
- [ ] TASK-03-02: Wire it to the snapshot data already fetched in `js/api.js`; animate transitions on year advance and decision effects using `effects.js`/`animations.css`.
- [ ] TASK-03-03: Make it work in both solo (`game.html`) and multiplayer (`coop.html`) contexts.

**Files / Surfaces**
- `mayor_web/game.html`, `coop.html`, new `mayor_web/js/scene.js` (or chart module), `mayor_web/js/api.js`, `css/animations.css`.

**Dependencies**
- PHASE-02.

**Exit Criteria**
- [ ] The signature visual updates live as the player acts and as years advance, in both modes.
- [ ] It reads correctly from existing snapshot fields with no backend changes.

**Phase Risks**
- **RISK-03-01:** Snapshot lacks a field the visual needs. Mitigation: confirm field availability against the engine snapshot in PHASE-01; if genuinely missing, scope a minimal additive snapshot field (the only allowed backend touch).

### PHASE-04 - Polish, Responsiveness & Performance
**Goal**
Final-pass quality: smooth, responsive, and within a performance budget.

**Tasks**
- [ ] TASK-04-01: Add cohesive micro-interactions/transitions across screens (consistent timing/easing from tokens).
- [ ] TASK-04-02: Make layouts responsive for desktop-first with acceptable tablet behavior; verify the core loop on a smaller viewport.
- [ ] TASK-04-03: Performance pass: cap animation cost, lazy-load heavy assets, ensure the signature visual stays smooth during multiplayer broadcasts.
- [ ] TASK-04-04: Accessibility basics: focus states, color-contrast on compliance/penalty semantics, reduced-motion respect.

**Files / Surfaces**
- `mayor_web/css/*`, `mayor_web/js/*`, all four HTML screens.

**Dependencies**
- PHASE-03.

**Exit Criteria**
- [ ] Smooth transitions, responsive layout, and a stable frame rate during play (incl. multiplayer).
- [ ] Reduced-motion and basic contrast checks pass.

**Phase Risks**
- **RISK-04-01:** Heavy visuals degrade multiplayer responsiveness. Mitigation: decouple rendering from network broadcasts; throttle visual updates.

## Verification Strategy
- **TEST-001:** Existing engine + API + multiplayer suites stay green (visual work must not regress logic).
- **MANUAL-001:** Play a full solo game and a multiplayer session; confirm the signature visual reflects state changes and the reskin is consistent across all four screens.
- **MANUAL-002:** Side-by-side before/after screenshots demonstrating the step-change vs. the current DOM-form UI.
- **OBS-001:** Frame-rate/perf check during a multiplayer session with the signature visual active.

## Risks and Alternatives
- **RISK-001:** Visual scope creep delays delivery. Mitigation: one signature visual + consistent reskin is the bar; defer anything beyond.
- **ALT-001:** Full framework rewrite (React/Vue SPA). Rejected unless Q-002 justifies it — risks throwing away working vanilla JS and re-introducing build complexity the project deliberately avoided.

## Grill Me
1. **Q-001:** Vanilla + canvas/SVG, or adopt a lightweight framework + build step?
   - **Recommended default:** Vanilla + canvas/SVG, extending the existing JS — lowest risk, preserves static-serve model.
   - **Why this matters:** Determines tooling, file structure, and how `mayor_api/main.py` serves assets.
   - **If answered differently:** A framework/build adds a bundler, changes static serving, and expands PHASE-01/02 substantially.
2. **Q-002:** Is introducing a build step (e.g., Vite) acceptable, or must the frontend stay buildless/static-served?
   - **Recommended default:** Stay buildless/static-served (current model) unless the signature visual demands a library that needs bundling.
   - **Why this matters:** Affects deployment, `mayor_api` static mounts, and contributor setup.
   - **If answered differently:** A build step requires updating run/deploy docs and the static-serving path.
3. **Q-003:** Which signature visual best fits the "Climate Mayor" theme — reactive city skyline, compliance gauge, or live market chart?
   - **Recommended default:** Reactive city skyline (strongest thematic fit and clearest emissions↔visual mapping), with a compliance gauge as a secondary element.
   - **Why this matters:** Defines PHASE-03 scope and which snapshot fields are visualized.
   - **If answered differently:** A market chart leans competitive-multiplayer; a gauge is the cheapest to ship.

## Suggested Next Step
Answer Q-001-Q-003, then execute PHASE-01 → PHASE-04. This is the final Sprint; on completion the product goal (consolidated single+multiplayer game with improved visuals) is met.
