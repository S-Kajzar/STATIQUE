#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atelier de statique graphique : environnement de tracé sur document réponse (DR).

Greffé sur le moteur de tracé du gabarit (classe Sketch, exposée par window.__app__.sketches) sans le modifier :
un script chargé après le moteur remplace, pour les seuls tracés dont le décor porte une entrée « graph », les
méthodes de saisie et de dessin. Les autres tracés gardent le comportement du gabarit.

Outils : Vecteur (longueur et intensité à l'échelle affichées, intensité imposée), Droite d'action (droite
prolongée sur toute la feuille), Parallèle (à une droite ou à un vecteur choisi ; un clic sur une autre droite change la
référence), Segment, Point, Mesurer (distance en cm du document, intensité correspondante, angle avec l'horizontale),
Texte, Gomme, Sélection (recolorer, changer l'épaisseur ou supprimer un tracé posé). En plein écran, le DR est
dimensionné pour tenir en entier. Après validation, la correction se rejoue pas à pas (étapes de DR.construire).
Aimantation aux points remarquables du DR, aux extrémités des tracés et aux intersections des droites.
Le fond du DR est affiché en transparence réglable sous les tracés.

Ce module fournit aussi la description d'un DR (points, droites données, zones d'échelle) et la résolution
d'un solide soumis à trois forces, qui génère la correction superposée.
"""
import json
import math

# ============================================================ barre d'outils
COULEURS = [("#1F5FA8", "bleue"), ("#1B7A43", "verte"), ("#7B3FA0", "violette"), ("#1C2530", "noire")]


def toolbar(s):
    label = s["label"]
    sw = "".join(f'<button type="button" class="sw" data-color="{c}" aria-label="Couleur {n}" '
                 f'aria-pressed="{"true" if i == 0 else "false"}" style="background:{c}"></button>'
                 for i, (c, n) in enumerate(COULEURS))
    outils = [("vec", "Vecteur", "Tracer un vecteur force à l'échelle"),
              ("dir", "Droite d'action", "Tracer une droite prolongée sur toute la feuille"),
              ("par", "Parallèle", "Tracer la parallèle à une droite ou à un vecteur"),
              ("line", "Segment", "Tracer un segment"),
              ("pt", "Point", "Marquer un point (point de concours…)"),
              ("mes", "Mesurer", "Mesurer une longueur et l'intensité correspondante"),
              ("text", "Texte", "Écrire un nom"),
              ("erase", "Gomme", "Effacer un tracé"),
              ("sel", "Sélection", "Choisir un tracé déjà posé pour changer sa couleur, son épaisseur ou le supprimer")]
    btn = "".join(f'<button type="button" data-tool="{k}" aria-pressed="{"true" if k == "vec" else "false"}" '
                  f'title="{t}">{n}</button>' for k, n, t in outils)
    return f"""              <div class="sk-toolbar gt-toolbar" role="toolbar" aria-label="Outils de construction {label}">
                <span class="tb-group gt-tools">{btn}</span>
                <span class="sep"></span>
                {sw}
                <span class="sep"></span>
                <span class="tb-group"><span class="tb-lab">Trait</span>
                  <button type="button" data-width="fin" aria-pressed="false">Fin</button>
                  <button type="button" data-width="moyen" aria-pressed="true">Moyen</button>
                  <button type="button" data-width="epais" aria-pressed="false">Épais</button></span>
                <span class="sep"></span>
                <label class="tb-group gt-imp"><span class="tb-lab">Intensité imposée</span>
                  <input type="text" class="gt-val" inputmode="decimal" autocomplete="off" placeholder="libre" aria-label="Intensité imposée du prochain vecteur"><span class="gt-unit"></span></label>
                <button type="button" class="gt-snap" aria-pressed="true" title="Accrocher aux points, extrémités et intersections">Aimant</button>
                <label class="tb-group gt-opa-l"><span class="tb-lab">DR</span>
                  <input type="range" class="gt-opa" min="15" max="100" step="5" value="45" aria-label="Opacité du document réponse"></label>
                <span class="sep"></span>
                <span class="tb-group"><span class="tb-lab">Zoom</span>
                  <button type="button" data-zoom="out" aria-label="Réduire le zoom">−</button>
                  <span class="zoom-val">100 %</span>
                  <button type="button" data-zoom="in" aria-label="Agrandir le zoom">+</button>
                  <button type="button" data-zoom="reset">Ajuster</button></span>
                <span class="sep"></span>
                <button type="button" data-act="undo">Annuler</button>
                <button type="button" class="gt-del" data-act="del" disabled title="Supprimer le tracé sélectionné (touche Suppr)">Supprimer</button>
                <button type="button" data-act="clear">Tout effacer</button>
                <span class="spacer"></span>
                <button type="button" class="btn-drprint" data-act="drprint">Imprimer les DR</button>
                <button type="button" data-act="full" aria-pressed="false">Plein écran</button>
              </div>
"""


CSS = """<style>
/* ---------- atelier de statique graphique ---------- */
.gt-toolbar .gt-tools{flex-wrap:wrap}
.gt-toolbar .gt-tools button[aria-pressed="true"]{background:var(--bleu); color:#fff; border-color:var(--bleu)}
.gt-toolbar .gt-val{width:5.2em; border:1px solid var(--trait); padding:3px 5px; font:600 .85rem var(--f-texte)}
.gt-toolbar .gt-unit{font:600 .8rem var(--f-titre); color:var(--encre-2)}
.gt-toolbar .gt-snap[aria-pressed="true"]{background:var(--jaune); color:var(--encre); border-color:var(--encre)}
.gt-toolbar .gt-opa{width:80px; accent-color:var(--bleu)}
.gt-status{background:var(--bleu-pale); border:1px solid #C9D8EC; border-top:0; padding:5px 10px; font-size:.86rem; line-height:1.4; color:var(--encre); min-height:2.9em}
.gt-status b{color:var(--bleu)}
.sketch.locked .gt-status{display:none}
.gt-sketch .sk-stage canvas{cursor:crosshair}
.gt-aide{background:#fff; border:1px solid var(--trait-fin); padding:6px 12px; margin:6px 0; font-size:.9rem}
.gt-aide summary{cursor:pointer; font-weight:700}
.gt-aide dl{display:grid; grid-template-columns:max-content 1fr; gap:4px 12px; margin:6px 0}
.gt-aide dt{font:700 .9rem var(--f-titre)}
.gt-aide dd{margin:0}
.res-table td,.res-table th{text-align:center}
.gt-toolbar button[data-tool="sel"][aria-pressed="true"]{background:var(--encre); border-color:var(--encre)}
.gt-toolbar .gt-del:not(:disabled){border-color:var(--rouge); color:var(--rouge)}
.gt-sketch.tool-sel .sk-stage canvas{cursor:pointer}
/* correction pas à pas */
.gt-steps{display:none; border:1px solid #C9D8EC; border-top:0; background:#fff; padding:6px 10px 8px; font-size:.9rem; line-height:1.4}
.sketch.revealed .gt-steps{display:block}
.gt-steps-head{display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin:0 0 4px}
.gt-steps-head b{font:800 .95rem var(--f-titre); margin-right:auto}
.gt-steps-head button{border:1.5px solid var(--encre); background:#fff; padding:3px 9px; font:700 .82rem var(--f-titre); cursor:pointer}
.gt-steps-head button:hover{background:var(--jaune-pale)}
.gt-steps-head button:disabled{opacity:.4; cursor:default}
.gt-st-n{font:700 .85rem var(--f-titre); color:var(--bleu); min-width:6.5em; text-align:center}
.gt-st-list{margin:0; padding:0; list-style:none}
.gt-st-list li{margin:2px 0; cursor:pointer; color:var(--encre-2)}
.gt-st-list li .st-d{display:none}
.gt-st-list li.on{color:var(--encre)}
.gt-st-list li.on .st-d,.gt-steps.all .gt-st-list li .st-d{display:inline}
.gt-st-list li.on>b{color:var(--bleu)}
/* plein écran : le DR occupe toute la place restante et tient en entier (dimensionné par le script) */
.gt-sketch.is-full .sk-layout{flex:1; min-height:0; display:flex}
.gt-sketch.is-full .sk-main{flex:1; min-height:0; height:auto; align-items:stretch}
.gt-sketch.is-full .sk-stage{flex:1 1 0; min-height:0; max-width:none; width:100%; display:flex; align-items:center;
  justify-content:center; background:transparent; border:0}
.gt-sketch.is-full .sk-stage canvas{flex:none; max-width:none; max-height:none; box-shadow:0 0 0 1px var(--trait)}
.gt-sketch.is-full .sk-stage.zoomed{display:block; overflow:auto; max-height:none}
.gt-sketch.is-full .selfeval,.gt-sketch.is-full .sk-print-wrap{display:none!important}
.gt-sketch.is-full .gt-status{min-height:0}
.gt-sketch.is-full .gt-steps{max-height:24vh; overflow:auto}
.gt-sketch.is-full .gt-st-list li:not(.on){display:none}
.gt-sketch.is-full .gt-steps.all .gt-st-list li{display:list-item}
@media print{ .gt-status{display:none!important} }
</style>"""


# ============================================================ moteur (greffon)
JS = r"""<script>/* ATELIER DE STATIQUE GRAPHIQUE — outils de construction greffés sur le moteur de tracé du gabarit
   (le moteur n'est pas modifié : seules les méthodes des tracés « graph » sont surchargées). */
(function () {
  "use strict";
  var app = window.__app__;
  if (!app || !app.sketches) return;
  var ids = Object.keys(app.sketches).filter(function (id) { var d = app.sketches[id].dec; return d && d.graph; });
  if (!ids.length) return;
  var P = Object.getPrototypeOf(app.sketches[ids[0]]);
  var base = {};
  ["down", "move", "up", "paint", "draw", "eraseAt", "setTool", "toggleFull", "setZoom"].forEach(function (k) { base[k] = P[k]; });
  var NEW = { vec: 1, dir: 1, par: 1, pt: 1, mes: 1, line: 1 };
  var HINTS = {
    vec: "<b>Vecteur</b> : appuie sur l'origine, glisse jusqu'à l'extrémité ; la longueur et l'intensité à l'échelle s'affichent. Pour un vecteur connu, saisis d'abord son intensité dans « Intensité imposée ».",
    dir: "<b>Droite d'action</b> : appuie sur un point de la droite et glisse vers un second point ; la droite est prolongée sur toute la feuille.",
    par: "<b>Parallèle</b> : clique d'abord sur la droite ou le vecteur de référence, puis appuie là où doit passer la parallèle (glisse pour ajuster). Pour changer de référence, clique simplement sur une autre droite ou un autre vecteur.",
    line: "<b>Segment</b> : trait droit entre deux points.",
    pt: "<b>Point</b> : clique pour marquer un point (point de concours I…), puis nomme-le avec l'outil Texte.",
    mes: "<b>Mesurer</b> : glisse d'un point à l'autre ; la distance en cm du document, l'intensité correspondante et l'angle s'affichent.",
    text: "<b>Texte</b> : clique à l'endroit voulu, tape le nom, valide avec Entrée.",
    erase: "<b>Gomme</b> : passe sur un tracé pour l'effacer.",
    sel: "<b>Sélection</b> : clique sur un tracé déjà posé ; il s'entoure de jaune. Clique alors une couleur ou une épaisseur pour le modifier, ou « Supprimer » (touche Suppr). Échap désélectionne.",
    pen: "<b>Crayon</b> : tracé libre."
  };
  function fr(x, d) { return (Math.abs(x) < 0.5 * Math.pow(10, -d) ? 0 : x).toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function sub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function unit(u) { var n = Math.hypot(u[0], u[1]) || 1; return [u[0] / n, u[1] / n]; }
  function dist(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1]); }
  function cross(u, v) { return u[0] * v[1] - u[1] * v[0]; }
  function segDist(p, a, b) {
    var dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy;
    var t = L2 ? ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2 : 0;
    t = Math.max(0, Math.min(1, t));
    return Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy);
  }
  function lineDist(p, q, u) { return Math.abs(cross(u, sub(p, q))); }
  function G(s) { return s.dec.graph; }
  function off(s) { return [s.dec.pad.l, s.dec.pad.t]; }
  function inPoly(x, y, poly) {
    var inside = false;
    for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      var xi = poly[i][0], yi = poly[i][1], xj = poly[j][0], yj = poly[j][1];
      if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) inside = !inside;
    }
    return inside;
  }
  function zoneAt(s, pt) {
    var z = G(s).zones, o = off(s), x = pt[0] - o[0], y = pt[1] - o[1];
    for (var i = 0; i < z.length; i++) if (!z[i].poly || inPoly(x, y, z[i].poly)) return z[i];
    return z[z.length - 1];
  }
  function lenInfo(s, a, b) {
    var L = dist(a, b), c = L / G(s).pxPerCm, z = zoneAt(s, a);
    var ang = Math.atan2(-(b[1] - a[1]), b[0] - a[0]) * 180 / Math.PI;
    return { cm: c, val: c * z.scale, z: z, ang: ang };
  }
  function lineOf(st) {
    if (st.t === "dir") return { p: st.a, u: unit(sub(st.b, st.a)), inf: true };
    if (st.t === "par") return { p: st.a, u: st.u, inf: true };
    if (st.t === "vec" || st.t === "line" || st.t === "arrow") return { p: st.a, u: unit(sub(st.b, st.a)), inf: false, a: st.a, b: st.b };
    return null;
  }
  function refLines(s) {
    var o = off(s);
    return (G(s).refs || []).map(function (r) {
      var a = [r[0] + o[0], r[1] + o[1]], b = [r[2] + o[0], r[3] + o[1]];
      return { p: a, u: unit(sub(b, a)), inf: true, ref: true };
    });
  }
  function allLines(s) {
    var L = refLines(s);
    s.strokes.forEach(function (st) { var l = lineOf(st); if (l && (l.inf || dist(l.a, l.b) > 3)) L.push(l); });
    return L;
  }
  function inter(L1, L2, W, H) {
    var d = cross(L1.u, L2.u);
    if (Math.abs(d) < 1e-6) return null;
    var w = sub(L2.p, L1.p), t = cross(w, L2.u) / d, t2 = cross(w, L1.u) / d;
    var q = [L1.p[0] + t * L1.u[0], L1.p[1] + t * L1.u[1]];
    function ok(L, tt) { if (L.inf) return true; var n = dist(L.a, L.b); return tt >= -0.02 * n - 2 && tt <= 1.02 * n + 2; }
    if (!ok(L1, t) || !ok(L2, t2)) return null;
    if (q[0] < 0 || q[1] < 0 || q[0] > W || q[1] > H) return null;
    return q;
  }
  function snapCands(s) {
    var o = off(s), g = G(s), pts = [];
    Object.keys(g.points || {}).forEach(function (k) { pts.push({ x: g.points[k][0] + o[0], y: g.points[k][1] + o[1], lab: k }); });
    s.strokes.forEach(function (st) {
      if (st.a && st.t !== "par") pts.push({ x: st.a[0], y: st.a[1] });
      if (st.b && st.t !== "dir") pts.push({ x: st.b[0], y: st.b[1] });
      if (st.t === "par") pts.push({ x: st.a[0], y: st.a[1] });
      if (st.t === "pt") pts.push({ x: st.x, y: st.y });
    });
    var L = allLines(s);
    for (var i = 0; i < L.length; i++)
      for (var j = i + 1; j < L.length; j++) {
        var q = inter(L[i], L[j], s.W, s.H);
        if (q) pts.push({ x: q[0], y: q[1], inter: true });
      }
    return pts;
  }
  function snap(s, p) {
    if (!s.gt.snap) return { x: p.x, y: p.y };
    var r = 14 * p.k, best = null, bd = r;
    snapCands(s).forEach(function (c) { var d = Math.hypot(c.x - p.x, c.y - p.y); if (d < bd) { bd = d; best = c; } });
    return best ? { x: best.x, y: best.y, snapped: true, lab: best.lab, inter: best.inter } : { x: p.x, y: p.y };
  }
  function pickLine(s, p) {
    var r = 12 * p.k, best = null, bd = r, q = [p.x, p.y];
    allLines(s).forEach(function (L) {
      var d = L.inf ? lineDist(q, L.p, L.u) : segDist(q, L.a, L.b);
      if (d < bd) { bd = d; best = L; }
    });
    return best;
  }
  function clip(s, p, u) {
    var t0 = -1e9, t1 = 1e9, W = s.W, H = s.H;
    [[0, W, p[0], u[0]], [0, H, p[1], u[1]]].forEach(function (c) {
      if (Math.abs(c[3]) < 1e-9) { if (c[2] < c[0] || c[2] > c[1]) { t0 = 1; t1 = 0; } return; }
      var a = (c[0] - c[2]) / c[3], b = (c[1] - c[2]) / c[3];
      t0 = Math.max(t0, Math.min(a, b)); t1 = Math.min(t1, Math.max(a, b));
    });
    if (t0 > t1) return null;
    return [[p[0] + t0 * u[0], p[1] + t0 * u[1]], [p[0] + t1 * u[0], p[1] + t1 * u[1]]];
  }
  function status(s, html) { var el = s.root.querySelector(".gt-status"); if (el) el.innerHTML = html; }
  function imposed(s, a, b) {
    var v = s.gt.val; if (!(v > 0)) return b;
    var d = sub(b, a); if (Math.hypot(d[0], d[1]) < 1) return b;
    var z = zoneAt(s, a), Lpx = v / z.scale * G(s).pxPerCm, u = unit(d);
    return [a[0] + u[0] * Lpx, a[1] + u[1] * Lpx];
  }
  function showLen(s, st) {
    var i = lenInfo(s, st.a, st.b), z = i.z;
    var what = st.t === "vec" ? "Vecteur" : st.t === "mes" ? "Mesure" : "Segment";
    var ang = i.ang; if (st.t !== "vec") { if (ang < 0) ang += 180; if (ang >= 180) ang -= 180; }
    status(s, "<b>" + what + "</b> : " + fr(i.cm, 2) + " cm → <b>" + fr(i.val, 0) + " " + z.unit + "</b> (échelle 1 cm ↔ " +
      fr(z.scale, 0) + " " + z.unit + ") · " + fr(ang, 0) + "° avec l'horizontale");
  }

  // ---------- dessin
  function arrowHead(ctx, a, b, color, w) {
    var u = unit(sub(b, a)), h = Math.max(10, w * 4.2), bw = h * 0.45;
    ctx.save(); ctx.fillStyle = color; ctx.beginPath();
    ctx.moveTo(b[0], b[1]);
    ctx.lineTo(b[0] - u[0] * h - u[1] * bw, b[1] - u[1] * h + u[0] * bw);
    ctx.lineTo(b[0] - u[0] * h + u[1] * bw, b[1] - u[1] * h - u[0] * bw);
    ctx.closePath(); ctx.fill(); ctx.restore();
  }
  function seg(ctx, a, b, color, w, dash) {
    ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = "round";
    if (dash) ctx.setLineDash(dash);
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); ctx.restore();
  }
  function label(ctx, s, x, y, color, size, align) {
    ctx.save(); ctx.font = "700 " + size + "px system-ui, Segoe UI, Arial, sans-serif";
    ctx.textAlign = align || "left"; ctx.textBaseline = "middle";
    ctx.lineWidth = Math.max(2, size / 4); ctx.strokeStyle = "rgba(255,255,255,.92)"; ctx.strokeText(s, x, y);
    ctx.fillStyle = color; ctx.fillText(s, x, y); ctx.restore();
  }
  function drawStroke(s, ctx, st) {
    if (st.t === "pen") {
      ctx.save(); ctx.strokeStyle = st.c; ctx.lineWidth = st.w; ctx.lineCap = "round"; ctx.lineJoin = "round";
      ctx.beginPath(); ctx.moveTo(st.pts[0][0], st.pts[0][1]);
      for (var i = 1; i < st.pts.length; i++) ctx.lineTo(st.pts[i][0], st.pts[i][1]);
      ctx.stroke(); ctx.restore();
    } else if (st.t === "line") seg(ctx, st.a, st.b, st.c, st.w);
    else if (st.t === "arrow" || st.t === "vec") {
      if (dist(st.a, st.b) < 1) return;
      var u = unit(sub(st.b, st.a)), h = Math.max(10, st.w * 4.2);
      seg(ctx, st.a, [st.b[0] - u[0] * h * 0.6, st.b[1] - u[1] * h * 0.6], st.c, st.w);
      arrowHead(ctx, st.a, st.b, st.c, st.w);
      if (st.t === "vec") { ctx.save(); ctx.fillStyle = st.c; ctx.beginPath(); ctx.arc(st.a[0], st.a[1], st.w * 0.9, 0, Math.PI * 2); ctx.fill(); ctx.restore(); }
    } else if (st.t === "dir" || st.t === "par") {
      var L = lineOf(st); if (st.t === "dir" && dist(st.a, st.b) < 1) return;
      var c = clip(s, L.p, L.u); if (!c) return;
      seg(ctx, c[0], c[1], st.c, st.w, st.t === "dir" ? [st.w * 6, st.w * 3, st.w, st.w * 3] : [st.w * 4, st.w * 3]);
      var r = st.w * 2.2;
      seg(ctx, [st.a[0] - r, st.a[1] - r], [st.a[0] + r, st.a[1] + r], st.c, st.w * 0.8);
      seg(ctx, [st.a[0] - r, st.a[1] + r], [st.a[0] + r, st.a[1] - r], st.c, st.w * 0.8);
    } else if (st.t === "pt") {
      var q = st.w * 3;
      seg(ctx, [st.x - q, st.y - q], [st.x + q, st.y + q], st.c, st.w);
      seg(ctx, [st.x - q, st.y + q], [st.x + q, st.y - q], st.c, st.w);
    } else if (st.t === "text") label(ctx, st.s, st.x, st.y, st.c, st.size, "left");
  }

  // ---------- un tracé est-il sous le pointeur ?
  function hit(s, st, p, r) {
    var w = (st.w || 2) / 2, q = [p.x, p.y];
    if (st.t === "pen") { for (var i = 1; i < st.pts.length; i++) if (segDist(q, st.pts[i - 1], st.pts[i]) <= r + w) return true; return false; }
    if (st.t === "line" || st.t === "arrow" || st.t === "vec") return segDist(q, st.a, st.b) <= r + w;
    if (st.t === "dir" || st.t === "par") { var L = lineOf(st); return lineDist(q, L.p, L.u) <= r + w; }
    if (st.t === "pt") return Math.hypot(p.x - st.x, p.y - st.y) <= r + st.w * 3;
    if (st.t === "text") {
      var ctx = s.ctx; ctx.save(); ctx.font = "700 " + st.size + "px system-ui, Segoe UI, Arial, sans-serif";
      var tw = ctx.measureText(st.s).width; ctx.restore();
      return p.x >= st.x - r && p.x <= st.x + tw + r && p.y >= st.y - st.size / 2 - r && p.y <= st.y + st.size / 2 + r;
    }
    return false;
  }
  var NOMS = { vec: "Vecteur", dir: "Droite d'action", par: "Parallèle", line: "Segment", pt: "Point", text: "Texte", pen: "Tracé libre", arrow: "Flèche" };
  function selOk(s) { if (s.gt.sel !== null && s.gt.sel >= s.strokes.length) s.gt.sel = null; return s.gt.sel !== null; }
  function updSel(s) {
    var ok = selOk(s), del = s.root.querySelector(".gt-del");
    if (del) del.disabled = !ok || s.locked;
    if (s.tool !== "sel") return;
    if (ok) {
      var st = s.strokes[s.gt.sel];
      status(s, "<b>" + (NOMS[st.t] || "Tracé") + " sélectionné.</b> Clique une couleur ou une épaisseur pour le modifier, ou « Supprimer » (touche Suppr). Échap : désélectionner.");
    } else status(s, HINTS.sel);
  }
  function supprimer(s) {
    if (s.locked || !selOk(s)) return;
    s.strokes.splice(s.gt.sel, 1); s.gt.sel = null; updSel(s); s.draw();
  }

  // ---------- surcharges
  P.setTool = function (t) {
    base.setTool.call(this, t);
    if (!this.gt) return;
    this.gt.ref = null; this.gt.meas = null; this.gt.hover = null; this.gt.sel = null;
    this.root.classList.toggle("tool-sel", t === "sel");
    status(this, HINTS[t] || "");
    updSel(this);
    this.draw();
  };
  P.down = function (e) {
    if (!this.gt) return base.down.call(this, e);
    this.gt.meas = null;
    if (this.tool === "sel") {
      if (this.locked || e.button > 0) return;
      e.preventDefault();
      var ps = this.pos(e), r = Math.max(6, 11 * ps.k), found = null;
      for (var i = this.strokes.length - 1; i >= 0; i--) if (hit(this, this.strokes[i], ps, r)) { found = i; break; }
      this.gt.sel = found; this.gt.k = ps.k; updSel(this); this.draw(); return;
    }
    if (!NEW[this.tool]) return base.down.call(this, e);
    if (this.locked || e.button > 0) return;
    e.preventDefault();
    var p = this.pos(e), w = Math.max(0.6, 2.6 * this.wFactor * p.k), q = snap(this, p);
    this.gt.k = p.k;
    if (this.tool === "pt") { this.strokes.push({ t: "pt", x: q.x, y: q.y, c: this.color, w: w, wf: this.wFactor }); this.draw(); return; }
    if (this.tool === "par" && !this.gt.ref) {
      var L = pickLine(this, p);
      if (L) { this.gt.ref = L; status(this, "<b>Référence choisie.</b> Appuie maintenant à l'endroit où doit passer la parallèle (une extrémité de vecteur par exemple), puis glisse pour ajuster."); }
      else status(this, "<b>Parallèle</b> : clique d'abord sur une droite ou sur un vecteur de référence.");
      this.draw(); return;
    }
    this.canvas.setPointerCapture(e.pointerId);
    if (this.tool === "par") {
      // un simple clic sur une autre droite (hors point d'accroche) change la référence ; appuyer et glisser pose la parallèle
      var autre = q.snapped ? null : pickLine(this, p);
      this.cur = { t: "par", a: [q.x, q.y], u: this.gt.ref.u.slice(), c: this.color, w: w * 0.8, wf: this.wFactor, pend: autre, p0: [p.x, p.y] };
    }
    else this.cur = { t: this.tool, a: [q.x, q.y], b: [q.x, q.y], c: this.color, w: this.tool === "dir" ? w * 0.8 : w, wf: this.wFactor };
    this.draw();
  };
  P.move = function (e) {
    if (!this.gt || this.erasing || (this.cur && !NEW[this.cur.t])) return base.move.call(this, e);
    var p = this.pos(e); this.gt.k = p.k;
    var q = (NEW[this.tool] && !this.locked) ? snap(this, p) : null;
    var hv = q && q.snapped ? q : null;
    var changed = !!hv !== !!this.gt.hover || (hv && (hv.x !== this.gt.hover.x || hv.y !== this.gt.hover.y));
    this.gt.hover = hv;
    if (this.cur) {
      if (this.cur.pend && Math.hypot(p.x - this.cur.p0[0], p.y - this.cur.p0[1]) > 6 * p.k) this.cur.pend = null;
      if (this.cur.t === "par") this.cur.a = [q.x, q.y];
      else {
        var b = [q.x, q.y];
        if (this.cur.t === "vec") b = imposed(this, this.cur.a, b);
        this.cur.b = b;
        if (this.cur.t !== "dir") showLen(this, this.cur);
      }
      changed = true;
    }
    if (changed) this.draw();
  };
  P.up = function (e) {
    if (!this.gt || !this.cur || !NEW[this.cur.t]) return base.up.call(this, e);
    var st = this.cur; this.cur = null;
    if (st.t === "mes") { if (dist(st.a, st.b) > 2) { this.gt.meas = st; showLen(this, st); } this.draw(); return; }
    if (st.pend) {
      this.gt.ref = st.pend;
      status(this, "<b>Nouvelle référence choisie</b> (en jaune). Appuie là où doit passer la parallèle, ou clique une autre droite pour changer encore de référence.");
      this.draw(); return;
    }
    delete st.pend; delete st.p0;
    if (st.t === "par" || dist(st.a, st.b) > 3) this.strokes.push(st);
    if (st.t === "vec" && this.gt.val > 0) { this.gt.val = 0; var vi = this.root.querySelector(".gt-val"); if (vi) vi.value = ""; }
    this.draw();
  };
  P.eraseAt = function (p) {
    if (!this.gt) return base.eraseAt.call(this, p);
    var r = Math.max(6, 11 * p.k), self = this, before = this.strokes.length;
    this.strokes = this.strokes.filter(function (st) { return !hit(self, st, p, r); });
    if (this.strokes.length !== before) { this.gt.sel = null; this.draw(); }
  };
  P.paint = function (ctx, opts) {
    if (!this.gt) return base.paint.call(this, ctx, opts);
    var p = this.dec.pad, self = this;
    ctx.setTransform(this.rs, 0, 0, this.rs, 0, 0);
    ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, this.W, this.H);
    if (this.img.naturalWidth) {
      ctx.save(); ctx.globalAlpha = (opts.student || opts.corr) ? this.gt.alpha : 1;
      ctx.drawImage(this.img, p.l, p.t, this.iw, this.ih); ctx.restore();
    }
    ctx.save(); ctx.translate(p.l, p.t); this.dec.decorate(ctx); ctx.restore();
    var k = this.gt.k || 1;
    if (opts.live && this.gt.ref) {
      var c = this.gt.ref.inf ? clip(this, this.gt.ref.p, this.gt.ref.u) : [this.gt.ref.a, this.gt.ref.b];
      if (c) seg(ctx, c[0], c[1], "rgba(242,183,5,.55)", 9 * k);
    }
    if (opts.student) {
      if (opts.live && selOk(this)) {
        var sst = this.strokes[this.gt.sel], halo = {};
        Object.keys(sst).forEach(function (key) { halo[key] = sst[key]; });
        halo.c = "rgba(242,183,5,.65)"; halo.w = (sst.w || 2) + 9 * k;
        if (sst.t === "text") { ctx.save(); ctx.font = "700 " + sst.size + "px system-ui, Segoe UI, Arial, sans-serif";
          var tw = ctx.measureText(sst.s).width; ctx.fillStyle = "rgba(242,183,5,.45)";
          ctx.fillRect(sst.x - 4 * k, sst.y - sst.size * 0.65, tw + 8 * k, sst.size * 1.3); ctx.restore(); }
        else drawStroke(self, ctx, halo);
      }
      var list = this.cur && !this.cur.pend ? this.strokes.concat([this.cur]) : this.strokes;
      list.forEach(function (st) { if (st.t !== "mes") drawStroke(self, ctx, st); });
    }
    if (opts.corr && this.dec.correction) {
      ctx.save(); ctx.translate(p.l, p.t);
      var steps = this.dec.steps;
      if (opts.live && steps && steps.length && !this.gt.all) {
        for (var si = 0; si < this.gt.step; si++) {
          ctx.save(); ctx.globalAlpha = si < this.gt.step - 1 ? 0.35 : 1; steps[si].f(ctx); ctx.restore();
        }
      } else this.dec.correction(ctx);
      ctx.restore();
    }
    if (opts.live) {
      var m = this.cur && this.cur.t === "mes" ? this.cur : this.gt.meas;
      if (m && dist(m.a, m.b) > 1) {
        var i = lenInfo(this, m.a, m.b), u = unit(sub(m.b, m.a)), n = [-u[1] * 7 * k, u[0] * 7 * k];
        seg(ctx, m.a, m.b, "#D35400", 2 * k, [6 * k, 4 * k]);
        seg(ctx, [m.a[0] - n[0], m.a[1] - n[1]], [m.a[0] + n[0], m.a[1] + n[1]], "#D35400", 2 * k);
        seg(ctx, [m.b[0] - n[0], m.b[1] - n[1]], [m.b[0] + n[0], m.b[1] + n[1]], "#D35400", 2 * k);
        label(ctx, fr(i.cm, 2) + " cm ↔ " + fr(i.val, 0) + " " + i.z.unit, (m.a[0] + m.b[0]) / 2 + n[0] * 2, (m.a[1] + m.b[1]) / 2 + n[1] * 2, "#D35400", 14 * k, "center");
      }
      if (this.gt.hover) {
        var h = this.gt.hover;
        ctx.save(); ctx.strokeStyle = h.inter ? "#D35400" : "#1F5FA8"; ctx.lineWidth = 2 * k;
        ctx.beginPath(); ctx.arc(h.x, h.y, 8 * k, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
        if (h.lab) label(ctx, h.lab, h.x + 11 * k, h.y - 11 * k, "#1F5FA8", 13 * k, "left");
        else if (h.inter) label(ctx, "intersection", h.x + 11 * k, h.y - 11 * k, "#D35400", 12 * k, "left");
      }
    }
  };
  function fit(s) {
    var cv = s.canvas, st = s.root.querySelector(".sk-stage");
    if (!s.root.classList.contains("is-full")) { cv.style.height = ""; if (s.zoom === 1) cv.style.width = ""; return; }
    var cw = st.clientWidth, ch = st.clientHeight; if (!cw || !ch) return;
    var k = Math.min(cw / s.W, (ch - 2) / s.H);
    cv.style.maxWidth = "none";
    if (s.zoom > 1) { cv.style.width = Math.floor(s.W * k * s.zoom) + "px"; cv.style.height = ""; }
    else { cv.style.width = Math.floor(s.W * k) + "px"; cv.style.height = Math.floor(s.H * k) + "px"; }
  }
  P.toggleFull = function () { base.toggleFull.call(this); if (this.gt) fit(this); };
  P.setZoom = function (what) { base.setZoom.call(this, what); if (this.gt) fit(this); };

  // ---------- correction pas à pas
  function stepsUI(s) {
    var steps = s.dec.steps; if (!steps || steps.length < 2) return;
    var box = document.createElement("div"); box.className = "gt-steps all";
    box.innerHTML = '<div class="gt-steps-head"><b>Correction pas à pas</b>' +
      '<button type="button" data-st="prev">◀ Précédente</button><span class="gt-st-n" aria-live="polite"></span>' +
      '<button type="button" data-st="next">Suivante ▶</button><button type="button" data-st="mode"></button></div>' +
      '<ol class="gt-st-list">' + steps.map(function (st, i) {
        return '<li data-i="' + i + '"><b>' + (i + 1) + ". " + st.t.charAt(0).toUpperCase() + st.t.slice(1) + "</b><span class=\"st-d\"> — " + st.d + "</span></li>";
      }).join("") + "</ol>";
    var anchor = s.root.querySelector(".gt-status");
    anchor.parentNode.insertBefore(box, anchor.nextSibling);
    var n = steps.length;
    function maj() {
      box.classList.toggle("all", s.gt.all);
      box.querySelector(".gt-st-n").textContent = s.gt.all ? "Toute la correction" : "Étape " + s.gt.step + " / " + n;
      box.querySelector("[data-st=mode]").textContent = s.gt.all ? "Voir pas à pas" : "Tout afficher";
      box.querySelector("[data-st=prev]").disabled = !s.gt.all && s.gt.step <= 1;
      box.querySelector("[data-st=next]").disabled = !s.gt.all && s.gt.step >= n;
      Array.prototype.forEach.call(box.querySelectorAll("li"), function (li, i) { li.classList.toggle("on", !s.gt.all && i === s.gt.step - 1); });
      s.showCorr = true; var tg = s.root.querySelector(".sk-corr-toggle input"); if (tg) tg.checked = true;
      s.draw();
    }
    function aller(k, all) { s.gt.all = !!all; if (!all) s.gt.step = Math.max(1, Math.min(n, k)); maj(); }
    box.querySelector("[data-st=prev]").addEventListener("click", function () { aller(s.gt.all ? n : s.gt.step - 1); });
    box.querySelector("[data-st=next]").addEventListener("click", function () { aller(s.gt.all ? 1 : s.gt.step + 1); });
    box.querySelector("[data-st=mode]").addEventListener("click", function () { aller(1, !s.gt.all); });
    Array.prototype.forEach.call(box.querySelectorAll("li"), function (li) {
      li.addEventListener("click", function () { aller(+li.getAttribute("data-i") + 1); });
    });
    s.gt.stepsMaj = function () { box.querySelector(".gt-st-n").textContent = s.gt.all ? "Toute la correction" : "Étape " + s.gt.step + " / " + n; };
    s.gt.stepsMaj();
    box.querySelector("[data-st=mode]").textContent = "Voir pas à pas";
  }

  P.draw = function () {
    if (!this.gt) return base.draw.call(this);
    var self = this;
    if (this.gt.raf) return;
    this.gt.raf = requestAnimationFrame(function () {
      self.gt.raf = 0;
      self.paint(self.ctx, { student: true, corr: self.showCorr && self.revealed, live: true });
    });
  };

  // ---------- initialisation des tracés « graph »
  ids.forEach(function (id) {
    var s = app.sketches[id], g = G(s), root = s.root;
    s.gt = { alpha: g.alpha || 0.45, snap: true, ref: null, hover: null, meas: null, val: 0, k: 1, raf: 0, sel: null, step: 1, all: true };
    Array.prototype.forEach.call(root.querySelectorAll("[data-color]"), function (b) {
      b.addEventListener("click", function () {
        if (s.tool === "sel" && selOk(s) && !s.locked) { s.strokes[s.gt.sel].c = b.getAttribute("data-color"); s.draw(); }
      });
    });
    Array.prototype.forEach.call(root.querySelectorAll("[data-width]"), function (b) {
      b.addEventListener("click", function () {
        if (s.tool !== "sel" || !selOk(s) || s.locked) return;
        var st = s.strokes[s.gt.sel], nf = { fin: 0.5, moyen: 1, epais: 2.1 }[b.getAttribute("data-width")], of = st.wf || 1;
        if (st.t === "text") st.size = st.size * (0.8 + 0.3 * nf) / (0.8 + 0.3 * of); else st.w = st.w * nf / of;
        st.wf = nf; s.draw();
      });
    });
    var del = root.querySelector(".gt-del");
    if (del) del.addEventListener("click", function () { supprimer(s); });
    var und = root.querySelector("[data-act=undo]");
    if (und) und.addEventListener("click", function () { s.gt.sel = null; updSel(s); });
    stepsUI(s);
    var stage = root.querySelector(".sk-stage");
    if (window.ResizeObserver) new ResizeObserver(function () { if (root.classList.contains("is-full")) fit(s); }).observe(stage);
    var opa = root.querySelector(".gt-opa");
    if (opa) { opa.value = Math.round(s.gt.alpha * 100); opa.addEventListener("input", function () { s.gt.alpha = opa.value / 100; s.draw(); }); }
    var val = root.querySelector(".gt-val"), un = root.querySelector(".gt-unit");
    if (un) un.textContent = g.zones[0].unit;
    if (val) val.addEventListener("input", function () {
      var v = parseFloat(String(val.value).replace(",", ".").replace(/\s/g, ""));
      s.gt.val = v > 0 ? v : 0;
      if (s.gt.val) status(s, "<b>Intensité imposée : " + fr(s.gt.val, 0) + " " + g.zones[0].unit + "</b>. Le prochain vecteur aura exactement cette longueur à l'échelle : choisis seulement son origine et sa direction.");
    });
    var sn = root.querySelector(".gt-snap");
    if (sn) sn.addEventListener("click", function () { s.gt.snap = !s.gt.snap; sn.setAttribute("aria-pressed", s.gt.snap ? "true" : "false"); s.gt.hover = null; s.draw(); });
    s.canvas.addEventListener("pointerleave", function () { if (s.gt.hover) { s.gt.hover = null; s.draw(); } });
    s.setTool("vec");
  });
  window.addEventListener("resize", function () { ids.forEach(function (id) { fit(app.sketches[id]); }); });
  document.addEventListener("keydown", function (e) {
    var t = e.target, tag = t && t.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || (t && t.isContentEditable)) return;
    ids.forEach(function (id) {
      var s = app.sketches[id];
      if (s.tool !== "sel" || !selOk(s)) return;
      if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); supprimer(s); }
      else if (e.key === "Escape") { s.gt.sel = null; updSel(s); s.draw(); }
    });
  });
  window.__atelier__ = { snapCands: snapCands, lenInfo: lenInfo, fit: fit };
})();
</script>"""


# ============================================================ description d'un DR et résolution graphique
def _unit(u):
    n = math.hypot(*u)
    return (u[0] / n, u[1] / n)


def _inter(p, u, q, v):
    d = u[0] * v[1] - u[1] * v[0]
    t = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / d
    return (p[0] + t * u[0], p[1] + t * u[1])


def _solve2(F, u, v):
    d = u[0] * v[1] - u[1] * v[0]
    return (-F[0] * v[1] + F[1] * v[0]) / d, (-u[0] * F[1] + u[1] * F[0]) / d


def angle(u):
    """Angle aigu (°) entre une direction et l'horizontale, dans [0 ; 90] (repère écran : y vers le bas)."""
    a = math.degrees(math.atan2(-u[1], u[0])) % 180
    return 180 - a if a > 90 else a


