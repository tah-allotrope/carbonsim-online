# Final Report — Vietnam Exchange Retheme & VND Reprice

**Plan:** `plans/2026-06-30-vietnam-exchange-retheme-reprice-plan.md`
**Date:** 2026-06-30
**Status:** All 5 phases shipped. 170/170 tests pass. One open finding queued for the plan author.

> *Note:* the available `skill` list does not include a `/report` skill — the per-phase + final reports are emitted as markdown to `reports/` as a substitute, per the request cadence (one report per phase + one final at the end).

## Phase ledger

| Phase | Title | Commit | Report | Tests |
|---|---|---|---|---|
| — | Q-001 / Q-002 locked into the plan | (in `plans/2026-06-30-…`) | — | — |
| 1 | Engine VND reprice + VN volume rescale | `888653d` | `reports/2026-06-30-phase-01-engine-reprice.md` | 152 → 166 |
| 2 | VND display layer (format.js, `$` → `đ`) | `80a5d43` | `reports/2026-06-30-phase-02-vnd-display.md` | 166 |
| 3 | Accent retint toward board palette | `6e9908c` | `reports/2026-06-30-phase-03-accent-retint.md` | 166 |
| 4 | Board stat tiles + opening-session strip | `c8dbc1f` | `reports/2026-06-30-phase-04-board-tiles.md` | 166 → 170 |
| 5 | Balance regression + verification | `60f78f7` | `reports/2026-06-30-phase-05-balance-verification.md` | 170 |

