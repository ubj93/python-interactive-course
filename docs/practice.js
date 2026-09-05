// Untimed practice state mirrors course/practice.py. Loaded before the main app;
// its progress, timestamp, catalog and rendering helpers are used only on calls.
const DIAGNOSTIC_IDS = ["1.2", "1.3", "2.1", "2.2", "3.1", "5.1"];
const PRACTICE_SESSION_ID = /^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$/;
function practiceObject(value) { return value !== null && typeof value === "object" && !Array.isArray(value); }
function practiceClone(value) { return JSON.parse(JSON.stringify(value)); }
function practiceTimestamp(value) {
  const date = parseTimestamp(value);
  return date && date.getUTCFullYear() >= 1 && date.getUTCFullYear() <= 9999 ? date : null;
}
function normalizePractice(value) {
  if (!practiceObject(value) || value.version !== 1 || typeof value.id !== "string" || value.id.match(PRACTICE_SESSION_ID)?.[0] !== value.id || typeof value.kind !== "string" || !value.kind) return null;
  const ids = value.ids, started = practiceTimestamp(value.started);
  if (!Array.isArray(ids) || !ids.length || ids.some(id => typeof id !== "string" || id.match(/^[0-9]+\.[0-9]+$/)?.[0] !== id) || new Set(ids).size !== ids.length || !started) return null;
  if (value.last_exercise != null && !ids.includes(value.last_exercise)) return null;
  if (!Array.isArray(value.attempts) || !practiceObject(value.reflections) || !practiceObject(value.drafts)) return null;
  const state = practiceClone(value); state.started = started.toISOString(); state.last_exercise = value.last_exercise ?? null;
  for (const attempt of state.attempts) {
    if (!practiceObject(attempt) || !ids.includes(attempt.exercise_id) || typeof attempt.passed !== "boolean") return null;
    const at = practiceTimestamp(attempt.at); if (!at || at < started) return null;
    attempt.at = at.toISOString();
  }
  for (const [id, reflection] of Object.entries(state.reflections)) {
    if (!ids.includes(id) || !practiceObject(reflection) || ![null, undefined, "confident", "needs_review"].includes(reflection.confidence)) return null;
    if (reflection.mistake_note !== undefined && (typeof reflection.mistake_note !== "string" || [...reflection.mistake_note].length > 500)) return null;
    if (reflection.help_at != null) {
      const at = practiceTimestamp(reflection.help_at); if (!at || at < started) return null;
      reflection.help_at = at.toISOString();
    }
  }
  if (Object.entries(state.drafts).some(([id, code]) => !ids.includes(id) || typeof code !== "string")) return null;
  return state;
}
function diagnosticState(value = P.diagnostic) {
  const state = normalizePractice(value);
  return state && state.kind === "diagnostic" && JSON.stringify(state.ids) === JSON.stringify(DIAGNOSTIC_IDS) ? state : null;
}
function practiceSummary(value) {
  const state = normalizePractice(value); if (!state) return null;
  return state.ids.map(id => {
    const attempts = state.attempts.filter(a => a.exercise_id === id);
    const latest = attempts.reduce((best, a) => !best || a.at >= best.at ? a : best, null);
    const reflection = state.reflections[id] || {};
    return {id, outcome: !latest ? "not_attempted" : latest.passed ? "passed" : "not_passed", attempts: attempts.length,
      confidence: reflection.confidence || null, mistake_note: reflection.mistake_note || "", help_used: Boolean(reflection.help_at)};
  });
}
function diagnosticSummary(value = P.diagnostic) { const state = diagnosticState(value); return state ? practiceSummary(state) : null; }
function saveDiagnostic(state, history, queue) {
  const previous = P;
  P = {...P, diagnostic: state};
  if (history !== undefined) P.diagnostic_history = history;
  if (queue !== undefined) P.review_queue = queue;
  if (!saveProgress()) { P = previous; throw new Error("Diagnostic could not be saved. Export your progress and free browser storage before continuing."); }
  return practiceClone(state);
}
function beginDiagnostic(fresh = false) {
  if (DIAGNOSTIC_IDS.some(id => !BY_ID[id])) throw new Error("The diagnostic exercises are unavailable in this catalog.");
  const state = diagnosticState();
  if (!fresh && P.diagnostic != null) {
    if (!state) throw new Error("Saved diagnostic data is invalid. Export your progress, or start a new round to archive it.");
    return state;
  }
  const history = practiceClone(Array.isArray(P.diagnostic_history) ? P.diagnostic_history : P.diagnostic_history === undefined ? [] : [P.diagnostic_history]);
  if (P.diagnostic != null) history.push(practiceClone(P.diagnostic));
  const id = window.crypto && window.crypto.randomUUID ? window.crypto.randomUUID() : Date.now().toString(36) + "-" + Math.random().toString(36).slice(2);
  return saveDiagnostic({version: 1, id, kind: "diagnostic", started: nowIso(), ids: [...DIAGNOSTIC_IDS], attempts: [], reflections: {}, drafts: {}, last_exercise: null}, history);
}
function updateDiagnostic(exId, action, sessionId, fields = {}) {
  const state = diagnosticState();
  if (!state || state.id !== sessionId) throw new Error("The diagnostic round changed; this result was not added to the new round.");
  if (!state.ids.includes(exId)) throw new Error("Unknown diagnostic exercise.");
  const priorConfidence = (state.reflections[exId] || {}).confidence;
  const at = nowIso();
  if (parseTimestamp(at) < parseTimestamp(state.started)) throw new Error("The clock is earlier than this diagnostic round.");
  if (action === "attempt") {
    if (typeof fields.passed !== "boolean") throw new Error("A diagnostic attempt needs a test outcome.");
    state.attempts.push({exercise_id: exId, at, passed: fields.passed});
  } else if (action === "reflect") {
    if (![null, "confident", "needs_review"].includes(fields.confidence) || typeof fields.note !== "string" || [...fields.note].length > 500) throw new Error("Choose a confidence and keep the note to 500 characters.");
    state.reflections[exId] = {...(state.reflections[exId] || {}), confidence: fields.confidence, mistake_note: fields.note};
  } else if (action === "help") {
    state.reflections[exId] = {...(state.reflections[exId] || {}), help_at: (state.reflections[exId] || {}).help_at || at};
  } else if (!["open", "draft"].includes(action)) throw new Error("Unknown diagnostic action.");
  if (fields.code !== undefined) {
    if (typeof fields.code !== "string") throw new Error("The diagnostic draft must be text.");
    state.drafts[exId] = fields.code;
  }
  state.last_exercise = exId;
  const queue = action === "reflect" && fields.confidence != null ? reflectReviewQueue(P.review_queue, exId, fields.confidence, fields.note, null, "diagnostic", new Date(), priorConfidence === fields.confidence) : undefined;
  return saveDiagnostic(state, undefined, queue);
}
function diagnosticLesson(id) { return LESSONS.find(lesson => lesson.cards.some(card => card.kind === "exercise" && card.exercise_id === id)); }
function diagnosticLessonLink(id) {
  const lesson = diagnosticLesson(id);
  return lesson ? `<a href="#/learn/${lesson.id}">Revisit ${esc(lesson.title)}</a>` : "";
}
function diagnosticRows(state, archived = false) {
  const rows = diagnosticSummary(state);
  if (!rows) return '<p class="muted">Unsupported archived round. Its original data remains in your progress export.</p>';
  return `<p>${rows.filter(row => row.attempts).length}/6 attempted · ${rows.filter(row => row.confidence).length}/6 reflections recorded</p><div class="list">` + rows.map(row => {
    const ex = BY_ID[row.id];
    return `<div class="item"><span class="t"><b>${row.id} ${esc(ex ? ex.title : "Exercise unavailable")}</b><small>${esc(row.outcome.replaceAll("_", " "))} · ${row.attempts} attempt(s) · confidence: ${esc((row.confidence || "not recorded").replaceAll("_", " "))}${row.help_used ? " · help used" : ""}</small>${row.mistake_note ? `<p>${esc(row.mistake_note)}</p>` : ""}<div class="row">${archived ? "" : `<a class="btn small secondary" href="#/diagnostic/${row.id}">${row.attempts ? "Revisit exercise" : "Try exercise"}</a>`}${diagnosticLessonLink(row.id)}</div></span></div>`;
  }).join("") + "</div>";
}
function diagnosticError(error) { toast(error.message || String(error)); }
function viewDiagnostic(exId) {
  let state;
  try { state = beginDiagnostic(); }
  catch (error) {
    app.innerHTML = `<div class="card"><h1>Fundamentals diagnostic</h1><p>${esc(error.message || error)}</p><div class="row"><a class="btn secondary" href="#/profile">Export progress</a><button class="btn" id="diagnostic-new">Start a new round</button></div></div>`;
    $("#diagnostic-new").onclick = () => { try { beginDiagnostic(true); viewDiagnostic(); } catch (e) { diagnosticError(e); } };
    return;
  }
  if (exId && state.ids.includes(exId) && BY_ID[exId]) return viewDiagnosticExercise(state, BY_ID[exId]);
  const resume = state.last_exercise || state.ids.find(id => !state.attempts.some(a => a.exercise_id === id)) || state.ids[0];
  app.innerHTML = `<div class="card"><h1>Fundamentals diagnostic</h1><p>Six untimed problems to find the Python topics you want to revisit. Try each problem before guidance; help is always available. These attempts and drafts are separate from course completion and XP.</p><p>Test outcome and confidence are separate. Use a short note to remember what tripped you up, then choose the lessons that would help.</p><div class="row"><a class="btn" href="#/diagnostic/${resume}">Resume diagnostic</a><button class="btn secondary" id="diagnostic-new">Start a new round</button><a href="#/">Dashboard</a></div></div><div class="card"><h2>This round</h2>${diagnosticRows(state)}</div><div class="card"><h2>Earlier rounds</h2>${Array.isArray(P.diagnostic_history) && P.diagnostic_history.length ? P.diagnostic_history.map((old, index) => `<details><summary>Round ${index + 1}${diagnosticState(old) ? " · " + esc(old.started) : " · unsupported data"}</summary>${diagnosticRows(old, true)}</details>`).join("") : '<p class="muted">Starting a new round keeps earlier summaries and drafts in your progress export.</p>'}</div>`;
  $("#diagnostic-new").onclick = () => { try { beginDiagnostic(true); viewDiagnostic(); } catch (error) { diagnosticError(error); } };
}
function diagnosticTestOutcome(result) {
  const tests = (result.tests || []).filter(test => test.status !== "skip");
  return !result.timed_out && !result.import_error && !result.crashed && tests.length > 0 && tests.every(test => test.status === "pass");
}
function diagnosticResultHtml(result, label = "Diagnostic") {
  const passed = diagnosticTestOutcome(result);
  let html = `<div class="banner ${passed ? "pass" : "fail"}">${esc(label)} tests ${passed ? "passed" : "not yet passing"}</div>`;
  if (result.timed_out) html += '<p>The run timed out. Check for an infinite loop.</p>';
  if (result.import_error || result.crashed) html += `<pre class="sol">${esc(shortTb(result.import_error || result.crashed))}</pre>`;
  for (const test of result.tests || []) html += `<div class="tc">${test.status === "pass" ? "✔" : test.status === "skip" ? "–" : "✘"} ${esc(test.doc || test.name)}${test.traceback || test.message ? `<pre>${esc(shortTb(test.traceback || test.message))}</pre>` : ""}</div>`;
  if (result.stdout) html += `<pre class="sol">${esc(result.stdout)}</pre>`;
  return html + '<p>Record your confidence and a short mistake note below. You can rerun this problem or choose another from the summary.</p>';
}
function viewDiagnosticExercise(state, ex) {
  const sid = state.id, reflection = state.reflections[ex.id] || {};
  const code = Object.prototype.hasOwnProperty.call(state.drafts, ex.id) ? state.drafts[ex.id] : ex.stub;
  try { updateDiagnostic(ex.id, "open", sid, {code}); } catch (error) { diagnosticError(error); return; }
  const row = diagnosticSummary(state).find(item => item.id === ex.id);
  app.innerHTML = `<div class="card"><a href="#/diagnostic">← Diagnostic summary</a><h1>${ex.id} ${esc(ex.title)}</h1><p class="muted" id="diagnostic-outcome">Untimed diagnostic · ${row.attempts} attempt(s) · latest outcome: ${esc(row.outcome.replaceAll("_", " "))}</p><p>Try it before opening guidance. Need a starting point? Help is available below.</p><div class="desc">${descToHtml(ex.description)}</div><div class="row"><button class="btn secondary" id="diagnostic-help">Need help</button><button class="btn secondary" id="diagnostic-tests">Show tests</button></div><div id="diagnostic-guidance" ${reflection.help_at ? "" : "hidden"}>${ex.hints.map(hint => `<div class="hint">${inline(hint)}</div>`).join("")}<p>${diagnosticLessonLink(ex.id)}</p></div><pre class="sol" id="diagnostic-test-source" hidden>${esc(ex.tests)}</pre></div><div class="card"><div class="editor"><textarea class="fallback" id="diagnostic-code">${esc(code)}</textarea></div><div class="row" style="margin-top:10px"><button class="btn" id="diagnostic-run">▶ Run diagnostic tests</button><span role="status" id="diagnostic-save"></span></div><div class="results" id="diagnostic-results"></div></div><div class="card"><h2>Your reflection</h2><p>Confidence is your judgment, independent of whether these tests passed.</p><label for="diagnostic-confidence">Confidence</label> <select id="diagnostic-confidence"><option value="">Choose when ready</option><option value="confident" ${reflection.confidence === "confident" ? "selected" : ""}>Confident</option><option value="needs_review" ${reflection.confidence === "needs_review" ? "selected" : ""}>Needs review</option></select><p><label for="diagnostic-note">Short mistake note (up to 500 characters)</label></p><textarea class="fallback" id="diagnostic-note" style="display:block;min-height:90px;border:1px solid var(--line);border-radius:8px" rows="3" maxlength="500" placeholder="What tripped me up, or what I want to revisit">${esc(reflection.mistake_note || "")}</textarea><p class="muted">Drafts and reflections save as you type.</p><div class="row"><a class="btn secondary" href="#/diagnostic">Choose what to revisit</a></div></div>`;
  const input = $("#diagnostic-code"), results = $("#diagnostic-results"), button = $("#diagnostic-run"), status = $("#diagnostic-save");
  const currentView = () => results.isConnected && $("#diagnostic-results") === results;
  const save = (action, fields) => {
    try { updateDiagnostic(ex.id, action, sid, fields); if (currentView()) status.textContent = "Saved"; return true; }
    catch (error) { if (currentView()) status.textContent = error.message || String(error); return false; }
  };
  let practiceEditor = null;
  const getCode = () => practiceEditor ? practiceEditor.getValue() : input.value;
  const saveCode = () => save("draft", {code: getCode()});
  if (window.CodeMirror) {
    practiceEditor = CodeMirror.fromTextArea(input, {mode: "python", lineNumbers: true, indentUnit: 4, tabSize: 4, indentWithTabs: false, theme: isDark ? "material-darker" : "default", viewportMargin: Infinity, extraKeys: {Tab: cm => cm.replaceSelection("    ", "end"), "Cmd-Enter": runTests, "Ctrl-Enter": runTests}});
    practiceEditor.on("change", saveCode);
  } else { input.addEventListener("input", saveCode); input.addEventListener("keydown", event => { if ((event.metaKey || event.ctrlKey) && event.key === "Enter") { event.preventDefault(); runTests(); } }); }
  const confidence = $("#diagnostic-confidence"), note = $("#diagnostic-note");
  const saveReflection = () => save("reflect", {confidence: confidence.value || null, note: note.value});
  confidence.addEventListener("change", saveReflection); note.addEventListener("input", saveReflection);
  $("#diagnostic-help").onclick = () => { if (save("help", {})) $("#diagnostic-guidance").hidden = false; };
  $("#diagnostic-tests").onclick = () => { const source = $("#diagnostic-test-source"); source.hidden = !source.hidden; };
  button.onclick = runTests;
  async function runTests() {
    if (button.disabled || !saveCode()) return;
    const submittedCode = getCode(); button.disabled = true; status.textContent = "Running…"; results.innerHTML = "";
    try {
      const result = await runInPython(ex, submittedCode);
      const saved = updateDiagnostic(ex.id, "attempt", sid, {passed: diagnosticTestOutcome(result)});
      if (currentView()) {
        const row = diagnosticSummary(saved).find(item => item.id === ex.id);
        $("#diagnostic-outcome").textContent = `Untimed diagnostic · ${row.attempts} attempt(s) · latest outcome: ${row.outcome.replaceAll("_", " ")}`;
        results.innerHTML = diagnosticResultHtml(result); status.textContent = "Result saved";
      }
      else if (location.hash === "#/diagnostic") viewDiagnostic();
    } catch (error) {
      if (currentView()) status.textContent = error.message || String(error);
      else diagnosticError(error);
    } finally { button.disabled = false; }
  }
}
