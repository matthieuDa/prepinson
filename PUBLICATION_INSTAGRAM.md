# Publication du flux Instagram de Prépinson

Cette fiche couvre la mise en production du flux Instagram hébergé par Prépinson. Le dépôt GitHub contient le code ; l'envoi sur GitHub ne publie pas à lui seul le site Netlify. La personne qui publie renseigne les éléments entre crochets et coche les contrôles après observation du site publié.

## Avant de publier

1. Confirmer la branche et le commit à déployer : `[branche]` / `[SHA]`. Examiner le diff et lancer `npm run check`, `npm run test:instagram` et `python3 scripts/security_scan.py`.
2. Dans Netlify, vérifier que la commande de build et le dossier publié proviennent de `netlify.toml` : `INSTAGRAM_SNAPSHOT_MODE=skip ./scripts/build.sh` et `dist`. Les images Instagram sont servies par les fonctions, pas copiées depuis le poste local.
3. Dans **Site configuration → Environment variables**, créer ou vérifier `INSTAGRAM_ACCESS_TOKEN` avec le jeton longue durée du compte professionnel `@haras_de_prepinson`, pour les contextes **Production** et **Deploy Previews**. Sur un forfait permettant les portées personnalisées, choisir **Functions** ; sur le forfait gratuit, cette restriction n'est pas disponible. Garder le jeton dans Netlify, hors de GitHub, des documents partagés, des logs et du navigateur. Vérifier que l'autorisation Meta est encore active.
4. Désigner l'adresse technique qui recevra l'alerte : `[adresse technique]`. Préparer un moniteur HTTP gratuit pour `https://[domaine]/instagram-health.json`, mais l'activer après le premier flux sain.

## Publication et premier chargement

1. Déclencher un déploiement **Production** du commit approuvé et attendre le statut « Published ». Les Deploy Previews initialisent leur propre stockage, distinct de celui de production ; leurs fonctions planifiées ne s'exécutent pas.
2. Dans les logs Netlify, contrôler `instagram-on-deploy`. Si le Blob `feed` est vide, cette fonction télécharge et optimise les publications en arrière-plan après le déploiement. Le premier visiteur ne lance pas cette opération. Elle peut prendre quelques minutes ; une réponse 503 du flux pendant ce premier traitement est attendue.
3. Vérifier ensuite `https://[domaine]/instagram-feed.json` : HTTP 200, six publications, dates et URLs d'images du domaine Prépinson. Si le compte contient réellement moins de six publications accessibles, documenter ce nombre et rechercher la cause du 503 de santé ; le site peut afficher les publications disponibles.
4. Ouvrir les six images et vérifier qu'elles répondent en HTTP 200. Confirmer que la somme de leurs tailles transférées reste inférieure à **1,2 Mo**. Les réponses du flux doivent porter `Netlify-CDN-Cache-Control: public, durable, max-age=300` ; celles des images `max-age=86400`.
5. Vérifier `https://[domaine]/instagram-health.json` : HTTP 200, `healthy: true`, `postCount: 6`, `ageHours` récent. Ce contrôle ne doit exposer ni jeton ni donnée privée.

## Contrôle du site publié

- Sur l'accueil, ordinateur et Android : avant d'approcher la section Instagram, aucune requête Instagram ne part ; après défilement, six publications apparaissent. Revenir vers la section après l'avoir dépassée et vérifier qu'elles restent visibles.
- Vérifier que le navigateur ne demande aucun média à Meta/Instagram : les images viennent du domaine Prépinson. Le lien direct vers le profil Instagram reste visible avec et sans JavaScript.
- Simuler si possible une réponse 503 du flux en environnement de test : le bouton « Réessayer » doit permettre de relancer le chargement ; le lien direct reste disponible. Vérifier les six langues.
- Sur une page autre que l'accueil, aucune requête de flux ne doit partir.
- Contrôler les en-têtes de cache sur les vraies réponses Netlify, et pas seulement dans les tests locaux.

## Automatisation et alerte

1. Activer un moniteur HTTP gratuit pour `https://[domaine]/instagram-health.json` avec alerte par courriel à `[adresse technique]` lorsque le statut n'est plus 200. Vérifier la réception au moyen du test d'alerte du fournisseur ou d'une URL de test renvoyant 503, sans interrompre le site de production.
2. La fonction `refresh-instagram` est planifiée par `netlify.toml` deux fois par jour (`17 */12 * * *`, heure UTC). Après le premier créneau suivant la publication, vérifier dans les logs son exécution et un nouvel `updatedAt` dans le flux. La réponse de santé passe à 503 si le flux a plus de 36 heures, est absent ou contient moins de six publications.
3. Vérifier après une vraie mise à jour que les images inchangées gardent la même URL, que les nouvelles sont servies et que les images de l'ancien flux restent accessibles pendant sept jours. Le nettoyage retire ensuite les images devenues inutiles.

## Incident et retour arrière

- Si l'API ou une image échoue pendant une synchronisation, le dernier flux complet doit rester visible. Consulter les logs de `refresh-instagram` et `instagram-on-deploy` ; ne pas supprimer le Blob `feed` pour relancer la synchronisation.
- Si l'autorisation Meta est révoquée ou le jeton expire, reconnecter le compte dans l'application Meta, remplacer le secret Netlify, supprimer uniquement la clé privée Blob `token`, puis relancer `refresh-instagram`. Vérifier ensuite le flux et la santé. Le renouvellement automatique tente normalement de prolonger le jeton chaque semaine ; un échec ponctuel conserve le jeton encore valide.
- En cas de régression du site, restaurer le déploiement Netlify précédent. Les Blobs du flux sont distincts du déploiement statique : vérifier le rendu et la santé après retour arrière. Garder le moniteur actif jusqu'à résolution.

## Fiche de validation

| Élément | Résultat |
| --- | --- |
| Commit publié | `[SHA]` |
| URL de production | `https://[domaine]/` |
| Premier flux sain, date et heure | `[à remplir]` |
| Six images sous 1,2 Mo | `[à remplir]` |
| Premier rafraîchissement planifié vérifié | `[à remplir]` |
| Moniteur et courriel d'alerte vérifiés | `[à remplir]` |
| Vérification Android et ordinateur | `[à remplir]` |
