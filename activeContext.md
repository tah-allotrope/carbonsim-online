# Active Context

## Plan

- [x] Review the latest CarbonSim and Vietnam ETS research in `research/`
- [x] Extract the V1 product assumptions that should govern future implementation work
- [x] Create a project `AGENTS.md` that defines scope, stack, rules, and delivery priorities
- [x] Write a detailed multi-phase markdown plan for building the online CarbonSim platform
- [x] Review the planning artifacts for consistency with the cited research and repo context

## Review / Results

- Created `AGENTS.md` as the project operating guide for future implementation work.
- Created `project-plan.md` as the multi-phase roadmap from research synthesis through pilot launch and V2 expansion.
- Locked in the core V1 posture: a Vietnam-aligned compliance simulator first, not an exchange-first trading game.
- Chosen default implementation path: `oTree` for multiplayer session plumbing, admin controls, rooms, exports, and server-authoritative live interactions.
- Captured the main V1 scope constraints: three compressed years, free allocation, sector-specific abatement, limited offsets, banking, penalties, sealed-bid auctions, and simple bilateral/facilitator-mediated secondary trading.
- Deferred higher-risk features such as a continuous order book, advanced AI market-making, and richer financial-market microstructure to later phases after the compliance and round engine are proven.
