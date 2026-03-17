#!/usr/bin/env python3
"""
generate_article.py — בינה Blog Auto-Article Generator
Generates Hebrew AI articles per category using Claude API.

Usage:
  python3 generate_article.py --all-categories       # one article per category (daily run)
  python3 generate_article.py --category "מדריך"     # specific category
  python3 generate_article.py --topic "X" --category "כלים"  # custom topic
  python3 generate_article.py --list-topics          # show all queues
  python3 generate_article.py --status               # show today's progress

Requirements:
  pip install anthropic
  export ANTHROPIC_API_KEY="your-key-here"
"""

import anthropic
import json
import os
import re
import sys
import argparse
from datetime import datetime, date
from pathlib import Path

BASE_DIR   = Path(__file__).parent
LOG_FILE   = BASE_DIR / "articles_log.json"
INDEX_FILE = BASE_DIR / "index.html"

# ── Topic queues per category ────────────────────────────────────────────────
# Each category has enough topics for months of daily publishing.
# The scheduler picks the next unpublished topic in order.

TOPICS = {
    "השוואה": [
        {"slug": "gemini-vs-claude-2025",         "topic": "Gemini 2.0 Ultra נגד Claude 3.7 — מי מנצח ב-2025?"},
        {"slug": "midjourney-vs-dalle-4",          "topic": "Midjourney v7 vs DALL-E 4: השוואת יצירת תמונות AI"},
        {"slug": "ai-coding-tools-compare",        "topic": "AI לכתיבת קוד: Copilot vs Cursor vs Codeium — מי הכי טוב?"},
        {"slug": "stable-diffusion-vs-midjourney", "topic": "Stable Diffusion vs Midjourney: מה עדיף לאמנים?"},
        {"slug": "gpt4o-vs-gemini-ultra",          "topic": "GPT-4o vs Gemini Ultra: השוואה מקיפה ב-2025"},
        {"slug": "claude-vs-gemini-code",          "topic": "Claude נגד Gemini לכתיבת קוד — מי מדויק יותר?"},
        {"slug": "chatgpt-vs-perplexity-search",   "topic": "ChatGPT vs Perplexity: מי מנצח בחיפוש מידע?"},
        {"slug": "runway-vs-kling-2025",           "topic": "Runway Gen-3 נגד Kling AI: השוואת יצירת וידאו"},
        {"slug": "notion-ai-vs-obsidian",          "topic": "Notion AI vs Obsidian AI: מה עדיף לניהול ידע?"},
        {"slug": "whisper-vs-otter-transcription", "topic": "Whisper vs Otter.ai: מה עדיף לתמלול בעברית?"},
        {"slug": "replit-vs-bolt-vs-v0",           "topic": "Replit vs Bolt.new vs v0 — איזה כלי Vibe Coding לבחור?"},
        {"slug": "elevenlabs-vs-murf-tts",         "topic": "ElevenLabs vs Murf.ai: השוואת כלי Text-to-Speech"},
        {"slug": "canva-ai-vs-adobe-firefly",      "topic": "Canva AI vs Adobe Firefly: מה עדיף לעיצוב גרפי?"},
    ],
    "כלים": [
        {"slug": "chatgpt-plugins-productivity",   "topic": "ChatGPT Plugins: 7 תוספות שמכפילות את הפרודוקטיביות"},
        {"slug": "ai-marketing-tools-2025",        "topic": "AI לשיווק: 5 כלים שמחליפים צוות שיווק שלם"},
        {"slug": "notion-ai-review",               "topic": "Notion AI: סקירה מלאה — האם זה שווה את הכסף?"},
        {"slug": "elevenlabs-hebrew-review",       "topic": "ElevenLabs: ייצור קבצי שמע בעברית עם AI — סקירה"},
        {"slug": "free-ai-tools-small-business",   "topic": "5 כלי AI לעסקים קטנים שלא עולים כלום"},
        {"slug": "otter-ai-meetings-review",       "topic": "Otter.ai: כלי ה-AI שמתמלל פגישות אוטומטית"},
        {"slug": "make-automations-2025",          "topic": "10 אוטומציות Make.com שחוסכות שעות בשבוע"},
        {"slug": "jasper-ai-copywriting",          "topic": "Jasper AI: כלי הכתיבה השיווקית — שווה 49 דולר לחודש?"},
        {"slug": "gamma-ai-presentations",         "topic": "Gamma.app: יצירת מצגות אוטומטית עם AI"},
        {"slug": "zapier-ai-automation",           "topic": "Zapier AI: אוטומציה חכמה לעסקים בלי קוד"},
        {"slug": "ai-email-tools-2025",            "topic": "3 כלי AI שכותבים את המיילים שלך — השוואה"},
        {"slug": "tome-ai-storytelling",           "topic": "Tome AI: יצירת תוכן ויזואלי מסיפור טקסט"},
        {"slug": "heygen-ai-avatar-video",         "topic": "HeyGen: ייצור וידאו עם אווטאר AI בעברית"},
    ],
    "מדריך": [
        {"slug": "best-prompts-2025",              "topic": "10 פרומפטים שכל אחד צריך לדעת ב-2025"},
        {"slug": "custom-gpt-business",            "topic": "כיצד לבנות GPT מותאם אישית לעסק שלך — שלב אחר שלב"},
        {"slug": "claude-api-beginners",           "topic": "Claude API: מדריך למפתחים מתחילים — שלב אחר שלב"},
        {"slug": "midjourney-advanced-prompts",    "topic": "מדריך פרומפטים מתקדמים ל-Midjourney v7"},
        {"slug": "guide-n8n-automation",           "topic": "n8n: מדריך אוטומציה בקוד פתוח — חינמי ועוצמתי"},
        {"slug": "guide-rag-basics",               "topic": "RAG מוסבר: כיצד AI לומד מהמסמכים שלך"},
        {"slug": "guide-fine-tuning-basics",       "topic": "Fine-tuning: כיצד לאמן מודל AI על הנתונים שלך"},
        {"slug": "guide-ai-content-calendar",      "topic": "מדריך: בניית לוח תוכן שלם עם AI תוך שעה"},
        {"slug": "guide-stable-diffusion-install", "topic": "Stable Diffusion: מדריך התקנה מלא על Mac ו-Windows"},
        {"slug": "guide-cursor-advanced",          "topic": "Cursor: מדריך מתקדם — Composer, Rules ו-Agents"},
        {"slug": "guide-langchain-intro",          "topic": "LangChain למתחילים: בניית אפליקציות AI בפייתון"},
        {"slug": "guide-chatbot-business",         "topic": "כיצד לבנות צ'אטבוט לעסק שלך עם Claude API"},
        {"slug": "guide-ai-seo-2025",              "topic": "SEO עם AI: מדריך מלא לדירוג גבוה ב-2025"},
    ],
    "חדשות": [
        {"slug": "ai-advertising-2025",            "topic": "כיצד AI משנה את עולם הפרסום ב-2025"},
        {"slug": "gpt5-what-we-know",              "topic": "GPT-5: כל מה שידוע עד כה — יכולות, מחיר ומועד שחרור"},
        {"slug": "ai-regulation-israel-2025",      "topic": "רגולציית AI בישראל 2025: מה השתנה ומה צפוי"},
        {"slug": "openai-new-products-2025",       "topic": "OpenAI 2025: כל המוצרים החדשים שהושקו השנה"},
        {"slug": "anthropic-funding-2025",         "topic": "Anthropic מגייסת $4B: מה זה אומר לעתיד Claude"},
        {"slug": "google-gemini-2025-updates",     "topic": "כל עדכוני Gemini 2025: מה חדש ומה מגיע"},
        {"slug": "ai-agents-2025-revolution",      "topic": "AI Agents ב-2025: המהפכה שמשנה את העבודה"},
        {"slug": "deepmind-alphafold3-news",       "topic": "AlphaFold 3 של DeepMind: מה זה אומר למדע הרפואה"},
        {"slug": "ai-hardware-2025",               "topic": "מעבדי AI 2025: NVIDIA H200, Apple M4 ו-Intel Gaudi"},
        {"slug": "meta-llama4-release",            "topic": "Meta Llama 4: המודל הקוד-פתוח שמאיים על GPT"},
        {"slug": "ai-copyright-law-2025",          "topic": "זכויות יוצרים ו-AI ב-2025: פסיקות ומה זה אומר לך"},
        {"slug": "robotics-ai-2025",               "topic": "רובוטיקה עם AI ב-2025: Figure, Tesla Optimus ועוד"},
    ],
    "ניתוח": [
        {"slug": "ai-jobs-future-2025",            "topic": "10 מקצועות שיעלמו בגלל AI — וכיצד להתכונן"},
        {"slug": "ai-productivity-real-numbers",   "topic": "כמה זמן AI באמת חוסך? מחקרים ונתונים אמיתיים"},
        {"slug": "ai-bubble-or-real-2025",         "topic": "בועת AI או מהפכה אמיתית? ניתוח כלכלי לשנת 2025"},
        {"slug": "ai-education-impact",            "topic": "AI בחינוך: השפעה על סטודנטים, מורים ואוניברסיטאות"},
        {"slug": "ai-healthcare-israel",           "topic": "AI ברפואה בישראל: מה קורה ומה עוד יקרה"},
        {"slug": "ai-vs-human-creativity",         "topic": "AI נגד יצירתיות אנושית: היכן עובר הגבול?"},
        {"slug": "cost-of-ai-for-startups",        "topic": "כמה עולה AI לסטארטאפ ישראלי ב-2025? ניתוח עלויות"},
        {"slug": "ai-social-media-impact",         "topic": "כיצד AI שינה את הסושיאל מדיה — ניתוח 2025"},
        {"slug": "israel-ai-ecosystem",            "topic": "אקוסיסטם ה-AI הישראלי: סטארטאפים, השקעות ומגמות"},
        {"slug": "ai-energy-consumption",          "topic": "AI וצריכת אנרגיה: בעיה סביבתית או פתרון?"},
        {"slug": "ai-startups-exit-2025",          "topic": "הייציאות הגדולות של סטארטאפי AI ב-2025"},
    ],
    "סקירה": [
        {"slug": "perplexity-pro-review-2025",     "topic": "Perplexity Pro: סקירה מעמיקה אחרי חודש שימוש"},
        {"slug": "claude-pro-worth-it",            "topic": "Claude Pro ב-2025: האם 20 דולר לחודש שווה זה?"},
        {"slug": "chatgpt-plus-review-2025",       "topic": "ChatGPT Plus 2025: סקירה מעמיקה — יתרונות וחסרונות"},
        {"slug": "copilot-microsoft-review",       "topic": "Microsoft Copilot: סקירה מלאה — האם זה שווה?"},
        {"slug": "cursor-pro-review",              "topic": "Cursor Pro: סקירת מפתח — חודש של שימוש יומיומי"},
        {"slug": "midjourney-pro-review",          "topic": "Midjourney Pro: סקירה מלאה לאמנים ומעצבים"},
        {"slug": "runway-gen3-review",             "topic": "Runway Gen-3 Alpha: סקירת וידאו AI מקצועית"},
        {"slug": "descript-full-review",           "topic": "Descript 2025: סקירה מלאה — עריכה מהטקסט"},
        {"slug": "notion-ai-full-review",          "topic": "Notion AI: סקירה מלאה לאחר 3 חודשים שימוש"},
        {"slug": "gamma-ai-full-review",           "topic": "Gamma.app: סקירה מלאה — מצגות AI בלחיצה"},
        {"slug": "gemini-advanced-review",         "topic": "Gemini Advanced: סקירה מול ChatGPT Plus"},
    ],
    "טיפים": [
        {"slug": "chatgpt-hidden-features",        "topic": "10 פיצ'רים נסתרים ב-ChatGPT שרוב המשתמשים לא מכירים"},
        {"slug": "ai-productivity-hacks",          "topic": "15 טריקי AI שיחסכו לך שעתיים ביום"},
        {"slug": "prompt-mistakes-to-avoid",       "topic": "7 טעויות פרומפטים שכולם עושים — וכיצד לתקן"},
        {"slug": "claude-tips-power-users",        "topic": "10 טיפים ל-Claude שרק משתמשי כוח יודעים"},
        {"slug": "ai-for-freelancers",             "topic": "AI לפרילנסרים: כיצד להכפיל הכנסה עם כלי AI"},
        {"slug": "ai-writing-tips-hebrew",         "topic": "כתיבה בעברית עם AI: 8 טיפים לתוצאות טובות יותר"},
        {"slug": "ai-image-prompt-tips",           "topic": "פרומפטים לתמונות AI: 10 טכניקות שמשפרות כל תמונה"},
        {"slug": "ai-code-review-tips",            "topic": "כיצד להשתמש ב-AI לביקורת קוד — טיפים מעשיים"},
        {"slug": "ai-study-tips-students",         "topic": "AI ללמידה: 8 שיטות לסטודנטים שמשפרות ציונים"},
        {"slug": "ai-business-workflow-tips",      "topic": "7 תהליכים עסקיים שכדאי לאוטומט עכשיו עם AI"},
        {"slug": "ai-content-repurpose-tips",      "topic": "כיצד להפוך כתבה אחת ל-10 פיסות תוכן עם AI"},
    ],
}

