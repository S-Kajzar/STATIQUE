#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cours 1.1 (Niveau 1) — Statique graphique, page autonome et interactive.

Contenu repris du cours « Séquence : Statique — Cours » : fonction du PFS, isoler un solide, définition du PFS,
hypothèses, traduction graphique (solide soumis à deux forces : bielle ; solide soumis à trois forces : levier de la
bride de serrage, résolu en trois étapes). S'y ajoutent un jeu d'isolement, une bielle qu'on fait tourner, la
résolution du levier pas à pas sur la figure, un dynamique interactif et un quiz. Appelé par src/generer.py.
"""
import math

from cours3 import COURS3_CSS, _carte, _sec, _vec
from niveau3 import HOUSE, esc, png

# ============================================================ géométrie du levier (fond g-levier.png, 377 × 439 px)
E, B, XF = (169.5, 57.0), (56.0, 313.0), 282.0
F_BAS, F_HAUT = (282.0, 352.0), (282.0, 195.0)      # flèche orange de la figure : 6 000 N
U6 = (1 / math.hypot(1, 0.18), 0.18 / math.hypot(1, 0.18))   # direction de la biellette 6 (DE)
I = (XF, E[1] + U6[1] / U6[0] * (XF - E[0]))
_ub = (I[0] - B[0], I[1] - B[1])
UB = (_ub[0] / math.hypot(*_ub), _ub[1] / math.hypot(*_ub))
F = 6000.0


def _solve(Fv, u, v):
    d = u[0] * v[1] - u[1] * v[0]
    return (-Fv[0] * v[1] + Fv[1] * v[0]) / d, (-u[0] * Fv[1] + u[1] * Fv[0]) / d


A6, A1 = _solve((0, -F), U6, UB)        # F6 = A6·U6 ; F1 = A1·UB
N6, N1 = abs(A6), abs(A1)
KPX = (F_BAS[1] - F_HAUT[1]) / F       # pixels par newton sur la figure
ANG6 = math.degrees(math.atan2(-U6[1], U6[0]))
ANGB = math.degrees(math.atan2(-UB[1], UB[0]))


def arr(x):
    """Lecture graphique : arrondi à la centaine."""
    return frn(round(x, -2))


def frn(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def _ext(p, u, t0=-600, t1=600):
    return (p[0] + t0 * u[0], p[1] + t0 * u[1], p[0] + t1 * u[0], p[1] + t1 * u[1])


def levier_svg():
    src, w, h = png("g-levier")
    e1 = _ext(E, U6)
    b1 = _ext(B, UB)
    f6 = (E[0] + A6 * KPX * U6[0] * 0.6, E[1] + A6 * KPX * U6[1] * 0.6)
    f1 = (B[0] + A1 * KPX * UB[0] * 0.3, B[1] + A1 * KPX * UB[1] * 0.3)
    return f"""<svg class="lev-svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="lev-t">
<title id="lev-t">Levier de la bride isolé : forces en F, E et B</title>
<defs><marker id="lv-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>
<image href="{src}" x="0" y="0" width="{w}" height="{h}"/>
<g class="lv lv-1"><line x1="{F_BAS[0]}" y1="{F_BAS[1]}" x2="{F_HAUT[0]}" y2="{F_HAUT[1]}" stroke="#E67E22" stroke-width="4" marker-end="url(#lv-ah)"/>
<text x="{F_BAS[0] - 8}" y="{F_BAS[1] - 40}" text-anchor="end" class="lv-t" fill="#E67E22">6 000 N</text></g>
<g class="lv lv-2"><line x1="{e1[0]:.1f}" y1="{e1[1]:.1f}" x2="{e1[2]:.1f}" y2="{e1[3]:.1f}" stroke="#17A2B8" stroke-width="2" stroke-dasharray="8 5"/>
<text x="{E[0] + 26}" y="{E[1] - 16}" class="lv-t" fill="#138496">direction (DE)</text></g>
<g class="lv lv-3"><line x1="{XF}" y1="0" x2="{XF}" y2="{h}" stroke="#E67E22" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="{I[0]:.1f}" cy="{I[1]:.1f}" r="6" fill="#C62828"/><text x="{I[0] + 9:.1f}" y="{I[1] - 8:.1f}" class="lv-t" fill="#C62828">I</text></g>
<g class="lv lv-4"><line x1="{b1[0]:.1f}" y1="{b1[1]:.1f}" x2="{b1[2]:.1f}" y2="{b1[3]:.1f}" stroke="#1B7A43" stroke-width="2" stroke-dasharray="8 5"/>
<text x="{B[0] + 70}" y="{B[1] - 100}" class="lv-t" fill="#1B7A43">direction (BI)</text></g>
<g class="lv lv-5"><line x1="{E[0]}" y1="{E[1]}" x2="{f6[0]:.1f}" y2="{f6[1]:.1f}" stroke="#17A2B8" stroke-width="4" marker-end="url(#lv-ah)"/>
<line x1="{B[0]}" y1="{B[1]}" x2="{f1[0]:.1f}" y2="{f1[1]:.1f}" stroke="#1B7A43" stroke-width="4" marker-end="url(#lv-ah)"/></g>
</svg>"""


def dynamique_svg():
    k = 0.03                       # pixels par newton du dessin du dynamique
    S = (230.0, 235.0)
    T = (S[0], S[1] - F * k)
    Q = (T[0] + A1 * UB[0] * k, T[1] + A1 * UB[1] * k)
    return f"""<svg class="dyn-svg" viewBox="0 0 300 260" role="img" aria-labelledby="dy-t">
