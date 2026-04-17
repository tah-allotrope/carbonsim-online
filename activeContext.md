# Active Context

## Plan

- [x] Review the latest CarbonSim and Vietnam ETS research in `research/`
- [x] Extract the V1 product assumptions that should govern future implementation work
- [x] Create a project `AGENTS.md` that defines scope, stack, rules, and delivery priorities
- [x] Write a detailed multi-phase markdown plan for building the online CarbonSim platform
- [x] Review the planning artifacts for consistency with the cited research and repo context
- [x] Inspect the current repository state and local Python runtime support for `oTree`
- [x] Update the repository with a concrete implementation plan for phases 1 and 2
- [x] Scaffold an `oTree` project with a multiplayer-ready CarbonSim workshop app
- [x] Implement session creation, join flow, facilitator visibility, and a placeholder company dashboard
- [x] Add a deterministic year-state engine with year-start allocation and year-end compliance processing
- [x] Write and run tests for allocation, emissions growth, banking, penalties, and multi-year scenarios
- [x] Update repo documentation for local setup and verification
- [x] Generate a phase report artifact for phase 1
- [x] Generate a phase report artifact for phase 2
- [x] Extend the implementation plan to cover phase 3 abatement and offset decisions
- [x] Add failing tests for sector-specific abatement logic, activation timing, offset caps, and dashboard projections
- [x] Implement phase 3 abatement menus, persistence rules, offset holding logic, and projected compliance updates
- [x] Update the live workshop dashboard so participants can make abatement and offset decisions during the decision window
- [x] Run verification for phase 3 and generate the phase 3 report artifact
- [x] Extend the implementation plan to cover phase 4 sealed-bid auctions
- [x] Add failing tests for auction scheduling, bid validation, clearing, tie behavior, and holdings settlement
- [x] Implement the phase 4 auction engine with public result display and facilitator controls
- [x] Update the live workshop dashboard with bid entry and auction status views
- [x] Run verification for phase 4, generate the phase 4 report artifact, and create the requested git commit
- [x] Extend the implementation plan to cover phase 5 bilateral secondary trading
- [x] Add failing tests for trade proposal, acceptance, rejection, expiration, duplicate handling, and settlement validation
- [x] Implement the phase 5 trading engine with server-side validation, audit history, and a public trade feed
- [x] Update the live workshop dashboard with trade proposal and trade response controls
- [x] Run verification for phase 5, generate the phase 5 report artifact, create the requested git commit, and push to origin

## Review / Results

- Created `AGENTS.md` as the project operating guide for future implementation work.
- Created `project-plan.md` as the multi-phase roadmap from research synthesis through pilot launch and V2 expansion.
- Locked in the core V1 posture: a Vietnam-aligned compliance simulator first, not an exchange-first trading game.
- Chosen default implementation path: `oTree` for multiplayer session plumbing, admin controls, rooms, exports, and server-authoritative live interactions.
- Captured the main V1 scope constraints: three compressed years, free allocation, sector-specific abatement, limited offsets, banking, penalties, sealed-bid auctions, and simple bilateral or facilitator-mediated secondary trading.
- Confirmed the local machine has Python 3.12 available through `uv`, which is suitable for installing `oTree`, while the default Python 3.14 runtime is likely too new for a stable `oTree` setup.
- Scaffolded an `oTree` project in `platform/` and added the `carbonsim_phase12` app wired into `platform/settings.py` with a workshop room and a phase-specific session config.
- Implemented the phase 1 participant experience: company assignment on session creation, facilitator designation, a join screen, and a live workshop dashboard fed by `oTree` live messages.
- Implemented the phase 2 rules engine in `platform/carbonsim_phase12/engine.py` with deterministic company generation, annual allocations, emissions growth, state transitions, banking, penalties, and an auditable event log.
- Added regression coverage in `platform/tests/test_engine.py` for company generation, year-start processing, year-end processing, three-year completion, audit logging, dashboard snapshots, and session config registration.
- Updated `README.md`, `.gitignore`, and `platform/requirements.txt` with the local Python 3.12 workflow, browser-bot helper dependencies, and the Windows-specific `oTree` boot nuance around `PATH` and SQLite schema versioning.
- Verified the prototype with `../.venv/Scripts/python.exe -m unittest tests.test_engine` from `platform/` and with a real `oTree` boot check against `http://127.0.0.1:8001/` after setting the expected SQLite `user_version` value for the installed `oTree` build.
- Generated the requested HTML phase artifacts in `reports/2026-04-17-phase-one-skeleton-app.html` and `reports/2026-04-17-phase-two-compliance-engine.html` using the loaded report template contract.
- Implemented phase 3 in the shared rules engine with sector-specific abatement catalogs, committed abatement costs, immediate versus next-year activation timing, offset purchases, offset surrender caps, and updated compliance projections.
- Extended the live workshop page so participants can commit abatement measures and buy offsets during the decision window while seeing projected emissions, offset holdings, and forward-looking net position update live.
- Expanded the unit suite to cover phase 3 behavior and confirmed the red-to-green flow by fixing the timing bug where decisions were initially ignored before the engine advanced into the decision window.
- Generated the phase 3 HTML artifact in `reports/2026-04-17-phase-three-abatement-offsets.html` using the same report template workflow as phases 1 and 2.
- Implemented phase 4 as a sealed-bid uniform-price allowance auction layered into the shared engine, with year-start auction scheduling, facilitator open and clear controls, bid validation, deterministic tie handling, and settlement into cash plus allowance holdings.
- Extended the live workshop dashboard with an auction board, public clearing output, facilitator auction lifecycle controls, and participant bid-entry controls that run through the existing `live_method` path.
- Expanded the unit suite to 15 tests and verified auction schedule creation, invalid bid rejection, clearing, settlement, and tie behavior on top of the earlier compliance and abatement rules.
- Generated the phase 4 HTML artifact in `reports/2026-04-17-phase-four-auction-market.html` and prepared the repo for the requested implementation commit.
- Implemented phase 5 as a bilateral trading layer with trade proposal, buyer response, expiry handling, duplicate-response protection, server-side settlement validation, and a public trade feed recorded in the shared engine state.
- Extended the live workshop dashboard with a trade proposal form, company trade inbox, accept and reject controls for buyers, and a public trade feed to make post-auction rebalancing visible and explainable.
- Expanded the unit suite to 20 tests and verified trade proposal, acceptance, rejection, expiry, and insufficient holdings or cash handling on top of the earlier compliance, abatement, and auction rules.
- Generated the phase 5 HTML artifact in `reports/2026-04-17-phase-five-secondary-trading.html` and prepared the repo for the requested commit and push to `origin`.
