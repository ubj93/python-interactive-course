// Web worker: loads Pyodide once and runs one exercise's unittest suite per message.
// Keeping Python off the main thread lets the page stay responsive and lets us kill
// runaway code (infinite loops) by terminating the worker.
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";
importScripts(PYODIDE_URL + "pyodide.js");

let pyodideReady = null;

function boot() {
  if (!pyodideReady) {
    pyodideReady = loadPyodide({ indexURL: PYODIDE_URL }).then((py) => {
      py.FS.mkdirTree("/course/ex");
      return py;
    });
  }
  return pyodideReady;
}

function writeFile(py, path, content) {
  const dir = path.substring(0, path.lastIndexOf("/"));
  if (dir) py.FS.mkdirTree(dir);
  if (typeof content === "string") {
    py.FS.writeFile(path, content, { encoding: "utf8" });
  } else if (content && content.base64) {
    const bin = atob(content.base64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    py.FS.writeFile(path, bytes);
  } else if (content && typeof content.text === "string") {
    py.FS.writeFile(path, content.text, { encoding: "utf8" });
  }
}

function rmTree(py, path) {
  try {
    const entries = py.FS.readdir(path).filter((n) => n !== "." && n !== "..");
    for (const name of entries) {
      const p = path + "/" + name;
      const st = py.FS.stat(p);
      if (py.FS.isDir(st.mode)) rmTree(py, p);
      else py.FS.unlink(p);
    }
    py.FS.rmdir(path);
  } catch (e) {
    /* did not exist */
  }
}

self.onmessage = async (event) => {
  const msg = event.data;
  if (msg.type === "boot") {
    try {
      self.postMessage({ type: "status", msg: "Loading Python runtime (about 10 MB, cached after the first time)…" });
      await boot();
      self.postMessage({ type: "ready" });
    } catch (e) {
      self.postMessage({ type: "error", id: null, error: String(e) });
    }
    return;
  }
  if (msg.type !== "run") return;
  try {
    const py = await boot();
    writeFile(py, "/course/harness.py", msg.harness);
    const dir = "/course/ex/" + msg.slug;
    rmTree(py, dir);
    py.FS.mkdirTree(dir);
    for (const [name, content] of Object.entries(msg.files)) {
      writeFile(py, dir + "/" + name, content);
    }
    py.setStdout({ batched: () => {} });
    py.setStderr({ batched: () => {} });
    const code = [
      "import sys, json, importlib",
      "if '/course' not in sys.path: sys.path.insert(0, '/course')",
      "import harness",
      "importlib.reload(harness)",
      "json.dumps(harness.run(" + JSON.stringify(dir) + "))",
    ].join("\n");
    const out = await py.runPythonAsync(code);
    self.postMessage({ type: "result", id: msg.id, result: JSON.parse(out) });
  } catch (e) {
    self.postMessage({ type: "error", id: msg.id, error: String(e && e.message ? e.message : e) });
  }
};
