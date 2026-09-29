"""Unit tests for check_file_size.executor.CheckFileSize."""

from __future__ import annotations

import pytest

from check_file_size.constants import Constants
from check_file_size.executor import CheckFileSize
from check_file_size.file_analyzer import FileAnalyzer
from check_file_size.file_collector import FileCollector


def test_run_no_args_prints_help_and_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([])

    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "usage" in out.lower()


def test_run_path_not_found_prints_error_and_exits_one(tmp_path, capsys):
    missing = tmp_path / "does_not_exist"

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(missing)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error: path not found" in captured.err
    assert "Error: path not found" not in captured.out
    assert "\033[" not in captured.err


def test_run_no_files_found_prints_message_and_exits_zero(tmp_path, capsys):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(empty_dir)])

    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "No files found for analysis." in out


def test_run_analyzes_and_reports_files(tmp_path, capsys):
    target = tmp_path / "project"
    target.mkdir()
    (target / "small.py").write_text("a\n")
    (target / "big.py").write_text("\n".join(str(i) for i in range(600)))

    CheckFileSize().run([str(target)])

    out = capsys.readouterr().out
    assert "Analyzing:" in out
    assert "small.py" in out
    assert "big.py" in out
    assert "Total:" in out


def test_run_applies_top_flag_to_limit_results(tmp_path, capsys):
    target = tmp_path / "project"
    target.mkdir()
    (target / "a.py").write_text("1\n" * 10)
    (target / "b.py").write_text("1\n" * 20)

    CheckFileSize().run([str(target), "--top", "1"])

    out = capsys.readouterr().out
    assert "b.py" in out
    assert "a.py" not in out


def test_run_output_is_plain_text_when_not_a_tty(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    target = tmp_path / "project"
    target.mkdir()
    (target / "a.py").write_text("1\n")

    CheckFileSize().run([str(target)])

    out = capsys.readouterr().out
    assert "Analyzing:" in out
    assert "\033[" not in out


@pytest.mark.parametrize(
    "extra",
    [["--top", "abc"], ["--unknown-option"], ["--warn", "x"]],
)
def test_run_usage_error_exits_one_on_stderr(tmp_path, capsys, extra):
    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(tmp_path), *extra])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "usage" in captured.err.lower()
    assert captured.out == ""


def test_run_help_flag_still_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run(["--help"])

    assert exc_info.value.code == 0
    assert "usage" in capsys.readouterr().out.lower()


def _project(tmp_path, *line_counts):
    target = tmp_path / "project"
    target.mkdir()
    for i, count in enumerate(line_counts):
        (target / f"f{i}.py").write_text("1\n" * count)
    return target


@pytest.mark.parametrize(
    "level, lines",
    [("warn", 3), ("error", 5), ("critical", 10)],
)
def test_run_fail_on_exits_two_when_level_reached(tmp_path, capsys, level, lines):
    target = _project(tmp_path, 1, lines)

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run(
            [str(target), "--warn", "3", "--error", "5", "--critical", "10", "--fail-on", level]
        )

    assert exc_info.value.code == 2
    out = capsys.readouterr().out
    assert "Summary:" in out
    assert "Total:" in out


@pytest.mark.parametrize(
    "level, lines",
    [("warn", 2), ("error", 4), ("critical", 9)],
)
def test_run_fail_on_passes_below_level(tmp_path, capsys, level, lines):
    target = _project(tmp_path, 1, lines)

    CheckFileSize().run(
        [str(target), "--warn", "3", "--error", "5", "--critical", "10", "--fail-on", level]
    )

    assert "Summary:" in capsys.readouterr().out


def test_run_fail_on_still_fails_when_offender_hidden_by_top(tmp_path, capsys):
    target = tmp_path / "project"
    target.mkdir()
    (target / "shown.py").write_text("1\n" * 30)
    (target / "hidden.py").write_text("1\n" * 28)

    # --top 1 hides hidden.py, which also breaches the gate; the report is
    # still printed in full before exiting 2.
    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run(
            [str(target), "--warn", "25", "--error", "100", "--critical", "200",
             "--top", "1", "--fail-on", "warn"]
        )

    assert exc_info.value.code == 2
    out = capsys.readouterr().out
    assert "shown.py" in out
    assert "hidden.py" not in out
    assert "1 file(s)" in out


