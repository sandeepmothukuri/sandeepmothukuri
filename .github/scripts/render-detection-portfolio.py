#!/usr/bin/env python3
"""Render two README blocks from real detection-rule metadata.

Markers:
    <!-- DETECTION-CASESTUDIES START --> ... <!-- DETECTION-CASESTUDIES END -->
    <!-- DETECTION-TRIGGERS START -->     ... <!-- DETECTION-TRIGGERS END -->

For each curated rule, fetches the raw YAML from github.com, parses
MITRE technique + severity + (for frequency rules) trigger window, then
renders:

  * Case-studies table: technique, what the rule catches, severity, link.
  * Triggers table: rule, configured trigger ("N events in Y min"), window.

All data is parsed from the user's own public detection files — nothing
is invented. Run with --check to print without writing.
"""
from __future__ import annotations
import re
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("Need pyyaml: pip install pyyaml\n")
    sys.exit(2)

OWNER = "sandeepmothukuri"
ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
TIMEOUT = 20

# Curated subset chosen to cover diverse MITRE tactics across all 4 labs.
CURATED = [
    # (repo, path, branch)
    ("advanced-soc-lab-v2.0", "config/elastalert2/rules/T1003_credential_dump.yml", "main"),
    ("advanced-soc-lab-v2.0", "config/elastalert2/rules/T1110_brute_force.yml",     "main"),
    ("advanced-soc-lab-v2.0", "config/elastalert2/rules/T1059_powershell.yml",      "main"),
    ("advanced-soc-lab-v2.0", "config/elastalert2/rules/T1557_responder.yml",       "main"),
    ("advanced-soc-lab-v2.0", "config/elastalert2/rules/network_c2_beacon.yml",     "main"),
    ("sentinel-detection-engine", "Detections/EntraID_ImpossibleTravel.yaml",        "main"),
    ("sentinel-detection-engine", "Detections/EntraID_MFAFatigue.yaml",              "main"),
    ("sentinel-detection-engine", "Detections/M365_MassSharePointDownload.yaml",     "main"),
    ("soc-threat-hunting-lab", "08-integrations/sigma-rules/c2-beaconing.yml",       "main"),
    ("soc-threat-hunting-lab", "08-integrations/sigma-rules/dns-tunneling.yml",      "main"),
]

# Extra context for techniques (one-line public knowledge, not invented).
TACTIC_FROM_T = {
    "T1003": "Credential Access",      "T1078": "Initial Access",
    "T1071": "Command & Control",      "T1059": "Execution",
    "T1110": "Credential Access",      "T1021": "Lateral Movement",
    "T1557": "Credential Access",      "T1041": "Exfiltration",
    "T1547": "Persistence",            "T1053": "Persistence",
    "T1046": "Discovery",              "T1047": "Execution",
    "T1550": "Lateral Movement",       "T1562": "Defense Evasion",
    "T1621": "Credential Access",      "T1213": "Collection",
    "T1539": "Credential Access",
}

PLAIN_FROM_T = {
    "T1003": "LSASS / SAM credential dumping",
    "T1003.001": "LSASS process memory dumping",
    "T1078.004": "Cloud-account abuse — sign-ins from implausibly distant locations",
    "T1071":     "Application-layer C2 beaconing",
    "T1071.004": "DNS tunnelling for C2 / exfiltration",
    "T1059":     "Command-and-scripting interpreter abuse",
    "T1059.001": "Encoded / obfuscated PowerShell execution",
    "T1110":     "Password brute-force / spray",
    "T1557":     "Adversary-in-the-middle (LLMNR / NBT-NS / mDNS poisoning)",
    "T1621":     "MFA-fatigue / push-bombing",
}


def fetch(repo: str, path: str, branch: str) -> str:
    url = f"https://raw.githubusercontent.com/{OWNER}/{repo}/{branch}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "detection-portfolio-renderer"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", errors="replace")


def find_first(s: str, *patterns: str) -> str | None:
    for p in patterns:
        m = re.search(p, s, re.IGNORECASE | re.MULTILINE)
        if m:
            return m.group(1).strip()
    return None


