#!/usr/bin/env node
/**
 * Add internal links (3-5 per article) + author box to auto-generated articles.
 * Uses keyword matching between article titles to find related articles.
 */
import fs from 'fs';
import path from 'path';

const ARTICLES_DIR = 'articles';

// Manual articles - don't modify
const MANUAL_SLUGS = new Set([
  'claude-vs-gpt4o', 'perplexity-ai', 'ollama-guide', 'gpt5-launch',
  'vibe-coding', 'midjourney-beginners', 'sora-openai', 'ai-jobs-2025',
  'ai-small-business', 'ai-video-tools', 'prompt-engineering', 'chatgpt-10-uses',
  'gemini-2025', 'deepseek-r2'
]);

const AUTHOR_BOX = `
<div class="author-box" style="background:var(--card-bg,#1a1a2e);border:1px solid var(--border,#2a2a4a);border-radius:12px;padding:20px 24px;margin:40px 0 0;display:flex;gap:16px;align-items:flex-start">
  <img loading="lazy" decoding="async" src="../images/yaniv-sorani.jpg" alt="יניב סוראני" width="64" height="64" style="border-radius:50%;flex-shrink:0;object-fit:cover" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2264%22 height=%2264%22 viewBox=%220 0 64 64%22%3E%3Ccircle cx=%2232%22 cy=%2232%22 r=%2232%22 fill=%22%237b6cf6%22/%3E%3Ctext x=%2250%25%22 y=%2255%25%22 text-anchor=%22middle%22 fill=%22white%22 font-size=%2228%22%3E&#129504;%3C/text%3E%3C/svg%3E'">
  <div>
    <p style="margin:0 0 4px;font-weight:700;font-size:0.95rem">יניב סוראני</p>
    <p style="margin:0 0 8px;font-size:0.82rem;color:var(--text-muted,#888)">מפתח ומומחה כלי בינה מלאכותית | מייסד בינה.co.il</p>
    <p style="margin:0;font-size:0.85rem;line-height:1.6">20+ שנות ניסיון בטכנולוגיה. בוחן ומשתמש בכלי AI מדי יום. כל תוכן באתר נכתב, נבדק ועורך ידנית.</p>
  </div>
</div>`;

// Build article index: slug -> { title, keywords }
const files = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html'));
const articleIndex = [];

for (const file of files) {
  const slug = file.replace('.html', '');
  const html = fs.readFileSync(path.join(ARTICLES_DIR, file), 'utf8');
  const titleM = html.match(/<title>([^<]+)<\/title>/i);
  const title = titleM ? titleM[1].replace(/\s*\|\s*בינה\s*$/, '').trim() : '';

  // Extract keywords from title (Hebrew + English words > 2 chars)
  const keywords = title.toLowerCase()
    .replace(/[^\w\s\u0590-\u05FF-]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2);

  articleIndex.push({ file, slug, title, keywords, url: `/articles/${slug}` });
}

// Find related articles by keyword overlap
function findRelated(currentSlug, count = 5) {
  const current = articleIndex.find(a => a.slug === currentSlug);
  if (!current) return [];

  const scored = articleIndex
    .filter(a => a.slug !== currentSlug)
    .map(a => {
      const overlap = current.keywords.filter(k => a.keywords.includes(k)).length;
      return { ...a, score: overlap };
    })
    .filter(a => a.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, count);

  return scored;
}

let addedLinks = 0;
let addedAuthor = 0;

for (const file of files) {
  const slug = file.replace('.html', '');

  // Skip manual articles
  if (MANUAL_SLUGS.has(slug)) continue;
  // Skip non-date-prefixed that aren't in manual list (product-, biz-, crazy- etc.)
  if (!slug.match(/^\d{4}-\d{2}-\d{2}-/)) continue;

  const filePath = path.join(ARTICLES_DIR, file);
  let html = fs.readFileSync(filePath, 'utf8');
  let modified = false;

  // 1. Add internal links if < 3 exist
  const existingLinks = (html.match(/href="\/articles\//g) || []).length;
  if (existingLinks < 3) {
    const related = findRelated(slug, 5);
    if (related.length >= 3) {
      // Build a "related articles" section
      const relatedHtml = `
<div class="related-inline" style="background:var(--bg-card,#12121f);border:1px solid var(--border,#1e1e32);border-radius:12px;padding:20px 24px;margin:32px 0">
  <h3 style="margin:0 0 12px;font-size:1.05rem;color:var(--heading,#f8fafc)">מאמרים קשורים</h3>
  <ul style="margin:0;padding:0 20px;display:flex;flex-direction:column;gap:8px">
${related.map(r => `    <li><a href="${r.url}" style="color:var(--accent,#06b6d4)">${r.title}</a></li>`).join('\n')}
  </ul>
</div>`;

      // Insert before </main> or before author-box
      if (html.includes('</main>')) {
        html = html.replace('</main>', `${relatedHtml}\n</main>`);
      } else if (html.includes('</article>')) {
        html = html.replace(/<\/article>(?![\s\S]*<\/article>)/, `${relatedHtml}\n</article>`);
      }
      addedLinks++;
      modified = true;
    }
  }

  // 2. Add author box if missing
  if (!html.includes('author-box')) {
    if (html.includes('</main>')) {
      html = html.replace('</main>', `${AUTHOR_BOX}\n</main>`);
    }
    addedAuthor++;
    modified = true;
  }

  if (modified) {
    fs.writeFileSync(filePath, html);
  }
}

console.log(`Added internal links sections: ${addedLinks}`);
console.log(`Added author boxes: ${addedAuthor}`);

// Verify internal links
let low = 0;
const sampled = files.filter(f => f.match(/^\d{4}-/)).slice(0, 10);
for (const f of sampled) {
  const html = fs.readFileSync(path.join(ARTICLES_DIR, f), 'utf8');
  const links = (html.match(/href="\/articles\//g) || []).length;
  if (links < 3) low++;
}
console.log(`Articles with <3 internal links (sample of 10): ${low}`);
