# -*- coding: utf-8 -*-
"""Administration des comptes utilisateurs — réservé au rôle admin."""

import tkinter as tk
from tkinter import ttk, messagebox

import db

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_BASE = ("Segoe UI", 10)
ACCENT = "#2f6f4f"

ROLES = ["operateur", "chef_de_poste", "superviseur", "admin"]
ROLES_LABELS = {
    "operateur": "Opérateur",
    "chef_de_poste": "Chef de poste",
    "superviseur": "Superviseur",
    "admin": "Administrateur",
}


class OngletAdministration(ttk.Frame):
    def __init__(self, parent, current_user, on_users_changed=None):
        super().__init__(parent, padding=16)
        self.current_user = current_user
        self.on_users_changed = on_users_changed

        ttk.Label(self, text="Administration — comptes utilisateurs", font=FONT_TITLE,
                  foreground=ACCENT).pack(anchor="w")
        ttk.Label(
            self,
            text="Créez les comptes de vos collaborateurs et gérez leurs rôles. Chaque "
                 "collaborateur doit avoir son propre compte pour que les relevés, "
                 "productions, incidents et checklists soient correctement attribués.",
            font=FONT_BASE, wraplength=820,
        ).pack(anchor="w", pady=(2, 14))

        form = ttk.LabelFrame(self, text="Créer un compte", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Nom complet :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.nom_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.nom_var, width=32, font=FONT_BASE).grid(
            row=0, column=1, pady=4, sticky="w"
        )

        ttk.Label(form, text="Identifiant de connexion :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.identifiant_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.identifiant_var, width=32, font=FONT_BASE).grid(
            row=1, column=1, pady=4, sticky="w"
        )

        ttk.Label(form, text="Rôle :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.role_var = tk.StringVar(value="operateur")
        ttk.Combobox(
            form, textvariable=self.role_var, state="readonly", width=20, font=FONT_BASE,
            values=[ROLES_LABELS[r] for r in ROLES]
        ).grid(row=2, column=1, pady=4, sticky="w")

        ttk.Label(form, text="Mot de passe initial :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mdp_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.mdp_var, width=20, font=FONT_BASE, show="*").grid(
            row=3, column=1, pady=4, sticky="w"
        )
        ttk.Label(
            form, text="(le collaborateur devra le changer à sa première connexion)",
            font=("Segoe UI", 8), foreground="#777777"
        ).grid(row=4, column=1, sticky="w")

        ttk.Button(form, text="Créer le compte", command=self._creer).grid(
            row=5, column=1, sticky="w", pady=10
        )

        ttk.Label(self, text="Comptes existants", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", pady=(14, 4)
        )
        cols = ("id", "nom_complet", "identifiant", "role", "actif", "date_creation")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        for c, w in zip(cols, (40, 180, 140, 130, 60, 150)):
            self.tree.heading(c, text=c.replace("_", " ").capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True)

        action_frame = ttk.Frame(self)
        action_frame.pack(anchor="w", pady=8)
        ttk.Button(action_frame, text="Désactiver le compte sélectionné",
                   command=self._desactiver).pack(side="left", padx=(0, 8))
        ttk.Button(action_frame, text="Réactiver le compte sélectionné",
                   command=self._reactiver).pack(side="left")

        self._rafraichir()

    def _creer(self):
        nom = self.nom_var.get().strip()
        identifiant = self.identifiant_var.get().strip()
        mdp = self.mdp_var.get()
        role_label = self.role_var.get()
        role = next((r for r in ROLES if ROLES_LABELS[r] == role_label), role_label)

        if not nom or not identifiant:
            messagebox.showerror("Erreur", "Le nom complet et l'identifiant sont obligatoires.")
            return
        if len(mdp) < 6:
            messagebox.showerror("Erreur", "Le mot de passe initial doit contenir au moins "
                                            "6 caractères.")
            return

        try:
            db.creer_utilisateur(identifiant, nom, role, mdp)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer le compte : identifiant "
                                            f"peut-être déjà utilisé.\n({e})")
            return

        db.log_audit(self.current_user["id"], "Création utilisateur", identifiant)
        self.nom_var.set("")
        self.identifiant_var.set("")
        self.mdp_var.set("")
        self._rafraichir()
        if self.on_users_changed:
            self.on_users_changed()
        messagebox.showinfo("Créé", f"Compte « {identifiant} » créé avec succès.")

    def _selection_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez un compte dans la liste.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def _desactiver(self):
        user_id = self._selection_id()
        if user_id is None:
            return
        if user_id == self.current_user["id"]:
            messagebox.showerror("Erreur", "Vous ne pouvez pas désactiver votre propre compte.")
            return
        if messagebox.askyesno("Confirmation", "Désactiver ce compte ? Le collaborateur ne "
                                                "pourra plus se connecter."):
            db.desactiver_utilisateur(user_id)
            db.log_audit(self.current_user["id"], "Désactivation utilisateur", f"id={user_id}")
            self._rafraichir()
            if self.on_users_changed:
                self.on_users_changed()

    def _reactiver(self):
        user_id = self._selection_id()
        if user_id is None:
            return
        db.reactiver_utilisateur(user_id)
        db.log_audit(self.current_user["id"], "Réactivation utilisateur", f"id={user_id}")
        self._rafraichir()
        if self.on_users_changed:
            self.on_users_changed()

    def _rafraichir(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for u in db.lister_utilisateurs():
            self.tree.insert(
                "", "end",
                values=(u["id"], u["nom_complet"], u["identifiant"],
                        ROLES_LABELS.get(u["role"], u["role"]),
                        "Oui" if u["actif"] else "Non", u["date_creation"])
            )
