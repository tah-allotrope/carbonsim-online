---
title: "Carbon Crunch Daily — Multiphase Implementation Plan"
date: "2026-04-29"
status: "draft"
request: "Take the Carbon Crunch Daily idea from the game-ification research brief and turn it into a concrete multiphase implementation plan."
plan_type: "multi-phase"
research_inputs:
  - "research/2026-04-26_carbon-game-ideas.md"
---

# Plan: Carbon Crunch Daily

## Objective

Build a Wordle-style daily 5-minute compliance puzzle that turns the existing CarbonSim engine into a solo, shareable, low-commitment experience. The puzzle should be solvable in under 5 minutes, produce a shareable score card, and run on a deterministic daily seed so every player worldwide sees the same puzzle. This expands CarbonSim’s reach from facilitated workshops to mass casual engagement.

## Context Snapshot

- **Current state:** The repo contains a 2,274-line pure-Python compliance engine (`platform/carbonsim_phase12/engine.py`) with no oTree imports. It already supports deterministic state evolution, abatement menus, offset caps, banking, penalties, and bot heuristics. The engine is exercised by 92 unit tests independently of oTree.
- **Desired state:** A daily-puzzle web app (static or thin-backend) that reuses the engine to generate a single-year compliance scenario, accepts player decisions, computes total cost, compares against an optimal oracle, and renders a shareable emoji-grid score card.
- **Key repo surfaces:**
  - `platform/carbonsim_phase12/engine.py` — compliance math, scenario packs, bot strategies
  - `platform/tests/test_engine.py` — deterministic fixtures and scenario tests
  - `platform/carbonsim_phase12/__init__.py` — oTree live pages (not reused for this idea)
  - `SCENARIO_PACKS` in `engine.py` — parameter sets that can be sampled for daily puzzles
- **Out of scope:** Multiplayer synchronization, facilitator controls, continuous order books, session replay, workshop analytics, oTree integration. This is intentionally a separate product surface.

## Research Inputs

- `research/2026-04-26_carbon-game-ideas.md` — Defines Idea 3 (Carbon Crunch Daily), its audience (mass casual + policy makers), core loop, reuse story, and recommended 5-phase shape. Also flags the need for an explicit measurement plan (engagement minutes, share rate, learning gains).
- `platform/carbonsim_phase12/engine.py` — Verified pure-Python, deterministic, seedable. The action space for a single company in one year is small enough to brute-force or to search with bot heuristics, which makes the optimal oracle feasible.

## Assumptions and Constraints

- **ASM-001:** The daily puzzle will use a *single-year, single-company* subset of the engine to keep the action space small and the solve time under 5 minutes.
- **ASM-002:** The engine’s deterministic behavior (verified by tests) means a daily integer seed can reproducibly generate the same puzzle parameters for all players.
- **ASM-003:** A shareable score card can be rendered as an emoji grid + cost spread (no image generation required for MVP).
- **CON-001:** The puzzle must work without authentication for the lowest friction on-ramp; a leaderboard therefore needs only a lightweight nickname + score submission, not full user accounts.
- **CON-002:** Hosting must stay within the project’s low-cost deployment posture (static site preferred, thin serverless backend acceptable).
- **DEC-001:** The puzzle frontend will be built as a new surface outside oTree, because oTree’s session model is the wrong substrate for daily stateless puzzles.

## Phase Summary

| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Extract engine to standalone package and build puzzle generator | None | `carbonsim-engine` package, daily puzzle generator with difficulty bounds |
| PHASE-02 | Build optimal-solution oracle | PHASE-01 | Optimal cost solver, correctness tests against brute force |
| PHASE-03 | Build static puzzle frontend with decision UI and share card | PHASE-01 | Deployable static site, decision form, results screen, emoji share card |
| PHASE-04 | Add daily seed pipeline and optional leaderboard | PHASE-02, PHASE-03 | Daily seed cron/API, score submission endpoint, leaderboard view |
| PHASE-05 | Growth experiments and distribution channels | PHASE-04 | Discord bot, daily email, embedded widget, analytics instrumentation |

