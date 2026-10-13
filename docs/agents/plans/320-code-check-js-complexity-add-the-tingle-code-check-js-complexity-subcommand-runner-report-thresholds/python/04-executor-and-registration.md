# Executor, dispatch and completion
Add `python/code_check/js_complexity/executor.py` with `CheckJsComplexity(DockerCheck)`. Its module docstring follows rubycritic's executor: usage, examples and exit status, with no config and no selection flags.

Class attributes:
- `PROG = "tingle code_check js_complexity"`, `CONFIG_SECTION = "js_complexity"`;
- `FLAGS`;
- `SINGLE_DEFAULTS` = warn, error, critical (from `Constants`), `top: 0`, `fail_on: None`, `min_level: "ok"`, `image: None` (no `details`);
- `LIST_KEYS = ()`, `THRESHOLD_KEYS = ("warn", "error", "critical")`;
- `DEFAULT_EXCLUDES = Constants.DEFAULT_EXCLUDES`;
- `NO_FILES_MESSAGE = "No JavaScript/TypeScript files found for analysis."`;
- `error_class = JsComplexityError`.

Overrides:
- `_load_config` returns `({}, None)`: there is no `--no-config` or config section before #322 (see the Notes in [python.md](../python.md)).
- `validate_config` is not used before #322. Keep the base `NotImplementedError`, or a stub that is never reached.
- `_select_files` and `_selection_options` force the #320 selection: default excludes only, no `.gitignore`, no globs.
- `_gate_value(result)` returns `result.score` (the rounded `s`). Only level rows (dropped and refused included) are passed to `_gate_failed`, never `PARSE` files.
- `_parse_output`: on `OutputFormatError`, `write_stderr(proc)`, then raise `could not parse the output of <image>: <reason>` (spec §4; note the wording differs from rubycritic's).
- `_execute` follows spec §3 steps 4–12:
  1. resolve the target;
  2. resolve the image;
  3. print the header;
  4. select (the base `_select` exits 0 on nothing, before Docker);
  5. preflight, `ensure_image`, run and `check_outcome`;
  6. parse;
  7. warnings in spec §10 order: refused lines as `Warning: the image skipped <line>: <message>` (`warnings` order), then `cannot parse <display>: <message>` (sorted by sent line);
  8. the report;
  9. return 2 if the gate failed, else 0.

Registration:
- `python/code_check/subcommands.py`: `SUBCOMMAND_NAMES = ("file_size", "rubycritic", "js_complexity")`.
- `python/code_check/executor.py`: import `CheckJsComplexity` and add `"js_complexity": (CheckJsComplexity, "JavaScript/TypeScript code complexity via FTA (Docker).")` after `rubycritic`. Update the module docstring usage.
- `python/code_check/completion.py`: import `code_check.js_complexity.flags.FLAGS` and add `"js_complexity": flag_tables(JS_COMPLEXITY_FLAG_DEFS)`. Update the docstring's list of flag modules.

Tests:
- `test_executor.py`, with `shutil.which` and `subprocess.run` mocked through `js_complexity.docker_runner`:
  - no args → help, exit 0; usage errors → 1; negative thresholds or `--top` and an empty `--image` → 1 with the spec texts;
  - path missing or unreadable, a mount root with `:`, an unreadable version file;
  - the exact `docker run` args and stdin for a directory and for a single file;
  - nothing selected → exit 0 with no Docker call;
  - docker not on PATH, `docker info` failing or timing out, a pull failure, a mount failure (125 + marker), a non-zero status, unparsable output;
  - warnings order;
  - `--fail-on` → 2, and never because of `PARSE`;
  - a decimal threshold printed with `format(v, "g")`;
  - the config file is never read, even when `~/.tingle/code_check/config.json` is broken.
- Extend `python/tests/code_check/test_executor.py` (subcommand list and dispatch) and `test_completion.py` (`js_complexity` flag names, `--min-level`/`--fail-on` choices, nothing for `--warn`/`--image` values, the file sentinel for the path).

## Files to Change
- `python/code_check/js_complexity/executor.py`: new.
- `python/code_check/subcommands.py`: add `js_complexity`.
- `python/code_check/executor.py`: register the subcommand and update the docstring.
- `python/code_check/completion.py`: add the flag table and update the docstring.
- `python/tests/code_check/js_complexity/test_executor.py`: new.
- `python/tests/code_check/test_executor.py`, `python/tests/code_check/test_completion.py`: extend.
