# Note de livraison — Niveau 3 : statique analytique

**Source** : séquence « Statique analytique » (rappel du PFS, torseur d'action mécanique transmissible, hypothèse du
problème plan, méthode de résolution ; exercices 1 à 5). Les **exercices 4 (capot d'automobile) et 5 (pédale de
commande) ne sont pas repris**, comme demandé. Pastille **Niveau 3** (violette) sur le cours et les trois exercices.

## Cours 3 — Statique analytique (`cours-statique-analytique.html`)

Page autonome, même charte que l'accueil, en 8 sections :

1. **Rappel du PFS** : définition, balance interactive (la masse change, R = −P se met à jour), énoncé encadré.
2. **Solide soumis à deux forces** : figure d'origine, énoncé, jeu « équilibre ou pas ? » (4 situations dessinées).
3. **Généralisation** : les trois puces vides du document deviennent des **cartes à retourner** (théorème de la
   résultante statique, théorème du moment statique, écriture torseur) ; tableau graphique / analytique.
4. **Torseur transmissible** : règle « mouvement libre ⇒ composante nulle » ; les tableaux vides « translation /
   rotation → force / moment » deviennent un **atelier des liaisons** : 9 liaisons (dont les deux exemples du cours,
   ponctuelle de normale y et pivot d'axe z), tableau des degrés de liberté, torseur à compléter case par case,
   vérification, solution, bascule « problème plan ».
5. **Problème plan** : les deux puces vides deviennent des cartes (Z = 0 ; L = M = 0) ; les deux exemples du cours
   (glissière d'axe x dans (x, y), rotule dans (y, z)) sont corrigés dans des volets ; jeu « combien d'inconnues ? ».
6. **Moment d'une force** (prérequis de la séquence) : formule, calculateur interactif (position, intensité, angle ;
   bras de levier et sens de rotation dessinés ; défi « annuler le moment »), transport des moments (BABAR).
7. **Méthode de résolution** : les 4 étapes du cours ; simulateur d'une poutre sur pivot et appui ponctuel, résolu
   **pas à pas** (bilan des torseurs, comptage, choix du point, équations et résultats en direct) ; trois défis.
8. **Quiz** de 8 questions, étoiles.

## Exercice 3.1 — Porte de coffre-fort (`coffre-fort.html`, 3 parties, 23 questions + 1 tracé, 1 h)

- Lecture du schéma cinématique : 0–1 et 0–2 encastrements (gonds scellés), **1–3 linéaire annulaire d'axe (A, y)**,
  **2–3 rotule de centre B**, 3–4 pivot d'axe vertical. Le graphe des liaisons (Q1.1 de la source) est un **tracé**
  sur un fond où les cinq solides sont déjà placés, avec correction superposée et auto-évaluation (5 critères).
- Repère (B, x, y) ; A (0 ; 2,1 m) ; G3 à 0,4 m ; G4 à 0,4 + 0,88 = 1,28 m.
- Résultats : M_B(P3) = −400 daN·m ; M_B(P4) = −3 840 daN·m ; **X_A ≈ −2 019,05 daN** ; Y_A = 0 ;
  **X_B ≈ 2 019,05 daN ; Y_B = 4 000 daN ; ‖B‖ ≈ 4 480,7 daN**.
- Ajouts : action intérieure 3–4 (oui/non), point de résolution, gond porteur, effet d'un écartement de la porte.

## Exercice 3.2 — Échelle de pompier (`echelle-pompier.html`, 4 parties, 24 questions, 1 h 15)

- Vérin (4 + 5) isolé : 2 forces ⇒ droite (BC) à 70°, vérin comprimé.
- Repère (A, x, y) : B (2,85 ; 1,65) m ; P3 = 5 000 daN à x = 6 m. B4/3 = F (−cos 70° ; sin 70°).
- Bras de levier du vérin d = 2,85 sin 70° + 1,65 cos 70° ≈ 3,24 m ; **F ≈ 9 252 daN** ; X_B ≈ −3 164 daN ;
  Y_B ≈ 8 694 daN ; X_A ≈ 3 164 daN ; **Y_A ≈ −3 694 daN** (la tourelle retient l'échelle) ; ‖A‖ ≈ 4 864 daN.
- Pression : S ≈ 7 853,98 mm² ; F ≈ 92 522 N ; **p ≈ 11,78 MPa ≈ 117,8 bar**.
- Ajouts : rapport Y_B / X_B, effet d'une charge plus éloignée sur la pression.

## Exercice 3.3 — Cadre de vélo (`cadre-velo.html`, 4 parties, 20 questions + 1 tracé, 1 h 10)

- Graphe des liaisons (tracé, 4 critères) : 1–2 pivot (A, z), 2–3 pivot en E, 3–1 pivot en F ; les actions
  extérieures (cycliste, roues) sont déjà dessinées. Une rotule est acceptée pour les articulations de l'amortisseur.
- Cadre complet : x_B = 1 102 mm ; M_C(P) = −242 000 N·mm ; **B ≈ 219,60 N ; C ≈ 780,40 N**.
- Amortisseur : 2 forces ⇒ droite (EF), qui passe par C (C, E, F alignés), comprimé.
- Bras arrière (2) : y_E ≈ 280,32 mm ; M_A(C) ≈ −335 572 N·mm ; d = 430 sin 35,5° ≈ 249,70 mm ;
  **E ≈ 1 343,9 N ; X_A ≈ 1 094,1 N ; Y_A = 0** — vérifié par le théorème des trois forces (concourantes en C).

## Conventions, tolérances et choix

- Problèmes plans (x, y) ; moments positifs dans le sens trigonométrique, M_A = x·F_y − y·F_x ; composantes
  algébriques (signe exigé), normes positives. Les orientations des actions inconnues sont fixées dans les données
  (ex. : vérin qui pousse, amortisseur comprimé) pour que les signes attendus soient sans ambiguïté.
- Unités notées pour moitié (gabarit) ; conversions acceptées avec leur unité (N, daN, kN, mm, m, N·m, daN·m,
  MPa, bar). Tolérances : valeur exacte ou ± 0,1 % à 0,3 % selon les arrondis intermédiaires demandés en amont.
- Chaque exercice a ses propres documents : DP1 (présentation, figures) et DT1 (formulaire de statique analytique :
  PFS, deux forces, moment, transport, torseurs plans des liaisons usuelles, méthode, vérin).
- Pages générées par `src/generer.py` à partir du gabarit (style, moteur Grading et moteur applicatif recopiés ;
  seules les entrées DECOR, DR_NAMES, CONSEIL_MIN et le texte « Quatre pages » sont remplacées).

## Vérifications

`tests/niveau3.test.js` (Playwright, Chromium), 11 parcours réussis : accueil (cartes et pastilles Niveau 3, pas de
débordement à 390 px) ; cours 3 (balance, jeux, cartes, atelier, calculateur de moment, poutre, défi, quiz) ; pour
chaque exercice, sujet entièrement juste = **20,0/20**, réponses fausses refusées, demi-point sans unité, mode
examen et remise de la copie. Aucune erreur JavaScript.
