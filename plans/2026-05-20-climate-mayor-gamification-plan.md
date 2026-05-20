---
title: "Climate Mayor — Gamification & Game-Feel Overhaul"
date: "2026-05-20"
status: "draft"
request: "Review available UI/webapp, select one to improve, make it more like a game via multiphase plan"
plan_type: "multi-phase"
research_inputs:
  - "research/2026-04-26_carbon-game-ideas.md"
---

# Plan: Climate Mayor — Gamification & Game-Feel Overhaul

## Objective

Transform Climate Mayor (`mayor_web/`) from a functional carbon-trading simulation into an engaging, polished game experience through frontend-only enhancements: animated visual feedback, sound design, progression systems, and micro-interactions. The goal is intrinsic motivation — a reason to play when no one is making you — which the research brief identifies as the missing ingredient.

## Context Snapshot

- **Current state:** Climate Mayor is a working single-player + co-op carbon ETS simulation with a dark cyberpunk aesthetic. It has year-based progression, event cards, abatement/offset decisions, save/load, tutorial mode, achievements, and a Chart.js summary screen. The UI is clean but static — no animations, no sound, no progression overlay, no loading ceremony. Interactions feel like form submissions, not game moves.
- **Desired state:** Every player action produces immediate, satisfying feedback (animation, sound, counter tick). Year transitions feel like level-ups. Event cards arrive with drama. Achievements pop with fanfare. A progress/XP overlay gives a persistent sense of advancement. The game loads with atmosphere and polish.
- **Key repo surfaces:**
  - `mayor_web/index.html` — Main menu / new game screen
  - `mayor_web/game.html` — Core gameplay loop (358 lines, inline `<script>`)
  - `mayor_web/summary.html` — End-of-game summary with Chart.js
  - `mayor_web/coop.html` — Co-op multiplayer page
  - `mayor_web/css/style.css` — All styling (150 lines, CSS custom properties)
  - `mayor_web/js/api.js` — API client (33 lines, thin fetch wrapper)
- **Out of scope:** Backend changes (`mayor_api/`), engine changes (`carbonsim_engine/`), oTree platform (`platform/`), new game modes, content/card additions, deployment changes.

## Research Inputs

- `research/2026-04-26_carbon-game-ideas.md` — Identifies "intrinsic motivation" as the missing element in the current repo. Climate game success factors from peer-reviewed literature: strong debrief/reflection, theory-driven psychological design, causal-reasoning support. The brief notes Climate Mayor already has causal feedback and debrief material, but lacks the engagement hooks that make players return voluntarily. This plan directly addresses that gap through game-feel and progression mechanics.

## Assumptions and Constraints

- **ASM-001:** All changes are pure frontend (HTML, CSS, vanilla JS). No build tools, no npm, no frameworks.
- **ASM-002:** The existing dark cyberpunk aesthetic (CSS custom properties in `:root`) is preserved and extended, not replaced.
- **ASM-003:** Sound and music assets will be royalty-free, small (< 50KB per effect, < 500KB for ambient loop), and hosted locally in `mayor_web/audio/`.
- **CON-001:** No changes to `mayor_api/` or `carbonsim_engine/` — all game-feel enhancements are client-side overlays on existing API responses.
- **CON-002:** Must not break existing save/load or co-op functionality.
- **DEC-001:** Sound is opt-in with a mute toggle (persisted to localStorage). No autoplay audio.

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Visual juice — animations, particle effects, animated counters, toast upgrades | None | `mayor_web/js/effects.js`, `mayor_web/css/animations.css`, updated `game.html` and `style.css` |
| PHASE-02 | Sound & atmosphere — audio manager, SFX, ambient music toggle | PHASE-01 | `mayor_web/js/audio.js`, `mayor_web/audio/` directory with assets, sound hooks in `game.html` |
| PHASE-03 | Progression & engagement — XP/level overlay, compliance progress bars, streak counter, achievement popups, timeline minimap | PHASE-01 | `mayor_web/js/progression.js`, updated `game.html`, `summary.html` |
| PHASE-04 | Polish & game feel — loading screen, page transitions, hover micro-interactions, keyboard shortcuts, responsive fixes | PHASE-01, PHASE-02, PHASE-03 | Updated all HTML files, `style.css`, new `mayor_web/js/shortcuts.js` |

