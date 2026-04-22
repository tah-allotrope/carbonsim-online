# Online CarbonSim Multi-Phase Plan

## Goal

Build a Vietnam-aligned, workshop-ready online CarbonSim platform that teaches ETS compliance behavior through a multi-user simulation with free allocation, abatement, limited offsets, simple trading, banking, surrender, and penalties.

## Planning Assumptions

- V1 targets 10-20 human participants in a facilitator-led session
- V1 uses `oTree` unless a concrete blocker is found
- V1 optimizes for compliance-market learning, not exchange realism
- V1 should be usable in live workshops before it is fully feature-complete relative to public CarbonSim descriptions
- Local research in `research/` is the primary source of truth for Vietnam-specific rules and product posture

## Product Thesis

The best first version is a hybrid:

- Use CarbonSim's learning shape: compressed years, company decisions, auctions, trading, and outcome feedback
- Use Vietnam-pilot-aligned rules: free allocation, controlled trading, limited offsets, high oversight, and simple market structure
- Use the local modeling logic: firms abate when abatement cost is below market price, then use offsets within limits, then acquire allowances or absorb higher compliance cost

## V1 Scope Definition

### Core Scenario

Each participant controls a company in a covered sector. Over three compressed virtual years, they must stay compliant at the lowest total cost by combining abatement, offsets, and trading decisions under a tightening cap.

### V1 Mechanics

- Year-start allocation
- Emissions baseline plus growth
- Sector-specific abatement options
- Offset usage cap
- Banking of unused allowances
- Sealed-bid auction windows
- Simple bilateral or facilitator-mediated secondary trades
- Year-end surrender and penalty settlement
- Ranking or outcome summary based on compliance efficiency

### Explicit V1 Non-Goals

- Full continuous order-book exchange
- Derivatives, leverage, or advanced financial products
- Perfect replication of registry, clearing, and settlement institutions
- Massive multiplayer scale
- Production-grade AI market ecosystem before the workshop loop is proven

## Phase 0 - Research Consolidation And Product Framing

### Objective

Turn the current research set into a stable implementation brief with clear V1 defaults and exclusions.

### Deliverables

- `AGENTS.md` with project rules and architecture guidance
- Confirmed V1 mechanics list
- Confirmed V2 backlog list
- Glossary of domain terms used consistently across product and code

### Tasks

- Normalize terminology: allowance, offset, allocation, surrender, compliance position, banking, penalty, auction, secondary trade
- Resolve any remaining ambiguity in offset cap, banking policy, and borrowing posture for V1 defaults
- Decide the default sectors for the first scenario set
- Decide what gets simulated versus explained in facilitator notes

### Exit Criteria

- Future implementation work can proceed without re-litigating the basic product shape
- V1 and V2 boundaries are written down clearly

## Phase 1 - Technical Spike And Skeleton App

### Objective

Prove the chosen stack can run a real multi-user workshop flow with minimal infrastructure.

### Deliverables

- Running `oTree` project in the repo
- Basic room/session creation flow
- Participant join flow
- Facilitator/admin access flow
- Placeholder company dashboard page

### Tasks

- Scaffold the base `oTree` app structure
- Establish local development workflow and environment setup
- Create one minimal synchronous game session with timer-driven transitions
- Verify that live updates work across multiple browser sessions
- Decide the baseline data model structure for sessions, players, companies, and yearly state

### Test And Verification

- Manual multi-tab dry run with at least 3 simulated participants
- Smoke test for session creation, joining, and page transitions
- Document setup steps in repo docs

### Exit Criteria

- The project has a working multiplayer skeleton suitable for domain logic implementation

## Phase 2 - Compliance Engine And Year State Machine

### Objective

Implement the rules engine that drives the entire simulation.

### Deliverables

- Deterministic year-start and year-end processing
- Cap, allocation, emissions growth, and compliance calculations
- Banking and penalty logic
- Round state machine documented in code and tests

### Tasks

- Model three-year session lifecycle
- Implement cap decline and yearly allocation logic
- Implement emissions baseline and growth progression
- Compute compliance position at any point in the year
- Implement year-end surrender flow and penalty application
- Persist an auditable event history for key state changes

### Test And Verification

- Unit tests for allocation, emissions growth, banking, and penalties
- Scenario tests for compliant, short, and surplus companies
- One end-to-end simulation test covering three years with deterministic fixtures

