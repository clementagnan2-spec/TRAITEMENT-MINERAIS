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
]
