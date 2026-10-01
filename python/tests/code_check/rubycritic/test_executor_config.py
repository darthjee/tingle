"""Tests for how CheckRubycritic applies ~/.tingle/code_check/config.json (issue #297)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from code_check.file_size.git_ignore import GitIgnore
from code_check.palette import Colors, Palette
from code_check.rubycritic import executor
from code_check.rubycritic.constants import Constants
from code_check.rubycritic.executor import CheckRubycritic
from code_check.rubycritic.selection import Selection


def _config_path() -> Path:
    # HOME is pointed at a fresh temp dir by the autouse fixture in conftest.py.
    return Path.home() / ".tingle" / "code_check" / "config.json"


def _write_config(content) -> Path:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if isinstance(content, str) else json.dumps(content))
    return path


def _run(args) -> int:
    try:
        CheckRubycritic().run(args)
    except SystemExit as exc:
        return exc.code
    return 0


def _cli(**overrides) -> dict:
    cli = {"path": "x", "warn": None, "error": None, "critical": None, "top": None,
           "min_level": None, "fail_on": None, "details": None, "image": None,
           "exclude": None, "no_default_excludes": False, "no_gitignore": False,
           "ignore": None, "include": None, "no_config": False}
    cli.update(overrides)
    return cli


@pytest.fixture(autouse=True)
def fake_git(monkeypatch):
    """Stub GitIgnore.ignored_paths so no real git runs."""
    monkeypatch.setattr(GitIgnore, "ignored_paths", staticmethod(lambda root: None))


@pytest.fixture
def no_docker(monkeypatch):
    """Record any command lookup or run (none is expected)."""
    import shutil
    import subprocess

    calls = []
    monkeypatch.setattr(shutil, "which", lambda *a, **k: calls.append(("which", a)))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: calls.append(("run", a)))
    return calls


@pytest.fixture
def selection_spy(monkeypatch):
    """Replace select_files with a spy returning no files (so the run exits 0)."""
    seen = {}

    def fake_select_files(target, root, **kwargs):
        seen.update(kwargs)
        return Selection(root, [], [])

    monkeypatch.setattr(executor, "select_files", fake_select_files)
    return seen


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    return root


# --- single values: default < config < CLI ----------------------------------------


def test_config_thresholds_and_image_apply(project, capsys, no_docker):
    path = _write_config({"rubycritic": {"warn": 10, "error": 20.5, "critical": 30,
                                         "image": "img:config"}})

    assert _run([str(project)]) == 0

    assert capsys.readouterr().out.splitlines() == [
        f"Analyzing: {project.resolve()}",
        "Thresholds: warn=10 | error=20.5 | critical=30",
        "Image: img:config",
        f"Config: {path}",
        "",
        "No Ruby files found for analysis.",
    ]
    assert no_docker == []


def test_cli_overrides_config_single_values(project, capsys, no_docker):
    _write_config({"rubycritic": {"warn": 10, "error": 20, "critical": 30,
                                  "image": "img:config"}})

    assert _run([str(project), "--warn", "40", "--critical", "600", "--image", "img:cli"]) == 0

    out = capsys.readouterr().out
    assert "Thresholds: warn=40 | error=20 | critical=600" in out
    assert "Image: img:cli" in out


@pytest.mark.parametrize(
    ("key", "default", "config_value", "cli_key", "cli_value"),
    [
        ("warn", 100, 10, "warn", 5.0),
        ("error", 200, 20.5, "error", 7.0),
        ("critical", 400, 30, "critical", 9.0),
        ("top", 0, 3, "top", 1),
        ("fail_on", None, "error", "fail_on", "critical"),
        ("min_level", "ok", "warn", "min_level", "error"),
        ("image", None, "img:config", "image", "img:cli"),
        ("details", None, 5, "details", 2),
    ],
)
def test_single_value_precedence(key, default, config_value, cli_key, cli_value):
    assert CheckRubycritic._merge(_cli(), {})[key] == default
    assert CheckRubycritic._merge(_cli(), {key: config_value})[key] == config_value
    merged = CheckRubycritic._merge(_cli(**{cli_key: cli_value}), {key: config_value})
    assert merged[key] == cli_value


def test_config_details_zero_means_all_methods():
    assert CheckRubycritic._merge(_cli(), {"details": 0})["details"] == 0


def test_cli_details_zero_wins_over_config():
    assert CheckRubycritic._merge(_cli(details=0), {"details": 5})["details"] == 0


def test_config_null_means_unset():
    merged = CheckRubycritic._merge(_cli(), {"fail_on": None, "details": None})

    assert merged["fail_on"] is None
    assert merged["details"] is None


def test_config_fail_on_gates_the_run(monkeypatch):
    _write_config({"rubycritic": {"fail_on": "warn"}})
    seen = {}

    def fake_execute(self, options, config_file=None):
        seen.update(options=options, config_file=config_file)
        return 0

    monkeypatch.setattr(CheckRubycritic, "_execute", fake_execute)

    assert _run(["app"]) == 0
    assert seen["options"]["fail_on"] == "warn"
    assert seen["config_file"] == _config_path()


# --- lists ------------------------------------------------------------------------


def test_lists_are_concatenated_config_first_and_deduplicated():
    config = {"exclude": ["db", "spec"], "ignore": ["a/**", "b/**"], "include": ["app/**"]}
    cli = _cli(exclude=" spec, tmp2 ,db", ignore=["b/**", "c/**"], include=["lib/**", "app/**"])

    merged = CheckRubycritic._merge(cli, config)

    assert merged["exclude"] == ["db", "spec", "tmp2"]
    assert merged["ignore"] == ["a/**", "b/**", "c/**"]
    assert merged["include"] == ["app/**", "lib/**"]


def test_config_lists_reach_file_selection(project, capsys, selection_spy):
    _write_config({"rubycritic": {"exclude": ["db"], "ignore": ["spec/fixtures/**"],
                                  "include": ["app/**"], "image": "img"}})

    assert _run([str(project), "--exclude", "tmp2", "--ignore", "**/legacy/**"]) == 0

    assert selection_spy == {
        "excludes": [*Constants.DEFAULT_EXCLUDES, "db", "tmp2"],
        "ignore": ["spec/fixtures/**", "**/legacy/**"],
        "include": ["app/**"],
        "gitignore": True,
    }


# --- booleans ---------------------------------------------------------------------


def test_config_no_default_excludes_drops_defaults(project, selection_spy):
    _write_config({"rubycritic": {"no_default_excludes": True, "exclude": ["db"],
                                  "image": "img"}})

    assert _run([str(project)]) == 0

    assert selection_spy["excludes"] == ["db"]


def test_cli_no_default_excludes_wins_over_config(project, selection_spy):
    _write_config({"rubycritic": {"no_default_excludes": False, "image": "img"}})

    assert _run([str(project), "--no-default-excludes", "--exclude", "x"]) == 0

    assert selection_spy["excludes"] == ["x"]


def test_config_gitignore_false_turns_it_off(project, selection_spy):
    _write_config({"rubycritic": {"gitignore": False, "image": "img"}})

    assert _run([str(project)]) == 0

    assert selection_spy["gitignore"] is False


def test_cli_no_gitignore_wins_over_config(project, selection_spy):
    _write_config({"rubycritic": {"gitignore": True, "image": "img"}})

    assert _run([str(project), "--no-gitignore"]) == 0

    assert selection_spy["gitignore"] is False


def test_boolean_merge_defaults():
    merged = CheckRubycritic._merge(_cli(), {})

    assert merged["no_default_excludes"] is False
    assert merged["gitignore"] is True


# --- --no-config ------------------------------------------------------------------


def test_no_config_ignores_a_broken_file(project, capsys, no_docker):
    _write_config("{not json")

    assert _run([str(project), "--no-config", "--image", "img"]) == 0

    captured = capsys.readouterr()
    assert "Config:" not in captured.out
    assert "Thresholds: warn=100 | error=200 | critical=400" in captured.out
    assert captured.err == ""


def test_no_config_ignores_a_valid_section(project, capsys, no_docker):
    _write_config({"rubycritic": {"warn": 1, "image": "img:config"}})

    assert _run([str(project), "--no-config", "--image", "img"]) == 0

    out = capsys.readouterr().out
    assert "warn=100" in out
    assert "Image: img\n" in out
    assert "Config:" not in out


def test_load_config_no_config_does_not_read_the_file(monkeypatch):
    monkeypatch.setattr(executor, "load_section", lambda *a, **k: pytest.fail("file read"))

    assert CheckRubycritic._load_config(True) == ({}, None)


# --- missing file, missing section, empty section ---------------------------------


def test_missing_file_uses_defaults_without_config_line(project, capsys, no_docker):
    assert not _config_path().exists()

    assert _run([str(project), "--image", "img"]) == 0

    out = capsys.readouterr().out
    assert "Config:" not in out
    assert "Thresholds: warn=100 | error=200 | critical=400" in out


def test_missing_section_uses_defaults_without_config_line(project, capsys, no_docker):
    _write_config({"file_size": {"warn": 1}})

    assert _run([str(project), "--image", "img"]) == 0

    out = capsys.readouterr().out
    assert "Config:" not in out
    assert "warn=100" in out


def test_empty_section_prints_config_line(project, capsys, no_docker):
    path = _write_config({"rubycritic": {}})

    assert _run([str(project), "--image", "img"]) == 0

    out = capsys.readouterr().out
    assert f"Config: {path}\n" in out
    assert "warn=100" in out


def test_load_config_returns_section_and_path():
    path = _write_config({"rubycritic": {"top": 2}})

    assert CheckRubycritic._load_config(False) == ({"top": 2}, path)


# --- errors -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        ("[1, 2]", "top level must be an object"),
        ({"rubycritic": []}, "'rubycritic' must be an object"),
        ({"rubycritic": {"ext": [".rb"]}}, "unknown key 'ext'"),
        ({"rubycritic": {"warn": -1}}, "'warn' must be a number >= 0"),
        ({"rubycritic": {"warn": True}}, "'warn' must be a number >= 0"),
        ('{"rubycritic": {"critical": NaN}}', "'critical' must be a number >= 0"),
        ({"rubycritic": {"image": " "}}, "'image' must be a non-empty string"),
        ({"rubycritic": {"details": -2}}, "'details' must be an integer >= 0 or null"),
    ],
)
def test_config_errors_exit_one_before_anything_else(tmp_path, capsys, no_docker, content, reason):
    path = _write_config(content)
    missing = tmp_path / "missing"

    # A missing path would be another error: the config is checked first.
    assert _run([str(missing)]) == 1

    captured = capsys.readouterr()
    assert captured.err.strip() == f"Error: {path}: {reason}"
    assert captured.out == ""
    assert no_docker == []


def test_invalid_json_exits_one(project, capsys, no_docker):
    path = _write_config("{not json")

    assert _run([str(project), "--image", "img"]) == 1

    err = capsys.readouterr().err.strip()
    assert err.startswith(f"Error: {path}: invalid JSON: ")
    assert no_docker == []


def test_config_error_is_red(project, capsys, monkeypatch):
    monkeypatch.setattr(Palette, "supports_color", staticmethod(lambda stream: True))
    path = _write_config({"rubycritic": {"ext": []}})

    assert _run([str(project)]) == 1

    assert capsys.readouterr().err == (
        f"{Colors.RED}Error: {path}: unknown key 'ext'{Colors.RESET}\n"
    )


def test_cli_validation_still_applies_after_merge(tmp_path, capsys):
    _write_config({"rubycritic": {"warn": 10}})

    assert _run([str(tmp_path / "missing"), "--top", "-1"]) == 1

    assert capsys.readouterr().err.strip() == "Error: --top must be an integer >= 0"


# --- image and VERSION ------------------------------------------------------------


def test_config_image_avoids_the_version_read(project, capsys, monkeypatch, no_docker):
    monkeypatch.setattr(Constants, "VERSION_FILE", project / "no-such-VERSION")
    _write_config({"rubycritic": {"image": "darthjee/tingle_rubycritic:0.6.0"}})

    assert _run([str(project)]) == 0

    captured = capsys.readouterr()
    assert "Image: darthjee/tingle_rubycritic:0.6.0" in captured.out
    assert captured.err == ""


def test_missing_version_without_image_still_fails(project, capsys, monkeypatch):
    missing = project / "no-such-VERSION"
    monkeypatch.setattr(Constants, "VERSION_FILE", missing)
    _write_config({"rubycritic": {"warn": 10}})

    assert _run([str(project)]) == 1

    assert "cannot read the tingle version" in capsys.readouterr().err


# --- header -----------------------------------------------------------------------


def test_print_header_with_config(tmp_path, capsys):
    config = tmp_path / "config.json"

    CheckRubycritic._print_header(
        Palette(), tmp_path, {"warn": 1, "error": 2, "critical": 3}, "img:1", config
    )

    assert capsys.readouterr().out == (
        f"Analyzing: {tmp_path}\n"
        "Thresholds: warn=1 | error=2 | critical=3\n"
        "Image: img:1\n"
        f"Config: {config}\n"
        "\n"
    )
