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
