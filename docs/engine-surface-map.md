# Engine Surface Map

> Generated: 2026-06-02
> Sprint 3 — PHASE-01 (TASK-01-01 through TASK-01-04)
> Classification: GAME-USED / MULTIPLAYER-CANDIDATE / DEAD

## engine/engine.py — Public Functions

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| `build_company_specs` | DEAD | None | Only used by old oTree platform. Game uses `create_initial_state` directly. |
| `create_initial_state` | GAME-USED | `solo.py:create_solo_game`, `coop.py:create_coop_game` | Core state factory for both solo and multiplayer. |
| `build_abatement_menu` | GAME-USED | Indirect via `create_initial_state` | Builds sector-specific abatement measures. |
| `apply_company_decision` | GAME-USED | `server/routes/game.py:decision_route`, `server/routes/game.py:fast_forward`, `server/routes/coop.py:coop_decision`, `engine.py:run_bot_turns` | Primary decision dispatcher (abatement, offsets, auctions, trades). |
| `propose_trade` | MULTIPLAYER-CANDIDATE | `engine.py:apply_company_decision` | Exposed in `__init__.py` but only called indirectly. Needed for competitive multiplayer (Sprint 4). |
| `respond_to_trade` | MULTIPLAYER-CANDIDATE | `engine.py:apply_company_decision` | Same as `propose_trade`. |
| `open_auction` | MULTIPLAYER-CANDIDATE | None direct; auctions created in `_start_year` | Auction lifecycle function. Needed for auction flow in multiplayer. |
| `submit_auction_bid` | MULTIPLAYER-CANDIDATE | `engine.py:apply_company_decision`, `engine.py:run_bot_turns` | Bid submission. |
| `close_auction` | MULTIPLAYER-CANDIDATE | None direct | Auction clearing. Needed for auction flow. |
| `start_simulation` | GAME-USED | `solo.py:create_solo_game`, `coop.py:create_coop_game`, `server/routes/game.py:advance_year` | Transitions from lobby to year 1. |
| `pause_session` | MULTIPLAYER-CANDIDATE | None direct | Host control for multiplayer. Referenced in `build_player_snapshot` can_pause flag. |
| `resume_session` | MULTIPLAYER-CANDIDATE | None direct | Host control for multiplayer. Referenced in `build_player_snapshot` can_resume flag. |
| `force_advance_phase` | GAME-USED | `server/routes/game.py:advance_year`, `server/routes/game.py:end_year`, `server/routes/game.py:fast_forward`, `server/routes/coop.py:coop_ready`, `engine/playtest.py` | Core phase transition driver. |
| `update_participant_status` | MULTIPLAYER-CANDIDATE | None direct | Tracks participant activity. Useful for facilitator dashboard in multiplayer. |
| `advance_state` | GAME-USED | `engine.py:apply_company_decision`, `engine.py:propose_trade`, `engine.py:respond_to_trade`, `engine.py:open_auction`, `engine.py:submit_auction_bid`, `engine.py:close_auction` | Auto-advances phase on deadline expiry. |
| `build_player_snapshot` | GAME-USED | `server/routes/game.py:_snapshot`, `engine/coop.py:participant_snapshot` | Player-facing state snapshot. |
| `build_facilitator_snapshot` | MULTIPLAYER-CANDIDATE | None direct | Facilitator/host dashboard data. Calls `build_session_analytics`, `build_session_replay`, `build_session_summary`. Needed for Sprint 4 host panel. |
| `build_session_replay` | MULTIPLAYER-CANDIDATE | `engine.py:build_facilitator_snapshot` | Timeline + company paths + market path. Useful for end-of-game review. |
| `build_session_analytics` | MULTIPLAYER-CANDIDATE | `engine.py:build_facilitator_snapshot`, `engine/playtest.py` | Sector breakdown, year metrics, company costs. Useful for analytics/reports. |
| `export_session_data` | MULTIPLAYER-CANDIDATE | None direct | CSV/export format for session data. Useful for workshop facilitator exports. |
| `build_session_summary` | GAME-USED | `server/routes/game.py:summary`, `server/routes/coop.py:coop_summary`, `engine/playtest.py`, `engine.py:build_facilitator_snapshot` | End-of-game rankings + facilitator notes. |
| `apply_shock` | MULTIPLAYER-CANDIDATE | `engine/cards.py:resolve_card` | Shock event system. Called by card resolution. Needed for event cards in both solo and multiplayer. |
| `run_bot_turns` | GAME-USED | `server/routes/game.py:end_year`, `server/routes/game.py:fast_forward`, `engine/playtest.py` | Bot AI decision automation. |

