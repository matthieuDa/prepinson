# Prépinson · dossier de livraison

Version préparée le 30 septembre 2026. Le site comporte 90 pages publiques, dans six langues, et 12 pages de confirmation non indexables.

## Périmètre livré

- Navigation commune au header et au footer : Haras, Chevaux, Maisons de vacances, Contact direct. Fil d’Ariane et page active. Accès discret aux maisons sur chaque page.
- Nouvelles pages Équipe, Pension & soins et Contact & accès en anglais, français, néerlandais, allemand, suédois et luxembourgeois.
- Eva et Nicolas conservent leurs coordonnées. Steven, Pierre et Luc ont leur portrait et leur fonction, sans coordonnées personnelles.
- Formation : nouvelle photographie sur l’accueil et la page Chevaux. Ventes : section 04 et cinq références internationales. Corrections des origines et des récits, photo réattribuée à Juni, deux photos de Jackson, vidéos conservées.
- La Grange et Le Cottage : noms publics harmonisés, anciennes URL conservées. La découverte des maisons mène à la présentation existante. Les réservations restent chez Casapilot et Airbnb.
- Galerie photos : les images de La Grange disponibles dans le projet montrent ses extérieurs, sa piscine et ses jardins ; des vues intérieures du Cottage sont présentes. Pas de promesse de visite complète des intérieurs de La Grange. La photo du cavalier dans l’allée reste en réserve.
- Cookie de langue interne limité à la session, posé sur choix explicite. Aucune écriture dans localStorage, aucun outil publicitaire ou de mesure individuelle, aucun bandeau. L’URL localisée est prioritaire ; la racine utilise la préférence choisie, puis la langue du navigateur, puis l’anglais.
- Mentions légales : Haras de Prépinson SRL, BCE/TVA BE 0699.571.027, Ortho 24. UNMISSABL est identifié comme créateur du site.

## Validation disponible

Les résultats détaillés et les captures sont dans `outputs/publication-2026-09-30/` du dossier de travail. Ce répertoire est volontairement exclu de Git et du site publié.

- Génération et contrôles : 90 pages, 12 confirmations, liens internes et ancres, six versions de chaque contenu, métadonnées, hreflang, données structurées, sitemap, médias et contrats de formulaires.
- Chrome : 720 configurations, 90 pages × 8 largeurs (360, 390, 761, 768, 1024, 1280, 1440, 1920 px), aucun débordement détecté.
- WebKit : même matrice de 720 configurations, aucun débordement détecté. Ce résultat porte sur le moteur WebKit automatisé, pas sur une recette dans Safari installé.
- Navigation : clavier, fermeture, restitution du focus, écran court, page derrière le menu rendue inerte, navigation sans JavaScript, langue de session et absence d’appels tiers. La simulation de zoom teste une largeur CSS de 720 px correspondant à une fenêtre de 1440 px à 200 %.
- Accessibilité automatisée : axe sur les 90 pages, règles WCAG 2 A/AA, WCAG 2.1 AA et bonnes pratiques, aucune violation détectée. Une recette humaine reste complémentaire à cette mesure.
- Formulaires : validation, erreur, confirmation, double clic et soumission sans JavaScript, avec réponses serveur simulées. En complément, une demande technique et une inscription fictive ont été soumises sur la preview le 30 septembre : confirmations affichées et deux enregistrements vérifiés dans Netlify. L’inscription fictive a ensuite été écartée de la liste active. La réception en boîte mail reste à tester après configuration des notifications.
- Instagram : sept tests du stockage, du rafraîchissement, des erreurs et de l’isolation des previews.
- Liens externes : 25 destinations contrôlées, réponses HTTP 200, dont les deux plateformes de réservation et les deux itinéraires.
- Sécurité : analyse des fichiers et de l’historique Git sans détection de secrets, de documents privés ou de tarifs chiffrés. En-têtes de sécurité et CSP conservés.

### Réserves de recette

