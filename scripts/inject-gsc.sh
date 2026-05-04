#!/bin/bash
# Usage: bash scripts/inject-gsc.sh "<google-site-verification-token>"
set -e

TOKEN="$1"
if [ -z "$TOKEN" ]; then
  echo "Usage: bash scripts/inject-gsc.sh \"<token>\""
  echo "Get token from Google Search Console → HTML tag verification"
  exit 1
fi

# Replace in all HTML files that have the placeholder
count=0
for f in index.html articles/*.html categories/*.html archive.html comparisons.html tools-hub.html guides-hub.html business-hub.html news-hub.html; do
  if [ -f "$f" ] && grep -q 'REPLACE_ME_WITH_GSC_TOKEN' "$f"; then
    sed -i '' "s/REPLACE_ME_WITH_GSC_TOKEN/${TOKEN}/g" "$f"
    count=$((count+1))
  fi
done

echo "Replaced GSC token in $count files."
echo "Now run: git add -A && git commit -m 'Add GSC verification token' && git push"
