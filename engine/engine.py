from __future__ import annotations

import random as _random
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from .constants import (
    PHASE_LOBBY,
    PHASE_YEAR_START,
    PHASE_DECISION_WINDOW,
    PHASE_COMPLIANCE,
    PHASE_COMPLETE,
    PHASE_PAUSED,
    DEFAULT_PHASE_DURATIONS,
    DEFAULT_OFFSET_USAGE_CAP,
    DEFAULT_AUCTION_COUNT,
    DEFAULT_AUCTION_PRICE_FLOOR,
    DEFAULT_AUCTION_PRICE_CEILING,
    DEFAULT_AUCTION_SHARE_OF_CAP,
    DEFAULT_TRADE_EXPIRY_SECONDS,
    DEFAULT_OFFSET_PRICE,
    DEFAULT_PENALTY_RATE,
    VND_FX,
    BOT_STRATEGY_CONSERVATIVE,
    BOT_STRATEGY_MODERATE,
    BOT_STRATEGY_AGGRESSIVE,
    BOT_STRATEGIES,
    YEARLY_ALLOCATION_FACTORS,
    PHASE_LABELS,
)
from .scenarios import SCENARIO_PACKS, SHOCK_CATALOG, VCM_CATALOG

COMPANY_LIBRARY = SCENARIO_PACKS["vietnam_pilot"]["company_library"]
ABATEMENT_CATALOG = SCENARIO_PACKS["vietnam_pilot"]["abatement_catalog"]


def create_initial_state(
    participant_count: int,
    *,
    num_years: int = 3,
    penalty_rate: float | None = None,
    offset_usage_cap: float | None = None,
    phase_durations: dict[str, int] | None = None,
    scenario: str | None = None,
    bot_count: int = 0,
    bot_strategy: str = BOT_STRATEGY_MODERATE,
    rng_seed: int | None = None,
    jurisdiction: str | None = None,
) -> dict[str, Any]:
    pack = SCENARIO_PACKS.get(
        scenario or "vietnam_pilot", SCENARIO_PACKS["vietnam_pilot"]
    )
    # Jurisdiction skin overlay (TASK-05-08): merge over a copy of the base pack
    # so company names, sector labels, and calibrated constants come from the
    # chosen jurisdiction (EU ETS, California ARB) without mutating the base.
    jurisdiction = jurisdiction or pack.get("jurisdiction")
    if jurisdiction and jurisdiction != "vietnam":
        overlay = load_jurisdiction(jurisdiction)
        if overlay:
            pack = {**deepcopy(pack), **overlay, "jurisdiction": jurisdiction}
    durations = dict(DEFAULT_PHASE_DURATIONS)
    if phase_durations:
        durations.update(phase_durations)

    effective_penalty = (
        penalty_rate if penalty_rate is not None else pack["penalty_rate"]
    )
    effective_offset_cap = (
        offset_usage_cap if offset_usage_cap is not None else pack["offset_usage_cap"]
    )
    # Deep-copy so per-game mutations (e.g. apply_shock(election_pressure),
    # which rewrites allocation_factors in place) never leak back into the
    # shared SCENARIO_PACKS dict and corrupt subsequent games in the process.
    allocation_factors = deepcopy(pack.get("allocation_factors", YEARLY_ALLOCATION_FACTORS))
    scenario_library = pack["company_library"]
    scenario_abatement = pack["abatement_catalog"]

    human_count = participant_count
    total_count = human_count + bot_count
    companies = []
    for index in range(total_count):
        base = deepcopy(scenario_library[index % len(scenario_library)])
        cohort = index // len(scenario_library)
        suffix = "" if cohort == 0 else f" {cohort + 1}"
        is_bot = index >= human_count
        base["company_id"] = f"C{index + 1:02d}"
        base["company_name"] = f"{base['company_name']}{suffix}"
        baseline_multiplier = 1 + (cohort * 0.04)
        base["baseline_emissions"] = round(
            base["baseline_emissions"] * baseline_multiplier, 2
        )
        base["cash"] = round(base["cash"] + (cohort * 175_000), 2)
        companies.append(
            {
                **base,
                "current_year_allocation": 0.0,
                "projected_emissions": base["baseline_emissions"],
                "allowances": 0.0,
                "banked_allowances": 0.0,
                "offset_holdings": 0.0,
                "offsets_used_for_compliance": 0.0,
                "penalty_due": 0.0,
                "cumulative_penalties": 0.0,
                "compliance_gap": 0.0,
                "abatement_menu": [
                    _enrich_measure(deepcopy(m)) for m in scenario_abatement[base["sector"]]
                ],
                "active_abatement_ids": [],
                "pending_abatement_ids": [],
                "abatement_cost_committed": 0.0,
                "auction_allowances_won": 0.0,
                "year_results": [],
                "forward_contracts": [],
                "vcm_projects": [],
                # Sprint 5 — capex / financing / tech-risk ledgers (additive;
                # active_abatement_ids remains the emissions source of truth).
                "active_abatement_assets": [],
                "active_loans": [],
                "tech_impaired_ids": [],
                "is_bot": is_bot,
                "bot_strategy": bot_strategy if is_bot else None,
            }
        )

    return {
        "participant_count": human_count,
        "total_count": total_count,
        "num_years": num_years,
        "current_year": 0,
        "current_cap": 0.0,
        "penalty_rate": effective_penalty,
        "offset_usage_cap": effective_offset_cap,
        "offset_price": pack.get("offset_price", DEFAULT_OFFSET_PRICE),
        "auction_count_per_year": pack.get(
            "auction_count_per_year", DEFAULT_AUCTION_COUNT
        ),
        "auction_price_floor": pack.get(
            "auction_price_floor", DEFAULT_AUCTION_PRICE_FLOOR
        ),
        "auction_price_ceiling": pack.get(
            "auction_price_ceiling", DEFAULT_AUCTION_PRICE_CEILING
        ),
        "auction_share_of_cap": pack.get(
            "auction_share_of_cap", DEFAULT_AUCTION_SHARE_OF_CAP
        ),
        "trade_expiry_seconds": pack.get(
            "trade_expiry_seconds", DEFAULT_TRADE_EXPIRY_SECONDS
        ),
        "allocation_factors": allocation_factors,
        "phase": PHASE_LOBBY,
        "paused_from": None,
        "phase_durations": durations,
        "phase_started_at": None,
        "phase_deadline_at": None,
        "started_at": None,
        "completed_at": None,
        "companies": companies,
        "auctions": [],
        "trades": [],
        "audit_log": [],
        "participant_status": {},
        "scenario": scenario or "vietnam_pilot",
        "active_shocks": [],
        "rng_seed": rng_seed if rng_seed is not None else _random.randint(0, 2**32 - 1),
        "offset_demand_this_year": 0.0,
        "offset_price_elasticity": pack.get("offset_price_elasticity", 0.4),
        "annual_offset_supply_cap": pack.get("annual_offset_supply_cap", 50.0),
        "current_offset_price": pack.get("offset_price", DEFAULT_OFFSET_PRICE),
        "last_auction_clearing_price": 0.0,
        # Sprint 4 — Story / policy stability.
        # policy_stability (0-100) drives the dynamic cap modulation and the
        # auto crackdown/relief triggers. Starts at 70 (neutral: cap modifier
        # is 1.0 at 70 so Sprint 1-3 balance is unchanged on a fresh game).
        "policy_stability": float(pack.get("policy_stability", 70.0)),
        "active_conditions": [],
        # Multi-turn card effects: each entry re-applies for `remaining_years`.
        "active_effects": [],
        # Card ids queued by follow_on_cards, force-drawn next decision window.
        "pending_card_injections": [],
        # Sprint 5 — meta-progression.
        "jurisdiction": pack.get("jurisdiction", "vietnam"),
        "scenario_interest_rate": pack.get("scenario_interest_rate", 0.08),
        "scenario_loan_term": pack.get("scenario_loan_term", 5),
        "xp": 0,
        "xp_level": 1,
        "unlocked_features": [],
    }


# XP level thresholds (TASK-05-05): index 0 -> level 1, etc.
XP_LEVEL_THRESHOLDS = [0, 200, 500, 1000, 2000, 4000]

# Default capex schema fields for abatement measures (TASK-05-01). Defaults are
# balance-neutral: capex == the legacy `cost`, no opex, no tech risk, so existing
# measures behave exactly as before; richer measures opt in explicitly.
def _enrich_measure(measure: dict[str, Any]) -> dict[str, Any]:
    cost = measure.get("cost", 0.0)
    measure.setdefault("capex", cost)
    measure.setdefault("annual_opex", 0.0)
    measure.setdefault("asset_life_years", 8)
    measure.setdefault("tech_risk_pct", 0.0)
    abatement = max(measure.get("abatement_amount", 0.0), 0.01)
    # break_even_year ~ capex / annual value of avoided penalty at a nominal rate.
    measure["break_even_year"] = round(measure["capex"] / (abatement * 1000.0), 2)
    return measure


def _register_abatement_asset(
    company: dict[str, Any], measure: dict[str, Any], year: int, *, financed: bool
) -> None:
    """Record an installed abatement asset for opex/tech-risk tracking (TASK-05-02)."""
    company.setdefault("active_abatement_assets", []).append({
        "measure_id": measure["measure_id"],
        "installed_year": year,
        "remaining_life": measure.get("asset_life_years", 8),
        "annual_opex": measure.get("annual_opex", 0.0),
        "annual_reduction": measure.get("abatement_amount", 0.0),
        "tech_risk_pct": measure.get("tech_risk_pct", 0.0),
        "financed": financed,
    })


def build_abatement_menu(sector: str) -> list[dict[str, Any]]:
    return [_enrich_measure(deepcopy(measure)) for measure in ABATEMENT_CATALOG[sector]]


_UNLOCK_TREE_CACHE: list[dict[str, Any]] | None = None


def load_unlock_tree() -> list[dict[str, Any]]:
    """Load the XP unlock tree definition (TASK-05-06), cached after first read."""
    global _UNLOCK_TREE_CACHE
    if _UNLOCK_TREE_CACHE is None:
        import json
        from pathlib import Path

        path = Path(__file__).parent / "data" / "unlock_tree.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            _UNLOCK_TREE_CACHE = data.get("nodes", data) if isinstance(data, dict) else data
        except (OSError, ValueError):
            _UNLOCK_TREE_CACHE = []
    return _UNLOCK_TREE_CACHE


def load_jurisdiction(jurisdiction: str) -> dict[str, Any]:
    """Load a jurisdiction skin overlay (TASK-05-08). Returns {} if absent.

    Money fields are FX'd to VND at load time so the JSON stays human-readable
    in the original per-tonne units. The Vietnam volume factor is intentionally
    NOT applied: jurisdiction overlays (EU/CA) keep their own realistic
    tonnages, and their company cash reflects an EU/California industrial
    budget, not the Vietnam national-scale rescale (plan DEC-002).
    """
    import json
    from copy import deepcopy
    from pathlib import Path

    if not jurisdiction or jurisdiction == "vietnam":
        return {}
    path = Path(__file__).parent / "data" / "jurisdictions" / f"{jurisdiction}.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}

    overlay = deepcopy(raw)
    for key in ("penalty_rate", "offset_price", "auction_price_floor", "auction_price_ceiling"):
        if key in overlay:
            overlay[key] = round(overlay[key] * VND_FX, 2)
    for company in overlay.get("company_library", []):
        if "cash" in company:
            company["cash"] = round(company["cash"] * VND_FX, 2)
    return overlay


