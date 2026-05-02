#!/usr/bin/env node
import fs from 'fs';

const ARTICLES_DIR = 'articles';

function extractTitle(html) {
  const m = html.match(/<title>([^<]+)<\/title>/i);
  return m ? m[1].replace(/\s*\|\s*בינה\s*$/, '').trim() : '';
}
function extractMeta(html, attr) {
  const re = new RegExp(`<meta[^>]*(?:name|property)="${attr}"[^>]*content="([^"]*)"`, 'i');
  const m = html.match(re);
  return m ? m[1] : '';
}
function extractDate(file) {
  const m = file.match(/^(\d{4}-\d{2}-\d{2})/);
  return m ? m[1] : '';
}

const categories = {
  comparisons: {
    he: 'השוואות',
    title: 'השוואות AI — איזה מודל הכי טוב?',
    desc: 'השוואות מקיפות בין מודלי AI מובילים: GPT-4o, Claude, Gemini ועוד. מחירים, ביצועים ויתרונות.',
    intro: 'עולם ה-AI מציע היום עשרות מודלים ופלטפורמות שמתחרים זה בזה על כל פרמטר אפשרי — מהירות, דיוק, מחיר, יכולת קידוד ויצירתיות. בעמוד זה ריכזנו את כל ההשוואות המקיפות שלנו, כדי שתוכלו לבחור את הכלי שמתאים בדיוק לצרכים שלכם. כל השוואה מבוססת על בדיקות מעשיות שביצענו בפועל.',
    match: (slug) => slug.includes('compare-')
  },
  guides: {
    he: 'מדריכים',
    title: 'מדריכי AI בעברית — מתחילים עד מתקדמים',
    desc: 'מדריכים מעשיים לשימוש ב-ChatGPT, Claude, כלי AI ופרומפטים. צעד אחרי צעד, בעברית.',
    intro: 'בין אם אתם מתחילים לגמרי ובין אם כבר משתמשים ב-AI כל יום — המדריכים שלנו יעזרו לכם להוציא את המקסימום מכל כלי. מפרומפטים בסיסיים ועד אסטרטגיות מתקדמות, הכל כתוב בעברית פשוטה עם דוגמאות מעשיות. כל מדריך נבדק ונכתב מניסיון אישי.',
    match: (slug) => slug.includes('guide-')
  },
  tools: {
    he: 'כלים',
    title: 'כלי AI — ביקורות, השוואות וטיפים',
    desc: 'סקירות מעמיקות של כלי AI לקידוד, כתיבה, וידאו ועוד. כולל כלים עם תמיכה בעברית.',
    intro: 'שוק כלי ה-AI מתרחב בקצב מסחרר. כל שבוע יוצאים כלים חדשים שמבטיחים לחסוך זמן, לייעל תהליכים ולשדרג את העבודה שלכם. אנחנו בודקים כל כלי בפועל ומדווחים מה באמת עובד — ומה פחות. מכלי קידוד ועד כלי וידאו, מחיפוש מידע ועד אוטומציה.',
    match: (slug) => slug.includes('tools-') || slug.includes('hebrew-')
  },
  business: {
    he: 'AI לעסקים',
    title: 'AI לעסקים — ROI, אוטומציה וכלים לעסקים ישראליים',
    desc: 'איך עסקים ישראליים משתמשים ב-AI: החזר השקעה, כלים מומלצים ומדריכים ליישום.',
    intro: 'בינה מלאכותית כבר לא רק לחברות הייטק ענקיות. עסקים קטנים ובינוניים בישראל מאמצים AI לשירות לקוחות, שיווק, ניתוח נתונים ואוטומציה — ורואים תוצאות מיידיות. כאן תמצאו מדריכים מעשיים, ניתוחי ROI וכלים מומלצים שמתאימים בדיוק לשוק הישראלי.',
    match: (slug) => slug.includes('business-') || slug.includes('ai-agents-')
  },
  news: {
    he: 'חדשות',
    title: 'חדשות AI שבועיות — עדכונים ומגמות',
    desc: 'חדשות שבועיות מעולם ה-AI: השקות, מגמות, ועדכונים חשובים בבינה מלאכותית.',
    intro: 'עולם ה-AI זז מהר — וקשה לעקוב אחרי הכל. בעמוד זה מרוכזים כל הסיכומים השבועיים שלנו: השקות חדשות, עדכוני מודלים, מגמות בתעשייה וחדשות שכדאי לדעת. אנחנו מסננים את הרעש ומביאים רק את מה שבאמת חשוב.',
    match: (slug) => slug.includes('weekly-') || slug.includes('gpt5-')
  },
  products: {
    he: 'מוצרי AI',
    title: 'מוצרי AI — סקירות מכשירים וחומרה',
    desc: 'סקירות מוצרי AI: מחשבים, טלפונים, רובוטים ומכשירים חכמים עם בינה מלאכותית.',
    intro: 'בינה מלאכותית לא רק בענן — היא נכנסת לחומרה שאנחנו משתמשים בה כל יום. מטלפונים חכמים ועד רובוטים, ממחשבים ניידים ועד משקפיים — סקרנו את המוצרים שמביאים AI לחיי היומיום שלכם.',
    match: (slug) => slug.includes('product-')
  }
};

