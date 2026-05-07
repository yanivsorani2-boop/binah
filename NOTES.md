# NOTES — פעולות שדורשות התערבות אנושית

## DONE (v6 — 2026-05-07 — radical consolidation)
- Clustered 63 thin auto articles into 17 canonical groups
- Deleted 46 duplicate HTML files + 138 orphan OG images
- Added 46 x 301 redirects in netlify.toml
- Cleaned sitemap.xml (17 auto articles remain)
- Removed orphan cards from index.html, archive.html, category pages, feed.xml
- All 10 production invariants PASS
- All sampled redirects return 200|1 (301 -> canonical)
- BLOCKED: content enrichment to 3000+ words (API key has no credits — see TODO 3)

## DONE (v5.1 — 2026-05-04)
- Synced sitemap.xml: all 63 canonical articles now indexed (was only 7)
- Replaced invariants.sh with production-aware version (10 curl-based checks)
- Disabled daily auto-generator (daily-update.yml → manual trigger only)
- Created scripts/sync-sitemap.js for future maintenance

## DONE (v5 — 2026-05-04)
- Consolidated 241 → 63 unique articles (removed doorway pages)
- Added 178 × 301 redirects for deleted duplicates
- Fixed BreadcrumbList schema (removed invalid wordCount from all)
- Added BreadcrumbList JSON-LD to all 63 auto articles
- Added BlogPosting JSON-LD to all articles
- Removed 62 FAQ placeholder schemas (spam answers)
- Fixed articleSection to Hebrew in all auto articles
- Fixed author name typo (סורני → סוראני)
- Recalculated accurate wordCount in BlogPosting
- Created RSS feed at /feed.xml (50 items)
- Generated favicon PNGs (16, 32, 192, 512)
- Updated site.webmanifest with correct icon paths
- Generated WebP + AVIF for all 282 OG images
- Added `<picture>` tags (AVIF/WebP/JPG) in homepage cards + hub pages
- Removed 150+ generic "read more" anchors
- Added 30 canonical article cards to homepage (with `<picture>`)
- Created archive.html with all 63 articles
- Created data/articles-archive.json for lazy loading
- Created 6 category hub pages under /categories/ with CollectionPage schema
- Added internal links (3-5) to all auto articles
- Added author boxes to all auto articles
- Added www → non-www 301 redirect in netlify.toml
- Added stale-while-revalidate cache headers
- Added feed.xml cache header (30 min)
- Created .protected-checksums.txt for 14 manual articles
- Created scripts/invariants.sh (26 checks, all PASS)
- Created scripts/inject-gsc.sh for easy GSC token injection
- All pages added to sitemap.xml

---

## TODO 1 — DNS: www redirect
ב-Netlify Dashboard → Domain settings:
1. כנס ל-Netlify Dashboard → Site → Domain management
2. לחץ "Add domain alias" → הקלד `www.binah.co.il`
3. ב-רשם הדומיין (GoDaddy / Cloudflare / אחר) הוסף CNAME record:
   - Name: `www`
   - Value: `apex-loadbalancer.netlify.com`
   - TTL: 3600
4. חזור ל-Netlify ובדוק שה-alias מופיע כ-active
5. ה-redirect ב-netlify.toml כבר מוגדר (301 www → non-www) — אין צורך לשנות שם כלום

---

## TODO 2 — GSC token
1. כנס ל-[Google Search Console](https://search.google.com/search-console)
2. הוסף property `https://binah.co.il` → בחר HTML tag verification
3. העתק את ה-token והרץ:
```bash
bash scripts/inject-gsc.sh "<your-token-here>"
git add -A && git commit -m "Add GSC verification token" && git push
```
4. חזור ל-GSC → לחץ Verify
5. כנס ל-Sitemaps → הוסף `https://binah.co.il/sitemap.xml`

---

## TODO 3 — ANTHROPIC_API_KEY (חובה להרחבת תוכן)
המפתח הקיים ב-~/.env מחזיר 404 על כל המודלים — כנראה חסרים credits או billing.
לתיקון:
1. כנס ל-https://console.anthropic.com/settings/billing
2. הוסף אמצעי תשלום / רכוש credits ($10 מספיק)
3. ודא שהמפתח פעיל:
```bash
source ~/.env && export ANTHROPIC_API_KEY
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-sonnet-4-5-20250514","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```
4. הרץ: `source ~/.env && export ANTHROPIC_API_KEY && node scripts/write-rich-articles.mjs`
5. אחרי הצלחה: `git add articles/ .merged/ && git commit -m "SEO v6: enrich 17 canonicals to 3000+ words" && git push`

---

## TODO 4 — POST-DEPLOY (Google Search Console)
1. כנס ל-Google Search Console → Indexing → Pages
2. סינון "נסרק אך לא נכלל באינדקס" — צריך לרדת מ-61 ל-~10 תוך 4-6 שבועות
3. URL Inspection: הזן את 17 הקנונים החדשים, לחץ "Request Indexing" לכל אחד
4. אחרי 3 שבועות: בדוק כמה מהם עברו ל-"Indexed"
5. אם עדיין יש "crawled but not indexed" — שקול הרחבת התוכן (TODO 3)
