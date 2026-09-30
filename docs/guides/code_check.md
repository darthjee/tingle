# `tingle code_check`

Code evaluation checks, grouped as subcommands.

## What it does

`tingle code_check` groups tools that look at a codebase and report on it.
Each check is a subcommand with its own options and its own guide. The
subcommands share one configuration file and one exit-code convention, so
they behave the same way in scripts and CI jobs.

## Usage

```
tingle code_check <subcommand> [options]
```

The subcommand comes first; its options follow it.

## Subcommands

| Subcommand | Description |
|---|---|
| [`file_size`](code_check/file_size.md) | Token efficiency triage: file size analysis. |

Subcommand names are exact: `file_size` works, `file-size` and `FILE_SIZE`
do not.

## Help

| Command | What it shows |
|---|---|
| `tingle code_check` | The list of subcommands. |
| `tingle code_check -h` or `tingle code_check --help` | The list of subcommands. |
| `tingle code_check -h <subcommand>` | The help of that subcommand. |
| `tingle code_check <subcommand> --help` | The help of that subcommand. |

These all exit with status `0`.

An unknown subcommand is an error, and so is an option given before the
subcommand. In both cases tingle prints an error and the list of
subcommands, then exits with status `1`:

```
$ tingle code_check nope
Error: unknown subcommand 'nope'

$ tingle code_check --top 5 file_size .
Error: expected a subcommand before options (got '--top')
```

## Configuration file

All subcommands read defaults from the same file:

```
~/.tingle/code_check/config.json
```

The file holds a JSON object with one top-level section per subcommand.
Each subcommand reads only its own section and ignores the others. The keys
of each section are documented on the subcommand's page.

| Subcommand | Section | Keys |
|---|---|---|
| `file_size` | `file_size` | [Configuration file](code_check/file_size.md#configuration-file) |

For example:

```json
{
  "file_size": {
    "warn": 200,
    "fail_on": "error"
  }
}
```

## Exit status

Every subcommand uses the same exit codes:

| Status | Meaning |
|---|---|
| `0` | Success, or the check gate passed or was not requested |
| `1` | Usage or configuration error (unknown subcommand or option, invalid value, invalid config file, ...) |
| `2` | The check gate failed (for `file_size`, `--fail-on`) |

## Migrating from `check_file_size`

`tingle check_file_size` was renamed to `tingle code_check file_size`. The
old name is still available as an alias: it takes the same options and
produces the same output and exit codes, but it is deprecated and prints a
warning on stderr before running:

```
Warning: 'tingle check_file_size' is deprecated; use 'tingle code_check file_size'.
```

The warning goes to stderr only, so stdout and the exit status are not
affected. The alias will be removed in a future release, so update your
scripts and CI jobs to call `tingle code_check file_size` instead:

```
# Before
tingle check_file_size --fail-on error .

# After
tingle code_check file_size --fail-on error .
```

The configuration file section was renamed too: `file_size` now reads the
`file_size` section of `~/.tingle/code_check/config.json`. The old
`check_file_size` section is still read, but it prints a deprecation warning
on stderr:

```
Warning: /home/me/.tingle/code_check/config.json: 'check_file_size' section is deprecated; rename it to 'file_size'.
```

Having both sections in the file is a config error (exit status `1`). To
migrate, rename the `check_file_size` key to `file_size`. See
[Legacy `check_file_size` section](code_check/file_size.md#legacy-check_file_size-section)
for details.

## Quick help

For a short summary of the command and its subcommands, run:

```
tingle --help code_check
```
