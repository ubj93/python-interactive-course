const assert = require("node:assert/strict"), fs = require("node:fs"), vm = require("node:vm"), path = require("node:path");
const source = fs.readFileSync(path.join(__dirname, "../docs/browser-backup.js"), "utf8");
const page = fs.readFileSync(path.join(__dirname, "../docs/index.html"), "utf8");
const migrate = page.slice(page.indexOf("function migrateCardProgress("), page.indexOf("function cardKey("));
const STORE = "cpe-course-progress-v1", DRAFT = "cpe-course-draft:", LEGACY = "cpe-course-interview";
const OLD = {version:1,xp:17,solved:{"1.2":{xp:17}},days:[],opened:{"1.2":null},diagnostic:{unsupported_recovery:"keep"}};
let memory, fail;
const storage = {
  get length() { return memory.size; },
  key(index) { return [...memory.keys()][index] || null; },
  getItem(key) { return memory.has(key) ? memory.get(key) : null; },
  setItem(key,value) { if (fail && fail("set",key)) throw new Error("storage unavailable"); memory.set(key,String(value)); },
  removeItem(key) { if (fail && fail("remove",key)) throw new Error("storage unavailable"); memory.delete(key); },
};
function setup() {
  memory = new Map([[STORE,JSON.stringify(OLD)],[DRAFT+"1.2","old exercise"],[DRAFT+"card:1.1:0","old positional card"],[DRAFT+"card:stable-card","old stable card"],["unrelated-app","keep"]]);
  fail = null;
  const context = vm.createContext({P:JSON.parse(JSON.stringify(OLD)),DATA:{legacy_card_ids:{"1.1:0":"stable-card"}},STORE_KEY:STORE,DRAFT_KEY:DRAFT,LEGACY_INTERVIEW_KEY:LEGACY,localStorage:storage,Date,Math,JSON,Object,Number,Error,nowIso:()=>"2026-09-05T00:00:00.000Z",parseTimestamp:value=>typeof value==="string"&&!Number.isNaN(Date.parse(value))?new Date(value):null,blankProgress:()=>({version:1,xp:0,solved:{},days:[]}),assert,pending:null});
  vm.runInContext(migrate+source,context);
  return context;
}
const run = (context,code) => vm.runInContext(code,context);
const snapshot = () => JSON.stringify([...memory.entries()].sort());
const incoming = {format:"python-cpe-course-backup",version:1,exported_at:"2026-09-05T00:00:00.000Z",progress:{xp:44,solved:{"2.1":{xp:44}},cards:{"1.1:0":{done:true,tries:1}},opened:{"2.1":17},custom:{keep:"nested"}},drafts:{[DRAFT+"1.2"]:"new exercise",[DRAFT+"card:new-id"]:"new card"},custom_wrapper:{retain:[1,true]},recovery_storage:{original:"opaque metadata"}};
const input = JSON.stringify(incoming);

// Preview and every invalid shape leave all live and recovery keys untouched.
let context = setup(); context.input=input;
const before = snapshot();
run(context,`const preview=previewBrowserBackup(input); assert.equal(preview.changed.length,1); assert.equal(preview.removed.length,2); assert.equal(preview.added.length,1);`);
assert.equal(snapshot(),before);
for (const invalid of [{...incoming,version:99},{...incoming,exported_at:"0001-01-01T00:00:00+01:00"},{...incoming,exported_at:"9999-12-31T23:59:59-01:00"},{...incoming,drafts:{outside:"no"}},{...incoming,drafts:{[DRAFT+"1.2"]:3}},{xp:false},{xp:1,cards:[]},{xp:1,days:["2026-02-30"]},{xp:1,attempts:{"1.2":true}},{progress:{xp:1}}]) {
  context.bad=JSON.stringify(invalid);
  run(context,"assert.throws(()=>parseBrowserBackup(bad));");
  assert.equal(snapshot(),before);
}
run(context,`assert.throws(()=>parseBrowserBackup('{"xp":1,"custom":1e999}'));`);

// Full replacement preserves its unknown metadata and leaves a complete old copy.
const key = run(context,"replaceBrowserBackup(preview)");
assert.equal(JSON.parse(memory.get(STORE)).xp,44);
assert.equal(memory.get(DRAFT+"1.2"),"new exercise");
assert.equal(memory.has(DRAFT+"card:stable-card"),false);
assert.equal(memory.get("unrelated-app"),"keep");
const recovery=JSON.parse(memory.get(key));
assert.deepEqual(recovery.progress,OLD);
assert.equal(recovery.drafts[DRAFT+"card:stable-card"],"old stable card");
assert.equal(recovery.recovery_storage[STORE],JSON.stringify(OLD));
const roundtrip=JSON.parse(run(context,"JSON.stringify(makeBrowserBackup())"));
assert.deepEqual(roundtrip.custom_wrapper,incoming.custom_wrapper);
assert.deepEqual(roundtrip.drafts,incoming.drafts);
assert.equal(roundtrip.progress.cards["stable-card"].done,true);

