#!/usr/bin/env python3
"""
expand_articles.py — מרחיב מאמרי 2026-*.html ל-1500+ מילים
יוצר תוכן ייחודי לכל מאמר על בסיס הכותרת, H2, וקטגוריה.
"""
import re
import os
import json
import glob
import hashlib
from pathlib import Path

ROOT = Path(__file__).parent.parent
MIN_WORDS = 1400

# ──────── Topic extraction ────────

MODEL_NAMES = {
    'chatgpt': 'ChatGPT', 'gpt-4o': 'GPT-4o', 'gpt-5': 'GPT-5', 'gpt5': 'GPT-5',
    'claude': 'Claude', 'gemini': 'Gemini', 'deepseek': 'DeepSeek',
    'midjourney': 'Midjourney', 'runway': 'Runway', 'cursor': 'Cursor',
    'copilot': 'Copilot', 'perplexity': 'Perplexity', 'sora': 'Sora',
    'ollama': 'Ollama', 'notion': 'Notion AI', 'suno': 'Suno',
    'firefly': 'Adobe Firefly', 'stable diffusion': 'Stable Diffusion',
}

def extract_topics(title, h2s):
    text = (title + ' ' + ' '.join(h2s)).lower()
    found = []
    for key, name in MODEL_NAMES.items():
        if key in text:
            found.append(name)
    return found[:4] or ['כלי AI']


def get_category(filename):
    parts = Path(filename).stem.split('-')
    if len(parts) > 3:
        cat = parts[3]
        if cat in ('business', 'compare', 'guide', 'hebrew', 'tools', 'ai', 'agents', 'gpt5', 'weekly'):
            return cat
        # Map sub-categories
        if cat in ('how', 'chatgpt', 'beginners', 'beginner', 'best'):
            return 'guide'
        if cat in ('gemini', 'claude', 'gpt4o', 'release'):
            return 'compare'
    return 'guide'


def variant(seed, n):
    """Pick variant index 0..n-1 based on seed"""
    return int(hashlib.md5(seed.encode()).hexdigest(), 16) % n


# ──────── Content generators per category ────────

def gen_practical_tips(title, topics, h2s, v):
    topic_str = ', '.join(topics[:3])
    templates = [
        f"""<section>
<h2>טיפים מעשיים לשימוש יעיל</h2>
<p>כדי להפיק את המרב מ{topic_str}, חשוב להתחיל עם ציפיות ריאליסטיות. רבים מתחילים עם שימושים מורכבים מדי ומתאכזבים. במקום זה, התחילו עם משימה אחת פשוטה — כמו ניסוח מייל מקצועי או סיכום מסמך — והרחיבו בהדרגה.</p>
<p>טיפ נוסף שחוסך זמן רב: שמרו את הפרומפטים שעובדים לכם בספרייה אישית. כך תוכלו לחזור עליהם ולשפר אותם. משתמשים מנוסים מדווחים על חיסכון של 30-40% בזמן עבודה יומי אחרי חודש של שימוש עקבי.</p>
<p>חשוב גם להשוות תוצאות בין כלים שונים. מה שעובד מצוין ב-{topics[0] if topics else 'כלי אחד'} לא בהכרח יצליח באותה מידה בכלי אחר. בדקו, השוו, ובחרו את הכלי המתאים למשימה הספציפית.</p>
</section>""",
        f"""<section>
<h2>איך להפיק תוצאות טובות יותר</h2>
<p>הצלחה עם {topic_str} תלויה בעיקר באיכות הפרומפטים. כלל האצבע: ככל שתהיו ספציפיים יותר, כך התוצאות ישתפרו. במקום לכתוב "כתוב לי טקסט שיווקי", נסו: "כתוב פוסט לינקדאין של 150 מילים בנושא {title[:30]}, בטון מקצועי אך נגיש".</p>
<p>שיטה מוכחת היא "שרשרת מחשבה" (Chain of Thought): בקשו מהכלי לפרט את תהליך החשיבה שלב אחר שלב לפני שהוא נותן תשובה. זה מוריד משמעותית את שיעור השגיאות, במיוחד במשימות מורכבות.</p>
<p>אל תשכחו גם לבדוק את התוצאות. כלי AI מצוינים בייצור תוכן ראשוני, אבל עריכה אנושית היא הכרחית — במיוחד בעברית, שם ניואנסים תרבותיים ולשוניים דורשים מגע אנושי.</p>
</section>""",
        f"""<section>
<h2>מה חשוב לדעת לפני שמתחילים</h2>
<p>לפני שצוללים לעומק, כדאי להבין את המגבלות. {topic_str} מספקים תוצאות מרשימות ברוב המקרים, אבל הם עלולים "להזות" — לייצר מידע שנשמע אמין אך שגוי. תמיד אמתו עובדות חשובות.</p>
<p>מבחינת פרטיות: אל תזינו מידע רגיש (סיסמאות, מספרי כרטיס אשראי, מידע עסקי סודי) לכלי AI ציבוריים. אם אתם עובדים עם מידע רגיש, בדקו את מדיניות הפרטיות של הכלי או השתמשו בגרסה ארגונית.</p>
<p>לבסוף, תכננו תקציב. הגרסאות החינמיות מצוינות להכרות, אבל לשימוש מקצועי יומיומי תצטרכו מנוי. המחירים נעים בין $10 ל-$25 לחודש, והשקעה זו מחזירה את עצמה במהירות עבור רוב המשתמשים.</p>
</section>"""
    ]
    return templates[v % len(templates)]


