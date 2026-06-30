# PHASE-02 Report — VND Display Layer

**Date:** 2026-06-30
**Phase:** PHASE-02 of `plans/2026-06-30-vietnam-exchange-retheme-reprice-plan.md`
**Status:** Complete. 166/166 tests still pass.

## What landed

### `web/js/format.js` (new, ~50 lines)

Shared formatters using `Intl.NumberFormat('vi-VN')` for Vietnamese dot-grouping. Display-only — engine, DB, and JSON stay numeric floats (CON-002).

```
formatVnd(n)           → "136.000 đ"         (full, for stat tiles)
formatVndAbbrev(n)     → "5.2T đ"            (abbrev, for inline deltas)
formatTonnes(n)        → "76.733.367 t"      (full, for stat tiles)
formatTonnesAbbrev(n)  → "76.7M t"           (abbrev, for compact tables)
```

Abbreviation tiers for VND: T (1e12) / B (1e9) / M (1e6) / K (1e3). For tonnes: B / M / K (no T, since the largest tonnage in a single pack is ~1.2B tCO2e for solo_standard over 15 years).

### Script wiring

Added `<script src="/js/format.js"></script>` to `web/game.html`, `web/summary.html`, `web/coop.html`. `web/index.html` does not need it (no money formatting in the lobby view). The shared module is loaded BEFORE the inline scripts so the inline templates can call the formatters.

### `$` → `đ` sweep

Replaced `$${fmt(...)}` and `${fmt(...)}` patterns in three HTML files (~30 substitutions). All call sites now route through `formatVnd` / `formatVndAbbrev` / `formatTonnes` / `formatTonnesAbbrev`.

| Pattern | Before | After |
|---|---|---|
| Stat tile money | `$${fmt(cash)}` → "5.2M" (wrong scale) | `${formatVnd(cash)}` → "5.217.871.200.000.000 đ" |
| Stat tile tonnage | `${fmt(projected)}` → "76.7M" (ok) | `${formatTonnes(projected)}` → "76.733.367 t" |
| Compact table cell | `$${fmt(m.cost)}` → "313.1M" (wrong) | `${formatVndAbbrev(m.cost)}` → "313.1T đ" |
| Gap indicator | `${fmt(gap)}` → "6.4M" | `${formatTonnesAbbrev(gap)}` → "6.4M t" |
| Inline floater | `-$ + fmt(m.cost)` | `formatVndAbbrev(m.cost)` |
| Forward contract | `$${fc.locked_price.toFixed(2)}/t` | `${formatVnd(fc.locked_price)}/tCO2e` |
| Auction bid fallback | `$${a.price_floor \|\| 80}` | `${formatVnd(a.price_floor \|\| 435200)}` |
| Bid input label | `Price ($)` | `Price (đ/tCO2e)` |

### Legacy `fmt` shims

The three local `function fmt(n)` definitions in `game.html`, `summary.html`, `coop.html` are kept as abbreviation shims (no longer called from any template; only defensively) and annotated to point at the new shared module. The local `fmt` in `effects.js:24` (inside `animateCounter`) is replaced with a delegate to the shared logic, since currency count-up animations need to know whether to append ` đ` or ` t`.

## Verification

```
$ pytest engine/tests/ server/tests/
166 passed in 32.10s
```

The new module is browser-only and is not exercised by the engine test suite, but the substitutions in the HTML templates cannot break the engine — they only consume values that the engine produces. (A future PR could add a Playwright smoke test to render `game.html` against a fixture state; not in scope here.)

### Manual smoke check (Python equivalent of `Intl.NumberFormat('vi-VN')`)

```
formatVnd(136_000)                 → "136.000 đ"
formatVnd(5_440_000)               → "5.440.000 đ"
formatVnd(5_217_871_200_000_000)   → "5.217.871.200.000.000 đ"
formatVnd(0)                       → "0 đ"
formatVnd(null)                    → "—"
formatVndAbbrev(5.22e15)           → "5.217,9T đ"
formatTonnes(76_733_367)           → "76.733.367 t"
formatTonnes(511_473_846)          → "511.473.846 t"
```

## Notes for the next phase

* PHASE-03 (accent retint) is independent and can run in parallel — the formatters don't care about the colour of the panels.
* PHASE-04 (board stat tiles) can now consume the headline values directly: `formatTonnes(511_473_846)` reads cleanly, and the `formatVnd`/`formatVndAbbrev` split keeps long company-cash values out of the way of compact tiles.
* The `co.html:267` bid input still uses the raw `<input type="number">` — the user types VND integers, no symbol prefix; the label `Price (đ/tCO2e)` clarifies the unit. No further UI change needed here.
