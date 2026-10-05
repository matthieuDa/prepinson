import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const languages = [
  ['en', 'Welcome to'],
  ['fr', 'Bienvenue à'],
  ['nl', 'Welkom bij'],
  ['de', 'Willkommen bei'],
  ['sv', 'Välkommen till'],
  ['lb', 'Wëllkomm zu'],
];
const gateway = await readFile(new URL('../dist/index.html', import.meta.url), 'utf8');
const config = await readFile(new URL('../netlify.toml', import.meta.url), 'utf8');
assert.doesNotMatch(config, /function\s*=\s*["']language-redirect["']/);
assert.match(gateway, /<body class="gateway">/);
assert.match(gateway, /<main>/);
assert.match(gateway, /Welcome to Prepinson\./);
for (const [lang, greeting] of languages) {
  assert.ok(gateway.includes(`href="/${lang}/"`), `${lang}: gateway link`);
  assert.ok(gateway.includes(`lang="${lang}"`), `${lang}: animated phrase`);
  assert.ok(gateway.includes(greeting), `${lang}: greeting`);
  const page = await readFile(new URL(`../dist/${lang}/index.html`, import.meta.url), 'utf8');
  assert.ok(page.includes(`<html lang="${lang}">`), `${lang}: stable locale page`);
}
console.log('PASS: six-language root gateway and stable locale pages');
