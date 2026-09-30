"""Shared navigation and breadcrumbs for every locale and both menus."""
from html import escape
from src.site_data import text

GROUPS = (
 ('nav_haras', (('nav_presentation', '#haras'), ('nav_team', 'team'), ('nav_facilities', 'horses/facilities'))),
 ('nav_horses', (('nav_overview', 'horses'), ('nav_boarding', 'horses/boarding'), ('nav_training', 'horses/programmes'), ('nav_sales', 'horses/for-sale'), ('nav_references', 'horses/references'))),
 ('nav_houses', (('nav_discover_houses', 'houses'), ('La Grange', 'houses/ortho-24'), ('Le Cottage', 'houses/ortho-25'), ('nav_activities', 'activities'))),
)

def href(lang, route):
    return f'/{lang}/' + (route if route.startswith('#') else route.strip('/') + '/' if route else '')

def label(key, lang):
    return key if key in {'La Grange','Le Cottage'} else text(key, lang)

def link(key, target, lang, current):
    active = ' aria-current="page"' if current == target else ''
    return f'<a href="{href(lang,target)}"{active}>{escape(label(key,lang))}</a>'

def menu(lang, current, mobile=False):
    groups = []
    for key, children in GROUPS:
        active = any(target == current for _, target in children)
        links = ''.join(link(k, target, lang, current) for k, target in children)
        groups.append(f'<details class="nav-group{" current-group" if active else ""}"><summary>{escape(label(key,lang))}<svg class="icon" aria-hidden="true"><use href="/icons.svg#chevron-down"/></svg></summary><div class="nav-submenu">{links}</div></details>')
    return ''.join(groups) + f'<a class="nav-book" href="/{lang}/contact/"' + (' aria-current="page"' if current == 'contact' else '') + f'>{text("nav_contact",lang)}</a>'

def footer_navigation(lang, current):
    columns = []
    for key, children in GROUPS:
        columns.append(f'<div><h3>{escape(label(key,lang))}</h3>' + ''.join(link(k,target,lang,current) for k,target in children) + '</div>')
    columns.append(f'<div><h3>{text("nav_contact",lang)}</h3>{link("nav_access","contact",lang,current)}<a href="mailto:sales@prepinson.com">sales@prepinson.com</a><a href="tel:+32470851310">+32 470 85 13 10</a><a href="/{lang}/#journal">{text("journal_nav",lang)}</a></div>')
    return f'<nav class="footer-navigation" aria-label="{text("menu",lang)}">{"".join(columns)}</nav>'

def crumbs(lang, route):
    if not route: return []
    items = [(text('nav_home',lang), href(lang,''))]
    if route.startswith('horses/'):
        items.append((text('nav_horses',lang),href(lang,'horses')))
    elif route.startswith('houses/') or route == 'activities':
        items.append((text('nav_houses',lang),href(lang,'houses')))
    key = next((key for _, children in GROUPS for key,target in children if target == route), None)
    key = key or {'contact':'nav_access','legal':'legal_heading','privacy':'privacy_label'}.get(route,'nav_home')
    items.append((label(key,lang),href(lang,route)))
    return items

def breadcrumbs(lang, route):
    items = crumbs(lang,route)
    if not items: return ''
    links = ''.join(f'<li><a href="{url}">{escape(name)}</a></li>' if i < len(items)-1 else f'<li aria-current="page">{escape(name)}</li>' for i,(name,url) in enumerate(items))
    return f'<nav class="breadcrumbs container" aria-label="{text("breadcrumb",lang)}"><ol>{links}</ol></nav>'
