"use strict";

// Path completion is an explicit planning choice, separate from lesson progress.
function refresherActivities() { return DATA.refresher.sessions.flatMap((session) => session.activities); }
function refresherStatus(saved, id) {
  const item = saved.activities[id];
  return item && ["done", "skipped"].includes(item.status) ? item.status : "pending";
}
function refresherState(value = P.refresher) {
  const ids = refresherActivities().map((activity) => activity.id);
  if (value == null) return { version: 1, path_id: "interview-refresher", next_activity: ids[0], activities: {}, mock_sessions: {} };
  if (value.version !== 1 || value.path_id !== "interview-refresher" || !value.activities || typeof value.activities !== "object" || Array.isArray(value.activities)) throw new Error("The saved refresher path is not supported. Export a backup before repairing its refresher field.");
  const saved = JSON.parse(JSON.stringify(value));
  if (saved.mock_sessions === undefined) saved.mock_sessions = {};
  if (!saved.mock_sessions || typeof saved.mock_sessions !== "object" || Array.isArray(saved.mock_sessions)) throw new Error("The saved refresher mock links are invalid. Export a backup before repairing them.");
  const pending = ids.filter((id) => refresherStatus(saved, id) === "pending");
  if (!pending.includes(saved.next_activity)) saved.next_activity = pending[0] || null;
  return saved;
}
function updateRefresher(value, action, id, note) {
  const saved = refresherState(value), ids = refresherActivities().map((item) => item.id);
  id = id || saved.next_activity;
  if (!ids.includes(id)) throw new Error("Choose an activity from the refresher path.");
  if (!["open", "done", "skip", "revisit", "note"].includes(action)) throw new Error("Unknown refresher action.");
  const item = Object.assign({}, saved.activities[id], { updated_at: nowIso() });
  if (action === "note") item.note = String(note || "");
  else if (["done", "skip", "revisit"].includes(action)) item.status = { done: "done", skip: "skipped", revisit: "pending" }[action];
  saved.activities[id] = item;
  if (["open", "revisit"].includes(action) && refresherStatus(saved, id) === "pending") saved.next_activity = id;
  else if (["done", "skip"].includes(action)) {
    const after = ids.indexOf(id) + 1;
    saved.next_activity = [...ids.slice(after), ...ids.slice(0, after)].find((candidate) => refresherStatus(saved, candidate) === "pending") || null;
  }
  return saved;
}
function saveRefresher(saved, interview = undefined) {
  const before = P;
  P = Object.assign({}, P, { refresher: saved });
  if (interview !== undefined) Object.assign(P, { interview, legacy_interview_migrated: true });
  if (!saveProgress()) { P = before; toast("Could not save the path. Free browser storage and try again."); return false; }
  return true;
}
function refresherWeakAreas(diagnostic = P.diagnostic) {
  const results = diagnosticSummary(diagnostic);
  if (!results) return [];
  const rows = [];
  for (const result of results) {
    const id = result.id, lessons = DATA.refresher.diagnostic_lessons[id], reasons = [];
    if (!lessons) continue;
    if (result.outcome === "not_passed") reasons.push("Latest diagnostic run did not pass");
    if (result.confidence === "needs_review") reasons.push("You marked this for review");
    if (result.help_used) reasons.push("You used diagnostic help");
    const note = result.mistake_note.trim();
    if (note) reasons.push("You recorded a mistake note");
    if (reasons.length) rows.push({ id, lessons, reasons, note });
  }
  return rows;
}
function refresherLessonLinks(ids) {
  return ids.map((id) => `<a class="btn small secondary" href="#/learn/${id}">Lesson ${id}: ${esc(LESSON_BY_ID[id].title)}</a>`).join("");
}
function refresherSuggestions() {
  const rows = refresherWeakAreas();
  return `<div class="card"><h2>Diagnostic review suggestions</h2>${rows.length ? rows.map((row) => `<p>${esc(row.reasons.join(" · "))}${row.note ? `<br>Your note: ${esc(row.note)}` : ""}</p><div class="row">${refresherLessonLinks(row.lessons)}</div>`).join("") : '<p>No review signals saved yet. Try the diagnostic and record confidence and notes.</p>'}<p><a href="#/diagnostic">Open the fundamentals diagnostic</a></p><p class="muted">These are review suggestions. They do not change your path or assert mastery.</p></div>`;
}
function refresherMock(session) {
  if (!session) return null;
  try {
    const saved = refresherState();
    return refresherActivities().find((activity) => activity.kind === "mock" && saved.mock_sessions[activity.id] === session.id) || null;
  } catch (error) { return null; }
}
function startRefresherMock(activity) {
  let saved = refresherState();
  let active = activeInterview();
  if (active && active.id !== saved.mock_sessions[activity.id]) { toast("A different mock is active. Finish it on the Mock interview page first."); return; }
  if (!active) {
    active = newSession(activity.exercises, activity.minutes);
    if (!active) { toast("This mock could not start. Check the device clock."); return; }
    saved.mock_sessions[activity.id] = active.id;
  }
  saved = updateRefresher(saved, "open", activity.id);
  if (saveRefresher(saved, active)) location.hash = "#/interview";
}
function viewRefresher(id) {
  const plan = DATA.refresher, activities = refresherActivities();
  let saved;
  try { saved = refresherState(); }
  catch (error) { app.innerHTML = `<div class="card"><h1>Interview refresher</h1><p>${esc(error.message)}</p><a href="#/profile">Export progress</a> · <a href="#/">Full curriculum</a></div>`; return; }
  const activity = activities.find((item) => item.id === id);
  if (id && !activity) { app.innerHTML = '<div class="card"><h1>Activity unavailable</h1><a href="#/refresher">Return to the saved path</a></div>'; return; }
  if (activity) {
    const opened = updateRefresher(saved, "open", activity.id);
    if (saveRefresher(opened)) saved = opened;
    const session = plan.sessions.find((item) => item.activities.includes(activity));
    const index = plan.sessions.indexOf(session) + 1;
    app.innerHTML = `<div class="crumbs"><a href="#/refresher">Interview refresher</a> › Session ${index}</div><div class="card">
      <p class="kind">Session ${index}: ${esc(session.title)}</p><h1>${esc(activity.title)}</h1><p>${activity.minutes} minutes · ${refresherStatus(saved, activity.id)}</p>
      <p>${esc(activity.description)}</p><p class="muted">Prerequisites: ${esc(session.prerequisite)}</p>
      <div class="row">${refresherLessonLinks(activity.lessons)}${activity.exercises.map((ex) => `<a class="btn secondary" href="#/ex/${ex}">Exercise ${ex}: ${esc(BY_ID[ex].title)}</a>`).join("")}${activity.kind === "diagnostic" ? '<a class="btn" href="#/diagnostic">Open diagnostic</a>' : ""}${activity.kind === "mock" ? '<button class="btn" id="refresher-mock">Start or resume curated mock</button><a href="#/interview">Review current or latest mock</a>' : ""}</div>
      <p><label for="refresher-note">Your takeaway or next practice</label></p><textarea class="answer" id="refresher-note" rows="3">${esc((saved.activities[id] || {}).note || "")}</textarea>
      <div class="row" style="margin-top:10px"><button class="btn secondary" id="refresher-save-note">Save note</button><button class="btn" id="refresher-done">Mark done</button><button class="btn secondary" id="refresher-skip">Skip activity</button><button class="btn secondary" id="refresher-revisit">Revisit activity</button></div>
      <p class="muted">Done, skip and revisit only change this path. They do not claim mastery or award XP. Save your note before leaving.</p></div>${refresherSuggestions()}`;
    $("#refresher-save-note").onclick = () => { if (saveRefresher(updateRefresher(P.refresher, "note", id, $("#refresher-note").value))) toast("Note saved"); };
    for (const action of ["done", "skip", "revisit"]) $("#refresher-" + action).onclick = () => {
      if (saveRefresher(updateRefresher(P.refresher, action, id))) {
        if (action === "revisit") { toast("Activity ready to revisit"); viewRefresher(id); }
        else location.hash = "#/refresher";
      }
    };
    if (activity.kind === "mock") $("#refresher-mock").onclick = () => startRefresherMock(activity);
    return;
  }
  const next = activities.find((item) => item.id === saved.next_activity);
  const done = activities.filter((item) => refresherStatus(saved, item.id) === "done").length;
  const skipped = activities.filter((item) => refresherStatus(saved, item.id) === "skipped").length;
  app.innerHTML = `<div class="crumbs"><a href="#/">Full curriculum</a> › Interview refresher</div><div class="card"><h1>${esc(plan.title)}</h1><p>${esc(plan.description)}</p><p>${esc(plan.prerequisites)}</p><p>${done} done · ${skipped} skipped · ${activities.length - done - skipped} remaining</p>${next ? `<h2>Next: ${esc(next.title)}</h2><a class="btn" id="refresher-resume" href="#/refresher/${next.id}">Resume activity · ${next.minutes} min</a>` : '<p>All path activities are done or skipped. Revisit any activity when useful.</p>'}</div>
    ${plan.sessions.map((session, index) => `<details class="card" ${session.activities.some((item) => item.id === saved.next_activity) ? "open" : ""}><summary><b>Session ${index + 1}: ${esc(session.title)}</b> · ${session.activities.reduce((total, item) => total + item.minutes, 0)} min</summary><p>Prerequisites: ${esc(session.prerequisite)}</p><div class="list">${session.activities.map((item) => `<a class="item" href="#/refresher/${item.id}"><span class="t"><b>${esc(item.title)}</b><small>${item.minutes} min · ${refresherStatus(saved, item.id)}</small></span></a>`).join("")}</div></details>`).join("")}
    ${refresherSuggestions()}<div class="card"><h2>Optional extensions for your target interview</h2>${plan.optional.map((item) => `<h3>${esc(item.title)}</h3><div class="row">${refresherLessonLinks(item.lessons)}</div>`).join("")}<p><a href="#/">Browse the full curriculum</a></p></div>`;
}
