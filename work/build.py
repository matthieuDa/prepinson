#!/usr/bin/env python3
"""Generate the multilingual Prepinson site with the approved V1 presentation."""

from html import escape
from pathlib import Path
import json
import hashlib
import re
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.site_data import FACILITY_FACTS, HOUSE_FACTS, LANGS, LANGUAGE_NAMES, ROUTES, TEXT, text  # noqa: E402
from src.client_content import HORSE_DISCIPLINES, HORSE_STORIES, PEDIGREES
from src.release_content import SALES_REFERENCES
from src.navigation import menu, breadcrumbs, crumbs
from src.legacy_routes import render_redirects
from src.presentation_data import MEDIA, PROPERTIES, GALLERY_ALT, ui, v1  # noqa: E402

try:
    from src.forms import render_confirmation, render_contact, render_dialogs as forms_dialogs, render_footer  # type: ignore  # noqa: E402
except ImportError:
    render_confirmation = render_contact = render_footer = None
    forms_dialogs = None

try:
    from src.activity_data import ACTIVITY_GROUPS, ACTIVITIES, activity_copy  # type: ignore  # noqa: E402
except ImportError:
    from src.presentation_data import ACTIVITIES as _ACTIVITIES  # noqa: E402
    ACTIVITY_GROUPS = tuple((key.removeprefix("act_"), key) for key, _ in _ACTIVITIES)
    ACTIVITIES = {key: tuple({"name": name, "url": link} for name, link in values) for key, values in _ACTIVITIES}
    def activity_copy(item, lang):
        return ""


OUT = ROOT / "dist"
DOMAIN = (os.environ.get("SITE_URL") or os.environ.get("URL") or "https://prepinson.netlify.app").rstrip("/")
PREVIEW_MODE = os.environ.get("PREVIEW_MODE") == "true"
ASSET_DOMAIN = os.environ.get("DEPLOY_PRIME_URL", DOMAIN).rstrip("/") if PREVIEW_MODE else DOMAIN
IG_HARAS = "https://www.instagram.com/haras_de_prepinson/"
IG_HOUSE = "https://www.instagram.com/prepinson_houses/"
MAP_HARAS = "https://maps.app.goo.gl/qU2NuF7tHseKitHJ6"
MAP_HOUSE = "https://maps.app.goo.gl/FzkorC926XiJ6Fzw7"
ASSET_VERSION = hashlib.sha256(b"".join((ROOT / name).read_bytes() for name in ("src/client_content.py", "src/release_content.py", "src/legal_content.py", "src/navigation.py", "src/styles.css", "src/navigation-refined.css", "src/fonts.css", "src/app.js", "src/site_data.py", "src/presentation_data.py", "src/form_data.py", "src/forms.py", "src/activity_data.py", "src/image-manifest.json", "src/designs/refinement.css", "src/designs/equilibre.css", "src/designs/refinement.js", "src/designs/illustrations/haras.webp", "src/designs/illustrations/horses.webp", "src/designs/illustrations/houses.webp", *(f"src/designs/assets/{name}.webp" for name in ("sales", "grevlunda", "prevet", "njoy", "equilannoo")), "work/build.py"))).hexdigest()[:12]

META = {
    "team": ("team_title", "team_desc"),
    "horses/boarding": ("boarding_title", "boarding_desc"),
    "contact": ("contact_page_title", "contact_page_desc"),
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
    "partners": ("partners_title", "partners_desc"),
    "legal": ("legal_title", "legal_desc"),
    "privacy": ("privacy_title", "privacy_desc"),
}

IMAGE_DIMS = {
    "hero-horses-2000.webp": (2000, 1333), "training-2000.webp": (2000, 1290),
    "facilities-2000.webp": (2000, 1333), "house-hero-2000.webp": (2000, 1333),
    "prepinson-horse-handler-outdoors.webp": (960, 640), "prepinson-stables-flowers.webp": (960, 640),
    "prepinson-show-jumping-training.webp": (960, 640), "prepinson-mare-and-foal.webp": (960, 640),
    "prepinson-ortho-25-garden-terrace.webp": (1200, 800), "eva-schiller.jpg": (960, 1200),
    "nicolas-derouault.jpg": (960, 1200),
}
IMAGE_MANIFEST_PATH = ROOT / "src/image-manifest.json"
IMAGE_MANIFEST = json.loads(IMAGE_MANIFEST_PATH.read_text(encoding="utf-8")) if IMAGE_MANIFEST_PATH.exists() else {}


def tx(key, lang, fallback=None):
    if key in TEXT:
        return text(key, lang)
    if fallback and fallback in TEXT:
        return text(fallback, lang)
    return fallback or key.replace("_", " ").capitalize()


def url(lang, route=""):
    return f"/{lang}/" + (route.strip("/") + "/" if route else "")


def facility_values(lang):
    indoor = FACILITY_FACTS["indoor"]
    outdoor = FACILITY_FACTS["outdoor"]
    estate = FACILITY_FACTS["estate"]
    return (
        (str(FACILITY_FACTS["sport_boxes"]), tx("stat_boxes", lang)),
        (str(FACILITY_FACTS["breeding_boxes"]), tx("stat_breeding", lang)),
        (f'{indoor["width"]} × {indoor["length"]} {indoor["unit"]}', tx("stat_indoor", lang)),
        (f'{outdoor["width"]} × {outdoor["length"]} {outdoor["unit"]}', tx("stat_outdoor", lang)),
        (f'{estate["value"]} {estate["unit"]}', tx("stat_land", lang)),
    )


def stat_strip(lang, light=False):
    return '<div class="stat-strip' + (' light' if light else '') + '">' + ''.join(
        f'<div><b>{value}</b><span>{label}</span></div>' for value, label in facility_values(lang)
    ) + '</div>'


def icon(name):
    return f'<svg class="icon icon-{name}" aria-hidden="true" focusable="false"><use href="/icons.svg#{name}"></use></svg>'


def headline(value):
    """Apply the V1 italic accent to the last word without changing its text."""
    words = value.rsplit(" ", 1)
    return escape(value) if len(words) == 1 else f'{escape(words[0])} <em>{escape(words[1])}</em>'


def display_title(value):
    """Render an editorial title using a clear line break instead of punctuation."""
    first, separator, second = value.partition("\n")
    return escape(first) + (f'<br><em>{escape(second)}</em>' if separator else "")


def image(name, alt, *, cls="", hero=False, width=None, height=None, position="", sizes=None):
    manifest = IMAGE_MANIFEST.get(name, {})
    width = manifest.get("width", IMAGE_DIMS.get(name, (width or 1200, height or 800))[0])
    height = manifest.get("height", IMAGE_DIMS.get(name, (width or 1200, height or 800))[1])
    loading = 'fetchpriority="high"' if hero else 'loading="lazy" decoding="async"'
    fallback = f'<img class="{cls}" src="/assets/{name}?v={ASSET_VERSION}" width="{width}" height="{height}" style="object-position:{position or "center"}" alt="{escape(re.sub(r"<[^>]+>", " ", alt))}" {loading}>'
    variants = manifest.get("variants", ())
    if not variants:
        return fallback
    srcset = ", ".join(f'{variant["src"]}?v={ASSET_VERSION} {variant["width"]}w' for variant in variants)
    responsive_sizes = sizes or ("(max-width: 700px) 1000px, 100vw" if hero else "(max-width: 700px) 88vw, 43vw")
    avif_srcset = srcset.replace(".webp", ".avif")
    mobile_sources = ""
    mobile_variants = IMAGE_MANIFEST.get(manifest.get("mobileImage"), {}).get("variants", manifest.get("mobile", ()))
    if hero and mobile_variants:
        mobile_webp = ", ".join(f'{item["src"]}?v={ASSET_VERSION} {item["width"]}w' for item in mobile_variants)
        mobile_avif = mobile_webp.replace(".webp", ".avif")
        mobile_sources = f'<source media="(max-width: 600px) and (orientation: portrait)" type="image/avif" srcset="{mobile_avif}" sizes="100vw"><source media="(max-width: 600px) and (orientation: portrait)" type="image/webp" srcset="{mobile_webp}" sizes="100vw">'
    return f'<picture>{mobile_sources}<source type="image/avif" srcset="{avif_srcset}" sizes="{responsive_sizes}"><source type="image/webp" srcset="{srcset}" sizes="{responsive_sizes}">{fallback}</picture>'


