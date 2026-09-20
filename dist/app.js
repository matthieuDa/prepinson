(() => {
  const button = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#primary-nav');
  if (button && nav) {
    const close = () => {
      nav.classList.remove('open');
      button.setAttribute('aria-expanded', 'false');
    };
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('open', open);
      if (open) nav.querySelector('a')?.focus();
    });
    nav.addEventListener('click', (event) => {
      if (event.target.closest('a')) close();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && nav.classList.contains('open')) {
        close();
        button.focus();
      }
    });
  }

  document.querySelectorAll('[data-language]').forEach((link) => {
    link.addEventListener('click', () => {
      const language = link.getAttribute('data-language');
      document.cookie = `prepinson-language=${language}; Max-Age=31536000; Path=/; SameSite=Lax; Secure`;
    });
  });
})();
