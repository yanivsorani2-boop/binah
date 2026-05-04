#!/bin/bash
set -e
BASE="${BASE:-https://binah.co.il}"
PASS=0; FAIL=0; FAILS=()
function ok { PASS=$((PASS+1)); echo "PASS $1"; }
function ko { FAIL=$((FAIL+1)); FAILS+=("FAIL $1"); echo "FAIL $1"; }

echo "=== Invariants on $BASE ==="
echo ""

# === Check 1: home links must ALL be in sitemap ===
HOME=$(curl -fsS "$BASE/")
SITEMAP=$(curl -fsS "$BASE/sitemap.xml")
home_arts=$(echo "$HOME" | grep -oE "href=['\"]/?articles/2026-[^'\"<>]+" | sed -E "s|href=['\"]?/?articles/||" | sed 's|\.html$||' | sort -u)
sitemap_arts=$(echo "$SITEMAP" | grep -oE '<loc>[^<]+/articles/2026-[^<]+</loc>' | sed -E 's|.*/articles/||;s|</loc>$||' | sort -u)
orphans=0; orphan_list=""
while IFS= read -r s; do
  [ -z "$s" ] && continue
  if ! echo "$sitemap_arts" | grep -qxF "$s"; then
    orphans=$((orphans+1))
    orphan_list="$orphan_list  $s\n"
  fi
done <<< "$home_arts"
if [ "$orphans" -eq 0 ]; then ok "home links subset of sitemap"; else ko "home links NOT in sitemap ($orphans orphans)"; fi

# === Check 2: sitemap URLs return HTTP 200 (sample 10) ===
bad=0; total=0
for url in $(echo "$SITEMAP" | grep -oE '<loc>[^<]+</loc>' | sed 's|<loc>||;s|</loc>||' | head -15); do
  [ -z "$url" ] && continue
  total=$((total+1))
  code=$(curl -sI "$url" -o /dev/null -w "%{http_code}" --max-time 10 2>/dev/null || echo "000")
  if [ "$code" != "200" ] && [ "$code" != "301" ]; then bad=$((bad+1)); fi
done
[ "$bad" -eq 0 ] && ok "sitemap URLs return 200 (sampled $total)" || ko "sitemap: $bad/$total non-200"

# === Check 3: BlogPosting + BreadcrumbList on articles (sample 5) ===
miss=0
for url in $(echo "$SITEMAP" | grep -oE '<loc>[^<]+/articles/2026-[^<]+</loc>' | sed 's|<loc>||;s|</loc>||' | head -5); do
  body=$(curl -fsS "$url" --max-time 10 2>/dev/null || echo "")
  echo "$body" | grep -q '"BlogPosting"' || miss=$((miss+1))
  echo "$body" | grep -q 'BreadcrumbList' || miss=$((miss+1))
done
[ "$miss" -eq 0 ] && ok "schemas on sampled articles" || ko "schemas missing ($miss issues)"

# === Check 4: <picture> wraps OG images in article bodies ===
naked=0
for url in $(echo "$SITEMAP" | grep -oE '<loc>[^<]+/articles/2026-[^<]+</loc>' | sed 's|<loc>||;s|</loc>||' | head -5); do
  body=$(curl -fsS "$url" --max-time 10 2>/dev/null || echo "")
  jpg_outside=$(echo "$body" | grep -oE '<img[^>]*src="[^"]*\.jpg"' | grep -v '<picture' | grep 'images/og' | wc -l | tr -d ' ')
  [ "$jpg_outside" -gt 0 ] && naked=$((naked+1))
done
[ "$naked" -eq 0 ] && ok "<picture> wraps OG images in articles" || ko "<picture> missing in $naked articles"

# === Check 5: www → non-www 301 ===
www=$(curl -sIL "https://www.binah.co.il/" -o /dev/null -w "%{http_code}|%{num_redirects}" --max-time 10 2>/dev/null || echo "000|0")
[ "$www" = "200|1" ] && ok "www -> non-www 301" || ko "www redirect: got $www (DNS/config issue — see NOTES.md)"

# === Check 6: no FAQ placeholder ===
faqspam=0
for url in $(echo "$SITEMAP" | grep -oE '<loc>[^<]+/articles/2026-[^<]+</loc>' | sed 's|<loc>||;s|</loc>||' | head -5); do
  body=$(curl -fsS "$url" --max-time 10 2>/dev/null || echo "")
  if echo "$body" | grep -qE 'קראו את המאמר המלא'; then faqspam=$((faqspam+1)); fi
done
[ "$faqspam" -eq 0 ] && ok "no FAQ placeholder" || ko "$faqspam articles have FAQ placeholder"

# === Check 7: cache-control includes s-maxage ===
ch=$(curl -sI "$BASE/" --max-time 10 2>/dev/null | grep -i 'cache-control')
echo "$ch" | grep -qi 's-maxage' && ok "cache-control has s-maxage" || ko "cache-control missing s-maxage"

# === Check 8: no duplicate topics in sitemap ===
sm_total=$(echo "$SITEMAP" | grep -oE '<loc>[^<]*/articles/2026-[^<]*</loc>' | wc -l | tr -d ' ')
sm_unique=$(echo "$SITEMAP" | grep -oE '<loc>[^<]*/articles/2026-[^<]*</loc>' | sed -E 's|.*/articles/[0-9]{4}-[0-9]{2}-[0-9]{2}-||;s|</loc>$||' | sort -u | wc -l | tr -d ' ')
[ "$sm_total" = "$sm_unique" ] && ok "no duplicate topics in sitemap ($sm_total)" || ko "sitemap duplicates: $sm_total total, $sm_unique unique"

# === Check 9: category pages return 200 ===
hub_fail=0
for p in comparisons guides tools business news products; do
  code=$(curl -sI "$BASE/categories/$p.html" -o /dev/null -w "%{http_code}" --max-time 10 2>/dev/null || echo "000")
  [ "$code" != "200" ] && hub_fail=$((hub_fail+1))
done
[ "$hub_fail" -eq 0 ] && ok "all 6 category pages return 200" || ko "$hub_fail category pages not 200"

# === Check 10: RSS feed returns 200 ===
rss_code=$(curl -sI "$BASE/feed.xml" -o /dev/null -w "%{http_code}" --max-time 10 2>/dev/null || echo "000")
[ "$rss_code" = "200" ] && ok "RSS feed returns 200" || ko "RSS feed: $rss_code"

echo ""
echo "==============================="
echo "PASS: $PASS | FAIL: $FAIL"
echo "==============================="
if [ "$FAIL" -gt 0 ]; then
  echo ""
  for f in "${FAILS[@]}"; do echo "  $f"; done
  exit 1
else
  echo "ALL INVARIANTS PASS"
  exit 0
fi
