# Spec: the `--details` drill-down

Sub-issue: #351. Parent: #344. Shared contracts: [README.md](README.md).

#351 fills `files[].functions` in the merged JSON from the same PDepend run
#346 already makes, and adds `--details [N]` and the `details` config key.
No second tool is needed (unlike `js_complexity`, which uses escomplex). The
image change and the Python change land in the same PR. Per-function data is
information only: it never sets a level and never changes the exit code. It
mirrors `js_complexity --details`.

## 1. Image changes

#346 emits `"functions": null` on every entry (README §9). #351 changes the
entrypoint so that `functions` holds the counted units of each analysed file
([image.md](image.md#xml--json-mapping)). Nothing else in the image
changes: same PDepend run, same options, same report. `tool_versions` does
not change. The Docker Hub description and
`docs/agents/tingle-php-complexity-image.md` mention the per-function data.

## 2. Which units are listed

The units are exactly the ones that make up the total CCN, so the drill-down
always adds up to the `CCN` column:

- every method of every `class` and `trait` PDepend attributes to the file,
  named `<Class>::<method>` with the short class or trait name
  (`Calculator::grade`, `Describes::describe`);
- every `function` PDepend attributes to the file, named by its short name
  (`clamp`), including functions declared inside `if (! function_exists(...))`
  blocks and inline in HTML (`title` in `page.php`).

Not listed, because PDepend 3.0.0 does not report them as units of the file:

- **closures and arrow functions** are not units. Inside a function or
  method their decisions count toward it (a probe: an `if` inside a closure
  passed to `array_map` raised the enclosing method's `ccn` to 2). At the top
  level they are not counted at all (`helpers.php`: `$double`, `$triple`).
  So there is no name to give them;
- **enum methods** and the **anonymous-class methods** PDepend emits as bare
  `<method>` elements (README deviation 7). An anonymous class's method is
  never listed under its own name; when PDepend folded its decisions into
  the enclosing method, they show in that method's `ccn`;
- interface methods (interfaces are not in the report).

Abstract methods of an abstract class are listed, with `ccn` 1, as PDepend
reports them.

## 3. Functions

Each entry of `files[].functions`:

| Field | From the summary XML | Notes |
|-------|----------------------|-------|
| `name` | `<class or trait @name>::<method @name>`, or `<function @name>` | Short names, without the namespace. PDepend writes them in UTF-8. |
| `line` | `@start` | 1-based line of the declaration in the original file (staging keeps the bytes, so the lines are the original ones). |
| `ccn` | `@ccn` | Cyclomatic complexity, ≥ 1. |
| `npath` | `@npath` | NPath complexity, ≥ 1, possibly above 2^53. |

- The list is in source order (by `line`, then `name`). A file with no
  counted unit gives `"functions": []`, and so does a file PDepend did not
  list (`pdepend: null`, for example `bootstrap.php` or `empty.php`).
- A parse error and a refused line get `null`.
- `sum(f.ccn for f in functions) == pdepend.ccn` for every analysed file;
  the smoke test checks it.

**Grounding results** (fixture in
[image.md](image.md#9-smoke-test-fixture)): `Calculator.php` →
`Calculator::add` (line 7, ccn 1, npath 1), `Calculator::sign` (12, 3, 3),
`Calculator::grade` (22, 7, 36); `Shapes.php` → 5 entries
(`Square::__construct` 12, `Square::area` 16, `Circle::__construct` 24,
`Circle::area` 28 with ccn 2, `Describes::describe` 36); `Modern.php` →
`Point::__construct` (21), `Point::withX` (25), no `Suit::color`;
`Anon.php` → `Factory::make` (9, ccn 2, npath 4) only; `helpers.php` →
`clamp` (3, ccn 3, npath 4), `greet` (14); `page.php` → `title` (4);
`bootstrap.php` and `empty.php` → `[]`. `crlf.php` and `bom.php` → line 3,
the same as `CVS/legacy.php` with LF and no BOM.

## 4. Report

`--details [N]` (#351):

| Flag | Type | Default | Help |
|------|------|---------|------|
| `--details [N]` | int ≥ 0, `nargs="?"`, `const=5` | `None` (off) | `Show the N most complex functions and methods under each file (default when given without N: 5; 0 = all)` |

- `--details` alone means `5`; `--details 0` lists every unit; a negative
  value is `Error: --details must be an integer >= 0`, exit 1.
- `DEFAULT_DETAILS = 5` lives in `php_complexity/constants.py`.
- Under each **shown level row** (after `--min-level` and `--top`), tingle
  prints the file's units sorted by `ccn` (highest first), then `line`
  (lowest first), then `name`, keeping the first `N` (all when `N` is 0).
  Never under a `PARSE` row.
- Each unit is one dim line, in `js_complexity`'s layout with `npath` in
  place of `sloc` (README deviation 15):

  ```python
  f"{c.DIM}{'':<16} ccn {f.ccn:>3}  npath {f.npath:>7}  {f.name}  ({path}:{f.line}){c.RESET}"
  ```

  where `path` is the row's displayed file. `{:>3}` and `{:>7}` are minimum
  widths; larger values are printed in full.
- The summary and the gate do not change.

Example: the [cli.md](cli.md#full-example) data with
`--warn 4 --error 6 --critical 10 --min-level warn --details 2` (real values
from the grounding image; no `Dup` column, which is #352's):

```
Status             CCN    Max    NPath     MI  Lines  File
──────────────── ─────  ─────  ───────  ─────  ─────  ──────────────────────────────────────────────────
🟣 CRITICAL          11      7       36     54     22  fixture/Calculator.php
                 ccn   7  npath      36  Calculator::grade  (fixture/Calculator.php:22)
                 ccn   3  npath       3  Calculator::sign  (fixture/Calculator.php:12)
🔴 ERROR              6      2        2     78     11  fixture/Shapes.php
                 ccn   2  npath       2  Circle::area  (fixture/Shapes.php:28)
                 ccn   1  npath       1  Square::__construct  (fixture/Shapes.php:12)
⚠️  WARN             4      3        4     66     12  fixture/helpers.php
                 ccn   3  npath       4  clamp  (fixture/helpers.php:3)
                 ccn   1  npath       1  greet  (fixture/helpers.php:14)
⛔ PARSE              -      -        -      -      -  fixture/attr_anon.php
⛔ PARSE              -      -        -      -      -  fixture/broken.php
⛔ PARSE              -      -        -      -      -  fixture/lenient.php
```

`Square::__construct` comes before `Square::area`, `Circle::__construct` and
`Describes::describe` (all ccn 1) because its line (12) is the lowest. With
`--details 0`, `Shapes.php` lists all 5 units.

## 5. Unavailable data

With `--details` set, a level row whose `functions` is:

- a non-empty list: the unit lines above;
- `[]`: nothing (the file has no counted function or method);
- `null`: one dim line `f"{c.DIM}{'':<16} (per-function data unavailable){c.RESET}"`.

`null` on a level row happens for a refused line, or with an image older
than #351 given through `--image`. It is **not** an error: the row keeps
its level and the run its exit code.

There is no separate failure mode: the units come from the PDepend run that
decides the levels, so if PDepend fails the whole run fails (exit 1) before
any report.

## 6. Config key

`details` in the `php_complexity` section: `nullable_non_negative_int`
(`'details' must be an integer >= 0 or null`), a single value with the usual
precedence (built-in `null` < config < CLI). #351 adds it to `SCHEMA` and to
`SINGLE_DEFAULTS`. See [config.md](config.md#2-keys).

## 7. Smoke test, docs and tests

- The smoke test (see [release.md](release.md#smoke_test_php_complexity))
  also asserts the `functions` column of the fixture table in
  [image.md](image.md#9-smoke-test-fixture): the names, lines and `ccn` of
  every entry for `Calculator.php`, `Shapes.php`, `Modern.php`, `Anon.php`
  and `helpers.php`; `[]` for `bootstrap.php` and `empty.php`; `null` for
  the parse errors and refused lines; every `line`, `ccn` and `npath` an int
  ≥ 1; and `sum(ccn) == pdepend.ccn` for every analysed file.
- Docs: `--details` in `docs/guides/code_check/php_complexity.md`,
  `long_help`, completion (`--details` takes a free-form value), and
  `docs/agents/tingle-php-complexity-image.md`.
- Python tests: `--details` alone, with `N`, with `0`, negative; sorting and
  ties (`ccn`, then `line`, then `name`); unit lines only under shown level
  rows (with `--top` and `--min-level`), never under `PARSE`; the
  unavailable note for `null` and nothing for `[]`; a large `npath`; the
  `details` config key and its precedence.
