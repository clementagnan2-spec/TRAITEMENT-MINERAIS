# -*- coding: utf-8 -*-
"""Saisie et consultation des relevés de paramètres d'exploitation réels."""

import tkinter as tk
from tkinter import ttk, messagebox

import db
from data_postes import POSTES_REF, obtenir_bareme

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
ACCENT = "#2f6f4f"
ALERTE = "#a6371f"

POSTES_PAR_ID = {p["id"]: p for p in POSTES_REF}


def _formater_bareme(bareme):
    """Formate un couple (borne_min, borne_max) en texte lisible, ex.
    'norme : 50 – 150' ou 'norme : ≤ 8' ou 'norme : ≥ 99.0'."""
    if bareme is None:
        return ""
    borne_min, borne_max = bareme
    if borne_min is not None and borne_max is not None:
        return f"norme : {borne_min:g} – {borne_max:g}"
    if borne_min is not None:
        return f"norme : ≥ {borne_min:g}"
    if borne_max is not None:
        return f"norme : ≤ {borne_max:g}"
    return ""


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
        self.bareme_label = ttk.Label(val_frame, text="", font=FONT_SMALL, foreground="#666666")
        self.bareme_label.pack(side="left", padx=(12, 0))

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

        cols = ("horodatage", "poste_titre", "parametre", "valeur", "unite", "conformite",
                "nom_complet")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        entetes = {"conformite": "Conformité"}
        largeurs = (140, 190, 200, 80, 60, 100, 150)
        for c, w in zip(cols, largeurs):
            self.tree.heading(c, text=entetes.get(c, c.replace("_", " ").capitalize()))
            self.tree.column(c, width=w, anchor="w")
        self.tree.tag_configure("non_conforme", background="#fbe4e0", foreground=ALERTE)
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
            self.bareme_label.configure(text="")

    def _maj_unite(self):
        poste_id = self.poste_var.get().split(" — ")[0]
        poste = POSTES_PAR_ID.get(poste_id)
        if not poste:
            return
        for nom, unite in poste["parametres"]:
            if nom == self.param_var.get():
                self.unite_label.configure(text=unite)
                bareme = obtenir_bareme(poste_id, nom)
                self.bareme_label.configure(text=_formater_bareme(bareme))
                return
        self.bareme_label.configure(text="")

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
        parametre = self.param_var.get()
        commentaire = self.commentaire_txt.get("1.0", "end").strip()
        unite = self.unite_label.cget("text")

        resultat = db.ajouter_releve(poste_id, self.current_user["id"], parametre, valeur,
                                      unite, commentaire)
        db.log_audit(self.current_user["id"], "Ajout relevé",
                      f"{poste_id} / {parametre} = {valeur}")

        self.valeur_var.set("")
        self.commentaire_txt.delete("1.0", "end")
        self._rafraichir_historique()

        if resultat["conforme"] is False:
            db.log_audit(
                self.current_user["id"], "ALERTE non-conformité",
                f"{poste_id} / {parametre} = {valeur} {unite} "
                f"({_formater_bareme((resultat['borne_min'], resultat['borne_max']))})"
            )
            messagebox.showwarning(
                "⚠ Valeur hors norme",
                f"Le relevé a été enregistré, mais la valeur saisie est hors du "
                f"barème normal pour ce paramètre.\n\n"
                f"Poste : {poste_id} — {POSTES_PAR_ID[poste_id]['titre']}\n"
                f"Paramètre : {parametre}\n"
                f"Valeur saisie : {valeur:g} {unite}\n"
                f"{_formater_bareme((resultat['borne_min'], resultat['borne_max']))}"
            )
        else:
            messagebox.showinfo("Enregistré", "Relevé enregistré avec succès.")

    def _rafraichir_historique(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        choix = self.filtre_var.get()
        poste_id = None if choix == "Tous" else choix.split(" — ")[0]
        for r in db.lister_releves(poste_id=poste_id, limite=200):
            conforme = r["conforme"]
            if conforme is None:
                texte_conformite = "—"
                tags = ()
            elif conforme:
                texte_conformite = "✓ Conforme"
                tags = ()
            else:
                texte_conformite = "⚠ Non conforme"
                tags = ("non_conforme",)
            self.tree.insert(
                "", "end", tags=tags,
                values=(r["horodatage"], r["poste_titre"], r["parametre"], r["valeur"],
                        r["unite"] or "", texte_conformite, r["nom_complet"])
            )
