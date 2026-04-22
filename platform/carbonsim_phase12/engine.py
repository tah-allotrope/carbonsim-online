from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any


PHASE_LOBBY = "lobby"
PHASE_YEAR_START = "year_start"
PHASE_DECISION_WINDOW = "decision_window"
PHASE_COMPLIANCE = "compliance"
PHASE_COMPLETE = "complete"
PHASE_PAUSED = "paused"

DEFAULT_PHASE_DURATIONS = {
    PHASE_YEAR_START: 5,
    PHASE_DECISION_WINDOW: 20,
    PHASE_COMPLIANCE: 5,
}

DEFAULT_OFFSET_USAGE_CAP = 0.1
DEFAULT_AUCTION_COUNT = 2
DEFAULT_AUCTION_PRICE_FLOOR = 80.0
DEFAULT_AUCTION_PRICE_CEILING = 300.0
DEFAULT_AUCTION_SHARE_OF_CAP = 0.12
DEFAULT_TRADE_EXPIRY_SECONDS = 20
DEFAULT_OFFSET_PRICE = 25.0
DEFAULT_PENALTY_RATE = 200.0

SCENARIO_PACKS = {
    "vietnam_pilot": {
        "label": "Vietnam Pilot (Default)",
        "description": "Three-year arc with tightening allocation, sector-specific abatement, and limited offsets aligned with Vietnam's pilot ETS posture.",
        "num_years": 3,
        "penalty_rate": 200.0,
        "offset_usage_cap": 0.1,
        "offset_price": 25.0,
        "auction_count_per_year": 2,
        "auction_price_floor": 80.0,
        "auction_price_ceiling": 300.0,
        "auction_share_of_cap": 0.12,
        "trade_expiry_seconds": 20,
        "allocation_factors": {1: 0.92, 2: 0.88, 3: 0.84},
        "company_library": [
            {
                "company_name": "Red River Thermal",
                "sector": "thermal_power",
                "baseline_emissions": 120.0,
                "growth_rate": 0.030,
                "cash": 1_500_000.0,
            },
            {
                "company_name": "Hai Phong Steel",
                "sector": "steel",
                "baseline_emissions": 95.0,
                "growth_rate": 0.022,
                "cash": 1_250_000.0,
            },
            {
                "company_name": "Da Nang Cement",
                "sector": "cement",
                "baseline_emissions": 88.0,
                "growth_rate": 0.018,
                "cash": 1_050_000.0,
            },
        ],
        "abatement_catalog": {
            "thermal_power": [
                {
                    "measure_id": "tp_heat_rate_upgrade",
                    "label": "Heat-rate upgrade",
                    "abatement_amount": 10.0,
                    "cost": 90000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "tp_cofiring_preparation",
                    "label": "Biomass cofiring preparation",
                    "abatement_amount": 7.0,
                    "cost": 65000.0,
                    "activation_timing": "next_year",
                },
            ],
            "steel": [
                {
                    "measure_id": "st_waste_heat_recovery",
                    "label": "Waste heat recovery",
                    "abatement_amount": 8.0,
                    "cost": 72000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "st_scrap_optimization",
                    "label": "Scrap ratio optimization",
                    "abatement_amount": 5.0,
                    "cost": 50000.0,
                    "activation_timing": "next_year",
                },
            ],
            "cement": [
                {
                    "measure_id": "ce_blended_clinker_shift",
                    "label": "Blended clinker shift",
                    "abatement_amount": 6.0,
                    "cost": 46000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "ce_kiln_control_upgrade",
                    "label": "Kiln control upgrade",
                    "abatement_amount": 4.0,
                    "cost": 38000.0,
                    "activation_timing": "next_year",
                },
            ],
        },
    },
    "high_pressure": {
        "label": "High Pressure",
        "description": "Sharper cap decline and higher penalty rate forces aggressive abatement and trading.",
        "num_years": 3,
        "penalty_rate": 350.0,
        "offset_usage_cap": 0.05,
        "offset_price": 40.0,
        "auction_count_per_year": 2,
        "auction_price_floor": 100.0,
        "auction_price_ceiling": 400.0,
        "auction_share_of_cap": 0.15,
        "trade_expiry_seconds": 20,
        "allocation_factors": {1: 0.90, 2: 0.82, 3: 0.74},
        "company_library": [
            {
                "company_name": "Red River Thermal",
                "sector": "thermal_power",
                "baseline_emissions": 120.0,
                "growth_rate": 0.035,
                "cash": 1_400_000.0,
            },
            {
                "company_name": "Hai Phong Steel",
                "sector": "steel",
                "baseline_emissions": 95.0,
                "growth_rate": 0.025,
                "cash": 1_150_000.0,
            },
            {
                "company_name": "Da Nang Cement",
                "sector": "cement",
                "baseline_emissions": 88.0,
                "growth_rate": 0.020,
                "cash": 950_000.0,
            },
        ],
        "abatement_catalog": {
            "thermal_power": [
                {
                    "measure_id": "tp_heat_rate_upgrade",
                    "label": "Heat-rate upgrade",
                    "abatement_amount": 10.0,
                    "cost": 90000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "tp_cofiring_preparation",
                    "label": "Biomass cofiring preparation",
                    "abatement_amount": 7.0,
                    "cost": 65000.0,
                    "activation_timing": "next_year",
                },
            ],
            "steel": [
                {
                    "measure_id": "st_waste_heat_recovery",
                    "label": "Waste heat recovery",
                    "abatement_amount": 8.0,
                    "cost": 72000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "st_scrap_optimization",
                    "label": "Scrap ratio optimization",
                    "abatement_amount": 5.0,
                    "cost": 50000.0,
                    "activation_timing": "next_year",
                },
            ],
            "cement": [
                {
                    "measure_id": "ce_blended_clinker_shift",
                    "label": "Blended clinker shift",
                    "abatement_amount": 6.0,
                    "cost": 46000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "ce_kiln_control_upgrade",
                    "label": "Kiln control upgrade",
                    "abatement_amount": 4.0,
                    "cost": 38000.0,
                    "activation_timing": "next_year",
                },
            ],
        },
    },
    "generous": {
        "label": "Generous Allocation",
        "description": "Gentler cap decline with lower penalties, suitable for introductory workshops where the learning focus is on market mechanics.",
        "num_years": 3,
        "penalty_rate": 120.0,
        "offset_usage_cap": 0.15,
        "offset_price": 18.0,
        "auction_count_per_year": 2,
        "auction_price_floor": 50.0,
        "auction_price_ceiling": 250.0,
        "auction_share_of_cap": 0.10,
        "trade_expiry_seconds": 25,
        "allocation_factors": {1: 0.95, 2: 0.92, 3: 0.89},
        "company_library": [
            {
                "company_name": "Red River Thermal",
                "sector": "thermal_power",
                "baseline_emissions": 120.0,
                "growth_rate": 0.025,
                "cash": 1_600_000.0,
            },
            {
                "company_name": "Hai Phong Steel",
                "sector": "steel",
                "baseline_emissions": 95.0,
                "growth_rate": 0.018,
                "cash": 1_350_000.0,
            },
            {
                "company_name": "Da Nang Cement",
                "sector": "cement",
                "baseline_emissions": 88.0,
                "growth_rate": 0.015,
                "cash": 1_150_000.0,
            },
        ],
        "abatement_catalog": {
            "thermal_power": [
                {
                    "measure_id": "tp_heat_rate_upgrade",
                    "label": "Heat-rate upgrade",
                    "abatement_amount": 12.0,
                    "cost": 85000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "tp_cofiring_preparation",
                    "label": "Biomass cofiring preparation",
                    "abatement_amount": 8.0,
                    "cost": 55000.0,
                    "activation_timing": "next_year",
                },
            ],
            "steel": [
                {
                    "measure_id": "st_waste_heat_recovery",
                    "label": "Waste heat recovery",
                    "abatement_amount": 9.0,
                    "cost": 68000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "st_scrap_optimization",
                    "label": "Scrap ratio optimization",
                    "abatement_amount": 6.0,
                    "cost": 42000.0,
                    "activation_timing": "next_year",
                },
            ],
            "cement": [
                {
                    "measure_id": "ce_blended_clinker_shift",
                    "label": "Blended clinker shift",
                    "abatement_amount": 7.0,
                    "cost": 38000.0,
                    "activation_timing": "immediate",
                },
                {
                    "measure_id": "ce_kiln_control_upgrade",
                    "label": "Kiln control upgrade",
                    "abatement_amount": 5.0,
                    "cost": 32000.0,
                    "activation_timing": "next_year",
                },
            ],
        },
    },
}

