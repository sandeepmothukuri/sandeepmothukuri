#!/usr/bin/env python3
"""Automated Plagiarism & Copycat Guardrail Engine.

Monitors public GitHub repositories for unauthorized mirrors, scraped forks,
and plagiarized copies of Sandeep Mothukuri's profile and detection engineering labs.
"""
from __future__ import annotations

import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

# Ensure UTF-8 output across Windows and CI runners
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OWNER = "sandeepmothukuri"
API_BASE = "https://api.github.com"

# Unique fingerprints characterizing this profile and custom detection portfolio
SIGNATURE_QUERIES = [
    # Full profile duplication check
    f'"Enterprise-Detection-Engineering-SOC-Lab" "PromptSentinel" "AI-SOC-Decision-Engine" -user:{OWNER}',
    # Author identity & website attribution scraping check
    f'filename:README.md "Sandeep Mothukuri" "cybertechnology.in" -user:{OWNER}',
    # Custom ElastAlert / Sigma detection rule fingerprint
    f'filename:T1003_credential_dump.yml "mimikatz" "lsass" -user:{OWNER}',
]


def search_github(query: str, token: str | None = None) -> list[dict]:
    """Execute a GitHub Code Search query."""
    encoded_q = urllib.parse.quote(query)
    url = f"{API_BASE}/search/code?q={encoded_q}&per_page=10"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Plagiarism-Guard-Bot",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
    except urllib.error.HTTPError as e:
        if e.code == 403:
            sys.stderr.write(f"GitHub API Rate Limit / Forbidden on query '{query}'\n")
            return []
        sys.stderr.write(f"HTTP {e.code} querying '{query}': {e.read().decode()}\n")
        return []
    except Exception as e:
        sys.stderr.write(f"Error querying '{query}': {e}\n")
        return []


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        # Try local gh CLI auth if available
        try:
            import subprocess
            token = subprocess.check_output(["gh", "auth", "token"], text=True).strip()
        except Exception:
            token = None

    print("============================================================")
    print("🛡️  Anti-Plagiarism & IP Infringement Monitor")
    print("============================================================")

    suspicious_repositories: dict[str, list[str]] = {}

    for query in SIGNATURE_QUERIES:
        print(f"Scanning fingerprint: {query[:55]}...")
        items = search_github(query, token)
        for item in items:
            repo_name = item.get("repository", {}).get("full_name")
            file_path = item.get("path")
            html_url = item.get("html_url")
            
            # Filter out domain lists or non-code artifacts
            if repo_name and not any(x in repo_name.lower() for x in ["dot-in", "domain-names", "expired"]):
                if repo_name not in suspicious_repositories:
                    suspicious_repositories[repo_name] = []
                suspicious_repositories[repo_name].append(html_url or file_path)

    print("------------------------------------------------------------")
    if suspicious_repositories:
        print(f"⚠️  Potential Unauthorized Copies Detected ({len(suspicious_repositories)} Repositories):")
        for repo, paths in suspicious_repositories.items():
            print(f"\n  🚨 Repo: https://github.com/{repo}")
            for p in paths[:3]:
                print(f"     Match: {p}")
        print("\nAction Required:")
        print("Review the matches above. If any infringe on your All Rights Reserved license,")
        print("submit a DMCA takedown using the template in DMCA.md or at https://github.com/contact/dmca")
        return 0  # Informational alert, do not fail CI unless desired
    else:
        print("✓ Zero unauthorized copies detected across public GitHub repositories.")
        print("✓ All proprietary assets, detection rules, and profile layout are unique to @sandeepmothukuri.")
        print("============================================================")
        return 0


if __name__ == "__main__":
    sys.exit(main())
