#!/usr/bin/env python3
"""
fix_adsense.py — תיקון כל המאמרים לעמידה בדרישות AdSense E-E-A-T
פעולות:
1. מוסיף meta name="author"
2. מוסיף JSON-LD Article + Person schema
3. מחליף "צוות בינה" ב-byline עם קישור לאודות
4. מוסיף "עודכן ונבדק" date
5. מוסיף canonical לדפי 2026-03-18 (כפולות) → 2026-03-19
6. מעדכן footer (מוסיף קישורי אודות/מתודולוגיה)
7. מוסיף "אודות" לנאב בדפי articles
"""

import os
import re
from pathlib import Path

BASE = Path("/Users/sorani/Desktop/site & tools/binah")
ARTICLES_DIR = BASE / "articles"
AUTHOR_NAME = "דניאל לוי"
AUTHOR_URL_ABS = "https://binah.co.il/about.html"
REVIEWED_DATE = "22 אפריל 2026"

# מיפוי כפולות: 2026-03-18 → canonical של 2026-03-19
CANONICAL_MAP = {
    "2026-03-18-ai-agents-enterprise-2026.html":
        "https://binah.co.il/articles/2026-03-19-ai-agents-enterprise-2026.html",
    "2026-03-18-business-ai-tools-israeli-businesses-roi-2026.html":
        "https://binah.co.il/articles/2026-03-19-business-ai-tools-israeli-businesses-roi-2026.html",
    "2026-03-18-compare-gpt4o-vs-claude-vs-gemini-2026.html":
        "https://binah.co.il/articles/2026-03-19-compare-claude-vs-gemini-vs-chatgpt-2026.html",
    "2026-03-18-compare-weekly-compare-models-march-2026.html":
        "https://binah.co.il/articles/2026-03-19-hebrew-weekly-hebrew-ai-tools-march-2026.html",
    "2026-03-18-guide-chatgpt-beginners-step-by-step-guide.html":
        "https://binah.co.il/articles/2026-03-19-guide-chatgpt-beginners-guide-step-by-step.html",
    "2026-03-18-hebrew-hebrew-ai-tools-review-2026.html":
        "https://binah.co.il/articles/2026-03-19-hebrew-hebrew-ai-tools-review-2026.html",
    "2026-03-18-tools-ai-tools-comparison-march-2026.html":
        "https://binah.co.il/articles/2026-03-19-tools-best-ai-coding-tools-2026-comparison.html",
}

JSON_LD_TEMPLATE = """  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{title}",
    "description": "{description}",
    "url": "{url}",
    "datePublished": "{date_published}",
    "dateModified": "2026-04-22",
    "inLanguage": "he",
    "author": {{
      "@type": "Person",
      "name": "דניאל לוי",
      "url": "https://binah.co.il/about.html"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "בינה",
      "url": "https://binah.co.il"
    }}
  }}
  </script>"""

NEW_FOOTER_INFO_COL = """      <div class="footer-col">
        <h4>מידע</h4>
        <ul>
          <li><a href="{prefix}about.html">אודות הכותב</a></li>
          <li><a href="{prefix}methodology.html">מתודולוגיה</a></li>
          <li><a href="{prefix}privacy-policy.html">מדיניות פרטיות</a></li>
          <li><a href="{prefix}disclaimer.html">כתב ויתור</a></li>
          <li><a href="{prefix}contact.html">צור קשר</a></li>
        </ul>
      </div>"""


def extract_meta(html, name):
    m = re.search(rf'<meta\s+name="{name}"\s+content="([^"]*)"', html)
    if not m:
        m = re.search(rf'<meta\s+content="([^"]*)"\s+name="{name}"', html)
    return m.group(1) if m else ""


def extract_og(html, prop):
    m = re.search(rf'<meta\s+property="og:{prop}"\s+content="([^"]*)"', html)
    return m.group(1) if m else ""


def extract_title(html):
    m = re.search(r'<title>([^<]+)</title>', html)
    return m.group(1).split('|')[0].strip() if m else ""


def extract_h1(html):
    m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    return m.group(1).strip() if m else ""


def extract_canonical_url(html):
    m = re.search(r'<link\s+rel="canonical"\s+href="([^"]*)"', html)
    return m.group(1) if m else ""


def extract_date_from_filename(filename):
    m = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
    return m.group(1) if m else "2026-03-18"


