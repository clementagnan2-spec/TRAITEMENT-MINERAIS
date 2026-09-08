# -*- coding: utf-8 -*-
"""
Référentiel des postes/circuits de l'usine, utilisé pour :
  - amorcer la table postes_reference en base au premier lancement
  - proposer les listes déroulantes de paramètres usuels par poste dans les
    formulaires de saisie de relevés

Librement adaptable : ajoutez, renommez ou retirez des postes ici pour
coller exactement au flowsheet réel de votre usine — la base de données
s'ajustera au prochain lancement (les postes déjà en base ne sont jamais
supprimés automatiquement, pour ne pas perdre l'historique).
"""

POSTES_REF = [
    {"id": "A0", "partie": "A — Fragmentation", "titre": "ROM Pad (Grade Control)",
     "parametres": [("Teneur moyenne du tas", "%"), ("Tonnage disponible du tas", "t"),
                    ("Humidité du tas", "%"), ("Nombre de tas actifs", "")]},
    {"id": "A1", "partie": "A — Fragmentation", "titre": "Circuit de concassage",
     "parametres": [("Intensité électrique moteur", "A"), ("Débit d'alimentation", "t/h"),
                    ("Granulométrie de sortie (P80)", "mm")]},
    {"id": "A2", "partie": "A — Fragmentation", "titre": "Circuit de broyage",
     "parametres": [("Pourcentage de solides", "%"), ("Débit d'alimentation", "t/h"),
                    ("Pression cyclone", "kPa"), ("Débit cyclone", "m³/h"),
                    ("P80 overflow", "µm")]},
    {"id": "B2", "partie": "B — Concentration", "titre": "Récupération magnétique",
     "parametres": [("Débit d'alimentation", "t/h"), ("Intensité du champ", "gauss")]},
    {"id": "B3", "partie": "B — Concentration", "titre": "Récupération gravimétrique",
     "parametres": [("Pourcentage de solides", "%"), ("Débit d'eau de lavage", "m³/h")]},
    {"id": "B4", "partie": "B — Concentration", "titre": "Flottation",
     "parametres": [("pH", ""), ("Débit d'air", "Nm³/h"), ("Pourcentage de solides", "%"),
                    ("Niveau de pulpe", "%")]},
    {"id": "C1", "partie": "C — Hydrométallurgie", "titre": "Lixiviation en tas",
     "parametres": [("Débit d'arrosage", "m³/h"), ("Concentration réactif", "g/L"),
                    ("pH solution", "")]},
    {"id": "C2", "partie": "C — Hydrométallurgie", "titre": "Lixiviation sous pression",
     "parametres": [("Pression", "bar"), ("Température", "°C")]},
    {"id": "C3", "partie": "C — Hydrométallurgie", "titre": "Lixiviation en cuve",
     "parametres": [("pH", ""), ("ORP", "mV"), ("Concentration réactif libre", "g/L"),
                    ("Temps de séjour", "h")]},
    {"id": "C4", "partie": "C — Hydrométallurgie", "titre": "Adsorption CIL/CIP",
     "parametres": [("Concentration charbon par cuve", "g/L"),
                    ("Teneur métal solution entrée", "ppm"),
                    ("Teneur métal solution sortie", "ppm")]},
    {"id": "D1", "partie": "D — Finition", "titre": "Conditionnement / finition",
     "parametres": [("Humidité résiduelle", "%"), ("Poids net conditionné", "kg")]},
    {"id": "D2", "partie": "D — Finition", "titre": "Raffinage",
     "parametres": [("Pureté du métal (loi)", "%"), ("Masse de métal raffiné", "kg"),
                    ("Pertes de fusion/affinage", "%")]},
    {"id": "D3", "partie": "D — Finition", "titre": "Gestion des rejets (Tailings)",
     "parametres": [("Débit de pulpe vers le parc à résidus", "m³/h"),
                    ("Teneur résiduelle en métal", "%"), ("Niveau du parc à résidus", "m")]},
]


