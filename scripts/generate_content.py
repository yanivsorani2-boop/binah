#!/usr/bin/env python3
"""
generate_content.py — מרחיב מאמרים ב-articles/2026-*.html ל-1500+ מילים.
דורש: ANTHROPIC_API_KEY בסביבה.
הרץ מה-root של הפרויקט: python3 scripts/generate_content.py

מה הסקריפט עושה:
  - סורק articles/2026-*.html
  - מוסיף תוכן Hebrew SEO-optimized דרך Claude API
  - מעדכן wordCount ב-JSON-LD
  - מוסיף FAQPage schema למאמרים עם "שאלות נפוצות"
  - מוסיף HowTo schema למאמרים עם "צעד-אחר-צעד"
  - delay 1 שניה בין קריאות
  - commit + push אחרי כל 50 מאמרים
"""
import os
import re
import sys
import time
import glob
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
BATCH_SIZE = 50
DELAY_SECONDS = 1
MIN_WORDS = 1500

try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
except (ImportError, KeyError) as e:
    print(f"ERROR: {e}")
    print("הרץ: pip install anthropic && export ANTHROPIC_API_KEY='sk-ant-...'")
    sys.exit(1)


def count_words(html: str) -> int:
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return len(text.split())


def get_word_count(html: str) -> int:
    m = re.search(r'"wordCount":\s*(\d+)', html)
    return int(m.group(1)) if m else 0


def update_word_count(html: str, count: int) -> str:
    if re.search(r'"wordCount":\s*\d+', html):
        return re.sub(r'"wordCount":\s*\d+', f'"wordCount": {count}', html)
    return html


def has_faq_section(html: str) -> bool:
    return bool(re.search(r'שאלות נפוצות|FAQ|שאלות ותשובות', html, re.IGNORECASE))


def has_howto_section(html: str) -> bool:
    return bool(re.search(r'צעד.{0,10}צעד|שלב.{0,10}שלב|step.{0,10}step|מדריך שלב', html, re.IGNORECASE))


def has_faq_schema(html: str) -> bool:
    return '"FAQPage"' in html


def has_howto_schema(html: str) -> bool:
    return '"HowTo"' in html


def expand_article(path: Path) -> bool:
    """מחזיר True אם שונה"""
    content = path.read_text(encoding='utf-8', errors='ignore')
    word_count = get_word_count(content)

    if word_count >= MIN_WORDS:
        print(f"  SKIP {path.name} ({word_count} words)")
        return False

    print(f"  EXPAND {path.name} ({word_count} words) ...", end='', flush=True)

    # Extract title for context
    title_m = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
    title = title_m.group(1).strip() if title_m else path.stem

    prompt = f"""אתה כותב תוכן SEO בעברית לבלוג AI. המאמר בשם: "{title}".
המאמר כרגע קצר מדי. הוסף 3-4 פסקאות HTML שמרחיבות את הנושא, כולל:
1. יתרונות וחסרונות
2. שימושים מעשיים לישראלים
3. השוואה לחלופות
4. טיפים מעשיים

חזור אך ורק ב-HTML (ללא ```), כולל תגי <section> ו-<p> בעברית, RTL, ללא JavaScript.
כתוב 400-600 מילים."""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        new_section = response.content[0].text.strip()
    except Exception as e:
        print(f" ERROR: {e}")
        return False

    # Inject before </main>
    if '</main>' in content:
        content = content.replace('</main>', f'\n{new_section}\n</main>', 1)
    else:
        content = content.replace('</body>', f'\n{new_section}\n</body>', 1)

    # Update wordCount
    new_count = count_words(content)
    content = update_word_count(content, new_count)

    # Add FAQPage schema if needed
    if has_faq_section(content) and not has_faq_schema(content):
        faq_schema = _build_faq_schema(content)
        if faq_schema:
            content = _inject_schema(content, faq_schema)

    # Add HowTo schema if needed
    if has_howto_section(content) and not has_howto_schema(content):
        howto_schema = _build_howto_schema(content, title)
        if howto_schema:
            content = _inject_schema(content, howto_schema)

    path.write_text(content, encoding='utf-8')
    print(f" OK ({new_count} words)")
    return True


def _build_faq_schema(html: str) -> str:
    # Extract Q&A pairs from the HTML
    questions = re.findall(r'<(?:h[2-4]|dt|strong)[^>]*>([^<]{10,100}?)\?<', html)
    if len(questions) < 2:
        return ""
    faqs = []
    for q in questions[:5]:
        faqs.append({"@type": "Question", "name": q.strip() + "?",
                     "acceptedAnswer": {"@type": "Answer", "text": "ראה פרטים במאמר."}})
    schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": faqs}
    return json.dumps(schema, ensure_ascii=False, indent=2)


def _build_howto_schema(html: str, title: str) -> str:
    steps = re.findall(r'<(?:li|h[2-4])[^>]*>([^<]{10,100})</(?:li|h[2-4])>', html)
    if len(steps) < 2:
        return ""
    how_steps = [{"@type": "HowToStep", "text": s.strip()} for s in steps[:6]]
    schema = {"@context": "https://schema.org", "@type": "HowTo",
              "name": title, "step": how_steps}
    return json.dumps(schema, ensure_ascii=False, indent=2)


def _inject_schema(html: str, schema_json: str) -> str:
    tag = f'\n<script type="application/ld+json">\n{schema_json}\n</script>'
    if '</head>' in html:
        return html.replace('</head>', tag + '\n</head>', 1)
    return html


def git_commit_push(batch_num: int):
    cwd = str(ROOT)
    subprocess.run(["git", "add", "articles/"], cwd=cwd, check=True)
    subprocess.run(["git", "commit", "-m",
                    f"SEO: expand article content batch {batch_num}",
                    "--author", "Claude Sonnet 4.6 <noreply@anthropic.com>"],
                   cwd=cwd, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=cwd, check=True)


if __name__ == "__main__":
    files = sorted(ROOT.glob("articles/2026-*.html"))
    print(f"Found {len(files)} articles to process")

    batch_num = 1
    changed_in_batch = 0

    for i, f in enumerate(files):
        changed = expand_article(f)
        if changed:
            changed_in_batch += 1
        time.sleep(DELAY_SECONDS)

        if (i + 1) % BATCH_SIZE == 0:
            if changed_in_batch > 0:
                print(f"\n--- Committing batch {batch_num} ({changed_in_batch} files) ---")
                git_commit_push(batch_num)
            batch_num += 1
            changed_in_batch = 0

    # Final batch
    if changed_in_batch > 0:
        print(f"\n--- Committing final batch {batch_num} ({changed_in_batch} files) ---")
        git_commit_push(batch_num)

    print("\nDone. Verify:")
    print('  for f in articles/2026-*.html; do')
    print('    words=$(grep -oP \'"wordCount": \\K[0-9]+\' "$f")')
    print('    [ "$words" -lt 1500 ] && echo "SHORT: $f ($words)"')
    print('  done')