SHOCK_CATALOG = {
    "emissions_spike": {
        "label": "Emissions Spike",
        "description": "Increase projected emissions for all companies in the current year by a percentage, simulating an unexpected production surge.",
        "applies_to": "all_companies",
    },
    "allowance_withdrawal": {
        "label": "Allowance Withdrawal",
        "description": "Reduce current allowance holdings by a percentage, simulating a regulatory correction or pre-verification adjustment.",
        "applies_to": "all_companies",
    },
    "cost_shock": {
        "label": "Cost Shock",
        "description": "Reduce cash for all companies by a percentage, simulating an external financial shock.",
        "applies_to": "all_companies",
    },
    "offset_supply_change": {
        "label": "Offset Supply Change",
        "description": "Change the offset usage cap for the current year, simulating policy changes to offset eligibility.",
        "applies_to": "session_wide",
    },
}

BOT_STRATEGY_CONSERVATIVE = "conservative"
BOT_STRATEGY_MODERATE = "moderate"
BOT_STRATEGY_AGGRESSIVE = "aggressive"

BOT_STRATEGIES = {
    BOT_STRATEGY_CONSERVATIVE: {
        "label": "Conservative",
        "description": "Activates cheap abatement early, buys small offsets to cover gap, bids conservatively in auctions, avoids trades.",
        "abatement_threshold_fraction": 0.5,
        "offset_gap_fraction": 0.3,
        "auction_bid_fraction": 0.6,
        "trade_likelihood": 0.0,
    },
    BOT_STRATEGY_MODERATE: {
        "label": "Moderate",
        "description": "Activates all immediate abatement, buys offsets for half the remaining gap, bids at mid-range in auctions, occasionally trades.",
        "abatement_threshold_fraction": 1.0,
        "offset_gap_fraction": 0.5,
        "auction_bid_fraction": 0.8,
        "trade_likelihood": 0.3,
    },
    BOT_STRATEGY_AGGRESSIVE: {
        "label": "Aggressive",
        "description": "Activates all abatement, buys offsets aggressively, bids high in auctions, actively seeks trades.",
        "abatement_threshold_fraction": 1.0,
        "offset_gap_fraction": 0.8,
        "auction_bid_fraction": 1.0,
        "trade_likelihood": 0.5,
    },
}

