import assert from 'node:assert/strict';
import redirect from '../netlify/edge-functions/language-redirect.js';

const cases = [
  ['fr-BE, en;q=0.8', '', 'fr'],
  ['de;q=0,nl;q=0.5', '', 'nl'],
  ['sv;q=0', '', 'en'],
  ['nl;q=0.2,fr;q=0.9', '', 'fr'],
  ['xx,de;q=0.6', '', 'de'],
  ['fr', 'prepinson-language=lb', 'lb'],
  ['fr', 'prepinson-language=xxx', 'fr'],
  ['de;q=2,sv;q=0.7', '', 'sv'],
];
for (const [language, cookie, expected] of cases) {
  const request = new Request('https://preview.example/?campaign=1', {
    headers: { 'Accept-Language': language, cookie },
  });
  const response = await redirect(request, { next() { throw new Error('Unexpected fallthrough'); } });
  assert.equal(response.status, 302);
  assert.equal(response.headers.get('location'), `https://preview.example/${expected}/?campaign=1`);
  assert.equal(response.headers.get('cache-control'), 'private, no-store');
  assert.equal(response.headers.get('vary'), 'Accept-Language, Cookie');
  assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(response.headers.get('x-frame-options'), 'DENY');
}
assert.equal(await redirect(new Request('https://preview.example/fr/horses/'), {
  next() { return 'stable'; },
}), 'stable');
console.log('PASS: 9 language negotiation and stable locale route checks');
