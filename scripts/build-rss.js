#!/usr/bin/env node
import fs from 'fs';

const articles = fs.readdirSync('articles').filter(f => f.endsWith('.html'));
const items = articles.map(f => {
  const html = fs.readFileSync(`articles/${f}`, 'utf8');
  const titleM = html.match(/<title>([^<]+)<\/title>/i);
  const title = titleM ? titleM[1].replace(/\s*\|\s*בינה\s*$/, '').trim() : '';
  const descM = html.match(/<meta[^>]*name="description"[^>]*content="([^"]*)"/i);
  const desc = descM ? descM[1] : '';
  const canoM = html.match(/<link[^>]*rel="canonical"[^>]*href="([^"]+)"/i);
  const cano = canoM ? canoM[1] : '';
  const dateMatch = f.match(/^(\d{4}-\d{2}-\d{2})/);
  const date = dateMatch ? new Date(dateMatch[1]) : new Date(fs.statSync(`articles/${f}`).mtime);
  return { title, desc, cano, date };
}).filter(i => i.title && i.cano)
  .sort((a, b) => b.date - a.date).slice(0, 50);

const escape = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const rfc822 = d => d.toUTCString();

const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>בינה — AI בעברית</title>
<link>https://binah.co.il</link>
<description>מדריכים, השוואות וחדשות AI בעברית</description>
<language>he-IL</language>
<atom:link href="https://binah.co.il/feed.xml" rel="self" type="application/rss+xml"/>
<lastBuildDate>${rfc822(new Date())}</lastBuildDate>
${items.map(i => `<item>
<title>${escape(i.title)}</title>
<link>${i.cano}</link>
<guid isPermaLink="true">${i.cano}</guid>
<description>${escape(i.desc || '')}</description>
<pubDate>${rfc822(i.date)}</pubDate>
</item>`).join('\n')}
</channel></rss>`;

fs.writeFileSync('feed.xml', rss);
console.log('Wrote feed.xml with', items.length, 'items');
