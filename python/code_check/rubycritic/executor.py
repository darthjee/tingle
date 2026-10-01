#!/usr/bin/env python3
"""executor.py — Ruby code complexity via RubyCritic (Docker).

Selects the `.rb` files under `<path>` on the host, runs RubyCritic (Flog,
Flay and Reek) inside the `darthjee/tingle_rubycritic` Docker image and
reports one row per file, classified by thresholds on the file's total Flog
complexity, plus RubyCritic's overall score. The host needs Docker, not Ruby.

File selection follows `file_size`: default and `--exclude` directory names,
`.gitignore` (unless `--no-gitignore`), `--ignore` and `--include` globs and
the fixed `.rb` filter. Symlinks resolving outside the mount root are skipped.

Personal defaults are read from the `rubycritic` section of
`~/.tingle/code_check/config.json` (keys: warn, error, critical, top, exclude,
ignore, include, no_default_excludes, gitignore, fail_on, min_level, image,
details; there is no `ext`). Single values given on the CLI win over the
config, which wins over the built-in defaults; list values (exclude, ignore,
include) are concatenated, config first, and deduplicated.
`--no-default-excludes` and `--no-gitignore` win over the config. An invalid
config prints `Error: <path>: <reason>` and exits with status 1 before any
file selection or Docker call. `--no-config` skips the file entirely.

Example config:
    {"rubycritic": {"warn": 50, "ignore": ["spec/fixtures/**"], "fail_on": "error"}}

Exit status: 0 on success (also when no `.rb` file is selected), 1 on errors
(bad option, invalid config, path missing or unreadable, Docker missing or
failing, image pull failure, unparsable output) and 2 when `--fail-on` is set
and any file reaches that level.

Dependencies: standard library only; Docker on the host at run time.

Usage:
    tingle code_check rubycritic <path> [options]

Examples
--------
    tingle code_check rubycritic ./app
    tingle code_check rubycritic ./app --warn 50 --error 100 --critical 200
    tingle code_check rubycritic ./app --top 10 --min-level warn
    tingle code_check rubycritic ./app --fail-on error
    tingle code_check rubycritic ./app --details
    tingle code_check rubycritic ./app --details 0
    tingle code_check rubycritic ./app --image tingle_rubycritic:dev
    tingle code_check rubycritic . --exclude spec,db
    tingle code_check rubycritic . --no-default-excludes --exclude vendor
    tingle code_check rubycritic . --ignore 'db/migrate/**' --ignore '*_spec.rb'
    tingle code_check rubycritic . --include 'app/**' --include 'lib/**'
    tingle code_check rubycritic . --no-gitignore
    tingle code_check rubycritic . --no-config

"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code_check.config import default_path, load_section
from code_check.excludes import parse_excludes, resolve_excludes
from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.palette import Palette
from code_check.rubycritic.config import ConfigError, validate
from code_check.rubycritic.constants import Constants
from code_check.rubycritic.docker_runner import DockerRunner, decode, write_stderr
from code_check.rubycritic.errors import RubycriticError
from code_check.rubycritic.flags import FLAGS
from code_check.rubycritic.image import resolve_image
from code_check.rubycritic.output_parser import OutputFormatError, ParsedOutput, parse
from code_check.rubycritic.reporter import Reporter
from code_check.rubycritic.selection import Selection, select_files
from common.arg_parser import ArgParser

# Program name shown in the help usage line.
PROG = "tingle code_check rubycritic"

# Section of the config file holding this command's options.
CONFIG_SECTION = "rubycritic"

# Built-in defaults for single-value options, applied after the config merge.
SINGLE_DEFAULTS: dict = {
    "warn": Constants.DEFAULT_WARN,
    "error": Constants.DEFAULT_ERROR,
    "critical": Constants.DEFAULT_CRITICAL,
    "top": 0,
    "fail_on": None,
    "min_level": "ok",
    "image": None,
    "details": None,
}

# Glob-list options merged as config list then CLI list (deduplicated).
LIST_KEYS = ("ignore", "include")

# Threshold options validated as numbers >= 0.
THRESHOLD_KEYS = ("warn", "error", "critical")


class CheckRubycritic:
    """Orchestrate the flow: parse → validate → resolve → select → run → report."""

    @staticmethod
    def _parse(arg_parser: ArgParser, args: list[str]) -> dict:
        """Parse args, remapping argparse usage errors (exit 2) to exit 1.

        Exit status 2 is reserved for a failed `--fail-on` gate; `--help`
        still exits 0.
        """
        try:
            return arg_parser.parse(args)
        except SystemExit as exc:
            if exc.code not in (0, None):
                raise SystemExit(1) from exc
            raise

    @staticmethod
    def _fail(message: str) -> None:
        """Print `Error: <message>` in red on stderr and exit with status 1."""
        err = Palette(sys.stderr)
        print(f"{err.RED}Error: {message}{err.RESET}", file=sys.stderr)
        sys.exit(1)

    @staticmethod
    def _warn(message: str) -> None:
        """Print `Warning: <message>` in yellow on stderr."""
        err = Palette(sys.stderr)
        print(f"{err.YELLOW}Warning: {message}{err.RESET}", file=sys.stderr)

    @classmethod
    def _load_config(cls, no_config: bool) -> tuple[dict, Path | None]:
        """Load and validate the `rubycritic` config section.

        Returns `(section, path)`; `path` is None when nothing was loaded
        (`--no-config`, missing file or missing section). A `ConfigError`
        prints `Error: <path>: <reason>` and exits with status 1.
        """
        if no_config:
            return {}, None
        path = default_path()
        try:
            section = load_section(CONFIG_SECTION, path)
            if section is None:
                return {}, None
            return validate(section, path), path
        except ConfigError as exc:
            cls._fail(str(exc))
            raise  # unreachable: _fail exits

    @staticmethod
    def _merge(cli: dict, config: dict) -> dict:
        """Resolve every option from the CLI args and the validated config section.

        Single values: built-in default < config < CLI (a config `null` means
        unset). Lists: config then CLI, concatenated and deduplicated.
        `--no-default-excludes` and `--no-gitignore` only turn behaviour off
        and win over the config.
        """
        merged = {"path": cli["path"]}
        for key, default in SINGLE_DEFAULTS.items():
            if cli.get(key) is not None:
                merged[key] = cli[key]
            else:
                merged[key] = config.get(key, default)
        for key in LIST_KEYS:
            merged[key] = list(dict.fromkeys(config.get(key, []) + (cli.get(key) or [])))
        excludes = config.get("exclude", []) + parse_excludes(cli.get("exclude"))
        merged["exclude"] = list(dict.fromkeys(excludes))
        merged["no_default_excludes"] = bool(cli.get("no_default_excludes")) or config.get(
            "no_default_excludes", False
        )
        merged["gitignore"] = not cli.get("no_gitignore") and config.get("gitignore", True)
        return merged

    @staticmethod
    def _validate(options: dict) -> dict:
        """Reject negative (or NaN) thresholds, a negative `--top`/`--details` and an empty `--image`."""
        for key in THRESHOLD_KEYS:
            value = options[key]
            if not (value >= 0):  # also rejects NaN
                raise RubycriticError(f"--{key} must be a number >= 0")
        if options["top"] < 0:
            raise RubycriticError("--top must be an integer >= 0")
        if options.get("details") is not None and options["details"] < 0:
            raise RubycriticError("--details must be an integer >= 0")
        if options["image"] is not None and not options["image"]:
            raise RubycriticError("--image must not be empty")
        return options

    @staticmethod
    def _resolve_target(path: str) -> tuple[Path, Path]:
        """Resolve `path` and its mount root (the directory, or a file's parent).

        Raises `RubycriticError` when the path is missing or unreadable, or
        when the mount root holds a `:` (Docker's `-v` cannot express it).
        """
        target = Path(path).resolve()
        if not target.exists():
            raise RubycriticError(f"path not found: {target}")
        is_dir = target.is_dir()
        mode = os.R_OK | os.X_OK if is_dir else os.R_OK
        if not os.access(target, mode):
            raise RubycriticError(f"path not readable: {target}")
        root = target if is_dir else target.parent
        if ":" in str(root):
            raise RubycriticError(
                f"cannot mount {root}: Docker volume paths cannot contain ':'"
            )
        return target, root

    @staticmethod
    def _print_header(
        out: Palette, target: Path, options: dict, image: str, config: Path | None = None
    ) -> None:
        """Print the analysis header (target, thresholds, image and loaded config file)."""
        thresholds = " | ".join(
            f"{key}={format(options[key], 'g')}" for key in THRESHOLD_KEYS
        )
        print(f"{out.CYAN}{out.BOLD}Analyzing:{out.RESET} {target}")
        print(f"{out.DIM}Thresholds: {thresholds}{out.RESET}")
        print(f"{out.DIM}Image: {image}{out.RESET}")
        if config is not None:
            print(f"{out.DIM}Config: {config}{out.RESET}")
        print()

    @staticmethod
    def _selection_options(options: dict) -> dict:
        """Resolve the merged file-selection options into `select_files` keyword arguments.

        The merged `exclude` names are added to the default excludes (dropped
        when `no_default_excludes` is set), `ignore`/`include` default to no
        globs and `gitignore` defaults to on.
        """
        return {
            "excludes": resolve_excludes(
                Constants.DEFAULT_EXCLUDES,
                options.get("exclude") or [],
                bool(options.get("no_default_excludes")),
            ),
            "ignore": options.get("ignore") or [],
            "include": options.get("include") or [],
            "gitignore": options.get("gitignore", True),
        }

    @classmethod
    def _select(cls, out: Palette, target: Path, root: Path, options: dict) -> Selection:
        """Select the files, warning about unsendable names.

        Exits 0 with `No Ruby files found for analysis.` (before any Docker
        call) when nothing is left to send.
        """
        selection = select_files(target, root, **cls._selection_options(options))
        for message in selection.skipped:
            cls._warn(message)
        if not selection.lines:
            print(f"{out.YELLOW}No Ruby files found for analysis.{out.RESET}")
            sys.exit(0)
        return selection

    @staticmethod
    def _parse_output(proc, lines: list[str], image: str) -> ParsedOutput:
        """Parse the container stdout; on a contract break pass its stderr through and fail."""
        try:
            return parse(decode(proc.stdout), lines)
        except OutputFormatError as exc:
            write_stderr(proc)
            raise RubycriticError(
                f"could not parse the RubyCritic output from {image}: {exc.reason}"
            ) from exc

    @staticmethod
    def _check_methods(parsed: ParsedOutput, details: int | None, image: str) -> None:
        """Fail when `--details` is set but the image printed no per-method data."""
        if details is not None and parsed.methods is None:
            raise RubycriticError(
                f"the RubyCritic output from {image} has no per-method data; "
                "--details needs a newer tingle_rubycritic image"
            )

    @staticmethod
    def _gate_failed(analyzer: FileAnalyzer, parsed: ParsedOutput, fail_on: str | None) -> bool:
        """Return True when `--fail-on` is set and any (non-PARSE) file reaches it."""
        if fail_on is None:
            return False
        return any(analyzer.reaches(r.complexity, fail_on) for r in parsed.results.values())

    def _execute(self, options: dict, config_file: Path | None = None) -> int:
        """Run the whole analysis for validated `options`; return the exit status.

        `config_file` is the loaded config file shown in the header, if any.

        Every failure raises `RubycriticError`.
        """
        target, root = self._resolve_target(options["path"])
        image = resolve_image(options["image"])
        out = Palette(sys.stdout)
        self._print_header(out, target, options, image, config_file)
        selection = self._select(out, target, root, options)

        runner = DockerRunner(image)
        runner.preflight()
        runner.ensure_image()
        proc = runner.run(root, selection.lines)
        runner.check_outcome(proc, root)
        parsed = self._parse_output(proc, selection.lines, image)
        self._check_methods(parsed, options["details"], image)

        analyzer = FileAnalyzer(options["warn"], options["error"], options["critical"])
        reporter = Reporter(analyzer, target, root, out)
        for line, message in sorted(parsed.parse_errors.items()):
            self._warn(f"cannot parse {reporter.display_path(line)}: {message}")
        reporter.report(parsed, options["min_level"], options["top"], options["details"])
        # The gate uses every file, not only the displayed rows.
        return 2 if self._gate_failed(analyzer, parsed, options["fail_on"]) else 0

    def run(self, args: list[str]) -> None:
        """Entry point for the subcommand."""
        arg_parser = ArgParser(FLAGS, prog=PROG)

        # No arguments → show help and exit
        if len(args) == 0:
            arg_parser.build().print_help()
            sys.exit(0)

        cli = self._parse(arg_parser, args)
        config, config_file = self._load_config(cli["no_config"])
        try:
            options = self._validate(self._merge(cli, config))
            status = self._execute(options, config_file)
        except RubycriticError as exc:
            self._fail(exc.message)
            raise  # unreachable: _fail exits
        if status:
            sys.exit(status)