## engine/engine.py — Internal Functions (not in `__init__.py`)

| Surface | Classification | Notes |
|---|---|---|
| `_company_snapshot` | GAME-USED | Helper for `build_player_snapshot`. |
| `_start_year` | GAME-USED | Year initialization: allocation, auctions, projections. |
| `_close_current_year` | GAME-USED | Year-end compliance: penalties, banking, offsets. |
| `_projected_emissions` | GAME-USED | Emissions calculation given active abatements. |
| `_set_phase` | GAME-USED | Phase transition with duration/deadline. |
| `_append_event` | GAME-USED | Audit log entry. |
| `_event_summary` | GAME-USED | Human-readable event text. |
| `_status_text` | GAME-USED | Phase status message for UI. |
| `_get_company` | GAME-USED | Company lookup helper. |
| `_get_measure` | GAME-USED | Abatement measure lookup. |
| `_get_auction` | GAME-USED | Auction lookup helper. |
| `_get_trade` | GAME-USED | Trade lookup helper. |
| `_build_year_auctions` | GAME-USED | Filter auctions by current year. |
| `_activate_pending_abatements` | GAME-USED | Year-start pending→active transition. |
| `_recalculate_company_projection` | GAME-USED | Recompute emissions + gap after decisions. |
| `_expire_trades` | GAME-USED | Auto-expire stale trade proposals. |
| `_decision_summary` | DEAD | Unused helper. No callers in engine or server. |
| `_serialize_time` | GAME-USED | datetime→ISO string. |
| `_parse_time` | GAME-USED | ISO string→datetime. |
| `_normalize_time` | GAME-USED | Ensure UTC timezone. |
| `_build_rankings` | GAME-USED | Called by `build_session_summary`. |
| `_facilitator_notes` | GAME-USED | Called by `build_session_summary`. |
| `_tracked_years` | GAME-USED | Called by `_build_year_markers`. |
| `_build_year_markers` | GAME-USED | Called by `build_session_analytics` and `build_session_replay`. |

## engine/solo.py

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| `create_solo_game` | GAME-USED | `server/routes/game.py:create_game_route`, `engine/playtest.py` | Solo game factory. |
| `solo_player_company` | GAME-USED | `server/routes/game.py:_snapshot`, `server/routes/game.py:decision_route`, `server/routes/game.py:fast_forward`, `engine/playtest.py` | Finds the human player company. |

## engine/coop.py

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| `create_coop_game` | GAME-USED | `server/routes/coop.py:create_coop_route` | Co-op game factory. |
| `add_coop_participant` | GAME-USED | `server/routes/coop.py:join_coop_route` | Join flow. |
| `set_participant_connection` | MULTIPLAYER-CANDIDATE | None direct | Reconnection tracking. Needed for Sprint 4 reconnect. |
| `set_participant_ready` | GAME-USED | `server/routes/coop.py:coop_ready` | Ready check. |
| `all_participants_ready` | GAME-USED | `server/routes/coop.py:coop_ready` | Ready check gate. |
| `reset_ready_check` | GAME-USED | `server/routes/coop.py:coop_ready` | Reset after phase advance. |
| `participant_snapshot` | GAME-USED | `server/routes/coop.py:create_coop_route`, `server/routes/coop.py:join_coop_route`, `server/routes/coop.py:coop_decision`, `server/routes/coop.py:get_coop_state` | Co-op player state. |

