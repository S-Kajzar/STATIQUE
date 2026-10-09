#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Statique graphique (Niveau 1) : exercices 1.2 à 1.5, indépendants, avec l'atelier de tracé.

Sources : « Panneau solaire » (modélisation des actions mécaniques), « Activité 3 – Pince Kobelco »,
« Activité 4 – Cric hydraulique roulant » et « Suspension arrière de VTT ». Chaque exercice est une page autonome
construite par niveau3.build_exo sur le gabarit ; ses tracés utilisent l'atelier (src/atelier.py) : DR en
transparence, vecteurs à l'échelle, droites d'action, parallèles, mesures, aimantation.

Les points des DR sont relevés dans les fonds produits par outils/preparer-images-graphique.py (en pixels du fond) ;
les solutions graphiques (point de concours, dynamique) sont calculées ici et dessinées dans la correction.
"""
import math

import atelier
from atelier import DR, fr, trois_forces
from niveau3 import (H_ENTIER, H_OUINON, H_DROITE, UNITE, KW, CODE, DROITE, ENTIER, YES, Q, QBAR, SK, V, data_box,
                     esc, figure, num, png, var, COMPRIME, SENS_OPPOSES)

H_LU = ("Lecture sur ton dynamique (outil <b>Mesurer</b> ou longueur affichée par l'outil Vecteur), arrondie à "
        "l'unité ; la tolérance couvre la précision du tracé. " + UNITE)
H_ANGLE = "Angle mesuré sur ton tracé, en degrés, arrondi à l'unité. " + UNITE
H_SENS = "Réponds en quelques mots (vers le haut, vers la gauche…)."
H_EX = "Valeur exacte. " + UNITE
TOL = 0.07          # tolérance relative des lectures graphiques
CORR_COUL = ["TEAL", "PURP", "ORNG"]


def lu(value, u, tol=TOL, variants=()):
    return num(value, u, relTol=tol, variants=variants)


def cartes_methode():
    """DT1 commun : la méthode de la statique graphique."""
    return ('<div class="doc-text"><h3>Isoler un solide</h3><p>On imagine le solide seul et on recense les actions '
            "mécaniques <strong>extérieures</strong> qui s'exercent sur lui. Pour chacune : nom, point d'application, "
            "direction (droite d'action), sens, intensité (norme).</p>"
            "<h3>Principe fondamental de la statique</h3><p>Un solide en équilibre sous l'action de <i>n</i> forces "
            "extérieures vérifie : la somme vectorielle des forces est nulle, et la somme de leurs moments en "
            "n'importe quel point est nulle.</p>"
            "<h3>Solide soumis à deux forces</h3><p>Les deux forces ont la <strong>même droite d'action</strong> (celle "
            "qui joint leurs points d'application), la <strong>même intensité</strong> et des <strong>sens "
            "contraires</strong>. Exemples : bielle, tirant, vérin, amortisseur articulés à leurs deux extrémités et "
            "de poids négligé.</p>"
            "<h3>Solide soumis à trois forces non parallèles</h3><ol><li>Les trois droites d'action sont "
            "<strong>concourantes</strong> : elles se coupent en un même point I.</li><li>Le <strong>dynamique des "
            "forces</strong> est fermé : les trois vecteurs mis bout à bout forment un triangle.</li></ol>"
            "<h3>Méthode</h3><ol><li>Tracer la force entièrement connue et les directions connues (solides soumis à "
            "deux forces, contacts sans frottement : perpendiculaires aux surfaces).</li><li>Prolonger deux droites "
            "d'action jusqu'à leur intersection I ; la troisième passe par son point d'application et par I.</li>"
            "<li>Choisir une échelle, tracer la force connue, puis, par ses extrémités, les parallèles aux deux autres "
            "directions : elles se coupent au troisième sommet du triangle.</li><li>Orienter les vecteurs bout à bout "
            "(sens de parcours unique), mesurer leurs longueurs et les convertir avec l'échelle.</li></ol>"
            "<h3>Actions mutuelles</h3><p>L'action de 1 sur 2 est opposée à l'action de 2 sur 1 : "
            f"{V('F', '1/2')} = −{V('F', '2/1')} (même droite d'action, même intensité, sens contraires).</p>"
            "<h3>Poids</h3><p><i>P</i> = <i>m</i> · <i>g</i> ; vertical, vers le bas, appliqué au centre de gravité.</p></div>")


def dt_aide():
    return ('<div class="doc-text"><h3>Atelier de tracé</h3>' + atelier.AIDE.replace("<details", "<div").replace(
        "</details>", "</div>").replace("<summary>", "<p><strong>").replace("</summary>", "</strong></p>") + "</div>")


def docs_for(dp_title, dp_html):
    return lambda: [("DP1", dp_title, "Dossier présentation", False, dp_html()),
                    ("DT1", "Méthode de la statique graphique", "Dossier technique", True, cartes_methode()),
                    ("DT2", "Mode d'emploi de l'atelier de tracé", "Dossier technique", True, dt_aide())]


def img_doc(name, alt, cap):
    src, w, h = png(name)
    return (f'<img class="doc-img" src="{src}" width="{w}" height="{h}" alt="{esc(alt)}">'
            f'<p class="doc-cap">{cap}</p>')


def res_table(rows):
    """Tableau des caractéristiques des forces (correction)."""
    body = "".join(f"<tr><td>{n}</td><td>{p}</td><td>{d}</td><td>{s}</td><td>{v}</td></tr>" for n, p, d, s, v in rows)
    return ('<table class="t res-table"><thead><tr><th>Force</th><th>Point d\'app.</th><th>Direction</th><th>Sens</th>'
            f"<th>Intensité</th></tr></thead><tbody>{body}</tbody></table>")


def sens_txt(F):
    """Sens d'une force (repère écran) en mots."""
    a = math.degrees(math.atan2(-F[1], F[0]))
    noms = [(-22.5, 22.5, "vers la droite"), (22.5, 67.5, "vers le haut et la droite"),
            (67.5, 112.5, "vers le haut"), (112.5, 157.5, "vers le haut et la gauche"),
            (-67.5, -22.5, "vers le bas et la droite"), (-112.5, -67.5, "vers le bas"),
            (-157.5, -112.5, "vers le bas et la gauche")]
    for lo, hi, n in noms:
        if lo <= a < hi:
            return n
    return "vers la gauche"


# ============================================================ EXERCICE 1.2 — PANNEAU SOLAIRE
PAN = DR("PANNEAU", "g-panneau-dr", (1780, 1142), 80,
         zones=[{"scale": 50, "unit": "N", "bar": (1150, 1085)}],
         points={"A": (251.2, 166.2), "G": (623.8, 526.2), "D": (782.5, 696.2), "E": (253.8, 696.2)}, rs=1.2)
P_PAN = 38 * 10
RES_PAN = trois_forces(("P", PAN.points["G"], (0, P_PAN)), ("D3/1", PAN.points["D"], (1, 0)), ("A2/1", PAN.points["A"]))
PAN.construire(RES_PAN, (1150, 150), [0, 1, 2], ["CORR", "TEAL", "PURP"], "N")
PAN.texte("Dynamique (1 cm ↔ 50 N)", 1150, 110, "CORR", 20)
NA_PAN, ND_PAN = RES_PAN["normes"]["A2/1"], RES_PAN["normes"]["D3/1"]
ANG_A_PAN = atelier.angle(RES_PAN["u3"])
FD_PAN = RES_PAN["forces"][1][2]
FA_PAN = RES_PAN["forces"][2][2]