## Detailed Phases

### PHASE-01 — Engine Extraction and Puzzle Generator

**Goal**
Make the compliance engine importable outside oTree and build a deterministic daily puzzle generator that produces solvable, non-trivial single-year scenarios.

**Tasks**
- [ ] TASK-01-01: Extract `engine.py` into a standalone Python package (`carbonsim-engine/`) with its own `pyproject.toml`, removing any implicit dependencies on the oTree app directory.
- [ ] TASK-01-02: Create `puzzle_generator.py` that accepts a daily integer seed, uses `random.Random(seed)` to sample from the existing `SCENARIO_PACKS` parameter distributions, and returns a single-company, single-year puzzle state.
- [ ] TASK-01-03: Define puzzle difficulty calibration: easy (abatement covers >70% of gap), medium (abatement + offsets within cap covers gap), hard (requires careful abatement + offset + trade decisions). Ensure every generated puzzle is solvable with zero penalties.
- [ ] TASK-01-04: Write unit tests for the generator: 100 consecutive seeds produce solvable puzzles; no puzzle is trivially solvable by abatement alone (unless difficulty = easy).
- [ ] TASK-01-05: Add a CLI entrypoint `python -m carbonsim_engine.generate_puzzle --seed 20260429` that prints the puzzle JSON.

**Files / Surfaces**
- `carbonsim-engine/pyproject.toml` — new standalone package
- `carbonsim-engine/carbonsim_engine/engine.py` — extracted engine (or symlink/copy)
- `carbonsim-engine/carbonsim_engine/puzzle_generator.py` — new generator module
- `carbonsim-engine/tests/test_puzzle_generator.py` — generator tests

**Dependencies**
- None

**Exit Criteria**
- [ ] `pip install -e carbonsim-engine/` succeeds in a clean venv.
- [ ] Generator produces a deterministic puzzle for any integer seed.
- [ ] 100-seed test suite passes with 100% solvability and appropriate difficulty spread.

**Phase Risks**
- **RISK-01-01:** Extracting the engine may reveal hidden oTree or Django dependencies not caught by grep. Mitigation: run engine tests in the clean venv immediately after extraction.

### PHASE-02 — Optimal-Solution Oracle

**Goal**
Compute the lowest-total-cost solution for any generated puzzle so players can be scored against a credible optimal baseline.

**Tasks**
- [ ] TASK-02-01: Implement `solve_puzzle(state) -> dict` that searches the action space for a single company in one year. Actions: activate zero or more abatement measures, buy offsets up to the cap, participate in the auction (simplified to a single uniform-price purchase), and optionally accept one bilateral trade at a fixed market price.
- [ ] TASK-02-02: Because the single-year action space is small (< 20 discrete actions), write a brute-force solver that enumerates all feasible action combinations, runs them through the engine’s year-end surrender logic, and returns the minimum total cost (abatement + offsets + auction + penalty).
- [ ] TASK-02-03: Optimize the solver with pruning: discard action sets that exceed cash, exceed offset cap, or are dominated by cheaper action sets with better abatement.
- [ ] TASK-02-04: Add correctness tests that compare the brute-force oracle against the existing bot heuristics (`run_bot_turns`) on the same puzzle; the oracle should always score equal or better.
- [ ] TASK-02-05: Expose a CLI `python -m carbonsim_engine.solve_puzzle --seed 20260429` that prints the optimal cost and action list.

**Files / Surfaces**
- `carbonsim-engine/carbonsim_engine/puzzle_solver.py` — new solver module
- `carbonsim-engine/tests/test_puzzle_solver.py` — solver correctness and performance tests

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] Solver returns the provably optimal cost for 100 sample seeds in under 1 second each.
- [ ] Solver never scores worse than the aggressive bot strategy.
- [ ] Solver handles edge cases: zero abatement, zero offsets, max offset cap, banked allowances from previous year (if we allow multi-year continuity later).

