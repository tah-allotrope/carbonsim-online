from __future__ import annotations

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
    BOT_STRATEGY_CONSERVATIVE,
    BOT_STRATEGY_MODERATE,
    BOT_STRATEGY_AGGRESSIVE,
    BOT_STRATEGIES,
    YEARLY_ALLOCATION_FACTORS,
    PHASE_LABELS,
)
from .scenarios import SCENARIO_PACKS, SHOCK_CATALOG

COMPANY_LIBRARY = SCENARIO_PACKS["vietnam_pilot"]["company_library"]
ABATEMENT_CATALOG = SCENARIO_PACKS["vietnam_pilot"]["abatement_catalog"]


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
    current_time = _normalize_time(now)
    for company in state["companies"]:
        if not company.get("is_bot"):
            continue
        strategy = BOT_STRATEGIES.get(
            company.get("bot_strategy", BOT_STRATEGY_MODERATE),
            BOT_STRATEGIES[BOT_STRATEGY_MODERATE],
        )

        _activate_pending_abatements(company)

        abatement_threshold = strategy["abatement_threshold_fraction"]
        for measure in company["abatement_menu"]:
            if (
                measure["measure_id"] in company["active_abatement_ids"]
                or measure["measure_id"] in company["pending_abatement_ids"]
            ):
                continue
            if company["allowances"] >= company["projected_emissions"]:
                break
            ordered = sorted(
                [
                    m
                    for m in company["abatement_menu"]
                    if m["measure_id"] not in company["active_abatement_ids"]
                    and m["measure_id"] not in company["pending_abatement_ids"]
                ],
                key=lambda m: m["cost"] / max(m["abatement_amount"], 0.01),
            )
            if not ordered:
                break
            target = ordered[0]
            if target["cost"] > company["cash"]:
                continue
            if company["allowances"] >= company["projected_emissions"] * abatement_threshold:
                break
            apply_company_decision(
                state,
                company_id=company["company_id"],
                action="activate_abatement",
                payload={"measure_id": target["measure_id"]},
                now=current_time,
            )

        _recalculate_company_projection(state, company)
        gap = company["projected_emissions"] - company["allowances"]
        if gap > 0:
            offset_qty = round(gap * strategy["offset_gap_fraction"], 2)
            if offset_qty > 0:
                total_cost = round(
                    offset_qty * state.get("offset_price", DEFAULT_OFFSET_PRICE), 2
                )
                if total_cost <= company["cash"]:
                    apply_company_decision(
                        state,
                        company_id=company["company_id"],
                        action="buy_offsets",
                        payload={"quantity": offset_qty},
                        now=current_time,
                    )

        for auction in state["auctions"]:
            if auction["status"] != "open" or auction["year"] != state["current_year"]:
                continue
            if company["allowances"] >= company["projected_emissions"]:
                break
            bid_qty = round(
                (company["projected_emissions"] - company["allowances"])
                * strategy["auction_bid_fraction"],
                2,
            )
            if bid_qty <= 0:
                continue
            bid_price = state["auction_price_floor"] + (
                state["auction_price_ceiling"] - state["auction_price_floor"]
            ) * strategy["auction_bid_fraction"]
            if bid_qty * bid_price > company["cash"]:
                continue
            try:
                submit_auction_bid(
                    state,
                    company_id=company["company_id"],
                    auction_id=auction["auction_id"],
                    quantity=bid_qty,
                    price=round(bid_price, 2),
                    now=current_time,
                )
            except ValueError:
                continue

    return state


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
        "is_bot": company.get("is_bot", False),
    }


def _start_year(state: dict[str, Any], year: int, now: datetime) -> None:
    state["current_year"] = year
    allocation_factor = state["allocation_factors"].get(year, 0.80)
    total_baseline = sum(
        company["baseline_emissions"] * (1 + company["growth_rate"]) ** (year - 1)
        for company in state["companies"]
    )
    state["current_cap"] = round(total_baseline * allocation_factor, 2)

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


def _projected_emissions(company: dict[str, Any], year: int) -> float:
    base = company["baseline_emissions"] * (1 + company["growth_rate"]) ** (year - 1)
    for measure in company["abatement_menu"]:
        if measure["measure_id"] in company["active_abatement_ids"]:
            base -= measure["abatement_amount"]
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
        return f"Year {details['year']} closed - penalties: {details['total_penalties']:.2f}, banked: {details['total_banked']:.2f}"
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


def _decision_summary(state: dict[str, Any], company: dict[str, Any]) -> dict[str, Any]:
    return {
        "company_id": company["company_id"],
        "company_name": company["company_name"],
        "year": state["current_year"],
        "allowances_held": company["allowances"],
        "projected_emissions": company["projected_emissions"],
        "compliance_gap": company["compliance_gap"],
        "offset_holdings": company["offset_holdings"],
        "banked_allowances": company["banked_allowances"],
        "cash": company["cash"],
        "active_abatement_ids": list(company["active_abatement_ids"]),
        "pending_abatement_ids": list(company["pending_abatement_ids"]),
    }


def _serialize_time(value: datetime) -> str:
    return value.isoformat()


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _normalize_time(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