## Detailed Phases

### PHASE-01 — Visual Juice & Feedback

**Goal**
Make every player action produce immediate, satisfying visual feedback. The game should feel alive and responsive rather than static.

**Tasks**
- [ ] TASK-01-01: Create `mayor_web/css/animations.css` with keyframe definitions for: card-reveal (scale + fade from center), card-dismiss (slide out + fade), year-transition (full-screen wipe with year number), decision-confirm (pulse glow on the triggered element), counter-tick (number rolls up/down with easing), toast-enhanced (slide-in with icon + auto-dismiss with progress bar).
- [ ] TASK-01-02: Create `mayor_web/js/effects.js` with utility functions: `animateCounter(element, from, to, duration)` for smooth number transitions, `particleBurst(x, y, color, count)` for small CSS particle effects on key actions, `glowPulse(element, color)` for temporary border/shadow glow, `screenFlash(color, duration)` for full-viewport flash on major events (penalties, achievements).
- [ ] TASK-01-03: Update `game.html` `renderContent()` to add CSS classes for card entrance animations. Each `.event-card` should animate in when first rendered. Card resolution buttons should trigger a dismiss animation before calling the API.
- [ ] TASK-01-04: Update `game.html` `doAdvanceYear()` to trigger a year-transition animation (overlay with the new year number scaling in, brief hold, fade out) before refreshing game state.
- [ ] TASK-01-05: Update `game.html` stat values (Cash, Allowances, Projected Emissions, Compliance Gap) to use `animateCounter()` instead of direct text replacement, so numbers visibly tick up/down on refresh.
- [ ] TASK-01-06: Replace the basic `.toast` in `style.css` with an enhanced toast system: categorized toasts (success/warning/error/info), icon prefix, slide-in from bottom-right with stacking, auto-dismiss progress bar animation. Update `showToast(msg)` in `game.html` to accept a category parameter.
- [ ] TASK-01-07: Add particle burst effect to the "Activate" button click in the abatement menu (green particles on successful activation).
- [ ] TASK-01-08: Add a glow-pulse effect on the compliance meter when compliance state changes (green pulse for compliant, red pulse for shortfall).
- [ ] TASK-01-09: Link `animations.css` in `game.html`, `index.html`, `summary.html`, and `coop.html` `<head>`.
- [ ] TASK-01-10: Link `effects.js` in `game.html` and `coop.html` before the inline `<script>` block.

**Files / Surfaces**
- `mayor_web/css/animations.css` — New file; all keyframe and animation class definitions
- `mayor_web/js/effects.js` — New file; JS animation utilities (animateCounter, particleBurst, glowPulse, screenFlash)
- `mayor_web/game.html` — Modify `renderContent()`, `doAdvanceYear()`, `showToast()`, stat rendering; add script/link tags
- `mayor_web/css/style.css` — Extend `.toast` styles, add transition properties to `.stat-value`, `.event-card`, `.compliance-meter`
- `mayor_web/index.html` — Add `animations.css` link
- `mayor_web/summary.html` — Add `animations.css` link
- `mayor_web/coop.html` — Add `animations.css` and `effects.js` links

**Dependencies**
- None

**Exit Criteria**
- [ ] Event cards animate in on render (visible scale+fade transition)
- [ ] Year advance triggers a visible full-screen year transition overlay
- [ ] Stat counters (Cash, Allowances, Emissions, Gap) animate numerically on state change
- [ ] Toasts appear with categorized styling (success green, error red, info blue)
- [ ] Activating an abatement measure triggers a green particle burst
- [ ] Compliance meter pulses on state change
- [ ] All existing functionality (save/load, card resolution, advance year, fast-forward) still works
- [ ] No JS console errors on a full game playthrough

**Phase Risks**
- **RISK-01-01:** Animation performance on low-end devices — mitigate by using CSS transforms and opacity only (GPU-composited), no layout-triggering properties. Keep particle count low (< 20 per burst).
- **RISK-01-02:** Animation timing conflicts with rapid API calls — mitigate by making animations interruptible (cancel previous animation before starting new one on same element).

