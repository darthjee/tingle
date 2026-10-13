"use strict";

// jscpd invocation and per-file duplicated lines
// (docs/agents/specs/code_check/js_complexity/duplication.md).
//
// A jscpd failure is never fatal: every file keeps `duplication: null` and
// one path-less {tool: "jscpd", message} warning is added.

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");
const { EntrypointError } = require("./errors");
const { STAGE_DIR, stagedNumber, stagedSizes } = require("./staging");

const JSCPD_HOME = "/opt/tingle_js_complexity/node_modules/jscpd";
const JSCPD = "/opt/tingle_js_complexity/node_modules/.bin/jscpd";
const OUTPUT_DIR = "/tmp/jscpd";
const REPORT_NAME = "jscpd";
const REPORT_PATH = path.join(OUTPUT_DIR, `${REPORT_NAME}.json`);
const MAX_SIZE = 1024 * 1024; // --max-size 1mb
// A file jscpd reads has at most MAX_SIZE bytes, so at most MAX_SIZE + 1 lines.
const MAX_LINE = MAX_SIZE + 1;
const ARGS = [
  STAGE_DIR,
  "--reporters", "json", "--output", OUTPUT_DIR, "--report-name", REPORT_NAME,
  "--silent", "--no-tips", "--no-colors",
  "--min-tokens", "50", "--min-lines", "5", "--mode", "mild", "--kind", "exact",
  "--format", "javascript,typescript,jsx,tsx",
  "--formats-exts", "javascript:js,mjs,cjs;typescript:ts,mts,cts;jsx:jsx;tsx:tsx",
  "--cross-formats", "js-ts",
  "--no-gitignore", "--max-size", "1mb",
];
const MAX_BUFFER = 1024 * 1024 * 1024;

// Soft failure: the reason ends up in the jscpd warning.
class JscpdError extends Error {}

// "5.4.1", from jscpd's own package.json.
function jscpdVersion() {
  let version;
  try {
    version = JSON.parse(fs.readFileSync(path.join(JSCPD_HOME, "package.json"), "utf8")).version;
  } catch (error) {
    throw new EntrypointError(`cannot read the jscpd version: ${error.message}`);
  }
  if (typeof version !== "string") throw new EntrypointError("cannot read the jscpd version");
  return version;
}

// Runs jscpd on the staged tree. Its stdout (a summary, printed even with
// --silent) and stderr both go to stderr: stdout holds only the JSON.
function runJscpd() {
  fs.rmSync(OUTPUT_DIR, { recursive: true, force: true });
  const result = spawnSync(JSCPD, ARGS, { cwd: "/tmp", maxBuffer: MAX_BUFFER });
  if (result.stdout) process.stderr.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  if (result.error) throw new JscpdError(`jscpd: ${result.error.message}`);
  if (result.signal) throw new JscpdError(`jscpd killed by ${result.signal}`);
  if (result.status !== 0) throw new JscpdError(`jscpd exited with status ${result.status}`);
}

function readReport() {
  let text;
  try {
    text = fs.readFileSync(REPORT_PATH, "utf8");
  } catch (_error) {
    throw new JscpdError(`jscpd report ${REPORT_PATH} is missing`);
  }
  try {
    return JSON.parse(text);
  } catch (_error) {
    throw new JscpdError(`jscpd report ${REPORT_PATH} is not valid JSON`);
  }
}

// {number, start, end} of one clone side, validated.
function cloneSide(side, staged) {
  const valid = side && typeof side === "object" && typeof side.name === "string"
    && Number.isInteger(side.start) && Number.isInteger(side.end)
    && side.start >= 1 && side.end >= side.start && side.end <= MAX_LINE;
  if (!valid) throw new JscpdError("jscpd report has a malformed duplicates entry");
  const number = stagedNumber(side.name);
  if (number === null || !staged.has(number)) {
    throw new JscpdError(`jscpd reported an unknown path: ${side.name}`);
  }
  return { number, start: side.start, end: side.end };
}

// Map: input line number -> Set of duplicated line numbers.
function coveredLines(report, staged) {
  const duplicates = report && typeof report === "object" ? report.duplicates : undefined;
  if (!Array.isArray(duplicates)) throw new JscpdError("jscpd report has no duplicates list");
  const covered = new Map();
  for (const clone of duplicates) {
    if (!clone || typeof clone !== "object") {
      throw new JscpdError("jscpd report has a malformed duplicates entry");
    }
    for (const side of [cloneSide(clone.firstFile, staged), cloneSide(clone.secondFile, staged)]) {
      if (!covered.has(side.number)) covered.set(side.number, new Set());
      const lines = covered.get(side.number);
      for (let line = side.start; line <= side.end; line += 1) lines.add(line);
    }
  }
  return covered;
}

// Runs jscpd and fills files[].duplication. Never throws on a jscpd failure.
function applyJscpd(files, staged, warnings) {
  let covered;
  try {
    runJscpd();
    covered = coveredLines(readReport(), staged);
  } catch (error) {
    if (!(error instanceof JscpdError)) throw error;
    for (const entry of files) entry.duplication = null;
    warnings.push({ tool: "jscpd", message: error.message.split("\n")[0] });
    return;
  }
  const sizes = stagedSizes();
  for (const number of staged) {
    const entry = files[number - 1];
    const size = sizes.get(number);
    if (entry.parse_error || size === undefined || size > MAX_SIZE) continue;
    const lines = covered.get(number);
    entry.duplication = { lines: lines ? lines.size : 0 };
  }
}

module.exports = { applyJscpd, jscpdVersion };
