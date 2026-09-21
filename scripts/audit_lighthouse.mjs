#!/usr/bin/env node

import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';

const lighthouseCli = process.env.LIGHTHOUSE_CLI;
const chromePath = process.env.CHROME_PATH;
const nodeBinary = process.env.NODE_BINARY || process.execPath;
const baseUrl = (process.env.BASE_URL || 'http://localhost:3008').replace(/\/$/, '');
const outputDir = resolve(process.env.OUTPUT_DIR || 'outputs/v1-restoration/lighthouse');
const debugPort = Number(process.env.CHROME_DEBUG_PORT || 9333);

if (!lighthouseCli || !chromePath) {
  console.error('Set LIGHTHOUSE_CLI and CHROME_PATH before running this audit.');
  process.exit(2);
}

const allRoutes = [
  ['home', '/en/'],
  ['horses', '/en/horses/'],
  ['programmes', '/en/horses/programmes/'],
  ['facilities', '/en/horses/facilities/'],
  ['for-sale', '/en/horses/for-sale/'],
  ['references', '/en/horses/references/'],
  ['houses', '/en/houses/'],
  ['ortho-24', '/en/houses/ortho-24/'],
  ['ortho-25', '/en/houses/ortho-25/'],
  ['activities', '/en/activities/'],
  ['legal', '/en/legal/'],
  ['privacy', '/en/privacy/'],
];

const allProfiles = [
  ['mobile', []],
  ['desktop', ['--preset=desktop']],
];

function selectedEntries(entries, environmentName) {
  const requested = (process.env[environmentName] || '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
  if (!requested.length) return entries;
  const known = new Set(entries.map(([name]) => name));
  const unknown = requested.filter((name) => !known.has(name));
  if (unknown.length) {
    console.error(`Unknown ${environmentName}: ${unknown.join(', ')}`);
    process.exit(2);
  }
  return entries.filter(([name]) => requested.includes(name));
}

const routes = selectedEntries(allRoutes, 'AUDIT_ROUTES');
const profiles = selectedEntries(allProfiles, 'AUDIT_PROFILES');

const excludedModes = new Set(['notApplicable', 'manual', 'informative']);

async function fileHash(path) {
  const contents = await readFile(path);
  return createHash('sha256').update(contents).digest('hex');
}

async function waitForChrome() {
  const endpoint = `http://127.0.0.1:${debugPort}/json/version`;
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(endpoint);
      if (response.ok) return;
    } catch {
      // Chrome is still starting.
    }
    await new Promise((resolveWait) => setTimeout(resolveWait, 100));
  }
  throw new Error(`Chrome did not expose its debugging endpoint on port ${debugPort}.`);
}

function reportPath(stem, extension) {
  return `${stem}.report.${extension}`;
}

await mkdir(outputDir, { recursive: true });
const profileDir = await mkdtemp(join(tmpdir(), 'prepinson-lighthouse-chrome-'));
const chrome = spawn(chromePath, [
  '--headless=new',
  '--no-sandbox',
  '--disable-gpu',
  '--disable-extensions',
  '--disable-background-networking',
  '--no-first-run',
  '--no-default-browser-check',
  `--remote-debugging-port=${debugPort}`,
  `--user-data-dir=${profileDir}`,
  'about:blank',
], { stdio: 'ignore' });

const summary = {
  generatedAt: new Date().toISOString(),
  baseUrl,
  routes: routes.length,
  profiles: profiles.map(([name]) => name),
  excludedAudits: [],
  snapshot: {
    generatorSha256: await fileHash('work/build.py'),
    sourceCssSha256: await fileHash('src/styles.css'),
    generatedCssSha256: await fileHash('dist/styles.css'),
  },
  runs: [],
};

let exitCode = 0;
try {
  await waitForChrome();
  for (const [profile, profileArgs] of profiles) {
    for (const [name, path] of routes) {
      const url = `${baseUrl}${path}`;
      const stem = join(outputDir, `${name}-${profile}`);
      console.log(`[${profile}] ${name}: ${url}`);
      const result = spawnSync(nodeBinary, [
        lighthouseCli,
        url,
        `--port=${debugPort}`,
        '--hostname=127.0.0.1',
        '--output=json',
        '--output=html',
        `--output-path=${stem}`,
        '--only-categories=performance,accessibility,best-practices,seo',
        '--quiet',
        '--no-enable-error-reporting',
        ...profileArgs,
      ], { encoding: 'utf8', maxBuffer: 20 * 1024 * 1024 });

      if (result.status !== 0) {
        exitCode = 1;
        summary.runs.push({ name, profile, url, error: (result.stderr || result.stdout || `Lighthouse exited ${result.status}`).trim() });
        continue;
      }

      const lhr = JSON.parse(await readFile(reportPath(stem, 'json'), 'utf8'));
      const scores = Object.fromEntries(
        Object.entries(lhr.categories).map(([key, category]) => [key, Math.round((category.score ?? 0) * 100)]),
      );
      const failedAudits = Object.values(lhr.audits)
        .filter((audit) => audit.score !== null && audit.score < 1 && !excludedModes.has(audit.scoreDisplayMode))
        .map((audit) => ({ id: audit.id, title: audit.title, score: audit.score, displayValue: audit.displayValue || '' }));
      const targets = {
        performance: profile === 'mobile' ? scores.performance >= 90 : true,
        accessibility: scores.accessibility === 100,
        'best-practices': scores['best-practices'] === 100,
        seo: scores.seo === 100,
      };
      if (Object.values(targets).some((passed) => !passed)) exitCode = 1;
      summary.runs.push({ name, profile, url, scores, targets, failedAudits });
    }
  }
} finally {
  chrome.kill('SIGTERM');
  await new Promise((resolve) => {
    if (chrome.exitCode !== null) return resolve();
    const timer = setTimeout(resolve, 5_000);
    chrome.once('exit', () => {
      clearTimeout(timer);
      resolve();
    });
  });
  await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }).catch(() => {});
}

await writeFile(join(outputDir, 'summary.json'), JSON.stringify(summary, null, 2) + '\n');
const lines = [
  '# Lighthouse — V1 restoration',
  '',
  `Generated: ${summary.generatedAt}`,
  `Generator SHA-256: ${summary.snapshot.generatorSha256}`,
  `Source CSS SHA-256: ${summary.snapshot.sourceCssSha256}`,
  `Generated CSS SHA-256: ${summary.snapshot.generatedCssSha256}`,
  '',
  '| Page | Profile | Performance | Accessibility | Best practices | SEO |',
  '|---|---:|---:|---:|---:|---:|',
];
for (const run of summary.runs) {
  if (run.error) lines.push(`| ${run.name} | ${run.profile} | ERROR | ERROR | ERROR | ERROR |`);
  else lines.push(`| ${run.name} | ${run.profile} | ${run.scores.performance} | ${run.scores.accessibility} | ${run.scores['best-practices']} | ${run.scores.seo} |`);
}
lines.push('', '## Failing audits', '');
for (const run of summary.runs) {
  if (run.error) {
    lines.push(`### ${run.name} — ${run.profile}`, '', `Run error: ${run.error}`, '');
  } else if (run.failedAudits.length) {
    lines.push(`### ${run.name} — ${run.profile}`, '');
    for (const audit of run.failedAudits) lines.push(`- ${audit.id}: ${audit.title}${audit.displayValue ? ` — ${audit.displayValue}` : ''}`);
    lines.push('');
  }
}
await writeFile(join(outputDir, 'summary.md'), lines.join('\n') + '\n');
console.log(`Reports written to ${outputDir}`);
process.exitCode = exitCode;