---

### PHASE-02 — Sound & Atmosphere

**Goal**
Add an audio layer that reinforces every game action with appropriate sound feedback and provides optional ambient atmosphere.

**Tasks**
- [ ] TASK-02-01: Create `mayor_web/audio/` directory structure.
- [ ] TASK-02-02: Source or generate royalty-free sound effects (all < 50KB each): `click.mp3` (UI button click), `card-draw.mp3` (card reveal whoosh), `card-resolve.mp3` (card dismiss), `year-advance.mp3` (level-up chime), `activate.mp3` (abatement activation confirmation), `penalty.mp3` (warning buzzer for penalty/shortfall), `success.mp3` (achievement/compliance success), `save.mp3` (save confirmation chirp), `error.mp3` (error feedback). Place in `mayor_web/audio/sfx/`.
- [ ] TASK-02-03: Source or generate a royalty-free ambient music loop (< 500KB, loopable, low-key electronic/atmospheric to match cyberpunk theme). Place as `mayor_web/audio/ambient.mp3`.
- [ ] TASK-02-04: Create `mayor_web/js/audio.js` with an `AudioManager` singleton: `init()` (preload all audio), `playSFX(name)` (play a named sound effect), `startAmbient()` / `stopAmbient()` (toggle background music with fade), `setMasterVolume(0-1)`, `mute()` / `unmute()`, `isMuted()`. Persist mute state to `localStorage['climate_mayor_muted']`.
- [ ] TASK-02-05: Add a mute/unmute toggle button to the game header in `game.html` (speaker icon, toggles between muted/unmuted states). Wire to `AudioManager.mute()`/`unmute()`.
- [ ] TASK-02-06: Hook sound effects into `game.html` actions: `doAdvanceYear()` → `year-advance`, `doResolveCard()` → `card-resolve`, card render → `card-draw`, `doDecision()` activate → `activate`, `doSave()` → `save`, `showToast('error')` → `error`, `showToast('success')` → `success`, all `.btn` clicks → `click`.
- [ ] TASK-02-07: Add ambient music auto-start (respecting mute state) when entering game.html. Stop on page unload.
- [ ] TASK-02-08: Add mute toggle to `index.html` header for consistency.
- [ ] TASK-02-09: Link `audio.js` in `game.html`, `index.html`, `summary.html`, and `coop.html`.

**Files / Surfaces**
- `mayor_web/js/audio.js` — New file; AudioManager singleton with Web Audio API or HTMLAudioElement pool
- `mayor_web/audio/sfx/` — New directory; 9 sound effect files
- `mayor_web/audio/ambient.mp3` — New file; loopable background track
- `mayor_web/game.html` — Add mute button to header, hook SFX into all action functions
- `mayor_web/index.html` — Add mute toggle, link audio.js
- `mayor_web/summary.html` — Link audio.js
- `mayor_web/coop.html` — Link audio.js, hook SFX

**Dependencies**
- PHASE-01 (enhanced toast categories are used to determine which SFX to play)

**Exit Criteria**
- [ ] Each game action (advance year, resolve card, activate abatement, save) plays a distinct sound effect
- [ ] Ambient music plays on game page load (if not muted)
- [ ] Mute toggle in header correctly silences all audio and persists across page reload
- [ ] No audio autoplay violations (audio starts only after first user interaction via click event)
- [ ] All audio files total < 1MB
- [ ] Audio degrades gracefully if files fail to load (no errors, game still works)

**Phase Risks**
- **RISK-02-01:** Browser autoplay policy blocks ambient music — mitigate by starting ambient only after first user click (e.g., the Advance Year button), not on page load. Store "user has interacted" flag.
- **RISK-02-02:** Audio asset licensing — mitigate by using only CC0/public-domain sources (freesound.org, pixabay audio) or procedurally generated Web Audio API tones as fallback.

---

### PHASE-03 — Progression & Engagement

**Goal**
Add visible progression systems that give players a persistent sense of advancement and reward good play beyond the raw compliance numbers.

