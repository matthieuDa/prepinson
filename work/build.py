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
DOMAIN = "https://www.prepinson.com"
PREVIEW_MODE = os.environ.get("PREVIEW_MODE") == "true"
ASSET_DOMAIN = os.environ.get("DEPLOY_PRIME_URL", DOMAIN).rstrip("/") if PREVIEW_MODE else DOMAIN
IG_HARAS = "https://www.instagram.com/haras_de_prepinson/"
IG_HOUSE = "https://www.instagram.com/prepinson_the_house/"
MAP_HARAS = "https://maps.app.goo.gl/qU2NuF7tHseKitHJ6"
MAP_HOUSE = "https://maps.app.goo.gl/FzkorC926XiJ6Fzw7"
ASSET_VERSION = hashlib.sha256(b"".join((ROOT / name).read_bytes() for name in ("src/styles.css", "src/fonts.css", "src/app.js", "src/site_data.py", "src/presentation_data.py", "src/form_data.py", "src/forms.py", "src/activity_data.py", "src/image-manifest.json", "work/build.py"))).hexdigest()[:12]

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
    fallback = f'<img class="{cls}" src="/assets/{name}?v={ASSET_VERSION}" width="{width}" height="{height}" alt="{escape(re.sub(r"<[^>]+>", " ", alt))}" {loading}>'
    variants = manifest.get("variants", ())
    if not variants:
        return fallback
    srcset = ", ".join(f'{variant["src"]}?v={ASSET_VERSION} {variant["width"]}w' for variant in variants)
    responsive_sizes = sizes or ("(max-width: 700px) 1000px, 100vw" if hero else "(max-width: 700px) 88vw, 43vw")
    avif_srcset = srcset.replace(".webp", ".avif")
    mobile_sources = ""
    if hero and manifest.get("mobile"):
        mobile_webp = ", ".join(f'{item["src"]}?v={ASSET_VERSION} {item["width"]}w' for item in manifest["mobile"])
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
    contact_href = home + "#contact" if route in {"legal", "privacy", "contact/thanks", "newsletter/thanks"} else "#contact"
    nav = ((home + "#haras", ui("nav_haras", lang)), (home + "#expertise", ui("nav_expertise", lang)), (url(lang, "horses"), tx("nav_horses", lang)), (home + "#journal", ui("nav_journal", lang)), (url(lang, "houses"), tx("nav_houses", lang)))
    links = "".join(f'<a href="{href}"' + (' aria-current="page"' if route == href.strip("/").removeprefix(lang + "/") else "") + f'>{label}</a>' for href, label in nav)
    cls = "nav solid-nav" if solid else "nav"
    brand = f'<a class="brand" href="{home}"><img src="/assets/logo.png?v={ASSET_VERSION}" width="260" height="260" alt=""><span class="wordmark">PREPINSON <small>HARAS DE PREPINSON</small></span></a>'
    return f'<a class="skip-link" href="#main">{tx("skip", lang)}</a><header class="{cls}">{brand}<nav class="navlinks" aria-label="{tx("menu", lang)}">{links}<a class="nav-book" href="{contact_href}">{tx("nav_contact", lang)} <span>{icon("arrow-up-right")}</span></a></nav>{language_switch(lang, route)}<button class="menu-toggle" data-menu-toggle type="button" aria-expanded="false" aria-controls="mobile-menu"><span>{tx("menu", lang)}</span>{icon("menu")}</button></header><nav id="mobile-menu" class="mobile-nav" aria-label="{tx("menu", lang)}">{links}<a href="{contact_href}">{tx("nav_contact", lang)}</a><small>ORTHO · ARDENNES</small></nav>'


def editorial_link(href, label, dark=True, **attrs):
    extras = " ".join(f'{key.replace("_", "-")}="{escape(str(value))}"' for key, value in attrs.items())
    cls = "editorial-link dark-link" if dark else "editorial-link"
    return f'<a class="{cls}" href="{href}" {extras}>{label}<span>{icon("arrow-up-right")}</span></a>'


