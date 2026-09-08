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
        ('Matière','Énergie','Réactifs','Main-d''œuvre','Maintenance','Amortissement',
         'Transport','Autre')),
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

-- -----------------------------------------------------------------
-- Module Logistique minière : flotte, dispatch, pont-bascule,
-- carburant, maintenance, magasin/pièces. Le coût logistique d'un
-- véhicule, rapporté aux tonnes transportées, peut être transféré comme
-- charge « Transport » vers le centre de coût d'un poste (voir
-- transferer_cout_logistique), rejoignant ainsi le même système de
-- coût de production / écritures comptables que le reste de l'usine.
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vehicules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    immatriculation TEXT,
    type TEXT NOT NULL CHECK (type IN
        ('Camion','Chargeuse','Excavatrice','Bulldozer','Citerne','Véhicule léger','Autre')),
    marque_modele TEXT,
    capacite_tonnes REAL,
    compteur_km REAL DEFAULT 0,
    compteur_heures REAL DEFAULT 0,
    conducteur_affecte TEXT,
    statut TEXT NOT NULL DEFAULT 'Disponible' CHECK (statut IN
        ('Disponible','En mission','Maintenance','Immobilisé')),
    assurance_echeance TEXT,
    prochaine_maintenance_heures REAL,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS missions_transport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER NOT NULL REFERENCES vehicules(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    origine TEXT,
    destination TEXT,
    poste_destination_id TEXT REFERENCES postes_reference(id),
    distance_km REAL,
    nombre_voyages REAL,
    tonnes_par_voyage REAL,
    tonnage_total REAL,
    temps_attente_min REAL,
    temps_chargement_min REAL,
    temps_dechargement_min REAL,
    carburant_consomme_l REAL,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS tickets_pesee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_ticket TEXT NOT NULL,
    vehicule_id INTEGER NOT NULL REFERENCES vehicules(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    matiere TEXT,
    poids_brut_t REAL NOT NULL,
    tare_t REAL NOT NULL,
    poids_net_t REAL NOT NULL,
    origine TEXT,
    destination TEXT,
    poste_destination_id TEXT REFERENCES postes_reference(id),
    grade_teneur REAL,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS pleins_carburant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER NOT NULL REFERENCES vehicules(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    compteur REAL,
    litres REAL NOT NULL,
    prix_unitaire REAL NOT NULL,
    montant REAL NOT NULL,
    conducteur TEXT,
    station TEXT,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS maintenances_flotte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER NOT NULL REFERENCES vehicules(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    type_intervention TEXT NOT NULL CHECK (type_intervention IN
        ('Préventive','Corrective','Vidange','Pneus','Batterie','Autre')),
    compteur_heures REAL,
    compteur_km REAL,
    description TEXT,
    cout REAL NOT NULL DEFAULT 0,
    prochaine_echeance_heures REAL
);

CREATE TABLE IF NOT EXISTS pieces_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    designation TEXT NOT NULL,
    categorie TEXT NOT NULL CHECK (categorie IN
        ('Pneus','Filtres','Huiles','Pièces mécaniques','Pièces électriques','Consommables',
         'EPI','Autre')),
    unite TEXT NOT NULL DEFAULT 'unité',
    stock_actuel REAL NOT NULL DEFAULT 0,
    seuil_alerte REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS mouvements_pieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    piece_id INTEGER NOT NULL REFERENCES pieces_stock(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    type_mouvement TEXT NOT NULL CHECK (type_mouvement IN ('Entrée','Sortie')),
    quantite REAL NOT NULL,
    vehicule_id INTEGER REFERENCES vehicules(id),
    cout_unitaire REAL,
    montant REAL,
    commentaire TEXT
);

CREATE TABLE IF NOT EXISTS charges_logistique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER NOT NULL REFERENCES vehicules(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    horodatage TEXT NOT NULL,
    categorie TEXT NOT NULL CHECK (categorie IN
        ('Carburant','Pneus','Maintenance','Personnel','Pièces','Autre')),
    montant REAL NOT NULL,
    origine TEXT NOT NULL DEFAULT 'Manuelle' CHECK (origine IN
        ('Manuelle','Carburant (auto)','Maintenance (auto)','Pièces (auto)')),
    commentaire TEXT
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


# ---------------------------------------------------------------------
# Module Logistique minière — flotte, dispatch, pont-bascule, carburant,
# maintenance, magasin/pièces, et liaison avec les coûts de production.
# ---------------------------------------------------------------------
def ajouter_vehicule(code, immatriculation, type_vehicule, marque_modele, capacite_tonnes,
                      conducteur_affecte, commentaire):
    conn = get_connection()
    conn.execute(
        "INSERT INTO vehicules (code, immatriculation, type, marque_modele, capacite_tonnes, "
        "conducteur_affecte, statut, commentaire) VALUES (?,?,?,?,?,?,'Disponible',?)",
        (code, immatriculation, type_vehicule, marque_modele, capacite_tonnes,
         conducteur_affecte, commentaire),
    )
    conn.commit()
    conn.close()


def lister_vehicules():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM vehicules ORDER BY code").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def obtenir_vehicule(vehicule_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM vehicules WHERE id = ?", (vehicule_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def modifier_statut_vehicule(vehicule_id, statut):
    conn = get_connection()
    conn.execute("UPDATE vehicules SET statut = ? WHERE id = ?", (statut, vehicule_id))
    conn.commit()
    conn.close()


def mettre_a_jour_compteurs_vehicule(vehicule_id, compteur_km=None, compteur_heures=None):
    conn = get_connection()
    if compteur_km is not None:
        conn.execute("UPDATE vehicules SET compteur_km = ? WHERE id = ?",
                     (compteur_km, vehicule_id))
    if compteur_heures is not None:
        conn.execute("UPDATE vehicules SET compteur_heures = ? WHERE id = ?",
                     (compteur_heures, vehicule_id))
    conn.commit()
    conn.close()


def ajouter_mission(vehicule_id, user_id, origine, destination, poste_destination_id,
                     distance_km, nombre_voyages, tonnes_par_voyage, temps_attente_min,
                     temps_chargement_min, temps_dechargement_min, carburant_consomme_l,
                     commentaire):
    tonnage_total = (nombre_voyages or 0) * (tonnes_par_voyage or 0)
    conn = get_connection()
    conn.execute(
        "INSERT INTO missions_transport (vehicule_id, user_id, horodatage, origine, "
        "destination, poste_destination_id, distance_km, nombre_voyages, tonnes_par_voyage, "
        "tonnage_total, temps_attente_min, temps_chargement_min, temps_dechargement_min, "
        "carburant_consomme_l, commentaire) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (vehicule_id, user_id, now_iso(), origine, destination, poste_destination_id,
         distance_km, nombre_voyages, tonnes_par_voyage, tonnage_total, temps_attente_min,
         temps_chargement_min, temps_dechargement_min, carburant_consomme_l, commentaire),
    )
    conn.commit()
    conn.close()
    return tonnage_total


def lister_missions(vehicule_id=None, limite=200):
    conn = get_connection()
    q = (
        "SELECT m.*, v.code AS vehicule_code, u.nom_complet FROM missions_transport m "
        "JOIN vehicules v ON v.id = m.vehicule_id JOIN users u ON u.id = m.user_id WHERE 1=1"
    )
    params = []
    if vehicule_id:
        q += " AND m.vehicule_id = ?"
        params.append(vehicule_id)
    q += " ORDER BY m.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ajouter_ticket_pesee(numero_ticket, vehicule_id, user_id, matiere, poids_brut_t, tare_t,
                          origine, destination, poste_destination_id, grade_teneur,
                          commentaire):
    poids_net_t = poids_brut_t - tare_t
    conn = get_connection()
    conn.execute(
        "INSERT INTO tickets_pesee (numero_ticket, vehicule_id, user_id, horodatage, "
        "matiere, poids_brut_t, tare_t, poids_net_t, origine, destination, "
        "poste_destination_id, grade_teneur, commentaire) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (numero_ticket, vehicule_id, user_id, now_iso(), matiere, poids_brut_t, tare_t,
         poids_net_t, origine, destination, poste_destination_id, grade_teneur, commentaire),
    )
    conn.commit()
    conn.close()

    # Le poids net alimente automatiquement le bilan matière du poste de
    # destination, comme une alimentation externe (ex. ROM livré au A0).
    if poste_destination_id:
        ajouter_production(poste_destination_id, user_id, "Alimentation", poids_net_t,
                            grade_teneur, f"Ticket de pesée {numero_ticket} — véhicule "
                                          f"{obtenir_vehicule(vehicule_id)['code']}")
    return poids_net_t


def lister_tickets_pesee(vehicule_id=None, limite=200):
    conn = get_connection()
    q = (
        "SELECT t.*, v.code AS vehicule_code, u.nom_complet FROM tickets_pesee t "
        "JOIN vehicules v ON v.id = t.vehicule_id JOIN users u ON u.id = t.user_id WHERE 1=1"
    )
    params = []
    if vehicule_id:
        q += " AND t.vehicule_id = ?"
        params.append(vehicule_id)
    q += " ORDER BY t.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ajouter_plein_carburant(vehicule_id, user_id, compteur, litres, prix_unitaire, conducteur,
                             station, commentaire):
    montant = litres * prix_unitaire
    conn = get_connection()
    conn.execute(
        "INSERT INTO pleins_carburant (vehicule_id, user_id, horodatage, compteur, litres, "
        "prix_unitaire, montant, conducteur, station, commentaire) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (vehicule_id, user_id, now_iso(), compteur, litres, prix_unitaire, montant,
         conducteur, station, commentaire),
    )
    conn.execute(
        "INSERT INTO charges_logistique (vehicule_id, user_id, horodatage, categorie, "
        "montant, origine, commentaire) VALUES (?,?,?,?,?,?,?)",
        (vehicule_id, user_id, now_iso(), "Carburant", montant, "Carburant (auto)",
         f"{litres:.1f} L à {prix_unitaire:.0f} FCFA/L — {station or ''}".strip()),
    )
    conn.commit()
    conn.close()
    return montant


