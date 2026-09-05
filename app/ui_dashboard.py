# -*- coding: utf-8 -*-
"""Tableau de bord — indicateurs clés du jour."""

import tkinter as tk
from tkinter import ttk

import db

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_KPI = ("Segoe UI", 26, "bold")
ACCENT = "#2f6f4f"
ALERTE = "#a6371f"


class OngletTableauDeBord(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user

        entete = ttk.Frame(self)
        entete.pack(fill="x")
        ttk.Label(entete, text="Tableau de bord", font=FONT_TITLE, foreground=ACCENT).pack(
            side="left"
        )
        ttk.Button(entete, text="Actualiser", command=self._rafraichir).pack(side="right")

        self.cartes_frame = ttk.Frame(self)
        self.cartes_frame.pack(fill="x", pady=20)

        self.derniers_incidents_label = ttk.Label(
            self, text="Derniers incidents ouverts", font=FONT_H2
        )
        self.derniers_incidents_label.pack(anchor="w", pady=(10, 4))

        cols = ("horodatage", "poste_titre", "gravite", "declare_par", "description")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=8)
        for c, w in zip(cols, (140, 160, 90, 140, 320)):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)

        self._rafraichir()

    def _carte(self, parent, titre, valeur, couleur=ACCENT):
        cadre = ttk.Frame(parent, padding=14, relief="solid", borderwidth=1)
        ttk.Label(cadre, text=titre, font=FONT_BASE).pack(anchor="w")
        ttk.Label(cadre, text=str(valeur), font=FONT_KPI, foreground=couleur).pack(anchor="w")
        return cadre

    def _rafraichir(self):
        for w in self.cartes_frame.winfo_children():
            w.destroy()

        kpis = db.kpis_du_jour()
        cartes = [
            ("Tonnage alimenté aujourd'hui (t)", f"{kpis['tonnage_alimentation_jour']:.1f}",
             ACCENT),
            ("Incidents ouverts", kpis["incidents_ouverts"],
             ALERTE if kpis["incidents_ouverts"] > 0 else ACCENT),
            ("Consignations (LOTO) actives", kpis["loto_actifs"],
             ALERTE if kpis["loto_actifs"] > 0 else ACCENT),
            ("Relevés saisis aujourd'hui", kpis["releves_jour"], ACCENT),
            ("Affectations planifiées aujourd'hui", kpis["equipes_planifiees_jour"], ACCENT),
        ]
        for i, (titre, valeur, couleur) in enumerate(cartes):
            carte = self._carte(self.cartes_frame, titre, valeur, couleur)
            carte.grid(row=0, column=i, padx=6, sticky="nsew")
            self.cartes_frame.columnconfigure(i, weight=1)

        for row in self.tree.get_children():
            self.tree.delete(row)
        for inc in db.lister_incidents(limite=15):
            if inc["statut"] == "Résolu":
                continue
            self.tree.insert(
                "", "end",
                values=(inc["horodatage"], inc["poste_titre"] or "—", inc["gravite"],
                        inc["declare_par"], inc["description"][:80])
            )
