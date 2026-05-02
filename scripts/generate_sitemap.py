#!/usr/bin/env python3
"""
generate_sitemap.py — יוצר sitemap.xml מלא ל-binah.co.il
סורק articles/, guides/, weekly/ רקורסיבית, מדלג על noindex.
הרץ מה-root של הפרויקט: python3 scripts/generate_sitemap.py
"""
import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
BASE = "https://binah.co.il"
TODAY = date.today().isoformat()

# קבצים שמועברים ב-301 — לא נכללים ב-sitemap
REDIRECT_SOURCES = {
    "articles": {"gemini-2025.html", "deepseek-r2.html"},
    "guides": {"guide-midjourney.html", "guide-ollama.html"},
}

MAIN_PAGES = [
    ("/"                        , "daily",   "1.0", "2026-05-01"),
    ("/comparisons"             , "weekly",  "0.9", "2026-05-02"),
    ("/guides-hebrew"           , "weekly",  "0.9", "2026-05-02"),
    ("/tools-hebrew"            , "weekly",  "0.9", "2026-05-02"),
    ("/news"                    , "weekly",  "0.9", "2026-05-02"),
    ("/business-ai"             , "weekly",  "0.9", "2026-05-02"),
    ("/ai-leaderboard.html"     , "weekly",  "0.9", "2026-04-29"),
    ("/ai-directory.html"       , "weekly",  "0.9", "2026-04-29"),
    ("/guides.html"             , "weekly",  "0.9", "2026-04-22"),
    ("/tools.html"              , "weekly",  "0.9", "2026-04-22"),
    ("/business.html"           , "weekly",  "0.9", "2026-04-22"),
    ("/weekly-news.html"        , "weekly",  "0.9", "2026-04-22"),
    ("/ai-products.html"        , "weekly",  "0.9", "2026-04-22"),
    ("/ai-crazy.html"           , "weekly",  "0.9", "2026-04-22"),
    ("/ai-news-live.html"       , "daily",   "0.9", "2026-04-22"),
    ("/ai-compare.html"         , "monthly", "0.9", "2026-04-22"),
    ("/ai-cost-calculator.html" , "monthly", "0.9", "2026-04-22"),
    ("/prompt-library.html"     , "weekly",  "0.9", "2026-05-01"),
    ("/prompt-generator.html"   , "monthly", "0.9", "2026-04-22"),
    ("/quiz.html"               , "monthly", "0.8", "2026-04-22"),
    ("/ai-ready.html"           , "monthly", "0.9", "2026-04-22"),
    ("/about.html"              , "monthly", "0.7", "2026-04-22"),
    ("/methodology.html"        , "monthly", "0.6", "2026-04-22"),
    ("/contact.html"            , "monthly", "0.4", "2026-04-22"),
    ("/ai-disclosure.html"      , "yearly",  "0.4", "2026-05-01"),
    ("/privacy-policy.html"     , "yearly",  "0.3", "2026-05-01"),
    ("/terms.html"              , "yearly",  "0.3", "2026-05-01"),
    ("/disclaimer.html"         , "yearly",  "0.3", "2026-04-22"),
]


def get_og_image(html_path: Path):
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'<meta property="og:image" content="([^"]+)"', content)
    return m.group(1) if m else None


def is_noindex(html_path: Path) -> bool:
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    return bool(re.search(r'<meta name="robots"[^>]*noindex', content))


def get_lastmod(html_path: Path) -> str:
    """חילוץ תאריך מ-slug (YYYY-MM-DD) או fallback ל-TODAY"""
    m = re.match(r'(\d{4}-\d{2}-\d{2})', html_path.stem)
    if m:
        return m.group(1)
    # נסה לחלץ מ-<meta name="date"> או <time datetime>
    content = html_path.read_text(encoding="utf-8", errors="ignore")
    tm = re.search(r'<time[^>]*datetime="(\d{4}-\d{2}-\d{2})"', content)
    if tm:
        return tm.group(1)
    return TODAY


def url_entry(loc: str, changefreq: str, priority: str, lastmod: str,
              image_loc=None) -> str:
    img_block = ""
    if image_loc:
        img_block = f"\n    <image:image><image:loc>{image_loc}</image:loc></image:image>"
    return (
        f"  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>"
        f"{img_block}\n"
        f"  </url>"
    )


def scan_dir(subdir: str, strip_html: bool, changefreq: str, priority: str) -> list[str]:
    """סורק תיקייה ומחזיר רשימת url_entry strings"""
    entries = []
    d = ROOT / subdir
    if not d.exists():
        return entries
    excludes = REDIRECT_SOURCES.get(subdir, set())
    for fname in sorted(os.listdir(d)):
        if not fname.endswith(".html"):
            continue
        if fname in excludes:
            continue
        path = d / fname
        if is_noindex(path):
            continue
        slug = fname[:-5] if strip_html else fname
        loc = f"{BASE}/{subdir}/{slug}"
        lastmod = get_lastmod(path)
        image = get_og_image(path)
        entries.append(url_entry(loc, changefreq, priority, lastmod, image))
    return entries


def build_sitemap() -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        "",
        "  <!-- Main pages -->",
    ]

    for path, freq, pri, lmod in MAIN_PAGES:
        loc = BASE + path
        lines.append(url_entry(loc, freq, pri, lmod))

    lines += ["", "  <!-- Articles -->"]
    lines += scan_dir("articles", strip_html=True,  changefreq="monthly", priority="0.8")

    lines += ["", "  <!-- Guides -->"]
    lines += scan_dir("guides",   strip_html=True,  changefreq="monthly", priority="0.8")

    lines += ["", "  <!-- Weekly -->"]
    lines += scan_dir("weekly",   strip_html=False, changefreq="monthly", priority="0.7")

    lines.append("")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sitemap = build_sitemap()
    out = ROOT / "sitemap.xml"
    out.write_text(sitemap, encoding="utf-8")
    # ספירת URLs
    count = sitemap.count("<loc>")
    print(f"sitemap.xml נכתב — {count} URLs")
