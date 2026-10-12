#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exercice 2.1 (Niveau 2) — Déplacer un torseur : entraînement à valeurs aléatoires, page autonome.

Chaque question donne un torseur connu au point A et les coordonnées de A et de B ; l'élève écrit le vecteur BA (en
colonne, entre parenthèses) puis le torseur au point B (relation de Varignon : la résultante ne change pas,
M_B = M_A + BA ∧ R). Séries de 5, 10, 15 ou 20 questions tirées au hasard parmi les types choisis : glisseur dans le
plan, torseur quelconque dans le plan, torseur dans l'espace. Correction pas à pas, note sur 20 en fin de série.
Mise en page plein écran (3 colonnes sur ordinateur, 2 sur tablette, 1 sur téléphone). L'adresse ?seed=… rend les
tirages reproductibles (tests). Appelé par src/generer.py.
"""
from cours3 import COURS3_CSS, _vec
from niveau3 import HOUSE


def render_torseur_alea(style, hub_css):
    rappel = ('<p>La <b>résultante</b> ' + _vec("R") + ' ne change pas d\'un point à l\'autre ; le <b>moment</b> se '
              "transporte par la relation de Varignon (« BABAR ») :</p>"
              '<div class="formule"><span class="f-main">' + _vec("M") + "<sub>B</sub> = " + _vec("M") + "<sub>A</sub> + " +
              _vec("BA") + " ∧ " + _vec("R") + '</span><span class="f-units">' + _vec("BA") +
              " = A − B (coordonnées de A moins celles de B)</span></div>"
              "<p>Avec " + _vec("BA") + " (<i>a</i> ; <i>b</i> ; <i>c</i>) et " + _vec("R") + " (<i>X</i> ; <i>Y</i> ; <i>Z</i>) :</p>"
              '<div class="formule"><span class="f-main">' + _vec("BA") + " ∧ " + _vec("R") + " = ( <i>b</i>·<i>Z</i> − "
              "<i>c</i>·<i>Y</i> ; <i>c</i>·<i>X</i> − <i>a</i>·<i>Z</i> ; <i>a</i>·<i>Y</i> − <i>b</i>·<i>X</i> )</span>"
              '<span class="f-units">dans le plan (x, y), seule la 3<sup>e</sup> composante reste :<br><i>N</i><sub>B</sub> = '
              "<i>N</i><sub>A</sub> + <i>a</i>·<i>Y</i> − <i>b</i>·<i>X</i></span></div>")
    types = "".join(f'<label class="ta-chip"><input type="checkbox" name="ta-type" value="{v}" checked><span>{t}</span></label>'
                    for v, t in (("1", "Glisseur plan"), ("2", "Torseur plan"), ("3", "Torseur 3D")))
    nombres = "".join(f'<label class="ta-chip"><input type="radio" name="ta-n" value="{n}"{" checked" if n == 10 else ""}>'
                      f"<span>{n}</span></label>" for n in (5, 10, 15, 20))
    body = f"""<div class="ta-app" id="ta">
<header class="ta-top">
  <div class="ta-id"><a class="ta-home no-print" href="index.html" title="Retour à l'accueil" aria-label="Retour à l'accueil">{HOUSE}</a>
    <span class="mc-tag">Exercice 2.1</span><span class="pastille n2">Niveau 2</span>
    <h1 id="home-title">Déplacer un torseur</h1></div>
  <div class="ta-prog" aria-live="polite"><span class="ta-qn">Question <b id="ta-k">1</b> / <b id="ta-N">10</b></span>
    <span class="ta-dots" id="ta-dots" aria-hidden="true"></span><span class="ta-okn">Réussies <b id="ta-ok">0</b></span></div>
  <div class="ta-menus">
    <details class="ta-pd ta-cfg" id="ta-cfg"><summary>Série : <span id="ta-cfg-sum">10 questions</span></summary><div class="ta-pop">
      <p class="ta-pop-t">Types de questions <span class="small">(tirés au hasard parmi ceux cochés)</span></p><div class="ta-chips">{types}</div>
      <p class="ta-pop-t">Nombre de questions</p><div class="ta-chips">{nombres}</div>
      <p class="ta-cfg-msg small" id="ta-cfg-msg"></p>
      <button type="button" class="btn" id="ta-go">Lancer la série</button></div></details>
    <details class="ta-pd ta-aide"><summary>Rappel</summary><div class="ta-pop">{rappel}</div></details>
  </div>