PARTS_PAN = [
    {"num": "1", "minutes": 10, "title": "Poids du panneau et bilan des actions",
     "intro": [
         "<p>Lors du réglage de l'inclinaison d'un panneau solaire, on veut déterminer les caractéristiques des forces "
         "qui s'exercent sur le panneau <strong>(1)</strong>, en équilibre dans la position représentée. Le panneau "
         "est articulé en A sur le pied support <strong>(2)</strong> et tenu en D par la barre de réglage "
         "<strong>(3)</strong>, elle-même articulée en E sur le pied.</p>",
         '<div class="n3-split">' + figure("g-panneau", "Panneau solaire 1 incliné, articulé en A sur le pied support 2, "
                                           "tenu en D par la barre de réglage horizontale 3 articulée en E ; centre de "
                                           "gravité G", "Figure 1 — Panneau solaire en position de réglage.", 360) +
         data_box(["Masse du panneau solaire : <i>m</i> = 38 kg ; <i>g</i> = 10 N/kg.",
                   "Liaisons en A, D et E : articulations sans frottement.",
                   "Poids de la barre de réglage (3) négligé.",
                   "Le panneau (1) est en équilibre."]) + "</div>",
     ],
     "blocks": [
         QBAR("Q1.1 – Q1.4", ["DP1", "DT1"]),
         Q("q1_1", "Calculer le poids <i>P</i> du panneau solaire.", H_EX,
           num(P_PAN, "N", absTol=0.5, variants=[var(P_PAN / 10, "daN", absTol=0.05)]), "<i>P</i> = 380 N",
           "<p><i>P</i> = <i>m</i> · <i>g</i> = 38 × 10 = <b>380 N</b>, vertical, vers le bas, appliqué en G.</p>"),
         Q("q1_2", "Combien d'actions mécaniques extérieures s'exercent sur le panneau (1) ?", H_ENTIER, ENTIER(3),
           "3 : le poids en G, l'action du pied en A, l'action de la barre en D",
           f"<p>{V('P')} en G, {V('A', '2/1')} (pied support en A) et {V('D', '3/1')} (barre de réglage en D). Le panneau "
           "est un <strong>solide soumis à trois forces</strong>.</p>"),
         Q("q1_3", "La barre de réglage (3) est articulée en E et en D, et son poids est négligé. À combien de forces "
           "est-elle soumise ?", H_ENTIER, ENTIER(2), "2 forces, en E et en D",
           "<p>La barre (3) ne touche que le pied (en E) et le panneau (en D) : c'est un <strong>solide soumis à deux "
           "forces</strong>.</p>"),
         Q("q1_4", f"En déduire la droite d'action de {V('D', '3/1')}.", H_DROITE,
           CODE(contains=["ed", "de", "horizont"]), "la droite (ED), horizontale",
           "<p>Deux forces en équilibre ont la même droite d'action, celle qui joint leurs points d'application : "
           f"(ED). Par le principe des actions mutuelles, {V('D', '3/1')} est portée par <strong>(ED)</strong>, "
           "c'est-à-dire <strong>horizontale</strong>.</p>"),
     ]},
    {"num": "2", "minutes": 30, "title": "Résolution graphique",
     "intro": ["<p>Le panneau est soumis à trois forces non parallèles : leurs droites d'action sont concourantes et "
               "leur dynamique est fermé. On travaille sur le document réponse ci-dessous, à droite duquel une zone "
               "est réservée au dynamique (échelle 1 cm ↔ 50 N).</p>"],
     "blocks": [
         QBAR("Q2.1", ["DT1", "DT2"], ans="sur le DR"),
         SK("sk_q2_1", "Q2.1", "PANNEAU",
            "Tracer les droites d'action des trois forces (point de concours I), puis le dynamique des forces dans la "
            "zone de droite, à l'échelle 1 cm ↔ 50 N.",
            ["La droite d'action de P est verticale et passe par G.",
             "La droite d'action de D3/1 est horizontale et passe par D.",
             "Le point de concours I est marqué ; la droite d'action de A2/1 joint A à I.",
             "P est tracé à l'échelle (7,6 cm pour 380 N).",
             "Les parallèles aux directions de D et de A ferment le triangle ; les vecteurs se suivent bout à bout."],
            atelier.AIDE + "<p>Conseil : <b>Droite d'action</b> par G (verticale) et par D (horizontale), <b>Point</b> à "
            "leur intersection I, puis <b>Droite d'action</b> de A vers I. Dans la zone de droite : saisis 380 dans "
            "« Intensité imposée » et trace P vers le bas, puis utilise <b>Parallèle</b> depuis ses deux extrémités.</p>",
            "<p>P vertical par G et D3/1 horizontal par D se coupent en <strong>I</strong>, à la verticale de G et à la "
            "hauteur de D. La droite d'action de A2/1 est <strong>(AI)</strong>, inclinée d'environ "
            f"{fr(ANG_A_PAN, 0)}° sur l'horizontale.</p><p>Dynamique : P (7,6 cm) vers le bas, puis la parallèle à "
            "(ED) par son extrémité, puis la parallèle à (AI) par son origine. Les vecteurs se suivent : "
            f"D3/1 ≈ {fr(ND_PAN, 0)} N vers la droite, A2/1 ≈ {fr(NA_PAN, 0)} N vers le haut et la gauche.</p>" +
            res_table([("P", "G", "verticale", "vers le bas", "380 N"),
                       (f"D<sub>3/1</sub>", "D", "(ED), horizontale", sens_txt(FD_PAN), f"≈ {fr(ND_PAN, 0)} N"),
                       (f"A<sub>2/1</sub>", "A", f"(AI), ≈ {fr(ANG_A_PAN, 0)}°", sens_txt(FA_PAN), f"≈ {fr(NA_PAN, 0)} N")])),
         QBAR("Q2.2 – Q2.6", ["DT1"]),
         Q("q2_2", f"Relever sur ton dynamique l'intensité de {V('D', '3/1')}.", H_LU,
           lu(ND_PAN, "N", variants=[var(ND_PAN / 10, "daN", relTol=TOL)]), f"‖{V('D', '3/1')}‖ ≈ {fr(ND_PAN, 0)} N",
           f"<p>Sur le dynamique, le côté horizontal mesure environ {fr(ND_PAN / 50, 1)} cm, soit "
           f"{fr(ND_PAN / 50, 1)} × 50 ≈ <b>{fr(ND_PAN, 0)} N</b>.</p>"),
         Q("q2_3", f"Relever l'intensité de {V('A', '2/1')}.", H_LU,
           lu(NA_PAN, "N", variants=[var(NA_PAN / 10, "daN", relTol=TOL)]), f"‖{V('A', '2/1')}‖ ≈ {fr(NA_PAN, 0)} N",
           f"<p>Le côté parallèle à (AI) mesure environ {fr(NA_PAN / 50, 1)} cm : {fr(NA_PAN / 50, 1)} × 50 ≈ "
           f"<b>{fr(NA_PAN, 0)} N</b>. C'est la plus grande des trois forces : le pied porte le poids et retient le "
           "panneau.</p>"),
         Q("q2_4", f"Quel angle la droite d'action de {V('A', '2/1')} fait-elle avec l'horizontale ?", H_ANGLE,
           num(ANG_A_PAN, "deg", absTol=3), f"≈ {fr(ANG_A_PAN, 0)}°",
           "<p>La droite (AI) est mesurée avec l'outil <b>Mesurer</b> (l'angle s'affiche) ou au rapporteur : environ "
           f"<b>{fr(ANG_A_PAN, 0)}°</b>.</p>"),
         Q("q2_5", f"Quel est le sens de {V('D', '3/1')} ?", H_SENS,
           KW([["droite"]], [["droit"]], forbid=["gauche"]), "vers la droite",
           "<p>Pour fermer le dynamique en mettant les vecteurs bout à bout, D3/1 part de l'extrémité de P vers la "
           "<strong>droite</strong> : la barre pousse le panneau vers l'extérieur.</p>"),
         Q("q2_6", "La barre de réglage (3) est-elle comprimée ou tendue ?", "Réponds en un mot.", COMPRIME, "comprimée",
           "<p>La barre pousse le panneau en D (vers la droite, loin de E) : elle est <strong>comprimée</strong> entre "
           "E et D.</p>"),
     ]},
]


