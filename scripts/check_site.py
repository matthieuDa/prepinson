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
from src.site_data import LANGS, ROUTES  # noqa: E402

DOMAIN = "https://www.prepinson.com"
ASSET_DOMAIN = os.environ.get("DEPLOY_PRIME_URL", DOMAIN).rstrip("/") if os.environ.get("PREVIEW_MODE") == "true" else DOMAIN
errors = []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs = []
        self.ids = set()
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
            self.ids.add(values["id"])
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
actual = set(DIST.glob("*/**/index.html")) - {DIST / "index.html"}
if actual != expected:
    fail("dist", f"route matrix mismatch; missing={sorted(map(str, expected-actual))}, extra={sorted(map(str, actual-expected))}")

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
    if metas.get("og:image") != ASSET_DOMAIN + "/assets/og-prepinson.jpg":
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
            fail(rel, "third-party script present")
        if tag == "img":
            if attrs.get("class") == "hero-image" and (attrs.get("loading") == "lazy" or attrs.get("fetchpriority") != "high"):
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
                path_part = candidate.strip().split()[0]
                if path_part.startswith("/") and not (DIST / path_part.lstrip("/")).exists():
                    fail(rel, f"missing responsive asset {path_part}")

gateway = (DIST / "index.html").read_text(encoding="utf-8")
if 'name="robots" content="noindex,follow"' not in gateway:
    fail("index.html", "root gateway must be non-indexable fallback")
for lang in LANGS:
    if f'href="/{lang}/"' not in gateway:
        fail("index.html", f"missing gateway link for {lang}")

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
if "newsletter" in public.lower() and re.search(r'<form[^>]+newsletter', public, re.I):
    fail("dist", "newsletter form must remain inactive")
if "instagram.com/embed" in public or "lightwidget" in public.lower():
    fail("dist", "remote Instagram/LightWidget embed present")

if errors:
    print("VALIDATION FAILED")
    for error in errors[:100]:
        print("-", error)
    raise SystemExit(1)
print(f"PASS: {len(expected)} localized pages, route matrix, metadata, hreflang, structured data, sitemap, assets, forms and security configuration.")
