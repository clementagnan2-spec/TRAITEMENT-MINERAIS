# -*- coding: utf-8 -*-
"""Onglet Coûts d'exploitation.

Réalise la liaison :
    Processus industriel (poste) -> Centre de coût -> Mouvement matière
    (productions déjà saisies dans l'onglet Production & bilan matière)
    -> Coût de production -> Écriture comptable.

Les charges (matière, énergie, réactifs, main-d'œuvre, maintenance) sont
saisies ici par poste. Le coût de revient est calculé en rapportant le
total des charges d'une période à la masse du flux de sortie choisi (issu
du bilan matière déjà calculé dans l'onglet Production). L'écriture
comptable générée fige ce calcul (montant, centre de coût, compte de
charge, coût unitaire) pour traçabilité.
"""

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

CATEGORIES_CHARGE = ["Matière", "Énergie", "Réactifs", "Main-d'œuvre", "Maintenance", "Autre"]
TYPES_FLUX = ["Alimentation", "Concentré", "Stérile / rejet", "Produit fini"]


class OngletCoutsExploitation(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user
        self._dernier_bilan_poste = None

        ttk.Label(self, text="Coûts d'exploitation", font=FONT_TITLE,
                  foreground=ACCENT).pack(anchor="w")
        ttk.Label(
            self,
            text="Chaque poste est relié à un centre de coût. Saisissez ici les charges "
                 "(matière, énergie, réactifs, main-d'œuvre, maintenance) par poste, puis "
                 "calculez le coût de revient sur une période à partir du bilan matière et "
                 "générez l'écriture comptable correspondante.",
            font=FONT_BASE, wraplength=860,
        ).pack(anchor="w", pady=(2, 14))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self._onglet_referentiel(notebook)
        self._onglet_saisie(notebook)
        self._onglet_calcul(notebook)

    # -----------------------------------------------------------------
    # Sous-onglet : référentiel des centres de coût
    # -----------------------------------------------------------------
    def _onglet_referentiel(self, notebook):
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Référentiel des centres de coût")

        cols = ("poste_id", "poste_titre", "code_centre", "compte_charge", "stock_entree",
                "stock_sortie", "methode_cout")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        largeurs = (60, 170, 90, 150, 110, 130, 90)
        for c, w in zip(cols, largeurs):
            tree.heading(c, text=c.replace("_", " ").capitalize())
            tree.column(c, width=w, anchor="w")
        tree.pack(fill="both", expand=True)

        for c in db.lister_centres_cout():
            tree.insert("", "end", values=(c["poste_id"], c["poste_titre"], c["code_centre"],
                                            c["compte_charge"], c["stock_entree"],
                                            c["stock_sortie"], c["methode_cout"]))

    # -----------------------------------------------------------------
    # Sous-onglet : saisie des charges
    # -----------------------------------------------------------------
    def _onglet_saisie(self, notebook):
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Saisie des charges")

        form = ttk.LabelFrame(frame, text="Nouvelle charge d'exploitation", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Poste / centre de coût :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.charge_poste_var = tk.StringVar()
        ttk.Combobox(
            form, textvariable=self.charge_poste_var, state="readonly", width=42,
            font=FONT_BASE, values=[f"{p['id']} — {p['titre']}" for p in POSTES_REF]
        ).grid(row=0, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Catégorie :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.categorie_var = tk.StringVar(value=CATEGORIES_CHARGE[0])
        ttk.Combobox(
            form, textvariable=self.categorie_var, state="readonly", width=20, font=FONT_BASE,
            values=CATEGORIES_CHARGE
        ).grid(row=1, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Montant (FCFA) :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.montant_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.montant_var, width=18, font=FONT_BASE).grid(
            row=2, column=1, pady=4, sticky="w"
        )

        ttk.Label(form, text="Commentaire :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.charge_commentaire_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.charge_commentaire_var, width=42,
                  font=FONT_BASE).grid(row=3, column=1, pady=4, sticky="w")

        ttk.Button(form, text="Enregistrer la charge", command=self._enregistrer_charge).grid(
            row=4, column=1, sticky="w", pady=10
        )

        ttk.Label(frame, text="Dernières charges saisies", font=FONT_H2).pack(
            anchor="w", pady=(14, 4)
        )
        cols = ("horodatage", "poste_titre", "categorie", "montant", "nom_complet",
                "commentaire")
        self.tree_charges = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c, w in zip(cols, (140, 170, 100, 100, 140, 200)):
            self.tree_charges.heading(c, text=c.replace("_", " ").capitalize())
            self.tree_charges.column(c, width=w, anchor="w")
        self.tree_charges.pack(fill="both", expand=True)

        self._rafraichir_charges()

    def _enregistrer_charge(self):
        if not self.charge_poste_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un poste.")
            return
        try:
            montant = float(self.montant_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Le montant doit être un nombre.")
            return

        poste_id = self.charge_poste_var.get().split(" — ")[0]
        db.ajouter_charge(poste_id, self.current_user["id"], self.categorie_var.get(), montant,
                           self.charge_commentaire_var.get().strip())
        db.log_audit(self.current_user["id"], "Ajout charge d'exploitation",
                      f"{poste_id} / {self.categorie_var.get()} / {montant} FCFA")

        self.montant_var.set("")
        self.charge_commentaire_var.set("")
        self._rafraichir_charges()
        messagebox.showinfo("Enregistré", "Charge enregistrée avec succès.")

    def _rafraichir_charges(self):
        for row in self.tree_charges.get_children():
            self.tree_charges.delete(row)
        for c in db.lister_charges(limite=100):
            self.tree_charges.insert(
                "", "end",
                values=(c["horodatage"], c["poste_titre"], c["categorie"],
                        f"{c['montant']:.0f}", c["nom_complet"], c["commentaire"] or "")
            )

    # -----------------------------------------------------------------
    # Sous-onglet : coût de revient & écriture comptable
    # -----------------------------------------------------------------
    def _onglet_calcul(self, notebook):
        frame = ttk.Frame(notebook, padding=12)
        notebook.add(frame, text="Coût de revient & écriture comptable")

        periode_frame = ttk.LabelFrame(frame, text="Période de calcul", padding=12)
        periode_frame.pack(fill="x")

        ttk.Label(periode_frame, text="Poste :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.calc_poste_var = tk.StringVar()
        ttk.Combobox(
            periode_frame, textvariable=self.calc_poste_var, state="readonly", width=42,
            font=FONT_BASE, values=[f"{p['id']} — {p['titre']}" for p in POSTES_REF]
        ).grid(row=0, column=1, pady=4, sticky="w")

        ttk.Label(periode_frame, text="Depuis (AAAA-MM-JJ) :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.calc_date_debut_var = tk.StringVar(
            value=(datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        )
        ttk.Entry(periode_frame, textvariable=self.calc_date_debut_var, width=14,
                  font=FONT_BASE).grid(row=1, column=1, pady=4, sticky="w")

        ttk.Button(periode_frame, text="Calculer le coût", command=self._calculer_cout).grid(
            row=2, column=1, sticky="w", pady=8
        )

        self.resultat = tk.Text(
            frame, height=11, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
        )
        self.resultat.pack(fill="both", expand=True, pady=(10, 10))
        self.resultat.configure(state="disabled")

        generer_frame = ttk.LabelFrame(frame, text="Générer l'écriture comptable", padding=12)
        generer_frame.pack(fill="x")

        ttk.Label(generer_frame, text="Flux de sortie de référence :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.flux_ref_var = tk.StringVar()
        self.flux_ref_combo = ttk.Combobox(
            generer_frame, textvariable=self.flux_ref_var, state="readonly", width=20,
            font=FONT_BASE, values=TYPES_FLUX
        )
        self.flux_ref_combo.grid(row=0, column=1, sticky="w")

        ttk.Button(generer_frame, text="Générer l'écriture comptable",
                   command=self._generer_ecriture).grid(row=0, column=2, padx=(16, 0))

        ttk.Label(frame, text="Écritures comptables générées", font=FONT_H2).pack(
            anchor="w", pady=(14, 4)
        )
        cols = ("horodatage", "poste_titre", "code_centre", "compte_charge", "montant_total",
                "flux_reference", "masse_reference_t", "cout_unitaire_t")
        self.tree_ecritures = ttk.Treeview(frame, columns=cols, show="headings", height=7)
        largeurs = (140, 160, 80, 140, 110, 100, 110, 110)
        for c, w in zip(cols, largeurs):
            self.tree_ecritures.heading(c, text=c.replace("_", " ").capitalize())
            self.tree_ecritures.column(c, width=w, anchor="w")
        self.tree_ecritures.pack(fill="both", expand=True)

        self._rafraichir_ecritures()

    def _ecrire_resultat(self, texte):
        self.resultat.configure(state="normal")
        self.resultat.delete("1.0", "end")
        self.resultat.insert("end", texte)
        self.resultat.configure(state="disabled")

    def _calculer_cout(self):
        if not self.calc_poste_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un poste.")
            return
        poste_id = self.calc_poste_var.get().split(" — ")[0]
        date_debut = self.calc_date_debut_var.get().strip()

        centre = db.obtenir_centre_cout(poste_id)
        if centre is None:
            messagebox.showerror(
                "Erreur", "Aucun centre de coût n'est défini pour ce poste dans le "
                          "référentiel (data_centres_cout.py)."
            )
            return

        cout = db.cout_centre_periode(poste_id, date_debut, None)
        bilan = db.bilan_matiere_periode(poste_id, date_debut, None)

        lignes = [
            f"COÛT DE PRODUCTION — {self.calc_poste_var.get()}",
            f"Centre de coût : {centre['code_centre']}   —   Compte de charge : "
            f"{centre['compte_charge']}",
            f"Depuis le {date_debut}\n",
            "Charges par catégorie :",
        ]
        if not cout["par_categorie"]:
            lignes.append("  (aucune charge saisie sur cette période)")
        for categorie, montant in cout["par_categorie"].items():
            lignes.append(f"  {categorie:<14} {montant:14,.0f} FCFA".replace(",", " "))
        lignes.append(f"\nCoût total du centre {centre['code_centre']} : "
                       f"{cout['total']:,.0f} FCFA".replace(",", " "))

        lignes.append("\nBilan matière disponible sur la période (pour le coût unitaire) :")
        if not bilan:
            lignes.append("  (aucune production saisie sur cette période pour ce poste)")
            self.flux_ref_combo.configure(values=TYPES_FLUX)
        else:
            for flux, agg in bilan.items():
                lignes.append(f"  {flux:<18} masse = {agg['masse_totale_t']:.2f} t")
            self.flux_ref_combo.configure(values=list(bilan.keys()))
            defaut = centre.get("flux_sortie_defaut")
            if defaut in bilan:
                self.flux_ref_var.set(defaut)
            else:
                self.flux_ref_var.set(list(bilan.keys())[0])

        self._ecrire_resultat("\n".join(lignes))
        self._dernier_bilan_poste = poste_id

    def _generer_ecriture(self):
        if not self.calc_poste_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un poste et calculez le coût d'abord.")
            return
        poste_id = self.calc_poste_var.get().split(" — ")[0]
        if poste_id != self._dernier_bilan_poste:
            messagebox.showerror(
                "Erreur", "Cliquez d'abord sur \u00ab Calculer le coût \u00bb pour ce poste "
                          "et cette période."
            )
            return

        date_debut = self.calc_date_debut_var.get().strip()
        flux_reference = self.flux_ref_var.get() or None

        try:
            resultat = db.generer_ecriture_comptable(
                poste_id, date_debut, None, flux_reference, self.current_user["id"]
            )
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        db.log_audit(
            self.current_user["id"], "Génération écriture comptable",
            f"{poste_id} / {resultat['code_centre']} / {resultat['total']:.0f} FCFA"
        )
        self._rafraichir_ecritures()

        detail_unitaire = (
            f"{resultat['cout_unitaire_t']:.2f} FCFA/t (sur {resultat['masse_reference_t']:.2f} t)"
            if resultat["cout_unitaire_t"] is not None
            else "non calculable (pas de masse pour ce flux sur la période)"
        )
        messagebox.showinfo(
            "Écriture générée",
            f"Écriture comptable enregistrée pour {resultat['code_centre']} "
            f"({resultat['compte_charge']}) :\n"
            f"Montant total : {resultat['total']:.0f} FCFA\n"
            f"Coût unitaire : {detail_unitaire}"
        )

    def _rafraichir_ecritures(self):
        for row in self.tree_ecritures.get_children():
            self.tree_ecritures.delete(row)
        for e in db.lister_ecritures_comptables(limite=100):
            self.tree_ecritures.insert(
                "", "end",
                values=(
                    e["horodatage"], e["poste_titre"], e["code_centre"], e["compte_charge"],
                    f"{e['montant_total']:.0f}", e["flux_reference"] or "",
                    f"{e['masse_reference_t']:.2f}" if e["masse_reference_t"] is not None
                    else "",
                    f"{e['cout_unitaire_t']:.2f}" if e["cout_unitaire_t"] is not None else "",
                )
            )
