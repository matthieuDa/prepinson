// Browser regressions for visible content, one-time reveals and motion preferences.
import { mkdir, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const modulePath = process.env.PLAYWRIGHT_MODULE || 'playwright';
const pw = await import(path.isAbsolute(modulePath) ? pathToFileURL(path.join(modulePath, 'index.js')).href : modulePath);
const engine = process.env.BROWSER_ENGINE || 'chromium';
const browser = await (pw[engine] || pw.default[engine]).launch({ headless: true, ...(engine === 'chromium' ? { executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' } : {}) });
const base = process.env.SITE_URL || 'http://localhost:3008';
const output = process.env.AUDIT_OUTPUT || 'outputs/navigation-motion';
await mkdir(output, { recursive: true });
const checks = [], errors = [];
function assert(ok, message) { if (!ok) throw Error(message); checks.push(message); }
try {
  for (const lang of ['en', 'fr', 'nl', 'de', 'sv', 'lb']) {
    for (const width of [390, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: 'no-preference' });
      const page = await context.newPage();
      page.on('pageerror', error => errors.push({ lang, width, error: error.message }));
      await page.goto(`${base}/${lang}/`);
      await page.evaluate(() => document.fonts.ready);
      assert(await page.locator('.hero-editorial').evaluate(el => getComputedStyle(el).opacity === '1' && getComputedStyle(el).animationName === 'none'), `${lang}/${width}: hero visible immediately`);
      if (lang === 'fr') await page.screenshot({ path: `${output}/home-${width}.png` });
      await page.evaluate(() => {
        const target = document.querySelector('.expertise-heading h2');
        window.scrollTo({ top: target.getBoundingClientRect().top + scrollY - innerHeight / 2, behavior: 'instant' });
      });
      await page.waitForFunction(() => document.querySelector('.expertise-heading h2').getAnimations().some(a => a.id === 'prepinson-reveal'));
      checks.push(`${lang}/${width}: section appears on entry`);
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.waitForFunction(() => !document.getAnimations().some(a => a.id === 'prepinson-reveal'));
      assert(await page.locator('.expertise-heading h2').evaluate(el => getComputedStyle(el).opacity === '1'), `${lang}/${width}: changing motion preference settles visible content`);
      await page.emulateMedia({ reducedMotion: 'no-preference' });
      await page.evaluate(() => scrollTo({ top: 0, behavior: 'instant' }));
      await page.evaluate(() => {
        const target = document.querySelector('.expertise-heading h2');
        scrollTo({ top: target.getBoundingClientRect().top + scrollY - innerHeight / 2, behavior: 'instant' });
      });
      await page.waitForTimeout(100);
      assert(await page.evaluate(() => !document.getAnimations().some(a => a.id === 'prepinson-reveal')), `${lang}/${width}: settled reveals never replay`);
      await page.evaluate(() => scrollTo({ top: 700, behavior: 'instant' }));
      if (width === 390) {
        await page.locator('[data-menu-toggle]').click();
        await page.locator('#mobile-menu .nav-group').nth(1).locator('summary').click();
        await page.waitForTimeout(300);
        assert(await page.locator('#mobile-menu').evaluate(el => {
          const r = el.getBoundingClientRect();
          return Math.abs(r.left) < 1 && r.right <= innerWidth + 1 && Math.abs(r.top - document.querySelector('header').getBoundingClientRect().bottom) < 1 && getComputedStyle(el).opacity === '1';
        }), `${lang}: mobile panel aligned after scrolling`);
        if (lang === 'fr') await page.screenshot({ path: `${output}/menu-mobile.png` });
      } else {
        await page.locator('.navlinks .nav-group').nth(1).locator('summary').hover();
        await page.waitForTimeout(500);
        assert(await page.locator('.navlinks .nav-group').nth(1).evaluate(el => el.open), `${lang}: refined desktop panel opens`);
        if (lang === 'fr') await page.screenshot({ path: `${output}/menu-desktop.png` });
      }
      await context.close();
    }
    const reduced = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
    const p = await reduced.newPage();
    await p.goto(`${base}/${lang}/`);
    await p.locator('.expertise-card').first().scrollIntoViewIfNeeded();
    assert(await p.evaluate(() => !document.getAnimations().length && [...document.querySelectorAll('main h2,.expertise-card')].every(el => getComputedStyle(el).opacity === '1')), `${lang}: reduced motion keeps all sections visible without animation`);
    await reduced.close();
  }
  const fallback = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const p = await fallback.newPage();
  await p.addInitScript(() => { delete window.IntersectionObserver; });
  await p.goto(`${base}/fr/`);
  await p.locator('.expertise-card').first().scrollIntoViewIfNeeded();
  assert(await p.locator('.expertise-card').first().evaluate(el => getComputedStyle(el).opacity === '1'), 'No observer: content remains visible');
  await fallback.close();
  const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const q = await nojs.newPage();
  await q.goto(`${base}/fr/`);
  assert(await q.locator('#mobile-menu').evaluate(el => getComputedStyle(el).opacity === '1' && getComputedStyle(el).visibility === 'visible'), 'No JavaScript: mobile navigation remains visible');
  assert(await q.locator('.hero-editorial').evaluate(el => getComputedStyle(el).opacity === '1'), 'No JavaScript: hero is visible');
  await nojs.close();
} catch (error) { errors.push({ error: error.stack }); }
await browser.close();
await writeFile(`${output}/motion-${engine}.json`, JSON.stringify({ date: new Date().toISOString(), engine, base, checks, errors }, null, 2));
console.log(JSON.stringify({ engine, checks: checks.length, errors }, null, 2));
if (errors.length) process.exitCode = 1;
