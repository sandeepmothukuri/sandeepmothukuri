#!/usr/bin/env bash
# Appends today's profile-views + per-repo traffic snapshot to metrics/history.json.
# Idempotent: if today's date is already recorded for a series, that series is skipped.
# Requires: gh CLI, jq, curl. GH_TOKEN must have public_repo scope (traffic API).
set -euo pipefail

OWNER="sandeepmothukuri"
TODAY="$(date -u +'%Y-%m-%d')"
YESTERDAY="$(date -u -d 'yesterday' +'%Y-%m-%d')"
HIST="metrics/history.json"

REPOS=(
  "advanced-soc-lab-v2.0"
  "ai-soc-lab"
  "soc-lab"
  "soc-lab-free"
  "soc-threat-hunting-lab"
  "Autonomous-SOC-Lab"
  "cyberblue"
)

mkdir -p metrics
[[ -f "$HIST" ]] || echo '{"profile_views":[],"repos":{}}' > "$HIST"

# --- profile views via hits.sh SVG (counter rendered as <text>NNN</text>) ---
hits_svg="$(curl -fsSL "https://hits.sh/github.com/${OWNER}.svg" 2>/dev/null || true)"
# Two identical text nodes (shadow + fill); grab the first numeric one.
total="$(printf '%s' "$hits_svg" | grep -oE '>[0-9]+<' | head -1 | tr -d '><')"
total="${total:-0}"

prev_total="$(jq -r '[.profile_views[].total] | last // 0' "$HIST")"
daily=$(( total - prev_total ))
(( daily < 0 )) && daily=0

already="$(jq --arg d "$TODAY" '[.profile_views[] | select(.date==$d)] | length' "$HIST")"
if [[ "$already" == "0" ]]; then
  tmp="$(mktemp)"
  jq --arg d "$TODAY" --argjson t "$total" --argjson dly "$daily" \
    '.profile_views += [{"date":$d,"total":$t,"daily":$dly}]' "$HIST" > "$tmp" && mv "$tmp" "$HIST"
  echo "profile_views: appended date=$TODAY total=$total daily=$daily"
else
  echo "profile_views: $TODAY already present, skipping"
fi

# --- per-repo snapshots ---
for repo in "${REPOS[@]}"; do
  views_json="$(gh api -H 'Accept: application/vnd.github+json' "/repos/${OWNER}/${repo}/traffic/views"  2>/dev/null || echo '{"views":[]}')"
  clones_json="$(gh api -H 'Accept: application/vnd.github+json' "/repos/${OWNER}/${repo}/traffic/clones" 2>/dev/null || echo '{"clones":[]}')"
  meta_json="$(gh api  -H 'Accept: application/vnd.github+json' "/repos/${OWNER}/${repo}"                  2>/dev/null || echo '{}')"

  # Yesterday's complete daily bucket (today's is partial)
  v_daily=$(echo "$views_json"  | jq --arg d "$YESTERDAY" '[.views[]  | select(.timestamp | startswith($d))] | (first.count    // 0)')
  v_uniq=$(echo  "$views_json"  | jq --arg d "$YESTERDAY" '[.views[]  | select(.timestamp | startswith($d))] | (first.uniques  // 0)')
  c_daily=$(echo "$clones_json" | jq --arg d "$YESTERDAY" '[.clones[] | select(.timestamp | startswith($d))] | (first.count    // 0)')
  c_uniq=$(echo  "$clones_json" | jq --arg d "$YESTERDAY" '[.clones[] | select(.timestamp | startswith($d))] | (first.uniques  // 0)')
  stars=$(echo "$meta_json" | jq -r '.stargazers_count // 0')
  forks=$(echo "$meta_json" | jq -r '.forks_count      // 0')

  already="$(jq --arg r "$repo" --arg d "$TODAY" '[.repos[$r][]? | select(.date==$d)] | length' "$HIST")"
  if [[ "$already" != "0" ]]; then
    echo "$repo: $TODAY already present, skipping"
    continue
  fi

  tmp="$(mktemp)"
  jq --arg r "$repo" --arg d "$TODAY" \
     --argjson v "$v_daily" --argjson vu "$v_uniq" \
     --argjson c "$c_daily" --argjson cu "$c_uniq" \
     --argjson s "$stars"   --argjson f  "$forks" \
     '.repos[$r] = ((.repos[$r] // []) + [{"date":$d,"views":$v,"unique":$vu,"clones":$c,"unique_cloners":$cu,"stars":$s,"forks":$f}])' \
     "$HIST" > "$tmp" && mv "$tmp" "$HIST"
  echo "$repo: appended views=$v_daily clones=$c_daily stars=$stars forks=$forks"
done

echo "Snapshot complete."
