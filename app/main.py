# -*- coding: utf-8 -*-
"""
Gestion des opérations — Usine de traitement des minerais
============================================================
Application de gestion opérationnelle réelle pour une usine de traitement
de minerais : comptes utilisateurs avec rôles, relevés d'exploitation,
productions réelles et bilan matière calculé, incidents, sécurité
(consignation LOTO + checklists HSE signées), affectations d'équipe,
administration des comptes, et un onglet Formation reprenant les outils
pédagogiques (glossaire, quiz, calculateurs de simulation).

Toutes les données opérationnelles sont stockées de façon persistante dans
une base SQLite locale (fichier mine_ops.sqlite3, créé automatiquement à
côté de l'exécutable).

Lancer avec :  python main.py
"""

import tkinter as tk
from tkinter import ttk

import db
from data_postes import POSTES_REF
from ui_login import EcranConnexion, DialogueChangerMotDePasse
from ui_dashboard import OngletTableauDeBord
from ui_releves import OngletReleves
from ui_productions import OngletProductions
from ui_couts import OngletCouts
from ui_incidents import OngletIncidents
from ui_securite import OngletSecuriteOps
from ui_equipes import OngletEquipes
from ui_admin import OngletAdministration
from formation_ui import FormationFrame

APP_TITLE = "Gestion des opérations — Usine de traitement des minerais"
CREDIT_TEXTE = ("Logiciel à usage de formation développé par Tagnan Clément : "
                "clementagnan2@gmail.com")
BG = "#f4f6f5"
ACCENT = "#2f6f4f"
FONT_BASE = ("Segoe UI", 10)
FONT_TITLE = ("Segoe UI", 13, "bold")

ROLES_LABELS = {
    "operateur": "Opérateur",
    "chef_de_poste": "Chef de poste",
    "superviseur": "Superviseur",
    "admin": "Administrateur",
}

# Rôles autorisés à voir chaque onglet opérationnel (au-delà du tableau de
# bord, des relevés, des incidents et de la sécurité, ouverts à tous)
ROLES_PRODUCTIONS = {"chef_de_poste", "superviseur", "admin"}
ROLES_EQUIPES = {"chef_de_poste", "superviseur", "admin"}
ROLES_ADMIN = {"admin"}


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1050x720")
        self.minsize(860, 600)
        self.configure(bg=BG)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=BG, font=FONT_BASE)
        style.configure("TNotebook", background=BG)
        style.configure("TFrame", background=BG)
        style.configure("TCheckbutton", background=BG, font=FONT_BASE)
        style.configure("TLabelframe", background=BG)
        style.configure("TLabelframe.Label", background=BG, font=("Segoe UI", 10, "bold"))

        db.init_db(POSTES_REF)

        self.current_user = None

        credit = tk.Label(
            self, text=CREDIT_TEXTE, font=("Segoe UI", 8), bg="#2f6f4f", fg="#ffffff",
            pady=3
        )
        credit.pack(fill="x", side="top")

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self._afficher_connexion()

    def _afficher_connexion(self):
        for w in self.container.winfo_children():
            w.destroy()
        EcranConnexion(self.container, on_success=self._connexion_reussie).pack(
            fill="both", expand=True
        )

    def _connexion_reussie(self, user):
        self.current_user = user
        if user["doit_changer_mdp"]:
            dialog = DialogueChangerMotDePasse(self, user, obligatoire=True)
            self.wait_window(dialog)
            self.current_user["doit_changer_mdp"] = 0
        self._construire_application_principale()

    def _construire_application_principale(self):
        for w in self.container.winfo_children():
            w.destroy()

        entete = ttk.Frame(self.container, padding=(16, 12, 16, 4))
        entete.pack(fill="x")
        gauche = ttk.Frame(entete)
        gauche.pack(side="left")
        ttk.Label(gauche, text=APP_TITLE, font=FONT_TITLE, foreground=ACCENT).pack(anchor="w")
        role_label = ROLES_LABELS.get(self.current_user["role"], self.current_user["role"])
        ttk.Label(
            gauche,
            text=f"Connecté(e) : {self.current_user['nom_complet']}  —  Rôle : {role_label}",
            font=FONT_BASE,
        ).pack(anchor="w")

        droite = ttk.Frame(entete)
        droite.pack(side="right")
        ttk.Button(droite, text="Changer mon mot de passe",
                   command=self._changer_mon_mdp).pack(side="left", padx=(0, 8))
        ttk.Button(droite, text="Se déconnecter", command=self._deconnexion).pack(side="left")

        notebook = ttk.Notebook(self.container)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        role = self.current_user["role"]

        notebook.add(OngletTableauDeBord(notebook, self.current_user), text="  Tableau de bord  ")
        notebook.add(OngletReleves(notebook, self.current_user), text="  Relevés  ")

        if role in ROLES_PRODUCTIONS:
            notebook.add(OngletProductions(notebook, self.current_user),
                         text="  Production & bilan matière  ")
            notebook.add(OngletCouts(notebook, self.current_user),
                         text="  Coûts d'exploitation  ")

        notebook.add(OngletIncidents(notebook, self.current_user), text="  Incidents  ")
        notebook.add(OngletSecuriteOps(notebook, self.current_user), text="  Sécurité (LOTO/HSE)  ")

        if role in ROLES_EQUIPES:
            notebook.add(OngletEquipes(notebook, self.current_user), text="  Équipes  ")

        if role in ROLES_ADMIN:
            notebook.add(
                OngletAdministration(notebook, self.current_user,
                                      on_users_changed=self._construire_application_principale),
                text="  Administration  "
            )

        notebook.add(FormationFrame(notebook), text="  Formation  ")

    def _changer_mon_mdp(self):
        dialog = DialogueChangerMotDePasse(self, self.current_user, obligatoire=False)
        self.wait_window(dialog)

    def _deconnexion(self):
        db.log_audit(self.current_user["id"], "Déconnexion")
        self.current_user = None
        self._afficher_connexion()


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