// Build article index
const allFiles = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html'));
const articleData = allFiles.map(file => {
  const slug = file.replace('.html', '');
  const html = fs.readFileSync(`${ARTICLES_DIR}/${file}`, 'utf8');
  return {
    file, slug,
    title: extractTitle(html),
    desc: extractMeta(html, 'description'),
    date: extractDate(file),
    ogImg: `/images/og/${slug}.jpg`
  };
}).filter(a => a.title);

for (const [key, cat] of Object.entries(categories)) {
  const articles = articleData.filter(a => cat.match(a.slug)).sort((a, b) => b.date.localeCompare(a.date));

  const cardHtml = articles.map(a => `      <article class="article-card has-thumb reveal">
        <div class="card-thumb"><h3 class="thumb-title"><a href="/articles/${a.file}">${a.title}</a></h3></div>
        <div class="card-body">
          <p class="card-excerpt">${a.desc}</p>
          <div class="card-meta"><span>${a.date}</span></div>
        </div>
      </article>`).join('\n');

  const schemaItems = articles.map((a, i) => `        {"@type":"ListItem","position":${i + 1},"url":"https://binah.co.il/articles/${a.slug}","name":"${a.title.replace(/"/g, '\\"')}"}`).join(',\n');

  const html = `<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <script>(function(){var t=localStorage.getItem('binah-theme');if(t==='light')document.documentElement.setAttribute('data-theme','light');})();</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="${cat.desc}">
  <title>${cat.title} | בינה — AI בעברית</title>
  <link rel="preload" href="../styles.min.css" as="style" onload="this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="../styles.min.css"></noscript>
  <link rel="canonical" href="https://binah.co.il/categories/${key}.html">
  <link rel="alternate" type="application/rss+xml" title="בינה RSS" href="/feed.xml">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-MG65DD6GYJ"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-MG65DD6GYJ');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9475752562192165" crossorigin="anonymous"></script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "${cat.title}",
    "description": "${cat.desc}",
    "url": "https://binah.co.il/categories/${key}.html",
    "mainEntity": {
      "@type": "ItemList",
      "numberOfItems": ${articles.length},
      "itemListElement": [
${schemaItems}
      ]
    }
  }
  </script>
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
        <a href="../business.html">AI לעסקים</a>
        <a href="../ai-products.html">מוצרי AI</a>
      </nav>
    </div>
  </div>
</header>
<main>
  <div class="container" style="padding:40px 0 80px">
    <h1 style="font-size:2rem;font-weight:900;margin-bottom:16px">${cat.title}</h1>
    <p style="color:var(--text-muted);margin-bottom:32px;max-width:700px;line-height:1.7">${cat.intro}</p>
    <div class="articles-grid">
${cardHtml}
    </div>
  </div>
</main>
<footer style="text-align:center;padding:24px;color:var(--text-muted);font-size:0.85rem;border-top:1px solid var(--border)">
  <p>© 2025-2026 בינה — AI בעברית. כל הזכויות שמורות.</p>
</footer>
</body>
</html>`;

  fs.writeFileSync(`categories/${key}.html`, html);
  console.log(`Created categories/${key}.html with ${articles.length} articles`);
}
