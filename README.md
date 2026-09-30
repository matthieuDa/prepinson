# Prepinson website

Six-language static website for Haras de Prepinson and the two holiday houses. The approved visual baseline is commit `fd597a0`; the current generator retains localized routes, technical SEO, secure forms and preview protection.

## Local use

Run `pnpm install` once, then `./run.sh` and open `http://localhost:3008/en/`. The server refreshes the local build before it starts. You can also run `./scripts/build.sh` separately.

The generator produces 72 public pages, 12 non-indexable form confirmations and a language gateway. Route and editorial data live in `src/site_data.py`; V1 presentation copy/media in `src/presentation_data.py`; forms and consent translations in `src/forms.py` and `src/form_data.py`. CSS, JavaScript and icon sources live in `src/`; edit these sources, never generated pages.

## Instagram feed

The home page displays up to six recent posts from `@haras_de_prepinson` using the official Instagram API. For local builds, put `INSTAGRAM_ACCESS_TOKEN=...` in the ignored `.env` file (or set it in the build environment). `work/instagram.py` fetches new images only, reduces them to at most 800 pixels on each side, and converts them to WebP under `dist/assets/instagram/`; it renews a local `.env` token after seven days. A failed update keeps the last complete snapshot. The browser requests only files from this site, near the Instagram section. The six current images total about 384 KB; the site checker enforces a 1.2 MB maximum for future snapshots. If the feed is unavailable, the direct profile link remains visible and a translated retry button appears when JavaScript is running.

On Netlify, set `INSTAGRAM_ACCESS_TOKEN` as a secret environment variable for Production and Deploy Previews. Restrict it to Functions scope when the plan offers custom scopes; on the Free plan, scopes cannot be customized, so keep the token in the Netlify UI and out of build output. Netlify builds skip the static snapshot. A deploy event initializes an empty Blob store in production or a deploy-specific store in a Deploy Preview; `refresh-instagram` then syncs production twice daily. The sync reuses unchanged WebP images, publishes the feed only after all selected images are ready, retains older images for seven days, and refreshes the token every seven days. A temporary token refresh failure does not interrupt a sync while the existing token still works. The browser reads `/instagram-feed.json`, rewritten to a function on Netlify; the local server serves the build snapshot. These functions use Netlify's durable CDN cache: five minutes for the feed and one day for images. The first visitor never waits for image conversion. Do not commit `.env` or paste the token into source files.

If Meta revokes access or the token expires, reconnect `@haras_de_prepinson` in the Meta app, replace the Functions-scoped Netlify secret, and clear the private Blob key `token` before running `refresh-instagram` again. The public feed keeps its last good version until a successful sync. Inspect function logs; never log or disclose tokens.

`/instagram-health.json` returns only `healthy`, `postCount`, and `ageHours`. It returns HTTP 503 if there are fewer than six posts, the feed is missing, or the last successful sync is more than 36 hours old. At publication, configure a free HTTP monitor such as [UptimeRobot](https://uptimerobot.com/pricing/) for this URL with email alerts to the site's technical contact; do not use the public customer address without approval. Check the published function and its alert once. Netlify's scheduled functions run automatically only on published deploys.

The production checklist and incident steps are in [PUBLICATION_INSTAGRAM.md](PUBLICATION_INSTAGRAM.md).

## Validation

Run `npm run check` and `python3 scripts/security_scan.py` before committing. Browser checks require Playwright and Chrome; install the tooling separately or set `PLAYWRIGHT_MODULE` to its module directory and `CHROME_PATH` to the browser executable.

- `npm run test:instagram`: in-memory synchronization, image retention, cache headers, cold start, token renewal failures, and health checks.
- `node scripts/check_forms.mjs`: simulated submissions only, six languages, validation, failure/success, no-JS and keyboard interactions.
- `node scripts/check_layout.mjs`: all 72 pages at seven widths, plus loaded photographs in reference screenshots.
- `LIGHTHOUSE_CLI=… CHROME_PATH=… node scripts/audit_lighthouse.mjs`: full audits of 12 templates on mobile/desktop. `AUDIT_ROUTES=home,ortho-25 AUDIT_PROFILES=mobile` selects a relevant regression check; no audits are excluded.

Reports and screenshots go to ignored `outputs/v1-restoration/`. These diagnostic artifacts are not deployed.

## Images and fonts

The approved photographs are served as AVIF with WebP fallback and responsive sizes. Portrait hero variants avoid downloading unseen horizontal pixels on phones. `src/image-manifest.json` records dimensions and variants. To regenerate them from the approved local sources, use `node scripts/optimize_images.mjs` with Sharp installed (or `SHARP_MODULE` pointing to its package directory). This optional media step is not repeated during Netlify builds. Local font sources and licenses are documented under `src/font-sources.json` and `dist/assets/fonts/`.

## Forms and deployment

Newsletter subscriptions use one Netlify form named `newsletter`, with explicit consent, locale, consent version and source path. Contact retains six `contact-{lang}` forms. POST actions use localized confirmation routes, not the root language redirect. Netlify stores submissions; campaign delivery is not included. Live receipt must be checked in the site account after inspecting notification settings.

Netlify runs the same static build. `/` uses an Edge Function to choose the visitor’s saved language or `Accept-Language`; explicit language URLs remain stable. Deploy Previews receive `X-Robots-Tag: noindex, nofollow, noarchive`. Production publication, domain migration and external account changes are outside this delivery.
