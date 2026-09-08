# -*- coding: utf-8 -*-
"""Module Logistique minière : flotte, dispatch, pont-bascule, carburant,
maintenance, magasin/pièces détachées, et liaison avec les coûts de
production (un véhicule a un coût logistique par tonne transportée,
transférable comme charge « Transport » vers le centre de coût d'un
poste — le même principe que le CMUP entre deux postes de production).
"""

import tkinter as tk
import datetime
from tkinter import ttk, messagebox

import db
from data_postes import POSTES_REF
from ui_widgets import rendre_defilant

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 10)
ACCENT = "#2f6f4f"
ALERTE = "#a6371f"

TYPES_VEHICULE = ["Camion", "Chargeuse", "Excavatrice", "Bulldozer", "Citerne",
                   "Véhicule léger", "Autre"]
STATUTS_VEHICULE = ["Disponible", "En mission", "Maintenance", "Immobilisé"]
TYPES_MAINTENANCE = ["Préventive", "Corrective", "Vidange", "Pneus", "Batterie", "Autre"]
CATEGORIES_PIECE = ["Pneus", "Filtres", "Huiles", "Pièces mécaniques", "Pièces électriques",
                     "Consommables", "EPI", "Autre"]
CATEGORIES_CHARGE_LOG = ["Personnel", "Autre"]


def _poste_valeurs():
    return [f"{p['id']} — {p['titre']}" for p in POSTES_REF]


