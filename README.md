# Statique : cours et exercices interactifs

Dépôt créé en dupliquant le gabarit du dépôt « Chaîne fonctionnelle » (même charte, mêmes pastilles Niveau 1 / Niveau 2,
même accueil en cartes illustrées). Publié par GitHub Pages depuis `index.html`.

| Adresse | Contenu |
|---|---|
| `index.html` | accueil : Les cours, Le formulaire, Les exercices, Études de cas |
| `potence.html` | Exercice 2.1 (Niveau 2) — Potence à tirant sur mur : 5 parties, 45 questions et 1 tracé, 2 h (repris du dépôt `statique-potence`) |
| `cours-statique-analytique.html` | Cours 3 (Niveau 3) — Statique analytique : balance, jeux, cartes à retourner, atelier des liaisons, calculateur de moment, poutre résolue pas à pas, quiz |
| `coffre-fort.html` | Exercice 3.1 (Niveau 3) — Porte de coffre-fort : 3 parties, 23 questions et 1 tracé, 1 h |
| `echelle-pompier.html` | Exercice 3.2 (Niveau 3) — Échelle de pompier : 4 parties, 24 questions, 1 h 15 |
| `cadre-velo.html` | Exercice 3.3 (Niveau 3) — Cadre de vélo tout terrain : 4 parties, 20 questions et 1 tracé, 1 h 10 |

Les autres cartes (cours 1 et 2, formulaire, exercice 1.1, étude de cas) sont légèrement transparentes et annoncées « En cours d'édition ».

## Régénérer les pages

```sh
python3 src/generer.py               # écrit index.html, potence.html, le cours 3 et les exercices 3.1 à 3.3
python3 outils/preparer-images-n3.py # seulement si src/images/originaux/n3-* change (Pillow)
```

## Tester

```sh
NODE_PATH=$(npm root -g) node --test tests/niveau3.test.js   # accueil, cours 3, 20/20 dans chaque exercice 3.x, examen
```

- `src/gabarit-exercice-interactif.html` : gabarit de référence (seul son bloc de style sert à l'accueil).
- `src/generer.py` : cartes de l'accueil (`EXERCICES` pour les contenus, `ENCOURS` pour les cartes en cours d'édition).
- `src/exercices/potence-source.html` : page de l'exercice telle que publiée dans `statique-potence` ; le générateur la copie en `potence.html` en ajoutant un lien de retour vers l'accueil.
- `src/images/` : vignettes des cartes (480 × 270) et figures du niveau 3 (`n3-*.png`, tirées de `src/images/originaux/`).
- `src/niveau3.py` : exercices 3.1 à 3.3 (questions, corrections, tolérances, graphes de liaisons) assemblés sur le gabarit.
- `src/cours3.py` : cours 3, page autonome interactive.
- Notes de conception du niveau 3 : [`NOTE-DE-LIVRAISON.md`](NOTE-DE-LIVRAISON.md).

**Remplacer une carte « en cours d'édition »** : déposer la page dans `src/exercices/`, la vignette dans `src/images/`, ajouter l'entrée dans `EXERCICES` et retirer la ligne correspondante de `ENCOURS`.
