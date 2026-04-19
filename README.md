# CarbonSim Online

A Vietnam-aligned, workshop-ready online CarbonSim platform for ETS training, built on oTree.

## What is implemented

- `plan/project-plan.md` defines the multi-phase roadmap.
- `platform/` contains an `oTree` project with the `carbonsim_phase12` app.
- **Phase 1**: Working room/session scaffold, participant join flow, facilitator-controlled launch, company dashboard.
- **Phase 2**: Deterministic year engine with year-start allocation, emissions growth, banking, year-end surrender, penalties, and an audit log.
- **Phase 3**: Sector-specific abatement menus, immediate vs. next-year activation timing, offset holdings with a configurable surrender cap, and dashboard projections.
- **Phase 4**: Sealed-bid, uniform-price primary auction with auction scheduling, bid validation, deterministic clearing, settlement, public result display, and facilitator controls.
- **Phase 5**: Bilateral secondary trading with trade proposals, buyer accept/reject, server-side validation, expiration handling, and a public trade feed.
- **Phase 6**: Facilitator tools (pause/resume/advance), participant status tracking, session data export, and session summary for debriefing.
- **Phase 7**: Three scenario packs (vietnam_pilot, high_pressure, generous), bot strategies (conservative, moderate, aggressive), and four shock event types.
- **Phase 8**: Deployment hardening (Docker, env-based configuration, production settings), health checks, session recovery/reconnection, structured audit logging, facilitator runbook.

## Project layout

- `research/` - Local source-of-truth reports and markdown conversions
- `plan/` - Markdown project roadmap
- `platform/` - Runnable `oTree` prototype
- `platform/carbonsim_phase12/` - Main oTree app (engine, pages, deployment module)
- `platform/tests/` - Unit test suite (86 tests)
- `platform/FACILITATOR_RUNBOOK.md` - Workshop operations guide
- `activeContext.md` - Current implementation tracking

## Local setup

Use Python 3.12 for oTree. The default Python 3.14 runtime on this machine is too new.

```bash
uv venv .venv --python "C:\Users\tukum\AppData\Roaming\uv\python\cpython-3.12.13-windows-x86_64-none\python.exe"
.venv/Scripts/python.exe -m ensurepip --upgrade
.venv/Scripts/python.exe -m pip install --upgrade pip
.venv/Scripts/python.exe -m pip install -r platform/requirements.txt
```

## Running tests

From `platform/`:

```bash
../.venv/Scripts/python.exe -m unittest tests.test_engine tests.test_deployment
```

## Running the prototype

For a clean local database, delete `platform/db.sqlite3` first. Then start the server:

```bash
set PATH=C:\Users\tukum\Downloads\carbonsim-online\.venv\Scripts;%PATH%
cd platform
otree devserver 8000
```

Open the demo or room pages from the running server and use one of the session configs.

## Docker deployment

```bash
cd platform
cp .env.example .env
# Edit .env with production values (OTREE_ADMIN_PASSWORD, SECRET_KEY, etc.)
docker compose up -d
docker compose logs -f web
```

## Heroku deployment

```bash
cd platform
heroku create your-app-name
heroku config:set OTREE_ADMIN_PASSWORD=your-strong-password
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set OTREE_PRODUCTION=1
git push heroku main
```

## Session configs

| Config | Scenario | Description |
|--------|----------|-------------|
| `carbonsim_workshop_phase12` | Vietnam Pilot | Default three-year arc, moderate pressure |
| `carbonsim_high_pressure` | High Pressure | Sharper cap decline, higher penalties, fewer offsets |
| `carbonsim_generous` | Generous Allocation | Gentler decline, lower penalties, more offsets |
| `carbonsim_workshop_with_bots` | Vietnam Pilot + Bots | Same as Vietnam Pilot with 3 bot participants |

## Research documents

The original research corpus remains in `research/`, including:

- `research/20260213_Recommendation_20Report_EN.md`
- `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`
- `research/2026-04-13_online-carbonsim-platform-create.md`
- `research/carbonsim prelim research.md`

See individual documents for licensing and attribution information.