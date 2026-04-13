# Research Brief: Online CarbonSim Platform for Vietnam

**Date:** 2026-04-06
**Modes run:** domain, codebase, math, literature
**Invocation context:** /research mode all for me to create an online carbonsim platform for 10-20 participants in Vietnam at zero/minimal cost that emulate the compliance carbon market with emission trading quota and carbon pricing with a a very close example to be found here https://youtu.be/7A6iH4Ol2Xw?si=WCsHLM6diRpVzH1A

---

## Synthesis
Vietnam's pilot ETS direction is already specific enough that your simulator should not start from a generic "carbon game" design. The strongest local evidence in this workspace and ICAP's Vietnam summary point to a pilot with free allocation, compliance-year accounting, offsets, registry-linked eligibility, and strong controls around settlement and supervision rather than a fully financialized exchange. For a 10-20 participant online simulation, the right abstraction is a simplified compliance market with annual rounds, free allowance allocation, limited offsets, banking, compliance penalties, and either negotiated trades or a simple central order book, not a complex derivatives venue. Sources: local Vietnam CTX reports, ICAP Vietnam, and ICAP ETS overview. https://icapcarbonaction.com/en/ets/vietnam https://icapcarbonaction.com/en/about-emissions-trading-systems

The reusable software landscape is uneven. Evidence for mature open-source, ETS-specific simulators is sparse; the strongest direct prior art is proprietary training software like CarbonSim rather than a forkable codebase. The best low-cost implementation path is therefore to build on an experiment framework designed for synchronous multiplayer sessions. Among the candidates, oTree is the best fit for 10-20 participants because it already supports rooms, admin flows, exports, real-time live pages, and auction-style interaction with minimal infrastructure. Empirica and nodeGame are credible alternatives if richer front-end interaction or lower-level real-time control becomes more important. https://otree.readthedocs.io/en/latest/ https://docs.empirica.ly/ https://nodegame.org/

[NOTE] The local modeling report changes the likely planning path: Vietnam's own ETS analysis already frames price formation as an equilibrium between marginal abatement cost and allowance supply-demand, with 10% and 20% offset scenarios and a price-search process over a mitigation-cost range. That means the first version does not need sophisticated agent-based market microstructure to be credible; it can use a simpler repeated-round rules engine anchored to MAC curves, allowance balances, and compliance costs. Source: local 20250708 impact/modeling report. `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`

For cost, zero/minimal hosting is realistic if the first version uses an experiment-style stack and modest concurrency. Render offers free static hosting and free web/database tiers with limits, while Cloudflare Workers provides a free tier and a $5/month paid floor with generous request allowances and no egress fees. For a 10-20 player pilot used in workshops rather than always-on production, hosting cost should be much smaller than custom development cost. https://render.com/pricing https://developers.cloudflare.com/workers/platform/pricing/

## Domain Landscape
### Overview
An ETS simulator close to Vietnam's pilot should model a cap-and-trade compliance system where a regulator sets a cap, allocates or auctions allowances, and requires covered firms to surrender allowances against verified emissions at period end. ICAP's ETS overview states the core ingredients are cap, allocation, surrender, MRV, and market oversight rather than pure price speculation. https://icapcarbonaction.com/en/about-emissions-trading-systems

ICAP's Vietnam page and local CTX reports indicate Vietnam's market is under development with a pilot structure centered on free allocation, regulated trading, registry control, and eventual exchange operation through HNX. During the pilot phase, allowances are expected to be allocated for free, credits are allowed within limits, and the market becomes more fully operational later. https://icapcarbonaction.com/en/ets/vietnam `research/20251128_Recommending_20the_20CTX_20Operational_20Model_20Report_EN.md`

### Key Tools and Frameworks
The closest prior art found is CarbonSim, a multiplayer carbon market simulation used for training and capacity building. Its public description references trading allowances and offsets across simulated firms and years, which makes it the best reference for feature shape even though it is not an open-source implementation. https://vncarbonmarket.com/en/carbon-sim/

For adjacent prior art, Stanford's Energy Market Game shows that workshop-style market simulations can successfully teach trading behavior, auctions, and policy impacts in a structured multi-user setting, even when the interface and mechanism are simplified. https://pesd.fsi.stanford.edu/energy-market-game

