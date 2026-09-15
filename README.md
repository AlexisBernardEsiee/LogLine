# LogLine

Game Jam 2026 — *Mourir pour mieux avancer*

## Environnement

Utilisation env conda : python 3.14

```
conda create -n logline python=3.14
```

```
conda activate logline
```

Installation des packages

```
pip install -r requirements.txt
```

Lancer le jeu

```
python main.py
```
---

## Squelette du projet

```
LogLine/
│
├── README.md
├── requirements.txt
├── .gitignore
├── main.py                         # [base] Point d'entrée Arcade → GameView
│
├── src/
│   ├── __init__.py
│   ├── constants.py                # [base] Fichier des constantes Écran, FPS, touches, taille joueur
│   │
│   ├── views/                      # Écrans Arcade
│   │   ├── __init__.py
│   │   ├── menu_view.py            # [] Accueil : Start / Continuer / Settings / Crédits
│   │   ├── warning_view.py         # [] Avertissement save existante (Continuer / Nouvelle partie)
│   │   ├── settings_view.py        # [] Sliders volume musique / SFX
│   │   ├── credits_view.py         # [] Équipe, outils, assets
│   │   ├── game_view.py            # [Alex] Boucle gameplay centrale 
│   │   ├── pause_view.py           # [] Échap : Reprendre / Quitter
│   │   ├── flashback_view.py       # [] Mort : flash blanc → texte / vignette → fondu retour
│   │   ├── void_view.py            # [] Le Néant (révélation finale)
│   │   └── ending_view.py          # [] Écran « FIN. » puis fondu vers les crédits
│   │
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── player.py               # [] Rectangle, flèches gauche / droite
│   │   ├── interactable.py         # [] Objets E (photo, verre, journal, cadre, livre)
│   │   ├── door.py                 # Portes + fondu entre salles
│   │   └── hazard.py               # Morts : poison, éclat de verre, lustre, trou
│   │
│   ├── systems/                    # Logique jeu
│   │   ├── __init__.py
│   │   ├── room_manager.py         # [] Chargement des tableaux, transitions, trou → Néant
│   │   ├── audio_manager.py        # [] Musique, SFX objets, pas, dégradation par flashback
│   │   ├── save_manager.py         # [] Autosave à la mort (salle, position, indices, nb morts)
│   │   ├── dialogue_manager.py     # [Alex] Chargement JSON + avance clic / touche
│   │   ├── death_manager.py        # [] Checkpoint, flash, flashback, compteur de morts
│   │   └── glitch_manager.py       # [] Scintillement → pixels verts → sauts → Néant
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── dialogue_box.py         # [] Boîte bas d'écran, texte défilant
│   │   ├── prompt.py               # [] Indicateur « E » en zone de proximité
│   │   └── tutorial_overlay.py     # [] « ← → marcher » / « E interagir » (salle 1)
│   │
│   └── data/
│       ├── dialogues/
│       │   ├── room_1.json         # [] Couloir
│       │   ├── room_2.json         # [] Bar à whisky
│       │   ├── room_3.json         # [] Chambre
│       │   ├── room_4.json         # [] Bureau
│       │   └── void.json           # [] Néant + 4e mur
│       └── rooms/
│           ├── room_1.json         # [] Layout couloir : hitboxes, portes, objets
│           ├── room_2.json
│           ├── room_3.json
│           ├── room_4.json
│           └── void.json
│
├── assets/
│   ├── images/
│   │   ├── player/                 # [] Sprites Jam (idle, walk)
│   │   ├── rooms/                  # [] Fonds salles 1–4 + Néant + manoir silhouette
│   │   ├── objects/                # [] Photo, verre, journal, cadre, marque-page, lustre
│   │   └── ui/                     # [] Boîte de dialogue, overlays
│   ├── sounds/
│   │   ├── music/                  # [] Thème exploration + variantes dégradées
│   │   ├── sfx/                    # [] Verre, page, verre brisé, mort, glitch
│   │   └── footsteps/              # [] Boucle de pas
│   └── maps/                       # [] Fonds / collisions si cartes Tiled (.tmx)
│
└── saves/                          # [] Autosave (créé à la première mort)
```
