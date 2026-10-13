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
//         FTA's stderr and jscpd's stdout and stderr are passed through to
//         stderr.
// Exit:   0 when the JSON was printed; FTA's status when FTA exits non-zero;
//         1 on any other failure ("tingle_js_complexity: <reason>" on stderr).
//         Nothing is printed on stdout on failure. A jscpd failure is not a
//         failure: every files[].duplication is null and one path-less
//         "jscpd" warning is added.
//
// Accepted files are copied to /tmp/stage/plain/<n>.<ext> (<n> = input line
// number) and FTA, then jscpd, run on that tree, never on /src. Nothing is
// written outside /tmp.
//
// Dependencies: Node standard library, /usr/local/bin/fta (FTA 3.1.0),
// /opt/tingle_js_complexity/node_modules/.bin/jscpd (jscpd 5.4.1).
//
// Contract: docs/agents/specs/code_check/js_complexity/image.md and
// docs/agents/specs/code_check/js_complexity/duplication.md.

const { EntrypointError } = require("./lib/errors");
const { readInputLines } = require("./lib/input");
const { realSrcRoot, selectLine } = require("./lib/selection");
const { stageFile } = require("./lib/staging");
const { applyFtaStderr, applyFtaStdout, ftaVersion, runFta } = require("./lib/fta");
const { applyJscpd, jscpdVersion } = require("./lib/jscpd");

function newEntry(line) {
  return { path: line, parse_error: false, fta: null, duplication: null, functions: null };
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
    } else if (stageFile(number, selection.realPath, selection.ext)) {
      staged.add(number);
    } else {
      entry.parse_error = true;
      warnings.push({ tool: "fta", path: line, message: "file is not valid UTF-8" });
    }
  });
  return staged;
}

function analyse(lines) {
  const files = [];
  const warnings = [];
  const fta = ftaVersion();
  const jscpd = jscpdVersion();
  const staged = stageLines(lines, files, warnings);
  if (staged.size > 0) {
    const result = runFta();
    applyFtaStderr(result.stderr, files, staged, warnings);
    applyFtaStdout(result.stdout, files, staged);
    applyJscpd(files, staged, warnings);
  }
  return { tool_versions: { fta, jscpd, escomplex: null }, files, warnings };
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
