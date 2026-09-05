// Exercise the actual browser progress functions with isolated in-memory storage.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const page = fs.readFileSync(path.join(__dirname, "../docs/index.html"), "utf8");
const start = page.indexOf("function localDay(");
const end = page.indexOf("function dailyExercise(", start);
assert.ok(start >= 0 && end > start, "browser progress functions must be present");
const NOW = Date.parse("2026-09-05T00:30:00.000Z");
class Clock extends Date {
  constructor(...args) { super(...(args.length ? args : [NOW])); }
  static now() { return NOW; }
}
const memory = new Map();
const localStorage = { getItem: (key) => memory.get(key) || null, setItem: (key, value) => memory.set(key, value) };
const ex = { id: "1.1", kyu: 5, xp: 20, time_limit_min: 5 };
const newYork = process.env.TZ === "America/New_York";
vm.runInNewContext(page.slice(start, end) + `
  const expectedDay = newYork ? "2026-09-04" : "2026-09-05";
  const legacy = newYork ? "2026-09-04T20:29:00" : "2026-09-05T09:29:00";
  assert.equal(today(), expectedDay);
  assert.equal(nowIso(), "2026-09-05T00:30:00.000Z");
  assert.equal(timestampDay("2026-03-08T04:30:00Z"), newYork ? "2026-03-07" : "2026-03-08");
  assert.equal(timestampDay(newYork ? "0001-01-01T00:30:00Z" : "9999-12-31T23:30:00Z"), null);
  if (newYork) {
    assert.equal(parseTimestamp("2026-03-08T02:30:00"), null);
    assert.equal(parseTimestamp("2026-11-01T01:30:00").toISOString(), "2026-11-01T05:30:00.000Z");
  }
  for (const value of ["2026-09-05T00:29:00.000Z", "2026-09-04T20:29:00-04:00", legacy]) {
    assert.equal(parseTimestamp(value).getTime(), NOW - 60000);
    assert.equal(elapsedSeconds(value), 60);
    const saved = { xp: 42, solved: { old: { passed_at: value, xp: 42 } }, opened: { [ex.id]: value }, days: ["2026-09-03"], custom: { keep: true } };
    localStorage.setItem(STORE_KEY, JSON.stringify(saved));
    P = loadProgress();
    const result = recordRun(ex, true);
    assert.equal(result.xp, 28);
    P = loadProgress();
    assert.equal(P.xp, 70);
    assert.equal(JSON.stringify(P.solved.old), JSON.stringify(saved.solved.old));
    assert.equal(P.opened[ex.id], value);
    assert.equal(P.custom.keep, true);
    assert.equal(P.solved[ex.id].seconds, 60);
    assert.equal(P.solved[ex.id].passed_at, "2026-09-05T00:30:00.000Z");
    assert.equal(solvedToday(), 2);
    assert.equal(recordRun(ex, true).xp, 0);
    assert.ok(P.days.includes(expectedDay));
    assert.equal(P.badges.first_blood, expectedDay);
  }
  for (const value of [null, 0, [], {}, "", "bad", "2026-09-05", "2026-02-30T00:00:00Z", "2026-09-05T24:00:00Z", "2026-09-05T00:00:00+24:00", "2026-09-05T00:00:00+01:99"]) {
    assert.equal(parseTimestamp(value), null);
    assert.equal(elapsedSeconds(value), null);
  }
  for (const value of [null, "", 17, {}, "bad", "2026-09-05T00:31:00Z"]) {
    P = blankProgress();
    P.opened[ex.id] = value;
    const result = recordRun(ex, true);
    assert.ok(P.solved[ex.id]);
    assert.equal(result.xp, 25);
    assert.equal(P.solved[ex.id].seconds, null);
    assert.equal(P.badges.speed_demon, undefined);
  }
  P = blankProgress();
  P.solved = { invalid: { passed_at: 17 }, boundary: { passed_at: "2026-09-05T00:20:00Z" } };
  assert.equal(solvedToday(), 1);
  P.days = ["2026-09-02", "2026-09-03"];
  assert.equal(streak(), newYork ? 2 : 0);
  P = blankProgress();
  P.daily[expectedDay] = { id: ex.id, done: false };
  assert.equal(recordRun(ex, true).daily, 5);
  assert.equal(P.daily[expectedDay].done, true);
`, { assert, Date: Clock, localStorage, STORE_KEY: "test-progress", ALL: [ex], DATA: {}, ex, NOW, newYork });
console.log(`Browser timestamp and persistence checks passed in ${process.env.TZ}`);
