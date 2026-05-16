#!/usr/bin/env python3
"""Render daily + 30-day metric badges into README.md between marker comments.

Markers:
    <!-- PROFILE-VIEWS START --> ... <!-- PROFILE-VIEWS END -->
    <!-- REPO-METRICS:<repo> START --> ... <!-- REPO-METRICS:<repo> END -->

Only the content between markers changes. Run with --check to diff without writing.
"""
from __future__ import annotations
import json
import re
import sys
import difflib
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
HIST = ROOT / "metrics" / "history.json"

LABEL_COLOR = "132f4c"


def badge(label: str, value: str, color: str) -> str:
    return (
        f'<img src="https://img.shields.io/badge/'
        f'{quote(label)}-{quote(str(value))}-{color}'
        f'?style=flat-square&labelColor={LABEL_COLOR}" alt="{label}: {value}">'
    )


def last_n_sum(rows: list[dict], key: str, n: int = 30) -> int:
    return sum(int(r.get(key, 0) or 0) for r in rows[-n:])


def latest(rows: list[dict], key: str, default: int = 0) -> int:
    return int(rows[-1].get(key, default)) if rows else default


def replace_block(text: str, marker: str, new_inner: str) -> str:
    start = f"<!-- {marker} START -->"
    end = f"<!-- {marker} END -->"
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    replacement = f"{start}\n{new_inner}\n{end}"
    new_text, n = pattern.subn(replacement, text)
    if n == 0:
        print(f"WARN: marker {marker} not found in README", file=sys.stderr)
    return new_text


def render_profile_block(hist: dict) -> str:
    rows = hist.get("profile_views", [])
    total = latest(rows, "total")
    daily = latest(rows, "daily")
    monthly = last_n_sum(rows, "daily", 30)
    return "  " + "\n  ".join([
        badge("Profile views", f"{total:,}", "3fb950"),
        badge("Last 30 days", f"{monthly:,}", "36d1dc"),
        badge("Today", f"{daily:,}", "ffcf5a"),
    ])


def render_repo_block(repo: str, rows: list[dict]) -> str:
    if not rows:
        return (
            "<sub>📊 metrics collecting — first snapshot pending</sub>"
        )
    v_daily = latest(rows, "views")
    v_month = last_n_sum(rows, "views", 30)
    c_daily = latest(rows, "clones")
    c_month = last_n_sum(rows, "clones", 30)
    stars = latest(rows, "stars")
    forks = latest(rows, "forks")
    # star/fork delta over 30 days
    if len(rows) >= 2:
        star_delta = stars - int(rows[max(0, len(rows) - 31)].get("stars", stars))
        fork_delta = forks - int(rows[max(0, len(rows) - 31)].get("forks", forks))
    else:
        star_delta = fork_delta = 0
    star_str = f"{stars} (+{star_delta}/30d)" if star_delta >= 0 else f"{stars} ({star_delta}/30d)"
    fork_str = f"{forks} (+{fork_delta}/30d)" if fork_delta >= 0 else f"{forks} ({fork_delta}/30d)"
    return "<sub>" + " ".join([
        badge("👁 views", f"{v_daily} today · {v_month} / 30d", "3fb950"),
        badge("📥 clones", f"{c_daily} today · {c_month} / 30d", "36d1dc"),
        badge("⭐ stars", star_str, "ffcf5a"),
        badge("🍴 forks", fork_str, "a371f7"),
    ]) + "</sub>"


def main() -> int:
    check = "--check" in sys.argv

    hist = json.loads(HIST.read_text(encoding="utf-8"))
    original = README.read_text(encoding="utf-8")
    text = original

    text = replace_block(text, "PROFILE-VIEWS", render_profile_block(hist))

    for repo, rows in hist.get("repos", {}).items():
        text = replace_block(text, f"REPO-METRICS:{repo}", render_repo_block(repo, rows))

    # Also handle repos that exist as markers in README but haven't been snapshotted yet
    for m in re.finditer(r"<!-- REPO-METRICS:([^\s]+) START -->", text):
        repo = m.group(1)
        if repo not in hist.get("repos", {}):
            text = replace_block(text, f"REPO-METRICS:{repo}", render_repo_block(repo, []))

    if text == original:
        print("No changes.")
        return 0

    if check:
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            text.splitlines(keepends=True),
            fromfile="README.md",
            tofile="README.md (rendered)",
        )
        sys.stdout.writelines(diff)
        return 0

    README.write_text(text, encoding="utf-8")
    print("README.md updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
