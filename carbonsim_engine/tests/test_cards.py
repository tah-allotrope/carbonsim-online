from __future__ import annotations

import json
import random
import unittest
from pathlib import Path

from carbonsim_engine.cards import CardDeck, draw_cards, resolve_card
from carbonsim_engine.engine import create_initial_state, start_simulation, force_advance_phase
from carbonsim_engine.scenarios import SHOCK_CATALOG, TECH_UNLOCK_TEMPLATES


SAMPLE_CARDS = [
    {
        "card_id": "crisis_001",
        "title": "Test Crisis",
        "description": "A test crisis card for unit testing purposes.",
        "category": "crisis",
        "effect_type": "emissions_spike",
        "effect_params": {"magnitude": 0.1},
        "prerequisites": {"min_year": 1, "max_year": 20},
        "weight": 10,
    },
    {
        "card_id": "opportunity_001",
        "title": "Test Opportunity",
        "description": "A test opportunity card for unit testing purposes.",
        "category": "opportunity",
        "effect_type": "cash_boost",
        "effect_params": {"magnitude": 0.05},
        "prerequisites": {"min_year": 1, "max_year": 20},
        "weight": 10,
    },
    {
        "card_id": "policy_001",
        "title": "Late Game Policy",
        "description": "A policy card that only appears after year 5.",
        "category": "policy",
        "effect_type": "election_pressure",
        "effect_params": {"magnitude": -0.03},
        "prerequisites": {"min_year": 5, "max_year": 20},
        "weight": 10,
    },
    {
        "card_id": "market_001",
        "title": "High Cash Card",
        "description": "A card requiring high cash reserves.",
        "category": "market",
        "effect_type": "allowance_boost",
        "effect_params": {"magnitude": 0.1},
        "prerequisites": {"min_year": 1, "max_year": 20, "min_cash": 500000},
        "weight": 10,
    },
]


class TestCardDeck(unittest.TestCase):
    def test_deck_initialization(self):
        deck = CardDeck(SAMPLE_CARDS)
        self.assertEqual(deck.remaining, len(SAMPLE_CARDS))
        self.assertEqual(deck.discarded, 0)

    def test_deck_from_json_list(self):
        deck = CardDeck.from_json(json.dumps(SAMPLE_CARDS))
        self.assertEqual(deck.remaining, len(SAMPLE_CARDS))

    def test_deck_from_json_dict_with_cards_key(self):
        data = json.dumps({"cards": SAMPLE_CARDS})
        deck = CardDeck.from_json(data)
        self.assertEqual(deck.remaining, len(SAMPLE_CARDS))

    def test_deck_from_json_file(self):
        path = Path(__file__).parent.parent / "data" / "starter_deck.json"
        if path.exists():
            deck = CardDeck.from_json(str(path))
            self.assertEqual(deck.remaining, 50)

    def test_draw_returns_correct_count(self):
        deck = CardDeck(SAMPLE_CARDS)
        drawn = deck.draw(count=2)
        self.assertEqual(len(drawn), 2)
        self.assertEqual(deck.remaining, len(SAMPLE_CARDS) - 2)
        self.assertEqual(deck.discarded, 2)

    def test_draw_with_state_filters_by_prerequisites(self):
        state = create_initial_state(participant_count=3)
        state["current_year"] = 1
        drawn = CardDeck(SAMPLE_CARDS).draw(count=4, state=state)
        card_ids = {c["card_id"] for c in drawn}
        self.assertNotIn("policy_001", card_ids, "policy_001 requires year>=5")

    def test_draw_includes_late_game_cards_when_year_high(self):
        state = create_initial_state(participant_count=3)
        state["current_year"] = 6
        drawn = CardDeck(SAMPLE_CARDS).draw(count=4, state=state)
        card_ids = {c["card_id"] for c in drawn}
        self.assertIn("policy_001", card_ids)

    def test_draw_with_seeded_rng_is_deterministic(self):
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        deck1 = CardDeck(SAMPLE_CARDS, rng=rng1)
        deck2 = CardDeck(SAMPLE_CARDS, rng=rng2)
        drawn1 = deck1.draw(count=2)
        drawn2 = deck2.draw(count=2)
        self.assertEqual(drawn1, drawn2)

    def test_draw_different_seeds_give_different_results(self):
        rng1 = random.Random(42)
        rng2 = random.Random(99)
        deck1 = CardDeck(SAMPLE_CARDS, rng=rng1)
        deck2 = CardDeck(SAMPLE_CARDS, rng=rng2)
        drawn1 = deck1.draw(count=2)
        drawn2 = deck2.draw(count=2)
        self.assertNotEqual(
            [c["card_id"] for c in drawn1],
            [c["card_id"] for c in drawn2],
        )

    def test_reshuffle_when_deck_exhausted(self):
        deck = CardDeck(SAMPLE_CARDS[:2])
        deck.draw(count=2)
        self.assertEqual(deck.remaining, 0)
        self.assertEqual(deck.discarded, 2)
        deck._reshuffle()
        self.assertEqual(deck.remaining, 2)
        self.assertEqual(deck.discarded, 0)

    def test_min_cash_filter(self):
        state = create_initial_state(participant_count=1)
        state["current_year"] = 1
        state["companies"][0]["cash"] = 10000
        drawn = CardDeck(SAMPLE_CARDS).draw(count=4, state=state)
        card_ids = {c["card_id"] for c in drawn}
        self.assertNotIn("market_001", card_ids, "market_001 requires min_cash=500000")

    def test_weighted_draw_prefers_higher_weight(self):
        cards = [
            {**SAMPLE_CARDS[0], "card_id": "heavy", "weight": 100},
            {**SAMPLE_CARDS[0], "card_id": "light", "weight": 1},
        ]
        rng = random.Random(0)
        drawn_counts = {"heavy": 0, "light": 0}
        for _ in range(100):
            deck = CardDeck([dict(c) for c in cards], rng=random.Random(_))
            drawn = deck.draw(count=1)
            drawn_counts[drawn[0]["card_id"]] += 1
        self.assertGreater(drawn_counts["heavy"], drawn_counts["light"])


