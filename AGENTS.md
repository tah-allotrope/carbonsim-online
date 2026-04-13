# CarbonSim Online Project Guide

## Mission

Build an online, workshop-ready CarbonSim-style platform for Vietnam-focused ETS training.

The product goal is not a generic carbon game. The goal is a credible, legible compliance-market simulator that helps 10-20 participants understand cap setting, free allocation, abatement, limited offsets, trading, banking, surrender, and penalties across compressed simulation years.

## Source Of Truth Order

When implementation decisions conflict, use this precedence order:

1. `research/2026-04-13_online-carbonsim-platform-create.md`
2. `research/20260213_Recommendation_20Report_EN.md`
3. `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`
4. `research/carbonsim prelim research.md`
5. `research/2026-04-06_online-carbonsim-platform.md`

Do not invent ETS rules if the local research already answers the question.

## Product Positioning

### V1 Product Shape

V1 is a compliance-market simulator first.

It should feel close to CarbonSim in learning flow, but its rule design should be anchored to Vietnam's pilot posture rather than to a highly financialized exchange.

### Primary Users

- Workshop participants learning ETS mechanics
- Facilitators running live sessions
- Policy, academic, and capacity-building teams needing exportable session data

### Default Session Shape

- 10-20 human participants
- 3 compressed virtual years
- 20-30 minutes per virtual year unless testing proves a better default
- Facilitator-controlled room/session start
- Server-authoritative timing and state changes

## Non-Negotiable V1 Rules

### Include In V1

- Free allocation at the start of each year
- Firm or sector-specific emissions baseline and growth assumptions
- Sector-specific abatement menus with marginal cost logic
- Limited offset use with a configurable cap
- Banking of unused allowances
- Year-end surrender and penalty logic
- A simple, legible trading layer
- Facilitator/admin controls
- Data export for post-session analysis

### Exclude From V1 By Default

- Continuous double-auction order book as the main market
- Derivatives or speculative financial features
- Borrowing, unless later product requirements explicitly demand it
- Complex settlement replicas beyond what is needed for pedagogy
- Heavy custom front-end architecture before core rules are stable

## Recommended Technical Direction

### Default Stack

- Framework: `oTree`
- Core language: Python
- Real-time interaction: `oTree` live pages / `live_method`
- Persistence: start with the simplest supported database for development, then move to Postgres for deployed sessions if needed
- Hosting target: low-cost deployment suitable for workshop usage, not premature scale infrastructure

### Why `oTree`

`oTree` is the default because it already provides the session, room, admin, export, and synchronized multiplayer primitives this project needs.

Do not move to `Empirica`, `Colyseus`, or a custom real-time stack unless V1 is blocked by a demonstrated limitation in `oTree`.

## Architecture Principles

### 1. Compliance Before Market Microstructure

The compliance engine is the product core. Trading exists to support compliance learning, not the other way around.

### 2. Server-Authoritative State

All timers, allocations, auction results, trade validation, surrender, penalties, and leaderboard updates must be computed on the server.

### 3. Simple And Explainable First

Prefer features that are easy for facilitators and participants to understand during a live workshop.

### 4. Research-Grounded Defaults

When choosing defaults, prefer Vietnam-pilot-aligned settings over generic ETS or financial-market conventions.

### 5. Deterministic Year Flow

Model the game as a clear state machine: lobby, year start, action windows, year end, compliance, next year, game over.

### 6. Auditability Matters

Persist the decisions and outcomes needed to reconstruct what happened in a session: allocations, bids, trades, abatement choices, surrender, penalties, rankings, and facilitator actions.

## V1 Domain Defaults

These are implementation defaults unless a phase plan or explicit product decision changes them:

- Three compressed years
- Free allocation at year start
- Banking allowed
- Borrowing disabled
- Offsets allowed only within a configurable cap
- Trading centered on sealed-bid auctions plus simple bilateral or facilitator-mediated secondary trading
- Penalty high enough that intentional non-compliance is never rational
- Price discovery driven by abatement cost, cap pressure, offset availability, and participant decisions

## V1 Feature Priorities

### Must Have

- Session creation and room join flow
- Participant company assignment
- Company dashboard with emissions, allocation, holdings, cash, and compliance position
- Abatement decision flow
- Year-start allocation and year-end compliance engine
- Auction flow
- Simple secondary trading flow
- Offset usage logic
- Banking and penalty handling
- Facilitator controls and exports
- Leaderboard or outcome summary

### Nice To Have If Cheap

- Shock events between years
- Basic bot participants for liquidity support
- Public trade feed
- Explainers or helper text inside the UI

### Defer To V2+

- Continuous order book
- Advanced AI agents
- Rich visual market charts beyond what helps learning
- Multi-market or cross-border scenarios
- Sophisticated registry or settlement simulation layers

## User Experience Rules

- Favor clarity over realism when the two are in tension.
- Every major player action should answer: what is my obligation, what are my options, what happens if I do nothing?
- The facilitator experience is a first-class product surface, not an afterthought.
- Avoid cluttered trader UIs that assume professional market knowledge.
- Keep mobile usability acceptable, but optimize first for facilitator-led desktop or laptop workshops.

## Delivery Rules

### Build Order

1. Prove the framework and session flow
2. Implement the compliance and year-state engine
3. Add abatement and offsets
4. Add auctions
5. Add simple secondary trading
6. Add facilitator tools, exports, and analytics
7. Add bots, shocks, and richer market behavior only after the core loop is stable

### Testing Expectations

- Write tests for the rules engine before or alongside implementation
- Prefer deterministic fixtures for cap, allocation, abatement, offsets, and penalties
- Add scenario tests that simulate a full three-year session
- Verify edge cases around offset caps, banking carry-forward, and non-compliance
- Run manual facilitator dry-runs before calling a phase complete

### Documentation Expectations

- Keep rules, assumptions, and formulas close to the code they govern
- Update this file when scope or architecture decisions materially change
- Record deviations from the research with a short rationale

## Guardrails For Future Agents

- Do not start with a continuous exchange UI just because CarbonSim can support one.
- Do not overfit to foreign ETS market structure if it conflicts with Vietnam pilot evidence.
- Do not add front-end complexity before the rules engine and facilitator flow are proven.
- Do not treat AI bots as mandatory for the very first playable prototype; introduce them when liquidity and pedagogy demand it.
- Do not mark a phase done without a runnable end-to-end workshop scenario.

## Phase Reference

Use `project-plan.md` as the execution roadmap.

If a task conflicts with the roadmap, update the roadmap first or explicitly document why the deviation is necessary.
