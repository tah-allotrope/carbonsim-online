# CarbonSim Facilitator Runbook

## Hosting Decision

### Recommended free-tier order

1. Oracle Cloud Always Free Ampere A1 VM
2. Fly.io fallback
3. Render + Supabase for throwaway demos only

Oracle is the primary recommendation because it is the only option in the current plan that gives a long-running Python process, working WebSockets, Postgres, and no mid-session sleep risk for a 90-minute workshop.

### Deployment surfaces in this repo

- `Dockerfile` runs `otree prodserver` in single-process mode for small workshops.
- `docker-compose.yml` provides `web` and `db` services for local and VM deployments.
- `.env.production.example` lists the production environment variables that must be filled in on the host.
- `Caddyfile` is the reverse-proxy template for HTTPS on Oracle.
- `fly.toml` is the fallback Fly.io app config.

## Pre-Session Checklist

### 1. Environment setup

- [ ] Confirm the oTree server is running and reachable at the expected URL.
- [ ] Verify `OTREE_ADMIN_PASSWORD` is set and the admin panel works.
- [ ] For Docker deployments run `docker compose up -d` and inspect `docker compose logs web`.
- [ ] For local workshops start from `platform/` with `otree devserver 8000`.
- [ ] Confirm the database is clean enough for a fresh workshop session.

### 2. Session configuration

- [ ] Choose a session config.
- [ ] Set realistic `phase_durations` for a live workshop rather than the short test defaults.
- [ ] Create a session in the admin panel for the expected participant count.
- [ ] Record the room URL and share it with participants.

### 3. Participant preparation

- [ ] Brief participants that they are covered companies in a compliance market simulator.
- [ ] Explain the three-year compressed structure.
- [ ] Confirm each participant can open the Welcome page and sees an assigned company.

## During-Session Operations

### Starting the simulation

1. The facilitator starts the session from the workshop hub.
2. Year 1 allocations are issued immediately.
3. The year-start timer transitions into the decision window.

### Year flow

Each simulated year follows this sequence:

1. Year Start: allocations are issued, the cap is announced, and pending abatements activate.
2. Decision Window: participants can activate abatement, buy offsets, bid in auctions, and propose bilateral trades.
3. Compliance: surrender is processed, surplus is banked, and shortfalls incur penalties.

### Facilitator controls

- Pause: freezes timers.
- Resume: restores the previous phase and extends the deadline by the pause duration.
- Advance phase: manually moves to the next phase.
- Open / Clear auction: controls scheduled year auctions.
- Run bot turn: executes all configured bot decisions in the current decision window.
- Apply shock: injects a market or policy disruption into the current year.

### Monitoring participants

The facilitator panel shows:

- phase, year, cap, and countdown
- participant company, cash, allowances, compliance gap, penalties, and last action
- auction log, active shocks, summary, replay, and analytics

### Handling disconnections

1. State is preserved on the server.
2. The reconnect action restores the latest company snapshot.
3. The facilitator panel exposes participant activity to confirm recovery.

## Debrief Guidance

### Core debrief questions

- What drove your abatement and offset choices?
- How did scarcity affect your auction and trade behavior?
- Did you bank allowances for future years?
- How did shocks alter your strategy?

### Role mapping

The simulator is a workshop abstraction of the Vietnam CTX, not a literal replica.

| Simulator role | Real-world analogue |
|---|---|
| Facilitator | Market operator / oversight analogue across MOF, HNX, and MAE roles |
| Participants | Covered regulated entities |
| Export / audit log | Simplified transaction and compliance reporting |

### Vietnam policy and market caveats

- Auctions in pilot: This simulator includes auctions to teach sealed-bid price discovery. Vietnam's 2025-2028 pilot is expected to rely on free allocation only, with auctioning later.
- Price scale: Monetary values in the simulator are simulation units, not real VND/tCO2 prices.
- Penalty design: Penalties are deliberately set above the auction ceiling so non-compliance is never the rational low-cost choice.
- Growth rates: Growth assumptions are conservative relative to historical Vietnamese sector growth so introductory sessions remain legible.
- Allocation method: The simulator uses a simplified percentage-of-projected-emissions allocation model, while real Vietnam implementation is expected to use sector benchmarking.
- Banking: Banking is allowed and modelled without an entity-level holding limit.
- Borrowing: Borrowing against future years is not allowed.
- Make-good obligation: The simulator uses a cash penalty only. Real ETSs may also require surrender of the missing allowances later.
- MRV gap: The simulator assumes perfect annual emissions knowledge. Real MRV involves verification risk and reporting delays.
- NRS gap: The simulator does not model the National Registry System reconciliation layer.
- Offset simplification: Offsets are treated as one pool, while real markets distinguish allowance and credit types.
- MAC curve compression: Abatement costs are intentionally compressed to keep multiple options strategically relevant.
- Omitted sectors: The simulator focuses on thermal power, steel, and cement rather than every sector in Vietnam's broader ETS scope.

### Shock narratives for facilitators

- Emissions spike: a drought reduces hydropower output and forces more thermal dispatch.
- Allowance withdrawal: the regulator corrects an over-allocation after review.
- Cost shock: fuel and industrial input costs rise sharply.
- Offset supply change: new domestic credits become eligible and alter offset availability.

## Export Contents

The session export includes:

- companies
- auctions
- trades
- rankings
- audit log
- replay
- analytics

Use the export for workshop debriefing, offline analysis, and backup.

## Deployment Operations

### Docker deployment

```bash
cd platform
copy .env.production.example .env
docker compose up -d
docker compose logs -f web
```

### Oracle Cloud primary path

1. Provision an Always Free Ampere A1 VM.
2. Clone the repo to the host.
3. Create `platform/.env` from `.env.production.example`.
4. Set `OTREE_ADMIN_PASSWORD`, `SECRET_KEY`, `DATABASE_URL`, and Postgres credentials.
5. Run `docker compose up -d`.
6. Put Caddy in front of the app using `Caddyfile` and a real hostname.

### Fly.io fallback

1. Validate `fly.toml`.
2. Create the app with `fly launch --no-deploy --copy-config`.
3. Provision Postgres and attach it.
4. Set `SECRET_KEY`, `OTREE_ADMIN_PASSWORD`, and `OTREE_PRODUCTION=1` as Fly secrets.
5. Run `fly deploy`.

### Backup and restore

Example backup command on a Docker host:

```bash
docker compose exec -T db pg_dump -U carbonsim carbonsim > carbonsim.sql
```

Example restore command:

```bash
docker compose exec -T db psql -U carbonsim carbonsim < carbonsim.sql
```

### Health monitoring

The `health_check` live action returns:

- phase
- year
- current_cap
- participant_count
- total_companies
- auction_count
- trade_count
- audit_log_size
- paused/complete flags

## Common Issues

| Issue | Resolution |
|---|---|
| Participant sees stale data | Refresh the page; the live pages also poll for updates. |
| Timer appears frozen | Confirm the session is not paused. |
| Auction actions do nothing | Confirm the current phase is the decision window and the auction status is valid. |
| Trade fails on acceptance | Holdings or buyer cash may have changed since proposal time. |
| Production boot fails immediately | Check that `SECRET_KEY` is set when `OTREE_PRODUCTION=1`. |
