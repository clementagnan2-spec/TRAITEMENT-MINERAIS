# -*- coding: utf-8 -*-
"""Journal des incidents/anomalies avec suivi de résolution."""

import tkinter as tk
from tkinter import ttk, messagebox

import db
from data_mine_types import postes_pour_type

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_BASE = ("Segoe UI", 10)
ACCENT = "#2f6f4f"

GRAVITES = ["Mineure", "Modérée", "Majeure", "Critique"]
PEUT_RESOUDRE = {"admin", "superviseur", "chef_de_poste"}


class OngletIncidents(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user
        self.postes_ref = postes_pour_type(db.get_type_mine())

        ttk.Label(self, text="Journal des incidents / anomalies", font=FONT_TITLE,
                  foreground=ACCENT).pack(anchor="w")
        ttk.Label(
            self,
            text="Tout collaborateur peut déclarer un incident. La résolution est réservée "
                 "aux chefs de poste, superviseurs et administrateurs.",
            font=FONT_BASE,
        ).pack(anchor="w", pady=(2, 14))

        form = ttk.LabelFrame(self, text="Déclarer un incident", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Poste concerné (optionnel) :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.poste_var = tk.StringVar()
        ttk.Combobox(
            form, textvariable=self.poste_var, state="readonly", width=42, font=FONT_BASE,
            values=["—"] + [f"{p['id']} — {p['titre']}" for p in self.postes_ref]
        ).grid(row=0, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Gravité :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.gravite_var = tk.StringVar(value=GRAVITES[0])
        ttk.Combobox(
            form, textvariable=self.gravite_var, state="readonly", width=20, font=FONT_BASE,
            values=GRAVITES
        ).grid(row=1, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Description :", font=FONT_BASE).grid(
            row=2, column=0, sticky="nw", padx=(0, 8), pady=4
        )
        self.description_txt = tk.Text(form, height=4, width=55, font=FONT_BASE)
        self.description_txt.grid(row=2, column=1, pady=4, sticky="w")

        ttk.Button(form, text="Déclarer l'incident", command=self._declarer).grid(
            row=3, column=1, sticky="w", pady=10
        )

        # --- Liste + résolution ---
        filtre_frame = ttk.Frame(self)
        filtre_frame.pack(fill="x", pady=(14, 4))
        ttk.Label(filtre_frame, text="Filtrer par statut :", font=FONT_BASE).pack(side="left")
        self.filtre_var = tk.StringVar(value="Tous")
        ttk.Combobox(
            filtre_frame, textvariable=self.filtre_var, state="readonly", width=20,
            font=FONT_BASE, values=["Tous", "Ouvert", "En cours de traitement", "Résolu"]
        ).pack(side="left", padx=8)
        ttk.Button(filtre_frame, text="Filtrer", command=self._rafraichir).pack(side="left")

        cols = ("id", "horodatage", "poste_titre", "gravite", "statut", "declare_par",
                "description")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        largeurs = (40, 140, 150, 90, 150, 130, 280)
        for c, w in zip(cols, largeurs):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)

        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", pady=8)
        if self.current_user["role"] in PEUT_RESOUDRE:
            ttk.Label(action_frame, text="Action corrective :", font=FONT_BASE).pack(
                side="left"
            )
            self.action_var = tk.StringVar()
            ttk.Entry(action_frame, textvariable=self.action_var, width=50, font=FONT_BASE).pack(
                side="left", padx=8
            )
            ttk.Button(action_frame, text="Marquer résolu",
                       command=self._marquer_resolu).pack(side="left", padx=4)
            ttk.Button(action_frame, text="Marquer en cours de traitement",
                       command=self._marquer_en_cours).pack(side="left", padx=4)
        else:
            ttk.Label(
                action_frame,
                text="Votre rôle ne permet pas de résoudre des incidents (réservé aux chefs "
                     "de poste, superviseurs et administrateurs).",
                font=FONT_BASE, foreground="#777777"
            ).pack(anchor="w")

        self._rafraichir()

    def _declarer(self):
        description = self.description_txt.get("1.0", "end").strip()
        if not description:
            messagebox.showerror("Erreur", "Veuillez décrire l'incident.")
            return
        choix = self.poste_var.get()
        poste_id = None if choix in ("", "—") else choix.split(" — ")[0]

        db.ajouter_incident(poste_id, self.current_user["id"], self.gravite_var.get(),
                             description)
        db.log_audit(self.current_user["id"], "Déclaration incident", description[:100])

        self.description_txt.delete("1.0", "end")
        self._rafraichir()
        messagebox.showinfo("Enregistré", "Incident déclaré. L'équipe d'encadrement est "
                                           "informée via le tableau de bord.")

    def _selection_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez d'abord un incident dans la liste.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def _marquer_resolu(self):
        incident_id = self._selection_id()
        if incident_id is None:
            return
        db.resoudre_incident(incident_id, self.current_user["id"], self.action_var.get())
        db.log_audit(self.current_user["id"], "Résolution incident", f"id={incident_id}")
        self.action_var.set("")
        self._rafraichir()

    def _marquer_en_cours(self):
        incident_id = self._selection_id()
        if incident_id is None:
            return
        db.maj_statut_incident(incident_id, "En cours de traitement")
        db.log_audit(self.current_user["id"], "Incident en cours", f"id={incident_id}")
        self._rafraichir()

    def _rafraichir(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        choix = self.filtre_var.get()
        statut = None if choix == "Tous" else choix
        for inc in db.lister_incidents(statut=statut, limite=300):
            self.tree.insert(
                "", "end",
                values=(inc["id"], inc["horodatage"], inc["poste_titre"] or "—",
                        inc["gravite"], inc["statut"], inc["declare_par"], inc["description"])
            )
