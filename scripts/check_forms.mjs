#!/usr/bin/env node

import { existsSync, statSync } from 'node:fs';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BASE_URL = (process.env.SITE_URL || 'http://127.0.0.1:3008').replace(/\/$/, '');
const LANGUAGES = ['en', 'fr', 'nl', 'de', 'sv', 'lb'];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function loadPlaywright() {
  let specifier = process.env.PLAYWRIGHT_MODULE || 'playwright-core';
  if (path.isAbsolute(specifier)) {
    if (existsSync(specifier) && statSync(specifier).isDirectory()) specifier = path.join(specifier, 'index.js');
    specifier = pathToFileURL(specifier).href;
  }
  try {
    return await import(specifier);
  } catch (error) {
    throw new Error(`Playwright is required. Install playwright-core or set PLAYWRIGHT_MODULE. (${error.message})`);
  }
}

function browserExecutable() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const candidates = process.platform === 'darwin'
    ? ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium']
    : process.platform === 'win32'
      ? ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe']
      : ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
  return candidates.find(existsSync);
}

async function waitForSite() {
  try {
    const response = await fetch(`${BASE_URL}/en/`);
    if (response.ok) return null;
  } catch (_) {
    // Start the project's local server below.
  }
  const server = spawn(process.execPath, ['server.mjs'], { cwd: ROOT, stdio: 'ignore' });
  for (let attempt = 0; attempt < 60; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 100));
    try {
      const response = await fetch(`${BASE_URL}/en/`);
      if (response.ok) return server;
    } catch (_) {
      // The server is still starting.
    }
  }
  server.kill();
  throw new Error(`The generated site is not available at ${BASE_URL}`);
}

function watchPage(page) {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  return () => assert(errors.length === 0, `Browser error: ${errors.join('; ')}`);
}

async function fillContact(page) {
  const form = page.locator('form.contact-form');
  await form.locator('[name="name"]').fill('Test Prepinson');
  await form.locator('[name="email"]').fill('forms-test@example.com');
  await form.locator('[name="message"]').fill('Controlled form validation.');
  await form.locator('[name="privacy_acknowledged"]').check();
  return form;
}

async function fillNewsletter(page) {
  const form = page.locator('form.updates-form');
  await form.locator('[name="email"]').fill('newsletter-test@example.com');
  await form.locator('[name="consent"]').check();
  return form;
}

async function checkMarkup(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const assertNoPageErrors = watchPage(page);
  for (const lang of LANGUAGES) {
    await page.goto(`${BASE_URL}/${lang}/`, { waitUntil: 'domcontentloaded' });
    const contract = await page.evaluate(() => {
      const contact = document.querySelector('form.contact-form');
      const newsletter = document.querySelector('form.updates-form');
      return {
        contactName: contact?.getAttribute('name'),
        contactAction: contact?.getAttribute('action'),
        contactProgressive: contact?.hasAttribute('data-progressive-form'),
        newsletterName: newsletter?.getAttribute('name'),
        newsletterAction: newsletter?.getAttribute('action'),
        newsletterProgressive: newsletter?.hasAttribute('data-progressive-form'),
        newsletterFields: Array.from(newsletter?.elements || []).map((field) => field.name).filter(Boolean),
        emailRequired: newsletter?.elements.email.required,
        consentRequired: newsletter?.elements.consent.required,
        honeypotTabIndex: newsletter?.elements.company.tabIndex,
        newsletterVisible: newsletter ? getComputedStyle(newsletter).display !== 'none' && getComputedStyle(newsletter).visibility !== 'hidden' : false,
        blockerProneClasses: Array.from(document.querySelectorAll('[class]')).flatMap((element) => Array.from(element.classList)).filter((name) => name.startsWith('newsletter-')),
      };
    });
    assert(contract.contactName === `contact-${lang}`, `${lang}: historic contact form name changed`);
    assert(contract.contactAction === `/${lang}/contact/thanks/`, `${lang}: wrong contact confirmation route`);
    assert(contract.contactProgressive, `${lang}: contact enhancement hook missing`);
    assert(contract.newsletterName === 'newsletter', `${lang}: newsletter must use the shared Netlify name`);
    assert(contract.newsletterAction === `/${lang}/newsletter/thanks/`, `${lang}: wrong newsletter confirmation route`);
    assert(contract.newsletterProgressive, `${lang}: newsletter enhancement hook missing`);
    for (const field of ['form-name', 'email', 'consent', 'language', 'consent_version', 'source_page', 'company']) {
      assert(contract.newsletterFields.includes(field), `${lang}: newsletter field ${field} missing`);
    }
    assert(contract.emailRequired && contract.consentRequired, `${lang}: newsletter email and consent must be required`);
    assert(contract.honeypotTabIndex === -1, `${lang}: honeypot must stay outside keyboard order`);
    assert(contract.newsletterVisible, `${lang}: newsletter form is hidden at mobile width`);
    assert(contract.blockerProneClasses.length === 0, `${lang}: blocker-prone newsletter classes remain: ${contract.blockerProneClasses.join(', ')}`);
  }
  assertNoPageErrors();
  await context.close();
}