**Tasks**
- [ ] TASK-03-01: Create `mayor_web/js/progression.js` with: XP calculation from game actions (e.g., +10 XP per year survived, +25 XP per achievement, +5 XP per abatement activated, -10 XP per penalty), level thresholds (Level 1-10 with escalating XP requirements), streak tracking (consecutive years compliant), and localStorage persistence keyed to game ID.
- [ ] TASK-03-02: Add an XP/level HUD bar to `game.html` — a thin persistent bar below the header showing current level, XP progress to next level (animated fill), and streak counter. Use the existing cyberpunk color palette (accent cyan for XP bar, green for streak).
- [ ] TASK-03-03: Add compliance target progress visualization to the Compliance Position card in `game.html`: a radial or horizontal progress bar showing "% of game years compliant so far" with color coding (green > 80%, orange 50-80%, red < 50%).
- [ ] TASK-03-04: Implement animated achievement popup overlay in `game.html`: when an achievement is earned (detected by comparing achievement arrays between refreshes), show a centered modal-style popup with the achievement icon, title, description, and XP reward, with entrance animation (scale up + glow) and auto-dismiss after 4 seconds. Play `success` SFX.
- [ ] TASK-03-05: Add a timeline minimap to `game.html` — a horizontal bar at the top or bottom of the main content showing all game years as small segments, color-coded by compliance status (green = compliant, red = shortfall, gray = future). Current year is highlighted. Clicking a past segment could show a tooltip with that year's stats.
- [ ] TASK-03-06: Update `summary.html` to show final XP earned, level reached, longest compliance streak, and a "performance grade" (S/A/B/C/D based on composite score of compliance %, cash remaining, penalties avoided). Add these to the share text.
- [ ] TASK-03-07: Add a "personal best" tracker in localStorage — after each completed game, compare score to stored best for that difficulty. Show "New Personal Best!" celebration on summary page if beaten.
- [ ] TASK-03-08: Link `progression.js` in `game.html` and `summary.html`.

**Files / Surfaces**
- `mayor_web/js/progression.js` — New file; XP/level/streak calculation, localStorage persistence, achievement diff detection
- `mayor_web/game.html` — Add XP HUD bar, compliance progress viz, achievement popup overlay, timeline minimap, link progression.js
- `mayor_web/summary.html` — Add final XP/level/streak/grade display, personal best comparison, link progression.js
- `mayor_web/css/style.css` — Add styles for XP bar, compliance progress, achievement popup, timeline minimap
- `mayor_web/css/animations.css` — Add achievement-popup entrance/exit keyframes

**Dependencies**
- PHASE-01 (uses `animateCounter`, `glowPulse`, `screenFlash` for achievement celebrations)

**Exit Criteria**
- [ ] XP bar visible below header during gameplay, fills smoothly on XP gain
- [ ] Level displayed and increments when XP threshold crossed
- [ ] Streak counter shows consecutive compliant years, resets on shortfall
- [ ] Achievement popup appears with animation when a new achievement is earned
- [ ] Timeline minimap shows color-coded year segments matching compliance history
- [ ] Summary page shows XP, level, streak, and performance grade
- [ ] Personal best detection works across games at same difficulty
- [ ] All progression data persists in localStorage and survives page reload

**Phase Risks**
- **RISK-03-01:** XP values feel arbitrary or unbalanced — mitigate by playtesting a full easy + standard + hard game and adjusting XP values so players reach level 3-5 in a typical standard game.
- **RISK-03-02:** Achievement diff detection may false-positive on page reload — mitigate by storing "last seen achievements" per game ID in localStorage and only showing popups for genuinely new ones.

---

### PHASE-04 — Polish & Game Feel

**Goal**
Add the final layer of polish that makes the game feel professional: loading ceremony, smooth transitions, micro-interactions, keyboard shortcuts, and responsive refinements.

