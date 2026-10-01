# Cli Plan: code_check rubycritic: add the tingle code_check rubycritic subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

What this agent relies on, produced by `python`:
- Subcommand name `rubycritic`, with the description `Ruby code complexity via RubyCritic (Docker).`
- Flags:
  - `path`
  - `--warn N`, `--error N`, `--critical N`: floats >= 0, defaults 100/200/400
  - `--top N`: 0 = all
  - `--min-level ok|warn|error|critical`
  - `--fail-on warn|error|critical`: exits 2
  - `--image IMAGE`: default `darthjee/tingle_rubycritic:<tingle version>`
- Exit codes 0, 1 and 2, as in [plan.md](plan.md#shared-contracts).

Copy help wording from the final `python/code_check/rubycritic/flags.py` help strings.

## Implementation Steps

### Step 1 — Update the code_check entry in commands/python.json
**`short_help`**
- Change it to `"Code evaluation checks (subcommands: file_size, rubycritic)."`.

**`long_help`**
- Add `rubycritic   Ruby code complexity via RubyCritic (Docker).` to the `Subcommands:` list.
- Add a "The rubycritic subcommand:" part after the `file_size` part, in the same shape, with flag descriptions aligned at column 36. It contains:
  - **Description:** runs RubyCritic in the `darthjee/tingle_rubycritic` Docker image on `.rb` files and measures each file's total Flog complexity. Docker is required, and the image is pulled when missing. The rating is shown for information only.
  - **`Usage:`** `tingle code_check rubycritic <path> [options]`.
  - **`Thresholds:`** `--warn`, `--error`, `--critical`.
  - **`Display:`** `--top`, `--min-level`.
  - **`CI gate:`** `--fail-on`.
  - **`Image:`** `--image`.
  - **Exit codes:** 0, 1 and 2, as in the shared contract.
  - **Streams:** the report goes to stdout and errors to stderr, with the same colour note as `file_size`.
  - **Examples:**
    - `./app`
    - custom thresholds
    - `--top 10`
    - `--min-level warn`
    - `--fail-on error`
    - `--image tingle_rubycritic:dev`

Leave out the #296 and #297 flags (`--exclude`, `--no-default-excludes`, `--ignore`, `--include`, `--no-gitignore`, `--no-config`) and the config section.
`bin/tingle` and `completions/bash/commands.sh` are generic and need no change. Completion lives in `python/code_check/completion.py`, which the `python` agent owns.

## Files to Change
- `commands/python.json`: `short_help`, plus the `long_help` subcommand list and the rubycritic part.

## CI Checks
- No CI job validates `commands/python.json`. Check it manually:
  - `jq empty commands/python.json`
  - `bin/tingle --help code_check`
  - `bin/tingle` (the command list)
  - `tingle code_check rubycritic --<TAB>`, with completion sourced

## Notes
- Nothing tests `long_help`, so it can drift from argparse. Write it from the final `flags.py`.
- #296 and #297 will each extend this entry again.
- Do not suggest that the default image works before a release (#294). The `--image tingle_rubycritic:dev` example covers local testing.
