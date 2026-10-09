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


# ============================================================ torseurs et vecteurs à compléter (questions groupées)
# Un groupe est rendu comme une question « groupe » du gabarit (.fast-q) : chaque case est notée séparément
# (pts par case), toutes les cases se valident ensemble. Cases : 0, nom d'une inconnue, valeur, expression linéaire.
def Z():
    """Case nulle."""
    return num(0, absTol=1e-6)


def SYM(*noms):
    """Case « inconnue » : son nom (X_A, Y_B…), insensible à la casse et au tiret bas."""
    return CODE(equals=[n.lower().replace("_", "") for n in noms])


def VAL(v, rel=0.002, abs_=None):
    """Case numérique, sans unité (l'unité est donnée par l'en-tête du torseur)."""
    return num(v, absTol=abs_ if abs_ is not None else 1e-9, relTol=rel)


def LIN(noms, coef, tol):
    """Case « expression » : coefficient × inconnue, par exemple −2,1X_A ou 3,24F."""
    return {"type": "lin", "vars": [n.lower().replace("_", "") for n in noms], "coef": coef, "absTol": tol}


def TZ(nom, point, cX, cY, cN):
    """Torseur plan (x, y) : composantes X, Y (résultante) et N (moment) ; chaque cellule = (grader, texte attendu)."""
    return {"kind": "tz", "nom": nom, "point": point, "cells": [("X", *cX), ("Y", *cY), ("N", *cN)]}


def VEC(nom, cells, unite=""):
    """Vecteur à composantes (ou liste de valeurs) : cells = [(nom de la case, grader, texte attendu)…]."""
    return {"kind": "vec", "nom": nom, "cells": cells, "unite": unite}


def GRP(qid, stem, hint, items, why, pts=0.5, unite=""):
    return {"kind": "grp", "id": qid, "stem": stem, "hint": hint, "items": items, "why": why, "pts": pts,
            "unite": unite}


def z():
    return (Z(), "0")


def sym(n):
    return (SYM(n), n.replace("_", "<sub>", 1) + "</sub>" if "_" in n else n)


def val(v, d=2, rel=0.002, abs_=None):
    return (VAL(v, rel, abs_), fr(v, d))


def lin(noms, coef, tol, d=3):
    n = noms[0]
    nh = n.replace("_", "<sub>", 1) + "</sub>" if "_" in n else n
    return (LIN(noms, coef, tol), f"{fr(coef, d)} {nh}")


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

H_TZ = ("Une composante inconnue s'écrit avec son nom (X_A, Y_B…), une composante nulle s'écrit 0, une valeur connue "
        "se saisit en nombre avec son signe. Unités : celles indiquées dans la question.")
H_TZ_B = ("Moments en daN·m, positifs dans le sens trigonométrique. Un moment inconnu s'écrit coefficient × inconnue, "
          "par exemple −1,5X_A (signe et coefficient comptent).")
H_RES = "Composantes algébriques, arrondies au centième, en daN. Une composante nulle s'écrit 0."

