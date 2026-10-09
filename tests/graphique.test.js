// Tests navigateur (Playwright + Chromium) de la statique graphique : cours 1.1, exercices 1.2 à 1.5, atelier de tracé.
//   python3 src/generer.py && NODE_PATH=$(npm root -g) node --test tests/graphique.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium } = require("playwright");
const REP = require("./reponses-graphique.js");

const ROOT = path.join(__dirname, "..");
const url = (f) => "file://" + path.join(ROOT, f);
const EXO = {
  "panneau-solaire.html": { parts: 2, sketches: ["sk_q2_1"], wrong: { q2_2: "230 N", q2_3: "380 N", q1_4: "(AD)" } },
  "pince-kobelco.html": { parts: 3, sketches: ["sk_q2_1", "sk_q3_1"], wrong: { q2_2: "2500 kN", q3_4: "2" } },
  "cric-hydraulique.html": { parts: 3, sketches: ["sk_q2_1"], wrong: { q3_3: "400 daN", q3_2: "60 daN" } },
  "suspension-vtt.html": { parts: 3, sketches: ["sk_q2_1"], wrong: { q3_3: "65 daN", q1_2: "(EF)" } },
};
let browser;
test.before(async () => { browser = await chromium.launch(); });
test.after(async () => { await browser.close(); });

