# -*- coding: utf-8 -*-
"""Registre de consignation (LOTO) et checklists HSE signées."""

import json
import tkinter as tk
from tkinter import ttk, messagebox

import db
from data_mine_types import postes_pour_type
from data_formation import SECURITE_HSE

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BASE = ("Segoe UI", 10)
ACCENT = "#2f6f4f"
ALERTE = "#a6371f"


class OngletSecuriteOps(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user

        ttk.Label(self, text="Sécurité — Consignation (LOTO) et checklist HSE",
                  font=FONT_TITLE, foreground=ACCENT).pack(anchor="w")
        ttk.Label(
            self,
            text="Registre réel des consignations d'équipement et des checklists de "
                 "sécurité signées par les opérateurs.",
            font=FONT_BASE,
        ).pack(anchor="w", pady=(2, 14))

        sous_notebook = ttk.Notebook(self)
        sous_notebook.pack(fill="both", expand=True)

        sous_notebook.add(_OngletLoto(sous_notebook, current_user), text="Consignation (LOTO)")
        sous_notebook.add(_OngletChecklist(sous_notebook, current_user),
                           text="Checklist HSE signée")


class _OngletLoto(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=12)
        self.current_user = current_user
        self.postes_ref = postes_pour_type(db.get_type_mine())

        form = ttk.LabelFrame(self, text="Verrouiller un équipement", padding=12)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Équipement :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.equipement_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.equipement_var, width=35, font=FONT_BASE).grid(
            row=0, column=1, pady=4, sticky="w"
        )

        ttk.Label(form, text="Poste / circuit :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.poste_var = tk.StringVar()
        ttk.Combobox(
            form, textvariable=self.poste_var, state="readonly", width=32, font=FONT_BASE,
            values=["—"] + [f"{p['id']} — {p['titre']}" for p in self.postes_ref]
        ).grid(row=1, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Motif :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.motif_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.motif_var, width=35, font=FONT_BASE).grid(
            row=2, column=1, pady=4, sticky="w"
        )

        ttk.Button(form, text="Verrouiller (consigner)", command=self._verrouiller).grid(
            row=3, column=1, sticky="w", pady=10
        )

        cols = ("id", "equipement", "poste_titre", "verrouille_par_nom",
                "horodatage_verrouillage", "statut", "deverrouille_par_nom",
                "horodatage_deverrouillage")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        largeurs = (36, 150, 140, 120, 130, 100, 120, 130)
        for c, w in zip(cols, largeurs):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=(6, 6))

        ttk.Button(self, text="Déverrouiller l'équipement sélectionné",
                   command=self._deverrouiller).pack(anchor="w")

        self._rafraichir()

    def _verrouiller(self):
        equip = self.equipement_var.get().strip()
        if not equip:
            messagebox.showerror("Erreur", "Indiquez le nom de l'équipement.")
            return
        choix = self.poste_var.get()
        poste_id = None if choix in ("", "—") else choix.split(" — ")[0]

        db.verrouiller_equipement(equip, poste_id, self.current_user["id"],
                                   self.motif_var.get().strip())
        db.log_audit(self.current_user["id"], "Consignation LOTO", equip)

        self.equipement_var.set("")
        self.motif_var.set("")
        self._rafraichir()
        messagebox.showinfo("Consigné", f"« {equip} » est maintenant verrouillé (LOTO).")

    def _deverrouiller(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez un équipement dans la liste.")
            return
        valeurs = self.tree.item(sel[0])["values"]
        loto_id, statut = valeurs[0], valeurs[5]
        if statut == "Déverrouillé":
            messagebox.showinfo("Déjà déverrouillé", "Cet équipement est déjà déverrouillé.")
            return
        if not messagebox.askyesno(
            "Confirmation",
            "Confirmez-vous que l'équipement est physiquement sécurisé pour le "
            "déverrouillage ? Cette action doit suivre la procédure de déconsignation."
        ):
            return
        db.deverrouiller_equipement(loto_id, self.current_user["id"])
        db.log_audit(self.current_user["id"], "Déconsignation LOTO", f"id={loto_id}")
        self._rafraichir()

    def _rafraichir(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for l in db.lister_loto():
            self.tree.insert(
                "", "end",
                values=(l["id"], l["equipement"], l["poste_titre"] or "—",
                        l["verrouille_par_nom"], l["horodatage_verrouillage"], l["statut"],
                        l["deverrouille_par_nom"] or "—", l["horodatage_deverrouillage"] or "—")
            )


class _OngletChecklist(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=12)
        self.current_user = current_user
        self.vars_points = []

        ttk.Label(
            self,
            text="Cochez chaque point vérifié, puis signez pour horodater et enregistrer "
                 "la checklist.",
            font=FONT_BASE, wraplength=780,
        ).pack(anchor="w", pady=(0, 8))

        cadre = ttk.LabelFrame(self, text="Points de sécurité", padding=10)
        cadre.pack(fill="x")
        for titre, detail in SECURITE_HSE:
            var = tk.BooleanVar()
            self.vars_points.append((titre, var))
            ttk.Checkbutton(cadre, text=titre, variable=var).pack(anchor="w", pady=2)

        sig_frame = ttk.Frame(self)
        sig_frame.pack(fill="x", pady=10)
        ttk.Label(sig_frame, text=f"Signature ({self.current_user['nom_complet']}) — "
                                   f"tapez votre nom complet pour confirmer :",
                  font=FONT_BASE).pack(anchor="w")
        self.signature_var = tk.StringVar()
        ttk.Entry(sig_frame, textvariable=self.signature_var, width=40, font=FONT_BASE).pack(
            anchor="w", pady=4
        )
        ttk.Button(sig_frame, text="Enregistrer la checklist signée",
                   command=self._enregistrer).pack(anchor="w", pady=6)

        ttk.Label(self, text="Historique des checklists signées", font=FONT_H2).pack(
            anchor="w", pady=(14, 4)
        )
        cols = ("horodatage", "nom_complet", "signature", "points_valides")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c, w in zip(cols, (140, 150, 150, 120)):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self._rafraichir()

    def _enregistrer(self):
        signature = self.signature_var.get().strip()
        if not signature:
            messagebox.showerror("Erreur", "Veuillez signer (taper votre nom complet).")
            return
        if signature.lower() != self.current_user["nom_complet"].lower():
            if not messagebox.askyesno(
                "Vérification",
                f"La signature saisie (« {signature} ») ne correspond pas exactement à "
                f"votre nom de compte (« {self.current_user['nom_complet']} »). "
                f"Continuer quand même ?"
            ):
                return

        points = {titre: var.get() for titre, var in self.vars_points}
        non_coches = [t for t, v in points.items() if not v]
        if non_coches and not messagebox.askyesno(
            "Points non cochés",
            "Certains points ne sont pas cochés :\n- " + "\n- ".join(non_coches) +
            "\n\nEnregistrer quand même ?"
        ):
            return

        db.enregistrer_checklist_hse(self.current_user["id"], None, json.dumps(points,
                                      ensure_ascii=False), signature)
        db.log_audit(self.current_user["id"], "Checklist HSE signée", signature)

        for _, var in self.vars_points:
            var.set(False)
        self.signature_var.set("")
        self._rafraichir()
        messagebox.showinfo("Enregistré", "Checklist HSE enregistrée et horodatée.")

    def _rafraichir(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for c in db.lister_checklist_hse():
            points = json.loads(c["points_json"])
            nb_ok = sum(1 for v in points.values() if v)
            self.tree.insert(
                "", "end",
                values=(c["horodatage"], c["nom_complet"], c["signature"],
                        f"{nb_ok} / {len(points)}")
            )