def lister_pleins_carburant(vehicule_id=None, limite=200):
    conn = get_connection()
    q = (
        "SELECT p.*, v.code AS vehicule_code, u.nom_complet FROM pleins_carburant p "
        "JOIN vehicules v ON v.id = p.vehicule_id JOIN users u ON u.id = p.user_id WHERE 1=1"
    )
    params = []
    if vehicule_id:
        q += " AND p.vehicule_id = ?"
        params.append(vehicule_id)
    q += " ORDER BY p.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def consommation_vehicule(vehicule_id, date_debut=None, date_fin=None):
    """Litres/jour, litres/tonne et coût carburant/tonne pour un véhicule
    sur une période, à comparer à une consommation standard (L/100km)
    saisie par l'utilisateur pour détecter une anomalie."""
    pleins = lister_pleins_carburant(vehicule_id=vehicule_id, limite=100000)
    if date_debut:
        pleins = [p for p in pleins if p["horodatage"] >= date_debut]
    if date_fin:
        pleins = [p for p in pleins if p["horodatage"] <= date_fin]
    litres_total = sum(p["litres"] for p in pleins)
    montant_total = sum(p["montant"] for p in pleins)

    missions = lister_missions(vehicule_id=vehicule_id, limite=100000)
    if date_debut:
        missions = [m for m in missions if m["horodatage"] >= date_debut]
    if date_fin:
        missions = [m for m in missions if m["horodatage"] <= date_fin]
    # Distance totale parcourue = distance du trajet x nombre de voyages
    # (approximation : suppose que "distance_km" saisie est déjà le
    # trajet aller-retour par voyage, ou à ajuster selon votre convention
    # de saisie).
    distance_total = sum((m["distance_km"] or 0) * (m["nombre_voyages"] or 0)
                          for m in missions)
    tonnage_total = sum(m["tonnage_total"] or 0 for m in missions)

    return {
        "litres_total": litres_total, "montant_total": montant_total,
        "distance_total_km": distance_total, "tonnage_total_t": tonnage_total,
        "litres_par_100km": (litres_total / distance_total * 100) if distance_total else None,
        "litres_par_tonne": (litres_total / tonnage_total) if tonnage_total else None,
        "cout_carburant_par_tonne": (montant_total / tonnage_total) if tonnage_total else None,
    }


