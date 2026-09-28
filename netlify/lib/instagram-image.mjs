import sharp from 'sharp';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// A gallery tile is at most ~350 CSS pixels wide. 800 pixels covers high-density screens.
export async function optimizeInstagramImage(input) {
  for (const [pixels, quality] of [[800, 68], [720, 60], [640, 52], [480, 44], [320, 35]]) {
    const image = await sharp(input)
      .rotate()
      .resize({ width: pixels, height: pixels, fit: 'inside', withoutEnlargement: true })
      .webp({ quality, effort: 5 })
      .toBuffer();
    if (image.length <= 180_000) return image;
  }
  throw new Error('Instagram image exceeds its size budget');
}

// The local Python build pipes downloaded images through the same encoder.
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  process.stdout.write(await optimizeInstagramImage(Buffer.concat(chunks)));
}
