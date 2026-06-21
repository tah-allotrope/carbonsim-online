# Research Brief: Management/Tycoon Game Design & Architecture → CarbonSim (rerun)

**Date:** 2026-06-20
**Modes run:** domain, codebase
**Depth:** standard
**Invocation context:** Rerun on the upgraded research skill for a briefs comparison. Extract design philosophy + simulation architecture from Kairosoft, Sid Meier, and tycoon games (RCT/OpenTTD, Theme Hospital, Capitalism, Factorio) and map onto CarbonSim Online (FastAPI + vanilla JS + canvas). Prior standard brief: [research/2026-06-20_sim-game-design-architecture.md](research/2026-06-20_sim-game-design-architecture.md).

> Rerun note: same topic, same depth, same verified source base as the prior brief. Evidence and conclusions are unchanged on re-examination; this artifact restates them compactly for side-by-side comparison and sharpens the **delta vs. the first brief** in each Synthesis. No contradictions surfaced against the earlier run.

---

## Synthesis

Three design traditions share one spine. **Sid Meier:** a game is "a series of interesting decisions," and every choice needs *impact and clarity* — he cut a Civ4 government feature because hidden math meant "the computer was having all the fun" ([Designer Notes — Sid's Rules](http://www.designer-notes.com/game-developer-column-5-sids-rules/)). Balance in big swings: "double it or cut it in half," not 5% tweaks (ibid.). **Kairosoft:** a short compulsion loop with relentless "number-go-up" progression and combinatorial discovery manufactures "one more year" ([Entertainment Analytical](https://entertainmentanalytical.blog/2024/06/01/kairosoft-games-progression-mastered/)). **Tycoons:** depth emerges from many simple autonomous agents over a deterministic core — RCT's "peeps" run "quite a primitive algorithm" that still looks "human" ([Arcade Attack — Sawyer](https://www.arcadeattack.co.uk/chris-sawyer-interview/)). Unifying them is Dormans' frame: games are **internal economies** of sources/drains/converters wired by **feedback loops**, best balanced by simulating thousands of runs before building ([Game Developer — Machinations](https://www.gamedeveloper.com/design/the-designer-s-notebook-machinations-a-new-way-to-design-game-mechanics)).

The architecture lesson is equally consistent: **a deterministic state core, separated from rendering, mutated only by validated commands, with disciplined RNG and caches.** OpenTTD ships *commands* not state because "without a player interfering a vehicle follows its orders always in the same way"; desyncs come from un-invalidated caches and divergent RNG order, caught by per-frame RNG checksums ([desync.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/desync.md)). Factorio runs the same deterministic-lockstep model and CRCs the whole map every tick ([Factorio Wiki](https://wiki.factorio.com/Desynchronization)).

CarbonSim already embodies most of this: a pure reducer (`apply_company_decision(state, action, payload) -> state`, gated to `DECISION_WINDOW`), an explicit phase state machine, JSON-driven card decks with choice overrides, an `audit_log` event stream, zlib-JSON state serialization, and a `snapshot` the canvas renders as a pure projection ([engine.py](engine/engine.py), [cards.py](engine/cards.py), [db.py](server/db.py)). The gaps are disciplinary, not structural: **unseeded RNG** (no reproducible replay), **no modeled negative feedback loop** (dominant-strategy risk), **AI competitors are scoreboard rows not agents**, and **decisions hide their projected outcomes** (Sid's clarity rule).

[NOTE] Re-examination confirms the prior brief's central claim — this is an **evolution, not a rewrite**. The single core-touching change (a per-game seed in state) is also the highest-leverage one: it turns the existing `audit_log` into a true replay/event-source and makes Monte-Carlo balancing meaningful.

## Domain

### Discovery
Canonical sources, unchanged from the prior run and re-confirmed: Soren Johnson's *Designer Notes* "Sid's Rules" ([link](http://www.designer-notes.com/game-developer-column-5-sids-rules/)) and Game Developer's "Key Design Lessons" ([link](https://www.gamedeveloper.com/pc/analysis-sid-meier-s-key-design-lessons)); Meier's GDC 2010 keynote "The Psychology of Game Design" ([GDC Vault](https://gdcvault.com/play/1012186/The-Psychology-of-Game-Design)); Adams & Dormans' Machinations ([Game Developer](https://www.gamedeveloper.com/design/the-designer-s-notebook-machinations-a-new-way-to-design-game-mechanics), book [ref](https://research.hva.nl/en/publications/game-mechanics-advanced-game-design/)); Kairosoft progression analysis ([Entertainment Analytical](https://entertainmentanalytical.blog/2024/06/01/kairosoft-games-progression-mastered/)); tycoon architecture via [OpenTTD desync.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/desync.md), [OpenRCT2](https://github.com/OpenRCT2/OpenRCT2/), and the Factorio determinism corpus ([FFF #47](https://www.factorio.com/blog/post/fff-47)); game-feel via "Juice it or lose it."

### Verification
Primary or near-primary and mutually consistent. The doubling/halving rule, "interesting decisions," the *Covert Action* "one good game" rule, and "the player should have the fun, not the designer or the computer" are quoted from the column written by Civ4's lead designer — high reliability. Player-optimism ("a player always expects to win a 1.5-to-0.5 battle") is corroborated across multiple independent reports of the same keynote. OpenTTD's command/RNG/cache mechanics are from the project's own engineering docs. Weakness flagged (unchanged): Kairosoft's internal formulas are deliberately undocumented, so claims about its *mechanism* are softer than claims about its *effect*.

### Comparison
Where depth comes from, per tradition:
- **Meier — decision-centric:** a few high-impact, *legible* choices; subsystems obey a hierarchy (*Pirates!*/*X-Com* succeed because mini-games serve one dominant loop; *Covert Action* failed because two strong systems "fought with each other") ([Sid's Rules](http://www.designer-notes.com/game-developer-column-5-sids-rules/)).
- **Kairosoft — progression-centric:** drip of unlocks + hidden combination depth over a low-friction loop ([Entertainment Analytical](https://entertainmentanalytical.blog/2024/06/01/kairosoft-games-progression-mastered/)).
- **Tycoons — simulation-centric:** emergent behavior from simple autonomous agents; the player shapes a system, not outcomes ([Sawyer interview](https://www.arcadeattack.co.uk/chris-sawyer-interview/)).
- **Dormans — economy-centric (unifying):** the design lever is the feedback loop; positive loops snowball, negative loops stabilize; balance by simulating thousands of runs ([Machinations](https://www.gamedeveloper.com/design/the-designer-s-notebook-machinations-a-new-way-to-design-game-mechanics)).
Across all, **juice is additive** — layer feedback (screenshake, particles, tweens, sound) onto a core that already works, never as a substitute ("Juice it or lose it").

### Synthesis
Actionable doctrine for CarbonSim (unchanged in substance; tightened): (1) keep turns to 2-3 *interesting, legible* decisions and show each option's projected consequence pre-commit; (2) tune economy constants by doubling/halving, then validate via Monte-Carlo; (3) engineer ≥1 stabilizing negative feedback loop; (4) add a Kairosoft-style progression drip (tech reveals, combinatorial abatement synergies, per-year personal-best beats); (5) promote AI companies to goal-driven agents; (6) bind a juice flourish to every economic event.

**Delta vs. first brief:** none in conclusions. The only refinement is prioritization — re-examination elevates **decision legibility** (showing projected outcomes) as the cheapest high-impact win, since the card-choice plumbing already exists and only the consequence-preview is missing.

### Confidence
High — design claims sourced to the designers themselves and a standard academic framework; only Kairosoft internals are intentionally opaque.

## Codebase

### Discovery
Relevant CarbonSim architecture: `engine/engine.py` (state machine + reducers + `apply_shock` + year cycle), `engine/cards.py` (deck, weighted draw, `resolve_card` choice override), `engine/playtest.py` (automated play harness), `server/db.py` (zlib state (de)serialization), `server/routes/game.py` (command endpoints), `server/ws.py` (co-op), and the frontend `web/js/isocity.js` / `effects.js` / `audio.js` (projection + juice).

### Verification
Confirmed in source this session:
- **Pure reducer core**, rejecting actions outside `PHASE_DECISION_WINDOW` ([engine.py:150-162](engine/engine.py)) — OpenTTD's command pattern.
- **Explicit phase machine** `LOBBY → YEAR_START → DECISION_WINDOW → COMPLIANCE → COMPLETE (+PAUSED)` ([engine.py:540-575](engine/engine.py)) — turn/phase-based, not continuous-tick; appropriate for a policy game.
- **Event stream** via `_append_event`/`_event_summary` into `audit_log` ([engine.py:1731-1785](engine/engine.py)) — latent event-sourcing.
- **Data-driven typed effects:** `apply_shock` dispatches 11 effects across all companies ([engine.py:1307-1416](engine/engine.py)); choices override `effect_type`/`effect_params` ([cards.py:126-166](engine/cards.py)).
- **State serialization:** zlib-JSON in SQLite ([db.py](server/db.py)); snapshot is a pure projection to the canvas.
- **Gap — non-deterministic RNG:** `CardDeck` defaults to an unseeded `random.Random()` ([cards.py:20-23](engine/cards.py)); no per-game seed in state → sessions are not reproducible.

### Comparison
| Reference pattern | CarbonSim today | Action |
|---|---|---|
| Deterministic core, separate from render (OpenTTD/Factorio) | ✅ reducer + snapshot + canvas | Keep; never move logic into JS |
| Validated command pattern (OpenTTD test-run→execute) | ✅ phase-gated `apply_company_decision` | For co-op, broadcast commands + re-apply (lockstep) vs. syncing state |
| Seeded RNG for replay (OpenTTD/Factorio CRC) | ❌ unseeded | Thread `seed` into `create_initial_state`, persist in state |
| Event sourcing / replay | ◐ `audit_log` not replayed | Make (seed + command log) replay sessions; reuse for undo/analytics/summary |
| Internal economy w/ feedback loops (Dormans) | ◐ economy exists, loops unmodeled | Add ≥1 negative loop; document as a Machinations diagram |
| Data-driven content | ✅ cards; ◐ economy/abatement constants in code | Move constants to data for balance sweeps |
| Autonomous agents (RCT peeps) | ❌ AI = scoreboard rows | Goal + simple abatement/trade policy per company |
| Juice over correct core | ✅ effects/audio/isocity | Bind a flourish to every economic event |
| Decision clarity (Sid) | ◐ choices exist, outcomes hidden | Show projected compliance/cash delta per option |

### Synthesis
Re-build sequence (re-confirmed): **(1) determinism** — seed in state, route all randomness through it (this alone upgrades `audit_log` to a replay/event-source and unlocks meaningful Monte-Carlo); **(2) economy modeling** — diagram sources/drains/converters, add a stabilizing negative loop, sweep constants via `playtest.py` to detect dominant strategies; **(3) legible decisions** — compute/show each option's projected outcome; **(4) agents** — goal-driven AI companies for emergent markets; **(5) progression + juice**. Steps 3-5 build on existing reducer/snapshot/juice layers; only step 1 touches the core, minimally.

**Delta vs. first brief:** identical roadmap. The rerun adds one implementation note — because `apply_shock` and `resolve_card` already pass deterministic state through pure functions, threading a seed is a localized change (engine state + `CardDeck` construction), not a cross-cutting refactor.

### Confidence
High for the architecture mapping (verified in source); Medium for the economy-balancing recommendations, which need empirical Monte-Carlo runs against CarbonSim's specific numbers to confirm a dominant strategy exists.

## Sources
- [Designer Notes — "Sid's Rules" (Soren Johnson)](http://www.designer-notes.com/game-developer-column-5-sids-rules/) — primary; interesting decisions, doubling/halving, Covert Action rule, "player has the fun."
- [Game Developer — Sid Meier's Key Design Lessons](https://www.gamedeveloper.com/pc/analysis-sid-meier-s-key-design-lessons) — corroborating summary.
- [GDC Vault — The Psychology of Game Design (Sid Meier, 2010)](https://gdcvault.com/play/1012186/The-Psychology-of-Game-Design) — player optimism, winner paradox, perceived fairness.
- [Game Developer — Machinations (Adams/Dormans)](https://www.gamedeveloper.com/design/the-designer-s-notebook-machinations-a-new-way-to-design-game-mechanics) + book *Game Mechanics: Advanced Game Design* ([ref](https://research.hva.nl/en/publications/game-mechanics-advanced-game-design/)) — internal economies, feedback loops, pre-build simulation.
- [Entertainment Analytical — Kairosoft: Progression Mastered](https://entertainmentanalytical.blog/2024/06/01/kairosoft-games-progression-mastered/) + [Wikipedia — Compulsion loop](https://en.wikipedia.org/wiki/Compulsion_loop) — number-go-up, drip progression.
- [OpenTTD — docs/desync.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/desync.md) — primary; deterministic sim, command transmission, RNG checksums, cache desyncs, replay.
- [Factorio Wiki — Desynchronization](https://wiki.factorio.com/Desynchronization) + [FFF #47](https://www.factorio.com/blog/post/fff-47) — deterministic lockstep, whole-map CRC per tick.
- [RollerCoaster Tycoon — Wikipedia](https://en.wikipedia.org/wiki/RollerCoaster_Tycoon) / [OpenRCT2](https://github.com/OpenRCT2/OpenRCT2/) / [Arcade Attack — Chris Sawyer interview](https://www.arcadeattack.co.uk/chris-sawyer-interview/) — assembly optimization, agent-based "peep" simulation.
- [Juice it or lose it (Jonasson & Purho)](https://www.gamedeveloper.com/design/squeezing-more-juice-out-of-your-game-design-) + Vlambeer "The Art of Screenshake" + Steve Swink, *Game Feel* — additive feedback over a working core.
- CarbonSim source: [engine/engine.py](engine/engine.py), [engine/cards.py](engine/cards.py), [engine/playtest.py](engine/playtest.py), [server/db.py](server/db.py), [web/js/isocity.js](web/js/isocity.js).
