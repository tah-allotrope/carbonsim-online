from __future__ import annotations

import random
import unittest
from datetime import datetime, timezone, timedelta

from engine import engine
from engine.cards import CardDeck, draw_cards, resolve_card


def utc(seconds=0):
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)


class PolicyStabilityStateTests(unittest.TestCase):
    def test_initial_state_has_policy_fields(self):
        state = engine.create_initial_state(participant_count=2)
        self.assertEqual(state["policy_stability"], 70.0)
        self.assertEqual(state["active_conditions"], [])
        self.assertEqual(state["active_effects"], [])
        self.assertEqual(state["pending_card_injections"], [])

    def test_cap_modifier_neutral_at_default_stability(self):
        # At the starting stability of 70, the cap modifier must be exactly 1.0
        # so a fresh game keeps the pre-Sprint-4 balance.
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        self.assertAlmostEqual(state["cap_modifier"], 1.0)

    def test_clean_year_raises_stability(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        # Make everyone over-compliant so nobody is penalized.
        for c in state["companies"]:
            c["allowances"] = c["projected_emissions"] + 50
        state["policy_stability"] = 60.0
        state = engine.force_advance_phase(state, utc(1))  # -> decision_window
        state = engine.force_advance_phase(state, utc(2))  # -> compliance (closes year)
        self.assertGreater(state["policy_stability"], 60.0)

    def test_high_penalty_year_lowers_stability(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        for c in state["companies"]:
            c["allowances"] = 0.0
            c["offset_holdings"] = 0.0
            engine._recalculate_company_projection(state, c)
        state["policy_stability"] = 70.0
        state = engine.force_advance_phase(state, utc(1))
        state = engine.force_advance_phase(state, utc(2))
        self.assertLess(state["policy_stability"], 70.0)

    def test_low_stability_sets_crackdown_condition(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        state["policy_stability"] = 10.0
        # Advance a full year so _start_year fires the policy triggers next year.
        state = engine.force_advance_phase(state, utc(1))  # decision_window
        state = engine.force_advance_phase(state, utc(2))  # compliance
        state = engine.force_advance_phase(state, utc(3))  # next year_start
        self.assertIn("regulatory_crackdown", state["active_conditions"])

    def test_snapshot_exposes_policy_climate(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        snap = engine.build_player_snapshot(
            state, company_id="C01", is_facilitator=False,
            participant_label="P", now=utc(3),
        )
        self.assertIn("policy_stability", snap)
        self.assertEqual(snap["policy_climate"], "stable")
        self.assertIn("active_conditions", snap)


class CascadingCardTests(unittest.TestCase):
    def setUp(self):
        self.state = engine.create_initial_state(participant_count=2)
        self.state = engine.start_simulation(self.state, utc())
        self.state = engine.force_advance_phase(self.state, utc(1))

    def test_sets_condition_records_flag(self):
        card = {
            "card_id": "x", "title": "X", "description": "d", "category": "crisis",
            "effect_type": "none", "effect_params": {},
            "sets_condition": "regulator_watching",
            "prerequisites": {"min_year": 1, "max_year": 20}, "weight": 1,
        }
        self.state = resolve_card(self.state, card, now=utc(2))
        self.assertIn("regulator_watching", self.state["active_conditions"])

    def test_requires_condition_gates_eligibility(self):
        gated = {
            "card_id": "gated", "title": "G", "description": "d", "category": "policy",
            "effect_type": "none", "effect_params": {},
            "requires_condition": "regulator_watching",
            "prerequisites": {"min_year": 1, "max_year": 20}, "weight": 100,
        }
        # Not eligible without the condition.
        deck = CardDeck([dict(gated)])
        self.assertEqual(deck.draw(count=1, state=self.state), [])
        # Eligible once the condition is set.
        self.state["active_conditions"] = ["regulator_watching"]
        deck2 = CardDeck([dict(gated)])
        self.assertEqual(len(deck2.draw(count=1, state=self.state)), 1)

    def test_follow_on_card_is_injected_and_drawn(self):
        parent = {
            "card_id": "parent", "title": "P", "description": "d", "category": "opportunity",
            "effect_type": "none", "effect_params": {},
            "follow_on_cards": ["child"],
            "prerequisites": {"min_year": 1, "max_year": 20}, "weight": 1,
        }
        child = {
            "card_id": "child", "title": "C", "description": "d", "category": "opportunity",
            "effect_type": "cash_boost", "effect_params": {"magnitude": 0.05},
            "prerequisites": {"min_year": 1, "max_year": 20}, "weight": 1,
        }
        self.state = resolve_card(self.state, parent, now=utc(2))
        self.assertIn("child", self.state["pending_card_injections"])
        deck = CardDeck([dict(child)])
        self.state, drawn = draw_cards(self.state, deck, count=1, now=utc(3))
        self.assertEqual(drawn[0]["card_id"], "child")
        self.assertEqual(self.state["pending_card_injections"], [])

    def test_effect_duration_queues_multi_turn_effect(self):
        card = {
            "card_id": "dur", "title": "D", "description": "d", "category": "crisis",
            "effect_type": "emissions_spike", "effect_params": {"magnitude": 0.05},
            "effect_duration": 3,
            "prerequisites": {"min_year": 1, "max_year": 20}, "weight": 1,
        }
        self.state = resolve_card(self.state, card, now=utc(2))
        effects = self.state["active_effects"]
        self.assertEqual(len(effects), 1)
        self.assertEqual(effects[0]["remaining_years"], 2)  # year 1 applied now

    def test_active_effect_applies_and_decrements_each_year(self):
        self.state["active_effects"] = [{
            "effect_type": "cost_shock", "effect_params": {"magnitude": 0.1},
            "remaining_years": 2,
        }]
        cash_before = self.state["companies"][0]["cash"]
        # Advance a full year; _start_year applies the effect then decrements.
        self.state = engine.force_advance_phase(self.state, utc(2))  # compliance
        self.state = engine.force_advance_phase(self.state, utc(3))  # next year_start
        self.assertLess(self.state["companies"][0]["cash"], cash_before)
        self.assertEqual(self.state["active_effects"][0]["remaining_years"], 1)


class StateWeightedDrawTests(unittest.TestCase):
    def _cards(self):
        return [
            {"card_id": "crisis_a", "title": "c", "description": "d", "category": "crisis",
             "effect_type": "none", "effect_params": {}, "prerequisites": {"min_year": 1, "max_year": 20}, "weight": 10},
            {"card_id": "opp_a", "title": "o", "description": "d", "category": "opportunity",
             "effect_type": "none", "effect_params": {}, "prerequisites": {"min_year": 1, "max_year": 20}, "weight": 10},
        ]

    def test_crisis_favored_in_unstable_climate(self):
        state = engine.create_initial_state(participant_count=1)
        state["current_year"] = 1
        state["policy_stability"] = 20.0  # crisis x2
        crisis = 0
        for i in range(200):
            deck = CardDeck([dict(c) for c in self._cards()], rng=random.Random(i))
            drawn = deck.draw(count=1, state=state)
            if drawn[0]["category"] == "crisis":
                crisis += 1
        self.assertGreater(crisis, 120)  # should clearly exceed 50/50


if __name__ == "__main__":
    unittest.main()