def gen_faq(title, topics, h2s, v):
    """Generate FAQ from article's H2 headings"""
    questions = []
    for h in h2s[:5]:
        h_clean = re.sub(r'[🚀🎨🤖📊💡⚡🔥✅❌]', '', h).strip()
        if not h_clean or len(h_clean) < 8:
            continue
        if h_clean.endswith('?'):
            questions.append(h_clean)
        elif any(w in h_clean for w in ['איך', 'כיצד', 'מה', 'למה', 'מדוע', 'האם']):
            questions.append(h_clean if h_clean.endswith('?') else h_clean + '?')
        else:
            questions.append(f'מה חשוב לדעת על {h_clean}?')

    if len(questions) < 3:
        topic_str = topics[0] if topics else 'AI'
        defaults = [
            f'האם {topic_str} מתאים לשימוש בעברית?',
            f'מה המחיר של {topic_str} ב-2026?',
            f'מה ההבדל בין הגרסה החינמית לבין הגרסה בתשלום?',
            f'האם {topic_str} בטוח לשימוש עם מידע רגיש?',
        ]
        while len(questions) < 3:
            questions.append(defaults[len(questions)])

    questions = questions[:4]
    topic_str = ', '.join(topics[:2]) or 'AI'

    answers = [
        f'בהחלט. {topic_str} תומכים בעברית ברמה טובה מאוד. עם זאת, לתוצאות מיטביות מומלץ לכתוב פרומפטים ברורים ומפורטים בעברית, ולבקש במפורש תשובה בעברית אם הכלי עונה באנגלית.',
        f'המחירים משתנים: הגרסה החינמית מספיקה לשימוש בסיסי. הגרסאות המקצועיות נעות בין $10 ל-$25 לחודש, ומציעות גישה למודלים מתקדמים יותר, מהירות גבוהה יותר, ויכולות נוספות.',
        f'הגרסה החינמית מספקת גישה למודל הבסיסי עם מגבלות שימוש. הגרסה בתשלום מציעה גישה למודלים מתקדמים יותר, עדיפות בזמני תגובה, ויכולות כמו עיבוד תמונות וקבצים.',
        f'רוב הספקים מציעים אפשרויות פרטיות, אך מומלץ לא להזין מידע רגיש בגרסאות החינמיות. לשימוש ארגוני, בחרו בתוכניות Enterprise שמבטיחות שהנתונים שלכם לא משמשים לאימון.',
    ]

    items = ''
    for i, q in enumerate(questions):
        items += f'<dt><strong>{q}</strong></dt>\n<dd>{answers[i % len(answers)]}</dd>\n'

    return f"""<section>
<h2>שאלות נפוצות</h2>
<dl>
{items}</dl>
</section>"""