YEARLY_ALLOCATION_FACTORS = {
    1: 0.92,
    2: 0.88,
    3: 0.84,
}

COMPANY_LIBRARY = SCENARIO_PACKS["vietnam_pilot"]["company_library"]

ABATEMENT_CATALOG = SCENARIO_PACKS["vietnam_pilot"]["abatement_catalog"]

PHASE_LABELS = {
    PHASE_LOBBY: "Lobby",
    PHASE_YEAR_START: "Year Start",
    PHASE_DECISION_WINDOW: "Decision Window",
    PHASE_COMPLIANCE: "Compliance Review",
    PHASE_COMPLETE: "Session Complete",
    PHASE_PAUSED: "Paused",
}


def build_company_specs(participant_count: int) -> list[dict[str, Any]]:
    specs = []
    for index in range(participant_count):
        base = deepcopy(COMPANY_LIBRARY[index % len(COMPANY_LIBRARY)])
        cohort = index // len(COMPANY_LIBRARY)
        suffix = "" if cohort == 0 else f" {cohort + 1}"
        base["company_id"] = f"C{index + 1:02d}"
        base["company_name"] = f"{base['company_name']}{suffix}"
        base["baseline_emissions"] = round(
            base["baseline_emissions"] * (1 + (cohort * 0.04)), 2
        )
        base["cash"] = round(base["cash"] + (cohort * 175_000), 2)
        specs.append(base)
    return specs


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
) -> dict[str, Any]:
    pack = SCENARIO_PACKS.get(
        scenario or "vietnam_pilot", SCENARIO_PACKS["vietnam_pilot"]
    )
    durations = dict(DEFAULT_PHASE_DURATIONS)
    if phase_durations:
        durations.update(phase_durations)

    effective_penalty = (
        penalty_rate if penalty_rate is not None else pack["penalty_rate"]
    )
    effective_offset_cap = (
        offset_usage_cap if offset_usage_cap is not None else pack["offset_usage_cap"]
    )
    allocation_factors = pack.get("allocation_factors", YEARLY_ALLOCATION_FACTORS)
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
                    deepcopy(m) for m in scenario_abatement[base["sector"]]
                ],
                "active_abatement_ids": [],
                "pending_abatement_ids": [],
                "abatement_cost_committed": 0.0,
                "auction_allowances_won": 0.0,
                "year_results": [],
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
    }


def build_abatement_menu(sector: str) -> list[dict[str, Any]]:
    return [deepcopy(measure) for measure in ABATEMENT_CATALOG[sector]]


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
        company["abatement_cost_committed"] = round(
            company["abatement_cost_committed"] + measure["cost"], 2
        )
        company["cash"] = round(company["cash"] - measure["cost"], 2)
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

    if action == "buy_offsets":
        quantity = round(float(payload.get("quantity", 0)), 2)
        if quantity <= 0:
            return state
        offset_price = payload.get(
            "price_per_unit", state.get("offset_price", DEFAULT_OFFSET_PRICE)
        )
        total_cost = round(quantity * float(offset_price), 2)
        company["offset_holdings"] = round(company["offset_holdings"] + quantity, 2)
        company["cash"] = round(company["cash"] - total_cost, 2)
        _recalculate_company_projection(state, company)
        _append_event(
            state,
            "offsets_purchased",
            decision_time,
            {
                "year": state["current_year"],
                "company_id": company_id,
                "quantity": quantity,
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
        "company_trade_book": company_trade_book,
        "leaderboard": leaderboard,
        "recent_events": recent_events,
    }


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
                    sum(result["projected_emissions"] for result in year_results), 2
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
                "cash": company["cash"],
                "abatement_cost_committed": company["abatement_cost_committed"],
                "active_abatement_ids": list(company["active_abatement_ids"]),
                "pending_abatement_ids": list(company["pending_abatement_ids"]),
                "auction_allowances_won": company["auction_allowances_won"],
                "year_results": company["year_results"],
            }
        )

    auctions_export = []
    for auction in state["auctions"]:
        auctions_export.append(
            {
                "auction_id": auction["auction_id"],
                "year": auction["year"],
                "label": auction["label"],
                "status": auction["status"],
                "supply": auction["supply"],
                "clearing_price": auction.get("clearing_price", 0),
                "bids": auction["bids"],
                "results": auction.get("results", []),
                "opened_at": auction.get("opened_at"),
                "closed_at": auction.get("closed_at"),
            }
        )

    trades_export = []
    for trade in state["trades"]:
        trades_export.append(
            {
                "trade_id": trade["trade_id"],
                "year": trade.get("year", 0),
                "seller_company_id": trade["seller_company_id"],
                "buyer_company_id": trade["buyer_company_id"],
                "quantity": trade["quantity"],
                "price_per_allowance": trade["price_per_allowance"],
                "total_value": trade["total_value"],
                "status": trade["status"],
                "created_at": trade["created_at"],
                "responded_at": trade.get("responded_at"),
            }
        )

    return {
        "phase": state["phase"],
        "current_year": state["current_year"],
        "num_years": state["num_years"],
        "current_cap": state["current_cap"],
        "penalty_rate": state["penalty_rate"],
        "offset_usage_cap": state["offset_usage_cap"],
        "started_at": state.get("started_at"),
        "completed_at": state.get("completed_at"),
        "companies": companies_export,
        "auctions": auctions_export,
        "trades": trades_export,
        "rankings": _build_rankings(state),
        "audit_log": state["audit_log"],
        "replay": build_session_replay(state),
        "analytics": build_session_analytics(state),
    }


