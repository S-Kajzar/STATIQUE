# Statique : cours et exercices interactifs

Dépôt créé en dupliquant le gabarit du dépôt « Chaîne fonctionnelle » (même charte, mêmes pastilles Niveau 1 / Niveau 2,
même accueil en cartes illustrées). Publié par GitHub Pages depuis `index.html`.

| Adresse | Contenu |
|---|---|
| `index.html` | accueil : Les cours, Le formulaire, Statique graphique (exercices Niveau 1), Statique analytique (exercices Niveau 2), Études de cas |
| `cours-statique-graphique.html` | Cours 1.1 (Niveau 1) — Statique graphique : isolement, PFS, deux forces (bielle animée), trois forces (levier de bride pas à pas), dynamique interactif, quiz |
| `panneau-solaire.html` | Exercice 1.2 (Niveau 1) — Panneau solaire : 2 parties, 9 questions et 1 tracé sur DR, 40 min |
| `pince-kobelco.html` | Exercice 1.3 (Niveau 1) — Pince de démolition : 3 parties, 11 questions et 2 tracés sur DR, 1 h 05 |
| `cric-hydraulique.html` | Exercice 1.4 (Niveau 1) — Cric hydraulique roulant : 3 parties, 9 questions et 1 tracé sur DR, 1 h 10 |
| `suspension-vtt.html` | Exercice 1.5 (Niveau 1) — Suspension arrière de VTT : 3 parties, 11 questions et 1 tracé sur DR, 1 h 10 |
| `cours-statique-analytique.html` | Cours 3 (Niveau 3) — Statique analytique : balance, jeux, cartes à retourner, atelier des liaisons, calculateur de moment, poutre résolue pas à pas, quiz |
| `deplacer-torseur.html` | Exercice 2.1 (Niveau 2) — Déplacer un torseur : entraînement à tirages aléatoires (glisseur plan, torseur plan, torseur 3D) sur un seul écran (données, réponse et correction côte à côte), vecteur BA et torseur en B à écrire, correction pas à pas, série de 10 notée sur 20 |
| `coffre-fort.html` | Exercice 2.2 (Niveau 2) — Porte de coffre-fort : 3 parties, 4 torseurs ou vecteurs à compléter, 2 questions et 1 tracé, 1 h |
| `echelle-pompier.html` | Exercice 2.3 (Niveau 2) — Échelle de pompier : 5 parties (vérin isolé, résolution graphique sur DR avec l'atelier de tracé, torseurs, PFS en A, capacité du vérin double effet en poussant et en tirant), 1 tracé, 1 h 45 |
| `cadre-velo.html` | Exercice 2.4 (Niveau 2) — Cadre de vélo tout terrain : 4 parties, 6 torseurs ou vecteurs à compléter, 3 questions et 1 tracé, 1 h 10 |
| `potence.html` | Exercice 2.5 (Niveau 2) — Potence à tirant sur mur : 5 parties, 45 questions et 1 tracé, 2 h (repris du dépôt `statique-potence`) |

Les autres cartes (formulaire, exercice 1.1, étude de cas) sont légèrement transparentes et annoncées « En cours d'édition ».

## Régénérer les pages

```sh
python3 src/generer.py                     # écrit index.html, potence.html, les cours 1.1 et 3, les exercices 1.2 à 1.5 et 2.1 à 2.4
python3 outils/preparer-images-n3.py       # seulement si src/images/originaux/n3-* change (Pillow)
python3 outils/preparer-images-graphique.py # seulement si src/images/originaux/g-* change (Pillow)
python3 outils/preparer-images-echelle.py  # exercice 2.3 : figures du manuel (n3-ep-*) et DR dessiné à l'échelle
python3 outils/vignette-torseur.py         # vignette de la carte 2.1, dessinée (Pillow)
```

## Tester

```sh
NODE_PATH=$(npm root -g) node --test tests/*.test.js   # accueil, cours 1.1 et 3, atelier de tracé, 20/20 dans chaque exercice, examen
```

- `src/gabarit-exercice-interactif.html` : gabarit de référence (seul son bloc de style sert à l'accueil).
- `src/generer.py` : cartes de l'accueil (`EXERCICES` pour les contenus, `ENCOURS` pour les cartes en cours d'édition).
- `src/exercices/potence-source.html` : page de l'exercice telle que publiée dans `statique-potence` ; le générateur la copie en `potence.html` en ajoutant un lien de retour vers l'accueil.
- `src/images/` : vignettes des cartes (480 × 270) et figures du niveau 3 (`n3-*.png`, tirées de `src/images/originaux/`).
- `src/niveau3.py` : exercices 2.2 à 2.4 (torseurs et vecteurs à compléter case par case, questions, corrections, graphes
  de liaisons) assemblés sur le gabarit ; constructeur de page commun à tous les exercices générés (`build_exo`).
- `src/torseur_alea.py` : exercice 2.1, page autonome d'entraînement à valeurs aléatoires (les tirages se recalculent
  dans le navigateur ; `deplacer-torseur.html?seed=42` rend la suite de tirages reproductible).
- `src/echelle_dr.py` : cotes du DR de l'échelle de pompier, partagées par son dessin et par la correction graphique.
- `src/cours3.py` : cours 3, page autonome interactive ; `src/cours1.py` : cours 1.1 (statique graphique).
- `src/graphique.py` : exercices 1.2 à 1.5 (points relevés sur les DR, constructions résolues, questions, corrections).
- `src/atelier.py` : **atelier de tracé** des exercices de statique graphique, greffé sur le moteur de tracé du gabarit
  sans le modifier : vecteur à l'échelle (intensité affichée ou imposée), droite d'action, parallèle (un clic sur une
  autre droite change la référence), segment, point, mesure (distance, intensité, angle), sélection (recolorer, changer
  l'épaisseur, supprimer), aimantation aux points, extrémités et intersections, DR en transparence réglable, zones
  d'échelle multiples sur un même DR, plein écran où le DR tient en entier, correction rejouée pas à pas
  (`DR.etape`, `DR.construire`).
- Notes de conception du niveau 3 : [`NOTE-DE-LIVRAISON.md`](NOTE-DE-LIVRAISON.md).

**Remplacer une carte « en cours d'édition »** : déposer la page dans `src/exercices/`, la vignette dans `src/images/`, ajouter l'entrée dans `EXERCICES` et retirer la ligne correspondante de `ENCOURS`.
