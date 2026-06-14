# CarbonSim Online Design Language

## Visual Direction

**Theme:** Bright Kairosoft-style pixel-art tycoon. Cheerful saturated colors, rounded gradient panels, soft drop shadows, and pill buttons evoke Kairosoft's cute management sims (Game Dev Story / Venture Towns register) while keeping carbon compliance data legible. The aesthetic is friendly and lively rather than austere. (See `research/2026-06-14_kairosoft-visual-style.md`.)

**Principles:**
1. **Clarity over decoration** — every visual element serves a compliance or game-state purpose
2. **Cheerful, rounded, tactile chrome** — rounded gradient panels and pressable pill buttons make the UI feel like a cute tycoon
3. **Consistent tokens** — one palette, one spacing scale, one type system across all screens
4. **Performance-first** — no heavy frameworks, canvas for the signature visual, CSS for everything else

## Color Tokens

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#fdf6e9` | Page background (bright warm cream) |
| `--bg-soft` | `#f4e8d2` | Softer cream (HUD strips) |
| `--panel` | `#fffefb` | Card/panel base (near-white) |
| `--line` | `rgba(74, 59, 45, 0.22)` | Borders, dividers |
| `--text` | `#2a2018` | Primary text (warm near-black) |
| `--muted` | `#6f5d46` | Secondary/label text |
| `--accent` | `#1f93c7` | Primary accent (bright sky azure) — interactive elements, phase badges |
| `--accent-bright` | `#2bb0e0` | Lighter azure for gradient tops/highlights |
| `--green` | `#4caf50` | Positive — compliant, success, abatement active |
| `--red` | `#e2553f` | Negative — shortfall, penalty, error |
| `--orange` | `#f5a623` | Warning — pending, approaching cap (sunny) |
| `--bevel-dark` | `#caa96c` | Pressable button bottom-edge color |
| `--bevel-light` / `--bevel-shadow` | `#fffefb` / `#a07d44` | Legacy bevel tokens (retained for compatibility) |

### Gradient & Radius Tokens
| Token | Value | Usage |
|---|---|---|
| `--grad-panel` | `linear-gradient(180deg,#fffefb,#f7eed9)` | Cards, buttons (default), modals, event cards |
| `--grad-accent` | `linear-gradient(180deg,--accent-bright,--accent)` | Primary buttons, blue badges, bubbles |
| `--grad-green` / `--grad-red` | green/red top→base gradients | Semantic badges/buttons/bubbles |
| `--radius` | `8px` | Inputs, stats, small chrome |
| `--radius-lg` | `16px` | Rounded cards, modals, event cards |

### Semantic Color Rules
- **Compliance gap <= 0** → `--green` (compliant)
- **Compliance gap > 0** → `--red` (shortfall)
- **Cash always** → `--accent` (neutral positive)
- **Penalties** → `--red`
- **Phase badge** → `--accent` (decision_window), `--green` (complete), `--orange` (paused)

## Typography

| Level | Family | Size | Weight | Usage |
|---|---|---|---|---|
| Display | `var(--font-display)` (Press Start 2P) | `clamp(1.2rem, 3vw, 2rem)` | 400 | Page titles, brand, major headings |
| Card title | `var(--mono)` | 0.85rem | 400 | Section headers (uppercase, tracked) |
| Stat value | `var(--mono)` | 1.3rem | 700 | Key metrics |
| Stat label | `var(--mono)` | 0.72rem | 400 | Metric labels (uppercase) |
| Body | `var(--font)` (Segoe UI) | 0.9rem | 400 | Prose, descriptions, dense stats |
| Badge | `var(--mono)` | 0.75rem | 400 | Status pills (uppercase) |

Press Start 2P is restricted to display type; dense stats and body text remain on the readable sans/mono stack. *Follow-up:* swapping the display face to a rounded-pixel OFL font (more Kairosoft-cute) is a drop-in change — add the `.ttf` + `@font-face`, record in `ATTRIBUTIONS.md`, and point `--font-display` at it.

## Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `--space-xs` | 4px | Inline gaps |
| `--space-sm` | 8px | Button gaps, tight padding |
| `--space-md` | 12px | Card inner padding |
| `--space-lg` | 16px | Grid gaps, card margins |
| `--space-xl` | 20px | Card padding |
| `--space-2xl` | 24px | Section gaps |

## Component Library

### Card
- Background: `var(--grad-panel)`, `var(--line)` border
- Border-radius: `var(--radius-lg)` (16px)
- Box-shadow: soft `0 4px 14px rgba(74,59,45,.12)`; hover deepens + translateY(-2px)
- Title: `var(--mono)` uppercase with accent color

### Button
- **Pill shape** (999px radius), `var(--grad-panel)` fill, soft shadow + colored bottom edge (`--bevel-dark`)
- **Primary**: `var(--grad-accent)` + white text + azure bottom edge/shadow
- **Danger**: `var(--grad-red)` + white text
- **Active/pressed**: translateY(2px), bottom edge collapses
- **Disabled**: 0.5 opacity, grayscale, no transform
- Short tactile transitions + subtle hover brightness

