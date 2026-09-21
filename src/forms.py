"""Render the localized, Netlify-compatible forms and their utility pages."""

from html import escape

from src.form_data import FORM_COPY, LANGS, SUBJECTS
from src.presentation_data import ui


IG_HARAS = "https://www.instagram.com/haras_de_prepinson/"
IG_HOUSE = "https://www.instagram.com/prepinson_houses/"
MAP_HARAS = "https://maps.app.goo.gl/qU2NuF7tHseKitHJ6"
MAP_HOUSE = "https://maps.app.goo.gl/FzkorC926XiJ6Fzw7"
CONSENT_VERSION = "2026-09-20"


def _arrow_icon():
    """Return the same typographic SVG arrow on every platform."""
    return '<svg class="icon icon-arrow" aria-hidden="true" viewBox="0 0 16 16"><path d="M4 12 12 4M6 4h6v6"/></svg>'


def _copy(lang):
    return FORM_COPY[lang if lang in LANGS else "en"]


def _route(route):
    return (route or "").strip("/")


def _page_url(lang, route):
    clean = _route(route)
    return f"/{lang}/" + (f"{clean}/" if clean else "")


def _context(route):
    clean = _route(route)
    if clean == "houses/ortho-24":
        return "houses", "ortho-24", "ortho-24"
    if clean == "houses/ortho-25":
        return "houses", "ortho-25", "ortho-25"
    if clean == "houses":
        return "houses", "", "stay"
    if clean == "horses/for-sale":
        return "horses", "", "horse-search"
    if clean in {"horses", "horses/facilities"}:
        return "horses", "", "boarding"
    if clean == "horses/programmes":
        return "horses", "", "training"
    if clean.startswith("horses"):
        return "horses", "", "other"
    return "general", "", "other"


def _form_state_attributes(copy):
    return (
        f'data-label-idle="{escape(copy["send"], quote=True)}" '
        f'data-label-pending="{escape(copy["sending"], quote=True)}" '
        f'data-error-server="{escape(copy["server_error"], quote=True)}" '
        f'data-error-network="{escape(copy["network_error"], quote=True)}" '
        f'data-error-timeout="{escape(copy["timeout_error"], quote=True)}"'
    )


def _newsletter_state_attributes(copy):
    return (
        f'data-label-idle="{escape(copy["newsletter_submit"], quote=True)}" '
        f'data-label-pending="{escape(copy["sending"], quote=True)}" '
        f'data-error-server="{escape(copy["server_error"], quote=True)}" '
        f'data-error-network="{escape(copy["network_error"], quote=True)}" '
        f'data-error-timeout="{escape(copy["timeout_error"], quote=True)}"'
    )