# ── Prompt templates per category ─────────────────────────────────────────────
PROMPTS = {
    "השוואה":  "כתוב כתבת השוואה מפורטת ל-{topic}. כלול טבלת השוואה, יתרונות וחסרונות של כל מוצר, המלצה סופית ברורה.",
    "כלים":    "כתוב סקירת כלי AI על {topic}. כלול: מה הכלי עושה, מחיר, יתרונות, חסרונות, למי מתאים, קישור לנסיון חינמי.",
    "מדריך":   "כתוב מדריך מעשי שלב-אחר-שלב על {topic}. כלול: דרישות מוקדמות, כל שלב עם הסבר, טיפים מעשיים, טעויות נפוצות להימנע מהן.",
    "חדשות":   "כתוב כתבת חדשות מנותחת על {topic}. כלול: מה קרה, מה המשמעות, מה השפעה על המשתמש הישראלי, מה צפוי הלאה.",
    "ניתוח":   "כתוב ניתוח מעמיק על {topic}. כלול: נתונים ועובדות, ניתוח מגמות, השפעה על ישראל, מסקנות מעשיות.",
    "סקירה":   "כתוב סקירת מוצר מקצועית על {topic}. כלול: ניסיון שימוש אישי, ציון (1-10) לכל פרמטר, מסקנה: כדאי לקנות?",
    "טיפים":   "כתוב מאמר טיפים מעשי על {topic}. כלול: כל טיפ עם הסבר + דוגמה + פרומפט מוכן לשימוש.",
}