<title id="dy-t">Dynamique des forces du levier : triangle fermé</title>
<defs><marker id="dy-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>
<line x1="{S[0]}" y1="{S[1]}" x2="{T[0]}" y2="{T[1]:.1f}" stroke="#E67E22" stroke-width="3.5" marker-end="url(#dy-ah)"/>
<line x1="{T[0]}" y1="{T[1]:.1f}" x2="{Q[0]:.1f}" y2="{Q[1]:.1f}" stroke="#1B7A43" stroke-width="3.5" marker-end="url(#dy-ah)"/>
<line x1="{Q[0]:.1f}" y1="{Q[1]:.1f}" x2="{S[0]}" y2="{S[1]}" stroke="#17A2B8" stroke-width="3.5" marker-end="url(#dy-ah)"/>
<text x="{S[0] + 8}" y="{(S[1] + T[1]) / 2:.1f}" class="lv-t" fill="#E67E22">6 000 N</text>
<text x="{(T[0] + Q[0]) / 2 - 8:.1f}" y="{(T[1] + Q[1]) / 2 - 8:.1f}" class="lv-t" fill="#1B7A43" text-anchor="end">F1 ≈ {arr(N1)} N</text>
<text x="{(Q[0] + S[0]) / 2:.1f}" y="{(Q[1] + S[1]) / 2 + 22:.1f}" text-anchor="middle" class="lv-t" fill="#138496">F6 ≈ {arr(N6)} N</text>
</svg>"""


ISOLE = [("Action de la pièce serrée sur le levier, en F", True),
         ("Action de la biellette 6 sur le levier, en E", True),
         ("Action du corps 1 sur le levier, en B (articulation)", True),
         ("Poids du levier", False),
         ("Action du levier sur la pièce serrée", False),
         ("Action de l'huile sur le piston 3", False)]

QUIZ = [
    ("Isoler un solide, c'est…", ["l'imaginer seul et recenser les actions extérieures", "le peser", "supprimer ses liaisons"], 0,
     "On l'imagine seul et on fait le bilan de toutes les actions extérieures qui s'exercent sur lui."),
    ("Un solide soumis à deux forces est en équilibre si elles ont…",
     ["même direction, même intensité, sens contraires", "même sens et même intensité", "des directions perpendiculaires"], 0,
     "Les deux forces sont directement opposées, portées par la droite qui joint leurs points d'application."),
    ("Une bielle est articulée en A et B, son poids est négligé. La droite d'action des forces est…",
     ["verticale", "(AB)", "perpendiculaire à (AB)"], 1, "Solide soumis à deux forces : droite d'action (AB)."),
    ("Pour un solide soumis à trois forces non parallèles, les droites d'action…",
     ["sont parallèles", "se coupent en un même point", "sont perpendiculaires"], 1,
     "Elles sont concourantes : c'est ainsi qu'on trouve la direction inconnue."),
    ("Le dynamique des forces d'un solide en équilibre sous trois forces est…",
     ["un triangle fermé", "une droite", "un carré"], 0, "Mises bout à bout, les trois forces forment un triangle fermé."),
    ("À l'échelle 1 cm ↔ 200 N, un vecteur de 3,5 cm représente…", ["57 N", "700 N", "350 N"], 1, "3,5 × 200 = 700 N."),
    ("L'action de A sur B et l'action de B sur A sont…", ["égales", "opposées", "perpendiculaires"], 1,
     "Principe des actions mutuelles : même droite d'action, même intensité, sens contraires."),
    ("Dans le dynamique, les vecteurs se suivent…", ["origine contre origine", "bout à bout, dans un seul sens de parcours",
                                                     "dans n'importe quel ordre de sens"], 1,
     "L'extrémité de l'un est l'origine du suivant : c'est ce qui donne le sens des forces inconnues."),
]


def render_cours1(style, hub_css):
    nav_items = [("k1-fct", "Isoler"), ("k1-pfs", "PFS"), ("k1-deux", "Deux forces"), ("k1-trois", "Trois forces"),
                 ("k1-ex", "Exemple résolu"), ("k1-dyn", "Dynamique"), ("k1-meth", "Méthode"), ("k1-quiz", "Quiz")]
    nav = "".join(f'<a href="#{a}">{n}. {t}</a>' for n, (a, t) in enumerate(nav_items, 1))
    bsrc, bw, bh = png("g-bride")
    psrc, pw, ph = png("g-piece6")

    iso = "".join(f'<label class="iso-l" data-ok="{1 if ok else 0}"><input type="checkbox"> {t}<span class="iso-fb"></span></label>'
                  for t, ok in ISOLE)
    s1 = _sec(1, "k1-fct", "Fonction du PFS et isolement d'un solide",
              "<p>Le <b>principe fondamental de la statique</b> (PFS) permet de déterminer les efforts dans un système : "
              "on en a besoin pour choisir un vérin, dimensionner un axe, vérifier une pièce.</p>"
              "<p>En physique, il faut d'abord bien définir le système étudié : on dit qu'on <b>isole</b> le système. "
              "Isoler, c'est l'imaginer seul et <b>recenser les efforts extérieurs</b> qui s'exercent sur lui.</p>"
              '<div class="cours-split"><figure class="fig" style="max-width:340px">'
              f'<img src="{bsrc}" width="{bw}" height="{bh}" alt="Bride de serrage hydraulique : corps 1, piston, levier, '
              'biellette 6, vis de serrage"><figcaption>Bride de serrage : le levier pivote en B sur le corps, la biellette '
              "6 le relie en E, la vis serre la pièce en F.</figcaption></figure>"
              f'<div class="jeu"><h3>Jeu : on isole le levier de la bride</h3><p>Coche les actions <b>extérieures au '
              f'levier</b> qui font partie de son bilan (poids négligé).</p><div class="iso">{iso}</div>'
              '<p class="k3-foot"><button type="button" class="btn" id="iso-ok">Vérifier</button> '
              '<b id="iso-fb" aria-live="polite"></b></p></div></div>')
    cartes = "".join([
        _carte("Condition 1", "Que vaut la somme vectorielle des forces extérieures ?",
               f"Elle est <b>nulle</b> : {_vec('F', '1')} + {_vec('F', '2')} + {_vec('F', '3')} + … = {_vec('0')}"),
        _carte("Condition 2", "Que vaut la somme des moments en un point A ?",
               "Elle est <b>nulle</b>, en n'importe quel point A : M<sub>A</sub>(F<sub>1</sub>) + M<sub>A</sub>(F<sub>2</sub>) + … = 0"),
    ])
    s2 = _sec(2, "k1-pfs", "Le principe fondamental de la statique",
              "<p>Un solide indéformable en équilibre sous l'action de <i>n</i> forces extérieures reste en équilibre si "
              "deux conditions sont réunies :</p>"
              f'<p class="cours-defi">À toi : réponds dans ta tête, puis retourne les cartes.</p><div class="k3-cartes">{cartes}</div>'
              "<h3>Hypothèses de travail</h3><ul><li>le <b>poids</b> des pièces peut être négligé (devant les efforts "
              "transmis) ;</li><li>les solides sont supposés <b>indéformables</b> ;</li><li>on néglige, lorsque c'est "
              "possible, les <b>frottements</b> entre les pièces.</li></ul>")
    s3 = _sec(3, "k1-deux", "Solide soumis à l'action de deux forces",
              '<div class="cours-split"><div><div class="enonce">Les deux forces ont la <b>même direction</b>, un '
              "<b>sens contraire</b> et la <b>même intensité</b>.</div><p>La direction commune est la droite qui joint "
              "les deux points d'application. Exemple : une <b>bielle</b> articulée en A et B, de poids négligé.</p>"
              '<div class="tab-wrap"><table class="t"><thead><tr><th>Vecteur</th><th>Origine</th><th>Droite d\'action</th><th>Sens</th><th>Norme</th>'
              "</tr></thead><tbody><tr><td>F<sub>1 ext/bielle</sub></td><td>A</td><td>(AB)</td><td>de B vers A</td><td>1 000 N</td></tr>"
              "<tr><td>F<sub>2 ext/bielle</sub></td><td>B</td><td>(AB)</td><td>de A vers B</td><td>1 000 N</td></tr></tbody></table></div></div>"
              '<div class="simu k1-biel"><h3>La bielle tourne, les forces suivent</h3>'
              '<svg class="biel-svg" viewBox="0 0 320 220" role="img" aria-label="Bielle AB et ses deux forces">'
              '<defs><marker id="bi-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>'
              '<g id="biel-g"><line x1="-150" y1="0" x2="150" y2="0" stroke="#9AA2A8" stroke-dasharray="5 4"/>'
              '<rect x="-80" y="-13" width="160" height="26" rx="13" fill="#D9E4F2" stroke="#1C2530" stroke-width="2"/>'
              '<circle cx="70" cy="0" r="6" fill="#fff" stroke="#1C2530" stroke-width="2"/><circle cx="-70" cy="0" r="6" fill="#fff" stroke="#1C2530" stroke-width="2"/>'
              '<line id="biel-f1" x1="70" y1="0" x2="140" y2="0" stroke="#1B7A43" stroke-width="4" marker-end="url(#bi-ah)"/>'
              '<line id="biel-f2" x1="-70" y1="0" x2="-140" y2="0" stroke="#1B7A43" stroke-width="4" marker-end="url(#bi-ah)"/>'
              '<text x="70" y="-18" class="lv-t" text-anchor="middle">A</text><text x="-70" y="-18" class="lv-t" text-anchor="middle">B</text></g></svg>'
              '<div class="simu-grid k3-col"><label><span>Inclinaison de la bielle : <output id="bi-oa">20°</output></span>'
              '<input type="range" id="bi-a" min="-80" max="80" step="5" value="20"></label>'
              '<label><span>Effort : <output id="bi-of">1 000 N</output></span><input type="range" id="bi-f" min="200" max="1600" step="100" value="1000"></label></div>'
              '<p class="small">Quelle que soit l\'inclinaison, les deux forces restent portées par (AB), égales et opposées : '
              "c'est la seule façon pour la bielle de ne pas bouger.</p></div></div>")
    s4 = _sec(4, "k1-trois", "Solide soumis à l'action de trois forces",
              "<p>Exemple : le <b>levier de la bride de serrage</b> isolé. Il est soumis à trois forces : l'action de la "
              "pièce serrée en F, l'action de la biellette 6 en E et l'action du corps 1 en B.</p>"
              '<div class="enonce">Traduction graphique du PFS pour un solide soumis à trois forces (non parallèles) :<br>'
              "1. les <b>directions des forces se coupent en un seul et même point</b> ;<br>"
              "2. le <b>dynamique des forces</b> est fermé : les trois vecteurs mis bout à bout forment un triangle.</div>"
              f'<figure class="fig" style="max-width:210px"><img src="{psrc}" width="{pw}" height="{ph}" alt="Pièce 6 : '
              'biellette articulée en D et E"><figcaption>La pièce 6 (biellette) est soumise à deux forces : sa direction '
              "est (DE).</figcaption></figure>")
    etapes = [
        ("Étape 1 — la force connue", "On connaît la force que le levier doit exercer sur la pièce : 6 000 N. Par le "
         "principe des actions mutuelles, F<sub>pièce/levier</sub> = 6 000 N, verticale, vers le haut, appliquée en F."),
        ("Étape 2a — une direction par un solide à deux forces", "La biellette 6 est soumise à deux forces : sa direction "
         "est (DE). Par actions mutuelles, F<sub>6/levier</sub> a la même direction, qui passe par E."),
        ("Étape 2b — le point de concours", "La verticale de F et la direction de F<sub>6/levier</sub> se coupent en I."),
        ("Étape 2c — la direction inconnue", "La troisième force, F<sub>1/levier</sub>, passe par B et par I : sa direction "
         f"est (BI), inclinée d'environ {frn(ANGB, 0)}°."),
        ("Étape 3 — le dynamique", "On trace la force connue à l'échelle (1 cm ↔ 2 000 N : 3 cm pour 6 000 N), puis, "
         "par ses extrémités, les parallèles aux deux directions : elles ferment le triangle. Les vecteurs se suivent bout à "
         f"bout ; on mesure : F<sub>6/levier</sub> ≈ {arr(N6)} N, F<sub>1/levier</sub> ≈ {arr(N1)} N."),
    ]
    et_html = "".join(f'<li class="k3-step" data-s="{i}"><span class="k3-sn">{i + 1}</span><div><b>{t}</b><p>{d}</p></div></li>'
                      for i, (t, d) in enumerate(etapes))
    tab_rows = [("F<sub>pièce/levier</sub>", "F", "verticale", "vers le haut", "6 000 N", 0),
                ("F<sub>6/levier</sub>", "E", f"(DE), ≈ {frn(abs(ANG6), 0)}° sous l'horizontale", "vers la droite et le bas", f"≈ {arr(N6)} N", 1),
                ("F<sub>1/levier</sub>", "B", f"(BI), ≈ {frn(ANGB, 0)}°", "vers la gauche et le bas", f"≈ {arr(N1)} N", 3)]
    tab = "".join(f'<tr><td>{n}</td><td>{o}</td><td class="ev" data-e="{e}">{d}</td><td class="ev" data-e="{4 if e else 0}">{s}</td>'
                  f'<td class="ev" data-e="{4 if e else 0}">{v}</td></tr>' for n, o, d, s, v, e in tab_rows)
    s5 = _sec(5, "k1-ex", "Exemple résolu pas à pas : le levier de la bride",
              '<div class="k1-ex-g"><div>' + levier_svg() + "</div><div>" +
              f'<ol class="k3-steps k1-steps">{et_html}</ol>'
              '<p class="k3-foot"><button type="button" class="btn" id="lv-next">Étape suivante</button> '
              '<button type="button" class="btn ghost" id="lv-all">Tout afficher</button> '
              '<button type="button" class="btn ghost" id="lv-reset">Recommencer</button></p></div></div>'
              '<div class="k1-ex-g"><div><h3>Tableau des caractéristiques</h3><div class="tab-wrap"><table class="t k1-tab"><thead><tr><th>Vecteur</th>'
              f"<th>Origine</th><th>Droite d'action</th><th>Sens</th><th>Norme</th></tr></thead><tbody>{tab}</tbody></table></div>"
              '<p class="small">Les cases se remplissent au fil des étapes. Le cours d\'origine annonce 4 600 N et 6 800 N, '
              "lus sur un tracé à la main ; la construction précise sur la figure donne les valeurs ci-dessus.</p></div>"
              f'<div class="k1-dyn-box ev" data-e="4"><h3>Dynamique des forces</h3>{dynamique_svg()}</div></div>')
    s6 = _sec(6, "k1-dyn", "À toi : le dynamique interactif",
              "<p>Une force connue <b>P</b>, verticale vers le bas, et deux directions connues. Fais varier les directions : "
              "le triangle se referme toujours, et les intensités se lisent sur ses côtés.</p>"
              '<div class="simu"><div class="k3-mom-g"><svg class="tri-svg" viewBox="0 0 420 340" role="img" aria-label="Dynamique des trois forces">'
              '<defs><marker id="tr-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>'
              '<line id="tr-p" stroke="#C62828" stroke-width="4" marker-end="url(#tr-ah)"/><line id="tr-2" stroke="#1B7A43" stroke-width="4" marker-end="url(#tr-ah)"/>'
              '<line id="tr-3" stroke="#1F5FA8" stroke-width="4" marker-end="url(#tr-ah)"/>'
              '<line id="tr-d2" stroke="#1B7A43" stroke-width="1" stroke-dasharray="5 4"/><line id="tr-d3" stroke="#1F5FA8" stroke-width="1" stroke-dasharray="5 4"/>'
              '<text id="tr-tp" class="lv-t" fill="#C62828"></text><text id="tr-t2" class="lv-t" fill="#1B7A43"></text><text id="tr-t3" class="lv-t" fill="#1F5FA8"></text></svg>'
              '<div class="simu-grid k3-col"><label><span>Intensité de P : <output id="tr-op">400 N</output></span><input type="range" id="tr-ip" min="100" max="800" step="50" value="400"></label>'
              '<label><span>Direction de F<sub>2</sub> : <output id="tr-o2">20°</output></span><input type="range" id="tr-i2" min="0" max="175" step="5" value="20"></label>'
              '<label><span>Direction de F<sub>3</sub> : <output id="tr-o3">120°</output></span><input type="range" id="tr-i3" min="0" max="175" step="5" value="120"></label>'
              '<p class="small">Angles mesurés depuis l\'horizontale. Échelle : 1 cm ↔ 100 N (1 cm = 40 px à l\'écran).</p></div></div>'
              '<div class="simu-out"><div><span>P (connue)</span><b id="tr-rp"></b></div><div><span>F<sub>2</sub></span><b id="tr-r2"></b></div>'
              '<div><span>F<sub>3</sub></span><b id="tr-r3"></b></div></div><p class="simu-verdict" id="tr-v"></p></div>')
    steps2 = [("Isoler", "Choisir le solide et faire le bilan des actions extérieures (tableau : nom, point "
               "d'application, direction, sens, intensité)."),
              ("Repérer les solides à deux forces", "Bielles, vérins, tirants, amortisseurs : leur direction est la droite "
               "qui joint leurs deux articulations. Reporter cette direction par actions mutuelles."),
              ("Trouver le point de concours", "Prolonger deux droites d'action connues jusqu'à leur intersection I ; la "
               "troisième direction passe par I."),
              ("Tracer le dynamique", "Choisir une échelle, tracer la force connue, mener par ses extrémités les parallèles "
               "aux deux autres directions, fermer le triangle bout à bout."),
              ("Conclure", "Mesurer, convertir avec l'échelle, compléter le tableau, répondre à la question posée.")]
    st_html = "".join(f'<li class="k3-step"><span class="k3-sn">{i + 1}</span><div><b>{t}</b><p>{d}</p></div></li>'
                      for i, (t, d) in enumerate(steps2))
    s7 = _sec(7, "k1-meth", "Méthode à retenir", f'<ol class="k3-steps">{st_html}</ol>'
              "<p>Dans les exercices, l'<b>atelier de tracé</b> te donne les outils du dessinateur : vecteur à l'échelle, "
              "droite d'action, parallèle, point, mesure — sur le document réponse affiché en transparence.</p>")
    quiz = "".join(
        f'<fieldset class="quiz-q" data-ok="{ok}"><legend><span class="q-num">{i + 1}</span> {q}</legend>' +
        "".join(f'<label><input type="radio" name="k1q{i}" value="{j}"> {o}</label>' for j, o in enumerate(opts)) +
        f'<p class="quiz-fb" aria-live="polite"></p><p class="quiz-why" hidden>{why}</p></fieldset>'
        for i, (q, opts, ok, why) in enumerate(QUIZ))
    s8 = _sec(8, "k1-quiz", "Quiz : vérifie tes connaissances",
              f'<p>Choisis une réponse : la correction s\'affiche aussitôt.</p><div class="quiz">{quiz}</div>'
              f'<div class="quiz-score" aria-live="polite"><span id="qz-score">0 / {len(QUIZ)}</span><span id="qz-stars" '
              'aria-hidden="true"></span><button type="button" class="btn ghost" id="qz-reset">Recommencer</button></div>')
    liens = "".join(f'<a class="btn ghost" href="{h}">{t}</a>' for h, t in
                    [("panneau-solaire.html", "Exercice 1.2 — Panneau solaire"), ("pince-kobelco.html", "Exercice 1.3 — Pince"),
                     ("cric-hydraulique.html", "Exercice 1.4 — Cric"), ("suspension-vtt.html", "Exercice 1.5 — Suspension de VTT")])
    body = f"""<div class="cours" id="cours-1">
