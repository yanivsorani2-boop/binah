#!/usr/bin/env node
/**
 * fix-external-rel.js — מוסיף rel="nofollow"/"sponsored" לכל external links
 * הרץ מה-root של הפרויקט: node scripts/fix-external-rel.js
 */
'use strict';

const fs = require('fs');
const path = require('path');

const AFFILIATE_DOMAINS = new Set([
  'claude.ai', 'openai.com', 'anthropic.com', 'perplexity.ai',
  'deepseek.ai', 'mistral.ai', 'ollama.com', 'midjourney.com',
  'runwayml.com', 'suno.com', 'cursor.sh',
]);

function getDomain(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch { return null; }
}

function processFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  let modified = false;

  const newContent = content.replace(/<a(\s[^>]*)?>/gi, (match, attrs) => {
    if (!attrs) return match;

    const hrefMatch = attrs.match(/href="(https?:\/\/[^"]+)"/i);
    if (!hrefMatch) return match;

    const domain = getDomain(hrefMatch[1]);
    if (!domain || domain === 'binah.co.il') return match;

    const relVal = AFFILIATE_DOMAINS.has(domain)
      ? 'sponsored noopener nofollow'
      : 'noopener nofollow';

    let a = attrs;

    // Update or add rel
    if (/\brel="/i.test(a)) {
      a = a.replace(/rel="[^"]*"/i, `rel="${relVal}"`);
    } else {
      a = a + ` rel="${relVal}"`;
    }

    // Add target="_blank" if missing
    if (!/\btarget="/i.test(a)) {
      a = a + ' target="_blank"';
    }

    modified = true;
    return `<a${a}>`;
  });

  if (modified) {
    fs.writeFileSync(filePath, newContent, 'utf8');
    return true;
  }
  return false;
}

const ROOT = process.cwd();
const DIRS = ['articles', 'guides'];
let total = 0, changed = 0;

for (const dir of DIRS) {
  const dirPath = path.join(ROOT, dir);
  if (!fs.existsSync(dirPath)) continue;
  const files = fs.readdirSync(dirPath).sort().filter(f => f.endsWith('.html'));
  for (const fname of files) {
    total++;
    if (processFile(path.join(dirPath, fname))) changed++;
  }
}

console.log(`Processed ${total} files, modified ${changed}`);