def fix_article(filepath, is_articles_subdir=True):
    prefix = "../" if is_articles_subdir else ""
    author_url = f"{prefix}about.html"

    html = filepath.read_text(encoding='utf-8')
    filename = filepath.name
    changed = False

    # 1. meta name="author"
    if 'name="author"' not in html:
        html = html.replace(
            '</head>',
            f'  <meta name="author" content="{AUTHOR_NAME}">\n</head>',
            1
        )
        changed = True

    # 2. JSON-LD schema (אם לא קיים)
    if 'application/ld+json' not in html:
        title = extract_h1(html) or extract_title(html)
        description = extract_meta(html, 'description') or extract_og(html, 'description')
        url = extract_canonical_url(html)
        date_published = extract_date_from_filename(filename)
        if not url:
            if is_articles_subdir:
                url = f"https://binah.co.il/articles/{filename}"
            else:
                url = f"https://binah.co.il/{filename}"
        # clean title for JSON (escape quotes)
        title_clean = title.replace('"', '\\"')
        desc_clean = description.replace('"', '\\"')
        jsonld = JSON_LD_TEMPLATE.format(
            title=title_clean,
            description=desc_clean,
            url=url,
            date_published=date_published
        )
        html = html.replace('</head>', f'{jsonld}\n</head>', 1)
        changed = True

    # 3. byline: "צוות בינה" → link
    if '✍ צוות בינה' in html:
        html = html.replace(
            '✍ צוות בינה',
            f'✍ <a href="{author_url}">{AUTHOR_NAME}</a>'
        )
        changed = True

    # 4. "עודכן ונבדק" — מוסיף לאחר ה-meta div אם לא קיים
    if 'עודכן ונבדק' not in html and '<div class="meta">' in html:
        reviewed_span = f'<span>🔄 עודכן ונבדק: {REVIEWED_DATE}</span>'
        html = html.replace(
            '</div>\n</div>\n\n<div class="container">\n  <div class="article-layout">',
            f'      {reviewed_span}\n    </div>\n</div>\n\n<div class="container">\n  <div class="article-layout">',
            1
        )
        changed = True

    # 5. canonical לכפולות
    if filename in CANONICAL_MAP:
        new_canonical = CANONICAL_MAP[filename]
        # עדכן canonical קיים
        old_canonical_m = re.search(r'<link\s+rel="canonical"\s+href="[^"]*"', html)
        if old_canonical_m:
            html = html.replace(
                old_canonical_m.group(0),
                f'<link rel="canonical" href="{new_canonical}"'
            )
            changed = True

    # 6. nav: הוסף "אודות" אם לא קיים
    if f'href="{prefix}about.html"' not in html and '<nav id="main-nav">' in html:
        html = html.replace(
            '</nav>',
            f'        <a href="{prefix}about.html">אודות</a>\n      </nav>',
            1
        )
        changed = True

    # 7. footer — עדכן עמודת מידע
    if f'href="{prefix}about.html">אודות הכותב' not in html:
        new_col = NEW_FOOTER_INFO_COL.format(prefix=prefix)
        # חפש עמודת מידע קיימת ועדכן אותה
        footer_col_pattern = re.compile(
            r'<div class="footer-col">\s*<h4>מידע</h4>.*?</div>',
            re.DOTALL
        )
        if footer_col_pattern.search(html):
            html = footer_col_pattern.sub(new_col, html, count=1)
            changed = True
        else:
            # הוסף לפני footer-bottom
            html = html.replace(
                '<div class="footer-bottom">',
                f'{new_col}\n    <div class="footer-bottom">',
                1
            )
            changed = True

    if changed:
        filepath.write_text(html, encoding='utf-8')
        print(f"✅ {filepath.name}")
    else:
        print(f"⚪ {filepath.name} (ללא שינוי)")


def fix_main_pages():
    """עדכן דפים ראשיים (לא articles/)"""
    main_pages = [
        BASE / "index.html",
        BASE / "guides.html",
        BASE / "tools.html",
        BASE / "quiz.html",
        BASE / "business.html",
        BASE / "ai-products.html",
        BASE / "weekly-news.html",
        BASE / "ai-crazy.html",
        BASE / "sitemap.html",
        BASE / "privacy-policy.html",
        BASE / "disclaimer.html",
        BASE / "contact.html",
        BASE / "article_claude_vs_gpt4o.html",
        BASE / "article2_ai_video_tools.html",
        BASE / "article3_vibe_coding.html",
    ]
    for p in main_pages:
        if p.exists():
            fix_article(p, is_articles_subdir=False)


def main():
    print("=== מתחיל תיקון AdSense E-E-A-T ===\n")

    # תיקון מאמרים בתיקיית articles/
    print("--- articles/ ---")
    for f in sorted(ARTICLES_DIR.glob("*.html")):
        fix_article(f, is_articles_subdir=True)

    # תיקון דפים ראשיים
    print("\n--- דפים ראשיים ---")
    fix_main_pages()

    print("\n=== סיים! ===")


if __name__ == "__main__":
    main()
