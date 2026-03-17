#!/usr/bin/env python3
"""
AIFlow Week 1 Master Automation
Reads all content files, builds week1_full_package.json, prints summary.
"""

import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = str(Path(__file__).parent)  # /Users/sorani/Desktop/binah

# ── File manifest ──────────────────────────────────────────────────────────────

ARTICLES = [
    {
        "file": "article_claude_vs_gpt4o.html",
        "title": "Claude 3.7 Sonnet נגד GPT-4o: מי המודל הטוב ביותר ב-2025?",
        "slug": "claude-vs-gpt4o-2025",
        "meta_description": "השוואה מקיפה בין Claude 3.7 Sonnet ו-GPT-4o ב-2025 — קידוד, כתיבה, מחיר וביצועים. מי מנצח?",
        "image_prompt": "two AI robots facing each other in a boxing ring, one labeled Claude one labeled GPT-4o, futuristic arena, neon lighting",
        "affiliate_links": ["[AFFILIATE_CLAUDE]", "[AFFILIATE_CHATGPT]"],
        "publish_day": "Sunday",
        "publish_time": "18:00",
    },
    {
        "file": "article2_ai_video_tools.html",
        "title": "5 כלי AI לעריכת וידאו שחוסכים 10 שעות בשבוע (2025)",
        "slug": "ai-video-tools-2025",
        "meta_description": "5 כלי AI לעריכת וידאו שחוסכים 10 שעות בשבוע ב-2025 — Runway, Kling, CapCut, Descript ו-Sora. השוואת מחירים.",
        "image_prompt": "futuristic video editing suite with AI holographic interface, multiple screens, neon blue and purple lighting",
        "affiliate_links": ["[AFFILIATE_RUNWAY]", "[AFFILIATE_DESCRIPT]"],
        "publish_day": "Tuesday",
        "publish_time": "18:00",
    },
    {
        "file": "article3_vibe_coding.html",
        "title": "Vibe Coding: כיצד לבנות אפליקציה ב-2025 בלי לדעת לתכנת",
        "slug": "vibe-coding-2025",
        "meta_description": "Vibe Coding — כיצד לבנות אפליקציה ב-2025 בלי לדעת לתכנת עם Cursor, Bolt.new, v0 ו-Replit AI. המדריך המלא.",
        "image_prompt": "person relaxing on couch while a holographic AI builds an app on screen, futuristic living room, warm lighting, digital particles",
        "affiliate_links": ["[AFFILIATE_CURSOR]", "[AFFILIATE_REPLIT]"],
        "publish_day": "Thursday",
        "publish_time": "18:00",
    },
]

SOCIAL_FILES = [
    {
        "file": "tiktok_script.txt",
        "platform": "TikTok",
        "article_slug": "claude-vs-gpt4o-2025",
        "scheduled_day": "Sunday",
        "scheduled_time": "18:30",
    },
    {
        "file": "instagram_carousel.txt",
        "platform": "Instagram",
        "article_slug": "claude-vs-gpt4o-2025",
        "scheduled_day": "Monday",
        "scheduled_time": "12:00",
    },
    {
        "file": "tiktok2_ai_video.txt",
        "platform": "TikTok",
        "article_slug": "ai-video-tools-2025",
        "scheduled_day": "Tuesday",
        "scheduled_time": "18:30",
    },
    {
        "file": "instagram2_video_carousel.txt",
        "platform": "Instagram",
        "article_slug": "ai-video-tools-2025",
        "scheduled_day": "Wednesday",
        "scheduled_time": "12:00",
    },
    {
        "file": "tiktok3_vibe_coding.txt",
        "platform": "TikTok",
        "article_slug": "vibe-coding-2025",
        "scheduled_day": "Thursday",
        "scheduled_time": "18:30",
    },
    {
        "file": "instagram3_vibe_coding_carousel.txt",
        "platform": "Instagram",
        "article_slug": "vibe-coding-2025",
        "scheduled_day": "Friday",
        "scheduled_time": "12:00",
    },
]

