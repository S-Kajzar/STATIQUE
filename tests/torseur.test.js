// Tests navigateur de l'exercice 2.1 « Déplacer un torseur » : séries de questions aléatoires (?seed=… pour les rendre
// reproductibles), types au choix, note sur 20, mise en page plein écran.
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
const serie = (page) => page.evaluate(() => window.__ta__.serie());
const fr = (x) => String(Math.round(x * 1000) / 1000).replace(".", ",");

// réponses recalculées ici, indépendamment de la page : BA = A − B ; M_B = M_A + BA ∧ R
function attendu(t) {
  const a = t.A.map((v, i) => v - t.B[i]), R = t.R;
  const c = [a[1] * R[2] - a[2] * R[1], a[2] * R[0] - a[0] * R[2], a[0] * R[1] - a[1] * R[0]];
  return { BA: a, R, MB: t.MA.map((m, i) => m + c[i]) };
}
// valeurs dans l'ordre des cases : BA (colonne), puis le torseur ligne par ligne
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
// règle la série dans le menu « Série » puis la lance
async function lancer(page, types, N) {
  await page.click("#ta-cfg summary");
  for (const v of [1, 2, 3]) {
    const cb = page.locator(`[name=ta-type][value="${v}"]`);
    if ((await cb.isChecked()) !== types.includes(v)) await page.locator(`[name=ta-type][value="${v}"] + span`).click();
  }
  await page.locator(`[name=ta-n][value="${N}"] + span`).click();
  await page.click("#ta-go");
}

test("accueil : carte Exercice 2.1 Niveau 2 vers la page d'entraînement", async () => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto(url("index.html"));
  const carte = page.locator(".mode-card", { hasText: "Déplacer un torseur" });
  assert.equal(await carte.count(), 1);
  assert.match(await carte.locator(".mc-tag").innerText(), /Exercice 2\.1\s*Niveau 2/);
  assert.equal(await carte.locator("a").getAttribute("href"), "deplacer-torseur.html");
  await context.close();
});

test("série par défaut : 10 questions mélangeant les trois types, conseil « brouillon », vecteur BA en colonne", async () => {
  const { context, page, errors } = await open("?seed=4");
  const s = await serie(page);
  assert.equal(s.N, 10);
  assert.deepEqual([1, 2, 3].map((t) => s.liste.filter((x) => x === t).length).sort(), [3, 3, 4]);
  assert.equal(await page.innerText("#ta-k"), "1");
  assert.equal(await page.innerText("#ta-N"), "10");
  assert.equal(await page.locator("#ta-dots i").count(), 10);
  assert.match(await page.innerText(".ta-conseil"), /Conseil : utilise un brouillon/);
  assert.equal(await page.locator("#ta-ba .vcol-b .ta-f").count(), (await tirage(page)).niv === 3 ? 3 : 2);
  assert.match(await page.innerText("#ta-cfg summary"), /10 questions · glisseur, plan, 3D/);
  assert.deepEqual(errors, []);
  await context.close();
});

