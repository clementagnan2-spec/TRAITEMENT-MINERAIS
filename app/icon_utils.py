# -*- coding: utf-8 -*-
"""Utilitaire partagé pour localiser les ressources embarquées et appliquer
l'icône de l'application (camion minier) à n'importe quelle fenêtre Tk —
fenêtre principale ou boîtes de dialogue secondaires (Toplevel)."""

import os
import sys
import traceback
import tkinter as tk

# Référence conservée pour empêcher le garbage collector de libérer les
# images PhotoImage tant que l'application tourne (bug classique Tkinter :
# l'icône disparaît si l'objet Python est détruit, même si la fenêtre
# l'utilise encore).
_IMAGES_ICONES = []


def resource_path(chemin_relatif):
    """Retourne le chemin absolu d'une ressource, que l'application tourne
    depuis le code source ou depuis un .exe compilé par PyInstaller
    (le mode dossier comme le mode --onefile utilisent sys._MEIPASS pour
    localiser les fichiers de données embarqués)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, chemin_relatif)


def _chemin_log():
    """Fichier journal placé à côté de l'exécutable (ou du script), pour
    diagnostiquer précisément ce qui se passe lors du chargement de
    l'icône sur la machine de l'utilisateur."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "icon_debug.log")


def _log(lignes):
    try:
        with open(_chemin_log(), "a", encoding="utf-8") as f:
            f.write("\n".join(lignes) + "\n" + ("-" * 60) + "\n")
    except Exception:
        pass  # le diagnostic ne doit jamais faire planter l'appli


def appliquer_icone(fenetre):
    """Applique l'icône de l'application à la fenêtre donnée (Tk ou
    Toplevel), et journalise chaque étape dans icon_debug.log à côté de
    l'exécutable pour pouvoir diagnostiquer un éventuel échec silencieux."""
    ico_path = resource_path(os.path.join("assets", "icon.ico"))
    png_path = resource_path(os.path.join("assets", "icon.png"))

    lignes = [
        f"appliquer_icone() sur {fenetre}",
        f"  sys.frozen = {getattr(sys, 'frozen', False)}",
        f"  sys._MEIPASS = {getattr(sys, '_MEIPASS', '(non défini)')}",
        f"  ico_path = {ico_path}",
        f"  ico_path existe = {os.path.exists(ico_path)}",
        f"  png_path = {png_path}",
        f"  png_path existe = {os.path.exists(png_path)}",
    ]

    icone_appliquee = False

    if os.path.exists(ico_path):
        try:
            fenetre.iconbitmap(ico_path)
            lignes.append("  iconbitmap(ico_path) : SUCCÈS")
            icone_appliquee = True
        except Exception as e:
            lignes.append(f"  iconbitmap(ico_path) : ÉCHEC — {type(e).__name__}: {e}")
            lignes.append("  " + traceback.format_exc().replace("\n", "\n  "))
    else:
        lignes.append("  iconbitmap non tenté : fichier .ico introuvable")

    if os.path.exists(png_path):
        try:
            img = tk.PhotoImage(file=png_path)
            _IMAGES_ICONES.append(img)  # garder une référence vivante
            fenetre.iconphoto(True, img)
            lignes.append("  iconphoto(png_path) : SUCCÈS")
            icone_appliquee = True
        except Exception as e:
            lignes.append(f"  iconphoto(png_path) : ÉCHEC — {type(e).__name__}: {e}")
            lignes.append("  " + traceback.format_exc().replace("\n", "\n  "))
    else:
        lignes.append("  iconphoto non tenté : fichier .png introuvable")

    resultat_texte = "icône appliquée" if icone_appliquee else "AUCUNE icône appliquée"
    lignes.append(f"  RÉSULTAT FINAL : {resultat_texte}")
    _log(lignes)

    return icone_appliquee

