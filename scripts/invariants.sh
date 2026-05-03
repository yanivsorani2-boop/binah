#!/bin/bash
# SEO Invariants Check — all must pass before any push
set -e
PASS=0; FAIL=0; WARN=0

function check {
  local name="$1" actual="$2" expect="$3"
  if [ "$actual" = "$expect" ]; then echo "PASS $name"; PASS=$((PASS+1));
  else echo "FAIL $name: got '$actual', expected '$expect'"; FAIL=$((FAIL+1)); fi
}

echo "=== INVARIANTS CHECK ==="
echo ""

# --- INVARIANT 1: Protected files unchanged ---
if [ -f .protected-checksums.txt ]; then
  tampered=0
  while IFS=' ' read -r hash path; do
    if [ -f "$path" ]; then
      current=$(md5 -r "$path" | awk '{print $1}')
      if [ "$current" != "$hash" ]; then
        echo "FAIL protected file modified: $path"
        tampered=$((tampered+1))
      fi
    fi
  done < .protected-checksums.txt
  if [ "$tampered" -eq 0 ]; then
    echo "PASS protected files intact ($(wc -l < .protected-checksums.txt | tr -d ' ') files)"
    PASS=$((PASS+1))
  else
    FAIL=$((FAIL+tampered))
  fi
else
  echo "WARN .protected-checksums.txt missing"
  WARN=$((WARN+1))
fi

# --- INVARIANT 2: No orphan canonicals (all date-prefixed articles linked from home) ---
total_canonicals=$(ls articles/2026-*.html 2>/dev/null | wc -l | tr -d ' ')
linked_from_home=$(grep -oE 'articles/2026-[^"'\''<>]+\.html' index.html 2>/dev/null | sort -u | wc -l | tr -d ' ')
[ "$linked_from_home" -ge 7 ] && echo "PASS canonicals linked from home: $linked_from_home / $total_canonicals" && PASS=$((PASS+1)) || \
  { echo "FAIL only $linked_from_home canonicals on home (need >=7, total=$total_canonicals)"; FAIL=$((FAIL+1)); }

# --- INVARIANT 3: No duplicate topics ---
unique_topics=$(ls articles/2026-*.html 2>/dev/null | sed -E 's|.*/||;s|^[0-9]{4}-[0-9]{2}-[0-9]{2}-||;s|\.html$||' | sort -u | wc -l | tr -d ' ')
[ "$total_canonicals" = "$unique_topics" ] && echo "PASS no duplicate topics: $total_canonicals = $unique_topics" && PASS=$((PASS+1)) || \
  { echo "FAIL duplicates: $total_canonicals files but only $unique_topics unique topics"; FAIL=$((FAIL+1)); }

# --- INVARIANT 4: Sitemap consistency ---
# Every file in sitemap must exist, every canonical article should be in sitemap
sitemap_missing=0
for url in $(grep -oE 'articles/2026-[^<]+' sitemap.xml 2>/dev/null | sed 's|articles/||'); do
  slug=$(echo "$url" | sed 's|\.html$||')
  if [ ! -f "articles/${slug}.html" ]; then
    sitemap_missing=$((sitemap_missing+1))
  fi
done
check "sitemap entries exist as files" "$sitemap_missing" "0"

# --- INVARIANT 5: BlogPosting on all auto articles ---
miss_bp=$(grep -rL '"BlogPosting"' articles/2026-*.html 2>/dev/null | wc -l | tr -d ' ')
check "BlogPosting on all auto articles" "$miss_bp" "0"

# --- INVARIANT 6: BreadcrumbList on all auto articles ---
miss_bc=$(grep -rL 'BreadcrumbList' articles/2026-*.html 2>/dev/null | wc -l | tr -d ' ')
check "BreadcrumbList on all auto articles" "$miss_bc" "0"

