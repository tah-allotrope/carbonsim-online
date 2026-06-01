# Project Structure

This document describes the top-level directory layout of CarbonSim Online.

## Code Directories

| Directory | Description |
|-----------|-------------|
| `engine/` | Python compliance engine. Contains the deterministic year cycle, abatement, offsets, banking, penalties, card system, tutorial, achievements, playtest harness, scenarios, and co-op state helpers. Installed as a pip package (`pip install -e engine/`). |
| `server/` | FastAPI backend. Serves the REST API, WebSocket endpoint for co-op mode, and the static frontend. Contains routes, database layer, models, and tests. |
| `web/` | Static HTML/CSS/JS frontend. Four screens (index, game, co-op, summary) with vanilla JS modules for API calls, audio, visual effects, XP progression, and keyboard shortcuts. |

## Documentation

| Directory | Description |
|-----------|-------------|
| `docs/` | Project structure guides (this file). |
| `plans/` | Sprint plans and roadmap index. See `plans/2026-05-29-game-focus-roadmap-index.md` for the 5-sprint execution plan. |
| `research/` | Vietnam ETS research documents and product framing. Source of truth for domain rules. |
| `reports/` | Phase and final reports generated during sprint execution. |

## Archive

| Directory | Description |
|-----------|-------------|
| `archive/otree-platform/` | Archived oTree workshop platform (Sprint 1). Contains salvaged deployment artifacts, pattern-mapping notes, and the runnable platform for Sprint 4 reference. |
| `archive/plans/` | Archived divergent plans (free-tier deployment, Vietnam market testing, Carbon Crunch Daily, co-op facilitator workshop). |
| `archive/reports/` | Archived obsolete oTree phase reports. |

## Utilities

| Directory | Description |
|-----------|-------------|
| `scripts/` | Utility scripts (report rendering helpers). |

## Where New Code Belongs

- **Engine logic** (compliance rules, game state, calculations): `engine/`
- **API endpoints** (REST routes, WebSocket handlers): `server/routes/`
- **Database schema and queries**: `server/db.py`
- **Request/response models**: `server/models.py`
- **Frontend screens**: `web/*.html`
- **Frontend JS modules**: `web/js/`
- **Frontend styles**: `web/css/`
- **Tests for engine**: `engine/tests/`
- **Tests for server**: `server/tests/`
