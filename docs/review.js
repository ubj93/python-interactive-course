// One queue across diagnostic and ordinary exercise reflections. Review runs use
// independent practice state and never call lifetime scoring or hint functions.
const REVIEW_INTERVALS = [1, 3, 7, 30];
function reviewExerciseId(value) { return typeof value === "string" && value.match(/^[0-9]+\.[0-9]+$/)?.[0] === value; }
function reviewDate(value) {
  if (typeof value !== "string" || value.length !== 10 || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  const [y, m, d] = value.split("-").map(Number), date = new Date(0);
  date.setUTCHours(0, 0, 0, 0); date.setUTCFullYear(y, m - 1, d);
  return y >= 1 && y <= 9999 && date.getUTCFullYear() === y && date.getUTCMonth() === m - 1 && date.getUTCDate() === d ? date : null;
}
function reviewQueue(value = P.review_queue) {
  if (value == null) return {version: 1, items: {}};
  if (!practiceObject(value) || value.version !== 1 || !practiceObject(value.items)) throw Error("Saved review queue is unsupported. Export a backup before repairing its review_queue field.");
  const queue = practiceClone(value);
  for (const [id, row] of Object.entries(queue.items)) {
    if (!reviewExerciseId(id) || !practiceObject(row) || !["confident", "needs_review"].includes(row.confidence) || typeof row.mistake_note !== "string" || [...row.mistake_note].length > 500 || !REVIEW_INTERVALS.includes(row.interval_days) || !reviewDate(row.next_review) || !Array.isArray(row.sources) || row.sources.some(source => typeof source !== "string")) throw Error("Invalid saved review item. Keep a progress backup before repairing it.");
  }
  return queue;
}
function reflectReviewQueue(value, id, confidence, note, interval = null, source = "exercise", now = new Date(), preserveSchedule = false) {
  const queue = reviewQueue(value);
  if (typeof id !== "string" || !reviewExerciseId(id) || !["confident", "needs_review"].includes(confidence) || typeof note !== "string" || [...note].length > 500) throw Error("Choose a confidence and keep the note to 500 characters.");
  const row = queue.items[id] || {}, sameConfidence = row.confidence === confidence, explicitInterval = interval != null;
  interval = interval == null ? (sameConfidence ? row.interval_days : confidence === "needs_review" ? 1 : 3) : interval;
  if (!REVIEW_INTERVALS.includes(interval)) throw Error("Choose a review interval of 1, 3, 7 or 30 days.");
  const keepDate = preserveSchedule && sameConfidence && !explicitInterval;
  const due = reviewDate(keepDate ? row.next_review : localDay(now));
  if (!due) throw Error("The next review date is outside the supported calendar.");
  if (!keepDate) due.setUTCDate(due.getUTCDate() + interval);
  if (due.getUTCFullYear() > 9999) throw Error("The next review date is outside the supported calendar.");
  const sources = row.sources || [];
  if (!sources.includes(source)) sources.push(source);
  queue.items[id] = {...row, confidence, mistake_note: note, interval_days: interval, next_review: due.toISOString().slice(0, 10), reflected_at: now.toISOString(), sources};
  return queue;
}
function reviewQueueRows(value = P.review_queue, date = today(), dueOnly = false) {
  return Object.entries(reviewQueue(value).items).map(([id, row]) => ({...row, id, due: row.next_review <= date})).filter(row => !dueOnly || row.due).sort((a, b) => Number(b.due) - Number(a.due) || Number(a.confidence !== "needs_review") - Number(b.confidence !== "needs_review") || a.next_review.localeCompare(b.next_review) || Number(a.id.split(".")[0]) - Number(b.id.split(".")[0]) || Number(a.id.split(".")[1]) - Number(b.id.split(".")[1]));
}
function saveReviewFields(fields) {
  const before = P; P = {...P, ...fields};
  if (!saveProgress()) { P = before; throw Error("Review work could not be saved. Export your progress and free browser storage before continuing."); }
}
function saveExerciseReflection(id, confidence, note, interval = null) {
  if (!BY_ID[id]) throw Error("Choose an existing exercise.");
  const queue = reflectReviewQueue(P.review_queue, id, confidence, note, interval);
  saveReviewFields({review_queue: queue}); return queue.items[id];
}
function reviewSession(value = P.review_session) {
  const state = normalizePractice(value); return state && state.kind === "review" ? state : null;
}
function beginReview(ids, fresh = false) {
  const state = reviewSession();
  if (!fresh && P.review_session != null) {
    if (!state) throw Error("Saved review round is invalid. Export it, or start a fresh round to archive it.");
    return state;
  }
  if (!Array.isArray(ids) || !ids.length || ids.some(id => !BY_ID[id]) || new Set(ids).size !== ids.length) throw Error("Choose existing exercises, or add a reflection to your review queue.");
  const history = practiceClone(Array.isArray(P.review_history) ? P.review_history : P.review_history == null ? [] : [P.review_history]);
  if (P.review_session != null) history.push(practiceClone(P.review_session));
  const id = window.crypto && window.crypto.randomUUID ? window.crypto.randomUUID() : Date.now().toString(36) + "-" + Math.random().toString(36).slice(2);
  const created = {version: 1, id, kind: "review", started: nowIso(), ids: [...ids], attempts: [], reflections: {}, drafts: {}, last_exercise: null};
  saveReviewFields({review_session: created, review_history: history}); return practiceClone(created);
}
function updateReview(id, action, sid, fields = {}) {
  const state = reviewSession();
  if (!state || state.id !== sid) throw Error("The review round changed; this result was not added to another round.");
  if (!state.ids.includes(id)) throw Error("Unknown review exercise.");
  const at = nowIso();
  if (parseTimestamp(at) < parseTimestamp(state.started)) throw Error("The clock is earlier than this review round.");
  const updates = {};
  if (action === "attempt") {
    if (typeof fields.passed !== "boolean") throw Error("A review attempt needs a test outcome.");
    state.attempts.push({exercise_id: id, at, passed: fields.passed});
  } else if (action === "reflect") {
    updates.review_queue = reflectReviewQueue(P.review_queue, id, fields.confidence, fields.note, fields.interval, "review");
    state.reflections[id] = {...state.reflections[id], confidence: fields.confidence, mistake_note: fields.note, interval_days: updates.review_queue.items[id].interval_days};
  } else if (action === "help") state.reflections[id] = {...state.reflections[id], help_at: (state.reflections[id] || {}).help_at || at};
  else if (!["open", "draft"].includes(action)) throw Error("Unknown review action.");
  if (fields.code !== undefined) {
    if (typeof fields.code !== "string") throw Error("The review draft must be text.");
    state.drafts[id] = fields.code;
  }
  state.last_exercise = id;
  saveReviewFields({...updates, review_session: state}); return practiceClone(state);
}
function finishReview() {
  const state = reviewSession(); if (!state) throw Error("There is no supported review round to finish.");
  const history = practiceClone(Array.isArray(P.review_history) ? P.review_history : P.review_history == null ? [] : [P.review_history]);
  history.push(state); saveReviewFields({review_session: null, review_history: history}); return state;
}
function reviewReflectionHtml(prefix, row = {}) {
  return `<h2>Your reflection</h2><p>Confidence is your judgment, independent of test results.</p><label for="${prefix}-confidence">Confidence</label> <select style="max-width:100%;font-size:16px" id="${prefix}-confidence"><option value="">Choose when ready</option><option value="needs_review" ${row.confidence === "needs_review" ? "selected" : ""}>Needs review</option><option value="confident" ${row.confidence === "confident" ? "selected" : ""}>Confident</option></select><p><label for="${prefix}-note">Short mistake note (up to 500 characters)</label></p><textarea class="fallback" style="display:block;min-height:90px;font-size:16px;border:1px solid var(--line);border-radius:8px" rows="3" maxlength="500" id="${prefix}-note">${esc(row.mistake_note || "")}</textarea><p><label for="${prefix}-interval">Revisit after</label> <select style="max-width:100%;font-size:16px" id="${prefix}-interval"><option value="">1 day if needs review; 3 days if confident</option><option value="7" ${row.interval_days === 7 ? "selected" : ""}>7 days</option><option value="30" ${row.interval_days === 30 ? "selected" : ""}>30 days</option></select></p><div class="row"><button class="btn secondary" id="${prefix}-save">Save reflection and review date</button> <span role="status" id="${prefix}-status"></span></div><p><a href="#/review">Open review queue</a> · You can practise anytime.</p>`;
}
function bindReviewReflection(prefix, save) {
  $("#" + prefix + "-save").onclick = () => {
    const status = $("#" + prefix + "-status");
    try {
      const interval = $("#" + prefix + "-interval").value;
      const row = save($("#" + prefix + "-confidence").value, $("#" + prefix + "-note").value, interval ? Number(interval) : null);
      status.textContent = "Saved. Next review: " + row.next_review;
    } catch (error) { status.textContent = error.message || String(error); }
  };
}
function exerciseReviewReflection(ex) {
  const box = $("#exercise-reflection"); if (!box) return;
  try {
    box.innerHTML = reviewReflectionHtml("exercise-review", reviewQueue().items[ex.id]);
    bindReviewReflection("exercise-review", (confidence, note, interval) => saveExerciseReflection(ex.id, confidence, note, interval));
  } catch (error) { box.innerHTML = `<p>${esc(error.message)}</p><a href="#/profile">Export progress</a>`; }
}
function reviewRowsHtml(state, archived = false) {
  const rows = practiceSummary(state);
  if (!rows) return '<p>Unsupported archived round. The original remains in your progress export.</p>';
  return rows.map(row => `<div class="item"><span class="t"><b>${row.id} ${esc(BY_ID[row.id] ? BY_ID[row.id].title : "Exercise unavailable")}</b><small>${esc(row.outcome.replaceAll("_", " "))} · ${row.attempts} attempt(s) · confidence: ${esc((row.confidence || "not recorded").replaceAll("_", " "))}</small>${row.mistake_note ? `<p style="overflow-wrap:anywhere">${esc(row.mistake_note)}</p>` : ""}${archived || !BY_ID[row.id] ? "" : `<a class="btn small secondary" href="#/review/${row.id}">Review exercise</a>`}</span></div>`).join("");
}
function viewReview(exId) {
  const state = reviewSession();
  if (exId && state && state.ids.includes(exId) && BY_ID[exId]) return viewReviewExercise(state, BY_ID[exId]);
  let rows;
  try { rows = reviewQueueRows(); }
  catch (error) { app.innerHTML = `<div class="card"><h1>Review queue</h1><p>${esc(error.message)}</p><a href="#/profile">Export progress</a></div>`; return; }
  const due = rows.filter(row => row.due && BY_ID[row.id]).map(row => row.id);
  const resume = state && (state.last_exercise || state.ids.find(id => !state.attempts.some(a => a.exercise_id === id)) || state.ids[0]);
  app.innerHTML = `<div class="card"><h1>Review queue</h1><p>Revisit marked weaknesses at your pace. Needs review defaults to 1 day; confident to 3 days. Choose 7 or 30 days when useful, or practise anytime.</p><p>Review rounds keep separate drafts and test outcomes. Original passes, XP and hint usage stay unchanged.</p><div class="row">${resume ? `<a class="btn" href="#/review/${resume}">Resume review</a><button class="btn secondary" id="review-finish">Finish this round</button>` : ""}${due.length ? `<button class="btn secondary" id="review-due">${state ? "Start a fresh due round" : "Start due review"} · ${due.length} exercise(s)</button>` : '<span class="muted">No reviews are due.</span>'}</div>${P.review_session != null && !state ? '<p>Unsupported saved round. Its data will be archived when you start a fresh round.</p>' : ""}<p><label for="review-manual">Manual practice</label> <select style="max-width:100%;font-size:16px" id="review-manual">${ALL.map(ex => `<option value="${ex.id}">${ex.id} ${esc(ex.title)}</option>`).join("")}</select> <button class="btn secondary" id="review-new">Start fresh practice</button></p></div><div class="card"><h2>Saved reflections</h2>${rows.length ? rows.map(row => `<div class="item"><span class="t"><b>${row.id} ${esc(BY_ID[row.id] ? BY_ID[row.id].title : "Exercise unavailable")}</b><small>${esc(row.confidence.replaceAll("_", " "))} · ${row.next_review} · ${row.due ? "ready to revisit" : "planned"}</small>${row.mistake_note ? `<p style="overflow-wrap:anywhere">${esc(row.mistake_note)}</p>` : ""}</span></div>`).join("") : '<p>After a diagnostic or exercise result, record confidence and a short mistake note to add it here.</p>'}</div>${state ? `<div class="card"><h2>This round</h2>${reviewRowsHtml(state)}</div>` : ""}<div class="card"><h2>Earlier review rounds</h2>${Array.isArray(P.review_history) && P.review_history.length ? P.review_history.map((old, i) => `<details><summary>Round ${i + 1}</summary>${reviewRowsHtml(old, true)}</details>`).join("") : '<p>Starting fresh preserves earlier rounds and their drafts.</p>'}</div>`;
  const start = ids => { try { const created = beginReview(ids, true); location.hash = "#/review/" + created.ids[0]; } catch (error) { toast(error.message); } };
  $("#review-new").onclick = () => start([$("#review-manual").value]);
  if ($("#review-due")) $("#review-due").onclick = () => start(due);
  if ($("#review-finish")) $("#review-finish").onclick = () => { try { finishReview(); viewReview(); } catch (error) { toast(error.message); } };
}
function viewReviewExercise(state, ex) {
  const sid = state.id, row = practiceSummary(state).find(item => item.id === ex.id);
  const code = Object.prototype.hasOwnProperty.call(state.drafts, ex.id) ? state.drafts[ex.id] : ex.stub;
  try { updateReview(ex.id, "open", sid, {code}); } catch (error) { toast(error.message); return; }
  app.innerHTML = `<div class="card"><a href="#/review">← Review queue and round summary</a><h1>${ex.id} ${esc(ex.title)}</h1><p id="review-outcome">Untimed review · ${row.attempts} attempt(s) · latest outcome: ${esc(row.outcome.replaceAll("_", " "))}</p><div class="desc">${descToHtml(ex.description)}</div><button class="btn secondary" id="review-help">Need help</button><button class="btn secondary" id="review-tests">Show tests</button><div id="review-guidance" ${row.help_used ? "" : "hidden"}>${ex.hints.map(hint => `<div class="hint">${inline(hint)}</div>`).join("")}<p>${diagnosticLessonLink(ex.id)}</p></div><pre class="sol" id="review-test-source" hidden>${esc(ex.tests)}</pre></div><div class="card"><div class="editor"><textarea class="fallback" id="review-code">${esc(code)}</textarea></div><p><button class="btn" id="review-run">▶ Run review tests</button> <span role="status" id="review-save"></span></p><div class="results" id="review-results"></div></div><div class="card">${reviewReflectionHtml("round-review", state.reflections[ex.id])}</div>`;
  const input = $("#review-code"), results = $("#review-results"), status = $("#review-save"), button = $("#review-run");
  const current = () => results.isConnected && $("#review-results") === results;
  const save = (action, fields) => { try { updateReview(ex.id, action, sid, fields); if (current()) status.textContent = "Saved"; return true; } catch (error) { if (current()) status.textContent = error.message; return false; } };
  let editor = null;
  const getCode = () => editor ? editor.getValue() : input.value;
  const saveCode = () => save("draft", {code: getCode()});
  if (window.CodeMirror) { editor = CodeMirror.fromTextArea(input, {mode: "python", lineNumbers: true, indentUnit: 4, theme: isDark ? "material-darker" : "default", viewportMargin: Infinity, extraKeys: {Tab: cm => cm.replaceSelection("    ", "end"), "Cmd-Enter": run, "Ctrl-Enter": run}}); editor.on("change", saveCode); }
  else { input.addEventListener("input", saveCode); input.addEventListener("keydown", event => { if ((event.metaKey || event.ctrlKey) && event.key === "Enter") { event.preventDefault(); run(); } }); }
  bindReviewReflection("round-review", (confidence, note, interval) => { updateReview(ex.id, "reflect", sid, {confidence, note, interval}); return P.review_queue.items[ex.id]; });
  $("#review-help").onclick = () => { if (save("help", {})) $("#review-guidance").hidden = false; };
  $("#review-tests").onclick = () => { const source = $("#review-test-source"); source.hidden = !source.hidden; };
  button.onclick = run;
  async function run() {
    if (button.disabled || !saveCode()) return;
    const code = getCode(); button.disabled = true; status.textContent = "Running…"; results.innerHTML = "";
    try {
      const result = await runInPython(ex, code);
      const saved = updateReview(ex.id, "attempt", sid, {passed: diagnosticTestOutcome(result)});
      if (current()) {
        const row = practiceSummary(saved).find(item => item.id === ex.id);
        $("#review-outcome").textContent = `Untimed review · ${row.attempts} attempt(s) · latest outcome: ${row.outcome.replaceAll("_", " ")}`;
        results.innerHTML = diagnosticResultHtml(result, "Review"); status.textContent = "Result saved";
      }
      else if (location.hash === "#/review") viewReview();
    } catch (error) { if (current()) status.textContent = error.message; else toast(error.message); }
    finally { button.disabled = false; }
  }
}
