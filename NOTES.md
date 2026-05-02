# NOTES — פעולות שדורשות התערבות אנושית

## שלב 11 — הרחבת תוכן מאמרים (Claude API)
**סטטוס: TODO**

הסקריפט `scripts/generate_content.py` מוכן. הוא מרחיב מאמרים ב-`articles/2026-*.html` ל-1500+ מילים, מוסיף FAQPage/HowTo schema.

### הוראות הפעלה:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
cd "/Users/sorani/Desktop/site & tools/binah"
python3 scripts/generate_content.py
```

### מה הסקריפט עושה:
- מעבד 50 מאמרים בכל batch
- מוסיף תוכן Hebrew SEO-optimized
- מעדכן wordCount ב-JSON-LD
- מוסיף FAQPage schema למאמרים עם "שאלות נפוצות"
- מוסיף HowTo schema למאמרים עם "צעד-אחר-צעד"
- delay 1 שניה בין קריאות (rate limiting)
- commit + push אחרי כל batch

---

## שלב 13 — Google Search Console Verification
**סטטוס: TODO**

1. כנס ל-[Google Search Console](https://search.google.com/search-console)
2. הוסף property: `https://binah.co.il`
3. בחר **"HTML tag"** verification method
4. העתק את הקוד שמתחיל ב-`google-site-verification`
5. ערוך `index.html` — החלף `REPLACE_ME_WITH_GSC_TOKEN` בקוד האמיתי
6. Push ל-GitHub ● המתן לדפלוי
7. לחץ "Verify" ב-GSC

### לאחר אימות:
- כנס ל-GSC → Sitemaps
- הוסף: `https://binah.co.il/sitemap.xml`
- לחץ Submit

---

## שלב 13 — קובץ אימות GSC
הקובץ `google-site-verification.html` קיים כ-placeholder.
אפשרות חלופית: החלף את תוכן הקובץ בקובץ האמיתי שמוריד Google.

---

## DNS — www redirect
וודא שיש CNAME/redirect מ-www.binah.co.il לאתר הראשי ב-Netlify DNS settings.

---

## RSS Feed
אם רוצים RSS feed ב-`/feed.xml` — יש לכתוב סקריפט generate_rss.py.
