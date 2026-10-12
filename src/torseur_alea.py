#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exercice 2.1 (Niveau 2) — Déplacer un torseur : entraînement à valeurs aléatoires, page autonome.

Chaque tirage donne un torseur connu au point A et les coordonnées de A et de B ; l'élève écrit le vecteur BA puis le
torseur au point B (relation de Varignon : la résultante ne change pas, M_B = M_A + BA ∧ R). Trois niveaux : glisseur
dans le plan, torseur quelconque dans le plan, torseur dans l'espace. Correction pas à pas, score, série de 10 tirages
notée sur 20. L'adresse ?seed=… rend les tirages reproductibles (tests). Appelé par src/generer.py.
"""
from cours3 import COURS3_CSS, _vec
from niveau3 import HOUSE


def render_torseur_alea(style, hub_css):
    rappel = ('<p>La <b>résultante</b> ' + _vec("R") + ' ne change pas d\'un point à l\'autre ; le <b>moment</b> se '
              "transporte par la relation de Varignon (« BABAR ») :</p>"
              '<div class="formule"><span class="f-main">' + _vec("M") + "<sub>B</sub> = " + _vec("M") + "<sub>A</sub> + " +
              _vec("BA") + " ∧ " + _vec("R") + '</span><span class="f-units">' + _vec("BA") +
              " = A − B (coordonnées de A moins celles de B)</span></div>"
              "<p>Avec " + _vec("BA") + " (<i>a</i>, <i>b</i>, <i>c</i>) et " + _vec("R") + " (<i>X</i>, <i>Y</i>, <i>Z</i>) :</p>"
              '<div class="formule"><span class="f-main">' + _vec("BA") + " ∧ " + _vec("R") + " = ( <i>b</i>·<i>Z</i> − "
              "<i>c</i>·<i>Y</i> ; <i>c</i>·<i>X</i> − <i>a</i>·<i>Z</i> ; <i>a</i>·<i>Y</i> − <i>b</i>·<i>X</i> )</span>"
              '<span class="f-units">dans le plan (x, y), seule la 3<sup>e</sup> composante reste :<br><i>N</i><sub>B</sub> = '
              "<i>N</i><sub>A</sub> + <i>a</i>·<i>Y</i> − <i>b</i>·<i>X</i></span></div>")
    body = f"""<div class="ta-app" id="ta">
<header class="ta-top">
  <div class="ta-id"><a class="ta-home no-print" href="index.html" title="Retour à l'accueil" aria-label="Retour à l'accueil">{HOUSE}</a>
    <span class="mc-tag">Exercice 2.1</span><span class="pastille n2">Niveau 2</span>
    <h1 id="home-title">Déplacer un torseur</h1></div>
  <div class="ta-niv" role="group" aria-label="Choisir le niveau">
    <button type="button" data-niv="1" aria-pressed="true" title="Glisseur dans le plan : moment nul en A">1 · Glisseur plan</button>
    <button type="button" data-niv="2" aria-pressed="false" title="Torseur quelconque dans le plan">2 · Torseur plan</button>
    <button type="button" data-niv="3" aria-pressed="false" title="Torseur dans l'espace">3 · Torseur 3D</button></div>
  <details class="ta-aide"><summary>Rappel</summary><div class="ta-pop">{rappel}</div></details>
  <div class="ta-score" aria-live="polite"><span>Tirage <b id="ta-n">1</b></span><span>Réussis <b id="ta-ok">0</b>/<b id="ta-tot">0</b></span>
    <span>Série <b id="ta-serie">0</b></span><span>Sur 10 : <b id="ta-dix">0 / 10</b></span></div>