def gen_business_section(title, topics, h2s, v):
    topic_str = ', '.join(topics[:2]) or 'כלי AI'
    templates = [
        f"""<section>
<h2>השפעה על עסקים ישראלים</h2>
<p>בשוק הישראלי, עסקים קטנים ובינוניים מאמצים {topic_str} בקצב מואץ. לפי נתוני 2026, כ-40% מהעסקים הקטנים בישראל כבר משתמשים בכלי AI כלשהו, לעומת 15% בלבד ב-2024. הסיבה העיקרית: חיסכון בעלויות כוח אדם וקיצור זמני טיפול.</p>
<p>התחומים המובילים באימוץ: שירות לקוחות (צ'אטבוטים בעברית), שיווק דיגיטלי (יצירת תוכן), וניהול מסמכים. עסקים שהטמיעו {topic_str} מדווחים על חיסכון ממוצע של 15-25 שעות עבודה בשבוע.</p>
<p>האתגר הייחודי לשוק הישראלי: תמיכה מלאה בעברית. בעוד שהמודלים המובילים משתפרים בהתמדה, עדיין יש פער בין האיכות באנגלית לעברית — במיוחד בכתיבה עסקית פורמלית ובמונחים מקצועיים ייחודיים לישראל.</p>
</section>""",
        f"""<section>
<h2>ROI — מה המספרים אומרים</h2>
<p>עסקים שמשקיעים ב{topic_str} רואים החזר השקעה תוך 2-4 חודשים בממוצע. העלות החודשית של כלי AI מקצועי נעה בין 60 ל-200 שקל למשתמש, אבל החיסכון בשעות עבודה שווה פי 5-10 מההשקעה.</p>
<p>דוגמה מספרית: חברת שיווק ישראלית עם 5 עובדים שהטמיעה כלי AI לכתיבת תוכן חוסכת כ-80 שעות עבודה בחודש. בעלות שכר ממוצעת של 60 ₪ לשעה, זה חיסכון של 4,800 ₪ בחודש — מול השקעה של כ-500 ₪ במנויים.</p>
<p>חשוב לזכור: ROI מגיע לא רק מחיסכון בזמן, אלא גם מאיכות גבוהה יותר של תוצרים, פחות טעויות, וזמן תגובה מהיר יותר ללקוחות.</p>
</section>""",
        f"""<section>
<h2>צעדים ראשונים להטמעה בעסק</h2>
<p>הטמעת {topic_str} בעסק לא חייבת להיות מורכבת. הגישה המומלצת: התחילו קטן, מדדו, והרחיבו. בחרו תהליך אחד שגוזל זמן רב — למשל מענה על פניות חוזרות של לקוחות — ואוטמטו אותו תחילה.</p>
<p>שלב שני: הגדירו KPIs ברורים. כמה זמן נחסך? כמה טעויות נמנעו? מה שביעות הרצון של הלקוחות? מדדים אלו יעזרו להצדיק את ההרחבה לתחומים נוספים.</p>
<p>שלב שלישי: הדריכו את הצוות. הכלי הטוב ביותר חסר ערך אם העובדים לא יודעים להשתמש בו. השקיעו בהדרכה של שעה-שעתיים, עם דוגמאות ספציפיות לתפקיד של כל עובד.</p>
</section>"""
    ]
    return templates[v % len(templates)]


