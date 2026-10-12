"use strict";

// Reads stdin and splits it into input lines (image.md section 4, "Lines").

const fs = require("fs");
const { EntrypointError } = require("./errors");

// Decodes `bytes` as UTF-8, or returns null when they are not valid UTF-8.
// A leading BOM is accepted.
function decodeUtf8(bytes) {
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch (_error) {
    return null;
  }
}

// Splits on "\n". A final "\n" does not start an extra line. Nothing is
// trimmed.
function splitLines(text) {
  if (text === "") return [];
  const lines = text.split("\n");
  if (text.endsWith("\n")) lines.pop();
  return lines;
}

// Returns the input lines read from stdin (fd 0).
function readInputLines() {
  const text = decodeUtf8(fs.readFileSync(0));
  if (text === null) throw new EntrypointError("stdin is not valid UTF-8");
  return splitLines(text);
}

module.exports = { decodeUtf8, readInputLines, splitLines };
