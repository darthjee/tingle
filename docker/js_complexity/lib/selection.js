"use strict";

// Refused lines (docs/agents/tingle-js-complexity-image.md, "Contract",
// "Refused lines"). Every line is checked in order; the first rule that
// matches refuses it.

const fs = require("fs");
const path = require("path");
const { SFC_EXTENSIONS } = require("./sfc");

const SRC = "/src";
const EXTENSIONS = new Set([
  "js", "mjs", "cjs", "jsx", "ts", "mts", "cts", "tsx", ...SFC_EXTENSIONS,
]);

// Lower-cased text after the last "." of the base name, or null.
function extensionOf(line) {
  const base = line.slice(line.lastIndexOf("/") + 1);
  const dot = base.lastIndexOf(".");
  return dot === -1 ? null : base.slice(dot + 1).toLowerCase();
}

function realSrcRoot() {
  try {
    return fs.realpathSync(SRC);
  } catch (_error) {
    return SRC;
  }
}

// Real path of /src/<line> when it is a regular file inside /src, else null.
function regularFileUnderSrc(line, srcRoot) {
  let real;
  try {
    real = fs.realpathSync(path.join(SRC, line));
    if (!fs.statSync(real).isFile()) return null;
  } catch (_error) {
    return null;
  }
  return real.startsWith(srcRoot + path.sep) ? real : null;
}

// Rules that need no file system access.
function syntacticRefusal(line, seen) {
  if (line === "") return "empty line";
  if (line.startsWith("/")) return "absolute path";
  if (line.split("/").includes("..")) return "path has a '..' segment";
  if (seen.has(line)) return "duplicate line";
  return null;
}

// Classifies one line. Returns {refusal} or {realPath, ext}. `seen` holds
// every earlier line (refused or not) and is updated here.
function selectLine(line, seen, srcRoot) {
  const refusal = syntacticRefusal(line, seen);
  seen.add(line);
  if (refusal) return { refusal };
  const realPath = regularFileUnderSrc(line, srcRoot);
  if (!realPath) return { refusal: "not a regular file under /src" };
  const ext = extensionOf(line);
  if (!EXTENSIONS.has(ext)) return { refusal: "unsupported extension" };
  return { realPath, ext };
}

module.exports = { extensionOf, realSrcRoot, selectLine };
