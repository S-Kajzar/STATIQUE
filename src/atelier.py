#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atelier de statique graphique : environnement de tracé sur document réponse (DR).

Greffé sur le moteur de tracé du gabarit (classe Sketch, exposée par window.__app__.sketches) sans le modifier :
un script chargé après le moteur remplace, pour les seuls tracés dont le décor porte une entrée « graph », les
méthodes de saisie et de dessin. Les autres tracés gardent le comportement du gabarit.

Outils : Vecteur (longueur et intensité à l'échelle affichées, intensité imposée), Droite d'action (droite
prolongée sur toute la feuille), Parallèle (à une droite ou à un vecteur choisi), Segment, Point, Mesurer
(distance en cm du document, intensité correspondante, angle avec l'horizontale), Texte, Gomme, Crayon.
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
              ("erase", "Gomme", "Effacer un tracé")]
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
  ["down", "move", "up", "paint", "draw", "eraseAt", "setTool"].forEach(function (k) { base[k] = P[k]; });
  var NEW = { vec: 1, dir: 1, par: 1, pt: 1, mes: 1, line: 1 };
  var HINTS = {
    vec: "<b>Vecteur</b> : appuie sur l'origine, glisse jusqu'à l'extrémité ; la longueur et l'intensité à l'échelle s'affichent. Pour un vecteur connu, saisis d'abord son intensité dans « Intensité imposée ».",
    dir: "<b>Droite d'action</b> : appuie sur un point de la droite et glisse vers un second point ; la droite est prolongée sur toute la feuille.",
    par: "<b>Parallèle</b> : clique d'abord sur la droite ou le vecteur de référence, puis appuie là où doit passer la parallèle (glisse pour ajuster). Reclique sur « Parallèle » pour changer de référence.",
    line: "<b>Segment</b> : trait droit entre deux points.",
    pt: "<b>Point</b> : clique pour marquer un point (point de concours I…), puis nomme-le avec l'outil Texte.",
    mes: "<b>Mesurer</b> : glisse d'un point à l'autre ; la distance en cm du document, l'intensité correspondante et l'angle s'affichent.",
    text: "<b>Texte</b> : clique à l'endroit voulu, tape le nom, valide avec Entrée.",
    erase: "<b>Gomme</b> : passe sur un tracé pour l'effacer.",
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

  // ---------- surcharges
  P.setTool = function (t) {
    base.setTool.call(this, t);
    if (!this.gt) return;
    this.gt.ref = null; this.gt.meas = null; this.gt.hover = null;
    status(this, HINTS[t] || "");
    this.draw();
  };
  P.down = function (e) {
    if (!this.gt) return base.down.call(this, e);
    this.gt.meas = null;
    if (!NEW[this.tool]) return base.down.call(this, e);
    if (this.locked || e.button > 0) return;
    e.preventDefault();
    var p = this.pos(e), w = Math.max(0.6, 2.6 * this.wFactor * p.k), q = snap(this, p);
    this.gt.k = p.k;
    if (this.tool === "pt") { this.strokes.push({ t: "pt", x: q.x, y: q.y, c: this.color, w: w }); this.draw(); return; }
    if (this.tool === "par" && !this.gt.ref) {
      var L = pickLine(this, p);
      if (L) { this.gt.ref = L; status(this, "<b>Référence choisie.</b> Appuie maintenant à l'endroit où doit passer la parallèle (une extrémité de vecteur par exemple), puis glisse pour ajuster."); }
      else status(this, "<b>Parallèle</b> : clique d'abord sur une droite ou sur un vecteur de référence.");
      this.draw(); return;
    }
    this.canvas.setPointerCapture(e.pointerId);
    if (this.tool === "par") this.cur = { t: "par", a: [q.x, q.y], u: this.gt.ref.u.slice(), c: this.color, w: w * 0.8 };
    else this.cur = { t: this.tool, a: [q.x, q.y], b: [q.x, q.y], c: this.color, w: this.tool === "dir" ? w * 0.8 : w };
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
    if (st.t === "par" || dist(st.a, st.b) > 3) this.strokes.push(st);
    if (st.t === "vec" && this.gt.val > 0) { this.gt.val = 0; var vi = this.root.querySelector(".gt-val"); if (vi) vi.value = ""; }
    this.draw();
  };
  P.eraseAt = function (p) {
    if (!this.gt) return base.eraseAt.call(this, p);
    var r = Math.max(6, 11 * p.k), self = this, before = this.strokes.length, q = [p.x, p.y], ctx = this.ctx;
    this.strokes = this.strokes.filter(function (st) {
      var w = (st.w || 2) / 2;
      if (st.t === "pen") { for (var i = 1; i < st.pts.length; i++) if (segDist(q, st.pts[i - 1], st.pts[i]) <= r + w) return false; return true; }
      if (st.t === "line" || st.t === "arrow" || st.t === "vec") return segDist(q, st.a, st.b) > r + w;
      if (st.t === "dir" || st.t === "par") { var L = lineOf(st); return lineDist(q, L.p, L.u) > r + w; }
      if (st.t === "pt") return Math.hypot(p.x - st.x, p.y - st.y) > r + st.w * 3;
      if (st.t === "text") {
        ctx.save(); ctx.font = "700 " + st.size + "px system-ui, Segoe UI, Arial, sans-serif";
        var tw = ctx.measureText(st.s).width; ctx.restore();
        return !(p.x >= st.x - r && p.x <= st.x + tw + r && p.y >= st.y - st.size / 2 - r && p.y <= st.y + st.size / 2 + r);
      }
      return true;
    });
    if (this.strokes.length !== before) this.draw();
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
      var list = this.cur ? this.strokes.concat([this.cur]) : this.strokes;
      list.forEach(function (st) { if (st.t !== "mes") drawStroke(self, ctx, st); });
    }
    if (opts.corr && this.dec.correction) { ctx.save(); ctx.translate(p.l, p.t); this.dec.correction(ctx); ctx.restore(); }
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
    s.gt = { alpha: g.alpha || 0.45, snap: true, ref: null, hover: null, meas: null, val: 0, k: 1, raf: 0 };
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
  window.__atelier__ = { snapCands: snapCands, lenInfo: lenInfo };
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


class DR:
    """Un document réponse : fond, points, droites données, zones d'échelle, constructions corrigées."""

    def __init__(self, name, img, size, px_cm, zones, points, refs=(), alpha=0.45, rs=1.2):
        self.name, self.img, (self.W, self.H), self.px_cm = name, img, size, px_cm
        self.zones, self.points, self.refs, self.alpha, self.rs = zones, points, list(refs), alpha, rs
        self.corr = []      # instructions JS de la correction
        self.f = max(1.0, self.W / 900)   # taille des traits et des textes, proportionnée au fond

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

    def construire(self, res, depart, ordre, couleurs, unite, dirs=None, sides=None, connu_trace=True):
        """Correction d'un solide soumis à trois forces : droites d'action, point I, dynamique à partir de depart.
        ordre : indices des forces dans res['forces'] dans l'ordre du dynamique."""
        forces = res["forces"]
        for i, (n, p, F) in enumerate(forces):
            if dirs is None or dirs[i]:
                self.droite(p, F if i != 2 else res["u3"])
        self.point(res["I"], "I")
        pt = depart
        for j, i in enumerate(ordre):
            n, p, F = forces[i]
            if j == 0 and not connu_trace:
                pt = (pt[0] + self.px(F, depart)[0], pt[1] + self.px(F, depart)[1])
                continue
            v = self.px(F, depart)
            q = (pt[0] + v[0], pt[1] + v[1])
            self.vecteur(pt, q, f"{n} ≈ {fr(math.hypot(*F))} {unite}", couleurs[j], (sides or [1, 1, 1])[j])
            pt = q

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
        return (f"    {self.name}: {{\n      pad: {{ t: 0, r: 0, b: 0, l: 0 }}, rs: {self.rs},\n"
                f"      graph: {json.dumps(graph, ensure_ascii=False)},\n"
                f"      decorate: function (c) {{ {' '.join(bars)} {extra_decorate} }},\n"
                f"      correction: function (c) {{\n        " + "\n        ".join(self.corr) + "\n      }\n    }")


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
<dt>Parallèle</dt><dd>clique la droite ou le vecteur de référence, puis appuie là où doit passer la parallèle. C'est l'outil
du dynamique : il remplace l'équerre et la règle.</dd>
<dt>Point, Texte</dt><dd>marque le point de concours I, nomme tes vecteurs.</dd>
<dt>Mesurer</dt><dd>donne une distance et l'intensité correspondante, sans rien tracer.</dd>
<dt>Aimant</dt><dd>accroche le pointeur aux points du DR, aux extrémités des tracés et aux intersections des droites
(cercle bleu ou orange). Désactive-le pour un placement libre.</dd>
<dt>DR</dt><dd>règle la transparence du document sous tes tracés. Le zoom et le plein écran aident à viser.</dd>
</dl></details>"""