</header>
<main class="ta-grid" id="ta-grid">
  <section class="ta-col ta-col-don" aria-labelledby="ta-h-don"><h2 id="ta-h-don"><span>1</span> Données <em class="ta-type" id="ta-type"></em></h2>
    <p id="ta-txt"></p><div class="ta-donnees" id="ta-donnees"></div>
    <svg class="ta-svg" id="ta-svg" viewBox="0 0 360 300" role="img" aria-label="Points A et B, résultante en A"></svg>
    <p class="ta-3d small" id="ta-3d" hidden>Vue en perspective : l'axe z vient vers toi ; les pointillés gris ramènent A et B dans le plan (x, z) pour lire leur profondeur.</p></section>
  <section class="ta-col ta-col-rep" aria-labelledby="ta-h-rep"><h2 id="ta-h-rep"><span>2</span> Ta réponse</h2>
    <p class="ta-conseil"><b>Conseil :</b> utilise un brouillon. Calcule d'abord <span class="vec">BA</span> = A − B, puis
    <span class="vec">BA</span> ∧ <span class="vec">R</span>, et seulement ensuite remplis les cases.</p>
    <div class="ta-saisie"><div class="ta-bloc"><h3>Le vecteur <span class="vec">BA</span> (en m)</h3><div class="ta-vecin" id="ta-ba"></div></div>
    <div class="ta-bloc"><h3>Le torseur au point B (N et N·m)</h3><div class="ta-tor" id="ta-tb"></div></div></div>
    <div class="ta-act"><button type="button" class="btn" id="ta-check" title="Touche Entrée">Vérifier</button>
      <button type="button" class="btn ghost" id="ta-sol" title="La question compte alors comme manquée">Correction</button>
      <button type="button" class="btn ta-next" id="ta-next" disabled>Question suivante ▶</button></div>
    <p class="ta-fb" id="ta-fb" aria-live="polite"></p></section>
  <section class="ta-col ta-col-cor" id="ta-col-cor" aria-labelledby="ta-h-cor"><h2 id="ta-h-cor"><span>3</span> Correction</h2>
    <p class="ta-vide small" id="ta-vide">La correction pas à pas s'affiche ici dès que ta réponse est juste, ou avec
    le bouton « Correction » (la question compte alors comme manquée).</p>
    <div class="ta-corr" id="ta-corr" hidden></div></section>
