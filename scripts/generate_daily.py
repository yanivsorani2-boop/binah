#!/usr/bin/env python3
"""
Daily content generator for binah.co.il
Runs via GitHub Actions every day at 7am Israel time.
"""

import anthropic
import os
import re
import json
import datetime
from pathlib import Path

# ── Setup ──────────────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ['CLAUDE_API_KEY'])
ROOT   = Path(__file__).parent.parent
TODAY  = datetime.date.today()
TODAY_STR = TODAY.strftime('%Y-%m-%d')
MONTHS_HE = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני',
             'יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר']

def he_date(d):
    return f"{d.day} {MONTHS_HE[d.month-1]} {d.year}"

def ask_claude(prompt, max_tokens=4000):
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

def parse_json(raw):
    """Robust JSON parser that handles Claude's occasional formatting issues."""
    raw = raw.strip()
    # Strip markdown code fences
    raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^```\s*',     '', raw, flags=re.MULTILINE)
    raw = re.sub(r'```\s*$',     '', raw)
    raw = raw.strip()

    # First try direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Strategy: extract body_html separately, then parse the rest
    try:
        body_match = re.search(r'"body_html"\s*:\s*"(.*?)"(?=\s*[,}])', raw, re.DOTALL)
        if body_match:
            body_html = body_match.group(1)
            # Replace the body_html value with a placeholder
            placeholder = '__BODY_HTML_PLACEHOLDER__'
            safe_raw = raw[:body_match.start(1)] + placeholder + raw[body_match.end(1):]
            data = json.loads(safe_raw)
            data['body_html'] = body_html.encode().decode('unicode_escape') if '\\n' in body_html else body_html
            return data
    except Exception:
        pass

    # Last resort: extract fields with regex
    def extract(key):
        m = re.search(rf'"{key}"\s*:\s*"(.*?)"(?=\s*[,}}])', raw, re.DOTALL)
        return m.group(1) if m else ''
    def extract_list(key):
        m = re.search(rf'"{key}"\s*:\s*\[(.*?)\]', raw, re.DOTALL)
        if not m: return []
        return re.findall(r'"([^"]+)"', m.group(1))
    def extract_html(key):
        # body_html may span many lines
        m = re.search(rf'"{key}"\s*:\s*"([\s\S]+?)"(?=\s*\n?\s*[}},])', raw)
        return m.group(1) if m else ''

    return {
        'slug':       extract('slug'),
        'title':      extract('title'),
        'category':   extract('category'),
        'cat_key':    extract('cat_key'),
        'excerpt':    extract('excerpt'),
        'read_time':  extract('read_time'),
        'tags':       extract_list('tags'),
        'body_html':  extract_html('body_html'),
    }


# ── Niche definitions ───────────────────────────────────────────────────────
# Each niche: key, Hebrew name, category key, weekly day (0=Mon … 6=Sun)
NICHES = [
    {
        'key':      'tools',
        'name':     'כלי AI',
        'cat_key':  'tools',
        'category': 'כלים',
        'weekly_day': 0,   # Monday
        'focus':    'כלים וטכנולוגיות AI חדשות — ביקורות, השוואות, טיפים לשימוש',
    },
    {
        'key':      'business',
        'name':     'עסקים ישראלים',
        'cat_key':  'analysis',
        'category': 'עסקים',
        'weekly_day': 1,   # Tuesday
        'focus':    'שימושי AI לעסקים ישראלים — חיסכון בזמן, אוטומציה, ROI',
    },
    {
        'key':      'compare',
        'name':     'השוואות AI',
        'cat_key':  'compare',
        'category': 'השוואה',
        'weekly_day': 2,   # Wednesday
        'focus':    'השוואות בין מודלים וכלי AI — יתרונות, חסרונות, מחירים',
    },
    {
        'key':      'hebrew',
        'name':     'AI בעברית',
        'cat_key':  'tools',
        'category': 'כלים',
        'weekly_day': 3,   # Thursday
        'focus':    'כלי AI עם תמיכה בעברית — בדיקות, ביקורות, כיצד להפיק את המיטב',
    },
    {
        'key':      'guide',
        'name':     'מדריכים',
        'cat_key':  'guide',
        'category': 'מדריך',
        'weekly_day': 4,   # Friday
        'focus':    'מדריכים מעשיים לשימוש ב-AI — צעד אחר צעד לכל רמה',
    },
]