### Exit Criteria

- A facilitator can run a no-trading simulation and still get coherent yearly compliance outcomes

## Phase 3 - Abatement And Offset Decision System

### Objective

Add the strategic decision layer that makes compliance behavior meaningful.

### Deliverables

- Sector-specific abatement menu model
- Abatement activation and persistence rules
- Offset holdings and usage cap logic
- Player dashboard showing cost/compliance impact of decisions

### Tasks

- Define the first set of sectors, probably thermal power, steel, and cement
- Create a small abatement catalog for each sector
- Model immediate versus delayed abatement activation where needed
- Implement offset purchase/holding/usage constraints
- Expose forward-looking compliance impact on the player dashboard

### Test And Verification

- Tests for MAC-based abatement effect on emissions
- Tests for offset usage capping at surrender time
- Manual walkthrough confirming the UI makes tradeoffs understandable

### Exit Criteria

- Participants can reduce exposure through abatement and offsets before market trading is added

## Phase 4 - Auction Market

### Objective

Introduce a simple, legible price-discovery mechanism that fits both pedagogy and Vietnam-aligned market conservatism.

### Deliverables

- Sealed-bid auction flow
- Auction schedule within each simulated year
- Auction clearing logic
- Public auction result display

### Tasks

- Choose one auction design for V1, preferably sealed-bid uniform-price unless testing shows a simpler method is better
- Implement bid entry, validation, closing, clearing, and allocation
- Broadcast auction outcomes to all participants
- Update holdings and cash balances after auction settlement
- Provide facilitator controls to open, close, and rerun auctions if needed during testing

### Test And Verification

- Clearing logic tests including tie and oversubscription cases
- Manual multi-user auction dry run
- Verify auction results match deterministic fixture expectations

### Exit Criteria

- The platform produces a common market price signal through auctions without requiring an order book

## Phase 5 - Secondary Trading Layer

### Objective

Add a simple secondary market that supports strategy without overwhelming users or the implementation.

### Deliverables

- Bilateral trade request flow or facilitator-mediated deal flow
- Trade validation and settlement logic
- Public or semi-public trade feed

### Tasks

- Select the simplest V1 secondary-trade pattern
- Implement trade proposal, acceptance, rejection, expiration, and settlement
- Validate holdings and cash constraints server-side
- Record trade history for audit and replay
- Add clear participant feedback about the impact of each trade

### Test And Verification

- Tests for invalid trades, duplicate acceptance, insufficient holdings, and race-like conditions
- Manual dry run with multiple simultaneous trade attempts

### Exit Criteria

- Participants can rebalance positions after auctions in a controlled and explainable way

## Phase 6 - Facilitator Tools, Analytics, And Session Exports

### Objective

Make the simulator operationally usable in real workshops.

### Deliverables

- Facilitator control panel
- Session timeline controls
- Participant status view
- Exportable session data
- End-of-session summary

### Tasks

- Add facilitator actions for start, pause, resume, next phase, and year close
- Add participant health/status indicators
- Export bids, trades, abatements, offsets, compliance outcomes, and rankings
- Add a session summary view suitable for debriefing
- Add facilitator notes for interpreting outcomes

### Test And Verification

- Full facilitator rehearsal from room creation through debrief
- Verify exports are complete enough for analysis
- Confirm that a workshop can recover from a stuck participant or timing hiccup

### Exit Criteria

- A facilitator can run a complete session without needing developer intervention

## Phase 7 - Pilot Scenario Design And Bot Support

### Objective

Prepare a robust first workshop package that works even when participant behavior is uneven.

### Deliverables

- First polished scenario pack
- Optional bot participants or bot liquidity helpers
- Shock-event capability if it materially improves teaching value

### Tasks

- Tune cap decline, growth, abatement costs, and penalty levels for a compelling three-year arc
- Add lightweight bots only if human-only sessions feel too thin
- Add one or two facilitator-triggered shocks if testing shows they improve learning outcomes
- Calibrate the scoring and leaderboard logic for fairness and clarity

### Test And Verification

- Multiple internal playtests with varying participant counts
- Compare results across small and large workshop sizes
- Ensure bots do not dominate or distort the lesson

### Exit Criteria

- The first workshop scenario consistently generates understandable strategy, price movement, and debrief material

