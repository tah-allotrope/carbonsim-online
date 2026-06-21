# Active Context — Sprint 4: Story (Cascading Cards + Policy Stability + City Canvas)

Plan: `plans/2026-06-21-carbonsim-elevation-plan.md` → PHASE-04
Cadence: implement fully → commit + push master → `/report Sprint 4`.

## Tasks
- [ ] TASK-04-01: `policy_stability` (0–100, start 70) + `active_conditions` + `active_effects` in state; yearly stability update in `_close_current_year`.
- [ ] TASK-04-02: policy-stability cap modulation in `_start_year` (neutral at 70 so existing balance holds); auto crackdown (<30) / relief (>85) triggers.
- [ ] TASK-04-03: Card schema: `follow_on_cards`, `sets_condition`, `requires_condition`, `effect_duration` in `resolve_card`. Injection queue in state.
- [ ] TASK-04-04: State-weighted draw in `CardDeck.draw` (crisis up when stability<40, opportunity up when >75); `requires_condition` gate in `_prereqs_met`.
- [ ] TASK-04-05: Author follow-on chains + `regulatory_crackdown` / `policy_relief` cards in `expansion_deck.json`.
- [ ] TASK-04-06: `active_effects` multi-turn tracking applied + decremented in `_start_year`.
- [ ] TASK-04-07: `web/js/isocity.js` — city-wide policy-climate smog overlay + "city clears" burst trigger.
- [ ] TASK-04-08: snapshot `policy_stability` + `active_conditions`; Policy Climate HUD indicator in `web/game.html`.
- [ ] Tests: extend `engine/tests/test_cards.py` / add policy-stability tests.

## Verification
- `python -m pytest engine/tests/` all pass.
- Missed-compliance year lowers policy_stability; clean year raises it.
- follow_on chain: parent choice injects child; child drawn within 2 years.
- Determinism check still passes.

## Review (complete)
- **All 8 tasks done.** 79 engine tests (+12 in `test_policy_story.py`); 138 total with server tests. Determinism holds. Frontend verified in browser preview (badge + crisis haze render, no console errors).
- `policy_stability` (0–100, start 70) + `active_conditions` + `active_effects` + `pending_card_injections` in state, with `_start_year` migration guards.
- Cap modulated by stability (`cap_modifier`, neutral 1.0 at 70 so Sprint 1–3 balance holds on a fresh game). Coefficient softened to 0.15, clamp [0.88, 1.10].
- `_update_policy_stability` (mean-reverting toward 60 + outcome deltas) and `_apply_policy_triggers` (crackdown <30 / relief >85, non-ratcheting effects).
- `_apply_active_effects` applies + decrements multi-turn card effects each year.
- Cards: `requires_condition` gate, `sets_condition`, `follow_on_cards` injection queue, `effect_duration` → active_effects; state-weighted draw (crisis↑ when stability<40, opportunity↑ when >75). `CardDeck.take_by_id` for forced follow-on draws.
- 10 cascading cards in `expansion_deck.json` (crackdown/relief + CBAM-lobby, missed-deadline→audit, green-tech→early-mover chains, 2 multi-turn duration cards).
- `isocity.js`: city-wide policy-climate haze overlay + `triggerCityClears()` + `setPolicyClimate()`. `game.html`: Policy Climate HUD badge + city-clears on penalty-free close.
- Added `scripts/preview_run.py` (launch.json referenced a missing file).

## Balance note
Policy-stability feedback initially re-created an aggressive-dominant death-spiral in the all-bot sweep (cap tightening + crackdown `cbam_threat` ratcheting penalty_rate via re-drawn crackdown card). Fixed by: softer cap coefficient, mean-reverting stability, and non-ratcheting crackdown effects (allowance_withdrawal, not cbam_threat). Sprint 3 sweep balance preserved (no strategy >60%; max ~0.40).
