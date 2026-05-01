from __future__ import annotations

import json
import os
import pytest
from fastapi.testclient import TestClient

from mayor_api.main import create_app
from mayor_api.db import init_db, DB_PATH


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

    def test_advance_year_tutorial_draws_fixed_card(self, client):
        create = client.post(
            "/api/games",
            json={"player_name": "Tutorial", "tutorial_mode": True, "num_years": 5},
        ).json()
        game_id = create["game_id"]

        resp = client.post(f"/api/games/{game_id}/advance-year")
        assert resp.status_code == 200
        data = resp.json()
        assert data["drawn_cards"]
        assert data["drawn_cards"][0]["card_id"] == "tutorial_001"

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

        joined = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        assert joined.status_code == 200
        guest_id = joined.json()["participant_id"]

        state = client.get(f"/api/coop/{game_id}/{host_id}")
        assert state.status_code == 200
        snapshot = state.json()["snapshot"]
        assert snapshot["coop_mode"] is True
        assert len(snapshot["participants"]) == 2

        ready_one = client.post(f"/api/coop/{game_id}/ready", json={"participant_id": host_id, "ready": True})
        assert ready_one.status_code == 200
        assert ready_one.json()["advanced"] is False

        ready_two = client.post(f"/api/coop/{game_id}/ready", json={"participant_id": guest_id, "ready": True})
        assert ready_two.status_code == 200
        assert ready_two.json()["advanced"] is True

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
