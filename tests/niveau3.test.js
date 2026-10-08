// Tests navigateur (Playwright + Chromium) du niveau 3 : accueil, cours 3, exercices 3.1 à 3.3.
//   python3 src/generer.py && NODE_PATH=$(npm root -g) node --test tests/niveau3.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium } = require("playwright");
const REP = require("./reponses-n3.js");

const ROOT = path.join(__dirname, "..");
const url = (f) => "file://" + path.join(ROOT, f);
const EXO = {
  "coffre-fort.html": { parts: 3, sketch: "sk_q1_5", points: 28, wrong: { q3_3: "2019,05 daN", q1_3: "pivot" } },
  "echelle-pompier.html": { parts: 4, sketch: null, points: 24, wrong: { q3_3: "5000 daN", q1_3: "AB" } },
  "cadre-velo.html": { parts: 4, sketch: "sk_q1_3", points: 24, wrong: { q4_5: "780,4 N", q3_3: "A" } },
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

async function drawLine(page, sk, x1, y1, x2, y2) {
  await page.click(`#${sk} [data-tool=line]`);
  const box = await page.locator(`#${sk} canvas`).boundingBox();
  await page.mouse.move(box.x + box.width * x1, box.y + box.height * y1);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * x2, box.y + box.height * y2, { steps: 6 });
  await page.mouse.up();
}

test("accueil : cours 3 et exercices 3.1 à 3.3 avec la pastille Niveau 3", async () => {
  const { context, page, errors } = await open("index.html");
  const cards = await page.locator(".mode-card").evaluateAll((cs) => cs.map((c) => [
    c.querySelector(".mc-tag").textContent.trim(), c.querySelector("h3").textContent,
    (c.querySelector("a") || { getAttribute: () => null }).getAttribute("href")]));
  for (const exp of [["Cours 3 Niveau 3", "Statique analytique", "cours-statique-analytique.html"],
    ["Exercice 3.1 Niveau 3", "Porte de coffre-fort", "coffre-fort.html"],
    ["Exercice 3.2 Niveau 3", "Échelle de pompier", "echelle-pompier.html"],
    ["Exercice 3.3 Niveau 3", "Cadre de vélo tout terrain", "cadre-velo.html"]])
    assert.ok(cards.some((c) => JSON.stringify(c) === JSON.stringify(exp)), exp.join(" | "));
  assert.equal(await page.locator(".pastille.n3").count(), 5); // 4 cartes + la légende
  await page.setViewportSize({ width: 390, height: 844 });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  assert.deepEqual(errors, []);
  await context.close();
});