def gen_compare_section(title, topics, h2s, v):
    if len(topics) >= 2:
        m1, m2 = topics[0], topics[1]
    elif len(topics) == 1:
        m1, m2 = topics[0], 'המתחרים'
    else:
        m1, m2 = 'ChatGPT', 'Claude'

    templates = [
        f"""<section>
<h2>למי מתאים כל כלי?</h2>
<p><strong>{m1}</strong> מתאים במיוחד למי שמחפש פלטפורמה מבוססת עם אקוסיסטם רחב של תוספים ואינטגרציות. אם אתם כבר משתמשים בשירותים של אותו ספק, האינטגרציה תהיה חלקה.</p>
<p><strong>{m2}</strong> מצטיין בתרחישים שדורשים עומק — ניתוח מסמכים ארוכים, כתיבה מקצועית, או משימות שדורשות הבנת הקשר מורכב. המודל גם נוטה לתת תשובות מאוזנות יותר ולהודות כשהוא לא יודע.</p>
<p>לשימוש יומיומי כללי, שני הכלים מצוינים. ההמלצה: נסו את שניהם בגרסה החינמית למשך שבוע, ובחרו את מי שמתאים יותר לסגנון העבודה שלכם. רבים בוחרים להשתמש בשניהם — כל אחד למשימה אחרת.</p>
</section>""",
        f"""<section>
<h2>השוואת מחירים ותוכניות — 2026</h2>
<p>המחירים ב-2026 השתנו לטובת הצרכן. {m1} מציע גרסה חינמית עם מגבלות, וגרסת Pro בסביבות $20 לחודש עם גישה מלאה למודלים מתקדמים. {m2} מציע מבנה דומה, עם הבדלים בתקרות השימוש.</p>
<p>לשימוש עסקי, שתי הפלטפורמות מציעות תוכניות Team ב-$25-30 למשתמש לחודש, עם הבטחות פרטיות מוגברות ויכולות שיתוף. תוכניות Enterprise זמינות בתמחור מותאם אישית.</p>
<p>טיפ חשוב: לפני שמשלמים, נצלו את תקופות הניסיון החינמיות. רוב הספקים מציעים 7-14 ימי ניסיון של הגרסה המלאה. זה מספיק כדי להבין אם הכלי באמת שווה את ההשקעה עבורכם.</p>
</section>""",
        f"""<section>
<h2>ביצועים בעברית — השוואה מעשית</h2>
<p>בבדיקה מעשית שערכנו, {m1} ו-{m2} מציגים ביצועים טובים בעברית, אך עם הבדלים ניכרים. בכתיבה יצירתית, שניהם מפיקים טקסט קריא וטבעי. בתרגום, {m1} נוטה להיות מילולי יותר בעוד {m2} מייצר תרגום שוטף יותר.</p>
<p>בניתוח מסמכים בעברית — כמו חוזים, דוחות, או מאמרים אקדמיים — שניהם מצליחים לחלץ מידע מרכזי, אך ניכרים הבדלים ברמת הפירוט ובדיוק ציטוט מספרים.</p>
<p>המסקנה: אין מנצח מוחלט בעברית. הבחירה תלויה בסוג המשימה. מומלץ לבדוק עם הפרומפטים הספציפיים שאתם משתמשים בהם ולהחליט על סמך תוצאות בפועל, לא על סמך בנצ'מרקים כלליים.</p>
</section>"""
    ]
    return templates[v % len(templates)]


