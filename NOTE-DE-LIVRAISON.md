# Note de livraison — Réorganisation des niveaux

- Les cartes « Cours 1 » et « Cours 2 », en cours d'édition, sont retirées : la rubrique « Les cours » ne garde que
  le cours 1.1 Statique graphique (Niveau 1), en premier, puis le cours 3 Statique analytique (Niveau 3).
- La rubrique « Statique graphique : exercices sur document réponse » (exercices 1.2 à 1.5, Niveau 1) passe au-dessus
  des exercices de statique analytique, rubrique renommée « Statique analytique : exercices ».
- Les exercices de statique analytique passent au **Niveau 2** (pastille bleue), « Déplacer un torseur » en premier :
  2.1 Déplacer un torseur (ancien 3.4), 2.2 Porte de coffre-fort (3.1), 2.3 Échelle de pompier (3.2), 2.4 Cadre de vélo
  (3.3), 2.5 Potence à tirant sur mur (ancien 2.1). Pages, liens du cours 3 et tests suivent la nouvelle numérotation ;
  les adresses des pages ne changent pas.
- Les notes de livraison plus bas gardent l'ancienne numérotation (3.1 à 3.4).

---

# Note de livraison — Atelier de tracé : parallèle, sélection, plein écran, correction pas à pas

Améliorations de l'atelier de statique graphique (exercices 1.2 à 1.5 et 3.2) :