## Phase 8 - Pilot Deployment And Dry-Run Operations

### Objective

Turn the prototype into a repeatable pilot service for real sessions.

### Deliverables

- Deployment setup
- Basic security and reliability hardening
- Runbook for workshop prep and live support

### Tasks

- Choose a low-cost deployment path that suits `oTree`
- Configure environment variables, persistent storage, backups, and logs
- Add authentication or access controls appropriate for facilitator/admin surfaces
- Add operational monitoring that is simple but sufficient for live workshops
- Write a runbook for before, during, and after session operations

### Test And Verification

- Staging dry run with realistic participant count
- Failure drill for refresh, reconnect, and facilitator recovery actions
- Verify exports and logs after a completed session

### Exit Criteria

- The team can host a live pilot session with acceptable operational confidence

## Phase 9 - Session Replay And Visualization

### Objective

Turn completed workshop sessions into legible replay artifacts that facilitators can use during debriefs without exporting raw JSON into another tool first.

### Deliverables

- Replay timeline for audit events
- Year-by-year replay markers for penalties, banking, trades, and auction outcomes
- Facilitator-facing replay view
- Export payload that includes replay data

### Tasks

- Build a server-side replay dataset from the auditable event log
- Summarize each simulated year into a small set of debrief-friendly markers
- Surface replay data in the facilitator panel
- Keep the replay exportable for offline review

### Test And Verification

- Tests for replay timeline completeness
- Tests for year marker accuracy after auction, trade, and shock events
- Manual facilitator check that the replay is understandable during a live debrief

### Exit Criteria

- A facilitator can reconstruct the important events of a session in order without inspecting raw logs

## Phase 10 - Expanded Facilitator Analytics

### Objective

Give facilitators a stronger post-session analytics surface so they can compare sectors, year outcomes, and participant cost drivers inside the product.

### Deliverables

- Market analytics summary
- Sector-level breakdowns
- Year-level metrics table
- Company cost analytics
- Export payload that includes analytics data

### Tasks

- Aggregate auction, trade, abatement, offset, and penalty activity into facilitator metrics
- Add sector and year summaries that support workshop discussion
- Surface analytics in the facilitator panel and export payload
- Preserve the current simple market structure while improving interpretability

### Test And Verification

- Tests for analytics aggregation after representative market actions
- Tests that facilitator snapshots expose analytics data
- Manual facilitator check that the analytics are useful for debriefing

### Exit Criteria

- A facilitator can explain who incurred costs, how the market evolved, and where compliance pressure concentrated without leaving the simulator

## Future V2 Candidate Tracks

- Richer secondary market, possibly a simple order book
- More sectors and scenario variants
- Stronger bot behaviors
- Multi-language support
- Deeper registry or settlement simulation if needed for training goals

## Decision Gate

Only add exchange-style complexity if pilot results show the current auction plus simple trading model fails to create the learning outcomes you need.

## Cross-Phase Workstreams

### Rules And Calibration

This runs through all phases.

- Keep the penalty structure clearly above rational non-compliance
- Tune cap decline and emissions growth so pressure rises across years
- Keep offset policy explicit and configurable
- Use small, transparent scenario datasets before increasing realism

### Testing Strategy

- Unit tests for every financial or compliance calculation
- Scenario tests for each phase boundary
- End-to-end dry runs before phase completion
- Regression tests for previously fixed rules bugs

### Documentation Strategy

- Update `AGENTS.md` when the project rules change
- Maintain a short scenario-spec document once implementation begins
- Document any deviations from research-backed defaults

## Recommended Initial Backlog

Start with these concrete tickets:

1. Scaffold the base `oTree` project
2. Implement session, room, and player/company assignment flows
3. Implement the three-year simulation state machine
4. Implement allocation, emissions, banking, and penalty calculations with tests
5. Implement abatement and offset models with tests
6. Implement the first sealed-bid auction flow
7. Implement simple bilateral trades
8. Build facilitator controls and exports
9. Run internal playtests and calibrate the scenario

## Definition Of A Successful V1

V1 is successful if:

- A facilitator can run a live workshop with 10-20 participants
- Participants can understand their compliance position and available actions
- The simulation creates real strategic tradeoffs around abatement, offsets, and allowance scarcity
- The results are exportable and useful for debriefing
- The implementation remains simple enough to operate and extend without a major platform rewrite
