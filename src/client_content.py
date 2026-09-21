"""Client-approved V6 facts and copy, supplied by Eva on 22 September 2026.

Language order is en, fr, nl, de, sv, lb. Portrait identities and horse origins
come from the client. Jackson's sire spelling follows the supplied pedigree
screenshot (Contendro I, whose sire is Contender), rather than the email typo.
"""

PEDIGREES = {
    "dalton": "Don Juan de Hus × Samsara de Hus (Soliman)",
    "juni": "Silver Deux de Virton HDC × Firsty de Prepinson (Eldorado de Hus)",
    "jackson": "Contendro I × Veda de Hus (Spartakhus)",
    "qurious": "Comme Il Faut × Calista FX (Diamant de Semilly)",
}
HORSE_STORIES = tuple(PEDIGREES)

TEXT_UPDATES = {
    "home_title": (
        "Haras de Prepinson | Breeding, Training & Sales",
        "Haras de Prepinson | Élevage, formation et vente de chevaux",
        "Haras de Prepinson | Fokkerij, opleiding en verkoop",
        "Haras de Prepinson | Zucht, Ausbildung und Verkauf",
        "Haras de Prepinson | Avel, utbildning och försäljning",
        "Haras de Prepinson | Zuucht, Ausbildung a Verkaf",
    ),
    "home_desc": (
        "Breeding and training stable in Ortho, in the Belgian Ardennes. Young horse development, sales and boarding, with 30 hectares of fields and professional arenas.",
        "Écurie d’élevage et de formation à Ortho, dans les Ardennes belges. Formation des jeunes chevaux, vente et pension, sur un domaine de 30 hectares.",
        "Fokkerij en opleidingsstal in Ortho, in de Belgische Ardennen. Opleiding van jonge paarden, verkoop en pension, met 30 hectare weiden en professionele pistes.",
        "Zucht- und Ausbildungsstall in Ortho in den belgischen Ardennen. Jungpferdeausbildung, Verkauf und Pension mit 30 Hektar Weiden und professionellen Reitplätzen.",
        "Avels- och utbildningsstall i Ortho i belgiska Ardennerna. Unghästutbildning, försäljning och uppstallning med 30 hektar betesmark och ridbanor för daglig träning.",
        "Zuucht- an Ausbildungsstall zu Ortho an de belschen Ardennen. Ausbildung vu jonke Päerd, Verkaf a Pensioun, mat 30 Hektar Wisen a professionelle Reitpisten.",
    ),
    "stat_breeding": (
        "foaling and young horse boxes, each 5 × 8 m",
        "boxes de poulinage et jeunes chevaux de 5 × 8 m",
        "boxen voor veulenen en jonge paarden, elk 5 × 8 m",
        "Abfohl- und Jungpferdeboxen, je 5 × 8 m",
        "boxar för fölning och unghästar, 5 × 8 m vardera",
        "Boxe fir d'Offillen a jonk Päerd, jeeweils 5 × 8 m",
    ),
    "stat_indoor": ("indoor arena, fibre footing", "manège couvert, sol fibré", "binnenpiste met vezelbodem", "Reithalle mit Faserboden", "ridhus med fiberunderlag", "Reithal mat Faserbuedem"),
    "stat_outdoor": ("outdoor arena, ebb and flow footing", "carrière extérieure, sol à subirrigation", "buitenpiste met eb-en-vloedbodem", "Außenplatz mit Ebbe-Flut-Boden", "utomhusbana med ebb- och flodsystem", "Baussebaan mat Ebbe-Flut-Buedem"),
    "facility_breeding": (
        "Separate breeding stable with 9 large boxes, each 5 × 8 m, for foaling and young horses, and veterinary reproduction equipment.",
        "Écurie d’élevage séparée avec 9 grands boxes de 5 × 8 m pour le poulinage et les jeunes chevaux, et un équipement vétérinaire de reproduction.",
        "Aparte fokkerijstal met 9 ruime boxen van elk 5 × 8 m voor het veulenen en jonge paarden, en veterinaire voortplantingsuitrusting.",
        "Separater Zuchtstall mit 9 großen Boxen von je 5 × 8 m zum Abfohlen und für junge Pferde sowie tiermedizinischer Reproduktionsausrüstung.",
        "Separat avelsstall med 9 stora boxar på 5 × 8 m för fölning och unghästar samt veterinär reproduktionsutrustning.",
        "Separate Zuuchtstall mat 9 grousse Boxe vu jeeweils 5 × 8 m fir d'Offillen a jonk Päerd, a veterinärer Reproduktiounsausrüstung.",
    ),
    "references_title": (
        "Prepinson horses | Dalton, Juni, Jackson and Qurious HS",
        "Les chevaux de Prepinson | Dalton, Juni, Jackson et Qurious HS",
        "Paarden van Prepinson | Dalton, Juni, Jackson en Qurious HS",
        "Prepinsons Pferde | Dalton, Juni, Jackson und Qurious HS",
        "Hästarna på Prepinson | Dalton, Juni, Jackson och Qurious HS",
        "D'Päerd vu Prepinson | Dalton, Juni, Jackson a Qurious HS",
    ),
    "references_hero": ("Horses and their stories.", "Des chevaux, des parcours.", "Paarden en hun verhalen.", "Pferde und ihre Geschichten.", "Hästarna och deras berättelser.", "Päerd an hir Geschichten."),
    "service_references": ("Discover their stories", "Découvrir leurs parcours", "Ontdek hun verhalen", "Ihre Geschichten entdecken", "Läs deras berättelser", "Hir Geschichten entdecken"),
    "service_references_copy": (
        "Dalton, Juni and Jackson were bred at Prepinson. Qurious HS joined us through our partnership with Grevlunda.",
        "Dalton, Juni et Jackson sont nés à Prepinson. Qurious HS nous a rejoints dans le cadre de notre partenariat avec Grevlunda.",
        "Dalton, Juni en Jackson zijn bij Prepinson gefokt. Qurious HS kwam bij ons via onze samenwerking met Grevlunda.",
        "Dalton, Juni und Jackson stammen aus unserer Zucht. Qurious HS kam durch unsere Zusammenarbeit mit Grevlunda hinzu.",
        "Dalton, Juni och Jackson är uppfödda på Prepinson. Qurious HS kom till oss genom vårt samarbete med Grevlunda.",
        "Den Dalton, d'Juni an de Jackson sinn zu Prepinson gezu ginn. De Qurious HS koum duerch eis Partnerschaft mat Grevlunda bei eis.",
    ),
    "dalton_title": (
        "Dalton de Prepinson\nDeveloping towards Grand Prix",
        "Dalton de Prepinson\nEn route vers le Grand Prix",
        "Dalton de Prepinson\nOp weg naar de Grand Prix",
        "Dalton de Prepinson\nAuf dem Weg zum Grand Prix",
        "Dalton de Prepinson\nPå väg mot Grand Prix",
        "Dalton de Prepinson\nUm Wee a Richtung Grand Prix",
    ),
    "dalton_copy": (
        "Born and raised at Prepinson, Dalton was sold to a talented rider in 2025. Since then, he has enjoyed great success and continues his development towards Grand Prix level.",
        "Né et élevé à Prepinson, Dalton a été vendu à un cavalier talentueux en 2025. Depuis, il connaît de beaux succès et poursuit sa formation vers le niveau Grand Prix.",
        "Dalton is geboren en grootgebracht bij Prepinson en werd in 2025 verkocht aan een getalenteerde ruiter. Sindsdien behaalt hij mooie successen en wordt hij verder opgeleid richting Grand Prix.",
        "Dalton wurde in Prepinson geboren und aufgezogen und 2025 an einen talentierten Reiter verkauft. Seitdem feiert er große Erfolge und wird weiter in Richtung Grand Prix ausgebildet.",
        "Dalton föddes och växte upp på Prepinson och såldes till en talangfull ryttare 2025. Sedan dess har han haft fina framgångar och fortsätter sin utbildning mot Grand Prix.",
        "Den Dalton ass zu Prepinson gebuer a grouss ginn a gouf 2025 un en talentéierte Reider verkaaft. Zënterhier huet hie schéin Erfolleger erreecht a gëtt weider a Richtung Grand Prix ausgebilt.",
    ),
    "juni_copy": (
        "Born and raised at Prepinson, Juni showed talent and promise from an early age. In 2025, Lisen and Peder Fredricson joined us as co-owners. Juni is now based at their stable, Grevlunda, in Sweden, where she continues her development as a show jumping horse in one of Europe’s leading equestrian environments.",
        "Née et élevée à Prepinson, Juni a montré des qualités prometteuses dès son plus jeune âge. En 2025, Lisen et Peder Fredricson nous ont rejoints comme copropriétaires. Juni est désormais installée dans leur écurie de Grevlunda, en Suède, où elle poursuit sa formation au saut d’obstacles dans un environnement reconnu au plus haut niveau européen.",
        "Juni is geboren en grootgebracht bij Prepinson en toonde al vroeg haar aanleg. In 2025 werden Lisen en Peder Fredricson samen met ons mede-eigenaar. Juni staat nu op hun stal Grevlunda in Zweden, waar ze zich verder ontwikkelt als springpaard in een van Europa’s toonaangevende sportstallen.",
        "Juni wurde in Prepinson geboren und aufgezogen und zeigte schon früh viel Talent. 2025 kamen Lisen und Peder Fredricson als Miteigentümer hinzu. Heute steht Juni in ihrem Stall Grevlunda in Schweden und setzt dort ihre Ausbildung als Springpferd in einem der führenden europäischen Reitsportbetriebe fort.",
        "Juni föddes och växte upp på Prepinson och visade tidigt sin talang. År 2025 blev Lisen och Peder Fredricson delägare tillsammans med oss. Juni finns nu på deras gård Grevlunda i Sverige, där hon fortsätter sin utveckling som hopphäst i en av Europas främsta ridsportmiljöer.",
        "D'Juni ass zu Prepinson gebuer a grouss ginn an huet schonn als jonkt Päerd vill Talent gewisen. 2025 sinn d'Lisen an de Peder Fredricson als Matbesëtzer dobäikomm. Haut steet si an hirem Stall Grevlunda a Schweden, wou si hir Ausbildung als Sprangpäerd an engem vun de féierenden europäesche Reitsportbetriber weiderféiert.",
    ),
    "jackson_copy": (
        "Jackson was the first horse bred at Prepinson to be approved as a stallion by both Selle Français and Swedish Warmblood. Since his approvals, he has progressed steadily through the levels, consistently performing among the best of his generation each competition year. He was later gelded to focus fully on his development and career as a show jumper. His power, quality and consistency make him a horse whose progress we follow with great interest.",
        "Jackson est le premier cheval né à Prepinson à avoir été approuvé comme étalon par le Selle Français et le Swedish Warmblood. Depuis, il a régulièrement progressé dans les épreuves, figurant parmi les meilleurs de sa génération à chaque saison de concours. Il a ensuite été castré pour se consacrer pleinement à sa formation et à sa carrière en saut d’obstacles. Sa force, sa qualité et sa régularité nous donnent envie de suivre chaque nouvelle étape de son parcours.",
        "Jackson was het eerste bij Prepinson gefokte paard dat als hengst werd goedgekeurd door zowel Selle Français als Swedish Warmblood. Sindsdien is hij gestaag doorgegroeid en behoort hij elk wedstrijdjaar tot de beste paarden van zijn generatie. Later werd hij gecastreerd om zich volledig op zijn ontwikkeling en springcarrière te richten. Met zijn kracht, kwaliteit en regelmaat volgen we zijn verdere loopbaan met veel belangstelling.",
        "Jackson war das erste in Prepinson gezogene Pferd, das sowohl von Selle Français als auch von Swedish Warmblood als Hengst anerkannt wurde. Seitdem hat er sich kontinuierlich weiterentwickelt und zählt in jeder Turniersaison zu den Besten seines Jahrgangs. Später wurde er gelegt, um seine Ausbildung und Karriere als Springpferd ganz in den Mittelpunkt zu stellen. Seine Kraft, Qualität und Beständigkeit machen seinen weiteren Weg für uns besonders spannend.",
        "Jackson var den första hästen uppfödd på Prepinson som godkändes som hingst av både Selle Français och Swedish Warmblood. Sedan dess har han stadigt gått upp i klasserna och hört till de bästa i sin årgång varje tävlingssäsong. Han kastrerades senare för att fullt ut fokusera på sin utveckling och karriär som hopphäst. Med sin styrka, kvalitet och jämnhet är han en häst vars fortsatta utveckling vi följer med stort intresse.",
        "De Jackson war dat éischt zu Prepinson gezu Päerd, dat souwuel vum Selle Français wéi och vum Swedish Warmblood als Hengst unerkannt gouf. Zënterhier ass hie Schrëtt fir Schrëtt an de Klassen eropgaangen a gehéiert all Concourssaison zu de Beschte vu sengem Joergang. Hie gouf spéider kastréiert, fir sech ganz op seng Ausbildung a Karriär als Sprangpäerd ze konzentréieren. Mat senger Kraaft, Qualitéit a Konstanz verfollege mir säi weidere Wee mat vill Interessi.",
    ),
    "qurious_title": (
        "Qurious HS\nWith Peder Fredricson at Grevlunda",
        "Qurious HS\nAvec Peder Fredricson à Grevlunda",
        "Qurious HS\nMet Peder Fredricson bij Grevlunda",
        "Qurious HS\nMit Peder Fredricson in Grevlunda",
        "Qurious HS\nMed Peder Fredricson på Grevlunda",
        "Qurious HS\nMam Peder Fredricson zu Grevlunda",
    ),
    "qurious_copy": (
        "Qurious HS joined Prepinson when we acquired him in partnership with Lisen and Peder Fredricson’s Grevlunda, sharing a strong belief in his potential. Now ridden by Peder Fredricson, he is progressing towards the highest level of show jumping. Although not bred by us, Qurious has become an important part of the Prepinson story, reflecting our ambition to identify and support horses for top-level sport. We are proud to share his journey with Grevlunda.",
        "Qurious HS a rejoint Prepinson lorsque nous l’avons acquis en partenariat avec Grevlunda, l’écurie de Lisen et Peder Fredricson, convaincus ensemble de son potentiel. Aujourd’hui monté par Peder Fredricson, il poursuit sa progression vers le plus haut niveau du saut d’obstacles. Sans être né chez nous, Qurious occupe une place importante dans l’histoire de Prepinson. Son parcours traduit notre volonté de repérer et d’accompagner des chevaux pour le sport de haut niveau, aux côtés de Grevlunda.",
        "Qurious HS kwam bij Prepinson toen we hem samen met Grevlunda, de stal van Lisen en Peder Fredricson, aankochten vanuit een gedeeld vertrouwen in zijn aanleg. Onder Peder Fredricson ontwikkelt hij zich nu richting het hoogste niveau in de springsport. Hoewel hij niet bij ons is gefokt, is Qurious een belangrijk deel van het verhaal van Prepinson. Hij laat zien hoe we talentvolle paarden voor de topsport willen vinden en begeleiden. We zijn trots zijn traject met Grevlunda te delen.",
        "Qurious HS kam zu Prepinson, als wir ihn gemeinsam mit Grevlunda, dem Stall von Lisen und Peder Fredricson, erwarben. Uns verband das Vertrauen in sein Potenzial. Heute wird er von Peder Fredricson geritten und entwickelt sich in Richtung Spitzensport. Obwohl er nicht aus unserer Zucht stammt, ist Qurious ein wichtiger Teil der Geschichte von Prepinson. Er steht für unser Ziel, Pferde für den Spitzensport zu entdecken und zu fördern. Wir sind stolz, diesen Weg mit Grevlunda zu teilen.",
        "Qurious HS kom till Prepinson när vi köpte honom tillsammans med Lisen och Peder Fredricsons Grevlunda, med en gemensam tro på hans potential. Nu rids han av Peder Fredricson och utvecklas mot den högsta nivån inom hoppning. Även om han inte är uppfödd hos oss har Qurious blivit en viktig del av Prepinsons historia. Han speglar vår ambition att hitta och stötta hästar för sporten på högsta nivå. Vi är stolta över att dela hans resa med Grevlunda.",
        "De Qurious HS koum bei Prepinson, wéi mir hien zesumme mat Grevlunda, dem Stall vu Lisen a Peder Fredricson, kaf hunn. Mir hunn all u säi Potenzial gegleeft. Haut gëtt hie vum Peder Fredricson geridden an entwéckelt sech a Richtung héchsten Niveau am Sprangsport. Och wann hien net bei eis gezu gouf, ass hien e wichtegen Deel vun der Geschicht vu Prepinson. Säi Wee weist eis Ambitioun, Päerd fir de Spëtzesport ze entdecken an ze begleeden. Mir si frou, dëse Wee mat Grevlunda ze deelen.",
    ),
}
TEXT_UPDATES["references_desc"] = TEXT_UPDATES["service_references_copy"]

