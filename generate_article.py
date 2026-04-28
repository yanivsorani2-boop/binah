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
    "השוואה": """כתוב כתבת השוואה מעמיקה ומקיפה על: {topic}

חובה לכלול את כל הסעיפים הבאים:

1. **מבוא** (2-3 פסקאות) — הצג את ההקשר: מדוע ההשוואה הזו חשובה ב-2026, מי צריך לקרוא אותה, מה תלמד
2. **סקירת המתחרים** — לכל מוצר/שירות: פסקה נפרדת עם תיאור, חברה מאחוריה, מה ייחודי בו
3. **השוואה לפי פרמטרים** — לפחות 6 פרמטרים (ביצועים, מחיר, ממשק, שפה עברית, אינטגרציות, תמיכה)
4. **טבלת השוואה** — HTML table עם כל המתחרים בשורות ופרמטרים בעמודות, כולל ✅ ❌ ⚠️
5. **ניסיון אישי** — 2-3 תרחישים ספציפיים שבדקת (כגון: כתבתי פרומפט X וקיבלתי Y)
6. **יתרונות וחסרונות** — לכל מוצר: bullet points מפורטים
7. **למי מתאים** — פרופיל משתמש לכל מוצר (פרילנסר / עסק / מפתח / סטודנט)
8. **מחירים מפורטים** — טבלת מחירים עם כל הפלאנים, מה כולל כל פלאן
9. **שאלות נפוצות** — 4-5 שאלות ותשובות אמיתיות שקוראים שואלים
10. **סיכום והמלצה** — המלצה ברורה: מי מנצח ולמה, עם ניסוח "אם אתה X — בחר Y"

כתוב בעברית תקינה ומקצועית. כל פסקה לפחות 3-4 משפטים. סה"כ לפחות 1500 מילה.""",

    "כלים": """כתוב סקירת כלי AI מקיפה ומעמיקה על: {topic}

חובה לכלול את כל הסעיפים הבאים:

1. **מבוא ורקע** (2-3 פסקאות) — מהו הכלי, מי פיתח אותו, מתי יצא, למה הוא חשוב
2. **מה הכלי עושה** — פירוט מלא של כל הפיצ'רים, עם דוגמאות קונקרטיות לכל פיצ'ר
3. **איך להתחיל** — הוראות שלב-אחר-שלב: הרשמה, הגדרה ראשונית, שימוש ראשון
4. **ניסיון אישי ודוגמאות** — לפחות 3 דוגמאות ספציפיות שניסית: פרומפט שהזנת + תוצאה שקיבלת
5. **יתרונות** — לפחות 5 יתרונות מפורטים (לא רשימה יבשה — הסבר כל אחד)
6. **חסרונות ומגבלות** — לפחות 4 חסרונות אמיתיים, כולל מה הכלי לא יכול לעשות
7. **תמחור מלא** — כל הפלאנים, מה כלול, מה לא כלול, האם יש חינמי, מה ה-ROI
8. **השוואה לחלופות** — 2-3 כלים מתחרים, מתי לבחור בהם במקום
9. **טיפים ופרומפטים** — 5 טיפים מעשיים + פרומפטים מוכנים לשימוש
10. **שאלות נפוצות** — 4-5 שאלות אמיתיות שמשתמשים שואלים
11. **מסקנה** — ציון (1-10) לכל פרמטר, המלצה סופית: למי כדאי, למי לא

כתוב בעברית תקינה ומקצועית. כל פסקה לפחות 3-4 משפטים. סה"כ לפחות 1500 מילה.""",

    "מדריך": """כתוב מדריך מקצועי ומקיף שלב-אחר-שלב על: {topic}

חובה לכלול את כל הסעיפים הבאים:

1. **מבוא** (2-3 פסקאות) — מה תלמד, למה זה חשוב, מה תוכל לעשות בסוף המדריך
2. **דרישות מוקדמות** — מה צריך לפני שמתחילים (חשבון, תוכנה, ידע בסיסי)
3. **רקע תיאורטי קצר** — הסבר מושגי בסיס חשובים שקורא מתחיל צריך להבין
4. **מדריך שלב-אחר-שלב** — לפחות 8-10 שלבים ממוספרים, כל שלב עם:
   - תיאור מה עושים
   - פרטים טכניים מדויקים (כפתורים, הגדרות, קוד לדוגמה)
   - צילום מסך מתואר (תאר מה היה צריך לראות)
   - טיפ קטן לסיום השלב
5. **דוגמה מעשית מלאה** — תרחיש ריאלי מקצה לקצה שעושה שימוש בכל מה שלמדת
6. **פרומפטים מוכנים לשימוש** — לפחות 5 פרומפטים/פקודות שניתן להעתיק ולהשתמש
7. **טעויות נפוצות** — 5 טעויות שמתחילים עושים + איך להימנע מהן
8. **פתרון בעיות** — 4-5 בעיות נפוצות ופתרונן
9. **שאלות נפוצות** — 4-5 שאלות שקוראים שואלים
10. **הצעדים הבאים** — מה ללמוד אחר כך, קישורים לנושאים מתקדמים

כתוב בעברית תקינה ומקצועית. כל שלב מפורט ומוסבר היטב. סה"כ לפחות 1600 מילה.""",

    "חדשות": """כתוב כתבת חדשות מנותחת ומעמיקה על: {topic}

חובה לכלול את כל הסעיפים הבאים:

1. **לד** (פסקה ראשונה) — 5 שאלות: מי, מה, מתי, איפה, למה — בפסקה אחת תמציתית
2. **הרקע** (2-3 פסקאות) — ההקשר המלא: מה הוביל לאירוע, מה קרה לפני כן
3. **הפרטים המלאים** — כל מה שידוע: נתונים, ציטוטים, מספרים, תאריכים
4. **הגורמים המעורבים** — מי החברות/אנשים המעורבים, מה עמדתם
5. **ניתוח: למה זה חשוב** — 3-4 פסקאות מנתחות: מה המשמעות הרחבה
6. **השפעה על ישראל** — ספציפית: מה זה אומר לעסקים, מפתחים ומשתמשים בישראל
7. **עמדות מומחים** — מה אומרים מומחים בתחום (תוכל להמציא ציטוטים סבירים)
8. **הצדדים השונים** — אם יש מחלוקת, הצג אותה בצורה מאוזנת
9. **מה צפוי הלאה** — תחזיות: מה יקרה ב-3 חודשים, שנה, 3 שנים
10. **שאלות נפוצות** — 4-5 שאלות שקוראים שואלים על הנושא
11. **סיכום** — פסקה אחת: מה הקורא צריך לזכור ולעשות

כתוב בעברית תקינה ומקצועית ועיתונאית. סה"כ לפחות 1400 מילה.""",

    "ניתוח": """כתוב ניתוח מעמיק ומבוסס נתונים על: {topic}

חובה לכלול את כל הסעיפים הבאים:

1. **מבוא ושאלת המחקר** — מה השאלה שאנחנו מנסים לענות עליה ולמה היא חשובה
2. **הנתונים והמחקרים** — ציין לפחות 5-6 נתונים/מחקרים/סטטיסטיקות עם מקורות
3. **ניתוח מגמות** — כיצד הדברים השתנו ב-3-5 שנים האחרונות, גרף מתואר
4. **הנקודות העיקריות** — 5-6 תובנות מנותחות, כל אחת עם הסבר של 3-4 משפטים
5. **פרספקטיבה ישראלית** — כיצד ישראל ייחודית בהשוואה עולמית בנושא זה
6. **מקרי מבחן** — 2-3 דוגמאות קונקרטיות (חברות, אנשים, מקרים) שממחישות את הניתוח
7. **הצדדים השנויים במחלוקת** — אם יש עמדות שונות, הצג את כולן בצורה הוגנת
8. **מה זה אומר עבורך** — השלכות מעשיות: מה עושה/לא עושה הקורא הממוצע
9. **שאלות נפוצות** — 4-5 שאלות על הנושא
10. **מסקנות** — 3-5 מסקנות ממוספרות, ברורות ומעשיות

כתוב בעברית תקינה ומקצועית. הבא נתונים ועובדות ספציפיות. סה"כ לפחות 1500 מילה.""",

    "סקירה": """כתוב סקירת מוצר מקצועית ומקיפה על: {topic}

חובה לכלול את כל הסעיפים הבאים:

1. **תקציר מנהלים** — 3 משפטים: מה זה, מחיר, ציון כולל, למי מתאים
2. **מי מאחורי המוצר** — החברה, ההיסטוריה, מי המנכ"ל, כמה משקיעים
3. **מה המוצר עושה** — תיאור מלא של כל הפיצ'רים עם דוגמאות
4. **ניסיון אישי שלב-אחר-שלב** — מה עשיתי: הרשמה → הגדרה → שימוש → תוצאות
5. **ביצועים** — מדידות ספציפיות: כמה מהר, כמה מדויק, בדיקות שעשיתי
6. **ציוני פרמטרים** (טבלה):
   - קלות שימוש (1-10)
   - ביצועים (1-10)
   - מחיר-ערך (1-10)
   - תמיכה בעברית (1-10)
   - תמיכת לקוחות (1-10)
   - ציון כולל (1-10)
7. **יתרונות** — לפחות 5 יתרונות ספציפיים שגיליתם
8. **חסרונות** — לפחות 4 חסרונות אמיתיים, כולל deal-breakers
9. **תמחור** — כל הפלאנים, מה כלול, טריק/מלכוד שכדאי לדעת
10. **השוואה ל-3 מתחרים** — קצר: מתי לבחור כל אחד
11. **שאלות נפוצות** — 4-5 שאלות שקוראים שואלים לפני קנייה
12. **מסקנה** — כדאי/לא כדאי + למי ספציפית

כתוב בעברית תקינה ומקצועית. הכל מבוסס על ניסיון ישיר. סה"כ לפחות 1500 מילה.""",

    "טיפים": """כתוב מאמר טיפים מעשי ועמוק על: {topic}

חובה לכלול את כל הסעיפים הבאים:

1. **מבוא** (2-3 פסקאות) — למה הטיפים האלה חשובים, כמה זמן/כסף הם יחסכו
2. **כל טיפ** — לכל טיפ (לפחות 8-10 טיפים):
   - כותרת H3 ממוספרת וברורה
   - הסבר מלא (3-4 משפטים): מה הבעיה שהטיפ פותר
   - דוגמה קונקרטית: תרחיש שכולם מכירים
   - פרומפט/פקודה מוכנה להעתקה (בתוך <code> או blockquote)
   - תוצאה שניתן לצפות לה
3. **טעויות נפוצות** — 3-4 טעויות שאנשים עושים בנושא
4. **כלים מומלצים** — 3-4 כלים שמשפרים את הביצוע
5. **שאלות נפוצות** — 4-5 שאלות שקוראים שואלים
6. **סיכום** — 3 הדברים הכי חשובים שכדאי להתחיל ליישם היום

כתוב בעברית תקינה ומקצועית. כל טיפ עם דוגמה מפורטת ופרומפט מוכן. סה"כ לפחות 1600 מילה.""",
}

