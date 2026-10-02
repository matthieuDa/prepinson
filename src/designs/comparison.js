(() => {
  const select = document.querySelector('#language');
  const languages = ['fr', 'en', 'nl', 'de', 'sv', 'lb'];
  const initial = new URL(location.href).searchParams.get('lang');
  if (languages.includes(initial)) select.value = initial;
  const update = () => {
    for (const link of document.querySelectorAll('[data-variant]')) {
      const hash = new URL(link.href).hash;
      link.href = `/propositions/${link.dataset.variant}/${select.value}/${hash}`;
    }
    document.querySelectorAll('[data-reference]').forEach(a => { a.href = `/${select.value}/`; });
    const url = new URL(location.href);
    url.searchParams.set('lang', select.value);
    history.replaceState(null, '', url);
  };
  select.addEventListener('change', update);
  update();
})();
