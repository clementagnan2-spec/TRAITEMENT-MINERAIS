# -*- coding: utf-8 -*-
"""Saisie et consultation des relevés de paramètres d'exploitation réels."""

import tkinter as tk
from tkinter import ttk, messagebox

import db
import analyse_indicateurs as analyse
from data_postes import POSTES_REF, obtenir_bareme
from ui_widgets import rendre_defilant

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SECTION = ("Segoe UI", 12, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
ACCENT = "#2f6f4f"
ALERTE = "#a6371f"

COULEUR_CRITIQUE = "#c0392b"
COULEUR_ATTENTION = "#c98a1f"
COULEUR_INFO = "#4a6a83"
COULEUR_OK = "#2f6f4f"
COULEUR_SANS_DONNEE = "#b6bcbb"

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

        corps = ttk.Frame(self)
        corps.pack(fill="both", expand=True)

        colonne_gauche = ttk.Frame(corps)
        colonne_gauche.pack(side="left", fill="both", expand=True)

        colonne_droite = ttk.Frame(corps, width=360)
        colonne_droite.pack(side="right", fill="y", padx=(16, 0))
        colonne_droite.pack_propagate(False)
        self._construire_panneau_analyse(colonne_droite)

        form = ttk.Frame(colonne_gauche)
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

        ttk.Button(colonne_gauche, text="Enregistrer le relevé", command=self._enregistrer).pack(
            anchor="w", pady=14
        )

        ttk.Separator(colonne_gauche).pack(fill="x", pady=6)
        filtre_frame = ttk.Frame(colonne_gauche)
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
        self.tree = ttk.Treeview(colonne_gauche, columns=cols, show="headings", height=12)
        entetes = {"conformite": "Conformité"}
        largeurs = (140, 190, 200, 80, 60, 100, 150)
        for c, w in zip(cols, largeurs):
            self.tree.heading(c, text=entetes.get(c, c.replace("_", " ").capitalize()))
            self.tree.column(c, width=w, anchor="w")
        self.tree.tag_configure("non_conforme", background="#fbe4e0", foreground=ALERTE)
        self.tree.pack(fill="both", expand=True, pady=(8, 0))

        self._rafraichir_historique()

    # -------------------------------------------------------------
    # Panneau d'analyse combinée (droite) : graphique + lecture croisée
    # -------------------------------------------------------------
    def _construire_panneau_analyse(self, parent):
        # Panneau défilant : si le contenu (graphique + commentaires) est
        # plus haut que la fenêtre, tout reste accessible par ascenseur au
        # lieu d'être coupé en bas de l'écran.
        interieur = rendre_defilant(parent)
        interieur.configure(padding=(0, 0, 8, 0))

        ttk.Label(
            interieur, text="Analyse combinée des indicateurs", font=FONT_SECTION,
            foreground=ACCENT, wraplength=330
        ).pack(anchor="w", pady=(0, 6))

        ttk.Label(interieur, text="Conformité récente par poste", font=FONT_BASE).pack(
            anchor="w"
        )
        self.canvas_graphique = tk.Canvas(
            interieur, width=326, height=90, bg="white", highlightthickness=1,
            highlightbackground="#d8dcda"
        )
        self.canvas_graphique.pack(anchor="w", pady=(4, 6))

        legende = ttk.Frame(interieur)
        legende.pack(anchor="w", pady=(0, 8))
        for couleur, texte in (
            (COULEUR_OK, "Conforme"), (COULEUR_ATTENTION, "À surveiller"),
            (COULEUR_CRITIQUE, "Hors norme"), (COULEUR_SANS_DONNEE, "Sans donnée"),
        ):
            bloc = ttk.Frame(legende)
            bloc.pack(side="left", padx=(0, 8))
            puce = tk.Canvas(bloc, width=9, height=9, highlightthickness=0)
            puce.create_rectangle(0, 0, 9, 9, fill=couleur, outline=couleur)
            puce.pack(side="left")
            ttk.Label(bloc, text=texte, font=("Segoe UI", 8)).pack(side="left", padx=(3, 0))

        entete_lecture = ttk.Frame(interieur)
        entete_lecture.pack(anchor="w", fill="x", pady=(2, 0))
        ttk.Label(entete_lecture, text="Lecture croisée des indicateurs", font=FONT_BASE).pack(
            side="left"
        )
        ttk.Button(
            entete_lecture, text="Actualiser", width=10, command=self._rafraichir_analyse
        ).pack(side="right")
        ttk.Label(
            interieur,
            text="Repère des situations que chaque relevé pris isolément ne montre pas.",
            font=("Segoe UI", 8), foreground="#777777", wraplength=330, justify="left",
        ).pack(anchor="w", pady=(1, 6))

        self.texte_alertes = tk.Text(
            interieur, width=40, height=16, font=FONT_SMALL, wrap="word",
            relief="flat", background="#f7f8f7", padx=8, pady=8, state="disabled",
            cursor="arrow", borderwidth=0,
        )
        self.texte_alertes.pack(anchor="w", fill="x", pady=(0, 8))

        self.texte_alertes.tag_configure(
            "critique", foreground=COULEUR_CRITIQUE, font=("Segoe UI", 9, "bold")
        )
        self.texte_alertes.tag_configure(
            "attention", foreground=COULEUR_ATTENTION, font=("Segoe UI", 9, "bold")
        )
        self.texte_alertes.tag_configure(
            "info", foreground=COULEUR_INFO, font=("Segoe UI", 9, "bold")
        )
        self.texte_alertes.tag_configure("corps", foreground="#2b2b2b")

        ttk.Label(
            interieur,
            text="Lecture automatique indicative, fondée sur des règles simples : elle "
                 "ne remplace pas le jugement d'un opérateur ou d'un responsable process "
                 "qualifié.",
            font=("Segoe UI", 8), foreground="#888888", wraplength=330, justify="left",
        ).pack(anchor="w", pady=(0, 4))

    def _rafraichir_analyse(self):
        releves = db.lister_releves(limite=300)
        self._dessiner_graphique(releves)
        self._afficher_alertes(releves)

    def _dessiner_graphique(self, releves):
        c = self.canvas_graphique
        c.delete("all")
        scores = [s for s in analyse.scores_conformite_par_poste(releves) if s[3] > 0][:8]

        largeur = int(c["width"])
        marge_gauche = 34
        marge_droite = 10
        marge_haut = 6
        marge_bas = 16
        hauteur_ligne = 22

        if not scores:
            hauteur = 60
            c.configure(height=hauteur)
            c.create_text(
                largeur / 2, hauteur / 2,
                text="Aucun relevé avec barème défini pour l'instant.",
                font=FONT_SMALL, fill="#888888", width=largeur - 20,
            )
            return

        n = len(scores)
        hauteur = marge_haut + marge_bas + n * hauteur_ligne
        c.configure(height=hauteur)
        zone_h = hauteur - marge_haut - marge_bas
        pas = zone_h / n
        hauteur_barre = max(10, pas * 0.65)

        # Axe de référence (0% .. 100%)
        for frac, etiquette in ((0.0, "0%"), (0.5, "50%"), (1.0, "100%")):
            x = marge_gauche + frac * (largeur - marge_gauche - marge_droite)
            c.create_line(x, marge_haut, x, hauteur - marge_bas, fill="#eef0ef")
            c.create_text(x, hauteur - 2, text=etiquette, font=("Segoe UI", 7),
                           fill="#999999", anchor="s")

        for i, (poste_id, titre, nb_conf, nb_total, score) in enumerate(scores):
            y_centre = marge_haut + pas * i + pas / 2
            y0 = y_centre - hauteur_barre / 2
            y1 = y_centre + hauteur_barre / 2
            x0 = marge_gauche
            largeur_dispo = largeur - marge_gauche - marge_droite

            if score >= 0.8:
                couleur = COULEUR_OK
            elif score >= 0.5:
                couleur = COULEUR_ATTENTION
            else:
                couleur = COULEUR_CRITIQUE

            x1 = x0 + largeur_dispo * score
            c.create_rectangle(x0, y0, largeur - marge_droite, y1, fill="#f0f1f0",
                                outline="")
            c.create_rectangle(x0, y0, x1, y1, fill=couleur, outline="")
            c.create_text(
                marge_gauche - 4, y_centre, text=poste_id, font=("Segoe UI", 8, "bold"),
                anchor="e", fill="#444444"
            )
            c.create_text(
                x1 + 4 if x1 + 30 < largeur - marge_droite else x1 - 4,
                y_centre, text=f"{round(score * 100)}%", font=("Segoe UI", 7),
                anchor="w" if x1 + 30 < largeur - marge_droite else "e",
                fill="#444444"
            )

    def _afficher_alertes(self, releves):
        alertes = analyse.generer_alertes(releves)
        self.texte_alertes.configure(state="normal")
        self.texte_alertes.delete("1.0", "end")
        for i, a in enumerate(alertes):
            if i > 0:
                self.texte_alertes.insert("end", "\n\n")
            icone = analyse.NIVEAU_ICONE.get(a["niveau"], "•")
            self.texte_alertes.insert("end", f"{icone} ", a["niveau"])
            self.texte_alertes.insert("end", a["texte"], "corps")
        self.texte_alertes.configure(state="disabled")

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
        self._rafraichir_analyse()
