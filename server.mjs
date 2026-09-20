import http from 'node:http';
import {stat} from 'node:fs/promises';
import {createReadStream} from 'node:fs';
import {createGzip} from 'node:zlib';
import {resolve, extname, sep} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(fileURLToPath(new URL('./dist',import.meta.url)));
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp','.avif':'image/avif','.svg':'image/svg+xml','.mp4':'video/mp4','.woff2':'font/woff2','.xml':'application/xml','.txt':'text/plain','.json':'application/json'};
const server=http.createServer(async(req,res)=>{
 try{
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{'Allow':'GET, HEAD'});return res.end();}
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  let file=resolve(root,'.'+pathname);
  if(file!==root&&!file.startsWith(root+sep)){res.writeHead(403);return res.end('Forbidden');}
  if(!extname(file))file=resolve(file,'index.html');
  const info=await stat(file);if(!info.isFile())throw new Error('Not a file');
  let start=0,end=info.size-1,status=200;
  const headers={'Content-Type':types[extname(file)]||'application/octet-stream','X-Content-Type-Options':'nosniff','Accept-Ranges':'bytes'};
  if(req.headers.range){
   const m=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
   if(!m||(!m[1]&&!m[2])){res.writeHead(416,{'Content-Range':`bytes */${info.size}`});return res.end();}
   if(!m[1])start=Math.max(0,info.size-Number(m[2]));else{start=Number(m[1]);if(m[2])end=Math.min(end,Number(m[2]));}
   if(start>end||start>=info.size){res.writeHead(416,{'Content-Range':`bytes */${info.size}`});return res.end();}
   status=206;headers['Content-Range']=`bytes ${start}-${end}/${info.size}`;
  }
  headers['Cache-Control']=pathname.startsWith('/assets/')?'public, max-age=31536000, immutable':'no-cache';
  const compress=status===200&&/^(?:text\/|application\/(?:javascript|xml|json))/.test(headers['Content-Type'])&&/\bgzip\b/.test(req.headers['accept-encoding']||'');
  if(compress){headers['Content-Encoding']='gzip';headers['Vary']='Accept-Encoding';}
  else headers['Content-Length']=end-start+1;
  res.writeHead(status,headers);
  if(req.method==='HEAD')return res.end();
  const stream=createReadStream(file,{start,end});stream.on('error',()=>res.destroy());res.on('close',()=>stream.destroy());if(compress)stream.pipe(createGzip()).pipe(res);else stream.pipe(res);
 }catch{res.writeHead(404,{'Content-Type':'text/html; charset=utf-8'});res.end('<h1>Page not found</h1><a href="/">Return to Prepinson</a>');}
});
server.on('error',err=>{console.error(err.code==='EADDRINUSE'?'Port 3008 is already in use. Stop the other server and run ./run.sh again.':err.message);process.exit(1)});
server.listen(3008,'0.0.0.0',()=>console.log('Prepinson is running at http://localhost:3008'));
