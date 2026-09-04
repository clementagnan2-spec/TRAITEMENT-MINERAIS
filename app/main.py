# -*- coding: utf-8 -*-
"""
Traitement des Minerais — Boîte à outils du minéralurgiste
============================================================
Application de bureau (Tkinter) construite à partir de deux programmes de
formation :
  1. "Traitement des Minerais — De la caractérisation du gisement au
     flowsheet industriel" (formation de cadrage)
  2. "Programme de Formation Opérationnelle — Métiers de l'Usine de
     Traitement" (formation opérationnelle, par poste et par circuit)

Modules :
  1. Glossaire (recherche)
  2. Bilan matière / rendement / récupération (2 produits)
  3. Granulométrie — calcul de P80 (ou de tout Pxx) par interpolation
  4. Assistant de sélection d'une méthode de concentration
  5. Diagnostic flottation (formation de cadrage)
  6. Postes & Métiers — fiches de poste par circuit (opérationnel)
  7. Sécurité (HSE) — points de sécurité transversaux
  8. Quiz de validation des connaissances (les deux formations)

Lancer avec :  python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random

from data import (
    GLOSSAIRE,
    DIAGNOSTIC_FLOTTATION,
    QUIZ,
    QUIZ_OPERATIONS,
    POSTES,
    METIERS_BLOCS,
    METIERS_COMPETENCES,
    SECURITE_HSE,
    suggerer_methode,
)

APP_TITLE = "Traitement des Minerais — Boîte à outils du minéralurgiste"
BG = "#f4f6f5"
ACCENT = "#2f6f4f"
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_H2 = ("Segoe UI", 12, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 10)


class ScrollableFrame(ttk.Frame):
    """Un frame avec ascenseur vertical, pour les onglets longs."""

    def __init__(self, parent):
        super().__init__(parent)
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.body = ttk.Frame(canvas)

        self.body.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.body, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)

        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)


# ----------------------------------------------------------------------
# Onglet 1 — Glossaire
# ----------------------------------------------------------------------
class OngletGlossaire(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padding=16)

        ttk.Label(self, text="Glossaire du traitement des minerais", font=FONT_TITLE).pack(
            anchor="w"
        )
        ttk.Label(
            self,
            text="Tapez un mot-clé pour filtrer (ex. 'flottation', 'récupération', 'P80')...",
            font=FONT_BASE,
        ).pack(anchor="w", pady=(4, 8))

        self.recherche = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.recherche, font=FONT_BASE)
        entry.pack(fill="x", pady=(0, 10))
        entry.bind("<KeyRelease>", lambda e: self._filtrer())

        self.container = ScrollableFrame(self)
        self.container.pack(fill="both", expand=True)

        self._afficher(GLOSSAIRE)

    def _afficher(self, termes):
        for w in self.container.body.winfo_children():
            w.destroy()
        if not termes:
            ttk.Label(self.container.body, text="Aucun terme ne correspond.", font=FONT_BASE).pack(
                anchor="w", padx=4, pady=4
            )
            return
        for terme, definition in termes:
            bloc = ttk.Frame(self.container.body, padding=(4, 6))
            bloc.pack(fill="x", anchor="w")
            ttk.Label(bloc, text=terme, font=FONT_H2, foreground=ACCENT).pack(anchor="w")
            ttk.Label(
                bloc, text=definition, font=FONT_BASE, wraplength=760, justify="left"
            ).pack(anchor="w")
            ttk.Separator(self.container.body).pack(fill="x", pady=2)

    def _filtrer(self):
        q = self.recherche.get().strip().lower()
        if not q:
            self._afficher(GLOSSAIRE)
            return
        filtres = [
            (t, d) for t, d in GLOSSAIRE if q in t.lower() or q in d.lower()
        ]
        self._afficher(filtres)


# ----------------------------------------------------------------------
# Onglet 2 — Bilan matière / rendement / récupération
# ----------------------------------------------------------------------
class OngletBilan(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padding=16)

        ttk.Label(
            self, text="Bilan à deux produits — Rendement et récupération", font=FONT_TITLE
        ).pack(anchor="w")
        ttk.Label(
            self,
            text=(
                "Circuit simple : alimentation F (teneur f) → concentré C (teneur c) + "
                "stérile T (teneur t).\nY = (f - t) / (c - t) x 100      "
                "R = Y x c / f      Ratio d'enrichissement = c / f"
            ),
            font=FONT_BASE,
            justify="left",
        ).pack(anchor="w", pady=(4, 14))

        form = ttk.Frame(self)
        form.pack(anchor="w")

        self.f = tk.StringVar(value="2.5")
        self.c = tk.StringVar(value="28")
        self.t = tk.StringVar(value="0.15")

        for i, (label, var) in enumerate(
            [
                ("Teneur alimentation f (%)", self.f),
                ("Teneur concentré c (%)", self.c),
                ("Teneur stérile t (%)", self.t),
            ]
        ):
            ttk.Label(form, text=label, font=FONT_BASE).grid(
                row=i, column=0, sticky="w", pady=4, padx=(0, 10)
            )
            ttk.Entry(form, textvariable=var, width=14, font=FONT_BASE).grid(
                row=i, column=1, pady=4
            )

        ttk.Button(self, text="Calculer", command=self._calculer).pack(anchor="w", pady=14)

        self.resultat = tk.Text(
            self, height=10, width=90, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
        )
        self.resultat.pack(fill="both", expand=True)
        self.resultat.configure(state="disabled")

    def _ecrire(self, texte):
        self.resultat.configure(state="normal")
        self.resultat.delete("1.0", "end")
        self.resultat.insert("end", texte)
        self.resultat.configure(state="disabled")

    def _calculer(self):
        try:
            f = float(self.f.get().replace(",", "."))
            c = float(self.c.get().replace(",", "."))
            t = float(self.t.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir des nombres valides.")
            return

        if c == t:
            messagebox.showerror("Erreur", "La teneur du concentré ne peut pas être égale à "
                                            "celle du stérile (division par zéro).")
            return
        if f == 0:
            messagebox.showerror("Erreur", "La teneur de l'alimentation ne peut pas être nulle.")
            return

        y = (f - t) / (c - t) * 100
        r = y * c / f
        ratio = c / f if f != 0 else float("nan")

        # Bilan sur une base de 100 t d'alimentation, pour vérification.
        masse_alim = 100.0
        masse_conc = masse_alim * y / 100
        masse_sterile = masse_alim - masse_conc
        metal_alim = masse_alim * f / 100
        metal_conc = masse_conc * c / 100
        metal_sterile = masse_sterile * t / 100

        texte = (
            f"RÉSULTATS\n"
            f"---------\n"
            f"Rendement massique vers le concentré : Y = {y:.2f} %\n"
            f"Récupération métallurgique            : R = {r:.2f} %\n"
            f"Ratio d'enrichissement                 : c/f = {ratio:.2f}\n\n"
            f"VÉRIFICATION SUR BASE 100 t D'ALIMENTATION\n"
            f"-------------------------------------------\n"
            f"Masse alimentation   : {masse_alim:8.2f} t   |   métal contenu : {metal_alim:6.3f} t\n"
            f"Masse concentré      : {masse_conc:8.2f} t   |   métal contenu : {metal_conc:6.3f} t\n"
            f"Masse stérile        : {masse_sterile:8.2f} t   |   métal contenu : {metal_sterile:6.3f} t\n"
            f"Fermeture du bilan métal (conc.+stér. / alim.) : "
            f"{(metal_conc + metal_sterile) / metal_alim * 100:.2f} % (doit être proche de 100 %)\n"
        )
        self._ecrire(texte)


# ----------------------------------------------------------------------
# Onglet 3 — Granulométrie / P80
# ----------------------------------------------------------------------
class OngletGranulo(ttk.Frame):
    """Table de tailles / % passant cumulé, avec calcul d'un Pxx par
    interpolation linéaire (comme dans l'exercice 2 du programme)."""

    DEFAUT = [
        (1000, 98), (500, 85), (425, 78), (300, 60),
        (212, 45), (150, 30), (106, 18), (75, 10),
    ]

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padding=16)

        ttk.Label(self, text="Granulométrie — calcul d'un Pxx (ex. P80)", font=FONT_TITLE).pack(
            anchor="w"
        )
        ttk.Label(
            self,
            text=(
                "Saisissez la distribution taille de maille (µm) / % passant cumulé, "
                "une ligne 'taille,passant' par ligne."
            ),
            font=FONT_BASE,
        ).pack(anchor="w", pady=(4, 10))

        cadre = ttk.Frame(self)
        cadre.pack(fill="both", expand=False)

        self.txt = tk.Text(cadre, height=10, width=30, font=FONT_MONO)
        self.txt.pack(side="left", fill="y")
        for taille, passant in self.DEFAUT:
            self.txt.insert("end", f"{taille},{passant}\n")

        droite = ttk.Frame(cadre, padding=(16, 0))
        droite.pack(side="left", fill="both", expand=True)

        ligne = ttk.Frame(droite)
        ligne.pack(anchor="w", pady=(0, 10))
        ttk.Label(ligne, text="Pxx recherché (ex. 80 pour P80) : ", font=FONT_BASE).pack(
            side="left"
        )
        self.pxx = tk.StringVar(value="80")
        ttk.Entry(ligne, textvariable=self.pxx, width=8, font=FONT_BASE).pack(side="left")

        ttk.Button(droite, text="Calculer le Pxx", command=self._calculer).pack(anchor="w")

        self.resultat = tk.Text(
            droite, height=8, width=60, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1
        )
        self.resultat.pack(fill="both", expand=True, pady=(10, 0))
        self.resultat.configure(state="disabled")

    def _lire_table(self):
        lignes = self.txt.get("1.0", "end").strip().splitlines()
        points = []
        for ligne in lignes:
            ligne = ligne.strip()
            if not ligne:
                continue
            sep = "," if "," in ligne else None
            if sep is None and ";" in ligne:
                sep = ";"
            if sep is None:
                parts = ligne.split()
            else:
                parts = ligne.split(sep)
            if len(parts) != 2:
                raise ValueError(f"Ligne invalide : '{ligne}'")
            taille = float(parts[0].strip().replace(",", "."))
            passant = float(parts[1].strip().replace(",", "."))
            points.append((taille, passant))
        # tri par % passant croissant
        points.sort(key=lambda p: p[1])
        return points

    def _ecrire(self, texte):
        self.resultat.configure(state="normal")
        self.resultat.delete("1.0", "end")
        self.resultat.insert("end", texte)
        self.resultat.configure(state="disabled")

    def _calculer(self):
        try:
            points = self._lire_table()
            cible = float(self.pxx.get().replace(",", "."))
        except ValueError as e:
            messagebox.showerror("Erreur", f"Données invalides : {e}")
            return

        if not points:
            messagebox.showerror("Erreur", "Aucune donnée saisie.")
            return

        if cible <= points[0][1]:
            messagebox.showerror(
                "Erreur",
                f"P{cible:.0f} est en dehors de la plage de données "
                f"({points[0][1]} % minimum).",
            )
            return
        if cible >= points[-1][1]:
            messagebox.showerror(
                "Erreur",
                f"P{cible:.0f} est en dehors de la plage de données "
                f"({points[-1][1]} % maximum).",
            )
            return

        # Recherche des deux points encadrant la cible
        for i in range(len(points) - 1):
            taille1, passant1 = points[i]
            taille2, passant2 = points[i + 1]
            if passant1 <= cible <= passant2:
                pxx = taille1 + (cible - passant1) / (passant2 - passant1) * (taille2 - taille1)
                texte = (
                    f"P{cible:.0f} ≈ {pxx:.1f} µm\n\n"
                    f"Interpolation linéaire entre :\n"
                    f"  {taille1:.0f} µm → {passant1:.1f} % passant\n"
                    f"  {taille2:.0f} µm → {passant2:.1f} % passant\n\n"
                    f"À comparer à la maille de libération déterminée par analyse "
                    f"minéralogique (Module 1) : si P{cible:.0f} lui est supérieur, une "
                    f"partie du minéral reste sous forme de particules mixtes non "
                    f"libérées, ce qui plafonnera la récupération atteignable en aval."
                )
                self._ecrire(texte)
                return


