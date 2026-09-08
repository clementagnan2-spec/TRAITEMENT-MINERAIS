# -*- coding: utf-8 -*-
"""
Couche d'accès aux données — base SQLite locale et persistante.

Le fichier de base de données est stocké dans le dossier utilisateur de
l'application (voir get_db_path). Toutes les opérations passent par ce
module : aucune autre partie de l'application n'ouvre sqlite3 directement.

NOTE DE PORTÉE : SQLite convient très bien à un poste unique ou à un petit
nombre de postes partageant un dossier réseau (faible concurrence
d'écriture). Pour une exploitation avec de nombreux postes simultanés, il
est recommandé de migrer vers un serveur de base de données dédié
(PostgreSQL par exemple) ; le schéma ci-dessous est conçu pour rester
compatible avec une telle migration (types simples, clés étrangères
explicites).
"""

import sqlite3
import os
import sys
import hashlib
import secrets
import datetime

DB_FILENAME = "mine_ops.sqlite3"


def get_db_path():
    """Retourne le chemin du fichier de base de données, à côté de
    l'exécutable ou du script — pour rester simple à sauvegarder/déplacer."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, DB_FILENAME)


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifiant TEXT UNIQUE NOT NULL,
    nom_complet TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin','superviseur','chef_de_poste','operateur')),
    mot_de_passe_hash TEXT NOT NULL,
    sel TEXT NOT NULL,
    actif INTEGER NOT NULL DEFAULT 1,
    doit_changer_mdp INTEGER NOT NULL DEFAULT 1,
    date_creation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS postes_reference (
    id TEXT PRIMARY KEY,
    partie TEXT NOT NULL,
    titre TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS affectations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    poste_id TEXT NOT NULL REFERENCES postes_reference(id),
    date_jour TEXT NOT NULL,
    quart TEXT NOT NULL CHECK (quart IN ('Matin','Après-midi','Nuit')),
    statut TEXT NOT NULL DEFAULT 'Planifiée' CHECK (statut IN ('Planifiée','En cours','Terminée','Absence')),
    cree_le TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS releves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poste_id TEXT NOT NULL REFERENCES postes_reference(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    parametre TEXT NOT NULL,
    valeur REAL NOT NULL,
    unite TEXT,
    commentaire TEXT,
    conforme INTEGER,
    borne_min REAL,
    borne_max REAL
);

CREATE TABLE IF NOT EXISTS productions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poste_id TEXT NOT NULL REFERENCES postes_reference(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    type_flux TEXT NOT NULL CHECK (type_flux IN ('Alimentation','Concentré','Stérile / rejet','Produit fini')),
    masse_tonnes REAL NOT NULL,
    teneur_pct REAL,
    commentaire TEXT,
    poste_origine_id TEXT REFERENCES postes_reference(id)
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poste_id TEXT REFERENCES postes_reference(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    gravite TEXT NOT NULL CHECK (gravite IN ('Mineure','Modérée','Majeure','Critique')),
    description TEXT NOT NULL,
    statut TEXT NOT NULL DEFAULT 'Ouvert' CHECK (statut IN ('Ouvert','En cours de traitement','Résolu')),
    resolu_par INTEGER REFERENCES users(id),
    horodatage_resolution TEXT,
    action_corrective TEXT
);

CREATE TABLE IF NOT EXISTS loto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipement TEXT NOT NULL,
    poste_id TEXT REFERENCES postes_reference(id),
    verrouille_par INTEGER NOT NULL REFERENCES users(id),
    horodatage_verrouillage TEXT NOT NULL,
    motif TEXT,
    deverrouille_par INTEGER REFERENCES users(id),
    horodatage_deverrouillage TEXT,
    statut TEXT NOT NULL DEFAULT 'Verrouillé' CHECK (statut IN ('Verrouillé','Déverrouillé'))
);

CREATE TABLE IF NOT EXISTS checklist_hse_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    poste_id TEXT REFERENCES postes_reference(id),
    horodatage TEXT NOT NULL,
    points_json TEXT NOT NULL,
    signature TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS journal_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    horodatage TEXT NOT NULL,
    action TEXT NOT NULL,
    details TEXT
);

-- -----------------------------------------------------------------
-- Comptabilité analytique : liaison processus -> centre de coût ->
-- mouvement matière -> coût de production -> écriture comptable.
-- Un centre de coût par poste (voir data_centres_cout.py) ; les
-- mouvements de matière réels sont déjà suivis dans la table
-- "productions" (poste_id + type_flux + masse_tonnes).
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS centres_cout (
    poste_id TEXT PRIMARY KEY REFERENCES postes_reference(id),
    code_centre TEXT NOT NULL,
    compte_charge TEXT NOT NULL,
    stock_entree TEXT,
    stock_sortie TEXT,
    methode_cout TEXT NOT NULL DEFAULT 'CMUP',
    flux_sortie_defaut TEXT
);

CREATE TABLE IF NOT EXISTS charges_exploitation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poste_id TEXT NOT NULL REFERENCES postes_reference(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    categorie TEXT NOT NULL CHECK (categorie IN
        ('Matière','Énergie','Réactifs','Main-d''œuvre','Maintenance','Amortissement','Autre')),
    montant REAL NOT NULL,
    compte_num TEXT,
    compte_libelle TEXT,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS ecritures_comptables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poste_id TEXT NOT NULL REFERENCES postes_reference(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    date_debut TEXT NOT NULL,
    date_fin TEXT,
    code_centre TEXT NOT NULL,
    montant_total REAL NOT NULL,
    flux_reference TEXT,
    masse_reference_t REAL,
    cout_unitaire_t REAL,
    compte_stock_num TEXT,
    compte_stock_libelle TEXT,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS ecritures_comptables_lignes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ecriture_id INTEGER NOT NULL REFERENCES ecritures_comptables(id),
    sens TEXT NOT NULL CHECK (sens IN ('Débit','Crédit')),
    compte_num TEXT NOT NULL,
    compte_libelle TEXT NOT NULL,
    libelle_ligne TEXT,
    montant REAL NOT NULL
);
"""


