"""Goal-driven company agents (Sprint 3).

Replaces the single-year threshold heuristics that previously lived inline in
``engine.run_bot_turns`` with planning agents that look across a 2-3 year
compliance horizon and use the full instrument stack (abatement, offsets,
forward contracts, VCM projects, ETS auctions, and bilateral OTC trades).

Design notes
------------
* ``plan_year`` is intentionally *near-pure*: it reads state and returns an
  ordered list of action dicts ``{"action", "payload"}``. It does not mutate
  state. ``engine.run_bot_turns`` is the dispatcher that applies the actions
  through the normal reducer, so every agent move is audited like a human move.
* Per RISK-03-01 the candidate set is bounded (at most ~10 abatement measures,
  one VCM project, one forward, one OTC proposal per agent per year) and pruned
  greedily by cost-effectiveness — no exhaustive search.
* Per RISK-03-02 trade decisions use the agent's *own* projected position and
  only read a peer's public ``compliance_gap``; they never read a peer's exact
  cash balance to gain an unfair edge.

Imports from ``engine`` are done lazily inside methods to avoid a circular
import (``engine`` imports this module inside ``run_bot_turns``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .constants import BOT_STRATEGIES, BOT_STRATEGY_MODERATE
from .scenarios import VCM_CATALOG


@dataclass
class CompanyAgent:
    """A goal-driven decision agent bound to one bot company."""

    company_id: str
    sector: str
    risk_appetite: str = BOT_STRATEGY_MODERATE
    horizon_years: int = 2
    cash_target_fraction: float = 0.3
    preferred_instruments: list[str] = field(default_factory=list)

    @classmethod
    def from_company(cls, company: dict[str, Any]) -> "CompanyAgent":
        strategy = company.get("bot_strategy") or BOT_STRATEGY_MODERATE
        profile = BOT_STRATEGIES.get(strategy, BOT_STRATEGIES[BOT_STRATEGY_MODERATE])
        return cls(
            company_id=company["company_id"],
            sector=company.get("sector", ""),
            risk_appetite=strategy,
            horizon_years=int(profile.get("horizon_years", 2)),
            cash_target_fraction=float(profile.get("cash_target_fraction", 0.3)),
            preferred_instruments=list(profile.get("preferred_instruments", [])),
        )

    @property
    def profile(self) -> dict[str, Any]:
        return BOT_STRATEGIES.get(
            self.risk_appetite, BOT_STRATEGIES[BOT_STRATEGY_MODERATE]
        )

    # ------------------------------------------------------------------ planning

    def plan_year(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        """Return an ordered list of action dicts for the current decision window.

        Does not mutate ``state``.
        """
        from .engine import (  # lazy import to avoid circular dependency
            DEFAULT_OFFSET_PRICE,
            DEFAULT_OFFSET_USAGE_CAP,
            DEFAULT_PENALTY_RATE,
            _get_company,
            project_outcome,
        )

        try:
            company = _get_company(state, self.company_id)
        except ValueError:
            return []

        p = self.profile
        actions: list[dict[str, Any]] = []

        proj = company.get("projected_emissions", 0.0)
        allowances = company.get("allowances", 0.0)
        offset_cap_pct = state.get("offset_usage_cap", DEFAULT_OFFSET_USAGE_CAP)
        penalty_rate = state.get("penalty_rate", DEFAULT_PENALTY_RATE)
        base_price = state.get("offset_price", DEFAULT_OFFSET_PRICE)
        spot_price = self._spot_price(state)

        cash = company.get("cash", 0.0)
        cash_floor = self._cash_floor(company)
        committed = 0.0

        def affordable(extra_cost: float) -> bool:
            return committed + extra_cost <= max(cash - cash_floor, 0.0)

        # ---- 1. Abatement (rank by cost per tonne abated) ----------------------
        immediate_cut = 0.0
        offset_cap = round(proj * offset_cap_pct, 2)
        usable = min(company.get("offset_holdings", 0.0), offset_cap)
        running_gap = round(proj - allowances - usable, 2)
        # Conservative bots only abate down to a threshold of remaining gap.
        target_gap = proj * (1.0 - p["abatement_threshold_fraction"])

        for measure in self._available_measures(company)[:10]:
            if running_gap <= target_gap:
                break
            if not affordable(measure["cost"]):
                continue
            per_tonne = measure["cost"] / max(measure["abatement_amount"], 0.01)
            # Skip measures that cost more per tonne than the penalty over the
            # horizon, unless the agent is aggressive (it abates regardless).
            if (
                per_tonne > penalty_rate * self.horizon_years
                and self.risk_appetite not in ("aggressive",)
            ):
                continue
            actions.append(
                {"action": "activate_abatement", "payload": {"measure_id": measure["measure_id"]}}
            )
            committed += measure["cost"]
            if measure["activation_timing"] == "immediate":
                running_gap -= measure["abatement_amount"]
                immediate_cut += measure["abatement_amount"]

        # Effective position after immediate abatement.
        eff_proj = max(proj - immediate_cut, 0.0)
        eff_cap = round(eff_proj * offset_cap_pct, 2)
        eff_usable = min(company.get("offset_holdings", 0.0), eff_cap)
        gap = round(eff_proj - allowances - eff_usable, 2)
        future_gap = self._estimate_future_gap(state, company)

        # ---- 2. Forward contracts (hedge next year's gap) ----------------------
        if (
            p.get("forward_appetite", 0.0) > 0.0
            and self.horizon_years > 1
            and future_gap > 0
            # Opportunistic discipline: only lock forwards when spot is still
            # cheap relative to its base (don't chase a spiking market).
            and spot_price <= base_price * 1.25
        ):
            fwd_qty = round(future_gap * p["forward_appetite"], 2)
            locked = round(spot_price * 1.05, 2)
            if fwd_qty > 0 and affordable(fwd_qty * locked):
                actions.append({"action": "buy_forward", "payload": {"quantity": fwd_qty}})
                committed += fwd_qty * locked

        # ---- 3. VCM project investment (multi-year credit stream) --------------
        if p.get("vcm_appetite", 0.0) > 0.0:
            invested = {v["project_id"] for v in company.get("vcm_projects", [])}
            multi_year_need = gap + future_gap
            wants_stream = multi_year_need > 0 or self.risk_appetite == "speculator"
            if wants_stream:
                ranked_projects = sorted(
                    VCM_CATALOG, key=lambda x: x["cost"] / max(x["annual_credits"], 0.01)
                )
                for proj_t in ranked_projects:
                    if proj_t["project_id"] in invested:
                        continue
                    if affordable(proj_t["cost"]):
                        actions.append(
                            {"action": "invest_vcm", "payload": {"project_id": proj_t["project_id"]}}
                        )
                        committed += proj_t["cost"]
                        break  # one VCM project per year

        # ---- 4. Spot offsets (cover residual gap, respecting the usage cap) -----
        if gap > 0:
            headroom = max(eff_cap - eff_usable, 0.0)
            qty = round(min(gap * p["offset_gap_fraction"], headroom), 2)
            if qty > 0 and affordable(qty * spot_price):
                # Confirm the projected compliance benefit via the pure helper.
                outcome = project_outcome(
                    state,
                    company_id=self.company_id,
                    action="buy_offsets",
                    payload={"quantity": qty, "price_per_unit": spot_price},
                )
                if outcome["compliance_gap_delta"] < 0:  # genuinely closes the gap
                    actions.append({"action": "buy_offsets", "payload": {"quantity": qty}})
                    committed += qty * spot_price
                    gap = round(gap + outcome["compliance_gap_delta"], 2)

        # ---- 5. Auction bids (cover whatever gap remains) ----------------------
        if gap > 0:
            floor = state.get("auction_price_floor", 80.0)
            ceiling = state.get("auction_price_ceiling", 300.0)
            bid_price = round(floor + (ceiling - floor) * p["auction_bid_fraction"], 2)
            for auction in state.get("auctions", []):
                if gap <= 0:
                    break
                if auction["status"] != "open" or auction["year"] != state["current_year"]:
                    continue
                bid_qty = round(gap * p["auction_bid_fraction"], 2)
                if bid_qty <= 0:
                    continue
                if affordable(bid_qty * bid_price):
                    actions.append(
                        {
                            "action": "submit_auction_bid",
                            "payload": {
                                "auction_id": auction["auction_id"],
                                "quantity": bid_qty,
                                "price": bid_price,
                            },
                        }
                    )
                    committed += bid_qty * bid_price
                    gap -= bid_qty

        # ---- 6. OTC proposal (sell surplus allowances to a deficit peer) -------
        otc = self._plan_otc(state, company, eff_proj, base_price)
        if otc is not None:
            actions.append(otc)

        return actions

    def _plan_otc(
        self,
        state: dict[str, Any],
        company: dict[str, Any],
        eff_proj: float,
        base_price: float,
    ) -> dict[str, Any] | None:
        """Propose at most one OTC sale of surplus allowances per year.

        Reads only peers' public ``compliance_gap``; never their cash.
        """
        appetite = self.profile.get("otc_appetite", 0.0)
        if appetite <= 0.0:
            return None
        surplus = round(company.get("allowances", 0.0) - eff_proj, 2)
        if surplus <= 0:
            return None

        # Find the peer with the largest projected shortfall.
        best_peer = None
        best_gap = 0.0
        for peer in state.get("companies", []):
            if peer["company_id"] == self.company_id:
                continue
            peer_gap = peer.get("compliance_gap", 0.0)
            if peer_gap > best_gap:
                best_gap = peer_gap
                best_peer = peer
        if best_peer is None or best_gap <= 0:
            return None

        quantity = round(min(surplus, best_gap) * appetite, 2)
        if quantity <= 0:
            return None
        # Speculators charge a premium over the offset spot price; others sell
        # near spot to move volume.
        premium = 1.0 + 0.3 * appetite
        price = round(base_price * premium, 2)
        return {
            "action": "propose_trade",
            "payload": {
                "buyer_company_id": best_peer["company_id"],
                "quantity": quantity,
                "price_per_allowance": price,
            },
        }

    # ----------------------------------------------------------------- responses

    def respond_to_trade(self, state: dict[str, Any], trade: dict[str, Any]) -> str:
        """Decide whether to accept a bilateral trade proposed to this agent.

        Returns ``"accept"`` or ``"reject"``. Accepts when buying the allowances
        is cheaper than paying the penalty for the agent's own shortfall and the
        agent can afford it.
        """
        from .engine import DEFAULT_PENALTY_RATE, _get_company

        try:
            company = _get_company(state, self.company_id)
        except ValueError:
            return "reject"

        gap = company.get("compliance_gap", 0.0)
        if gap <= 0:
            return "reject"  # no need for the allowances
        penalty_rate = state.get("penalty_rate", DEFAULT_PENALTY_RATE)
        price = trade.get("price_per_allowance", 0.0)
        total = trade.get("total_value", 0.0)
        cash_floor = self._cash_floor(company)
        # Buy only if the per-allowance price beats the penalty and we keep a
        # cash reserve afterwards.
        if price <= penalty_rate and company.get("cash", 0.0) - total >= cash_floor:
            return "accept"
        return "reject"

    # ------------------------------------------------------------------- helpers

    def _cash_floor(self, company: dict[str, Any]) -> float:
        base = company.get("starting_cash", company.get("cash", 0.0))
        return round(base * self.cash_target_fraction, 2)

    @staticmethod
    def _available_measures(company: dict[str, Any]) -> list[dict[str, Any]]:
        active = set(company.get("active_abatement_ids", []))
        pending = set(company.get("pending_abatement_ids", []))
        return sorted(
            [
                m
                for m in company.get("abatement_menu", [])
                if m["measure_id"] not in active and m["measure_id"] not in pending
            ],
            key=lambda m: m["cost"] / max(m["abatement_amount"], 0.01),
        )

    @staticmethod
    def _spot_price(state: dict[str, Any]) -> float:
        from .engine import DEFAULT_OFFSET_PRICE

        base = state.get("offset_price", DEFAULT_OFFSET_PRICE)
        elasticity = state.get("offset_price_elasticity", 0.4)
        supply_cap = max(state.get("annual_offset_supply_cap", 50.0), 1.0)
        demand = state.get("offset_demand_this_year", 0.0)
        return round(base * (1 + elasticity * min(demand / supply_cap, 1.0)), 2)

    def _estimate_future_gap(self, state: dict[str, Any], company: dict[str, Any]) -> float:
        """Estimate next year's compliance gap (cap tightens, emissions grow).

        Uses the public allocation-factor schedule and the company's growth
        rate; assumes free-allocation share scales with the cap. Bounded to the
        agent's horizon so a 1-year planner returns 0.
        """
        if self.horizon_years <= 1:
            return 0.0
        year = state.get("current_year", 1)
        next_year = year + 1
        if next_year > state.get("num_years", year):
            return 0.0

        factors = state.get("allocation_factors", {})
        this_factor = factors.get(year) or factors.get(str(year)) or 0.8
        next_factor = factors.get(next_year) or factors.get(str(next_year)) or this_factor

        growth = company.get("growth_rate", 0.0)
        baseline = company.get("baseline_emissions", 0.0)
        # Emissions next year before any *new* abatement, keeping current measures.
        active = set(company.get("active_abatement_ids", []))
        active_cut = sum(
            m["abatement_amount"]
            for m in company.get("abatement_menu", [])
            if m["measure_id"] in active
        )
        next_emissions = max(baseline * (1 + growth) ** (next_year - 1) - active_cut, 0.0)
        # Approximate next-year free allocation as current allocation scaled by
        # the factor decline (auction share is constant).
        current_alloc = company.get("current_year_allocation", 0.0)
        next_alloc = current_alloc * (next_factor / this_factor) if this_factor else current_alloc
        return round(max(next_emissions - next_alloc, 0.0), 2)
