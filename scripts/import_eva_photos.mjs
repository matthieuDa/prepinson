/** Import Eva's V6 originals. Usage: SHARP_MODULE=/path/to/sharp node scripts/import_eva_photos.mjs /path/to/selection1 */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const sharp=require(process.env.SHARP_MODULE || 'sharp');
const sourceDir=process.argv[2];
if(!sourceDir)throw new Error('Provide the directory containing Eva’s originals.');
const root=path.resolve(import.meta.dirname,'..');
const manifest=JSON.parse(await fs.readFile(path.join(root,'src/image-manifest.json')));
const sources=JSON.parse(await fs.readFile(path.join(root,'work/asset-sources.json')));
const photos=[
 ['3M3A3140','prepinson-sport-horse',2000],
 ['3M3A3500','prepinson-horse-care',1400],
 ['3M3A3575','eva-schiller-portrait',960,.64],
 ['3M3A3579','nicolas-derouault-portrait',960,.56],
 ['3M3A3564','prepinson-team-portrait',2000],
 ['3M3A3597','prepinson-team-arena',2000],
 ['3M3A2995','prepinson-young-horse',1600],
 ['3M3A2759','prepinson-pastures',1600],
 ['3M3A3793','prepinson-rider-detail',1200],
];
for(const [original,stem,maxWidth,focal] of photos){
 const input=await fs.readFile(path.join(sourceDir,original+'.jpg'));
 const meta=await sharp(input).metadata();
 let base=sharp(input).rotate();
 if(focal){
  const width=Math.round(meta.height*.8);
  base=base.extract({left:Math.min(meta.width-width,Math.max(0,Math.round(meta.width*focal-width/2))),top:0,width,height:meta.height});
 }
 const full=await base.resize({width:maxWidth,withoutEnlargement:true}).webp({quality:86,effort:5}).toBuffer({resolveWithObject:true});
 const filename=stem+'.webp';
 await fs.writeFile(path.join(root,'dist/assets',filename),full.data);
 const {width,height}=full.info;
 const variants=[];
 for(const w of [...new Set([480,768,1200,width].filter(w=>w<=width))].sort((a,b)=>a-b)){
  const src=`/assets/${stem}-${w}.webp`;
  const resize=base.clone().resize({width:w,withoutEnlargement:true});
  await resize.clone().webp({quality:80,effort:5}).toFile(path.join(root,'dist',src));
  await resize.clone().avif({quality:50,effort:5}).toFile(path.join(root,'dist',src.replace('.webp','.avif')));
  variants.push({src,width:w,height:Math.round(height*w/width)});
 }
 manifest[filename]={width,height,variants};
 sources[filename]=`${original}.jpg, original supplied by Eva Schiller, V6, 2026-09-22`;
 console.log(`${filename}: ${width} × ${height}`);
}
manifest['prepinson-sport-horse.webp'].mobileImage='prepinson-rider-detail.webp';
await fs.writeFile(path.join(root,'src/image-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
await fs.writeFile(path.join(root,'work/asset-sources.json'),JSON.stringify(sources,null,2)+'\n');