def hash_password(password, sel=None):
    if sel is None:
        sel = secrets.token_hex(16)
    h = hashlib.sha256((sel + password).encode("utf-8")).hexdigest()
    return h, sel


def verify_password(password, sel, hash_attendu):
    h, _ = hash_password(password, sel)
    return secrets.compare_digest(h, hash_attendu)


def now_iso():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db(postes_reference):
    """Crée les tables si nécessaire et amorce un compte admin par défaut
    ainsi que la table de référence des postes/circuits."""
    conn = get_connection()
    conn.executescript(SCHEMA)

    # Migration légère pour les bases existantes créées avant l'ajout du
    # barème de conformité : on ajoute les colonnes si elles manquent.
    colonnes_releves = {row["name"] for row in conn.execute("PRAGMA table_info(releves)")}
    for colonne, type_sql in (("conforme", "INTEGER"), ("borne_min", "REAL"),
                               ("borne_max", "REAL")):
        if colonne not in colonnes_releves:
            conn.execute(f"ALTER TABLE releves ADD COLUMN {colonne} {type_sql}")

    for p in postes_reference:
        conn.execute(
            "INSERT OR IGNORE INTO postes_reference (id, partie, titre) VALUES (?,?,?)",
            (p["id"], p["partie"], p["titre"]),
        )

    from data_centres_cout import CENTRES_COUT_REF
    for c in CENTRES_COUT_REF:
        conn.execute(
            "INSERT OR IGNORE INTO centres_cout (poste_id, code_centre, compte_charge, "
            "stock_entree, stock_sortie, methode_cout, flux_sortie_defaut) "
            "VALUES (?,?,?,?,?,?,?)",
            (c["poste_id"], c["code_centre"], c["compte_charge"], c["stock_entree"],
             c["stock_sortie"], c["methode_cout"], c["flux_sortie_defaut"]),
        )

    cur = conn.execute("SELECT COUNT(*) AS n FROM users")
    if cur.fetchone()["n"] == 0:
        h, sel = hash_password("admin123")
        conn.execute(
            "INSERT INTO users (identifiant, nom_complet, role, mot_de_passe_hash, sel, "
            "actif, doit_changer_mdp, date_creation) VALUES (?,?,?,?,?,1,1,?)",
            ("admin", "Administrateur", "admin", h, sel, now_iso()),
        )
    conn.commit()
    conn.close()


