#!/usr/bin/env node
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';

const dir = 'images/og';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.jpg'));
console.log(`Processing ${files.length} images...`);

let done = 0;
for (const f of files) {
  const input = path.join(dir, f);
  const webpOut = input.replace('.jpg', '.webp');
  const avifOut = input.replace('.jpg', '.avif');

  try {
    if (!fs.existsSync(webpOut)) {
      await sharp(input).webp({ quality: 85 }).toFile(webpOut);
    }
    if (!fs.existsSync(avifOut)) {
      await sharp(input).avif({ quality: 60 }).toFile(avifOut);
    }
    done++;
    if (done % 50 === 0) console.log(`  ${done}/${files.length}`);
  } catch (e) {
    console.error(`Error processing ${f}: ${e.message}`);
  }
}
console.log(`Done: ${done} images optimized`);
