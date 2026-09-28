import assert from 'node:assert/strict';
import { test } from 'node:test';
import { syncInstagram } from '../netlify/lib/instagram.mjs';
import { serveFeed } from '../netlify/functions/instagram-feed.mjs';
import { serveImage } from '../netlify/functions/instagram-image.mjs';
import { serveHealth } from '../netlify/functions/instagram-health.mjs';

class MemoryStore {
  entries = new Map();
  version = 0;
  async get(key, { type } = {}) {
    const entry = this.entries.get(key);
    if (!entry) return null;
    return type === 'json' ? JSON.parse(entry.value) : entry.value;
  }
  async getMetadata(key) {
    const entry = this.entries.get(key);
    return entry ? { etag: entry.etag, metadata: entry.metadata } : null;
  }
  async getWithMetadata(key, { type } = {}) {
    const entry = this.entries.get(key);
    return entry ? { data: type === 'json' ? JSON.parse(entry.value) : entry.value, etag: entry.etag, metadata: entry.metadata } : null;
  }
  async set(key, value, options = {}) {
    const current = this.entries.get(key);
    if ((options.onlyIfNew && current) || (options.onlyIfMatch && options.onlyIfMatch !== current?.etag)) {
      return { modified: false };
    }
    const etag = String(++this.version);
    this.entries.set(key, { value, etag, metadata: options.metadata || {} });
    return { modified: true, etag };
  }
  async delete(key) { this.entries.delete(key); }
  async *list({ prefix }) {
    yield { blobs: [...this.entries.keys()].filter((key) => key.startsWith(prefix)).map((key) => ({ key })), directories: [] };
  }
}

function fixture(ids, { failImage, failRefresh = false } = {}) {
  const calls = { images: 0, refresh: 0 };
  const request = async (url) => {
    if (url.includes('/refresh_access_token')) {
      calls.refresh++;
      return failRefresh ? { ok: false, status: 500 } : { ok: true, json: async () => ({ access_token: 'renewed' }) };
    }
    if (url.includes('/me/media')) {
      return { ok: true, json: async () => ({ data: ids.map((id) => ({
        id, media_type: 'IMAGE', media_url: `https://images.cdninstagram.com/${id}.jpg`,
        permalink: `https://www.instagram.com/p/${id}/`, caption: `Post ${id}`,
      })) }) };
    }
    calls.images++;
    if (url.includes(failImage)) return { ok: false, status: 404, headers: new Headers() };
    return { ok: true, headers: new Headers({ 'content-type': 'image/jpeg' }), arrayBuffer: async () => new Uint8Array([1, 2, 3]).buffer };
  };
  return { request, calls };
}

function setup() {
  const store = new MemoryStore();
  const tokenStore = new MemoryStore();
  tokenStore.set('token', JSON.stringify({ value: 'valid', refreshedAt: 0 }));
  const logs = [];
  const logger = { warn: (message) => logs.push(message) };
  return { store, tokenStore, logger, logs, optimize: async () => Buffer.alloc(100) };
}

const six = ['10000001', '10000002', '10000003', '10000004', '10000005', '10000006'];
const day = 86400000;

test('publishes six posts, reuses unchanged images, and retains a removed image for seven days', async () => {
  const deps = setup();
  const first = fixture(six);
  await syncInstagram({ ...deps, ...first, now: day });
  assert.equal((await deps.store.get('feed', { type: 'json' })).posts.length, 6);
  assert.equal(first.calls.images, 6);
  const same = fixture(six);
  await syncInstagram({ ...deps, ...same, now: 2 * day });
  assert.equal(same.calls.images, 0);
  const next = fixture([...six.slice(1), '10000007']);
  await syncInstagram({ ...deps, ...next, now: 3 * day });
  assert.equal(next.calls.images, 1);
  assert.ok(await deps.store.getMetadata('image/10000001'));
  await syncInstagram({ ...deps, ...fixture([...six.slice(1), '10000007']), now: 8 * day });
  assert.ok(await deps.store.getMetadata('image/10000001'));
  await syncInstagram({ ...deps, ...fixture([...six.slice(1), '10000007']), now: 9 * day });
  assert.equal(await deps.store.getMetadata('image/10000001'), null);
});

