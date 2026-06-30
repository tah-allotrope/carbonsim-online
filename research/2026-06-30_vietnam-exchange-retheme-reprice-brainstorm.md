---
title: "CarbonSim — Vietnam Exchange Retheme & VND Reprice"
date: "2026-06-30"
type: "brainstorm"
depth: "standard"
source_request: "Adjust CarbonSim visual/color palette to align with the Vietnam domestic carbon exchange trading board photo AND adjust game mechanics to reflect the first-transaction article (136,000 VND/tCO2e, VN2025, 511,473,846 tCO2e total allocation, first session 29/06/2026)."
slug: "vietnam-exchange-retheme-reprice"
---

# Brainstorm: CarbonSim — Vietnam Exchange Retheme & VND Reprice

## Problem & Why Now
On 29/06/2026 Vietnam recorded its first-ever domestic carbon transaction — 400 tCO2e at
136,000 VND/tCO2e (54,000,000 VND total) on the opening session of the domestic carbon
exchange, quota code VN2025, with a total allocated national quota of 511,473,846 tCO2e
([VnExpress source](https://vnexpress.net/viet-nam-ghi-nhan-giao-dich-carbon-dau-tien-gia-136-000-dong-mot-tan-co2e-5091078.html)).
CarbonSim is a Vietnam-pilot carbon-market sim, so this is a moment to make the game feel
ripped-from-the-headlines: align the look with the real exchange board and ground the
economy in real VND figures and the real national scale. Doing it now capitalizes on the
news cycle and the fact that `vietnam_pilot` is already the default scenario.

## Current vs Desired State
<!-- seeds /plan ## Context Snapshot -->
- **Current state:**
  - Vanilla HTML/CSS/JS frontend served by FastAPI; SQLite persistence; deterministic
    Python engine. Isometric city via `web/js/isocity.js` (canvas).
  - Theme is a **bright cream/azure Kairosoft** palette — all tokens in
    `web/css/style.css` `:root` (`--bg:#fdf6e9`, `--accent:#1f93c7`, `--green:#4caf50`,
    `--red:#e2553f`, bevel/gradient tokens). Monospace token (`--mono`) already exists.
  - Prices are **abstract `$X.XX`** driven by `offset_price` (default 25) and
    `penalty_rate` per pack in `engine/scenarios.py` + `engine/constants.py`.
  - Per-company economy runs at **small scale** (baseline_emissions ~120 t; cash ~1.5M).
  - Packs: `vietnam_pilot` (default, offset 25, penalty 301), `high_pressure`,
    `generous`, `solo_easy/standard/hard/tutorial`; jurisdiction overlays for
    California/EU under `engine/data/jurisdictions/*.json`.
  - Market ticker + compliance meter already render in `web/game.html`; badge classes
    `.badge-blue/green/red/orange` and `.stat-value` exist.
- **Desired state:**
  - **Accent-retint** of the existing (light) layout toward the board's cyan/teal +
    green-listed + red-sell language, with numeric tickers in monospace and
    Vietnamese-formatted VND values. No dark-mode rewrite, no canvas re-theme.
  - Economy denominated in **VND**, with the default Vietnam price landing on the real
    **136,000 VND/tCO2e**, all other monetary values converted by the same factor.
  - Market screen surfaces the **real board's stat tiles** (total allocated quota, latest
    execution price, trade volume, trade value, best bid / lowest offer).
  - Vietnam packs **rescaled** so total company allocations sum to ~**511,473,846 tCO2e**.
- **Key repo surfaces:**
  - `web/css/style.css` — `:root` palette tokens (retint target).
  - `web/game.html` — market ticker, compliance meter, stat tiles, badges.
  - `web/index.html` — scenario/lobby UI.
  - `web/js/` (number/price formatting in the JS that renders snapshots).
  - `engine/scenarios.py` — pack offset_price, penalty_rate, allocation_factors,
    company_library, abatement_catalog (reprice + rescale target).
  - `engine/constants.py` — `DEFAULT_OFFSET_PRICE`, `DEFAULT_PENALTY_RATE`, auction floor/ceiling.
  - `engine/engine.py` — price calc (lines ~361–398), trading/auction actions.

## Resolved Decisions
<!-- the grilled Q&A; each one keeps /plan's Grill Me empty -->
- **DEC-001:** Do both efforts in one body of work, **visual-led** — the retint is the
  headline; mechanics changes make the new look meaningful. — keeps the news tie-in front-and-center.
- **DEC-002:** **Accent-retint only**, not a full dark theme — keep current layout/structure,
  shift palette toward cyan/teal/green/red accents, apply monospace to numbers. — avoids the
  high-collision dark-canvas/sprite-contrast rework the explore agent flagged.
- **DEC-003:** Enter VN data by **repricing existing packs to VND** (not a separate pack /
  not an event). — single coherent economy; `vietnam_pilot` is already default.
- **DEC-004:** **Convert everything proportionally** — one FX factor scales penalties,
  capex/abatement costs, loans, and budgets together so existing balance is preserved.
- **DEC-005:** **Anchor the FX factor on `vietnam_pilot` → 136,000 VND/tCO2e** (factor ≈
  ×5,440 from the current 25). Other packs scale by the same factor and land above/below as
  realistic price variation. — hits the real headline number without flattening pack differences.
- **DEC-006:** **Add the missing board stat tiles** to the market screen (total allocated
  quota, latest price, trade volume, trade value, best bid, lowest offer). — mirrors the
  real exchange board's information layout.
- **DEC-007:** **Currency label = `đ` with `/tCO2e`** (e.g. `136.000 đ/tCO2e`), replacing
  `$`. — authentic to the board photo and article.
- **DEC-008:** **Vietnamese dot-grouping** for large numbers (`136.000`, `511.473.846`). —
  matches the board exactly. (Implementation must ensure parsing/storage stays numeric;
  formatting is display-only.)
- **DEC-009:** **Rescale the sim** so playable numbers match the national scale (not just a
  flavor stat). — user wants the magnitudes to feel real, not cosmetic.
- **DEC-010:** **Rescale scope = Vietnam packs only, sum-of-company-caps ≈ 511,473,846
  tCO2e**; California/EU jurisdictions keep their own realistic totals. Balance must be
  re-verified after. — targets the real figure precisely without making other jurisdictions arbitrary.

## Assumptions & Constraints
<!-- seeds /plan ## Assumptions and Constraints -->
- **ASM-001:** The retint reuses existing CSS tokens/classes (`--accent`, `--green`,
  `--red`, `.badge-*`, `.stat-value`, `--mono`); no new component framework introduced.
- **ASM-002:** The board's bid/offer tiles can be populated from existing instruments
  (OTC `propose_trade`, auction bids, forward contracts); if no live order book exists,
  best-bid/lowest-offer derive from current offers or are shown as "—" when empty.
- **ASM-003:** `vietnam_pilot` remains the default pack and the canonical 136,000 anchor.
- **CON-001:** **Two orthogonal scaling axes interact and must not be conflated.** FX
  reprice (×~5,440) applies to *per-tonne rates* and *cash amounts*; the volume rescale
  (to hit 511M) applies to *tonnage quantities* and to *cash that scales with company size*.
  Per-tonne fields (`offset_price`, `penalty_rate`, auction floor/ceiling) get **FX only**;
  tonnage fields (`baseline_emissions`, `abatement_amount`, allocations) get the **volume
  factor only**; lump-sum cash (`cash`, capex `cost`) gets **FX × volume**. /plan must lay
  out the per-field mapping explicitly.
- **CON-002:** Number formatting is display-layer only — engine/DB/JSON stay numeric to
  avoid breaking arithmetic and the deterministic engine.
- **CON-003:** Balance is currently hand-tuned (memory: `solo_standard` penalty raised to
  1000 for flattest win-rate; policy-stability cap-modifier neutral at 70). Reprice +
  rescale must preserve *ratios*; a regression pass on win-rate/balance is required.
- **CON-004:** Keep the light layout legible — retint accents must hold WCAG contrast on
  the cream/near-white panels (don't drop board-dark colors straight onto light surfaces).

## Approaches Considered
<!-- seeds /plan ## Risks and Alternatives -->
- **Chosen:** Visual-led accent-retint + full VND reprice (anchored to 136,000) + Vietnam-pack
  rescale to 511M + board stat tiles. — maximal news authenticity at moderate, well-scoped effort.
- **ALT-001:** Full dark trading-board theme — rejected (DEC-002); high collision with canvas
  sprites/haze and bevel system, large rework for little gameplay gain.
- **ALT-002:** Separate `vietnam_2025` scenario pack instead of repricing in place — rejected
  (DEC-003); user wants the whole economy in VND, not an opt-in.
- **ALT-003:** Show 511M as flavor-only headline without rescaling the sim — rejected
  (DEC-009); user wants real magnitudes in play.
- **ALT-004:** Uniform rescale factor across all packs — rejected (DEC-010); would make
  CA/EU totals arbitrary.

## Out of Scope
- Dark mode / theme toggle / canvas (isocity) re-theme.
- New trading instruments or a real continuous order book (reuse existing OTC/auction/forward).
- Re-tuning difficulty by hand beyond preserving existing ratios (no new balance design).
- Localization of UI text into Vietnamese (only currency symbol + number formatting change).
- Backend persistence/schema changes beyond what reprice/rescale of pack constants requires.

## Open Questions
<!-- the few that survived; seed /plan ## Grill Me. -->
1. **Q-001:** After reprice (×~5,440) + Vietnam rescale (sum→511M), what is the acceptance
   bar for "balance preserved"? (e.g., no strategy exceeds ~45% win rate, as in the prior
   `solo_standard` tuning.)
   - **Recommended default:** Reuse the existing balance bar — run the same win-rate/dominance
     check used when `solo_standard` penalty was set to 1000; flag any pack that drifts >5pp.
   - **Why this matters:** Determines whether a balance-regression phase is "verify only" or
     "verify + re-tune," and how much QA the plan budgets.
2. **Q-002:** Should the first-session facts (date 29/06/2026, 400 tCO2e first trade,
   54,000,000 VND value, lowest offer 135,000, listing status) appear as a one-time
   "opening session" reference on the board, or only the live/derived stats?
   - **Recommended default:** Show a static "opening session" reference strip (date + the
     real first-trade figures) on the Vietnam market screen for flavor; keep all other tiles
     live/derived from game state.
   - **Why this matters:** Affects how literally the board photo is reproduced vs. how much
     is driven by gameplay.

## Suggested Next Step
Run `/plan vietnam-exchange-retheme-reprice` to turn this into a multi-phase implementation plan.
