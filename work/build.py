#!/usr/bin/env python3
"""Generate the complete multilingual Prepinson static website."""

from html import escape
from pathlib import Path
import json
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.site_data import LANGS, LANGUAGE_NAMES, ROUTES, text  # noqa: E402

OUT = ROOT / "dist"
DOMAIN = "https://www.prepinson.com"
# Preview media must resolve to the new deploy, while canonical URLs stay stable.
ASSET_DOMAIN = os.environ.get("DEPLOY_PRIME_URL", DOMAIN).rstrip("/") if os.environ.get("PREVIEW_MODE") == "true" else DOMAIN
IG_HARAS = "https://www.instagram.com/haras_de_prepinson/"
IG_HOUSE = "https://www.instagram.com/prepinson_the_house/"
MAP_HARAS = "https://maps.app.goo.gl/qU2NuF7tHseKitHJ6"
MAP_HOUSE = "https://maps.app.goo.gl/FzkorC926XiJ6Fzw7"
CASA = "https://www.casapilot.com/en/1091854-holiday-home-in-la-roche-en-ardenne-ardennes-and-eifel-belgium"
AIRBNB = "https://airbnb.com/h/ortho25"

META = {
    "": ("home_title", "home_desc"),
    "horses": ("horses_title", "horses_desc"),
    "horses/programmes": ("programmes_title", "programmes_desc"),
    "horses/facilities": ("facilities_title", "facilities_desc"),
    "horses/for-sale": ("sales_title", "sales_desc"),
    "horses/references": ("references_title", "references_desc"),
    "houses": ("houses_title", "houses_desc"),
    "houses/ortho-24": ("ortho24_title", "ortho24_desc"),
    "houses/ortho-25": ("ortho25_title", "ortho25_desc"),
    "activities": ("activities_title", "activities_desc"),
    "legal": ("legal_title", "legal_desc"),
    "privacy": ("privacy_title", "privacy_desc"),
}

NAV = (
    ("", "nav_home"), ("horses", "nav_horses"),
    ("horses/programmes", "nav_programmes"),
    ("horses/facilities", "nav_facilities"),
    ("horses/for-sale", "nav_sales"), ("houses", "nav_houses"),
    ("activities", "nav_activities"),
)

IMAGE_DIMS = {
    "hero-horses": (2000, 1333), "training": (2000, 1290),
    "facilities": (2000, 1333), "house-hero": (2000, 1333),
}


def url(lang, route=""):
    return f"/{lang}/" + (route.strip("/") + "/" if route else "")


def responsive_image(stem, alt, hero=False, cls=""):
    w, h = IMAGE_DIMS[stem]
    sizes = "100vw" if hero else "(max-width: 760px) 100vw, 50vw"
    loading = 'fetchpriority="high"' if hero else 'loading="lazy" decoding="async"'
    return (
        f'<picture><source type="image/webp" srcset="'
        + ", ".join(f"/assets/{stem}-{n}.webp {n}w" for n in (480, 768, 1200, 1600, 2000))
        + f'" sizes="{sizes}"><img class="{cls}" src="/assets/{stem}-1200.webp" '
          f'width="{w}" height="{h}" alt="{escape(alt)}" {loading}></picture>'
    )


def static_image(name, alt, width=1200, height=800, cls="", hero=False):
    loading = 'fetchpriority="high"' if hero else 'loading="lazy" decoding="async"'
    return (f'<img class="{cls}" src="/assets/{name}" width="{width}" height="{height}" '
            f'alt="{escape(alt)}" {loading}>')


def language_links(lang, route):
    links = []
    for code in LANGS:
        current = ' aria-current="true"' if code == lang else ""
        links.append(f'<a href="{url(code, route)}" lang="{code}" hreflang="{code}" data-language="{code}"{current}>{code.upper()}</a>')
    return "".join(links)


