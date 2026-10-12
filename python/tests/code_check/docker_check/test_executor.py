"""Unit tests for code_check.docker_check.executor.DockerCheck, driven by a fake check.

No Docker, no config file outside HOME (autouse fixture in tests/code_check/conftest.py)
and no git: the fake check's hooks return canned data.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

import pytest

from code_check.config import ConfigError
from code_check.docker_check.errors import DockerCheckError
from code_check.docker_check.executor import DockerCheck
from code_check.docker_check.selection import Selection
from code_check.file_size.file_analyzer import FileAnalyzer


class FakeError(DockerCheckError):
    """The fake check's error class."""


FLAGS: list[dict] = [
    {"name": "path", "type": str, "help": "file or directory"},
    {"name": "--warn", "type": float, "default": None, "help": "warn"},
    {"name": "--error", "type": float, "default": None, "help": "error"},
    {"name": "--critical", "type": float, "default": None, "help": "critical"},
    {"name": "--top", "type": int, "default": None, "help": "top"},
    {
        "name": "--fail-on", "type": str, "choices": ["warn", "error", "critical"],
        "default": None, "help": "gate",
    },
    {"name": "--image", "type": str, "default": None, "help": "image"},
    {"name": "--exclude", "type": str, "default": None, "help": "exclude"},
    {"name": "--no-default-excludes", "action": "store_true", "help": "no defaults"},
    {"name": "--no-gitignore", "action": "store_true", "help": "no gitignore"},
    {"name": "--ignore", "type": str, "action": "append", "default": None, "help": "ignore"},
    {"name": "--include", "type": str, "action": "append", "default": None, "help": "include"},
    {"name": "--no-config", "action": "store_true", "help": "no config"},
]


class FakeCheck(DockerCheck):
    """A minimal Docker-backed check: no `details` option, canned selection and results."""

    PROG = "tingle code_check fake"
    FLAGS = FLAGS
    CONFIG_SECTION = "fake"
    SINGLE_DEFAULTS: ClassVar[dict] = {
        "warn": 10, "error": 20, "critical": 40, "top": 0, "fail_on": None, "image": None,
    }
    LIST_KEYS = ("ignore", "include")
    THRESHOLD_KEYS = ("warn", "error", "critical")
    DEFAULT_EXCLUDES: ClassVar[list[str]] = ["node_modules", "dist"]
    NO_FILES_MESSAGE = "No fake files found for analysis."
    error_class = FakeError

    lines: ClassVar[list[str]] = ["a.js"]
    scores: ClassVar[list[float]] = [5]
    calls: ClassVar[list] = []

    @staticmethod
    def validate_config(section, path):
        if not isinstance(section, dict):
            raise ConfigError(f"{path}: 'fake' must be an object")
        return section

    @classmethod
    def _select_files(cls, target, root, **kwargs):
        cls.calls.append(("select", target, root, kwargs))
        return Selection(root, list(cls.lines), [])

    @staticmethod
    def _gate_value(result):
        return result.score

    def _execute(self, options, config_file=None):
        target, root = self._resolve_target(options["path"])
        out = SimpleNamespace(CYAN="", BOLD="", RESET="", DIM="", YELLOW="")
        self._print_header(out, target, options, options["image"] or "fake:1", config_file)
        self._select(out, target, root, options)
        analyzer = FileAnalyzer(options["warn"], options["error"], options["critical"])
        results = [SimpleNamespace(score=s) for s in self.scores]
        return 2 if self._gate_failed(analyzer, results, options["fail_on"]) else 0


class DetailsCheck(FakeCheck):
    """The fake check with a `details` option."""

    SINGLE_DEFAULTS: ClassVar[dict] = {**FakeCheck.SINGLE_DEFAULTS, "details": None}


@pytest.fixture(autouse=True)
def reset_fake(monkeypatch):
    monkeypatch.setattr(FakeCheck, "lines", ["a.js"])
    monkeypatch.setattr(FakeCheck, "scores", [5])
    monkeypatch.setattr(FakeCheck, "calls", [])


def _write_config(data) -> Path:
    path = Path(os.environ["HOME"]) / ".tingle" / "code_check" / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data))
    return path


def _run(args) -> int:
    with pytest.raises(SystemExit) as exc_info:
        FakeCheck().run(args)
    return exc_info.value.code


def _cli(**overrides):
    cli = {
        "path": "p", "warn": None, "error": None, "critical": None, "top": None,
        "fail_on": None, "image": None, "exclude": None, "no_default_excludes": False,
        "no_gitignore": False, "ignore": None, "include": None, "no_config": False,
    }
    cli.update(overrides)
    return cli


# --- run: help and parse -----------------------------------------------------------


def test_no_args_prints_help_and_exits_zero(capsys):
    assert _run([]) == 0
    assert capsys.readouterr().out.startswith("usage: tingle code_check fake ")


