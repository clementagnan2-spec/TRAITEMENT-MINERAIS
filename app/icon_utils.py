# -*- coding: utf-8 -*-
"""Utilitaire partagé pour localiser les ressources embarquées et appliquer
l'icône de l'application (lingot d'or) à n'importe quelle fenêtre Tk —
fenêtre principale ou boîtes de dialogue secondaires (Toplevel)."""

import os
import sys
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


def appliquer_icone(fenetre):
    """Applique l'icône lingot d'or à la fenêtre donnée (Tk ou Toplevel).
    Essaie d'abord le .ico (nécessaire pour un rendu correct dans la barre
    des tâches Windows), puis retombe sur le .png (multiplateforme) si le
    .ico échoue ou n'est pas supporté (cas normal sous Linux/macOS, où le
    format .ico natif Windows n'est pas pris en charge par Tk)."""
    ico_path = resource_path(os.path.join("assets", "icon.ico"))
    png_path = resource_path(os.path.join("assets", "icon.png"))

    icone_appliquee = False

    if os.path.exists(ico_path):
        try:
            fenetre.iconbitmap(ico_path)
            icone_appliquee = True
        except tk.TclError:
            pass

    if os.path.exists(png_path):
        try:
            img = tk.PhotoImage(file=png_path)
            _IMAGES_ICONES.append(img)  # garder une référence vivante
            fenetre.iconphoto(True, img)
            icone_appliquee = True
        except tk.TclError:
            pass

    return icone_appliquee
