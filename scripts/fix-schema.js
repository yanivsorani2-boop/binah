#!/usr/bin/env node
/**
 * Fix Schema issues in all articles:
 * 1. Remove wordCount from BreadcrumbList
 * 2. Add/update BlogPosting JSON-LD
 * 3. Remove FAQ placeholder spam (no API key = delete FAQPage entirely)
 */

import fs from 'fs';
import path from 'path';

const ARTICLES_DIR = 'articles';

// Manual articles to not touch
const MANUAL_SLUGS = [
  'claude-vs-gpt4o', 'perplexity-ai', 'ollama-guide', 'gpt5-launch',
  'vibe-coding', 'midjourney-beginners', 'sora-openai', 'ai-jobs-2025',
  'ai-small-business', 'ai-video-tools', 'prompt-engineering', 'chatgpt-10-uses',
  'gemini-2025', 'deepseek-r2'
];

// articleSection mapping
function getSection(slug) {
  if (slug.includes('compare-') || slug.includes('compare_')) return 'comparisons';
  if (slug.includes('guide-') || slug.includes('guide_')) return 'guides';
  if (slug.includes('tools-') || slug.includes('tool-')) return 'tools';
  if (slug.includes('business-') || slug.includes('biz-')) return 'business';
  if (slug.includes('crazy-')) return 'crazy';
  if (slug.includes('product-')) return 'products';
  if (slug.includes('hebrew-')) return 'hebrew';
  if (slug.includes('weekly-')) return 'news';
  return 'articles';
}

function getSectionHe(section) {
  const map = {
    comparisons: 'comparisons',
    guides: 'guides',
    tools: 'tools',
    business: 'AI business',
    crazy: 'AI crazy',
    products: 'AI products',
    hebrew: 'hebrew',
    news: 'news',
    articles: 'articles'
  };
  return map[section] || 'articles';
}

function countWords(html) {
  // Remove scripts, styles, tags
  let text = html.replace(/<script[\s\S]*?<\/script>/gi, '');
  text = text.replace(/<style[\s\S]*?<\/style>/gi, '');
  text = text.replace(/<[^>]+>/g, ' ');
  text = text.replace(/&[a-z]+;/gi, ' ');
  text = text.replace(/\s+/g, ' ').trim();
  return text.split(/\s+/).filter(w => w.length > 0).length;
}

function extractMeta(html, attr) {
  const re = new RegExp(`<meta[^>]*(?:name|property)="${attr}"[^>]*content="([^"]*)"`, 'i');
  const m = html.match(re);
  if (m) return m[1];
  // Try reversed order
  const re2 = new RegExp(`<meta[^>]*content="([^"]*)"[^>]*(?:name|property)="${attr}"`, 'i');
  const m2 = html.match(re2);
  return m2 ? m2[1] : '';
}

function extractTitle(html) {
  const m = html.match(/<title>([^<]+)<\/title>/i);
  return m ? m[1].replace(/\s*\|\s*בינה\s*$/, '').trim() : '';
}

function extractCanonical(html) {
  const m = html.match(/<link[^>]*rel="canonical"[^>]*href="([^"]+)"/i);
  return m ? m[1] : '';
}

function extractOgImage(html) {
  return extractMeta(html, 'og:image');
}

function extractDateFromSlug(filename) {
  const m = filename.match(/^(\d{4}-\d{2}-\d{2})/);
  return m ? m[1] : null;
}

const files = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html'));
let fixedBreadcrumb = 0, addedBlogPosting = 0, removedFaq = 0;