def responsive_image(stem, alt, *, cls="", hero=False, sizes=None, position=""):
    cover_sizes = sizes or ("(max-width: 700px) 1350px, 100vw" if stem == "hero-horses" and hero else "(max-width: 700px) 1000px, 100vw" if hero else "100vw")
    return image(f"{stem}-2000.webp", alt, cls=cls, hero=hero, sizes=cover_sizes, position=position)


def language_switch(lang, route):
    options = "".join(
        f'<a href="{url(code, route)}" lang="{code}" hreflang="{code}" data-language="{code}"' +
        (' aria-current="true"' if code == lang else "") + f'><span>{code.upper()}</span>{LANGUAGE_NAMES[code]}</a>'
        for code in LANGS
    )
    return f'<details class="language-switch"><summary aria-label="{escape(tx("language", lang))}: {escape(LANGUAGE_NAMES[lang])}"><span>{lang.upper()}</span>{icon("chevron-down")}</summary><nav aria-label="{escape(tx("language", lang))}" class="language-options">{options}</nav></details>'


def header(lang, route, solid=False):
    home = url(lang)
    links = menu(lang, route)
    cls = "nav solid-nav" if solid else "nav"
    brand = f'<a class="brand" href="{home}"><img src="/assets/logo.png?v={ASSET_VERSION}" width="260" height="260" alt=""><span class="wordmark">PREPINSON <small>HARAS DE PREPINSON</small></span></a>'
    return f'<a class="skip-link" href="#main">{tx("skip", lang)}</a><header class="{cls}">{brand}<nav class="navlinks" aria-label="{tx("menu", lang)}">{links}</nav>{language_switch(lang, route)}<button class="menu-toggle" data-menu-toggle data-open-label="{tx("menu",lang)}" data-close-label="{tx("close",lang)}" aria-label="{tx("menu",lang)}" type="button" aria-expanded="false" aria-controls="mobile-menu"><span>{tx("menu", lang)}</span>{icon("menu")}</button></header><noscript><style>.menu-toggle{{display:none}}@media(max-width:1250px){{.mobile-nav{{position:relative;inset:auto;transform:none;visibility:visible;max-height:none;z-index:1;margin-top:110px}}.solid-nav~.mobile-nav{{margin-top:0}}}}@media(max-width:700px){{.mobile-nav{{margin-top:85px}}}}</style></noscript><nav id="mobile-menu" class="mobile-nav" aria-label="{tx("menu", lang)}">{links}<small>ORTHO · ARDENNES</small></nav>'



def editorial_link(href, label, dark=True, **attrs):
    extras = " ".join(f'{key.replace("_", "-")}="{escape(str(value))}"' for key, value in attrs.items())
    cls = "editorial-link dark-link" if dark else "editorial-link"
    return f'<a class="{cls}" href="{href}" {extras}>{label}<span>{icon("arrow-up-right")}</span></a>'


def inner_hero(lang, eyebrow, title, intro, media, *, booking=None, position="center", title_html=None):
    alt = ui({"training": "alt_training", "facilities": "alt_facilities", "house-hero": "alt_houses", "hero-horses-2000.webp": "alt_hero"}.get(media, "alt_houses"), lang)
    if media in GALLERY_ALT: alt = GALLERY_ALT[media][lang]
    visual = responsive_image(media, alt, cls="hero-media", hero=True, position=position) if media in {"training", "facilities", "house-hero"} else image(media, alt, cls="hero-media", hero=True, position=position, sizes="(max-width: 700px) max(825px, 105svh), 100vw" if media == "cottage.jpg" else None)
    action = f'<a class="btn light" href="{booking}" target="_blank" rel="noopener noreferrer">{ui("check_availability", lang)} {icon("arrow-up-right")}</a>' if booking else ""
    return f'<section class="hero inner-hero">{visual}<div class="hero-shade"></div><div class="hero-content reveal"><p class="eyebrow">{eyebrow}</p><h1>{title_html or escape(title)}</h1><p>{intro}</p>{action}</div><div class="hero-bottom"><span class="location">{ui("location", lang)}</span><a class="scroll-link" href="#discover">{ui("scroll", lang)} <span>{icon("arrow-down")}</span></a></div></section>'