def header(lang, route):
    links = "".join(
        f'<a href="{url(lang, target)}"' + (' aria-current="page"' if route == target else "") + f'>{text(label, lang)}</a>'
        for target, label in NAV
    )
    return f'''<a class="skip-link" href="#main">{text("skip", lang)}</a>
<header class="site-header">
  <a class="brand" href="{url(lang)}" aria-label="HARAS DE PREPINSON"><img src="/assets/logo-mark.png" width="260" height="260" alt=""><span>HARAS DE PREPINSON</span></a>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav"><span>{text('menu', lang)}</span></button>
  <nav id="primary-nav" class="primary-nav" aria-label="{text('menu', lang)}">{links}<a class="contact-link" href="#contact">{text('nav_contact', lang)}</a></nav>
  <nav class="language-nav" aria-label="{text('language', lang)}">{language_links(lang, route)}</nav>
</header>'''


def footer(lang):
    opts = "".join(f'<option value="{text(k, lang)}">{text(k, lang)}</option>' for k in (
        "interest_boarding", "interest_training", "interest_sales", "interest_stay", "interest_other"))
    return f'''<section id="contact" class="contact"><div class="split container"><div><p class="eyebrow">{text('contact_eyebrow', lang)}</p><h2>{text('contact_title', lang)}</h2><p>{text('contact_copy', lang)}</p><p><a href="mailto:haras@prepinson.com">haras@prepinson.com</a><br><a href="tel:+32470851310">+32 470 85 13 10</a></p></div>
<form name="contact-{lang}" method="POST" data-netlify="true" netlify-honeypot="company"><input type="hidden" name="form-name" value="contact-{lang}"><p class="trap"><label>Do not fill <input name="company" tabindex="-1" autocomplete="off"></label></p>
<label>{text('form_name', lang)}<input name="name" autocomplete="name" required></label><label>{text('form_email', lang)}<input type="email" name="email" autocomplete="email" required></label><label>{text('form_interest', lang)}<select name="interest">{opts}</select></label><label>{text('form_message', lang)}<textarea name="message" rows="5" required></textarea></label><label class="check"><input type="checkbox" name="privacy" required> <span>{text('form_privacy', lang)} <a href="{url(lang, 'privacy')}">{text('footer_privacy', lang)}</a></span></label><button class="button" type="submit">{text('form_send', lang)}</button></form></div></section>
<footer><div class="container footer-grid"><div><h2>{text('newsletter_title', lang)}</h2><p>{text('newsletter_copy', lang)}</p><button class="button muted" type="button" disabled>{text('newsletter_status', lang)}</button></div><div><strong>HORSES</strong><a href="{IG_HARAS}" rel="noopener noreferrer">Instagram</a><a href="mailto:haras@prepinson.com">haras@prepinson.com</a></div><div><strong>HOUSES</strong><a href="{IG_HOUSE}" rel="noopener noreferrer">Instagram</a><a href="mailto:thehouse@prepinson.com">thehouse@prepinson.com</a></div><div><strong>{text('footer_visit', lang)}</strong><address>Ortho 24<br>6983 La Roche-en-Ardenne<br>Belgium</address><a href="{MAP_HARAS}" rel="noopener noreferrer">{text('footer_maps_haras', lang)}</a><a href="{MAP_HOUSE}" rel="noopener noreferrer">{text('footer_maps_house', lang)}</a></div></div><div class="container footer-bottom"><span>© 2026 HARAS DE PREPINSON</span><a href="{url(lang, 'legal')}">{text('footer_legal', lang)}</a><a href="{url(lang, 'privacy')}">{text('footer_privacy', lang)}</a></div></footer>'''


def hero(lang, eyebrow, heading, intro, image="hero-horses"):
    return f'''<section class="hero">{responsive_image(image, heading, True, 'hero-image')}<div class="hero-overlay"><p class="eyebrow">{eyebrow}</p><h1>{heading}</h1><p>{intro}</p><a class="button light" href="#content">{text('discover', lang)}</a></div></section>'''


def cards(items):
    return '<div class="card-grid">' + "".join(f'<article class="card"><h2>{title}</h2><p>{copy}</p>{link}</article>' for title, copy, link in items) + '</div>'