def inner_hero(lang, eyebrow, title, intro, media, *, booking=None, position="center", title_html=None):
    alt = ui({"training": "alt_training", "facilities": "alt_facilities", "house-hero": "alt_houses", "hero-horses-2000.webp": "alt_hero"}.get(media, "alt_houses"), lang)
    if media in GALLERY_ALT: alt = GALLERY_ALT[media][lang]
    visual = responsive_image(media, alt, cls="hero-media", hero=True, position=position) if media in {"training", "facilities", "house-hero"} else image(media, alt, cls="hero-media", hero=True, position=position)
    action = f'<a class="btn light" href="{booking}" target="_blank" rel="noopener noreferrer">{ui("check_availability", lang)} {icon("arrow-up-right")}</a>' if booking else ""
    return f'<section class="hero inner-hero">{visual}<div class="hero-shade"></div><div class="hero-content reveal"><p class="eyebrow">{eyebrow}</p><h1>{title_html or escape(title)}</h1><p>{intro}</p>{action}</div><div class="hero-bottom"><span class="location">{ui("location", lang)}</span><a class="scroll-link" href="#discover">{ui("scroll", lang)} <span>{icon("arrow-down")}</span></a></div></section>'


def home(lang):
    expert = (
        ("01", "boarding", ui("boarding_title", lang), ui("boarding_copy", lang), "boarding"),
        ("02", "training", ui("training_title", lang), ui("training_copy", lang), "training"),
        ("03", "breeding", ui("breeding_title", lang), ui("breeding_copy", lang), "breeding"),
    )
    cards = "".join(f'<a class="expertise-card" href="{url(lang, "horses")}#{target}"><div class="expertise-image">{image(MEDIA[media], ui("alt_" + media, lang))}<span class="image-index">{number}</span></div><div class="expertise-title"><h3>{title}</h3><span>{icon("arrow-up-right")}</span></div><p>{copy}</p></a>' for number, media, title, copy, target in expert)
    refs = "".join(f'<a href="{url(lang, "horses/references")}#{slug}"><span class="pedigree-year">0{i}</span><div><h3>{display_title(tx(f"{slug}_title", lang))}</h3><p>{tx(f"{slug}_copy", lang)}</p></div><span class="pedigree-arrow">{icon("arrow-up-right")}</span></a>' for i, slug in enumerate(("dalton", "juni", "jackson"), 1))
    people = (("team_eva", "Eva Schiller", ui("eva_role", lang), "eva.schiller@prepinson.com", "+352 691 22 38 36"), ("team_nicolas", "Nicolas Derouault", ui("nicolas_role", lang), "nicolas.derouault@prepinson.com", "+32 470 85 13 10"))
    team = "".join(f'<article class="team-card">{image(MEDIA[media], name)}<div><p class="eyebrow">{role}</p><h3>{name}</h3><a href="mailto:{email}">{email} {icon("arrow-up-right")}</a><a href="tel:{phone.replace(" ", "")}">{phone}</a></div></article>' for media, name, role, email, phone in people)
    return f'''
<section class="haras-hero">{responsive_image("hero-horses", ui("alt_hero", lang), cls="haras-hero-photo", hero=True, position="center 45%")}
<div class="haras-hero-overlay"></div><div class="hero-editorial"><p class="eyebrow">{v1("home_eyebrow", lang)}</p><h1>{v1("home_hero", lang)}</h1><div class="hero-intro-line"><span>{v1("home_tagline", lang)}</span>{editorial_link("#haras", ui("hero_cta", lang), dark=False)}</div></div>
<div class="hero-side"><button type="button" data-video-open="/assets/haras-film.mp4" class="film-button"><span class="circle">{icon("play")}</span><span>{v1("hero_film", lang)}</span></button></div><div class="hero-baseline"><span>{ui("location", lang)}</span><span>{v1("home_services_line", lang)}</span><a href="#haras">{ui("scroll", lang)} <span>{icon("arrow-down")}</span></a></div></section>
<section id="haras" class="haras-intro container"><div class="intro-label"><span class="eyebrow">{ui("intro_label", lang)}</span><span class="tiny-serif">01 —</span></div><div class="haras-intro-copy"><h2>{v1("home_intro_title", lang)}</h2><p>{v1("home_intro", lang)}</p><p class="quiet-copy">{v1("home_intro_secondary", lang)}</p>{editorial_link(url(lang, "horses"), v1("home_intro_link", lang))}</div><figure class="intro-portrait">{image(MEDIA["intro"], ui("alt_intro", lang), position="45% 50%") }<figcaption>{ui("intro_note", lang)}</figcaption></figure></section>
<section id="expertise" class="expertise-section"><div class="container"><div class="expertise-heading"><p class="eyebrow">{ui("expertise_label", lang)}</p><h2>{v1("expertise_title", lang)}</h2><p>{v1("expertise_intro", lang)}</p></div><div class="expertise-grid">{cards}</div></div></section>
<section class="facilities-home"><div class="haras-landscape">{responsive_image("facilities", ui("alt_facilities", lang), position="center 45%")}<div class="landscape-caption"><span class="eyebrow">{tx("facilities_hero", lang)}</span>{editorial_link(url(lang, "horses/facilities"), ui("facilities_cta", lang), dark=False)}</div></div>{stat_strip(lang)}</section>
<section class="selected-section container"><div class="selected-heading"><p class="eyebrow">{ui("references_label", lang)}</p><h2>{tx("references_hero", lang)}</h2><p>{tx("service_references_copy", lang)}</p>{editorial_link(url(lang, "horses/references"), tx("service_references", lang))}</div><div class="pedigree-list">{refs}</div></section>
<section id="team" class="team-section"><div class="container"><div class="team-heading"><p class="eyebrow">{ui("team_label", lang)}</p><h2>{v1("team_title", lang)}</h2><p>{v1("team_intro", lang)}</p></div><div class="team-grid">{team}</div></div></section>
<section class="home-houses"><div class="estate-grid container"><div class="estate-photo">{responsive_image("house-hero", ui("alt_houses", lang))}</div><div class="estate-copy"><p class="eyebrow">{ui("houses_label", lang)}</p><h2>{tx("houses_teaser_title", lang)}</h2><p>{ui("houses_home_copy", lang)}</p>{editorial_link(url(lang, "houses"), ui("houses_cta", lang))}</div></div></section>
<section id="journal" class="journal-stories feedpane-section container"><div class="section-head"><div><p class="eyebrow">{ui("journal_label", lang)}</p><h2>{v1("journal_title", lang)}</h2></div><p class="journal-intro">{v1("journal_intro", lang)}</p></div><div id="feedpane" class="feedpane-shell" aria-label="Instagram · Haras de Prepinson"></div><script src="https://feedpane.com/widget.js" data-key="6c7a542cd3ba470d84f9ce26f775c77c" data-target="#feedpane" data-cols="3" data-mobile-cols="1" data-gap="14" data-radius="0" data-posts="6" data-autoplay="false" defer></script><p class="feedpane-fallback">{editorial_link(IG_HARAS, ui("instagram_fallback", lang), target="_blank", rel="noopener noreferrer")}</p></section>'''


