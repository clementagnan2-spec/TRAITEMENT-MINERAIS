# Gestion des opérations — Usine de traitement des minerais

Application de bureau pour la gestion réelle des opérations d'une usine de
traitement de minerais : comptes utilisateurs avec rôles, relevés
d'exploitation, productions réelles avec bilan matière calculé, incidents,
sécurité (consignation LOTO + checklists HSE signées), affectations
d'équipe, et administration des comptes. Un onglet **Formation** conserve
les outils pédagogiques (glossaire, quiz, calculateurs de simulation,
fiches de poste de référence).

*Développé par Tagnan Clément — clementagnan2@gmail.com*

## ⚠️ À lire avant déploiement en conditions réelles

Ce logiciel est un **vrai outil fonctionnel**, testé de bout en bout
(connexion, saisie, calculs, persistance des données). Mais avant de vous
en servir pour piloter une exploitation réelle, ayez ces limites en tête :

- **Base de données** : SQLite, un simple fichier local
  (`app/mine_ops.sqlite3`). Très bien pour un poste unique ou un petit
  nombre de postes partageant un dossier réseau à faible fréquence
  d'écriture simultanée. **Pas conçu pour de nombreux utilisateurs
  écrivant en même temps** (dizaines de postes simultanés) : dans ce cas,
  migrez vers un serveur de base de données dédié (PostgreSQL par
  exemple) — le code est structuré pour rendre cette migration réalisable
  sans tout réécrire (toutes les requêtes passent par `app/db.py`).
- **Sauvegardes** : le fichier `.sqlite3` contient TOUTES vos données de
  production, incidents, LOTO, etc. Il n'est **pas** suivi par Git
  (volontairement, voir `.gitignore`). Mettez en place une sauvegarde
  régulière de ce fichier (copie automatisée vers un autre disque/serveur)
  — sans quoi une panne disque fait perdre l'historique.
- **Authentification** : mots de passe hachés (SHA-256 salé), correct pour
  un usage interne sur un réseau de confiance, mais **ce n'est pas un
  système d'authentification durci** pour une exposition sur Internet.
  N'exposez pas cette application directement sur Internet sans un VPN ou
  une passerelle sécurisée en amont.
- **Pas d'intégration capteurs/SCADA** : les relevés et productions sont
  saisis manuellement par les opérateurs. Une intégration avec des
  capteurs ou un système SCADA existant est un projet à part, non couvert
  ici.
- **Conformité réglementaire** : les modules sécurité (LOTO, HSE) sont des
  outils d'aide à la traçabilité, pas un système certifié conforme à une
  réglementation minière spécifique (qui varie par pays). Faites valider
  le processus par votre responsable HSE avant un déploiement officiel.

En résumé : c'est un bon point de départ solide et réellement utilisable
pour une petite/moyenne exploitation ou un site pilote — pas encore un
système d'entreprise critique multi-sites.

## ⚠️ Windows signale l'exécutable comme virus / le supprime

C'est un **faux positif très courant** avec les exécutables générés par
PyInstaller, pas un vrai virus. Deux causes principales :

1. L'ancien mode de compilation (`--onefile`) s'auto-extrait dans un
   dossier temporaire à chaque lancement, ce qui ressemble à un
   comportement de « dropper » aux yeux des antivirus heuristiques.
2. L'exécutable n'est pas signé numériquement (aucun certificat éditeur
   reconnu par Microsoft) : Windows SmartScreen se méfie par défaut de
   tout logiciel sans réputation connue, qu'il soit malveillant ou non.

**Ce projet compile maintenant en mode dossier** (`--windowed` sans
`--onefile`), nettement moins sujet à ce faux positif, et intègre des
métadonnées de version (éditeur, description) qui aident aussi à réduire
le risque. Le livrable est un fichier `GestionOperationsMine-windows.zip`
contenant un dossier avec l'exécutable et ses fichiers de support — à
dézipper avant utilisation (ne pas lancer l'exe depuis l'intérieur du zip).

Si Windows Defender le bloque quand même :

- **Solution durable et gratuite** : signalez le faux positif à
  Microsoft via
  [https://www.microsoft.com/en-us/wdsi/filesubmission](https://www.microsoft.com/en-us/wdsi/filesubmission)
  (catégorie « Logiciel que je pense sain »). Microsoft met généralement
  à jour ses définitions sous 24 à 72 h après vérification.
- **Solution immédiate pour votre propre déploiement interne** : ajoutez
  une exclusion dans Windows Defender pour le dossier où se trouve
  l'application (*Sécurité Windows → Protection contre les virus et
  menaces → Gérer les paramètres → Ajouter ou supprimer des exclusions*).
  À ne faire que pour un logiciel dont vous connaissez l'origine (ce
  dépôt), jamais en général.
- **Solution la plus robuste à terme** : faire signer l'exécutable avec
  un certificat de signature de code (« code signing certificate »,
  quelques dizaines à quelques centaines d'euros par an selon l'autorité
  de certification). Un exécutable signé par un éditeur identifié bâtit
  une réputation auprès de Windows SmartScreen au fil des téléchargements
  et n'est presque plus jamais bloqué.
- Le blocage peut aussi venir du **navigateur** (Chrome/Edge SmartScreen)
  au moment du téléchargement plutôt que de l'antivirus lui-même :
  cliquez sur « Conserver quand même » / « Autres options » → « Conserver »
  si cette option apparaît, après vous être assuré de la provenance du
  fichier (votre propre dépôt GitHub).

## Comptes et rôles

