#!/usr/bin/env node
/**
 * Generate article cards for all 63 canonical (date-prefixed) articles
 * and inject them into index.html after <!-- NEW_ARTICLES_HERE -->
 */
import fs from 'fs';

const ARTICLES_DIR = 'articles';

function extractMeta(html, attr) {
  const re = new RegExp(`<meta[^>]*(?:name|property)="${attr}"[^>]*content="([^"]*)"`, 'i');
  const m = html.match(re);
  if (m) return m[1];
  const re2 = new RegExp(`<meta[^>]*content="([^"]*)"[^>]*(?:name|property)="${attr}"`, 'i');
  const m2 = html.match(re2);
  return m2 ? m2[1] : '';
}

function extractTitle(html) {
  const m = html.match(/<title>([^<]+)<\/title>/i);
  return m ? m[1].replace(/\s*\|\s*בינה\s*$/, '').trim() : '';
}

function getCategory(slug) {
  if (slug.includes('compare-') || slug.includes('compare_')) return { cat: 'compare', label: 'השוואה' };
  if (slug.includes('guide-')) return { cat: 'guide', label: 'מדריך' };
  if (slug.includes('tools-') || slug.includes('tool-')) return { cat: 'tools', label: 'כלים' };
  if (slug.includes('business-') || slug.includes('biz-')) return { cat: 'business', label: 'AI לעסקים' };
  if (slug.includes('crazy-')) return { cat: 'crazy', label: 'AI מטורף' };
  if (slug.includes('product-')) return { cat: 'products', label: 'מוצרי AI' };
  if (slug.includes('hebrew-')) return { cat: 'tools', label: 'עברית' };
  if (slug.includes('weekly-')) return { cat: 'news', label: 'חדשות' };
  if (slug.includes('gpt5-')) return { cat: 'news', label: 'חדשות' };
  return { cat: 'guide', label: 'מאמר' };
}

function formatDate(dateStr) {
  const months = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
  const [y, m, d] = dateStr.split('-').map(Number);
  return `${d} ${months[m-1]} ${y}`;
}

// Get all canonical date-prefixed articles
const files = fs.readdirSync(ARTICLES_DIR)
  .filter(f => f.endsWith('.html') && f.match(/^\d{4}-\d{2}-\d{2}-/))
  .sort().reverse(); // newest first

const cards = [];

for (const file of files) {
  const slug = file.replace('.html', '');
  const html = fs.readFileSync(`${ARTICLES_DIR}/${file}`, 'utf8');
  const title = extractTitle(html);
  const desc = extractMeta(html, 'description');
  const ogImage = extractMeta(html, 'og:image');
  const dateMatch = file.match(/^(\d{4}-\d{2}-\d{2})/);
  const dateStr = dateMatch ? dateMatch[1] : '';
  const { cat, label } = getCategory(slug);

  // Extract wordCount for reading time
  const wcMatch = html.match(/"wordCount"\s*:\s*(\d+)/);
  const wordCount = wcMatch ? parseInt(wcMatch[1]) : 1000;
  const readTime = Math.max(3, Math.round(wordCount / 200));

  // Use local image path for src
  const imgFilename = slug + '.jpg';
  const avifFilename = slug + '.avif';
  const webpFilename = slug + '.webp';

  const card = `        <article class="article-card has-thumb reveal" data-cat="${cat}">
          <div class="card-thumb"><picture><source srcset="/images/og/${avifFilename}" type="image/avif"><source srcset="/images/og/${webpFilename}" type="image/webp"><img loading="lazy" decoding="async" src="/images/og/${imgFilename}" alt="${title}" width="1200" height="630"></picture><h3 class="thumb-title"><a href="articles/${file}">${title}</a></h3></div>
          <div class="card-body">
            <span class="card-category cat-${cat}">${label}</span>
            <p class="card-excerpt">${desc}</p>
            <div class="card-meta"><span>⏱ ${readTime} דקות · ${formatDate(dateStr)}</span></div>
          </div>
        </article>`;

  cards.push(card);
}

console.log(`Generated ${cards.length} cards`);

// Insert into index.html — first 30 inline, rest go to archive
let indexHtml = fs.readFileSync('index.html', 'utf8');

const inlineCards = cards.slice(0, 30).join('\n');

// Replace the <!-- NEW_ARTICLES_HERE --> marker area
indexHtml = indexHtml.replace(
  /<!-- NEW_ARTICLES_HERE -->[\s\S]*?<!-- FEATURED -->/,
  `<!-- NEW_ARTICLES_HERE -->\n${inlineCards}\n\n        <!-- FEATURED -->`
);

fs.writeFileSync('index.html', indexHtml);
console.log(`Injected 30 cards into index.html`);

// Create archive.html with ALL cards
const archiveCards = cards.join('\n');
const archiveHtml = `<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <script>(function(){var t=localStorage.getItem('binah-theme');if(t==='light')document.documentElement.setAttribute('data-theme','light');})();</script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="ארכיון כל המאמרים של בינה — מדריכים, השוואות וחדשות AI בעברית">
  <title>ארכיון מאמרים | בינה — AI בעברית</title>
  <link rel="preload" href="styles.min.css" as="style" onload="this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="styles.min.css"></noscript>
  <link rel="canonical" href="https://binah.co.il/archive.html">
  <link rel="alternate" type="application/rss+xml" title="בינה RSS" href="/feed.xml">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-MG65DD6GYJ"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-MG65DD6GYJ');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9475752562192165" crossorigin="anonymous"></script>
</head>
<body>
<header>
  <div class="container">
    <div class="nav-inner">
      <a href="index.html" class="logo">בינה ✦</a>
      <nav id="main-nav">
        <a href="index.html">ראשי</a>
        <a href="index.html#articles">מאמרים</a>
        <a href="guides.html">מדריכים</a>
        <a href="tools.html">כלים</a>
        <a href="business.html">AI לעסקים</a>
        <a href="ai-products.html">מוצרי AI</a>
      </nav>
    </div>
  </div>
</header>
<main>
  <div class="container" style="padding:40px 0 80px">
    <h1 style="font-size:2rem;font-weight:900;margin-bottom:24px">ארכיון מאמרים</h1>
    <p style="color:var(--text-muted);margin-bottom:32px">כל ${cards.length} המאמרים שפורסמו באתר בינה, מהחדש לישן.</p>
    <div class="articles-grid">
${archiveCards}
    </div>
  </div>
</main>
<footer style="text-align:center;padding:24px;color:var(--text-muted);font-size:0.85rem;border-top:1px solid var(--border)">
  <p>© 2025-2026 בינה — AI בעברית. כל הזכויות שמורות.</p>
</footer>
</body>
</html>`;

fs.writeFileSync('archive.html', archiveHtml);
console.log('Created archive.html');

// Also create data/articles-archive.json for lazy loading
const archiveData = files.map(file => {
  const slug = file.replace('.html', '');
  const html = fs.readFileSync(`${ARTICLES_DIR}/${file}`, 'utf8');
  const title = extractTitle(html);
  const desc = extractMeta(html, 'description');
  const dateMatch = file.match(/^(\d{4}-\d{2}-\d{2})/);
  const { cat } = getCategory(slug);
  return { slug, title, excerpt: desc, img: `/images/og/${slug}.jpg`, cat, date: dateMatch?.[1] || '' };
});

fs.mkdirSync('data', { recursive: true });
fs.writeFileSync('data/articles-archive.json', JSON.stringify(archiveData, null, 2));
console.log('Created data/articles-archive.json');
