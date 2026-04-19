import importlib
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

from carbonsim_phase12 import engine


def utc(year=2026, month=1, day=1, offset_seconds=0):
    return datetime(year, month, day, 9, 0, tzinfo=timezone.utc) + timedelta(
        seconds=offset_seconds
    )


_platform_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _platform_dir not in sys.path:
    sys.path.insert(0, _platform_dir)


class ConfigurationTests(unittest.TestCase):
    def test_settings_loads_secret_key_from_env(self):
        import settings as settings_module

        self.assertTrue(hasattr(settings_module, "SECRET_KEY"))

    def test_settings_admin_password_reads_env_var(self):
        import settings as settings_module

        original = os.environ.get("OTREE_ADMIN_PASSWORD")
        os.environ["OTREE_ADMIN_PASSWORD"] = "test_deployment_password"
        try:
            importlib.reload(settings_module)
            self.assertEqual(settings_module.ADMIN_PASSWORD, "test_deployment_password")
        finally:
            if original is not None:
                os.environ["OTREE_ADMIN_PASSWORD"] = original
            else:
                del os.environ["OTREE_ADMIN_PASSWORD"]

    def test_settings_room_config_exists(self):
        import settings as settings_module

        room_names = [room["name"] for room in settings_module.ROOMS]
        self.assertIn("workshop_room", room_names)

    def test_environment_config_module_loads(self):
        from carbonsim_phase12 import deployment

        self.assertTrue(
            hasattr(deployment, "HEALTH_CHECK_FIELDS"),
            "deployment module should expose HEALTH_CHECK_FIELDS",
        )

    def test_environment_config_defaults_are_reasonable(self):
        from carbonsim_phase12 import deployment

        self.assertTrue(deployment.HEALTH_CHECK_FIELDS)
        self.assertIsInstance(deployment.SESSION_RECOVERY_ENABLED, bool)


class HealthCheckTests(unittest.TestCase):
    def test_health_check_returns_expected_keys(self):
        state = engine.create_initial_state(participant_count=3)
        from carbonsim_phase12 import deployment

        health = deployment.health_check(state)
        for key in deployment.HEALTH_CHECK_FIELDS:
            self.assertIn(key, health, f"health_check missing key: {key}")

    def test_health_check_reports_lobby_phase_for_fresh_state(self):
        state = engine.create_initial_state(participant_count=3)
        from carbonsim_phase12 import deployment

        health = deployment.health_check(state)
        self.assertEqual(health["phase"], engine.PHASE_LOBBY)
        self.assertEqual(health["current_year"], 0)

    def test_health_check_reports_active_session(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        from carbonsim_phase12 import deployment

        health = deployment.health_check(state)
        self.assertEqual(health["phase"], engine.PHASE_YEAR_START)
        self.assertEqual(health["current_year"], 1)
        self.assertEqual(health["participant_count"], 3)
        self.assertGreater(health["total_companies"], 0)

    def test_health_check_reports_paused_state(self):
        state = engine.create_initial_state(participant_count=3)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(offset_seconds=1))
        state = engine.pause_session(state, utc(offset_seconds=2))
        from carbonsim_phase12 import deployment

        health = deployment.health_check(state)
        self.assertEqual(health["phase"], engine.PHASE_PAUSED)
        self.assertTrue(health["is_paused"])

    def test_health_check_reports_complete_state(self):
        state = engine.create_initial_state(
            participant_count=2,
            phase_durations={"year_start": 1, "decision_window": 1, "compliance": 1},
        )
        state = engine.start_simulation(state, utc())
        for step in range(6):
            state = engine.advance_state(state, utc(offset_seconds=step * 5 + 10))
        from carbonsim_phase12 import deployment

        health = deployment.health_check(state)
        self.assertEqual(health["phase"], engine.PHASE_COMPLETE)
        self.assertTrue(health["is_complete"])


