# Guide Plan: docs: add user guide for `tingle check_file_size` (docs/guides/check_file_size.md)

Main plan: [plan.md](plan.md)

## Overview
Add `docs/guides/check_file_size.md` and turn the placeholder entry in
`docs/guides/README.md` into a link. The guide documents the current
behaviour; behaviour changes are tracked separately in #185 (CI exit-status
flag) and #186 (`.min.*` not skipped, colours always on).

## Context
Part of #172. Existing guides (`linux.md`, `install.md`, `kube.md`) set
the shape: `# \`tingle <cmd>\`` title + one-line summary, "What it does",
usage, per-feature sections, errors, "Quick help". Source of truth:
`long_help` in `commands/python.json` and `python/check_file_size/`
(`executor.py`, `constants.py`, `file_collector.py`, `skip_checks.py`,
`file_analyzer.py`, `reporter.py`).

Facts verified in the code:
- `<path>` is a file or directory; directories are walked recursively
  (`rglob`).
- Defaults: `--warn 300`, `--error 500`, `--critical 1000`, `--top 0`
  (all), `--exclude node_modules,dist,build,.git,vendor,third_party,.next,__pycache__,.cache,coverage,.nuxt,out,target`,
  `--ext` none (repeatable, `action=append`).
- `--exclude` **replaces** the defaults; matching is against every path
  component, case-insensitive. `--ext` is compared case-insensitively to
  the file's last suffix.
- Single-file target: `--ext`/`--exclude` ignored; only the binary check
  applies.
- Binary skip: known extension list, or first 1024 bytes contain a NUL byte
  or are not valid UTF-8, or the file cannot be read. Do not list
  `.min.js`/`.min.css` (they never match — #186).
- Classification: `lines >= critical` → 🟣 CRITICAL; `>= error` → 🔴 ERROR;
  `>= warn` → ⚠️ WARN; else ✅ OK.
- Output: `Analyzing: <absolute target>`, `Thresholds: warn=… | error=… |
  critical=…`, blank line, table header `Status / Lines / File`, rows
  sorted by lines descending (`--top` applied after sort), then a rule,
  `Summary: N file(s) | a OK | b WARN | c ERROR | d CRITICAL` and
  `Total: X lines`. Summary/total reflect only the rows shown (after
  `--top`). Numbers use `.` as thousands separator. Paths are relative to
  the target directory's parent (so they start with the target dir's name);
  for a single file, just its name. ANSI colours always emitted.
- Exit status: no args → argparse help, 0; path not found → red
  `Error: path not found: <absolute path>` on stdout, 1; no files →
  `No files found for analysis.`, 0; invalid/unknown options → argparse
  usage error on stderr, 2; otherwise 0 regardless of classifications.

## Implementation Steps

### Step 1 — Write `docs/guides/check_file_size.md`
Sections, in order:
1. Title `# \`tingle check_file_size\`` and the short help line.
2. **What it does** — purpose (token-efficiency triage before feeding a repo
   to an AI).
3. **Usage** — `tingle check_file_size <path> [options]`; file vs directory.
4. **Options** — table or list of every option with its default;
   `--exclude` replace-not-add warning plus an example that keeps the
   defaults and adds one (e.g. `--exclude node_modules,dist,…,target,fixtures`);
   note that `--ext`/`--exclude` do nothing for a single-file target.
5. **Skipped files** — excluded directories and automatic binary detection.
6. **Reading the output** — header, table, classifications with boundaries,
   thousands separator, path display, summary/total (and that they cover
   only shown rows with `--top`), plus a sample output block (plain text,
   no ANSI codes) with a few rows across classifications.
7. **Examples** — the five `long_help` examples in `tingle check_file_size`
   form, each with a one-line explanation.
8. **Exit status and errors** — the cases above; state explicitly that it is
   not a CI gate today and reference #185.
9. **Quick help** — `tingle --help check_file_size`.

### Step 2 — Update `docs/guides/README.md`
Replace the placeholder line with
`- [\`check_file_size\`](check_file_size.md) — Token efficiency triage: file size analysis.`
(drop *(guide coming soon)*).

## Files to Change
- `docs/guides/check_file_size.md` — new guide.
- `docs/guides/README.md` — link the guide, remove placeholder marker.

## Notes
- Root `README.md` scripts table links `install` and `linux` to their
  guides; the `check_file_size` row should link to
  `docs/guides/check_file_size.md` the same way. `README.md` is
  architect-owned (outside `guide` scope) — the architect makes that
  one-line change when implementing.
- Verify sample output and behaviour against the real command
  (`bin/tingle check_file_size <dir>`) before finalising.
- No CI job covers `docs/guides/` (CircleCI only lints/tests `python/`).
