from pathlib import Path
from html.parser import HTMLParser
from html import escape
import json,csv,re
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'dist'
LANGS=['en','fr','de','sv','nl','lb']
NAMES={'en':'English','fr':'Français','de':'Deutsch','sv':'Svenska','nl':'Nederlands','lb':'Lëtzebuergesch'}
def norm(s):return ' '.join(s.split())
source=json.loads((ROOT/'src/locales/source-strings.json').read_text())
translations={l:{} for l in LANGS}
for row in csv.reader((ROOT/'src/locales/translations.tsv').open(),delimiter='\t'):
 assert len(row)==6,row
 for l,v in zip(LANGS[1:],row[1:]):translations[l][norm(source[int(row[0])])]=v.strip()
for row in csv.reader((ROOT/'src/locales/additional.tsv').open(),delimiter='\t'):
 assert len(row)==6,row
 for l,v in zip(LANGS[1:],row[1:]):translations[l][norm(row[0])]=v.strip()
UI={
'en':{'menu':'Menu','close':'Close','language':'Language','enlarge':'Enlarge photograph: ','photo':'property photograph','instagram':'Haras de Prépinson — latest Instagram posts','pause':'Pause background film','play':'Play background film'},
'fr':{'menu':'Menu','close':'Fermer','language':'Langue','enlarge':'Agrandir la photo : ','photo':'photo de la maison','instagram':'Haras de Prépinson — dernières publications Instagram','pause':'Mettre le film en pause','play':'Lire le film'},
'de':{'menu':'Menü','close':'Schließen','language':'Sprache','enlarge':'Foto vergrößern: ','photo':'Hausfoto','instagram':'Haras de Prépinson — aktuelle Instagram-Beiträge','pause':'Hintergrundfilm pausieren','play':'Hintergrundfilm abspielen'},
'sv':{'menu':'Meny','close':'Stäng','language':'Språk','enlarge':'Förstora bilden: ','photo':'bild av huset','instagram':'Haras de Prépinson — senaste Instagram-inläggen','pause':'Pausa bakgrundsfilmen','play':'Spela bakgrundsfilmen'},
'nl':{'menu':'Menu','close':'Sluiten','language':'Taal','enlarge':'Foto vergroten: ','photo':'foto van het huis','instagram':'Haras de Prépinson — recente Instagram-berichten','pause':'Achtergrondfilm pauzeren','play':'Achtergrondfilm afspelen'},
'lb':{'menu':'Menü','close':'Zoumaachen','language':'Sprooch','enlarge':'Foto vergréisseren: ','photo':'Foto vum Haus','instagram':'Haras de Prépinson — aktuell Instagram-Bäiträg','pause':'Hannergrondfilm pauséieren','play':'Hannergrondfilm ofspillen'}}
ICONS={'↗':'arrow-up-right','↘':'arrow-down-right','↓':'arrow-down','←':'arrow-left','→':'arrow-right','▷':'play','▶':'play','Ⅱ':'pause','☰':'menu','◎':'instagram'}
def icon(name):return f'<svg class="icon icon-{name}" aria-hidden="true" focusable="false"><use href="/icons.svg#{name}"></use></svg>'
def tr(s,l):
 n=norm(s)
 if l=='en':return s.replace('Menu ☰','Menu ☰')
 if n in translations[l]:return translations[l][n]
 if n.startswith('Enlarge photograph: '):return UI[l]['enlarge']+tr(n[len('Enlarge photograph: '):],l)
 if ' — property photograph ' in n:return n.replace('property photograph',UI[l]['photo'])
 return s

def url(path,l):
 return ('/' if l=='en' else '/'+l+'/')+path.strip('/')+('/' if path.strip('/') else '')
def local_href(href,l):
 if href.startswith('/') and not href.startswith('//') and not href.startswith(('/assets/','/icons.svg','/styles.css','/app.js','/favicon.svg')):
  return ('/'+l if l!='en' else '')+href
 return href

def switch(l,route):
 links=''.join(f'<a href="{url(route,x)}" lang="{x}" hreflang="{x}" data-language="{x}"'+(' aria-current="true"' if x==l else '')+f'><span>{x.upper()}</span>{NAMES[x]}</a>' for x in LANGS)
 return f'<details class="language-switch"><summary aria-label="{UI[l]["language"]}: {NAMES[l]}"><span>{l.upper()}</span>{icon("chevron-down")}</summary><nav aria-label="{UI[l]["language"]}" class="language-options">{links}</nav></details>'

