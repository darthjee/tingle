"""Unit tests for code_check.php_complexity.executor.CheckPhpComplexity (Docker is mocked).

HOME points at an empty temp dir (autouse fixture in tests/code_check/conftest.py),
so no config is loaded; the config tests live in test_executor_config.py.
`GitIgnore.ignored_paths` is stubbed (autouse), so no real git runs here.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from code_check.file_size.git_ignore import GitIgnore, GitIgnored
from code_check.palette import Palette
from code_check.php_complexity import docker_runner
from code_check.php_complexity.constants import Constants
from code_check.php_complexity.errors import PhpComplexityError
from code_check.php_complexity.executor import CheckPhpComplexity
from tests.code_check.php_complexity.sample_output import (
    DETAILED,
    LINES,
    SAMPLE,
    entry,
    output,
)

NO_FILES = "No PHP files found for analysis."


@pytest.fixture(autouse=True)
def fake_git(monkeypatch):
    """Stub GitIgnore.ignored_paths (no real git); records the roots it was called with."""
    state = {"calls": [], "result": None}

    def ignored_paths(root):
        state["calls"].append(root)
        return state["result"]

    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(ignored_paths))
    return state


def _run(args):
    try:
        CheckPhpComplexity().run(args)
    except SystemExit as exc:
        return exc.code
    return 0


# --- class attributes --------------------------------------------------------------


def test_class_attributes():
    assert CheckPhpComplexity.PROG == "tingle code_check php_complexity"
    assert CheckPhpComplexity.CONFIG_SECTION == "php_complexity"
    assert CheckPhpComplexity.LIST_KEYS == ("ignore", "include")
    assert CheckPhpComplexity.THRESHOLD_KEYS == ("warn", "error", "critical")
    assert CheckPhpComplexity.DEFAULT_EXCLUDES is Constants.DEFAULT_EXCLUDES
    assert CheckPhpComplexity.NO_FILES_MESSAGE == NO_FILES
    assert CheckPhpComplexity.error_class is PhpComplexityError
    assert CheckPhpComplexity.SINGLE_DEFAULTS == {
        "warn": 20, "error": 40, "critical": 60, "top": 0, "fail_on": None,
        "min_level": "ok", "image": None, "details": None,
    }


# --- help and usage errors ---------------------------------------------------------


def test_no_args_prints_help_and_exits_zero(capsys):
    assert _run([]) == 0

    out = capsys.readouterr().out
    assert out.startswith("usage: tingle code_check php_complexity ")
    assert "--image" in out
    assert "--no-config" in out


def test_help_exits_zero(capsys):
    assert _run(["-h"]) == 0

    assert capsys.readouterr().out.startswith("usage: tingle code_check php_complexity ")


@pytest.mark.parametrize(
    "args",
    [
        [".", "--warn", "x"],
        [".", "--top", "1.5"],
        [".", "--min-level", "bad"],
        [".", "--fail-on", "ok"],
        [".", "--details", "x"],
        [".", "--unknown"],
    ],
)
def test_argparse_usage_errors_exit_one(capsys, args):
    assert _run(args) == 1

    assert "usage:" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--warn", "-1"], "Error: --warn must be a number >= 0"),
        (["--error", "-0.5"], "Error: --error must be a number >= 0"),
        (["--critical", "-3"], "Error: --critical must be a number >= 0"),
        (["--warn", "nan"], "Error: --warn must be a number >= 0"),
        (["--top", "-1"], "Error: --top must be an integer >= 0"),
        (["--details", "-1"], "Error: --details must be an integer >= 0"),
        (["--image", ""], "Error: --image must not be empty"),
    ],
)
def test_validation_errors_exit_one(tmp_path, capsys, args, message):
    assert _run([str(tmp_path / "missing"), *args]) == 1

    captured = capsys.readouterr()
    assert captured.err.strip() == message
    assert captured.out == ""


def test_merge_fills_the_built_in_defaults():
    cli = {"path": "x", "warn": None, "error": 35.5, "critical": None, "top": None,
           "min_level": None, "fail_on": None, "image": None, "details": None,
           "no_config": False}

    options = CheckPhpComplexity._merge(cli, {})

    assert {k: options[k] for k in CheckPhpComplexity.SINGLE_DEFAULTS} == {
        "warn": 20, "error": 35.5, "critical": 60, "top": 0, "fail_on": None,
        "min_level": "ok", "image": None, "details": None,
    }


def test_selection_options_use_the_merged_options():
    options = {"exclude": ["x"], "no_default_excludes": False, "ignore": ["a"],
               "include": ["b"], "gitignore": True}

    assert CheckPhpComplexity._selection_options(options) == {
        "excludes": [*Constants.DEFAULT_EXCLUDES, "x"],
        "ignore": ["a"],
        "include": ["b"],
        "gitignore": True,
        "skip_bootstrap_cache": True,
    }


def test_no_default_excludes_drops_defaults_and_bootstrap_cache_rule():
    options = {"exclude": ["x"], "no_default_excludes": True, "ignore": [],
               "include": [], "gitignore": False}

    assert CheckPhpComplexity._selection_options(options) == {
        "excludes": ["x"],
        "ignore": [],
        "include": [],
        "gitignore": False,
        "skip_bootstrap_cache": False,
    }


def test_merge_carries_the_selection_options():
    cli = {"path": ".", "exclude": " a, ,b", "no_default_excludes": True,
           "no_gitignore": True, "ignore": ["x", "x"], "include": ["y"]}

    merged = CheckPhpComplexity._merge(cli, {})

    assert merged["exclude"] == ["a", "b"]
    assert merged["no_default_excludes"] is True
    assert merged["gitignore"] is False
    assert merged["ignore"] == ["x"]
    assert merged["include"] == ["y"]


def test_merge_defaults_turn_gitignore_on():
    merged = CheckPhpComplexity._merge({"path": "."}, {})

    assert merged["exclude"] == []
    assert merged["no_default_excludes"] is False
    assert merged["gitignore"] is True
    assert merged["ignore"] == []
    assert merged["include"] == []


def test_validate_config_uses_the_php_complexity_schema(tmp_path):
    from code_check.config import ConfigError

    assert CheckPhpComplexity.validate_config({"warn": 1}, tmp_path / "c.json") == {"warn": 1}
    assert CheckPhpComplexity.validate_config({"details": 1}, tmp_path / "c.json") == {
        "details": 1,
    }
    with pytest.raises(ConfigError, match="unknown key 'ext'"):
        CheckPhpComplexity.validate_config({"ext": [".php"]}, tmp_path / "c.json")


# --- path and image ----------------------------------------------------------------


def test_path_not_found_exits_one(tmp_path, capsys):
    missing = tmp_path / "missing"

    assert _run([str(missing), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == f"Error: path not found: {missing.resolve()}"


def test_unreadable_path_exits_one(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(os, "access", lambda path, mode: False)

    assert _run([str(tmp_path), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == f"Error: path not readable: {tmp_path.resolve()}"


def test_mount_root_with_colon_exits_one(tmp_path, capsys):
    target = tmp_path / "a:b"
    target.mkdir()

    assert _run([str(target), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == (
        f"Error: cannot mount {target.resolve()}: Docker volume paths cannot contain ':'"
    )


def test_unreadable_version_file_exits_one(tmp_path, capsys, monkeypatch):
    missing = tmp_path / "VERSION"
    monkeypatch.setattr(Constants, "VERSION_FILE", missing)

    assert _run([str(tmp_path)]) == 1

    assert capsys.readouterr().err.strip() == (
        f"Error: cannot read the tingle version from {missing}; use --image to choose the image"
    )


# --- nothing selected --------------------------------------------------------------


@pytest.fixture
def no_docker(monkeypatch):
    """Record any command lookup or run (none is expected)."""
    calls = []
    monkeypatch.setattr(docker_runner.shutil, "which", lambda *a, **k: calls.append(a))
    monkeypatch.setattr(docker_runner.subprocess, "run", lambda *a, **k: calls.append(a))
    return calls


def test_nothing_selected_exits_zero_without_docker(tmp_path, capsys, no_docker):
    (tmp_path / "a.py").write_text("x\n")
    (tmp_path / "welcome.blade.php").write_text("x\n")
    for rel in ("vendor/skip.php", "storage/skip.php", "bootstrap/cache/services.php"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("<?php\n")

    assert _run([str(tmp_path), "--image", "img:dev"]) == 0

    captured = capsys.readouterr()
    assert captured.out == (
        f"Analyzing: {tmp_path.resolve()}\n"
        "Thresholds: warn=20 | error=40 | critical=60\n"
        "Image: img:dev\n"
        "\n"
        f"{NO_FILES}\n"
    )
    assert captured.err == ""
    assert no_docker == []


@pytest.mark.parametrize("name", ["a.py", "welcome.blade.php", "W.BLADE.PHP"])
def test_single_unsupported_file_exits_zero_without_docker(tmp_path, capsys, no_docker, name):
    (tmp_path / name).write_text("x\n")

    assert _run([str(tmp_path / name), "--image", "img"]) == 0

    assert NO_FILES in capsys.readouterr().out
    assert no_docker == []


def test_unsendable_name_is_warned(tmp_path, capsys, no_docker):
    (tmp_path / "a\nb.php").write_text("x\n")

    assert _run([str(tmp_path), "--image", "img"]) == 0

    captured = capsys.readouterr()
    assert captured.err == "Warning: skipping file with a newline in its name: 'a\\nb.php'\n"
    assert NO_FILES in captured.out


def test_gitignore_is_consulted_by_default(tmp_path, capsys, no_docker, fake_git):
    fake_git["result"] = GitIgnored(set(), [])

    _run([str(tmp_path), "--image", "img"])

    assert len(fake_git["calls"]) == 1


def test_no_gitignore_does_not_consult_git(tmp_path, capsys, no_docker, fake_git):
    fake_git["result"] = GitIgnored(set(), [])

    _run([str(tmp_path), "--no-gitignore", "--image", "img"])

    assert fake_git["calls"] == []


def test_broken_config_file_is_skipped_with_no_config(tmp_path, capsys, no_docker):
    config = Path(os.environ["HOME"]) / ".tingle" / "code_check" / "config.json"
    config.parent.mkdir(parents=True)
    config.write_text("{ broken")

    assert _run([str(tmp_path), "--image", "img", "--no-config"]) == 0

    captured = capsys.readouterr()
    assert "Config:" not in captured.out
    assert captured.err == ""


# --- end to end (Docker mocked) ----------------------------------------------------

# cli.md §6 full example: the fixture files tingle sends and the image's output.
FIXTURE_OUTPUT = SAMPLE
EXTRA_FIXTURE_FILES = ("welcome.blade.php", "notes.txt")


class FakeDocker:
    """Scripted `docker`: answers info, image inspect, pull and run by sub-command."""

    def __init__(self, stdout="", run_status=0, stderr=b"", info=0, inspect=0, pull=0):
        self.calls = []
        self.stdout = stdout.encode() if isinstance(stdout, str) else stdout
        self.statuses = {"info": info, "image": inspect, "pull": pull, "run": run_status}
        self.stderr = stderr

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        status = self.statuses[args[1]]
        if isinstance(status, BaseException):
            raise status
        if args[1] == "run":
            return SimpleNamespace(returncode=status, stdout=self.stdout, stderr=self.stderr)
        return SimpleNamespace(returncode=status, stdout=b"", stderr=b"")

    @property
    def subcommands(self):
        return [args[1] for args, _ in self.calls]

    def run_call(self):
        return next((a, k) for a, k in self.calls if a[1] == "run")


@pytest.fixture
def fixture_dir(tmp_path):
    root = tmp_path / "fixture"
    for name in (*LINES, *EXTRA_FIXTURE_FILES):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<?php\n")
    return root


@pytest.fixture
def docker(monkeypatch):
    """Install a FakeDocker (reconfigure it through `docker.configure(...)`)."""
    state = {"fake": FakeDocker(json.dumps(FIXTURE_OUTPUT)), "which": "/usr/bin/docker"}

    def configure(**kwargs):
        state["fake"] = FakeDocker(**kwargs)
        return state["fake"]

    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: state["which"])
    monkeypatch.setattr(docker_runner.subprocess, "run", lambda *a, **k: state["fake"](*a, **k))
    return SimpleNamespace(configure=configure, get=lambda: state["fake"], state=state)


def test_end_to_end_full_example(fixture_dir, capsys, docker, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    status = _run([str(fixture_dir), "--image", "darthjee/tingle_php_complexity:0.9.0"])

    assert status == 0
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        f"Analyzing: {fixture_dir.resolve()}",
        "Thresholds: warn=20 | error=40 | critical=60",
        "Image: darthjee/tingle_php_complexity:0.9.0",
        "",
        "Status             CCN    Max    NPath     MI  Lines    Dup  File",
        (
            f"{'─' * 16} {'─' * 5}  {'─' * 5}  {'─' * 7}  {'─' * 5}  "
            f"{'─' * 5}  {'─' * 5}  {'─' * 50}"
        ),
        "✅ OK                11      7       36     54     22      0  fixture/Calculator.php",
        "✅ OK                 6      2        2     78     11      0  fixture/Shapes.php",
        "✅ OK                 4      3        4     66     12      0  fixture/helpers.php",
        "✅ OK                 3      3        4     58      9     13  fixture/dup_a.php",
        "✅ OK                 3      3        4     58      9     13  fixture/dup_b.php",
        "✅ OK                 2      2        4     66      6      0  fixture/Anon.php",
        "✅ OK                 2      2        2     80      2      0  fixture/CVS/legacy.php",
        "✅ OK                 2      1        1     79     11      0  fixture/Modern.php",
        "✅ OK                 2      2        2     78      2      0  fixture/UPPER.PHP",
        "✅ OK                 2      2        2     80      2      0  fixture/bom.php",
        "✅ OK                 2      2        2     80      2      0  fixture/crlf.php",
        "✅ OK                 2      2        2     90      4      0  fixture/page.php",
        "✅ OK                 1      1        1     83      2      0  fixture/latin1.php",
        "✅ OK                 0      -        -      -      -      0  fixture/bootstrap.php",
        "✅ OK                 0      -        -      -      -      0  fixture/empty.php",
        "⛔ PARSE              -      -        -      -      -      -  fixture/attr_anon.php",
        "⛔ PARSE              -      -        -      -      -      -  fixture/broken.php",
        "⛔ PARSE              -      -        -      -      -      -  fixture/lenient.php",
        "",
        "─" * 78,
        "Summary: 18 file(s) | 15 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 3 skipped (parse error)",
        "CCN: avg 2.80 | max 11.00",
    ]
    assert captured.err.splitlines() == [
        "Warning: cannot parse fixture/attr_anon.php: Unexpected token: #[, line: 14, col: 20",
        (
            "Warning: cannot parse fixture/broken.php: "
            'syntax error, unexpected token ":", expecting variable on line 10'
        ),
        'Warning: cannot parse fixture/lenient.php: syntax error, unexpected token ";" on line 5',
    ]


def test_end_to_end_docker_calls_and_stdin(fixture_dir, capsys, docker):
    _run([str(fixture_dir), "--image", "img:dev"])

    fake = docker.get()
    assert fake.subcommands == ["info", "image", "run"]
    args, kwargs = fake.run_call()
    assert args == [
        "docker", "run", "--rm", "-i", "--pull", "never", "--network", "none",
        "--security-opt", "no-new-privileges",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", f"{fixture_dir.resolve()}:/src:ro",
        "-w", "/src",
        "img:dev",
    ]
    assert kwargs["input"] == "".join(f"{n}\n" for n in LINES).encode()


def test_end_to_end_single_file_mounts_parent(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(output([entry("Calculator.php", 45)])))

    status = _run([str(fixture_dir / "Calculator.php"), "--image", "img:dev"])

    assert status == 0
    args, kwargs = docker.get().run_call()
    assert f"{fixture_dir.resolve()}:/src:ro" in args
    assert kwargs["input"] == b"Calculator.php\n"
    out = capsys.readouterr().out
    assert "  Calculator.php\n" in out
    assert "Summary: 1 file(s) | 0 OK | 0 WARN | 1 ERROR | 0 CRITICAL\n" in out


def test_end_to_end_default_image_from_version(fixture_dir, capsys, docker, monkeypatch, tmp_path):
    version = tmp_path / "VERSION"
    version.write_text(" 9.8.7\n")
    monkeypatch.setattr(Constants, "VERSION_FILE", version)

    _run([str(fixture_dir)])

    assert docker.get().run_call()[0][-1] == "darthjee/tingle_php_complexity:9.8.7"
    assert "Image: darthjee/tingle_php_complexity:9.8.7" in capsys.readouterr().out


def test_end_to_end_decimal_thresholds_in_header(fixture_dir, capsys, docker):
    _run([str(fixture_dir), "--image", "img", "--warn", "2.5", "--error", "40.0"])

    assert "Thresholds: warn=2.5 | error=40 | critical=60\n" in capsys.readouterr().out


def test_end_to_end_low_thresholds_and_min_level(fixture_dir, capsys, docker):
    status = _run([
        str(fixture_dir), "--image", "img",
        "--warn", "4", "--error", "6", "--critical", "10", "--min-level", "warn",
    ])

    assert status == 0
    out = capsys.readouterr().out.splitlines()
    assert out[6:9] == [
        "🟣 CRITICAL          11      7       36     54     22      0  fixture/Calculator.php",
        "🔴 ERROR              6      2        2     78     11      0  fixture/Shapes.php",
        "⚠️  WARN             4      3        4     66     12      0  fixture/helpers.php",
    ]
    assert out[-2] == (
        "Summary: 18 file(s) | 12 OK | 1 WARN | 1 ERROR | 1 CRITICAL | 3 skipped (parse error)"
    )


def test_end_to_end_details_under_shown_rows(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(DETAILED))

    status = _run([
        str(fixture_dir), "--image", "img",
        "--warn", "4", "--error", "6", "--critical", "10", "--min-level", "warn",
        "--details", "2",
    ])

    assert status == 0
    out = capsys.readouterr().out.splitlines()
    pad = " " * 16
    assert out[6:18] == [
        "🟣 CRITICAL          11      7       36     54     22      0  fixture/Calculator.php",
        f"{pad} ccn   7  npath      36  Calculator::grade  (fixture/Calculator.php:22)",
        f"{pad} ccn   3  npath       3  Calculator::sign  (fixture/Calculator.php:12)",
        "🔴 ERROR              6      2        2     78     11      0  fixture/Shapes.php",
        f"{pad} ccn   2  npath       2  Circle::area  (fixture/Shapes.php:28)",
        f"{pad} ccn   1  npath       1  Square::__construct  (fixture/Shapes.php:12)",
        "⚠️  WARN             4      3        4     66     12      0  fixture/helpers.php",
        f"{pad} ccn   3  npath       4  clamp  (fixture/helpers.php:3)",
        f"{pad} ccn   1  npath       1  greet  (fixture/helpers.php:14)",
        "⛔ PARSE              -      -        -      -      -      -  fixture/attr_anon.php",
        "⛔ PARSE              -      -        -      -      -      -  fixture/broken.php",
        "⛔ PARSE              -      -        -      -      -      -  fixture/lenient.php",
    ]


def test_end_to_end_details_alone_means_five(fixture_dir, capsys, docker):
    functions = [
        {"name": f"f{i}", "line": i, "ccn": 1, "npath": 1} for i in range(1, 9)
    ]
    data = output([entry("Calculator.php", 8, functions=functions)])
    docker.configure(stdout=json.dumps(data))

    assert _run([str(fixture_dir / "Calculator.php"), "--image", "img", "--details"]) == 0

    out = capsys.readouterr().out
    assert [f"f{i}  (Calculator.php:{i})" in out for i in range(1, 9)] == [True] * 5 + [False] * 3


def test_end_to_end_details_zero_lists_every_unit(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(DETAILED))

    assert _run([str(fixture_dir), "--image", "img", "--details", "0"]) == 0

    out = capsys.readouterr().out
    for name in ("Square::__construct", "Square::area", "Circle::__construct",
                 "Circle::area", "Describes::describe"):
        assert f"  {name}  (fixture/Shapes.php:" in out


def test_end_to_end_without_details_prints_no_unit_lines(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(DETAILED))

    assert _run([str(fixture_dir), "--image", "img"]) == 0

    out = capsys.readouterr().out
    assert "Calculator::grade" not in out
    assert "unavailable" not in out


def test_end_to_end_details_with_an_older_image_shows_the_note(fixture_dir, capsys, docker):
    # SAMPLE is what an image older than #351 emits: `functions: null` everywhere.
    status = _run([
        str(fixture_dir), "--image", "img:old", "--min-level", "ok", "--top", "1",
        "--details",
    ])

    assert status == 0
    out = capsys.readouterr().out.splitlines()
    assert out[6] == (
        "✅ OK                11      7       36     54     22      0  fixture/Calculator.php"
    )
    assert out[7] == f"{' ' * 16} (per-function data unavailable)"
    assert out[8].startswith("⛔ PARSE")


@pytest.mark.parametrize("details", [None, "0"])
def test_details_do_not_change_the_exit_code(fixture_dir, capsys, docker, details):
    docker.configure(stdout=json.dumps(DETAILED))
    extra = [] if details is None else ["--details", details]

    assert _run([str(fixture_dir), "--image", "img", "--warn", "11", "--fail-on", "warn",
                 *extra]) == 2
    assert _run([str(fixture_dir), "--image", "img", "--fail-on", "warn", *extra]) == 0


def test_end_to_end_pulls_missing_image(fixture_dir, capsys, docker):
    fake = docker.configure(stdout=json.dumps(FIXTURE_OUTPUT), inspect=1)

    assert _run([str(fixture_dir), "--image", "img"]) == 0

    assert fake.subcommands == ["info", "image", "pull", "run"]
    assert "Pulling img ..." in capsys.readouterr().err


def test_warning_order(tmp_path, capsys, docker):
    names = ("a.php", "b.php", "c.php", "d.php")
    for name in names:
        (tmp_path / name).write_text("<?php\n")
    data = output(
        [
            entry("a.php", parse_error=True),
            entry("b.php"),
            entry("c.php", parse_error=True),
            entry("d.php", 3),
        ],
        [
            {"tool": "php", "path": "c.php", "message": "syntax error"},
            {"tool": "entrypoint", "path": "b.php", "message": "not a regular file under /src"},
            {"tool": "pdepend", "message": "Something odd"},
            {"tool": "pdepend", "path": "a.php", "message": "Unexpected token"},
            {"tool": "jscpd", "path": "d.php", "message": "per-file, not printed"},
        ],
    )
    docker.configure(stdout=json.dumps(data))

    assert _run([str(tmp_path), "--image", "img"]) == 0

    folder = tmp_path.name
    assert capsys.readouterr().err.splitlines() == [
        "Warning: the image skipped b.php: not a regular file under /src",
        f"Warning: cannot parse {folder}/a.php: Unexpected token",
        f"Warning: cannot parse {folder}/c.php: syntax error",
        "Warning: PDepend reported: Something odd",
    ]



def _jscpd_failure(tmp_path, docker, warnings):
    for name in ("a.php", "b.php"):
        (tmp_path / name).write_text("<?php\n")
    data = output(
        [
            entry("a.php", 30, duplication=None),
            entry("b.php", 1, duplication=None),
        ],
        warnings,
    )
    docker.configure(stdout=json.dumps(data))


def test_jscpd_failure_prints_a_warning(tmp_path, capsys, docker):
    _jscpd_failure(tmp_path, docker, [
        {"tool": "pdepend", "message": "Something odd"},
        {"tool": "jscpd", "message": "jscpd exited with status 2"},
    ])

    assert _run([str(tmp_path), "--image", "img:dev"]) == 0

    captured = capsys.readouterr()
    assert captured.err.splitlines() == [
        "Warning: PDepend reported: Something odd",
        (
            "Warning: jscpd failed in img:dev; duplication data is not available: "
            "jscpd exited with status 2"
        ),
    ]
    folder = tmp_path.name
    assert f"     30      2        4     66      6      -  {folder}/a.php" in captured.out


def test_jscpd_failure_keeps_the_gate_exit_code(tmp_path, capsys, docker):
    _jscpd_failure(tmp_path, docker, [{"tool": "jscpd", "message": "jscpd killed by SIGKILL"}])

    assert _run([str(tmp_path), "--image", "img", "--fail-on", "warn"]) == 2
    assert "Warning: jscpd failed in img; " in capsys.readouterr().err


def test_no_jscpd_warning_without_a_jscpd_failure(fixture_dir, capsys, docker):
    assert _run([str(fixture_dir), "--image", "img"]) == 0

    assert "jscpd" not in capsys.readouterr().err

# --- Docker failures ---------------------------------------------------------------


def test_docker_not_on_path(fixture_dir, capsys, docker):
    docker.state["which"] = None

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == (
        "Error: docker not found on PATH; "
        "tingle code_check php_complexity needs Docker to run PDepend"
    )
    assert docker.get().calls == []


@pytest.mark.parametrize("info", [1, subprocess.TimeoutExpired(["docker", "info"], 30)])
def test_daemon_not_responding(fixture_dir, capsys, docker, info):
    docker.configure(info=info)

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == (
        "Error: the Docker daemon is not responding (docker info failed); start Docker and retry"
    )


def test_pull_failure(fixture_dir, capsys, docker):
    docker.configure(inspect=1, pull=1)

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.splitlines()[-1] == "Error: could not pull image img"


@pytest.mark.parametrize("stderr", [b"docker: mounts denied\n", b"path is not shared from the host\n"])
def test_mount_failure(fixture_dir, capsys, docker, stderr):
    docker.configure(run_status=125, stderr=stderr)

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.splitlines() == [
        stderr.decode().strip(),
        (
            f"Error: Docker could not mount {fixture_dir.resolve()}; on Docker Desktop, share it "
            "(or a parent folder) under Settings > Resources > File sharing, then retry"
        ),
    ]


@pytest.mark.parametrize("status", [1, 3, 137])
def test_container_failure(fixture_dir, capsys, docker, status):
    docker.configure(run_status=status, stderr=b"tingle_php_complexity: boom\n")

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.splitlines() == [
        "tingle_php_complexity: boom",
        f"Error: PDepend failed in img (exit {status})",
    ]


def _bad_tool_versions():
    return json.dumps(output([], None) | {"tool_versions": {"php": "8.5.11"}})


def _bad_entry():
    data = json.loads(json.dumps(SAMPLE))
    data["files"][0]["parse_error"] = 1
    return json.dumps(data)


def _bad_warnings():
    data = json.loads(json.dumps(SAMPLE))
    data["warnings"].append({"tool": "phpstan", "message": "m"})
    return json.dumps(data)


@pytest.mark.parametrize(
    ("stdout", "reason"),
    [
        ("nope", "invalid JSON: "),
        ("[]", "expected a JSON object"),
        (_bad_tool_versions(), "unexpected tool_versions"),
        (json.dumps(output([])), "files do not match the sent lines"),
        (_bad_entry(), "unexpected files entry: 0"),
        (_bad_warnings(), "unexpected warnings"),
    ],
)
def test_unparsable_output(fixture_dir, capsys, docker, stdout, reason):
    docker.configure(stdout=stdout, stderr=b"container noise\n")

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    err = capsys.readouterr().err.splitlines()
    assert err[0] == "container noise"
    assert err[1].startswith(f"Error: could not parse the output of img: {reason}")


def test_parse_output_raises_with_reason():
    proc = SimpleNamespace(returncode=0, stdout=b"[]", stderr=b"")

    with pytest.raises(PhpComplexityError) as exc_info:
        CheckPhpComplexity._parse_output(proc, ["a.php"], "img")

    assert exc_info.value.message == "could not parse the output of img: expected a JSON object"


# --- gate --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["--fail-on", "warn"], 0),
        (["--warn", "11", "--fail-on", "warn"], 2),
        (["--warn", "12", "--fail-on", "warn"], 0),
        (["--error", "11", "--fail-on", "error"], 2),
        (["--critical", "11", "--fail-on", "critical"], 2),
        (["--critical", "11.5", "--fail-on", "critical"], 0),
    ],
)
def test_fail_on(fixture_dir, capsys, docker, args, expected):
    assert _run([str(fixture_dir), "--image", "img", *args]) == expected


def test_fail_on_uses_hidden_rows(fixture_dir, capsys, docker):
    status = _run([
        str(fixture_dir), "--image", "img", "--warn", "5", "--error", "10",
        "--min-level", "critical", "--top", "1", "--fail-on", "error",
    ])

    assert status == 2


def test_fail_on_uses_the_total_ccn_not_max_or_npath(fixture_dir, capsys, docker):
    data = output([entry("Calculator.php", 5, max_ccn=99, max_npath=10**20, min_mi=0)])
    docker.configure(stdout=json.dumps(data))

    status = _run([str(fixture_dir / "Calculator.php"), "--image", "img", "--fail-on", "warn"])

    assert status == 0


def test_parse_rows_never_fail_the_gate(fixture_dir, capsys, docker):
    files = [entry(n, parse_error=True) for n in LINES]
    docker.configure(stdout=json.dumps(output(files)))

    status = _run([str(fixture_dir), "--image", "img", "--warn", "0", "--fail-on", "warn"])

    assert status == 0
    out = capsys.readouterr().out
    assert "Summary: 18 file(s) | 0 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 18 skipped" in out
    assert "CCN: n/a" in out


def test_files_without_data_count_for_the_gate(fixture_dir, capsys, docker):
    files = [entry(n) for n in LINES]
    docker.configure(stdout=json.dumps(output(files)))

    status = _run([str(fixture_dir), "--image", "img", "--warn", "0", "--fail-on", "warn"])

    assert status == 2


def test_print_header(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    CheckPhpComplexity._print_header(
        Palette(), tmp_path, {"warn": 20, "error": 12.5, "critical": 60.0}, "img:1"
    )

    assert capsys.readouterr().out == (
        f"Analyzing: {tmp_path}\nThresholds: warn=20 | error=12.5 | critical=60\nImage: img:1\n\n"
    )
