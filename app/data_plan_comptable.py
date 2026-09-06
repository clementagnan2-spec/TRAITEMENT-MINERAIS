# -*- coding: utf-8 -*-
"""
Correspondance avec le plan comptable SYSCOHADA (système comptable OHADA),
utilisée pour affecter automatiquement un compte à chaque charge saisie et
pour valoriser le mouvement de stock/en-cours généré par chaque centre de
coût.

Le SYSCOHADA fixe les comptes principaux (2 à 3 chiffres, ex. 601, 602,
604, 61, 62, 66, 31 à 39...) ; les subdivisions plus fines (4e chiffre et
au-delà) sont laissées libres à chaque entité — c'est le cas des
subdivisions utilisées ci-dessous. Adaptez-les si votre entité utilise
déjà une nomenclature de comptes différente.
"""

# Classe 6 — comptes de charges par catégorie de charge d'exploitation
COMPTES_CHARGES = {
    "Matière": {
        "numero": "6021",
        "libelle": "Achats de matières premières et fournitures liées",
    },
    "Réactifs": {
        "numero": "6041",
        "libelle": "Achats stockés de matières et fournitures consommables — réactifs",
    },
    "Énergie": {
        "numero": "6042",
        "libelle": "Achats stockés de matières et fournitures consommables — combustibles/énergie",
    },
    "Main-d'œuvre": {
        "numero": "6611",
        "libelle": "Rémunérations directes versées au personnel national",
    },
    "Maintenance": {
        "numero": "6243",
        "libelle": "Entretiens, réparations et maintenance",
    },
    "Autre": {
        "numero": "6288",
        "libelle": "Autres charges externes diverses",
    },
}

COMPTE_CHARGE_DEFAUT = {"numero": "628", "libelle": "Autres services extérieurs"}

# Classe 3 — comptes de stocks / en-cours de production, selon le libellé
# du "stock_sortie" défini dans data_centres_cout.py pour chaque centre de
# coût (31/32 approvisionnements, 33 en-cours de production de biens,
# 35 stocks de produits).
COMPTES_STOCKS = {
    "ROM": {"numero": "321", "libelle": "Autres approvisionnements — Minerai ROM"},
    "ROM disponible": {"numero": "321", "libelle": "Autres approvisionnements — Minerai ROM"},
    "Concassé": {"numero": "331", "libelle": "En-cours de production — Minerai concassé"},
    "Broyé": {"numero": "332", "libelle": "En-cours de production — Minerai broyé"},
    "Concentré": {"numero": "333", "libelle": "En-cours de production — Concentré"},
    "Concentré/Rejets": {
        "numero": "333", "libelle": "En-cours de production — Concentré / rejets"
    },
    "Solution": {"numero": "334", "libelle": "En-cours de production — Solution"},
    "Solution riche": {"numero": "334", "libelle": "En-cours de production — Solution riche"},
    "Pulpe": {"numero": "332", "libelle": "En-cours de production — Pulpe"},
    "Produit intermédiaire": {
        "numero": "335", "libelle": "En-cours de production — Produit intermédiaire"
    },
    "Produit fini": {"numero": "351", "libelle": "Stocks de produits finis"},
    "Minerai": {"numero": "321", "libelle": "Autres approvisionnements — Minerai"},
}

COMPTE_STOCK_DEFAUT = {"numero": "33", "libelle": "En-cours de production de biens"}

# Compte de contrepartie crédité lors de la valorisation en stock du coût
# de production de la période (transfert de charges vers le bilan).
COMPTE_CONTREPARTIE_STOCK = {
    "numero": "736",
    "libelle": "Variation des stocks de biens et de services produits",
}


def compte_charge(categorie):
    return COMPTES_CHARGES.get(categorie, COMPTE_CHARGE_DEFAUT)


def compte_stock(libelle_stock):
    return COMPTES_STOCKS.get(libelle_stock, COMPTE_STOCK_DEFAUT)
