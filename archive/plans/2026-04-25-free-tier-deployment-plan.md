---
title: "CarbonSim Free-Tier Deployment Plan"
date: "2026-04-25"
status: "draft"
request: "Create a detailed multi-phase markdown deployment plan for the CarbonSim online oTree app on free-tier services. Rank top 3 free-tier options."
plan_type: "multi-phase"
research_inputs:
  - "research/2026-04-13_online-carbonsim-platform-create.md"
  - "research/2026-04-06_online-carbonsim-platform.md"
---

# Plan: CarbonSim Free-Tier Deployment

## Objective
Deploy the existing oTree-based CarbonSim workshop (Django/ASGI, Postgres, WebSocket live methods, ~20 concurrent participants per session) to a zero-cost or near-zero-cost host that supports long-running Python processes and WebSockets. This plan picks a primary platform, defines a fallback, and sequences the work from provider selection through pilot dry-run.

## Context Snapshot
- **Current state:** oTree app in `platform/` runs locally with `otree prodserver1of2` (web/ASGI) plus `otree prodserver2of2` (worker), backed by SQLite (dev) or Postgres via `DATABASE_URL`. `platform/Dockerfile`, `platform/docker-compose.yml`, and `platform/Procfile` already exist; `settings.py` reads `SECRET_KEY`, `OTREE_PRODUCTION`, `OTREE_ADMIN_PASSWORD` from env. 92 tests pass through phase 10 (replay + analytics).
- **Desired state:** A publicly reachable URL serves the facilitator panel and participant workshop hub, survives 90-minute live sessions without sleeping, holds Postgres state across sessions, and costs $0 (or covered by perpetual free credits) for the pilot phase.
- **Key repo surfaces:** `platform/Dockerfile`, `platform/docker-compose.yml`, `platform/Procfile`, `platform/settings.py`, `platform/requirements.txt`, `platform/FACILITATOR_RUNBOOK.md`, `README.md` deployment section.
- **Out of scope:** Custom domain + TLS automation beyond what the host provides for free, paid tier upgrades, multi-region HA, autoscaling beyond a single instance, CI/CD pipelines.

## Research Inputs
- `research/2026-04-13_online-carbonsim-platform-create.md` — confirms the V1 deployment posture (single-region, oTree prodserver, Postgres, 20-person workshops) and rules out exchange-grade infra. Justifies optimizing free-tier picks for a single always-on instance over autoscaling fleets.
- `research/2026-04-06_online-carbonsim-platform.md` — establishes that live WebSocket fidelity and facilitator continuity are the binding constraints, which eliminates "scale-to-zero" platforms with cold starts longer than a few seconds during a live session.
- Repo audit (no separate brief): `platform/Procfile` already encodes the two-process model; many free tiers cap at one process, which forces a decision between collapsing to `otree prodserver` (single-process mode) or paying for a worker.

## Assumptions and Constraints
- **ASM-001:** Workshops are scheduled events (~90 min), not 24/7 traffic. Brief idle periods between sessions are acceptable, but mid-session sleep/cold-start is unacceptable.
- **ASM-002:** A single instance with 1 vCPU and 512 MB RAM is sufficient for ~20 concurrent oTree live-method clients based on oTree's documented sizing for classroom/workshop use.
- **ASM-003:** The facilitator can run a one-shot `otree resetdb` and `otree devserver` style migration via the host's shell or a release command; no zero-downtime migration tooling is required.
- **CON-001:** "Free tier" must be perpetually free at this scale, or covered by always-on free credits — not a 12-month introductory offer.
- **CON-002:** WebSockets must work without per-request limits that interrupt 20+ minute decision windows. Rules out platforms that proxy WS through short-lived HTTP request budgets.
- **CON-003:** Postgres must survive across sessions and idle weeks (rules out free tiers that auto-pause/wipe DBs after 7 days unless we add a keep-alive job).
- **DEC-001:** App stays as oTree on Python 3.12; no rewrite to Streamlit/Firebase/Supabase Edge runtimes — those are server BaaS or single-page-app hosts, not Django/ASGI hosts.
- **DEC-002:** The deploy artifact is the existing `platform/Dockerfile` (not a buildpack), so any chosen host must accept a Docker image or a `Procfile` plus `requirements.txt`.

## Free-Tier Provider Evaluation

