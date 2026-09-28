import { getStore } from '@netlify/blobs';
import { optimizeInstagramImage } from './instagram-image.mjs';

const API = 'https://graph.instagram.com';
const FIELDS = 'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,children{media_type,media_url,thumbnail_url}';
const REGION = 'eu-central-1';
const RETAIN_MS = 7 * 86400000;

export const publicStore = () => getStore({ name: 'prepinson-instagram', region: REGION });
const privateStore = () => getStore({ name: 'prepinson-instagram-private', region: REGION });

function imageSource(item) {
  if (item.media_type === 'VIDEO') return item.thumbnail_url || item.media_url;
  if (item.media_type === 'CAROUSEL_ALBUM') {
    return item.children?.data?.find((child) => child.media_type === 'IMAGE' && child.media_url)?.media_url
      || item.media_url || item.thumbnail_url;
  }
  return item.media_url || item.thumbnail_url;
}

function trustedImage(source) {
  try {
    const url = new URL(source);
    return url.protocol === 'https:' && (url.hostname.endsWith('.cdninstagram.com') || url.hostname.endsWith('.fbcdn.net'));
  } catch {
    return false;
  }
}

async function accessToken(store, request, now, logger) {
  const saved = await store.get('token', { type: 'json' });
  let value = saved?.value || process.env.INSTAGRAM_ACCESS_TOKEN;
  if (!value) throw new Error('Instagram token is not configured');
  if (!saved || now - saved.refreshedAt > 7 * 86400000) {
    try {
      const params = new URLSearchParams({ grant_type: 'ig_refresh_token', access_token: value });
      const response = await request(`${API}/refresh_access_token?${params}`, { signal: AbortSignal.timeout(12000) });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const refreshed = await response.json();
      if (!refreshed.access_token) throw new Error('missing access token');
      value = refreshed.access_token;
      await store.set('token', JSON.stringify({ value, refreshedAt: now }));
    } catch (error) {
      // A temporary refresh failure must not hide a feed while the old token works.
      logger.warn(`Instagram token renewal failed: ${error.message}`);
    }
  }
  return value;
}

async function collectImages(store, activeIds, now, logger) {
  try {
    const saved = await store.get('image-retention', { type: 'json' }) || {};
    const retention = {};
    for await (const page of store.list({ prefix: 'image/', paginate: true })) {
      for (const { key } of page.blobs) {
        const id = key.slice('image/'.length);
        if (!/^\d+$/.test(id)) continue;
        if (activeIds.has(id)) {
          retention[id] = now;
        } else {
          const lastSeen = Number(saved[id]) || now;
          if (now - lastSeen >= RETAIN_MS) await store.delete(key);
          else retention[id] = lastSeen;
        }
      }
    }
    await store.set('image-retention', JSON.stringify(retention));
  } catch (error) {
    // The new feed is already published. Cleanup can retry on the next sync.
    logger.warn(`Instagram image cleanup failed: ${error.message}`);
  }
}

// Dependencies can be replaced by an in-memory store and HTTP fixtures in tests.
export async function syncInstagram({
  store = publicStore(), tokenStore = privateStore(), request = fetch,
  optimize = optimizeInstagramImage, now = Date.now(), logger = console,
} = {}) {
  const token = await accessToken(tokenStore, request, now, logger);
  const response = await request(`${API}/v24.0/me/media?${new URLSearchParams({ fields: FIELDS, limit: '6' })}`, {
    headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(12000),
  });
  if (!response.ok) throw new Error(`Instagram API returned ${response.status}`);
  const media = await response.json();
  if (!Array.isArray(media.data)) throw new Error('Instagram returned an invalid media list');

  const oldEntry = await store.getWithMetadata('feed', { type: 'json' });
  const posts = [];
  for (const item of media.data.slice(0, 6)) {
    const id = String(item.id || '');
    const source = imageSource(item);
    const permalink = item.permalink || '';
    if (!/^\d{8,30}$/.test(id) || !trustedImage(source) || !permalink.startsWith('https://www.instagram.com/')) {
      throw new Error('Instagram returned an unusable publication');
    }
    const key = `image/${id}`;
    if (!await store.getMetadata(key)) {
      const imageResponse = await request(source, { signal: AbortSignal.timeout(12000) });
      const type = imageResponse.headers.get('content-type')?.split(';')[0];
      if (!imageResponse.ok || !['image/jpeg', 'image/webp', 'image/png'].includes(type)) {
        throw new Error(`Instagram image ${id} is unavailable`);
      }
      const image = await imageResponse.arrayBuffer();
      if (image.byteLength > 8_000_000) throw new Error(`Instagram image ${id} exceeds the input limit`);
      const optimized = await optimize(Buffer.from(image));
      if (optimized.byteLength > 180_000) throw new Error(`Instagram image ${id} exceeds the output limit`);
      await store.set(key, optimized, { metadata: { type: 'image/webp' }, onlyIfNew: true });
    }
    posts.push({
      id, caption: String(item.caption || '').slice(0, 500), permalink,
      image: `/instagram-image?id=${id}`, timestamp: item.timestamp || '',
    });
  }
  if (posts.length < 6) logger.warn(`Instagram exposes only ${posts.length} of 6 expected publications`);
  const feed = { posts, updatedAt: new Date(now).toISOString() };
  const result = await store.set('feed', JSON.stringify(feed), oldEntry?.etag
    ? { onlyIfMatch: oldEntry.etag } : { onlyIfNew: true });
  if (!result.modified) return store.get('feed', { type: 'json' });
  await collectImages(store, new Set(posts.map((post) => post.id)), now, logger);
  return feed;
}
