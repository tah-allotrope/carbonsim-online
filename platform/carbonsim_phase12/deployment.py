from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from . import engine


HEALTH_CHECK_FIELDS = [
    "phase",
    "current_year",
    "current_cap",
    "participant_count",
    "total_companies",
    "is_paused",
    "is_complete",
    "active_auctions",
    "pending_trades",
    "audit_log_entries",
    "started_at",
    "completed_at",
]

SESSION_RECOVERY_ENABLED = True


def health_check(state: dict[str, Any]) -> dict[str, Any]:
    phase = state.get("phase", engine.PHASE_LOBBY)
    return {
        "phase": phase,
        "current_year": state.get("current_year", 0),
        "current_cap": state.get("current_cap", 0.0),
        "participant_count": state.get("participant_count", 0),
        "total_companies": len(state.get("companies", [])),
        "is_paused": phase == engine.PHASE_PAUSED,
        "is_complete": phase == engine.PHASE_COMPLETE,
        "active_auctions": len(
            [a for a in state.get("auctions", []) if a.get("status") == "open"]
        ),
        "pending_trades": len(
            [t for t in state.get("trades", []) if t.get("status") == "proposed"]
        ),
        "audit_log_entries": len(state.get("audit_log", [])),
        "started_at": state.get("started_at"),
        "completed_at": state.get("completed_at"),
    }


def reconnect_company(state: dict[str, Any], company_id: str) -> dict[str, Any] | None:
    for company in state.get("companies", []):
        if company["company_id"] == company_id:
            snapshot = engine._company_snapshot(state, company)
            snapshot["company_id"] = company["company_id"]
            snapshot["sector"] = company["sector"]
            snapshot["is_bot"] = company.get("is_bot", False)
            snapshot["banked_allowances"] = company["banked_allowances"]
            snapshot["cumulative_penalties"] = company["cumulative_penalties"]
            snapshot["year_results"] = company["year_results"]
            return snapshot
    return None


def get_company_role(state: dict[str, Any], company_id: str) -> str:
    for index, company in enumerate(state.get("companies", [])):
        if company["company_id"] == company_id:
            if index == 0:
                return "facilitator"
            return "participant"
    return "unknown"


def validate_facilitator_action(*, is_facilitator: bool) -> bool:
    return is_facilitator


def validate_decision_action(state: dict[str, Any], company_id: str) -> bool:
    if state.get("phase") != engine.PHASE_DECISION_WINDOW:
        return False
    for company in state.get("companies", []):
        if company["company_id"] == company_id:
            return True
    return False


def format_audit_event(
    *,
    event_type: str,
    year: int,
    details: dict[str, Any],
    session_id: str,
) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "year": year,
        "details": details,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
