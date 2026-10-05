"""Legacy WordPress URLs inventoried from the live sitemap on 2026-09-30.

Removed seminar/partner offers have no equivalent and return a real 404.
Language homepages remain stable. Redirects precede the generic fallback.
"""
LEGACY_ROUTES = (
 ('/about-us/', '/en/team/', 301),
 ('/fr/a-propos-de-nous/', '/fr/team/', 301),
 ('/contact-us/', '/en/contact/', 301),
 ('/fr/contactez-nous/', '/fr/contact/', 301),
 ('/horses/', '/en/horses/', 301),
 ('/fr/chevaux/', '/fr/horses/', 301),
 ('/horses-gallery/', '/en/horses/facilities/', 301),
 ('/fr/galerie-des-chevaux/', '/fr/horses/facilities/', 301),
 ('/the-house-gallery/', '/en/houses/', 301),
 ('/fr/la-galerie-photo-de-la-maison/', '/fr/houses/', 301),
 ('/partners/', '/en/partners/', 301),
 ('/fr/partenaires/', '/fr/partners/', 301),
 ('/event-type-pages/', '/404.html', 404),
 ('/equicoaching-retreat/', '/404.html', 404),
 ('/wp-sitemap.xml', '/sitemap.xml', 301),
 ('/page-sitemap.xml', '/sitemap.xml', 301),
)

def render_redirects():
    return ''.join(f'{old} {new} {status}\n' for old,new,status in LEGACY_ROUTES)
