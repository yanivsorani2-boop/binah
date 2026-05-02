#!/usr/bin/env node
import fs from 'fs';

const ARTICLES_DIR = 'articles';

function countWords(html) {
  let text = html.replace(/<script[\s\S]*?<\/script>/gi, '');
  text = text.replace(/<style[\s\S]*?<\/style>/gi, '');
  text = text.replace(/<[^>]+>/g, ' ');
  text = text.replace(/&[a-z]+;/gi, ' ');
  text = text.replace(/\s+/g, ' ').trim();
  return text.split(/\s+/).filter(w => w.length > 0).length;
}

const files = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html') && f.match(/^\d{4}-/));
let updated = 0;
let below1500 = 0;

for (const file of files) {
  const filePath = `${ARTICLES_DIR}/${file}`;
  let html = fs.readFileSync(filePath, 'utf8');

  // Extract main/article content for word count
  const mainMatch = html.match(/<(?:main|article)[^>]*>([\s\S]*?)<\/(?:main|article)>/i);
  const wc = mainMatch ? countWords(mainMatch[1]) : countWords(html);

  // Update wordCount in BlogPosting
  const oldMatch = html.match(/"wordCount":\s*(\d+)/);
  if (oldMatch && parseInt(oldMatch[1]) !== wc) {
    html = html.replace(/"wordCount":\s*\d+/, `"wordCount": ${wc}`);
    fs.writeFileSync(filePath, html);
    updated++;
  }

  if (wc < 1500) below1500++;
}

console.log(`Updated wordCount in ${updated} articles`);
console.log(`Articles below 1500 words: ${below1500}`);