def test_run_without_fail_on_never_exits_non_zero(tmp_path, capsys):
    target = _project(tmp_path, 50)

    CheckFileSize().run([str(target), "--warn", "3", "--error", "5", "--critical", "10"])

    assert "1 CRITICAL" in capsys.readouterr().out


def test_run_fail_on_invalid_value_exits_one(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(tmp_path), "--fail-on", "foo"])

    assert exc_info.value.code == 1
    assert "invalid choice" in capsys.readouterr().err


def test_run_fail_on_with_no_files_exits_zero(tmp_path, capsys):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(empty_dir), "--fail-on", "warn"])

    assert exc_info.value.code == 0
    assert "No files found for analysis." in capsys.readouterr().out


def test_parse_excludes_strips_whitespace_and_drops_empty_entries():
    assert CheckFileSize._parse_excludes(" a , ,b,, c ") == ["a", "b", "c"]


def test_parse_excludes_empty_string_returns_empty_list():
    assert CheckFileSize._parse_excludes("") == []


@pytest.mark.parametrize(
    ("exclude", "no_defaults", "expected"),
    [
        (None, False, Constants.DEFAULT_EXCLUDES),
        ("x", False, [*Constants.DEFAULT_EXCLUDES, "x"]),
        (None, True, []),
        ("x", True, ["x"]),
        (" x, ,y", True, ["x", "y"]),
        ("dist", False, Constants.DEFAULT_EXCLUDES),
        ("x,x", True, ["x"]),
        ("", False, Constants.DEFAULT_EXCLUDES),
        (",", False, Constants.DEFAULT_EXCLUDES),
    ],
)
def test_resolve_excludes(exclude, no_defaults, expected):
    args = {"exclude": exclude, "no_default_excludes": no_defaults}

    assert CheckFileSize._resolve_excludes(args) == expected


def test_resolve_excludes_does_not_mutate_defaults():
    before = list(Constants.DEFAULT_EXCLUDES)

    CheckFileSize._resolve_excludes({"exclude": "x", "no_default_excludes": False})

    assert before == Constants.DEFAULT_EXCLUDES


def test_analyze_sorts_descending_and_drops_unreadable(monkeypatch):
    counts = {"a": 5, "b": -1, "c": 20, "d": 0}
    analyzer = FileAnalyzer(300, 500, 1000)
    monkeypatch.setattr(analyzer, "count_lines", lambda f: counts[f])

    results = CheckFileSize._analyze(analyzer, ["a", "b", "c", "d"])

    assert results == [("c", 20), ("a", 5), ("d", 0)]


@pytest.mark.parametrize(
    ("fail_on", "lines", "expected"),
    [
        (None, 5000, False),
        ("error", 499, False),
        ("error", 500, True),
        ("error", 501, True),
    ],
)
def test_gate_failed(fail_on, lines, expected):
    analyzer = FileAnalyzer(300, 500, 1000)
    results = [("small.py", 1), ("big.py", lines)]

    assert CheckFileSize._gate_failed(analyzer, results, fail_on) is expected


def test_gate_failed_with_no_results_is_false():
    analyzer = FileAnalyzer(300, 500, 1000)

    assert CheckFileSize._gate_failed(analyzer, [], "warn") is False


def _make_project(root):
    for rel in ("src/main.py", "src/util.js", "src/extern/lib.py", "docs/guide.txt",
                "README.md", "app.test.js"):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")


def test_run_ignore_flag_is_repeatable_and_drops_matches(tmp_path, capsys):
    _make_project(tmp_path)

    CheckFileSize().run([str(tmp_path), "--ignore", "*.test.js", "--ignore", "docs/**"])

    out = capsys.readouterr().out
    assert "main.py" in out
    assert "README.md" in out
    assert "app.test.js" not in out
    assert "guide.txt" not in out


def test_run_include_flag_combines_with_ext(tmp_path, capsys):
    _make_project(tmp_path)

    CheckFileSize().run([str(tmp_path), "--include", "src/**", "--ext", ".py"])

    out = capsys.readouterr().out
    assert "main.py" in out
    assert "lib.py" in out
    assert "util.js" not in out
    assert "README.md" not in out


