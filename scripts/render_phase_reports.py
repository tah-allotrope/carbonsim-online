from __future__ import annotations

from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = (
    Path.home()
    / ".config"
    / "opencode"
    / "skills"
    / "report"
    / "assets"
    / "report-template.html"
)
FINAL_TEMPLATE_PATH = (
    Path.home()
    / ".config"
    / "opencode"
    / "skills"
    / "report"
    / "assets"
    / "final-report-template.html"
)
REPORTS_DIR = ROOT / "reports"


def summary_card(title: str, body: str) -> str:
    return f"""<article class="summary-card"><div class="summary-label">{title}</div><div class="summary-value">{body}</div></article>"""


def unordered(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def render_report(phase_name: str, replacements: dict[str, str]) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    content = template
    content = content.replace("{{PHASE_NAME}}", phase_name)
    content = content.replace("{{PROJECT}}", "CarbonSim Online")
    content = content.replace("{{REPO}}", "carbonsim-online")
    content = content.replace("{{DATE}}", str(date.today()))
    for token, value in replacements.items():
        content = content.replace("{{" + token + "}}", value)
    return content


def render_final_report(report_title: str, replacements: dict[str, str]) -> str:
    template = FINAL_TEMPLATE_PATH.read_text(encoding="utf-8")
    content = template
    content = content.replace("{{REPORT_TITLE}}", report_title)
    content = content.replace("{{PROJECT}}", "CarbonSim Online")
    content = content.replace("{{REPO}}", "carbonsim-online")
    content = content.replace("{{DATE}}", str(date.today()))
    for token, value in replacements.items():
        content = content.replace("{{" + token + "}}", value)
    return content


def phase_one_report() -> str:
    return render_report(
        "phase-one-skeleton-app",
        {
            "INPUT_OUTPUT_CONTENT": "".join(
                [
                    summary_card(
                        "Input",
                        "Phase 1 plan scope, existing research corpus, and an empty repo without application code.",
                    ),
                    summary_card(
                        "Output",
                        "A runnable `oTree` project in `platform/` with room config, session config, participant join flow, facilitator launch control, and a live workshop dashboard.",
                    ),
                    summary_card(
                        "Key Files",
                        "`platform/settings.py`, `platform/carbonsim_phase12/__init__.py`, `platform/carbonsim_phase12/Welcome.html`, `platform/carbonsim_phase12/WorkshopHub.html`",
                    ),
                    summary_card(
                        "Verification",
                        "Unit tests passed and an `oTree` boot check reached the admin/demo surface on a live local server.",
                    ),
                ]
            ),
            "MERMAID_DIAGRAM": """flowchart LR
Repo[Repo with plan and research only] --> Env[Create Python 3.12 venv]
Env --> Install[Install oTree]
Install --> Scaffold[Scaffold platform project and carbonsim app]
Scaffold --> Configure[Add room and session config]
Configure --> UI[Build join page and live workshop hub]
UI --> Verify[Boot local oTree server and confirm app loads]""",
            "MATH_ALGORITHM_SECTION": unordered(
                [
                    "Phase 1 used minimal algorithmic logic: deterministic company assignment from a fixed company library and facilitator assignment to the first participant in session order.",
                    "No market-clearing or abatement math was implemented in this phase; the goal was proving multiplayer workflow and synchronized state delivery.",
                    "Live dashboard updates poll the server every two seconds through `oTree` live messages so the UI reflects the authoritative session state.",
                ]
            ),
            "TOOLS_METHODS": unordered(
                [
                    "Framework: `oTree` 6.0.14 on Python 3.12 inside `.venv`.",
                    "Scaffolding method: `otree startproject platform` and `otree startapp carbonsim_phase12`.",
                    "Interaction method: `Page.live_method` broadcasts one snapshot per participant from server state rather than trusting client-side timers.",
                    "Verification method: `python -m unittest tests.test_engine` plus a scripted `otree devserver` boot check.",
                ]
            ),
            "CHARTS_SECTION": """<div class="empty-state"><strong>No quantitative chart needed.</strong><p>Phase 1 was an infrastructure milestone, so the meaningful result is a working session skeleton rather than numeric output.</p></div>""",
            "LIMITATIONS_ALTERNATIVES": unordered(
                [
                    "The dashboard is intentionally a placeholder and does not yet include abatement, offsets, auctions, or trade interactions.",
                    "The facilitator role is assigned to the first participant for speed; a richer admin-role model can be added later if workshops need stricter separation.",
                    "Second-best alternative: build the same flow in a custom React plus WebSocket stack, but that would add complexity before the core workshop loop is proven.",
                ]
            ),
            "ERRORS_WARNINGS_FLAGS": unordered(
                [
                    "Initial installation attempt failed because the shell mangled the Windows path to the virtualenv Python executable.",
                    "The `oTree` devserver reloader could not find `otree.exe` on Windows unless the virtualenv `Scripts` directory was placed on `PATH`.",
                    "A fresh SQLite database still needed the `PRAGMA user_version` expected by the installed `oTree` build before the boot check would pass.",
                ]
            ),
            "OPEN_QUESTIONS": unordered(
                [
                    "Should facilitator identity remain tied to the first participant or move into an explicit room/admin join workflow?",
                    "Should phase timing continue as polling-based live refresh in V1, or switch to facilitator-driven transitions only?",
                    "Next phase seed: wire the live dashboard to deterministic compliance calculations and an auditable state machine.",
                ]
            ),
        },
    )


def phase_two_report() -> str:
    return render_report(
        "phase-two-compliance-engine",
        {
            "INPUT_OUTPUT_CONTENT": "".join(
                [
                    summary_card(
                        "Input",
                        "Phase 2 requirements for deterministic year flow, allocations, emissions growth, banking, penalties, and auditable state transitions.",
                    ),
                    summary_card(
                        "Output",
                        "A plain Python rules engine driving year start, decision window, compliance review, three-year completion, leaderboard snapshots, and audit events.",
                    ),
                    summary_card(
                        "Key Files",
                        "`platform/carbonsim_phase12/engine.py` and `platform/tests/test_engine.py`",
                    ),
                    summary_card(
                        "Verification",
                        "Seven unit tests cover company generation, allocation initialization, penalty handling, three-year completion, audit logging, dashboard snapshots, and session config registration.",
                    ),
                ]
            ),
            "MERMAID_DIAGRAM": """flowchart LR
Init[Create initial state] --> Start[Start simulation]
Start --> YearStart[Apply allocation and emissions growth]
YearStart --> Window[Decision window countdown]
Window --> Close[Close year]
Close --> Review[Bank surplus and apply penalties]
Review --> Next{Last year reached?}
Next -- No --> YearStart
Next -- Yes --> Complete[Mark session complete and log event]""",
            "MATH_ALGORITHM_SECTION": unordered(
                [
                    "Projected emissions use compound growth: `baseline_emissions * (1 + growth_rate) ** year`.",
                    "Yearly free allocation uses declining allocation factors: year 1 = 0.92, year 2 = 0.88, year 3 = 0.84 of projected emissions.",
                    "Banking rule: `banked_allowances = max(0, allowances - projected_emissions)` after year-end surrender.",
                    "Penalty rule: `penalty_due = max(0, projected_emissions - allowances) * penalty_rate`, with the default penalty rate set to 200 per uncovered allowance.",
                    "The engine is server-authoritative and advances phases only when the current timestamp passes the stored phase deadline.",
                ]
            ),
            "TOOLS_METHODS": unordered(
                [
                    "Implementation method: keep the compliance engine in `engine.py` as plain Python dictionaries and functions so calculations are easy to test outside `oTree`.",
                    "State method: persist the whole session snapshot in `SESSION_FIELDS` as `carbonsim_state`.",
                    "Audit method: append structured events with timestamps, type, year, and human-readable summary after each key state transition.",
                    "Test method: red/green flow using `unittest` before engine implementation, then rerun the suite after integration.",
                ]
            ),
            "CHARTS_SECTION": """<div class="empty-state"><strong>No chart included.</strong><p>The implemented calculations are deterministic and verified through tests, but this phase did not generate session datasets large enough to justify a real chart artifact.</p></div>""",
            "LIMITATIONS_ALTERNATIVES": unordered(
                [
                    "The engine currently uses fixed allocation factors and company archetypes rather than calibration imported from scenario data files.",
                    "Offsets, abatement menus, and auction behavior are intentionally absent because the roadmap puts them after the compliance engine is proven.",
                    "Second-best alternative: embed the rules directly inside page callbacks, but that would make deterministic testing and future calibration much harder.",
                ]
            ),
            "ERRORS_WARNINGS_FLAGS": unordered(
                [
                    "The first red test failed because `carbonsim_phase12.engine` did not yet exist, which confirmed the tests were properly driving the implementation.",
                    "Static analysis inside the editor complained about dynamic config typing in the tests, so the assertions were simplified to concrete values.",
                    "Framework-level `otree test` was less useful for this phase than plain unit tests plus a live boot check because there are no browser bots yet.",
                ]
            ),
            "OPEN_QUESTIONS": unordered(
                [
                    "How should scenario calibration data be externalized so future sectors and workshop variants do not require code edits?",
                    "Should year transitions remain time-driven in later phases, or should the facilitator explicitly close windows for live workshops?",
                    "Next phase seed: add abatement and offset decisions on top of the existing compliance position and audit trail.",
                ]
            ),
        },
    )


def phase_three_report() -> str:
    return render_report(
        "phase-three-abatement-offsets",
        {
            "INPUT_OUTPUT_CONTENT": "".join(
                [
                    summary_card(
                        "Input",
                        "Phase 3 requirements for sector-specific abatement menus, activation timing rules, offset holding and usage constraints, and dashboard decision support.",
                    ),
                    summary_card(
                        "Output",
                        "A decision layer that lets players commit abatement measures, buy offsets, see delayed activation effects, and preview their forward-looking compliance position in the live dashboard.",
                    ),
                    summary_card(
                        "Key Files",
                        "`platform/carbonsim_phase12/engine.py`, `platform/carbonsim_phase12/__init__.py`, `platform/carbonsim_phase12/WorkshopHub.html`, and `platform/tests/test_engine.py`",
                    ),
                    summary_card(
                        "Verification",
                        "Eleven unit tests cover abatement menu generation, immediate and delayed activation, offset-cap usage, and projected dashboard summaries alongside earlier phase behavior.",
                    ),
                ]
            ),
            "MERMAID_DIAGRAM": """flowchart LR
YearStart[Year starts with allocation] --> Window[Decision window opens]
Window --> Abate[Commit abatement measure]
Window --> Offset[Buy offsets]
Abate --> Recalc[Recalculate projected emissions and net position]
Offset --> Recalc
Recalc --> Close[Compliance close]
Close --> Cap[Apply offset usage cap]
Cap --> Penalty[Bank surplus or penalize shortfall]""",
            "MATH_ALGORITHM_SECTION": unordered(
                [
                    "Gross emissions still follow compound growth, but active abatement subtracts a fixed sector-specific reduction before compliance is evaluated.",
                    "Immediate measures reduce the current year's projected emissions as soon as they are committed; delayed measures move into a pending list and become active at the next year start.",
                    "Offsets can be purchased and held freely in the prototype, but year-end compliance only uses `min(offset_holdings, projected_emissions * offset_usage_cap)`.",
                    "Forward-looking dashboard net position is computed as allowances plus usable offsets minus projected emissions, so players can see whether a decision materially improves compliance before surrender.",
                ]
            ),
            "TOOLS_METHODS": unordered(
                [
                    "Implementation method: extend the plain Python engine rather than burying decision logic inside page handlers.",
                    "UI method: use the existing `live_method` channel so every abatement or offset action immediately rebroadcasts an updated player snapshot.",
                    "State method: keep active and pending abatement IDs separate so next-year activation is deterministic and auditable.",
                    "Verification method: add failing `unittest` cases first for each new behavior, then implement only until the expanded suite passes.",
                ]
            ),
            "CHARTS_SECTION": """<div class="empty-state"><strong>No chart included.</strong><p>Phase 3 produced richer decision logic, but the meaningful proof is deterministic test coverage plus the live dashboard state transitions rather than a fabricated visualization.</p></div>""",
            "LIMITATIONS_ALTERNATIVES": unordered(
                [
                    "Abatement measures use simple fixed reductions and committed costs rather than full MAC curves or scenario file imports.",
                    "Offset purchases do not yet compete in a market; they are a placeholder decision mechanic ahead of auction and trading phases.",
                    "Second-best alternative: keep the dashboard read-only until auctions exist, but that would delay the strategic compliance behavior phase 3 is meant to teach.",
                ]
            ),
            "ERRORS_WARNINGS_FLAGS": unordered(
                [
                    "The first implementation attempt ignored phase 3 decisions because the engine had not advanced into the decision window before processing actions.",
                    "That bug surfaced immediately in the red tests when immediate abatement, offset purchases, and dashboard cost summaries remained unchanged.",
                    "The fix was to advance the authoritative state inside `apply_company_decision` before validating and applying the requested action.",
                ]
            ),
            "OPEN_QUESTIONS": unordered(
                [
                    "Should offset purchases remain a simple fixed-price placeholder through phase 4, or should auctions set the first shared price signal for both allowances and offsets?",
                    "How much sector heterogeneity should move into scenario data before phase 4 and 5 begin adding market interactions?",
                    "Next phase seed: feed the existing compliance engine and decision layer into a sealed-bid auction with holdings and cash settlement.",
                ]
            ),
        },
    )


def phase_four_report() -> str:
    return render_report(
        "phase-four-auction-market",
        {
            "INPUT_OUTPUT_CONTENT": "".join(
                [
                    summary_card(
                        "Input",
                        "Phase 4 requirements for a simple auction market: sealed bids, public results, clearing logic, and settlement into the existing compliance engine.",
                    ),
                    summary_card(
                        "Output",
                        "A sealed-bid uniform-price auction flow with year-start scheduling, facilitator open and clear controls, participant bid submission, deterministic tie handling, and allowance plus cash settlement.",
                    ),
                    summary_card(
                        "Key Files",
                        "`platform/carbonsim_phase12/engine.py`, `platform/carbonsim_phase12/__init__.py`, `platform/carbonsim_phase12/WorkshopHub.html`, and `platform/tests/test_engine.py`",
                    ),
                    summary_card(
                        "Verification",
                        "Fifteen unit tests now cover the earlier phases plus auction schedule generation, bid validation, uniform-price clearing, settlement, and tie behavior.",
                    ),
                ]
            ),
            "MERMAID_DIAGRAM": """flowchart LR
YearStart[Build year auction schedule] --> Open[Facilitator opens auction]
Open --> Bid[Participants submit sealed bids]
Bid --> Order[Sort bids by price then time]
Order --> Clear[Allocate supply and set uniform clearing price]
Clear --> Settle[Update allowances and cash]
Settle --> Broadcast[Show public auction results in dashboard]""",
            "MATH_ALGORITHM_SECTION": unordered(
                [
                    "Year auction supply is derived from a share of the annual cap and split evenly across the configured auctions, with the last auction absorbing rounding differences.",
                    "Bids are ranked by descending price and then ascending submission time, which creates deterministic tie handling when multiple bids sit on the clearing price.",
                    "The clearing price is the lowest accepted winning bid price, and all winners pay that uniform price rather than their individual submitted prices.",
                    "Settlement adds awarded quantity to allowance holdings and subtracts `awarded_quantity * clearing_price` from company cash so the auction immediately changes compliance position.",
                ]
            ),
            "TOOLS_METHODS": unordered(
                [
                    "Implementation method: keep the auction book and results inside the shared engine state so price discovery stays server-authoritative.",
                    "UI method: extend the existing live dashboard with facilitator open and clear buttons plus participant bid-entry controls rather than adding a separate auction page.",
                    "Validation method: reject bids outside the price collar or above available cash before they enter the bid book.",
                    "Test method: write red `unittest` cases first for schedule creation, invalid bids, clearing, settlement, and price-tie behavior, then implement until green.",
                ]
            ),
            "CHARTS_SECTION": """<div class="empty-state"><strong>No chart included.</strong><p>Phase 4 produced a real price-discovery mechanism, but the meaningful artifact here is the deterministic clearing logic and public auction board rather than an invented chart.</p></div>""",
            "LIMITATIONS_ALTERNATIVES": unordered(
                [
                    "The auction market is intentionally simple and facilitator-driven rather than fully time-scheduled inside the year state machine.",
                    "Auctions currently offer a single current-year allowance product and do not yet include future vintages or reserve-price interventions.",
                    "Second-best alternative: jump straight to a continuous order book, but that would add concurrency and fairness complexity before the primary market pattern is proven.",
                ]
            ),
            "ERRORS_WARNINGS_FLAGS": unordered(
                [
                    "The only implementation issue after adding the engine was a test that compared mutated in-place company state rather than storing pre-auction cash first.",
                    "Fixing that assertion confirmed the settlement logic already worked and kept the implementation itself unchanged.",
                    "The auction controls still rely on facilitator actions to open and clear auctions, which is acceptable for testing but worth revisiting for later workshop flow refinement.",
                ]
            ),
            "OPEN_QUESTIONS": unordered(
                [
                    "Should the next phase keep facilitator-managed auction cadence, or should auctions become part of an automatic intra-year schedule?",
                    "Do workshop goals need future-vintage allowances in primary auctions, or is current-year supply enough for V1?",
                    "Next phase seed: add simple bilateral secondary trading on top of the auction-cleared allowance positions and public price signal.",
                ]
            ),
        },
    )


def phase_five_report() -> str:
    return render_report(
        "phase-five-secondary-trading",
        {
            "INPUT_OUTPUT_CONTENT": "".join(
                [
                    summary_card(
                        "Input",
                        "Phase 5 requirements for the simplest V1 secondary market: bilateral trade proposals, responses, settlement validation, and a trade feed.",
                    ),
                    summary_card(
                        "Output",
                        "A server-authoritative bilateral trading layer with proposals, accept and reject responses, expiry handling, holdings and cash checks, settlement, and a public trade feed in the workshop dashboard.",
                    ),
                    summary_card(
                        "Key Files",
                        "`platform/carbonsim_phase12/engine.py`, `platform/carbonsim_phase12/__init__.py`, `platform/carbonsim_phase12/WorkshopHub.html`, and `platform/tests/test_engine.py`",
                    ),
                    summary_card(
                        "Verification",
                        "Twenty unit tests now cover trading proposal creation, acceptance, rejection, expiry, insufficient holdings and cash, and the earlier auction and compliance behavior.",
                    ),
                ]
            ),
            "MERMAID_DIAGRAM": """flowchart LR
Open[Decision window open] --> Propose[Seller proposes bilateral trade]
Propose --> Validate[Server validates holdings and buyer cash]
Validate --> Inbox[Buyer sees trade in inbox]
Inbox --> Accept[Accept trade]
Inbox --> Reject[Reject trade]
Accept --> Settle[Transfer allowances and cash]
Reject --> Close[Mark rejected]
Propose --> Expire[Expire if unanswered]
Settle --> Feed[Publish trade feed update]""",
            "MATH_ALGORITHM_SECTION": unordered(
                [
                    "Trade value is calculated as `quantity * price_per_allowance`, and that full value must be affordable by the buyer at proposal time and again at acceptance time.",
                    "Settlement transfers the proposed allowance quantity from seller to buyer and the total trade value from buyer cash to seller cash in one server-side transaction.",
                    "Trade expiry is time-based: open proposals move to `expired` when the current time passes `expires_at`, preventing stale deals from settling later in the round.",
                    "Compliance position is recalculated for both counterparties immediately after accepted trades so the dashboard reflects the new post-trade exposure without waiting for year-end processing.",
                ]
            ),
            "TOOLS_METHODS": unordered(
                [
                    "Implementation method: keep trade lifecycle state in the shared engine next to auctions so all market actions remain auditable and server-authoritative.",
                    "UI method: add a proposal form, buyer inbox, and public trade feed to the existing live workshop dashboard rather than branching into a separate trading page.",
                    "Validation method: reject proposals when the seller lacks allowances or the buyer lacks cash, and reject duplicate responses once a trade is no longer `proposed`.",
                    "Test method: write red `unittest` cases first for proposal, acceptance, rejection, expiry, and invalid settlement, then implement until the full suite returns green.",
                ]
            ),
            "CHARTS_SECTION": """<div class="empty-state"><strong>No chart included.</strong><p>Phase 5 is about controlled trade lifecycle behavior and settlement integrity, so the highest-value evidence is deterministic test coverage and the public trade feed rather than a synthetic visualization.</p></div>""",
            "LIMITATIONS_ALTERNATIVES": unordered(
                [
                    "The trading layer is intentionally bilateral and simple; there is no matching engine or open order book yet.",
                    "Trades are proposed seller-to-buyer rather than being discovered in a shared request-for-quote interface, which keeps implementation legible but less market-like.",
                    "Second-best alternative: wait until a full exchange exists, but that would postpone the strategic rebalancing behavior phase 5 is meant to introduce after auctions.",
                ]
            ),
            "ERRORS_WARNINGS_FLAGS": unordered(
                [
                    "The only issues in this phase were test-side: one invalid timestamp helper call used `second=60`, and one settlement assertion compared against a mutated in-place object reference.",
                    "Fixing those tests confirmed the trade engine itself already handled expiry and settlement correctly.",
                    "The dashboard now exposes public trade history, but later phases may still choose to make parts of the feed semi-public depending on facilitator goals.",
                ]
            ),
            "OPEN_QUESTIONS": unordered(
                [
                    "Should later versions keep bilateral targeted proposals only, or add a facilitator-mediated request board before considering a full exchange?",
                    "Do workshops need trade cancellation before response, or is proposal plus accept or reject enough for V1?",
                    "Next phase seed: build facilitator controls, participant health views, and export-ready session analytics on top of the now-complete compliance, auction, and bilateral trade loop.",
                ]
            ),
        },
    )


def phase_nine_report() -> str:
    return render_report(
        "phase-nine-session-replay",
        {
            "INPUT_OUTPUT_CONTENT": "".join(
                [
                    summary_card(
                        "Input",
                        "Phase 9 requirements for facilitator-facing replay artifacts: ordered audit timelines, year markers, market-path reconstruction, and export-ready replay payloads.",
                    ),
                    summary_card(
                        "Output",
                        "A server-side replay dataset plus facilitator-panel replay views that show year markers, market path, company replay histories, and recent audit events without requiring raw JSON inspection.",
                    ),
                    summary_card(
                        "Key Files",
                        "`platform/carbonsim_phase12/engine.py`, `platform/carbonsim_phase12/FacilitatorPanel.html`, and `platform/tests/test_engine.py`",
                    ),
                    summary_card(
                        "Verification",
                        "Replay-specific regression coverage now verifies timeline completeness, year marker accuracy, market-path payloads, company replay histories, facilitator snapshots, and enriched export payloads inside the 92-test suite.",
                    ),
                ]
            ),
            "MERMAID_DIAGRAM": """flowchart LR
Audit[Audit log and year results] --> Replay[Build replay timeline]
Replay --> Markers[Aggregate year markers]
Replay --> Market[Extract auction market path]
Replay --> Companies[Collect company replay histories]
Markers --> Panel[Render facilitator replay tables]
Market --> Panel
Companies --> Panel
Panel --> Export[Ship replay in session export]""",
            "MATH_ALGORITHM_SECTION": unordered(
                [
                    "Replay timeline order is deterministic because it uses the existing audit log sequence and assigns a monotonic `step` counter during export generation.",
                    "Year markers aggregate accepted trades, penalties, banked allowances, offset usage, clearing prices, and shocks by tracked simulation year rather than by UI state.",
                    "Market path reconstruction reads the authoritative auction records already persisted in engine state, avoiding any client-derived replay assumptions.",
                    "Company replay paths reuse stored `year_results` so debrief data matches the same surrender, banking, and penalty calculations already proven by earlier phases.",
                ]
            ),
            "TOOLS_METHODS": unordered(
                [
                    "Replay generation stays server-side in `engine.py`, which keeps debrief artifacts consistent with the authoritative audit trail.",
                    "Facilitator rendering uses tables and summary cards in `FacilitatorPanel.html` so the replay remains readable in-browser during live debriefs.",
                    "Export method: `export_session_data` now includes the full replay payload for offline review and downstream analysis.",
                    "Verification method: extend `unittest` coverage for replay timelines, year markers, market paths, company histories, and facilitator snapshot payloads.",
                ]
            ),
            "CHARTS_SECTION": """<div class="empty-state"><strong>No chart included.</strong><p>Phase 9 is primarily about ordered reconstruction and facilitator readability, so the meaningful artifact is the replay dataset and panel presentation rather than a quantitative chart.</p></div>""",
            "LIMITATIONS_ALTERNATIVES": unordered(
                [
                    "Replay is table-based and export-friendly rather than an animated scrubber UI, which keeps the debrief surface simple for workshop facilitators.",
                    "The timeline summarizes events with server-provided text instead of richer natural-language narration; that keeps the output auditable but less story-like.",
                    "Second-best alternative: require facilitators to inspect raw export JSON in external tools, but that would undermine the goal of in-product debriefing.",
                ]
            ),
            "ERRORS_WARNINGS_FLAGS": unordered(
                [
                    "The main phase-9 gap was not missing replay generation logic but incomplete facilitator surfacing of market path and company replay views.",
                    "That gap was closed by extending the facilitator panel to render both payloads directly from the replay snapshot instead of leaving them export-only.",
                    "Replay coverage now sits inside the full platform suite, so regressions in later phases should be caught without a separate manual replay harness.",
                ]
            ),
            "OPEN_QUESTIONS": unordered(
                [
                    "Should a later version add a visual scrubber or chart-based replay once real facilitator feedback shows the tables are not enough?",
                    "Should replay events be grouped into facilitator-curated narrative chapters for larger workshops with more audit noise?",
                    "Next phase seed: deepen post-session analytics so facilitators can explain not just what happened, but where costs and pressure concentrated.",
                ]
            ),
        },
    )


def phase_ten_report() -> str:
    return render_report(
        "phase-ten-facilitator-analytics",
        {
            "INPUT_OUTPUT_CONTENT": "".join(
                [
                    summary_card(
                        "Input",
                        "Phase 10 requirements for stronger facilitator analytics: market summaries, sector breakdowns, year metrics, company cost drivers, and export-ready analytics payloads.",
                    ),
                    summary_card(
                        "Output",
                        "Expanded analytics generation plus facilitator-panel views that surface market stat cards, sector and year tables, company cost analytics, and decision-count summaries directly inside the simulator.",
                    ),
                    summary_card(
                        "Key Files",
                        "`platform/carbonsim_phase12/engine.py`, `platform/carbonsim_phase12/FacilitatorPanel.html`, and `platform/tests/test_engine.py`",
                    ),
                    summary_card(
                        "Verification",
                        "Analytics-specific regression coverage now checks market metrics, sector breakdowns, year metrics, company cost rows, decision-count payloads, facilitator snapshots, and export enrichment inside the 92-test suite.",
                    ),
                ]
            ),
            "MERMAID_DIAGRAM": """flowchart LR
State[Authoritative engine state] --> Metrics[Aggregate market metrics]
State --> Sector[Aggregate sector breakdown]
State --> Years[Aggregate year metrics]
State --> Costs[Aggregate company cost drivers]
State --> Decisions[Count decision events]
Metrics --> Snapshot[Build facilitator snapshot]
Sector --> Snapshot
Years --> Snapshot
Costs --> Snapshot
Decisions --> Snapshot
Snapshot --> Panel[Render analytics cards and tables]
Snapshot --> Export[Ship analytics in export payload]""",
            "MATH_ALGORITHM_SECTION": unordered(
                [
                    "Market metrics aggregate auction awards, accepted trade quantities and values, average clearing price across cleared auctions, offsets purchased, abatement actions, and applied shocks.",
                    "Sector breakdown rolls up current company state by sector, including projected emissions, allowances, banked allowances, offset holdings, penalties, and active abatement counts.",
                    "Year metrics combine replay year markers with stored company `year_results`, which keeps annual totals aligned with already-tested compliance calculations.",
                    "Net company compliance cost is computed as abatement cost plus offset spend plus auction spend plus trade purchases plus penalties minus trade sales.",
                ]
            ),
            "TOOLS_METHODS": unordered(
                [
                    "Analytics generation lives in `build_session_analytics` so the facilitator view and export payload share one calculation path.",
                    "Facilitator rendering uses compact stat cards plus structured tables to keep debrief discussion usable on a single page.",
                    "Decision-count summaries are derived from the audit log rather than page interactions, which makes the analytics resilient to future UI changes.",
                    "Verification method: add regression tests for analytics aggregation and payload structure, then rerun the full engine and deployment suite.",
                ]
            ),
            "CHARTS_SECTION": """<div class="chart-frame"><div class="viz-frame" style="height:320px;"><canvas id="phase10Chart"></canvas></div></div>
<script>
Chart.defaults.devicePixelRatio = 1;
Chart.defaults.animation = false;
Chart.defaults.resizeDelay = 150;
Chart.defaults.normalized = true;
Chart.defaults.maintainAspectRatio = false;
const phase10Ctx = document.getElementById('phase10Chart');
if (phase10Ctx) {
  new Chart(phase10Ctx, {
    type: 'bar',
    data: {
      labels: ['Market metrics', 'Sector breakdown', 'Year metrics', 'Company costs', 'Decision counts'],
      datasets: [{
        label: 'Phase 10 analytics surfaces',
        data: [1, 1, 1, 1, 1],
        backgroundColor: ['#00f5ff', '#39ff14', '#00f5ff', '#39ff14', '#00f5ff']
      }]
    },
    options: {
      animation: false,
      resizeDelay: 150,
      normalized: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Implemented analytics views delivered in phase 10' }
      },
      scales: {
        y: { beginAtZero: true, max: 1.2, ticks: { stepSize: 1 } }
      }
    }
  });
}
</script>""",
            "LIMITATIONS_ALTERNATIVES": unordered(
                [
                    "Analytics remain descriptive and workshop-focused rather than predictive; there is no comparative benchmarking across many sessions yet.",
                    "The facilitator view emphasizes tables for traceability instead of denser dashboard visualizations, which favors clarity over visual richness.",
                    "Second-best alternative: leave analytics in exported JSON only, but that would force facilitators into external tooling during debriefs.",
                ]
            ),
            "ERRORS_WARNINGS_FLAGS": unordered(
                [
                    "The only implementation failure came from a new regression asserting an event type that the analytics-rich fixture never emits because it begins after simulation start.",
                    "Fixing that test to assert on actual emitted events kept the production analytics code unchanged and clarified the fixture lifecycle.",
                    "The expanded analytics surface now depends on payload size staying manageable, which is acceptable for the workshop-scale participant counts targeted by V1.",
                ]
            ),
            "OPEN_QUESTIONS": unordered(
                [
                    "Should future iterations compare multiple sessions or scenarios side by side for facilitator calibration across workshops?",
                    "Do facilitators need chart-heavy visuals, or are the current tables and summary cards sufficient for live debriefs?",
                    "Next phase seed: use pilot feedback to decide whether to deepen facilitator analysis, improve replay UX, or move into broader V2 scenario and market expansion.",
                ]
            ),
        },
    )


def final_report() -> str:
    return render_final_report(
        "carbonsim-online-v1-final",
        {
            "ONE_LINE_TAKEAWAY": "The repository now delivers a workshop-ready Vietnam-aligned ETS simulator through phases 1 to 10, with replay and analytics built into the facilitator workflow rather than left to external analysis.",
            "EXECUTIVE_SUMMARY": '<div class="summary-grid"><div class="subcard"><h3>What was built</h3><p>The project progressed from research framing and an oTree multiplayer skeleton to a full compliance-market simulator with abatement, offsets, auctions, bilateral trading, facilitator controls, deployment hardening, replay, and analytics.</p></div><div class="subcard"><h3>What matters now</h3><p>The simulator is usable for facilitator-led workshops because session operation, recovery, export, replay, and debrief analytics are all available inside the product.</p></div><div class="subcard"><h3>Recommended direction</h3><p>Use this build for pilot workshops, collect facilitator feedback on replay and analytics usability, and only then decide whether V2 should invest in richer market microstructure or richer debrief tooling.</p></div><div class="subcard"><h3>Evidence</h3><p>The platform passes 92 automated tests covering the engine, deployment, replay, analytics, exports, and facilitator snapshot payloads.</p></div></div>',
            "BACKGROUND_OBJECTIVE": '<div class="narrative"><p>CarbonSim Online was scoped as a Vietnam-focused ETS training platform, not a generic trading game. The central objective was to build a compliance-first simulator that helps participants understand allocations, emissions growth, abatement, offsets, allowance scarcity, trading, banking, surrender, and penalties across a compressed three-year workshop flow.</p><p>The product strategy favored oTree because it already provides multiplayer sessions, admin surfaces, and synchronized interactions. That made it possible to keep the implementation focused on the rules engine and facilitator experience rather than infrastructure reinvention.</p></div>',
            "INPUTS_SCOPE": '<div class="dual-grid"><div class="subcard"><h3>Primary inputs</h3><ul><li>`plan/project-plan.md` as the execution roadmap.</li><li>`research/` reports as the Vietnam ETS source-of-truth corpus.</li><li>`AGENTS.md` as the project operating guide and scope constraint.</li><li>The active implementation and test suite in `platform/`.</li></ul></div><div class="subcard"><h3>In scope</h3><ul><li>Workshop session flow for 10-20 participants.</li><li>Compliance engine, abatement, offsets, auctions, and bilateral trades.</li><li>Facilitator controls, export, deployment hardening, replay, and analytics.</li></ul><h3>Out of scope</h3><ul><li>Continuous order-book exchange behavior.</li><li>Derivatives or speculative financial products.</li><li>Large-scale production infrastructure beyond pilot readiness.</li></ul></div></div>',
            "ASSUMPTIONS_CONSTRAINTS": '<div class="dual-grid"><div class="subcard"><h3>Assumptions</h3><ul><li>V1 remains compliance-first and facilitator-led.</li><li>Server-authoritative logic is the right default for fairness and auditability.</li><li>Three compressed years are enough to teach scarcity, banking, and penalties.</li></ul></div><div class="subcard"><h3>Constraints</h3><ul><li>`oTree` compatibility required Python 3.12 rather than the machine default Python 3.14.</li><li>Workshop usability favored explainable mechanics over realistic exchange complexity.</li><li>Facilitator debrief surfaces had to work inside the product, not through separate analyst tooling.</li></ul></div></div>',
            "METHODOLOGY": '<div class="phase-grid"><div class="subcard"><h3>Build order</h3><p>The implementation followed the roadmap: multiplayer skeleton first, then the compliance engine, then strategic decisions, market mechanics, facilitator operations, deployment readiness, replay, and analytics.</p></div><div class="subcard"><h3>Verification style</h3><p>New logic was added under regression coverage, with the engine kept in plain Python to make deterministic testing straightforward. The current suite covers 92 tests across engine and deployment paths.</p></div><div class="subcard"><h3>Design principle</h3><p>The core rule was to make trading support compliance learning, not dominate it. That kept the simulator legible for workshops and avoided premature exchange-like complexity.</p></div><div class="subcard"><h3>Operational method</h3><p>Facilitator functionality was treated as a first-class product surface, resulting in built-in controls, recovery paths, replay, analytics, and export rather than relegating workshop operations to manual workarounds.</p></div></div>',
            "PHASE_ANALYSIS": '<div class="narrative"><p>Phases 1 and 2 established the product spine: a live oTree workshop flow and a deterministic compliance engine with auditable state transitions. Phases 3 through 5 layered the decision and market mechanics participants need to learn from: abatement, offsets, auctions, and simple bilateral trades.</p><p>Phase 6 shifted focus to facilitator operations with pause, resume, export, participant visibility, and summary generation. Phase 7 improved workshop robustness through scenarios, bots, and shocks, while phase 8 hardened the system for pilot deployment with Docker, operational checks, and reconnection support.</p><p>Phases 9 and 10 completed the post-session workflow. Replay now reconstructs session events, market path, and company histories from the audit trail, and analytics now summarize market activity, sector pressure, year outcomes, and company cost drivers directly inside the facilitator panel.</p></div>',
            "FINDINGS_RECOMMENDATION": '<div class="dual-grid"><div class="subcard"><h3>Findings</h3><ul><li>The compliance-first architecture holds together across the full three-year simulation.</li><li>Facilitator workflow is now operationally credible because control, recovery, replay, analytics, and export are all present.</li><li>The project avoided unnecessary exchange complexity while still delivering meaningful market behavior through auctions and bilateral trading.</li></ul></div><div class="subcard"><h3>Recommendation</h3><p>Move into pilot workshops with the current build, use facilitator feedback to evaluate whether replay and analytics are sufficient in practice, and delay any order-book or heavier market features until that evidence shows a clear need.</p></div></div>',
            "IMPLEMENTATION_PATH": '<div class="dual-grid"><div class="subcard"><h3>Immediate path</h3><ol><li>Run pilot sessions using the existing scenario configs and facilitator runbook.</li><li>Capture qualitative facilitator feedback on replay readability and analytics usefulness.</li><li>Review exports and audit trails after completed sessions to identify recurring blind spots.</li></ol></div><div class="subcard"><h3>Likely next build options</h3><ol><li>Refine replay UX if facilitators need more guided debrief flow.</li><li>Expand analytics only if pilot feedback shows missing sector, year, or company views.</li><li>Consider richer market mechanics only if current auctions plus bilateral trades fail to create the intended learning outcomes.</li></ol></div></div>',
            "RISKS_OPEN_QUESTIONS": '<div class="dual-grid"><div class="subcard"><h3>Risks</h3><ul><li>Replay and analytics are still workshop-scale surfaces and may need refinement after real facilitator usage.</li><li>Market behavior remains intentionally simple; some advanced ETS training needs may eventually exceed the current design.</li><li>Operational quality now depends on following the runbook and deployment setup correctly in live sessions.</li></ul></div><div class="subcard"><h3>Open questions</h3><ul><li>Are the current replay tables sufficient, or should the debrief move toward a more visual timeline?</li><li>Should analytics evolve toward cross-session comparison after the first pilot wave?</li><li>Will pilot workshops justify deeper scenario breadth before deeper market complexity?</li></ul></div></div>',
            "APPENDICES_EVIDENCE": '<div class="appendix-grid"><div class="subcard"><h3>Key evidence</h3><ul><li>92 automated tests pass across engine and deployment modules.</li><li>Replay is included in facilitator snapshots and session export payloads.</li><li>Analytics is included in facilitator snapshots and session export payloads.</li><li>Deployment guidance and operations runbook are documented in `platform/FACILITATOR_RUNBOOK.md` and `README.md`.</li></ul></div><div class="subcard"><h3>Glossary</h3><ul><li><strong>Allocation:</strong> free allowances assigned at the start of a year.</li><li><strong>Banking:</strong> carrying unused allowances into future years.</li><li><strong>Offset cap:</strong> limit on how much compliance can be met with offsets.</li><li><strong>Replay:</strong> ordered reconstruction of workshop events for debriefing.</li><li><strong>Analytics:</strong> facilitator-oriented summaries of market, sector, year, and company outcomes.</li></ul></div></div>',
            "OPTIONAL_MERMAID_BLOCK": '<div class="diagram-frame"><div class="mermaid">flowchart LR\nResearch[Research and product framing] --> Skeleton[Session scaffold]\nSkeleton --> Engine[Compliance engine]\nEngine --> Decisions[Abatement and offsets]\nDecisions --> Market[Auctions and bilateral trades]\nMarket --> Ops[Facilitator controls and deployment]\nOps --> Debrief[Replay and analytics]\nDebrief --> Pilot[Pilot-ready workshop service]</div></div>',
            "OPTIONAL_CHARTS_BLOCK": "<div class=\"chart-frame\"><div class=\"viz-frame\" style=\"height:320px;\"><canvas id=\"finalPhaseChart\"></canvas></div></div><script>Chart.defaults.devicePixelRatio = 1; Chart.defaults.animation = false; Chart.defaults.resizeDelay = 150; Chart.defaults.normalized = true; Chart.defaults.maintainAspectRatio = false; const finalCtx = document.getElementById('finalPhaseChart'); if (finalCtx) { new Chart(finalCtx, { type: 'bar', data: { labels: ['Ph1-2 Core', 'Ph3-5 Market', 'Ph6-8 Operations', 'Ph9 Replay', 'Ph10 Analytics'], datasets: [{ label: 'Delivered phase groups', data: [1, 1, 1, 1, 1], backgroundColor: ['#9d6b37', '#3b6f76', '#9d6b37', '#3b6f76', '#9d6b37'] }] }, options: { animation: false, resizeDelay: 150, normalized: true, maintainAspectRatio: false, plugins: { legend: { display: false }, title: { display: true, text: 'Delivered capability groups across the roadmap' } }, scales: { y: { beginAtZero: true, max: 1.2, ticks: { stepSize: 1 } } } } }); }</script>",
        },
    )


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = str(date.today())
    outputs = {
        REPORTS_DIR / f"{today}-phase-one-skeleton-app.html": phase_one_report(),
        REPORTS_DIR / f"{today}-phase-two-compliance-engine.html": phase_two_report(),
        REPORTS_DIR
        / f"{today}-phase-three-abatement-offsets.html": phase_three_report(),
        REPORTS_DIR / f"{today}-phase-four-auction-market.html": phase_four_report(),
        REPORTS_DIR / f"{today}-phase-five-secondary-trading.html": phase_five_report(),
        REPORTS_DIR / f"{today}-phase-nine-session-replay.html": phase_nine_report(),
        REPORTS_DIR
        / f"{today}-phase-ten-facilitator-analytics.html": phase_ten_report(),
        REPORTS_DIR / f"{today}-final-carbonsim-online-v1.html": final_report(),
    }
    for path, html in outputs.items():
        path.write_text(html, encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