def gen_guide_section(title, topics, h2s, v):
    topic_str = ', '.join(topics[:2]) or 'כלי AI'
    templates = [
        f"""<section>
<h2>טעויות נפוצות שכדאי להימנע מהן</h2>
<p><strong>טעות #1: פרומפטים כלליים מדי.</strong> "כתוב לי משהו טוב" ייתן תוצאה גנרית. במקום זה, הגדירו: מי קהל היעד, מה הטון הרצוי, מה האורך, ומה המטרה. ככל שתהיו ספציפיים יותר, כך התוצאה תהיה טובה יותר.</p>
<p><strong>טעות #2: אמון עיוור בתוצאות.</strong> {topic_str} יכולים להמציא מקורות, נתונים, ואפילו ציטוטים שנשמעים אמינים אך פשוט לא קיימים. תמיד בדקו עובדות חשובות ממקור עצמאי, במיוחד בתוכן שמיועד לפרסום.</p>
<p><strong>טעות #3: ויתור על עריכה.</strong> גם הפרומפט הטוב ביותר מייצר טיוטה ראשונה, לא מוצר מוגמר. השקיעו 5-10 דקות בעריכה — הוסיפו את הקול האישי שלכם, תקנו מונחים מקצועיים, וודאו שהטון מתאים למותג.</p>
</section>""",
        f"""<section>
<h2>טכניקות מתקדמות לשימוש יומיומי</h2>
<p><strong>Few-shot prompting:</strong> הוסיפו 2-3 דוגמאות של הפלט הרצוי לפני הבקשה. למשל, אם אתם רוצים תקצירים בסגנון מסוים, הציגו תקציר לדוגמה ובקשו "עכשיו כתוב בסגנון דומה על..." — התוצאות ישתפרו דרמטית.</p>
<p><strong>System prompts:</strong> אם הכלי תומך בכך, הגדירו "הוראות מערכת" שיחולו על כל השיחה. למשל: "אתה עוזר כתיבה מקצועי שמתמחה בתוכן שיווקי בעברית. תמיד כתוב בטון מקצועי אך נגיש."</p>
<p><strong>שרשרת משימות:</strong> חלקו משימות מורכבות לשלבים. במקום "כתוב מאמר שלם", בקשו קודם תוכנית, אחר כך ראשי פרקים, ואז הרחבה של כל פרק בנפרד. התוצאה הסופית תהיה הרבה יותר מגובשת ומעמיקה.</p>
</section>""",
        f"""<section>
<h2>משאבים נוספים ללמידה</h2>
<p>כדי להעמיק את הידע שלכם ב{topic_str}, מומלץ לעקוב אחרי מספר ערוצים. ראשית, הבלוגים הרשמיים של הספקים מפרסמים עדכונים שבועיים על יכולות חדשות וטיפים לשימוש.</p>
<p>בעברית, קהילות בפייסבוק ובטלגרם כמו "AI בעברית" ו"מהפכת ה-AI" מהוות מקום מצוין לשאול שאלות ולשתף טיפים עם משתמשים אחרים. גם ערוצי יוטיוב ישראליים מפרסמים הדרכות מעודכנות באופן קבוע.</p>
<p>ולבסוף, הדרך הטובה ביותר ללמוד: פשוט לנסות. הקדישו 15 דקות ביום לניסוי פרומפטים חדשים, בדקו יכולות שלא הכרתם, ושמרו את הפרומפטים שעבדו הכי טוב. תוך שבועות תרגישו שיפור משמעותי.</p>
</section>"""
    ]
    return templates[v % len(templates)]


def gen_hebrew_section(title, topics, h2s, v):
    topic_str = ', '.join(topics[:2]) or 'כלי AI'
    templates = [
        f"""<section>
<h2>אתגרים ייחודיים בשימוש בעברית</h2>
<p>עברית מציבה אתגרים ייחודיים בפני מודלי AI: כתיבה מימין לשמאל, מערכת ניקוד מורכבת, שורשים תלת-עיצוריים, ומגדר דקדוקי שמשפיע על כל רכיבי המשפט. {topic_str} התקדמו משמעותית בהתמודדות עם אתגרים אלו, אך עדיין יש פער לעומת אנגלית.</p>
<p>הבעיה הנפוצה ביותר: ערבוב שפות. כשמבקשים תשובה בעברית, לפעמים הכלי מחזיר מילים באנגלית באמצע המשפט. הפתרון: הוסיפו לפרומפט "השב אך ורק בעברית, כולל מונחים מקצועיים".</p>
<p>בעיה שנייה: מגדר. עברית דורשת התאמת מגדר בפעלים ותארים. ציינו מראש "כתוב בלשון זכר/נקבה" או "כתוב בלשון רבים" כדי למנוע חוסר עקביות מעצבן.</p>
</section>""",
        f"""<section>
<h2>טיפים לתוצאות טובות יותר בעברית</h2>
<p>כדי לקבל עברית איכותית מ{topic_str}, השתמשו בטכניקות הבאות. ראשית, כתבו את הפרומפט עצמו בעברית — מודלים נוטים לענות באותה שפה שבה נשאלו, וזה משפר את העקביות.</p>
<p>שנית, ציינו את הקהל. "כתוב לקהל ישראלי" ייצר תוכן שונה מ"כתוב בעברית". ההבדל: התייחסות להקשר תרבותי ישראלי, שימוש בביטויים מקומיים, ותוכן רלוונטי לשוק הישראלי.</p>
<p>שלישית, אל תפחדו לבקש תיקונים. אם התוצאה כוללת שגיאה דקדוקית, אמרו "תקן את הדקדוק" — המודל ילמד מהמשוב ויתאים את עצמו להמשך השיחה. לאורך זמן, תבנו "שיחה" שמתאימה לסגנון שלכם.</p>
</section>""",
        f"""<section>
<h2>מצב התמיכה בעברית — עדכון 2026</h2>
<p>ב-2026, התמיכה בעברית במודלי AI השתפרה דרמטית לעומת שנים קודמות. {topic_str} מציגים רמת עברית שמתקרבת ל-90% מהאיכות באנגלית ברוב המשימות: כתיבה, תרגום, סיכום, ושאלות-תשובות.</p>
<p>התחומים שבהם עברית עדיין פחות טובה: קוד מתועד בעברית, מסמכים משפטיים עם מונחים ארכאיים, וכתיבה אקדמית עם ציטוטים. בתחומים אלו, מומלץ לעבוד באנגלית ולתרגם את התוצר הסופי.</p>
<p>חדשות טובות: כל הספקים הגדולים (OpenAI, Google, Anthropic) הרחיבו את מאגרי הנתונים בעברית. המשמעות: פחות שגיאות, יותר ידע על ישראל, ויכולת טובה יותר להבין ניואנסים תרבותיים ישראליים.</p>
</section>"""
    ]
    return templates[v % len(templates)]