### Prior Art and Existing Approaches
The strongest prior art pattern is not a full exchange clone but a training simulator with compressed time, repeated compliance periods, simplified market instruments, and explicit learning objectives. Local notes in `research/carbonsim prelim research.md` already describe a plausible CarbonSim-style pattern: multi-year rounds, free allocation plus auctions, exchange and OTC trading, offsets, banking, and compliance penalties.

Local Vietnam reports suggest an even more conservative pilot framing: negotiated transactions, pre-trade validation, RTGS/DvP settlement, no CCP during the pilot, and daily reconciliation to the national registry. For a workshop product, that supports building a simpler educational market than a full matching engine. `research/20260213_Recommendation_20Report_EN.md`

### Known Gaps or Limitations
Evidence for open-source, carbon-ETS-specific simulators is sparse. The reusable codebases found are generic experiment/game frameworks rather than carbon-market platforms. That implies the main design task is encoding ETS rules credibly, not finding a prebuilt carbon exchange to adapt.

The YouTube source itself was not fetchable beyond title-level metadata, so the brief relies on the local CarbonSim notes plus public CarbonSim and ETS references rather than a verified transcript of the video. https://vncarbonmarket.com/en/carbon-sim/

## Codebase Survey
### Repos Identified
`oTree-org/oTree` is an active Python framework for multiplayer decision games, behavioral experiments, and surveys. GitHub metadata shows recent updates in 2026, 500+ stars, and explicit support for multiplayer games and auctions through docs. https://github.com/oTree-org/oTree

`empiricaly/empirica` is an open-source TypeScript framework for multi-participant and real-time human experiments online. It is more front-end flexible than oTree but heavier to stand up and appears more engineering-intensive. https://github.com/empiricaly/empirica

`nodeGame/nodegame` is a JavaScript framework for online multiplayer real-time games and experiments with bots, waiting rooms, and monitoring. It is powerful but lower-level and older in style than oTree for this use case. https://github.com/nodeGame/nodegame

Carbon-market-specific repos found on GitHub were weak reuse candidates. `mikejsoh/captrade` is a small 2018 Go web app with no visible ecosystem traction, and `Drew-Meseck/Cap-and-Trade-Simulation` is a 2020 notebook-style economics capstone rather than a reusable production base. https://github.com/mikejsoh/captrade https://github.com/Drew-Meseck/Cap-and-Trade-Simulation

### Architecture Summary
oTree's architecture is especially aligned with a small synchronous classroom simulation: rooms for participant intake, server-side Python models for shared state, page flows for round structure, and live pages for real-time bidding and market updates. Its docs explicitly include live pages, wait pages, bots, admin, and data export, which map directly to your scenario. https://otree.readthedocs.io/en/latest/ https://otree.readthedocs.io/en/latest/live.html

Empirica is stronger if the goal shifts toward a custom React-heavy game with more bespoke interaction. Its README positions it as a framework for multi-participant real-time experiments online, but it assumes more stack ownership. https://github.com/empiricaly/empirica

nodeGame offers strong real-time and synchronous control, plus bots and monitors, but its operational style is lower-level and likely increases development and maintenance load relative to oTree for a 10-20 user platform. https://github.com/nodeGame/nodegame

### Key Files and Patterns
The most relevant oTree pattern is `live_method`, which supports server-authoritative real-time messaging for auction-style interaction. The docs show bid submission, broadcast updates, state rehydration on page load, and database-backed message history through `ExtraModel`, which is enough to implement a compact market board, order entry, auction clearing, and OTC messaging. https://otree.readthedocs.io/en/latest/live.html

Local workspace material also provides an implementation-oriented sketch already: `research/carbonsim prelim research.md` includes state-machine concepts, company and unit data models, banking, offsets, penalties, and AI bot ideas. That note is not a source of external truth, but it is a strong internal starting point for planning.

### DeepWiki Notes
No DeepWiki material was available in this workspace for the identified repos.

### Reuse and Adaptation Opportunities
Best reuse path: use oTree for participant/session/admin/export plumbing and implement ETS-specific logic in server-side Python. That reduces both hosting and engineering cost while preserving synchronous multiplayer behavior.

Second-best path: use Empirica if a richer, game-like UI is a hard requirement and you are willing to pay a complexity premium.