def build_session_summary(state: dict[str, Any]) -> dict[str, Any]:
    rankings = _build_rankings(state)

    total_penalties = sum(c["cumulative_penalties"] for c in state["companies"])
    total_trades_completed = len(
        [t for t in state["trades"] if t["status"] == "accepted"]
    )
    total_auctions_cleared = len(
        [a for a in state["auctions"] if a["status"] == "cleared"]
    )
    avg_clearing_price = 0.0
    cleared_auctions = [
        a
        for a in state["auctions"]
        if a["status"] == "cleared" and a["clearing_price"] > 0
    ]
    if cleared_auctions:
        avg_clearing_price = round(
            sum(a["clearing_price"] for a in cleared_auctions) / len(cleared_auctions),
            2,
        )

    year_summaries = []
    for year in range(1, state["current_year"] + 1):
        year_companies = []
        for company in state["companies"]:
            year_result = next(
                (r for r in company["year_results"] if r["year"] == year), None
            )
            if year_result:
                year_companies.append(
                    {
                        "company_id": company["company_id"],
                        "company_name": company["company_name"],
                        "projected_emissions": year_result["projected_emissions"],
                        "allocation": year_result["allocation"],
                        "offsets_used": year_result["offsets_used_for_compliance"],
                        "banked": year_result["banked_allowances"],
                        "shortfall": year_result["shortfall"],
                        "penalty_due": year_result["penalty_due"],
                    }
                )
        year_auctions = [
            {
                "auction_id": a["auction_id"],
                "clearing_price": a["clearing_price"],
                "status": a["status"],
            }
            for a in state["auctions"]
            if a["year"] == year
        ]
        year_summaries.append(
            {
                "year": year,
                "companies": year_companies,
                "auctions": year_auctions,
            }
        )

    return {
        "headline": (
            f"Completed {state['current_year']} of {state['num_years']} years"
            if state["phase"] == PHASE_COMPLETE
            else f"Year {state['current_year']} of {state['num_years']} in progress ({PHASE_LABELS.get(state['phase'], state['phase'])})"
        ),
        "started_at": state.get("started_at"),
        "completed_at": state.get("completed_at"),
        "total_participants": state["participant_count"],
        "total_penalties_across_all_companies": total_penalties,
        "total_trades_completed": total_trades_completed,
        "total_auctions_cleared": total_auctions_cleared,
        "average_clearing_price": avg_clearing_price,
        "rankings": rankings,
        "year_summaries": year_summaries,
        "facilitator_notes": _facilitator_notes(state),
    }


def _facilitator_notes(state: dict[str, Any]) -> list[str]:
    notes = []
    if state["phase"] == PHASE_COMPLETE:
        notes.append(
            "The session is complete. Use the rankings and year summaries for debriefing."
        )
        notes.append(
            "Ask participants: What drove your abatement and offset decisions?"
        )
        notes.append(
            "Ask participants: How did allowance scarcity affect your trading strategy?"
        )
    elif state["phase"] == PHASE_PAUSED:
        notes.append("The session is paused. Use resume to continue.")
    elif state["phase"] == PHASE_LOBBY:
        notes.append("Waiting for participants to join. Press start when ready.")

    if state["current_year"] > 0:
        non_compliant = [c for c in state["companies"] if c["cumulative_penalties"] > 0]
        if non_compliant:
            notes.append(
                f"{len(non_compliant)} company(ies) have incurred penalties so far. Discuss why during debrief."
            )

        total_abatement = sum(
            len(c["active_abatement_ids"]) for c in state["companies"]
        )
        if total_abatement == 0:
            notes.append(
                "No companies have activated abatement measures yet. Consider whether price signals are strong enough."
            )

    return notes


def _build_rankings(state: dict[str, Any]) -> list[dict[str, Any]]:
    rankings = []
    for rank_index, company in enumerate(
        sorted(
            state["companies"],
            key=lambda c: (
                c["cumulative_penalties"],
                c["penalty_due"],
                -c["banked_allowances"],
            ),
        ),
        start=1,
    ):
        total_abatement = sum(
            measure["abatement_amount"]
            for measure in company["abatement_menu"]
            if measure["measure_id"] in company["active_abatement_ids"]
        )
        rankings.append(
            {
                "rank": rank_index,
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "sector": company["sector"],
                "cumulative_penalties": company["cumulative_penalties"],
                "banked_allowances": company["banked_allowances"],
                "cash_remaining": company["cash"],
                "total_abatement": total_abatement,
                "year_results": company["year_results"],
            }
        )
    return rankings


