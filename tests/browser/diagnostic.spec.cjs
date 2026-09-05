const {test: base, expect} = require("playwright/test");
const KEY = "cpe-course-progress-v1", IDS = ["1.2", "1.3", "2.1", "2.2", "3.1", "5.1"];
const test = base.extend({page: async ({page}, use) => {
  const errors = []; page.on("pageerror", error => errors.push(error.message));
  await page.route("**/*", route => new URL(route.request().url()).hostname === "127.0.0.1" ? route.continue() : route.abort());
  await page.route("**/worker.js", route => route.fulfill({contentType: "application/javascript", body: `self.onmessage = ({data}) => {
    if (data.type === "boot") self.postMessage({type:"ready"});
    if (data.type === "run") self.postMessage({type:"result",id:data.id,result:{tests:[{name:"test_answer",status:data.files["exercise.py"].includes("FAIL") ? "fail" : "pass"}]}});
  };`}));
  await use(page); expect(errors).toEqual([]);
}});
async function progress(page) { return page.evaluate(key => JSON.parse(localStorage.getItem(key)), KEY); }
function lifetime(saved) { const {diagnostic, diagnostic_history, review_queue, ...rest} = saved; return rest; }
async function start(page) {
  await page.goto("/#/diagnostic");
  await page.evaluate(key => {
    const saved = JSON.parse(localStorage.getItem(key));
    saved.xp = 100; saved.solved = {"1.2": {passed_at: "2026-01-01T12:00:00Z", xp: 30}};
    saved.hints = {"1.2": 2}; saved.cards = {"1.2:1": {done:true,correct:true,tries:1}};
    localStorage.setItem(key, JSON.stringify(saved));
    localStorage.setItem("cpe-course-draft:1.2", "# saved ordinary answer");
  }, KEY);
  await page.reload(); return lifetime(await progress(page));
}

