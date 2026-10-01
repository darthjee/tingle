# Plan: code_check rubycritic: add the tingle code_check rubycritic subcommand (runner, report, thresholds)

Issue: [295-code-check-rubycritic-add-the-tingle-code-check-rubycritic-subcommand-runner-report-thresholds.md](../../issues/295-code-check-rubycritic-add-the-tingle-code-check-rubycritic-subcommand-runner-report-thresholds.md)

## Overview
This plan adds `tingle code_check rubycritic <path>`, a new Python subcommand in `python/code_check/rubycritic/`. It selects `.rb` files using `file_size`'s `FileCollector` (with the binary check turned off), runs RubyCritic inside the `darthjee/tingle_rubycritic` Docker image, and prints a per-file report in `file_size`'s style, with warn/error/critical thresholds and a `--fail-on` gate.
The `python` agent does most of the work: the package, the dispatch, the completion and the tests. `cli` updates the help text in `commands/python.json`, `guide` writes the user guide, and `product-owner` updates `docs/agents/architecture.md`. The architect updates the root `README.md`.
The normative contract is [`subcommand.md`](../../specs/code_check/rubycritic/subcommand.md) together with [`README.md`](../../specs/code_check/rubycritic/README.md). Where they disagree with this plan, the spec wins.

## Agents involved

- [python](python.md)
- [cli](cli.md)
- [guide](guide.md)
- [product-owner](product-owner.md)

Order: `python` goes first. `cli`, `guide` and `product-owner` build on its final flag set, help strings and module names, so they run after it. All the work ships in the same PR, so the help text never advertises a subcommand that does not exist.

**Architect integration (root files, not delegated):**
- In `README.md`, reword the `code_check` row (line ~81, currently "First subcommand: file_size ...") so it lists both subcommands, linking to `docs/guides/code_check/rubycritic.md`.
- Also in `README.md`, change the Prerequisites line "`docker` for `tingle linux`" to "`docker` for `tingle linux` and `tingle code_check rubycritic`".
- Check that `SUBCOMMANDS`, `SUBCOMMAND_NAMES`, `long_help`, completion and the guide all agree on the flag set.

## Shared contracts

**Subcommand registration**
- `python/code_check/executor.py` `SUBCOMMANDS` gains `"rubycritic": (CheckRubycritic, "Ruby code complexity via RubyCritic (Docker).")`, after `file_size`.
- `python/code_check/subcommands.py` `SUBCOMMAND_NAMES = ("file_size", "rubycritic")`.
- The description string `Ruby code complexity via RubyCritic (Docker).` is reused verbatim in `long_help`'s `Subcommands:` list, in the `docs/guides/code_check.md` table and in `docs/guides/README.md`.
- `PROG = "tingle code_check rubycritic"`.

**Flags** (`python/code_check/rubycritic/flags.py` `FLAGS`, import-light)

| Flag | Type / choices | Default | Notes |
|---|---|---|---|
| `path` | positional | none | Directory (recursive) or a single `.rb` file. |
| `--warn N` | float >= 0 | 100 | Defaults are applied after parsing (config merge comes in #297). |
| `--error N` | float >= 0 | 200 | |
| `--critical N` | float >= 0 | 400 | |
| `--top N` | int >= 0 | 0 (all) | Filters level rows only. |
| `--min-level LEVEL` | ok, warn, error, critical | ok | Display only. Applied before `--top`. |
| `--fail-on LEVEL` | warn, error, critical | off | Exits 2. Counts every selected file and never PARSE rows. |
| `--image IMAGE` | non-empty string | `darthjee/tingle_rubycritic:<version>` | `<version>` comes from `shell/linux/VERSION`. |

Not in this issue: `--exclude`, `--no-default-excludes`, `--ignore`, `--include` and `--no-gitignore` (#296); the `rubycritic` config section and `--no-config` (#297).

**Exit codes**
- 0: success, help, or `No Ruby files found for analysis.`
- 1: usage errors (argparse's 2 is remapped to 1), path missing or unreadable, `:` in the mount root, unreadable version without `--image`, docker not found, daemon not responding, pull failed, mount denied, container failure, or unparsable output.
- 2: the `--fail-on` gate failed.

**Default excludes**
- `file_size`'s `DEFAULT_EXCLUDES` followed by `tmp`, `log` and `.bundle`.

**Package modules** (`python/code_check/rubycritic/`; `product-owner` documents these names)
- `__init__.py`
- `constants.py`
- `errors.py`
- `flags.py`
- `image.py`
- `selection.py`
- `docker_runner.py`
- `output_parser.py`
- `reporter.py`
- `executor.py`

**FileCollector change**
- `FileCollector(..., *, ignore=None, include=None, gitignore=True, binary_check=True)`.
- rubycritic calls it with `gitignore=False` and `binary_check=False`.
- `FileCollector` stays in `file_size/` and rubycritic imports it from there. This is a deliberate exception to the "move a helper up once a second consumer needs it" rule, because the spec says it is "reused directly, not copied".

**Docker run line**
- `docker run --rm -i --pull never --network none --security-opt no-new-privileges --user <uid>:<gid> -v <root>:/src:ro -w /src <image>`.
- Stdin receives the selected paths relative to `<root>`, sorted, one per line.