def home(lang):
    expert = (
        ("01", "boarding", ui("boarding_title", lang), ui("boarding_copy", lang), "boarding"),
        ("02", "training", ui("training_title", lang), ui("training_copy", lang), "training"),
        ("03", "breeding", ui("breeding_title", lang), ui("breeding_copy", lang), "breeding"),
        ("04", "sales", tx("nav_sales", lang), tx("sales_message", lang), "sales"),
    )
    cards = "".join(f'<a class="expertise-card" href="{url(lang, "horses/for-sale") if target == "sales" else url(lang, "horses") + "#" + target}"><div class="expertise-image">{image("sales.webp" if media == "sales" else MEDIA[media], tx("sales_heading", lang) if media == "sales" else ui("alt_" + media, lang))}</div><div class="expertise-content"><span class="expertise-number">{number}</span><h3>{title}</h3><div class="expertise-detail"><div><p>{copy}</p></div></div><span class="expertise-arrow">{icon("arrow-up-right")}</span></div></a>' for number, media, title, copy, target in expert)
    refs = "".join(f'<a href="{url(lang, "horses/references")}#{slug}"><span class="pedigree-year">0{i}</span><div><h3>{display_title(tx(f"{slug}_title", lang))}</h3></div><span class="pedigree-arrow">{icon("arrow-up-right")}</span></a>' for i, slug in enumerate(HORSE_STORIES, 1))
    people = (("team_eva", "Eva Schiller", ui("eva_role", lang), "eva.schiller@prepinson.com", "+352 691 22 38 36"), ("team_nicolas", "Nicolas Derouault", ui("nicolas_role", lang), "nicolas.derouault@prepinson.com", "+32 470 85 13 10"))
    team = "".join(f'<article class="team-card">{image(MEDIA[media], name)}<div><p class="eyebrow">{role}</p><h3>{name}</h3><a href="mailto:{email}">{email} {icon("arrow-up-right")}</a><a href="tel:{phone.replace(" ", "")}">{phone}</a></div></article>' for media, name, role, email, phone in people)
    return f'''
<section class="haras-hero">{responsive_image("hero-horses", ui("alt_hero", lang), cls="haras-hero-photo", hero=True, position="center 45%")}
<div class="haras-hero-overlay"></div><div class="hero-editorial"><p class="eyebrow">{v1("home_eyebrow", lang)}</p><h1>{v1("home_hero", lang)}</h1><div class="hero-intro-line"><span>{v1("home_tagline", lang)}</span>{editorial_link("#haras", ui("hero_cta", lang), dark=False)}</div></div>
<div class="hero-baseline"><span>{ui("location", lang)}</span><span>{v1("home_services_line", lang)}</span><a href="#haras">{ui("scroll", lang)} <span>{icon("arrow-down")}</span></a></div></section>
<section id="haras" class="haras-intro container"><div class="intro-label"><span class="eyebrow">{ui("intro_label", lang)}</span><span class="tiny-serif">01</span></div><div class="haras-intro-copy"><h2>{v1("home_intro_title", lang)}</h2><p>{v1("home_intro", lang)}</p><p>{v1("home_intro_programmes", lang)}</p><p class="quiet-copy">{v1("home_intro_secondary", lang)}</p>{editorial_link(url(lang, "horses"), v1("home_intro_link", lang))}</div><figure class="intro-portrait">{image(MEDIA["intro"], GALLERY_ALT[MEDIA["intro"]][lang], position="45% 50%") }<figcaption>{ui("intro_note", lang)}</figcaption></figure></section>
<section id="expertise" class="expertise-section"><div class="container"><div class="expertise-heading"><p class="eyebrow">{ui("expertise_label", lang)}</p><h2>{v1("expertise_title", lang)}</h2><p>{v1("expertise_intro", lang)}</p></div><div class="expertise-grid">{cards}</div></div></section>
<section class="facilities-home"><div class="haras-landscape">{responsive_image("facilities", ui("alt_facilities", lang), position="center 45%")}<div class="landscape-caption"><span class="eyebrow">{tx("facilities_hero", lang)}</span>{editorial_link(url(lang, "horses/facilities"), ui("facilities_cta", lang), dark=False)}</div></div>{stat_strip(lang)}</section>
<section class="selected-section container"><div class="selected-heading"><p class="eyebrow">{ui("references_label", lang)}</p><h2>{tx("references_hero", lang)}</h2><p>{tx("service_references_copy", lang)}</p>{editorial_link(url(lang, "horses/references"), tx("service_references", lang))}</div><div class="pedigree-list">{refs}</div></section>
<section id="team" class="team-section"><div class="container"><div class="team-heading"><p class="eyebrow">{ui("team_label", lang)}</p><h2>{v1("team_title", lang)}</h2><p>{v1("team_intro", lang)}</p></div><div class="team-grid">{team}</div>{editorial_link(url(lang,"team"), tx("all_team",lang))}</div></section>
<section class="home-houses"><div class="estate-grid container"><div class="estate-photo">{responsive_image("house-hero", ui("alt_houses", lang))}</div><div class="estate-copy"><p class="eyebrow">{ui("houses_label", lang)}</p><h2>{tx("houses_teaser_title", lang)}</h2><p>{ui("houses_home_copy", lang)}</p>{editorial_link(url(lang, "houses"), ui("houses_cta", lang))}</div></div></section>
<section id="journal" class="journal-stories container"><div class="section-head"><div><p class="eyebrow">{ui("journal_label", lang)}</p><h2>{v1("journal_title", lang)}</h2></div><p class="journal-intro">{v1("journal_intro", lang)}</p></div><div id="instagram-feed" class="instagram-feed" role="region" aria-label="Instagram · Haras de Prepinson" aria-live="polite"></div><button type="button" class="instagram-retry" data-instagram-retry hidden>{ui("instagram_retry", lang)}</button><p class="instagram-fallback">{editorial_link(IG_HARAS, ui("instagram_fallback", lang), target="_blank", rel="noopener noreferrer")}</p></section>'''


def team_album(lang):
    group = "prepinson-team-portrait.webp"
    group_alt = GALLERY_ALT[group][lang]
    photos = tuple((name, GALLERY_ALT[name][lang]) for name in ("prepinson-team-arena.webp", "prepinson-horse-care.webp", "prepinson-young-horse.webp", "prepinson-pastures.webp", "prepinson-rider-detail.webp"))
    return f'''<div class="team-album"><h3>{ui("team_gallery_title", lang)}</h3><button class="team-group-photo" type="button" data-lightbox-item="0" data-lightbox-src="/assets/{group}?v={ASSET_VERSION}" aria-label="{escape(ui("gallery_label", lang) + ": " + group_alt)}">{image(group, group_alt, sizes="86vw")}</button><details class="team-gallery-more"><summary>{ui("team_gallery_link", lang)} {icon("plus")}</summary>{gallery(photos, lang)}</details></div>'''


def horses(lang):
    sections = (("boarding", "01", ui("boarding_title", lang), ui("boarding_copy", lang), MEDIA["boarding"], "horses/boarding", tx("nav_boarding", lang)), ("training", "02", ui("training_title", lang), ui("training_copy", lang), MEDIA["training"], "horses/programmes", tx("nav_programmes", lang)), ("breeding", "03", ui("breeding_title", lang), ui("breeding_copy", lang), MEDIA["breeding"], "horses/references", tx("service_references", lang)))
    body = inner_hero(lang, v1("home_eyebrow", lang), tx("horses_hero", lang), v1("horses_tagline", lang), "training", title_html=v1("horses_hero", lang)) + f'<section id="discover" class="intro container"><div><p class="eyebrow">{tx("world_horses", lang)}</p><h2>{ui("horses_intro_first", lang)}<br><em>{ui("horses_intro_second", lang)}</em></h2></div><p class="body-copy">{tx("horses_intro", lang)}</p></section><section class="service-stories container">'
    for anchor, number, title, copy, media, route, cta in sections:
        body += f'<article id="{anchor}" class="service-story"><div class="service-story-image">{image(media, ui("alt_" + anchor, lang))}</div><div><p class="eyebrow">{number} / {title}</p><h2>{title}</h2><p>{copy}</p>{editorial_link(url(lang, route), cta)}</div></article>'
    return body + f'<article id="sales" class="service-story"><div class="service-story-image">{image("sales.webp",tx("sales_heading",lang),width=1200,height=1801)}</div><div><p class="eyebrow">04 / {tx("sales_heading",lang)}</p><h2>{tx("sales_range",lang)}</h2><p>{tx("sales_message",lang)}</p><p><a class="text-link" href="mailto:sales@prepinson.com">sales@prepinson.com</a></p>{editorial_link(url(lang,"horses/for-sale"),tx("nav_sales",lang))}</div></article></section>' + sales_references(lang) + f'<section class="container reference-invitation"><h2>{tx("references_hero",lang)}</h2>{editorial_link(url(lang,"horses/references"),tx("nav_references",lang))}</section><section class="horses-team-gallery container" id="team-gallery">{team_album(lang)}{editorial_link(url(lang,"team"),tx("all_team",lang))}</section>'



def programmes(lang):
    subjects = ("programme-foal", "programme-pre-breaking", "programme-breaking", "programme-jumping")
    panels = "".join(f'<details name="programmes"' + (' open' if i == 1 else '') + f'><summary><span class="programme-number">0{i}</span><span>{tx(f"p{i}_title", lang)}</span><span class="programme-toggle">{icon("plus")}</span></summary><div class="programme-panel"><p><strong>{tx(f"p{i}_timing", lang)}</strong></p><p>{tx(f"p{i}_copy", lang)}</p><a class="text-link" href="#contact" data-contact-subject="{subjects[i - 1]}">{ui("programme_cta", lang)} {icon("arrow-up-right")}</a></div></details>' for i in range(1, 5))
    return inner_hero(lang, tx("nav_programmes", lang), tx("programmes_hero", lang), tx("programmes_intro", lang), "training") + f'<section id="discover" class="programmes-section container"><div class="programmes-heading"><p class="eyebrow">{tx("nav_programmes", lang)}</p><h2>{ui("programmes_list_title", lang)}</h2></div><div class="programme-list" data-exclusive-details>{panels}</div></section>'


