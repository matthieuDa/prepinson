/** Rebuild responsive variants from the approved local photographs, never upscale. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const modulePath=process.env.SHARP_MODULE;
const require=createRequire(import.meta.url);
const imported=modulePath?require(modulePath):await import('sharp');
const sharp=imported.default || imported;
const root=path.resolve(import.meta.dirname,'..');
const manifest=JSON.parse(await fs.readFile(path.join(root,'src/image-manifest.json'),'utf8'));
const assetDir=path.join(root,'dist/assets');
const requested=new Set((process.env.IMAGE_FAMILIES || '').split(',').filter(Boolean));
const entries=Object.entries(manifest).filter(([filename])=>!requested.size || requested.has(filename));
for(const [filename,item] of entries){
 const original=await fs.readFile(path.join(assetDir,filename));
 for(const variant of item.variants){
  const output=path.join(root,'dist',variant.src);
  const source=sharp(original).resize({width:variant.width,withoutEnlargement:true});
  // A source may itself be the largest approved WebP; do not transcode it in place.
  if(path.resolve(output)!==path.resolve(assetDir,filename))await source.clone().webp({quality:80,effort:5}).toFile(output);
  await source.clone().avif({quality:50,effort:5}).toFile(output.replace(/\.webp$/,'.avif'));
 }
 if(item.mobile){
  const largest=item.mobile.reduce((a,b)=>a.width>b.width?a:b);
  const cropWidth=Math.min(item.width,Math.round(item.height*largest.width/largest.height));
  for(const variant of item.mobile){
   const source=sharp(original).extract(item.mobileCrop || {left:Math.round((item.width-cropWidth)/2),top:0,width:cropWidth,height:item.height}).resize({width:variant.width,withoutEnlargement:true});
   const output=path.join(root,'dist',variant.src);
   await source.clone().webp({quality:80,effort:5}).toFile(output);
   await source.clone().avif({quality:52,effort:5}).toFile(output.replace(/\.webp$/,'.avif'));
  }
 }
}
console.log(`Optimized ${entries.length} approved image families.`);
