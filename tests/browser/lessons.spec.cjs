const { test: base, expect } = require("playwright/test");

const STORE_KEY = "cpe-course-progress-v1";
// Exercise grading is covered by the Python suites. Keep navigation checks
// deterministic and offline while still exercising the real worker protocol.
const passingWorker = `
self.onmessage = ({ data }) => {
  if (data.type === "boot") self.postMessage({ type: "ready" });
  if (data.type === "run") self.postMessage({
    type: "result", id: data.id,
    result: { tests: [{ name: "test_answer", status: "pass" }] },
  });
};`;

const test = base.extend({
  page: async ({ page }, use) => {
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.route("**/*", (route) => {
      const url = new URL(route.request().url());
      return url.hostname === "127.0.0.1" ? route.continue() : route.abort();
    });
    await page.route("**/worker.js", (route) => route.fulfill({
      contentType: "application/javascript", body: passingWorker,
    }));
    await use(page);
    expect(errors).toEqual([]);
  },
});

async function progress(page) {
  return page.evaluate((key) => JSON.parse(localStorage.getItem(key)), STORE_KEY);
}

// Seed only the state needed for an edge case, in Playwright's fresh context.
async function startAtExercise(page, { solved = false, recapDone = false } = {}) {
  await page.goto("/#/learn/1.1");
  await page.evaluate(({ key, solved, recapDone }) => {
    const lesson = window.COURSE_DATA.parts[0].lessons[0];
    const saved = JSON.parse(localStorage.getItem(key) || "{}");
    saved.cards = {};
    lesson.cards.forEach((card, index) => {
      if (card.kind !== "exercise" && (card.kind !== "recap" || recapDone)) {
        saved.cards[lesson.id + ":" + index] = { done: true, correct: null, tries: 0 };
      }
    });
    if (solved) saved.solved = { "1.1": { passed_at: "2026-01-01T12:00:00Z", xp: 3 } };
    localStorage.setItem(key, JSON.stringify(saved));
  }, { key: STORE_KEY, solved, recapDone });
  await page.reload();
  await expect(page.locator(".kind")).toHaveText("Exercise");
}

async function passExercise(page) {
  await page.locator("#code").fill("def greet_device(hostname, os_name, ram_gb):\n    return f'Hello, {hostname}! You are running {os_name} with {ram_gb} GB of RAM.'\n");
  await page.getByRole("button", { name: "Run tests" }).click();
  await expect(page.locator("#results")).toContainText("All 1 tests passed");
}

async function returnToLesson(page) {
  const continuation = page.getByRole("link", { name: /^Continue: Lesson 1\.1 / });
  await expect(continuation).toHaveAttribute("href", "#/learn/1.1");
  await continuation.click();
}

async function finishRecap(page) {
  await expect(page.locator(".kind")).toHaveText("Recap");
  await page.getByRole("button", { name: "Continue", exact: false }).click();
  await expect(page.getByRole("heading", { name: "✔ Lesson 1.1 complete" })).toBeVisible();
}