def horses(lang):
    sections = (("boarding", "01", ui("boarding_title", lang), ui("boarding_copy", lang), MEDIA["boarding"], "horses/facilities", tx("nav_facilities", lang)), ("training", "02", ui("training_title", lang), ui("training_copy", lang), MEDIA["training"], "horses/programmes", tx("nav_programmes", lang)), ("breeding", "03", ui("breeding_title", lang), ui("breeding_copy", lang), MEDIA["breeding"], "horses/references", tx("service_references", lang)))
    body = inner_hero(lang, v1("home_eyebrow", lang), tx("horses_hero", lang), v1("horses_tagline", lang), "training", title_html=v1("horses_hero", lang)) + f'<section id="discover" class="intro container"><div><p class="eyebrow">{tx("world_horses", lang)}</p><h2>{ui("horses_intro_first", lang)}<br><em>{ui("horses_intro_second", lang)}</em></h2></div><p class="body-copy">{tx("horses_intro", lang)}</p></section><section class="service-stories container">'
    for anchor, number, title, copy, media, route, cta in sections:
        body += f'<article id="{anchor}" class="service-story"><div class="service-story-image">{image(media, ui("alt_" + anchor, lang))}</div><div><p class="eyebrow">{number} / {title}</p><h2>{title}</h2><p>{copy}</p>{editorial_link(url(lang, route), cta)}</div></article>'
    return body + f'</section><section class="instagram-band"><div><p class="eyebrow">{tx("nav_sales", lang)}</p><h2>{tx("sales_range", lang)}</h2><p>{tx("sales_intro", lang)}</p></div><a class="btn light" href="{url(lang, "horses/for-sale")}">{tx("nav_sales", lang)} {icon("arrow-up-right")}</a></section>'