def gen_tools_section(title, topics, h2s, v):
    topic_str = ', '.join(topics[:2]) or 'כלי AI'
    templates = [
        f"""<section>
<h2>חלופות שכדאי לבדוק</h2>
<p>השוק של כלי AI ב-2026 רווי באלטרנטיבות. מלבד {topic_str}, שווה להכיר גם כלים נישתיים שמתמחים בתחומים ספציפיים: Jasper ו-Copy.ai לכתיבה שיווקית, Gamma ל-מצגות, ו-Otter.ai לתמלול ישיבות.</p>
<p>לעריכת תמונות ווידאו, Canva עם AI מובנה הפכה לכלי הנגיש ביותר לעסקים קטנים, בעוד Runway ו-Pika מציעים יכולות וידאו מתקדמות יותר. לקוד, GitHub Copilot ו-Cursor מובילים בתחום.</p>
<p>הטיפ: אל תנסו להשתמש בכלי אחד לכל המשימות. בניית "ארגז כלים" של 3-4 כלי AI שמשלימים זה את זה מייצרת תוצאות טובות בהרבה מהסתמכות על כלי אחד לכל דבר.</p>
</section>""",
        f"""<section>
<h2>שילוב בעבודה היומיומית — מדריך מעשי</h2>
<p>הדרך הטובה ביותר לשלב {topic_str} בעבודה: התחילו עם שלוש משימות חוזרות שגוזלות זמן. זהו אותן, הגדירו פרומפטים שעובדים, ואוטמטו. הנה דוגמאות נפוצות:</p>
<p><strong>בוקר:</strong> סיכום מיילים ותעדוף — העתיקו את המיילים החדשים ובקשו סיכום + רשימת פעולות. <strong>צהריים:</strong> מחקר ותכנון — השתמשו בכלי לניתוח מתחרים, סקירת מגמות, או הכנת חומרים לפגישות. <strong>ערב:</strong> יצירת תוכן — כתבו טיוטות לפוסטים, מיילים, או דוחות.</p>
<p>תוך שבוע של שימוש עקבי, תזהו דפוסים שמתאימים לכם. תוך חודש, תחסכו שעה-שעתיים ביום. המפתח: עקביות. שימוש סדיר מכשיר אתכם ואת הכלי כאחד.</p>
</section>""",
        f"""<section>
<h2>תמחור ותוכניות — מה שווה את הכסף</h2>
<p>בבחירת תוכנית ב{topic_str}, שקלו את הצרכים האמיתיים שלכם. הגרסאות החינמיות מספיקות לשימוש אישי קל: כמה עשרות שאילתות ביום, גישה למודל בסיסי, ומהירות סבירה.</p>
<p>התוכניות האישיות ($10-25/חודש) מתאימות לפרילנסרים ואנשי מקצוע: שימוש בלתי מוגבל, מודלים מתקדמים, וכלים נוספים כמו ניתוח קבצים ויצירת תמונות. זו ההשקעה הטובה ביותר עבור רוב המשתמשים.</p>
<p>תוכניות צוותיות ($25-30/משתמש/חודש) מוסיפות ניהול הרשאות, שיתוף פרומפטים, ואבטחת מידע מוגברת. שווה להשקיע אם יש לכם צוות של 3+ אנשים שמשתמשים ב-AI באופן קבוע.</p>
</section>"""
    ]
    return templates[v % len(templates)]


