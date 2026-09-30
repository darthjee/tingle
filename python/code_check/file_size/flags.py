"""flags.py — Command-line flag definitions for code_check file_size.

`FLAGS` is consumed by `common.arg_parser.ArgParser` in the executor and by
`code_check.completion`, so it must stay cheap to import: it depends only on
`constants` and `file_analyzer`.
"""

from __future__ import annotations

from code_check.file_size.constants import Constants
from code_check.file_size.file_analyzer import FileAnalyzer

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
        "default": None,
        "help": f"Yellow threshold in lines (default: {Constants.DEFAULT_WARN})",
    },
    {
        "name": "--error",
        "type": int,
        "default": None,
        "help": f"Red threshold in lines (default: {Constants.DEFAULT_ERROR})",
    },
    {
        "name": "--critical",
        "type": int,
        "default": None,
        "help": f"Critical threshold in lines (default: {Constants.DEFAULT_CRITICAL})",
    },
    {
        "name": "--top",
        "type": int,
        "default": None,
        "help": "Show only top N largest files (default: 0 = all)",
    },
    {
        "name": "--min-level",
        "type": str,
        "choices": list(FileAnalyzer.LEVELS),
        "default": None,
        "help": "Show only files at this level or higher (default: ok)",
    },
    {
        "name": "--exclude",
        "type": str,
        "default": None,
        "help": (
            "Extra directory names to skip (comma-separated), added to the "
            f"defaults: {','.join(Constants.DEFAULT_EXCLUDES)}"
        ),
    },
    {
        "name": "--no-default-excludes",
        "action": "store_true",
        "help": "Do not skip the default directories; only --exclude names apply",
    },
    {
        "name": "--no-gitignore",
        "action": "store_true",
        "help": "Do not skip files ignored by git (.gitignore, .git/info/exclude, global excludes)",
    },
    {
        "name": "--ignore",
        "type": str,
        "action": "append",
        "default": None,
        "help": "Skip files whose path relative to <path> matches this glob (can be repeated)",
    },
    {
        "name": "--include",
        "type": str,
        "action": "append",
        "default": None,
        "help": (
            "Only analyse files whose path relative to <path> matches this glob "
            "(can be repeated)"
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
    {
        "name": "--no-config",
        "action": "store_true",
        "help": "Do not read ~/.tingle/code_check/config.json",
    },
]
