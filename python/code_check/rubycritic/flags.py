"""flags.py — Command-line flag definitions for code_check rubycritic.

`FLAGS` is consumed by `common.arg_parser.ArgParser` in the executor and by
`code_check.completion`, so it must stay cheap to import: it depends only on
`constants` and `file_size.file_analyzer`.
"""

from __future__ import annotations

from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.rubycritic.constants import Constants

# Flag definitions for ArgParser.
FLAGS: list[dict] = [
    {
        "name": "path",
        "type": str,
        "help": "Ruby file or directory to analyse (recursive)",
    },
    {
        "name": "--warn",
        "type": float,
        "default": None,
        "help": (
            "Warn threshold on the file's total Flog complexity "
            f"(default: {format(Constants.DEFAULT_WARN, 'g')})"
        ),
    },
    {
        "name": "--error",
        "type": float,
        "default": None,
        "help": (
            "Error threshold on the file's total Flog complexity "
            f"(default: {format(Constants.DEFAULT_ERROR, 'g')})"
        ),
    },
    {
        "name": "--critical",
        "type": float,
        "default": None,
        "help": (
            "Critical threshold on the file's total Flog complexity "
            f"(default: {format(Constants.DEFAULT_CRITICAL, 'g')})"
        ),
    },
    {
        "name": "--top",
        "type": int,
        "default": None,
        "help": "Show only the top N most complex files (default: 0 = all)",
    },
    {
        "name": "--min-level",
        "type": str,
        "choices": list(FileAnalyzer.LEVELS),
        "default": None,
        "help": "Show only files at this level or higher (default: ok)",
    },
    {
        "name": "--fail-on",
        "type": str,
        "choices": ["warn", "error", "critical"],
        "default": None,
        "help": "Exit with status 2 if any file reaches this level or higher",
    },
    {
        "name": "--image",
        "type": str,
        "default": None,
        "help": (
            f"Docker image to run (default: {Constants.IMAGE_REPO}:<tingle version>)"
        ),
    },
]
