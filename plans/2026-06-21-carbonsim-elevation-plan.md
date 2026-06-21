---
title: "CarbonSim Elevation: Tycoon-Grade Carbon Market Game"
date: "2026-06-21"
status: "draft"
request: "Elevate CarbonSim Online to Kairosoft/Sid Meier/tycoon sophistication level while deeply reflecting carbon market domain mechanics"
plan_type: "multi-phase"
research_inputs:
  - "research/2026-06-21_carbonsim-elevation-brainstorm.md"
  - "research/2026-06-21_management-sim-architecture.md"
  - "research/2026-06-20_sim-game-design-architecture-2.md"
---

# Plan: CarbonSim Elevation — Tycoon-Grade Carbon Market Game

## Objective

Transform CarbonSim Online from a functional carbon-compliance sim into a tight, replayable 20–40 min strategy game with Kairosoft-level mechanical depth and authentic carbon market texture. The architecture is already sound (OpenRCT2-class reducer + audit_log + snapshot); every sprint layers new mechanics onto that core without rewriting it. The goal after all five sprints: a session that creates "one more run" compulsion through escalating market tension, visible decision consequences, narrative event arcs, and persistent meta-progression.

## Context Snapshot

- **Current state:** 5 decision types (abatement toggle, spot offset buy, auction bid, bilateral trade); static scenario-fixed offset price; 3 bot strategy profiles (single-year threshold heuristics, no lookahead); 70 JSON cards with binary 2-choice one-shot effects; XP/level UI wired to nothing; city canvas is ambient decoration; no pre-commit consequence preview; scripted linear cap decline; win = survive all years.
- **Desired state:** Dynamic offset pricing that rises with demand; goal-driven AI agents with multi-year horizons; state-reactive cascading cards (story-generator model); full carbon instrument stack (spot, ETS auctions, OTC, forwards, VCM project investment); abatement as capex with payback arcs and financing; a city canvas that reflects compliance trajectory; a year-end narrative report screen; Kairosoft XP unlock tree (advanced techs, market tools, scenario skins); hard binary win/lose gate with star-rating replayability layer.
- **Key repo surfaces:**
  - `engine/engine.py` — reducer core, `apply_company_decision`, `_start_year`, `_close_current_year`, `run_bot_turns`, `apply_shock`
  - `engine/cards.py` + `engine/data/starter_deck.json` + `engine/data/expansion_deck.json` — card deck, `resolve_card`, prerequisite filtering
  - `engine/scenarios.py` — `SCENARIO_PACKS`, `SHOCK_CATALOG`, `allocation_factors`
  - `engine/constants.py` — bot strategy constants, phase durations
  - `engine/playtest.py` — seeded Monte-Carlo harness (already exists; extend, don't replace)
  - `engine/achievements.py` — 4 binary achievements (extend into unlock tree)
  - `engine/solo.py` — solo game creation (add seed threading here)
  - `server/db.py` — zlib-JSON state serialization (forward contracts + VCM credits must survive save/load)
  - `server/routes/game.py` — REST endpoints for solo decisions
  - `web/game.html` — UI panels, XP HUD (unimplemented), phase modals
  - `web/js/isocity.js` — city canvas renderer (add smog overlay + building tier logic)
  - `web/js/effects.js` — particle/juice layer (bind to new economic events)
  - `web/js/audio.js` — chiptune SFX (add market-event SFX hooks)
  - `web/css/style.css` — year-end report screen styling
- **Out of scope:** Real-time multiplayer / lockstep networking; LLM-generated card text; deep DNE regulatory fidelity; ECS refactor; mobile/native ports; online persistent leaderboards; carbon registry API integration.

## Research Inputs

- `research/2026-06-21_carbonsim-elevation-brainstorm.md` — 16 resolved decisions defining scope, mechanic choices, instrument stack, AI model, win condition, and 5-sprint delivery order.
- `research/2026-06-21_management-sim-architecture.md` — Exhaustive 224-source brief. Key findings applied: (1) OpenRCT2-twin architecture confirmation — reducer + audit_log + snapshot is correct, do not change it. (2) Dominant-strategy risk from static offset pricing — demand-responsive negative feedback loop (BazaarBot pattern) is the prescribed fix. (3) "Theme is not meaning" (Soren Johnson) — carbon mechanics must be the lesson, not flavor text. (4) Seeded playtest harness already exists in `playtest.py`; extend bot policies before adding new infrastructure. (5) Avoid ECS and lockstep — wrong scale and wrong loop type. (6) Sequence by leverage-per-effort: determinism → market feedback → AI agents → story cards → meta.
- `research/2026-06-20_sim-game-design-architecture-2.md` — Standard brief. Key applied: decision legibility (Sid's clarity rule) is the cheapest high-impact win; card-choice plumbing already exists, only the consequence-preview is missing.

## Assumptions and Constraints

- **ASM-001:** `project_outcome(state, action, payload) -> delta_dict` can be implemented as a pure function reusing existing compliance math in `engine.py` with no side effects. Must be validated when multi-instrument interactions are involved (e.g., forward contracts reducing spot demand in the same year).
- **ASM-002:** Forward contracts and VCM project credits are serialized as part of company state (list fields on the company dict) and survive the existing zlib-JSON save/load without schema migration tooling.
- **ASM-003:** Year-end narrative text is template-driven (Python f-string templates), not LLM-generated. Keeps the game deterministic, offline-capable, and maintenance-free.
- **ASM-004:** City tier upgrades (Sprint 4) use 2-tier sprite swap on existing `isocity.js` building sprites + a procedural smog overlay. No new hand-drawn art assets are required for an MVP pass; art can be upgraded independently later.
- **ASM-005:** The seeded Monte-Carlo harness in `playtest.py` is extended with varied bot policies (Sprint 3) before the dynamic offset price (Sprint 2) so that balancing sweeps are meaningful from the start.
- **CON-001:** Session target is 20–40 min solo. Every added mechanic must fit that budget. Validate median session length in `playtest.py` batch runs after each sprint.
- **CON-002:** No new Python dependencies beyond the existing FastAPI + stdlib stack. Dynamic pricing, capex math, and forward contract pricing are pure arithmetic.
- **CON-003:** Forward contract delivery and VCM credit generation are multi-year state; they must not break the existing `force_advance_phase` / `_start_year` hooks that `playtest.py` calls.
- **DEC-001:** Strategy game first — carbon mechanics are the medium, not the lesson. Fun is the primary design constraint.
- **DEC-002:** Hard binary win/lose gate — survive without bankruptcy AND achieve compliance in the final year. Star rating (0–5 stars based on penalty-free years + leaderboard rank vs. AI) layered on top for replayability.
- **DEC-003:** Vietnam-anchored narrative with jurisdiction-switchable skins (EU ETS Phase 4, California ARB). Plausible Vietnamese fiction, not DNE fidelity.

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Foundation: determinism + consequence preview + year-end ceremony | None | Seeded state, `project_outcome` fn, year-end report screen |
| PHASE-02 | Market: dynamic pricing + full instrument stack in UI | PHASE-01 | Demand-responsive offset price, forwards, VCM, OTC surfaced |
| PHASE-03 | AI: goal-driven agents + playtest dominance sweep | PHASE-01, PHASE-02 | Multi-year bot planning, varied strategies, win-rate report |
| PHASE-04 | Story: cascading cards + policy stability + city canvas | PHASE-01, PHASE-02 | State-reactive deck, `policy_stability` field, city tier upgrade |
| PHASE-05 | Meta: capex abatement + XP unlock tree + jurisdiction skins | PHASE-01–04 | Payback arcs, loan financing, persistent progression, skin system |

---

## Detailed Phases

### PHASE-01 — Foundation: Determinism, Consequence Preview, Year-End Ceremony

**Goal**

Wire a per-game seed through state (unlocking true replay and meaningful Monte-Carlo), add a pure `project_outcome` function so every decision surface can show its projected compliance and cash impact before the player commits, and build the year-end narrative report screen that creates Kairosoft-style ceremony around each year close.

**Tasks**

- [ ] TASK-01-01: Add `rng_seed: int` field to the game state dict in `engine/engine.py:create_initial_state`. Generate with `random.randint(0, 2**32)` at game creation time and persist in state.
- [ ] TASK-01-02: In `engine/solo.py:create_solo_game`, pass the seed through to `create_initial_state` and into `CardDeck(seed=state['rng_seed'])` so all card draws are reproducible.
- [ ] TASK-01-03: Verify `engine/playtest.py:run_playtest(seed)` already uses `CardDeck(seed=seed)` — if yes, annotate; if no, fix. Confirm two runs with identical seeds produce identical card draw sequences.
- [ ] TASK-01-04: Implement `engine/engine.py:project_outcome(state, company_id, action, payload) -> dict` — a pure, no-side-effect function that returns `{compliance_gap_delta, cash_delta, notes: [str]}`. Reuse the arithmetic from `_close_current_year` and `activate_abatement`. Cover all 5 existing action types plus forward contract and VCM stubs (can return `None` for unimplemented instruments; Sprint 2 fills them in).
- [ ] TASK-01-05: Expose `project_outcome` as `GET /api/game/{gameId}/project?action=...&payload=...` in `server/routes/game.py`. No auth change required; read-only endpoint.
- [ ] TASK-01-06: In `web/game.html`, wire the abatement measure list, offset buy input, and card choice buttons to call `project_outcome` on hover/focus and display a tooltip: `Compliance gap: ±X t CO₂ | Cash: ±$Y`. Use the existing tooltip CSS class.
- [ ] TASK-01-07: Build the year-end report screen in `web/game.html` as a modal that fires after `_close_current_year` returns. Content: year number, emissions vs. cap bar, penalties paid, cash delta, audit_log event count, a 2–3 sentence narrative string (see TASK-01-08), personal-best vs. prior run (stored in `localStorage`), and a "Start Year N+1" button.
- [ ] TASK-01-08: Add `generate_year_summary(state, year_result) -> str` in `engine/engine.py` — Python f-string templates keyed on outcome buckets (penalty-free / minor shortfall / severe shortfall / near-bankruptcy). Return the string in the `/api/game/{gameId}/advance` response JSON.
- [ ] TASK-01-09: Extend `run_playtest_batch` in `engine/playtest.py` to assert that two runs with the same seed produce identical `audit_log` entries. Fail the test if they diverge (regression guard for determinism).

**Files / Surfaces**

- `engine/engine.py` — add `rng_seed` to state, add `project_outcome`, add `generate_year_summary`
- `engine/solo.py` — thread seed through `create_solo_game`
- `engine/cards.py` — confirm `CardDeck(seed=...)` path
- `engine/playtest.py` — add determinism regression test
- `server/routes/game.py` — add `GET /project` endpoint
- `web/game.html` — wire consequence preview tooltips + year-end modal
- `web/css/style.css` — year-end report screen layout (new `.year-end-report` card class)

**Dependencies**

- None (this is the baseline sprint)

**Exit Criteria**

- [ ] Two solo game runs with the same seed produce byte-identical `audit_log` entries for all card draws (verified by the new `run_playtest_batch` assertion).
- [ ] `GET /api/game/{gameId}/project?action=buy_offsets&payload={"tonnes":100}` returns `{compliance_gap_delta, cash_delta}` without mutating state (run twice, compare `GET /api/game/{gameId}` state before and after).
- [ ] Year-end modal fires after each year closes in browser; displays narrative string, metrics, and "Start Year N+1" button.
- [ ] Consequence preview tooltip appears on abatement menu items and offset buy input in browser.

**Phase Risks**

- **RISK-01-01:** `project_outcome` must not mutate state. Use `copy.deepcopy(state)` internally and discard after calculation. Risk: performance on slow connections. Mitigation: deepcopy is cheap for ~8-company dicts; profile if >100ms.
- **RISK-01-02:** `localStorage` personal-best relies on `game_id` or player name as key. Risk: key collision across sessions. Mitigation: key on `scenario_id + player_name`; document the limitation.

---

### PHASE-02 — Market: Dynamic Offset Pricing + Full Instrument Stack

**Goal**

Replace the static scenario offset price with a demand-responsive pricing model (negative feedback loop that kills the dominant buy-offsets strategy), and surface all four carbon market instruments in the solo UI: ETS auctions (already in engine), OTC bilateral trades (already in engine backend, not in solo UI), forward contracts (new), and VCM project investment (new).

**Tasks**

- [ ] TASK-02-01: Add `offset_demand_this_year: float` accumulator to game state (reset in `_start_year`). Every `buy_offsets` action increments it by the tonnes purchased.
- [ ] TASK-02-02: In `engine/engine.py:buy_offsets` (inside `apply_company_decision`), compute `effective_offset_price` dynamically: `base_price * (1 + elasticity * (offset_demand_this_year / annual_offset_supply_cap))`. Add `offset_price_elasticity: float` (default `0.4`) and `annual_offset_supply_cap: float` (default `total_baseline_emissions * offset_usage_cap`) to `SCENARIO_PACKS` in `engine/scenarios.py`.
- [ ] TASK-02-03: Include `current_offset_price` in the snapshot so the frontend can display it as a live market ticker.
- [ ] TASK-02-04: Wire forward contracts: add `forward_contracts: list[{delivery_year, tonnes, locked_price, purchased_year}]` to company state. Add `buy_forward` action to `apply_company_decision`: deduct premium (`locked_price = current_offset_price * 1.15`), append to `forward_contracts`. In `_start_year`, resolve maturing contracts: add credits to `allowances` (or equivalent), log in `audit_log`.
- [ ] TASK-02-05: Wire VCM project investment: add `vcm_projects: list[{start_year, annual_credits, remaining_years, project_name}]` to company state. Add `invest_vcm` action: deduct `project_cost`, append a project with `annual_credits` and `remaining_years=3`. In `_start_year`, generate credits for all active projects (decrement `remaining_years`; remove when 0).
- [ ] TASK-02-06: Surface OTC bilateral trades in the solo game UI. Currently `propose_trade` and `respond_trade` exist in the engine but are only wired in the coop API. Add `POST /api/game/{gameId}/trade` (propose) and `POST /api/game/{gameId}/trade/{tradeId}/respond` to `server/routes/game.py`. Add a "Trade Market" panel to `web/game.html` listing open offers from AI companies with Accept/Counter buttons.
- [ ] TASK-02-07: Extend `project_outcome` (TASK-01-04) to cover `buy_forward` and `invest_vcm` with meaningful `compliance_gap_delta` projections (forward = reduces projected gap in delivery_year; VCM = reduces gap for next 3 years).
- [ ] TASK-02-08: Add a "Market" info panel to `web/game.html`: live offset price ticker (updates after each purchase), auction clearing price from last auction, 3 most recent OTC trades. Bind price change to a `effects.js` particle flash (green = price stable, yellow/red = rising).
- [ ] TASK-02-09: Run `playtest.py` batch after this sprint. Confirm no single instrument dominates (win rate variance across strategies < 30%). If offset-only still dominates, increase `offset_price_elasticity` until resolved.

**Files / Surfaces**

- `engine/engine.py` — `buy_offsets` (dynamic price), `_start_year` (contract resolution, VCM credit generation), `apply_company_decision` (new `buy_forward`, `invest_vcm` branches)
- `engine/scenarios.py` — add `offset_price_elasticity`, `annual_offset_supply_cap` to all `SCENARIO_PACKS`
- `server/routes/game.py` — add OTC trade endpoints for solo mode
- `web/game.html` — Market panel, OTC Trade panel, forward/VCM decision buttons
- `web/js/effects.js` — price-change particle flash
- `web/css/style.css` — Market panel styles

**Dependencies**

- PHASE-01 (seed-in-state for deterministic `playtest.py` validation; `project_outcome` for forward/VCM previews)

**Exit Criteria**

- [ ] Buying offsets in year 1 raises `current_offset_price` for subsequent purchases that same year (verified via `GET /api/game/{gameId}` after two sequential `buy_offsets` calls).
- [ ] A forward contract purchased in year 1 for delivery in year 2 generates credits in year 2's `_start_year` cycle (verify via `audit_log`).
- [ ] A VCM project generates credits in years 1, 2, and 3 after purchase; is absent from `vcm_projects` after year 3 (verify via `audit_log` across 3 years in `playtest.py`).
- [ ] `playtest.py` batch (8 runs, varied strategies) shows < 30% win rate variance across instrument strategies after elasticity tuning.
- [ ] OTC trade proposed by an AI company appears in the Trade Market panel in browser; player can Accept and state updates.

**Phase Risks**

- **RISK-02-01:** Forward contract price of `spot * 1.15` may be too cheap or too expensive depending on spot volatility. Mitigation: expose `forward_premium_rate` in `SCENARIO_PACKS`; tune in TASK-02-09.
- **RISK-02-02:** VCM credits accumulate in state for 3 years. If a save is loaded mid-project, `remaining_years` must count correctly. Mitigation: `remaining_years` is the source of truth; validate save/load round-trip in exit criteria.
- **RISK-02-03:** OTC trades between the player and AI companies require AI companies to proactively propose trades. This is addressed in PHASE-03 (bot trade logic). For PHASE-02, surface player-initiated OTC only; AI proposals are a PHASE-03 enhancement.

---

### PHASE-03 — AI: Goal-Driven Agents + Playtest Dominance Sweep

**Goal**

Replace the 3-profile single-year threshold bots with goal-driven agents that plan across a 2–3 year compliance horizon, use all four market instruments strategically, and propose bilateral OTC trades to the player. Extend `playtest.py` with varied bot policies and run a dominant-strategy sweep to validate game balance.

**Tasks**

- [ ] TASK-03-01: Define a `CompanyAgent` dataclass in `engine/agents.py` (new file): fields `company_id`, `sector`, `risk_appetite` (enum: conservative/moderate/aggressive/opportunistic), `horizon_years: int` (2 or 3), `cash_target_fraction: float`, `preferred_instruments: list[str]`.
- [ ] TASK-03-02: Implement `CompanyAgent.plan_year(state) -> list[Action]` — produces an ordered action list for the current decision window. Logic: (1) compute projected compliance gap over `horizon_years` using `project_outcome`; (2) rank abatement options by NPV over horizon (capex / annual_reduction / break_even_year — stub until PHASE-05 adds capex, use current cost/reduction ratio); (3) budget offsets vs. allowance banking vs. auction bids; (4) decide whether to propose an OTC trade based on surplus/deficit position.
- [ ] TASK-03-03: Replace `run_bot_turns` in `engine/engine.py` with a call to `CompanyAgent.plan_year` for each bot company. Preserve the existing `bot_strategy` field as the `risk_appetite` input so saved games are not broken.
- [ ] TASK-03-04: Add 2 new bot strategy profiles to `engine/constants.py`: `opportunistic` (exploits price dips; buys forwards when spot < scenario average; proposes aggressive OTC trades) and `speculator` (minimal abatement; banks allowances; sells OTC at a premium in year 3). Total: 5 strategy profiles.
- [ ] TASK-03-05: Add AI-initiated OTC trade proposals. In `CompanyAgent.plan_year`, if the agent has surplus allowances and the player's company has a projected shortfall (readable from state), append a `propose_trade` action targeting the player's company. Cap at 1 proposal per bot per year to avoid spam.
- [ ] TASK-03-06: Extend `engine/playtest.py`: add `run_strategy_sweep(seeds: list[int]) -> DataFrame-like dict` that runs one game per (seed × strategy combination), collects `{strategy, win_rate, mean_cash, mean_penalties, dominant_instrument}`, and prints a summary table. Flag any strategy with win rate > 60% as a dominant strategy requiring tuning.
- [ ] TASK-03-07: Run `run_strategy_sweep` with 20 seeds × 5 strategies (100 games). Adjust `offset_price_elasticity`, `penalty_rate`, or `forward_premium_rate` in `scenarios.py` until no strategy exceeds 60% win rate. Document the final constants.
- [ ] TASK-03-08: Add `GET /api/game/{gameId}/ai-signals` endpoint in `server/routes/game.py` that returns a JSON array of AI company postures (e.g., `{"company": "Vinacomin", "posture": "buying_offsets", "open_trades": 1}`). Display in UI as competitor intelligence (optional, but adds strategic texture).

**Files / Surfaces**

- `engine/agents.py` — new file; `CompanyAgent` class and `plan_year`
- `engine/engine.py` — replace `run_bot_turns` with `CompanyAgent.plan_year` dispatch
- `engine/constants.py` — 2 new strategy profiles
- `engine/playtest.py` — `run_strategy_sweep`
- `engine/scenarios.py` — balance constant tuning
- `server/routes/game.py` — `GET /ai-signals` (optional)
- `web/game.html` — competitor posture display (optional)

**Dependencies**

- PHASE-01 (`project_outcome` used by `CompanyAgent.plan_year`)
- PHASE-02 (dynamic offset price, forward/VCM instruments; bots must plan against dynamic prices)

**Exit Criteria**

- [ ] `run_strategy_sweep(seeds=range(20))` completes without error and produces a summary table.
- [ ] No strategy shows win rate > 60% in the sweep (rebalance constants until true).
- [ ] A playtest run includes at least 1 AI-initiated OTC trade proposal per 3-year game (verify via `audit_log`).
- [ ] A solo game in browser shows the player receiving an OTC trade proposal from an AI company in the Trade Market panel.
- [ ] Median session length from `run_playtest_batch` is ≤ 40 simulated minutes (verify via year-close timestamps in state).

**Phase Risks**

- **RISK-03-01:** `CompanyAgent.plan_year` calling `project_outcome` for each possible action may be slow if the action space is large. Mitigation: evaluate at most 10 candidate actions per agent per year; prune dominated options greedily.
- **RISK-03-02:** AI-proposed OTC trades may create an unfair advantage if bots can read the player's exact state. Mitigation: bots use their own projected state for trade decisions, not the player's actual cash balance.

---

### PHASE-04 — Story: Cascading Cards + Policy Stability + City Canvas

**Goal**

Replace the flat one-shot event card system with a state-reactive story-generator model: cards draw from live game state, can spawn follow-on cards, and can persist multi-turn conditions. Add a `policy_stability` field that makes the regulatory cap dynamic and unpredictable. Upgrade the city canvas to reflect compliance trajectory visually.

**Tasks**

- [ ] TASK-04-01: Add `policy_stability: float` (0–100, start 70) and `active_conditions: list[str]` to game state in `engine/engine.py`. `policy_stability` starts at 70 and changes each year: +5 if aggregate compliance rate > 80%; −10 if > 30% of companies paid penalties; −15 for `election_pressure` shock; +3 per year above 85% compliance.
- [ ] TASK-04-02: Replace scripted `allocation_factors` with a policy-stability-driven formula in `engine/scenarios.py` / `_start_year`: `cap_this_year = baseline_cap * (1 - base_decline_rate * (1 + (50 - policy_stability) / 200))`. When `policy_stability < 30`, draw a `regulatory_crackdown` card automatically. When `policy_stability > 85`, draw a `policy_relief` card.
- [ ] TASK-04-03: Extend the card JSON schema (`engine/data/starter_deck.json`, `engine/data/expansion_deck.json`) to support: `follow_on_cards: list[str]` (card_ids to inject into the draw pile when this card resolves with a specific choice), `sets_condition: str` (sets a flag in `active_conditions`), `requires_condition: str` (prerequisite gate), and `effect_duration: int` (apply effect for N years, not just 1). Update `resolve_card` in `engine/cards.py` to handle these fields.
- [ ] TASK-04-04: Update `CardDeck.draw_cards` in `engine/cards.py` to weight draw probability by game state: increase weight of `crisis` cards when `policy_stability < 40`; increase weight of `opportunity` cards when `policy_stability > 75`; filter `requires_condition` against `state['active_conditions']`.
- [ ] TASK-04-05: Author follow-on card chains for the 5 highest-weight cards in each category (20 cards total). Examples: `crisis/compliance_deadline_missed` → sets `condition: regulator_watching`; `policy/cbam_threat` with choice "lobby against" → spawns `policy/cbam_delayed` next year; `opportunity/tech_unlock` with choice "adopt" → spawns `opportunity/early_mover_bonus` in year+1. Add these as new cards in `expansion_deck.json` or extend existing cards.
- [ ] TASK-04-06: Add multi-turn effect tracking to game state: `active_effects: list[{effect_type, effect_params, remaining_years}]`. In `_start_year`, apply all active effects and decrement `remaining_years`; remove when 0. Wire `effect_duration` from card JSON to this list.
- [ ] TASK-04-07: Upgrade `web/js/isocity.js`: add a `smog_opacity` layer (CSS filter or canvas overlay) scaled by `compliance_gap / total_emissions`. Add building tier logic: for each building slot, if the corresponding company has `active_abatement` measures, draw the tier-2 sprite variant (can be a color-shifted or modified version of the existing sprite using canvas transforms — no new art files required for MVP). Trigger a "city clears" particle burst via `effects.js` when a penalty-free year closes.
- [ ] TASK-04-08: Add `policy_stability` and `active_conditions` to the snapshot payload so the frontend can display a "Policy Climate" indicator (stable/warning/crisis) in the header HUD.

**Files / Surfaces**

- `engine/engine.py` — `policy_stability` field, `active_conditions`, `active_effects`, `_start_year` (stability math + cap formula), `_close_current_year` (stability update)
- `engine/cards.py` — `resolve_card` (follow-on injection, condition setting, duration), `draw_cards` (state-weighted draw)
- `engine/data/starter_deck.json` + `engine/data/expansion_deck.json` — new fields + 20 follow-on cards
- `engine/scenarios.py` — remove scripted `allocation_factors`, replace with stability-driven formula
- `web/js/isocity.js` — smog overlay + building tier rendering
- `web/js/effects.js` — "city clears" burst
- `web/game.html` — Policy Climate indicator in header HUD

**Dependencies**

- PHASE-01 (seed-in-state so cascading card chains are reproducible for debugging and playtest validation)
- PHASE-02 (dynamic offset price interacts with `policy_stability`; a crackdown should also spike demand and raise prices)

**Exit Criteria**

- [ ] `run_playtest(seed=42)` with a missed compliance year shows `regulator_watching` in `active_conditions` in year+1 state.
- [ ] A `follow_on_cards` chain resolves correctly: parent card choice A injects child card into draw pile; child card is drawn within 2 years (verify via `audit_log` in `playtest.py`).
- [ ] `policy_stability` decreases after a high-penalty year and increases after a clean year (verify via state after `_close_current_year` in playtest).
- [ ] City canvas in browser shows smog overlay when compliance gap > 20%; overlay clears after a penalty-free year.
- [ ] No card draw raises a `KeyError` on the new schema fields (backward-compatibility: treat missing fields as their defaults).

**Phase Risks**

- **RISK-04-01:** Removing scripted `allocation_factors` breaks existing save games that were created before PHASE-04. Mitigation: add a migration guard in `_start_year` — if `policy_stability` is absent from state (legacy save), initialize it to 70 and use a scripted fallback for `allocation_factors`.
- **RISK-04-02:** Canvas transforms for building tier-2 without new assets may look low quality. Mitigation: hue-rotate + brightness filter on existing sprites is acceptable for Sprint 4 MVP; flag for art pass in Sprint 5 if budget allows.

---

### PHASE-05 — Meta: Capex Abatement + XP Unlock Tree + Jurisdiction Skins

**Goal**

Restructure abatement as a capex investment with payback arcs and loan financing (making decarbonisation decisions feel realistic), implement the XP unlock tree that creates persistent Kairosoft-style meta-progression, and add jurisdiction skin switching (EU ETS Phase 4, California ARB) to extend replayability.

**Tasks**

- [ ] TASK-05-01: Extend abatement measure schema in `engine/scenarios.py` with: `capex: float`, `annual_opex: float`, `asset_life_years: int`, `break_even_year: int` (computed), `tech_risk_pct: float` (chance of underperformance). Migrate all existing 3-sector abatement catalogs to use these fields.
- [ ] TASK-05-02: Restructure `activate_abatement` in `engine/engine.py`: instead of deducting full cost immediately, record the capex as a `pending_loan` or `cash_deduction` (player's choice — see TASK-05-03). Add `active_abatement_assets: list[{measure_id, installed_year, remaining_life, annual_reduction}]` to company state. In `_start_year`, apply annual reductions and deduct `annual_opex`.
- [ ] TASK-05-03: Add `finance_abatement` action to `apply_company_decision`: player can choose to pay `capex` in full now, or take a loan. Loan terms: `loan_amount = capex`, repaid in equal annual installments over `min(asset_life_years, scenario_loan_term)` years at `scenario_interest_rate` (add both to `SCENARIO_PACKS`). Add `active_loans: list[{principal, annual_payment, remaining_years}]` to company state; deduct `annual_payment` in `_start_year`.
- [ ] TASK-05-04: Add `tech_failure` card type: at `_start_year`, for each active abatement asset, roll against `tech_risk_pct` using the seeded RNG. If triggered, inject a `tech_failure_{measure_id}` card into the draw pile for that company (reduces `annual_reduction` by 50% for 1 year; player can choose to repair at cost or accept the hit).
- [ ] TASK-05-05: Implement XP engine in `engine/achievements.py` (extend existing file): `award_xp(state, event_type) -> int` per event (penalty-free year: +50 XP; first compliance: +100; OTC trade closed: +20; VCM project matured: +40; star rating multiplier at game end). Add `xp: int` and `xp_level: int` to game state; level thresholds at `[0, 200, 500, 1000, 2000, 4000]`.
- [ ] TASK-05-06: Define the unlock tree in `engine/data/unlock_tree.json` (new file): each node has `level_required`, `unlock_type` (one of: `abatement_tier`, `market_tool`, `scenario_skin`), and `unlock_id`. Examples: Level 2 → Tier-2 abatement (higher efficiency measures available); Level 3 → limit orders in auctions; Level 4 → forward contract term extended to 2 years; Level 5 → EU ETS skin unlocked; Level 6 → `speculator` AI difficulty.
- [ ] TASK-05-07: Store XP persistently in the player profile: add `POST /api/player/xp` endpoint (or extend the existing profile endpoint in `server/routes/`) that saves `{player_name, xp, unlocks}` to a new `player_profiles` SQLite table in `db.py`. Load on game start; pass `unlocked_features` into `create_initial_state`.
- [ ] TASK-05-08: Implement jurisdiction skins. Add `jurisdiction: str` field (default `vietnam`) to `SCENARIO_PACKS`. Create `engine/data/jurisdictions/eu_ets.json` and `engine/data/jurisdictions/california_arb.json` with: company names, sector labels, card flavor overrides, `penalty_rate`, `base_cap_decline_rate`, `offset_usage_cap`. In `create_initial_state`, merge the jurisdiction file over the base scenario constants.
- [ ] TASK-05-09: Wire the XP HUD in `web/game.html` (the level badge and XP bar already exist but are unimplemented): on each state refresh, read `state.xp` and `state.xp_level` and update the bar. Show unlock notifications as a toast when a new level is reached.
- [ ] TASK-05-10: Add an "Unlock Tree" screen accessible from the main menu (a modal in `web/index.html` or `web/game.html`): shows all nodes, grayed out if locked, highlighted if newly unlocked. Uses `unlock_tree.json` as its data source.
- [ ] TASK-05-11: Run final `run_strategy_sweep` (30 seeds × 5 strategies) across Vietnam + EU ETS scenarios. Confirm no dominant strategy, no jurisdiction-specific balance outliers.

**Files / Surfaces**

- `engine/engine.py` — `activate_abatement` restructure, `finance_abatement` action, `_start_year` (loan repayment, asset annual reductions, tech_failure roll), `award_xp` hooks
- `engine/scenarios.py` — abatement schema extension (`capex`, `annual_opex`, `asset_life_years`, `tech_risk_pct`), loan term constants
- `engine/achievements.py` — XP engine, `award_xp`, level thresholds
- `engine/data/unlock_tree.json` — new file; unlock tree definition
- `engine/data/jurisdictions/eu_ets.json` — new file
- `engine/data/jurisdictions/california_arb.json` — new file
- `server/db.py` — `player_profiles` table
- `server/routes/` — player XP persistence endpoint
- `web/game.html` — XP HUD wired, unlock toast, loan/capex UI in abatement panel
- `web/index.html` — unlock tree screen, jurisdiction selector on new game
- `web/css/style.css` — unlock tree modal, jurisdiction selector styles

**Dependencies**

- PHASE-01–04 (capex interacts with `project_outcome`, bot planning, card chains, and city canvas)

**Exit Criteria**

- [ ] Installing an abatement measure via loan creates entries in `active_loans` and deducts `annual_payment` in subsequent `_start_year` calls (verify via `audit_log` over 3 years in `playtest.py`).
- [ ] A tech_failure card is injected when the seeded RNG roll triggers it (verify by setting `tech_risk_pct=1.0` in a test scenario and confirming the card appears in `audit_log`).
- [ ] XP accumulates in state after a penalty-free year; `xp_level` increments at the correct threshold (verify via unit test against `award_xp`).
- [ ] Switching to EU ETS jurisdiction on the new game screen loads EU company names, sector labels, and EU-calibrated constants (verify via `GET /api/game/{gameId}` snapshot).
- [ ] XP HUD in browser shows correct level and bar fill based on `state.xp`.
- [ ] Final strategy sweep: no strategy > 60% win rate in either jurisdiction.

**Phase Risks**

- **RISK-05-01:** Capex restructure changes `activate_abatement` semantics. Existing saves with the old schema will have `active_abatement` lists but no `active_abatement_assets` or `active_loans`. Mitigation: migration guard in `_start_year` — if `active_abatement_assets` is absent, initialize from legacy `active_abatement` list with `remaining_life = asset_life_years` and no loan.
- **RISK-05-02:** `player_profiles` table adds persistent server state. Mitigation: scope to SQLite (same `mayor.db`); no new infrastructure. Player identified by name string (no auth); appropriate for a game context.
- **RISK-05-03:** Jurisdiction skin JSON files may diverge from base `SCENARIO_PACKS` schema over time. Mitigation: validate jurisdiction JSON against a pydantic schema on load; fail loudly if fields are missing.

---

## Verification Strategy

- **TEST-001:** `python -m pytest engine/tests/` — extend existing test suite with unit tests for `project_outcome`, `CompanyAgent.plan_year`, `award_xp`, loan repayment math, and jurisdiction JSON loading. Target: all existing tests still pass after each sprint.
- **TEST-002:** `python engine/playtest.py --batch --seeds 20` — run after every sprint. Assert: (a) no `KeyError` or `AssertionError` in any run; (b) median session ≤ 40 simulated minutes; (c) no single strategy > 60% win rate (from Sprint 3 onward).
- **TEST-003:** Determinism regression: `python engine/playtest.py --determinism-check --seed 42` — runs the same seed twice and diffs `audit_log`. Must produce zero diffs (from Sprint 1 onward, guarding every sprint).
- **MANUAL-001:** After each sprint, play a solo game in browser from start to completion. Verify: year-end screen fires, consequence previews appear, city canvas updates, XP bar increments. Record session length.
- **MANUAL-002:** After Sprint 2, manually test all four instrument types in browser: buy offsets (observe price rise), submit auction bid, propose OTC trade to AI, buy a forward contract, invest in a VCM project. Verify state changes via `GET /api/game/{gameId}`.
- **MANUAL-003:** After Sprint 4, deliberately miss compliance in year 1. Verify: `regulator_watching` condition appears; a follow-on regulator card is drawn in year 2; city smog overlay increases.
- **OBS-001:** After Sprint 5, run the full strategy sweep (`run_strategy_sweep(seeds=range(30))`). Print the win-rate table. If any strategy > 60%, tune `offset_price_elasticity` or `penalty_rate` and re-run before marking the sprint complete.

## Risks and Alternatives

- **RISK-001 (Cross-phase — state schema migration):** Each sprint adds new fields to the game state dict. Legacy saves loaded mid-development will be missing those fields. Mitigation: add initialization guards at the top of `_start_year` for each new field (`state.setdefault('policy_stability', 70)` etc.). Document the migration guards as a section in `engine/engine.py` comments.
- **RISK-002 (Session length creep):** Adding 4 new instruments, capex decisions, and card chains could push the median session above 40 min. Mitigation: measure after every sprint in `playtest.py`; if > 40 min, reduce decision window timer or simplify one instrument (VCM is the most cuttable).
- **RISK-003 (Balance instability across sprints):** Balance constants tuned in Sprint 2 may break when AI agents (Sprint 3) or cascading cards (Sprint 4) are added. Mitigation: run `run_playtest_batch` after every sprint, not just the final sweep; re-tune constants whenever win rate variance spikes.
- **ALT-001: BazaarBot full agent market** — A multi-agent market engine where all companies post asks/bids and price clears autonomously. Rejected: adds significant complexity without proportional gameplay improvement at 8 companies. The demand-accumulator model (TASK-02-02) achieves the same negative feedback loop with < 20 lines of code.
- **ALT-002: LLM-generated year-end narrative** — Generative text per run. Rejected for now: introduces an API dependency and non-determinism. Template-driven text (TASK-01-08) covers the 80% case; LLM is a future enhancement.
- **ALT-003: ECS (Entity-Component-System) engine refactor** — Rejected conclusively by research evidence. ECS pays off at thousands of entities; CarbonSim has ~8 companies. The existing Python reducer is correct and maintainable at this scale.

## Grill Me

1. **Q-001: City canvas art for tier-2 buildings (Sprint 4)**
   - **Recommended default:** Use canvas `hue-rotate` + `brightness` CSS filter on existing building sprites to create tier-2 variants. No new art assets required for MVP.
   - **Why this matters:** If new hand-drawn sprites are available or commissioned, Sprint 4 is much more visually impactful. If not, the filter approach is functional but visually modest.
   - **If answered differently:** If new sprites are provided, update TASK-04-07 to load them from a `sprites/tier2/` directory in `web/assets/`.

2. **Q-002: Forward contract pricing — is spot × 1.15 the right premium?**
   - **Recommended default:** `1.15` — forwards cost 15% more than spot, making them useful when spot price volatility (from DEC-003 demand response) is expected to exceed 15%.
   - **Why this matters:** If the premium is too low, forwards dominate (everyone locks in early). If too high, they're never used.
   - **If answered differently:** Expose `forward_premium_rate` in `SCENARIO_PACKS` and tune per-scenario in the Sprint 2 balance sweep (TASK-02-09).

3. **Q-003: XP persistence — is player identification by name string sufficient, or do we need a login/profile system?**
   - **Recommended default:** Name string as key, stored in `player_profiles` SQLite table. Sufficient for a game context without authentication.
   - **Why this matters:** A real profile/auth system is a significant scope expansion. Name-keyed persistence is simple but allows name collisions on shared servers.
   - **If answered differently:** Add a UUID player token stored in `localStorage` and passed in API headers; server maps UUID to profile row.

## Suggested Next Step

Review the Grill Me questions above, update this plan if needed, then begin implementation starting with PHASE-01. Each sprint should end with a `git commit` and a `playtest.py` batch run before the next sprint begins.
