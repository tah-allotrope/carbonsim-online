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


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = str(date.today())
    outputs = {
        REPORTS_DIR / f"{today}-phase-one-skeleton-app.html": phase_one_report(),
        REPORTS_DIR / f"{today}-phase-two-compliance-engine.html": phase_two_report(),
        REPORTS_DIR
        / f"{today}-phase-three-abatement-offsets.html": phase_three_report(),
        REPORTS_DIR / f"{today}-phase-four-auction-market.html": phase_four_report(),
    }
    for path, html in outputs.items():
        path.write_text(html, encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
