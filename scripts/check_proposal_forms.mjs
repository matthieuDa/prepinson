import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {mkdir,writeFile} from 'node:fs/promises';
const modulePath=process.env.PLAYWRIGHT_MODULE||'playwright';
const {chromium}=await import(path.isAbsolute(modulePath)?pathToFileURL(path.join(modulePath,'index.mjs')).href:modulePath);
const base=process.env.SITE_URL||'http://localhost:3013';
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const checks=[];
try {
 for(const variant of ['equilibre','editorial','serein']) {
  const context=await browser.newContext({viewport:{width:1440,height:1100},reducedMotion:'reduce'}),page=await context.newPage();
  let posts=0;
  await context.route('**/*',route=>route.request().method()==='POST'?(posts++,route.fulfill({status:200,body:'mocked'})):route.continue());
  if(process.env.CAPTURE_PREVIEWS) {
   await mkdir('src/designs/previews',{recursive:true});
   await page.goto(`${base}/propositions/${variant}/fr/`);
   await page.evaluate(async()=>{await document.fonts.ready;const image=document.querySelector('.intro-portrait img');image.loading='eager';await image.decode();});
   await page.locator('#haras').scrollIntoViewIfNeeded();
   await page.screenshot({path:`src/designs/previews/${variant}.jpg`,type:'jpeg',quality:84});
  }
  for(const lang of ['fr','en','nl','de','sv','lb']) {
   await page.goto(`${base}/propositions/${variant}/${lang}/contact/`);
   const form=page.locator('form.contact-form');
   await form.locator('[name="name"]').fill('Controlled test');
   await form.locator('[name="email"]').fill('test@example.com');
   await form.locator('[name="subject"]').selectOption({index:1});
   await form.locator('[name="message"]').fill('Validation locale avec réponse simulée.');
   await form.locator('[name="privacy_acknowledged"]').check();
   await form.locator('button[type="submit"]').click();
   await page.waitForURL(`**/propositions/${variant}/${lang}/contact/thanks/`);
   checks.push(`${variant}/${lang}: mocked contact confirmation retains proposal`);
   await page.goto(`${base}/propositions/${variant}/${lang}/`);
   const news=page.locator('form.updates-form');
   await news.locator('[name="email"]').fill('test@example.com');
   await news.locator('[name="consent"]').check();
   await news.locator('button[type="submit"]').click();
   await page.waitForURL(`**/propositions/${variant}/${lang}/newsletter/thanks/`);
   checks.push(`${variant}/${lang}: mocked newsletter confirmation retains proposal`);
  }
  if(posts!==12)throw Error(`Unexpected POST count: ${posts}`);
  await context.close();
 }
 await mkdir('evidence/proposals',{recursive:true});
 await writeFile('evidence/proposals/forms.json',JSON.stringify({checks,mocked:true},null,2));
 console.log(`${checks.length} form flows checked with intercepted submissions.`);
} finally {await browser.close();}
