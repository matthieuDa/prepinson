import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const modulePath=process.env.PLAYWRIGHT_MODULE||'playwright';
const {chromium}=await import(path.isAbsolute(modulePath)?pathToFileURL(path.join(modulePath,'index.mjs')).href:modulePath);
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
const base=process.env.SITE_URL||'http://localhost:3013';
const axe=await readFile(process.env.AXE_MODULE||createRequire(import.meta.url).resolve('axe-core/axe.min.js'),'utf8');
const page=await browser.newPage({reducedMotion:'reduce'});const failures=[];let states=0;
const inspect=async(label)=>{
 await page.evaluate(axe);
 const issues=await page.evaluate(async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})));
 states++;if(issues.length)failures.push({label,issues});
};
for(const variant of ['equilibre','editorial','serein'])for(const lang of ['fr','en','nl','de','sv','lb'])for(const width of [390,1440]){
 await page.setViewportSize({width,height:900});
 for(const route of ['','horses/programmes/','contact/']){
  await page.goto(`${base}/propositions/${variant}/${lang}/${route}`);await page.evaluate(()=>document.fonts.ready);
  await inspect(`${variant}/${lang}/${route} ${width}`);
 }
 if(width===390){await page.locator('[data-menu-toggle]').click();await page.locator('#mobile-menu .nav-group').nth(1).locator('summary').click();}
 else {await page.locator('.navlinks .nav-group').nth(1).locator('summary').hover();await page.waitForFunction(()=>document.querySelectorAll('.navlinks .nav-group')[1].open);}
 await inspect(`${variant}/${lang}/navigation ${width}`);
}
await page.goto(`${base}/propositions/`);await inspect('comparison');
await browser.close();await mkdir('evidence/proposals',{recursive:true});await writeFile('evidence/proposals/accessibility.json',JSON.stringify({states,failures},null,2));console.log(JSON.stringify({states,failures},null,2));if(failures.length)process.exitCode=1;
