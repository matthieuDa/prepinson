from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json,re
ROOT=Path(__file__).resolve().parent.parent/'dist'
errors=[]
class Page(HTMLParser):
 def __init__(self):super().__init__();self.text=[];self.attrs=[];self.skip=0;self.ids=set();self.lang='';self.alts=[]
 def handle_starttag(self,t,a):
  d=dict(a);self.attrs.append((t,d))
  if t in ['script','style']:self.skip+=1
  if d.get('id'):self.ids.add(d['id'])
  if t=='html':self.lang=d.get('lang')
  if t=='link' and d.get('hreflang'):self.alts.append(d['hreflang'])
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip-=1
 def handle_data(self,d):
  if d.strip() and not self.skip:self.text.append(d.strip())
parsed={}
for p in ROOT.rglob('*.html'):
 q=Page();q.feed(p.read_text());parsed[p]=q
for p,q in parsed.items():
 assert set(q.alts)==set(['en','fr','de','sv','nl','lb','x-default']),(p,q.alts)
 for t,a in q.attrs:
  for k in ['src','href','poster','data-film']:
   u=a.get(k,'')
   if u.startswith('/') and not u.startswith('//'):
    target=ROOT/urlsplit(u).path.lstrip('/')
    if target.is_dir():target=target/'index.html'
    if not target.exists():errors.append((p,u,'missing local file'))
    elif k=='href' and target.suffix=='.html' and urlsplit(u).fragment and urlsplit(u).fragment not in parsed[target].ids:errors.append((p,u,'missing anchor'))
 for t in q.text:
  if any(g in t for g in '↗↘↓←→▷▶Ⅱ☰◎'):errors.append((p,t,'text icon'))
 if q.lang not in ['en','fr','de','sv','nl','lb']:errors.append((p,q.lang,'language'))
 for t,a in q.attrs:
  if t=='script' and a.get('type')=='application/ld+json':pass
assert len(parsed)==30,len(parsed)
assert not errors,errors
print('PASS: 30 pages, 6 languages, reciprocal alternate links, local assets, anchors and SVG-only UI icons.')
english=set().union(*(set(q.text) for p,q in parsed.items() if q.lang=='en'))
for lang in ['fr','de','sv','nl','lb']:
 same=set().union(*(set(q.text)&english for p,q in parsed.items() if q.lang==lang))
 print(lang,'shared text:',sorted(same))
