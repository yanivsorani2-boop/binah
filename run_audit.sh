#!/bin/bash
echo "=== FINAL AUDIT ===" > audit-results.txt
BASE="https://binah.co.il"

echo "1. noindex check (sample 20):" >> audit-results.txt
fail=0
for f in $(ls articles/2026-*.html | head -20); do
  grep -q 'noindex' "$f" && fail=$((fail+1))
done
echo "  noindex articles: $fail / 20 (expected: 0)" >> audit-results.txt

echo "2. .html redirects:" >> audit-results.txt
redir=$(curl -sIL ${BASE}/articles/claude-vs-gpt4o.html -o /dev/null -w '%{num_redirects}')
echo "  $redir redirect (expected: 1)" >> audit-results.txt

echo "3. Sitemap entries:" >> audit-results.txt
count=$(curl -s ${BASE}/sitemap.xml | grep -c '<loc>')
echo "  $count URLs in sitemap.xml" >> audit-results.txt

echo "4. Cache-Control:" >> audit-results.txt
echo "  $(curl -sI ${BASE}/ | grep -i 'cache-control')" >> audit-results.txt

echo "5. www redirect:" >> audit-results.txt
curl -sIL "https://www.binah.co.il/" -o /dev/null -w '  HTTP %{http_code}, redirects=%{num_redirects}\n' >> audit-results.txt

echo "6. Favicon:" >> audit-results.txt
for p in /favicon.ico /favicon.svg /apple-touch-icon.png /site.webmanifest; do
  echo "  $p: $(curl -sI ${BASE}$p -o /dev/null -w %{http_code})" >> audit-results.txt
done

echo "7. RSS feed:" >> audit-results.txt
curl -sI ${BASE}/feed.xml -o /dev/null -w '  HTTP %{http_code}\n' >> audit-results.txt

echo "8. Hub pages:" >> audit-results.txt
for p in comparisons guides-hebrew tools-hebrew news business-ai; do
  echo "  /$p: $(curl -sI ${BASE}/${p} -o /dev/null -w %{http_code})" >> audit-results.txt
done

echo "9. Homepage HTML size:" >> audit-results.txt
size=$(curl -s ${BASE}/ | wc -c)
echo "  $size bytes" >> audit-results.txt

echo "10. OG images:" >> audit-results.txt
echo "  /images/og/claude-vs-gpt4o.jpg: $(curl -sI ${BASE}/images/og/claude-vs-gpt4o.jpg -o /dev/null -w %{http_code})" >> audit-results.txt

echo "11. Generic anchors:" >> audit-results.txt
echo "  'קרא עוד' count: $(curl -s ${BASE}/ | grep -oE '<a[^>]*>קרא עוד' | wc -l)" >> audit-results.txt

echo "12. Article word counts (sample 5):" >> audit-results.txt
for f in $(ls articles/2026-*.html | head -5); do
  wc=$(grep -oP '"wordCount": \K[0-9]+' "$f" 2>/dev/null || echo "?")
  echo "  $f: $wc words" >> audit-results.txt
done

echo "13. External links rel=nofollow:" >> audit-results.txt
total=$(grep -hoE 'href="https://[^"]+"' articles/*.html 2>/dev/null | grep -v binah.co.il | wc -l)
withrel=$(grep -hoE '<a [^>]*href="https://[^"]+"[^>]*rel="[^"]*nofollow' articles/*.html 2>/dev/null | grep -v binah.co.il | wc -l)
echo "  $withrel / $total external links have rel=nofollow" >> audit-results.txt

echo "14. BlogPosting schema:" >> audit-results.txt
total_arts=$(ls articles/*.html | wc -l)
with_bp=$(grep -lE '"@type".*"BlogPosting"' articles/*.html 2>/dev/null | wc -l)
echo "  $with_bp / $total_arts articles have BlogPosting schema" >> audit-results.txt

echo "15. hreflang on homepage:" >> audit-results.txt
echo "  $(curl -s ${BASE}/ | grep -c 'hreflang') hreflang tags" >> audit-results.txt

echo "" >> audit-results.txt
echo "=== DONE ===" >> audit-results.txt