def dp_panneau():
    return ('<div class="doc-text"><h3>Panneau solaire réglable</h3><p>Le panneau (1), de 38 kg, est articulé en A au '
            "sommet du pied support (2). Son inclinaison se règle avec la barre (3), percée de plusieurs trous, articulée "
            "en E sur le pied et en D sur le panneau. Toutes les liaisons sont des articulations sans frottement.</p></div>"
            + img_doc("g-panneau", "Panneau solaire, pied support et barre de réglage", "Le panneau en position de réglage."))


# ============================================================ EXERCICE 1.3 — PINCE KOBELCO
VERIN = 2500  # kN


def _pince_dr(name, img, size, pts, ref, v1, v2, nom_contact):
    L = math.hypot(v2[0] - v1[0], v2[1] - v1[1])
    d = DR(name, img, size, L / 10, zones=[{"scale": 250, "unit": "kN", "bar": (40, 600)}],
           points={**pts, "origine de Fc2/3": v1, "extrémité de Fc2/3": v2}, refs=[ref, v1 + v2], alpha=0.5, rs=1.6)
    u = ((v2[0] - v1[0]) / L, (v2[1] - v1[1]) / L)
    res = trois_forces(("Fc2/3", pts["C"], (VERIN * u[0], VERIN * u[1])), (nom_contact, pts[nom_contact[0]], (1, 0)),
                       ("B1/3", pts["B"]))
    # correction : directions + I ; dynamique à partir du vecteur donné : Fc, puis B (par l'extrémité), puis contact
    for i in (1, 2):
        n, p, F = res["forces"][i]
        d.droite(p, F if i == 1 else res["u3"])
    d.point(res["I"], "I")
    Fc, Fcon, Fb = res["forces"][0][2], res["forces"][1][2], res["forces"][2][2]
    k = d.px_cm / 250
    x = (v2[0] + Fb[0] * k, v2[1] + Fb[1] * k)
    d.vecteur(v2, x, f"B1/3 ≈ {fr(math.hypot(*Fb))} kN", "PURP", -1)
    d.vecteur(x, v1, f"{nom_contact} ≈ {fr(math.hypot(*Fcon))} kN", "TEAL", 1)
    d.droite(v1, (1, 0), "TEAL", 1.6)
    d.droite(v2, res["u3"], "PURP", 1.6)
    return d, res


PINCE1, RES_P1 = _pince_dr("PINCE1", "g-pince-dr1", (1169, 670),
                           {"B": (80, 95.75), "C": (247.5, 102.5), "G": (150, 313.75)},
                           (225.5, 9.5, 270, 197.5), (983.75, 23), (1125, 650), "G béton/3")
PINCE2, RES_P2 = _pince_dr("PINCE2", "g-pince-dr2", (1169, 665),
                           {"B": (76.25, 112.5), "C": (248, 138), "I": (148, 452.5)},
                           (219.5, 12, 270.5, 242.5), (982, 24.5), (1118.75, 653.75), "I béton/3")
NG_P1, NB_P1 = RES_P1["normes"]["G béton/3"], RES_P1["normes"]["B1/3"]
NI_P2, NB_P2 = RES_P2["normes"]["I béton/3"], RES_P2["normes"]["B1/3"]


def _pince_sk(sid, label, bg, contact, res):
    nb, nc = res["normes"]["B1/3"], res["normes"][f"{contact} béton/3"]
    return SK(sid, label, bg,
              f"Représenter les droites d'action des forces en B, C et {contact} (point de concours), puis tracer le "
              "dynamique des forces à partir du vecteur Fc2/3 déjà tracé (1 cm ↔ 250 kN).",
              [f"La droite d'action en {contact} est horizontale (contact avec le bloc, perpendiculaire à ses faces).",
               f"Le point de concours I est à l'intersection de la droite (AC) passant par C et de l'horizontale par {contact}.",
               "La droite d'action en B joint B au point I.",
               f"Le dynamique est fermé à partir de Fc2/3 : parallèle à l'horizontale par une extrémité, parallèle à (BI) par l'autre.",
               "Les vecteurs se suivent bout à bout et sont nommés."],
              atelier.AIDE + f"<p>Conseil : <b>Droite d'action</b> horizontale par {contact}, puis <b>Point</b> I à "
              "l'intersection avec la droite tracée à travers C, puis <b>Droite d'action</b> de B vers I. Pour le "
              "dynamique : <b>Parallèle</b> à l'horizontale par l'origine de Fc2/3, <b>Parallèle</b> à (BI) par son "
              "extrémité, puis <b>Vecteur</b> sur chaque côté.</p>",
              f"<p>La force du bloc en {contact} est horizontale ; elle coupe la droite (AC) en <strong>I</strong>. La "
              "force de l'articulation B passe par I. Le dynamique, construit à partir de Fc2/3 (10 cm), donne :</p>" +
              res_table([("Fc<sub>2/3</sub>", "C", "(AC)", "vers le bas", "2 500 kN"),
                         ("B<sub>1/3</sub>", "B", "(BI)", sens_txt(res["forces"][2][2]), f"≈ {fr(nb)} kN"),
                         (f"{contact}<sub>béton/3</sub>", contact, "horizontale", sens_txt(res["forces"][1][2]),
                          f"≈ {fr(nc)} kN")]))