def gallery(items, lang):
    buttons = "".join(f'<button type="button" data-lightbox-item="{i}" data-lightbox-src="/assets/{name}?v={ASSET_VERSION}" aria-label="{escape(ui("gallery_label", lang))}: {escape(alt)}">{image(name, alt, sizes="(max-width: 700px) 43vw, 28vw")}</button>' for i, (name, alt) in enumerate(items))
    return f'<div class="gallery" aria-label="{escape(ui("gallery_label", lang))}">{buttons}</div>'


def facilities(lang):
    gallery_items = (("prepinson-indoor-riding-arena.webp", ui("alt_indoor", lang)), ("prepinson-outdoor-jumping-arena.webp", ui("alt_training", lang)), ("prepinson-outdoor-arena.webp", ui("alt_outdoor", lang)), ("prepinson-horses-green-paddocks.webp", ui("alt_paddocks", lang)), ("prepinson-rider-saddle-detail.webp", ui("alt_saddle", lang)), ("prepinson-stables-flowers.webp", ui("alt_boarding", lang)))
    items = "".join(f'<li>{tx(key, lang)}</li>' for key in ("facility_equipment", "facility_club", "facility_breeding", "facility_trails"))
    return inner_hero(lang, tx("nav_facilities", lang), tx("facilities_hero", lang), tx("facilities_intro", lang), "facilities") + f'<section id="discover" class="facilities-detail container"><div class="section-head"><div><p class="eyebrow">{tx("stats_title", lang)}</p><h2>{ui("facilities_detail_title", lang)}</h2></div></div>{stat_strip(lang, light=True)}<div class="facilities-copy"><ul class="large-list">{items}</ul><div><p>Ortho 24<br>6983 La Roche-en-Ardenne<br>{ui("country", lang)}</p><p>{ui("transport_access", lang)}</p>{editorial_link("#contact", tx("nav_contact", lang))}{editorial_link(MAP_HARAS, tx("footer_maps_haras", lang), target="_blank", rel="noopener noreferrer")}</div></div>{gallery(gallery_items, lang)}</section>'


def sales(lang):
    return inner_hero(lang, tx("nav_sales", lang), tx("sales_hero", lang), tx("sales_message", lang), "hero-horses-2000.webp") + f'<section id="discover" class="sales-section container"><div><p class="eyebrow">{tx("sales_heading", lang)}</p><h2>{tx("sales_range", lang)}</h2><p>{tx("sales_cta", lang)}</p><p><a class="text-link" href="mailto:sales@prepinson.com">sales@prepinson.com</a></p><a class="btn dark" href="#contact" data-contact-subject="horse-search">{ui("sales_cta", lang)} {icon("arrow-up-right")}</a></div>{image("sales.webp", tx("sales_range", lang), width=1200, height=1801)}</section>' + sales_references(lang)



def reference_gallery(items, lang):
    """Align photographs by their native proportions without cropping or matting."""
    ratios = [IMAGE_MANIFEST[name]["width"] / IMAGE_MANIFEST[name]["height"] for name, _ in items]
    buttons = ""
    for i, ((name, alt), ratio) in enumerate(zip(items, ratios)):
        sizes = f"(max-width: 700px) 86vw, {72 * ratio / sum(ratios):.1f}vw"
        buttons += f'<button type="button" style="flex-grow:{ratio:.6f}" data-lightbox-item="{i}" data-lightbox-src="/assets/{name}?v={ASSET_VERSION}" aria-label="{escape(ui("enlarge", lang) + ": " + alt, quote=True)}">{image(name, alt, sizes=sizes)}</button>'
    return f'<div class="reference-gallery" role="group" aria-label="{escape(ui("gallery_label", lang))}">{buttons}</div>'


def references(lang):
    dalton_photos = ("dalton-falsterbo-dressage.webp", "dalton-falsterbo-finish.webp", "dalton-falsterbo-arena-entry.webp")
    dalton_gallery = '<div class="reference-media"><p class="eyebrow">' + escape(ui("dalton_gallery", lang)) + '</p>' + reference_gallery(tuple((name, GALLERY_ALT[name][lang]) for name in dalton_photos), lang) + '</div>'
    media = {
        "dalton": dalton_gallery,
        "juni": '<div class="reference-media">' + reference_gallery((("juni-stable.webp",ui("juni_photo",lang)),("juni-jumping.webp",ui("juni_jumping",lang))),lang) + f'<button type="button" class="film-button dark-film" data-video-open="/assets/juni-prepinson.mp4?v={ASSET_VERSION}" data-video-caption="Juni de Prepinson"><span class="circle">{icon("play")}</span>{escape(ui("juni_video", lang))}</button></div>',
        "jackson": '<div class="reference-media">' + reference_gallery((("jackson-standing.webp",ui("jackson_standing",lang)),("jackson-jumping.webp",ui("jackson_jumping",lang))),lang) + '</div>',
        "qurious": f'<div class="reference-media"><button type="button" class="film-button dark-film" data-video-open="/assets/qurious-hs.mp4?v={ASSET_VERSION}" data-video-caption="Qurious HS"><span class="circle">{icon("play")}</span>{escape(ui("qurious_video", lang))}</button></div>',

    }
    rows = "".join(
        f'<article id="{slug}" class="reference-story"><p class="eyebrow">0{i} / HARAS DE PREPINSON</p><h2>{display_title(tx(f"{slug}_title", lang))}</h2><div class="reference-facts"><p class="reference-pedigree"><span>{ui("reference_training", lang)}</span>{ui("reference_" + HORSE_DISCIPLINES[slug], lang)}</p><p class="reference-pedigree"><span>{ui("pedigree", lang)}</span>{escape(PEDIGREES[slug])}</p></div><div class="reference-story-copy"><p>{tx(f"{slug}_copy", lang)}</p></div>{media.get(slug, "")}</article>'
        for i, slug in enumerate(HORSE_STORIES, 1)
    )
    return inner_hero(lang, ui("references_selection_label", lang), tx("references_hero", lang), tx("references_intro", lang), "hero-horses-2000.webp") + f'<section id="discover" class="reference-stories container">{rows}</section>'


def property_card(lang, slug):
    prop = PROPERTIES[slug]
    facts = HOUSE_FACTS[slug]
    title = tx("ortho24_display_title" if slug == "ortho-24" else "ortho25_display_title", lang, "ortho24_title" if slug == "ortho-24" else "ortho25_title")
    description = v1("ortho24_copy" if slug == "ortho-24" else "ortho25_copy", lang)
    booking_label = ui("book_casapilot" if slug == "ortho-24" else "book_airbnb", lang)
    return f'<article class="property-card"><a class="property-image" href="{url(lang, "houses/" + slug)}">{image(prop["image"], title.replace(chr(10), " "))}</a><div class="property-info"><p class="eyebrow">ORTHO · ARDENNES</p><h3>{display_title(title)}</h3><div class="property-meta"><span>{facts["guests"]} {tx("guests", lang)}</span><span>{facts["bedrooms"]} {tx("bedrooms", lang)}</span><span>{facts["bathrooms"]} {tx("bathrooms", lang)}</span></div><p>{description}</p><div class="property-links"><a class="btn dark" href="{url(lang, "houses/" + slug)}">{tx("explore_house", lang)} {icon("arrow-up-right")}</a><a class="text-link" href="{prop["booking"]}" target="_blank" rel="noopener noreferrer">{booking_label} {icon("arrow-up-right")}</a></div></div></article>'


