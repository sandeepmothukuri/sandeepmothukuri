#!/usr/bin/env bash
# Generates digest.md with last-14-day traffic stats across all listed repos.
# Run from repo root. Requires `gh` CLI and `jq`; both are pre-installed on ubuntu-latest runners.
set -euo pipefail

REPOS=(
  "advanced-soc-lab-v2.0"
  "ai-soc-lab"
  "soc-lab"
  "soc-lab-free"
  "soc-threat-hunting-lab"
  "Autonomous-SOC-Lab"
  "cyberblue"
)
OWNER="sandeepmothukuri"
TODAY="$(date -u +'%Y-%m-%d %H:%M UTC')"

{
  echo "## 📈 Repo Traffic — Last 14 Days"
  echo ""
  echo "_Generated ${TODAY}. Private to repo admins (this is an Actions run summary, not published to README)._"
  echo ""
  echo "| Repo | 👁 Views | 🧑 Unique | 📥 Clones | 🆔 Unique cloners | ⭐ Stars |"
  echo "|---|---:|---:|---:|---:|---:|"

  for repo in "${REPOS[@]}"; do
    views=$(gh api -H "Accept: application/vnd.github+json" \
      "/repos/${OWNER}/${repo}/traffic/views" 2>/dev/null || echo '{}')
    clones=$(gh api -H "Accept: application/vnd.github+json" \
      "/repos/${OWNER}/${repo}/traffic/clones" 2>/dev/null || echo '{}')
    stars=$(gh api -H "Accept: application/vnd.github+json" \
      "/repos/${OWNER}/${repo}" 2>/dev/null | jq -r '.stargazers_count // 0')

    v_count=$(echo "$views"  | jq -r '.count   // 0')
    v_uniq=$(echo  "$views"  | jq -r '.uniques // 0')
    c_count=$(echo "$clones" | jq -r '.count   // 0')
    c_uniq=$(echo  "$clones" | jq -r '.uniques // 0')

    echo "| [${repo}](https://github.com/${OWNER}/${repo}) | ${v_count} | ${v_uniq} | ${c_count} | ${c_uniq} | ${stars} |"
  done

  echo ""
  echo "### 🔗 Top Referrers (across all repos, last 14 d)"
  echo ""
  echo "| Source | Repo | Visits | Unique |"
  echo "|---|---|---:|---:|"

  for repo in "${REPOS[@]}"; do
    gh api -H "Accept: application/vnd.github+json" \
      "/repos/${OWNER}/${repo}/traffic/popular/referrers" 2>/dev/null \
      | jq -r --arg r "$repo" '.[] | "\(.referrer)|\($r)|\(.count)|\(.uniques)"' \
      || true
  done | sort -t'|' -k3 -rn | head -10 | awk -F'|' '{printf "| %s | %s | %s | %s |\n", $1, $2, $3, $4}'

  echo ""
  echo "> ℹ️ GitHub anonymizes individual viewers/cloners. The numbers above are aggregate. For named interest (recruiters, hiring managers, etc.) check each repo's auto-generated **STARGAZERS.md** and the auto-created **\"⭐ New stargazer: @username\"** issues."
} > digest.md

echo "Wrote digest.md:"
cat digest.md