def programmes(lang):
    subjects = ("programme-foal", "programme-pre-breaking", "programme-breaking", "programme-jumping")
    panels = "".join(f'<details' + (' open' if i == 1 else '') + f'><summary><span class="programme-number">0{i}</span><span>{tx(f"p{i}_title", lang)}</span><span class="programme-toggle">{icon("plus")}</span></summary><div class="programme-panel"><p><strong>{tx(f"p{i}_timing", lang)}</strong></p><p>{tx(f"p{i}_copy", lang)}</p><a class="text-link" href="#contact" data-contact-subject="{subjects[i - 1]}">{ui("programme_cta", lang)} {icon("arrow-up-right")}</a></div></details>' for i in range(1, 5))
    return inner_hero(lang, tx("nav_programmes", lang), tx("programmes_hero", lang), tx("programmes_intro", lang), "training") + f'<section id="discover" class="programmes-section container"><div class="programmes-heading"><p class="eyebrow">{tx("nav_programmes", lang)}</p><h2>{ui("programmes_list_title", lang)}</h2></div><div class="programme-list">{panels}</div></section>'


def gallery(items, lang):
    buttons = "".join(f'<button type="button" data-lightbox-item="{i}" data-lightbox-src="/assets/{name}?v={ASSET_VERSION}" aria-label="{escape(ui("gallery_label", lang))}: {escape(alt)}">{image(name, alt, sizes="(max-width: 700px) 43vw, 28vw")}</button>' for i, (name, alt) in enumerate(items))
    return f'<div class="gallery" aria-label="{escape(ui("gallery_label", lang))}">{buttons}</div>'


def facilities(lang):
    gallery_items = (("prepinson-indoor-riding-arena.webp", ui("alt_indoor", lang)), ("prepinson-outdoor-jumping-arena.webp", ui("alt_training", lang)), ("prepinson-outdoor-arena.webp", ui("alt_outdoor", lang)), ("prepinson-horses-green-paddocks.webp", ui("alt_paddocks", lang)), ("prepinson-rider-saddle-detail.webp", ui("alt_saddle", lang)), ("prepinson-stables-flowers.webp", ui("alt_boarding", lang)))
    items = "".join(f'<li>{tx(key, lang)}</li>' for key in ("facility_equipment", "facility_club", "facility_breeding", "facility_trails"))
    return inner_hero(lang, tx("nav_facilities", lang), tx("facilities_hero", lang), tx("facilities_intro", lang), "facilities") + f'<section id="discover" class="facilities-detail container"><div class="section-head"><div><p class="eyebrow">{tx("stats_title", lang)}</p><h2>{ui("facilities_detail_title", lang)}</h2></div></div>{stat_strip(lang, light=True)}<div class="facilities-copy"><ul class="large-list">{items}</ul><div><p>Ortho 24<br>6983 La Roche-en-Ardenne<br>{ui("country", lang)}</p><p>{ui("transport_access", lang)}</p>{editorial_link("#contact", tx("nav_contact", lang))}{editorial_link(MAP_HARAS, tx("footer_maps_haras", lang), target="_blank", rel="noopener noreferrer")}</div></div>{gallery(gallery_items, lang)}</section>'