def houses(lang):
    return inner_hero(lang, ui("houses_label", lang), tx("houses_hero", lang), v1("houses_tagline", lang), "house-hero", title_html=v1("houses_hero", lang)) + f'<section id="discover" class="intro container"><div><p class="eyebrow">{ui("houses_label", lang)}</p><h2>{v1("houses_intro_title", lang)}</h2></div><p class="body-copy">{ui("houses_home_copy", lang)}</p></section><section class="property-grid container">{property_card(lang, "ortho-24")}{property_card(lang, "ortho-25")}</section><section class="estate-section"><div class="estate-grid container"><div class="estate-photo">{image("house-1.jpg", ui("location", lang))}</div><div class="estate-copy"><p class="eyebrow">{tx("nav_activities", lang)}</p><h2>{v1("houses_estate_title", lang)}</h2><p>{v1("houses_estate_copy", lang)}</p>{editorial_link(url(lang, "activities"), ui("activities_cta", lang))}</div></div></section><section class="house-instagram"><div class="container"><div><p class="eyebrow">PREPINSON HOUSES</p><h2>{v1("houses_instagram_title", lang)}</h2></div><div><p>{v1("houses_instagram_copy", lang)}</p>{editorial_link(IG_HOUSE, "@prepinson_houses", target="_blank", rel="noopener noreferrer")}</div></div></section>'


def house(lang, slug):
    prop = PROPERTIES[slug]; is24 = slug == "ortho-24"
    facts = HOUSE_FACTS[slug]
    title = tx("ortho24_display_title" if is24 else "ortho25_display_title", lang, "ortho24_title" if is24 else "ortho25_title")
    description = v1("ortho24_copy" if is24 else "ortho25_copy", lang); other = "ortho-25" if is24 else "ortho-24"
    amenities = f'<span>{facts["guests"]} {tx("guests", lang)}</span><span>{facts["bedrooms"]} {tx("bedrooms", lang)}</span><span>{facts["bathrooms"]} {tx("bathrooms", lang)}</span>'
    amenities += "".join(f'<span>{ui(key, lang)}</span>' for key in (("pool", "hot_tub", "cinema") if is24 else ("garden", "kitchen", "parking")))
    film = f'<button type="button" data-video-open="/assets/house-film.mp4" class="film-button dark-film"><span class="circle">{icon("play")}</span>{ui("watch_film", lang)}</button>' if is24 else ""
    localized_gallery = tuple((name, GALLERY_ALT[name][lang]) for name, _ in prop["gallery"])
    booking_label = ui("book_casapilot" if is24 else "book_airbnb", lang)
    return inner_hero(lang, "ORTHO · " + ui("country", lang).upper(), title.replace("\n", " "), ui("ortho24_tag" if is24 else "ortho25_tag", lang), prop["image"], booking=prop["booking"], title_html=display_title(title)) + f'<section id="discover" class="property-detail container"><div class="property-summary"><div><p class="eyebrow">{ui("houses_label", lang)}</p><h2>{v1("house_detail_intro", lang)}</h2><p>{description}</p><div class="amenities">{amenities}</div></div><aside class="booking-panel"><h3>{ui("booking_title", lang)}</h3><p>{booking_label}</p><a class="btn dark" href="{prop["booking"]}" target="_blank" rel="noopener noreferrer">{booking_label} {icon("arrow-up-right")}</a><a class="text-link" href="#contact" data-contact-subject="{slug}">{tx("nav_contact", lang)} {icon("arrow-up-right")}</a></aside></div><div class="property-gallery-heading"><p class="eyebrow">{ui("gallery_label", lang)}</p><h2>{ui("gallery_title", lang)}</h2></div>{gallery(localized_gallery, lang)}</section><section class="property-film"><div class="container">{film}{editorial_link(url(lang, "activities"), ui("activities_cta", lang))}</div></section><section class="other-property container"><p class="eyebrow">{ui("other_house", lang)}</p>{property_card(lang, other)}</section>'


def activities(lang):
    groups = ""
    index_links = ""
    for group, label_key in ACTIVITY_GROUPS:
        items = ACTIVITIES[group] if isinstance(ACTIVITIES, dict) else [item for item in ACTIVITIES if item.get("group") == group]
        label = tx(label_key, lang)
        index_links += f'<a href="#activity-{group}">{escape(label)}</a>'
        cards = ""
        for item in items:
            name = item.get("name") or item.get("title"); href = item.get("url") or item.get("href"); copy = activity_copy(item, lang)
            cards += f'<article class="activity-source"><h3>{escape(name)}</h3>{f"<p>{escape(copy)}</p>" if copy else ""}<a class="text-link" href="{escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">{ui("official_link", lang)} {icon("arrow-up-right")}</a></article>'
        groups += f'<section id="activity-{group}" class="activity-chapter"><div class="activity-chapter-heading"><p class="eyebrow">{escape(ui("activities_guide_label", lang))}</p><h2>{escape(label)}</h2><p>{escape(ui("activity_" + group + "_intro", lang))}</p></div><div class="activity-source-list">{cards}</div></section>'

    house_cards = ""
    for slug, title_key in (("ortho-24", "ortho24_display_title"), ("ortho-25", "ortho25_display_title")):
        title = tx(title_key, lang, "ortho24_title" if slug == "ortho-24" else "ortho25_title")
        house_cards += f'<a class="activities-stay-card" href="{url(lang, "houses/" + slug)}">{image(PROPERTIES[slug]["image"], "", sizes="(max-width: 700px) 44vw, 28vw")}<span>{display_title(title)} {icon("arrow-up-right")}</span></a>'

    guide = f'''<article id="discover" class="activities-guide container">
  <header class="activities-guide-intro">
    <div><p class="eyebrow">{escape(ui("activities_guide_label", lang))}</p><h2>{escape(ui("activities_guide_title", lang))}</h2></div>
    <div class="activities-guide-intro-copy"><p>{escape(ui("activities_guide_intro", lang))}</p><nav class="activity-index" aria-label="{escape(ui('activities_guide_label', lang), quote=True)}">{index_links}</nav></div>
  </header>
  {groups}
  <p class="notice">{escape(tx("activity_conditions", lang))}</p>
</article>'''
    stay = f'''<section class="activities-stay" aria-labelledby="activities-stay-title">
  <div class="activities-stay-grid container">
    <div class="activities-stay-copy"><p class="eyebrow">{escape(ui("houses_label", lang))}</p><h2 id="activities-stay-title">{escape(ui("activities_stay_title", lang))}</h2><p>{escape(ui("activities_stay_copy", lang))}</p>{editorial_link(url(lang, "houses"), ui("houses_cta", lang), dark=False)}</div>
    <div class="activities-stay-images">{house_cards}</div>
  </div>
</section>'''
    return inner_hero(lang, tx("nav_activities", lang), tx("activities_hero", lang), tx("activities_intro", lang), "facilities") + guide + stay


def legal(lang):
    return f'<section class="text-page container" id="content"><p class="eyebrow">PREPINSON</p><h1>{tx("legal_heading", lang)}</h1><h2>{tx("legal_company", lang)}</h2><p>Haras de Prépinson SRL<br>{tx("legal_registration",lang)} : BE 0699.571.027<br>Ortho 24, 6983 La Roche-en-Ardenne, {ui("country", lang)}<br><a href="mailto:haras@prepinson.com">haras@prepinson.com</a> · <a href="tel:+32470851310">+32 470 85 13 10</a></p><h2>{tx("legal_creator",lang)}</h2><p><a href="https://unmissabl.com/">UNMISSABL · unmissabl.com</a></p><h2>{tx("legal_host", lang)}</h2><p>Netlify, Inc. · 44 Montgomery Street, Suite 300, San Francisco, California 94104, USA.</p><h2>{tx("legal_ip", lang)}</h2><p>{tx("legal_ip_copy", lang)}</p></section>'


