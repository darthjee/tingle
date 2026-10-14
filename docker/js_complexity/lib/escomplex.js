"use strict";

// typhonjs-escomplex wrapper and the entrypoint helpers that drive it
// (docs/agents/tingle-js-complexity-image.md, "Contract").
//
// Wrapper usage (inside the container):
//   echo '["/tmp/stage/plain/1.ts"]' | node /opt/tingle_js_complexity/lib/escomplex.js
//
// Input:  stdin, a JSON array of staged file paths
//         (/tmp/stage/plain/<n>.<ext>, /tmp/stage/sfc/<n>.<ext>.<ts|tsx|js|jsx>).
// Output: stdout, one JSON object mapping each path to
//         {"functions": [{name, line, cyclo, sloc}, ...]} or
//         {"error": "<one-line message>"}.
// Exit:   0 when the object was printed, 1 when the input is not a JSON
//         array of strings.
//
// The entrypoint runs the wrapper as a separate process, so a crash or an
// out-of-memory error in escomplex cannot take it down: only the wrapper
// process loads typhonjs-escomplex. A wrapper failure is never fatal: every
// file keeps `functions: null` and one path-less {tool: "escomplex", message}
// warning is added.
//
// Dependencies: Node standard library,
// /opt/tingle_js_complexity/node_modules/typhonjs-escomplex (0.1.0).

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const { EntrypointError } = require("./errors");
const { STAGE_DIR, stagedNumber } = require("./staging");

const ESCOMPLEX_HOME = "/opt/tingle_js_complexity/node_modules/typhonjs-escomplex";
const WRAPPER = __filename;
const MAX_BUFFER = 1024 * 1024 * 1024;

// escomplex's defaults, made explicit (see the escomplex part of "Contract").
const MODULE_OPTIONS = { logicalor: true, switchcase: true, forin: false, trycatch: false, newmi: false };

const COMMON = [
  "decorators-legacy", "classProperties", "classPrivateProperties", "classPrivateMethods",
  "dynamicImport", "importMeta", "topLevelAwait", "optionalChaining",
  "nullishCoalescingOperator", "logicalAssignment", "numericSeparator",
  "objectRestSpread", "optionalCatchBinding", "exportDefaultFrom",
];

// Parser plugins by the staged file's last extension.
const PLUGINS = {
  ts: ["typescript", ...COMMON],
  mts: ["typescript", ...COMMON],
  cts: ["typescript", ...COMMON],
  tsx: ["typescript", "jsx", ...COMMON],
  js: ["jsx", ...COMMON],
  mjs: ["jsx", ...COMMON],
  cjs: ["jsx", ...COMMON],
  jsx: ["jsx", ...COMMON],
};

// Soft failure: the reason ends up in the escomplex warning.
class EscomplexError extends Error {}

function oneLine(message) {
  return String(message).split("\n")[0];
}

function isPositiveInt(value) {
  return Number.isInteger(value) && value >= 1;
}

function isFunctionEntry(f) {
  return f && typeof f === "object" && typeof f.name === "string"
    && isPositiveInt(f.line) && isPositiveInt(f.cyclo) && isPositiveInt(f.sloc);
}

// ---------------------------------------------------------------------------
// Wrapper process
// ---------------------------------------------------------------------------

function pluginsFor(stagedPath) {
  const ext = path.extname(stagedPath).slice(1).toLowerCase();
  const plugins = PLUGINS[ext];
  if (!plugins) throw new Error(`unsupported extension: .${ext}`);
  return plugins;
}

function toFunction(method, name) {
  return {
    name,
    line: method.lineStart,
    cyclo: method.cyclomatic,
    sloc: method.sloc && method.sloc.physical,
  };
}

function compareFunctions(a, b) {
  if (a.line !== b.line) return a.line - b.line;
  if (a.name < b.name) return -1;
  return a.name > b.name ? 1 : 0;
}

// Flattens methods and classes[].methods of one module report.
function functionsOf(report) {
  const functions = (report.methods || []).map((m) => toFunction(m, m.name));
  for (const klass of report.classes || []) {
    const className = klass.name || "<anonymous>";
    for (const m of klass.methods || []) functions.push(toFunction(m, `${className}.${m.name}`));
  }
  for (const f of functions) {
    if (!isFunctionEntry(f)) throw new Error(`malformed escomplex function entry: ${f.name}`);
  }
  return functions.sort(compareFunctions);
}

function analyseFile(escomplex, stagedPath) {
  try {
    const source = fs.readFileSync(stagedPath, "utf8");
    const report = escomplex.analyzeModule(source, MODULE_OPTIONS, {
      sourceType: "unambiguous", plugins: pluginsFor(stagedPath),
    });
    return { functions: functionsOf(report) };
  } catch (error) {
    const message = error && error.message ? error.message : String(error);
    return { error: oneLine(message) };
  }
}

