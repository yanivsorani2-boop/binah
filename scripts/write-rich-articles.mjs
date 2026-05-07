import Anthropic from '@anthropic-ai/sdk';
import fs from 'fs';

const client = new Anthropic();
const plan = JSON.parse(fs.readFileSync('.cluster-plan.json','utf8'));

const allArticles = fs.readdirSync('articles').filter(f=>f.endsWith('.html')).map(f=>f.slice(0,-5));
const allGuides = fs.readdirSync('guides').filter(f=>f.endsWith('.html')).map(f=>f.slice(0,-5));

const TOPIC_MAP = {
  'compare-flagship-models': {topic_he:'השוואת Claude vs GPT-4o vs Gemini 2.5 Pro — איזה מודל AI הכי טוב ב-2026', keywords:['Claude','GPT-4o','Gemini 2.5 Pro','השוואת מודלים','בנצ\'מרק AI','מחיר API'], category:'השוואות'},
  'compare-models-general': {topic_he:'השוואת מודלי AI מקיפה — בנצ\'מרקים, מחירים ויכולות 2026', keywords:['מודלי AI','בנצ\'מרק','MMLU','HumanEval','השוואה'], category:'השוואות'},
  'guide-chatgpt-mastery': {topic_he:'מדריך ChatGPT המקיף 2026 — ממתחיל עד מומחה', keywords:['ChatGPT','GPT-4o','פרומפטים','OpenAI','שימוש מתקדם'], category:'מדריכים'},
  'guide-prompts-engineering': {topic_he:'Prompt Engineering בעברית — המדריך המקצועי המלא', keywords:['פרומפטים','prompt engineering','chain of thought','few-shot'], category:'מדריכים'},
  'guide-ai-tools-overview': {topic_he:'מדריך כלי AI 2026 — מה לבחור ולמה', keywords:['כלי AI','AI tools','השוואה','מומלצים'], category:'מדריכים'},
  'guide-weekly-ai-roundup': {topic_he:'סיכום שבועי AI — חידושים, מודלים וכלים חדשים באפריל 2026', keywords:['חדשות AI','עדכונים שבועיים','מודלים חדשים'], category:'חדשות'},
  'tools-coding-comparison': {topic_he:'הכלים הטובים ביותר לתכנות עם AI ב-2026 — Cursor, Copilot, Claude Code', keywords:['Cursor','Copilot','Claude Code','AI coding','vibe coding'], category:'כלים'},
  'tools-video-comparison': {topic_he:'כלי AI ליצירת וידאו — Sora, Runway, Pika ועוד ב-2026', keywords:['Sora','Runway','Pika','AI video','יצירת סרטונים'], category:'כלים'},
  'tools-writing-comparison': {topic_he:'כלי כתיבה עם AI — מה הכי טוב לתוכן בעברית ב-2026', keywords:['כתיבה AI','copywriting','תוכן שיווקי','עברית'], category:'כלים'},
  'tools-comprehensive-comparison': {topic_he:'השוואת כלי AI מקיפה 2026 — לכל תחום הכלי הטוב ביותר', keywords:['כלי AI','השוואה','המלצות','best AI tools'], category:'כלים'},
  'tools-weekly-roundup': {topic_he:'סיכום שבועי כלי AI חדשים — אפריל 2026', keywords:['כלים חדשים','עדכונים','launches'], category:'כלים'},
  'business-ai-roi-israel': {topic_he:'AI לעסקים בישראל — איך להחזיר את ההשקעה תוך 3 חודשים', keywords:['AI לעסקים','ROI','אוטומציה','ישראל','עסקים קטנים'], category:'AI לעסקים'},
  'business-weekly-roundup': {topic_he:'AI בעולם העסקי — סיכום שבועי לעסקים ישראלים', keywords:['AI עסקים','חדשות','ישראל'], category:'AI לעסקים'},
  'hebrew-ai-tools-review': {topic_he:'כלי AI בעברית — סקירה מלאה של מה שעובד ומה לא ב-2026', keywords:['AI עברית','כלים בעברית','תמיכה בעברית','RTL'], category:'עברית'},
  'hebrew-weekly-roundup': {topic_he:'סיכום שבועי כלי AI בעברית — אפריל 2026', keywords:['עברית','כלים','חדשות'], category:'עברית'},
  'ai-agents-enterprise': {topic_he:'סוכני AI בארגונים — המהפכה האוטונומית של 2026', keywords:['AI agents','autonomous','enterprise','automation','ארגונים'], category:'מאמרים'},
  'misc': {topic_he:'GPT-5 ומה שאחריו — השפעת המודלים החדשים על תעשיית ה-AI ב-2026', keywords:['GPT-5','מודלים חדשים','OpenAI','השפעה'], category:'מאמרים'},
};