**Tasks**
- [ ] TASK-04-01: Add a loading screen to `game.html`: when the page loads (before API response), show a full-screen overlay with the Climate Mayor logo/title, a pulsing loading indicator, and a random gameplay tip (from a hardcoded array of 10-15 tips). Fade out when game state loads.
- [ ] TASK-04-02: Add smooth page transitions: when navigating between `index.html` → `game.html` → `summary.html`, use a CSS fade-out on the current page before navigation. Implement via a `navigateTo(url)` helper that adds a `.page-exit` class, waits 300ms, then sets `window.location`.
- [ ] TASK-04-03: Add hover micro-interactions to all interactive elements: buttons get a subtle scale(1.02) + brightness boost on hover, cards get a border-glow intensification, table rows get a highlight slide, badges get a gentle pulse. All via CSS `:hover` transitions.
- [ ] TASK-04-04: Create `mayor_web/js/shortcuts.js` with keyboard shortcut support: `Space` or `Enter` = Advance Year (when no modal open), `S` = Quick Save, `Esc` = Close any open modal, `1-9` = Quick-select abatement measure, `M` = Toggle mute. Show a small keyboard icon in the header that reveals the shortcut cheat sheet on hover.
- [ ] TASK-04-05: Improve responsive behavior in `style.css`: ensure the game is playable on tablets (768px-1024px) and tolerable on phones (< 768px). Key fixes: stack the grid layouts, make the header vertical, ensure tables scroll horizontally, size touch targets to 44px minimum.
- [ ] TASK-04-06: Add a subtle animated background to the `<body>` — a slow-moving CSS gradient or subtle grid-line animation that reinforces the cyberpunk theme without distracting from content.
- [ ] TASK-04-07: Polish the `index.html` main menu: add a tagline/subtitle, animate the "Start Game" button with a subtle pulse, add a brief "How to Play" expandable section with 3-4 bullet points.
- [ ] TASK-04-08: Add a "Game Over" ceremony to the completion state in `game.html`: instead of jumping straight to the static "Game Complete!" card, play a short sequence — screen dims, stats count up one by one, final grade reveals with appropriate SFX and particle effects, then the "View Summary" button appears.
- [ ] TASK-04-09: Link `shortcuts.js` in `game.html` and `coop.html`.
- [ ] TASK-04-10: Final cross-browser test pass: verify all animations, audio, and interactions work in Chrome, Firefox, and Edge. Fix any CSS prefixing issues.

**Files / Surfaces**
- `mayor_web/js/shortcuts.js` — New file; keyboard shortcut handler with cheat-sheet overlay
- `mayor_web/game.html` — Add loading screen, page transitions, game-over ceremony, link shortcuts.js
- `mayor_web/index.html` — Add tagline, pulse animation, how-to-play section, page transition
- `mayor_web/summary.html` — Add page transition entrance
- `mayor_web/coop.html` — Add page transition, link shortcuts.js
- `mayor_web/css/style.css` — Hover micro-interactions, responsive fixes, animated background, loading screen styles
- `mayor_web/css/animations.css` — Page transition keyframes, loading screen pulse, game-over sequence keyframes

**Dependencies**
- PHASE-01 (uses effects.js utilities for game-over ceremony)
- PHASE-02 (uses audio.js for game-over SFX, mute toggle for shortcut)
- PHASE-03 (game-over ceremony shows XP/level/grade from progression.js)

**Exit Criteria**
- [ ] Loading screen appears with a tip while game state loads, then fades out smoothly
- [ ] Page transitions are smooth (fade out current, fade in new)
- [ ] All buttons and cards have visible hover micro-interactions
- [ ] Keyboard shortcuts work: Space/Enter advances year, S saves, Esc closes modals, M toggles mute
- [ ] Shortcut cheat sheet appears on hover over keyboard icon
- [ ] Game is usable on a 768px-wide screen (no horizontal overflow, touch targets adequate)
- [ ] Animated background visible but not distracting
- [ ] Game-over ceremony plays a sequenced stat reveal before showing the summary link
- [ ] Full playthrough (new game → play 5 years → save → load → complete → summary) works without errors in Chrome, Firefox, Edge

**Phase Risks**
- **RISK-04-01:** Keyboard shortcuts conflict with browser defaults — mitigate by only capturing shortcuts when no input/textarea is focused, and using non-conflicting keys (avoid Ctrl+key combos).
- **RISK-04-02:** Animated background causes performance issues — mitigate by using a simple CSS gradient animation (no canvas, no JS), and adding `prefers-reduced-motion` media query to disable it.

