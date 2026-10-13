# Guide Plan: code_check js_complexity: add the tingle code_check js_complexity subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

You rely on the values in [plan.md](plan.md#shared-contracts): name, description, flags and defaults, exit codes, messages, the selection rules and the report layout (spec §6). Only the #320 flags exist. Do not document selection flags, config, `--details`, `Dup` or SFC files as available.

## Implementation Steps

### Step 1 — Write `docs/guides/code_check/js_complexity.md`
Follow the structure of `docs/guides/code_check/rubycritic.md`:
- what it does (FTA in Docker, no Node on the host) and the requirements (Docker running, image pulled on first use, Docker Desktop file sharing);
- usage and the `<path>` rules (directory or single file; the single file mounts its parent);
- which files are analysed: extensions, declaration files skipped, default excludes, symlinks, unsendable names;
- thresholds and levels on the rounded FTA score, with FTA's own bands (50/60) and tingle's `critical=75`;
- reading the report: header, columns, `⛔ PARSE` rows, dropped files shown as `OK 0.0`, the summary and `FTA score`. Reuse the spec §6 full example;
- display flags, the `--fail-on` CI gate, `--image` (including a local `tingle_js_complexity:dev`);
- exit codes and the common errors with their exact texts (spec §10);
- limitations:
  - Podman aliased as `docker` may work but is not supported;
  - no Docker-in-Docker inside the `darthjee/tingle` image;
  - minified bundles and generated code are analysed and likely `CRITICAL`. Mention that `--ignore`/`--exclude` and the `*.min.js` skip are coming (#321/#323), rather than documenting flags that do not exist yet.

### Step 2 — Update the index `docs/guides/code_check.md`
- Add the `js_complexity` row to the subcommand table with the shared one-line description.
- Mention `js_complexity` next to `file_size`/`rubycritic` in the exact-names sentence.
- Do **not** add a config-section row yet (#322).

## Files to Change
- `docs/guides/code_check/js_complexity.md`: new guide.
- `docs/guides/code_check.md`: index row and the name sentence.

## Notes
- The Podman note and the generated-code/minified advice are required by spec §1.
- Keep the guide markdownlint-clean (`.markdownlint.json`).