def _tracked_years(state: dict[str, Any]) -> list[int]:
    years = {
        result["year"]
        for company in state["companies"]
        for result in company.get("year_results", [])
    }
    if state.get("current_year", 0) > 0:
        years.add(state["current_year"])
    return sorted(years)


def _build_year_markers(state: dict[str, Any]) -> list[dict[str, Any]]:
    year_markers = []
    for year in _tracked_years(state):
        year_results = [
            next((result for result in company["year_results"] if result["year"] == year), None)
            for company in state["companies"]
        ]
        year_results = [result for result in year_results if result is not None]
        auctions = [auction for auction in state["auctions"] if auction["year"] == year]
        accepted_trades = [
            trade
            for trade in state["trades"]
            if trade.get("year") == year and trade["status"] == "accepted"
        ]
        shocks = [
            shock for shock in state.get("active_shocks", []) if shock["year"] == year
        ]
        cleared_prices = [
            auction["clearing_price"]
            for auction in auctions
            if auction["status"] == "cleared" and auction["clearing_price"] > 0
        ]
        year_markers.append(
            {
                "year": year,
                "event_count": len(
                    [event for event in state["audit_log"] if event.get("year") == year]
                ),
                "auction_count": len(auctions),
                "accepted_trade_count": len(accepted_trades),
                "trade_volume": round(
                    sum(trade["quantity"] for trade in accepted_trades), 2
                ),
                "total_penalties": round(
                    sum(result["penalty_due"] for result in year_results), 2
                ),
                "total_banked_allowances": round(
                    sum(result["banked_allowances"] for result in year_results), 2
                ),
                "total_offsets_used": round(
                    sum(result["offsets_used_for_compliance"] for result in year_results),
                    2,
                ),
                "average_clearing_price": round(
                    sum(cleared_prices) / len(cleared_prices), 2
                )
                if cleared_prices
                else 0.0,
                "shock_count": len(shocks),
            }
        )
    return year_markers


def apply_shock(
    state: dict[str, Any],
    *,
    shock_type: str,
    magnitude: float = 0.1,
    now: datetime | None = None,
) -> dict[str, Any]:
    if now is None:
        now = datetime.now(timezone.utc)
    current_time = _normalize_time(now)

    if state["phase"] not in {PHASE_DECISION_WINDOW, PHASE_YEAR_START}:
        return state

    if shock_type == "emissions_spike":
        for company in state["companies"]:
            increase = round(company["projected_emissions"] * magnitude, 2)
            company["projected_emissions"] = round(
                company["projected_emissions"] + increase, 2
            )
            company["compliance_gap"] = round(
                company["projected_emissions"]
                - company["allowances"]
                - company["offset_holdings"],
                2,
            )
        _append_event(
            state,
            "shock_emissions_spike",
            current_time,
            {"year": state["current_year"], "magnitude": magnitude},
        )

    elif shock_type == "allowance_withdrawal":
        for company in state["companies"]:
            withdrawal = round(company["allowances"] * magnitude, 2)
            company["allowances"] = round(
                max(0.0, company["allowances"] - withdrawal), 2
            )
            company["compliance_gap"] = round(
                company["projected_emissions"]
                - company["allowances"]
                - company["offset_holdings"],
                2,
            )
        _append_event(
            state,
            "shock_allowance_withdrawal",
            current_time,
            {"year": state["current_year"], "magnitude": magnitude},
        )

    elif shock_type == "cost_shock":
        for company in state["companies"]:
            reduction = round(company["cash"] * magnitude, 2)
            company["cash"] = round(max(0.0, company["cash"] - reduction), 2)
        _append_event(
            state,
            "shock_cost_shock",
            current_time,
            {"year": state["current_year"], "magnitude": magnitude},
        )

    elif shock_type == "offset_supply_change":
        old_cap = state["offset_usage_cap"]
        state["offset_usage_cap"] = round(old_cap * (1.0 + magnitude), 4)
        for company in state["companies"]:
            company["compliance_gap"] = round(
                company["projected_emissions"]
                - company["allowances"]
                - min(
                    company["offset_holdings"],
                    company["projected_emissions"] * state["offset_usage_cap"],
                ),
                2,
            )
        _append_event(
            state,
            "shock_offset_supply_change",
            current_time,
            {
                "year": state["current_year"],
                "old_cap": old_cap,
                "new_cap": state["offset_usage_cap"],
            },
        )
    else:
        return state

    shock_record = {
        "shock_id": f"S{len(state.get('active_shocks', [])) + 1:03d}",
        "shock_type": shock_type,
        "magnitude": magnitude,
        "year": state["current_year"],
        "applied_at": _serialize_time(current_time),
    }
    state.setdefault("active_shocks", []).append(shock_record)
    return state


