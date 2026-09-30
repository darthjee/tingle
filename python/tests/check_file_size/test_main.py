"""Unit tests for the check_file_size.main alias shim."""

from __future__ import annotations

import check_file_size.main as main_module


def test_shim_uses_code_check_file_size_executor():
    from code_check.file_size.executor import CheckFileSize

    assert main_module.CheckFileSize is CheckFileSize


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
    assert capsys.readouterr().err == ""


def test_main_has_no_complete_flow(monkeypatch, capsys):
    called = {"run": False}

    class FakeCheckFileSize:
        def run(self, args):
            called["run"] = True

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "complete", "."])

    main_module.main()

    assert called["run"] is False
    assert capsys.readouterr().out == ""


def test_main_does_not_dispatch_unknown_flow(monkeypatch):
    called = {"run": False}

    class FakeCheckFileSize:
        def run(self, args):
            called["run"] = True

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "not_a_flow"])

    main_module.main()

    assert called["run"] is False