for (const [type, nom, nb] of [[1, "Glisseur plan", 5], [2, "Torseur plan", 5], [3, "Torseur 3D", 5]]) {
  test(`série de ${nb} « ${nom} » seule : réponses justes, figure, correction en colonnes, 20 / 20`, async () => {
    const { context, page, errors } = await open("?seed=" + (11 * type));
    await lancer(page, [type], nb);
    assert.match(await page.innerText("#ta-cfg summary"), new RegExp(`${nb} questions`));
    for (let i = 0; i < nb; i++) {
      const t = await tirage(page);
      assert.equal(t.niv, type);
      assert.equal(await page.innerText("#ta-type"), nom);
      if (type === 1) assert.deepEqual(t.MA, [0, 0, 0]);
      if (type === 2) assert.ok(t.MA[2] !== 0 && t.MA[0] === 0 && t.MA[1] === 0);
      if (type < 3) assert.ok(t.A[2] === 0 && t.B[2] === 0 && t.R[2] === 0);
      assert.ok(await page.isVisible("#ta-svg"), "figure (perspective en 3D)");
      assert.ok(await page.locator("#ta-next").isDisabled(), "pas de question suivante avant d'avoir répondu");
      await remplir(page, cases(t));
      assert.match(await page.innerText("#ta-fb"), /Tout est juste/);
      assert.ok(await page.isVisible("#ta-corr"));
      assert.ok(await page.locator("#ta-corr .vcol-b").count() >= 3, "vecteurs de la correction en colonne");
      const corr = await page.innerText("#ta-corr");
      assert.ok(corr.includes(fr(attendu(t).MB[2]).replace("-", "−")), "moment N_B dans la correction");
      assert.equal(await page.innerText("#ta-ok"), String(i + 1));
      await page.click("#ta-next");
    }
    assert.ok(await page.isVisible("#ta-bilan") && !(await page.isVisible("#ta-grid")));
    assert.match(await page.innerText("#ta-note"), /^20 \/ 20 ★★★$/);
    assert.equal(await page.locator(".ta-bil-l li.ok").count(), nb);
    // nouvelle série avec les mêmes réglages
    await page.click("#ta-encore");
    assert.ok(await page.isVisible("#ta-grid"));
    assert.equal(await page.innerText("#ta-k"), "1");
    assert.deepEqual((await serie(page)).liste, Array(nb).fill(type));
    assert.deepEqual(errors, []);
    await context.close();
  });
}

test("réglages : 20 questions plan + 3D réparties à parts égales ; au moins un type exigé", async () => {
  const { context, page, errors } = await open("?seed=6");
  await lancer(page, [2, 3], 20);
  const s = await serie(page);
  assert.equal(s.liste.length, 20);
  assert.equal(s.liste.filter((x) => x === 2).length, 10);
  assert.equal(s.liste.filter((x) => x === 3).length, 10);
  assert.notDeepEqual(s.liste, [2, 3].concat(...Array(9).fill([2, 3])), "ordre tiré au hasard");
  assert.equal(await page.locator("#ta-dots i").count(), 20);
  await page.click("#ta-cfg summary");
  for (const v of [2, 3]) await page.locator(`[name=ta-type][value="${v}"] + span`).click();
  assert.match(await page.innerText("#ta-cfg-msg"), /au moins un type/);
  assert.ok(await page.locator("#ta-go").isDisabled());
  await page.locator(`[name=ta-type][value="1"] + span`).click();
  await page.locator(`[name=ta-n][value="15"] + span`).click();
  await page.click("#ta-go");
  assert.deepEqual((await serie(page)).liste, Array(15).fill(1));
  assert.ok(!(await page.locator("#ta-cfg").evaluate((d) => d.open)));
  assert.deepEqual(errors, []);
  await context.close();
});

test("erreurs : cases notées une à une, question manquée si fausse au premier essai ; note de fin de série", async () => {
  const { context, page, errors } = await open("?seed=5");
  await lancer(page, [2], 5);
  // Q1 : BA inversé (AB au lieu de BA) et N_B faux, puis corrigé : réussie au 2e essai = manquée
  const t = await tirage(page), v = cases(t), faux = v.slice();
  faux[0] = -v[0] || 9; faux[1] = -v[1] || 9;
  const e = attendu(t);
  faux[4] = 2 * t.MA[2] - e.MB[2];
  if (Math.abs(faux[4] - v[4]) < 0.2) faux[4] = v[4] + 50;
  await remplir(page, faux);
  assert.match(await page.innerText("#ta-fb"), /3 cases à revoir/);
  assert.equal(await page.locator("#ta .ta-f.ko").count(), 3);
  assert.ok(!(await page.isVisible("#ta-corr")));
  assert.ok(!(await page.locator("#ta-next").isDisabled()), "on peut passer à la suite après une vérification");
  await remplir(page, v);
  assert.match(await page.innerText("#ta-fb"), /Tout est juste/);
  assert.equal(await page.innerText("#ta-ok"), "0");
  assert.equal(await page.locator("#ta-dots i.ko").count(), 1);
  await page.click("#ta-next");
  // Q2 et Q3 justes (saisies avec virgule, point, signe − typographique, espaces)
  for (let i = 0; i < 2; i++) {
    const vv = cases(await tirage(page)).map((x, j) => (j % 2 ? String(x) : fr(x).replace("-", "−") + " "));
    await remplir(page, vv);
    assert.match(await page.innerText("#ta-fb"), /Tout est juste/);
    await page.click("#ta-next");
  }
  // Q4 : correction demandée sans répondre ; Q5 juste
  await page.click("#ta-sol");
  assert.ok(await page.isVisible("#ta-corr"));
  assert.equal(await page.locator("#ta .ta-att").count(), 5);
  await page.click("#ta-next");
  assert.equal(await page.innerText("#ta-next"), "Voir ma note ▶");
  await remplir(page, cases(await tirage(page)));
  await page.click("#ta-next");
  assert.match(await page.innerText("#ta-note"), /^12 \/ 20 ★☆☆$/);
  assert.match(await page.innerText("#ta-bilan"), /3 questions réussies du premier coup sur 5\. Torseur plan : 3 \/ 5/);
  assert.deepEqual(await page.locator(".ta-bil-l li").evaluateAll((l) => l.map((x) => x.className)), ["ko", "ok", "ok", "ko", "ok"]);
  await page.click("#ta-regl");
  assert.ok(await page.locator("#ta-cfg").evaluate((d) => d.open));
  assert.deepEqual(errors, []);
  await context.close();
});

