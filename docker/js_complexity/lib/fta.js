"use strict";

// FTA invocation and parsing (image.md section 6).

const fs = require("fs");
const { spawnSync } = require("child_process");
const { EntrypointError } = require("./errors");
const { STAGE_DIR, stagedNumber } = require("./staging");

const FTA = "/usr/local/bin/fta";
const CONFIG_PATH = "/tmp/fta.json";
const CONFIG = { extensions: [".mjs", ".cjs", ".mts", ".cts"] };
const ARGS = [
  STAGE_DIR, "--json",
  "--config-path", CONFIG_PATH,
  "--score-cap", "1000000000",
  "--exclude-under", "0",
  "--include-comments", "false",
];
const FAILED_RE = /Failed to analyze \/tmp\/stage\/(plain|sfc)\/(\d+)\.\S*: (.*)$/;
const MAX_BUFFER = 1024 * 1024 * 1024;

// process.env without DEBUG (FTA switches to debug logging when it is set).
function ftaEnv() {
  const env = { ...process.env };
  delete env.DEBUG;
  return env;
}

function spawnFta(args) {
  const result = spawnSync(FTA, args, {
    cwd: "/tmp", env: ftaEnv(), encoding: "utf8", maxBuffer: MAX_BUFFER,
  });
  if (result.error) throw new EntrypointError(`fta: ${result.error.message}`);
  if (result.signal) throw new EntrypointError(`fta killed by ${result.signal}`);
  return result;
}

// "fta 3.1.0" -> "3.1.0".
function ftaVersion() {
  const result = spawnFta(["--version"]);
  const match = /^fta (\S+)\s*$/.exec(result.stdout);
  if (result.status !== 0 || !match) {
    throw new EntrypointError("fta --version failed");
  }
  return match[1];
}

// Runs FTA on the staged tree. Returns {stdout, stderr}; a non-zero status is
// passed through as the exit status.
function runFta() {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(CONFIG));
  const result = spawnFta(ARGS);
  process.stderr.write(result.stderr);
  if (result.status !== 0) {
    throw new EntrypointError(`fta exited with status ${result.status}`, result.status);
  }
  return result;
}

// Entry of the staged input line `number`, or a fatal error.
function stagedEntry(files, staged, number, toolPath) {
  if (number === null || !staged.has(number)) {
    throw new EntrypointError(`fta reported an unknown path: ${toolPath}`);
  }
  return files[number - 1];
}

// Marks the files FTA logged as "Failed to analyze" as parse errors.
function applyFtaStderr(stderr, files, staged, warnings) {
  for (const logLine of stderr.split(/\r?\n/)) {
    const match = FAILED_RE.exec(logLine);
    if (!match) continue;
    const entry = stagedEntry(files, staged, Number(match[2]), logLine);
    entry.parse_error = true;
    entry.fta = null;
    warnings.push({ tool: "fta", path: entry.path, message: match[3] });
  }
}

function parseFtaJson(stdout) {
  let report;
  try {
    report = JSON.parse(stdout);
  } catch (_error) {
    report = null;
  }
  if (!Array.isArray(report)) {
    throw new EntrypointError("fta output is not a JSON array");
  }
  return report;
}

// Fills files[].fta from FTA's JSON array.
function applyFtaStdout(stdout, files, staged) {
  for (const item of parseFtaJson(stdout)) {
    const name = item && item.file_name;
    const entry = stagedEntry(files, staged, stagedNumber(String(name)), name);
    if (entry.parse_error) continue;
    entry.fta = {
      score: item.fta_score,
      cyclo: item.cyclo,
      lines: item.line_count,
      assessment: item.assessment,
    };
  }
}

module.exports = { applyFtaStderr, applyFtaStdout, ftaVersion, runFta };
