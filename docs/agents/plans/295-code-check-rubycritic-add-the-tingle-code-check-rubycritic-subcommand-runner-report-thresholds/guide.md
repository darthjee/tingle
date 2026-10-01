# Guide Plan: code_check rubycritic: add the tingle code_check rubycritic subcommand

Main plan: [plan.md](plan.md)

## Shared contracts

What this agent relies on, produced by `python` and `cli`:
- The description `Ruby code complexity via RubyCritic (Docker).`
- The flag set, defaults and exit codes in [plan.md](plan.md#shared-contracts).
- Messages verbatim from spec §10 ([subcommand.md](../../specs/code_check/rubycritic/subcommand.md)).
- The default excludes: `file_size`'s list plus `tmp`, `log` and `.bundle`.

## Implementation Steps

### Step 1 — Write docs/guides/code_check/rubycritic.md
Follow the `docs/guides/code_check/file_size.md` convention.

**Opening**
- Title ``# `tingle code_check rubycritic` ``.
- A tagline.
- A line saying this is a subcommand of [`tingle code_check`](../code_check.md).

**What it does**
- `.rb` files are selected on the host, then RubyCritic (Flog, Flay, Reek) runs in `darthjee/tingle_rubycritic`.
- The level comes from each file's total Flog complexity.
- The rating (A–F) is for information only.

**Requirements**
- Docker on PATH with a running daemon. No host Ruby is needed.
- The image is pulled automatically on first use, with progress on stderr. Pinned tags are never pulled again.
- Podman note: it may work when aliased as `docker`, but it is not supported.
- Docker Desktop's file-sharing setting must cover the folder.
- One sentence on the sandbox: no network, read-only mount, your uid/gid.

**Usage**
- A directory is scanned recursively.
- A single `.rb` file mounts its parent directory.

**Options table**
- Rows: `--warn`, `--error`, `--critical`, `--top`, `--min-level`, `--fail-on` and `--image`.
- Add `###` subsections for `--min-level`/`--top` (level rows only, PARSE rows always shown), `--fail-on` (never PARSE rows) and `--image` (local builds, default tag from tingle's version, error suggesting `--image`).

**Skipped files**
- The full default exclude list.
- There is no binary check, so non-UTF-8 `.rb` files appear as PARSE rows.
- Names with a newline, or names that are not UTF-8, are skipped with a warning.

**Reading the output**
- Use the spec §6 sample.
- Explain:
  - the Header;
  - the Columns;
  - the Classifications, including `⛔ PARSE`;
  - the sort order;
  - the Summary, including `| k skipped (parse error)` and `Score: …/100 (RubyCritic)` or `n/a`;
  - the parse warnings;
  - that files missing from the output show as OK `0.00` `-`;
  - the Colours (TTY only, and `NO_COLOR`).

**Examples**
- A basic run, custom thresholds, `--top`/`--min-level`, `--image tingle_rubycritic:dev` and a single file.
- A `### Using in CI` section with `--fail-on error`.

**Exit status and errors**
- A `Situation | Output | Exit status` table with every case from spec §9/§10.
- Then the short 0/1/2 table.

**Limitations**
- No Docker-in-Docker: inside the `darthjee/tingle` container the command fails with "docker not found".
- Exclude, ignore and include flags and `.gitignore` support are not available yet.
- There is no config-file section and no `--no-config` yet.

**Quick help**
- `tingle code_check rubycritic --help` and `tingle --help code_check`.

### Step 2 — Update the guide indexes
**`docs/guides/code_check.md`**
- Add ``| [`rubycritic`](code_check/rubycritic.md) | Ruby code complexity via RubyCritic (Docker). |`` to the `## Subcommands` table, after `file_size`.
- In `## Configuration file`, note that `rubycritic` does not read the config file yet.
- In `## Exit status`, generalise the `2` row to "`--fail-on` gate failed", so it no longer names only `file_size`.
- Optionally mention `rubycritic` in the "Subcommand names are exact" line.

**`docs/guides/README.md`**
- Add a nested entry under `code_check`, after `file_size`: ``- [`rubycritic`](code_check/rubycritic.md) — Ruby code complexity via RubyCritic (Docker).`` (indented two spaces)

## Files to Change
- `docs/guides/code_check/rubycritic.md`: new user guide page.
- `docs/guides/code_check.md`: subcommand table row, config note and exit-status wording.
- `docs/guides/README.md`: nested index entry.

## Notes
- Keep the page in sync with the final `long_help` in `commands/python.json` and with the `flags.py` help texts.
- The specs `file-selection.md` §7 and `config.md` say #296 and #297 will update "the `rubycritic` section of `docs/guides/code_check.md`". With a separate page, those issues should update `code_check/rubycritic.md` instead. That spec wording is `product-owner`'s to fix (see [product-owner.md](product-owner.md)).
- The root `README.md` row is handled by the architect, not this agent.
