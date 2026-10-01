#!/usr/bin/env python3
"""executor.py — Ruby code complexity via RubyCritic (Docker).

Selects the `.rb` files under `<path>` on the host, runs RubyCritic (Flog,
Flay and Reek) inside the `darthjee/tingle_rubycritic` Docker image and
reports one row per file, classified by thresholds on the file's total Flog
complexity, plus RubyCritic's overall score. The host needs Docker, not Ruby.

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
    tingle code_check rubycritic ./app --image tingle_rubycritic:dev

"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code_check.palette import Palette
from code_check.rubycritic.constants import Constants
from code_check.rubycritic.docker_runner import DockerRunner
from code_check.rubycritic.errors import RubycriticError
from code_check.rubycritic.flags import FLAGS
from code_check.rubycritic.image import resolve_image
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
        """Reject negative (or NaN) thresholds, a negative `--top` and an empty `--image`."""
        for key in THRESHOLD_KEYS:
            value = options[key]
            if not (value >= 0):  # also rejects NaN
                raise RubycriticError(f"--{key} must be a number >= 0")
        if options["top"] < 0:
            raise RubycriticError("--top must be an integer >= 0")
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

    @classmethod
    def _select(cls, out: Palette, target: Path, root: Path) -> Selection:
        """Select the files, warning about unsendable names.

        Exits 0 with `No Ruby files found for analysis.` (before any Docker
        call) when nothing is left to send.
        """
        selection = select_files(target, root)
        for message in selection.skipped:
            cls._warn(message)
        if not selection.lines:
            print(f"{out.YELLOW}No Ruby files found for analysis.{out.RESET}")
            sys.exit(0)
        return selection

    def run(self, args: list[str]) -> None:
        """Entry point for the subcommand."""
        arg_parser = ArgParser(FLAGS, prog=PROG)

        # No arguments → show help and exit
        if len(args) == 0:
            arg_parser.build().print_help()
            sys.exit(0)

        cli = self._parse(arg_parser, args)
        try:
            options = self._validate(self._apply_defaults(cli))
            target, root = self._resolve_target(options["path"])
            image = resolve_image(options["image"])
            out = Palette(sys.stdout)
            self._print_header(out, target, options, image)
            selection = self._select(out, target, root)
            runner = DockerRunner(image)
            runner.preflight()
            runner.ensure_image()
            proc = runner.run(root, selection.lines)
            runner.check_outcome(proc, root)
        except RubycriticError as exc:
            self._fail(exc.message)
