# Cli Plan: code_check js_complexity: add the tingle code_check js_complexity subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

You rely on `python` producing the values in [plan.md](plan.md#shared-contracts): the name, the one-line description, `short_help`, the flags with their defaults, the exit codes and the selection rules. Copy them as they are.

## Implementation Steps

### Step 1 — Update the `code_check` help in `commands/python.json`
- `short_help` → `Code evaluation checks (subcommands: file_size, rubycritic, js_complexity).`
- `long_help`:
  - add `js_complexity   JavaScript/TypeScript code complexity via FTA (Docker).` to the `Subcommands:` list, with the column alignment adjusted;
  - append a `The js_complexity subcommand:` part after the rubycritic one, in the same shape:
    - intro: FTA in `darthjee/tingle_js_complexity`, Docker required, the image pulled when missing, `Cyclo`/`Lines`/`Assessment` for information only;
    - `Usage:` and the `<path>` description;
    - `File selection:` as a prose paragraph with no flags: the 8 extensions (any case), declaration files always skipped, the default excludes (`node_modules, dist, build, ..., .turbo, .svelte-kit, .output, .vercel, .parcel-cache, storybook-static`), the symlink and single-file rules;
    - `Thresholds:` (50/60/75 on the file's FTA score, decimals allowed);
    - `Display:` (`--top`, `--min-level`);
    - `CI gate:` (`--fail-on`, never triggered by parse errors);
    - `Image:`;
    - `Exit codes:` (0 also when no JavaScript/TypeScript files are found);
    - the stdout/stderr and colour sentence;
    - `Examples:` (`./src`, thresholds, `--top 10`, `--min-level warn`, `--fail-on error`, `--image tingle_js_complexity:dev`).
- Do **not** document `--exclude`, `--ignore`, `--include`, `--no-gitignore`, `--no-default-excludes`, `--no-config`, a configuration section or `--details`. They come in #321/#322/#325.
- Keep the file valid JSON (escaped newlines and quotes) and wrap lines at the same width as the rubycritic part.

## Files to Change
- `commands/python.json`: `code_check` `short_help` and `long_help`.

## Notes
- Check against `tingle --help code_check` after `python` lands, so the flag help matches `flags.py`.
- Completion is in `python/code_check/completion.py` (python's scope). `commands.sh` already forwards to it, so no shell completion change is expected. Check `tingle code_check js<TAB>` once both are in.