def run_bot_turns(
    state: dict[str, Any], *, now: datetime | None = None
) -> dict[str, Any]:
    if now is None:
        now = datetime.now(timezone.utc)
    if state["phase"] != PHASE_DECISION_WINDOW:
        return state

    bot_companies = [c for c in state["companies"] if c.get("is_bot")]
    for company in bot_companies:
        strategy_key = company.get("bot_strategy", BOT_STRATEGY_MODERATE)
        strategy = BOT_STRATEGIES.get(
            strategy_key, BOT_STRATEGIES[BOT_STRATEGY_MODERATE]
        )

        for measure in company["abatement_menu"]:
            if measure["measure_id"] in company["active_abatement_ids"]:
                continue
            if measure["measure_id"] in company["pending_abatement_ids"]:
                continue
            cost_ratio = measure["cost"] / max(company["projected_emissions"], 1.0)
            if (
                measure["activation_timing"] == "immediate"
                and cost_ratio <= strategy["abatement_threshold_fraction"] * 1000
            ):
                if company["cash"] >= measure["cost"]:
                    state = apply_company_decision(
                        state,
                        company_id=company["company_id"],
                        action="activate_abatement",
                        payload={"measure_id": measure["measure_id"]},
                        now=now,
                    )
                    company = _get_company(state, company["company_id"])
                    break
            elif strategy["abatement_threshold_fraction"] >= 1.0:
                if company["cash"] >= measure["cost"]:
                    state = apply_company_decision(
                        state,
                        company_id=company["company_id"],
                        action="activate_abatement",
                        payload={"measure_id": measure["measure_id"]},
                        now=now,
                    )
                    company = _get_company(state, company["company_id"])

        company = _get_company(state, company["company_id"])
        if company["compliance_gap"] > 0:
            max_affordable = min(
                company["cash"]
                / max(state.get("offset_price", DEFAULT_OFFSET_PRICE), 1.0),
                company["compliance_gap"],
            )
            desired = round(
                company["compliance_gap"] * strategy["offset_gap_fraction"], 2
            )
            quantity = round(min(desired, max_affordable), 2)
            if quantity > 0:
                state = apply_company_decision(
                    state,
                    company_id=company["company_id"],
                    action="buy_offsets",
                    payload={
                        "quantity": quantity,
                        "price_per_unit": state.get(
                            "offset_price", DEFAULT_OFFSET_PRICE
                        ),
                    },
                    now=now,
                )
                company = _get_company(state, company["company_id"])

        for auction in state["auctions"]:
            if auction["year"] != state["current_year"] or auction["status"] != "open":
                continue
            if company["compliance_gap"] > 0:
                bid_quantity = round(
                    min(
                        company["compliance_gap"] * strategy["auction_bid_fraction"],
                        auction["supply"] / max(len(state["companies"]), 1),
                    ),
                    2,
                )
                if bid_quantity > 0:
                    mid_price = round(
                        (state["auction_price_floor"] + state["auction_price_ceiling"])
                        / 2,
                        2,
                    )
                    bid_price = round(mid_price * strategy["auction_bid_fraction"], 2)
                    bid_price = max(
                        state["auction_price_floor"],
                        min(bid_price, state["auction_price_ceiling"]),
                    )
                    total_cost = round(bid_quantity * bid_price, 2)
                    if total_cost <= company["cash"] and bid_quantity > 0:
                        try:
                            state = submit_auction_bid(
                                state,
                                company_id=company["company_id"],
                                auction_id=auction["auction_id"],
                                quantity=bid_quantity,
                                price=bid_price,
                                now=now,
                            )
                        except ValueError:
                            pass
                        company = _get_company(state, company["company_id"])
            break

    return state


def _company_snapshot(state: dict[str, Any], company: dict[str, Any]) -> dict[str, Any]:
    decision_summary = _decision_summary(state, company)
    return {
        "company_name": company["company_name"],
        "sector_label": company["sector"].replace("_", " ").title(),
        "baseline_emissions": company["baseline_emissions"],
        "projected_emissions": company["projected_emissions"],
        "current_year_allocation": company["current_year_allocation"],
        "allowances": company["allowances"],
        "banked_allowances": company["banked_allowances"],
        "offset_holdings": company["offset_holdings"],
        "offsets_used_for_compliance": company["offsets_used_for_compliance"],
        "compliance_gap": company["compliance_gap"],
        "penalty_due": company["penalty_due"],
        "cumulative_penalties": company["cumulative_penalties"],
        "cash": company["cash"],
        "auction_allowances_won": company["auction_allowances_won"],
        "abatement_menu": [
            {
                **measure,
                "is_active": measure["measure_id"] in company["active_abatement_ids"],
                "is_pending": measure["measure_id"] in company["pending_abatement_ids"],
            }
            for measure in company["abatement_menu"]
        ],
        "decision_summary": decision_summary,
        "is_bot": company.get("is_bot", False),
    }


