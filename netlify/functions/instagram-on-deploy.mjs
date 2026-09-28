import { privateStore, publicStore, syncInstagram } from '../lib/instagram.mjs';

// Netlify invokes this after a deploy; previews use deploy-specific storage.
export async function initializeInstagram(event, {
  openPublicStore = publicStore, openPrivateStore = privateStore,
  sync = syncInstagram, logger = console,
} = {}) {
  const context = event.deploy.context;
  if (context !== 'production' && context !== 'deploy-preview') return;
  try {
    const store = openPublicStore(context);
    if (await store.get('feed', { type: 'json' })) return;
    const feed = await sync({ store, tokenStore: openPrivateStore(context) });
    logger.log(`Instagram feed initialized: ${feed.posts.length} posts`);
  } catch (error) {
    logger.error('Instagram feed initialization failed:', error.message);
    throw error;
  }
}

export default { deploySucceeded: initializeInstagram };