# ── 1. Daily Article (general) ─────────────────────────────────────────────
def generate_article(date_str):
    prompt = f"""אתה עורך תוכן של אתר חדשות AI בעברית בשם "בינה".
כתוב כתבה מקצועית ומעניינת על נושא AI רלוונטי לתאריך {date_str}.

החזר JSON נקי בלבד (ללא markdown):
{{
  "slug": "כינוי-באנגלית-עם-מקפים-קצר",
  "title": "כותרת הכתבה בעברית",
  "category": "אחת מ: חדשות / כלים / ניתוח / השוואה / מדריך",
  "cat_key": "אחת מ: news / tools / analysis / compare / guide",
  "excerpt": "תקציר של משפט אחד-שניים",
  "read_time": "X דקות",
  "tags": ["תג1", "תג2", "תג3"],
  "body_html": "תוכן HTML מלא — פסקאות <p>, כותרות <h2>, רשימות <ul><li>. 700-900 מילים."
}}

כתיבה עיתונאית בעברית. נושאים: מודלים חדשים, כלים, מחקרים, שימושים עסקיים, טרנדים."""

    return parse_json(ask_claude(prompt, 5000))


# ── 2. Niche Daily Article ─────────────────────────────────────────────────
def generate_niche_article(niche, date_str):
    prompt = f"""אתה עורך תוכן של אתר חדשות AI בעברית בשם "בינה".
כתוב כתבה מקצועית בנישה: {niche['name']}.
תאריך: {date_str}.
מיקוד: {niche['focus']}

החזר JSON נקי בלבד (ללא markdown):
{{
  "slug": "כינוי-באנגלית-עם-מקפים-קצר",
  "title": "כותרת הכתבה בעברית",
  "category": "{niche['category']}",
  "cat_key": "{niche['cat_key']}",
  "excerpt": "תקציר של משפט אחד-שניים",
  "read_time": "X דקות",
  "tags": ["תג1", "תג2", "תג3"],
  "body_html": "תוכן HTML מלא — פסקאות <p>, כותרות <h2>, רשימות <ul><li>. 600-800 מילים."
}}

כתיבה מקצועית ומעשית בעברית."""

    return parse_json(ask_claude(prompt, 4500))


def build_article_html(data, date_str, slug=''):
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in data['tags'])
    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <script>(function(){{var t=localStorage.getItem('binah-theme');if(t==='light')document.documentElement.setAttribute('data-theme','light');}})();</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{data['excerpt']}">
  <meta property="og:title" content="{data['title']}">
  <meta property="og:type" content="article">
  <meta name="robots" content="index, follow">
  <title>{data['title']} | בינה</title>
  <link rel="stylesheet" href="../styles.min.css">
  <link rel="canonical" href="https://binah.co.il/articles/{slug}.html">
  <meta property="og:url" content="https://binah.co.il/articles/{slug}.html">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="בינה">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-MG65DD6GYJ"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-MG65DD6GYJ');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9475752562192165" crossorigin="anonymous"></script>
</head>
<body>
<header>
  <div class="container">
    <div class="nav-inner">
      <a href="../index.html" class="logo">בינה ✦</a>
      <nav id="main-nav">
        <a href="../index.html">ראשי</a>
        <a href="../index.html#articles">מאמרים</a>
        <a href="../guides.html">מדריכים</a>
        <a href="../tools.html">כלים</a>
        <a href="../quiz.html">בחר AI</a>
        <a href="../business.html">AI לעסקים</a>
        <a href="../ai-products.html">מוצרי AI</a>
        <a href="../weekly-news.html">חדשות</a>
        <a href="../ai-crazy.html">AI מטורף</a>
      </nav>
      <div style="display:flex;align-items:center;gap:10px;flex-shrink:0">
        <button class="theme-toggle" onclick="toggleTheme()" aria-label="החלף ערכת נושא">
          <span class="icon-dark">🌙 כהה</span>
          <span class="icon-light">☀️ בהיר</span>
        </button>
        <button class="hamburger" id="hamburger" aria-label="תפריט" onclick="toggleMenu()">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </div>
</header>

<div class="container">
  <div class="ad-zone ad-banner"><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-9475752562192165" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>
</div>

<div class="container">
  <div class="article-header">
    <span class="category">{data['category']}</span>
    <h1>{data['title']}</h1>
    <div class="meta">
      <span>📅 {date_str}</span>
      <span>⏱ {data['read_time']} קריאה</span>
      <span>✍ צוות בינה</span>
    </div>
  </div>