PARTS_COFFRE = [
    {"num": "1", "minutes": 15, "title": "Modélisation : graphe des liaisons",
     "intro": [
         "<p>La porte de coffre-fort ferme la salle des coffres d'une banque. Elle se compose d'une porte "
         "<strong>(4)</strong> articulée sur un bras de manœuvre <strong>(3)</strong>. L'ensemble est articulé sur "
         "deux gonds <strong>(1)</strong> et <strong>(2)</strong> scellés dans le mur <strong>(0)</strong> en A et B. "
         "L'étude est réalisée dans le plan (<var>x</var>, <var>y</var>) ; l'ensemble est en équilibre. "
         f"{V('P', '4')} (3 000 daN) schématise le poids de la porte et {V('P', '3')} (1 000 daN) le poids du bras.</p>",
         '<div class="n3-split">' +
         figure("n3-coffre-plan", "Plan de la porte : gonds A en haut et B en bas, bras 3 en bleu, porte 4, poids "
                "P3 de 1 000 daN en G3 et P4 de 3 000 daN en G4 ; cotes 1 050, 1 050, 400 et a = 880 mm",
                "Figure 1 — Porte de coffre-fort (cotes en mm).", 420) +
         figure("n3-coffre-cine", "Schéma cinématique : mur 0, gond 1 en A, gond 2 en B, bras 3, porte 4",
                "Figure 2 — Schéma cinématique.", 230) + "</div>",
     ],
     "blocks": [
         QBAR("Q1.1", ["DP1", "DT1"], ans="sur la figure"),
         SK("sk_q1_1", "Q1.1", "GRAPHE_COFFRE",
            "À l'aide du schéma cinématique, réaliser le graphe des liaisons du système : relier les solides et nommer "
            "chaque liaison (avec son centre ou son axe).",
            ["Cinq liaisons sont tracées, ni plus ni moins : 0–1, 0–2, 1–3, 2–3 et 3–4.",
             "Les liaisons 0–1 et 0–2 sont nommées « encastrement ».",
             "La liaison 1–3 est nommée « linéaire annulaire d'axe (A, y) ».",
             "La liaison 2–3 est nommée « rotule de centre B ».",
             "La liaison 3–4 est nommée « pivot d'axe y » (vertical)."],
            "<p>Outils : <b>Ligne</b> pour relier deux solides, <b>Texte</b> pour nommer la liaison.</p>" +
            figure("n3-coffre-cine", "Schéma cinématique de la porte", "Schéma cinématique (rappel).", 200),
            "<p>Cinq liaisons : 0–1 et 0–2 <strong>encastrements</strong> (gonds scellés) ; 1–3 <strong>linéaire "
            "annulaire d'axe (A, <var>y</var>)</strong> (sphère dans un cylindre vertical) ; 2–3 <strong>rotule de "
            "centre B</strong> ; 3–4 <strong>pivot d'axe <var>y</var></strong>. L'ensemble {0, 1, 2} forme le bâti ; "
            "la linéaire annulaire et la rotule réalisent ensemble un pivot d'axe (AB).</p>"),
     ]},
    {"num": "2", "minutes": 20, "title": "Isolement de l'ensemble (3 + 4) : bilan des actions",
     "intro": ["<p>On isole l'ensemble {3 + 4}. Repère (B, <var>x</var>, <var>y</var>) : origine B, <var>x</var> "
               "horizontal vers la droite, <var>y</var> vertical vers le haut. Les cotes sont sur la figure 1.</p>"],
     "blocks": [
         QBAR("Q2.1 – Q2.2", ["DP1", "DT1"]),
         GRP("q2_1", "Donner les coordonnées des points A, G3 et G4 dans le repère (B, x, y), en mètres.",
             "Nombres en mètres, arrondis au centième.",
             [VEC("A", [("x", *val(0, 2, 0, 0.005)), ("y", *val(YA_C, 2, 0, 0.005))]),
              VEC("G3", [("x", *val(XG3_C, 2, 0, 0.005)), ("y", *val(YG_C, 2, 0, 0.005))]),
              VEC("G4", [("x", *val(XG4_C, 2, 0, 0.005)), ("y", *val(YG_C, 2, 0, 0.005))])],
             "<p>A est à la verticale de B, 1 050 + 1 050 = 2 100 mm plus haut. G3 est à 400 mm de l'axe AB, à "
             "mi-hauteur ; G4 est 880 mm plus loin (la cote <i>a</i> part de G3, pas de l'axe).</p>"),
         GRP("q2_2", "Isoler l'ensemble (3 + 4) et écrire, en leur point d'application, les torseurs des actions "
             "mécaniques extérieures, dans le plan (x, y). Forces en daN.", H_TZ,
             [TZ("1→3", "A", sym("X_A"), z(), z()),
              TZ("2→3", "B", sym("X_B"), sym("Y_B"), z()),
              TZ("P3", "G3", z(), val(-P3_C, 0, 0, 0.5), z()),
              TZ("P4", "G4", z(), val(-P4_C, 0, 0, 0.5), z())],
             "<p><strong>Linéaire annulaire d'axe (A, <var>y</var>)</strong> : translation selon <var>y</var> et "
             "rotations libres ⇒ <i>Y</i><sub>A</sub> = 0 et moment nul : une seule inconnue, <i>X</i><sub>A</sub>. "
             "<strong>Rotule de centre B</strong> : force quelconque passant par B, moment nul : <i>X</i><sub>B</sub>, "
             "<i>Y</i><sub>B</sub>. Les poids sont verticaux, vers le bas. Bilan : 3 inconnues pour 3 équations, le "
             "problème est résoluble. La liaison 3–4 est intérieure à l'ensemble isolé : elle n'apparaît pas.</p>"),
     ]},
    {"num": "3", "minutes": 25, "title": "Application du PFS au point B",
     "intro": ["<p>On choisit le point où l'action a le plus d'inconnues : B. Tous les torseurs y sont transportés, "
               "puis on écrit les trois équations du PFS.</p>"],
     "blocks": [
         QBAR("Q3.1 – Q3.4", ["DT1"]),
         GRP("q3_1", "Écrire les quatre torseurs au point B (forces en daN, moments en daN·m).", H_TZ_B,
             [TZ("1→3", "B", sym("X_A"), z(), lin(["X_A"], -YA_C, 0.006, 1)),
              TZ("2→3", "B", sym("X_B"), sym("Y_B"), z()),
              TZ("P3", "B", z(), val(-P3_C, 0, 0, 0.5), val(MP3_C, 0, 0, 0.5)),
              TZ("P4", "B", z(), val(-P4_C, 0, 0, 0.5), val(MP4_C, 0, 0, 0.5))],
             "<p>La résultante ne change pas ; le moment en B vaut <i>M</i><sub>B</sub> = <i>x</i>·<i>F</i><sub>y</sub> − "
             "<i>y</i>·<i>F</i><sub>x</sub> avec (<i>x</i> ; <i>y</i>) les coordonnées du point d'application :</p>" +
             eq("<i>N</i><sub>B</sub>(A) = 0 × 0 − 2,1 × <i>X</i><sub>A</sub> = −2,1 <i>X</i><sub>A</sub> ; "
                "<i>N</i><sub>B</sub>(P3) = 0,4 × (−1 000) = −400 ; <i>N</i><sub>B</sub>(P4) = 1,28 × (−3 000) = −3 840")),
         GRP("q3_2", "Résoudre le PFS et donner les actions mécaniques en A et en B.", H_RES,
             [VEC(V("A", "1/3"), [("X", *val(XA_C, 2, 0.001)), ("Y", *val(0, 0, 0, 0.5))], "daN"),
              VEC(V("B", "2/3"), [("X", *val(XB_C, 2, 0.001)), ("Y", *val(YB_C, 0, 0.001))], "daN")],
             eq("Σ<i>N</i><sub>B</sub> = 0 : −2,1 <i>X</i><sub>A</sub> − 400 − 3 840 = 0 ⇒ <i>X</i><sub>A</sub> = " +
                frac("−4 240", "2,1") + f" ≈ <b>{fr(XA_C)} daN</b>") +
             eq(f"Σ<i>X</i> = 0 : <i>X</i><sub>A</sub> + <i>X</i><sub>B</sub> = 0 ⇒ <i>X</i><sub>B</sub> ≈ <b>{fr(XB_C)} daN</b>") +
             eq("Σ<i>Y</i> = 0 : <i>Y</i><sub>B</sub> − 1 000 − 3 000 = 0 ⇒ <i>Y</i><sub>B</sub> = <b>4 000 daN</b>") +
             "<p>Les gonds forment un couple de forces horizontales : le gond du haut retient le bras (vers les "
             "<var>x</var> négatifs), celui du bas le pousse.</p>"),
         Q("q3_3", f"Calculer la norme ‖{V('B', '2/3')}‖.", H_D,
           num(NB_C, "daN", relTol=0.001, variants=[var(NB_C * 10, "N", relTol=0.001), var(NB_C / 100, "kN", relTol=0.001)]),
           f"‖{V('B', '2/3')}‖ ≈ {fr(NB_C, 1)} daN",
           eq(f"‖{V('B', '2/3')}‖ = " + sqrt("<i>X</i><sub>B</sub>² + <i>Y</i><sub>B</sub>²") + f" ≈ <b>{fr(NB_C, 1)} daN</b>")),
         Q("q3_4", "Lequel des deux gonds porte le poids de la porte et du bras ?",
           "Réponds par le point (A ou B) ou par le numéro du gond.",
           CODE(equals=["b", "2", "gondb", "gond2", "legondb", "legond2", "enb", "gondenb", "legondenb", "pointb",
                        "gond2enb", "legond2enb", "gondinferieur", "legondinferieur", "legondinferieur2"]),
           "le gond (2), en B",
           "<p><i>Y</i><sub>A</sub> = 0 : seul le gond B reprend la charge verticale de 4 000 daN ; le gond A ne fait que "
           "retenir le bras horizontalement.</p>"),
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

UX_E, UY_E = -math.cos(ALPHA), math.sin(ALPHA)

PARTS_ECHELLE = [
    {"num": "1", "minutes": 10, "title": "Isolement du vérin (4 + 5)",
     "intro": [
         "<p>Une échelle de pompier <strong>(3)</strong> est articulée en A (pivot d'axe (A, <var>z</var>)) sur une "
         "tourelle <strong>(2)</strong>, qui peut pivoter autour de (D, <var>y</var>) par rapport au châssis "
         "<strong>(1)</strong>. Le levage est réalisé par un vérin hydraulique <strong>4 + 5</strong> articulé en B sur "
         "l'échelle et en C sur la tourelle par deux <strong>liaisons rotules</strong>. Étude dans le plan "
         f"(<var>x</var>, <var>y</var>), ensemble en équilibre ; {V('P', '3')} (5 000 daN) schématise le poids de "
         "l'échelle ; le poids du vérin est négligé.</p>",
         figure("n3-echelle", "Échelle 3 articulée en A sur la tourelle 2, vérin 4 + 5 entre B et C incliné de 70°, "
                "poids P3 de 5 000 daN en G3", "Figure 1 — Échelle de pompier.", 440),
     ],
     "blocks": [
         QBAR("Q1.1 – Q1.2", ["DP1", "DT1"]),
         Q("q1_1", "Isoler le vérin (4 + 5) : quelle est la droite d'action des actions mécaniques qui agissent sur lui ?",
           H_DROITE, DROITE("B", "C"), "la droite (BC)",
           "<p>Le vérin, de poids négligé, n'est lié qu'en B et en C : solide soumis à deux forces, de même droite "
           "d'action <strong>(BC)</strong>, même intensité, sens contraires. La direction de l'action en B est donc "
           "connue : il ne restera que son intensité.</p>"),
         Q("q1_2", "Le vérin est-il comprimé ou tendu ?", "Réponds en un mot.", COMPRIME, "comprimé",
           "<p>Le vérin pousse l'échelle par en dessous : il travaille en compression.</p>"),
     ]},
    {"num": "2", "minutes": 20, "title": "Isolement de l'échelle (3) : bilan des actions",
     "intro": [
         "<p>On isole l'échelle (3). Repère (A, <var>x</var>, <var>y</var>) de la figure 2. On note <i>F</i> "
         "l'intensité (inconnue) de l'action du vérin.</p>",
         figure("n3-echelle-iso", "Échelle isolée : A à l'origine, B à 2,85 m en x et 1,65 m en y, droite BC à 70°, "
                "poids P3 de 5 000 daN à 6 m de A", "Figure 2 — Échelle (3) isolée.", 400),
     ],
     "blocks": [
         QBAR("Q2.1 – Q2.2", ["DT1"]),
         GRP("q2_1", "Donner les coordonnées de B (en m) et les composantes du vecteur unitaire <i>u</i> porté par (BC), "
             "orienté de C vers B.", "Coordonnées au centième, composantes de <i>u</i> au millième.",
             [VEC("B", [("x", *val(XB_E, 2, 0, 0.005)), ("y", *val(YB_E, 2, 0, 0.005))], "m"),
              VEC("<i>u</i>", [("x", *val(UX_E, 3, 0, 0.003)), ("y", *val(UY_E, 3, 0, 0.003))])],
             "<p>B est lu sur la figure : 2,85 m et 1,65 m. La droite (CB) fait 70° avec <var>x</var>, B étant au-dessus "
             "et à gauche de C : <i>u</i> = (−cos 70° ; sin 70°) ≈ (−0,342 ; 0,940).</p>"),
         GRP("q2_2", "Écrire, en leur point d'application, les torseurs des actions mécaniques extérieures sur "
             "l'échelle (forces en daN).",
             "Inconnues : X_A, Y_A et F. Une composante de l'action du vérin s'écrit coefficient × F (ex. −0,5F) ; "
             "une composante nulle s'écrit 0.",
             [TZ("2→3", "A", sym("X_A"), sym("Y_A"), z()),
              TZ("4→3", "B", lin(["F"], UX_E, 0.003), lin(["F"], UY_E, 0.003), z()),
              TZ("P3", "G3", z(), val(-P_E, 0, 0, 0.5), z())],
             "<p>Pivot d'axe (A, <var>z</var>) : <i>X</i><sub>A</sub>, <i>Y</i><sub>A</sub>, moment nul. Rotule en B, "
             "direction connue : <i>F</i> · <i>u</i>, une seule inconnue. Poids vertical. 3 inconnues "
             "(<i>X</i><sub>A</sub>, <i>Y</i><sub>A</sub>, <i>F</i>) pour 3 équations : sans l'isolement du vérin, on en "
             "aurait 4.</p>"),
     ]},
    {"num": "3", "minutes": 30, "title": "PFS au point A et résultats",
     "intro": [],
     "blocks": [
         QBAR("Q3.1 – Q3.4", ["DT1"]),
         GRP("q3_1", "Écrire les trois torseurs au point A (forces en daN, moments en daN·m).",
             "Moments positifs dans le sens trigonométrique ; un moment inconnu s'écrit coefficient × F (au centième).",
             [TZ("2→3", "A", sym("X_A"), sym("Y_A"), z()),
              TZ("4→3", "A", lin(["F"], UX_E, 0.003), lin(["F"], UY_E, 0.003), lin(["F"], D_E, 0.008, 2)),
              TZ("P3", "A", z(), val(-P_E, 0, 0, 0.5), val(MP_E, 0, 0, 0.5))],
             eq("<i>N</i><sub>A</sub>(B) = 2,85 × 0,940 <i>F</i> − 1,65 × (−0,342 <i>F</i>) ≈ <b>3,24 <i>F</i></b> ; "
                "<i>N</i><sub>A</sub>(P3) = 6 × (−5 000) = <b>−30 000</b>") +
             "<p>3,24 m est la distance de A à la droite (BC) : le bras de levier du vérin.</p>"),
         Q("q3_2", "Écrire l'équation des moments en A et en déduire l'intensité <i>F</i> de l'action du vérin.", H_U,
           num(F_E, "daN", relTol=0.002, variants=[var(FN_E, "N", relTol=0.002), var(FN_E / 1000, "kN", relTol=0.002)]),
           f"<i>F</i> ≈ {fr(F_E, 0)} daN",
           eq("3,24 <i>F</i> − 30 000 = 0 ⇒ <i>F</i> = " + frac("30 000", fr(D_E, 3)) + f" ≈ <b>{fr(F_E, 0)} daN</b>")),
         GRP("q3_3", "Donner les actions mécaniques en A et en B.", "Composantes algébriques, arrondies à l'unité, en daN.",
             [VEC(V("A", "2/3"), [("X", *val(AX_E, 0, 0.003)), ("Y", *val(AY_E, 0, 0.003))], "daN"),
              VEC(V("B", "4/3"), [("X", *val(BX_E, 0, 0.003)), ("Y", *val(BY_E, 0, 0.003))], "daN")],
             eq(f"<i>X</i><sub>B</sub> = −0,342 <i>F</i> ≈ {fr(BX_E, 0)} ; <i>Y</i><sub>B</sub> = 0,940 <i>F</i> ≈ {fr(BY_E, 0)}") +
             eq(f"Σ<i>X</i> = 0 ⇒ <i>X</i><sub>A</sub> ≈ {fr(AX_E, 0)} ; Σ<i>Y</i> = 0 ⇒ <i>Y</i><sub>A</sub> = 5 000 − "
                f"{fr(BY_E, 0)} ≈ {fr(AY_E, 0)}") +
             "<p><i>Y</i><sub>A</sub> &lt; 0 : la tourelle retient l'échelle vers le bas, le vérin poussant plus fort "
             "que le poids.</p>"),
         Q("q3_4", f"Calculer la norme ‖{V('A', '2/3')}‖.", H_U,
           num(NA_E, "daN", relTol=0.003, variants=[var(NA_E * 10, "N", relTol=0.003)]), f"≈ {fr(NA_E, 0)} daN",
           eq(f"‖{V('A', '2/3')}‖ = " + sqrt(f"{fr(AX_E, 0)}² + ({fr(AY_E, 0)})²") + f" ≈ <b>{fr(NA_E, 0)} daN</b>")),
     ]},
    {"num": "4", "minutes": 10, "title": "Pression d'alimentation du vérin",
     "intro": ["<p>Le diamètre du piston du vérin est de 100 mm ; l'huile agit sur toute la surface du piston.</p>"],
     "blocks": [
         QBAR("Q4.1 – Q4.2", ["DT1"]),
         Q("q4_1", "Calculer la surface <i>S</i> du piston.", H_C,
           num(S_E, "mm2", relTol=0.001, variants=[var(S_E / 100, "cm2", relTol=0.001)]), f"<i>S</i> ≈ {fr(S_E)} mm²",
           eq("<i>S</i> = " + frac("π × 100²", "4") + f" ≈ <b>{fr(S_E)} mm²</b>")),
         Q("q4_2", "Calculer la pression d'alimentation <i>p</i> nécessaire.", H_C,
           num(PR_E, "MPa", relTol=0.003, variants=[var(PR_E * 10, "bar", relTol=0.003), var(PR_E * 1e6, "Pa", relTol=0.003)]),
           f"<i>p</i> ≈ {fr(PR_E)} MPa (≈ {fr(PR_E * 10, 1)} bar)",
           eq("<i>p</i> = " + frac("<i>F</i>", "<i>S</i>") + " = " + frac(fr(FN_E, 0) + " N", fr(S_E) + " mm²") +
              f" ≈ <b>{fr(PR_E)} MPa</b> ≈ {fr(PR_E * 10, 1)} bar") + "<p>Attention : <i>F</i> en newtons (1 daN = 10 N).</p>"),
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

CB_V, SB_V = math.cos(BETA), math.sin(BETA)
NE_A_V = (XE_V - XA_V) * (-SB_V) - YE_V * (-CB_V)     # moment en A de E3/2 = coefficient × E

PARTS_VELO = [
    {"num": "1", "minutes": 15, "title": "Graphe des liaisons",
     "intro": [
         "<p>Le cadre d'un vélo tout terrain est réalisé en deux parties <strong>(1)</strong> et <strong>(2)</strong> "
         "articulées en A (pivot d'axe (A, <var>z</var>)). Un amortisseur <strong>(3)</strong> est articulé en E sur "
         f"(2) et en F sur (1). Le poids {V('P')} = 1 000 N du cycliste, vertical, est supposé appliqué en D. "
         f"{V('B')} et {V('C')} sont les actions des roues sur le cadre ; les autres poids et actions sont négligés.</p>",
         figure("n3-velo-cadre", "Cadre de VTT : cadre avant 1, bras arrière 2, amortisseur 3 entre E et F ; poids "
                "P de 1 000 N en D, actions verticales B et C des roues ; cotes 242, 188 et 672 mm ; droite CEF à "
                "35,5°", "Figure 1 — Cadre de vélo tout terrain (cotes en mm).", 760),
     ],
     "blocks": [
         QBAR("Q1.1", ["DP1"], ans="sur la figure"),
         SK("sk_q1_1", "Q1.1", "GRAPHE_VELO",
            "Réaliser le graphe des liaisons des solides (1), (2) et (3) et nommer chaque liaison. Les actions "
            "extérieures (cycliste, roues) sont déjà placées.",
            ["Trois liaisons sont tracées : 1–2, 2–3 et 3–1 (le graphe forme une boucle fermée).",
             "La liaison 1–2 est nommée « pivot d'axe (A, z) ».",
             "La liaison 2–3 est nommée « pivot (ou rotule) en E ».",
             "La liaison 3–1 est nommée « pivot (ou rotule) en F »."],
            "<p>Outils : <b>Ligne</b> pour relier deux solides, <b>Texte</b> pour nommer la liaison et son centre.</p>" +
            figure("n3-velo-amortisseur", "Amortisseur 3 articulé en E et F, incliné de 35,5°", "L'amortisseur (3).", 200),
            "<p>Trois liaisons en boucle fermée : 1–2 <strong>pivot d'axe (A, <var>z</var>)</strong>, 2–3 <strong>pivot "
            "d'axe (E, <var>z</var>)</strong>, 3–1 <strong>pivot d'axe (F, <var>z</var>)</strong>.</p>"),
     ]},
    {"num": "2", "minutes": 20, "title": "Isolement du cadre complet (1 + 2 + 3)",
     "intro": ["<p>On isole le cadre complet. Repère (C, <var>x</var>, <var>y</var>) : origine C, <var>x</var> "
               "horizontal vers l'avant, <var>y</var> vertical vers le haut. C, A et B sont sur l'axe <var>x</var>. "
               f"On note <i>Y</i><sub>B</sub> et <i>Y</i><sub>C</sub> les composantes de {V('B')} et {V('C')}.</p>"],
     "blocks": [
         QBAR("Q2.1 – Q2.3", ["DP1", "DT1"]),
         GRP("q2_1", "Écrire, en leur point d'application, les torseurs des actions extérieures sur le cadre complet "
             "(forces en N).", H_TZ.replace("X_A, Y_B…", "Y_B, Y_C…"),
             [TZ("P", "D", z(), val(-P_V, 0, 0, 0.5), z()),
              TZ("roue AV→1", "B", z(), sym("Y_B"), z()),
              TZ("roue AR→2", "C", z(), sym("Y_C"), z())],
             "<p>Trois forces verticales. Les actions de l'amortisseur et du pivot A sont intérieures au cadre "
             "complet : elles n'apparaissent pas. 2 inconnues, et l'équation Σ<i>X</i> = 0 est toujours vérifiée.</p>"),
         GRP("q2_2", "Écrire ces trois torseurs au point C (forces en N, moments en N·mm).",
             "Moments positifs dans le sens trigonométrique ; un moment inconnu s'écrit coefficient × inconnue (ex. 500Y_B).",
             [TZ("P", "C", z(), val(-P_V, 0, 0, 0.5), val(MP_V, 0, 0, 0.5)),
              TZ("roue AV→1", "C", z(), sym("Y_B"), lin(["Y_B", "B"], XB_V, 0.5, 0)),
              TZ("roue AR→2", "C", z(), sym("Y_C"), z())],
             eq("<i>N</i><sub>C</sub>(P) = 242 × (−1 000) = −242 000 ; <i>N</i><sub>C</sub>(B) = 1 102 <i>Y</i><sub>B</sub> "
                "(<i>x</i><sub>B</sub> = 242 + 188 + 672 = 1 102 mm) ; <i>N</i><sub>C</sub>(C) = 0")),
         GRP("q2_3", "Résoudre et donner les actions des roues.", "Valeurs arrondies au centième, en N.",
             [VEC("Composantes", [("Y<sub>B</sub>", *val(B_V, 2, 0, 0.006)), ("Y<sub>C</sub>", *val(C_V, 2, 0, 0.006))], "N")],
             eq("1 102 <i>Y</i><sub>B</sub> − 242 000 = 0 ⇒ <i>Y</i><sub>B</sub> = " + frac("242 000", "1 102") +
                f" ≈ <b>{fr(B_V)} N</b> ; <i>Y</i><sub>C</sub> = 1 000 − {fr(B_V)} ≈ <b>{fr(C_V)} N</b>")),
     ]},
    {"num": "3", "minutes": 10, "title": "Isolement de l'amortisseur (3)",
     "intro": [figure("n3-velo-amortisseur", "Amortisseur 3 entre E et F, incliné de 35,5° sur l'horizontale",
                      "Figure 2 — Amortisseur (3).", 240)],
     "blocks": [
         QBAR("Q3.1 – Q3.2", ["DP1", "DT1"]),
         Q("q3_1", "Isoler l'amortisseur (3) : quelle est la droite d'action de l'action mécanique en E ?", H_DROITE,
           DROITE("E", "F"), "la droite (EF)",
           "<p>Deux forces seulement (poids négligé) : droite d'action <strong>(EF)</strong>, inclinée de 35,5°.</p>"),
         Q("q3_2", "Cette droite passe par un autre point remarquable du vélo. Lequel ?", H_POINT, POINT("C"), "le point C",
           "<p>C, E et F sont alignés : l'action de l'amortisseur sur le bras arrière passe par C.</p>"),
     ]},
    {"num": "4", "minutes": 25, "title": "Isolement du bras arrière (2)",
     "intro": [
         '<div class="n3-split">' +
         figure("n3-velo-arriere", "Bras arrière 2 isolé : C, A à 430 mm sur l'axe x, E à 393 mm de C en x, sur la "
                "droite CEF à 35,5°", "Figure 3 — Bras arrière (2) isolé.", 340) +
         "<p>On isole le bras arrière (2), repère (C, <var>x</var>, <var>y</var>). L'amortisseur, comprimé, pousse "
         "le bras en E vers C ; on note <i>E</i> l'intensité de cette action et <i>X</i><sub>A</sub>, "
         "<i>Y</i><sub>A</sub> les composantes de l'action du cadre (1) en A.</p></div>",
     ],
     "blocks": [
         QBAR("Q4.1 – Q4.5", ["DT1"]),
         GRP("q4_1", "Donner les coordonnées de A et de E (en mm) et le vecteur unitaire <i>u</i> de l'action de "
             "l'amortisseur sur le bras (dirigé de F vers C).", "Coordonnées au centième, composantes de <i>u</i> au millième.",
             [VEC("A", [("x", *val(XA_V, 2, 0, 0.05)), ("y", *val(0, 0, 0, 0.05))], "mm"),
              VEC("E", [("x", *val(XE_V, 2, 0, 0.05)), ("y", *val(YE_V, 2, 0, 0.03))], "mm"),
              VEC("<i>u</i>", [("x", *val(-CB_V, 3, 0, 0.003)), ("y", *val(-SB_V, 3, 0, 0.003))])],
             f"<p>A (430 ; 0) ; E (393 ; 393 × tan 35,5° ≈ {fr(YE_V)}) ; <i>u</i> = (−cos 35,5° ; −sin 35,5°) ≈ "
             f"({fr(-CB_V, 3)} ; {fr(-SB_V, 3)}).</p>"),
         GRP("q4_2", "Écrire les trois torseurs au point A (forces en N, moments en N·mm).",
             "Inconnues : X_A, Y_A et E ; une composante de l'action de l'amortisseur s'écrit coefficient × E (au millième "
             "pour les forces, au dixième pour le moment). La valeur de Y_C est celle de Q2.3.",
             [TZ("roue AR→2", "A", z(), val(C_V, 2, 0, 0.06), val(MC_V, 0, 0.002)),
              TZ("1→2", "A", sym("X_A"), sym("Y_A"), z()),
              TZ("3→2", "A", lin(["E"], -CB_V, 0.003), lin(["E"], -SB_V, 0.003), lin(["E"], NE_A_V, 0.6, 1))],
             "<p>Avec <span class=\"vec\">AC</span> (−430 ; 0) et <span class=\"vec\">AE</span> (−37 ; 280,32) :</p>" +
             eq(f"<i>N</i><sub>A</sub>(C) = −430 × {fr(C_V)} ≈ {fr(MC_V, 0)} ; <i>N</i><sub>A</sub>(E) = (−37)(−0,581 <i>E</i>) − "
                f"280,32 × (−0,814 <i>E</i>) ≈ <b>{fr(NE_A_V, 1)} <i>E</i></b>") +
             "<p>249,7 mm est la distance de A à la droite (CE) : 430 × sin 35,5°.</p>"),
         Q("q4_3", "En déduire l'intensité <i>E</i> de l'effort de compression dans l'amortisseur.", H_D,
           num(E_V, "N", relTol=0.002, variants=[var(E_V / 10, "daN", relTol=0.002)]), f"<i>E</i> ≈ {fr(E_V, 1)} N",
           eq(f"Σ<i>N</i><sub>A</sub> = 0 : {fr(NE_A_V, 1)} <i>E</i> + ({fr(MC_V, 0)}) = 0 ⇒ <i>E</i> ≈ <b>{fr(E_V, 1)} N</b>")),
         GRP("q4_4", "Donner l'action du cadre (1) sur le bras (2) en A.", "Composantes algébriques au dixième, en N.",
             [VEC(V("A", "1/2"), [("X", *val(AX_V, 1, 0.002)), ("Y", *val(0, 0, 0, 1.0))], "N")],
             eq(f"Σ<i>X</i> = 0 : <i>X</i><sub>A</sub> − 0,814 <i>E</i> = 0 ⇒ <i>X</i><sub>A</sub> ≈ <b>{fr(AX_V, 1)} N</b>") +
             eq(f"Σ<i>Y</i> = 0 : <i>Y</i><sub>A</sub> + {fr(C_V)} − 0,581 <i>E</i> = 0 ⇒ <i>Y</i><sub>A</sub> = <b>0</b>") +
             "<p>Vérification : trois forces non parallèles sont concourantes ; C et E passent par C, donc A aussi : "
             "l'action en A est portée par (AC), horizontale.</p>"),
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
DR_NAMES = {"GRAPHE_COFFRE": ("DR1", "Q1.1", "Graphe des liaisons de la porte de coffre-fort"),
            "GRAPHE_VELO": ("DR1", "Q1.1", "Graphe des liaisons du cadre de vélo")}


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
                <p class="se-title">Auto-évaluation — {n} points sur les {fpts(total_pts)} de la partie {part['num']}</p>
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


def grp_cells(b):
    """Cases d'un groupe : (identifiant, nom affiché, grader, texte attendu)."""
    out, k = [], 0
    for it in b["items"]:
        for lab, g, txt in it["cells"]:
            k += 1
            out.append((f"{b['id']}_{k}", f"{it['nom']} {lab}", g, txt))
    return out


def block_points(b):
    if b["kind"] == "q":
        return 1
    if b["kind"] == "sk":
        return len(b["criteria"])
    if b["kind"] == "grp":
        return b["pts"] * len(grp_cells(b))
    return 0


def part_points(p):
    t = sum(block_points(b) for b in p["blocks"])
    return int(t) if t == int(t) else t


def fpts(x):
    """Nombre de points à la française : 19, 7,5."""
    return str(int(x)) if x == int(x) else fr(x, 1)


def _tz_html(nom, point, cells, unite=""):
    """Torseur plan affiché : cellules X, Y (résultante) et N (moment) ; les autres sont des tirets."""
    c = {lab: html_ for lab, html_ in cells}
    rows = [(c["X"], "—"), (c["Y"], "—"), ("—", c["N"])]
    body = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    return (f'<span class="torseur tzq-t"><span class="tz-n">{{<i>T</i><sub>{nom}</sub>}}<sub>{point}</sub> =</span>'
            f'<span class="tz-b"><table>{body}</table></span><span class="tz-r">({point}, x, y, z){unite}</span></span>')


def _vec_html(nom, cells, unite=""):
    inner = " ; ".join(f'<span class="vc"><span class="vc-l">{lab}</span>{h}</span>' for lab, h in cells)
    return f'<span class="vecq"><span class="vecq-n">{nom}</span> = ( {inner} ){(" " + unite) if unite else ""}</span>'


def render_grp(b):
    cells = grp_cells(b)
    by_item, k = [], 0
    for it in b["items"]:
        row = []
        for lab, g, txt in it["cells"]:
            cid, clab = cells[k][0], cells[k][1]
            k += 1
            inp = (f'<span class="sol"><input type="text" data-q="{cid}" aria-label="{esc(b["label"] + " " + clab)}" '
                   f'autocomplete="off" autocapitalize="off" spellcheck="false"><span class="mark"></span></span>')
            row.append((lab, inp))
        if it["kind"] == "tz":
            by_item.append(_tz_html(it["nom"], it["point"], row))
        else:
            by_item.append(_vec_html(it["nom"], row, it.get("unite", "")))
    attendu = []
    for it in b["items"]:
        row = [(lab, txt) for lab, g, txt in it["cells"]]
        attendu.append(_tz_html(it["nom"], it["point"], row) if it["kind"] == "tz" else
                       _vec_html(it["nom"], row, it.get("unite", "")))
    n = len(cells)
    return f"""
        <div class="fast-q tzq" id="{b['id']}">
          <p class="q-stem"><span class="q-num">{b['label']}</span> <strong>{b['stem']}</strong></p>
          <p class="q-hint">{b['hint']}</p>
          <div class="tzq-items">{"".join(f'<div class="tzq-item">{h}</div>' for h in by_item)}</div>
          <div class="fast-foot"><button type="button" class="btn btn-fast" data-done="Saisie validée">Valider les {n} cases</button>
            <span class="q-status" aria-live="polite"></span></div>
          <p class="q-msg" role="alert"></p>
          <div class="q-expl" hidden><p class="q-expected"><span>Réponse attendue :</span></p>
            <div class="tzq-items tzq-att">{"".join(f'<div class="tzq-item">{h}</div>' for h in attendu)}</div>
            <div class="q-why">{b['why']}</div></div>
        </div>"""


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
        elif b["kind"] == "grp":
            blocks.append(render_grp(b))
    n = p["num"]
    pct = fr(p["minutes"] / total_min * 100, 1)
    return f"""
  <section class="part" id="partie-{n}" aria-labelledby="t-partie-{n}">
    <header class="part-head"><div class="part-num" aria-hidden="true">{n}</div>
      <div><h2 id="t-partie-{n}"><span class="sr-only">Partie {n} : </span>{p['title']}</h2>
        <div class="duree">Durée conseillée : {hm(p['minutes'])} · Barème : {fpts(pts)} points, soit {pct} % de la note</div></div></header>
    <div class="part-body">
      {"".join(p["intro"])}{"".join(blocks)}
    </div>
  </section>"""


def check_parts(parts):
    """Libellés et cohérence : identifiants qN_M rangés dans la partie N, sans doublon."""
    seen = set()
    for p in parts:
        for b in p["blocks"]:
            if b["kind"] in ("q", "sk", "grp"):
                qid = b["id"][3:] if b["kind"] == "sk" else b["id"]
                assert qid not in seen, f"identifiant en double : {qid}"
                seen.add(qid)
                assert qid.startswith(f"q{p['num']}_"), f"{qid} rangé dans la partie {p['num']}"
                b["label"] = label_of(qid)


TZ_JS = r"""<script>/* Correcteur « expression linéaire » (coefficient × inconnue) des cases de torseurs : il s'ajoute aux types
   du moteur Grading sans le modifier. Accepte −2,1X_A, -2.1*XA, XA×(-2,1), 3,24 F… */
(function () {
  "use strict";
  if (typeof Grading === "undefined" || Grading.__lin) return;
  var base = Grading.grade;
  function norm(s) {
    return String(s).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      .replace(/[\u2212\u2013\u2014]/g, "-").replace(/,/g, ".").replace(/[\s\u00a0\u202f×*·⋅_()]/g, "");
  }
  function gradeLin(ans, g) {
    var s = norm(ans), m, sign = 1, k = null, v = null;
    if ((m = s.match(/^([+-]?)(\d*\.?\d*)([a-z]+)$/))) { sign = m[1] === "-" ? -1 : 1; k = m[2]; v = m[3]; }
    else if ((m = s.match(/^([+-]?)([a-z]+)([+-]?\d*\.?\d+)$/))) { sign = m[1] === "-" ? -1 : 1; v = m[2]; k = m[3]; }
    else return { ok: false };
    if (g.vars.indexOf(v) < 0) return { ok: false };
    var c = k === "" || k === "." ? 1 : parseFloat(k);
    if (!isFinite(c)) return { ok: false };
    c *= sign;
    return { ok: Math.abs(c - g.coef) <= (g.absTol || 0) + 1e-9 };
  }
  Grading.grade = function (ans, g) {
    if (g && g.type === "lin") {
      if (ans == null || !String(ans).trim()) return { ok: false, score: 0, invalid: "Saisis une réponse avant de valider." };
      var r = gradeLin(ans, g); r.score = r.ok ? 1 : 0; return r;
    }
    return base(ans, g);
  };
  Grading.__lin = true;
})();
</script>"""

TZ_CSS = """
/* ---------- torseurs et vecteurs à compléter ---------- */
.tzq{margin:14px 0 6px; padding:10px 0 12px 14px; border-left:3px solid var(--trait)}
.tzq.is-ok{border-left-color:var(--vert)}
.tzq-items{display:flex; flex-wrap:wrap; gap:14px 26px; align-items:center; margin:8px 0}
.tzq-item{max-width:100%; overflow-x:auto}
.tzq .tz-b td{padding:2px 6px; vertical-align:top}
.tzq .sol{display:inline-flex; flex-direction:column; align-items:center}
.tzq .sol input{width:7.6em; border:1.5px dashed var(--encre-2); padding:5px 6px; background:#fff; font:600 .95rem var(--f-texte); text-align:center}
.tzq .sol.is-ok input{border:2px solid var(--vert); background:var(--vert-pale)}
.tzq .sol.is-ko input{border:2px solid var(--rouge); background:var(--rouge-pale)}
.tzq .sol input:disabled{color:var(--encre); -webkit-text-fill-color:var(--encre)}
.tzq .sol .mark{display:block; font-size:.72rem; font-weight:700; min-height:1em}
.tzq .sol.is-ok .mark{color:var(--vert)} .tzq .sol.is-ko .mark{color:var(--rouge)}
.vecq{display:inline-flex; align-items:center; gap:6px; flex-wrap:wrap; font-size:1.02rem}
.vecq-n{font-weight:700}
.vc{display:inline-flex; flex-direction:column; align-items:center; gap:1px}
.vc-l{font-size:.75rem; color:var(--encre-2)}
.tzq-att .vc-l{display:none}
.tzq-att{background:#fff; border:1px solid var(--trait-fin); padding:6px 10px}
.tzq .q-status{font-weight:700}
@media print{ .tzq .sol input{border:1px solid #555!important} }
"""

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
__TZ_CSS__
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
    n_q = sum(1 for p in parts for b in p["blocks"] if b["kind"] in ("q", "grp"))
    n_grp = sum(1 for p in parts for b in p["blocks"] if b["kind"] == "grp")
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
    # le libellé du bouton d'une question groupée validée dépend du sujet (torseurs, vecteurs, diagramme)
    app = sub_once(app, r'btn\.textContent = "Diagramme validé";',
                   'btn.textContent = btn.getAttribute("data-done") || "Diagramme validé";')

    parts_cfg, qcfg, skcfg = [], {}, {}
    for p in parts:
        parts_cfg.append({"num": p["num"], "title": p["title"], "minutes": p["minutes"], "duration": hm(p["minutes"]),
                          "points": part_points(p)})
        for b in p["blocks"]:
            if b["kind"] == "q":
                qcfg[b["id"]] = {"label": b["label"], "part": p["num"], "pts": 1, "grader": b["grader"]}
            elif b["kind"] == "grp":
                for cid, clab, gr, _t in grp_cells(b):
                    qcfg[cid] = {"label": f"{b['label']} ({re.sub(r'<[^>]+>', '', clab)})", "part": p["num"],
                                 "pts": b["pts"], "grader": gr}
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
    cartouche = (f"{n_q} questions notées" + (f", dont {n_grp} torseurs et vecteurs à compléter case par case" if n_grp else
                                                " (unités comprises)") +
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
{CONTENT_CSS.replace("__TZ_CSS__", TZ_CSS)}
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
{TZ_JS}
{e.get("extra_js", "")}
</body>
</html>
"""
    stats = {"n_q": n_q, "n_sk": n_sk, "minutes": total, "points": sum(part_points(p) for p in parts),
             "parts": len(parts)}
    return page, stats

