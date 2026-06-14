# Gap Analysis: McDonald's-Style Satirical Multi-Sector Tycoon

**Date:** 2026-06-14
**Scope:** Evolve CarbonSim from a single-company, turn-based carbon-compliance sim into a *McDonald's Video Game*-style opinionated tycoon — interconnected supply-chain sectors, a real-time-with-pause loop, a stakeholder/public-opinion backlash system, an influence/integrity ("dirty options") layer, and visible reactive externalities — adapted to the carbon/ETS domain.
**Status:** Draft for Review

---

## Executive Summary

CarbonSim already has the bones of a tycoon — an extensible decision engine, a time-based phase clock (currently used only by multiplayer), an event-card system, and a reactive isometric city — so the target is reachable by *extending* rather than rebuilding. But the **thesis** of the McDonald's Video Game is *structural futility* — the system is rigged so you can't win cleanly — and the carbon analog must be the **spine** of this game: a carbon market **cannot solve climate change on its own**; it rewards paper compliance over real decarbonization, so a player can "win" while the planet keeps warming (markets are **necessary but insufficient**). The gap is therefore both this missing systemic core **and** the missing systems of consequence: no planetary-outcome/futility mechanic, no public-opinion backlash, no tempting "dirty options," no multi-sector supply chain, and discrete-turn (not real-time) solo. **3 CRITICAL gaps** (systemic insufficiency core; multi-sector supply chain; stakeholder backlash) and **2 HIGH** (influence layer; real-time-with-pause). Recommendation: establish the **futility core first**, then the consequence systems (backlash → influence layer) on the existing single-company engine, then the real-time loop, then the multi-sector restructure last.

---

## Current Capabilities (What We Have)

| Capability | Status | Key Surfaces |
|---|---|---|
| Extensible decision dispatch (activate_abatement, buy_offsets, auctions, trades) | Mature | `engine/engine.py:150` `apply_company_decision` |
| Time-based phase clock with deadlines (real-time machinery) | Working (MP only) | `engine/engine.py:633` `advance_state`, `_set_phase` (`phase_deadline_at`), `engine/constants.py` durations |
| Pause / resume | Working | `engine/engine.py:501` `pause_session`, `:516` `resume_session` |
| Event-card system (draw, choices, effects) | Mature | `engine/cards.py`, `resolve_card`, `engine/data/*deck.json` |
| Penalties / compliance scoring | Mature | `engine/engine.py:1653` `_close_current_year`, `penalty_due` |
| Bots & competitive multiplayer | Mature | `engine/coop.py`, `server/routes/coop.py`, `server/ws.py` |
| Reactive isometric city (smog∝emissions, abatement cleans, compliance tint) | Working | `web/js/isocity.js` |
| Single-company control | Mature | `engine/solo.py`, `server/routes/game.py` |
| Audit log / event stream | Mature | `engine/engine.py` `_append_event`, `audit_log` |
| **Multi-sector supply chain** | **Missing** | — (one `company` with a flat `abatement_menu`) |
| **Stakeholder / public-opinion backlash** | **Missing** | — (only cash penalties) |
| **Influence / integrity "dirty options"** | **Missing** | — (offsets are uniform, no lobbying/PR) |
| **Real-time-with-pause solo loop** | **Missing** | — (solo is turn-based by design) |
| Satirical / procedural-rhetoric framing | Partial | neutral/educational per `AGENTS.md`; smog visual hints at it |

---

## Target State

> A carbon tycoon whose **core thesis is that the market alone cannot solve climate change.** The player manages an **interconnected supply chain** (e.g. generation → industry → market/HQ) under a **continuously ticking, pausable** clock; profit pressure tempts them toward **influence/integrity shortcuts** (lobbying, greenwashing, low-quality offsets) that work short-term but feed a **stakeholder backlash** system (regulators, communities, NGOs, investors) escalating **warning → protest → boycott/divestment**. Throughout, a **planetary climate trajectory keeps deteriorating largely regardless of the player's individual compliance**, and the UI makes the **divergence between "market success" and "real-world outcome"** legible — so that even a high-scoring player *feels* that paper compliance ≠ a solved climate. The **isometric city visibly reacts** to both progress and futility. This is the McDonald's Video Game's procedural rhetoric — structural insufficiency — in the carbon domain.

---

## Gap Analysis

### GAP-01: No multi-sector supply chain

**Severity:** CRITICAL — the defining structural feature of the target. The McD game's tension comes from decisions in one sector rippling to others; CarbonSim is a single flat firm.

**Current state:** A player is one `company` dict with a flat `abatement_menu` and scalar `projected_emissions` driven by `_projected_emissions` (`engine/engine.py:1747`). Scenarios (`engine/scenarios.py`) define company profiles, not interlinked sectors.