def render_contact(lang, route):
    """Return the contextual contact section for a public page.

    Activities, legal, privacy and confirmation pages intentionally omit the
    repeated contact form. Other pages keep the six historic Netlify names.
    """
    lang = lang if lang in LANGS else "en"
    clean = _route(route)
    if clean in {"activities", "legal", "privacy", "contact/thanks", "newsletter/thanks"}:
        return ""

    copy = _copy(lang)
    area, property_name, selected = _context(clean)
    source_page = _page_url(lang, clean)
    form_name = f"contact-{lang}"
    action = f"/{lang}/contact/thanks/"
    direct = (
        f'<a href="mailto:thehouse@prepinson.com">thehouse@prepinson.com {_arrow_icon()}</a>'
        if area == "houses"
        else f'<a href="mailto:haras@prepinson.com">haras@prepinson.com {_arrow_icon()}</a>'
    )
    if area == "general":
        direct += f'<a href="mailto:thehouse@prepinson.com">thehouse@prepinson.com {_arrow_icon()}</a>'
    context_copy = (
        copy["contact_houses_copy"]
        if area == "houses"
        else copy["contact_sales_copy"]
        if clean == "horses/for-sale"
        else copy["contact_horses_copy"]
        if area == "horses"
        else copy["contact_copy"]
    )
    options = "".join(
        f'<option value="{escape(key, quote=True)}"' + (" selected" if key == selected else "") + f'>{escape(label)}</option>'
        for key, label in SUBJECTS[lang]
    )

    return f'''<section id="contact" class="contact-section" aria-labelledby="contact-title">
  <div class="container contact-layout">
    <div class="contact-copy">
      <p class="eyebrow">{escape(copy['contact_eyebrow'])}</p>
      <h2 id="contact-title">{copy['contact_title']}</h2>
      <p>{escape(context_copy)}</p>
      <div class="contact-direct">{direct}<a href="tel:+32470851310">+32 470 85 13 10</a></div>
    </div>
    <form class="contact-form" name="{form_name}" method="POST" action="{action}" data-netlify="true" netlify-honeypot="company" data-progressive-form {_form_state_attributes(copy)}>
      <input type="hidden" name="form-name" value="{form_name}">
      <input type="hidden" name="language" value="{lang}">
      <input type="hidden" name="source_page" value="{escape(source_page, quote=True)}">
      <input type="hidden" name="context" value="{area}">
      <input type="hidden" name="property" value="{property_name}">
      <p class="form-trap" aria-hidden="true"><label>{escape(copy['trap'])}<input name="company" tabindex="-1" autocomplete="off"></label></p>
      <div class="form-grid">
        <label><span>{escape(copy['name'])}</span><input type="text" name="name" autocomplete="name" required></label>
        <label><span>{escape(copy['email'])}</span><input type="email" name="email" autocomplete="email" required></label>
      </div>
      <label><span>{escape(copy['subject'])}</span><select name="subject" required>{options}</select></label>
      <label><span>{escape(copy['message'])}</span><textarea name="message" rows="5" required></textarea></label>
      <label class="form-consent"><input type="checkbox" name="privacy_acknowledged" value="yes" required><span>{escape(copy['privacy'])} <a href="/{lang}/privacy/">{escape(copy['privacy_link'])}</a></span></label>
      <p class="form-required">{escape(copy['required_note'])}</p>
      <p class="form-status" data-form-status role="status" aria-live="polite" hidden></p>
      <button class="btn dark" type="submit"><span data-submit-label>{escape(copy['send'])}</span>{_arrow_icon()}</button>
    </form>
  </div>
</section>'''


