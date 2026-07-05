# binah.co.il — תוכנית מיקוד עסקי

## מטרה
מיקוד האתר בקהל עסקי ישראלי: שימור ~27 מאמרים (עסקים + מדריכים איכותיים), הסרת ~25 מאמרים מיושנים/כפולים עם 301.

## שלבים
1. **מיפוי** — סיכום עמודים ונכסים + טבלת שימור/הסרה. ✅ אושר על-ידי המשתמש.
2. **מערכת עיצוב + דף בית חדש** — design-system.css (tokens) + index.html חדש (גיבוי לישן). ⏳ בביצוע. אין לגעת במאמרים ובעמודים אחרים בשלב זה.
3. **עמודי מקצוע** — בניית 6 עמודי `/solutions/*.html` (lawyers, accountants, realtors, clinics, restaurants, contractors) שדף הבית כבר מקשר אליהם (כרגע placeholders → 404).
4. **מחשבון חיסכון** — בניית `/savings-calculator.html` (teaser קיים בדף הבית).
5. **הסרה** (לאחר אישור בלבד) — מחיקת 25 המאמרים, הוספת 301 ב-netlify.toml, עדכון sitemap.xml, feed.xml, archive.html, עמודי קטגוריה, .protected-checksums.txt.
6. **אימות** — `bash scripts/invariants.sh` (כל 10 הבדיקות חייבות לעבור) + בדיקת הפניות מדגמית.

## Placeholders להחלפה
- מספר וואטסאפ בכפתור הצף: `972500000000` (index.html)

## רשימת שימור מאושרת
biz-ai-accounting-finance, biz-ai-content-writing, biz-ai-customer-service, biz-ai-data-analytics, biz-ai-design-images, biz-ai-hiring-hr, biz-ai-marketing-small-business, biz-ai-seo-website, biz-ai-time-automation, biz-ai-whatsapp-crm, ai-small-business, 2026-04-25-business-ai-tools-israeli-businesses-roi-2026, 2026-04-25-ai-agents-enterprise-2026, 2026-03-24-guide-ai-prompts-guide-for-beginners, 2026-04-25-guide-chatgpt-practical-guide-beginners-to-advanced, 2026-04-25-hebrew-hebrew-ai-tools-review-2026, 2026-04-25-tools-ai-tools-comparison-2026, 2026-04-24-tools-ai-coding-tools-comparison-2026, 2026-04-18-tools-ai-video-tools-comparison-2026, 2026-03-24-tools-best-ai-writing-tools-2026-comparison, 2026-04-25-compare-gemini-2-vs-gpt4o-vs-claude-3-5-comparison-2026, 2026-03-24-gpt5-release-impact-2026, ollama-guide, midjourney-beginners, vibe-coding, perplexity-ai, chatgpt-10-uses.

## מערכת עיצוב (design-system.css)
- רקע: #0A0E1A, משטחים: #111827
- גרדיאנט מותג: כחול חשמלי → סגול → ציאן (כותרות והדגשות)
- CTA: ציאן זוהר, hover עם glow עדין
- טיפוגרפיה: Heebo, כותרות weight 800-900
- כרטיסים: glassmorphism (שקיפות + blur + מסגרת דקה + פינות מעוגלות)
- אנימציות: fade-up בגלילה (IntersectionObserver), בלי ספריות חיצוניות
- RTL מלא, mobile-first

## רשימת הסרה (25)
7 × crazy-*, 10 × product-*, ai-jobs-2025, gemini-2025, gpt5-launch, ai-video-tools, sora-openai, claude-vs-gpt4o, deepseek-r2, prompt-engineering.

## כללים
- אין שינוי עמודים ללא אישור מפורש של המשתמש לכל שלב.
- כל הסרה מלווה ב-301 לקנוני הרלוונטי.
- אין לשנות עיצוב/צבעים.
- commit + push רק לאחר אישור (Netlify מפרסם אוטומטית עם push).
