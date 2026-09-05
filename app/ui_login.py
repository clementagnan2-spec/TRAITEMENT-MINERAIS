# -*- coding: utf-8 -*-
"""Écran de connexion et boîte de dialogue de changement de mot de passe."""

import tkinter as tk
from tkinter import ttk, messagebox

import db

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_BASE = ("Segoe UI", 10)
ACCENT = "#2f6f4f"


class EcranConnexion(ttk.Frame):
    """Affiché tant qu'aucun utilisateur n'est authentifié.
    Appelle on_success(user_dict) une fois la connexion validée."""

    def __init__(self, parent, on_success):
        super().__init__(parent, padding=40)
        self.on_success = on_success

        cadre = ttk.Frame(self)
        cadre.pack(expand=True)

        ttk.Label(cadre, text="Gestion des opérations — Usine de traitement",
                  font=FONT_TITLE, foreground=ACCENT).pack(pady=(0, 4))
        ttk.Label(cadre, text="Connexion", font=("Segoe UI", 12)).pack(pady=(0, 20))

        form = ttk.Frame(cadre)
        form.pack()

        ttk.Label(form, text="Identifiant :", font=FONT_BASE).grid(
            row=0, column=0, sticky="e", padx=6, pady=6
        )
        self.identifiant = tk.StringVar()
        ttk.Entry(form, textvariable=self.identifiant, font=FONT_BASE, width=26).grid(
            row=0, column=1, pady=6
        )

        ttk.Label(form, text="Mot de passe :", font=FONT_BASE).grid(
            row=1, column=0, sticky="e", padx=6, pady=6
        )
        self.mot_de_passe = tk.StringVar()
        entry_mdp = ttk.Entry(form, textvariable=self.mot_de_passe, font=FONT_BASE, width=26,
                               show="*")
        entry_mdp.grid(row=1, column=1, pady=6)
        entry_mdp.bind("<Return>", lambda e: self._connecter())

        ttk.Button(cadre, text="Se connecter", command=self._connecter).pack(pady=16)

        self.erreur = ttk.Label(cadre, text="", font=FONT_BASE, foreground="#a6371f")
        self.erreur.pack()

        ttk.Label(
            cadre,
            text="Compte par défaut à la première utilisation : admin / admin123\n"
                 "(changez ce mot de passe immédiatement après la première connexion)",
            font=("Segoe UI", 8), foreground="#777777", justify="center"
        ).pack(pady=(20, 0))

    def _connecter(self):
        identifiant = self.identifiant.get().strip()
        mdp = self.mot_de_passe.get()
        if not identifiant or not mdp:
            self.erreur.configure(text="Veuillez renseigner l'identifiant et le mot de passe.")
            return
        user = db.authentifier(identifiant, mdp)
        if user is None:
            self.erreur.configure(text="Identifiant ou mot de passe incorrect, ou compte "
                                        "désactivé.")
            return
        self.erreur.configure(text="")
        db.log_audit(user["id"], "Connexion")
        self.on_success(user)


class DialogueChangerMotDePasse(tk.Toplevel):
    def __init__(self, parent, user, obligatoire=False):
        super().__init__(parent)
        self.user = user
        self.title("Changer le mot de passe")
        self.geometry("360x220")
        self.resizable(False, False)
        self.grab_set()

        cadre = ttk.Frame(self, padding=20)
        cadre.pack(fill="both", expand=True)

        if obligatoire:
            ttk.Label(
                cadre, text="Pour des raisons de sécurité, vous devez changer votre mot de "
                            "passe avant de continuer.",
                font=FONT_BASE, wraplength=320, foreground="#a6371f"
            ).pack(pady=(0, 10))
            self.protocol("WM_DELETE_WINDOW", lambda: None)

        ttk.Label(cadre, text="Nouveau mot de passe :", font=FONT_BASE).pack(anchor="w")
        self.mdp1 = tk.StringVar()
        ttk.Entry(cadre, textvariable=self.mdp1, show="*", font=FONT_BASE).pack(fill="x", pady=4)

        ttk.Label(cadre, text="Confirmer le mot de passe :", font=FONT_BASE).pack(anchor="w")
        self.mdp2 = tk.StringVar()
        ttk.Entry(cadre, textvariable=self.mdp2, show="*", font=FONT_BASE).pack(fill="x", pady=4)

        ttk.Button(cadre, text="Valider", command=self._valider).pack(pady=14)

    def _valider(self):
        m1, m2 = self.mdp1.get(), self.mdp2.get()
        if len(m1) < 6:
            messagebox.showerror("Erreur", "Le mot de passe doit contenir au moins 6 "
                                            "caractères.", parent=self)
            return
        if m1 != m2:
            messagebox.showerror("Erreur", "Les deux mots de passe ne correspondent pas.",
                                  parent=self)
            return
        db.changer_mot_de_passe(self.user["id"], m1)
        db.log_audit(self.user["id"], "Changement de mot de passe")
        messagebox.showinfo("Succès", "Mot de passe mis à jour.", parent=self)
        self.destroy()
