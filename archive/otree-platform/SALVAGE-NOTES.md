# Salvage Notes — oTree Platform Archive

**Date:** 2026-06-02
**Sprint:** 1 — Canonical Game Stack Consolidation (PHASE-01)
**Source:** `platform/` (oTree workshop product)

## Import Verification

grep confirmed **zero inbound imports** from the game stack (`mayor_api/`, `mayor_web/`, `carbonsim_engine/`) to `platform/` or `carbonsim_phase12`. The platform is cleanly severable.

## Salvaged Artifacts

| File | Purpose | Future Use |
|------|---------|------------|
| `Dockerfile` | Python 3.12-slim container running oTree prodserver | Adapt for FastAPI game deployment (Sprint 4 deployment) |
| `Caddyfile` | Reverse proxy template for HTTPS | Reuse pattern for game server HTTPS termination |
| `fly.toml` | Fly.io app config (Singapore region) | Adapt for game deployment on Fly.io |
| `docker-compose.yml` | Web + Postgres services with health checks | Adapt for game + optional Postgres persistence |
| `Procfile` | Single-process production server | Adapt `web: uvicorn mayor_api.main:create_app --factory` |
| `FACILITATOR_RUNBOOK.md` | Pre-session checklist, debrief guidance, deployment ops | Adapt for game facilitator/host documentation (Sprint 4) |

## Pattern Mappings to Sprint 4 (Multiplayer Build-Out)

### Room/Session Flow → GAP-05 Lobby & Room Code

The oTree platform uses oTree's built-in room system (`settings.py` ROOMS config). Key patterns to adapt:

- **Welcome page** (`Welcome.html`): Participant enters display name, sees assigned company/sector/role. Map to game's room join screen.
- **Company assignment** (`__init__.py:40-68`): `creating_session()` assigns companies from engine state to participants in order. First participant becomes facilitator. Adapt for game's room-code join flow.
- **Session config** (`settings.py:7-52`): Scenario selection, phase durations, bot count. Map to game's session creation options.

### Facilitator Controls → GAP-05 Host Controls

The `FacilitatorPanel.html` and `live_facilitator_panel()` in `__init__.py:302-354` implement:

- **Pause/Resume/Advance**: `engine.pause_session()`, `engine.resume_session()`, `engine.force_advance_phase()` — these engine functions already exist and are used by the game stack.
- **Shock application**: `engine.apply_shock(shock_type, magnitude)` — exists in engine.
- **Bot turn execution**: `engine.run_bot_turns()` — exists in engine.
- **Session export**: `engine.export_session_data()` — exists in engine.
- **Health check** (`deployment.py:27-46`): Returns phase, year, cap, participant count, paused/complete flags. Adapt for game's host dashboard WebSocket broadcast.

### Live State Broadcasting → GAP-05 WebSocket Sync

The `live_workshop_hub()` function (`__init__.py:157-299`) demonstrates:

- **Broadcast pattern** (`_broadcast_state`): Sends per-player snapshots to all participants after every action.
- **Action routing**: Single `live_method` dispatches by `action` field — pause, resume, advance, abatement, offsets, auctions, trades, export.
- **Reconnection** (`deployment.py:49-60`): `reconnect_company()` restores latest company snapshot on reconnect.

### Participant Dashboard → Existing `mayor_web/game.html`

The `WorkshopHub.html` is the richest reference for multiplayer UI:

- **Company dashboard**: Emissions, allocation, holdings, offsets, auction wins, banked, compliance gap, penalty.
- **Decision impact panel**: Abatement cost, active/pending measures, max offsets, projected net position.
- **Abatement menu**: Per-measure commit buttons with status (Available/Active/Queued).
- **Offset purchase**: Quantity input + buy button, gated on `phase == 'decision_window'`.
- **Auction board**: Scheduled auctions with bid forms (non-facilitator) or open/close controls (facilitator).
- **Bilateral trade**: Propose form (buyer select, quantity, price) + trade inbox with accept/reject.
- **Public trade feed**: All completed trades visible to all participants.
- **Leaderboard**: Company rankings by banked allowances, compliance gap, cumulative penalties.

### Deployment Patterns → Sprint 4 Deployment

- **Docker Compose** with Postgres health check pattern is directly reusable.
- **Caddy reverse proxy** pattern for HTTPS termination.
- **Fly.io config** with auto-scaling settings.
- **Environment variable pattern** (`OTREE_PRODUCTION`, `SECRET_KEY`, `DATABASE_URL`) — adapt for game's env vars.
- **Backup/restore** via `pg_dump`/`psql` commands in runbook.

## What Was NOT Salvaged

- The oTree app framework itself (`BaseConstants`, `BaseSubsession`, `BaseGroup`, `BasePlayer`, `Page` classes) — oTree-specific, not portable.
- `platform/tests/` — oTree-specific test fixtures, not portable to FastAPI test patterns.
- `platform/carbonsim_phase12/engine.py` — 1-line shim (`from carbonsim_engine.engine import *`), no unique code.
- `platform/db.sqlite3` — runtime database, not portable.
- `platform/_static/` — oTree static asset directory.
- `platform/.env.example`, `.env.production.example` — oTree-specific env templates (patterns noted in SALVAGE-NOTES).
- `platform/.gitignore`, `platform/.pytest_cache/` — tooling artifacts.

## Recommendation for Sprint 4

When implementing multiplayer in Sprint 4, the highest-value patterns to port are:

1. **Facilitator/host control panel** — the `FacilitatorPanel.html` layout and action set is a solid starting point for a game host dashboard.
2. **Live broadcast pattern** — the `_broadcast_state` + per-action snapshot refresh pattern maps directly to WebSocket broadcasts in `mayor_api/ws.py`.
3. **Reconnection flow** — `deployment.py:reconnect_company()` shows the minimal state needed to resume a dropped participant.
4. **Trade proposal/inbox UI** — `WorkshopHub.html` trade section is a working bilateral trade interface.
5. **Auction board UI** — sealed-bid auction form with facilitator open/close controls.
6. **Deployment stack** — Docker Compose + Caddy + Fly.io configs are directly adaptable with minor modifications.
