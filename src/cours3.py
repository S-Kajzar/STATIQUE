#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cours 3 (Niveau 3) — Statique analytique, page autonome et interactive.

Contenu repris de la séquence « Statique analytique » : rappel du PFS (énoncé, solide soumis à deux forces,
généralisation par les torseurs), torseur d'action mécanique transmissible par une liaison, hypothèse du
problème plan, méthode de résolution. Les cases à compléter du document d'origine deviennent des cartes à
retourner ; les tableaux « degrés de liberté → torseur » deviennent un atelier interactif. S'y ajoutent une
balance (R = −P), un jeu « équilibre ou pas ? », un calculateur de moment, un simulateur de poutre résolu pas à
pas et un quiz. Appelé par src/generer.py.
"""
from niveau3 import HOUSE, esc, figure, frac, tz

# ============================================================ données
LIAISONS = [
    # clé, nom, ddl (Tx Ty Tz Rx Ry Rz : 1 = libre), description
    ("ponctuelle", "Ponctuelle de normale y", "101111",
     "Une sphère posée sur un plan : seul le déplacement selon la normale y est empêché."),
    ("pivot", "Pivot d'axe z", "000001", "Un arbre dans un palier avec épaulements : seule la rotation autour de z reste."),
    ("glissiere", "Glissière d'axe x", "100000", "Un tiroir dans ses rails : seule la translation selon x reste."),
    ("pivotglissant", "Pivot glissant d'axe x", "100100", "Un arbre long dans un alésage : il tourne et coulisse selon x."),
    ("rotule", "Rotule de centre O", "000111", "Une sphère dans une sphère creuse : les trois rotations restent."),
    ("lannulaire", "Linéaire annulaire d'axe x", "100111", "Une sphère dans un cylindre d'axe x : translation x et trois rotations."),
    ("lrectiligne", "Linéaire rectiligne de normale y, ligne x", "101110",
     "Un cylindre posé sur un plan, contact selon une ligne x : il glisse selon x et z, roule autour de x et pivote autour de y."),
    ("appuiplan", "Appui plan de normale y", "101010", "Deux surfaces planes en contact : glissement selon x et z, rotation autour de y."),
    ("encastrement", "Encastrement", "000000", "Deux pièces soudées ou boulonnées : aucun mouvement."),
]
COMP = ["X", "Y", "Z", "L", "M", "N"]

JEU_DEUX = [
    # (description, équilibre ?, explication, svg)
    ("Même droite d'action, même intensité, sens contraires", True,
     "Les trois conditions sont réunies : le solide reste immobile.", "ok"),
    ("Droites d'action parallèles, même intensité, sens contraires", False,
     "La somme des forces est nulle mais elles forment un couple : le solide tourne.", "couple"),
    ("Même droite d'action, sens contraires, intensités différentes", False,
     "La somme des forces n'est pas nulle : le solide part dans le sens de la plus grande.", "inegal"),
    ("Même droite d'action, même intensité, même sens", False,
     "Les forces s'ajoutent : le solide est entraîné dans leur sens.", "meme"),
]

JEU_PLAN = [
    ("Pivot d'axe z", 2, "X et Y : le moment N est nul (rotation libre autour de z)."),
    ("Ponctuelle de normale y", 1, "Y seulement : la force est portée par la normale au contact."),
    ("Glissière d'axe x", 2, "Y et N : la translation selon x est libre, la rotation autour de z bloquée."),
    ("Encastrement", 3, "X, Y et N : tout est bloqué."),
    ("Rotule de centre O", 2, "X et Y : aucune rotation n'est bloquée, donc N = 0."),
    ("Linéaire annulaire d'axe y", 1, "X seulement : translation libre selon y, rotations libres."),
    ("Appui plan de normale y", 2, "Y et N : glissement selon x libre, rotation autour de z bloquée."),
]

QUIZ = [
    ("Un solide est en équilibre sous l'action de deux forces. Elles ont nécessairement…",
     ["la même direction, la même intensité et des sens contraires", "la même intensité seulement",
      "des directions perpendiculaires"], 0,
     "Deux forces en équilibre sont directement opposées : même droite d'action, même intensité, sens contraires."),
    ("Combien d'équations scalaires le PFS fournit-il pour un problème plan ?", ["2", "3", "6"], 1,
     "Σ<i>X</i> = 0, Σ<i>Y</i> = 0 et Σ<i>N</i> = 0 : trois équations (six dans l'espace)."),
    ("Une liaison laisse libre la rotation autour de z. Dans son torseur…", ["X = 0", "N = 0", "Z = 0"], 1,
     "Un mouvement libre correspond à une composante nulle : rotation libre autour de z ⇒ moment N nul."),
    ("Dans le plan (x, y), combien d'inconnues transmet une liaison pivot d'axe z ?", ["1", "2", "3"], 1,
     "<i>X</i> et <i>Y</i> : la force passe par le centre de la liaison, le moment <i>N</i> est nul."),
    ("Où vaut-il mieux écrire l'équation des moments ?",
     ["au point où l'action a le plus d'inconnues", "toujours à l'origine du repère", "au centre de gravité"], 0,
     "Les inconnues de l'action en ce point ont un moment nul : elles disparaissent de l'équation."),
    ("Une force (0 ; −100 N) est appliquée au point (2 m ; 0). Son moment en l'origine vaut…",
     ["+200 N·m", "−200 N·m", "−50 N·m"], 1, "<i>M</i> = <i>x</i> · <i>F</i><sub>y</sub> − <i>y</i> · <i>F</i><sub>x</sub> = 2 × (−100) − 0 = −200 N·m (sens horaire)."),
    ("Le problème compte 4 inconnues dans le plan. On peut…",
     ["le résoudre directement", "chercher une simplification (solide soumis à deux forces…)", "ignorer une inconnue"], 1,
     "4 inconnues pour 3 équations : il faut d'abord isoler un autre solide (souvent un solide soumis à deux forces) pour "
     "connaître une direction."),
    ("Pour déplacer un torseur du point A au point B…",
     ["la résultante et le moment ne changent pas", "la résultante est conservée, le moment devient M_A + BA ∧ R",
      "le moment est conservé, la résultante change"], 1,
     "La résultante est la même en tout point ; le moment se transporte par la relation de Varignon (« BABAR »)."),
]


# ============================================================ petites figures en SVG
def _svg_deux(kind):
    """Barre et deux forces, pour le jeu « équilibre ou pas ? »."""
    bar = '<rect x="50" y="42" width="140" height="26" rx="13" fill="#D9E4F2" stroke="#1C2530" stroke-width="2"/>'
    mk = '<marker id="ah-{0}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#C62828"/></marker>'.format(kind)
    a = f'marker-end="url(#ah-{kind})" stroke="#C62828" stroke-width="3.5"'
    if kind == "ok":
        fl = f'<line x1="60" y1="55" x2="8" y2="55" {a}/><line x1="180" y1="55" x2="232" y2="55" {a}/>'
    elif kind == "couple":
        fl = f'<line x1="60" y1="45" x2="10" y2="45" {a}/><line x1="180" y1="65" x2="230" y2="65" {a}/>'
    elif kind == "inegal":
        fl = f'<line x1="60" y1="55" x2="30" y2="55" {a}/><line x1="180" y1="55" x2="236" y2="55" {a}/>'
    else:
        fl = f'<line x1="60" y1="55" x2="8" y2="55" {a}/><line x1="180" y1="55" x2="128" y2="55" {a}/>'
    return (f'<svg viewBox="0 0 240 110" class="deux-svg" role="img" aria-label="Barre soumise à deux forces">'
            f'<defs>{mk}</defs>{bar}{fl}</svg>')


BALANCE_SVG = """<svg class="bal-svg" viewBox="0 0 320 300" role="img" aria-labelledby="bal-t">
<title id="bal-t">Bloc posé sur le sol : son poids P et la réaction R du sol</title>
<defs><marker id="bal-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker>
<pattern id="bal-h" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8" stroke="#46525C" stroke-width="1.4"/></pattern></defs>
<rect x="20" y="160" width="280" height="22" fill="url(#bal-h)"/><line x1="20" y1="160" x2="300" y2="160" stroke="#1C2530" stroke-width="2"/>
<rect id="bal-bloc" x="100" y="120" width="120" height="40" fill="#D9E4F2" stroke="#1C2530" stroke-width="2"/>
<line id="bal-r" x1="160" y1="160" x2="160" y2="80" stroke="#1F5FA8" stroke-width="4" marker-end="url(#bal-ah)"/>
<line id="bal-p" x1="160" y1="140" x2="160" y2="220" stroke="#C62828" stroke-width="4" marker-end="url(#bal-ah)"/>
<circle cx="160" cy="140" r="4" fill="#1C2530"/><circle cx="160" cy="160" r="4" fill="#1C2530"/>
<text id="bal-rt" x="172" y="92" class="lab-b">R</text><text id="bal-pt" x="172" y="226" class="lab-r">P</text>
</svg>"""

MOMENT_SVG = """<svg class="mom-svg" viewBox="0 0 520 330" role="img" aria-labelledby="mom-t">
<title id="mom-t">Force F appliquée en P et son moment par rapport au point A</title>
<defs><marker id="mom-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>
<g class="grille" id="mom-grille"></g>
<line x1="20" y1="210" x2="505" y2="210" class="axe" marker-end="url(#mom-ah)"/><text x="500" y="228" class="ax">x</text>
<line x1="80" y1="315" x2="80" y2="15" class="axe" marker-end="url(#mom-ah)"/><text x="90" y="20" class="ax">y</text>
<line id="mom-ligne" class="ligne-action"/>
<line id="mom-d" class="bras"/><text id="mom-dt" class="lab-v">d</text>
<line id="mom-ap" class="ap"/>
<path id="mom-arc" fill="none" stroke-width="3" marker-end="url(#mom-ah)"/>
<line id="mom-f" stroke="#C62828" stroke-width="4" marker-end="url(#mom-ah)"/>
<circle cx="80" cy="210" r="5" fill="#1C2530"/><text x="62" y="230" class="pt">A</text>
<circle id="mom-p" r="5" fill="#1C2530"/><text id="mom-pt" class="pt">P</text><text id="mom-ft" class="lab-r">F</text>
</svg>"""

POUTRE_SVG = """<svg class="pou-svg" viewBox="0 30 580 268" role="img" aria-labelledby="pou-t">
<title id="pou-t">Poutre AB de 4 m : pivot en A, appui ponctuel en B, charge F inclinée</title>
<defs><marker id="pou-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker>
<pattern id="pou-h" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#46525C" stroke-width="1.3"/></pattern></defs>
<rect x="70" y="146" width="440" height="16" fill="#D9E4F2" stroke="#1C2530" stroke-width="2"/>
<path d="M70 162 56 190 84 190Z" fill="#fff" stroke="#1C2530" stroke-width="2"/><rect x="44" y="190" width="52" height="10" fill="url(#pou-h)"/>
<circle cx="70" cy="162" r="4" fill="#1C2530"/>
<circle cx="510" cy="175" r="12" fill="#fff" stroke="#1C2530" stroke-width="2"/><rect x="484" y="187" width="52" height="10" fill="url(#pou-h)"/>
<line x1="484" y1="187" x2="536" y2="187" stroke="#1C2530" stroke-width="2"/>
<text x="44" y="214" class="pt">A</text><text x="530" y="214" class="pt">B</text>
<line x1="70" y1="276" x2="510" y2="276" stroke="#9AA2A8" stroke-width="1"/><text x="275" y="290" class="ax">L = 4 m</text>
<line id="pou-xa" stroke="#1F5FA8" stroke-width="4" marker-end="url(#pou-ah)"/><text id="pou-xat" class="lab-b" x="4" y="128"></text>
<line id="pou-ya" stroke="#1F5FA8" stroke-width="4" marker-end="url(#pou-ah)"/><text id="pou-yat" class="lab-b" x="82" y="240"></text>
<line id="pou-yb" stroke="#1B7A43" stroke-width="4" marker-end="url(#pou-ah)"/><text id="pou-ybt" class="lab-g" x="498" y="240" text-anchor="end"></text>
<line id="pou-f" stroke="#C62828" stroke-width="4" marker-end="url(#pou-ah)"/><text id="pou-ft" class="lab-r">F</text>
<circle id="pou-pt" r="4" fill="#C62828"/>
</svg>"""


def _sec(n, ident, titre, body):
    return (f'<section class="part cours-sec" id="{ident}" aria-labelledby="{ident}-t"><header class="part-head">'
            f'<div class="part-num" aria-hidden="true">{n}</div><div><h2 id="{ident}-t" style="padding:14px 16px">{titre}'
            f'</h2></div></header><div class="part-body">{body}</div></section>')


def _carte(titre, recto, verso):
    return (f'<button type="button" class="k3-carte" aria-expanded="false"><b>{titre}</b><span class="k3-q">{recto}</span>'
            f'<span class="k3-dos">{verso}</span></button>')


def _vec(l, i=""):
    return f'<span class="vec">{l}</span>' + (f"<sub>{i}</sub>" if i else "")


# ============================================================ rendu
def render_cours3(style, hub_css):
    nav_items = [("k3-pfs", "Le PFS"), ("k3-deux", "Deux forces"), ("k3-gen", "Généralisation"),
                 ("k3-tor", "Torseurs des liaisons"), ("k3-plan", "Problème plan"), ("k3-mom", "Moments"),
                 ("k3-meth", "Méthode"), ("k3-quiz", "Quiz")]
    nav = "".join(f'<a href="#{a}">{n}. {t}</a>' for n, (a, t) in enumerate(nav_items, 1))

    s1 = _sec(1, "k3-pfs", "Rappel du principe fondamental de la statique",
              "<p>La <b>statique</b> est la partie de la mécanique qui étudie l'<b>équilibre des systèmes matériels</b> "
              "(un solide ou un ensemble de solides) <b>au repos</b> par rapport à un repère fixe. Son but : connaître les "
              "forces qui existent dans un mécanisme pour le <b>dimensionner</b> correctement.</p>"
              '<div class="cours-split"><div class="bal">' + BALANCE_SVG +
              '<label class="bal-l"><span>Masse du bloc : <output id="bal-m">50 kg</output></span>'
              '<input type="range" id="bal-in" min="10" max="150" step="5" value="50"></label></div>'
              "<div><p>Un solide immobile voit son poids <b>compensé</b> par une résultante directement opposée : la "
              "réaction du sol.</p>"
              f'<div class="formule"><span class="f-main">{_vec("R")} = −{_vec("P")} &nbsp;ou&nbsp; {_vec("R")} + '
              f'{_vec("P")} = {_vec("0")}</span></div>'
              '<p class="bal-out">P = <b id="bal-p-v">490,5 N</b> ; R = <b id="bal-r-v">490,5 N</b></p>'
              '<p class="cours-defi">À toi : change la masse. Les deux flèches restent-elles égales ?</p>'
              "<p class=\"small\">Cette relation est une conséquence du principe fondamental de la statique (PFS).</p>"
              "</div></div>"
              "<h3>Énoncé</h3><p>Un ensemble matériel {S} est en <b>équilibre</b> par rapport à un repère R si, au cours "
              "du temps, chaque point de {S} conserve une position fixe par rapport à R.</p>"
              '<div class="enonce">Si un ensemble matériel {S} est en équilibre par rapport à un repère R, la somme des '
              "actions mécaniques extérieures à {S} qui agissent sur {S} est nulle.</div>")

    jeu_deux = "".join(
        f'<div class="deux-c" data-ok="{"oui" if ok else "non"}">{_svg_deux(k)}<p>{d}</p>'
        '<div class="deux-b"><button type="button" class="btn ghost" data-v="oui">Équilibre</button>'
        '<button type="button" class="btn ghost" data-v="non">Pas d\'équilibre</button></div>'
        f'<p class="deux-fb" aria-live="polite"></p><p class="deux-why" hidden>{why}</p></div>'
        for d, ok, why, k in JEU_DEUX)
    s2 = _sec(2, "k3-deux", "Solide soumis à l'action de deux forces",
              '<div class="cours-split">' + figure("n3-deux-forces", "Solide S en équilibre sous deux forces F et −F "
                                                   "appliquées en A et B, portées par la droite AB", "", 280) +
              '<div><div class="enonce">Un solide est en équilibre sous l\'action de deux forces si et seulement si ces '
              "deux forces ont la <b>même direction</b>, la <b>même intensité</b> et des <b>sens contraires</b>.</div>"
              "<p>La direction commune est la droite qui joint les deux points d'application. C'est l'outil qui débloque "
              "beaucoup de problèmes : un vérin, un tirant ou une biellette articulés à leurs deux extrémités et de poids "
              "négligé donnent immédiatement la <b>direction</b> d'une action.</p></div></div>"
              f'<div class="jeu"><h3>Jeu : équilibre ou pas ?</h3><div class="deux-g">{jeu_deux}</div>'
              f'<p class="jeu-score" aria-live="polite">Score : <span id="deux-s">0 / {len(JEU_DEUX)}</span></p></div>')

    cartes_gen = "".join([
        _carte("Condition 1", "Que vaut la somme des forces extérieures ?",
               f"<b>Théorème de la résultante statique</b> : Σ {_vec('F')}<sub>ext→S</sub> = {_vec('0')}"),
        _carte("Condition 2", "Que vaut la somme des moments, en un point A ?",
               f"<b>Théorème du moment statique</b> : Σ {_vec('M')}<sub>A</sub>({_vec('F')}<sub>ext→S</sub>) = "
               f"{_vec('0')}, quel que soit A (le même pour toutes les forces)"),
        _carte("Écriture torseur", "Comment écrire les deux conditions en une seule ligne ?",
               "Σ {<i>T</i><sub>ext→S</sub>}<sub>A</sub> = {0} : la somme des torseurs, tous écrits au "
               "<b>même point</b>, est le torseur nul. Dans l'espace : 3 + 3 = <b>6 équations</b>."),
    ])
    s3 = _sec(3, "k3-gen", "Généralisation : la méthode analytique",
              "<p>En première, les problèmes de statique étaient résolus <b>graphiquement</b>. Cette méthode est limitée "
              "aux problèmes <b>plans</b> et aux solides soumis à <b>2 ou 3 forces</b>. La méthode <b>analytique</b>, qui "
              "utilise les torseurs, résout des problèmes dans l'espace, avec autant d'actions mécaniques qu'on veut.</p>"
              "<p>Pour un solide S quelconque, en équilibre sous l'action de <i>n</i> actions mécaniques, s'il y a "
              "équilibre :</p>"
              f'<p class="cours-defi">À toi : réponds dans ta tête, puis retourne chaque carte.</p><div class="k3-cartes">{cartes_gen}</div>'
              '<div class="exemple"><h3>Graphique ou analytique ?</h3><table class="t"><thead><tr><th></th><th>Graphique'
              '</th><th>Analytique</th></tr></thead><tbody><tr><td>Problème</td><td>plan uniquement</td><td>plan ou '
              'espace</td></tr><tr><td>Nombre d\'actions</td><td>2 ou 3 forces</td><td>quelconque</td></tr><tr><td>'
              'Outil</td><td>dynamique, concours des droites</td><td>torseurs, équations</td></tr><tr><td>Précision'
              '</td><td>celle du tracé</td><td>celle du calcul</td></tr></tbody></table></div>')

    lia_btns = "".join(f'<button type="button" class="k3-lia" data-k="{k}" data-ddl="{d}" data-desc="{esc(desc)}" '
                       f'aria-pressed="{"true" if i == 0 else "false"}">{n}</button>'
                       for i, (k, n, d, desc) in enumerate(LIAISONS))
    ddl_rows = ('<tr><th>Translation</th>' + "".join(f'<td data-i="{i}"></td>' for i in range(3)) + "</tr>"
                '<tr><th>Rotation</th>' + "".join(f'<td data-i="{i}"></td>' for i in range(3, 6)) + "</tr>")
    tor_cells = "".join(f'<button type="button" class="k3-c" data-i="{i}" aria-label="Composante {c}">0</button>'
                        for i, c in enumerate(COMP))
    s4 = _sec(4, "k3-tor", "Torseur d'action mécanique transmissible par une liaison",
              "<p>Dès que l'on assemble deux pièces, il y a contact, donc une <b>liaison</b> et une <b>action "
              "mécanique</b>. Il existe un lien direct entre les <b>degrés de liberté</b> de la liaison et les "
              "<b>coordonnées du torseur</b> qu'elle transmet :</p>"
              '<div class="regle"><div><b>Mouvement libre</b><span>⇒ composante <b>nulle</b> : une translation libre '
              "selon x ne peut pas transmettre de force selon x (<i>X</i> = 0) ; une rotation libre autour de x ne peut "
              "pas transmettre de moment autour de x (<i>L</i> = 0).</span></div><div><b>Mouvement bloqué</b><span>⇒ "
              "composante <b>inconnue</b> : c'est l'obstacle qui fait naître l'effort.</span></div></div>"
              "<p>Le torseur au centre O de la liaison s'écrit dans la base (x, y, z) :</p>" +
              '<div class="eq">' + tz("1→2", "O", [("<i>X</i>", "<i>L</i>"), ("<i>Y</i>", "<i>M</i>"), ("<i>Z</i>", "<i>N</i>")]) +
              "</div>"
              '<div class="simu k3-atelier" id="k3-atelier"><h3>Atelier des liaisons</h3>'
              f'<div class="k3-lias" role="group" aria-label="Choisir une liaison">{lia_btns}</div>'
              '<p class="k3-desc" id="k3-desc"></p>'
              '<div class="k3-grid"><div><p class="k3-lab">Degrés de liberté (1 = mouvement libre)</p>'
              '<table class="t k3-ddl"><thead><tr><th></th><th>x</th><th>y</th><th>z</th></tr></thead><tbody>'
              + ddl_rows + "</tbody></table></div>"
              '<div><p class="k3-lab">Torseur transmissible : clique sur une case pour basculer 0 ↔ inconnue</p>'
              f'<div class="k3-tor"><span class="k3-brace">{{</span><div class="k3-cells">{tor_cells}</div>'
              '<span class="k3-brace">}</span><span class="k3-base">O, (x, y, z)</span></div>'
              '<label class="k3-plan-l"><input type="checkbox" id="k3-plan-cb"> Problème plan (x, y) : barrer <i>Z</i>, '
              "<i>L</i> et <i>M</i></label></div></div>"
              '<p class="k3-foot"><button type="button" class="btn" id="k3-ok">Vérifier</button> '
              '<button type="button" class="btn ghost" id="k3-sol">Solution</button> '
              '<b id="k3-fb" aria-live="polite"></b></p>'
              '<p class="small" id="k3-nb"></p></div>')
    cartes_plan = "".join([
        _carte("Forces", "Que devient la résultante dans un problème plan (x, y) ?",
               "Les forces sont <b>contenues dans le plan</b> (x, y) : <i>Z</i> = 0."),
        _carte("Moments", "Que devient le moment ?",
               "Les moments sont <b>perpendiculaires au plan</b>, portés par z : <i>L</i> = <i>M</i> = 0."),
    ])
    ex_plan = "".join(
        f'<details class="k3-ex"><summary>{t}</summary><div>{d}</div></details>' for t, d in [
            ("Liaison glissière d'axe x, problème dans le plan (x, y)",
             "<p>Degrés de liberté : translation selon x seulement ⇒ torseur dans l'espace "
             "{0 <i>L</i> ; <i>Y</i> <i>M</i> ; <i>Z</i> <i>N</i>}. Dans le plan (x, y), on barre <i>Z</i>, <i>L</i>, "
             "<i>M</i> :</p>" + '<div class="eq">' + tz("1→2", "O", [("0", "—"), ("<i>Y</i>", "—"), ("—", "<i>N</i>")]) +
             "</div><p><b>2 inconnues</b> : <i>Y</i> et <i>N</i>.</p>"),
            ("Liaison rotule, problème dans le plan (y, z)",
             "<p>Degrés de liberté : les trois rotations ⇒ {<i>X</i> 0 ; <i>Y</i> 0 ; <i>Z</i> 0}. Dans le plan "
             "(y, z), les forces utiles sont <i>Y</i> et <i>Z</i>, et le seul moment utile est <i>L</i> (autour de x, "
             "perpendiculaire au plan), nul ici :</p>" + '<div class="eq">' +
             tz("1→2", "O", [("—", "0"), ("<i>Y</i>", "—"), ("<i>Z</i>", "—")]) +
             "</div><p><b>2 inconnues</b> : <i>Y</i> et <i>Z</i>.</p>")])
    jeu_plan = "".join(
        f'<div class="jeu-l k3-jp" data-ok="{n}"><span>{t}</span>' +
        "".join(f'<button type="button" class="btn ghost" data-v="{v}">{v}</button>' for v in range(4)) +
        f'<b class="jeu-fb" aria-live="polite"></b><span class="k3-jp-why" hidden>{why}</span></div>'
        for t, n, why in JEU_PLAN)
    s5 = _sec(5, "k3-plan", "Hypothèse du problème plan",
              "<p>Quand le système admet un <b>plan de symétrie</b> qui contient les efforts (ou des efforts symétriques "
              "par rapport à ce plan), on l'étudie dans ce plan d'étude. Dans un problème plan :</p>"
              f'<div class="k3-cartes">{cartes_plan}</div>'
              '<div class="formule"><span class="f-main">' +
              tz("1→2", "O", [("<i>X</i>", "—"), ("<i>Y</i>", "—"), ("—", "<i>N</i>")]) +
              '</span><span class="f-units">3 composantes au plus<br>⇒ le PFS donne <b>3 équations</b> : '
              "Σ<i>X</i> = 0, Σ<i>Y</i> = 0, Σ<i>N</i> = 0</span></div>"
              "<h3>Exemples du cours</h3>" + ex_plan +
              f'<div class="jeu"><h3>Jeu : combien d\'inconnues dans le plan (x, y) ?</h3>{jeu_plan}'
              f'<p class="jeu-score" aria-live="polite">Score : <span id="k3-jp-s">0 / {len(JEU_PLAN)}</span></p></div>')

    s6 = _sec(6, "k3-mom", "Prérequis : le moment d'une force",
              "<p>Le moment d'une force mesure sa capacité à faire tourner le solide autour d'un point. Dans le plan "
              f"(x, y), pour une force {_vec('F')} (<i>F</i><sub>x</sub> ; <i>F</i><sub>y</sub>) appliquée en P, avec "
              f"{_vec('AP')} (<i>x</i> ; <i>y</i>) :</p>"
              '<div class="formule"><span class="f-main"><i>M</i><sub>A</sub> = <i>x</i> · <i>F</i><sub>y</sub> − '
              '<i>y</i> · <i>F</i><sub>x</sub> = ± <i>F</i> × <i>d</i></span><span class="f-units"><i>d</i> : bras de '
              "levier, distance de A à la droite d'action<br>positif dans le sens trigonométrique (anti-horaire)</span></div>"
              '<div class="simu" id="k3-mom-simu"><h3>Calculateur : déplace la force, regarde son moment en A</h3>'
              '<div class="k3-mom-g">' + MOMENT_SVG +
              '<div class="simu-grid k3-col">'
              '<label><span>Position x de P : <output id="mo-x">4 m</output></span><input type="range" id="mi-x" min="-1" max="10" step="0.5" value="4"></label>'
              '<label><span>Position y de P : <output id="mo-y">1 m</output></span><input type="range" id="mi-y" min="-2" max="4" step="0.5" value="1"></label>'
              '<label><span>Intensité F : <output id="mo-f">500 N</output></span><input type="range" id="mi-f" min="0" max="1000" step="50" value="500"></label>'
              '<label><span>Angle de F avec x : <output id="mo-a">270°</output></span><input type="range" id="mi-a" min="0" max="355" step="5" value="270"></label>'
              "</div></div>"
              '<div class="simu-out"><div><span>Composantes de F</span><b id="mr-fxy"></b></div><div><span>Moment en A'
              '</span><b id="mr-m"></b></div><div><span>Bras de levier d</span><b id="mr-d"></b></div></div>'
              '<p class="simu-verdict" id="mr-v"></p>'
              '<details class="simu-defi"><summary>Défi : annule le moment sans mettre F à zéro</summary><p>Oriente la '
              "force pour que sa droite d'action passe par A. <b id=\"mr-defi\"></b></p></details></div>"
              "<h3>Déplacer un torseur</h3><p>Pour écrire toutes les équations au même point, on <b>déplace</b> les "
              "torseurs : la résultante est la même en tout point, le moment se transporte par la relation de Varignon "
              "(« BABAR ») :</p>"
              f'<div class="formule"><span class="f-main">{_vec("M")}<sub>B</sub> = {_vec("M")}<sub>A</sub> + '
              f'{_vec("BA")} ∧ {_vec("R")}</span><span class="f-units">dans le plan : <i>N</i><sub>B</sub> = '
              "<i>N</i><sub>A</sub> + <i>x</i><sub>BA</sub> · <i>R</i><sub>y</sub> − <i>y</i><sub>BA</sub> · "
              "<i>R</i><sub>x</sub></span></div>")

    steps = [
        ("Isoler et faire le bilan", "Après l'étude du système (énoncé, documents techniques), <b>isoler</b> un solide "
         "ou un ensemble de solides et faire le <b>bilan des actions mécaniques extérieures</b> (B.A.M.E.) en écrivant "
         "les torseurs en leurs points d'application."),
        ("Compter", "La méthode analytique donne jusqu'à <b>6 équations</b> (<b>3</b> dans un problème plan). Vérifier "
         "que le nombre d'inconnues est <b>inférieur ou égal</b> au nombre d'équations. Sinon, le problème ne peut pas "
         "être résolu tel quel : il faut le simplifier (isoler d'abord un autre solide)."),
        ("Choisir un point", "Choisir le point de résolution — en général celui où l'action mécanique a <b>le plus "
         "d'inconnues</b> — et y <b>déplacer</b> tous les autres torseurs en calculant leurs nouveaux moments."),
        ("Écrire et résoudre", "Écrire les équations issues du PFS et les résoudre. Présenter les résultats avec les "
         "<b>coordonnées</b> des forces et leurs <b>normes</b>."),
    ]
    steps_html = "".join(f'<li class="k3-step" data-s="{i}"><span class="k3-sn">{i + 1}</span><div><b>{t}</b><p>{d}'
                         "</p></div></li>" for i, (t, d) in enumerate(steps))
    s7 = _sec(7, "k3-meth", "Méthode de résolution",
              f'<ol class="k3-steps">{steps_html}</ol>'
              '<div class="simu" id="k3-pou"><h3>Simulateur : une poutre résolue pas à pas</h3>'
              "<p>Une poutre AB de 4 m (poids négligé) est articulée en A (pivot d'axe z) et posée en B sur un appui "
              "ponctuel de normale y. Une charge <i>F</i> s'applique à la distance <i>a</i> de A, inclinée de "
              "<i>α</i> sur la poutre.</p>" + POUTRE_SVG +
              '<div class="simu-grid">'
              '<label><span>Intensité F : <output id="po-f">1 000 N</output></span><input type="range" id="pi-f" min="0" max="2000" step="100" value="1000"></label>'
              '<label><span>Position a : <output id="po-a">1,0 m</output></span><input type="range" id="pi-a" min="0" max="4" step="0.1" value="1"></label>'
              '<label><span>Angle α : <output id="po-al">90°</output></span><input type="range" id="pi-al" min="30" max="150" step="5" value="90"></label>'
              "</div>"
              '<div class="k3-etapes"><div class="k3-et" data-e="0"><b>1. Bilan</b><div id="pe-1"></div></div>'
              '<div class="k3-et" data-e="1"><b>2. Compter</b><div>Inconnues : <i>X</i><sub>A</sub>, <i>Y</i><sub>A</sub> '
              "(pivot), <i>Y</i><sub>B</sub> (ponctuelle) = 3 ≤ 3 équations : résoluble.</div></div>"
              '<div class="k3-et" data-e="2"><b>3. Point A</b><div>Deux inconnues en A : on y écrit les moments, '
              "<i>X</i><sub>A</sub> et <i>Y</i><sub>A</sub> disparaissent.</div></div>"
              '<div class="k3-et" data-e="3"><b>4. Équations et résultats</b><div id="pe-4"></div></div></div>'
              '<p class="k3-foot"><button type="button" class="btn" id="pe-next">Étape suivante</button> '
              '<button type="button" class="btn ghost" id="pe-all">Tout afficher</button> '
              '<button type="button" class="btn ghost" id="pe-reset">Recommencer</button></p>'
              '<details class="simu-defi"><summary>Défis</summary><ul class="k3-defis">'
              '<li id="df-1">Place la charge pour que les deux appuis portent autant : <i>Y</i><sub>A</sub> = '
              "<i>Y</i><sub>B</sub>. <b></b></li>"
              '<li id="df-2">Oriente la charge pour que le pivot A ne reçoive aucun effort horizontal. <b></b></li>'
              '<li id="df-3">Trouve une position où l\'appui B ne porte rien. <b></b></li></ul></details></div>')

    quiz = "".join(
        f'<fieldset class="quiz-q" data-ok="{ok}"><legend><span class="q-num">{i + 1}</span> {q}</legend>' +
        "".join(f'<label><input type="radio" name="k3q{i}" value="{j}"> {o}</label>' for j, o in enumerate(opts)) +
        f'<p class="quiz-fb" aria-live="polite"></p><p class="quiz-why" hidden>{why}</p></fieldset>'
        for i, (q, opts, ok, why) in enumerate(QUIZ))
    s8 = _sec(8, "k3-quiz", "Quiz : vérifie tes connaissances",
              f'<p>Choisis une réponse : la correction s\'affiche aussitôt.</p><div class="quiz">{quiz}</div>'
              f'<div class="quiz-score" aria-live="polite"><span id="qz-score">0 / {len(QUIZ)}</span><span id="qz-stars" '
              'aria-hidden="true"></span><button type="button" class="btn ghost" id="qz-reset">Recommencer</button></div>')

    liens = "".join(f'<a class="btn ghost" href="{h}">{t}</a>' for h, t in
                    [("coffre-fort.html", "Exercice 3.1 — Porte de coffre-fort"),
                     ("echelle-pompier.html", "Exercice 3.2 — Échelle de pompier"),
                     ("cadre-velo.html", "Exercice 3.3 — Cadre de vélo")])
    body = f"""<div class="cours" id="cours-3">