def home(lang):
    faq = "".join(f'<details><summary>{text(f"faq_{i}_q",lang)}</summary><p>{text(f"faq_{i}_a",lang)}</p></details>' for i in range(1, 5))
    return hero(lang, text("home_eyebrow",lang), text("home_hero",lang), text("home_tagline",lang)) + f'''
<section id="content" class="intro container"><h2>{text('home_intro_title',lang)}</h2><p>{text('home_intro',lang)}</p></section>
<section class="world container">{cards([
 (text('world_horses',lang), text('world_horses_copy',lang), f'<a href="{url(lang,"horses")}">{text("learn_more",lang)} →</a>'),
 (text('world_houses',lang), text('world_houses_copy',lang), f'<a href="{url(lang,"houses")}">{text("learn_more",lang)} →</a>')])}</section>
<section class="stats"><div class="container"><h2>{text('stats_title',lang)}</h2><div class="stat-grid"><div><b>18</b><span>{text('stat_boxes',lang)}</span></div><div><b>27 × 60 m</b><span>{text('stat_indoor',lang)}</span></div><div><b>40 × 75 m</b><span>{text('stat_outdoor',lang)}</span></div><div><b>28 ha</b><span>{text('stat_land',lang)}</span></div></div></div></section>
<section class="feature split container"><div>{responsive_image('house-hero', text('houses_teaser_title',lang), False)}</div><div><h2>{text('houses_teaser_title',lang)}</h2><p>{text('houses_teaser_copy',lang)}</p><a class="button" href="{url(lang,'houses')}">{text('learn_more',lang)} — {text('world_houses',lang)}</a></div></section>
<section class="instagram container"><h2>{text('instagram_title',lang)}</h2><p>{text('instagram_copy',lang)}</p><div class="gallery">{static_image('prepinson-mare-and-foal.webp','',960,640)}{static_image('prepinson-show-jumping-training.webp','',960,640)}{static_image('prepinson-stables-flowers.webp','',960,640)}</div><a href="{IG_HARAS}" rel="noopener noreferrer">Instagram →</a></section>
<section class="faq container"><h2>{text('faq_title',lang)}</h2>{faq}</section>'''


def horses(lang):
    items=[]
    for r, a, b in (("horses/programmes","service_programmes","service_programmes_copy"),("horses/facilities","service_facilities","service_facilities_copy"),("horses/references","service_references","service_references_copy"),("horses/for-sale","service_sales","service_sales_copy")):
        items.append((text(a,lang), text(b,lang), f'<a href="{url(lang,r)}">{text("learn_more",lang)} →</a>'))
    return hero(lang, "HARAS DE PREPINSON · BELGIUM", text("horses_hero",lang), text("horses_intro",lang), "training") + f'<section id="content" class="container">{cards(items)}</section>'


def programmes(lang):
    items=[]
    for i in range(1,5):
        items.append((text(f"p{i}_title",lang), f'<strong>{text(f"p{i}_timing",lang)}</strong><br>{text(f"p{i}_copy",lang)}', ""))
    return hero(lang, text("nav_programmes",lang), text("programmes_hero",lang), text("programmes_intro",lang), "training") + f'<section id="content" class="container">{cards(items)}</section>'


def facilities(lang):
    bullets = ["facility_equipment","facility_club","facility_breeding","facility_trails"]
    return hero(lang, text("nav_facilities",lang), text("facilities_hero",lang), text("facilities_intro",lang), "facilities") + f'''<section id="content" class="split container"><div><h2>{text('stats_title',lang)}</h2><ul class="large-list"><li>18 {text('stat_boxes',lang)}</li><li>27 × 60 m {text('stat_indoor',lang)} · fibre</li><li>40 × 75 m {text('stat_outdoor',lang)} · ebb &amp; flood</li><li>28 ha {text('stat_land',lang)}</li>{''.join(f'<li>{text(k,lang)}</li>' for k in bullets)}</ul><p>{text('rental_range',lang)}</p><p>{text('availability',lang)}</p></div>{responsive_image('facilities',text('facilities_hero',lang),False)}</section>'''


def sales(lang):
    return hero(lang, text("nav_sales",lang), text("sales_hero",lang), text("sales_intro",lang), "hero-horses") + f'''<section id="content" class="split container"><div><h2>{text('sales_range',lang)}</h2><p>{text('sales_cta',lang)}</p><a class="button" href="#contact">{text('nav_contact',lang)}</a></div>{static_image('prepinson-bay-horse-outdoors.webp','',960,640)}</section>'''


