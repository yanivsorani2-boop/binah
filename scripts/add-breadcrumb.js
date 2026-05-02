#!/usr/bin/env node
import fs from 'fs';

const ARTICLES_DIR = 'articles';

function extractTitle(html) {
  const m = html.match(/<title>([^<]+)<\/title>/i);
  return m ? m[1].replace(/\s*\|\s*בינה\s*$/, '').trim() : '';
}

function extractCanonical(html) {
  const m = html.match(/<link[^>]*rel="canonical"[^>]*href="([^"]+)"/i);
  return m ? m[1] : '';
}

const files = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html') && f.match(/^\d{4}-/));
let added = 0;

for (const file of files) {
  const filePath = `${ARTICLES_DIR}/${file}`;
  let html = fs.readFileSync(filePath, 'utf8');

  if (html.includes('BreadcrumbList')) continue;

  const title = extractTitle(html);
  const canonical = extractCanonical(html);

  const breadcrumb = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "בינה", "item": "https://binah.co.il/" },
      { "@type": "ListItem", "position": 2, "name": "מאמרים", "item": "https://binah.co.il/articles/" },
      { "@type": "ListItem", "position": 3, "name": title, "item": canonical }
    ]
  };

  const jsonLd = `<script type="application/ld+json">\n${JSON.stringify(breadcrumb, null, 2)}\n</script>`;

  html = html.replace('</head>', `${jsonLd}\n</head>`);
  fs.writeFileSync(filePath, html);
  added++;
}

console.log(`Added BreadcrumbList to ${added} articles`);

// Verify
const missing = fs.readdirSync(ARTICLES_DIR)
  .filter(f => f.endsWith('.html') && f.match(/^\d{4}-/))
  .filter(f => !fs.readFileSync(`${ARTICLES_DIR}/${f}`, 'utf8').includes('BreadcrumbList'))
  .length;
console.log(`Articles still missing BreadcrumbList: ${missing}`);
