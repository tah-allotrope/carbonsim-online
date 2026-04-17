# CarbonSim Online

This repository now contains both the Vietnam ETS research base and a runnable `oTree` prototype for phases 1 through 5 of the implementation plan.

## What is implemented

- `plan/project-plan.md` defines the multi-phase roadmap.
- `platform/` contains an `oTree` project with the `carbonsim_phase12` app.
- Phase 1 is covered by a working room/session scaffold, participant join flow, facilitator-controlled launch, and a placeholder company dashboard.
- Phase 2 is covered by a deterministic year engine with year-start allocation, emissions growth, banking, year-end surrender, penalties, and an audit log.
- Phase 3 adds sector-specific abatement menus, immediate vs. next-year activation timing, offset holdings with a configurable surrender cap, and dashboard projections for forward-looking compliance decisions.
- Phase 4 adds a sealed-bid, uniform-price primary auction with auction scheduling, bid validation, deterministic clearing, settlement into allowance holdings, public result display, and facilitator open/clear controls.
- Phase 5 adds bilateral secondary trading with trade proposals, buyer accept or reject responses, server-side holdings and cash validation, expiration handling, and a public trade feed.

## Project layout

- `research/` - local source-of-truth reports and markdown conversions
- `plan/` - markdown project roadmap
- `platform/` - runnable `oTree` prototype
- `activeContext.md` - current implementation tracking

## Local setup

Use Python 3.12 for `oTree`. The default Python 3.14 runtime on this machine is too new for the current setup.

```bash
uv venv .venv --python "C:\Users\tukum\AppData\Roaming\uv\python\cpython-3.12.13-windows-x86_64-none\python.exe"
./.venv/Scripts/python.exe -m ensurepip --upgrade
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -r platform/requirements.txt
```

## Running the prototype

From `platform/`:

```bash
../.venv/Scripts/python.exe -m unittest tests.test_engine
```

For a clean local database, `oTree` expects `db.sqlite3` to match its internal schema version. The easiest path is:

```bash
rm "platform/db.sqlite3"
```

Then start the server from `platform/`. On Windows, make sure the virtualenv `Scripts` directory is on `PATH` before starting `oTree`, otherwise the dev reloader may not find `otree.exe`.

```bash
set PATH=C:\Users\tukum\Downloads\carbonsim-online\.venv\Scripts;%PATH%
cd platform
otree devserver 8000
```

Open the demo or room pages from the running server and use the `carbonsim_workshop_phase12` session config.

## Verification completed

- `../.venv/Scripts/python.exe -m unittest tests.test_engine`
- Local `oTree` boot check against `http://127.0.0.1:8001/` after creating the database and setting the SQLite schema version expected by `oTree`

The test suite now covers phase 5 behavior as well, including trade proposal, acceptance, rejection, expiration, and settlement validation alongside the earlier auction and compliance rules.

## Research documents

The original research corpus remains in `research/`, including:

- `research/20260213_Recommendation_20Report_EN.md`
- `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`
- `research/2026-04-13_online-carbonsim-platform-create.md`
- `research/carbonsim prelim research.md`

See individual documents for licensing and attribution information.
