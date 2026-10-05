(() => {
  'use strict';

  const body = document.body;
  const menuButton = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('#mobile-menu');
  const languageSwitches = Array.from(document.querySelectorAll('details.language-switch'));
  const pageMain = document.querySelector('main');
  const pageFooter = document.querySelector('footer');
  const header = document.querySelector('header.nav');
  const desktopQuery = window.matchMedia('(min-width: 1251px)');
  let navigationFocus = null;
  document.addEventListener('focusin', event => {
    if (event.target === body) return;
    navigationFocus = event.target.closest('.navlinks') ? 'desktop'
      : event.target.closest('#mobile-menu, [data-menu-toggle]') ? 'mobile' : null;
  });
  document.addEventListener('pointerdown', event => {
    if (!event.target.closest('.navlinks, #mobile-menu, [data-menu-toggle]')) navigationFocus = null;
  });

  // Overlay the hero at the top, then fix the header while it can hide and return on scroll.
  if (header) {
    const placeholder = document.createElement('div');
    placeholder.className = 'nav-placeholder';
    placeholder.hidden = true;
    placeholder.setAttribute('aria-hidden', 'true');
    if (header.classList.contains('solid-nav')) header.before(placeholder);
    let frame = 0;
    const updateHeader = () => {
      frame = 0;
      const stuck = window.scrollY >= 96;
      header.classList.toggle('is-stuck', stuck);
      placeholder.hidden = !stuck;
      document.documentElement.style.setProperty('--nav-panel-top', `${Math.max(0, header.getBoundingClientRect().bottom)}px`);
    };
    const scheduleHeader = () => { if (!frame) frame = requestAnimationFrame(updateHeader); };
    window.addEventListener('scroll', scheduleHeader, { passive: true });
    window.addEventListener('resize', scheduleHeader);
    if ('ResizeObserver' in window) new ResizeObserver(scheduleHeader).observe(header);
    updateHeader();
  }

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
    document.querySelector('.stay-ribbon')?.toggleAttribute('inert', inert);
    document.querySelectorAll('.nav .brand, .nav .navlinks, .nav .language-switch').forEach((element) => {
      element.inert = inert;
    });
  };

  const setMenu = (open, restoreFocus = false) => {
    if (!menuButton || !mobileMenu) return;
    mobileMenu.classList.toggle('open', open);
    header?.classList.toggle('mobile-menu-open', open);
    mobileMenu.setAttribute('aria-hidden', String(!open));
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? menuButton.dataset.closeLabel : menuButton.dataset.openLabel);
    menuButton.querySelector('span').textContent = menuButton.getAttribute('aria-label');
    menuButton.querySelector('use').setAttribute('href', open ? '/icons.svg#close' : '/icons.svg#menu');
    setPageInert(open);
    if (open) {
      languageSwitches.forEach((details) => details.removeAttribute('open'));
      mobileMenu.querySelector('summary, a, button')?.focus();
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
    const closeAtDesktop = (event) => {
      if (event.matches && mobileMenu.classList.contains('open')) {
        setMenu(false);
        if (navigationFocus === 'mobile') header?.querySelector('.navlinks summary')?.focus({ preventScroll: true });
      }
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
      navGroups.forEach(group => closeGroup(group));
    });
  });

  const navGroups = [...document.querySelectorAll('.nav-group')];
  const hoverQuery = window.matchMedia('(min-width: 1251px) and (hover: hover) and (pointer: fine)');
  const navStates = new Map(navGroups.map(group => [group, { enter: 0, leave: 0, inside: false, suppressed: false, hoverOpened: false }]));
  const clearTimers = state => { clearTimeout(state.enter); clearTimeout(state.leave); };
  const keyboardInside = group => group.contains(document.activeElement) && document.activeElement.matches(':focus-visible');
  const closeGroup = (group, suppress = false) => {
    const state = navStates.get(group);
    clearTimers(state);
    const summary = group.querySelector('summary');
    if (group.open && group.contains(document.activeElement) && document.activeElement !== summary) summary.focus({ preventScroll: true });
    state.hoverOpened = false;
    state.suppressed = suppress;
    group.open = false;
  };
  const syncHeaderSurface = () => header?.classList.toggle('disclosure-open', Boolean(header.querySelector('details[open]')));
  navGroups.forEach(group => {
    const state = navStates.get(group);
    const summary = group.querySelector('summary');
    group.addEventListener('toggle', () => {
      if (group.open) {
        navGroups.filter(other => other !== group).forEach(other => closeGroup(other));
        languageSwitches.forEach(other => { other.open = false; });
      }
      syncHeaderSurface();
    });
    // Native details remains the click, keyboard, touch and no-JavaScript fallback.
    if (!group.closest('.navlinks')) return;
    group.addEventListener('pointerenter', event => {
      if (event.pointerType !== 'mouse' || !hoverQuery.matches) return;
      state.inside = true;
      clearTimers(state);
      if (state.suppressed || group.open) return;
      state.enter = setTimeout(() => {
        if (!state.inside || state.suppressed || !hoverQuery.matches) return;
        navGroups.filter(other => other !== group).forEach(other => closeGroup(other));
        languageSwitches.forEach(other => { other.open = false; });
        state.hoverOpened = true;
        group.open = true;
        syncHeaderSurface();
      }, 120);
    });
    group.addEventListener('pointerleave', () => {
      state.inside = false;
      state.suppressed = false;
      clearTimers(state);
      state.leave = setTimeout(() => {
        if (!state.inside && !keyboardInside(group)) { closeGroup(group); syncHeaderSurface(); }
      }, 220);
    });
    summary.addEventListener('click', event => {
      clearTimers(state);
      // A click arriving just after hover should not collapse the new panel.
      if (event.detail && state.hoverOpened && group.open) event.preventDefault();
      state.hoverOpened = false;
    });
    summary.addEventListener('keydown', () => { clearTimers(state); state.hoverOpened = false; });
    group.addEventListener('focusout', event => {
      if (!event.relatedTarget || group.contains(event.relatedTarget)) return;
      setTimeout(() => {
        if (!group.contains(document.activeElement) && !state.inside) { closeGroup(group); syncHeaderSurface(); }
      }, 0);
    });
  });
  languageSwitches.forEach(details => {
    details.addEventListener('toggle', syncHeaderSurface);
    details.addEventListener('focusout', event => {
      // WebKit can blur a summary to the body before activating a clicked link.
      // Outside clicks already dismiss this menu; only follow explicit focus moves.
      if (!event.relatedTarget || details.contains(event.relatedTarget)) return;
      setTimeout(() => {
        if (!details.contains(document.activeElement)) details.open = false;
      }, 0);
    });
  });
  hoverQuery.addEventListener('change', () => {
    if (desktopQuery.matches && mobileMenu?.classList.contains('open')) setMenu(false);
    navGroups.forEach(group => {
      const state = navStates.get(group);
      state.inside = false;
      clearTimers(state);
      if (group.closest('.navlinks') ? !hoverQuery.matches : desktopQuery.matches) closeGroup(group);
    });
    if (!desktopQuery.matches && navigationFocus === 'desktop') menuButton?.focus({ preventScroll: true });
    if (desktopQuery.matches && navigationFocus === 'mobile') header?.querySelector('.navlinks summary')?.focus({ preventScroll: true });
    syncHeaderSurface();
  });
  document.addEventListener('click', event => {
    navGroups.forEach(group => { if (!group.contains(event.target)) closeGroup(group); });
    syncHeaderSurface();
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    const openGroup = navGroups.find(group => group.open);
    if (openGroup) {
      const restoreFocus = openGroup.contains(document.activeElement);
      closeGroup(openGroup, true);
      if (restoreFocus) openGroup.querySelector('summary').focus();
      syncHeaderSurface();
      event.stopImmediatePropagation();
    }
  });

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const disclosures = new Map();
  document.querySelectorAll('main details:not(.contact-alternatives)').forEach((details) => {
    const summary = details.querySelector(':scope > summary');
    if (!summary) return;
    const state = { expanded: details.open, animation: null };
    disclosures.set(details, state);
    // Native grouping remains in the HTML for visitors without JavaScript.
    // Enhanced groups allow the outgoing panel to finish its closing motion.
    if (details.parentElement.matches('[data-exclusive-details]')) details.removeAttribute('name');
    const finish = () => {
      const animation = state.animation;
      state.animation = null;
      if (animation) { animation.onfinish = null; animation.cancel(); }
      details.open = state.expanded;
      details.style.overflow = '';
    };
    state.finish = finish;
    state.setExpanded = (expanded) => {
      const start = details.getBoundingClientRect().height;
      if (state.animation) { state.animation.onfinish = null; state.animation.cancel(); }
      state.animation = null;
      state.expanded = expanded;
      summary.setAttribute('aria-expanded', String(expanded));
      details.dataset.expanded = String(expanded);
      Array.from(details.children).filter(child => child !== summary).forEach(child => { child.inert = !expanded; });
      if (reducedMotion.matches || typeof details.animate !== 'function') { finish(); return; }
      if (expanded) details.open = true;
      const style = getComputedStyle(details);
      const borders = parseFloat(style.borderTopWidth) + parseFloat(style.borderBottomWidth);
      const end = expanded ? details.getBoundingClientRect().height : summary.getBoundingClientRect().height + borders;
      details.style.overflow = 'hidden';
      state.animation = details.animate({ height: [`${start}px`, `${end}px`] }, {
        duration: 280, easing: 'cubic-bezier(.22, .61, .36, 1)', fill: 'both',
      });
      state.animation.onfinish = finish;
    };
    summary.addEventListener('click', (event) => {
      event.preventDefault();
      const expanded = !state.expanded;
      const group = details.parentElement;
      if (expanded && group.matches('[data-exclusive-details]')) {
        group.querySelectorAll(':scope > details').forEach(other => {
          const sibling = disclosures.get(other);
          if (other !== details && sibling?.expanded) sibling.setExpanded(false);
        });
      }
      state.setExpanded(expanded);
    });
  });
  // Complete pending transitions when their geometry or motion preference changes.
  const finishDisclosures = () => disclosures.forEach(state => { if (state.animation) state.finish(); });
  window.addEventListener('resize', finishDisclosures);
  reducedMotion.addEventListener('change', finishDisclosures);

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
      document.cookie = `prepinson-language=${encodeURIComponent(language)}; Path=/; SameSite=Lax${secure}`;

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
  const videoCaption = videoDialog?.querySelector('.dialog-caption');
  const defaultVideoCaption = videoCaption?.textContent;
  const defaultVideoLabel = videoDialog?.getAttribute('aria-label');
  document.querySelectorAll('[data-video-open], [data-film]').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      if (!videoDialog || !dialogVideo) return;
      const source = trigger.getAttribute('data-video-open') || trigger.getAttribute('data-film');
      if (!source) return;
      if (videoCaption) videoCaption.textContent = trigger.getAttribute('data-video-caption') || defaultVideoCaption;
      videoDialog.setAttribute('aria-label', trigger.textContent.trim() || defaultVideoLabel);
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
    if (videoCaption) videoCaption.textContent = defaultVideoCaption;
    if (defaultVideoLabel) videoDialog.setAttribute('aria-label', defaultVideoLabel);
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

  const instagramFeed = document.querySelector('#instagram-feed');
  if (instagramFeed) {
    const retry = document.querySelector('[data-instagram-retry]');
    let requested = false;
    const loadInstagram = async () => {
      if (requested) return;
      requested = true;
      if (retry) { retry.hidden = true; retry.disabled = true; }
      observer?.disconnect();
      window.removeEventListener('scroll', onScroll);
      try {
        const response = await fetch('/instagram-feed.json');
        if (!response.ok) throw new Error('feed unavailable');
        const { posts } = await response.json();
        if (!Array.isArray(posts)) throw new Error('invalid feed');
        if (!posts.length) return;
        const grid = document.createElement('div');
        grid.className = 'instagram-grid';
        for (const post of posts.slice(0, 6)) {
          if (!post.image || !/^https:\/\/www\.instagram\.com\//.test(post.permalink || '')) continue;
          const link = document.createElement('a');
          link.href = post.permalink;
          link.target = '_blank';
          link.rel = 'noopener noreferrer';
          link.className = 'instagram-post';
          link.setAttribute('aria-label', post.caption ? `Instagram : ${post.caption.slice(0, 120)}` : 'Voir cette publication sur Instagram');
          const image = document.createElement('img');
          image.src = post.image;
          image.alt = post.caption ? post.caption.slice(0, 160) : 'Publication du Haras de Prepinson';
          image.loading = 'lazy';
          image.decoding = 'async';
          link.appendChild(image);
          grid.appendChild(link);
        }
        if (grid.children.length) instagramFeed.replaceChildren(grid);
        else throw new Error('no usable posts');
      } catch {
        requested = false;
        if (retry) retry.hidden = false;
        // The profile link remains available when the API or connection fails.
      } finally {
        if (retry) retry.disabled = false;
      }
    };

    const isNearViewport = () => {
      const rect = instagramFeed.getBoundingClientRect();
      return rect.top <= window.innerHeight + 200 && rect.bottom >= -200;
    };
    const onScroll = () => {
      if (isNearViewport()) loadInstagram();
    };
    const observer = 'IntersectionObserver' in window
      ? new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) loadInstagram();
      }, { rootMargin: '200px 0px' })
      : null;
    if (observer) observer.observe(instagramFeed);
    else window.addEventListener('scroll', onScroll, { passive: true });
    retry?.addEventListener('click', loadInstagram);
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
    const focusable = [menuButton, ...mobileMenu.querySelectorAll('summary, a[href], button:not([disabled])')].filter(el => el.getClientRects().length && (!el.closest('details') || el.tagName === 'SUMMARY' || el.closest('details').open));
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

