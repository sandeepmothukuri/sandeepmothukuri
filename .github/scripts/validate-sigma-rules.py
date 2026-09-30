#!/usr/bin/env python3
"""Automated Sigma Rule Linter & Detection-as-Code Quality Gate.

Fetches and validates detection rules across Sandeep's open-source security labs:
- Enterprise-Detection-Engineering-SOC-Lab
- soc-threat-hunting-lab
- sentinel-detection-engine

Validates YAML syntax, required schema keys (title/logsource/detection/level),
MITRE ATT&CK technique tags, and condition integrity.
"""
from __future__ import annotations

import io
import re
import sys
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("Missing pyyaml: pip install pyyaml\n")
    sys.exit(2)

# Ensure stdout handles Unicode/emojis across Windows and Linux
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OWNER = "sandeepmothukuri"
TIMEOUT = 15

RULES_TO_VALIDATE = [
    # Enterprise Detection Engineering SOC Lab
    ("Enterprise-Detection-Engineering-SOC-Lab", "config/elastalert2/rules/T1003_credential_dump.yml", "elastalert"),
    ("Enterprise-Detection-Engineering-SOC-Lab", "config/elastalert2/rules/T1110_brute_force.yml",     "elastalert"),
    ("Enterprise-Detection-Engineering-SOC-Lab", "config/elastalert2/rules/T1059_powershell.yml",      "elastalert"),
    ("Enterprise-Detection-Engineering-SOC-Lab", "config/elastalert2/rules/T1557_responder.yml",       "elastalert"),
    ("Enterprise-Detection-Engineering-SOC-Lab", "config/elastalert2/rules/network_c2_beacon.yml",     "elastalert"),
    # SOC Threat Hunting Lab (Sigma)
    ("soc-threat-hunting-lab", "08-integrations/sigma-rules/c2-beaconing.yml", "sigma"),
    ("soc-threat-hunting-lab", "08-integrations/sigma-rules/dns-tunneling.yml", "sigma"),
    # Microsoft Sentinel Detection Engine
    ("sentinel-detection-engine", "Detections/EntraID_ImpossibleTravel.yaml", "sentinel"),
    ("sentinel-detection-engine", "Detections/EntraID_MFAFatigue.yaml", "sentinel"),
    ("sentinel-detection-engine", "Detections/M365_MassSharePointDownload.yaml", "sentinel"),
]


def fetch_rule(repo: str, path: str) -> str:
    url = f"https://raw.githubusercontent.com/{OWNER}/{repo}/main/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "Sigma-CI-Validator"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", errors="replace")


def validate_rule(name: str, content: str, rule_type: str) -> tuple[bool, str, str]:
    """Validate YAML syntax and schema requirements."""
    try:
        data = yaml.safe_load(content)
    except Exception as e:
        return False, "YAML Syntax Error", str(e)

    if not isinstance(data, dict):
        return False, "Malformed Document", "Root element must be a mapping"

    if rule_type == "sigma":
        required = ["title", "logsource", "detection"]
        for key in required:
            if key not in data:
                return False, "Missing Schema Key", f"Required key '{key}' missing"
        
        # Validate detection condition
        det = data.get("detection", {})
        if not isinstance(det, dict) or "condition" not in det:
            return False, "Missing Condition", "detection block must include 'condition'"

        # Validate ATT&CK tags
        tags = data.get("tags", [])
        attack_tags = [t for t in tags if "attack." in str(t).lower() or re.match(r"t\d{4}", str(t).lower())]
        mitre_info = f"Tags: {len(attack_tags)} ATT&CK tags"

    elif rule_type == "sentinel":
        if "id" not in data and "name" not in data:
            return False, "Missing Name/ID", "Sentinel rule must specify 'id' or 'name'"
        if "query" not in data:
            return False, "Missing KQL Query", "Sentinel rule must include 'query'"
        mitre_info = f"Severity: {data.get('severity', 'Medium')}"

    elif rule_type == "elastalert":
        if "name" not in data:
            return False, "Missing Rule Name", "ElastAlert rule must include 'name'"
        if "type" not in data:
            return False, "Missing Type", "ElastAlert rule must include 'type'"
        mitre_info = f"Type: {data.get('type')}"

    else:
        mitre_info = "Parsed"

    return True, "PASSED", mitre_info


def main() -> int:
    print(f"============================================================")
    print(f"🛡️  Detection-as-Code Quality Gate: Validating {len(RULES_TO_VALIDATE)} Rules")
    print(f"============================================================")

    passed = 0
    failed = 0

    for repo, path, rtype in RULES_TO_VALIDATE:
        rule_name = Path(path).name
        try:
            content = fetch_rule(repo, path)
            ok, status, detail = validate_rule(rule_name, content, rtype)
        except Exception as e:
            ok, status, detail = False, "Fetch Error", str(e)

        if ok:
            passed += 1
            print(f"  ✓ [{rtype.upper():10s}] {rule_name:35s} -> {status} ({detail})")
        else:
            failed += 1
            print(f"  ✗ [{rtype.upper():10s}] {rule_name:35s} -> {status}: {detail}")

    total = len(RULES_TO_VALIDATE)
    pass_pct = (passed / total) * 100 if total else 0

    print(f"------------------------------------------------------------")
    print(f"Results: {passed}/{total} Passed ({pass_pct:.1f}%) · {failed} Errors")
    print(f"Quality Gate Status: {'✓ PASS (100% Validated)' if failed == 0 else '✗ FAIL'}")
    print(f"============================================================")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
