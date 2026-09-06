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
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS productions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poste_id TEXT NOT NULL REFERENCES postes_reference(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    type_flux TEXT NOT NULL CHECK (type_flux IN ('Alimentation','Concentré','Stérile / rejet','Produit fini')),
    masse_tonnes REAL NOT NULL,
    teneur_pct REAL,
    commentaire TEXT
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

CREATE TABLE IF NOT EXISTS configuration (
    cle TEXT PRIMARY KEY,
    valeur TEXT
);

CREATE TABLE IF NOT EXISTS couts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categorie TEXT NOT NULL CHECK (categorie IN ('Réactifs','Main-d''oeuvre','Énergie',
                                                   'Maintenance','Autre')),
    poste_id TEXT REFERENCES postes_reference(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    montant REAL NOT NULL,
    devise TEXT NOT NULL DEFAULT 'XOF',
    description TEXT
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

    for p in postes_reference:
        conn.execute(
            "INSERT OR IGNORE INTO postes_reference (id, partie, titre) VALUES (?,?,?)",
            (p["id"], p["partie"], p["titre"]),
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
# Configuration du site (paramètres clé/valeur, ex. type de mine actif)
# ---------------------------------------------------------------------
def get_configuration(cle, defaut=None):
    conn = get_connection()
    row = conn.execute("SELECT valeur FROM configuration WHERE cle = ?", (cle,)).fetchone()
    conn.close()
    return row["valeur"] if row is not None else defaut


def set_configuration(cle, valeur):
    conn = get_connection()
    conn.execute(
        "INSERT INTO configuration (cle, valeur) VALUES (?, ?) "
        "ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur",
        (cle, valeur),
    )
    conn.commit()
    conn.close()


def get_type_mine():
    """Retourne le type de mine actif du site (nom du profil dans
    data_mine_types.MINE_TYPES). Import différé pour éviter tout cycle
    d'import avec data_mine_types (qui importe data_postes, pas db)."""
    from data_mine_types import DEFAUT
    return get_configuration("type_mine", DEFAUT)


def set_type_mine(type_mine):
    set_configuration("type_mine", type_mine)


# ---------------------------------------------------------------------
# Coûts d'exploitation (Réactifs, Main-d'oeuvre, Énergie, Maintenance, Autre)
# ---------------------------------------------------------------------
def ajouter_cout(categorie, poste_id, user_id, montant, devise, description):
    conn = get_connection()
    conn.execute(
        "INSERT INTO couts (categorie, poste_id, user_id, horodatage, montant, devise, "
        "description) VALUES (?,?,?,?,?,?,?)",
        (categorie, poste_id, user_id, now_iso(), montant, devise, description),
    )
    conn.commit()
    conn.close()


def lister_couts(categorie=None, poste_id=None, date_debut=None, date_fin=None, limite=500):
    conn = get_connection()
    q = (
        "SELECT c.*, u.nom_complet, p.titre AS poste_titre "
        "FROM couts c "
        "JOIN users u ON u.id = c.user_id "
        "LEFT JOIN postes_reference p ON p.id = c.poste_id WHERE 1=1"
    )
    params = []
    if categorie:
        q += " AND c.categorie = ?"
        params.append(categorie)
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


def synthese_couts_periode(date_debut, date_fin, poste_id=None):
    """Calcule le total des coûts par catégorie sur la période, le total
    général, le tonnage alimenté sur la même période (depuis productions),
    et le coût par tonne qui en résulte. Retourne un dict prêt à afficher."""
    couts = lister_couts(poste_id=poste_id, date_debut=date_debut, date_fin=date_fin,
                          limite=100000)
    par_categorie = {}
    total = 0.0
    devise = "XOF"
    for c in couts:
        par_categorie.setdefault(c["categorie"], 0.0)
        par_categorie[c["categorie"]] += c["montant"]
        total += c["montant"]
        devise = c["devise"] or devise

    conn = get_connection()
    q = "SELECT COALESCE(SUM(masse_tonnes),0) AS s FROM productions WHERE type_flux = " \
        "'Alimentation' AND horodatage >= ?"
    params = [date_debut]
    if date_fin:
        q += " AND horodatage <= ?"
        params.append(date_fin)
    if poste_id:
        q += " AND poste_id = ?"
        params.append(poste_id)
    tonnage = conn.execute(q, params).fetchone()["s"]
    conn.close()

    cout_par_tonne = (total / tonnage) if tonnage and tonnage > 0 else None

    return {
        "par_categorie": par_categorie,
        "total": total,
        "devise": devise,
        "tonnage_periode": tonnage,
        "cout_par_tonne": cout_par_tonne,
    }


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
    conn = get_connection()
    conn.execute(
        "INSERT INTO releves (poste_id, user_id, horodatage, parametre, valeur, unite, "
        "commentaire) VALUES (?,?,?,?,?,?,?)",
        (poste_id, user_id, now_iso(), parametre, valeur, unite, commentaire),
    )
    conn.commit()
    conn.close()


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
def ajouter_production(poste_id, user_id, type_flux, masse_tonnes, teneur_pct, commentaire):
    conn = get_connection()
    conn.execute(
        "INSERT INTO productions (poste_id, user_id, horodatage, type_flux, masse_tonnes, "
        "teneur_pct, commentaire) VALUES (?,?,?,?,?,?,?)",
        (poste_id, user_id, now_iso(), type_flux, masse_tonnes, teneur_pct, commentaire),
    )
    conn.commit()
    conn.close()


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

    equipes_jour = conn.execute(
        "SELECT COUNT(*) AS n FROM affectations WHERE date_jour = ?", (aujourdhui,)
    ).fetchone()["n"]

    conn.close()
    return {
        "tonnage_alimentation_jour": tonnage,
        "incidents_ouverts": incidents_ouverts,
        "loto_actifs": loto_actifs,
        "releves_jour": releves_jour,
        "equipes_planifiees_jour": equipes_jour,
    }
