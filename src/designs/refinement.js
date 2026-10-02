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
})();