# ----------------------------------------------------------------------
# Onglet 4 — Assistant de sélection de méthode de concentration
# ----------------------------------------------------------------------
class OngletSelection(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padding=16)

        ttk.Label(
            self, text="Assistant de sélection d'une méthode de concentration", font=FONT_TITLE
        ).pack(anchor="w")
        ttk.Label(
            self,
            text="Cochez les propriétés physiques distinctives du minéral cible par rapport "
                 "à la gangue.",
            font=FONT_BASE,
        ).pack(anchor="w", pady=(4, 14))

        self.densite = tk.BooleanVar()
        self.magnetique = tk.BooleanVar()
        self.conducteur = tk.BooleanVar()
        self.mouillabilite = tk.BooleanVar()
        self.fine = tk.BooleanVar()

        options = [
            (self.densite, "Écart de densité important avec la gangue"),
            (self.magnetique, "Susceptibilité magnétique exploitable "
                               "(ferro- ou paramagnétique)"),
            (self.conducteur, "Conductivité électrique de surface distincte"),
            (self.mouillabilite, "Mouillabilité de surface modifiable par réactifs "
                                  "(flottation envisageable)"),
            (self.fine, "Minéral finement disséminé dans la gangue (nécessite un "
                        "broyage fin)"),
        ]
        for var, label in options:
            ttk.Checkbutton(self, text=label, variable=var, style="TCheckbutton").pack(
                anchor="w", pady=3
            )

        ttk.Button(self, text="Suggérer une méthode", command=self._suggerer).pack(
            anchor="w", pady=14
        )

        self.resultat = tk.Text(
            self, height=8, width=90, font=FONT_MONO, bg="#ffffff", relief="solid", borderwidth=1,
            wrap="word"
        )
        self.resultat.pack(fill="both", expand=True)
        self.resultat.configure(state="disabled")

    def _suggerer(self):
        methode, justification = suggerer_methode(
            self.densite.get(),
            self.magnetique.get(),
            self.conducteur.get(),
            self.mouillabilite.get(),
            self.fine.get(),
        )
        texte = f"MÉTHODE SUGGÉRÉE : {methode}\n\nJustification :\n{justification}\n\n" \
                "Rappel : en pratique industrielle, un flowsheet enchaîne souvent " \
                "plusieurs méthodes, de la plus grossière/économique vers la plus " \
                "fine/sélective (Module 3.5)."
        self.resultat.configure(state="normal")
        self.resultat.delete("1.0", "end")
        self.resultat.insert("end", texte)
        self.resultat.configure(state="disabled")


