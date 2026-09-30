# Issue: code_check rubycritic: write specs in docs/agents/specs/code_check/rubycritic/

## Description
Write the specs for the new `tingle code_check rubycritic <path>` subcommand (parent #290). The subcommand measures Ruby code complexity by running [RubyCritic](https://github.com/whitesmith/rubycritic) inside a published Docker image, `darthjee/tingle_rubycritic`.

The specs go under `docs/agents/specs/code_check/rubycritic/`, and `docs/agents/specs.md` indexes them. They are temporary: a later sub-issue of #290 removes them once everything has landed.

## Problem
Parent #290 was split into six implementation sub-issues (#293–#297) and a cleanup (#298). Several of them share contracts:
- the CLI and flag names
- the config keys
- the image stdin/stdout contract
- the RubyCritic JSON fields
- exit codes and the filter order

Without one agreed, normative source, the parallel image track (#293 → #294) and Python track (#295 → #296 → #297) could drift apart. Also, the RubyCritic JSON shape that #290's report design relies on has not been checked against real output.

## Expected Behavior
### What the specs must pin down
Add a shared `README.md` for the contracts used by more than one sub-issue, plus one spec per concern:
- **CLI:** `tingle code_check rubycritic <path>`.
  - Flags: `--warn/--error/--critical` (numbers ≥ 0; defaults 100/200/400, applied to the file's total Flog complexity), `--top`, `--min-level`, `--fail-on` (exit 2), `--image`, `--exclude`/`--no-default-excludes`, `--ignore`, `--include`, `--no-gitignore`, `--no-config`.
  - Only `.rb` files are analysed; there is no `--ext`.
- **Report:** the same layout as `file_size`.
  - Columns: `Status`, `Complexity`, `Rating` (A–F, information only), `Smells` (Reek count), `Duplication` (Flay score), `File`.
  - Rows are sorted by complexity, highest first.
  - The summary gives file counts per level and `Score: NN.NN/100 (RubyCritic)`.
  - `--top`/`--min-level` limit the display only.
- **Image contract:**
  - Run as `docker run --rm -i --network none --user <uid>:<gid> -v <path>:/src:ro -w /src <image>`.
  - The file list comes in on stdin, one relative path per line.
  - The entrypoint runs `rubycritic --format json --no-browser -p /tmp/out <files>` and prints `report.json` on stdout. Everything else goes to stderr; failure → non-zero exit.
  - The image has no git, so there is no churn.
- **RubyCritic JSON fields** used, and how container paths (`/src/...`) map back to paths relative to `<path>`.
- **Default image:** `darthjee/tingle_rubycritic:<tingle version>`, with the version read the way `shell/linux/docker_run.sh` reads `shell/linux/VERSION`.
- **Config:** the `rubycritic` section in `~/.tingle/code_check/config.json`.
  - Keys: `warn`, `error`, `critical`, `top`, `exclude`, `no_default_excludes`, `ignore`, `include`, `gitignore`, `fail_on`, `min_level`, `image`.
  - CLI flags override single values, and list values are merged.
  - A missing file is fine. Invalid JSON, an unknown key or a wrong type → stderr, exit 1.
- **Exit codes:**
  - 0 when all is well.
  - 1 for Docker missing or daemon down, container or RubyCritic failure, unparsable output, bad path, or config error.
  - 2 only for `--fail-on`.
- **Edge cases:**
  - `PARSE` status for files RubyCritic can't parse. They count as skipped and never trigger `--fail-on`.
  - Symlinks pointing outside `<path>` are skipped.
  - A single-file `<path>` → mount its parent directory.
  - No `.rb` files → empty report, exit 0, no container started.
  - Docker Desktop file-sharing hint.
  - Filenames containing a newline are skipped with a warning.
  - Files RubyCritic drops are reported as `OK` with complexity 0.
- **Filter order** shared with `file_size`'s `FileCollector`: default excludes → `--exclude` → `.gitignore` → `--ignore` → `--include`/`.rb`.

### Grounding in real RubyCritic output
The JSON fields and behaviours assumed so far (`complexity`, `rating`, `smells`, `duplication`, overall `score`, parse errors, dropped files) come from RubyCritic's general reputation and have **not** been checked. Before writing `subcommand.md` and `image.md`, the spec author must:

1. Run RubyCritic (the version to pin) with `--format json --no-browser` in a `ruby:3.3-slim` container, **without git installed**, on a small fixture:
   - a simple file
   - a complex file
   - a file with duplicated code
   - a file with a syntax error
   - an empty file
   - a file with no methods
2. Record in the specs:
   - the exact JSON path of every field the report uses (per file and overall)
   - how paths appear in the JSON
   - what happens to the syntax-error file (skipped? warned on stderr? present with an error marker?) and how tingle detects it, so it can show the `PARSE` row
   - whether empty or method-less files are absent from the JSON, which drives the "report as `OK`, complexity 0" rule
   - whether running with no git produces any warning, and whether `-p /tmp/out` works under a read-only `/src` and a foreign uid
3. Put a trimmed sample of the real JSON in `subcommand.md` as the contract example.

If the real output contradicts a decision in #290 (for example, a missing field), the spec says so explicitly and proposes the closest alternative. It must not silently drop the column or rule.

### Pinned values
- **Default excludes:** `file_size`'s `DEFAULT_EXCLUDES` (`node_modules`, `dist`, `build`, `.git`, `vendor`, `third_party`, `.next`, `__pycache__`, `.cache`, `coverage`, `.nuxt`, `out`, `target`) **plus** the Ruby-specific `tmp`, `log` and `.bundle`. `file-selection.md` lists the full set, and `README.md` repeats it.
- **Versions:** the Ruby base image is pinned to an **exact patch**, e.g. `ruby:3.3.N-slim`, and RubyCritic is pinned to the latest stable version at the time of writing, through `Gemfile.lock`. `image.md` records both exact versions. Bumping either one is a deliberate change.
- **Messages:** the same style as `file_size`: `Error: <message>` in red on stderr, then exit 1, and `Warning: <message>` for non-fatal cases. `subcommand.md` lists the exact text for:
  - `docker` not found
  - the Docker daemon not responding
  - a mount failure, with the Docker Desktop file-sharing hint
  - a container or RubyCritic failure, with its stderr passed through
  - output that can't be parsed
  - `<path>` missing or unreadable
  - a skipped filename that contains a newline (warning)
  
  `config.md` reuses `file_size`'s config error wording.
- **Ownership of `docker/`:** the new top-level `docker/` folder, created in #293, is owned by the **`shell`** agent. The specs (`README.md` and `image.md`) record this, and #293 extends `.claude/agents/shell.md`'s scope and adds the folder to `docs/agents/folder-structure.md`.

## Solution
### Spec file layout
The specs use a nested folder, `docs/agents/specs/code_check/rubycritic/`, so that future `code_check` subcommands can get sibling folders. Update the conventions in `docs/agents/specs.md` to allow `<command>/<subcommand>/` folders.

| File | Sub-issue | Content |
|---|---|---|
| `README.md` | #290 (parent) | Overview, links to #290 and every sub-issue, merge order (including the rule that #294 lands before the release that ships #295), and the shared contracts: CLI/flag names, exit codes, config keys, filter order and a summary of the image contract |
| `image.md` | #293 | Dockerfile (Ruby 3.3.x, no git), pinned gem, the entrypoint stdin → stdout JSON contract, the smoke-test fixture, the local `:dev` build |
| `release.md` | #294 | Tagging (same semver as tingle), amd64/arm64 manifest, `scripts/release_image.sh` steps, Docker Hub description, the ordering rule |
| `subcommand.md` | #295 | Preflight, the `docker run` line, the RubyCritic JSON fields used and path mapping, report layout, thresholds, `--top`/`--min-level`/`--fail-on`/`--image`, exit codes, edge cases |
| `file-selection.md` | #296 | Default excludes, `--exclude`/`--no-default-excludes`, `--ignore`/`--include`, `.gitignore`/`--no-gitignore`, symlinks, filter order |
| `config.md` | #297 | `rubycritic` section schema, precedence and list merging, error handling, `--no-config` |

Each feature spec links its sub-issue and can be read on its own. The cleanup sub-issue #298 removes the whole folder.

### Specs index and links
- In `docs/agents/specs.md`, replace "No specs in progress." under **Current specs** with the table from its conventions:

  | Topic | Specs | Parent issue | Sub-issues |
  |---|---|---|---|
  | `code_check rubycritic` | [code_check/rubycritic/](specs/code_check/rubycritic/README.md) | #290 | #292 #293 #294 #295 #296 #297 #298 |

- Also in `specs.md`, extend the **Conventions** section so a topic may be a nested `<command>/<subcommand>/` folder.
- `README.md` links #290 and has a sub-issue table giving, for each sub-issue, its spec file and what it depends on. #292 (specs) and #298 (cleanup) have no feature file.
- Each feature spec links its own sub-issue at the top.
- Cleanup (#298) removes the row, restoring "No specs in progress." if no other specs remain.

### Out of scope
Any implementation. This sub-issue is docs only: no Dockerfile, CI, Python, guide or agent-file changes.

### Agents
- `product-owner` writes the specs and runs the RubyCritic check using Docker.

## Benefits
- A single normative contract lets the image track and the Python track proceed in parallel without drifting apart.
- The report design is based on RubyCritic's real JSON rather than on assumptions.
- Each implementation sub-issue has a self-contained spec to implement against and review against.
