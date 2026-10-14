"use strict";

// Script extraction for .vue, .svelte and .astro single-file components
// (docs/agents/specs/code_check/js_complexity/sfc.md, sections 2-4).
//
// Pure functions, no file system access. extractSfc(text, ext) returns
// {error: "<message>"} or {code, vext}: `code` is the original text with
// every character outside the kept script contents replaced by a space and
// every line terminator kept, so line L of `code` is line L of the
// component (the line map is the identity). `vext` is the virtual module's
// extension: "tsx", "ts", "jsx" or "js".

const SFC_EXTENSIONS = new Set(["vue", "svelte", "astro"]);

const BOM = "﻿";
const OPEN_TAG_RE = /<script\b[^>]*>/gi;
const CLOSE_TAG_RE = /<\/script\s*>/gi;
const ATTRIBUTE_RE = /([^\s"'=<>/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g;
const CODE_TYPES = new Set(["module", "text/javascript", "application/javascript"]);

// lang attribute (lower-cased) -> {ts, jsx}.
const LANGUAGES = {
  js: { ts: false, jsx: false },
  javascript: { ts: false, jsx: false },
  jsx: { ts: false, jsx: true },
  ts: { ts: true, jsx: false },
  typescript: { ts: true, jsx: false },
  tsx: { ts: true, jsx: true },
};
const TS = LANGUAGES.ts;
const JS = LANGUAGES.js;

class ExtractionError extends Error {}

// Lines of `text` as {start, end, next}: [start, end) is the content without
// its terminator, `next` the offset of the following line.
function* lineSpans(text, from) {
  const re = /\r\n|\n|\r/g;
  re.lastIndex = from;
  let start = from;
  while (start <= text.length) {
    const match = re.exec(text);
    if (!match) {
      yield { start, end: text.length, next: text.length + 1 };
      return;
    }
    yield { start, end: match.index, next: re.lastIndex };
    start = re.lastIndex;
  }
}

// Astro frontmatter: {start, end, after} of its content, or null when the
// first line (after `offset`, the BOM length) is not exactly "---".
function frontmatter(text, offset) {
  const lines = lineSpans(text, offset);
  const first = lines.next().value;
  if (text.slice(first.start, first.end) !== "---") return null;
  for (const line of lines) {
    if (text.slice(line.start, line.end) === "---") {
      return { start: first.next, end: line.start, after: line.end };
    }
  }
  throw new ExtractionError("unterminated frontmatter");
}

// Lower-cased attribute name -> value ("" for a bare attribute).
function parseAttributes(tag) {
  const inner = tag.replace(/^<script/i, "").replace(/\/?>$/, "");
  const attributes = {};
  for (const match of inner.matchAll(ATTRIBUTE_RE)) {
    const name = match[1].toLowerCase();
    if (name in attributes) continue;
    const value = match[2] ?? match[3] ?? match[4] ?? "";
    attributes[name] = value;
  }
  return attributes;
}

// True when the block is code tingle analyses (no src, a JS type).
function isCodeBlock(attributes) {
  if ("src" in attributes) return false;
  if (!("type" in attributes)) return true;
  return CODE_TYPES.has(attributes.type.trim().toLowerCase());
}

// {ts, jsx} of a block from its lang attribute. A missing lang is JS, or TS
// for Astro.
function blockLanguage(attributes, ext) {
  if (!("lang" in attributes)) return ext === "astro" ? TS : JS;
  const language = LANGUAGES[attributes.lang.toLowerCase()];
  if (!language) throw new ExtractionError(`unsupported <script lang="${attributes.lang}">`);
  return language;
}

// {end, next} of the content starting at `start`: it runs to the first
// following </script>, or to the end of the text when there is none. A
// self-closing tag has no content.
function contentEnd(text, tag, start) {
  if (tag.endsWith("/>")) return { end: start, next: start };
  const close = new RegExp(CLOSE_TAG_RE.source, "gi");
  close.lastIndex = start;
  const closing = close.exec(text);
  if (!closing) return { end: text.length, next: text.length };
  return { end: closing.index, next: close.lastIndex };
}

// Every <script> element from offset `from`: {attributes, start, end} of its
// content.
function scriptElements(text, from) {
  const elements = [];
  const open = new RegExp(OPEN_TAG_RE.source, "gi");
  open.lastIndex = from;
  let match;
  while ((match = open.exec(text)) !== null) {
    const tag = match[0];
    const start = match.index + tag.length;
    const { end, next } = contentEnd(text, tag, start);
    elements.push({ attributes: parseAttributes(tag), start, end });
    open.lastIndex = next;
  }
  return elements;
}

// Kept blocks of the component: [{start, end, ts, jsx}], in file order.
function keptBlocks(text, ext) {
  const offset = text.startsWith(BOM) ? BOM.length : 0;
  const blocks = [];
  let from = offset;
  if (ext === "astro") {
    const matter = frontmatter(text, offset);
    if (matter) {
      blocks.push({ start: matter.start, end: matter.end, ...TS });
      from = matter.after;
    }
  }
  for (const element of scriptElements(text, from)) {
    if (!isCodeBlock(element.attributes)) continue;
    const language = blockLanguage(element.attributes, ext);
    blocks.push({ start: element.start, end: element.end, ...language });
  }
  return blocks;
}

// `text` with every character outside `blocks` replaced by a space and
// every line terminator kept (one space per UTF-16 code unit).
function pad(text, blocks) {
  const parts = [];
  let cursor = 0;
  for (const block of blocks) {
    parts.push(text.slice(cursor, block.start).replace(/[^\r\n]/g, " "));
    parts.push(text.slice(block.start, block.end));
    cursor = block.end;
  }
  parts.push(text.slice(cursor).replace(/[^\r\n]/g, " "));
  return parts.join("");
}

function virtualExtension(blocks) {
  const ts = blocks.some((block) => block.ts);
  const jsx = blocks.some((block) => block.jsx);
  if (ts) return jsx ? "tsx" : "ts";
  return jsx ? "jsx" : "js";
}

// {code, vext} of the component `text` (extension `ext`, lower-cased), or
// {error} when it cannot be extracted.
function extractSfc(text, ext) {
  let blocks;
  try {
    blocks = keptBlocks(text, ext);
  } catch (error) {
    if (error instanceof ExtractionError) return { error: error.message };
    throw error;
  }
  return { code: pad(text, blocks), vext: virtualExtension(blocks) };
}

module.exports = { SFC_EXTENSIONS, extractSfc };
