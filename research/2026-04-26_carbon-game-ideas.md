# Research Brief: Three Game-ification Directions for CarbonSim Online

**Date:** 2026-04-26
**Modes run:** domain, codebase
**Depth:** standard
**Invocation context:** "i want to have 3 ideas that will further develop this repo into a fun project that policy makers, lay people can use playing around with carbon market like a game. each idea will be capable of spawning a multiphase plan on its own"

---

## Synthesis

The current repo is a workshop-tested compliance simulator built on oTree, designed for facilitator-led, 10-20 person live sessions of ~60-90 minutes [`research/20250418_Final_20Report_EN.md`](research/20250418_Final_20Report_EN.md). To extend it into something policy makers and lay people will play voluntarily — without a facilitator and without coordinating schedules — the design has to shed two assumptions: that play is synchronous, and that learning happens through facilitation rather than mechanics. The strongest evidence-based directions in the climate-game landscape are **stakeholder-negotiation simulators** ([En-ROADS](https://www.climateinteractive.org/climate-action-simulation/) is the canonical example), **cooperative tableau-builders** ([Daybreak](https://en.wikipedia.org/wiki/Daybreak_(board_game)) — Spiel des Jahres Kennerspiel 2024), and **short-session digital games** that lean on daily-ritual and shareable-score mechanics that have proven viral outside the climate space (Wordle, NYT Connections).

The repo's biggest reusable asset is `platform/carbonsim_phase12/engine.py`: ~2,265 lines of pure-Python functions over a state dict, with no oTree imports inside the engine itself (verified by `Grep "^def |^class "` — all 30+ entry points are stateless). The compliance math, scenario packs, and bot heuristics can be lifted out and reused unchanged in a desktop solo mode, an asynchronous web app, or even a JS port. What is *not* reusable across all three directions is oTree's live-page/session model — it's the right substrate for a multiplayer roundtable game but the wrong substrate for solo-play or daily-puzzle modes, which need persistent state, save/resume, and (for the puzzle) a deterministic seedable solver.

Peer-reviewed reviews of climate serious games consistently identify three success factors: **strong debrief/reflection mechanisms**, **theory-driven psychological design**, and **causal-reasoning support over factual recall** [IOP systematic review](https://iopscience.iop.org/article/10.1088/1748-9326/aac1c6) [npj Urban Sustainability 2025](https://www.nature.com/articles/s42949-025-00296-8). Two of these are present in the current repo (the engine produces the causal feedback; the export/replay produces material for debrief). The missing one is *intrinsic motivation* — a reason to play when no one is making you. The three ideas below each solve that differently: narrative drive (Idea 1), social/role-play stakes (Idea 2), and habit-loop + status-share (Idea 3).

[NOTE] The research literature is also clear that empirical evidence on serious-game *behavior change* (as distinct from engagement) remains thin [ScienceDirect 2026](https://www.sciencedirect.com/science/article/abs/pii/S0272494426000435). Plans built on these ideas should set engagement and conceptual-learning targets, not policy-attitude-shift targets — the latter would be over-claiming.

---

## Domain

### Discovery

The strongest reference points for "carbon market as a game" cluster in three categories: facilitated stakeholder simulators, cooperative board games adapted to digital, and short-session educational tools.

**Facilitated stakeholder simulators.** En-ROADS Climate Action Simulation by Climate Interactive + MIT Sloan is the canonical adult/professional version: 6-8 stakeholder groups (government, business, civil society) negotiate climate solutions while a facilitator runs the En-ROADS simulator behind the scenes; goal is staying below 2°C [Climate Interactive — Climate Action Simulation](https://www.climateinteractive.org/climate-action-simulation/) [Climate Interactive — En-ROADS](https://www.climateinteractive.org/en-roads/). The strength is intrinsic motivation through role conflict and live deal-making; the weakness is the same one CarbonSim Online has — it requires a facilitator and a synchronized cohort.

**Cooperative tableau-builders.** Daybreak by Matt Leacock and Matteo Menapace (2023) won the 2024 Spiel des Jahres Kennerspiel — the strongest critical recognition a climate game has received [Wikipedia — Daybreak](https://en.wikipedia.org/wiki/Daybreak_(board_game)) [Co-op Board Games review](https://coopboardgames.com/cooperative-board-game-reviews/daybreak-review/). Players control four global powers (US, China, Europe, Global South), build engines through card combos and tags, and collectively race to "Drawdown" (net-negative emissions). The mechanic worth borrowing is the *tag/combo* engine: small decisions stack into emergent strategy without needing a regulator to enforce rules.

**Short-session digital tools.** Carbon City Zero (Possible UK) is a deck-builder where players spend "spending power" against "carbon" to decarbonize a city; rounds are 30-45 min and can be cooperative or competitive [The Earthbound Report](https://earthbound.report/2026/02/13/three-board-games-for-the-climate/). Field Day's Carbon Cycle Game is a free online action-card game [Field Day](https://fielddaylab.wisc.edu/play/carbon-game/). The economics-games.com "Carbon Market Game" is a price-competition / quantity-precommitment market exercise designed for econ classrooms [economics-games.com](https://economics-games.com/carbon-market-game). None of these have hit mass adoption outside their niches — a gap a polished carbon-market product could fill.

### Verification

The Climate Interactive page for the Climate Action Simulation explicitly describes the 6-8 stakeholder structure, the facilitator's role as "UN Secretary-General," and the real-time En-ROADS analysis loop [Climate Interactive — Climate Action Simulation](https://www.climateinteractive.org/climate-action-simulation/). This is a primary source from the tool's developer; it's reliable for design facts, less so for effectiveness claims.

Daybreak's awards (Spiel des Jahres Kennerspiel 2024, Lizzie Magie 2025) are matters of public record and confirmed across Wikipedia and review sites [Wikipedia — Daybreak](https://en.wikipedia.org/wiki/Daybreak_(board_game)). Reviewer consensus on mechanical strengths (tag combos, theme-mechanic fit) is strong but reviewer-dependent.

The peer-reviewed effectiveness literature is more mixed. The IOP systematic review of "serious games" for climate engagement reports that adaptation games are effective for engagement and social learning, but flags that empirical evidence on *behavior change* is limited [IOP Science — systematic review](https://iopscience.iop.org/article/10.1088/1748-9326/aac1c6). A 2026 ScienceDirect call-for-rigorous-evaluations paper, using Climate Fresk as a case study, makes the same argument more sharply: most climate-game studies measure self-reported attitude change without controls, and the field needs RCTs [ScienceDirect 2026](https://www.sciencedirect.com/science/article/abs/pii/S0272494426000435). For our purposes, this means **claim engagement and conceptual learning, not policy attitude shift**.

### Comparison

If you want to maximise *depth of engagement per session*, En-ROADS-style stakeholder negotiation is the proven format — but it inherits the facilitator dependency that already limits the current repo. If you want *broadest reach with no facilitator*, Daybreak-style solo/co-op tableau-building is the design lineage with the strongest critical reception, but it's a substantial mechanic-design project. If you want *fastest path to mass adoption*, the Wordle/Connections daily-puzzle pattern is the most underexploited surface in the climate-game space — the economics-games.com Carbon Market Game proves the underlying economics work as a short exercise [economics-games.com](https://economics-games.com/carbon-market-game), but no one has paired that with the daily-ritual + share-card playbook that has driven Wordle to 6M+ daily players (NYT acquisition reporting, public).

The three are not substitutes — they target different audiences (workshop attendees vs. cooperative-game enthusiasts vs. casual mobile users) and different motivations (deal-making vs. system-mastery vs. daily-ritual). A repo that wants to grow beyond workshops should pick one and commit; a repo that wants to be a platform should sequence them.

### Synthesis

The literature points to three concrete idea archetypes, each with strong precedent and clear distinct value. **Idea 1 (Climate Mayor)** = Daybreak-style solo/co-op narrative tableau, replayable, lay-public-friendly, leans on engine reuse and a new content layer. **Idea 2 (Stakeholder Roundtable)** = En-ROADS-style pre-game negotiation that hands negotiated parameters to the existing trading engine, then scores stakeholders against hidden KPIs — directly extends the facilitator workflow the repo already has. **Idea 3 (Carbon Crunch Daily)** = Wordle-style daily 5-minute puzzle with a shareable score card, exploits the deterministic engine and the proven viral mechanics of daily-puzzle games.

What is missing across all three is an explicit *measurement plan* — what does success look like in engagement minutes, learning gains, or share rate. Any plan should bake that in, because the literature says effectiveness claims without measurement are the field's weakest point.

### Confidence

Medium-High — the canonical references (En-ROADS, Daybreak, the IOP systematic review) are primary sources or peer-reviewed; the daily-puzzle inference is a commercial-pattern argument rather than a peer-reviewed claim, and is flagged as such.

---

## Codebase

### Discovery

The repo's structure (verified by `Glob platform/**/*.py`):

- `platform/carbonsim_phase12/engine.py` — ~2,265 lines, 30+ public functions, all operating on a `state: dict` argument. No oTree imports in the engine itself (confirmed via `Grep "^def |^class " platform/carbonsim_phase12/engine.py` — all entry points are top-level functions, not Player/Subsession methods).
- `platform/carbonsim_phase12/__init__.py` — oTree app: Player/Subsession models, `live_method` handlers, page classes.
- `platform/carbonsim_phase12/deployment.py` — health check, reconnect, role auth.
- `platform/tests/test_engine.py` and `test_deployment.py` — 92 passing tests covering the engine and deployment layer.
- `platform/carbonsim_phase12/WorkshopHub.html`, `FacilitatorPanel.html`, `Welcome.html` — Django templates rendered by oTree.

### Verification

The state-dict pattern is verifiable from the function signatures: every public engine function takes `state: dict[str, Any]` as its first argument and returns a dict (or mutates state in place and returns it). Examples from `Grep` output: `start_simulation(state, now)`, `apply_company_decision(state, ...)`, `propose_trade(state, ...)`, `clear_auction(state, ...)`, `apply_shock(state, ...)`, `export_session_data(state)`, `build_session_replay(state)`. This is a portability win — a non-oTree caller (a Flask app, a CLI, a scheduled job, a static-site build script) can import these functions directly.

The 92 passing tests confirm the engine is exercised independently of oTree's runtime — `tests/test_engine.py` builds states and calls engine functions directly, no oTree fixtures. This is the strongest signal that the engine is decoupled enough to lift out for any of the three ideas.

What is *not* decoupled: real-time interaction (the `live_method` handlers in `__init__.py` translate browser events into engine calls), session/room management (oTree's), and the participant join flow (oTree's). Anything we build outside oTree has to replace these.

### Comparison

**Reuse map across the three ideas:**

| Component | Idea 1 (Climate Mayor) | Idea 2 (Stakeholder Roundtable) | Idea 3 (Carbon Crunch Daily) |
|---|---|---|---|
| `engine.py` compliance math | High reuse (extend years, add narrative hooks) | High reuse (unchanged) | High reuse (single-year subset) |
| `SCENARIO_PACKS` | Reuse + extend with story scenarios | Reuse, parameters become negotiated outputs | Reuse, vary by daily seed |
| Auction system | Optional / reduced to NPC market | Full reuse | Not needed |
| Bilateral trades | Optional with NPC partners | Full reuse | Not needed |
| Bots (`run_bot_turns`) | Reuse as opponent companies | Reuse for absent stakeholders | Reuse as the "optimal solver" baseline |
| Shocks (`apply_shock`) | High reuse — narrative events | High reuse | High reuse — daily variant |
| Export / replay | Adapt for solo run summary | Reuse for stakeholder scorecards | Adapt for share-card generation |
| oTree session model | Replace with persistent solo state | Reuse fully | Replace with stateless puzzle endpoint |
| Templates (`WorkshopHub.html` etc.) | Replace | Reuse + add negotiation UI | Replace |

The pattern is clear: Idea 2 reuses the *most* of the existing repo (engine + oTree + templates) and adds a negotiation layer. Idea 1 reuses the engine but rewrites the session and UI layers. Idea 3 reuses *only* the engine and rewrites everything else — but the engine is the hard part, so this is still high leverage.

### Synthesis

The most cost-efficient first idea to ship is whichever one reuses the most of the existing surface; that is **Idea 2**. The most reach-efficient (potential audience per dev hour) is **Idea 3**, because the engine port is the hardest part and it's already done — the rest is a static frontend and a daily seed. **Idea 1** is the highest content-cost option (narrative writing, balancing) but produces the most replayable single-player product.

A reusable refactor that would help all three: extract `engine.py` as a standalone Python package (`carbonsim-engine`) with no oTree dependencies, publish to PyPI or just vendor it, and let the three game frontends depend on it. This is a small refactor — based on the `Grep` results no oTree imports exist in the engine — but doing it explicitly creates a clean substrate.

### Confidence

High — function signatures, file layout, and test isolation were verified directly in this session.

---

## The Three Ideas

Each idea below is structured to seed its own `/plan` invocation. Every idea includes the audience, the core loop, the reuse story, the new build, and the multi-phase shape.

### Idea 1 — Climate Mayor (single-player narrative tycoon)

**Pitch.** You are the newly appointed Director of Industry for a Vietnamese province. Over 10-20 virtual years you manage a portfolio of facilities (your starting set is procedurally rolled from the existing company library), navigate elections, board reviews, and crises, and try to hit Drawdown without bankrupting your province. Asynchronous, save/resume, plays in 30-60 min sessions.

**Audience.** Lay public who want a long-form, story-driven climate experience; policy makers who want to internalize compliance trade-offs at their own pace.

**Core loop.** Each virtual year: (1) review your facilities' compliance position, (2) draw 2-3 event cards (drought reduces hydro → thermal dispatch up; new heat-pump tech available; new FDI proposal; CBAM threat), (3) make abatement and trading decisions, (4) end-of-year scorecard with narrative beats. NPC industry peers run on bot heuristics.

**Reuse.** `engine.py` compliance math, scenario packs as starting conditions, bot heuristics for NPCs, shocks as event-card payloads.

**New build.** Persistent solo session model (replace oTree), event-card content system + writer's pipeline, narrative UI, save/load, end-of-run summary that's shareable. Likely best built as a new web frontend (Next.js/Astro) consuming a Python API wrapper around the engine.

**Why it could spawn a 5-phase plan.** (1) extract engine to standalone package; (2) design event-card system + write 50-card starter deck; (3) build solo session backend (FastAPI) + persistent state; (4) frontend with year-cycle UI and end-of-run summary; (5) playtest, balance, content expansion. Naturally extends to co-op (2-4 players running the province together) as a phase 6.

---

### Idea 2 — Stakeholder Roundtable (pre-game policy negotiation)

**Pitch.** Before the trading session begins, players role-play 4-6 stakeholder groups (Regulator/MOF, Heavy Industry, SME Coalition, Environmental NGO, Citizens/Workers, International Investors). Each has a hidden agenda and KPIs. They negotiate the scenario parameters live — allocation factors, penalty rate, offset cap, who gets free allowances. The negotiated parameters get plugged into the existing trading engine, and players then play the trading session as covered companies. A debrief shows each stakeholder how their negotiated rules played out against their hidden KPIs.

**Audience.** The current workshop audience plus policy-school students, civil-society trainees, and ETS-design practitioners. Same facilitator dependency as today, but adds a richer learning loop.

**Core loop.** Negotiation phase (15-20 min): stakeholders propose parameter packages, vote, deal-make. Trading phase (60-90 min): the existing 3-year session runs with the negotiated parameters. Debrief: scorecards reveal hidden KPIs and what each group "won" or "lost."

**Reuse.** Maximum — engine is unchanged; oTree session model is unchanged; existing templates extended. Only new surface is the negotiation UI and the parameter-injection bridge.

**New build.** Stakeholder role definitions + hidden KPI design, negotiation UI (proposal cards, voting, side-deals), parameter-injection into `create_initial_state`, scorecard generation per role, debrief tooling.

**Why it could spawn a 5-phase plan.** (1) stakeholder role + KPI design (research-heavy: who has what real interests in Vietnam's CTX); (2) negotiation phase mechanics + UI; (3) parameter-injection bridge into engine; (4) per-role scorecards and debrief; (5) facilitator runbook + workshop pilot. Direct lineage to En-ROADS Climate Action Simulation [Climate Interactive — Climate Action Simulation](https://www.climateinteractive.org/climate-action-simulation/).

---

### Idea 3 — Carbon Crunch Daily (Wordle-style 5-minute puzzle)

**Pitch.** Every day, a fresh deterministic compliance puzzle is published: "You have 100 allowances. Projected emissions: 110. Abatement menu: [X, Y, Z]. Offset price: 25. Penalty: 200. Minimize total cost." Players solve in 5 minutes, get a score, and share an emoji-grid result like Wordle. A global daily leaderboard shows the score distribution; an "optimal" line shows the engine-calculated best score.

**Audience.** Mass — anyone with 5 minutes and curiosity. The on-ramp Wordle proved exists for a daily intellectual ritual. Policy makers get a quick way to sharpen compliance intuition; lay public get a low-commitment introduction to ETS thinking.

**Core loop.** (1) Open page → see today's puzzle; (2) make decisions (activate abatements, buy offsets, allocate cash) — instant feedback on compliance gap; (3) submit → see your total cost vs. optimal; (4) get a share card with emoji grid + cost spread; (5) come back tomorrow.

**Reuse.** Engine is the entire backend. The deterministic, seedable nature of the engine (verified — bot heuristics use deterministic random, sorting is deterministic) means the same daily seed produces the same puzzle for everyone globally.

**New build.** Daily-puzzle generator (random scenario within solvability bounds), optimal-solution oracle (reuse `run_bot_turns` with an aggressive variant or write a brute-force solver since the action space is small), static frontend (probably a SvelteKit or Next.js static-site), share-card image generation (Open Graph + canvas), thin leaderboard backend. Could even be done as a JS port of the engine (~2,000 lines is manageable) so the entire game runs client-side with no backend.

**Why it could spawn a 5-phase plan.** (1) puzzle generator + difficulty calibration (must be solvable, not trivially); (2) optimal-solution oracle; (3) frontend (decision UI + share card); (4) daily seed pipeline + optional leaderboard; (5) growth experiments (Discord bot, daily email, embedded widget for partner sites). Lowest engineering cost per potential reach of the three.

---

## Sources

- [Climate Interactive — En-ROADS](https://www.climateinteractive.org/en-roads/) — primary source; canonical climate-policy simulator with stakeholder-negotiation game built on top.
- [Climate Interactive — Climate Action Simulation](https://www.climateinteractive.org/climate-action-simulation/) — primary source; documents the 6-8-stakeholder negotiation format that grounds Idea 2.
- [Wikipedia — Daybreak (board game)](https://en.wikipedia.org/wiki/Daybreak_(board_game)) — reference for cooperative tableau-builder mechanics and 2024 Spiel des Jahres Kennerspiel award.
- [Co-op Board Games — Daybreak Review](https://coopboardgames.com/cooperative-board-game-reviews/daybreak-review/) — reviewer perspective on tag/combo engine relevant to Idea 1.
- [Earthbound Report — Three board games for the climate](https://earthbound.report/2026/02/13/three-board-games-for-the-climate/) — Carbon City Zero and adjacent climate board games.
- [Field Day — Carbon Cycle Game](https://fielddaylab.wisc.edu/play/carbon-game/) — example of free online climate educational game.
- [economics-games.com — Carbon Market Game](https://economics-games.com/carbon-market-game) — proof that short-form online carbon-market exercises work pedagogically.
- [IOP Science — Adaptive and interactive climate futures: systematic review of 'serious games'](https://iopscience.iop.org/article/10.1088/1748-9326/aac1c6) — peer-reviewed effectiveness review; success factors for serious games.
- [npj Urban Sustainability 2025 — A policy-relevant serious game to guide urban sustainability transformation](https://www.nature.com/articles/s42949-025-00296-8) — recent peer-reviewed example of policy-game design and evaluation.
- [ScienceDirect 2026 — A call for robust evaluations of serious games for climate change mitigation](https://www.sciencedirect.com/science/article/abs/pii/S0272494426000435) — evidence-quality caveat that bounds reasonable claims in any plan.
- [Climate Interactive — 19 Climate Games that Could Change the Future](https://www.climateinteractive.org/blog/19-climate-games-that-could-change-the-future/) — landscape overview from a primary actor in the space.
- [`research/20250418_Final_20Report_EN.md`](research/20250418_Final_20Report_EN.md) — local report; documents the existing CarbonSim's workshop usage and audience.
- [`platform/carbonsim_phase12/engine.py`](platform/carbonsim_phase12/engine.py) — local source; ~2,265 lines, pure-Python state-dict pattern, no oTree imports inside the engine, the foundation all three ideas reuse.