**Phase Risks**
- **RISK-02-01:** If we later expand to multi-year daily puzzles, the action space explodes and brute force becomes infeasible. Mitigation: the solver is already modular; we can swap in a heuristic search or MILP formulation without changing the frontend contract.

### PHASE-03 — Puzzle Frontend and Share Card

**Goal**
Build a lightweight, mobile-friendly web UI where players open the day’s puzzle, make decisions, submit, and receive a shareable score card.

**Tasks**
- [ ] TASK-03-01: Choose and scaffold the frontend stack. Recommended: Astro or Next.js static export, because it produces deployable HTML/JS/CSS with no runtime server. Host on Vercel, Cloudflare Pages, or GitHub Pages.
- [ ] TASK-03-02: Implement the puzzle page: load today’s puzzle parameters (from a static JSON built at deploy time or from a thin API), display company profile (emissions baseline, abatement menu, offset price, penalty rate, cash), and render decision controls (abatement toggles, offset quantity slider, auction bid quantity/price inputs).
- [ ] TASK-03-03: Add instant feedback: as the player changes decisions, show projected emissions, compliance gap, and estimated total cost in real time.
- [ ] TASK-03-04: Implement the submit flow: on submit, freeze inputs, compute total cost client-side (if engine is ported to JS) or send decisions to a serverless function (if engine stays Python), then display the results screen with player cost vs. optimal cost.
- [ ] TASK-03-05: Build the share card: an emoji-grid visualization (e.g., green squares for abatement choices, yellow for offsets, gray for penalties) plus the cost spread in text form, suitable for copying to clipboard and pasting into Twitter/X, LinkedIn, or Slack.
- [ ] TASK-03-06: Add an “Explain” view that walks through the optimal solution step by step, turning the puzzle into a micro-learning moment.
- [ ] TASK-03-07: Ensure mobile usability: touch-friendly inputs, readable fonts, no horizontal scrolling.

**Files / Surfaces**
- `carbon-crunch-daily/` — new frontend directory
- `carbon-crunch-daily/src/pages/index.astro` (or `.tsx`) — puzzle page
- `carbon-crunch-daily/src/components/PuzzleForm.tsx` — decision controls
- `carbon-crunch-daily/src/components/ShareCard.tsx` — share card renderer
- `carbon-crunch-daily/src/lib/puzzleClient.ts` — client-side puzzle loader and cost calculator

**Dependencies**
- PHASE-01

**Exit Criteria**
- [ ] A player can complete the full loop (open → decide → submit → see score → copy share card) in under 5 minutes on a mobile phone.
- [ ] The share card renders correctly when pasted into Twitter/X and LinkedIn.
- [ ] The “Explain” view displays the optimal actions and their cost breakdown.

**Phase Risks**
- **RISK-03-01:** Portability tradeoff. Porting the full engine to JS is high effort; calling a Python backend adds latency and hosting cost. Mitigation: start with a serverless Python function (e.g., Vercel Edge or AWS Lambda) that imports `carbonsim-engine`; if traffic justifies it, consider a JS port later.

### PHASE-04 — Daily Seed Pipeline and Leaderboard

**Goal**
Automate the daily puzzle release and add a lightweight leaderboard so players can compare scores.

**Tasks**
- [ ] TASK-04-01: Build a daily seed pipeline: a scheduled job (GitHub Actions cron, or a simple script run at build time) that generates the next N days of puzzles, runs the solver on each, and writes static JSON files `puzzles/YYYYMMDD.json` plus a manifest.
- [ ] TASK-04-02: Add a thin score-submission backend. Because the puzzle is public, we must treat scores as unauthenticated and prevent trivial cheating by accepting only decision payloads, re-running the engine server-side, and recording the verified cost. Store submissions in a free-tier database (e.g., Vercel KV, Supabase, or Fly.io Postgres).
- [ ] TASK-04-03: Build a leaderboard view: daily tab (today’s scores), weekly tab, and a personal-best streak tracker (stored in localStorage for simplicity; server-side streaks only if authentication is added later).
- [ ] TASK-04-04: Add a small admin endpoint or script to regenerate puzzles if a bug is discovered post-publish.
- [ ] TASK-04-05: Instrument basic analytics: daily unique players, share-card copy events, average solve time, average cost spread vs. optimal. Use privacy-friendly analytics (Plausible or Cloudflare Web Analytics) rather than cookie-based trackers.

