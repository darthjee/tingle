#!/usr/bin/env python3
"""
check_file_size.py — Token efficiency triage: file size analysis.

Analyzes source files and lists them by size (line count), classifying
them by configurable thresholds. Useful for identifying token consumption
bottlenecks before feeding a repository to an AI.

Usage:
    ./check_file_size.py <path> [options]

Examples:
    ./check_file_size.py ./src
    ./check_file_size.py ./src --warn 300 --error 500 --critical 1000
    ./check_file_size.py ./src --top 20
    ./check_file_size.py ./src --exclude node_modules,dist,build
    ./check_file_size.py ./src --ext .py --ext .js
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from check_file_size.constants import Constants  # noqa: E402
from check_file_size.file_analyzer import FileAnalyzer  # noqa: E402
from check_file_size.file_collector import FileCollector  # noqa: E402
from check_file_size.reporter import Reporter  # noqa: E402
from common.arg_parser import ArgParser  # noqa: E402


class CheckFileSize:
    """Orchestrate the analysis flow: parse → collect → analyze → report."""

    @staticmethod
    def _flags() -> list[dict]:
        """Build the flag definitions for ArgParser."""
        return [
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
        ]

    def run(self):
        """Entry point for the script."""
        arg_parser = ArgParser(self._flags())

        # No arguments → show help and exit
        if len(sys.argv) == 1:
            arg_parser.build().print_help()
            sys.exit(0)

        args = arg_parser.parse()
        target = Path(args["path"]).resolve()

        if not target.exists():
            print(f"{Constants.RED}Error: path not found: {target}{Constants.RESET}")
            sys.exit(1)

        excludes = [e.strip() for e in args["exclude"].split(",") if e.strip()]

        # Header
        print(f"{Constants.CYAN}{Constants.BOLD}Analyzing:{Constants.RESET} {target}")
        print(
            f"{Constants.DIM}Thresholds: warn={args['warn']} | error={args['error']} | "
            f"critical={args['critical']}{Constants.RESET}"
        )
        print()

        # Collect files
        collector = FileCollector(excludes, args["ext"])
        files = collector.collect(target)

        if not files:
            print(f"{Constants.YELLOW}No files found for analysis.{Constants.RESET}")
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

        # Apply --top if provided
        if args["top"] > 0:
            results = results[:args["top"]]

        Reporter(analyzer, target).report(results)


if __name__ == "__main__":
    CheckFileSize().run()
