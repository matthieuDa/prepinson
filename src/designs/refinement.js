/* Follow the real header edge through transitions, resizing and text reflow. */
(() => {
  const header = document.querySelector('header.nav');
  if (!header) return;
  let frame;
  const sync = () => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      document.documentElement.style.setProperty('--nav-panel-top', `${Math.max(0, header.getBoundingClientRect().bottom)}px`);
    });
  };
  if ('ResizeObserver' in window) new ResizeObserver(sync).observe(header);
  window.visualViewport?.addEventListener('resize', sync);
  document.fonts?.ready.then(sync);
  sync();

  const initEditorialNav = () => {
    if (header.dataset.editorialNav || getComputedStyle(header).getPropertyValue('--nav-editorial').trim() !== '1') return;
    header.dataset.editorialNav = 'true';
    const groups = [...header.querySelectorAll('.navlinks .nav-group')];
    const desktop = matchMedia('(min-width: 1251px)');
    const illustrations = ['haras', 'horses', 'houses'];
    groups.forEach((group, index) => {
      const panel = group.querySelector('.nav-submenu');
      const links = [...panel.querySelectorAll(':scope > a')];
      if (!links.length) return;
      const linkList = document.createElement('div');
      linkList.className = 'nav-menu-links';
      links.forEach(link => linkList.append(link));
      panel.append(linkList);
      const destination = index === 0 ? links.find(link => link.href.includes('/facilities/')) || links[0] : links[0];
      const feature = document.createElement('a');
      feature.className = 'nav-feature';
      feature.href = destination.href;
      const photo = document.createElement('img');
      photo.src = `/assets/nav-illustrations/${illustrations[index] || illustrations[0]}.webp?v=__ASSET_VERSION__`;
      photo.alt = '';
      photo.width = 960;
      photo.height = 640;
      photo.decoding = 'async';
      photo.loading = 'lazy';
      const caption = document.createElement('span');
      caption.textContent = destination.textContent;
      feature.append(photo, caption);
      panel.append(feature);
    });

    let previousY = Math.max(0, scrollY);
    let direction = 0;
    let distance = 0;
    let scheduled = 0;
    const isOpen = () => header.classList.contains('mobile-menu-open') || Boolean(header.querySelector('details[open]'));
    const updateTone = () => {
      // White over the opening photograph; ink when the white surface is visible.
      header.dataset.tone = isOpen() || header.classList.contains('is-stuck') || header.classList.contains('solid-nav') ? 'dark' : 'light';
    };
    const updatePanels = () => {
      const open = isOpen();
      const panel = desktop.matches ? header.querySelector('.navlinks .nav-group[open] .nav-submenu') : null;
      const height = header.offsetHeight + (panel?.getBoundingClientRect().height || 0);
      // Retain the last panel size on close; only its visual scale animates.
      if (open) header.style.setProperty('--nav-reveal-height', `${height}px`);
      header.classList.toggle('nav-expanded', open);
      if (open && header.classList.contains('nav-away')) header.classList.remove('nav-away');
      updateTone();
      sync();
    };
    const updateScroll = () => {
      scheduled = 0;
      const y = Math.max(0, scrollY);
      const change = y - previousY;
      const nextDirection = Math.sign(change);
      if (nextDirection && nextDirection !== direction) distance = 0;
      if (nextDirection) direction = nextDirection;
      distance += Math.abs(change);
      if (y < 100 || isOpen() || (header.contains(document.activeElement) && document.activeElement.matches(':focus-visible'))) {
        header.classList.remove('nav-away');
      } else if (direction > 0 && distance > 10) {
        header.classList.add('nav-away');
      } else if (direction < 0 && distance > 8) {
        header.classList.remove('nav-away');
      }
      previousY = y;
      updateTone();
      sync();
    };
    const schedule = () => { if (!scheduled) scheduled = requestAnimationFrame(updateScroll); };
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', () => { updatePanels(); schedule(); });
    header.querySelectorAll('details').forEach(details => details.addEventListener('toggle', updatePanels));
    new MutationObserver(mutations => {
      if (mutations.some(mutation => mutation.attributeName === 'class')) updatePanels();
    }).observe(header, { attributes: true, attributeFilter: ['class'] });
    header.addEventListener('focusin', () => header.classList.remove('nav-away'));
    document.fonts?.ready.then(updatePanels);
    updatePanels();
  };
  initEditorialNav();
  // Deferred styles may settle after this script on a cold WebKit load.
  if (document.readyState !== 'complete') window.addEventListener('load', initEditorialNav, { once: true });
})();
