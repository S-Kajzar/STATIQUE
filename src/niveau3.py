#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Niveau 3 de « Statique » : cours 3 (statique analytique, interactif) et exercices 3.1 à 3.3.

Source : séquence « Statique analytique » (rappel du PFS, torseurs des actions mécaniques transmissibles,
problème plan, méthode de résolution ; exercices 1 « porte de coffre-fort », 2 « échelle de pompier » et
3 « cadre de vélo » — les exercices 4 et 5 de la séquence ne sont pas repris).

Chaque exercice est une page autonome construite sur le gabarit (bloc de style, moteur de correction Grading
et moteur applicatif recopiés tels quels ; seules les entrées propres au sujet sont remplacées : DECOR,
DR_NAMES, CONSEIL_MIN et le texte de la fenêtre « Imprimer les DR »). Le cours est une page autonome qui
reprend la charte de l'accueil. Ce module est appelé par src/generer.py.
"""
import base64
import html
import json
import math
import pathlib
import re
import struct

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = ROOT / "src" / "images"

HOUSE = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.3" '
         'stroke-linejoin="round" stroke-linecap="round"><path d="M3 11.5 12 4l9 7.5"/>'
         '<path d="M5.5 9.8V20h4.5v-5.5h4V20h4.5V9.8"/></svg>')


# ============================================================ outils
def png(name):
    data = (IMAGES / f"{name}.png").read_bytes()
    w, h = struct.unpack(">II", data[16:24])
    return "data:image/png;base64," + base64.b64encode(data).decode(), w, h


def esc(s):
    return html.escape(s, quote=True)


def fr(x, d=2):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def frac(a, b):
    return f'<span class="frac"><span>{a}</span><span>{b}</span></span>'


def sqrt(x):
    return f'<span class="sqrt"><span class="radix">√</span><span class="rad">{x}</span></span>'


def eq(s):
    return f'<div class="eq">{s}</div>'


def figure(name, alt, caption, maxw):
    src, w, h = png(name)
    return (f'<figure class="fig" style="max-width:{maxw}px"><img src="{src}" alt="{esc(alt)}" '
            f'width="{w}" height="{h}">' + (f"<figcaption>{caption}</figcaption>" if caption else "") + "</figure>")


def V(lettre, indice=""):
    """Vecteur : lettre surmontée d'une flèche, avec son indice (ex. A1/3)."""
    return f'<span class="vec">{lettre}</span>' + (f"<sub>{indice}</sub>" if indice else "")


def tz(nom, point, rows, base="(x, y, z)"):
    """Torseur écrit en colonnes (résultante | moment) entre accolades."""
    body = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    return (f'<span class="torseur"><span class="tz-n">{{<i>T</i><sub>{nom}</sub>}}<sub>{point}</sub> =</span>'
            f'<span class="tz-b"><table>{body}</table></span><span class="tz-r">({point}, {base[1:]}</span></span>')


def tzp(nom, point, x, y, n):
    """Torseur d'un problème plan (x, y) : composantes X, Y et N ; les autres sont barrées d'un tiret."""
    return tz(nom, point, [(x, "—"), (y, "—"), ("—", n)])


# ============================================================ unités et correcteurs
def unit(label, *accept):
    return {"label": label, "accept": list(accept)}


U = {
    "N": unit("N", "n", "newton", "newtons"),
    "daN": unit("daN", "dan", "decanewton", "decanewtons"),
    "kN": unit("kN", "kn", "kilonewton", "kilonewtons"),
    "mm": unit("mm", "mm", "millimetre", "millimetres"),
    "cm": unit("cm", "cm", "centimetre", "centimetres"),
    "m": unit("m", "m", "metre", "metres"),
    "Nm": unit("N·m", "nm", "newtonmetre", "newtonmetres", "metrenewton"),
    "Nmm": unit("N·mm", "nmm", "newtonmillimetre", "newtonmillimetres"),
    "daNm": unit("daN·m", "danm", "decanewtonmetre", "decanewtonmetres"),
    "daNmm": unit("daN·mm", "danmm"),
    "mm2": unit("mm²", "mm2", "millimetrecarre", "millimetrescarres"),
    "cm2": unit("cm²", "cm2", "centimetrecarre", "centimetrescarres"),
    "MPa": unit("MPa", "mpa", "n/mm2", "nmm-2", "megapascal", "megapascals"),
    "Pa": unit("Pa", "pa", "pascal", "pascals"),
    "bar": unit("bar", "bar", "bars"),
    "deg": unit("°", "°", "deg", "degre", "degres"),
}


def num(value, unit_key=None, absTol=None, relTol=None, variants=()):
    g = {"type": "num", "value": value}
    if absTol is not None:
        g["absTol"] = absTol
    if relTol is not None:
        g["relTol"] = relTol
    if unit_key:
        g["unit"] = U[unit_key]
    if variants:
        g["variants"] = [dict(v, strictUnit=True, unit=U[v.pop("u")]) for v in [dict(x) for x in variants]]
    return g


def var(value, u, absTol=None, relTol=None):
    v = {"value": value, "u": u}
    if absTol is not None:
        v["absTol"] = absTol
    if relTol is not None:
        v["relTol"] = relTol
    return v


def KW(*patterns, forbid=()):
    """Mots clés : chaque motif est une liste de groupes de synonymes, tous requis."""
    return {"type": "kw", "any": [[list(g) for g in p] for p in patterns], "forbid": list(forbid)}


def CODE(equals=(), contains=(), reject=()):
    return {"type": "code", "equals": list(equals), "contains": list(contains), "rejectContains": list(reject)}


def ENTIER(n):
    return num(n, absTol=0)


YES = {"type": "yesno", "value": True}
NO = {"type": "yesno", "value": False}

LIAISON_PIVOT = KW([["pivot"]], forbid=["glissant", "glissiere", "rotule", "spherique"])
LIAISON_ENC = KW([["encastrement"]], [["encastree"]], [["fixe"]], [["complete"]], [["rigide"]],
                 forbid=["pivot", "rotule", "glissiere", "ponctuelle", "lineaire"])
LIAISON_LA = KW([["lineaire"], ["annulaire"]], [["sphere"], ["cylindre"]], forbid=["rectiligne", "plan"])
LIAISON_ROTULE = KW([["rotule"]], [["spherique"]], forbid=["annulaire", "cylindre", "lineaire", "plan", "doigt"])
COMPRIME = KW([["compression"]], [["comprime"]], [["compresse"]], forbid=["traction", "tendu", "tire", "etire"])
SENS_OPPOSES = KW([["contraire"]], [["contraires"]], [["oppose"]], [["opposes"]], [["inverse"]], [["inverses"]],
                  forbid=["meme", "identique", "identiques"])


def POINT(p):
    p = p.lower()
    return CODE(equals=[p, "point" + p, "en" + p, "au" + p, "aupoint" + p, "lepoint" + p, "enpoint" + p, p + "0"])


def DROITE(a, b):
    a, b = a.lower(), b.lower()
    return CODE(contains=[a + b, b + a])


UNITE = "Saisis la valeur <strong>avec son unité</strong> : l'unité vaut la moitié des points de la question."
H_C = "Arrondir au centième. " + UNITE
H_U = "Arrondir à l'unité. " + UNITE
H_D = "Arrondir au dixième. " + UNITE
H_EX = "Valeur exacte. " + UNITE
H_U_SIGNE = "Arrondir à l'unité. Composante algébrique : n'oublie pas le signe. " + UNITE
H_C_SIGNE = "Arrondir au centième. Composante algébrique : n'oublie pas le signe. " + UNITE
H_EX_SIGNE = "Valeur exacte. Moment algébrique : n'oublie pas le signe. " + UNITE
H_ENTIER = "Donne un nombre entier, en chiffres."
H_OUINON = "Commence ta réponse par « oui » ou « non »."
H_MOT = "Réponds par le nom de la liaison (un ou quelques mots)."
H_POINT = "Réponds par le nom du point (une lettre)."
H_DROITE = "Réponds par le nom de la droite, par exemple (MN)."
H_COMP = "Écris le nom de la composante, par exemple X_A."
H_SANS = "Arrondir au centième. Nombre sans unité ; n'oublie pas le signe."


# ============================================================ blocs de contenu
def Q(qid, stem, hint, grader, expected, why):
    return {"kind": "q", "id": qid, "stem": stem, "hint": hint, "grader": grader, "expected": expected, "why": why}


def QBAR(label, docs, ans="ci-dessous"):
    return {"kind": "qbar", "label": label, "docs": docs, "ans": ans}


def SK(sid, label, bg, stem, criteria, side, expl, deps=()):
    return {"kind": "sk", "id": sid, "label": label, "bg": bg, "stem": stem, "criteria": criteria,
            "deps": list(deps), "side": side, "expl": expl}


def data_box(items, cols=False):
    return (f'<div class="data"><p class="data-title">Données</p><ul{" class=\"cols\"" if cols else ""}>' +
            "".join(f"<li>{i}</li>" for i in items) + "</ul></div>")


def label_of(qid):
    p, n = qid[1:].split("_")
    return f"Q{p}.{n}"


# ============================================================ DOCUMENT TECHNIQUE COMMUN
DT_FORMULAIRE = (
    '<div class="doc-text"><h3>Principe fondamental de la statique (PFS)</h3>'
    "<p>Un solide (ou un ensemble de solides) isolé est en équilibre si la somme des torseurs des actions "
    "mécaniques extérieures, écrits <strong>au même point</strong>, est nulle :</p>"
    "<ul><li><strong>théorème de la résultante statique</strong> : Σ <span class=\"vec\">F</span><sub>ext</sub> = "
    "<span class=\"vec\">0</span> ;</li><li><strong>théorème du moment statique</strong> : Σ "
    "<span class=\"vec\">M</span><sub>A</sub>(<span class=\"vec\">F</span><sub>ext</sub>) = <span class=\"vec\">0</span>, "
    "en un point A quelconque.</li></ul>"
    "<p>Dans l'espace : 6 équations. <strong>Problème plan (x, y)</strong> : 3 équations — Σ<i>X</i> = 0, "
    "Σ<i>Y</i> = 0 et Σ<i>N</i> = 0 (moments autour de z).</p>"
    "<h3>Solide soumis à deux forces</h3><p>Il est en équilibre si et seulement si les deux forces ont la "
    "<strong>même droite d'action</strong> (celle qui joint leurs points d'application), la <strong>même "
    "intensité</strong> et des <strong>sens contraires</strong>.</p>"
    "<h3>Moment d'une force dans le plan (x, y)</h3>"
    "<p>Pour une force <span class=\"vec\">F</span> (<i>F</i><sub>x</sub> ; <i>F</i><sub>y</sub>) appliquée en P, "
    "avec <span class=\"vec\">AP</span> (<i>x</i> ; <i>y</i>) :</p>"
    "<p class=\"dt-f\"><i>M</i><sub>A</sub>(<span class=\"vec\">F</span>) = <i>x</i> · <i>F</i><sub>y</sub> − "
    "<i>y</i> · <i>F</i><sub>x</sub></p>"
    "<p>Positif dans le sens trigonométrique (anti-horaire). Autre écriture : ± <i>F</i> × <i>d</i>, avec "
    "<i>d</i> la distance de A à la droite d'action de <span class=\"vec\">F</span>. Une force dont la droite "
    "d'action passe par A a un moment nul en A.</p>"
    "<p><strong>Déplacer un torseur</strong> de A vers B : la résultante ne change pas, le moment devient "
    "<span class=\"vec\">M</span><sub>B</sub> = <span class=\"vec\">M</span><sub>A</sub> + "
    "<span class=\"vec\">BA</span> ∧ <span class=\"vec\">R</span>.</p>"
    "<h3>Torseurs transmissibles dans le plan (x, y)</h3>"
    '<table class="t dt-t"><thead><tr><th>Liaison</th><th>Composantes inconnues</th><th>Inconnues</th></tr></thead><tbody>'
    "<tr><td>Ponctuelle de normale y</td><td><i>Y</i></td><td>1</td></tr>"
    "<tr><td>Linéaire annulaire d'axe y</td><td><i>X</i> (perpendiculaire à l'axe)</td><td>1</td></tr>"
    "<tr><td>Rotule (sphérique)</td><td><i>X</i>, <i>Y</i></td><td>2</td></tr>"
    "<tr><td>Pivot d'axe z</td><td><i>X</i>, <i>Y</i></td><td>2</td></tr>"
    "<tr><td>Glissière d'axe x</td><td><i>Y</i>, <i>N</i></td><td>2</td></tr>"
    "<tr><td>Encastrement</td><td><i>X</i>, <i>Y</i>, <i>N</i></td><td>3</td></tr>"
    "</tbody></table>"
    "<p>Une liaison laisse un mouvement possible ⇒ la composante correspondante du torseur est nulle "
    "(translation libre selon x ⇒ <i>X</i> = 0 ; rotation libre autour de z ⇒ <i>N</i> = 0).</p>"
    "<h3>Méthode</h3><ol><li>Isoler, faire le bilan des actions extérieures (torseurs en leurs points).</li>"
    "<li>Compter : inconnues ≤ équations (3 dans le plan).</li><li>Choisir le point où l'action a le plus "
    "d'inconnues, y écrire tous les moments.</li><li>Écrire les équations, résoudre, donner coordonnées et "
    "normes : ‖<span class=\"vec\">F</span>‖ = " + sqrt("<i>X</i>² + <i>Y</i>²") + ".</li></ol>"
    "<h3>Vérin hydraulique</h3><p><i>F</i> = <i>p</i> × <i>S</i> ; avec <i>F</i> en N et <i>S</i> en mm², "
    "<i>p</i> sort en MPa (N/mm²). 1 MPa = 10 bar.</p></div>")


