import { publicStore } from '../lib/instagram.mjs';

export async function serveImage(request, store = publicStore()) {
  if (request.method !== 'GET' && request.method !== 'HEAD') return new Response(null, { status: 405 });
  const id = new URL(request.url).searchParams.get('id') || '';
  if (!/^\d{8,30}$/.test(id)) return new Response(null, { status: 404 });
  const entry = await store.getWithMetadata(`image/${id}`, { type: 'arrayBuffer' });
  if (!entry?.data) return new Response(null, { status: 404 });
  return new Response(request.method === 'HEAD' ? null : entry.data, {
    headers: {
      'Content-Type': entry.metadata?.type || 'image/jpeg',
      'Cache-Control': 'public, max-age=86400',
      'Netlify-CDN-Cache-Control': 'public, durable, max-age=86400',
      'X-Content-Type-Options': 'nosniff',
    },
  });
}

export default serveImage;