Firefox n’a pas pu être lancé de manière fiable sur ce Mac : le moteur récent refuse le profil temporaire ; le moteur précédent échoue au démarrage du processus de rendu. Safari installé n’a pas pu être contrôlé car le Mac est verrouillé. Reprendre ces deux recettes sur un appareil disponible avant de présenter la couverture comme exhaustive.

Les mesures Lighthouse sont des mesures de laboratoire. Le score SEO contrôle une base technique ; il ne prouve ni un classement Google ni une présence dans les réponses des IA. Les Core Web Vitals réels, en particulier l’INP, nécessitent des visites réelles et des données de terrain suffisantes.

- Déploiement : 118 contrôles HTTP passent sur la preview (pages, redirections, médias, sitemap, en-têtes et Instagram), 108 contrôles de navigation passent dans Chrome sur Netlify et sept cas de négociation de langue sont vérifiés sur la fonction Edge.

## Vérifications Netlify et conditions de bascule

Constat effectué dans le compte Netlify le 30 septembre 2026 : détection des formulaires active ; formulaires `contact-en/fr/nl/de/sv/lb` et `newsletter` présents ; aucune notification de soumission configurée. Le projet utilise seulement `prepinson.netlify.app`, sans domaine personnalisé attaché.

Avant la bascule :

1. Configurer les notifications des sept formulaires actifs vers les adresses choisies par Matthieu. Faire une demande de test identifiée, vérifier sa présence dans Netlify et sa réception dans la boîte destinataire. La confirmation actuelle signifie « inscription enregistrée », pas « message de confirmation envoyé ».
2. Préparer l’envoi des newsletters avec un lien de désinscription simple dans chaque email, sans pixel de suivi. Netlify Forms collecte les inscriptions ; il ne constitue pas un outil d’envoi de campagnes.
3. Vérifier les droits de publication des photographies et vidéos, y compris ceux provenant des plateformes de réservation, et les autorisations des personnes représentées. La provenance est documentée dans `work/asset-sources.json` et `work/property-sources.json` ; elle ne remplace pas les autorisations.
4. Faire une sauvegarde complète de WordPress auprès de l’hébergeur actuel, fichiers et base de données. Un export Git du nouveau site ou une copie des pages publiques ne remplace pas cette sauvegarde.
5. Identifier et conserver le déploiement Netlify retenu, son commit Git et le déploiement précédent. Terminer la recette Firefox/Safari et la revue visuelle des six langues.
6. Attacher `www.prepinson.com` et `prepinson.com`, choisir `www` comme canonique, obtenir le certificat HTTPS, puis modifier uniquement les enregistrements web nécessaires. Ne pas remplacer les serveurs DNS sans inventaire complet de la zone.
7. Préserver MX, SPF, DKIM, DMARC et les validations Microsoft. État relevé : MX `0 prepinson-com.mail.protection.outlook.com.` ; SPF `v=spf1 include:_mailcust.gandi.net include:spf.protection.outlook.com -all`. Les sélecteurs DKIM ne sont pas devinés : exporter la zone complète chez le registrar avant toute opération.
8. Après bascule, vérifier `/`, `/fr/`, une ancienne URL par langue, une erreur 404, `/robots.txt`, `/sitemap.xml`, HTTPS, formulaires, médias et état Instagram. Vérifier que la production n’a aucun `noindex` et que la preview reste non indexable.

### Retour arrière

Avant changement DNS, noter les valeurs et TTL réellement présents dans la zone. Relevé informatif du 30 septembre : A racine `54.247.136.197`, CNAME www `batipart-elb-1538075746.eu-central-1.elb.amazonaws.com.`. Les revérifier au moment de la bascule.

Si le problème concerne le nouveau code, republier le dernier déploiement Netlify validé. Si la migration du domaine doit être annulée, rétablir les seuls enregistrements web sauvegardés et conserver l’ancien hébergement actif pendant la propagation. Aucune suppression de WordPress n’est prévue lors de la bascule.

## Référencement Google et IA