def apply_company_decision(
    state: dict[str, Any],
    *,
    company_id: str,
    action: str,
    payload: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    state = advance_state(state, now)
    company = _get_company(state, company_id)
    decision_time = _normalize_time(now)

    if state["phase"] != PHASE_DECISION_WINDOW:
        return state

    if action == "activate_abatement":
        measure_id = payload["measure_id"]
        measure = _get_measure(company, measure_id)
        if (
            measure_id in company["active_abatement_ids"]
            or measure_id in company["pending_abatement_ids"]
        ):
            return state
        # Pay capex up front (legacy behaviour: capex defaults to `cost`). The
        # loan path lives in finance_abatement.
        capex = measure.get("capex", measure["cost"])
        company["abatement_cost_committed"] = round(
            company["abatement_cost_committed"] + capex, 2
        )
        company["cash"] = round(company["cash"] - capex, 2)
        _register_abatement_asset(company, measure, state["current_year"], financed=False)
        if measure["activation_timing"] == "immediate":
            company["active_abatement_ids"].append(measure_id)
        else:
            company["pending_abatement_ids"].append(measure_id)
        _recalculate_company_projection(state, company)
        _append_event(
            state,
            "abatement_activated",
            decision_time,
            {
                "year": state["current_year"],
                "company_id": company_id,
                "measure_id": measure_id,
            },
        )
        return state

    if action == "finance_abatement":
        # Capex via loan instead of cash up front (TASK-05-03).
        measure_id = payload["measure_id"]
        measure = _get_measure(company, measure_id)
        if (
            measure_id in company["active_abatement_ids"]
            or measure_id in company["pending_abatement_ids"]
        ):
            return state
        capex = measure.get("capex", measure["cost"])
        rate = state.get("scenario_interest_rate", 0.08)
        term = min(measure.get("asset_life_years", 8), state.get("scenario_loan_term", 5))
        term = max(int(term), 1)
        # Equal annual installments: amortized payment over the term.
        if rate > 0:
            annual_payment = round(capex * rate / (1 - (1 + rate) ** (-term)), 2)
        else:
            annual_payment = round(capex / term, 2)
        company.setdefault("active_loans", []).append({
            "loan_id": f"LN-Y{state['current_year']}-{len(company.get('active_loans', [])) + 1:02d}",
            "principal": round(capex, 2),
            "annual_payment": annual_payment,
            "remaining_years": term,
            "measure_id": measure_id,
            "interest_rate": rate,
        })
        company["abatement_cost_committed"] = round(
            company["abatement_cost_committed"] + capex, 2
        )
        _register_abatement_asset(company, measure, state["current_year"], financed=True)
        if measure["activation_timing"] == "immediate":
            company["active_abatement_ids"].append(measure_id)
        else:
            company["pending_abatement_ids"].append(measure_id)
        _recalculate_company_projection(state, company)
        _append_event(
            state,
            "abatement_financed",
            decision_time,
            {
                "year": state["current_year"],
                "company_id": company_id,
                "measure_id": measure_id,
                "annual_payment": annual_payment,
                "term": term,
            },
        )
        return state

    if action == "buy_offsets":
        quantity = round(float(payload.get("quantity", 0)), 2)
        if quantity <= 0:
            return state
        base_price = state.get("offset_price", DEFAULT_OFFSET_PRICE)
        elasticity = state.get("offset_price_elasticity", 0.4)
        supply_cap = max(state.get("annual_offset_supply_cap", 50.0), 1.0)
        demand = state.get("offset_demand_this_year", 0.0)
        live_price = round(base_price * (1 + elasticity * min(demand / supply_cap, 1.0)), 2)
        offset_price = payload.get("price_per_unit", live_price)
        total_cost = round(quantity * float(offset_price), 2)
        company["offset_holdings"] = round(company["offset_holdings"] + quantity, 2)
        company["cash"] = round(company["cash"] - total_cost, 2)
        new_demand = round(demand + quantity, 2)
        state["offset_demand_this_year"] = new_demand
        state["current_offset_price"] = round(
            base_price * (1 + elasticity * min(new_demand / supply_cap, 1.0)), 2
        )
        _recalculate_company_projection(state, company)
        _append_event(
            state,
            "offsets_purchased",
            decision_time,
            {
                "year": state["current_year"],
                "company_id": company_id,
                "quantity": quantity,
                "price_per_unit": float(offset_price),
            },
        )
        return state

    if action == "buy_forward":
        quantity = round(float(payload.get("quantity", 0)), 2)
        if quantity <= 0:
            return state
        base_price = state.get("offset_price", DEFAULT_OFFSET_PRICE)
        elasticity = state.get("offset_price_elasticity", 0.4)
        supply_cap = max(state.get("annual_offset_supply_cap", 50.0), 1.0)
        demand = state.get("offset_demand_this_year", 0.0)
        spot_price = round(base_price * (1 + elasticity * min(demand / supply_cap, 1.0)), 2)
        locked_price = round(spot_price * 1.05, 2)  # 5% forward term premium
        total_cost = round(quantity * locked_price, 2)
        if company["cash"] < total_cost:
            return state
        delivery_year = state["current_year"] + 1
        contract_id = f"FWD-Y{state['current_year']}-{len(company['forward_contracts']) + 1:02d}"
        company["cash"] = round(company["cash"] - total_cost, 2)
        company["forward_contracts"].append({
            "contract_id": contract_id,
            "quantity": quantity,
            "locked_price": locked_price,
            "purchase_year": state["current_year"],
            "delivery_year": delivery_year,
        })
        _append_event(
            state,
            "forward_purchased",
            decision_time,
            {
                "year": state["current_year"],
                "company_id": company_id,
                "quantity": quantity,
                "locked_price": locked_price,
                "delivery_year": delivery_year,
                "contract_id": contract_id,
            },
        )
        return state

    if action == "invest_vcm":
        project_id = payload.get("project_id", "")
        proj_template = next((p for p in VCM_CATALOG if p["project_id"] == project_id), None)
        if not proj_template:
            return state
        if any(p["project_id"] == project_id for p in company.get("vcm_projects", [])):
            return state  # already invested
        cost = proj_template["cost"]
        if company["cash"] < cost:
            return state
        company["cash"] = round(company["cash"] - cost, 2)
        company["vcm_projects"].append({
            "project_id": project_id,
            "label": proj_template["label"],
            "annual_credits": proj_template["annual_credits"],
            "remaining_years": proj_template["duration_years"],
            "cost": cost,
            "invested_year": state["current_year"],
        })
        _append_event(
            state,
            "vcm_invested",
            decision_time,
            {
                "year": state["current_year"],
                "company_id": company_id,
                "project_id": project_id,
                "cost": cost,
                "annual_credits": proj_template["annual_credits"],
            },
        )
        return state

    if action == "submit_auction_bid":
        return submit_auction_bid(
            state,
            company_id=company_id,
            auction_id=payload["auction_id"],
            quantity=payload["quantity"],
            price=payload["price"],
            now=decision_time,
        )

    if action == "propose_trade":
        return propose_trade(
            state,
            seller_company_id=company_id,
            buyer_company_id=payload["buyer_company_id"],
            quantity=payload["quantity"],
            price_per_allowance=payload["price_per_allowance"],
            now=decision_time,
        )

    return state


def propose_trade(
    state: dict[str, Any],
    *,
    seller_company_id: str,
    buyer_company_id: str,
    quantity: float,
    price_per_allowance: float,
    now: datetime,
) -> dict[str, Any]:
    state = advance_state(state, now)
    if state["phase"] != PHASE_DECISION_WINDOW:
        raise ValueError("Trades can only be proposed during the decision window")

    seller = _get_company(state, seller_company_id)
    buyer = _get_company(state, buyer_company_id)
    quantity = round(float(quantity), 2)
    price_per_allowance = round(float(price_per_allowance), 2)
    total_value = round(quantity * price_per_allowance, 2)

    if seller_company_id == buyer_company_id:
        raise ValueError("Trade counterparty must be different from seller")
    if quantity <= 0 or price_per_allowance <= 0:
        raise ValueError("Trade quantity and price must be positive")
    if seller["allowances"] < quantity:
        raise ValueError("Seller does not have enough allowances")
    if buyer["cash"] < total_value:
        raise ValueError("Buyer does not have enough cash")

    created_at = _normalize_time(now)
    trade = {
        "trade_id": f"T{len(state['trades']) + 1:03d}",
        "year": state["current_year"],
        "seller_company_id": seller_company_id,
        "buyer_company_id": buyer_company_id,
        "quantity": quantity,
        "price_per_allowance": price_per_allowance,
        "total_value": total_value,
        "status": "proposed",
        "created_at": _serialize_time(created_at),
        "expires_at": _serialize_time(
            created_at + timedelta(seconds=state["trade_expiry_seconds"])
        ),
        "responded_at": None,
    }
    state["trades"].append(trade)
    _append_event(
        state,
        "trade_proposed",
        created_at,
        {
            "year": state["current_year"],
            "trade_id": trade["trade_id"],
            "seller_company_id": seller_company_id,
            "buyer_company_id": buyer_company_id,
            "quantity": quantity,
            "price_per_allowance": price_per_allowance,
        },
    )
    return state


def respond_to_trade(
    state: dict[str, Any],
    *,
    trade_id: str,
    responder_company_id: str,
    response: str,
    now: datetime,
) -> dict[str, Any]:
    state = advance_state(state, now)
    trade = _get_trade(state, trade_id)
    if trade["status"] != "proposed":
        raise ValueError("Trade is no longer open for response")
    if responder_company_id != trade["buyer_company_id"]:
        raise ValueError("Only the designated buyer can respond to this trade")

    response_time = _normalize_time(now)
    if response == "reject":
        trade["status"] = "rejected"
        trade["responded_at"] = _serialize_time(response_time)
        _append_event(
            state,
            "trade_rejected",
            response_time,
            {"year": state["current_year"], "trade_id": trade_id},
        )
        return state

    if response != "accept":
        raise ValueError("Unsupported trade response")

    seller = _get_company(state, trade["seller_company_id"])
    buyer = _get_company(state, trade["buyer_company_id"])
    if seller["allowances"] < trade["quantity"]:
        raise ValueError("Seller no longer has enough allowances")
    if buyer["cash"] < trade["total_value"]:
        raise ValueError("Buyer no longer has enough cash")

    seller["allowances"] = round(seller["allowances"] - trade["quantity"], 2)
    buyer["allowances"] = round(buyer["allowances"] + trade["quantity"], 2)
    seller["cash"] = round(seller["cash"] + trade["total_value"], 2)
    buyer["cash"] = round(buyer["cash"] - trade["total_value"], 2)
    _recalculate_company_projection(state, seller)
    _recalculate_company_projection(state, buyer)

    trade["status"] = "accepted"
    trade["responded_at"] = _serialize_time(response_time)
    _append_event(
        state,
        "trade_accepted",
        response_time,
        {
            "year": state["current_year"],
            "trade_id": trade_id,
            "quantity": trade["quantity"],
            "price_per_allowance": trade["price_per_allowance"],
        },
    )
    return state


def open_auction(
    state: dict[str, Any], *, auction_id: str, now: datetime
) -> dict[str, Any]:
    state = advance_state(state, now)
    auction = _get_auction(state, auction_id)
    if auction["status"] == "scheduled":
        auction["status"] = "open"
        auction["opened_at"] = _serialize_time(_normalize_time(now))
        _append_event(
            state,
            "auction_opened",
            _normalize_time(now),
            {"year": state["current_year"], "auction_id": auction_id},
        )
    return state


def submit_auction_bid(
    state: dict[str, Any],
    *,
    company_id: str,
    auction_id: str,
    quantity: float,
    price: float,
    now: datetime,
) -> dict[str, Any]:
    state = advance_state(state, now)
    company = _get_company(state, company_id)
    auction = _get_auction(state, auction_id)

    if auction["status"] != "open":
        raise ValueError("Auction is not open for bids")
    if quantity <= 0:
        raise ValueError("Bid quantity must be positive")
    if price < state["auction_price_floor"] or price > state["auction_price_ceiling"]:
        raise ValueError("Bid price is outside the auction collar")
    if round(quantity * price, 2) > company["cash"]:
        raise ValueError("Company does not have enough cash for this bid")

    bid = {
        "bid_id": f"{auction_id}-B{len(auction['bids']) + 1:03d}",
        "company_id": company_id,
        "quantity": round(quantity, 2),
        "price": round(price, 2),
        "submitted_at": _serialize_time(_normalize_time(now)),
    }
    auction["bids"].append(bid)
    _append_event(
        state,
        "auction_bid_submitted",
        _normalize_time(now),
        {
            "year": state["current_year"],
            "auction_id": auction_id,
            "company_id": company_id,
            "quantity": quantity,
            "price": price,
        },
    )
    return state


def close_auction(
    state: dict[str, Any], *, auction_id: str, now: datetime
) -> dict[str, Any]:
    state = advance_state(state, now)
    auction = _get_auction(state, auction_id)
    if auction["status"] not in {"open", "scheduled"}:
        return state

    ordered_bids = sorted(
        auction["bids"],
        key=lambda bid: (-bid["price"], bid["submitted_at"], bid["bid_id"]),
    )
    remaining_supply = auction["supply"]
    results = []
    clearing_price = 0.0

    for bid in ordered_bids:
        awarded_quantity = min(bid["quantity"], remaining_supply)
        if awarded_quantity <= 0:
            results.append({**bid, "awarded_quantity": 0.0, "payment_due": 0.0})
            continue
        remaining_supply = round(remaining_supply - awarded_quantity, 2)
        clearing_price = bid["price"]
        results.append({**bid, "awarded_quantity": awarded_quantity})

    results_by_company = {result["company_id"]: 0.0 for result in results}
    for result in results:
        result["payment_due"] = round(result["awarded_quantity"] * clearing_price, 2)
        results_by_company[result["company_id"]] = round(
            results_by_company[result["company_id"]] + result["awarded_quantity"], 2
        )

    for company in state["companies"]:
        awarded = results_by_company.get(company["company_id"], 0.0)
        if awarded <= 0:
            continue
        payment_due = round(awarded * clearing_price, 2)
        company["allowances"] = round(company["allowances"] + awarded, 2)
        company["auction_allowances_won"] = round(
            company["auction_allowances_won"] + awarded, 2
        )
        company["cash"] = round(company["cash"] - payment_due, 2)
        company["compliance_gap"] = round(
            company["projected_emissions"]
            - company["allowances"]
            - company["offset_holdings"],
            2,
        )

    auction["status"] = "cleared"
    auction["closed_at"] = _serialize_time(_normalize_time(now))
    auction["clearing_price"] = clearing_price
    auction["results"] = results
    auction["remaining_supply"] = remaining_supply
    _append_event(
        state,
        "auction_cleared",
        _normalize_time(now),
        {
            "year": state["current_year"],
            "auction_id": auction_id,
            "clearing_price": clearing_price,
            "cleared_quantity": round(auction["supply"] - remaining_supply, 2),
        },
    )
    return state


def start_simulation(state: dict[str, Any], now: datetime) -> dict[str, Any]:
    if state["phase"] != PHASE_LOBBY:
        return state

    current_time = _normalize_time(now)
    state["started_at"] = _serialize_time(current_time)
    _start_year(state, 1, current_time)
    return state


def pause_session(state: dict[str, Any], now: datetime) -> dict[str, Any]:
    phasable = {PHASE_YEAR_START, PHASE_DECISION_WINDOW, PHASE_COMPLIANCE}
    if state["phase"] not in phasable:
        return state

    current_time = _normalize_time(now)
    state["paused_from"] = _serialize_time(current_time)
    state["phase_before_pause"] = state["phase"]
    state["phase"] = PHASE_PAUSED
    _append_event(
        state, "session_paused", current_time, {"year": state["current_year"]}
    )
    return state


def resume_session(state: dict[str, Any], now: datetime) -> dict[str, Any]:
    if state["phase"] != PHASE_PAUSED:
        return state

    current_time = _normalize_time(now)
    previous_phase = state.get("phase_before_pause", PHASE_YEAR_START)
    pause_duration = current_time - _parse_time(state["paused_from"])

    state["phase"] = previous_phase
    state["paused_from"] = None
    state.pop("phase_before_pause", None)

    if state["phase_deadline_at"]:
        old_deadline = _parse_time(state["phase_deadline_at"])
        new_deadline = old_deadline + pause_duration
        state["phase_deadline_at"] = _serialize_time(new_deadline)

    _append_event(
        state, "session_resumed", current_time, {"year": state["current_year"]}
    )
    return state


def force_advance_phase(state: dict[str, Any], now: datetime) -> dict[str, Any]:
    if state["phase"] in {PHASE_LOBBY, PHASE_COMPLETE, PHASE_PAUSED}:
        return state

    current_time = _normalize_time(now)
    previous_phase = state["phase"]

    if state["phase"] == PHASE_YEAR_START:
        _set_phase(state, PHASE_DECISION_WINDOW, current_time)
        _append_event(
            state,
            "decision_window_opened",
            current_time,
            {"year": state["current_year"]},
        )
        _append_event(
            state,
            "phase_force_advanced",
            current_time,
            {"year": state["current_year"], "from_phase": previous_phase},
        )
        return state

    if state["phase"] == PHASE_DECISION_WINDOW:
        _close_current_year(state, current_time)
        _set_phase(state, PHASE_COMPLIANCE, current_time)
        _append_event(
            state,
            "phase_force_advanced",
            current_time,
            {"year": state["current_year"], "from_phase": previous_phase},
        )
        return state

    if state["phase"] == PHASE_COMPLIANCE:
        if state["current_year"] >= state["num_years"]:
            state["phase"] = PHASE_COMPLETE
            state["phase_started_at"] = _serialize_time(current_time)
            state["phase_deadline_at"] = None
            state["completed_at"] = _serialize_time(current_time)
            _append_event(
                state,
                "session_completed",
                current_time,
                {"year": state["current_year"]},
            )
            _append_event(
                state,
                "phase_force_advanced",
                current_time,
                {"year": state["current_year"], "from_phase": previous_phase},
            )
        else:
            _start_year(state, state["current_year"] + 1, current_time)
            _append_event(
                state,
                "phase_force_advanced",
                current_time,
                {"year": state["current_year"], "from_phase": previous_phase},
            )
        return state

    return state


def update_participant_status(
    state: dict[str, Any],
    *,
    company_id: str,
    action: str,
    now: datetime,
) -> dict[str, Any]:
    current_time = _normalize_time(now)
    status = state.setdefault("participant_status", {})
    if company_id not in status:
        status[company_id] = {
            "last_seen": None,
            "last_action": None,
            "decision_count_this_year": 0,
        }
    entry = status[company_id]
    entry["last_seen"] = _serialize_time(current_time)
    entry["last_action"] = action
    if action in {
        "activate_abatement",
        "buy_offsets",
        "submit_auction_bid",
        "propose_trade",
        "respond_trade",
    }:
        entry["decision_count_this_year"] = entry.get("decision_count_this_year", 0) + 1
    return state


def advance_state(state: dict[str, Any], now: datetime) -> dict[str, Any]:
    if state["phase"] in {PHASE_LOBBY, PHASE_COMPLETE, PHASE_PAUSED}:
        return state

    current_time = _normalize_time(now)
    _expire_trades(state, current_time)
    while (
        state["phase_deadline_at"]
        and _parse_time(state["phase_deadline_at"]) <= current_time
    ):
        transition_time = _parse_time(state["phase_deadline_at"])

        if state["phase"] == PHASE_YEAR_START:
            _set_phase(state, PHASE_DECISION_WINDOW, transition_time)
            _append_event(
                state,
                "decision_window_opened",
                transition_time,
                {"year": state["current_year"]},
            )
            continue

        if state["phase"] == PHASE_DECISION_WINDOW:
            _close_current_year(state, transition_time)
            _set_phase(state, PHASE_COMPLIANCE, transition_time)
            continue

        if state["phase"] == PHASE_COMPLIANCE:
            if state["current_year"] >= state["num_years"]:
                state["phase"] = PHASE_COMPLETE
                state["phase_started_at"] = _serialize_time(transition_time)
                state["phase_deadline_at"] = None
                state["completed_at"] = _serialize_time(transition_time)
                _append_event(
                    state,
                    "session_completed",
                    transition_time,
                    {"year": state["current_year"]},
                )
            else:
                _start_year(state, state["current_year"] + 1, transition_time)
            continue

        break

    return state


def build_player_snapshot(
    state: dict[str, Any],
    *,
    company_id: str,
    is_facilitator: bool,
    participant_label: str,
    now: datetime,
) -> dict[str, Any]:
    current_time = _normalize_time(now)
    company = next(
        (item for item in state["companies"] if item["company_id"] == company_id), None
    )
    deadline = (
        _parse_time(state["phase_deadline_at"]) if state["phase_deadline_at"] else None
    )
    countdown = (
        0
        if deadline is None
        else max(0, int((deadline - current_time).total_seconds()))
    )

    leaderboard = []
    for item in sorted(
        state["companies"],
        key=lambda company_state: (
            company_state["cumulative_penalties"],
            company_state["penalty_due"],
            -company_state["banked_allowances"],
            company_state["company_name"],
        ),
    ):
        leaderboard.append(
            {
                "company_id": item["company_id"],
                "company_name": item["company_name"],
                "sector_label": item["sector"].replace("_", " ").title(),
                "banked_allowances": item["banked_allowances"],
                "compliance_gap": item["compliance_gap"],
                "cumulative_penalties": item["cumulative_penalties"],
            }
        )

    recent_events = []
    for event in reversed(state["audit_log"][-8:]):
        recent_events.append(
            {
                "timestamp": event["timestamp"],
                "event_type": event["event_type"].replace("_", " "),
                "summary": event["summary"],
            }
        )

    auction_board = []
    for auction in state["auctions"]:
        if auction["year"] != state["current_year"]:
            continue
        auction_board.append(
            {
                "auction_id": auction["auction_id"],
                "label": auction["label"],
                "status": auction["status"],
                "supply": auction["supply"],
                "clearing_price": auction["clearing_price"],
                "bid_count": len(auction["bids"]),
                "results": auction["results"],
            }
        )

    trade_feed = []
    company_trade_book = []
    for trade in state["trades"]:
        trade_feed.append(
            {
                "trade_id": trade["trade_id"],
                "seller_company_id": trade["seller_company_id"],
                "buyer_company_id": trade["buyer_company_id"],
                "quantity": trade["quantity"],
                "price_per_allowance": trade["price_per_allowance"],
                "status": trade["status"],
            }
        )
        if company and (
            trade["seller_company_id"] == company["company_id"]
            or trade["buyer_company_id"] == company["company_id"]
        ):
            company_trade_book.append(deepcopy(trade_feed[-1]))

    return {
        "participant_label": participant_label,
        "phase": state["phase"],
        "phase_label": PHASE_LABELS[state["phase"]],
        "status_text": _status_text(state),
        "countdown_seconds": countdown,
        "current_year": state["current_year"],
        "num_years": state["num_years"],
        "current_cap": state["current_cap"],
        "session_started": state["phase"] != PHASE_LOBBY,
        "session_complete": state["phase"] == PHASE_COMPLETE,
        "can_start": is_facilitator and state["phase"] == PHASE_LOBBY,
        "can_pause": is_facilitator
        and state["phase"]
        in {PHASE_YEAR_START, PHASE_DECISION_WINDOW, PHASE_COMPLIANCE},
        "can_resume": is_facilitator and state["phase"] == PHASE_PAUSED,
        "can_advance_phase": is_facilitator
        and state["phase"]
        in {PHASE_YEAR_START, PHASE_DECISION_WINDOW, PHASE_COMPLIANCE},
        "is_facilitator": is_facilitator,
        "auction_board": auction_board,
        "trade_feed": trade_feed,
        "company": None if company is None else _company_snapshot(state, company),
        "player_company": None if company is None else _company_snapshot(state, company),
        "companies": [] if company is None else [_company_snapshot(state, company)],
        "company_trade_book": company_trade_book,
        "leaderboard": leaderboard,
        "recent_events": recent_events,
        "offset_price": state.get("offset_price", DEFAULT_OFFSET_PRICE),
        "current_offset_price": state.get("current_offset_price", state.get("offset_price", DEFAULT_OFFSET_PRICE)),
        "offset_usage_cap": state.get("offset_usage_cap", DEFAULT_OFFSET_USAGE_CAP),
        "penalty_rate": state.get("penalty_rate", DEFAULT_PENALTY_RATE),
        "last_auction_clearing_price": state.get("last_auction_clearing_price", 0.0),
        "offset_demand_this_year": state.get("offset_demand_this_year", 0.0),
        "annual_offset_supply_cap": state.get("annual_offset_supply_cap", 50.0),
        "vcm_catalog": VCM_CATALOG,
        # 2026-06-30 PHASE-04 — board stat tiles. Headline values for the
        # Vietnam carbon exchange "trading board" view; live/derived from
        # current game state where possible, with `None` for absent data
        # so the UI can render "—" (plan ASM-002).
        "market_board": _build_market_board(state),
        # Sprint 4 — policy climate.
        "policy_stability": state.get("policy_stability", 70.0),
        "policy_climate": _policy_climate_label(state.get("policy_stability", 70.0)),
        "active_conditions": list(state.get("active_conditions", [])),
        "cap_modifier": state.get("cap_modifier", 1.0),
        # Sprint 5 — meta-progression.
        "jurisdiction": state.get("jurisdiction", "vietnam"),
        "xp": state.get("xp", 0),
        "xp_level": state.get("xp_level", 1),
        "xp_thresholds": XP_LEVEL_THRESHOLDS,
        "unlocked_features": list(state.get("unlocked_features", [])),
        "unlock_tree": load_unlock_tree(),
    }


def _policy_climate_label(stability: float) -> str:
    """Banded label for the HUD indicator."""
    if stability < 30:
        return "crisis"
    if stability < 50:
        return "warning"
    if stability > 85:
        return "favorable"
    return "stable"


def build_facilitator_snapshot(
    state: dict[str, Any],
    *,
    now: datetime,
) -> dict[str, Any]:
    current_time = _normalize_time(now)
    deadline = (
        _parse_time(state["phase_deadline_at"]) if state["phase_deadline_at"] else None
    )
    countdown = (
        0
        if deadline is None
        else max(0, int((deadline - current_time).total_seconds()))
    )

    participant_rows = []
    status_map = state.get("participant_status", {})
    for company in state["companies"]:
        cid = company["company_id"]
        entry = status_map.get(cid, {})
        participant_rows.append(
            {
                "company_id": cid,
                "company_name": company["company_name"],
                "sector_label": company["sector"].replace("_", " ").title(),
                "last_seen": entry.get("last_seen"),
                "last_action": entry.get("last_action"),
                "decisions_this_year": entry.get("decision_count_this_year", 0),
                "cash": company["cash"],
                "allowances": company["allowances"],
                "compliance_gap": company["compliance_gap"],
                "cumulative_penalties": company["cumulative_penalties"],
            }
        )

    auction_log = []
    for auction in state["auctions"]:
        auction_log.append(
            {
                "auction_id": auction["auction_id"],
                "year": auction["year"],
                "label": auction["label"],
                "status": auction["status"],
                "supply": auction["supply"],
                "clearing_price": auction["clearing_price"],
                "bid_count": len(auction["bids"]),
            }
        )

    analytics = build_session_analytics(state)
    replay = build_session_replay(state)
    summary = build_session_summary(state)

    return {
        "phase": state["phase"],
        "phase_label": PHASE_LABELS[state["phase"]],
        "current_year": state["current_year"],
        "num_years": state["num_years"],
        "current_cap": state["current_cap"],
        "countdown_seconds": countdown,
        "can_pause": state["phase"]
        in {PHASE_YEAR_START, PHASE_DECISION_WINDOW, PHASE_COMPLIANCE},
        "can_resume": state["phase"] == PHASE_PAUSED,
        "can_advance_phase": state["phase"]
        in {PHASE_YEAR_START, PHASE_DECISION_WINDOW, PHASE_COMPLIANCE},
        "session_complete": state["phase"] == PHASE_COMPLETE,
        "scenario": state.get("scenario", "vietnam_pilot"),
        "bot_count": sum(1 for c in state["companies"] if c.get("is_bot")),
        "active_shocks": state.get("active_shocks", []),
        "participant_rows": participant_rows,
        "auction_log": auction_log,
        "trade_count": len(state["trades"]),
        "audit_log_length": len(state["audit_log"]),
        "session_analytics": analytics,
        "session_replay": replay,
        "session_summary": summary,
    }


def build_session_replay(state: dict[str, Any]) -> dict[str, Any]:
    timeline = [
        {
            "step": index,
            "timestamp": event["timestamp"],
            "year": event.get("year", 0),
            "event_type": event["event_type"],
            "summary": event["summary"],
        }
        for index, event in enumerate(state["audit_log"], start=1)
    ]

    company_paths = [
        {
            "company_id": company["company_id"],
            "company_name": company["company_name"],
            "sector": company["sector"],
            "year_results": deepcopy(company["year_results"]),
        }
        for company in state["companies"]
    ]
    market_path = [
        {
            "auction_id": auction["auction_id"],
            "year": auction["year"],
            "status": auction["status"],
            "clearing_price": auction["clearing_price"],
            "supply": auction["supply"],
        }
        for auction in state["auctions"]
    ]
    return {
        "timeline": timeline,
        "year_markers": _build_year_markers(state),
        "market_path": market_path,
        "company_paths": company_paths,
    }


def build_session_analytics(state: dict[str, Any]) -> dict[str, Any]:
    decision_counts = {}
    for event in state["audit_log"]:
        decision_counts[event["event_type"]] = (
            decision_counts.get(event["event_type"], 0) + 1
        )

    sector_breakdown = []
    for sector in sorted({company["sector"] for company in state["companies"]}):
        companies = [company for company in state["companies"] if company["sector"] == sector]
        sector_breakdown.append(
            {
                "sector": sector,
                "company_count": len(companies),
                "projected_emissions": round(
                    sum(company["projected_emissions"] for company in companies), 2
                ),
                "allowances": round(
                    sum(company["allowances"] for company in companies), 2
                ),
                "banked_allowances": round(
                    sum(company["banked_allowances"] for company in companies), 2
                ),
                "offset_holdings": round(
                    sum(company["offset_holdings"] for company in companies), 2
                ),
                "cumulative_penalties": round(
                    sum(company["cumulative_penalties"] for company in companies), 2
                ),
                "active_abatement_count": sum(
                    len(company["active_abatement_ids"]) for company in companies
                ),
            }
        )

    year_metrics = []
    for marker in _build_year_markers(state):
        year = marker["year"]
        year_results = []
        for company in state["companies"]:
            year_result = next(
                (result for result in company["year_results"] if result["year"] == year),
                None,
            )
            if year_result:
                year_results.append(year_result)
        year_metrics.append(
            {
                "year": year,
                "total_projected_emissions": round(
                    sum(
                        result.get("projected_emissions", result.get("emissions", 0))
                        for result in year_results
                    ),
                    2,
                ),
                "total_allocation": round(
                    sum(result["allocation"] for result in year_results), 2
                ),
                "total_offsets_used": marker["total_offsets_used"],
                "total_banked_allowances": marker["total_banked_allowances"],
                "total_penalties": marker["total_penalties"],
                "average_clearing_price": marker["average_clearing_price"],
                "trade_volume": marker["trade_volume"],
                "shock_count": marker["shock_count"],
            }
        )

    company_costs = []
    for company in state["companies"]:
        company_id = company["company_id"]
        offset_spend = round(
            sum(
                event["details"]["quantity"] * state["offset_price"]
                for event in state["audit_log"]
                if event["event_type"] == "offsets_purchased"
                and event["details"]["company_id"] == company_id
            ),
            2,
        )
        auction_spend = round(
            sum(
                result["payment_due"]
                for auction in state["auctions"]
                for result in auction.get("results", [])
                if result["company_id"] == company_id
            ),
            2,
        )
        trade_purchases = round(
            sum(
                trade["total_value"]
                for trade in state["trades"]
                if trade["status"] == "accepted"
                and trade["buyer_company_id"] == company_id
            ),
            2,
        )
        trade_sales = round(
            sum(
                trade["total_value"]
                for trade in state["trades"]
                if trade["status"] == "accepted"
                and trade["seller_company_id"] == company_id
            ),
            2,
        )
        company_costs.append(
            {
                "company_id": company_id,
                "company_name": company["company_name"],
                "sector": company["sector"],
                "abatement_cost": company["abatement_cost_committed"],
                "offset_spend": offset_spend,
                "auction_spend": auction_spend,
                "trade_purchases": trade_purchases,
                "trade_sales": trade_sales,
                "penalties": company["cumulative_penalties"],
                "net_compliance_cost": round(
                    company["abatement_cost_committed"]
                    + offset_spend
                    + auction_spend
                    + trade_purchases
                    + company["cumulative_penalties"]
                    - trade_sales,
                    2,
                ),
            }
        )

    cleared_auctions = [
        auction
        for auction in state["auctions"]
        if auction["status"] == "cleared" and auction["clearing_price"] > 0
    ]
    accepted_trades = [
        trade for trade in state["trades"] if trade["status"] == "accepted"
    ]
    market_metrics = {
        "total_auction_volume": round(
            sum(
                result["awarded_quantity"]
                for auction in state["auctions"]
                for result in auction.get("results", [])
            ),
            2,
        ),
        "total_trade_volume": round(
            sum(trade["quantity"] for trade in accepted_trades), 2
        ),
        "total_trade_value": round(
            sum(trade["total_value"] for trade in accepted_trades), 2
        ),
        "average_clearing_price": round(
            sum(auction["clearing_price"] for auction in cleared_auctions)
            / len(cleared_auctions),
            2,
        )
        if cleared_auctions
        else 0.0,
        "total_offsets_purchased": round(
            sum(
                event["details"]["quantity"]
                for event in state["audit_log"]
                if event["event_type"] == "offsets_purchased"
            ),
            2,
        ),
        "total_abatement_actions": decision_counts.get("abatement_activated", 0),
        "shock_count": len(state.get("active_shocks", [])),
    }

    return {
        "decision_counts": decision_counts,
        "market_metrics": market_metrics,
        "sector_breakdown": sector_breakdown,
        "year_metrics": year_metrics,
        "company_costs": company_costs,
    }


def export_session_data(state: dict[str, Any]) -> dict[str, Any]:
    companies_export = []
    for company in state["companies"]:
        companies_export.append(
            {
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "sector": company["sector"],
                "baseline_emissions": company["baseline_emissions"],
                "growth_rate": company["growth_rate"],
                "current_year_allocation": company["current_year_allocation"],
                "projected_emissions": company["projected_emissions"],
                "allowances": company["allowances"],
                "banked_allowances": company["banked_allowances"],
                "offset_holdings": company["offset_holdings"],
                "offsets_used_for_compliance": company["offsets_used_for_compliance"],
                "penalty_due": company["penalty_due"],
                "cumulative_penalties": company["cumulative_penalties"],
                "compliance_gap": company["compliance_gap"],
                "cash": company["cash"],
                "abatement_cost_committed": company["abatement_cost_committed"],
                "active_abatement_ids": company["active_abatement_ids"],
                "pending_abatement_ids": company["pending_abatement_ids"],
                "auction_allowances_won": company["auction_allowances_won"],
                "year_results": company["year_results"],
                "is_bot": company.get("is_bot", False),
            }
        )

    return {
        "session_meta": {
            "num_years": state["num_years"],
            "current_year": state["current_year"],
            "phase": state["phase"],
            "penalty_rate": state["penalty_rate"],
            "offset_usage_cap": state["offset_usage_cap"],
            "allocation_factors": state["allocation_factors"],
            "scenario": state.get("scenario", "vietnam_pilot"),
        },
        "companies": companies_export,
        "auctions": [
            {
                "auction_id": auction["auction_id"],
                "year": auction["year"],
                "label": auction["label"],
                "status": auction["status"],
                "supply": auction["supply"],
                "clearing_price": auction["clearing_price"],
                "bid_count": len(auction["bids"]),
                "results": auction.get("results", []),
            }
            for auction in state["auctions"]
        ],
        "trades": [
            {
                "trade_id": trade["trade_id"],
                "year": trade["year"],
                "seller_company_id": trade["seller_company_id"],
                "buyer_company_id": trade["buyer_company_id"],
                "quantity": trade["quantity"],
                "price_per_allowance": trade["price_per_allowance"],
                "status": trade["status"],
            }
            for trade in state["trades"]
        ],
        "audit_log": state["audit_log"],
    }


def build_session_summary(state: dict[str, Any]) -> dict[str, Any]:
    rankings = _build_rankings(state)
    return {
        "scenario": state.get("scenario", "vietnam_pilot"),
        "num_years": state["num_years"],
        "completed_at": state.get("completed_at"),
        "participant_count": state["participant_count"],
        "total_companies": len(state["companies"]),
        "rankings": rankings,
        "facilitator_notes": _facilitator_notes(state),
    }


def _facilitator_notes(state: dict[str, Any]) -> list[str]:
    notes = []
    proj = sum(
        company["projected_emissions"] for company in state["companies"]
    )
    allowances = sum(company["allowances"] for company in state["companies"])
    total_offsets = sum(
        company["offset_holdings"] for company in state["companies"]
    )
    total_penalties = sum(
        company["cumulative_penalties"] for company in state["companies"]
    )

    notes.append(f"Companies: {len(state['companies'])}")
    notes.append(f"Current year: {state['current_year']}/{state['num_years']}")
    notes.append(f"Total projected emissions: {proj:.2f}")
    notes.append(f"Total allowances in circulation: {allowances:.2f}")
    notes.append(f"Total offset holdings: {total_offsets:.2f}")
    notes.append(f"Total cumulative penalties: {total_penalties:.2f}")

    sorted_companies = sorted(
        state["companies"],
        key=lambda c: (c["cumulative_penalties"], c["compliance_gap"]),
    )
    for company in sorted_companies[:3]:
        notes.append(
            f"  {company['company_name']}: "
            f"gap={company['compliance_gap']:.2f}, "
            f"penalties={company['cumulative_penalties']:.2f}"
        )

    return notes


def _build_rankings(state: dict[str, Any]) -> list[dict[str, Any]]:
    rankings = []
    for idx, company in enumerate(
        sorted(
            state["companies"],
            key=lambda c: (
                c["cumulative_penalties"],
                -c["banked_allowances"],
                c["company_name"],
            ),
        ),
        start=1,
    ):
        rankings.append(
            {
                "rank": idx,
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "sector": company["sector"],
                "cumulative_penalties": company["cumulative_penalties"],
                "compliance_gap": company["compliance_gap"],
                "banked_allowances": company["banked_allowances"],
                "cash": company["cash"],
            }
        )
    return rankings


def _tracked_years(state: dict[str, Any]) -> list[int]:
    return sorted(
        {result["year"] for company in state["companies"] for result in company["year_results"]}
    )


def _build_year_markers(state: dict[str, Any]) -> list[dict[str, Any]]:
    markers = []
    for year in _tracked_years(state):
        year_results = [
            result
            for company in state["companies"]
            for result in company["year_results"]
            if result["year"] == year
        ]
        markers.append(
            {
                "year": year,
                "total_allocation": round(
                    sum(result["allocation"] for result in year_results), 2
                ),
                "total_emissions": round(
                    sum(result["emissions"] for result in year_results), 2
                ),
                "total_offsets_used": round(
                    sum(result.get("offsets_used", 0) for result in year_results), 2
                ),
                "total_banked_allowances": round(
                    sum(
                        result.get("banked_allowances", 0) for result in year_results
                    ),
                    2,
                ),
                "total_penalties": round(
                    sum(result.get("penalty_due", 0) for result in year_results), 2
                ),
                "total_auction_spend": round(
                    sum(result.get("auction_spend", 0) for result in year_results), 2
                ),
                "trade_volume": round(
                    sum(result.get("trade_volume", 0) for result in year_results), 2
                ),
                "average_clearing_price": round(
                    sum(
                        result.get("auction_clearing_price", 0)
                        for result in year_results
                    )
                    / len([r for r in year_results if r.get("auction_clearing_price")])
                    if any(r.get("auction_clearing_price") for r in year_results)
                    else 0.0,
                    2,
                ),
                "shock_count": next(
                    (
                        r.get("shock_count", 0)
                        for r in year_results
                        if r.get("shock_count") is not None
                    ),
                    0,
                ),
            }
        )
    return markers


def apply_shock(
    state: dict[str, Any],
    *,
    shock_type: str,
    magnitude: float = 0.1,
    shock_params: dict[str, Any] | None = None,
    now: datetime,
) -> dict[str, Any]:
    if shock_type not in SHOCK_CATALOG:
        raise ValueError(f"Unknown shock type: {shock_type}")

    current_time = _normalize_time(now)

    if shock_type == "emissions_spike":
        for company in state["companies"]:
            increase = round(
                company["projected_emissions"] * abs(magnitude), 2
            )
            company["projected_emissions"] = round(
                company["projected_emissions"] + increase, 2
            )
            company["compliance_gap"] = round(
                company["projected_emissions"]
                - company["allowances"]
                - company["offset_holdings"],
                2,
            )

    elif shock_type == "allowance_withdrawal":
        for company in state["companies"]:
            withdrawn = round(company["allowances"] * abs(magnitude), 2)
            company["allowances"] = round(company["allowances"] - withdrawn, 2)
            company["compliance_gap"] = round(
                company["projected_emissions"]
                - company["allowances"]
                - company["offset_holdings"],
                2,
            )

    elif shock_type == "cost_shock":
        for company in state["companies"]:
            hit = round(company["cash"] * abs(magnitude), 2)
            company["cash"] = round(company["cash"] - hit, 2)

    elif shock_type == "offset_supply_change":
        current_cap = state["offset_usage_cap"]
        new_cap = round(current_cap * (1 + magnitude), 4)
        state["offset_usage_cap"] = max(0.0, min(1.0, new_cap))

    elif shock_type == "tech_unlock":
        from .scenarios import TECH_UNLOCK_TEMPLATES, _scale_tonnage, _scale_money
        params = shock_params or {}
        sector = params.get("sector", "all")
        template_key = params.get("template", "default")
        template = TECH_UNLOCK_TEMPLATES.get(template_key, TECH_UNLOCK_TEMPLATES["default"])
        measure_label = params.get("measure_label", template["measure_label"])
        # Card decks carry RAW (unscaled) abatement_amount/cost. On a Vietnam
        # V-rescaled game these must be scaled to match real measures, or the
        # injected tech unlock delivers ~8 t against 76M-t baselines and is dead
        # weight — which silently skews strategy balance (plan CON-001). Template
        # fallbacks are already scaled, so only param-supplied values are scaled.
        # EU/CA jurisdiction games keep their own raw tonnages (plan DEC-002).
        vn_scaled = state.get("jurisdiction") in (None, "", "vietnam")
        _st = _scale_tonnage if vn_scaled else (lambda x: x)
        _sm = _scale_money if vn_scaled else (lambda x: x)
        abatement_amount = _st(params["abatement_amount"]) if "abatement_amount" in params else template["abatement_amount"]
        cost = _sm(params["cost"]) if "cost" in params else template["cost"]
        activation_timing = params.get("activation_timing", template["activation_timing"])
        new_measure = {
            "measure_id": f"card_{len(state.get('active_shocks', []))}_{state['current_year']}",
            "label": measure_label,
            "abatement_amount": abatement_amount,
            "cost": cost,
            "activation_timing": activation_timing,
        }
        for company in state["companies"]:
            if sector == "all" or company["sector"] == sector:
                existing_ids = {m["measure_id"] for m in company["abatement_menu"]}
                if new_measure["measure_id"] not in existing_ids:
                    company["abatement_menu"].append(deepcopy(new_measure))

    elif shock_type == "fdi_proposal":
        for company in state["companies"]:
            boost = round(company["cash"] * abs(magnitude), 2)
            company["cash"] = round(company["cash"] + boost, 2)

    elif shock_type == "cbam_threat":
        penalty_premium = abs(magnitude)
        current_penalty = state.get("penalty_rate", 200.0)
        state["penalty_rate"] = round(current_penalty * (1 + penalty_premium), 2)

    elif shock_type == "election_pressure":
        adjustment = magnitude
        for year_key in list(state.get("allocation_factors", {}).keys()):
            try:
                year_num = int(year_key)
            except (ValueError, TypeError):
                continue
            if year_num >= state.get("current_year", 1):
                current = state["allocation_factors"][year_key]
                state["allocation_factors"][year_key] = round(
                    max(0.5, min(1.0, current + adjustment)), 4
                )

    elif shock_type == "allowance_boost":
        for company in state["companies"]:
            bonus = round(company["allowances"] * abs(magnitude), 2)
            company["allowances"] = round(company["allowances"] + bonus, 2)
            company["compliance_gap"] = round(
                company["projected_emissions"]
                - company["allowances"]
                - company["offset_holdings"],
                2,
            )

    elif shock_type == "cash_boost":
        for company in state["companies"]:
            bonus = round(company["cash"] * abs(magnitude), 2)
            company["cash"] = round(company["cash"] + bonus, 2)

    shock_entry = {
        "shock_type": shock_type,
        "magnitude": magnitude,
        "applied_at": _serialize_time(current_time),
        "year": state["current_year"],
    }
    state.setdefault("active_shocks", []).append(shock_entry)

    _append_event(
        state,
        "shock_applied",
        current_time,
        {
            "year": state["current_year"],
            "shock_type": shock_type,
            "magnitude": magnitude,
            "description": _event_summary("shock_applied", shock_entry),
        },
    )
    return state


def run_bot_turns(
    state: dict[str, Any],
    *,
    now: datetime,
) -> dict[str, Any]:
    """Drive all bot companies for the current decision window.

    Sprint 3: each bot is planned by a goal-driven ``CompanyAgent`` (see
    ``engine/agents.py``) that looks across a multi-year horizon and uses the
    full instrument stack. This function is the dispatcher — it applies the
    agent's planned actions through the normal reducer so every move is audited
    exactly like a human move. A second pass lets bot buyers respond to any
    bilateral OTC trades proposed to them this turn.
    """
    from .agents import CompanyAgent  # lazy import to avoid circular dependency

    current_time = _normalize_time(now)
    bots = [company for company in state["companies"] if company.get("is_bot")]
    agents = {bot["company_id"]: CompanyAgent.from_company(bot) for bot in bots}

    # Pass 1: each bot plans and acts (including proposing OTC trades).
    for bot in bots:
        agent = agents[bot["company_id"]]
        for action in agent.plan_year(state):
            try:
                apply_company_decision(
                    state,
                    company_id=bot["company_id"],
                    action=action["action"],
                    payload=action.get("payload", {}),
                    now=current_time,
                )
            except (ValueError, KeyError):
                # Greedy plan may include an action that is no longer valid once
                # earlier actions consumed cash/allowances; skip it.
                continue

    # Pass 2: bot buyers respond to open OTC proposals targeting them.
    for trade in state["trades"]:
        if trade["status"] != "proposed":
            continue
        buyer_id = trade["buyer_company_id"]
        agent = agents.get(buyer_id)
        if agent is None:
            continue  # human-targeted proposals are left for the player to answer
        decision = agent.respond_to_trade(state, trade)
        try:
            respond_to_trade(
                state,
                trade_id=trade["trade_id"],
                responder_company_id=buyer_id,
                response=decision,
                now=current_time,
            )
        except ValueError:
            continue

    return state


def ai_market_signals(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Competitor-intelligence summary: each bot's posture and open trades.

    Read-only. Derives a coarse posture from each bot's current compliance gap
    and its strategy's preferred instruments, plus its count of open OTC offers.
    """
    from .agents import CompanyAgent

    signals = []
    for company in state["companies"]:
        if not company.get("is_bot"):
            continue
        agent = CompanyAgent.from_company(company)
        gap = company.get("compliance_gap", 0.0)
        if gap > company.get("projected_emissions", 0.0) * 0.05:
            posture = "covering_shortfall"
        elif gap < 0:
            posture = "banking_surplus"
        else:
            posture = "balanced"
        open_trades = sum(
            1
            for trade in state.get("trades", [])
            if trade["status"] == "proposed"
            and trade["seller_company_id"] == company["company_id"]
        )
        signals.append(
            {
                "company_id": company["company_id"],
                "company_name": company.get("company_name", company["company_id"]),
                "sector_label": company.get("sector", "").replace("_", " ").title(),
                "strategy": agent.risk_appetite,
                "strategy_label": agent.profile.get("label", agent.risk_appetite.title()),
                "posture": posture,
                "preferred_instruments": agent.preferred_instruments,
                "open_trades": open_trades,
                "compliance_gap": round(gap, 2),
            }
        )
    return signals


def _company_snapshot(state: dict[str, Any], company: dict[str, Any]) -> dict[str, Any]:
    return {
        "company_id": company["company_id"],
        "company_name": company["company_name"],
        "sector_label": company["sector"].replace("_", " ").title(),
        "baseline_emissions": company["baseline_emissions"],
        "growth_rate": company["growth_rate"],
        "projected_emissions": company["projected_emissions"],
        "current_year_allocation": company["current_year_allocation"],
        "allowances": company["allowances"],
        "banked_allowances": company["banked_allowances"],
        "offset_holdings": company["offset_holdings"],
        "compliance_gap": company["compliance_gap"],
        "penalty_due": company["penalty_due"],
        "cumulative_penalties": company["cumulative_penalties"],
        "cash": company["cash"],
        "abatement_cost_committed": company["abatement_cost_committed"],
        "abatement_menu": [
            {
                "measure_id": m["measure_id"],
                "label": m["label"],
                "abatement_amount": m["abatement_amount"],
                "cost": m["cost"],
                "activation_timing": m["activation_timing"],
                "active": m["measure_id"] in company["active_abatement_ids"],
                "pending": m["measure_id"] in company["pending_abatement_ids"],
            }
            for m in company["abatement_menu"]
        ],
        "auction_allowances_won": company["auction_allowances_won"],
        "year_results": company["year_results"],
        "forward_contracts": company.get("forward_contracts", []),
        "vcm_projects": company.get("vcm_projects", []),
        "active_abatement_assets": company.get("active_abatement_assets", []),
        "active_loans": company.get("active_loans", []),
        "tech_impaired_ids": company.get("tech_impaired_ids", []),
        "is_bot": company.get("is_bot", False),
    }


def _start_year(state: dict[str, Any], year: int, now: datetime) -> None:
    state["current_year"] = year
    # Migration guards for Sprint 4 fields (legacy saves created pre-PHASE-04).
    state.setdefault("policy_stability", 70.0)
    state.setdefault("active_conditions", [])
    state.setdefault("active_effects", [])
    state.setdefault("pending_card_injections", [])
    state.setdefault("xp", 0)
    state.setdefault("xp_level", 1)
    state.setdefault("unlocked_features", [])
    state.setdefault("jurisdiction", "vietnam")

    # Apply any multi-turn active effects for this year, then decrement them.
    _apply_active_effects(state, now)
    # Policy-stability auto triggers (crackdown / relief) before the cap is set.
    _apply_policy_triggers(state, year, now)

    # Reset demand accumulator and restore base offset price for the new year
    state["offset_demand_this_year"] = 0.0
    state["current_offset_price"] = state.get("offset_price", DEFAULT_OFFSET_PRICE)
    # Retrieve allocation factor supporting both string and integer keys
    factors = state.get("allocation_factors", {})
    allocation_factor = factors.get(year)
    if allocation_factor is None:
        allocation_factor = factors.get(str(year), 0.80)
    # Policy stability modulates the cap: a stable regulator hands out more
    # allowances (relief), an unstable one tightens (crackdown). The modifier is
    # exactly 1.0 at the starting stability of 70, so a fresh game keeps the
    # Sprint 1-3 balance; it only diverges as stability drifts.
    stability = state.get("policy_stability", 70.0)
    cap_modifier = round(1.0 + ((stability - 70.0) / 100.0) * 0.15, 4)
    cap_modifier = max(0.88, min(1.10, cap_modifier))
    state["cap_modifier"] = cap_modifier
    total_baseline = sum(
        company["baseline_emissions"] * (1 + company["growth_rate"]) ** (year - 1)
        for company in state["companies"]
    )
    state["current_cap"] = round(total_baseline * allocation_factor * cap_modifier, 2)

    auction_supply = round(
        state["current_cap"] * state.get("auction_share_of_cap", DEFAULT_AUCTION_SHARE_OF_CAP),
        2,
    )
    free_allocation = round(state["current_cap"] - auction_supply, 2)

    for company in state["companies"]:
        pct = (
            company["baseline_emissions"]
            / total_baseline
            if total_baseline > 0
            else 1.0 / len(state["companies"])
        )
        company["current_year_allocation"] = round(free_allocation * pct, 2)
        company["allowances"] = round(
            company["allowances"] + company["banked_allowances"], 2
        )
        company["allowances"] = round(
            company["allowances"] + company["current_year_allocation"], 2
        )
        company["banked_allowances"] = 0.0
        company["projected_emissions"] = _projected_emissions(company, year)
        company["compliance_gap"] = round(
            company["projected_emissions"]
            - company["allowances"]
            - company["offset_holdings"],
            2,
        )
        company["auction_allowances_won"] = 0.0
        _activate_pending_abatements(company)

        # --- Sprint 5: capex servicing + tech-failure (additive) ---
        company.setdefault("active_abatement_assets", [])
        company.setdefault("active_loans", [])
        company.setdefault("tech_impaired_ids", [])
        _service_abatement_assets(state, company, year, now)
        _recalculate_company_projection(state, company)

        # Deliver maturing forward contracts
        delivered_ids: list[str] = []
        for fc in company.get("forward_contracts", []):
            if fc["delivery_year"] == year:
                company["offset_holdings"] = round(company["offset_holdings"] + fc["quantity"], 2)
                delivered_ids.append(fc["contract_id"])
                _append_event(
                    state,
                    "forward_delivered",
                    now,
                    {
                        "year": year,
                        "company_id": company["company_id"],
                        "quantity": fc["quantity"],
                        "contract_id": fc["contract_id"],
                    },
                )
        if delivered_ids:
            company["forward_contracts"] = [
                fc for fc in company["forward_contracts"] if fc["contract_id"] not in delivered_ids
            ]
            _recalculate_company_projection(state, company)

        # Generate annual VCM project credits
        for proj in company.get("vcm_projects", []):
            if proj["remaining_years"] > 0:
                company["offset_holdings"] = round(
                    company["offset_holdings"] + proj["annual_credits"], 2
                )
                proj["remaining_years"] -= 1
                _append_event(
                    state,
                    "vcm_credits_generated",
                    now,
                    {
                        "year": year,
                        "company_id": company["company_id"],
                        "project_id": proj["project_id"],
                        "credits": proj["annual_credits"],
                        "remaining_years": proj["remaining_years"],
                    },
                )
            if proj["remaining_years"] > 0:
                _recalculate_company_projection(state, company)

    state["auctions"] = [
        a for a in state.get("auctions", []) if a["year"] != year
    ]
    auction_count = state.get("auction_count_per_year", DEFAULT_AUCTION_COUNT)
    per_auction_supply = round(auction_supply / max(auction_count, 1), 2)
    for i in range(auction_count):
        state["auctions"].append(
            {
                "auction_id": f"Y{year}A{i + 1:02d}",
                "label": f"Year {year} Auction {i + 1}",
                "year": year,
                "supply": per_auction_supply,
                "status": "scheduled",
                "bids": [],
                "clearing_price": 0.0,
                "results": [],
                "remaining_supply": per_auction_supply,
                "opened_at": None,
                "closed_at": None,
            }
        )

    _set_phase(state, PHASE_YEAR_START, now)
    _append_event(
        state,
        "year_started",
        now,
        {
            "year": year,
            "cap": state["current_cap"],
            "free_allocation": free_allocation,
            "auction_supply": auction_supply,
        },
    )


def project_outcome(
    state: dict[str, Any],
    *,
    company_id: str,
    action: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Pure function: returns {compliance_gap_delta, cash_delta, notes} for a proposed action.

    Does NOT mutate state. Used by the UI to show projected consequences before commit.
    """
    try:
        company = _get_company(state, company_id)
    except ValueError:
        return {"compliance_gap_delta": 0.0, "cash_delta": 0.0, "notes": []}

    projected = company.get("projected_emissions", 0.0)
    allowances = company.get("allowances", 0.0)
    offset_holdings = company.get("offset_holdings", 0.0)
    offset_cap_pct = state.get("offset_usage_cap", DEFAULT_OFFSET_USAGE_CAP)
    offset_price = state.get("offset_price", DEFAULT_OFFSET_PRICE)
    offset_cap = round(projected * offset_cap_pct, 2)
    current_usable = min(offset_holdings, offset_cap)
    current_gap = round(projected - allowances - current_usable, 2)

    notes: list[str] = []
    new_gap = current_gap
    cash_delta = 0.0

    if action == "activate_abatement":
        measure_id = payload.get("measure_id", "")
        try:
            measure = _get_measure(company, measure_id)
        except ValueError:
            return {"compliance_gap_delta": 0.0, "cash_delta": 0.0, "notes": ["Measure not found"]}
        cost = measure.get("cost", 0.0)
        abatement = measure.get("abatement_amount", 0.0)
        timing = measure.get("activation_timing", "next_year")
        cash_delta = -cost
        if timing == "immediate":
            new_projected = max(projected - abatement, 0.0)
            new_offset_cap = round(new_projected * offset_cap_pct, 2)
            new_usable = min(offset_holdings, new_offset_cap)
            new_gap = round(new_projected - allowances - new_usable, 2)
            notes.append(f"Cuts emissions {abatement:.0f} t this year")
        else:
            notes.append(f"Cuts emissions {abatement:.0f} t from next year")

    elif action == "buy_offsets":
        quantity = float(payload.get("quantity", 0))
        price = float(payload.get("price_per_unit", offset_price))
        cash_delta = -round(quantity * price, 2)
        new_holdings = offset_holdings + quantity
        new_usable = min(new_holdings, offset_cap)
        effective_gain = new_usable - current_usable
        new_gap = round(current_gap - effective_gain, 2)
        if offset_holdings >= offset_cap:
            notes.append(f"Already at cap ({offset_cap:.0f} t max usable) — no compliance benefit")
        elif new_holdings > offset_cap:
            excess = round(new_holdings - offset_cap, 1)
            notes.append(f"{excess:.0f} t excess (above cap, no compliance benefit)")

    elif action == "submit_auction_bid":
        quantity = float(payload.get("quantity", 0))
        price = float(payload.get("price", 0))
        cash_delta = -round(quantity * price, 2)
        new_gap = round(current_gap - quantity, 2)
        notes.append("Assumes bid wins at stated price")

    elif action == "buy_forward":
        quantity = float(payload.get("quantity", 0))
        base_price = state.get("offset_price", DEFAULT_OFFSET_PRICE)
        elasticity = state.get("offset_price_elasticity", 0.4)
        supply_cap = max(state.get("annual_offset_supply_cap", 50.0), 1.0)
        demand = state.get("offset_demand_this_year", 0.0)
        spot_price = round(base_price * (1 + elasticity * min(demand / supply_cap, 1.0)), 2)
        locked_price = round(spot_price * 1.05, 2)
        cash_delta = -round(quantity * locked_price, 2)
        delivery_year = state.get("current_year", 0) + 1
        notes.append(f"Delivers {quantity:.0f} t credits in Year {delivery_year}")
        notes.append(f"Locked at ${locked_price:.2f}/t (spot + 5% premium)")

    elif action == "invest_vcm":
        project_id = payload.get("project_id", "")
        proj_template = next((p for p in VCM_CATALOG if p["project_id"] == project_id), None)
        if not proj_template:
            return {"compliance_gap_delta": 0.0, "cash_delta": 0.0, "notes": ["Project not found"]}
        cash_delta = -proj_template["cost"]
        annual = proj_template["annual_credits"]
        duration = proj_template["duration_years"]
        total = annual * duration
        delivery_year = state.get("current_year", 0) + 1
        notes.append(f"{annual:.0f} t/yr for {duration} yrs = {total:.0f} t total")
        notes.append(f"Credits start Year {delivery_year}")

    gap_delta = round(new_gap - current_gap, 2)
    return {
        "compliance_gap_delta": gap_delta,
        "cash_delta": round(cash_delta, 2),
        "notes": notes,
    }


def generate_year_summary(state: dict[str, Any]) -> str:
    """Template-driven 2-3 sentence narrative for the year-end report screen."""
    player = next((c for c in state.get("companies", []) if not c.get("is_bot")), None)
    if not player or not player.get("year_results"):
        return ""
    latest = player["year_results"][-1]
    year = latest.get("year", state.get("current_year", 0))
    shortfall = latest.get("shortfall", 0.0)
    penalty = latest.get("penalty_due", 0.0)
    banked = latest.get("banked_allowances", 0.0)
    cash = latest.get("cash", player.get("cash", 0.0))

    if shortfall <= 0:
        if banked > 0:
            outcome = (
                f"Year {year} closed with full compliance — "
                f"you banked {banked:.0f} surplus allowances for future years."
            )
        else:
            outcome = f"Year {year} closed with full compliance. Your emissions stayed within the allocated cap."
    elif penalty < 500_000:
        outcome = (
            f"Year {year} closed with a minor shortfall of {shortfall:.0f} t, "
            f"incurring a ${penalty:,.0f} penalty."
        )
    else:
        outcome = (
            f"Year {year} saw a compliance gap of {shortfall:.0f} t — "
            f"a ${penalty:,.0f} penalty has been charged to your budget."
        )

    if cash < 300_000:
        cash_note = "Cash reserves are critically low. Financing options will be constrained next year."
    elif cash > 3_000_000:
        cash_note = "Your cash position is strong, leaving room for strategic investment."
    else:
        cash_note = f"Cash stands at ${cash:,.0f} heading into Year {year + 1}."

    remaining = state.get("num_years", 15) - year
    if remaining > 0:
        factors = state.get("allocation_factors", {})
        next_factor = factors.get(year + 1) or factors.get(str(year + 1))
        if next_factor and next_factor < (factors.get(year) or factors.get(str(year), 1.0)):
            outlook = "The cap tightens next year — plan your abatement and market strategy accordingly."
        else:
            s = "s" if remaining != 1 else ""
            outlook = f"{remaining} compliance year{s} remain in this period."
    else:
        outlook = "This was the final compliance year."

    return f"{outcome} {cash_note} {outlook}"


def _close_current_year(state: dict[str, Any], now: datetime) -> None:
    year = state["current_year"]
    for company in state["companies"]:
        emissions = company["projected_emissions"]
        allowances_held = company["allowances"]
        offset_holdings = company["offset_holdings"]

        offset_cap = round(emissions * state.get("offset_usage_cap", DEFAULT_OFFSET_USAGE_CAP), 2)
        usable_offsets = min(offset_holdings, offset_cap)
        total_cover = round(allowances_held + usable_offsets, 2)
        shortfall = round(emissions - total_cover, 2)

        offsets_used = usable_offsets if shortfall <= 0 else usable_offsets
        if shortfall > 0:
            penalty = round(shortfall * state["penalty_rate"], 2)
            company["penalty_due"] = penalty
            company["cumulative_penalties"] = round(
                company["cumulative_penalties"] + penalty, 2
            )
            company["cash"] = round(company["cash"] - penalty, 2)
        else:
            company["penalty_due"] = 0.0

        remaining_allowances = round(total_cover - emissions, 2)
        if remaining_allowances > 0:
            company["banked_allowances"] = round(
                company["banked_allowances"] + remaining_allowances, 2
            )

        company["offset_holdings"] = round(
            company["offset_holdings"] - offsets_used, 2
        )
        company["offsets_used_for_compliance"] = round(
            company["offsets_used_for_compliance"] + offsets_used, 2
        )
        company["allowances"] = 0.0

        year_result = {
            "year": year,
            "allocation": company["current_year_allocation"],
            "emissions": emissions,
            "allowances_held": allowances_held,
            "offset_holdings": company["offset_holdings"],
            "offsets_used": offsets_used,
            "shortfall": round(max(shortfall, 0), 2),
            "penalty_due": company["penalty_due"],
            "banked_allowances": company["banked_allowances"],
            "cash": company["cash"],
            "auction_spend": company["auction_allowances_won"],
            "auction_clearing_price": 0.0,
            "trade_volume": round(
                sum(
                    trade["quantity"]
                    for trade in state["trades"]
                    if trade["year"] == year and trade["status"] == "accepted"
                    and (
                        trade["seller_company_id"] == company["company_id"]
                        or trade["buyer_company_id"] == company["company_id"]
                    )
                ),
                2,
            ),
        }
        company["year_results"].append(year_result)

    cleared = [
        a for a in state["auctions"] if a["year"] == year and a["status"] == "cleared"
    ]
    if cleared:
        state["last_auction_clearing_price"] = round(
            max(a["clearing_price"] for a in cleared), 2
        )
    for auction in cleared:
        for company in state["companies"]:
            for result in company["year_results"]:
                if result["year"] != year:
                    continue
                current = result.get("auction_clearing_price", 0) or 0
                result["auction_clearing_price"] = round(
                    max(current, auction["clearing_price"]), 2
                )

    _append_event(
        state,
        "year_closed",
        now,
        {
            "year": year,
            "total_penalties": round(
                sum(c["penalty_due"] for c in state["companies"]), 2
            ),
            "total_banked": round(
                sum(c["banked_allowances"] for c in state["companies"]), 2
            ),
        },
    )

    _update_policy_stability(state, year, now)
    _award_year_xp(state, year, now)


def _award_year_xp(state: dict[str, Any], year: int, now: datetime) -> None:
    """Grant the human player XP for this year's outcome (TASK-05-05)."""
    player = next((c for c in state.get("companies", []) if not c.get("is_bot")), None)
    if not player or not player.get("year_results"):
        return
    latest = player["year_results"][-1]
    if latest.get("penalty_due", 0) <= 0 and latest.get("shortfall", 0) <= 0:
        award_xp(state, "penalty_free_year")
        # First-ever compliant year carries a one-off bonus.
        if not state.get("_first_compliance_awarded"):
            award_xp(state, "first_compliance")
            state["_first_compliance_awarded"] = True


def _update_policy_stability(state: dict[str, Any], year: int, now: datetime) -> None:
    """Adjust policy_stability from this year's compliance outcomes (TASK-04-01).

    +5 if aggregate compliance rate > 80%; +3 more above 85%; -10 if more than
    30% of companies paid penalties; -15 if an election_pressure shock fired this
    year. Clamped to [0, 100].
    """
    state.setdefault("policy_stability", 70.0)
    companies = state.get("companies", [])
    if not companies:
        return
    n = len(companies)
    compliant = sum(
        1
        for c in companies
        if (c["year_results"][-1]["shortfall"] if c.get("year_results") else 0) <= 0
    )
    penalized = sum(
        1
        for c in companies
        if (c["year_results"][-1]["penalty_due"] if c.get("year_results") else 0) > 0
    )
    compliance_rate = compliant / n
    penalty_rate_frac = penalized / n

    before = state["policy_stability"]
    # Mean reversion toward a neutral baseline keeps stability from pinning at an
    # extreme (a permanent death-spiral or runaway relief) when the field is
    # structurally over- or under-compliant; the outcome deltas then push around
    # that baseline.
    delta = (60.0 - before) * 0.10
    if compliance_rate > 0.80:
        delta += 4.0
    if compliance_rate > 0.85:
        delta += 2.0
    if penalty_rate_frac > 0.30:
        delta -= 6.0
    # An election_pressure shock applied this year shakes regulatory confidence.
    if any(
        s.get("shock_type") == "election_pressure" and s.get("year") == year
        for s in state.get("active_shocks", [])
    ):
        delta -= 10.0

    state["policy_stability"] = round(max(0.0, min(100.0, before + delta)), 2)
    if state["policy_stability"] != before:
        _append_event(
            state,
            "policy_stability_changed",
            now,
            {
                "year": year,
                "before": before,
                "after": state["policy_stability"],
                "delta": round(state["policy_stability"] - before, 2),
                "compliance_rate": round(compliance_rate, 2),
            },
        )


def _service_abatement_assets(
    state: dict[str, Any], company: dict[str, Any], year: int, now: datetime
) -> None:
    """Annual capex servicing (TASK-05-02/03/04): opex, loan payments, tech rolls.

    Runs once per company at year start. Restores last year's tech impairment
    (it lasts one year), then rolls new failures with the seeded RNG, deducts
    annual opex for active assets, and amortizes outstanding loans.
    """
    # Tech impairment lasts one year — clear last year's, then roll fresh ones.
    company["tech_impaired_ids"] = []
    rng = _deterministic_rng(state, f"techfail-{company['company_id']}-{year}")
    for asset in company.get("active_abatement_assets", []):
        asset["remaining_life"] = asset.get("remaining_life", 8) - 1
        # Opex only while the asset is live and actually abating.
        if asset["measure_id"] in company["active_abatement_ids"]:
            opex = asset.get("annual_opex", 0.0)
            if opex:
                company["cash"] = round(company["cash"] - opex, 2)
            risk = asset.get("tech_risk_pct", 0.0)
            if risk > 0 and rng.random() < risk:
                company["tech_impaired_ids"].append(asset["measure_id"])
                _append_event(
                    state, "tech_failure", now,
                    {"year": year, "company_id": company["company_id"],
                     "measure_id": asset["measure_id"]},
                )

    # Amortize outstanding loans.
    surviving_loans = []
    for loan in company.get("active_loans", []):
        if loan.get("remaining_years", 0) > 0:
            company["cash"] = round(company["cash"] - loan["annual_payment"], 2)
            loan["remaining_years"] -= 1
        if loan.get("remaining_years", 0) > 0:
            surviving_loans.append(loan)
    company["active_loans"] = surviving_loans


def _deterministic_rng(state: dict[str, Any], salt: str) -> "_random.Random":
    """A reproducible RNG derived from the game seed plus a salt string."""
    base = state.get("rng_seed", 0)
    return _random.Random(f"{base}-{salt}")


def award_xp(state: dict[str, Any], event_type: str) -> int:
    """Award XP for a game event and recompute level (TASK-05-05).

    Returns the points awarded. Levels follow XP_LEVEL_THRESHOLDS.
    """
    from .achievements import XP_EVENT_POINTS

    points = XP_EVENT_POINTS.get(event_type, 0)
    if points == 0:
        return 0
    state["xp"] = int(state.get("xp", 0)) + points
    new_level = 1
    for i, threshold in enumerate(XP_LEVEL_THRESHOLDS):
        if state["xp"] >= threshold:
            new_level = i + 1
    state["xp_level"] = new_level
    return points


def _apply_active_effects(state: dict[str, Any], now: datetime) -> None:
    """Re-apply multi-turn card effects for the new year, then decrement them.

    Each entry is ``{effect_type, effect_params, remaining_years}``. The effect
    is applied through the normal shock pipeline once per active year; entries
    reaching zero remaining years are dropped.
    """
    effects = state.get("active_effects", [])
    if not effects:
        return
    surviving: list[dict[str, Any]] = []
    for effect in effects:
        etype = effect.get("effect_type", "none")
        remaining = effect.get("remaining_years", 0)
        if etype != "none" and remaining > 0:
            params = dict(effect.get("effect_params", {}))
            magnitude = params.pop("magnitude", 0.1)
            try:
                apply_shock(
                    state,
                    shock_type=etype,
                    magnitude=magnitude,
                    shock_params=params,
                    now=now,
                )
            except ValueError:
                pass
        effect["remaining_years"] = remaining - 1
        if effect["remaining_years"] > 0:
            surviving.append(effect)
    state["active_effects"] = surviving


def _apply_policy_triggers(state: dict[str, Any], year: int, now: datetime) -> None:
    """Auto crackdown / relief when policy_stability crosses thresholds (TASK-04-02).

    Implemented engine-side (deterministic, no deck dependency): a crackdown sets
    the ``regulatory_crackdown`` condition and raises the penalty rate for the
    year; relief sets ``policy_relief`` and grants a one-off allowance boost. The
    matching narrative cards also exist in the deck for the drawn path.
    """
    stability = state.get("policy_stability", 70.0)
    conditions = state.setdefault("active_conditions", [])

    if stability < 30 and "regulatory_crackdown" not in conditions:
        conditions.append("regulatory_crackdown")
        conditions[:] = [c for c in conditions if c != "policy_relief"]
        # One-time allowance withdrawal — a non-ratcheting hit. (Deliberately not
        # cbam_threat, which permanently multiplies penalty_rate and compounds
        # into a death-spiral when the crackdown card is re-drawn each year.)
        apply_shock(state, shock_type="allowance_withdrawal", magnitude=0.08, now=now)
        _append_event(
            state,
            "policy_climate_shift",
            now,
            {"year": year, "shift": "regulatory_crackdown", "policy_stability": stability},
        )
    elif stability > 85 and "policy_relief" not in conditions:
        conditions.append("policy_relief")
        conditions[:] = [c for c in conditions if c != "regulatory_crackdown"]
        apply_shock(state, shock_type="allowance_boost", magnitude=0.08, now=now)
        _append_event(
            state,
            "policy_climate_shift",
            now,
            {"year": year, "shift": "policy_relief", "policy_stability": stability},
        )
    elif 30 <= stability <= 85:
        # Climate normalised — clear the extreme conditions.
        conditions[:] = [
            c for c in conditions if c not in ("regulatory_crackdown", "policy_relief")
        ]


def _projected_emissions(company: dict[str, Any], year: int) -> float:
    base = company["baseline_emissions"] * (1 + company["growth_rate"]) ** (year - 1)
    impaired = set(company.get("tech_impaired_ids", []))
    for measure in company["abatement_menu"]:
        if measure["measure_id"] in company["active_abatement_ids"]:
            # A tech-failed asset delivers only half its abatement this year.
            factor = 0.5 if measure["measure_id"] in impaired else 1.0
            base -= measure["abatement_amount"] * factor
    return round(max(base, 0), 2)


def _set_phase(state: dict[str, Any], phase: str, now: datetime) -> None:
    duration = state.get("phase_durations", DEFAULT_PHASE_DURATIONS).get(phase, 10)
    state["phase"] = phase
    state["phase_started_at"] = _serialize_time(now)
    state["phase_deadline_at"] = _serialize_time(
        now + timedelta(minutes=duration)
    )


def _append_event(
    state: dict[str, Any],
    event_type: str,
    timestamp: datetime,
    details: dict[str, Any],
) -> None:
    state["audit_log"].append(
        {
            "timestamp": _serialize_time(timestamp),
            "year": state.get("current_year", 0),
            "event_type": event_type,
            "details": details,
            "summary": _event_summary(event_type, details),
        }
    )


def _event_summary(event_type: str, details: dict[str, Any]) -> str:
    if event_type == "year_started":
        return f"Year {details['year']} began with cap {details['cap']:.2f} (free: {details['free_allocation']:.2f}, auction: {details['auction_supply']:.2f})"
    if event_type == "year_closed":
        return f"Year {details['year']} closed - all-company penalties: {details['total_penalties']:.2f}, banked: {details['total_banked']:.2f}"
    if event_type == "decision_window_opened":
        return "Decision window opened"
    if event_type == "abatement_activated":
        return f"Abatement {details['measure_id']} activated for {details['company_id']}"
    if event_type == "offsets_purchased":
        return f"{details['company_id']} bought {details['quantity']:.2f} offset tonnes"
    if event_type == "auction_opened":
        return f"Auction {details['auction_id']} opened"
    if event_type == "auction_bid_submitted":
        return f"{details['company_id']} bid {details['quantity']:.2f} @ {details['price']:.2f} in {details['auction_id']}"
    if event_type == "auction_cleared":
        return f"Auction {details['auction_id']} cleared at {details['clearing_price']:.2f} for {details['cleared_quantity']:.2f} tonnes"
    if event_type == "trade_proposed":
        return f"Trade {details['trade_id']}: {details['seller_company_id']} -> {details['buyer_company_id']} {details['quantity']:.2f} @ {details['price_per_allowance']:.2f}"
    if event_type == "trade_accepted":
        return f"Trade {details['trade_id']} accepted: {details['quantity']:.2f} @ {details['price_per_allowance']:.2f}"
    if event_type == "trade_rejected":
        return f"Trade {details['trade_id']} rejected"
    if event_type == "session_paused":
        return f"Session paused in year {details['year']}"
    if event_type == "session_resumed":
        return f"Session resumed in year {details['year']}"
    if event_type == "session_completed":
        return "Session completed"
    if event_type == "phase_force_advanced":
        return f"Phase force-advanced from {details.get('from_phase', 'unknown')} in year {details['year']}"
    if event_type == "shock_applied":
        return f"Shock '{details['shock_type']}' (magnitude {details['magnitude']}) applied in year {details['year']}"
    if event_type == "policy_stability_changed":
        return f"Policy stability {details['before']:.0f} -> {details['after']:.0f} ({details['delta']:+.0f}) in year {details['year']}"
    if event_type == "policy_climate_shift":
        return f"Policy climate shift: {details['shift'].replace('_', ' ')} in year {details['year']}"
    if event_type == "abatement_financed":
        return f"{details['company_id']} financed {details['measure_id']} (loan ${details['annual_payment']:,.0f}/yr x {details['term']}y)"
    if event_type == "tech_failure":
        return f"Tech failure on {details['measure_id']} for {details['company_id']} in year {details['year']}"
    if event_type == "card_resolved":
        title = details.get("title", details.get("card_id", "unknown"))
        return f"Event card '{title}' resolved in year {details['year']}"
    if event_type == "card_drawn":
        title = details.get("title", details.get("card_id", "unknown"))
        return f"Event card '{title}' drawn in year {details['year']}"
    return f"{event_type}: {details}"


def _status_text(state: dict[str, Any]) -> str:
    texts = {
        PHASE_LOBBY: "Waiting for facilitator to start the session...",
        PHASE_YEAR_START: f"Year {state['current_year']} is starting — get ready!",
        PHASE_DECISION_WINDOW: f"Decision window open — make your abatement, offset, auction, and trade choices for Year {state['current_year']}",
        PHASE_COMPLIANCE: f"Year {state['current_year']} is closing — compliance results pending...",
        PHASE_COMPLETE: "Session complete! Check the leaderboard and facilitator panel for final results.",
        PHASE_PAUSED: "Session paused by facilitator. Waiting for resume...",
    }
    return texts.get(state["phase"], f"Phase: {state['phase']}")


def _build_market_board(state: dict[str, Any]) -> dict[str, Any]:
    """Headline values for the Vietnam carbon exchange 'trading board' view
    (plan 2026-06-30 PHASE-04). Live/derived from current state where
    possible; `None` for absent data so the UI can render "—".

    Fields:
      * total_allocated_quota (tCO2e)  — sum of company baseline × current
        year's allocation factor. For Vietnam this lands on
        VN_NATIONAL_ALLOCATION_TCO2E (511,473,846) by design (PHASE-01).
      * latest_execution_price (đ/tCO2e) — last auction clearing price if
        any auction has cleared, else the live offset price.
      * total_trade_volume (tCO2e)     — sum of accepted OTC trade qty.
      * total_trade_value (đ)          — sum of accepted OTC trade total.
      * best_bid (đ/tCO2e)             — max live bid across open
        auctions. None when no auction is open or no bid submitted.
      * lowest_offer (đ/tCO2e)         — min price_per_allowance across
        open OTC trades. None when no OTC offer is open.
    """
    from .constants import VN_NATIONAL_ALLOCATION_TCO2E

    companies = state.get("companies", [])
    if not companies:
        return {
            "total_allocated_quota": 0.0,
            "latest_execution_price": None,
            "total_trade_volume": 0.0,
            "total_trade_value": 0.0,
            "best_bid": None,
            "lowest_offer": None,
        }

    current_year = state.get("current_year", 1)
    factors = state.get("allocation_factors", {}) or {}
    year_factor = factors.get(current_year) or factors.get(str(current_year)) or 1.0
    jurisdiction = state.get("jurisdiction", "vietnam")
    if jurisdiction == "vietnam":
        # Headline tile: Vietnam is anchored to the real national quota.
        total_quota = float(VN_NATIONAL_ALLOCATION_TCO2E)
    else:
        # EU/CA keep their own realistic totals.
        total_quota = round(
            sum(co.get("baseline_emissions", 0.0) * year_factor for co in companies),
            2,
        )

    last_auction = state.get("last_auction_clearing_price") or 0.0
    if last_auction > 0:
        latest_execution = float(last_auction)
    else:
        latest_execution = float(
            state.get("current_offset_price")
            or state.get("offset_price")
            or DEFAULT_OFFSET_PRICE
        )

    accepted = [t for t in state.get("trades", []) if t.get("status") == "accepted"]
    total_volume = round(sum(t.get("quantity", 0.0) for t in accepted), 2)
    total_value = round(sum(t.get("total_value", 0.0) for t in accepted), 2)

    best_bid: float | None = None
    for auction in state.get("auctions", []):
        if auction.get("status") != "open":
            continue
        for bid in auction.get("bids", []) or []:
            price = bid.get("price")
            if price is None:
                continue
            best_bid = price if best_bid is None else max(best_bid, price)

    lowest_offer: float | None = None
    for trade in state.get("trades", []):
        if trade.get("status") != "open":
            continue
        price = trade.get("price_per_allowance")
        if price is None:
            continue
        lowest_offer = price if lowest_offer is None else min(lowest_offer, price)

    return {
        "total_allocated_quota": total_quota,
        "latest_execution_price": latest_execution,
        "total_trade_volume": total_volume,
        "total_trade_value": total_value,
        "best_bid": best_bid,
        "lowest_offer": lowest_offer,
    }


def _get_company(state: dict[str, Any], company_id: str) -> dict[str, Any]:
    for company in state["companies"]:
        if company["company_id"] == company_id:
            return company
    raise ValueError(f"Company not found: {company_id}")


def _get_measure(company: dict[str, Any], measure_id: str) -> dict[str, Any]:
    for measure in company["abatement_menu"]:
        if measure["measure_id"] == measure_id:
            return measure
    raise ValueError(f"Measure not found: {measure_id}")


def _get_auction(state: dict[str, Any], auction_id: str) -> dict[str, Any]:
    for auction in state["auctions"]:
        if auction["auction_id"] == auction_id:
            return auction
    raise ValueError(f"Auction not found: {auction_id}")


def _get_trade(state: dict[str, Any], trade_id: str) -> dict[str, Any]:
    for trade in state["trades"]:
        if trade["trade_id"] == trade_id:
            return trade
    raise ValueError(f"Trade not found: {trade_id}")


def _build_year_auctions(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        auction
        for auction in state.get("auctions", [])
        if auction["year"] == state["current_year"]
    ]


def _activate_pending_abatements(company: dict[str, Any]) -> None:
    for measure in company["abatement_menu"]:
        if measure["measure_id"] in company["pending_abatement_ids"]:
            company["pending_abatement_ids"].remove(measure["measure_id"])
            company["active_abatement_ids"].append(measure["measure_id"])


def _recalculate_company_projection(
    state: dict[str, Any], company: dict[str, Any]
) -> None:
    year = state["current_year"]
    company["projected_emissions"] = _projected_emissions(company, year)
    company["compliance_gap"] = round(
        company["projected_emissions"]
        - company["allowances"]
        - company["offset_holdings"],
        2,
    )


def _expire_trades(state: dict[str, Any], now: datetime) -> None:
    current_time = _normalize_time(now)
    for trade in state["trades"]:
        if trade["status"] != "proposed":
            continue
        if _parse_time(trade["expires_at"]) <= current_time:
            trade["status"] = "expired"


def _serialize_time(value: datetime) -> str:
    return value.isoformat()


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _normalize_time(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