def _start_year(state: dict[str, Any], year: int, now: datetime) -> None:
    state["current_year"] = year
    current_cap = 0.0

    for company in state["companies"]:
        _activate_pending_abatements(company)
        projected_emissions = _projected_emissions(company, year)
        allocation = round(
            projected_emissions
            * state.get("allocation_factors", YEARLY_ALLOCATION_FACTORS).get(
                year, 0.80
            ),
            2,
        )
        company["projected_emissions"] = projected_emissions
        company["current_year_allocation"] = allocation
        company["allowances"] = round(company["banked_allowances"] + allocation, 2)
        company["offsets_used_for_compliance"] = 0.0
        company["penalty_due"] = 0.0
        company["compliance_gap"] = round(
            projected_emissions - company["allowances"] - company["offset_holdings"], 2
        )
        current_cap += allocation

    state["current_cap"] = round(current_cap, 2)
    state["auctions"] = _build_year_auctions(state)
    for cid in state.get("participant_status", {}):
        state["participant_status"][cid]["decision_count_this_year"] = 0
    _set_phase(state, PHASE_YEAR_START, now)
    _append_event(
        state,
        "year_started",
        now,
        {"year": year, "cap": state["current_cap"]},
    )


def _close_current_year(state: dict[str, Any], now: datetime) -> None:
    year = state["current_year"]
    for company in state["companies"]:
        required_allowances = company["projected_emissions"]
        max_offset_use = round(required_allowances * state["offset_usage_cap"], 2)
        offsets_used = min(company["offset_holdings"], max_offset_use)
        net_requirement = max(0.0, round(required_allowances - offsets_used, 2))
        surplus = max(0.0, round(company["allowances"] - net_requirement, 2))
        shortfall = max(0.0, round(net_requirement - company["allowances"], 2))
        penalty = round(shortfall * state["penalty_rate"], 2)

        company["banked_allowances"] = surplus
        company["allowances"] = surplus
        company["offsets_used_for_compliance"] = offsets_used
        company["offset_holdings"] = round(company["offset_holdings"] - offsets_used, 2)
        company["compliance_gap"] = shortfall
        company["penalty_due"] = penalty
        company["cumulative_penalties"] = round(
            company["cumulative_penalties"] + penalty, 2
        )
        company["cash"] = round(company["cash"] - penalty, 2)
        company["year_results"].append(
            {
                "year": year,
                "projected_emissions": company["projected_emissions"],
                "allocation": company["current_year_allocation"],
                "offsets_used_for_compliance": offsets_used,
                "banked_allowances": surplus,
                "shortfall": shortfall,
                "penalty_due": penalty,
            }
        )

    _append_event(state, "year_closed", now, {"year": year})


def _projected_emissions(company: dict[str, Any], year: int) -> float:
    gross_emissions = company["baseline_emissions"] * (
        (1 + company["growth_rate"]) ** year
    )
    active_abatement = sum(
        measure["abatement_amount"]
        for measure in company["abatement_menu"]
        if measure["measure_id"] in company["active_abatement_ids"]
    )
    return round(max(0.0, gross_emissions - active_abatement), 2)


def _set_phase(state: dict[str, Any], phase: str, now: datetime) -> None:
    state["phase"] = phase
    state["phase_started_at"] = _serialize_time(now)
    duration = state["phase_durations"].get(phase)
    if duration is None:
        state["phase_deadline_at"] = None
    else:
        state["phase_deadline_at"] = _serialize_time(now + timedelta(seconds=duration))


def _append_event(
    state: dict[str, Any],
    event_type: str,
    now: datetime,
    details: dict[str, Any],
) -> None:
    state["audit_log"].append(
        {
            "timestamp": _serialize_time(now),
            "event_type": event_type,
            "year": state["current_year"],
            "summary": _event_summary(event_type, details),
            "details": details,
        }
    )


def _event_summary(event_type: str, details: dict[str, Any]) -> str:
    if event_type == "year_started":
        return f"Year {details['year']} opened with cap {details['cap']}"
    if event_type == "decision_window_opened":
        return f"Companies can now review year {details['year']} allocations and compliance positions"
    if event_type == "year_closed":
        return f"Year {details['year']} compliance was processed and banked balances were updated"
    if event_type == "abatement_activated":
        return f"Company {details['company_id']} committed to abatement measure {details['measure_id']}"
    if event_type == "offsets_purchased":
        return (
            f"Company {details['company_id']} purchased {details['quantity']} offsets"
        )
    if event_type == "auction_opened":
        return f"Auction {details['auction_id']} is now open for bids"
    if event_type == "auction_bid_submitted":
        return f"Company {details['company_id']} submitted {details['quantity']} allowances at bid price {details['price']}"
    if event_type == "auction_cleared":
        return f"Auction {details['auction_id']} cleared at {details['clearing_price']} for {details['cleared_quantity']} allowances"
    if event_type == "trade_proposed":
        return f"Trade {details['trade_id']} proposed: seller {details['seller_company_id']} offered {details['quantity']} allowances to {details['buyer_company_id']} at {details['price_per_allowance']}"
    if event_type == "trade_rejected":
        return f"Trade {details['trade_id']} was rejected"
    if event_type == "trade_accepted":
        return f"Trade {details['trade_id']} settled for {details['quantity']} allowances at {details['price_per_allowance']}"
    if event_type == "trade_expired":
        return f"Trade {details['trade_id']} expired without a response"
    if event_type == "session_completed":
        return f"All {details['year']} simulation years are complete"
    if event_type == "session_paused":
        return f"Session paused during year {details['year']}"
    if event_type == "session_resumed":
        return f"Session resumed for year {details['year']}"
    if event_type == "phase_force_advanced":
        return f"Facilitator forced advance from {details.get('from_phase', '?')} during year {details['year']}"
    if event_type == "shock_emissions_spike":
        return f"Emissions spike shock: all projected emissions increased by {details['magnitude'] * 100:.0f}% in year {details['year']}"
    if event_type == "shock_allowance_withdrawal":
        return f"Allowance withdrawal shock: all allowances reduced by {details['magnitude'] * 100:.0f}% in year {details['year']}"
    if event_type == "shock_cost_shock":
        return f"Cost shock: all company cash reduced by {details['magnitude'] * 100:.0f}% in year {details['year']}"
    if event_type == "shock_offset_supply_change":
        return f"Offset supply change: offset usage cap changed from {details.get('old_cap', '?')} to {details.get('new_cap', '?')} in year {details['year']}"
    return event_type.replace("_", " ")