# ============================================================ EXERCICE 3.1 — PORTE DE COFFRE-FORT
P3_C, P4_C = 1000.0, 3000.0                       # daN
YA_C, XG3_C, XG4_C, YG_C = 2.1, 0.4, 1.28, 1.05   # m, repère (B, x, y)
MP3_C = -XG3_C * P3_C                             # daN·m
MP4_C = -XG4_C * P4_C
XA_C = (MP3_C + MP4_C) / YA_C                     # −2,1·XA + MP3 + MP4 = 0
XB_C = -XA_C
YB_C = P3_C + P4_C
NB_C = math.hypot(XB_C, YB_C)

PARTS_COFFRE = [
    {"num": "1", "minutes": 15, "title": "Analyse du mécanisme : graphe des liaisons",
     "intro": [
         "<p>La porte de coffre-fort ferme la salle des coffres d'une banque. Elle se compose d'une porte "
         "<strong>(4)</strong> articulée sur un bras de manœuvre <strong>(3)</strong>. L'ensemble est articulé sur "
         "deux gonds <strong>(1)</strong> et <strong>(2)</strong> scellés dans le mur <strong>(0)</strong> en A et B.</p>"
         "<p>Avant de calculer, on identifie chaque liaison sur le schéma cinématique (DP1) : c'est elle qui fixera "
         "la forme des torseurs.</p>",
         '<div class="n3-split">' +
         figure("n3-coffre-plan", "Plan de la porte : gonds A en haut et B en bas, bras 3 en bleu, porte 4, poids "
                "P3 de 1 000 daN en G3 et P4 de 3 000 daN en G4 ; cotes 1 050, 1 050, 400 et a = 880 mm",
                "Figure 1 — Porte de coffre-fort (cotes en mm).", 420) +
         figure("n3-coffre-cine", "Schéma cinématique : mur 0, gond 1 en A, gond 2 en B, bras 3, porte 4",
                "Figure 2 — Schéma cinématique.", 230) + "</div>",
     ],
     "blocks": [
         QBAR("Q1.1 – Q1.4", ["DP1", "DT1"]),
         Q("q1_1", "Les gonds (1) et (2) sont scellés dans le mur (0). Quelle liaison existe entre le mur (0) et le "
           "gond (1) ?", H_MOT, LIAISON_ENC, "encastrement (liaison complète, aucun mouvement possible)",
           "<p>« Scellé » signifie que le gond est noyé dans la maçonnerie : aucun mouvement relatif n'est possible "
           "entre (0) et (1). C'est une <strong>liaison encastrement</strong> (0 degré de liberté). Il en va de même "
           "pour le gond (2). Sur le schéma, le trait plein qui relie chaque gond au mur hachuré le traduit.</p>"),
         Q("q1_2", "Sur le schéma cinématique, quelle liaison relie le gond (1) au bras (3) en A ?", H_MOT,
           LIAISON_LA, "liaison linéaire annulaire (sphère-cylindre) d'axe (A, <var>y</var>)",
           "<p>En A, le symbole est une <strong>sphère</strong> (le cercle) prise entre deux traits parallèles "
           "verticaux qui représentent un <strong>cylindre</strong> d'axe vertical : c'est la liaison "
           "<strong>linéaire annulaire</strong> d'axe (A, <var>y</var>).</p><p>Degrés de liberté : la translation "
           "selon <var>y</var> et les trois rotations. Le gond (1) ne peut donc pas porter de charge verticale.</p>"),
         Q("q1_3", "Quelle liaison relie le gond (2) au bras (3) en B ?", H_MOT, LIAISON_ROTULE,
           "liaison rotule (sphérique) de centre B",
           "<p>En B, la sphère est entourée de deux arcs de cercle : c'est le symbole de la <strong>liaison "
           "rotule</strong> (ou sphérique) de centre B. Trois rotations possibles, aucune translation : le gond (2) "
           "transmet une force de direction quelconque passant par B, mais aucun moment.</p>"),
         Q("q1_4", "Quelle liaison relie le bras (3) à la porte (4) ?", H_MOT, LIAISON_PIVOT,
           "liaison pivot d'axe vertical (<var>y</var>)",
           "<p>L'arbre vertical solidaire de (3) tourne dans un palier de (4) muni de deux épaulements qui "
           "interdisent la translation : c'est une <strong>liaison pivot</strong> d'axe vertical. La porte peut "
           "pivoter sur le bras pour s'ajuster contre le chambranle.</p>"),
         QBAR("Q1.5", ["DP1"], ans="sur la figure"),
         SK("sk_q1_5", "Q1.5", "GRAPHE_COFFRE",
            "Compléter le graphe des liaisons : relier les solides deux à deux et nommer chaque liaison (avec son "
            "centre ou son axe).",
            ["Cinq liaisons sont tracées, ni plus ni moins : 0–1, 0–2, 1–3, 2–3 et 3–4.",
             "Les liaisons 0–1 et 0–2 sont nommées « encastrement ».",
             "La liaison 1–3 est nommée « linéaire annulaire d'axe (A, y) ».",
             "La liaison 2–3 est nommée « rotule de centre B ».",
             "La liaison 3–4 est nommée « pivot d'axe y » (vertical)."],
            "<p>Outils : <b>Ligne</b> pour relier deux solides, <b>Texte</b> pour nommer la liaison. Les bulles "
            "représentent les solides ; deux solides sont reliés s'ils sont en contact direct.</p>" +
            figure("n3-coffre-cine", "Schéma cinématique de la porte", "Schéma cinématique (rappel).", 200),
            "<p>Le graphe compte <strong>cinq liaisons</strong>. Les gonds (1) et (2) ne touchent que le mur et le "
            "bras ; la porte (4) ne touche que le bras (3).</p><ul>"
            "<li>0–1 et 0–2 : <strong>encastrements</strong> (gonds scellés) ;</li>"
            "<li>1–3 : <strong>linéaire annulaire d'axe (A, <var>y</var>)</strong> ;</li>"
            "<li>2–3 : <strong>rotule de centre B</strong> ;</li>"
            "<li>3–4 : <strong>pivot d'axe <var>y</var></strong>.</li></ul>"
            "<p>Comme (0), (1) et (2) sont liés rigidement, l'ensemble {0, 1, 2} se comporte comme un seul bâti : "
            "le bras (3) est guidé par une linéaire annulaire en A et une rotule en B, ce qui réalise un pivot "
            "d'axe (AB) — la porte tourne autour de la verticale passant par ses gonds.</p>"),
         QBAR("Q1.6", ["DP1"]),
         Q("q1_6", "On va isoler l'ensemble (3 + 4). L'action de la liaison pivot entre (3) et (4) fera-t-elle "
           "partie du bilan des actions extérieures ?", H_OUINON, NO,
           "non : c'est une action intérieure à l'ensemble isolé",
           "<p>Seules les actions exercées <strong>par l'extérieur</strong> de l'ensemble isolé comptent. La liaison "
           "3–4 relie deux solides de l'ensemble : ses actions (3 → 4 et 4 → 3) sont intérieures, opposées, et "
           "s'annulent dans le PFS. Sur le graphe, on « entoure » 3 et 4 : seules les liaisons qui traversent la "
           "frontière (1–3 et 2–3) et les poids donnent des actions extérieures.</p>"),
     ]},
    {"num": "2", "minutes": 20, "title": "Isolement de l'ensemble (3 + 4) : bilan des actions",
     "intro": [
         "<p>On isole l'ensemble E = {bras (3) + porte (4)}. L'étude est menée dans le plan (<var>x</var>, "
         "<var>y</var>) : chaque torseur se réduit à deux composantes de force <i>X</i>, <i>Y</i> et un moment "
         "<i>N</i> autour de <var>z</var>.</p>",
         data_box(["Repère (B, <var>x</var>, <var>y</var>) : origine B, <var>x</var> horizontal vers la droite, "
                   "<var>y</var> vertical vers le haut.",
                   "A est à la verticale de B : AB = 1 050 + 1 050 mm.",
                   "G3 : 400 mm à droite de l'axe AB, à mi-hauteur ; G4 : 880 mm plus loin, à la même hauteur.",
                   f"{V('P', '3')} = 1 000 daN en G3, {V('P', '4')} = 3 000 daN en G4, verticaux vers le bas.",
                   "Liaisons supposées parfaites (sans frottement)."], cols=True),
     ],
     "blocks": [
         QBAR("Q2.1 – Q2.6", ["DT1"]),
         Q("q2_1", "Combien d'actions mécaniques extérieures s'exercent sur l'ensemble (3 + 4) ?", H_ENTIER, ENTIER(4),
           "4 actions : A<sub>1/3</sub>, B<sub>2/3</sub>, P<sub>3</sub> et P<sub>4</sub>",
           f"<p>Deux actions de liaison — {V('A', '1/3')} (gond 1 en A) et {V('B', '2/3')} (gond 2 en B) — et deux "
           f"actions à distance, les poids {V('P', '3')} et {V('P', '4')}.</p>"),
         Q("q2_2", "Dans le plan (<var>x</var>, <var>y</var>), combien d'inconnues comporte l'action "
           f"{V('A', '1/3')} transmise par la linéaire annulaire d'axe (A, <var>y</var>) ?", H_ENTIER, ENTIER(1),
           "1 inconnue : <i>X</i><sub>A</sub>",
           "<p>La linéaire annulaire d'axe <var>y</var> laisse la translation selon <var>y</var> et toutes les "
           "rotations : <i>Y</i><sub>A</sub> = 0 et les moments sont nuls. Dans le plan, il reste la seule "
           "composante <i>X</i><sub>A</sub>, perpendiculaire à l'axe :</p>" +
           eq(tzp("1→3", "A", "<i>X</i><sub>A</sub>", "0", "0"))),
         Q("q2_3", f"Laquelle des deux composantes de force de {V('A', '1/3')}, <i>X</i><sub>A</sub> ou "
           "<i>Y</i><sub>A</sub>, est nulle ?", H_COMP, CODE(equals=["ya", "ya0", "y", "y0", "yaestnulle"]),
           "<i>Y</i><sub>A</sub> = 0",
           "<p>La translation selon l'axe <var>y</var> de la linéaire annulaire est libre : aucune force ne peut "
           "être transmise dans cette direction, donc <i>Y</i><sub>A</sub> = 0. Conséquence importante : "
           "<strong>tout le poids sera repris par le gond B</strong>.</p>"),
         Q("q2_4", f"Combien d'inconnues comporte l'action {V('B', '2/3')} transmise par la rotule de centre B, "
           "dans le plan ?", H_ENTIER, ENTIER(2), "2 inconnues : <i>X</i><sub>B</sub> et <i>Y</i><sub>B</sub>",
           "<p>La rotule bloque les trois translations et laisse les trois rotations : force quelconque passant "
           "par B, moment nul.</p>" + eq(tzp("2→3", "B", "<i>X</i><sub>B</sub>", "<i>Y</i><sub>B</sub>", "0"))),
         Q("q2_5", "Combien d'inconnues compte au total le problème ?", H_ENTIER, ENTIER(3),
           "3 inconnues : <i>X</i><sub>A</sub>, <i>X</i><sub>B</sub>, <i>Y</i><sub>B</sub>",
           "<p>1 inconnue en A + 2 inconnues en B = <strong>3 inconnues</strong>. Les poids sont entièrement "
           "connus :</p>" + eq(tzp("P3", "G3", "0", "−1 000", "0") + " &nbsp; " +
                               tzp("P4", "G4", "0", "−3 000", "0")) + "<p class=\"small\">(en daN)</p>"),
         Q("q2_6", "Le problème plan est-il résoluble par le PFS ?", H_OUINON, YES,
           "oui : 3 inconnues pour 3 équations",
           "<p>Un problème plan fournit <strong>3 équations</strong> (Σ<i>X</i> = 0, Σ<i>Y</i> = 0, Σ<i>N</i> = 0). "
           "Avec 3 inconnues, le système est <strong>déterminé</strong> : on peut le résoudre.</p>"),
         QBAR("Q2.7 – Q2.9", ["DP1", "DT1"]),
         Q("q2_7", "Quelle est l'ordonnée <i>y</i><sub>A</sub> du point A dans le repère (B, <var>x</var>, "
           "<var>y</var>) ?", H_EX, num(2.1, "m", absTol=0.0005, variants=[var(2100, "mm", absTol=0.5),
                                                                            var(210, "cm", absTol=0.05)]),
           "<i>y</i><sub>A</sub> = 2,1 m (2 100 mm)",
           eq("<i>y</i><sub>A</sub> = 1 050 + 1 050 = <b>2 100 mm = 2,1 m</b>") +
           "<p>A est à la verticale de B : <i>x</i><sub>A</sub> = 0, donc <span class=\"vec\">BA</span> (0 ; 2,1).</p>"),
         Q("q2_8", "Quelle est l'abscisse <i>x</i><sub>G4</sub> du centre de gravité G4 de la porte ?", H_EX,
           num(1.28, "m", absTol=0.0005, variants=[var(1280, "mm", absTol=0.5), var(128, "cm", absTol=0.05)]),
           "<i>x</i><sub>G4</sub> = 1,28 m (1 280 mm)",
           eq("<i>x</i><sub>G4</sub> = 400 + 880 = <b>1 280 mm = 1,28 m</b>") +
           "<p>La cote <i>a</i> = 880 mm part de G3, pas de l'axe AB : il faut lui ajouter les 400 mm.</p>"),
         Q("q2_9", "En quel point vaut-il mieux écrire le théorème du moment statique ?", H_POINT, POINT("B"),
           "au point B",
           "<p>On choisit le point où l'action a <strong>le plus d'inconnues</strong> : B (2 inconnues). Les "
           "moments de <i>X</i><sub>B</sub> et <i>Y</i><sub>B</sub> y sont nuls, et l'équation des moments ne "
           "contient plus que <i>X</i><sub>A</sub> : elle se résout immédiatement.</p>"),
     ]},
    {"num": "3", "minutes": 25, "title": "Application du PFS et résultats",
     "intro": [
         "<p>On écrit tous les torseurs au point B, puis les trois équations du PFS. Convention : moment positif "
         "dans le sens trigonométrique, <i>M</i><sub>B</sub>(<span class=\"vec\">F</span>) = <i>x</i> · "
         "<i>F</i><sub>y</sub> − <i>y</i> · <i>F</i><sub>x</sub>, où (<i>x</i> ; <i>y</i>) sont les coordonnées du "
         "point d'application dans le repère (B, <var>x</var>, <var>y</var>).</p>",
     ],
     "blocks": [
         QBAR("Q3.1 – Q3.3", ["DT1"]),
         Q("q3_1", f"Calculer le moment en B du poids {V('P', '3')}.", H_EX_SIGNE,
           num(MP3_C, "daNm", absTol=0.5, variants=[var(MP3_C * 10, "Nm", absTol=5), var(MP3_C * 1000, "daNmm", absTol=500)]),
           f"<i>M</i><sub>B</sub>({V('P', '3')}) = −400 daN·m",
           eq(f"<i>M</i><sub>B</sub>({V('P', '3')}) = <i>x</i><sub>G3</sub> · (−<i>P</i><sub>3</sub>) − "
              "<i>y</i><sub>G3</sub> · 0 = 0,4 × (−1 000) = <b>−400 daN·m</b>") +
           "<p>Négatif : le poids tend à faire tourner l'ensemble dans le sens horaire autour de B.</p>"),
         Q("q3_2", f"Calculer le moment en B du poids {V('P', '4')}.", H_EX_SIGNE,
           num(MP4_C, "daNm", absTol=0.5, variants=[var(MP4_C * 10, "Nm", absTol=5), var(MP4_C * 1000, "daNmm", absTol=500)]),
           f"<i>M</i><sub>B</sub>({V('P', '4')}) = −3 840 daN·m",
           eq(f"<i>M</i><sub>B</sub>({V('P', '4')}) = 1,28 × (−3 000) = <b>−3 840 daN·m</b>") +
           "<p>La porte, lourde et éloignée de l'axe des gonds, produit presque tout le moment.</p>"),
         Q("q3_3", "Écrire l'équation des moments en B et en déduire <i>X</i><sub>A</sub>.", H_C_SIGNE,
           num(XA_C, "daN", relTol=0.001, variants=[var(XA_C * 10, "N", relTol=0.001), var(XA_C / 100, "kN", relTol=0.001)]),
           f"<i>X</i><sub>A</sub> ≈ {fr(XA_C)} daN",
           f"<p>Moment de {V('A', '1/3')} en B : A(0 ; 2,1) et {V('A', '1/3')} (<i>X</i><sub>A</sub> ; 0), donc "
           "<i>M</i><sub>B</sub> = 0 × 0 − 2,1 × <i>X</i><sub>A</sub> = −2,1 <i>X</i><sub>A</sub>.</p>" +
           eq("Σ<i>N</i><sub>B</sub> = 0 ⇒ −2,1 <i>X</i><sub>A</sub> − 400 − 3 840 = 0") +
           eq("<i>X</i><sub>A</sub> = " + frac("−4 240", "2,1") + f" ≈ <b>{fr(XA_C)} daN</b>") +
           "<p>Le signe moins indique que l'action du gond (1) sur le bras est dirigée vers les <var>x</var> "
           "négatifs : le gond <strong>retient</strong> le haut du bras, que le poids de la porte tend à faire "
           "basculer vers la droite.</p>"),
         QBAR("Q3.4 – Q3.9", ["DT1"]),
         Q("q3_4", "Écrire l'équation de la résultante selon <var>x</var> et en déduire <i>X</i><sub>B</sub>.",
           H_C_SIGNE, num(XB_C, "daN", relTol=0.001, variants=[var(XB_C * 10, "N", relTol=0.001), var(XB_C / 100, "kN", relTol=0.001)]),
           f"<i>X</i><sub>B</sub> ≈ {fr(XB_C)} daN",
           eq("Σ<i>X</i> = 0 ⇒ <i>X</i><sub>A</sub> + <i>X</i><sub>B</sub> = 0 ⇒ <i>X</i><sub>B</sub> = "
              f"−<i>X</i><sub>A</sub> ≈ <b>{fr(XB_C)} daN</b>") +
           "<p>Les deux gonds forment un <strong>couple</strong> de forces horizontales opposées qui équilibre le "
           "couple dû aux poids : le gond du haut tire, celui du bas pousse.</p>"),
         Q("q3_5", "Écrire l'équation de la résultante selon <var>y</var> et en déduire <i>Y</i><sub>B</sub>.",
           H_C_SIGNE, num(YB_C, "daN", absTol=0.006, variants=[var(YB_C * 10, "N", absTol=0.06), var(YB_C / 100, "kN", absTol=0.00006)]),
           "<i>Y</i><sub>B</sub> = 4 000 daN",
           eq("Σ<i>Y</i> = 0 ⇒ 0 + <i>Y</i><sub>B</sub> − 1 000 − 3 000 = 0 ⇒ <i>Y</i><sub>B</sub> = "
              "<b>4 000 daN</b>") +
           "<p><i>Y</i><sub>A</sub> étant nul, le gond B porte <strong>tout le poids</strong> de l'ensemble.</p>"),
         Q("q3_6", f"Donner la norme ‖{V('A', '1/3')}‖.", H_C,
           num(abs(XA_C), "daN", relTol=0.001, variants=[var(abs(XA_C) * 10, "N", relTol=0.001), var(abs(XA_C) / 100, "kN", relTol=0.001)]),
           f"‖{V('A', '1/3')}‖ ≈ {fr(abs(XA_C))} daN",
           f"<p>{V('A', '1/3')} n'a qu'une composante : sa norme est la valeur absolue de <i>X</i><sub>A</sub>, "
           f"soit <b>{fr(abs(XA_C))} daN</b> (une norme est toujours positive).</p>"),
         Q("q3_7", f"Calculer la norme ‖{V('B', '2/3')}‖.", H_D,
           num(NB_C, "daN", relTol=0.001, variants=[var(NB_C * 10, "N", relTol=0.001), var(NB_C / 100, "kN", relTol=0.001)]),
           f"‖{V('B', '2/3')}‖ ≈ {fr(NB_C, 1)} daN",
           eq(f"‖{V('B', '2/3')}‖ = " + sqrt("<i>X</i><sub>B</sub>² + <i>Y</i><sub>B</sub>²") + " = " +
              sqrt(f"{fr(XB_C)}² + 4 000²") + f" ≈ <b>{fr(NB_C, 1)} daN</b>") +
           f"<p>Résultats : {V('A', '1/3')} ({fr(XA_C)} ; 0) daN et {V('B', '2/3')} ({fr(XB_C)} ; 4 000) daN.</p>"),
         Q("q3_8", "Lequel des deux gonds porte le poids de la porte et du bras ?",
           "Réponds par le point (A ou B) ou par le numéro du gond.",
           CODE(equals=["b", "2", "gondb", "gond2", "legondb", "legond2", "enb", "gondenb", "legondenb", "pointb",
                        "gond2enb", "legond2enb", "legondeb", "legondenb", "gondinferieur", "legondinferieur",
                        "gondinferieurb", "legondinferieurb", "legondinferieur2"]),
           "le gond (2), en B",
           "<p><i>Y</i><sub>A</sub> = 0 : seul le gond (2), en B, reprend la charge verticale de 4 000 daN. Le gond "
           "(1), en A, ne fait que retenir le bras horizontalement. C'est pourquoi le gond inférieur est conçu comme "
           "une butée (rotule) et le gond supérieur comme un simple guidage (linéaire annulaire).</p>"),
         Q("q3_9", "On écarte la porte de l'axe des gonds (la cote <i>a</i> augmente), sans changer les poids. "
           "L'intensité de l'action du gond A augmente-t-elle ?", H_OUINON, YES,
           "oui : |<i>X</i><sub>A</sub>| = (0,4 × 1 000 + <i>x</i><sub>G4</sub> × 3 000) / 2,1 croît avec <i>a</i>",
           "<p>L'équation des moments donne |<i>X</i><sub>A</sub>| = (400 + 3 000 · <i>x</i><sub>G4</sub>) / 2,1 : "
           "plus la porte est loin de l'axe, plus son moment est grand, et plus les gonds doivent réagir. "
           "Augmenter l'écart AB entre les gonds réduirait au contraire cet effort.</p>"),
     ]},
]


