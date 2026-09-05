const { test: base, expect } = require("playwright/test");

const STORE_KEY = "cpe-course-progress-v1";
const LEGACY_KEY = "cpe-course-interview";
const passingWorker = `
self.onmessage = async ({data}) => {
  if (data.type === "boot") self.postMessage({type:"ready"});
  if (data.type === "run") {
    self.postMessage({type:"result",id:data.id,result:{tests:[{name:"test_answer",status:"pass"}]}});
  }
};`;
const test = base.extend({
  page: async ({ page }, use) => {
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.route("**/*", route => new URL(route.request().url()).hostname === "127.0.0.1" ? route.continue() : route.abort());
    await page.route("**/worker.js", route => route.fulfill({contentType:"application/javascript",body:passingWorker}));
    await use(page);
    expect(errors).toEqual([]);
  },
});

async function progress(page) {
  return page.evaluate(key => JSON.parse(localStorage.getItem(key)), STORE_KEY);
}

test("legacy round needs a fresh solved retry and keeps its finished result", async ({ page }) => {
  await page.goto("/#/interview");
  await page.evaluate(({key, legacy}) => {
    const started = Date.now();
    localStorage.setItem(key, JSON.stringify({xp:100,solved:{"9.1":{passed_at:new Date(started-86400000).toISOString(),xp:100}}}));
    localStorage.setItem(legacy, JSON.stringify({ids:["9.1"],started,deadline:started+2700000,before:["9.1"]}));
  }, {key:STORE_KEY,legacy:LEGACY_KEY});
  await page.reload();
  await expect(page.getByText("0/1 passed · 0/1 on time", {exact:true})).toBeVisible();
  await expect(page.getByText(/Only fresh runs since migration count/)).toBeVisible();
  expect(await page.evaluate(key => localStorage.getItem(key), LEGACY_KEY)).toBeNull();
  const originalSolved = (await progress(page)).solved;
  await page.locator('.item[href="#/ex/9.1"]').click();
  await page.getByRole("button", {name:"Run tests"}).click();
  await expect(page.locator("#results")).toContainText("already solved, no extra xp");
  await page.goto("/#/interview");
  await expect(page.getByText("1/1 passed · 1/1 on time", {exact:true})).toBeVisible();
  await page.getByRole("button", {name:"Finish and save result"}).click();
  await page.reload();
  await expect(page.locator("summary")).toHaveText("Last round: 1/1 passed · 1/1 on time");
  const saved = await progress(page);
  expect(saved.xp).toBe(100);
  expect(saved.solved).toEqual(originalSolved);
  expect(saved.interview).toBeNull();
  expect(saved.last_interview.attempts).toHaveLength(1);
  await page.getByRole("button", {name:"Start a 45-minute round",exact:true}).click();
  await expect(page.getByText("0/3 passed · 0/3 on time", {exact:true})).toBeVisible();
  expect((await progress(page)).last_interview).toEqual(saved.last_interview);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

for (const existingRound of [true, false]) test(`a pending run cannot credit a ${existingRound ? "replacement" : "new"} round or write into its view`, async ({ page }) => {
  let releaseRun;
  const release = new Promise(resolve => { releaseRun = resolve; });
  await page.route("**/__release-run__", async route => { await release; await route.fulfill({body:"ready"}); });
  await page.route("**/worker.js", route => route.fulfill({contentType:"application/javascript",body:passingWorker.replace('self.postMessage({type:"result"', 'await fetch("/__release-run__"); self.postMessage({type:"result"')}));
  await page.goto("/#/interview");
  await page.evaluate(({key, existingRound}) => {
    const started = new Date().toISOString();
    const solved = {};
    for (const part of window.COURSE_DATA.parts) for (const ex of part.exercises) {
      if (!["9.1","9.2","9.3"].includes(ex.id)) solved[ex.id] = {passed_at:started,xp:1};
    }
    const interview = existingRound ? {version:1,id:"round-a",kind:"interview",ids:["9.1"],started,deadline:new Date(Date.now()+2700000).toISOString(),status:"active",attempts:[]} : null;
    localStorage.setItem(key, JSON.stringify({xp:100,solved,interview}));
  }, {key:STORE_KEY,existingRound});
  await page.reload();
  await page.goto("/#/ex/9.1");
  const request = page.waitForRequest("**/__release-run__");
  await page.getByRole("button", {name:"Run tests"}).click();
  await request;
  await page.goto("/#/interview");
  await page.getByRole("button", {name:existingRound ? "Save this round and start another" : "Start a 45-minute round",exact:true}).click();
  const before = await progress(page);
  expect(before.interview.ids).toContain("9.1");
  releaseRun();
  await expect.poll(async () => (await progress(page)).attempts["9.1"]).toBe(1);
  const after = await progress(page);
  expect(after.interview.attempts).toEqual([]);
  expect(after.last_interview).toEqual(before.last_interview);
  await expect(page.getByText("0/3 passed · 0/3 on time", {exact:true})).toBeVisible();
});

test("a second exercise run cannot discard a pending submission", async ({ page }) => {
  let releaseRun;
  const release = new Promise(resolve => { releaseRun = resolve; });
  await page.route("**/__release-run__", async route => { await release; await route.fulfill({body:"ready"}); });
  await page.route("**/worker.js", route => route.fulfill({contentType:"application/javascript",body:passingWorker.replace('self.postMessage({type:"result"', 'await fetch("/__release-run__"); self.postMessage({type:"result"')}));
  await page.goto("/#/ex/9.1");
  const request = page.waitForRequest("**/__release-run__");
  await page.getByRole("button", {name:"Run tests"}).click();
  await request;
  await page.goto("/#/ex/9.2");
  await page.getByRole("button", {name:"Run tests"}).click();
  await expect(page.locator("#results")).toContainText("Another test run is still running");
  releaseRun();
  await expect.poll(async () => (await progress(page)).attempts["9.1"]).toBe(1);
  expect((await progress(page)).attempts["9.2"]).toBeUndefined();
  await expect(page.getByRole("heading", {name:/^9\.2 /})).toBeVisible();
});
