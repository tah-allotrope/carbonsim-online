#!/usr/bin/env python3
"""Render a phase or final report from the report skill templates."""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path("C:/Users/tukum/.config/opencode/skills/report")
REPORTS_DIR = Path(__file__).parent.parent / "reports"


def sanitize_kebab(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def render(template_path: Path, tokens: dict[str, str], out_path: Path) -> None:
    html = template_path.read_text(encoding="utf-8")
    for key, value in tokens.items():
        html = html.replace(f"{{{{{key}}}}}", value)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"rendered {out_path}")


def phase_report(phase_name: str, content: dict[str, str]) -> Path:
    template = SKILL_DIR / "assets" / "report-template.html"
    today = datetime.now().strftime("%Y-%m-%d")
    safe_name = sanitize_kebab(phase_name)
    out = REPORTS_DIR / f"{today}-{safe_name}.html"
    tokens = {
        "PHASE_NAME": phase_name,
        "DATE": today,
        "PROJECT": "CarbonSim Online",
        "REPO": "carbonsim-online",
        **content,
    }
    render(template, tokens, out)
    return out


def final_report(plan_path: Path, report_name: str, content: dict[str, str]) -> Path:
    template = SKILL_DIR / "assets" / "final-report-template.html"
    today = datetime.now().strftime("%Y-%m-%d")
    safe_name = sanitize_kebab(report_name)
    out = REPORTS_DIR / f"{today}-final-{safe_name}.html"
    tokens = {
        "REPORT_TITLE": report_name,
        "DATE": today,
        "PROJECT": "CarbonSim Online",
        "REPO": "carbonsim-online",
        **content,
    }
    render(template, tokens, out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["phase", "final"])
    parser.add_argument("--name", required=True)
    parser.add_argument("--plan", default="")
    parser.add_argument("--tokens", default="", help="key=value,key=value")
    args = parser.parse_args()

    extra = {}
    if args.tokens:
        for pair in args.tokens.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                extra[k.strip()] = v.strip()

    if args.mode == "phase":
        phase_report(args.name, extra)
    else:
        final_report(Path(args.plan), args.name, extra)


if __name__ == "__main__":
    main()