def trois_forces(known, second, third):
    """Solide soumis à trois forces non parallèles.

    known  = (nom, point, vecteur force connu (repère écran, en unité de force))
    second = (nom, point, direction connue)
    third  = (nom, point) : direction inconnue, déduite du point de concours I.
    Retourne I, les trois vecteurs force et leurs normes."""
    nk, pk, K = known
    n2, p2, u2 = second
    n3, p3 = third
    u2 = _unit(u2)
    I = _inter(pk, _unit(K), p2, u2)
    u3 = _unit((I[0] - p3[0], I[1] - p3[1]))
    a, b = _solve2(K, u2, u3)
    F2 = (a * u2[0], a * u2[1])
    F3 = (b * u3[0], b * u3[1])
    return {"I": I, "u3": u3, "forces": [(nk, pk, K), (n2, p2, F2), (n3, p3, F3)],
            "normes": {nk: math.hypot(*K), n2: abs(a), n3: abs(b)}}


def _clip(p, u, W, H):
    t0, t1 = -1e9, 1e9
    for lo, hi, c, d in ((0, W, p[0], u[0]), (0, H, p[1], u[1])):
        if abs(d) < 1e-9:
            continue
        a, b = (lo - c) / d, (hi - c) / d
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    return (p[0] + t0 * u[0], p[1] + t0 * u[1]), (p[0] + t1 * u[0], p[1] + t1 * u[1])