def references(lang):
    stories=[(text('dalton_title',lang),text('dalton_copy',lang)),(text('juni_title',lang),text('juni_copy',lang)),(text('jackson_title',lang),text('jackson_copy',lang))]
    return hero(lang, text("service_references",lang), text("references_hero",lang), text("reference_photo_note",lang), "hero-horses") + f'<section id="content" class="container">{cards([(a,b,"") for a,b in stories])}</section>'


def houses(lang):
    house_cards=[(text('ortho24_title',lang),text('ortho24_desc',lang),f'<a href="{url(lang,"houses/ortho-24")}">{text("explore_house",lang)} →</a>'),(text('ortho25_title',lang),text('ortho25_desc',lang),f'<a href="{url(lang,"houses/ortho-25")}">{text("explore_house",lang)} →</a>')]
    return hero(lang, "ORTHO · BELGIAN ARDENNES", text("houses_hero",lang), text("houses_intro",lang), "house-hero") + f'<section id="content" class="container">{cards(house_cards)}</section>'


def house(lang, which):
    is24=which=="ortho-24"; title=text("ortho24_title" if is24 else "ortho25_title",lang); desc=text("ortho24_desc" if is24 else "ortho25_desc",lang); booking=CASA if is24 else AIRBNB
    photo="house-hero" if is24 else "prepinson-ortho-25-garden-terrace.webp"
    media=responsive_image(photo,title,True,'hero-image') if is24 else static_image(photo,title,1200,800,'hero-image',hero=True)
    return f'<section class="hero">{media}<div class="hero-overlay"><p class="eyebrow">ORTHO · BELGIUM</p><h1>{title}</h1><p>{desc}</p></div></section><section id="content" class="split container"><div><h2>{text("house_detail_intro",lang)}</h2><p>{desc}</p><p>8 {text("guests",lang)} · {4 if is24 else 3} {text("bedrooms",lang)} · {4 if is24 else 3} {text("bathrooms",lang)}</p></div><div><a class="button" href="{booking}" rel="noopener noreferrer">{text("book_official",lang)} →</a><p><a href="{MAP_HOUSE}" rel="noopener noreferrer">Google Maps →</a></p></div></section>'


ACTIVITIES = (
    ("act_walk", (("Ortho-Hives Tourisme","https://www.ortho-hives-tourisme.com/randonner"),("Lac et barrage de Nisramont","https://www.la-roche-tourisme.com/le-lac-et-le-barrage-de-nisramont/"),("Le Hérou","https://www.luxembourg-belge.be/diffusio/fr/voir-faire/visiter/patrimoine-naturel/nadrin/le-herou_TFOALD-01-08H9-01.php"),("Le Cheslé","https://www.la-roche-tourisme.com/la-forteresse-celtique-du-chesle/"))),
    ("act_cycle", (("SoWatt e-bike","https://sowatt.bike/fr"),("Wildtrails","https://www.wildtrails.be/"),("Brandsport","https://www.brandsport.be/"),("Ardenne Aventures","https://ardenneaventures.com/"),("Trott-e-Trail","https://www.trott-e-trail.com/"))),
    ("act_family", (("Syndicat d’Initiative de La Roche-en-Ardenne","https://www.la-roche-tourisme.com/"),("Château féodal de La Roche-en-Ardenne","https://www.chateaudelaroche.be/"),("Parc à Gibier","https://www.parc-gibier-laroche.be/"),("Grottes de Hotton","https://grottesdehotton.be/"),("Parc Chlorophylle","https://www.parcchlorophylle.com/"),("Houtopia","https://www.houtopia.be/"),("Brasserie d'Achouffe","https://chouffe.com/"))),
)


def activities(lang):
    groups=""
    for key, places in ACTIVITIES:
        groups += f'<section><h2>{text(key,lang)}</h2><div class="link-grid">' + "".join(f'<a class="place" href="{href}" rel="noopener noreferrer"><strong>{name}</strong><span>{text("official_site",lang)} →</span></a>' for name,href in places) + '</div></section>'
    return hero(lang, text("nav_activities",lang), text("activities_hero",lang), text("activities_intro",lang), "facilities") + f'<div id="content" class="activities container">{groups}<p class="notice">{text("activity_conditions",lang)}</p></div>'


