---
title: "CarbonSim — Vietnam Exchange Retheme & VND Reprice"
date: "2026-06-30"
status: "draft"
request: "Adjust CarbonSim visual/color palette to align with the Vietnam domestic carbon exchange trading board photo AND adjust game mechanics to reflect the first-transaction article (136,000 VND/tCO2e, VN2025, 511,473,846 tCO2e total allocation, first session 29/06/2026)."
plan_type: "multi-phase"
research_inputs:
  - "research/2026-06-30_vietnam-exchange-retheme-reprice-brainstorm.md"
---

# Plan: CarbonSim — Vietnam Exchange Retheme & VND Reprice

## Objective
Make CarbonSim feel ripped from the 29/06/2026 headline: re-denominate the economy in
Vietnamese đồng so the default pilot price lands on the real **136,000 đ/tCO2e**, rescale
the Vietnam scenario so company allocations sum to the real national quota of
**511,473,846 tCO2e**, surface the real exchange board's stat tiles, and retint the existing
(light) UI toward the board's cyan/teal + green-listed + red-sell language with monospace
numeric tickers. Visual change is the headline; the mechanics changes make the look meaningful.

## Context Snapshot
- **Current state:**
  - Vanilla HTML/CSS/JS frontend served by FastAPI; deterministic Python engine; SQLite.
  - Theme = bright cream/azure Kairosoft palette, all tokens in `web/css/style.css` `:root`
    (`--bg:#fdf6e9`, `--accent:#1f93c7`, `--green:#4caf50`, `--red:#e2553f`, bevel/gradient
    tokens, `--mono` already defined).
  - Prices are abstract `$X.XX`. Defaults in `engine/constants.py`
    (`DEFAULT_OFFSET_PRICE=25.0`, `DEFAULT_PENALTY_RATE=200.0`, auction floor 80 / ceiling 300).
  - Per-pack economics in `engine/scenarios.py` (`vietnam_pilot`: `offset_price=25.0`,
    `penalty_rate=301.0`, `allocation_factors {1:0.92,2:0.88,3:0.84}`, three companies with
    `baseline_emissions` ~88–120 t and `cash` ~1.05–1.5M, abatement `cost` ~38k–90k).
  - Live price calc in `engine/engine.py` (~lines 361–398): `base_price * (1 + elasticity *
    min(demand/supply_cap, 1.0))`, forwards at 1.05× spot.
  - Frontend currency is a hardcoded `$` prefix at ~126 sites across `web/game.html`,
    `web/summary.html`, `web/coop.html`, `web/index.html`, plus `web/js/effects.js`.
  - Number formatting via a duplicated `fmt(n)` helper (`game.html:1120`, `summary.html:258`,
    `coop.html:410`, and currency-aware variant in `effects.js:24`) that abbreviates with
    `M`/`K` and `toFixed`.
  - Tests exist that may assert on monetary values: `engine/tests/test_engine.py`,
    `test_agents.py`, `test_policy_story.py`, `test_meta.py`, `test_cards.py`,
    `server/tests/test_api.py`, `test_coop.py`.
- **Desired state:**
  - All monetary values in VND; `vietnam_pilot` base price = 136,000 đ/tCO2e (FX factor
    ≈ ×5,440 from 25). Other packs scale by the same factor.
  - Vietnam packs rescaled so the sum of company allocations ≈ 511,473,846 tCO2e; CA/EU
    jurisdiction overlays keep their own realistic totals.
  - UI shows `136.000 đ/tCO2e` with Vietnamese dot-grouping (`511.473.846`), monospace tickers.
  - Market screen shows board stat tiles (total allocated quota, latest execution price,
    trade volume, trade value, best bid, lowest offer) plus a static "opening session"
    reference strip with the real first-trade figures.
  - Light layout retained; accents retinted toward cyan/teal/green/red.
- **Key repo surfaces:** `engine/constants.py`, `engine/scenarios.py`, `engine/engine.py`,
  `engine/data/jurisdictions/*.json`, `web/css/style.css`, `web/game.html`,
  `web/summary.html`, `web/coop.html`, `web/index.html`, `web/js/effects.js`,
  `engine/tests/*`, `server/tests/*`.