# ---------------------------------------------------------------------
# Barème normal des indicateurs (bornes de conformité)
# ---------------------------------------------------------------------
# Ce barème définit, pour chaque couple (poste, paramètre), la plage de
# valeurs considérée comme normale en exploitation courante. Il sert à
# déclencher une alerte de non-conformité lors de la saisie d'un relevé
# (voir ui_releves.py) et à repérer les dérives dans l'historique.
#
# Format : (poste_id, "nom exact du paramètre") -> (borne_min, borne_max)
#   - Utilisez None pour une borne non contrainte (ex. (None, 10) = "≤ 10").
#   - Un couple absent de ce dictionnaire n'est simplement pas contrôlé.
#
# IMPORTANT : les valeurs ci-dessous sont des valeurs indicatives de
# démarrage. Elles DOIVENT être ajustées par un responsable process/
# métallurgie pour correspondre aux normes réelles de votre usine avant
# une mise en exploitation.
BAREME_NORMES = {
    # A0 — ROM Pad (Grade Control)
    ("A0", "Teneur moyenne du tas"): (0.5, 5.0),
    ("A0", "Tonnage disponible du tas"): (500, 50000),
    ("A0", "Humidité du tas"): (2, 12),
    ("A0", "Nombre de tas actifs"): (1, 6),

    # A1 — Circuit de concassage
    ("A1", "Intensité électrique moteur"): (50, 250),
    ("A1", "Débit d'alimentation"): (100, 800),
    ("A1", "Granulométrie de sortie (P80)"): (5, 25),

    # A2 — Circuit de broyage
    ("A2", "Pourcentage de solides"): (60, 78),
    ("A2", "Débit d'alimentation"): (100, 600),
    ("A2", "Pression cyclone"): (50, 150),
    ("A2", "Débit cyclone"): (200, 1200),
    ("A2", "P80 overflow"): (75, 150),

    # B2 — Récupération magnétique
    ("B2", "Débit d'alimentation"): (50, 400),
    ("B2", "Intensité du champ"): (500, 3000),

    # B3 — Récupération gravimétrique
    ("B3", "Pourcentage de solides"): (20, 45),
    ("B3", "Débit d'eau de lavage"): (10, 100),

    # B4 — Flottation
    ("B4", "pH"): (7, 11),
    ("B4", "Débit d'air"): (50, 500),
    ("B4", "Pourcentage de solides"): (25, 40),
    ("B4", "Niveau de pulpe"): (60, 90),

    # C1 — Lixiviation en tas
    ("C1", "Débit d'arrosage"): (5, 50),
    ("C1", "Concentration réactif"): (0.1, 2.0),
    ("C1", "pH solution"): (9, 11),

    # C2 — Lixiviation sous pression
    ("C2", "Pression"): (10, 60),
    ("C2", "Température"): (80, 220),

    # C3 — Lixiviation en cuve
    ("C3", "pH"): (9.5, 11.5),
    ("C3", "ORP"): (100, 250),
    ("C3", "Concentration réactif libre"): (0.05, 1.0),
    ("C3", "Temps de séjour"): (12, 36),

    # C4 — Adsorption CIL/CIP
    ("C4", "Concentration charbon par cuve"): (10, 30),
    ("C4", "Teneur métal solution entrée"): (0.5, 5),
    ("C4", "Teneur métal solution sortie"): (None, 0.05),

    # D1 — Conditionnement / finition
    ("D1", "Humidité résiduelle"): (None, 8),
    ("D1", "Poids net conditionné"): (10, 1000),

    # D2 — Raffinage
    ("D2", "Pureté du métal (loi)"): (99.0, 99.99),
    ("D2", "Masse de métal raffiné"): (None, 500),
    ("D2", "Pertes de fusion/affinage"): (None, 2),

    # D3 — Gestion des rejets (Tailings)
    ("D3", "Débit de pulpe vers le parc à résidus"): (50, 500),
    ("D3", "Teneur résiduelle en métal"): (None, 0.1),
    ("D3", "Niveau du parc à résidus"): (None, 30),
}