class TestResolveCard(unittest.TestCase):
    def setUp(self):
        self.state = create_initial_state(participant_count=3)
        self.state = start_simulation(self.state, now=self._utc())
        self.state = force_advance_phase(self.state, now=self._utc(seconds=1))

    def _utc(self, **kwargs):
        from datetime import datetime, timezone, timedelta
        secs = kwargs.pop("second", 0) or kwargs.pop("seconds", 0)
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        return base + timedelta(seconds=secs, **kwargs)

    def test_resolve_emissions_spike_card(self):
        before = [c["projected_emissions"] for c in self.state["companies"]]
        card = SAMPLE_CARDS[0]
        self.state = resolve_card(self.state, card, now=self._utc(seconds=5))
        after = [c["projected_emissions"] for c in self.state["companies"]]
        for b, a in zip(before, after):
            self.assertAlmostEqual(a, round(b * 1.1, 2))

    def test_resolve_card_creates_audit_entry(self):
        card = SAMPLE_CARDS[0]
        self.state = resolve_card(self.state, card, now=self._utc(seconds=5))
        events = [e for e in self.state["audit_log"] if e["event_type"] == "card_resolved"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["details"]["card_id"], "crisis_001")

    def test_resolve_card_with_choice(self):
        choice_card = {
            "card_id": "policy_choice",
            "title": "Choice Card",
            "description": "A card with player choices for testing.",
            "category": "policy",
            "effect_type": "none",
            "effect_params": {},
            "prerequisites": {"min_year": 1, "max_year": 20},
            "weight": 5,
            "choices": [
                {
                    "id": "tighten",
                    "label": "Tighten cap",
                    "description": "Reduce offset availability",
                    "effect_type": "offset_supply_change",
                    "effect_params": {"magnitude": -0.2},
                },
                {
                    "id": "loosen",
                    "label": "Loosen cap",
                    "description": "Increase offset availability",
                    "effect_type": "offset_supply_change",
                    "effect_params": {"magnitude": 0.2},
                },
            ],
        }
        original_cap = self.state["offset_usage_cap"]
        self.state = resolve_card(self.state, choice_card, choice_id="loosen", now=self._utc(seconds=5))
        self.assertGreater(self.state["offset_usage_cap"], original_cap)

    def test_resolve_card_saves_choice_in_audit(self):
        choice_card = {
            "card_id": "choice_test",
            "title": "Choice Audit Test",
            "description": "Testing that choice_id is saved in the audit log.",
            "category": "policy",
            "effect_type": "none",
            "effect_params": {},
            "prerequisites": {"min_year": 1, "max_year": 20},
            "weight": 5,
            "choices": [
                {
                    "id": "opt_a",
                    "label": "Option A",
                    "description": "First option",
                    "effect_type": "none",
                    "effect_params": {},
                },
            ],
        }
        self.state = resolve_card(self.state, choice_card, choice_id="opt_a", now=self._utc(seconds=5))
        events = [e for e in self.state["audit_log"] if e["event_type"] == "card_resolved"]
        self.assertEqual(events[0]["details"]["choice_id"], "opt_a")


