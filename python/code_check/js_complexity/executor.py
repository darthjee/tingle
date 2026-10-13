#!/usr/bin/env python3
"""executor.py — JavaScript/TypeScript code complexity via FTA (Docker).

Selects the JavaScript/TypeScript files under `<path>` on the host, runs FTA
inside the `darthjee/tingle_js_complexity` Docker image and reports one row
per file, classified by thresholds on the file's FTA score rounded to one
decimal. `Cyclo`, `Lines` and `Assessment` are information only. The host
needs Docker, not Node.js.

File selection follows `file_size`, applied in this order: default and
`--exclude` directory names (`--no-default-excludes` drops the defaults),
`.gitignore` (unless `--no-gitignore`), `--ignore` globs, then `--include`
globs together with the fixed core extensions (`.js .mjs .cjs .jsx .ts .mts
.cts .tsx`, case-insensitive), then the declaration files (`.d.ts`,
`.d.mts`, `.d.cts`). Symlinks resolving outside the mount root are skipped.
For a single-file `<path>` the directory excludes don't apply and the globs
match the file name. There is no config file yet.

Exit status: 0 on success (also when no file is selected), 1 on errors (bad
option, path missing or unreadable, Docker missing or failing, image pull
failure, container failure, unparsable output) and 2 when `--fail-on` is set
and any file reaches that level.

Dependencies: standard library only; Docker on the host at run time.

Usage:
    tingle code_check js_complexity <path> [options]

Examples
--------
    tingle code_check js_complexity ./src
    tingle code_check js_complexity ./src --warn 40 --error 55 --critical 70
    tingle code_check js_complexity ./src --top 10 --min-level warn
    tingle code_check js_complexity ./src --fail-on error
    tingle code_check js_complexity ./src --image tingle_js_complexity:dev
    tingle code_check js_complexity ./src --exclude test,fixtures
    tingle code_check js_complexity ./src --no-default-excludes --exclude vendor
    tingle code_check js_complexity ./src --ignore '**/*.test.ts'
    tingle code_check js_complexity ./src --include 'src/**'
    tingle code_check js_complexity ./src --no-gitignore

"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code_check.docker_check.executor import DockerCheck
from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.js_complexity.constants import Constants
from code_check.js_complexity.docker_runner import DockerRunner, decode, write_stderr
from code_check.js_complexity.errors import JsComplexityError
from code_check.js_complexity.flags import FLAGS
from code_check.js_complexity.image import resolve_image
from code_check.js_complexity.output_parser import (
    FileResult,
    OutputFormatError,
    ParsedOutput,
    parse,
)
from code_check.js_complexity.reporter import Reporter
from code_check.js_complexity.selection import Selection, select_files
from code_check.palette import Palette
from common.arg_parser import ArgParser

# Program name shown in the help usage line.
PROG = "tingle code_check js_complexity"

# Section of the config file holding this command's options (read from #322).
CONFIG_SECTION = "js_complexity"

# Built-in defaults for single-value options.
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


class CheckJsComplexity(DockerCheck):
    """Orchestrate the flow: parse → validate → resolve → select → run → report."""

    PROG = PROG
    FLAGS = FLAGS
    CONFIG_SECTION = CONFIG_SECTION
    SINGLE_DEFAULTS = SINGLE_DEFAULTS
    LIST_KEYS = ("ignore", "include")
    THRESHOLD_KEYS = THRESHOLD_KEYS
    DEFAULT_EXCLUDES = Constants.DEFAULT_EXCLUDES
    NO_FILES_MESSAGE = "No JavaScript/TypeScript files found for analysis."
    error_class = JsComplexityError

    @staticmethod
    def _parse(arg_parser: ArgParser, args: list[str]) -> dict:
        """Parse args like the base class, adding `no_config` (read by `DockerCheck.run`).

        There is no `--no-config` flag yet; #322 adds it and removes this override.
        """
        cli = DockerCheck._parse(arg_parser, args)
        cli.setdefault("no_config", False)
        return cli

    @classmethod
    def _load_config(cls, no_config: bool) -> tuple[dict, Path | None]:
        """Return no config: the file is never read.

        There is no `--no-config` flag and no `js_complexity` config section
        yet; #322 replaces this override.
        """
        return {}, None

    @staticmethod
    def _select_files(target: Path, root: Path, **kwargs) -> Selection:
        """Select the JS/TS files through this module's `select_files`."""
        return select_files(target, root, **kwargs)

    @staticmethod
    def _gate_value(result: FileResult) -> float:
        """Classify a file for the `--fail-on` gate by its rounded FTA score."""
        return result.score

    @staticmethod
    def _parse_output(proc, lines: list[str], image: str) -> ParsedOutput:
        """Parse the container stdout; on a contract break pass its stderr through and fail."""
        try:
            return parse(decode(proc.stdout), lines)
        except OutputFormatError as exc:
            write_stderr(proc)
            raise JsComplexityError(
                f"could not parse the output of {image}: {exc.reason}"
            ) from exc

    @classmethod
    def _print_warnings(cls, parsed: ParsedOutput, reporter: Reporter) -> None:
        """Warn about the refused lines (warnings order), then the unparsable files."""
        for line, message in parsed.refused:
            cls._warn(f"the image skipped {line}: {message}")
        for line, message in sorted(parsed.parse_errors.items()):
            cls._warn(f"cannot parse {reporter.display_path(line)}: {message}")

    def _execute(self, options: dict, config_file: Path | None = None) -> int:
        """Run the whole analysis for validated `options`; return the exit status.

        Every failure raises `JsComplexityError`.
        """
        target, root = self._resolve_target(options["path"])
        image = resolve_image(options["image"])
        out = Palette(sys.stdout)
        self._print_header(out, target, options, image, config_file)
        selection = self._select(out, target, root, options)

        runner = DockerRunner(image)
        runner.preflight()
        runner.ensure_image()
        proc = runner.run(root, selection.lines)
        runner.check_outcome(proc, root)
        parsed = self._parse_output(proc, selection.lines, image)

        analyzer = FileAnalyzer(options["warn"], options["error"], options["critical"])
        reporter = Reporter(analyzer, target, root, out)
        self._print_warnings(parsed, reporter)
        reporter.report(parsed, options["min_level"], options["top"])
        # The gate uses every level row (never PARSE files), not only the displayed ones.
        failed = self._gate_failed(analyzer, parsed.results.values(), options["fail_on"])
        return 2 if failed else 0