def parse_metadata(text: str) -> dict:
    """Best-effort parse — tolerates ElastAlert / Sentinel / Sigma formats."""
    # First try strict YAML for the simpler files
    parsed = None
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError:
        parsed = None

    name = None
    severity = None
    technique = None
    num_events = None
    timeframe_min = None
    description = None
    rule_type = None  # "frequency", "any", "scheduled-query", "sigma"

    if isinstance(parsed, dict):
        name = parsed.get("name") or parsed.get("title")
        # Rule type heuristic
        if parsed.get("type") == "frequency":
            rule_type = "frequency"
        elif parsed.get("type") == "any":
            rule_type = "any"
        elif parsed.get("queryFrequency") or parsed.get("queryPeriod"):
            rule_type = "scheduled-query"
        elif parsed.get("logsource") and parsed.get("detection"):
            rule_type = "sigma"
        # Sentinel uses "severity"; Sigma uses "level"; ElastAlert sometimes nests
        severity = parsed.get("severity") or parsed.get("level")
        description = parsed.get("description")
        if isinstance(description, str):
            description = " ".join(description.split())
            # First sentence often captures the essence — keep it tight
            first_sent = re.split(r"(?<=[.!?])\s+", description, maxsplit=1)[0]
            description = first_sent
            if len(description) > 110:
                description = description[:107] + "…"
        # Sentinel uses relevantTechniques: [list]
        techs = parsed.get("relevantTechniques") or []
        if isinstance(techs, list) and techs:
            technique = str(techs[0])
        # ElastAlert pattern: http_post_payload.mitre / .severity
        payload = parsed.get("http_post_payload") or {}
        if isinstance(payload, dict):
            if not technique and payload.get("mitre"):
                technique = str(payload["mitre"])
            if not severity and payload.get("severity"):
                severity = str(payload["severity"])
        # Sigma tags: ["attack.t1078.004", ...]
        if not technique and isinstance(parsed.get("tags"), list):
            for t in parsed["tags"]:
                m = re.match(r"attack\.(t\d{4}(?:\.\d+)?)", str(t).lower())
                if m:
                    technique = m.group(1).upper()
                    break
        num_events = parsed.get("num_events")
        tf = parsed.get("timeframe")
        if isinstance(tf, dict):
            timeframe_min = tf.get("minutes") or tf.get("hours", 0) * 60 or tf.get("seconds", 0) / 60
        # Sentinel: queryFrequency / queryPeriod like "1h"
        if timeframe_min is None and parsed.get("queryFrequency"):
            qf = str(parsed["queryFrequency"])
            mm = re.match(r"(\d+)([mhd])", qf)
            if mm:
                v = int(mm.group(1))
                timeframe_min = {"m": v, "h": v * 60, "d": v * 1440}[mm.group(2)]

    # Regex fallback for fields the YAML parser missed (e.g. ElastAlert quirks)
    if not technique:
        # Look in raw text for T1234 or T1234.001
        m = re.search(r"\b(T\d{4}(?:\.\d+)?)\b", text)
        if m:
            technique = m.group(1)
    if not name:
        name = find_first(text, r"^name:\s*[\"']?([^\"'\n]+)", r"^title:\s*[\"']?([^\"'\n]+)") or "(unnamed rule)"
    if not severity:
        severity = find_first(text, r"^severity:\s*[\"']?([^\"'\n]+)", r"^level:\s*([a-zA-Z]+)") or "—"

    return {
        "name": name,
        "severity": severity,
        "technique": technique,
        "num_events": num_events,
        "timeframe_min": timeframe_min,
        "description": description,
        "rule_type": rule_type,
    }


def replace_block(text: str, marker: str, new_inner: str) -> str:
    start = f"<!-- {marker} START -->"
    end = f"<!-- {marker} END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    new_text, n = pattern.subn(f"{start}\n{new_inner}\n{end}", text)
    if n == 0:
        print(f"WARN: marker {marker} not found in README", file=sys.stderr)
    return new_text


def gh_file_link(repo: str, branch: str, path: str) -> str:
    return f"https://github.com/{OWNER}/{repo}/blob/{branch}/{path}"


def short_name(name: str) -> str:
    # Strip leading rule-id prefix like "SOC-002 | "
    return re.sub(r"^[A-Z]+-\d+\s*\|\s*", "", name).strip()


