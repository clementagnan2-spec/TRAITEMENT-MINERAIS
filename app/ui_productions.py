# -*- coding: utf-8 -*-
"""Saisie des productions réelles (masses, teneurs) et bilan matière calculé
à partir de ces données — par opposition au calculateur pédagogique de
l'onglet Formation, qui fonctionne sur des valeurs saisies librement."""

import tkinter as tk
import datetime
from tkinter import ttk, messagebox

import db
from data_postes import POSTES_REF

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 10)
ACCENT = "#2f6f4f"

TYPES_FLUX = ["Alimentation", "Concentré", "Stérile / rejet", "Produit fini"]


class OngletProductions(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user

        ttk.Label(self, text="Production réelle & bilan matière", font=FONT_TITLE,
                  foreground=ACCENT).pack(anchor="w")
        ttk.Label(
            self,
            text="Enregistrez les masses et teneurs réelles mesurées à chaque poste. Le "
                 "bilan matière ci-dessous est calculé automatiquement à partir de ces "
                 "données, sur la période choisie.",
            font=FONT_BASE, wraplength=820,
        ).pack(anchor="w", pady=(2, 14))

        # --- Formulaire de saisie ---
        form = ttk.LabelFrame(self, text="Nouvelle saisie de production", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Poste / circuit :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.poste_var = tk.StringVar()
        ttk.Combobox(
            form, textvariable=self.poste_var, state="readonly", width=42, font=FONT_BASE,
            values=[f"{p['id']} — {p['titre']}" for p in POSTES_REF]
        ).grid(row=0, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Type de flux :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.flux_var = tk.StringVar(value=TYPES_FLUX[0])
        flux_combo = ttk.Combobox(
            form, textvariable=self.flux_var, state="readonly", width=20, font=FONT_BASE,
            values=TYPES_FLUX
        )
        flux_combo.grid(row=1, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Poste d'origine (transfert de stock) :", font=FONT_BASE).grid(
            row=1, column=2, sticky="w", padx=(20, 8)
        )
        self.SANS_ORIGINE = "(Aucun — apport externe)"
        self.poste_origine_var = tk.StringVar(value=self.SANS_ORIGINE)
        self.poste_origine_combo = ttk.Combobox(
            form, textvariable=self.poste_origine_var, state="readonly", width=32,
            font=FONT_BASE,
            values=[self.SANS_ORIGINE] + [f"{p['id']} — {p['titre']}" for p in POSTES_REF]
        )
        self.poste_origine_combo.grid(row=1, column=3, pady=4, sticky="w")

        def _maj_etat_origine(*_):
            if self.flux_var.get() == "Alimentation":
                self.poste_origine_combo.configure(state="readonly")
            else:
                self.poste_origine_var.set(self.SANS_ORIGINE)
                self.poste_origine_combo.configure(state="disabled")

        self.flux_var.trace_add("write", _maj_etat_origine)
        _maj_etat_origine()

        ttk.Label(form, text="Masse (tonnes) :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.masse_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.masse_var, width=15, font=FONT_BASE).grid(
            row=2, column=1, pady=4, sticky="w"
        )

        ttk.Label(form, text="Teneur (%) — optionnel :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.teneur_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.teneur_var, width=15, font=FONT_BASE).grid(
            row=3, column=1, pady=4, sticky="w"
        )

        ttk.Label(form, text="Commentaire :", font=FONT_BASE).grid(
            row=4, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.commentaire_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.commentaire_var, width=42, font=FONT_BASE).grid(
            row=4, column=1, pady=4, sticky="w"
        )

        ttk.Button(form, text="Enregistrer la production", command=self._enregistrer).grid(
            row=5, column=1, sticky="w", pady=10
        )

        # --- Bilan matière calculé ---
        bilan_frame = ttk.LabelFrame(self, text="Bilan matière calculé (période)", padding=12)
        bilan_frame.pack(fill="both", expand=True, pady=(14, 0))

        periode_frame = ttk.Frame(bilan_frame)
        periode_frame.pack(anchor="w", pady=(0, 8))
        ttk.Label(periode_frame, text="Poste :", font=FONT_BASE).pack(side="left")
        self.bilan_poste_var = tk.StringVar()
        ttk.Combobox(
            periode_frame, textvariable=self.bilan_poste_var, state="readonly", width=35,
            font=FONT_BASE, values=[f"{p['id']} — {p['titre']}" for p in POSTES_REF]
        ).pack(side="left", padx=(4, 16))

        ttk.Label(periode_frame, text="Depuis (AAAA-MM-JJ) :", font=FONT_BASE).pack(side="left")
        self.date_debut_var = tk.StringVar(
            value=(datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        )
        ttk.Entry(periode_frame, textvariable=self.date_debut_var, width=12, font=FONT_BASE).pack(
            side="left", padx=(4, 16)
        )

        ttk.Button(periode_frame, text="Calculer le bilan", command=self._calculer_bilan).pack(
            side="left"
        )

        self.resultat = tk.Text(
            bilan_frame, height=10, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
        )
        self.resultat.pack(fill="both", expand=True)
        self.resultat.configure(state="disabled")

        # --- Historique récent ---
        ttk.Label(self, text="Dernières saisies", font=FONT_H2).pack(anchor="w", pady=(14, 4))
        cols = ("horodatage", "poste_titre", "type_flux", "masse_tonnes", "teneur_pct",
                "nom_complet")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c, w in zip(cols, (140, 170, 120, 90, 80, 140)):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self._rafraichir_historique()

    def _enregistrer(self):
        if not self.poste_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un poste.")
            return
        try:
            masse = float(self.masse_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "La masse doit être un nombre.")
            return
        teneur = None
        if self.teneur_var.get().strip():
            try:
                teneur = float(self.teneur_var.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erreur", "La teneur doit être un nombre.")
                return

        poste_id = self.poste_var.get().split(" — ")[0]

        origine_txt = self.poste_origine_var.get()
        if self.flux_var.get() == "Alimentation" and origine_txt not in ("", self.SANS_ORIGINE):
            poste_origine_id = origine_txt.split(" — ")[0]
            if poste_origine_id == poste_id:
                messagebox.showerror("Erreur", "Le poste d'origine doit être différent du "
                                                "poste de destination.")
                return
            cmup = db.transferer_stock(poste_origine_id, poste_id, self.current_user["id"],
                                        masse, teneur, self.commentaire_var.get().strip())
            db.log_audit(
                self.current_user["id"], "Transfert de stock",
                f"{poste_origine_id} -> {poste_id} / {masse} t"
                + (f" @ {cmup:.2f} FCFA/t" if cmup is not None else " (CMUP inconnu)")
            )
            if cmup is not None:
                messagebox.showinfo(
                    "Enregistré",
                    f"Transfert enregistré : {masse:.2f} t de {poste_origine_id} vers "
                    f"{poste_id}.\nCharge « Matière » créée automatiquement chez {poste_id} : "
                    f"{masse * cmup:,.0f} FCFA (à {cmup:.2f} FCFA/t, CMUP de "
                    f"{poste_origine_id}).".replace(",", " ")
                )
            else:
                messagebox.showinfo(
                    "Enregistré",
                    f"Transfert enregistré : {masse:.2f} t de {poste_origine_id} vers "
                    f"{poste_id}.\nAucun CMUP n'est encore connu pour {poste_origine_id} "
                    "(générez d'abord une écriture comptable pour ce poste) : aucune charge "
                    "« Matière » n'a été créée automatiquement — vous pouvez la saisir "
                    "manuellement dans Coûts d'exploitation."
                )
        else:
            db.ajouter_production(poste_id, self.current_user["id"], self.flux_var.get(),
                                   masse, teneur, self.commentaire_var.get().strip())
            db.log_audit(self.current_user["id"], "Ajout production",
                          f"{poste_id} / {self.flux_var.get()} / {masse} t")
            messagebox.showinfo("Enregistré", "Production enregistrée avec succès.")

        self.masse_var.set("")
        self.teneur_var.set("")
        self.commentaire_var.set("")
        self._rafraichir_historique()

    def _ecrire_bilan(self, texte):
        self.resultat.configure(state="normal")
        self.resultat.delete("1.0", "end")
        self.resultat.insert("end", texte)
        self.resultat.configure(state="disabled")

    def _calculer_bilan(self):
        if not self.bilan_poste_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un poste pour le bilan.")
            return
        poste_id = self.bilan_poste_var.get().split(" — ")[0]
        date_debut = self.date_debut_var.get().strip()

        resultat = db.bilan_matiere_periode(poste_id, date_debut, None)
        if not resultat:
            self._ecrire_bilan(
                "Aucune donnée de production enregistrée pour ce poste sur cette période.\n"
                "Saisissez des productions ci-dessus (Alimentation, Concentré, Stérile/rejet) "
                "pour voir apparaître un bilan."
            )
            return

        lignes = [f"BILAN MATIÈRE — {self.bilan_poste_var.get()}",
                  f"Depuis le {date_debut}\n", ""]
        for flux, agg in resultat.items():
            teneur_txt = f"{agg['teneur_moyenne_pct']:.3f} %" if agg["teneur_moyenne_pct"] \
                is not None else "n/d"
            lignes.append(
                f"{flux:<18} masse = {agg['masse_totale_t']:10.2f} t   "
                f"teneur moy. = {teneur_txt:>10}   métal = {agg['metal_total_t']:8.3f} t"
            )

        alim = resultat.get("Alimentation")
        conc = resultat.get("Concentré")
        sterile = resultat.get("Stérile / rejet")
        if alim and conc and alim["masse_totale_t"] > 0:
            y = conc["masse_totale_t"] / alim["masse_totale_t"] * 100
            lignes.append("")
            lignes.append(f"Rendement massique observé (concentré/alimentation) : Y = "
                           f"{y:.2f} %")
            if alim["teneur_moyenne_pct"] and alim["teneur_moyenne_pct"] > 0 and \
                    conc["teneur_moyenne_pct"] is not None:
                r = y * conc["teneur_moyenne_pct"] / alim["teneur_moyenne_pct"]
                lignes.append(f"Récupération métallurgique observée : R = {r:.2f} %")
            if alim["metal_total_t"] > 0:
                fermeture = (conc["metal_total_t"] + (sterile["metal_total_t"] if sterile
                             else 0)) / alim["metal_total_t"] * 100
                lignes.append(f"Fermeture du bilan métal (conc.+stérile / alim.) : "
                              f"{fermeture:.1f} % (proche de 100 % attendu ; un écart "
                              f"important indique des données manquantes ou des erreurs de "
                              f"mesure/échantillonnage)")

        self._ecrire_bilan("\n".join(lignes))

    def _rafraichir_historique(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in db.lister_productions(limite=100):
            self.tree.insert(
                "", "end",
                values=(p["horodatage"], p["poste_titre"], p["type_flux"], p["masse_tonnes"],
                        p["teneur_pct"] if p["teneur_pct"] is not None else "", p["nom_complet"])
            )