# ============================================================ EXERCICE 3.2 — ÉCHELLE DE POMPIER
P_E = 5000.0                       # daN
XB_E, YB_E, XG_E = 2.85, 1.65, 6.0  # m, repère (A, x, y)
ALPHA = math.radians(70)
D_E = XB_E * math.sin(ALPHA) + YB_E * math.cos(ALPHA)
MP_E = -XG_E * P_E
F_E = -MP_E / D_E
BX_E, BY_E = -F_E * math.cos(ALPHA), F_E * math.sin(ALPHA)
AX_E, AY_E = -BX_E, P_E - BY_E
NA_E = math.hypot(AX_E, AY_E)
S_E = math.pi * 100 ** 2 / 4
FN_E = F_E * 10
PR_E = FN_E / S_E

PARTS_ECHELLE = [
    {"num": "1", "minutes": 15, "title": "Isolement du vérin (4 + 5)",
     "intro": [
         "<p>Une échelle de pompier <strong>(3)</strong> est articulée en A (pivot d'axe (A, <var>z</var>)) sur une "
         "tourelle <strong>(2)</strong>, qui peut pivoter autour de l'axe (D, <var>y</var>) par rapport au châssis du "
         "camion <strong>(1)</strong>. Le levage est réalisé par un vérin hydraulique <strong>4 + 5</strong> "
         "(4 = tige, 5 = corps) articulé en B sur l'échelle et en C sur la tourelle par deux "
         "<strong>liaisons rotules</strong> de centres B et C.</p><p>L'étude est menée dans le plan (<var>x</var>, "
         f"<var>y</var>) ; l'ensemble est en équilibre. {V('P', '3')} (5 000 daN) schématise le poids de "
         "l'échelle ; le poids du vérin est négligé.</p>",
         figure("n3-echelle", "Échelle 3 articulée en A sur la tourelle 2, vérin 4 + 5 entre B et C incliné de 70°, "
                "échelle inclinée de 30°, poids P3 de 5 000 daN en G3", "Figure 1 — Échelle de pompier.", 440),
     ],
     "blocks": [
         QBAR("Q1.1 – Q1.5", ["DP1", "DT1"]),
         Q("q1_1", "On isole le vérin (4 + 5). À combien d'actions mécaniques extérieures est-il soumis ?",
           H_ENTIER, ENTIER(2), "2 actions : en B (échelle) et en C (tourelle)",
           "<p>Son poids est négligé ; il ne reste que les deux actions des rotules : "
           f"{V('B', '3/4')} exercée par l'échelle sur la tige et {V('C', '2/5')} exercée par la tourelle sur le "
           "corps. Les actions entre tige et corps (et la pression de l'huile) sont <strong>intérieures</strong> au "
           "vérin isolé.</p>"),
         Q("q1_2", "Compléter : un solide soumis à deux forces est en équilibre si ces deux forces ont la même droite "
           "d'action, la même intensité et des sens …", "Réponds en un mot.", SENS_OPPOSES, "contraires (opposés)",
           "<p>C'est le cas particulier du PFS pour <strong>deux forces</strong> : même droite d'action, même "
           "intensité, sens contraires. Leur somme est nulle et leurs moments se compensent en tout point.</p>"),
         Q("q1_3", "En déduire la droite d'action des actions qui s'exercent sur le vérin.", H_DROITE, DROITE("B", "C"),
           "la droite (BC), axe du vérin",
           "<p>Les deux forces passent par leurs points d'application B et C (centres des rotules) et ont la même "
           "droite d'action : c'est la droite <strong>(BC)</strong>, axe du vérin. On connaît donc la "
           f"<strong>direction</strong> de {V('B', '4/3')} avant tout calcul : il ne restera que son intensité à "
           "déterminer.</p>"),
         Q("q1_4", "Quel angle la droite (BC) fait-elle avec l'axe <var>x</var> ?", "Valeur lue sur la figure, en "
           "degrés. " + UNITE, num(70, "deg", absTol=0.5), "70°",
           "<p>Lecture directe sur la figure : la droite (BC) est inclinée de <strong>70°</strong> par rapport à "
           f"l'horizontale. Un vecteur unitaire dirigé de C vers B s'écrit (−cos 70° ; sin 70°) : B est au-dessus "
           "et à gauche de C.</p>"),
         Q("q1_5", "Le vérin est-il comprimé ou tendu ?", "Réponds en un mot.", COMPRIME, "comprimé",
           "<p>Le vérin soutient l'échelle par en dessous : sa tige <strong>pousse</strong> sur l'échelle en B, et "
           "l'échelle repousse la tige. Les deux actions sont dirigées vers l'intérieur du vérin : il travaille en "
           "<strong>compression</strong>. C'est aussi pour cela que l'huile doit être sous pression côté fond du "
           "piston (partie 4).</p>"),
     ]},
    {"num": "2", "minutes": 20, "title": "Isolement de l'échelle (3) : bilan des actions",
     "intro": [
         "<p>On isole l'échelle (3). Les coordonnées sont données dans le repère (A, <var>x</var>, <var>y</var>) "
         "de la figure ci-dessous.</p>",
         '<div class="n3-split">' +
         figure("n3-echelle-iso", "Échelle isolée : A à l'origine, B à 2,85 m en x et 1,65 m en y, droite BC à 70°, "
                "poids P3 de 5 000 daN à 6 m de A", "Figure 2 — Échelle (3) isolée.", 400) +
         data_box(["Repère (A, <var>x</var>, <var>y</var>) : <var>x</var> horizontal, <var>y</var> vertical vers le "
                   "haut.", "B (2,85 ; 1,65) m.", f"{V('P', '3')} = 5 000 daN, vertical vers le bas, sa droite "
                   "d'action est à 6 m de A (<i>x</i> = 6 m).",
                   "Droite (BC) inclinée de 70° sur l'axe <var>x</var>.",
                   "Le vérin pousse : " + V('B', '4/3') + " = <i>F</i> · (−cos 70° ; sin 70°), avec <i>F</i> &gt; 0."]) +
         "</div>",
     ],
     "blocks": [
         QBAR("Q2.1 – Q2.6", ["DT1"]),
         Q("q2_1", "Combien d'actions mécaniques extérieures s'exercent sur l'échelle (3) ?", H_ENTIER, ENTIER(3),
           f"3 actions : {V('A', '2/3')}, {V('B', '4/3')} et {V('P', '3')}",
           f"<p>{V('A', '2/3')} (pivot en A, tourelle), {V('B', '4/3')} (rotule en B, tige du vérin) et le poids "
           f"{V('P', '3')}.</p>"),
         Q("q2_2", "Combien d'inconnues comporte, dans le plan, l'action du pivot d'axe (A, <var>z</var>) ?",
           H_ENTIER, ENTIER(2), "2 inconnues : <i>X</i><sub>A</sub>, <i>Y</i><sub>A</sub>",
           "<p>Le pivot d'axe <var>z</var> laisse seulement la rotation autour de <var>z</var> : <i>N</i><sub>A</sub> "
           "= 0. Dans le plan, il reste deux inconnues :</p>" +
           eq(tzp("2→3", "A", "<i>X</i><sub>A</sub>", "<i>Y</i><sub>A</sub>", "0"))),
         Q("q2_3", f"Combien d'inconnues reste-t-il pour {V('B', '4/3')}, une fois sa direction connue grâce à "
           "l'isolement du vérin ?", H_ENTIER, ENTIER(1), "1 inconnue : l'intensité <i>F</i>",
           "<p>Une rotule transmet a priori deux inconnues (<i>X</i><sub>B</sub>, <i>Y</i><sub>B</sub>), mais la "
           "direction (BC) les lie : <i>X</i><sub>B</sub> = −<i>F</i> cos 70° et <i>Y</i><sub>B</sub> = <i>F</i> "
           "sin 70°. Il ne reste qu'<strong>une</strong> inconnue, <i>F</i>.</p>" +
           eq(tzp("4→3", "B", "−<i>F</i> cos 70°", "<i>F</i> sin 70°", "0"))),
         Q("q2_4", "Avec 3 inconnues au total, le problème plan est-il résoluble ?", H_OUINON, YES,
           "oui : 3 inconnues (<i>X</i><sub>A</sub>, <i>Y</i><sub>A</sub>, <i>F</i>) pour 3 équations",
           "<p>Sans l'isolement préalable du vérin, on aurait 4 inconnues pour 3 équations : le problème serait "
           "insoluble. Isoler d'abord le solide soumis à deux forces est la clé de la résolution.</p>"),
         Q("q2_5", f"Calculer le rapport <i>Y</i><sub>B</sub> / <i>X</i><sub>B</sub> des composantes de "
           f"{V('B', '4/3')}.", H_SANS, num(-math.tan(ALPHA), absTol=0.006), "<i>Y</i><sub>B</sub> / "
           "<i>X</i><sub>B</sub> = −tan 70° ≈ −2,75",
           eq(frac("<i>Y</i><sub>B</sub>", "<i>X</i><sub>B</sub>") + " = " + frac("<i>F</i> sin 70°",
              "−<i>F</i> cos 70°") + " = −tan 70° ≈ <b>−2,75</b>") +
           "<p>La composante verticale est presque trois fois plus grande que l'horizontale : le vérin est proche "
           "de la verticale.</p>"),
         Q("q2_6", "En quel point faut-il écrire l'équation des moments pour obtenir directement <i>F</i> ?",
           H_POINT, POINT("A"), "au point A",
           "<p>En A, l'action du pivot (2 inconnues) a un moment nul : l'équation des moments ne contient plus que "
           "<i>F</i>.</p>"),
     ]},
    {"num": "3", "minutes": 25, "title": "PFS appliqué à l'échelle",
     "intro": ["<p>Convention : moment positif dans le sens trigonométrique, <i>M</i><sub>A</sub>(<span "
               "class=\"vec\">F</span>) = <i>x</i> · <i>F</i><sub>y</sub> − <i>y</i> · <i>F</i><sub>x</sub>.</p>"],
     "blocks": [
         QBAR("Q3.1 – Q3.3", ["DT1"]),
         Q("q3_1", f"Calculer le moment en A du poids {V('P', '3')}.", H_EX_SIGNE,
           num(MP_E, "daNm", absTol=0.5, variants=[var(MP_E * 10, "Nm", absTol=5), var(MP_E / 100, "kN", absTol=0.005)]),
           f"<i>M</i><sub>A</sub>({V('P', '3')}) = −30 000 daN·m",
           eq(f"<i>M</i><sub>A</sub>({V('P', '3')}) = 6 × (−5 000) = <b>−30 000 daN·m</b>") +
           "<p>Seule l'abscisse de G3 compte pour une force verticale : sa hauteur n'intervient pas.</p>"),
         Q("q3_2", f"Le moment de {V('B', '4/3')} en A s'écrit <i>M</i><sub>A</sub> = 2,85 · <i>F</i> sin 70° − "
           "1,65 · (−<i>F</i> cos 70°) = <i>F</i> · <i>d</i>. Calculer <i>d</i>.", H_C,
           num(D_E, "m", absTol=0.006, variants=[var(D_E * 1000, "mm", absTol=6)]),
           f"<i>d</i> ≈ {fr(D_E)} m",
           eq(f"<i>d</i> = 2,85 × sin 70° + 1,65 × cos 70° = 2,678 + 0,564 ≈ <b>{fr(D_E)} m</b>") +
           "<p><i>d</i> est la <strong>distance du point A à la droite (BC)</strong> : le bras de levier du vérin. "
           "Plus le vérin est ancré loin de l'articulation A, plus il est efficace.</p>"),
         Q("q3_3", f"Écrire l'équation des moments en A et en déduire l'intensité <i>F</i> = ‖{V('B', '4/3')}‖.", H_U,
           num(F_E, "daN", relTol=0.002, variants=[var(FN_E, "N", relTol=0.002), var(FN_E / 1000, "kN", relTol=0.002)]),
           f"<i>F</i> ≈ {fr(F_E, 0)} daN",
           eq("Σ<i>N</i><sub>A</sub> = 0 ⇒ <i>F</i> · <i>d</i> − 30 000 = 0 ⇒ <i>F</i> = " + frac("30 000", fr(D_E, 3)) +
              f" ≈ <b>{fr(F_E, 0)} daN</b>") +
           "<p>Le vérin pousse avec près de deux fois le poids de l'échelle : son bras de levier (3,24 m) est bien plus "
           "court que celui du poids (6 m).</p>"),
         QBAR("Q3.4 – Q3.8", ["DT1"]),
         Q("q3_4", "En déduire <i>X</i><sub>B</sub>.", H_U_SIGNE,
           num(BX_E, "daN", relTol=0.003, variants=[var(BX_E * 10, "N", relTol=0.003)]),
           f"<i>X</i><sub>B</sub> ≈ {fr(BX_E, 0)} daN",
           eq(f"<i>X</i><sub>B</sub> = −<i>F</i> cos 70° = −{fr(F_E, 0)} × 0,342 ≈ <b>{fr(BX_E, 0)} daN</b>")),
         Q("q3_5", "En déduire <i>Y</i><sub>B</sub>.", H_U_SIGNE,
           num(BY_E, "daN", relTol=0.002, variants=[var(BY_E * 10, "N", relTol=0.002)]),
           f"<i>Y</i><sub>B</sub> ≈ {fr(BY_E, 0)} daN",
           eq(f"<i>Y</i><sub>B</sub> = <i>F</i> sin 70° = {fr(F_E, 0)} × 0,940 ≈ <b>{fr(BY_E, 0)} daN</b>")),
         Q("q3_6", "Écrire l'équation de la résultante selon <var>x</var> et en déduire <i>X</i><sub>A</sub>.",
           H_U_SIGNE, num(AX_E, "daN", relTol=0.003, variants=[var(AX_E * 10, "N", relTol=0.003)]),
           f"<i>X</i><sub>A</sub> ≈ {fr(AX_E, 0)} daN",
           eq(f"Σ<i>X</i> = 0 ⇒ <i>X</i><sub>A</sub> + <i>X</i><sub>B</sub> = 0 ⇒ <i>X</i><sub>A</sub> ≈ "
              f"<b>{fr(AX_E, 0)} daN</b>")),
         Q("q3_7", "Écrire l'équation de la résultante selon <var>y</var> et en déduire <i>Y</i><sub>A</sub>.",
           H_U_SIGNE, num(AY_E, "daN", relTol=0.003, variants=[var(AY_E * 10, "N", relTol=0.003)]),
           f"<i>Y</i><sub>A</sub> ≈ {fr(AY_E, 0)} daN",
           eq(f"Σ<i>Y</i> = 0 ⇒ <i>Y</i><sub>A</sub> + <i>Y</i><sub>B</sub> − 5 000 = 0 ⇒ <i>Y</i><sub>A</sub> = "
              f"5 000 − {fr(BY_E, 0)} ≈ <b>{fr(AY_E, 0)} daN</b>") +
           "<p>Négatif : la tourelle <strong>retient</strong> l'échelle vers le bas en A. Le vérin pousse plus fort "
           "que le poids ; l'articulation A empêche l'échelle de se soulever.</p>"),
         Q("q3_8", f"Calculer la norme ‖{V('A', '2/3')}‖.", H_U,
           num(NA_E, "daN", relTol=0.003, variants=[var(NA_E * 10, "N", relTol=0.003)]),
           f"‖{V('A', '2/3')}‖ ≈ {fr(NA_E, 0)} daN",
           eq(f"‖{V('A', '2/3')}‖ = " + sqrt(f"{fr(AX_E, 0)}² + ({fr(AY_E, 0)})²") + f" ≈ <b>{fr(NA_E, 0)} daN</b>") +
           f"<p>Bilan : {V('A', '2/3')} ({fr(AX_E, 0)} ; {fr(AY_E, 0)}) daN, {V('B', '4/3')} ({fr(BX_E, 0)} ; "
           f"{fr(BY_E, 0)}) daN, d'intensité {fr(F_E, 0)} daN.</p>"),
     ]},
    {"num": "4", "minutes": 15, "title": "Pression d'alimentation du vérin",
     "intro": ["<p>Le diamètre du piston du vérin est de 100 mm. L'huile agit sur toute la surface du piston "
               "(côté fond) pour pousser la tige.</p>"],
     "blocks": [
         QBAR("Q4.1 – Q4.5", ["DT1"]),
         Q("q4_1", "Calculer la surface <i>S</i> du piston.", H_C,
           num(S_E, "mm2", relTol=0.001, variants=[var(S_E / 100, "cm2", relTol=0.001)]),
           f"<i>S</i> ≈ {fr(S_E)} mm²",
           eq("<i>S</i> = " + frac("π · <i>D</i>²", "4") + " = " + frac("π × 100²", "4") + f" ≈ <b>{fr(S_E)} mm²</b>")),
         Q("q4_2", "Convertir l'effort <i>F</i> du vérin en newtons.", H_U,
           num(FN_E, "N", relTol=0.002, variants=[var(F_E, "daN", relTol=0.002), var(FN_E / 1000, "kN", relTol=0.002)]),
           f"<i>F</i> ≈ {fr(FN_E, 0)} N",
           eq(f"1 daN = 10 N ⇒ <i>F</i> ≈ {fr(F_E, 0)} × 10 ≈ <b>{fr(FN_E, 0)} N</b>") +
           "<p>Indispensable pour obtenir la pression en MPa avec une surface en mm².</p>"),
         Q("q4_3", "Calculer la pression d'alimentation <i>p</i> nécessaire.", H_C,
           num(PR_E, "MPa", relTol=0.003, variants=[var(PR_E * 10, "bar", relTol=0.003), var(PR_E * 1e6, "Pa", relTol=0.003)]),
           f"<i>p</i> ≈ {fr(PR_E)} MPa",
           eq("<i>p</i> = " + frac("<i>F</i>", "<i>S</i>") + " = " + frac(fr(FN_E, 0), fr(S_E)) +
              f" ≈ <b>{fr(PR_E)} MPa</b>") + "<p>N / mm² = MPa.</p>"),
         Q("q4_4", "Exprimer cette pression en bar.", H_D,
           num(PR_E * 10, "bar", relTol=0.003, variants=[var(PR_E, "MPa", relTol=0.003)]),
           f"<i>p</i> ≈ {fr(PR_E * 10, 1)} bar",
           eq(f"1 MPa = 10 bar ⇒ <i>p</i> ≈ <b>{fr(PR_E * 10, 1)} bar</b>") +
           "<p>Une pression courante pour un circuit hydraulique mobile (souvent 150 à 250 bar).</p>"),
         Q("q4_5", "Un équipement plus lourd est ajouté en bout d'échelle : G3 s'éloigne de A. La pression "
           "nécessaire augmente-t-elle ?", H_OUINON, YES, "oui : <i>F</i> = <i>P</i><sub>3</sub> · <i>x</i><sub>G3</sub> / <i>d</i> augmente",
           "<p>L'équation des moments donne <i>F</i> = <i>P</i><sub>3</sub> · <i>x</i><sub>G3</sub> / <i>d</i>. Le "
           "moment du poids augmente, le bras de levier <i>d</i> du vérin ne change pas : <i>F</i>, donc "
           "<i>p</i> = <i>F</i> / <i>S</i>, augmente.</p>"),
     ]},
]


