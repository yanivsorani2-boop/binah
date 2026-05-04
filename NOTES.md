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
1. הוסף `www.binah.co.il` כ-domain alias
2. הוסף CNAME record: `www → apex-loadbalancer.netlify.com`
3. ה-redirect ב-netlify.toml כבר מוגדר (301 www → non-www)

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

## TODO 3 — ANTHROPIC_API_KEY (אופציונלי)
להרחבת תוכן המאמרים ל-1500+ מילים ולייצור FAQ אמיתיים:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python3 scripts/generate_content.py
```
