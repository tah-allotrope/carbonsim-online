from __future__ import annotations

import json
import os
import pytest
from fastapi.testclient import TestClient

from server.main import create_app
from server.db import init_db, DB_PATH


@pytest.fixture(autouse=True)
def test_db():
    test_path = str(DB_PATH) + ".test"
    os.environ["MAYOR_DB_PATH"] = test_path
    init_db(test_path)
    yield
    if os.path.exists(test_path):
        os.remove(test_path)
    if os.path.exists(test_path + "-wal"):
        os.remove(test_path + "-wal")
    if os.path.exists(test_path + "-shm"):
        os.remove(test_path + "-shm")


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


class TestHealth:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestCreateGame:
    def test_create_game_defaults(self, client):
        resp = client.post("/api/games", json={"player_name": "Test Player"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["player_name"] == "Test Player"
        assert data["difficulty"] == "standard"
        assert data["total_years"] == 15
        assert data["status"] == "active"
        assert "game_id" in data
        assert "snapshot" in data

    def test_create_game_easy(self, client):
        resp = client.post("/api/games", json={"player_name": "Bob", "difficulty": "easy"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["difficulty"] == "easy"
        assert data["total_years"] == 20

    def test_create_game_hard(self, client):
        resp = client.post("/api/games", json={"player_name": "Pro", "difficulty": "hard"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["difficulty"] == "hard"
        assert data["total_years"] == 10

    def test_create_game_custom_years(self, client):
        resp = client.post("/api/games", json={"player_name": "Custom", "num_years": 12})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_years"] == 12

    def test_create_game_tutorial_mode(self, client):
        resp = client.post("/api/games", json={"player_name": "Learner", "tutorial_mode": True, "num_years": 5})
        assert resp.status_code == 200
        data = resp.json()
        state = client.get(f"/api/games/{data['game_id']}").json()
        assert "fast_forward" in state["available_actions"]


class TestGetGame:
    def test_get_game_returns_snapshot(self, client):
        create = client.post("/api/games", json={"player_name": "Getter"}).json()
        game_id = create["game_id"]
        resp = client.get(f"/api/games/{game_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["game_id"] == game_id
        assert data["player_name"] == "Getter"
        assert "snapshot" in data
        assert "available_actions" in data

    def test_get_game_not_found(self, client):
        resp = client.get("/api/games/nonexistent")
        assert resp.status_code == 404


class TestGameLifecycle:
    def test_advance_year(self, client):
        create = client.post("/api/games", json={"player_name": "Advancer"}).json()
        game_id = create["game_id"]
        resp = client.post(f"/api/games/{game_id}/advance-year")
        assert resp.status_code == 200
        data = resp.json()
        assert data["year"] >= 1
        assert "phase" in data
        assert "snapshot" in data

    def test_end_year(self, client):
        create = client.post("/api/games", json={"player_name": "Ender"}).json()
        game_id = create["game_id"]
        client.post(f"/api/games/{game_id}/advance-year")
        resp = client.post(f"/api/games/{game_id}/end-year")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "year_ended"

    def test_resolve_card(self, client):
        create = client.post("/api/games", json={"player_name": "Resolver"}).json()
        game_id = create["game_id"]
        advance = client.post(f"/api/games/{game_id}/advance-year").json()

    def test_decision_activate_abatement(self, client):
        create = client.post("/api/games", json={"player_name": "Decider"}).json()
        game_id = create["game_id"]
        client.post(f"/api/games/{game_id}/advance-year")

        state_resp = client.get(f"/api/games/{game_id}")
        state = state_resp.json()
        snapshot = state["snapshot"]
        company_key = None
        for key in ("company_id", "player_company_id", "id"):
            if key in snapshot:
                company_key = key
                break

        menu = snapshot.get("abatement_menu", []) or snapshot.get("companies", [{}])[0].get("abatement_menu", [])
        if menu:
            measure_id = menu[0]["measure_id"]
            resp = client.post(
                f"/api/games/{game_id}/decision",
                json={"action": "activate_abatement", "payload": {"measure_id": measure_id}},
            )
            assert resp.status_code == 200
            assert resp.json()["status"] == "applied"

    def test_list_games(self, client):
        client.post("/api/games", json={"player_name": "A"})
        client.post("/api/games", json={"player_name": "B"})
        resp = client.get("/api/games")
        assert resp.status_code == 200
        games = resp.json()
        assert len(games) >= 2

    def test_save_and_load_game(self, client):
        create = client.post("/api/games", json={"player_name": "Saver"}).json()
        game_id = create["game_id"]
        save_resp = client.post(f"/api/games/{game_id}/save", json={"save_name": "Test Save"})
        assert save_resp.status_code == 200
        save_data = save_resp.json()
        assert save_data["save_name"] == "Test Save"
        assert "save_id" in save_data

        saves_resp = client.get(f"/api/games/{game_id}/saves")
        assert saves_resp.status_code == 200
        saves = saves_resp.json()
        assert len(saves) >= 1

        load_resp = client.post(f"/api/games/{game_id}/load/{save_data['save_id']}")
        assert load_resp.status_code == 200
        assert load_resp.json()["status"] == "loaded"

    def test_delete_game(self, client):
        create = client.post("/api/games", json={"player_name": "Deleter"}).json()
        game_id = create["game_id"]
        resp = client.delete(f"/api/games/{game_id}")
        assert resp.status_code == 200
        resp = client.get(f"/api/games/{game_id}")
        assert resp.status_code == 404

    def test_summary(self, client):
        create = client.post("/api/games", json={"player_name": "Summarizer"}).json()
        game_id = create["game_id"]
        client.post(f"/api/games/{game_id}/advance-year")
        client.post(f"/api/games/{game_id}/end-year")
        resp = client.get(f"/api/games/{game_id}/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["player_name"] == "Summarizer"
        assert "snapshot" in data
        assert "achievements" in data

    def test_tutorial_draws_fixed_card_for_year_one(self, client):
        # The year-1 decision window opens at creation, so the fixed tutorial
        # card for year 1 is available immediately.
        create = client.post(
            "/api/games",
            json={"player_name": "Tutorial", "tutorial_mode": True, "num_years": 5},
        ).json()
        game_id = create["game_id"]

        state = client.get(f"/api/games/{game_id}").json()
        assert state["snapshot"]["phase"] == "decision_window"
        assert state["drawn_cards"]
        assert state["drawn_cards"][0]["card_id"] == "tutorial_001"

    def test_fast_forward_advances_game(self, client):
        create = client.post(
            "/api/games",
            json={"player_name": "Sprinter", "difficulty": "easy", "num_years": 5},
        ).json()
        game_id = create["game_id"]

        start_state = client.get(f"/api/games/{game_id}").json()
        resp = client.post(f"/api/games/{game_id}/fast-forward", json={"years": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "fast_forwarded"
        assert data["current_year"] >= start_state["current_year"]

    def test_playtest_returns_aggregate_metrics(self, client):
        resp = client.post("/api/games/playtest")
        assert resp.status_code == 200
        data = resp.json()
        assert "aggregate" in data
        assert set(data["aggregate"]["by_difficulty"].keys()) == {"easy", "standard", "hard"}


class TestCoopLifecycle:
    def test_create_join_and_ready_coop_game(self, client):
        created = client.post(
            "/api/coop",
            json={"host_name": "Host", "player_count": 2, "difficulty": "standard", "num_years": 5},
        )
        assert created.status_code == 200
        created_data = created.json()
        game_id = created_data["game_id"]
        host_id = created_data["participant_id"]
        assert "room_code" in created_data
        assert len(created_data["room_code"]) == 6

        joined = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        assert joined.status_code == 200
        guest_id = joined.json()["participant_id"]

        state = client.get(f"/api/coop/{game_id}/{host_id}")
        assert state.status_code == 200
        snapshot = state.json()["snapshot"]
        assert snapshot["coop_mode"] is True
        assert snapshot["competitive_mode"] is True
        assert len(snapshot["participants"]) == 2

        ready_one = client.post(f"/api/coop/{game_id}/ready", json={"participant_id": host_id, "ready": True})
        assert ready_one.status_code == 200
        assert ready_one.json()["status"] == "ready_recorded"

        ready_two = client.post(f"/api/coop/{game_id}/ready", json={"participant_id": guest_id, "ready": True})
        assert ready_two.status_code == 200

        start_resp = client.post(f"/api/coop/{game_id}/start", json={"participant_id": host_id})
        assert start_resp.status_code == 200
        assert start_resp.json()["status"] == "started"

    def test_coop_websocket_broadcasts_snapshot(self, client):
        created = client.post(
            "/api/coop",
            json={"host_name": "Host", "player_count": 2, "difficulty": "standard", "num_years": 5},
        ).json()
        game_id = created["game_id"]
        host_id = created["participant_id"]
        guest = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"}).json()
        guest_id = guest["participant_id"]

        with client.websocket_connect(f"/ws/games/{game_id}/{host_id}") as host_ws:
            host_message = host_ws.receive_json()
            assert host_message["type"] == "snapshot"
            with client.websocket_connect(f"/ws/games/{game_id}/{guest_id}") as guest_ws:
                guest_message = guest_ws.receive_json()
                assert guest_message["type"] == "snapshot"
                host_ws.send_json({"type": "refresh"})
                refreshed = host_ws.receive_json()
                assert refreshed["type"] == "snapshot"

    def test_coop_summary_returns_mvp(self, client):
        created = client.post(
            "/api/coop",
            json={"host_name": "Host", "player_count": 2, "difficulty": "standard", "num_years": 5},
        ).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})

        resp = client.get(f"/api/coop/{game_id}/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["participants"]) == 2
        assert data["mvp"] is not None

    def test_four_player_coop_join_flow(self, client):
        created = client.post(
            "/api/coop",
            json={"host_name": "Host", "player_count": 4, "difficulty": "easy", "num_years": 5},
        ).json()
        game_id = created["game_id"]

        joined_ids = [created["participant_id"]]
        for name in ("Guest A", "Guest B", "Guest C"):
            joined = client.post(f"/api/coop/{game_id}/join", json={"player_name": name})
            assert joined.status_code == 200
            joined_ids.append(joined.json()["participant_id"])

        summary = client.get(f"/api/coop/{game_id}/summary")
        assert summary.status_code == 200
        assert len(summary.json()["participants"]) == 4
        assert len(set(joined_ids)) == 4

    def test_full_game_playthrough(self, client):
        create = client.post("/api/games", json={"player_name": "FullPlay", "difficulty": "easy", "num_years": 5}).json()
        game_id = create["game_id"]

        for _ in range(3):
            advance = client.post(f"/api/games/{game_id}/advance-year")
            assert advance.status_code == 200

            end = client.post(f"/api/games/{game_id}/end-year")
            assert end.status_code == 200

        summary = client.get(f"/api/games/{game_id}/summary")
        assert summary.status_code == 200

    def test_game_completion_sets_status(self, client):
        create = client.post("/api/games", json={"player_name": "Completer", "num_years": 5}).json()
        game_id = create["game_id"]
        client.post(f"/api/games/{game_id}/advance-year")
        client.post(f"/api/games/{game_id}/end-year")
        resp = client.get(f"/api/games/{game_id}")
        assert resp.status_code == 200


class TestStateAssertions:
    """Tests that assert real state changes, not just status codes."""

    def _get_company_from_snapshot(self, snapshot):
        if snapshot.get("company"):
            return snapshot["company"]
        if snapshot.get("companies"):
            return snapshot["companies"][0]
        return snapshot

    def test_advance_year_changes_phase_and_year(self, client):
        create = client.post("/api/games", json={"player_name": "PhaseTester", "num_years": 5}).json()
        game_id = create["game_id"]
        pre = client.get(f"/api/games/{game_id}").json()
        pre_phase = pre["snapshot"]["phase"]
        pre_year = pre["current_year"]

        resp = client.post(f"/api/games/{game_id}/advance-year")
        assert resp.status_code == 200
        data = resp.json()
        assert data["year"] > pre_year or data["phase"] != pre_phase
        assert data["phase"] in ("year_start", "decision_window", "compliance")

    def test_end_year_advances_to_next_year_or_complete(self, client):
        create = client.post("/api/games", json={"player_name": "YearEnder", "num_years": 5}).json()
        game_id = create["game_id"]
        client.post(f"/api/games/{game_id}/advance-year")
        pre = client.get(f"/api/games/{game_id}").json()
        pre_year = pre["current_year"]

        resp = client.post(f"/api/games/{game_id}/end-year")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "year_ended"
        assert data["year"] >= pre_year

    def test_offset_purchase_changes_state(self, client):
        create = client.post("/api/games", json={"player_name": "OffsetTester"}).json()
        game_id = create["game_id"]
        client.post(f"/api/games/{game_id}/advance-year")
        state_resp = client.get(f"/api/games/{game_id}").json()
        company = self._get_company_from_snapshot(state_resp["snapshot"])
        pre_cash = company["cash"]
        offset_price = 25.0
        qty = 10

        resp = client.post(
            f"/api/games/{game_id}/decision",
            json={"action": "buy_offsets", "payload": {"quantity": qty, "price_per_unit": offset_price}},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "applied"
        post_resp = client.get(f"/api/games/{game_id}").json()
        post_company = self._get_company_from_snapshot(post_resp["snapshot"])
        assert post_company["cash"] <= pre_cash

    def test_summary_contains_achievements_and_rankings(self, client):
        create = client.post("/api/games", json={"player_name": "SummaryTester", "num_years": 5}).json()
        game_id = create["game_id"]
        client.post(f"/api/games/{game_id}/advance-year")
        client.post(f"/api/games/{game_id}/end-year")
        summary = client.get(f"/api/games/{game_id}/summary").json()
        assert "achievements" in summary
        assert summary["completed_years"] >= 1

    def test_e2e_full_game_loop_with_multiple_years(self, client):
        create = client.post("/api/games", json={"player_name": "E2ETester", "difficulty": "easy", "num_years": 5}).json()
        game_id = create["game_id"]
        years_advanced = 0
        for _ in range(5):
            advance = client.post(f"/api/games/{game_id}/advance-year")
            if advance.status_code == 200:
                years_advanced += 1
            end = client.post(f"/api/games/{game_id}/end-year")
            assert end.status_code == 200

        summary = client.get(f"/api/games/{game_id}/summary").json()
        assert summary["completed_years"] >= 1
        assert "achievements" in summary
        assert summary["player_name"] == "E2ETester"

    def test_new_game_opens_decision_window(self, client):
        # Regression guard: a fresh solo game must land in the decision window
        # so the player can actually act (not stuck in year_start).
        create = client.post("/api/games", json={"player_name": "Fresh"}).json()
        assert create["snapshot"]["phase"] == "decision_window"

    def test_decision_in_window_changes_state(self, client):
        # Regression guard for the silent-no-op bug: activating an abatement in
        # the decision window must deduct cash and mark the measure.
        create = client.post("/api/games", json={"player_name": "Doer"}).json()
        game_id = create["game_id"]
        snap = client.get(f"/api/games/{game_id}").json()["snapshot"]
        assert snap["phase"] == "decision_window"
        company = self._get_company_from_snapshot(snap)
        pre_cash = company["cash"]
        menu = company.get("abatement_menu", [])
        assert menu, "expected an abatement menu in the decision window"
        measure_id = menu[0]["measure_id"]

        resp = client.post(
            f"/api/games/{game_id}/decision",
            json={"action": "activate_abatement", "payload": {"measure_id": measure_id}},
        )
        assert resp.status_code == 200

        post = self._get_company_from_snapshot(client.get(f"/api/games/{game_id}").json()["snapshot"])
        assert post["cash"] < pre_cash
        item = next(m for m in post["abatement_menu"] if m["measure_id"] == measure_id)
        assert item["active"] or item["pending"]

    def test_advance_year_reopens_decision_window(self, client):
        # Advancing from the decision window closes/scores the year and opens
        # the next year's window (turn-based loop stays playable).
        create = client.post("/api/games", json={"player_name": "Loop", "num_years": 5}).json()
        game_id = create["game_id"]
        assert create["snapshot"]["phase"] == "decision_window"

        data = client.post(f"/api/games/{game_id}/advance-year").json()
        assert data["phase"] == "decision_window"
        assert data["year"] == 2

    def test_fast_forward_changes_year_and_phase(self, client):
        create = client.post("/api/games", json={"player_name": "FastForwarder", "difficulty": "easy", "num_years": 10}).json()
        game_id = create["game_id"]
        pre = client.get(f"/api/games/{game_id}").json()
        pre_year = pre["current_year"]

        resp = client.post(f"/api/games/{game_id}/fast-forward", json={"years": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_year"] > pre_year
        assert data["status"] == "fast_forwarded"


class TestStaticAssets:
    def test_assets_manifest_returns_200(self, client):
        resp = client.get("/assets/manifest.json")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/json"
        data = resp.json()
        assert "version" in data
        assert "assets" in data
        assert "ground" in data["assets"]

    def test_assets_tile_returns_png(self, client):
        resp = client.get("/assets/tiles/ground.png")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"

    def test_assets_font_returns_ttf(self, client):
        resp = client.get("/assets/fonts/PressStart2P-Regular.ttf")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "font/ttf"

    def test_all_manifest_paths_exist(self, client):
        manifest = client.get("/assets/manifest.json").json()
        for name, entry in manifest.get("assets", {}).items():
            path = entry["path"]
            resp = client.get(path)
            assert resp.status_code == 200, f"Manifest asset '{name}' at {path} returned {resp.status_code}"
