# -*- coding: utf-8 -*-
"""
Moteur d'analyse combinée des relevés d'exploitation.

Contrairement au contrôle de conformité (data_postes.evaluer_conformite),
qui juge CHAQUE relevé isolément par rapport à son barème, ce module lit
PLUSIEURS indicateurs ensemble pour repérer des situations qui n'apparaissent
que par combinaison (ex. intensité moteur élevée + débit d'alimentation
faible = signe de bourrage, pas juste deux valeurs isolées).

Deux sorties principales :
  - scores_conformite_par_poste(releves) : pour le graphique (barres), un
    score de conformité récent par poste.
  - generer_alertes(releves) : pour le texte, une liste de lectures
    combinées, triées par sévérité.

Librement adaptable : les règles ci-dessous sont des exemples représentatifs
d'une usine de traitement de minerais avec circuit de cyanuration. Ajoutez,
retirez ou ajustez des règles dans REGLES_COMBINEES pour coller à votre
flowsheet réel (voir aussi data_postes.py pour la liste des postes/
paramètres disponibles).
"""

from data_postes import POSTES_REF, obtenir_bareme

POSTES_PAR_ID = {p["id"]: p for p in POSTES_REF}

NIVEAU_ORDRE = {"critique": 0, "attention": 1, "info": 2}
NIVEAU_ICONE = {"critique": "⛔", "attention": "⚠", "info": "ℹ"}


# ---------------------------------------------------------------------
# Préparation des données
# ---------------------------------------------------------------------
def dernieres_valeurs(releves):
    """À partir d'une liste de relevés (triés du plus récent au plus
    ancien, comme le renvoie db.lister_releves), garde uniquement la
    valeur la plus récente pour chaque couple (poste_id, paramètre).

    Retourne un dict : (poste_id, parametre) -> relevé (dict).
    """
    dv = {}
    for r in releves:
        cle = (r["poste_id"], r["parametre"])
        if cle not in dv:
            dv[cle] = r
    return dv


def _valeur(dv, poste_id, parametre):
    r = dv.get((poste_id, parametre))
    return None if r is None else r["valeur"]


def _position_relative(valeur, poste_id, parametre):
    """Position de la valeur dans le barème normal, en fraction (0 = borne
    basse, 1 = borne haute). Peut sortir de [0, 1] si hors norme. Retourne
    None si la valeur ou le barème est indisponible, ou si le barème n'a
    qu'une seule borne (auquel cas on retourne 0 dans la norme, >1 au-delà,
    ou <0 en-deçà, selon le sens de la borne)."""
    if valeur is None:
        return None
    bareme = obtenir_bareme(poste_id, parametre)
    if bareme is None:
        return None
    bmin, bmax = bareme
    if bmin is not None and bmax is not None and bmax != bmin:
        return (valeur - bmin) / (bmax - bmin)
    if bmax is not None:
        return valeur / bmax if bmax else None
    if bmin is not None:
        return valeur / bmin if bmin else None
    return None


def _proche_ou_au_dela(valeur, poste_id, parametre, seuil_proche=0.85):
    """True si la valeur dépasse déjà la borne haute, ou s'en approche
    (au-delà de seuil_proche, ex. 0.85 = 85% de la plage normale)."""
    pos = _position_relative(valeur, poste_id, parametre)
    return pos is not None and pos >= seuil_proche


def _sous_ou_proche_de_la_borne_basse(valeur, poste_id, parametre, seuil_proche=0.15):
    pos = _position_relative(valeur, poste_id, parametre)
    return pos is not None and pos <= seuil_proche


# ---------------------------------------------------------------------
# Règles combinées (lecture croisée de plusieurs indicateurs)
# ---------------------------------------------------------------------
# Chaque règle est une fonction qui reçoit `dv` (dernières valeurs connues,
# voir dernieres_valeurs) et retourne soit None (rien à signaler), soit un
# texte d'alerte. Le niveau ("critique" / "attention" / "info") est fixé
# par la règle elle-même dans le tuple retourné.

def _regle_surcharge_concasseur(dv):
    intensite = _valeur(dv, "A1", "Intensité électrique moteur")
    debit = _valeur(dv, "A1", "Débit d'alimentation")
    if intensite is None:
        return None
    intensite_haute = _proche_ou_au_dela(intensite, "A1", "Intensité électrique moteur", 0.85)
    if not intensite_haute:
        return None
    debit_bas = debit is not None and _sous_ou_proche_de_la_borne_basse(
        debit, "A1", "Débit d'alimentation", 0.25
    )
    if debit_bas:
        return (
            "critique",
            f"Concassage (A1) : intensité moteur élevée ({intensite:g} A) combinée à un "
            f"débit d'alimentation faible ({debit:g} t/h) — signature typique d'un bourrage "
            f"ou d'un blocage en chambre de concassage. Risque de surtension et de casse "
            f"mécanique si la charge n'est pas dégagée rapidement."
        )
    return (
        "attention",
        f"Concassage (A1) : intensité moteur proche de la limite haute ({intensite:g} A). "
        f"À surveiller — une dérive supplémentaire exposerait le moteur à une surtension."
    )


