const {test:base,expect}=require("playwright/test");
const KEY="cpe-course-progress-v1";
const test=base.extend({page:async({page},use)=>{
  const errors=[];page.on("pageerror",error=>errors.push(error.message));
  await page.route("**/*",route=>new URL(route.request().url()).hostname==="127.0.0.1"?route.continue():route.abort());
  await page.route("**/worker.js",route=>route.fulfill({contentType:"application/javascript",body:'self.onmessage=({data})=>{if(data.type==="boot")self.postMessage({type:"ready"});if(data.type==="run")self.postMessage({type:"result",id:data.id,result:{tests:[{name:"test_bridge",status:data.files["exercise.py"].includes("# FAIL")?"fail":"pass"}]}})}'}));
  await use(page);expect(errors).toEqual([]);
}});
const saved=page=>page.evaluate(key=>JSON.parse(localStorage.getItem(key)),KEY);

for(const topic of ["return","collections","aliasing","defaults","process"]){
  test(`${topic} bridge: worked example, repair, independent check, reload and return`,async({page})=>{
    await page.goto("/#/diagnostic");
    const bridge=await page.evaluate(topic=>DATA.bash_bridges.find(bridge=>bridge.id===topic),topic);
    const before=await page.evaluate(({lessonId,KEY})=>{
      const lesson=LESSON_BY_ID[lessonId];P.cards=P.cards||{};P.card_reward_history=P.card_reward_history||{};
      for(const card of lesson.cards.slice(3)){P.cards[card.id]={done:true,correct:true,tries:1};if(["code","quiz","predict","fill"].includes(card.kind))P.card_reward_history[card.id]=true;}
      P.xp=200;for(const id of lesson.cards.filter(card=>card.kind==="exercise").map(card=>card.exercise_id))P.solved[id]={xp:20};saveProgress();
      return JSON.parse(localStorage.getItem(KEY));
    },{lessonId:bridge.lesson,KEY});
    await page.goto(`/#/learn/${bridge.lesson}?card=${bridge.card}`);
    await expect(page.locator(".cardbody h3")).toBeVisible();
    await expect(page.getByRole("link",{name:"Return to diagnostic",exact:true})).toBeVisible();
    await page.locator("#nextbtn").click();
    await expect(page).toHaveURL(new RegExp(`card=bash-${topic}-modify$`));
    const cards=await page.evaluate(lesson=>LESSON_BY_ID[lesson].cards.slice(0,3),bridge.lesson);
    await page.locator("#cardcode").fill(cards[1].starter+"\n"+cards[1].solution);
    await page.reload();
    await expect(page.locator("#cardcode")).toHaveValue(cards[1].starter+"\n"+cards[1].solution);
    await page.locator("#runcard").click();
    await expect(page.locator("#feedback")).toContainText("It runs and does the job");
    await page.locator("#go").click();
    await expect(page).toHaveURL(new RegExp(`card=bash-${topic}-check$`));
    await expect(page.locator("#cardcode")).toHaveValue(cards[2].starter+"\n");
    await page.locator("#cardcode").fill(cards[2].starter+"\n"+cards[2].solution);
    await page.locator("#runcard").click();
    await expect(page.locator("#feedback")).toContainText("bridge is complete");
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    await page.getByRole("link",{name:"Return to diagnostic",exact:true}).click();
    const after=await saved(page);
    for(const [id,state]of Object.entries(before.cards))expect(after.cards[id]).toEqual(state);
    for(const [id,reward]of Object.entries(before.card_reward_history))expect(after.card_reward_history[id]).toBe(reward);
    expect(after.solved).toEqual(before.solved);expect(after.xp).toBe(202);
    expect(after.diagnostic).toEqual(before.diagnostic);
    // Explicit bridge review still starts at the worked example after the whole
    // lesson is completed; replay leaves earned XP and saved answers intact.
    await page.goto(`/#/learn/${bridge.lesson}?card=${bridge.card}`);
    await expect(page.locator(".cardbody h3")).toBeVisible();
    await page.locator("#nextbtn").click();await page.locator("#runcard").click();
    await expect(page.locator("#feedback")).toContainText("It runs and does the job");
    expect((await saved(page)).xp).toBe(202);
    await page.goto(`/#/learn/${bridge.lesson}`);
    await expect(page.getByRole("heading",{name:new RegExp(`Lesson ${bridge.lesson.replace('.','\\.')} complete`)})).toBeVisible();
  });
}

test("diagnostic suggestions are optional, reflect saved gaps and retain review navigation",async({page})=>{
  await page.goto("/#/diagnostic");
  await expect(page.locator(".bash-bridges")).toHaveCount(0);
  await page.goto("/#/diagnostic/3.1");
  await page.getByLabel("Confidence",{exact:true}).selectOption("needs_review");
  await page.locator("#diagnostic-note").fill("Printed instead of returning the command list");
  await page.getByRole("link",{name:"Choose what to revisit",exact:true}).click();
  await expect(page.locator(".bash-bridges")).toHaveCount(1);
  await expect(page.locator(".bash-bridges")).toContainText("not a diagnosis");
  await expect(page.locator(".bash-bridges")).toContainText("process failures are not directly assessed");
  await page.getByRole("link",{name:"Return versus print",exact:true}).click();
  await expect(page).toHaveURL(/#\/learn\/3\.1\?card=bash-return-worked$/);
  await page.getByRole("link",{name:"Return to diagnostic",exact:true}).click();
  expect((await saved(page)).diagnostic.reflections["3.1"].mistake_note).toContain("Printed");
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test("a card from another lesson cannot redirect progress or clear saved answers",async({page})=>{
  await page.goto("/#/diagnostic");const before=await saved(page);
  await page.goto("/#/learn/3.1?card=bash-process-worked");
  await expect(page.locator("#toast")).toContainText("does not belong");
  await expect(page.getByRole("heading",{name:/Part 3/})).toBeVisible();
  expect(await saved(page)).toEqual(before);
});