def sales(lang):
    return inner_hero(lang, tx("nav_sales", lang), tx("sales_hero", lang), tx("sales_intro", lang), "hero-horses-2000.webp") + f'<section id="discover" class="sales-section container"><div><p class="eyebrow">{tx("nav_sales", lang)}</p><h2>{tx("sales_range", lang)}</h2><p>{tx("sales_cta", lang)}</p><a class="btn dark" href="#contact" data-contact-subject="horse-search">{ui("sales_cta", lang)} {icon("arrow-up-right")}</a></div>{image("prepinson-bay-horse-outdoors.webp", tx("sales_range", lang))}</section>'


def references(lang):
    rows = "".join(f'<article id="{slug}" class="reference-story"><p class="eyebrow">0{i} / HARAS DE PREPINSON</p><h2>{display_title(tx(f"{slug}_title", lang))}</h2><p>{tx(f"{slug}_copy", lang)}</p></article>' for i, slug in enumerate(("dalton", "juni", "jackson"), 1))
    return inner_hero(lang, tx("service_references", lang), tx("references_hero", lang), tx("service_references_copy", lang), "hero-horses-2000.webp") + f'<section id="discover" class="reference-stories container">{rows}</section>'


def property_card(lang, slug):
    prop = PROPERTIES[slug]
    facts = HOUSE_FACTS[slug]
    title = tx("ortho24_display_title" if slug == "ortho-24" else "ortho25_display_title", lang, "ortho24_title" if slug == "ortho-24" else "ortho25_title")
    description = v1("ortho24_copy" if slug == "ortho-24" else "ortho25_copy", lang)
    booking_label = ui("book_casapilot" if slug == "ortho-24" else "book_airbnb", lang)
    return f'<article class="property-card"><a class="property-image" href="{url(lang, "houses/" + slug)}">{image(prop["image"], title)}</a><div class="property-info"><p class="eyebrow">ORTHO · ARDENNES</p><h3>{title}</h3><div class="property-meta"><span>{facts["guests"]} {tx("guests", lang)}</span><span>{facts["bedrooms"]} {tx("bedrooms", lang)}</span><span>{facts["bathrooms"]} {tx("bathrooms", lang)}</span></div><p>{description}</p><div class="property-links"><a class="btn dark" href="{url(lang, "houses/" + slug)}">{tx("explore_house", lang)} {icon("arrow-up-right")}</a><a class="text-link" href="{prop["booking"]}" target="_blank" rel="noopener noreferrer">{booking_label} {icon("arrow-up-right")}</a></div></div></article>'