class TestDrawCardsFunction(unittest.TestCase):
    def setUp(self):
        self.state = create_initial_state(participant_count=3)
        self.state = start_simulation(self.state, now=self._utc())
        self.state = force_advance_phase(self.state, now=self._utc(seconds=1))

    def _utc(self, **kwargs):
        from datetime import datetime, timezone, timedelta
        secs = kwargs.pop("second", 0) or kwargs.pop("seconds", 0)
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        return base + timedelta(seconds=secs, **kwargs)

    def test_draw_cards_returns_drawn_cards(self):
        deck = CardDeck(SAMPLE_CARDS)
        state, drawn = draw_cards(self.state, deck, count=2, now=self._utc(seconds=5))
        self.assertEqual(len(drawn), 2)

    def test_draw_cards_logs_audit_events(self):
        deck = CardDeck(SAMPLE_CARDS)
        state, drawn = draw_cards(self.state, deck, count=2, now=self._utc(seconds=5))
        events = [e for e in state["audit_log"] if e["event_type"] == "card_drawn"]
        self.assertEqual(len(events), 2)


class TestShockCatalog(unittest.TestCase):
    def test_all_effect_types_have_catalog_entries(self):
        expected_types = {
            "emissions_spike", "allowance_withdrawal", "cost_shock",
            "offset_supply_change", "tech_unlock", "fdi_proposal",
            "cbam_threat", "election_pressure", "allowance_boost",
            "cash_boost",
        }
        for etype in expected_types:
            self.assertIn(etype, SHOCK_CATALOG, f"Missing SHOCK_CATALOG entry for {etype}")

    def test_all_shock_types_have_label_and_description(self):
        for stype, entry in SHOCK_CATALOG.items():
            self.assertIn("label", entry, f"Missing label for {stype}")
            self.assertIn("description", entry, f"Missing description for {stype}")
            self.assertIn("applies_to", entry, f"Missing applies_to for {stype}")

    def test_tech_unlock_templates_defined(self):
        self.assertGreater(len(TECH_UNLOCK_TEMPLATES), 0)
        for key, template in TECH_UNLOCK_TEMPLATES.items():
            self.assertIn("measure_label", template, f"Missing measure_label in {key}")
            self.assertIn("abatement_amount", template, f"Missing abatement_amount in {key}")
            self.assertIn("cost", template, f"Missing cost in {key}")


