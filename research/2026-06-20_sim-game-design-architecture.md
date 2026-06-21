# Research Brief: Design Philosophy & Simulation Architecture of Management/Tycoon Games — Applied to CarbonSim

**Date:** 2026-06-20
**Modes run:** domain, codebase
**Depth:** standard
**Invocation context:** Understand the philosophy, design, and architecture of resource-management games (Kairosoft, Sid Meier, tycoons) so CarbonSim Online (FastAPI + vanilla JS + canvas isometric renderer) can be re-built with comparable sophistication. Map findings back to CarbonSim's existing stack.

---

## Synthesis

Three traditions converge on the same spine. **Sid Meier** treats a game as "a series of interesting decisions" where every choice must have both *impact and clarity* — he cut a Civ4 government system because its hidden math meant "the computer was having all the fun" ([Designer Notes — Sid's Rules](http://www.designer-notes.com/game-developer-column-5-sids-rules/)). **Kairosoft** runs a tight compulsion loop with relentless "number-go-up" progression and combinatorial discovery that produces "one more year" pull ([Entertainment Analytical](https://entertainmentanalytical.blog/2024/06/01/kairosoft-games-progression-mastered/)). **The tycoon lineage** (RollerCoaster/Transport Tycoon, Theme Hospital) builds depth from many simple autonomous agents over a deterministic core ([RCT — Wikipedia](https://en.wikipedia.org/wiki/RollerCoaster_Tycoon); [OpenTTD desync docs](https://github.com/OpenTTD/OpenTTD/blob/master/docs/desync.md)). Underneath all three sits Joris Dormans' formal view of games as **internal economies of sources, drains, converters and feedback loops** that should be simulated and balanced *before* implementation ([Game Developer — Machinations](https://www.gamedeveloper.com/design/the-designer-s-notebook-machinations-a-new-way-to-design-game-mechanics)).

The architecture lesson is remarkably consistent: **a deterministic state core, strictly separated from rendering, mutated only through validated commands, with RNG and caches disciplined for reproducibility.** OpenTTD ships only *commands* over the network and re-simulates locally because "without a player interfering a vehicle follows its orders always in the same way"; desyncs come from un-invalidated caches and divergent RNG call order, caught by per-frame RNG checksums ([desync.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/desync.md)). Factorio uses the same deterministic-lockstep model and CRC-checks the whole map every tick ([Factorio Wiki — Desynchronization](https://wiki.factorio.com/Desynchronization)).

**CarbonSim already has ~70% of this architecture and doesn't know it.** Its engine is a pure reducer (`apply_company_decision(state, action, payload) -> state`, gated to the `DECISION_WINDOW` phase) over a JSON-serializable state dict, with an `audit_log` event stream, zlib state serialization, and a `snapshot` that the canvas renders as a pure projection ([engine.py](engine/engine.py), [db.py](server/db.py)). The signature gaps are not structural but *disciplinary*: (1) card/economy randomness uses an **unseeded** `random.Random()` so sessions are not reproducible or replayable ([cards.py](engine/cards.py)); (2) the internal economy has **no modeled negative feedback loops**, risking a dominant strategy; (3) AI competitors are scoreboard rows, not strategic agents; (4) player decisions don't surface their *projected* consequences, violating Sid's clarity rule.

[NOTE] The right move is *not* a rewrite. It is to (a) thread a per-game seed into state to unlock deterministic replay/event-sourcing on top of the existing `audit_log`, (b) formalize the economy as a Machinations-style model and Monte-Carlo it through the existing playtest harness, (c) promote AI companies to simple goal-driven agents, and (d) add a legibility/juice layer that makes every state change show its cause and effect. These are additive changes to a sound core.

## Domain

### Discovery
The strongest, most citable sources cluster by theme. **Design philosophy:** Soren Johnson's *Designer Notes* column "Sid's Rules" is the canonical write-up of Meier's heuristics ([link](http://www.designer-notes.com/game-developer-column-5-sids-rules/)); Game Developer's "Sid Meier's Key Design Lessons" corroborates ([link](https://www.gamedeveloper.com/pc/analysis-sid-meier-s-key-design-lessons)); Meier's GDC 2010 keynote "The Psychology of Game Design (Everything You Know Is Wrong)" is the source for player-optimism findings ([GDC Vault](https://gdcvault.com/play/1012186/The-Psychology-of-Game-Design), [Game Developer video](https://www.gamedeveloper.com/design/video-sid-meier-s-psychology-of-game-design)). **Economy/feedback theory:** Adams & Dormans, *Game Mechanics: Advanced Game Design*, and the Machinations framework ([Game Developer](https://www.gamedeveloper.com/design/the-designer-s-notebook-machinations-a-new-way-to-design-game-mechanics)). **Kairosoft loop:** Entertainment Analytical's "Progression Mastered" plus the compulsion-loop literature ([Wikipedia](https://en.wikipedia.org/wiki/Compulsion_loop)). **Tycoon architecture:** OpenTTD's `desync.md`, OpenRCT2, and the Factorio determinism corpus. **Juice:** Jonasson & Purho's "Juice it or lose it" and Vlambeer's "Art of screenshake".

### Verification
These are primary or near-primary and mutually consistent. The doubling/halving rule, "interesting decisions," the *Covert Action* "one good game" rule, and "the player should have the fun, not the designer or the computer" are quoted directly from the Designer Notes column written by Civ4's lead designer ([link](http://www.designer-notes.com/game-developer-column-5-sids-rules/)) — high reliability. Player-optimism ("players expect to win a 1.5-to-0.5 battle and feel cheated when they lose") is from multiple independent reports of the same GDC keynote. OpenTTD's command/RNG/cache claims come from the project's own engineering docs. Kairosoft's internal formulas are deliberately opaque (players reverse-engineer them), so claims about *mechanism* are weaker than claims about *effect* (the loop is demonstrably sticky) — flagged accordingly.

### Comparison
The traditions differ mainly in **where depth comes from**:
- **Sid Meier (decision-centric):** depth = a few high-impact, *legible* choices per turn; balance via large multipliers ("double it or cut it in half") not fine tweaks ([Sid's Rules](http://www.designer-notes.com/game-developer-column-5-sids-rules/)). Subsystems obey a hierarchy — *Pirates!* and *X-Com* work because mini-games serve one dominant loop; *Covert Action* failed because two strong systems "fought with each other."
- **Kairosoft (progression-centric):** depth = a steady drip of unlocks and combinatorial reveals over a short, low-friction loop; the *number going up* and hidden combination tables (genre × type) create discovery and "one more year" compulsion ([Entertainment Analytical](https://entertainmentanalytical.blog/2024/06/01/kairosoft-games-progression-mastered/)).
- **Tycoons (simulation-centric):** depth = emergent behavior from many simple autonomous agents. RCT's guests ("peeps") run "quite a primitive algorithm" that nonetheless looks "human" ([Arcade Attack — Sawyer interview](https://www.arcadeattack.co.uk/chris-sawyer-interview/)); the player shapes a system rather than scripting outcomes.
- **Dormans (economy-centric, unifying):** all of the above are *internal economies*; the design lever is the **feedback loop**. Positive loops snowball (rich-get-richer), negative loops stabilize; balance by *simulating thousands of runs* to find volatility and dominant strategies before building ([Machinations](https://www.gamedeveloper.com/design/the-designer-s-notebook-machinations-a-new-way-to-design-game-mechanics)).

Across all four, **juice is the same and additive**: take a core that already works, then layer screenshake, particles, tweens, and sound so each state change *feels* causal ("Juice it or lose it"). Juice is never a substitute for a correct economy.

### Synthesis
For CarbonSim, the actionable doctrine is:
1. **Make every turn a small set of interesting, *legible* decisions.** Abatement vs. offsets vs. paying the penalty is already a real cost curve; the missing piece is *showing the projected consequence* of each option before the player commits (Sid's clarity rule). Event cards now have choices (fixed this session) — keep them to 2-3 options with visibly different outcomes.
2. **Balance in big swings, then simulate.** Tune economy constants by doubling/halving, and validate with Monte-Carlo runs through the playtest harness rather than hand-feel.
3. **Engineer one or two stabilizing negative feedback loops** (e.g., rising offset prices as demand climbs; cap decline that bites harder when everyone over-emits) so no single strategy dominates — the central Dormans lesson.
4. **Add a Kairosoft progression drip**: titles/XP exist; add tech-unlock reveals, combinatorial abatement synergies, and per-year "personal best" beats to manufacture "one more year."
5. **Promote AI companies to simple agents** with goals/strategies so the market and leaderboard become emergent, not scripted.
6. **Juice on top, not instead**: tie a feedback flourish to every economic event (already partially present via `effects.js`/`isocity.js` floaters).

### Confidence
High — design claims are sourced to the designers themselves (Johnson/Meier) and a standard academic framework (Adams/Dormans); only Kairosoft's internal formulas are intentionally undocumented.

## Codebase

### Discovery
CarbonSim's relevant architecture lives in: `engine/engine.py` (state machine + reducers + shocks + year cycle), `engine/cards.py` (deck, weighted draw, `resolve_card` with choice override), `engine/playtest.py` (automated play harness), `server/db.py` (zlib state (de)serialization), `server/routes/game.py` (command endpoints), `server/ws.py` (co-op), and the frontend juice/projection layer `web/js/isocity.js`, `web/js/effects.js`, `web/js/audio.js`.

### Verification
Confirmed directly in source this session:
- **Pure reducer core:** `apply_company_decision(state, *, company_id, action, payload, now)` returns new state and rejects anything outside `PHASE_DECISION_WINDOW` ([engine.py:150-162](engine/engine.py)). This is exactly OpenTTD's command pattern — validated mutation of canonical state.
- **Explicit state machine:** `PHASE_LOBBY → YEAR_START → DECISION_WINDOW → COMPLIANCE → COMPLETE` (+ `PAUSED`) with `_set_phase` transitions ([engine.py:540-575](engine/engine.py)). Turn/phase-based, not continuous-tick — appropriate for a policy game.
- **Event stream:** every mutation appends to `audit_log` via `_append_event` with a human `_event_summary` ([engine.py:1731-1785](engine/engine.py), [cards.py:187](engine/cards.py)) — a latent event-sourcing substrate.
- **Effects as data-driven shocks:** `apply_shock` dispatches 11 typed effects over all companies ([engine.py:1307-1416](engine/engine.py)); cards are JSON-driven and choices override `effect_type`/`effect_params` ([cards.py:126-166](engine/cards.py)).
- **State serialization:** zlib-compressed JSON in SQLite ([db.py](server/db.py)); snapshot is a pure projection consumed by the canvas renderer (`Isocity.update(snapshot)`).
- **Gap — non-deterministic RNG:** `CardDeck` defaults to a fresh, unseeded `random.Random()` ([cards.py:20-23](engine/cards.py)); no per-game seed is threaded into state. So identical inputs do **not** reproduce a session — the one place CarbonSim diverges from the OpenTTD/Factorio determinism discipline.

### Comparison
| Pattern (reference games) | CarbonSim today | Action |
|---|---|---|
| Deterministic state core, separate from render (OpenTTD/Factorio) | ✅ engine reducer + snapshot + canvas projection | Keep; never move game logic into JS |
| Command pattern with validation (OpenTTD test-run→execute) | ✅ `apply_company_decision` gated by phase | For co-op, broadcast commands and re-apply deterministically (lockstep) instead of syncing state |
| Seeded RNG in state for replay (OpenTTD checksums / Factorio CRC) | ❌ unseeded `random.Random()` | Thread `seed` into `create_initial_state`; persist in state |
| Event sourcing / replay log | ◐ `audit_log` exists but isn't replayed | Make (seed + command log) replay the whole session; reuse for undo, analytics, summary |
| Internal economy with feedback loops (Dormans) | ◐ economy exists, loops unmodeled | Add ≥1 negative loop; document as a Machinations diagram |
| Data-driven content (cards JSON) | ✅ cards; ◐ abatement/economy constants in code | Move economy constants + abatement menu to data for balance sweeps |
| Autonomous agents (RCT peeps) | ❌ AI = scoreboard rows | Give companies goals + a simple abatement/trade policy |
| Juice over correct core (Vlambeer/Swink) | ✅ `effects.js`/`audio.js`/`isocity.js` | Bind a flourish to every economic event; keep core authoritative |
| Decision clarity (Sid) | ◐ choices exist, outcomes hidden | Show projected compliance/cash delta per option pre-commit |

### Synthesis
The re-build is an **evolution, not a rewrite**. Sequence: (1) **Determinism** — add a per-game seed to state and route all randomness through it; this single change converts `audit_log` into a true replay/event-source and makes Monte-Carlo balancing meaningful. (2) **Economy modeling** — diagram the sources/drains/converters, introduce a stabilizing negative feedback loop, and sweep constants through `playtest.py` to detect dominant strategies (Dormans). (3) **Legible decisions** — compute and display each option's projected outcome so the player, not the engine, "has the fun" (Sid). (4) **Agents** — upgrade AI companies to goal-driven policies for emergent markets (tycoon). (5) **Progression + juice** — drip unlocks/reveals and bind feedback to every event (Kairosoft + game-feel). Items 3-5 build cleanly on the existing reducer/snapshot/juice layers; only item 1 touches the core, and minimally.

### Confidence
High for the architecture mapping (verified in source this session); Medium for the economy-balancing recommendations, which are sound in theory but need empirical Monte-Carlo runs against CarbonSim's specific numbers to confirm a dominant strategy exists.

## Sources
- [Designer Notes — "Sid's Rules" (Soren Johnson)](http://www.designer-notes.com/game-developer-column-5-sids-rules/) — primary; interesting decisions, doubling/halving, Covert Action rule, "player has the fun."
- [Game Developer — Analysis: Sid Meier's Key Design Lessons](https://www.gamedeveloper.com/pc/analysis-sid-meier-s-key-design-lessons) — corroborating summary of Meier's heuristics.
- [GDC Vault — The Psychology of Game Design (Sid Meier, 2010)](https://gdcvault.com/play/1012186/The-Psychology-of-Game-Design) / [Game Developer video](https://www.gamedeveloper.com/design/video-sid-meier-s-psychology-of-game-design) — player optimism, "winner paradox," perceived fairness.
- [Game Developer — Machinations: A New Way to Design Game Mechanics (Adams/Dormans)](https://www.gamedeveloper.com/design/the-designer-s-notebook-machinations-a-new-way-to-design-game-mechanics) — internal economies, sources/drains/converters, feedback loops, pre-build simulation. Book: *Game Mechanics: Advanced Game Design* ([ref](https://research.hva.nl/en/publications/game-mechanics-advanced-game-design/)).
- [Entertainment Analytical — Kairosoft: Progression Mastered](https://entertainmentanalytical.blog/2024/06/01/kairosoft-games-progression-mastered/) + [Wikipedia — Compulsion loop](https://en.wikipedia.org/wiki/Compulsion_loop) — number-go-up, drip progression, loop stickiness.
- [OpenTTD — docs/desync.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/desync.md) — primary; deterministic sim, command transmission, RNG checksums, cache-induced desyncs, savegame+command-log replay.
- [Factorio Wiki — Desynchronization](https://wiki.factorio.com/Desynchronization) / [FFF #47 — CRC fun](https://www.factorio.com/blog/post/fff-47) — deterministic lockstep, whole-map CRC per tick.
- [RollerCoaster Tycoon — Wikipedia](https://en.wikipedia.org/wiki/RollerCoaster_Tycoon) / [OpenRCT2](https://github.com/OpenRCT2/OpenRCT2/) / [Arcade Attack — Chris Sawyer interview](https://www.arcadeattack.co.uk/chris-sawyer-interview/) — assembly optimization, agent-based "peep" simulation.
- [Juice it or lose it (Jonasson & Purho)](https://www.gamedeveloper.com/design/squeezing-more-juice-out-of-your-game-design-) + Vlambeer "The Art of Screenshake" + Steve Swink, *Game Feel* — additive feedback layer over a working core.
- CarbonSim source (this repo): [engine/engine.py](engine/engine.py), [engine/cards.py](engine/cards.py), [engine/playtest.py](engine/playtest.py), [server/db.py](server/db.py), [web/js/isocity.js](web/js/isocity.js).
