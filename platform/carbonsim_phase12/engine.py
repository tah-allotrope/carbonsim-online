from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any


PHASE_LOBBY = "lobby"
PHASE_YEAR_START = "year_start"
PHASE_DECISION_WINDOW = "decision_window"
PHASE_COMPLIANCE = "compliance"
PHASE_COMPLETE = "complete"

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

YEARLY_ALLOCATION_FACTORS = {
    1: 0.92,
    2: 0.88,
    3: 0.84,
}

COMPANY_LIBRARY = [
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
]

PHASE_LABELS = {
    PHASE_LOBBY: "Lobby",
    PHASE_YEAR_START: "Year Start",
    PHASE_DECISION_WINDOW: "Decision Window",
    PHASE_COMPLIANCE: "Compliance Review",
    PHASE_COMPLETE: "Session Complete",
}

ABATEMENT_CATALOG = {
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
    penalty_rate: float = 200.0,
    offset_usage_cap: float = DEFAULT_OFFSET_USAGE_CAP,
    phase_durations: dict[str, int] | None = None,
) -> dict[str, Any]:
    durations = dict(DEFAULT_PHASE_DURATIONS)
    if phase_durations:
        durations.update(phase_durations)

    companies = []
    for spec in build_company_specs(participant_count):
        companies.append(
            {
                **spec,
                "current_year_allocation": 0.0,
                "projected_emissions": spec["baseline_emissions"],
                "allowances": 0.0,
                "banked_allowances": 0.0,
                "offset_holdings": 0.0,
                "offsets_used_for_compliance": 0.0,
                "penalty_due": 0.0,
                "cumulative_penalties": 0.0,
                "compliance_gap": 0.0,
                "abatement_menu": build_abatement_menu(spec["sector"]),
                "active_abatement_ids": [],
                "pending_abatement_ids": [],
                "abatement_cost_committed": 0.0,
                "auction_allowances_won": 0.0,
                "year_results": [],
            }
        )

    return {
        "participant_count": participant_count,
        "num_years": num_years,
        "current_year": 0,
        "current_cap": 0.0,
        "penalty_rate": penalty_rate,
        "offset_usage_cap": offset_usage_cap,
        "auction_count_per_year": DEFAULT_AUCTION_COUNT,
        "auction_price_floor": DEFAULT_AUCTION_PRICE_FLOOR,
        "auction_price_ceiling": DEFAULT_AUCTION_PRICE_CEILING,
        "auction_share_of_cap": DEFAULT_AUCTION_SHARE_OF_CAP,
        "phase": PHASE_LOBBY,
        "phase_durations": durations,
        "phase_started_at": None,
        "phase_deadline_at": None,
        "started_at": None,
        "completed_at": None,
        "companies": companies,
        "auctions": [],
        "audit_log": [],
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
        offset_price = payload.get("price_per_unit", 25.0)
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


def advance_state(state: dict[str, Any], now: datetime) -> dict[str, Any]:
    if state["phase"] in {PHASE_LOBBY, PHASE_COMPLETE}:
        return state

    current_time = _normalize_time(now)
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
        "is_facilitator": is_facilitator,
        "auction_board": auction_board,
        "company": None if company is None else _company_snapshot(state, company),
        "leaderboard": leaderboard,
        "recent_events": recent_events,
    }


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
    }


def _start_year(state: dict[str, Any], year: int, now: datetime) -> None:
    state["current_year"] = year
    current_cap = 0.0

    for company in state["companies"]:
        _activate_pending_abatements(company)
        projected_emissions = _projected_emissions(company, year)
        allocation = round(
            projected_emissions * YEARLY_ALLOCATION_FACTORS.get(year, 0.80), 2
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
    if event_type == "session_completed":
        return f"All {details['year']} simulation years are complete"
    return event_type.replace("_", " ")


def _status_text(state: dict[str, Any]) -> str:
    if state["phase"] == PHASE_LOBBY:
        return "Participants are joining the workshop. The facilitator can start the first virtual year when everyone is ready."
    if state["phase"] == PHASE_YEAR_START:
        return "Fresh annual allocations have been issued and the cap has tightened. Participants should review their company positions."
    if state["phase"] == PHASE_DECISION_WINDOW:
        return "The action window is open. Participants can commit abatement measures, buy offsets, and submit sealed bids into the current allowance auction while projected compliance updates live."
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
