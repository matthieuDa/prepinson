import { syncInstagram } from '../lib/instagram.mjs';

export default async () => {
  try {
    const feed = await syncInstagram();
    console.log(`Instagram feed refreshed: ${feed.posts.length} posts`);
    return new Response(null, { status: 204 });
  } catch (error) {
    console.error('Instagram feed refresh failed:', error.message);
    return new Response(null, { status: 500 });
  }
};
