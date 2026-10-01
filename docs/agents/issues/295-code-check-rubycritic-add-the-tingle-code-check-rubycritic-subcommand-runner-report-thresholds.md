# Issue: code_check rubycritic: add the tingle code_check rubycritic subcommand (runner, report, thresholds)

## Description
Add the `tingle code_check rubycritic <path>` subcommand (parent #290). It measures Ruby code complexity by running RubyCritic inside the `darthjee/tingle_rubycritic` Docker image, and prints a per-file report in the same style as `tingle code_check file_size`.

The normative contract is [`docs/agents/specs/code_check/rubycritic/subcommand.md`](../specs/code_check/rubycritic/subcommand.md), together with the shared contracts in [`README.md`](../specs/code_check/rubycritic/README.md). This issue summarises that spec. Where they differ, the spec wins.

## Solution
### Package and dispatch
- New package `python/code_check/rubycritic/`, laid out like `file_size/`: `flags.py` (import-light `FLAGS`), `constants.py`, `executor.py` (`CheckRubycritic`, `PROG = "tingle code_check rubycritic"`), and one module each for the Docker runner, JSON parsing and the reporter.
- Register `"rubycritic"` in `SUBCOMMANDS` (`python/code_check/executor.py`, after `file_size`) and in `SUBCOMMAND_NAMES` (`python/code_check/subcommands.py`).
- `commands/python.json`: list both subcommands in `short_help`, and add a `rubycritic` part to `long_help` in the same shape as `file_size` (usage, flags, examples, exit status).
- `python/code_check/completion.py`: complete `rubycritic` from `code_check.rubycritic.flags.FLAGS` (flag names, choices, file sentinel for the path).

### Flags
`path`, `--warn/--error/--critical` (floats ≥ 0; defaults 100/200/400, applied after the later config merge), `--top`, `--min-level`, `--fail-on` (exit 2), `--image`. Negative values, a negative `--top` and an empty `--image` are usage errors (exit 1). Argparse usage errors are remapped from 2 to 1. Levels use `file_size`'s comparisons and labels (`🟣 CRITICAL`). The rating is shown for information only.

### Run order
1. No arguments: print help, exit 0. Then parse flags.
2. Resolve `<path>`: missing → `path not found`; unreadable → `path not readable`; a mount root containing `:` is an error. All of these exit 1.
3. Resolve the image: `--image`, otherwise `darthjee/tingle_rubycritic:<version>`. `<version>` is read from `shell/linux/VERSION`, located from the module path rather than the cwd. If the file is missing or empty, show an error suggesting `--image` (exit 1).
4. Print the header (`Analyzing:`, `Thresholds:`, `Image:`).
5. Select the files. If none are selected, print `No Ruby files found for analysis.` and exit 0 without any Docker call (not even the preflight).
6. **Preflight:** `docker` on PATH, then `docker info` with a 30 s timeout. A failure exits 1.
7. **Pull when missing:** run `docker image inspect`. If that fails, run `docker pull` with its progress on stderr. A failed pull exits 1.
8. **Run:** `docker run --rm -i --pull never --network none --security-opt no-new-privileges --user <uid>:<gid> -v <root>:/src:ro -w /src <image>`. Stdin gets the selected paths relative to `<root>`, sorted, one per line. There is no timeout.
9. Print a warning for each `parse_errors` entry, then the report. Exit 2 if the `--fail-on` gate failed, otherwise 0.

### File selection (this issue only)
- Reuse `file_size`'s `FileCollector`: `.rb` files only (case-insensitive), minus the default excludes (`file_size`'s list plus `tmp`, `log`, `.bundle`).
- Add a keyword-only `binary_check=True` argument to `FileCollector` and pass `False`, so non-UTF-8 `.rb` files reach the image and become `PARSE` rows.
- A single-file `<path>` mounts its parent directory and sends only the file name.
- Names with a newline, or names that are not valid UTF-8, are skipped with a warning and not counted.

### Output parsing
- Container exit 125 together with `mounts denied` or `not shared from the host` on stderr → Docker Desktop file-sharing hint, exit 1.
- Any other non-zero status → pass the container stderr through, print `RubyCritic failed in <image> (exit N)`, exit 1.
- Exit 0 with invalid JSON, or JSON that fails the structural checks → `could not parse the RubyCritic output`, exit 1.
- Paths: strip a leading `/src/` or `./`, then match exactly against the sent lines. Entries matching no sent line are ignored.
- `Smells` counts the smell entries whose type is not `DuplicateCode`, `HighComplexity` or `VeryHighComplexity`.
- A sent file that is missing from the output → `OK`, complexity `0.00`, rating `-`.
- A file listed in `parse_errors` → `⛔ PARSE` row. It counts as skipped, never triggers `--fail-on`, and takes precedence over `analysed_modules`.

### Report
- Columns: `Status`, `Complexity` (2 decimals), `Rating`, `Smells`, `Duplication`, `File`.
- Rows are sorted by complexity, highest first (ties by path). `PARSE` rows come last.
- `--min-level` and `--top` filter only the level rows. When no row is left, print `No files at or above <LEVEL>.`
- The summary counts every selected file, adds `| k skipped (parse error)` when k > 0, then prints `Score: NN.NN/100 (RubyCritic)` (or `n/a` when the score is null). There is no `Total:` line.

### Tests
Under `python/tests/code_check/rubycritic/`, with `shutil.which` and `subprocess.run` mocked (Docker never actually runs). They cover the list in spec §11. Coverage stays at or above 75%.

### Docs
- A new guide page, `docs/guides/code_check/rubycritic.md`, following the existing per-subcommand convention (`code_check/file_size.md`), plus a row in the subcommand table of `docs/guides/code_check.md`. The page includes the Podman note (it may work when aliased as `docker`, but it is not supported).
- `docs/agents/architecture.md`.
- The `README.md` table.

### Out of scope
- `--exclude`, `--no-default-excludes`, `--ignore`, `--include`, `.gitignore`/`--no-gitignore` and the symlink rule (#296).
- The `rubycritic` config section and `--no-config` (#297).
- Docker-in-Docker: inside the `darthjee/tingle` container, the command fails with "docker not found".

### Verification
- `cd python && ruff check . && pytest`.
- Manual end-to-end check against the image built in #293: `bin/tingle code_check rubycritic docker/rubycritic/fixture --image tingle_rubycritic:dev`.

### Depends on
- #292 (specs, merged).
- #293 (image, merged): its local build is used for manual testing.
- #294 (publishing) is not required to merge this issue. Until it ships, the default image tag only exists after a release.

### Agents
- `python`: the package, tests, and the `FileCollector` change.
- `cli`: `commands/python.json` help and completion.
- `guide`: the user guide pages.