# ============================================================ EXERCICE 3.3 — CADRE DE VÉLO
P_V = 1000.0                     # N
XD_V, XA_V, XB_V = 242.0, 430.0, 1102.0   # mm, repère (C, x, y)
BETA = math.radians(35.5)
XE_V = 393.0
YE_V = XE_V * math.tan(BETA)
MP_V = -XD_V * P_V               # N·mm
B_V = -MP_V / XB_V
C_V = P_V - B_V
MC_V = -XA_V * C_V               # moment en A de l'action en C, N·mm
D_V = XA_V * math.sin(BETA)
E_V = -MC_V / D_V
AX_V = E_V * math.cos(BETA)
AY_V = C_V - E_V * math.sin(BETA)

PARTS_VELO = [
    {"num": "1", "minutes": 15, "title": "Graphe des liaisons",
     "intro": [
         "<p>Le cadre d'un vélo tout terrain est réalisé en deux parties <strong>(1)</strong> (cadre avant) et "
         "<strong>(2)</strong> (bras oscillant arrière), articulées en A par une liaison pivot d'axe (A, "
         "<var>z</var>). Un amortisseur <strong>(3)</strong> relie les deux parties : il est articulé en E sur (2) et "
         f"en F sur (1). Le poids {V('P')} = 1 000 N du cycliste, vertical, est supposé entièrement appliqué en D. "
         f"{V('B')} et {V('C')} sont les actions des roues avant et arrière sur le cadre ; les autres poids et "
         "actions du cycliste (guidon, pédales) sont négligés.</p>",
         figure("n3-velo-cadre", "Cadre de VTT : cadre avant 1, bras arrière 2, amortisseur 3 entre E et F ; poids "
                "P de 1 000 N en D, actions verticales B et C des roues ; cotes 242, 188 et 672 mm ; droite CEF à "
                "35,5°", "Figure 1 — Cadre de vélo tout terrain (cotes en mm).", 760),
     ],
     "blocks": [
         QBAR("Q1.1 – Q1.2", ["DP1", "DT1"]),
         Q("q1_1", "Quelle liaison relie le cadre avant (1) au bras arrière (2) en A ?", H_MOT, LIAISON_PIVOT,
           "liaison pivot d'axe (A, <var>z</var>)",
           "<p>L'énoncé le précise : le bras arrière oscille autour d'un axe perpendiculaire au plan du vélo, en A. "
           "Un seul mouvement possible, la rotation autour de <var>z</var> : <strong>liaison pivot</strong>.</p>"),
         Q("q1_2", "L'amortisseur (3) est articulé en E sur (2) et en F sur (1). Dans le plan, quelle liaison "
           "modélise chacune de ces articulations ?", H_MOT,
           KW([["pivot"]], [["rotule"]], [["spherique"]], [["articulation"]], forbid=["glissant", "glissiere", "encastrement"]),
           "liaison pivot d'axe (E, <var>z</var>) et pivot d'axe (F, <var>z</var>) (une rotule est aussi acceptée)",
           "<p>Les œillets de l'amortisseur tournent autour d'axes parallèles à <var>z</var> : <strong>pivots</strong> "
           "d'axes (E, <var>z</var>) et (F, <var>z</var>). Des rotules (silentblocs) conduiraient au même modèle "
           "dans le plan : une force passant par le centre, sans moment.</p>"),
         QBAR("Q1.3", ["DP1"], ans="sur la figure"),
         SK("sk_q1_3", "Q1.3", "GRAPHE_VELO",
            "Compléter le graphe des liaisons des solides (1), (2) et (3). Les actions extérieures (cycliste, roues) "
            "sont déjà placées.",
            ["Trois liaisons sont tracées : 1–2, 2–3 et 3–1 (le graphe forme une boucle fermée).",
             "La liaison 1–2 est nommée « pivot d'axe (A, z) ».",
             "La liaison 2–3 est nommée « pivot (ou rotule) en E ».",
             "La liaison 3–1 est nommée « pivot (ou rotule) en F »."],
            "<p>Outils : <b>Ligne</b> pour relier deux solides, <b>Texte</b> pour nommer la liaison et son centre. "
            "L'amortisseur (3) est considéré comme un seul solide.</p>" +
            figure("n3-velo-amortisseur", "Amortisseur 3 articulé en E et F, incliné de 35,5°", "L'amortisseur (3).", 200),
            "<p>Trois liaisons, qui forment une <strong>boucle fermée</strong> 1 → 2 → 3 → 1 :</p><ul>"
            "<li>1–2 : <strong>pivot d'axe (A, <var>z</var>)</strong> ;</li>"
            "<li>2–3 : <strong>pivot d'axe (E, <var>z</var>)</strong> ;</li>"
            "<li>3–1 : <strong>pivot d'axe (F, <var>z</var>)</strong>.</li></ul>"
            "<p>Les actions extérieures s'appliquent sur (1) (cycliste en D, roue avant en B) et sur (2) (roue arrière "
            "en C). C'est l'amortisseur, en se comprimant, qui laisse osciller le bras arrière autour de A.</p>"),
     ]},
    {"num": "2", "minutes": 20, "title": "Isolement du cadre complet (1 + 2 + 3)",
     "intro": [
         "<p>On isole l'ensemble du cadre {1 + 2 + 3}. Repère (C, <var>x</var>, <var>y</var>) : origine C (contact de "
         "la roue arrière), <var>x</var> horizontal vers l'avant, <var>y</var> vertical vers le haut.</p>",
         data_box(["C, A et B sont sur l'axe <var>x</var> : CA = 242 + 188 mm, AB = 672 mm.",
                   f"{V('P')} = 1 000 N, vertical vers le bas, appliqué en D, à 242 mm de C selon <var>x</var>.",
                   f"{V('B')} et {V('C')} sont verticales (vers le haut).",
                   "Convention : moment positif dans le sens trigonométrique, <i>M</i><sub>C</sub> = <i>x</i> · "
                   "<i>F</i><sub>y</sub> − <i>y</i> · <i>F</i><sub>x</sub>."], cols=True),
     ],
     "blocks": [
         QBAR("Q2.1 – Q2.6", ["DP1", "DT1"]),
         Q("q2_1", "Combien d'actions mécaniques extérieures s'exercent sur le cadre complet ?", H_ENTIER, ENTIER(3),
           f"3 actions : {V('P')}, {V('B')} et {V('C')}",
           f"<p>Le poids du cycliste {V('P')} et les actions des deux roues {V('B')} et {V('C')}. Toutes trois sont "
           "verticales : le cadre est soumis à trois <strong>forces parallèles</strong>.</p>"),
         Q("q2_2", "Les actions de l'amortisseur (3) sur les cadres (1) et (2) interviennent-elles dans ce bilan ?",
           H_OUINON, NO, "non : elles sont intérieures à l'ensemble isolé",
           "<p>L'amortisseur fait partie de l'ensemble isolé : ses actions sur (1) et (2) sont intérieures, comme "
           "celles du pivot A. C'est tout l'intérêt de cet isolement : il donne B et C sans rien connaître de la "
           "suspension.</p>"),
         Q("q2_3", "Quelle est l'abscisse <i>x</i><sub>B</sub> du point B ?", H_EX,
           num(XB_V, "mm", absTol=0.5, variants=[var(XB_V / 1000, "m", absTol=0.0005), var(XB_V / 10, "cm", absTol=0.05)]),
           "<i>x</i><sub>B</sub> = 1 102 mm",
           eq("<i>x</i><sub>B</sub> = 242 + 188 + 672 = <b>1 102 mm</b>")),
         Q("q2_4", f"Calculer le moment en C du poids {V('P')}.", H_EX_SIGNE,
           num(MP_V, "Nmm", absTol=0.5, variants=[var(MP_V / 1000, "Nm", absTol=0.0005)]),
           f"<i>M</i><sub>C</sub>({V('P')}) = −242 000 N·mm = −242 N·m",
           eq(f"<i>M</i><sub>C</sub>({V('P')}) = 242 × (−1 000) = <b>−242 000 N·mm</b> = −242 N·m")),
         Q("q2_5", f"Écrire l'équation des moments en C et en déduire l'intensité de {V('B')}.", H_C,
           num(B_V, "N", absTol=0.006, variants=[var(B_V / 10, "daN", absTol=0.0006)]),
           f"<i>B</i> ≈ {fr(B_V)} N",
           eq("Σ<i>N</i><sub>C</sub> = 0 ⇒ 1 102 · <i>B</i> − 242 000 = 0 ⇒ <i>B</i> = " + frac("242 000", "1 102") +
              f" ≈ <b>{fr(B_V)} N</b>") +
           f"<p>{V('C')} passe par C : son moment y est nul. On a écrit les moments au point qui élimine une "
           "inconnue.</p>"),
         Q("q2_6", f"En déduire l'intensité de {V('C')}.", H_C,
           num(C_V, "N", absTol=0.006, variants=[var(C_V / 10, "daN", absTol=0.0006)]),
           f"<i>C</i> ≈ {fr(C_V)} N",
           eq(f"Σ<i>Y</i> = 0 ⇒ <i>B</i> + <i>C</i> − 1 000 = 0 ⇒ <i>C</i> = 1 000 − {fr(B_V)} ≈ <b>{fr(C_V)} N</b>") +
           "<p>La roue arrière porte 78 % du poids : la selle D est bien plus proche de C que de B.</p>"),
     ]},
    {"num": "3", "minutes": 10, "title": "Isolement de l'amortisseur (3)",
     "intro": ["<p>On isole l'amortisseur (3), dont le poids est négligé. C, E et F sont alignés ; la droite (CEF) "
               "fait 35,5° avec l'axe <var>x</var>.</p>",
               figure("n3-velo-amortisseur", "Amortisseur 3 entre E et F, incliné de 35,5° sur l'horizontale",
                      "Figure 2 — Amortisseur (3).", 240)],
     "blocks": [
         QBAR("Q3.1 – Q3.4", ["DP1", "DT1"]),
         Q("q3_1", "À combien d'actions mécaniques extérieures l'amortisseur est-il soumis ?", H_ENTIER, ENTIER(2),
           "2 actions : en E (cadre 2) et en F (cadre 1)",
           f"<p>{V('E', '2/3')} et {V('F', '1/3')}, exercées par les articulations ; aucune autre action.</p>"),
         Q("q3_2", "En déduire la droite d'action de l'action mécanique en E.", H_DROITE, DROITE("E", "F"),
           "la droite (EF), axe de l'amortisseur",
           "<p>Solide soumis à deux forces : elles sont portées par la droite qui joint leurs points d'application, "
           "<strong>(EF)</strong>, avec même intensité et sens contraires.</p>"),
         Q("q3_3", "Cette droite passe par un autre point remarquable du vélo. Lequel ?", H_POINT, POINT("C"), "le point C",
           "<p>La figure l'indique : <strong>C, E et F sont alignés</strong>. La droite d'action de l'amortisseur "
           "passe par C, le contact de la roue arrière. Cette remarque va beaucoup simplifier le calcul suivant.</p>"),
         Q("q3_4", "Sous le poids du cycliste, l'amortisseur est-il comprimé ?", H_OUINON, YES,
           "oui : il est comprimé",
           "<p>La roue arrière pousse le bras (2) vers le haut ; le bras tourne autour de A et rapproche E de F : "
           "l'amortisseur est <strong>comprimé</strong>. Le calcul de la partie 4 le confirmera (intensité positive "
           "dans le sens choisi).</p>"),
     ]},
    {"num": "4", "minutes": 25, "title": "Isolement du bras arrière (2)",
     "intro": [
         "<p>On isole le bras arrière (2). Repère (C, <var>x</var>, <var>y</var>).</p>",
         '<div class="n3-split">' +
         figure("n3-velo-arriere", "Bras arrière 2 isolé : C, A à 430 mm sur l'axe x, E à 393 mm de C en x, sur la "
                "droite CEF à 35,5°", "Figure 3 — Bras arrière (2) isolé.", 340) +
         data_box([f"{V('C')} : vertical vers le haut, intensité trouvée en Q2.6.",
                   "A (430 ; 0) mm ; E (393 ; <i>y</i><sub>E</sub>) mm, sur la droite (CE) inclinée de 35,5°.",
                   f"L'amortisseur comprimé pousse le bras : {V('E', '3/2')} = <i>E</i> · (−cos 35,5° ; −sin 35,5°), "
                   "dirigée de F vers C, avec <i>E</i> &gt; 0.",
                   f"{V('A', '1/2')} (<i>X</i><sub>A</sub> ; <i>Y</i><sub>A</sub>)."]) + "</div>",
     ],
     "blocks": [
         QBAR("Q4.1 – Q4.4", ["DT1"]),
         Q("q4_1", "Combien d'inconnues compte le problème, en tenant compte de la direction connue de l'action en E ?",
           H_ENTIER, ENTIER(3), "3 inconnues : <i>X</i><sub>A</sub>, <i>Y</i><sub>A</sub> et <i>E</i>",
           "<p>2 inconnues au pivot A, 1 inconnue (l'intensité) en E ; " + V('C') + " est connue. 3 inconnues pour 3 "
           "équations : le problème est résoluble.</p>" +
           eq(tzp("1→2", "A", "<i>X</i><sub>A</sub>", "<i>Y</i><sub>A</sub>", "0") + " &nbsp; " +
              tzp("3→2", "E", "−<i>E</i> cos 35,5°", "−<i>E</i> sin 35,5°", "0"))),
         Q("q4_2", "Calculer l'ordonnée <i>y</i><sub>E</sub> du point E.", H_C,
           num(YE_V, "mm", absTol=0.02, variants=[var(YE_V / 1000, "m", absTol=0.00002)]),
           f"<i>y</i><sub>E</sub> ≈ {fr(YE_V)} mm",
           eq(f"<i>y</i><sub>E</sub> = 393 × tan 35,5° ≈ <b>{fr(YE_V)} mm</b>")),
         Q("q4_3", f"Calculer le moment en A de l'action {V('C')}.", H_U_SIGNE,
           num(MC_V, "Nmm", relTol=0.001, variants=[var(MC_V / 1000, "Nm", relTol=0.001)]),
           f"<i>M</i><sub>A</sub>({V('C')}) ≈ {fr(MC_V, 0)} N·mm",
           f"<p>C est à 430 mm à gauche de A : <span class=\"vec\">AC</span> (−430 ; 0) et {V('C')} (0 ; {fr(C_V)}).</p>" +
           eq(f"<i>M</i><sub>A</sub>({V('C')}) = −430 × {fr(C_V)} ≈ <b>{fr(MC_V, 0)} N·mm</b>")),
         Q("q4_4", f"La droite d'action de {V('E', '3/2')} passe par C. En déduire la distance <i>d</i> du point A à "
           "cette droite.", H_C, num(D_V, "mm", absTol=0.02, variants=[var(D_V / 1000, "m", absTol=0.00002)]),
           f"<i>d</i> ≈ {fr(D_V)} mm",
           eq(f"<i>d</i> = AC · sin 35,5° = 430 × sin 35,5° ≈ <b>{fr(D_V)} mm</b>") +
           "<p>Le triangle formé par A, C et le pied de la perpendiculaire est rectangle : la droite fait 35,5° avec "
           "(CA).</p>"),
         QBAR("Q4.5 – Q4.8", ["DT1"]),
         Q("q4_5", "Écrire l'équation des moments en A et en déduire l'effort de compression <i>E</i> dans "
           "l'amortisseur.", H_D, num(E_V, "N", relTol=0.002, variants=[var(E_V / 10, "daN", relTol=0.002)]),
           f"<i>E</i> ≈ {fr(E_V, 1)} N",
           "<p>Le moment de " + V('E', '3/2') + " en A vaut +<i>E</i> · <i>d</i> (il fait tourner le bras dans le "
           "sens trigonométrique, à l'inverse de " + V('C') + ").</p>" +
           eq("Σ<i>N</i><sub>A</sub> = 0 ⇒ <i>E</i> · <i>d</i> − 430 · <i>C</i> = 0 ⇒ <i>E</i> = " +
              frac("<i>C</i>", "sin 35,5°") + " = " + frac(fr(C_V), "0,5807") + f" ≈ <b>{fr(E_V, 1)} N</b>") +
           "<p>L'amortisseur est comprimé par une force supérieure au poids du cycliste.</p>"),
         Q("q4_6", "En déduire <i>X</i><sub>A</sub>.", H_D.replace("Arrondir au dixième.", "Arrondir au dixième. Composante "
           "algébrique : n'oublie pas le signe."),
           num(AX_V, "N", relTol=0.002, variants=[var(AX_V / 10, "daN", relTol=0.002)]),
           f"<i>X</i><sub>A</sub> ≈ {fr(AX_V, 1)} N",
           eq(f"Σ<i>X</i> = 0 ⇒ <i>X</i><sub>A</sub> − <i>E</i> cos 35,5° = 0 ⇒ <i>X</i><sub>A</sub> = "
              f"{fr(E_V, 1)} × 0,8141 ≈ <b>{fr(AX_V, 1)} N</b>")),
         Q("q4_7", "En déduire <i>Y</i><sub>A</sub>.", "Composante algébrique : n'oublie pas le signe. " + UNITE,
           num(0.0, "N", absTol=1.0, variants=[var(0.0, "daN", absTol=0.1)]),
           "<i>Y</i><sub>A</sub> = 0 N",
           eq(f"Σ<i>Y</i> = 0 ⇒ <i>Y</i><sub>A</sub> + <i>C</i> − <i>E</i> sin 35,5° = 0 ⇒ <i>Y</i><sub>A</sub> = "
              f"{fr(C_V)} − {fr(C_V)} = <b>0</b>") +
           "<p>Ce n'est pas un hasard : <i>E</i> sin 35,5° = <i>C</i> exactement (question Q4.5).</p>"),
         Q("q4_8", f"L'action {V('A', '1/2')} est-elle portée par la droite (AC) ?", H_OUINON, YES,
           "oui : les trois forces sont concourantes en C",
           "<p>Le bras (2) est soumis à <strong>trois forces non parallèles</strong> : elles sont "
           f"<strong>concourantes</strong>. {V('C')} et {V('E', '3/2')} passent toutes deux par C, donc "
           f"{V('A', '1/2')} passe aussi par C : elle est portée par (AC), horizontale. D'où <i>Y</i><sub>A</sub> = 0 "
           "et <i>X</i><sub>A</sub> = <i>C</i> / tan 35,5°. Le théorème des trois forces permet de vérifier le "
           "résultat analytique.</p>"),
     ]},
]