test("learn, exercise, pass, recap, complete, and next lesson", async ({ page }) => {
  await page.goto("/#/learn/1.1");
  const cards = await page.evaluate(() => window.COURSE_DATA.parts[0].lessons[0].cards);
  for (const card of cards) {
    if (card.kind === "exercise") break;
    if (card.kind === "teach") {
      await page.locator("#nextbtn").click();
    } else if (card.kind === "code") {
      await page.locator("#cardcode").fill((card.starter || "") + "\n" + card.solution);
      await page.locator("#runcard").click();
      await page.locator("#go").click();
    } else if (card.kind === "quiz") {
      await page.locator(".opt").nth(card.correct).click();
      await page.locator("#go").click();
    } else {
      await page.locator("#ans").fill(card.answers[0]);
      await page.locator("#checkbtn").click();
      await page.locator("#go").click();
    }
  }
  await expect(page.locator(".kind")).toHaveText("Exercise");
  await page.getByRole("link", { name: "Open the exercise" }).click();
  await expect(page).toHaveURL(/#\/ex\/1\.1\?from=1\.1$/);
  await passExercise(page);
  await returnToLesson(page);
  await finishRecap(page);
  await page.getByRole("link", { name: /^Next: Lesson 1\.2 / }).click();
  await expect(page).toHaveURL(/#\/learn\/1\.2$/);
  await expect(page.locator(".kind")).toHaveText("Learn");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("reload and leaving preserve the unfinished recap; complete reload shows completion", async ({ page }) => {
  await startAtExercise(page);
  await page.getByRole("link", { name: "Open the exercise" }).click();
  await passExercise(page);
  await returnToLesson(page);
  await expect(page.locator(".kind")).toHaveText("Recap");
  await page.reload();
  await expect(page.locator(".kind")).toHaveText("Recap");
  await page.getByRole("link", { name: "Home", exact: true }).click();
  await page.getByRole("link", { name: /^Continue learning: 1\.1 / }).click();
  await finishRecap(page);
  await page.reload();
  await expect(page.getByRole("heading", { name: "✔ Lesson 1.1 complete" })).toBeVisible();
  await expect(page.locator(".kind")).toHaveCount(0);
});

test("leaving an unsolved exercise resumes the unfinished exercise card", async ({ page }) => {
  await startAtExercise(page);
  await page.getByRole("link", { name: "Open the exercise" }).click();
  await page.getByRole("link", { name: "Lesson 1.1", exact: true }).click();
  await expect(page.locator(".kind")).toHaveText("Exercise");
  await page.reload();
  await expect(page.getByRole("link", { name: "Open the exercise" })).toBeVisible();
});

test("skipping stays available and the missing exercise completes after its recap", async ({ page }) => {
  await startAtExercise(page);
  await page.getByRole("button", { name: "Skip for now" }).click();
  await expect(page.locator(".kind")).toHaveText("Recap");
  await page.locator("#nextbtn").click();
  await expect(page.getByRole("heading", { name: "Cards done" })).toBeVisible();
  const saved = await progress(page);
  expect(saved.solved["1.1"]).toBeUndefined();
  const exerciseIndex = await page.evaluate(() => window.COURSE_DATA.parts[0].lessons[0].cards.findIndex((card) => card.kind === "exercise"));
  expect(saved.cards["1.1:" + exerciseIndex]).toBeUndefined();
  await page.getByRole("link", { name: "Do exercise 1.1" }).click();
  await passExercise(page);
  await expect(page.getByRole("link", { name: /^Continue: Lesson 1\.2 / })).toBeVisible();
  await page.getByRole("link", { name: "Lesson 1.1", exact: true }).click();
  await expect(page.getByRole("heading", { name: "✔ Lesson 1.1 complete" })).toBeVisible();
});

test("an already-solved exercise returns to its unfinished lesson without a loop or extra XP", async ({ page }) => {
  await startAtExercise(page, { solved: true });
  await page.goto("/#/ex/1.1?from=1.1");
  const xpBefore = (await progress(page)).xp;
  await returnToLesson(page);
  await expect(page.locator(".kind")).toHaveText("Exercise");
  await expect(page.getByText("✔ solved", { exact: true })).toBeVisible();
  await page.locator("#nextbtn").click();
  await finishRecap(page);
  expect((await progress(page)).xp).toBe(xpBefore);
  await page.goto("/#/ex/1.1?from=1.1");
  await expect(page.getByRole("link", { name: /^Continue: Lesson 1\.2 / })).toBeVisible();
});

for (const origin of ["1.2", "999.1"]) {
  test(`an unrelated or missing origin (${origin}) falls back to the exercise's lesson`, async ({ page }) => {
    await startAtExercise(page);
    await page.goto(`/#/ex/1.1?from=${origin}`);
    await expect(page.getByRole("link", { name: "Lesson 1.1", exact: true })).toBeVisible();
    await passExercise(page);
    await returnToLesson(page);
    await expect(page.locator(".kind")).toHaveText("Recap");
  });
}
