---
title: "Retro Isometric Tycoon — Sprint Index (Sprints 1-5)"
date: "2026-06-13"
status: "draft"
request: "Index tying together the five multiphase plans derived from reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md."
plan_type: "index"
---

# Retro Isometric Tycoon — Sprint Index

Execution order for reskinning CarbonSim into a playable retro **isometric tycoon** browser game (free+attribution assets, vanilla JS + canvas + FastAPI), derived from [the gap analysis](../reports/2026-06-13-retro-isometric-tycoon-gap-analysis.md). Sprints are dependency-ordered — do not start a sprint before its predecessor's exit criteria are met. Each plan has its own phases, exit criteria, and (where relevant) a `## Grill Me` question to answer before starting.

## Sequence

| Sprint | Plan | Covers (gaps) | Depends on | Theme |
|---|---|---|---|---|
| 1 | [Retro Asset Pipeline & Static Serving](2026-06-13-retro-asset-pipeline-plan.md) | GAP-03 | — | Source/vet free assets, add `/assets` mount + manifest |
| 2 | [Retro Design Token System & Chrome](2026-06-13-retro-design-tokens-plan.md) | GAP-02 | Sprint 1 | Swap `:root` tokens to tycoon palette + beveled chrome |
| 3 | [Isometric Renderer & State Mapping](2026-06-13-isometric-renderer-plan.md) | GAP-01, GAP-04 | Sprint 2 | Build `isocity.js`, deterministic engine→city mapping |
| 4 | [Retro Reskin Across All Screens](2026-06-13-retro-reskin-all-screens-plan.md) | GAP-05 | Sprint 3 | Consistency sweep + iso default in every mode, remove skyline |
| 5 | [Retro SFX & Perf/A11y Polish](2026-06-13-retro-sfx-perf-polish-plan.md) | GAP-06, GAP-07 | Sprint 4 | Chiptune SFX, pixel effects, perf + accessibility hardening |

## Why this order
- **Assets first (S1):** nothing visual can be built until tiles/sprites/font exist and are servable. Cheapest, unblocks all.
- **Identity before renderer (S2 before S3):** establish the retro palette/chrome so the isometric scene is built to match it, not retro-fitted later.
- **Core renderer before sweep (S3 before S4):** build and prove the iso city behind a feature flag, then make every screen consistent and flip it on.
- **Logic before polish (S4 before S5):** ship the coherent retro look across all modes, then tune sound, performance, and accessibility.

## How to run each sprint
1. Open the sprint plan, answer any `## Grill Me` question (only Sprint 3 has one), update the plan.
2. Execute phases in order; honor each phase's exit criteria.
3. Keep `activeContext.md` pointed at the current sprint/phase.
4. Only advance once the current sprint's verification passes.

## Decisions locked during gap analysis
- **Aesthetic:** isometric tycoon (SimCity 2000 / Theme Hospital register).
- **Scope:** full reskin across all modes (solo, multiplayer, co-op, summary) — not a theme toggle.
- **Assets:** free with attribution acceptable (CC-BY/OFL), CC0 preferred; tracked in `ATTRIBUTIONS.md`.
- **Tech:** stay vanilla JS + canvas + FastAPI; no new frontend framework.
