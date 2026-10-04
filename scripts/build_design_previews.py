"""Build isolated CSS proposals from an unchanged generated reference site."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
SOURCE = ROOT / 'src/designs'
VARIANTS = ('equilibre', 'editorial', 'serein')
LANGS = ('fr', 'en', 'nl', 'de', 'sv', 'lb')
MARKER_START = '<!-- design-preview:start -->'
MARKER_END = '<!-- design-preview:end -->'


def build():
    subprocess.run([sys.executable, str(ROOT / 'work/build.py')], cwd=ROOT, check=True)
    pages = sorted(OUT.rglob('*.html'))
    preview = OUT / 'propositions'
    static = preview / 'assets'
    static.mkdir(parents=True, exist_ok=True)
    for name in ('refinement.css', 'refinement.js', *(v + '.css' for v in VARIANTS), 'comparison.css', 'comparison.js'):
        shutil.copy2(SOURCE / name, static / name)
    if (SOURCE / 'previews').exists():
        shutil.copytree(SOURCE / 'previews', static / 'previews', dirs_exist_ok=True)
    if (SOURCE / 'illustrations').exists():
        shutil.copytree(SOURCE / 'illustrations', static / 'illustrations', dirs_exist_ok=True)
    version = hashlib.sha256(b''.join((SOURCE / n).read_bytes() for n in ('refinement.css', 'refinement.js', *(v + '.css' for v in VARIANTS)))).hexdigest()[:12]
    integrity = []
    pattern = r'\b(href|action)="(/(?:en|fr|nl|de|sv|lb)/[^"\s]*)"'
    for variant in VARIANTS:
        prefix = '/propositions/' + variant
        extra = (MARKER_START + '<meta name="robots" content="noindex,nofollow">'
                 + f'<link rel="stylesheet" href="/propositions/assets/refinement.css?v={version}">'
                 + f'<link rel="stylesheet" href="/propositions/assets/{variant}.css?v={version}">'
                 + f'<script src="/propositions/assets/refinement.js?v={version}" defer></script>' + MARKER_END)
        for page in pages:
            original = page.read_text()
            html = re.sub(pattern, lambda m: f'{m[1]}="{prefix}{m[2]}"', original)
            html = html.replace('</head>', extra + '</head>')
            target = preview / variant / page.relative_to(OUT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html)
            # A strict round trip proves texts, media, semantics and behaviours weren't rewritten.
            normalized = html.replace(extra, '').replace(prefix + '/', '/')
            if normalized != original:
                raise RuntimeError(f'Content drift: {target}')
            integrity.append(str(target.relative_to(OUT)))
    shutil.copy2(SOURCE / 'comparison.html', preview / 'index.html')
    (preview / 'integrity.json').write_text(json.dumps({'reference_commit': '7c464e89719ebffb9e9464359724cafe8eb7e518', 'version': version, 'languages': LANGS, 'variants': VARIANTS, 'identical_pages_per_variant': len(pages), 'content_verified': len(integrity)}, indent=2))
    with (OUT / '_headers').open('a') as headers:
        headers.write('\n/propositions/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n')
    print(f'Built {len(integrity)} isolated proposal pages; original content and assets preserved.')


if __name__ == '__main__':
    build()
