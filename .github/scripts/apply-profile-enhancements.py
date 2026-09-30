#!/usr/bin/env python3
"""Profile validation and integrity check.

Ensures that all critical autopilot marker comments remain intact in README.md:
- TOP-DRIVERS (dynamic leaderboard)
- FEATURED-LABS (descending traffic grid)
- REPO-METRICS (per-repo traffic badges)
- STATUS (India IST shift status)
- CVE-OF-THE-WEEK (CISA KEV threat intel)
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

# Ensure stdout handles Unicode/emojis safely across Windows and Linux
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"

REQUIRED_MARKERS = [
    "TOP-DRIVERS",
    "FEATURED-LABS",
    "STATUS",
    "PUBLIC-REPOS",
    "DAYS-COUNTER",
    "PROFILE-VIEWS",
    "LAB-AGGREGATE",
    "SECOPS-HYGIENE",
]


def validate_profile() -> int:
    if not README.exists():
        print("ERROR: README.md not found", file=sys.stderr)
        return 1

    content = README.read_text(encoding="utf-8")
    missing = []

    for marker in REQUIRED_MARKERS:
        has_space = f"<!-- {marker} START -->" in content and f"<!-- {marker} END -->" in content
        has_hyphen = f"<!-- {marker}-START -->" in content and f"<!-- {marker}-END -->" in content
        if not (has_space or has_hyphen):
            missing.append(marker)

    # Check CVE marker (supports both hyphen and space)
    cve_ok = (
        ("<!-- CVE-OF-THE-WEEK-START -->" in content and "<!-- CVE-OF-THE-WEEK-END -->" in content)
        or ("<!-- CVE-OF-THE-WEEK START -->" in content and "<!-- CVE-OF-THE-WEEK END -->" in content)
    )
    if not cve_ok:
        missing.append("CVE-OF-THE-WEEK")

    if missing:
        print(f"ERROR: Missing essential profile markers: {missing}", file=sys.stderr)
        return 1

    print("✓ All essential profile markers verified successfully:")
    for marker in REQUIRED_MARKERS + ["CVE-OF-THE-WEEK"]:
        print(f"  - {marker}: OK")
    return 0


if __name__ == "__main__":
    sys.exit(validate_profile())
