# Python Plan: code_check rubycritic: add the tingle code_check rubycritic subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

**What this agent produces (the other agents rely on these)**
- `SUBCOMMANDS["rubycritic"] = (CheckRubycritic, "Ruby code complexity via RubyCritic (Docker).")`, after `file_size`.
- `SUBCOMMAND_NAMES = ("file_size", "rubycritic")`.
- `PROG = "tingle code_check rubycritic"`.
- `code_check.rubycritic.flags.FLAGS` with exactly these flags:
  - `path`
  - `--warn`, `--error`, `--critical`: floats >= 0, defaults 100/200/400
  - `--top`: int >= 0, 0 means all
  - `--min-level`: ok, warn, error or critical
  - `--fail-on`: warn, error or critical
  - `--image`
- `cli` and `guide` copy their help texts from these definitions.
- Exit codes are 0, 1 and 2, as in [plan.md](plan.md#shared-contracts). Messages are verbatim from spec §10.
- Module names, which `product-owner` documents:
  - `constants.py`, `errors.py`, `flags.py`, `image.py`
  - `selection.py`, `docker_runner.py`, `output_parser.py`, `reporter.py`
  - `executor.py`
  - If any name changes, say so in the PR so the architecture doc matches.
- `FileCollector` gains a keyword-only `binary_check: bool = True`.

## Steps

- [01 — FileCollector binary_check](python/01-file-collector-binary-check.md)
- [02 — Package skeleton, flags, image and dispatch](python/02-skeleton-flags-dispatch.md)
- [03 — Completion for rubycritic](python/03-completion.md)
- [04 — File selection](python/04-file-selection.md)
- [05 — Docker runner](python/05-docker-runner.md)
- [06 — Output parser](python/06-output-parser.md)
- [07 — Reporter and full run](python/07-reporter-and-run.md)

## CI Checks
- `python/`: `ruff check .` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`; coverage must stay >= 75%)

## Notes
- **mccabe limit.** Codacy's prospector enforces a cyclomatic complexity limit of 10 (see #202). Keep `CheckRubycritic.run` flat: helpers raise `RubycriticError(message)` and `run` catches it once, then calls `_fail`.
- **Docstrings.** Every module needs the `"""name.py — summary."""` docstring and `from __future__ import annotations`. Multi-line docstrings start on the first line (D212).
- **dodgy.** Avoid identifiers that look like secrets, such as `password` or `secret` (see #192/#193).
- **Docker never runs in tests.** Mock `shutil.which` and `subprocess.run` on the module under test, using the recorder pattern from `tests/code_check/file_size/test_git_ignore.py`.
- **Tests may run as root** (docker-compose), where `os.access` always succeeds. Monkeypatch `os.access` in the unreadable-path tests rather than relying on chmod.
- **Non-UTF-8 names.** macOS APFS rejects non-UTF-8 file names. Test that filter with synthetic surrogate-escaped strings (`b"\xff".decode("utf-8", "surrogateescape")`), not real files.
- **Pull progress.** `docker pull` progress goes to the real stderr. Flush `sys.stderr` first. Under pytest, `subprocess.run` is mocked, so the missing fileno on capture streams does not matter. Fall back gracefully if `fileno()` raises.
- **Decoding.** Decode container stdout and stderr as UTF-8 with `errors="replace"`.
- **NaN.** `nan` must be rejected by validation; `not (value >= 0)` covers it. `inf` is accepted; the spec is silent on it.
- **Display.** Show thresholds with `format(v, "g")`, so 100.0 prints as `100`. Write the help defaults the same way.
- **Duplication column.** Print it with `int(round(value))`. Flay mass is integral in practice.
- **Default image tag.** It only exists after a release (#294). Manual testing uses `bin/tingle code_check rubycritic docker/rubycritic/fixture --image tingle_rubycritic:dev`, with the image built from `docker/rubycritic/`.
