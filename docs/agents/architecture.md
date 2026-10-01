# Architecture

## Overview

Tingle is a flat collection of independent, single-purpose utility scripts —
there is no shared application runtime or framework. Each script solves one
recurring task on its own, in whichever language is the best fit (Bash,
Python, or Node.js).

## Source Code Layout

There is no single main source folder; scripts are grouped by language:

### `shell/`

Bash/Shell scripts. Best fit for simple file/OS-level operations and gluing
together other CLI tools.

`shell/linux/` holds `tingle linux`, which runs GNU/Linux tools in the
`darthjee/tingle` image through `docker_run <mode> [docker-args...] --
<command> [args...]` (`shell/linux/docker_run.sh`). Handlers pass any extra
`docker run` args before `--`: `tingle linux shell` uses that slot for its
host integration (git, ssh, kube and aws config, the SSH agent, and
`--network host` on native Linux Docker, all skipped with `--isolated` or
`TINGLE_LINUX_ISOLATED=1`), while `tingle linux sed` stays a bare
`docker_run stdin -- sed ...`. See
[tingle-linux-image.md](tingle-linux-image.md#shell-host-integration).

### `python/`

Python scripts. Best fit for tasks needing richer data manipulation, parsing,
or third-party libraries.

### `node/`

Node.js scripts. Best fit for tasks that benefit from the npm ecosystem
(e.g. working with JSON/APIs).

### Command entrypoint convention

Every command's entry point is `<language>/<command>/main.<extension>` (e.g.
`python/code_check/main.py`, `shell/install/main.sh`) — this is the file
`commands/*.json`'s `path` field points at, and the only thing `bin/tingle`
dispatches to.

- `main.<ext>` is a thin dispatcher, never invoked directly by the user with
  raw command args: `bin/tingle` (or the completion hub) always prepends a
  leading flow verb, `run` or `complete`, as argv[1] / `$1`. `main.<ext>`
  reads that verb and forwards the rest of argv (argv[2:]) to either:
  - the executor, `<command>/executor.<ext>`, for `run`; or
  - the completion handler, `<command>/completion.<ext>`, for `complete`.
- Completion is opt-in per command. The completion hub (see `completions/`
  below) detects support by checking whether `completion.<ext>` exists next
  to a command's `main.<ext>` — it never invokes `main.<ext> complete` to
  probe for support. Commands without a `completion.<ext>` (e.g. the
  `check_file_size` alias, `install`) get the hub's generic native
  file/folder completion fallback instead.
- A completion handler's stdout is the list of suggestions, which the hub
  filters with `compgen -W "<output>" -- "$cur"`. Empty output means no
  suggestions. If the whole output, with surrounding whitespace trimmed, is
  exactly the reserved sentinel `__tingle_files__`, the hub instead uses its
  native file/folder completion — the same fallback a command with no
  `completion.<ext>` gets. Use it for positions that take a path (e.g.
  `tingle linux sed <TAB>`). `code_check`'s completion, for example,
  returns subcommand names at the first position, flag names when the word
  being typed starts with `-`, and `__tingle_files__` for the path position.
  Each subcommand's completion is driven by its own `flags.FLAGS`
  (`code_check.file_size.flags`, `code_check.rubycritic.flags`):
  `flag_tables(flags)` in `python/code_check/completion.py` turns a `FLAGS`
  list into its flag names and value-taking flags (with their `choices`), and
  `SUBCOMMAND_FLAGS` maps each subcommand name to those tables. Adding a
  subcommand means adding its entry there.
- A completion handler receives raw argv, including a possibly-empty
  trailing element for the word currently being typed, and must not run it
  through a strict parser (e.g. `argparse`) — that trailing empty string is
  significant and would break/be rejected by a strict parser.

### Breaking a command down once it outgrows a single file

Most Python (and other language) scripts stay a single file for their
executor. Once a command's logic grows too large for one file, break it down
following this pattern instead of inventing a one-off structure:

- The executor (`executor.<ext>`) stays a thin shell: parse args, instantiate
  the orchestrator class, call it, exit.
- Reusable/common code (e.g. the generic argument parser) lives in
  `python/common/` (or the equivalent `<lang>/common/` folder), not inside
  the command's own package.
- Argument parsing goes through the shared `ArgParser`
  (`python/common/arg_parser.py`):
  - `ArgParser(flags: list[dict], prog: str | None = None)` — `flags` is a
    list of dicts shaped like `argparse.add_argument`'s kwargs plus a
    `"name"` key for the flag string, e.g.
    `{"name": "--warn", "type": int, "default": 300, "help": "..."}`.
    `prog` is optional and sets the program name shown in `usage:` and help
    output (e.g. `"tingle code_check file_size"`); when omitted, argparse's
    default is used.
  - `.parse(argv: list[str] | None = None) -> dict` — parses (defaulting to
    `sys.argv[1:]`) and returns a plain `dict` of option name → value (not an
    `argparse.Namespace`).
  - Command-specific code only supplies its flag list and calls
    `ArgParser(flags).parse()`, instead of building its own
    `argparse.ArgumentParser`.
