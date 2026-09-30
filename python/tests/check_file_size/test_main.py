"""Unit tests for the check_file_size.main alias shim."""

from __future__ import annotations

import io
import sys

import pytest

import check_file_size.main as main_module
from code_check.file_size.executor import CheckFileSize
from code_check.palette import Colors

WARNING = (
    "Warning: 'tingle check_file_size' is deprecated; "
    "use 'tingle code_check file_size'."
)


class TtyStream(io.StringIO):
    """StringIO that claims to be a terminal."""

    def isatty(self) -> bool:
        return True


def test_shim_uses_code_check_file_size_executor():
    assert main_module.CheckFileSize is CheckFileSize


def test_warning_text_matches_contract():
    assert main_module.WARNING == WARNING


def test_main_dispatches_run_flow_with_remaining_args(monkeypatch, capsys):
    captured = {}

    class FakeCheckFileSize:
        def run(self, args):
            captured["args"] = args

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr(
        "sys.argv", ["main.py", "run", "./src", "--warn", "100"]
    )

    main_module.main()

    assert captured["args"] == ["./src", "--warn", "100"]
    assert capsys.readouterr().err == WARNING + "\n"


def test_run_warning_goes_to_stderr_only(monkeypatch, capsys):
    class FakeCheckFileSize:
        def run(self, args):
            print("report line")

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "run", "."])

    main_module.main()

    out, err = capsys.readouterr()
    assert out == "report line\n"
    assert err == WARNING + "\n"


def test_run_warning_is_printed_before_executor_runs(monkeypatch):
    stream = io.StringIO()
    seen = []

    class FakeCheckFileSize:
        def run(self, args):
            seen.append(stream.getvalue())

    monkeypatch.setattr(sys, "stderr", stream)
    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "run", "."])

    main_module.main()

    assert seen == [WARNING + "\n"]


def test_run_stdout_matches_direct_executor_call(tmp_path, monkeypatch, capsys):
    (tmp_path / "small.py").write_text("print('hi')\n")
    (tmp_path / "big.py").write_text("x = 1\n" * 50)
    args = [str(tmp_path), "--no-config", "--warn", "10", "--fail-on", "warn"]
    monkeypatch.setenv("NO_COLOR", "1")

    with pytest.raises(SystemExit) as direct_exit:
        CheckFileSize().run(list(args))
    direct = capsys.readouterr()

    monkeypatch.setattr("sys.argv", ["main.py", "run", *args])
    with pytest.raises(SystemExit) as shim_exit:
        main_module.main()
    shim = capsys.readouterr()

    assert shim.out == direct.out
    assert shim.err == WARNING + "\n" + direct.err
    assert shim_exit.value.code == direct_exit.value.code == 2


def test_run_stdout_matches_direct_executor_call_without_exit(
    tmp_path, monkeypatch, capsys
):
    (tmp_path / "small.py").write_text("print('hi')\n")
    args = [str(tmp_path), "--no-config"]
    monkeypatch.setenv("NO_COLOR", "1")

    CheckFileSize().run(list(args))
    direct = capsys.readouterr()

    monkeypatch.setattr("sys.argv", ["main.py", "run", *args])
    main_module.main()
    shim = capsys.readouterr()

    assert shim.out == direct.out
    assert shim.err == WARNING + "\n" + direct.err


@pytest.mark.parametrize("code", [0, 1, 2])
def test_run_forwards_exit_status_unchanged(monkeypatch, capsys, code):
    class FakeCheckFileSize:
        def run(self, args):
            sys.exit(code)

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "run", "."])

    with pytest.raises(SystemExit) as exc:
        main_module.main()

    assert exc.value.code == code
    assert capsys.readouterr().err == WARNING + "\n"


def _run_noop(monkeypatch):
    class FakeCheckFileSize:
        def run(self, args):
            pass

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "run", "."])
    main_module.main()


def test_warning_is_plain_when_stderr_is_not_a_tty(monkeypatch, capsys):
    monkeypatch.delenv("NO_COLOR", raising=False)

    _run_noop(monkeypatch)

    err = capsys.readouterr().err
    assert "\033[" not in err
    assert err == WARNING + "\n"


def test_warning_is_plain_with_no_color_on_a_tty(monkeypatch):
    stream = TtyStream()
    monkeypatch.setattr(sys, "stderr", stream)
    monkeypatch.setenv("NO_COLOR", "1")

    _run_noop(monkeypatch)

    assert "\033[" not in stream.getvalue()
    assert stream.getvalue() == WARNING + "\n"


def test_warning_is_yellow_on_a_tty(monkeypatch):
    stream = TtyStream()
    monkeypatch.setattr(sys, "stderr", stream)
    monkeypatch.delenv("NO_COLOR", raising=False)

    _run_noop(monkeypatch)

    assert stream.getvalue() == f"{Colors.YELLOW}{WARNING}{Colors.RESET}\n"


def test_main_has_no_complete_flow(monkeypatch, capsys):
    called = {"run": False}

    class FakeCheckFileSize:
        def run(self, args):
            called["run"] = True

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "complete", "."])

    main_module.main()

    assert called["run"] is False
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""


def test_main_does_not_dispatch_unknown_flow(monkeypatch, capsys):
    called = {"run": False}

    class FakeCheckFileSize:
        def run(self, args):
            called["run"] = True

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "not_a_flow"])

    main_module.main()

    assert called["run"] is False
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