ARTICLE_WRAPPER = '''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <script>(function(){{var t=localStorage.getItem('binah-theme');if(t==='light')document.documentElement.setAttribute('data-theme','light');}})();</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{meta_desc}">
  <meta name="author" content="יניב סוראני">
  <meta property="og:title" content="{title}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="בינה">
  <meta property="og:url" content="https://binah.co.il/articles/{slug}.html">
  <meta name="robots" content="index, follow">
  <title>{title} | בינה</title>
  <link rel="stylesheet" href="../styles.min.css">
  <link rel="canonical" href="https://binah.co.il/articles/{slug}.html">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-MG65DD6GYJ"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-MG65DD6GYJ');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9475752562192165" crossorigin="anonymous"></script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{title}",
    "description": "{meta_desc}",
    "url": "https://binah.co.il/articles/{slug}.html",
    "datePublished": "{date_iso}",
    "dateModified": "{date_iso}",
    "inLanguage": "he",
    "author": {{
      "@type": "Person",
      "name": "יניב סוראני",
      "url": "https://binah.co.il/about.html"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "בינה",
      "url": "https://binah.co.il"
    }}
  }}
  </script>
</head>
<body>
<header>
  <div class="container">
    <div class="nav-inner">
      <a href="../index.html" class="logo">בינה ✦</a>
      <nav id="main-nav">
        <a href="../index.html">ראשי</a>
        <a href="../guides.html">מדריכים</a>
        <a href="../tools.html">כלים</a>
        <a href="../quiz.html">בחר AI</a>
        <a href="../business.html">AI לעסקים</a>
        <a href="../ai-products.html">מוצרי AI</a>
        <a href="../weekly-news.html">חדשות</a>
        <a href="../ai-crazy.html">AI מטורף</a>
        <a href="../about.html">אודות</a>
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
    <span class="category">{category}</span>
    <h1>{title}</h1>
    <div class="meta">
      <span>📅 {date}</span>
      <span>⏱ {read_time} דקות קריאה</span>
      <span>✍ <a href="../about.html">יניב סוראני</a></span>
      <span>🔄 עודכן: {date}</span>
    </div>
  </div>
</div>
<div class="container">
  <div class="article-layout">
    <main class="article-body">
      <button class="btn-back" onclick="history.back()">→ חזרה</button>
{body}
      <div class="ad-in-article"><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-9475752562192165" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>
    </main>
    <aside class="article-sidebar">
      <div class="sidebar-widget">
        <h3>מדריכים מומלצים</h3>
        <ul>
          <li><a href="../guides/guide-chatgpt.html">מדריך ChatGPT</a></li>
          <li><a href="../guides/guide-claude.html">מדריך Claude AI</a></li>
          <li><a href="../guides/guide-prompt-basics.html">Prompt Engineering</a></li>
          <li><a href="../guides/guide-midjourney.html">מדריך Midjourney</a></li>
        </ul>
      </div>
      <div class="ad-zone" style="min-height:300px"><ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-9475752562192165" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div>
      <div class="sidebar-widget" style="margin-top:20px">
        <h3>אודות הכותב</h3>
        <p style="font-size:0.88rem;line-height:1.7;color:var(--text-secondary)">
          <strong>יניב סוראני</strong> — עורך תוכן ומומחה AI עם 8+ שנות ניסיון.
          <a href="../about.html">קרא עוד ←</a>
        </p>
      </div>
    </aside>
  </div>
</div>
<footer>
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <div class="logo">בינה ✦</div>
        <p>הבלוג המוביל בעברית על בינה מלאכותית. מדריכים, השוואות וחדשות AI — מתעדכן יומיומית.</p>
      </div>
      <div class="footer-col"><h4>תוכן</h4><ul>
        <li><a href="../index.html">ראשי</a></li>
        <li><a href="../guides.html">מדריכים</a></li>
        <li><a href="../weekly-news.html">חדשות</a></li>
        <li><a href="../ai-crazy.html">AI מטורף</a></li>
      </ul></div>
      <div class="footer-col"><h4>מידע</h4><ul>
        <li><a href="../about.html">אודות הכותב</a></li>
        <li><a href="../methodology.html">מתודולוגיה</a></li>
        <li><a href="../privacy-policy.html">מדיניות פרטיות</a></li>
        <li><a href="../disclaimer.html">כתב ויתור</a></li>
        <li><a href="../contact.html">צור קשר</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <span>© 2025 בינה. כל הזכויות שמורות.</span>
      <span style="color:var(--text-muted);font-size:0.75rem">מופעל בעזרת Claude AI ✦</span>
    </div>
  </div>
</footer>
<button id="back-to-top" aria-label="חזרה לראש הדף" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<script src="../site.min.js"></script>
<script src="../header-bg.min.js"></script>
<script src="/tracker.js"></script>
</body>
</html>'''


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_log():
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text(encoding='utf-8'))
    return {"published": [], "category_indices": {}}


