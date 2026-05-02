#!/usr/bin/env node
import fs from 'fs';

const ARTICLES_DIR = 'articles';
const MANUAL_SLUGS = new Set([
  'claude-vs-gpt4o', 'perplexity-ai', 'ollama-guide', 'gpt5-launch',
  'vibe-coding', 'midjourney-beginners', 'sora-openai', 'ai-jobs-2025',
  'ai-small-business', 'ai-video-tools', 'prompt-engineering', 'chatgpt-10-uses',
  'gemini-2025', 'deepseek-r2'
]);

const sectionMap = {
  'comparisons': 'השוואות',
  'guides': 'מדריכים',
  'tools': 'כלים',
  'business': 'AI לעסקים',
  'AI business': 'AI לעסקים',
  'crazy': 'AI מטורף',
  'AI crazy': 'AI מטורף',
  'products': 'מוצרי AI',
  'AI products': 'מוצרי AI',
  'hebrew': 'עברית',
  'news': 'חדשות שבועיות',
  'articles': 'מאמרים'
};

const files = fs.readdirSync(ARTICLES_DIR).filter(f => f.endsWith('.html'));
let fixed = 0;

for (const file of files) {
  const slug = file.replace('.html', '');
  if (MANUAL_SLUGS.has(slug)) continue;
  if (!slug.match(/^\d{4}-\d{2}-\d{2}-/)) continue;

  const filePath = `${ARTICLES_DIR}/${file}`;
  let html = fs.readFileSync(filePath, 'utf8');

  const match = html.match(/"articleSection":\s*"([^"]+)"/);
  if (match) {
    const current = match[1];
    const hebrew = sectionMap[current];
    if (hebrew && hebrew !== current) {
      html = html.replace(`"articleSection": "${current}"`, `"articleSection": "${hebrew}"`);
      fs.writeFileSync(filePath, html);
      fixed++;
    }
  }
}

console.log(`Fixed ${fixed} articleSection values to Hebrew`);

// Verify
const engCount = fs.readdirSync(ARTICLES_DIR)
  .filter(f => f.endsWith('.html') && f.match(/^\d{4}-/))
  .filter(f => {
    const html = fs.readFileSync(`${ARTICLES_DIR}/${f}`, 'utf8');
    const m = html.match(/"articleSection":\s*"([^"]+)"/);
    return m && Object.keys(sectionMap).includes(m[1]);
  }).length;
console.log(`Articles with English articleSection remaining: ${engCount}`);