PARTS_PINCE = [
    {"num": "1", "minutes": 15, "title": "Vérin et bloc de béton",
     "intro": [
         "<p>La pince de démolition comprend un corps <strong>(1)</strong>, deux vérins <strong>(2)</strong> articulés "
         "en A et D sur le corps et en C et F sur les mâchoires <strong>(3)</strong>. Chaque vérin exerce une force de "
         "<strong>2 500 kN</strong>. On veut concasser un bloc de béton de 800 mm de largeur et trouver la "
         "configuration la plus efficace : bloc serré entre H et G (configuration 1) ou entre I et J (configuration 2). "
         "Le système est symétrique : on étudie la mâchoire de droite. Les poids sont négligés.</p>",
         '<div class="n3-split">' + figure("g-pince-schema", "Schéma de la pince : corps 1, vérins 2 entre A et C, D et F, "
                                           "mâchoires 3 articulées en B et E, points de serrage G, H, I, J",
                                           "Figure 1 — Pince et repères.", 300) +
         figure("g-pince-configs", "Configuration 1 : bloc serré entre H et G ; configuration 2 : bloc serré entre I et J",
                "Figure 2 — Les deux configurations.", 380) + "</div>",
     ],
     "blocks": [
         QBAR("Q1.1 – Q1.5", ["DP1", "DT1"]),
         Q("q1_1", "On isole le vérin (2) de droite. À combien de forces est-il soumis ?", H_ENTIER, ENTIER(2),
           "2 forces, en A et en C",
           "<p>Le vérin n'est lié qu'au corps (en A) et à la mâchoire (en C) ; son poids est négligé : solide soumis "
           "à deux forces.</p>"),
         Q("q1_2", "Quelle est la droite d'action des forces en A et en C ?", H_DROITE, DROITE("A", "C"),
           "la droite (AC)", "<p>Deux forces en équilibre ont pour droite d'action la droite qui joint leurs points "
           "d'application : <strong>(AC)</strong>, l'axe du vérin.</p>"),
         Q("q1_3", "Quelle est l'intensité de la force exercée en C par le vérin sur la mâchoire ?", H_EX,
           num(VERIN, "kN", absTol=0.5, variants=[var(VERIN * 1000, "N", absTol=500)]),
           "2 500 kN", "<p>Même intensité aux deux extrémités du vérin : <b>2 500 kN</b> en A comme en C.</p>"),
         Q("q1_4", "Le vérin pousse sur la mâchoire pour fermer la pince. Est-il comprimé ?", H_OUINON, YES,
           "oui, il est comprimé", "<p>Les deux forces sont dirigées vers l'intérieur du vérin : il travaille en "
           "<strong>compression</strong>.</p>"),
         Q("q1_5", "On isole le bloc de béton, serré entre H et G (contacts sans frottement). Quelle est la direction "
           "des forces en H et en G ?", "Réponds en un ou quelques mots.", CODE(contains=["hg", "gh", "horizont"]),
           "horizontale, portée par (HG)",
           "<p>Le bloc est soumis à deux forces (poids négligé) : elles sont portées par <strong>(HG)</strong>, qui est "
           "horizontale (perpendiculaire aux faces du bloc). Même intensité, sens contraires : les deux mâchoires "
           "serrent le bloc.</p>"),
     ]},
    {"num": "2", "minutes": 25, "title": "Configuration 1 : mâchoire serrant en G",
     "intro": ["<p>On isole la mâchoire (3) de droite : elle est soumise à la force du vérin en C (connue, déjà tracée "
               "sur le DR à l'échelle 1 cm ↔ 250 kN), à la force du bloc en G (horizontale) et à la force de "
               "l'articulation en B (inconnue).</p>"],
     "blocks": [
         QBAR("Q2.1", ["DT1", "DT2"], ans="sur le DR"),
         _pince_sk("sk_q2_1", "Q2.1", "PINCE1", "G", RES_P1),
         QBAR("Q2.2 – Q2.3", ["DT1"]),
         Q("q2_2", "Relever l'intensité de la force exercée par le bloc sur la mâchoire en G (effort de concassage).",
           H_LU, lu(NG_P1, "kN", variants=[var(NG_P1 * 1000, "N", relTol=TOL)]), f"≈ {fr(NG_P1)} kN",
           f"<p>Côté horizontal du dynamique : environ {fr(NG_P1 / 250, 1)} cm, soit ≈ <b>{fr(NG_P1)} kN</b>.</p>"),
         Q("q2_3", "Relever l'intensité de la force de l'articulation en B.", H_LU,
           lu(NB_P1, "kN", variants=[var(NB_P1 * 1000, "N", relTol=TOL)]), f"≈ {fr(NB_P1)} kN",
           f"<p>Côté parallèle à (BI) : environ {fr(NB_P1 / 250, 1)} cm, soit ≈ <b>{fr(NB_P1)} kN</b>. L'axe B est "
           "le plus chargé.</p>"),
     ]},
    {"num": "3", "minutes": 25, "title": "Configuration 2 et conclusion",
     "intro": ["<p>Même étude quand le bloc est serré entre I et J, plus loin de l'articulation B.</p>"],
     "blocks": [
         QBAR("Q3.1", ["DT1", "DT2"], ans="sur le DR"),
         _pince_sk("sk_q3_1", "Q3.1", "PINCE2", "I", RES_P2),
         QBAR("Q3.2 – Q3.5", ["DT1"]),
         Q("q3_2", "Relever l'intensité de la force exercée par le bloc sur la mâchoire en I.", H_LU,
           lu(NI_P2, "kN", variants=[var(NI_P2 * 1000, "N", relTol=TOL)]), f"≈ {fr(NI_P2)} kN",
           f"<p>Côté horizontal du dynamique : environ {fr(NI_P2 / 250, 1)} cm, soit ≈ <b>{fr(NI_P2)} kN</b>.</p>"),
         Q("q3_3", "Relever l'intensité de la force de l'articulation en B.", H_LU,
           lu(NB_P2, "kN", variants=[var(NB_P2 * 1000, "N", relTol=TOL)]), f"≈ {fr(NB_P2)} kN",
           f"<p>Environ {fr(NB_P2 / 250, 1)} cm, soit ≈ <b>{fr(NB_P2)} kN</b>.</p>"),
         Q("q3_4", "Quelle configuration est la plus efficace pour concasser le bloc ?", "Réponds par 1 ou 2.",
           CODE(equals=["1", "configuration1", "laconfiguration1", "config1", "laconfig1", "c1"]), "la configuration 1",
           f"<p>Avec le même vérin, le bloc reçoit ≈ {fr(NG_P1)} kN en configuration 1 contre ≈ {fr(NI_P2)} kN en "
           "configuration 2 : la <strong>configuration 1</strong> écrase le bloc avec un effort environ "
           f"{fr(NG_P1 / NI_P2, 1)} fois plus grand.</p>"),
         Q("q3_5", "L'effort de serrage est-il plus grand quand le bloc est serré près de l'articulation B ?", H_OUINON,
           YES, "oui", "<p>Comme pour une pince ou un casse-noix : plus le point de serrage est proche de l'axe "
           "d'articulation, plus le bras de levier de l'effort de serrage est court et plus cet effort est grand pour la "
           "même poussée du vérin.</p>"),
     ]},
]


def dp_pince():
    return ('<div class="doc-text"><h3>Pince de démolition</h3><p>Montée au bout d\'une flèche articulée, la pince '
            "concasse les bases d'immeubles et les dalles. Deux vérins (diamètre de piston 320 mm, pression 314 bar) "
            "articulés en A et D sur le corps (1) et en C et F sur les mâchoires (3) exercent chacun une force de "
            "<strong>2 500 kN</strong> (1 kN = 1 000 N).</p><p>Problématique : concasser un bloc de béton de 800 mm "
            "de largeur. Configuration 1 : efforts sur le bloc entre H et G. Configuration 2 : entre I et J. Le système "
            "est symétrique : on étudie la mâchoire de droite. Poids des pièces négligés.</p></div>" +
            img_doc("g-pince-photo", "Pelle de démolition équipée d'une pince", "Pelle de démolition à flèche articulée.") +
            img_doc("g-pince-cotee", "Pince cotée : hauteur 2 720 mm, ouvertures 1 350 et 2 070 mm", "Encombrement de la pince (mm).") +
            img_doc("g-pince-schema", "Schéma : corps, vérins, mâchoires", "Repères des articulations.") +
            img_doc("g-pince-configs", "Les deux configurations de serrage", "Configurations 1 et 2."))


