# -*- coding: utf-8 -*-
"""Suivi des coûts d'exploitation (réactifs, main-d'œuvre, énergie,
maintenance) et calcul du coût par tonne traitée à partir des données de
production réelles. Complète l'onglet Production & bilan matière sans
remplacer un logiciel de comptabilité générale : ce n'est pas une
comptabilité officielle, seulement un suivi opérationnel des coûts."""

import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import db
from data_mine_types import postes_pour_type

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 10)
ACCENT = "#2f6f4f"

CATEGORIES = ["Réactifs", "Main-d'oeuvre", "Énergie", "Maintenance", "Autre"]


class OngletCouts(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user
        self.postes_ref = postes_pour_type(db.get_type_mine())

        ttk.Label(self, text="Coûts d'exploitation", font=FONT_TITLE, foreground=ACCENT).pack(
            anchor="w"
        )
        ttk.Label(
            self,
            text="Suivi des coûts réels (réactifs, main-d'œuvre, énergie, maintenance) et "
                 "calcul du coût par tonne traitée à partir des productions enregistrées. "
                 "Ce n'est pas une comptabilité officielle — pour vos états financiers, "
                 "utilisez votre logiciel de comptabilité habituel.",
            font=FONT_BASE, wraplength=820,
        ).pack(anchor="w", pady=(2, 14))

        # --- Formulaire de saisie ---
        form = ttk.LabelFrame(self, text="Enregistrer un coût", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Catégorie :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.categorie_var = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(
            form, textvariable=self.categorie_var, state="readonly", width=20, font=FONT_BASE,
            values=CATEGORIES
        ).grid(row=0, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Poste concerné (optionnel) :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.poste_var = tk.StringVar()
        ttk.Combobox(
            form, textvariable=self.poste_var, state="readonly", width=42, font=FONT_BASE,
            values=["—"] + [f"{p['id']} — {p['titre']}" for p in self.postes_ref]
        ).grid(row=1, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Montant :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        montant_frame = ttk.Frame(form)
        montant_frame.grid(row=2, column=1, sticky="w", pady=4)
        self.montant_var = tk.StringVar()
        ttk.Entry(montant_frame, textvariable=self.montant_var, width=16, font=FONT_BASE).pack(
            side="left"
        )
        self.devise_var = tk.StringVar(value="XOF")
        ttk.Entry(montant_frame, textvariable=self.devise_var, width=6, font=FONT_BASE).pack(
            side="left", padx=(6, 0)
        )

        ttk.Label(form, text="Description :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.description_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.description_var, width=42, font=FONT_BASE).grid(
            row=3, column=1, pady=4, sticky="w"
        )

        ttk.Button(form, text="Enregistrer le coût", command=self._enregistrer).grid(
            row=4, column=1, sticky="w", pady=10
        )

        # --- Synthèse / coût par tonne ---
        synth_frame = ttk.LabelFrame(self, text="Synthèse et coût par tonne", padding=12)
        synth_frame.pack(fill="both", expand=True, pady=(14, 0))

        periode_frame = ttk.Frame(synth_frame)
        periode_frame.pack(anchor="w", pady=(0, 8))
        ttk.Label(periode_frame, text="Poste (optionnel) :", font=FONT_BASE).pack(side="left")
        self.synth_poste_var = tk.StringVar()
        ttk.Combobox(
            periode_frame, textvariable=self.synth_poste_var, state="readonly", width=32,
            font=FONT_BASE, values=["Tous"] + [f"{p['id']} — {p['titre']}" for p in
                                                self.postes_ref]
        ).pack(side="left", padx=(4, 16))

        ttk.Label(periode_frame, text="Depuis (AAAA-MM-JJ) :", font=FONT_BASE).pack(side="left")
        self.date_debut_var = tk.StringVar(
            value=(datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        )
        ttk.Entry(periode_frame, textvariable=self.date_debut_var, width=12, font=FONT_BASE).pack(
            side="left", padx=(4, 16)
        )
        ttk.Button(periode_frame, text="Calculer", command=self._calculer_synthese).pack(
            side="left"
        )

        self.resultat = tk.Text(
            synth_frame, height=10, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
        )
        self.resultat.pack(fill="both", expand=True)
        self.resultat.configure(state="disabled")

        # --- Historique ---
        ttk.Label(self, text="Derniers coûts enregistrés", font=FONT_H2).pack(
            anchor="w", pady=(14, 4)
        )
        cols = ("horodatage", "categorie", "poste_titre", "montant", "devise", "nom_complet",
                "description")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        largeurs = (130, 100, 160, 90, 50, 130, 220)
        for c, w in zip(cols, largeurs):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self._rafraichir_historique()

    def _enregistrer(self):
        try:
            montant = float(self.montant_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Le montant doit être un nombre.")
            return
        if montant <= 0:
            messagebox.showerror("Erreur", "Le montant doit être positif.")
            return

        choix = self.poste_var.get()
        poste_id = None if choix in ("", "—") else choix.split(" — ")[0]
        devise = self.devise_var.get().strip() or "XOF"

        db.ajouter_cout(self.categorie_var.get(), poste_id, self.current_user["id"], montant,
                         devise, self.description_var.get().strip())
        db.log_audit(self.current_user["id"], "Ajout coût",
                      f"{self.categorie_var.get()} / {montant} {devise}")

        self.montant_var.set("")
        self.description_var.set("")
        self._rafraichir_historique()
        messagebox.showinfo("Enregistré", "Coût enregistré avec succès.")

    def _ecrire_synthese(self, texte):
        self.resultat.configure(state="normal")
        self.resultat.delete("1.0", "end")
        self.resultat.insert("end", texte)
        self.resultat.configure(state="disabled")

    def _calculer_synthese(self):
        choix = self.synth_poste_var.get()
        poste_id = None if choix in ("", "Tous") else choix.split(" — ")[0]
        date_debut = self.date_debut_var.get().strip()

        synth = db.synthese_couts_periode(date_debut, None, poste_id=poste_id)

        if synth["total"] == 0:
            self._ecrire_synthese(
                "Aucun coût enregistré pour cette période / ce poste.\nEnregistrez des "
                "coûts ci-dessus pour voir apparaître la synthèse."
            )
            return

        lignes = [f"SYNTHÈSE DES COÛTS — {choix or 'Tous les postes'}",
                  f"Depuis le {date_debut}\n", "Répartition par catégorie :"]
        for cat, montant in synth["par_categorie"].items():
            part = montant / synth["total"] * 100
            lignes.append(f"  {cat:<16} {montant:>14,.0f} {synth['devise']}   "
                          f"({part:5.1f} %)".replace(",", " "))

        lignes.append("")
        lignes.append(f"TOTAL DES COÛTS : {synth['total']:,.0f} {synth['devise']}".replace(
            ",", " "))
        lignes.append(f"Tonnage alimenté sur la période : {synth['tonnage_periode']:,.1f} t"
                      .replace(",", " "))

        if synth["cout_par_tonne"] is not None:
            lignes.append("")
            lignes.append(f"➜ COÛT PAR TONNE TRAITÉE : {synth['cout_par_tonne']:,.0f} "
                          f"{synth['devise']} / t".replace(",", " "))
        else:
            lignes.append("")
            lignes.append("Coût par tonne non calculable : aucune production "
                          "(Alimentation) enregistrée sur cette période pour ce poste. "
                          "Renseignez les productions réelles dans l'onglet « Production "
                          "& bilan matière ».")

        self._ecrire_synthese("\n".join(lignes))

    def _rafraichir_historique(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in db.lister_couts(limite=100):
            self.tree.insert(
                "", "end",
                values=(c["horodatage"], c["categorie"], c["poste_titre"] or "—",
                        f"{c['montant']:,.0f}".replace(",", " "), c["devise"],
                        c["nom_complet"], c["description"] or "")
            )
