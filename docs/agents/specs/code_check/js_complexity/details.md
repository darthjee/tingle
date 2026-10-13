# Spec: `--details` via typhonjs-escomplex

Sub-issue: #325. Parent: #315. Shared contracts: [README.md](README.md).

#325 adds [typhonjs-escomplex](https://github.com/typhonjs-node-escomplex/typhonjs-escomplex)
to the image through a small Node wrapper, fills `files[].functions` and
`tool_versions.escomplex` in the merged JSON, and adds `--details [N]` and
the `details` config key. The image change and the Python change land in the
same PR. Per-function data is information only: it never sets a level and
never changes the exit code. It mirrors `rubycritic --details`.

## 1. Image changes

- `package.json` gets `"typhonjs-escomplex": "0.1.0"` (exact); the
  regenerated lock pins its tree, including `@typhonjs/babel-parser` `0.2.0`,
  `@babel/parser` `7.29.9`, `typhonjs-escomplex-module` and
  `typhonjs-escomplex-project` `0.1.0`, the `escomplex-plugin-*` packages
  `0.1.0` and `typhonjs-escomplex-commons` `0.1.1`.
- `tool_versions.escomplex` becomes `"0.1.0"`, read from
  `node_modules/typhonjs-escomplex/package.json`.
- The wrapper is `docker/js_complexity/lib/escomplex.js`. The Docker Hub
  description mentions escomplex.

## 2. escomplex wrapper

The entrypoint runs the wrapper as a **separate process** after FTA (and
jscpd), so a crash or an out-of-memory error in escomplex cannot take the
entrypoint down:

```
node /opt/tingle_js_complexity/lib/escomplex.js
```