function extractMain(html) {
  const m = html.match(/<main[^>]*>([\s\S]*?)<\/main>/);
  if (!m) return '';
  return m[1].replace(/<script[\s\S]*?<\/script>/g,'').replace(/<style[\s\S]*?<\/style>/g,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
}

function buildPrompt(topic, keywords, sources, allSlugs, category, today) {
  return `אתה כותב SEO בעברית עם 15 שנות ניסיון. אתה כותב מאמר עומק לבלוג binah.co.il (AI בעברית).

הנושא: ${topic}
מילות מפתח עיקריות: ${keywords.join(', ')}
קטגוריה: ${category}
תאריך: ${today}

הנה ${sources.length} מאמרים קיימים על אותו נושא שגוגל דחה כי הם דומים מדי. שאיב מהם את כל הנתונים הקונקרטיים, ההשוואות, הדוגמאות והסטטיסטיקות. צור מהם מאמר אחד עשיר שיהיה הקנוני היחיד.

=== תוכן הקבצים המקוריים ===
${sources.map((s,i)=>`--- מקור ${i+1}: ${s.slug} ---\n${s.text.substring(0,3000)}\n`).join('\n')}

=== דרישות חמורות ===
1. אורך: 3200-3800 מילים בעברית. ספור לפני שמסיים.
2. מבנה חובה (לפי הסדר):
   - <h1> כותרת חזקה ושיווקית עם מילת המפתח העיקרית
   - <p> פתיחה חזקה (hook) של 80-120 מילים שמסבירה למה זה רלוונטי לקוראים ב-2026
   - <h2> "מה חדש ב-2026" - סיכום של 3-5 שינויים אמיתיים מהשנה האחרונה (מבוסס על המקורות)
   - <h2> "השוואה מקיפה" - עם <table> שמכיל לפחות 5 שורות ו-4 עמודות (מודל/כלי, מחיר, יכולת מרכזית, מתי להשתמש)
   - <h2> "ניתוח לעומק לפי קטגוריה" - 3-5 תתי-<h3>, כל אחד עם דוגמה אמיתית, נתון מספרי, או ציטוט מבנצ'מרק
   - <h2> "מקרי שימוש מעשיים" - 4-6 use cases קונקרטיים. כל אחד עם <h3> ופסקה של 80-150 מילים שמתארת תרחיש אמיתי + הכלי המומלץ + צעדים בפועל
   - <h2> "טעויות נפוצות שכדאי להימנע מהן" - 4-5 טעויות אמיתיות, כל אחת עם הסבר ופתרון
   - <h2> "מה כדאי לבחור - לפי סוג משתמש" - המלצות נפרדות ל: מפתחים, יוצרי תוכן, עסקים קטנים, סטודנטים
   - <h2> "שאלות נפוצות" - 6-8 שאלות שגולש אמיתי ישאל ב-Google People Also Ask. תשובות 2-4 משפטים, מבוססות על המאמר. אסור placeholder.
   - <h2> "סיכום והמלצה" - 100-150 מילים. 3 takeaways עיקריים בנקודות.
3. טון: מקצועי אבל נגיש. בלי buzzwords ריקים. בלי שיווק. בלי "מהפכת AI" או "עתיד מסעיר".
4. ערך אמיתי: כל H2 חייב להכיל לפחות פרט קונקרטי אחד - מספר, תאריך, שם כלי, גרסה, מחיר, ביצוע בנצ'מרק. אסור פסקאות שהן רק generalities.
5. קישורים פנימיים: הוסף 6-10 <a href="/articles/SLUG"> או <a href="/guides/SLUG"> בתוך הפסקאות. בחר רק מהרשימה הזו: ${allSlugs.slice(0,60).join(', ')}. הקישור חייב להיות במשפט שהזכרת בו את הנושא של המאמר המקושר.
6. SEO:
   - מילת המפתח העיקרית בH1, ב-H2 הראשון, ובפסקה הראשונה.
   - LSI keywords (מילים נרדפות) ב-3-4 H2s.
   - אורך פסקה: 2-4 משפטים. אסור פסקה ארוכה מדי.
7. עברית:
   - RTL נקי. סימני פיסוק נכונים.
   - בלי אנגלית מיותרת - תרגם מונחים אם יש מקבילה (אבל שמור שמות כלים באנגלית: ChatGPT, Claude, Gemini).
   - בלי אימוג'ים. בלי ASCII art.
8. אסור absolutely:
   - "כפי שראינו במאמרים קודמים" / "לתשובה מפורטת ראו..."
   - placeholder text
   - quotes שלא ניתן לאמת
   - הבטחות שיווקיות
   - תוכן שחוזר על עצמו

=== פלט ===
החזר רק HTML גולמי שיוזרק בתוך <main>. בלי <html>/<head>/<body>. בלי הסברים שלך. בלי prefix. רק HTML שמתחיל ב-<h1> ומסתיים ב-</p> או דומה.`;
}

async function processCluster(cname, info) {
  const meta = TOPIC_MAP[cname];
  if (!meta) { console.log(`  No meta for ${cname}, skipping`); return null; }

  const allSlugs = [
    ...allArticles.filter(s => !s.startsWith('2026-')).map(s => `/articles/${s}`),
    ...allGuides.map(s => `/guides/${s}`)
  ];

  const sources = [info.canonical, ...info.redirects].slice(0, 8).map(slug => {
    const p = `articles/${slug}.html`;
    if (!fs.existsSync(p)) return null;
    return { slug, text: extractMain(fs.readFileSync(p, 'utf8')) };
  }).filter(Boolean);

  if (!sources.length) { console.log(`  No sources for ${cname}`); return null; }

  const today = new Date().toISOString().slice(0, 10);
  const prompt = buildPrompt(meta.topic_he, meta.keywords, sources, allSlugs, meta.category, today);

  console.log(`  [${cname}] Sending to Claude (${sources.length} sources, ${Math.round(prompt.length/1000)}k chars)...`);

  let content;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const msg = await client.messages.create({
        model: 'claude-sonnet-4-5-20250514',
        max_tokens: 16000,
        messages: [{ role: 'user', content: prompt }]
      });
      content = msg.content[0].text.trim();
      break;
    } catch (e) {
      console.log(`  Attempt ${attempt} failed: ${e.message}`);
      if (attempt < 3) {
        console.log(`  Waiting ${attempt * 30}s before retry...`);
        await new Promise(r => setTimeout(r, attempt * 30000));
      } else {
        throw e;
      }
    }
  }

  // Strip markdown fences if present
  content = content.replace(/^```html?\s*\n?/i, '').replace(/\n?```\s*$/i, '');

  if (!content.startsWith('<h1')) {
    // Try to find <h1 in the content
    const idx = content.indexOf('<h1');
    if (idx > 0) content = content.substring(idx);
  }

  const wordCount = content.replace(/<[^>]+>/g, ' ').split(/\s+/).filter(w => w.length).length;
  console.log(`  Got ${wordCount} words`);

  if (wordCount < 2500) {
    console.log(`  WARNING: Only ${wordCount} words, attempting extension...`);
    try {
      const ext = await client.messages.create({
        model: 'claude-sonnet-4-5-20250514',
        max_tokens: 16000,
        messages: [
          { role: 'user', content: prompt },
          { role: 'assistant', content: content },
          { role: 'user', content: `המאמר הזה רק ${wordCount} מילים. הרחב אותו ל-3500+ מילים. הוסף עוד דוגמאות, נתונים מספריים, use cases ו-FAQ. החזר את כל ה-HTML מחדש (מתחיל ב-<h1>).` }
        ]
      });
      const ext_content = ext.content[0].text.trim().replace(/^```html?\s*\n?/i, '').replace(/\n?```\s*$/i, '');
      const ext_wc = ext_content.replace(/<[^>]+>/g, ' ').split(/\s+/).filter(w => w.length).length;
      if (ext_wc > wordCount) {
        content = ext_content;
        console.log(`  Extended to ${ext_wc} words`);
      }
    } catch (e) {
      console.log(`  Extension failed: ${e.message}, using original`);
    }
  }

  return { content, wordCount, meta };
}