## engine/cards.py

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| `CardDeck` (class) | GAME-USED | `server/routes/game.py:advance_year`, `engine/playtest.py` | Weighted card draw with prerequisites. |
| `draw_cards` | GAME-USED | `server/routes/game.py:advance_year`, `engine/playtest.py` | Draw + audit log. |
| `resolve_card` | GAME-USED | `server/routes/game.py:resolve_card_route`, `engine/playtest.py` | Apply card effects (shocks). |

## engine/achievements.py

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| `ACHIEVEMENTS` (dict) | GAME-USED | `engine/__init__.py` export | Achievement definitions. |
| `compute_achievements` | GAME-USED | `server/routes/game.py:summary` | Evaluate achievements at game end. |

## engine/tutorial.py

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| `TUTORIAL_CARDS` (list) | GAME-USED | `server/routes/game.py:advance_year` | Tutorial event cards. |
| `mark_tutorial_state` | GAME-USED | None direct (state flag set in solo.py) | Marks tutorial flags. |
| `tutorial_notes_for_year` | GAME-USED | `server/routes/game.py:end_year` | Year-specific tutorial hints. |

## engine/playtest.py

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| `run_playtest` | GAME-USED | `engine/__init__.py` export | Single automated playthrough. |
| `run_playtest_batch` | GAME-USED | `server/routes/game.py:playtest_route` | Batch playtests for balance tuning. |
| `summarize_playtests` | GAME-USED | `engine/playtest.py:run_playtest_batch` | Aggregate metrics. |

## engine/scenarios.py

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| `SCENARIO_PACKS` (dict) | GAME-USED | `engine.py:create_initial_state`, `engine/solo.py`, `engine/constants.py` | Scenario definitions (vietnam_pilot, solo_easy, solo_standard, solo_hard, solo_tutorial, high_pressure, generous). |
| `SHOCK_CATALOG` (dict) | GAME-USED | `engine.py:apply_shock` | Shock type definitions. |
| `TECH_UNLOCK_TEMPLATES` (dict) | GAME-USED | `engine.py:apply_shock` (tech_unlock shock) | Abatement measure templates for tech unlock shocks. |

## engine/constants.py

| Surface | Classification | Callers | Notes |
|---|---|---|---|
| Phase constants (`PHASE_*`) | GAME-USED | Throughout engine + server | Phase identifiers. |
| `DEFAULT_PHASE_DURATIONS` | GAME-USED | `engine.py:create_initial_state`, `engine.py:_set_phase` | Default phase timeouts. |
| `DEFAULT_*` constants | GAME-USED | Throughout engine | Default values for penalty, offset, auction, trade. |
| `BOT_STRATEGIES` | GAME-USED | `engine.py:run_bot_turns` | Bot AI strategy definitions. |
| `YEARLY_ALLOCATION_FACTORS` | GAME-USED | `engine.py:create_initial_state` | Fallback allocation factors. |
| `PHASE_LABELS` | GAME-USED | `engine.py:build_player_snapshot`, `engine.py:build_facilitator_snapshot` | Human-readable phase names. |

## Summary Counts

| Category | Count |
|---|---|
| GAME-USED | 38 |
| MULTIPLAYER-CANDIDATE | 13 |
| DEAD | 2 |

## Dead Code Details

1. **`build_company_specs`** (`engine.py:36-49`) — Built for oTree workshop platform. The game uses `create_initial_state` which builds company specs inline. No callers in server/, web/, or engine/ (other than `__init__.py` export).

2. **`_decision_summary`** (`engine.py:1916-1929`) — Internal helper that builds a decision summary dict. No callers anywhere in the codebase.

## Proposed Actions

| Surface | Action |
|---|---|
| `build_company_specs` | Remove from `__init__.py` and `engine.py`. Dead oTree artifact. |
| `_decision_summary` | Remove from `engine.py`. Dead internal helper. |
| All MULTIPLAYER-CANDIDATE surfaces | Keep but document as quarantine candidates. Sprint 4 will determine which are adopted. |
| All GAME-USED surfaces | Core engine — no changes in this phase. |