# ============================================================ tracés : fonds et décor
SK_BG = {"GRAPHE_COFFRE": "n3-graphe-coffre", "GRAPHE_VELO": "n3-graphe-velo"}

DECOR_HELPERS = r"""  // bulle d'un solide du graphe des liaisons (ellipse de 48 × 32 px)
  function bulle(c, x, y, num, nom) {
    c.save(); c.fillStyle = "#FFF3C4"; c.strokeStyle = "#1C2530"; c.lineWidth = 2.5;
    c.beginPath(); c.ellipse(x, y, 48, 32, 0, 0, Math.PI * 2); c.fill(); c.stroke(); c.restore();
    text(c, num, x, y - 7, "#1C2530", 24, "center", "800");
    text(c, nom, x, y + 15, "#46525C", 12, "center", "600");
  }
  // liaison du graphe : segment entre les bords de deux bulles
  function lien(c, a, b, color) {
    var dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L;
    var r = 1 / Math.sqrt(Math.pow(ux / 48, 2) + Math.pow(uy / 32, 2));
    line(c, a[0] + ux * r, a[1] + uy * r, b[0] - ux * r, b[1] - uy * r, color, 3.4);
  }
"""

DECOR = {
    "GRAPHE_COFFRE": r"""    GRAPHE_COFFRE: {
      pad: { t: 10, r: 10, b: 10, l: 10 }, rs: 2.4,
      decorate: function (c) {
        bulle(c, 90, 200, "0", "mur"); bulle(c, 290, 75, "1", "gond"); bulle(c, 290, 325, "2", "gond");
        bulle(c, 480, 200, "3", "bras"); bulle(c, 670, 200, "4", "porte");
      },
      correction: function (c) {
        var P = { 0: [90, 200], 1: [290, 75], 2: [290, 325], 3: [480, 200], 4: [670, 200] };
        lien(c, P[0], P[1], CORR); lien(c, P[0], P[2], CORR); lien(c, P[1], P[3], CORR);
        lien(c, P[2], P[3], CORR); lien(c, P[3], P[4], CORR);
        text(c, "Encastrement", 172, 112, CORR, 15, "center", "700");
        text(c, "Encastrement", 172, 290, CORR, 15, "center", "700");
        text(c, "Linéaire annulaire", 392, 102, CORR, 15, "left", "700");
        text(c, "d'axe (A, y)", 392, 121, CORR, 15, "left", "700");
        text(c, "Rotule", 392, 290, CORR, 15, "left", "700");
        text(c, "de centre B", 392, 309, CORR, 15, "left", "700");
        text(c, "Pivot", 575, 168, CORR, 15, "center", "700");
        text(c, "d'axe y", 575, 232, CORR, 15, "center", "700");
      }
    }""",
    "GRAPHE_VELO": r"""    GRAPHE_VELO: {
      pad: { t: 10, r: 10, b: 10, l: 10 }, rs: 2.4,
      decorate: function (c) {
        bulle(c, 200, 200, "1", "cadre avant"); bulle(c, 560, 320, "2", "bras arrière");
        bulle(c, 560, 80, "3", "amortisseur");
        arrow(c, 70, 50, 160, 172, "#46525C", 2.2); text(c, "Cycliste : P en D", 20, 34, "#46525C", 14, "left", "700");
        arrow(c, 60, 340, 158, 222, "#46525C", 2.2); text(c, "Roue avant : B", 20, 358, "#46525C", 14, "left", "700");
        arrow(c, 730, 250, 606, 306, "#46525C", 2.2); text(c, "Roue arrière : C", 745, 236, "#46525C", 14, "right", "700");
      },
      correction: function (c) {
        var P = { 1: [200, 200], 2: [560, 320], 3: [560, 80] };
        lien(c, P[1], P[2], CORR); lien(c, P[2], P[3], CORR); lien(c, P[3], P[1], CORR);
        text(c, "Pivot d'axe (A, z)", 360, 292, CORR, 15, "center", "700");
        text(c, "Pivot en E", 576, 200, CORR, 15, "left", "700");
        text(c, "Pivot en F", 360, 112, CORR, 15, "center", "700");
      }
    }""",
}
DR_NAMES = {"GRAPHE_COFFRE": ("DR1", "Q1.5", "Graphe des liaisons de la porte de coffre-fort"),
            "GRAPHE_VELO": ("DR1", "Q1.3", "Graphe des liaisons du cadre de vélo")}