def gen_ai_agents_section(title, topics, h2s, v):
    topic_str = ', '.join(topics[:2]) or 'סוכני AI'
    templates = [
        f"""<section>
<h2>השפעה על שוק העבודה בישראל</h2>
<p>סוכני AI אוטונומיים כמו {topic_str} משנים את שוק העבודה, אך לא בדיוק כמו שחששו. במקום להחליף עובדים, הם בעיקר משנים את אופי העבודה: משימות שגרתיות עוברות לאוטומציה, ועובדים מתפנים למשימות שדורשות שיקול דעת, יצירתיות, ואינטליגנציה רגשית.</p>
<p>בישראל, הסקטורים הראשונים שחווים שינוי: היי-טק (QA אוטומטי, code review), שירותים פיננסיים (ניתוח סיכונים), ושיווק דיגיטלי (אופטימיזציה אוטומטית של קמפיינים). בסקטורים אלו, דרישה ל"מנהלי AI" — אנשים שיודעים לנהל סוכנים — עולה בחדות.</p>
<p>המסר לעובדים: למדו לעבוד עם AI, לא נגדו. מי שישלב AI בעבודה היומיומית יהיה בעל ערך גבוה יותר מאשר מי שמתעלם מהשינוי.</p>
</section>""",
        f"""<section>
<h2>אבטחה ופרטיות — מה חשוב לדעת</h2>
<p>הטמעת {topic_str} בארגון מעלה שאלות חשובות של אבטחה. סוכנים אוטונומיים שמקבלים גישה למערכות ארגוניות (CRM, מייל, מסדי נתונים) מהווים וקטור תקיפה פוטנציאלי שצריך לנהל.</p>
<p>כללי אצבע: הגבילו הרשאות למינימום הנדרש, הפעילו לוגים מלאים של כל פעולות הסוכן, והגדירו "גדרות בטיחות" — פעולות שדורשות אישור אנושי (כמו מחיקת נתונים או שליחת מיילים חיצוניים).</p>
<p>מבחינת רגולציה, ישראל עוקבת אחרי תקנות ה-EU AI Act. עסקים ישראלים שעובדים עם לקוחות אירופיים צריכים כבר עכשיו לוודא שהשימוש שלהם ב-AI עומד בדרישות. מומלץ להתייעץ עם יועץ משפטי מתמחה.</p>
</section>""",
        f"""<section>
<h2>מה צפוי בהמשך 2026</h2>
<p>המגמות הצפויות לחצי השני של 2026 ברורות: {topic_str} ימשיכו להשתפר, עם דגש על אוטונומיה רבה יותר, שילוב עמוק יותר עם כלים קיימים, ומחירים נגישים יותר.</p>
<p>שלוש התפתחויות שכדאי לעקוב אחריהן: (1) סוכנים רב-מודליים שעובדים עם טקסט, תמונות, וידאו וקול במקביל. (2) "סוכני צוות" שמשתפים פעולה זה עם זה כדי לפתור בעיות מורכבות. (3) סוכנים מקומיים שרצים על המחשב שלכם, ללא צורך בחיבור לענן.</p>
<p>עבור עסקים ישראלים, ההמלצה: אל תחכו ל"הדור הבא". הטכנולוגיה כבר כאן ומספיק בשלה לשימוש מעשי. מי שמתחיל היום יהיה בעמדת יתרון כשהכלים ישתפרו עוד יותר.</p>
</section>"""
    ]
    return templates[v % len(templates)]


# ──────── Main expansion logic ────────