async function checkInteractions(browser) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  const assertNoPageErrors = watchPage(page);
  await page.goto(`${BASE_URL}/en/houses/ortho-24/`, { waitUntil: 'domcontentloaded' });
  await page.evaluate(() => document.fonts?.ready);
  assert(!(await context.cookies()).some((cookie) => cookie.name === 'prepinson-language'), 'Loading an explicit language URL changed the language preference');

  const menuButton = page.locator('[data-menu-toggle]');
  const menu = page.locator('#mobile-menu');
  await menuButton.click();
  assert(await menuButton.getAttribute('aria-expanded') === 'true', 'Mobile menu did not expose its expanded state');
  assert(await menu.evaluate((element) => element.classList.contains('open')), 'Mobile menu did not open');
  assert(await page.locator('main').evaluate((element) => element.inert), 'Page content remained interactive behind the mobile menu');
  await page.keyboard.press('Escape');
  assert(await menuButton.getAttribute('aria-expanded') === 'false', 'Escape did not close the mobile menu');
  assert(await menuButton.evaluate((element) => document.activeElement === element), 'Mobile menu did not restore focus');
  assert(!(await context.cookies()).some((cookie) => cookie.name === 'prepinson-language'), 'Menu interaction changed the language preference');

  const languageSwitch = page.locator('details.language-switch');
  await languageSwitch.locator('summary').click();
  assert(await languageSwitch.getAttribute('open') !== null, 'Compact language selector did not open');
  await page.keyboard.press('Escape');
  assert(await languageSwitch.getAttribute('open') === null, 'Escape did not close the language selector');
  assert(!(await context.cookies()).some((cookie) => cookie.name === 'prepinson-language'), 'Opening the language selector selected its current language');

  const firstPhoto = page.locator('[data-lightbox-item]').first();
  await firstPhoto.click();
  const lightbox = page.locator('[data-lightbox]');
  assert(await lightbox.getAttribute('open') !== null, 'Gallery lightbox did not open');
  assert((await lightbox.locator('[data-lightbox-image]').getAttribute('alt') || '').length > 5, 'Lightbox did not preserve the photograph alternative text');
  await lightbox.locator('[data-lightbox-next]').click();
  assert((await lightbox.locator('[data-lightbox-caption]').textContent()).trim().startsWith('2 / '), 'Lightbox next control did not advance');
  await page.keyboard.press('Escape');
  assert(await firstPhoto.evaluate((element) => document.activeElement === element), 'Lightbox did not restore focus to its opener');
  assert(!(await context.cookies()).some((cookie) => cookie.name === 'prepinson-language'), 'Gallery interaction changed the language preference');

  const filmButton = page.locator('[data-video-open]').first();
  await filmButton.click();
  const filmDialog = page.locator('[data-video-modal]');
  assert(await filmDialog.getAttribute('open') !== null, 'Film dialog did not open');
  assert((await filmDialog.locator('video').getAttribute('src') || '').endsWith('.mp4'), 'Film source was not attached on demand');
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => {
    const dialog = document.querySelector('[data-video-modal]');
    const video = dialog?.querySelector('video');
    return dialog && !dialog.open && video && !video.hasAttribute('src');
  });
  assert(await filmDialog.locator('video').getAttribute('src') === null, 'Closing the film did not release its source');
  assert(await filmButton.evaluate((element) => document.activeElement === element), 'Film dialog did not restore focus to its opener');

  const cookieBeforeLanguageChoice = (await context.cookies()).find((cookie) => cookie.name === 'prepinson-language');
  assert(!cookieBeforeLanguageChoice, `Language preference changed before a language link was selected: ${cookieBeforeLanguageChoice?.value}`);
  await languageSwitch.locator('summary').click();
  await languageSwitch.locator('[data-language="fr"]').click();
  await page.waitForURL('**/fr/houses/ortho-24/');
  const cookies = await context.cookies();
  const languageCookie = cookies.find((cookie) => cookie.name === 'prepinson-language');
  const storedLanguage = await page.evaluate(() => localStorage.getItem('prepinson-language'));
  assert(languageCookie?.value === 'fr', `Manual language choice was not persisted for the secure redirect: cookies=${JSON.stringify(cookies)} storage=${storedLanguage}`);
  assertNoPageErrors();
  await context.close();
}