The user listed Firebase, Supabase, Streamlit, Oracle, plus standard alternatives. Most listed options do **not** host long-running Python/Django/ASGI processes; they were screened out before ranking.

### Disqualified outright
| Provider | Why disqualified |
|---|---|
| **Firebase Hosting / Cloud Functions** | Static hosting + short-lived functions only. No persistent Django/ASGI runtime. Cloud Functions max execution is too short for live WebSocket sessions. |
| **Supabase (as app host)** | Backend-as-a-service. Edge Functions are Deno-only, not Python. **Useful only as a free Postgres provider for a separate app host (see hybrid in option #3).** |
| **Streamlit Community Cloud** | Streamlit apps only; no Django/oTree. Not relevant. |
| **PythonAnywhere Free** | No WebSockets on free tier. Single worker. No Postgres on free. Hard fail on live methods. |
| **AWS Free Tier (t2.micro EC2)** | 12-month introductory only — fails CON-001. After year 1 it bills. |
| **Railway** | No perpetual free tier; $5 trial credit only. Not free. |
| **Heroku** | No free dynos since Nov 2022. |

### Top 3 ranking (viable for oTree)

| Rank | Provider | Always-free at this scale? | WebSockets | Postgres free | Sleep / cold start | Setup effort | Resource ceiling |
|---|---|---|---|---|---|---|---|
| **#1** | **Oracle Cloud Always Free (Ampere A1 ARM VM)** | Yes, perpetual | Yes (full VM, no proxy limits) | Yes (self-hosted Postgres in Docker) | Never sleeps | High (manual VM ops) | 4 OCPU / 24 GB RAM / 200 GB block storage — far exceeds need |
| **#2** | **Fly.io (free allowance)** | Effectively yes for 1 small machine + 1 GB Postgres; card on file required | Yes, native (TCP + WS) | Yes (Fly Postgres free dev cluster) | Auto-stop is **opt-in**; can be disabled | Low (`fly launch` reads Dockerfile) | shared-cpu-1x / 256 MB (free); upgradeable per-second |
| **#3** | **Render Free Web Service + Supabase Postgres free** | Yes, but with caveats | Yes on Render web | Yes on Supabase (500 MB) | Render web sleeps after 15 min idle; Supabase DB pauses after 7 days idle | Lowest (git-push to Render, copy DSN from Supabase) | 512 MB RAM / 0.1 CPU; 750 h/mo |

**Why this order:**
1. **Oracle** is the only option with no operational footnotes for a 90-minute live session: a real VM, no sleep, no per-request WebSocket budget, free forever, more RAM than we will ever use. Cost is a one-time setup tax (Linux + Docker + reverse proxy + TLS).
2. **Fly.io** is the most oTree-native PaaS: Dockerfile-first, persistent volumes, built-in Postgres, WebSockets work without configuration. Requires a card but, at this scale, stays inside the always-free allowance. Best option if Oracle's ops burden is unwanted.
3. **Render + Supabase** is the fastest path to a URL but has two real risks for live workshops: web service cold-starts after 15 min idle (a participant waiting on a phase boundary can be the unlucky request that pays the cold start), and Supabase pauses idle databases after 7 days. Workable for demo or ad-hoc use with a warm-up step in the runbook.

**Primary recommendation:** Deploy on **Oracle Cloud Always Free (Ampere A1)**. Use **Fly.io** as the documented fallback if the Oracle account is unavailable or the user wants to skip VM ops.

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | Pick provider, harden settings for cloud | None | Decision log, env-var template, settings audit |
| PHASE-02 | Deploy primary path on Oracle Cloud Always Free | PHASE-01 | Public URL, running container, persistent Postgres |
| PHASE-03 | Configure ops surface (TLS, backups, runbook) | PHASE-02 | HTTPS endpoint, daily DB dump, updated runbook |
| PHASE-04 | Document Fly.io fallback path | PHASE-01 | `fly.toml`, fallback section in runbook |
| PHASE-05 | Pilot dry-run + acceptance | PHASE-03 | Recorded 20-participant rehearsal, sign-off checklist |

## Detailed Phases

### PHASE-01 — Provider selection and cloud-readiness audit
**Goal**
Lock in Oracle as primary, document Fly.io as fallback, and make sure `platform/` runs cleanly behind a public reverse proxy with env-driven config and Postgres.

**Tasks**
- [ ] TASK-01-01: Add a `## Hosting decision` section to `platform/FACILITATOR_RUNBOOK.md` summarizing the ranking table and naming Oracle as primary.
- [ ] TASK-01-02: Verify `platform/settings.py` reads every secret from env (`SECRET_KEY`, `OTREE_ADMIN_PASSWORD`, `OTREE_PRODUCTION`, `DATABASE_URL`). Replace the hardcoded `SECRET_KEY` fallback `"1314886002300"` with `None` and fail fast in production when missing.
- [ ] TASK-01-03: Confirm `platform/requirements.txt` pins `otree>=5.0.0a21`, `psycopg2`, `requests`, `ws4py`. Add `gunicorn` only if the chosen run command needs it (oTree's `prodserver1of2` already wraps Daphne — do not double-wrap).
- [ ] TASK-01-04: Audit `platform/Dockerfile` — current `CMD ["otree", "prodserver1of2"]` runs only the web side. Decide for free-tier: collapse to `otree prodserver` (single-process) by changing `CMD` to `["otree", "prodserver"]` so we do not need a second container. Document the tradeoff (slightly lower throughput, fine for ≤20 participants).
- [ ] TASK-01-05: Add a `.env.production.example` next to `platform/Dockerfile` listing required keys with empty values; do **not** commit a real `.env`.
- [ ] TASK-01-06: Run `python -m unittest discover` from `platform/` once more to confirm all 92 tests still pass after settings hardening.

**Files / Surfaces**
- `platform/settings.py` — env handling, SECRET_KEY enforcement.
- `platform/Dockerfile` — `CMD` collapse to single-process.
- `platform/requirements.txt` — confirm minimal deps.
- `platform/FACILITATOR_RUNBOOK.md` — hosting decision section.
- `platform/.env.production.example` — env-var template.

**Dependencies**
- None.

**Exit Criteria**
- [ ] `SECRET_KEY` missing in production raises an explicit error before serving traffic.
- [ ] `docker build -t carbonsim platform/` succeeds locally.
- [ ] `docker run --rm -e SECRET_KEY=... -e DATABASE_URL=postgres://... -p 8000:8000 carbonsim` boots and serves the admin login at `http://localhost:8000/`.
- [ ] All 92 unit tests still pass.

**Phase Risks**
- **RISK-01-01:** Collapsing to `otree prodserver` may change behavior under load. Mitigation: this is the documented oTree "small workshop" mode and is what the runbook will recommend; load test in PHASE-05.

### PHASE-02 — Deploy on Oracle Cloud Always Free
**Goal**
Stand up a single Ampere A1 ARM VM running the Docker image plus a Postgres container, with the workshop reachable from a public IP on port 80/443.

**Tasks**
- [ ] TASK-02-01: Create an Oracle Cloud account (corporate email + card for identity verification, no charge). Choose the **Always Free** Ampere A1 shape: 2 OCPU / 12 GB RAM is sufficient and stays inside the perpetual cap.
- [ ] TASK-02-02: Provision a VCN with a public subnet. Open ingress on TCP 22 (SSH, restricted to facilitator IP), 80, 443. Assign a reserved public IPv4.
- [ ] TASK-02-03: SSH in and install Docker + Docker Compose plugin (`sudo dnf install -y docker docker-compose-plugin` on Oracle Linux 9 / `apt install` on Ubuntu 22.04 ARM image).
- [ ] TASK-02-04: `git clone` this repo onto the VM under `/opt/carbonsim` (or `scp` a tarball if the repo stays private without a deploy key).
- [ ] TASK-02-05: Create `/opt/carbonsim/platform/.env` from the template with real secrets: `OTREE_ADMIN_PASSWORD`, `SECRET_KEY` (generate via `python -c "import secrets;print(secrets.token_urlsafe(50))"`), `OTREE_PRODUCTION=1`, `POSTGRES_PASSWORD`, and a `DATABASE_URL=postgres://carbonsim:<pw>@db:5432/carbonsim`.
- [ ] TASK-02-06: Edit `platform/docker-compose.yml` for production: drop the `worker` service (per TASK-01-04), bind `web` to `127.0.0.1:8000` (Caddy will front it), keep the `db` service with the named volume.
- [ ] TASK-02-07: `docker compose up -d` from `platform/`. Confirm `docker compose logs web` shows oTree booted and migrated against Postgres.
- [ ] TASK-02-08: Run one-time `docker compose exec web otree resetdb --noinput` to materialize the schema if not auto-migrated, then create the workshop room session via the admin UI to smoke-test.

**Files / Surfaces**
- `platform/docker-compose.yml` — prod overrides (worker removed, web bound to localhost).
- `/opt/carbonsim/platform/.env` (on VM, not in repo) — real secrets.
- Oracle VCN security list — ingress rules.

**Dependencies**
- PHASE-01 complete; image builds cleanly.

**Exit Criteria**
- [ ] `curl http://<public-ip>/` returns oTree's home page (after Caddy in PHASE-03; for now `curl 127.0.0.1:8000` from the VM works).
- [ ] `docker compose ps` shows `web` and `db` healthy.
- [ ] A demo session created via `/admin` reaches the participant join screen end-to-end from a browser on the facilitator's machine.

**Phase Risks**
- **RISK-02-01:** Oracle has historically reclaimed unused Always Free VMs. Mitigation: enable auto-renewal flag and run a cron'd `uptime` ping into a log so the VM never looks idle.
- **RISK-02-02:** ARM image vs. amd64 mismatch — `psycopg2` and `python:3.12-slim` both publish ARM builds, so this is unlikely, but TASK-02-07 must verify at first boot.

### PHASE-03 — TLS, backups, ops hardening
**Goal**
Make the deployment safe to hand to a facilitator: HTTPS on a real hostname, daily Postgres dump to durable storage, restart-on-failure, monitoring hook.

**Tasks**
- [ ] TASK-03-01: Pick a hostname. Either reuse a domain the user owns, or use a free dynamic DNS provider (DuckDNS) pointing at the VM's reserved public IP.
- [ ] TASK-03-02: Add a `caddy` service to `platform/docker-compose.yml` that proxies `:443 → web:8000`. A 5-line Caddyfile (`carbonsim.<domain> { reverse_proxy web:8000 }`) gives automatic Let's Encrypt TLS with no extra config. Open VCN ingress 80/443.
- [ ] TASK-03-03: Verify WebSocket upgrade traverses Caddy correctly by hitting `wss://<host>/...` from the in-app live page (Caddy's `reverse_proxy` upgrades WS by default; confirm in browser devtools network tab).
- [ ] TASK-03-04: Add a nightly `pg_dump` cron on the host: `0 3 * * * docker compose exec -T db pg_dump -U carbonsim carbonsim | gzip > /opt/carbonsim/backups/$(date +\%F).sql.gz` and a 14-day retention `find ... -mtime +14 -delete`. Backups live on the VM's 200 GB block storage (also free).
- [ ] TASK-03-05: Set `restart: unless-stopped` on all services (already in compose) and enable Docker on boot: `sudo systemctl enable --now docker`.
- [ ] TASK-03-06: Update `platform/FACILITATOR_RUNBOOK.md` Deployment section with: SSH instructions, `.env` template path, `docker compose` commands, backup/restore commands, and the public URL.

**Files / Surfaces**
- `platform/docker-compose.yml` — `caddy` service.
- `platform/Caddyfile` (new) — 5-line reverse proxy config.
- `platform/FACILITATOR_RUNBOOK.md` — deployment + backup section.
- VM crontab — nightly `pg_dump`.

**Dependencies**
- PHASE-02 web reachable on the public IP.

**Exit Criteria**
- [ ] `curl -I https://<host>/` returns 200 with a valid Let's Encrypt cert.
- [ ] Browser devtools shows `wss://` upgrade succeeds on the workshop hub page.
- [ ] First nightly dump appears in `/opt/carbonsim/backups/` and `gunzip -c <dump> | head` shows valid SQL.
- [ ] Rebooting the VM (`sudo reboot`) brings `web`, `db`, `caddy` back automatically.

**Phase Risks**
- **RISK-03-01:** Caddy auto-TLS requires that the hostname resolve to the VM before issuance. Mitigation: set DNS A record first, wait for propagation (`dig +short`), then `docker compose up -d caddy`.

### PHASE-04 — Fly.io fallback path
**Goal**
Document, but do not deploy, a second working path so the facilitator can switch hosts in under 60 minutes if Oracle becomes unavailable.

**Tasks**
- [ ] TASK-04-01: Add `platform/fly.toml` with `app = "carbonsim"`, `primary_region` chosen near workshop participants (e.g. `sin` for Vietnam pilots), `[http_service] internal_port = 8000`, `auto_stop_machines = false`, `min_machines_running = 1`.
- [ ] TASK-04-02: Document the `flyctl launch --no-deploy --copy-config` flow in `platform/FACILITATOR_RUNBOOK.md` under a "Fallback: Fly.io" subsection.
- [ ] TASK-04-03: Document the `fly postgres create --name carbonsim-db --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1` command and the `fly postgres attach` step that wires `DATABASE_URL` into the app.
- [ ] TASK-04-04: Document `fly secrets set SECRET_KEY=... OTREE_ADMIN_PASSWORD=... OTREE_PRODUCTION=1` and `fly deploy`.
- [ ] TASK-04-05: Note the always-free caveats: card on file required, soft-cap monitoring via `fly dashboard`, and the recommendation to keep `auto_stop_machines = false` so live sessions are never cold-started.

**Files / Surfaces**
- `platform/fly.toml` (new) — Fly app config.
- `platform/FACILITATOR_RUNBOOK.md` — fallback section.

**Dependencies**
- PHASE-01 image builds cleanly (Fly uses the same `Dockerfile`).

**Exit Criteria**
- [ ] `fly.toml` validates via `flyctl config validate` (run locally, no deploy needed).
- [ ] Runbook contains a copy-pasteable command sequence for full redeploy in <10 commands.

**Phase Risks**
- **RISK-04-01:** Fly's free-tier policy has shifted twice in the last 18 months. Mitigation: re-verify the resource cap on the day of fallback, not in advance — the runbook should link to `https://fly.io/docs/about/pricing/` rather than hard-code numbers.

### PHASE-05 — Pilot dry-run and sign-off
**Goal**
Prove the deployed instance survives a realistic 20-participant 90-minute workshop end-to-end before scheduling the real pilot.

**Tasks**
- [ ] TASK-05-01: Schedule a 90-minute internal rehearsal with 20 browser tabs (or browser-bot helpers from `platform/scripts/`, if present) joining the `workshop_room`.
- [ ] TASK-05-02: During the rehearsal, monitor `docker compose stats` for memory headroom (must stay under 80% of VM RAM) and `docker compose logs web` for `WebSocket disconnect` events.
- [ ] TASK-05-03: Trigger one shock event mid-session (per phase 7 facilitator controls) and confirm all participants see the update within 2 seconds.
- [ ] TASK-05-04: At session end, click the facilitator panel "Export" button and confirm the JSON export contains companies, auctions, trades, audit log, replay, and analytics blocks.
- [ ] TASK-05-05: Restore the latest nightly dump to a scratch Postgres instance and run a few `SELECT count(*) FROM ...` sanity queries to prove backups are usable.
- [ ] TASK-05-06: Record results, blockers, and follow-ups in `activeContext.md` under a new "Free-tier deployment dry run" review section.

**Files / Surfaces**
- `activeContext.md` — review section for the dry-run.
- `platform/FACILITATOR_RUNBOOK.md` — append rehearsal results / known limits.

**Dependencies**
- PHASE-03 complete (HTTPS + backups working).

**Exit Criteria**
- [ ] Rehearsal completes 3 simulated years with all 20 participants online and no facilitator-side errors.
- [ ] Export JSON validates against the schema implied by `export_session_data` (spot-check non-empty blocks).
- [ ] Backup-restore round trip succeeds.
- [ ] Sign-off line added to `activeContext.md`.

**Phase Risks**
- **RISK-05-01:** Network egress on Oracle Always Free is capped at 10 TB/month — far above what 20 participants will use, but worth confirming via VM metrics during the dry-run so it doesn't surprise us at scale.

## Verification Strategy
- **TEST-001:** Run `python -m unittest discover` from `platform/` after every settings change in PHASE-01; confirm 92 tests pass.
- **TEST-002:** `docker build` and `docker compose up` locally before pushing to the VM; the local container must serve `/admin` and accept a websocket upgrade on the workshop hub page.
- **MANUAL-001:** End-to-end smoke: facilitator creates session → participant joins via room URL → year 1 advances → bid placed → auction clears → trade proposed → analytics export downloads.
- **MANUAL-002:** Disconnect simulation: refresh a participant tab mid-decision, confirm `reconnect` action restores their company state (this exercises the phase 8 deployment module against the real DB).
- **OBS-001:** During PHASE-05, capture `docker stats` and Caddy access logs; archive both alongside `reports/` so the pilot dry-run is auditable.
- **OBS-002:** Add a one-line `/health` curl from a free uptime monitor (UptimeRobot free tier, 5-minute interval) so silent VM death is detected before a workshop.

## Risks and Alternatives
- **RISK-001:** Oracle Cloud accounts have been flagged and revoked unpredictably for some users in the past. Mitigation: PHASE-04 documents Fly.io as a working fallback; nightly Postgres dump is portable.
- **RISK-002:** WebSocket disconnects under flaky participant networks could be misread as platform problems. Mitigation: phase 8's `reconnect_company` already exists; PHASE-05 explicitly tests it.
- **ALT-001:** **Render + Supabase hybrid (rank #3).** Faster setup but rejected as primary because Render free web services sleep after 15 min idle, which kills the participant experience if the facilitator opens the URL ahead of a session. Acceptable for one-off internal demos only — keep as a "throwaway link" option in the runbook, not the production path.
- **ALT-002:** **Google Cloud Run.** Generous free request quota, but its 60-minute WebSocket cap and scale-to-zero behavior add operational gotchas for a 90-minute live workshop. Not worth the configuration tax when Oracle gives us a real VM for free.
- **ALT-003:** **Self-hosting on the facilitator's laptop with a Cloudflare Tunnel.** Truly free, no provider lock-in, but ties workshop uptime to a person's laptop and home network. Out of scope — workshop is a scheduled event, not ad-hoc.

## Grill Me
1. **Q-001:** Is there a domain name the project already controls (e.g. `carbonsim.<something>`), or should the runbook default to a free DuckDNS subdomain?
   - **Recommended default:** Use DuckDNS for the pilot, swap to a real domain post-pilot.
   - **Why this matters:** Determines the hostname inside the Caddyfile in TASK-03-02 and the Let's Encrypt issuance path.
   - **If answered differently:** A real domain shortens DNS propagation and looks better to pilot stakeholders, but adds a registrar/billing dependency outside "free tier."
2. **Q-002:** Does the user have an existing Oracle Cloud account, or do we need to allow time (24–48h) for Oracle's identity verification before PHASE-02 can start?
   - **Recommended default:** Assume new account; schedule PHASE-02 at least 2 days after PHASE-01 sign-off.
   - **Why this matters:** Oracle ID verification is a known multi-day blocker.
   - **If answered differently:** If an account already exists, PHASE-02 can start the same day as PHASE-01.
3. **Q-003:** Should bots (`carbonsim_workshop_with_bots` config) be the default session for the public deployment, or should a fresh deploy default to `carbonsim_workshop_phase12` with no bots?
   - **Recommended default:** No bots by default; facilitator picks the bot config explicitly per session.
   - **Why this matters:** Affects the smoke-test step in TASK-02-08 and the rehearsal participant count in TASK-05-01.
   - **If answered differently:** A bots-default deploy means the rehearsal needs only ~17 humans + 3 bots.
4. **Q-004:** What is the geographic distribution of pilot participants? Vietnam-only, mixed APAC, or global?
   - **Recommended default:** Vietnam-only — pick Oracle's `ap-singapore-1` region for the VM and Fly's `sin` as fallback.
   - **Why this matters:** Drives Oracle region selection in TASK-02-01 and Fly `primary_region` in TASK-04-01. Wrong region adds 200+ ms latency to live methods.
   - **If answered differently:** Global participants may justify Fly.io's multi-region routing as primary instead of Oracle.
5. **Q-005:** Is there budget appetite for a $5–10/month upgrade if the free tier proves marginal during PHASE-05?
   - **Recommended default:** No paid upgrade — re-architect to bots + smaller cohorts before paying.
   - **Why this matters:** Determines whether PHASE-05 failure means "stop and redesign" or "switch to Fly.io paid `shared-cpu-1x` at ~$3/month."
   - **If answered differently:** A small budget unlocks Fly.io as a no-asterisks primary and demotes Oracle to fallback.

## Suggested Next Step
Answer the Grill Me questions (especially Q-002 on Oracle account status and Q-004 on participant geography), then begin PHASE-01 by hardening `platform/settings.py` and updating the Dockerfile `CMD` to single-process mode.
