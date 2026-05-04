#!/usr/bin/env node
/**
 * Ensure every date-prefixed article in filesystem is in sitemap.xml
 * Remove sitemap entries for articles that don't exist on filesystem.
 */
import fs from 'fs';

const ARTICLES_DIR = 'articles';
const SITEMAP_FILE = 'sitemap.xml';

// Get all date-prefixed article slugs from filesystem
const fsArticles = fs.readdirSync(ARTICLES_DIR)
  .filter(f => f.endsWith('.html') && f.match(/^\d{4}-\d{2}-\d{2}-/))
  .map(f => f.replace('.html', ''));

// Read sitemap
let sitemap = fs.readFileSync(SITEMAP_FILE, 'utf8');

// Find slugs already in sitemap
const inSitemap = new Set();
const sitemapRegex = /articles\/(2026-[^<\s]+)/g;
let m;
while ((m = sitemapRegex.exec(sitemap)) !== null) {
  inSitemap.add(m[1]);
}

console.log(`Filesystem articles: ${fsArticles.length}`);
console.log(`Already in sitemap: ${inSitemap.size}`);

// Add missing articles to sitemap
let added = 0;
for (const slug of fsArticles) {
  if (inSitemap.has(slug)) continue;

  const dateMatch = slug.match(/^(\d{4}-\d{2}-\d{2})/);
  const date = dateMatch ? dateMatch[1] : '2026-01-01';

  const entry = `  <url>
    <loc>https://binah.co.il/articles/${slug}</loc>
    <lastmod>${date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>\n`;

  sitemap = sitemap.replace('</urlset>', entry + '</urlset>');
  added++;
}

fs.writeFileSync(SITEMAP_FILE, sitemap);
console.log(`Added ${added} articles to sitemap`);

// Verify
const finalCount = (sitemap.match(/articles\/2026-/g) || []).length;
console.log(`Total 2026 articles in sitemap now: ${finalCount}`);
