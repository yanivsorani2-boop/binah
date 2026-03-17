# בינה — AI Blog Setup Guide

## מבנה הפרויקט

```
binah/
├── index.html                   ← דף הבית
├── styles.css                   ← עיצוב גלובלי
├── article_claude_vs_gpt4o.html ← כתבה 1
├── article2_ai_video_tools.html ← כתבה 2
├── article3_vibe_coding.html    ← כתבה 3
├── privacy-policy.html          ← מדיניות פרטיות (חובה ל-AdSense)
├── ads.txt                      ← AdSense verification
├── sitemap.xml                  ← מפת אתר ל-Google
├── generate_article.py          ← מחולל כתבות אוטומטי (Claude API)
├── scheduler.py                 ← scheduler יומי
└── automation_master.py         ← packaging ל-Make.com/WordPress
```

---

## שלב 1: התקן תלויות

```bash
pip install anthropic
```

## שלב 2: הגדר API Key

```bash
# הוסף לקובץ ~/.zshrc:
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxx"

# טעין:
source ~/.zshrc
```

## שלב 3: בדוק שהכל עובד

```bash
cd ~/Desktop/binah
python3 generate_article.py --dry-run        # בדיקה ללא API
python3 generate_article.py --list-topics    # רשימת נושאים בתור
python3 generate_article.py                  # יצירת כתבה אחת
```

## שלב 4: הפעל Scheduler אוטומטי (macOS)

```bash
python3 scheduler.py --setup-cron
```

**חשוב:** פתח את הקובץ שנוצר וערוך את ה-API key:
```
~/Library/LaunchAgents/com.binah.scheduler.plist
```
החלף `REPLACE_WITH_YOUR_API_KEY` ← ה-API key שלך.

אז:
```bash
launchctl load ~/Library/LaunchAgents/com.binah.scheduler.plist
```

הסקדיולר יריץ כתבה חדשה בכל יום ראשון, שלישי וחמישי בשעה 8:00.

---

## Google AdSense — הגדרה

### 1. הגש בקשה ל-AdSense
- גש ל-adsense.google.com
- הגש בקשה עם הדומיין שלך
- חכה לאישור (3-14 ימים לאחר שהאתר עולה ויש לו תוכן)

### 2. קבל Publisher ID
- נראה כך: `pub-1234567890123456`

### 3. עדכן ads.txt
- פתח `ads.txt`
- החלף `REPLACE_WITH_YOUR_PUBLISHER_ID` ← ה-ID שלך

### 4. הוסף קוד AdSense לכל דף HTML
- מצא את ה-comment: `<!-- ADSENSE_HEAD_CODE_HERE -->`
- החלף עם הקוד שגוגל נותן (ה-`<script async src="https://pagead2...">`)

### 5. הגדר Ad Units בממשק AdSense
- צור Ad Units מסוג: Leaderboard (728x90), Rectangle (300x250), In-article
- קבל את ה-code לכל unit
- החלף את ה-comments בכתבות:
  - `<!-- ADSENSE_LEADERBOARD_HERE -->` ← קוד ה-leaderboard
  - `<!-- ADSENSE_SIDEBAR_HERE -->` ← קוד ה-rectangle
  - `<!-- ADSENSE_IN_ARTICLE_HERE -->` ← קוד ה-in-article

---

## Google Analytics 4 — הגדרה

1. גש ל-analytics.google.com → צור Property חדש
2. קבל את ה-Measurement ID (G-XXXXXXXXXX)
3. הוסף לכל HTML page במקום `<!-- GA4_CODE_HERE -->`:

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

---

## פרסום האתר

### אפשרות א׳: GitHub Pages (חינמי)
```bash
cd ~/Desktop/binah
git init
git add .
git commit -m "initial"
# Push ל-GitHub → הגדר Pages → דומיין מותאם
```

### אפשרות ב׳: Netlify (חינמי)
- גרור את תיקיית `binah` לממשק Netlify
- חבר דומיין

### אפשרות ג׳: WordPress
- ייבא את ה-HTML דרך WordPress REST API
- הרץ: `python3 automation_master.py` לקבלת JSON מוכן לפרסום

---

## בדיקת האוטומציה

```bash
# בדוק סטטוס
python3 scheduler.py --status

# הרץ ידנית (ללא קשר ליום בשבוע)
python3 scheduler.py --force

# ראה log
tail -f scheduler.log
```

---

## עלויות חודשיות

| שירות | עלות | הערה |
|-------|------|------|
| Anthropic API | ~$2-5 | ~10 כתבות/חודש |
| Hosting (Netlify) | חינמי | |
| דומיין (.co.il) | ~₪40/שנה | |
| Google Analytics | חינמי | |
| Google AdSense | חינמי (מרוויח) | |
| **סה"כ** | **~$5/חודש** | |