# ============================================================ DOCUMENTS (DP1 propres, DT1 commun)
def dp_coffre():
    src, w, h = png("n3-coffre-photo")
    return ('<div class="doc-text"><h3>Porte de coffre-fort</h3><p>La porte <strong>(4)</strong>, de 3 000 daN, est '
            "articulée sur un bras de manœuvre <strong>(3)</strong> de 1 000 daN. Le bras est guidé par deux gonds "
            "<strong>(1)</strong> (en A) et <strong>(2)</strong> (en B) scellés dans le mur <strong>(0)</strong>. "
            "Étude dans le plan (<var>x</var>, <var>y</var>) ; l'ensemble est en équilibre, porte ouverte.</p></div>"
            f'<img class="doc-img" src="{src}" width="{w}" height="{h}" alt="Porte de coffre-fort circulaire en acier, '
            'montée sur un bras à deux gonds">' + '<p class="doc-cap">Une porte de salle des coffres.</p>' +
            '<img class="doc-img" src="{0}" width="{1}" height="{2}" alt="Plan coté de la porte">'.format(*png("n3-coffre-plan")) +
            '<p class="doc-cap">Plan : cotes en millimètres.</p>' +
            '<img class="doc-img" src="{0}" width="{1}" height="{2}" alt="Schéma cinématique">'.format(*png("n3-coffre-cine")) +
            '<p class="doc-cap">Schéma cinématique : 0 mur, 1 et 2 gonds, 3 bras, 4 porte.</p>')


def dp_echelle():
    return ('<div class="doc-text"><h3>Échelle de pompier</h3><p>L\'échelle <strong>(3)</strong> est articulée en A '
            "(pivot d'axe (A, <var>z</var>)) sur la tourelle <strong>(2)</strong>, qui tourne autour de (D, <var>y</var>) "
            "sur le châssis <strong>(1)</strong>. Le vérin <strong>4 + 5</strong> (tige 4, corps 5) est articulé par des "
            "rotules en B (échelle) et en C (tourelle). Poids de l'échelle : 5 000 daN ; poids du vérin négligé. "
            "Diamètre du piston : 100 mm.</p></div>" +
            '<img class="doc-img" src="{0}" width="{1}" height="{2}" alt="Échelle, tourelle et vérin">'.format(*png("n3-echelle")) +
            '<p class="doc-cap">Ensemble échelle, tourelle, vérin.</p>' +
            '<img class="doc-img" src="{0}" width="{1}" height="{2}" alt="Échelle isolée cotée">'.format(*png("n3-echelle-iso")) +
            '<p class="doc-cap">Échelle isolée : cotes en mètres.</p>')


def dp_velo():
    return ('<div class="doc-text"><h3>Cadre de VTT tout suspendu</h3><p>Cadre avant <strong>(1)</strong> et bras '
            "arrière <strong>(2)</strong> articulés en A (pivot d'axe (A, <var>z</var>)) ; amortisseur "
            "<strong>(3)</strong> articulé en E sur (2) et en F sur (1). Poids du cycliste : 1 000 N en D. Actions "
            "des roues : B (avant) et C (arrière), verticales. C, E et F sont alignés.</p></div>" +
            '<img class="doc-img" src="{0}" width="{1}" height="{2}" alt="Cadre de vélo coté">'.format(*png("n3-velo")) +
            '<p class="doc-cap">Cadre complet, amortisseur et bras arrière isolés : cotes en millimètres.</p>')


# ============================================================ définition des exercices
EXOS = [
    {"page": "coffre-fort.html", "tag": "Exercice 3.1", "level": "Niveau 3", "title": "Porte de coffre-fort",
     "parts": PARTS_COFFRE, "dp": ("Présentation de la porte", dp_coffre), "vign": "carte-coffre-fort.jpg",
     "mots": ["Graphe des liaisons", "Torseurs", "PFS plan", "Gonds"],
     "alt": "Plan de la porte de coffre-fort : bras, porte, gonds A et B, poids P3 et P4",
     "hero": ("n3-coffre-photo", "Porte de coffre-fort en acier montée sur un bras à deux gonds",
              "Une porte de 3 tonnes suspendue à deux gonds : lequel porte la charge ?"),
     "sub": "Une porte de 3 000 daN, articulée sur un bras guidé par deux gonds scellés dans le mur. Après le graphe "
            "des liaisons, tu isoles l'ensemble bras + porte, écris les torseurs dans le plan et appliques le PFS "
            "pour trouver les actions sur les gonds A et B.",
     "desc": "Statique analytique : graphe des liaisons, torseurs transmissibles dans le plan, application du PFS à "
             "une porte de coffre-fort articulée sur deux gonds."},
    {"page": "echelle-pompier.html", "tag": "Exercice 3.2", "level": "Niveau 3", "title": "Échelle de pompier",
     "parts": PARTS_ECHELLE, "dp": ("Présentation de l'échelle", dp_echelle), "vign": "carte-echelle-pompier.jpg",
     "mots": ["Deux forces", "Vérin", "PFS plan", "Pression"],
     "alt": "Échelle de pompier levée par un vérin articulé en B et C",
     "hero": ("n3-echelle", "Échelle de pompier levée par un vérin hydraulique",
              "Quel effort le vérin doit-il fournir pour lever l'échelle ?"),
     "sub": "Une échelle de 5 000 daN levée par un vérin hydraulique. L'isolement du vérin donne la direction de "
            "son action ; le PFS appliqué à l'échelle donne les efforts en A et en B, puis la pression "
            "d'alimentation nécessaire.",
     "desc": "Statique analytique : solide soumis à deux forces, PFS dans le plan appliqué à une échelle de pompier, "
             "pression d'alimentation d'un vérin."},
    {"page": "cadre-velo.html", "tag": "Exercice 3.3", "level": "Niveau 3", "title": "Cadre de vélo tout terrain",
     "parts": PARTS_VELO, "dp": ("Présentation du cadre", dp_velo), "vign": "carte-cadre-velo.jpg",
     "mots": ["Isolements successifs", "Amortisseur", "Trois forces", "Pivot"],
     "alt": "Cadre de VTT tout suspendu : cadre avant, bras arrière et amortisseur",
     "hero": ("n3-velo-cadre", "Cadre de VTT tout suspendu avec son amortisseur",
              "Quel effort comprime l'amortisseur quand le cycliste s'assied ?"),
     "sub": "Un cadre de VTT en deux parties articulées et un amortisseur. Trois isolements successifs — cadre "
            "complet, amortisseur, bras arrière — donnent les actions des roues, puis l'effort de compression de "
            "l'amortisseur et l'action du pivot A.",
     "desc": "Statique analytique : isolements successifs d'un cadre de vélo tout suspendu, solide soumis à deux "
             "forces, PFS dans le plan, effort dans l'amortisseur."},
]


