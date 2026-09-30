#!/usr/bin/env python3
"""Read-only checks against a deployed preview. Never submits forms."""
import sys,json,datetime,concurrent.futures,urllib.request,urllib.error,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from src.site_data import LANGS,ROUTES
DOMAIN="https://www.prepinson.com"
from src.legacy_routes import LEGACY_ROUTES
BASE=sys.argv[1].rstrip('/')
OUT=Path(sys.argv[2] if len(sys.argv)>2 else 'outputs/publication-2026-09-30/deployment.json')
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args):return None
opener=urllib.request.build_opener(NoRedirect)
def get(path):
 try:
  r=opener.open(BASE+path,timeout=30)
 except urllib.error.HTTPError as e:r=e
 return r.status,dict(r.headers),r.read()
checks=[];errors=[]
def page(item):
 lang,route=item;path=f'/{lang}/'+(route+'/' if route else '')
 status,h,b=get(path);s=b.decode();fail=[]
 if status!=200:fail.append('status '+str(status))
 if f'<html lang="{lang}">' not in s:fail.append('language')
 if f'href="{DOMAIN}{path}"' not in s:fail.append('canonical')
 if not any(k.lower()=='content-security-policy' for k in h):fail.append('CSP')
 if 'netlify.app' in BASE and not any(k.lower()=='x-robots-tag' and 'noindex' in v for k,v in h.items()):fail.append('preview not noindex')
 return {'path':path,'status':status,'errors':fail}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:checks=list(pool.map(page,[(l,r) for l in LANGS for r in ROUTES]))
for old,new,expected in LEGACY_ROUTES:
 status,h,b=get(old);location=next((v for k,v in h.items() if k.lower()=='location'),'')
 fail=[]
 if status!=expected:fail.append(f'expected {expected}, got {status}')
 if expected==301 and not (location==new or location==BASE+new):fail.append('destination '+location)
 checks.append({'path':old,'status':status,'location':location,'errors':fail})
for path in ['/robots.txt','/sitemap.xml','/instagram-feed.json','/instagram-health.json','/assets/steven-brunet-800.avif','/assets/pierre-martin-800.avif','/assets/luc-canivet-800.avif','/assets/training-new-800.avif','/assets/jackson-standing-800.avif','/assets/jackson-jumping-800.avif','/assets/juni-jumping-400.avif']:
 status,h,b=get(path);fail=[]
 if status!=200:fail.append('status '+str(status))
 record={'path':path,'status':status,'errors':fail}
 if path=='/sitemap.xml':record['urls']=len(ET.fromstring(b).findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'))
 if path=='/instagram-health.json':record['health']=json.loads(b)
 if path.startswith('/assets/'):record['cache']=next((v for k,v in h.items() if k.lower()=='cache-control'),'')
 checks.append(record)
status,h,b=get('/publication-qa-page-inexistante/')
checks.append({'path':'/publication-qa-page-inexistante/','status':status,'errors':[] if status==404 else ['false 404']})
errors=[c for c in checks if c['errors']]
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps({'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':BASE,'checks':checks,'errors':errors},indent=2))
print(json.dumps({'checks':len(checks),'errors':errors},indent=2))
sys.exit(bool(errors))
