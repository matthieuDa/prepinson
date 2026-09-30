// Regression coverage for the primary contact path and uncropped reference photos.
import {mkdir} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const modulePath=process.env.PLAYWRIGHT_MODULE||'playwright';
const pw=await import(path.isAbsolute(modulePath)?pathToFileURL(path.join(modulePath,'index.js')).href:modulePath);
const engine=process.env.BROWSER_ENGINE||'chromium';
const browser=await (pw[engine]||pw.default[engine]).launch({headless:true,...(engine==='chromium'?{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'}:{})});
const base=process.env.SITE_URL||'http://localhost:3008';
const output=process.env.AUDIT_OUTPUT||'outputs/ux-review';
await mkdir(output,{recursive:true});
let checks=0;
function assert(ok,message) {if(!ok) throw Error(message); checks++;}
try {
  for(const lang of ['en','fr','nl','de','sv','lb']) {
    for(const width of [390,768,1440]) {
      const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
      const page=await context.newPage();
      await page.goto(`${base}/${lang}/contact/`);
      assert(await page.locator('main form').count()===1,`${lang}/${width}: one primary contact form`);
      const subject=page.locator('.contact-form select');
      assert(await subject.inputValue()==='',`${lang}/${width}: subject starts with an explicit choice`);
      assert(!(await subject.evaluate(el=>el.validity.valid)),`${lang}/${width}: empty subject cannot submit`);
      const alternatives=page.locator('.contact-alternatives');
      assert(!(await alternatives.evaluate(el=>el.open)),`${lang}/${width}: direct contacts are optional`);
      await alternatives.locator('summary').focus();
      await page.keyboard.press('Enter');
      assert(await alternatives.locator('a[href="mailto:sales@prepinson.com"]').isVisible(),`${lang}/${width}: sales email accessible by keyboard`);
      assert(await alternatives.locator('a').count()===4,`${lang}/${width}: three labeled emails and one phone`);
      await alternatives.locator('summary').press('Enter');
      assert(await page.locator('footer a[href^="https://maps.app.goo.gl/"]').count()===1,`${lang}/${width}: footer offers one address link`);
      assert(await page.locator('footer address a').innerText().then(t=>t.includes('Ortho 24')),`${lang}/${width}: directions label is the address`);
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${lang}/${width}: contact has no horizontal overflow`);
      if(process.env.AXE_MODULE&&width===390) {
        await page.addScriptTag({path:process.env.AXE_MODULE});
        const result=await page.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));
        assert(result.violations.length===0,`${lang}: contact accessibility: ${JSON.stringify(result.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)})))}`);
      }
      if(lang==='fr'&&width!==768) {
        await page.screenshot({path:`${output}/contact-${width}-${engine}.png`,fullPage:true});
      }
      await page.goto(`${base}/${lang}/horses/references/`);
      const photos=page.locator('.reference-gallery img');
      assert(await photos.count()===7,`${lang}/${width}: all seven reference photos retained`);
      for(const photo of await photos.all()) {
        await photo.scrollIntoViewIfNeeded();
        await photo.evaluate(el=>el.decode());
        const geometry=await photo.evaluate(el=>{
          const r=el.getBoundingClientRect(),b=el.closest('button').getBoundingClientRect();
          return {natural:el.naturalWidth/el.naturalHeight,display:r.width/r.height,fit:Math.abs(b.width-r.width)<1&&Math.abs(b.height-r.height)<1};
        });
        assert(Math.abs(geometry.natural-geometry.display)<.015&&geometry.fit,`${lang}/${width}: whole photo without crop or framing`);
      }
      if(lang==='fr'&&width!==768) {
        for(const id of ['dalton','juni','jackson']) {
          await page.locator(`#${id} .reference-gallery`).screenshot({path:`${output}/${id}-${width}-${engine}.png`});
        }
      }
      const opener=page.locator('#juni [data-lightbox-item]').first();
      await opener.click();
      assert(await page.locator('[data-lightbox]').evaluate(el=>el.open),`${lang}/${width}: enlarge photo still opens`);
      assert((await page.locator('[data-lightbox-image]').getAttribute('src')).includes('juni-stable.webp'),`${lang}/${width}: lightbox uses original photo`);
      await page.keyboard.press('Escape');
      assert(await opener.evaluate(el=>el===document.activeElement),`${lang}/${width}: closing gallery restores focus`);
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${lang}/${width}: references have no horizontal overflow`);
      if(process.env.AXE_MODULE&&width===390) {
        await page.addScriptTag({path:process.env.AXE_MODULE});
        const result=await page.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));
        assert(result.violations.length===0,`${lang}: references accessibility: ${result.violations.map(v=>v.id)}`);
      }
      await context.close();
    }
  }
  console.log(`PASS: ${checks} contact, footer and reference checks in ${engine}.`);
} finally {await browser.close();}
