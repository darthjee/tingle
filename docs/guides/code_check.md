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
| `file_size` | `check_file_size` | [Configuration file](code_check/file_size.md#configuration-file) |

For example:

```json
{
  "check_file_size": {
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

## Quick help

For a short summary of the command and its subcommands, run:

```
tingle --help code_check
```