def test_argparse_error_exits_one(tmp_path, capsys):
    assert _run([str(tmp_path), "--warn", "x"]) == 1
    assert "usage: tingle code_check fake" in capsys.readouterr().err


def test_help_exits_zero(capsys):
    assert _run(["--help"]) == 0


# --- run: full flow ----------------------------------------------------------------


def test_success_returns_without_exit(tmp_path, capsys):
    FakeCheck().run([str(tmp_path)])

    out = capsys.readouterr().out
    assert f"Analyzing: {tmp_path.resolve()}" in out
    assert "Thresholds: warn=10 | error=20 | critical=40" in out
    assert "Image: fake:1" in out


def test_no_files_prints_message_and_exits_zero(tmp_path, capsys):
    FakeCheck.lines = []

    assert _run([str(tmp_path)]) == 0
    assert "No fake files found for analysis." in capsys.readouterr().out


def test_skipped_names_are_warned(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(
        FakeCheck,
        "_select_files",
        classmethod(lambda cls, target, root, **kw: Selection(root, ["a.js"], ["skip me"])),
    )

    FakeCheck().run([str(tmp_path)])

    assert "Warning: skip me" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("score", "fail_on", "status"),
    [(5, "warn", None), (10, "warn", 2), (25, "error", 2), (25, "critical", None)],
)
def test_fail_on_gate_uses_gate_value(tmp_path, score, fail_on, status):
    FakeCheck.scores = [1, score]

    if status is None:
        FakeCheck().run([str(tmp_path), "--fail-on", fail_on])
    else:
        assert _run([str(tmp_path), "--fail-on", fail_on]) == status


def test_gate_without_fail_on_never_fails():
    analyzer = FileAnalyzer(1, 2, 3)

    assert FakeCheck._gate_failed(analyzer, [SimpleNamespace(score=99)], None) is False


def test_error_class_prints_error_and_exits_one(tmp_path, capsys):
    assert _run([str(tmp_path / "missing")]) == 1
    assert capsys.readouterr().err == f"Error: path not found: {(tmp_path / 'missing')}\n"


def test_validation_error_exits_one(tmp_path, capsys):
    assert _run([str(tmp_path), "--warn", "-1"]) == 1
    assert capsys.readouterr().err == "Error: --warn must be a number >= 0\n"


# --- config ------------------------------------------------------------------------


def test_config_is_loaded_and_shown(tmp_path, capsys):
    path = _write_config({"fake": {"warn": 3}})

    FakeCheck().run([str(tmp_path)])

    out = capsys.readouterr().out
    assert "Thresholds: warn=3 | error=20 | critical=40" in out
    assert f"Config: {path}" in out


def test_no_config_skips_the_file(tmp_path, capsys):
    _write_config({"fake": {"warn": 3}})

    FakeCheck().run([str(tmp_path), "--no-config"])

    out = capsys.readouterr().out
    assert "warn=10" in out
    assert "Config:" not in out


def test_load_config_without_file_or_section():
    assert FakeCheck._load_config(False) == ({}, None)
    _write_config({"other": {}})
    assert FakeCheck._load_config(False) == ({}, None)
    assert FakeCheck._load_config(True) == ({}, None)


def test_invalid_config_prints_error_and_exits_one(tmp_path, capsys):
    path = _write_config({"fake": []})

    assert _run([str(tmp_path)]) == 1
    assert capsys.readouterr().err == f"Error: {path}: 'fake' must be an object\n"


def test_load_section_hook_is_used(monkeypatch):
    seen = []
    monkeypatch.setattr(
        FakeCheck, "_load_section",
        staticmethod(lambda name, path=None: seen.append(name) or {"top": 1}),
    )

    config, _path = FakeCheck._load_config(False)

    assert config == {"top": 1}
    assert seen == ["fake"]


def test_default_hooks_are_abstract():
    with pytest.raises(NotImplementedError):
        DockerCheck.validate_config({}, Path("x"))
    with pytest.raises(NotImplementedError):
        DockerCheck._gate_value(None)
    with pytest.raises(NotImplementedError):
        DockerCheck()._execute({})


def test_default_select_files_hook_uses_extensions(tmp_path, monkeypatch):
    from code_check.file_size.git_ignore import GitIgnore

    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(lambda root: None))
    (tmp_path / "a.go").write_text("x")
    (tmp_path / "b.txt").write_text("x")

    selection = DockerCheck._select_files(tmp_path, tmp_path, extensions=[".go"], excludes=[])

    assert selection.lines == ["a.go"]


# --- merge -------------------------------------------------------------------------


def test_merge_order_cli_over_config_over_defaults():
    merged = FakeCheck._merge(_cli(warn=1.0), {"warn": 2, "error": 3, "image": None})

    assert merged["warn"] == 1.0
    assert merged["error"] == 3
    assert merged["critical"] == 40
    assert merged["image"] is None