## Verification Strategy

- **TEST-001:** After each phase, do a full manual playthrough: create new game (easy mode for speed) → play through 3+ years → activate abatement → resolve event cards → save → load → complete game → view summary. Verify all new features trigger correctly.
- **TEST-002:** After PHASE-02, verify mute state persists: mute audio → close tab → reopen → confirm still muted. Unmute → close tab → reopen → confirm ambient plays after first click.
- **TEST-003:** After PHASE-03, verify progression persistence: play 3 years → note XP/level → close tab → resume game → confirm XP/level unchanged. Complete game → check personal best stored.
- **TEST-004:** After PHASE-04, test responsive layout at 1440px, 1024px, 768px, and 375px widths. Verify no horizontal scroll, no overlapping elements, touch targets >= 44px.
- **MANUAL-001:** After PHASE-04, open the game in Chrome, Firefox, and Edge. Verify animations, sounds, and interactions work consistently. Check DevTools console for errors/warnings.
- **OBS-001:** Monitor total asset size of `mayor_web/` after all phases. Target: < 2MB total added (audio is the largest contributor). Verify with `du -sh mayor_web/audio/`.

## Risks and Alternatives

- **RISK-001:** Scope creep from "game feel" into "new game features" — mitigate by strictly enforcing the out-of-scope boundary: no backend changes, no new game mechanics, no card content. This plan enhances *presentation* of existing mechanics only.
- **RISK-002:** Audio assets bloat the repo — mitigate by compressing all audio to low-bitrate MP3 (64kbps for SFX, 96kbps for ambient). Total audio budget: < 1MB.
- **RISK-003:** Vanilla JS animation code becomes unwieldy — mitigate by keeping `effects.js` under 200 lines with well-named utility functions. If it grows beyond that, split into `effects.js` (visual) and `transitions.js` (page-level).
- **ALT-001:** Use a lightweight animation library (anime.js, GSAP) instead of custom CSS/JS — rejected because the constraint is zero dependencies, and the animations needed are simple enough for vanilla CSS + requestAnimationFrame.
- **ALT-002:** Use Web Audio API for procedural sound generation instead of audio files — considered as fallback if licensing is problematic, but pre-recorded SFX sound better for the effort. Keep as Plan B for PHASE-02.

## Grill Me

1. **Q-001:** Should sound effects be generated procedurally via Web Audio API (zero file size, but less polished) or sourced as royalty-free audio files (better quality, adds ~500KB-1MB to repo)?
   - **Recommended default:** Royalty-free audio files from freesound.org/pixabay (CC0 licensed).
   - **Why this matters:** Affects PHASE-02 task complexity and repo size. Procedural audio requires more JS code but zero assets; file-based audio sounds better but adds download weight.
   - **If answered differently:** If procedural, TASK-02-02 and TASK-02-03 are replaced with Web Audio API synthesis code in `audio.js`, and the `audio/` directory is not needed.

2. **Q-002:** What performance grade scale should the summary use — the current simple A/B/C or a more granular S/A/B/C/D/F scale common in games?
   - **Recommended default:** S/A/B/C/D (5 tiers, no F — even a poor run gets a D, which feels less punishing).
   - **Why this matters:** Affects PHASE-03 TASK-03-06 scoring logic and the share text format.
   - **If answered differently:** If keeping A/B/C, TASK-03-06 is simpler but less game-like.

3. **Q-003:** Should the XP/progression system persist across games (global player profile) or reset per game?
   - **Recommended default:** Per-game XP with a global "lifetime XP" counter shown on the main menu. Each game starts at Level 1, but your total XP across all games is tracked.
   - **Why this matters:** Affects PHASE-03 localStorage schema and whether the index page needs a profile display.
   - **If answered differently:** If global-only, a single game won't show level progression (you'd already be high level); if per-game-only, there's no cross-session incentive.

## Suggested Next Step

Answer the 3 Grill Me questions (or accept the recommended defaults), then begin PHASE-01 implementation. Each phase can be committed independently and tested before proceeding to the next.
