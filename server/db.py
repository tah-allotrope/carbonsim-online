from __future__ import annotations

import json
import sqlite3
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "mayor.db"


def _get_db(path: str | None = None) -> sqlite3.Connection:
    db_path = path or str(DB_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(path: str | None = None) -> None:
    conn = _get_db(path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT PRIMARY KEY,
            player_name TEXT NOT NULL,
            province_name TEXT NOT NULL DEFAULT 'default',
            difficulty TEXT NOT NULL DEFAULT 'standard',
            status TEXT NOT NULL DEFAULT 'active',
            current_year INTEGER NOT NULL DEFAULT 0,
            total_years INTEGER NOT NULL DEFAULT 15,
            state_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS game_saves (
            save_id TEXT PRIMARY KEY,
            game_id TEXT NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
            save_name TEXT NOT NULL,
            state_json TEXT NOT NULL,
            saved_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def compress_state(state: dict[str, Any]) -> str:
    raw = json.dumps(state, default=str)
    compressed = zlib.compress(raw.encode("utf-8"))
    return compressed.hex()


def decompress_state(hex_data: str) -> dict[str, Any]:
    compressed = bytes.fromhex(hex_data)
    raw = zlib.decompress(compressed).decode("utf-8")
    return json.loads(raw)


def create_game(game_id: str, player_name: str, province_name: str, difficulty: str, total_years: int, state: dict[str, Any], db_path: str | None = None) -> dict[str, Any]:
    conn = _get_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    state_json = compress_state(state)
    conn.execute(
        "INSERT INTO games (game_id, player_name, province_name, difficulty, status, current_year, total_years, state_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (game_id, player_name, province_name, difficulty, "active", state.get("current_year", 0), total_years, state_json, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM games WHERE game_id = ?", (game_id,)).fetchone()
    conn.close()
    return dict(row)


def get_game(game_id: str, db_path: str | None = None) -> dict[str, Any] | None:
    conn = _get_db(db_path)
    row = conn.execute("SELECT * FROM games WHERE game_id = ?", (game_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_game_state(game_id: str, state: dict[str, Any], db_path: str | None = None) -> None:
    conn = _get_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    state_json = compress_state(state)
    conn.execute(
        "UPDATE games SET state_json = ?, current_year = ?, status = ?, updated_at = ? WHERE game_id = ?",
        (state_json, state.get("current_year", 0), state.get("game_status", "active"), now, game_id),
    )
    conn.commit()
    conn.close()


def list_games(db_path: str | None = None) -> list[dict[str, Any]]:
    conn = _get_db(db_path)
    rows = conn.execute("SELECT game_id, player_name, difficulty, status, current_year, total_years, created_at, updated_at FROM games ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_game(game_id: str, db_path: str | None = None) -> bool:
    conn = _get_db(db_path)
    conn.execute("DELETE FROM game_saves WHERE game_id = ?", (game_id,))
    cursor = conn.execute("DELETE FROM games WHERE game_id = ?", (game_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def create_save(save_id: str, game_id: str, save_name: str, state: dict[str, Any], db_path: str | None = None) -> dict[str, Any]:
    conn = _get_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    state_json = compress_state(state)
    conn.execute(
        "INSERT INTO game_saves (save_id, game_id, save_name, state_json, saved_at) VALUES (?, ?, ?, ?, ?)",
        (save_id, game_id, save_name, state_json, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM game_saves WHERE save_id = ?", (save_id,)).fetchone()
    conn.close()
    return dict(row)


def list_saves(game_id: str, db_path: str | None = None) -> list[dict[str, Any]]:
    conn = _get_db(db_path)
    rows = conn.execute("SELECT save_id, game_id, save_name, saved_at FROM game_saves WHERE game_id = ? ORDER BY saved_at DESC", (game_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_save(save_id: str, db_path: str | None = None) -> dict[str, Any] | None:
    conn = _get_db(db_path)
    row = conn.execute("SELECT * FROM game_saves WHERE save_id = ?", (save_id,)).fetchone()
    conn.close()
    if row:
        state = decompress_state(row["state_json"])
        return state
    return None