- Beyond arg parsing, a command breaks its own logic down by class/file as
  needed: it becomes a package under `python/<command>/` (package-style,
  `__init__.py` + one file per class), with the orchestrator class named
  after the command.

`python/code_check/file_size/` is the first example of this pattern in
practice: it holds `executor.py` (the `CheckFileSize` orchestrator class),
`constants.py`, `config.py` (its config section), `flags.py` (its flag
list), `skip_checks.py`, `glob_matcher.py`, `git_ignore.py`,
`file_collector.py`, `file_analyzer.py`, and `reporter.py`. Helpers shared
by all `code_check` subcommands sit one level up in `python/code_check/`:
`palette.py` (`Palette` plus `Colors`), a generic `config.py`
(`default_path`, `load_section`, `ConfigError`) and `subcommands.py`
(`SUBCOMMAND_NAMES`, import-light so completion can read it).

`python/code_check/rubycritic/` follows the same layout:

- `executor.py` — `CheckRubycritic` (`PROG = "tingle code_check rubycritic"`).
  `run` calls `_execute(options)` and catches `RubycriticError` in one place,
  printing it and exiting 1.
- `constants.py` — thresholds, default excludes, the image repository, the
  `VERSION` file path, the `docker info` timeout, the mount-error markers
  and the smell types that are not counted.
- `errors.py` — `RubycriticError`, the user-facing error.
- `flags.py` — the import-light `FLAGS` list (shared by the parser and
  completion).
- `image.py` — `resolve_image`: `--image`, or the default image.
- `selection.py` — `Selection`: the mount root, the `.rb` paths sent on
  stdin and the warnings for names that cannot be sent.
