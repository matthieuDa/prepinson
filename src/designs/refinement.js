/* Follow the real header edge through transitions, resizing and text reflow. */
(() => {
  const header = document.querySelector('header.nav');
  if (!header) return;
  // Six masked layers soften from top to bottom; Equilibre opts in through CSS.
  // The decoration never enters the focus order or handles pointer input.
  const initBlur = () => {
    if (header.hasAttribute('data-progressive-blur') || getComputedStyle(header).getPropertyValue('--nav-progressive-blur').trim() !== '1') return;
    const blur = document.createElement('div');
    blur.className = 'nav-blur';
    blur.setAttribute('aria-hidden', 'true');
    for (let layer = 0; layer < 6; layer++) blur.append(document.createElement('span'));
    header.prepend(blur);
    header.dataset.progressiveBlur = '';
  };
  initBlur();
  // WebKit may resolve the variant stylesheet after this deferred script on a cold load.
  if (document.readyState !== 'complete') window.addEventListener('load', initBlur, { once: true });
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
})();
