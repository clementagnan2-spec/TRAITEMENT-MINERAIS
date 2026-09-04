# -*- coding: utf-8 -*-
"""
Données pédagogiques du logiciel : glossaire, quiz, checklist de diagnostic
et règles de sélection de méthode de concentration.
Contenu dérivé du programme de formation "Traitement des Minerais".
"""

GLOSSAIRE = [
    ("Minerai", "Matériau brut extrait de la mine, constitué du minéral valorisable "
                 "(la valeur) et de la gangue (minéraux sans valeur économique)."),
    ("Gangue", "Minéraux sans valeur économique associés au minéral valorisable dans le minerai."),
    ("Concentré", "Produit enrichi en minéral valorisable issu d'une opération de concentration."),
    ("Stérile / résidu", "Produit appauvri en minéral valorisable, rejeté en fin de traitement (tailings)."),
    ("Teneur", "Proportion de l'élément ou du minéral d'intérêt dans un flux "
               "(souvent en % ou en g/t pour les métaux précieux)."),
    ("Rendement massique (Y)", "Part de la masse d'alimentation retrouvée dans un produit donné "
                                "(souvent le concentré). Y = (f - t) / (c - t) x 100"),
    ("Récupération métallurgique (R)", "Part du métal contenu dans l'alimentation retrouvée dans un "
                                        "produit donné. R = Y x c / f"),
    ("Ratio d'enrichissement", "Rapport entre la teneur du concentré et celle de l'alimentation (c / f)."),
    ("Libération", "Degré de séparation physique du minéral valorisable et de la gangue "
                   "à une taille de particule donnée."),
    ("Maille de libération", "Taille en dessous de laquelle la majorité du minéral d'intérêt est libérée."),
    ("P80", "Taille de maille laissant passer 80 % de la masse d'un produit granulométrique."),
    ("d50c", "Taille de coupure à laquelle une particule a 50 % de chance de suivre l'overflow "
             "ou l'underflow d'un hydrocyclone. Caractérise l'efficacité de classification."),
    ("Charge circulante", "Rapport entre le débit renvoyé au broyeur et le débit d'alimentation "
                           "fraîche, en circuit fermé (%)."),
    ("Circuit ouvert", "Le produit du broyeur part directement en aval, sans recirculation."),
    ("Circuit fermé", "Le broyeur est associé à un classificateur (souvent hydrocyclone) : "
                       "le grossier (underflow) est renvoyé au broyeur."),
    ("Work Index de Bond (Wi)", "Indice de travail déterminé en laboratoire, référence pour "
                                 "dimensionner un broyeur industriel."),
    ("Séparation gravimétrique", "Exploite l'écart de densité entre minéraux (tables à secousses, "
                                  "jigs, spirales, concentrateurs centrifuges)."),
    ("Séparation magnétique LIMS", "Basse intensité : traite les minéraux fortement magnétiques "
                                    "(ferromagnétiques), ex. magnétite."),
    ("Séparation magnétique HIMS/WHIMS", "Haute intensité : nécessaire pour les minéraux faiblement "
                                          "magnétiques (paramagnétiques), ex. hématite, terres rares."),
    ("Séparation électrostatique", "Exploite les différences de conductivité électrique de surface "
                                    "(sables minéraux lourds : rutile, zircon, ilménite)."),
    ("Flottation", "Sépare les minéraux selon leur hydrophobicité de surface, via des bulles d'air "
                    "dans une pulpe agitée."),
    ("Collecteur", "Réactif qui rend la surface du minéral cible hydrophobe (ex. xanthates, amines)."),
    ("Moussant", "Réactif qui stabilise la mousse et contrôle la taille des bulles (ex. MIBC)."),
    ("Activant", "Favorise l'adsorption du collecteur sur un minéral peu réactif (ex. sulfate de cuivre)."),
    ("Déprimant", "Empêche la flottation d'un minéral indésirable (ex. chaux, cyanure)."),
    ("Rougher", "Étage principal de flottation, favorise la récupération."),
    ("Scavenger", "Retraite les rejets du rougher pour récupérer les dernières traces de minéral."),
    ("Cleaner", "Reflotte le concentré rougher pour en améliorer la teneur."),
    ("Épaississeur", "Concentre une pulpe diluée par décantation gravitaire, assistée de floculants."),
    ("Filtration", "Élimine l'eau résiduelle d'une pulpe épaissie pour produire un gâteau solide."),
    ("Locked-cycle test", "Essai de laboratoire simulant l'accumulation des recirculations "
                           "(eau, mixtes) d'un circuit industriel fermé."),
    ("Réconciliation de données", "Ajustement statistique des teneurs mesurées pour respecter la "
                                   "conservation de la masse (souvent par moindres carrés pondérés)."),
    ("Plan d'expériences (DOE)", "Structure l'exploration de plusieurs facteurs simultanément "
                                  "(pH, dosage, granulométrie) en un nombre limité d'essais."),
]

