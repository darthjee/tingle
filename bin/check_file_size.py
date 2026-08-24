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


from __future__ import annotations    # ← adicionar esta linha

import argparse
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────
# 1. Constants
# ──────────────────────────────────────────────────────────────────────
class Constants:
    """Immutable configuration: colors, exclusions, binary extensions."""

    # ANSI color codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

    # Default directories to exclude
    DEFAULT_EXCLUDES = [
        "node_modules", "dist", "build", ".git", "vendor",
        "third_party", ".next", "__pycache__", ".cache",
        "coverage", ".nuxt", "out", "target",
    ]

    # Binary file extensions — skipped automatically
    BINARY_EXTENSIONS = {
        # Images
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg",
        ".tiff", ".tif", ".raw", ".heic", ".avif",
        # Videos
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv",
        # Audio
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
        # Binary documents
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        # Archives
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
        # Executables and libraries
        ".exe", ".dll", ".so", ".dylib", ".bin", ".o", ".class", ".jar",
        ".war", ".pyc", ".pyo", ".wasm",
        # Binary fonts
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        # Databases
        ".db", ".sqlite", ".sqlite3", ".mdb",
        # Other
        ".dat", ".pak", ".bundle", ".min.js", ".min.css",
        ".lock", ".map",
    }

    # Default thresholds (in lines)
    DEFAULT_WARN = 300
    DEFAULT_ERROR = 500
    DEFAULT_CRITICAL = 1000

# ──────────────────────────────────────────────────────────────────────
# 2. SkipChecks
# ──────────────────────────────────────────────────────────────────────
class SkipChecks:
    """Determine whether a file should be skipped from analysis."""

    @staticmethod
    def is_binary_file(path: Path) -> bool:
        """Check if a file is binary by extension or content."""
        # 1. Known binary extension
        if path.suffix.lower() in Constants.BINARY_EXTENSIONS:
            return True

        # 2. Content-based detection — read first 1024 bytes
        try:
            with open(path, "rb") as f:
                chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
            try:
                chunk.decode("utf-8")
            except UnicodeDecodeError:
                return True
        except (OSError, PermissionError):
            return True

        return False

# ──────────────────────────────────────────────────────────────────────
# 3. FileCollector
# ──────────────────────────────────────────────────────────────────────
class FileCollector:
    """Walk paths recursively, applying exclusions and filters."""

    def __init__(self, excludes: list[str], extensions: list[str] | None):
        self._exclude_set = {e.lower() for e in excludes}
        self._ext_set = {e.lower() for e in extensions} if extensions else None

    def collect(self, target: Path) -> list[Path]:
        """Collect all analyzable files from a file or directory path."""
        if target.is_file():
            if not SkipChecks.is_binary_file(target):
                return [target]
            return []

        if not target.is_dir():
            return []

        files = []
        for path in target.rglob("*"):
            if not path.is_file():
                continue
            if self._is_excluded(path):
                continue
            if self._ext_set and path.suffix.lower() not in self._ext_set:
                continue
            if SkipChecks.is_binary_file(path):
                continue
            files.append(path)

        return files

    def _is_excluded(self, path: Path) -> bool:
        """Check if any path component matches an exclusion entry."""
        return any(
            part.lower() in self._exclude_set
            for part in path.parts
        )

# ──────────────────────────────────────────────────────────────────────
# 4. FileAnalyzer
# ──────────────────────────────────────────────────────────────────────
class FileAnalyzer:
    """Count lines and classify files by threshold."""

    def __init__(self, warn: int, error: int, critical: int):
        self._warn = warn
        self._error = error
        self._critical = critical

    @staticmethod
    def count_lines(path: Path) -> int:
        """Count the number of lines in a text file. Returns -1 on error."""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return sum(1 for _ in f)
        except (OSError, PermissionError):
            return -1

    def classify(self, lines: int) -> tuple[str, str]:
        """Return (label, color) based on line count and thresholds."""
        if lines >= self._critical:
            return ("🟣 CRITICAL", Constants.MAGENTA + Constants.BOLD)
        elif lines >= self._error:
            return ("🔴 ERROR", Constants.RED + Constants.BOLD)
        elif lines >= self._warn:
            return ("⚠️  WARN", Constants.YELLOW)
        else:
            return ("✅ OK", Constants.GREEN)

    @staticmethod
    def format_number(n: int) -> str:
        """Format number with thousands separator."""
        return f"{n:,}".replace(",", ".")

