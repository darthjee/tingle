# Python Plan: code_check js_complexity: support .vue/.svelte/.astro single-file components

Main plan: [plan.md](plan.md)

## Shared contracts

- The host selects `.vue`, `.svelte` and `.astro` (any letter case) in
  addition to the core extensions. No declaration or minified skip applies to
  them.
- The image's JSON shape is unchanged, so an SFC row is parsed and reported
  like any other file. Extraction errors arrive as `parse_error: true` plus a
  warning `{"tool": "entrypoint", "path": <line>, "message": ...}`, and must
  render as `⛔ PARSE` with `Warning: cannot parse <file>: <message>`.

## Implementation Steps

### Step 1 — Selection
- In `python/code_check/js_complexity/constants.py`, add
  `SFC_EXTENSIONS: ClassVar[list[str]] = [".vue", ".svelte", ".astro"]`, with
  a comment.
- In `python/code_check/js_complexity/selection.py`, pass
  `extensions=[*Constants.EXTENSIONS, *Constants.SFC_EXTENSIONS]` to
  `select_files`. Update the module docstring.
- In the help docstring of `python/code_check/js_complexity/executor.py`
  (around line 26), mention the three SFC extensions next to the core list,
  using the shared wording from [plan.md](plan.md#shared-contracts).
- In `python/code_check/js_complexity/flags.py`, update the help text if it
  describes the extension set (line 12).
- In `output_parser.py`, check that a `PARSE` row whose warning has tool
  `entrypoint` is rendered with `cannot parse`. Today `entrypoint` warnings
  may only come with refused rows (`parse_error: false`). If they are handled
  differently, make `parse_error: true` + `entrypoint` produce the normal
  `PARSE` row and warning.

### Step 2 — Tests
- `python/tests/code_check/js_complexity/test_selection.py`:
  - a `test_sfc_extensions` constant test;
  - parametrise "each extension in any case is selected" over
    `.vue/.svelte/.astro` (lower, upper and mixed case);
  - a `.vue` file inside a directory with core files is selected;
  - `Cart.vue.ts` and `Cart.vue` are both selected.
- `test_output_parser.py` / `test_executor.py`:
  - an SFC row (`src/Cart.vue`, with functions at original lines) is reported
    under the original path with the given line numbers;
  - a no-script SFC row (`fta: null`, `parse_error: false`) shows as `OK 0.0`;
  - a `parse_error: true` row with an `entrypoint` warning
    `unsupported <script lang="coffee">` shows as `⛔ PARSE` with the warning
    text.
- Extend `python/tests/code_check/js_complexity/sample_output.py` with the SFC
  entries if the other tests build on it.

## Files to Change
- `python/code_check/js_complexity/constants.py` — `SFC_EXTENSIONS`.
- `python/code_check/js_complexity/selection.py` — pass the SFC extensions;
  update the docstring.
- `python/code_check/js_complexity/executor.py` — the help docstring.
- `python/code_check/js_complexity/flags.py` — the help text, if it names
  extensions.
- `python/code_check/js_complexity/output_parser.py` — only if the
  `entrypoint` parse-error warning is not handled already.
- `python/tests/code_check/js_complexity/test_selection.py`,
  `test_output_parser.py`, `test_executor.py`, `sample_output.py` — the new
  cases.

## CI Checks
- `python`: run the same command the CircleCI python job runs (pytest plus
  the linters configured in `.circleci/config.yml`), for example
  `cd python && pytest tests/code_check/js_complexity`.
