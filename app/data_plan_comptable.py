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
    "Amortissement": {
        "numero": "6813",
        "libelle": "Dotations aux amortissements des immobilisations corporelles — matériel de production",
    },
    "Autre": {
        "numero": "6288",
        "libelle": "Autres charges externes diverses",
    },
}

COMPTE_CHARGE_DEFAUT = {"numero": "628", "libelle": "Autres services extérieurs"}

# Classe 3 — comptes de stocks / en-cours de production, selon le libellé
# du "stock_sortie" défini dans data_centres_cout.py pour chaque centre de
# coût. Racines SYSCOHADA (à ne pas confondre avec le PCG français, qui
# numérote différemment) :
#   31 Marchandises · 32 Matières premières et fournitures liées ·
#   33 Autres approvisionnements · 34 Produits en cours · 35 Services en
#   cours · 36 Produits finis · 37 Produits intermédiaires et résiduels.
COMPTES_STOCKS = {
    "ROM": {"numero": "321", "libelle": "Matières premières et fournitures liées — Minerai ROM"},
    "ROM disponible": {
        "numero": "321", "libelle": "Matières premières et fournitures liées — Minerai ROM"
    },
    "Minerai": {"numero": "321", "libelle": "Matières premières et fournitures liées — Minerai"},
    "Concassé": {"numero": "341", "libelle": "Produits en cours — Minerai concassé"},
    "Broyé": {"numero": "342", "libelle": "Produits en cours — Minerai broyé"},
    "Pulpe": {"numero": "343", "libelle": "Produits en cours — Pulpe"},
    "Concentré": {"numero": "371", "libelle": "Produits intermédiaires — Concentré"},
    "Concentré/Rejets": {
        "numero": "372", "libelle": "Produits intermédiaires et résiduels — Concentré/rejets"
    },
    "Solution": {"numero": "373", "libelle": "Produits intermédiaires — Solution"},
    "Solution riche": {"numero": "374", "libelle": "Produits intermédiaires — Solution riche"},
    "Produit intermédiaire": {
        "numero": "375", "libelle": "Produits intermédiaires — Produit intermédiaire"
    },
    "Produit fini": {"numero": "361", "libelle": "Produits finis"},
    "Métal raffiné": {"numero": "362", "libelle": "Produits finis — Métal raffiné"},
    "Rejets stockés (tailings)": {
        "numero": "377", "libelle": "Produits intermédiaires et résiduels — Rejets (tailings)"
    },
}

COMPTE_STOCK_DEFAUT = {"numero": "34", "libelle": "Produits en cours"}

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