# ----------------------------------------------------------------------
# Onglet 5 — Diagnostic flottation
# ----------------------------------------------------------------------
class OngletDiagnostic(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padding=16)

        ttk.Label(
            self,
            text="Checklist de diagnostic — baisse de récupération en flottation",
            font=FONT_TITLE,
        ).pack(anchor="w")
        ttk.Label(
            self,
            text="À vérifier dans l'ordre : du plus en amont vers le plus en aval, du plus "
                 "facilement mesurable vers le plus complexe.",
            font=FONT_BASE,
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(4, 14))

        container = ScrollableFrame(self)
        container.pack(fill="both", expand=True)

        for titre, detail in DIAGNOSTIC_FLOTTATION:
            var = tk.BooleanVar()
            bloc = ttk.Frame(container.body, padding=(4, 6))
            bloc.pack(fill="x", anchor="w")
            ttk.Checkbutton(bloc, variable=var, text=titre, style="TCheckbutton").pack(
                anchor="w"
            )
            ttk.Label(
                bloc, text=detail, font=FONT_BASE, wraplength=740, justify="left"
            ).pack(anchor="w", padx=(24, 0))
            ttk.Separator(container.body).pack(fill="x", pady=4)


# ----------------------------------------------------------------------
# Onglet 6 — Postes & Métiers (formation opérationnelle)
# ----------------------------------------------------------------------
class OngletPostes(ttk.Frame):
    PARTIES = ["Toutes"] + sorted({p["partie"] for p in POSTES})

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padding=16)

        ttk.Label(self, text="Postes & Métiers de l'usine", font=FONT_TITLE).pack(anchor="w")
        ttk.Label(
            self,
            text="Fiches par circuit/poste : contrôles de routine, paramètres à surveiller, "
                 "anomalies fréquentes, missions et compétences.",
            font=FONT_BASE,
        ).pack(anchor="w", pady=(4, 10))

        filtre_frame = ttk.Frame(self)
        filtre_frame.pack(anchor="w", pady=(0, 10))
        ttk.Label(filtre_frame, text="Filtrer par partie : ", font=FONT_BASE).pack(side="left")
        self.partie_var = tk.StringVar(value="Toutes")
        combo = ttk.Combobox(
            filtre_frame, textvariable=self.partie_var, values=self.PARTIES,
            state="readonly", width=28, font=FONT_BASE
        )
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self._afficher())

        self.container = ScrollableFrame(self)
        self.container.pack(fill="both", expand=True)

        self._afficher()

    def _ligne_liste(self, parent, titre, items):
        if not items:
            return
        ttk.Label(parent, text=titre, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 0))
        for item in items:
            if isinstance(item, tuple):
                texte = f"• {item[0]} — {item[1]}"
            else:
                texte = f"• {item}"
            ttk.Label(
                parent, text=texte, font=FONT_BASE, wraplength=740, justify="left"
            ).pack(anchor="w", padx=(10, 0))

    def _afficher(self):
        for w in self.container.body.winfo_children():
            w.destroy()

        choix = self.partie_var.get()
        postes = POSTES if choix == "Toutes" else [p for p in POSTES if p["partie"] == choix]

        partie_courante = None
        for poste in postes:
            if poste["partie"] != partie_courante:
                partie_courante = poste["partie"]
                ttk.Label(
                    self.container.body, text=partie_courante, font=FONT_TITLE, foreground=ACCENT
                ).pack(anchor="w", pady=(14, 4))

            bloc = ttk.Frame(self.container.body, padding=(4, 8))
            bloc.pack(fill="x", anchor="w")
            ttk.Label(
                bloc, text=f"{poste['id']} — {poste['titre']}", font=FONT_H2
            ).pack(anchor="w")
            if poste.get("description"):
                ttk.Label(
                    bloc, text=poste["description"], font=FONT_BASE, wraplength=740,
                    justify="left"
                ).pack(anchor="w", pady=(2, 0))

            self._ligne_liste(bloc, "Contrôles de routine", poste.get("controles"))
            self._ligne_liste(bloc, "Paramètres à surveiller", poste.get("parametres"))
            self._ligne_liste(bloc, "Anomalies fréquentes", poste.get("anomalies"))
            self._ligne_liste(bloc, "Missions type", poste.get("missions"))
            self._ligne_liste(bloc, "Compétences visées", poste.get("competences"))
            self._ligne_liste(bloc, "Outils clés", poste.get("outils"))
            self._ligne_liste(bloc, "Points de sécurité clés", poste.get("securite"))

            ttk.Separator(self.container.body).pack(fill="x", pady=6)

        # Tables métiers -> blocs / compétences, affichées en bas de la vue complète
        if choix == "Toutes":
            ttk.Label(
                self.container.body, text="Métier / poste → blocs recommandés", font=FONT_TITLE,
                foreground=ACCENT
            ).pack(anchor="w", pady=(14, 4))
            for metier, blocs in METIERS_BLOCS:
                ttk.Label(
                    self.container.body, text=f"• {metier} → {blocs}", font=FONT_BASE,
                    wraplength=740, justify="left"
                ).pack(anchor="w", padx=(10, 0), pady=1)

            ttk.Label(
                self.container.body,
                text="Métier / poste → compétence opérationnelle visée",
                font=FONT_TITLE, foreground=ACCENT
            ).pack(anchor="w", pady=(14, 4))
            for metier, comp in METIERS_COMPETENCES:
                ttk.Label(
                    self.container.body, text=f"• {metier} : {comp}", font=FONT_BASE,
                    wraplength=740, justify="left"
                ).pack(anchor="w", padx=(10, 0), pady=1)