### Badge
- Pill shape (999px radius), **gradient** semantic fills, soft 1px shadow
- Variants: `badge-green` (dark ink), `badge-red`/`badge-blue` (white), `badge-orange` (dark ink)

### Bubble (notification / speech)
- Pill with a small bottom tail (`.bubble::after`)
- Variants: `bubble-accent`, `bubble-green`, `bubble-red`
- Used by in-game floating feedback (Sprint 4)

### Stat
- Label/value pair in a soft-shadow panel (`var(--radius)`)
- Value uses mono font, 1.3rem; color variants `.accent`/`.green`/`.red`

### Input / Select
- White background, `var(--line)` border, soft inner shadow
- Focus: accent border + 3px accent focus ring
- Full width by default

### Table
- Full width, border-collapse
- Header: accent color, uppercase mono
- Row hover: subtle accent tint

### Progress Bar
- 6px height, rounded
- Fill: gradient from accent to green
- Smooth width transitions

### Toast
- Rounded panel with semantic accent
- Slide-in animation
- Variants: success (green), error (red), warning (orange), info (accent)
- Auto-dismiss with progress bar

## Building Sprite Spec (for Sprint 2)

Author Kairosoft-*inspired* original (or CC0/CC-BY) sprites to this spec so the set stays coherent — never reuse Kairosoft's actual assets.

| Property | Spec |
|---|---|
| Canvas | 64×64 PNG, transparent background |
| Footprint | 64×32 isometric diamond (matches `isocity.js` `TILE_W`/`TILE_H`); buildings may rise above, drawn with a vertical offset |
| Palette | Sprint-1 token palette (cream/azure/green/red/orange); saturated, cheerful |
| Outline | 1px dark warm outline (≈ `--bevel-shadow`) for the cute Kairosoft read |
| Light | Top-left light source; soft 1–2 step shading |
| Variety | ≥4 sector types (thermal, steel/cement, generation, generic industry) × dirty/clean + ≥1 upgrade tier; plus decorations (trees/roads) |
| Naming | `bldg_<sector>_<state>` (e.g. `bldg_thermal_dirty`) registered in `web/assets/manifest.json` |

## Signature Visual: Isometric City

The isometric pixel-art city is the primary signature visual. It renders as a canvas element above the game dashboard and deterministically maps engine state to city geometry. Implementation details live in Sprint 3 (`plans/2026-06-13-isometric-renderer-plan.md`).

### Behavior
- **Plots** represent companies in the market. The local player's plot carries a gold marker.
- **Building sprite** swaps from dirty to clean when abatement is active.
- **Smog overlay** density scales with projected emissions.
- **Plot tint** shifts to a warning color when compliance gap is positive.
- **Year transitions** trigger a dawn/dusk cycle animation.

### Technical
- Canvas-based, `requestAnimationFrame` loop
- Throttled to 30fps when tab not focused
- Respects `prefers-reduced-motion`
- Data source: engine snapshot fields (`projected_emissions`, `allowances`, `compliance_gap`, `abatement_menu`)

## Responsive Layout

| Breakpoint | Behavior |
|---|---|
| > 1100px | Full 2-column grid, max-width container |
| 768-1100px | 2-column grid maintained, tighter padding |
| < 768px | Single column, stacked header |

## Accessibility

Focus/motion/canvas behavior carried over from Sprint 5 (still in effect). **Color contrast for the new Kairosoft palette was sanity-checked but a full axe/Lighthouse re-verification is pending** (Sprint 1 was a style change; numbers below are approximate and should be re-measured).

- **Focus:** All interactive elements have a visible `:focus-visible` outline (2px solid `--accent`, 2px offset); inputs additionally get a 3px accent focus ring. Covered by a global rule plus component rules.
- **Motion:** `prefers-reduced-motion: reduce` disables animations, stops the isometric city RAF loop, hides DOM particles, and renders a single static city frame.
- **Canvas:** The isometric canvas is `aria-hidden="true"` and purely decorative; the same state is exposed as text stats, badges, and leaderboard rows.
- **Color & contrast (approximate, re-verify):**
  - Body text (`--text #2a2018` on `--bg #fdf6e9` / `--panel`): very high (dark-on-cream).
  - White text on `--accent #1f93c7` (primary buttons): chosen to meet the large/bold-text threshold (≈3:1+); confirm for 0.9rem bold button labels.
  - Green/orange badges use **dark ink** on their gradient fills to avoid white-on-bright failures; red/blue badges use white.
- **Minimum contrast target:** 4.5:1 body text, 3:1 large/bold UI text.
- **Typography:** Press Start 2P used only for display text to preserve readability (rounded-pixel swap is a follow-up).
- **Open item:** run a full axe/Lighthouse pass on the new palette (tracked for the Sprint-4 perf/a11y phase).
