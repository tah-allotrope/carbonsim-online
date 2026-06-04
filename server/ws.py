from __future__ import annotations

import asyncio
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

from engine import participant_snapshot, set_participant_connection

from .db import decompress_state, get_game as db_get_game, update_game_state as db_update_game_state


class CoopConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, dict[str, WebSocket]] = defaultdict(dict)

    async def connect(self, game_id: str, participant_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        existing = self._rooms[game_id].get(participant_id)
        if existing:
            try:
                await existing.close()
            except Exception:
                pass
        self._rooms[game_id][participant_id] = websocket
        state = _load_state(game_id)
        set_participant_connection(state, participant_id=participant_id, connected=True)
        db_update_game_state(game_id, state)
        await self.broadcast_snapshot(game_id)

    async def disconnect(self, game_id: str, participant_id: str, websocket: WebSocket) -> None:
        current = self._rooms[game_id].get(participant_id)
        if current is websocket:
            self._rooms[game_id].pop(participant_id, None)
        try:
            state = _load_state(game_id)
            set_participant_connection(state, participant_id=participant_id, connected=False)
            db_update_game_state(game_id, state)
        except (ValueError, Exception):
            pass
        if self._rooms[game_id]:
            await self.broadcast_snapshot(game_id)

    async def broadcast_snapshot(self, game_id: str) -> None:
        state = _load_state(game_id)
        payload = {
            "type": "snapshot",
            "game_id": game_id,
            "game_status": state.get("game_status", "lobby"),
            "room_code": state.get("room_code", ""),
            "participants": [
                {
                    "participant_id": participant["participant_id"],
                    "player_name": participant["player_name"],
                    "snapshot": participant_snapshot(state, participant_id=participant["participant_id"]),
                }
                for participant in state.get("participants", [])
            ],
        }
        stale: list[str] = []
        for pid, socket in list(self._rooms[game_id].items()):
            try:
                await socket.send_json(payload)
            except Exception:
                stale.append(pid)
        for pid in stale:
            self._rooms[game_id].pop(pid, None)

    def is_connected(self, game_id: str, participant_id: str) -> bool:
        return participant_id in self._rooms.get(game_id, {})


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
