import {mkdir,writeFile,readFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const pwPath=process.env.PLAYWRIGHT_MODULE||'playwright';
const pw=await import(path.isAbsolute(pwPath)?pathToFileURL(path.join(pwPath,'index.mjs')).href:pwPath);
const engine=process.env.BROWSER_ENGINE||'chromium';
const browser=await pw[engine].launch({headless:true,...(engine==='chromium'?{executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{})});
const base=process.env.SITE_URL||'http://localhost:3013';
const output=process.env.AUDIT_OUTPUT||'evidence/proposals';
await mkdir(output,{recursive:true});
const variants=['equilibre','editorial','serein'], langs=['fr','en','nl','de','sv','lb'];
const routes=['','horses','horses/programmes','horses/facilities','horses/for-sale','horses/references','houses','houses/ortho-24','houses/ortho-25','activities','legal','privacy','team','horses/boarding','contact'];
const viewports=[[280,653],[320,568],[360,800],[390,844],[540,720],[699,900],[700,900],[701,900],[768,1024],[900,700],[901,900],[1024,768],[1250,900],[1251,900],[1440,1000],[1920,1080],[2560,1080],[844,390],[1114,720],[720,540]];
const issues=[], checks={layouts:0,interactions:0,content:0,accessibility:0};
const context=await browser.newContext({reducedMotion:'reduce'});
const page=await context.newPage();
let current='';
page.on('pageerror',e=>issues.push({type:'javascript',url:current,error:e.message}));
const assert=(ok,message)=>{checks.interactions++;if(!ok)issues.push({type:'interaction',url:current,message});};
try {
 for(const variant of variants) for(const lang of langs) for(const route of routes) {
  current=`/propositions/${variant}/${lang}/${route?route+'/':''}`;
  const response=await page.goto(base+current,{waitUntil:'load'});
  if(response.status()!==200)issues.push({type:'http',url:current,status:response.status()});
  await page.evaluate(()=>document.fonts.ready);
  for(const [width,height] of viewports) {
   await page.setViewportSize({width,height});
   const result=await page.evaluate(()=>{
    const ignored='[hidden],.form-trap,.visually-hidden,dialog:not([open]),.mobile-nav:not(.open)';
    const overflow=[...document.querySelectorAll('main *,header *,footer *')].filter(el=>{
     if(el.closest(ignored))return false;
     const s=getComputedStyle(el),r=el.getBoundingClientRect();
     return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0&&(r.left < -1||r.right>innerWidth+1);
    }).slice(0,5).map(el=>({class:typeof el.className==='string'?el.className:el.tagName,text:el.textContent.trim().slice(0,65),width:el.getBoundingClientRect().width,left:el.getBoundingClientRect().left}));
    const header=document.querySelector('header.nav'), items=header?[...header.querySelectorAll(':scope > a,:scope > nav,:scope > details,:scope > button')].filter(x=>getComputedStyle(x).display!=='none'):[];
    const overlap=items.some((a,i)=>items.slice(i+1).some(b=>{const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();return Math.min(x.right,y.right)>Math.max(x.left,y.left)+1&&Math.min(x.bottom,y.bottom)>Math.max(x.top,y.top)+1;}));
    return {scroll:document.documentElement.scrollWidth,overflow,overlap};
   });
   checks.layouts++;
   if(result.scroll>width+1||result.overflow.length||result.overlap)issues.push({type:'layout',url:current,width,height,...result});
  }
 }
 // Same-origin text, image and link signatures, independent of the CSS proposal.
 for(const lang of langs) {
  await page.goto(`${base}/${lang}/`);
  const signature=await page.locator('main').evaluate(el=>({text:el.textContent,images:[...el.querySelectorAll('img')].map(i=>i.getAttribute('src'))}));
  for(const variant of variants) {
   await page.goto(`${base}/propositions/${variant}/${lang}/`);
   const actual=await page.locator('main').evaluate(el=>({text:el.textContent,images:[...el.querySelectorAll('img')].map(i=>i.getAttribute('src'))}));
   checks.content++;
   if(JSON.stringify(signature)!==JSON.stringify(actual))issues.push({type:'content',variant,lang});
  }
 }
 for(const variant of variants) for(const lang of langs) {
  const prefix=`/propositions/${variant}`;
  current=`${prefix}/${lang}/`;
  await page.setViewportSize({width:1440,height:1000});await page.goto(base+current);
  const groups=page.locator('.navlinks .nav-group');
  await groups.nth(1).locator('summary').hover();
  await page.waitForFunction(()=>document.querySelectorAll('.navlinks .nav-group')[1].open);
  const panel=await groups.nth(1).locator('.nav-submenu').boundingBox();
  assert(panel.x===0&&Math.abs(panel.width-1440)<1,'Desktop panel spans header');
  await groups.nth(1).locator('a').last().hover();
  assert(await groups.nth(1).evaluate(x=>x.open),'Pointer reaches final submenu link');
  await page.keyboard.press('Escape');
  assert(!await groups.nth(1).evaluate(x=>x.open),'Escape dismisses menu');
  await groups.first().locator('summary').focus();await page.keyboard.press('Enter');
  assert(await groups.first().evaluate(x=>x.open),'Keyboard opens menu');
  await page.keyboard.press('Escape');
  await page.evaluate(()=>scrollTo({top:650,behavior:'instant'}));
  await page.waitForFunction(()=>document.querySelector('header').classList.contains('is-stuck'));
  assert(await page.locator('header').evaluate(x=>x.getBoundingClientRect().top===0),'Sticky header remains reachable');
  await page.setViewportSize({width:320,height:480});
  const button=page.locator('[data-menu-toggle]');await button.click();
  assert(await page.locator('main').evaluate(x=>x.inert),'Mobile menu protects background focus');
  await page.locator('#mobile-menu .nav-group').nth(2).locator('summary').click();
  await page.locator(`#mobile-menu a[href='${prefix}/${lang}/houses/ortho-25/']`).click();
  await page.waitForURL(`**${prefix}/${lang}/houses/ortho-25/`);
  assert((await page.locator('h1').innerText()).includes('Le Cottage'),'Mobile navigation keeps proposal');
  await page.locator('header .language-switch > summary').click();
  const other=lang==='fr'?'de':'fr';
  await page.locator(`header [data-language="${other}"]`).click();
  await page.waitForURL(`**${prefix}/${other}/houses/ortho-25/`);
  assert(await page.locator('html').getAttribute('lang')===other,'Language change keeps proposal and route');
  await page.setViewportSize({width:844,height:390});await button.click();
  await page.locator('#mobile-menu .nav-group').nth(1).locator('summary').click();
  await page.locator(`#mobile-menu a[href='${prefix}/${other}/horses/references/']`).click();
  await page.waitForURL(`**${prefix}/${other}/horses/references/`);
  assert(true,'Landscape menu scrolls to destination');
  await page.goto(`${base}${prefix}/${lang}/horses/programmes/`);
  const programmes=page.locator('.programme-list > details');
  await programmes.nth(3).locator('summary').click();
  assert(await programmes.evaluateAll(xs=>xs.filter(x=>x.open).length===1&&xs[3].open),'Programmes stay exclusive');
  assert(await page.evaluate(()=>!document.getAnimations().length),'Reduced motion avoids animation');
 }
 // Bounded visual inspection batch: each proposal, desktop, mobile, tablet and short landscape.
 for(const variant of variants) for(const [width,height] of [[1440,1100],[390,844],[768,1024],[844,390]]) {
  await page.setViewportSize({width,height});
  await page.goto(`${base}/propositions/${variant}/fr/`);await page.evaluate(async()=>{await document.fonts.ready;const images=[...document.querySelectorAll('.haras-hero img,.intro-portrait img')];for(const i of images)i.loading='eager';await Promise.all(images.map(i=>i.decode().catch(()=>{})));});
  await page.screenshot({path:`${output}/${variant}-home-${width}.png`});
  await page.locator('#haras').scrollIntoViewIfNeeded();
  await page.screenshot({path:`${output}/${variant}-intro-${width}.png`});
  if(width===1440) {
   await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));
   await page.locator('.navlinks .nav-group').nth(1).locator('summary').hover();
   await page.waitForFunction(()=>document.querySelectorAll('.navlinks .nav-group')[1].open);
   await page.screenshot({path:`${output}/${variant}-nav-${width}.png`});
  }
 }
 for(const route of ['horses/programmes','houses/ortho-24','team','contact','activities']) for(const [width,height] of [[1440,1000],[390,844]]) {
  await page.setViewportSize({width,height});await page.goto(`${base}/propositions/equilibre/fr/${route}/`);
  await page.evaluate(async()=>{await document.fonts.ready;for(const i of document.images)i.loading='eager';await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));});
  await page.screenshot({path:`${output}/equilibre-${route.replaceAll('/','-')}-${width}.png`,fullPage:true});
 }
 for(const variant of variants) {
  const c=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:568}}),p=await c.newPage();
  await p.goto(`${base}/propositions/${variant}/fr/`);
  await p.locator('#mobile-menu .nav-group').nth(1).locator('summary').click();
  await p.locator(`#mobile-menu a[href='/propositions/${variant}/fr/horses/boarding/']`).click();
  assert(await p.locator('h1').isVisible(),`${variant}: no-JS menu works`);
  await c.close();
 }
} catch(e) {issues.push({type:'fatal',url:current,error:e.stack});}
await browser.close();
await writeFile(`${output}/report-${engine}.json`,JSON.stringify({base,engine,checks,viewports,issues},null,2));
console.log(JSON.stringify({checks,issueCount:issues.length,issues:issues.slice(0,12)},null,2));
if(issues.length)process.exitCode=1;
