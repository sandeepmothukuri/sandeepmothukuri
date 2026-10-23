#!/usr/bin/env python3
"""Render the compact top-community-driver SVG from repository traffic history.

Set metrics/dashboard.json mode to "manual" to use the editable values there.
In "automatic" mode, totals are recalculated from metrics/history.json.
"""
from __future__ import annotations
import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER = "sandeepmothukuri"
CONFIG_PATH = ROOT / "metrics" / "dashboard.json"
HISTORY_PATH = ROOT / "metrics" / "history.json"
OUTPUT_PATH = ROOT / "assets" / "top-community-driver.svg"

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def traffic_totals(history: dict, repo: str) -> tuple[int, int]:
    today = dt.datetime.now(dt.timezone.utc).date()
    cutoff = today - dt.timedelta(days=29)
    rows = history.get("repos", {}).get(repo, [])
    totals = {"views": 0, "clones": 0}
    for row in rows:
        try:
            day = dt.date.fromisoformat(str(row.get("date", ""))[:10])
        except ValueError:
            continue
        if cutoff <= day <= today:
            totals["views"] += int(row.get("views", 0) or 0)
            totals["clones"] += int(row.get("clones", 0) or 0)
    return totals["clones"], totals["views"]

def build_svg(repo: str, clones: int, views: int) -> str:
    title = "Evidence-Driven SOC Platform"
    url = f"https://github.com/{OWNER}/{repo}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="172" viewBox="0 0 900 172" role="img" aria-labelledby="title desc">
  <title id="title">Top Community Driver — 30-day repository metrics</title>
  <desc id="desc">{html.escape(title)} with {clones} clones and {views} views in the last 30 days.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1728"/><stop offset="1" stop-color="#101f35"/></linearGradient>
    <linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#818cf8"/></linearGradient>
    <style>
      .font{{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Arial,sans-serif}}
      .main{{fill:#f8fafc}} .muted{{fill:#9fb1c7}}
      .label{{fill:#8ea4bd;font-size:10px;font-weight:750;letter-spacing:1.2px}}
      .value{{fill:#f8fafc;font-size:25px;font-weight:800}}
    </style>
  </defs>
  <rect x="1" y="1" width="898" height="170" rx="15" fill="url(#bg)" stroke="#28435f"/>
  <rect x="1" y="1" width="898" height="3" rx="1.5" fill="url(#line)"/>
  <g class="font">
    <circle cx="29" cy="29" r="13" fill="#302817" stroke="#b8872c"/>
    <path d="M23 23h3l1.5 3h3L32 23h3l-1.5 8h-9z" fill="#fbbf24"/><path d="M25 32h6l-1 3h-4z" fill="#f59e0b"/>
    <text x="50" y="26" class="main" font-size="16" font-weight="800">Top Community Driver</text>
    <text x="50" y="43" class="muted" font-size="10.5">LAST 30 DAYS · REPOSITORY TELEMETRY</text>
    <rect x="22" y="58" width="856" height="1" fill="#233951"/>
    <text x="24" y="80" class="label">#1 REPOSITORY</text>
    <text x="24" y="103" class="main" font-size="17" font-weight="750">{html.escape(title)}</text>
    <text x="24" y="121" class="muted" font-size="11.5">Evidence-driven investigation &amp; alert triage</text>
    <a href="{url}"><text x="24" y="146" fill="#7dd3fc" font-size="11.5" font-weight="700">View repository ↗</text></a>
    <rect x="516" y="72" width="157" height="77" rx="10" fill="#171b38" stroke="#51449a"/>
    <text x="532" y="91" class="label">GIT CLONES</text><text x="532" y="121" class="value">{clones:,}</text><text x="532" y="138" class="muted" font-size="10.5">Last 30 days</text>
    <path d="M622 132l8 -8 8 3 8 -13 8 5 7 -10" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <rect x="687" y="72" width="191" height="77" rx="10" fill="#0d2b2b" stroke="#18765e"/>
    <text x="703" y="91" class="label">REPOSITORY VIEWS</text><text x="703" y="121" class="value">{views:,}</text><text x="703" y="138" class="muted" font-size="10.5">Last 30 days</text>
    <path d="M823 132l8 -5 8 2 8 -12 8 4 8 -11" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>
'''

def main() -> None:
    config = load_json(CONFIG_PATH)
    repo = config.get("repository", "Evidence-Driven-SOC-Platform")
    if config.get("mode", "automatic").lower() == "manual":
        manual = config.get("manual", {})
        clones = max(0, int(manual.get("clones_30d", 0)))
        views = max(0, int(manual.get("views_30d", 0)))
    else:
        history = load_json(HISTORY_PATH)
        clones, views = traffic_totals(history, repo)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_svg(repo, clones, views), encoding="utf-8")
    print(f"Rendered {OUTPUT_PATH.relative_to(ROOT)}: {clones} clones, {views} views (30d)")

if __name__ == "__main__":
    main()
