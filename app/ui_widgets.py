# -*- coding: utf-8 -*-
"""Petits composants d'interface partagés entre plusieurs onglets."""

import tkinter as tk
from tkinter import ttk


def rendre_defilant(parent):
    """Enveloppe le contenu d'un onglet dans un canvas avec ascenseur
    vertical, pour que rien ne soit coupé quel que soit le nombre de
    sections ou la taille de la fenêtre."""
    conteneur = ttk.Frame(parent)
    conteneur.pack(fill="both", expand=True)

    canvas = tk.Canvas(conteneur, highlightthickness=0, bg="#f4f6f5")
    scrollbar = ttk.Scrollbar(conteneur, orient="vertical", command=canvas.yview)
    interieur = ttk.Frame(canvas, padding=12)

    interieur.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    fenetre_id = canvas.create_window((0, 0), window=interieur, anchor="nw")
    canvas.bind(
        "<Configure>", lambda e: canvas.itemconfig(fenetre_id, width=e.width)
    )
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _molette(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _activer_molette(_event):
        canvas.bind_all("<MouseWheel>", _molette)

    def _desactiver_molette(_event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _activer_molette)
    canvas.bind("<Leave>", _desactiver_molette)
    return interieur