CONTENT_CALENDAR = [
    {
        "day": "Sunday",
        "tasks": [
            {"time": "18:00", "action": "Publish Article 1", "details": "Claude vs GPT-4o", "platform": "Blog"},
            {"time": "18:30", "action": "Post TikTok 1", "details": "Claude vs GPT-4o hook", "platform": "TikTok"},
        ],
    },
    {
        "day": "Monday",
        "tasks": [
            {"time": "12:00", "action": "Post Instagram Carousel 1", "details": "Claude vs GPT-4o visual summary", "platform": "Instagram"},
        ],
    },
    {
        "day": "Tuesday",
        "tasks": [
            {"time": "18:00", "action": "Publish Article 2", "details": "5 כלי AI לעריכת וידאו", "platform": "Blog"},
            {"time": "18:30", "action": "Post TikTok 2", "details": "AI video tools hook", "platform": "TikTok"},
        ],
    },
    {
        "day": "Wednesday",
        "tasks": [
            {"time": "12:00", "action": "Post Instagram Carousel 2", "details": "AI video tools visual", "platform": "Instagram"},
        ],
    },
    {
        "day": "Thursday",
        "tasks": [
            {"time": "18:00", "action": "Publish Article 3", "details": "Vibe Coding מדריך", "platform": "Blog"},
            {"time": "18:30", "action": "Post TikTok 3", "details": "Vibe Coding demo hook", "platform": "TikTok"},
        ],
    },
    {
        "day": "Friday",
        "tasks": [
            {"time": "12:00", "action": "Post Instagram Carousel 3", "details": "Vibe Coding visual", "platform": "Instagram"},
        ],
    },
    {
        "day": "Saturday",
        "tasks": [
            {
                "time": "16:00",
                "action": "Roundup Story/Reel",
                "details": '3 דברים שAI עשה השבוע — סיכום שבועי',
                "platform": "Instagram/TikTok",
            }
        ],
    },
]

