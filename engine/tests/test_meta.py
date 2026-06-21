from __future__ import annotations

import unittest
from datetime import datetime, timezone, timedelta

from engine import engine
from engine.engine import award_xp, load_unlock_tree, load_jurisdiction, XP_LEVEL_THRESHOLDS


def utc(seconds=0):
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)


def _window(scenario="solo_standard", bot_count=1, jurisdiction=None):
    state = engine.create_initial_state(
        participant_count=1, bot_count=bot_count, scenario=scenario, jurisdiction=jurisdiction
    )
    state = engine.start_simulation(state, utc())
    state = engine.force_advance_phase(state, utc(1))
    return state


class CapexSchemaTests(unittest.TestCase):
    def test_measures_enriched_with_capex_fields(self):
        state = engine.create_initial_state(participant_count=1)
        m = state["companies"][0]["abatement_menu"][0]
        for key in ("capex", "annual_opex", "asset_life_years", "tech_risk_pct", "break_even_year"):
            self.assertIn(key, m)
        self.assertEqual(m["capex"], m["cost"])  # balance-neutral default

    def test_activate_abatement_records_asset(self):
        state = _window()
        c = state["companies"][0]
        mid = c["abatement_menu"][0]["measure_id"]
        state = engine.apply_company_decision(
            state, company_id=c["company_id"], action="activate_abatement",
            payload={"measure_id": mid}, now=utc(2),
        )
        self.assertEqual(len(c["active_abatement_assets"]), 1)
        self.assertEqual(c["active_abatement_assets"][0]["measure_id"], mid)


class FinancingTests(unittest.TestCase):
    def test_finance_abatement_creates_loan_without_upfront_cash(self):
        state = _window()
        c = state["companies"][0]
        cash0 = c["cash"]
        mid = c["abatement_menu"][0]["measure_id"]
        state = engine.apply_company_decision(
            state, company_id=c["company_id"], action="finance_abatement",
            payload={"measure_id": mid}, now=utc(2),
        )
        self.assertEqual(len(c["active_loans"]), 1)
        self.assertEqual(c["cash"], cash0)  # no capex paid up front
        self.assertGreater(c["active_loans"][0]["annual_payment"], 0)

    def test_loan_payment_deducted_each_year(self):
        state = _window()
        c = state["companies"][0]
        mid = c["abatement_menu"][0]["measure_id"]
        state = engine.apply_company_decision(
            state, company_id=c["company_id"], action="finance_abatement",
            payload={"measure_id": mid}, now=utc(2),
        )
        payment = c["active_loans"][0]["annual_payment"]
        cash_before = c["cash"]
        state = engine.force_advance_phase(state, utc(3))  # compliance
        state = engine.force_advance_phase(state, utc(4))  # next year_start (services loans)
        # Cash dropped by at least the loan payment (plus any compliance effects).
        self.assertLessEqual(c["cash"], cash_before - payment + 1)


class TechFailureTests(unittest.TestCase):
    def test_tech_failure_impairs_then_restores(self):
        state = _window()
        c = state["companies"][0]
        # Force a guaranteed failure on a measure with full tech risk.
        m = c["abatement_menu"][0]
        m["tech_risk_pct"] = 1.0
        mid = m["measure_id"]
        state = engine.apply_company_decision(
            state, company_id=c["company_id"], action="activate_abatement",
            payload={"measure_id": mid}, now=utc(2),
        )
        # ensure the asset carries the risk
        c["active_abatement_assets"][0]["tech_risk_pct"] = 1.0
        state = engine.force_advance_phase(state, utc(3))  # decision_window -> compliance
        state = engine.force_advance_phase(state, utc(4))  # compliance -> next year start (roll failure)
        self.assertIn(mid, c["tech_impaired_ids"])
        # Clear the risk; impairment lasts only one year and clears at the next
        # year start (impaired list is reset before the fresh roll).
        c["active_abatement_assets"][0]["tech_risk_pct"] = 0.0
        state = engine.force_advance_phase(state, utc(5))  # year_start -> decision_window
        state = engine.force_advance_phase(state, utc(6))  # decision_window -> compliance
        state = engine.force_advance_phase(state, utc(7))  # compliance -> next year start (restore)
        self.assertNotIn(mid, c["tech_impaired_ids"])


class XPTests(unittest.TestCase):
    def test_award_xp_accumulates_and_levels(self):
        state = {"xp": 0, "xp_level": 1}
        award_xp(state, "first_compliance")   # +100
        self.assertEqual(state["xp"], 100)
        self.assertEqual(state["xp_level"], 1)
        award_xp(state, "first_compliance")   # +100 -> 200 -> level 2
        self.assertEqual(state["xp"], 200)
        self.assertEqual(state["xp_level"], 2)

    def test_unknown_event_awards_nothing(self):
        state = {"xp": 5}
        self.assertEqual(award_xp(state, "not_an_event"), 0)
        self.assertEqual(state["xp"], 5)

    def test_penalty_free_year_awards_xp_in_game(self):
        state = _window(bot_count=1)
        player = next(c for c in state["companies"] if not c.get("is_bot"))
        player["allowances"] = player["projected_emissions"] + 100  # guarantee compliance
        state = engine.force_advance_phase(state, utc(2))  # compliance closes the year
        self.assertGreater(state["xp"], 0)

    def test_thresholds_shape(self):
        self.assertEqual(XP_LEVEL_THRESHOLDS[0], 0)
        self.assertEqual(len(XP_LEVEL_THRESHOLDS), 6)


class UnlockTreeTests(unittest.TestCase):
    def test_unlock_tree_loads_nodes(self):
        nodes = load_unlock_tree()
        self.assertGreater(len(nodes), 0)
        for node in nodes:
            self.assertIn("level_required", node)
            self.assertIn("unlock_type", node)

    def test_snapshot_exposes_meta_fields(self):
        state = _window()
        snap = engine.build_player_snapshot(
            state, company_id="C01", is_facilitator=False, participant_label="P", now=utc(3)
        )
        for key in ("xp", "xp_level", "unlock_tree", "jurisdiction"):
            self.assertIn(key, snap)


class JurisdictionTests(unittest.TestCase):
    def test_eu_ets_overlay_applies(self):
        state = engine.create_initial_state(participant_count=1, scenario="solo_standard", jurisdiction="eu_ets")
        self.assertEqual(state["jurisdiction"], "eu_ets")
        self.assertEqual(state["penalty_rate"], 950.0)
        names = [c["company_name"].split(" ")[0] for c in state["companies"]]
        self.assertIn("Ruhr", names)

    def test_vietnam_default_unchanged(self):
        state = engine.create_initial_state(participant_count=1, scenario="solo_standard")
        self.assertEqual(state["jurisdiction"], "vietnam")
        self.assertEqual(state["penalty_rate"], 1000.0)  # Sprint 3 tuned value

    def test_load_jurisdiction_missing_returns_empty(self):
        self.assertEqual(load_jurisdiction("atlantis"), {})


if __name__ == "__main__":
    unittest.main()