Le contenu essentiel est rendu en HTML, disponible sans JavaScript. Les URL des six langues sont explicites et liées par hreflang. Le sitemap contient les 90 pages publiques. Les entités, services, maisons et fils d’Ariane sont décrits avec des données structurées correspondant au contenu visible. Les robots peuvent lire les pages publiques ; les confirmations et la page 404 ne sont pas indexables.

Les anciennes pages WordPress utiles sont redirigées vers leurs équivalents dans la bonne langue. Les anciennes offres de séminaires et partenaires, sans contenu équivalent validé, renvoient une vraie erreur 404 plutôt qu’une page sans rapport. La liste est dans `src/legacy_routes.py`.

Les nouvelles pages répondent à trois besoins distincts : identifier l’équipe, comprendre la pension, et contacter le bon interlocuteur. Les pages existantes couvrent déjà formation, vente, références, installations, deux maisons et alentours. Aucune page de comparaison ou série de pages géographiques répétitives n’a été créée. Les améliorations éditoriales suivantes seront utiles lorsqu’il existe des informations vérifiées : photos intérieures de La Grange, conditions pratiques de pension, nouvelles références et témoignages autorisés.

Dans Search Console et Bing Webmaster Tools, utiliser les propriétés du domaine, soumettre `https://www.prepinson.com/sitemap.xml`, inspecter l’accueil et les trois nouveaux types de page dans plusieurs langues, puis suivre couverture, erreurs 404, requêtes et Core Web Vitals. La session Google disponible indique ne pas avoir accès à la propriété prepinson.com ; Bing Webmaster Tools présente un écran de connexion. L’accès aux comptes propriétaires et la validation restent à effectuer ; aucun code de suivi visiteur n’est nécessaire pour ces consoles. Ne promettre ni indexation immédiate ni classement.

## Maintenance

- Chaque semaine au lancement : vérifier les demandes Netlify, les erreurs de traitement, le flux Instagram, les liens de réservation et les alertes de déploiement. Consulter `PUBLICATION_INSTAGRAM.md` pour le flux interne.
- Chaque mois : traiter les demandes de droits et de désinscription, puis supprimer les demandes sans contrat après 24 mois depuis le dernier échange. Supprimer les inscriptions retirées immédiatement des listes d’envoi ; réexaminer les inscriptions sans interaction active depuis 24 mois. Cette règle doit être appliquée dans Netlify, les exports et les boîtes de notification, pas seulement affichée sur le site.
- Les pièces liées aux contrats, obligations comptables ou litiges suivent leurs durées applicables dans un stockage séparé à accès restreint. Ne pas conserver indéfiniment les copies des formulaires au prétexte qu’une pièce comptable doit être conservée.
- À chaque changement de contenu : mettre à jour les six langues, lancer `npm run build`, `npm run check` et `npm run test:release`, puis vérifier la preview. Les notifications, droits des médias et destinataires restent des réglages opérationnels.
- À chaque changement de navigation, formulaire ou styles : ajouter les tests de navigation et de formulaires et revoir les captures 390, 761 et 1440 px. Relancer Lighthouse en cas de modification de médias, polices ou code chargé.
- Mettre les dépendances à jour après contrôle de la preview et conserver un déploiement de retour arrière.

## Sources vérifiées

- [BCE Public Search · Haras de Prépinson](https://kbopub.economie.fgov.be/kbopub/zoeknummerform.html?nummer=0699571027) : entreprise active, nom, forme juridique, siège et assujettissement TVA.
- [APD · Cookies et autres traceurs](https://www.autoriteprotectiondonnees.be/cookies-et-autres-traceurs) : préférence linguistique de session exemptée de consentement, avec obligation d’information.
- [RGPD](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32016R0679) : transparence, bases de traitement et droits. Les 24 mois constituent une politique de conservation retenue pour le site, pas une durée universelle imposée par la loi.
- [Netlify DPA](https://www.netlify.com/pdf/netlify-dpa.pdf) et [confidentialité Netlify](https://www.netlify.com/privacy/) : sous-traitance et transferts internationaux.
