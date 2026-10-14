"use strict";

// Staged tree (docs/agents/tingle-js-complexity-image.md,
// "Contract", "Staged tree"). Accepted line <n> is copied to
// /tmp/stage/plain/<n>.<ext>: opaque names dodge FTA's built-in filters, and
// copies (not symlinks) because FTA does not follow symlinks.
//
// A .vue, .svelte or .astro component is not copied: its script blocks are
// extracted (lib/sfc.js) into a padded virtual module written to
// /tmp/stage/sfc/<n>.<ext>.<vext> (<vext> = ts, tsx, js or jsx), which keeps
// the component's line numbers
// (docs/agents/tingle-js-complexity-image.md, "Single-file components").

const fs = require("fs");
const path = require("path");
const { decodeUtf8 } = require("./input");
const { SFC_EXTENSIONS, extractSfc } = require("./sfc");

const STAGE_DIR = "/tmp/stage";
const PLAIN_DIR = path.join(STAGE_DIR, "plain");
const SFC_DIR = path.join(STAGE_DIR, "sfc");

function stagePlain(number, bytes, ext) {
  fs.mkdirSync(PLAIN_DIR, { recursive: true });
  fs.writeFileSync(path.join(PLAIN_DIR, `${number}.${ext}`), bytes);
  return { staged: true };
}

function stageSfc(number, text, ext) {
  const result = extractSfc(text, ext);
  if (result.error) return { extractionError: result.error };
  fs.mkdirSync(SFC_DIR, { recursive: true });
  fs.writeFileSync(path.join(SFC_DIR, `${number}.${ext}.${result.vext}`), result.code);
  return { staged: true };
}

// Stages the file of input line `number` (`ext` lower-cased). Returns
// {staged: true}, {invalidUtf8: true} (nothing staged) or
// {extractionError: "<message>"} (an SFC whose scripts cannot be extracted;
// nothing staged).
function stageFile(number, realPath, ext) {
  const bytes = fs.readFileSync(realPath);
  const text = decodeUtf8(bytes, true);
  if (text === null) return { invalidUtf8: true };
  if (SFC_EXTENSIONS.has(ext)) return stageSfc(number, text, ext);
  return stagePlain(number, bytes, ext);
}

// Input line number <n> of a staged path relative to STAGE_DIR
// ("plain/6.ts", "sfc/5.vue.ts"), or null.
function stagedNumber(relativePath) {
  const match = /^(?:plain|sfc)\/(\d+)\.[^/]+$/.exec(relativePath);
  return match ? Number(match[1]) : null;
}

// Map: input line number -> byte size of its staged copy, for every file
// under STAGE_DIR.
function stagedSizes() {
  const sizes = new Map();
  for (const sub of ["plain", "sfc"]) {
    const dir = path.join(STAGE_DIR, sub);
    if (!fs.existsSync(dir)) continue;
    for (const name of fs.readdirSync(dir)) {
      const number = stagedNumber(`${sub}/${name}`);
      if (number !== null) sizes.set(number, fs.statSync(path.join(dir, name)).size);
    }
  }
  return sizes;
}

module.exports = { STAGE_DIR, stageFile, stagedNumber, stagedSizes };
