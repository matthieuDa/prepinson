import { publicStore, syncInstagram } from '../lib/instagram.mjs';

// Netlify invokes this after a deploy; only production initializes shared storage.
export default {
  async deploySucceeded(event) {
    if (event.deploy.context !== 'production') return;
    try {
      if (await publicStore().get('feed', { type: 'json' })) return;
      const feed = await syncInstagram();
      console.log(`Instagram feed initialized: ${feed.posts.length} posts`);
    } catch (error) {
      console.error('Instagram feed initialization failed:', error.message);
      throw error;
    }
  },
};