</div>

<div class="container">
  <div class="article-layout">
    <main class="article-body">
      <button class="btn-back" onclick="history.back()">→ חזרה</button>
      {data['body_html']}
      <div class="article-tags" style="margin-top:32px;display:flex;gap:8px;flex-wrap:wrap">
        {tags_html}
      </div>
    </main>
    <aside class="article-sidebar">
      <div class="sidebar-widget">
        <h3>מדריכים מומלצים</h3>
        <ul>
          <li><a href="../guides/guide-chatgpt.html">מדריך ChatGPT</a></li>
          <li><a href="../guides/guide-prompt-basics.html">Prompt Engineering</a></li>
          <li><a href="../guides/guide-claude.html">מדריך Claude AI</a></li>
          <li><a href="../guides/guide-ollama.html">מדריך Ollama</a></li>
        </ul>
      </div>
      <div class="sidebar-widget">
        <h3>כלים</h3>
        <ul>
          <li><a href="../tools.html">כל כלי ה-AI</a></li>
          <li><a href="../quiz.html">איזה AI מתאים לי?</a></li>
        </ul>
      </div>
      <div class="sidebar-widget">
        <h3>חדשות שבועיות</h3>
        <ul>
          <li><a href="../weekly-news.html">גיליון השבוע</a></li>
        </ul>
      </div>
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
        <li><a href="../tools.html">כלים</a></li>
        <li><a href="../weekly-news.html">חדשות</a></li>
        <li><a href="../ai-crazy.html">AI מטורף</a></li>
      </ul></div>
      <div class="footer-col"><h4>מידע</h4><ul>
        <li><a href="../privacy-policy.html">מדיניות פרטיות</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom"><span>© 2025 בינה. כל הזכויות שמורות.</span></div>
  </div>
</footer>

<button id="back-to-top" aria-label="חזרה לראש" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<script src="../site.min.js"></script>
<script src="../header-bg.min.js"></script>
<script src="/tracker.js"></script>
</body>
</html>"""


def inject_article_index(data, slug, date_str):
    path = ROOT / 'index.html'
    html = path.read_text()
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in data['tags'][:3])
    card = f"""        <!-- NEW_ARTICLES_HERE -->
        <article class="article-card has-thumb reveal" data-cat="{data['cat_key']}">
          <div class="card-thumb"><a href="articles/{slug}.html" class="thumb-title">{data['title']}</a></div>
          <div class="card-body">
            <span class="card-category cat-{data['cat_key']}">{data['category']}</span>
            <p class="card-excerpt">{data['excerpt']}</p>
            <div class="card-tags">{tags_html}</div>
            <div class="card-meta"><span>⏱ {data['read_time']} · {date_str}</span><a href="articles/{slug}.html" class="read-more">קרא עוד ←</a></div>
          </div>
        </article>"""
    html = html.replace('        <!-- NEW_ARTICLES_HERE -->', card, 1)
    path.write_text(html)


# ── 3. Daily AI-Crazy Story ────────────────────────────────────────────────
def generate_crazy_story(date_str):
    prompt = f"""אתה עורך של "AI מטורף" — כתבות על הדברים הכי מדהימים בעולם ה-AI.
כתוב כותרת ותקציר לסיפור יומי מרתק לתאריך {date_str}.

החזר JSON נקי בלבד:
{{
  "title": "כותרת קצרה ומושכת",
  "cat_key": "אחד מ: news / analysis / compare / tools / review",
  "excerpt": "2-3 משפטים מרתקים שגורמים לרצות לקרוא עוד",
  "tags": ["תג1", "תג2"]
}}

נושאים: הישגים מדהימים, שימושים בלתי צפויים, רובוטיקה, יצירתיות, רגולציה מפתיעה."""

    return parse_json(ask_claude(prompt, 600))


def inject_crazy_story(data, date_str):
    path = ROOT / 'ai-crazy.html'
    html = path.read_text()
    tags_html = ''.join(f'<span class="news-tag">{t}</span>' for t in data['tags'])
    card = f"""    <!-- NEW_CRAZY_STORIES_HERE -->
      <div class="news-card has-thumb reveal" data-cat="{data['cat_key']}">
        <div class="card-thumb"><div class="thumb-title">{data['title']}</div></div>
        <div class="card-body">
          <div class="news-card-top">
            <span class="news-num">{date_str}</span>
            <span class="new-badge">חדש</span>
          </div>
          <p class="news-card-body">{data['excerpt']}</p>
          <div class="news-card-footer">
            {tags_html}
          </div>
        </div>
      </div>"""
    html = html.replace('    <!-- NEW_CRAZY_STORIES_HERE -->', card, 1)
    path.write_text(html)


# ── 4. Niche Weekly Roundup ────────────────────────────────────────────────
def generate_niche_weekly(niche, date_str):
    prompt = f"""אתה עורך של "בינה" — אתר חדשות AI בעברית.