**Files / Surfaces**
- `.github/workflows/daily-puzzle.yml` — cron workflow to generate puzzles
- `carbon-crunch-daily/api/submit-score.py` (or equivalent serverless function) — score validation and storage
- `carbon-crunch-daily/src/components/Leaderboard.tsx` — leaderboard UI
- `carbon-crunch-daily/src/lib/analytics.ts` — event tracking wrapper

**Dependencies**
- PHASE-02, PHASE-03

**Exit Criteria**
- [ ] A new puzzle is automatically published every day at 00:00 UTC without manual intervention.
- [ ] A player can submit a score, see their rank on a leaderboard, and view the daily score distribution.
- [ ] Analytics dashboard shows daily active players and share rate.

**Phase Risks**
- **RISK-04-01:** Cheating is trivial if we accept client-reported scores. Mitigation: server-side re-computation of cost from submitted decisions is mandatory.
- **RISK-04-02:** Free-tier database limits may throttle leaderboard writes if the puzzle goes viral. Mitigation: start with rate limiting (one submission per IP per day); upgrade database only if sustained traffic justifies it.

### PHASE-05 — Growth Experiments and Distribution

**Goal**
Extend the puzzle’s reach through low-cost distribution channels and iterate based on engagement data.

**Tasks**
- [ ] TASK-05-01: Build a Discord bot that posts the daily puzzle link each morning to a configured channel, along with yesterday’s optimal score and a fun fact about the scenario’s sector.
- [ ] TASK-05-02: Add an optional daily email signup (e.g., Buttondown or Mailchimp free tier) that sends the puzzle link + a sector explainer each morning.
- [ ] TASK-05-03: Create an embeddable widget (`<iframe>`) so partner sites (climate blogs, policy schools, NGO pages) can host the puzzle inline.
- [ ] TASK-05-04: Run A/B experiments on share-card copy (emoji density vs. text brevity), puzzle difficulty scheduling (easy on weekends, hard mid-week), and the presence of the “Explain” view.
- [ ] TASK-05-05: Define and instrument the measurement plan: target 1,000 daily active players within 3 months of launch; target 15% share-card copy rate; target <30 seconds average time-to-first-decision.

**Files / Surfaces**
- `carbon-crunch-daily/scripts/discord_bot.py` — daily post bot
- `carbon-crunch-daily/public/widget.html` — embeddable iframe page
- `carbon-crunch-daily/src/lib/experiments.ts` — experiment flagging and bucketing

**Dependencies**
- PHASE-04

**Exit Criteria**
- [ ] Discord bot posts daily for 7 consecutive days without failure.
- [ ] At least one partner site embeds the widget.
- [ ] A/B experiment framework is running and collecting data on at least one variant.

**Phase Risks**
- **RISK-05-01:** Growth experiments can distract from core puzzle quality. Mitigation: cap experiment time to 20% of phase effort; kill experiments that do not move the target metrics within two weeks.

## Verification Strategy

- **TEST-001:** Run the full engine test suite (`unittest tests.test_engine`) after extraction to ensure no regressions.
- **TEST-002:** Script `scripts/verify_puzzles.py` generates puzzles for the next 30 days, solves each, and asserts solvability + optimal cost < penalty-only cost.
- **MANUAL-001:** Complete the puzzle on a mobile device, copy the share card, paste it into a social platform, and confirm formatting.
- **MANUAL-002:** Facilitator dry-run: run the puzzle during a 15-minute break in a real CarbonSim workshop and collect verbal feedback.
- **OBS-001:** Monitor daily active player count, share-card copy rate, and average solve time via the analytics dashboard.