def houses(lang):
    return inner_hero(lang, ui("houses_label", lang), tx("houses_hero", lang), v1("houses_tagline", lang), "house-hero", title_html=v1("houses_hero", lang)) + f'<section id="discover" class="intro container"><div><p class="eyebrow">{ui("houses_label", lang)}</p><h2>{v1("houses_intro_title", lang)}</h2></div><p class="body-copy">{ui("houses_home_copy", lang)}</p></section><section class="property-grid container">{property_card(lang, "ortho-24")}{property_card(lang, "ortho-25")}</section><section class="estate-section"><div class="estate-grid container"><div class="estate-photo">{image("house-1.jpg", ui("location", lang))}</div><div class="estate-copy"><p class="eyebrow">{tx("nav_activities", lang)}</p><h2>{v1("houses_estate_title", lang)}</h2><p>{v1("houses_estate_copy", lang)}</p>{editorial_link(url(lang, "activities"), ui("activities_cta", lang))}</div></div></section><section class="house-instagram"><div class="container"><div><p class="eyebrow">PREPINSON THE HOUSE</p><h2>{v1("houses_instagram_title", lang)}</h2></div><div><p>{v1("houses_instagram_copy", lang)}</p>{editorial_link(IG_HOUSE, "@prepinson_the_house", target="_blank", rel="noopener noreferrer")}</div></div></section>'


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
    return inner_hero(lang, "ORTHO · " + ui("country", lang).upper(), title, ui("ortho24_tag" if is24 else "ortho25_tag", lang), prop["image"], booking=prop["booking"], title_html=escape(title.split(" — ")[0]) + ' —<br><em>' + escape(title.split(" — ")[1]) + '</em>') + f'<section id="discover" class="property-detail container"><div class="property-summary"><div><p class="eyebrow">{ui("houses_label", lang)}</p><h2>{v1("house_detail_intro", lang)}</h2><p>{description}</p><div class="amenities">{amenities}</div></div><aside class="booking-panel"><h3>{ui("booking_title", lang)}</h3><p>{booking_label}</p><a class="btn dark" href="{prop["booking"]}" target="_blank" rel="noopener noreferrer">{booking_label} {icon("arrow-up-right")}</a><a class="text-link" href="#contact" data-contact-subject="{slug}">{tx("nav_contact", lang)} {icon("arrow-up-right")}</a></aside></div><div class="property-gallery-heading"><p class="eyebrow">{ui("gallery_label", lang)}</p><h2>{ui("gallery_title", lang)}</h2></div>{gallery(localized_gallery, lang)}</section><section class="property-film"><div class="container">{film}{editorial_link(url(lang, "activities"), ui("activities_cta", lang))}</div></section><section class="other-property container"><p class="eyebrow">{ui("other_house", lang)}</p>{property_card(lang, other)}</section>'


def activities(lang):
    groups = ""
    for group, label_key in ACTIVITY_GROUPS:
        items = ACTIVITIES[group] if isinstance(ACTIVITIES, dict) else [item for item in ACTIVITIES if item.get("group") == group]
        cards = ""
        for item in items:
            name = item.get("name") or item.get("title"); href = item.get("url") or item.get("href"); copy = activity_copy(item, lang)
            cards += f'<a class="place" href="{href}" target="_blank" rel="noopener noreferrer"><strong>{name}</strong>{f"<p>{copy}</p>" if copy else ""}<span>{ui("official_link", lang)} {icon("arrow-up-right")}</span></a>'
        groups += f'<section><h2>{tx(label_key, lang)}</h2><div class="link-grid">{cards}</div></section>'
    return inner_hero(lang, tx("nav_activities", lang), tx("activities_hero", lang), tx("activities_intro", lang), "facilities") + f'<div id="discover" class="activities container">{groups}<p class="notice">{tx("activity_conditions", lang)}</p></div>'


def legal(lang):
    return f'<section class="text-page container" id="content"><p class="eyebrow">PREPINSON</p><h1>{tx("legal_heading", lang)}</h1><h2>{tx("legal_company", lang)}</h2><p>Ortho 24, 6983 La Roche-en-Ardenne, {ui("country", lang)}<br><a href="mailto:haras@prepinson.com">haras@prepinson.com</a> · <a href="tel:+32470851310">+32 470 85 13 10</a></p><h2>{tx("legal_host", lang)}</h2><p>Netlify, Inc. · 44 Montgomery Street, Suite 300, San Francisco, California 94104, USA.</p><h2>{tx("legal_ip", lang)}</h2><p>{tx("legal_ip_copy", lang)}</p></section>'


