#!/usr/bin/env python3
"""executor.py — Ruby code complexity via RubyCritic (Docker).

Selects the `.rb` files under `<path>` on the host, runs RubyCritic (Flog,
Flay and Reek) inside the `darthjee/tingle_rubycritic` Docker image and
reports one row per file, classified by thresholds on the file's total Flog
complexity, plus RubyCritic's overall score. The host needs Docker, not Ruby.

File selection follows `file_size`: default and `--exclude` directory names,
`.gitignore` (unless `--no-gitignore`), `--ignore` and `--include` globs and
the fixed `.rb` filter. Symlinks resolving outside the mount root are skipped.

Exit status: 0 on success (also when no `.rb` file is selected), 1 on errors
(bad option, path missing or unreadable, Docker missing or failing, image pull
failure, unparsable output) and 2 when `--fail-on` is set and any file
reaches that level.

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

"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code_check.excludes import parse_excludes, resolve_excludes
from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.palette import Palette
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

# Built-in defaults for single-value options, applied after parsing.
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

    @staticmethod
    def _apply_defaults(cli: dict) -> dict:
        """Fill every unset single-value option with its built-in default."""
        options = dict(cli)
        for key, default in SINGLE_DEFAULTS.items():
            if options.get(key) is None:
                options[key] = default
        return options

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
    def _print_header(out: Palette, target: Path, options: dict, image: str) -> None:
        """Print the analysis header (target, thresholds and image)."""
        thresholds = " | ".join(
            f"{key}={format(options[key], 'g')}" for key in THRESHOLD_KEYS
        )
        print(f"{out.CYAN}{out.BOLD}Analyzing:{out.RESET} {target}")
        print(f"{out.DIM}Thresholds: {thresholds}{out.RESET}")
        print(f"{out.DIM}Image: {image}{out.RESET}")
        print()

    @staticmethod
    def _selection_options(options: dict) -> dict:
        """Resolve the file-selection flags into `select_files` keyword arguments.

        `--exclude` names are added to the default excludes (dropped with
        `--no-default-excludes`), `--ignore`/`--include` default to no globs and
        `.gitignore` is on unless `--no-gitignore` is given.
        """
        return {
            "excludes": resolve_excludes(
                Constants.DEFAULT_EXCLUDES,
                parse_excludes(options.get("exclude")),
                bool(options.get("no_default_excludes")),
            ),
            "ignore": options.get("ignore") or [],
            "include": options.get("include") or [],
            "gitignore": not options.get("no_gitignore"),
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

    def _execute(self, options: dict) -> int:
        """Run the whole analysis for validated `options`; return the exit status.

        Every failure raises `RubycriticError`.
        """
        target, root = self._resolve_target(options["path"])
        image = resolve_image(options["image"])
        out = Palette(sys.stdout)
        self._print_header(out, target, options, image)
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
        try:
            status = self._execute(self._validate(self._apply_defaults(cli)))
        except RubycriticError as exc:
            self._fail(exc.message)
            raise  # unreachable: _fail exits
        if status:
            sys.exit(status)