def legal(lang):
    return f'''<section class="text-page container" id="content"><p class="eyebrow">PREPINSON</p><h1>{text('legal_heading',lang)}</h1><h2>{text('legal_company',lang)}</h2><p>Haras de Prepinson<br>Ortho 24, 6983 La Roche-en-Ardenne, Belgium<br>BCE 0699571027 · VAT BE 0699.571.027<br><a href="mailto:haras@prepinson.com">haras@prepinson.com</a> · <a href="tel:+32470851310">+32 470 85 13 10</a></p><p class="notice">{text('legal_pending',lang)}</p><h2>{text('legal_host',lang)}</h2><p>Netlify, Inc. · 44 Montgomery Street, Suite 300, San Francisco, California 94104, USA.</p><h2>{text('legal_ip',lang)}</h2><p>{text('legal_ip_copy',lang)}</p></section>'''


def privacy(lang):
    sections=(("privacy_collect","privacy_collect_copy"),("privacy_basis","privacy_basis_copy"),("privacy_processors","privacy_processors_copy"),("privacy_rights","privacy_rights_copy"))
    return f'<section class="text-page container" id="content"><p class="eyebrow">PREPINSON</p><h1>{text("privacy_heading",lang)}</h1>' + "".join(f'<h2>{text(a,lang)}</h2><p>{text(b,lang)}</p>' for a,b in sections) + f'<h2>{text("privacy_language",lang)}</h2><p>{text("privacy_language_copy",lang)}</p></section>'


BUILDERS={"":home,"horses":horses,"horses/programmes":programmes,"horses/facilities":facilities,"horses/for-sale":sales,"horses/references":references,"houses":houses,"activities":activities,"legal":legal,"privacy":privacy}


def breadcrumbs(lang, route):
    if not route: return ""
    parts=route.split("/"); items=[f'<a href="{url(lang)}">{text("nav_home",lang)}</a>']; cur=[]
    label_map={"horses":"nav_horses","programmes":"nav_programmes","facilities":"nav_facilities","for-sale":"nav_sales","references":"service_references","houses":"nav_houses","activities":"nav_activities","legal":"footer_legal","privacy":"footer_privacy"}
    for p in parts:
        cur.append(p); label=text(label_map[p],lang) if p in label_map else ("Ortho 24" if p=="ortho-24" else "Ortho 25")
        items.append(f'<a href="{url(lang,"/".join(cur))}">{label}</a>')
    return '<nav class="breadcrumbs container" aria-label="Breadcrumb">'+'<span aria-hidden="true">/</span>'.join(items)+'</nav>'


def schema(lang, route, title, description):
    page_url=DOMAIN+url(lang,route)
    org={"@type":"Organization","@id":DOMAIN+"/#organization","name":"Haras de Prepinson","url":DOMAIN+url(lang),"logo":{"@type":"ImageObject","url":ASSET_DOMAIN+"/assets/logo.png"},"email":"haras@prepinson.com","telephone":"+32470851310","sameAs":[IG_HARAS,IG_HOUSE]}
    place={"@type":"LocalBusiness","@id":DOMAIN+"/#haras","name":"Haras de Prepinson","url":DOMAIN+url(lang,"horses"),"image":ASSET_DOMAIN+"/assets/og-prepinson.jpg","address":{"@type":"PostalAddress","streetAddress":"Ortho 24","postalCode":"6983","addressLocality":"La Roche-en-Ardenne","addressCountry":"BE"},"geo":{"@type":"GeoCoordinates","latitude":50.1284709,"longitude":5.6128915},"sameAs":[IG_HARAS,MAP_HARAS],"parentOrganization":{"@id":DOMAIN+"/#organization"}}
    lodging={"@type":"LodgingBusiness","@id":DOMAIN+"/#houses","name":"Prepinson The House","url":DOMAIN+url(lang,"houses"),"image":ASSET_DOMAIN+"/assets/house-hero-1200.webp","email":"thehouse@prepinson.com","address":{"@type":"PostalAddress","streetAddress":"Ortho 24","postalCode":"6983","addressLocality":"La Roche-en-Ardenne","addressCountry":"BE"},"geo":{"@type":"GeoCoordinates","latitude":50.126626,"longitude":5.6133845},"sameAs":[IG_HOUSE,MAP_HOUSE,CASA,AIRBNB],"parentOrganization":{"@id":DOMAIN+"/#organization"}}
    web={"@type":"WebPage","@id":page_url+"#webpage","url":page_url,"name":title,"description":description,"inLanguage":lang,"isPartOf":{"@id":DOMAIN+"/#website"}}
    return {"@context":"https://schema.org","@graph":[org,place,lodging,{"@type":"WebSite","@id":DOMAIN+"/#website","url":DOMAIN,"name":"Prepinson","publisher":{"@id":DOMAIN+"/#organization"}},web]}


