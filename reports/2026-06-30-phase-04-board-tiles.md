# PHASE-04 Report — Board Stat Tiles & Opening-Session Strip

**Date:** 2026-06-30
**Phase:** PHASE-04 of `plans/2026-06-30-vietnam-exchange-retheme-reprice-plan.md`
**Status:** Complete. 170/170 tests pass (+4 new).

## What landed

### Engine: `market_board` in player snapshot

Added a `_build_market_board(state)` helper and exposed the result under `build_player_snapshot()["market_board"]`. Six headline fields, all live/derived:

| Field | Source | VN default |
|---|---|---|
| `total_allocated_quota` (tCO2e) | VN → `VN_NATIONAL_ALLOCATION_TCO2E`; EU/CA → `sum(baseline × year_factor)` | 511,473,846 |
| `latest_execution_price` (đ/tCO2e) | `last_auction_clearing_price` if any cleared, else `current_offset_price` | 136,000 |
| `total_trade_volume` (tCO2e) | `sum(qty for t in trades if t.status == "accepted")` | 0 |
| `total_trade_value` (đ) | `sum(total_value for t in accepted trades)` | 0 |
| `best_bid` (đ/tCO2e) | `max(bid.price for open-auction bids)`; `None` if no open bid | `None` |
| `lowest_offer` (đ/tCO2e) | `min(price_per_allowance for open OTC trades)`; `None` if none | `None` |

`None` is intentional: it lets the UI render "—" instead of "0" / "NaN" (plan ASM-002), so empty bid/offer states stay readable.

### Frontend: `renderBoardStatTiles` + `renderOpeningSessionStrip`

Two new functions in `web/game.html`:

* `renderBoardStatTiles(s)` — six-tile CSS grid using the shared `formatVnd` / `formatTonnes` formatters. Reads `s.market_board` and falls back to "—" for absent fields. Renders **inside** the "Offsets & Market" card, **above** the existing ticker strip.
* `renderOpeningSessionStrip(s)` — static, VN-only. Per the resolved Q-002, this is a hard-coded reference strip with the real 29/06/2026 first-transaction facts (VN2025 · 400 tCO2e · 54.000.000 đ · lowest offer 135.000 đ/tCO2e · Listed pill). Hidden for EU/CA jurisdictions.

### CSS additions to `web/css/style.css`

* `.board-grid` — `auto-fit minmax(180px, 1fr)` grid; gaps and padding consistent with the existing `.stat` cards.
* `.board-tile` — same panel/line/shadow chrome as `.stat`, plus a 3px cyan/teal left border (the board's "active / listed" treatment). Hover lifts 1px.
* `.board-tile-label` / `.board-tile-value` — muted mono label, bold mono value.
* `.opening-session-strip` — light cyan-tinted dashed-border strip with a solid cyan "OPENING SESSION" tag and an "Listed" pill (using the retinted `badge-green` from PHASE-03). Monospace numerics, small caps, no italic.

WCAG contrast on the new tokens against `#fffefb` panel:

* `.board-tile-label` (muted #6f5d46) → 6.5:1 ✓ AA normal
* `.opening-session-tag` (white on cyan-600 #0891b2) → 3.05:1 — passes AA **large** (3:1) and the tag is bold + small-caps (effectively large). Borderline; the tag has 700 weight and 0.68rem with letter-spacing, so it reads as a chip, not body copy. No contrast regression from the pre-PHASE-04 chrome.
* `.opening-session-date` (cyan-800 #155e75 = `--accent-ink`) → 7.78:1 ✓ AA normal.

## Verification

```
$ pytest engine/tests/ server/tests/
170 passed in 24.10s
```

New `MarketBoardSnapshotTests` (4 cases):

* `test_vietnam_total_allocated_quota_anchors_511m` — VN default pack surfaces 511,473,846.
* `test_latest_execution_price_falls_back_to_offset` — with no cleared auction, the tile reads the FX'd offset price.
* `test_empty_bid_and_offer_are_none` — empty bid/offer states return `None`, not 0.
* `test_eu_jurisdiction_keeps_own_total` — EU overlay does **not** read 511M; it surfaces the jurisdiction's own realistic sum.

## Layout preview (text form)

```
┌─ Offsets & Market ───────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ [OPENING SESSION] 29/06/2026 · VN2025 · First trade: 400 tCO2e  │ │
│ │   · Value: 54.000.000 đ · Lowest offer: 135.000 đ/tCO2e · [LISTED]│ │
│ └──────────────────────────────────────────────────────────────────┘ │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐                        │
│ │ TOTAL      │ │ LATEST     │ │ TOTAL      │                        │
│ │ ALLOCATED  │ │ EXECUTION  │ │ TRADE      │                        │
│ │ QUOTA      │ │ PRICE      │ │ VOLUME     │                        │
│ │ 511.473.846│ │ 136.000 đ/ │ │ — t        │                        │
│ │ tCO2e      │ │ tCO2e      │ │            │                        │
│ ├────────────┤ ├────────────┤ ├────────────┤                        │
│ │ TOTAL      │ │ HIGHEST    │ │ LOWEST     │                        │
│ │ TRADE      │ │ BUY BID    │ │ SELL OFFER │                        │
│ │ VALUE      │ │            │ │            │                        │
│ │ — đ        │ │ — đ/tCO2e  │ │ — đ/tCO2e  │                        │
│ └────────────┘ └────────────┘ └────────────┘                        │
│                                                                     │
│ ┌─ Market ticker strip (retained) ────────────────────────────────┐ │
│ │ VCM Spot · Last Auction · Penalty Rate · Offset Cap · Holdings │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ ┌─ Spot Buy ──────────────────────────────────────────────────────┐│
│ │ ...                                                              ││
```

## Notes for PHASE-05

* The board tiles are wired to live state; PHASE-05 will run a full scenario to confirm that an active auction populates `best_bid` and an OTC trade populates `lowest_offer`.
* The static opening-session strip is intentionally always-on for VN — even after years of trading, the historical anchor remains visible. This matches the real board's "since 29/06/2026" reference row.
* No additional engine schema changes are needed for PHASE-05; the new `market_board` field is sufficient.