- **Out of scope:** Dark mode / theme toggle / `isocity.js` canvas re-theme; new trading
  instruments or a continuous order book; hand re-tuning difficulty beyond preserving ratios;
  Vietnamese-language UI translation (only currency symbol + number format change); DB schema
  changes beyond what the constant reprice/rescale requires.

## Research Inputs
- `research/2026-06-30_vietnam-exchange-retheme-reprice-brainstorm.md` — Fixes all ten core
  decisions (visual-led; accent-retint only; reprice-in-place to VND; one proportional FX
  factor anchored on `vietnam_pilot`→136,000; add board stat tiles; `đ` label + Vietnamese
  dot-grouping; rescale VN packs to sum 511M). Its CON-001 (two orthogonal scaling axes —
  per-tonne rates vs. tonnage vs. lump-sum cash — must not be double-applied) directly shapes
  Phase 1's per-field mapping. Its two open questions are carried into `## Grill Me` below.

## Assumptions and Constraints
- **ASM-001:** Retint reuses existing CSS tokens/classes (`--accent`, `--green`, `--red`,
  `.badge-*`, `.stat-value`, `--mono`); no new component framework.
- **ASM-002:** Board bid/offer tiles populate from existing instruments (OTC `propose_trade`,
  auction bids, forwards); when no live order exists, show `—`.
- **ASM-003:** `vietnam_pilot` stays the default pack and the canonical 136,000 anchor.
- **CON-001 (critical):** Two orthogonal scaling axes. **FX reprice (×5,440)** applies to
  *per-tonne rates* and *cash amounts*; the **volume rescale** (to hit 511M) applies to
  *tonnage quantities* and to *cash that scales with company size*. Per-field mapping:
  - Per-tonne fields → **FX only**: `offset_price`, `penalty_rate`, `auction_price_floor`,
    `auction_price_ceiling`, `DEFAULT_OFFSET_PRICE`, `DEFAULT_PENALTY_RATE`.
  - Tonnage fields → **volume factor (V) only**: `baseline_emissions`, `abatement_amount`,
    derived allocations/caps. (No price dimension — do not apply FX.)
  - Lump-sum cash → **FX × V**: company `cash`, abatement `cost` (scales with company size).
  Define V per Vietnam pack so `sum(baseline_emissions × allocation_factor)` ≈ 511,473,846.
- **CON-002:** Number formatting is **display-only**; engine/DB/JSON stay numeric floats to
  preserve deterministic arithmetic. Never store dot-grouped strings.
- **CON-003:** Balance is hand-tuned (memory: `solo_standard` penalty=1000 for flattest
  win-rate; policy-stability cap-modifier neutral at 70). Reprice + rescale must preserve
  *ratios*; a balance-regression pass is mandatory before merge.
- **CON-004:** Keep the light layout legible — retinted accents must hold WCAG AA contrast on
  cream/near-white panels; do not drop board-dark colors directly onto light surfaces.
- **DEC-001:** FX anchor = `vietnam_pilot` `offset_price` 25 → 136,000 (factor ×5,440);
  all packs scale by the same factor (brainstorm DEC-005).
- **DEC-002:** Rescale scope = Vietnam packs only; sum-of-company-caps ≈ 511,473,846 tCO2e
  (brainstorm DEC-010).

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Reprice + rescale the engine economy to VND / 511M | None | Updated `constants.py`, `scenarios.py`; per-field scaling applied; green test suite |
| PHASE-02 | VND display layer (đ symbol + Vietnamese dot-grouping) | PHASE-01 | Central `fmt`/currency helper; `$`→`đ` across templates; numeric tickers monospace |
| PHASE-03 | Accent retint toward the board palette | None (parallel to 01–02) | Retinted `:root` tokens in `style.css`; contrast-checked light theme |
| PHASE-04 | Board stat tiles + opening-session reference strip | PHASE-01, PHASE-02, PHASE-03 | Market-screen tiles & static opening-session strip in `game.html` |
| PHASE-05 | Balance regression + full verification | PHASE-01–04 | Win-rate/balance check, test/lint pass, screenshots |

## Detailed Phases

### PHASE-01 - Reprice & Rescale the Engine Economy
**Goal**
Re-denominate every monetary value in VND with one FX factor (×5,440) and rescale Vietnam
packs so allocations sum to ~511,473,846 tCO2e, applying CON-001's per-field mapping so the
two scaling axes are never conflated.

