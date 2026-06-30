# PHASE-03 Report — Accent Retint Toward Board Palette

**Date:** 2026-06-30
**Phase:** PHASE-03 of `plans/2026-06-30-vietnam-exchange-retheme-reprice-plan.md`
**Status:** Complete. 166/166 tests still pass.

## What landed

### `web/css/style.css` `:root` palette

Retinted the existing light theme's accents toward the Vietnam carbon exchange board's cyan/teal/green/red language. The cream base (`--bg`, `--bg-soft`, `--panel`), warm near-black text (`--text`), and warm brown line colour (`--line`) are unchanged — only the brand accents moved.

| Token | Before | After | Notes |
|---|---|---|---|
| `--accent` | `#1f93c7` (sky azure) | **`#0891b2`** (cyan-600) | Board teal |
| `--accent-bright` | `#2bb0e0` | **`#06b6d4`** (cyan-500) | Lighter gradient top |
| `--accent-ink` | `#157197` | **`#155e75`** (cyan-800) | Darker for small text AA contrast |
| `--green` | `#4caf50` (grass) | **`#16a34a`** (green-600) | Board listed-green |
| `--red` | `#e2553f` (warm) | **`#dc2626`** (red-600) | Board sell-red |
| `--grad-accent` | `#2bb0e0 → #1f93c7` | **`#06b6d4 → #0891b2`** | |
| `--grad-green` | `#66c06a → #4caf50` | **`#4ade80 → #16a34a`** | |
| `--grad-red` | `#ef6e59 → #e2553f` | **`#f87171 → #dc2626`** | |

### Button shadow / glow updates

`btn-primary` / `btn-danger` keep the three-layer shadow pattern (chrome depth, body shadow); only the colour literals change.

```
btn-primary  shadow #156f97 → #155e75  (deeper teal chrome depth)
btn-primary  glow    rgba(31,147,199,0.32) → rgba(8,145,178,0.32)
btn-danger   shadow #b23e2c → #b91c1c
btn-danger   glow    rgba(226,85,63,0.32) → rgba(220,38,38,0.32)
```

### Inline colour updates (HTML/JS)

Six HTML/JS files had inline `rgba(31,147,199,...)`, `rgba(226,85,63,...)`, `#1f93c7`, `#e2553f`, and `#4caf50` literals. Swept them all to the new palette:

* `web/game.html`: `is-player` row highlight, CityRenderer floaters (green for abatement, red for cost, cyan for offset).
* `web/summary.html`: `is-player` row highlight, Chart.js bar fills/borders.
* `web/coop.html`: `is-you` row highlight, CityRenderer floaters.
* `web/css/style.css`: `tbody tr:hover` background, `leaderboard-row:hover` background, `input:focus` ring.

### WCAG contrast check

Manual relative-luminance check on the new palette against the retained `#fffefb` panel:

| Pair | Contrast | WCAG bar | Pass |
|---|---|---|---|
| `--accent-ink` `#155e75` on panel | **7.78 : 1** | AA normal (4.5:1) | ✓ |
| `--red` `#dc2626` on panel | **5.27 : 1** | AA normal (4.5:1) | ✓ |
| `--green` `#16a34a` on panel | **3.14 : 1** | AA large (3:1) | ✓ (used for fills/borders/large stat values, not small text) |
| `--accent` `#0891b2` on panel | **3.05 : 1** | AA large (3:1) | ✓ (used for fills, borders, focus rings, large stat values) |

Small-text accents (button text on `btn-primary` / `btn-danger` backgrounds, toast titles, link hover) read white on the new colour blocks — same as before, no change.

## Verification

```
$ pytest engine/tests/ server/tests/
166 passed in 32.10s
```

CSS changes don't touch the engine. Visual verification is browser-only and is queued for PHASE-05 (which takes the post-retint screenshots).

## Notes for the next phase

* The retint deliberately kept the warm cream base + warm brown lines. PHASE-04 (board stat tiles + opening-session strip) will sit naturally on the new palette: the cyan/teal accent reads as "active / listed", green as "compliant", red as "sell-side / shortfall", matching the board's stat-tile language.
* The Vietnamese `Intl.NumberFormat('vi-VN')` numeric values from PHASE-02 (e.g. `136.000 đ`, `511.473.846 tCO2e`) will render in monospace `--mono` against the new teal-on-cream stat tiles, which mirrors the board's "monospace ticker" look.