def render(lang, route):
    title=text(META[route][0],lang); desc=text(META[route][1],lang); canonical=DOMAIN+url(lang,route)
    alts="".join(f'<link rel="alternate" hreflang="{code}" href="{DOMAIN+url(code,route)}">' for code in LANGS)
    xdefault=DOMAIN+("/" if not route else url("en",route))
    if route.startswith("houses/"): content=house(lang,route.rsplit("/",1)[1])
    else: content=BUILDERS[route](lang)
    body=header(lang,route)+breadcrumbs(lang,route)+f'<main id="main">{content}</main>'+footer(lang)
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(desc)}"><meta name="theme-color" content="#183b32"><link rel="canonical" href="{canonical}">{alts}<link rel="alternate" hreflang="x-default" href="{xdefault}"><meta property="og:type" content="website"><meta property="og:site_name" content="Prepinson"><meta property="og:locale" content="{lang}"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ASSET_DOMAIN}/assets/og-prepinson.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title)}"><meta name="twitter:description" content="{escape(desc)}"><meta name="twitter:image" content="{ASSET_DOMAIN}/assets/og-prepinson.jpg"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/styles.css"><script type="application/ld+json">{json.dumps(schema(lang,route,title,desc),ensure_ascii=False)}</script><script src="/app.js" defer></script></head><body>{body}</body></html>'''


def gateway():
    links="".join(f'<a href="/{code}/" lang="{code}" hreflang="{code}">{name}</a>' for code,name in LANGUAGE_NAMES.items())
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><title>Prepinson — Choose your language</title><link rel="stylesheet" href="/styles.css"><link rel="icon" href="/favicon.svg" type="image/svg+xml"></head><body class="gateway"><main><img src="/assets/logo-mark.png" width="260" height="260" alt="Haras de Prepinson"><h1>Choose your language</h1><nav aria-label="Language">{links}</nav><p>Your language is selected automatically on the hosted website.</p></main></body></html>'''


def build():
    for child in list(OUT.iterdir()):
        if child.name in {"assets","styles.css","app.js","favicon.svg"}: continue
        shutil.rmtree(child) if child.is_dir() else child.unlink()
    (OUT/"index.html").write_text(gateway(),encoding="utf-8")
    for lang in LANGS:
        for route in ROUTES:
            target=OUT/lang/route/"index.html" if route else OUT/lang/"index.html"
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(render(lang,route),encoding="utf-8")
    entries=[]
    for route in ROUTES:
        for lang in LANGS:
            loc=DOMAIN+url(lang,route)
            alternates="".join(f'<xhtml:link rel="alternate" hreflang="{code}" href="{DOMAIN+url(code,route)}"/>' for code in LANGS)
            xdefault=DOMAIN+("/" if not route else url("en",route))
            entries.append(f'<url><loc>{loc}</loc>{alternates}<xhtml:link rel="alternate" hreflang="x-default" href="{xdefault}"/></url>')
    (OUT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+''.join(entries)+'</urlset>',encoding="utf-8")
    (OUT/"robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n',encoding="utf-8")
    (OUT/"_redirects").write_text('/horses /en/horses/ 301\n/horses/* /en/horses/:splat 301\n/houses /en/houses/ 301\n/houses/* /en/houses/:splat 301\n',encoding="utf-8")
    preview_header = "  X-Robots-Tag: noindex, nofollow, noarchive\n" if os.environ.get("PREVIEW_MODE") == "true" else ""
    (OUT/"_headers").write_text("/*\n" + preview_header + "  X-Content-Type-Options: nosniff\n", encoding="utf-8")
    print(f"Generated {len(LANGS)*len(ROUTES)} localized pages plus language gateway")


if __name__ == "__main__":
    build()
