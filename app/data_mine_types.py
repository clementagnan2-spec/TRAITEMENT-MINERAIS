# -*- coding: utf-8 -*-
"""
Profils de type de mine : chaque profil définit quels postes/circuits
(parmi ceux de data_postes.POSTES_REF) sont pertinents pour ce type
d'exploitation. Choisir un type de mine dans l'onglet Administration
filtre automatiquement tous les formulaires de saisie (relevés,
productions, incidents, équipes, LOTO) pour ne montrer que les circuits
correspondants.

Librement adaptable : ajoutez ou modifiez des profils ici selon vos
besoins. Un profil est juste une liste d'identifiants de postes tirés de
data_postes.POSTES_REF — aucun poste n'est supprimé de la base de
données en changeant de profil, seul l'affichage est filtré.
"""

from data_postes import POSTES_REF

TOUS_LES_IDS = [p["id"] for p in POSTES_REF]

DEFAUT = "Générique / tous les circuits"

MINE_TYPES = {
    DEFAUT: {
        "description": "Affiche l'ensemble des circuits définis. Utile pour un site "
                        "polymétallique, un usage de formation, ou tant que le type de "
                        "mine n'a pas encore été choisi.",
        "postes": list(TOUS_LES_IDS),
    },
    "Or — sulfureux (flottation + CIL/CIP)": {
        "description": "Minerai d'or associé à des sulfures (pyrite, arsénopyrite...), "
                        "nécessitant flottation puis cyanuration du concentré (CIL/CIP).",
        "postes": ["A0", "A1", "A2", "B4", "C4", "D1", "D2"],
    },
    "Or — oxydé (lixiviation en tas)": {
        "description": "Minerai d'or oxydé, traitable par cyanuration directe en tas "
                        "(heap leaching), sans étape de concentration physique préalable.",
        "postes": ["A0", "A1", "C1", "D1", "D2"],
    },
    "Cuivre — sulfuré (flottation, concentré vendu en fonderie)": {
        "description": "Minerai de cuivre sulfuré (chalcopyrite...), concentré par "
                        "flottation puis expédié en fonderie externe (pas d'hydrométallurgie "
                        "sur site).",
        "postes": ["A0", "A1", "A2", "B4", "D1", "D2"],
    },
    "Cuivre — oxydé (lixiviation + SX-EW)": {
        "description": "Minerai de cuivre oxydé, traité par lixiviation en tas puis "
                        "extraction par solvant/électrolyse (SX-EW). Remarque : l'étape "
                        "SX-EW elle-même n'est pas encore modélisée comme poste distinct "
                        "dans ce logiciel — seule la lixiviation en tas amont l'est.",
        "postes": ["A0", "A1", "C1", "D1", "D2"],
    },
    "Fer (magnétique / gravimétrique)": {
        "description": "Minerai de fer (magnétite, hématite), concentré par séparation "
                        "magnétique et/ou gravimétrique, sans hydrométallurgie.",
        "postes": ["A0", "A1", "A2", "B2", "B3", "D1"],
    },
    "Nickel latéritique (HPAL)": {
        "description": "Minerai de nickel latéritique, traité par lixiviation sous "
                        "pression (HPAL) puis en cuve.",
        "postes": ["A0", "A1", "C2", "C3", "D1", "D2"],
    },
    "Minéraux lourds / sables minéraux (gravimétrique)": {
        "description": "Sables minéraux (ilménite, rutile, zircon...), concentrés "
                        "principalement par gravimétrie. Remarque : la séparation "
                        "électrostatique, souvent utilisée en complément pour ce type de "
                        "minerai, n'est pas encore modélisée comme poste distinct.",
        "postes": ["A0", "A1", "B3", "D1"],
    },
}


def liste_types_mine():
    """Retourne la liste des noms de profils disponibles, profil générique en premier."""
    autres = sorted(k for k in MINE_TYPES if k != DEFAUT)
    return [DEFAUT] + autres


def postes_pour_type(type_mine):
    """Retourne la sous-liste de POSTES_REF pertinente pour le type de mine donné,
    dans l'ordre d'origine. Si le type de mine est inconnu ou vide, retourne tous
    les postes (comportement de repli sûr : ne masque jamais un poste par erreur)."""
    profil = MINE_TYPES.get(type_mine)
    ids_actifs = set(profil["postes"]) if profil else set(TOUS_LES_IDS)
    return [p for p in POSTES_REF if p["id"] in ids_actifs]