def privacy(lang):
    sections = (("privacy_collect", "privacy_collect_copy"), ("privacy_basis", "privacy_basis_copy"), ("privacy_processors", "privacy_processors_copy"), ("privacy_newsletter", "privacy_newsletter_copy"), ("privacy_rights", "privacy_rights_copy"), ("privacy_language", "privacy_language_copy"), ("privacy_retention", "privacy_retention_copy"), ("privacy_transfers", "privacy_transfers_copy"), ("privacy_external", "privacy_external_copy"))
    return f'<section class="text-page container" id="content"><p class="eyebrow">PREPINSON</p><h1>{tx("privacy_heading", lang)}</h1><h2>{tx("privacy_controller",lang)}</h2><p>Haras de Prépinson SRL · BE 0699.571.027<br>Ortho 24, 6983 La Roche-en-Ardenne, {ui("country",lang)}<br><a href="mailto:haras@prepinson.com">haras@prepinson.com</a></p>' + "".join(f'<h2>{tx(a, lang)}</h2><p>{tx(b, lang)}</p>' for a, b in sections if a in TEXT) + '<p><a href="https://www.autoriteprotectiondonnees.be/">Autorité de protection des données · APD / GBA</a> · <a href="https://www.netlify.com/privacy/">Netlify</a> · <a href="https://www.netlify.com/pdf/netlify-dpa.pdf">Netlify DPA</a></p></section>'


def partners(lang):
    marks = (
        ("Grevlunda", "grevlunda.webp", "https://grevlunda.com/", "grevlunda", 500, 271),
        ("PreVet", "prevet.webp", "https://prevet.se/", "prevet", 1200, 675),
        ("nJoy Coaching", "njoy.webp", "https://njoycoaching.fr/", "njoy", 500, 849),
        ("Equilannoo", "equilannoo.webp", "https://equilannoo.eu/", "equilannoo", 900, 441),
    )
    cards = "".join(
        f'<a class="partner-card partner-{theme}" href="{site}" target="_blank" rel="noopener noreferrer" aria-label="{name} · {ui("official_link", lang)}">'
        f'<span class="partner-logo">{image(mark, name, width=width, height=height)}</span>'
        f'<span class="partner-caption"><strong>{name}</strong><span>{ui("official_link", lang)} {icon("arrow-up-right")}</span></span></a>'
        for name, mark, site, theme, width, height in marks
    )
    return f'<section class="partners-page container" id="content"><div class="partners-heading"><p class="eyebrow">PREPINSON</p><h1>{tx("nav_partners", lang)}</h1><p>{tx("partners_intro", lang)}</p></div><div class="partners-grid">{cards}</div></section>'


def sales_references(lang):
    rows = ''.join(f'<li><div><h3>{escape(name)}</h3><p>{escape(pedigree)}</p></div><span class="destination"><span aria-hidden="true">{flag}</span> {tx("country_"+country,lang)}</span></li>' for name,pedigree,country,flag in SALES_REFERENCES)
    return f'<section class="sales-references container" id="sales-references"><p class="eyebrow">{tx("sales_references",lang)}</p><h2>{tx("sales_world",lang)}</h2><ul>{rows}</ul></section>'


def team_page(lang):
    leaders = ((MEDIA['team_eva'],'Eva Schiller',ui('eva_role',lang),'eva.schiller@prepinson.com','+352 691 22 38 36'),(MEDIA['team_nicolas'],'Nicolas Derouault',ui('nicolas_role',lang),'nicolas.derouault@prepinson.com','+32 470 85 13 10'))
    cards = ''.join(f'<article class="team-card">{image(photo,name,hero=name == "Eva Schiller",sizes="(max-width:700px) 88vw, 43vw")}<div><p class="eyebrow">{role}</p><h2>{name}</h2><a href="mailto:{mail}">{mail}</a><a href="tel:{phone.replace(" ","")}">{phone}</a></div></article>' for photo,name,role,mail,phone in leaders)
    staff = ''.join(f'<article class="staff-card">{image(photo,name,sizes="(max-width:700px) 88vw, 28vw")}<h2>{name}</h2><p>{tx(role,lang)}</p></article>' for photo,name,role in (('steven-brunet.webp','Steven Brunet','steven_role'),('pierre-martin.webp','Pierre Martin','pierre_role'),('luc-canivet.webp','Luc Canivet','luc_role')))
    return f'<section class="team-page container"><div class="page-heading"><p class="eyebrow">HARAS DE PREPINSON</p><h1>{tx("nav_team",lang)}</h1><p>{ui("team_intro",lang)}</p></div><div class="team-grid">{cards}</div><div class="staff-grid">{staff}</div>{team_album(lang)}</section>'


def boarding_page(lang):
    return f'''<section class="boarding-page container"><div class="page-heading"><p class="eyebrow">{tx("nav_boarding",lang)}</p><h1>{tx("boarding_hero",lang)}</h1><p>{tx("boarding_desc",lang)}</p>{editorial_link('#contact',tx('boarding_cta',lang),data_contact_subject='boarding')}</div><div class="boarding-intro"><div>{image(MEDIA['boarding'],ui('alt_boarding',lang),hero=True,sizes='(max-width:700px) 88vw, 43vw')}</div><div><h2>{tx('boarding_daily',lang)}</h2><p>{tx('boarding_daily_copy',lang)}</p>{editorial_link(url(lang,'team'),tx('all_team',lang))}</div></div><div class="boarding-work"><h2>{tx('boarding_work',lang)}</h2><p>{tx('boarding_work_copy',lang)}</p><div class="related-links">{editorial_link(url(lang,'horses/facilities'),tx('nav_facilities',lang))}{editorial_link(url(lang,'horses/programmes'),tx('nav_training',lang))}</div></div>{stat_strip(lang)}</section>'''


def contact_page(lang):
    # This page is the form itself; avoid introductory cards repeating its actions.
    return render_contact(lang, "contact") if render_contact else fallback_contact(lang, "contact")


BUILDERS = {"team": team_page, "horses/boarding": boarding_page, "contact": contact_page, "": home, "horses": horses, "horses/programmes": programmes, "horses/facilities": facilities, "horses/for-sale": sales, "horses/references": references, "houses": houses, "activities": activities, "legal": legal, "privacy": privacy, "partners": partners}


def dialogs(lang):
    return f'<dialog class="dialog video-dialog" data-video-modal aria-label="{escape(ui("watch_film", lang))}"><button class="dialog-close" type="button" data-dialog-close aria-label="{escape(tx("close", lang))}">{icon("close")}</button><video controls playsinline preload="none"></video></dialog><dialog class="dialog lightbox" data-lightbox aria-label="{escape(ui("gallery_label", lang))}"><button class="dialog-close" type="button" data-dialog-close aria-label="{escape(ui("close_gallery", lang))}">{icon("close")}</button><img alt=""><div class="lightbox-controls"><button type="button" data-lightbox-prev aria-label="{escape(ui("previous", lang))}">{icon("arrow-left")}</button><span data-lightbox-label></span><button type="button" data-lightbox-next aria-label="{escape(ui("next", lang))}">{icon("arrow-right")}</button></div></dialog>'


