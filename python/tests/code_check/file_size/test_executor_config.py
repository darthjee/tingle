"""Tests for how CheckFileSize applies ~/.tingle/code_check/config.json (issue #253)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from check_file_size.constants import Constants
from check_file_size.executor import CheckFileSize
from check_file_size.file_collector import FileCollector


def _config_path() -> Path:
    # HOME is pointed at a fresh temp dir by the autouse fixture in conftest.py.
    return Path.home() / ".tingle" / "code_check" / "config.json"


def _write_config(content) -> Path:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if isinstance(content, str) else json.dumps(content))
    return path


def _spy_collector(monkeypatch) -> dict:
    """Record the arguments FileCollector is built with."""
    seen = {}
    real_init = FileCollector.__init__

    def spy_init(self, excludes, extensions, **kwargs):
        seen.update(kwargs, excludes=excludes, extensions=extensions)
        real_init(self, excludes, extensions, **kwargs)

    monkeypatch.setattr(FileCollector, "__init__", spy_init)
    return seen


def _project(root: Path) -> Path:
    """Build files with 5, 50 and 500 lines."""
    for name, lines in (("small.py", 5), ("mid.py", 50), ("big.js", 500)):
        (root / name).write_text("\n".join("x" for _ in range(lines)))
    return root


# --- single values --------------------------------------------------------------


def test_config_thresholds_apply(tmp_path, capsys):
    _write_config({"check_file_size": {"warn": 10, "error": 20, "critical": 30}})

    CheckFileSize().run([str(_project(tmp_path))])

    out = capsys.readouterr().out
    assert "Thresholds: warn=10 | error=20 | critical=30" in out
    assert "1 OK" in out
    assert "2 CRITICAL" in out


def test_cli_overrides_config_single_values(tmp_path, capsys):
    _write_config({"check_file_size": {"warn": 10, "error": 20, "critical": 30}})

    CheckFileSize().run([str(_project(tmp_path)), "--warn", "40", "--critical", "600"])

    assert "Thresholds: warn=40 | error=20 | critical=600" in capsys.readouterr().out


def test_config_top_and_min_level_apply(tmp_path, capsys):
    _write_config({"check_file_size": {"warn": 10, "min_level": "warn", "top": 1}})

    CheckFileSize().run([str(_project(tmp_path))])

    out = capsys.readouterr().out
    assert "big.js" in out
    assert "mid.py" not in out
    assert "small.py" not in out


def test_cli_top_and_min_level_override_config(tmp_path, capsys):
    _write_config({"check_file_size": {"warn": 10, "min_level": "critical", "top": 1}})

    CheckFileSize().run([str(_project(tmp_path)), "--min-level", "ok", "--top", "0"])

    out = capsys.readouterr().out
    assert all(name in out for name in ("big.js", "mid.py", "small.py"))


def test_config_fail_on_gates_exit_status(tmp_path, capsys):
    _write_config({"check_file_size": {"fail_on": "error"}})

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(_project(tmp_path))])

    assert exc_info.value.code == 2


def test_cli_fail_on_overrides_config(tmp_path, capsys):
    _write_config({"check_file_size": {"fail_on": "warn"}})

    # big.js has 500 lines: reaches error but not critical.
    CheckFileSize().run([str(_project(tmp_path)), "--fail-on", "critical"])

    assert "big.js" in capsys.readouterr().out


def test_config_fail_on_null_means_no_gate(tmp_path, capsys):
    _write_config({"check_file_size": {"fail_on": None}})

    CheckFileSize().run([str(_project(tmp_path))])

    assert "big.js" in capsys.readouterr().out


# --- lists ----------------------------------------------------------------------


def test_config_and_cli_lists_are_merged_and_deduplicated(tmp_path, capsys, monkeypatch):
    _project(tmp_path)
    _write_config({"check_file_size": {
        "exclude": ["fixtures", "tmp"],
        "ignore": ["*.lock", "a"],
        "include": ["*.py"],
        "ext": [".py"],
    }})
    seen = _spy_collector(monkeypatch)

    CheckFileSize().run([
        str(tmp_path),
        "--exclude", "tmp,extra",
        "--ignore", "a", "--ignore", "b",
        "--include", "*.js",
        "--ext", ".js", "--ext", ".py",
    ])

    assert seen["excludes"] == [*Constants.DEFAULT_EXCLUDES, "fixtures", "tmp", "extra"]
    assert seen["ignore"] == ["*.lock", "a", "b"]
    assert seen["include"] == ["*.py", "*.js"]
    assert seen["extensions"] == [".py", ".js"]


def test_config_ignore_drops_files(tmp_path, capsys):
    _write_config({"check_file_size": {"ignore": ["*.js"]}})

    CheckFileSize().run([str(_project(tmp_path)), "--ignore", "small.*"])

    out = capsys.readouterr().out
    assert "mid.py" in out
    assert "big.js" not in out
    assert "small.py" not in out


def test_empty_config_ext_means_no_filter(tmp_path, capsys, monkeypatch):
    _write_config({"check_file_size": {"ext": []}})

    CheckFileSize().run([str(_project(tmp_path))])

    out = capsys.readouterr().out
    assert "big.js" in out
    assert "small.py" in out


# --- booleans -------------------------------------------------------------------


def test_config_gitignore_false_applies(tmp_path, capsys, monkeypatch):
    _write_config({"check_file_size": {"gitignore": False}})
    seen = _spy_collector(monkeypatch)

    CheckFileSize().run([str(_project(tmp_path))])

    assert seen["gitignore"] is False


def test_cli_no_gitignore_wins_over_config_true(tmp_path, capsys, monkeypatch):
    _write_config({"check_file_size": {"gitignore": True}})
    seen = _spy_collector(monkeypatch)

    CheckFileSize().run([str(_project(tmp_path)), "--no-gitignore"])

    assert seen["gitignore"] is False


def test_config_no_default_excludes_applies(tmp_path, capsys, monkeypatch):
    _write_config({"check_file_size": {"no_default_excludes": True, "exclude": ["x"]}})
    seen = _spy_collector(monkeypatch)

    CheckFileSize().run([str(_project(tmp_path))])

    assert seen["excludes"] == ["x"]


def test_cli_no_default_excludes_wins_over_config_false(tmp_path, capsys, monkeypatch):
    _write_config({"check_file_size": {"no_default_excludes": False}})
    seen = _spy_collector(monkeypatch)

    CheckFileSize().run([str(_project(tmp_path)), "--no-default-excludes"])

    assert seen["excludes"] == []


# --- errors ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        ("{oops", "invalid JSON"),
        ("[]", "top level must be an object"),
        ('{"check_file_size": []}', "'check_file_size' must be an object"),
        ('{"check_file_size": {"path": "."}}', "unknown key 'path'"),
        ('{"check_file_size": {"top": true}}', "'top' must be an integer >= 0"),
        (
            '{"check_file_size": {"fail_on": "ok"}}',
            "'fail_on' must be one of warn, error, critical or null",
        ),
    ],
)
def test_config_error_prints_to_stderr_and_exits_one(tmp_path, capsys, content, reason):
    path = _write_config(content)

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(_project(tmp_path))])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith(f"Error: {path}: ")
    assert reason in captured.err
    assert "\033[" not in captured.err


def test_config_is_validated_even_when_cli_sets_every_value(tmp_path, capsys):
    _write_config({"check_file_size": {"warn": -1}})

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(_project(tmp_path)), "--warn", "10"])

    assert exc_info.value.code == 1
    assert "'warn' must be an integer >= 0" in capsys.readouterr().err


def test_config_error_reported_before_path_not_found(tmp_path, capsys):
    _write_config("{oops")

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(tmp_path / "missing")])

    assert exc_info.value.code == 1
    assert "invalid JSON" in capsys.readouterr().err


def test_no_args_prints_help_even_with_invalid_config(capsys):
    _write_config("{oops")

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "--no-config" in captured.out
    assert captured.err == ""


# --- --no-config ----------------------------------------------------------------


def test_no_config_ignores_valid_config(tmp_path, capsys):
    _write_config({"check_file_size": {"warn": 10}})

    CheckFileSize().run([str(_project(tmp_path)), "--no-config"])

    out = capsys.readouterr().out
    assert f"warn={Constants.DEFAULT_WARN}" in out
    assert "Config:" not in out


def test_no_config_ignores_invalid_config(tmp_path, capsys):
    _write_config("{oops")

    CheckFileSize().run([str(_project(tmp_path)), "--no-config"])

    captured = capsys.readouterr()
    assert captured.err == ""
    assert "big.js" in captured.out


# --- Config: header line ----------------------------------------------------------


@pytest.mark.parametrize("section", [{}, {"warn": 400}])
def test_header_shows_config_line_when_section_loaded(tmp_path, capsys, section):
    path = _write_config({"check_file_size": section})

    CheckFileSize().run([str(_project(tmp_path))])

    lines = capsys.readouterr().out.splitlines()
    thresholds = next(i for i, line in enumerate(lines) if line.startswith("Thresholds:"))
    assert lines[thresholds + 1] == f"Config: {path}"
    assert lines[thresholds + 2] == ""


def test_header_has_no_config_line_without_file(tmp_path, capsys):
    CheckFileSize().run([str(_project(tmp_path))])

    assert "Config:" not in capsys.readouterr().out


def test_header_has_no_config_line_without_section(tmp_path, capsys):
    _write_config({"code_check": {"anything": 1}})

    CheckFileSize().run([str(_project(tmp_path))])

    assert "Config:" not in capsys.readouterr().out


# --- _merge ---------------------------------------------------------------------

EMPTY_CLI = {
    "path": ".",
    "warn": None,
    "error": None,
    "critical": None,
    "top": None,
    "fail_on": None,
    "min_level": None,
    "exclude": None,
    "ignore": None,
    "include": None,
    "ext": None,
    "no_default_excludes": False,
    "no_gitignore": False,
    "no_config": False,
}


def test_merge_with_nothing_gives_builtin_defaults():
    assert CheckFileSize._merge(dict(EMPTY_CLI), {}) == {
        "path": ".",
        "warn": Constants.DEFAULT_WARN,
        "error": Constants.DEFAULT_ERROR,
        "critical": Constants.DEFAULT_CRITICAL,
        "top": 0,
        "fail_on": None,
        "min_level": "ok",
        "exclude": [],
        "ignore": [],
        "include": [],
        "ext": [],
        "no_default_excludes": False,
        "gitignore": True,
    }


@pytest.mark.parametrize(
    ("key", "cli", "config", "expected"),
    [
        ("warn", None, 7, 7),
        ("warn", 9, 7, 9),
        ("warn", 0, 7, 0),
        ("top", None, 3, 3),
        ("top", 0, 3, 0),
        ("fail_on", None, "warn", "warn"),
        ("fail_on", "critical", "warn", "critical"),
        ("fail_on", "error", None, "error"),
        ("min_level", None, "error", "error"),
        ("min_level", "ok", "error", "ok"),
    ],
)
def test_merge_single_values(key, cli, config, expected):
    merged = CheckFileSize._merge({**EMPTY_CLI, key: cli}, {key: config})

    assert merged[key] == expected


@pytest.mark.parametrize("key", ["ignore", "include", "ext"])
@pytest.mark.parametrize(
    ("cli", "config", "expected"),
    [
        (None, ["a"], ["a"]),
        (["b"], [], ["b"]),
        (["b", "a"], ["a", "c"], ["a", "c", "b"]),
        (["a", "a"], None, ["a"]),
    ],
)
def test_merge_lists(key, cli, config, expected):
    section = {} if config is None else {key: config}

    assert CheckFileSize._merge({**EMPTY_CLI, key: cli}, section)[key] == expected


@pytest.mark.parametrize(
    ("cli", "config", "expected"),
    [
        (None, ["a"], ["a"]),
        ("b, a", ["a"], ["a", "b"]),
        ("a,,b", [], ["a", "b"]),
    ],
)
def test_merge_exclude(cli, config, expected):
    merged = CheckFileSize._merge({**EMPTY_CLI, "exclude": cli}, {"exclude": config})

    assert merged["exclude"] == expected


@pytest.mark.parametrize(
    ("cli_flag", "config", "expected"),
    [
        (False, {}, True),
        (False, {"gitignore": True}, True),
        (False, {"gitignore": False}, False),
        (True, {"gitignore": True}, False),
        (True, {}, False),
    ],
)
def test_merge_gitignore(cli_flag, config, expected):
    merged = CheckFileSize._merge({**EMPTY_CLI, "no_gitignore": cli_flag}, config)

    assert merged["gitignore"] is expected


@pytest.mark.parametrize(
    ("cli_flag", "config", "expected"),
    [
        (False, {}, False),
        (False, {"no_default_excludes": True}, True),
        (True, {"no_default_excludes": False}, True),
    ],
)
def test_merge_no_default_excludes(cli_flag, config, expected):
    merged = CheckFileSize._merge({**EMPTY_CLI, "no_default_excludes": cli_flag}, config)

    assert merged["no_default_excludes"] is expected


def test_merge_does_not_mutate_config_lists():
    config = {"ignore": ["a"], "exclude": ["x"]}

    CheckFileSize._merge({**EMPTY_CLI, "ignore": ["b"], "exclude": "y"}, config)

    assert config == {"ignore": ["a"], "exclude": ["x"]}