# --- INVARIANT 7: No FAQ placeholder spam ---
faq_spam=$(grep -rl 'קראו את המאמר המלא' articles/*.html 2>/dev/null | wc -l | tr -d ' ')
check "no FAQ placeholder answers" "$faq_spam" "0"

# --- INVARIANT 8: wordCount NOT in BreadcrumbList ---
bad_wc=0
for f in articles/2026-*.html; do
  if python3 -c "
import json,re,sys
h=open('$f').read()
for m in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',h,re.S):
  try:
    d=json.loads(m)
    if d.get('@type')=='BreadcrumbList' and 'wordCount' in d:
      print('bad'); sys.exit(0)
  except: pass
" 2>/dev/null | grep -q bad; then
    bad_wc=$((bad_wc+1))
  fi
done
check "wordCount NOT in BreadcrumbList" "$bad_wc" "0"

# --- INVARIANT 9: articleSection in Hebrew ---
eng_section=$(grep -lE '"articleSection":\s*"(articles|tools|comparisons|guides|business|news|hebrew|crazy|products)"' articles/2026-*.html 2>/dev/null | wc -l | tr -d ' ')
check "articleSection in Hebrew" "$eng_section" "0"

# --- INVARIANT 10: Author name correct (no typo) ---
typo=$(grep -rl 'יניב סורני' articles/ 2>/dev/null | wc -l | tr -d ' ')
check "no author name typo" "$typo" "0"

# --- INVARIANT 11: No generic 'read more' on homepage ---
read_more=$(grep -c 'class="read-more"' index.html 2>/dev/null | tr -d ' ')
check "no read-more on homepage" "$read_more" "0"

# --- INVARIANT 12: RSS feed exists ---
[ -f "feed.xml" ] && echo "PASS feed.xml exists" && PASS=$((PASS+1)) || { echo "FAIL feed.xml missing"; FAIL=$((FAIL+1)); }

# --- INVARIANT 13: Category pages exist ---
for p in comparisons guides tools business news products; do
  [ -f "categories/$p.html" ] && PASS=$((PASS+1)) || { echo "FAIL categories/$p.html missing"; FAIL=$((FAIL+1)); }
done
echo "PASS all 6 category pages exist"

# --- INVARIANT 14: Archive page exists ---
[ -f "archive.html" ] && echo "PASS archive.html exists" && PASS=$((PASS+1)) || { echo "FAIL archive.html missing"; FAIL=$((FAIL+1)); }

# --- INVARIANT 15: Favicon set ---
fav_ok=0
for f in favicon.ico favicon.svg favicon-32x32.png favicon-16x16.png apple-touch-icon.png android-chrome-192x192.png android-chrome-512x512.png site.webmanifest; do
  [ -f "$f" ] && fav_ok=$((fav_ok+1)) || { echo "FAIL favicon missing: $f"; FAIL=$((FAIL+1)); }
done
[ "$fav_ok" -eq 8 ] && echo "PASS all favicons present" && PASS=$((PASS+1))

# --- INVARIANT 16: Homepage size < 150KB ---
sz=$(wc -c < index.html | tr -d ' ')
[ "$sz" -lt 150000 ] && echo "PASS homepage size: ${sz}B" && PASS=$((PASS+1)) || { echo "FAIL homepage too large: ${sz}B"; FAIL=$((FAIL+1)); }

# --- INVARIANT 17: www redirect configured ---
grep -q 'www.binah.co.il' netlify.toml && echo "PASS www redirect in netlify.toml" && PASS=$((PASS+1)) || { echo "FAIL www redirect missing"; FAIL=$((FAIL+1)); }

# --- INVARIANT 18: s-maxage configured ---
grep -q 's-maxage' netlify.toml && echo "PASS s-maxage in netlify.toml" && PASS=$((PASS+1)) || { echo "FAIL s-maxage missing"; FAIL=$((FAIL+1)); }

# --- INVARIANT 19: Internal links (sampled) ---
low_links=0
for f in $(ls articles/2026-*.html | head -10); do
  c=$(grep -oE 'href="/articles/[^"]+' "$f" 2>/dev/null | sort -u | wc -l | tr -d ' ')
  [ "$c" -lt 3 ] && low_links=$((low_links+1))
done
check "internal links >=3 (10 sampled)" "$low_links" "0"

# --- INVARIANT 20: Author box (sampled) ---
no_author=0
for f in $(ls articles/2026-*.html | head -10); do
  grep -q 'author-box' "$f" || no_author=$((no_author+1))
done
check "author box present (10 sampled)" "$no_author" "0"

# --- INVARIANT 21: <picture> tags on home ---
pic=$(grep -c '<picture>' index.html | tr -d ' ')
[ "$pic" -ge 20 ] && echo "PASS <picture> on home: $pic" && PASS=$((PASS+1)) || { echo "FAIL <picture> on home: $pic (need >=20)"; FAIL=$((FAIL+1)); }

# --- WARNINGS (non-blocking) ---
echo ""
gsc=$(grep -c 'REPLACE_ME_WITH_GSC_TOKEN' index.html 2>/dev/null | tr -d ' ')
[ "$gsc" -gt 0 ] && echo "WARN GSC token placeholder (manual action)" && WARN=$((WARN+1))

low_wc=0
for f in articles/2026-*.html; do
  wc_val=$(grep -oE '"wordCount":\s*[0-9]+' "$f" | grep -oE '[0-9]+' | head -1)
  [ -n "$wc_val" ] && [ "$wc_val" -lt 1500 ] && low_wc=$((low_wc+1))
done
[ "$low_wc" -gt 2 ] && echo "WARN $low_wc articles below 1500 words (needs API key)" && WARN=$((WARN+1))

echo ""
echo "==============================="
echo "PASS: $PASS | FAIL: $FAIL | WARN: $WARN"
echo "==============================="
if [ "$FAIL" -eq 0 ]; then
  echo "ALL INVARIANTS PASS"
  [ "$WARN" -gt 0 ] && echo "($WARN non-blocking warnings)"
  exit 0
else
  echo "FIX $FAIL FAILURES BEFORE PUSH"
  exit 1
fi
