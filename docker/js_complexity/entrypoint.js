"use strict";

// Entrypoint of the tingle_js_complexity image
// (`tingle code_check js_complexity`).
//
// Usage (inside the container, /src mounted read-only):
//   printf '%s\n' src/a.ts lib/b.js | node /opt/tingle_js_complexity/entrypoint.js
//
// Input:  stdin, one path per line, relative to /src. Split on "\n" (a final
//         "\n" adds no line), nothing trimmed. Arguments are ignored. Lines
//         that are empty, absolute, contain a ".." segment, are duplicates,
//         are not a regular file under /src or have an unsupported extension
//         are refused (an "entrypoint" warning, never analysed).
// Output: stdout, exactly one JSON object followed by "\n":
//           {"tool_versions": {"fta", "jscpd", "escomplex"},
//            "files": [one entry per input line, in input order:
//                      {path, parse_error, fta, duplication, functions}],
//            "warnings": [{tool, path?, message}]}
//         FTA's stderr, jscpd's stdout and stderr and the escomplex
//         wrapper's stderr are passed through to stderr.
// Exit:   0 when the JSON was printed; FTA's status when FTA exits non-zero;
//         1 on any other failure ("tingle_js_complexity: <reason>" on stderr).
//         Nothing is printed on stdout on failure. A jscpd failure is not a
//         failure: every files[].duplication is null and one path-less
//         "jscpd" warning is added. Neither is an escomplex failure: a file
//         escomplex cannot parse gets functions: null and an "escomplex"
//         warning with its path; a wrapper failure sets every
//         files[].functions to null and adds one path-less "escomplex"
//         warning.
//
// Accepted extensions: js, mjs, cjs, jsx, ts, mts, cts, tsx, and the
// single-file components vue, svelte and astro (compared on the lower-cased
// last extension).
//
// Accepted files are copied to /tmp/stage/plain/<n>.<ext> (<n> = input line
// number). For a .vue, .svelte or .astro component, only its <script> blocks
// (and Astro frontmatter) are kept, padded with spaces so the original line
// numbers do not move, in /tmp/stage/sfc/<n>.<ext>.<ts|tsx|js|jsx>; a
// component whose scripts cannot be extracted (unsupported <script lang>,
// unterminated frontmatter) gets parse_error: true and an "entrypoint"
// warning with its path. FTA, then jscpd, then the escomplex wrapper (a
// separate node process, lib/escomplex.js) run on that tree, never on /src.
// Nothing is written outside /tmp.
//
// Dependencies: Node standard library, /usr/local/bin/fta (FTA 3.1.0),
// /opt/tingle_js_complexity/node_modules/.bin/jscpd (jscpd 5.4.1),
// /opt/tingle_js_complexity/node_modules/typhonjs-escomplex
// (typhonjs-escomplex 0.1.0, loaded only by lib/escomplex.js).
//
// Contract: docs/agents/tingle-js-complexity-image.md ("Contract").

const { EntrypointError } = require("./lib/errors");
const { readInputLines } = require("./lib/input");
const { realSrcRoot, selectLine } = require("./lib/selection");
const { stageFile } = require("./lib/staging");
const { applyFtaStderr, applyFtaStdout, ftaVersion, runFta } = require("./lib/fta");
const { applyJscpd, jscpdVersion } = require("./lib/jscpd");
const { applyEscomplex, escomplexVersion } = require("./lib/escomplex");

function newEntry(line) {
  return { path: line, parse_error: false, fta: null, duplication: null, functions: null };
}

// Records the outcome of stageFile for input line `number`.
function recordStaging(outcome, number, entry, staged, warnings) {
  if (outcome.staged) {
    staged.add(number);
    return;
  }
  entry.parse_error = true;
  if (outcome.invalidUtf8) {
    warnings.push({ tool: "fta", path: entry.path, message: "file is not valid UTF-8" });
  } else {
    warnings.push({ tool: "entrypoint", path: entry.path, message: outcome.extractionError });
  }
}

// Builds files[] and stages the accepted lines. Returns the set of staged
// input line numbers.
function stageLines(lines, files, warnings) {
  const seen = new Set();
  const staged = new Set();
  const srcRoot = realSrcRoot();
  lines.forEach((line, index) => {
    const number = index + 1;
    const entry = newEntry(line);
    files.push(entry);
    const selection = selectLine(line, seen, srcRoot);
    if (selection.refusal) {
      warnings.push({ tool: "entrypoint", path: line, message: selection.refusal });
    } else {
      recordStaging(stageFile(number, selection.realPath, selection.ext), number, entry, staged, warnings);
    }
  });
  return staged;
}

function analyse(lines) {
  const files = [];
  const warnings = [];
  const fta = ftaVersion();
  const jscpd = jscpdVersion();
  const escomplex = escomplexVersion();
  const staged = stageLines(lines, files, warnings);
  if (staged.size > 0) {
    const result = runFta();
    applyFtaStderr(result.stderr, files, staged, warnings);
    applyFtaStdout(result.stdout, files, staged);
    applyJscpd(files, staged, warnings);
    applyEscomplex(files, staged, warnings);
  }
  return { tool_versions: { fta, jscpd, escomplex }, files, warnings };
}

function fail(error) {
  const reason = error && error.message ? error.message : String(error);
  process.stderr.write(`tingle_js_complexity: ${reason.split("\n")[0]}\n`);
  process.exitCode = error instanceof EntrypointError ? error.status : 1;
}

function main() {
  let output;
  try {
    output = analyse(readInputLines());
  } catch (error) {
    fail(error);
    return;
  }
  process.stdout.write(`${JSON.stringify(output)}\n`);
}

main();