- `docker_runner.py` — `DockerRunner`: preflight, pull, run and outcome check.
- `output_parser.py` — checks the container's JSON and maps its paths back to
  the sent lines (`OutputFormatError` on a contract break). The JSON shape is
  pinned in
  [tingle-rubycritic-image.md](tingle-rubycritic-image.md#rubycritic-json-contract).
- `reporter.py` — the header, table, summary and `Score:` line.

The Docker runner contract, in short (the code and its tests are the
reference for the full rules):

- Preflight: `shutil.which("docker")`, then `docker info` with a 30 s
  timeout.
- Image: `docker image inspect <image>`; when it is missing, `docker pull`
  with its progress on stderr.
- Run: `docker run --rm -i --pull never --network none --security-opt
  no-new-privileges --user <uid>:<gid> -v <root>:/src:ro -w /src <image>`,
  with the selected paths (relative to `<root>`) on stdin, one per line. All
  commands are list-form, never through a shell.
- Default image: `darthjee/tingle_rubycritic:<version>`, where `<version>` is
  read from `shell/linux/VERSION`, located relative to the module path (not
  the working directory).
- No Docker-in-Docker: tingle calls the host's `docker`, it never runs
  inside a container itself.

**`FileCollector` reuse.** `rubycritic` imports `FileCollector` straight
from `code_check.file_size.file_collector` and passes the keyword-only
`binary_check=False` (the default `True` keeps `file_size`'s binary skip).
This is an intentional exception to the "move a helper up once a second
consumer needs it" rule below: the collector stays in `file_size/` until a
third consumer, or a change that only one side needs, makes the move worth
it.

#### Subcommand dispatch

A command that groups several related checks under one name (e.g.
`tingle code_check <subcommand>`) keeps the usual `main.py` /
`executor.py` / `completion.py` trio at its top level, and puts each
subcommand in its own sub-package. `python/code_check/` is the reference:

- `python/code_check/executor.py` holds `CodeCheck`, whose static
  `SUBCOMMANDS` dict maps each exact subcommand name to its class and a
  one-line description:

  ```python
  SUBCOMMANDS = {
      "file_size": (CheckFileSize, "Token efficiency triage: file size analysis."),
      "rubycritic": (CheckRubycritic, "Ruby code complexity via RubyCritic (Docker)."),
  }
  ```

  There are no argparse subparsers: names are matched exactly, with no case
  folding and no aliases.
- `SUBCOMMAND_NAMES` in `python/code_check/subcommands.py` must list the same
  names as `SUBCOMMANDS`, in the same order; completion reads it so it never
  imports a subcommand implementation. A test enforces that the two match.
- `CodeCheck.run` looks up `args[0]` in `SUBCOMMANDS` and forwards
  `args[1:]` to that subcommand unchanged. `-h <sub>` / `--help <sub>` is
  forwarded as `<sub> -h`.
- Exit codes:
  - `0` — no args, `-h` or `--help`: lists the subcommands, then
    `Run 'tingle code_check <subcommand> --help' for its options.`
  - `1` — unknown subcommand (`Error: unknown subcommand '<x>'`) or a flag
    before the subcommand (`Error: expected a subcommand before options
    (got '<flag>')`); both print in red to stderr, followed by the list.
  - `2` — reserved for check gates such as `--fail-on`. A subcommand's own
    exit code is forwarded unchanged.
- Code used by a single subcommand stays in that subcommand's package. Move
  a helper up to the parent package (or to `python/common/`) only once a
  second consumer needs it. The one current exception is `FileCollector`,
  shared by `file_size` and `rubycritic` (see above).
- When an existing command becomes a subcommand, its old entry point stays
  as a thin shim so existing callers keep working. `python/check_file_size/`
  (`__init__.py`, `main.py`) is that shim: it forwards to
  `code_check/file_size` and prints
  `Warning: 'tingle check_file_size' is deprecated; use 'tingle code_check file_size'.`
  on stderr. Stdout and exit codes are unchanged. Its `commands/python.json`
  entry still points at `python/check_file_size/main.py`. The shim is kept
  until a future issue removes the alias.

#### kube AWS credentials

`python/kube/auth.py` owns the AWS side of kube's pre-check. It works out
which credentials the AWS CLI will use and checks that they are valid. It
does this before kube touches the cluster, so a bad login fails early with a
clear message instead of an opaque `kubectl` error. It exposes two functions:

- `detect_credential_source() -> str` reads the process environment and
  returns one of:
  - `"env"`: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are both set
    and non-empty.
  - `"partial"`: only one of the two is non-empty.
  - `"profile"`: neither is set.

  `AWS_SESSION_TOKEN` does not affect detection. It is still passed to the
  AWS CLI through the environment, so temporary credentials keep working.
- `check_aws_credentials(profile: str | None) -> tuple[bool, str | None]`
  runs `aws sts get-caller-identity` and returns `(True, None)` on success
  or `(False, <error>)` on failure.
  - **`None`-profile convention:** with a profile name it adds
    `--profile <profile>`. With `profile=None` it leaves the flag out, so
    the AWS CLI uses its own credential chain, starting with the environment
    variables. The caller (`executor.py`) passes `None` when the source is
    `"env"`, and passes the configured `aws_profile` for `"partial"` and
    `"profile"`.

No config key was added for this. `aws_profile` (default `"default"`) is
still the only AWS setting in kube's config. It is ignored when the
environment already has full credentials. See [flow.md](flow.md#kube-aws-credential-pre-check)
for the runtime sequence.

#### Test folder location

Tests for `python/` live under `python/tests/`, mirroring the package layout
under `python/` (e.g. `python/tests/code_check/file_size/`,
`python/tests/common/`, `python/tests/code_check/rubycritic/`), rather than
a top-level `tests/`. Future Python commands under this repo should follow
the same pattern.

The `rubycritic` tests mock `shutil.which` and `subprocess.run`, so Docker
never runs in the test suite; a shared container output sample lives in
`python/tests/code_check/rubycritic/sample_output.py`.

### `bin/`

Callable entry points intended to be placed on `PATH`. Each file here is a
thin wrapper that dispatches to the actual implementation in `shell/`,
`python/`, or `node/` — this is the only folder users should invoke directly.

### `completions/`

Holds the bash completion scripts for `tingle`:

- `completions/tingle.bash` — central hub, sourced from `~/.bashrc` by
  `tingle install`. Sources the two files below and registers the
  `complete -F` dispatcher for the `tingle` command.
- `completions/bash/tingle.sh` — level-one completion: command names (reads
  `commands/*.json`).
- `completions/bash/commands.sh` — level-two completion: command-specific
  arguments. Delegates to a command's own `completion.<ext>` via
  `tingle resolve <cmd>` when one exists, or falls back to native
  file/folder completion (`compgen -f` + `compopt -o filenames`) otherwise.
  The same file/folder fallback runs when a handler prints exactly the
  sentinel `__tingle_files__`.

### `.circleci/`

Holds the CI pipeline config (`.circleci/config.yml`). Owned by `architect`,
since CI is cross-cutting rather than belonging to a single language
specialist.

## Conventions

- Each script is self-contained: no shared internal library or cross-script
  imports unless a clear, recurring need arises.
- Each script documents its own usage and dependencies in a header comment.
- New scripts are registered in the table in `README.md`.