- **Input:** on stdin, a JSON array of the staged file paths
  (`/tmp/stage/plain/<n>.<ext>` and, from #326, `/tmp/stage/sfc/<n>.<ext>.<ts|js>`).
  Not on the command line, so there is no argument-length limit.
- **Output:** on stdout, one JSON object mapping each staged path to either
  `{"functions": [...]}` or `{"error": <one-line message>}`.
- For each file it reads the staged copy as UTF-8 (already checked) and
  calls

  ```js
  escomplex.analyzeModule(source, MODULE_OPTIONS, { sourceType: "unambiguous", plugins })
  ```

  catching any exception per file.

**Pinned module options** (escomplex's defaults, made explicit):

```js
const MODULE_OPTIONS = { logicalor: true, switchcase: true, forin: false, trycatch: false, newmi: false };
```

**Pinned parser options.** escomplex's default plugin set enables `jsx` and
`typescript` together, which fails on `<T>value` type assertions in `.ts`
files (`Unterminated JSX contents`; README deviation 9). The wrapper passes
its own `plugins`, chosen by the staged file's last extension:

| Staged extension | `plugins` |
|------------------|-----------|
| `ts`, `mts`, `cts` (and SFC `….ts`) | `["typescript", ...COMMON]` |
| `tsx` | `["typescript", "jsx", ...COMMON]` |
| `js`, `mjs`, `cjs`, `jsx` (and SFC `….js`) | `["jsx", ...COMMON]` |

```js
const COMMON = [
  "decorators-legacy", "classProperties", "classPrivateProperties", "classPrivateMethods",
  "dynamicImport", "importMeta", "topLevelAwait", "optionalChaining",
  "nullishCoalescingOperator", "logicalAssignment", "numericSeparator",
  "objectRestSpread", "optionalCatchBinding", "exportDefaultFrom",
];
```

`sourceType: "unambiguous"` lets both ES modules and CommonJS parse.
Changing a plugin or a module option is a deliberate change, like a version
bump.

## 3. Functions

escomplex 0.1.0's report (trimmed, from the grounding run on `complex.ts`
with the image built from #325, `0.6.1-arm64`: only `reducer` and
`Store.dispatch` kept; `halstead`, `aggregate`, `maintainability` and the
averages omitted):

```json
{
  "methods": [
    {"name": "reducer", "lineStart": 31, "lineEnd": 72, "cyclomatic": 15, "sloc": {"logical": 48, "physical": 42}}
  ],
  "classes": [
    {
      "name": "Store",
      "methods": [
        {"name": "dispatch", "lineStart": 93, "lineEnd": 105, "cyclomatic": 3, "sloc": {"logical": 13, "physical": 13}}
      ]
    }
  ]
}
```

- `methods` lists every function outside a class, nested and anonymous ones
  included (escomplex names an anonymous one `<anon method-N>`).
  `classes[].methods` lists every method of a class, with the functions
  nested in them.
- The wrapper flattens both into one list. Each entry is:

| Field | From | Notes |
|-------|------|-------|
| `name` | `m.name` for `methods`; `"<Class>.<name>"` for `classes[].methods` (`<anonymous>` when the class has no name) | `"reducer"`, `"Store.dispatch"`, `"<anon method-1>"`. |
| `line` | `m.lineStart` | 1-based line of the function in the original file. |
| `cyclo` | `m.cyclomatic` | Cyclomatic complexity, ≥ 1. |
| `sloc` | `m.sloc.physical` | `lineEnd - lineStart + 1`, the lines the function spans. |

- The list is in source order (by `line`, then `name`). A file with no
  function gives `"functions": []`.
- The entrypoint copies each list to `files[<n>].functions`. A file the
  wrapper reports with `error`, a `parse_error` file and a refused line get
  `null`.

**Grounding results** (image built from #325, `0.6.1-arm64`, escomplex
0.1.0): `complex.ts` 30 functions (8 of them `Store.<method>` entries); the
most complex are `reducer` (line 31, cyclo 15, sloc 42), `ruleTags` (line
156, cyclo 6, sloc 7), `score` (line 225, cyclo 6, sloc 23) and `ruleCoupon`
(line 149, cyclo 5, sloc 6). `simple.js` 2 (`add` line 3 and `double` line
5, both cyclo 1, sloc 1), `component.tsx` 3, `dup_a.js`/`dup_b.js` 3 each, `empty.js`,
`short.js` and `ext/types.d.ts` 0 (`[]`), `broken.js` an error
(`Unexpected keyword 'return'. (2:2)`). See the full table in
[image.md](image.md#10-grounding-run).

**Line numbers with CRLF and a BOM.** Babel counts `\r\n` as one line break
and ignores a leading BOM, so `line` is the editor's line number. Checked: a
function at line 3 of a CRLF file and at line 4 of a file with a BOM came
back as `lineStart` 3 and 4. For an SFC, the virtual module keeps the
original line numbers (see [sfc.md](sfc.md#4-line-map)); checked with a
CRLF + BOM `Cart.vue` (function at line 13).

## 4. Report

`--details [N]` (#325):

| Flag | Type | Default | Help |
|------|------|---------|------|
| `--details [N]` | int ≥ 0, `nargs="?"`, `const=5` | `None` (off) | `Show the N most complex functions under each file (default when given without N: 5; 0 = all)` |

- `--details` alone means `5`; `--details 0` lists every function; a
  negative value is `Error: --details must be an integer >= 0`, exit 1.
- `DEFAULT_DETAILS = 5` lives in `js_complexity/constants.py`.
- Under each **shown level row** (after `--min-level` and `--top`), tingle
  prints the file's functions sorted by `cyclo` (highest first), then `line`,
  then `name`, keeping the first `N` (all when `N` is 0). Never under a
  `PARSE` row.
- Each function is one dim line:

  ```python
  f"{c.DIM}{'':<16} cyclo {f.cyclo:>3}  sloc {f.sloc:>4}  {f.name}  ({path}:{f.line}){c.RESET}"
  ```

  where `path` is the row's displayed file.
- The summary and the gate do not change.

Example (`--details 2`, the [subcommand.md](subcommand.md#full-example) run
with #324 and #325, first rows):

```
Status             FTA  Cyclo  Lines    Dup  Assessment         File
──────────────── ─────  ─────  ─────  ─────  ─────────────────  ──────────────────────────────────────────────────
🔴 ERROR           71.3    136    245      0  Needs improvement  fixture/complex.ts
                 cyclo  15  sloc   42  reducer  (fixture/complex.ts:31)
                 cyclo   6  sloc    7  ruleTags  (fixture/complex.ts:156)
✅ OK              37.4      3     18      0  OK                 fixture/component.tsx
                 cyclo   2  sloc   17  Counter  (fixture/component.tsx:8)
                 cyclo   2  sloc    5  <anon method-1>  (fixture/component.tsx:11)
```

The values come from the grounding fixture (image built from #325,
`0.6.1-arm64`); they change with the fixture content. `ruleTags` comes
before `score` (both cyclo 6) because its line is lower. With `--details 0`,
`complex.ts` lists all 30 functions.

## 5. Unavailable data

With `--details` set, a level row whose `functions` is:

- a non-empty list: the function lines above;
- `[]`: nothing (the file has no function);
- `null`: one dim line `f"{c.DIM}{'':<16} (per-function data unavailable){c.RESET}"`.

`null` happens when escomplex could not parse a file FTA parsed (for example
very new TypeScript syntax), when escomplex failed as a whole, or with an
image older than #325 given through `--image`. Unlike `rubycritic`, a
missing per-function block is **not** an error: the row keeps its level and
the run its exit code.

## 6. Failure handling

- **One file fails** (`{"error": ...}` from the wrapper): `functions: null`
  for that file, and a `warnings` entry
  `{"tool": "escomplex", "path": <line>, "message": <error>}`. Tingle does
  not print these per-file warnings; the row shows the unavailable note
  under `--details`.
- **The wrapper fails** (non-zero exit, killed, stdout not a JSON object, or
  an entry that does not map to a staged file): `functions: null` for every
  file, `tool_versions.escomplex` kept, and one `warnings` entry
  `{"tool": "escomplex", "message": <one-line reason>}` (no `path`). The
  entrypoint's exit status is unchanged.

Tingle prints, for each `escomplex` warning without a `path`:

```
Warning: escomplex failed in <image>; per-function data is not available: <message>
```

The exit code is unchanged.

## 7. Config key

`details` in the `js_complexity` section: `nullable_non_negative_int`
(`'details' must be an integer >= 0 or null`), a single value with the usual
precedence (built-in `null` < config < CLI). See
[config.md](config.md#2-keys).

## 8. Smoke test, docs and tests

- The smoke test also asserts `tool_versions.escomplex == "0.1.0"`;
  `functions` for `complex.ts` with at least 20 entries, one named `reducer`
  and one starting with `Store.`; `[]` for `empty.js` and `short.js`; `null`
  for `broken.js` and `latin1.js`; and that every `line`, `cyclo` and `sloc`
  is an int ≥ 1.
- Docs: `--details` in `docs/guides/code_check/js_complexity.md`,
  `long_help`, completion (`--details` takes a free-form value), and
  `docs/agents/tingle-js-complexity-image.md`.
- Python tests: `--details` alone, with `N`, with `0`, negative; sorting and
  ties; function lines only under shown level rows, never under `PARSE`;
  the unavailable note for `null` and nothing for `[]`; the warning for an
  `escomplex` entry without a `path` and none for one with a `path`; the
  `details` config key and its precedence.