צור סיכום שבועי לנישה: {niche['name']}.
תאריך: {date_str}. מיקוד: {niche['focus']}

החזר JSON נקי בלבד:
{{
  "slug": "weekly-{niche['key']}-כינוי-קצר",
  "title": "כותרת לסיכום השבועי בעברית",
  "category": "{niche['category']}",
  "cat_key": "{niche['cat_key']}",
  "excerpt": "תקציר של 2 משפטים",
  "read_time": "X דקות",
  "tags": ["תג1", "תג2", "תג3"],
  "body_html": "HTML מלא — 4-5 פריטים עם <h2> לכל אחד, פסקאות <p>. 500-700 מילים."
}}"""

    return parse_json(ask_claude(prompt, 4000))


# ── 5. Weekly Issue (Sundays) ──────────────────────────────────────────────
def generate_weekly_issue(date_str):
    prompt = f"""אתה עורך ראשי של "בינה" — אתר חדשות AI בעברית.
צור גיליון שבועי מקיף לשבוע {date_str}.

החזר JSON נקי בלבד:
{{
  "issue_title": "שבוע [תאריך] — [תיאור קצר]",
  "issue_sub": "תת כותרת — 4 נושאים עיקריים",
  "stories": [
    {{"num":"01","title":"כותרת 1","cat_key":"news","body":"3-4 משפטים","tags":["תג1","תג2"]}},
    {{"num":"02","title":"כותרת 2","cat_key":"analysis","body":"3-4 משפטים","tags":["תג1","תג2"]}},
    {{"num":"03","title":"כותרת 3","cat_key":"tools","body":"3-4 משפטים","tags":["תג1","תג2"]}},
    {{"num":"04","title":"כותרת 4","cat_key":"compare","body":"3-4 משפטים","tags":["תג1","תג2"]}}
  ],
  "tools": [
    {{"name":"שם כלי","cat_key":"tips","desc":"משפט תיאור","badge":"חדש"}},
    {{"name":"שם כלי","cat_key":"analysis","desc":"משפט תיאור","badge":"עדכון"}},
    {{"name":"שם כלי","cat_key":"review","desc":"משפט תיאור","badge":"v2"}}
  ],
  "forecast": ["תחזית 1", "תחזית 2"]
}}"""

    return parse_json(ask_claude(prompt, 3000))


def build_weekly_html(data, date_str, week_slug):
    stories_html = ''
    for i, s in enumerate(data['stories']):
        featured = 'featured-news-card ' if i == 0 else ''
        badge    = '<span class="new-badge">חם</span>' if i == 0 else ''
        tags_html = ''.join(f'<span class="news-tag">{t}</span>' for t in s['tags'])
        stories_html += f"""
      <div class="news-card {featured}has-thumb reveal" data-cat="{s['cat_key']}">
        <div class="card-thumb"><div class="thumb-title">{s['title']}</div></div>
        <div class="card-body">
          <div class="news-card-top"><span class="news-num">{s['num']}</span>{badge}</div>
          <p class="news-card-body">{s['body']}</p>
          <div class="news-card-footer">{tags_html}</div>
        </div>
      </div>"""

    tools_html = ''
    for t in data.get('tools', []):
        tools_html += f"""
      <div class="tool-card has-thumb reveal" data-cat="{t['cat_key']}">
        <div class="card-thumb" style="height:100px"><div class="thumb-title" style="font-size:1.02rem;padding:20px 14px 10px">{t['name']}</div></div>
        <div class="card-body">
          <p class="tool-card-desc">{t['desc']}</p>
          <span class="news-tag">{t['badge']}</span>
        </div>
      </div>"""

    forecast_html = ''.join(f'<li>{f}</li>' for f in data['forecast'])

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <script>(function(){{var t=localStorage.getItem('binah-theme');if(t==='light')document.documentElement.setAttribute('data-theme','light');}})();</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="גיליון שבועי {date_str} — {data['issue_sub']}">
  <meta name="robots" content="index, follow">
  <title>{data['issue_title']} | בינה</title>
  <link rel="stylesheet" href="../styles.min.css">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-MG65DD6GYJ"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-MG65DD6GYJ');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9475752562192165" crossorigin="anonymous"></script>
</head>
<body>
<header>
  <div class="container">
    <div class="nav-inner">
      <a href="../index.html" class="logo">בינה ✦</a>
      <nav id="main-nav">
        <a href="../index.html">ראשי</a>
        <a href="../index.html#articles">מאמרים</a>
        <a href="../guides.html">מדריכים</a>
        <a href="../tools.html">כלים</a>
        <a href="../quiz.html">בחר AI</a>
        <a href="../business.html">AI לעסקים</a>
        <a href="../ai-products.html">מוצרי AI</a>
        <a href="../weekly-news.html" class="active">חדשות</a>
        <a href="../ai-crazy.html">AI מטורף</a>
      </nav>
      <div style="display:flex;align-items:center;gap:10px;flex-shrink:0">
        <button class="theme-toggle" onclick="toggleTheme()" aria-label="החלף ערכת נושא">
          <span class="icon-dark">🌙 כהה</span>
          <span class="icon-light">☀️ בהיר</span>
        </button>
        <button class="hamburger" id="hamburger" aria-label="תפריט" onclick="toggleMenu()">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </div>
</header>

<section style="padding:48px 0 64px">
  <div class="container">
    <div class="news-issue-header reveal">
      <div class="news-issue-label">גיליון שבועי</div>
      <h1 class="news-issue-title">{data['issue_title']}</h1>
      <p class="news-issue-sub">{data['issue_sub']}</p>
      <div style="margin-top:16px">
        <a href="../weekly-news.html" class="btn-outline" style="font-size:0.85rem">← כל הגיליונות</a>
      </div>
    </div>

    <div class="news-cards-grid">{stories_html}
    </div>

    <div class="news-section-header reveal" style="margin-top:56px">
      <span class="section-num">02</span>
      <h2>כלי AI חדשים שכדאי לנסות</h2>
    </div>
    <div class="tools-row">{tools_html}
    </div>

    <div class="news-forecast reveal">
      <div class="news-forecast-icon">🔭</div>
      <div>
        <h3>תחזיות לשבוע הבא</h3>
        <ul>{forecast_html}</ul>
      </div>
    </div>

    <div style="margin-top:40px;text-align:center">
      <a href="../weekly-news.html" class="btn-primary">← לגיליונות נוספים</a>
    </div>
  </div>
</section>

<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand"><div class="logo">בינה ✦</div><p>הבלוג המוביל בעברית על בינה מלאכותית.</p></div>
      <div class="footer-col"><h4>תוכן</h4><ul>
        <li><a href="../index.html">ראשי</a></li>
        <li><a href="../guides.html">מדריכים</a></li>
        <li><a href="../tools.html">כלים</a></li>
        <li><a href="../weekly-news.html">חדשות</a></li>
        <li><a href="../ai-crazy.html">AI מטורף</a></li>
      </ul></div>
      <div class="footer-col"><h4>מידע</h4><ul>
        <li><a href="../privacy-policy.html">מדיניות פרטיות</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom"><span>© 2025 בינה. כל הזכויות שמורות.</span></div>
  </div>
</footer>
<button id="back-to-top" aria-label="חזרה לראש" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<script src="../site.min.js"></script>
<script src="../header-bg.min.js"></script>
<script src="/tracker.js"></script>
<script src="../card-bg.min.js"></script>
</body>
</html>"""