ARTICLE_WRAPPER = '''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <script>
    (function(){{
      var t = localStorage.getItem('binah-theme');
      if (t === 'light') document.documentElement.setAttribute('data-theme','light');
    }})();
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{meta_desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:type" content="article">
  <meta name="robots" content="index, follow">
  <title>{title} | בינה</title>
  <link rel="stylesheet" href="../styles.css">
  <!-- GA4_CODE_HERE --><!-- ADSENSE_HEAD_CODE_HERE -->
</head>
<body>
<header>
  <div class="container">
    <div class="nav-inner">
      <a href="../index.html" class="logo">בינה ✦</a>
      <nav>
        <a href="../index.html">ראשי</a>
        <a href="../index.html#articles">כתבות</a>
        <a href="../guides.html">מדריכים</a>
        <a href="../weekly-news.html">חדשות</a>
      </nav>
      <button class="theme-toggle" onclick="toggleTheme()" aria-label="החלף ערכת נושא">
        <span class="icon-dark">🌙 כהה</span>
        <span class="icon-light">☀️ בהיר</span>
      </button>
    </div>
  </div>
</header>
<div class="container">
  <div class="ad-zone ad-banner"><!-- ADSENSE_LEADERBOARD_HERE --><span>פרסומת</span></div>
</div>
<div class="container">
  <div class="article-header">
    <span class="category">{category}</span>
    <h1>{title}</h1>
    <div class="meta">
      <span>📅 {date}</span>
      <span>⏱ {read_time} דקות קריאה</span>
      <span>✍ צוות בינה</span>
    </div>
  </div>
</div>
<div class="container">
  <div class="article-layout">
    <main class="article-body">
{body}
      <div class="ad-in-article"><!-- ADSENSE_BOTTOM_HERE --><span>פרסומת</span></div>
    </main>
    <aside class="sidebar sticky-sidebar">
      <div class="ad-zone ad-rectangle"><!-- ADSENSE_SIDEBAR_HERE --><span>פרסומת</span></div>
      <div class="widget">
        <div class="widget-title">מדריכים מומלצים</div>
        <div class="widget-list">
          <div class="widget-item"><a href="../guides/guide-chatgpt.html">מדריך ChatGPT</a><span>5 דקות</span></div>
          <div class="widget-item"><a href="../guides/guide-claude.html">מדריך Claude AI</a><span>6 דקות</span></div>
          <div class="widget-item"><a href="../guides/guide-prompt-basics.html">Prompt Engineering</a><span>10 דקות</span></div>
        </div>
      </div>
      <div class="ad-zone" style="min-height:300px"><!-- ADSENSE_SIDEBAR_2_HERE --><span>פרסומת</span></div>
    </aside>
  </div>
</div>
<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand"><div class="logo">בינה ✦</div><p>הבלוג המוביל בעברית על בינה מלאכותית.</p></div>
      <div class="footer-col"><h4>תוכן</h4><ul>
        <li><a href="../index.html">ראשי</a></li>
        <li><a href="../guides.html">מדריכים</a></li>
        <li><a href="../weekly-news.html">חדשות</a></li>
      </ul></div>
      <div class="footer-col"><h4>מידע</h4><ul>
        <li><a href="../privacy-policy.html">מדיניות פרטיות</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom"><span>© 2025 בינה.</span></div>
  </div>
</footer>
<script>
function toggleTheme() {{
  var html = document.documentElement;
  var isLight = html.getAttribute('data-theme') === 'light';
  if (isLight) {{ html.removeAttribute('data-theme'); localStorage.setItem('binah-theme','dark'); }}
  else {{ html.setAttribute('data-theme','light'); localStorage.setItem('binah-theme','light'); }}
}}
</script>
</body>
</html>'''


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text(encoding='utf-8'))
    return {"published": [], "category_indices": {}}