def test_run_ignore_wins_over_include(tmp_path, capsys):
    _make_project(tmp_path)

    CheckFileSize().run([str(tmp_path), "--include", "src/**", "--ignore", "src/extern/"])

    out = capsys.readouterr().out
    assert "main.py" in out
    assert "util.js" in out
    assert "lib.py" not in out


def test_run_passes_glob_lists_to_collector(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("x\n")
    seen = {}
    real_init = FileCollector.__init__

    def spy_init(self, *args, **kwargs):
        seen.update(kwargs)
        real_init(self, *args, **kwargs)

    monkeypatch.setattr(FileCollector, "__init__", spy_init)

    CheckFileSize().run([str(tmp_path), "--ignore", "a", "--ignore", "b", "--include", "*.py"])

    assert seen == {"ignore": ["a", "b"], "include": ["*.py"]}


def test_run_passes_empty_glob_lists_when_flags_absent(tmp_path, monkeypatch):
    (tmp_path / "a.py").write_text("x\n")
    seen = {}
    real_init = FileCollector.__init__

    def spy_init(self, *args, **kwargs):
        seen.update(kwargs)
        real_init(self, *args, **kwargs)

    monkeypatch.setattr(FileCollector, "__init__", spy_init)

    CheckFileSize().run([str(tmp_path)])

    assert seen == {"ignore": [], "include": []}


def test_run_everything_filtered_out_prints_no_files_and_exits_zero(tmp_path, capsys):
    file_path = tmp_path / "main.py"
    file_path.write_text("x\n")

    with pytest.raises(SystemExit) as exc_info:
        CheckFileSize().run([str(file_path), "--ignore", "main.*"])

    assert exc_info.value.code == 0
    assert "No files found for analysis." in capsys.readouterr().out


def _spy_excludes(monkeypatch):
    seen = {}
    real_init = FileCollector.__init__

    def spy_init(self, excludes, *args, **kwargs):
        seen["excludes"] = excludes
        real_init(self, excludes, *args, **kwargs)

    monkeypatch.setattr(FileCollector, "__init__", spy_init)
    return seen


def _make_excluded_project(root):
    for rel in ("src/main.py", "node_modules/pkg/index.js", "fixtures/data.txt"):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x\n")


def test_run_exclude_adds_to_defaults(tmp_path, capsys, monkeypatch):
    _make_excluded_project(tmp_path)
    seen = _spy_excludes(monkeypatch)

    CheckFileSize().run([str(tmp_path), "--exclude", "fixtures"])

    assert seen["excludes"] == [*Constants.DEFAULT_EXCLUDES, "fixtures"]
    out = capsys.readouterr().out
    assert "main.py" in out
    assert "index.js" not in out
    assert "data.txt" not in out


def test_run_without_exclude_uses_defaults(tmp_path, capsys, monkeypatch):
    _make_excluded_project(tmp_path)
    seen = _spy_excludes(monkeypatch)

    CheckFileSize().run([str(tmp_path)])

    assert seen["excludes"] == Constants.DEFAULT_EXCLUDES
    out = capsys.readouterr().out
    assert "data.txt" in out
    assert "index.js" not in out


def test_run_no_default_excludes_walks_default_dirs(tmp_path, capsys, monkeypatch):
    _make_excluded_project(tmp_path)
    seen = _spy_excludes(monkeypatch)

    CheckFileSize().run([str(tmp_path), "--no-default-excludes"])

    assert seen["excludes"] == []
    out = capsys.readouterr().out
    assert "index.js" in out
    assert "data.txt" in out


def test_run_no_default_excludes_with_exclude_only_skips_given(tmp_path, capsys):
    _make_excluded_project(tmp_path)

    CheckFileSize().run([str(tmp_path), "--no-default-excludes", "--exclude", "fixtures"])

    out = capsys.readouterr().out
    assert "index.js" in out
    assert "main.py" in out
    assert "data.txt" not in out


def test_help_says_exclude_adds_to_defaults(capsys):
    with pytest.raises(SystemExit):
        CheckFileSize().run(["--help"])

    out = " ".join(capsys.readouterr().out.split())
    assert "added to the defaults" in out
    assert "--no-default-excludes" in out
