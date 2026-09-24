#!/usr/bin/env python3
"""
executor.py — Token efficiency triage: file size analysis.

Analyzes source files and lists them by size (line count), classifying
them by configurable thresholds. Useful for identifying token consumption
bottlenecks before feeding a repository to an AI.

With `--fail-on warn|error|critical` it acts as a CI gate: exit status is 0
on success, 1 on errors (path not found, bad option) and 2 when any analysed
file reaches the given level.

Usage:
    ./check_file_size.py <path> [options]

Examples
--------
    ./check_file_size.py ./src
    ./check_file_size.py ./src --warn 300 --error 500 --critical 1000
    ./check_file_size.py ./src --top 20
    ./check_file_size.py ./src --exclude node_modules,dist,build
    ./check_file_size.py ./src --ext .py --ext .js
    ./check_file_size.py ./src --fail-on error

"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from check_file_size.constants import Constants
from check_file_size.file_analyzer import FileAnalyzer
from check_file_size.file_collector import FileCollector
from check_file_size.palette import Palette
from check_file_size.reporter import Reporter
from common.arg_parser import ArgParser

# Flag definitions for ArgParser.
FLAGS: list[dict] = [
    {
        "name": "path",
        "type": str,
        "help": "File or directory to analyze (recursive)",
    },
    {
        "name": "--warn",
        "type": int,
        "default": Constants.DEFAULT_WARN,
        "help": f"Yellow threshold in lines (default: {Constants.DEFAULT_WARN})",
    },
    {
        "name": "--error",
        "type": int,
        "default": Constants.DEFAULT_ERROR,
        "help": f"Red threshold in lines (default: {Constants.DEFAULT_ERROR})",
    },
    {
        "name": "--critical",
        "type": int,
        "default": Constants.DEFAULT_CRITICAL,
        "help": f"Critical threshold in lines (default: {Constants.DEFAULT_CRITICAL})",
    },
    {
        "name": "--top",
        "type": int,
        "default": 0,
        "help": "Show only top N largest files (0 = all)",
    },
    {
        "name": "--exclude",
        "type": str,
        "default": ",".join(Constants.DEFAULT_EXCLUDES),
        "help": (
            "Directories to ignore (comma-separated). "
            f"Default: {','.join(Constants.DEFAULT_EXCLUDES)}"
        ),
    },
    {
        "name": "--ext",
        "type": str,
        "action": "append",
        "default": None,
        "help": "Filter by extension (can be repeated). Ex: --ext .py --ext .js",
    },
    {
        "name": "--fail-on",
        "type": str,
        "choices": ["warn", "error", "critical"],
        "default": None,
        "help": "Exit with status 2 if any file reaches this level or higher",
    },
]


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
    def _resolve_target(path: str) -> Path:
        """Resolve `path`, exiting with status 1 when it does not exist."""
        target = Path(path).resolve()
        if not target.exists():
            err = Palette(sys.stderr)
            print(f"{err.RED}Error: path not found: {target}{err.RESET}", file=sys.stderr)
            sys.exit(1)
        return target

    @staticmethod
    def _parse_excludes(raw: str) -> list[str]:
        """Split a comma-separated exclude list, dropping blank entries."""
        return [e.strip() for e in raw.split(",") if e.strip()]

    @staticmethod
    def _print_header(out: Palette, target: Path, args: dict) -> None:
        """Print the analysis header (target and thresholds)."""
        print(f"{out.CYAN}{out.BOLD}Analyzing:{out.RESET} {target}")
        print(
            f"{out.DIM}Thresholds: warn={args['warn']} | error={args['error']} | "
            f"critical={args['critical']}{out.RESET}"
        )
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

    def run(self, args: list[str]):
        """Entry point for the script."""
        arg_parser = ArgParser(FLAGS)

        # No arguments → show help and exit
        if len(args) == 0:
            arg_parser.build().print_help()
            sys.exit(0)

        args = self._parse(arg_parser, args)
        target = self._resolve_target(args["path"])

        out = Palette(sys.stdout)
        self._print_header(out, target, args)

        collector = FileCollector(self._parse_excludes(args["exclude"]), args["ext"])
        files = collector.collect(target)

        if not files:
            print(f"{out.YELLOW}No files found for analysis.{out.RESET}")
            sys.exit(0)

        analyzer = FileAnalyzer(args["warn"], args["error"], args["critical"])
        results = self._analyze(analyzer, files)

        # Evaluate the --fail-on gate on every analysed file (before --top)
        gate_failed = self._gate_failed(analyzer, results, args["fail_on"])

        if args["top"] > 0:
            results = results[:args["top"]]

        Reporter(analyzer, target, out).report(results)

        if gate_failed:
            sys.exit(2)