**Tasks**
- [ ] TASK-01-01: Define `FX = 5440.0` (so `vietnam_pilot.offset_price` 25 → 136,000) and
      apply to per-tonne + cash defaults in `engine/constants.py`
      (`DEFAULT_OFFSET_PRICE`, `DEFAULT_PENALTY_RATE`, `DEFAULT_AUCTION_PRICE_FLOOR`,
      `DEFAULT_AUCTION_PRICE_CEILING`). Add a short comment documenting the anchor.
- [ ] TASK-01-02: In `engine/scenarios.py`, apply **FX only** to every pack's per-tonne
      fields (`offset_price`, `penalty_rate`, `auction_price_floor`, `auction_price_ceiling`).
      Verify `vietnam_pilot.offset_price == 136000.0`.
- [ ] TASK-01-03: Compute the Vietnam volume factor `V` so
      `sum(company.baseline_emissions × allocation_factor)` over Vietnam packs ≈ 511,473,846.
      Apply `V` to `baseline_emissions` (and any tonnage-derived fields) for Vietnam packs only.
- [ ] TASK-01-04: Apply `FX × V` to Vietnam company `cash` and abatement `cost`; apply `V`
      only to abatement `abatement_amount` (tonnage). Leave CA/EU jurisdiction JSON tonnages
      at their own realistic scale, but apply **FX only** to their per-tonne money fields so
      currency is uniform.
- [ ] TASK-01-05: Audit `engine/engine.py` price/penalty math (~lines 361–398) for any
      hardcoded magnitudes or abbreviation thresholds; confirm formulas are scale-invariant
      (they multiply parametrized values, so should need no change — record the confirmation).
- [ ] TASK-01-06: Update any engine/server tests that assert on old absolute money values
      (`engine/tests/test_engine.py`, `test_agents.py`, `test_meta.py`, `server/tests/*`) to
      the new VND magnitudes; prefer asserting on ratios/relationships where practical.

**Files / Surfaces**
- `engine/constants.py` — default per-tonne + auction money constants.
- `engine/scenarios.py` — all packs' per-tonne fields; Vietnam packs' tonnage + cash fields.
- `engine/engine.py` — confirm price/penalty math is scale-invariant.
- `engine/data/jurisdictions/*.json` — FX on money fields only; tonnages unchanged.
- `engine/tests/*`, `server/tests/*` — update value-coupled assertions.

**Dependencies**
- None.

**Exit Criteria**
- [ ] `vietnam_pilot` base price resolves to 136,000 đ/tCO2e.
- [ ] Sum of Vietnam company allocations ≈ 511,473,846 tCO2e (±0.5%).
- [ ] `pytest engine server` passes.
- [ ] No per-tonne field received the volume factor and no tonnage field received FX (spot-audited).

**Phase Risks**
- **RISK-01-01:** Double-applying FX to a field that's also volume-scaled inflates cash by
  ~5,440×. Mitigation: implement the per-field mapping table from CON-001 as the single source
  of truth; add a unit test asserting the 136,000 anchor and the 511M sum.

### PHASE-02 - VND Display Layer
**Goal**
Show all money as VND with the `đ` symbol and Vietnamese dot-grouping, without abbreviating
the headline figures the board shows in full.

**Tasks**
- [ ] TASK-02-01: Introduce a single shared formatting module (e.g. `web/js/format.js`) with
      `formatVnd(n)` → `136.000 đ` and `formatTonnes(n)` → `511.473.846` using
      `Intl.NumberFormat('vi-VN')` (dot grouping), and have it loaded by `game.html`,
      `summary.html`, `coop.html`.
- [ ] TASK-02-02: Replace the duplicated `fmt(n)` definitions (`game.html:1120`,
      `summary.html:258`, `coop.html:410`) and the currency-aware variant in
      `web/js/effects.js:24` to delegate to the shared helpers. Decide abbreviation policy:
      keep `M`/`K` for inline deltas, but render board headline tiles in **full** dot-grouped
      form (the photo shows `511.473.846`, not `511.5M`).
- [ ] TASK-02-03: Replace the hardcoded `$` prefix at its ~126 sites across `web/game.html`,
      `web/summary.html`, `web/coop.html`, `web/index.html` with the `đ` suffix convention
      (`136.000 đ`), routing through `formatVnd` rather than string-concatenating a symbol.