- **Parallèle** : une fois une parallèle posée, un simple clic sur une autre droite d'action ou un autre vecteur change
  la référence (surlignée en jaune). Appuyer sur un point (accroché par l'aimant) ou appuyer-glisser pose la parallèle.
- **Sélection** (nouvel outil) : un clic sur un tracé posé l'entoure de jaune ; une pastille de couleur le recolore,
  Fin / Moyen / Épais change son épaisseur, « Supprimer » ou la touche Suppr l'efface, Échap désélectionne.
- **Plein écran** : le DR est dimensionné pour tenir en entier dans la place laissée par la barre d'outils, la consigne
  et le bouton de validation (testé en 1366 × 768, 1280 × 600 et tablette en portrait), proportions conservées ; le
  zoom reste disponible. Sur la pince Kobelco, le vecteur Fc2/3 donné, qui occupe toute la hauteur du DR, est
  désormais visible jusqu'à sa pointe.
- **Correction pas à pas** : après validation, « Voir pas à pas » rejoue la construction sur le DR, une étape à la
  fois (étapes précédentes estompées), avec une consigne simple pour chaque action : droite d'action de la force connue,
  droite d'action de direction connue (et pourquoi), point de concours, troisième droite, force connue à l'échelle (avec
  l'astuce « Intensité imposée »), parallèles, vecteurs bout à bout et lecture. 7 étapes pour un solide (panneau,
  échelle), 6 pour la pince, 14 pour les deux isolements successifs du cric et du VTT (report par actions mutuelles).
  En plein écran, seule l'étape en cours s'affiche sous le DR.

---

# Note de livraison — Exercice 3.4 : ergonomie « un seul écran »

L'entraînement « Déplacer un torseur » tient désormais dans un écran d'ordinateur (testé en 1366 × 768 et 1280 × 720,
niveaux 1 à 3, correction affichée) : plus besoin de remonter pour relire les données.

- **Barre d'en-tête** compacte : titre, choix du niveau, bouton « Rappel » (formule de Varignon en surimpression,
  refermée d'un clic ailleurs), score (tirage, réussis, série, série de 10).
- **Trois colonnes** : 1 Données (torseur en A, points A et B, figure), 2 Ta réponse (BA, torseur en B, boutons),
  3 Correction (pas à pas). Sur tablette, la correction passe sous les données, à côté de la réponse ; sur téléphone,
  une seule colonne, la page descend vers la correction et remonte d'elle-même au tirage suivant.
- **Clavier** : le curseur est placé dans la première case ; Entrée vérifie, ramène le curseur sur la première case
  fausse, puis lance le tirage suivant quand tout est juste ; Tab passe d'une case à l'autre.
- **Correction en place** : la valeur attendue s'affiche sous chaque case fausse ou vide.

---

# Note de livraison — Exercice 3.2 enrichi : échelle de pompier (schémas et questions du manuel)

L'exercice reprend l'exercice résolu du manuel (statique plane) : mêmes données, avec ses schémas et ses questions.
Il passe de 4 à **5 parties** (1 h 45, 34 points) :

| Partie | Contenu |
|---|---|
| 1. Vérin isolé | droite d'action (BC), compression ; correction illustrée par le vérin isolé du manuel |
| 2. Résolution graphique (nouvelle) | tableau bilan des forces ; **tracé sur DR avec l'atelier** : verticale de G3, (BC), point de concours I, (AI), dynamique à 1 cm ↔ 1 000 daN ; lectures de B4/3 et A2/3, angle de (AI), sens de A2/3 ; correction superposée + construction du manuel |
| 3. Résolution calculée | B et vecteur unitaire u ; torseurs en leur point (inchangé) |
| 4. PFS en A | torseurs en A, F, composantes de A et B, ‖A‖ (comparée à la lecture graphique), **angle α<sub>A</sub> ≈ −49,4°** (nouveau) |
| 5. Vérin double effet | coupe longitudinale du manuel ; S, pression nécessaire (≈ 117,8 bar) ; **capacité en poussant à 150 bar** (11 781 daN), le vérin tient-il l'échelle, **couronne S′**, **capacité en tirant** (9 067 daN), écart de 23 % |

- Le **DR est dessiné** à l'échelle 1 cm ↔ 1 m d'après les cotes du manuel (`src/echelle_dr.py`,
  `outils/preparer-images-echelle.py`) : la construction exacte retrouve les valeurs du calcul (9 252 et 4 864 daN), le
  manuel, tracé à la main, annonce 9 300 et 4 900 daN ; les lectures sont acceptées à ± 7 %.
- Figures reprises du manuel : vérin isolé, construction graphique (correction), vérin en coupe. Les schémas du piston
  isolé en poussant et en tirant sont redessinés en vectoriel (le scan, teinté, laissait voir le verso).
- Dossiers : DP1 (présentation, figures, vérin), DT1 (formulaire de statique analytique), DT2 (méthode de la statique
  graphique et mode d'emploi de l'atelier).

Tests : 20/20 sur tout le sujet (tracé compris), cases de torseur fausses, examen et téléphone, et un test qui fait la
construction sur le DR (I accroché à l'intersection, dynamique à l'échelle, lectures acceptées).

---

# Note de livraison — Exercice 3.4 : déplacer un torseur (entraînement aléatoire)

Nouvelle carte **Exercice 3.4 · Niveau 3** (`deplacer-torseur.html`), page autonome : chaque tirage donne un torseur
connu au point A et les coordonnées de A et de B ; l'élève écrit le **vecteur BA** puis le **torseur au point B**.

- **Trois niveaux** : 1 · glisseur dans le plan (moment nul en A) ; 2 · torseur quelconque dans le plan (N<sub>A</sub>
  ≠ 0) ; 3 · torseur dans l'espace (6 composantes, produit vectoriel complet).
- **Tirages** : coordonnées au décimètre entre −0,6 et 1,2 m (A et B distants d'au moins 0,25 m), forces par pas de
  10 N, moments par pas de 5 N·m ; les résultats tombent juste au millième.
- **Figure** (niveaux 1 et 2) : axes, A, B, vecteur BA en tirets, résultante R, arc du moment N<sub>A</sub> orienté
  selon son signe ; étiquettes placées automatiquement.
- **Correction** case par case (tolérance ± 0,01 m sur BA, ± 0,5 % sur le torseur), puis correction pas à pas :
  BA = A − B, résultante inchangée, N<sub>B</sub> = N<sub>A</sub> + a·Y − b·X (ou les trois composantes de BA ∧ R),
  torseur final.
- **Score** : tirages réussis du premier coup, série en cours, et une **série de 10 notée sur 20**. Voir la correction
  avant de répondre compte le tirage comme manqué. Rien n'est enregistré.
- `?seed=…` dans l'adresse rend les tirages reproductibles (utile pour un sujet commun en classe et pour les tests).

Tests (`tests/torseur.test.js`) : réponses recalculées indépendamment de la page pour les trois niveaux ; erreurs de
signe (AB au lieu de BA) notées case par case ; saisies avec virgule, point, signe − typographique ; série de 10 =
20/20 ; 300 tirages cohérents et variés ; sens de l'arc du moment ; aucun débordement sur téléphone.

---

# Note de livraison — Niveau 3 : saisie des torseurs et des vecteurs

Les exercices 3.1 à 3.3 sont **moins guidés** : les questions intermédiaires (nature de chaque liaison, nombre
d'inconnues, coordonnées une à une, moment de chaque force…) sont remplacées par des **torseurs et des vecteurs à
compléter**, comme sur une copie.

- **Torseur plan** {T}<sub>P</sub> écrit en colonnes (X | — ; Y | — ; — | N) : l'élève remplit X, Y et N. Une inconnue
  s'écrit par son nom (X_A, Y_B ; casse et tiret bas indifférents), une composante nulle par 0, une valeur par un nombre
  signé, un moment transporté par une **expression linéaire** coefficient × inconnue (−2,1X_A, 3,24F, 1 102Y_B…).
- **Vecteur** (coordonnées d'un point, vecteur unitaire, résultat) : une case par composante.
- Chaque case est notée séparément (½ point) ; le bloc se valide en une fois (question « groupe » du gabarit, déjà
  prévue par son moteur) et la correction affiche les torseurs attendus et la démarche. En mode examen, les cases sont
  corrigées à la remise de la copie.
- Le correcteur d'expressions linéaires (type `lin`) est ajouté au moteur Grading par un petit script, sans modifier le
  moteur ; seul le libellé du bouton validé (« Saisie validée » au lieu de « Diagramme validé ») est rendu paramétrable
  dans la copie générée.

| Exercice | À compléter |
|---|---|
| 3.1 Porte de coffre-fort | graphe des liaisons (tracé) ; coordonnées de A, G3, G4 ; 4 torseurs en leur point ; 4 torseurs transportés en B ; vecteurs A1/3 et B2/3 ; ‖B‖ ; gond porteur |
| 3.2 Échelle de pompier | droite d'action du vérin, compression ; B et vecteur unitaire u ; 3 torseurs en leur point (action du vérin en fonction de F) ; 3 torseurs en A ; F ; vecteurs A2/3, B4/3 ; ‖A‖ ; surface, pression |
| 3.3 Cadre de vélo | graphe des liaisons (tracé) ; 3 torseurs du cadre complet puis transportés en C ; Y_B, Y_C ; amortisseur (EF), point C ; A, E, u ; 3 torseurs du bras arrière en A ; E ; vecteur A1/2 |

Tests : pour chaque exercice, sujet entièrement juste = 20/20 en saisissant tous les torseurs ; cases fausses (signe
inversé, inconnue mal nommée) notées case par case ; mode examen. Les résultats numériques sont inchangés (voir plus bas).

---

# Note de livraison — Statique graphique (Niveau 1) : cours 1.1 et exercices 1.2 à 1.5

**Sources** : « Séquence : Statique — Cours » (statique graphique), « Exercice — Panneau solaire », « Activité 3 – Pince
Kobelco », « Activité 4 – Cric hydraulique roulant », « Suspension arrière de VTT ». Nouvelle carte **Cours 1.1** (pastille
verte Niveau 1) et nouvelle rubrique de l'accueil **« Statique graphique : exercices sur document réponse »** (exercices
1.2 à 1.5, indépendants). La carte « Cours 1 — Principe fondamental de la statique » (en cours d'édition) est conservée.

## Atelier de tracé (`src/atelier.py`)

Environnement de construction graphique superposé au **document réponse affiché en légère transparence** (opacité
réglable, 45 % par défaut ; le DR s'imprime à pleine opacité). Il est greffé sur le moteur de tracé du gabarit sans le
modifier : un script chargé après le moteur surcharge les méthodes des seuls tracés dont le décor porte une entrée
`graph` (correction superposée, auto-évaluation, impression, plein écran et zoom restent ceux du gabarit).

| Outil | Rôle |
|---|---|
| Vecteur | flèche origine → extrémité ; longueur en cm du document, intensité à l'échelle et angle affichés en direct ; **intensité imposée** pour tracer une force connue exactement à l'échelle |
| Droite d'action | droite passant par deux points, prolongée sur toute la feuille |
| Parallèle | choisir une droite ou un vecteur de référence, puis le point de passage (remplace l'équerre) |
| Segment, Point, Texte | traits, point de concours I, noms des vecteurs |
| Mesurer | distance, intensité correspondante et angle, sans rien tracer |
| Gomme, Annuler, Tout effacer | comme dans le gabarit, étendus aux nouveaux tracés |
| Aimant | accroche aux points du DR, aux extrémités des tracés et aux **intersections** des droites (cercle bleu ou orange) |

Un DR peut porter plusieurs **zones d'échelle** (cric, VTT : l'échelle est celle de la zone où commence le vecteur). Les
barres d'échelle d'origine sont remplacées par des barres « 1 cm ↔ … » dessinées par le moteur.

## Cours 1.1 — Statique graphique (`cours-statique-graphique.html`)

Fonction du PFS et isolement (jeu : bilan des actions extérieures du levier de la bride), PFS (cartes à retourner),
hypothèses, solide soumis à deux forces (bielle qu'on fait tourner), solide soumis à trois forces, **exemple de la bride
résolu pas à pas sur la figure** (force connue, direction par la biellette 6, point I, direction (BI), dynamique), dynamique
interactif (trois forces, directions réglables), méthode en cinq étapes, quiz de 8 questions.

- Valeurs de l'exemple **recalculées sur la figure** : F6/levier ≈ 5 000 N, F1/levier ≈ 7 100 N (le cours
  d'origine annonce 4 600 N et 6 800 N, lus sur un tracé à la main).
- Échelle du dynamique : la source indique « 1 cm = 200 N », incompatible avec 6 000 N (30 cm) ; le cours retient
  1 cm ↔ 2 000 N.

## Exercices (solutions calculées à partir des points relevés sur les DR)

**1.2 Panneau solaire** (2 parties, 9 questions, 1 tracé, 40 min) : P = 380 N ; barre (3) soumise à deux forces ⇒ D3/1
horizontale ; I à la verticale de G et à la hauteur de D ; A2/1 portée par (AI), ≈ 55° ; dynamique
1 cm ↔ 50 N dans une zone ajoutée à droite de la figure : **D3/1 ≈ 267 N, A2/1 ≈ 465 N** ; barre comprimée.

**1.3 Pince de démolition** (3 parties, 11 questions, 2 tracés, 1 h 05) : vérin = deux forces, (AC), 2 500 kN, comprimé ;
bloc : forces horizontales (HG). Dynamique construit à partir du vecteur Fc2/3 donné (10 cm, 1 cm ↔ 250 kN).
Configuration 1 : **G ≈ 1 857 kN**, B ≈ 3 426 kN ; configuration 2 : **I ≈ 1 194 kN**, B ≈ 2 991 kN ⇒
la configuration 1 (serrage près de l'articulation B) est la plus efficace.

**1.4 Cric hydraulique** (3 parties, 9 questions, 1 tracé, 1 h 10) : bielle (CF), groupe hydraulique (AD). Sellette
(1 cm ↔ 50 daN) : E2/4 ≈ 397 daN, F3/4 ≈ 29 daN. Bras (1 cm ↔ 150 daN) : **effort du vérin D1/2 ≈ 1 081 daN**,
B0/2 ≈ 1 202 daN. Les deux constructions sont sur le même DR (comme sur la feuille), pour pouvoir reporter la
direction de E par parallèle. Échelles changées (source : barres « 25 daN » et « 75 daN » qui donnaient un dynamique de
16 cm pour la charge) ; question 13 de la source corrigée (« direction de l'action en B », et non en E).

**1.5 Suspension de VTT** (3 parties, 11 questions, 1 tracé, 1 h 10) : bases (AB), amortisseur (FG). Haubans
(1 cm ↔ 10 daN) : B4/3 ≈ 56 daN, D2/3 ≈ 94 daN. Basculeur (1 cm ↔ 40 daN au lieu de 20 daN, pour que le
dynamique tienne sur la feuille) : **F1/2 ≈ 175 daN** (effort supporté par l'amortisseur, comprimé), E0/2 ≈ 254 daN.
Question 14 de la source corrigée (dynamique du basculeur 2, et non des haubans 3).

**Communs** : les tableaux d'isolement deviennent des questions (direction, nombre de forces, actions mutuelles, sens) ;
les lectures graphiques sont notées avec une tolérance de 7 % (± 3° pour un angle, ± 7 daN pour la petite force F3/4 du
cric) ; documents DP1 (présentation), DT1 (méthode de la statique graphique), DT2 (mode d'emploi de l'atelier). Le nom
du site d'origine et les grilles des feuilles ne sont pas repris.

## Vérifications

`tests/graphique.test.js` (Playwright) : accueil, cours 1.1 (isolement, bielle, levier pas à pas, dynamique interactif,
quiz), **construction complète du panneau solaire à la souris** avec l'aimant, l'intensité imposée et deux parallèles
(dynamique mesuré : 380, 267 et 465 N), gomme, annulation, correction superposée ; 20/20 dans chaque exercice, lectures
fausses refusées, mode examen, aucun débordement à 390 px. Les tests du niveau 3 passent toujours.

---

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
