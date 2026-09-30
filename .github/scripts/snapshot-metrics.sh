#!/usr/bin/env bash
# Snapshot profile views + per-repo traffic snapshot into metrics/history.json.
# Delegates to snapshot-metrics.py which pulls 14-day API traffic and updates live metrics without skipping.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/snapshot-metrics.py"