- [ ] TASK-02-04: Apply `var(--mono)` to all numeric ticker/stat values (price, volume,
      value, cash, allowances) so figures read like the board.

**Files / Surfaces**
- `web/js/format.js` (new) — shared VND/tonnes formatters.
- `web/game.html`, `web/summary.html`, `web/coop.html`, `web/index.html` — symbol + helper swap.
- `web/js/effects.js` — currency-aware float formatter delegates to shared helper.

**Dependencies**
- PHASE-01 (values must already be VND magnitudes).

**Exit Criteria**
- [ ] Price renders as `136.000 đ/tCO2e`; national quota renders as `511.473.846 tCO2e`.
- [ ] No `$` remains in user-facing templates (grep clean).
- [ ] Numeric tickers render in monospace.

**Phase Risks**
- **RISK-02-01:** `vi-VN` locale uses `.` for thousands and `,` for decimals — any code that
  parses formatted strings back to numbers would break. Mitigation: formatting is one-way
  (display only, CON-002); confirm no parse-from-display paths exist.

### PHASE-03 - Accent Retint Toward the Board Palette
**Goal**
Shift the existing light theme's accents toward the board's cyan/teal (headers/active),
green (listed/compliant), red (sell-side/shortfall) language — no dark mode, no canvas changes.

**Tasks**
- [ ] TASK-03-01: In `web/css/style.css` `:root`, retint `--accent`/`--accent-bright`/
      `--accent-ink` toward cyan/teal and adjust `--green`/`--red` toward the board's
      listed-green / sell-red, keeping the cream `--bg`/`--panel` base.
- [ ] TASK-03-02: Update the dependent gradient tokens (`--grad-accent`, `--grad-green`,
      `--grad-red`) to match the retinted accents.
- [ ] TASK-03-03: Verify `--accent-ink` and status colors still meet WCAG AA (≥4.5:1) on
      `--panel`/`--bg`; nudge the `-ink` variants if contrast regresses (CON-004).
- [ ] TASK-03-04: Confirm `.badge-green` reads as "listed/active" and `.badge-red` as
      "sell/shortfall" under the new palette; adjust badge text/border if needed.

**Files / Surfaces**
- `web/css/style.css` — `:root` palette + gradient tokens only.

**Dependencies**
- None (can run parallel to PHASE-01/02).

**Exit Criteria**
- [ ] Accents read cyan/teal-forward; green=listed, red=sell, on the retained light base.
- [ ] All text/accent pairs pass WCAG AA contrast.
- [ ] No layout/structure changes; `isocity.js` untouched.

**Phase Risks**
- **RISK-03-01:** Board-dark cyan dropped onto cream fails contrast or looks muddy.
  Mitigation: use the existing `-ink` darker-variant pattern for text; reserve bright cyan
  for fills/borders, not small text.

### PHASE-04 - Board Stat Tiles & Opening-Session Strip
**Goal**
Reproduce the exchange board's information layout on the market screen and add a static
opening-session reference for authenticity.

**Tasks**
- [ ] TASK-04-01: Add stat tiles to the market section of `web/game.html`: total allocated
      quota (511.473.846 tCO2e), latest execution price, total trade volume, total trade
      value, highest buy bid, lowest sell offer — using `.stat`/`.stat-value` + monospace.
- [ ] TASK-04-02: Wire tiles to existing snapshot fields where present (offset/last price,
      auction clearing price); derive best-bid/lowest-offer from open OTC/auction state, and
      render `—` when none exist (ASM-002). Add snapshot fields in the engine only if a needed
      value isn't already exposed.
- [ ] TASK-04-03: Add a static "Opening session · 29/06/2026" reference strip showing the real
      first-trade facts (VN2025, 400 tCO2e first trade, 54.000.000 đ value, lowest offer
      135.000 đ, "Listed" status pill) on the Vietnam market screen.
- [ ] TASK-04-04: Style green "active/listed" pill and red sell-side figures to match the board.

**Files / Surfaces**
- `web/game.html` — market-screen tiles + opening-session strip.
- `engine/engine.py` / snapshot serializer — only if a tile needs a value not already exposed.

**Dependencies**
- PHASE-01 (values), PHASE-02 (formatting), PHASE-03 (palette).

