# -*- coding: utf-8 -*-
"""
Référentiel des centres de coût — un centre de coût par poste/processus de
data_postes.py, utilisé pour :
  - amorcer la table centres_cout en base au premier lancement
  - afficher la table de référence (code, compte de charge, stock
    entrée/sortie, méthode de valorisation) dans l'onglet Coûts d'exploitation
  - déterminer, par défaut, quel type de flux (voir TYPES_FLUX dans
    ui_productions.py) sert de dénominateur au calcul du coût unitaire à la
    tonne pour ce poste

Librement adaptable : ce référentiel doit rester cohérent avec
data_postes.py (un centre de coût par poste_id qui y existe). Un poste
ajouté dans data_postes.py sans entrée correspondante ici reste utilisable
pour les relevés/productions, mais n'apparaîtra pas dans le calcul de coût
tant qu'un centre de coût ne lui est pas associé.
"""

CENTRES_COUT_REF = [
    {"poste_id": "A0", "code_centre": "CC-A0", "compte_charge": "Charges minières",
     "stock_entree": "ROM", "stock_sortie": "ROM disponible",
     "methode_cout": "FIFO/CMUP", "flux_sortie_defaut": "Alimentation"},
    {"poste_id": "A1", "code_centre": "CC-A1", "compte_charge": "Charges concassage",
     "stock_entree": "ROM", "stock_sortie": "Concassé",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Alimentation"},
    {"poste_id": "A2", "code_centre": "CC-A2", "compte_charge": "Charges broyage",
     "stock_entree": "Concassé", "stock_sortie": "Broyé",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Alimentation"},
    {"poste_id": "B2", "code_centre": "CC-B2", "compte_charge": "Charges procédé",
     "stock_entree": "Broyé", "stock_sortie": "Concentré",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Concentré"},
    {"poste_id": "B3", "code_centre": "CC-B3", "compte_charge": "Charges procédé",
     "stock_entree": "Broyé", "stock_sortie": "Concentré",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Concentré"},
    {"poste_id": "B4", "code_centre": "CC-B4", "compte_charge": "Charges flottation",
     "stock_entree": "Broyé", "stock_sortie": "Concentré/Rejets",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Concentré"},
    {"poste_id": "C1", "code_centre": "CC-C1", "compte_charge": "Charges lixiviation",
     "stock_entree": "Minerai", "stock_sortie": "Solution",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Concentré"},
    {"poste_id": "C2", "code_centre": "CC-C2", "compte_charge": "Charges lixiviation",
     "stock_entree": "Minerai", "stock_sortie": "Solution",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Concentré"},
    {"poste_id": "C3", "code_centre": "CC-C3", "compte_charge": "Charges lixiviation",
     "stock_entree": "Minerai", "stock_sortie": "Solution",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Concentré"},
    {"poste_id": "C4", "code_centre": "CC-C4", "compte_charge": "Charges CIL/CIP",
     "stock_entree": "Pulpe", "stock_sortie": "Solution riche",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Concentré"},
    {"poste_id": "D1", "code_centre": "CC-D1", "compte_charge": "Charges de finition",
     "stock_entree": "Produit intermédiaire", "stock_sortie": "Produit fini",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Produit fini"},
    {"poste_id": "D2", "code_centre": "CC-D2", "compte_charge": "Charges de raffinage",
     "stock_entree": "Produit fini", "stock_sortie": "Métal raffiné",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Produit fini"},
    {"poste_id": "D3", "code_centre": "CC-D3", "compte_charge": "Charges de gestion des rejets",
     "stock_entree": "Concentré/Rejets", "stock_sortie": "Rejets stockés (tailings)",
     "methode_cout": "CMUP", "flux_sortie_defaut": "Stérile / rejet"},
]
