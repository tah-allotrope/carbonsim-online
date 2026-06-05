# Climate Mayor Design Language

## Visual Direction

**Theme:** Dark cyberpunk-inflected dashboard. Deep blacks with cyan/green neon accents. The aesthetic communicates "command center for carbon compliance" — serious but not austere, with game-feel moments (particles, glows, animated transitions) that reward player action.

**Principles:**
1. **Clarity over decoration** — every visual element serves a compliance or game-state purpose
2. **Reactive feedback** — the UI responds visibly to every player decision (glow pulses, counter animations, toast notifications)
3. **Consistent tokens** — one palette, one spacing scale, one type system across all screens
4. **Performance-first** — no heavy frameworks, canvas for the signature visual, CSS for everything else

## Color Tokens

| Token | Value | Usage |
|---|---|---|
| `--bg` | `#0d0d0d` | Page background |
| `--bg-soft` | `#111111` | Modal/overlay background |
| `--panel` | `rgba(13,13,13,0.88)` | Card/panel background |
| `--line` | `rgba(0,245,255,0.26)` | Borders, dividers |
| `--text` | `#e9f6ff` | Primary text |
| `--muted` | `#8ea3ad` | Secondary/label text |
| `--accent` | `#00f5ff` | Primary accent (cyan) — interactive elements, phase badges |
| `--green` | `#39ff14` | Positive — compliant, success, abatement active |
| `--red` | `#ff4444` | Negative — shortfall, penalty, error |
| `--orange` | `#ffaa00` | Warning — pending, approaching cap |
| `--glow` | `0 0 18px rgba(0,245,255,0.42)` | Accent glow shadow |

### Semantic Color Rules
- **Compliance gap <= 0** → `--green` (compliant)
- **Compliance gap > 0** → `--red` (shortfall)
- **Cash always** → `--accent` (neutral positive)
- **Penalties** → `--red`
- **Phase badge** → `--accent` (decision_window), `--green` (complete), `--orange` (paused)

## Typography

| Level | Family | Size | Weight | Usage |
|---|---|---|---|---|
| Display | `var(--font)` (Segoe UI) | `clamp(1.6rem, 3vw, 2.4rem)` | 700 | Page titles |
| Card title | `var(--mono)` | 0.85rem | 400 | Section headers (uppercase, tracked) |
| Stat value | `var(--mono)` | 1.3rem | 700 | Key metrics |
| Stat label | `var(--mono)` | 0.72rem | 400 | Metric labels (uppercase) |
| Body | `var(--font)` | 0.9rem | 400 | Prose, descriptions |
| Badge | `var(--mono)` | 0.75rem | 400 | Status pills (uppercase) |

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
- Background: `var(--panel)` with `var(--line)` border
- Border-radius: `var(--radius)` (14px)
- Hover: border brightens, subtle lift
- Title: `var(--mono)` uppercase with accent color

### Button
- **Default**: Transparent bg, `var(--line)` border, hover glow
- **Primary**: Accent bg, accent border, white text
- **Danger**: Red border, red-tinted bg
- **Disabled**: 0.3 opacity, no interactions
- All buttons: 8px radius, cubic-bezier transitions

### Badge
- Pill shape (999px radius)
- Variants: `badge-green`, `badge-red`, `badge-orange`, `badge-blue`
- Uppercase mono text

### Stat
- Label/value pair
- Value uses mono font, 1.3rem
- Color variants: `.accent`, `.green`, `.red`

### Input / Select
- Dark bg, subtle border
- Focus: accent border + glow shadow
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
- Fixed bottom-right
- Slide-in animation
- Variants: success (green), error (red), warning (orange), info (cyan)
- Auto-dismiss with progress bar

## Signature Visual: City Skyline

The city skyline is the primary signature visual. It renders as a canvas element above the game dashboard.

### Behavior
- **Buildings** represent companies in the market. Player's company is highlighted with accent glow.
- **Sky color** shifts based on compliance: clear blue (compliant) → hazy orange (approaching gap) → red-brown (shortfall).
- **Smog particles** emit from building tops proportional to projected emissions. More emissions = denser smog.
- **Year transitions** trigger a dawn/dusk cycle animation.
- **Abatement activation** causes a building's smoke to visibly reduce.
- **Offset purchase** shows a brief green sparkle effect.

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

- All interactive elements have focus states (accent border + glow)
- Color is never the sole indicator — badges include text labels
- `prefers-reduced-motion` disables animations, background gradients, and particle effects
- Skyline canvas has `aria-hidden="true"` (decorative)
- Minimum contrast ratio: 4.5:1 for body text, 3:1 for large text
