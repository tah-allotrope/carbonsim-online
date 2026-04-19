# CarbonSim Facilitator Runbook

## Pre-Session Checklist

### 1. Environment Setup

- [ ] Confirm the oTree server is running and accessible at the expected URL
- [ ] Verify `OTREE_ADMIN_PASSWORD` is set and the admin panel at `/otree-admin/` works
- [ ] For Docker deployments: `docker compose up -d` then check logs with `docker compose logs web`
- [ ] For local workshops: start the server from `platform/` with `otree devserver 8000`
- [ ] Confirm the database is clean. If reusing a previous session, clear it from the admin panel or delete `db.sqlite3`

### 2. Session Configuration

- [ ] Choose a session config from the available options:
  - **Vietnam Pilot (default)**: Three-year arc with tightening allocation, moderate penalty (200/tCO2), 10% offset cap. Best for first-time participants.
  - **High Pressure**: Sharper cap decline, higher penalty (350/tCO2), 5% offset cap. Creates more trading urgency.
  - **Generous Allocation**: Gentler decline, lower penalty (120/tCO2), 15% offset cap. Good for introductory sessions.
  - **Vietnam Pilot + Bots**: Same as Vietnam Pilot but includes 3 bot participants for liquidity. Recommended when participant count is below 6.
- [ ] Set `phase_durations` if you want non-default timings. Defaults are year_start=5s, decision_window=20s, compliance=5s (compressed for testing; use 300s/600s/180s for real workshops)
- [ ] In the admin panel, create a session with the chosen config and the expected number of participants
- [ ] Note the session URL and room URL for participant distribution

### 3. Participant Preparation

- [ ] Prepare browser tabs or a shared link for each participant
- [ ] Brief participants on the simulation premise: they are companies in a capped ETS, must stay compliant by combining free allocation, abatement, offsets, and trading
- [ ] Explain the three-year arc and compressed timing
- [ ] Confirm each participant can access the Welcome page and sees their assigned company name and sector

## During-Session Operations

### Starting the Simulation

1. As the facilitator (Player 1), click **Start Session** on the dashboard to begin Year 1
2. All participants will see the phase change from Lobby to Year Start
3. The decision window timer will begin counting down after the year-start phase

### Year Flow

Each simulated year follows this sequence:

1. **Year Start**: Allocations are issued, cap is announced, pending abatements activate
2. **Decision Window**: Participants can:
   - Activate abatement measures (costs deducted immediately, effect immediate or next year)
   - Purchase offsets (within the offset usage cap)
   - Submit bids in scheduled allowance auctions (facilitator must open and close each auction)
   - Propose and respond to bilateral allowance trades
3. **Compliance**: Year-end processing. Offsets are applied (up to cap), banked allowances carry forward, shortfalls incur penalties

### Facilitator Controls

- **Pause**: Freezes all timers. Use when participants need a break or you need to explain something
- **Resume**: Continues from where the pause occurred, extending the deadline by the pause duration
- **Advance Phase**: Manually moves to the next phase. Use if timers are too fast/slow for your group
- **Open/Close Auction**: Opens a scheduled auction for bids, then closes it to determine the clearing price and settle

### Shock Events

Shocks are facilitator-triggered disruptions that add teaching moments:

- **Emissions Spike**: Increases all companies' projected emissions by a percentage. Demonstrates cap pressure.
- **Allowance Withdrawal**: Reduces all companies' allowance holdings by a percentage. Demonstrates scarcity.
- **Cost Shock**: Reduces all companies' cash by a percentage. Demonstrates financial pressure.
- **Offset Supply Change**: Modifies the offset usage cap up or down. Demonstrates policy shifts.

To apply a shock: select the type from the dropdown, set a magnitude (e.g., 0.1 for 10%), and click **Apply Shock**.

### Bot Participants

Click **Run Bot Turn** on the facilitator panel to let all bot participants make their decisions for the current decision window. Bots follow their assigned strategy (conservative, moderate, or aggressive).

### Monitoring Participants

The facilitator panel shows:
- Phase, year, cap, and countdown timer
- Each participant's company, decisions this year, cash, allowances, compliance gap, and last action
- Active shocks and auction log
- Session summary for debriefing

### Handling Disconnections

If a participant loses connection:
1. Their state is fully preserved on the server
2. When they rejoin, they will automatically receive the current snapshot
3. The facilitator can check participant status in the panel to confirm they are reconnecting
4. No data is lost during disconnections; the year continues for all other participants

### Common Issues

| Issue | Resolution |
|-------|-------------|
| Participant sees stale data | Ask them to refresh the page; auto-poll updates every 2 seconds |
| Timer appears frozen | The session may be paused. Check the facilitator panel for pause state |
| Auction won't open | Ensure the auction is in "scheduled" status and the session is in the decision window phase |
| Participants can't trade | Trades require a positive allowance quantity and positive price per allowance |

## Post-Session Operations

### Debriefing

1. Use the **Export** button on the facilitator panel to download the full session data as JSON
2. The session summary provides:
   - Headline (e.g., "Completed 3 of 3 years")
   - Year-by-year compliance summaries per company
   - Final rankings sorted by cumulative penalties (lowest wins)
   - Market metrics (trades completed, auctions cleared, average clearing price)
   - Facilitator notes for discussion prompts
3. Key debrief questions:
   - What drove your abatement and offset decisions?
   - How did allowance scarcity affect your trading strategy?
   - Did you bank allowances for future years? Why or why not?
   - How did shock events (if any) change your behavior?
   - What would you do differently with more companies in the market?

### Data Export

The JSON export contains:
- **companies**: Full state for each company (holdings, penalties, year results, abatement)
- **auctions**: All auction bids, clearing prices, and settlement details
- **trades**: Complete trade history with proposals, responses, and expiration
- **rankings**: Companies ranked by cumulative penalties
- **audit_log**: Timestamped record of every game event

### Session Cleanup

- For local deployments: stop the server with Ctrl+C
- For Docker deployments: `docker compose down`
- For persistent data: save the JSON export before shutting down
- oTree stores session data in the database; old sessions can be cleared from `/otree-admin/`

## Production Deployment Notes

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OTREE_ADMIN_PASSWORD` | Admin panel access | None (required in production) |
| `SECRET_KEY` | Session security | Dev default (must change in production) |
| `OTREE_PRODUCTION` | Enables production mode | `0` |
| `DATABASE_URL` | Postgres connection string | SQLite (local dev only) |

### Docker Deployment

```bash
cd platform
cp .env.example .env
# Edit .env with production values
docker compose up -d
# Check logs
docker compose logs -f web
```

### Heroku Deployment

```bash
cd platform
heroku create your-app-name
heroku config:set OTREE_ADMIN_PASSWORD=your-strong-password
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set OTREE_PRODUCTION=1
git push heroku main
```

### Health Monitoring

The `deployment.health_check()` function provides a snapshot of the current session state:
- Phase, year, cap
- Participant count and company count
- Active auctions and pending trades
- Whether the session is paused or complete

This can be called programmatically via the `health_check` action in the live_method.

### Database Considerations

- For local workshops: SQLite is sufficient (oTree default)
- For production: use Postgres via `DATABASE_URL` environment variable
- The `psycopg2` package is included in `requirements.txt` for Postgres support
- Backup strategy: export session data after each workshop and store the JSON externally