# ----------------------------------------------------------------------
# Onglet 7 — Sécurité (HSE)
# ----------------------------------------------------------------------
class OngletSecurite(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padding=16)

        ttk.Label(self, text="Sécurité et bonnes pratiques (HSE)", font=FONT_TITLE).pack(
            anchor="w"
        )
        ttk.Label(
            self,
            text="Points de sécurité transversaux, applicables à tous les postes de l'usine.",
            font=FONT_BASE,
        ).pack(anchor="w", pady=(4, 14))

        container = ScrollableFrame(self)
        container.pack(fill="both", expand=True)

        for titre, detail in SECURITE_HSE:
            bloc = ttk.Frame(container.body, padding=(4, 8))
            bloc.pack(fill="x", anchor="w")
            ttk.Label(bloc, text=f"⚠ {titre}", font=FONT_H2, foreground="#a6371f").pack(
                anchor="w"
            )
            ttk.Label(
                bloc, text=detail, font=FONT_BASE, wraplength=740, justify="left"
            ).pack(anchor="w", padx=(20, 0))
            ttk.Separator(container.body).pack(fill="x", pady=4)

        rappel = ttk.Frame(container.body, padding=(4, 10))
        rappel.pack(fill="x", anchor="w")
        ttk.Label(
            rappel,
            text="Ces points s'ajoutent aux consignes de sécurité spécifiques à chaque poste "
                 "(voir l'onglet « Postes & Métiers »), en particulier pour la flottation "
                 "(réactifs), la lixiviation (cyanure) et l'autoclave (pression).",
            font=FONT_BASE, wraplength=740, justify="left",
        ).pack(anchor="w")