Weak path: adapt `captrade` or similar small carbon repos; they appear too stale and narrow to reduce risk meaningfully.

## Mathematical and Algorithmic Foundations
### Problem Formulation
The local Vietnam modeling report defines allowance price formation as a supply-demand equilibrium derived from marginal abatement cost choices. Firms compare abatement cost `Ci` with market price `P`; if `Ci < P`, they abate, otherwise they buy allowances or credits, subject to offset limits. This is a strong fit for a simulation because it yields a simple rules engine grounded in policy analysis rather than arbitrary gameplay. `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`

The same report defines total compliance cost as the sum of in-market abatement, offset purchases, allowance purchases, and higher-cost out-of-market abatement when market instruments are insufficient. That suggests a minimal mathematically credible core: per-firm MAC curve, emissions obligation, allowance allocation, offset limit, and end-of-round compliance accounting. `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`

### Core Algorithms or Methods
A first version can use repeated discrete rounds with these mechanics:
- allocate allowances and emissions obligations
- let firms compare current market price to their MAC options
- allow trades through negotiated deals or a simple order book
- allow offsets up to a cap
- settle and bank surplus allowances
- apply non-compliance penalties

This matches both the World Bank ETS handbook's phased implementation logic and MITRE's experimental evidence that repeated auctions plus secondary trading and banking can produce meaningful strategic behavior without requiring a full institutional market stack. https://documents1.worldbank.org/curated/en/230501617685724056/pdf/Emissions-Trading-in-Practice-A-Handbook-on-Design-and-Implementation.pdf https://www.mitre.org/sites/default/files/pdf/10_2878.pdf

For market design, a classroom simulator has three credible options:
- negotiated trades only, closest to Vietnam pilot recommendations in local reports
- periodic sealed-bid uniform-price auctions plus bilateral secondary trading
- continuous double auction order book, closer to CarbonSim-style gameplay but more complex

Cason and Plott's experimental work is relevant because it compares emissions-trading mechanism behavior directly rather than treating the market layer as a UI afterthought. https://www.ecowin.org/pdf/documents/Carbon%20emissions%20trading%201.pdf

### Complexity and Trade-offs
Negotiated trades are the simplest to explain and implement but produce weaker price discovery and more facilitator dependence. Continuous order books feel more like a live market but add matching, concurrency, and fairness complexity. Periodic auctions with a simple secondary market are the best compromise for 10-20 participants because they create common price signals while keeping interaction legible.

Banking materially improves strategic depth and is supported by both ETS practice and experimental literature. Borrowing should likely be excluded in the first version because local Vietnam references and major ETS practice treat it cautiously or prohibit it in the pilot context. `research/20260213_Recommendation_20Report_EN.md` https://documents1.worldbank.org/curated/en/230501617685724056/pdf/Emissions-Trading-in-Practice-A-Handbook-on-Design-and-Implementation.pdf

### Reference Implementations
There is no strong open-source reference implementation for a Vietnam-style ETS simulator. The nearest practical references are:
- oTree live auction examples for real-time interaction patterns
- CarbonSim public descriptions for product shape
- local `carbonsim prelim research.md` for domain-specific object models and flows

### Key Papers
MITRE's repeated-auction study is directly useful for deciding whether to include bankable allowances and a secondary market. Cason and Plott remain useful for emissions-trading mechanism comparison and experimental grounding. https://www.mitre.org/sites/default/files/pdf/10_2878.pdf https://www.ecowin.org/pdf/documents/Carbon%20emissions%20trading%201.pdf

## Literature and Reports
### Key Papers
Open, directly relevant literature on ETS experiments is thinner than the general ETS design literature. The most useful materials found are experimental or technical rather than recent ML-style academic papers. MITRE's work on repeated auctions and secondary trading is especially relevant because it studies bankable allowances in a repeated setting, which is structurally close to a multi-round classroom simulation. https://www.mitre.org/sites/default/files/pdf/10_2878.pdf

Cason and Plott provide foundational experimental evidence on emissions-trading institutions and are still worth using because the simulator's central design problem is mechanism behavior, not just UI. https://www.ecowin.org/pdf/documents/Carbon%20emissions%20trading%201.pdf