class TestNewShockTypes(unittest.TestCase):
    def setUp(self):
        self.state = create_initial_state(participant_count=3)
        from datetime import datetime, timezone
        self.now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def test_tech_unlock_adds_measure_to_companies(self):
        from carbonsim_engine.engine import apply_shock
        before_count = len(self.state["companies"][0]["abatement_menu"])
        self.state = apply_shock(
            self.state,
            shock_type="tech_unlock",
            magnitude=0,
            shock_params={
                "sector": "all",
                "measure_label": "Test Measure",
                "abatement_amount": 5.0,
                "cost": 10000.0,
                "activation_timing": "immediate",
            },
            now=self.now,
        )
        after_count = len(self.state["companies"][0]["abatement_menu"])
        self.assertEqual(after_count, before_count + 1)
        new_measure = self.state["companies"][0]["abatement_menu"][-1]
        self.assertEqual(new_measure["label"], "Test Measure")

    def test_tech_unlock_sector_specific(self):
        from carbonsim_engine.engine import apply_shock
        self.state["companies"][0]["sector"] = "steel"
        self.state["companies"][1]["sector"] = "cement"
        before_steel = len(self.state["companies"][0]["abatement_menu"])
        before_cement = len(self.state["companies"][1]["abatement_menu"])
        self.state = apply_shock(
            self.state,
            shock_type="tech_unlock",
            magnitude=0,
            shock_params={"sector": "steel", "measure_label": "Steel Only", "abatement_amount": 10.0, "cost": 50000.0, "activation_timing": "immediate"},
            now=self.now,
        )
        self.assertEqual(len(self.state["companies"][0]["abatement_menu"]), before_steel + 1)
        self.assertEqual(len(self.state["companies"][1]["abatement_menu"]), before_cement)

    def test_fdi_proposal_boosts_cash(self):
        from carbonsim_engine.engine import apply_shock
        before = [c["cash"] for c in self.state["companies"]]
        self.state = apply_shock(self.state, shock_type="fdi_proposal", magnitude=0.1, now=self.now)
        after = [c["cash"] for c in self.state["companies"]]
        for b, a in zip(before, after):
            self.assertAlmostEqual(a, round(b * 1.1, 2))

    def test_cbam_threat_increases_penalty_rate(self):
        from carbonsim_engine.engine import apply_shock
        before = self.state["penalty_rate"]
        self.state = apply_shock(self.state, shock_type="cbam_threat", magnitude=0.15, now=self.now)
        self.assertAlmostEqual(self.state["penalty_rate"], round(before * 1.15, 2))

    def test_election_pressure_modifies_allocation_factors(self):
        from carbonsim_engine.engine import apply_shock
        self.state["current_year"] = 2
        self.state["allocation_factors"] = {2: 0.9, 3: 0.85}
        self.state = apply_shock(self.state, shock_type="election_pressure", magnitude=-0.05, now=self.now)
        self.assertAlmostEqual(self.state["allocation_factors"][2], 0.85)
        self.assertAlmostEqual(self.state["allocation_factors"][3], 0.80)

    def test_allowance_boost_adds_allowances(self):
        from carbonsim_engine.engine import apply_shock
        before = [c["allowances"] for c in self.state["companies"]]
        self.state = apply_shock(self.state, shock_type="allowance_boost", magnitude=0.1, now=self.now)
        after = [c["allowances"] for c in self.state["companies"]]
        for b, a in zip(before, after):
            self.assertAlmostEqual(a, round(b * 1.1, 2))

    def test_cash_boost_adds_cash(self):
        from carbonsim_engine.engine import apply_shock
        before = [c["cash"] for c in self.state["companies"]]
        self.state = apply_shock(self.state, shock_type="cash_boost", magnitude=0.08, now=self.now)
        after = [c["cash"] for c in self.state["companies"]]
        for b, a in zip(before, after):
            self.assertAlmostEqual(a, round(b * 1.08, 2))

    def test_shock_appears_in_active_shocks(self):
        from carbonsim_engine.engine import apply_shock
        self.state = apply_shock(self.state, shock_type="tech_unlock", magnitude=0.1, shock_params={"sector": "all", "measure_label": "Test", "abatement_amount": 5.0, "cost": 10000.0, "activation_timing": "immediate"}, now=self.now)
        self.assertEqual(len(self.state["active_shocks"]), 1)
        self.assertEqual(self.state["active_shocks"][0]["shock_type"], "tech_unlock")

    def test_unknown_shock_type_raises(self):
        from carbonsim_engine.engine import apply_shock
        with self.assertRaises(ValueError):
            apply_shock(self.state, shock_type="nonexistent", magnitude=0.1, now=self.now)


if __name__ == "__main__":
    unittest.main()