# ============================================================ EXERCICE 1.4 — CRIC HYDRAULIQUE ROULANT
CRIC = DR("CRIC", "g-cric-dr", (2430, 1548), 86.2,
          zones=[{"scale": 50, "unit": "daN", "bar": (90, 1470), "poly": [[0, 0], [1500, 0], [760, 1548], [0, 1548]]},
                 {"scale": 150, "unit": "daN", "bar": (1950, 1470)}],
          points={"G": (800, 135), "E (sellette)": (785, 531), "F": (895, 725.5), "B": (1422, 672.5),
                  "D": (1454.5, 990), "E (bras)": (2272.5, 548)},
          refs=[(342.5, 807.5, 1112.5, 692.5), (1241.25, 975, 1938.75, 1022)], alpha=0.45, rs=1.0)
CF = (1112.5 - 342.5, 692.5 - 807.5)
AD = (1938.75 - 1241.25, 1022 - 975)
RES_S = trois_forces(("G V/4", CRIC.points["G"], (0, 400)), ("F3/4", CRIC.points["F"], CF), ("E2/4", CRIC.points["E (sellette)"]))
E24 = RES_S["forces"][2][2]
RES_B = trois_forces(("E4/2", CRIC.points["E (bras)"], (-E24[0], -E24[1])), ("D1/2", CRIC.points["D"], AD),
                     ("B0/2", CRIC.points["B"]))
CRIC.construire(RES_S, (560, 430), [0, 1, 2], ["CORR", "TEAL", "PURP"], "daN", dirs=[True, False, True], sides=[-1, 1, -1])
CRIC.construire(RES_B, (1700, 70), [0, 1, 2], ["PURP", "TEAL", "ORNG"], "daN", dirs=[True, False, True], sides=[1, 1, 1])
NE_C, NF_C = RES_S["normes"]["E2/4"], RES_S["normes"]["F3/4"]
ND_C, NB_C = RES_B["normes"]["D1/2"], RES_B["normes"]["B0/2"]

PARTS_CRIC = [
    {"num": "1", "minutes": 15, "title": "Bielle et groupe hydraulique",
     "intro": [
         "<p>Le cric est constitué d'un groupe hydraulique <strong>(1)</strong> articulé en A sur le châssis roulant "
         "<strong>(0)</strong>, dont le piston est lié en D à un bras <strong>(2)</strong>. Le bras, articulé en B sur "
         "le châssis, est lié en E à la sellette <strong>(4)</strong>. Une bielle <strong>(3)</strong>, liée en C au "
         "châssis et en F à la sellette, empêche la rotation de cette dernière. Lors de la levée d'un véhicule, un "
         "effort de <strong>400 daN</strong>, vertical, vers le bas, s'exerce en G sur la sellette. On cherche l'effort "
         "que doit fournir le vérin.</p>",
         figure("g-cric-meca", "Cric : groupe hydraulique 1 de A à D, bras 2 articulé en B, sellette 4 en E, bielle 3 de C à F, "
                "charge en G", "Figure 1 — Cric hydraulique roulant (plan de symétrie).", 620),
         data_box(["Étude dans le plan de symétrie, pour la position représentée.",
                   "Liaisons parfaites (frottements négligés) ; poids des pièces négligés.",
                   "Charge : G<sub>V/4</sub> = 400 daN, verticale, vers le bas."]),
     ],
     "blocks": [
         QBAR("Q1.1 – Q1.4", ["DP1", "DT1"]),
         Q("q1_1", "On isole la bielle (3). Quelle est la droite d'action des efforts en C et en F ?", H_DROITE,
           DROITE("C", "F"), "la droite (CF)", "<p>La bielle, articulée en C et F et de poids négligé, est soumise à "
           "deux forces : elles sont portées par <strong>(CF)</strong>.</p>"),
         Q("q1_2", "On isole le groupe hydraulique (1). Quelle est la droite d'action des efforts en A et en D ?",
           H_DROITE, DROITE("A", "D"), "la droite (AD)", "<p>Le groupe hydraulique (corps + piston) n'est lié qu'en A et "
           "en D : deux forces portées par <strong>(AD)</strong>, l'axe du vérin.</p>"),
         Q("q1_3", f"D'après le principe des actions mutuelles, {V('F', '4/3')} et {V('F', '3/4')} ont la même direction "
           "et la même intensité. Leurs sens sont-ils…", "Réponds en un mot.", SENS_OPPOSES, "contraires (opposés)",
           f"<p>{V('F', '3/4')} = −{V('F', '4/3')} : même droite d'action (CF), même intensité, sens contraires.</p>"),
         Q("q1_4", "On isole la sellette (4). À combien de forces est-elle soumise ?", H_ENTIER, ENTIER(3),
           "3 : en G (charge), en E (bras), en F (bielle)",
           "<p>La charge en G (connue), l'action du bras en E (inconnue) et l'action de la bielle en F (direction (CF) "
           "connue) : solide soumis à <strong>trois forces</strong>.</p>"),
     ]},
    {"num": "2", "minutes": 40, "title": "Constructions graphiques sur le DR",
     "intro": ["<p>Le DR comporte deux zones : à gauche la sellette (4), échelle <strong>1 cm ↔ 50 daN</strong> ; à "
               "droite le bras (2), échelle <strong>1 cm ↔ 150 daN</strong>. L'outil Vecteur applique automatiquement "
               "l'échelle de la zone où commence le vecteur. Les droites (CF) et (AD) sont données.</p>"],
     "blocks": [
         QBAR("Q2.1", ["DT1", "DT2"], ans="sur le DR"),
         SK("sk_q2_1", "Q2.1", "CRIC",
            "Sellette (4) : déterminer la direction de l'action en E (point de concours) et tracer le dynamique. Bras (2) : "
            "reporter E4/2, déterminer la direction de l'action en B et tracer le dynamique.",
            ["Sellette : la verticale par G coupe (CF) en I ; la droite d'action de E2/4 est (EI).",
             "Sellette : dynamique fermé, la charge de 400 daN tracée à l'échelle (8 cm).",
             "Bras : E4/2 est reporté en E (parallèle à E2/4, sens opposé, même intensité).",
             "Bras : la droite d'action de E4/2 coupe (AD) en I' ; la droite d'action de B0/2 est (BI').",
             "Bras : dynamique fermé à l'échelle 1 cm ↔ 150 daN, vecteurs bout à bout."],
            atelier.AIDE + "<p>Conseil : pour reporter la direction de E sur le bras, utilise <b>Parallèle</b> en "
            "choisissant comme référence ta droite (EI) de la sellette, puis appuie sur le point E du bras.</p>",
            "<p><strong>Sellette.</strong> La verticale de G coupe (CF) en I, juste sous F : l'action du bras en E est "
            "presque verticale. Dynamique (1 cm ↔ 50 daN) : 400 daN vers le bas, F3/4 très petit le long de (CF), "
            "E2/4 ferme le triangle.</p>" +
            res_table([("G<sub>V/4</sub>", "G", "verticale", "vers le bas", "400 daN"),
                       ("F<sub>3/4</sub>", "F", "(CF)", sens_txt(RES_S["forces"][1][2]), f"≈ {fr(NF_C)} daN"),
                       ("E<sub>2/4</sub>", "E", "(EI)", sens_txt(E24), f"≈ {fr(NE_C)} daN")]) +
            "<p><strong>Bras.</strong> E4/2 = −E2/4 descend en E ; sa droite d'action coupe (AD) en I'. La force de "
            "l'articulation B passe par I'. Dynamique (1 cm ↔ 150 daN) :</p>" +
            res_table([("E<sub>4/2</sub>", "E", "// (EI)", sens_txt(RES_B["forces"][0][2]), f"≈ {fr(NE_C)} daN"),
                       ("D<sub>1/2</sub>", "D", "(AD)", sens_txt(RES_B["forces"][1][2]), f"≈ {fr(ND_C)} daN"),
                       ("B<sub>0/2</sub>", "B", "(BI')", sens_txt(RES_B["forces"][2][2]), f"≈ {fr(NB_C)} daN")])),
     ]},
    {"num": "3", "minutes": 15, "title": "Résultats",
     "intro": [],
     "blocks": [
         QBAR("Q3.1 – Q3.5", ["DT1"]),
         Q("q3_1", f"Relever l'intensité de {V('E', '2/4')}.", H_LU, lu(NE_C, "daN", variants=[var(NE_C * 10, "N", relTol=TOL)]),
           f"≈ {fr(NE_C)} daN", f"<p>≈ {fr(NE_C / 50, 1)} cm × 50 ≈ <b>{fr(NE_C)} daN</b> : le bras porte presque toute la "
           "charge.</p>"),
         Q("q3_2", f"Relever l'intensité de {V('F', '3/4')}.", "Lecture sur ton dynamique, arrondie à l'unité ; ce vecteur "
           "est court : vise juste. " + UNITE, num(NF_C, "daN", absTol=7, variants=[var(NF_C * 10, "N", absTol=70)]),
           f"≈ {fr(NF_C)} daN", f"<p>Le côté porté par (CF) ne mesure qu'environ {fr(NF_C / 50, 1)} cm : la bielle "
           f"n'est presque pas chargée (≈ <b>{fr(NF_C)} daN</b>). Elle sert seulement à garder la sellette "
           "horizontale.</p>"),
         Q("q3_3", f"Relever l'intensité de {V('D', '1/2')}, effort que doit fournir le vérin.", H_LU,
           lu(ND_C, "daN", variants=[var(ND_C * 10, "N", relTol=TOL)]), f"≈ {fr(ND_C)} daN",
           f"<p>≈ {fr(ND_C / 150, 1)} cm × 150 ≈ <b>{fr(ND_C)} daN</b>.</p>"),
         Q("q3_4", f"Relever l'intensité de {V('B', '0/2')}.", H_LU, lu(NB_C, "daN", variants=[var(NB_C * 10, "N", relTol=TOL)]),
           f"≈ {fr(NB_C)} daN", f"<p>≈ {fr(NB_C / 150, 1)} cm × 150 ≈ <b>{fr(NB_C)} daN</b>.</p>"),
         Q("q3_5", "L'effort du vérin est-il plus grand que la charge soulevée ?", H_OUINON, YES,
           f"oui, environ {fr(ND_C / 400, 1)} fois plus grand",
           f"<p>{fr(ND_C)} daN pour 400 daN soulevés : le vérin, presque horizontal et proche de l'articulation B, "
           "travaille avec un petit bras de levier. C'est le prix d'une grande course de levée ; le groupe "
           "hydraulique fournit cet effort sans difficulté.</p>"),
     ]},
]