async function open(file, viewport) {
  const context = await browser.newContext({ viewport: viewport || { width: 1366, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("dialog", (d) => d.accept());
  await page.goto(url(file));
  return { context, page, errors };
}
const text = (page, sel) => page.locator(sel).first().innerText();

test("accueil : cours 1.1 et section des exercices de statique graphique (Niveau 1)", async () => {
  const { context, page, errors } = await open("index.html");
  const cards = await page.locator(".mode-card").evaluateAll((cs) => cs.map((c) => [
    c.querySelector(".mc-tag").textContent.trim(), c.querySelector("h3").textContent,
    (c.querySelector("a") || { getAttribute: () => null }).getAttribute("href")]));
  for (const exp of [["Cours 1.1 Niveau 1", "Statique graphique", "cours-statique-graphique.html"],
    ["Exercice 1.2 Niveau 1", "Panneau solaire", "panneau-solaire.html"],
    ["Exercice 1.3 Niveau 1", "Pince de démolition", "pince-kobelco.html"],
    ["Exercice 1.4 Niveau 1", "Cric hydraulique roulant", "cric-hydraulique.html"],
    ["Exercice 1.5 Niveau 1", "Suspension arrière de VTT", "suspension-vtt.html"]])
    assert.ok(cards.some((c) => JSON.stringify(c) === JSON.stringify(exp)), exp.join(" | "));
  assert.equal(await page.locator(".graphique-grid .mode-card").count(), 4);
  assert.match(await page.locator("h2.home-choose").allInnerTexts().then((t) => t.join("|")), /Statique graphique/);
  assert.deepEqual(errors, []);
  await context.close();
});

test("cours 1.1 : isolement, cartes, bielle, levier pas à pas, dynamique interactif, quiz", async () => {
  const { context, page, errors } = await open("cours-statique-graphique.html");
  assert.match(await text(page, ".home-head"), /Cours 1\.1[\s\S]*Niveau 1[\s\S]*Statique graphique/);
  assert.equal(await page.locator(".cours-sec").count(), 8);
  // isolement juste : les trois premières actions seulement
  for (let i = 0; i < 3; i++) await page.locator(".iso-l input").nth(i).check();
  await page.click("#iso-ok");
  assert.match(await text(page, "#iso-fb"), /Bilan juste/);
  await page.click(".k3-carte >> nth=0");
  assert.match(await text(page, ".k3-carte >> nth=0"), /nulle/);
  // bielle
  await page.fill("#bi-a", "-40");
  assert.match(await page.getAttribute("#biel-g", "transform"), /rotate\(40\)/);
  // levier : aucune étape, puis toutes
  assert.equal(await page.locator(".lev-svg .lv.on").count(), 0);
  await page.click("#lv-next"); await page.click("#lv-next");
  assert.equal(await page.locator(".lev-svg .lv.on").count(), 2);
  await page.click("#lv-all");
  assert.equal(await page.locator(".lev-svg .lv.on").count(), 5);
  assert.match(await text(page, ".k1-tab"), /≈ 5\s000 N[\s\S]*≈ 7\s100 N/);
  // dynamique interactif : directions parallèles → impossible ; P vertical, F2 à 0°, F3 à 90° impossible aussi
  await page.fill("#tr-i2", "20"); await page.fill("#tr-i3", "20");
  assert.match(await text(page, "#tr-v"), /parallèles/);
  await page.fill("#tr-i2", "0"); await page.fill("#tr-i3", "135"); await page.fill("#tr-ip", "400");
  assert.match(await text(page, "#tr-r2"), /^400\sN$/);   // triangle rectangle isocèle
  assert.match(await text(page, "#tr-r3"), /^566\sN$/);
  // quiz tout juste
  const qz = page.locator(".quiz-q");
  for (let i = 0; i < await qz.count(); i++) {
    const ok = await qz.nth(i).getAttribute("data-ok");
    await qz.nth(i).locator(`input[value="${ok}"]`).check();
  }
  assert.equal((await text(page, "#qz-stars")).trim(), "★★★");
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  assert.deepEqual(errors, []);
  await context.close();
});

test("atelier : construction complète du panneau solaire avec l'aimant, l'intensité imposée et les parallèles", async () => {
  const { context, page, errors } = await open("panneau-solaire.html");
  await page.click("[data-mode=training]");
  const sk = "sk_q2_1", W = 1780, H = 1142;
  await page.locator("#" + sk).scrollIntoViewIfNeeded();
  // DR en transparence
  assert.equal(await page.evaluate(() => window.__app__.sketches.sk_q2_1.gt.alpha), 0.45);
  await page.fill(`#${sk} .gt-opa`, "70");
  assert.equal(await page.evaluate(() => window.__app__.sketches.sk_q2_1.gt.alpha), 0.7);
  async function xy(x, y) { const b = await page.locator(`#${sk} canvas`).boundingBox(); return [b.x + x * b.width / W, b.y + y * b.height / H]; }
  async function drag(tool, a, c) {
    if (tool) await page.click(`#${sk} [data-tool=${tool}]`);
    const A = await xy(...a), C = await xy(...c);
    await page.mouse.move(A[0], A[1]); await page.mouse.down();
    await page.mouse.move((A[0] + C[0]) / 2, (A[1] + C[1]) / 2, { steps: 3 }); await page.mouse.move(C[0], C[1], { steps: 3 });
    await page.mouse.up();
  }
  async function click(tool, a) { if (tool) await page.click(`#${sk} [data-tool=${tool}]`); const A = await xy(...a); await page.mouse.click(A[0], A[1]); }
  const G = [623.8, 526.2], D = [782.5, 696.2], A = [251.2, 166.2];
  await drag("dir", [G[0] + 3, G[1] + 2], [G[0], G[1] + 300]);
  await drag("dir", [D[0] + 2, D[1] - 2], [D[0] - 400, D[1]]);
  await click("pt", [G[0] + 4, D[1] + 4]);
  await drag("dir", [A[0] + 3, A[1] + 3], [G[0] + 3, D[1] - 3]);
  await page.fill(`#${sk} .gt-val`, "380");
  await drag("vec", [1150, 150], [1150, 500]);
  assert.match(await text(page, `#${sk} .gt-status`), /7,60 cm → 380 N/);
  await click("par", [400, D[1] + 1]);                          // référence : la droite horizontale par D
  assert.match(await text(page, `#${sk} .gt-status`), /Référence choisie/);
  await drag(null, [1152, 758], [1152, 758]);                   // parallèle par l'extrémité de P
  await click("par", [(A[0] + G[0]) / 2, (A[1] + D[1]) / 2 + 2]);
  await drag(null, [1149, 152], [1149, 152]);                   // parallèle à (AI) par l'origine de P
  await drag("vec", [1152, 758], [1577, 760]);
  await drag("vec", [1577, 760], [1150, 150]);
  const v = await page.evaluate(() => { const s = window.__app__.sketches.sk_q2_1; return s.strokes.filter((x) => x.t === "vec").map((x) => Math.round(window.__atelier__.lenInfo(s, x.a, x.b).val)); });
  assert.deepEqual(v, [380, 267, 465]);
  const I = await page.evaluate(() => window.__app__.sketches.sk_q2_1.strokes.find((x) => x.t === "pt"));
  assert.ok(Math.abs(I.x - 623.8) < 1 && Math.abs(I.y - 696.2) < 1, "I accroché à l'intersection");
  // mesure, gomme, annuler
  await drag("mes", [1150, 150], [1150, 758]);
  assert.match(await text(page, `#${sk} .gt-status`), /Mesure : 7,60 cm → 380 N/);
  const n = await page.evaluate(() => window.__app__.sketches.sk_q2_1.strokes.length);
  await drag("erase", [1300, 758], [1310, 758]);
  assert.equal(await page.evaluate(() => window.__app__.sketches.sk_q2_1.strokes.length), n - 2);  // vecteur D et parallèle
  await page.click(`#${sk} [data-act=undo]`);
  assert.equal(await page.evaluate(() => window.__app__.sketches.sk_q2_1.strokes.length), n - 3);
  // validation : correction superposée et auto-évaluation
  await page.click(`#${sk} .btn-sketch`);
  assert.ok(await page.isVisible(`#${sk} .selfeval`));
  assert.ok(await page.isChecked(`#${sk} .sk-corr-toggle input`));
  assert.deepEqual(errors, []);
  await context.close();
});

for (const file of Object.keys(EXO)) {
  const X = EXO[file];
  test(`${file} : sujet entièrement juste = 20/20, lectures fausses refusées`, async () => {
    const { context, page, errors } = await open(file);
    assert.equal(await page.locator("#home .btn-mode").count(), 2);
    assert.match(await text(page, ".home-facts"), new RegExp(`${X.parts} parties`));
    assert.match(await text(page, ".home-head"), /Niveau 1/);
    await page.click("[data-mode=training]");
    assert.deepEqual(await page.locator(".rail .tab").allInnerTexts(), ["DP1", "DT1", "DT2"]);
    assert.equal(await page.locator(".gt-sketch").count(), X.sketches.length);
    const ids = await page.evaluate(() => Object.keys(window.__QCFG__));
    assert.deepEqual(ids.slice().sort(), Object.keys(REP[file]).sort());
    for (const [id, ans] of Object.entries(X.wrong)) {
      await page.fill(`#in-${id}`, ans);
      assert.equal(await page.evaluate(([i, a]) => Grading.grade(a, window.__QCFG__[i].grader).ok, [id, ans]), false, `${id} : « ${ans} »`);
    }
    for (const [id, ans] of Object.entries(REP[file])) {
      await page.fill(`#in-${id}`, ans);
      await page.click(`#${id} .btn-validate`);
      assert.match(await text(page, `#${id} .q-status`), /Juste/, `${id} : « ${ans} »`);
      assert.doesNotMatch(await text(page, `#${id} .q-status`), /unité/i, id);
    }
    for (const sk of X.sketches) {
      await page.click(`#${sk} .btn-sketch`);
      for (const cb of await page.locator(`#${sk} .se-item input`).all()) await cb.check();
      await page.click(`#${sk} .btn-self`);
    }
    assert.match(await text(page, "#score-val"), /20,0/);
    assert.equal((await text(page, "#recap .final-note")).trim(), "20,0/20");
    assert.deepEqual(errors, []);
    await context.close();
  });

  test(`${file} : mode examen et téléphone`, async () => {
    const { context, page, errors } = await open(file, { width: 390, height: 844 });
    await page.click("[data-mode=exam]");
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.click("#exam-submit");
    await page.click("#exam-submit");
    for (const sk of X.sketches) assert.ok(await page.isVisible(`#${sk} .selfeval`));
    assert.deepEqual(errors, []);
    await context.close();
  });
}