for (const file of files) {
  const slug = file.replace('.html', '');

  // Skip manual articles
  if (MANUAL_SLUGS.some(s => slug === s)) continue;

  const filePath = path.join(ARTICLES_DIR, file);
  let html = fs.readFileSync(filePath, 'utf8');
  let modified = false;

  // 1. Fix BreadcrumbList — remove wordCount
  const breadcrumbRegex = /(<script[^>]*type="application\/ld\+json"[^>]*>)\s*(\{[\s\S]*?"@type"\s*:\s*"BreadcrumbList"[\s\S]*?\})\s*(<\/script>)/g;
  let match;
  while ((match = breadcrumbRegex.exec(html)) !== null) {
    try {
      const jsonStr = match[2];
      const obj = JSON.parse(jsonStr);
      if (obj['@type'] === 'BreadcrumbList' && 'wordCount' in obj) {
        delete obj.wordCount;
        const newJson = JSON.stringify(obj, null, 2);
        html = html.replace(match[0], `${match[1]}\n${newJson}\n${match[3]}`);
        fixedBreadcrumb++;
        modified = true;
      }
    } catch (e) {
      // Try to remove wordCount with regex if JSON parse fails
      if (match[2].includes('"wordCount"')) {
        const fixed = match[2].replace(/,?\s*"wordCount"\s*:\s*\d+\s*,?/g, ',').replace(/,\s*,/g, ',').replace(/,\s*\}/g, '}').replace(/\{\s*,/g, '{');
        html = html.replace(match[0], `${match[1]}\n${fixed}\n${match[3]}`);
        fixedBreadcrumb++;
        modified = true;
      }
    }
  }

  // 2. Remove FAQ placeholder spam
  const faqRegex = /<script[^>]*type="application\/ld\+json"[^>]*>\s*\{[\s\S]*?"@type"\s*:\s*"FAQPage"[\s\S]*?\}\s*<\/script>/g;
  if (html.match(faqRegex)) {
    // Check if answers contain placeholder text
    if (html.includes('קראו את המאמר המלא') || html.includes('ראו פירוט נוסף')) {
      html = html.replace(faqRegex, '');
      removedFaq++;
      modified = true;
    }
  }

  // 3. Add BlogPosting schema if missing
  if (!html.includes('"@type":"BlogPosting"') && !html.includes('"@type": "BlogPosting"') && !html.includes('"@type" : "BlogPosting"')) {
    const title = extractTitle(html);
    const description = extractMeta(html, 'description');
    const canonical = extractCanonical(html);
    const ogImage = extractOgImage(html);
    const datePublished = extractDateFromSlug(file) || '2026-01-01';
    const dateModified = new Date().toISOString().split('T')[0];

    // Count words in main/article content
    const mainMatch = html.match(/<(?:main|article)[^>]*>([\s\S]*?)<\/(?:main|article)>/i);
    const wordCount = mainMatch ? countWords(mainMatch[1]) : countWords(html);

    const section = getSection(slug);
    const sectionHe = getSectionHe(section);

    // Extract 3-5 keywords from title
    const keywords = title.replace(/[^\w\s\u0590-\u05FF]/g, ' ').split(/\s+/).filter(w => w.length > 2).slice(0, 5).join(', ');

    const blogPosting = {
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": title,
      "description": description,
      "url": canonical,
      "mainEntityOfPage": { "@type": "WebPage", "@id": canonical },
      "image": { "@type": "ImageObject", "url": ogImage, "width": 1200, "height": 630 },
      "inLanguage": "he",
      "datePublished": datePublished,
      "dateModified": dateModified,
      "wordCount": wordCount,
      "articleSection": sectionHe,
      "keywords": keywords,
      "author": { "@type": "Person", "name": "\u05D9\u05E0\u05D9\u05D1 \u05E1\u05D5\u05E8\u05E0\u05D9", "url": "https://binah.co.il/about" },
      "publisher": {
        "@type": "Organization",
        "name": "\u05D1\u05D9\u05E0\u05D4",
        "url": "https://binah.co.il",
        "logo": { "@type": "ImageObject", "url": "https://binah.co.il/images/logo.svg", "width": 512, "height": 512 }
      }
    };

    const jsonLd = `<script type="application/ld+json">\n${JSON.stringify(blogPosting, null, 2)}\n</script>`;

    // Insert before </head>
    html = html.replace('</head>', `${jsonLd}\n</head>`);
    addedBlogPosting++;
    modified = true;
  }

  if (modified) {
    fs.writeFileSync(filePath, html);
  }
}

console.log(`Fixed BreadcrumbList (removed wordCount): ${fixedBreadcrumb}`);
console.log(`Added BlogPosting schema: ${addedBlogPosting}`);
console.log(`Removed placeholder FAQ: ${removedFaq}`);

// Verify
const allArticles = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html'));
let missingBP = 0;
let badBreadcrumb = 0;
let badFaq = 0;

for (const file of allArticles) {
  const html = fs.readFileSync(path.join(ARTICLES_DIR, file), 'utf8');
  if (!html.includes('"BlogPosting"')) missingBP++;

  // Check wordCount in BreadcrumbList
  const schemas = html.matchAll(/<script[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/g);
  for (const m of schemas) {
    try {
      const obj = JSON.parse(m[1]);
      if (obj['@type'] === 'BreadcrumbList' && 'wordCount' in obj) badBreadcrumb++;
    } catch {}
  }

  if (html.includes('קראו את המאמר המלא')) badFaq++;
}

console.log(`\n=== VERIFICATION ===`);
console.log(`Articles missing BlogPosting: ${missingBP} (target: 0)`);
console.log(`BreadcrumbList with wordCount: ${badBreadcrumb} (target: 0)`);
console.log(`FAQ with placeholder: ${badFaq} (target: 0)`);
