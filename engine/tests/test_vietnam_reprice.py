"""Tests for the 2026-06-30 Vietnam exchange retheme & VND reprice.

Anchors:
* vietnam_pilot.offset_price == 136,000 đ/tCO2e (real first-transaction price)
* vietnam_pilot year-1 cap ≈ 511,473,846 tCO2e (real national allocation)
* Per-field mapping from plan CON-001 is applied correctly
"""
from __future__ import annotations

import unittest

from engine.constants import VND_FX, VN_VOLUME_FACTOR, VN_NATIONAL_ALLOCATION_TCO2E
from engine.scenarios import SCENARIO_PACKS, VCM_CATALOG, TECH_UNLOCK_TEMPLATES


class VNDAnchorTests(unittest.TestCase):
    def test_fx_anchor_constant(self):
        # 25 USD-ish * 5440 = 136,000 đ/tCO2e
        self.assertEqual(VND_FX, 5440.0)
        self.assertEqual(round(25.0 * VND_FX, 2), 136_000.0)

    def test_vietnam_pilot_offset_price_anchor(self):
        # Real first-transaction price: 136,000 đ/tCO2e
        self.assertEqual(SCENARIO_PACKS["vietnam_pilot"]["offset_price"], 136_000.0)

    def test_vietnam_pilot_penalty_rate_fx_only(self):
        # 301 * 5440 = 1,637,440 (FX only, no V on per-tonne rates)
        self.assertEqual(SCENARIO_PACKS["vietnam_pilot"]["penalty_rate"], 301.0 * 5440.0)

    def test_vietnam_pilot_auction_floor_ceiling_fx_only(self):
        # 80 * 5440 = 435,200 ; 300 * 5440 = 1,632,000
        self.assertEqual(SCENARIO_PACKS["vietnam_pilot"]["auction_price_floor"], 80.0 * 5440.0)
        self.assertEqual(SCENARIO_PACKS["vietnam_pilot"]["auction_price_ceiling"], 300.0 * 5440.0)


class VietnamVolumeRescaleTests(unittest.TestCase):
    def test_vietnam_pilot_baseline_emissions_v_only(self):
        # baseline 120 t/yr * V = 120 * 639,444.73 = 76,733,367.20 tCO2e/yr
        baseline = SCENARIO_PACKS["vietnam_pilot"]["company_library"][0]["baseline_emissions"]
        self.assertEqual(baseline, round(120.0 * VN_VOLUME_FACTOR, 2))

    def test_vietnam_pilot_abatement_amount_v_only(self):
        # abatement_amount 10 t/yr * V = 10 * 639,444.73 = 6,394,447.27 tCO2e/yr
        measure = SCENARIO_PACKS["vietnam_pilot"]["abatement_catalog"]["thermal_power"][0]
        self.assertEqual(measure["abatement_amount"], round(10.0 * VN_VOLUME_FACTOR, 2))

    def test_vietnam_pilot_three_year_cap_sum_equals_national_allocation(self):
        # Sum of company baseline * allocation_factor[year] across the 3-year
        # horizon should land on the real national allocation, ±0.5%
        # (per plan TEST-002). This is the headline "total allocated quota"
        # tile value the Vietnam board will display.
        pack = SCENARIO_PACKS["vietnam_pilot"]
        cap = sum(
            co["baseline_emissions"] * pack["allocation_factors"][year]
            for co in pack["company_library"]
            for year in pack["allocation_factors"]
        )
        target = VN_NATIONAL_ALLOCATION_TCO2E
        self.assertAlmostEqual(cap, target, delta=target * 0.005)

    def test_abatement_cost_is_money_not_per_tonne(self):
        # CON-001 audit: abatement cost is lump-sum money (FX × V), not per-tonne.
        # 90,000 * 5440 * 639,445 = 3.13e14 đ — the per-tonne equivalent
        # should still be plausible for an industrial measure.
        measure = SCENARIO_PACKS["vietnam_pilot"]["abatement_catalog"]["thermal_power"][0]
        cost = measure["cost"]
        per_tonne_vnd = cost / measure["abatement_amount"]
        # Per-tonne cost should be in the FX-only band: 90,000 / 10 * 5440 = 48,960,000
        expected_per_tonne = (90_000.0 / 10.0) * VND_FX
        self.assertAlmostEqual(per_tonne_vnd, expected_per_tonne, delta=1.0)