def log_audit(user_id, action, details=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO journal_audit (user_id, horodatage, action, details) VALUES (?,?,?,?)",
        (user_id, now_iso(), action, details),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# Utilisateurs
# ---------------------------------------------------------------------
def authentifier(identifiant, mot_de_passe):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE identifiant = ? AND actif = 1", (identifiant,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    if verify_password(mot_de_passe, row["sel"], row["mot_de_passe_hash"]):
        return dict(row)
    return None


def creer_utilisateur(identifiant, nom_complet, role, mot_de_passe):
    h, sel = hash_password(mot_de_passe)
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (identifiant, nom_complet, role, mot_de_passe_hash, sel, actif, "
        "doit_changer_mdp, date_creation) VALUES (?,?,?,?,?,1,1,?)",
        (identifiant, nom_complet, role, h, sel, now_iso()),
    )
    conn.commit()
    conn.close()


def lister_utilisateurs(actifs_seulement=False):
    conn = get_connection()
    q = "SELECT * FROM users"
    if actifs_seulement:
        q += " WHERE actif = 1"
    q += " ORDER BY nom_complet"
    rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def desactiver_utilisateur(user_id):
    conn = get_connection()
    conn.execute("UPDATE users SET actif = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def reactiver_utilisateur(user_id):
    conn = get_connection()
    conn.execute("UPDATE users SET actif = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def changer_mot_de_passe(user_id, nouveau_mdp):
    h, sel = hash_password(nouveau_mdp)
    conn = get_connection()
    conn.execute(
        "UPDATE users SET mot_de_passe_hash = ?, sel = ?, doit_changer_mdp = 0 WHERE id = ?",
        (h, sel, user_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# Postes de référence
# ---------------------------------------------------------------------
def lister_postes_reference():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM postes_reference ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------
# Affectations (planning d'équipe)
# ---------------------------------------------------------------------
def creer_affectation(user_id, poste_id, date_jour, quart):
    conn = get_connection()
    conn.execute(
        "INSERT INTO affectations (user_id, poste_id, date_jour, quart, statut, cree_le) "
        "VALUES (?,?,?,?,'Planifiée',?)",
        (user_id, poste_id, date_jour, quart, now_iso()),
    )
    conn.commit()
    conn.close()


def lister_affectations(date_jour=None):
    conn = get_connection()
    q = (
        "SELECT a.*, u.nom_complet, p.titre AS poste_titre "
        "FROM affectations a "
        "JOIN users u ON u.id = a.user_id "
        "JOIN postes_reference p ON p.id = a.poste_id"
    )
    params = ()
    if date_jour:
        q += " WHERE a.date_jour = ?"
        params = (date_jour,)
    q += " ORDER BY a.date_jour DESC, a.quart, u.nom_complet"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def maj_statut_affectation(affectation_id, statut):
    conn = get_connection()
    conn.execute("UPDATE affectations SET statut = ? WHERE id = ?", (statut, affectation_id))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# Relevés d'exploitation
# ---------------------------------------------------------------------
def ajouter_releve(poste_id, user_id, parametre, valeur, unite, commentaire):
    from data_postes import evaluer_conformite

    conforme, borne_min, borne_max = evaluer_conformite(poste_id, parametre, valeur)

    conn = get_connection()
    conn.execute(
        "INSERT INTO releves (poste_id, user_id, horodatage, parametre, valeur, unite, "
        "commentaire, conforme, borne_min, borne_max) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (poste_id, user_id, now_iso(), parametre, valeur, unite, commentaire,
         (None if conforme is None else int(conforme)), borne_min, borne_max),
    )
    conn.commit()
    conn.close()

    return {"conforme": conforme, "borne_min": borne_min, "borne_max": borne_max}


def lister_releves(poste_id=None, limite=200):
    conn = get_connection()
    q = (
        "SELECT r.*, u.nom_complet, p.titre AS poste_titre "
        "FROM releves r "
        "JOIN users u ON u.id = r.user_id "
        "JOIN postes_reference p ON p.id = r.poste_id"
    )
    params = ()
    if poste_id:
        q += " WHERE r.poste_id = ?"
        params = (poste_id,)
    q += " ORDER BY r.horodatage DESC LIMIT ?"
    rows = conn.execute(q, params + (limite,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------
# Productions réelles (pour bilan matière)
# ---------------------------------------------------------------------
def ajouter_production(poste_id, user_id, type_flux, masse_tonnes, teneur_pct, commentaire,
                        poste_origine_id=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO productions (poste_id, user_id, horodatage, type_flux, masse_tonnes, "
        "teneur_pct, commentaire, poste_origine_id) VALUES (?,?,?,?,?,?,?,?)",
        (poste_id, user_id, now_iso(), type_flux, masse_tonnes, teneur_pct, commentaire,
         poste_origine_id),
    )
    conn.commit()
    conn.close()


def dernier_cout_unitaire(poste_id):
    """Dernier coût unitaire à la tonne (CMUP) connu pour ce poste, issu de
    la dernière écriture comptable générée qui en comportait un."""
    conn = get_connection()
    row = conn.execute(
        "SELECT cout_unitaire_t FROM ecritures_comptables WHERE poste_id = ? "
        "AND cout_unitaire_t IS NOT NULL ORDER BY horodatage DESC LIMIT 1",
        (poste_id,),
    ).fetchone()
    conn.close()
    return row["cout_unitaire_t"] if row else None


def transferer_stock(poste_origine_id, poste_destination_id, user_id, masse_tonnes, teneur_pct,
                      commentaire):
    """Enregistre le transfert d'une masse de matière du stock d'un poste
    vers l'« Alimentation » d'un poste suivant (ex. le broyé de A2 qui
    alimente la flottation B4). Ce transfert :
      - crée l'entrée « Alimentation » chez le poste de destination, en
        traçant explicitement le poste d'origine (pour que le stock du
        poste d'origine soit ensuite compté comme sorti — voir
        niveaux_stocks) ;
      - si un CMUP (coût unitaire à la tonne) est déjà connu pour le poste
        d'origine, valorise automatiquement ce transfert comme une charge
        « Matière » chez le poste de destination, à ce CMUP — c'est la
        matière première du poste suivant, à son coût de revient.
    Retourne le CMUP utilisé (ou None si aucun n'était disponible, auquel
    cas aucune charge n'a été créée automatiquement)."""
    ajouter_production(poste_destination_id, user_id, "Alimentation", masse_tonnes, teneur_pct,
                        commentaire, poste_origine_id=poste_origine_id)

    cmup = dernier_cout_unitaire(poste_origine_id)
    if cmup is not None:
        montant = masse_tonnes * cmup
        centre_origine = obtenir_centre_cout(poste_origine_id)
        libelle_origine = centre_origine["code_centre"] if centre_origine else poste_origine_id
        ajouter_charge(
            poste_destination_id, user_id, "Matière", montant,
            f"Transfert depuis {libelle_origine} — {masse_tonnes:.2f} t à "
            f"{cmup:.2f} FCFA/t (CMUP)"
        )
    return cmup


def lister_productions(poste_id=None, date_debut=None, date_fin=None, limite=500):
    conn = get_connection()
    q = (
        "SELECT p.*, u.nom_complet, pr.titre AS poste_titre "
        "FROM productions p "
        "JOIN users u ON u.id = p.user_id "
        "JOIN postes_reference pr ON pr.id = p.poste_id WHERE 1=1"
    )
    params = []
    if poste_id:
        q += " AND p.poste_id = ?"
        params.append(poste_id)
    if date_debut:
        q += " AND p.horodatage >= ?"
        params.append(date_debut)
    if date_fin:
        q += " AND p.horodatage <= ?"
        params.append(date_fin)
    q += " ORDER BY p.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def bilan_matiere_periode(poste_id, date_debut, date_fin):
    """Agrège les productions du poste sur la période et calcule un bilan
    matière pondéré (masse totale et teneur moyenne pondérée par flux)."""
    prods = lister_productions(poste_id=poste_id, date_debut=date_debut, date_fin=date_fin,
                                limite=100000)
    par_flux = {}
    for p in prods:
        flux = p["type_flux"]
        par_flux.setdefault(flux, {"masse": 0.0, "metal": 0.0})
        par_flux[flux]["masse"] += p["masse_tonnes"]
        if p["teneur_pct"] is not None:
            par_flux[flux]["metal"] += p["masse_tonnes"] * p["teneur_pct"] / 100.0

    resultat = {}
    for flux, agg in par_flux.items():
        teneur_moy = (agg["metal"] / agg["masse"] * 100) if agg["masse"] > 0 else None
        resultat[flux] = {
            "masse_totale_t": agg["masse"],
            "teneur_moyenne_pct": teneur_moy,
            "metal_total_t": agg["metal"],
        }
    return resultat


# ---------------------------------------------------------------------
# Incidents
# ---------------------------------------------------------------------
def ajouter_incident(poste_id, user_id, gravite, description):
    conn = get_connection()
    conn.execute(
        "INSERT INTO incidents (poste_id, user_id, horodatage, gravite, description, statut) "
        "VALUES (?,?,?,?,?,'Ouvert')",
        (poste_id, user_id, now_iso(), gravite, description),
    )
    conn.commit()
    conn.close()


def lister_incidents(statut=None, limite=200):
    conn = get_connection()
    q = (
        "SELECT i.*, u.nom_complet AS declare_par, p.titre AS poste_titre, "
        "r.nom_complet AS resolu_par_nom "
        "FROM incidents i "
        "JOIN users u ON u.id = i.user_id "
        "LEFT JOIN postes_reference p ON p.id = i.poste_id "
        "LEFT JOIN users r ON r.id = i.resolu_par WHERE 1=1"
    )
    params = []
    if statut:
        q += " AND i.statut = ?"
        params.append(statut)
    q += " ORDER BY i.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def resoudre_incident(incident_id, resolu_par_id, action_corrective):
    conn = get_connection()
    conn.execute(
        "UPDATE incidents SET statut = 'Résolu', resolu_par = ?, horodatage_resolution = ?, "
        "action_corrective = ? WHERE id = ?",
        (resolu_par_id, now_iso(), action_corrective, incident_id),
    )
    conn.commit()
    conn.close()


def maj_statut_incident(incident_id, statut):
    conn = get_connection()
    conn.execute("UPDATE incidents SET statut = ? WHERE id = ?", (statut, incident_id))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# LOTO (consignation)
# ---------------------------------------------------------------------
def verrouiller_equipement(equipement, poste_id, user_id, motif):
    conn = get_connection()
    conn.execute(
        "INSERT INTO loto (equipement, poste_id, verrouille_par, horodatage_verrouillage, "
        "motif, statut) VALUES (?,?,?,?,?,'Verrouillé')",
        (equipement, poste_id, user_id, now_iso(), motif),
    )
    conn.commit()
    conn.close()


def deverrouiller_equipement(loto_id, user_id):
    conn = get_connection()
    conn.execute(
        "UPDATE loto SET statut = 'Déverrouillé', deverrouille_par = ?, "
        "horodatage_deverrouillage = ? WHERE id = ?",
        (user_id, now_iso(), loto_id),
    )
    conn.commit()
    conn.close()


def lister_loto(statut=None):
    conn = get_connection()
    q = (
        "SELECT l.*, u1.nom_complet AS verrouille_par_nom, u2.nom_complet AS "
        "deverrouille_par_nom, p.titre AS poste_titre "
        "FROM loto l "
        "JOIN users u1 ON u1.id = l.verrouille_par "
        "LEFT JOIN users u2 ON u2.id = l.deverrouille_par "
        "LEFT JOIN postes_reference p ON p.id = l.poste_id WHERE 1=1"
    )
    params = []
    if statut:
        q += " AND l.statut = ?"
        params.append(statut)
    q += " ORDER BY l.horodatage_verrouillage DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------
# Checklist HSE (signée)
# ---------------------------------------------------------------------
def enregistrer_checklist_hse(user_id, poste_id, points_json, signature):
    conn = get_connection()
    conn.execute(
        "INSERT INTO checklist_hse_log (user_id, poste_id, horodatage, points_json, "
        "signature) VALUES (?,?,?,?,?)",
        (user_id, poste_id, now_iso(), points_json, signature),
    )
    conn.commit()
    conn.close()


def lister_checklist_hse(limite=100):
    conn = get_connection()
    rows = conn.execute(
        "SELECT c.*, u.nom_complet, p.titre AS poste_titre "
        "FROM checklist_hse_log c "
        "JOIN users u ON u.id = c.user_id "
        "LEFT JOIN postes_reference p ON p.id = c.poste_id "
        "ORDER BY c.horodatage DESC LIMIT ?",
        (limite,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------
# Tableau de bord — agrégations du jour
# ---------------------------------------------------------------------
def kpis_du_jour():
    aujourdhui = datetime.date.today().isoformat()
    conn = get_connection()

    tonnage = conn.execute(
        "SELECT COALESCE(SUM(masse_tonnes),0) AS s FROM productions "
        "WHERE type_flux = 'Alimentation' AND horodatage >= ?",
        (aujourdhui,),
    ).fetchone()["s"]

    incidents_ouverts = conn.execute(
        "SELECT COUNT(*) AS n FROM incidents WHERE statut != 'Résolu'"
    ).fetchone()["n"]

    loto_actifs = conn.execute(
        "SELECT COUNT(*) AS n FROM loto WHERE statut = 'Verrouillé'"
    ).fetchone()["n"]

    releves_jour = conn.execute(
        "SELECT COUNT(*) AS n FROM releves WHERE horodatage >= ?", (aujourdhui,)
    ).fetchone()["n"]

    releves_non_conformes_jour = conn.execute(
        "SELECT COUNT(*) AS n FROM releves WHERE horodatage >= ? AND conforme = 0",
        (aujourdhui,),
    ).fetchone()["n"]

    equipes_jour = conn.execute(
        "SELECT COUNT(*) AS n FROM affectations WHERE date_jour = ?", (aujourdhui,)
    ).fetchone()["n"]

    conn.close()
    return {
        "tonnage_alimentation_jour": tonnage,
        "incidents_ouverts": incidents_ouverts,
        "loto_actifs": loto_actifs,
        "releves_jour": releves_jour,
        "releves_non_conformes_jour": releves_non_conformes_jour,
        "equipes_planifiees_jour": equipes_jour,
    }


# ---------------------------------------------------------------------
# Comptabilité analytique — centres de coût, charges, écritures
# ---------------------------------------------------------------------
def lister_centres_cout():
    conn = get_connection()
    rows = conn.execute(
        "SELECT cc.*, p.titre AS poste_titre FROM centres_cout cc "
        "JOIN postes_reference p ON p.id = cc.poste_id ORDER BY cc.poste_id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_centre_cout(poste_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM centres_cout WHERE poste_id = ?", (poste_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def ajouter_charge(poste_id, user_id, categorie, montant, commentaire):
    from data_plan_comptable import compte_charge
    compte = compte_charge(categorie)
    conn = get_connection()
    conn.execute(
        "INSERT INTO charges_exploitation (poste_id, user_id, horodatage, categorie, "
        "montant, compte_num, compte_libelle, commentaire) VALUES (?,?,?,?,?,?,?,?)",
        (poste_id, user_id, now_iso(), categorie, montant, compte["numero"],
         compte["libelle"], commentaire),
    )
    conn.commit()
    conn.close()


def lister_charges(poste_id=None, date_debut=None, date_fin=None, limite=500):
    conn = get_connection()
    q = (
        "SELECT c.*, u.nom_complet, p.titre AS poste_titre "
        "FROM charges_exploitation c "
        "JOIN users u ON u.id = c.user_id "
        "JOIN postes_reference p ON p.id = c.poste_id WHERE 1=1"
    )
    params = []
    if poste_id:
        q += " AND c.poste_id = ?"
        params.append(poste_id)
    if date_debut:
        q += " AND c.horodatage >= ?"
        params.append(date_debut)
    if date_fin:
        q += " AND c.horodatage <= ?"
        params.append(date_fin)
    q += " ORDER BY c.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cout_centre_periode(poste_id, date_debut, date_fin=None):
    """Agrège les charges saisies pour ce poste sur la période, par
    catégorie et par compte SYSCOHADA, et calcule le coût total du
    centre de coût."""
    charges = lister_charges(poste_id=poste_id, date_debut=date_debut, date_fin=date_fin,
                              limite=100000)
    par_categorie = {}
    par_compte = {}
    total = 0.0
    for c in charges:
        par_categorie.setdefault(c["categorie"], 0.0)
        par_categorie[c["categorie"]] += c["montant"]

        cle_compte = (c["compte_num"], c["compte_libelle"])
        par_compte.setdefault(cle_compte, 0.0)
        par_compte[cle_compte] += c["montant"]

        total += c["montant"]
    return {"par_categorie": par_categorie, "par_compte": par_compte, "total": total}


def generer_ecriture_comptable(poste_id, date_debut, date_fin, flux_reference, user_id,
                                commentaire=""):
    """Calcule le coût total du centre de coût sur la période, le rapporte
    à la masse du flux de sortie choisi (issue du bilan matière) pour
    obtenir un coût unitaire à la tonne, puis enregistre l'écriture
    comptable SYSCOHADA correspondante :
      - une ligne au débit par compte de charge (classe 6) déjà engagé,
        pour information/traçabilité (ces charges sont supposées déjà
        comptabilisées au fil de l'eau en comptabilité générale) ;
      - une ligne au débit du compte de stock/en-cours (classe 3) du
        poste, pour le montant total (valorisation de la production) ;
      - une ligne au crédit du compte de contrepartie 736 "Variation des
        stocks de biens et de services produits", pour le même montant.
    """
    from data_plan_comptable import compte_stock, COMPTE_CONTREPARTIE_STOCK

    centre = obtenir_centre_cout(poste_id)
    if centre is None:
        raise ValueError("Aucun centre de coût défini pour ce poste.")

    cout = cout_centre_periode(poste_id, date_debut, date_fin)
    total = cout["total"]
    if total <= 0:
        raise ValueError("Aucune charge saisie sur cette période : rien à comptabiliser.")

    masse_ref = None
    cout_unitaire = None
    if flux_reference:
        bilan = bilan_matiere_periode(poste_id, date_debut, date_fin)
        agg = bilan.get(flux_reference)
        if agg and agg["masse_totale_t"] > 0:
            masse_ref = agg["masse_totale_t"]
            cout_unitaire = total / masse_ref

    stock = compte_stock(centre["stock_sortie"])

    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO ecritures_comptables (poste_id, user_id, horodatage, date_debut, "
        "date_fin, code_centre, montant_total, flux_reference, masse_reference_t, "
        "cout_unitaire_t, compte_stock_num, compte_stock_libelle, commentaire) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (poste_id, user_id, now_iso(), date_debut, date_fin, centre["code_centre"], total,
         flux_reference, masse_ref, cout_unitaire, stock["numero"], stock["libelle"],
         commentaire),
    )
    ecriture_id = cur.lastrowid

    lignes = []
    for (compte_num, compte_libelle), montant in cout["par_compte"].items():
        lignes.append(("Débit", compte_num, compte_libelle,
                        f"Charges {centre['code_centre']} — période au {date_debut}", montant))
    lignes.append(("Débit", stock["numero"], stock["libelle"],
                    f"Entrée en stock — {centre['code_centre']} ({centre['stock_sortie']})",
                    total))
    lignes.append(("Crédit", COMPTE_CONTREPARTIE_STOCK["numero"],
                    COMPTE_CONTREPARTIE_STOCK["libelle"],
                    f"Valorisation de la production — {centre['code_centre']}", total))

    for sens, compte_num, compte_libelle, libelle_ligne, montant in lignes:
        conn.execute(
            "INSERT INTO ecritures_comptables_lignes (ecriture_id, sens, compte_num, "
            "compte_libelle, libelle_ligne, montant) VALUES (?,?,?,?,?,?)",
            (ecriture_id, sens, compte_num, compte_libelle, libelle_ligne, montant),
        )
    conn.commit()
    conn.close()

    return {
        "ecriture_id": ecriture_id, "total": total, "par_categorie": cout["par_categorie"],
        "masse_reference_t": masse_ref, "cout_unitaire_t": cout_unitaire,
        "code_centre": centre["code_centre"], "lignes": lignes,
    }


def niveaux_stocks(date_debut=None, date_fin=None):
    """Pour chaque centre de coût, calcule la masse entrée (flux
    'Alimentation'), la masse sortie et le solde physique (entrées -
    sorties) sur la période, ainsi que la valorisation du solde à partir
    du dernier coût unitaire connu pour ce poste (issu de la dernière
    écriture comptable générée).

    La masse sortie d'un poste compte deux choses : ses propres flux de
    sortie (Concentré, Stérile/rejet, Produit fini) ET la masse que des
    postes en aval ont transférée depuis son stock (voir
    transferer_stock) — c'est ce qui fait qu'un stock en amont diminue
    bien quand le poste suivant produit à partir de lui.

    Un solde >= 0 est qualifié de débiteur (normal pour un compte de
    stock/actif) ; un solde négatif (sorties > entrées constatées) est
    qualifié de créditeur — signe d'un écart à vérifier."""
    conn = get_connection()
    q_entrees = (
        "SELECT COALESCE(SUM(masse_tonnes), 0) AS m FROM productions "
        "WHERE poste_id = ? AND type_flux = 'Alimentation'"
    )
    q_sorties_propres = (
        "SELECT COALESCE(SUM(masse_tonnes), 0) AS m FROM productions "
        "WHERE poste_id = ? AND type_flux != 'Alimentation'"
    )
    q_sorties_transferees = (
        "SELECT COALESCE(SUM(masse_tonnes), 0) AS m FROM productions "
        "WHERE poste_origine_id = ?"
    )
    if date_debut:
        q_entrees += " AND horodatage >= ?"
        q_sorties_propres += " AND horodatage >= ?"
        q_sorties_transferees += " AND horodatage >= ?"
    if date_fin:
        q_entrees += " AND horodatage <= ?"
        q_sorties_propres += " AND horodatage <= ?"
        q_sorties_transferees += " AND horodatage <= ?"

    resultats = []
    for c in lister_centres_cout():
        params = [c["poste_id"]]
        if date_debut:
            params.append(date_debut)
        if date_fin:
            params.append(date_fin)
        entrees = conn.execute(q_entrees, params).fetchone()["m"]
        sorties_propres = conn.execute(q_sorties_propres, params).fetchone()["m"]
        sorties_transferees = conn.execute(q_sorties_transferees, params).fetchone()["m"]
        sorties = sorties_propres + sorties_transferees
        solde = entrees - sorties

        cout_unitaire = dernier_cout_unitaire(c["poste_id"])
        valeur_solde = solde * cout_unitaire if cout_unitaire is not None else None

        resultats.append({
            "poste_id": c["poste_id"], "poste_titre": c["poste_titre"],
            "code_centre": c["code_centre"], "entrees_t": entrees,
            "sorties_t": sorties, "sorties_propres_t": sorties_propres,
            "sorties_transferees_t": sorties_transferees, "solde_t": solde,
            "sens": "Débiteur" if solde >= 0 else "Créditeur",
            "cout_unitaire_t": cout_unitaire, "valeur_solde": valeur_solde,
        })
    conn.close()
    return resultats


def lister_lignes_ecriture(ecriture_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM ecritures_comptables_lignes WHERE ecriture_id = ? ORDER BY id",
        (ecriture_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def lister_ecritures_comptables(poste_id=None, limite=200):
    conn = get_connection()
    q = (
        "SELECT e.*, p.titre AS poste_titre, u.nom_complet FROM ecritures_comptables e "
        "JOIN postes_reference p ON p.id = e.poste_id "
        "JOIN users u ON u.id = e.user_id WHERE 1=1"
    )
    params = []
    if poste_id:
        q += " AND e.poste_id = ?"
        params.append(poste_id)
    q += " ORDER BY e.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
