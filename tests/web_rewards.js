const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../docs/index.html'), 'utf8');
const start = source.indexOf('function localDay(');
const end = source.indexOf('// ------------------------------------------------------------------ rendering helpers', start);
assert.ok(start > 0 && end > start);
const memory = new Map();
const localStorage = {getItem: key => memory.get(key) || null, setItem: (key, value) => memory.set(key, value)};
vm.runInNewContext(source.slice(start, end) + `
  assert.equal(recordCard('1.1', 'card-first', true, true), 1);
  assert.equal(recordCard('1.1', 'card-first', true, true), 0);
  P.cards = {}; saveProgress(); P = loadProgress();
  assert.equal(recordCard('1.1', 'card-first', true, true), 0);
  assert.equal(P.xp, 1);
  P = blankProgress();
  recordCard('1.1', 'card-first', true, false);
  P.cards = {}; saveProgress(); P = loadProgress();
  assert.equal(recordCard('1.1', 'card-first', true, true), 0);
  assert.equal(P.xp, 0);
  for (const alreadySolved of [false, true]) {
    P = blankProgress();
    for (let d = 1; d < 7; d++) { const date = new Date(); date.setDate(date.getDate()-d); P.days.push(localDay(date)); }
    if (alreadySolved) { P.solved['1.1'] = {passed_at:'2026-01-01T00:00:00.000Z',xp:9}; P.xp = 9; }
    const result = recordRun({id:'1.1'}, alreadySolved);
    assert.deepEqual(Array.from(result.badges), ['week_streak']);
    assert.equal(P.badges.first_blood, undefined);
    assert.equal(result.xp, 0);
    assert.equal(P.xp, alreadySolved ? 9 : 0);
  }
  // Imported CLI history has no replay state, but its award cannot repeat.
  P = migrateCardProgress(Object.assign(blankProgress(), {xp: 71, card_reward_history: {'1.1:0': true}}));
  assert.equal(recordCard('1.1', 'card-first', true, true), 0);
  assert.equal(P.xp, 71);
  // Legacy state may include retries after a rewarded first answer.
  P = migrateCardProgress(Object.assign(blankProgress(), {xp: 71, cards: {'1.1:0': {done:true, correct:true, tries:5}}}));
  cardRewardHistory(); P.cards = {};
  assert.equal(recordCard('1.1', 'card-first', true, true), 0);
  assert.equal(P.xp, 71);
  P = blankProgress();
  for (let d = 1; d < 30; d++) { const date = new Date(); date.setDate(date.getDate()-d); P.days.push(localDay(date)); }
  recordCard('1.1', 'card-first', false);
  assert.ok(P.badges.week_streak);
  assert.ok(P.badges.month_streak);
  assert.equal(P.badges.first_blood, undefined);
  assert.equal(P.xp, 0);
`, {assert, Date, localStorage, STORE_KEY:'test-rewards', DATA:{parts:[],card_xp:1,legacy_card_ids:{'1.1:0':'card-first'}}, ALL:[], BY_ID:{}});
console.log('Browser replay and streak reward regressions passed');
