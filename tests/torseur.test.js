// Tests navigateur de l'exercice 3.4 « Déplacer un torseur » (tirages aléatoires, ?seed=… pour les rendre reproductibles).
//   python3 src/generer.py && NODE_PATH=$(npm root -g) node --test tests/torseur.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium } = require("playwright");

const ROOT = path.join(__dirname, "..");
const url = (f) => "file://" + path.join(ROOT, f);
let browser;
test.before(async () => { browser = await chromium.launch(); });
test.after(async () => { await browser.close(); });

async function open(q, viewport) {
  const context = await browser.newContext({ viewport: viewport || { width: 1366, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(url("deplacer-torseur.html") + (q || ""));
  return { context, page, errors };
}
const tirage = (page) => page.evaluate(() => window.__ta__.courant());
const fr = (x) => String(Math.round(x * 1000) / 1000).replace(".", ",");

// réponses recalculées ici, indépendamment de la page : BA = A − B ; M_B = M_A + BA ∧ R
function attendu(t) {
  const a = t.A.map((v, i) => v - t.B[i]), R = t.R;
  const c = [a[1] * R[2] - a[2] * R[1], a[2] * R[0] - a[0] * R[2], a[0] * R[1] - a[1] * R[0]];
  return { BA: a, R, MB: t.MA.map((m, i) => m + c[i]) };
}
// valeurs dans l'ordre des cases : BA, puis le torseur ligne par ligne
function cases(t) {
  const e = attendu(t);
  if (t.niv < 3) return [e.BA[0], e.BA[1], e.R[0], e.R[1], e.MB[2]];
  return [e.BA[0], e.BA[1], e.BA[2], e.R[0], e.MB[0], e.R[1], e.MB[1], e.R[2], e.MB[2]];
}
async function remplir(page, vals) {
  const inputs = page.locator("#ta .ta-f input");
  assert.equal(await inputs.count(), vals.length);
  for (let i = 0; i < vals.length; i++) await inputs.nth(i).fill(typeof vals[i] === "number" ? fr(vals[i]) : vals[i]);
  await page.click("#ta-check");
}

test("accueil : carte Exercice 3.4 Niveau 3 vers la page d'entraînement", async () => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(url("index.html"));
  const carte = page.locator(".mode-card", { hasText: "Déplacer un torseur" });
  assert.equal(await carte.count(), 1);
  assert.match(await carte.locator(".mc-tag").innerText(), /Exercice 3\.4\s*Niveau 3/);
  assert.equal(await carte.locator("a").getAttribute("href"), "deplacer-torseur.html");
  await context.close();
});

for (const niv of [1, 2, 3]) {
  test(`niveau ${niv} : réponses justes, figure, correction pas à pas, score`, async () => {
    const { context, page, errors } = await open("?seed=" + (11 * niv));
    await page.click(`[data-niv="${niv}"]`);
    const t = await tirage(page);
    assert.equal(t.niv, niv);
    if (niv === 1) assert.deepEqual(t.MA, [0, 0, 0]);
    if (niv === 2) assert.ok(t.MA[2] !== 0 && t.MA[0] === 0 && t.MA[1] === 0);
    if (niv < 3) assert.ok(t.A[2] === 0 && t.B[2] === 0 && t.R[2] === 0);
    assert.equal(await page.isVisible("#ta-svg"), niv < 3);
    await remplir(page, cases(t));
    assert.match(await page.innerText("#ta-fb"), /Tout est juste/);
    assert.equal(await page.locator("#ta .ta-f.ok").count(), niv < 3 ? 5 : 9);
    assert.ok(await page.isVisible("#ta-corr"));
    const e = attendu(t);
    const corr = await page.innerText("#ta-corr");
    assert.ok(corr.includes(fr(e.MB[2]).replace("-", "−")), "moment N_B dans la correction");
    assert.match(corr, /BA/);
    assert.equal(await page.innerText("#ta-ok"), "1");
    assert.equal(await page.innerText("#ta-serie"), "1");
    assert.deepEqual(errors, []);
    await context.close();
  });
}

test("erreurs : signe de BA inversé (BA ↔ AB) noté faux case par case, tirage compté manqué", async () => {
  const { context, page } = await open("?seed=5");
  await page.click('[data-niv="2"]');
  const t = await tirage(page);
  const v = cases(t);
  const faux = v.slice();
  faux[0] = -v[0] || 9; faux[1] = -v[1] || 9;                          // vecteur AB au lieu de BA
  const e = attendu(t);
  faux[4] = 2 * t.MA[2] - e.MB[2];                                      // N_A − BA ∧ R : erreur de signe classique
  if (Math.abs(faux[4] - v[4]) < 0.2) faux[4] = v[4] + 50;
  await remplir(page, faux);
  assert.match(await page.innerText("#ta-fb"), /3 cases à revoir/);
  assert.equal(await page.locator("#ta .ta-f.ko").count(), 3);
  assert.ok(!(await page.isVisible("#ta-corr")));
  await remplir(page, v);                                               // corrigé au deuxième essai : pas compté réussi
  assert.match(await page.innerText("#ta-fb"), /Tout est juste/);
  assert.equal(await page.innerText("#ta-ok"), "0");
  assert.equal(await page.innerText("#ta-tot"), "1");
  // saisies acceptées : virgule, point, signe moins typographique, espaces
  await page.click("#ta-new");
  const t2 = await tirage(page);
  const v2 = cases(t2).map((x, i) => (i % 2 ? String(x) : fr(x).replace("-", "−") + " "));
  await remplir(page, v2);
  assert.match(await page.innerText("#ta-fb"), /Tout est juste/);
  assert.equal(await page.innerText("#ta-ok"), "1");
  // « Voir la correction » sans répondre : tirage compté manqué, série remise à zéro
  await page.click("#ta-new");
  await page.click("#ta-sol");
  assert.ok(await page.isVisible("#ta-corr"));
  assert.equal(await page.innerText("#ta-tot"), "3");
  assert.equal(await page.innerText("#ta-serie"), "0");
  await context.close();
});

test("série de 10 tirages justes = 20 / 20", async () => {
  const { context, page, errors } = await open("?seed=99");
  await page.click('[data-niv="3"]');
  for (let i = 0; i < 10; i++) {
    await remplir(page, cases(await tirage(page)));
    assert.match(await page.innerText("#ta-fb"), /Tout est juste/, `tirage ${i + 1}`);
    if (i < 9) { assert.ok(!(await page.isVisible("#ta-fin"))); await page.click("#ta-new"); }
  }
  assert.match(await page.innerText("#ta-fin"), /20 \/ 20 ★★★/);
  assert.equal(await page.innerText("#ta-dix"), "10 / 10");
  assert.deepEqual(errors, []);
  await context.close();
});

test("tirages : reproductibles avec ?seed, variés, cohérents sur 300 tirages", async () => {
  const a = await open("?seed=42"), b = await open("?seed=42"), c = await open("?seed=43");
  assert.deepEqual(await tirage(a.page), await tirage(b.page));
  assert.notDeepEqual(await tirage(a.page), await tirage(c.page));
  const res = await a.page.evaluate(() => {
    const out = [];
    for (const n of [1, 2, 3]) {
      document.querySelector(`[data-niv="${n}"]`).click();
      for (let i = 0; i < 100; i++) { out.push(window.__ta__.courant()); document.querySelector("#ta-new").click(); }
    }
    return out;
  });
  const vus = new Set(res.map((t) => JSON.stringify([t.A, t.B, t.R, t.MA])));
  assert.ok(vus.size > 290, "tirages variés");
  for (const t of res) {
    const e = attendu(t);
    assert.ok(Math.hypot(...e.BA) >= 0.25 - 1e-9, "A et B distincts");
    assert.ok(Math.abs(t.R[0]) + Math.abs(t.R[1]) >= 50, "résultante non négligeable dans le plan");
    for (let i = 0; i < 3; i++) {
      assert.ok(Math.abs(t.BA[i] - e.BA[i]) < 1e-9 && Math.abs(t.MB[i] - e.MB[i]) < 1e-6, "calcul de la page");
      assert.ok(Math.abs(t.A[i] * 10 - Math.round(t.A[i] * 10)) < 1e-9, "coordonnées au décimètre");
    }
  }
  assert.ok(res.slice(0, 100).some((t) => attendu(t).MB[2] !== 0), "N_B non nul au niveau 1");
  for (const x of [a, b, c]) { assert.deepEqual(x.errors, []); await x.context.close(); }
});

test("figure du niveau 2 : l'arc du moment N_A tourne dans le sens de son signe (trigonométrique si positif)", async () => {
  const { context, page, errors } = await open("?seed=1");
  await page.click('[data-niv="2"]');
  for (let i = 0; i < 12; i++) {
    const [n, sens] = await page.evaluate(() => {
      const t = window.__ta__.courant(), path = document.querySelector("#ta-svg path[fill=none]"), c = document.querySelector("#ta-svg circle");
      const L = path.getTotalLength(), cx = +c.getAttribute("cx"), cy = +c.getAttribute("cy");
      let s = 0, pr = path.getPointAtLength(0);   // aire balayée, repère écran (y vers le bas)
      for (let k = 1; k <= 40; k++) { const q = path.getPointAtLength(L * k / 40); s += (pr.x - cx) * (q.y - cy) - (q.x - cx) * (pr.y - cy); pr = q; }
      return [t.MA[2], s < 0 ? "trigo" : "horaire"];
    });
    assert.equal(sens, n > 0 ? "trigo" : "horaire", `N_A = ${n}`);
    await page.click("#ta-new");
  }
  assert.deepEqual(errors, []);
  await context.close();
});

test("téléphone : aucun débordement horizontal, niveaux 1 à 3", async () => {
  const { context, page, errors } = await open("?seed=3", { width: 390, height: 844 });
  for (const n of [1, 2, 3]) {
    await page.click(`[data-niv="${n}"]`);
    await page.click("#ta-sol");
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `niveau ${n}`);
  }
  assert.deepEqual(errors, []);
  await context.close();
});
