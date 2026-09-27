#!/usr/bin/env python3
"""Calendar-accurate wrapper for the profile metrics renderer.

The existing renderer historically used the last 30 stored snapshots. This
wrapper keeps the existing README rendering logic but replaces repository
traffic calculations with the exact calendar window: today + previous 29 days.
Missing snapshot dates count as zero, which is important for newly tracked repos.
"""
from __future__ import annotations

import datetime
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / ".github" / "scripts" / "render-metrics.py"

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


def render_repo_block(repo: str, rows: list[dict]) -> str:
    if not rows:
        return "<sub>📊 metrics collecting — first snapshot pending</sub>"

    window = calendar_window(rows, 30)
    today_row = window[-1] if window else {}
    available = [r for r in window if r]
    latest = available[-1] if available else {}
    first = available[0] if available else {}

    views_today = int(today_row.get("views", 0) or 0)
    clones_today = int(today_row.get("clones", 0) or 0)
    views_30d = sum(int(r.get("views", 0) or 0) for r in window)
    clones_30d = sum(int(r.get("clones", 0) or 0) for r in window)
    stars = int(latest.get("stars", 0) or 0)
    forks = int(latest.get("forks", 0) or 0)
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


renderer.render_repo_block = render_repo_block
renderer.main()