AUTOMATION_STACK = [
    {
        "tool": "Make.com",
        "purpose": "Claude API → WordPress REST API — auto-publish articles on schedule",
        "priority": "high",
        "monthly_cost_usd": 9,
    },
    {
        "tool": "Make.com",
        "purpose": "JSON package → Hootsuite API — schedule all social posts from week1_full_package.json",
        "priority": "high",
        "monthly_cost_usd": 0,  # included in Make plan
    },
    {
        "tool": "Canva API",
        "purpose": "Auto-generate carousel images from slide text in instagram carousel files",
        "priority": "medium",
        "monthly_cost_usd": 13,
    },
    {
        "tool": "Yoast SEO",
        "purpose": "WordPress plugin — meta tags, schema markup, readability analysis for Hebrew content",
        "priority": "high",
        "monthly_cost_usd": 0,  # free tier
    },
    {
        "tool": "Google Analytics 4",
        "purpose": "Track article traffic, bounce rate, time-on-page, conversion events",
        "priority": "high",
        "monthly_cost_usd": 0,
    },
    {
        "tool": "Google AdSense",
        "purpose": "Display ad monetization — place in article body, sidebar, between H2 sections",
        "priority": "high",
        "monthly_cost_usd": 0,
    },
    {
        "tool": "Hootsuite",
        "purpose": "Social media scheduling — queue all TikTok + Instagram posts for the week",
        "priority": "medium",
        "monthly_cost_usd": 19,
    },
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def read_file(filename):
    path = os.path.join(BASE_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"[FILE NOT FOUND: {filename}]"


def file_size_kb(filename):
    path = os.path.join(BASE_DIR, filename)
    try:
        return round(os.path.getsize(path) / 1024, 1)
    except FileNotFoundError:
        return 0


def count_words(text):
    # rough word count (handles Hebrew)
    return len(text.split())


# ── Build package ──────────────────────────────────────────────────────────────

def build_package():
    articles_data = []
    for a in ARTICLES:
        html = read_file(a["file"])
        articles_data.append({
            "title": a["title"],
            "slug": a["slug"],
            "meta_description": a["meta_description"],
            "html_content": html,
            "image_prompt": a["image_prompt"],
            "affiliate_links": a["affiliate_links"],
            "publish_day": a["publish_day"],
            "publish_time": a["publish_time"],
            "word_count": count_words(html),
            "file_size_kb": file_size_kb(a["file"]),
        })

    social_data = []
    for s in SOCIAL_FILES:
        content = read_file(s["file"])
        social_data.append({
            "platform": s["platform"],
            "article_slug": s["article_slug"],
            "content": content,
            "hashtags": [line.strip() for line in content.splitlines() if line.startswith("#")],
            "scheduled_day": s["scheduled_day"],
            "scheduled_time": s["scheduled_time"],
            "file": s["file"],
        })

    package = {
        "week": 1,
        "blog_name": "AIFlow",
        "language": "Hebrew",
        "generated_at": datetime.now().isoformat(),
        "monetization": {
            "primary": "Google AdSense",
            "secondary": "Affiliate marketing (Runway, Descript, Cursor, Replit, Claude, ChatGPT)",
        },
        "content_calendar": CONTENT_CALENDAR,
        "articles": articles_data,
        "social_schedule": social_data,
        "automation_stack": AUTOMATION_STACK,
    }

    return package


# ── Print summary ──────────────────────────────────────────────────────────────

def print_summary(package):
    divider = "=" * 60

    print(divider)
    print("  AIFlow — Week 1 Full Package Summary")
    print(divider)
    print(f"  Generated: {package['generated_at']}")
    print(f"  Blog: {package['blog_name']} | Language: {package['language']}")
    print()

    # Articles
    print("── ARTICLES ──────────────────────────────────────────────")
    total_words = 0
    for i, a in enumerate(package["articles"], 1):
        wc = a["word_count"]
        total_words += wc
        print(f"  {i}. {a['title'][:55]}...")
        print(f"     Slug:       /{a['slug']}/")
        print(f"     Publish:    {a['publish_day']} @ {a['publish_time']}")
        print(f"     Words:      ~{wc:,}  |  Size: {a['file_size_kb']} KB")
        print(f"     Affiliates: {', '.join(a['affiliate_links'])}")
        print()
    print(f"  TOTAL words across all articles: ~{total_words:,}")
    print()

    # Social
    print("── SOCIAL SCHEDULE ───────────────────────────────────────")
    for s in package["social_schedule"]:
        print(f"  [{s['scheduled_day']:10s} {s['scheduled_time']}] {s['platform']:12s} → {s['file']}")
    print()

    # Calendar
    print("── CONTENT CALENDAR ──────────────────────────────────────")
    for day in package["content_calendar"]:
        print(f"  {day['day']}:")
        for t in day["tasks"]:
            print(f"    {t['time']} — {t['action']} ({t['platform']}): {t['details']}")
    print()

    # Automation
    print("── AUTOMATION STACK ──────────────────────────────────────")
    for tool in package["automation_stack"]:
        cost = f"${tool['monthly_cost_usd']}/mo" if tool["monthly_cost_usd"] > 0 else "FREE"
        print(f"  [{tool['priority'].upper():6s}] {tool['tool']:20s} — {cost}")
        print(f"           {tool['purpose'][:65]}")
    print()

    # File inventory
    print("── FILE INVENTORY ────────────────────────────────────────")
    all_files = [a["file"] for a in ARTICLES] + [s["file"] for s in SOCIAL_FILES] + ["automation_master.py"]
    for fname in all_files:
        size = file_size_kb(fname)
        status = "✓" if size > 0 else "✗ MISSING"
        print(f"  {status}  {fname:45s} {size} KB")
    print()

    output_file = os.path.join(BASE_DIR, "week1_full_package.json")
    print(f"── OUTPUT ────────────────────────────────────────────────")
    print(f"  JSON saved to: {output_file}")
    size = file_size_kb("week1_full_package.json")
    print(f"  Package size:  {size} KB")
    print()
    print(divider)
    print("  Week 1 package complete. Ready for publishing.")
    print(divider)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("Building AIFlow Week 1 package...\n")
    package = build_package()

    output_path = os.path.join(BASE_DIR, "week1_full_package.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(package, f, ensure_ascii=False, indent=2)

    print_summary(package)


if __name__ == "__main__":
    main()
