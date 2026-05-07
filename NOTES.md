# NOTES — פעולות שדורשות התערבות אנושית

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

## TODO 3 — ANTHROPIC_API_KEY (חובה לפעולה v6 step 3)
המפתח הקיים ב-~/.env מחזיר 404 על כל המודלים — כנראה חסרים credits או billing.
לתיקון:
1. כנס ל-https://console.anthropic.com/settings/billing
2. הוסף אמצעי תשלום / רכוש credits
3. ודא שהמפתח פעיל: `curl -s https://api.anthropic.com/v1/messages -H "x-api-key: $ANTHROPIC_API_KEY" ...`
4. הרץ: `source ~/.env && export ANTHROPIC_API_KEY && node scripts/write-rich-articles.mjs`
5. אחרי הצלחה: `git add articles/ .merged/ && git commit -m "SEO v6: enrich 17 canonicals" && git push`