Final: 170 passed, 1 expected warn (httpx deprecation from FastAPI's TestClient — pre-existing, unrelated).

## What shipped (one-line per phase)

**PHASE-01** — Engine. New constants `VND_FX = 5440.0`, `VN_NATIONAL_ALLOCATION_TCO2E = 511_473_846.0`, derived `VN_VOLUME_FACTOR ≈ 639,444.73`. `scenarios.py` refactored into `_RAW_PACKS` + `_rescale_vn_pack` builder (per-field mapping per plan CON-001). Jurisdiction overlays FX'd at `load_jurisdiction` load time; VN volume factor intentionally not applied to EU/CA (plan DEC-002). Anchors: `vietnam_pilot.offset_price = 136,000 đ`; 3-year cap sum = 511,473,846 tCO2e. EU penalty 950 → 5,168,000; VN solo_standard 1000 → 5,440,000.

**PHASE-02** — Frontend display. New `web/js/format.js` with `formatVnd` / `formatVndAbbrev` / `formatTonnes` / `formatTonnesAbbrev` (Vietnamese dot-grouping via `Intl.NumberFormat('vi-VN')`). 30+ `$` → `đ` substitutions across `game.html` / `summary.html` / `coop.html`; legacy `fmt` shims kept as defensive stubs. `effects.js` `animateCounter` delegates to the shared formatters.

**PHASE-03** — Accent retint. `:root` retinted in `web/css/style.css`: cyan/teal family (`#0891b2` / `#06b6d4` / `#155e75`), green-600 (`#16a34a`), red-600 (`#dc2626`). Cream base + warm text/lines unchanged. WCAG: accent-ink 7.78:1 (AA normal); red 5.27:1 (AA normal); accent/green 3:1 (AA large) on `#fffefb` panel. All inline `rgba(...)` and hex literals swept in `game.html` / `summary.html` / `coop.html`.

**PHASE-04** — Market board. Engine: `_build_market_board(state)` → `build_player_snapshot()["market_board"]` (six fields: `total_allocated_quota`, `latest_execution_price`, `total_trade_volume`, `total_trade_value`, `best_bid`, `lowest_offer`; `None` for absent data). Frontend: `renderBoardStatTiles` (six-tile CSS grid, cyan/teal left-border) + `renderOpeningSessionStrip` (static, VN-only, with the real 29/06/2026 first-transaction facts: VN2025 · 400 tCO2e · 54.000.000 đ · 135.000 đ/tCO2e · Listed pill). New `.board-grid` / `.board-tile` / `.opening-session-strip` CSS.

**PHASE-05** — Verification. 170/170 tests pass. Strategy sweep run on `solo_standard` and across all 7 VN packs; per-pack penalty-nudge experiment (x1 → x50) confirms the structural break documented in PHASE-01 F-1 cannot be closed by tuning the per-tonne penalty. Three new tools committed for the plan author to re-run after amending CON-001.

## The headline product surface

```
vietnam_pilot (default pack)
  offset_price:  136.000 đ/tCO2e         ← real first-transaction price
  penalty_rate:  1.637.440 đ/tCO2e       ← FX-only per-tonne
  total quota:   511.473.846 tCO2e       ← real national allocation

  Red River Thermal:  76.733.400 tCO2e/yr × 0,92 = 70.594.728 tCO2e (year 1)
  Hai Phong Steel:    60.747.275 tCO2e/yr × 0,92 = 55.887.493 tCO2e
  Da Nang Cement:     56.271.160 tCO2e/yr × 0,92 = 51.769.467 tCO2e
  ─────────────────────────────────────
  year 1 cap sum:                          178.251.688 tCO2e
  3-year cap sum:                          511.473.846 tCO2e  ✓ headline

Market screen
  Opening session · 29/06/2026 · VN2025 · 400 tCO2e · 54.000.000 đ
  · Lowest offer 135.000 đ/tCO2e · [Listed]                ← static anchor

  Board stat tiles (6):
    Total Allocated Quota      511.473.846 tCO2e
    Latest Execution Price     136.000 đ/tCO2e
    Total Trade Volume         — t
    Total Trade Value          — đ
    Highest Buy Bid            — đ/tCO2e
    Lowest Sell Offer          — đ/tCO2e
```

## Open finding — CON-001 amendment (queued for plan author)

Documented in PHASE-01 finding F-1 and PHASE-05 verification. Per-tonne penalty (FX only) and lump-sum cash (FX × V) are on different scales, fixing the penalty/cash ratio at `1 / V` of pre-rescale. No amount of per-pack penalty tuning closes the gap; the empirical nudge scan only shifts dominance from `aggressive` to `opportunistic`.

Two recommended amendments, both plan-level changes (out of scope for the per-phase implementation):

* **Option A** — apply `V` to `penalty_rate` for VN packs (in addition to FX). Restores the penalty/cash ratio. Display value becomes astronomical (~3.5e12 đ/tCO2e) — would need a "penalty in tỷ đ" display unit.
* **Option B** — drop `V` from cash (apply FX only). Cash becomes 8.16e9 đ ≈ $343k, plausible industrial budget. Penalty 5.44M đ/tonne = 67% of cash/tonne — compliance mandatory, not optional. Abatement cost 3.13e14 đ per measure becomes unaffordable; the strategy sweep would shift to a "compliance via offsets + auctions" game.

Either amendment is a CON-001 table edit + a 1-line change in `_rescale_vn_pack` (option A) or a parameter swap in `_scale_money` for `co["cash"]` (option B). The plan's 5pp drift tolerance is unreachable as written.

## How to re-run the verification

```
# full test suite
pytest engine/tests/ server/tests/                # 170 passed

# strategy sweep on solo_standard (the swept pack)
python -m tools.strategy_sweep                    # 20 seeds, prints dominant

# per-pack sweep (10 seeds each, all 7 VN packs)
python -m tools.pack_sweep                        # shows max strategy + distribution

# per-pack penalty nudge scan (solo_standard, x1 -> x50)
python -m tools.penalty_nudge                     # shows dominance migration
```

## Files touched

```
M  engine/constants.py
M  engine/engine.py
M  engine/scenarios.py
M  engine/tests/test_agents.py
M  engine/tests/test_cards.py
M  engine/tests/test_engine.py
M  engine/tests/test_meta.py
M  engine/tests/test_vietnam_reprice.py            (new, 18 tests)
M  plans/2026-06-30-vietnam-exchange-retheme-reprice-plan.md
M  reports/2026-06-30-phase-01-engine-reprice.md   (new)
M  reports/2026-06-30-phase-02-vnd-display.md     (new)
M  reports/2026-06-30-phase-03-accent-retint.md   (new)
M  reports/2026-06-30-phase-04-board-tiles.md     (new)
M  reports/2026-06-30-phase-05-balance-verification.md  (new)
M  tools/pack_sweep.py                            (new)
M  tools/penalty_nudge.py                         (new)
M  tools/strategy_sweep.py                        (new)
M  web/coop.html
M  web/css/style.css
M  web/game.html
M  web/js/effects.js
M  web/js/format.js                               (new)
M  web/summary.html
```

5 commits, all on `master`, all pushed to `origin`.