def fallback_contact(lang, route):
    return f'<section id="contact" class="contact-section"><div class="container contact-layout"><div class="contact-copy"><p class="eyebrow">{tx("contact_eyebrow", lang)}</p><h2>{tx("contact_title", lang)}</h2><p>{tx("contact_copy", lang)}</p></div><form class="contact-form" name="contact-{lang}" method="POST" data-netlify="true"><input type="hidden" name="form-name" value="contact-{lang}"><label><span>{tx("form_name", lang)}</span><input name="name" required></label><label><span>{tx("form_email", lang)}</span><input type="email" name="email" required></label><label><span>{tx("form_message", lang)}</span><textarea name="message" required></textarea></label><button class="btn dark" type="submit">{tx("form_send", lang)}</button></form></div></section>'


def fallback_footer(lang, route):
    return f'<footer class="footer haras-footer"><div class="container"><div class="footer-invitation"><div><p class="eyebrow">PREPINSON</p><h2>{tx("newsletter_title", lang)}</h2></div><div class="footer-contact"><a href="mailto:haras@prepinson.com">haras@prepinson.com</a><a href="mailto:thehouse@prepinson.com">thehouse@prepinson.com</a><p>Ortho 24<br>6983 La Roche-en-Ardenne<br>Belgium</p></div></div><div class="footer-signature">PREPINSON</div><div class="footer-bottom"><span>© 2026 HARAS DE PREPINSON</span><a href="{url(lang, "legal")}">{tx("footer_legal", lang)}</a><a href="{url(lang, "privacy")}">{tx("footer_privacy", lang)}</a></div></div></footer>'


def schema(lang, route, title, description):
    page_url = DOMAIN + url(lang, route)
    org = {"@type": "Organization", "@id": DOMAIN + "/#organization", "name": "Haras de Prepinson", "url": DOMAIN + url(lang), "logo": {"@type": "ImageObject", "url": ASSET_DOMAIN + "/assets/logo.png"}, "email": "haras@prepinson.com", "telephone": "+32470851310", "sameAs": [IG_HARAS, IG_HOUSE]}
    place = {"@type": "LocalBusiness", "@id": DOMAIN + "/#haras", "name": "Haras de Prepinson", "url": DOMAIN + url(lang, "horses"), "image": ASSET_DOMAIN + "/assets/og-prepinson.jpg", "address": {"@type": "PostalAddress", "streetAddress": "Ortho 24", "postalCode": "6983", "addressLocality": "La Roche-en-Ardenne", "addressCountry": "BE"}, "geo": {"@type": "GeoCoordinates", "latitude": 50.1284709, "longitude": 5.6128915}, "sameAs": [IG_HARAS, MAP_HARAS], "parentOrganization": {"@id": DOMAIN + "/#organization"}}
    lodging = {"@type": "LodgingBusiness", "@id": DOMAIN + "/#houses", "name": "Prepinson The House", "url": DOMAIN + url(lang, "houses"), "image": ASSET_DOMAIN + "/assets/og-houses.jpg", "email": "thehouse@prepinson.com", "address": {"@type": "PostalAddress", "streetAddress": "Ortho 24", "postalCode": "6983", "addressLocality": "La Roche-en-Ardenne", "addressCountry": "BE"}, "geo": {"@type": "GeoCoordinates", "latitude": 50.126626, "longitude": 5.6133845}, "sameAs": [IG_HOUSE, MAP_HOUSE]}
    web = {"@type": "WebPage", "@id": page_url + "#webpage", "url": page_url, "name": title, "description": description, "inLanguage": lang, "isPartOf": {"@id": DOMAIN + "/#website"}}
    graph = [org, place, lodging, {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN, "name": "Prepinson", "publisher": {"@id": DOMAIN + "/#organization"}}, web]
    if route == "activities":
        graph.append({"@type": "Article", "@id": page_url + "#guide", "headline": title, "description": description, "inLanguage": lang, "mainEntityOfPage": {"@id": page_url + "#webpage"}, "publisher": {"@id": DOMAIN + "/#organization"}, "image": ASSET_DOMAIN + "/assets/og-houses.jpg"})
    if route.startswith("houses/"):
        prop = PROPERTIES[route.rsplit("/", 1)[1]]
        graph.append({"@type": "House", "@id": DOMAIN + "/#" + route.rsplit("/",1)[1], "identifier": route.rsplit("/",1)[1], "name": "La Grange" if route.endswith("ortho-24") else "Le Cottage", "url": page_url, "description": description, "image": [ASSET_DOMAIN + "/assets/" + item[0] for item in prop["gallery"]], "containsPlace": {"@type": "Accommodation", "occupancy": {"@type": "QuantitativeValue", "value": 8}, "numberOfBedrooms": prop["bedrooms"], "numberOfBathroomsTotal": prop["bathrooms"]}, "sameAs": [prop["booking"]]})
    if route:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [{"@type":"ListItem", "position":i, "name":name, "item":DOMAIN+target} for i,(name,target) in enumerate(crumbs(lang,route),1)]})
    if route == "team": web["@type"] = "AboutPage"
    if route == "contact": web["@type"] = "ContactPage"
    if route in {"horses/boarding","horses/programmes","horses/for-sale"}:
        graph.append({"@type":"Service","name":title.split(" | ")[0],"url":page_url,"description":description,"provider":{"@id":DOMAIN+"/#haras"}})
    return {"@context": "https://schema.org", "@graph": graph}


def render(lang, route):
    title, description = tx(META[route][0], lang), tx(META[route][1], lang); canonical = DOMAIN + url(lang, route)
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{DOMAIN + url(code, route)}">' for code in LANGS); xdefault = DOMAIN + ("/" if not route else url("en", route))
    content = house(lang, route.rsplit("/", 1)[1]) if route.startswith("houses/") else BUILDERS[route](lang)
    solid = route in {"legal", "privacy", "team", "contact", "horses/boarding", "partners"}
    content = breadcrumbs(lang,route) + content if solid else content.replace('</section>', '</section>' + breadcrumbs(lang,route), 1)
    contact = "" if route == "contact" else (render_contact(lang, route) if render_contact else fallback_contact(lang, route)); footer = render_footer(lang, route) if render_footer else fallback_footer(lang, route)
    body = header(lang, route, solid) + f'<main id="main">{content}{contact}</main>' + footer + (forms_dialogs(lang) if forms_dialogs else dialogs(lang))
    og_image = "og-houses.jpg" if route.startswith("houses") else "og-prepinson.jpg"
    ui_strings = json.dumps({"menu": tx("menu", lang), "close": tx("close", lang), "language": tx("language", lang)}, ensure_ascii=False)
    preview_class = ' class="is-preview"' if PREVIEW_MODE else ""
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(description)}"><meta name="theme-color" content="#21382d"><link rel="canonical" href="{canonical}">{alternates}<link rel="alternate" hreflang="x-default" href="{xdefault}"><meta property="og:type" content="website"><meta property="og:site_name" content="Prepinson"><meta property="og:locale" content="{lang}"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ASSET_DOMAIN}/assets/{og_image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title)}"><meta name="twitter:description" content="{escape(description)}"><meta name="twitter:image" content="{ASSET_DOMAIN}/assets/{og_image}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="preload" href="/assets/fonts/cormorant-garamond-regular.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/dm-sans-regular.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}"><script type="application/ld+json">{json.dumps(schema(lang, route, title, description), ensure_ascii=False)}</script><script type="application/json" id="ui-strings">{ui_strings}</script><script src="/app.js?v={ASSET_VERSION}" defer></script></head><body{preview_class} data-language="{lang}" data-route="{route}">{body}</body></html>'


