#!/usr/bin/env python3
"""Automated Zero-Broken-Links Verification Guardrail.

Extracts all external links from README.md and verifies their HTTP reachability.
Ensures zero dead links (404, 410, DNS resolution failures) in the production profile.
"""
from __future__ import annotations

import concurrent.futures
import io
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Ensure UTF-8 output across Windows and CI runners
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

README = Path(__file__).resolve().parents[2] / "README.md"
TIMEOUT = 10
MAX_WORKERS = 8

# Common platforms that return 403/999/429 to non-browser scrapers
BOT_PROTECTED_DOMAINS = (
    "linkedin.com",
    "www.linkedin.com",
    "twitter.com",
    "x.com",
    "medium.com",
    "reddit.com",
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def extract_urls(text: str) -> list[str]:
    """Find all unique http(s) URLs in markdown and HTML attributes."""
    # Matches URLs inside markdown links, image tags, href, src
    raw_urls = re.findall(r"https?://[^\s\"'<>)\`]+", text)
    cleaned = set()
    for u in raw_urls:
        # Strip trailing punctuation from markdown syntax
        u = u.rstrip(".,;)]}>`")
        if u.startswith("http://") or u.startswith("https://"):
            cleaned.add(u)
    return sorted(cleaned)


def check_url(url: str) -> tuple[str, bool, int | str, str]:
    """Check a single URL. Returns (url, is_ok, status_code_or_err, note)."""
    import time

    is_bot_protected = any(domain in url for domain in BOT_PROTECTED_DOMAINS)

    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
        method="HEAD",
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            code = response.getcode()
            return url, True, code, "OK"
    except urllib.error.HTTPError as e:
        if is_bot_protected and e.code in (403, 405, 429, 999):
            return url, True, e.code, "Bot-Shielded (Expected)"

        if e.code == 429:
            # Temporary rate limiting - wait 1.5s and retry once
            time.sleep(1.5)
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as retry_resp:
                    return url, True, retry_resp.getcode(), "OK (Retry)"
            except urllib.error.HTTPError as retry_e:
                if retry_e.code == 429:
                    return url, True, 429, "Throttled / Live Endpoint"
            except Exception:
                pass

        # Try GET fallback for HEAD rejections or servers not implementing HEAD (e.g. 404 on HEAD)
        if e.code in (405, 403, 404, 400):
            try:
                get_req = urllib.request.Request(
                    url,
                    headers={"User-Agent": USER_AGENT, "Range": "bytes=0-1024"},
                )
                with urllib.request.urlopen(get_req, timeout=TIMEOUT) as get_resp:
                    return url, True, get_resp.getcode(), "OK (GET fallback)"
            except urllib.error.HTTPError as get_e:
                if is_bot_protected and get_e.code in (403, 405, 429, 999):
                    return url, True, get_e.code, "Bot-Shielded (Expected)"
                if get_e.code in (401, 403):
                    return url, True, get_e.code, "Restricted Endpoint"
                if get_e.code == 429:
                    return url, True, 429, "Throttled / Live Endpoint"
                return url, False, get_e.code, f"HTTP {get_e.code}"
            except Exception as get_err:
                return url, False, "ERR", str(get_err)
        elif e.code in (401, 403):
            return url, True, e.code, "Restricted Endpoint"
        else:
            return url, False, e.code, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return url, False, "DNS/CONN", str(e.reason)
    except Exception as e:
        return url, False, "TIMEOUT/ERR", str(e)


def main() -> int:
    if not README.exists():
        print(f"ERROR: {README} not found", file=sys.stderr)
        return 1

    content = README.read_text(encoding="utf-8")
    urls = extract_urls(content)

    print("============================================================")
    print(f"🔗  Link Integrity Guardrail: Checking {len(urls)} Unique URLs")
    print("============================================================")

    passed: list[tuple] = []
    failed: list[tuple] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            url, ok, code, note = res
            if ok:
                passed.append(res)
                # Print concise status
                display_url = url if len(url) <= 65 else url[:62] + "..."
                print(f"  ✓ [{str(code):4s}] {display_url:65s} ({note})")
            else:
                failed.append(res)
                print(f"  ✗ [{str(code):4s}] {url} -> {note}")

    print("------------------------------------------------------------")
    print(f"Results: {len(passed)} Valid / Reachable · {len(failed)} Broken")
    print("============================================================")

    if failed:
        print("\n🚨 Broken Links Detected:")
        for url, _, code, note in failed:
            print(f"  - {url} (Status: {code}, Detail: {note})")
        return 1

    print("✓ All hyperlinks in README.md are 100% healthy and verified!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
