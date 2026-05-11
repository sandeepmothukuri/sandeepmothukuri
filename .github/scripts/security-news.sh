#!/usr/bin/env bash
# Pulls latest cybersecurity headlines from public RSS feeds → news.md
# Note: pipefail intentionally omitted — SIGPIPE from `head` in piped streams
#       is expected and harmless; we only want to fail on real errors.
set -eu

FEEDS=(
  "https://feeds.feedburner.com/TheHackersNews|The Hacker News"
  "https://www.bleepingcomputer.com/feed/|BleepingComputer"
  "https://krebsonsecurity.com/feed/|Krebs on Security"
)
TODAY="$(date -u +'%Y-%m-%d %H:%M UTC')"

clean() { sed 's/<!\[CDATA\[//g; s/\]\]>//g' | sed 's/<[^>]*>//g' | tr -s ' \t\n' ' ' | sed 's/^ *//;s/ *$//'; }

{
  echo "### 📰 Threat Headlines"
  echo ""
  echo "_Last refresh: ${TODAY}_"
  echo ""

  for entry in "${FEEDS[@]}"; do
    url="${entry%%|*}"
    name="${entry##*|}"
    echo "**${name}**"
    echo ""

    raw=$(curl -fsSL --max-time 20 -A "Mozilla/5.0 (compatible; SOC-Lab-Profile/1.0)" "$url" 2>/dev/null || echo "")
    if [ -z "$raw" ]; then
      echo "- _Feed temporarily unavailable._"
      echo ""
      continue
    fi

    echo "$raw" \
      | tr -d '\n' \
      | sed 's/<item/\n<item/g' \
      | grep -E "^<item" \
      | head -4 \
      | while read -r item; do
          title=$(echo "$item" | sed -n 's/.*<title[^>]*>\(.*\)<\/title>.*/\1/p' | clean)
          link=$(echo "$item" | sed -n 's/.*<link[^>]*>\([^<]*\)<\/link>.*/\1/p' | clean)
          [ -z "$link" ] && link=$(echo "$item" | sed -n 's/.*<link[^>]*href="\([^"]*\)".*/\1/p' | clean)
          if [ -n "$title" ] && [ -n "$link" ]; then
            echo "- [${title}](${link})"
          fi
        done
    echo ""
  done

  echo "> Headlines pulled from public RSS feeds. Not endorsements — just situational awareness."
} > news.md

echo "Wrote news.md:"
cat news.md