# ----------------------------------------------------------------------
# Onglet 8 — Quiz
# ----------------------------------------------------------------------
class OngletQuiz(ttk.Frame):
    CATEGORIES = ["Les deux formations", "Formation de cadrage", "Formation opérationnelle"]

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(padding=16)
        self.banque = list(QUIZ) + list(QUIZ_OPERATIONS)
        self.questions = list(self.banque)
        self.index = 0
        self.score = 0

        self.titre = ttk.Label(self, text="Quiz de validation des connaissances", font=FONT_TITLE)
        self.titre.pack(anchor="w")

        cat_frame = ttk.Frame(self)
        cat_frame.pack(anchor="w", pady=(4, 4))
        ttk.Label(cat_frame, text="Catégorie : ", font=FONT_BASE).pack(side="left")
        self.categorie_var = tk.StringVar(value=self.CATEGORIES[0])
        combo = ttk.Combobox(
            cat_frame, textvariable=self.categorie_var, values=self.CATEGORIES,
            state="readonly", width=26, font=FONT_BASE
        )
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self._recommencer())

        self.progression = ttk.Label(self, text="", font=FONT_BASE)
        self.progression.pack(anchor="w", pady=(4, 14))

        self.question_label = ttk.Label(
            self, text="", font=FONT_H2, wraplength=760, justify="left"
        )
        self.question_label.pack(anchor="w", pady=(0, 10))

        self.choix_var = tk.IntVar(value=-1)
        self.boutons_choix = []
        for i in range(4):
            rb = ttk.Radiobutton(self, text="", variable=self.choix_var, value=i)
            rb.pack(anchor="w", pady=3)
            self.boutons_choix.append(rb)

        barre = ttk.Frame(self)
        barre.pack(anchor="w", pady=16)
        ttk.Button(barre, text="Valider", command=self._valider).pack(side="left", padx=(0, 8))
        ttk.Button(barre, text="Recommencer", command=self._recommencer).pack(side="left")

        self.feedback = tk.Text(
            self, height=6, width=90, font=FONT_BASE, bg="#ffffff", relief="solid", borderwidth=1,
            wrap="word"
        )
        self.feedback.pack(fill="both", expand=True)
        self.feedback.configure(state="disabled")

        self._recommencer()

    def _recommencer(self):
        choix = self.categorie_var.get()
        if choix == "Formation de cadrage":
            self.questions = [q for q in self.banque if q["categorie"] == "Formation de cadrage"]
        elif choix == "Formation opérationnelle":
            self.questions = [q for q in self.banque if q["categorie"] == "Formation opérationnelle"]
        else:
            self.questions = list(self.banque)
        random.shuffle(self.questions)
        self.index = 0
        self.score = 0
        self._afficher_question()

    def _afficher_question(self):
        self.choix_var.set(-1)
        self._ecrire_feedback("")
        if self.index >= len(self.questions):
            self.question_label.configure(text="")
            for rb in self.boutons_choix:
                rb.pack_forget()
            self.progression.configure(
                text=f"Quiz terminé — score final : {self.score} / {len(self.questions)}"
            )
            self._ecrire_feedback(
                f"Bravo, vous avez terminé le quiz avec {self.score} bonnes réponses sur "
                f"{len(self.questions)}. Cliquez sur 'Recommencer' pour relancer un nouveau tirage."
            )
            return

        for rb in self.boutons_choix:
            rb.pack(anchor="w", pady=3)

        q = self.questions[self.index]
        self.progression.configure(
            text=f"Question {self.index + 1} / {len(self.questions)}   —   Score : "
                 f"{self.score}   —   [{q['categorie']}]"
        )
        self.question_label.configure(text=q["question"])
        for i, choix in enumerate(q["choices"]):
            self.boutons_choix[i].configure(text=choix)

    def _ecrire_feedback(self, texte):
        self.feedback.configure(state="normal")
        self.feedback.delete("1.0", "end")
        self.feedback.insert("end", texte)
        self.feedback.configure(state="disabled")

    def _valider(self):
        if self.index >= len(self.questions):
            return
        choix = self.choix_var.get()
        if choix == -1:
            messagebox.showinfo("Quiz", "Sélectionnez une réponse avant de valider.")
            return
        q = self.questions[self.index]
        correct = choix == q["correct"]
        if correct:
            self.score += 1
            self._ecrire_feedback("✔ Bonne réponse !\n\n" + q["explication"])
        else:
            bonne = q["choices"][q["correct"]]
            self._ecrire_feedback(
                f"✘ Pas tout à fait. La bonne réponse était : « {bonne} »\n\n{q['explication']}"
            )
        self.index += 1
        self.after(1800, self._afficher_question)


