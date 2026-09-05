// Test the shipped session engine and interview view with disposable browser state.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const imported = JSON.parse(fs.readFileSync(0, "utf8"));
const page = fs.readFileSync(path.join(__dirname, "../docs/index.html"), "utf8");
const progressStart = page.indexOf("function localDay(");
const progressEnd = page.indexOf("function dailyExercise(", progressStart);
const viewStart = page.indexOf("let interviewTimer = null;");
const viewEnd = page.indexOf("// ------------------------------------------------------------------ router", viewStart);
assert.ok(progressStart >= 0 && progressEnd > progressStart && viewStart >= 0 && viewEnd > viewStart);
const BASE = Date.parse("2026-09-05T12:00:00.000Z");
let now = BASE;
class Clock extends Date {
  constructor(...args) { super(...(args.length ? args : [now])); }
  static now() { return now; }
}
const clock = { set: (value) => { now = value; } };
const memory = new Map();
const storage = {
  fail: false,
  getItem: (key) => memory.get(key) || null,
  setItem(key, value) { if (this.fail) throw new Error("storage full"); memory.set(key, value); },
  removeItem: (key) => memory.delete(key),
};
const ex1 = { id: "9.1", title: "Repeat exercise", kyu: 5, xp: 20, time_limit_min: 1, part: { num: 9 } };
const ex2 = { ...ex1, id: "9.2", title: "Second exercise" };
const elements = new Map(), timers = new Map();
let html = "", nextTimer = 1;
const app = {
  get innerHTML() { return html; },
  set innerHTML(value) {
    html = value; elements.clear();
    for (const match of value.matchAll(/\bid="([^"]+)"/g)) elements.set("#" + match[1], { textContent: "", className: "", onclick: null });
  },
};
const sandbox = { refresherMock: () => null, assert, Date: Clock, localStorage: storage, storage, memory, BASE, clock, imported, app, ALL: [ex1, ex2], BY_ID: { "9.1": ex1, "9.2": ex2 }, ex1, ex2, DATA: {}, STORE_KEY: "test-progress", LEGACY_INTERVIEW_KEY: "test-old-interview", $: (selector) => elements.get(selector) || null, esc: (value) => String(value).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"), toast: () => {}, renderHeader: () => {}, setInterval: (fn) => { const id = nextTimer++; timers.set(id, fn); return id; }, clearInterval: (id) => timers.delete(id), timers };
const script = page.slice(progressStart, progressEnd) + page.slice(viewStart, viewEnd) + `
  function reset() { P = blankProgress(); memory.clear(); storage.fail = false; clock.set(BASE); }
  assert.equal(JSON.stringify(sessionSummary(imported)), JSON.stringify(imported.summary));
  reset();
  P.xp = 100; P.solved[ex1.id] = { passed_at: "2026-09-04T12:00:00Z", xp: 100 };
  const oldSolved = JSON.stringify(P.solved);
  assert.ok(beginInterview([ex1.id], 1));
  assert.equal(sessionSummary(activeInterview()).passed, 0);
  viewInterview();
  assert.ok(app.innerHTML.includes("0/1 passed"));
  assert.ok(app.innerHTML.includes("Not passed"));
  assert.equal(timers.size, 1);
  clock.set(BASE + 30000);
  assert.equal(recordRun(ex1, true).xp, 0);
  assert.equal(P.xp, 100);
  assert.equal(JSON.stringify(P.solved), oldSolved);
  clock.set(BASE + 300000);
  recordRun(ex1, false);
  P = loadProgress();
  viewInterview();
  assert.ok($("#interviewclock").textContent.includes("Time is up"));
  assert.ok(app.innerHTML.includes("1/1 on time"));
  $("#finish").onclick();
  assert.equal(P.interview, null);
  assert.ok(P.badges.interviewer);
  assert.equal(timers.size, 0);
  assert.ok(app.innerHTML.includes("Last round: 1/1 passed"));
  const frozen = JSON.stringify(P.last_interview);
  recordRun(ex1, true);
  P = loadProgress();
  viewInterview();
  assert.equal(JSON.stringify(P.last_interview), frozen);
  assert.ok(beginInterview([ex1.id], 1));
  assert.equal(JSON.stringify(P.last_interview), frozen);
  assert.equal(sessionSummary(activeInterview()).passed, 0);
  assert.equal(recordSessionAttempt(P.last_interview, ex1.id, true), false);

  reset(); beginInterview([ex1.id, ex2.id], 1);
  clock.set(BASE + 60000); recordRun(ex1, true);
  clock.set(BASE + 60001); recordRun(ex2, true);
  clock.set(BASE + 80000); recordRun(ex1, true);
  assert.equal(sessionSummary(activeInterview()).passed, 2);
  assert.equal(sessionSummary(activeInterview()).on_time, 1);
  assert.equal(sessionSummary(activeInterview()).results[0].attempts, 2);
  clock.set(BASE + 90000); assert.ok(completeInterview());
  assert.equal(P.badges.interviewer, undefined);
  const exported = JSON.parse(JSON.stringify(P.last_interview));
  assert.equal(exported.summary.results[0].passed_at, "2026-09-05T12:01:00.000Z");

  reset(); beginInterview([ex1.id], 1);
  const before = JSON.stringify(P.interview);
  assert.equal(recordSessionAttempt(P.interview, ex2.id, true), false);
  assert.equal(recordSessionAttempt(P.interview, ex1.id, true, "2026-09-05T11:59:59Z"), false);
  assert.equal(JSON.stringify(P.interview), before);
  assert.equal(beginInterview([], 1), false);
  assert.equal(beginInterview([ex1.id], 0), false);
  assert.equal(beginInterview([ex1.id], Infinity), false);
  assert.equal(JSON.stringify(P.interview), before);
  const good = P.interview;
  for (const value of [null, [], 17, {}, {...good, ids: []}, {...good, ids: [ex1.id, ex1.id]}, {...good, ids: [null]}, {...good, started: "bad"}, {...good, deadline: good.started}, {...good, attempts: null}, {...good, status: []}, {...good, kind: 7}, {...good, status: "finished", finished_at: null}, {...good, version: true}, {...good, version: 999}]) {
    assert.equal(normalizeSession(value), null);
    assert.equal(sessionSummary(value), null);
    assert.equal(finishSession(value), null);
  }
  P.interview = { ids: [], started: "bad", deadline: "bad" };
  const invalid = JSON.stringify(P.interview);
  recordRun(ex1, true);
  assert.equal(JSON.stringify(P.interview), invalid);
  viewInterview(); assert.ok(app.innerHTML.includes("invalid saved data"));
  assert.ok(beginInterview(["9.99"], 1));
  viewInterview(); assert.ok(app.innerHTML.includes("unavailable in this catalog"));

  reset();
  const legacy = { ids: [ex1.id], started: BASE, deadline: BASE + 60000, before: [ex1.id], custom: "preserve" };
  storage.setItem(STORE_KEY, JSON.stringify({ xp: 100, solved: { [ex1.id]: { passed_at: "2026-09-05T12:00:00Z", xp: 100 } } }));
  storage.setItem(LEGACY_INTERVIEW_KEY, JSON.stringify(legacy));
  storage.fail = true;
  P = loadProgress();
  assert.equal(P.interview, null);
  assert.ok(storage.getItem(LEGACY_INTERVIEW_KEY));
  storage.fail = false;
  P = loadProgress();
  assert.equal(P.xp, 100);
  assert.equal(P.interview.custom, "preserve");
  assert.equal(P.interview.started, "2026-09-05T12:00:00.000Z");
  assert.equal(storage.getItem(LEGACY_INTERVIEW_KEY), null);
  assert.equal(sessionSummary(activeInterview()).passed, 0);
  viewInterview(); assert.ok(app.innerHTML.includes("Only fresh runs since migration count"));
  clock.set(BASE + 10000); recordRun(ex1, true);
  storage.fail = true;
  const activeBeforeFailure = JSON.stringify(P.interview);
  assert.equal(completeInterview(), false);
  assert.equal(JSON.stringify(P.interview), activeBeforeFailure);
  assert.equal(P.last_interview, null);
  storage.fail = false;
  assert.ok(completeInterview());
  storage.setItem(LEGACY_INTERVIEW_KEY, JSON.stringify(legacy));
  P = loadProgress();
  assert.equal(P.interview, null); // a stale legacy key cannot resurrect a finished round
  assert.equal(P.last_interview.summary.passed, 1);
  P = Object.assign(blankProgress(), { legacy_interview_migrated: true }); saveProgress();
  P = loadProgress(); assert.equal(P.interview, null);

  reset(); beginInterview([ex1.id], 1);
  const submittedRound = P.interview.id;
  clock.set(BASE + 1000); beginInterview([ex1.id], 1);
  const replacement = P.interview.id;
  assert.notEqual(submittedRound, replacement);
  const previousRound = JSON.stringify(P.last_interview);
  recordRun(ex1, false, submittedRound);
  assert.equal(P.attempts[ex1.id], 1); // ordinary practice still records once
  assert.equal(sessionSummary(activeInterview()).results[0].attempts, 0);
  assert.equal(JSON.stringify(P.last_interview), previousRound);
  recordRun(ex1, true, replacement);
  assert.equal(sessionSummary(activeInterview()).passed, 1);

  reset(); beginInterview([ex1.id], 1);
  recordRun(ex1, false, null); // submitted outside a round
  assert.equal(sessionSummary(activeInterview()).results[0].attempts, 0);
  clock.set(BASE + 10000); recordRun(ex1, true);
  const beforeRollback = JSON.stringify(P);
  clock.set(BASE + 5000);
  assert.equal(completeInterview(), false);
  assert.equal(beginInterview([ex1.id], 1), false);
  assert.equal(JSON.stringify(P), beforeRollback);
  clock.set(BASE - 1000);
  assert.equal(beginInterview([ex1.id], 1), false);
  assert.equal(JSON.stringify(P), beforeRollback);

  reset();
  const held = ALL.splice(0); viewInterview(); $("#start").onclick();
  assert.equal(P.interview, null);
  ALL.push(...held);
  viewInterview(); $("#start").onclick();
  assert.equal(P.interview.ids.length, 2);
  clock.set(BASE + 2700001);
  for (const update of timers.values()) update();
  assert.ok($("#interviewclock").textContent.includes("Time is up"));
  JSON.stringify(exported);
`;
const exported = vm.runInNewContext(script, sandbox);
process.stdout.write(exported);
