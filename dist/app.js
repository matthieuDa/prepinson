(() => {
  'use strict';

  const body = document.body;
  const menuButton = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('#mobile-menu');
  const languageSwitches = Array.from(document.querySelectorAll('details.language-switch'));
  const pageMain = document.querySelector('main');
  const pageFooter = document.querySelector('footer');

  if (body.dataset.page === '404') {
    const supported = ['en', 'fr', 'nl', 'de', 'sv', 'lb'];
    const browserLanguage = (navigator.languages?.[0] || navigator.language || 'en').toLowerCase();
    const language = supported.find((code) => browserLanguage === code || browserLanguage.startsWith(`${code}-`)) || 'en';
    const copy = {
      en: ['This path seems to have wandered off.', 'Even the horses take the wrong trail sometimes. Let us take you back to Prepinson.', 'Return to Prepinson'],
      fr: ['Cette page semble s’être égarée.', 'Même les chevaux se trompent parfois de chemin. Revenons ensemble à Prepinson.', 'Revenir à Prepinson'],
      nl: ['Deze pagina lijkt verdwaald.', 'Ook paarden nemen soms het verkeerde pad. We brengen u terug naar Prepinson.', 'Terug naar Prepinson'],
      de: ['Diese Seite scheint sich verirrt zu haben.', 'Auch Pferde nehmen manchmal den falschen Weg. Zurück nach Prepinson.', 'Zurück zu Prepinson'],
      sv: ['Den här sidan verkar ha gått vilse.', 'Även hästar tar ibland fel väg. Vi tar dig tillbaka till Prepinson.', 'Tillbaka till Prepinson'],
      lb: ['Dës Säit schéngt sech verirrt ze hunn.', 'Och Päerd huelen heiansdo de falsche Wee. Zeréck op Prepinson.', 'Zeréck op Prepinson'],
    };
    document.documentElement.lang = language;
    const home = `/${language}/`;
    document.querySelector('[data-404-title]').textContent = copy[language][0];
    document.querySelector('[data-404-copy]').textContent = copy[language][1];
    const action = document.querySelector('[data-404-action]');
    action.firstChild.textContent = `${copy[language][2]} `;
    action.href = home;
    document.querySelector('[data-404-home]').href = home;
  }

  const openDialogs = () => Array.from(document.querySelectorAll('dialog[open]'));
  const syncScrollLock = () => {
    const menuOpen = Boolean(mobileMenu?.classList.contains('open'));
    body.classList.toggle('locked', menuOpen || openDialogs().length > 0);
  };

  const setPageInert = (inert) => {
    if (pageMain) pageMain.inert = inert;
    if (pageFooter) pageFooter.inert = inert;
    document.querySelectorAll('.nav .brand, .nav .navlinks, .nav .language-switch').forEach((element) => {
      element.inert = inert;
    });
  };

  const setMenu = (open, restoreFocus = false) => {
    if (!menuButton || !mobileMenu) return;
    mobileMenu.classList.toggle('open', open);
    mobileMenu.setAttribute('aria-hidden', String(!open));
    menuButton.setAttribute('aria-expanded', String(open));
    setPageInert(open);
    if (open) {
      languageSwitches.forEach((details) => details.removeAttribute('open'));
      mobileMenu.querySelector('a, button')?.focus();
    } else if (restoreFocus) {
      menuButton.focus();
    }
    syncScrollLock();
  };

  if (menuButton && mobileMenu) {
    mobileMenu.setAttribute('aria-hidden', 'true');
    menuButton.addEventListener('click', () => {
      setMenu(menuButton.getAttribute('aria-expanded') !== 'true');
    });
    mobileMenu.addEventListener('click', (event) => {
      if (event.target.closest('a')) setMenu(false);
    });
    const desktopQuery = window.matchMedia('(min-width: 1251px)');
    const closeAtDesktop = (event) => {
      if (event.matches && mobileMenu.classList.contains('open')) setMenu(false);
    };
    if (typeof desktopQuery.addEventListener === 'function') desktopQuery.addEventListener('change', closeAtDesktop);
    else desktopQuery.addListener(closeAtDesktop);
  }

  languageSwitches.forEach((details) => {
    details.addEventListener('toggle', () => {
      if (!details.open) return;
      languageSwitches.forEach((other) => {
        if (other !== details) other.removeAttribute('open');
      });
      if (mobileMenu?.classList.contains('open')) setMenu(false);
    });
  });

  document.querySelectorAll('[data-exclusive-details]').forEach((group) => {
    const items = Array.from(group.querySelectorAll(':scope > details'));
    items.forEach((details) => {
      details.addEventListener('toggle', () => {
        if (!details.open) return;
        items.forEach((other) => {
          if (other !== details) other.removeAttribute('open');
        });
      });
    });
  });

  document.addEventListener('click', (event) => {
    languageSwitches.forEach((details) => {
      if (details.open && !details.contains(event.target)) details.removeAttribute('open');
    });
  });

  document.querySelectorAll('a[data-language]').forEach((link) => {
    const language = link.getAttribute('data-language');
    if (location.hash) {
      try {
        const target = new URL(link.href, location.href);
        if (target.origin === location.origin) {
          target.hash = location.hash;
          link.href = target.href;
        }
      } catch (_) {
        // The original localized URL remains usable.
      }
    }
    link.addEventListener('click', () => {
      if (!language) return;
      const secure = location.protocol === 'https:' ? '; Secure' : '';
      document.cookie = `prepinson-language=${encodeURIComponent(language)}; Max-Age=31536000; Path=/; SameSite=Lax${secure}`;
      try {
        localStorage.setItem('prepinson-language', language);
      } catch (_) {
        // The cookie is sufficient when storage is unavailable.
      }
    });
  });

  const dialogTriggers = new WeakMap();
  const showDialog = (dialog, trigger) => {
    if (!dialog || dialog.open) return;
    dialogTriggers.set(dialog, trigger);
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
    syncScrollLock();
  };

  document.querySelectorAll('dialog').forEach((dialog) => {
    dialog.querySelectorAll('[data-dialog-close], [data-close]').forEach((button) => {
      button.addEventListener('click', () => dialog.close());
    });
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener('close', () => {
      syncScrollLock();
      const trigger = dialogTriggers.get(dialog);
      if (trigger?.isConnected) trigger.focus();
    });
  });

  const videoDialog = document.querySelector('[data-video-modal]');
  const dialogVideo = videoDialog?.querySelector('video');
  document.querySelectorAll('[data-video-open], [data-film]').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      if (!videoDialog || !dialogVideo) return;
      const source = trigger.getAttribute('data-video-open') || trigger.getAttribute('data-film');
      if (!source) return;
      dialogVideo.src = source;
      showDialog(videoDialog, trigger);
      dialogVideo.play().catch(() => {
        // Native controls remain available when autoplay is declined.
      });
    });
  });
  videoDialog?.addEventListener('close', () => {
    dialogVideo?.pause();
    dialogVideo?.removeAttribute('src');
    dialogVideo?.load();
  });

  const lightbox = document.querySelector('[data-lightbox]');
  const lightboxImage = lightbox?.querySelector('[data-lightbox-image], img');
  const lightboxCaption = lightbox?.querySelector('[data-lightbox-caption], .lightbox-label');
  const lightboxItems = Array.from(document.querySelectorAll('[data-lightbox-item], [data-gallery]'));
  let selectedImage = 0;

  const showImage = (position) => {
    if (!lightboxImage || lightboxItems.length === 0) return;
    selectedImage = (position + lightboxItems.length) % lightboxItems.length;
    const item = lightboxItems[selectedImage];
    const sourceImage = item.querySelector('img');
    const source = item.getAttribute('data-lightbox-src') || sourceImage?.currentSrc || sourceImage?.src;
    const alt = item.getAttribute('data-lightbox-alt') || sourceImage?.alt || '';
    if (!source) return;
    lightboxImage.src = source;
    lightboxImage.alt = alt;
    if (lightboxCaption) {
      const detail = item.getAttribute('data-lightbox-caption') || alt;
      lightboxCaption.textContent = `${selectedImage + 1} / ${lightboxItems.length}${detail ? `: ${detail}` : ''}`;
    }
  };

  lightboxItems.forEach((item, index) => {
    item.addEventListener('click', () => {
      if (!lightbox) return;
      showImage(index);
      showDialog(lightbox, item);
    });
  });
  lightbox?.querySelector('[data-lightbox-prev], [data-prev]')?.addEventListener('click', () => showImage(selectedImage - 1));
  lightbox?.querySelector('[data-lightbox-next], [data-next]')?.addEventListener('click', () => showImage(selectedImage + 1));
  lightbox?.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') showImage(selectedImage - 1);
    if (event.key === 'ArrowRight') showImage(selectedImage + 1);
  });

  document.querySelectorAll('[data-contact-subject]').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const select = document.querySelector('#contact select[name="subject"]');
      if (!select) return;
      const requested = trigger.getAttribute('data-contact-subject');
      const option = Array.from(select.options).find((candidate) => candidate.value === requested || candidate.textContent.trim() === requested);
      if (option) {
        select.value = option.value;
        select.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  });

  const formDataAsParams = (form) => {
    const params = new URLSearchParams();
    new FormData(form).forEach((value, key) => {
      if (typeof value === 'string') params.append(key, value);
    });
    return params;
  };

  if ('fetch' in window && 'AbortController' in window && 'URLSearchParams' in window) {
    document.querySelectorAll('form[data-progressive-form]').forEach((form) => {
      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (form.dataset.submitting === 'true' || !form.reportValidity()) return;

        const button = form.querySelector('button[type="submit"]');
        const buttonLabel = button?.querySelector('[data-submit-label]');
        const status = form.querySelector('[data-form-status]');
        const controller = new AbortController();
        let timedOut = false;
        const timeout = window.setTimeout(() => {
          timedOut = true;
          controller.abort();
        }, 15000);

        form.dataset.submitting = 'true';
        form.setAttribute('aria-busy', 'true');
        if (button) button.disabled = true;
        if (buttonLabel) buttonLabel.textContent = form.dataset.labelPending || '';
        if (status) {
          status.hidden = true;
          status.textContent = '';
        }

        try {
          const response = await fetch(form.action, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formDataAsParams(form),
            credentials: 'same-origin',
            signal: controller.signal,
          });
          if (!response.ok) throw new Error('server');
          window.location.assign(form.action);
          return;
        } catch (error) {
          if (status) {
            status.textContent = timedOut
              ? form.dataset.errorTimeout
              : error.message === 'server'
                ? form.dataset.errorServer
                : form.dataset.errorNetwork;
            status.hidden = false;
          }
        } finally {
          window.clearTimeout(timeout);
          form.dataset.submitting = 'false';
          form.removeAttribute('aria-busy');
          if (button) button.disabled = false;
          if (buttonLabel) buttonLabel.textContent = form.dataset.labelIdle || '';
        }
      });
    });
  }

  // FeedPane creates its lightbox link before a post is selected. Give that
  // link the real profile destination until the widget supplies a permalink.
  const feedpaneFallback = document.querySelector('.feedpane-fallback a[href]');
  if (feedpaneFallback) {
    const initialiseFeedpaneLink = () => {
      const link = document.querySelector('.fp-lb-link');
      if (!link) return false;
      if (!link.getAttribute('href')) link.href = feedpaneFallback.href;
      return true;
    };
    if (!initialiseFeedpaneLink()) {
      const observer = new MutationObserver(() => {
        if (initialiseFeedpaneLink()) observer.disconnect();
      });
      observer.observe(document.body, { childList: true, subtree: true });
    }
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      languageSwitches.forEach((details) => {
        if (details.open) {
          details.removeAttribute('open');
          details.querySelector('summary')?.focus();
        }
      });
      if (mobileMenu?.classList.contains('open')) setMenu(false, true);
      return;
    }
    if (event.key !== 'Tab' || !mobileMenu?.classList.contains('open') || !menuButton) return;
    const focusable = [menuButton, ...mobileMenu.querySelectorAll('a[href], button:not([disabled])')];
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
})();