def ajouter_maintenance(vehicule_id, user_id, type_intervention, compteur_heures,
                         compteur_km, description, cout, prochaine_echeance_heures):
    conn = get_connection()
    conn.execute(
        "INSERT INTO maintenances_flotte (vehicule_id, user_id, horodatage, "
        "type_intervention, compteur_heures, compteur_km, description, cout, "
        "prochaine_echeance_heures) VALUES (?,?,?,?,?,?,?,?,?)",
        (vehicule_id, user_id, now_iso(), type_intervention, compteur_heures, compteur_km,
         description, cout, prochaine_echeance_heures),
    )
    if cout:
        conn.execute(
            "INSERT INTO charges_logistique (vehicule_id, user_id, horodatage, categorie, "
            "montant, origine, commentaire) VALUES (?,?,?,?,?,?,?)",
            (vehicule_id, user_id, now_iso(), "Maintenance", cout, "Maintenance (auto)",
             f"{type_intervention} — {description or ''}".strip()),
        )
    if prochaine_echeance_heures is not None:
        conn.execute("UPDATE vehicules SET prochaine_maintenance_heures = ? WHERE id = ?",
                     (prochaine_echeance_heures, vehicule_id))
    if compteur_heures is not None or compteur_km is not None:
        if compteur_heures is not None:
            conn.execute("UPDATE vehicules SET compteur_heures = ? WHERE id = ?",
                         (compteur_heures, vehicule_id))
        if compteur_km is not None:
            conn.execute("UPDATE vehicules SET compteur_km = ? WHERE id = ?",
                         (compteur_km, vehicule_id))
    conn.commit()
    conn.close()