</header>
<div class="ta-fin" id="ta-fin" hidden></div>
<main class="ta-grid">
  <section class="ta-col ta-col-don" aria-labelledby="ta-h-don"><h2 id="ta-h-don"><span>1</span> Données</h2>
    <p id="ta-txt"></p><div class="ta-donnees" id="ta-donnees"></div>
    <svg class="ta-svg" id="ta-svg" viewBox="0 0 360 300" role="img" aria-label="Points A et B, résultante en A"></svg>
    <p class="ta-3d small" id="ta-3d" hidden>Pas de figure en 3D : travaille sur les coordonnées.</p></section>
  <section class="ta-col ta-col-rep" aria-labelledby="ta-h-rep"><h2 id="ta-h-rep"><span>2</span> Ta réponse</h2>
    <h3>Le vecteur <span class="vec">BA</span> (en m)</h3><div class="ta-row" id="ta-ba"></div>
    <h3>Le torseur au point B (N et N·m)</h3><div class="ta-tor" id="ta-tb"></div>
    <div class="ta-act"><button type="button" class="btn" id="ta-check" title="Touche Entrée">Vérifier</button>
      <button type="button" class="btn ghost" id="ta-sol" title="Le tirage compte alors comme manqué">Correction</button>
      <button type="button" class="btn ghost" id="ta-new">Nouveau tirage</button></div>
    <p class="ta-fb" id="ta-fb" aria-live="polite"></p></section>
  <section class="ta-col ta-col-cor" id="ta-col-cor" aria-labelledby="ta-h-cor"><h2 id="ta-h-cor"><span>3</span> Correction</h2>
    <p class="ta-vide small" id="ta-vide">La correction pas à pas s'affiche ici dès que ta réponse est juste, ou avec
    le bouton « Correction » (le tirage compte alors comme manqué).</p>
    <div class="ta-corr" id="ta-corr" hidden></div></section>