class OngletLogistique(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, padding=16)
        self.current_user = current_user

        ttk.Label(self, text="Logistique minière", font=FONT_TITLE, foreground=ACCENT).pack(
            anchor="w"
        )
        ttk.Label(
            self,
            text="Flotte, dispatch, pont-bascule, carburant, maintenance et magasin. Le coût "
                 "logistique d'un véhicule (carburant + maintenance + pièces + personnel), "
                 "rapporté aux tonnes transportées, peut être transféré comme charge "
                 "« Transport » vers un poste de production, au même titre que les charges "
                 "saisies dans Coûts d'exploitation.",
            font=FONT_BASE, wraplength=860,
        ).pack(anchor="w", pady=(2, 12))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self._onglet_tableau_bord(notebook)
        self._onglet_flotte(notebook)
        self._onglet_dispatch(notebook)
        self._onglet_pesee(notebook)
        self._onglet_carburant(notebook)
        self._onglet_maintenance(notebook)
        self._onglet_magasin(notebook)
        self._onglet_cout_logistique(notebook)

    # -----------------------------------------------------------------
    # Utilitaire commun
    # -----------------------------------------------------------------
    def _valeurs_vehicules(self):
        return [f"{v['id']} — {v['code']} ({v['type']})" for v in db.lister_vehicules()]

    def _id_vehicule(self, texte):
        return int(texte.split(" — ")[0]) if texte else None

    # -----------------------------------------------------------------
    # Tableau de bord logistique
    # -----------------------------------------------------------------
    def _onglet_tableau_bord(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Tableau de bord")
        frame = rendre_defilant(page)

        ttk.Button(frame, text="Actualiser", command=lambda: self._rafraichir_dashboard(cartes)) \
            .pack(anchor="w", pady=(0, 10))

        grille = ttk.Frame(frame)
        grille.pack(fill="x")
        cartes = {}
        libelles = [
            ("flotte_totale", "Flotte totale"),
            ("flotte_disponible", "Flotte disponible"),
            ("flotte_en_mission", "Flotte en mission"),
            ("flotte_maintenance", "Flotte en maintenance"),
            ("flotte_immobilisee", "Flotte immobilisée"),
            ("tonnes_transportees_jour", "Tonnes transportées (jour)"),
            ("nombre_voyages_jour", "Voyages (jour)"),
            ("litres_carburant_jour", "Litres carburant (jour)"),
            ("cout_carburant_jour", "Coût carburant (jour, FCFA)"),
            ("cout_transport_par_tonne_jour", "Coût transport/t (jour, FCFA)"),
            ("pieces_sous_seuil", "Pièces sous seuil d'alerte"),
        ]
        for i, (cle, libelle) in enumerate(libelles):
            carte = ttk.LabelFrame(grille, text=libelle, padding=10)
            carte.grid(row=i // 3, column=i % 3, padx=6, pady=6, sticky="nsew")
            valeur_label = ttk.Label(carte, text="—", font=("Segoe UI", 14, "bold"))
            valeur_label.pack()
            cartes[cle] = valeur_label
        for c in range(3):
            grille.columnconfigure(c, weight=1)

        self._rafraichir_dashboard(cartes)

    def _rafraichir_dashboard(self, cartes):
        kpis = db.kpis_logistique_jour()
        seuils_alerte = {"flotte_immobilisee", "pieces_sous_seuil"}
        for cle, label in cartes.items():
            valeur = kpis.get(cle)
            if valeur is None:
                texte = "—"
            elif cle in ("cout_carburant_jour", "cout_transport_par_tonne_jour"):
                texte = f"{valeur:,.0f}".replace(",", " ")
            elif isinstance(valeur, float):
                texte = f"{valeur:.2f}"
            else:
                texte = str(valeur)
            label.configure(text=texte)
            if cle in seuils_alerte and valeur:
                label.configure(foreground=ALERTE)
            else:
                label.configure(foreground="black")

    # -----------------------------------------------------------------
    # Flotte
    # -----------------------------------------------------------------
    def _onglet_flotte(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Flotte")
        frame = rendre_defilant(page)

        form = ttk.LabelFrame(frame, text="Nouveau véhicule / engin", padding=12)
        form.pack(fill="x")

        champs = [
            ("Code véhicule :", "code_var"), ("Immatriculation :", "immat_var"),
            ("Marque / modèle :", "marque_var"), ("Capacité (tonnes) :", "capacite_var"),
            ("Conducteur affecté :", "conducteur_var"),
        ]
        for i, (label, attr) in enumerate(champs):
            ttk.Label(form, text=label, font=FONT_BASE).grid(
                row=i, column=0, sticky="w", padx=(0, 8), pady=4
            )
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(form, textvariable=var, width=30, font=FONT_BASE).grid(
                row=i, column=1, sticky="w", pady=4
            )

        ttk.Label(form, text="Type :", font=FONT_BASE).grid(
            row=len(champs), column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.type_vehicule_var = tk.StringVar(value=TYPES_VEHICULE[0])
        ttk.Combobox(form, textvariable=self.type_vehicule_var, state="readonly", width=27,
                     font=FONT_BASE, values=TYPES_VEHICULE).grid(
            row=len(champs), column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Commentaire :", font=FONT_BASE).grid(
            row=len(champs) + 1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.vehicule_commentaire_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.vehicule_commentaire_var, width=42,
                  font=FONT_BASE).grid(row=len(champs) + 1, column=1, sticky="w", pady=4)

        ttk.Button(form, text="Créer le véhicule", command=self._creer_vehicule).grid(
            row=len(champs) + 2, column=1, sticky="w", pady=10
        )

        ttk.Label(frame, text="Flotte", font=FONT_H2).pack(anchor="w", pady=(14, 4))

        statut_frame = ttk.Frame(frame)
        statut_frame.pack(fill="x", pady=(0, 6))
        ttk.Label(statut_frame, text="Changer le statut du véhicule sélectionné :",
                  font=FONT_BASE).pack(side="left", padx=(0, 8))
        self.nouveau_statut_var = tk.StringVar(value=STATUTS_VEHICULE[0])
        ttk.Combobox(statut_frame, textvariable=self.nouveau_statut_var, state="readonly",
                     width=16, font=FONT_BASE, values=STATUTS_VEHICULE).pack(side="left")
        ttk.Button(statut_frame, text="Appliquer", command=self._changer_statut).pack(
            side="left", padx=(8, 0)
        )

        cols = ("id", "code", "type", "immatriculation", "marque_modele", "capacite_tonnes",
                "compteur_km", "compteur_heures", "conducteur_affecte", "statut")
        entetes = ("ID", "Code", "Type", "Immat.", "Marque/modèle", "Capacité (t)",
                   "Compteur (km)", "Compteur (h)", "Conducteur", "Statut")
        self.tree_flotte = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        largeurs = (40, 80, 100, 90, 130, 90, 100, 90, 130, 100)
        for c, txt, w in zip(cols, entetes, largeurs):
            self.tree_flotte.heading(c, text=txt)
            self.tree_flotte.column(c, width=w, anchor="w")
        self.tree_flotte.tag_configure("immobilise", foreground=ALERTE)
        self.tree_flotte.pack(fill="both", expand=True)

        self._rafraichir_flotte()

    def _creer_vehicule(self):
        if not self.code_var.get().strip():
            messagebox.showerror("Erreur", "Le code véhicule est obligatoire.")
            return
        try:
            capacite = float(self.capacite_var.get().replace(",", ".")) \
                if self.capacite_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Erreur", "La capacité doit être un nombre.")
            return
        try:
            db.ajouter_vehicule(
                self.code_var.get().strip(), self.immat_var.get().strip(),
                self.type_vehicule_var.get(), self.marque_var.get().strip(), capacite,
                self.conducteur_var.get().strip(), self.vehicule_commentaire_var.get().strip()
            )
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer ce véhicule (code déjà "
                                            f"utilisé ?).\n({e})")
            return
        db.log_audit(self.current_user["id"], "Création véhicule", self.code_var.get())
        for attr in ("code_var", "immat_var", "marque_var", "capacite_var", "conducteur_var",
                     "vehicule_commentaire_var"):
            getattr(self, attr).set("")
        self._rafraichir_flotte()
        self._rafraichir_listes_vehicules()
        messagebox.showinfo("Créé", "Véhicule créé avec succès.")

    def _changer_statut(self):
        selection = self.tree_flotte.selection()
        if not selection:
            messagebox.showerror("Erreur", "Sélectionnez un véhicule dans la liste.")
            return
        vehicule_id = int(self.tree_flotte.item(selection[0], "values")[0])
        db.modifier_statut_vehicule(vehicule_id, self.nouveau_statut_var.get())
        db.log_audit(self.current_user["id"], "Changement statut véhicule",
                      f"{vehicule_id} -> {self.nouveau_statut_var.get()}")
        self._rafraichir_flotte()

    def _rafraichir_flotte(self):
        for row in self.tree_flotte.get_children():
            self.tree_flotte.delete(row)
        for v in db.lister_vehicules():
            tag = "immobilise" if v["statut"] == "Immobilisé" else ""
            self.tree_flotte.insert(
                "", "end", tags=(tag,),
                values=(v["id"], v["code"], v["type"], v["immatriculation"] or "",
                        v["marque_modele"] or "", v["capacite_tonnes"] or "",
                        v["compteur_km"], v["compteur_heures"], v["conducteur_affecte"] or "",
                        v["statut"])
            )

    def _rafraichir_listes_vehicules(self):
        """Met à jour les combobox véhicules des autres sous-onglets."""
        valeurs = self._valeurs_vehicules()
        for combo in (getattr(self, "combo_veh_dispatch", None),
                      getattr(self, "combo_veh_pesee", None),
                      getattr(self, "combo_veh_carburant", None),
                      getattr(self, "combo_veh_maintenance", None),
                      getattr(self, "combo_veh_mouvement", None),
                      getattr(self, "combo_veh_cout", None)):
            if combo is not None:
                combo.configure(values=valeurs)

    # -----------------------------------------------------------------
    # Dispatch / missions de transport
    # -----------------------------------------------------------------
    def _onglet_dispatch(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Dispatch / missions")
        frame = rendre_defilant(page)

        form = ttk.LabelFrame(frame, text="Nouvelle mission", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Véhicule :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mission_vehicule_var = tk.StringVar()
        self.combo_veh_dispatch = ttk.Combobox(
            form, textvariable=self.mission_vehicule_var, state="readonly", width=32,
            font=FONT_BASE, values=self._valeurs_vehicules()
        )
        self.combo_veh_dispatch.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Origine :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mission_origine_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.mission_origine_var, width=30, font=FONT_BASE).grid(
            row=1, column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Destination :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mission_destination_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.mission_destination_var, width=30,
                  font=FONT_BASE).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Poste de destination (optionnel) :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mission_poste_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.mission_poste_var, state="readonly", width=32,
                     font=FONT_BASE, values=["(aucun)"] + _poste_valeurs()).grid(
            row=3, column=1, sticky="w", pady=4
        )

        champs_num = [
            ("Distance (km) :", "mission_distance_var"),
            ("Nombre de voyages :", "mission_voyages_var"),
            ("Tonnes par voyage :", "mission_tpv_var"),
            ("Temps d'attente (min) :", "mission_attente_var"),
            ("Temps de chargement (min) :", "mission_chargement_var"),
            ("Temps de déchargement (min) :", "mission_dechargement_var"),
            ("Carburant consommé (L) :", "mission_carburant_var"),
        ]
        for i, (label, attr) in enumerate(champs_num, start=4):
            ttk.Label(form, text=label, font=FONT_BASE).grid(
                row=i, column=0, sticky="w", padx=(0, 8), pady=4
            )
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(form, textvariable=var, width=16, font=FONT_BASE).grid(
                row=i, column=1, sticky="w", pady=4
            )

        ligne_commentaire = 4 + len(champs_num)
        ttk.Label(form, text="Commentaire :", font=FONT_BASE).grid(
            row=ligne_commentaire, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mission_commentaire_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.mission_commentaire_var, width=42,
                  font=FONT_BASE).grid(row=ligne_commentaire, column=1, sticky="w", pady=4)

        ttk.Button(form, text="Enregistrer la mission", command=self._enregistrer_mission).grid(
            row=ligne_commentaire + 1, column=1, sticky="w", pady=10
        )

        ttk.Label(frame, text="Dernières missions", font=FONT_H2).pack(anchor="w",
                                                                         pady=(14, 4))
        cols = ("horodatage", "vehicule_code", "origine", "destination", "distance_km",
                "nombre_voyages", "tonnage_total", "nom_complet")
        entetes = ("Horodatage", "Véhicule", "Origine", "Destination", "Distance (km)",
                   "Voyages", "Tonnage total (t)", "Saisi par")
        self.tree_missions = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        largeurs = (140, 90, 110, 110, 90, 70, 110, 130)
        for c, txt, w in zip(cols, entetes, largeurs):
            self.tree_missions.heading(c, text=txt)
            self.tree_missions.column(c, width=w, anchor="w")
        self.tree_missions.pack(fill="both", expand=True)

        self._rafraichir_missions()

    def _enregistrer_mission(self):
        if not self.mission_vehicule_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un véhicule.")
            return
        try:
            distance = float(self.mission_distance_var.get().replace(",", ".")) \
                if self.mission_distance_var.get().strip() else None
            voyages = float(self.mission_voyages_var.get().replace(",", ".")) \
                if self.mission_voyages_var.get().strip() else 0
            tpv = float(self.mission_tpv_var.get().replace(",", ".")) \
                if self.mission_tpv_var.get().strip() else 0
            attente = float(self.mission_attente_var.get().replace(",", ".")) \
                if self.mission_attente_var.get().strip() else None
            chargement = float(self.mission_chargement_var.get().replace(",", ".")) \
                if self.mission_chargement_var.get().strip() else None
            dechargement = float(self.mission_dechargement_var.get().replace(",", ".")) \
                if self.mission_dechargement_var.get().strip() else None
            carburant = float(self.mission_carburant_var.get().replace(",", ".")) \
                if self.mission_carburant_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Erreur", "Les champs numériques doivent être des nombres.")
            return

        vehicule_id = self._id_vehicule(self.mission_vehicule_var.get())
        poste_txt = self.mission_poste_var.get()
        poste_id = poste_txt.split(" — ")[0] if poste_txt and poste_txt != "(aucun)" else None

        tonnage = db.ajouter_mission(
            vehicule_id, self.current_user["id"], self.mission_origine_var.get().strip(),
            self.mission_destination_var.get().strip(), poste_id, distance, voyages, tpv,
            attente, chargement, dechargement, carburant,
            self.mission_commentaire_var.get().strip()
        )
        db.log_audit(self.current_user["id"], "Mission de transport",
                      f"{self.mission_vehicule_var.get()} / {tonnage:.2f} t")

        for attr in ("mission_origine_var", "mission_destination_var", "mission_distance_var",
                     "mission_voyages_var", "mission_tpv_var", "mission_attente_var",
                     "mission_chargement_var", "mission_dechargement_var",
                     "mission_carburant_var", "mission_commentaire_var"):
            getattr(self, attr).set("")
        self._rafraichir_missions()
        messagebox.showinfo("Enregistré", f"Mission enregistrée : {tonnage:.2f} t "
                                           f"transportées.")

    def _rafraichir_missions(self):
        for row in self.tree_missions.get_children():
            self.tree_missions.delete(row)
        for m in db.lister_missions(limite=100):
            self.tree_missions.insert(
                "", "end",
                values=(m["horodatage"], m["vehicule_code"], m["origine"] or "",
                        m["destination"] or "", m["distance_km"] or "",
                        m["nombre_voyages"] or "",
                        f"{m['tonnage_total']:.2f}" if m["tonnage_total"] else "0.00",
                        m["nom_complet"])
            )

    # -----------------------------------------------------------------
    # Pont-bascule (weighbridge)
    # -----------------------------------------------------------------
    def _onglet_pesee(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Pont-bascule")
        frame = rendre_defilant(page)

        ttk.Label(
            frame,
            text="Le poids net est calculé automatiquement (brut − tare). S'il est rattaché à "
                 "un poste de destination, il alimente automatiquement le bilan matière de ce "
                 "poste comme une « Alimentation » (visible dans Production & bilan matière).",
            font=FONT_BASE, wraplength=860,
        ).pack(anchor="w", pady=(0, 8))

        form = ttk.LabelFrame(frame, text="Nouveau ticket de pesée", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="N° ticket :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_numero_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.ticket_numero_var, width=22, font=FONT_BASE).grid(
            row=0, column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Véhicule :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_vehicule_var = tk.StringVar()
        self.combo_veh_pesee = ttk.Combobox(
            form, textvariable=self.ticket_vehicule_var, state="readonly", width=32,
            font=FONT_BASE, values=self._valeurs_vehicules()
        )
        self.combo_veh_pesee.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Matière :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_matiere_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.ticket_matiere_var, width=22, font=FONT_BASE).grid(
            row=2, column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Poids brut (t) :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_brut_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.ticket_brut_var, width=16, font=FONT_BASE).grid(
            row=3, column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Tare (t) :", font=FONT_BASE).grid(
            row=4, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_tare_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.ticket_tare_var, width=16, font=FONT_BASE).grid(
            row=4, column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Origine :", font=FONT_BASE).grid(
            row=5, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_origine_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.ticket_origine_var, width=22, font=FONT_BASE).grid(
            row=5, column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Destination :", font=FONT_BASE).grid(
            row=6, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_destination_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.ticket_destination_var, width=22,
                  font=FONT_BASE).grid(row=6, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Poste de destination (optionnel) :", font=FONT_BASE).grid(
            row=7, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_poste_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.ticket_poste_var, state="readonly", width=32,
                     font=FONT_BASE, values=["(aucun)"] + _poste_valeurs()).grid(
            row=7, column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Teneur / grade (%, optionnel) :", font=FONT_BASE).grid(
            row=8, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_grade_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.ticket_grade_var, width=16, font=FONT_BASE).grid(
            row=8, column=1, sticky="w", pady=4
        )

        ttk.Label(form, text="Commentaire :", font=FONT_BASE).grid(
            row=9, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.ticket_commentaire_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.ticket_commentaire_var, width=42,
                  font=FONT_BASE).grid(row=9, column=1, sticky="w", pady=4)

        ttk.Button(form, text="Enregistrer le ticket", command=self._enregistrer_ticket).grid(
            row=10, column=1, sticky="w", pady=10
        )

        ttk.Label(frame, text="Derniers tickets de pesée", font=FONT_H2).pack(anchor="w",
                                                                                pady=(14, 4))
        cols = ("horodatage", "numero_ticket", "vehicule_code", "matiere", "poids_brut_t",
                "tare_t", "poids_net_t", "origine", "destination")
        entetes = ("Horodatage", "N° ticket", "Véhicule", "Matière", "Brut (t)", "Tare (t)",
                   "Net (t)", "Origine", "Destination")
        self.tree_pesee = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        largeurs = (140, 100, 90, 100, 70, 70, 70, 100, 100)
        for c, txt, w in zip(cols, entetes, largeurs):
            self.tree_pesee.heading(c, text=txt)
            self.tree_pesee.column(c, width=w, anchor="w")
        self.tree_pesee.pack(fill="both", expand=True)

        self._rafraichir_pesee()

    def _enregistrer_ticket(self):
        if not self.ticket_numero_var.get().strip() or not self.ticket_vehicule_var.get():
            messagebox.showerror("Erreur", "Le numéro de ticket et le véhicule sont "
                                            "obligatoires.")
            return
        try:
            brut = float(self.ticket_brut_var.get().replace(",", "."))
            tare = float(self.ticket_tare_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Le poids brut et la tare doivent être des "
                                            "nombres.")
            return
        if tare > brut:
            messagebox.showerror("Erreur", "La tare ne peut pas dépasser le poids brut.")
            return
        grade = None
        if self.ticket_grade_var.get().strip():
            try:
                grade = float(self.ticket_grade_var.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erreur", "La teneur doit être un nombre.")
                return

        vehicule_id = self._id_vehicule(self.ticket_vehicule_var.get())
        poste_txt = self.ticket_poste_var.get()
        poste_id = poste_txt.split(" — ")[0] if poste_txt and poste_txt != "(aucun)" else None

        poids_net = db.ajouter_ticket_pesee(
            self.ticket_numero_var.get().strip(), vehicule_id, self.current_user["id"],
            self.ticket_matiere_var.get().strip(), brut, tare,
            self.ticket_origine_var.get().strip(), self.ticket_destination_var.get().strip(),
            poste_id, grade, self.ticket_commentaire_var.get().strip()
        )
        db.log_audit(self.current_user["id"], "Ticket de pesée",
                      f"{self.ticket_numero_var.get()} / {poids_net:.2f} t")

        for attr in ("ticket_numero_var", "ticket_matiere_var", "ticket_brut_var",
                     "ticket_tare_var", "ticket_origine_var", "ticket_destination_var",
                     "ticket_grade_var", "ticket_commentaire_var"):
            getattr(self, attr).set("")
        self._rafraichir_pesee()

        message = f"Poids net : {poids_net:.2f} t."
        if poste_id:
            message += f"\nAjouté automatiquement en Alimentation au bilan matière de " \
                       f"{poste_id}."
        messagebox.showinfo("Enregistré", message)

    def _rafraichir_pesee(self):
        for row in self.tree_pesee.get_children():
            self.tree_pesee.delete(row)
        for t in db.lister_tickets_pesee(limite=100):
            self.tree_pesee.insert(
                "", "end",
                values=(t["horodatage"], t["numero_ticket"], t["vehicule_code"],
                        t["matiere"] or "", f"{t['poids_brut_t']:.2f}", f"{t['tare_t']:.2f}",
                        f"{t['poids_net_t']:.2f}", t["origine"] or "", t["destination"] or "")
            )

    # -----------------------------------------------------------------
    # Carburant
    # -----------------------------------------------------------------
    def _onglet_carburant(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Carburant")
        frame = rendre_defilant(page)

        form = ttk.LabelFrame(frame, text="Nouveau plein", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Véhicule :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.plein_vehicule_var = tk.StringVar()
        self.combo_veh_carburant = ttk.Combobox(
            form, textvariable=self.plein_vehicule_var, state="readonly", width=32,
            font=FONT_BASE, values=self._valeurs_vehicules()
        )
        self.combo_veh_carburant.grid(row=0, column=1, sticky="w", pady=4)

        champs = [
            ("Compteur (km ou h) :", "plein_compteur_var"), ("Litres :", "plein_litres_var"),
            ("Prix unitaire (FCFA/L) :", "plein_prix_var"),
            ("Conducteur :", "plein_conducteur_var"), ("Station :", "plein_station_var"),
        ]
        for i, (label, attr) in enumerate(champs, start=1):
            ttk.Label(form, text=label, font=FONT_BASE).grid(
                row=i, column=0, sticky="w", padx=(0, 8), pady=4
            )
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(form, textvariable=var, width=22, font=FONT_BASE).grid(
                row=i, column=1, sticky="w", pady=4
            )

        ttk.Label(form, text="Commentaire :", font=FONT_BASE).grid(
            row=len(champs) + 1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.plein_commentaire_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.plein_commentaire_var, width=42,
                  font=FONT_BASE).grid(row=len(champs) + 1, column=1, sticky="w", pady=4)

        ttk.Button(form, text="Enregistrer le plein", command=self._enregistrer_plein).grid(
            row=len(champs) + 2, column=1, sticky="w", pady=10
        )

        ttk.Label(frame, text="Consommation & anomalie", font=FONT_H2).pack(anchor="w",
                                                                              pady=(14, 4))
        consult_frame = ttk.Frame(frame)
        consult_frame.pack(fill="x", pady=(0, 6))
        ttk.Label(consult_frame, text="Véhicule :", font=FONT_BASE).pack(side="left")
        self.conso_vehicule_var = tk.StringVar()
        self.combo_veh_conso = ttk.Combobox(
            consult_frame, textvariable=self.conso_vehicule_var, state="readonly", width=32,
            font=FONT_BASE, values=self._valeurs_vehicules()
        )
        self.combo_veh_conso.pack(side="left", padx=8)
        ttk.Label(consult_frame, text="Consommation standard (L/100km, optionnel) :",
                  font=FONT_BASE).pack(side="left", padx=(12, 4))
        self.conso_standard_var = tk.StringVar()
        ttk.Entry(consult_frame, textvariable=self.conso_standard_var, width=8,
                  font=FONT_BASE).pack(side="left")
        ttk.Button(consult_frame, text="Calculer", command=self._calculer_consommation).pack(
            side="left", padx=8
        )

        self.resultat_conso = tk.Text(
            frame, height=8, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
        )
        self.resultat_conso.pack(fill="both", expand=True, pady=(0, 10))
        self.resultat_conso.configure(state="disabled")

        ttk.Label(frame, text="Derniers pleins", font=FONT_H2).pack(anchor="w", pady=(4, 4))
        cols = ("horodatage", "vehicule_code", "litres", "prix_unitaire", "montant",
                "conducteur", "station")
        entetes = ("Horodatage", "Véhicule", "Litres", "Prix unit.", "Montant (FCFA)",
                   "Conducteur", "Station")
        self.tree_carburant = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        largeurs = (140, 90, 70, 90, 110, 110, 110)
        for c, txt, w in zip(cols, entetes, largeurs):
            self.tree_carburant.heading(c, text=txt)
            self.tree_carburant.column(c, width=w, anchor="w")
        self.tree_carburant.pack(fill="both", expand=True)

        self._rafraichir_carburant()

    def _enregistrer_plein(self):
        if not self.plein_vehicule_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un véhicule.")
            return
        try:
            compteur = float(self.plein_compteur_var.get().replace(",", ".")) \
                if self.plein_compteur_var.get().strip() else None
            litres = float(self.plein_litres_var.get().replace(",", "."))
            prix = float(self.plein_prix_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Litres et prix unitaire doivent être des "
                                            "nombres.")
            return

        vehicule_id = self._id_vehicule(self.plein_vehicule_var.get())
        montant = db.ajouter_plein_carburant(
            vehicule_id, self.current_user["id"], compteur, litres, prix,
            self.plein_conducteur_var.get().strip(), self.plein_station_var.get().strip(),
            self.plein_commentaire_var.get().strip()
        )
        db.log_audit(self.current_user["id"], "Plein carburant",
                      f"{self.plein_vehicule_var.get()} / {litres} L / {montant:.0f} FCFA")

        for attr in ("plein_compteur_var", "plein_litres_var", "plein_prix_var",
                     "plein_conducteur_var", "plein_station_var", "plein_commentaire_var"):
            getattr(self, attr).set("")
        self._rafraichir_carburant()
        messagebox.showinfo("Enregistré", f"Plein enregistré : {montant:,.0f} FCFA."
                             .replace(",", " "))

    def _calculer_consommation(self):
        if not self.conso_vehicule_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un véhicule.")
            return
        vehicule_id = self._id_vehicule(self.conso_vehicule_var.get())
        conso = db.consommation_vehicule(vehicule_id)

        lignes = [
            f"CONSOMMATION — {self.conso_vehicule_var.get()}",
            f"Litres consommés (total) : {conso['litres_total']:.1f} L",
            f"Montant carburant (total) : {conso['montant_total']:,.0f} FCFA"
            .replace(",", " "),
            f"Distance parcourue (missions) : {conso['distance_total_km']:.1f} km",
            f"Tonnage transporté (missions) : {conso['tonnage_total_t']:.2f} t",
        ]
        if conso["litres_par_100km"] is not None:
            lignes.append(f"\nConsommation réelle : {conso['litres_par_100km']:.1f} L/100km")
            if self.conso_standard_var.get().strip():
                try:
                    standard = float(self.conso_standard_var.get().replace(",", "."))
                    ecart = (conso["litres_par_100km"] - standard) / standard * 100
                    lignes.append(f"Consommation standard : {standard:.1f} L/100km")
                    signe = "+" if ecart >= 0 else ""
                    lignes.append(f"Écart : {signe}{ecart:.1f} %"
                                  + ("  ⚠ ANOMALIE À CONTRÔLER" if abs(ecart) > 20 else ""))
                except ValueError:
                    lignes.append("(consommation standard invalide, ignorée)")
        if conso["litres_par_tonne"] is not None:
            lignes.append(f"\nLitres/tonne : {conso['litres_par_tonne']:.2f} L/t")
        if conso["cout_carburant_par_tonne"] is not None:
            lignes.append(f"Coût carburant/tonne : "
                           f"{conso['cout_carburant_par_tonne']:,.0f} FCFA/t"
                           .replace(",", " "))

        self.resultat_conso.configure(state="normal")
        self.resultat_conso.delete("1.0", "end")
        self.resultat_conso.insert("end", "\n".join(lignes))
        self.resultat_conso.configure(state="disabled")

    def _rafraichir_carburant(self):
        for row in self.tree_carburant.get_children():
            self.tree_carburant.delete(row)
        for p in db.lister_pleins_carburant(limite=100):
            self.tree_carburant.insert(
                "", "end",
                values=(p["horodatage"], p["vehicule_code"], f"{p['litres']:.1f}",
                        f"{p['prix_unitaire']:.0f}", f"{p['montant']:.0f}",
                        p["conducteur"] or "", p["station"] or "")
            )

    # -----------------------------------------------------------------
    # Maintenance
    # -----------------------------------------------------------------
    def _onglet_maintenance(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Maintenance")
        frame = rendre_defilant(page)

        form = ttk.LabelFrame(frame, text="Nouvelle intervention", padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Véhicule :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.maint_vehicule_var = tk.StringVar()
        self.combo_veh_maintenance = ttk.Combobox(
            form, textvariable=self.maint_vehicule_var, state="readonly", width=32,
            font=FONT_BASE, values=self._valeurs_vehicules()
        )
        self.combo_veh_maintenance.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Type d'intervention :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.maint_type_var = tk.StringVar(value=TYPES_MAINTENANCE[0])
        ttk.Combobox(form, textvariable=self.maint_type_var, state="readonly", width=20,
                     font=FONT_BASE, values=TYPES_MAINTENANCE).grid(
            row=1, column=1, sticky="w", pady=4
        )

        champs = [
            ("Compteur heures actuel :", "maint_heures_var"),
            ("Compteur km actuel :", "maint_km_var"), ("Coût (FCFA) :", "maint_cout_var"),
            ("Prochaine échéance (heures) :", "maint_echeance_var"),
        ]
        for i, (label, attr) in enumerate(champs, start=2):
            ttk.Label(form, text=label, font=FONT_BASE).grid(
                row=i, column=0, sticky="w", padx=(0, 8), pady=4
            )
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(form, textvariable=var, width=18, font=FONT_BASE).grid(
                row=i, column=1, sticky="w", pady=4
            )

        ligne_desc = 2 + len(champs)
        ttk.Label(form, text="Description :", font=FONT_BASE).grid(
            row=ligne_desc, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.maint_description_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.maint_description_var, width=42,
                  font=FONT_BASE).grid(row=ligne_desc, column=1, sticky="w", pady=4)

        ttk.Button(form, text="Enregistrer l'intervention",
                   command=self._enregistrer_maintenance).grid(
            row=ligne_desc + 1, column=1, sticky="w", pady=10
        )

        ttk.Label(frame, text="Historique des interventions", font=FONT_H2).pack(
            anchor="w", pady=(14, 4)
        )
        cols = ("horodatage", "vehicule_code", "type_intervention", "compteur_heures",
                "cout", "prochaine_echeance_heures", "description")
        entetes = ("Horodatage", "Véhicule", "Type", "Compteur (h)", "Coût (FCFA)",
                   "Prochaine échéance (h)", "Description")
        self.tree_maintenance = ttk.Treeview(frame, columns=cols, show="headings", height=9)
        largeurs = (140, 90, 100, 100, 100, 140, 220)
        for c, txt, w in zip(cols, entetes, largeurs):
            self.tree_maintenance.heading(c, text=txt)
            self.tree_maintenance.column(c, width=w, anchor="w")
        self.tree_maintenance.pack(fill="both", expand=True)

        self._rafraichir_maintenance()

    def _enregistrer_maintenance(self):
        if not self.maint_vehicule_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un véhicule.")
            return
        try:
            heures = float(self.maint_heures_var.get().replace(",", ".")) \
                if self.maint_heures_var.get().strip() else None
            km = float(self.maint_km_var.get().replace(",", ".")) \
                if self.maint_km_var.get().strip() else None
            cout = float(self.maint_cout_var.get().replace(",", ".")) \
                if self.maint_cout_var.get().strip() else 0
            echeance = float(self.maint_echeance_var.get().replace(",", ".")) \
                if self.maint_echeance_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Erreur", "Les champs numériques doivent être des nombres.")
            return

        vehicule_id = self._id_vehicule(self.maint_vehicule_var.get())
        db.ajouter_maintenance(
            vehicule_id, self.current_user["id"], self.maint_type_var.get(), heures, km,
            self.maint_description_var.get().strip(), cout, echeance
        )
        db.log_audit(self.current_user["id"], "Maintenance véhicule",
                      f"{self.maint_vehicule_var.get()} / {self.maint_type_var.get()} / "
                      f"{cout:.0f} FCFA")

        for attr in ("maint_heures_var", "maint_km_var", "maint_cout_var",
                     "maint_echeance_var", "maint_description_var"):
            getattr(self, attr).set("")
        self._rafraichir_maintenance()
        self._rafraichir_flotte()
        messagebox.showinfo("Enregistré", "Intervention enregistrée avec succès.")

    def _rafraichir_maintenance(self):
        for row in self.tree_maintenance.get_children():
            self.tree_maintenance.delete(row)
        for m in db.lister_maintenances(limite=100):
            self.tree_maintenance.insert(
                "", "end",
                values=(m["horodatage"], m["vehicule_code"], m["type_intervention"],
                        m["compteur_heures"] or "", f"{m['cout']:.0f}",
                        m["prochaine_echeance_heures"] or "", m["description"] or "")
            )

    # -----------------------------------------------------------------
    # Magasin / pièces détachées
    # -----------------------------------------------------------------
    def _onglet_magasin(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Magasin / pièces")
        frame = rendre_defilant(page)

        form_piece = ttk.LabelFrame(frame, text="Nouvelle référence pièce", padding=12)
        form_piece.pack(fill="x")

        champs = [("Code :", "piece_code_var"), ("Désignation :", "piece_designation_var"),
                  ("Unité :", "piece_unite_var"), ("Stock initial :", "piece_stock_var"),
                  ("Seuil d'alerte :", "piece_seuil_var")]
        for i, (label, attr) in enumerate(champs):
            ttk.Label(form_piece, text=label, font=FONT_BASE).grid(
                row=i, column=0, sticky="w", padx=(0, 8), pady=4
            )
            var = tk.StringVar()
            setattr(self, attr, var)
            ttk.Entry(form_piece, textvariable=var, width=22, font=FONT_BASE).grid(
                row=i, column=1, sticky="w", pady=4
            )
        self.piece_unite_var.set("unité")

        ttk.Label(form_piece, text="Catégorie :", font=FONT_BASE).grid(
            row=len(champs), column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.piece_categorie_var = tk.StringVar(value=CATEGORIES_PIECE[0])
        ttk.Combobox(form_piece, textvariable=self.piece_categorie_var, state="readonly",
                     width=19, font=FONT_BASE, values=CATEGORIES_PIECE).grid(
            row=len(champs), column=1, sticky="w", pady=4
        )
        ttk.Button(form_piece, text="Créer la référence", command=self._creer_piece).grid(
            row=len(champs) + 1, column=1, sticky="w", pady=10
        )

        form_mvt = ttk.LabelFrame(frame, text="Mouvement de stock (entrée / sortie)",
                                   padding=12)
        form_mvt.pack(fill="x", pady=(12, 0))

        ttk.Label(form_mvt, text="Pièce :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mvt_piece_var = tk.StringVar()
        self.combo_piece_mouvement = ttk.Combobox(
            form_mvt, textvariable=self.mvt_piece_var, state="readonly", width=36,
            font=FONT_BASE
        )
        self.combo_piece_mouvement.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form_mvt, text="Type :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mvt_type_var = tk.StringVar(value="Sortie")
        ttk.Combobox(form_mvt, textvariable=self.mvt_type_var, state="readonly", width=14,
                     font=FONT_BASE, values=["Entrée", "Sortie"]).grid(
            row=1, column=1, sticky="w", pady=4
        )

        ttk.Label(form_mvt, text="Quantité :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mvt_quantite_var = tk.StringVar()
        ttk.Entry(form_mvt, textvariable=self.mvt_quantite_var, width=16, font=FONT_BASE).grid(
            row=2, column=1, sticky="w", pady=4
        )

        ttk.Label(form_mvt, text="Coût unitaire (FCFA, si sortie) :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mvt_cout_var = tk.StringVar()
        ttk.Entry(form_mvt, textvariable=self.mvt_cout_var, width=16, font=FONT_BASE).grid(
            row=3, column=1, sticky="w", pady=4
        )

        ttk.Label(form_mvt, text="Véhicule concerné (si sortie) :", font=FONT_BASE).grid(
            row=4, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mvt_vehicule_var = tk.StringVar()
        self.combo_veh_mouvement = ttk.Combobox(
            form_mvt, textvariable=self.mvt_vehicule_var, state="readonly", width=32,
            font=FONT_BASE, values=["(aucun)"] + self._valeurs_vehicules()
        )
        self.combo_veh_mouvement.grid(row=4, column=1, sticky="w", pady=4)

        ttk.Label(form_mvt, text="Commentaire :", font=FONT_BASE).grid(
            row=5, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.mvt_commentaire_var = tk.StringVar()
        ttk.Entry(form_mvt, textvariable=self.mvt_commentaire_var, width=42,
                  font=FONT_BASE).grid(row=5, column=1, sticky="w", pady=4)

        ttk.Button(form_mvt, text="Enregistrer le mouvement",
                   command=self._enregistrer_mouvement).grid(
            row=6, column=1, sticky="w", pady=10
        )

        ttk.Label(frame, text="Stock des pièces", font=FONT_H2).pack(anchor="w", pady=(14, 4))
        cols = ("code", "designation", "categorie", "unite", "stock_actuel", "seuil_alerte")
        entetes = ("Code", "Désignation", "Catégorie", "Unité", "Stock actuel", "Seuil alerte")
        self.tree_pieces = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        largeurs = (90, 200, 140, 70, 90, 90)
        for c, txt, w in zip(cols, entetes, largeurs):
            self.tree_pieces.heading(c, text=txt)
            self.tree_pieces.column(c, width=w, anchor="w")
        self.tree_pieces.tag_configure("sous_seuil", foreground=ALERTE)
        self.tree_pieces.pack(fill="both", expand=True)

        self._rafraichir_pieces()

    def _creer_piece(self):
        if not self.piece_code_var.get().strip() or not self.piece_designation_var.get() \
                .strip():
            messagebox.showerror("Erreur", "Le code et la désignation sont obligatoires.")
            return
        try:
            stock_initial = float(self.piece_stock_var.get().replace(",", ".")) \
                if self.piece_stock_var.get().strip() else 0
            seuil = float(self.piece_seuil_var.get().replace(",", ".")) \
                if self.piece_seuil_var.get().strip() else 0
        except ValueError:
            messagebox.showerror("Erreur", "Stock initial et seuil doivent être des "
                                            "nombres.")
            return
        try:
            db.ajouter_piece(
                self.piece_code_var.get().strip(), self.piece_designation_var.get().strip(),
                self.piece_categorie_var.get(), self.piece_unite_var.get().strip() or "unité",
                stock_initial, seuil
            )
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de créer cette pièce (code déjà "
                                            f"utilisé ?).\n({e})")
            return
        db.log_audit(self.current_user["id"], "Création pièce", self.piece_code_var.get())
        for attr in ("piece_code_var", "piece_designation_var", "piece_stock_var",
                     "piece_seuil_var"):
            getattr(self, attr).set("")
        self._rafraichir_pieces()
        messagebox.showinfo("Créée", "Référence pièce créée avec succès.")

    def _enregistrer_mouvement(self):
        if not self.mvt_piece_var.get():
            messagebox.showerror("Erreur", "Sélectionnez une pièce.")
            return
        try:
            quantite = float(self.mvt_quantite_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "La quantité doit être un nombre.")
            return
        cout_unitaire = None
        if self.mvt_cout_var.get().strip():
            try:
                cout_unitaire = float(self.mvt_cout_var.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erreur", "Le coût unitaire doit être un nombre.")
                return

        piece_id = int(self.mvt_piece_var.get().split(" — ")[0])
        vehicule_txt = self.mvt_vehicule_var.get()
        vehicule_id = self._id_vehicule(vehicule_txt) if vehicule_txt and vehicule_txt != \
            "(aucun)" else None

        db.mouvement_piece(piece_id, self.current_user["id"], self.mvt_type_var.get(),
                            quantite, vehicule_id, cout_unitaire,
                            self.mvt_commentaire_var.get().strip())
        db.log_audit(self.current_user["id"], "Mouvement pièce",
                      f"{self.mvt_piece_var.get()} / {self.mvt_type_var.get()} / {quantite}")

        for attr in ("mvt_quantite_var", "mvt_cout_var", "mvt_commentaire_var"):
            getattr(self, attr).set("")
        self._rafraichir_pieces()
        messagebox.showinfo("Enregistré", "Mouvement de stock enregistré.")

    def _rafraichir_pieces(self):
        pieces = db.lister_pieces()
        self.combo_piece_mouvement.configure(
            values=[f"{p['id']} — {p['code']} ({p['designation']})" for p in pieces]
        )
        for row in self.tree_pieces.get_children():
            self.tree_pieces.delete(row)
        for p in pieces:
            tag = "sous_seuil" if p["stock_actuel"] <= p["seuil_alerte"] else ""
            self.tree_pieces.insert(
                "", "end", tags=(tag,),
                values=(p["code"], p["designation"], p["categorie"], p["unite"],
                        p["stock_actuel"], p["seuil_alerte"])
            )

    # -----------------------------------------------------------------
    # Coût logistique & liaison comptable
    # -----------------------------------------------------------------
    def _onglet_cout_logistique(self, notebook):
        page = ttk.Frame(notebook)
        notebook.add(page, text="Coût logistique & liaison comptable")
        frame = rendre_defilant(page)

        ttk.Label(
            frame,
            text="Le coût logistique total d'un véhicule (carburant + maintenance + pièces + "
                 "personnel/autres charges) est rapporté aux tonnes transportées (missions + "
                 "tickets de pesée) pour obtenir un coût par tonne, puis peut être transféré "
                 "comme charge « Transport » vers le centre de coût d'un poste de production.",
            font=FONT_BASE, wraplength=860,
        ).pack(anchor="w", pady=(0, 8))

        charge_frame = ttk.LabelFrame(frame, text="Charge logistique manuelle (personnel, "
                                                    "autres)", padding=12)
        charge_frame.pack(fill="x")
        ttk.Label(charge_frame, text="Véhicule :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.charge_log_vehicule_var = tk.StringVar()
        ttk.Combobox(charge_frame, textvariable=self.charge_log_vehicule_var, state="readonly",
                     width=32, font=FONT_BASE, values=self._valeurs_vehicules()).grid(
            row=0, column=1, sticky="w", pady=4
        )
        ttk.Label(charge_frame, text="Catégorie :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.charge_log_categorie_var = tk.StringVar(value=CATEGORIES_CHARGE_LOG[0])
        ttk.Combobox(charge_frame, textvariable=self.charge_log_categorie_var, state="readonly",
                     width=16, font=FONT_BASE, values=CATEGORIES_CHARGE_LOG).grid(
            row=1, column=1, sticky="w", pady=4
        )
        ttk.Label(charge_frame, text="Montant (FCFA) :", font=FONT_BASE).grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.charge_log_montant_var = tk.StringVar()
        ttk.Entry(charge_frame, textvariable=self.charge_log_montant_var, width=18,
                  font=FONT_BASE).grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(charge_frame, text="Commentaire :", font=FONT_BASE).grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.charge_log_commentaire_var = tk.StringVar()
        ttk.Entry(charge_frame, textvariable=self.charge_log_commentaire_var, width=42,
                  font=FONT_BASE).grid(row=3, column=1, sticky="w", pady=4)
        ttk.Button(charge_frame, text="Enregistrer la charge",
                   command=self._enregistrer_charge_logistique).grid(
            row=4, column=1, sticky="w", pady=10
        )

        calc_frame = ttk.LabelFrame(frame, text="Coût logistique par tonne", padding=12)
        calc_frame.pack(fill="x", pady=(12, 0))
        ttk.Label(calc_frame, text="Véhicule :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.cout_log_vehicule_var = tk.StringVar()
        self.combo_veh_cout = ttk.Combobox(
            calc_frame, textvariable=self.cout_log_vehicule_var, state="readonly", width=32,
            font=FONT_BASE, values=self._valeurs_vehicules()
        )
        self.combo_veh_cout.grid(row=0, column=1, sticky="w", pady=4)
        ttk.Label(calc_frame, text="Depuis (AAAA-MM-JJ, optionnel) :", font=FONT_BASE).grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4
        )
        self.cout_log_date_var = tk.StringVar()
        ttk.Entry(calc_frame, textvariable=self.cout_log_date_var, width=14,
                  font=FONT_BASE).grid(row=1, column=1, sticky="w", pady=4)
        ttk.Button(calc_frame, text="Calculer", command=self._calculer_cout_logistique).grid(
            row=2, column=1, sticky="w", pady=8
        )

        self.resultat_cout_log = tk.Text(
            frame, height=9, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
        )
        self.resultat_cout_log.pack(fill="both", expand=True, pady=(0, 10))
        self.resultat_cout_log.configure(state="disabled")

        transfert_frame = ttk.LabelFrame(frame, text="Transférer vers un poste de production",
                                          padding=12)
        transfert_frame.pack(fill="x")
        ttk.Label(transfert_frame, text="Poste de destination :", font=FONT_BASE).grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )
        self.transfert_poste_var = tk.StringVar()
        ttk.Combobox(transfert_frame, textvariable=self.transfert_poste_var, state="readonly",
                     width=32, font=FONT_BASE, values=_poste_valeurs()).grid(
            row=0, column=1, sticky="w"
        )
        ttk.Button(transfert_frame, text="Transférer le coût logistique (charge Transport)",
                   command=self._transferer_cout_logistique).grid(
            row=0, column=2, padx=(16, 0)
        )

    def _enregistrer_charge_logistique(self):
        if not self.charge_log_vehicule_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un véhicule.")
            return
        try:
            montant = float(self.charge_log_montant_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Le montant doit être un nombre.")
            return
        vehicule_id = self._id_vehicule(self.charge_log_vehicule_var.get())
        db.ajouter_charge_logistique(vehicule_id, self.current_user["id"],
                                      self.charge_log_categorie_var.get(), montant,
                                      self.charge_log_commentaire_var.get().strip())
        db.log_audit(self.current_user["id"], "Charge logistique",
                      f"{self.charge_log_vehicule_var.get()} / "
                      f"{self.charge_log_categorie_var.get()} / {montant} FCFA")
        self.charge_log_montant_var.set("")
        self.charge_log_commentaire_var.set("")
        messagebox.showinfo("Enregistré", "Charge logistique enregistrée.")

    def _calculer_cout_logistique(self):
        if not self.cout_log_vehicule_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un véhicule.")
            return
        vehicule_id = self._id_vehicule(self.cout_log_vehicule_var.get())
        date_debut = self.cout_log_date_var.get().strip() or None
        cout = db.cout_logistique_vehicule(vehicule_id, date_debut, None)

        lignes = [f"COÛT LOGISTIQUE — {self.cout_log_vehicule_var.get()}"]
        if date_debut:
            lignes.append(f"Depuis le {date_debut}")
        lignes.append("\nCharges par catégorie :")
        if not cout["par_categorie"]:
            lignes.append("  (aucune charge logistique sur cette période)")
        for categorie, montant in cout["par_categorie"].items():
            lignes.append(f"  {categorie:<14} {montant:14,.0f} FCFA".replace(",", " "))
        lignes.append(f"\nCoût logistique total : {cout['total']:,.0f} FCFA"
                       .replace(",", " "))
        lignes.append(f"Tonnage transporté : {cout['tonnage_total_t']:.2f} t")
        if cout["cout_par_tonne"] is not None:
            lignes.append(f"Coût logistique par tonne : {cout['cout_par_tonne']:,.2f} FCFA/t"
                           .replace(",", " "))
        else:
            lignes.append("Coût logistique par tonne : non calculable (aucune tonne "
                           "transportée)")

        self.resultat_cout_log.configure(state="normal")
        self.resultat_cout_log.delete("1.0", "end")
        self.resultat_cout_log.insert("end", "\n".join(lignes))
        self.resultat_cout_log.configure(state="disabled")

    def _transferer_cout_logistique(self):
        if not self.cout_log_vehicule_var.get() or not self.transfert_poste_var.get():
            messagebox.showerror("Erreur", "Sélectionnez un véhicule (et calculez son coût) "
                                            "ainsi qu'un poste de destination.")
            return
        vehicule_id = self._id_vehicule(self.cout_log_vehicule_var.get())
        poste_id = self.transfert_poste_var.get().split(" — ")[0]
        date_debut = self.cout_log_date_var.get().strip() or None

        try:
            cout = db.transferer_cout_logistique(vehicule_id, poste_id,
                                                   self.current_user["id"], date_debut, None)
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        db.log_audit(
            self.current_user["id"], "Transfert coût logistique",
            f"{self.cout_log_vehicule_var.get()} -> {poste_id} / {cout['total']:.0f} FCFA"
        )
        messagebox.showinfo(
            "Transféré",
            f"Charge « Transport » de {cout['total']:,.0f} FCFA créée pour {poste_id} "
            f"({cout['cout_par_tonne']:.2f} FCFA/t sur {cout['tonnage_total_t']:.2f} t).\n\n"
            "Elle apparaîtra dans Coûts d'exploitation et sera prise en compte dans le "
            "prochain calcul du coût de revient de ce poste.".replace(",", " ")
        )
