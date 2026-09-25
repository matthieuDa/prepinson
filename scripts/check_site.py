#!/usr/bin/env python3
"""Fail-closed validation for the generated multilingual website."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
sys.path.insert(0, str(ROOT))
from src.form_data import FORM_COPY  # noqa: E402
from src.site_data import LANGS, ROUTES  # noqa: E402

DOMAIN = "https://www.prepinson.com"
ASSET_DOMAIN = os.environ.get("DEPLOY_PRIME_URL", DOMAIN).rstrip("/") if os.environ.get("PREVIEW_MODE") == "true" else DOMAIN
errors = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs = []
        self.ids = set()
        self.duplicate_ids = set()
        self.forms = []
        self.current_form = None
        self.lang = None
        self.h1 = 0
        self.title = ""
        self.in_title = False
        self.jsonld = []
        self.script_type = None
        self.script_text = ""

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.attrs.append((tag, values))
        if values.get("id"):
            if values["id"] in self.ids:
                self.duplicate_ids.add(values["id"])
            self.ids.add(values["id"])
        if tag == "form":
            self.current_form = {"attrs": values, "fields": []}
            self.forms.append(self.current_form)
        elif tag in {"input", "select", "textarea", "button"} and self.current_form is not None:
            self.current_form["fields"].append((tag, values))
        if tag == "html":
            self.lang = values.get("lang")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self.in_title = True
        elif tag == "script":
            self.script_type = values.get("type")
            self.script_text = ""

    def handle_endtag(self, tag):
        if tag == "form":
            self.current_form = None
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self.script_type == "application/ld+json":
            self.jsonld.append(self.script_text)
            self.script_type = None

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.script_type == "application/ld+json":
            self.script_text += data


def fail(path, message):
    errors.append(f"{path}: {message}")


expected = {DIST / lang / route / "index.html" if route else DIST / lang / "index.html" for lang in LANGS for route in ROUTES}
utility = {DIST / lang / kind / "thanks" / "index.html" for lang in LANGS for kind in ("contact", "newsletter")}
all_expected = expected | utility
actual = set(DIST.glob("*/**/index.html")) - {DIST / "index.html"}
if actual != all_expected:
    fail("dist", f"route matrix mismatch; missing={sorted(map(str, all_expected-actual))}, extra={sorted(map(str, actual-all_expected))}")

pages = {}
for path in sorted(expected):
    page = Page()
    raw = path.read_text(encoding="utf-8")
    page.feed(raw)
    pages[path] = page
    rel = path.relative_to(DIST)
    lang = rel.parts[0]
    route = "/".join(rel.parts[1:-1])
    canonical = DOMAIN + f"/{lang}/" + (route + "/" if route else "")

    if "—" in raw:
        fail(rel, "public copy contains an em dash")
    if "prepinson_the_house" in raw:
        fail(rel, "obsolete houses Instagram handle remains in public copy")
    if "https://www.instagram.com/prepinson_houses/" not in raw or "@prepinson_houses" not in raw:
        fail(rel, "current houses Instagram link or label is missing")
    for map_label in (FORM_COPY[lang]["haras_map"], FORM_COPY[lang]["house_map"]):
        if map_label not in raw:
            fail(rel, f"footer map link is not explicit: {map_label}")
    if route == "horses/programmes":
        if 'class="programme-list" data-exclusive-details' not in raw:
            fail(rel, "programme list is not configured as an exclusive details group")
        if raw.count('name="programmes"') != 4:
            fail(rel, "programme details do not share the native exclusive group name")
        if raw.count('name="programmes" open') != 1:
            fail(rel, "programme list must start with exactly one open panel")

    if 'class="updates-form"' not in raw or "newsletter-form" in raw:
        fail(rel, "newsletter must use the content-blocker-resistant footer classes")
    if route == "activities":
        if 'class="contact-section"' in raw:
            fail(rel, "Activities must end with the houses feature, without a contact form")
        if raw.count('class="activity-chapter"') != 5:
            fail(rel, "Activities must contain the five editorial guide chapters")
        for house_route in (f"/{lang}/houses/ortho-24/", f"/{lang}/houses/ortho-25/"):
            if house_route not in raw:
                fail(rel, f"Activities houses feature is missing {house_route}")
    if route == "horses/references":
        for asset in ("dalton-falsterbo-dressage.webp", "dalton-falsterbo-finish.webp", "dalton-falsterbo-arena-entry.webp"):
            if asset not in raw:
                fail(rel, f"Dalton reference gallery is missing {asset}")

    if page.duplicate_ids:
        fail(rel, f"duplicate IDs: {page.duplicate_ids}")
    if page.lang != lang:
        fail(rel, f"html lang {page.lang!r}, expected {lang!r}")
    if page.h1 != 1:
        fail(rel, f"expected exactly one h1, got {page.h1}")
    if not page.title.strip():
        fail(rel, "missing title")

    metas = {(a.get("property") or a.get("name")): a.get("content") for t, a in page.attrs if t == "meta"}
    links = [(a.get("rel"), a.get("hreflang"), a.get("href")) for t, a in page.attrs if t == "link"]
    canonicals = [href for rels, _, href in links if rels == "canonical"]
    if canonicals != [canonical]:
        fail(rel, f"canonical mismatch {canonicals}")
    expected_alts = {code: DOMAIN + f"/{code}/" + (route + "/" if route else "") for code in LANGS}
    expected_alts["x-default"] = DOMAIN + ("/" if not route else f"/en/{route}/")
    alts = {hreflang: href for rels, hreflang, href in links if rels == "alternate" and hreflang}
    if alts != expected_alts:
        fail(rel, f"hreflang mismatch {alts}")
    for key in ("description", "og:title", "og:description", "og:url", "og:image", "twitter:card", "twitter:image"):
        if not metas.get(key):
            fail(rel, f"missing {key}")
    if metas.get("og:url") != canonical:
        fail(rel, "og:url differs from canonical")
    if metas.get("og:image") != ASSET_DOMAIN + ("/assets/og-houses.jpg" if route.startswith("houses") else "/assets/og-prepinson.jpg"):
        fail(rel, "unexpected social image")
    if metas.get("twitter:image") != metas.get("og:image"):
        fail(rel, "Twitter image differs from social image")
    if not page.jsonld:
        fail(rel, "missing JSON-LD")
    for block in page.jsonld:
        try:
            data = json.loads(block)
            if data.get("@context") != "https://schema.org" or not data.get("@graph"):
                fail(rel, "incomplete JSON-LD graph")
            graph = {item.get("@id"): item for item in data.get("@graph", [])}
            haras = graph.get(DOMAIN + "/#haras", {})
            houses = graph.get(DOMAIN + "/#houses", {})
            if "https://maps.app.goo.gl/qU2NuF7tHseKitHJ6" not in haras.get("sameAs", []):
                fail(rel, "Haras Google Business Profile is not attached to the Haras entity")
            if "https://maps.app.goo.gl/FzkorC926XiJ6Fzw7" not in houses.get("sameAs", []):
                fail(rel, "House Google Business Profile is not attached to the lodging entity")
        except json.JSONDecodeError as exc:
            fail(rel, f"invalid JSON-LD: {exc}")

    for tag, attrs in page.attrs:
        if tag == "iframe":
            fail(rel, "third-party iframe present")
        if tag == "script" and attrs.get("src", "").startswith(("http://", "https://")):
            fail(rel, "third-party script must be loaded on demand, not in page HTML")
        if tag == "img":
            if "hero-image" in attrs.get("class", "").split() and (attrs.get("loading") == "lazy" or attrs.get("fetchpriority") != "high"):
                fail(rel, "hero image must load with high priority, without lazy loading")
            if not attrs.get("width") or not attrs.get("height"):
                fail(rel, f"image missing dimensions: {attrs.get('src')}")
            if attrs.get("alt") is None:
                fail(rel, f"image missing alt attribute: {attrs.get('src')}")
        for field in ("src", "href"):
            value = attrs.get(field, "")
            if value.startswith("http://"):
                fail(rel, f"insecure URL {value}")
            if value.startswith("/") and not value.startswith("//"):
                target = DIST / urlsplit(value).path.lstrip("/")
                if target.is_dir():
                    target /= "index.html"
                if not target.exists():
                    fail(rel, f"missing local target {value}")
                fragment = urlsplit(value).fragment
                if fragment and target.suffix == ".html" and target in pages and fragment not in pages[target].ids:
                    fail(rel, f"missing anchor {value}")
        if tag == "source":
            for candidate in attrs.get("srcset", "").split(","):
                if not candidate.strip():
                    continue
                path_part = candidate.strip().split()[0]
                if path_part.startswith("/") and not (DIST / urlsplit(path_part).path.lstrip("/")).exists():
                    fail(rel, f"missing responsive asset {path_part}")

gateway = (DIST / "index.html").read_text(encoding="utf-8")
if "—" in gateway:
    fail("index.html", "language gateway contains an em dash")
if 'name="robots" content="noindex,follow"' not in gateway:
    fail("index.html", "root gateway must be non-indexable fallback")
for lang in LANGS:
    if f'href="/{lang}/"' not in gateway:
        fail("index.html", f"missing gateway link for {lang}")

not_found = (DIST / "404.html").read_text(encoding="utf-8")
if "—" in not_found:
    fail("404.html", "404 page contains an em dash")
if 'name="robots" content="noindex,nofollow"' not in not_found or 'data-page="404"' not in not_found:
    fail("404.html", "404 page must be localized by the site script and excluded from indexing")
if "/* /404.html 404" not in (DIST / "_redirects").read_text(encoding="utf-8"):
    fail("_redirects", "missing Netlify 404 fallback")

ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
tree = ET.parse(DIST / "sitemap.xml")
urls = tree.findall("s:url", ns)
if len(urls) != len(LANGS) * len(ROUTES):
    fail("sitemap.xml", f"expected {len(LANGS)*len(ROUTES)} URLs, got {len(urls)}")
for node in urls:
    alternates = node.findall("x:link", ns)
    if len(alternates) != len(LANGS) + 1:
        fail("sitemap.xml", "URL without complete alternate set")

robots = (DIST / "robots.txt").read_text(encoding="utf-8")
if "Disallow:" in robots or f"Sitemap: {DOMAIN}/sitemap.xml" not in robots:
    fail("robots.txt", "robots policy or sitemap declaration is wrong")

config = (ROOT / "netlify.toml").read_text(encoding="utf-8")
for required in ("Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy", 'path = "/"'):
    if required not in config:
        fail("netlify.toml", f"missing {required}")
edge = (ROOT / "netlify/edge-functions/language-redirect.js").read_text(encoding="utf-8")
if "accept-language" not in edge or "prepinson-language" not in edge or "status: 302" not in edge:
    fail("language-redirect.js", "language detection, cookie preference or temporary redirect missing")

public = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in expected)
for pattern in (r"€\s*\d", r"\b\d+[.,]?\d*\s*€", r"\bEUR\s*\d", r"\bUSD\s*\d"):
    if re.search(pattern, public, re.I):
        fail("dist", f"public price pattern found: {pattern}")
if re.search(r"(?:api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}", public, re.I):
    fail("dist", "possible credential in public HTML")
for path, page in pages.items():
    lang = path.relative_to(DIST).parts[0]
    route = "/".join(path.relative_to(DIST).parts[1:-1])
    forms = {form["attrs"].get("name"): form for form in page.forms}
    required_forms = ["newsletter"] + ([] if route in {"activities", "legal", "privacy"} else ["contact-" + lang])
    for name in required_forms:
        if name not in forms:
            fail(path, f"missing expected form {name}")
            continue
        form = forms[name]
        kind = "newsletter" if name == "newsletter" else "contact"
        attrs = form["attrs"]
        fields = {v.get("name"): v for _, v in form["fields"] if v.get("name")}
        if attrs.get("action") != f"/{lang}/{kind}/thanks/" or attrs.get("method", "").upper() != "POST":
            fail(path, f"wrong form endpoint for {name}")
        if attrs.get("data-netlify") != "true" or attrs.get("netlify-honeypot") != "company":
            fail(path, f"missing Netlify detection/spam protection for {name}")
        for field in ("form-name", "email", "company", "language", "source_page"):
            if field not in fields:
                fail(path, f"missing {field} in {name}")
        if fields.get("form-name", {}).get("value") != name:
            fail(path, f"wrong hidden form-name for {name}")
        if fields.get("language", {}).get("value") != lang:
            fail(path, f"wrong form language for {name}")
        if fields.get("email", {}).get("type") != "email" or "required" not in fields.get("email", {}):
            fail(path, f"email validation missing for {name}")
        if kind == "newsletter":
            consent = fields.get("consent", {})
            if consent.get("value") != "yes" or "required" not in consent or "checked" in consent:
                fail(path, "newsletter consent must be explicit, required and unchecked")
            if not fields.get("consent_version", {}).get("value"):
                fail(path, "newsletter consent version absent")
        if "?" in fields.get("source_page", {}).get("value", ""):
            fail(path, "query parameters must not be recorded in form source")

for path in utility:
    page = Page(); raw = path.read_text(encoding="utf-8"); page.feed(raw); pages[path] = page
    metas = {a.get("name"): a.get("content", "") for t, a in page.attrs if t == "meta"}
    if "noindex" not in metas.get("robots", "") or page.h1 != 1:
        fail(path, "confirmation must have one h1 and noindex")
    if page.lang != path.relative_to(DIST).parts[0]:
        fail(path, "confirmation language mismatch")
    if str(path.relative_to(DIST).parent) in (DIST / "sitemap.xml").read_text():
        fail(path, "confirmation included in sitemap")

# Check every fragment after parsing the entire route set, including same-page links.
for path, page in pages.items():
    for tag, attrs in page.attrs:
        href = attrs.get("href", "")
        if not href.startswith(("/", "#")):
            continue
        parts = urlsplit(href)
        target = DIST / parts.path.lstrip("/") if parts.path else path
        if target.is_dir(): target /= "index.html"
        if parts.fragment and target.suffix == ".html":
            if target not in pages:
                if not target.exists():
                    fail(path, f"missing local page {href}")
                    continue
                parsed = Page(); parsed.feed(target.read_text()); pages_target = parsed
            else: pages_target = pages[target]
            if parts.fragment not in pages_target.ids:
                fail(path, f"missing target anchor {href}")

for phrase in ("HubSpot", "Three factual stories", "Individual photographs will be added", "Use these verified official links", "Practical questions", "8 8 guests"):
    if phrase in public:
        fail("dist", f"outdated editorial text: {phrase}")
if "instagram.com/embed" in public or "lightwidget" in public.lower():
    fail("dist", "remote Instagram/LightWidget embed present")

if errors:
    print("VALIDATION FAILED")
    for error in errors[:100]:
        print("-", error)
    raise SystemExit(1)
print(f"PASS: {len(expected)} public pages + {len(utility)} confirmations, route matrix, metadata, hreflang, structured data, sitemap, assets, forms and security configuration.")
