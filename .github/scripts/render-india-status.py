#!/usr/bin/env python3
"""Render the profile status badge using India Standard Time (Asia/Kolkata).

This runs after the main metrics renderer so the profile never displays the
legacy UK timezone. The status is intentionally derived from the current
India time on every daily workflow run.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
IST = ZoneInfo("Asia/Kolkata")


def badge(label: str, value: str, color: str = "8b949e") -> str:
    from urllib.parse import quote

    def esc(value: str) -> str:
        return quote(str(value).replace("_", "__").replace("-", "--"))

    return (
        f'<img src="https://img.shields.io/badge/'
        f'{esc(label)}-{esc(value)}-{color}'
        f'?style=flat-square&labelColor=132f4c" '
        f'alt="{label}: {value}">'
    )


def render_status() -> str:
    now = dt.datetime.now(IST)
    h = now.hour
    dow = now.weekday()

    if dow < 5 and 8 <= h < 20:
        value = f"🟢 On-shift · India {now:%H:%M} IST"
        color = "3fb950"
    elif dow < 5:
        value = f"🌙 Off-shift · India {now:%H:%M} IST"
        color = "a371f7"
    else:
        value = f"🛌 Weekend · India {now:%H:%M} IST"
        color = "8b949e"

    return "  " + badge("Status", value, color) + "\n  " + badge(
        "This week", "On-call (escalations welcome)", "36d1dc"
    )


def main() -> None:
    text = README.read_text(encoding="utf-8")
    start = "<!-- STATUS START -->"
    end = "<!-- STATUS END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{render_status()}\n{end}"
    new_text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit("STATUS markers not found exactly once in README.md")
    README.write_text(new_text, encoding="utf-8")
    print("Updated profile status using Asia/Kolkata (IST).")


if __name__ == "__main__":
    main()