def dp_cric():
    return ('<div class="doc-text"><h3>Cric hydraulique roulant</h3><p>Ce cric soulève les véhicules ; il se place '
            "rapidement sous le véhicule et demande peu d'effort à l'utilisateur. Groupe hydraulique (1) articulé en A "
            "sur le châssis roulant (0), piston lié en D au bras (2) ; bras articulé en B sur le châssis et lié en E à la "
            "sellette (4) ; bielle (3) liée en C au châssis et en F à la sellette. Charge : 400 daN verticale en G.</p></div>" +
            img_doc("g-cric-photo", "Cric hydraulique roulant rouge", "Le cric.") +
            img_doc("g-cric-meca", "Mécanisme du cric", "Les pièces et les articulations."))


# ============================================================ EXERCICE 1.5 — SUSPENSION ARRIÈRE DE VTT
VTT = DR("VTT", "g-vtt-dr", (2339, 1653), 78.74,
         zones=[{"scale": 10, "unit": "daN", "bar": (110, 1500), "poly": [[0, 0], [1024, 0], [1024, 1653], [0, 1653]]},
                {"scale": 40, "unit": "daN", "bar": (1100, 1500)}],
         points={"C": (456, 1147), "B": (670, 1300), "D (haubans)": (925, 696), "D (basculeur)": (1188, 1237),
                 "E": (1586, 1179), "F": (1727.5, 1009)},
         refs=[(344.2, 1361.2, 877.5, 1255.8), (1712.8, 821.7, 1755, 1363)], alpha=0.45, rs=1.0)
UAB = (877.5 - 344.2, 1255.8 - 1361.2)
UFG = (1755 - 1712.8, 1363 - 821.7)
RES_H = trois_forces(("C R/3", VTT.points["C"], (0, -65)), ("B4/3", VTT.points["B"], UAB), ("D2/3", VTT.points["D (haubans)"]))
D23 = RES_H["forces"][2][2]
RES_K = trois_forces(("D3/2", VTT.points["D (basculeur)"], (-D23[0], -D23[1])), ("F1/2", VTT.points["F"], UFG),
                     ("E0/2", VTT.points["E"]))
VTT.construire(RES_H, (200, 1000), [0, 1, 2], ["CORR", "TEAL", "PURP"], "daN", dirs=[True, False, True], sides=[1, -1, 1])
VTT.construire(RES_K, (1300, 650), [0, 1, 2], ["PURP", "TEAL", "ORNG"], "daN", dirs=[True, False, True], sides=[1, 1, 1])
NB_V, ND_V = RES_H["normes"]["B4/3"], RES_H["normes"]["D2/3"]
NF_V, NE_V = RES_K["normes"]["F1/2"], RES_K["normes"]["E0/2"]