def _regle_colmatage_cyclone(dv):
    pression = _valeur(dv, "A2", "Pression cyclone")
    debit_cyclone = _valeur(dv, "A2", "Débit cyclone")
    if pression is None or debit_cyclone is None:
        return None
    pression_haute = _proche_ou_au_dela(pression, "A2", "Pression cyclone", 0.85)
    debit_bas = _sous_ou_proche_de_la_borne_basse(debit_cyclone, "A2", "Débit cyclone", 0.2)
    if pression_haute and debit_bas:
        return (
            "critique",
            f"Broyage (A2) : pression cyclone élevée ({pression:g} kPa) avec un débit cyclone "
            f"réduit ({debit_cyclone:g} m³/h) — signe probable d'un colmatage (apex/vortex "
            f"finder bouché). Risque d'usure prématurée de la pompe et de perte de classification."
        )
    return None


def _regle_cyanure_ph(dv, poste_id, nom_poste, param_ph, param_reactif):
    ph = _valeur(dv, poste_id, param_ph)
    reactif = _valeur(dv, poste_id, param_reactif)
    if ph is None or reactif is None:
        return None
    reactif_haut = _proche_ou_au_dela(reactif, poste_id, param_reactif, 0.85)
    ph_bas = _sous_ou_proche_de_la_borne_basse(ph, poste_id, param_ph, 0.2)
    if reactif_haut and ph_bas:
        return (
            "critique",
            f"{nom_poste} ({poste_id}) : concentration en réactif de cyanuration élevée "
            f"({reactif:g}) combinée à un pH en baisse ({ph:g}) — zone à surveiller en priorité. "
            f"En milieu cyanuré, un pH insuffisamment alcalin favorise le dégagement de gaz "
            f"cyanhydrique (HCN), dangereux pour les opérateurs. Vérifier immédiatement le "
            f"dosage de chaux, la ventilation de la zone et le port des EPI (détecteur HCN)."
        )
    if reactif_haut:
        return (
            "attention",
            f"{nom_poste} ({poste_id}) : concentration en réactif de cyanuration proche de "
            f"la limite haute ({reactif:g}) — zone à forte concentration de cyanure, "
            f"maintenir la surveillance de la ventilation et des EPI."
        )
    if ph_bas:
        return (
            "attention",
            f"{nom_poste} ({poste_id}) : pH en baisse ({ph:g}), proche de la borne basse — "
            f"à corriger avant que la marge d'alcalinité ne devienne insuffisante en présence "
            f"de cyanure."
        )
    return None


def _regle_cyanure_c1(dv):
    return _regle_cyanure_ph(dv, "C1", "Lixiviation en tas", "pH solution", "Concentration réactif")


def _regle_cyanure_c3(dv):
    return _regle_cyanure_ph(
        dv, "C3", "Lixiviation en cuve", "pH", "Concentration réactif libre"
    )


def _regle_parc_a_residus(dv):
    niveau = _valeur(dv, "D3", "Niveau du parc à résidus")
    teneur = _valeur(dv, "D3", "Teneur résiduelle en métal")
    alertes = []
    if niveau is not None and _proche_ou_au_dela(niveau, "D3", "Niveau du parc à résidus", 0.85):
        alertes.append(
            ("critique" if niveau > (obtenir_bareme("D3", "Niveau du parc à résidus")[1] or niveau)
             else "attention",
             f"Gestion des rejets (D3) : niveau du parc à résidus élevé ({niveau:g} m), proche "
             f"de la limite. Risque de débordement — planifier une vidange ou un rehaussement "
             f"de digue avant la prochaine forte pluie.")
        )
    if teneur is not None and _proche_ou_au_dela(
        teneur, "D3", "Teneur résiduelle en métal", 1.0
    ):
        alertes.append(
            ("attention",
             f"Gestion des rejets (D3) : teneur résiduelle en métal hors norme ({teneur:g} %) "
             f"— pertes de métal vers les résidus, à recouper avec la récupération en amont "
             f"(flottation / CIL-CIP).")
        )
    return alertes


def _regle_flottation(dv):
    ph = _valeur(dv, "B4", "pH")
    niveau_pulpe = _valeur(dv, "B4", "Niveau de pulpe")
    if ph is None or niveau_pulpe is None:
        return None
    ph_hors_norme = _proche_ou_au_dela(ph, "B4", "pH", 1.0) or _sous_ou_proche_de_la_borne_basse(
        ph, "B4", "pH", 0.0
    )
    pulpe_basse = _sous_ou_proche_de_la_borne_basse(niveau_pulpe, "B4", "Niveau de pulpe", 0.2)
    if ph_hors_norme and pulpe_basse:
        return (
            "attention",
            f"Flottation (B4) : pH hors plage ({ph:g}) combiné à un niveau de pulpe bas "
            f"({niveau_pulpe:g} %) — conditions de flottation dégradées, risque de perte de "
            f"récupération. Vérifier le dosage des réactifs et l'aération des cellules."
        )
    return None


