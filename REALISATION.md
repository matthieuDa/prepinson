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
- Scan : fichiers actuels/publics et 1 277 objets Git historiques examinés ; aucun motif de secret, document privé ou montant public détecté dans le périmètre vérifié. Ce contrôle ne constitue pas une garantie absolue de sécurité.
- Build déterministe : deux générations successives produisent la même empreinte des fichiers texte livrés.

### Vérification du déploiement — 20 septembre 2026

La [pull request existante](https://github.com/matthieuDa/prepinson/pull/1) reste ouverte, sans fusion en production. Le [Deploy Preview](https://deploy-preview-1--prepinson.netlify.app/fr/) contient la restauration. La recette complète porte sur le commit de code `d865c5f273def289b2dbddd4fc8ed7ae9e9ce133`, déployé sous le [permalien audité](https://6ab033502c006c0009875af6--prepinson.netlify.app/fr/).

- **84 pages HTTP 200**, langues, liens et ancres internes vérifiés ; **343 ressources** répondent correctement.
- Les empreintes des CSS, JavaScript, robots.txt et sitemap.xml servis correspondent aux fichiers du commit. Le sitemap contient exactement 72 pages et exclut les confirmations.
- Les redirections linguistiques temporaires et le choix manuel fonctionnent en ligne ; une URL linguistique explicite reste stable.
- Le `noindex` et les en-têtes de sécurité sont présents sur les pages de prévisualisation.
- Netlify a traité `newsletter` et les six `contact-{lang}`. **Le stockage d’une véritable soumission n’est pas encore vérifié**, faute de session Netlify authentifiée et d’inspection préalable des notifications.
- Aucun motif de secret ou prix détecté dans les textes et bundles récupérés ; aucun document privé référencé par les pages contrôlées.
- La revue indépendante du déploiement a rejoué les cinq parcours principaux en français à 390 et 1440 px : aucune image cassée, aucun débordement, aucune exception JavaScript ni violation CSP. Navigation clavier, galeries, contexte des formulaires et arrêt des vidéos vérifiés.
- Un dernier correctif ajoute le favicon aux douze confirmations pour éliminer leur requête inutile vers `/favicon.ico`. Cette modification n’altère ni le contenu ni le rendu des 72 pages publiques. La vérification HTTP et la revue navigateur ciblée sont rejouées sur ce correctif final.

| Configuration auditée | Audits | Performance mobile | Performance ordinateur | Accessibilité | Bonnes pratiques | SEO |
|---|---:|---:|---:|---:|---:|---:|
| Production locale | 24 | 97–100 | 100 | 100 | 100 | 100 |
| Deploy Preview Netlify | 24 | 97–100 | 99–100 | 100 | 100 | 69 |

Aucun contrôle Lighthouse n’a été exclu. **La seule cause de perte SEO du preview est `is-crawlable` : la réponse `X-Robots-Tag: noindex` interdit intentionnellement son indexation.** La configuration de production a été auditée séparément ; elle n’a pas été publiée. Les résultats du preview sont dans `outputs/v1-restoration/lighthouse-deployed/summary.md` et les 24 rapports associés. La preuve HTTP et le commit effectivement vérifié sont dans `outputs/v1-restoration/deployment-verification.json`.

### Comparaisons visuelles

Chaque comparatif présente la V1 à gauche et la restauration à droite, aux mêmes dimensions. Les captures intégrales finales se trouvent dans `outputs/v1-restoration/final/`. Les différences prévues sont les photographies naturelles, le logo agrandi, les ajouts factuels et Maisons, les états de formulaires et les corrections d’accessibilité. Aucun nouveau style visuel n’a été introduit.

| Parcours | Mobile 390 px | Tablette 768 px | Ordinateur 1440 px |
|---|---|---|---|
| Accueil | [Comparatif](outputs/v1-restoration/independent-review/compare-390-home.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-768-home.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-1440-home.webp) |
| Chevaux | [Comparatif](outputs/v1-restoration/independent-review/compare-390-horses-.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-768-horses-.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-1440-horses-.webp) |
| Maisons | [Comparatif](outputs/v1-restoration/independent-review/compare-390-houses-.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-768-houses-.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-1440-houses-.webp) |
| Ortho 24 | [Comparatif](outputs/v1-restoration/independent-review/compare-390-houses-ortho-24-.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-768-houses-ortho-24-.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-1440-houses-ortho-24-.webp) |
| Ortho 25 | [Comparatif](outputs/v1-restoration/independent-review/compare-390-houses-ortho-25-.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-768-houses-ortho-25-.webp) | [Comparatif](outputs/v1-restoration/independent-review/compare-1440-houses-ortho-25-.webp) |

Les preuves de la revue indépendante en ligne sont conservées dans `outputs/v1-restoration/independent-review/deployed-report.json` et ses captures. Ces fichiers de recette restent locaux et ne sont pas exposés par le site.

## V4 — Instagram, mobile et révision linguistique

- Le Journal de l’accueil utilise le widget FeedPane fourni pour `@haras_de_prepinson`, avec six publications, une colonne sur téléphone, un lien de repli vers Instagram et aucune lecture vidéo automatique. La politique de confidentialité et la CSP décrivent et limitent les échanges nécessaires avec FeedPane et les médias Instagram.
- La newsletter mobile possède désormais un encadrement clair, des champs et une action tactiles, ainsi qu’une typographie lisible. Les liens légaux du pied de page disposent d’une zone d’action de 44 px et le Deploy Preview réserve l’espace occupé par Netlify Drawer afin qu’il ne les recouvre plus.
- Les flèches des formulaires et du pied de page sont des SVG de l’interface ; aucun caractère susceptible d’être transformé en emoji n’est utilisé.
- Ortho 25 utilise à nouveau la vue extérieure en pierre de la V1 pour la carte et le héros. Les actions de réservation nomment explicitement Casapilot ou Airbnb.
- Les répétitions des introductions Programmes, Installations et galeries des maisons ont été supprimées. Les titres de Dalton, Juni et Jackson utilisent une hiérarchie sur deux lignes au lieu d’un tiret long.
- L’échelle typographique a été rééquilibrée aux endroits où les textes secondaires étaient trop petits, sans modifier les proportions V1 qui restaient cohérentes.
- La racine non indexable présente une entrée chaleureuse et les six langues. Une page 404 non indexable, localisée selon la langue du navigateur, ramène vers la bonne version du site avec un trait d’humour discret.
- La révision éditoriale corrige les erreurs prioritaires en allemand, luxembourgeois, suédois et néerlandais. Les programmes expliquent les apprentissages, la vente s’adresse à l’acheteur, et les noms communs du haras et des maisons sont harmonisés. Le luxembourgeois reste à faire relire par un locuteur natif avant la production.

Recette locale V4 : 72 pages, 12 confirmations, passerelle et 404 validées ; 504 couples page/largeur sans débordement ; formulaires testés dans les six langues ; FeedPane charge effectivement ses publications sans requête échouée. Les captures V4 restent locales dans `outputs/v4/`.

Le commit V4 `dcbedb27ef62239d67271c6ae68c40f12adb4c56` est vérifié sur le [Deploy Preview stable](https://deploy-preview-1--prepinson.netlify.app/en/) et son [permalien](https://6ab081f4781e0a0008b5a91d--prepinson.netlify.app/en/). Sur téléphone, les deux liens légaux ont été activés jusqu’à leur page cible, le widget expose six publications, la newsletter et son action sont visibles, le formulaire utilise le SVG attendu, et la 404 personnalisée répond avec le statut HTTP 404. Aucun échec réseau FeedPane/Instagram ni erreur JavaScript du site n’a été observé. Les seules violations de console proviennent de Netlify Drawer, que la CSP du site empêche volontairement d’être chargé dans une iframe.

## V5 — Newsletter mobile et guide des Ardennes

- Le formulaire d’inscription conserve son nom Netlify `newsletter` et ses six parcours localisés, mais ses classes visibles ont été renommées pour éviter les filtres cosmétiques des bloqueurs de contenu mobiles. L’e-mail, le consentement et l’action restent utilisables à 390 px, avec ou sans JavaScript.
- La page Activités est désormais un guide éditorial structuré en cinq chapitres : promenades, vélo, eau, culture et famille. Chaque chapitre apporte un contexte local utile et renvoie ensuite vers les sources officielles pour les conditions à jour.
- Les six versions possèdent leurs propres introductions et un balisage `Article` relié au site dans les données structurées. Les liens internes et les titres de sections renforcent le parcours éditorial sans créer de faux articles ni d’informations pratiques non vérifiées.
- Le formulaire de contact a été retiré de la page Activités. La page se termine par une présentation de La Grange et du Cottage, avec accès direct à chaque maison et à la page d’ensemble.

Recette locale V5 : génération et contrôle des 72 pages publiques et 12 confirmations, neuf scénarios linguistiques, formulaires dans les six langues, validation mobile de la newsletter et 504 configurations de mise en page sans débordement. Les captures de contrôle V5 restent locales dans `outputs/v5/`.

## Photographies de Dalton de Prepinson

Trois photographies identifiées et transmises par Eva ont été ajoutées au récit de Dalton sur la page Références : une image en piste, le moment suivant la reprise et l’entrée dans l’arène de Falsterbo. Les vues très proches et le doublon sont volontairement écartés afin de conserver une séquence courte et éditoriale.

Chaque image possède des variantes AVIF et WebP responsives, sans agrandissement, ainsi qu’un texte alternatif propre aux six langues. La galerie s’ouvre au clavier dans la visionneuse accessible existante. Ces photographies ne sont associées ni à Juni ni à Jackson.

## V6 — Accordéons et naturel des six langues

- Les quatre programmes forment désormais un accordéon exclusif : l’ouverture d’un panneau referme le précédent. Le comportement utilise le regroupement HTML natif, avec un complément JavaScript générique réutilisable par les futurs groupes similaires.
- Le slogan traduit littéralement sur la page Chevaux a été remplacé par une formulation propre à chaque langue. Les accroches des chevaux et des maisons, plusieurs appels éditoriaux et les titres de séjour ont également été révisés lorsqu’ils reprenaient trop directement une structure anglaise.
- Les tirets longs ont été retirés du contenu public, des sujets de formulaire, des titres de maisons, des légendes de visionneuse et des titres de navigateur. Les plages numériques conservent le tiret typographique approprié.
- Les liens d’adresse du pied de page indiquent explicitement qu’ils ouvrent le haras ou les maisons dans Google Maps, dans les six langues.

Recette locale V6 : 72 pages publiques et 12 confirmations validées, neuf scénarios linguistiques, formulaires testés dans les six langues, 504 configurations de mise en page sans erreur et interaction exclusive des programmes vérifiée à la souris et au clavier. Les captures dédiées à la page Programmes sont conservées localement dans `outputs/v6-editorial/`.

Le groupe logo de la navigation a ensuite été agrandi sur ordinateur et mobile, avec un ajustement spécifique sous 390 px. Le compte Instagram des maisons utilise désormais `@prepinson_houses` dans le pied de page, la page Maisons et les données structurées. Une validation empêche le retour de l’ancien identifiant dans les pages générées.

## V6 finale : retours d’Eva et photographies, 22 septembre 2026

La direction artistique approuvée est conservée. Les derniers faits et textes d’Eva sont regroupés dans `src/client_content.py`, utilisés par le générateur pour les six langues.

- L’accueil présente désormais l’élevage, la formation, la vente et la pension. L’introduction décrit la progression des jeunes chevaux, les concours, les sorties quotidiennes et le travail en forêt.
- Les capacités sont corrigées partout dans les pages et métadonnées : 19 boxes de sport, 9 boxes de poulinage et jeunes chevaux de 5 × 8 m, domaine de 30 ha. Les pistes conservent leurs dimensions et précisent le sol fibré du manège et la subirrigation de la carrière. « Ebb & floor » dans le mail est traité comme une coquille pour « ebb and flow ».
- Eva : `3M3A3575`. Nicolas : `3M3A3579`. La photographie d’introduction avec Helena et Dalton est remplacée par `3M3A3500`.
- Accueil ordinateur : `3M3A3140`, un jeune cheval au travail en liberté dans le manège. Accueil téléphone en portrait : `3M3A3793`, détail du cavalier et du tapis Prepinson, pour éviter de couper le cheval de la photo horizontale. Le troupeau `3M3A2739` reste utilisé ailleurs sur le site.
- La section Équipe comprend une photographie de groupe (`3M3A3564`) puis une galerie dépliable : équipe devant la carrière (`3M3A3597`), préparation du cheval (`3M3A3500`), jeune cheval gris (`3M3A2995`), paddocks (`3M3A2759`) et détail équestre (`3M3A3793`). La visionneuse existante permet le parcours au clavier et le retour du focus.
- Neuf originaux ont été optimisés en variantes WebP et AVIF avec Sharp, sans agrandissement ni génération d’image. L’import reproductible est dans `scripts/import_eva_photos.mjs`. Les fichiers photo originaux et leurs métadonnées privées ne sont pas publiés.
- L’ancien film n’est plus proposé sur l’accueil. Une nouvelle vidéo pourra être intégrée lorsqu’Eva la fournira ; les films des maisons restent disponibles.
- Les récits de Dalton, Juni et Jackson reprennent les nouvelles informations d’Eva. La légende de Dalton précise son titre à Falsterbo chez les six ans. Le paragraphe dupliqué de Jackson n’est publié qu’une fois.
- Qurious HS possède son propre récit et son lien depuis l’accueil. Il est explicitement présenté comme acquis avec Grevlunda, et non comme issu de l’élevage. Les intitulés de la section et les métadonnées ont été adaptés en conséquence. L’accueil reste synthétique et renvoie aux récits complets.
- Les quatre origines sont affichées. Pour Jackson, **Contendro I** est retenu selon la capture de pedigree fournie : Contender y est son grand-père. La page Hippomundo citée dans le mail n’a pas été accessible à l’outil de consultation ; aucune vérification indépendante de ses résultats sportifs n’est revendiquée. Les récits et résultats publiés proviennent du mail d’Eva.
- FeedPane est conservé, crédit compris. Le contraste du crédit est corrigé et le lien de sa visionneuse possède une destination Instagram valide avant qu’une publication soit sélectionnée.

### Recette V6 finale

- 72 pages publiques, 12 confirmations, liens, ressources, métadonnées, sitemap, données structurées et neuf scénarios de langue : réussite.
- 504 configurations de mise en page, six langues, de 360 à 1920 px : aucun débordement détecté. Cadrages des portraits et de l’accueil contrôlés visuellement à 390 et 1440 px ; la correction du héros mobile suit cette inspection.
- Galerie à 390 et 1440 px : ouverture au clavier, photo suivante, fermeture par Échap et retour du focus vérifiés.
- Formulaires : contrats localisés, validation, erreurs réseau/serveur, succès, double clic et fonctionnement sans JavaScript vérifiés par les tests existants. Aucun nouvel envoi réel ni message externe n’a été effectué.
- Audit des capacités et des quatre pedigrees dans les six langues : aucune ancienne capacité 18/28 dans les contenus concernés ; portraits et retrait du film vérifiés.
- Scan des fichiers publics/suivis et de l’historique : aucune correspondance de secret, document privé ou prix numérique. `git diff --check` passe.
- Lighthouse du 22 septembre 2026, configuration de production locale, contrôles non exclus : accueil, installations et références, mobile et ordinateur. Performance mobile **97–98**, ordinateur **100** ; accessibilité **100**, bonnes pratiques **100**, SEO **100**. Les deux défauts FeedPane identifiés au premier passage ont été corrigés puis l’accueil a été audité de nouveau.

Rapports et captures locaux : `outputs/v6/layout-report.json`, `outputs/v6/hero-fr-390.png`, `outputs/v6/hero-fr-1440.png`, `outputs/v6/team-fr-390.png`, `outputs/v6/team-fr-1440.png`, `outputs/v6/qurious-fr.png`, `outputs/v6/lighthouse/` et `outputs/v6/lighthouse-home-final/`. Les scores locaux ne sont pas présentés comme des scores du preview ; celui-ci conserve son `noindex`.

Publication limitée à la branche et au Deploy Preview de la PR existante. Les dépendances précédemment documentées (relecture native luxembourgeoise et éléments juridiques avant production) subsistent. Aucune photographie n’a été attribuée à Juni, Jackson ou Qurious sans identification fournie.

### Ajustements après retour de Matthieu

- La photographie principale précédente (`3M3A2739`, troupeau et poulains) est rétablie sur ordinateur **et** téléphone, avec les variantes et cadrages antérieurs. Ce choix remplace la proposition sportive décrite ci-dessus.
- Les nouveaux portraits d’Eva et Nicolas restent sur l’accueil. La photographie de groupe et la galerie complémentaire sont déplacées en fin de page Chevaux, après la présentation de la vente et avant le contact (`/fr/horses/#team-gallery`, avec équivalents dans les six langues).
- Les textes des quatre références occupent les deux colonnes de contenu sous les titres et origines. Ils ne tombent plus dans la petite colonne de numérotation, même lorsqu’aucune photographie n’accompagne le récit. La largeur de lecture est limitée à 76 caractères typographiques environ, et reste fluide sur téléphone.
- Les programmes et la galerie dépliable s’ouvrent et se ferment avec une transition de hauteur de 280 ms et une rotation de leur icône. Les clics rapides peuvent inverser l’animation sans bloquer l’élément. Les programmes restent exclusifs ; le panneau sortant termine sa fermeture pendant l’ouverture du nouveau.
- La réduction des mouvements supprime la transition. Les résumés restent utilisables au clavier ; le contenu en cours de fermeture devient inerte. Sans JavaScript, les accordéons HTML restent fonctionnels et les programmes conservent leur regroupement exclusif natif.

Contrôles : génération des 72 pages et 12 confirmations, neuf scénarios linguistiques, parcours d’accordéons à la souris et au clavier, inversion rapide, réduction des mouvements, exclusivité sans JavaScript, ouverture/fermeture de la galerie, placement des photographies et largeur des récits à 390 et 1440 px. Captures et résultats conservés dans `outputs/v6-adjustments/`. Les 504 contrôles de mise en page sur les six langues et sept largeurs passent sans erreur après ces corrections. Aucun nouveau score Lighthouse n’est revendiqué pour cet ajustement.