def lister_maintenances(vehicule_id=None, limite=200):
    conn = get_connection()
    q = (
        "SELECT m.*, v.code AS vehicule_code, u.nom_complet FROM maintenances_flotte m "
        "JOIN vehicules v ON v.id = m.vehicule_id JOIN users u ON u.id = m.user_id WHERE 1=1"
    )
    params = []
    if vehicule_id:
        q += " AND m.vehicule_id = ?"
        params.append(vehicule_id)
    q += " ORDER BY m.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ajouter_piece(code, designation, categorie, unite, stock_initial, seuil_alerte):
    conn = get_connection()
    conn.execute(
        "INSERT INTO pieces_stock (code, designation, categorie, unite, stock_actuel, "
        "seuil_alerte) VALUES (?,?,?,?,?,?)",
        (code, designation, categorie, unite, stock_initial, seuil_alerte),
    )
    conn.commit()
    conn.close()


def lister_pieces():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM pieces_stock ORDER BY categorie, designation").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mouvement_piece(piece_id, user_id, type_mouvement, quantite, vehicule_id, cout_unitaire,
                     commentaire):
    montant = (quantite * cout_unitaire) if cout_unitaire is not None else None
    conn = get_connection()
    conn.execute(
        "INSERT INTO mouvements_pieces (piece_id, user_id, horodatage, type_mouvement, "
        "quantite, vehicule_id, cout_unitaire, montant, commentaire) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (piece_id, user_id, now_iso(), type_mouvement, quantite, vehicule_id, cout_unitaire,
         montant, commentaire),
    )
    delta = quantite if type_mouvement == "Entrée" else -quantite
    conn.execute("UPDATE pieces_stock SET stock_actuel = stock_actuel + ? WHERE id = ?",
                 (delta, piece_id))

    if type_mouvement == "Sortie" and vehicule_id and montant:
        conn.execute(
            "INSERT INTO charges_logistique (vehicule_id, user_id, horodatage, categorie, "
            "montant, origine, commentaire) VALUES (?,?,?,?,?,?,?)",
            (vehicule_id, user_id, now_iso(), "Pièces", montant, "Pièces (auto)",
             (commentaire or "").strip()),
        )
    conn.commit()
    conn.close()


