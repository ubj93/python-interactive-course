const { test: base, expect } = require("playwright/test");
const KEY = "cpe-course-progress-v1", DRAFT = "cpe-course-draft:", RECOVERY = "cpe-course-backup-recovery:", PENDING = "cpe-course-backup-pending-v1";
const test = base.extend({
  page: async ({ page }, use) => {
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.route("**/*", route => new URL(route.request().url()).hostname === "127.0.0.1" ? route.continue() : route.abort());
    await page.route("**/worker.js", route => route.fulfill({ contentType: "application/javascript", body: 'self.onmessage=({data})=>{if(data.type==="boot")self.postMessage({type:"ready"});if(data.type==="run")self.postMessage({type:"result",id:data.id,result:{tests:[{name:"test_answer",status:"pass"}]}})}' }));
    await use(page);
    expect(errors).toEqual([]);
  },
});
const storage = page => page.evaluate(() => Object.fromEntries(Object.keys(localStorage).sort().map(key => [key, localStorage.getItem(key)])));
const live = values => Object.fromEntries(Object.entries(values).filter(([key]) => !key.startsWith(RECOVERY) && key !== PENDING));
const backup = (xp = 40) => ({format:"python-cpe-course-backup",version:1,exported_at:"2026-09-05T12:00:00Z",progress:{xp,solved:{},opened:{"1.1":17}},drafts:{[DRAFT+"1.2"]:"new answer",[DRAFT+"new-card"]:"new draft"},extension:{keep:"unknown metadata"}});
async function preview(page, value) {
  await page.locator("#io").fill(typeof value === "string" ? value : JSON.stringify(value));
  await page.getByRole("button", {name:"Import",exact:true}).click();
}
async function seed(page) {
  await page.goto("/#/profile");
  await page.evaluate(({KEY,DRAFT}) => {
    P.xp=18; P.solved={"1.1":{xp:18}}; saveProgress();
    localStorage.setItem(DRAFT+"1.2", "saved answer");
    localStorage.setItem(DRAFT+"card:1.1:3", "legacy card answer");
    localStorage.setItem("unrelated-app", "leave intact");
  }, {KEY,DRAFT});
  await page.reload();
}

