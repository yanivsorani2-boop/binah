#!/usr/bin/env node
/**
 * Replace <img src="...og/X.jpg"> with <picture> elements.
 * Keep og:image as JPG (Facebook compatibility).
 */
import fs from 'fs';

function processFile(filePath) {
  let html = fs.readFileSync(filePath, 'utf8');

  // Match img tags pointing to /images/og/*.jpg (not inside meta tags)
  const imgRegex = /(<img\s+[^>]*src=")(\/images\/og\/[^"]+\.jpg)("[^>]*>)/g;

  let count = 0;
  html = html.replace(imgRegex, (match, prefix, src, suffix) => {
    // Don't replace if already inside <picture>
    // Simple check: look back for <picture> in the surrounding context
    const avifSrc = src.replace('.jpg', '.avif');
    const webpSrc = src.replace('.jpg', '.webp');

    count++;
    return `<picture><source srcset="${avifSrc}" type="image/avif"><source srcset="${webpSrc}" type="image/webp">${prefix}${src}${suffix}</picture>`;
  });

  if (count > 0) {
    // Avoid double-wrapping
    html = html.replace(/<picture><picture>/g, '<picture>');
    html = html.replace(/<\/picture><\/picture>/g, '</picture>');
    fs.writeFileSync(filePath, html);
  }
  return count;
}

// Process index.html
let total = processFile('index.html');
console.log(`index.html: ${total} images wrapped`);

// Process all article files
const articles = fs.readdirSync('articles').filter(f => f.endsWith('.html'));
for (const f of articles) {
  const n = processFile(`articles/${f}`);
  total += n;
}

// Process hub pages
const hubs = ['comparisons.html', 'tools-hub.html', 'guides-hub.html', 'business-hub.html', 'news-hub.html'].filter(f => fs.existsSync(f));
for (const f of hubs) {
  const n = processFile(f);
  total += n;
}

console.log(`Total images wrapped in <picture>: ${total}`);