</main>
<section class="ta-bilan" id="ta-bilan" hidden aria-live="polite"></section>
<footer class="ta-foot small"><p>Saisie : nombres décimaux avec une virgule ou un point, signe compris ; <kbd>Tab</kbd> passe
à la case suivante, <kbd>Entrée</kbd> vérifie, puis passe à la question suivante. Tolérance : ± 0,01 m sur BA, ± 0,5 %
(au moins 0,1) sur le torseur. Une question n'est réussie que si tout est juste à la première vérification ; la note
sur 20 est donnée en fin de série.</p>
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
<meta name="description" content="Entraînement à valeurs aléatoires (niveau 2) : séries de 5 à 20 questions pour transporter un torseur d'un point A à un point B, dans le plan et dans l'espace, avec correction pas à pas et note sur 20.">
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
/* ---------- plein écran : barre d'en-tête, puis données | réponse | correction ; la taille du texte suit l'écran ---------- */
.ta-page #home{padding:8px clamp(6px, 1vw, 16px) 12px}
.ta-app{display:flex; flex-direction:column; min-height:calc(100dvh - 20px); font-size:clamp(14.5px, .3vw + .85vh + 5px, 23px)}
.ta-top{display:flex; flex-wrap:wrap; align-items:center; gap:6px 16px; background:var(--encre); color:#fff; padding:7px 12px; position:relative}
.ta-id{display:flex; align-items:center; gap:8px; flex-wrap:wrap}
#ta .ta-id h1{margin:0; font:800 1.2em/1.2 var(--f-titre); color:#fff}
.ta-home{display:inline-flex; color:var(--jaune)} .ta-home svg{width:22px; height:22px}
.ta-prog{display:flex; align-items:center; flex-wrap:wrap; gap:4px 12px; font-size:.88em}
.ta-prog b{color:var(--jaune); font-family:var(--f-titre)}
.ta-dots{display:flex; flex-wrap:wrap; gap:3px; max-width:min(46vw, 420px)}
.ta-dots i{width:.8em; height:.8em; border-radius:50%; background:rgba(255,255,255,.22); display:inline-block}
.ta-dots i.ok{background:#3FBF6F} .ta-dots i.ko{background:#E5534B} .ta-dots i.on{outline:2px solid var(--jaune); outline-offset:1px}
.ta-menus{display:flex; gap:6px; margin-left:auto}
.ta-pd summary{cursor:pointer; list-style:none; border:1.5px solid #fff; padding:4px 10px; font:700 .86em var(--f-titre); white-space:nowrap}
.ta-pd summary::-webkit-details-marker{display:none}
.ta-pd[open] summary{background:#fff; color:var(--encre)}
.ta-cfg summary{border-color:var(--jaune)}
.ta-pop{position:absolute; right:12px; top:100%; z-index:20; width:min(560px, calc(100vw - 24px)); background:var(--papier); color:var(--encre);
  border:2px solid var(--encre); box-shadow:0 8px 24px rgba(0,0,0,.25); padding:8px 14px 12px; font-size:.92em}
.ta-pop .formule{margin:6px 0}
.ta-pop-t{font:700 .95em var(--f-titre); margin:6px 0 4px}
.ta-chips{display:flex; flex-wrap:wrap; gap:6px}
.ta-chip input{position:absolute; opacity:0; pointer-events:none}
.ta-chip span{display:inline-block; border:1.5px solid var(--encre); padding:5px 12px; font:700 .9em var(--f-titre); cursor:pointer; background:#fff}
.ta-chip input:checked+span{background:var(--encre); color:var(--jaune)}
.ta-chip input:focus-visible+span{outline:2px solid var(--bleu); outline-offset:2px}
.ta-cfg-msg{color:var(--rouge); min-height:1.2em; margin:6px 0}
.ta-grid{flex:1; display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.05fr) minmax(0,1fr); gap:clamp(6px, .8vw, 14px); margin-top:8px; align-items:stretch}
@media (max-width:1100px){ .ta-grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr); grid-template-areas:"don rep" "cor rep"; align-items:start}
  .ta-col-don{grid-area:don} .ta-col-rep{grid-area:rep} .ta-col-cor{grid-area:cor} }
@media (max-width:700px){ .ta-grid{grid-template-columns:1fr; grid-template-areas:"don" "rep" "cor"} .ta-menus{margin-left:0} .ta-app{min-height:0} }
.ta-col{background:#fff; border:1px solid var(--trait-fin); padding:.5em .8em .7em; min-width:0}
.ta-col h2{display:flex; align-items:center; flex-wrap:wrap; gap:8px; font:800 1.05em var(--f-titre); margin:0 0 .4em}
.ta-col h2 span{display:inline-grid; place-items:center; width:1.4em; height:1.4em; background:var(--encre); color:var(--jaune); font-size:.85em}
.ta-type{font:700 .78em var(--f-titre); color:var(--bleu); border:1.5px solid var(--bleu); padding:1px 8px; margin-left:auto}
.ta-col h3{font:700 .92em var(--f-titre); margin:.5em 0 .3em}
.ta-col p{margin:0 0 .4em}
#ta-txt{font-size:.95em}
#ta .vec{line-height:1} #ta .vec::before{top:-.04em} #ta .vec::after{top:-.24em}
.ta-donnees{border-left:4px solid var(--bleu); padding:2px 10px; margin:0 0 .5em}
.ta-donnees p{margin:2px 0}
.ta-svg{display:block; width:100%; height:auto; max-height:52vh; background:#fff; border:1px solid var(--trait-fin)}
.ta-svg .ax{stroke:#9AA2A8; stroke-width:1}
.ta-svg text{font:700 13px var(--f-texte)}
.ta-conseil{background:var(--jaune-pale); border-left:4px solid var(--jaune); padding:.35em .7em; font-size:.88em}
.ta-saisie{display:flex; flex-wrap:wrap; gap:.4em 1.6em; align-items:flex-start}
/* vecteur en colonne, entre parenthèses */
.vcol{display:inline-flex; align-items:center; gap:.3em; vertical-align:middle}
.vcol-b{display:inline-block; border-left:2px solid currentColor; border-right:2px solid currentColor; border-radius:1.1em / 50%; padding:.15em .55em}
.vcol-b table{border-collapse:collapse} .vcol-b td{padding:.05em .2em; text-align:center}
.vcol-b td.vl{font:600 .75em var(--f-texte); color:var(--encre-2); padding-right:.4em; text-align:right}
.ta-vecin .vcol-b{padding:.25em .6em}
.ta-f{position:relative; display:inline-flex; flex-direction:column; align-items:center; gap:2px; line-height:1.25; font-size:.8em;
  color:var(--encre-2); padding-bottom:1.15em}
.ta-f input{width:6.4em; border:1.5px dashed var(--encre-2); padding:.25em .3em; background:#fff; font:600 1.15em var(--f-texte); text-align:center}
.ta-vecin .ta-f{padding-bottom:1.05em}
.ta-f input:focus{outline:2px solid var(--jaune); outline-offset:1px; border-style:solid}
.ta-f.ok input{border:2px solid var(--vert); background:var(--vert-pale)}
.ta-f.ko input{border:2px solid var(--rouge); background:var(--rouge-pale)}
.ta-att{position:absolute; bottom:0; left:0; right:0; text-align:center; font:700 .9em var(--f-texte); color:var(--vert); white-space:nowrap}
.ta-tor{display:inline-flex; align-items:center; gap:6px; flex-wrap:wrap; max-width:100%}
.ta-tor .tz-b td{padding:0 .25em; text-align:center; min-width:0}
.ta-tor .dash{color:var(--encre-2); padding:0 1.6em}
.ta-act{display:flex; flex-wrap:wrap; gap:6px; margin-top:.3em}
.ta-act .btn{padding:.4em .8em; font-size:.92em}
.ta-next:not(:disabled){background:var(--vert); border-color:var(--vert)}
kbd{font:600 .72rem var(--f-texte); border:1px solid currentColor; border-radius:3px; padding:0 4px; margin-left:4px; opacity:.8}
.ta-fb{min-height:1.5em; margin:.4em 0 0; font-weight:700}
.ta-fb.ok{color:var(--vert)} .ta-fb.ko{color:var(--rouge)}
.ta-corr{border-left:4px solid var(--vert); padding:0 10px; font-size:.92em}
.ta-corr p{margin:3px 0}
.ta-corr .eq{line-height:1.8; margin:2px 0 4px}
.ta-vide{color:var(--encre-2)}
.ta-grid[hidden],.ta-bilan[hidden]{display:none}
.ta-bilan{flex:1; background:#fff; border:1px solid var(--trait-fin); margin-top:8px; padding:1em 1.4em}
.ta-bilan h2{font:800 1.4em var(--f-titre); margin:0 0 .3em}
.ta-note{font:800 2.6em var(--f-titre); color:var(--bleu); margin:.1em 0}
.ta-note small{font-size:.45em; color:var(--encre-2)} .ta-et{font-size:.55em; color:var(--jaune)}
.ta-bil-l{display:grid; grid-template-columns:repeat(auto-fill, minmax(12em, 1fr)); gap:4px 14px; padding:0; list-style:none; margin:.6em 0 1em}
.ta-bil-l li{border-left:4px solid var(--trait-fin); padding:2px 8px}
.ta-bil-l li.ok{border-color:var(--vert)} .ta-bil-l li.ko{border-color:var(--rouge)}
.ta-bilan .ta-act .btn{font-size:1em}
.ta-foot{margin-top:10px; color:var(--encre-2)}
.ta-foot p{margin:4px 0}
@media (max-width:700px){ #ta .ta-id h1{font-size:1.05em} .ta-dots{max-width:100%} .ta-f input{width:5.6em} }
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

  var NOM_TYPE = { 1: "Glisseur plan", 2: "Torseur plan", 3: "Torseur 3D" };
  var niv = 1, cur = null, essai = 0, interagi = false, reussi = false;
  var serie = { types: [1, 2, 3], N: 10, liste: [], k: 0, res: [] };   // res[i] : true (réussie), false (manquée), undefined

  function melange(t) { for (var i = t.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), x = t[i]; t[i] = t[j]; t[j] = x; } return t; }
  function lancer(types, N) {
    serie = { types: types.slice(), N: N, liste: [], k: 0, res: [] };
    for (var i = 0; i < N; i++) serie.liste.push(types[i % types.length]);   // répartition équilibrée, puis ordre au hasard
    melange(serie.liste);
    q("#ta-N").textContent = N;
    q("#ta-cfg-sum").textContent = N + " questions · " + types.map(function (t) { return ["glisseur", "plan", "3D"][t - 1]; }).join(", ");
    q("#ta-bilan").hidden = true; q("#ta-grid").hidden = false;
    poser();
  }

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
  function col(vals, labels) {     // vecteur en colonne, entre parenthèses
    return '<span class="vcol"><span class="vcol-b"><table>' + vals.map(function (v, i) {
      return "<tr>" + (labels ? '<td class="vl">' + labels[i] + "</td>" : "") + "<td>" + v + "</td></tr>"; }).join("") + "</table></span></span>";
  }
  function torseurHtml(nom, pt, R, M, plan) {
    var rows = plan ? [[fr(R[0]), "—"], [fr(R[1]), "—"], ["—", fr(M[2])]] : [[fr(R[0]), fr(M[0])], [fr(R[1]), fr(M[1])], [fr(R[2]), fr(M[2])]];
    return '<span class="torseur"><span class="tz-n">{<i>T</i><sub>' + nom + "</sub>}<sub>" + pt + '</sub> =</span><span class="tz-b"><table>' +
      rows.map(function (r) { return "<tr><td>" + r[0] + "</td><td>" + r[1] + "</td></tr>"; }).join("") +
      '</table></span><span class="tz-r">(' + pt + ", x, y, z)</span></span>";
  }
  function champ(id, lab) { return '<label class="ta-f" data-k="' + id + '">' + (lab ? "<span>" + lab + "</span>" : "") + '<input type="text" inputmode="decimal" autocomplete="off" aria-label="' + lab.replace(/<\/?sub>/g, "") + '"></label>'; }
  function points() {
    q("#ta-dots").innerHTML = serie.liste.map(function (t, i) {
      var r = serie.res[i]; return '<i class="' + (r === true ? "ok" : r === false ? "ko" : "") + (i === serie.k ? " on" : "") + '" title="Question ' + (i + 1) + " : " + NOM_TYPE[t] + '"></i>';
    }).join("");
    q("#ta-ok").textContent = serie.res.filter(function (r) { return r === true; }).length;
  }
  function poser() {
    niv = serie.liste[serie.k];
    cur = tirage(); essai = 0; reussi = false;
    var plan = niv < 3;
    q("#ta-type").textContent = NOM_TYPE[niv];
    q("#ta-next").disabled = true;
    q("#ta-next").textContent = serie.k === serie.N - 1 ? "Voir ma note ▶" : "Question suivante ▶";
    q("#ta-txt").innerHTML = "Action mécanique de 1 sur 2, connue au point A" + (plan ? " ; problème plan (x, y)" : " ; problème dans l'espace") +
      ". Écris le vecteur <span class=\"vec\">BA</span>, puis le torseur au point B.";
    q("#ta-donnees").innerHTML = "<div>" + torseurHtml("1→2", "A", cur.R, cur.MA, plan) + "</div>" +
      "<p><b>A</b> " + coord(cur.A) + " &nbsp; <b>B</b> " + coord(cur.B) + "</p><p class=\"small\">Forces en N, moments en N·m.</p>";
    var ba = ["x", "y"].concat(plan ? [] : ["z"]);
    q("#ta-ba").innerHTML = '<span class="vec">BA</span> = ' + col(ba.map(function (c, i) { return champ("ba" + i, ""); }), ba);
    qa("#ta-ba input").forEach(function (inp, i) { inp.setAttribute("aria-label", "BA, composante " + ba[i]); });
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
    q("#ta-k").textContent = serie.k + 1;
    points();
    // la grille garde sa place : sur un écran étroit, on y revient seulement si elle est sortie de l'écran
    var grid = q(".ta-grid"), top = grid.getBoundingClientRect().top;
    if (interagi && top < 0) grid.scrollIntoView({ block: "start", behavior: "smooth" });
    var first = q(".ta-f input");
    if (first && (interagi || matchMedia("(min-width: 701px)").matches)) first.focus({ preventScroll: true });
  }
  function figure() {
    var svg = q("#ta-svg"), d3 = niv === 3;
    q("#ta-3d").hidden = !d3;
    // projection : plan (x, y) tel quel ; en 3D, perspective cavalière (z vers l'avant, à 45°, réduit de moitié)
    var kz = 0.5 * Math.SQRT1_2;
    function pr(P) { return d3 ? [P[0] - kz * P[2], P[1] - kz * P[2]] : [P[0], P[1]]; }
    var A = pr(cur.A), B = pr(cur.B), O = [0, 0], R2 = pr(cur.R), nR = Math.hypot(R2[0], R2[1]) || 1;
    var nR3 = Math.hypot(cur.R[0], cur.R[1], cur.R[2]);
    var L = 55 + 55 * Math.min(1, nR3 / 560);                    // longueur de R à l'écran (px), croissante avec |R|
    var pieds = d3 ? [pr([cur.A[0], 0, cur.A[2]]), pr([cur.B[0], 0, cur.B[2]])] : [];
    function cadre(extra) {
      var pts = [O, A, B].concat(pieds).concat(extra ? [extra] : []);
      var xs = pts.map(function (p) { return p[0]; }), ys = pts.map(function (p) { return p[1]; });
      var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs), y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
      var s = Math.min(280 / Math.max(x1 - x0, 0.2), 220 / Math.max(y1 - y0, 0.2));
      return { s: s, ox: 180 - (x0 + x1) / 2 * s, oy: 150 + (y0 + y1) / 2 * s, x0: x0, x1: x1, y0: y0, y1: y1 };
    }
    var f = cadre(), Tip = [A[0] + R2[0] / nR * L / f.s, A[1] + R2[1] / nR * L / f.s];
    f = cadre(Tip);
    function X(x) { return f.ox + x * f.s; } function Y(y) { return f.oy - y * f.s; }
    var h = '<defs><marker id="ta-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>';
    var ax0 = X(f.x0) - 25, ax1 = X(f.x1) + 25, ay0 = Y(f.y0) + 25, ay1 = Y(f.y1) - 25;
    h += '<line class="ax" x1="' + ax0 + '" y1="' + Y(0) + '" x2="' + ax1 + '" y2="' + Y(0) + '" marker-end="url(#ta-ah)"/>';
    h += '<line class="ax" x1="' + X(0) + '" y1="' + ay0 + '" x2="' + X(0) + '" y2="' + ay1 + '" marker-end="url(#ta-ah)"/>';
    h += '<text x="' + (ax1 - 8) + '" y="' + (Y(0) + 16) + '" fill="#46525C">x</text><text x="' + (X(0) + 7) + '" y="' + (ay1 + 8) + '" fill="#46525C">y</text>';
    if (d3) {   // axe z vers l'avant (en bas à gauche), et rappels des points dans le plan (x, z)
      var zl = Math.max(60, Math.min(X(0) - 12, 300 - Y(0)) * 0.95), zx = X(0) - zl * Math.SQRT1_2, zy = Y(0) + zl * Math.SQRT1_2;
      h += '<line class="ax" x1="' + (X(0) + 25) + '" y1="' + (Y(0) - 25) + '" x2="' + zx + '" y2="' + zy + '" marker-end="url(#ta-ah)"/>';
      h += '<text x="' + (zx - 4) + '" y="' + (zy - 6) + '" fill="#46525C" text-anchor="end">z</text>';
      [[cur.A, A], [cur.B, B]].forEach(function (c) {
        var pz = pr([c[0][0], 0, c[0][2]]), px = pr([c[0][0], 0, 0]);
        h += '<polyline points="' + X(c[1][0]) + "," + Y(c[1][1]) + " " + X(pz[0]) + "," + Y(pz[1]) + " " + X(px[0]) + "," + Y(px[1]) +
          '" fill="none" stroke="#9AA2A8" stroke-dasharray="3 3"/>';
      });
    }
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
    var cx = X(A[0]), cy = Y(A[1]), aR = ang(A, Tip), aAB = ang(A, B), aA = libre([aR, aAB].concat(d3 ? [Math.PI / 2] : []));
    if (!d3 && cur.MA[2]) {
      // arc de 240° dont l'ouverture est centrée sur R ; sens trigonométrique = angle décroissant à l'écran (y vers le bas)
      var r = 20, pos = cur.MA[2] > 0, a0 = aR + (pos ? -1.05 : 1.05), a1 = a0 + (pos ? -4.18 : 4.18);
      h += '<path d="M' + (cx + r * Math.cos(a0)) + " " + (cy + r * Math.sin(a0)) + " A" + r + " " + r + " 0 1 " + (pos ? 0 : 1) + " " +
        (cx + r * Math.cos(a1)) + " " + (cy + r * Math.sin(a1)) + '" fill="none" stroke="#1B7A43" stroke-width="2.5" marker-end="url(#ta-ah)"/>';
      var aN = libre([aR, aAB, aA]);
      h += texte(cx, cy, aN, 40, "N<tspan baseline-shift=\"sub\" font-size=\"10\">A</tspan>", "#1B7A43");
    }
    h += '<circle cx="' + cx + '" cy="' + cy + '" r="4.5" fill="#1C2530"/>' + texte(cx, cy, aA, !d3 && cur.MA[2] ? 34 : 16, "A", "#1C2530");
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
    fb.textContent = juste ? "✔ Tout est juste ! Entrée : " + (serie.k === serie.N - 1 ? "voir ta note." : "question suivante.") :
      "✘ " + (tous.length - bons) + " case" + (tous.length - bons > 1 ? "s" : "") + " à revoir (en rouge) : corrige et vérifie à nouveau, ou demande la correction.";
    reussi = juste;
    if (!juste) { var ko = q(".ta-f.ko input"); if (ko) ko.focus({ preventScroll: true }); }
    if (essai === 1) compter(juste);
    if (juste) corriger();
  }
  function compter(juste) {
    serie.res[serie.k] = juste;
    q("#ta-next").disabled = false;
    points();
  }
  function suivante() {
    if (q("#ta-next").disabled) return;
    if (serie.k < serie.N - 1) { serie.k++; poser(); } else bilan();
  }
  function bilan() {
    var ok = serie.res.filter(function (r) { return r === true; }).length, N = serie.N;
    var note = Math.round(ok / N * 40) / 2, et = note >= 18 ? "★★★" : note >= 14 ? "★★☆" : note >= 10 ? "★☆☆" : "☆☆☆";
    var parType = serie.types.map(function (t) {
      var idx = serie.liste.map(function (x, i) { return x === t ? i : -1; }).filter(function (i) { return i >= 0; });
      return NOM_TYPE[t] + " : " + idx.filter(function (i) { return serie.res[i]; }).length + " / " + idx.length;
    }).join(" · ");
    q("#ta-bilan").innerHTML = "<h2>Série terminée</h2>" +
      '<p class="ta-note" id="ta-note">' + fr(note, 1) + " <small>/ 20</small> <span class=\"ta-et\">" + et + "</span></p>" +
      "<p>" + ok + " question" + (ok > 1 ? "s" : "") + " réussie" + (ok > 1 ? "s" : "") + " du premier coup sur " + N + ". " + parType + ".</p>" +
      '<ol class="ta-bil-l">' + serie.liste.map(function (t, i) {
        return '<li class="' + (serie.res[i] ? "ok" : "ko") + '">' + (serie.res[i] ? "✔ " : "✘ ") + "Q" + (i + 1) + " · " + NOM_TYPE[t] + "</li>"; }).join("") + "</ol>" +
      '<div class="ta-act"><button type="button" class="btn" id="ta-encore">Nouvelle série (mêmes réglages)</button>' +
      '<button type="button" class="btn ghost" id="ta-regl">Changer les réglages</button></div>';
    q("#ta-grid").hidden = true; q("#ta-bilan").hidden = false;
    q("#ta-encore").addEventListener("click", function () { lancer(serie.types, serie.N); });
    q("#ta-regl").addEventListener("click", function (e) { e.stopPropagation(); q("#ta-cfg").open = true; });
    q("#ta-encore").focus({ preventScroll: true });
    q("#ta-bilan").scrollIntoView({ block: "nearest" });
  }
  function corriger() {
    var c = cur, plan = c.niv < 3, a = c.BA, R = c.R;
    var n = plan ? 2 : 3, sl = function (v) { return v.slice(0, n); };
    var h = "<p><b>1. Vecteur <span class=\"vec\">BA</span></b> = A − B :</p><div class=\"eq\"><span class=\"vec\">BA</span> = " +
      col(sl(c.A).map(function (x, i) { return fr(x) + " − " + par(c.B[i]); })) + " = <b>" + col(sl(a).map(function (x) { return fr(x); })) + "</b> m</div>";
    h += "<p><b>2. Résultante</b> : elle ne change pas d'un point à l'autre :</p><div class=\"eq\"><span class=\"vec\">R</span> = " + col(sl(R).map(function (x) { return fr(x); })) + " N</div>";
    if (plan) {
      h += '<p><b>3. Moment en B</b> : <i>N</i><sub>B</sub> = <i>N</i><sub>A</sub> + <i>a</i>·<i>Y</i> − <i>b</i>·<i>X</i></p><div class="eq"><i>N</i><sub>B</sub> = ' +
        fr(c.MA[2]) + " + " + par(a[0]) + " × " + par(R[1]) + " − " + par(a[1]) + " × " + par(R[0]) + " = " + fr(c.MA[2]) + " + " + par(c.C[2]) +
        " = <b>" + fr(c.MB[2]) + " N·m</b></div>";
    } else {
      h += "<p><b>3. Produit vectoriel</b> <span class=\"vec\">BA</span> ∧ <span class=\"vec\">R</span> = (b·Z − c·Y ; c·X − a·Z ; a·Y − b·X) :</p>" +
        '<div class="eq">L : ' + par(a[1]) + " × " + par(R[2]) + " − " + par(a[2]) + " × " + par(R[1]) + " = " + fr(c.C[0]) +
        "<br>M : " + par(a[2]) + " × " + par(R[0]) + " − " + par(a[0]) + " × " + par(R[2]) + " = " + fr(c.C[1]) +
        "<br>N : " + par(a[0]) + " × " + par(R[1]) + " − " + par(a[1]) + " × " + par(R[0]) + " = " + fr(c.C[2]) + "</div>" +
        "<p><b>4. Moment en B</b> = <span class=\"vec\">M</span><sub>A</sub> + <span class=\"vec\">BA</span> ∧ <span class=\"vec\">R</span> :</p><div class=\"eq\">" +
        col([0, 1, 2].map(function (i) { return fr(c.MA[i]) + " + " + par(c.C[i]); })) + " = <b>" + col(c.MB.map(function (x) { return fr(x); })) + "</b> N·m</div>";
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
    var cc = q("#ta-col-cor"), r = cc.getBoundingClientRect();
    if (interagi && r.top > innerHeight - 80) cc.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  q("#ta-check").addEventListener("click", verifier);
  q("#ta-sol").addEventListener("click", function () { if (essai === 0) { essai = 1; compter(false); } corriger(); q("#ta-next").focus({ preventScroll: true }); });
  q("#ta-next").addEventListener("click", suivante);
  root.addEventListener("keydown", function (e) {
    if (e.key !== "Enter" || !e.target.closest(".ta-f")) return;
    e.preventDefault();
    if (reussi) suivante(); else verifier();
  });
  function choix() {
    var types = qa("[name=ta-type]:checked").map(function (x) { return +x.value; });
    var N = +(q("[name=ta-n]:checked") || { value: 10 }).value;
    q("#ta-cfg-msg").textContent = types.length ? "" : "Coche au moins un type de question.";
    q("#ta-go").disabled = !types.length;
    return { types: types, N: N };
  }
  qa("[name=ta-type], [name=ta-n]").forEach(function (x) { x.addEventListener("change", choix); });
  q("#ta-go").addEventListener("click", function () { var c = choix(); if (!c.types.length) return; q("#ta-cfg").open = false; lancer(c.types, c.N); });
  root.addEventListener("pointerdown", function () { interagi = true; });
  root.addEventListener("keydown", function () { interagi = true; }, true);
  document.addEventListener("click", function (e) {      // fermer les menus en cliquant ailleurs
    qa(".ta-pd").forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; });
  });
  qa(".ta-pd").forEach(function (d) {                      // un seul menu ouvert à la fois
    d.addEventListener("toggle", function () { if (d.open) qa(".ta-pd").forEach(function (x) { if (x !== d) x.open = false; }); });
  });
  window.__ta__ = { courant: function () { return cur; }, niveau: function () { return niv; }, serie: function () { return serie; } };
  lancer([1, 2, 3], 10);
})();
</script>"""
