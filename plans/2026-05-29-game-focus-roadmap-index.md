---
title: "Game-Focus Roadmap — Sprint Index (Sprints 1-5)"
date: "2026-05-29"
status: "draft"
request: "Index tying together the five sequenced multiphase plans derived from reports/2026-05-29-single-multiplayer-game-gap-analysis.md."
plan_type: "index"
---

# Game-Focus Roadmap — Sprint Index

This is the execution order for refocusing the repo onto a single + multiplayer carbon-market game with improved visuals, derived from [the gap analysis](../reports/2026-05-29-single-multiplayer-game-gap-analysis.md). Sprints are strictly dependency-ordered — do not start a Sprint before its predecessor's exit criteria are met. Each plan has its own phases and `## Grill Me` questions to answer before starting.

## Sequence

| Sprint | Plan | Covers (gaps) | Depends on | Theme |
|---|---|---|---|---|
| 1 | [Canonical Game Stack Consolidation](2026-05-29-canonical-game-stack-consolidation-plan.md) | GAP-01, GAP-02, GAP-07 | — | Pick one product, remove oTree, fix the lying docs |
| 2 | [Repository Reorganization & Clutter Purge](2026-05-29-repo-reorganization-cleanup-plan.md) | GAP-06 | Sprint 1 | Conventional layout, delete duplicate worktree & obsolete reports |
| 3 | [Engine Trim, Modularization & Test Unification](2026-05-29-engine-trim-test-unification-plan.md) | GAP-03, GAP-08 | Sprint 2 | Clean, tested core; fix the 2 failing tests |
| 4 | [Single-Player Polish & Multiplayer Build-Out](2026-05-29-singleplayer-multiplayer-buildout-plan.md) | GAP-05 | Sprint 3 | Real lobby/room/host/reconnect multiplayer |
| 5 | [Visual Step-Change](2026-05-29-visual-step-change-plan.md) | GAP-04 | Sprint 4 | Design system + signature animated visual |

## Why this order
- **Docs/stack first (S1):** every later Sprint targets the wrong product if `README`/`AGENTS` still describe oTree. Cheapest, highest-leverage, unblocks all.
- **Reorg before refactor (S2 before S3):** move files once, while the tree is small (oTree already removed), so import churn happens a single time.
- **Stable core before features (S3 before S4/S5):** trim/test the engine so multiplayer and visuals build on solid ground.
- **Logic before polish (S4 before S5):** ship working single+multiplayer, then make it look like a step up from CarbonSim.

## How to run each Sprint
1. Open the Sprint plan, answer its `## Grill Me` questions, update the plan.
2. Execute phases in order; honor each phase's exit criteria.
3. Keep `activeContext.md` pointed at the current Sprint/phase.
4. Only advance to the next Sprint once the current Sprint's verification passes.
