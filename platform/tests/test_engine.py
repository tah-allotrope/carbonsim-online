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

    def test_trade_proposal_is_recorded_and_visible(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        seller = state["companies"][0]
        buyer = state["companies"][1]
        seller["allowances"] = round(seller["allowances"] + 15, 2)

        state = engine.propose_trade(
            state,
            seller_company_id=seller["company_id"],
            buyer_company_id=buyer["company_id"],
            quantity=5,
            price_per_allowance=125,
            now=utc(second=7),
        )

        self.assertEqual(len(state["trades"]), 1)
        self.assertEqual(state["trades"][0]["status"], "proposed")

    def test_trade_acceptance_settles_allowances_and_cash(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        seller = state["companies"][0]
        buyer = state["companies"][1]
        seller["allowances"] = round(seller["allowances"] + 12, 2)
        seller_cash_before = seller["cash"]
        buyer_cash_before = buyer["cash"]
        seller_allowances_before = seller["allowances"]
        buyer_allowances_before = buyer["allowances"]

        state = engine.propose_trade(
            state,
            seller_company_id=seller["company_id"],
            buyer_company_id=buyer["company_id"],
            quantity=4,
            price_per_allowance=140,
            now=utc(second=7),
        )
        trade_id = state["trades"][0]["trade_id"]

        settled = engine.respond_to_trade(
            state,
            trade_id=trade_id,
            responder_company_id=buyer["company_id"],
            response="accept",
            now=utc(second=8),
        )

        updated_seller = settled["companies"][0]
        updated_buyer = settled["companies"][1]
        trade = settled["trades"][0]

        self.assertEqual(trade["status"], "accepted")
        self.assertEqual(
            updated_seller["allowances"], round(seller_allowances_before - 4, 2)
        )
        self.assertEqual(
            updated_buyer["allowances"], round(buyer_allowances_before + 4, 2)
        )
        self.assertEqual(
            updated_seller["cash"], round(seller_cash_before + (4 * 140), 2)
        )
        self.assertEqual(updated_buyer["cash"], round(buyer_cash_before - (4 * 140), 2))

    def test_trade_rejection_and_duplicate_acceptance_are_blocked(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        seller = state["companies"][0]
        buyer = state["companies"][1]
        seller["allowances"] = round(seller["allowances"] + 10, 2)

        state = engine.propose_trade(
            state,
            seller_company_id=seller["company_id"],
            buyer_company_id=buyer["company_id"],
            quantity=3,
            price_per_allowance=130,
            now=utc(second=7),
        )
        trade_id = state["trades"][0]["trade_id"]

        rejected = engine.respond_to_trade(
            state,
            trade_id=trade_id,
            responder_company_id=buyer["company_id"],
            response="reject",
            now=utc(second=8),
        )
        self.assertEqual(rejected["trades"][0]["status"], "rejected")

        with self.assertRaises(ValueError):
            engine.respond_to_trade(
                rejected,
                trade_id=trade_id,
                responder_company_id=buyer["company_id"],
                response="accept",
                now=utc(second=9),
            )

    def test_trade_proposal_rejects_insufficient_holdings_and_cash(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        seller = state["companies"][0]
        buyer = state["companies"][1]

        with self.assertRaises(ValueError):
            engine.propose_trade(
                state,
                seller_company_id=seller["company_id"],
                buyer_company_id=buyer["company_id"],
                quantity=999,
                price_per_allowance=120,
                now=utc(second=7),
            )

        seller["allowances"] = round(seller["allowances"] + 15, 2)
        with self.assertRaises(ValueError):
            engine.propose_trade(
                state,
                seller_company_id=seller["company_id"],
                buyer_company_id=buyer["company_id"],
                quantity=5,
                price_per_allowance=999999,
                now=utc(second=7),
            )

    def test_trade_expiration_marks_stale_proposals(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        seller = state["companies"][0]
        buyer = state["companies"][1]
        seller["allowances"] = round(seller["allowances"] + 8, 2)

        state = engine.propose_trade(
            state,
            seller_company_id=seller["company_id"],
            buyer_company_id=buyer["company_id"],
            quantity=2,
            price_per_allowance=110,
            now=utc(second=7),
        )

        expired = engine.advance_state(
            state, datetime(2026, 1, 1, 9, 1, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(expired["trades"][0]["status"], "expired")


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


class FacilitatorControlTests(unittest.TestCase):
    def test_pause_during_decision_window(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.advance_state(state, utc(second=6))

        self.assertEqual(state["phase"], engine.PHASE_DECISION_WINDOW)

        paused = engine.pause_session(state, utc(second=10))

        self.assertEqual(paused["phase"], engine.PHASE_PAUSED)
        self.assertIsNotNone(paused["paused_from"])
        self.assertEqual(paused["phase_before_pause"], engine.PHASE_DECISION_WINDOW)

    def test_resume_from_pause_extends_deadline(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.advance_state(state, utc(second=6))
        original_deadline = state["phase_deadline_at"]

        paused = engine.pause_session(state, utc(second=10))

        resumed = engine.resume_session(paused, utc(second=15))

        self.assertEqual(resumed["phase"], engine.PHASE_DECISION_WINDOW)
        self.assertIsNone(resumed["paused_from"])
        self.assertNotEqual(resumed["phase_deadline_at"], original_deadline)

    def test_cannot_pause_in_lobby_or_complete(self):
        state = engine.create_initial_state(participant_count=3)

        still_lobby = engine.pause_session(state, utc())
        self.assertEqual(still_lobby["phase"], engine.PHASE_LOBBY)

    def test_cannot_resume_when_not_paused(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        unchanged = engine.resume_session(state, utc(second=5))
        self.assertEqual(unchanged["phase"], engine.PHASE_YEAR_START)

    def test_force_advance_from_year_start_to_decision_window(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        self.assertEqual(state["phase"], engine.PHASE_YEAR_START)

        forced = engine.force_advance_phase(state, utc(second=1))

        self.assertEqual(forced["phase"], engine.PHASE_DECISION_WINDOW)

    def test_force_advance_from_decision_window_to_compliance(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.advance_state(state, utc(second=6))

        forced = engine.force_advance_phase(state, utc(second=7))

        self.assertEqual(forced["phase"], engine.PHASE_COMPLIANCE)

    def test_force_advance_from_compliance_to_next_year(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        self.assertEqual(state["phase"], engine.PHASE_DECISION_WINDOW)

        state = engine.force_advance_phase(state, utc(second=2))

        self.assertEqual(state["phase"], engine.PHASE_COMPLIANCE)

        state = engine.force_advance_phase(state, utc(second=3))

        self.assertEqual(state["current_year"], 2)
        self.assertEqual(state["phase"], engine.PHASE_YEAR_START)

    def test_force_advance_from_final_compliance_to_complete(self):
        state = engine.create_initial_state(
            participant_count=3,
            phase_durations={"year_start": 1, "decision_window": 1, "compliance": 1},
        )
        state = engine.start_simulation(state, utc())

        for year in range(3):
            if state["current_year"] != year + 1:
                pass
            state = engine.advance_state(state, utc(second=2 + (year * 3)))
            state = engine.advance_state(state, utc(second=4 + (year * 3)))
            if year < 2:
                state = engine.advance_state(state, utc(second=6 + (year * 3)))
                state = engine.advance_state(state, utc(second=7 + (year * 3)))

        state = engine.advance_state(state, utc(second=10))

        if state["phase"] != engine.PHASE_COMPLETE:
            state = engine.force_advance_phase(state, utc(second=12))
            if state["phase"] == engine.PHASE_COMPLIANCE and state["current_year"] >= 3:
                state = engine.force_advance_phase(state, utc(second=13))

        self.assertEqual(state["phase"], engine.PHASE_COMPLETE)

    def test_cannot_force_advance_from_lobby(self):
        state = engine.create_initial_state(participant_count=3)

        unchanged = engine.force_advance_phase(state, utc())

        self.assertEqual(unchanged["phase"], engine.PHASE_LOBBY)

    def test_cannot_force_advance_while_paused(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        paused = engine.pause_session(state, utc(second=1))

        unchanged = engine.force_advance_phase(paused, utc(second=2))

        self.assertEqual(unchanged["phase"], engine.PHASE_PAUSED)

    def test_pause_and_resume_log_audit_events(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.advance_state(state, utc(second=6))

        state = engine.pause_session(state, utc(second=10))
        pause_events = [
            e for e in state["audit_log"] if e["event_type"] == "session_paused"
        ]
        self.assertEqual(len(pause_events), 1)

        state = engine.resume_session(state, utc(second=15))
        resume_events = [
            e for e in state["audit_log"] if e["event_type"] == "session_resumed"
        ]
        self.assertEqual(len(resume_events), 1)

    def test_advance_state_ignores_phase_while_paused(self):
        state = engine.create_initial_state(
            participant_count=3,
            phase_durations={"year_start": 1, "decision_window": 1, "compliance": 1},
        )
        state = engine.start_simulation(state, utc())
        state = engine.pause_session(state, utc(second=0))

        state = engine.advance_state(state, utc(second=30))

        self.assertEqual(state["phase"], engine.PHASE_PAUSED)


class ParticipantStatusTests(unittest.TestCase):
    def test_update_participant_status_records_last_seen(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.advance_state(state, utc(second=6))

        state = engine.update_participant_status(
            state, company_id="C01", action="activate_abatement", now=utc(second=8)
        )

        status = state["participant_status"]["C01"]
        self.assertIsNotNone(status["last_seen"])
        self.assertEqual(status["last_action"], "activate_abatement")

    def test_decision_counter_increments_for_key_actions(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.advance_state(state, utc(second=6))

        state = engine.update_participant_status(
            state, company_id="C01", action="activate_abatement", now=utc(second=8)
        )
        state = engine.update_participant_status(
            state, company_id="C01", action="buy_offsets", now=utc(second=9)
        )

        self.assertEqual(
            state["participant_status"]["C01"]["decision_count_this_year"], 2
        )


def test_decision_counter_resets_on_new_year(self):
    state = engine.create_initial_state(participant_count=3)
    state = engine.start_simulation(state, utc())
    state = engine.force_advance_phase(state, utc(second=1))
    state = engine.update_participant_status(
        state, company_id="C01", action="activate_abatement", now=utc(second=2)
    )
    self.assertEqual(state["participant_status"]["C01"]["decision_count_this_year"], 1)

    state = engine.force_advance_phase(state, utc(second=3))
    state = engine.force_advance_phase(state, utc(second=4))

    self.assertEqual(state["current_year"], 2)
    self.assertEqual(state["participant_status"]["C01"]["decision_count_this_year"], 0)


class ExportAndSummaryTests(unittest.TestCase):
    def _completed_session(self):
        state = engine.create_initial_state(
            participant_count=3,
            phase_durations={"year_start": 1, "decision_window": 1, "compliance": 1},
        )
        state = engine.start_simulation(state, utc())

        for year in range(3):
            state = engine.advance_state(state, utc(second=2 + year * 3))
            if state["phase"] != engine.PHASE_COMPLETE:
                state = engine.advance_state(state, utc(second=4 + year * 3))
            if state["phase"] != engine.PHASE_COMPLETE:
                state = engine.advance_state(state, utc(second=6 + year * 3))
            if state["phase"] != engine.PHASE_COMPLETE:
                state = engine.advance_state(state, utc(second=7 + year * 3))

        if state["phase"] != engine.PHASE_COMPLETE:
            state = engine.force_advance_phase(state, utc(second=30))

        return state

    def test_export_session_data_contains_companies_trades_and_rankings(self):
        state = self._completed_session()
        export = engine.export_session_data(state)

        self.assertEqual(len(export["companies"]), 3)
        self.assertIn("auctions", export)
        self.assertIn("trades", export)
        self.assertIn("rankings", export)
        self.assertIn("audit_log", export)
        self.assertEqual(export["phase"], engine.PHASE_COMPLETE)

    def test_export_rankings_are_sorted_by_penalties(self):
        state = self._completed_session()
        export = engine.export_session_data(state)

        rankings = export["rankings"]
        self.assertEqual(len(rankings), 3)
        for i in range(len(rankings) - 1):
            self.assertLessEqual(
                rankings[i]["cumulative_penalties"],
                rankings[i + 1]["cumulative_penalties"],
            )

    def test_export_includes_year_results_for_each_company(self):
        state = self._completed_session()
        export = engine.export_session_data(state)

        for company in export["companies"]:
            self.assertIn("year_results", company)
            self.assertEqual(len(company["year_results"]), 3)

    def test_session_summary_has_headline_and_facilitator_notes(self):
        state = self._completed_session()
        summary = engine.build_session_summary(state)

        self.assertIn("headline", summary)
        self.assertIn("facilitator_notes", summary)
        self.assertIn("rankings", summary)
        self.assertIn("year_summaries", summary)
        self.assertEqual(len(summary["rankings"]), 3)

    def test_session_summary_aggregates_market_metrics(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        summary = engine.build_session_summary(state)

        self.assertIn("total_penalties_across_all_companies", summary)
        self.assertIn("total_trades_completed", summary)
        self.assertIn("average_clearing_price", summary)

    def test_facilitator_snapshot_shows_participant_rows(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.update_participant_status(
            state, company_id="C01", action="activate_abatement", now=utc(second=2)
        )

        snap = engine.build_facilitator_snapshot(state, now=utc(second=3))

        self.assertEqual(len(snap["participant_rows"]), 3)
        self.assertEqual(snap["participant_rows"][0]["company_id"], "C01")
        self.assertEqual(snap["participant_rows"][0]["decisions_this_year"], 1)
        self.assertTrue(snap["can_pause"])

    def test_facilitator_snapshot_shows_auction_log(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        snap = engine.build_facilitator_snapshot(state, now=utc(second=1))
        self.assertGreaterEqual(len(snap["auction_log"]), 1)
        self.assertEqual(snap["auction_log"][0]["status"], "scheduled")


class ScenarioAndBotTests(unittest.TestCase):
    def test_scenario_pack_vietnam_pilot_loads(self):
        pack = engine.SCENARIO_PACKS["vietnam_pilot"]
        self.assertEqual(pack["num_years"], 3)
        self.assertEqual(pack["penalty_rate"], 200.0)
        self.assertEqual(len(pack["company_library"]), 3)
        self.assertIn("thermal_power", pack["abatement_catalog"])

    def test_scenario_pack_high_pressure_has_tighter_allocations(self):
        pack = engine.SCENARIO_PACKS["high_pressure"]
        self.assertEqual(pack["penalty_rate"], 350.0)
        self.assertLess(
            pack["allocation_factors"][3],
            engine.SCENARIO_PACKS["vietnam_pilot"]["allocation_factors"][3],
        )

    def test_scenario_pack_generous_has_higher_allocations(self):
        pack = engine.SCENARIO_PACKS["generous"]
        self.assertEqual(pack["penalty_rate"], 120.0)
        self.assertGreater(
            pack["allocation_factors"][1],
            engine.SCENARIO_PACKS["vietnam_pilot"]["allocation_factors"][1],
        )

    def test_create_initial_state_with_scenario(self):
        state = engine.create_initial_state(
            participant_count=3, scenario="high_pressure"
        )
        self.assertEqual(state["penalty_rate"], 350.0)
        self.assertEqual(state["offset_usage_cap"], 0.05)
        self.assertEqual(state["scenario"], "high_pressure")

    def test_create_initial_state_with_bots(self):
        state = engine.create_initial_state(participant_count=2, bot_count=1)
        self.assertEqual(state["participant_count"], 2)
        self.assertEqual(state["total_count"], 3)
        self.assertEqual(len(state["companies"]), 3)
        human_companies = [c for c in state["companies"] if not c.get("is_bot")]
        bot_companies = [c for c in state["companies"] if c.get("is_bot")]
        self.assertEqual(len(human_companies), 2)
        self.assertEqual(len(bot_companies), 1)
        self.assertIsNotNone(bot_companies[0]["bot_strategy"])

    def test_bot_companies_have_strategy_flag(self):
        state = engine.create_initial_state(participant_count=2, bot_count=2)
        bot_companies = [c for c in state["companies"] if c.get("is_bot")]
        for bot in bot_companies:
            self.assertTrue(bot["is_bot"])
            self.assertEqual(bot["bot_strategy"], engine.BOT_STRATEGY_MODERATE)

    def test_run_bot_turns_activates_abatement_in_decision_window(self):
        state = engine.create_initial_state(participant_count=2, bot_count=1)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        state = engine.run_bot_turns(state, now=utc(second=2))

        bot = next(c for c in state["companies"] if c.get("is_bot"))
        self.assertGreater(len(bot["active_abatement_ids"]), 0)

    def test_run_bot_turns_does_nothing_outside_decision_window(self):
        state = engine.create_initial_state(participant_count=2, bot_count=1)
        state = engine.start_simulation(state, utc())

        state = engine.run_bot_turns(state, now=utc(second=1))

        bot = next(c for c in state["companies"] if c.get("is_bot"))
        self.assertEqual(len(bot["active_abatement_ids"]), 0)

    def test_run_bot_turns_buys_offsets_when_compliance_gap_exists(self):
        state = engine.create_initial_state(
            participant_count=2, bot_count=1, bot_strategy="moderate"
        )
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        state = engine.run_bot_turns(state, now=utc(second=2))

        bot = next(c for c in state["companies"] if c.get("is_bot"))
        if bot["compliance_gap"] > 0:
            self.assertGreater(bot["offset_holdings"], 0)

    def test_run_bot_turns_conservative_strategy_is_less_aggressive(self):
        state_conservative = engine.create_initial_state(
            participant_count=2, bot_count=1, bot_strategy="conservative"
        )
        state_aggressive = engine.create_initial_state(
            participant_count=2, bot_count=1, bot_strategy="aggressive"
        )

        state_conservative = engine.start_simulation(state_conservative, utc())
        state_conservative = engine.force_advance_phase(
            state_conservative, utc(second=1)
        )
        state_conservative = engine.run_bot_turns(state_conservative, now=utc(second=2))

        state_aggressive = engine.start_simulation(state_aggressive, utc())
        state_aggressive = engine.force_advance_phase(state_aggressive, utc(second=1))
        state_aggressive = engine.run_bot_turns(state_aggressive, now=utc(second=2))

        bot_conservative = next(
            c for c in state_conservative["companies"] if c.get("is_bot")
        )
        bot_aggressive = next(
            c for c in state_aggressive["companies"] if c.get("is_bot")
        )
        self.assertLessEqual(
            len(bot_conservative["active_abatement_ids"]),
            len(bot_aggressive["active_abatement_ids"]),
        )

    def test_scenario_allocation_factors_override_defaults(self):
        state = engine.create_initial_state(
            participant_count=3, scenario="high_pressure"
        )
        state = engine.start_simulation(state, utc())
        year1_allocation = state["companies"][0]["current_year_allocation"]
        projected = state["companies"][0]["projected_emissions"]
        expected_factor = engine.SCENARIO_PACKS["high_pressure"]["allocation_factors"][
            1
        ]
        self.assertAlmostEqual(
            year1_allocation, round(projected * expected_factor, 2), places=1
        )

    def test_scenario_abatement_catalog_differs_from_default(self):
        state_default = engine.create_initial_state(
            participant_count=3, scenario="vietnam_pilot"
        )
        state_generous = engine.create_initial_state(
            participant_count=3, scenario="generous"
        )

        default_tp_amount = state_default["companies"][0]["abatement_menu"][0][
            "abatement_amount"
        ]
        generous_tp_amount = state_generous["companies"][0]["abatement_menu"][0][
            "abatement_amount"
        ]
        self.assertNotEqual(default_tp_amount, generous_tp_amount)


class ShockEventTests(unittest.TestCase):
    def test_emissions_spike_increases_projected_emissions(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        original_emissions = state["companies"][0]["projected_emissions"]
        original_gap = state["companies"][0]["compliance_gap"]

        state = engine.apply_shock(
            state, shock_type="emissions_spike", magnitude=0.15, now=utc(second=3)
        )

        self.assertGreater(
            state["companies"][0]["projected_emissions"], original_emissions
        )
        self.assertGreater(state["companies"][0]["compliance_gap"], original_gap)
        self.assertEqual(len(state["active_shocks"]), 1)

    def test_allowance_withdrawal_reduces_holdings(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        original_allowances = state["companies"][0]["allowances"]

        state = engine.apply_shock(
            state, shock_type="allowance_withdrawal", magnitude=0.2, now=utc(second=3)
        )

        self.assertLess(state["companies"][0]["allowances"], original_allowances)
        self.assertGreater(state["companies"][0]["compliance_gap"], 0)

    def test_cost_shock_reduces_cash(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        original_cash = state["companies"][0]["cash"]

        state = engine.apply_shock(
            state, shock_type="cost_shock", magnitude=0.1, now=utc(second=3)
        )

        self.assertLess(state["companies"][0]["cash"], original_cash)

    def test_offset_supply_change_modifies_cap(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        original_cap = state["offset_usage_cap"]

        state = engine.apply_shock(
            state, shock_type="offset_supply_change", magnitude=0.5, now=utc(second=3)
        )

        self.assertNotEqual(state["offset_usage_cap"], original_cap)

    def test_shock_cannot_be_applied_in_lobby(self):
        state = engine.create_initial_state(participant_count=3)

        unchanged = engine.apply_shock(
            state, shock_type="emissions_spike", magnitude=0.1, now=utc()
        )

        self.assertEqual(len(unchanged.get("active_shocks", [])), 0)

    def test_shock_cannot_be_applied_in_complete(self):
        state = engine.create_initial_state(
            participant_count=3,
            phase_durations={"year_start": 1, "decision_window": 1, "compliance": 1},
        )
        state = engine.start_simulation(state, utc())
        state = engine.advance_state(state, utc(second=20))

        unchanged = engine.apply_shock(
            state, shock_type="emissions_spike", magnitude=0.1, now=utc(second=25)
        )

        self.assertEqual(len(unchanged.get("active_shocks", [])), 0)

    def test_shock_events_are_recorded_in_audit_log(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        state = engine.apply_shock(
            state, shock_type="cost_shock", magnitude=0.1, now=utc(second=3)
        )

        shock_events = [
            e for e in state["audit_log"] if e["event_type"] == "shock_cost_shock"
        ]
        self.assertEqual(len(shock_events), 1)
        self.assertEqual(shock_events[0]["details"]["magnitude"], 0.1)

    def test_shock_appears_in_facilitator_snapshot(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))
        state = engine.apply_shock(
            state, shock_type="emissions_spike", magnitude=0.1, now=utc(second=3)
        )

        snap = engine.build_facilitator_snapshot(state, now=utc(second=4))
        self.assertEqual(len(snap["active_shocks"]), 1)
        self.assertEqual(snap["active_shocks"][0]["shock_type"], "emissions_spike")

    def test_shock_appears_in_export_data(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))
        state = engine.apply_shock(
            state, shock_type="allowance_withdrawal", magnitude=0.2, now=utc(second=3)
        )

        export = engine.export_session_data(state)
        shock_audit = [e for e in export["audit_log"] if "shock" in e["event_type"]]
        self.assertGreater(len(shock_audit), 0)


if __name__ == "__main__":
    unittest.main()
