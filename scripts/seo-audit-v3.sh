#!/bin/bash
set -e
B="https://binah.co.il"
PASS=0; FAIL=0; WARN=0
function check {
  local name="$1" actual="$2" expect="$3"
  if [ "$actual" = "$expect" ]; then echo "PASS $name ($actual)"; PASS=$((PASS+1));
  else echo "FAIL $name: got '$actual', expected '$expect'"; FAIL=$((FAIL+1)); fi
}

echo "=== AUDIT v3 ==="
echo ""

# 1. Canonicals discoverable from homepage (local check)
linked=$(grep -oE 'href="articles/2026-[^"]+' index.html | sort -u | wc -l | tr -d ' ')
[ "$linked" -ge 7 ] && echo "PASS canonicals on home: $linked" && PASS=$((PASS+1)) || \
  { echo "FAIL only $linked canonicals linked from home (need >=7)"; FAIL=$((FAIL+1)); }

# 2. FAQ answers not placeholder
bad=$(grep -rl 'קראו את המאמר המלא' articles/*.html 2>/dev/null | wc -l | tr -d ' ')
check "no FAQ placeholder" "$bad" "0"

# 3. <picture> on home
pic=$(grep -c '<picture>' index.html | tr -d ' ')
[ "$pic" -ge 27 ] && echo "PASS <picture> on home: $pic" && PASS=$((PASS+1)) || \
  { echo "FAIL <picture> on home: $pic (need >=27)"; FAIL=$((FAIL+1)); }

# 3b. home size
sz=$(wc -c < index.html | tr -d ' ')
[ "$sz" -lt 90000 ] && echo "PASS home size $sz" && PASS=$((PASS+1)) || \
  { echo "FAIL home size $sz (target < 90000)"; FAIL=$((FAIL+1)); }

# 4. www redirect in config
if grep -q 'www.binah.co.il' netlify.toml; then
  echo "PASS www redirect configured"
  PASS=$((PASS+1))
else
  echo "FAIL www redirect missing"
  FAIL=$((FAIL+1))
fi

# 5. Hub pages exist
for p in comparisons guides tools business news products; do
  if [ -f "categories/$p.html" ]; then
    echo "PASS hub /categories/$p.html exists"
    PASS=$((PASS+1))
  else
    echo "FAIL hub /categories/$p.html missing"
    FAIL=$((FAIL+1))
  fi
done

# 6. JPG always in <picture>
jpg_naked=$(grep -rE '<img[^>]*src="/images/og/[^"]+\.jpg"' --include='*.html' . 2>/dev/null | grep -v '<picture>' | grep -v 'meta' | wc -l | tr -d ' ')
check "all JPGs wrapped in <picture>" "$jpg_naked" "0"

# 7. GSC token
gsc=$(grep -c 'REPLACE_ME_WITH_GSC_TOKEN' index.html | tr -d ' ')
if [ "$gsc" -eq 0 ]; then
  echo "PASS GSC token replaced"
  PASS=$((PASS+1))
else
  echo "WARN GSC token still placeholder (manual action needed)"
  WARN=$((WARN+1))
fi

# 8. Archive page
if [ -f "archive.html" ]; then
  echo "PASS archive.html exists"
  PASS=$((PASS+1))
else
  echo "FAIL archive.html missing"
  FAIL=$((FAIL+1))
fi

# 9. Author name fix
typo=$(grep -rl 'יניב סורני' articles/ 2>/dev/null | wc -l | tr -d ' ')
check "no author typo" "$typo" "0"

# 10. articleSection in Hebrew
eng=$(grep -lE '"articleSection":\s*"(articles|tools|comparisons|guides|business)"' articles/2026-*.html 2>/dev/null | wc -l | tr -d ' ')
check "articleSection in Hebrew" "$eng" "0"

# 11. BreadcrumbList on canonicals
miss_bc=0
for slug in 2026-04-25-ai-agents-enterprise-2026 2026-04-25-guide-chatgpt-practical-guide-beginners-to-advanced 2026-04-25-hebrew-hebrew-ai-tools-review-2026; do
  if [ -f "articles/${slug}.html" ]; then
    cnt=$(grep -c 'BreadcrumbList' "articles/${slug}.html" | tr -d ' ')
    [ "$cnt" -eq 0 ] && miss_bc=$((miss_bc+1))
  fi
done
check "BreadcrumbList on canonicals" "$miss_bc" "0"

# 12. Word count (warning only if API key missing)
low=0
for f in articles/2026-*.html; do
  wc_val=$(grep -oE '"wordCount":\s*[0-9]+' "$f" | grep -oE '[0-9]+' | head -1)
  [ -n "$wc_val" ] && [ "$wc_val" -lt 1500 ] && low=$((low+1))
done
if [ "$low" -le 2 ]; then
  echo "PASS word counts (<=2 below 1500)"
  PASS=$((PASS+1))
else
  echo "WARN $low articles below 1500 words (needs ANTHROPIC_API_KEY to expand)"
  WARN=$((WARN+1))
fi

# 13. BlogPosting on all articles
miss_bp=$(grep -rL '"BlogPosting"' articles/*.html 2>/dev/null | wc -l | tr -d ' ')
check "BlogPosting on all articles" "$miss_bp" "0"

# 14. RSS feed
if [ -f "feed.xml" ]; then
  echo "PASS RSS feed.xml exists"
  PASS=$((PASS+1))
else
  echo "FAIL RSS feed.xml missing"
  FAIL=$((FAIL+1))
fi

# 15. Internal links per article
low_links=0
for f in $(ls articles/2026-*.html | head -10); do
  c=$(grep -oE 'href="/articles/[^"]+' "$f" 2>/dev/null | sort -u | wc -l | tr -d ' ')
  [ "$c" -lt 3 ] && low_links=$((low_links+1))
done
check "internal links >=3 per article (10 sampled)" "$low_links" "0"

# 16. Author box
no_author=0
for f in $(ls articles/2026-*.html | head -10); do
  grep -q 'author-box' "$f" || no_author=$((no_author+1))
done
check "author box on articles (10 sampled)" "$no_author" "0"

echo ""
echo "=== SUMMARY ==="
echo "PASS: $PASS, FAIL: $FAIL, WARN: $WARN"
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CRITICAL CHECKS PASSED"
  [ "$WARN" -gt 0 ] && echo "(${WARN} warnings — manual action or API key needed)"
else
  echo "FIX REMAINING ISSUES"
  exit 1
fi
