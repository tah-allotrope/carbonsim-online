# CarbonSim Online — Vietnam Market Testing Plan

**Version:** 1.0  
**Date:** 2026-04-26  
**Repo:** `carbonsim-online` — `platform/carbonsim_phase12/`  
**Test runner:** `cd platform && ../.venv/Scripts/python.exe -m unittest tests.test_engine tests.test_deployment -v`  
**Audience:** Developers, analysts, and facilitators who need to verify that the simulator is functionally correct and Vietnam-policy-grounded before a live workshop.

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [How to Run the Existing Test Suite](#2-how-to-run-the-existing-test-suite)
3. [Codebase Quick Reference](#3-codebase-quick-reference)
4. [SECTION A — Functional Testing](#section-a--functional-testing)
   - [A1 — Compliance Engine](#a1--compliance-engine)
   - [A2 — Auction System](#a2--auction-system)
   - [A3 — Trading System](#a3--trading-system)
   - [A4 — Facilitator Controls](#a4--facilitator-controls)
   - [A5 — Scenario Packs and Bots](#a5--scenario-packs-and-bots)
   - [A6 — Shock Events](#a6--shock-events)
   - [A7 — Exports, Replay, and Analytics](#a7--exports-replay-and-analytics)
   - [A8 — Integration: Full 3-Year Simulation](#a8--integration-full-3-year-simulation)
5. [SECTION B — Vietnam Market Alignment](#section-b--vietnam-market-alignment)
   - [B1 — Covered Sectors](#b1--covered-sectors)
   - [B2 — Emissions Baselines and Growth Rates](#b2--emissions-baselines-and-growth-rates)
   - [B3 — Allocation Factors and Methodology](#b3--allocation-factors-and-methodology)
   - [B4 — Penalty Rate](#b4--penalty-rate)
   - [B5 — Auction Price Floor and Ceiling](#b5--auction-price-floor-and-ceiling)
   - [B6 — Offset Usage Cap](#b6--offset-usage-cap)
   - [B7 — Trading Mechanics](#b7--trading-mechanics)
   - [B8 — Abatement Catalog Alignment](#b8--abatement-catalog-alignment)
   - [B9 — Parameter Alignment Matrix](#b9--parameter-alignment-matrix)
6. [SECTION C — Policy and Regulatory Alignment](#section-c--policy-and-regulatory-alignment)
   - [C1 — Legal Basis and Institutional Roles](#c1--legal-basis-and-institutional-roles)
   - [C2 — Compliance Framework Rules](#c2--compliance-framework-rules)
   - [C3 — Market Oversight and Stabilisation](#c3--market-oversight-and-stabilisation)
   - [C4 — MRV and Registry Gaps](#c4--mrv-and-registry-gaps)
7. [SECTION D — Workshop Flow Testing](#section-d--workshop-flow-testing)
8. [SECTION E — Deployment and Operational Testing](#section-e--deployment-and-operational-testing)
9. [Known Gaps Catalogue](#known-gaps-catalogue)
10. [Data Sources for Validation](#data-sources-for-validation)
11. [Open Design Decisions](#open-design-decisions)

---

## 1. Purpose and Scope

This document is the primary testing reference for `carbonsim-online`. It covers three concerns:

**Functional correctness** — every engine formula, state transition, auction clearing rule, trade settlement path, and facilitator control produces the output documented in the codebase.

**Vietnam market alignment** — every hardcoded number and rule in the `vietnam_pilot` scenario pack (`engine.py` lines 31–120) is grounded in, or a documented simplification of, Vietnam's current ETS regulatory and research evidence.

**Policy alignment** — the simulator's overall design (free allocation, cap tightening, offset limits, penalty structure, banking, no-borrowing) is consistent with the Vietnamese ETS legal framework (Decree 06/2022 as amended by Decree 119/2025, PM Decision 232/QD-TTg 2025, PM Decision 13/2024).

**Out of scope:** UI pixel-level testing, production security penetration testing, performance load testing beyond 20 participants, continuous order-book features (not built in V1), accessibility (WCAG) compliance.

---

## 2. How to Run the Existing Test Suite

The repo ships with 92 passing tests across two files. All new test cases in this plan should follow the same pattern.

```bash
# From the repo root
cd platform

# Run all tests
../.venv/Scripts/python.exe -m unittest tests.test_engine tests.test_deployment -v

# Run a single test class
../.venv/Scripts/python.exe -m unittest tests.test_engine.TestComplianceEngine -v

# Run a single test method
../.venv/Scripts/python.exe -m unittest tests.test_engine.TestComplianceEngine.test_year_end_penalty -v
```

**Baseline gate:** All 92 existing tests must pass before any other testing proceeds. If any fail, treat as a blocking regression.

---

## 3. Codebase Quick Reference

| File | Lines | What it contains |
|---|---|---|
| `platform/carbonsim_phase12/engine.py` | ~2,265 | All ETS logic: `SCENARIO_PACKS`, allocation, compliance, auctions, trades, bots, shocks, analytics |
| `platform/carbonsim_phase12/__init__.py` | ~300+ | oTree app, `live_method` handlers, page classes |
| `platform/carbonsim_phase12/deployment.py` | ~99 | Health checks, reconnect, role-based access |
| `platform/tests/test_engine.py` | ~1,207 | 62 engine unit/scenario tests |
| `platform/tests/test_deployment.py` | ~276 | 24 deployment and integration tests |
| `platform/settings.py` | ~96 | Session configs, room configs |
| `FACILITATOR_RUNBOOK.md` | ~400+ | Operator guide — update with gap notes from this plan |

**Key constants in `engine.py` (Vietnam Pilot scenario, lines 31–120):**

```
penalty_rate          = 200.0       VND per allowance shortfall
offset_usage_cap      = 0.10        10% of emissions
auction_count_per_year = 2
auction_price_floor   = 80.0
auction_price_ceiling = 300.0
auction_share_of_cap  = 0.12        12% of annual cap auctioned
allocation_factors    = {1: 0.92, 2: 0.88, 3: 0.84}

thermal_power:  baseline=120, growth_rate=0.030
steel:          baseline= 95, growth_rate=0.022
cement:         baseline= 88, growth_rate=0.018
```

---

## SECTION A — Functional Testing

### A1 — Compliance Engine

#### TEST-A1-01 Existing suite baseline
**What:** Run all 92 existing tests.  
**Command:** `../.venv/Scripts/python.exe -m unittest tests.test_engine tests.test_deployment -v`  
**Acceptance:** 0 failures, 0 errors.

---

#### TEST-A1-02 Emissions growth formula
**Formula:** `projected_emissions = baseline × (1 + growth_rate) ^ year`

**Expected values (Vietnam Pilot):**

| Sector | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| thermal_power (120, 3.0%) | 123.60 | 127.31 | 131.12 |
| steel (95, 2.2%) | 97.09 | 99.22 | 101.40 |
| cement (88, 1.8%) | 89.58 | 91.20 | 92.84 |

**How to test:**
```python
from carbonsim_phase12.engine import _compute_projected_emissions
assert round(_compute_projected_emissions(120.0, 0.030, 1), 2) == 123.60
assert round(_compute_projected_emissions(120.0, 0.030, 2), 2) == 127.31
assert round(_compute_projected_emissions(120.0, 0.030, 3), 2) == 131.12
assert round(_compute_projected_emissions(95.0, 0.022, 1), 2) == 97.09
assert round(_compute_projected_emissions(88.0, 0.018, 1), 2) == 89.58
```
**Acceptance:** All assertions pass to 2 decimal places.

---

#### TEST-A1-03 Year-start allocation
**Formula:** `allocation = projected_emissions × allocation_factor[year]`  
**Then:** `allowances = banked_allowances + allocation` (year 1: banked = 0)

**Expected year-1 allocations (Vietnam Pilot):**

| Sector | Projected Y1 | Factor | Allocation |
|---|---|---|---|
| thermal_power | 123.60 | 0.92 | 113.71 |
| steel | 97.09 | 0.92 | 89.32 |
| cement | 89.58 | 0.92 | 82.41 |

**Acceptance:** `start_year(state, year=1)` sets each company's `allowances` to these values (±0.01 rounding).

---

#### TEST-A1-04 Year-end compliance — shortfall and penalty
**Setup:**
```python
projected_emissions = 110
allowances          = 100
offset_holdings     = 5
offset_usage_cap    = 0.10
penalty_rate        = 200
```
**Expected calculation:**
```
max_offset_use = 110 × 0.10 = 11.0
offsets_used   = min(5, 11.0) = 5
net_requirement = 110 - 5 = 105
shortfall       = max(0, 105 - 100) = 5
penalty         = 5 × 200 = 1000
banked_surplus  = 0
```
**Acceptance:** `process_year_end()` returns exactly these values; company cash decreases by 1000; cumulative_penalties increases by 1000; offset_holdings decreases by 5.

---

#### TEST-A1-05 Year-end compliance — surplus and banking
**Setup:**
```python
projected_emissions = 100
allowances          = 120
offset_holdings     = 0
```
**Expected:**
```
shortfall = 0
penalty   = 0
surplus   = 20
banked_allowances = 20
```
**Acceptance:** After year-end, `banked_allowances = 20`. After `start_year(state, year=2)`, opening allowances = new_allocation + 20.

---

#### TEST-A1-06 Three-year banking accumulation
**Setup:** Company consistently over-allocated (surplus each year). No trades, no offsets.  
**Expected:** banked_allowances compounds across years; year 3 opening allowances = year-3 allocation + accumulated bank.  
**Acceptance:** `year_results[2]["banked_allowances"]` > `year_results[1]["banked_allowances"]` > 0.

---

#### TEST-A1-07 No-borrowing constraint
**What:** Verify the engine provides no mechanism to use future-year allocations for current-year compliance.  
**How:** Attempt to create state where year-1 compliance draws on allowances that haven't been allocated yet.  
**Acceptance:** No function in `engine.py` accepts a year parameter that allows forward-drawing. `process_year_end()` only counts allowances in the current `company["allowances"]` field — there is no "borrow from next year" path. Confirm by code inspection of `process_year_end` and by confirming no test sets future-year allowances before they are allocated.

---

#### TEST-A1-08 Immediate vs. next-year abatement activation timing

**Immediate (e.g., `tp_heat_rate_upgrade`):**
- Activate in year 1 → `projected_emissions` reduced in year 1.

**Next-year (e.g., `tp_cofiring_preparation`):**
- Activate in year 1 → pending; `start_year(year=2)` promotes to active → `projected_emissions` reduced from year 2 onward.

```python
state = create_initial_state(num_participants=1, scenario="vietnam_pilot")
start_simulation(state)
co = state["companies"][0]  # thermal_power

# Activate immediate measure
activate_abatement(state, co["company_id"], "tp_heat_rate_upgrade")
# projected_emissions must drop immediately
assert co["projected_emissions"] < 123.60

# Activate next-year measure
activate_abatement(state, co["company_id"], "tp_cofiring_preparation")
# Still not reduced yet — reduction pending
pe_before = co["projected_emissions"]
start_year(state, year=2)
# Now activated
assert co["projected_emissions"] < pe_before
```
**Acceptance:** Both timing paths work correctly.

---

#### TEST-A1-09 Abatement cost deducted from cash
**Setup:** Company cash = 1,000,000. Activate `tp_heat_rate_upgrade` (cost = 90,000).  
**Expected:** cash = 910,000 after activation.  
**Acceptance:** Company cash decreases by exact abatement cost; double-activation of the same measure is rejected (or no-ops safely).

---

#### TEST-A1-10 Offset purchase and cap enforcement
**Setup:** projected_emissions = 100, offset_usage_cap = 0.10.  
**Purchase 15 offsets.**  
**At year-end:**
```
max_offset_use = 100 × 0.10 = 10
offsets_used   = min(15, 10) = 10
remaining      = 5  (unused, carry forward if modelled, or lost)
```
**Acceptance:** Year-end shows 10 offsets used; penalty calculated against (emissions - 10), not (emissions - 15); remaining offset_holdings updated correctly.

---

#### TEST-A1-11 Compliance gap live update
**What:** After each decision (abatement, offset purchase, auction win, trade settlement), the company's `compliance_gap` field must reflect the current net position.  
**Formula:** `compliance_gap = projected_emissions - allowances - offset_holdings`  
**Acceptance:** After each of the following, compliance_gap recomputes correctly:
1. `activate_abatement()` (projected_emissions decreases)
2. `purchase_offsets()` (offset_holdings increases)
3. `settle_auction()` (allowances increases)
4. `accept_trade()` as buyer (allowances increases)
5. `accept_trade()` as seller (allowances decreases)

---

### A2 — Auction System

#### TEST-A2-01 Auction scheduling
**Vietnam Pilot:** 2 auctions per year, `auction_share_of_cap = 0.12`.  
**Expected:** Each year, `schedule_auctions()` creates exactly 2 auction records. Total supply across both = 12% of that year's total cap. Each auction gets equal share; last gets remainder if odd.  
**Acceptance:** `len([a for a in state["auctions"] if a["year"] == 1]) == 2`; supply sums correctly.

---

#### TEST-A2-02 Uniform-price clearing — basic case

**Setup:** 3 bids, supply = 8 units.

| Bid | Price | Quantity |
|---|---|---|
| A | 100 | 5 |
| B | 80 | 5 |
| C | 60 | 5 |

**Expected:**
- Sort descending by price: A(100,5), B(80,5), C(60,5)
- Remaining supply: 8
- A: awarded=5, remaining=3
- B: awarded=3, remaining=0
- C: awarded=0
- **clearing_price = 80** (lowest accepted bid)
- A pays 5 × 80 = 400 (not 5 × 100)
- B pays 3 × 80 = 240

**Acceptance:** `clear_auction()` returns these exact values. All winners pay clearing_price, not their bid.

---

#### TEST-A2-03 Uniform-price clearing — oversubscription
**Setup:** 5 bids all at price=100, quantity=3 each, supply=10.  
**Expected:** All bids accepted (5×3=15 > 10); rationing by bid order; 2 bids get quantity=3, one gets quantity=2, remainder get 0 depending on tie-breaking.  
**Acceptance:** Total awarded = 10; clearing_price = 100.

---

#### TEST-A2-04 Bid price floor/ceiling validation
**Vietnam Pilot:** floor=80, ceiling=300.

| Bid price | Expected |
|---|---|
| 79 | Rejected — below floor |
| 80 | Accepted |
| 300 | Accepted |
| 301 | Rejected — above ceiling |

**Acceptance:** `submit_auction_bid()` raises `ValueError` for out-of-range prices.

---

#### TEST-A2-05 Bid cash validation
**Setup:** company cash = 500. Bid quantity=10, price=60 → total = 600 > 500.  
**Acceptance:** `submit_auction_bid()` raises `ValueError("insufficient cash")`.

---

#### TEST-A2-06 Empty auction (no bids)
**Setup:** Auction opened and closed with zero bids.  
**Acceptance:** `clear_auction()` sets clearing_price=0, awarded_quantity=0, status="cleared"; no company holdings change.

---

#### TEST-A2-07 Tie-breaking — same price, different submit times
**Setup:** Two bids at price=100 submitted 1ms apart, supply only allows one to be filled.  
**Acceptance:** Earlier bid wins; both pay clearing_price=100; later bid gets awarded=0.

---

#### TEST-A2-08 Auction settlement — holdings and compliance_gap update
**Setup:** Company wins 5 allowances at clearing_price=90, cash=5000.  
**Expected after settlement:** allowances += 5, cash -= 450 (5×90), compliance_gap recalculated.  
**Acceptance:** All three fields updated atomically.

---

### A3 — Trading System

#### TEST-A3-01 Trade proposal validation — seller holdings
**Setup:** seller.allowances = 3; propose trade for quantity=5.  
**Acceptance:** `propose_trade()` raises `ValueError("insufficient allowances")`.

---

#### TEST-A3-02 Trade proposal validation — buyer cash
**Setup:** buyer.cash = 400; propose trade quantity=5, price=100 (total=500 > 400).  
**Acceptance:** `propose_trade()` raises `ValueError("insufficient cash")`.

---

#### TEST-A3-03 Trade acceptance — correct settlement
**Setup:**
- Seller: allowances=10, cash=1000
- Buyer: cash=2000
- Trade: quantity=5, price=100

**Expected after acceptance:**
- seller: allowances=5, cash=1500 (+500)
- buyer: allowances=5, cash=1500 (-500)

**Acceptance:** Both compliance_gap fields recalculated; trade status="accepted"; audit log event appended.

---

#### TEST-A3-04 Trade acceptance re-validates holdings
**Setup:** Seller proposes trade for 5 allowances (has 10). Between proposal and acceptance, seller wins an auction and sells 8 allowances to someone else → seller now has 2.  
**Acceptance:** `accept_trade()` raises `ValueError` (seller no longer has 5); trade status set to a failure state; no settlement occurs.

---

#### TEST-A3-05 Trade rejection
**What:** Buyer explicitly rejects a pending trade.  
**Acceptance:** Trade status="rejected"; no allowances or cash transferred; audit log event appended.

---

#### TEST-A3-06 Trade expiry timer
**Setup:** `trade_expiry_seconds = 20`; create trade proposal; advance mock clock by 21 seconds.  
**Acceptance:** `respond_to_trade()` or `advance_state()` triggers expiry; status="expired"; no settlement; audit log event appended.

---

#### TEST-A3-07 Trade feed visibility
**What:** All accepted, rejected, and expired trades are visible in the trade feed (not filtered per-company in the audit log).  
**Acceptance:** `export_session_data()` returns all trades regardless of status in the `trades` array.

---

### A4 — Facilitator Controls

#### TEST-A4-01 Phase state machine — all transitions
**Expected transition sequence:**

```
PHASE_LOBBY
  → PHASE_YEAR_START       (start_simulation)
  → PHASE_DECISION_WINDOW  (advance_state / deadline)
  → PHASE_COMPLIANCE       (advance_state / deadline)
  → PHASE_YEAR_START       (year 2, if year < num_years)
  → PHASE_DECISION_WINDOW
  → PHASE_COMPLIANCE
  → PHASE_YEAR_START       (year 3)
  → PHASE_DECISION_WINDOW
  → PHASE_COMPLIANCE
  → PHASE_COMPLETE
```

**Acceptance:** `force_advance_phase()` produces the correct next phase for each input. Calling it from PHASE_COMPLETE is a no-op or raises gracefully.

---

#### TEST-A4-02 Pause and resume deadline extension
**Setup:** deadline = T+600s. Pause at T+100s. Resume at T+200s (pause duration = 100s).  
**Expected:** new deadline = T+700s (original + pause_duration).  
**Acceptance:** `resume_session()` sets deadline = original_deadline + (resume_time - pause_time); phase restored to phase_before_pause.

---

#### TEST-A4-03 Cannot pause from invalid phases
**What:** Pause should only work from PHASE_YEAR_START, PHASE_DECISION_WINDOW, PHASE_COMPLIANCE.  
**Acceptance:** Attempting to pause from PHASE_LOBBY or PHASE_COMPLETE raises or returns an error; state unchanged.

---

#### TEST-A4-04 Participant status tracking
**What:** `last_seen`, `last_action`, `decision_count_this_year` update on each decision.  
**Acceptance:** After a participant activates abatement, their `last_action` timestamp advances; `decision_count_this_year` increments. At `start_year()`, `decision_count_this_year` resets to 0.

---

#### TEST-A4-05 Role-based action gating
**What:** Only the facilitator can trigger auctions, trigger shocks, pause/resume, force-advance, and export.  
**Acceptance:** Attempting these actions with a non-facilitator company_id raises `PermissionError` or equivalent; state unchanged.

---

### A5 — Scenario Packs and Bots

#### TEST-A5-01 All scenario packs load correctly

| Scenario | allocation_factors | penalty_rate | offset_usage_cap | floor | ceiling |
|---|---|---|---|---|---|
| vietnam_pilot | 0.92/0.88/0.84 | 200 | 0.10 | 80 | 300 |
| high_pressure | 0.90/0.82/0.74 | 350 | 0.05 | 100 | 400 |
| generous | 0.95/0.92/0.89 | 120 | 0.15 | 50 | 250 |

**Command:**
```python
for scenario in ["vietnam_pilot", "high_pressure", "generous"]:
    state = create_initial_state(num_participants=3, scenario=scenario)
    assert state["allocation_factors"] == expected[scenario]
    assert state["penalty_rate"] == expected_penalty[scenario]
```
**Acceptance:** All values match the table.

---

#### TEST-A5-02 Bot conservative strategy — no trading
**Setup:** Conservative bot; run `run_bot_turns()` across a full decision window.  
**Acceptance:** Conservative bot submits zero trade proposals (`trade_likelihood = 0.0`); it does activate cheap abatements and may bid in auctions.

---

#### TEST-A5-03 Bot moderate strategy — partial abatement and trading
**Setup:** Moderate bot; run `run_bot_turns()`.  
**Acceptance:** Moderate bot activates all abatements below its `abatement_threshold_fraction × compliance_gap`; it bids in auctions; it occasionally proposes trades.

---

#### TEST-A5-04 Bot aggressive strategy — full abatement and active trading
**Setup:** Aggressive bot.  
**Acceptance:** Aggressive bot activates all available abatements; bids the maximum quantity it can afford; proposes trades at a `trade_likelihood = 0.5` rate.

---

#### TEST-A5-05 Mixed human/bot session coherence
**Setup:** 2 humans + 4 bots; run full 3-year simulation.  
**Acceptance:** No exceptions raised; all 6 companies complete 3 `year_results` entries; audit log contains events for all participants.

---

### A6 — Shock Events

#### TEST-A6-01 emissions_spike
**Setup:** magnitude=0.10; company projected_emissions = 100.  
**Expected:** projected_emissions = 100 × (1 + 0.10) = 110 for all companies.  
**Acceptance:** All companies updated; audit log event appended with `shock_type="emissions_spike"`.

---

#### TEST-A6-02 allowance_withdrawal
**Setup:** magnitude=0.20; company allowances = 100.  
**Expected:** allowances = 100 - (100 × 0.20) = 80.  
**Acceptance:** compliance_gap recalculated after deduction.

---

#### TEST-A6-03 cost_shock
**Setup:** magnitude=0.15; company cash = 1,000,000.  
**Expected:** cash = 1,000,000 - (1,000,000 × 0.15) = 850,000.  
**Acceptance:** All companies updated.

---

#### TEST-A6-04 offset_supply_change
**Setup:** current offset_usage_cap=0.10; magnitude=0.50.  
**Expected:** offset_usage_cap = 0.10 × 1.50 = 0.15.  
**Acceptance:** State-level cap updated; per-company max_offset_use recalculated.

---

#### TEST-A6-05 Shock during PHASE_COMPLIANCE (edge)
**What:** Trigger a shock when the session is in PHASE_COMPLIANCE (year-end).  
**Acceptance:** Shock applies cleanly; compliance processing that follows uses the updated values.

---

### A7 — Exports, Replay, and Analytics

#### TEST-A7-01 Export structure completeness
**After a 3-year session, `export_session_data()` must include:**

```json
{
  "session_metadata": { "scenario", "num_years", "created_at", ... },
  "companies": [
    {
      "company_name", "sector", "cash", "banked_allowances",
      "cumulative_penalties", "abatement_ids_activated",
      "year_results": [
        { "year", "allocation", "projected_emissions", "offsets_used",
          "banked", "shortfall", "penalty" }
      ]
    }
  ],
  "auctions": [
    { "year", "auction_id", "status", "supply", "clearing_price",
      "bids": [...], "results": [...] }
  ],
  "trades": [
    { "trade_id", "seller_id", "buyer_id", "quantity", "price",
      "status", "created_at", "resolved_at" }
  ],
  "audit_log": [ { "event_type", "timestamp", "details" } ],
  "rankings": [ { "rank", "company_name", "cumulative_penalties", "cash" } ]
}
```

**Acceptance:** Parsed export passes a structural schema check; no required fields are null or missing.

---

#### TEST-A7-02 Rankings sort order
**What:** Rankings sorted by (cumulative_penalties ASC, penalty_due ASC, banked_allowances DESC, company_name ASC).  
**Setup:** Set up 3 companies with different penalty totals.  
**Acceptance:** `generate_rankings()` returns companies in correct order; rank 1 = lowest penalties.

---

#### TEST-A7-03 Replay timeline ordering
**What:** `generate_replay()` returns events in ascending timestamp order.  
**Acceptance:** All events in `replay["timeline"]` have non-decreasing timestamps; year markers appear at correct year boundaries.

---

#### TEST-A7-04 Analytics aggregation accuracy
**What:** Market metrics in `generate_analytics()` must be computable from raw company/auction/trade data.  
**Acceptance:**
- `total_auction_volume` = sum of all awarded quantities across all auctions
- `total_trade_volume` = sum of quantities of all accepted trades
- `avg_clearing_price` = weighted average of auction clearing prices by volume
- `total_penalties` = sum of all company `cumulative_penalties`
- Per-sector breakdowns sum to cross-sector totals

---

### A8 — Integration: Full 3-Year Simulation

#### TEST-A8-01 Bot-only full 3-year run
**Script:**
```python
from carbonsim_phase12.engine import (
    create_initial_state, start_simulation, start_year,
    process_year_end, run_bot_turns, force_advance_phase,
    schedule_auctions, clear_auction, export_session_data
)
import unittest

state = create_initial_state(num_participants=0, num_bots=6, scenario="vietnam_pilot")
start_simulation(state)

for year in range(1, 4):
    start_year(state, year)
    run_bot_turns(state)          # bots make decisions
    # clear auctions
    for auction in [a for a in state["auctions"] if a["year"] == year]:
        clear_auction(state, auction["auction_id"])
    process_year_end(state, year)

assert state["phase"] == "PHASE_COMPLETE"
assert all(len(c["year_results"]) == 3 for c in state["companies"])

export = export_session_data(state)
assert len(export["companies"]) == 6
assert len(export["audit_log"]) > 0
```
**Acceptance:** No exceptions; assertions pass; export parses cleanly.

---

#### TEST-A8-02 All three scenarios complete without error
**What:** Run TEST-A8-01 for each of `vietnam_pilot`, `high_pressure`, `generous`.  
**Acceptance:** All three complete; `high_pressure` companies have higher average penalties than `generous`; `generous` companies have higher average banked allowances.

---

#### TEST-A8-03 Determinism — same seed, same output
**What:** Given identical initial conditions and bot strategy seeds, two runs must produce identical audit logs.  
**Acceptance:** `export["audit_log"]` from run 1 equals `export["audit_log"]` from run 2 (same timestamps, same event sequences).

---

## SECTION B — Vietnam Market Alignment

This section validates every hardcoded number in the `vietnam_pilot` scenario against the research evidence in the `research/` directory. For each parameter the tester must record one of three verdicts:

- **CONFIRMED** — directly supported by a named research source
- **PLAUSIBLE** — consistent with research direction but not explicitly specified; acceptable as a workshop simplification
- **GAP** — departs from or contradicts policy; requires a facilitator note

---

### B1 — Covered Sectors

#### TEST-B1-01 Sector names match Vietnam ETS pilot coverage

**Check:** The three sectors in `SCENARIO_PACKS["vietnam_pilot"]["company_library"]` are `thermal_power`, `steel`, `cement`.

**Policy source:** Decree 119/2025/ND-CP; `research/20251128_CTX-Model-Impact-Assessment-Report_EN-1.md` (Executive Summary, p. vii): *"The CTX pilot will initially cover the thermal power, cement, and steel sectors."*

**Verdict: CONFIRMED**

**Note:** Three other sectors listed in Vietnam's broader ETS coverage (aviation, chemicals, paper) are not modelled. This is an **intentional scope limitation** — document in facilitator runbook: *"The simulator covers the three highest-emitting pilot sectors. Aviation, chemicals, and paper are in scope for later phases of Vietnam's ETS."*

---

#### TEST-B1-02 Company geographic names are Vietnam-contextually accurate

| Company | Location | Real-world basis |
|---|---|---|
| Red River Thermal | Red River delta, northern Vietnam | Major thermal power cluster (Quảng Ninh, Hải Dương, Ninh Bình coal plants) |
| Hai Phong Steel | Hải Phòng, northern Vietnam | Formosa + Hòa Phát steel presence; major industrial port city |
| Da Nang Cement | Đà Nẵng, central Vietnam | Hải Vân Cement, proximity to limestone deposits |

**Verdict: CONFIRMED** — all three reference real Vietnamese industrial geography.

---

### B2 — Emissions Baselines and Growth Rates

#### TEST-B2-01 Sector emissions ordering matches Vietnam reality

**Check:** thermal_power (120) > steel (95) > cement (88).

**Policy source:** Vietnam's GHG Inventory and sector MRV data consistently show thermal power as the largest emitter among these three pilot sectors.

**Verdict: CONFIRMED** (relative ordering).

**Note:** The absolute values (88–120 units) are dimensionless workshop-scale quantities, not megatonnes. No validation of absolute magnitude is possible or required.

---

#### TEST-B2-02 Growth rates vs. historical Vietnam sectoral data

**Simulator values vs. historical Vietnam ranges:**

| Sector | Simulator | Historical Vietnam range | Assessment |
|---|---|---|---|
| thermal_power | 3.0%/yr | 5–8%/yr (pre-2023) | **Conservative** |
| steel | 2.2%/yr | 4–6%/yr | **Conservative** |
| cement | 1.8%/yr | 2–4%/yr | **Low end of range** |

**Data sources to validate against:** IEA Southeast Asia Energy Outlook 2023; Vietnam NDC 2022 Update (sectoral BAU projections); VNEEC modeling reports in `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`.

**Verdict: PLAUSIBLE** — conservative rates are a deliberate workshop choice to avoid overwhelming first-time participants. The compliance pressure is still visible across three years without being extreme.

**Required facilitator note:** *"Growth rates in this simulator are conservative compared to Vietnam's historical sector trends (thermal power has grown ~5–8%/year historically). For advanced sessions, increase growth rates via the scenario config to create more acute compliance pressure."*

---

### B3 — Allocation Factors and Methodology

#### TEST-B3-01 Annual tightening schedule

**Simulator:** `{1: 0.92, 2: 0.88, 3: 0.84}` → 4 percentage-point annual decline.

**International comparison:**
- EU ETS Phase 4: 4.3% linear reduction factor per year (2024–2027)
- CarbonSim default: 3% annual cap decline
- Vietnam pilot: allocation tightening schedule **not yet publicly specified** in available research

**Verdict: PLAUSIBLE** — 4 pp/year is in line with international practice. Vietnam's actual schedule will be determined in subsequent technical guidance.

**Required facilitator note:** *"The 8% cumulative tightening across three years (92% → 88% → 84%) is a simulation parameter. Vietnam's actual 2025–2028 allocation schedule has not yet been publicly finalized."*

---

#### TEST-B3-02 Allocation method — grandfathering vs. benchmarking

**Simulator formula:** `allocation = projected_emissions × allocation_factor[year]`  
This is equivalent to **grandfathering** (allocating a % of historical/projected emissions to each company).

**Vietnam policy reality:** Decree 06/2022 specifies that the thermal power sector will eventually use **heat-rate benchmarks**; steel and cement may use product-output benchmarks. The actual method for 2025–2028 is still being defined.

**Verdict: PLAUSIBLE simplification** (grandfathering is the easiest to explain in a workshop).

**Required facilitator note:** *"Real Vietnamese ETS allocation uses sector-specific benchmarks (e.g., tCO₂ per MWh for power plants), not a flat % of your historical emissions. Companies that are more efficient than the benchmark receive a windfall; inefficient companies face a tighter gap."*

---

### B4 — Penalty Rate

#### TEST-B4-01 Penalty rate value

**Simulator:** 200 VND/allowance (vietnam_pilot), 350 (high_pressure), 120 (generous).

**Vietnam policy:** Decree 06/2022 and Decree 119/2025 establish ETS penalties; specific VND/tCO₂ rates are set in subordinate technical guidance not yet publicly finalized. No specific rate has been confirmed in the available research files.

**Verdict: PLAUSIBLE** — rate is chosen to be high enough to incentivize compliance in the simulation context.

---

#### TEST-B4-02 Penalty vs. auction ceiling — rational compliance check

**DESIGN ISSUE: In all three scenarios, `penalty_rate < auction_price_ceiling`.**

| Scenario | Penalty | Ceiling | Rational non-compliance possible? |
|---|---|---|---|
| vietnam_pilot | 200 | 300 | YES — pay 200 instead of buying at 200–300 |
| high_pressure | 350 | 400 | YES — pay 350 instead of buying at 350–400 |
| generous | 120 | 250 | YES — pay 120 instead of buying at 120–250 |

**ETS design principle:** The penalty must exceed the highest possible allowance price (the ceiling) to ensure compliance is always the rational choice. EU ETS (€100 penalty + make-good) and CarbonSim ($300 penalty = $300 ceiling) both follow this principle.

**Vietnam policy intent:** The research confirms penalties are designed to make compliance economically rational.

**Required action (one of two options):**
1. **Fix:** Raise `penalty_rate` in each scenario to `auction_price_ceiling + 1` (e.g., 301 for vietnam_pilot).
2. **Document:** If rational non-compliance is an intended teaching scenario, add an on-screen facilitator warning: *"In this scenario, paying the penalty may be cheaper than buying allowances at peak prices. Does this match Vietnam's policy intent?"*

**Test to write:**
```python
for scenario_name, pack in SCENARIO_PACKS.items():
    assert pack["penalty_rate"] > pack["auction_price_ceiling"], (
        f"Scenario '{scenario_name}': penalty ({pack['penalty_rate']}) must exceed "
        f"auction ceiling ({pack['auction_price_ceiling']}) to ensure rational compliance"
    )
```

---

### B5 — Auction Price Floor and Ceiling

#### TEST-B5-01 Price scale validation

**Simulator values:** floor=80, ceiling=300 (vietnam_pilot).

**Real-world context:** Vietnam's CTX pilot price stabilization mechanisms (price containment reserve, SAM) are under design. The impact assessment modeling report (`research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`) references compliance cost scenarios in USD ranges (~$5–50/tCO₂ = ~125,000–1,250,000 VND/tCO₂ at current rates).

**Conclusion:** The simulator's 80–300 range is **orders of magnitude below any realistic VND/tCO₂ price**. This is intentional — the numbers are dimensionless workshop-scale units.

**Required facilitator note:** *"All monetary values in this simulator are dimensionless 'simulation units', not real VND/tCO₂ prices. Vietnam's actual carbon price will be in the range of hundreds of thousands to millions of VND per tonne CO₂."*

**Verdict: PLAUSIBLE** (acknowledged simplification).

---

#### TEST-B5-02 Auction in pilot vs. real policy timeline

**KNOWN GAP (GAP-01):** The simulator includes auctions in the Vietnam Pilot scenario. Vietnam's 2025–2028 pilot uses free allocation only. Auctioning is planned post-2028 (PM Decision 232/QD-TTg, January 2025).

**Verdict: DELIBERATE PEDAGOGICAL DEPARTURE**

**Required facilitator note (must be in `FACILITATOR_RUNBOOK.md`):** *"This simulator includes government auctions to teach the mechanics of sealed-bid price discovery. In reality, Vietnam's 2025–2028 pilot phase operates with free allocation only. Auctioning is planned for the post-2028 full-operation phase under PM Decision 232/QD-TTg."*

---

### B6 — Offset Usage Cap

#### TEST-B6-01 10% cap vs. Vietnam policy and international benchmarks

**Simulator:** `offset_usage_cap = 0.10` (vietnam_pilot).

**International benchmarks:**
- California: 4–6%
- RGGI: 3.3%
- China: 5%
- CarbonSim spec default: 10%
- Vietnam policy: not yet publicly specified; research synthesis confirms "offset use limited to a defined share of annual compliance obligation"

**Verdict: PLAUSIBLE** — 10% is at the higher end of international practice but within a reasonable workshop range.

**Required facilitator note:** *"Vietnam's actual domestic carbon credit usage limit will be set in subordinate legislation. The 10% cap in this simulator is at the upper end of international practice; Vietnam may set a lower limit when final rules are published."*

---

#### TEST-B6-02 Single undifferentiated offset pool

**Simulator:** `offset_holdings` is a single integer — no distinction between credit types.

**Vietnam reality:** Vietnam's registry will distinguish allowances (VNUA) from domestic carbon credits (VNCCs). International offsets (VCS, Gold Standard) have a separate eligibility pathway. The CTX pilot initially focuses on allowances; credit integration is phased.

**Verdict: KNOWN SIMPLIFICATION (GAP-08)**

**Required facilitator note:** *"The simulator treats all offsets as a single interchangeable pool. Real markets distinguish allowances from domestic credits (VNCCs) and international offsets, each with different eligibility rules and quality tiers."*

---

### B7 — Trading Mechanics

#### TEST-B7-01 Bilateral trade model vs. Vietnam CTX design

**Simulator:** Seller proposes directly to buyer; immediate settlement on acceptance.

**Vietnam CTX proposal (from `research/20260213_Recommendation_20Report_EN.md`):**
- Negotiated transactions executed on HNX platform
- RTGS/DvP settlement (no CCP)
- Daily reconciliation to the National Registry System (NRS)
- Mandatory pre-trade validation
- SSC market surveillance oversight

**Assessment:** The simulator's direct bilateral model captures the core transaction logic. The HNX intermediation layer, NRS reconciliation, and SSC surveillance are not modelled.

**Verdict: PLAUSIBLE** — bilateral model is the correct pedagogical abstraction for the pilot-phase market design.

**Required facilitator note:** *"In the real CTX, every bilateral trade must be executed through the HNX platform and settled against the National Registry System before it is final. The simulator skips the intermediary and registry steps."*

---

### B8 — Abatement Catalog Alignment

#### TEST-B8-01 Thermal power measures — Vietnam relevance

| Measure | Cost/tonne | Type | Vietnam context |
|---|---|---|---|
| Heat-rate upgrade (10t, 90,000 VND) | 9,000/t | Efficiency | Primary near-term option for Vietnam's coal fleet; widely referenced in NDC and JETP Investment Plan |
| Biomass cofiring (7t, 65,000 VND) | 9,286/t | Fuel switch | Pilot programs at EVN thermal plants; JETP-supported; next-year delay is realistic (permitting, supply chain) |

**Verdict: CONFIRMED — both measures are Vietnam-relevant.**

---

#### TEST-B8-02 Steel measures — Vietnam relevance

| Measure | Cost/tonne | Type | Vietnam context |
|---|---|---|---|
| Waste heat recovery (8t, 72,000 VND) | 9,000/t | Efficiency | Standard for integrated mills (Formosa Hà Tĩnh-scale); immediate activation plausible |
| Scrap ratio optimization (5t, 50,000 VND) | 10,000/t | Process | EAF scrap use increasing as Vietnam's scrap supply grows; next-year delay realistic (supply contracts) |

**Verdict: CONFIRMED — both measures are Vietnam-relevant.**

---

#### TEST-B8-03 Cement measures — Vietnam relevance

| Measure | Cost/tonne | Type | Vietnam context |
|---|---|---|---|
| Blended clinker shift (6t, 46,000 VND) | 7,667/t | Process | Vietnam already uses blended cement widely; this is the most accessible and cost-effective measure |
| Kiln control upgrade (4t, 38,000 VND) | 9,500/t | Efficiency | Common in Vicem group plants; next-year delay realistic (installation and calibration) |

**Verdict: CONFIRMED — both measures are Vietnam-relevant.**

---

#### TEST-B8-04 MAC curve ordering check

**Computed cost per tonne across all measures:**

| Measure | Cost/tonne (sim units) |
|---|---|
| Blended clinker (cement) | 7,667 |
| Heat-rate upgrade (thermal) | 9,000 |
| Waste heat recovery (steel) | 9,000 |
| Kiln control (cement) | 9,500 |
| Biomass cofiring (thermal) | 9,286 |
| Scrap optimization (steel) | 10,000 |

**Assessment:** All measures cluster tightly in the 7,667–10,000 range. A real MAC curve would show much wider spread (negative-cost efficiency measures at left, expensive CCS at right). This tight clustering is a deliberate simplification — it prevents dominant strategies and keeps all options on the table throughout the workshop.

**Required facilitator note:** *"In reality, a MAC curve has a much wider cost spread — some measures have negative cost (net savings) and others cost hundreds of dollars per tonne. The simulator uses a compressed range to keep all options strategically viable across all three years."*

---

### B9 — Parameter Alignment Matrix

Complete this matrix after working through B1–B8 and record the verdict for each parameter.

| Parameter | Value (vietnam_pilot) | Policy Basis | Research Source | Verdict | Facilitator Note Required? |
|---|---|---|---|---|---|
| Covered sectors | thermal_power, steel, cement | Decree 119/2025 | CTX Impact Assessment p.vii | CONFIRMED | Yes — note omitted sectors |
| Emissions ordering | 120 > 95 > 88 | Vietnam GHG inventory | NDC 2022 | CONFIRMED | No |
| Growth rates | 3.0%, 2.2%, 1.8% | Conservative vs. 5–8% historical | IEA SEA Outlook 2023 | PLAUSIBLE | Yes — note conservatism |
| Allocation factors | 0.92/0.88/0.84 | Not yet specified in policy | Research synthesis | PLAUSIBLE | Yes — note as simulation parameter |
| Allocation method | Grandfathering (% of projected) | Pending benchmarking rules | Decree 06/2022 | PLAUSIBLE | Yes — note benchmarking gap |
| Penalty rate | 200 VND | Not yet specified | None directly | PLAUSIBLE | Yes — note design issue (< ceiling) |
| Penalty vs. ceiling | 200 < 300 — DESIGN ISSUE | ETS principle: penalty > ceiling | CarbonSim spec | GAP | Yes — mandatory |
| Auction in pilot | 12% of cap auctioned | Post-2028 only (real policy) | PM Decision 232/QD-TTg | DEPARTURE | Yes — mandatory |
| Price floor/ceiling | 80 / 300 sim units | Pending CTX price mechanism | Research synthesis | PLAUSIBLE | Yes — note scale |
| Offset cap | 10% | Pending subordinate legislation | Research synthesis | PLAUSIBLE | Yes — note upper-end |
| Offset types | Single pool | Multiple credit types in real market | CTX Impact Assessment | SIMPLIFICATION | Yes |
| Banking | Allowed (unlimited) | Decree 06/2022 allows banking | CTX Operational Model | CONFIRMED | Optional — note no limit |
| Borrowing | Prohibited | All major ETS, Decree 06/2022 | Research synthesis | CONFIRMED | No |
| Sectors omitted | Aviation, chemicals, paper | In scope for later ETS phases | PM Decision 13/2024 | ACKNOWLEDGED | Yes |

---

## SECTION C — Policy and Regulatory Alignment

### C1 — Legal Basis and Institutional Roles

#### TEST-C1-01 Legal framework citations are current

**Check:** All policy references in `FACILITATOR_RUNBOOK.md` and any in-app text use the current legal instruments:

| Instrument | Date | Key content |
|---|---|---|
| Law on Environmental Protection 2020 | Nov 2020 | Mandates domestic carbon market |
| Decree 06/2022/ND-CP | 7 Jan 2022 | ETS framework: MRV, allocation, trading, registry |
| Decree 119/2025/ND-CP | 9 Jun 2025 | Amends Decree 06; operationalises CTX definition |
| PM Decision 232/QD-TTg | 24 Jan 2025 | Approves pilot roadmap 2025–2028; full op from 2029 |
| PM Decision 13/2024/QD-TTg | 13 Aug 2024 | Updates GHG inventory sector list |

**Acceptance:** `FACILITATOR_RUNBOOK.md` references at least Decree 06/2022 (as amended), PM Decision 232/QD-TTg, and PM Decision 13/2024. No references to the now-superseded PM Decision 01/2022/QD-TTg (replaced by PM Decision 13/2024).

---

#### TEST-C1-02 Institutional role mapping

**Real institutions and their CTX roles:**

| Institution | Role |
|---|---|
| Ministry of Finance (MOF) | Responsible for CTX development and operation |
| Hanoi Stock Exchange (HNX) | Operating the CTX trading platform |
| Vietnam Securities Depository and Clearing Corporation (VSDC) | Settlement and clearing |
| Ministry of Agriculture and Environment (MAE) | National Registry System (NRS); market compliance oversight |
| State Securities Commission (SSC) | Market supervision |

**Simulator mapping:**
- Facilitator → MOF/HNX operator role (controls session, market mechanics)
- Participants → regulated entities (covered companies)
- No NRS, VSDC, SSC roles modelled

**Acceptance:** `FACILITATOR_RUNBOOK.md` includes a section mapping simulator roles to real institutions. Text should not imply the facilitator *is* the government — the facilitator is the market operator analogue.

---

#### TEST-C1-03 Pilot timeline framing

**Real timeline:** Pilot 2025–2028; full operation from 2029 (PM Decision 232/QD-TTg).  
**Simulator:** 3 compressed virtual years in a workshop session.

**Acceptance:** Workshop welcome instructions or facilitator briefing notes: *"Each virtual year represents one annual ETS compliance period, analogous to one year in Vietnam's 2025–2028 pilot phase."*

---

#### TEST-C1-04 Omitted sectors acknowledged

**Check:** `FACILITATOR_RUNBOOK.md` explicitly notes that aviation, chemicals, and paper are covered under Vietnam's broader ETS mandate (PM Decision 13/2024) but are not modelled in the simulator.

**Acceptance:** A debrief prompt: *"Vietnam's ETS covers [6 sectors]. This simulator focuses on the three largest pilot sectors. Why might the government prioritise these three first?"*

---

### C2 — Compliance Framework Rules

#### TEST-C2-01 Banking rule — correct and documented

**Policy basis:** Decree 06/2022 allows carrying unused allowances forward. There is no specified banking limit for the pilot phase in the available research.

**Simulator behaviour:** Unlimited banking (all surplus carries forward).

**Acceptance:**
1. TEST-A1-05 and TEST-A1-06 pass (banking logic is correct).
2. `FACILITATOR_RUNBOOK.md` notes: *"Banking is permitted under Decree 06/2022. The simulator allows unlimited banking. Some ETSs impose entity-level holding limits to prevent hoarding — Vietnam has not yet specified such limits."*

---

#### TEST-C2-02 No-borrowing rule — correct and documented

**Policy basis:** Borrowing is not provided for in Decree 06/2022 or any subordinate legislation. All major ETS frameworks prohibit it.

**Acceptance:**
1. TEST-A1-07 passes (no-borrowing is enforced in code).
2. `FACILITATOR_RUNBOOK.md` notes: *"Borrowing against future-year allocations is prohibited, consistent with all major ETS frameworks."*

---

#### TEST-C2-03 Offset make-good obligation — not modelled

**Real ETS design:** Some systems (EU ETS, California) impose a make-good obligation — companies that pay a penalty must *also* surrender missing allowances the following year.

**Simulator behaviour:** Penalty is cash-only. No make-good obligation.

**Acceptance:** `FACILITATOR_RUNBOOK.md` includes debrief prompt: *"Real ETS penalties often include a 'make-good' obligation — you pay the fine AND still have to surrender the missing allowances next year. The simulator uses cash-only penalties. How would a make-good requirement change your strategy?"*

---

### C3 — Market Oversight and Stabilisation

#### TEST-C3-01 Facilitator controls mapped to real oversight mechanisms

| Simulator control | Real CTX analogue |
|---|---|
| Pause session | Trading suspension by SSC/HNX |
| Force-advance phase | Compliance deadline enforcement by MAE |
| Trigger shock event | Market stabilisation trigger (SAM, CCR) |
| Export session data | Transaction reporting to NRS/SSC |
| Open/close auction | Government auction process |

**Acceptance:** Facilitator runbook debrief section maps each control to its real-world equivalent.

---

#### TEST-C3-02 Shock event Vietnam-context narratives

Each of the 4 shock types should have a Vietnam-specific debrief narrative in `FACILITATOR_RUNBOOK.md`:

| Shock | Vietnam narrative |
|---|---|
| emissions_spike | Severe drought reduces hydropower output → thermal dispatch surge → all thermal companies must run harder → emissions spike |
| allowance_withdrawal | Regulator discovers over-allocation after MRV audit → announces clawback of excess allowances mid-period |
| cost_shock | Global coal price spike raises fuel costs for thermal generators and operating costs for industrial producers |
| offset_supply_change | Regulator announces expansion of eligible domestic carbon credit types (e.g., new forestry REDD+ credits approved), temporarily flooding the offset market |

**Acceptance:** All four narratives are present in `FACILITATOR_RUNBOOK.md`.

---

#### TEST-C3-03 Price stabilisation mechanisms — not modelled

**Real Vietnam CTX:** The proposed operational model includes a Supply Adjustment Mechanism (SAM) and Cost Containment Reserve (CCR) analogous to the EU's Market Stability Reserve.

**Simulator:** No automatic price stabilisation. Facilitator can manually trigger shocks (which could simulate a SAM release) but there is no automatic trigger.

**Acceptance:** `FACILITATOR_RUNBOOK.md` notes: *"The real CTX will include automatic price containment mechanisms (floor/ceiling reserves). The simulator does not model these automatically — the facilitator triggers shocks manually to simulate market interventions."*

---

### C4 — MRV and Registry Gaps

#### TEST-C4-01 MRV gap acknowledged

**Real Vietnam:** MRV (Measurement, Reporting, Verification) is the weakest readiness area. The March 2025 Final Report (`research/20250418_Final_20Report_EN.md`) notes *"low readiness levels, particularly in MRV capacity"* among surveyed companies.

**Simulator:** Emissions are known exactly every year — perfect MRV, no uncertainty.

**Required debrief prompt in `FACILITATOR_RUNBOOK.md`:** *"This simulator gives you perfect emissions data every year. In the real ETS, your reported emissions go through an independent verification process, and errors can trigger compliance reviews. How would MRV uncertainty change your compliance strategy? What if your verifier rejects your data in February and your surrender deadline is March 31?"*

---

#### TEST-C4-02 NRS (National Registry System) gap acknowledged

**Real Vietnam:** MAE manages the NRS as the authoritative ledger. Every allowance issuance, trade, and surrender must be recorded in the NRS and reconciled daily. The NRS is separate from the CTX trading platform.

**Simulator:** State held in oTree's database; no registry layer; no reconciliation step.

**Required facilitator note:** *"The simulator does not model the National Registry System (NRS). In the real CTX, a trade is only final when both the CTX (HNX) and the NRS (MAE) record it. A transaction on the trading platform that fails NRS reconciliation is void."*

---

#### TEST-C4-03 KYC / participant eligibility not modelled

**Real Vietnam:** Companies must be registered in the NRS and pass KYC requirements before trading. The pilot covers ~1,912 facilities (as of the research reports).

**Simulator:** Any participant who joins the oTree session gets a company immediately.

**Acceptance:** This is an acknowledged scope exclusion; no code change required. Facilitator note: *"In the real CTX, companies must apply to MAE for registry accounts and complete KYC before they can trade."*

---

## SECTION D — Workshop Flow Testing

These are manual tests requiring a running oTree devserver (`cd platform && otree devserver`).

#### TEST-D-01 Devserver startup and health check
```bash
cd platform
otree devserver
```
Navigate to `http://localhost:8000/demo`.  
**Acceptance:** WorkshopHub room appears; "Start demo session" launches without console errors.

---

#### TEST-D-02 Three-participant join flow
Open 3 browser tabs. Join as three distinct participants.  
**Acceptance:**
- Tab 1 (first joiner) sees the facilitator panel.
- Tabs 2 and 3 see participant dashboards with unique company assignments.
- Company names match `vietnam_pilot` company library.
- No two participants share the same company.

---

#### TEST-D-03 Year-start allocation display
After facilitator starts simulation:  
**Acceptance:**
- Each participant sees their company's allowances, projected emissions, compliance gap.
- Values match TEST-A1-02/A1-03 formula outputs (±0.01 rounding).
- No NaN or undefined values in any field.

---

#### TEST-D-04 Decision window — live compliance gap updates
In the decision window, participant activates an abatement measure.  
**Acceptance:** Compliance gap on their dashboard updates within 1 second to reflect the abatement. No page refresh required.

---

#### TEST-D-05 Auction open/close/clear flow
Facilitator opens auction; participants submit bids; facilitator closes and clears.  
**Acceptance:**
- Clearing price, volume, and bid count visible to all participants after clearing.
- Company allowances and cash updated on their dashboards.

---

#### TEST-D-06 Trade propose/accept flow
Participant A proposes a trade to Participant B.  
**Acceptance:**
- Participant B sees the trade proposal.
- On acceptance, both balances update on their dashboards within 1 second.
- Trade appears in the trade feed visible to all.

---

#### TEST-D-07 Trade expiry (20-second timer)
Propose a trade and wait without responding.  
**Acceptance:** After 20 seconds, trade shows as "expired" on both dashboards; no settlement.

---

#### TEST-D-08 Year-end compliance display
Facilitator advances to year-end compliance phase.  
**Acceptance:**
- Each participant sees their penalty (if any), offsets used, banked allowances.
- Values match TEST-A1-04/A1-05 formula outputs.
- Rankings visible.

---

#### TEST-D-09 Full 3-year session and export
Run a complete 3-year session (manually or with bots).  
**Acceptance:**
- Session reaches PHASE_COMPLETE.
- Facilitator can download export JSON.
- Export parses without error and contains all 3 year_results per company.

---

#### TEST-D-10 Replay and analytics pages
After session completion, facilitator opens replay and analytics panels.  
**Acceptance:**
- Replay timeline shows ordered events with year markers.
- Analytics cards show market metrics, sector breakdown, and decision counts.
- No console errors.

---

#### TEST-D-11 Shock trigger and dashboard propagation
Facilitator triggers each of the 4 shock types.  
**Acceptance:**
- Participant dashboards update within 2 seconds.
- Shock event visible in audit log after export.

---

#### TEST-D-12 Pause/resume with deadline extension
Facilitator pauses mid-decision-window; resumes after ~30 seconds.  
**Acceptance:**
- Participants see "session paused" state during pause.
- On resume, deadline extends by approximately 30 seconds (within ±2s).
- Participant decisions made before pause are preserved.

---

#### TEST-D-13 Facilitator runbook coverage check (manual review)
Open `FACILITATOR_RUNBOOK.md` and verify each of the following notes is present:

- [ ] Auctions in pilot — pedagogical departure note (GAP-01)
- [ ] Price scale — dimensionless units note
- [ ] Penalty < ceiling — design issue note (GAP-06)
- [ ] Growth rate conservatism note
- [ ] Allocation method vs. benchmarking note
- [ ] MRV gap debrief prompt
- [ ] NRS gap note
- [ ] Offset cap uncertainty note
- [ ] Vietnam-context narratives for all 4 shock types
- [ ] Institutional role mapping table
- [ ] Omitted sectors note
- [ ] Banking (unlimited) note
- [ ] No borrowing confirmation
- [ ] Make-good obligation debrief prompt
- [ ] MAC curve compression note

---

## SECTION E — Deployment and Operational Testing

#### TEST-E-01 Docker Compose startup
```bash
docker-compose up --build
```
**Acceptance:** `web`, `worker`, and `db` services reach healthy status; no crash loops; `docker ps` shows all three running.

---

#### TEST-E-02 Environment variable validation
Set required env vars:
```bash
export OTREE_ADMIN_PASSWORD=testpass123
export SECRET_KEY=a-long-random-string
export DATABASE_URL=postgres://otree:otree@db/otree
export OTREE_PRODUCTION=1
```
**Acceptance:**
- App starts without error.
- `OTREE_PRODUCTION=1` disables debug mode (no stack traces in browser on error).
- `SECRET_KEY` is not hardcoded in `settings.py` — confirm with: `grep -n "SECRET_KEY" platform/settings.py`.

---

#### TEST-E-03 Health check response
```bash
curl http://localhost:8000/health  # or equivalent oTree health endpoint
```
**Acceptance:** `deployment.py::health_check()` returns a JSON dict with `phase`, `year`, `participant_count`, `auction_count`, `trade_count`, and `audit_log_size`.

---

#### TEST-E-04 Session recovery after reconnect
1. Start a session; advance to year 2 mid-decision-window.
2. Close one participant's browser tab.
3. Reopen and rejoin with the same participant name.

**Acceptance:** `reconnect_company()` restores correct company state; participant sees live dashboard with their current allowances, cash, compliance gap, and decision history intact.

---

#### TEST-E-05 Postgres persistence after restart
1. Start a session; advance to year 2.
2. Run `docker-compose restart`.
3. Navigate back to the session URL.

**Acceptance:** Session state fully preserved; no corruption of company state or audit log; participants can rejoin and continue.

---

#### TEST-E-06 Deployment test suite
```bash
cd platform
../.venv/Scripts/python.exe -m unittest tests.test_deployment -v
```
**Acceptance:** All 24 deployment tests pass.

---

#### TEST-E-07 Production mode flag check
```bash
grep -n "OTREE_PRODUCTION\|DEBUG" platform/settings.py
```
**Acceptance:** `OTREE_PRODUCTION` is read from environment (`os.environ`), not hardcoded to `0` or `False`. No hardcoded `DEBUG = True`.

---

## Known Gaps Catalogue

The following simplifications are **intentional and acceptable** for a workshop tool. Each must be documented in `FACILITATOR_RUNBOOK.md` with the debrief prompt specified below.

| ID | Description | Simulator | Real Vietnam Policy | Mandatory Facilitator Note |
|---|---|---|---|---|
| GAP-01 | Auctions in pilot phase | 2 auctions/year at 12% of cap | Free allocation only 2025–2028; auctioning post-2028 (PM Decision 232/QD-TTg) | Required — high risk of misconception |
| GAP-02 | Allocation method | Grandfathering (% of projected emissions) | Benchmarking-based methodology for thermal power; product benchmarks for steel/cement | Required |
| GAP-03 | No MRV modelling | Perfect emissions knowledge each year | Annual verified MRV reports; low capacity noted | Required — strong debrief prompt |
| GAP-04 | No NRS/registry | State in oTree DB; no reconciliation | All transactions in MAE NRS; daily reconciliation | Required |
| GAP-05 | Price scale | 80–300 simulation units | ~125,000–1,250,000 VND/tCO₂ (USD 5–50 range) | Required |
| GAP-06 | Penalty < auction ceiling | All 3 scenarios: penalty < ceiling | ETS design principle: penalty must exceed ceiling | Required — potential misconception; consider fixing in code |
| GAP-07 | Conservative growth rates | 1.8–3.0%/yr | Historical Vietnam: 5–8% (thermal), 4–6% (steel), 2–4% (cement) | Optional — useful for advanced sessions |
| GAP-08 | Single offset pool | One undifferentiated offset type | VNCCs, CDM offsets, VCS — different eligibility rules | Required |
| GAP-09 | Unlimited banking | No banking limit | Vietnam's limit not yet specified; some ETSs impose entity holding limits | Optional |
| GAP-10 | No market abuse controls | No position limits, no surveillance | SSC oversight; position limits proposed in Draft Decree | Optional |
| GAP-11 | No make-good obligation | Cash penalty only | EU ETS and California impose make-good (surrender deficit next year) | Required — debrief prompt |
| GAP-12 | No KYC / participant eligibility | Any session joiner gets a company | NRS account + KYC required in real CTX | Optional |
| GAP-13 | Compressed MAC curve | All measures 7,667–10,000/tonne (tight range) | Real MAC curves span negative-cost to $150+/tonne | Required |
| GAP-14 | No price stabilisation mechanism | Manual facilitator shocks only | Automatic SAM/CCR mechanisms in CTX proposal | Optional |
| GAP-15 | Omitted sectors | Only thermal, steel, cement | Aviation, chemicals, paper also in scope (PM Decision 13/2024) | Optional |

---

## Data Sources for Validation

| Source | Relevance | Location |
|---|---|---|
| Decree 06/2022/ND-CP (7 Jan 2022) | Legal basis; allocation, banking, trading, registry rules | Vietnamese government gazette |
| Decree 119/2025/ND-CP (9 Jun 2025) | Amends Decree 06; CTX definition; operationalises pilot | Vietnamese government gazette |
| PM Decision 232/QD-TTg (24 Jan 2025) | Pilot roadmap 2025–2028; full operation from 2029 | Vietnamese government gazette |
| PM Decision 13/2024/QD-TTg (13 Aug 2024) | Updated GHG inventory sector list (replaces PM Decision 01/2022) | Vietnamese government gazette |
| `research/20251128_CTX-Model-Impact-Assessment-Report_EN-1.md` | Covered sectors; institutional roles; financial feasibility of CTX | Repo research folder |
| `research/20251128_Recommending_20the_20CTX_20Operational_20Model_20Report_EN.md` | Transaction model; settlement design; market stability mechanisms | Repo research folder |
| `research/20260213_Recommendation_20Report_EN.md` | Transaction methods, supervision, bilateral trade design, DLT roadmap | Repo research folder |
| `research/20250418_Final_20Report_EN.md` | ETS simulation training results; MRV readiness; CarbonSim usage history | Repo research folder |
| `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md` | Price formation; MAC curves; compliance-cost modeling; carbon price range | Repo research folder |
| `research/2026-04-13_online-carbonsim-platform-create.md` | Synthesis brief; design rationale for simulator mechanics | Repo research folder |
| `research/carbonsim prelim research.md` | CarbonSim technical spec; year flow; compliance formulas | Repo research folder |
| ICAP Vietnam ETS Profile | Current pilot status; free allocation; covered entities | https://icapcarbonaction.com/en/ets/vietnam |
| IEA Southeast Asia Energy Outlook 2023 | Sector growth rate benchmarks | IEA website |
| Vietnam NDC 2022 Update | Sectoral BAU emissions baseline and reduction targets | UNFCCC NDC registry |
| IPCC 2006/2019 Guidelines Vol. 2 (Energy) | Reference emission factors for power, steel, cement | IPCC website |

---

## Open Design Decisions

The following decisions require facilitator or developer input before the simulator is used in a formal workshop. They are not bugs — they are policy choices that affect what participants learn.

**OD-001 — Penalty vs. ceiling (GAP-06)**  
_Question:_ Should the penalty rate be raised above the auction price ceiling in each scenario to ensure non-compliance is always economically irrational?

| Option | Change | Tradeoff |
|---|---|---|
| A — Fix (recommended) | Raise penalty to ceiling+1 in all three scenarios | Consistent with Vietnam policy intent; cleaner learning model |
| B — Document | Keep as-is; add mandatory facilitator warning | Allows "strategic non-compliance" as a teaching scenario; requires active facilitation |

_Recommended default:_ Option A — raise vietnam_pilot penalty to 301, high_pressure to 401, generous to 251.

---

**OD-002 — Auctions in the Vietnam Pilot scenario (GAP-01)**  
_Question:_ Should auctions be removed from the `vietnam_pilot` scenario to accurately reflect the 2025–2028 free-allocation-only pilot, with a separate `vietnam_full_operation` scenario that adds auctions?

| Option | Change | Tradeoff |
|---|---|---|
| A — Keep auctions (current) | Add mandatory facilitator disclaimer | Teaches auction mechanics even in "Vietnam Pilot" framing |
| B — Split scenarios | Create `vietnam_pilot` (no auctions) + `vietnam_full_operation` (with auctions) | More accurate framing; requires updating `settings.py` session configs |

_Recommended default:_ Option A for V1 (minimise code change); Option B as a V2 improvement.

---

**OD-003 — Growth rate calibration**  
_Question:_ Should growth rates be increased to match historical Vietnamese sector data, or kept conservative?

| Option | Growth rates | When to use |
|---|---|---|
| A — Conservative (current) | 3.0%, 2.2%, 1.8% | First-time participants; introductory workshops |
| B — Historical | ~5.5%, 4.5%, 3.0% | Policy professionals; advanced workshops |

_Recommended default:_ Add a `growth_rate_multiplier` parameter to `create_initial_state()` (default=1.0); facilitators can set it to 1.5–2.0 for advanced sessions without changing scenario pack defaults.

---

*End of Vietnam Market Testing Plan v1.0*