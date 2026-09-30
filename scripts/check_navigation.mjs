// Real-browser interaction checks; all submissions are covered by check_forms.mjs with mocked endpoints.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const modulePath=process.env.PLAYWRIGHT_MODULE||'playwright';
const pw=await import(path.isAbsolute(modulePath)?pathToFileURL(path.join(modulePath,'index.js')).href:modulePath);
const engineName=process.env.BROWSER_ENGINE||'chromium';
const browser=await (pw[engineName]||pw.default[engineName]).launch({headless:true,...(engineName==='chromium'?{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{})});
const base=process.env.SITE_URL||'http://localhost:3008', output=process.env.AUDIT_OUTPUT||'outputs/publication-2026-09-30';
await mkdir(output,{recursive:true});
const checks=[],errors=[];
function assert(ok,message){if(!ok)throw Error(message);checks.push(message);}
try {
 for(const lang of ['en','fr','nl','de','sv','lb']) {
  const context=await browser.newContext({viewport:{width:360,height:480},reducedMotion:'reduce'}),page=await context.newPage();
  const external=[];page.on('request',req=>{if(!req.url().startsWith(base)&&!req.url().startsWith('data:')&&!req.url().startsWith('blob:'+base+'/'))external.push(req.url());});
  await page.goto(`${base}/${lang}/contact/`);
  assert((await context.cookies()).length===0,`${lang}: no unsolicited cookie`);
  const button=page.locator('[data-menu-toggle]'),groups=page.locator('#mobile-menu .nav-group');
  await button.click();
  assert(await page.locator('main').evaluate(el=>el.inert),`${lang}: contact form and main inert under menu`);
  assert(await page.locator('footer').evaluate(el=>el.inert),`${lang}: footer inert under menu`);
  assert(await groups.first().locator('summary').evaluate(el=>el===document.activeElement),`${lang}: focus enters mobile menu`);
  await page.keyboard.press('Enter');
  await page.waitForFunction(()=>document.querySelector('#mobile-menu .nav-group').open);
  await page.keyboard.press('Tab');
  assert(await page.locator('#mobile-menu').evaluate(el=>el.contains(document.activeElement)),`${lang}: submenu keyboard reachable`);
  await page.keyboard.press('Escape');
  assert(!(await groups.first().evaluate(el=>el.open)),`${lang}: Escape closes submenu`);
  await page.keyboard.press('Escape');
  assert(await button.evaluate(el=>el===document.activeElement&&el.getAttribute('aria-expanded')==='false'),`${lang}: Escape returns focus to menu control`);
  assert(!(await page.locator('main').evaluate(el=>el.inert)),`${lang}: contact unlocked after close`);
  await button.click();
  await groups.nth(2).locator('summary').click();
  const cottage=groups.nth(2).locator(`a[href='/${lang}/houses/ortho-25/']`);
  await cottage.click();await page.waitForURL(`**/${lang}/houses/ortho-25/`);
  assert((await page.locator('h1').innerText()).includes('Le Cottage'),`${lang}: touch menu navigates to Le Cottage`);
  await page.locator('header .language-switch summary').click();
  const other=lang==='fr'?'en':'fr';
  await page.locator(`header .language-switch [data-language=${other}]`).click();await page.waitForURL(`**/${other}/houses/ortho-25/`);
  const cookies=await context.cookies();
  assert(cookies.length===1&&cookies[0].name==='prepinson-language'&&cookies[0].expires===-1&&cookies[0].value===other,`${lang}: manual language choice creates only a session cookie`);
  assert(await page.evaluate(()=>localStorage.length===0),`${lang}: no local storage`);
  await page.goto(`${base}/${lang}/team/`);
  assert(await page.locator('html').getAttribute('lang')===lang,`${lang}: explicit URL overrides cookie`);
  await page.setViewportSize({width:1440,height:900});
  const desktop=page.locator('.navlinks .nav-group');
  await desktop.first().locator('summary').focus();await page.keyboard.press('Enter');
  assert(await desktop.first().evaluate(el=>el.open),`${lang}: desktop keyboard menu opens`);
  await page.keyboard.press('Escape');
  assert(await desktop.first().locator('summary').evaluate(el=>el===document.activeElement),`${lang}: desktop closure restores focus`);
  assert(await page.locator('.navlinks > a[href$="/contact/"]').count()===1,`${lang}: Contact is a direct link`);
  // Browser zoom reflows a 1440px window at 200% into a 720 CSS-pixel viewport.
  await page.setViewportSize({width:720,height:450});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${lang}: 200 percent zoom-equivalent viewport has no horizontal page overflow`);
  assert(external.length===0,`${lang}: no third-party requests ${external.join(", ")}`);
  await context.close();
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:640}}),p=await nojs.newPage();
  await p.goto(`${base}/${lang}/`);
  await p.locator('#mobile-menu .nav-group').nth(1).locator('summary').click();
  await p.locator(`#mobile-menu a[href='/${lang}/horses/boarding/']`).click();
  await p.waitForURL(`**/${lang}/horses/boarding/`);
  assert(await p.locator('h1').isVisible(),`${lang}: navigation works without JavaScript`);
  await nojs.close();
 }
 if(process.env.AXE_MODULE) {
  const axe=await readFile(process.env.AXE_MODULE,'utf8');
  const context=await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'}),page=await context.newPage();
  for(const lang of ['en','fr','nl','de','sv','lb'])for(const route of ['','horses/','horses/programmes/','horses/facilities/','horses/for-sale/','horses/references/','houses/','houses/ortho-24/','houses/ortho-25/','activities/','legal/','privacy/','team/','horses/boarding/','contact/']) {
   await page.goto(`${base}/${lang}/${route}`);await page.evaluate(axe);
   const violations=await page.evaluate(async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','best-practice']}})).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)})));
   if(violations.length)errors.push({page:`/${lang}/${route}`,violations});
   checks.push(`axe: /${lang}/${route}`);
  }
  await context.close();
 }
} catch(error){errors.push({error:error.stack});}
const report={date:new Date().toISOString(),engine:engineName,version:browser.version(),base,checks,errors};
await browser.close();await writeFile(`${output}/navigation-${engineName}.json`,JSON.stringify(report,null,2));
console.log(JSON.stringify({engine:engineName,checks:checks.length,errorCount:errors.length,errors:errors.slice(0,5)},null,2));if(errors.length)process.exitCode=1;