# ============================================================ rendu des exercices
def render_q(q):
    qid, label = q["id"], q["label"]
    return f"""
        <div class="q" id="{qid}" data-q="{qid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{q['stem']}</strong></p>
          <p class="q-hint" id="h-{qid}">{q['hint']}</p>
          <div class="q-row">
            <input type="text" class="q-input" id="in-{qid}" aria-label="Réponse {label}" aria-describedby="h-{qid}" autocomplete="off" autocapitalize="off" spellcheck="false">
            <button type="button" class="btn btn-validate">Valider</button>
            <span class="q-status" aria-live="polite"></span>
            <span class="print-only pstat">Non validée : comptée fausse</span>
          </div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden>
            <p class="q-unit-msg" hidden></p>
            <p class="q-expected"><span>Réponse attendue :</span> {q['expected']}</p>
            <div class="q-why">{q['why']}</div>
          </div>
        </div>"""


def render_qbar(b):
    chips = "".join(f'<button type="button" class="doc-chip" data-doc="{d}" aria-pressed="false">{d}</button>'
                    for d in b["docs"])
    return (f'\n      <div class="qbar" role="group" aria-label="{b["label"]}"><div class="qb-num">{b["label"]}</div>'
            f'<div class="qb-docs">Documents à consulter : {chips}</div><div class="qb-ans">Répondre : {b["ans"]}</div></div>')


# Contexte de rendu de l'exercice en cours de construction (fonds de tracé, barre d'outils propre à un sujet)
CTX = {"sk_bg": None, "toolbar": None}


def render_sk(s, part, total_pts):
    sid, label = s["id"], s["label"]
    src, w, h = png((CTX["sk_bg"] or SK_BG)[s["bg"]])
    crit = "".join(f'<label class="se-item"><input type="checkbox" data-crit="{i}"><span>{c}</span></label>'
                   for i, c in enumerate(s["criteria"]))
    n = len(s["criteria"])
    note = ("La correction se superposera à ton tracé une fois la question " + ", ".join(label_of(d) for d in s["deps"]) +
            " validée.") if s["deps"] else "La correction se superpose à ton tracé dès que tu le valides."
    toolbar = CTX["toolbar"](s) if CTX["toolbar"] else f"""              <div class="sk-toolbar" role="toolbar" aria-label="Outils de tracé {label}">
                <button type="button" data-tool="pen" aria-pressed="false">Crayon</button>
                <button type="button" data-tool="line" aria-pressed="true">Ligne</button>
                <button type="button" data-tool="arrow" aria-pressed="false">Flèche</button>
                <button type="button" data-tool="text" aria-pressed="false">Texte</button>
                <button type="button" data-tool="erase" aria-pressed="false">Gomme</button>
                <span class="sep"></span>
                <button type="button" class="sw" data-color="#1F5FA8" aria-label="Couleur bleue" aria-pressed="true" style="background:#1F5FA8"></button>
                <button type="button" class="sw" data-color="#1B7A43" aria-label="Couleur verte" aria-pressed="false" style="background:#1B7A43"></button>
                <button type="button" class="sw" data-color="#1C2530" aria-label="Couleur noire" aria-pressed="false" style="background:#1C2530"></button>
                <span class="sep"></span>
                <span class="tb-group"><span class="tb-lab">Trait</span>
                  <button type="button" data-width="fin" aria-pressed="false">Fin</button>
                  <button type="button" data-width="moyen" aria-pressed="true">Moyen</button>
                  <button type="button" data-width="epais" aria-pressed="false">Épais</button></span>
                <span class="sep"></span>
                <span class="tb-group"><span class="tb-lab">Zoom</span>
                  <button type="button" data-zoom="out" aria-label="Réduire le zoom">−</button>
                  <span class="zoom-val">100 %</span>
                  <button type="button" data-zoom="in" aria-label="Agrandir le zoom">+</button>
                  <button type="button" data-zoom="reset">Ajuster</button></span>
                <span class="sep"></span>
                <button type="button" data-act="undo">Annuler</button>
                <button type="button" data-act="clear">Tout effacer</button>
                <span class="spacer"></span>
                <button type="button" class="btn-drprint" data-act="drprint">Imprimer les DR</button>
                <button type="button" data-act="full" aria-pressed="false">Plein écran</button>
              </div>
"""
    return f"""
        <div class="sketch{' gt-sketch' if CTX['toolbar'] else ''}" data-sketch="{sid}" id="{sid}">
          <p class="q-stem"><span class="q-num">{label}</span> <strong>{s['stem']}</strong></p>
          <div class="sk-layout">
            <div class="sk-main">
{toolbar}              <div class="sk-stage"><img class="sk-bg" src="{src}" width="{w}" height="{h}" alt="" hidden>
                <canvas role="img" aria-label="Zone de tracé {label}"></canvas></div>
              <div class="gt-status" aria-live="polite"></div>
              <div class="sk-foot">
                <button type="button" class="btn btn-sketch">Valider mon tracé</button>
                <label class="sk-corr-toggle"><input type="checkbox"> Superposer la correction</label>
                <span class="sk-meas" aria-live="polite"></span><span class="q-status" aria-live="polite"></span>
              </div>
              <div class="sk-print-wrap print-only"><p>Tracé de l'élève</p><img class="sk-print sk-print-student" alt="Tracé de l'élève">
                <p>Correction superposée à la figure</p><img class="sk-print sk-print-corr" alt="Correction du tracé"></div>
              <div class="selfeval" hidden>
                <p class="se-title">Auto-évaluation — {n} points sur les {total_pts} de la partie {part['num']}</p>
                <p class="se-lead">Compare ton tracé à la correction ci-dessus, puis coche uniquement ce que ton tracé comporte réellement. Sois honnête : c'est toi qui repères ce qu'il te reste à travailler.</p>
                {crit}
                <div class="se-foot"><button type="button" class="btn btn-self">Valider mon auto-évaluation</button>
                  <span class="se-score" aria-live="polite"></span></div>
                <p class="print-only se-print"></p>
              </div>
            </div>
            <div class="sk-side">{s['side']}</div>
          </div>
          <p class="sk-note sk-note-wrap">{note} <span class="sk-wait" aria-live="polite"></span></p>
          <div class="q-expl" hidden><p class="q-expected"><span>Correction du tracé</span></p>
            {s['expl']}</div>
        </div>"""


def part_points(p):
    return sum(1 if b["kind"] == "q" else len(b["criteria"]) for b in p["blocks"] if b["kind"] in ("q", "sk"))


def hm(minutes):
    h, m = divmod(minutes, 60)
    return f"{h} h {m:02d}" if h else f"{m} min"


def render_part(p, total_min):
    pts = part_points(p)
    blocks = []
    for b in p["blocks"]:
        if b["kind"] == "q":
            blocks.append(render_q(b))
        elif b["kind"] == "qbar":
            blocks.append(render_qbar(b))
        elif b["kind"] == "sk":
            blocks.append(render_sk(b, p, pts))
    n = p["num"]
    pct = fr(p["minutes"] / total_min * 100, 1)
    return f"""
  <section class="part" id="partie-{n}" aria-labelledby="t-partie-{n}">
    <header class="part-head"><div class="part-num" aria-hidden="true">{n}</div>
      <div><h2 id="t-partie-{n}"><span class="sr-only">Partie {n} : </span>{p['title']}</h2>
        <div class="duree">Durée conseillée : {hm(p['minutes'])} · Barème : {pts} points, soit {pct} % de la note</div></div></header>
    <div class="part-body">
      {"".join(p["intro"])}{"".join(blocks)}
    </div>
  </section>"""


def check_parts(parts):
    """Libellés et cohérence : identifiants qN_M rangés dans la partie N, sans doublon."""
    seen = set()
    for p in parts:
        for b in p["blocks"]:
            if b["kind"] in ("q", "sk"):
                qid = b["id"][3:] if b["kind"] == "sk" else b["id"]
                assert qid not in seen, f"identifiant en double : {qid}"
                seen.add(qid)
                assert qid.startswith(f"q{p['num']}_"), f"{qid} rangé dans la partie {p['num']}"
                b["label"] = label_of(qid)


CONTENT_CSS = """<style>
/* ---------- compléments de contenu (hors gabarit) : calculs, torseurs, retour à l'accueil ---------- */
.eq{margin:.35rem 0 .55rem; overflow-x:auto; line-height:2.1}
.eq b{background:#fff; border:1px solid var(--trait); padding:0 .3rem; white-space:nowrap}
.frac{display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 .12em; line-height:1.25}
.frac>span{padding:0 .25em; white-space:nowrap}
.frac>span:first-child{border-bottom:1px solid currentColor}
.sqrt{white-space:nowrap; display:inline-flex; align-items:stretch; vertical-align:middle}
.sqrt>.radix{display:flex; align-items:flex-end; font-size:1.1em; line-height:1; margin-right:-.12em}
.sqrt>.rad{border-top:1.2px solid currentColor; border-left:1.2px solid currentColor; padding:.12em .2em 0 .25em; line-height:1.35; display:inline-flex; align-items:center}
.torseur{display:inline-flex; align-items:center; gap:6px; margin:4px 0; flex-wrap:wrap; vertical-align:middle}
.tz-b{display:inline-block; border-left:2px solid currentColor; border-right:2px solid currentColor; border-radius:10px; padding:2px 6px}
.tz-b table{border-collapse:collapse} .tz-b td{padding:1px 10px; text-align:center; min-width:3.2em; line-height:1.5}
.tz-r{font-size:.8rem; color:var(--encre-2)}
.home-hero img{display:block; width:auto!important; max-width:100%; max-height:300px; margin:0 auto}
.n3-split{display:flex; flex-wrap:wrap; gap:12px 18px; align-items:flex-start}
.n3-split>.fig{flex:0 1 auto; margin:0} .n3-split>.data{flex:1 1 300px; margin:0}
.doc-text ol,.doc-text ul{padding-left:1.2rem}
.doc-text li{margin:.2rem 0}
.dt-f{font:700 1.05rem var(--f-titre); background:var(--jaune-pale); padding:4px 10px; display:inline-block}
.dt-t{font-size:.9rem}
.retour-accueil{display:inline-flex; align-items:center; gap:8px; text-decoration:none; margin:0 0 14px}
.retour-accueil svg,.c-top svg{width:18px; height:18px; flex:0 0 auto}
body:not(.no-mode) .home-back{display:none}
.c-top{margin:0 0 12px}
.c-top a{display:inline-flex; align-items:center; gap:6px; font:600 .95rem var(--f-titre); color:var(--encre); text-decoration:none; border:1.5px solid var(--encre); background:var(--papier); padding:5px 12px 5px 10px}
.c-top a:hover{background:var(--jaune-pale)}
.home-head .pastille{display:inline-block; font:700 .72rem var(--f-titre); letter-spacing:.03em; background:#7B3FA0; color:#fff; padding:2px 8px; margin-left:8px; vertical-align:middle}
.home-head .pastille.n1{background:var(--vert)} .home-head .pastille.n2{background:var(--bleu)}
.gt-status:empty{display:none}
.home-head .mc-tag{vertical-align:middle}
.recap-foot a.btn{display:inline-flex; align-items:center; gap:8px; text-decoration:none}
.recap-foot a.btn svg{width:18px; height:18px}
@media print{
  .c-top,.home-back{display:none!important}
  /* correctif repris du dépôt RDM : la correction des tracés ne doit pas s'imprimer avant la remise en mode examen */
  body:not(.corrections-open) .sketch .q-expl[hidden]{display:none!important}
  .eq{overflow:visible; line-height:1.7}
}
</style>"""


CONVENTIONS_N3 = ("<p><strong>Conventions.</strong> Étude dans le plan (<var>x</var>, <var>y</var>) : chaque torseur se réduit à "
                  "<i>X</i>, <i>Y</i> et au moment <i>N</i> autour de <var>z</var>. Un moment est <strong>positif dans le "
                  "sens trigonométrique</strong> : M<sub>A</sub>(F) = <var>x</var>·F<sub>y</sub> − <var>y</var>·F<sub>x</sub>. "
                  "Les composantes sont algébriques : n'oublie pas le signe ; une norme est toujours positive.</p>")
CALCULS_N3 = ("<p><strong>Calculs.</strong> Garde les valeurs non arrondies dans ta calculatrice : les tolérances couvrent les "
              "arrondis des résultats intermédiaires demandés.</p>")


