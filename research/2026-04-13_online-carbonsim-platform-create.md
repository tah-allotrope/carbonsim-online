# Research Brief: Online CarbonSim Platform

**Date:** 2026-04-13
**Modes run:** domain, codebase, math, literature
**Depth:** deep
**Invocation context:** using information in research folder as starting point to then invoke research deep mode skill for me to create an online version of carbonsim

---

## Synthesis
The strongest conclusion from the local Vietnam reports and current public ETS references is that an online CarbonSim for this repo should model a compliance market first, not a generic trading game. Vietnam's pilot direction centers on free allocation during the pilot, offset use within limits, regulator-led supervision, and tightly controlled trading, clearing, and registry reconciliation rather than a highly financialized continuous market from day one. That means the most credible V1 is a multi-round compliance simulator with annual allocation, abatement choices, limited offsets, banking, penalties, and a simple trading layer. [ICAP Vietnam](https://icapcarbonaction.com/en/ets/vietnam) [`research/20260213_Recommendation_20Report_EN.md`](research/20260213_Recommendation_20Report_EN.md:697) [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md:780)

Using the existing `research/` folder as a base materially changes the implementation recommendation. The local modeling report already frames price formation as a supply-demand equilibrium around mitigation costs, and the CarbonSim notes already define the main game objects, year flow, compliance formulas, and market features. So the missing asset is not domain design; it is a practical web implementation path. For a 10-20 participant workshop system, `oTree` is the best first platform because it is purpose-built for multiplayer experiments, has rooms/admin/export support, and has a server-authoritative live-page model that maps well to auctions, OTC messaging, and synchronized round state. [oTree docs](https://otree.readthedocs.io/en/latest/) [oTree live pages](https://otree.readthedocs.io/en/latest/live.html) [`research/carbonsim prelim research.md`](research/carbonsim%20prelim%20research.md:104)

[NOTE] The biggest planning shift from the earlier repo research is that you probably should not start with a continuous double-auction exchange, even though CarbonSim can support one. Vietnam's pilot evidence and small-session pedagogy both point toward sealed-bid auctions plus simple bilateral or facilitator-mediated secondary trading as the lowest-risk V1. If later sessions need richer market dynamics, you can still add an order book after the compliance and round engine are stable. [`research/20260213_Recommendation_20Report_EN.md`](research/20260213_Recommendation_20Report_EN.md:697) [CarbonSim public page](https://vncarbonmarket.com/en/carbon-sim/) [EDF CarbonSim](https://www.edf.org/climate/carbonsim-edfs-carbon-market-simulation-tool)

## Domain
### Discovery
The highest-signal domain sources were the repo's Vietnam CTX and modeling reports, ICAP's ETS overview and Vietnam page, and the public CarbonSim descriptions from Vietnam Carbon Market and EDF. The local reports are especially important because they are specific to the Vietnam pilot you want to emulate, while the public CarbonSim pages define the shape of the training product you want to reproduce. [ICAP ETS overview](https://icapcarbonaction.com/en/about-emissions-trading-systems) [ICAP Vietnam](https://icapcarbonaction.com/en/ets/vietnam) [CarbonSim public page](https://vncarbonmarket.com/en/carbon-sim/) [EDF CarbonSim](https://www.edf.org/climate/carbonsim-edfs-carbon-market-simulation-tool)

### Verification
ICAP is reliable here for canonical ETS structure and current jurisdiction status: it states that ETS design rests on cap, allocation, surrender, MRV, and oversight, and that Vietnam's pilot phase allocates allowances for free and allows certified credits within defined thresholds before fuller market operation later. [ICAP ETS overview](https://icapcarbonaction.com/en/about-emissions-trading-systems) [ICAP Vietnam](https://icapcarbonaction.com/en/ets/vietnam)

The local February 2026 recommendation report is trustworthy for pilot transaction design because it describes the proposed pilot procedures directly: mandatory intermediation, pre-trade validation, negotiated transactions on HNX, RTGS/DvP settlement without a CCP, and daily reconciliation back to the national registry. That is stronger evidence for V1 market design than generic foreign ETS examples. [`research/20260213_Recommendation_20Report_EN.md`](research/20260213_Recommendation_20Report_EN.md:697)

CarbonSim's public pages are reliable for product framing but not implementation internals. They consistently confirm that the exercise teaches ETS literacy through multi-user, AI-enhanced, multi-year sessions with abatements, auctions, exchanges, OTC trades, offsets, and leaderboard-style performance feedback. [CarbonSim public page](https://vncarbonmarket.com/en/carbon-sim/) [EDF CarbonSim](https://www.edf.org/climate/carbonsim-edfs-carbon-market-simulation-tool)

### Comparison
There are really two viable domain abstractions.

One is a close CarbonSim-style market game with auctions, exchange trading, OTC, offsets, banking, and shocks across three compressed years. This is the strongest match to the public CarbonSim descriptions and the local technical notes. [CarbonSim public page](https://vncarbonmarket.com/en/carbon-sim/) [`research/carbonsim prelim research.md`](research/carbonsim%20prelim%20research.md:104)

The other is a more conservative Vietnam-pilot simulator emphasizing free allocation, compliance accounting, limited offsets, negotiated transactions, and regulator-controlled settlement. This is closer to the local policy evidence and easier to explain in workshops. [`research/20260213_Recommendation_20Report_EN.md`](research/20260213_Recommendation_20Report_EN.md:697) [ICAP Vietnam](https://icapcarbonaction.com/en/ets/vietnam)

For this repo, the best comparison outcome is a hybrid: keep CarbonSim's learning flow and multi-year pressure, but anchor the market rules to Vietnam's pilot posture rather than to a full-featured exchange.

### Synthesis
The domain evidence supports a V1 with these mechanics: three compressed virtual years; free allocation at year start; sector-specific abatement options; limited offsets; simple secondary trading; year-end surrender and penalties; banking allowed; borrowing excluded. That preserves the strategic lesson of cap tightening while staying consistent with Vietnam's pilot direction and with the local modeling logic. [ICAP Vietnam](https://icapcarbonaction.com/en/ets/vietnam) [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md:825) [`research/carbonsim prelim research.md`](research/carbonsim%20prelim%20research.md:25)

The domain gap is not rules; it is choosing how much market microstructure to simulate. The evidence favors starting with a simple, legible market and only adding an order book if workshop goals later require richer price discovery.

### Confidence
High - the repo contains strong Vietnam-specific reports and the public ETS/CarbonSim sources align with them on the important product-shape questions.

## Codebase
### Discovery
The most relevant implementation candidates are `oTree`, `Empirica`, and `Colyseus`. Current repo metadata shows all three are active, but they solve different problems: `oTree` is built for multiplayer experiments and surveys, `Empirica` is an experiment framework with a custom React/GraphQL stack, and `Colyseus` is a general authoritative multiplayer server. [https://github.com/oTree-org/oTree](https://github.com/oTree-org/oTree) [https://github.com/empiricaly/empirica](https://github.com/empiricaly/empirica) [https://github.com/colyseus/colyseus](https://github.com/colyseus/colyseus)

Verified GitHub metadata from this session shows `oTree` at 520 stars and updated 2026-04-10, `Empirica` at 61 stars and updated 2025-12-20, and `Colyseus` at 6,827 stars and updated 2026-04-13. Those numbers do not decide fit alone, but they do help distinguish mature niche tooling from general-purpose real-time infrastructure. [https://github.com/oTree-org/oTree](https://github.com/oTree-org/oTree) [https://github.com/empiricaly/empirica](https://github.com/empiricaly/empirica) [https://github.com/colyseus/colyseus](https://github.com/colyseus/colyseus)

### Verification
`oTree` explicitly supports multiplayer games, auctions, bots, rooms, admin, exports, and live pages. Its `live_method` pattern is server-authoritative, supports broadcast and directed messages, and recommends persisting history via the database and `ExtraModel`, which fits a market board and audit trail well. [oTree docs](https://otree.readthedocs.io/en/latest/) [oTree live pages](https://otree.readthedocs.io/en/latest/live.html)

`Empirica` explicitly targets multiplayer interactive experiments and games in the browser and includes an admin panel plus game/round/stage abstractions. That is relevant, but it also assumes a heavier custom app stack with Go, GraphQL, TypeScript, JavaScript, and React. [Empirica docs](https://docs.empirica.ly/)

`Colyseus` is clearly capable for a CarbonSim clone because it provides authoritative rooms, matchmaking, state sync, and real-time client messaging, but it is a lower-level multiplayer framework rather than a domain-specific experiment platform. You would own more of the session/admin/data-collection layer yourself. [Colyseus docs](https://docs.colyseus.io/)

### Comparison
`oTree` is best when the main problem is coordinating a structured, synchronous workshop with rounds, forms, admin control, room links, exports, and modest real-time interaction. That is very close to this use case.

`Empirica` is strongest when you want a more custom React experience and are willing to pay a complexity premium. It is a good second choice if UI flexibility becomes more important than quick delivery. [Empirica docs](https://docs.empirica.ly/)

`Colyseus` is strongest if the goal shifts from "training simulator" toward "bespoke multiplayer market game." It would likely produce the richest final interaction model, but it also creates the most surface area for state sync, admin tools, data export, and deployment work. [Colyseus docs](https://docs.colyseus.io/)

### Synthesis
The existing research folder already contains enough CarbonSim-specific domain design that you do not need a blank-slate game engine first. The most leverage comes from reusing `oTree`'s session plumbing and implementing the ETS logic as server-side Python models plus live-page handlers. [oTree live pages](https://otree.readthedocs.io/en/latest/live.html) [`research/carbonsim prelim research.md`](research/carbonsim%20prelim%20research.md:446)

The practical recommendation is:
- V1: `oTree` for rooms, admin, participant flow, exports, and live auction/trade interactions.
- V2: add richer front-end behavior inside `oTree` templates if needed.
- V3 only if necessary: migrate specific market interactions to a custom real-time stack such as `Colyseus`.

### Confidence
High - the framework docs and current repo metadata were verified directly, and the fit differences are clear for this project shape.

## Math
### Discovery
The local July 2025 modeling report is the strongest math source because it already formalizes the Vietnam ETS as a supply-demand market with mitigation-cost-based firm decisions, offset limits, and compliance-cost calculations. The local CarbonSim specification then provides implementation-oriented formulas for compliance, banking, penalties, and abatement timing. [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md:740) [`research/carbonsim prelim research.md`](research/carbonsim%20prelim%20research.md:39)

### Verification
The local modeling report explicitly assumes that in ETS settings firms first adopt mitigation measures cheaper than the market price, then use offsets, then buy allowances or higher-cost mitigation as needed. It also defines the initial carbon price as the level that minimizes the supply-demand gap while keeping prices from becoming unnecessarily high. That is a credible foundation for a simplified simulator because it ties player behavior to MAC logic rather than arbitrary game rules. [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md:782) [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md:825)

The same report also warns that perfect competition is an assumption and that strategic behavior can differ in reality. That matters because it means a classroom simulator can use equilibrium-based starting logic while still introducing trading frictions and strategic decisions for pedagogy. [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md:751)

### Comparison
There are two mathematical implementation paths.

The first is equilibrium-first: compute starting prices and firm incentives from MAC curves, allowance supply, emissions obligations, and offset caps, then let players trade around that structure. This is strongly supported by the local Vietnam modeling report and is enough for a credible V1. [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md:825)

The second is market-microstructure-first: simulate a full continuous order book with price-time priority, stop orders, candles, and richer AI liquidity. That can be engaging, and the local CarbonSim notes describe it in detail, but the local policy evidence does not require it for credibility. [`research/carbonsim prelim research.md`](research/carbonsim%20prelim%20research.md:224)

### Synthesis
The best math core for V1 is minimal and testable:
- per-firm baseline emissions and yearly growth
- yearly cap and free allocation
- a small MAC curve / abatement menu per firm or sector
- offset usage cap
- end-of-year compliance position
- banking and non-compliance penalty

With that core, you can run sealed-bid auctions and bilateral trades without needing a full exchange engine. The local report's decision ladder already tells you what the player and bot heuristics should be: abate below price, use offsets up to the cap, then buy allowances or pay for higher-cost measures. [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md:782)

### Confidence
High - the repo already contains a directly relevant local model, and it is more specific to your problem than generic economics references.

## Literature
### Discovery
The strongest practitioner evidence is the public CarbonSim material from EDF and Vietnam Carbon Market plus Stanford's Energy Market Game as adjacent proof that online training simulations can work for policy and market education. [EDF CarbonSim](https://www.edf.org/climate/carbonsim-edfs-carbon-market-simulation-tool) [CarbonSim public page](https://vncarbonmarket.com/en/carbon-sim/) [Stanford Energy Market Game](https://pesd.fsi.stanford.edu/energy-market-game)

The repo's earlier brief also identified older experimental literature on repeated auctions and emissions-trading mechanisms. In this pass, the PDF endpoints for those papers returned raw PDF payloads rather than cleanly extracted text, so they remain useful leads but not primary evidence for exact claims here. [`research/2026-04-06_online-carbonsim-platform.md`](research/2026-04-06_online-carbonsim-platform.md:106)

### Verification
The practitioner evidence is solid for product existence and use cases: EDF states CarbonSim is AI-enhanced, multi-lingual, multi-user, and used for ETS capacity building; the Vietnam Carbon Market page adds that participants manage virtual companies over up to three virtual years using abatements, auctions, exchange trades, and OTC markets; Stanford's EMG confirms that free, online policy market games can be used for workshops and multiplayer play. [EDF CarbonSim](https://www.edf.org/climate/carbonsim-edfs-carbon-market-simulation-tool) [CarbonSim public page](https://vncarbonmarket.com/en/carbon-sim/) [Stanford Energy Market Game](https://pesd.fsi.stanford.edu/energy-market-game)

The literature gap is real: there is much more published material about ETS policy design than about maintained, open, deployable training software for carbon markets. That makes direct code reuse unlikely and increases the value of the repo's own research notes.

### Comparison
The literature and practitioner landscape splits into three buckets:

Public ETS explainers and policy reports explain what should be simulated.

Training tools like CarbonSim and Energy Market Game prove that simulation-based learning works and show what users expect from the experience.

Open-source frameworks like `oTree` and `Empirica` are not carbon-market tools themselves, but they are the most realistic software substrate for building one.

### Synthesis
The literature does not hand you an open-source CarbonSim clone. What it does provide is enough evidence to justify a narrow, workshop-oriented product with strong pedagogical structure and realistic policy rules. That is exactly where your local research folder is strongest: it bridges the gap between ETS policy literature and buildable product mechanics.

### Confidence
Medium - the practitioner evidence is strong, but the open literature on reusable carbon-simulation software is sparse and the older PDF papers were not cleanly machine-readable in this pass.

## Sources
- [ICAP About Emissions Trading Systems](https://icapcarbonaction.com/en/about-emissions-trading-systems) - official explainer; best concise reference for ETS core design elements.
- [ICAP Vietnam ETS page](https://icapcarbonaction.com/en/ets/vietnam) - jurisdiction summary; strongest current public reference for Vietnam pilot status and institutions.
- [oTree documentation](https://otree.readthedocs.io/en/latest/) - framework docs; confirms multiplayer, rooms, admin, exports, and experiment structure.
- [oTree live pages](https://otree.readthedocs.io/en/latest/live.html) - framework docs; confirms server-authoritative real-time interaction pattern.
- [Empirica documentation](https://docs.empirica.ly/) - framework docs; confirms multiplayer experiment support and heavier custom stack.
- [Colyseus documentation](https://docs.colyseus.io/) - framework docs; confirms authoritative real-time room/state model.
- [CarbonSim public page](https://vncarbonmarket.com/en/carbon-sim/) - practitioner source; strongest public description of CarbonSim session flow and features.
- [EDF CarbonSim](https://www.edf.org/climate/carbonsim-edfs-carbon-market-simulation-tool) - practitioner source; validates CarbonSim positioning and deployment history.
- [Stanford Energy Market Game](https://pesd.fsi.stanford.edu/energy-market-game) - adjacent prior art; shows free online market-simulation training can work in practice.
- [`research/20260213_Recommendation_20Report_EN.md`](research/20260213_Recommendation_20Report_EN.md) - local technical report; strongest evidence for Vietnam pilot transaction, settlement, and oversight design.
- [`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`](research/20250708_Impact-Assessing-and-Modeling-Report_EN.md) - local technical report; strongest evidence for price formation, MAC logic, offset scenarios, and compliance-cost modeling.
- [`research/carbonsim prelim research.md`](research/carbonsim%20prelim%20research.md) - local internal specification; best implementation-oriented starting point for a CarbonSim-like rules engine and session flow.
