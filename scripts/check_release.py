#!/usr/bin/env python3
"""Publication invariants beyond the generic site checker."""
from pathlib import Path
from html.parser import HTMLParser
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from src.site_data import LANGS,ROUTES,TEXT
from src.release_content import COPY
from src.navigation import GROUPS
from src.legacy_routes import LEGACY_ROUTES
class Tree(HTMLParser):
 def __init__(self): super().__init__();self.stack=[];self.links=[];self.ids=set();self.images=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if 'id' in a:self.ids.add(a['id'])
  if t=='a':self.links.append(a.get('href',''))
  if t=='img':self.images.append(a)
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
for key,values in COPY.items():check(len(values)==6 and all(values),f'{key}: missing translation')
check(len(ROUTES)==15,'Expected 15 public routes')
for lang in LANGS:
 for route in ROUTES:
  path=ROOT/'dist'/lang/route/'index.html';body=path.read_text();p=Tree();p.feed(body)
  for link in p.links:
   if not link.startswith('/') and not link.startswith('#'):continue
   dest,_,anchor=link.partition('#');dest=dest.split('?')[0]
   target=(ROOT/'dist'/dest.lstrip('/')/'index.html') if dest else path
   check(target.exists(),f'{path}: broken {link}')
   if target.exists() and anchor:
    parser=Tree();parser.feed(target.read_text());check(anchor in parser.ids,f'{path}: missing anchor {link}')
  check('localStorage' not in body,'Inline persistent storage')
  check('class="footer-navigation"' in body,f'{path}: footer navigation missing')
  for _,items in GROUPS:
   for _,dest in items:
    if not dest.startswith('#'):check(f'/{lang}/{dest}/' in body,f'{path}: missing nav {dest}')
 team=(ROOT/'dist'/lang/'team/index.html').read_text()
 for person in ('Steven Brunet','Pierre Martin','Luc Canivet'):check(person in team,f'{lang}: missing {person}')
 for card in team.split('<article class="staff-card">')[1:]:
  card=card.split('</article>')[0];check('mailto:' not in card and 'tel:' not in card,'New staff contact leaked')
 refs=(ROOT/'dist'/lang/'horses/references/index.html').read_text()
 check('qurious-hs-jumping' not in refs,f'{lang}: misattributed photograph')
 for asset in ('juni-jumping','jackson-standing','jackson-jumping','qurious-hs.mp4','juni-prepinson.mp4'):check(asset in refs,f'{lang}: missing {asset}')
 for pedigree in ('Soliman – Rubin Royal OLD','Eldorado de Hus – Spartakhus','Spartakhus – Lavaletto','Diamant de Semilly – Cardento'):check(pedigree in refs,f'{lang}: incomplete {pedigree}')
 for route in ('horses','horses/for-sale'):
  page=(ROOT/'dist'/lang/route/'index.html').read_text()
  for name in ('Dalton','Gatsby','Ines','Gamble','Idalgo'):check(name+' de Prepinson' in page,f'{lang}/{route}: missing sales reference {name}')
js=(ROOT/'src/app.js').read_text()
check('Max-Age=' not in js and 'localStorage' not in js,'Language preference must be session only')
red=(ROOT/'dist/_redirects').read_text()
for old,new,status in LEGACY_ROUTES:check(f'{old} {new} {status}' in red,f'Missing redirect {old}')
if errors:print('\n'.join(errors));raise SystemExit(1)
print(f'PASS: publication content, navigation, anchors, media attribution, session cookie, and {len(LEGACY_ROUTES)} legacy mappings across {len(LANGS)*len(ROUTES)} pages.')