class PerFieldMappingAuditTests(unittest.TestCase):
    """No field should receive the wrong axis (FX vs V vs both)."""

    def test_per_tonne_fields_get_fx_only(self):
        pack = SCENARIO_PACKS["vietnam_pilot"]
        self.assertEqual(pack["penalty_rate"] / 301.0, VND_FX)
        self.assertEqual(pack["offset_price"] / 25.0, VND_FX)
        self.assertEqual(pack["auction_price_floor"] / 80.0, VND_FX)
        self.assertEqual(pack["auction_price_ceiling"] / 300.0, VND_FX)

    def test_tonnage_fields_get_v_only(self):
        # baseline 120 t → 120 * V; abatement 10 t → 10 * V; no FX added.
        # The rescale rounds to 2 đ / 2 tCO2e precision, so we allow a small
        # delta rather than a strict equality on the ratio.
        pack = SCENARIO_PACKS["vietnam_pilot"]
        baseline = pack["company_library"][0]["baseline_emissions"]
        self.assertAlmostEqual(baseline / 120.0, VN_VOLUME_FACTOR, delta=0.01)
        measure = pack["abatement_catalog"]["thermal_power"][0]
        self.assertAlmostEqual(measure["abatement_amount"] / 10.0, VN_VOLUME_FACTOR, delta=0.01)

    def test_lump_sum_money_gets_fx_times_v(self):
        # company cash 1,500,000 → 1,500,000 * FX * V
        cash = SCENARIO_PACKS["vietnam_pilot"]["company_library"][0]["cash"]
        self.assertEqual(cash, round(1_500_000.0 * VND_FX * VN_VOLUME_FACTOR, 2))


class VCMAandTechUnlockTests(unittest.TestCase):
    def test_vcm_costs_get_fx_times_v(self):
        # REDD+ 150,000 → 150,000 * FX * V
        redd = next(p for p in VCM_CATALOG if p["project_id"] == "vcm_redd_plus")
        self.assertEqual(redd["cost"], round(150_000.0 * VND_FX * VN_VOLUME_FACTOR, 2))

    def test_vcm_annual_credits_get_v_only(self):
        # annual_credits is tonnage (tCO2e/yr into offset_holdings) → V only, no FX.
        redd = next(p for p in VCM_CATALOG if p["project_id"] == "vcm_redd_plus")
        self.assertEqual(redd["annual_credits"], round(8.0 * VN_VOLUME_FACTOR, 2))

    def test_tech_unlock_templates_get_fx_times_v(self):
        # default 40,000 → 40,000 * FX * V
        self.assertEqual(
            TECH_UNLOCK_TEMPLATES["default"]["cost"],
            round(40_000.0 * VND_FX * VN_VOLUME_FACTOR, 2),
        )

    def test_tech_unlock_abatement_amount_gets_v_only(self):
        # abatement_amount is tonnage → V only, no FX.
        self.assertEqual(
            TECH_UNLOCK_TEMPLATES["default"]["abatement_amount"],
            round(5.0 * VN_VOLUME_FACTOR, 2),
        )


