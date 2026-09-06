# -*- coding: utf-8 -*-
"""
Import de données d'exemple depuis un classeur Excel, et génération du
modèle (.xlsx) correspondant.

Le classeur comporte deux feuilles :
  - "Productions" : alimente la table productions (mouvements matière),
    comme dans l'onglet Production & bilan matière.
  - "Charges" : alimente la table charges_exploitation, comme dans
    l'onglet Coûts d'exploitation.

Chaque feuille a une ligne d'en-têtes suivie des données ; les listes
déroulantes (poste, type de flux, catégorie) sont ajoutées au modèle pour
limiter les erreurs de saisie.
"""

import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation

import db
from data_postes import POSTES_REF

POSTE_IDS = [p["id"] for p in POSTES_REF]
TYPES_FLUX = ["Alimentation", "Concentré", "Stérile / rejet", "Produit fini"]
CATEGORIES_CHARGE = ["Matière", "Énergie", "Réactifs", "Main-d'œuvre", "Maintenance", "Autre"]

ENTETES_PRODUCTIONS = ["Poste (code)", "Type de flux", "Masse (tonnes)", "Teneur (%)",
                        "Commentaire"]
ENTETES_CHARGES = ["Poste (code)", "Catégorie", "Montant (FCFA)", "Commentaire"]

EXEMPLES_PRODUCTIONS = [
    ["A2", "Alimentation", 1000, 1.20, "Exemple — alimentation broyage"],
    ["A2", "Concentré", 780, 3.10, "Exemple — concentré broyage"],
    ["B4", "Concentré", 120, 28.0, "Exemple — concentré flottation"],
]
EXEMPLES_CHARGES = [
    ["A2", "Matière", 10000000, "Exemple — minerai alimenté"],
    ["A2", "Énergie", 1500000, "Exemple — électricité broyeur"],
    ["A2", "Main-d'œuvre", 500000, "Exemple — équipe de poste"],
    ["A2", "Maintenance", 300000, "Exemple — pièces d'usure"],
]


def _ajouter_validation(ws, colonne_lettre, valeurs, nb_lignes):
    dv = DataValidation(
        type="list", formula1='"' + ",".join(valeurs) + '"', allow_blank=True
    )
    ws.add_data_validation(dv)
    dv.add(f"{colonne_lettre}2:{colonne_lettre}{nb_lignes}")


def generer_modele(chemin, nb_lignes_vides=30):
    """Crée le fichier .xlsx modèle (feuilles Productions et Charges,
    avec quelques lignes d'exemple déjà remplies) au chemin donné."""
    wb = openpyxl.Workbook()

    ws1 = wb.active
    ws1.title = "Productions"
    ws1.append(ENTETES_PRODUCTIONS)
    for ligne in EXEMPLES_PRODUCTIONS:
        ws1.append(ligne)
    total_lignes_1 = 1 + len(EXEMPLES_PRODUCTIONS) + nb_lignes_vides
    _ajouter_validation(ws1, "A", POSTE_IDS, total_lignes_1)
    _ajouter_validation(ws1, "B", TYPES_FLUX, total_lignes_1)
    for col, largeur in zip("ABCDE", (14, 16, 14, 10, 40)):
        ws1.column_dimensions[col].width = largeur

    ws2 = wb.create_sheet("Charges")
    ws2.append(ENTETES_CHARGES)
    for ligne in EXEMPLES_CHARGES:
        ws2.append(ligne)
    total_lignes_2 = 1 + len(EXEMPLES_CHARGES) + nb_lignes_vides
    _ajouter_validation(ws2, "A", POSTE_IDS, total_lignes_2)
    _ajouter_validation(ws2, "B", CATEGORIES_CHARGE, total_lignes_2)
    for col, largeur in zip("ABCD", (14, 16, 16, 40)):
        ws2.column_dimensions[col].width = largeur

    wb.save(chemin)


def importer_fichier(chemin, user_id):
    """Lit le classeur et insère les lignes valides en base. Retourne un
    résumé (nombre importé par feuille, liste des erreurs rencontrées)
    sans jamais lever d'exception pour une ligne individuellement
    invalide — ces lignes sont simplement signalées."""
    wb = openpyxl.load_workbook(chemin, data_only=True)
    resultat = {"productions_importees": 0, "charges_importees": 0, "erreurs": []}

    if "Productions" in wb.sheetnames:
        ws = wb["Productions"]
        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            poste_id, type_flux, masse, teneur, commentaire = (list(row) + [None] * 5)[:5]
            if poste_id is None and type_flux is None and masse is None:
                continue
            poste_id = str(poste_id).strip() if poste_id is not None else ""
            if poste_id not in POSTE_IDS:
                resultat["erreurs"].append(f"Productions, ligne {i} : poste « {poste_id} » "
                                            f"inconnu.")
                continue
            if type_flux not in TYPES_FLUX:
                resultat["erreurs"].append(f"Productions, ligne {i} : type de flux "
                                            f"« {type_flux} » invalide.")
                continue
            try:
                masse = float(masse)
            except (TypeError, ValueError):
                resultat["erreurs"].append(f"Productions, ligne {i} : masse invalide.")
                continue
            teneur_val = None
            if teneur not in (None, ""):
                try:
                    teneur_val = float(teneur)
                except (TypeError, ValueError):
                    resultat["erreurs"].append(f"Productions, ligne {i} : teneur invalide "
                                                f"(ignorée).")
            db.ajouter_production(poste_id, user_id, type_flux, masse, teneur_val,
                                   (commentaire or "").strip())
            resultat["productions_importees"] += 1

    if "Charges" in wb.sheetnames:
        ws = wb["Charges"]
        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            poste_id, categorie, montant, commentaire = (list(row) + [None] * 4)[:4]
            if poste_id is None and categorie is None and montant is None:
                continue
            poste_id = str(poste_id).strip() if poste_id is not None else ""
            if poste_id not in POSTE_IDS:
                resultat["erreurs"].append(f"Charges, ligne {i} : poste « {poste_id} » "
                                            f"inconnu.")
                continue
            if categorie not in CATEGORIES_CHARGE:
                resultat["erreurs"].append(f"Charges, ligne {i} : catégorie « {categorie} » "
                                            f"invalide.")
                continue
            try:
                montant = float(montant)
            except (TypeError, ValueError):
                resultat["erreurs"].append(f"Charges, ligne {i} : montant invalide.")
                continue
            db.ajouter_charge(poste_id, user_id, categorie, montant,
                               (commentaire or "").strip())
            resultat["charges_importees"] += 1

    return resultat