def privacy(lang):
    sections = (("privacy_collect", "privacy_collect_copy"), ("privacy_basis", "privacy_basis_copy"), ("privacy_processors", "privacy_processors_copy"), ("privacy_newsletter", "privacy_newsletter_copy"), ("privacy_rights", "privacy_rights_copy"), ("privacy_language", "privacy_language_copy"))
    return f'<section class="text-page container" id="content"><p class="eyebrow">PREPINSON</p><h1>{tx("privacy_heading", lang)}</h1>' + "".join(f'<h2>{tx(a, lang)}</h2><p>{tx(b, lang)}</p>' for a, b in sections if a in TEXT) + '</section>'


BUILDERS = {"": home, "horses": horses, "horses/programmes": programmes, "horses/facilities": facilities, "horses/for-sale": sales, "horses/references": references, "houses": houses, "activities": activities, "legal": legal, "privacy": privacy}


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
    if route.startswith("houses/"):
        prop = PROPERTIES[route.rsplit("/", 1)[1]]
        graph.append({"@type": "VacationRental", "name": prop["short"], "url": page_url, "description": description, "image": [ASSET_DOMAIN + "/assets/" + item[0] for item in prop["gallery"]], "containsPlace": {"@type": "Accommodation", "occupancy": {"@type": "QuantitativeValue", "value": 8}, "numberOfBedrooms": prop["bedrooms"], "numberOfBathroomsTotal": prop["bathrooms"]}, "sameAs": [prop["booking"]]})
    return {"@context": "https://schema.org", "@graph": graph}


def render(lang, route):
    title, description = tx(META[route][0], lang), tx(META[route][1], lang); canonical = DOMAIN + url(lang, route)
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{DOMAIN + url(code, route)}">' for code in LANGS); xdefault = DOMAIN + ("/" if not route else url("en", route))
    content = house(lang, route.rsplit("/", 1)[1]) if route.startswith("houses/") else BUILDERS[route](lang)
    contact = render_contact(lang, route) if render_contact else fallback_contact(lang, route); footer = render_footer(lang, route) if render_footer else fallback_footer(lang, route)
    body = header(lang, route, route in {"legal", "privacy"}) + f'<main id="main">{content}</main>' + contact + footer + (forms_dialogs(lang) if forms_dialogs else dialogs(lang))
    og_image = "og-houses.jpg" if route.startswith("houses") else "og-prepinson.jpg"
    ui_strings = json.dumps({"menu": tx("menu", lang), "close": tx("close", lang), "language": tx("language", lang)}, ensure_ascii=False)
    preview_class = ' class="is-preview"' if PREVIEW_MODE else ""
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(description)}"><meta name="theme-color" content="#21382d"><link rel="canonical" href="{canonical}">{alternates}<link rel="alternate" hreflang="x-default" href="{xdefault}"><meta property="og:type" content="website"><meta property="og:site_name" content="Prepinson"><meta property="og:locale" content="{lang}"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ASSET_DOMAIN}/assets/{og_image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title)}"><meta name="twitter:description" content="{escape(description)}"><meta name="twitter:image" content="{ASSET_DOMAIN}/assets/{og_image}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}"><script type="application/ld+json">{json.dumps(schema(lang, route, title, description), ensure_ascii=False)}</script><script type="application/json" id="ui-strings">{ui_strings}</script><script src="/app.js?v={ASSET_VERSION}" defer></script></head><body{preview_class} data-language="{lang}" data-route="{route}">{body}</body></html>'


