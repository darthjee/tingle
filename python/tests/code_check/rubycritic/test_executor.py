"""Unit tests for code_check.rubycritic.executor.CheckRubycritic (parse, validate, resolve)."""

from __future__ import annotations

import json
import os
from types import SimpleNamespace

import pytest

from code_check.file_size.git_ignore import GitIgnore, GitIgnored
from code_check.palette import Palette
from code_check.rubycritic import docker_runner
from code_check.rubycritic.errors import RubycriticError
from code_check.rubycritic.executor import CheckRubycritic
from tests.code_check.rubycritic.sample_output import sample


@pytest.fixture(autouse=True)
def fake_git(monkeypatch):
    """Stub GitIgnore.ignored_paths (no real git); returns the roots it was called with."""
    state = {"calls": [], "result": None}

    def ignored_paths(root):
        state["calls"].append(root)
        return state["result"]

    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(ignored_paths))
    return state


def _run(args):
    with pytest.raises(SystemExit) as exc_info:
        CheckRubycritic().run(args)
    return exc_info.value.code


# --- help and usage errors ---------------------------------------------------------


def test_run_no_args_prints_help_and_exits_zero(capsys):
    assert _run([]) == 0

    out = capsys.readouterr().out
    assert out.startswith("usage: tingle code_check rubycritic ")
    assert "--image" in out


def test_run_help_exits_zero(capsys):
    assert _run(["-h"]) == 0

    assert capsys.readouterr().out.startswith("usage: tingle code_check rubycritic ")


@pytest.mark.parametrize(
    "args",
    [
        [".", "--warn", "x"],
        [".", "--top", "1.5"],
        [".", "--details", "x"],
        [".", "--min-level", "bad"],
        [".", "--fail-on", "ok"],
        [".", "--unknown"],
    ],
)
def test_run_argparse_usage_errors_exit_one(capsys, args):
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
def test_run_validation_errors_exit_one(tmp_path, capsys, args, message):
    missing = tmp_path / "missing"

    assert _run([str(missing), *args]) == 1

    captured = capsys.readouterr()
    # Validation runs before the path is resolved.
    assert captured.err.strip() == message
    assert captured.out == ""


def test_validate_accepts_zero_and_inf():
    options = {"warn": 0.0, "error": float("inf"), "critical": 0.0, "top": 0, "image": None}

    assert CheckRubycritic._validate(options) is options


def test_apply_defaults_fills_unset_values():
    cli = {"path": "x", "warn": None, "error": 5.0, "critical": None, "top": None,
           "min_level": None, "fail_on": None, "image": None}

    options = CheckRubycritic._apply_defaults(cli)

    assert options == {"path": "x", "warn": 100, "error": 5.0, "critical": 400, "top": 0,
                       "min_level": "ok", "fail_on": None, "image": None, "details": None}


@pytest.mark.parametrize("details", [0, 5])
def test_validate_accepts_details(details):
    options = {"warn": 0.0, "error": 0.0, "critical": 0.0, "top": 0, "image": None,
               "details": details}

    assert CheckRubycritic._validate(options) is options


# --- path resolution ---------------------------------------------------------------


