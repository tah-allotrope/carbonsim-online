from datetime import datetime, timezone
import unittest

from engine import engine
from engine.agents import CompanyAgent
from engine.constants import (
    BOT_STRATEGIES,
    BOT_STRATEGY_OPPORTUNISTIC,
    BOT_STRATEGY_SPECULATOR,
)
from engine.playtest import run_strategy_sweep


def utc(second=0):
    return datetime(2026, 1, 1, 9, 0, second, tzinfo=timezone.utc)


def _decision_window(bot_count=2, participant_count=1, scenario=None):
    state = engine.create_initial_state(
        participant_count=participant_count, bot_count=bot_count, scenario=scenario
    )
    state = engine.start_simulation(state, utc())
    state = engine.force_advance_phase(state, utc(second=1))
    return state


class CompanyAgentConstructionTests(unittest.TestCase):
    def test_from_company_reads_strategy_profile(self):
        state = engine.create_initial_state(participant_count=1, bot_count=1)
        bot = next(c for c in state["companies"] if c.get("is_bot"))
        bot["bot_strategy"] = BOT_STRATEGY_OPPORTUNISTIC

        agent = CompanyAgent.from_company(bot)

        self.assertEqual(agent.risk_appetite, BOT_STRATEGY_OPPORTUNISTIC)
        self.assertEqual(
            agent.horizon_years,
            BOT_STRATEGIES[BOT_STRATEGY_OPPORTUNISTIC]["horizon_years"],
        )
        self.assertGreater(len(agent.preferred_instruments), 0)

    def test_five_strategy_profiles_exist(self):
        self.assertEqual(len(BOT_STRATEGIES), 5)
        for profile in BOT_STRATEGIES.values():
            for key in (
                "horizon_years",
                "cash_target_fraction",
                "forward_appetite",
                "vcm_appetite",
                "otc_appetite",
            ):
                self.assertIn(key, profile)


class PlanYearTests(unittest.TestCase):
    def test_plan_year_returns_actions_without_mutating_state(self):
        state = _decision_window(bot_count=1)
        bot = next(c for c in state["companies"] if c.get("is_bot"))
        agent = CompanyAgent.from_company(bot)

        before_cash = bot["cash"]
        before_active = list(bot["active_abatement_ids"])
        actions = agent.plan_year(state)

        self.assertIsInstance(actions, list)
        # plan_year must be side-effect free
        self.assertEqual(bot["cash"], before_cash)
        self.assertEqual(bot["active_abatement_ids"], before_active)

    def test_plan_year_proposes_abatement_when_short(self):
        state = _decision_window(bot_count=1)
        bot = next(c for c in state["companies"] if c.get("is_bot"))
        # Force a clear shortfall so abatement is warranted.
        bot["allowances"] = 0.0
        engine._recalculate_company_projection(state, bot)
        agent = CompanyAgent.from_company(bot)

        actions = agent.plan_year(state)
        kinds = {a["action"] for a in actions}
        self.assertTrue(
            kinds & {"activate_abatement", "buy_offsets", "submit_auction_bid"},
            f"expected a compliance action, got {kinds}",
        )


class DispatchTests(unittest.TestCase):
    def test_run_bot_turns_drives_bots_and_leaves_human_untouched(self):
        state = _decision_window(bot_count=2, participant_count=1)
        human = next(c for c in state["companies"] if not c.get("is_bot"))

        state = engine.run_bot_turns(state, now=utc(second=2))

        self.assertEqual(human["active_abatement_ids"], [])

    def test_speculator_can_propose_otc_trade(self):
        state = _decision_window(bot_count=2, participant_count=1)
        bots = [c for c in state["companies"] if c.get("is_bot")]
        # Seller: surplus allowances + speculator. Buyer: large shortfall.
        seller, buyer = bots[0], bots[1]
        seller["bot_strategy"] = BOT_STRATEGY_SPECULATOR
        seller["allowances"] = seller["projected_emissions"] + 200
        engine._recalculate_company_projection(state, seller)
        buyer["allowances"] = 0.0
        engine._recalculate_company_projection(state, buyer)

        agent = CompanyAgent.from_company(seller)
        actions = agent.plan_year(state)
        self.assertTrue(
            any(a["action"] == "propose_trade" for a in actions),
            "speculator with surplus should propose an OTC trade",
        )

    def test_bot_session_completes_with_agents(self):
        state = engine.create_initial_state(participant_count=1, bot_count=3)
        state = engine.start_simulation(state, utc())
        for _ in range(state["num_years"] * 3):
            if state["phase"] in {engine.PHASE_LOBBY, engine.PHASE_COMPLETE}:
                break
            if state["phase"] == engine.PHASE_DECISION_WINDOW:
                state = engine.run_bot_turns(state, now=utc(second=1))
            state = engine.force_advance_phase(state, utc(second=2))
        self.assertEqual(state["phase"], engine.PHASE_COMPLETE)


class AiSignalsTests(unittest.TestCase):
    def test_ai_market_signals_reports_each_bot(self):
        state = _decision_window(bot_count=2, participant_count=1)
        signals = engine.ai_market_signals(state)

        self.assertEqual(len(signals), 2)
        for sig in signals:
            self.assertIn("strategy", sig)
            self.assertIn("posture", sig)
            self.assertIn("open_trades", sig)


class StrategySweepTests(unittest.TestCase):
    def test_sweep_runs_and_reports_all_strategies(self):
        result = run_strategy_sweep(range(3))

        self.assertEqual(len(result["rows"]), 5)
        self.assertEqual(result["seeds"], 3)
        total_win_rate = sum(r["win_rate"] for r in result["rows"])
        self.assertAlmostEqual(total_win_rate, 1.0, places=2)

    def test_sweep_flags_no_dominant_strategy_over_20_seeds(self):
        result = run_strategy_sweep(range(20))
        self.assertEqual(
            result["dominant_strategies"],
            [],
            f"strategy exceeded 60% win rate: {result['rows']}",
        )


if __name__ == "__main__":
    unittest.main()
