#!/usr/bin/env node
import sharp from 'sharp';

const sizes = [16, 32, 192, 512];
for (const s of sizes) {
  const out = s <= 32 ? `favicon-${s}x${s}.png` : `android-chrome-${s}x${s}.png`;
  await sharp('favicon.svg').resize(s, s).png().toFile(out);
  console.log(`Generated ${out}`);
}