def save_log(log):
    LOG_FILE.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')


def published_today_per_category():
    """Returns set of categories already published today."""
    log = load_log()
    today = date.today().isoformat()
    done = set()
    for a in log.get("published", []):
        if a.get("published_at", "")[:10] == today:
            done.add(a.get("category", ""))
    return done


def next_topic(category):
    """Returns next unpublished topic for category."""
    log = load_log()
    indices = log.get("category_indices", {})
    published_slugs = {a["slug"] for a in log.get("published", [])}
    queue = TOPICS.get(category, [])
    idx = indices.get(category, 0)
    # Find next not-yet-published topic starting from current index
    for i in range(len(queue)):
        t = queue[(idx + i) % len(queue)]
        if t["slug"] not in published_slugs:
            return t, (idx + i) % len(queue)
    # All published — cycle back from start
    return queue[idx % len(queue)], idx % len(queue)


def insert_ads(body):
    """Insert an ad zone after every 2nd <h2> heading."""
    ad = '\n      <div class="ad-in-article"><!-- ADSENSE_IN_ARTICLE_HERE --><span>פרסומת</span></div>\n'
    parts = re.split(r'(<h2[^>]*>)', body)
    result, count = [], 0
    for p in parts:
        result.append(p)
        if re.match(r'<h2', p):
            count += 1
            if count % 2 == 0:
                result.append(ad)
    return ''.join(result)


