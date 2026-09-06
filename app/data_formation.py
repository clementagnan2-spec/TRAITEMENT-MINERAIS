# -*- coding: utf-8 -*-
"""
Données pédagogiques du logiciel : glossaire, quiz, checklist de diagnostic,
règles de sélection de méthode de concentration, fiches de poste et sécurité.

Contenu dérivé de deux programmes de formation :
  1. "Traitement des Minerais — De la caractérisation du gisement au
     flowsheet industriel" (formation de cadrage)
  2. "Programme de Formation Opérationnelle — Métiers de l'Usine de
     Traitement" (formation opérationnelle, par poste et par circuit)
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

    # --- Termes issus du programme opérationnel (postes, HSE, hydrométallurgie) ---
    ("Consignation (LOTO)", "Lock-Out / Tag-Out : procédure obligatoire de mise hors énergie "
                             "et de verrouillage d'un équipement avant toute intervention, "
                             "quelle que soit l'urgence perçue."),
    ("EPI", "Équipement de Protection Individuelle : casque, protections auditives et "
            "oculaires, gants, chaussures de sécurité, protection respiratoire selon le poste."),
    ("FDS", "Fiche de Données de Sécurité : document décrivant les dangers et précautions "
            "d'usage de chaque réactif chimique manipulé sur le poste."),
    ("Lixiviation en tas (heap leaching)", "Le minerai concassé est empilé sur une aire "
                                            "étanche et arrosé en continu d'une solution "
                                            "lixiviante (souvent cyanurée pour l'or) qui "
                                            "percole et dissout le métal."),
    ("Lixiviation sous pression (autoclave)", "Lixiviation accélérée en travaillant à "
                                               "température et pression supérieures aux "
                                               "conditions atmosphériques, utile pour les "
                                               "minerais réfractaires."),
    ("Lixiviation en cuve (tank leaching)", "Lixiviation en série de cuves agitées, avec "
                                             "dosage du réactif lixiviant et de l'agent "
                                             "oxydant, suivi de pH et d'ORP."),
    ("ORP", "Potentiel d'oxydoréduction (Oxidation-Reduction Potential) : indicateur suivi "
            "en lixiviation en cuve pour contrôler les conditions d'oxydation."),
    ("CIL (Carbon-in-Leach)", "Procédé où l'adsorption du métal dissous sur charbon actif a "
                               "lieu simultanément à la lixiviation, dans les mêmes cuves."),
    ("CIP (Carbon-in-Pulp)", "Procédé où l'adsorption du métal dissous sur charbon actif a "
                              "lieu après la lixiviation, dans une série de cuves dédiées."),
    ("Contre-courant (CIL/CIP)", "Principe de circulation où le charbon actif est transféré "
                                  "en sens inverse du flux de pulpe : le charbon le plus frais "
                                  "rencontre la solution la plus appauvrie, et le charbon le "
                                  "plus chargé rencontre la solution la plus riche."),
    ("Élution", "Étape qui extrait le métal adsorbé sur le charbon actif chargé, en aval du "
                "circuit CIL/CIP, avant régénération du charbon."),
    ("Criblage de rétention", "Grille placée dans chaque cuve CIL/CIP qui retient le charbon "
                               "actif tout en laissant passer la pulpe."),
    ("Ronde de contrôle", "Tournée d'inspection visuelle et instrumentale effectuée par "
                           "l'opérateur avant ou pendant le poste, pour détecter toute "
                           "anomalie naissante."),
    ("Carnet de bord / main courante", "Registre de poste où l'opérateur consigne les "
                                        "relevés, incidents et consignes transmises en relève."),
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
        "categorie": "Formation de cadrage",
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
        "categorie": "Formation de cadrage",
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
        "categorie": "Formation de cadrage",
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
        "categorie": "Formation de cadrage",
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
        "categorie": "Formation de cadrage",
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
        "categorie": "Formation de cadrage",
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
        "categorie": "Formation de cadrage",
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

# ========================================================================
# CONTENU OPÉRATIONNEL — issu du "Programme de Formation Opérationnelle,
# Métiers de l'Usine de Traitement"
# ========================================================================

# Fiches de poste / circuit : contrôles de routine, paramètres à
# surveiller, anomalies fréquentes, missions et compétences visées.
# Chaque fiche est un dict ; les champs absents sont simplement None.
POSTES = [
    {
        "partie": "A — Fragmentation",
        "id": "A1",
        "titre": "Circuit de concassage",
        "description": "Réduit le tout-venant extrait de la mine à une granulométrie "
                        "compatible avec l'alimentation du broyage (généralement < 15–20 mm "
                        "en sortie de concassage tertiaire).",
        "controles": [
            "Alimentation régulière (pas de sur-remplissage ni de manque)",
            "Niveau des trémies tampon",
            "État des toiles de crible",
            "Absence de blocage (voûte, bourrage)",
        ],
        "parametres": [
            "Intensité électrique des moteurs (indicateur indirect de charge)",
            "Débit d'alimentation",
            "Granulométrie de sortie (contrôle visuel ou tamis de contrôle)",
        ],
        "anomalies": [
            ("Présence de corps étrangers (métal, bois)", "Déclenche les détecteurs ; "
             "arrêter et retirer selon procédure."),
            ("Bourrage", "Souvent dû à un minerai humide ou argileux ; dégager uniquement "
             "après consignation complète."),
            ("Usure anormale des blindages", "Signaler à la maintenance pour suivi."),
        ],
        "securite": [
            "Consignation obligatoire avant toute intervention sur un concasseur à l'arrêt.",
            "Interdiction de dégager un bourrage manuellement sans consignation complète.",
            "Port des EPI : casque, protections auditives, lunettes, chaussures de sécurité.",
            "Vigilance particulière aux zones de happement (convoyeurs, poulies).",
        ],
    },
    {
        "partie": "A — Fragmentation",
        "id": "A2",
        "titre": "Circuit de broyage",
        "description": "Affine la granulométrie du minerai jusqu'à la maille visée pour la "
                        "libération du minéral d'intérêt.",
        "controles": None,
        "parametres": [
            "Pourcentage de solides de la pulpe",
            "Débit d'alimentation",
            "Niveau de charge du broyeur",
            "Pression et débit au cyclone de classification",
            "Granulométrie de l'overflow (contrôle périodique)",
        ],
        "anomalies": [
            ("Surcharge du broyeur", "Bruit étouffé, hausse d'intensité : réduire le débit "
             "d'alimentation et/ou augmenter le débit d'eau d'appoint."),
            ("Sous-charge", "Bruit métallique fort : augmenter l'alimentation."),
            ("Dérive de coupure du cyclone", "Usure du spigot/vortex : contrôler et "
             "planifier le remplacement."),
        ],
        "securite": [
            "Aucune intervention sur trappes ou portes d'inspection sans consignation.",
            "Attention aux projections de pulpe lors des purges et des contrôles d'échantillon.",
            "Respect strict des procédures de rechargement en corps broyants (charge, "
            "manutention).",
        ],
    },
    {
        "partie": "A — Fragmentation",
        "id": "A3",
        "titre": "Métier — Opérateur concasseur",
        "description": "Responsable de la conduite quotidienne du circuit de concassage : "
                        "démarrage/arrêt selon procédure, surveillance continue des "
                        "paramètres, premier niveau de diagnostic, alerte maintenance.",
        "missions": [
            "Ronde de contrôle avant démarrage",
            "Conduite en poste",
            "Tenue du carnet de bord (relevés, incidents)",
            "Nettoyage et rangement de la zone concasseur",
        ],
        "competences": [
            "Lecture des indicateurs de salle de contrôle ou du tableau local",
            "Reconnaissance des bruits et vibrations anormaux",
            "Application des consignes de consignation",
        ],
    },
    {
        "partie": "A — Fragmentation",
        "id": "A4",
        "titre": "Métier — Opérateur broyeur",
        "description": "Assure la conduite du circuit broyeur–cyclone : ajustement des "
                        "débits d'eau, suivi du pourcentage de solides, gestion du "
                        "rechargement en corps broyants, remontée d'alerte.",
        "missions": [
            "Relevés d'instrumentation",
            "Prélèvements d'échantillons pour contrôle granulométrique",
            "Ajustement fin des débits selon consignes",
            "Participation au rechargement en boulets",
        ],
        "competences": [
            "Interprétation des tendances d'intensité électrique et de pression cyclone",
            "Communication avec le laboratoire pour le suivi du P80",
        ],
    },
    {
        "partie": "B — Concentration",
        "id": "B1",
        "titre": "Circuit de concentration (vue d'ensemble)",
        "description": "Regroupe les opérations qui exploitent une propriété physique "
                        "(densité, magnétisme) ou physico-chimique (mouillabilité de "
                        "surface) du minéral pour le séparer de la gangue.",
        "controles": None, "parametres": None, "anomalies": None, "securite": None,
    },
    {
        "partie": "B — Concentration",
        "id": "B2",
        "titre": "Récupération magnétique",
        "description": None,
        "controles": [
            "Alimentation régulière et homogène du séparateur",
            "Propreté des tambours/matrices",
            "Intégrité de l'aimantation (selon technologie)",
        ],
        "parametres": [
            "Débit d'alimentation",
            "Intensité du champ (si réglable)",
            "Qualité visuelle de la séparation (produit magnétique vs non magnétique)",
        ],
        "anomalies": [
            ("Colmatage par des fines", "Nettoyer selon procédure et vérifier la cause "
             "amont (granulométrie)."),
            ("Perte de champ (usure)", "Signaler à la maintenance."),
            ("Mauvaise répartition de l'alimentation", "Ajuster la distribution sur la "
             "largeur du tambour."),
        ],
    },
    {
        "partie": "B — Concentration",
        "id": "B3",
        "titre": "Récupération gravimétrique",
        "description": None,
        "controles": [
            "Niveau et régularité de l'alimentation en pulpe",
            "Réglage de l'inclinaison/amplitude (tables)",
            "Débit d'eau de lavage",
        ],
        "parametres": [
            "Pourcentage de solides d'alimentation",
            "Aspect visuel des bandes de séparation",
            "Fréquence de purge du concentré (concentrateurs centrifuges)",
        ],
        "anomalies": [
            ("Engorgement par des fines en excès", "Vérifier la granulométrie amont."),
            ("Déréglage de l'inclinaison", "Recaler selon consigne."),
            ("Usure des rifles ou de la toile de table", "Planifier le remplacement."),
        ],
    },
    {
        "partie": "B — Concentration",
        "id": "B4",
        "titre": "Flottation (conduite de poste)",
        "description": None,
        "controles": [
            "Niveaux de pulpe dans chaque cellule",
            "Aspect et vitesse de la mousse",
            "Dosage effectif des réactifs (vérification pompes doseuses)",
        ],
        "parametres": [
            "pH de la pulpe",
            "Débit d'air",
            "Pourcentage de solides",
            "Aspect de la mousse (couleur, charge, vitesse de raclage)",
        ],
        "anomalies": [
            ("Mousse trop sèche ou trop chargée", "Sur/sous-dosage moussant : ajuster le "
             "dosage."),
            ("pH hors cible", "Vérifier le dosage de chaux et l'étalonnage du capteur."),
            ("Dérive de couleur de mousse", "Peut signaler un changement minéralogique de "
             "l'alimentation ; alerter le laboratoire."),
        ],
        "securite": [
            "Manipulation des réactifs chimiques selon fiches de données de sécurité (FDS).",
            "Port des EPI adaptés (gants, lunettes, protection respiratoire selon réactif).",
            "Ventilation et douches de sécurité à proximité des zones de conditionnement "
            "réactifs.",
        ],
    },
    {
        "partie": "C — Hydrométallurgie",
        "id": "C1",
        "titre": "Lixiviation en tas (heap leaching)",
        "description": "Le minerai concassé est empilé sur une aire étanche et arrosé en "
                        "continu d'une solution lixiviante (souvent cyanurée pour l'or), qui "
                        "percole à travers le tas et dissout le métal.",
        "controles": [
            "Débit et répartition homogène de l'arrosage",
            "Intégrité de la géomembrane",
            "Niveau des bassins (solution riche / solution pauvre)",
        ],
        "parametres": [
            "Concentration en réactif lixiviant",
            "pH de la solution",
            "Teneur en métal de la solution riche (suivi de rendement)",
        ],
        "anomalies": None,
        "securite": [
            "Manipulation stricte des solutions cyanurées : EPI complets, procédure "
            "d'urgence en cas de contact.",
            "Contrôle régulier de l'étanchéité des bassins et de la géomembrane.",
            "Interdiction d'accès non autorisé aux zones d'arrosage et de bassins.",
        ],
    },
    {
        "partie": "C — Hydrométallurgie",
        "id": "C2",
        "titre": "Lixiviation sous pression (autoclave)",
        "description": "Accélère la dissolution en travaillant à température et pression "
                        "supérieures aux conditions atmosphériques ; utile pour des minerais "
                        "réfractaires mal traités par lixiviation classique.",
        "controles": [
            "Pression et température de consigne",
            "Étanchéité des joints",
            "Purges de sécurité",
        ],
        "parametres": [
            "Pression interne",
            "Température",
            "Débit d'alimentation en pulpe et en réactif oxydant",
        ],
        "anomalies": None,
        "securite": [
            "Équipement sous pression : consignes strictes de démarrage/arrêt et de purge.",
            "Formation spécifique obligatoire avant toute conduite d'autoclave.",
            "Surveillance renforcée des soupapes de sécurité et systèmes d'arrêt d'urgence.",
        ],
    },
    {
        "partie": "C — Hydrométallurgie",
        "id": "C3",
        "titre": "Lixiviation en cuve (tank leaching)",
        "description": None,
        "controles": [
            "Niveau et agitation de chaque cuve",
            "Dosage du réactif lixiviant et de l'agent oxydant",
            "Aération si nécessaire",
        ],
        "parametres": [
            "pH",
            "Potentiel d'oxydoréduction (ORP)",
            "Concentration résiduelle en réactif libre",
            "Temps de séjour",
        ],
        "anomalies": [
            ("Sous-dosage en réactif", "Rendement en baisse : vérifier le dosage réel."),
            ("Agitation insuffisante", "Décantation prématurée : vérifier l'agitateur."),
            ("Consommation anormale de réactif", "Minerai plus consommateur que prévu : "
             "alerter le laboratoire."),
        ],
    },
    {
        "partie": "C — Hydrométallurgie",
        "id": "C4",
        "titre": "Adsorption — Opérateur CIL/CIP",
        "description": "Les procédés CIL (Carbon-in-Leach) et CIP (Carbon-in-Pulp) captent "
                        "le métal dissous par adsorption sur charbon actif, circulant à "
                        "contre-courant du flux de pulpe entre une série de cuves.",
        "missions": [
            "Transfert du charbon entre cuves (contre-courant)",
            "Criblage du charbon (rétention dans les cuves, passage de la pulpe)",
            "Suivi de la charge en métal du charbon",
        ],
        "parametres": [
            "Concentration en charbon par cuve",
            "Teneur en métal en solution en entrée et sortie de chaque cuve",
            "État des cribles de rétention (colmatage, usure)",
        ],
        "anomalies": [
            ("Perte de charbon", "Crible percé : arrêter et réparer."),
            ("Baisse de rendement d'adsorption", "Charbon saturé, à régénérer ou "
             "renouveler."),
            ("Mauvaise circulation contre-courant", "Vérifier les transferts entre cuves."),
        ],
        "securite": [
            "Manipulation du charbon actif chargé en cyanure : EPI complets.",
            "Procédures spécifiques de criblage et de transfert entre cuves.",
            "Surveillance des systèmes d'agitation et d'aération des cuves.",
        ],
    },
    {
        "partie": "D — Finition",
        "id": "D1",
        "titre": "Conditionnement / finition du produit final",
        "description": "Regroupe les opérations qui mettent le produit final (concentré, "
                        "précipité, ou métal) sous une forme adaptée à son stockage, son "
                        "transport ou sa commercialisation : séchage final, mise en sac ou "
                        "en fût, protection contre l'humidité ou l'oxydation, étiquetage et "
                        "traçabilité.",
        "controles": [
            "Humidité résiduelle du produit",
            "Intégrité de l'emballage",
            "Conformité de l'étiquetage (lot, teneur, poids)",
        ],
        "parametres": [
            "Poids net par unité conditionnée",
            "Traçabilité du lot (numéro, date, provenance)",
            "Conditions de stockage (température, humidité)",
        ],
        "anomalies": None,
        "securite": None,
    },
    {
        "partie": "E — Rôles transversaux",
        "id": "E1",
        "titre": "Opérateur d'usine (généraliste)",
        "description": "Doit être capable d'assurer une présence active sur plusieurs "
                        "postes de la chaîne et de comprendre l'impact de chaque circuit sur "
                        "les suivants.",
        "competences": [
            "Vision d'ensemble du flowsheet",
            "Capacité à effectuer les rondes de contrôle sur l'ensemble des circuits",
            "Communication efficace entre postes (transmission de consignes en relève)",
        ],
        "outils": ["Carnet de bord / main courante", "Procédures de consignation",
                    "Plan de circulation et fiches de poste"],
    },
    {
        "partie": "E — Rôles transversaux",
        "id": "E2",
        "titre": "Opérateur de procédé / process",
        "description": "Vision transversale du bilan global de l'usine : suit les "
                        "indicateurs de performance de chaque circuit, alerte en cas de "
                        "dérive et propose des ajustements en lien avec le laboratoire et "
                        "l'encadrement technique.",
        "competences": [
            "Lecture de tableaux de bord multi-circuits",
            "Compréhension des bilans matière simplifiés",
            "Capacité à relier un symptôme (baisse de récupération, dérive de teneur) à sa "
            "cause probable dans le circuit amont",
        ],
    },
]

# Table métier → blocs recommandés (issue de la formation opérationnelle)
METIERS_BLOCS = [
    ("Opérateur concasseur", "A1, A3"),
    ("Opérateur broyeur", "A2, A4"),
    ("Opérateur d'usine (généraliste)", "A à E (parcours complet)"),
    ("Opérateur CIL/CIP", "C4"),
    ("Opérateur de procédé / process", "B, C, E2"),
    ("Chef de poste / superviseur", "Parcours complet + module bilans (formation de cadrage)"),
]

# Table métier → compétence opérationnelle visée en fin de parcours
METIERS_COMPETENCES = [
    ("Opérateur concasseur", "Conduire le circuit de concassage en autonomie et détecter "
                              "les anomalies courantes"),
    ("Opérateur broyeur", "Maintenir les paramètres de broyage dans leur plage cible et "
                           "ajuster en poste"),
    ("Opérateur CIL/CIP", "Assurer le transfert et le suivi du charbon actif, détecter une "
                           "baisse d'adsorption"),
    ("Opérateur de procédé", "Suivre les indicateurs multi-circuits et relier un symptôme "
                              "à sa cause probable"),
    ("Opérateur d'usine (généraliste)", "Assurer une rotation efficace entre postes avec "
                                         "une vision d'ensemble du flowsheet"),
]

# Points de sécurité transversaux (Section 5 — HSE)
SECURITE_HSE = [
    ("Consignation systématique (LOTO)", "Avant toute intervention sur un équipement à "
                                          "l'arrêt, quelle que soit l'urgence perçue."),
    ("Port des EPI adaptés à chaque poste", "Casque, protections auditives et oculaires, "
                                             "gants, chaussures de sécurité, protection "
                                             "respiratoire si réactifs."),
    ("Connaissance des FDS", "Fiches de données de sécurité de tous les réactifs manipulés "
                              "sur le poste, en particulier les réactifs cyanurés en "
                              "hydrométallurgie."),
    ("Procédures d'urgence connues", "Douche de sécurité, rince-œil, numéros d'alerte, "
                                      "points de rassemblement — affichés et connus de "
                                      "tous."),
    ("Culture du reporting", "Signalement systématique de toute anomalie, même mineure, "
                              "avant qu'elle ne s'aggrave."),
]

QUIZ_OPERATIONS = [
    {
        "categorie": "Formation opérationnelle",
        "question": "Une trémie tampon en aval du concasseur est pleine : peut-on quand "
                     "même démarrer/maintenir l'alimentation amont si le débit reste faible ?",
        "choices": [
            "Oui, tant que le débit reste faible",
            "Non, une trémie aval pleine impose l'arrêt de l'alimentation amont",
            "Oui, sans aucune condition",
            "Cela dépend uniquement de la couleur du minerai",
        ],
        "correct": 1,
        "explication": "Une trémie aval pleine impose l'arrêt de l'alimentation amont, sous "
                        "peine de débordement ou de bourrage en cascade.",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "Un bourrage sur le circuit de concassage doit être dégagé...",
        "choices": [
            "Immédiatement, à la main, pour gagner du temps",
            "Après consignation complète de l'équipement",
            "Seulement en fin de poste",
            "Uniquement par le chef de poste, sans consignation",
        ],
        "correct": 1,
        "explication": "C'est une règle de sécurité non négociable : consignation complète "
                        "obligatoire avant tout dégagement de bourrage.",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "Le port des protections auditives est-il nécessaire si le concasseur "
                     "tourne à vide ?",
        "choices": [
            "Non, ce n'est pas nécessaire à vide",
            "Oui, le bruit reste dangereux même à vide ; les EPI sont requis en permanence",
            "Seulement si le bruit dépasse 100 dB",
            "Seulement pour les visiteurs",
        ],
        "correct": 1,
        "explication": "Les EPI sont requis en permanence dans la zone, indépendamment de "
                        "l'état de charge de l'équipement.",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "En poste, le bruit du broyeur devient sourd et étouffé, et l'intensité "
                     "électrique du moteur augmente progressivement. Quelle est la cause la "
                     "plus probable ?",
        "choices": [
            "Une sous-charge du broyeur",
            "Une surcharge du broyeur (excès de charge solide ou % solides trop élevé)",
            "Une fuite d'eau de refroidissement",
            "Un problème de pH",
        ],
        "correct": 1,
        "explication": "Bruit sourd/étouffé + hausse d'intensité est le signe caractéristique "
                        "d'une surcharge du broyeur. Action : réduire le débit d'alimentation "
                        "fraîche et/ou augmenter le débit d'eau d'appoint.",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "À l'inverse, un bruit métallique fort et clair au broyeur signale "
                     "plutôt...",
        "choices": [
            "Une surcharge",
            "Une sous-charge (choc direct des corps broyants entre eux)",
            "Un dosage de réactif incorrect",
            "Une dérive de pH",
        ],
        "correct": 1,
        "explication": "Un bruit métallique fort et clair signale une sous-charge ; la "
                        "conduite à tenir est alors d'augmenter l'alimentation.",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "Sur un banc de flottation cuivre (consigne pH 10,5–11,0), un relevé "
                     "affiche pH = 9,4 avec une mousse plus sèche et moins stable. Quelle "
                     "cause vérifier en priorité ?",
        "choices": [
            "Une hausse du débit d'air uniquement",
            "Une dérive de la pompe doseuse de chaux (sous-dosage) ou du capteur pH",
            "Un excès de moussant",
            "Un débit d'alimentation trop faible",
        ],
        "correct": 1,
        "explication": "Causes à vérifier en priorité : sous-dosage de chaux, changement de "
                        "minéralogie de l'alimentation, ou dérive du capteur pH lui-même "
                        "(à confirmer par une mesure de contrôle indépendante).",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "Dans un circuit CIL/CIP, comment circulent le charbon actif et la "
                     "pulpe l'un par rapport à l'autre ?",
        "choices": [
            "Dans le même sens (co-courant)",
            "En sens opposés (contre-courant)",
            "Le charbon reste fixe, seule la pulpe circule",
            "Il n'y a pas de circulation organisée",
        ],
        "correct": 1,
        "explication": "Le charbon et la pulpe circulent en sens opposés (contre-courant) : "
                        "le charbon le plus frais rencontre la solution la plus appauvrie, "
                        "et le charbon le plus chargé rencontre la solution la plus riche, "
                        "ce qui maximise l'efficacité globale d'adsorption.",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "Le criblage de rétention dans une cuve CIL/CIP sert à...",
        "choices": [
            "Filtrer l'eau de procédé",
            "Retenir le charbon actif dans la cuve pendant que la pulpe passe",
            "Mesurer le pH de la pulpe",
            "Mesurer la teneur en cyanure",
        ],
        "correct": 1,
        "explication": "Le crible retient le charbon actif tout en laissant passer la "
                        "pulpe, condition nécessaire au fonctionnement du contre-courant.",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "Avant d'intervenir sur un équipement à l'arrêt, que faut-il faire ?",
        "choices": [
            "Couper simplement l'interrupteur local",
            "Une consignation complète (LOTO) est obligatoire",
            "Attendre 10 minutes puis intervenir",
            "Prévenir uniquement par talkie-walkie",
        ],
        "correct": 1,
        "explication": "Seule une consignation complète garantit l'absence de redémarrage "
                        "intempestif.",
    },
    {
        "categorie": "Formation opérationnelle",
        "question": "En cas de contact avec une solution cyanurée, que faut-il faire ?",
        "choices": [
            "Se laver simplement les mains au savon",
            "Appliquer immédiatement la procédure d'urgence (douche/rince-œil) et alerter",
            "Attendre la fin du poste pour signaler",
            "Continuer le travail si aucune douleur n'est ressentie",
        ],
        "correct": 1,
        "explication": "Toute exposition à un réactif dangereux impose une action "
                        "immédiate selon la procédure d'urgence, jamais un report.",
    },
]

# ========================================================================
# CONTENU GRADE CONTROL — issu du programme "Grade Control — Contrôle de
# teneurs minières" (Datamine Studio RM, mine à ciel ouvert & souterraine)
# ========================================================================

# Termes de glossaire spécifiques au Grade Control, à fusionner avec le
# glossaire général au chargement de l'application.
GLOSSAIRE_GRADE_CONTROL = [
    ("Grade Control", "Ensemble des méthodes utilisées pour délimiter, au moment de "
                       "l'exploitation, les zones de minerai et de stérile réellement "
                       "envoyées respectivement à l'usine et au terril, à partir de données "
                       "de production (forages de production, échantillonnage rapproché)."),
    ("Resource Modeling", "Modélisation de la ressource à l'échelle du gisement, en amont du "
                           "Grade Control : s'appuie sur des données de sondage plus espacées "
                           "et vise à estimer les tonnages/teneurs globaux, pas à guider "
                           "l'excavation bloc par bloc au jour le jour."),
    ("Modèle de blocs (Block Model)", "Découpage du gisement en blocs 3D réguliers, chacun "
                                       "porteur d'attributs (teneur estimée, densité, domaine "
                                       "géologique, classification Ore/Waste...)."),
    ("Domaine géologique", "Zone du gisement définie par des caractéristiques géologiques "
                            "homogènes (lithologie, altération, structure), à l'intérieur de "
                            "laquelle l'estimation des teneurs est réalisée séparément."),
    ("Wireframe", "Surface 3D filaire délimitant un volume géologique (corps minéralisé, "
                  "domaine, topographie), utilisée pour coder le modèle de blocs."),
    ("Nearest Neighbour (plus proche voisin)", "Méthode d'estimation la plus simple : "
                                                "chaque bloc reçoit la teneur de l'échantillon "
                                                "le plus proche, sans pondération ni lissage."),
    ("Inverse Distance (distance inverse)", "Méthode d'estimation qui pondère les "
                                             "échantillons voisins par l'inverse de leur "
                                             "distance (souvent élevée à une puissance) au "
                                             "bloc à estimer."),
    ("Krigeage", "Méthode d'estimation géostatistique qui pondère les échantillons voisins "
                 "en tenant compte à la fois de leur distance et de leur corrélation "
                 "spatiale (variogramme), pour produire l'estimateur linéaire non biaisé de "
                 "variance minimale."),
    ("Variogramme", "Outil géostatistique qui quantifie comment la ressemblance entre deux "
                     "échantillons diminue avec la distance qui les sépare ; sert de base "
                     "au krigeage."),
    ("Teneur de coupure (Cut-off Grade)", "Teneur seuil séparant ce qui est envoyé à l'usine "
                                           "(minerai) de ce qui est envoyé au terril "
                                           "(stérile) ; déterminée à partir des coûts "
                                           "opératoires, du prix du métal et de la "
                                           "récupération métallurgique."),
    ("Ore / Minerai (Grade Control)", "Bloc dont la teneur estimée est supérieure ou égale à "
                                       "la teneur de coupure : destiné au traitement."),
    ("Waste / Stérile (Grade Control)", "Bloc dont la teneur estimée est inférieure à la "
                                         "teneur de coupure : destiné au terril."),
    ("Dilution (minière)", "Incorporation involontaire de stérile dans le minerai extrait "
                            "(ou l'inverse), du fait des limites pratiques de sélectivité de "
                            "l'excavation ; fait baisser la teneur réellement traitée par "
                            "rapport à la teneur du modèle de blocs."),
    ("Perte de minerai (Ore Loss)", "Minerai laissé en place ou envoyé par erreur au terril "
                                     "du fait des limites de sélectivité de l'exploitation."),
    ("Sondage de production", "Forage rapproché réalisé spécifiquement pour le Grade "
                               "Control, à une maille beaucoup plus dense que les sondages "
                               "d'exploration, pour guider l'excavation à court terme."),
    ("Contact minerai/stérile", "Limite géologique ou géométrique séparant une zone "
                                 "minéralisée d'une zone stérile ; sa bonne interprétation "
                                 "conditionne la précision du Grade Control."),
]

# Contenu de référence par module du programme (affichable dans l'onglet
# Grade Control, façon fiche de cours consultable).
GRADE_CONTROL_MODULES = [
    {
        "id": "M1",
        "titre": "Introduction au Grade Control",
        "points": [
            "Définition et rôle du Grade Control dans une exploitation minière",
            "Différence avec l'Exploration et le Resource Modeling : le Grade Control "
            "opère à l'échelle de la production à court terme, avec des données plus "
            "denses",
            "Conséquences d'un mauvais contrôle de teneurs : dilution excessive, pertes "
            "de minerai, mauvaise réconciliation usine/modèle",
            "Le Grade Control fait le pont entre Géologie, Mine Planning et Production",
        ],
    },
    {
        "id": "M2",
        "titre": "Données et échantillonnage",
        "points": [
            "Types de données : sondages de production, échantillonnage de rainures/faces, "
            "résultats d'analyses",
            "Contrôle qualité des données avant utilisation (cohérence, doublons, valeurs "
            "aberrantes)",
            "Identification et traitement des valeurs aberrantes (« outliers ») avant "
            "estimation, pour ne pas fausser localement le modèle",
        ],
    },
    {
        "id": "M3",
        "titre": "Compréhension de la minéralisation",
        "points": [
            "Interprétation des domaines géologiques et des contacts minerai/stérile",
            "Notion de continuité de la minéralisation dans l'espace",
            "La géologie doit guider le Grade Control, pas l'inverse : un modèle "
            "statistiquement propre mais géologiquement incohérent reste faux",
        ],
    },
    {
        "id": "M4",
        "titre": "Modèle de blocs et Grade Control",
        "points": [
            "Structure d'un Block Model : blocs réguliers 3D porteurs d'attributs",
            "Codage des domaines géologiques dans le modèle à partir des wireframes",
            "Classification des blocs selon les critères du projet (teneur, domaine, "
            "confiance de l'estimation)",
        ],
    },
    {
        "id": "M5",
        "titre": "Estimation des teneurs",
        "points": [
            "Nearest Neighbour : simple mais grossier, sensible à la position exacte des "
            "échantillons",
            "Inverse Distance : pondération par distance, plus lisse, ne tient pas compte "
            "de la corrélation spatiale réelle",
            "Krigeage : s'appuie sur le variogramme, généralement la méthode de référence "
            "quand les données le permettent",
            "La densité des données de sondage conditionne fortement la fiabilité de "
            "l'estimation, quelle que soit la méthode",
        ],
    },
    {
        "id": "M6",
        "titre": "Définition de la teneur de coupure",
        "points": [
            "La teneur de coupure a un rôle économique : elle sépare ce qui couvre ses "
            "coûts de traitement de ce qui n'en couvre pas",
            "Formule usuelle simplifiée : Cut-off = (coût minier + coût de traitement) / "
            "(prix du métal x récupération métallurgique)",
            "Un projet peut définir plusieurs catégories de minerai (haute/basse teneur) "
            "selon sa stratégie de traitement",
        ],
    },
    {
        "id": "M7",
        "titre": "Grade Control à ciel ouvert",
        "points": [
            "Définition des limites minerai/stérile à l'échelle des bancs (benches) "
            "d'exploitation",
            "Création de polygones de Grade Control guidant directement les opérateurs "
            "d'engins",
            "Gestion de la dilution géométrique liée à la sélectivité des équipements "
            "(largeur de godet, précision GPS des engins)",
        ],
    },
    {
        "id": "M8",
        "titre": "Grade Control en mine souterraine",
        "points": [
            "Données issues de forages et échantillonnages souterrains, souvent plus "
            "contraints géométriquement qu'à ciel ouvert",
            "Application du Grade Control aux structures minéralisées (veines, filons) : "
            "sélectivité souvent plus fine mais accès plus limité",
            "Gestion de la dilution propre au souterrain (débourrage des épontes, "
            "sur-creusement)",
        ],
    },
    {
        "id": "M9",
        "titre": "Grade Control avec Datamine Studio RM",
        "points": [
            "Chaîne de travail logicielle : préparation projet → import des données → "
            "visualisation 3D → wireframes → modèle de blocs → codage → estimation → "
            "cut-off → classification Ore/Waste → extraction des résultats",
            "Chaque étape logicielle correspond à une étape méthodologique du Grade "
            "Control ; l'outil ne remplace pas la compréhension géologique en amont",
        ],
    },
    {
        "id": "M10",
        "titre": "Interprétation et contrôle des résultats",
        "points": [
            "Contrôle de cohérence des teneurs estimées par rapport aux données brutes",
            "Identification des anomalies (teneurs isolées extrêmes, discontinuités "
            "suspectes aux limites de domaines)",
            "Contrôle des limites Ore/Waste avant transmission à la production",
        ],
    },
    {
        "id": "M11",
        "titre": "Projet pratique complet",
        "points": [
            "Enchaînement de bout en bout : données géologiques → préparation → "
            "modélisation → estimation → cut-off → Ore/Waste → visualisation → "
            "interprétation → résultats",
            "Objectif : reproduire en conditions proches du réel un cycle complet de "
            "Grade Control",
        ],
    },
    {
        "id": "M12",
        "titre": "Application professionnelle",
        "points": [
            "Organisation du travail de Grade Control en entreprise : cycle récurrent "
            "(souvent quotidien ou hebdomadaire) aligné sur le planning de production",
            "Collaboration étroite entre Géologue, Mine Planning et Production : le Grade "
            "Control n'a de valeur que s'il est utilisé à temps par les équipes terrain",
            "Bonnes pratiques : traçabilité des versions de modèle, documentation des "
            "hypothèses de cut-off, contrôle systématique avant diffusion",
            "Erreur fréquente à éviter : figer un cut-off une fois pour toutes sans le "
            "reconsidérer quand les prix métaux ou les coûts opératoires changent "
            "significativement",
        ],
    },
]


def calculer_teneur_coupure(cout_minier, cout_traitement, prix_metal, recuperation_pct,
                             autres_couts=0.0):
    """Calcule une teneur de coupure économique simplifiée (Module 6).

    cout_minier, cout_traitement, autres_couts : coûts par tonne traitée, dans la même
        devise que prix_metal (ex. $/t)
    prix_metal : prix de vente net du métal, par unité de teneur cohérente avec la
        teneur recherchée (ex. $/once, $/tonne de métal contenu, selon convention)
    recuperation_pct : récupération métallurgique attendue, en %

    Retourne la teneur de coupure dans l'unité cohérente avec prix_metal (ex. si prix_metal
    est en $ par tonne de métal contenu, le résultat est une teneur en fraction/tonne ;
    à adapter aux conventions du projet — cet outil est pédagogique, pas un calcul officiel
    de coupure de réserve).
    """
    if prix_metal <= 0 or recuperation_pct <= 0:
        raise ValueError("Le prix du métal et la récupération doivent être strictement "
                          "positifs.")
    couts_totaux = cout_minier + cout_traitement + autres_couts
    return couts_totaux / (prix_metal * recuperation_pct / 100)


QUIZ_GRADE_CONTROL = [
    {
        "categorie": "Grade Control",
        "question": "Quelle est la principale différence entre le Resource Modeling et le "
                     "Grade Control ?",
        "choices": [
            "Ce sont exactement la même chose",
            "Le Grade Control utilise des données de production plus denses pour guider "
            "l'excavation à court terme, contrairement au Resource Modeling à l'échelle "
            "du gisement",
            "Le Resource Modeling ne sert qu'en mine souterraine",
            "Le Grade Control ne concerne que la phase d'exploration",
        ],
        "correct": 1,
        "explication": "Le Grade Control s'appuie sur des sondages de production "
                        "rapprochés pour guider l'excavation au jour le jour, alors que le "
                        "Resource Modeling estime la ressource globale à partir de données "
                        "de sondage plus espacées.",
    },
    {
        "categorie": "Grade Control",
        "question": "Un bloc dont la teneur estimée est inférieure à la teneur de coupure "
                     "est classé...",
        "choices": ["Ore / Minerai", "Waste / Stérile", "Toujours en attente d'analyse",
                    "Automatiquement en minerai haute teneur"],
        "correct": 1,
        "explication": "Par définition, la teneur de coupure sépare le minerai (teneur ≥ "
                        "cut-off) du stérile (teneur < cut-off).",
    },
    {
        "categorie": "Grade Control",
        "question": "Parmi ces méthodes d'estimation, laquelle s'appuie explicitement sur "
                     "un variogramme (corrélation spatiale) ?",
        "choices": ["Nearest Neighbour", "Inverse Distance", "Krigeage",
                    "Aucune des trois"],
        "correct": 2,
        "explication": "Le krigeage utilise le variogramme pour pondérer les échantillons "
                        "en tenant compte à la fois de la distance et de la structure "
                        "spatiale de la minéralisation, contrairement au plus proche voisin "
                        "ou à la distance inverse.",
    },
    {
        "categorie": "Grade Control",
        "question": "Qu'est-ce que la dilution minière ?",
        "choices": [
            "Une méthode d'estimation des teneurs",
            "L'incorporation involontaire de stérile dans le minerai extrait, qui fait "
            "baisser la teneur réellement traitée",
            "Un réactif utilisé en flottation",
            "La densité de forage utilisée pour le Grade Control",
        ],
        "correct": 1,
        "explication": "La dilution résulte des limites pratiques de sélectivité de "
                        "l'excavation (largeur de godet, précision de guidage) et fait "
                        "baisser la teneur réellement envoyée à l'usine par rapport à celle "
                        "du modèle de blocs.",
    },
    {
        "categorie": "Grade Control",
        "question": "En Grade Control à ciel ouvert, à quelle échelle les limites "
                     "minerai/stérile sont-elles typiquement définies ?",
        "choices": ["À l'échelle du gisement entier, une fois pour toutes",
                    "À l'échelle des bancs d'exploitation (benches), via des polygones "
                    "guidant les engins",
                    "Uniquement a posteriori, après traitement en usine",
                    "Elles ne sont jamais définies à ciel ouvert"],
        "correct": 1,
        "explication": "Le Grade Control à ciel ouvert produit des polygones à l'échelle "
                        "des bancs d'exploitation, directement utilisables par les "
                        "opérateurs d'engins sur le terrain.",
    },
    {
        "categorie": "Grade Control",
        "question": "Pourquoi la teneur de coupure ne doit-elle pas être figée une fois "
                     "pour toutes ?",
        "choices": [
            "Parce que la réglementation minière l'interdit",
            "Parce qu'elle dépend du prix du métal et des coûts opératoires, qui varient "
            "dans le temps",
            "Parce qu'elle doit changer tous les jours par principe",
            "Parce que Datamine Studio RM la recalcule automatiquement",
        ],
        "correct": 1,
        "explication": "La teneur de coupure économique dépend directement des coûts "
                        "miniers et de traitement ainsi que du prix du métal ; une "
                        "variation significative de ces paramètres justifie de la "
                        "reconsidérer.",
    },
    {
        "categorie": "Grade Control",
        "question": "Dans la chaîne de travail Grade Control sous Datamine Studio RM, "
                     "que fait-on juste avant d'appliquer le cut-off ?",
        "choices": [
            "L'extraction finale des résultats",
            "L'estimation des teneurs dans le modèle de blocs",
            "L'importation brute des données de sondage, sans autre étape",
            "La classification Ore/Waste",
        ],
        "correct": 1,
        "explication": "La séquence logique est : préparation → import → wireframes → "
                        "modèle de blocs → codage → ESTIMATION des teneurs → application "
                        "du CUT-OFF → classification Ore/Waste → extraction.",
    },
]

# Le glossaire général intègre aussi les termes spécifiques au Grade Control.
GLOSSAIRE = GLOSSAIRE + GLOSSAIRE_GRADE_CONTROL
