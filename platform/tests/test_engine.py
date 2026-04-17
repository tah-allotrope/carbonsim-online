from datetime import datetime, timedelta, timezone
import unittest


from carbonsim_phase12 import engine


def utc(year=2026, month=1, day=1, second=0):
    return datetime(year, month, day, 9, 0, second, tzinfo=timezone.utc)


class EngineTests(unittest.TestCase):
    def test_build_company_specs_matches_requested_participant_count(self):
        specs = engine.build_company_specs(5)

        self.assertEqual(len(specs), 5)
        self.assertEqual(len({spec["company_id"] for spec in specs}), 5)
        self.assertTrue(
            {"thermal_power", "steel", "cement"}.issubset(
                {spec["sector"] for spec in specs}
            )
        )

    def test_start_simulation_initializes_year_one_allocations(self):
        state = engine.create_initial_state(participant_count=3)

        started = engine.start_simulation(state, utc())

        self.assertEqual(started["phase"], engine.PHASE_YEAR_START)
        self.assertEqual(started["current_year"], 1)
        self.assertGreater(started["current_cap"], 0)
        for company in started["companies"]:
            self.assertGreater(company["current_year_allocation"], 0)
            self.assertGreater(
                company["projected_emissions"], company["baseline_emissions"]
            )
            self.assertEqual(company["allowances"], company["current_year_allocation"])

    def test_year_end_processing_banks_surplus_and_penalizes_shortfall(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        surplus_company = state["companies"][0]
        short_company = state["companies"][1]

        surplus_company["allowances"] = round(
            surplus_company["projected_emissions"] + 12, 2
        )
        short_company["allowances"] = round(short_company["projected_emissions"] - 5, 2)

        reviewed = engine.advance_state(state, utc(second=26))

        self.assertEqual(reviewed["phase"], engine.PHASE_COMPLIANCE)

        updated_surplus = reviewed["companies"][0]
        updated_short = reviewed["companies"][1]

        self.assertEqual(updated_surplus["banked_allowances"], 12)
        self.assertEqual(updated_surplus["penalty_due"], 0)
        self.assertEqual(updated_short["banked_allowances"], 0)
        self.assertEqual(
            updated_short["penalty_due"], round(5 * reviewed["penalty_rate"], 2)
        )
        self.assertEqual(updated_short["allowances"], 0)

    def test_advance_state_completes_three_year_cycle(self):
        state = engine.create_initial_state(
            participant_count=4,
            phase_durations={
                "year_start": 1,
                "decision_window": 1,
                "compliance": 1,
            },
        )
        state = engine.start_simulation(state, utc())

        completed = engine.advance_state(state, utc(second=20))

        self.assertEqual(completed["phase"], engine.PHASE_COMPLETE)
        self.assertEqual(completed["current_year"], completed["num_years"])
        self.assertTrue(
            any(
                event["event_type"] == "session_completed"
                for event in completed["audit_log"]
            )
        )

    def test_audit_log_records_year_start_and_year_close_events(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.advance_state(state, utc(second=26))

        event_types = [event["event_type"] for event in state["audit_log"]]
        self.assertIn("year_started", event_types)
        self.assertIn("year_closed", event_types)

    def test_player_snapshot_exposes_dashboard_metrics(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        snapshot = engine.build_player_snapshot(
            state,
            company_id=state["companies"][0]["company_id"],
            is_facilitator=True,
            participant_label="Facilitator",
            now=utc(second=1),
        )

        self.assertEqual(snapshot["phase"], engine.PHASE_YEAR_START)
        self.assertFalse(snapshot["can_start"])
        self.assertIsNotNone(snapshot["company"])
        self.assertIn("projected_emissions", snapshot["company"])
        self.assertEqual(len(snapshot["leaderboard"]), 3)

    def test_company_state_includes_sector_specific_abatement_menu(self):
        state = engine.create_initial_state(participant_count=3)

        thermal = state["companies"][0]
        steel = state["companies"][1]
        cement = state["companies"][2]

        self.assertGreaterEqual(len(thermal["abatement_menu"]), 2)
        self.assertGreaterEqual(len(steel["abatement_menu"]), 2)
        self.assertGreaterEqual(len(cement["abatement_menu"]), 2)
        self.assertNotEqual(
            {measure["measure_id"] for measure in thermal["abatement_menu"]},
            {measure["measure_id"] for measure in steel["abatement_menu"]},
        )

    def test_immediate_and_delayed_abatement_activation_affect_projected_emissions(
        self,
    ):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        company_id = state["companies"][0]["company_id"]
        immediate_id = next(
            measure["measure_id"]
            for measure in state["companies"][0]["abatement_menu"]
            if measure["activation_timing"] == "immediate"
        )
        delayed_id = next(
            measure["measure_id"]
            for measure in state["companies"][0]["abatement_menu"]
            if measure["activation_timing"] == "next_year"
        )

        original_emissions = state["companies"][0]["projected_emissions"]
        state = engine.apply_company_decision(
            state,
            company_id=company_id,
            action="activate_abatement",
            payload={"measure_id": immediate_id},
            now=utc(second=6),
        )
        state = engine.apply_company_decision(
            state,
            company_id=company_id,
            action="activate_abatement",
            payload={"measure_id": delayed_id},
            now=utc(second=7),
        )

        updated_company = state["companies"][0]
        self.assertLess(updated_company["projected_emissions"], original_emissions)
        self.assertIn(delayed_id, updated_company["pending_abatement_ids"])

    def test_offset_purchase_is_capped_at_configured_share_during_compliance(self):
        state = engine.create_initial_state(participant_count=3, offset_usage_cap=0.1)
        state = engine.start_simulation(state, utc())

        company = state["companies"][0]
        state = engine.apply_company_decision(
            state,
            company_id=company["company_id"],
            action="buy_offsets",
            payload={"quantity": 25},
            now=utc(second=8),
        )

        updated_company = state["companies"][0]
        self.assertEqual(updated_company["offset_holdings"], 25)

        updated_company["allowances"] = round(
            updated_company["projected_emissions"] - 30, 2
        )
        reviewed = engine.advance_state(state, utc(second=26))
        reviewed_company = reviewed["companies"][0]
        expected_offsets_used = round(reviewed_company["projected_emissions"] * 0.1, 2)

        self.assertEqual(
            reviewed_company["offsets_used_for_compliance"], expected_offsets_used
        )
        self.assertEqual(
            reviewed_company["offset_holdings"], round(25 - expected_offsets_used, 2)
        )

    def test_player_snapshot_exposes_forward_looking_decision_impact(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        company = state["companies"][0]
        measure_id = company["abatement_menu"][0]["measure_id"]
        state = engine.apply_company_decision(
            state,
            company_id=company["company_id"],
            action="activate_abatement",
            payload={"measure_id": measure_id},
            now=utc(second=6),
        )
        state = engine.apply_company_decision(
            state,
            company_id=company["company_id"],
            action="buy_offsets",
            payload={"quantity": 6},
            now=utc(second=7),
        )

        snapshot = engine.build_player_snapshot(
            state,
            company_id=company["company_id"],
            is_facilitator=False,
            participant_label="Player",
            now=utc(second=8),
        )

        self.assertIn("decision_summary", snapshot["company"])
        self.assertGreater(
            snapshot["company"]["decision_summary"]["abatement_cost_committed"], 0
        )
        self.assertEqual(snapshot["company"]["decision_summary"]["offset_holdings"], 6)
        self.assertIn("abatement_menu", snapshot["company"])

    def test_year_start_creates_auction_schedule(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        self.assertGreaterEqual(len(state["auctions"]), 1)
        first_auction = state["auctions"][0]
        self.assertEqual(first_auction["year"], 1)
        self.assertEqual(first_auction["status"], "scheduled")
        self.assertGreater(first_auction["supply"], 0)

    def test_submit_auction_bid_validates_price_and_cash(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.open_auction(
            state, auction_id=state["auctions"][0]["auction_id"], now=utc(second=6)
        )
        company = state["companies"][0]

        with self.assertRaises(ValueError):
            engine.submit_auction_bid(
                state,
                company_id=company["company_id"],
                auction_id=state["auctions"][0]["auction_id"],
                quantity=5,
                price=0,
                now=utc(second=7),
            )

        with self.assertRaises(ValueError):
            engine.submit_auction_bid(
                state,
                company_id=company["company_id"],
                auction_id=state["auctions"][0]["auction_id"],
                quantity=100000,
                price=500,
                now=utc(second=7),
            )

    def test_uniform_price_auction_clears_and_settles_holdings(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        auction_id = state["auctions"][0]["auction_id"]
        state = engine.open_auction(state, auction_id=auction_id, now=utc(second=6))

        first = state["companies"][0]
        second = state["companies"][1]
        third = state["companies"][2]
        first_cash_before = first["cash"]

        state = engine.submit_auction_bid(
            state,
            company_id=first["company_id"],
            auction_id=auction_id,
            quantity=8,
            price=130,
            now=utc(second=7),
        )
        state = engine.submit_auction_bid(
            state,
            company_id=second["company_id"],
            auction_id=auction_id,
            quantity=6,
            price=120,
            now=utc(second=8),
        )
        state = engine.submit_auction_bid(
            state,
            company_id=third["company_id"],
            auction_id=auction_id,
            quantity=4,
            price=110,
            now=utc(second=9),
        )

        cleared = engine.close_auction(state, auction_id=auction_id, now=utc(second=10))
        auction = next(
            auction
            for auction in cleared["auctions"]
            if auction["auction_id"] == auction_id
        )

        self.assertEqual(auction["status"], "cleared")
        self.assertGreater(auction["clearing_price"], 0)
        self.assertGreater(
            sum(result["awarded_quantity"] for result in auction["results"]), 0
        )
        updated_first = cleared["companies"][0]
        self.assertGreater(updated_first["auction_allowances_won"], 0)
        self.assertLess(updated_first["cash"], first_cash_before)

    def test_tie_at_clearing_price_respects_bid_order(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        auction_id = state["auctions"][0]["auction_id"]
        state = engine.open_auction(state, auction_id=auction_id, now=utc(second=6))

        auction = next(
            item for item in state["auctions"] if item["auction_id"] == auction_id
        )
        auction["supply"] = 5

        state = engine.submit_auction_bid(
            state,
            company_id=state["companies"][0]["company_id"],
            auction_id=auction_id,
            quantity=3,
            price=120,
            now=utc(second=7),
        )
        state = engine.submit_auction_bid(
            state,
            company_id=state["companies"][1]["company_id"],
            auction_id=auction_id,
            quantity=3,
            price=120,
            now=utc(second=8),
        )

        cleared = engine.close_auction(state, auction_id=auction_id, now=utc(second=9))
        auction = next(
            item for item in cleared["auctions"] if item["auction_id"] == auction_id
        )
        results_by_company = {
            result["company_id"]: result["awarded_quantity"]
            for result in auction["results"]
        }

        self.assertEqual(results_by_company[state["companies"][0]["company_id"]], 3)
        self.assertEqual(results_by_company[state["companies"][1]["company_id"]], 2)


class SettingsTests(unittest.TestCase):
    def test_session_config_registers_phase_one_and_two_app(self):
        import settings

        target = next(
            config
            for config in settings.SESSION_CONFIGS
            if config["name"] == "carbonsim_workshop_phase12"
        )

        self.assertEqual(target["app_sequence"], ["carbonsim_phase12"])
        self.assertEqual(target["num_demo_participants"], 6)


if __name__ == "__main__":
    unittest.main()
