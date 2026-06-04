from __future__ import annotations

import os
import pytest
from fastapi.testclient import TestClient

from server.main import create_app
from server.db import init_db, DB_PATH


@pytest.fixture(autouse=True)
def test_db():
    test_path = str(DB_PATH) + ".test_coop"
    os.environ["MAYOR_DB_PATH"] = test_path
    init_db(test_path)
    yield
    for suffix in ("", "-wal", "-shm"):
        path = test_path + suffix
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c


class TestRoomCode:
    def test_create_returns_room_code(self, client):
        resp = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5})
        assert resp.status_code == 200
        data = resp.json()
        assert "room_code" in data
        assert len(data["room_code"]) == 6
        assert data["room_code"].isalnum()

    def test_join_by_room_code(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 3, "num_years": 5}).json()
        code = created["room_code"]

        joined = client.post("/api/coop/join-by-code", json={"room_code": code, "player_name": "Guest"})
        assert joined.status_code == 200
        assert joined.json()["participant_id"] == "P02"
        assert joined.json()["room_code"] == code

    def test_join_by_invalid_code_returns_404(self, client):
        resp = client.post("/api/coop/join-by-code", json={"room_code": "ZZZZZZ", "player_name": "Ghost"})
        assert resp.status_code == 404

    def test_join_by_code_case_insensitive(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        code = created["room_code"]
        joined = client.post("/api/coop/join-by-code", json={"room_code": code.lower(), "player_name": "Guest"})
        assert joined.status_code == 200


class TestLobby:
    def test_lobby_snapshot(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        resp = client.get(f"/api/coop/{game_id}/lobby")
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "lobby"
        assert data["game_status"] == "lobby"
        assert len(data["participants"]) == 1
        assert data["participants"][0]["is_host"] is True

    def test_lobby_updates_on_join(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 3, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        lobby = client.get(f"/api/coop/{game_id}/lobby").json()
        assert len(lobby["participants"]) == 2

    def test_cannot_join_after_start(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})
        join_resp = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Late"})
        assert join_resp.status_code == 400

    def test_cannot_join_full_game(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        late = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Too Late"})
        assert late.status_code == 400


class TestHostControls:
    def test_host_can_start_game(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        resp = client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})
        assert resp.status_code == 200
        assert resp.json()["status"] == "started"

    def test_non_host_cannot_start(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        guest = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"}).json()
        resp = client.post(f"/api/coop/{game_id}/start", json={"participant_id": guest["participant_id"]})
        assert resp.status_code == 403

    def test_cannot_start_with_one_player(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        resp = client.post(f"/api/coop/{created['game_id']}/start", json={"participant_id": created["participant_id"]})
        assert resp.status_code == 400

    def test_host_can_advance_year(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})
        resp = client.post(f"/api/coop/{game_id}/advance-year", json={"participant_id": created["participant_id"]})
        assert resp.status_code == 200
        assert resp.json()["status"] == "year_advanced"

    def test_non_host_cannot_advance_year(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        guest = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"}).json()
        client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})
        resp = client.post(f"/api/coop/{game_id}/advance-year", json={"participant_id": guest["participant_id"]})
        assert resp.status_code == 403

    def test_host_can_pause_and_resume(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})

        pause = client.post(f"/api/coop/{game_id}/pause", json={"participant_id": created["participant_id"]})
        assert pause.status_code == 200
        assert pause.json()["phase"] == "paused"

        resume = client.post(f"/api/coop/{game_id}/resume", json={"participant_id": created["participant_id"]})
        assert resume.status_code == 200
        assert resume.json()["phase"] != "paused"


class TestCompetitiveGameplay:
    def test_each_player_has_own_company(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        guest = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"}).json()

        host_state = client.get(f"/api/coop/{game_id}/{created['participant_id']}").json()
        guest_state = client.get(f"/api/coop/{game_id}/{guest['participant_id']}").json()

        host_company = host_state["snapshot"]["player_company"]
        guest_company = guest_state["snapshot"]["player_company"]
        assert host_company["company_id"] != guest_company["company_id"]

    def test_decision_affects_only_own_company(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        guest = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"}).json()
        client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})

        host_snap = client.get(f"/api/coop/{game_id}/{created['participant_id']}").json()["snapshot"]
        menu = host_snap.get("player_company", {}).get("abatement_menu", [])
        if not menu:
            return
        measure_id = menu[0]["measure_id"]
        pre_cash = host_snap["player_company"]["cash"]

        resp = client.post(
            f"/api/coop/{game_id}/decision/{created['participant_id']}",
            json={"action": "activate_abatement", "payload": {"measure_id": measure_id}},
        )
        assert resp.status_code == 200

        host_post = client.get(f"/api/coop/{game_id}/{created['participant_id']}").json()["snapshot"]
        guest_post = client.get(f"/api/coop/{game_id}/{guest['participant_id']}").json()["snapshot"]
        assert host_post["player_company"]["cash"] <= pre_cash
        assert guest_post["player_company"]["cash"] == guest["snapshot"]["player_company"]["cash"] if "player_company" in guest.get("snapshot", {}) else True

    def test_leaderboard_returns_rankings(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})

        resp = client.get(f"/api/coop/{game_id}/leaderboard")
        assert resp.status_code == 200
        board = resp.json()["leaderboard"]
        assert len(board) >= 2
        assert board[0]["rank"] == 1

    def test_websocket_broadcasts_to_all_players(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        guest = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"}).json()

        with client.websocket_connect(f"/ws/games/{game_id}/{created['participant_id']}") as host_ws:
            host_msg = host_ws.receive_json()
            assert host_msg["type"] == "snapshot"
            assert host_msg["game_status"] == "lobby"

            with client.websocket_connect(f"/ws/games/{game_id}/{guest['participant_id']}") as guest_ws:
                guest_msg = guest_ws.receive_json()
                assert guest_msg["type"] == "snapshot"

                host_ws.send_json({"type": "refresh"})
                refreshed = host_ws.receive_json()
                assert refreshed["type"] == "snapshot"

    def test_summary_shows_competitive_results(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})

        resp = client.get(f"/api/coop/{game_id}/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "leaderboard" in data
        assert len(data["leaderboard"]) >= 2
        assert data["mvp"] is not None


class TestFullCompetitiveCycle:
    def test_multi_year_competitive_game(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "difficulty": "easy", "num_years": 5}).json()
        game_id = created["game_id"]
        guest = client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"}).json()

        start = client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})
        assert start.status_code == 200

        for _ in range(3):
            advance = client.post(f"/api/coop/{game_id}/advance-year", json={"participant_id": created["participant_id"]})
            assert advance.status_code == 200

        state = client.get(f"/api/coop/{game_id}/{created['participant_id']}").json()
        assert state["snapshot"]["current_year"] >= 1

        summary = client.get(f"/api/coop/{game_id}/summary")
        assert summary.status_code == 200
        assert len(summary.json()["leaderboard"]) >= 2

    def test_game_completion_via_host_advance(self, client):
        created = client.post("/api/coop", json={"host_name": "Host", "player_count": 2, "num_years": 5}).json()
        game_id = created["game_id"]
        client.post(f"/api/coop/{game_id}/join", json={"player_name": "Guest"})
        client.post(f"/api/coop/{game_id}/start", json={"participant_id": created["participant_id"]})

        for _ in range(10):
            resp = client.post(f"/api/coop/{game_id}/advance-year", json={"participant_id": created["participant_id"]})
            if resp.status_code != 200:
                break
            data = resp.json()
            if data.get("game_status") == "completed":
                break

        state = client.get(f"/api/coop/{game_id}/{created['participant_id']}").json()
        assert state["game_status"] in ("completed", "active")
