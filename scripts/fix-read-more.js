#!/usr/bin/env node
/**
 * Replace "קרא עוד ←" with card-level link wrapper.
 * For index.html and hub pages.
 */
import fs from 'fs';

const files = [
  'index.html',
  'comparisons.html',
  'tools.html', 'tools-hub.html',
  'guides.html', 'guides-hub.html',
  'business.html', 'business-hub.html',
  'news-hub.html', 'weekly-news.html',
  'ai-products.html', 'ai-crazy.html'
].filter(f => fs.existsSync(f));

let totalFixed = 0;

for (const file of files) {
  let html = fs.readFileSync(file, 'utf8');
  const before = (html.match(/קרא עוד/g) || []).length;
  if (before === 0) continue;

  // Remove the read-more link, keep the meta span
  html = html.replace(/<a[^>]*class="read-more"[^>]*>קרא עוד ←<\/a>/g, '');

  // For cards with thumb-title links, the card is already clickable via the title
  // Just add CSS to make the whole card clickable via the existing title link

  fs.writeFileSync(file, html);
  const after = (html.match(/קרא עוד/g) || []).length;
  console.log(`${file}: ${before} → ${after} "קרא עוד" links`);
  totalFixed += (before - after);
}

console.log(`Total fixed: ${totalFixed}`);