async function checkNativeValidation(browser) {
  const context = await browser.newContext();
  let postCount = 0;
  await context.route('**/*', async (route) => {
    if (route.request().method() === 'POST') {
      postCount += 1;
      await route.fulfill({ status: 200, contentType: 'text/html', body: '<p>unexpected post</p>' });
    } else await route.continue();
  });
  const page = await context.newPage();
  const assertNoPageErrors = watchPage(page);
  await page.goto(`${BASE_URL}/fr/`, { waitUntil: 'domcontentloaded' });

  const newsletter = page.locator('form.updates-form');
  await newsletter.locator('button[type="submit"]').click();
  assert(await newsletter.locator('[name="email"]').evaluate((field) => field.matches(':invalid')), 'Empty newsletter email was accepted');
  await newsletter.locator('[name="email"]').fill('not-an-email');
  await newsletter.locator('button[type="submit"]').click();
  assert(await newsletter.locator('[name="email"]').evaluate((field) => field.matches(':invalid')), 'Malformed newsletter email was accepted');
  await newsletter.locator('[name="email"]').fill('valid@example.com');
  await newsletter.locator('button[type="submit"]').click();
  assert(await newsletter.locator('[name="consent"]').evaluate((field) => field.matches(':invalid')), 'Newsletter submitted without consent');

  const contact = page.locator('form.contact-form');
  await contact.locator('button[type="submit"]').click();
  assert(await contact.locator('[name="name"]').evaluate((field) => field.matches(':invalid')), 'Empty contact form was accepted');
  assert(postCount === 0, `Invalid forms issued ${postCount} POST request(s)`);
  assertNoPageErrors();
  await context.close();
}

async function checkServerError(browser) {
  const context = await browser.newContext();
  let postCount = 0;
  await context.route('**/*', async (route) => {
    if (route.request().method() === 'POST') {
      postCount += 1;
      await route.fulfill({ status: 503, contentType: 'text/plain', body: 'controlled failure' });
    } else await route.continue();
  });
  const page = await context.newPage();
  const assertNoPageErrors = watchPage(page);
  await page.goto(`${BASE_URL}/de/`, { waitUntil: 'domcontentloaded' });
  const form = await fillContact(page);
  await form.locator('button[type="submit"]').click();
  const status = form.locator('[data-form-status]');
  await status.waitFor({ state: 'visible' });
  assert((await status.textContent()).trim().length > 10, 'Server error message is not explicit');
  assert(await form.locator('[name="message"]').inputValue() === 'Controlled form validation.', 'Server error erased the message');
  assert(await form.locator('button[type="submit"]').isEnabled(), 'Server error left the submit button disabled');
  assert(postCount === 1, `Server error issued ${postCount} POST requests`);
  assertNoPageErrors();
  await context.close();
}

async function checkNetworkError(browser) {
  const context = await browser.newContext();
  let postCount = 0;
  await context.route('**/*', async (route) => {
    if (route.request().method() === 'POST') {
      postCount += 1;
      await route.abort('failed');
    } else await route.continue();
  });
  const page = await context.newPage();
  const assertNoPageErrors = watchPage(page);
  await page.goto(`${BASE_URL}/nl/`, { waitUntil: 'domcontentloaded' });
  const form = await fillNewsletter(page);
  await form.locator('button[type="submit"]').click();
  const status = form.locator('[data-form-status]');
  await status.waitFor({ state: 'visible' });
  assert((await status.textContent()).trim().length > 10, 'Network error message is not explicit');
  assert(await form.locator('[name="email"]').inputValue() === 'newsletter-test@example.com', 'Network error erased the email');
  assert(await form.locator('button[type="submit"]').isEnabled(), 'Network error left the submit button disabled');
  assert(postCount === 1, `Network error issued ${postCount} POST requests`);
  assertNoPageErrors();
  await context.close();
}