test("exercise and stable code-card drafts round-trip with all progress after preview and cancel", async ({page}) => {
  await page.goto("/#/ex/1.2");
  await page.locator("#code").fill("# saved exercise answer\nanswer = 42\n");
  const card = await page.evaluate(() => {
    const lesson=DATA.parts[0].lessons[0], index=lesson.cards.findIndex(card=>card.kind==="code");
    P.cards = P.cards || {};
    lesson.cards.slice(0,index).forEach(card=>{P.cards[card.id]={done:true,correct:null,tries:0};});
    P.xp=123; P.solved={"1.2":{xp:7}};
    const diagnostic=beginDiagnostic();
    updateDiagnostic("1.2","reflect",diagnostic.id,{confidence:"needs_review",note:"Remember stripping"});
    P.diagnostic.drafts["1.2"]="# diagnostic draft";
    P.review_queue={version:1,items:{"1.2":{note:"opaque review note"}}};
    P.unrecognized_extension={nested:["keep",17,null]}; saveProgress();
    localStorage.setItem(DRAFT_KEY+"card:legacy-extra", "# retained old card");
    return lesson.cards[index];
  });
  await page.goto("/#/learn/1.1");
  await page.locator("#cardcode").fill("# saved code card\nprint('restored')\n");
  await page.goto("/#/profile");
  await page.getByRole("button",{name:"Export",exact:true}).click();
  const exported=await page.locator("#io").inputValue(), document=JSON.parse(exported);
  expect(document.format).toBe("python-cpe-course-backup");
  expect(document.drafts[DRAFT+"1.2"]).toContain("answer = 42");
  expect(document.drafts[DRAFT+"card:"+card.id]).toContain("saved code card");
  expect(document.progress.diagnostic.drafts["1.2"]).toBe("# diagnostic draft");
  await page.evaluate(({KEY,DRAFT}) => {
    localStorage.setItem(KEY,JSON.stringify({xp:9,solved:{}}));
    Object.keys(localStorage).filter(key=>key.startsWith(DRAFT)).forEach(key=>localStorage.removeItem(key));
    localStorage.setItem(DRAFT+"1.2","foreign answer"); localStorage.setItem(DRAFT+"remove-me","foreign draft");
  },{KEY,DRAFT});
  await page.reload();
  const before=await storage(page);
  await preview(page,exported);
  await expect(page.locator("#backup-preview")).toContainText("9 → 123 XP");
  await expect(page.locator("#backup-preview")).toContainText("1 replaced, 1 removed");
  expect(await storage(page)).toEqual(before);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.getByRole("button",{name:"Cancel import"}).click();
  expect(await storage(page)).toEqual(before);
  await preview(page,exported);
  await page.getByRole("button",{name:"Replace progress and drafts"}).click();
  const after=await storage(page), restored=JSON.parse(after[KEY]);
  expect(restored.unrecognized_extension).toEqual(document.progress.unrecognized_extension);
  expect(restored.review_queue).toEqual(document.progress.review_queue);
  expect(restored.diagnostic).toEqual(document.progress.diagnostic);
  expect(after[DRAFT+"remove-me"]).toBeUndefined();
  expect(JSON.parse(after[Object.keys(after).find(key=>key.startsWith(RECOVERY))]).recovery_storage[KEY]).toBe(before[KEY]);
  await page.getByRole("button",{name:"Load recovery JSON for preview"}).click();
  await expect(page.locator("#backup-preview")).toContainText("123 → 9 XP");
  await page.getByRole("button",{name:"Cancel import"}).click();
  await page.goto("/#/ex/1.2");
  await expect(page.locator("#code")).toHaveValue(document.drafts[DRAFT+"1.2"]);
  await page.goto("/#/learn/1.1");
  await expect(page.locator("#cardcode")).toHaveValue(document.drafts[DRAFT+"card:"+card.id]);
  await page.reload();
  await expect(page.locator("#cardcode")).toHaveValue(document.drafts[DRAFT+"card:"+card.id]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test("legacy import preserves drafts and invalid imports preserve input and recovery copies", async ({page}) => {
  await seed(page);
  const before=await storage(page);
  await preview(page,{xp:23,solved:{},review_queue:{unknown:"preserve"}});
  await expect(page.locator("#backup-preview")).toContainText("keep all 2 current code drafts");
  await page.getByRole("button",{name:"Replace progress only"}).click();
  const saved=await storage(page);
  for(const [key,value] of Object.entries(before).filter(([key])=>key.startsWith(DRAFT))) expect(saved[key]).toBe(value);
  expect(JSON.parse(saved[KEY]).xp).toBe(23);
  for(const invalid of [{...backup(),version:99},{...backup(),drafts:{"other-app":"no"}},{...backup(),progress:{xp:1,cards:[]}},'{"xp":']) {
    const source=typeof invalid==="string"?invalid:JSON.stringify(invalid), current=await storage(page);
    await preview(page,source);
    await expect(page.locator("#backup-preview")).toContainText("Import rejected");
    await expect(page.locator("#io")).toHaveValue(source);
    expect(await storage(page)).toEqual(current);
  }
});

test("a changed draft after preview requires another explicit confirmation", async ({page}) => {
  await seed(page);
  await preview(page,backup());
  await page.evaluate(DRAFT=>localStorage.setItem(DRAFT+"1.2","saved after preview"),DRAFT);
  const before=await storage(page);
  await page.getByRole("button",{name:"Replace progress and drafts"}).click();
  await expect(page.locator("#backup-preview")).toContainText("Review this updated preview");
  expect(await storage(page)).toEqual(before);
  await page.getByRole("button",{name:"Replace progress and drafts"}).click();
  expect((await storage(page))[DRAFT+"1.2"]).toBe("new answer");
  await page.getByRole("button",{name:"Export",exact:true}).click();
  expect(JSON.parse(await page.locator("#io").inputValue()).extension).toEqual({keep:"unknown metadata"});
});

test("storage quota before recovery leaves data untouched and a later write failure rolls back", async ({page}) => {
  await seed(page);
  const before=await storage(page), incoming=JSON.stringify(backup());
  await page.evaluate(RECOVERY=>{window.savedSet=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key.startsWith(RECOVERY))throw new Error("quota");return window.savedSet.call(this,key,value);};},RECOVERY);
  await preview(page,incoming);
  await page.getByRole("button",{name:"Replace progress and drafts"}).click();
  await expect(page.locator("#backup-preview")).toContainText("previous data was retained");
  expect(await storage(page)).toEqual(before);
  await expect(page.locator("#io")).toHaveValue(incoming);
  await page.evaluate(DRAFT=>{let failed=false;Storage.prototype.setItem=function(key,value){if(key===DRAFT+"new-card"&&!failed){failed=true;throw new Error("quota during import");}return window.savedSet.call(this,key,value);};},DRAFT);
  await preview(page,incoming);
  await page.getByRole("button",{name:"Replace progress and drafts"}).click();
  await expect(page.locator("#backup-preview")).toContainText("previous data was retained");
  const after=await storage(page);
  expect(live(after)).toEqual(live(before));
  expect(after[PENDING]).toBeUndefined();
  expect(Object.keys(after).filter(key=>key.startsWith(RECOVERY))).toHaveLength(1);
  await page.evaluate(()=>{Storage.prototype.setItem=window.savedSet;});
  await page.reload();
  expect(live(await storage(page))).toEqual(live(before));
});

test("an interrupted import blocks study until recovery survives reload and can retry", async ({page}) => {
  await seed(page);
  const before=await storage(page);
  await page.evaluate(DRAFT=>{window.savedSet=Storage.prototype.setItem;let failed=false;Storage.prototype.setItem=function(key,value){if(key===DRAFT+"new-card")failed=true;if(failed)throw new Error("storage unavailable");return window.savedSet.call(this,key,value);};},DRAFT);
  await preview(page,backup());
  await page.getByRole("button",{name:"Replace progress and drafts"}).click();
  await expect(page.getByRole("heading",{name:"Recover the interrupted import"})).toBeVisible();
  const interrupted=await storage(page), recovery=JSON.parse(interrupted[interrupted[PENDING]]);
  expect(recovery.progress.xp).toBe(18);
  expect(recovery.recovery_storage[KEY]).toBe(before[KEY]);
  expect(recovery.drafts[DRAFT+"1.2"]).toBe("saved answer");
  await page.addInitScript(PENDING=>{if(localStorage.getItem(PENDING)){window.savedSet=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new Error("storage still unavailable");};}},PENDING);
  await page.reload();
  await expect(page.getByRole("heading",{name:"Recover the interrupted import"})).toBeVisible();
  await expect(page.locator("#backup-recovery-json")).toContainText("saved answer");
  await page.goto("/#/ex/1.2");
  await expect(page.locator("#code")).toHaveCount(0);
  await page.evaluate(()=>{Storage.prototype.setItem=window.savedSet;});
  await page.getByRole("button",{name:"Retry recovery"}).click();
  await expect(page.locator("#code")).toHaveValue("saved answer");
  const after=await storage(page);
  expect(after[PENDING]).toBeUndefined();
  expect(after[DRAFT+"card:1.1:3"]).toBe(before[DRAFT+"card:1.1:3"]);
  expect(JSON.parse(after[KEY]).xp).toBe(18);
  expect(after[interrupted[PENDING]]).toBe(interrupted[interrupted[PENDING]]);
});