**Exit Criteria**
- [ ] Market screen shows the six board stat tiles with correct VND/tonnes formatting.
- [ ] Opening-session strip renders the real first-trade figures with a green Listed pill.
- [ ] Empty bid/offer states show `—` rather than `0`/`NaN`.

**Phase Risks**
- **RISK-04-01:** No live order book means bid/offer tiles look empty in solo play.
  Mitigation: derive from current offers/auction state; otherwise the opening-session strip
  carries the headline figures so the board still reads as intended.

### PHASE-05 - Balance Regression & Verification
**Goal**
Prove the reprice/rescale preserved gameplay balance and the visual changes render correctly.

**Tasks**
- [ ] TASK-05-01: Re-run the balance/win-rate check used when `solo_standard` penalty was set
      to 1000 (memory CON-003); confirm no strategy drifts beyond the agreed bar (see Grill Q-001).
- [ ] TASK-05-02: Run full `pytest` (engine + server) and any linters; fix fallout.
- [ ] TASK-05-03: Launch the app via the preview workflow; capture screenshots of the market
      screen (tiles + opening-session strip), compliance meter, and summary screen showing
      VND/monospace/retint.

**Files / Surfaces**
- `engine/tests/*`, `server/tests/*`; whatever harness produced the prior win-rate numbers.

**Dependencies**
- PHASE-01–04.

**Exit Criteria**
- [ ] Balance check within the agreed tolerance; test suite green.
- [ ] Screenshots confirm 136.000 đ pricing, 511.473.846 quota, retinted board look.

**Phase Risks**
- **RISK-05-01:** Rescale subtly shifts win rates beyond tolerance. Mitigation: because FX is a
  uniform multiplier and V preserves intra-pack ratios, drift should be minimal; if it isn't,
  re-tune only the offending pack's `penalty_rate` (per-tonne, FX-scaled) rather than reworking.

## Verification Strategy
- **TEST-001:** `pytest engine/tests server/tests` passes after value-coupled assertions are
  updated to VND magnitudes (PHASE-01/05).
- **TEST-002:** New unit test asserting `vietnam_pilot` base price == 136,000 and Vietnam
  allocation sum ≈ 511,473,846 (±0.5%).
- **MANUAL-001:** Preview the app; confirm price `136.000 đ/tCO2e`, quota `511.473.846 tCO2e`,
  monospace tickers, retinted cyan/teal/green/red, and the opening-session strip.
- **OBS-001:** Grep templates to confirm no `$` remains in user-facing strings.
- **OBS-002:** Re-run the prior win-rate/dominance harness; record before/after per strategy.

## Risks and Alternatives
- **RISK-001:** Conflating the FX and volume axes corrupts the economy (cash off by ~5,440×).
  Mitigation: CON-001 per-field mapping + anchor/sum unit test (TEST-002).
- **RISK-002:** Hidden hardcoded `$`/abbreviation assumptions in JS produce inconsistent
  displays. Mitigation: centralize formatting (PHASE-02) and grep-verify (OBS-001).
- **ALT-001:** Separate `vietnam_2025` pack instead of repricing in place — rejected
  (brainstorm DEC-003); user wants the whole economy in VND.
- **ALT-002:** Full dark trading-board theme — rejected (brainstorm DEC-002); high collision
  with canvas sprites/haze for little gameplay gain.
- **ALT-003:** 511M as flavor stat only without rescaling — rejected (brainstorm DEC-009).

## Grill Me — RESOLVED
1. **Q-001: Balance bar — REUSE win-rate harness, ~5pp drift tolerance.** PHASE-05 runs the same
   harness used when `solo_standard` penalty was tuned to 1000. Any pack whose top-strategy
   win rate drifts >5pp from its current value triggers a per-pack `penalty_rate` nudge
   (per-tonne, FX-scaled) rather than a wholesale re-tune. Recorded 2026-06-30.
2. **Q-002: Opening-session strip — STATIC.** Real first-trade facts (VN2025, 29/06/2026,
   400 tCO2e, 54.000.000 đ, lowest offer 135.000 đ) render as a static reference strip on
   the Vietnam market screen; all other stat tiles remain live/derived from game state
   (show `—` when no order exists). Recorded 2026-06-30.

## Suggested Next Step
Answer the two `## Grill Me` questions, fold the answers into this plan, then begin
implementation with PHASE-01 (engine reprice & rescale) and PHASE-03 (retint) in parallel.
