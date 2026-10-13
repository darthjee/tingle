"""Tests for how CheckJsComplexity applies ~/.tingle/code_check/config.json (issue #322)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from code_check.file_size.git_ignore import GitIgnore
from code_check.js_complexity import executor
from code_check.js_complexity.constants import Constants
from code_check.js_complexity.executor import CheckJsComplexity
from code_check.js_complexity.selection import Selection
from code_check.palette import Colors, Palette

NO_FILES = "No JavaScript/TypeScript files found for analysis."
DEFAULT_THRESHOLDS = "Thresholds: warn=50 | error=60 | critical=75"


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
        CheckJsComplexity().run(args)
    except SystemExit as exc:
        return exc.code
    return 0


def _cli(**overrides) -> dict:
    cli = {"path": "x", "warn": None, "error": None, "critical": None, "top": None,
           "min_level": None, "fail_on": None, "image": None,
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
    path = _write_config({"js_complexity": {"warn": 10, "error": 20.5, "critical": 30,
                                            "image": "img:config"}})

    assert _run([str(project)]) == 0

    assert capsys.readouterr().out.splitlines() == [
        f"Analyzing: {project.resolve()}",
        "Thresholds: warn=10 | error=20.5 | critical=30",
        "Image: img:config",
        f"Config: {path}",
        "",
        NO_FILES,
    ]
    assert no_docker == []


def test_cli_overrides_config_single_values(project, capsys, no_docker):
    _write_config({"js_complexity": {"warn": 10, "error": 20, "critical": 30,
                                     "image": "img:config"}})

    assert _run([str(project), "--warn", "40", "--critical", "90", "--image", "img:cli"]) == 0

    out = capsys.readouterr().out
    assert "Thresholds: warn=40 | error=20 | critical=90" in out
    assert "Image: img:cli" in out


@pytest.mark.parametrize(
    ("key", "default", "config_value", "cli_value"),
    [
        ("warn", 50, 10, 5.0),
        ("error", 60, 20.5, 7.0),
        ("critical", 75, 30, 9.0),
        ("top", 0, 3, 1),
        ("fail_on", None, "error", "critical"),
        ("min_level", "ok", "warn", "error"),
        ("image", None, "img:config", "img:cli"),
    ],
)
def test_single_value_precedence(key, default, config_value, cli_value):
    assert CheckJsComplexity._merge(_cli(), {})[key] == default
    assert CheckJsComplexity._merge(_cli(), {key: config_value})[key] == config_value
    merged = CheckJsComplexity._merge(_cli(**{key: cli_value}), {key: config_value})
    assert merged[key] == cli_value


def test_cli_zero_top_wins_over_config():
    assert CheckJsComplexity._merge(_cli(top=0), {"top": 5})["top"] == 0


def test_config_null_means_unset():
    merged = CheckJsComplexity._merge(_cli(), {"fail_on": None})

    assert merged["fail_on"] is None


def test_config_fail_on_gates_the_run(monkeypatch):
    _write_config({"js_complexity": {"fail_on": "warn"}})
    seen = {}

    def fake_execute(self, options, config_file=None):
        seen.update(options=options, config_file=config_file)
        return 0

    monkeypatch.setattr(CheckJsComplexity, "_execute", fake_execute)

    assert _run(["src"]) == 0
    assert seen["options"]["fail_on"] == "warn"
    assert seen["config_file"] == _config_path()


# --- lists ------------------------------------------------------------------------


def test_lists_are_concatenated_config_first_and_deduplicated():
    config = {"exclude": ["generated", "test"], "ignore": ["a/**", "b/**"],
              "include": ["src/**"]}
    cli = _cli(exclude=" test, tmp2 ,generated", ignore=["b/**", "c/**"],
               include=["lib/**", "src/**"])

    merged = CheckJsComplexity._merge(cli, config)

    assert merged["exclude"] == ["generated", "test", "tmp2"]
    assert merged["ignore"] == ["a/**", "b/**", "c/**"]
    assert merged["include"] == ["src/**", "lib/**"]


def test_config_lists_reach_file_selection(project, capsys, selection_spy):
    _write_config({"js_complexity": {"exclude": ["generated"], "ignore": ["**/*.test.ts"],
                                     "include": ["src/**"], "image": "img"}})

    assert _run([str(project), "--exclude", "fixtures", "--ignore", "**/legacy/**"]) == 0

    assert selection_spy == {
        "excludes": [*Constants.DEFAULT_EXCLUDES, "generated", "fixtures"],
        "ignore": ["**/*.test.ts", "**/legacy/**"],
        "include": ["src/**"],
        "gitignore": True,
        "skip_minified": True,
    }


# --- booleans ---------------------------------------------------------------------


def test_config_no_default_excludes_drops_defaults(project, selection_spy):
    _write_config({"js_complexity": {"no_default_excludes": True, "exclude": ["generated"],
                                     "image": "img"}})

    assert _run([str(project)]) == 0

    assert selection_spy["excludes"] == ["generated"]


def test_cli_no_default_excludes_wins_over_config(project, selection_spy):
    _write_config({"js_complexity": {"no_default_excludes": False, "image": "img"}})

    assert _run([str(project), "--no-default-excludes", "--exclude", "x"]) == 0

    assert selection_spy["excludes"] == ["x"]


def test_config_gitignore_false_turns_it_off(project, selection_spy):
    _write_config({"js_complexity": {"gitignore": False, "image": "img"}})

    assert _run([str(project)]) == 0

    assert selection_spy["gitignore"] is False


def test_cli_no_gitignore_wins_over_config(project, selection_spy):
    _write_config({"js_complexity": {"gitignore": True, "image": "img"}})

    assert _run([str(project), "--no-gitignore"]) == 0

    assert selection_spy["gitignore"] is False


def test_boolean_merge_defaults():
    merged = CheckJsComplexity._merge(_cli(), {})

    assert merged["no_default_excludes"] is False
    assert merged["gitignore"] is True


# --- --no-config ------------------------------------------------------------------


def test_no_config_ignores_a_broken_file(project, capsys, no_docker):
    _write_config("{not json")

    assert _run([str(project), "--no-config", "--image", "img"]) == 0

    captured = capsys.readouterr()
    assert "Config:" not in captured.out
    assert DEFAULT_THRESHOLDS in captured.out
    assert captured.err == ""


def test_no_config_ignores_a_valid_section(project, capsys, no_docker):
    _write_config({"js_complexity": {"warn": 1, "image": "img:config"}})

    assert _run([str(project), "--no-config", "--image", "img"]) == 0

    out = capsys.readouterr().out
    assert "warn=50" in out
    assert "Image: img\n" in out
    assert "Config:" not in out


def test_load_config_no_config_does_not_read_the_file(monkeypatch):
    monkeypatch.setattr(executor, "load_section", lambda *a, **k: pytest.fail("file read"))

    assert CheckJsComplexity._load_config(True) == ({}, None)


# --- missing file, missing section, empty section ---------------------------------


def test_missing_file_uses_defaults_without_config_line(project, capsys, no_docker):
    assert not _config_path().exists()

    assert _run([str(project), "--image", "img"]) == 0

    out = capsys.readouterr().out
    assert "Config:" not in out
    assert DEFAULT_THRESHOLDS in out


@pytest.mark.parametrize(
    "content",
    [
        {"file_size": {"warn": 1}},
        {"rubycritic": {"warn": 1}},
        {"file_size": {"warn": 1, "ext": [".py"]}, "rubycritic": {"warn": 1, "details": 3}},
    ],
)
def test_other_sections_only_use_defaults_without_config_line(project, capsys, no_docker,
                                                              content):
    _write_config(content)

    assert _run([str(project), "--image", "img"]) == 0

    captured = capsys.readouterr()
    assert "Config:" not in captured.out
    assert DEFAULT_THRESHOLDS in captured.out
    assert captured.err == ""


def test_invalid_other_section_is_ignored(project, capsys, no_docker):
    _write_config({"rubycritic": {"warn": -1, "bogus": 1}, "file_size": []})

    assert _run([str(project), "--image", "img"]) == 0

    assert capsys.readouterr().err == ""


def test_empty_section_prints_config_line(project, capsys, no_docker):
    path = _write_config({"js_complexity": {}})

    assert _run([str(project), "--image", "img"]) == 0

    out = capsys.readouterr().out
    assert f"Config: {path}\n" in out
    assert "warn=50" in out


def test_load_config_returns_section_and_path():
    path = _write_config({"js_complexity": {"top": 2}})

    assert CheckJsComplexity._load_config(False) == ({"top": 2}, path)


# --- errors -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        ("[1, 2]", "top level must be an object"),
        ({"js_complexity": []}, "'js_complexity' must be an object"),
        ({"js_complexity": {"ext": [".js"]}}, "unknown key 'ext'"),
        ({"js_complexity": {"details": -1}}, "'details' must be an integer >= 0 or null"),
        ({"js_complexity": {"bogus": 1}}, "unknown key 'bogus'"),
        ({"js_complexity": {"warn": -1}}, "'warn' must be a number >= 0"),
        ({"js_complexity": {"warn": True}}, "'warn' must be a number >= 0"),
        ('{"js_complexity": {"critical": NaN}}', "'critical' must be a number >= 0"),
        ({"js_complexity": {"top": 1.5}}, "'top' must be an integer >= 0"),
        ({"js_complexity": {"image": " "}}, "'image' must be a non-empty string"),
        ({"js_complexity": {"ignore": "**/*.ts"}}, "'ignore' must be a list of strings"),
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


def test_unreadable_config_exits_one(project, capsys, no_docker):
    path = _config_path()
    path.mkdir(parents=True)  # a directory cannot be read as a file

    assert _run([str(project), "--image", "img"]) == 1

    err = capsys.readouterr().err.strip()
    assert err.startswith(f"Error: {path}: cannot read file: ")
    assert no_docker == []


def test_config_error_does_not_select_files(project, capsys, monkeypatch):
    monkeypatch.setattr(executor, "select_files", lambda *a, **k: pytest.fail("selected"))
    _write_config({"js_complexity": {"warn": -1}})

    assert _run([str(project)]) == 1


def test_config_error_is_red(project, capsys, monkeypatch):
    monkeypatch.setattr(Palette, "supports_color", staticmethod(lambda stream: True))
    path = _write_config({"js_complexity": {"ext": []}})

    assert _run([str(project)]) == 1

    assert capsys.readouterr().err == (
        f"{Colors.RED}Error: {path}: unknown key 'ext'{Colors.RESET}\n"
    )


def test_cli_validation_still_applies_after_merge(tmp_path, capsys):
    _write_config({"js_complexity": {"warn": 10}})

    assert _run([str(tmp_path / "missing"), "--top", "-1"]) == 1

    assert capsys.readouterr().err.strip() == "Error: --top must be an integer >= 0"


# --- image and VERSION ------------------------------------------------------------


def test_config_image_avoids_the_version_read(project, capsys, monkeypatch, no_docker):
    monkeypatch.setattr(Constants, "VERSION_FILE", project / "no-such-VERSION")
    _write_config({"js_complexity": {"image": "darthjee/tingle_js_complexity:0.9.0"}})

    assert _run([str(project)]) == 0

    captured = capsys.readouterr()
    assert "Image: darthjee/tingle_js_complexity:0.9.0" in captured.out
    assert captured.err == ""


def test_missing_version_without_image_still_fails(project, capsys, monkeypatch):
    monkeypatch.setattr(Constants, "VERSION_FILE", project / "no-such-VERSION")
    _write_config({"js_complexity": {"warn": 10}})

    assert _run([str(project)]) == 1

    assert "cannot read the tingle version" in capsys.readouterr().err


# --- header -----------------------------------------------------------------------


def test_print_header_with_config(tmp_path, capsys):
    config = tmp_path / "config.json"

    CheckJsComplexity._print_header(
        Palette(), tmp_path, {"warn": 1, "error": 2, "critical": 3}, "img:1", config
    )

    assert capsys.readouterr().out == (
        f"Analyzing: {tmp_path}\n"
        "Thresholds: warn=1 | error=2 | critical=3\n"
        "Image: img:1\n"
        f"Config: {config}\n"
        "\n"
    )


def test_print_header_without_config(tmp_path, capsys):
    CheckJsComplexity._print_header(
        Palette(), tmp_path, {"warn": 1, "error": 2, "critical": 3}, "img:1"
    )

    assert "Config:" not in capsys.readouterr().out