def update_weekly_news_page(data, week_slug, date_str):
    """Move current issue to archive, insert new issue at top"""
    path = ROOT / 'weekly-news.html'
    html = path.read_text()

    html = re.sub(
        r'(<h2 class="news-issue-title">).*?(</h2>)',
        rf'\g<1>{data["issue_title"]}\g<2>', html, count=1)
    html = re.sub(
        r'(<p class="news-issue-sub">).*?(</p>)',
        rf'\g<1>{data["issue_sub"]}\g<2>', html, count=1)

    cards_html = ''
    for i, s in enumerate(data['stories']):
        featured = 'featured-news-card ' if i == 0 else ''
        badge    = '<span class="new-badge">חם</span>' if i == 0 else ''
        tags_html = ''.join(f'<span class="news-tag">{t}</span>' for t in s['tags'])
        cards_html += f"""
      <div class="news-card {featured}has-thumb reveal" data-cat="{s['cat_key']}">
        <div class="card-thumb"><div class="thumb-title">{s['title']}</div></div>
        <div class="card-body">
          <div class="news-card-top"><span class="news-num">{s['num']}</span>{badge}</div>
          <p class="news-card-body">{s['body']}</p>
          <div class="news-card-footer">{tags_html}<a href="weekly/{week_slug}.html" class="btn-guide">קרא עוד ←</a></div>
        </div>
      </div>"""

    html = re.sub(
        r'(<div class="news-cards-grid">).*?(</div><!-- /news-cards-grid -->)',
        rf'\1{cards_html}\n    \2', html, count=1, flags=re.DOTALL)

    new_archive = f"""
      <div class="archive-card has-thumb reveal" data-cat="news">
        <div class="card-thumb" style="height:110px"><div class="thumb-title" style="font-size:0.98rem;padding:22px 14px 10px">{data['issue_title']}</div></div>
        <div class="card-body" style="padding:18px 20px">
          <div class="weekly-date">שבוע {date_str}</div>
          <p style="color:var(--text-muted);font-size:0.82rem">{data['issue_sub']}</p>
          <a href="weekly/{week_slug}.html" class="btn-guide" style="margin-top:12px;font-size:0.78rem">קרא גיליון ←</a>
        </div>
      </div>
      <!-- NEW_ARCHIVE_HERE -->"""

    if '<!-- NEW_ARCHIVE_HERE -->' in html:
        html = html.replace('      <!-- NEW_ARCHIVE_HERE -->', new_archive, 1)
    else:
        html = html.replace('<div class="archive-grid">',
                            '<div class="archive-grid">\n      <!-- NEW_ARCHIVE_HERE -->', 1)
        html = html.replace('      <!-- NEW_ARCHIVE_HERE -->', new_archive, 1)

    path.write_text(html)


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    day_of_week = TODAY.weekday()  # 0=Mon, 6=Sun
    is_sunday   = day_of_week == 6
    date_str    = he_date(TODAY)
    print(f"🚀 עדכון יומי — {date_str}")

    # 1. General daily article
    print("📝 מייצר כתבה יומית כללית...")
    article = generate_article(date_str)
    slug    = f"{TODAY_STR}-{article['slug']}"
    (ROOT / 'articles' / f"{slug}.html").write_text(build_article_html(article, date_str, slug))
    inject_article_index(article, slug, date_str)
    print(f"   ✅ articles/{slug}.html")

    # 2. Niche daily articles (one per niche every day)
    for niche in NICHES:
        print(f"📝 מייצר כתבה לנישה: {niche['name']}...")
        ndata = generate_niche_article(niche, date_str)
        nslug = f"{TODAY_STR}-{niche['key']}-{ndata['slug']}"
        (ROOT / 'articles' / f"{nslug}.html").write_text(build_article_html(ndata, date_str, nslug))
        inject_article_index(ndata, nslug, date_str)
        print(f"   ✅ articles/{nslug}.html")

        # Niche weekly roundup on the designated day
        if day_of_week == niche['weekly_day']:
            print(f"   📰 יום שבועי לנישה {niche['name']} — מייצר סיכום שבועי...")
            wdata = generate_niche_weekly(niche, date_str)
            wslug = f"{TODAY_STR}-{niche['key']}-{wdata['slug']}"
            (ROOT / 'articles' / f"{wslug}.html").write_text(build_article_html(wdata, date_str, wslug))
            inject_article_index(wdata, wslug, date_str)
            print(f"   ✅ articles/{wslug}.html")

    # 3. Daily AI-Crazy story
    print("🤯 מייצר סיפור AI מטורף...")
    crazy = generate_crazy_story(date_str)
    inject_crazy_story(crazy, date_str)
    print("   ✅ נוסף ל-ai-crazy.html")

    # 4. Main weekly issue — Sundays only
    if is_sunday:
        print("📰 יום ראשון — מייצר גיליון שבועי ראשי...")
        weekly_data = generate_weekly_issue(date_str)
        week_slug   = f"week-{TODAY_STR}"
        weekly_html = build_weekly_html(weekly_data, date_str, week_slug)
        (ROOT / 'weekly' / f"{week_slug}.html").write_text(weekly_html)
        update_weekly_news_page(weekly_data, week_slug, date_str)
        print(f"   ✅ weekly/{week_slug}.html")

    print("✅ הכל הושלם!")


if __name__ == '__main__':
    main()