function wrapperMain() {
  let paths;
  try {
    paths = JSON.parse(fs.readFileSync(0, "utf8"));
  } catch (_error) {
    paths = null;
  }
  if (!Array.isArray(paths) || !paths.every((p) => typeof p === "string")) {
    process.stderr.write("escomplex wrapper: stdin is not a JSON array of paths\n");
    process.exitCode = 1;
    return;
  }
  const escomplex = require(ESCOMPLEX_HOME); // eslint-disable-line global-require
  const result = {};
  for (const stagedPath of paths) result[stagedPath] = analyseFile(escomplex, stagedPath);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

// ---------------------------------------------------------------------------
// Entrypoint helpers
// ---------------------------------------------------------------------------

// "0.1.0", from typhonjs-escomplex's own package.json.
function escomplexVersion() {
  let version;
  try {
    version = JSON.parse(fs.readFileSync(path.join(ESCOMPLEX_HOME, "package.json"), "utf8")).version;
  } catch (error) {
    throw new EntrypointError(`cannot read the escomplex version: ${error.message}`);
  }
  if (typeof version !== "string") throw new EntrypointError("cannot read the escomplex version");
  return version;
}

// Map: input line number -> absolute staged path, for every file under
// STAGE_DIR.
function stagedPaths() {
  const paths = new Map();
  for (const sub of ["plain", "sfc"]) {
    const dir = path.join(STAGE_DIR, sub);
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      const number = stagedNumber(`${sub}/${name}`);
      if (number !== null) paths.set(number, path.join(dir, name));
    }
  }
  return paths;
}

// Runs the wrapper on `paths`. Returns its parsed stdout object.
function runWrapper(paths) {
  const result = spawnSync(process.execPath, [WRAPPER], {
    cwd: "/tmp", input: JSON.stringify(paths), encoding: "utf8", maxBuffer: MAX_BUFFER,
  });
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.error) throw new EscomplexError(`escomplex: ${result.error.message}`);
  if (result.signal) throw new EscomplexError(`escomplex killed by ${result.signal}`);
  if (result.status !== 0) throw new EscomplexError(`escomplex exited with status ${result.status}`);
  let output;
  try {
    output = JSON.parse(result.stdout);
  } catch (_error) {
    output = null;
  }
  if (!output || typeof output !== "object" || Array.isArray(output)) {
    throw new EscomplexError("escomplex output is not a JSON object");
  }
  return output;
}

// Checks the wrapper output against the sent paths. Returns
// Map: staged path -> {functions} | {error}.
function validateOutput(output, sent) {
  const results = new Map();
  for (const [key, value] of Object.entries(output)) {
    if (!sent.has(key)) throw new EscomplexError(`escomplex reported an unknown path: ${key}`);
    const valid = value && typeof value === "object" && (
      typeof value.error === "string"
      || (Array.isArray(value.functions) && value.functions.every(isFunctionEntry)));
    if (!valid) throw new EscomplexError(`escomplex output has a malformed entry: ${key}`);
    results.set(key, value);
  }
  for (const stagedPath of sent.keys()) {
    if (!results.has(stagedPath)) throw new EscomplexError(`escomplex did not report ${stagedPath}`);
  }
  return results;
}

function copyFunction(f) {
  return { name: f.name, line: f.line, cyclo: f.cyclo, sloc: f.sloc };
}

// Runs the wrapper on the staged files FTA parsed and fills
// files[].functions. Never throws on an escomplex failure.
function applyEscomplex(files, staged, warnings) {
  const sent = new Map(); // staged path -> files[] entry
  const allPaths = stagedPaths();
  for (const number of [...staged].sort((a, b) => a - b)) {
    const entry = files[number - 1];
    const stagedPath = allPaths.get(number);
    if (entry.parse_error || stagedPath === undefined) continue;
    sent.set(stagedPath, entry);
  }
  if (sent.size === 0) return;
  let results;
  try {
    results = validateOutput(runWrapper([...sent.keys()]), sent);
  } catch (error) {
    if (!(error instanceof EscomplexError)) throw error;
    for (const entry of files) entry.functions = null;
    warnings.push({ tool: "escomplex", message: oneLine(error.message) });
    return;
  }
  for (const [stagedPath, entry] of sent) {
    const value = results.get(stagedPath);
    if (typeof value.error === "string") {
      entry.functions = null;
      warnings.push({ tool: "escomplex", path: entry.path, message: oneLine(value.error) });
    } else {
      entry.functions = value.functions.map(copyFunction);
    }
  }
}

if (require.main === module) wrapperMain();

module.exports = { applyEscomplex, escomplexVersion };