def obtenir_bareme(poste_id, parametre):
    """Retourne (borne_min, borne_max) pour un couple (poste, paramètre),
    ou None si aucune norme n'est définie pour ce paramètre."""
    return BAREME_NORMES.get((poste_id, parametre))


def evaluer_conformite(poste_id, parametre, valeur):
    """Compare une valeur mesurée au barème normal.

    Retourne un tuple (conforme, borne_min, borne_max) :
      - conforme = True  -> valeur dans la plage normale
      - conforme = False -> valeur hors plage (non-conformité)
      - conforme = None  -> aucun barème défini pour ce paramètre
    """
    bareme = obtenir_bareme(poste_id, parametre)
    if bareme is None:
        return None, None, None
    borne_min, borne_max = bareme
    conforme = True
    if borne_min is not None and valeur < borne_min:
        conforme = False
    if borne_max is not None and valeur > borne_max:
        conforme = False
    return conforme, borne_min, borne_max


# ---------------------------------------------------------------------
# Description du risque encouru en cas de non-conformité
# ---------------------------------------------------------------------
# Pour chaque couple (poste, paramètre) déjà présent dans BAREME_NORMES, ce
# dictionnaire donne une phrase courte expliquant le risque opérationnel
# concret selon que la valeur mesurée est AU-DESSUS ("haut") ou EN-DESSOUS
# ("bas") de la norme — plutôt que le simple mot « Non conforme » affiché
# dans l'historique des relevés (voir ui_releves.py).
#
# Un couple (poste, paramètre) sans entrée ici, ou une direction absente
# (ex. barème à une seule borne), retombe sur un message générique dans
# decrire_risque(). Adaptez librement ces textes à votre procédé réel.
RISQUES = {
    # A0 — ROM Pad (Grade Control)
    ("A0", "Teneur moyenne du tas"): {
        "haut": "teneur inhabituellement élevée — vérifier l'échantillonnage, risque "
                "d'erreur d'estimation des réserves",
        "bas": "teneur trop faible — risque de traiter un tout-venant sous-économique",
    },
    ("A0", "Tonnage disponible du tas"): {
        "haut": "tas surdimensionné — risque de dégradation/oxydation prolongée avant "
                "traitement",
        "bas": "stock tampon insuffisant — risque de rupture d'alimentation du concassage",
    },
    ("A0", "Humidité du tas"): {
        "haut": "minerai trop humide — risque de colmatage des convoyeurs et des grilles",
        "bas": "minerai trop sec — risque d'émission de poussières",
    },
    ("A0", "Nombre de tas actifs"): {
        "haut": "trop de tas actifs simultanés — dilution du contrôle de la teneur "
                "d'alimentation (grade control)",
        "bas": "trop peu de tas actifs — risque de rupture d'approvisionnement en cas "
               "d'arrêt d'un front",
    },

    # A1 — Circuit de concassage
    ("A1", "Intensité électrique moteur"): {
        "haut": "surtension moteur — risque de surchauffe et de casse mécanique du "
                "concasseur",
        "bas": "sous-charge — fonctionnement à vide, usure inutile",
    },
    ("A1", "Débit d'alimentation"): {
        "haut": "surcharge du concasseur — risque de bourrage et de blocage en chambre",
        "bas": "sous-alimentation — perte de productivité",
    },
    ("A1", "Granulométrie de sortie (P80)"): {
        "haut": "produit trop grossier — surcharge du circuit de broyage en aval",
        "bas": "sur-concassage — consommation d'énergie et usure excessives",
    },

    # A2 — Circuit de broyage
    ("A2", "Pourcentage de solides"): {
        "haut": "pulpe trop épaisse — risque de colmatage du broyeur et de "
                "surconsommation énergétique",
        "bas": "pulpe trop diluée — perte d'efficacité de broyage",
    },
    ("A2", "Débit d'alimentation"): {
        "haut": "surcharge du broyeur — risque de débordement",
        "bas": "sous-charge — broyage inefficace, sur-broyage du produit",
    },
    ("A2", "Pression cyclone"): {
        "haut": "pression excessive — risque de colmatage (apex/vortex bouché) et "
                "d'usure prématurée de la pompe",
        "bas": "pression insuffisante — mauvaise classification, produit trop grossier",
    },
    ("A2", "Débit cyclone"): {
        "haut": "débit excessif — usure accélérée du cyclone",
        "bas": "débit insuffisant — signe possible de colmatage du cyclone",
    },
    ("A2", "P80 overflow"): {
        "haut": "produit de broyage trop grossier — perte de libération minérale en aval",
        "bas": "sur-broyage — surconsommation d'énergie, génération excessive de fines",
    },

    # B2 — Récupération magnétique
    ("B2", "Débit d'alimentation"): {
        "haut": "surcharge du séparateur magnétique — perte de récupération",
        "bas": "sous-charge — perte de productivité",
    },
    ("B2", "Intensité du champ"): {
        "haut": "champ excessif — récupération de gangue non magnétique, perte de "
                "qualité du concentré",
        "bas": "champ magnétique insuffisant — perte de récupération du minéral "
               "magnétique",
    },

    # B3 — Récupération gravimétrique
    ("B3", "Pourcentage de solides"): {
        "haut": "pulpe trop épaisse — mauvaise séparation gravimétrique",
        "bas": "pulpe trop diluée — perte de récupération, surconsommation d'eau",
    },
    ("B3", "Débit d'eau de lavage"): {
        "haut": "lavage excessif — perte de minéral utile entraîné avec l'eau de lavage",
        "bas": "lavage insuffisant — concentré contaminé par la gangue",
    },

    # B4 — Flottation
    ("B4", "pH"): {
        "haut": "pH trop alcalin — dépression du minéral utile, perte de récupération, "
                "surconsommation de réactifs",
        "bas": "pH trop acide — mauvaise sélectivité de la flottation, risque de "
               "corrosion des équipements",
    },
    ("B4", "Débit d'air"): {
        "haut": "aération excessive — mousse instable, entraînement de gangue",
        "bas": "aération insuffisante — mauvaise formation de mousse, perte de "
               "récupération",
    },
    ("B4", "Pourcentage de solides"): {
        "haut": "pulpe trop épaisse — mauvaise flottation",
        "bas": "pulpe trop diluée — perte de capacité, surconsommation de réactifs",
    },
    ("B4", "Niveau de pulpe"): {
        "haut": "niveau de pulpe haut — risque de débordement de la cellule",
        "bas": "niveau de pulpe bas — temps de rétention insuffisant, perte de "
               "récupération",
    },

    # C1 — Lixiviation en tas
    ("C1", "Débit d'arrosage"): {
        "haut": "arrosage excessif — dilution de la solution riche, surconsommation d'eau",
        "bas": "arrosage insuffisant — lixiviation incomplète, perte de récupération",
    },
    ("C1", "Concentration réactif"): {
        "haut": "concentration en réactif de cyanuration élevée — zone à forte "
                "concentration de cyanure, risque HSE et surcoût réactif",
        "bas": "concentration insuffisante — lixiviation incomplète, perte de "
               "récupération",
    },
    ("C1", "pH solution"): {
        "haut": "pH excessif — surconsommation de chaux",
        "bas": "pH insuffisamment alcalin — risque de dégagement de gaz cyanhydrique "
               "(HCN), danger pour les opérateurs",
    },

    # C2 — Lixiviation sous pression
    ("C2", "Pression"): {
        "haut": "pression excessive — risque de dépassement des limites de sécurité de "
                "l'autoclave",
        "bas": "pression insuffisante — réaction de lixiviation incomplète",
    },
    ("C2", "Température"): {
        "haut": "température excessive — risque pour l'intégrité de l'autoclave",
        "bas": "température insuffisante — cinétique ralentie, perte de récupération",
    },

    # C3 — Lixiviation en cuve
    ("C3", "pH"): {
        "haut": "pH excessif — surconsommation de chaux",
        "bas": "pH insuffisamment alcalin — risque de dégagement de gaz cyanhydrique "
               "(HCN), danger pour les opérateurs",
    },
    ("C3", "ORP"): {
        "haut": "potentiel redox élevé — surconsommation d'oxydant",
        "bas": "potentiel redox insuffisant — cinétique de dissolution du métal ralentie",
    },
    ("C3", "Concentration réactif libre"): {
        "haut": "concentration en cyanure libre élevée — zone à forte concentration de "
                "cyanure, risque HSE",
        "bas": "concentration insuffisante — lixiviation incomplète",
    },
    ("C3", "Temps de séjour"): {
        "haut": "temps de séjour excessif — perte de capacité de traitement",
        "bas": "temps de séjour insuffisant — lixiviation incomplète, perte de "
               "récupération",
    },

    # C4 — Adsorption CIL/CIP
    ("C4", "Concentration charbon par cuve"): {
        "haut": "charge de charbon excessive — risque de saturation prématurée du charbon",
        "bas": "charge de charbon insuffisante — perte de métal en solution résiduelle",
    },
    ("C4", "Teneur métal solution entrée"): {
        "haut": "teneur d'entrée anormalement élevée — vérifier l'étape de lixiviation "
                "en amont",
        "bas": "teneur faible en entrée — sous-utilisation du circuit d'adsorption",
    },
    ("C4", "Teneur métal solution sortie"): {
        "haut": "perte de métal en solution de queue — récupération insuffisante, "
                "revoir le circuit CIL/CIP",
    },

    # D1 — Conditionnement / finition
    ("D1", "Humidité résiduelle"): {
        "haut": "produit trop humide — non-conformité pour l'expédition, risque de "
                "dégradation en stockage",
    },

    # D2 — Raffinage
    ("D2", "Pureté du métal (loi)"): {
        "bas": "métal sous la pureté requise — non-conformité produit, risque de rejet "
               "par l'acheteur",
    },
    ("D2", "Masse de métal raffiné"): {
        "haut": "masse anormalement élevée pour une coulée — vérifier la pesée et "
                "l'enregistrement",
    },
    ("D2", "Pertes de fusion/affinage"): {
        "haut": "pertes de fusion/affinage supérieures à la norme — perte de rendement "
                "métallurgique",
    },

    # D3 — Gestion des rejets (Tailings)
    ("D3", "Débit de pulpe vers le parc à résidus"): {
        "haut": "débit excessif vers le parc à résidus — risque de surcharge "
                "hydraulique de la digue",
        "bas": "débit anormalement bas — vérifier une éventuelle obstruction en amont",
    },
    ("D3", "Teneur résiduelle en métal"): {
        "haut": "perte de métal vers les résidus — récupération insuffisante en amont",
    },
    ("D3", "Niveau du parc à résidus"): {
        "haut": "niveau élevé — risque de débordement, prévoir vidange ou rehaussement "
                "de digue",
    },
}


def decrire_risque(poste_id, parametre, valeur, borne_min, borne_max):
    """Phrase courte décrivant le risque opérationnel concret d'une valeur
    hors norme, pour affichage dans l'historique des relevés (remplace le
    simple « Non conforme »). À n'appeler que lorsque la valeur est hors
    barème (conforme = False)."""
    if borne_max is not None and valeur > borne_max:
        direction = "haut"
    elif borne_min is not None and valeur < borne_min:
        direction = "bas"
    else:
        direction = None

    texte = None
    if direction:
        texte = RISQUES.get((poste_id, parametre), {}).get(direction)

    if texte:
        return texte

    # Repli générique si aucun texte spécifique n'est défini pour ce
    # couple (poste, paramètre, direction).
    if direction == "haut":
        return f"valeur supérieure à la norme (≤ {borne_max:g}) — dérive du procédé à vérifier"
    if direction == "bas":
        return f"valeur inférieure à la norme (≥ {borne_min:g}) — dérive du procédé à vérifier"
    return "valeur hors du barème normal — dérive du procédé à vérifier"
