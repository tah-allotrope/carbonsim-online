# CarbonSim Online

A single-player and multiplayer carbon compliance game built with FastAPI and vanilla JS.

## Architecture

- **Engine:** `carbonsim_engine/` — deterministic compliance engine (year cycle, abatement, offsets, banking, penalties, cards, tutorial, achievements, playtest)
- **Server:** `mayor_api/` — FastAPI backend serving the API and static frontend, with WebSocket support for co-op mode
- **Web:** `mayor_web/` — static HTML/CSS/JS frontend (game UI, co-op UI, summary screens)

## Local Setup

```bash
pip install -r requirements.txt
pip install -e carbonsim_engine/
```

## Running the Server

```bash
uvicorn mayor_api.main:create_app --factory --reload
```

Open `http://localhost:8000` in a browser.

## Running Tests

```bash
pytest mayor_api/tests/test_api.py carbonsim_engine/tests/ -q
```

## Project Layout

| Directory | Purpose |
|-----------|---------|
| `carbonsim_engine/` | Compliance engine, cards, tutorial, achievements, playtest |
| `mayor_api/` | FastAPI server, routes, WebSocket, database, models |
| `mayor_web/` | Static HTML/CSS/JS frontend |
| `plans/` | Sprint plans and roadmap |
| `research/` | Vietnam ETS research and product framing |
| `reports/` | Phase and final reports |
| `archive/` | Archived oTree platform and obsolete plans |

## Sprint Roadmap

See `plans/2026-05-29-game-focus-roadmap-index.md` for the 5-sprint execution plan:

1. **Canonical Game Stack Consolidation** — declare game stack canonical, archive oTree, rewrite docs
2. **Repository Reorganization & Clutter Purge** — conventional layout, delete duplicates
3. **Engine Trim, Modularization & Test Unification** — clean tested core, fix failing tests
4. **Single-Player Polish & Multiplayer Build-Out** — lobby, room codes, host controls, reconnection
5. **Visual Step-Change** — design system, signature animated visual

## Research Documents

- `research/2026-04-13_online-carbonsim-platform-create.md`
- `research/20260213_Recommendation_20Report_EN.md`
- `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`
- `research/carbonsim prelim research.md`

See individual documents for licensing and attribution.
