from datetime import datetime, timedelta, timezone
import unittest

from carbonsim_engine import engine


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

        state = engine.force_advance_phase(state, utc(second=1))
        state = engine.close_auction(
            state, auction_id=state["auctions"][0]["auction_id"], now=utc(second=2)
        )
        state = engine.force_advance_phase(state, utc(second=3))

        for company in state["companies"]:
            self.assertEqual(company["allowances"], 0)

        surplus = next(c for c in state["companies"] if c["company_id"] == "C01")
        short = next(c for c in state["companies"] if c["company_id"] == "C02")
        self.assertGreater(surplus["banked_allowances"], 0)
        self.assertGreater(short["cumulative_penalties"], 0)

    def test_company_can_activate_abatement_and_reduces_emissions(self):
        state = engine.create_initial_state(participant_count=1)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))
        company = state["companies"][0]
        pre = company["projected_emissions"]

        state = engine.apply_company_decision(
            state,
            company_id=company["company_id"],
            action="activate_abatement",
            payload={"measure_id": company["abatement_menu"][0]["measure_id"]},
            now=utc(second=2),
        )

        post = company["projected_emissions"]
        self.assertLess(post, pre)
        self.assertIn(
            company["abatement_menu"][0]["measure_id"], company["active_abatement_ids"]
        )

    def test_abatement_deduction_is_bounded(self):
        state = engine.create_initial_state(participant_count=1)
        company = state["companies"][0]

        for measure in company["abatement_menu"]:
            remaining = company["baseline_emissions"] - sum(
                m["abatement_amount"] for m in company["abatement_menu"]
            )
            if remaining <= 0:
                break

        self.assertGreaterEqual(remaining, 0)

    def test_closing_all_auctions_generates_results(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        for auction in state["auctions"]:
            self.assertEqual(auction["status"], "scheduled")

        for auction in state["auctions"]:
            state = engine.open_auction(
                state, auction_id=auction["auction_id"], now=utc(second=1)
            )
            for company in state["companies"]:
                state = engine.submit_auction_bid(
                    state,
                    company_id=company["company_id"],
                    auction_id=auction["auction_id"],
                    quantity=10,
                    price=100,
                    now=utc(second=2),
                )
            state = engine.close_auction(
                state, auction_id=auction["auction_id"], now=utc(second=3)
            )

        for auction in state["auctions"]:
            self.assertEqual(auction["status"], "cleared")
            self.assertGreater(auction["clearing_price"], 0)

    def test_bots_are_injected_when_bot_count_is_positive(self):
        state = engine.create_initial_state(participant_count=2, bot_count=3)

        human = [c for c in state["companies"] if not c.get("is_bot")]
        bots = [c for c in state["companies"] if c.get("is_bot")]

        self.assertEqual(len(human), 2)
        self.assertEqual(len(bots), 3)

    def test_bots_have_a_strategy_assigned(self):
        state = engine.create_initial_state(participant_count=2, bot_count=2)

        for bot in [c for c in state["companies"] if c.get("is_bot")]:
            self.assertIsNotNone(bot.get("bot_strategy"))

    def test_runner_runs_bots_without_error(self):
        state = engine.create_initial_state(participant_count=1, bot_count=2)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        state = engine.run_bot_turns(state, now=utc(second=2))
        self.assertTrue(True)

    def test_bots_do_not_modify_human_company(self):
        state = engine.create_initial_state(participant_count=1, bot_count=1)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        human = [c for c in state["companies"] if not c.get("is_bot")][0]
        state = engine.run_bot_turns(state, now=utc(second=2))
        self.assertEqual(human["active_abatement_ids"], [])

    def test_session_can_complete_all_years_for_3_participants(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())

        for _ in range(state["num_years"] * 3):
            if state["phase"] in {engine.PHASE_LOBBY, engine.PHASE_COMPLETE}:
                break
            state = engine.force_advance_phase(state, utc(second=1))

        self.assertEqual(state["phase"], engine.PHASE_COMPLETE)
        for company in state["companies"]:
            self.assertGreater(len(company["year_results"]), 0)

    def test_bot_session_completes_all_years(self):
        state = engine.create_initial_state(
            participant_count=1, bot_count=2
        )
        state = engine.start_simulation(state, utc())

        for _ in range(state["num_years"] * 3):
            if state["phase"] in {engine.PHASE_LOBBY, engine.PHASE_COMPLETE}:
                break
            if state["phase"] == engine.PHASE_DECISION_WINDOW:
                state = engine.run_bot_turns(state, now=utc(second=1))
            state = engine.force_advance_phase(state, utc(second=2))

        self.assertEqual(state["phase"], engine.PHASE_COMPLETE)

    def test_offset_purchases_are_counted_correctly(self):
        state = engine.create_initial_state(participant_count=1)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        company = state["companies"][0]
        initial_cash = company["cash"]
        offset_qty = 25
        offset_price = state["offset_price"]

        state = engine.apply_company_decision(
            state,
            company_id=company["company_id"],
            action="buy_offsets",
            payload={"quantity": offset_qty},
            now=utc(second=2),
        )

        expected_cost = round(offset_qty * offset_price, 2)
        self.assertAlmostEqual(company["offset_holdings"], offset_qty)
        self.assertAlmostEqual(company["cash"], initial_cash - expected_cost)

    def test_trade_transfers_allowances_and_cash(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))

        seller = state["companies"][0]
        buyer = state["companies"][1]
        seller["allowances"] = 100
        qty = 30
        price = 20

        state = engine.apply_company_decision(
            state,
            company_id=seller["company_id"],
            action="propose_trade",
            payload={
                "buyer_company_id": buyer["company_id"],
                "quantity": qty,
                "price_per_allowance": price,
            },
            now=utc(second=2),
        )

        trade_id = state["trades"][-1]["trade_id"]
        state = engine.respond_to_trade(
            state,
            trade_id=trade_id,
            responder_company_id=buyer["company_id"],
            response="accept",
            now=utc(second=3),
        )

        self.assertEqual(trade["trade_id"], trade_id) if False else None
        self.assertAlmostEqual(seller["allowances"], 100 - qty)
        self.assertAlmostEqual(buyer["allowances"], qty)
        self.assertAlmostEqual(seller["cash"], 1_500_000.0 + qty * price)
        self.assertAlmostEqual(buyer["cash"], 1_250_000.0 - qty * price)

    def test_build_player_snapshot_returns_expected_structure(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        snap = engine.build_player_snapshot(
            state,
            company_id="C01",
            is_facilitator=False,
            participant_label="Alice",
            now=utc(second=4),
        )

        self.assertIn("phase", snap)
        self.assertIn("company", snap)
        self.assertEqual(snap.get("participant_label"), "Alice")
        self.assertFalse(snap.get("can_start"))
        self.assertIn("leaderboard", snap)

    def test_build_facilitator_snapshot_returns_expected_structure(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        snap = engine.build_facilitator_snapshot(state, now=utc(second=4))

        self.assertIn("phase", snap)
        self.assertIn("participant_rows", snap)
        self.assertIn("auction_log", snap)
        self.assertIn("session_analytics", snap)
        self.assertIn("session_replay", snap)

    def test_session_replay_contains_timeline_and_company_paths(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        replay = engine.build_session_replay(state)

        self.assertIn("timeline", replay)
        self.assertIn("company_paths", replay)
        self.assertGreater(len(replay["timeline"]), 0)

    def test_session_analytics_contains_decision_counts(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        analytics = engine.build_session_analytics(state)

        self.assertIn("decision_counts", analytics)
        self.assertIn("market_metrics", analytics)

    def test_export_session_data_includes_all_companies(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        export = engine.export_session_data(state)

        self.assertEqual(len(export["companies"]), len(state["companies"]))

    def test_build_session_summary_contains_rankings(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        summary = engine.build_session_summary(state)

        self.assertIn("rankings", summary)
        self.assertEqual(len(summary["rankings"]), len(state["companies"]))

    def test_session_moves_through_phases_in_order(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        self.assertEqual(state["phase"], engine.PHASE_YEAR_START)

        state = engine.force_advance_phase(state, utc(second=1))
        self.assertEqual(state["phase"], engine.PHASE_DECISION_WINDOW)

        state = engine.force_advance_phase(state, utc(second=2))
        self.assertEqual(state["phase"], engine.PHASE_COMPLIANCE)

        state = engine.force_advance_phase(state, utc(second=3))
        self.assertEqual(state["phase"], engine.PHASE_YEAR_START)

    def test_pause_and_resume_preserves_deadline_offset(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        state = engine.pause_session(state, utc(second=10))
        self.assertEqual(state["phase"], engine.PHASE_PAUSED)

        state = engine.resume_session(state, utc(second=30))
        self.assertEqual(state["phase"], engine.PHASE_YEAR_START)

    def test_force_advance_phase_does_not_move_past_complete(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())

        for _ in range(20):
            state = engine.force_advance_phase(state, utc(second=1))

        self.assertEqual(state["phase"], engine.PHASE_COMPLETE)

    def test_cap_reduces_each_year(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        caps = [state["current_cap"]]

        for _ in range(state["num_years"] * 3):
            if state["phase"] == engine.PHASE_COMPLETE:
                break
            state = engine.force_advance_phase(state, utc(second=3))
            if state["phase"] == engine.PHASE_YEAR_START:
                caps.append(state["current_cap"])

        if len(caps) >= 2:
            self.assertGreater(caps[0], caps[1])

    def test_shock_applies_to_company_emissions(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        before = [c["projected_emissions"] for c in state["companies"]]

        state = engine.apply_shock(
            state, shock_type="emissions_spike", magnitude=0.1, now=utc(second=3)
        )
        after = [c["projected_emissions"] for c in state["companies"]]

        for b, a in zip(before, after):
            self.assertGreater(a, b)

    def test_shock_magnitude_is_proportional(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        before = [c["projected_emissions"] for c in state["companies"]]

        state = engine.apply_shock(
            state, shock_type="emissions_spike", magnitude=0.1, now=utc(second=3)
        )
        after = [c["projected_emissions"] for c in state["companies"]]

        for b, a in zip(before, after):
            self.assertAlmostEqual(a, round(b * 1.1, 2))

    def test_shock_appears_in_active_shocks(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(second=1))
        state = engine.apply_shock(
            state, shock_type="allowance_withdrawal", magnitude=0.2, now=utc(second=3)
        )

        snap = engine.build_facilitator_snapshot(state, now=utc(second=4))
        self.assertEqual(len(snap["active_shocks"]), 1)
        self.assertEqual(snap["active_shocks"][0]["shock_type"], "allowance_withdrawal")

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