def fr(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def direction_txt(u):
    """Direction d'une droite (repère écran) en mots : verticale, horizontale ou inclinée de x° sur l'horizontale."""
    a = angle(u)
    if a > 88.5:
        return "verticale"
    if a < 1.5:
        return "horizontale"
    return f"inclinée d'environ {fr(a)}° sur l'horizontale"


def sens_txt(F):
    """Sens d'une force (repère écran) en mots."""
    a = math.degrees(math.atan2(-F[1], F[0]))
    for lo, hi, n in ((-22.5, 22.5, "vers la droite"), (22.5, 67.5, "vers le haut et la droite"),
                      (67.5, 112.5, "vers le haut"), (112.5, 157.5, "vers le haut et la gauche"),
                      (-67.5, -22.5, "vers le bas et la droite"), (-112.5, -67.5, "vers le bas"),
                      (-157.5, -112.5, "vers le bas et la gauche")):
        if lo <= a < hi:
            return n
    return "vers la gauche"


class DR:
    """Un document réponse : fond, points, droites données, zones d'échelle, constructions corrigées.

    La correction est découpée en étapes (etape) : chacune a un titre, une consigne simple et ses tracés ; l'atelier
    les affiche une à une (correction pas à pas) ou toutes ensemble (correction superposée)."""

    def __init__(self, name, img, size, px_cm, zones, points, refs=(), alpha=0.45, rs=1.2):
        self.name, self.img, (self.W, self.H), self.px_cm = name, img, size, px_cm
        self.zones, self.points, self.refs, self.alpha, self.rs = zones, points, list(refs), alpha, rs
        self.steps = []     # [{"t": titre, "d": consigne, "js": [instructions de dessin]}]
        self.f = max(1.0, self.W / 900)   # taille des traits et des textes, proportionnée au fond

    @property
    def corr(self):
        """Instructions de dessin de l'étape en cours (une étape « Correction » est créée au besoin)."""
        if not self.steps:
            self.etape("Correction", "")
        return self.steps[-1]["js"]

    def etape(self, titre, consigne):
        self.steps.append({"t": titre, "d": consigne, "js": []})

    def zone_scale(self, pt):
        for z in self.zones:
            if not z.get("poly") or _in_poly(pt, z["poly"]):
                return z
        return self.zones[-1]

    def px(self, F, pt):
        """Vecteur force (unité de force) → vecteur en pixels du DR, selon la zone de pt."""
        z = self.zone_scale(pt)
        k = self.px_cm / z["scale"]
        return (F[0] * k, F[1] * k)

    # ---- correction
    def droite(self, p, u, color="CORR", w=2.6):
        a, b = _clip(p, _unit(u), self.W, self.H)
        f = self.f
        self.corr.append(f"line(c, {a[0]:.1f}, {a[1]:.1f}, {b[0]:.1f}, {b[1]:.1f}, {color}, {w * f:.1f}, [{14 * f:.0f}, {7 * f:.0f}]);")

    def trait(self, p, u, t0, t1, color="CORR", w=1.8):
        """Trait de construction (parallèle du dynamique) limité au voisinage du triangle."""
        u = _unit(u)
        a, b = (p[0] + t0 * u[0], p[1] + t0 * u[1]), (p[0] + t1 * u[0], p[1] + t1 * u[1])
        f = self.f
        self.corr.append(f"line(c, {a[0]:.1f}, {a[1]:.1f}, {b[0]:.1f}, {b[1]:.1f}, {color}, {w * f:.1f}, [{8 * f:.0f}, {6 * f:.0f}]);")

    def point(self, p, nom, color="CORR", dx=12, dy=-14):
        f = self.f
        self.corr.append(f"dot(c, {p[0]:.1f}, {p[1]:.1f}, {6 * f:.1f}, {color}); "
                         f"text(c, {json.dumps(nom)}, {p[0] + dx * f:.1f}, {p[1] + dy * f:.1f}, {color}, {24 * f:.0f}, 'left', '800');")

    def vecteur(self, a, b, nom, color, side=1, size=20):
        ux, uy = _unit((b[0] - a[0], b[1] - a[1]))
        f = self.f
        ox, oy = side * (-uy), side * ux          # normale au vecteur, du côté choisi
        tw = len(nom) * 0.56 * size * f           # largeur approchée de l'étiquette
        d = 14 * f + 0.5 * tw * abs(ox) + 0.6 * size * f * abs(oy)
        mx, my = (a[0] + b[0]) / 2 + ox * d, (a[1] + b[1]) / 2 + oy * d
        self.corr.append(f"arrow(c, {a[0]:.1f}, {a[1]:.1f}, {b[0]:.1f}, {b[1]:.1f}, {color}, {3.6 * f:.1f}, {18 * f:.0f}); "
                         f"text(c, {json.dumps(nom)}, {mx:.1f}, {my:.1f}, {color}, {size * f:.0f}, 'center', '800');")

    def texte(self, s, x, y, color="CORR", size=20, align="left"):
        self.corr.append(f"text(c, {json.dumps(s)}, {x:.1f}, {y:.1f}, {color}, {size * self.f:.0f}, '{align}', '800');")

    def construire(self, res, depart, ordre, couleurs, unite, dirs=None, sides=None, connu_trace=True,
                   noms=("", "", ""), quoi="", nom_i="I", t=None):
        """Correction d'un solide soumis à trois forces, en étapes : droites d'action, point de concours, troisième
        droite, force connue à l'échelle, parallèles, vecteurs lus. ordre : indices des forces dans res['forces']
        dans l'ordre du dynamique. noms : points d'application (texte des consignes) ; t : consignes remplaçant
        celles par défaut (clés k1, k2, I, k3, dyn, par, fin)."""
        t = t or {}
        forces = res["forces"]
        dirs = dirs or [True, True, True]
        (n1, p1, F1), (n2, p2, F2), (n3, p3, F3) = [forces[i] for i in ordre]
        u_of = [F1, F2, res["u3"]]
        q1, q2, q3 = (noms[i] if noms[i] else "son point d'application" for i in ordre)
        z = self.zone_scale(depart)
        N1, N2, N3 = (math.hypot(*F) for F in (F1, F2, F3))
        tq = (quoi + " : ") if quoi else ""

        def droite_i(i):
            n, p, F = forces[i]
            self.droite(p, F if i != 2 else res["u3"])

        self.etape(f"{tq}droite d'action de {n1}", t.get("k1") or
                   f"{n1} est connue : trace sa droite d'action, {direction_txt(F1)}, passant par {q1}.")
        if dirs[ordre[0]]:
            droite_i(ordre[0])
        self.etape(f"{tq}droite d'action de {n2}", t.get("k2") or
                   f"Trace la droite d'action de {n2} : elle passe par {q2} et elle est {direction_txt(F2)}.")
        if dirs[ordre[1]]:
            droite_i(ordre[1])
        self.etape(f"{tq}point de concours {nom_i}", t.get("I") or
                   f"Prolonge ces deux droites jusqu'à leur intersection et marque le point {nom_i} (outil Point) : "
                   "les trois droites d'action d'un solide soumis à trois forces sont concourantes.")
        self.point(res["I"], nom_i)
        self.etape(f"{tq}droite d'action de {n3}", t.get("k3") or
                   f"Trace la droite d'action de {n3} : elle passe par {q3} et par {nom_i}. Sa direction est maintenant "
                   f"connue ({direction_txt(res['u3'])}).")
        if dirs[ordre[2]]:
            droite_i(ordre[2])
        v1 = self.px(F1, depart)
        a, b = depart, (depart[0] + v1[0], depart[1] + v1[1])
        self.etape(f"{tq}{n1} à l'échelle", t.get("dyn") or
                   f"Dans la zone du dynamique (1 cm ↔ {fr(z['scale'])} {unite}), trace {n1} : {fr(N1 / z['scale'], 1)} cm "
                   f"pour {fr(N1)} {unite}, {sens_txt(F1)}. Astuce : saisis {fr(N1)} dans « Intensité imposée », puis "
                   "trace le vecteur avec l'outil Vecteur.")
        if connu_trace:
            self.vecteur(a, b, f"{n1} = {fr(N1)} {unite}", couleurs[0], (sides or [1, 1, 1])[0])
        v2, v3 = self.px(F2, depart), self.px(F3, depart)
        c = (b[0] + v2[0], b[1] + v2[1])
        L2, L3 = math.hypot(*v2), math.hypot(*v3)
        self.etape(f"{tq}parallèles", t.get("par") or
                   f"Avec l'outil Parallèle : par la pointe de {n1}, trace la parallèle à la droite d'action de {n2} ; par "
                   f"son origine, la parallèle à celle de {n3}. Elles se coupent au troisième sommet du triangle.")
        self.trait(b, v2, -0.25 * L2, 1.25 * L2, couleurs[1])
        self.trait(a, (-v3[0], -v3[1]), -0.25 * L3, 1.25 * L3, couleurs[2])
        self.etape(f"{tq}{n2} et {n3}", t.get("fin") or
                   f"Trace {n2} puis {n3} sur les côtés du triangle, bout à bout : chaque flèche part de la pointe de la "
                   f"précédente et le triangle se referme. Mesure-les et convertis avec l'échelle : {n2} ≈ {fr(N2)} {unite}, "
                   f"{n3} ≈ {fr(N3)} {unite}.")
        self.vecteur(b, c, f"{n2} ≈ {fr(N2)} {unite}", couleurs[1], (sides or [1, 1, 1])[1])
        self.vecteur(c, a, f"{n3} ≈ {fr(N3)} {unite}", couleurs[2], (sides or [1, 1, 1])[2])

    def decor_js(self, extra_decorate=""):
        bars = []
        for z in self.zones:
            x, y = z["bar"]
            L, f = self.px_cm, self.f
            bars.append(f"line(c, {x}, {y}, {x + L:.1f}, {y}, '#1C2530', {3 * f:.1f}); "
                        f"line(c, {x}, {y - 9 * f:.0f}, {x}, {y + 9 * f:.0f}, '#1C2530', {3 * f:.1f}); "
                        f"line(c, {x + L:.1f}, {y - 9 * f:.0f}, {x + L:.1f}, {y + 9 * f:.0f}, '#1C2530', {3 * f:.1f}); "
                        f"text(c, {json.dumps('1 cm ↔ ' + fr(z['scale']) + ' ' + z['unit'])}, {x}, {y - 24 * f:.0f}, '#1C2530', {20 * f:.0f}, 'left', '800');")
        graph = {"alpha": self.alpha, "pxPerCm": self.px_cm,
                 "zones": [{"unit": z["unit"], "scale": z["scale"], **({"poly": z["poly"]} if z.get("poly") else {})}
                           for z in self.zones],
                 "points": {k: [round(v[0], 1), round(v[1], 1)] for k, v in self.points.items()},
                 "refs": [[round(c, 1) for c in r] for r in self.refs]}
        steps = ",\n        ".join(
            f"{{ t: {json.dumps(st['t'], ensure_ascii=False)}, d: {json.dumps(st['d'], ensure_ascii=False)}, "
            f"f: function (c) {{ {' '.join(st['js'])} }} }}" for st in self.steps)
        return (f"    {self.name}: {{\n      pad: {{ t: 0, r: 0, b: 0, l: 0 }}, rs: {self.rs},\n"
                f"      graph: {json.dumps(graph, ensure_ascii=False)},\n"
                f"      decorate: function (c) {{ {' '.join(bars)} {extra_decorate} }},\n"
                f"      steps: [\n        {steps}\n      ],\n"
                f"      correction: function (c) {{ this.steps.forEach(function (s) {{ s.f(c); }}); }}\n    }}")


def _in_poly(p, poly):
    x, y = p
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


AIDE = """<details class="gt-aide"><summary>Mode d'emploi de l'atelier de tracé</summary><dl>
<dt>Vecteur</dt><dd>appuie sur l'origine, glisse jusqu'à l'extrémité. La longueur (cm du document) et l'intensité à l'échelle
s'affichent en direct. Pour tracer une force connue, saisis d'abord son intensité dans « Intensité imposée ».</dd>
<dt>Droite d'action</dt><dd>deux points suffisent : la droite est prolongée sur toute la feuille.</dd>
<dt>Parallèle</dt><dd>clique la droite ou le vecteur de référence (surligné en jaune), puis appuie là où doit passer la
parallèle. Pour changer de référence, clique simplement sur une autre droite ou un autre vecteur. C'est l'outil du dynamique :
il remplace l'équerre et la règle.</dd>
<dt>Point, Texte</dt><dd>marque le point de concours I, nomme tes vecteurs.</dd>
<dt>Sélection</dt><dd>clique un tracé déjà posé : il s'entoure de jaune. Une couleur ou une épaisseur le modifie ;
« Supprimer » (ou la touche Suppr) l'efface.</dd>
<dt>Mesurer</dt><dd>donne une distance et l'intensité correspondante, sans rien tracer.</dd>
<dt>Aimant</dt><dd>accroche le pointeur aux points du DR, aux extrémités des tracés et aux intersections des droites
(cercle bleu ou orange). Désactive-le pour un placement libre.</dd>
<dt>DR</dt><dd>règle la transparence du document sous tes tracés. Le zoom et le plein écran (le DR y tient en entier)
aident à viser.</dd>
<dt>Correction</dt><dd>après validation, « Voir pas à pas » rejoue la construction étape par étape, avec la consigne de
chaque action.</dd>
</dl></details>"""