</main>
<footer class="ta-foot small"><p>Saisie : nombres décimaux avec une virgule ou un point, signe compris ; <kbd>Tab</kbd> passe
à la case suivante, <kbd>Entrée</kbd> vérifie, puis lance le tirage suivant quand tout est juste. Tolérance : ± 0,01 m sur
BA, ± 0,5 % (au moins 0,1) sur le torseur. Un tirage n'est compté réussi que si tout est juste à la première vérification.</p>
<p class="no-print"><a href="cours-statique-analytique.html">Cours 3 — Statique analytique</a> · <a href="coffre-fort.html">Exercice 2.2</a>
· <a href="echelle-pompier.html">Exercice 2.3</a> · <a href="cadre-velo.html">Exercice 2.4</a> · <a href="index.html">Accueil</a></p></footer>
</div>"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Fichier généré par src/generer.py (contenu : src/torseur_alea.py) : ne pas modifier à la main. -->
<title>Déplacer un torseur — entraînement — Statique</title>
<meta name="description" content="Entraînement à valeurs aléatoires (niveau 2) : transporter un torseur d'un point A à un point B, dans le plan et dans l'espace, avec correction pas à pas.">
{style}
{hub_css}
{COURS3_CSS}
{CSS}
</head>
<body class="no-mode hub cours-page ta-page">
<section id="home" aria-labelledby="home-title">{body}</section>
{JS}
</body>
</html>
"""


CSS = """<style>
/* ---------- un seul écran : barre d'en-tête, puis données | réponse | correction côte à côte ---------- */
.ta-page #home{padding:10px 16px 16px}
.ta-app{max-width:1500px; margin:0 auto}
.ta-top{display:flex; flex-wrap:wrap; align-items:center; gap:8px 16px; background:var(--encre); color:#fff; padding:8px 12px; position:relative}
.ta-id{display:flex; align-items:center; gap:8px; flex-wrap:wrap}
#ta .ta-id h1{margin:0; font:800 1.25rem/1.2 var(--f-titre); color:#fff}
.ta-home{display:inline-flex; color:var(--jaune)} .ta-home svg{width:22px; height:22px}
.ta-niv{display:flex; gap:0; border:1.5px solid var(--jaune)}
.ta-niv button{background:transparent; color:#fff; border:0; border-right:1px solid rgba(255,255,255,.25); padding:6px 10px; font:700 .86rem var(--f-titre); cursor:pointer}
.ta-niv button:last-child{border-right:0}
.ta-niv button[aria-pressed=true]{background:var(--jaune); color:var(--encre)}
.ta-niv button:focus-visible{outline:2px solid #fff; outline-offset:-4px}
.ta-score{display:flex; flex-wrap:wrap; gap:4px 14px; font-size:.88rem; margin-left:auto}
.ta-score b{color:var(--jaune); font-family:var(--f-titre)}
.ta-aide{position:static} .ta-aide summary{cursor:pointer; list-style:none; border:1.5px solid #fff; padding:4px 10px; font:700 .86rem var(--f-titre)}
.ta-aide summary::-webkit-details-marker{display:none}
.ta-aide[open] summary{background:#fff; color:var(--encre)}
.ta-pop{position:absolute; right:12px; top:100%; z-index:20; width:min(560px, calc(100vw - 32px)); background:var(--papier); color:var(--encre);
  border:2px solid var(--encre); box-shadow:0 8px 24px rgba(0,0,0,.25); padding:6px 14px; font-size:.92rem}
.ta-pop .formule{margin:6px 0}
.ta-grid{display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,1.05fr); gap:12px; margin-top:10px; align-items:start}
@media (max-width:1180px){ .ta-grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr); grid-template-areas:"don rep" "cor rep"}
  .ta-col-don{grid-area:don} .ta-col-rep{grid-area:rep} .ta-col-cor{grid-area:cor} }
@media (max-width:700px){ .ta-grid{grid-template-columns:1fr; grid-template-areas:"don" "rep" "cor"} .ta-score{margin-left:0} }
.ta-col{background:#fff; border:1px solid var(--trait-fin); padding:8px 12px 10px; min-width:0}
.ta-col h2{display:flex; align-items:center; gap:8px; font:800 1.02rem var(--f-titre); margin:0 0 6px}
.ta-col h2 span{display:inline-grid; place-items:center; width:22px; height:22px; background:var(--encre); color:var(--jaune); font-size:.85rem}
.ta-col h3{font:700 .92rem var(--f-titre); margin:8px 0 4px}
.ta-col p{margin:0 0 6px}
#ta-txt{font-size:.92rem}
#ta .vec{line-height:1} #ta .vec::before{top:-.04em} #ta .vec::after{top:-.24em}
.ta-donnees{border-left:4px solid var(--bleu); padding:2px 10px; margin:0 0 6px}
.ta-donnees p{margin:2px 0}
.ta-donnees .torseur{font-size:.95rem}
.ta-svg{display:block; width:100%; max-height:min(300px, 36vh); background:#fff; border:1px solid var(--trait-fin)}
.ta-svg .ax{stroke:#9AA2A8; stroke-width:1}
.ta-svg text{font:700 13px var(--f-texte)}
.ta-row{display:flex; flex-wrap:wrap; gap:8px; align-items:flex-end}
.ta-f{position:relative; display:inline-flex; flex-direction:column; align-items:center; gap:2px; line-height:1.25; font-size:.78rem;
  color:var(--encre-2); padding-bottom:14px}
.ta-f input{width:6.2em; border:1.5px dashed var(--encre-2); padding:4px 5px; background:#fff; font:600 .95rem var(--f-texte); text-align:center}
.ta-f input:focus{outline:2px solid var(--jaune); outline-offset:1px; border-style:solid}
.ta-f.ok input{border:2px solid var(--vert); background:var(--vert-pale)}
.ta-f.ko input{border:2px solid var(--rouge); background:var(--rouge-pale)}
.ta-att{position:absolute; bottom:0; left:0; right:0; text-align:center; font:700 .74rem var(--f-texte); color:var(--vert); white-space:nowrap}
.ta-tor{display:inline-flex; align-items:center; gap:6px; flex-wrap:wrap; max-width:100%}
.ta-tor .tz-b td{padding:0 4px; text-align:center; min-width:0}
.ta-tor .dash{color:var(--encre-2); padding:0 1.6em}
.ta-act{display:flex; flex-wrap:wrap; gap:6px; margin-top:4px}
.ta-act .btn{padding:6px 11px; font-size:.9rem}
kbd{font:600 .72rem var(--f-texte); border:1px solid currentColor; border-radius:3px; padding:0 4px; margin-left:4px; opacity:.8}
.ta-fb{min-height:1.5em; margin:6px 0 0; font-weight:700}
.ta-fb.ok{color:var(--vert)} .ta-fb.ko{color:var(--rouge)}
.ta-corr{border-left:4px solid var(--vert); padding:0 10px; font-size:.9rem}
.ta-corr p{margin:3px 0}
.ta-corr .eq{line-height:1.7; margin:2px 0 4px}
.ta-corr .torseur{font-size:.92rem}
.ta-vide{color:var(--encre-2)}
.ta-fin{background:var(--jaune-pale); border:2px solid var(--jaune); padding:6px 12px; margin:8px 0 0; font:700 1.02rem var(--f-titre)}
.ta-foot{margin-top:12px; color:var(--encre-2)}
.ta-foot p{margin:4px 0}
@media (max-width:700px){ #ta .ta-id h1{font-size:1.1rem} .ta-niv button{padding:6px 7px; font-size:.8rem} }
</style>"""


JS = r"""<script>
(function () {
  "use strict";
  var root = document.getElementById("ta");
  function q(s) { return root.querySelector(s); }
  function qa(s) { return Array.prototype.slice.call(root.querySelectorAll(s)); }
  // ---------- tirages : générateur reproductible si l'adresse porte ?seed=…
  var seed = parseInt(new URLSearchParams(location.search).get("seed"), 10);
  var rnd = Math.random;
  if (isFinite(seed)) {
    rnd = function () {   // mulberry32
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function ent(a, b) { return a + Math.floor(rnd() * (b - a + 1)); }
  function pas(a, b, p) { return ent(Math.round(a / p), Math.round(b / p)) * p; }
  function nz(f) { var v; do { v = f(); } while (Math.abs(v) < 1e-9); return v; }
  function arr(x) { return Math.round(x * 1000) / 1000; }
  function fr(x, d) {
    if (Math.abs(x) < 1e-9) x = 0;
    var s = x.toLocaleString("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: d === undefined ? 3 : d });
    return s.replace("-", "−");
  }
  function par(x) { return x < 0 ? "(" + fr(x) + ")" : fr(x); }

  var niv = 1, cur = null, essai = 0, nTirage = 0, interagi = false, reussi = false, stats = { ok: 0, tot: 0, serie: 0, dix: 0, dixTot: 0 };
  
  function tirage() {
    var c = function () { return pas(-0.6, 1.2, 0.1); };
    var A, B;
    do {
      A = [c(), c(), niv === 3 ? pas(-0.6, 0.8, 0.1) : 0];
      B = [c(), c(), niv === 3 ? pas(-0.6, 0.8, 0.1) : 0];
    } while (Math.hypot(A[0] - B[0], A[1] - B[1], A[2] - B[2]) < 0.25);
    var R = [pas(-400, 400, 10), pas(-400, 400, 10), niv === 3 ? pas(-300, 300, 10) : 0];
    if (Math.abs(R[0]) + Math.abs(R[1]) < 50) R[1] = nz(function () { return pas(-400, 400, 10); });
    var MA = [0, 0, 0];
    if (niv === 2) MA[2] = nz(function () { return pas(-150, 150, 5); });
    if (niv === 3) MA = [pas(-150, 150, 5), pas(-150, 150, 5), pas(-150, 150, 5)];
    var BA = [arr(A[0] - B[0]), arr(A[1] - B[1]), arr(A[2] - B[2])];
    var Cx = [arr(BA[1] * R[2] - BA[2] * R[1]), arr(BA[2] * R[0] - BA[0] * R[2]), arr(BA[0] * R[1] - BA[1] * R[0])];
    var MB = [arr(MA[0] + Cx[0]), arr(MA[1] + Cx[1]), arr(MA[2] + Cx[2])];
    return { A: A, B: B, R: R, MA: MA, BA: BA, C: Cx, MB: MB, niv: niv };
  }

  // ---------- affichage
  function coord(P) { return "(" + fr(P[0]) + " ; " + fr(P[1]) + (niv === 3 ? " ; " + fr(P[2]) : "") + ") m"; }
  function torseurHtml(nom, pt, R, M, plan) {
    var rows = plan ? [[fr(R[0]), "—"], [fr(R[1]), "—"], ["—", fr(M[2])]] : [[fr(R[0]), fr(M[0])], [fr(R[1]), fr(M[1])], [fr(R[2]), fr(M[2])]];
    return '<span class="torseur"><span class="tz-n">{<i>T</i><sub>' + nom + "</sub>}<sub>" + pt + '</sub> =</span><span class="tz-b"><table>' +
      rows.map(function (r) { return "<tr><td>" + r[0] + "</td><td>" + r[1] + "</td></tr>"; }).join("") +
      '</table></span><span class="tz-r">(' + pt + ", x, y, z)</span></span>";
  }
  function champ(id, lab) { return '<label class="ta-f" data-k="' + id + '"><span>' + lab + '</span><input type="text" inputmode="decimal" autocomplete="off" aria-label="' + lab.replace(/<\/?sub>/g, "") + '"></label>'; }
  function poser() {
    cur = tirage(); essai = 0;
    var plan = niv < 3;
    q("#ta-txt").innerHTML = "Action mécanique de 1 sur 2, connue au point A" + (plan ? " ; problème plan (x, y)" : " ; problème dans l'espace") +
      ". Écris le vecteur <span class=\"vec\">BA</span>, puis le torseur au point B.";
    q("#ta-donnees").innerHTML = "<div>" + torseurHtml("1→2", "A", cur.R, cur.MA, plan) + "</div>" +
      "<p><b>A</b> " + coord(cur.A) + " &nbsp; <b>B</b> " + coord(cur.B) + "</p><p class=\"small\">Forces en N, moments en N·m.</p>";
    var ba = ["x", "y"].concat(plan ? [] : ["z"]);
    q("#ta-ba").innerHTML = ba.map(function (c, i) { return champ("ba" + i, "BA<sub>" + c + "</sub>"); }).join("");
    if (plan) {
      q("#ta-tb").innerHTML = '<span class="tz-n">{<i>T</i><sub>1→2</sub>}<sub>B</sub> =</span><span class="tz-b"><table>' +
        "<tr><td>" + champ("r0", "X") + '</td><td class="dash">—</td></tr><tr><td>' + champ("r1", "Y") + '</td><td class="dash">—</td></tr>' +
        '<tr><td class="dash">—</td><td>' + champ("m2", "N<sub>B</sub>") + "</td></tr></table></span>";
    } else {
      q("#ta-tb").innerHTML = '<span class="tz-n">{<i>T</i><sub>1→2</sub>}<sub>B</sub> =</span><span class="tz-b"><table>' +
        [0, 1, 2].map(function (i) { return "<tr><td>" + champ("r" + i, ["X", "Y", "Z"][i]) + "</td><td>" + champ("m" + i, ["L", "M", "N"][i] + "<sub>B</sub>") + "</td></tr>"; }).join("") +
        "</table></span>";
    }
    q("#ta-corr").hidden = true; q("#ta-vide").hidden = false; q("#ta-fb").textContent = ""; q("#ta-fb").className = "ta-fb";
    figure();
    q("#ta-n").textContent = ++nTirage;
    // la grille garde sa place : sur un écran étroit, on y revient seulement si elle est sortie de l'écran
    var grid = q(".ta-grid"), top = grid.getBoundingClientRect().top;
    if (interagi && top < 0) grid.scrollIntoView({ block: "start", behavior: "smooth" });
    var first = q(".ta-f input");
    if (first && (interagi || matchMedia("(min-width: 701px)").matches)) first.focus({ preventScroll: true });
  }
  function figure() {
    var svg = q("#ta-svg");
    q("#ta-3d").hidden = niv !== 3;
    if (niv === 3) { svg.style.display = "none"; return; }
    svg.style.display = "";
    var A = cur.A, B = cur.B, R = cur.R, nR = Math.hypot(R[0], R[1]);
    var L = 55 + 55 * Math.min(1, nR / 560);                     // longueur de R à l'écran (px), croissante avec |R|
    function cadre(extra) {
      var xs = [0, A[0], B[0]].concat(extra ? [extra[0]] : []), ys = [0, A[1], B[1]].concat(extra ? [extra[1]] : []);
      var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
      var s = Math.min(280 / Math.max(x1 - x0, 0.2), 220 / Math.max(y1 - y0, 0.2));
      return { s: s, ox: 180 - (x0 + x1) / 2 * s, oy: 150 + (y0 + y1) / 2 * s, x0: x0, x1: x1, y0: y0, y1: y1 };
    }
    var f = cadre(), Tip = [A[0] + R[0] / nR * L / f.s, A[1] + R[1] / nR * L / f.s];
    f = cadre(Tip);
    function X(x) { return f.ox + x * f.s; } function Y(y) { return f.oy - y * f.s; }
    var h = '<defs><marker id="ta-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>';
    var ax0 = X(f.x0) - 25, ax1 = X(f.x1) + 25, ay0 = Y(f.y0) + 25, ay1 = Y(f.y1) - 25;
    h += '<line class="ax" x1="' + ax0 + '" y1="' + Y(0) + '" x2="' + ax1 + '" y2="' + Y(0) + '" marker-end="url(#ta-ah)"/>';
    h += '<line class="ax" x1="' + X(0) + '" y1="' + ay0 + '" x2="' + X(0) + '" y2="' + ay1 + '" marker-end="url(#ta-ah)"/>';
    h += '<text x="' + (ax1 - 8) + '" y="' + (Y(0) + 16) + '" fill="#46525C">x</text><text x="' + (X(0) + 7) + '" y="' + (ay1 + 8) + '" fill="#46525C">y</text>';
    h += '<line x1="' + X(B[0]) + '" y1="' + Y(B[1]) + '" x2="' + X(A[0]) + '" y2="' + Y(A[1]) + '" stroke="#7B3FA0" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#ta-ah)"/>';
    h += '<line x1="' + X(A[0]) + '" y1="' + Y(A[1]) + '" x2="' + X(Tip[0]) + '" y2="' + Y(Tip[1]) + '" stroke="#C62828" stroke-width="3.5" marker-end="url(#ta-ah)"/>';
    // étiquettes : dans la direction la plus libre (loin des traits qui partent du point), sans sortir du cadre
    function ang(p, q) { return Math.atan2(Y(q[1]) - Y(p[1]), X(q[0]) - X(p[0])); }
    function libre(pris) {
      var best = 0, dmax = -1;
      for (var k = 0; k < 24; k++) {
        var a = k * Math.PI / 12, d = Math.PI;
        pris.forEach(function (b) { var e = Math.abs(((a - b) % (2 * Math.PI) + 3 * Math.PI) % (2 * Math.PI) - Math.PI); d = Math.min(d, e); });
        if (d > dmax + 1e-9) { dmax = d; best = a; }
      }
      return best;
    }
    function texte(px, py, a, d, txt, coul) {
      var x = Math.max(12, Math.min(348, px + d * Math.cos(a))), y = Math.max(16, Math.min(294, py + d * Math.sin(a) + 5));
      return '<text x="' + x + '" y="' + y + '" text-anchor="middle" fill="' + coul + '">' + txt + "</text>";
    }
    var cx = X(A[0]), cy = Y(A[1]), aR = ang(A, Tip), aAB = ang(A, B), aA = libre([aR, aAB]);
    if (cur.MA[2]) {
      // arc de 240° dont l'ouverture est centrée sur R ; sens trigonométrique = angle décroissant à l'écran (y vers le bas)
      var r = 20, pos = cur.MA[2] > 0, a0 = aR + (pos ? -1.05 : 1.05), a1 = a0 + (pos ? -4.18 : 4.18);
      h += '<path d="M' + (cx + r * Math.cos(a0)) + " " + (cy + r * Math.sin(a0)) + " A" + r + " " + r + " 0 1 " + (pos ? 0 : 1) + " " +
        (cx + r * Math.cos(a1)) + " " + (cy + r * Math.sin(a1)) + '" fill="none" stroke="#1B7A43" stroke-width="2.5" marker-end="url(#ta-ah)"/>';
      var aN = libre([aR, aAB, aA]);
      h += texte(cx, cy, aN, 40, "N<tspan baseline-shift=\"sub\" font-size=\"10\">A</tspan>", "#1B7A43");
    }
    h += '<circle cx="' + cx + '" cy="' + cy + '" r="4.5" fill="#1C2530"/>' + texte(cx, cy, aA, cur.MA[2] ? 34 : 16, "A", "#1C2530");
    h += '<circle cx="' + X(B[0]) + '" cy="' + Y(B[1]) + '" r="4.5" fill="#1C2530"/>' + texte(X(B[0]), Y(B[1]), ang(B, A) + Math.PI, 16, "B", "#1C2530");
    h += texte(X(Tip[0]), Y(Tip[1]), aR, 14, "R", "#C62828");
    svg.innerHTML = h;
  }

  // ---------- correction
  function lire(inp) {
    var s = String(inp.value).replace(/[\s  ]/g, "").replace(/[−–]/g, "-").replace(",", ".");
    if (!/^[+-]?(\d+\.?\d*|\.\d+)$/.test(s)) return null;
    return parseFloat(s);
  }
  function attendu(k) {
    var i = +k.slice(-1);
    if (k.indexOf("ba") === 0) return cur.BA[i];
    if (k[0] === "r") return cur.R[i];
    return cur.MB[i];
  }
  function verifier() {
    var bons = 0, tous = qa(".ta-f");
    tous.forEach(function (f) {
      var k = f.getAttribute("data-k"), v = lire(f.querySelector("input")), a = attendu(k);
      var tol = k.indexOf("ba") === 0 ? 0.01 : Math.max(0.1, Math.abs(a) * 0.005);
      var ok = v !== null && Math.abs(v - a) <= tol + 1e-9;
      f.classList.toggle("ok", ok); f.classList.toggle("ko", !ok); if (ok) bons++;
    });
    essai++;
    var fb = q("#ta-fb"), juste = bons === tous.length;
    fb.className = "ta-fb " + (juste ? "ok" : "ko");
    fb.textContent = juste ? "✔ Tout est juste ! Entrée : tirage suivant." : "✘ " + (tous.length - bons) + " case" + (tous.length - bons > 1 ? "s" : "") +
      " à revoir (en rouge) : corrige et vérifie à nouveau.";
    reussi = juste;
    if (!juste) { var ko = q(".ta-f.ko input"); if (ko) ko.focus({ preventScroll: true }); }
    if (essai === 1) compter(juste);
    if (juste) corriger();
  }
  function compter(juste) {
    stats.tot++; if (juste) { stats.ok++; stats.serie++; } else stats.serie = 0;
    if (stats.dixTot < 10) { stats.dixTot++; if (juste) stats.dix++; }
    q("#ta-ok").textContent = stats.ok; q("#ta-tot").textContent = stats.tot; q("#ta-serie").textContent = stats.serie;
    q("#ta-dix").textContent = stats.dix + " / " + stats.dixTot + (stats.dixTot < 10 ? " (sur 10)" : "");
    if (stats.dixTot === 10 && !q("#ta-fin").dataset.done) {
      q("#ta-fin").dataset.done = "1"; q("#ta-fin").hidden = false;
      var n = stats.dix * 2, et = n >= 18 ? "★★★" : n >= 14 ? "★★☆" : n >= 10 ? "★☆☆" : "☆☆☆";
      q("#ta-fin").textContent = "Série de 10 terminée : " + n + " / 20 " + et + " — tu peux continuer à t'entraîner.";
    }
  }
  function corriger() {
    var c = cur, plan = c.niv < 3, a = c.BA, R = c.R;
    var h = "<p><b>1. Vecteur BA</b> = A − B = (" + fr(c.A[0]) + " − " + par(c.B[0]) + " ; " + fr(c.A[1]) + " − " + par(c.B[1]) +
      (plan ? "" : " ; " + fr(c.A[2]) + " − " + par(c.B[2])) + ") = <b>(" + fr(a[0]) + " ; " + fr(a[1]) + (plan ? "" : " ; " + fr(a[2])) + ") m</b></p>";
    h += "<p><b>2. Résultante</b> : elle ne change pas d'un point à l'autre : " + "(" + fr(R[0]) + " ; " + fr(R[1]) + (plan ? "" : " ; " + fr(R[2])) + ") N.</p>";
    if (plan) {
      h += '<p><b>3. Moment en B</b> : <i>N</i><sub>B</sub> = <i>N</i><sub>A</sub> + <i>a</i>·<i>Y</i> − <i>b</i>·<i>X</i></p><div class="eq"><i>N</i><sub>B</sub> = ' +
        fr(c.MA[2]) + " + " + par(a[0]) + " × " + par(R[1]) + " − " + par(a[1]) + " × " + par(R[0]) + " = " + fr(c.MA[2]) + " + " + par(c.C[2]) +
        " = <b>" + fr(c.MB[2]) + " N·m</b></div>";
    } else {
      h += "<p><b>3. Produit vectoriel</b> <span class=\"vec\">BA</span> ∧ <span class=\"vec\">R</span> = (b·Z − c·Y ; c·X − a·Z ; a·Y − b·X) :</p>" +
        '<div class="eq">L : ' + par(a[1]) + " × " + par(R[2]) + " − " + par(a[2]) + " × " + par(R[1]) + " = " + fr(c.C[0]) +
        "<br>M : " + par(a[2]) + " × " + par(R[0]) + " − " + par(a[0]) + " × " + par(R[2]) + " = " + fr(c.C[1]) +
        "<br>N : " + par(a[0]) + " × " + par(R[1]) + " − " + par(a[1]) + " × " + par(R[0]) + " = " + fr(c.C[2]) + "</div>" +
        "<p><b>4. Moment en B</b> = M<sub>A</sub> + BA ∧ R = (" + fr(c.MA[0]) + " + " + par(c.C[0]) + " ; " + fr(c.MA[1]) + " + " + par(c.C[1]) +
        " ; " + fr(c.MA[2]) + " + " + par(c.C[2]) + ") = <b>(" + fr(c.MB[0]) + " ; " + fr(c.MB[1]) + " ; " + fr(c.MB[2]) + ") N·m</b></p>";
    }
    h += "<div>" + torseurHtml("1→2", "B", R, c.MB, plan) + "</div>";
    if (plan && c.niv === 1) h += '<p class="small">En A, le moment est nul : la droite d\'action de R passe par A. En B, il ne l\'est plus '
      + "(sauf si B est sur cette droite) : c'est le « bras de levier » qui apparaît.</p>";
    q("#ta-corr").innerHTML = h; q("#ta-corr").hidden = false; q("#ta-vide").hidden = true;
    // valeur attendue sous chaque case fausse ou vide
    qa(".ta-f").forEach(function (f) {
      if (f.classList.contains("ok")) return;
      if (!f.classList.contains("ko")) f.classList.add("ko");
      var att = f.querySelector(".ta-att") || f.appendChild(document.createElement("span"));
      att.className = "ta-att"; att.textContent = "→ " + fr(attendu(f.getAttribute("data-k")));
    });
    // écran étroit : la correction est sous la réponse ; on la montre en descendant, jamais en remontant
    var col = q("#ta-col-cor"), r = col.getBoundingClientRect();
    if (interagi && r.top > innerHeight - 80) col.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  q("#ta-check").addEventListener("click", verifier);
  q("#ta-sol").addEventListener("click", function () { if (essai === 0) { essai = 1; compter(false); } corriger(); });
  q("#ta-new").addEventListener("click", function () { reussi = false; poser(); });   // un tirage passé sans réponse n'est pas compté
  root.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" || !e.target.closest(".ta-f")) return;
    e.preventDefault();
    if (reussi) { reussi = false; poser(); } else verifier();
  });
  root.addEventListener("pointerdown", function () { interagi = true; });
  root.addEventListener("keydown", function () { interagi = true; }, true);
  document.addEventListener("click", function (e) {      // fermer le rappel en cliquant ailleurs
    var d = q(".ta-aide"); if (d.open && !d.contains(e.target)) d.open = false;
  });
  qa("[data-niv]").forEach(function (b) {
    b.addEventListener("click", function () {
      niv = +b.getAttribute("data-niv");
      qa("[data-niv]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      poser();
    });
  });
  window.__ta__ = { courant: function () { return cur; }, niveau: function () { return niv; } };
  poser();
})();
</script>"""