def build_exo(e, g):
    """Page autonome d'un exercice : contenu + bloc de style, Grading et moteur applicatif du gabarit."""
    parts = e["parts"]
    check_parts(parts)
    CTX["sk_bg"], CTX["toolbar"] = e.get("sk_bg"), e.get("toolbar")
    decor_src, drn_src = e.get("decor", DECOR), e.get("dr_names", DR_NAMES)
    total = sum(p["minutes"] for p in parts)
    n_q = sum(1 for p in parts for b in p["blocks"] if b["kind"] == "q")
    n_sk = sum(1 for p in parts for b in p["blocks"] if b["kind"] == "sk")
    s0 = g.index("<style>:root{")
    style = g[s0:g.index("</style>", s0) + len("</style>")]
    grading = re.search(r"<script>/\*GRADING-START\*/.*?</script>", g, re.S).group(0)
    app_start = g.index("<script>(function () {")
    app = g[app_start:g.rindex("</script>") + len("</script>")]

    def sub_once(text, pattern, repl, flags=0):
        new, n = re.subn(pattern, lambda m: repl, text, flags=flags)
        assert n == 1, f"motif introuvable ou multiple : {pattern!r} ({n})"
        return new

    bgs = sorted({b["bg"] for p in parts for b in p["blocks"] if b["kind"] == "sk"})
    decor = (e.get("decor_helpers", DECOR_HELPERS) + "  var DECOR = {\n" + ",\n".join(decor_src[k] for k in bgs) +
             "\n  };\n")
    drn = "  var DR_NAMES = {\n" + ",\n".join(
        f'    {k}: {{ doc: "{drn_src[k][0]}", q: "{drn_src[k][1]}", t: "{drn_src[k][2]}", scale: false }}'
        for k in bgs) + "\n  };\n"
    app = sub_once(app, r"var CONSEIL_MIN = \d+;", f"var CONSEIL_MIN = {total};")
    app = sub_once(app, r"  var DECOR = \{\n.*?\n  \};\n", decor, re.S)
    app = sub_once(app, r"  var DR_NAMES = \{\n.*?\n  \};\n", drn, re.S)
    app = sub_once(app, r"Quatre pages, une par document", "Une page par document réponse")

    parts_cfg, qcfg, skcfg = [], {}, {}
    for p in parts:
        parts_cfg.append({"num": p["num"], "title": p["title"], "minutes": p["minutes"], "duration": hm(p["minutes"]),
                          "points": part_points(p)})
        for b in p["blocks"]:
            if b["kind"] == "q":
                qcfg[b["id"]] = {"label": b["label"], "part": p["num"], "pts": 1, "grader": b["grader"]}
            elif b["kind"] == "sk":
                skcfg[b["id"]] = {"bg": b["bg"], "deps": b["deps"], "label": b["label"], "part": p["num"],
                                  "pts": len(b["criteria"]), "criteria": [re.sub(r"<[^>]+>", "", c) for c in b["criteria"]]}
    config = (f"<script>window.__PARTS__ = {json.dumps(parts_cfg, ensure_ascii=False)};\n"
              f"window.__QCFG__ = {json.dumps(qcfg, ensure_ascii=False)};\n"
              f"window.__SKCFG__ = {json.dumps(skcfg, ensure_ascii=False)};</script>")

    if e.get("docs"):
        docs = e["docs"]()
    else:
        dp_title, dp_fn = e["dp"]
        docs = [("DP1", dp_title, "Dossier présentation", False, dp_fn()),
                ("DT1", "Formulaire de statique analytique", "Dossier technique", True, DT_FORMULAIRE)]
    doc_names = [d[0] for d in docs]
    docs_txt = ", ".join(doc_names[:-1]) + " et " + doc_names[-1] if len(doc_names) > 1 else doc_names[0]
    rail, grp = [], False
    for k, t, kind, is_dt, _c in docs:
        if is_dt and not grp:
            rail.append('<div class="grp" aria-hidden="true"></div>')
            grp = True
        rail.append(f'<button type="button" class="tab{" dt" if is_dt else ""}" data-doc="{k}" aria-selected="false" '
                    f'title="{esc(t)}">{k}</button>')
    tabs = "".join(f'<button type="button" data-doc="{k}" aria-selected="false">{k}</button>' for k, *_r in docs)
    secs = "\n".join(f'<section class="doc" id="doc-{k}" data-title="{k} : {esc(t)}" data-kind="{kind}">{c}</section>'
                     for k, t, kind, _d, c in docs)

    hsrc, hw, hh = png(e["hero"][0])
    sk_fact = (f'<div><b>{n_sk} tracé{"s" if n_sk > 1 else ""}</b><span>{e.get("sk_fact", "graphe des liaisons, auto-évalué")}</span></div>'
               if n_sk else '<div><b>Unités</b><span>notées (demi-point)</span></div>')
    parts_html = "".join(render_part(p, total) for p in parts)
    cartouche = (f"{n_q} questions notées (unités comprises)" +
                 (f" et {n_sk} tracé auto-évalué" if n_sk else "") +
                 f", répartis en {len(parts)} parties pondérées par leur durée.")
    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Fichier généré par src/generer.py (contenu : {e.get("module", "src/niveau3.py")}) à partir de src/gabarit-exercice-interactif.html : ne pas modifier à la main. -->
<title>{e['title']} — Statique — exercice interactif</title>
<meta name="description" content="{esc(e['desc'])}">
{style}
{CONTENT_CSS}
{e.get("extra_css", "")}
</head>
<body class="no-mode">

<nav class="rail" aria-label="Dossier de présentation et dossier technique">
  {"".join(rail)}
</nav>

<aside id="docpanel" aria-label="Documents du sujet" aria-hidden="true">
  <div class="dp-head">
    <h3 id="dp-title">Documents</h3>
    <button type="button" id="dp-out" aria-label="Réduire">−</button><span id="dp-zoom" class="small">100 %</span>
    <button type="button" id="dp-in" aria-label="Agrandir">+</button>
    <button type="button" id="dp-fit">Ajuster</button>
    <button type="button" id="dp-close">Fermer</button>
  </div>
  <div class="dp-tabs" role="tablist" aria-label="Choisir un document">{tabs}</div>
  <div class="dp-body">
{secs}
  </div>
</aside>

<section id="home" aria-labelledby="home-title">
  <div class="home-inner">
    <header class="home-head">
      <span class="mc-tag">{e['tag']}</span><span class="pastille {e.get("pastille", "n3")}">{e['level']}</span>
      <h1 id="home-title">{e['title']}</h1>
      <p class="home-sub">{e['sub']}</p>
    </header>
    <figure class="home-hero">
      <img src="{hsrc}" alt="{esc(e['hero'][1])}" width="{hw}" height="{hh}">
      <figcaption>{e['hero'][2]}</figcaption>
    </figure>
    <div class="home-facts">
      <div><b>{len(parts)} parties</b><span>{n_q} questions, dans l'ordre de résolution</span></div>
      <div><b>{hm(total)}</b><span>durée conseillée, qui fixe la pondération</span></div>
      <div><b>{len(docs)} documents</b><span>{docs_txt} consultables</span></div>
      {sk_fact}
    </div>
    <h2 class="home-choose">Choisis ton mode de travail</h2>
    <div class="modes">
      <article class="mode-card">
        <div class="mc-head"><span class="mc-tag">Mode 1</span><h3>Mode entraînement</h3></div>
        <p class="mc-lead">Pour apprendre en avançant, question par question.</p>
        <ul><li>Chaque question se valide isolément ; la démarche corrigée s'affiche aussitôt.</li>
          <li>La note pondérée s'actualise en continu dans le bandeau.</li>
          <li>Les documents et le chronomètre restent disponibles, sans contrainte de temps.</li></ul>
        <button type="button" class="btn btn-mode" data-mode="training">Commencer l'entraînement</button>
      </article>
      <article class="mode-card exam">
        <div class="mc-head"><span class="mc-tag">Mode 2</span><h3>Mode examen</h3></div>
        <p class="mc-lead">Pour se placer en conditions d'évaluation.</p>
        <ul><li>Aucune correction et aucune note pendant la composition ; les réponses restent modifiables.</li>
          <li>Le chronomètre tourne, à comparer à la durée conseillée.</li>
          <li>En fin de sujet, le bouton « J'ai fini, je fais corriger ma copie » dévoile d'un coup les corrections, les notes par partie et la note globale.</li></ul>
        <button type="button" class="btn btn-mode" data-mode="exam">Composer en mode examen</button>
      </article>
    </div>
    <p class="home-note small">Le mode se choisit une seule fois : pour en changer, recharge la page. Rien n'est enregistré sur l'ordinateur.</p>
    <p class="home-back no-print"><a class="btn ghost retour-accueil" href="index.html">{HOUSE} Accueil : Statique</a></p>
  </div>
</section>

<main class="page">
  <section class="print-only print-summary">
    <p>Élève : <span class="print-nom"></span> | Copie imprimée le <span class="print-date"></span></p>
    <p>Mode : <span class="print-mode"></span> | Temps de rédaction : <strong class="print-time"></strong> (durée conseillée : {hm(total)})</p>
    <p class="print-note-line">Note finale pondérée : <strong class="final-note"></strong></p>
    <p class="print-nograde">Copie non corrigée : les corrections et la note n'apparaissent qu'après la remise de la copie en mode examen.</p>
  </section>

  <nav class="c-top no-print" aria-label="Navigation"><a href="index.html">{HOUSE} Accueil</a> <a href="{e.get("cours", ("cours-statique-analytique.html", ""))[0]}">{e.get("cours", ("", "Cours 3 — Statique analytique"))[1]}</a></nav>

  <header class="cartouche">
    <div class="title">
      <h1>{e['title']}</h1>
      <p>{cartouche}</p></div>
    <div class="nom"><label for="nom-eleve">Nom et prénom</label><input id="nom-eleve" type="text" autocomplete="name"></div>
  </header>

  <div class="consignes">
    <p class="only-training"><strong>Mode entraînement.</strong> Réponds dans chaque champ puis clique sur « Valider » : une réponse validée est définitive et sa correction s'affiche aussitôt.</p>
    <p class="only-exam"><strong>Mode examen.</strong> Compose tout le sujet sans correction ni note : tes réponses restent modifiables jusqu'au bout. Le bouton « J'ai fini, je fais corriger ma copie », en fin de sujet, dévoile d'un coup les corrections, les notes par partie et la note globale.</p>
    {e.get("conventions", CONVENTIONS_N3)}
    <p><strong>Les unités sont notées.</strong> Pour toute question numérique, la valeur vaut la moitié des points et l'unité l'autre moitié : une valeur juste écrite sans unité, ou avec une unité fausse, ne rapporte qu'un demi-point. Une valeur convertie (N, daN, kN, mm, m) avec la bonne unité est acceptée.</p>
    {e.get("calculs", CALCULS_N3)}
    <p>Le dossier de présentation (DP1) et le dossier technique (DT) s'ouvrent avec les onglets sur le bord droit, ou avec les boutons des en-têtes de question.</p>
    <p><strong>Le tracé compte aussi.</strong> Quand sa correction s'affiche, tu t'attribues toi-même les points à l'aide d'une grille de critères.</p>
    <p><strong>Barème pondéré par la durée conseillée</strong> : chaque partie est notée sur 20, puis pèse au prorata de son temps. Le récapitulatif de fin de sujet donne le détail partie par partie.</p>
  </div>
{parts_html}

  <section class="recap" id="recap" aria-labelledby="t-recap">
    <header class="recap-head"><h2 id="t-recap">Récapitulatif et note finale</h2>
      <p class="small">Les questions non validées comptent comme fausses. Chaque partie est ramenée sur 20, puis pondérée par sa durée conseillée.</p></header>
    <div id="exam-submit-wrap">
      <p class="es-lead">Ta copie n'est pas encore corrigée : aucune réponse n'est verrouillée, tu peux encore revenir sur les questions et le tracé.</p>
      <button type="button" class="btn btn-exam" id="exam-submit">J'ai fini, je fais corriger ma copie</button>
      <p class="es-warn" id="exam-warn" role="alert"></p>
    </div>
    <div id="recap-graded">
      <div class="recap-wrap">
        <table class="t recap-table">
          <thead><tr><th>Partie</th><th>Durée</th><th>Poids</th><th>Points</th><th>Note /20</th><th>Contribution</th></tr></thead>
          <tbody id="recap-body"></tbody>
          <tfoot><tr><th colspan="4">Note globale pondérée</th><th class="final-note"></th><th></th></tr></tfoot>
        </table>
      </div>
      <p class="final-detail small"></p>
    </div>
    <div class="recap-foot" id="recap-foot"><button type="button" class="btn btn-print">Imprimer ma copie</button>
      <span class="small no-print">L'impression reprend tes réponses, les corrections, ton tracé et ce récapitulatif.</span>
      <a class="btn ghost no-print" href="index.html">{HOUSE} Retour à l'accueil</a></div>
  </section>
</main>

<footer class="banner" aria-label="Suivi de la composition">
  <div class="score-block"><div class="lab">Note provisoire</div><div class="score" id="score-val">–<small>/20</small></div></div>
  <div class="exam-block"><div class="lab">Mode examen</div><div class="exam-state">Note masquée</div></div>
  <div class="timer-block"><div class="lab">Temps</div><div class="timer" id="timer-val">0:00:00</div></div>
  <div class="count" id="score-count" aria-live="polite"></div>
  <div class="spacer"></div>
  <button type="button" class="btn-docs" id="btn-docs">Documents</button>
</footer>

<!-- CONFIGURATION DU SUJET -->
{config}
{grading}
{app}
{e.get("extra_js", "")}
</body>
</html>
"""
    stats = {"n_q": n_q, "n_sk": n_sk, "minutes": total, "points": sum(part_points(p) for p in parts),
             "parts": len(parts)}
    return page, stats

