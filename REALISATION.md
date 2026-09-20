# Réalisation Prepinson — restauration de la V1

## Livraison

La référence est la version approuvée par Eva, commit `fd597a0`. La présentation et les textes approuvés ont été réintégrés dans le générateur actuel, sans revenir à l’ancienne chaîne de localisation.

- Navigation V1, sélecteur de langue compact, tiroir mobile et nom Prepinson visible ; logo agrandi conformément à la demande.
- Cormorant Garamond et DM Sans hébergées localement, titres italiques et compositions éditoriales restaurés.
- Accueil : introduction avec portrait, trois savoir-faire photographiques, installations et chiffres, références, équipe, Maisons, Journal, contact et pied de page V1.
- Parcours Maisons restaurés : cartes, capacités, équipements vérifiés, réservation Casapilot/Airbnb et deux galeries de six photos avec visionneuse.
- Quatre programmes en accordéons et demandes contextualisées ; pages installations, ventes, références et activités intégrées au même vocabulaire visuel.
- FAQ artificielle, doublons, textes de chantier et ancienne annonce HubSpot retirés. Titres visuels séparés des titres SEO.
- 18 boxes sport, manège 27 × 60 m, carrière 40 × 75 m, 28 ha. Aucun prix publié.
- Dalton, Juni et Jackson sont des références historiques ; aucune disponibilité commerciale ni identité photographique n’est supposée.
- Film des maisons vérifié visuellement : il montre Ortho 24. Il a été retiré d’Ortho 25 pour éviter une attribution incorrecte.

## Photographies et performance

La photographie couleur des juments et poulains remplace l’ancienne image d’accueil refusée par Eva. Les fleurs des écuries, la jument et son poulain, le saut en couleur et le cavalier dans la carrière sont affectés aux sections correspondantes. Aucun filtre de désaturation ajouté.

Les images utilisent des variantes AVIF avec repli WebP et leurs dimensions réelles. Des cadrages portraits dédiés aux téléphones conservent les sujets sans charger toute la largeur inutilisée. Les galeries utilisent des tailles adaptées à leurs colonnes ; leur visionneuse ouvre l’original. Aucun agrandissement artificiel des sources.

La carte de partage est distincte pour les univers Haras et Maisons, en 1200 × 630. Les polices et médias restent locaux. Les URL des ressources sont versionnées après modification.

## Newsletter et contact

Le formulaire `newsletter` est partagé entre les six langues, avec adresse e-mail, consentement obligatoire non précoché, version du consentement, langue, page d’origine sans paramètres et champ antispam. Il couvre le haras et les maisons, sans champ d’intérêt supplémentaire.

Les six formulaires `contact-{lang}` sont conservés. Les pages Maisons affichent le contact des séjours et présélectionnent le contexte pertinent. Une demande de contact n’inscrit pas à la newsletter.

Tous les formulaires fonctionnent par POST natif ; JavaScript ajoute chargement, succès et erreurs accessibles. La saisie est préservée en cas d’échec et aucun envoi n’est répété automatiquement. Les 12 confirmations localisées sont non indexables et absentes du sitemap.

Netlify assure la collecte ; aucune campagne, confirmation par e-mail ni intégration HubSpot n’est activée. Les tests navigateur utilisent exclusivement des réponses simulées et ne créent pas d’abonnements réels.

**Vérification de réception Netlify : en attente d’accès au compte.** La session disponible n’est pas connectée. Il faut consulter les notifications avant une soumission contrôlée, puis constater l’enregistrement dans Netlify. La présence du HTML traité ne constitue pas une preuve de stockage. Aucune communication externe n’a été envoyée pour cette recette.

## Validation

- 72 pages publiques en anglais, français, néerlandais, allemand, suédois et luxembourgeois, 12 confirmations et passerelle linguistique.
- Contrôle des routes, liens et ancres, canonical, hreflang, JSON-LD, sitemap, ressources responsives et contrats de formulaires.
- Neuf scénarios de négociation linguistique. Seule la racine choisit temporairement une langue ; les URL explicites restent stables.
- 504 configurations de mise en page : 72 pages × 360, 390, 768, 1024, 1280, 1440 et 1920 pixels.
- Tests des six langues, consentement et adresse invalides, double clic, erreurs HTTP/réseau/délai, succès et soumission sans JavaScript.
- Menu clavier, Échap, retour du focus, arrière-plan inerte, sélection linguistique, accordéons, galerie et arrêt des vidéos vérifiés.
- Revue indépendante GPT-6 Astra High : comparaison directe avec la V1, restauration des textes et italiques, corrections des contrastes, liens descriptifs, photographie de saut en couleur, descriptions des galeries et film attribué à la bonne maison.
- Lighthouse du 20 septembre 2026, configuration de production locale sans exclusion : 24 audits (12 gabarits × mobile/ordinateur), SEO/accessibilité/bonnes pratiques 100 partout, performance mobile 97–100 et ordinateur 100 partout. Les deux pages de confirmation restent volontairement non indexables et ne sont pas des pages publiques de référencement.

Les captures et rapports détaillés se trouvent dans `outputs/v1-restoration/` dans l’espace de travail ; ils ne sont pas déployés. Les scripts de recette sont conservés dans le dépôt.

## Dépendances avant production

- Vérifier la réception des formulaires dans le compte Netlify et les notifications souhaitées.
- Confirmer la dénomination sociale, le siège légal, le responsable du traitement et les durées de conservation à appliquer. Aucune durée légale fictive n’a été inventée.
- Faire identifier les photographies individuelles de Dalton, Juni et Jackson avant toute association nominative.
- Obtenir les consignes précises pour les transporteurs ; le site invite déjà à coordonner leur arrivée avec l’équipe.
- Préparer séparément les futures campagnes et leur désabonnement. HubSpot n’est pas nécessaire à la collecte actuelle.
- Traiter séparément la migration du domaine et la mise en indexation de production.

La livraison concerne uniquement la branche `codex/prepinson-delivery` et le Deploy Preview de la pull request existante. Aucun changement de domaine, fiche Google Business, compte HubSpot ou abonnement tiers n’est effectué.

## Résultats et preuves de recette

- Lighthouse complet : `outputs/v1-restoration/lighthouse-final/summary.md`, avec les 24 rapports JSON et HTML.
- Revue indépendante : `outputs/v1-restoration/independent-review/REVUE.md` et 15 comparatifs V1/résultat.
- Responsive : `outputs/v1-restoration/final/layout-report.json`, 504 configurations sans erreur ; captures finales dans le même dossier.
- Formulaires : suite navigateur réussie dans les six langues, envois simulés uniquement.
- Scan : fichiers actuels/publics et 506 objets Git historiques examinés ; aucun motif de secret, document privé ou montant public détecté dans le périmètre vérifié. Ce contrôle ne constitue pas une garantie absolue de sécurité.
- Build déterministe : deux générations successives produisent la même empreinte des fichiers texte livrés.

La vérification HTTP du Deploy Preview est effectuée après le push ; sa preuve est enregistrée dans le dossier de recette. Le `noindex` du preview reste obligatoire et son impact sur le score SEO est rapporté séparément.
