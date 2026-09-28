import { publicStore } from '../lib/instagram.mjs';

export async function serveFeed(request, store = publicStore()) {
  if (request.method !== 'GET' && request.method !== 'HEAD') return new Response(null, { status: 405 });
  try {
    const feed = await store.get('feed', { type: 'json' });
    if (!feed) return Response.json({ posts: [] }, { status: 503, headers: { 'Cache-Control': 'no-store' } });
    return new Response(request.method === 'HEAD' ? null : JSON.stringify(feed), {
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'public, max-age=60',
        'Netlify-CDN-Cache-Control': 'public, durable, max-age=300',
      },
    });
  } catch (error) {
    console.error('Instagram feed unavailable:', error.message);
    return Response.json({ posts: [] }, { status: 503, headers: { 'Cache-Control': 'no-store' } });
  }
}

export default (request, context) => serveFeed(request, publicStore(context?.deploy?.context));
