# -*- coding: utf-8 -*-
"""Onglet Coûts d'exploitation.

Réalise la liaison :
    Processus industriel (poste) -> Centre de coût -> Mouvement matière
    (productions déjà saisies dans l'onglet Production & bilan matière)
    -> Coût de production -> Écriture comptable (plan comptable SYSCOHADA).

Les charges (matière, énergie, réactifs, main-d'œuvre, maintenance) sont
saisies ici par poste ; chacune est automatiquement rattachée à un compte
SYSCOHADA de la classe 6 (voir data_plan_comptable.py). Le coût de revient
est calculé en rapportant le total des charges d'une période à la masse du
flux de sortie choisi (issu du bilan matière déjà calculé dans l'onglet
Production). L'écriture comptable générée valorise ce coût dans le compte
de stock/en-cours (classe 3) du poste, en contrepartie du compte 736
"Variation des stocks de biens et de services produits".
"""

import tkinter as tk
import datetime
from tkinter import ttk, messagebox

import db
from data_postes import POSTES_REF
from ui_widgets import rendre_defilant as _rendre_defilant

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 10)
ACCENT = "#2f6f4f"

CATEGORIES_CHARGE = ["Matière", "Énergie", "Réactifs", "Main-d'œuvre", "Maintenance", "Amortissement", "Autre"]
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
                 "(matière, énergie, réactifs, main-d'œuvre, maintenance) par poste — chacune "
                 "est rattachée automatiquement à un compte du plan comptable SYSCOHADA — puis "
                 "calculez le coût de revient sur une période et générez l'écriture comptable.",
            font=FONT_BASE, wraplength=860,
        ).pack(anchor="w", pady=(2, 8))
        ttk.Button(self, text="Voir le plan comptable lié à la production",
                   command=self._voir_plan_comptable).pack(anchor="w", pady=(0, 10))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self._onglet_referentiel(notebook)
        self._onglet_saisie(notebook)
        self._onglet_calcul(notebook)
        self._onglet_stocks(notebook)

    def _voir_plan_comptable(self):
        from data_plan_comptable import COMPTES_CHARGES, COMPTES_STOCKS, \
            COMPTE_CONTREPARTIE_STOCK

        fenetre = tk.Toplevel(self)
        fenetre.title("Plan comptable lié à la production (SYSCOHADA)")
        fenetre.geometry("760x520")

        ttk.Label(
            fenetre, text="Plan comptable lié à la production", font=FONT_H2, foreground=ACCENT
        ).pack(anchor="w", padx=12, pady=(12, 4))
        ttk.Label(
            fenetre,
            text="Comptes réellement utilisés par le module Coûts d'exploitation, d'après "
                 "les catégories de charges et les centres de coût du référentiel.",
            font=FONT_BASE, wraplength=720,
        ).pack(anchor="w", padx=12, pady=(0, 10))

        cols = ("numero", "libelle", "type")
        tree = ttk.Treeview(fenetre, columns=cols, show="headings", height=20)
        tree.heading("numero", text="N° compte")
        tree.heading("libelle", text="Libellé")
        tree.heading("type", text="Type")
        tree.column("numero", width=90, anchor="w")
        tree.column("libelle", width=470, anchor="w")
        tree.column("type", width=150, anchor="w")
        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        vues = set()
        for categorie, compte in sorted(COMPTES_CHARGES.items(), key=lambda kv: kv[1]["numero"]):
            cle = (compte["numero"], compte["libelle"])
            if cle in vues:
                continue
            vues.add(cle)
            tree.insert("", "end", values=(compte["numero"], compte["libelle"],
                                            f"Charge (classe 6) — {categorie}"))

        vues = set()
        for libelle_stock, compte in sorted(COMPTES_STOCKS.items(),
                                             key=lambda kv: kv[1]["numero"]):
            cle = (compte["numero"], compte["libelle"])
            if cle in vues:
                continue
            vues.add(cle)
            tree.insert("", "end", values=(compte["numero"], compte["libelle"],
                                            "Stock / en-cours (classe 3)"))

        tree.insert("", "end", values=(
            COMPTE_CONTREPARTIE_STOCK["numero"], COMPTE_CONTREPARTIE_STOCK["libelle"],
            "Contrepartie (classe 7)"
        ))

        ttk.Button(fenetre, text="Fermer", command=fenetre.destroy).pack(pady=(0, 12))

    # -----------------------------------------------------------------
    # Sous-onglet : référentiel des centres de coût
    # -----------------------------------------------------------------
    def _onglet_referentiel(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Référentiel des centres de coût")
        frame = _rendre_defilant(page)

        cols = ("poste_id", "poste_titre", "code_centre", "stock_entree", "stock_sortie",
                "compte_stock_sortie", "methode_cout")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        largeurs = (60, 170, 90, 110, 130, 230, 90)
        for c, w in zip(cols, largeurs):
            tree.heading(c, text=c.replace("_", " ").capitalize())
            tree.column(c, width=w, anchor="w")
        tree.pack(fill="both", expand=True)

        from data_plan_comptable import compte_stock
        for c in db.lister_centres_cout():
            cs = compte_stock(c["stock_sortie"])
            tree.insert("", "end", values=(
                c["poste_id"], c["poste_titre"], c["code_centre"], c["stock_entree"],
                c["stock_sortie"], f"{cs['numero']} — {cs['libelle']}", c["methode_cout"]
            ))

    # -----------------------------------------------------------------
    # Sous-onglet : saisie des charges
    # -----------------------------------------------------------------
    def _onglet_saisie(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Saisie des charges")
        frame = _rendre_defilant(page)

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
        categorie_combo = ttk.Combobox(
            form, textvariable=self.categorie_var, state="readonly", width=20, font=FONT_BASE,
            values=CATEGORIES_CHARGE
        )
        categorie_combo.grid(row=1, column=1, pady=4, sticky="w")

        self.compte_apercu_var = tk.StringVar()
        ttk.Label(form, textvariable=self.compte_apercu_var, font=FONT_BASE,
                  foreground="#666666").grid(row=1, column=2, sticky="w", padx=(12, 0))

        from data_plan_comptable import compte_charge

        def _maj_apercu_compte(*_):
            cpt = compte_charge(self.categorie_var.get())
            self.compte_apercu_var.set(f"→ compte {cpt['numero']} ({cpt['libelle']})")

        self.categorie_var.trace_add("write", _maj_apercu_compte)
        _maj_apercu_compte()

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
        cols = ("horodatage", "poste_titre", "categorie", "compte_num", "montant",
                "nom_complet")
        self.tree_charges = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c, w in zip(cols, (140, 160, 90, 80, 100, 140)):
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
                values=(c["horodatage"], c["poste_titre"], c["categorie"], c["compte_num"],
                        f"{c['montant']:.0f}", c["nom_complet"])
            )

    # -----------------------------------------------------------------
    # Sous-onglet : coût de revient & écriture comptable
    # -----------------------------------------------------------------
    def _onglet_calcul(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Coût de revient & écriture comptable")
        frame = _rendre_defilant(page)

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
            frame, height=13, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
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

        ttk.Label(frame, text="Dernière écriture générée (détail des lignes)", font=FONT_H2).pack(
            anchor="w", pady=(14, 4)
        )
        self.detail_ecriture = tk.Text(
            frame, height=8, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
        )
        self.detail_ecriture.pack(fill="both", expand=True)
        self.detail_ecriture.configure(state="disabled")

        ttk.Label(frame, text="Historique des écritures comptables", font=FONT_H2).pack(
            anchor="w", pady=(14, 4)
        )
        cols = ("horodatage", "poste_titre", "code_centre", "montant_total", "flux_reference",
                "masse_reference_t", "cout_unitaire_t", "compte_stock_num")
        self.tree_ecritures = ttk.Treeview(frame, columns=cols, show="headings", height=7)
        largeurs = (140, 150, 80, 110, 100, 100, 100, 100)
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

    def _ecrire_detail_ecriture(self, texte):
        self.detail_ecriture.configure(state="normal")
        self.detail_ecriture.delete("1.0", "end")
        self.detail_ecriture.insert("end", texte)
        self.detail_ecriture.configure(state="disabled")

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
            f"Centre de coût : {centre['code_centre']}",
            f"Depuis le {date_debut}\n",
            "Charges par compte SYSCOHADA :",
        ]
        if not cout["par_compte"]:
            lignes.append("  (aucune charge saisie sur cette période)")
        for (compte_num, compte_libelle), montant in cout["par_compte"].items():
            lignes.append(
                f"  {compte_num:<6} {compte_libelle:<55} {montant:14,.0f} FCFA"
                .replace(",", " ")
            )
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

        lignes_txt = [
            f"ÉCRITURE COMPTABLE #{resultat['ecriture_id']} — {resultat['code_centre']}",
            f"{'Sens':<8}{'Compte':<8}{'Libellé':<55}{'Montant':>14}", "-" * 90,
        ]
        for sens, compte_num, compte_libelle, libelle_ligne, montant in resultat["lignes"]:
            lignes_txt.append(
                f"{sens:<8}{compte_num:<8}{compte_libelle:<55}{montant:14,.0f}"
                .replace(",", " ")
            )
        self._ecrire_detail_ecriture("\n".join(lignes_txt))

        detail_unitaire = (
            f"{resultat['cout_unitaire_t']:.2f} FCFA/t (sur {resultat['masse_reference_t']:.2f} t)"
            if resultat["cout_unitaire_t"] is not None
            else "non calculable (pas de masse pour ce flux sur la période)"
        )
        messagebox.showinfo(
            "Écriture générée",
            f"Écriture comptable #{resultat['ecriture_id']} enregistrée pour "
            f"{resultat['code_centre']} :\n"
            f"Montant total : {resultat['total']:.0f} FCFA\n"
            f"Coût unitaire : {detail_unitaire}\n\n"
            f"Le détail des lignes (comptes SYSCOHADA) est affiché ci-dessous."
        )

    # -----------------------------------------------------------------
    # Sous-onglet : niveau des stocks par circuit
    # -----------------------------------------------------------------
    def _onglet_stocks(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Niveau des stocks par circuit")
        frame = _rendre_defilant(page)

        ttk.Label(
            frame,
            text="Pour chaque circuit (poste), masse entrée (flux « Alimentation ») et masse "
                 "sortie, qui comprend à la fois la production propre du poste (concentré, "
                 "stérile/rejet, produit fini) ET la matière transférée vers un poste aval "
                 "(saisie comme « Alimentation » avec un poste d'origine, dans Production & "
                 "bilan matière) — c'est ce qui fait diminuer le stock d'un poste quand le "
                 "poste suivant produit à partir de lui. Le solde est débiteur (normal) s'il "
                 "est positif ou nul, créditeur (à vérifier) s'il est négatif. La valeur du "
                 "solde utilise le dernier coût unitaire à la tonne (CMUP) calculé pour ce "
                 "poste, quand il est disponible.",
            font=FONT_BASE, wraplength=860,
        ).pack(anchor="w", pady=(0, 8))

        filtre_frame = ttk.Frame(frame)
        filtre_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(filtre_frame, text="Depuis (AAAA-MM-JJ, vide = tout l'historique) :",
                  font=FONT_BASE).pack(side="left", padx=(0, 8))
        self.stocks_date_debut_var = tk.StringVar()
        ttk.Entry(filtre_frame, textvariable=self.stocks_date_debut_var, width=14,
                  font=FONT_BASE).pack(side="left", padx=(0, 8))
        ttk.Button(filtre_frame, text="Actualiser",
                   command=self._rafraichir_stocks).pack(side="left")

        cols = ("poste_titre", "code_centre", "entrees_t", "sorties_propres_t",
                "sorties_transferees_t", "sorties_t", "solde_t", "sens", "cout_unitaire_t",
                "valeur_solde")
        self.tree_stocks = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        entetes = ("Poste", "Centre", "Entrées (t)", "Sorties propres (t)",
                   "dont transférées vers l'aval (t)", "Sorties totales (t)", "Solde (t)",
                   "Sens", "CMUP (FCFA/t)", "Valeur du solde (FCFA)")
        largeurs = (160, 70, 90, 110, 190, 100, 90, 90, 110, 150)
        for c, txt, w in zip(cols, entetes, largeurs):
            self.tree_stocks.heading(c, text=txt)
            self.tree_stocks.column(c, width=w, anchor="w")
        self.tree_stocks.tag_configure("crediteur", foreground="#b00020")
        self.tree_stocks.pack(fill="both", expand=True)

        self._rafraichir_stocks()

    def _rafraichir_stocks(self):
        for row in self.tree_stocks.get_children():
            self.tree_stocks.delete(row)
        date_debut = self.stocks_date_debut_var.get().strip() or None
        for s in db.niveaux_stocks(date_debut=date_debut):
            tag = "crediteur" if s["sens"] == "Créditeur" else ""
            self.tree_stocks.insert(
                "", "end", tags=(tag,),
                values=(
                    s["poste_titre"], s["code_centre"], f"{s['entrees_t']:.2f}",
                    f"{s['sorties_propres_t']:.2f}", f"{s['sorties_transferees_t']:.2f}",
                    f"{s['sorties_t']:.2f}", f"{s['solde_t']:.2f}", s["sens"],
                    f"{s['cout_unitaire_t']:.2f}" if s["cout_unitaire_t"] is not None else "—",
                    f"{s['valeur_solde']:,.0f}".replace(",", " ")
                    if s["valeur_solde"] is not None else "—",
                )
            )

    def _rafraichir_ecritures(self):
        for row in self.tree_ecritures.get_children():
            self.tree_ecritures.delete(row)
        for e in db.lister_ecritures_comptables(limite=100):
            self.tree_ecritures.insert(
                "", "end",
                values=(
                    e["horodatage"], e["poste_titre"], e["code_centre"],
                    f"{e['montant_total']:.0f}", e["flux_reference"] or "",
                    f"{e['masse_reference_t']:.2f}" if e["masse_reference_t"] is not None
                    else "",
                    f"{e['cout_unitaire_t']:.2f}" if e["cout_unitaire_t"] is not None else "",
                    e["compte_stock_num"] or "",
                )
            )