## Risks and Alternatives

- **RISK-001:** The daily puzzle may cannibalize workshop attendance if policy makers perceive it as a substitute. Mitigation: position the puzzle explicitly as an “on-ramp” or “daily warm-up” in all copy, not a replacement for the full simulation.
- **RISK-002:** Brute-force solver performance degrades if puzzle complexity increases (more abatement options, multi-year). Mitigation: solver is modular; we can replace brute force with integer programming or memoized dynamic programming without changing the API.
- **ALT-001:** *Client-side JS port of the engine.* This would eliminate backend latency and hosting cost entirely. It was not chosen because ~2,000 lines of Python engine logic would need a full rewrite and test suite; a serverless Python function is faster to ship and easier to maintain in parity with the workshop product.
- **ALT-002:** *Authenticate users for leaderboard integrity.* This was not chosen because it adds friction to a 5-minute daily ritual; anonymous nicknames + IP rate limiting strike a better friction/integrity balance for V1.

## Grill Me

1. **Q-001:** Should the daily puzzle allow players to “go back” and retry the same day’s puzzle multiple times, or is it strictly one attempt per day like Wordle?
   - **Recommended default:** Strictly one submission per day per IP (with localStorage enforcement). Retry would undermine share-card comparability.
   - **Why this matters:** Determines whether the leaderboard tracks first-attempt scores only or best scores, and whether we need anti-replay logic beyond IP rate limiting.
   - **If answered differently:** If retries are allowed, we must track best-score logic server-side and the share card should display number of attempts.

2. **Q-002:** Should the puzzle reuse the existing Vietnam-pilot sector set (thermal power, steel, cement) or rotate through a broader set of sectors and regions?
   - **Recommended default:** Start with the existing three sectors, rotating daily, so the puzzle reinforces workshop learning.
   - **Why this matters:** Sector rotation affects content writing (each sector needs a short explainer in the “Explain” view) and puzzle balance (abatement menus differ by sector).
   - **If answered differently:** A broader sector set requires new abatement catalog entries and re-calibration of the difficulty bounds.

3. **Q-003:** Do we want multi-year continuity (e.g., a 3-day arc where banked allowances carry over) or strictly independent daily puzzles?
   - **Recommended default:** Strictly independent daily puzzles for V1. Multi-year continuity is a V2 feature that complicates the oracle and the onboarding flow.
   - **Why this matters:** Independent puzzles mean each day is self-contained; multi-year arcs require tutorial onboarding and state persistence across days.
   - **If answered differently:** Multi-year arcs would need a player identity system (even if lightweight) and a very different frontend flow.

4. **Q-004:** What is the maximum acceptable hosting budget for the leaderboard backend?
   - **Recommended default:** $0/month at launch (serverless free tiers: Vercel Hobby, Supabase free, or Cloudflare Workers).
   - **Why this matters:** Determines whether we can afford a persistent Postgres instance or must rely on KV stores and edge functions.
   - **If answered differently:** If a small budget is approved, we could use a managed Postgres on Fly.io or Railway for richer analytics and stronger anti-cheat.

5. **Q-005:** Should the share card include the player’s rank or percentile, or only their absolute cost spread vs. optimal?
   - **Recommended default:** Absolute cost spread only for V1. Rank requires a real-time leaderboard query that may be stale or slow.
   - **Why this matters:** Rank adds competitive pressure but also potential disappointment for late-day players. Absolute spread is a self-contained metric.
   - **If answered differently:** If rank is included, we need a nightly cutoff or a rolling percentile calculation.

## Suggested Next Step

Answer the Grill Me questions, update this plan with the decisions, then begin PHASE-01 by creating the `carbonsim-engine` standalone package and the puzzle generator.