def _regle_raffinage(dv):
    pertes = _valeur(dv, "D2", "Pertes de fusion/affinage")
    if pertes is None:
        return None
    if _proche_ou_au_dela(pertes, "D2", "Pertes de fusion/affinage", 1.0):
        return (
            "attention",
            f"Raffinage (D2) : pertes de fusion/affinage supérieures à la norme ({pertes:g} %) "
            f"— écart à investiguer avec le responsable métallurgie."
        )
    return None


REGLES_COMBINEES = [
    _regle_surcharge_concasseur,
    _regle_colmatage_cyclone,
    _regle_cyanure_c1,
    _regle_cyanure_c3,
    _regle_flottation,
    _regle_raffinage,
]

REGLES_MULTI = [
    _regle_parc_a_residus,
]


# ---------------------------------------------------------------------
# Score de conformité par poste (pour le graphique)
# ---------------------------------------------------------------------
def scores_conformite_par_poste(releves, fenetre=8):
    """Pour chaque poste ayant des relevés, calcule un score de conformité
    récent (fraction de relevés conformes parmi les `fenetre` derniers
    relevés de ce poste, tous paramètres confondus).

    Retourne une liste de tuples (poste_id, titre, nb_conforme, nb_total,
    score 0..1 ou None si aucun relevé n'a de barème défini), triée par
    score croissant (le poste le plus préoccupant en premier).
    """
    par_poste = {}
    for r in releves:
        par_poste.setdefault(r["poste_id"], []).append(r)

    resultats = []
    for poste_id, poste in POSTES_PAR_ID.items():
        rs = par_poste.get(poste_id, [])[:fenetre]
        evalues = [r for r in rs if r["conforme"] is not None]
        if not evalues:
            resultats.append((poste_id, poste["titre"], 0, 0, None))
            continue
        nb_conforme = sum(1 for r in evalues if r["conforme"])
        nb_total = len(evalues)
        resultats.append((poste_id, poste["titre"], nb_conforme, nb_total, nb_conforme / nb_total))

    # Postes avec données d'abord (triés du plus préoccupant au meilleur),
    # puis postes sans aucune donnée à la fin.
    avec_score = sorted([r for r in resultats if r[4] is not None], key=lambda r: r[4])
    sans_score = [r for r in resultats if r[4] is None]
    return avec_score + sans_score


# ---------------------------------------------------------------------
# Génération des alertes combinées (pour le texte)
# ---------------------------------------------------------------------
def generer_alertes(releves, seuil_derive=0.5, min_relevés_derive=3):
    """Analyse l'ensemble des derniers relevés et retourne une liste
    d'alertes triées par sévérité : [{"niveau": .., "texte": ..}, ...].
    """
    dv = dernieres_valeurs(releves)
    alertes = []

    for regle in REGLES_COMBINEES:
        res = regle(dv)
        if res:
            niveau, texte = res
            alertes.append({"niveau": niveau, "texte": texte})

    for regle in REGLES_MULTI:
        for res in regle(dv) or []:
            niveau, texte = res
            alertes.append({"niveau": niveau, "texte": texte})

    # Dérive générale par poste : beaucoup de non-conformités récentes,
    # même sans règle combinée spécifique définie pour ce poste.
    par_poste = {}
    for r in releves:
        par_poste.setdefault(r["poste_id"], []).append(r)
    for poste_id, rs in par_poste.items():
        rs = rs[:10]
        evalues = [r for r in rs if r["conforme"] is not None]
        if len(evalues) < min_relevés_derive:
            continue
        nb_non_conforme = sum(1 for r in evalues if not r["conforme"])
        ratio = nb_non_conforme / len(evalues)
        if ratio >= seuil_derive:
            titre = POSTES_PAR_ID.get(poste_id, {}).get("titre", poste_id)
            alertes.append({
                "niveau": "attention",
                "texte": (
                    f"{titre} ({poste_id}) : {nb_non_conforme}/{len(evalues)} des derniers "
                    f"relevés sont hors norme — poste en dérive, une inspection est recommandée."
                ),
            })

    alertes.sort(key=lambda a: NIVEAU_ORDRE.get(a["niveau"], 9))

    if not alertes:
        alertes.append({
            "niveau": "info",
            "texte": "Aucune combinaison à risque détectée dans les relevés récents : les "
                     "indicateurs disponibles semblent cohérents entre eux.",
        })

    return alertes