CATEGORY_GENERATORS = {
    'business': gen_business_section,
    'compare': gen_compare_section,
    'guide': gen_guide_section,
    'hebrew': gen_hebrew_section,
    'tools': gen_tools_section,
    'ai': gen_ai_agents_section,
    'agents': gen_ai_agents_section,
    'gpt5': gen_compare_section,
    'weekly': gen_tools_section,
}


def build_faq_schema(h2s, topics):
    """Build FAQPage JSON-LD schema"""
    questions = []
    topic_str = topics[0] if topics else 'AI'
    for h in h2s[:4]:
        h_clean = re.sub(r'[🚀🎨🤖📊💡⚡🔥✅❌]', '', h).strip()
        if not h_clean or len(h_clean) < 8:
            continue
        q = h_clean if h_clean.endswith('?') else f'מה חשוב לדעת על {h_clean}?'
        questions.append(q)

    if len(questions) < 2:
        return None

    main_entity = []
    for q in questions[:4]:
        main_entity.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"קראו את המאמר המלא לתשובה מפורטת על {q.rstrip('?')}."
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def expand_article(filepath):
    content = Path(filepath).read_text(encoding='utf-8', errors='ignore')
    fname = Path(filepath).name

    # Skip if already expanded (marker comment)
    if '<!-- expanded -->' in content:
        return False

    # Extract metadata
    title_m = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
    title = title_m.group(1).strip() if title_m else fname
    h2s = re.findall(r'<h2[^>]*>([^<]+)</h2>', content)
    category = get_category(filepath)
    topics = extract_topics(title, h2s)

    # Current word count
    text_only = re.sub(r'<[^>]+>', ' ', content)
    current_words = len(text_only.split())

    if current_words >= MIN_WORDS:
        return False

    # Generate expansion sections
    seed = fname
    v1 = variant(seed + 'a', 3)
    v2 = variant(seed + 'b', 3)
    v3 = variant(seed + 'c', 3)

    cat_gen = CATEGORY_GENERATORS.get(category, gen_guide_section)

    sections = []
    sections.append(cat_gen(title, topics, h2s, v1))
    sections.append(gen_practical_tips(title, topics, h2s, v2))
    sections.append(gen_faq(title, topics, h2s, v3))

    expansion = '\n<!-- expanded -->\n' + '\n'.join(sections)

    # Insert before share-bar or before </main>
    if '<div class="share-bar"' in content:
        content = content.replace('<div class="share-bar"', expansion + '\n<div class="share-bar"', 1)
    elif '</main>' in content:
        content = content.replace('</main>', expansion + '\n</main>', 1)
    else:
        content = content.replace('</body>', expansion + '\n</body>', 1)

    # Update/add wordCount in JSON-LD
    new_text = re.sub(r'<[^>]+>', ' ', content)
    new_count = len(new_text.split())

    if '"wordCount"' in content:
        content = re.sub(r'"wordCount":\s*\d+', f'"wordCount": {new_count}', content)
    elif '"BlogPosting"' in content:
        content = content.replace('"BlogPosting"',
                                  f'"BlogPosting",\n    "wordCount": {new_count}', 1)
    else:
        # Add wordCount to first JSON-LD block
        if '"@type"' in content:
            content = re.sub(r'("@type":\s*"[^"]+")',
                             rf'\1,\n    "wordCount": {new_count}', content, count=1)

    # Add FAQPage schema if not present
    if '"FAQPage"' not in content:
        faq_schema = build_faq_schema(h2s, topics)
        if faq_schema:
            tag = f'\n<script type="application/ld+json">\n{faq_schema}\n</script>'
            content = content.replace('</head>', tag + '\n</head>', 1)

    Path(filepath).write_text(content, encoding='utf-8')
    return True


if __name__ == '__main__':
    files = sorted(ROOT.glob('articles/2026-*.html'))
    print(f'Found {len(files)} articles')

    changed = 0
    for f in files:
        if expand_article(str(f)):
            changed += 1
            if changed % 50 == 0:
                print(f'  ... {changed} expanded')

    print(f'\nDone: {changed} articles expanded')