V1_UPDATES = {
    "home_tagline": (
        "Breeding, training, sales and boarding<br>in the Belgian Ardennes.",
        "Élevage, formation, vente et pension<br>dans les Ardennes belges.",
        "Fokkerij, opleiding, verkoop en pension<br>in de Belgische Ardennen.",
        "Zucht, Ausbildung, Verkauf und Pension<br>in den belgischen Ardennen.",
        "Avel, utbildning, försäljning och uppstallning<br>i belgiska Ardennerna.",
        "Zuucht, Ausbildung, Verkaf a Pensioun<br>an de belschen Ardennen.",
    ),
    "home_intro": (
        "We breed, train and sell young horses in Ortho, in the heart of the Belgian Ardennes, with a focus on their long-term development.",
        "À Ortho, au cœur des Ardennes belges, nous élevons, formons et vendons de jeunes chevaux en veillant à leur développement sur le long terme.",
        "In Ortho, in het hart van de Belgische Ardennen, fokken, trainen en verkopen we jonge paarden, met aandacht voor hun ontwikkeling op lange termijn.",
        "In Ortho, im Herzen der belgischen Ardennen, züchten, trainieren und verkaufen wir junge Pferde. Ihre langfristige Entwicklung steht dabei im Mittelpunkt.",
        "Vi föder upp, utbildar och säljer unga hästar i Ortho, mitt i belgiska Ardennerna, med fokus på deras långsiktiga utveckling.",
        "Zu Ortho, am Häerz vun de belschen Ardennen, ziichten, trainéieren a verkafe mir jonk Päerd. Hir laangfristeg Entwécklung steet dobäi am Mëttelpunkt.",
    ),
    "home_intro_programmes": (
        "Our programmes cover every stage of their education, from foal handling and preparation for breaking-in to early ridden work, jumping and competition.",
        "Nos programmes accompagnent chaque étape de leur apprentissage : manipulation du poulain, préparation au débourrage, premiers pas sous la selle, saut d’obstacles et concours.",
        "Onze programma’s begeleiden elke fase van de opleiding: van de omgang met veulens en voorbereiding op het zadelmak maken tot de eerste ritten, springen en wedstrijden.",
        "Unsere Programme begleiten jede Ausbildungsphase: vom Umgang mit Fohlen und der Vorbereitung auf das Anreiten über die ersten Schritte unter dem Sattel bis zum Springen und Turnierstart.",
        "Våra program omfattar varje steg i utbildningen, från fölhantering och förberedelser för inridning till de första passen under ryttare, hoppning och tävling.",
        "Eis Programmer begleeden all Etapp vun der Ausbildung: vum Ëmgang mam Fëllechen an der Virbereedung op d'Areiden iwwer déi éischt Schrëtt ënner dem Suedel bis zum Sprangen a Concoursen.",
    ),
    "home_intro_secondary": (
        "Horses benefit from attentive daily care in a calm, natural environment, with daily turnout across our 30 hectares of fields, training in our arenas and regular riding in the surrounding forests.",
        "Les chevaux bénéficient de soins attentifs dans un cadre calme et naturel. Leur quotidien associe sorties dans nos 30 hectares de prairies, travail dans les pistes et sorties régulières dans les forêts environnantes.",
        "De paarden krijgen zorgvuldige dagelijkse verzorging in een rustige, natuurlijke omgeving. Ze gaan dagelijks naar buiten op onze 30 hectare weiden, trainen in de pistes en maken regelmatig ritten door de omliggende bossen.",
        "Die Pferde werden in ruhiger, natürlicher Umgebung täglich aufmerksam betreut. Dazu gehören täglicher Auslauf auf unseren 30 Hektar Weiden, Training in den Reitbahnen und regelmäßige Ausritte in die umliegenden Wälder.",
        "Hästarna får omsorgsfull daglig skötsel i en lugn och naturlig miljö, med daglig utevistelse på våra 30 hektar betesmark, träning på ridbanorna och regelbundna uteritter i de omgivande skogarna.",
        "D'Päerd ginn an engem rouegen, natierlechen Ëmfeld all Dag mat Opmierksamkeet versuergt. Si kommen all Dag op eis 30 Hektar Wisen, trainéieren op de Pisten a ginn reegelméisseg an de Bëscher ronderëm geridden.",
    ),
    "home_services_line": (
        "BREEDING / TRAINING / SALES", "ÉLEVAGE / FORMATION / VENTE", "FOKKERIJ / OPLEIDING / VERKOOP", "ZUCHT / AUSBILDUNG / VERKAUF", "AVEL / UTBILDNING / FÖRSÄLJNING", "ZUUCHT / AUSBILDUNG / VERKAF",
    ),
}

