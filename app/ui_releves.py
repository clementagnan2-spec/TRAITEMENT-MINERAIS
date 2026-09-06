# -*- coding: utf-8 -*-
"""Saisie et consultation des relevés de paramètres d'exploitation réels."""

import tkinter as tk
from tkinter import ttk, messagebox

import db
from data_postes import POSTES_REF

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_BASE = ("Segoe UI", 10)
ACCENT = "#2f6f4f"

POSTES_PAR_ID = {p["id"]: p for p in POSTES_REF}


class OngletReleves(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user

        ttk.Label(self, text="Relevés d'exploitation", font=FONT_TITLE, foreground=ACCENT).pack(
            anchor="w"
        )
        ttk.Label(
            self,
            text="Saisissez un relevé de paramètre réel pour un poste. Chaque relevé est "
                 "horodaté et associé à votre compte.",
            font=FONT_BASE,
        ).pack(anchor="w", pady=(2, 14))

        form = ttk.Frame(self)
        form.pack(anchor="w", fill="x")

        ttk.Label(form, text="Poste / circuit :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.poste_var = tk.StringVar()
        self.poste_combo = ttk.Combobox(
            form, textvariable=self.poste_var, state="readonly", width=45, font=FONT_BASE,
            values=[f"{p['id']} — {p['titre']}" for p in POSTES_REF]
        )
        self.poste_combo.grid(row=0, column=1, pady=4, sticky="w")
        self.poste_combo.bind("<<ComboboxSelected>>", lambda e: self._maj_parametres())

        ttk.Label(form, text="Paramètre :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.param_var = tk.StringVar()
        self.param_combo = ttk.Combobox(
            form, textvariable=self.param_var, state="readonly", width=45, font=FONT_BASE
        )
        self.param_combo.grid(row=1, column=1, pady=4, sticky="w")
        self.param_combo.bind("<<ComboboxSelected>>", lambda e: self._maj_unite())

        ttk.Label(form, text="Valeur :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        val_frame = ttk.Frame(form)
        val_frame.grid(row=2, column=1, sticky="w", pady=4)
        self.valeur_var = tk.StringVar()
        ttk.Entry(val_frame, textvariable=self.valeur_var, width=15, font=FONT_BASE).pack(
            side="left"
        )
        self.unite_label = ttk.Label(val_frame, text="", font=FONT_BASE)
        self.unite_label.pack(side="left", padx=(8, 0))

        ttk.Label(form, text="Commentaire (optionnel) :", font=FONT_BASE).grid(
            row=3, column=0, sticky="nw", padx=(0, 8), pady=4
        )
        self.commentaire_txt = tk.Text(form, height=3, width=45, font=FONT_BASE)
        self.commentaire_txt.grid(row=3, column=1, pady=4, sticky="w")

        ttk.Button(self, text="Enregistrer le relevé", command=self._enregistrer).pack(
            anchor="w", pady=14
        )

        ttk.Separator(self).pack(fill="x", pady=6)
        filtre_frame = ttk.Frame(self)
        filtre_frame.pack(anchor="w", fill="x")
        ttk.Label(filtre_frame, text="Historique — filtrer par poste :", font=FONT_BASE).pack(
            side="left"
        )
        self.filtre_var = tk.StringVar(value="Tous")
        filtre_combo = ttk.Combobox(
            filtre_frame, textvariable=self.filtre_var, state="readonly", width=40,
            font=FONT_BASE,
            values=["Tous"] + [f"{p['id']} — {p['titre']}" for p in POSTES_REF]
        )
        filtre_combo.pack(side="left", padx=8)
        filtre_combo.bind("<<ComboboxSelected>>", lambda e: self._rafraichir_historique())

        cols = ("horodatage", "poste_titre", "parametre", "valeur", "unite", "nom_complet")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        largeurs = (140, 190, 200, 80, 60, 150)
        for c, w in zip(cols, largeurs):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=(8, 0))

        self._rafraichir_historique()

    def _maj_parametres(self):
        poste_id = self.poste_var.get().split(" — ")[0]
        poste = POSTES_PAR_ID.get(poste_id)
        if poste:
            noms = [p[0] for p in poste["parametres"]]
            self.param_combo.configure(values=noms)
            self.param_var.set("")
            self.unite_label.configure(text="")

    def _maj_unite(self):
        poste_id = self.poste_var.get().split(" — ")[0]
        poste = POSTES_PAR_ID.get(poste_id)
        if not poste:
            return
        for nom, unite in poste["parametres"]:
            if nom == self.param_var.get():
                self.unite_label.configure(text=unite)
                return

    def _enregistrer(self):
        if not self.poste_var.get() or not self.param_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un poste et un paramètre.")
            return
        try:
            valeur = float(self.valeur_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "La valeur doit être un nombre.")
            return

        poste_id = self.poste_var.get().split(" — ")[0]
        commentaire = self.commentaire_txt.get("1.0", "end").strip()
        unite = self.unite_label.cget("text")

        db.ajouter_releve(poste_id, self.current_user["id"], self.param_var.get(), valeur,
                           unite, commentaire)
        db.log_audit(self.current_user["id"], "Ajout relevé",
                      f"{poste_id} / {self.param_var.get()} = {valeur}")

        self.valeur_var.set("")
        self.commentaire_txt.delete("1.0", "end")
        self._rafraichir_historique()
        messagebox.showinfo("Enregistré", "Relevé enregistré avec succès.")

    def _rafraichir_historique(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        choix = self.filtre_var.get()
        poste_id = None if choix == "Tous" else choix.split(" — ")[0]
        for r in db.lister_releves(poste_id=poste_id, limite=200):
            self.tree.insert(
                "", "end",
                values=(r["horodatage"], r["poste_titre"], r["parametre"], r["valeur"],
                        r["unite"] or "", r["nom_complet"])
            )