def gateway():
    links = "".join(f'<a href="/{code}/" lang="{code}" hreflang="{code}">{name}</a>' for code, name in LANGUAGE_NAMES.items())
    greetings = "".join(f'<span lang="{code}" style="--step:{i}"><span>{welcome}</span> <em>Prepinson.</em></span>' for i, (code, welcome) in enumerate((('en', 'Welcome to'), ('fr', 'Bienvenue à'), ('nl', 'Welkom bij'), ('de', 'Willkommen bei'), ('sv', 'Välkommen till'), ('lb', 'Wëllkomm zu'))))
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{DOMAIN}/{code}/">' for code in LANGS)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Prepinson | Horse breeding and holiday homes in Belgium</title><meta name="description" content="Discover Haras de Prepinson, its horses and holiday homes in the Belgian Ardennes. Choose your language to continue."><link rel="canonical" href="{DOMAIN}/">{alternates}<link rel="alternate" hreflang="x-default" href="{DOMAIN}/"><link rel="preload" href="/assets/fonts/cormorant-garamond-regular.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/dm-sans-regular.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"></head><body class="gateway"><main><div class="gateway-visual">{responsive_image("hero-horses", "Horses and foals in the fields at Haras de Prepinson", cls="gateway-photo", hero=True)}</div><section class="gateway-panel"><a class="gateway-brand" href="/en/"><img src="/assets/logo.png?v={ASSET_VERSION}" width="260" height="260" alt=""><span>PREPINSON<small>HARAS DE PREPINSON</small></span></a><p class="eyebrow">ORTHO · BELGIAN ARDENNES</p><h1><span class="visually-hidden">Welcome to Prepinson.</span><span class="gateway-greetings" aria-hidden="true">{greetings}</span></h1><p>Choose your language to continue.</p><nav aria-label="Language">{links}</nav></section></main></body></html>'''


def not_found():
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Page not found | Prepinson</title><link rel="preload" href="/assets/fonts/cormorant-garamond-regular.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/dm-sans-regular.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><script src="/app.js?v={ASSET_VERSION}" defer></script></head><body class="not-found" data-page="404"><main><div class="not-found-visual">{image("prepinson-horse-handler-outdoors.webp", "Horse and handler at Haras de Prepinson", cls="not-found-photo", hero=True)}</div><section class="not-found-panel"><a class="gateway-brand" href="/en/" data-404-home><img src="/assets/logo.png?v={ASSET_VERSION}" width="260" height="260" alt=""><span>PREPINSON<small>HARAS DE PREPINSON</small></span></a><p class="eyebrow">404</p><h1 data-404-title>This path seems to have wandered off.</h1><p data-404-copy>Even the horses take the wrong trail sometimes. Let us take you back to Prepinson.</p><a class="btn dark" href="/en/" data-404-action>Return to Prepinson {icon("arrow-up-right")}</a></section></main></body></html>'


def confirmation_page(lang, kind):
    content = render_confirmation(lang, kind) if render_confirmation else f'<section class="text-page container"><p class="eyebrow">PREPINSON</p><h1>{tx("newsletter_success" if kind == "newsletter" else "contact_success", lang, "contact_title")}</h1><a class="btn dark" href="{url(lang)}">{tx("nav_home", lang)}</a></section>'
    preview_class = ' class="is-preview"' if PREVIEW_MODE else ""
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Prepinson</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="preload" href="/assets/fonts/cormorant-garamond-regular.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/dm-sans-regular.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}"></head><body{preview_class}>{header(lang, kind + "/thanks", True)}<main id="main">{content}</main><script src="/app.js?v={ASSET_VERSION}" defer></script></body></html>'


def build():
    OUT.mkdir(exist_ok=True)
    if (ROOT / "src/styles.css").exists():
        fonts = (ROOT / "src/fonts.css").read_text(encoding="utf-8") if (ROOT / "src/fonts.css").exists() else ""
        styles = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("src/styles.css", "src/navigation-refined.css", "src/designs/refinement.css", "src/designs/equilibre.css"))
        (OUT / "styles.css").write_text(fonts + "\n" + styles, encoding="utf-8")
    if (ROOT / "src/app.js").exists():
        app = (ROOT / "src/app.js").read_text(encoding="utf-8")
        finishing = (ROOT / "src/designs/refinement.js").read_text(encoding="utf-8").replace("__ASSET_VERSION__", ASSET_VERSION)
        (OUT / "app.js").write_text(app + "\n" + finishing, encoding="utf-8")
    nav_illustrations = OUT / "assets" / "nav-illustrations"
    nav_illustrations.mkdir(parents=True, exist_ok=True)
    for name in ("haras.webp", "horses.webp", "houses.webp"):
        shutil.copy2(ROOT / "src" / "designs" / "illustrations" / name, nav_illustrations / name)
    for name in ("sales", "grevlunda", "prevet", "njoy", "equilannoo"):
        shutil.copy2(ROOT / "src" / "designs" / "assets" / f"{name}.webp", OUT / "assets" / f"{name}.webp")
    if (ROOT / "src/icons.svg").exists(): shutil.copy2(ROOT / "src/icons.svg", OUT / "icons.svg")
    for child in list(OUT.iterdir()):
        if child.name in {"assets", "styles.css", "app.js", "favicon.svg", "icons.svg", "instagram-feed.json"}: continue
        shutil.rmtree(child) if child.is_dir() else child.unlink()
    (OUT / "index.html").write_text(gateway(), encoding="utf-8")
    (OUT / "404.html").write_text(not_found(), encoding="utf-8")
    for lang in LANGS:
        for route in ROUTES:
            target = OUT / lang / route / "index.html" if route else OUT / lang / "index.html"; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(render(lang, route), encoding="utf-8")
        for kind in ("contact", "newsletter"):
            target = OUT / lang / kind / "thanks" / "index.html"; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(confirmation_page(lang, kind), encoding="utf-8")
    entries = []
    for route in ROUTES:
        for lang in LANGS:
            loc = DOMAIN + url(lang, route); alternates = "".join(f'<xhtml:link rel="alternate" hreflang="{code}" href="{DOMAIN + url(code, route)}"/>' for code in LANGS); xdefault = DOMAIN + ("/" if not route else url("en", route)); entries.append(f'<url><loc>{loc}</loc>{alternates}<xhtml:link rel="alternate" hreflang="x-default" href="{xdefault}"/></url>')
    gateway_alternates = "".join(f'<xhtml:link rel="alternate" hreflang="{code}" href="{DOMAIN}/{code}/"/>' for code in LANGS)
    entries.insert(0, f'<url><loc>{DOMAIN}/</loc>{gateway_alternates}<xhtml:link rel="alternate" hreflang="x-default" href="{DOMAIN}/"/></url>')
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + ''.join(entries) + '</urlset>', encoding="utf-8")
    (OUT / "robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n', encoding="utf-8")
    (OUT / "_redirects").write_text(render_redirects() + '/instagram-feed.json /.netlify/functions/instagram-feed 200!\n/instagram-image /.netlify/functions/instagram-image 200!\n/instagram-health.json /.netlify/functions/instagram-health 200!\n/horses /en/horses/ 301\n/horses/* /en/horses/:splat 301\n/houses /en/houses/ 301\n/houses/* /en/houses/:splat 301\n/* /404.html 404\n', encoding="utf-8")
    preview_header = "  X-Robots-Tag: noindex, nofollow, noarchive\n" if PREVIEW_MODE else ""
    (OUT / "_headers").write_text("/*\n" + preview_header + "  X-Content-Type-Options: nosniff\n", encoding="utf-8")
    from work.instagram import build as build_instagram
    build_instagram()
    print(f"Generated {len(LANGS) * len(ROUTES)} public pages, 12 confirmations, language gateway, and 404 page")


if __name__ == "__main__": build()