test("cours 3 : balance, jeux, cartes, atelier des liaisons, moment, poutre pas à pas, quiz", async () => {
  const { context, page, errors } = await open("cours-statique-analytique.html");
  assert.match(await text(page, ".home-head"), /Cours 3[\s\S]*Niveau 3[\s\S]*Statique analytique/);
  assert.equal(await page.locator(".cours-sec").count(), 8);
  // balance : R = P = m g
  await page.fill("#bal-in", "100");
  assert.equal((await text(page, "#bal-p-v")).trim(), "981,0 N");
  assert.equal((await text(page, "#bal-r-v")).trim(), "981,0 N");
  // jeu deux forces : 3 justes, 1 fausse
  const deux = page.locator(".deux-c");
  for (let i = 0; i < 4; i++) {
    const ok = await deux.nth(i).getAttribute("data-ok");
    await deux.nth(i).locator(`button[data-v="${i === 1 ? (ok === "oui" ? "non" : "oui") : ok}"]`).click();
  }
  assert.equal((await text(page, "#deux-s")).trim(), "3 / 4");
  // carte à retourner
  await page.click(".k3-carte >> nth=0");
  assert.match(await text(page, ".k3-carte >> nth=0"), /résultante statique/);
  // atelier : pivot d'axe z → X Y Z L M (N = 0) ; plan → 2 inconnues
  await page.click(".k3-lia[data-k=pivot]");
  for (const i of [0, 1, 2, 3, 4]) await page.click(`.k3-c[data-i="${i}"]`);
  await page.check("#k3-plan-cb");
  await page.click("#k3-ok");
  assert.match(await text(page, "#k3-fb"), /Juste[\s\S]*5 inconnues[\s\S]*2 dans le plan/);
  await page.click(".k3-lia[data-k=ponctuelle]");
  await page.click(`.k3-c[data-i="0"]`);
  await page.click("#k3-ok");
  assert.match(await text(page, "#k3-fb"), /2 cases à revoir/);
  await page.click("#k3-sol");
  assert.match(await text(page, "#k3-fb"), /Juste[\s\S]*1 inconnue/);
  // jeu du plan
  const jp = page.locator(".k3-jp");
  for (let i = 0; i < await jp.count(); i++) {
    const ok = await jp.nth(i).getAttribute("data-ok");
    await jp.nth(i).locator(`button[data-v="${ok}"]`).click();
  }
  assert.equal((await text(page, "#k3-jp-s")).trim(), `${await jp.count()} / ${await jp.count()}`);
  // moment : F = 500 N vers le bas en (4 ; 1) → M = −2 000 N·m ; force dirigée vers A → moment nul
  assert.match(await text(page, "#mr-m"), /^−2\s000 N·m$/);
  await page.fill("#mi-x", "4"); await page.fill("#mi-y", "0"); await page.fill("#mi-a", "180");
  assert.match(await text(page, "#mr-v"), /Moment nul/);
  // poutre : F = 1 000 N vertical à 1 m → YB = 250 N, YA = 750 N, XA = 0
  await page.click("#pe-all");
  assert.match(await text(page, "#pe-4"), /YB = 250 N[\s\S]*XA = 0 N[\s\S]*YA = 750 N/);
  await page.fill("#pi-a", "2");
  assert.match(await page.locator("#df-1").textContent(), /Réussi/);
  // quiz : tout juste → trois étoiles
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

for (const file of Object.keys(EXO)) {
  const X = EXO[file];
  test(`${file} : sujet entièrement juste = 20/20 en entraînement`, async () => {
    const { context, page, errors } = await open(file);
    assert.equal(await page.locator("#home .btn-mode").count(), 2);
    assert.match(await text(page, ".home-facts"), new RegExp(`${X.parts} parties`));
    await page.click("[data-mode=training]");
    assert.equal(await page.locator(".part").count(), X.parts);
    assert.deepEqual(await page.locator(".rail .tab").allInnerTexts(), ["DP1", "DT1"]);
    const ids = await page.evaluate(() => Object.keys(window.__QCFG__));
    assert.deepEqual(ids.slice().sort(), Object.keys(REP[file]).sort());
    for (const [id, ans] of Object.entries(REP[file])) {
      await page.fill(`#in-${id}`, ans);
      await page.click(`#${id} .btn-validate`);
      assert.match(await text(page, `#${id} .q-status`), /Juste/, `${id} : « ${ans} »`);
      assert.doesNotMatch(await text(page, `#${id} .q-status`), /unité/i, id);
    }
    if (X.sketch) {
      await drawLine(page, X.sketch, 0.2, 0.5, 0.4, 0.2);
      await page.click(`#${X.sketch} .btn-sketch`);
      assert.ok(await page.isVisible(`#${X.sketch} .selfeval`));
      for (const cb of await page.locator(`#${X.sketch} .se-item input`).all()) await cb.check();
      await page.click(`#${X.sketch} .btn-self`);
    }
    assert.match(await text(page, "#score-val"), /20,0/);
    assert.equal((await text(page, "#recap .final-note")).trim(), "20,0/20");
    assert.deepEqual(errors, []);
    await context.close();
  });

  test(`${file} : réponses fausses et unité manquante`, async () => {
    const { context, page, errors } = await open(file);
    await page.click("[data-mode=training]");
    for (const [id, ans] of Object.entries(X.wrong)) {
      await page.fill(`#in-${id}`, ans);
      await page.click(`#${id} .btn-validate`);
      assert.doesNotMatch(await text(page, `#${id} .q-status`), /^Juste/, `${id} : « ${ans} »`);
    }
    // valeur juste sans unité : demi-point
    const [id, ans] = Object.entries(REP[file]).find(([, a]) => /\d\s*(daN|N|mm|m|MPa)\b/.test(a));
    await page.fill(`#in-${id}`, ans.replace(/\s*(daN|N\.mm|N|mm|m|MPa)\b.*$/, ""));
    await page.click(`#${id} .btn-validate`);
    assert.match(await text(page, `#${id} .q-status`), /unité/i, id);
    assert.deepEqual(errors, []);
    await context.close();
  });

  test(`${file} : mode examen, remise de la copie, aucun débordement sur téléphone`, async () => {
    const { context, page, errors } = await open(file, { width: 390, height: 844 });
    await page.click("[data-mode=exam]");
    const [id, ans] = Object.entries(REP[file])[0];
    await page.fill(`#in-${id}`, ans);
    assert.ok(!(await page.isVisible(`#${id} .q-expl`)));
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.click("#exam-submit");
    await page.click("#exam-submit");
    assert.ok(await page.isVisible(`#${id} .q-expl`));
    assert.match(await text(page, "#recap .final-note"), /\/20/);
    assert.deepEqual(errors, []);
    await context.close();
  });
}
