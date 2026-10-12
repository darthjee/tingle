# Grounding run
Before writing any spec, run the real tools to learn their actual output. The specs are then based on that output, not on assumptions. Nothing from this step is committed.

1. **Pick versions.** Choose the current **active Node LTS** `node:<major>.<minor>.<patch>-slim` tag and the latest stable `fta-cli`, `jscpd` and `typhonjs-escomplex`. Record each exact version.
2. **Build the fixture** in a scratch directory outside the repo:
   - `simple.js`, `complex.ts`, `component.tsx`, `widget.jsx`;
   - `dup_a.js` and `dup_b.js`, sharing a block of about 20 lines;
   - `broken.js` (a syntax error) and `empty.js`;
   - `bundle.min.js`;
   - `Cart.vue` with `<script setup lang="ts">`;
   - `crlf.js` with CRLF line endings, `bom.ts` with a UTF-8 BOM, and `latin1.js` with non-UTF-8 bytes.
3. **Run the tools** in a throwaway container: `--network none`, `--user $(id -u):$(id -g)`, the fixture mounted read-only at `/src`, no git installed, and all output under `/tmp`. Install the npm packages in a prior networked step, or build a throwaway image.
   - Run FTA on a staged tree `/tmp/stage/`, once with symlinks and once with copies, to decide between them.
   - Run jscpd on the same tree.
   - Run escomplex through a minimal Node wrapper, with the parser options that will be pinned (TS, JSX, decorators).
4. **Record**, as working notes for steps 02–06:
   - each exact command;
   - the JSON path of every field the report uses;
   - how paths appear in each tool's output;
   - a per-fixture results table: FTA score and assessment, parse error or not, dropped or not, jscpd duplicated lines, and whether escomplex returned functions;
   - FTA's assessment bands;
   - any network or out-of-`/tmp` access;
   - jscpd's defaults for `min-tokens`/`min-lines` and the values chosen to pin.
5. Keep **trimmed** JSON samples (one or two entries per tool, with every field used) for the specs.

## Files to Change
- None. This step only produces working notes and samples.
