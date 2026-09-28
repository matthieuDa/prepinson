import { publicStore } from '../lib/instagram.mjs';

export async function serveHealth(request, store = publicStore(), now = Date.now()) {
  if (request.method !== 'GET' && request.method !== 'HEAD') return new Response(null, { status: 405 });
  try {
    const feed = await store.get('feed', { type: 'json' });
    const ageHours = feed?.updatedAt ? (now - Date.parse(feed.updatedAt)) / 3600000 : null;
    const count = Array.isArray(feed?.posts) ? feed.posts.length : 0;
    const healthy = Number.isFinite(ageHours) && ageHours >= 0 && ageHours <= 36 && count === 6;
    const body = { healthy, postCount: count, ageHours: Number.isFinite(ageHours) ? Math.round(ageHours * 10) / 10 : null };
    return new Response(request.method === 'HEAD' ? null : JSON.stringify(body), {
      status: healthy ? 200 : 503,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'public, max-age=300',
        'Netlify-CDN-Cache-Control': 'public, durable, max-age=1800',
      },
    });
  } catch (error) {
    console.error('Instagram health check failed:', error.message);
    return Response.json({ healthy: false, postCount: 0, ageHours: null }, {
      status: 503, headers: { 'Cache-Control': 'no-store' },
    });
  }
}

export default serveHealth;
