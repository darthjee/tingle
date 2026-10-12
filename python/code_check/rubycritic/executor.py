#!/usr/bin/env python3
"""executor.py — Ruby code complexity via RubyCritic (Docker).

Selects the `.rb` files under `<path>` on the host, runs RubyCritic (Flog,
Flay and Reek) inside the `darthjee/tingle_rubycritic` Docker image and
reports one row per file, classified by thresholds on the file's total Flog
complexity, plus RubyCritic's overall score. The host needs Docker, not Ruby.

File selection follows `file_size`: default and `--exclude` directory names,
`.gitignore` (unless `--no-gitignore`), `--ignore` and `--include` globs and
the fixed `.rb` filter. Symlinks resolving outside the mount root are skipped.

Personal defaults are read from the `rubycritic` section of
`~/.tingle/code_check/config.json` (keys: warn, error, critical, top, exclude,
ignore, include, no_default_excludes, gitignore, fail_on, min_level, image,
details; there is no `ext`). Single values given on the CLI win over the
config, which wins over the built-in defaults; list values (exclude, ignore,
include) are concatenated, config first, and deduplicated.
`--no-default-excludes` and `--no-gitignore` win over the config. An invalid
config prints `Error: <path>: <reason>` and exits with status 1 before any
file selection or Docker call. `--no-config` skips the file entirely.

Example config:
    {"rubycritic": {"warn": 50, "ignore": ["spec/fixtures/**"], "fail_on": "error"}}

Exit status: 0 on success (also when no `.rb` file is selected), 1 on errors
(bad option, invalid config, path missing or unreadable, Docker missing or
failing, image pull failure, unparsable output) and 2 when `--fail-on` is set
and any file reaches that level.

Dependencies: standard library only; Docker on the host at run time.

Usage:
    tingle code_check rubycritic <path> [options]

Examples
--------
    tingle code_check rubycritic ./app
    tingle code_check rubycritic ./app --warn 50 --error 100 --critical 200
    tingle code_check rubycritic ./app --top 10 --min-level warn
    tingle code_check rubycritic ./app --fail-on error
    tingle code_check rubycritic ./app --details
    tingle code_check rubycritic ./app --details 0
    tingle code_check rubycritic ./app --image tingle_rubycritic:dev
    tingle code_check rubycritic . --exclude spec,db
    tingle code_check rubycritic . --no-default-excludes --exclude vendor
    tingle code_check rubycritic . --ignore 'db/migrate/**' --ignore '*_spec.rb'
    tingle code_check rubycritic . --include 'app/**' --include 'lib/**'
    tingle code_check rubycritic . --no-gitignore
    tingle code_check rubycritic . --no-config

"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from code_check.config import load_section
from code_check.docker_check.executor import DockerCheck
from code_check.file_size.file_analyzer import FileAnalyzer
from code_check.palette import Palette
from code_check.rubycritic.config import validate
from code_check.rubycritic.constants import Constants
from code_check.rubycritic.docker_runner import DockerRunner, decode, write_stderr
from code_check.rubycritic.errors import RubycriticError
from code_check.rubycritic.flags import FLAGS
from code_check.rubycritic.image import resolve_image
from code_check.rubycritic.output_parser import FileResult, OutputFormatError, ParsedOutput, parse
from code_check.rubycritic.reporter import Reporter
from code_check.rubycritic.selection import Selection, select_files

# Program name shown in the help usage line.
PROG = "tingle code_check rubycritic"

# Section of the config file holding this command's options.
CONFIG_SECTION = "rubycritic"

# Built-in defaults for single-value options, applied after the config merge.
SINGLE_DEFAULTS: dict = {
    "warn": Constants.DEFAULT_WARN,
    "error": Constants.DEFAULT_ERROR,
    "critical": Constants.DEFAULT_CRITICAL,
    "top": 0,
    "fail_on": None,
    "min_level": "ok",
    "image": None,
    "details": None,
}

# Glob-list options merged as config list then CLI list (deduplicated).
LIST_KEYS = ("ignore", "include")

# Threshold options validated as numbers >= 0.
THRESHOLD_KEYS = ("warn", "error", "critical")


class CheckRubycritic(DockerCheck):
    """Orchestrate the flow: parse → validate → resolve → select → run → report."""

    PROG = PROG
    FLAGS = FLAGS
    CONFIG_SECTION = CONFIG_SECTION
    SINGLE_DEFAULTS = SINGLE_DEFAULTS
    LIST_KEYS = LIST_KEYS
    THRESHOLD_KEYS = THRESHOLD_KEYS
    DEFAULT_EXCLUDES = Constants.DEFAULT_EXCLUDES
    NO_FILES_MESSAGE = "No Ruby files found for analysis."
    error_class = RubycriticError

    validate_config = staticmethod(validate)

    @staticmethod
    def _load_section(name: str, path: Path | None = None) -> dict | None:
        """Read the config section through this module's `load_section`."""
        return load_section(name, path)

    @staticmethod
    def _select_files(target: Path, root: Path, **kwargs) -> Selection:
        """Select the `.rb` files through this module's `select_files`."""
        return select_files(target, root, **kwargs)

    @staticmethod
    def _gate_value(result: FileResult) -> float:
        """Classify a file for the `--fail-on` gate by its total Flog complexity."""
        return result.complexity

    @staticmethod
    def _parse_output(proc, lines: list[str], image: str) -> ParsedOutput:
        """Parse the container stdout; on a contract break pass its stderr through and fail."""
        try:
            return parse(decode(proc.stdout), lines)
        except OutputFormatError as exc:
            write_stderr(proc)
            raise RubycriticError(
                f"could not parse the RubyCritic output from {image}: {exc.reason}"
            ) from exc

    @staticmethod
    def _check_methods(parsed: ParsedOutput, details: int | None, image: str) -> None:
        """Fail when `--details` is set but the image printed no per-method data."""
        if details is not None and parsed.methods is None:
            raise RubycriticError(
                f"the RubyCritic output from {image} has no per-method data; "
                "--details needs a newer tingle_rubycritic image"
            )

    def _execute(self, options: dict, config_file: Path | None = None) -> int:
        """Run the whole analysis for validated `options`; return the exit status.

        `config_file` is the loaded config file shown in the header, if any.

        Every failure raises `RubycriticError`.
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
        self._check_methods(parsed, options["details"], image)

        analyzer = FileAnalyzer(options["warn"], options["error"], options["critical"])
        reporter = Reporter(analyzer, target, root, out)
        for line, message in sorted(parsed.parse_errors.items()):
            self._warn(f"cannot parse {reporter.display_path(line)}: {message}")
        reporter.report(parsed, options["min_level"], options["top"], options["details"])
        # The gate uses every file, not only the displayed rows.
        failed = self._gate_failed(analyzer, parsed.results.values(), options["fail_on"])
        return 2 if failed else 0