// Subtle, one-time editorial motion. The base state is always visible:
// no hidden CSS class, inline bootstrap, timer fallback or extra request.
(() => {
  'use strict';
  document.documentElement.classList.add('nav-enhanced');
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  if (preference.matches || !('IntersectionObserver' in window) || !Element.prototype.animate) return;

  const selectors = [
    'main h2', '.intro-portrait', '.expertise-card', '.team-card',
    '.staff-card', '.property-card', '.service-story-image', '.estate-photo',
    '.activity-image', '.activities-stay-card',
  ];
  const items = [...document.querySelectorAll(selectors.join(','))].filter(element => {
    // Keep forms, disclosures, the first viewport and anchor destinations stable.
    if (element.closest('.hero, .haras-hero, dialog, details, form, #contact')) return false;
    const bounds = element.getBoundingClientRect();
    return bounds.height > 0 && bounds.top >= innerHeight;
  });
  const waiting = new Set(items);
  const active = new Map();
  const settle = element => {
    waiting.delete(element);
    observer.unobserve(element);
    active.get(element)?.cancel();
    active.delete(element);
  };
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      const element = entry.target;
      waiting.delete(element);
      observer.unobserve(element);
      if (preference.matches || document.visibilityState === 'hidden' || element.contains(document.activeElement)) continue;
      const animation = element.animate([
        { opacity: .25, transform: 'translateY(12px)' },
        { opacity: 1, transform: 'translateY(0)' },
      ], { duration: 560, easing: 'cubic-bezier(.22,.61,.36,1)' });
      animation.id = 'prepinson-reveal';
      active.set(element, animation);
      animation.onfinish = () => active.delete(element);
    }
  }, { threshold: 0, rootMargin: '0px 0px -16px 0px' });
  items.forEach(element => observer.observe(element));

  document.addEventListener('focusin', event => {
    for (const element of [...waiting, ...active.keys()]) {
      if (element.contains(event.target)) settle(element);
    }
  });
  const settleHash = () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = id && document.getElementById(id);
    if (!target) return;
    for (const element of [...waiting, ...active.keys()]) {
      if (target.contains(element) || element.contains(target)) settle(element);
    }
  };
  window.addEventListener('hashchange', settleHash);
  settleHash();
  const settleAll = () => {
    observer.disconnect();
    waiting.clear();
    active.forEach(animation => animation.cancel());
    active.clear();
  };
  preference.addEventListener('change', event => { if (event.matches) settleAll(); });
  window.addEventListener('pagehide', settleAll);
  window.addEventListener('beforeprint', settleAll);
})();
