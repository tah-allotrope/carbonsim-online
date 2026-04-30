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
- [x] Add failing tests for auction scheduling, bidding, clearing, and dashboard integration
- [x] Implement phase 4 sealed-bid auctions with multi-bid clearing, results, and dashboard updates
- [x] Run verification for phase 4 and generate the phase 4 report artifact
- [x] Extend the implementation plan to cover phase 5 secondary trading
- [x] Add failing tests for trade proposal, acceptance, expiry, and dashboard feed
- [x] Implement phase 5 bilateral trading with expiry, accept/reject, and live trade feed
- [x] Run verification for phase 5 and generate the phase 5 report artifact
- [x] Extend the implementation plan to cover phase 6 facilitator tools
- [x] Add failing tests for session pause/resume, phase advance, participant status, and snapshot
- [x] Implement phase 6 facilitator controls: pause/resume, force-advance, status tracking, facilitator snapshot
- [x] Run verification for phase 6 and generate the phase 6 report artifact
- [x] Extend the implementation plan to cover phase 7 scenarios, bots, and shocks
- [x] Add failing tests for scenario packs, bot strategies, shock application, and session replay
- [x] Implement phase 7: scenario packs, bot AI, shock events, session replay, and analytics
- [x] Run verification for phase 7 and generate the phase 7 report artifact
- [x] Extend the implementation plan to cover phase 8 pilot deployment
- [x] Add failing tests for deployment hardening, config, health checks, and session recovery
- [x] Implement phase 8: deployment config, health endpoint, session recovery, and oTree launch wrappers
- [x] Run verification for phase 8 and generate the phase 8 report artifact
- [x] Extend the implementation plan to cover phase 9 session replay and export
- [x] Add failing tests for export format, replay data, analytics, and summary
- [x] Implement phase 9: session replay, analytics dashboard, CSV/JSON export, and session summary
- [x] Run verification for phase 9 and generate the phase 9 report artifact
- [x] Write the Climate Mayor single-player narrative tycoon multi-phase plan
- [x] Implement Phase 1: Extract engine into standalone `carbonsim_engine/` package
- [ ] Implement Phase 2: Event-Card System (50+ events, CardDeck class, integration)

## Goal
- Implement Phase 2 of the Climate Mayor plan: Event-Card System

## Constraints & Preferences
- 50+ event cards across 4 types: policy, market, weather, tech
- Each event has: id, type, title, description, effect (dict), rarity (common/rare/legendary)
- CardDeck class with: draw(), shuffle(), seed-based determinism, discard pile
- Wire into existing `apply_shock()` in engine
- Events must be legible to non-expert players (workshop-friendly language)
- Follow Vietnam ETS research for realistic event modeling

## Progress
### Done
- (Phase 1 complete — see prior section)

### In Progress
- Phase 2: Event-Card System

### Blocked
- (none)

## Key Decisions
- (TBD during implementation)

## Next Steps
- Create `carbonsim_engine/events.py` with 50+ event definitions
- Create `carbonsim_engine/deck.py` with CardDeck class
- Update `carbonsim_engine/__init__.py` to export new types
- Write tests in `carbonsim_engine/tests/test_events.py`
- Update `SHOCK_CATALOG` in `scenarios.py` to reference event IDs
- Generate Phase 2 report

## Critical Context
- `apply_shock(state, shock_type, intensity, year)` already exists in engine.py
- Shock types in engine: "carbon_price_crash", "new_regulation", "technology_breakthrough", "recession"
- Event cards should map to these shock types (or extend them)
- Solo mode (Phase 3+) will draw event cards between years

## Relevant Files
- `carbonsim_engine/engine.py`: contains `apply_shock()` at line ~1970
- `carbonsim_engine/scenarios.py`: contains `SHOCK_CATALOG`
- `carbonsim_engine/solo.py`: stub for future solo mode that will use events
- `plans/2026-04-30-climate-mayor-plan.md`: Phase 2 spec at section "Phase 2 -- Event-Card System"