# Checklist de diagnostic d'une baisse de récupération en flottation (Module 4 / Exercice 4),
# du plus en amont vers le plus en aval.
DIAGNOSTIC_FLOTTATION = [
    ("1. Alimentation",
     "La teneur du minerai a-t-elle chuté ? Y a-t-il un changement de zone d'extraction "
     "impliquant une minéralogie différente (oxydation, minéraux secondaires moins flottables) ?"),
    ("2. Granulométrie (P80 broyage)",
     "Une dérive du circuit de broyage (usure de corps broyants, dérive du cyclone) peut "
     "désajuster la maille de libération réellement obtenue."),
    ("3. Dosage réel des réactifs",
     "Contrôler le débit effectif des pompes doseuses (usure, bouchage), la concentration "
     "des solutions préparées, un éventuel changement de lot ou de fournisseur."),
    ("4. pH mesuré vs pH cible",
     "Un capteur dérivé ou une consommation de chaux imprévue peut sortir le circuit de sa "
     "fenêtre de sélectivité optimale."),
    ("5. Paramètres mécaniques",
     "Débit d'air réellement délivré, niveaux de pulpe, usure des rotors/stators, temps de "
     "résidence effectif (débit d'alimentation en hausse ?)."),
    ("6. Qualité de l'eau recyclée",
     "Accumulation d'ions ou de réactifs résiduels pouvant déprimer involontairement le "
     "minéral cible."),
]

# Règles simplifiées de sélection de méthode de concentration (Module 3),
# utilisées par l'assistant de sélection.
def suggerer_methode(densite_elevee, magnetique, conducteur, mouillabilite_exploitable, taille_fine):
    """
    Retourne (méthode suggérée, justification) à partir de propriétés physiques
    du minéral cible, sur le modèle du raisonnement du Module 3 / Exercice 3.
    """
    if magnetique:
        return ("Séparation magnétique (LIMS si fortement magnétique, HIMS/WHIMS si faiblement "
                 "magnétique)",
                "Le minéral présente une susceptibilité magnétique exploitable : c'est le "
                "critère le plus direct et le moins coûteux à mettre en œuvre.")
    if conducteur:
        return ("Séparation électrostatique",
                "Le minéral se distingue par sa conductivité électrique de surface, typique "
                "des sables minéraux lourds (rutile, zircon, ilménite).")
    if taille_fine and mouillabilite_exploitable:
        return ("Flottation",
                "La finesse de la dissémination impose un broyage fin ; seule la flottation, "
                "par son mécanisme de surface, reste efficace sur des particules très fines.")
    if densite_elevee:
        return ("Séparation gravimétrique (tables, spirales, jigs ou concentrateurs centrifuges)",
                "Un écart de densité important entre le minéral et la gangue rend la "
                "gravimétrie pertinente : coût opératoire faible, pas de réactifs.")
    if mouillabilite_exploitable:
        return ("Flottation",
                "En l'absence de propriété physique distinctive exploitable simplement "
                "(densité, magnétisme, conductivité), la flottation, via la chimie de "
                "surface, reste la méthode la plus universelle.")
    return ("Caractérisation complémentaire nécessaire",
            "Aucune propriété distinctive nette n'a été indiquée : il faut approfondir la "
            "caractérisation minéralogique (Module 1) avant de choisir une méthode.")