def save_log(log):
    LOG_FILE.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')


def published_this_week_per_category():
    """Returns set of categories already published this week (Mon–Sun)."""
    log = load_log()
    today = date.today()
    week_start = (today - __import__('datetime').timedelta(days=today.weekday())).isoformat()
    week_end   = today.isoformat()
    done = set()
    for a in log.get("published", []):
        pub = a.get("published_at", "")[:10]
        if week_start <= pub <= week_end:
            done.add(a.get("category", ""))
    return done


def published_today_per_category():
    """Legacy: Returns set of categories already published today."""
    return published_this_week_per_category()


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
        "אתה כותב תוכן מקצועי ומעמיק בעברית לבלוג AI בשם 'בינה'.\n"
        "כתוב בעברית תקינה, מקצועית ומפורטת — לפחות 1500 מילה.\n"
        "כלול: כותרות H2 ו-H3 ממוספרות, רשימות bullet, טבלת HTML אם רלוונטי, קוד בתוך <code>, ציטוטים בתוך <blockquote>.\n"
        "כל פסקה — לפחות 3-4 משפטים. אל תקצר שאלות נפוצות — כל תשובה לפחות 3 משפטים.\n"
        "הוצא רק HTML פנימי (ללא DOCTYPE/html/head/body).\n"
        "השתמש ב-<h2>,<h3>,<p>,<ul>,<li>,<ol>,<strong>,<em>,<table>,<thead>,<tbody>,<tr>,<th>,<td>,<code>,<blockquote>.\n"
        "אל תוסיף style inline. אל תכלול מבוא מיותר — היכנס ישירות לתוכן."
    )
    user_prompt = prompt_template.format(topic=title)

    print(f"  → [{category}] {title}")
    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    body = msg.content[0].text.strip()
    body_with_ads = insert_ads(body)

    today_str = he_date()
    date_iso  = date.today().isoformat()
    read_time = max(6, len(body.split()) // 200)
    meta_desc = first_p_text(body)

    html = ARTICLE_WRAPPER.format(
        title=title, category=category, meta_desc=meta_desc,
        date=today_str, date_iso=date_iso, slug=slug,
        read_time=read_time, body=body_with_ads,
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
          <p class="card-excerpt">קרא את הכתבה המלאה על {title.split(':')[0]}. מדריך מקיף ומעמיק.</p>
          <div class="card-meta">
            <span>{date_str}</span>
            <span>✍ יניב סוראני</span>
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
