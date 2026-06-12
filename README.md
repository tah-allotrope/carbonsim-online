# CarbonSim Online

A single-player and multiplayer carbon compliance game built with FastAPI and vanilla JS.

## Architecture

- **Engine:** `engine/` — deterministic compliance engine (year cycle, abatement, offsets, banking, penalties, cards, tutorial, achievements, playtest)
- **Server:** `server/` — FastAPI backend serving the API and static frontend, with WebSocket support for co-op mode
- **Web:** `web/` — static HTML/CSS/JS frontend (game UI, co-op UI, summary screens)

## Local Setup

```bash
pip install -r requirements.txt
pip install -e engine/
```

## Running the Server

```bash
uvicorn server.main:create_app --factory --reload
```

Open `http://localhost:8000` in a browser.

## Running Tests

```bash
pytest server/tests/test_api.py engine/tests/ -q
```

## Project Layout

| Directory | Purpose |
|-----------|---------|
| `engine/` | Compliance engine, cards, tutorial, achievements, playtest, scenarios |
| `server/` | FastAPI server, routes, WebSocket, database, models, tests |
| `web/` | Static HTML/CSS/JS frontend (game, co-op, summary screens) |
| `plans/` | Sprint plans and roadmap |
| `research/` | Vietnam ETS research and product framing |
| `reports/` | Phase and final reports |
| `scripts/` | Utility scripts (report rendering) |
| `archive/` | Archived oTree platform, obsolete plans, and old reports |
| `docs/` | Project structure and contributor guides |

## Sprint Roadmap

See `plans/2026-05-29-game-focus-roadmap-index.md` for the 5-sprint execution plan:

1. **Canonical Game Stack Consolidation** — declare game stack canonical, archive oTree, rewrite docs
2. **Repository Reorganization & Clutter Purge** — conventional layout, delete duplicates
3. **Engine Trim, Modularization & Test Unification** — clean tested core, fix failing tests
4. **Single-Player Polish & Multiplayer Build-Out** — lobby, room codes, host controls, reconnection
5. **Visual Step-Change** — design system, signature animated visual

## Asset Attributions

See `ATTRIBUTIONS.md` for the source, author, and license of every asset under `web/assets/`.

## Research Documents

- `research/2026-04-13_online-carbonsim-platform-create.md`
- `research/20260213_Recommendation_20Report_EN.md`
- `research/20250708_Impact-Assessing-and-Modeling-Report_EN.md`
- `research/carbonsim prelim research.md`

See individual documents for licensing and attribution.
