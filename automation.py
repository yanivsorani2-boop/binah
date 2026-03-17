#!/usr/bin/env python3
"""
AIFlow Manager — Automation Script
Packages all content into a structured JSON ready for Make.com / Zapier
"""

import json
import os
from datetime import datetime

# ─── Load content files ───────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_file(name):
    path = os.path.join(BASE_DIR, name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

article_html   = read_file("article_claude_vs_gpt4o.html")
tiktok_script  = read_file("tiktok_script.txt")
instagram_data = read_file("instagram_carousel.txt")

# ─── Meta ─────────────────────────────────────────────────────────────────────

meta = {
    "title":           "Claude 3.7 Sonnet נגד GPT-4o: מי המודל הטוב ביותר ב-2025?",
    "slug":            "claude-37-vs-gpt4o-2025",
    "meta_description": "Claude 3.7 Sonnet מול GPT-4o — מי מנצח ב-2025? השוואה מעמיקה בכתיבת קוד, תוכן, מחיר ובטיחות. קראו לפני שאתם משלמים על מנוי.",
    "category":        "השוואות AI",
    "tags":            ["Claude", "GPT-4o", "בינה מלאכותית", "כלי AI", "השוואה"],
    "affiliate_links": {
        "claude_pro":  "https://claude.ai/upgrade",
        "chatgpt_plus": "https://chat.openai.com/subscribe"
    },
    "image_prompt":    "Two AI robots facing each other in a futuristic arena, one glowing cyan labeled Claude and one glowing green labeled GPT, dramatic lighting, tech aesthetic, dark background, cinematic composition, 16:9 ratio",
    "publish_date":    datetime.now().strftime("%Y-%m-%d"),
    "status":          "draft"
}

# ─── Social content ────────────────────────────────────────────────────────────

social = {
    "tiktok": {
        "script":   tiktok_script,
        "duration": "60-75 seconds",
        "hashtags": ["#AI", "#בינהמלאכותית", "#ChatGPT", "#Claude", "#כליAI",
                     "#טכנולוגיה", "#מפתחים", "#אוטומציה", "#AItools", "#tech"]
    },
    "instagram_carousel": {
        "slides":   6,
        "content":  instagram_data,
        "hashtags": ["#AI", "#בינהמלאכותית", "#ChatGPT", "#Claude", "#כליAI",
                     "#טכנולוגיה", "#מפתחים", "#אוטומציה", "#AItools", "#השוואה",
                     "#סטארטאפ", "#יזמות", "#ישראל"]
    }
}

# ─── WordPress payload ────────────────────────────────────────────────────────

wordpress_payload = {
    "title":        meta["title"],
    "slug":         meta["slug"],
    "content":      article_html,
    "excerpt":      meta["meta_description"],
    "status":       meta["status"],
    "categories":   [meta["category"]],
    "tags":         meta["tags"],
    "yoast_meta": {
        "meta_description": meta["meta_description"],
        "focus_keyword":    "Claude 3.7 vs GPT-4o"
    }
}

# ─── Final output ─────────────────────────────────────────────────────────────

output = {
    "generated_at":      datetime.now().isoformat(),
    "week":              1,
    "article_number":    1,
    "meta":              meta,
    "wordpress_payload": wordpress_payload,
    "social_content":    social,
    "automation_notes": {
        "make_scenario":  "WordPress API → post article → trigger Hootsuite schedule",
        "hootsuite_queue": "TikTok: Monday 18:00 | Instagram: Tuesday 12:00",
        "recommended_tools": [
            "Make.com — connect Claude API + WordPress + Hootsuite",
            "Hootsuite — schedule TikTok & Instagram posts",
            "Yoast SEO — WordPress SEO plugin",
            "Canva API — auto-generate carousel images"
        ]
    }
}

# ─── Save ─────────────────────────────────────────────────────────────────────

out_path = os.path.join(BASE_DIR, "week1_article1_package.json")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ Package saved: {out_path}")
print(f"   Article: {meta['title']}")
print(f"   Status:  {meta['status']}")
print(f"   Date:    {meta['publish_date']}")
print()
print("Next steps:")
print("  1. Upload article_claude_vs_gpt4o.html to WordPress")
print("  2. Use week1_article1_package.json with Make.com")
print("  3. Schedule TikTok: Monday 18:00")
print("  4. Schedule Instagram: Tuesday 12:00")