<nav class="c-top no-print" aria-label="Navigation"><a href="index.html">{HOUSE} Accueil</a></nav>
<div class="home-top home-top-single"><div class="home-top-l"><header class="home-head"><span class="mc-tag">Cours 3</span> <span class="pastille n3">Niveau 3</span>
<h1 id="home-title">Statique analytique</h1><p class="home-sub">Résoudre un problème de statique par le calcul : le principe
fondamental de la statique écrit avec des torseurs, le torseur transmissible par chaque liaison, l'hypothèse du problème
plan et une méthode en quatre étapes. Environ 1 heure, avec des cartes à retourner, deux jeux, un atelier des liaisons,
un calculateur de moment, une poutre résolue pas à pas et un quiz.</p></header></div></div>
<div class="k3-obj"><div><h3>Objectif</h3><ul><li>Résoudre par la méthode analytique un problème de statique.</li></ul></div>
<div><h3>Prérequis</h3><ul><li>Savoir calculer le moment d'une force (rappel en section 6).</li>
<li>Savoir écrire une action mécanique sous forme de torseur.</li></ul></div></div>
<nav class="cours-nav no-print" aria-label="Étapes du cours">{nav}</nav>
{s1}{s2}{s3}{s4}{s5}{s6}{s7}{s8}
<div class="cours-foot no-print"><span class="small">S'entraîner :</span> {liens}
<button type="button" class="btn ghost" id="cours-print">Imprimer le cours</button>
<a class="btn ghost" href="index.html">{HOUSE} Retour à l'accueil</a></div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Fichier généré par src/generer.py (contenu : src/cours3.py) : ne pas modifier à la main. -->
<title>Statique analytique — cours — Statique</title>
<meta name="description" content="Cours interactif de statique analytique (niveau 3) : PFS, solide soumis à deux forces, torseurs des liaisons, problème plan, moment d'une force, méthode de résolution, quiz.">
{style}
{hub_css}
{COURS3_CSS}
</head>
<body class="no-mode hub cours-page">
<section id="home" aria-labelledby="home-title"><div class="home-inner">{body}</div></section>
{COURS3_JS}
</body>
</html>
"""


COURS3_CSS = """<style>
/* ---------- cours interactif (d'après les cours du dépôt RDM) ---------- */
.pastille.n3{background:#7B3FA0}
.cours .part{margin-bottom:22px}
.cours .part-body h3{font:700 1.12rem var(--f-titre); margin:16px 0 6px}
.cours-nav{display:flex; flex-wrap:wrap; gap:6px; margin:0 0 16px}
.cours-nav a{font:600 .92rem var(--f-titre); color:var(--encre); background:var(--papier); border:1.5px solid var(--encre); padding:5px 12px; text-decoration:none}
.cours-nav a:hover{background:var(--jaune-pale)}
.cours-split{display:flex; gap:18px; align-items:flex-start; flex-wrap:wrap}
.cours-split>div{flex:1 1 300px; min-width:0}
.cours-split>.fig{flex:0 1 auto; margin:0}
.cours-defi{font-weight:700; color:var(--bleu)}
.enonce{border:2px solid var(--encre); background:#fff; padding:10px 16px; margin:10px 0; font-weight:700; text-align:center; max-width:640px}
.formule{display:flex; flex-wrap:wrap; gap:14px 28px; align-items:center; border:2px solid var(--rouge); background:#fff; padding:10px 18px; margin:12px 0; max-width:680px}
.formule .f-main{font:700 1.35rem var(--f-titre); line-height:2}
.formule .f-units{font-size:.9rem; color:var(--encre-2)}
.exemple{background:#F6F7F4; border:1px solid var(--trait-fin); padding:6px 16px; margin-top:12px}
.simu{border:2px solid var(--bleu); background:var(--bleu-pale); padding:12px 16px; margin:14px 0}
.simu h3{margin:0 0 8px!important; font:700 1.15rem var(--f-titre); color:var(--bleu)}
.simu-grid{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px 18px; margin:8px 0}
.simu-grid.k3-col{grid-template-columns:1fr; align-content:start}
@media (max-width:640px){ .simu-grid{grid-template-columns:1fr} }
.simu-grid label{display:flex; flex-direction:column; gap:4px; font-weight:600; font-size:.92rem}
.simu-grid output{font:700 1rem var(--f-titre); color:var(--bleu)}
.simu-grid input[type=range]{width:100%; accent-color:var(--bleu)}
.simu-out{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; margin:12px 0 8px}
.simu-out div{background:var(--encre); color:#fff; padding:6px 10px}
.simu-out span{display:block; font-size:.78rem; color:#D7DDE2}
.simu-out b{font:700 1.05rem var(--f-titre); color:var(--jaune)}
@media (max-width:640px){ .simu-out{grid-template-columns:1fr} }
.simu-verdict{font-weight:700; margin:8px 0 4px}
.simu-defi{margin-top:8px; background:#fff; border:1px dashed var(--bleu); padding:6px 10px}
.simu-defi summary{cursor:pointer; font-weight:600}
.jeu{border:2px dashed var(--encre-2); background:#fff; padding:10px 16px; margin:14px 0}
.jeu h3{margin:0 0 8px!important}
.jeu-l{display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding:6px 0; border-bottom:1px solid var(--trait-fin)}
.jeu-l>span:first-child{flex:1 1 220px; font-weight:600}
.jeu-l .btn{padding:4px 12px; min-width:2.6em}
.jeu-l.is-ok{background:var(--vert-pale)} .jeu-l.is-ko{background:var(--rouge-pale)}
.jeu-fb{min-width:1.6em}
.jeu-score{font:700 1.1rem var(--f-titre); margin:8px 0 0}
.k3-jp-why{flex-basis:100%; font-size:.88rem; color:var(--encre-2)}
.quiz{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px}
.quiz-q{border:1.5px solid var(--encre); background:#fff; padding:8px 14px 10px; margin:0}
.quiz-q legend{font-weight:700; padding:0 4px}
.quiz-q label{display:block; padding:3px 0; cursor:pointer}
.quiz-q.is-ok{border-color:var(--vert); background:var(--vert-pale)}
.quiz-q.is-ko{border-color:var(--rouge); background:var(--rouge-pale)}
.quiz-q label.good{font-weight:700; color:var(--vert)}
.quiz-fb{margin:4px 0 0; font-weight:700}
.quiz-q.is-ok .quiz-fb{color:var(--vert)} .quiz-q.is-ko .quiz-fb{color:var(--rouge)}
.quiz-why{margin:2px 0 0; font-size:.9rem}
.quiz-score{display:flex; align-items:center; gap:14px; margin:14px 0 0; font:700 1.3rem var(--f-titre)}
#qz-stars{color:var(--jaune); font-size:1.6rem; letter-spacing:2px}
.cours-foot{display:flex; flex-wrap:wrap; gap:10px; margin:6px 0 0}
.cours-foot .small{align-self:center}
.k3-obj{display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:0 0 14px}
.k3-obj>div{background:var(--papier); border:1px solid var(--trait-fin); border-top:4px solid #7B3FA0; padding:6px 16px}
.k3-obj h3{margin:4px 0; font:700 1.05rem var(--f-titre)}
.k3-obj ul{margin:4px 0 6px; padding-left:1.2rem}
@media (max-width:640px){ .k3-obj{grid-template-columns:1fr} }
/* balance */
.bal{flex:0 1 300px!important}
.bal-svg{width:100%; max-width:300px; background:#fff; border:1px solid var(--trait-fin)}
.bal-l{display:flex; flex-direction:column; gap:4px; font-weight:600; font-size:.92rem; margin-top:6px}
.bal-l input{accent-color:var(--bleu)}
.bal-out{font-size:1.05rem}
.lab-b,.lab-r,.lab-g,.lab-v{font:italic 700 17px var(--f-texte)}
.pou-svg .lab-b,.pou-svg .lab-g{font-size:14px; font-style:normal}
.lab-b{fill:#1F5FA8} .lab-r{fill:#C62828} .lab-g{fill:#1B7A43} .lab-v{fill:#7B3FA0}
.pt{font:700 15px var(--f-titre); fill:var(--encre)}
.ax{font:600 13px var(--f-texte); fill:var(--encre-2)}
/* cartes à retourner */
.k3-cartes{display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:12px; margin:8px 0 14px}
.k3-carte{display:flex; flex-direction:column; gap:6px; align-items:flex-start; text-align:left; min-height:110px; padding:12px 14px; border:2px solid var(--encre); background:var(--jaune-pale); font:inherit; cursor:pointer; transition:background .2s}
.k3-carte b{font:700 1.1rem var(--f-titre)}
.k3-carte .k3-dos{display:none}
.k3-carte[aria-expanded="true"]{background:#fff; border-color:#7B3FA0}
.k3-carte[aria-expanded="true"] .k3-dos{display:block; animation:reveal .25s ease}
.k3-carte[aria-expanded="true"] .k3-q{color:var(--encre-2); font-size:.85rem}
.k3-carte[aria-expanded="false"]::after{content:"Clique pour retourner"; font-size:.8rem; color:var(--encre-2)}
/* jeu deux forces */
.deux-g{display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:12px}
.deux-c{border:1.5px solid var(--encre); background:#fff; padding:8px 12px}
.deux-c p{margin:4px 0; font-size:.92rem}
.deux-svg{width:100%; height:auto; max-height:100px}
.deux-b{display:flex; gap:6px; flex-wrap:wrap}
.deux-b .btn{padding:4px 10px; font-size:.88rem}
.deux-c.is-ok{background:var(--vert-pale); border-color:var(--vert)} .deux-c.is-ko{background:var(--rouge-pale); border-color:var(--rouge)}
.deux-fb{font-weight:700}
/* atelier des liaisons */
.regle{display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:10px 0}
.regle>div{background:#fff; border-left:5px solid var(--vert); padding:8px 12px}
.regle>div+div{border-left-color:var(--rouge)}
.regle>div>b{display:block; font:700 1.05rem var(--f-titre)}
@media (max-width:640px){ .regle{grid-template-columns:1fr} }
.k3-lias{display:flex; flex-wrap:wrap; gap:6px; margin:4px 0 8px}
.k3-lia{border:1.5px solid var(--encre); background:var(--papier); padding:5px 10px; font:600 .88rem var(--f-titre); cursor:pointer}
.k3-lia[aria-pressed="true"]{background:var(--encre); color:var(--jaune)}
.k3-lia.fait::after{content:" ✔"; color:var(--vert)}
.k3-lia[aria-pressed="true"].fait::after{color:var(--jaune)}
.k3-desc{font-style:italic; margin:0 0 8px}
.k3-grid{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.2fr); gap:16px; align-items:start}
@media (max-width:760px){ .k3-grid{grid-template-columns:1fr} }
.k3-lab{font-weight:700; font-size:.9rem; margin:0 0 4px}
.k3-ddl{background:#fff}
.k3-ddl td{text-align:center; font:700 1.1rem var(--f-titre); width:3.2em}
.k3-ddl td.libre{background:var(--vert-pale); color:var(--vert)}
.k3-ddl td.bloque{background:#F4F5F2; color:var(--encre-2)}
.k3-tor{display:flex; align-items:center; gap:6px; flex-wrap:wrap}
.k3-brace{font:300 4.4rem/1 var(--f-texte); color:var(--encre)}
.k3-cells{display:grid; grid-template-columns:repeat(2,64px); grid-auto-flow:column; grid-template-rows:repeat(3,40px); gap:4px}
.k3-c{border:1.5px solid var(--encre); background:#fff; font:italic 700 1.15rem var(--f-texte); cursor:pointer}
.k3-c.on{background:var(--jaune-pale)}
.k3-c.ok{background:var(--vert-pale); border-color:var(--vert)} .k3-c.ko{background:var(--rouge-pale); border-color:var(--rouge)}
.k3-c.barre{text-decoration:line-through; opacity:.4}
.k3-base{font-size:.85rem; color:var(--encre-2)}
.k3-plan-l{display:block; margin-top:8px; font-weight:600; font-size:.92rem}
.k3-foot{display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:10px 0 4px}
#k3-fb.ok{color:var(--vert)} #k3-fb.ko{color:var(--rouge)}
.k3-ex{background:#fff; border:1px solid var(--trait); padding:6px 12px; margin:6px 0}
.k3-ex summary{cursor:pointer; font-weight:700}
.torseur{display:inline-flex; align-items:center; gap:6px; margin:4px 0; flex-wrap:wrap; vertical-align:middle}
.tz-b{display:inline-block; border-left:2px solid currentColor; border-right:2px solid currentColor; border-radius:10px; padding:2px 6px}
.tz-b table{border-collapse:collapse} .tz-b td{padding:1px 10px; text-align:center; min-width:3em; line-height:1.5}
.tz-r{font-size:.8rem; color:var(--encre-2)}
.formule .torseur{font-size:1.1rem}
.eq{margin:.35rem 0 .55rem; overflow-x:auto; line-height:2.1}
.frac{display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; margin:0 .12em; line-height:1.25}
.frac>span{padding:0 .25em; white-space:nowrap}
.frac>span:first-child{border-bottom:1px solid currentColor}
/* calculateur de moment */
.k3-mom-g{display:grid; grid-template-columns:minmax(0,1.7fr) minmax(0,1fr); gap:14px; align-items:start}
@media (max-width:760px){ .k3-mom-g{grid-template-columns:1fr} }
.mom-svg{width:100%; height:auto; background:#fff; border:1px solid var(--trait-fin)}
.mom-svg .axe{stroke:#46525C; stroke-width:1.5}
.mom-svg .grille line{stroke:#ECEEEA; stroke-width:1}
.mom-svg .ligne-action{stroke:#C62828; stroke-width:1.3; stroke-dasharray:6 5; opacity:.7}
.mom-svg .bras{stroke:#7B3FA0; stroke-width:2.5; stroke-dasharray:4 3}
.mom-svg .ap{stroke:#46525C; stroke-width:1.3; stroke-dasharray:2 4}
#mr-v.pos{color:var(--vert)} #mr-v.neg{color:var(--rouge)} #mr-v.nul{color:var(--encre-2)}
/* méthode et poutre */
.k3-steps{list-style:none; padding:0; margin:6px 0 12px; display:grid; gap:8px}
.k3-step{display:grid; grid-template-columns:44px 1fr; gap:10px; background:#fff; border:1px solid var(--trait-fin); padding:8px 12px; transition:background .2s, border-color .2s}
.k3-step p{margin:2px 0 0}
.k3-sn{display:flex; align-items:center; justify-content:center; width:38px; height:38px; border-radius:50%; background:var(--encre); color:var(--jaune); font:700 1.3rem var(--f-titre)}
.k3-step.on{background:var(--jaune-pale); border-color:var(--jaune)}
.pou-svg{display:block; width:100%; max-width:660px; height:auto; background:#fff; border:1px solid var(--trait-fin); margin:6px auto}
.k3-etapes{display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px}
@media (max-width:760px){ .k3-etapes{grid-template-columns:1fr} }
.k3-et{background:#fff; border:1.5px solid var(--trait); padding:8px 12px; min-height:70px}
.k3-et>div{display:none; font-size:.92rem; margin-top:4px}
.k3-et.vu{border-color:var(--bleu)}
.k3-et.vu>div{display:block; animation:reveal .25s ease}
.k3-et .torseur{font-size:.85rem}
.k3-et .eqs p{margin:2px 0}
.k3-defis li{margin:4px 0}
.k3-defis b{color:var(--vert)}
@media print{
  body.cours-page #home{display:block!important; padding:0}
  .no-print,.cours-nav,.cours-foot,.k3-foot,.simu-defi{display:none!important}
  .k3-carte .k3-dos,.quiz-why[hidden],.deux-why[hidden],.k3-jp-why[hidden],.k3-et>div{display:block!important}
  .k3-ex{display:block} .k3-ex>div{display:block!important}
}
</style>"""


COURS3_JS = r"""<script>
(function () {
  "use strict";
  var root = document.getElementById("cours-3");
  function q(s) { return root.querySelector(s); }
  function qa(s) { return Array.prototype.slice.call(root.querySelectorAll(s)); }
  function fr(x, d) {
    return (Math.abs(x) < 0.5 * Math.pow(10, -d) ? 0 : x).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d }).replace("-", "\u2212");
  }
  function setLine(el, x1, y1, x2, y2) { el.setAttribute("x1", x1); el.setAttribute("y1", y1); el.setAttribute("x2", x2); el.setAttribute("y2", y2); }
  function show(el, on) { el.style.display = on ? "" : "none"; }
  function setText(el, s, x, y) { el.textContent = s; el.setAttribute("x", x); el.setAttribute("y", y); }

  // ---------- 1. balance : R = −P
  var balIn = q("#bal-in");
  function balance() {
    var m = +balIn.value, p = m * 9.81, L = 20 + m * 0.6;
    q("#bal-m").textContent = m + " kg";
    setLine(q("#bal-r"), 160, 160, 160, 160 - L); setLine(q("#bal-p"), 160, 140, 160, 140 + L);
    q("#bal-rt").setAttribute("y", 160 - L + 12); q("#bal-pt").setAttribute("y", 140 + L);
    q("#bal-p-v").textContent = fr(p, 1) + " N"; q("#bal-r-v").textContent = fr(p, 1) + " N";
  }
  balIn.addEventListener("input", balance); balance();

  // ---------- 2. jeu : équilibre ou pas ?
  var deux = qa(".deux-c");
  function deuxScore() { q("#deux-s").textContent = deux.filter(function (c) { return c.classList.contains("is-ok"); }).length + " / " + deux.length; }
  deux.forEach(function (c) {
    Array.prototype.forEach.call(c.querySelectorAll("button"), function (b) {
      b.addEventListener("click", function () {
        if (c.classList.contains("is-ok") || c.classList.contains("is-ko")) return;
        var ok = b.getAttribute("data-v") === c.getAttribute("data-ok");
        c.classList.add(ok ? "is-ok" : "is-ko");
        c.querySelector(".deux-fb").textContent = ok ? "✔ Bien vu !" : "✘ Non : " + (c.getAttribute("data-ok") === "oui" ? "équilibre." : "pas d'équilibre.");
        c.querySelector(".deux-why").hidden = false;
        deuxScore();
      });
    });
  });
  deuxScore();

  // ---------- 3 et 5. cartes à retourner
  qa(".k3-carte").forEach(function (b) {
    b.addEventListener("click", function () { b.setAttribute("aria-expanded", b.getAttribute("aria-expanded") === "true" ? "false" : "true"); });
  });

  // ---------- 4. atelier des liaisons
  var COMP = ["X", "Y", "Z", "L", "M", "N"], cur = null, ddl = "";
  var cells = qa(".k3-c"), ddlTd = qa(".k3-ddl td"), plan = q("#k3-plan-cb"), fb = q("#k3-fb");
  function attendu(i) { return ddl.charAt(i) === "0"; }  // mouvement bloqué ⇒ composante inconnue
  function renderCells() {
    cells.forEach(function (c, i) {
      var on = c.classList.contains("on");
      c.textContent = on ? COMP[i] : "0";
      c.classList.toggle("barre", plan.checked && (i === 2 || i === 3 || i === 4));
    });
    var n = 0, np = 0;
    for (var i = 0; i < 6; i++) if (attendu(i)) { n++; if (i === 0 || i === 1 || i === 5) np++; }
    q("#k3-nb").innerHTML = plan.checked ? "Dans le plan (x, y), on ne garde que <i>X</i>, <i>Y</i> et <i>N</i>." : "";
    q("#k3-nb").dataset.n = n; q("#k3-nb").dataset.np = np;
  }
  function choisir(btn) {
    qa(".k3-lia").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
    cur = btn; ddl = btn.getAttribute("data-ddl");
    q("#k3-desc").textContent = btn.getAttribute("data-desc");
    ddlTd.forEach(function (td) {
      var i = +td.getAttribute("data-i"), libre = ddl.charAt(i) === "1";
      td.textContent = libre ? "1" : "0"; td.className = libre ? "libre" : "bloque";
    });
    cells.forEach(function (c) { c.classList.remove("on", "ok", "ko"); });
    fb.textContent = ""; fb.className = "";
    renderCells();
  }
  qa(".k3-lia").forEach(function (b) { b.addEventListener("click", function () { choisir(b); }); });
  cells.forEach(function (c) {
    c.addEventListener("click", function () { c.classList.toggle("on"); c.classList.remove("ok", "ko"); fb.textContent = ""; renderCells(); });
  });
  plan.addEventListener("change", renderCells);
  function verifier() {
    var bons = 0;
    cells.forEach(function (c, i) {
      var ok = c.classList.contains("on") === attendu(i);
      c.classList.toggle("ok", ok); c.classList.toggle("ko", !ok); if (ok) bons++;
    });
    var nb = +q("#k3-nb").dataset.n, np = +q("#k3-nb").dataset.np;
    if (bons === 6) {
      fb.className = "ok";
      fb.innerHTML = "✔ Juste ! " + nb + " inconnue" + (nb > 1 ? "s" : "") + " dans l'espace" +
        (plan.checked ? ", " + np + " dans le plan (x, y)." : ".");
      cur.classList.add("fait");
    } else { fb.className = "ko"; fb.textContent = "✘ " + (6 - bons) + " case" + (6 - bons > 1 ? "s" : "") + " à revoir : un mouvement libre donne une composante nulle."; }
  }
  q("#k3-ok").addEventListener("click", verifier);
  q("#k3-sol").addEventListener("click", function () {
    cells.forEach(function (c, i) { c.classList.toggle("on", attendu(i)); });
    renderCells(); verifier();
  });
  choisir(qa(".k3-lia")[0]);

  // ---------- 5. jeu : combien d'inconnues dans le plan ?
  var jp = qa(".k3-jp");
  function jpScore() { q("#k3-jp-s").textContent = jp.filter(function (l) { return l.classList.contains("is-ok"); }).length + " / " + jp.length; }
  jp.forEach(function (l) {
    Array.prototype.forEach.call(l.querySelectorAll("button"), function (b) {
      b.addEventListener("click", function () {
        if (l.classList.contains("is-ok") || l.classList.contains("is-ko")) return;
        var ok = b.getAttribute("data-v") === l.getAttribute("data-ok");
        l.classList.add(ok ? "is-ok" : "is-ko");
        l.querySelector(".jeu-fb").textContent = ok ? "✔" : "✘ " + l.getAttribute("data-ok");
        l.querySelector(".k3-jp-why").hidden = false;
        jpScore();
      });
    });
  });
  jpScore();

  // ---------- 6. calculateur de moment (1 m = 40 px, A en (80 ; 210))
  var OX = 80, OY = 210, K = 40;
  var g = q("#mom-grille"), svgNS = "http://www.w3.org/2000/svg";
  for (var gx = -1; gx <= 10; gx++) { var l1 = document.createElementNS(svgNS, "line"); setLine(l1, OX + gx * K, 15, OX + gx * K, 315); g.appendChild(l1); }
  for (var gy = -2; gy <= 4; gy++) { var l2 = document.createElementNS(svgNS, "line"); setLine(l2, 20, OY - gy * K, 505, OY - gy * K); g.appendChild(l2); }
  var MX = q("#mi-x"), MY = q("#mi-y"), MF = q("#mi-f"), MA = q("#mi-a");
  function moment() {
    var x = +MX.value, y = +MY.value, F = +MF.value, a = +MA.value * Math.PI / 180;
    var fx = F * Math.cos(a), fy = F * Math.sin(a), M = x * fy - y * fx;
    q("#mo-x").textContent = fr(x, 1) + " m"; q("#mo-y").textContent = fr(y, 1) + " m";
    q("#mo-f").textContent = fr(F, 0) + " N"; q("#mo-a").textContent = MA.value + "°";
    var px = OX + x * K, py = OY - y * K, L = 20 + F * 0.09;
    var ex = px + L * Math.cos(a), ey = py - L * Math.sin(a);
    q("#mom-p").setAttribute("cx", px); q("#mom-p").setAttribute("cy", py);
    setText(q("#mom-pt"), "P", px - 16, py + 18);
    setLine(q("#mom-f"), px, py, ex, ey); show(q("#mom-f"), F > 0);
    setText(q("#mom-ft"), "F", ex + 6, ey - 6); show(q("#mom-ft"), F > 0);
    setLine(q("#mom-ap"), OX, OY, px, py);
    var ca = Math.cos(a), sa = Math.sin(a);
    setLine(q("#mom-ligne"), px - 700 * ca, py + 700 * sa, px + 700 * ca, py - 700 * sa); show(q("#mom-ligne"), F > 0);
    // pied de la perpendiculaire de A sur la droite d'action
    var t = (OX - px) * ca + (OY - py) * (-sa), hx = px + t * ca, hy = py - t * sa;
    var d = F > 0 ? Math.abs(M) / F : 0;
    setLine(q("#mom-d"), OX, OY, hx, hy); show(q("#mom-d"), F > 0 && d > 0.01);
    setText(q("#mom-dt"), "d", (OX + hx) / 2 + 6, (OY + hy) / 2 - 6); show(q("#mom-dt"), F > 0 && d > 0.01);
    var arc = q("#mom-arc"), r = 26;
    if (Math.abs(M) > 0.5) {
      var s = M > 0 ? 0 : 1, a1 = M > 0 ? 0.3 : 2.8, a2 = M > 0 ? 2.8 : 0.3;
      arc.setAttribute("d", "M" + (OX + r * Math.cos(a1)) + " " + (OY - r * Math.sin(a1)) + " A" + r + " " + r + " 0 0 " + s + " " + (OX + r * Math.cos(a2)) + " " + (OY - r * Math.sin(a2)));
      arc.setAttribute("stroke", M > 0 ? "#1B7A43" : "#C62828"); show(arc, true);
    } else show(arc, false);
    q("#mr-fxy").textContent = "(" + fr(fx, 0) + " ; " + fr(fy, 0) + ") N";
    q("#mr-m").textContent = fr(M, 0) + " N·m";
    q("#mr-d").textContent = fr(d, 2) + " m";
    var v = q("#mr-v");
    if (Math.abs(M) < 0.5) { v.className = "simu-verdict nul"; v.textContent = F > 0 ? "Moment nul : la droite d'action de F passe par A, la force ne fait pas tourner autour de A." : "Pas de force, pas de moment."; }
    else if (M > 0) { v.className = "simu-verdict pos"; v.textContent = "M > 0 : F fait tourner autour de A dans le sens trigonométrique (anti-horaire)."; }
    else { v.className = "simu-verdict neg"; v.textContent = "M < 0 : F fait tourner autour de A dans le sens horaire."; }
    q("#mr-defi").textContent = (F > 0 && Math.abs(M) < 0.5 && (x !== 0 || y !== 0)) ? "✔ Défi réussi !" : "";
  }
  [MX, MY, MF, MA].forEach(function (el) { el.addEventListener("input", moment); });
  moment();

  // ---------- 7. méthode : poutre AB de 4 m, pas à pas (1 m = 110 px, A en (70 ; 154))
  var PF = q("#pi-f"), PA = q("#pi-a"), PAL = q("#pi-al"), etape = 0;
  var steps = qa(".k3-step"), ets = qa(".k3-et");
  function tz(n, p, x, y, nn) {
    return '<span class="torseur"><span class="tz-n">{<i>T</i><sub>' + n + '</sub>}<sub>' + p + '</sub> =</span><span class="tz-b"><table><tr><td>' + x + "</td><td>—</td></tr><tr><td>" + y + "</td><td>—</td></tr><tr><td>—</td><td>" + nn + '</td></tr></table></span></span>';
  }
  function poutre() {
    var F = +PF.value, a = +PA.value, al = +PAL.value * Math.PI / 180;
    var fx = F * Math.cos(al), fy = -F * Math.sin(al);
    var YB = -a * fy / 4, XA = -fx, YA = -fy - YB;
    q("#po-f").textContent = fr(F, 0) + " N"; q("#po-a").textContent = fr(a, 1) + " m"; q("#po-al").textContent = PAL.value + "°";
    var ax = 70 + a * 110, ay = 146, L = 18 + F * 0.045;
    setLine(q("#pou-f"), ax - L * Math.cos(al), ay - L * Math.sin(al), ax, ay); show(q("#pou-f"), F > 0);
    q("#pou-pt").setAttribute("cx", ax); q("#pou-pt").setAttribute("cy", ay);
    setText(q("#pou-ft"), "F", ax - L * Math.cos(al) - 18, ay - L * Math.sin(al));
    // réaction : flèche attachée au point (px ; py), du côté −u ; pointe sur le point si la valeur est positive
    function reac(id, tid, px, py, ux, uy, val, lab) {
      var el = q(id), t = q(tid);
      if (Math.abs(val) < 0.5 || F <= 0) { show(el, false); show(t, false); return; }
      show(el, true); show(t, true);
      var len = 12 + 55 * Math.abs(val) / F, ox = px - ux * len, oy = py - uy * len;
      if (val > 0) setLine(el, ox, oy, px, py); else setLine(el, px, py, ox, oy);
      t.textContent = lab + " = " + fr(val, 0) + " N";
    }
    reac("#pou-xa", "#pou-xat", 62, 154, 1, 0, XA, "XA");
    reac("#pou-ya", "#pou-yat", 70, 204, 0, -1, YA, "YA");
    reac("#pou-yb", "#pou-ybt", 510, 204, 0, -1, YB, "YB");
    q("#pe-1").innerHTML = '<div class="eqs">' + tz("0→1", "A", "<i>X</i><sub>A</sub>", "<i>Y</i><sub>A</sub>", "0") + " " +
      tz("0→1", "B", "0", "<i>Y</i><sub>B</sub>", "0") + " " + tz("F", "P", fr(fx, 0), fr(fy, 0), "0") + "</div>";
    q("#pe-4").innerHTML = '<div class="eqs"><p>Σ<i>N</i><sub>A</sub> : 4 · <i>Y</i><sub>B</sub> + ' + fr(a, 1) + " × (" + fr(fy, 0) + ") = 0 ⇒ <b><i>Y</i><sub>B</sub> = " + fr(YB, 0) + " N</b></p>" +
      "<p>Σ<i>X</i> : <i>X</i><sub>A</sub> + (" + fr(fx, 0) + ") = 0 ⇒ <b><i>X</i><sub>A</sub> = " + fr(XA, 0) + " N</b></p>" +
      "<p>Σ<i>Y</i> : <i>Y</i><sub>A</sub> + <i>Y</i><sub>B</sub> + (" + fr(fy, 0) + ") = 0 ⇒ <b><i>Y</i><sub>A</sub> = " + fr(YA, 0) + " N</b></p>" +
      "<p>‖<i>A</i>‖ = " + fr(Math.hypot(XA, YA), 0) + " N ; ‖<i>B</i>‖ = " + fr(Math.abs(YB), 0) + " N</p></div>";
    var df = [F > 0 && Math.abs(YA - YB) < 1, F > 0 && Math.abs(XA) < 1, F > 0 && Math.abs(YB) < 1 && Math.abs(YA) > 1];
    ["#df-1 b", "#df-2 b", "#df-3 b"].forEach(function (s, i) { if (df[i]) q(s).textContent = "✔ Réussi !"; });
  }
  function montrer(n) {
    etape = n;
    ets.forEach(function (e, i) { e.classList.toggle("vu", i < n); });
    steps.forEach(function (s, i) { s.classList.toggle("on", i === n - 1); });
    q("#pe-next").disabled = n >= 4;
  }
  q("#pe-next").addEventListener("click", function () { montrer(Math.min(4, etape + 1)); });
  q("#pe-all").addEventListener("click", function () { montrer(4); });
  q("#pe-reset").addEventListener("click", function () { montrer(0); });
  [PF, PA, PAL].forEach(function (el) { el.addEventListener("input", poutre); });
  poutre(); montrer(0);

  // ---------- 8. quiz
  var qs = qa(".quiz-q");
  function score() {
    var n = qs.filter(function (f) { return f.classList.contains("is-ok"); }).length;
    var done = qs.filter(function (f) { return f.classList.contains("done"); }).length;
    var st = n === qs.length ? 3 : n >= qs.length - 2 ? 2 : n >= 2 ? 1 : 0;
    q("#qz-score").textContent = n + " / " + qs.length;
    q("#qz-stars").textContent = done === qs.length ? "★★★".slice(0, st) + "☆☆☆".slice(0, 3 - st) : "";
  }
  qs.forEach(function (fs) {
    fs.addEventListener("change", function (e) {
      if (fs.classList.contains("done")) return;
      var ok = e.target.value === fs.getAttribute("data-ok");
      fs.classList.add("done", ok ? "is-ok" : "is-ko");
      fs.querySelector(".quiz-fb").textContent = ok ? "✔ Bonne réponse !" : "✘ Pas tout à fait.";
      fs.querySelector(".quiz-why").hidden = false;
      Array.prototype.forEach.call(fs.querySelectorAll("input"), function (i) {
        i.disabled = true;
        if (i.value === fs.getAttribute("data-ok")) i.parentNode.classList.add("good");
      });
      score();
    });
  });
  q("#qz-reset").addEventListener("click", function () {
    qs.forEach(function (fs) {
      fs.classList.remove("done", "is-ok", "is-ko");
      fs.querySelector(".quiz-fb").textContent = "";
      fs.querySelector(".quiz-why").hidden = true;
      Array.prototype.forEach.call(fs.querySelectorAll("input"), function (i) { i.disabled = false; i.checked = false; i.parentNode.classList.remove("good"); });
    });
    score();
  });
  score();
  q("#cours-print").addEventListener("click", function () { window.print(); });
})();
</script>"""
