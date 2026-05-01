from __future__ import annotations

import asyncio
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

from carbonsim_engine import participant_snapshot, set_participant_connection

from .db import decompress_state, get_game as db_get_game, update_game_state as db_update_game_state


class CoopConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, game_id: str, participant_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms[game_id].add(websocket)
        state = _load_state(game_id)
        set_participant_connection(state, participant_id=participant_id, connected=True)
        db_update_game_state(game_id, state)
        await self.broadcast_snapshot(game_id)

    async def disconnect(self, game_id: str, participant_id: str, websocket: WebSocket) -> None:
        self._rooms[game_id].discard(websocket)
        state = _load_state(game_id)
        try:
            set_participant_connection(state, participant_id=participant_id, connected=False)
            db_update_game_state(game_id, state)
        except ValueError:
            pass
        if self._rooms[game_id]:
            await self.broadcast_snapshot(game_id)

    async def broadcast_snapshot(self, game_id: str) -> None:
        state = _load_state(game_id)
        payload = {
            "type": "snapshot",
            "game_id": game_id,
            "participants": [
                {
                    "participant_id": participant["participant_id"],
                    "player_name": participant["player_name"],
                    "snapshot": participant_snapshot(state, participant_id=participant["participant_id"]),
                }
                for participant in state.get("participants", [])
            ],
        }
        stale: list[WebSocket] = []
        for socket in list(self._rooms[game_id]):
            try:
                await socket.send_json(payload)
            except Exception:
                stale.append(socket)
        for socket in stale:
            self._rooms[game_id].discard(socket)


manager = CoopConnectionManager()


async def coop_ws_endpoint(websocket: WebSocket, game_id: str, participant_id: str) -> None:
    await manager.connect(game_id, participant_id, websocket)
    try:
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message.get("type") == "refresh":
                await manager.broadcast_snapshot(game_id)
            else:
                await asyncio.sleep(0)
    except WebSocketDisconnect:
        await manager.disconnect(game_id, participant_id, websocket)


def _load_state(game_id: str) -> dict:
    row = db_get_game(game_id)
    if not row:
        raise ValueError("Game not found")
    return decompress_state(row["state_json"])