UI_UPDATES = {
    "intro_label": ("Breeding and training stable", "Écurie d’élevage et de formation", "Fokkerij en opleidingsstal", "Zucht- und Ausbildungsstall", "Avels- och utbildningsstall", "Zuucht- an Ausbildungsstall"),
    "references_label": ("Part of Prepinson", "L’histoire de Prepinson", "Verbonden met Prepinson", "Mit Prepinson verbunden", "En del av Prepinson", "En Deel vu Prepinson"),
    "pedigree": ("Pedigree", "Origines", "Afstamming", "Abstammung", "Härstamning", "Ofstamung"),
    "team_gallery_title": ("The team, every day.", "L’équipe au quotidien.", "Het team, elke dag.", "Unser Team im Alltag.", "Teamet i vardagen.", "D'Ekipp am Alldag."),
    "team_gallery_link": ("More photographs of Prepinson", "Plus de photos de Prepinson", "Meer foto’s van Prepinson", "Weitere Bilder von Prepinson", "Fler bilder från Prepinson", "Méi Fotoe vu Prepinson"),
    "dalton_gallery": (
        "Dalton at Falsterbo, where he won the championship for six-year-old horses.",
        "Dalton à Falsterbo, où il a remporté le championnat des chevaux de six ans.",
        "Dalton in Falsterbo, waar hij het kampioenschap voor zesjarige paarden won.",
        "Dalton in Falsterbo, wo er das Championat der sechsjährigen Pferde gewann.",
        "Dalton i Falsterbo, där han vann championatet för sexåriga hästar.",
        "Den Dalton zu Falsterbo, wou hien de Championnat fir sechsjäreg Päerd gewonnen huet.",
    ),
    "alt_sport_hero": ("Horse training at Haras de Prepinson", "Le travail des chevaux au Haras de Prepinson", "Paardentraining bij Haras de Prepinson", "Pferdeausbildung im Haras de Prepinson", "Hästutbildning på Haras de Prepinson", "Ausbildung vun de Päerd am Haras de Prepinson"),
}

