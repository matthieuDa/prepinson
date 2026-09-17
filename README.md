# Prépinson

Start from this directory with `./run.sh`, then open http://localhost:3008.
Requires Node.js 20 or later. No package installation, API keys, database or build is needed. The homepage focuses on the haras; houses are accessed from the navigation.
Stop with Ctrl+C.

The five page types are available in six languages (30 static HTML pages): English at `/`, French at `/fr/`, German at `/de/`, Swedish at `/sv/`, Dutch at `/nl/` and Luxembourgish at `/lb/`. Each language selector keeps the current page. Shared SVG icons replace text-symbol controls on all devices.

`dist/` contains the ready-to-run site, shared CSS/JS, SVG icons and local media. `server.mjs` supports video range requests. Run `./scripts/build.sh` with Python 3 to regenerate all languages from `work/build.py`, `work/home-haras.html`, `src/journal.html`, `src/programmes.html` and `src/locales/*.tsv`. A build is not needed to launch. Run `npm run check` and `python3 scripts/check_site.py` for syntax, local links, icons and language-alternate checks.

Features: responsive navigation, original estate film, keyboard-accessible photo lightboxes, individual house pages, official team profiles, expanded archive gallery, verified external booking and Instagram links for both the haras and houses, Netlify-ready contact and mailing-list forms, a branded favicon, semantic HTML, page descriptions, canonical URLs, JSON-LD, translated metadata, reciprocal hreflang links and a multilingual sitemap.

Content sources: the existing official Prépinson site, the linked Casapilot Grange listing and Airbnb Ortho25 listing. Media provenance is recorded in work/asset-sources.json and work/property-sources.json. Media belongs to its respective owners; this is the requested local redesign.

Before public launch: Eva should confirm rental amenities and photo selection, and supply selected completed sale references and any newer horse imagery. The three named horses are verified breeding examples, not claimed sales or current availability. Only verified booking destinations are used: Grange on Casapilot, Cottage on Airbnb. No second platform listing is invented. Canonical URLs and sitemap assume publication on www.prepinson.com. Google Fonts provides typography with system fallbacks. The homepage embeds the official Instagram profile through instagram.com/embed.js; a permanent direct profile link remains available if Instagram is blocked. The feed was verified displaying the real profile and six recent posts locally.

Instagram-derived editorial content: four training stages (foal handling, pre-breaking, breaking in and show jumping training) and three short journal cards, linking to the original public posts. Sources: https://www.instagram.com/p/DdJgK95CPEn/ (programmes), https://www.instagram.com/p/Dc_CsCqiNez/ (breeding), https://www.instagram.com/p/Dc3el30CMPW/ (training season). Card photographs come from the official Prépinson website. The live Instagram embed remains in Instagram’s own language; all surrounding site content is translated.
