# -*- coding: utf-8 -*-
"""Gestion des affectations d'équipe par poste et par quart."""

import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import db
from data_mine_types import postes_pour_type

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_BASE = ("Segoe UI", 10)
ACCENT = "#2f6f4f"

QUARTS = ["Matin", "Après-midi", "Nuit"]
STATUTS = ["Planifiée", "En cours", "Terminée", "Absence"]


class OngletEquipes(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user
        self.postes_ref = postes_pour_type(db.get_type_mine())

        ttk.Label(self, text="Gestion des équipes — affectations", font=FONT_TITLE,
                  foreground=ACCENT).pack(anchor="w")
        ttk.Label(
            self,
            text="Planifiez qui est affecté à quel poste, pour quel quart et quel jour.",
            font=FONT_BASE,
        ).pack(anchor="w", pady=(2, 14))

        form = ttk.LabelFrame(self, text="Nouvelle affectation", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Collaborateur :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(form, textvariable=self.user_var, state="readonly",
                                        width=32, font=FONT_BASE)
        self.user_combo.grid(row=0, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Poste / circuit :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.poste_var = tk.StringVar()
        ttk.Combobox(
            form, textvariable=self.poste_var, state="readonly", width=32, font=FONT_BASE,
            values=[f"{p['id']} — {p['titre']}" for p in self.postes_ref]
        ).grid(row=1, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Date (AAAA-MM-JJ) :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.date_var = tk.StringVar(value=datetime.date.today().isoformat())
        ttk.Entry(form, textvariable=self.date_var, width=16, font=FONT_BASE).grid(
            row=2, column=1, pady=4, sticky="w"
        )

        ttk.Label(form, text="Quart :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.quart_var = tk.StringVar(value=QUARTS[0])
        ttk.Combobox(
            form, textvariable=self.quart_var, state="readonly", width=16, font=FONT_BASE,
            values=QUARTS
        ).grid(row=3, column=1, pady=4, sticky="w")

        ttk.Button(form, text="Créer l'affectation", command=self._creer).grid(
            row=4, column=1, sticky="w", pady=10
        )

        filtre_frame = ttk.Frame(self)
        filtre_frame.pack(fill="x", pady=(14, 4))
        ttk.Label(filtre_frame, text="Voir le planning du (AAAA-MM-JJ) :", font=FONT_BASE).pack(
            side="left"
        )
        self.filtre_date_var = tk.StringVar(value=datetime.date.today().isoformat())
        ttk.Entry(filtre_frame, textvariable=self.filtre_date_var, width=14,
                  font=FONT_BASE).pack(side="left", padx=8)
        ttk.Button(filtre_frame, text="Afficher", command=self._rafraichir).pack(side="left")
        ttk.Button(filtre_frame, text="Voir tout l'historique",
                   command=lambda: self._rafraichir(tout=True)).pack(side="left", padx=8)

        cols = ("id", "date_jour", "quart", "poste_titre", "nom_complet", "statut")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c, w in zip(cols, (40, 100, 100, 180, 150, 100)):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=(6, 6))

        statut_frame = ttk.Frame(self)
        statut_frame.pack(anchor="w")
        ttk.Label(statut_frame, text="Changer le statut de l'affectation sélectionnée :",
                  font=FONT_BASE).pack(side="left")
        self.nouveau_statut_var = tk.StringVar(value=STATUTS[0])
        ttk.Combobox(
            statut_frame, textvariable=self.nouveau_statut_var, state="readonly", width=14,
            font=FONT_BASE, values=STATUTS
        ).pack(side="left", padx=8)
        ttk.Button(statut_frame, text="Appliquer", command=self._changer_statut).pack(
            side="left"
        )

        self.rafraichir_utilisateurs()
        self._rafraichir()

    def rafraichir_utilisateurs(self):
        users = db.lister_utilisateurs(actifs_seulement=True)
        self._users_par_label = {f"{u['nom_complet']} ({u['role']})": u["id"] for u in users}
        self.user_combo.configure(values=list(self._users_par_label.keys()))

    def _creer(self):
        if not self.user_var.get() or not self.poste_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un collaborateur et un poste.")
            return
        user_id = self._users_par_label.get(self.user_var.get())
        poste_id = self.poste_var.get().split(" — ")[0]

        db.creer_affectation(user_id, poste_id, self.date_var.get().strip(),
                              self.quart_var.get())
        db.log_audit(self.current_user["id"], "Création affectation",
                      f"{self.user_var.get()} / {poste_id} / {self.date_var.get()}")
        self._rafraichir()
        messagebox.showinfo("Créé", "Affectation créée.")

    def _changer_statut(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez une affectation dans la liste.")
            return
        affectation_id = self.tree.item(sel[0])["values"][0]
        db.maj_statut_affectation(affectation_id, self.nouveau_statut_var.get())
        self._rafraichir()

    def _rafraichir(self, tout=False):
        for row in self.tree.get_children():
            self.tree.delete(row)
        date_jour = None if tout else self.filtre_date_var.get().strip()
        for a in db.lister_affectations(date_jour=date_jour):
            self.tree.insert(
                "", "end",
                values=(a["id"], a["date_jour"], a["quart"], a["poste_titre"],
                        a["nom_complet"], a["statut"])
            )