PARTS_VTT = [
    {"num": "1", "minutes": 15, "title": "Isolements préliminaires",
     "intro": [
         "<p>La suspension arrière d'un VTT est constituée d'un amortisseur <strong>(1)</strong> articulé en G sur le "
         "cadre <strong>(0)</strong> et en F sur le basculeur <strong>(2)</strong>. Le basculeur est articulé en E sur "
         "le cadre et en D sur les haubans <strong>(3)</strong>. Les bases <strong>(4)</strong> sont articulées en A sur "
         "le cadre et en B sur les haubans. On cherche l'effort que supporte l'amortisseur quand la roue exerce en C "
         "sur les haubans un effort vertical de <strong>65 daN</strong>, noté C<sub>R/3</sub>.</p>",
         figure("g-vtt-cadre", "Cadre 0, amortisseur 1 entre F et G, basculeur 2 articulé en E, haubans 3 de C à D, bases 4 de "
                "A à B ; effort de la roue en C vertical vers le haut", "Figure 1 — Suspension arrière (plan de symétrie).", 620),
         data_box(["Étude dans le plan de symétrie du vélo, pour la position représentée.",
                   "Liaisons parfaites ; poids des pièces négligés ; pièces rigides.",
                   "C<sub>R/3</sub> = 65 daN, vertical, vers le haut."]),
     ],
     "blocks": [
         QBAR("Q1.1 – Q1.5", ["DP1", "DT1"]),
         Q("q1_1", "On isole les bases (4). Quelle est la droite d'action des actions en A et en B ?", H_DROITE,
           DROITE("A", "B"), "la droite (AB)", "<p>Les bases, articulées en A et B, sont soumises à deux forces "
           "portées par <strong>(AB)</strong>.</p>"),
         Q("q1_2", "On isole l'amortisseur (1). Quelle est la droite d'action des actions en F et en G ?", H_DROITE,
           DROITE("F", "G"), "la droite (FG)", "<p>Deux forces portées par <strong>(FG)</strong>, l'axe de "
           "l'amortisseur.</p>"),
         Q("q1_3", f"D'après le principe des actions mutuelles, a-t-on {V('B', '4/3')} = −{V('B', '3/4')} ?", H_OUINON,
           YES, "oui", f"<p>{V('B', '4/3')} et {V('B', '3/4')} ont même droite d'action (AB), même intensité et des "
           "sens contraires.</p>"),
         Q("q1_4", "On isole les haubans (3). À combien de forces sont-ils soumis ?", H_ENTIER, ENTIER(3),
           "3 : en C (roue), en B (bases), en D (basculeur)",
           "<p>C<sub>R/3</sub> connue, B<sub>4/3</sub> de direction (AB) connue, D<sub>2/3</sub> inconnue : trois forces, "
           "concourantes.</p>"),
         Q("q1_5", "On isole le basculeur (2). À combien de forces est-il soumis ?", H_ENTIER, ENTIER(3),
           "3 : en D (haubans), en F (amortisseur), en E (cadre)",
           "<p>D<sub>3/2</sub> (déduite des haubans), F<sub>1/2</sub> de direction (FG), E<sub>0/2</sub> inconnue.</p>"),
     ]},
    {"num": "2", "minutes": 40, "title": "Constructions graphiques sur le DR",
     "intro": ["<p>Zone de gauche : haubans (3), échelle <strong>1 cm ↔ 10 daN</strong>. Zone de droite : basculeur "
               "(2), échelle <strong>1 cm ↔ 40 daN</strong>. Les droites (AB) et (FG) sont données.</p>"],
     "blocks": [
         QBAR("Q2.1", ["DT1", "DT2"], ans="sur le DR"),
         SK("sk_q2_1", "Q2.1", "VTT",
            "Haubans (3) : déterminer la direction de l'action en D et tracer le dynamique. Basculeur (2) : reporter "
            "D3/2, déterminer la direction de l'action en E et tracer le dynamique.",
            ["Haubans : la verticale par C coupe (AB) en I ; la droite d'action de D2/3 est (DI).",
             "Haubans : dynamique fermé, C tracé à l'échelle (6,5 cm pour 65 daN).",
             "Basculeur : D3/2 est reporté en D (parallèle à (DI), sens opposé à D2/3, même intensité).",
             "Basculeur : la droite d'action de D3/2 coupe (FG) en I' ; la droite d'action de E0/2 est (EI').",
             "Basculeur : dynamique fermé à l'échelle 1 cm ↔ 40 daN, vecteurs bout à bout."],
            atelier.AIDE + "<p>Conseil : pour reporter la direction de D sur le basculeur, utilise <b>Parallèle</b> avec "
            "ta droite (DI) des haubans comme référence, puis appuie sur le point D du basculeur.</p>",
            "<p><strong>Haubans.</strong> La verticale de C coupe (AB) en I, sous C ; l'action du basculeur en D est "
            "portée par (DI). Dynamique (1 cm ↔ 10 daN) :</p>" +
            res_table([("C<sub>R/3</sub>", "C", "verticale", "vers le haut", "65 daN"),
                       ("B<sub>4/3</sub>", "B", "(AB)", sens_txt(RES_H["forces"][1][2]), f"≈ {fr(NB_V)} daN"),
                       ("D<sub>2/3</sub>", "D", "(DI)", sens_txt(D23), f"≈ {fr(ND_V)} daN")]) +
            "<p><strong>Basculeur.</strong> D3/2 = −D2/3 ; sa droite d'action coupe (FG) en I', au-dessus du basculeur. "
            "L'action du cadre en E passe par I'. Dynamique (1 cm ↔ 40 daN) :</p>" +
            res_table([("D<sub>3/2</sub>", "D", "// (DI)", sens_txt(RES_K["forces"][0][2]), f"≈ {fr(ND_V)} daN"),
                       ("F<sub>1/2</sub>", "F", "(FG)", sens_txt(RES_K["forces"][1][2]), f"≈ {fr(NF_V)} daN"),
                       ("E<sub>0/2</sub>", "E", "(EI')", sens_txt(RES_K["forces"][2][2]), f"≈ {fr(NE_V)} daN")])),
     ]},
    {"num": "3", "minutes": 15, "title": "Résultats et conclusion",
     "intro": [],
     "blocks": [
         QBAR("Q3.1 – Q3.6", ["DT1"]),
         Q("q3_1", f"Relever l'intensité de {V('B', '4/3')}.", H_LU, lu(NB_V, "daN", variants=[var(NB_V * 10, "N", relTol=TOL)]),
           f"≈ {fr(NB_V)} daN", f"<p>≈ {fr(NB_V / 10, 1)} cm × 10 ≈ <b>{fr(NB_V)} daN</b>.</p>"),
         Q("q3_2", f"Relever l'intensité de {V('D', '2/3')}.", H_LU, lu(ND_V, "daN", variants=[var(ND_V * 10, "N", relTol=TOL)]),
           f"≈ {fr(ND_V)} daN", f"<p>≈ {fr(ND_V / 10, 1)} cm × 10 ≈ <b>{fr(ND_V)} daN</b>.</p>"),
         Q("q3_3", f"Relever l'intensité de {V('F', '1/2')}.", H_LU, lu(NF_V, "daN", variants=[var(NF_V * 10, "N", relTol=TOL)]),
           f"≈ {fr(NF_V)} daN", f"<p>≈ {fr(NF_V / 40, 1)} cm × 40 ≈ <b>{fr(NF_V)} daN</b>.</p>"),
         Q("q3_4", f"Relever l'intensité de {V('E', '0/2')}.", H_LU, lu(NE_V, "daN", variants=[var(NE_V * 10, "N", relTol=TOL)]),
           f"≈ {fr(NE_V)} daN", f"<p>≈ {fr(NE_V / 40, 1)} cm × 40 ≈ <b>{fr(NE_V)} daN</b>.</p>"),
         Q("q3_5", "L'amortisseur est-il comprimé ?", H_OUINON, YES, "oui",
           "<p>F<sub>1/2</sub> pousse le basculeur vers le haut : par actions mutuelles, le basculeur pousse "
           "l'amortisseur vers le bas en F, le cadre le repousse en G : il est <strong>comprimé</strong>.</p>"),
         Q("q3_6", "Conclure : quel effort l'amortisseur supporte-t-il ?", H_LU,
           lu(NF_V, "daN", variants=[var(NF_V * 10, "N", relTol=TOL)]), f"≈ {fr(NF_V)} daN",
           f"<p>L'amortisseur supporte ≈ <b>{fr(NF_V)} daN</b>, soit environ {fr(NF_V / 65, 1)} fois l'effort de la roue : "
           "c'est cette valeur qui sert à régler sa précontrainte (il ne doit pas s'écraser de plus d'un tiers de sa "
           "course quand le cycliste monte sur le vélo).</p>"),
     ]},
]


