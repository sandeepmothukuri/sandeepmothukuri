#!/usr/bin/env bash
# Appends today's profile-views + per-repo traffic snapshot to metrics/history.json.
# Idempotent: if today's date is already recorded for a series, that series is skipped.
# Requires: gh CLI, jq, curl. GH_TOKEN must have access to the public repository traffic API.
# Public repositories are discovered automatically every run; the profile repository
# itself is excluded because its traffic is tracked separately as profile metrics.
set -euo pipefail

OWNER="sandeepmothukuri"
TODAY="$(date -u +'%Y-%m-%d')"
YESTERDAY="$(date -u -d 'yesterday' +'%Y-%m-%d')"
HIST="metrics/history.json"

mkdir -p metrics
[[ -f "$HIST" ]] || echo '{"profile_views":[],"repos":{}}' > "$HIST"

# --- discover every public repository owned by the profile ---
# Paginate so this continues to work if the account grows beyond 100 public repos.
# The profile repository is intentionally excluded from lab/repository traffic
# because its profile-view counter is maintained separately below.
mapfile -t REPOS < <(
  gh api --paginate \
    -H 'Accept: application/vnd.github+json' \
    "/users/${OWNER}/repos?type=public&per_page=100" \
    --jq '.[] | select(.name != "'"$OWNER"'") | .name' \
    | sort -u
)

echo "Discovered ${#REPOS[@]} public repositories for ${OWNER}."

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
  views_json="$(gh api -H 'Accept: application/vnd.github+json' "/repos/${OWNER}/${repo}/traffic/views" 2>/dev/null || echo '{"views":[]}')"
  clones_json="$(gh api -H 'Accept: application/vnd.github+json' "/repos/${OWNER}/${repo}/traffic/clones" 2>/dev/null || echo '{"clones":[]}')"
  meta_json="$(gh api -H 'Accept: application/vnd.github+json' "/repos/${OWNER}/${repo}" 2>/dev/null || echo '{}')"
  release_json="$(gh api --paginate --slurp -H 'Accept: application/vnd.github+json' "/repos/${OWNER}/${repo}/releases?per_page=100" 2>/dev/null || echo '[]')"

  # Yesterday's complete daily bucket (today's is partial).
  # Note: first.count would parse as .first.count in jq — must use .[0].count.
  v_daily=$(echo "$views_json" | jq --arg d "$YESTERDAY" '[.views[] | select(.timestamp | startswith($d))] | (.[0].count // 0)')
  v_uniq=$(echo "$views_json" | jq --arg d "$YESTERDAY" '[.views[] | select(.timestamp | startswith($d))] | (.[0].uniques // 0)')
  c_daily=$(echo "$clones_json" | jq --arg d "$YESTERDAY" '[.clones[] | select(.timestamp | startswith($d))] | (.[0].count // 0)')
  c_uniq=$(echo "$clones_json" | jq --arg d "$YESTERDAY" '[.clones[] | select(.timestamp | startswith($d))] | (.[0].uniques // 0)')
  stars=$(echo "$meta_json" | jq -r '.stargazers_count // 0')
  forks=$(echo "$meta_json" | jq -r '.forks_count // 0')
  release_downloads=$(echo "$release_json" | jq '[.[][]?.assets[]?.download_count // 0] | add // 0')

  already="$(jq --arg r "$repo" --arg d "$TODAY" '[.repos[$r][]? | select(.date==$d)] | length' "$HIST")"
  if [[ "$already" != "0" ]]; then
    has_release_downloads="$(jq --arg r "$repo" --arg d "$TODAY" '[.repos[$r][]? | select(.date==$d) | has("release_downloads")] | any' "$HIST")"
    if [[ "$has_release_downloads" == "true" ]]; then
      echo "$repo: $TODAY already present, skipping"
    else
      tmp="$(mktemp)"
      jq --arg r "$repo" --arg d "$TODAY" --argjson rd "$release_downloads" \
        '(.repos[$r] |= map(if .date == $d then .release_downloads = $rd else . end))' \
        "$HIST" > "$tmp" && mv "$tmp" "$HIST"
      echo "$repo: added release_downloads=$release_downloads to today's snapshot"
    fi
    continue
  fi

  tmp="$(mktemp)"
  jq --arg r "$repo" --arg d "$TODAY" \
     --argjson v "$v_daily" --argjson vu "$v_uniq" \
     --argjson c "$c_daily" --argjson cu "$c_uniq" \
     --argjson s "$stars" --argjson f "$forks" --argjson rd "$release_downloads" \
     '.repos[$r] = ((.repos[$r] // []) + [{"date":$d,"views":$v,"unique":$vu,"clones":$c,"unique_cloners":$cu,"stars":$s,"forks":$f,"release_downloads":$rd}])' \
     "$HIST" > "$tmp" && mv "$tmp" "$HIST"
  echo "$repo: appended views=$v_daily clones=$c_daily stars=$stars forks=$forks release_downloads=$release_downloads"
done

echo "Snapshot complete. Tracked public repositories: ${#REPOS[@]}"