// Legacy import preserves every current draft; current recovery copies survive.
context=setup(); const legacyDrafts=run(context,"JSON.stringify(currentBrowserDrafts())");
run(context,'replaceBrowserBackup(previewBrowserBackup(JSON.stringify({xp:2,solved:{}})))');
assert.equal(run(context,"JSON.stringify(currentBrowserDrafts())"),legacyDrafts);

// No durable recovery space means no live data is touched.
context=setup(); context.input=input; const beforeQuota=snapshot();
fail=(_op,key)=>key.startsWith("cpe-course-backup-recovery:");
run(context,"assert.throws(()=>replaceBrowserBackup(previewBrowserBackup(input)), /retained/);");
assert.equal(snapshot(),beforeQuota);

// Failure after one changed draft rolls back live data, keeping recovery available.
context=setup(); context.input=input; const originalStorage=run(context,"JSON.stringify(captureBackupStorage())");
let once=true;
fail=(op,key)=>{if(once&&op==="set"&&key===DRAFT+"card:new-id"){once=false;return true;}return false;};
run(context,"assert.throws(()=>replaceBrowserBackup(previewBrowserBackup(input)), /retained/);");
assert.equal(run(context,"JSON.stringify(captureBackupStorage())"),originalStorage);
assert.equal(memory.has("cpe-course-backup-pending-v1"),false);
assert.deepEqual(context.P,OLD);

// Persistent failures leave the complete durable copy and block further saves.
context=setup(); context.input=input;
let blocked=false;
fail=(op,key)=>{if(op==="set"&&key===DRAFT+"card:new-id")blocked=true;return blocked;};
run(context,"assert.throws(()=>replaceBrowserBackup(previewBrowserBackup(input)), /recovery copy/); assert.equal(backupImportPending(),true); assert.equal(recoverPendingImport().blocked,true);");
const recoveryKey=memory.get("cpe-course-backup-pending-v1");
assert.deepEqual(JSON.parse(memory.get(recoveryKey)).progress,OLD);
fail=null;
run(context,"assert.equal(recoverPendingImport(),null); assert.equal(backupImportPending(),false);");
assert.equal(memory.get(DRAFT+"1.2"),"old exercise");
assert.equal(memory.get(DRAFT+"card:stable-card"),"old stable card");
assert.equal(memory.has(DRAFT+"card:new-id"),false);
assert.equal(memory.get(STORE),JSON.stringify(OLD));

// Every forward write/removal boundary either commits fully or restores the
// original data, including failures removing the final pending marker.
context=setup(); context.input=input;
let writes=0;
fail=()=>{writes++;return false;};
run(context,"replaceBrowserBackup(previewBrowserBackup(input));");
const writeCount=writes;
for (let boundary=1;boundary<=writeCount;boundary++) for (const persistent of [false,true]) {
  context=setup();context.input=input;
  const original=run(context,"JSON.stringify(captureBackupStorage())");
  let count=0;
  fail=()=>{count++;return persistent?count>=boundary:count===boundary;};
  run(context,"assert.throws(()=>replaceBrowserBackup(previewBrowserBackup(input)));");
  assert.deepEqual(context.P,OLD);
  if (memory.has("cpe-course-backup-pending-v1")) {
    const copy=JSON.parse(memory.get(memory.get("cpe-course-backup-pending-v1")));
    assert.deepEqual(copy.progress,OLD);
    assert.equal(copy.drafts[DRAFT+"card:stable-card"],"old stable card");
  }
  fail=null;
  run(context,"assert.equal(recoverPendingImport(),null);");
  assert.equal(run(context,"JSON.stringify(captureBackupStorage())"),original);
}

// An invalid or future recovery snapshot cannot clear any live data.
for (const corruption of [{version:99},{recovery_storage:{}}]) {
  context=setup(); const recoveryName="cpe-course-backup-recovery:damaged";
  const damaged={...run(context,"makeBrowserBackup()"),recovery_storage:run(context,"captureBackupStorage()"),...corruption};
  memory.set(recoveryName,JSON.stringify(damaged)); memory.set("cpe-course-backup-pending-v1",recoveryName);
  const saved=snapshot();
  run(context,"assert.equal(recoverPendingImport().blocked,true);");
  assert.equal(snapshot(),saved);
}

// A test result or another tab changing the saved state requires a fresh preview.
context=setup();context.input=input;
run(context,"const stale=previewBrowserBackup(input); P.xp++; assert.throws(()=>replaceBrowserBackup(stale), /changed/);");
context=setup();context.input=input;
run(context,"pending={id:'worker'}; assert.throws(()=>replaceBrowserBackup(previewBrowserBackup(input)), /running tests/);");
assert.equal(memory.size,5);

// Emit a real envelope for the Python reader to validate without losing drafts.
process.stdout.write(JSON.stringify(roundtrip));