# ──────────────────────────────────────────────────────────────────────
# 5. ArgParser
# ──────────────────────────────────────────────────────────────────────
class ArgParser:
    """Build and parse command-line arguments."""

    @staticmethod
    def build() -> argparse.ArgumentParser:
        """Build and return the configured argument parser."""
        parser = argparse.ArgumentParser(
            description="Token efficiency triage: file size analysis.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__doc__,
        )
        parser.add_argument(
            "path",
            type=str,
            help="File or directory to analyze (recursive)",
        )
        parser.add_argument(
            "--warn",
            type=int,
            default=Constants.DEFAULT_WARN,
            help=f"Yellow threshold in lines (default: {Constants.DEFAULT_WARN})",
        )
        parser.add_argument(
            "--error",
            type=int,
            default=Constants.DEFAULT_ERROR,
            help=f"Red threshold in lines (default: {Constants.DEFAULT_ERROR})",
        )
        parser.add_argument(
            "--critical",
            type=int,
            default=Constants.DEFAULT_CRITICAL,
            help=f"Critical threshold in lines (default: {Constants.DEFAULT_CRITICAL})",
        )
        parser.add_argument(
            "--top",
            type=int,
            default=0,
            help="Show only top N largest files (0 = all)",
        )
        parser.add_argument(
            "--exclude",
            type=str,
            default=",".join(Constants.DEFAULT_EXCLUDES),
            help=(
                "Directories to ignore (comma-separated). "
                f"Default: {','.join(Constants.DEFAULT_EXCLUDES)}"
            ),
        )
        parser.add_argument(
            "--ext",
            type=str,
            action="append",
            default=None,
            help="Filter by extension (can be repeated). Ex: --ext .py --ext .js",
        )
        return parser

# ──────────────────────────────────────────────────────────────────────
# 6. Main
# ──────────────────────────────────────────────────────────────────────
class Main:
    """Orchestrate the analysis flow: parse → collect → analyze → report."""

    @staticmethod
    def run():
        """Entry point for the script."""
        # No arguments → show help and exit
        if len(sys.argv) == 1:
            ArgParser.build().print_help()
            sys.exit(0)

        args = ArgParser.build().parse_args()
        target = Path(args.path).resolve()

        if not target.exists():
            print(f"{Constants.RED}Error: path not found: {target}{Constants.RESET}")
            sys.exit(1)

        excludes = [e.strip() for e in args.exclude.split(",") if e.strip()]

        # Header
        print(f"{Constants.CYAN}{Constants.BOLD}Analyzing:{Constants.RESET} {target}")
        print(
            f"{Constants.DIM}Thresholds: warn={args.warn} | error={args.error} | "
            f"critical={args.critical}{Constants.RESET}"
        )
        print()

        # Collect files
        collector = FileCollector(excludes, args.ext)
        files = collector.collect(target)

        if not files:
            print(f"{Constants.YELLOW}No files found for analysis.{Constants.RESET}")
            sys.exit(0)

        # Analyze
        analyzer = FileAnalyzer(args.warn, args.error, args.critical)
        results = []
        for f in files:
            lines = analyzer.count_lines(f)
            if lines >= 0:
                results.append((f, lines))

        # Sort by line count (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        # Apply --top if provided
        if args.top > 0:
            results = results[:args.top]

        # Table header
        print(f"{'Status':<16} {'Lines':>10}  {'File'}")
        print(f"{'─' * 16} {'─' * 10}  {'─' * 50}")

        counts = {"OK": 0, "WARN": 0, "ERROR": 0, "CRITICAL": 0}
        total_lines = 0

        for path, lines in results:
            label, color = analyzer.classify(lines)
            try:
                display_path = str(
                    path.relative_to(target.parent)
                ) if target.is_dir() else path.name
            except ValueError:
                display_path = str(path)

            print(f"{color}{label:<16}{Constants.RESET} {analyzer.format_number(lines):>10}  {display_path}")

            total_lines += lines
            if "OK" in label:
                counts["OK"] += 1
            elif "WARN" in label:
                counts["WARN"] += 1
            elif "ERROR" in label:
                counts["ERROR"] += 1
            elif "CRITICAL" in label:
                counts["CRITICAL"] += 1

        # Summary
        print()
        print(f"{Constants.GRAY}{'─' * 78}{Constants.RESET}")
        print(
            f"{Constants.BOLD}Summary:{Constants.RESET} "
            f"{len(results)} file(s) | "
            f"{Constants.GREEN}{counts['OK']} OK{Constants.RESET} | "
            f"{Constants.YELLOW}{counts['WARN']} WARN{Constants.RESET} | "
            f"{Constants.RED}{counts['ERROR']} ERROR{Constants.RESET} | "
            f"{Constants.MAGENTA}{counts['CRITICAL']} CRITICAL{Constants.RESET}"
        )
        print(f"{Constants.BOLD}Total:{Constants.RESET} {analyzer.format_number(total_lines)} lines")

if __name__ == "__main__":
    Main.run()