# NOTES — פעולות שדורשות התערבות אנושית

## DONE (2026-05-02)
- Consolidated 241 → 63 unique articles (removed doorway pages)
- Fixed BreadcrumbList schema (removed invalid wordCount)
- Added BlogPosting JSON-LD to all articles
- Removed 62 FAQ placeholder schemas
- Created RSS feed at /feed.xml
- Generated favicon PNGs (16, 32, 192, 512)
- Generated WebP + AVIF for all OG images
- Added `<picture>` tags with modern formats
- Removed 150+ generic "read more" anchors
- Added internal links (3-5) to all auto articles
- Added author boxes to all auto articles
- Added www → non-www redirect
- Added stale-while-revalidate cache headers

---

## TODO — Google Search Console Verification

1. כנס ל-[Google Search Console](https://search.google.com/search-console)
2. הוסף property: `https://binah.co.il`
3. בחר **"HTML tag"** verification method
4. העתק את הקוד שמתחיל ב-`google-site-verification`
5. ערוך `index.html` — החלף `REPLACE_ME_WITH_GSC_TOKEN` בקוד האמיתי
6. Push ל-GitHub → המתן לדפלוי
7. לחץ "Verify" ב-GSC

### לאחר אימות:
- כנס ל-GSC → Sitemaps
- הוסף: `https://binah.co.il/sitemap.xml`
- לחץ Submit

---

## TODO — DNS: www redirect
ב-Netlify Dashboard → Domain settings:
1. הוסף `www.binah.co.il` כ-domain alias
2. אם משתמש ב-Netlify DNS: הוסף CNAME record `www → apex-loadbalancer.netlify.com`
3. אם DNS חיצוני (Cloudflare/GoDaddy): הוסף CNAME `www → binah.co.il` (או ל-apex-loadbalancer.netlify.com)
4. ה-redirect עצמו כבר מוגדר ב-netlify.toml (301 www → non-www)

---

## TODO — ANTHROPIC_API_KEY (אופציונלי)
עם API key אפשר:
- לייצר FAQ אמיתיים (לא placeholder) לכל מאמר
- לאחד תוכן כפול באמצעות Claude API
- הרץ: `export ANTHROPIC_API_KEY="sk-ant-..." && node scripts/fix-schema.js`

---

## TODO — הרחבת תוכן מאמרים (Claude API)
הסקריפט `scripts/generate_content.py` מוכן. מרחיב מאמרים ל-1500+ מילים.
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
cd "/Users/sorani/Desktop/site & tools/binah"
python3 scripts/generate_content.py
```
