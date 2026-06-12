# CarbonSim Online Design Language

## Visual Direction

**Theme:** Retro isometric tycoon. Warm parchment tones, chunky beveled chrome, and a pixel display font evoke classic management sims (SimCity 2000 / Theme Hospital register) while keeping carbon compliance data legible. The aesthetic is playful and readable rather than cinematic.

**Principles:**
1. **Clarity over decoration** — every visual element serves a compliance or game-state purpose
2. **Chunky, tactile chrome** — raised panels and inset buttons make the UI feel like a tycoon interface
3. **Consistent tokens** — one palette, one spacing scale, one type system across all screens
4. **Performance-first** — no heavy frameworks, canvas for the signature visual, CSS for everything else

## Color Tokens

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#f7f1e7` | Page background (parchment) |
| `--bg-soft` | `#efe4d0` | Modal/overlay background, softer parchment |
| `--panel` | `#fffdf9` | Card/panel background (off-white) |
| `--line` | `rgba(92, 77, 60, 0.28)` | Borders, dividers |
| `--text` | `#1f1912` | Primary text (dark ink) |
| `--muted` | `#6b5e4f` | Secondary/label text |
| `--accent` | `#3b6f76` | Primary accent (teal) — interactive elements, phase badges |
| `--green` | `#5a8f4e` | Positive — compliant, success, abatement active |
| `--red` | `#b54a3f` | Negative — shortfall, penalty, error |
| `--orange` | `#d4883a` | Warning — pending, approaching cap |
| `--bevel-light` | `#fff8e7` | Raised edge highlight |
| `--bevel-dark` | `#8b7355` | Recessed edge shadow |
| `--bevel-shadow` | `#4a3b2d` | Drop-shadow for raised chrome |

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

Press Start 2P is restricted to display type; dense stats and body text remain on the readable sans/mono stack.

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
- Background: `var(--panel)` with `var(--bevel-dark)` border
- Border-radius: `var(--radius)` (8px)
- Box-shadow: inset `var(--bevel-light)` top-left, inset `var(--bevel-dark)` bottom-right, offset `var(--bevel-shadow)`
- Hover: translateY(-2px), shadow deepens
- Title: `var(--mono)` uppercase with accent color

### Button
- **Default**: `var(--panel)` bg, `var(--bevel-dark)` border, raised bevel shadow
- **Primary**: `var(--accent)` bg, white text
- **Danger**: `var(--red)` bg, white text
- **Disabled**: 0.45 opacity, grayscale, no transform
- **Active/pressed**: reverse inset shadows, translateY(2px)
- All buttons: 8px radius, short tactile transitions

### Badge
- Pill shape (999px radius)
- Solid semantic background colors with subtle bevel inset
- Variants: `badge-green`, `badge-red`, `badge-orange`, `badge-blue`
- White or dark ink text for contrast

### Stat
- Label/value pair inside a beveled panel
- Value uses mono font, 1.3rem
- Color variants: `.accent`, `.green`, `.red`

### Input / Select
- `var(--bg-soft)` background
- Inset bevel shadow
- Focus: accent border + inset accent ring
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
- Beveled panel with semantic border
- Slide-in animation
- Variants: success (green), error (red), warning (orange), info (accent)
- Auto-dismiss with progress bar

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

- All interactive elements have visible `:focus-visible` states
- Color is never the sole indicator — badges include text labels
- `prefers-reduced-motion` disables animations, background gradients, and particle effects
- Canvas has `aria-hidden="true"` (decorative)
- Minimum contrast ratio: 4.5:1 for body text, 3:1 for large text
- Press Start 2P is used only for large display text to preserve readability