async function checkTimeout(browser) {
  const context = await browser.newContext();
  await context.addInitScript(() => {
    const nativeTimeout = window.setTimeout.bind(window);
    window.setTimeout = (callback, delay, ...args) => nativeTimeout(callback, delay === 15000 ? 50 : delay, ...args);
    window.fetch = (_url, options = {}) => new Promise((_resolve, reject) => {
      options.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
    });
  });
  const page = await context.newPage();
  const assertNoPageErrors = watchPage(page);
  await page.goto(`${BASE_URL}/sv/`, { waitUntil: 'domcontentloaded' });
  const form = await fillNewsletter(page);
  await form.locator('button[type="submit"]').click();
  const status = form.locator('[data-form-status]');
  await status.waitFor({ state: 'visible' });
  assert((await status.textContent()).trim().length > 10, 'Timeout message is not explicit');
  assert(await form.locator('[name="email"]').inputValue() === 'newsletter-test@example.com', 'Timeout erased the email');
  assert(await form.locator('button[type="submit"]').isEnabled(), 'Timeout left the submit button disabled');
  assertNoPageErrors();
  await context.close();
}

async function checkSuccessAndDoubleClick(browser) {
  const context = await browser.newContext();
  let postCount = 0;
  await context.route('**/*', async (route) => {
    if (route.request().method() === 'POST') {
      postCount += 1;
      await new Promise((resolve) => setTimeout(resolve, 180));
      await route.fulfill({ status: 200, contentType: 'text/plain', body: 'accepted' });
    } else await route.continue();
  });
  const page = await context.newPage();
  const assertNoPageErrors = watchPage(page);
  await page.goto(`${BASE_URL}/lb/`, { waitUntil: 'domcontentloaded' });
  const form = await fillNewsletter(page);
  await form.locator('button[type="submit"]').dblclick();
  await page.waitForURL('**/lb/newsletter/thanks/');
  assert(postCount === 1, `Double click issued ${postCount} newsletter POST requests`);
  assert(await page.locator('.confirmation-page').count() === 1, 'Newsletter success page did not render');

  await page.goto(`${BASE_URL}/en/`, { waitUntil: 'domcontentloaded' });
  const contact = await fillContact(page);
  await contact.locator('button[type="submit"]').click();
  await page.waitForURL('**/en/contact/thanks/');
  assert(postCount === 2, 'Contact success did not issue exactly one POST request');
  assert(await page.locator('.confirmation-page').count() === 1, 'Contact success page did not render');
  assertNoPageErrors();
  await context.close();
}

async function checkWithoutJavaScript(browser) {
  const context = await browser.newContext({ javaScriptEnabled: false });
  let postedBody = '';
  let postCount = 0;
  await context.route('**/*', async (route) => {
    if (route.request().method() === 'POST') {
      postCount += 1;
      postedBody = route.request().postData() || '';
      await route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: '<!doctype html><html lang="fr"><body><main id="native-success">ok</main></body></html>' });
    } else await route.continue();
  });
  const page = await context.newPage();
  await page.goto(`${BASE_URL}/fr/`, { waitUntil: 'domcontentloaded' });
  const form = page.locator('form.updates-form');
  await form.locator('[name="email"]').fill('no-js-test@example.com');
  await form.locator('[name="consent"]').check({ force: true });
  await Promise.all([
    page.waitForURL('**/fr/newsletter/thanks/'),
    form.locator('button[type="submit"]').click(),
  ]);
  assert(postCount === 1, `No-JS submission issued ${postCount} POST requests`);
  for (const field of ['form-name=newsletter', 'email=no-js-test%40example.com', 'consent=yes', 'language=fr', 'consent_version=', 'source_page=']) {
    assert(postedBody.includes(field), `No-JS POST is missing ${field}`);
  }
  assert(await page.locator('#native-success').count() === 1, 'No-JS POST did not navigate to its action response');
  await context.close();
}

const playwright = await loadPlaywright();
const server = await waitForSite();
const executablePath = browserExecutable();
const chromium = playwright.chromium || playwright.default?.chromium;
assert(chromium, 'The selected Playwright module does not expose Chromium');
const browser = await chromium.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });

try {
  await checkMarkup(browser);
  await checkInteractions(browser);
  await checkNativeValidation(browser);
  await checkServerError(browser);
  await checkNetworkError(browser);
  await checkTimeout(browser);
  await checkSuccessAndDoubleClick(browser);
  await checkWithoutJavaScript(browser);
  console.log('PASS: localized form contracts, validation, failures, success, double-click and no-JS submission.');
} finally {
  await browser.close();
  if (server) server.kill();
}