def lister_mouvements_pieces(piece_id=None, limite=200):
    conn = get_connection()
    q = (
        "SELECT mp.*, ps.designation, ps.code AS piece_code, u.nom_complet, "
        "v.code AS vehicule_code FROM mouvements_pieces mp "
        "JOIN pieces_stock ps ON ps.id = mp.piece_id JOIN users u ON u.id = mp.user_id "
        "LEFT JOIN vehicules v ON v.id = mp.vehicule_id WHERE 1=1"
    )
    params = []
    if piece_id:
        q += " AND mp.piece_id = ?"
        params.append(piece_id)
    q += " ORDER BY mp.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ajouter_charge_logistique(vehicule_id, user_id, categorie, montant, commentaire):
    """Charge logistique saisie manuellement (ex. personnel, autres coûts) —
    les charges Carburant/Maintenance/Pièces sont elles générées
    automatiquement par les fonctions correspondantes ci-dessus."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO charges_logistique (vehicule_id, user_id, horodatage, categorie, "
        "montant, origine, commentaire) VALUES (?,?,?,?,?,'Manuelle',?)",
        (vehicule_id, user_id, now_iso(), categorie, montant, commentaire),
    )
    conn.commit()
    conn.close()


def lister_charges_logistique(vehicule_id=None, limite=500):
    conn = get_connection()
    q = (
        "SELECT cl.*, v.code AS vehicule_code, u.nom_complet FROM charges_logistique cl "
        "JOIN vehicules v ON v.id = cl.vehicule_id JOIN users u ON u.id = cl.user_id WHERE 1=1"
    )
    params = []
    if vehicule_id:
        q += " AND cl.vehicule_id = ?"
        params.append(vehicule_id)
    q += " ORDER BY cl.horodatage DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cout_logistique_vehicule(vehicule_id, date_debut=None, date_fin=None):
    """Coût logistique total d'un véhicule sur une période (carburant +
    maintenance + pièces + personnel/autres charges manuelles), rapporté
    aux tonnes transportées (missions + tickets de pesée), pour obtenir un
    coût logistique par tonne — la même logique que le CMUP des postes de
    production, appliquée à un véhicule."""
    charges = lister_charges_logistique(vehicule_id=vehicule_id, limite=100000)
    if date_debut:
        charges = [c for c in charges if c["horodatage"] >= date_debut]
    if date_fin:
        charges = [c for c in charges if c["horodatage"] <= date_fin]
    par_categorie = {}
    total = 0.0
    for c in charges:
        par_categorie.setdefault(c["categorie"], 0.0)
        par_categorie[c["categorie"]] += c["montant"]
        total += c["montant"]

    missions = lister_missions(vehicule_id=vehicule_id, limite=100000)
    if date_debut:
        missions = [m for m in missions if m["horodatage"] >= date_debut]
    if date_fin:
        missions = [m for m in missions if m["horodatage"] <= date_fin]
    tonnage_missions = sum(m["tonnage_total"] or 0 for m in missions)

    tickets = lister_tickets_pesee(vehicule_id=vehicule_id, limite=100000)
    if date_debut:
        tickets = [t for t in tickets if t["horodatage"] >= date_debut]
    if date_fin:
        tickets = [t for t in tickets if t["horodatage"] <= date_fin]
    tonnage_tickets = sum(t["poids_net_t"] for t in tickets)

    tonnage_total = tonnage_missions + tonnage_tickets
    cout_par_tonne = (total / tonnage_total) if tonnage_total else None

    return {
        "total": total, "par_categorie": par_categorie, "tonnage_total_t": tonnage_total,
        "cout_par_tonne": cout_par_tonne,
    }


def transferer_cout_logistique(vehicule_id, poste_destination_id, user_id, date_debut,
                                date_fin=None):
    """Transfère le coût logistique par tonne d'un véhicule vers le
    centre de coût d'un poste de production, comme charge « Transport » —
    exactement le même principe que transferer_stock pour la matière
    entre deux postes de production."""
    cout = cout_logistique_vehicule(vehicule_id, date_debut, date_fin)
    if cout["cout_par_tonne"] is None:
        raise ValueError("Aucune tonne transportée sur cette période : impossible de "
                          "calculer un coût logistique par tonne.")
    vehicule = obtenir_vehicule(vehicule_id)
    montant = cout["total"]
    ajouter_charge(
        poste_destination_id, user_id, "Transport", montant,
        f"Coût logistique {vehicule['code']} — {cout['tonnage_total_t']:.2f} t à "
        f"{cout['cout_par_tonne']:.2f} FCFA/t"
    )
    return cout


def kpis_logistique_jour():
    aujourdhui = datetime.date.today().isoformat()
    conn = get_connection()

    flotte = conn.execute("SELECT statut, COUNT(*) AS n FROM vehicules GROUP BY statut") \
        .fetchall()
    flotte_par_statut = {r["statut"]: r["n"] for r in flotte}
    flotte_totale = sum(flotte_par_statut.values())

    tonnes_missions = conn.execute(
        "SELECT COALESCE(SUM(tonnage_total), 0) AS t FROM missions_transport "
        "WHERE horodatage >= ?", (aujourdhui,)
    ).fetchone()["t"]
    tonnes_tickets = conn.execute(
        "SELECT COALESCE(SUM(poids_net_t), 0) AS t FROM tickets_pesee WHERE horodatage >= ?",
        (aujourdhui,),
    ).fetchone()["t"]
    nombre_voyages = conn.execute(
        "SELECT COALESCE(SUM(nombre_voyages), 0) AS n FROM missions_transport "
        "WHERE horodatage >= ?", (aujourdhui,)
    ).fetchone()["n"]
    litres_jour = conn.execute(
        "SELECT COALESCE(SUM(litres), 0) AS l FROM pleins_carburant WHERE horodatage >= ?",
        (aujourdhui,),
    ).fetchone()["l"]
    cout_carburant_jour = conn.execute(
        "SELECT COALESCE(SUM(montant), 0) AS m FROM pleins_carburant WHERE horodatage >= ?",
        (aujourdhui,),
    ).fetchone()["m"]
    pieces_sous_seuil = conn.execute(
        "SELECT COUNT(*) AS n FROM pieces_stock WHERE stock_actuel <= seuil_alerte"
    ).fetchone()["n"]

    conn.close()
    tonnes_jour = tonnes_missions + tonnes_tickets
    return {
        "flotte_totale": flotte_totale,
        "flotte_disponible": flotte_par_statut.get("Disponible", 0),
        "flotte_en_mission": flotte_par_statut.get("En mission", 0),
        "flotte_maintenance": flotte_par_statut.get("Maintenance", 0),
        "flotte_immobilisee": flotte_par_statut.get("Immobilisé", 0),
        "tonnes_transportees_jour": tonnes_jour,
        "nombre_voyages_jour": nombre_voyages,
        "litres_carburant_jour": litres_jour,
        "cout_carburant_jour": cout_carburant_jour,
        "cout_transport_par_tonne_jour": (cout_carburant_jour / tonnes_jour)
        if tonnes_jour else None,
        "pieces_sous_seuil": pieces_sous_seuil,
    }