def _status_text(state: dict[str, Any]) -> str:
    if state["phase"] == PHASE_PAUSED:
        return "The session is paused. The facilitator can resume when ready."
    if state["phase"] == PHASE_LOBBY:
        return "Participants are joining the workshop. The facilitator can start the first virtual year when everyone is ready."
    if state["phase"] == PHASE_YEAR_START:
        return "Fresh annual allocations have been issued and the cap has tightened. Participants should review their company positions."
    if state["phase"] == PHASE_DECISION_WINDOW:
        return "The action window is open. Participants can commit abatement measures, buy offsets, submit sealed bids into the current allowance auction, and propose bilateral trades while projected compliance updates live."
    if state["phase"] == PHASE_COMPLIANCE:
        return "Year-end surrender has been processed. Surplus allowances are banked and shortfalls trigger penalties."
    return "The three-year phase 1 and 2 prototype is complete and ready for debrief."


def _get_company(state: dict[str, Any], company_id: str) -> dict[str, Any]:
    return next(
        company for company in state["companies"] if company["company_id"] == company_id
    )


def _get_measure(company: dict[str, Any], measure_id: str) -> dict[str, Any]:
    return next(
        measure
        for measure in company["abatement_menu"]
        if measure["measure_id"] == measure_id
    )


def _get_auction(state: dict[str, Any], auction_id: str) -> dict[str, Any]:
    return next(
        auction for auction in state["auctions"] if auction["auction_id"] == auction_id
    )


def _get_trade(state: dict[str, Any], trade_id: str) -> dict[str, Any]:
    return next(trade for trade in state["trades"] if trade["trade_id"] == trade_id)


def _build_year_auctions(state: dict[str, Any]) -> list[dict[str, Any]]:
    total_supply = round(state["current_cap"] * state["auction_share_of_cap"], 2)
    count = state["auction_count_per_year"]
    per_auction_supply = round(total_supply / count, 2)
    auctions = []
    for index in range(count):
        supply = per_auction_supply
        if index == count - 1:
            assigned = round(per_auction_supply * (count - 1), 2)
            supply = round(total_supply - assigned, 2)
        auctions.append(
            {
                "auction_id": f"Y{state['current_year']}-A{index + 1}",
                "label": f"Year {state['current_year']} Auction {index + 1}",
                "year": state["current_year"],
                "status": "scheduled",
                "supply": supply,
                "bids": [],
                "results": [],
                "clearing_price": 0.0,
                "remaining_supply": supply,
                "opened_at": None,
                "closed_at": None,
            }
        )
    return auctions


def _activate_pending_abatements(company: dict[str, Any]) -> None:
    for measure_id in company["pending_abatement_ids"]:
        if measure_id not in company["active_abatement_ids"]:
            company["active_abatement_ids"].append(measure_id)
    company["pending_abatement_ids"] = []


def _recalculate_company_projection(
    state: dict[str, Any], company: dict[str, Any]
) -> None:
    company["projected_emissions"] = _projected_emissions(
        company, state["current_year"]
    )
    company["compliance_gap"] = round(
        company["projected_emissions"]
        - company["allowances"]
        - company["offset_holdings"],
        2,
    )


def _expire_trades(state: dict[str, Any], now: datetime) -> None:
    for trade in state["trades"]:
        if trade["status"] != "proposed":
            continue
        if _parse_time(trade["expires_at"]) <= now:
            trade["status"] = "expired"
            trade["responded_at"] = _serialize_time(now)
            _append_event(
                state,
                "trade_expired",
                now,
                {"year": state["current_year"], "trade_id": trade["trade_id"]},
            )


def _decision_summary(state: dict[str, Any], company: dict[str, Any]) -> dict[str, Any]:
    max_offsets_usable = round(
        company["projected_emissions"] * state["offset_usage_cap"], 2
    )
    return {
        "active_abatement_count": len(company["active_abatement_ids"]),
        "pending_abatement_count": len(company["pending_abatement_ids"]),
        "abatement_cost_committed": company["abatement_cost_committed"],
        "offset_holdings": company["offset_holdings"],
        "max_offsets_usable_this_year": max_offsets_usable,
        "projected_net_position": round(
            company["allowances"]
            + min(company["offset_holdings"], max_offsets_usable)
            - company["projected_emissions"],
            2,
        ),
    }


def _serialize_time(value: datetime) -> str:
    return _normalize_time(value).isoformat()


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _normalize_time(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