class JurisdictionFXTests(unittest.TestCase):
    def test_eu_jurisdiction_uses_fx_only_no_v(self):
        from engine.engine import load_jurisdiction
        overlay = load_jurisdiction("eu_ets")
        # penalty 950 → 950 * FX (no V — V is VN-only per plan DEC-002)
        self.assertEqual(overlay["penalty_rate"], round(950.0 * VND_FX, 2))
        # cash 1,600,000 → 1,600,000 * FX only
        ruhr = next(c for c in overlay["company_library"] if c["company_name"].startswith("Ruhr"))
        self.assertEqual(ruhr["cash"], round(1_600_000.0 * VND_FX, 2))
        # tonnage unchanged: 120.0
        self.assertEqual(ruhr["baseline_emissions"], 120.0)


class MarketBoardSnapshotTests(unittest.TestCase):
    """2026-06-30 PHASE-04 — the six board stat tiles surface in the
    player snapshot under ``market_board``. Live/derived from state where
    possible; ``None`` for absent data (plan ASM-002)."""

    def _make_state(self, scenario="vietnam_pilot"):
        from engine import engine
        state = engine.create_initial_state(participant_count=1, scenario=scenario)
        state = engine.start_simulation(state, __import__("datetime").datetime(2026, 1, 1, tzinfo=__import__("datetime").timezone.utc))
        return state

    def test_vietnam_total_allocated_quota_anchors_511m(self):
        from engine import engine
        import datetime
        state = engine.create_initial_state(participant_count=1, scenario="vietnam_pilot")
        state = engine.start_simulation(
            state, datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        )
        snap = engine.build_player_snapshot(
            state, company_id="C01", is_facilitator=False, participant_label="P",
            now=datetime.datetime(2026, 1, 2, tzinfo=datetime.timezone.utc),
        )
        self.assertIn("market_board", snap)
        board = snap["market_board"]
        self.assertEqual(board["total_allocated_quota"], VN_NATIONAL_ALLOCATION_TCO2E)

    def test_latest_execution_price_falls_back_to_offset(self):
        from engine import engine
        import datetime
        state = engine.create_initial_state(participant_count=1, scenario="vietnam_pilot")
        state = engine.start_simulation(
            state, datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        )
        snap = engine.build_player_snapshot(
            state, company_id="C01", is_facilitator=False, participant_label="P",
            now=datetime.datetime(2026, 1, 2, tzinfo=datetime.timezone.utc),
        )
        board = snap["market_board"]
        # No auction cleared yet, so falls back to the (FX'd) offset price.
        self.assertEqual(
            board["latest_execution_price"],
            SCENARIO_PACKS["vietnam_pilot"]["offset_price"],
        )

    def test_empty_bid_and_offer_are_none(self):
        from engine import engine
        import datetime
        state = engine.create_initial_state(participant_count=1, scenario="vietnam_pilot")
        state = engine.start_simulation(
            state, datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        )
        snap = engine.build_player_snapshot(
            state, company_id="C01", is_facilitator=False, participant_label="P",
            now=datetime.datetime(2026, 1, 2, tzinfo=datetime.timezone.utc),
        )
        board = snap["market_board"]
        self.assertIsNone(board["best_bid"])
        self.assertIsNone(board["lowest_offer"])
        self.assertEqual(board["total_trade_volume"], 0.0)
        self.assertEqual(board["total_trade_value"], 0.0)

    def test_eu_jurisdiction_keeps_own_total(self):
        from engine import engine
        import datetime
        state = engine.create_initial_state(participant_count=1, scenario="solo_standard", jurisdiction="eu_ets")
        state = engine.start_simulation(
            state, datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        )
        snap = engine.build_player_snapshot(
            state, company_id="C01", is_facilitator=False, participant_label="P",
            now=datetime.datetime(2026, 1, 2, tzinfo=datetime.timezone.utc),
        )
        board = snap["market_board"]
        # EU total is NOT 511M — it's the jurisdiction's own realistic sum.
        self.assertNotEqual(board["total_allocated_quota"], VN_NATIONAL_ALLOCATION_TCO2E)
        self.assertGreater(board["total_allocated_quota"], 0.0)


if __name__ == "__main__":
    unittest.main()