| Rôle | Peut faire |
|---|---|
| **Opérateur** | Saisir des relevés, déclarer des incidents, verrouiller/déverrouiller des équipements (LOTO), signer des checklists HSE, consulter le tableau de bord et la formation |
| **Chef de poste** | Tout ce que fait l'opérateur, + saisir les productions réelles et consulter le bilan matière, + résoudre des incidents, + gérer les affectations d'équipe |
| **Superviseur** | Mêmes droits que chef de poste (vision multi-équipes) |
| **Administrateur** | Tout ce qui précède, + créer/désactiver des comptes utilisateurs |

**Compte par défaut à la première utilisation** : `admin` / `admin123`
— changez ce mot de passe immédiatement (l'application vous y oblige dès
la première connexion), puis créez un compte pour chaque collaborateur
depuis l'onglet **Administration**.

## Lancer depuis le code source

```bash
git clone <url-de-ce-depot>
cd mine-ops
python app/main.py
```

Prérequis : Python 3.9+ (Tkinter inclus dans l'installateur standard
Windows ; sous Linux, `sudo apt install python3-tk` si besoin). Aucune
dépendance externe n'est nécessaire pour l'exécution (SQLite est inclus
dans Python) — `requirements.txt` ne sert qu'à la compilation en `.exe`.

## Obtenir le fichier .exe (compilation automatique sur GitHub)

Un workflow **GitHub Actions** (`.github/workflows/build.yml`) compile
automatiquement l'application en `.exe` Windows, sans machine Windows ni
installation locale :

1. Poussez ce dossier sur un dépôt GitHub :
   ```bash
   git init
   git add .
   git commit -m "Gestion des opérations - usine de traitement"
   git branch -M main
   git remote add origin https://github.com/<votre-compte>/<votre-depot>.git
   git push -u origin main
   ```
2. Onglet **Actions** du dépôt → le workflow se lance automatiquement
   (ou via *Run workflow*).
3. Une fois terminé (✅), téléchargez l'artefact
   **`GestionOperationsMine-windows`** → à l'intérieur se trouve
   `GestionOperationsMine-windows.zip`. **Dézippez-le entièrement** dans
   un dossier (ne lancez jamais l'exe depuis l'intérieur d'un zip
   ouvert), puis lancez `GestionOperationsMine.exe` — il a besoin des
   fichiers du sous-dossier `_internal` à côté de lui pour fonctionner.

Pour une release téléchargeable stable, poussez un tag :
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Compiler soi-même en local (alternatif)

```bash
pip install -r requirements.txt
pyinstaller --noconfirm --windowed --name GestionOperationsMine ^
  --icon app/assets/icon.ico --add-data "app/assets;assets" ^
  --version-file version_info.txt app/main.py
# (sous Linux/macOS, remplacez --add-data "app/assets;assets" par "app/assets:assets"
# et retirez --version-file, spécifique à Windows)
# Le résultat apparaît dans dist/GestionOperationsMine/ (dossier complet, pas un fichier
# unique) — c'est volontaire, voir la section sur les faux positifs antivirus ci-dessus.
```

## Déploiement multi-postes (plusieurs opérateurs, plusieurs ordinateurs)

Solution simple sans serveur dédié : placez `GestionOperationsMine.exe` et
le fichier `mine_ops.sqlite3` sur un **dossier réseau partagé**, et faites
pointer chaque poste vers ce même dossier (raccourci vers l'exécutable
placé dans le dossier partagé, ou copie de l'exe sur chaque poste avec le
`.sqlite3` sur le partage réseau). Convient à une poignée de postes
écrivant occasionnellement. Pour un usage plus intensif, migrez vers un
serveur PostgreSQL (voir l'avertissement de portée ci-dessus).

## Structure du projet

```
mine-ops/
├── app/
│   ├── main.py            # Point d'entrée, assemble l'application
│   ├── db.py                # Accès base de données (SQLite) — toute la logique de persistance
│   ├── data_postes.py       # Référentiel des postes/circuits (à adapter à votre flowsheet réel)
│   ├── data_formation.py    # Contenu pédagogique (glossaire, quiz, fiches de poste de référence)
│   ├── ui_login.py           # Écran de connexion, changement de mot de passe
│   ├── ui_dashboard.py       # Tableau de bord (KPIs du jour)
│   ├── ui_releves.py         # Saisie des relevés de paramètres réels
│   ├── ui_productions.py     # Saisie de production réelle + bilan matière calculé
│   ├── ui_incidents.py       # Journal des incidents/anomalies
│   ├── ui_securite.py        # Consignation LOTO + checklist HSE signée
│   ├── ui_equipes.py         # Affectations d'équipe par poste/quart
│   ├── ui_admin.py           # Gestion des comptes utilisateurs (admin)
│   ├── formation_ui.py       # Outils de formation intégrés (glossaire, quiz, calculateurs)
│   └── assets/
│       ├── icon.ico           # Icône de l'application (lingot d'or) — fenêtre + .exe
│       └── icon.png
├── .github/workflows/
│   └── build.yml              # Compilation automatique du .exe sur GitHub Actions
├── requirements.txt
└── README.md
```

## Adapter à votre usine réelle

- **Postes/circuits** : modifiez `app/data_postes.py` pour refléter
  exactement votre flowsheet (ajoutez/retirez des circuits, ajustez les
  paramètres proposés dans les formulaires de relevé).
- **Rôles** : si votre organisation a d'autres intitulés de poste,
  adaptez `ROLES` / `ROLES_LABELS` dans `app/db.py` (contrainte SQL) et
  `app/ui_admin.py` / `app/main.py` (interface).
- **Contenu de formation** : `app/data_formation.py` reprend le contenu
  des deux programmes de formation fournis précédemment ; à mettre à jour
  librement.