class Localizer(HTMLParser):
 def __init__(self,l,route):super().__init__(convert_charrefs=True);self.l=l;self.route=route;self.parts=[];self.script=None;self.data=[]
 def handle_decl(self,d):self.parts.append('<!'+d+'>')
 def handle_comment(self,d):self.parts.append('<!--'+d+'-->')
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='script':self.script=a.get('type','script');self.data=[]
  if tag=='html':a['lang']=self.l
  if tag=='body':a['data-language']=self.l
  if tag=='button' and a.get('class')=='menu-toggle':self.parts.append(switch(self.l,self.route))
  for k,v in list(a.items()):
   if v is None:continue
   if k in ['alt','title','aria-label'] or (tag=='meta' and k=='content'):a[k]=tr(v,self.l)
   if k=='href':a[k]=local_href(v,self.l)
  if tag=='link' and a.get('rel')=='canonical':a['href']='https://www.prepinson.com'+url(self.route,self.l)
  self.parts.append('<'+tag+''.join(' '+k if v is None else ' '+k+'="'+escape(v,quote=True)+'"' for k,v in a.items())+'>')
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.parts[-1]=self.parts[-1][:-1]+'/>'
 def handle_endtag(self,tag):
  if tag=='script':
   data=''.join(self.data)
   if self.script=='application/ld+json':
    obj=json.loads(data)
    def walk(x):
     if isinstance(x,dict):return {k:walk(v) for k,v in x.items()}
     if isinstance(x,list):return [walk(v) for v in x]
     if isinstance(x,str):
      if x.startswith('https://www.prepinson.com') and '/assets/' not in x:return 'https://www.prepinson.com'+url(self.route,self.l)
      return tr(x,self.l)
     return x
    obj=walk(obj);obj['inLanguage']=self.l
    if obj.get('@type')=='LocalBusiness':obj['description']=tr(source[2],self.l)
    data=json.dumps(obj,ensure_ascii=False)
   self.parts.append(data);self.script=None;self.data=[]
  if tag=='head':
   for l in LANGS:self.parts.append(f'<link rel="alternate" hreflang="{l}" href="https://www.prepinson.com{url(self.route,l)}">')
   self.parts.append(f'<link rel="alternate" hreflang="x-default" href="https://www.prepinson.com{url(self.route,"en")}">')
   self.parts.append('<script type="application/json" id="ui-strings">'+json.dumps(UI[self.l],ensure_ascii=False)+'</script>')
  self.parts.append('</'+tag+'>')
 def handle_data(self,d):
  if self.script is not None:self.data.append(d);return
  translated=tr(d,self.l)
  # Translation preserves deliberate spacing between text and inline elements.
  if d[:1].isspace() and not translated[:1].isspace():translated=' '+translated
  if d[-1:].isspace() and not translated[-1:].isspace():translated+=' '
  s=escape(translated,quote=False)
  if norm(d)=='Menu ☰':s=escape(UI[self.l]['menu'])+' '+icon('menu')
  elif norm(d)=='×':s=icon('close')
  elif norm(d)=='+':s=icon('plus')
  else:
   for glyph,name in ICONS.items():s=s.replace(glyph,icon(name))
  self.parts.append(s)
 def result(self):return ''.join(self.parts)

routes=['','horses','houses','houses/ortho-24','houses/ortho-25']
originals={r:(OUT/r/'index.html').read_text() for r in routes}
for l in LANGS:
 for r,html in originals.items():
  p=Localizer(l,r);p.feed(html);path=OUT/url(r,l).strip('/')/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(p.result())
 for name,value in UI[l].items():pass
 (ROOT/'src/locales'/f'{l}.json').write_text(json.dumps(translations[l],ensure_ascii=False,indent=2)+'\n')
urls=''.join('<url><loc>https://www.prepinson.com'+url(r,l)+'</loc>'+''.join(f'<xhtml:link rel="alternate" hreflang="{a}" href="https://www.prepinson.com{url(r,a)}"/>' for a in LANGS)+'</url>' for l in LANGS for r in routes)
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+urls+'</urlset>')
print('Built 30 pages in English, French, German, Swedish, Dutch and Luxembourgish.')