def dp_vtt():
    return ('<div class="doc-text"><h3>Suspension arrière de VTT</h3><p>Amortisseur (1) articulé en G sur le cadre (0) et en '
            "F sur le basculeur (2) ; basculeur articulé en E sur le cadre et en D sur les haubans (3) ; bases (4) "
            "articulées en A sur le cadre et en B sur les haubans. Effort de la roue sur les haubans en C : 65 daN, "
            "vertical. En règle générale, l'amortisseur ne doit pas s'écraser de plus d'un tiers de sa course quand le "
            "cycliste monte sur le vélo.</p></div>" +
            img_doc("g-vtt-photo", "VTT tout suspendu", "Un VTT tout suspendu.") +
            img_doc("g-vtt-cadre", "Cadre et suspension arrière, repères des pièces", "Pièces et articulations."))


# ============================================================ définitions des exercices
DRS = {d.name: d for d in (PAN, PINCE1, PINCE2, CRIC, VTT)}
DR_TITRES = {"PANNEAU": ("DR1", "Q2.1", "Panneau solaire : droites d'action et dynamique"),
             "PINCE1": ("DR1", "Q2.1", "Mâchoire, configuration 1"),
             "PINCE2": ("DR2", "Q3.1", "Mâchoire, configuration 2"),
             "CRIC": ("DR1", "Q2.1", "Sellette (4) et bras (2)"),
             "VTT": ("DR1", "Q2.1", "Haubans (3) et basculeur (2)")}
CONVENTIONS = ("<p><strong>Statique graphique.</strong> Les forces se déterminent par des tracés sur le document réponse "
               "(DR) : droites d'action, point de concours, dynamique des forces à l'échelle indiquée. Les intensités "
               "demandées se lisent sur ton dynamique ; la tolérance couvre la précision d'un tracé soigné (environ "
               "7 %). L'atelier de tracé (DT2) remplace règle, équerre et rapporteur.</p>")
CALCULS = ""

COMMUN = {"module": "src/graphique.py", "pastille": "n1", "level": "Niveau 1", "toolbar": atelier.toolbar,
          "sk_bg": {k: d.img for k, d in DRS.items()},
          "decor_helpers": "", "decor": {k: d.decor_js() for k, d in DRS.items()}, "dr_names": DR_TITRES,
          "extra_css": atelier.CSS, "extra_js": atelier.JS, "conventions": CONVENTIONS, "calculs": CALCULS,
          "cours": ("cours-statique-graphique.html", "Cours 1.1 — Statique graphique"),
          "sk_fact": "sur DR, avec l'atelier de tracé"}

EXOS = [
    {**COMMUN, "page": "panneau-solaire.html", "tag": "Exercice 1.2", "title": "Panneau solaire", "parts": PARTS_PAN,
     "docs": docs_for("Présentation du panneau solaire", dp_panneau), "vign": "carte-panneau-solaire.jpg",
     "mots": ["Poids", "Deux forces", "Point de concours", "Dynamique"],
     "alt": "Panneau solaire incliné sur son pied, barre de réglage horizontale",
     "hero": ("g-panneau", "Panneau solaire sur son pied support et sa barre de réglage",
              "Quelles forces tiennent le panneau en équilibre ?"),
     "sub": "Un panneau solaire de 38 kg tenu par son pied et une barre de réglage : calcul du poids, solide soumis à "
            "deux forces, puis droites d'action concourantes et dynamique des forces tracés sur le DR.",
     "desc": "Statique graphique : poids, solide soumis à deux puis à trois forces, point de concours et dynamique "
             "des forces pour un panneau solaire."},
    {**COMMUN, "page": "pince-kobelco.html", "tag": "Exercice 1.3", "title": "Pince de démolition", "parts": PARTS_PINCE,
     "docs": docs_for("Présentation de la pince", dp_pince), "vign": "carte-pince-kobelco.jpg",
     "mots": ["Vérin", "Trois forces", "Dynamique", "Comparer"],
     "alt": "Pelle de démolition équipée d'une pince",
     "hero": ("g-pince-photo", "Pelle de démolition équipée d'une pince à béton",
              "Où serrer le bloc pour l'écraser le plus fort ?"),
     "sub": "Une pince de démolition pousse ses mâchoires avec deux vérins de 2 500 kN. Deux constructions graphiques "
            "comparent l'effort de concassage selon l'endroit où le bloc de béton est serré.",
     "desc": "Statique graphique : solide soumis à deux et à trois forces, dynamique à l'échelle, comparaison de deux "
             "configurations d'une pince de démolition."},
    {**COMMUN, "page": "cric-hydraulique.html", "tag": "Exercice 1.4", "title": "Cric hydraulique roulant",
     "parts": PARTS_CRIC, "docs": docs_for("Présentation du cric", dp_cric), "vign": "carte-cric-hydraulique.jpg",
     "mots": ["Bielle", "Actions mutuelles", "Deux dynamiques", "Vérin"],
     "alt": "Cric hydraulique roulant",
     "hero": ("g-cric-meca", "Mécanisme du cric : groupe hydraulique, bras, sellette, bielle",
              "Quel effort le vérin fournit-il pour soulever 400 daN ?"),
     "sub": "Un cric soulève une charge de 400 daN. Deux isolements successifs — la sellette puis le bras — et deux "
            "dynamiques sur le même DR conduisent à l'effort du vérin.",
     "desc": "Statique graphique : isolements successifs d'un cric hydraulique, actions mutuelles, deux dynamiques "
             "des forces, effort du vérin."},
    {**COMMUN, "page": "suspension-vtt.html", "tag": "Exercice 1.5", "title": "Suspension arrière de VTT",
     "parts": PARTS_VTT, "docs": docs_for("Présentation de la suspension", dp_vtt), "vign": "carte-suspension-vtt.jpg",
     "mots": ["Haubans", "Basculeur", "Amortisseur", "Dynamique"],
     "alt": "VTT tout suspendu",
     "hero": ("g-vtt-photo", "VTT tout suspendu", "Quel effort l'amortisseur supporte-t-il ?"),
     "sub": "La roue pousse les haubans avec 65 daN. En isolant les haubans puis le basculeur, deux constructions "
            "graphiques donnent l'effort supporté par l'amortisseur.",
     "desc": "Statique graphique : isolements successifs d'une suspension de VTT, actions mutuelles, deux dynamiques, "
             "effort dans l'amortisseur."},
]
