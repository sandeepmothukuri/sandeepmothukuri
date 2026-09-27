#!/usr/bin/env python3
"""Calendar-accurate profile metrics renderer with verified traffic baselines.

Also patches the legacy renderer's leaderboard so the profile's Top repositories
section is recalculated every day from the actual 30-day traffic window.
"""
from __future__ import annotations

import datetime
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / ".github" / "scripts" / "render-metrics.py"
BASELINE = ROOT / "metrics" / "traffic-baseline.json"

spec = importlib.util.spec_from_file_location("legacy_renderer", TARGET)
renderer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(renderer)


def calendar_window(rows: list[dict], days: int = 30) -> list[dict]:
    today = datetime.date.today()
    by_date: dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        d = str(row.get("date", ""))[:10]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            by_date[d] = row
    return [
        by_date.get((today - datetime.timedelta(days=i)).isoformat(), {})
        for i in range(days - 1, -1, -1)
    ]


def load_baselines() -> dict:
    if not BASELINE.exists():
        return {}
    try:
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def repo_traffic_30d(repo: str, rows: list[dict], baseline_data: dict) -> tuple[int, int]:
    """Return calendar-accurate 30d views/clones, including verified baselines."""
    window = calendar_window(rows, 30)
    baseline = baseline_data.get("repos", {}).get(repo, {})
    baseline_end = str(baseline_data.get("window_end", ""))[:10]

    if baseline and baseline_end:
        views = int(baseline.get("views", 0) or 0)
        clones = int(baseline.get("clones", 0) or 0)
        for row in window:
            d = str(row.get("date", ""))[:10]
            if d and d > baseline_end:
                views += int(row.get("views", 0) or 0)
                clones += int(row.get("clones", 0) or 0)
        return views, clones

    return (
        sum(int(row.get("views", 0) or 0) for row in window),
        sum(int(row.get("clones", 0) or 0) for row in window),
    )


def render_repo_block(repo: str, rows: list[dict]) -> str:
    baseline_data = load_baselines()
    baseline = baseline_data.get("repos", {}).get(repo, {})
    baseline_end = str(baseline_data.get("window_end", ""))[:10]

    window = calendar_window(rows, 30)
    today_row = window[-1] if window else {}
    available = [r for r in window if r]
    latest = available[-1] if available else {}

    if baseline and baseline_end:
        views_30d = int(baseline.get("views", 0) or 0)
        clones_30d = int(baseline.get("clones", 0) or 0)
        for row in window:
            d = str(row.get("date", ""))[:10]
            if d and d > baseline_end:
                views_30d += int(row.get("views", 0) or 0)
                clones_30d += int(row.get("clones", 0) or 0)
        views_today = int(today_row.get("views", 0) or 0)
        clones_today = int(today_row.get("clones", 0) or 0)
    else:
        views_today = int(today_row.get("views", 0) or 0)
        clones_today = int(today_row.get("clones", 0) or 0)
        views_30d = sum(int(r.get("views", 0) or 0) for r in window)
        clones_30d = sum(int(r.get("clones", 0) or 0) for r in window)

    stars = int(latest.get("stars", 0) or 0)
    forks = int(latest.get("forks", 0) or 0)
    first = available[0] if available else {}
    star_delta = stars - int(first.get("stars", stars) or stars) if first else 0
    fork_delta = forks - int(first.get("forks", forks) or forks) if first else 0

    star_str = f"{stars} (+{star_delta}/30d)" if star_delta >= 0 else f"{stars} ({star_delta}/30d)"
    fork_str = f"{forks} (+{fork_delta}/30d)" if fork_delta >= 0 else f"{forks} ({fork_delta}/30d)"

    return "<sub>" + " ".join([
        renderer.badge("👁 views", f"{views_today} today · {views_30d} / last 30d", "3fb950"),
        renderer.badge("📥 clones", f"{clones_today} today · {clones_30d} / last 30d", "36d1dc"),
        renderer.badge("⭐ stars", star_str, "ffcf5a"),
        renderer.badge("🍴 forks", fork_str, "a371f7"),
    ]) + "</sub>"


def render_top_repo_block(hist: dict) -> str:
    """Render the top three repositories by combined 30-day views + clones.

    The ranking is recalculated every daily run. Ties are resolved by clones,
    then views, then repository name. Verified traffic baselines are included.
    """
    baseline_data = load_baselines()
    ranked: list[tuple[int, int, int, str]] = []

    for repo, rows in hist.get("repos", {}).items():
        views, clones = repo_traffic_30d(repo, rows, baseline_data)
        if views == 0 and clones == 0 and not rows:
            continue
        score = views + clones
        ranked.append((score, clones, views, repo))

    if not ranked:
        return "<sub>Leaderboard pending — first traffic snapshot still collecting.</sub>"

    ranked.sort(key=lambda item: (-item[0], -item[1], -item[2], item[3].lower()))
    badges = []
    for rank, (score, clones, views, repo) in enumerate(ranked[:3], start=1):
        metric = f"{views} views · {clones} clones"
        badges.append(
            f'<a href="https://github.com/{renderer.OWNER}/{repo}">'
            f'{renderer.badge(f"#{rank} {repo}", metric, "1f6feb")}</a>'
        )

    return (
        '<p align="center">\n'
        '<sub>🏆 <b>Top repositories</b> · last 30 days · ranked by views + clones</sub><br>\n'
        + "  ".join(badges)
        + '\n</p>'
    )


renderer.render_repo_block = render_repo_block
renderer.render_top_repo_block = render_top_repo_block
renderer.main()
