# CarbonSim Online Project Guide

## Mission

Build a polished single-player and multiplayer carbon compliance game that teaches ETS mechanics through strategic decision-making across compressed simulation years.

The product is a game first. It uses Vietnam-pilot-aligned rules as its domain foundation, but its primary goal is an engaging, legible learning experience — not a workshop platform replica.

## Source Of Truth Order

When implementation decisions conflict, use this precedence order:

1. `reports/2026-05-29-single-multiplayer-game-gap-analysis.md`
2. `research/2026-04-13_online-carbonsim-platform-create.md`
3. `research/20260213_Recommendation_20Report_EN.md`
4. `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`
5. `research/carbonsim prelim research.md`

Do not invent ETS rules if the local research already answers the question.

## Technical Stack

- **Engine:** `engine/` — Python compliance engine
- **Server:** `server/` — FastAPI with WebSocket support
- **Frontend:** `web/` — static HTML/CSS/JS (vanilla, no build step)
- **Database:** SQLite (dev), Postgres (production)
- **Testing:** pytest

## Architecture Principles

### 1. Compliance Before Market Microstructure

The compliance engine is the product core. Trading exists to support compliance learning, not the other way around.

### 2. Server-Authoritative State

All timers, allocations, auction results, trade validation, surrender, penalties, and leaderboard updates must be computed on the server.

### 3. Simple And Explainable First

Prefer features that are easy for players and hosts to understand.

### 4. Research-Grounded Defaults

When choosing defaults, prefer Vietnam-pilot-aligned settings over generic ETS or financial-market conventions.

### 5. Deterministic Year Flow

Model the game as a clear state machine: lobby, year start, action windows, year end, compliance, next year, game over.

### 6. Auditability Matters

Persist the decisions and outcomes needed to reconstruct what happened in a session.

## V1 Domain Defaults

- Three compressed years
- Free allocation at year start
- Banking allowed
- Borrowing disabled
- Offsets allowed only within a configurable cap
- Trading centered on sealed-bid auctions plus simple bilateral trading
- Penalty high enough that intentional non-compliance is never rational

## Feature Priorities

### Must Have

- Single-player game loop (create, decisions, advance years, completion, summary)
- Multiplayer with lobby, room codes, host controls, and reconnection
- Company dashboard with emissions, allocation, holdings, cash, and compliance position
- Abatement decision flow with sector-specific menus
- Year-start allocation and year-end compliance engine
- Auction flow
- Simple secondary trading
- Offset usage logic
- Banking and penalty handling
- Leaderboard or outcome summary

### Nice To Have

- Shock events between years
- Basic bot participants for liquidity support
- Public trade feed
- Tutorial mode and helper text
- Achievement system

### Defer To V2+

- Continuous order book
- Advanced AI agents
- Multi-market or cross-border scenarios
- Sophisticated registry or settlement simulation

## User Experience Rules

- Favor clarity over realism when the two are in tension.
- Every major player action should answer: what is my obligation, what are my options, what happens if I do nothing?
- The host/facilitator experience is a first-class product surface.
- Avoid cluttered trader UIs that assume professional market knowledge.
- Optimize for desktop/laptop; mobile usability is acceptable but secondary.
- Visual quality should be a clear step above table-based simulators.

## Sprint Roadmap

Use `plans/2026-05-29-game-focus-roadmap-index.md` as the execution roadmap. The five sprints are dependency-ordered:

1. Canonical Game Stack Consolidation
2. Repository Reorganization & Clutter Purge
3. Engine Trim, Modularization & Test Unification
4. Single-Player Polish & Multiplayer Build-Out
5. Visual Step-Change

## Testing Expectations

- Write tests for the rules engine before or alongside implementation
- Prefer deterministic fixtures for cap, allocation, abatement, offsets, and penalties
- Add scenario tests that simulate a full three-year session
- Verify edge cases around offset caps, banking carry-forward, and non-compliance
- Run `pytest server/tests/test_api.py engine/tests/ -q` before committing

## Guardrails For Future Agents

- Do not reintroduce oTree or the archived workshop platform.
- Do not add a build step to the frontend unless explicitly justified.
- Do not add front-end complexity before the rules engine and multiplayer flow are proven.
- Do not treat AI bots as mandatory; introduce them when liquidity and pedagogy demand it.
- Do not mark a sprint done without a runnable end-to-end scenario.
- Visual work is bounded to Sprint 5's plan — do not over-engineer the frontend before then.
