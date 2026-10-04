# Prépinson — trois nuances de finition

Référence figée : `7c464e89719ebffb9e9464359724cafe8eb7e518`, branche `codex/prepinson-navigation-motion`, preview n°3. Le site publié et cette branche ne sont pas modifiés.

Le brief est une finition du design approuvé, avec le contenu définitif. Les polices Cormorant Garamond et DM Sans, les couleurs, les photos, les textes, l'ordre du contenu et les fonctionnalités sont conservés.

## Propositions

- **Équilibre — option retenue** : colonne de lecture adaptée aux trois paragraphes, navbar transparente au flou progressif neutre, sous-menus clairs sur trois colonnes.
- **Éditorial** : lecture légèrement plus ample, portrait plus discret, sous-menus en Cormorant Garamond.
- **Serein** : titres un peu plus contenus, rythme légèrement resserré, panneau de navigation sur deux colonnes.

Comparaison : `/propositions/`. Chaque site est disponible sous `/propositions/{equilibre,editorial,serein}/{fr,en,nl,de,sv,lb}/`. Les liens de navigation, le changement de langue et les confirmations restent dans la proposition choisie. Le sélecteur de langue de la page de comparaison concerne les aperçus ; les notes de présentation sont en français.

## Isolation et construction

`npm run build:proposals` construit d'abord la référence avec son générateur d'origine. Il crée ensuite trois copies de chaque page, en ajoutant seulement les feuilles CSS et le petit script de synchronisation géométrique de la navigation et de décoration du flou, et en préfixant les destinations internes. Les assets restent partagés et inchangés. Une normalisation stricte vérifie à la génération et dans `check_site.py` que les trois copies restituent exactement le HTML de référence.

Sources : `src/designs/refinement.css` (socle commun), les trois petites feuilles de variante et `refinement.js`. Aucun changement au générateur d'origine, au JavaScript métier ou aux fichiers de contenu. Les sorties de comparaison sont ignorées par Git et reconstruites par Netlify sur cette branche. Les aperçus sont marqués `noindex`.

Après le choix du client, intégrer seulement le socle, la feuille retenue et, si nécessaire, la synchronisation du bord du header. Les copies de pages et la page de comparaison n'ont pas vocation à rejoindre la production.

## Responsive et validation

Les contenus commandent la hauteur des heroes. Les colonnes se réorganisent à des largeurs adaptées au contenu ; les menus restent défilables dans les fenêtres peu hautes. Les contrôles tactiles, le clavier, la réduction des mouvements, le mode sans JavaScript et les confirmations sont vérifiés.

La matrice couvre 20 formats de 280 à 2560 pixels, dont 540 × 720, 1114 × 720, 844 × 390 et le reflow à 720 pixels correspondant à une fenêtre de 1440 pixels zoomée à 200 %. Il s'agit de fenêtres de navigateur simulées, pas d'une recette sur appareils pliables physiques ni d'une simulation matérielle de charnière.

Commandes : `npm run test:proposals`, `npm run test:a11y:proposals`, `node scripts/check_proposal_forms.mjs`. Playwright, axe-core et les navigateurs se configurent avec `PLAYWRIGHT_MODULE`, `AXE_MODULE`, `PLAYWRIGHT_BROWSERS_PATH` et `CHROME_PATH`. Les soumissions des tests sont interceptées ; aucun message n'est envoyé.

Les vignettes proviennent des vrais aperçus. Elles peuvent être régénérées avec `CAPTURE_PREVIEWS=1 node scripts/check_proposal_forms.mjs`. Le rapport final est enregistré dans `docs/audits/2026-10-02-design-proposals.json`.

## Équilibre retenue — 4 octobre 2026

La navbar reprend le flou progressif de la capture client : six couches masquées de 1 à 24 pixels, un voile neutre et une disparition douce vers la photo. Le fond vert, la bordure horizontale et l'ombre du header sont retirés. Le petit soulignement doré de la rubrique active reste présent. Le bouton Contact et le séparateur vertical des langues suivent la capture.

Le header reste transparent au défilement ; le voile devient plus soutenu pour garder les libellés blancs lisibles au-dessus des sections claires. Sur les pages sans hero photographique, les libellés sont foncés au repos, y compris lorsque le menu mobile est ouvert. Les couches de flou sont décoratives, sans événements de pointeur ni entrée dans l'arbre d'accessibilité. Le masque CSS fournit aussi un flou de repli sans JavaScript. Les préférences de réduction des mouvements, de réduction de la transparence et de couleurs forcées sont conservées ou prises en compte.

Principe technique de référence : [Progressive blur in CSS, Kenneth Nym](https://kennethnym.com/blog/progressive-blur-in-css/). L'effet ne dépend d'aucune bibliothèque.

Lien de revue : `/propositions/equilibre/fr/`. Les deux autres nuances restent disponibles pour comparaison ; elles n'activent pas les couches de flou. La vignette Équilibre et la mention « Option retenue » sont actualisées.

Validation ciblée : 1 800 configurations de mise en page et 67 contrôles d'interaction par moteur (Chromium et WebKit), six langues, 20 formats, 49 états axe sans violation détectée. Les contrôles complémentaires du flou, du menu mobile, des préférences d'affichage et du repli sans JavaScript figurent dans `docs/audits/2026-10-04-progressive-nav.json`. Les corrections finales du contraste du menu mobile sur page claire et de l’activation au premier chargement Safari ont été revérifiées sur les deux moteurs (110 assertions complémentaires sans échec).