test('a failed new image or API call does not replace the complete feed', async () => {
  const deps = setup();
  await syncInstagram({ ...deps, ...fixture(six), now: day });
  const before = await deps.store.get('feed', { type: 'json' });
  await assert.rejects(syncInstagram({ ...deps, ...fixture([...six.slice(1), '10000007'], { failImage: '10000007' }), now: 2 * day }));
  assert.deepEqual(await deps.store.get('feed', { type: 'json' }), before);
  await assert.rejects(syncInstagram({ ...deps, request: async () => ({ ok: false, status: 500 }), now: 2 * day }));
  assert.deepEqual(await deps.store.get('feed', { type: 'json' }), before);
});

test('a failed token renewal uses the still-valid token', async () => {
  const deps = setup();
  const source = fixture(six, { failRefresh: true });
  await syncInstagram({ ...deps, ...source, now: 8 * day });
  assert.equal(source.calls.refresh, 1);
  assert.equal((await deps.store.get('feed', { type: 'json' })).posts.length, 6);
  assert.ok(deps.logs.some((message) => message.includes('token renewal failed')));
});

test('a successful response with fewer posts publishes its actual count and warns', async () => {
  const deps = setup();
  await syncInstagram({ ...deps, ...fixture(six.slice(0, 5)), now: day });
  assert.equal((await deps.store.get('feed', { type: 'json' })).posts.length, 5);
  assert.ok(deps.logs.some((message) => message.includes('only 5')));
});

test('cold start is fast, and feed and retired images have explicit CDN cache headers', async () => {
  const deps = setup();
  const cold = await serveFeed(new Request('https://www.prepinson.com/instagram-feed.json'), deps.store);
  assert.equal(cold.status, 503);
  await syncInstagram({ ...deps, ...fixture(six), now: day });
  const feed = await serveFeed(new Request('https://www.prepinson.com/instagram-feed.json'), deps.store);
  assert.equal(feed.status, 200);
  assert.match(feed.headers.get('Netlify-CDN-Cache-Control'), /durable.*max-age=300/);
  await syncInstagram({ ...deps, ...fixture([...six.slice(1), '10000007']), now: 2 * day });
  const retired = await serveImage(new Request('https://www.prepinson.com/instagram-image?id=10000001'), deps.store);
  assert.equal(retired.status, 200);
  assert.equal(retired.headers.get('Content-Type'), 'image/webp');
  assert.match(retired.headers.get('Netlify-CDN-Cache-Control'), /max-age=86400/);
  const missing = await serveImage(new Request('https://www.prepinson.com/instagram-image?id=99999999'), deps.store);
  assert.equal(missing.status, 404);
});

test('health reports the count and flags stale or incomplete feeds without revealing a token', async () => {
  const deps = setup();
  await syncInstagram({ ...deps, ...fixture(six), now: day });
  const healthy = await serveHealth(new Request('https://www.prepinson.com/instagram-health.json'), deps.store, day + 3600000);
  assert.equal(healthy.status, 200);
  assert.deepEqual(await healthy.json(), { healthy: true, postCount: 6, ageHours: 1 });
  const stale = await serveHealth(new Request('https://www.prepinson.com/instagram-health.json'), deps.store, day + 37 * 3600000);
  assert.equal(stale.status, 503);
  assert.equal((await stale.json()).healthy, false);
  await syncInstagram({ ...deps, ...fixture(six.slice(0, 5)), now: 3 * day });
  const partial = await serveHealth(new Request('https://www.prepinson.com/instagram-health.json'), deps.store, 3 * day);
  assert.equal(partial.status, 503);
  assert.equal((await partial.json()).postCount, 5);
});
