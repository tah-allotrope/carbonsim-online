---
title: "Kairosoft Visual Upgrade — Sprint Index (Sprints 1-4)"
date: "2026-06-14"
status: "draft"
request: "Index tying together the four multiphase plans derived from reports/2026-06-14-kairosoft-visual-style-gap-analysis.md."
plan_type: "index"
---

# Kairosoft Visual Upgrade — Sprint Index

Execution order for upgrading CarbonSim's in-game visuals to a Kairosoft cute pixel-art tycoon look, derived from [the gap analysis](../reports/2026-06-14-kairosoft-visual-style-gap-analysis.md) and [the research brief](../research/2026-06-14_kairosoft-visual-style.md). This is a **frontend-only, art-and-juice upgrade** on the existing isometric renderer — no engine/test risk. Sprints are dependency-ordered; honor each sprint's exit criteria before the next.

## Sequence

| Sprint | Plan | Covers (gaps) | Depends on | Theme |
|---|---|---|---|---|
| 1 | [Bright Palette & Rounded UI/Font](2026-06-14-kairosoft-palette-ui-plan.md) | GAP-03 | — | Cheapest, instant mood shift; sets the target palette |
| 2 | [Characterful Building Sprite Art & Sourcing](2026-06-14-kairosoft-building-art-plan.md) | GAP-01, GAP-05 | Sprint 1 | The biggest visual lever; cute outlined varied buildings |
| 3 | [Animated Chibi Citizens & Frame-Animation Core](2026-06-14-kairosoft-citizens-plan.md) | GAP-02 | Sprint 2 | The signature "life"; adds sprite animation the renderer lacks |
| 4 | [Floating Feedback Juice + Perf & Cross-Screen](2026-06-14-kairosoft-feedback-juice-plan.md) | GAP-04, GAP-07, GAP-08 | Sprint 3 | Coins/emotes/pop-ups; perf hardening; all screens |

## Why this order
- **Palette first (S1):** pure CSS token swap; instantly shifts the whole app to the bright Kairosoft mood and defines the palette the art must match. Highest impact per effort.
- **Buildings before citizens (S2 before S3):** the single biggest visual change, and citizens populate finished buildings.
- **Citizens need an animation core (S3):** the renderer only blits static frames today; the frame-animation capability built here also serves later effects.
- **Juice last (S4):** floating feedback + perf hardening land best once the scene (buildings + citizens) is in place; also the cross-screen rollout pass.

## How to run each sprint
1. Open the sprint plan, answer its `## Grill Me` questions (Sprints 1 & 2 each have one; 3 & 4 have none), update the plan.
2. Execute phases in order; honor each phase's exit criteria.
3. Keep `activeContext.md` pointed at the current sprint/phase.
4. Verify in the browser before advancing (this is visual work — screenshots/preview matter).

## Open decisions to settle up front
- **Font (S1):** keep Press Start 2P vs. adopt a rounded pixel display font. *Default: add a rounded display font, keep mono for stats.*
- **Asset strategy (S2):** author original pixel art vs. CC0/CC-BY cute-iso packs. *Default: start from CC0 packs + light original edits; track in `ATTRIBUTIONS.md`.* This gates the art sprints.

## Decisions locked
- **Projection:** stays **true isometric** for now (`isocity.js` 2:1 diamond); authentic 3/4 oblique reprojection is backlog (gap-analysis GAP-06).
- **Originality/IP:** Kairosoft-*inspired* originals or CC0/CC-BY only — never Kairosoft's actual assets.
- **Scope:** frontend-only; no engine or gameplay changes.
