"use strict";

const BROWSER_BACKUP_FORMAT = "python-cpe-course-backup";
const BACKUP_META_KEY = "cpe-course-backup-metadata-v1";
const BACKUP_RECOVERY_PREFIX = "cpe-course-backup-recovery:";
const BACKUP_PENDING_KEY = "cpe-course-backup-pending-v1";
let backupRecoveryProblem = null;

function backupObject(value) { return value !== null && typeof value === "object" && !Array.isArray(value); }
function backupClone(value) { return JSON.parse(JSON.stringify(value)); }
function backupRequire(condition, message) { if (!condition) throw new Error(message); }
function backupFiniteJSON(value) {
  if (typeof value === "number") backupRequire(Number.isFinite(value), "Backup numbers must be finite.");
  else if (value && typeof value === "object") for (const item of Object.values(value)) backupFiniteJSON(item);
}
function backupCounter(value) { return Number.isSafeInteger(value) && value >= 0; }
function backupNumber(value) { return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= Number.MAX_SAFE_INTEGER; }
function validateBackupProgress(progress) {
  backupRequire(backupObject(progress) && backupNumber(progress.xp), "Progress must be an object with a valid nonnegative XP value.");
  backupRequire(progress.version === undefined || progress.version === 1, "Unsupported progress version; the original input has been kept.");
  for (const key of ["solved", "attempts", "hints", "opened", "badges", "daily", "cards", "card_reward_history"]) {
    if (progress[key] !== undefined) backupRequire(backupObject(progress[key]), `Progress ${key} must be an object.`);
  }
  for (const key of ["solved", "daily", "cards"]) for (const value of Object.values(progress[key] || {})) backupRequire(backupObject(value), `Each ${key} record must be an object.`);
  for (const key of ["attempts", "hints"]) for (const value of Object.values(progress[key] || {})) backupRequire(backupCounter(value), `Progress ${key} must contain nonnegative integer counts.`);
  // Legacy malformed opened values are preserved; elapsedSeconds ignores them.
  for (const value of Object.values(progress.badges || {})) backupRequire(typeof value === "string", "Progress badges must contain strings.");
  for (const value of Object.values(progress.solved || {})) if (value.xp !== undefined) backupRequire(backupNumber(value.xp), "Solved XP values must be valid nonnegative numbers.");
  for (const value of Object.values(progress.daily || {})) {
    if (value.done !== undefined) backupRequire(typeof value.done === "boolean", "Daily done flags must be boolean.");
    if (value.id !== undefined) backupRequire(typeof value.id === "string", "Daily exercise IDs must be strings.");
  }
  for (const value of Object.values(progress.cards || {})) {
    if (value.done !== undefined) backupRequire(typeof value.done === "boolean", "Card done flags must be boolean.");
    if (value.correct !== undefined) backupRequire(value.correct === null || typeof value.correct === "boolean", "Card correctness must be boolean or null.");
    if (value.tries !== undefined) backupRequire(backupCounter(value.tries), "Card attempts must be nonnegative integer counts.");
  }
  for (const value of Object.values(progress.card_reward_history || {})) backupRequire(typeof value === "boolean", "Card reward history must contain boolean flags.");
  for (const key of ["days", "peeked"]) if (progress[key] !== undefined) backupRequire(Array.isArray(progress[key]) && progress[key].every((value) => typeof value === "string"), `Progress ${key} must be a list of strings.`);
  for (const day of progress.days || []) {
    const date = /^\d{4}-\d{2}-\d{2}$/.test(day) && new Date(day + "T12:00:00Z");
    backupRequire(date && !Number.isNaN(date.getTime()) && day.slice(0, 4) !== "0000" && date.toISOString().slice(0, 10) === day, "Practice days must be valid YYYY-MM-DD dates.");
  }
  for (const key of ["last", "last_lesson"]) if (progress[key] !== undefined) backupRequire(progress[key] === null || typeof progress[key] === "string", `Progress ${key} must be a string or null.`);
  return progress;
}
function parseBrowserBackup(source) {
  const value = typeof source === "string" ? JSON.parse(source) : source;
  backupRequire(backupObject(value), "Paste a browser backup or legacy progress object.");
  backupFiniteJSON(value);
  const envelope = ["format", "progress", "drafts", "exported_at"].some((key) => Object.prototype.hasOwnProperty.call(value, key));
  if (!envelope) return { legacy: true, progress: backupClone(validateBackupProgress(value)), drafts: null, metadata: null };
  backupRequire(value.format === BROWSER_BACKUP_FORMAT && value.version === 1, "Unsupported backup format or version; the original input has been kept.");
  const exported = parseTimestamp(value.exported_at);
  backupRequire(exported && exported.getUTCFullYear() >= 1 && exported.getUTCFullYear() <= 9999, "The backup export timestamp is invalid.");
  validateBackupProgress(value.progress);
  backupRequire(backupObject(value.drafts), "Backup drafts must be an object.");
  for (const [key, code] of Object.entries(value.drafts)) backupRequire(key.startsWith(DRAFT_KEY) && key.length > DRAFT_KEY.length && typeof code === "string", "Each draft must have a course draft key and text content.");
  const metadata = backupClone(value);
  for (const key of ["format", "version", "exported_at", "progress", "drafts"]) delete metadata[key];
  return { legacy: false, progress: backupClone(value.progress), drafts: backupClone(value.drafts), metadata };
}
function backupStorageKeys() {
  const keys = [];
  for (let index = 0; index < localStorage.length; index++) keys.push(localStorage.key(index));
  return keys.filter((key) => typeof key === "string").sort();
}
function backupManagedKey(key) { return [STORE_KEY, LEGACY_INTERVIEW_KEY, BACKUP_META_KEY].includes(key) || key.startsWith(DRAFT_KEY); }
function captureBackupStorage() {
  const values = {};
  for (const key of [...new Set([STORE_KEY, LEGACY_INTERVIEW_KEY, BACKUP_META_KEY, ...backupStorageKeys().filter((key) => key.startsWith(DRAFT_KEY))])].sort()) values[key] = localStorage.getItem(key);
  return values;
}
function currentBrowserDrafts(storage = captureBackupStorage()) { return Object.fromEntries(Object.entries(storage).filter(([key, value]) => key.startsWith(DRAFT_KEY) && value !== null)); }
function makeBrowserBackup(storage = captureBackupStorage()) {
  let metadata = {};
  if (storage[BACKUP_META_KEY] !== null) {
    try { const saved = JSON.parse(storage[BACKUP_META_KEY]); if (backupObject(saved)) metadata = saved; }
    catch (error) { metadata = { unreadable_browser_metadata: storage[BACKUP_META_KEY] }; }
  }
  return { ...metadata, format: BROWSER_BACKUP_FORMAT, version: 1, exported_at: nowIso(), progress: backupClone(P), drafts: currentBrowserDrafts(storage) };
}
function backupFingerprint(storage = captureBackupStorage()) { return JSON.stringify({ progress: P, storage }); }
function previewBrowserBackup(source) {
  const incoming = parseBrowserBackup(source), storage = captureBackupStorage(), current = currentBrowserDrafts(storage);
  const target = incoming.legacy ? current : incoming.drafts;
  return { incoming, fingerprint: backupFingerprint(storage), changed: Object.keys(target).filter((key) => current[key] !== undefined && current[key] !== target[key]), added: Object.keys(target).filter((key) => current[key] === undefined), removed: Object.keys(current).filter((key) => target[key] === undefined), currentDrafts: Object.keys(current).length, targetDrafts: Object.keys(target).length, currentXP: P.xp, currentSolved: Object.keys(P.solved).length };
}
function restoreBackupStorage(values) {
  backupRequire(backupObject(values) && [STORE_KEY, LEGACY_INTERVIEW_KEY, BACKUP_META_KEY].every((key) => Object.prototype.hasOwnProperty.call(values, key)) && Object.entries(values).every(([key, value]) => backupManagedKey(key) && (value === null || typeof value === "string")), "The recovery storage snapshot is invalid.");
  for (const key of backupStorageKeys().filter(backupManagedKey)) if (values[key] == null) localStorage.removeItem(key);
  for (const [key, value] of Object.entries(values)) if (value !== null) localStorage.setItem(key, value);
}
function backupImportPending() {
  try { return localStorage.getItem(BACKUP_PENDING_KEY) !== null; } catch (error) { return true; }
}
function recoverPendingImport() {
  let key;
  try { key = localStorage.getItem(BACKUP_PENDING_KEY); } catch (error) { return null; }
  if (!key) { backupRecoveryProblem = null; return null; }
  let copy = null;
  try {
    backupRequire(key.startsWith(BACKUP_RECOVERY_PREFIX), "The pending recovery reference is invalid.");
    copy = JSON.parse(localStorage.getItem(key));
    backupRequire(backupObject(copy) && copy.format === BROWSER_BACKUP_FORMAT && copy.version === 1 && backupObject(copy.progress), "The recovery copy is unavailable or uses an unsupported version.");
    restoreBackupStorage(copy.recovery_storage);
    localStorage.removeItem(BACKUP_PENDING_KEY);
    backupRecoveryProblem = null;
    return null;
  } catch (error) {
    backupRecoveryProblem = { key, copy, message: error.message || String(error) };
    let progress = null;
    try { if (copy) progress = validateBackupProgress(copy.progress); } catch (invalid) {}
    return { blocked: true, progress };
  }
}
function replaceBrowserBackup(preview) {
  backupRequire(typeof pending === "undefined" || pending === null, "Wait for the running tests to finish, then preview this import again.");
  backupRequire(preview.fingerprint === backupFingerprint(), "Saved data changed after this preview. Preview the import again before replacing it.");
  backupRequire(!backupImportPending(), "Finish recovering the previous import first.");
  const before = P, storage = captureBackupStorage();
  const recovery = { ...makeBrowserBackup(storage), recovery_storage: storage };
  const key = BACKUP_RECOVERY_PREFIX + Date.now() + "-" + Math.random().toString(36).slice(2);
  let importPending = false;
  try {
    backupRequire(localStorage.getItem(key) === null, "Could not allocate a new recovery copy. Try again.");
    // Save the complete old state durably before touching any live progress/drafts.
    localStorage.setItem(key, JSON.stringify(recovery));
    localStorage.setItem(BACKUP_PENDING_KEY, key);
    importPending = true;
    const incoming = preview.incoming;
    if (!incoming.legacy) {
      for (const oldKey of backupStorageKeys().filter((item) => item.startsWith(DRAFT_KEY))) if (!Object.prototype.hasOwnProperty.call(incoming.drafts, oldKey)) localStorage.removeItem(oldKey);
      for (const [draftKey, code] of Object.entries(incoming.drafts)) localStorage.setItem(draftKey, code);
      localStorage.setItem(BACKUP_META_KEY, JSON.stringify(incoming.metadata));
    }
    const replacement = migrateCardProgress({ ...blankProgress(), ...backupClone(incoming.progress), legacy_interview_migrated: true });
    localStorage.setItem(STORE_KEY, JSON.stringify(replacement));
    localStorage.removeItem(LEGACY_INTERVIEW_KEY);
    localStorage.removeItem(BACKUP_PENDING_KEY); // commit only after every live write
    P = replacement;
    backupRecoveryProblem = null;
    return key;
  } catch (error) {
    P = before;
    if (importPending) {
      const result = recoverPendingImport();
      if (result && result.blocked) throw new Error("Import stopped. Your complete previous data is saved in a recovery copy; free storage and retry recovery.");
    }
    throw new Error("Import stopped; previous data was retained. " + (error.message || error));
  }
}
function backupRecoveryView() {
  if (!backupRecoveryProblem) return false;
  const problem = backupRecoveryProblem;
  app.innerHTML = `<div class="card"><h1>Recover the interrupted import</h1><p>Your previous data was saved before import. Storage prevented restoration. Free browser storage, then retry; keep the recovery JSON below as a separate copy.</p><p class="bad">${esc(problem.message)}</p><button class="btn" id="backup-retry-recovery">Retry recovery</button><p><label for="backup-recovery-json">Recovery JSON</label></p><textarea class="answer" rows="12" id="backup-recovery-json">${esc(JSON.stringify(problem.copy, null, 2))}</textarea></div>`;
  $("#backup-retry-recovery").onclick = () => { const result = recoverPendingImport(); if (!result) { P = loadProgress(); renderHeader(); route(); } else backupRecoveryView(); };
  return true;
}
function browserBackupControls() {
  const io = $("#io"), panel = $("#backup-preview");
  $("#exportbtn").onclick = () => { try { io.value = JSON.stringify(makeBrowserBackup(), null, 2); io.select(); toast("Copy the backup JSON to keep progress and code drafts"); } catch (error) { panel.textContent = "Could not read the full backup: " + error.message; } };
  const showPreview = () => {
    const source = io.value;
    try {
      const preview = previewBrowserBackup(source), incoming = preview.incoming;
      const details = [...preview.changed.map((key) => "Replace " + key.slice(DRAFT_KEY.length)), ...preview.removed.map((key) => "Remove " + key.slice(DRAFT_KEY.length)), ...preview.added.map((key) => "Add " + key.slice(DRAFT_KEY.length))];
      panel.innerHTML = `<div class="card" style="margin-top:12px"><h3>Import preview</h3><p>Replace all progress: ${preview.currentXP} → ${incoming.progress.xp} XP; ${preview.currentSolved} → ${Object.keys(incoming.progress.solved || {}).length} solved exercises. Saved sessions, notes and the refresher path will use the imported progress.</p><p>${incoming.legacy ? `Legacy progress file: keep all ${preview.currentDrafts} current code drafts.` : `Code drafts: ${preview.currentDrafts} → ${preview.targetDrafts}; ${preview.changed.length} replaced, ${preview.removed.length} removed, ${preview.added.length} added.`}</p>${details.length ? `<details><summary>Draft changes</summary><ul>${details.map((detail) => `<li>${esc(detail)}</li>`).join("")}</ul></details>` : ""}<p>A complete recovery copy of your current data will be saved first. If there is not enough storage for it, the import will stop.</p><div class="row"><button class="btn" id="backup-replace">${incoming.legacy ? "Replace progress only" : "Replace progress and drafts"}</button><button class="btn secondary" id="backup-cancel">Cancel import</button></div></div>`;
      $("#backup-cancel").onclick = () => { panel.innerHTML = '<p>Import cancelled. Saved data is unchanged.</p>'; };
      $("#backup-replace").onclick = () => {
        try {
          if (io.value !== source || preview.fingerprint !== backupFingerprint()) { showPreview(); panel.insertAdjacentHTML("afterbegin", '<p class="bad">The input or saved data changed. Review this updated preview before replacing it.</p>'); return; }
          replaceBrowserBackup(preview); renderHeader(); viewProfile(); toast("Imported. Your previous data is available under Recovery copies.");
        }
        catch (error) { if (!backupRecoveryView()) panel.textContent = error.message; }
      };
    } catch (error) { panel.textContent = "Import rejected: " + (error.message || error); }
  };
  $("#importbtn").onclick = showPreview;
  let recoveries;
  try { recoveries = backupStorageKeys().filter((key) => key.startsWith(BACKUP_RECOVERY_PREFIX)).reverse(); }
  catch (error) { $("#backup-recovery-list").textContent = "Could not read recovery copies: " + error.message; return; }
  $("#backup-recovery-list").innerHTML = recoveries.length ? `<label for="backup-recovery-choice">Recovery copies</label><select id="backup-recovery-choice" class="answer">${recoveries.map((key, index) => `<option value="${esc(key)}">${index === 0 ? "Latest: " : ""}${esc(key.slice(BACKUP_RECOVERY_PREFIX.length))}</option>`).join("")}</select><button class="btn secondary" id="backup-load-recovery" style="margin-top:8px">Load recovery JSON for preview</button>` : '<p class="muted">Recovery copies will appear here after an import.</p>';
  if (recoveries.length) $("#backup-load-recovery").onclick = () => { try { io.value = localStorage.getItem($("#backup-recovery-choice").value) || ""; showPreview(); } catch (error) { panel.textContent = "Could not read this recovery copy: " + error.message; } };
}
