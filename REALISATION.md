# Réalisation du site Prepinson

## Livraison réalisée

- Générateur statique unique pour 12 routes et 6 langues : anglais, français, néerlandais, allemand, suédois et luxembourgeois, soit 72 pages localisées.
- Sélection automatique temporaire de langue uniquement sur `/`, avec priorité au choix manuel enregistré, puis à `Accept-Language`. Toutes les URL explicites restent stables.
- Métadonnées propres à chaque page et langue, canonical, hreflang réciproques, `x-default`, Open Graph, Twitter Card et image de partage 1200 × 630.
- `robots.txt` et sitemap multilingue complets, générés depuis le même registre de routes.
- Données structurées `Organization`, `WebSite`, `WebPage` et `LocalBusiness`, avec les deux fiches Google Maps distinctes.
- Contenu validé : 18 boxes sport, manège 27 × 60 m, carrière 40 × 75 m, 28 ha, équipements et quatre programmes. Aucun tarif ni prix indicatif publié.
- Pages dédiées aux chevaux à vendre, installations, programmes, références Dalton/Juni/Jackson, maisons, activités, mentions légales et confidentialité.
- Bloc Maisons et FAQ sur l’accueil. Le bouton de contact mène au formulaire de la page.
- Newsletter visible mais désactivée, sans champ ni collecte, jusqu’à la connexion HubSpot.
- Galerie Instagram locale et liens externes. Aucun widget LightWidget ni script Instagram tiers.
- Photos couleur haute définition d’Eva exportées en WebP aux largeurs 480, 768, 1200, 1600 et 2000 px, qualité 80. L’image sociale JPEG est recadrée à 1200 × 630, qualité élevée.
- Navigation clavier, lien d’évitement, focus visible, menu accessible, mouvement réduit et mises en page de 360 à 1920 px.
- CSP stricte et en-têtes de sécurité : anti-framing, nosniff, politique de référent, permissions et isolation d’origine.

## Contrôles

- Le validateur du projet vérifie les 72 pages, les liens locaux, les ancres, les images responsives, les titres, descriptions, canonical, hreflang, Open Graph, JSON-LD, sitemap, robots, formulaires et la configuration de sécurité.
- Les liens d’activités, de réservation et les deux liens Google Maps ont été contrôlés le 20 septembre 2026. Les liens obsolètes du Cheslé et d’Ardenne Aventures ont été remplacés par leurs pages officielles actives.
- Lighthouse local sans exclusion, après corrections : mobile 99 performance, 100 accessibilité, 100 bonnes pratiques et 100 SEO ; desktop 99 performance, 100 accessibilité, 100 bonnes pratiques et 100 SEO.
- Le scan reproductible du worktree et des 305 objets Git historiques ne trouve aucun identifiant, document privé ou montant public correspondant aux motifs contrôlés.
- La revue indépendante GPT-6 Astra High a corrigé la négociation `Accept-Language` pour les qualités nulles ou invalides, le chargement du hero Ortho 25 et les URL d’images sociales propres au preview. Les neuf cas de routage de langue passent.
- Deploy Preview vérifié : `https://deploy-preview-1--prepinson.netlify.app/`.
- Lighthouse du déploiement immuable Netlify, sans retirer de contrôle : mobile et desktop 100 performance, 100 accessibilité et 100 bonnes pratiques. Le SEO obtient 69 uniquement parce que le seul audit SEO échoué est `is-crawlable`, conséquence directe du `noindex` obligatoire du preview. Le même build en configuration de production, sans cet en-tête, obtient 100 SEO.
- La barre de collaboration Netlify est injectée uniquement sur l’URL stable du Deploy Preview. Les audits automatisés utilisent le permalien immuable du même déploiement afin de mesurer le site livré sans ce code tiers propre à Netlify.

## Réglages d’export des images

- Pour une nouvelle photographie avec Squoosh : redimensionner au plus près de 2000 px de large, exporter en WebP avec une qualité proche de 80, conserver les métadonnées désactivées et vérifier les visages, crins et feuillages à 100 %.
- Générer les variantes 480, 768, 1200, 1600 et 2000 px en conservant exactement le même cadrage. Le HTML choisit automatiquement la taille adaptée à l’écran.
- Pour la vignette WhatsApp et Open Graph : cadrage horizontal 1200 × 630, JPEG qualité 84 environ, sujet principal éloigné des bords et poids visé inférieur à 300 Ko.
- Utiliser un nom descriptif en minuscules, sans espace ni accent, puis ajouter un texte alternatif factuel sans supposer l’identité d’un cheval.

## Dépendances restant avant la production

- Connecter HubSpot et définir le consentement, la double confirmation et la durée de conservation avant d’activer la newsletter.
- Le forfait gratuit LightWidget ne prend pas en charge HTTPS. Garder la galerie locale ou souscrire un service adapté après décision d’Eva.
- Faire identifier formellement par Eva les photos de Dalton, Juni et Jackson avant de les associer à ces chevaux.
- Confirmer la dénomination sociale, le siège légal, l’identité du responsable de traitement et les durées de conservation dans les sources officielles.
- Obtenir et publier les consignes d’accès précises destinées aux transporteurs.
- Effectuer séparément la migration du domaine, la levée du `noindex` du preview et les éventuelles modifications des fiches Google Business Profile.
