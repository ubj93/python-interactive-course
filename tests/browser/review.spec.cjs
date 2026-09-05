const {test: base, expect} = require('playwright/test');
const KEY = 'cpe-course-progress-v1';
const test = base.extend({page: async ({page}, use) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.route('**/*', route => new URL(route.request().url()).hostname === '127.0.0.1' ? route.continue() : route.abort());
  await page.route('**/worker.js', route => route.fulfill({contentType:'application/javascript',body:`self.onmessage=({data})=>{if(data.type==='boot')self.postMessage({type:'ready'});if(data.type==='run')setTimeout(()=>self.postMessage({type:'result',id:data.id,result:{stdout:'Diagnostic status',tests:[{name:'answer',status:data.files['exercise.py'].includes('FAIL')?'fail':'pass'}]}}),700);};`}));
  await use(page);
  expect(errors).toEqual([]);
}});
async function saved(page) {return page.evaluate(key => JSON.parse(localStorage.getItem(key)), KEY);}
async function newReview(page, id) {
  await page.goto('/#/review');
  await page.locator('#review-manual').selectOption(id);
  await page.locator('#review-new').click();
  await expect(page.locator('#review-code')).toBeVisible();
}

test('exercise reflection, separate scratch work, reload and fresh round', async ({page}) => {
  await page.goto('/#/ex/1.1');
  await page.locator('#code').fill('# saved ordinary answer');
  await page.locator('#runbtn').click();
  await expect(page.locator('#exercise-review-save')).toBeVisible();
  await page.locator('#exercise-review-confidence').selectOption('needs_review');
  await page.locator('#exercise-review-note').fill('Check empty hostnames');
  await page.locator('#exercise-review-save').click();
  await expect(page.locator('#exercise-review-status')).toContainText('Next review:');
  const original = await saved(page);
  await newReview(page, '1.1');
  await expect(page.locator('#review-code')).not.toHaveValue('# saved ordinary answer');
  await page.locator('#review-code').fill('# FAIL first review attempt');
  await page.locator('#review-run').click();
  await expect(page.locator('#review-outcome')).toContainText('1 attempt(s) · latest outcome: not passed');
  await page.locator('#review-code').fill('# my review draft');
  await page.locator('#review-run').click();
  await expect(page.locator('#review-results')).toContainText('Review tests passed');
  await expect(page.locator('#review-results')).toContainText('Diagnostic status');
  await expect(page.locator('#review-outcome')).toContainText('2 attempt(s) · latest outcome: passed');
  await page.reload();
  await expect(page.locator('#review-code')).toHaveValue('# my review draft');
  await page.locator('#round-review-confidence').selectOption('confident');
  await page.locator('#round-review-note').fill('Remembered the shape');
  await page.locator('#round-review-interval').selectOption('30');
  await page.locator('#round-review-save').click();
  await expect(page.locator('#round-review-status')).toContainText('Next review:');
  await page.reload();
  await expect(page.locator('#round-review-interval')).toHaveValue('30');
  await page.locator('#round-review-note').fill('Edited takeaway');
  await page.locator('#round-review-save').click();
  await expect(page.locator('#round-review-status')).toContainText('Next review:');
  const reviewed = await saved(page);
  expect(reviewed.xp).toBe(original.xp);
  expect(reviewed.solved).toEqual(original.solved);
  expect(reviewed.attempts).toEqual(original.attempts);
  expect(reviewed.hints).toEqual(original.hints);
  expect(reviewed.review_queue.items['1.1'].interval_days).toBe(30);
  expect(reviewed.review_queue.items['1.1'].sources).toEqual(['exercise','review']);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await newReview(page, '1.1');
  await expect(page.locator('#review-code')).not.toHaveValue('# my review draft');
  const fresh = await saved(page);
  expect(fresh.review_session.id).not.toBe(reviewed.review_session.id);
  expect(fresh.review_history[0].drafts['1.1']).toBe('# my review draft');
  await page.goto('/#/ex/1.1');
  await expect(page.locator('#code')).toHaveValue('# saved ordinary answer');
});

test('diagnostic confidence shares the queue and quota failure preserves both', async ({page}) => {
  await page.goto('/#/diagnostic/1.2');
  await page.locator('#diagnostic-note').fill('Watch the edge case');
  expect((await saved(page)).review_queue).toBeUndefined();
  await page.locator('#diagnostic-confidence').selectOption('needs_review');
  await page.evaluate(() => {saveExerciseReflection('1.2','needs_review','Watch the edge case',30);P.review_queue.items['1.2'].next_review='2026-12-01';saveProgress();});
  await page.locator('#diagnostic-note').fill('Watch the edge case again');
  const before = await saved(page);
  expect(before.review_queue.items['1.2'].mistake_note).toBe('Watch the edge case again');
  expect(before.review_queue.items['1.2'].interval_days).toBe(30);
  expect(before.review_queue.items['1.2'].next_review).toBe('2026-12-01');
  await page.evaluate(() => {Storage.prototype.setItem = function() {throw Error('quota');};});
  await page.locator('#diagnostic-confidence').selectOption('confident');
  await expect(page.locator('#diagnostic-save')).toContainText('could not be saved');
  expect(await saved(page)).toEqual(before);
  await page.reload();
  await page.goto('/#/review');
  await expect(page.getByText('Watch the edge case')).toBeVisible();
  await page.locator('#review-manual').selectOption('1.2');
  await page.locator('#review-new').click();
  await expect(page.locator('#review-code')).toBeVisible();
  await page.locator('#review-help').click();
  const after = await saved(page);
  expect(after.xp).toBe(before.xp);
  expect(after.hints).toEqual(before.hints);
  expect(Object.keys(after.review_queue.items)).toEqual(['1.2']);
});

test('late grading cannot attach to a newly started review round', async ({page}) => {
  await newReview(page, '1.1');
  await page.locator('#review-code').fill('# submitted to old round');
  await page.locator('#review-run').click();
  await page.getByRole('link', {name:'← Review queue and round summary'}).click();
  await page.locator('#review-manual').selectOption('1.2');
  await page.locator('#review-new').click();
  await expect(page.locator('#review-code')).toBeVisible();
  await expect(page.locator('#toast')).toContainText('The review round changed');
  const progress = await saved(page);
  expect(progress.review_session.ids).toEqual(['1.2']);
  expect(progress.review_session.attempts).toEqual([]);
  expect(progress.review_history[0].drafts['1.1']).toBe('# submitted to old round');
  expect(progress.xp).toBe(0);
});

test('failed fresh-round save preserves current round and drafts', async ({page}) => {
  await newReview(page, '1.1');
  await page.locator('#review-code').fill('# keep this draft');
  await page.getByRole('link', {name:'← Review queue and round summary'}).click();
  const before = await saved(page);
  await page.evaluate(() => {Storage.prototype.setItem = function() {throw Error('quota');};});
  await page.locator('#review-manual').selectOption('1.2');
  await page.locator('#review-new').click();
  await expect(page.locator('#toast')).toContainText('could not be saved');
  expect(await saved(page)).toEqual(before);
  await page.getByRole('link', {name:'Resume review'}).click();
  await page.reload();
  await expect(page.locator('#review-code')).toHaveValue('# keep this draft');
});
