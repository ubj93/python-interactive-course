// Opt-in: this check loads the real Pyodide runtime from the app's public CDN.
const { test, expect } = require("playwright/test");
const { execFileSync } = require("node:child_process");
const path = require("node:path");
const fs = require("node:fs");
const root = path.resolve(__dirname, "../..");

test("public generalization cases pass references and reject plausible mistakes in real Python", async ({ page }) => {
  test.skip(process.env.COURSE_REAL_BROWSER_TESTS !== "1", "Set COURSE_REAL_BROWSER_TESTS=1 to load the real Python runtime");
  test.setTimeout(120000);
  const cases = JSON.parse(execFileSync(process.env.PYTHON || "python3", [path.join(root, "tests/generalization_cases.py")], {encoding: "utf8"}));
  const harness = fs.readFileSync(path.join(root, "course/harness.py"), "utf8");
  // Use the shipped UTF-8 page, public bundle and worker; never mock Python.
  await page.goto("/");
  const bundle = await page.evaluate(() => ({harness: window.COURSE_DATA.harness,
    tests: Object.fromEntries(window.COURSE_DATA.parts.flatMap(part => part.exercises.map(ex => [ex.dir, ex.tests])))}));
  expect(bundle.harness, "Regenerate docs/exercises.js before this browser check").toBe(harness);
  for (const candidate of cases) {
    expect(candidate.files["test_exercise.py"].startsWith(bundle.tests[candidate.slug]), "Bundled tests must match the public source: " + candidate.name).toBe(true);
  }
  const results = await page.evaluate(async ({ cases, harness }) => {
    const worker = new Worker("/worker.js");
    function message(payload, type) {
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => { worker.terminate(); reject(Error("Real Python worker timed out")); }, type === "ready" ? 90000 : 5000);
        worker.onmessage = ({data}) => {
          if (data.type === type) { clearTimeout(timer); resolve(data); }
          else if (data.type === "error") { clearTimeout(timer); reject(Error(data.error)); }
        };
        worker.onerror = event => { clearTimeout(timer); reject(Error(event.message)); };
        worker.postMessage(payload);
      });
    }
    try {
      const coldStart = performance.now();
      await message({type: "boot"}, "ready");
      const bootMs = performance.now() - coldStart, runs = [];
      for (let index = 0; index < cases.length; index++) {
        const candidate = cases[index], started = performance.now();
        const {result} = await message({type: "run", id: index, slug: candidate.slug, files: candidate.files, harness}, "result");
        runs.push({name: candidate.name, expected: candidate.passes, ms: performance.now() - started, result});
      }
      return {bootMs, runs};
    } finally { worker.terminate(); }
  }, {cases, harness});
  console.log(`Real Python boot: ${results.bootMs.toFixed(0)}ms`);
  for (const run of results.runs) {
    const result = run.result, failures = result.tests.filter(row => row.status !== "pass");
    expect(result.import_error, run.name).toBeNull();
    expect(result.tests.map(row => row.name), run.name).toContain("test_generalization_seeded");
    if (!run.name.includes("full suite")) expect(result.tests, run.name).toHaveLength(1);
    expect(failures.length === 0, run.name + ": " + JSON.stringify(failures)).toBe(run.expected);
    if (!run.expected) {
      expect(failures[0].status, run.name).toBe("fail");
      expect(failures[0].message.length, run.name).toBeLessThan(400);
    }
    console.log(`${run.name}: ${run.ms.toFixed(1)}ms${failures.length ? "; " + failures[0].message : ""}`);
  }
});
