# Research Brief: Management/Tycoon Game Design & Simulation Architecture → CarbonSim (exhaustive)

**Date:** 2026-06-21
**Modes run:** domain, codebase
**Depth:** exhaustive
**Invocation context:** `/research management/tycoon game design & simulation architecture for CarbonSim --depth exhaustive`. Extract design philosophy + engine architecture from Kairosoft, Sid Meier, and tycoon/management/automation sims and map onto CarbonSim Online (FastAPI + vanilla JS + canvas; deterministic Python reducer, phase state machine, JSON card decks, audit_log, zlib state serialization, snapshot rendering). Builds on the prior standard briefs ([1](research/2026-06-20_sim-game-design-architecture.md), [2](research/2026-06-20_sim-game-design-architecture-2.md)).
**Sources (wide/cited):** ~224 gathered / 35 cited | **Ratio used:** github=0.30, industry=0.30, web=0.25, academia=0.15

---

## Synthesis

The exhaustive pass confirms the prior briefs' thesis and adds a concrete architectural twin: **OpenRCT2 is almost exactly what CarbonSim already is** — every state change flows through a validated game-command, a replay system records the command stream, and desync is caught by comparing RNG-state checksums with snapshot resync ([Game Commands](https://github.com/OpenRCT2/OpenRCT2/wiki/Game-Commands), [Replay System](https://github.com/OpenRCT2/OpenRCT2/wiki/Replay-System), [Game Synchronization](https://deepwiki.com/OpenRCT2/OpenRCT2/6.2-game-synchronization)). That is CarbonSim's reducer + `audit_log` + `snapshot` triad. OpenTTD (command-only sync, chunked versioned saves) and the determinism canon (Gaffer On Games on [float determinism](https://gafferongames.com/post/floating_point_determinism/) and [lockstep](https://gafferongames.com/post/deterministic_lockstep/); Age of Empires' [1500 Archers](https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond); Factorio's "deterministic or desync" discipline, [FFF #204](https://factorio.com/blog/post/fff-204)) all converge on one rule: **sync inputs, recompute state, and a saved seed + command log reproduces any run exactly** ([PRNG replay](https://www.gamedeveloper.com/design/prngs-and-controlling-fate-in-video-games)).

On design, the canon is tight and mutually reinforcing. Sid Meier: a decision is interesting only when no option dominates, options are unequal, and the player chooses informedly with **visible consequences** ([Interesting Decisions](https://www.gdcvault.com/play/1015756/Interesting)); balance in big swings ("double it or cut it in half"); and **"theme is not meaning" — meaning lives in mechanics, not flavor text** ([Designer Notes 12](http://www.designer-notes.com/game-developer-column-12-theme-is-not-meaning-part-ii/)), which is decisive for a *carbon* game. His "water finds a crack" warns that players optimize any exploitable loop, so balance must be adversarial and simulation-validated ([Designer Notes 17](https://www.designer-notes.com/game-developer-column-17-water-finds-a-crack/)). Dormans supplies the formal economy frame (sources/drains/converters/traders; positive loops snowball, negative loops stabilize), and the failure mode is the **runaway-leader problem**, whose remedy is engineered negative feedback / rubber-banding ([Engineering Emergence](https://eprints.illc.uva.nl/id/eprint/2118/1/DS-2012-12.text.pdf), [runaway leader](https://oakleafgames.wordpress.com/2014/02/13/game-theory-runaway-leader-rubber-banding-and-feedback/)). Kairosoft shows depth-from-a-lookup-table (genre×type combination ratings) over a tight loop ([combination tables](https://kairosoft.wiki.gg/wiki/Genres_and_types_(Game_Dev_Story))); RimWorld reframes the sim as a **story generator** ([GDC 2017](https://www.youtube.com/watch?v=VdqhHKjepiE)); and juice (Swink's taxonomy; [Juice it or lose it](https://www.youtube.com/watch?v=Fy0aCDmgnxg); [Art of Screenshake](https://www.youtube.com/watch?v=AJdEqssNZ-U)) is additive polish — with the explicit caveat that it must serve clarity, not [mask weak mechanics](https://www.gamedeveloper.com/design/video-indies-resist-the-urge-to-juice-it-or-lose-it-).

[NOTE] The single sharpest new finding vs. the prior briefs: CarbonSim's negative pressure is **exogenous and scripted** (a linear cap decline in `scenarios.py`), not an **endogenous feedback loop**. Static offset pricing means an optimal strategy can't be self-correcting — the runaway-leader risk Dormans warns about. The highest-value mechanical upgrade is a demand-responsive offset price (a [BazaarBot](https://github.com/larsiusprime/bazaarBot)-style negative loop), validated by extending the seeded Monte-Carlo harness that already exists.

[NOTE] Scope discipline from the evidence: do **not** adopt ECS or lockstep. ECS (Overwatch, flecs) pays off at thousands of entities; CarbonSim has ~8 companies, so a pure reducer is the right call. Co-op is turn-based, so authoritative-server state-sync (what `ws.py` already does) is correct — lockstep is for real-time RTS. The transferable lessons are *determinism-for-replay* and *rules-as-data*, not networking model or ECS.

### Source Coverage
| bucket | target | gathered | qualified | cited | reallocated |
|---|---|---|---|---|---|
| github | 75 | 81 | 76 | 10 | absorbed academia overflow |
| industry | 75 | 62 | 50 | 12 | −13 (saturated at canon) |
| web | 62 | 68 | 58 | 8 | +6 over |
| academia | 38 | 13 | 11 | 5 | −25 (worker failed; recovered via main-thread mini-pass) |
| **total** | **250** | **~224** | **~195** | **35** | non-strict ratio |

## Domain

### Discovery
Strongest sources by theme. **Architecture twins:** OpenRCT2 (command/replay/checksum), OpenTTD ([desync.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/desync.md), [savegame_format.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/savegame_format.md)), MicropolisCore (headless deterministic city engine). **Determinism canon:** Gaffer On Games trilogy, 1500 Archers, Factorio FFFs, [GGRS](https://github.com/gschup/ggrs) rollback, [FixPointCS](https://github.com/XMunkki/FixPointCS). **Rules-as-data:** FreeOrion [FOCS](https://www.freeorion.org/index.php/FOCS_Scripting_Details), Unciv [rulesets/uniques](https://github.com/yairm210/Unciv/wiki/Project-structure-and-major-classes), [Cataclysm-DDA JSON copy-from](https://docs.cataclysmdda.org/JSON/JSON_INFO.html), openage [nyan](https://github.com/SFTtech/nyan). **Economy/feedback:** Dormans + Machinations ([book ch.5](https://www.oreilly.com/library/view/game-mechanics-advanced/9780132946728/ch05.html)), [Widelands Request/Supply](https://github.com/widelands/widelands/blob/master/src/economy/economy.cc), BazaarBot, [OpenTTD cargo formula](https://wiki.openttd.org/en/Manual/Game%20Mechanics/Cargo%20income). **Design philosophy:** Sid Meier (Interesting Decisions; [Psychology of Game Design](https://www.gdcvault.com/play/1012186/The-Psychology-of-Game)), Soren Johnson's Designer Notes columns. **Agents/story:** OpenRCT2 peeps, [Cities: Skylines traffic](https://www.gamedeveloper.com/design/game-design-deep-dive-traffic-systems-in-i-cities-skylines-i-), RimWorld, Dwarf Fortress. **Serious-games-for-climate (academia):** [robust-evaluation review](https://www.sciencedirect.com/science/article/abs/pii/S0272494426000435), [Waterloo cap-and-trade game](https://uwaterloo.ca/chemical-engineering/news/serious-game-teaches-students-how-cap-and-trade-reduces-co2). **Automated balancing (academia):** [curiosity-driven RL playtesting](https://arxiv.org/pdf/2103.13798), [Dungeons & Replicants](https://antoniosliapis.com/papers/dungeons_replicants_automated_game_balancing_across_multiple_difficulty_dimensions_via_deep_player_behavior_modeling.pdf), [FDG board-game playtesting](https://dl.acm.org/doi/10.1145/3102071.3102105).

### Verification
Architecture claims are primary (project engineering docs/wikis, designer talks) and cross-corroborated: OpenRCT2's command+replay+checksum, OpenTTD's command-only sync, AoE's lockstep, and Factorio's determinism independently state the same model — high reliability. Design rules are quoted from the designers (Meier keynote/talk; Johnson's columns). **Weak/flagged:** academia bucket under-delivered (worker failure; recovered ~13 sources by main-thread search) and several balancing/serious-game papers are paywalled (abstract-only); the serious-games review itself notes *robust evaluation evidence is limited*, so "games teach climate policy" is supported but not strongly. Kairosoft internals remain reverse-engineered (effect documented, mechanism inferred).

### Comparison
- **Determinism approaches:** command-only sync (OpenTTD/AoE) vs. snapshot+checksum resync (OpenRCT2) vs. rollback (GGRS). For a turn-based server-authoritative game, OpenRCT2's *record-commands-for-replay* (not networked rollback) is the closest fit; fixed-point math (FixPointCS) matters only if logic must be bit-identical across machines — **not required** for a single-authority Python engine, but float-ordering hygiene still applies.
- **Rules-as-data:** Unciv keeps the Ruleset **out of** serialized save state (only `GameInfo` is saved); FreeOrion's FOCS is a richer ValueRef/Condition/Effect DSL; Cataclysm uses JSON `copy-from` inheritance. CarbonSim's JSON cards sit at the simple end — the upgrade path is a small effect-DSL with inheritance, keeping decks out of saved state (the Unciv lesson).
- **Economy modeling:** scripted constants (OpenTTD cargo formula) vs. emergent agent markets (BazaarBot) vs. diagram-and-simulate (Machinations). CarbonSim is at "scripted constants"; the leverage is adding one emergent negative loop, not a full agent economy.
- **Depth source:** Sid Meier (few legible decisions) vs. Kairosoft (combinatorial drip) vs. RimWorld/DF (emergent story) vs. tycoon agents (peeps/citizens). These are complementary layers, not alternatives.

### Synthesis
Doctrine for CarbonSim, evidence-ranked: (1) **make the climate message mechanical** — "theme is not meaning"; the carbon cost curve *is* the lesson, flavor text isn't. (2) **Decisions need visible projected consequences** (Meier) — show each option's compliance/cash delta pre-commit. (3) **Add endogenous negative feedback** (demand-responsive offset price; rubber-banding) to kill dominant strategies, then **validate with seeded Monte-Carlo** (the harness exists). (4) **Evolve cards toward a small rules-as-data DSL** with inheritance, kept out of save state. (5) **Promote AI companies to goal-driven agents** (BazaarBot market participants) and frame events as a **story generator** (RimWorld). (6) **Layer juice on the working core**, serving clarity. Avoid ECS and lockstep (wrong scale / wrong loop).

### Confidence
High for architecture + design-philosophy (primary, heavily corroborated); Medium for the climate-pedagogy and automated-balancing claims (academia thin/paywalled, evaluation evidence acknowledged-limited).

## Codebase

### Discovery
CarbonSim modules surveyed directly: `engine/engine.py` (reducer + `apply_shock` + phase machine + `audit_log`), `engine/cards.py` (deck, `resolve_card` choice override), `engine/playtest.py` (seeded Monte-Carlo harness), `engine/scenarios.py` (`SCENARIO_PACKS` economy constants), `server/db.py` (zlib state), `server/ws.py` (co-op), `web/js/isocity.js`/`effects.js`/`audio.js` (snapshot projection + juice).

### Verification
- **OpenRCT2-twin confirmed:** `apply_company_decision` is the validated-command reducer; `audit_log`/`_event_summary` is the replay/event stream; `snapshot` is the projection. CarbonSim independently arrived at the OpenRCT2 triad ([engine.py](engine/engine.py)).
- **Balancing infra already exists:** `run_playtest(seed)` / `run_playtest_batch` run **seeded** simulations with per-difficulty aggregates and `dead_cards` detection ([playtest.py](engine/playtest.py)) — but the bot plays `choices[0]` greedily, so it won't find dominant strategies until given varied policies.
- **Determinism gap is isolated:** the **live** path never seeds the deck — `CardDeck` defaults to unseeded `random.Random()` ([cards.py:20-23](engine/cards.py)) — even though `playtest.py` already seeds. Wiring a per-game seed into `create_solo_game`/state is localized.
- **Economy is parameterized but not adaptive:** `SCENARIO_PACKS` centralizes `penalty_rate`, `offset_price`, `offset_usage_cap`, and a *scripted linear* cap decline (`allocation_factors = 1.0 − (y−1)·rate`) ([scenarios.py](engine/scenarios.py)). Exogenous difficulty ramp; no endogenous feedback.
- **Co-op is server-authoritative state-sync:** `ws.py` `broadcast_snapshot` pushes `participant_snapshot` to all clients — correct for turn-based; lockstep unnecessary.

### Comparison
| Reference pattern | CarbonSim today | Action |
|---|---|---|
| Command + replay + checksum (OpenRCT2) | ✅ reducer + audit_log + snapshot | Formalize audit_log as replay; add a state checksum for save integrity |
| Seed-in-state for replay (OpenTTD/PRNG) | ❌ live deck unseeded; ✅ in playtest | Thread per-game seed into state; route all RNG through it |
| Endogenous negative feedback (Dormans/BazaarBot) | ❌ only scripted cap decline | Demand-responsive offset price; rubber-banding vs. leader |
| Rules-as-data w/ inheritance (Unciv/FOCS/Cataclysm) | ◐ flat JSON cards | Small effect-DSL + copy-from; keep decks out of save state |
| Simulation-based balancing (RL/agent papers) | ◐ seeded harness, greedy bot | Add varied bot policies; sweep for win-rate/dominant strategy |
| Agent competitors (peeps/citizens) | ❌ scoreboard rows | Goal-driven company agents (market participants) |
| Juice serving clarity (Swink; counterpoint) | ✅ effects/audio/isocity | Bind to economic events; don't juice a passive loop |
| ECS / lockstep | ❌ (reducer; state-sync) | Keep as-is — correct for scale/turn-based |

### Synthesis
Re-build is an evolution. Ordered by leverage-per-effort: **(1)** seed-in-state (unlocks true replay on the existing `audit_log` + meaningful Monte-Carlo) — localized to `cards.py`/state init; **(2)** one endogenous negative feedback loop (demand-responsive offset price) — the core mechanical fix for dominant-strategy risk; **(3)** decision-consequence previews in the UI (cheap; card-choice plumbing already shipped); **(4)** extend `playtest.py` bots with varied strategies and a dominant-strategy/win-rate report; **(5)** evolve cards toward a small rules-as-data DSL kept out of save state; **(6)** goal-driven AI agents + story-generator event framing; **(7)** juice bound to economic events. Steps 3-7 ride existing layers; only 1-2 touch the core, minimally.

### Confidence
High — every codebase claim verified in source this session; the OpenRCT2-twin mapping and the seeded-harness-already-exists finding are directly observed, not inferred.

## Sources
*(Curated high-signal subset; full ~224-source ledger at [research/sources/2026-06-21_management-sim-architecture.sources.jsonl](research/sources/2026-06-21_management-sim-architecture.sources.jsonl).)*
- [OpenRCT2 Game Commands](https://github.com/OpenRCT2/OpenRCT2/wiki/Game-Commands) / [Replay System](https://github.com/OpenRCT2/OpenRCT2/wiki/Replay-System) / [Game Synchronization](https://deepwiki.com/OpenRCT2/OpenRCT2/6.2-game-synchronization) — github; the closest architectural twin to CarbonSim's reducer+audit_log+snapshot.
- [OpenTTD desync.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/desync.md) / [savegame_format.md](https://github.com/OpenTTD/OpenTTD/blob/master/docs/savegame_format.md) — github; command-only determinism + chunked versioned saves.
- [Gaffer On Games: Floating Point Determinism](https://gafferongames.com/post/floating_point_determinism/) / [Deterministic Lockstep](https://gafferongames.com/post/deterministic_lockstep/) / [Fix Your Timestep](https://gafferongames.com/post/fix_your_timestep/) — web; determinism + loop canon.
- [1500 Archers on a 28.8](https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond) — industry; sync commands not state.
- [Factorio FFF #204](https://factorio.com/blog/post/fff-204) — industry; "deterministic or desync."
- [PRNGs and Controlling Fate](https://www.gamedeveloper.com/design/prngs-and-controlling-fate-in-video-games) — web; seed+input log = exact replay.
- [Sid Meier — Interesting Decisions (GDC)](https://www.gdcvault.com/play/1015756/Interesting) / [Psychology of Game Design](https://www.gdcvault.com/play/1012186/The-Psychology-of-Game) — web/industry; choice criteria + player optimism.
- [Designer Notes 5: Sid's Rules](http://www.designer-notes.com/game-developer-column-5-sids-rules/) / [12: Theme Is Not Meaning](http://www.designer-notes.com/game-developer-column-12-theme-is-not-meaning-part-ii/) / [17: Water Finds a Crack](https://www.designer-notes.com/game-developer-column-17-water-finds-a-crack/) — industry; doubling/halving, mechanics-as-meaning, adversarial optimization.
- [Game Mechanics: Advanced Game Design, ch.5 Machinations](https://www.oreilly.com/library/view/game-mechanics-advanced/9780132946728/ch05.html) + [Dormans, Engineering Emergence (PhD)](https://eprints.illc.uva.nl/id/eprint/2118/1/DS-2012-12.text.pdf) — industry/academia; internal economies + feedback loops.
- [Runaway leader / rubber-banding](https://oakleafgames.wordpress.com/2014/02/13/game-theory-runaway-leader-rubber-banding-and-feedback/) — web; negative-feedback remedies.
- [Widelands economy.cc](https://github.com/widelands/widelands/blob/master/src/economy/economy.cc) / [BazaarBot](https://github.com/larsiusprime/bazaarBot) / [OpenTTD cargo formula](https://wiki.openttd.org/en/Manual/Game%20Mechanics/Cargo%20income) — github/web; Request-Supply, emergent pricing, distance/timeliness payment.
- [FreeOrion FOCS](https://www.freeorion.org/index.php/FOCS_Scripting_Details) / [Unciv project structure](https://github.com/yairm210/Unciv/wiki/Project-structure-and-major-classes) / [Cataclysm JSON_INFO](https://docs.cataclysmdda.org/JSON/JSON_INFO.html) — github; rules-as-data + ruleset-out-of-save.
- [Overwatch ECS (GDC)](https://www.gdcvault.com/play/1024001/-Overwatch-Gameplay-Architecture-and) / [Acton DOD](https://www.youtube.com/watch?v=rX0ItVEVjHc) — industry; state/logic separation (scope caveat: ECS over-kill here).
- [Cities: Skylines traffic deep dive](https://www.gamedeveloper.com/design/game-design-deep-dive-traffic-systems-in-i-cities-skylines-i-) / [RimWorld GDC 2017](https://www.youtube.com/watch?v=VdqhHKjepiE) — industry; agent simulation + story-generator framing.
- [Kairosoft combination tables](https://kairosoft.wiki.gg/wiki/Genres_and_types_(Game_Dev_Story)) / [Compulsion loop](https://en.wikipedia.org/wiki/Compulsion_loop) — web; combinatorial depth + loop stickiness.
- [Juice it or lose it](https://www.youtube.com/watch?v=Fy0aCDmgnxg) / [Art of Screenshake](https://www.youtube.com/watch?v=AJdEqssNZ-U) / [Swink, Game Feel ch.1](http://mycours.es/gamedesign2014/files/2014/10/Game-Feel-Steve-Swink-chapter-1.pdf) / [juice counterpoint](https://www.gamedeveloper.com/design/video-indies-resist-the-urge-to-juice-it-or-lose-it-) — industry; juice + the clarity caveat.
- [Curiosity-driven RL playtesting](https://arxiv.org/pdf/2103.13798) / [Dungeons & Replicants](https://antoniosliapis.com/papers/dungeons_replicants_automated_game_balancing_across_multiple_difficulty_dimensions_via_deep_player_behavior_modeling.pdf) / [FDG board-game playtesting](https://dl.acm.org/doi/10.1145/3102071.3102105) — academia; automated/agent-based balancing.
- [Serious-games-for-climate evaluation review](https://www.sciencedirect.com/science/article/abs/pii/S0272494426000435) / [Waterloo cap-and-trade game](https://uwaterloo.ca/chemical-engineering/news/serious-game-teaches-students-how-cap-and-trade-reduces-co2) — academia; pedagogy evidence (limited) + a direct cap-and-trade game cousin.
- CarbonSim source: [engine/engine.py](engine/engine.py), [engine/cards.py](engine/cards.py), [engine/playtest.py](engine/playtest.py), [engine/scenarios.py](engine/scenarios.py), [server/db.py](server/db.py), [server/ws.py](server/ws.py).

*Full source ledger (≈224 entries, all buckets, tiered): [research/sources/2026-06-21_management-sim-architecture.sources.jsonl](research/sources/2026-06-21_management-sim-architecture.sources.jsonl)*
