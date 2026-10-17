# Plan: code_check php_complexity: per-method complexity drill-down (--details)

Issue: [351-code-check-php-complexity-per-method-complexity-drill-down-details.md](../../issues/351-code-check-php-complexity-per-method-complexity-drill-down-details.md)

## Overview
Fill `files[].functions` in the `tingle_php_complexity` image from the PDepend run it already makes, and add `--details [N]` plus the `details` config key to `tingle code_check php_complexity`. Under each shown level row, the CLI lists the file's `N` most complex methods and functions. The image change and the Python change ship in the same PR. The normative spec is `docs/agents/specs/code_check/php_complexity/details.md`. This mirrors `js_complexity --details` (#325, PR #337).

## Agents involved

- [shell](shell.md)
- [python](python.md)
- [guide](guide.md)
- [product-owner](product-owner.md)

## Shared contracts

**`files[].functions`** (produced by the image, consumed by `python/code_check/php_complexity/output_parser.py`, which already validates this shape):

- `null`: for a parse error (`parse_error: true`) and for a refused line.
- `[]`: for an analysed file with no counted unit, including files PDepend did not list (`pdepend: null`, e.g. `bootstrap.php`, `empty.php`).
- Otherwise a list, in source order (by `line`, then `name`), of:

  | Field | Type | From the summary XML |
  |-------|------|----------------------|
  | `name` | string | `<class or trait @name>::<method @name>`, or `<function @name>` (short names, UTF-8) |
  | `line` | int ≥ 1 | `@start` |
  | `ccn` | int ≥ 1 | `@ccn` |
  | `npath` | int ≥ 1 | `@npath`, emitted as a JSON integer, possibly above 2^53 (same encoding as `max_npath`) |

- Counted units are the same ones `tpc_summarize` already adds to `pdepend.ccn`, so `sum(f.ccn) == pdepend.ccn` for every analysed file.
- Example: `Calculator.php` → `[{"name":"Calculator::add","line":7,"ccn":1,"npath":1},{"name":"Calculator::sign","line":12,"ccn":3,"npath":3},{"name":"Calculator::grade","line":22,"ccn":7,"npath":36}]`.

**CLI** (`--details`): `int`, `nargs="?"`, `const=Constants.DEFAULT_DETAILS` (5), default `None`. Config key `details`: `nullable_non_negative_int`, built-in default `None`.
