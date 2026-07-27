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
import io
import os

# Ensure stdout can handle emoji/Unicode on Windows (cp1252 default would crash).
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import difflib
import datetime
import urllib.request
from pathlib import Path
from urllib.parse import quote

OWNER = "sandeepmothukuri"
GH_JOIN = datetime.datetime(2026, 2, 4, 16, 56, 35, tzinfo=datetime.timezone.utc)

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
HIST = ROOT / "metrics" / "history.json"

LABEL_COLOR = "132f4c"


def _shields_escape(s: str) -> str:
    # shields.io static badges require literal hyphens to be doubled and underscores doubled.
    return quote(str(s).replace("_", "__").replace("-", "--"))


def badge(label: str, value: str, color: str) -> str:
    return (
        f'<img src="https://img.shields.io/badge/'
        f'{_shields_escape(label)}-{_shields_escape(value)}-{color}'
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


def uk_now() -> datetime.datetime:
    # UK is UTC year-round-ish; use BST offset between last-Sun-Mar and last-Sun-Oct.
    now = datetime.datetime.now(datetime.timezone.utc)
    year = now.year
    def last_sunday(y: int, m: int) -> datetime.date:
        d = datetime.date(y, m, 31)
        while d.weekday() != 6:
            d -= datetime.timedelta(days=1)
        return d
    bst_start = datetime.datetime.combine(last_sunday(year, 3), datetime.time(1, 0), tzinfo=datetime.timezone.utc)
    bst_end   = datetime.datetime.combine(last_sunday(year, 10), datetime.time(1, 0), tzinfo=datetime.timezone.utc)
    offset = datetime.timedelta(hours=1) if bst_start <= now < bst_end else datetime.timedelta(hours=0)
    return now + offset


def render_greeting_block() -> str:
    now = uk_now()
    h = now.hour
    if   5 <= h < 12: g = "Good morning"
    elif 12 <= h < 18: g = "Good afternoon"
    elif 18 <= h < 22: g = "Good evening"
    else: g = "Working the night shift"
    counter = (
        f'<img src="https://api.visitorbadge.io/api/visitors?'
        f'path=github.com%2F{OWNER}&label=Visitors%20today&countColor=%2336d1dc&labelColor=%23132f4c&style=flat-square" '
        f'alt="Visitors today">'
    )
    return f'<sub><b>👋 {g}!</b> &nbsp;·&nbsp; {counter}</sub>'


def render_status_block() -> str:
    now = uk_now()
    h, dow = now.hour, now.weekday()  # 0=Mon
    on_shift = (dow < 5 and 8 <= h < 20)
    tz_label = "BST" if (uk_now() - datetime.datetime.now(datetime.timezone.utc)).total_seconds() > 0 else "GMT"
    if on_shift:
        status = badge("Status", f"🟢 On-shift · UK {now:%H:%M} {tz_label}", "3fb950")
    elif dow < 5:
        status = badge("Status", f"🌙 Off-shift · UK {now:%H:%M} {tz_label}", "a371f7")
    else:
        status = badge("Status", f"🛌 Weekend · UK {now:%H:%M} {tz_label}", "8b949e")
    rota = badge("This week", "On-call (escalations welcome)", "36d1dc")
    return "  " + status + "\n  " + rota


def render_days_block(commits_this_year: int = 0, streak_days: int = 0) -> str:
    streak_label = "1 day" if streak_days == 1 else f"{streak_days} days"
    return "  " + "  ".join([
        badge("Commits", f"{commits_this_year:,} this year", "3fb950"),
        badge("Streak", streak_label, "ff8c42"),
    ])


def fetch_github_activity() -> tuple[int, int]:
    """Return (commits_this_year, current_streak_days). Best-effort; returns (0,0) on failure."""
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    if not token:
        return 0, 0
    year = datetime.datetime.now(datetime.timezone.utc).year
    body = json.dumps({
        "query": """
        query($login:String!,$from:DateTime!,$to:DateTime!){
          user(login:$login){
            contributionsCollection(from:$from,to:$to){
              contributionCalendar{
                totalContributions
                weeks{contributionDays{date contributionCount}}
              }
            }
          }
        }""",
        "variables": {
            "login": OWNER,
            "from": f"{year}-01-01T00:00:00Z",
            "to":   f"{year}-12-31T23:59:59Z",
        },
    }).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
    except Exception:
        return 0, 0
    cc = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total = int(cc["totalContributions"])
    days = [d for w in cc["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"], reverse=True)
    streak = 0
    today = datetime.date.today().isoformat()
    for d in days:
        if d["date"] > today:
            continue
        if int(d["contributionCount"]) > 0:
            streak += 1
        else:
            if d["date"] != today or streak > 0:
                break
    return total, streak


def fetch_public_repo_count() -> int:
    """Return the live public-repo count for OWNER. 0 on failure."""
    try:
        with urllib.request.urlopen(f"https://api.github.com/users/{OWNER}", timeout=15) as r:
            return int(json.loads(r.read()).get("public_repos", 0))
    except Exception:
        return 0


def render_public_repos_block() -> str:
    n = fetch_public_repo_count()
    return "  " + badge("Public repos", str(n), "a371f7")


def render_top_repo_block(hist: dict) -> str:
    """Render the top three labs by seven-day engagement as a linked badge bar."""
    ranked: list[tuple[int, str, int, int]] = []
    for repo, rows in hist.get("repos", {}).items():
        if not rows:
            continue
        views = sum(int(row.get("views", 0) or 0) for row in rows[-7:])
        clones = sum(int(row.get("clones", 0) or 0) for row in rows[-7:])
        ranked.append((views + clones * 3, repo, views, clones))

    if not ranked:
        return "<sub>Leaderboard pending — first week of data still collecting.</sub>"

    ranked.sort(key=lambda row: (-row[0], row[1].lower()))
    badges = []
    for rank, (_, repo, views, clones) in enumerate(ranked[:3], start=1):
        metric = f"{views} views · {clones} clones"
        badges.append(
            f'<a href="https://github.com/{OWNER}/{repo}">'
            f'{badge(f"#{rank} {repo}", metric, "1f6feb")}</a>'
        )

    return (
        '<p align="center">\n'
        '<sub>🏆 <b>Top repositories this week</b> · ranked by views and clones</sub><br>\n'
        + "  ".join(badges)
        + '\n</p>'
    )


def render_aggregate_block(hist: dict) -> str:
    repos = hist.get("repos", {})
    n_labs = sum(1 for rows in repos.values() if rows)
    if not n_labs:
        return "<sub>Aggregate metrics warming up — first snapshot pending.</sub>"
    views_30d = sum(sum(int(r.get("views", 0) or 0)  for r in rows[-30:]) for rows in repos.values())
    clones_30d = sum(sum(int(r.get("clones", 0) or 0) for r in rows[-30:]) for rows in repos.values())
    stars_total = sum(int(rows[-1].get("stars", 0) or 0) for rows in repos.values() if rows)
    forks_total = sum(int(rows[-1].get("forks", 0) or 0) for rows in repos.values() if rows)
    return "  " + "  ".join([
        badge("Total lab clones", f"{clones_30d:,} / 30d", "36d1dc"),
        badge("Total lab views",  f"{views_30d:,} / 30d",  "3fb950"),
        badge("Total stars",      f"{stars_total:,}",      "ffcf5a"),
        badge("Total forks",      f"{forks_total:,}",      "a371f7"),
        badge("Labs tracked",     str(n_labs),             "ff8c42"),
    ])


def main() -> int:
    check = "--check" in sys.argv

    hist = json.loads(HIST.read_text(encoding="utf-8"))
    original = README.read_text(encoding="utf-8")
    text = original

    text = replace_block(text, "PROFILE-VIEWS", render_profile_block(hist))
    text = replace_block(text, "PUBLIC-REPOS", render_public_repos_block())
    text = replace_block(text, "LAB-AGGREGATE", render_aggregate_block(hist))
    text = replace_block(text, "GREETING", render_greeting_block())
    text = replace_block(text, "STATUS", render_status_block())
    commits_yr, streak = fetch_github_activity()
    text = replace_block(text, "DAYS-COUNTER", render_days_block(commits_yr, streak))
    text = replace_block(text, "TOP-REPO", render_top_repo_block(hist))

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

# Leaderboard refresh trigger: configuration changes start an immediate run.
