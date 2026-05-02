#!/usr/bin/env node
/**
 * Consolidate duplicate articles by topic.
 * For each topic with 2+ articles, keeps the newest (by date) and longest (by file size) as canonical.
 * Deletes duplicates, adds 301 redirects, updates sitemap and index.html.
 */

import fs from 'fs';
import path from 'path';

const ARTICLES_DIR = 'articles';
const NETLIFY_TOML = 'netlify.toml';
const SITEMAP = 'sitemap.xml';
const INDEX = 'index.html';

// Non-date-prefixed articles (manually edited) - never touch
const MANUAL_ARTICLES = new Set(fs.readdirSync(ARTICLES_DIR)
  .filter(f => f.endsWith('.html') && !f.match(/^\d{4}-\d{2}-\d{2}-/)));

console.log(`Manual articles (untouched): ${MANUAL_ARTICLES.size}`);

// 1. Group date-prefixed articles by topic
const dateArticles = fs.readdirSync(ARTICLES_DIR)
  .filter(f => f.endsWith('.html') && f.match(/^\d{4}-\d{2}-\d{2}-/));

console.log(`Total date-prefixed articles: ${dateArticles.length}`);

const groups = {};
for (const file of dateArticles) {
  const match = file.match(/^(\d{4}-\d{2}-\d{2})-(.+)\.html$/);
  if (!match) continue;
  const [, dateStr, topic] = match;
  if (!groups[topic]) groups[topic] = [];
  const filePath = path.join(ARTICLES_DIR, file);
  const stat = fs.statSync(filePath);
  groups[topic].push({ file, dateStr, topic, filePath, size: stat.size });
}

const uniqueTopics = Object.keys(groups).length;
const dupeTopics = Object.entries(groups).filter(([, v]) => v.length > 1);
console.log(`Unique topics: ${uniqueTopics}`);
console.log(`Topics with duplicates: ${dupeTopics.length}`);

// 2. For each group, pick canonical (newest date, then largest file)
const toDelete = [];
const redirects = [];

for (const [topic, articles] of Object.entries(groups)) {
  if (articles.length === 1) continue;

  // Sort: newest date first, then largest size
  articles.sort((a, b) => {
    const dateCmp = b.dateStr.localeCompare(a.dateStr);
    if (dateCmp !== 0) return dateCmp;
    return b.size - a.size;
  });

  const canonical = articles[0];
  console.log(`\nTopic: ${topic} (${articles.length} articles)`);
  console.log(`  Canonical: ${canonical.file} (${canonical.size} bytes)`);

  for (let i = 1; i < articles.length; i++) {
    const dupe = articles[i];
    console.log(`  Delete: ${dupe.file}`);
    toDelete.push(dupe);

    // Redirect: both with and without .html
    const fromSlug = dupe.file.replace('.html', '');
    const toSlug = canonical.file.replace('.html', '');
    redirects.push({
      from: `/articles/${fromSlug}`,
      to: `/articles/${toSlug}`,
    });
  }
}

console.log(`\nArticles to delete: ${toDelete.length}`);
console.log(`Redirects to add: ${redirects.length}`);

// 3. Delete duplicate files
for (const dupe of toDelete) {
  fs.unlinkSync(dupe.filePath);
}
console.log(`Deleted ${toDelete.length} duplicate files.`);

// 4. Update netlify.toml - remove old .html→non-.html redirects for deleted files, add 301 topic redirects
let toml = fs.readFileSync(NETLIFY_TOML, 'utf8');

// Remove existing redirects for deleted files (both .html strip and any other)
const deletedSlugs = new Set(toDelete.map(d => d.file.replace('.html', '')));

// Parse toml into sections: split by [[redirects]]
const tomlParts = toml.split(/(?=\[\[redirects\]\])/);
const headerPart = tomlParts[0]; // everything before first [[redirects]]
const redirectParts = tomlParts.slice(1);

// Filter out redirects that reference deleted articles
const keptRedirects = redirectParts.filter(part => {
  // Check if this redirect references a deleted slug
  for (const slug of deletedSlugs) {
    if (part.includes(`/articles/${slug}`)) {
      // Only remove if the "from" is the deleted article
      const fromMatch = part.match(/from\s*=\s*"([^"]+)"/);
      if (fromMatch && fromMatch[1].includes(slug)) {
        return false; // Remove this redirect
      }
    }
  }
  return true;
});

// Build new redirects for consolidated topics
const newRedirectsToml = redirects.map(r => `
[[redirects]]
  from = "${r.from}"
  to = "${r.to}"
  status = 301
  force = true

[[redirects]]
  from = "${r.from}.html"
  to = "${r.to}"
  status = 301
  force = true`).join('\n');

// Reassemble toml
toml = headerPart + keptRedirects.join('') + '\n\n# Consolidated duplicate topic redirects\n' + newRedirectsToml + '\n';
fs.writeFileSync(NETLIFY_TOML, toml);
console.log('Updated netlify.toml with consolidation redirects.');

// 5. Update sitemap.xml - remove deleted article URLs
let sitemap = fs.readFileSync(SITEMAP, 'utf8');
let removedFromSitemap = 0;
for (const slug of deletedSlugs) {
  // Match <url>...</url> blocks containing this slug
  const re = new RegExp(`\\s*<url>[\\s\\S]*?${slug.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\s\\S]*?</url>`, 'g');
  const before = sitemap.length;
  sitemap = sitemap.replace(re, '');
  if (sitemap.length < before) removedFromSitemap++;
}
fs.writeFileSync(SITEMAP, sitemap);
console.log(`Removed ${removedFromSitemap} entries from sitemap.xml.`);

// 6. Update index.html - remove cards for deleted articles
let indexHtml = fs.readFileSync(INDEX, 'utf8');
let removedCards = 0;
for (const slug of deletedSlugs) {
  // Match <article class="article-card ...>...</article> containing this slug
  const escapedSlug = slug.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(`\\s*<article class="article-card[^>]*>[\\s\\S]*?${escapedSlug}[\\s\\S]*?</article>`, 'g');
  const before = indexHtml.length;
  indexHtml = indexHtml.replace(re, '');
  if (indexHtml.length < before) removedCards++;
}
fs.writeFileSync(INDEX, indexHtml);
console.log(`Removed ${removedCards} cards from index.html.`);

// 7. Summary
const remaining = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html') && f.match(/^\d{4}-\d{2}-\d{2}-/));
const remainingTopics = new Set(remaining.map(f => f.replace(/^\d{4}-\d{2}-\d{2}-/, '').replace('.html', '')));
console.log(`\n=== SUMMARY ===`);
console.log(`Remaining date-prefixed articles: ${remaining.length}`);
console.log(`Unique topics: ${remainingTopics.size}`);
console.log(`One-to-one: ${remaining.length === remainingTopics.size ? 'YES' : 'NO'}`);
