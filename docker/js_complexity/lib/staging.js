"use strict";

// Staged tree (image.md section 5). Accepted line <n> is copied to
// /tmp/stage/plain/<n>.<ext>: opaque names dodge FTA's built-in filters, and
// copies (not symlinks) because FTA does not follow symlinks.

const fs = require("fs");
const path = require("path");
const { decodeUtf8 } = require("./input");

const STAGE_DIR = "/tmp/stage";
const PLAIN_DIR = path.join(STAGE_DIR, "plain");

// Stages the file of input line `number`. Returns false (nothing staged)
// when its content is not valid UTF-8.
function stageFile(number, realPath, ext) {
  const bytes = fs.readFileSync(realPath);
  if (decodeUtf8(bytes) === null) return false;
  fs.mkdirSync(PLAIN_DIR, { recursive: true });
  fs.writeFileSync(path.join(PLAIN_DIR, `${number}.${ext}`), bytes);
  return true;
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