<nav class="c-top no-print" aria-label="Navigation"><a href="index.html">{HOUSE} Accueil</a></nav>
<div class="home-top home-top-single"><div class="home-top-l"><header class="home-head"><span class="mc-tag">Cours 1.1</span> <span class="pastille">Niveau 1</span>
<h1 id="home-title">Statique graphique</h1><p class="home-sub">Isoler un solide, appliquer le principe fondamental de la statique et
le traduire graphiquement : solide soumis à deux forces, solide soumis à trois forces, point de concours et dynamique des
forces. Environ 45 minutes, avec un jeu d'isolement, une bielle animée, un exemple résolu pas à pas, un dynamique
interactif et un quiz.</p></header></div></div>
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
<!-- Fichier généré par src/generer.py (contenu : src/cours1.py) : ne pas modifier à la main. -->
<title>Statique graphique — cours — Statique</title>
<meta name="description" content="Cours interactif de statique graphique (niveau 1) : isoler un solide, PFS, solide soumis à deux et à trois forces, point de concours, dynamique des forces, quiz.">
{style}
{hub_css}
{COURS3_CSS}
{CSS}
</head>
<body class="no-mode hub cours-page">
<section id="home" aria-labelledby="home-title"><div class="home-inner">{body}</div></section>
{JS}
</body>
</html>
"""


CSS = """<style>
.lv-t{font:700 13px var(--f-texte)}
.tab-wrap{overflow-x:auto; max-width:100%}
.k1-ex-g>div{min-width:0}
.k1-ex-g{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.1fr); gap:16px; align-items:start; margin:6px 0 14px}
@media (max-width:760px){ .k1-ex-g{grid-template-columns:1fr} }
.lev-svg{width:100%; max-width:430px; height:auto; background:#fff; border:1px solid var(--trait-fin)}
.lev-svg .lv{opacity:0; transition:opacity .35s}
.lev-svg .lv.on{opacity:1}
.k1-steps .k3-step{opacity:.45} .k1-steps .k3-step.vu{opacity:1}
.k1-tab td.ev{color:transparent; background:repeating-linear-gradient(135deg,#F4F5F2 0 8px,#ECEEEA 8px 16px)}
.k1-tab td.ev.on{color:inherit; background:var(--vert-pale)}
.k1-dyn-box{opacity:.15; transition:opacity .35s} .k1-dyn-box.on{opacity:1}
.dyn-svg{width:100%; max-width:320px; height:auto; background:#fff; border:1px solid var(--trait-fin)}
.biel-svg,.tri-svg{width:100%; height:auto; background:#fff; border:1px solid var(--trait-fin)}
.k1-biel{display:block}
.iso{display:grid; gap:4px}
.iso-l{display:flex; gap:8px; align-items:center; background:#fff; border:1px solid var(--trait-fin); padding:5px 8px; cursor:pointer}
.iso-l.ok{background:var(--vert-pale); border-color:var(--vert)} .iso-l.ko{background:var(--rouge-pale); border-color:var(--rouge)}
.iso-fb{margin-left:auto; font-weight:700}
#iso-fb.ok{color:var(--vert)} #iso-fb.ko{color:var(--rouge)}
@media print{ .lev-svg .lv,.k1-dyn-box{opacity:1!important} .k1-tab td.ev{color:inherit!important; background:none!important} }
</style>"""


JS = r"""<script>
(function () {
  "use strict";
  var root = document.getElementById("cours-1");
  function q(s) { return root.querySelector(s); }
  function qa(s) { return Array.prototype.slice.call(root.querySelectorAll(s)); }
  function fr(x, d) { return (Math.abs(x) < 0.5 * Math.pow(10, -d) ? 0 : x).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d }).replace("-", "−"); }
  function setLine(el, x1, y1, x2, y2) { el.setAttribute("x1", x1); el.setAttribute("y1", y1); el.setAttribute("x2", x2); el.setAttribute("y2", y2); }

  // ---------- 1. isolement du levier
  q("#iso-ok").addEventListener("click", function () {
    var bons = 0, tot = 0;
    qa(".iso-l").forEach(function (l) {
      var c = l.querySelector("input").checked, ok = (l.getAttribute("data-ok") === "1") === c;
      l.classList.toggle("ok", ok); l.classList.toggle("ko", !ok);
      l.querySelector(".iso-fb").textContent = ok ? "✔" : (l.getAttribute("data-ok") === "1" ? "✘ à garder" : "✘ à exclure");
      tot++; if (ok) bons++;
    });
    var fb = q("#iso-fb");
    fb.className = bons === tot ? "ok" : "ko";
    fb.textContent = bons === tot ? "✔ Bilan juste : trois actions extérieures." : bons + " / " + tot + " justes : relis l'énoncé de l'isolement.";
  });

  // ---------- 2. cartes à retourner
  qa(".k3-carte").forEach(function (b) {
    b.addEventListener("click", function () { b.setAttribute("aria-expanded", b.getAttribute("aria-expanded") === "true" ? "false" : "true"); });
  });

  // ---------- 3. bielle
  var BA = q("#bi-a"), BF = q("#bi-f");
  function bielle() {
    var a = +BA.value, f = +BF.value, L = 25 + f * 0.05;
    q("#bi-oa").textContent = a + "°"; q("#bi-of").textContent = fr(f, 0) + " N";
    q("#biel-g").setAttribute("transform", "translate(160 110) rotate(" + (-a) + ")");
    setLine(q("#biel-f1"), 70, 0, 70 + L, 0); setLine(q("#biel-f2"), -70, 0, -70 - L, 0);
  }
  [BA, BF].forEach(function (el) { el.addEventListener("input", bielle); }); bielle();

  // ---------- 5. levier pas à pas
  var lv = 0, LVMAX = 5, steps = qa(".k1-steps .k3-step");
  function levier(n) {
    lv = n;
    for (var i = 1; i <= 5; i++) { var g = q(".lv-" + i); if (g) g.classList.toggle("on", n >= i); }
    steps.forEach(function (s, i) { s.classList.toggle("vu", i < n); s.classList.toggle("on", i === n - 1); });
    qa(".ev").forEach(function (c) { c.classList.toggle("on", n > +c.getAttribute("data-e")); });
    q("#lv-next").disabled = n >= LVMAX;
  }
  q("#lv-next").addEventListener("click", function () { levier(Math.min(LVMAX, lv + 1)); });
  q("#lv-all").addEventListener("click", function () { levier(LVMAX); });
  q("#lv-reset").addEventListener("click", function () { levier(0); });
  levier(0);

  // ---------- 6. dynamique interactif (1 cm ↔ 100 N, 40 px/cm)
  var IP = q("#tr-ip"), I2 = q("#tr-i2"), I3 = q("#tr-i3"), K = 0.4;
  function tri() {
    var P = +IP.value, a2 = +I2.value * Math.PI / 180, a3 = +I3.value * Math.PI / 180;
    q("#tr-op").textContent = fr(P, 0) + " N"; q("#tr-o2").textContent = I2.value + "°"; q("#tr-o3").textContent = I3.value + "°";
    var u2 = [Math.cos(a2), -Math.sin(a2)], u3 = [Math.cos(a3), -Math.sin(a3)], Fp = [0, P];
    var d = u2[0] * u3[1] - u2[1] * u3[0], v = q("#tr-v");
    if (Math.abs(d) < 0.02) {
      ["#tr-2", "#tr-3", "#tr-d2", "#tr-d3"].forEach(function (s) { q(s).style.display = "none"; });
      q("#tr-r2").textContent = "—"; q("#tr-r3").textContent = "—";
      v.className = "simu-verdict ko"; v.textContent = "Directions parallèles : le triangle ne peut pas se fermer, il n'y a pas d'équilibre possible.";
      return;
    }
    ["#tr-2", "#tr-3", "#tr-d2", "#tr-d3"].forEach(function (s) { q(s).style.display = ""; });
    var a = (-Fp[0] * u3[1] + Fp[1] * u3[0]) / d, b = (-u2[0] * Fp[1] + u2[1] * Fp[0]) / d;
    var S = [210, 30], T = [S[0], S[1] + P * K], Q = [T[0] + a * u2[0] * K, T[1] + a * u2[1] * K];
    var pts = [S, T, Q], mx = Math.min(S[0], T[0], Q[0]), Mx = Math.max(S[0], T[0], Q[0]), my = Math.min(S[1], T[1], Q[1]), My = Math.max(S[1], T[1], Q[1]);
    var dx = 210 - (mx + Mx) / 2, dy = 170 - (my + My) / 2, sc = Math.min(1, 380 / (Mx - mx + 1), 300 / (My - my + 1));
    function t(p) { return [210 + (p[0] - (mx + Mx) / 2) * sc, 170 + (p[1] - (my + My) / 2) * sc]; }
    var s = t(S), tt = t(T), qq = t(Q);
    setLine(q("#tr-p"), s[0], s[1], tt[0], tt[1]); setLine(q("#tr-2"), tt[0], tt[1], qq[0], qq[1]); setLine(q("#tr-3"), qq[0], qq[1], s[0], s[1]);
    setLine(q("#tr-d2"), tt[0] - u2[0] * 500, tt[1] - u2[1] * 500, tt[0] + u2[0] * 500, tt[1] + u2[1] * 500);
    setLine(q("#tr-d3"), s[0] - u3[0] * 500, s[1] - u3[1] * 500, s[0] + u3[0] * 500, s[1] + u3[1] * 500);
    function lab(id, p1, p2, txt) { var el = q(id); el.textContent = txt; el.setAttribute("x", (p1[0] + p2[0]) / 2 + 8); el.setAttribute("y", (p1[1] + p2[1]) / 2 - 6); }
    lab("#tr-tp", s, tt, "P"); lab("#tr-t2", tt, qq, "F2"); lab("#tr-t3", qq, s, "F3");
    q("#tr-rp").textContent = fr(P, 0) + " N"; q("#tr-r2").textContent = fr(Math.abs(a), 0) + " N"; q("#tr-r3").textContent = fr(Math.abs(b), 0) + " N";
    v.className = "simu-verdict ok";
    v.textContent = "Triangle fermé : F2 ≈ " + fr(Math.abs(a), 0) + " N et F3 ≈ " + fr(Math.abs(b), 0) + " N." +
      (Math.max(Math.abs(a), Math.abs(b)) > 2 * P ? " Directions presque parallèles : les forces deviennent très grandes !" : "");
  }
  [IP, I2, I3].forEach(function (el) { el.addEventListener("input", tri); }); tri();

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