class SessionRecoveryTests(unittest.TestCase):
    def test_reconnect_company_restores_state(self):
        state = engine.create_initial_state(participant_count=3)
        from carbonsim_phase12 import deployment

        company = state["companies"][0]
        recovered = deployment.reconnect_company(state, company["company_id"])
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered["company_name"], company["company_name"])
        self.assertIn("allowances", recovered)
        self.assertEqual(recovered["company_id"], company["company_id"])

    def test_reconnect_company_preserves_holdings_after_decisions(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(offset_seconds=1))
        from carbonsim_phase12 import deployment

        company = state["companies"][0]
        original_allowances = company["allowances"]
        recovered = deployment.reconnect_company(state, company["company_id"])
        self.assertEqual(recovered["allowances"], original_allowances)

    def test_reconnect_company_returns_none_for_invalid_id(self):
        state = engine.create_initial_state(participant_count=3)
        from carbonsim_phase12 import deployment

        self.assertIsNone(deployment.reconnect_company(state, "INVALID_ID"))

    def test_get_company_role_returns_participant_for_non_facilitator(self):
        state = engine.create_initial_state(participant_count=3)
        from carbonsim_phase12 import deployment

        self.assertEqual(
            deployment.get_company_role(state, state["companies"][1]["company_id"]),
            "participant",
        )

    def test_get_company_role_returns_facilitator_for_first_company(self):
        state = engine.create_initial_state(participant_count=3)
        from carbonsim_phase12 import deployment

        self.assertEqual(
            deployment.get_company_role(state, state["companies"][0]["company_id"]),
            "facilitator",
        )

    def test_validate_facilitator_action_returns_true_for_facilitator(self):
        from carbonsim_phase12 import deployment

        self.assertTrue(deployment.validate_facilitator_action(is_facilitator=True))

    def test_validate_facilitator_action_returns_false_for_non_facilitator(self):
        from carbonsim_phase12 import deployment

        self.assertFalse(deployment.validate_facilitator_action(is_facilitator=False))

    def test_validate_decision_action_returns_true_in_decision_window(self):
        state = engine.create_initial_state(participant_count=2)
        state = engine.start_simulation(state, utc())
        state = engine.force_advance_phase(state, utc(offset_seconds=1))
        from carbonsim_phase12 import deployment

        self.assertTrue(
            deployment.validate_decision_action(
                state, state["companies"][0]["company_id"]
            )
        )

    def test_validate_decision_action_returns_false_in_lobby(self):
        state = engine.create_initial_state(participant_count=2)
        from carbonsim_phase12 import deployment

        self.assertFalse(
            deployment.validate_decision_action(
                state, state["companies"][0]["company_id"]
            )
        )


class StructuredLoggingTests(unittest.TestCase):
    def test_format_event_creates_structured_dict(self):
        from carbonsim_phase12 import deployment

        event = deployment.format_audit_event(
            event_type="session_started",
            year=1,
            details={"num_companies": 3},
            session_id="test-session-001",
        )
        self.assertEqual(event["event_type"], "session_started")
        self.assertEqual(event["year"], 1)
        self.assertEqual(event["session_id"], "test-session-001")
        self.assertIn("timestamp", event)

    def test_format_event_includes_all_required_fields(self):
        from carbonsim_phase12 import deployment

        event = deployment.format_audit_event(
            event_type="auction_cleared",
            year=2,
            details={"clearing_price": 120.0},
            session_id="s2",
        )
        self.assertIn("event_type", event)
        self.assertIn("year", event)
        self.assertIn("details", event)
        self.assertIn("session_id", event)
        self.assertIn("timestamp", event)


class ExportIntegrityTests(unittest.TestCase):
    def test_full_three_year_export_has_complete_data(self):
        state = engine.create_initial_state(
            participant_count=3,
            phase_durations={"year_start": 1, "decision_window": 1, "compliance": 1},
        )
        state = engine.start_simulation(state, utc())
        for step in range(9):
            state = engine.advance_state(state, utc(offset_seconds=step * 10 + 10))

        export = engine.export_session_data(state)
        self.assertIn("companies", export)
        self.assertIn("auctions", export)
        self.assertIn("trades", export)
        self.assertIn("rankings", export)
        self.assertIn("audit_log", export)
        self.assertEqual(len(export["companies"]), 3)

    def test_export_includes_year_results(self):
        state = engine.create_initial_state(
            participant_count=2,
            phase_durations={"year_start": 1, "decision_window": 1, "compliance": 1},
        )
        state = engine.start_simulation(state, utc())
        for step in range(6):
            state = engine.advance_state(state, utc(offset_seconds=step * 10 + 10))

        export = engine.export_session_data(state)
        for company in export["companies"]:
            self.assertGreater(len(company["year_results"]), 0)

    def test_session_summary_has_debrief_sections(self):
        state = engine.create_initial_state(
            participant_count=2,
            phase_durations={"year_start": 1, "decision_window": 1, "compliance": 1},
        )
        state = engine.start_simulation(state, utc())
        for step in range(6):
            state = engine.advance_state(state, utc(offset_seconds=step * 10 + 10))

        summary = engine.build_session_summary(state)
        self.assertIn("headline", summary)
        self.assertIn("year_summaries", summary)
        self.assertIn("rankings", summary)
        self.assertIn("total_trades_completed", summary)
        self.assertIn("average_clearing_price", summary)


if __name__ == "__main__":
    unittest.main()