def render_footer(lang, route):
    """Return the V1 footer with the shared, functional newsletter form."""
    lang = lang if lang in LANGS else "en"
    clean = _route(route)
    copy = _copy(lang)
    source_page = _page_url(lang, clean)
    action = f"/{lang}/newsletter/thanks/"

    return f'''<footer class="footer haras-footer">
  <div class="container">
    <div class="updates-row">
      <div><p class="eyebrow">PREPINSON</p><h2>{escape(copy['newsletter_title'])}</h2><p>{escape(copy['newsletter_copy'])}</p></div>
      <form class="updates-form" id="prepinson-updates" name="newsletter" method="POST" action="{action}" data-netlify="true" netlify-honeypot="company" data-progressive-form {_newsletter_state_attributes(copy)}>
        <input type="hidden" name="form-name" value="newsletter">
        <input type="hidden" name="language" value="{lang}">
        <input type="hidden" name="consent_version" value="{CONSENT_VERSION}">
        <input type="hidden" name="source_page" value="{escape(source_page, quote=True)}">
        <p class="form-trap" aria-hidden="true"><label>{escape(copy['trap'])}<input name="company" tabindex="-1" autocomplete="off"></label></p>
        <div class="updates-fields">
          <label class="updates-email"><span class="visually-hidden">{escape(copy['newsletter_email'])}</span><input type="email" name="email" autocomplete="email" placeholder="{escape(copy['newsletter_email'], quote=True)}" required></label>
          <button type="submit"><span data-submit-label>{escape(copy['newsletter_submit'])}</span>{_arrow_icon()}</button>
        </div>
        <label class="updates-consent"><input type="checkbox" name="consent" value="yes" required><span>{escape(copy['newsletter_consent'])}</span></label>
        <p class="updates-note">{escape(copy['newsletter_note'])} <a href="/{lang}/privacy/">{escape(copy['privacy_link'])}</a></p>
        <p class="form-status" data-form-status role="status" aria-live="polite" hidden></p>
      </form>
    </div>
    <div class="footer-social">
      <div><p class="eyebrow">{escape(copy['horses']).upper()}</p><a href="mailto:haras@prepinson.com">haras@prepinson.com</a><a href="{IG_HARAS}" target="_blank" rel="noopener noreferrer">@haras_de_prepinson {_arrow_icon()}</a></div>
      <div><p class="eyebrow">{escape(copy['houses']).upper()}</p><a href="mailto:thehouse@prepinson.com">thehouse@prepinson.com</a><a href="{IG_HOUSE}" target="_blank" rel="noopener noreferrer">@prepinson_houses {_arrow_icon()}</a></div>
      <div><p class="eyebrow">{escape(copy['visit']).upper()}</p><address>Ortho 24<br>6983 La Roche-en-Ardenne<br>{ui("country", lang)}</address><a href="{MAP_HARAS}" target="_blank" rel="noopener noreferrer">{escape(copy['haras_map'])} {_arrow_icon()}</a><a href="{MAP_HOUSE}" target="_blank" rel="noopener noreferrer">{escape(copy['house_map'])} {_arrow_icon()}</a></div>
    </div>
    <div class="footer-signature" aria-hidden="true">PREPINSON</div>
    <div class="footer-bottom"><span>© 2026 HARAS DE PREPINSON</span><div class="footer-legal"><a href="/{lang}/legal/">{escape(copy['legal'])}</a><a href="/{lang}/privacy/">{escape(copy['privacy_link'])}</a></div></div>
  </div>
</footer>'''


def render_confirmation(lang, kind):
    """Return a localized Contact or Newsletter confirmation page body."""
    lang = lang if lang in LANGS else "en"
    if kind not in {"contact", "newsletter"}:
        raise ValueError("kind must be 'contact' or 'newsletter'")
    copy = _copy(lang)
    title = copy[f"{kind}_success_title"]
    body = copy[f"{kind}_success_copy"]
    return f'''<section class="confirmation-page text-page container" id="content">
  <p class="eyebrow">PREPINSON</p>
  <h1>{escape(title)}</h1>
  <p>{escape(body)}</p>
  <a class="btn dark" href="/{lang}/">{escape(copy['back'])} {_arrow_icon()}</a>
</section>'''


def render_dialogs(lang):
    """Return the shared, localized film and lightbox dialogs."""
    copy = _copy(lang if lang in LANGS else "en")
    return f'''<dialog class="dialog video-dialog" data-video-modal aria-label="{escape(copy['film'], quote=True)}">
  <button class="dialog-close" type="button" data-dialog-close aria-label="{escape(copy['close_film'], quote=True)}">×</button>
  <video controls playsinline preload="none"></video>
  <p class="dialog-caption">Prepinson · Papilio Productions</p>
</dialog>
<dialog class="dialog lightbox" data-lightbox aria-label="{escape(copy['gallery'], quote=True)}">
  <button class="dialog-close" type="button" data-dialog-close aria-label="{escape(copy['close_gallery'], quote=True)}">×</button>
  <img data-lightbox-image width="1200" height="800" alt="">
  <div class="lightbox-controls"><button type="button" data-lightbox-prev aria-label="{escape(copy['previous'], quote=True)}">←</button><span data-lightbox-caption></span><button type="button" data-lightbox-next aria-label="{escape(copy['next'], quote=True)}">→</button></div>
</dialog>'''