def test_run_path_not_found_exits_one(tmp_path, capsys):
    missing = tmp_path / "missing"

    assert _run([str(missing), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == f"Error: path not found: {missing.resolve()}"


def test_resolve_target_directory_is_its_own_root(tmp_path):
    target, root = CheckRubycritic._resolve_target(str(tmp_path))

    assert target == tmp_path.resolve()
    assert root == tmp_path.resolve()


def test_resolve_target_file_root_is_parent(tmp_path):
    file_path = tmp_path / "a.rb"
    file_path.write_text("x\n")

    target, root = CheckRubycritic._resolve_target(str(file_path))

    assert target == file_path.resolve()
    assert root == tmp_path.resolve()


def test_resolve_target_unreadable_file(tmp_path, monkeypatch):
    file_path = tmp_path / "a.rb"
    file_path.write_text("x\n")
    modes = []

    def fake_access(path, mode):
        modes.append(mode)
        return False

    monkeypatch.setattr(os, "access", fake_access)

    with pytest.raises(RubycriticError) as exc_info:
        CheckRubycritic._resolve_target(str(file_path))

    assert exc_info.value.message == f"path not readable: {file_path.resolve()}"
    assert modes == [os.R_OK]


def test_resolve_target_directory_needs_read_and_execute(tmp_path, monkeypatch):
    modes = []

    def fake_access(path, mode):
        modes.append(mode)
        return mode == os.R_OK

    monkeypatch.setattr(os, "access", fake_access)

    with pytest.raises(RubycriticError, match="path not readable"):
        CheckRubycritic._resolve_target(str(tmp_path))

    assert modes == [os.R_OK | os.X_OK]


def test_run_unreadable_path_exits_one(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(os, "access", lambda path, mode: False)

    assert _run([str(tmp_path), "--image", "img"]) == 1

    assert capsys.readouterr().err.strip() == f"Error: path not readable: {tmp_path.resolve()}"


def test_resolve_target_colon_in_directory_root(tmp_path):
    target = tmp_path / "a:b"
    target.mkdir()

    with pytest.raises(RubycriticError) as exc_info:
        CheckRubycritic._resolve_target(str(target))

    assert exc_info.value.message == (
        f"cannot mount {target.resolve()}: Docker volume paths cannot contain ':'"
    )


def test_resolve_target_colon_in_file_parent(tmp_path):
    parent = tmp_path / "a:b"
    parent.mkdir()
    (parent / "x.rb").write_text("x\n")

    with pytest.raises(RubycriticError, match=r"cannot mount .*a:b: Docker volume"):
        CheckRubycritic._resolve_target(str(parent / "x.rb"))


def test_resolve_target_colon_in_file_name_only_is_fine(tmp_path):
    file_path = tmp_path / "a:b.rb"
    file_path.write_text("x\n")

    _target, root = CheckRubycritic._resolve_target(str(file_path))

    assert root == tmp_path.resolve()


# --- image ------------------------------------------------------------------------


def test_run_unreadable_version_file_exits_one(tmp_path, capsys, monkeypatch):
    from code_check.rubycritic.constants import Constants

    missing = tmp_path / "VERSION"
    monkeypatch.setattr(Constants, "VERSION_FILE", missing)

    assert _run([str(tmp_path)]) == 1

    assert capsys.readouterr().err.strip() == (
        f"Error: cannot read the tingle version from {missing}; use --image to choose the image"
    )


# --- header -----------------------------------------------------------------------


def test_print_header(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    options = {"warn": 100, "error": 12.5, "critical": 400.0}

    CheckRubycritic._print_header(Palette(), tmp_path, options, "img:1")

    assert capsys.readouterr().out == (
        f"Analyzing: {tmp_path}\n"
        "Thresholds: warn=100 | error=12.5 | critical=400\n"
        "Image: img:1\n"
        "\n"
    )


# --- selection ----------------------------------------------------------------------


@pytest.fixture
def no_docker(monkeypatch):
    """Fail the test if anything looks up or runs a command."""
    import shutil
    import subprocess

    calls = []
    monkeypatch.setattr(shutil, "which", lambda *a, **k: calls.append(("which", a)))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append(("run", a)))
    return calls


def test_run_no_ruby_files_exits_zero_without_docker(tmp_path, capsys, no_docker):
    (tmp_path / "a.py").write_text("x\n")
    (tmp_path / "tmp").mkdir()
    (tmp_path / "tmp" / "skip.rb").write_text("x\n")

    assert _run([str(tmp_path), "--image", "img:dev"]) == 0

    captured = capsys.readouterr()
    assert captured.out == (
        f"Analyzing: {tmp_path.resolve()}\n"
        "Thresholds: warn=100 | error=200 | critical=400\n"
        "Image: img:dev\n"
        "\n"
        "No Ruby files found for analysis.\n"
    )
    assert captured.err == ""
    assert no_docker == []


def test_run_single_non_ruby_file_exits_zero_without_docker(tmp_path, capsys, no_docker):
    file_path = tmp_path / "a.py"
    file_path.write_text("x\n")

    assert _run([str(file_path), "--image", "img:dev"]) == 0

    assert "No Ruby files found for analysis." in capsys.readouterr().out
    assert no_docker == []


def test_select_warns_about_unsendable_names(tmp_path, capsys, monkeypatch):
    from code_check.rubycritic import executor
    from code_check.rubycritic.selection import Selection

    monkeypatch.setattr(
        executor,
        "select_files",
        lambda target, root, **kwargs: Selection(
            root, [], ["skipping file with a newline in its name: 'a'"]
        ),
    )

    with pytest.raises(SystemExit) as exc_info:
        CheckRubycritic._select(Palette(), tmp_path, tmp_path, {})

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert captured.err == "Warning: skipping file with a newline in its name: 'a'\n"
    assert captured.out == "No Ruby files found for analysis.\n"


# --- end to end (Docker mocked) ----------------------------------------------------

FIXTURE_FILES = (
    "complex.rb", "dup_a.rb", "dup_b.rb", "constants_only.rb", "empty.rb", "simple.rb", "broken.rb",
)


def _module(path, complexity, rating, smells, duplication):
    return {"path": path, "complexity": complexity, "rating": rating,
            "smells": [{"type": "TooManyStatements"}] * smells + [{"type": "DuplicateCode"}],
            "duplication": duplication}


FIXTURE_OUTPUT = sample(
    analysed_modules=[
        _module("complex.rb", 72.25, "B", 14, 0),
        _module("dup_a.rb", 15.11, "C", 11, 39),
        _module("dup_b.rb", 15.11, "C", 11, 39),
        _module("constants_only.rb", 0.0, "A", 0, 0),
        _module("empty.rb", 0.0, "A", 0, 0),
        _module("simple.rb", 0.0, "A", 1, 0),
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
        (root / name).write_text("x = 1\n")
    return root


@pytest.fixture
def docker(monkeypatch):
    """Install a FakeDocker (configure it through `docker.configure(...)`)."""
    state = {"fake": FakeDocker(json.dumps(FIXTURE_OUTPUT))}

    def configure(**kwargs):
        state["fake"] = FakeDocker(**kwargs)
        return state["fake"]

    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: "/usr/bin/docker")
    monkeypatch.setattr(docker_runner.subprocess, "run", lambda *a, **k: state["fake"](*a, **k))
    return SimpleNamespace(configure=configure, get=lambda: state["fake"])


def _run_status(args):
    try:
        CheckRubycritic().run(args)
    except SystemExit as exc:
        return exc.code
    return 0


def test_end_to_end_full_example(fixture_dir, capsys, docker, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    status = _run_status([
        str(fixture_dir), "--warn", "10", "--error", "50", "--critical", "100",
        "--image", "darthjee/tingle_rubycritic:0.6.0",
    ])

    assert status == 0
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        f"Analyzing: {fixture_dir.resolve()}",
        "Thresholds: warn=10 | error=50 | critical=100",
        "Image: darthjee/tingle_rubycritic:0.6.0",
        "",
        "Status           Complexity  Rating  Smells  Duplication  File",
        f"{'─' * 16} {'─' * 10}  {'─' * 6}  {'─' * 6}  {'─' * 11}  {'─' * 50}",
        "🔴 ERROR               72.25  B           14            0  fixture/complex.rb",
        "⚠️  WARN              15.11  C           11           39  fixture/dup_a.rb",
        "⚠️  WARN              15.11  C           11           39  fixture/dup_b.rb",
        "✅ OK                   0.00  A            0            0  fixture/constants_only.rb",
        "✅ OK                   0.00  A            0            0  fixture/empty.rb",
        "✅ OK                   0.00  A            1            0  fixture/simple.rb",
        "⛔ PARSE                   -  -            -            -  fixture/broken.rb",
        "",
        "─" * 78,
        "Summary: 7 file(s) | 3 OK | 2 WARN | 1 ERROR | 0 CRITICAL | 1 skipped (parse error)",
        "Score: 83.23/100 (RubyCritic)",
    ]
    assert captured.err == "Warning: cannot parse fixture/broken.rb: unexpected token tSTRING\n"


def test_end_to_end_docker_calls_and_stdin(fixture_dir, capsys, docker):
    _run_status([str(fixture_dir), "--image", "img:dev"])

    fake = docker.get()
    assert fake.subcommands == ["info", "image", "run"]
    args, kwargs = fake.run_call()
    assert args[-1] == "img:dev"
    assert f"{fixture_dir.resolve()}:/src:ro" in args
    assert kwargs["input"] == "".join(f"{n}\n" for n in sorted(FIXTURE_FILES)).encode()


def test_end_to_end_single_file_mounts_parent(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(sample(
        analysed_modules=[_module("complex.rb", 72.25, "B", 2, 0)], parse_errors=[],
    )))

    status = _run_status([str(fixture_dir / "complex.rb"), "--image", "img:dev"])

    assert status == 0
    args, kwargs = docker.get().run_call()
    assert f"{fixture_dir.resolve()}:/src:ro" in args
    assert kwargs["input"] == b"complex.rb\n"
    out = capsys.readouterr().out
    assert "  complex.rb\n" in out
    assert "Summary: 1 file(s) | 1 OK | 0 WARN | 0 ERROR | 0 CRITICAL\n" in out


def test_end_to_end_default_image_from_version(fixture_dir, capsys, docker, monkeypatch, tmp_path):
    from code_check.rubycritic.constants import Constants

    version = tmp_path / "VERSION"
    version.write_text(" 9.8.7\n")
    monkeypatch.setattr(Constants, "VERSION_FILE", version)

    _run_status([str(fixture_dir)])

    assert docker.get().run_call()[0][-1] == "darthjee/tingle_rubycritic:9.8.7"
    assert "Image: darthjee/tingle_rubycritic:9.8.7" in capsys.readouterr().out


@pytest.mark.parametrize(("fail_on", "expected"), [("warn", 2), ("error", 2), ("critical", 0)])
def test_end_to_end_fail_on(fixture_dir, capsys, docker, fail_on, expected):
    status = _run_status([
        str(fixture_dir), "--image", "img", "--warn", "10", "--error", "50",
        "--critical", "100", "--fail-on", fail_on,
    ])

    assert status == expected


def test_end_to_end_fail_on_uses_hidden_rows(fixture_dir, capsys, docker):
    status = _run_status([
        str(fixture_dir), "--image", "img", "--warn", "10", "--error", "50",
        "--min-level", "critical", "--top", "1", "--fail-on", "error",
    ])

    assert status == 2
    assert "No files at or above CRITICAL." not in capsys.readouterr().out  # PARSE row shown


def test_end_to_end_parse_rows_never_fail_the_gate(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(sample(
        analysed_modules=[],
        parse_errors=[{"path": n, "message": "bad"} for n in FIXTURE_FILES],
        score=None,
    )))

    status = _run_status([str(fixture_dir), "--image", "img", "--warn", "0", "--fail-on", "warn"])

    assert status == 0
    out = capsys.readouterr().out
    assert "Summary: 7 file(s) | 0 OK | 0 WARN | 0 ERROR | 0 CRITICAL | 7 skipped" in out
    assert "Score: n/a (RubyCritic)" in out


def test_end_to_end_dropped_files_count_for_the_gate(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(sample(analysed_modules=[], parse_errors=[])))

    status = _run_status([str(fixture_dir), "--image", "img", "--warn", "0", "--fail-on", "warn"])

    assert status == 2
    assert "Summary: 7 file(s) | 0 OK | 7 WARN" in capsys.readouterr().out


def test_end_to_end_invalid_json(fixture_dir, capsys, docker):
    docker.configure(stdout="Score: 80\n", stderr=b"progress\n")

    assert _run_status([str(fixture_dir), "--image", "img"]) == 1

    err = capsys.readouterr().err
    assert err.startswith("progress\nError: could not parse the RubyCritic output from img: ")
    assert "invalid JSON: " in err


def test_end_to_end_structural_failure(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(sample(score="x")))

    assert _run_status([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err == (
        "Error: could not parse the RubyCritic output from img: unexpected score\n"
    )


def test_end_to_end_success_discards_container_stderr(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(FIXTURE_OUTPUT), stderr=b"rubycritic progress\n")

    assert _run_status([str(fixture_dir), "--image", "img"]) == 0

    assert "rubycritic progress" not in capsys.readouterr().err


def test_end_to_end_container_failure(fixture_dir, capsys, docker):
    docker.configure(run_status=1, stderr=b"boom\n")

    assert _run_status([str(fixture_dir), "--image", "img"]) == 1

    captured = capsys.readouterr()
    assert captured.err == "boom\nError: RubyCritic failed in img (exit 1)\n"
    assert "Summary:" not in captured.out


def test_end_to_end_mount_failure(fixture_dir, capsys, docker):
    docker.configure(run_status=125, stderr=b"docker: mounts denied: nope\n")

    assert _run_status([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err == (
        "docker: mounts denied: nope\n"
        f"Error: Docker could not mount {fixture_dir.resolve()}; on Docker Desktop, share it "
        "(or a parent folder) under Settings > Resources > File sharing, then retry\n"
    )


def test_end_to_end_docker_missing(fixture_dir, capsys, docker, monkeypatch):
    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: None)

    assert _run_status([str(fixture_dir), "--image", "img"]) == 1

    assert "Error: docker not found on PATH" in capsys.readouterr().err
    assert docker.get().calls == []


def test_end_to_end_daemon_down(fixture_dir, capsys, docker):
    fake = docker.configure(info=1)

    assert _run_status([str(fixture_dir), "--image", "img"]) == 1

    assert "Error: the Docker daemon is not responding" in capsys.readouterr().err
    assert fake.subcommands == ["info"]


def test_end_to_end_pull_when_missing(fixture_dir, capsys, docker):
    fake = docker.configure(stdout=json.dumps(FIXTURE_OUTPUT), inspect=1)

    assert _run_status([str(fixture_dir), "--image", "img"]) == 0

    assert fake.subcommands == ["info", "image", "pull", "run"]
    assert "Pulling img ...\n" in capsys.readouterr().err


def test_end_to_end_pull_failure(fixture_dir, capsys, docker):
    fake = docker.configure(inspect=1, pull=1)

    assert _run_status([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err.endswith("Error: could not pull image img\n")
    assert "run" not in fake.subcommands


def test_end_to_end_unsendable_name_is_skipped(fixture_dir, capsys, docker):
    (fixture_dir / "new\nline.rb").write_text("x\n")

    _run_status([str(fixture_dir), "--image", "img"])

    _args, kwargs = docker.get().run_call()
    assert b"line.rb" not in kwargs["input"]
    captured = capsys.readouterr()
    assert "Warning: skipping file with a newline in its name: 'new\\nline.rb'\n" in captured.err
    assert "Summary: 7 file(s) |" in captured.out


def _without_methods():
    data = sample(analysed_modules=FIXTURE_OUTPUT["analysed_modules"])
    del data["methods"]
    return json.dumps(data)


def test_end_to_end_missing_methods_with_details_fails(fixture_dir, capsys, docker):
    docker.configure(stdout=_without_methods())

    assert _run_status([str(fixture_dir), "--image", "img", "--details"]) == 1

    captured = capsys.readouterr()
    assert captured.err.endswith(
        "Error: the RubyCritic output from img has no per-method data; "
        "--details needs a newer tingle_rubycritic image\n"
    )
    assert "Summary:" not in captured.out


def test_end_to_end_missing_methods_without_details_is_fine(fixture_dir, capsys, docker):
    docker.configure(stdout=_without_methods())

    assert _run_status([str(fixture_dir), "--image", "img"]) == 0

    assert "Summary: 7 file(s)" in capsys.readouterr().out


def test_end_to_end_malformed_methods_fails_without_details(fixture_dir, capsys, docker):
    docker.configure(stdout=json.dumps(sample(methods="x")))

    assert _run_status([str(fixture_dir), "--image", "img"]) == 1

    assert capsys.readouterr().err == (
        "Error: could not parse the RubyCritic output from img: unexpected methods\n"
    )


def test_end_to_end_details(fixture_dir, capsys, docker, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)

    status = _run_status([
        str(fixture_dir), "--image", "img", "--warn", "10", "--error", "50", "--details", "1",
    ])

    assert status == 0
    out = capsys.readouterr().out.splitlines()
    index = out.index("🔴 ERROR               72.25  B           14            0  fixture/complex.rb")
    assert out[index + 1] == f"{'':<16} {72.25:>10.2f}  Complex#run  (fixture/complex.rb:2)"
    assert out[index + 2].startswith("⚠️  WARN")
    assert "  DupA#a  (fixture/dup_a.rb:2)" in out[index + 3]
    assert out[index + 4].endswith("fixture/dup_b.rb")


# --- file selection options --------------------------------------------------------


def test_selection_options_defaults():
    from code_check.rubycritic.constants import Constants

    assert CheckRubycritic._selection_options({}) == {
        "excludes": Constants.DEFAULT_EXCLUDES,
        "ignore": [],
        "include": [],
        "gitignore": True,
    }


def test_selection_options_from_flags():
    from code_check.rubycritic.constants import Constants

    options = {
        "exclude": " spec, ,tmp,db ",
        "no_default_excludes": False,
        "ignore": ["*_spec.rb"],
        "include": ["app/**"],
        "no_gitignore": True,
    }

    assert CheckRubycritic._selection_options(options) == {
        "excludes": [*Constants.DEFAULT_EXCLUDES, "spec", "db"],
        "ignore": ["*_spec.rb"],
        "include": ["app/**"],
        "gitignore": False,
    }


def test_selection_options_no_default_excludes():
    options = {"exclude": "spec", "no_default_excludes": True}

    assert CheckRubycritic._selection_options(options)["excludes"] == ["spec"]


def _stdin(docker):
    _args, kwargs = docker.get().run_call()
    return kwargs["input"].decode().splitlines()


def test_end_to_end_exclude_and_ignore_reflected_in_stdin(fixture_dir, capsys, docker):
    (fixture_dir / "spec").mkdir()
    (fixture_dir / "spec" / "a_spec.rb").write_text("x\n")
    (fixture_dir / "lib").mkdir()
    (fixture_dir / "lib" / "keep.rb").write_text("x\n")
    (fixture_dir / "lib" / "skip_me.rb").write_text("x\n")

    _run_status([
        str(fixture_dir), "--image", "img", "--exclude", "spec",
        "--ignore", "lib/skip_*", "--ignore", "dup_*.rb",
    ])

    expected = sorted({*FIXTURE_FILES, "lib/keep.rb"} - {"dup_a.rb", "dup_b.rb"})
    assert _stdin(docker) == expected


def test_end_to_end_include_reflected_in_stdin(fixture_dir, capsys, docker):
    _run_status([str(fixture_dir), "--image", "img", "--include", "dup_*", "--include", "*.txt"])

    assert _stdin(docker) == ["dup_a.rb", "dup_b.rb"]


def test_end_to_end_gitignore_on_by_default(fixture_dir, capsys, docker, fake_git):
    root = fixture_dir.resolve()
    fake_git["result"] = GitIgnored({root / "broken.rb"}, [])

    _run_status([str(fixture_dir), "--image", "img"])

    assert "broken.rb" not in _stdin(docker)
    assert fake_git["calls"] == [root]


def test_end_to_end_no_gitignore_skips_git(fixture_dir, capsys, docker, fake_git):
    fake_git["result"] = GitIgnored({fixture_dir.resolve() / "broken.rb"}, [])

    _run_status([str(fixture_dir), "--image", "img", "--no-gitignore"])

    assert "broken.rb" in _stdin(docker)
    assert fake_git["calls"] == []


def test_end_to_end_symlink_stdin_line_is_its_target(tmp_path, capsys, docker):
    root = tmp_path / "proj"
    (root / "lib").mkdir(parents=True)
    (root / "lib" / "real.rb").write_text("x\n")
    (root / "link.rb").symlink_to(root / "lib" / "real.rb")
    outside = tmp_path / "outside.rb"
    outside.write_text("x\n")
    (root / "out.rb").symlink_to(outside)

    _run_status([str(root), "--image", "img"])

    assert _stdin(docker) == ["lib/real.rb"]