test("tirages : reproductibles avec ?seed, variés, cohérents sur 100 questions", async () => {
  const a = await open("?seed=42"), b = await open("?seed=42"), c = await open("?seed=43");
  assert.deepEqual(await tirage(a.page), await tirage(b.page));
  assert.notDeepEqual(await tirage(a.page), await tirage(c.page));
  await lancer(a.page, [1, 2, 3], 20);
  const res = await a.page.evaluate(() => {
    const out = [];
    for (let k = 0; k < 5; k++) {
      for (let i = 0; i < 20; i++) {
        out.push(window.__ta__.courant());
        document.querySelector("#ta-sol").click(); document.querySelector("#ta-next").click();
      }
      document.querySelector("#ta-encore").click();
    }
    return out;
  });
  assert.equal(res.length, 100);
  const vus = new Set(res.map((t) => JSON.stringify([t.A, t.B, t.R, t.MA])));
  assert.ok(vus.size > 95, "tirages variés");
  for (const t of res) {
    const e = attendu(t);
    assert.ok(Math.hypot(...e.BA) >= 0.25 - 1e-9, "A et B distincts");
    assert.ok(Math.abs(t.R[0]) + Math.abs(t.R[1]) >= 50, "résultante non négligeable dans le plan");
    for (let i = 0; i < 3; i++) {
      assert.ok(Math.abs(t.BA[i] - e.BA[i]) < 1e-9 && Math.abs(t.MB[i] - e.MB[i]) < 1e-6, "calcul de la page");
      assert.ok(Math.abs(t.A[i] * 10 - Math.round(t.A[i] * 10)) < 1e-9, "coordonnées au décimètre");
    }
  }
  for (const x of [a, b, c]) { assert.deepEqual(x.errors, []); await x.context.close(); }
});

test("figure du torseur plan : l'arc du moment N_A tourne dans le sens de son signe (trigonométrique si positif)", async () => {
  const { context, page, errors } = await open("?seed=1");
  await lancer(page, [2], 15);
  for (let i = 0; i < 12; i++) {
    const [n, sens] = await page.evaluate(() => {
      const t = window.__ta__.courant(), path = document.querySelector("#ta-svg path[fill=none]"), c = document.querySelector("#ta-svg circle");
      const L = path.getTotalLength(), cx = +c.getAttribute("cx"), cy = +c.getAttribute("cy");
      let s = 0, pr = path.getPointAtLength(0);   // aire balayée, repère écran (y vers le bas)
      for (let k = 1; k <= 40; k++) { const q = path.getPointAtLength(L * k / 40); s += (pr.x - cx) * (q.y - cy) - (q.x - cx) * (pr.y - cy); pr = q; }
      return [t.MA[2], s < 0 ? "trigo" : "horaire"];
    });
    assert.equal(sens, n > 0 ? "trigo" : "horaire", `N_A = ${n}`);
    await page.click("#ta-sol"); await page.click("#ta-next");
  }
  assert.deepEqual(errors, []);
  await context.close();
});

