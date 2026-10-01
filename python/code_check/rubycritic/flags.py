"""flags.py — Command-line flag definitions for code_check rubycritic.

`FLAGS` is consumed by `common.arg_parser.ArgParser` in the executor and by
`code_check.completion`, so it must stay cheap to import: it depends only on
`constants` and `file_size.file_analyzer`.

The file-selection flags (`--exclude`, `--no-default-excludes`,
`--no-gitignore`, `--ignore`, `--include`) mirror `file_size`'s; the `.rb`
filter is fixed, so there is no `--ext`. Their parsing lives in
`code_check.excludes` and `rubycritic.selection`, never here.
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
        "name": "--details",
        "type": int,
        "nargs": "?",
        "const": Constants.DEFAULT_DETAILS,
        "default": None,
        "help": (
            "Show the N most complex methods under each file "
            f"(default when given without N: {Constants.DEFAULT_DETAILS}; 0 = all)"
        ),
    },
    {
        "name": "--image",
        "type": str,
        "default": None,
        "help": (
            f"Docker image to run (default: {Constants.IMAGE_REPO}:<tingle version>)"
        ),
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
            "Only analyse .rb files whose path relative to <path> matches this glob "
            "(can be repeated)"
        ),
    },
]
