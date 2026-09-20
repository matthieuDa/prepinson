# Prepinson website

Six-language static website for Haras de Prepinson and the two holiday houses. The approved visual baseline is commit `fd597a0`; the current generator retains localized routes, technical SEO, secure forms and preview protection.

## Local use

Run `./scripts/build.sh`, then `./run.sh` and open `http://localhost:3008/en/`.

The generator produces 72 public pages, 12 non-indexable form confirmations and a language gateway. Route and editorial data live in `src/site_data.py`; V1 presentation copy/media in `src/presentation_data.py`; forms and consent translations in `src/forms.py` and `src/form_data.py`. CSS, JavaScript and icon sources live in `src/`; edit these sources, never generated pages.

## Validation

Run `npm run check` and `python3 scripts/security_scan.py` before committing. Browser checks require Playwright and Chrome; install the tooling separately or set `PLAYWRIGHT_MODULE` to its module directory and `CHROME_PATH` to the browser executable.

- `node scripts/check_forms.mjs`: simulated submissions only, six languages, validation, failure/success, no-JS and keyboard interactions.
- `node scripts/check_layout.mjs`: all 72 pages at seven widths, plus loaded photographs in reference screenshots.
- `LIGHTHOUSE_CLI=… CHROME_PATH=… node scripts/audit_lighthouse.mjs`: full audits of 12 templates on mobile/desktop. `AUDIT_ROUTES=home,ortho-25 AUDIT_PROFILES=mobile` selects a relevant regression check; no audits are excluded.

Reports and screenshots go to ignored `outputs/v1-restoration/`. These diagnostic artifacts are not deployed.

## Images and fonts

The approved photographs are served as AVIF with WebP fallback and responsive sizes. Portrait hero variants avoid downloading unseen horizontal pixels on phones. `src/image-manifest.json` records dimensions and variants. To regenerate them from the approved local sources, use `node scripts/optimize_images.mjs` with Sharp installed (or `SHARP_MODULE` pointing to its package directory). This optional media step is not repeated during Netlify builds. Local font sources and licenses are documented under `src/font-sources.json` and `dist/assets/fonts/`.

## Forms and deployment

Newsletter subscriptions use one Netlify form named `newsletter`, with explicit consent, locale, consent version and source path. Contact retains six `contact-{lang}` forms. POST actions use localized confirmation routes, not the root language redirect. Netlify stores submissions; campaign delivery is not included. Live receipt must be checked in the site account after inspecting notification settings.

Netlify runs the same static build. `/` uses an Edge Function to choose the visitor’s saved language or `Accept-Language`; explicit language URLs remain stable. Deploy Previews receive `X-Robots-Tag: noindex, nofollow, noarchive`. Production publication, domain migration and external account changes are outside this delivery.