(async () => {
  fs.mkdirSync('.merged', { recursive: true });
  const results = {};
  const entries = Object.entries(plan);

  for (let i = 0; i < entries.length; i++) {
    const [cname, info] = entries[i];
    console.log(`\n[${i+1}/${entries.length}] Processing ${cname} (${info.count} articles)...`);

    try {
      const result = await processCluster(cname, info);
      if (!result) continue;

      const { content, wordCount, meta } = result;

      // Write merged HTML for review
      fs.writeFileSync(`.merged/${cname}.html`, content);

      // Update canonical article file
      const canPath = `articles/${info.canonical}.html`;
      let html = fs.readFileSync(canPath, 'utf8');

      // Replace main content
      html = html.replace(/<main[^>]*>[\s\S]*?<\/main>/,
        `<main class="article-body">\n      <a href="../index.html" class="btn-back">-> חזרה</a>\n${content}\n</main>`);

      // Update wordCount in BlogPosting JSON-LD
      html = html.replace(/"wordCount":\s*\d+/, `"wordCount": ${wordCount}`);

      // Update dateModified
      const today = new Date().toISOString().slice(0, 10);
      html = html.replace(/"dateModified":\s*"[^"]+"/, `"dateModified": "${today}"`);

      // Update title
      const newTitle = meta.topic_he + ' | בינה';
      html = html.replace(/<title>[^<]+<\/title>/, `<title>${newTitle}</title>`);

      // Update og:title
      html = html.replace(/(<meta\s+property="og:title"\s+content=")[^"]+(")/,
        `$1${meta.topic_he}$2`);

      // Update headline in BlogPosting
      html = html.replace(/"headline":\s*"[^"]+"/, `"headline": "${meta.topic_he.replace(/"/g, '\\"')}"`);

      fs.writeFileSync(canPath, html);
      results[cname] = { canonical: info.canonical, wordCount };
      console.log(`  Saved ${canPath} (${wordCount} words)`);

      // Rate limit: wait 5s between clusters
      if (i < entries.length - 1) {
        await new Promise(r => setTimeout(r, 5000));
      }
    } catch (e) {
      console.error(`  FAILED ${cname}: ${e.message}`);
      results[cname] = { canonical: info.canonical, error: e.message };
    }
  }

  console.log('\n=== SUMMARY ===');
  for (const [cname, r] of Object.entries(results)) {
    if (r.error) console.log(`  FAIL ${cname}: ${r.error}`);
    else console.log(`  OK ${cname}: ${r.canonical} (${r.wordCount} words)`);
  }

  fs.writeFileSync('.merge-results.json', JSON.stringify(results, null, 2));
})();
