import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const mod=process.env.PLAYWRIGHT_MODULE||'playwright-core';
const pw=await import(path.isAbsolute(mod)?pathToFileURL(path.join(mod,'index.js')).href:mod);
const chromium=pw.chromium||pw.default?.chromium;
const base=process.env.SITE_URL||'http://localhost:3008';
const output=process.env.AUDIT_OUTPUT||'outputs/v1-restoration';
await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const langs=['en','fr','nl','de','sv','lb'];
const routes=['','horses','horses/programmes','horses/facilities','horses/for-sale','horses/references','houses','houses/ortho-24','houses/ortho-25','activities','legal','privacy'];
const widths=[360,390,768,1024,1280,1440,1920], errors=[],checks=[];
const context=await browser.newContext({deviceScaleFactor:1});
const page=await context.newPage();
let current='';
page.on('pageerror',error=>errors.push({page:current,type:'javascript',message:error.message}));
for(const lang of (process.env.CAPTURE_ONLY ? [] : langs))for(const route of routes){
 current=`/${lang}/${route?route+'/':''}`;
 const response=await page.goto(base+current,{waitUntil:'load'});
 if(response.status()!==200)errors.push({page:current,type:'http',status:response.status()});
 await page.evaluate(()=>document.fonts.ready);
 for(const width of widths){
  await page.setViewportSize({width,height:900});
  const result=await page.evaluate(()=>{
   const overflow=[...document.querySelectorAll('main *,header *,footer *,#contact *')].filter(el=>{
    const r=el.getBoundingClientRect(),s=getComputedStyle(el);
    return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&(r.left < -1||r.right>innerWidth+1)&&!el.closest('[hidden],.form-trap,.sr-only,dialog:not([open]),.mobile-menu:not(.open)');
   }).slice(0,10).map(el=>({tag:el.tagName,cls:el.className,text:el.textContent.trim().slice(0,60),rect:{x:el.getBoundingClientRect().x,w:el.getBoundingClientRect().width}}));
   return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth,overflow,bodyFont:getComputedStyle(document.body).fontFamily,h1Font:getComputedStyle(document.querySelector('h1')).fontFamily,images:[...document.images].filter(x=>x.getBoundingClientRect().top<innerHeight&&x.getBoundingClientRect().bottom>0&&!x.closest('dialog')).every(x=>x.complete&&x.naturalWidth>0)};
  });
  if(result.scrollWidth>width+1||result.overflow.length)errors.push({page:current,type:'overflow',...result});
  checks.push({page:current,width,scrollWidth:result.scrollWidth});
 }
}
for(const route of ['','horses','houses','houses/ortho-24','houses/ortho-25'])for(const width of [390,768,1440]){
 await page.setViewportSize({width,height:900});
 await page.goto(base+'/en/'+(route?route+'/':''),{waitUntil:'load'});await page.evaluate(()=>document.fonts.ready);
 await page.evaluate(async()=>{for(const i of document.images){if(!i.closest('dialog'))i.loading='eager';} await Promise.all([...document.images].filter(i=>!i.closest('dialog')).map(i=>i.decode().catch(()=>{})));});
 // Capture the settled top position; smooth scrolling would displace fixed UI in a full-page screenshot.
 await page.evaluate(()=>{window.scrollTo({top:0,behavior:'instant'});});
 await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await page.evaluate(()=>Promise.all([...document.images].filter(i=>!i.closest('dialog')).map(i=>i.complete?Promise.resolve():new Promise(r=>{i.onload=r;i.onerror=r;setTimeout(r,3000)}))));
 await page.screenshot({path:`${output}/current-${route.replaceAll('/','-')||'home'}-${width}.png`,fullPage:true});
 await page.screenshot({path:`${output}/viewport-${route.replaceAll('/','-')||'home'}-${width}.png`});
}
await browser.close();
if(!process.env.CAPTURE_ONLY)await writeFile(`${output}/layout-report.json`,JSON.stringify({date:new Date().toISOString(),base,checks,errors},null,2));
console.log(JSON.stringify({checks:checks.length,errorCount:errors.length,errors:errors.slice(0,8)},null,2));
if(errors.length)process.exitCode=1;