**What's needed:**
- A sector model (e.g. generation, industry, market/HQ) with per-sector state and **cross-sector coupling** (output/cost/emissions of one feeds the next).
- Per-sector decisions and a UI to switch between sector panels (mirrors McD's four panels).
- Emissions/cost/cash recomputation across the chain.

**Existing assets to reuse:**
- `apply_company_decision` dispatch (`engine/engine.py:150`) — add sector-scoped actions to the same pattern.
- `engine/scenarios.py` — extend scenario packs to declare sectors.
- `_recalculate_company_projection` / `_projected_emissions` — generalize to a sector pipeline.
- `web/js/isocity.js` plots — already render multiple "buildings"; can represent sectors.

**Effort estimate:** 1 large multi-phase plan (4–5 phases).

---

### GAP-02: No stakeholder / public-opinion backlash system

**Severity:** CRITICAL — the procedural-rhetoric payload. Today the only consequence is cash penalty; there is no escalating reputational pressure (the McD "detractors").

**Current state:** Consequences are limited to `penalty_due` at year close (`engine/engine.py:_close_current_year`). Event cards exist but are one-shot, not a persistent escalating state.

**What's needed:**
- A reputation/stakeholder model with named groups (regulators, communities, NGOs, investors) each holding an escalation level: **warning → protest → boycott/divestment**, with effects (cost, market access, cap tightening, cash-out).
- Triggers from emissions, integrity shortcuts (GAP-03), and missed compliance.
- Decay/recovery via genuine abatement or remediation spend.

**Existing assets to reuse:**
- Event/audit system (`_append_event`, `audit_log`) for surfacing escalations.
- `engine/cards.py` for narrative beats tied to escalation thresholds.
- `engine/achievements.py` threshold-evaluation pattern as a model for level transitions.

**Effort estimate:** 1 multi-phase plan (3–4 phases).

---

### GAP-03: No influence / integrity ("dirty options") layer

**Severity:** HIGH — the McD "special operations" (bribery, PR, greenwashing) are what make externalizing *tempting*; without them there's no moral tension.

**Current state:** Offsets are a single uniform action at one price (`buy_offsets`, `DEFAULT_OFFSET_PRICE`); no lobbying, PR, regulator capture, or offset-quality tiers.

**What's needed:**
- New decision actions: lobby (delay cap decline), greenwashing/PR (suppress backlash temporarily), buy **low-quality/high-risk offsets** (cheaper, but exposure risk), regulator capture (reduce penalties) — each **cheap short-term, risky long-term** via GAP-02.
- Integrity meter / exposure probability that converts shortcuts into backlash escalations.

**Existing assets to reuse:**
- `apply_company_decision` action dispatch — add actions alongside `submit_auction_bid`/`propose_trade` (`engine/engine.py:217-235`).
- Offset machinery (`buy_offsets`) — extend to quality tiers.
- Bot strategies (`engine/constants.py BOT_STRATEGIES`) — bots can also use shortcuts.

**Effort estimate:** 1 multi-phase plan (3 phases). Depends on GAP-02.

---

### GAP-04: No real-time-with-pause solo loop

**Severity:** HIGH — the target's "ongoing pressure" comes from a ticking, pausable clock; solo is now deliberately discrete-turn.

**Current state:** The engine *already* supports timed phase advancement (`advance_state` consuming `phase_deadline_at`, durations in `engine/constants.py`) and `pause_session`/`resume_session` — but solo (`server/routes/game.py`) nulls the deadline to stay turn-based, and only multiplayer uses the clock.

**What's needed:**
- A solo continuous-tick mode (server tick or client-driven `advance_state` calls) with **pause/resume** in the UI, replacing/augmenting the annual turn.
- Reconcile with the just-shipped turn-based solo (offer both, or make real-time the default with pause).

**Existing assets to reuse:**
- `advance_state`, `pause_session`, `resume_session` (engine) — already implemented.
- `server/ws.py` coop tick/broadcast loop — a template for a solo tick.
- `web/game.html` `doAdvanceYear`/`doFastForward` — evolve into play/pause controls.

**Effort estimate:** 1 multi-phase plan (3 phases).

---

### GAP-05: No systemic-insufficiency / planetary-outcome core (the "futility" thesis)

**Severity:** CRITICAL — this is the game's *thesis*, the carbon analog of the McDonald's game's structural futility. Without it the game implicitly says "the market solves it," the opposite of the intended message.

**Current state:** Outcomes are entirely **local to the player** — compliance gap, penalties, cash, and an end-of-game grade (`engine/engine.py:_close_current_year`, `engine/achievements.py`, `web/summary.html`). There is **no planetary/global state**: nothing represents cumulative global emissions, a temperature/“planet health” trajectory, or the divergence between *paper compliance* and *real decarbonization*. Winning the market currently implies winning for the climate — which is the message to subvert.

**What's needed:**
- A **planetary climate trajectory** (e.g. cumulative global emissions / warming index) that is largely **exogenous** — driven by the wider economy and other actors — so it keeps worsening even when the player is compliant; the player can *bend* it only marginally alone.
- A modeled distinction between **compliance** and **actual atmospheric impact** (offsets/trades reallocate a budget but don't shrink it fast enough; low-quality offsets count on paper but not in reality).
- **UI surfacing of the divergence**: market score "green" while the planet meter reddens; an endgame that lands the insufficiency — individual/market success against systemic failure, with collective/structural action (beyond one player's market moves) shown as the only thing that meaningfully moves the global needle.

**Existing assets to reuse:**
- `engine/engine.py` year-close pipeline (`_close_current_year`) and `audit_log` — add a global-state update each year.
- `web/summary.html` grade/standings screen — extend to contrast "your grade" vs "the planet's outcome."
- `web/js/isocity.js` sky/compliance tinting — already shifts with state; extend to reflect the planetary trajectory, not just local compliance.
- `engine/scenarios.py` — declare the exogenous global emissions path per scenario/difficulty.

**Effort estimate:** 1 multi-phase plan (3 phases). Threads through every other system, so define it early.

---

## Second-Tier Gaps

| Gap | Severity | Summary | Existing Assets |
|---|---|---|---|
| GAP-06: Visible reactive externalities for new systems | MEDIUM | Extend the iso city to show sectors, backlash (protesters/placards), and shortcut exposure — make the rhetoric legible | `web/js/isocity.js` (smog, sprites, triggers); `web/js/effects.js` |
| GAP-07: Procedural-rhetoric framing/tone | MEDIUM | Shift copy/feedback so the player *feels* the perverse incentive and the "necessary but insufficient" thesis; reconcile with `AGENTS.md` educational mission | tutorial/card copy (`engine/tutorial.py`, deck JSON) |
| GAP-08: Resource-chain dynamics (degradation/capacity analogs) | MEDIUM | McD land degradation → CarbonSim capacity/asset-aging so sectors can't be milked indefinitely | scenario/company fields in `engine/scenarios.py` |
| GAP-09: Balance & tuning for the new loop | MEDIUM | New actions + backlash + planetary path need playtest tuning | `engine/playtest.py` batch harness already exists |

---

## Recommended Sprint Sequencing

| Priority | Gap | Rationale |
|---|---|---|
| Sprint 1 | GAP-05 (systemic-insufficiency core) | The thesis/spine — establish the planetary trajectory and the market-vs-reality divergence first, so every later system plugs into it and the "futility" message is structural, not bolted on. |
| Sprint 2 | GAP-02 (stakeholder backlash) | Procedural-rhetoric consequence layer; reuses cards/events; hooks into the planetary state from Sprint 1. |
| Sprint 3 | GAP-03 (influence/integrity layer) | The "tempting shortcuts" that make backlash + insufficiency meaningful; new dispatch actions + exposure model. Depends on Sprint 2. |
| Sprint 4 | GAP-04 (real-time-with-pause loop) | Adds ongoing pressure; engine machinery already exists, so mostly wiring + UI. Independent of sectors. |
| Sprint 5 | GAP-01 (multi-sector supply chain) | Biggest, riskiest structural change — do it once the thesis + consequence/loop core are proven and stable. |
| Sprint 6 | GAP-06 + GAP-07 (+ GAP-08/09) | Make it *felt* and *legible*: reactive city, "necessary but insufficient" framing, resource dynamics, balance. |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Mission conflict: McD-style satire/"dirty options" vs. CarbonSim's educational ETS mandate (`AGENTS.md`, Vietnam-pilot grounding) | Product identity drift | H | Frame shortcuts as *teaching* externality economics (consequences always land); keep ETS rules accurate; get product sign-off before building shortcuts |
| "Futility" message misread as "ETS is pointless" / nihilistic / demotivating | Wrong takeaway; alienates pilot stakeholders | H | Frame as **"necessary but insufficient"**, not "useless": market success still matters but must pair with structural/collective action; show what *does* move the planetary needle. Validate the ending message with product/educators (Sprint 1). |
| Real-time loop collides with the just-shipped turn-based solo fix | Rework, player confusion | M | Make real-time an explicit mode/toggle; keep turn-based intact |
| Multi-sector rewrite destabilizes the engine + 116 tests | Regressions | M | Do GAP-01 last, behind the stable consequence core; expand `engine/playtest.py` coverage first |
| Scope explosion (4 big systems) | Never ships | H | Strict sprint gating; each sprint independently playable/valuable |
| Balance: shortcuts dominate or backlash feels arbitrary | Bad game feel | M | Tune via `engine/playtest.py` batch sims each sprint |

---

## Suggested Next Step

Review this report, then invoke `/plan` per sprint — start with **GAP-05 (systemic-insufficiency core)** since it is the thesis every other system plugs into, then **GAP-02 (stakeholder backlash)** and **GAP-03 (influence layer)**. Confirm both framing risks (the satire-vs-education tension and the "necessary but insufficient" vs. "ETS is pointless" reading) with product before building. Grounding research: `research/2026-06-14_mcdonalds-video-game-comparison.md`.
