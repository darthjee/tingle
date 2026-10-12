"""executor.py — The base class shared by the Docker-backed checks.

`DockerCheck` holds the flow every Docker-backed check follows: parse the
CLI, load and validate its config section, merge the two with the built-in
defaults, validate the options, resolve the target and its mount root, print
the header, select the files and gate the exit status on `--fail-on`. Each
check subclasses it and supplies its own values through class attributes
(`PROG`, `FLAGS`, `CONFIG_SECTION`, `SINGLE_DEFAULTS`, `LIST_KEYS`,
`THRESHOLD_KEYS`, `DEFAULT_EXCLUDES`, `NO_FILES_MESSAGE`, `error_class`) and
hooks (`validate_config`, `_load_section`, `_select_files`, `_gate_value`,
`_execute`).

Display filtering (`--min-level` then `--top`) stays in each check's
reporter.

Dependencies: standard library only.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, ClassVar

from code_check.config import ConfigError, default_path, load_section
from code_check.docker_check.errors import DockerCheckError
from code_check.docker_check.selection import Selection, select_files
from code_check.excludes import parse_excludes, resolve_excludes
from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.palette import Palette
from common.arg_parser import ArgParser


class DockerCheck:
    """Orchestrate the flow: parse → validate → resolve → select → run → report."""

    # Program name shown in the help usage line.
    PROG: ClassVar[str] = ""

    # Flag definitions passed to `ArgParser`.
    FLAGS: ClassVar[list] = []

    # Section of the config file holding this command's options.
    CONFIG_SECTION: ClassVar[str] = ""

    # Built-in defaults for single-value options, applied after the config merge.
    SINGLE_DEFAULTS: ClassVar[dict] = {}

    # Glob-list options merged as config list then CLI list (deduplicated).
    LIST_KEYS: ClassVar[tuple[str, ...]] = ()

    # Threshold options validated as numbers >= 0.
    THRESHOLD_KEYS: ClassVar[tuple[str, ...]] = ()

    # Directory names excluded by default (before `--exclude`).
    DEFAULT_EXCLUDES: ClassVar[list[str]] = []

    # Printed (then exit 0) when no file is left to send to the container.
    NO_FILES_MESSAGE: ClassVar[str] = "No files found for analysis."

    # The error class raised by the check (a `DockerCheckError` subclass).
    error_class: ClassVar[type[DockerCheckError]] = DockerCheckError

    @staticmethod
    def validate_config(section: Any, path: Path) -> dict:
        """Check the config `section` read from `path`; return it or raise `ConfigError`."""
        raise NotImplementedError

    @staticmethod
    def _load_section(name: str, path: Path | None = None) -> dict | None:
        """Read the config section `name` from `path` (hook for the check's own lookup)."""
        return load_section(name, path)

    @staticmethod
    def _select_files(target: Path, root: Path, **kwargs) -> Selection:
        """Select the files to send (hook; checks bind their extensions and skip rules)."""
        return select_files(target, root, **kwargs)

    @staticmethod
    def _gate_value(result: Any) -> float:
        """Return the value a result is classified by for the `--fail-on` gate."""
        raise NotImplementedError

    def _execute(self, options: dict, config_file: Path | None = None) -> int:
        """Run the whole analysis for validated `options`; return the exit status."""
        raise NotImplementedError

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
        """Load and validate the check's config section.

        Returns `(section, path)`; `path` is None when nothing was loaded
        (`--no-config`, missing file or missing section). A `ConfigError`
        prints `Error: <path>: <reason>` and exits with status 1.
        """
        if no_config:
            return {}, None
        path = default_path()
        try:
            section = cls._load_section(cls.CONFIG_SECTION, path)
            if section is None:
                return {}, None
            return cls.validate_config(section, path), path
        except ConfigError as exc:
            cls._fail(str(exc))
            raise  # unreachable: _fail exits

    @classmethod
    def _merge(cls, cli: dict, config: dict) -> dict:
        """Resolve every option from the CLI args and the validated config section.

        Single values: built-in default < config < CLI (a config `null` means
        unset). Lists: config then CLI, concatenated and deduplicated.
        `--no-default-excludes` and `--no-gitignore` only turn behaviour off
        and win over the config.
        """
        merged = {"path": cli["path"]}
        for key, default in cls.SINGLE_DEFAULTS.items():
            if cli.get(key) is not None:
                merged[key] = cli[key]
            else:
                merged[key] = config.get(key, default)
        for key in cls.LIST_KEYS:
            merged[key] = list(dict.fromkeys(config.get(key, []) + (cli.get(key) or [])))
        excludes = config.get("exclude", []) + parse_excludes(cli.get("exclude"))
        merged["exclude"] = list(dict.fromkeys(excludes))
        merged["no_default_excludes"] = bool(cli.get("no_default_excludes")) or config.get(
            "no_default_excludes", False
        )
        merged["gitignore"] = not cli.get("no_gitignore") and config.get("gitignore", True)
        return merged

    @classmethod
    def _validate(cls, options: dict) -> dict:
        """Reject negative (or NaN) thresholds, a negative `--top`/`--details` and an empty `--image`.

        The `--details` check runs only when the check has a `details` option.
        """
        for key in cls.THRESHOLD_KEYS:
            value = options[key]
            if not (value >= 0):  # also rejects NaN
                raise cls.error_class(f"--{key} must be a number >= 0")
        if options["top"] < 0:
            raise cls.error_class("--top must be an integer >= 0")
        if (
            "details" in cls.SINGLE_DEFAULTS
            and options.get("details") is not None
            and options["details"] < 0
        ):
            raise cls.error_class("--details must be an integer >= 0")
        if options["image"] is not None and not options["image"]:
            raise cls.error_class("--image must not be empty")
        return options

    @classmethod
    def _resolve_target(cls, path: str) -> tuple[Path, Path]:
        """Resolve `path` and its mount root (the directory, or a file's parent).

        Raises `error_class` when the path is missing or unreadable, or when
        the mount root holds a `:` (Docker's `-v` cannot express it).
        """
        target = Path(path).resolve()
        if not target.exists():
            raise cls.error_class(f"path not found: {target}")
        is_dir = target.is_dir()
        mode = os.R_OK | os.X_OK if is_dir else os.R_OK
        if not os.access(target, mode):
            raise cls.error_class(f"path not readable: {target}")
        root = target if is_dir else target.parent
        if ":" in str(root):
            raise cls.error_class(
                f"cannot mount {root}: Docker volume paths cannot contain ':'"
            )
        return target, root

    @classmethod
    def _print_header(
        cls, out: Palette, target: Path, options: dict, image: str, config: Path | None = None
    ) -> None:
        """Print the analysis header (target, thresholds, image and loaded config file)."""
        thresholds = " | ".join(
            f"{key}={format(options[key], 'g')}" for key in cls.THRESHOLD_KEYS
        )
        print(f"{out.CYAN}{out.BOLD}Analyzing:{out.RESET} {target}")
        print(f"{out.DIM}Thresholds: {thresholds}{out.RESET}")
        print(f"{out.DIM}Image: {image}{out.RESET}")
        if config is not None:
            print(f"{out.DIM}Config: {config}{out.RESET}")
        print()

    @classmethod
    def _selection_options(cls, options: dict) -> dict:
        """Resolve the merged file-selection options into `select_files` keyword arguments.

        The merged `exclude` names are added to the default excludes (dropped
        when `no_default_excludes` is set), `ignore`/`include` default to no
        globs and `gitignore` defaults to on.
        """
        return {
            "excludes": resolve_excludes(
                cls.DEFAULT_EXCLUDES,
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

        Exits 0 with `NO_FILES_MESSAGE` (before any Docker call) when nothing
        is left to send.
        """
        selection = cls._select_files(target, root, **cls._selection_options(options))
        for message in selection.skipped:
            cls._warn(message)
        if not selection.lines:
            print(f"{out.YELLOW}{cls.NO_FILES_MESSAGE}{out.RESET}")
            sys.exit(0)
        return selection

    @classmethod
    def _gate_failed(
        cls, analyzer: FileAnalyzer, results: Iterable[Any], fail_on: str | None
    ) -> bool:
        """Return True when `--fail-on` is set and any result reaches it."""
        if fail_on is None:
            return False
        return any(analyzer.reaches(cls._gate_value(r), fail_on) for r in results)

    def run(self, args: list[str]) -> None:
        """Entry point for the subcommand."""
        arg_parser = ArgParser(self.FLAGS, prog=self.PROG)

        # No arguments → show help and exit
        if len(args) == 0:
            arg_parser.build().print_help()
            sys.exit(0)

        cli = self._parse(arg_parser, args)
        config, config_file = self._load_config(cli["no_config"])
        try:
            options = self._validate(self._merge(cli, config))
            status = self._execute(options, config_file)
        except DockerCheckError as exc:
            self._fail(exc.message)
            raise  # unreachable: _fail exits
        if status:
            sys.exit(status)