# ----------------------------------------------------------------------
# Fenêtre principale
# ----------------------------------------------------------------------
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("900x680")
        self.minsize(760, 560)
        self.configure(bg=BG)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=BG, font=FONT_BASE)
        style.configure("TNotebook", background=BG)
        style.configure("TFrame", background=BG)
        style.configure("TCheckbutton", background=BG, font=FONT_BASE)

        entete = ttk.Frame(self, padding=(16, 14, 16, 4))
        entete.pack(fill="x")
        ttk.Label(entete, text=APP_TITLE, font=FONT_TITLE, foreground=ACCENT).pack(anchor="w")
        ttk.Label(
            entete,
            text="Basé sur « Traitement des Minerais — De la caractérisation du gisement au "
                 "flowsheet industriel » et sur « Programme de Formation Opérationnelle — "
                 "Métiers de l'Usine de Traitement »",
            font=FONT_BASE,
        ).pack(anchor="w")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        notebook.add(OngletGlossaire(notebook), text="  Glossaire  ")
        notebook.add(OngletBilan(notebook), text="  Bilan matière  ")
        notebook.add(OngletGranulo(notebook), text="  Granulométrie (P80)  ")
        notebook.add(OngletSelection(notebook), text="  Choix de méthode  ")
        notebook.add(OngletDiagnostic(notebook), text="  Diagnostic flottation  ")
        notebook.add(OngletPostes(notebook), text="  Postes & Métiers  ")
        notebook.add(OngletSecurite(notebook), text="  Sécurité (HSE)  ")
        notebook.add(OngletQuiz(notebook), text="  Quiz  ")


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