def test_merge_lists_concatenate_and_dedup():
    merged = FakeCheck._merge(
        _cli(ignore=["b", "c"], include=["x"], exclude="d,e"),
        {"ignore": ["a", "b"], "exclude": ["d", "z"]},
    )

    assert merged["ignore"] == ["a", "b", "c"]
    assert merged["include"] == ["x"]
    assert merged["exclude"] == ["d", "z", "e"]


def test_merge_negative_flags_win_over_config():
    merged = FakeCheck._merge(
        _cli(no_default_excludes=True, no_gitignore=True),
        {"no_default_excludes": False, "gitignore": True},
    )
    assert merged["no_default_excludes"] is True
    assert merged["gitignore"] is False

    merged = FakeCheck._merge(_cli(), {"no_default_excludes": True, "gitignore": False})
    assert merged["no_default_excludes"] is True
    assert merged["gitignore"] is False


def test_selection_options_use_default_excludes():
    options = {"exclude": ["x"], "no_default_excludes": False}
    assert FakeCheck._selection_options(options) == {
        "excludes": ["node_modules", "dist", "x"],
        "ignore": [],
        "include": [],
        "gitignore": True,
    }
    options["no_default_excludes"] = True
    assert FakeCheck._selection_options(options)["excludes"] == ["x"]


def test_select_passes_selection_options(tmp_path):
    out = SimpleNamespace(YELLOW="", RESET="")

    FakeCheck._select(out, tmp_path, tmp_path, {"ignore": ["g"], "gitignore": False})

    assert FakeCheck.calls == [(
        "select", tmp_path, tmp_path,
        {"excludes": ["node_modules", "dist"], "ignore": ["g"], "include": [], "gitignore": False},
    )]


# --- validate ----------------------------------------------------------------------


def _options(**overrides):
    options = {"warn": 1, "error": 2, "critical": 3, "top": 0, "image": None}
    options.update(overrides)
    return options


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"error": -1}, "--error must be a number >= 0"),
        ({"critical": float("nan")}, "--critical must be a number >= 0"),
        ({"top": -1}, "--top must be an integer >= 0"),
        ({"image": ""}, "--image must not be empty"),
    ],
)
def test_validate_rejects(overrides, message):
    with pytest.raises(FakeError) as exc_info:
        FakeCheck._validate(_options(**overrides))

    assert exc_info.value.message == message


def test_validate_ignores_details_without_details_option():
    options = _options(details=-1)

    assert FakeCheck._validate(options) is options


def test_validate_checks_details_with_details_option():
    assert DetailsCheck._validate(_options(details=None))["details"] is None
    assert DetailsCheck._validate(_options(details=0))["details"] == 0
    with pytest.raises(FakeError) as exc_info:
        DetailsCheck._validate(_options(details=-1))

    assert exc_info.value.message == "--details must be an integer >= 0"


# --- resolve_target ----------------------------------------------------------------


def test_resolve_target_directory_and_file(tmp_path):
    (tmp_path / "a.js").write_text("x")

    assert FakeCheck._resolve_target(str(tmp_path)) == (tmp_path.resolve(), tmp_path.resolve())
    target, root = FakeCheck._resolve_target(str(tmp_path / "a.js"))
    assert target == (tmp_path / "a.js").resolve()
    assert root == tmp_path.resolve()


def test_resolve_target_missing(tmp_path):
    with pytest.raises(FakeError) as exc_info:
        FakeCheck._resolve_target(str(tmp_path / "nope"))

    assert exc_info.value.message == f"path not found: {tmp_path.resolve() / 'nope'}"


def test_resolve_target_unreadable(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "access", lambda path, mode: False)

    with pytest.raises(FakeError) as exc_info:
        FakeCheck._resolve_target(str(tmp_path))

    assert exc_info.value.message == f"path not readable: {tmp_path.resolve()}"


def test_resolve_target_colon_in_root(tmp_path):
    root = tmp_path / "a:b"
    root.mkdir()

    with pytest.raises(FakeError) as exc_info:
        FakeCheck._resolve_target(str(root))

    assert exc_info.value.message == (
        f"cannot mount {root.resolve()}: Docker volume paths cannot contain ':'"
    )


# --- header ------------------------------------------------------------------------


def test_print_header_without_config(tmp_path, capsys):
    out = SimpleNamespace(CYAN="", BOLD="", RESET="", DIM="")

    FakeCheck._print_header(out, tmp_path, _options(warn=1.5), "img:1")

    assert capsys.readouterr().out == (
        f"Analyzing: {tmp_path}\n"
        "Thresholds: warn=1.5 | error=2 | critical=3\n"
        "Image: img:1\n"
        "\n"
    )
