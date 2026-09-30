#!/usr/bin/env python3
"""Snapshot profile views + per-repo 14-day traffic into metrics/history.json.

Runs on autopilot (e.g. every 5 hours). Safe and idempotent:
- Pulls live 14-day traffic for every public repository via GitHub API.
- Upserts the 14-day daily data points into history.json, ensuring no historical
  days are lost or zeroed out.
- Updates today's live views, clones, stars, forks, and releases on every run.
- Preserves all existing records older than 14 days.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

OWNER = "sandeepmothukuri"
ROOT = Path(__file__).resolve().parents[2]
HIST_PATH = ROOT / "metrics" / "history.json"


def get_public_repos() -> list[str]:
    cmd = [
        "gh", "api", "--paginate",
        "-H", "Accept: application/vnd.github+json",
        f"/users/{OWNER}/repos?type=public&per_page=100",
        "--jq", f'.[] | select(.name != "{OWNER}") | .name'
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        repos = [r.strip() for r in out.splitlines() if r.strip()]
        return sorted(list(set(repos)))
    except Exception as e:
        print(f"Error fetching repo list: {e}", file=sys.stderr)
        return []


def update_profile_views(hist: dict, today_str: str) -> None:
    try:
        req = urllib.request.Request(
            f"https://hits.sh/github.com/{OWNER}.svg",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            svg = resp.read().decode("utf-8", errors="replace")
        
        matches = re.findall(r">([0-9]+)<", svg)
        total = int(matches[0]) if matches else 0
    except Exception as e:
        print(f"Warn: unable to fetch hits.sh profile views: {e}", file=sys.stderr)
        return

    if total <= 0:
        return

    views = hist.setdefault("profile_views", [])
    
    # Find last total before today
    yesterday_totals = [entry.get("total", 0) for entry in views if entry.get("date") != today_str]
    prev_total = yesterday_totals[-1] if yesterday_totals else (views[-1].get("total", 0) if views else 0)
    daily = max(0, total - prev_total)

    existing_idx = next((i for i, entry in enumerate(views) if entry.get("date") == today_str), None)
    if existing_idx is not None:
        views[existing_idx]["total"] = total
        views[existing_idx]["daily"] = daily
        print(f"profile_views: updated date={today_str} total={total} daily={daily}")
    else:
        views.append({"date": today_str, "total": total, "daily": daily})
        print(f"profile_views: appended date={today_str} total={total} daily={daily}")


def update_repos(hist: dict, repos: list[str], today_str: str, yesterday_str: str) -> None:
    repos_dict = hist.setdefault("repos", {})

    for repo in repos:
        # 1. Views
        try:
            v_out = subprocess.check_output(
                ["gh", "api", "-H", "Accept: application/vnd.github+json", f"/repos/{OWNER}/{repo}/traffic/views"],
                stderr=subprocess.DEVNULL
            )
            v_json = json.loads(v_out)
        except Exception:
            v_json = {"views": []}

        # 2. Clones
        try:
            c_out = subprocess.check_output(
                ["gh", "api", "-H", "Accept: application/vnd.github+json", f"/repos/{OWNER}/{repo}/traffic/clones"],
                stderr=subprocess.DEVNULL
            )
            c_json = json.loads(c_out)
        except Exception:
            c_json = {"clones": []}

        # 3. Meta
        try:
            m_out = subprocess.check_output(
                ["gh", "api", "-H", "Accept: application/vnd.github+json", f"/repos/{OWNER}/{repo}"],
                stderr=subprocess.DEVNULL
            )
            meta = json.loads(m_out)
        except Exception:
            meta = {}

        # 4. Releases
        try:
            rel_out = subprocess.check_output(
                ["gh", "api", "--paginate", "--slurp", "-H", "Accept: application/vnd.github+json", f"/repos/{OWNER}/{repo}/releases?per_page=100"],
                stderr=subprocess.DEVNULL
            )
            rel_data = json.loads(rel_out)
            release_downloads = sum(
                a.get("download_count", 0)
                for page in rel_data
                for r in page
                for a in r.get("assets", [])
            )
        except Exception:
            release_downloads = 0

        stars = int(meta.get("stargazers_count", 0))
        forks = int(meta.get("forks_count", 0))

        views_by_date = {item["timestamp"][:10]: item for item in v_json.get("views", [])}
        clones_by_date = {item["timestamp"][:10]: item for item in c_json.get("clones", [])}
        api_dates = sorted(list(set(views_by_date.keys()) | set(clones_by_date.keys())))

        existing_rows = repos_dict.get(repo, [])
        row_map = {r["date"]: r for r in existing_rows if isinstance(r, dict) and "date" in r}

        # Map API dates (D) to snapshot dates (D + 1 day)
        for api_d in api_dates:
            try:
                snap_d = (datetime.date.fromisoformat(api_d) + datetime.timedelta(days=1)).isoformat()
            except ValueError:
                continue

            v_item = views_by_date.get(api_d, {})
            c_item = clones_by_date.get(api_d, {})
            v_cnt = int(v_item.get("count", 0))
            v_u = int(v_item.get("uniques", 0))
            c_cnt = int(c_item.get("count", 0))
            c_u = int(c_item.get("uniques", 0))

            if snap_d in row_map:
                row_map[snap_d]["views"] = v_cnt
                row_map[snap_d]["unique"] = v_u
                row_map[snap_d]["clones"] = c_cnt
                row_map[snap_d]["unique_cloners"] = c_u
                row_map[snap_d]["stars"] = stars
                row_map[snap_d]["forks"] = forks
                row_map[snap_d]["release_downloads"] = release_downloads
            else:
                row_map[snap_d] = {
                    "date": snap_d,
                    "views": v_cnt,
                    "unique": v_u,
                    "clones": c_cnt,
                    "unique_cloners": c_u,
                    "stars": stars,
                    "forks": forks,
                    "release_downloads": release_downloads,
                }

        # Ensure today is updated
        latest_views = views_by_date.get(yesterday_str, {}).get("count", 0)
        latest_clones = clones_by_date.get(yesterday_str, {}).get("count", 0)
        latest_vu = views_by_date.get(yesterday_str, {}).get("uniques", 0)
        latest_cu = clones_by_date.get(yesterday_str, {}).get("uniques", 0)

        # If today has actual traffic in the API, use today's traffic
        if today_str in views_by_date or today_str in clones_by_date:
            today_v = views_by_date.get(today_str, {}).get("count", 0)
            today_vu = views_by_date.get(today_str, {}).get("uniques", 0)
            today_c = clones_by_date.get(today_str, {}).get("count", 0)
            today_cu = clones_by_date.get(today_str, {}).get("uniques", 0)
        else:
            today_v = latest_views
            today_vu = latest_vu
            today_c = latest_clones
            today_cu = latest_cu

        row_map[today_str] = {
            "date": today_str,
            "views": today_v,
            "unique": today_vu,
            "clones": today_c,
            "unique_cloners": today_cu,
            "stars": stars,
            "forks": forks,
            "release_downloads": release_downloads,
        }

        # Sort all rows by date
        repos_dict[repo] = [row_map[k] for k in sorted(row_map.keys())]
        print(f"{repo}: updated (views={today_v}, clones={today_c}, stars={stars}, forks={forks})")


def main() -> None:
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    yesterday_str = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    HIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    if HIST_PATH.exists():
        try:
            with open(HIST_PATH, "r", encoding="utf-8") as f:
                hist = json.load(f)
        except Exception:
            hist = {"profile_views": [], "repos": {}}
    else:
        hist = {"profile_views": [], "repos": {}}

    repos = get_public_repos()
    print(f"Discovered {len(repos)} public repositories for {OWNER}.")

    update_profile_views(hist, today_str)
    update_repos(hist, repos, today_str, yesterday_str)

    with open(HIST_PATH, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2)

    print("Snapshot complete.")


if __name__ == "__main__":
    main()
