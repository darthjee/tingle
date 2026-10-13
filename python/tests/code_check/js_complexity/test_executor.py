"""Unit tests for code_check.js_complexity.executor.CheckJsComplexity (Docker is mocked).

HOME points at an empty temp dir (autouse fixture in tests/code_check/conftest.py),
so no config file is found; the config itself is covered by test_executor_config.py.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from code_check.file_size.git_ignore import GitIgnore, GitIgnored
from code_check.js_complexity import docker_runner
from code_check.js_complexity.constants import Constants
from code_check.js_complexity.errors import JsComplexityError
from code_check.js_complexity.executor import CheckJsComplexity
from code_check.palette import Palette
from tests.code_check.js_complexity.sample_output import entry, output


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
        CheckJsComplexity().run(args)
    except SystemExit as exc:
        return exc.code
    return 0


# --- help and usage errors ---------------------------------------------------------


def test_no_args_prints_help_and_exits_zero(capsys):
    assert _run([]) == 0

    out = capsys.readouterr().out
    assert out.startswith("usage: tingle code_check js_complexity ")
    assert "--image" in out
    assert "--no-config" in out


def test_help_exits_zero(capsys):
    assert _run(["-h"]) == 0

    assert capsys.readouterr().out.startswith("usage: tingle code_check js_complexity ")


@pytest.mark.parametrize(
    "args",
    [
        [".", "--warn", "x"],
        [".", "--top", "1.5"],
        [".", "--min-level", "bad"],
        [".", "--fail-on", "ok"],
        [".", "--details"],
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
        (["--image", ""], "Error: --image must not be empty"),
    ],
)
def test_validation_errors_exit_one(tmp_path, capsys, args, message):
    assert _run([str(tmp_path / "missing"), *args]) == 1

    captured = capsys.readouterr()
    assert captured.err.strip() == message
    assert captured.out == ""


def test_merge_fills_the_built_in_defaults():
    cli = {"path": "x", "warn": None, "error": 55.5, "critical": None, "top": None,
           "min_level": None, "fail_on": None, "image": None, "no_config": False}

    options = CheckJsComplexity._merge(cli, {})

    assert {k: options[k] for k in CheckJsComplexity.SINGLE_DEFAULTS} == {
        "warn": 50, "error": 55.5, "critical": 75, "top": 0, "fail_on": None,
        "min_level": "ok", "image": None,
    }


def test_merge_resolves_the_selection_options():
    cli = {"path": "x", "exclude": "test,,fixtures,test", "no_default_excludes": False,
           "no_gitignore": False, "ignore": ["a", "b", "a"], "include": ["c", "c"],
           "no_config": False}

    options = CheckJsComplexity._merge(cli, {})

    assert options["exclude"] == ["test", "fixtures"]
    assert options["no_default_excludes"] is False
    assert options["gitignore"] is True
    assert options["ignore"] == ["a", "b"]
    assert options["include"] == ["c"]


def test_merge_no_gitignore_turns_gitignore_off():
    options = CheckJsComplexity._merge({"path": "x", "no_gitignore": True}, {})

    assert options["gitignore"] is False


def test_selection_options_defaults():
    assert CheckJsComplexity._selection_options({}) == {
        "excludes": Constants.DEFAULT_EXCLUDES,
        "ignore": [],
        "include": [],
        "gitignore": True,
    }


def test_selection_options_from_flags():
    options = {"exclude": ["test", "dist"], "no_default_excludes": False, "ignore": ["a"],
               "include": ["b"], "gitignore": False}

    assert CheckJsComplexity._selection_options(options) == {
        "excludes": [*Constants.DEFAULT_EXCLUDES, "test"],
        "ignore": ["a"],
        "include": ["b"],
        "gitignore": False,
    }


def test_selection_options_no_default_excludes():
    options = {"exclude": ["vendor"], "no_default_excludes": True}

    assert CheckJsComplexity._selection_options(options)["excludes"] == ["vendor"]


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
    (tmp_path / "types.d.ts").write_text("x\n")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "skip.js").write_text("x\n")

    assert _run([str(tmp_path), "--image", "img:dev"]) == 0

    captured = capsys.readouterr()
    assert captured.out == (
        f"Analyzing: {tmp_path.resolve()}\n"
        "Thresholds: warn=50 | error=60 | critical=75\n"
        "Image: img:dev\n"
        "\n"
        "No JavaScript/TypeScript files found for analysis.\n"
    )
    assert captured.err == ""
    assert no_docker == []


@pytest.mark.parametrize("name", ["a.py", "types.d.ts"])
def test_single_unsupported_file_exits_zero_without_docker(tmp_path, capsys, no_docker, name):
    (tmp_path / name).write_text("x\n")

    assert _run([str(tmp_path / name), "--image", "img"]) == 0

    assert "No JavaScript/TypeScript files found for analysis." in capsys.readouterr().out
    assert no_docker == []


def test_unsendable_name_is_warned(tmp_path, capsys, no_docker):
    (tmp_path / "a\nb.js").write_text("x\n")

    assert _run([str(tmp_path), "--image", "img"]) == 0

    captured = capsys.readouterr()
    assert captured.err == "Warning: skipping file with a newline in its name: 'a\\nb.js'\n"
    assert "No JavaScript/TypeScript files found for analysis." in captured.out


def test_gitignore_is_consulted_by_default(tmp_path, capsys, no_docker, fake_git):
    fake_git["result"] = GitIgnored(set(), [])

    _run([str(tmp_path), "--image", "img"])

    assert fake_git["calls"] == [tmp_path.resolve()]


def test_no_gitignore_does_not_consult_git(tmp_path, capsys, no_docker, fake_git):
    _run([str(tmp_path), "--image", "img", "--no-gitignore"])

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

FIXTURE_FILES = ("complex.ts", "simple.js", "empty.js", "broken.js", "latin1.js", "gone.js")

FIXTURE_OUTPUT = output(
    [
        entry("broken.js", parse_error=True),
        entry("complex.ts", 71.25291592210418, fta={
            "score": 71.25291592210418, "cyclo": 136, "lines": 245,
            "assessment": "Needs improvement",
        }),
        entry("empty.js"),
        entry("gone.js"),
        entry("latin1.js", parse_error=True),
        entry("simple.js", 7.690944198185733, fta={
            "score": 7.690944198185733, "cyclo": 1, "lines": 6, "assessment": "OK",
        }),
    ],
    [
        {"tool": "jscpd", "message": "jscpd failed"},
        {"tool": "fta", "path": "latin1.js", "message": "file is not valid UTF-8"},
        {"tool": "entrypoint", "path": "gone.js", "message": "not a regular file under /src"},
        {"tool": "fta", "path": "broken.js", "message": "Expected ','"},
    ],
)


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
    root.mkdir()
    for name in FIXTURE_FILES:
        (root / name).write_text("const a = 1;\n")
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


def test_end_to_end_report_and_warnings(fixture_dir, capsys, docker, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    status = _run([str(fixture_dir), "--image", "darthjee/tingle_js_complexity:0.9.0"])

    assert status == 0
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        f"Analyzing: {fixture_dir.resolve()}",
        "Thresholds: warn=50 | error=60 | critical=75",
        "Image: darthjee/tingle_js_complexity:0.9.0",
        "",
        "Status             FTA  Cyclo  Lines  Assessment         File",
        f"{'─' * 16} {'─' * 5}  {'─' * 5}  {'─' * 5}  {'─' * 17}  {'─' * 50}",
        "🔴 ERROR           71.3    136    245  Needs improvement  fixture/complex.ts",
        "✅ OK               7.7      1      6  OK                 fixture/simple.js",
        "✅ OK               0.0      -      -  -                  fixture/empty.js",
        "✅ OK               0.0      -      -  -                  fixture/gone.js",
        "⛔ PARSE              -      -      -  -                  fixture/broken.js",
        "⛔ PARSE              -      -      -  -                  fixture/latin1.js",
        "",
        "─" * 78,
        "Summary: 6 file(s) | 3 OK | 0 WARN | 1 ERROR | 0 CRITICAL | 2 skipped (parse error)",
        "FTA score: avg 19.75 | max 71.30",
    ]
    assert captured.err.splitlines() == [
        "Warning: the image skipped gone.js: not a regular file under /src",
        "Warning: cannot parse fixture/broken.js: Expected ','",
        "Warning: cannot parse fixture/latin1.js: file is not valid UTF-8",
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
    assert kwargs["input"] == "".join(f"{n}\n" for n in sorted(FIXTURE_FILES)).encode()


def test_end_to_end_single_file_mounts_parent(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(output([entry("complex.ts", 61.0)])))

    status = _run([str(fixture_dir / "complex.ts"), "--image", "img:dev"])

    assert status == 0
    args, kwargs = docker.get().run_call()
    assert f"{fixture_dir.resolve()}:/src:ro" in args
    assert kwargs["input"] == b"complex.ts\n"
    out = capsys.readouterr().out
    assert "  complex.ts\n" in out
    assert "Summary: 1 file(s) | 0 OK | 0 WARN | 1 ERROR | 0 CRITICAL\n" in out


def test_end_to_end_default_image_from_version(fixture_dir, capsys, docker, monkeypatch, tmp_path):
    version = tmp_path / "VERSION"
    version.write_text(" 9.8.7\n")
    monkeypatch.setattr(Constants, "VERSION_FILE", version)

    _run([str(fixture_dir)])

    assert docker.get().run_call()[0][-1] == "darthjee/tingle_js_complexity:9.8.7"
    assert "Image: darthjee/tingle_js_complexity:9.8.7" in capsys.readouterr().out


def test_end_to_end_decimal_thresholds_in_header(fixture_dir, capsys, docker):
    _run([str(fixture_dir), "--image", "img", "--warn", "42.5", "--error", "60.0"])

    assert "Thresholds: warn=42.5 | error=60 | critical=75\n" in capsys.readouterr().out


def test_end_to_end_pulls_missing_image(fixture_dir, capsys, docker):
    fake = docker.configure(stdout=json.dumps(FIXTURE_OUTPUT), inspect=1)

    assert _run([str(fixture_dir), "--image", "img"]) == 0

    assert fake.subcommands == ["info", "image", "pull", "run"]
    assert "Pulling img ..." in capsys.readouterr().err


# --- Docker failures ---------------------------------------------------------------


def test_docker_not_on_path(fixture_dir, capsys, docker):
    docker.state["which"] = None

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == (
        "Error: docker not found on PATH; tingle code_check js_complexity needs Docker to run FTA"
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


def test_mount_failure(fixture_dir, capsys, docker):
    docker.configure(run_status=125, stderr=b"docker: Error response: mounts denied\n")

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.splitlines() == [
        "docker: Error response: mounts denied",
        (
            f"Error: Docker could not mount {fixture_dir.resolve()}; on Docker Desktop, share it "
            "(or a parent folder) under Settings > Resources > File sharing, then retry"
        ),
    ]


def test_container_failure(fixture_dir, capsys, docker):
    docker.configure(run_status=3, stderr=b"tingle_js_complexity: boom\n")

    assert _run([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.splitlines() == [
        "tingle_js_complexity: boom",
        "Error: FTA failed in img (exit 3)",
    ]


@pytest.mark.parametrize(
    ("stdout", "reason"),
    [
        ("nope", "invalid JSON: "),
        ("[]", "expected a JSON object"),
        (json.dumps(output([])), "files do not match the sent lines"),
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

    with pytest.raises(JsComplexityError) as exc_info:
        CheckJsComplexity._parse_output(proc, ["a.js"], "img")

    assert exc_info.value.message == "could not parse the output of img: expected a JSON object"


# --- gate --------------------------------------------------------------------------


@pytest.mark.parametrize(("fail_on", "expected"), [("warn", 2), ("error", 2), ("critical", 0)])
def test_fail_on(fixture_dir, capsys, docker, fail_on, expected):
    assert _run([str(fixture_dir), "--image", "img", "--fail-on", fail_on]) == expected


def test_fail_on_uses_hidden_rows(fixture_dir, capsys, docker):
    status = _run([
        str(fixture_dir), "--image", "img", "--min-level", "critical", "--fail-on", "error",
    ])

    assert status == 2


def test_fail_on_uses_the_rounded_score(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(output([entry("complex.ts", 59.96)])))

    status = _run([str(fixture_dir / "complex.ts"), "--image", "img", "--fail-on", "error"])

    assert status == 2
    assert "🔴 ERROR           60.0" in capsys.readouterr().out


def test_parse_rows_never_fail_the_gate(fixture_dir, capsys, docker):
    files = [entry(n, parse_error=True) for n in sorted(FIXTURE_FILES)]
    docker.configure(stdout=json.dumps(output(files)))

    status = _run([str(fixture_dir), "--image", "img", "--warn", "0", "--fail-on", "warn"])

    assert status == 0
    out = capsys.readouterr().out
    assert "Summary: 6 file(s) | 0 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 6 skipped" in out
    assert "FTA score: n/a" in out


def test_dropped_files_count_for_the_gate(fixture_dir, capsys, docker):
    files = [entry(n) for n in sorted(FIXTURE_FILES)]
    docker.configure(stdout=json.dumps(output(files)))

    status = _run([str(fixture_dir), "--image", "img", "--warn", "0", "--fail-on", "warn"])

    assert status == 2


def test_print_header(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    CheckJsComplexity._print_header(
        Palette(), tmp_path, {"warn": 50, "error": 12.5, "critical": 75.0}, "img:1"
    )

    assert capsys.readouterr().out == (
        f"Analyzing: {tmp_path}\nThresholds: warn=50 | error=12.5 | critical=75\nImage: img:1\n\n"
    )