QUIZ = [
    {
        "question": "Quelle formule permet de calculer le rendement massique vers le concentré ?",
        "choices": [
            "Y = (f - t) / (c - t) x 100",
            "Y = (c - f) / (c - t) x 100",
            "Y = f / c x 100",
            "Y = (c + t) / f x 100",
        ],
        "correct": 0,
        "explication": "Y (%) = (f - t) / (c - t) x 100, où f, c, t sont les teneurs de "
                        "l'alimentation, du concentré et du stérile.",
    },
    {
        "question": "Pourquoi un P80 de broyage supérieur à la maille de libération plafonne-t-il "
                     "la récupération atteignable ?",
        "choices": [
            "Parce que le broyeur consomme trop d'énergie",
            "Parce qu'une partie du minéral reste en particules mixtes non libérées, "
            "non triables en aval",
            "Parce que la pulpe devient trop diluée",
            "Parce que le pH devient instable",
        ],
        "correct": 1,
        "explication": "Si la taille des particules reste au-dessus de la maille de libération, "
                        "des particules mixtes (minéral + gangue) subsistent et aucune méthode "
                        "de concentration en aval ne peut les trier correctement.",
    },
    {
        "question": "Quel est le rôle d'un collecteur en flottation ?",
        "choices": [
            "Stabiliser la mousse",
            "Rendre la surface du minéral cible hydrophobe",
            "Faire baisser le pH",
            "Empêcher la flottation d'un minéral indésirable",
        ],
        "correct": 1,
        "explication": "Le collecteur modifie sélectivement la mouillabilité de surface du "
                        "minéral cible pour le rendre hydrophobe et donc flottable.",
    },
    {
        "question": "Dans un circuit rougher-scavenger-cleaner, quel est le rôle du scavenger ?",
        "choices": [
            "Améliorer la teneur du concentré",
            "Retraiter les rejets du rougher pour récupérer les dernières traces de minéral",
            "Réaliser l'étape principale de flottation",
            "Contrôler le pH du circuit",
        ],
        "correct": 1,
        "explication": "Le scavenger retraite les rejets (queues) du rougher pour maximiser la "
                        "récupération, quitte à perdre en teneur.",
    },
    {
        "question": "Pourquoi réalise-t-on un essai locked-cycle avant de passer à l'échelle "
                     "pilote ?",
        "choices": [
            "Pour économiser du minerai",
            "Pour simuler l'effet de l'accumulation des eaux recyclées et charges "
            "circulantes d'un circuit fermé industriel",
            "Pour tester uniquement la couleur du concentré",
            "Parce que c'est obligatoire réglementairement",
        ],
        "correct": 1,
        "explication": "Un essai batch simple ne reproduit pas l'effet de l'accumulation des "
                        "recirculations ; le locked-cycle réintroduit les flux de recirculation "
                        "sur plusieurs cycles pour atteindre un état stabilisé représentatif.",
    },
    {
        "question": "Quelle méthode de concentration convient le mieux à la magnétite "
                     "(fortement ferromagnétique) ?",
        "choices": [
            "Séparation électrostatique",
            "Flottation",
            "Séparation magnétique basse intensité (LIMS)",
            "Séparation magnétique haute intensité (HIMS)",
        ],
        "correct": 2,
        "explication": "La magnétite étant fortement ferromagnétique, la LIMS suffit : "
                        "simple, robuste et peu coûteuse en réactifs.",
    },
    {
        "question": "Que mesure le d50c d'un hydrocyclone ?",
        "choices": [
            "La densité de la pulpe",
            "La taille de coupure à laquelle une particule a 50 % de chance de suivre "
            "l'overflow ou l'underflow",
            "Le débit d'air injecté",
            "Le pH optimal de séparation",
        ],
        "correct": 1,
        "explication": "Le d50c caractérise l'efficacité de classification d'un hydrocyclone.",
    },
]