### Technical Reports
The World Bank handbook is the strongest single design reference for turning climate-policy rules into an implementable ETS structure. It covers cap setting, allocation, offsets, auctions, registry, compliance, MRV, and phased rollout, which collectively define what a realistic simulator should and should not include. https://documents1.worldbank.org/curated/en/230501617685724056/pdf/Emissions-Trading-in-Practice-A-Handbook-on-Design-and-Implementation.pdf

ICAP's jurisdiction pages for Vietnam, EU ETS, UK ETS, and China ETS are also high-signal because they summarize live system design elements in a compact comparable format. They are especially useful for deciding which features to simulate in a Vietnam-focused product: EU for mature market institutions, UK for price-stability tools, and China for a less-financialized market with exchange price limits. https://icapcarbonaction.com/en/ets/vietnam https://icapcarbonaction.com/en/compare/99/43 https://icapcarbonaction.com/en/ets/china-national-ets

The local Vietnam CTX reports in this workspace are essential technical reports for this specific project because they discuss governance, transaction methods, surveillance, offset limits, price formation, and pilot constraints in the exact national context you care about. `research/20251128_Recommending_20the_20CTX_20Operational_20Model_20Report_EN.md` `research/20251128_CTX-Model-Impact-Assessment-Report_EN-1.md` `research/20260213_Recommendation_20Report_EN.md` `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`

### Practitioner Sources
CarbonSim's public site is the strongest practitioner source for product benchmarking. It is not enough to reverse-engineer implementation details, but it does validate the demand for a multiplayer carbon market training tool with realistic institution flow. https://vncarbonmarket.com/en/carbon-sim/

oTree documentation is also a practitioner source in the best sense: operationally detailed, actively maintained, and directly relevant to multiplayer auction-style implementation. https://otree.readthedocs.io/en/latest/

### Gaps in Published Work
There is a clear gap between ETS policy literature and open-source simulation implementations. Published work explains ETS design and even experimental market mechanisms, but there is little maintained, open, deployable software for carbon-market training that a small team can adopt as-is. That gap favors a "build small on a mature experiment framework" strategy.

## Sources
- [ICAP About Emissions Trading Systems](https://icapcarbonaction.com/en/about-emissions-trading-systems) - canonical concise explanation of cap-and-trade structure and required design elements.
- [ICAP Vietnam ETS page](https://icapcarbonaction.com/en/ets/vietnam) - current high-level summary of Vietnam's pilot ETS direction and institutions.
- [ICAP Compare ETS: UK and EU ETS](https://icapcarbonaction.com/en/compare/99/43) - compact comparative reference for allocation, stability tools, participation, and compliance design.
- [ICAP China National ETS](https://icapcarbonaction.com/en/ets/china-national-ets) - useful comparator for a less-financialized ETS with exchange price limits and non-financial allowance status.
- [World Bank: Emissions Trading in Practice Handbook](https://documents1.worldbank.org/curated/en/230501617685724056/pdf/Emissions-Trading-in-Practice-A-Handbook-on-Design-and-Implementation.pdf) - best single technical report on ETS design and phased implementation.
- [CarbonSim public site](https://vncarbonmarket.com/en/carbon-sim/) - closest direct prior art for a multiplayer carbon market training simulator.
- [oTree documentation](https://otree.readthedocs.io/en/latest/) - strongest low-cost platform candidate for synchronous multiplayer simulation.
- [oTree live pages docs](https://otree.readthedocs.io/en/latest/live.html) - concrete real-time interaction model for bids, auctions, messaging, and game state sync.
- [Empirica repository](https://github.com/empiricaly/empirica) - alternative real-time experiment framework with more front-end flexibility and more engineering overhead.
- [nodeGame repository](https://github.com/nodeGame/nodegame) - alternative real-time multiplayer framework with strong synchronous controls and bots.
- [Render pricing](https://render.com/pricing) - evidence that a workshop-scale deployment can start on free or very low-cost infrastructure.
- [Cloudflare Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/) - evidence for minimal-cost serverless hosting with free tier and low paid floor.
- [MITRE repeated auctions paper](https://www.mitre.org/sites/default/files/pdf/10_2878.pdf) - experimental evidence for repeated auctions, secondary trading, and bankable allowances.
- [Cason and Plott emissions trading paper](https://www.ecowin.org/pdf/documents/Carbon%20emissions%20trading%201.pdf) - foundational mechanism-design evidence for emissions trading market structure.