def gateway():
    links = "".join(f'<a href="/{code}/" lang="{code}" hreflang="{code}">{name}</a>' for code, name in LANGUAGE_NAMES.items())
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><title>Welcome to Prepinson — Choose your language</title><meta name="description" content="Choose your language to discover Haras de Prepinson and its holiday homes in the Belgian Ardennes."><link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"></head><body class="gateway"><main><div class="gateway-visual">{responsive_image("hero-horses", "Horses and foals in the fields at Haras de Prepinson", cls="gateway-photo", hero=True)}</div><section class="gateway-panel"><a class="gateway-brand" href="/en/"><img src="/assets/logo.png?v={ASSET_VERSION}" width="260" height="260" alt=""><span>PREPINSON<small>HARAS DE PREPINSON</small></span></a><p class="eyebrow">ORTHO · BELGIAN ARDENNES</p><h1>Welcome to Prepinson.<br><em>Bienvenue à Prepinson.</em></h1><p>Choose the language in which you would like to continue.</p><nav aria-label="Language">{links}</nav></section></main></body></html>'


def not_found():
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Page not found — Prepinson</title><link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><script src="/app.js?v={ASSET_VERSION}" defer></script></head><body class="not-found" data-page="404"><main><div class="not-found-visual">{image("prepinson-horse-handler-outdoors.webp", "Horse and handler at Haras de Prepinson", cls="not-found-photo", hero=True)}</div><section class="not-found-panel"><a class="gateway-brand" href="/en/" data-404-home><img src="/assets/logo.png?v={ASSET_VERSION}" width="260" height="260" alt=""><span>PREPINSON<small>HARAS DE PREPINSON</small></span></a><p class="eyebrow">404</p><h1 data-404-title>This path seems to have wandered off.</h1><p data-404-copy>Even the horses take the wrong trail sometimes. Let us take you back to Prepinson.</p><a class="btn dark" href="/en/" data-404-action>Return to Prepinson {icon("arrow-up-right")}</a></section></main></body></html>'


def confirmation_page(lang, kind):
    content = render_confirmation(lang, kind) if render_confirmation else f'<section class="text-page container"><p class="eyebrow">PREPINSON</p><h1>{tx("newsletter_success" if kind == "newsletter" else "contact_success", lang, "contact_title")}</h1><a class="btn dark" href="{url(lang)}">{tx("nav_home", lang)}</a></section>'
    preview_class = ' class="is-preview"' if PREVIEW_MODE else ""
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Prepinson</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/styles.css?v={ASSET_VERSION}"></head><body{preview_class}>{header(lang, kind + "/thanks", True)}<main id="main">{content}</main><script src="/app.js?v={ASSET_VERSION}" defer></script></body></html>'


def build():
    OUT.mkdir(exist_ok=True)
    if (ROOT / "src/styles.css").exists():
        fonts = (ROOT / "src/fonts.css").read_text(encoding="utf-8") if (ROOT / "src/fonts.css").exists() else ""
        styles = (ROOT / "src/styles.css").read_text(encoding="utf-8")
        (OUT / "styles.css").write_text(fonts + "\n" + styles, encoding="utf-8")
    if (ROOT / "src/app.js").exists(): shutil.copy2(ROOT / "src/app.js", OUT / "app.js")
    if (ROOT / "src/icons.svg").exists(): shutil.copy2(ROOT / "src/icons.svg", OUT / "icons.svg")
    for child in list(OUT.iterdir()):
        if child.name in {"assets", "styles.css", "app.js", "favicon.svg", "icons.svg"}: continue
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
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + ''.join(entries) + '</urlset>', encoding="utf-8")
    (OUT / "robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n', encoding="utf-8")
    (OUT / "_redirects").write_text('/horses /en/horses/ 301\n/horses/* /en/horses/:splat 301\n/houses /en/houses/ 301\n/houses/* /en/houses/:splat 301\n/* /404.html 404\n', encoding="utf-8")
    preview_header = "  X-Robots-Tag: noindex, nofollow, noarchive\n" if PREVIEW_MODE else ""
    (OUT / "_headers").write_text("/*\n" + preview_header + "  X-Content-Type-Options: nosniff\n", encoding="utf-8")
    print(f"Generated {len(LANGS) * len(ROUTES)} public pages, 12 confirmations, language gateway, and 404 page")


if __name__ == "__main__": build()
