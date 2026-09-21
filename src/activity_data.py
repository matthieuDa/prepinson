"""Curated activity links and localized descriptions for the Ardennes guide."""

from src.site_data import LANGS


# Each group key maps to a translated heading in site_data.TEXT.
ACTIVITY_GROUPS = (
    ("walking", "act_walk"),
    ("cycling", "act_cycle"),
    ("water", "act_water"),
    ("culture", "act_culture"),
    ("family", "act_family"),
)


# Copy values follow LANGS: English, French, Dutch, German, Swedish,
# Luxembourgish. URLs are the existing official destinations already curated
# for the site; descriptions deliberately omit hours, prices and distances.
ACTIVITIES = (
    {
        "group": "walking",
        "name": "Ortho-Hives Tourisme",
        "url": "https://www.ortho-hives-tourisme.com/randonner",
        "copy": (
            "Marked walks around Ortho and practical information about trail conditions.",
            "Des promenades balisées autour d’Ortho et des informations pratiques sur l’état des sentiers.",
            "Gemarkeerde wandelingen rond Ortho en praktische informatie over de toestand van de paden.",
            "Markierte Wanderungen rund um Ortho und praktische Hinweise zum Zustand der Wege.",
            "Markerade vandringsleder runt Ortho och information om vandringsledernas skick.",
            "Markéiert Wanderunge ronderëm Ortho a praktesch Informatiounen iwwer den Zoustand vun de Weeër.",
        ),
    },
    {
        "group": "walking",
        "name": "Lac et barrage de Nisramont",
        "url": "https://www.la-roche-tourisme.com/le-lac-et-le-barrage-de-nisramont/",
        "copy": (
            "Lakeside and forest paths where the two branches of the Ourthe meet.",
            "Des sentiers entre lac et forêt, à la rencontre des deux branches de l’Ourthe.",
            "Paden langs het meer en door het bos, waar de twee takken van de Ourthe samenkomen.",
            "Wege am See und durch den Wald, wo die beiden Arme der Ourthe zusammenfließen.",
            "Stigar längs sjön och genom skogen där Ourthes två grenar möts.",
            "Weeër laanscht de Séi an duerch de Bësch, wou déi zwou Ourthe-Aarme zesummekommen.",
        ),
    },
    {
        "group": "walking",
        "name": "Le Hérou",
        "url": "https://www.luxembourg-belge.be/diffusio/fr/voir-faire/visiter/patrimoine-naturel/nadrin/le-herou_TFOALD-01-08H9-01.php",
        "copy": (
            "A natural site above the Ourthe, discovered along its forest walking routes.",
            "Un site naturel au-dessus de l’Ourthe, à découvrir par ses sentiers forestiers.",
            "Een natuurgebied boven de Ourthe, te ontdekken via bospaden.",
            "Ein Naturgebiet über der Ourthe, das sich auf Waldwegen entdecken lässt.",
            "Ett naturområde ovanför Ourthe som upptäcks längs skogsstigar.",
            "En Natursite iwwer der Ourthe, deen een iwwer Bëschweeër entdecke kann.",
        ),
    },
    {
        "group": "cycling",
        "name": "SoWatt e-bike",
        "url": "https://sowatt.bike/fr",
        "copy": (
            "Bike and e-bike hire, with guided rides from La Roche-en-Ardenne.",
            "Location de vélos et vélos électriques, avec sorties guidées au départ de La Roche-en-Ardenne.",
            "Verhuur van fietsen en e-bikes, met begeleide tochten vanuit La Roche-en-Ardenne.",
            "Fahrrad- und E-Bike-Verleih mit geführten Touren ab La Roche-en-Ardenne.",
            "Cykel- och elcykeluthyrning med guidade turer från La Roche-en-Ardenne.",
            "Vëlo- an E-Bike-Locatioun mat guidéierten Touren ab La Roche-en-Ardenne.",
        ),
    },
    {
        "group": "cycling",
        "name": "Trott-e-Trail",
        "url": "https://www.trott-e-trail.com/",
        "copy": (
            "Guided rides on all-terrain electric scooters through the Ourthe valley.",
            "Des balades guidées en trottinette électrique tout-terrain dans la vallée de l’Ourthe.",
            "Begeleide ritten op elektrische terreinsteps door de Ourthevallei.",
            "Geführte Touren mit geländegängigen E-Scootern durch das Ourthe-Tal.",
            "Guidade turer med terränggående elsparkcyklar genom Ourthedalen.",
            "Guidéiert Touren op elektreschen Offroad-Trottinetten duerch den Ourthe-Dall.",
        ),
    },
    {
        "group": "water",
        "name": "Brandsport",
        "url": "https://www.brandsport.be/",
        "copy": (
            "Kayaking and rafting on the Ourthe, alongside other outdoor activities.",
            "Kayak et rafting sur l’Ourthe, parmi d’autres activités de plein air.",
            "Kajakken en raften op de Ourthe, naast andere buitenactiviteiten.",
            "Kajak und Rafting auf der Ourthe sowie weitere Outdoor-Aktivitäten.",
            "Kajak och forsränning på Ourthe, tillsammans med andra utomhusaktiviteter.",
            "Kajak a Rafting op der Ourthe, nieft aneren Outdoor-Aktivitéiten.",
        ),
    },
    {
        "group": "water",
        "name": "Ardenne Aventures",
        "url": "https://ardenneaventures.com/",
        "copy": (
            "Kayaking, mountain biking and treetop courses from La Roche-en-Ardenne.",
            "Kayak, VTT et parcours dans les arbres au départ de La Roche-en-Ardenne.",
            "Kajakken, mountainbiken en boomparcours vanuit La Roche-en-Ardenne.",
            "Kajak, Mountainbike und Hochseilparcours ab La Roche-en-Ardenne.",
            "Kajak, mountainbike och höghöjdsbanor från La Roche-en-Ardenne.",
            "Kajak, Mountainbike an Héichseel-Parcours ab La Roche-en-Ardenne.",
        ),
    },
    {
        "group": "culture",
        "name": "Le Cheslé",
        "url": "https://www.la-roche-tourisme.com/la-forteresse-celtique-du-chesle/",
        "copy": (
            "A Celtic archaeological site reached on foot through the forest.",
            "Un site archéologique celtique que l’on rejoint à pied à travers la forêt.",
            "Een Keltische archeologische site die te voet door het bos bereikbaar is.",
            "Eine keltische Ausgrabungsstätte, die zu Fuß durch den Wald erreichbar ist.",
            "En keltisk fornlämning som nås till fots genom skogen.",
            "En kelteschen archeologesche Site, deen een zu Fouss duerch de Bësch erreecht.",
        ),
    },
    {
        "group": "culture",
        "name": "Syndicat d’Initiative de La Roche-en-Ardenne",
        "url": "https://www.la-roche-tourisme.com/",
        "copy": (
            "Local ideas for heritage, nature, food and outings in La Roche-en-Ardenne.",
            "Des idées locales autour du patrimoine, de la nature, du terroir et des sorties à La Roche-en-Ardenne.",
            "Lokale ideeën voor erfgoed, natuur, streekproducten en uitstappen in La Roche-en-Ardenne.",
            "Lokale Anregungen zu Kulturerbe, Natur, regionalen Produkten und Ausflügen in La Roche-en-Ardenne.",
            "Lokala tips om kulturarv, natur, mat och utflykter i La Roche-en-Ardenne.",
            "Lokal Iddien iwwer Patrimoine, Natur, regional Produiten an Ausflich zu La Roche-en-Ardenne.",
        ),
    },
    {
        "group": "culture",
        "name": "Château féodal de La Roche-en-Ardenne",
        "url": "https://www.chateaudelaroche.be/",
        "copy": (
            "The ruins of a medieval castle overlooking La Roche-en-Ardenne and the Ourthe valley.",
            "Les ruines d’un château médiéval qui domine La Roche-en-Ardenne et la vallée de l’Ourthe.",
            "De ruïnes van een middeleeuws kasteel boven La Roche-en-Ardenne en de Ourthevallei.",
            "Die Ruinen einer mittelalterlichen Burg über La Roche-en-Ardenne und dem Ourthe-Tal.",
            "Ruinerna av en medeltida borg ovanför La Roche-en-Ardenne och Ourthedalen.",
            "D'Ruine vun enger mëttelalterlecher Buerg iwwer La Roche-en-Ardenne an dem Ourthe-Dall.",
        ),
    },
    {
        "group": "culture",
        "name": "Brasserie d’Achouffe",
        "url": "https://chouffe.com/",
        "copy": (
            "A brewery visit devoted to the making of its local beers.",
            "Une visite de la brasserie consacrée à la fabrication de ses bières locales.",
            "Een brouwerijbezoek over de productie van de lokale bieren.",
            "Eine Brauereibesichtigung zur Herstellung der regionalen Biere.",
            "Ett bryggeribesök om hur de lokala ölsorterna tillverkas.",
            "Eng Brauereivisitt iwwer d'Produktioun vun de lokale Béier.",
        ),
    },
    {
        "group": "family",
        "name": "Wildtrails",
        "url": "https://www.wildtrails.be/",
        "copy": (
            "Organised group experiences and private venues around Jupille and Rendeux.",
            "Des expériences organisées pour les groupes et des lieux privatifs autour de Jupille et Rendeux.",
            "Georganiseerde groepservaringen en privélocaties rond Jupille en Rendeux.",
            "Organisierte Gruppenerlebnisse und private Veranstaltungsorte rund um Jupille und Rendeux.",
            "Organiserade gruppupplevelser och privata mötesplatser runt Jupille och Rendeux.",
            "Organiséiert Erliefnisser fir Gruppen a privat Plazen ronderëm Jupille a Rendeux.",
        ),
    },
    {
        "group": "family",
        "name": "Parc à Gibier",
        "url": "https://www.parc-gibier-laroche.be/",
        "copy": (
            "A walking route among animals from Ardennes forests and the farm.",
            "Un parcours à pied parmi les animaux des forêts ardennaises et de la ferme.",
            "Een wandelroute langs dieren uit de Ardense bossen en van de boerderij.",
            "Ein Rundweg zu Tieren aus den Ardennenwäldern und vom Bauernhof.",
            "En promenadslinga bland djur från Ardennernas skogar och bondgården.",
            "E Fousswee laanscht Déieren aus den Ardennebëscher a vum Bauerenhaff.",
        ),
    },
    {
        "group": "family",
        "name": "Grottes de Hotton",
        "url": "https://grottesdehotton.be/",
        "copy": (
            "A guided underground visit through the natural galleries of the Hotton caves.",
            "Une visite souterraine guidée dans les galeries naturelles des grottes de Hotton.",
            "Een begeleid ondergronds bezoek door de natuurlijke galerijen van de grotten van Hotton.",
            "Eine geführte unterirdische Besichtigung durch die natürlichen Galerien der Grotten von Hotton.",
            "En guidad underjordisk tur genom Hotton-grottornas naturliga salar.",
            "Eng guidéiert Visitt ënner dem Buedem duerch déi natierlech Galerie vun de Grotte vun Hotton.",
        ),
    },
    {
        "group": "family",
        "name": "Parc Chlorophylle",
        "url": "https://www.parcchlorophylle.com/",
        "copy": (
            "A recreational forest park for discovering the woodland on foot with children.",
            "Un parc forestier récréatif pour découvrir la forêt à pied avec les enfants.",
            "Een recreatief bospark om het bos te voet met kinderen te ontdekken.",
            "Ein Freizeit-Waldpark, in dem Familien den Wald zu Fuß entdecken können.",
            "En skogspark där familjer kan upptäcka skogen till fots.",
            "E Fräizäit-Bëschpark, fir de Bësch mat Kanner zu Fouss ze entdecken.",
        ),
    },
    {
        "group": "family",
        "name": "Houtopia",
        "url": "https://www.houtopia.be/",
        "copy": (
            "Indoor sensory activities and an outdoor play area centred on the five senses.",
            "Des expériences sensorielles à l’intérieur et une plaine de jeux extérieure autour des cinq sens.",
            "Zintuiglijke activiteiten binnen en een buitenspeelterrein rond de vijf zintuigen.",
            "Sinneserlebnisse im Innenbereich und ein Außenspielplatz rund um die fünf Sinne.",
            "Sinnesaktiviteter inomhus och en lekplats utomhus med fokus på de fem sinnena.",
            "Sensoresch Aktivitéiten dobannen an eng Spillplaz dobaussen ronderëm déi fënnef Sënner.",
        ),
    },
)


def activity_copy(item, lang):
    """Return one activity description in the requested language."""
    values = item["copy"]
    if len(values) != len(LANGS):
        raise ValueError(f"Activity {item['name']!r} has {len(values)} translations")
    return values[LANGS.index(lang)]


def _validate():
    groups = {key for key, _ in ACTIVITY_GROUPS}
    urls = set()
    for item in ACTIVITIES:
        if item["group"] not in groups:
            raise ValueError(f"Unknown activity group {item['group']!r}")
        if item["url"] in urls:
            raise ValueError(f"Duplicate activity URL {item['url']!r}")
        urls.add(item["url"])
        activity_copy(item, LANGS[0])


_validate()
