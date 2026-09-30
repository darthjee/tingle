#!/usr/bin/env python3
"""executor.py — Token efficiency triage: file size analysis.

Analyzes source files and lists them by size (line count), classifying
them by configurable thresholds. Useful for identifying token consumption
bottlenecks before feeding a repository to an AI.

With `--fail-on warn|error|critical` it acts as a CI gate: exit status is 0
on success, 1 on errors (path not found, bad option) and 2 when any analysed
file reaches the given level.

When `<path>` is inside a git work tree, untracked files ignored by git
(`.gitignore`, `.git/info/exclude`, global excludes) are skipped by default;
tracked files are always analysed. `--no-gitignore` turns this off.

Personal defaults are read from the `check_file_size` section of
`~/.tingle/code_check/config.json` (keys: warn, error, critical, top, exclude,
ignore, include, ext, no_default_excludes, gitignore, fail_on, min_level).
Single values given on the CLI win over the config; list values (exclude,
ignore, include, ext) are concatenated, config first. An invalid config exits
with status 1. `--no-config` skips the file entirely.

Example config:
    {"check_file_size": {"warn": 250, "ignore": ["*.lock"], "fail_on": "error"}}

Usage:
    tingle code_check file_size <path> [options]

Examples
--------
    tingle code_check file_size ./src
    tingle code_check file_size ./src --warn 300 --error 500 --critical 1000
    tingle code_check file_size ./src --top 20
    tingle code_check file_size ./src --min-level warn
    tingle code_check file_size ./src --min-level error --top 5
    tingle code_check file_size ./src --exclude fixtures
    tingle code_check file_size ./src --no-default-excludes --exclude fixtures
    tingle code_check file_size . --no-gitignore
    tingle code_check file_size ./src --ext .py --ext .js
    tingle code_check file_size . --ignore '*.test.js' --ignore 'docs/**'
    tingle code_check file_size . --include 'src/**' --ext .py
    tingle code_check file_size ./src --fail-on error
    tingle code_check file_size ./src --no-config

"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code_check.config import default_path, load_section
from code_check.file_size.config import ConfigError, validate
from code_check.file_size.constants import Constants
from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.file_size.file_collector import FileCollector
from code_check.file_size.flags import FLAGS
from code_check.file_size.reporter import Reporter
from code_check.palette import Palette
from common.arg_parser import ArgParser

# Section of the config file holding this command's options.
CONFIG_SECTION = "check_file_size"

# Built-in defaults for single-value options, applied after the config merge.
SINGLE_DEFAULTS: dict = {
    "warn": Constants.DEFAULT_WARN,
    "error": Constants.DEFAULT_ERROR,
    "critical": Constants.DEFAULT_CRITICAL,
    "top": 0,
    "fail_on": None,
    "min_level": "ok",
}

# Options whose config list and CLI list are concatenated.
LIST_KEYS = ("ignore", "include", "ext")


class CheckFileSize:
    """Orchestrate the analysis flow: parse → collect → analyze → report."""

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

    @classmethod
    def _resolve_target(cls, path: str) -> Path:
        """Resolve `path`, exiting with status 1 when it does not exist."""
        target = Path(path).resolve()
        if not target.exists():
            cls._fail(f"path not found: {target}")
        return target

    @classmethod
    def _load_config(cls, no_config: bool) -> tuple[dict, Path | None]:
        """Load and validate the config section.

        Returns `(section, path)`; `path` is None when nothing was loaded
        (`--no-config`, missing file or missing section). A `ConfigError`
        exits with status 1.
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
    def _parse_excludes(raw: str) -> list[str]:
        """Split a comma-separated exclude list, dropping blank entries."""
        return [e.strip() for e in raw.split(",") if e.strip()]

    @staticmethod
    def _resolve_excludes(extra: list[str], no_default_excludes: bool) -> list[str]:
        """Merge the default excludes with the `extra` names, deduplicated.

        The defaults are dropped when `no_default_excludes` is set.
        """
        base = [] if no_default_excludes else list(Constants.DEFAULT_EXCLUDES)
        return list(dict.fromkeys(base + extra))

    @classmethod
    def _merge(cls, cli: dict, config: dict) -> dict:
        """Resolve every option from the CLI args and the validated config section.

        Single values: built-in default < config < CLI. Lists: config then CLI,
        concatenated and deduplicated. `--no-default-excludes` and
        `--no-gitignore` only turn behaviour off and win over the config.
        """
        merged = {"path": cli["path"]}
        for key, default in SINGLE_DEFAULTS.items():
            if cli[key] is not None:
                merged[key] = cli[key]
            else:
                merged[key] = config.get(key, default)
        for key in LIST_KEYS:
            merged[key] = list(dict.fromkeys(config.get(key, []) + (cli[key] or [])))
        excludes = config.get("exclude", []) + cls._parse_excludes(cli["exclude"] or "")
        merged["exclude"] = list(dict.fromkeys(excludes))
        merged["no_default_excludes"] = cli["no_default_excludes"] or config.get(
            "no_default_excludes", False
        )
        merged["gitignore"] = not cli["no_gitignore"] and config.get("gitignore", True)
        return merged

    @staticmethod
    def _print_header(
        out: Palette, target: Path, args: dict, config: Path | None = None
    ) -> None:
        """Print the analysis header (target, thresholds and loaded config file)."""
        print(f"{out.CYAN}{out.BOLD}Analyzing:{out.RESET} {target}")
        print(
            f"{out.DIM}Thresholds: warn={args['warn']} | error={args['error']} | "
            f"critical={args['critical']}{out.RESET}"
        )
        if config is not None:
            print(f"{out.DIM}Config: {config}{out.RESET}")
        print()

    @staticmethod
    def _analyze(analyzer: FileAnalyzer, files) -> list[tuple[Path, int]]:
        """Count lines per file, drop unreadable ones and sort descending."""
        counted = ((f, analyzer.count_lines(f)) for f in files)
        results = [(f, lines) for f, lines in counted if lines >= 0]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def _gate_failed(analyzer: FileAnalyzer, results, fail_on: str | None) -> bool:
        """Return True when `--fail-on` is set and any result reaches it."""
        if fail_on is None:
            return False
        return any(analyzer.reaches(lines, fail_on) for _path, lines in results)

    @staticmethod
    def _select_shown(analyzer: FileAnalyzer, results, min_level: str, top: int):
        """Return the rows to display: filter by `--min-level`, then cut by `--top`."""
        shown = [r for r in results if analyzer.reaches(r[1], min_level)]
        if top > 0:
            shown = shown[:top]
        return shown

    def run(self, args: list[str]):
        """Entry point for the script."""
        arg_parser = ArgParser(FLAGS)

        # No arguments → show help and exit
        if len(args) == 0:
            arg_parser.build().print_help()
            sys.exit(0)

        cli = self._parse(arg_parser, args)
        config, config_file = self._load_config(cli["no_config"])
        args = self._merge(cli, config)
        min_level = args["min_level"]
        target = self._resolve_target(args["path"])

        out = Palette(sys.stdout)
        self._print_header(out, target, args, config_file)

        collector = FileCollector(
            self._resolve_excludes(args["exclude"], args["no_default_excludes"]),
            args["ext"],
            ignore=args["ignore"],
            include=args["include"],
            gitignore=args["gitignore"],
        )
        files = collector.collect(target)

        if not files:
            print(f"{out.YELLOW}No files found for analysis.{out.RESET}")
            sys.exit(0)

        analyzer = FileAnalyzer(args["warn"], args["error"], args["critical"])
        results = self._analyze(analyzer, files)

        # The --fail-on gate and the summary use every analysed file;
        # --min-level and --top only decide which rows are displayed.
        gate_failed = self._gate_failed(analyzer, results, args["fail_on"])
        shown = self._select_shown(analyzer, results, min_level, args["top"])

        Reporter(analyzer, target, out).report(results, shown, min_level)

        if gate_failed:
            sys.exit(2)