def render_casestudies(rules: list[dict]) -> str:
    lines = [
        "<details open>",
        "<summary><b>📋 Detection case studies</b> &mdash; "
        f"{len(rules)} representative rules from my live detection portfolio</summary>",
        "",
        "| Technique | Tactic | What the rule catches | Severity | Source |",
        "|---|---|---|---|---|",
    ]
    for r in rules:
        t = r["technique"] or "—"
        t_root = t.split(".")[0]
        tactic = TACTIC_FROM_T.get(t_root, "—")
        plain = PLAIN_FROM_T.get(t) or PLAIN_FROM_T.get(t_root) or short_name(r["name"])
        sev = str(r["severity"] or "—").title()
        link = f"[{r['repo']}](https://github.com/{OWNER}/{r['repo']}/blob/{r['branch']}/{r['path']})"
        # Sentinel rules also have a description — prefer it if available and short
        desc = r.get("description") or plain
        lines.append(f"| **{t}** | {tactic} | {desc} | {sev} | {link} |")
    lines.append("")
    lines.append("<sub>Auto-generated from the YAML in each lab — refreshes weekly via `.github/workflows/detection-portfolio.yml`. Click any rule link to read the full detection logic.</sub>")
    lines.append("</details>")
    return "\n".join(lines)


def render_triggers(rules: list[dict]) -> str:
    if not rules:
        return "<sub>No rule metadata yet — re-run after merging rules.</sub>"
    lines = [
        "| Rule | Type | Trigger | Worst-case latency | Source |",
        "|---|---|---|---|---|",
    ]
    latencies: list[int] = []
    for r in rules:
        rt = r.get("rule_type") or "—"
        if rt == "frequency" and r["num_events"] and r["timeframe_min"]:
            tf = int(r["timeframe_min"])
            trig = f"**{r['num_events']} events in {tf}m**"
            lat = f"≤ {tf}m"
            latencies.append(tf)
        elif rt == "scheduled-query" and r["timeframe_min"]:
            tf = int(r["timeframe_min"])
            trig = f"KQL polled every {tf // 60}h" if tf >= 60 else f"KQL polled every {tf}m"
            lat = f"≤ {tf}m"
            latencies.append(tf)
        elif rt == "any":
            trig = "Fires on first match (no time aggregation)"
            lat = "near real-time"
            latencies.append(1)
        elif rt == "sigma":
            trig = "Sigma — backend-defined (Splunk/QRadar/Elastic timing)"
            lat = "backend-dependent"
        else:
            trig = "—"
            lat = "—"
        link = f"[{Path(r['path']).name}](https://github.com/{OWNER}/{r['repo']}/blob/{r['branch']}/{r['path']})"
        lines.append(f"| {short_name(r['name'])} | `{rt}` | {trig} | {lat} | {link} |")
    lines.append("")
    if latencies:
        lines.append(
            f"<sub>Latency = the rule's own detection window (parsed from `timeframe`, `queryFrequency`, "
            f"or `type`). Portfolio spread: {min(latencies)}–{max(latencies)} minutes worst-case. "
            "These are configured windows, not measured end-to-end times — click any source link to verify the raw values.</sub>"
        )
    return "\n".join(lines)


def main() -> int:
    check = "--check" in sys.argv
    rules: list[dict] = []
    for repo, path, branch in CURATED:
        try:
            text = fetch(repo, path, branch)
        except Exception as e:
            print(f"WARN: skipping {repo}/{path}: {e}", file=sys.stderr)
            continue
        meta = parse_metadata(text)
        meta.update({"repo": repo, "path": path, "branch": branch})
        rules.append(meta)
    if not rules:
        print("ERROR: no rules fetched", file=sys.stderr)
        return 1
    original = README.read_text(encoding="utf-8")
    text = replace_block(original, "DETECTION-CASESTUDIES", render_casestudies(rules))
    text = replace_block(text, "DETECTION-TRIGGERS",   render_triggers(rules))
    if text == original:
        print("No changes.")
        return 0
    if check:
        sys.stdout.write(text)
        return 0
    README.write_text(text, encoding="utf-8")
    print(f"README.md updated from {len(rules)} live rule files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