def he_date():
    months = ["ינואר","פברואר","מרץ","אפריל","מאי","יוני",
              "יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר"]
    d = date.today()
    return f"{d.day} {months[d.month-1]} {d.year}"


def first_p_text(html):
    m = re.search(r'<p[^>]*>(.*?)</p>', html, re.S)
    if not m:
        return ""
    t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return (t[:152] + "...") if len(t) > 155 else t


# ── Core generation ───────────────────────────────────────────────────────────

def generate(category, topic_data):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set.  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    title  = topic_data["topic"]
    slug   = topic_data["slug"]

    prompt_template = PROMPTS.get(category, PROMPTS["כלים"])
    system_prompt = (
        "אתה כותב תוכן מקצועי בעברית לבלוג AI בשם 'בינה'.\n"
        "כתוב בעברית תקינה ומקצועית, כ-900-1200 מילים.\n"
        "כלול כותרות H2 ו-H3, רשימות ✓, טבלת השוואה אם רלוונטי.\n"
        "הוצא רק HTML פנימי (ללא DOCTYPE/html/head/body). השתמש ב-<h2>,<h3>,<p>,<ul>,<li>,<strong>,<table>.\n"
        "אל תוסיף style inline."
    )
    user_prompt = prompt_template.format(topic=title)

    print(f"  → [{category}] {title}")
    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    body = msg.content[0].text.strip()
    body_with_ads = insert_ads(body)

    today_str = he_date()
    read_time = max(4, len(body.split()) // 200)
    meta_desc = first_p_text(body)

    html = ARTICLE_WRAPPER.format(
        title=title, category=category, meta_desc=meta_desc,
        date=today_str, read_time=read_time, body=body_with_ads,
    )

    out_path = BASE_DIR / "articles" / f"{slug}.html"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(html, encoding='utf-8')

    # Update log
    log = load_log()
    log["published"].append({
        "title": title, "slug": slug, "category": category,
        "published_at": datetime.now().isoformat(),
        "word_count": len(body.split()), "read_time": read_time,
    })
    indices = log.setdefault("category_indices", {})
    _, next_idx = next_topic(category)
    indices[category] = (next_idx + 1) % len(TOPICS.get(category, [1]))
    save_log(log)

    # Add card to index.html
    _add_index_card(title, slug, category, today_str)

    print(f"    ✓ Saved: articles/{slug}.html  (~{len(body.split())} מילים)")
    return slug


def _add_index_card(title, slug, category, date_str):
    """Prepend a new article card to the articles-grid in index.html."""
    if not INDEX_FILE.exists():
        return
    cat_data = {
        "השוואה": "compare", "כלים": "tools", "מדריך": "guide",
        "חדשות": "news",    "ניתוח": "analysis", "סקירה": "tools", "טיפים": "tools",
    }
    data_cat = cat_data.get(category, "tools")
    card = f"""
        <article class="article-card" data-cat="{data_cat}">
          <span class="card-category">{category}</span>
          <a href="articles/{slug}.html" class="card-title">{title}</a>
          <p class="card-excerpt">קרא את הכתבה המלאה על {title.split(':')[0]}.</p>
          <div class="card-meta">
            <span>{date_str}</span>
            <a href="articles/{slug}.html" class="read-more">קרא עוד ←</a>
          </div>
        </article>"""

    html = INDEX_FILE.read_text(encoding='utf-8')
    marker = '<div class="articles-grid" id="articles-grid">'
    if marker in html:
        html = html.replace(marker, marker + card)
        INDEX_FILE.write_text(html, encoding='utf-8')


# ── CLI ───────────────────────────────────────────────────────────────────────

def cmd_all_categories(skip_done=True):
    """Generate one article per category. Skip categories already done today."""
    done_today = published_today_per_category() if skip_done else set()
    categories = list(TOPICS.keys())
    print(f"Categories: {len(categories)}  |  Already done today: {len(done_today)}")
    generated = []
    for cat in categories:
        if cat in done_today:
            print(f"  ✓ [{cat}] Already published today — skipping")
            continue
        topic_data, _ = next_topic(cat)
        slug = generate(cat, topic_data)
        generated.append((cat, slug))
    return generated


def cmd_status():
    log = load_log()
    today = date.today().isoformat()
    done = {a["category"]: a for a in log.get("published", []) if a["published_at"][:10] == today}
    print(f"\n📊 Daily Status — {today}")
    print("=" * 55)
    for cat in TOPICS:
        status = "✅" if cat in done else "⏳"
        info   = f"  {done[cat]['title'][:40]}..." if cat in done else ""
        print(f"  {status}  {cat:<10}{info}")
    total = len(log.get("published", []))
    print(f"\n  Total articles ever published: {total}")
    print()


def cmd_list():
    log = load_log()
    published_slugs = {a["slug"] for a in log.get("published", [])}
    indices = log.get("category_indices", {})
    for cat, queue in TOPICS.items():
        idx = indices.get(cat, 0)
        print(f"\n  [{cat}]")
        for i, t in enumerate(queue):
            marker  = "→" if i == idx else " "
            done    = "✓" if t["slug"] in published_slugs else " "
            print(f"    [{done}] {marker} {t['topic'][:60]}")


def main():
    p = argparse.ArgumentParser(description='בינה Article Generator')
    p.add_argument('--all-categories', action='store_true', help='Generate one article per category (skips already done today)')
    p.add_argument('--force-all',      action='store_true', help='Generate for all categories even if already done today')
    p.add_argument('--category',       type=str, help=f'Single category: {list(TOPICS.keys())}')
    p.add_argument('--topic',          type=str, help='Custom topic text (use with --category)')
    p.add_argument('--list-topics',    action='store_true')
    p.add_argument('--status',         action='store_true')
    args = p.parse_args()

    if args.status:
        cmd_status(); return
    if args.list_topics:
        cmd_list(); return
    if args.all_categories:
        cmd_all_categories(skip_done=True); return
    if args.force_all:
        cmd_all_categories(skip_done=False); return
    if args.category:
        cat = args.category
        if cat not in TOPICS:
            print(f"Unknown category: {cat}. Options: {list(TOPICS.keys())}"); sys.exit(1)
        if args.topic:
            topic_data = {"slug": re.sub(r'[^a-z0-9]+', '-', args.topic.lower())[:50].strip('-'), "topic": args.topic}
        else:
            topic_data, _ = next_topic(cat)
        generate(cat, topic_data); return

    p.print_help()


if __name__ == "__main__":
    main()
