# Traitement des Minerais — Boîte à outils du minéralurgiste

Logiciel de bureau (Windows/Linux/macOS) construit à partir de deux
programmes de formation :

1. *« Traitement des Minerais — De la caractérisation du gisement au
   flowsheet industriel »* (formation de cadrage, théorique et méthodologique)
2. *« Programme de Formation Opérationnelle — Métiers de l'Usine de
   Traitement »* (formation opérationnelle, par poste et par circuit :
   concassage, broyage, concentration, lixiviation, CIL/CIP, finition, HSE)

## Fonctionnalités

| Onglet | Contenu |
|---|---|
| **Glossaire** | Recherche dans ~47 termes clés (théoriques + opérationnels : LOTO, CIL/CIP, ORP, heap leaching...) |
| **Bilan matière** | Calcul du rendement massique, de la récupération métallurgique et du ratio d'enrichissement (bilan à 2 produits), avec vérification du bilan métal sur base 100 t |
| **Granulométrie (P80)** | Interpolation d'un Pxx (ex. P80) à partir d'une courbe granulométrique saisie |
| **Choix de méthode** | Assistant de sélection d'une méthode de concentration (gravimétrie, magnétique, électrostatique, flottation) à partir des propriétés physiques du minéral |
| **Diagnostic flottation** | Checklist méthodique pour diagnostiquer une baisse de récupération, de l'amont vers l'aval |
| **Postes & Métiers** | Fiches par circuit/poste (concassage, broyage, magnétique, gravimétrique, flottation, lixiviation tas/autoclave/cuve, CIL/CIP, finition, rôles transversaux) : contrôles de routine, paramètres à surveiller, anomalies fréquentes, missions et compétences ; filtrable par partie A à E ; tables métier → blocs recommandés et métier → compétence visée |
| **Sécurité (HSE)** | Points de sécurité transversaux : consignation (LOTO), EPI, FDS, procédures d'urgence, culture du reporting |
| **Quiz** | Quiz de validation des connaissances (17 questions), filtrable par catégorie : formation de cadrage, formation opérationnelle, ou les deux |

## Lancer le logiciel depuis le code source

Prérequis : Python 3.9+ (Tkinter est inclus dans l'installateur standard de
Python sous Windows ; sous Linux, installez le paquet `python3-tk` si besoin).

```bash
git clone <url-de-ce-depot>
cd traitement-minerais
python app/main.py
```

## Obtenir le fichier .exe (compilation automatique sur GitHub)

Ce dépôt contient un workflow **GitHub Actions**
(`.github/workflows/build.yml`) qui compile automatiquement l'application en
`.exe` Windows avec PyInstaller, **sans que vous ayez besoin d'une machine
Windows ni d'installer quoi que ce soit localement** :

1. Créez un dépôt GitHub et poussez le contenu de ce dossier dedans :
   ```bash
   git init
   git add .
   git commit -m "Traitement des Minerais - boîte à outils"
   git branch -M main
   git remote add origin https://github.com/<votre-compte>/<votre-depot>.git
   git push -u origin main
   ```
2. Sur GitHub, ouvrez l'onglet **Actions** du dépôt : le workflow
   « Compiler le .exe (Windows) » se lance automatiquement à chaque `push`
   sur `main` (il peut aussi être relancé manuellement via le bouton
   *Run workflow*).
3. Une fois le workflow terminé (icône verte ✅), ouvrez le run correspondant
   puis téléchargez l'artefact **`TraitementMinerais-exe`** : il contient
   `TraitementMinerais.exe`, prêt à l'emploi sur Windows.

### Publier une release téléchargeable (optionnel)

Si vous créez et poussez un tag de version, par exemple :

```bash
git tag v1.0.0
git push origin v1.0.0
```

le workflow joint automatiquement `TraitementMinerais.exe` à une **Release
GitHub**, ce qui donne un lien de téléchargement stable et permanent pour vos
utilisateurs (page *Releases* du dépôt).

## Compiler soi-même en local (alternatif)

```bash
pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --name TraitementMinerais app/main.py
# L'exécutable apparaît dans dist/
```

## Structure du projet

```
traitement-minerais/
├── app/
│   ├── main.py        # Interface graphique (Tkinter) et logique de l'appli
│   └── data.py         # Glossaire, quiz, checklist, règles métier
├── .github/workflows/
│   └── build.yml        # Compilation automatique du .exe sur GitHub Actions
├── requirements.txt
└── README.md
```

## Contenu pédagogique source

Les formules, la checklist de diagnostic et les questions de quiz sont
directement issues du programme de formation fourni (modules 1 à 7 :
caractérisation, fragmentation/classification, méthodes de concentration
physique, flottation, séparation solide-liquide, bilans et indicateurs,
optimisation du procédé).