for (const [w, h] of [[1920, 1080], [1366, 768], [1280, 720]]) {
  test(`plein écran ${w} × ${h} : données, saisie, boutons et correction visibles sans défiler, largeur occupée`, async () => {
    const { context, page, errors } = await open("?seed=21", { width: w, height: h });
    for (const n of [1, 2, 3]) {
      await lancer(page, [n], 5);
      await page.click("#ta-sol");
      const hors = await page.evaluate(() => {
        const sel = ["#ta-donnees", "#ta-svg", "#ta .ta-f", "#ta-check", "#ta-sol", "#ta-next", "#ta-fb", "#ta-corr", ".ta-prog", ".ta-conseil"];
        const out = [];
        for (const s of sel) for (const e of document.querySelectorAll(s)) {
          if (getComputedStyle(e).display === "none") continue;
          const r = e.getBoundingClientRect();
          if (r.bottom > innerHeight + 0.5 || r.top < 0 || r.right > innerWidth) out.push(`${s} ${Math.round(r.top)}→${Math.round(r.bottom)}`);
        }
        const g = document.querySelector("#ta-grid").getBoundingClientRect();
        if (g.width < innerWidth - 50) out.push(`grille étroite ${Math.round(g.width)}`);
        return [scrollY].concat(out);
      });
      assert.deepEqual(hors, [0], `type ${n}`);
    }
    assert.deepEqual(errors, []);
    await context.close();
  });
}

test("clavier : Entrée vérifie, puis passe à la question suivante ; valeurs attendues sous les cases ; menus", async () => {
  const { context, page, errors } = await open("?seed=8");
  await lancer(page, [2], 5);
  const first = page.locator("#ta .ta-f input").first();
  assert.ok(await first.evaluate((e) => e === document.activeElement), "curseur dans la première case");
  const t = await tirage(page);
  const v = cases(t);
  const inputs = page.locator("#ta .ta-f input");
  for (let i = 0; i < v.length; i++) await inputs.nth(i).fill(i === 4 ? "999" : fr(v[i]));
  await page.keyboard.press("Enter");
  assert.match(await page.innerText("#ta-fb"), /1 case à revoir/);
  assert.ok(await inputs.nth(4).evaluate((e) => e === document.activeElement), "curseur sur la case fausse");
  await inputs.nth(4).fill(fr(v[4]));
  await page.keyboard.press("Enter");
  assert.match(await page.innerText("#ta-fb"), /Tout est juste/);
  await page.keyboard.press("Enter");                                  // question suivante
  assert.equal(await page.innerText("#ta-k"), "2");
  assert.notDeepEqual(await tirage(page), t);
  assert.ok(await first.evaluate((e) => e === document.activeElement && e.value === ""));
  await page.click("#ta-sol");
  const att = await page.locator("#ta .ta-att").allInnerTexts();
  assert.deepEqual(att, cases(await tirage(page)).map((x) => "→ " + fr(x).replace("-", "−")));
  // un seul menu ouvert à la fois, refermé par un clic ailleurs
  await page.click(".ta-aide summary");
  assert.ok(await page.isVisible(".ta-aide .ta-pop"));
  await page.click("#ta-cfg summary");
  assert.ok(!(await page.isVisible(".ta-aide .ta-pop")) && await page.isVisible("#ta-cfg .ta-pop"));
  await page.mouse.click(5, 700);
  assert.ok(!(await page.isVisible("#ta-cfg .ta-pop")));
  assert.deepEqual(errors, []);
  await context.close();
});

test("tablette et téléphone : aucun débordement horizontal, types 1 à 3", async () => {
  for (const vp of [{ width: 820, height: 1180 }, { width: 390, height: 844 }]) {
    const { context, page, errors } = await open("?seed=3", vp);
    for (const n of [1, 2, 3]) {
      await lancer(page, [n], 5);
      await page.click("#ta-sol");
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${vp.width} px, type ${n}`);
    }
    assert.deepEqual(errors, []);
    await context.close();
  }
});