test("six fresh exercises, help escape, independent outcomes/reflections and saved summary", async ({page}) => {
  const before = await start(page);
  await expect(page.locator("#app")).toContainText("0/6 attempted");
  for (const id of IDS) {
    await page.goto("/#/diagnostic/" + id);
    await expect(page.locator("#diagnostic-guidance")).toBeHidden();
    await expect(page.locator("#diagnostic-code")).not.toHaveValue("# saved ordinary answer");
    if (id === "1.2") {
      await page.locator("#diagnostic-help").click();
      await expect(page.locator("#diagnostic-guidance")).toBeVisible();
      await page.locator("#diagnostic-code").fill("# FAIL");
      await page.locator("#diagnostic-run").click();
      await expect(page.locator("#diagnostic-results")).toContainText("not yet passing");
      await expect(page.locator("#diagnostic-outcome")).toContainText("1 attempt(s) · latest outcome: not passed");
    }
    await page.locator("#diagnostic-code").fill("# my diagnostic draft " + id);
    await page.locator("#diagnostic-run").click();
    await expect(page.locator("#diagnostic-results")).toContainText("Diagnostic tests passed");
    await expect(page.locator("#diagnostic-outcome")).toContainText(`${id === "1.2" ? 2 : 1} attempt(s) · latest outcome: passed`);
    await page.locator("#diagnostic-confidence").selectOption(id === "1.2" ? "needs_review" : "confident");
    await page.locator("#diagnostic-note").fill(id === "1.2" ? "Strip first; passing still needs review" : "Understood " + id);
    await page.reload();
    await expect(page.locator("#diagnostic-code")).toHaveValue("# my diagnostic draft " + id);
    await expect(page.locator("#diagnostic-confidence")).toHaveValue(id === "1.2" ? "needs_review" : "confident");
  }
  await page.getByRole("link", {name:"Choose what to revisit"}).click();
  await expect(page.locator("#app")).toContainText("6/6 attempted · 6/6 reflections recorded");
  await expect(page.locator("#app")).toContainText("passed · 2 attempt(s) · confidence: needs review · help used");
  await expect(page.locator("#app")).toContainText("Strip first; passing still needs review");
  await expect(page.locator('a[href="#/learn/1.2"]')).toHaveText("Revisit Cleaning up strings");
  expect(lifetime(await progress(page))).toEqual(before);
  expect(await page.evaluate(() => localStorage.getItem("cpe-course-draft:1.2"))).toBe("# saved ordinary answer");
  const old = (await progress(page)).diagnostic;
  await page.locator("#diagnostic-new").click();
  const saved = await progress(page);
  expect(saved.diagnostic.attempts).toEqual([]); expect(saved.diagnostic_history.at(-1)).toEqual(old);
  await page.locator("details summary").click();
  await expect(page.locator("details")).toContainText("Strip first; passing still needs review");
  await page.reload(); await expect(page.locator("#app")).toContainText("0/6 attempted");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("pending result keeps newer draft and cannot enter a replacement round", async ({page}) => {
  const before = await start(page);
  await page.goto("/#/diagnostic/1.2");
  await page.evaluate(() => { runInPython = () => new Promise(resolve => { window.finishDiagnostic = resolve; }); });
  await page.locator("#diagnostic-code").fill("# submitted draft");
  await page.locator("#diagnostic-run").click();
  await page.locator("#diagnostic-code").fill("# newer draft while grading");
  await page.locator("#diagnostic-confidence").selectOption("needs_review");
  await page.locator("#diagnostic-note").fill("Keep my reflection while grading");
  await page.evaluate(() => window.finishDiagnostic({tests:[{status:"pass"}]}));
  await expect(page.locator("#diagnostic-outcome")).toContainText("1 attempt(s) · latest outcome: passed");
  await expect(page.locator("#diagnostic-code")).toHaveValue("# newer draft while grading");
  await expect(page.locator("#diagnostic-confidence")).toHaveValue("needs_review");
  await expect(page.locator("#diagnostic-note")).toHaveValue("Keep my reflection while grading");
  await page.locator("#diagnostic-run").click();
  await page.getByRole("link", {name:"Choose what to revisit"}).click();
  await page.evaluate(() => window.finishDiagnostic({tests:[{status:"pass"}]}));
  await expect(page.locator("#app")).toContainText("1/6 attempted");
  expect((await progress(page)).diagnostic.drafts["1.2"]).toBe("# newer draft while grading");
  await page.goto("/#/diagnostic/1.2");
  await page.locator("#diagnostic-run").click();
  await page.getByRole("link", {name:"Choose what to revisit"}).click();
  await page.locator("#diagnostic-new").click();
  const saved = await progress(page);
  await page.evaluate(() => window.finishDiagnostic({tests:[{status:"pass"}]}));
  await expect(page.locator("#toast")).toContainText("round changed");
  expect(await progress(page)).toEqual(saved);
  expect(lifetime(saved)).toEqual(before);
});

test("storage failures and invalid imported metadata remain recoverable", async ({page}) => {
  await start(page);
  await page.goto("/#/diagnostic/1.2");
  const saved = await progress(page);
  await page.evaluate(() => { window.realSetItem = Storage.prototype.setItem; Storage.prototype.setItem = () => { throw Error("full"); }; });
  await page.locator("#diagnostic-code").fill("# retain in editor until storage is free");
  await expect(page.locator("#diagnostic-save")).toContainText("could not be saved");
  await page.locator("#diagnostic-run").click();
  expect(await progress(page)).toEqual(saved);
  await expect(page.locator("#diagnostic-results")).toBeEmpty();
  await page.evaluate(key => {
    Storage.prototype.setItem = window.realSetItem;
    const p = JSON.parse(localStorage.getItem(key)); p.diagnostic = {id:"../../escape",drafts:{"1.2":"keep imported work"}};
    localStorage.setItem(key, JSON.stringify(p));
  }, KEY);
  await page.reload();
  await expect(page.locator("#app")).toContainText("Saved diagnostic data is invalid");
  const raw = (await progress(page)).diagnostic;
  await page.locator("#diagnostic-new").click();
  expect((await progress(page)).diagnostic_history.at(-1)).toEqual(raw);
});