GALLERY_COPY = {
    "prepinson-team-portrait.webp": ("The Prepinson team", "L’équipe de Prepinson", "Het team van Prepinson", "Das Team von Prepinson", "Teamet på Prepinson", "D'Ekipp vu Prepinson"),
    "prepinson-team-arena.webp": ("The team heading towards the outdoor arena", "L’équipe rejoint la carrière extérieure", "Het team op weg naar de buitenpiste", "Das Team auf dem Weg zum Außenplatz", "Teamet på väg till utomhusbanan", "D'Ekipp um Wee bei d'Baussebaan"),
    "prepinson-young-horse.webp": ("A young grey horse in the indoor arena", "Un jeune cheval gris dans le manège", "Een jong schimmelpaard in de binnenpiste", "Ein junger Schimmel in der Reithalle", "En ung skimmel i ridhuset", "E jonkt gro Päerd an der Reithal"),
    "prepinson-pastures.webp": ("Horses in the Prepinson paddocks", "Chevaux dans les paddocks de Prepinson", "Paarden in de paddocks van Prepinson", "Pferde auf den Paddocks von Prepinson", "Hästar i hagarna på Prepinson", "Päerd an de Paddocke vu Prepinson"),
    "prepinson-rider-detail.webp": ("Rider and saddlecloth bearing the Prepinson logo", "Cavalier et tapis de selle aux couleurs de Prepinson", "Ruiter en zadeldek met het logo van Prepinson", "Reiter und Schabracke mit dem Prepinson-Logo", "Ryttare och schabrak med Prepinsons logotyp", "Reider a Suedeldecke mam Logo vu Prepinson"),
    "prepinson-horse-care.webp": ("Preparing a horse for daily work at Prepinson", "Préparation d’un cheval pour le travail quotidien à Prepinson", "Een paard klaarmaken voor het dagelijkse werk bij Prepinson", "Ein Pferd wird in Prepinson für die tägliche Arbeit vorbereitet", "En häst görs i ordning för det dagliga arbetet på Prepinson", "E Päerd gëtt zu Prepinson fir déi deeglech Aarbecht prett gemaach"),
}
GALLERY_COPY["prepinson-sport-horse.webp"] = UI_UPDATES["alt_sport_hero"]
