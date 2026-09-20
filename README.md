# Prepinson website

Static, six-language website for Haras de Prepinson and the two Prepinson holiday houses.

## Local use

Run `./scripts/build.sh`, then `./run.sh` and open `http://localhost:3008/en/`.

The generator writes 12 routes in English, French, Dutch, German, Swedish and Luxembourgish. `src/site_data.py` is the shared route and translation registry; `work/build.py` generates the HTML, metadata, structured data, `robots.txt`, `sitemap.xml`, Netlify form markup and language alternates.

Run `python3 scripts/check_site.py` and `npm run check` before committing. Netlify runs the same build. The root path uses an Edge Function to select the visitor’s language from the saved preference and then `Accept-Language`; every explicit language URL remains stable.

Deploy Previews receive `X-Robots-Tag: noindex, nofollow, noarchive`. The production configuration remains indexable, but production publication and domain migration are outside this delivery.
