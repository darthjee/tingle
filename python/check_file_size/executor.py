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

    def run(self, args: list[str]):
        """Entry point for the script."""
        arg_parser = ArgParser(FLAGS)

        # No arguments → show help and exit
        if len(args) == 0:
            arg_parser.build().print_help()
            sys.exit(0)

        args = self._parse(arg_parser, args)
        target = Path(args["path"]).resolve()

        if not target.exists():
            err = Palette(sys.stderr)
            print(f"{err.RED}Error: path not found: {target}{err.RESET}", file=sys.stderr)
            sys.exit(1)

        out = Palette(sys.stdout)

        excludes = [e.strip() for e in args["exclude"].split(",") if e.strip()]

        # Header
        print(f"{out.CYAN}{out.BOLD}Analyzing:{out.RESET} {target}")
        print(
            f"{out.DIM}Thresholds: warn={args['warn']} | error={args['error']} | "
            f"critical={args['critical']}{out.RESET}"
        )
        print()

        # Collect files
        collector = FileCollector(excludes, args["ext"])
        files = collector.collect(target)

        if not files:
            print(f"{out.YELLOW}No files found for analysis.{out.RESET}")
            sys.exit(0)

        # Analyze
        analyzer = FileAnalyzer(args["warn"], args["error"], args["critical"])
        results = []
        for f in files:
            lines = analyzer.count_lines(f)
            if lines >= 0:
                results.append((f, lines))

        # Sort by line count (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        # Evaluate the --fail-on gate on every analysed file (before --top)
        fail_on = args["fail_on"]
        gate_failed = fail_on is not None and any(
            analyzer.reaches(lines, fail_on) for _path, lines in results
        )

        # Apply --top if provided
        if args["top"] > 0:
            results = results[:args["top"]]

        Reporter(analyzer, target, out).report(results)

        if gate_failed:
            sys.exit(2)
