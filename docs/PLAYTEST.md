# Solo Playtest Walkthrough

A step-by-step follow-along for verifying that solo play behaves correctly.

## Launch

```bash
pip install -r requirements.txt
uvicorn server.main:create_app --factory --port 8000
```

Open **http://localhost:8000**.

## Start

On the menu: enter a name, tick **"Start with the guided 3-year tutorial"**, click **Start Game**.

## Follow-along (check each "Expect")

| # | Do | Expect |
|---|----|--------|
| 1 | Land in the game | Phase badge **Decisions**, **Year 1/5**, Cash **$900.0K**, Allowances **91.8**, Emissions **90.0**, gap **−1.8 (Compliant)**, event card *"Welcome to Climate Mayor"* |
| 2 | Resolve the event card | Card clears; any stated effect applies |
| 3 | Abatement Menu → **Activate** "Boiler efficiency tune-up" (−9t, $30K, immediate) | Cash → **$870.0K**, Emissions → **81.0**, row flips to **Active**, the city building visibly de-smogs |
| 4 | Offsets → enter **5** → **Buy Offsets** | Cash → **~$869.9K** (−$125 = 5×$25), Holdings **5 t** |
| 5 | Click **Advance Year** | **Year 2/5**, new Decisions window, new tutorial card, allowances tighten (cap declines) |
| 6 | Repeat 3–5 each year | Company Standings (bots) update each year |
| 7 | Advance through Year 5 | **🏆 Game Completed** → "View Final Grade Summary" |

If any *Expect* doesn't match, that's a bug to report.

## How the solo turn loop works

Solo is **turn-based**. Each year the game rests in the **decision window**, where your
Activate / Buy Offsets actions apply. **Advance Year** ends the turn: bots act, the year is
closed and scored, and the next year's decision window opens. The game only advances when you
choose to. (The shared engine's timed phase model is used for multiplayer co-op, not solo.)

## Core rules recap

- **Goal:** keep projected emissions under your (declining) allowance each year, or pay
  penalties (~$200/t). Survive all years with the best compliance and cash.
- **Abatement:** permanent emission cuts; *immediate* measures apply this year, *next_year*
  measures apply from the following year. Costs cash now.
- **Offsets:** ~$25/t but usable only up to **10% of emissions** — good for small gaps.
- **Difficulty:** Easy 20y / Standard 15y / Hard 10y (steeper cap decline, higher penalties).
