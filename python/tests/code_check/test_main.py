"""Unit tests for code_check.main's flow-verb dispatcher."""

from __future__ import annotations

import code_check.main as main_module


def test_main_dispatches_run_flow_with_remaining_args(monkeypatch):
    captured = {}

    class FakeCodeCheck:
        def run(self, args):
            captured["args"] = args

    monkeypatch.setattr(main_module, "CodeCheck", FakeCodeCheck)
    monkeypatch.setattr("sys.argv", ["main.py", "run", "file_size", "./src", "--warn", "100"])

    main_module.main()

    assert captured["args"] == ["file_size", "./src", "--warn", "100"]


def test_main_does_not_dispatch_unknown_flow(monkeypatch, capsys):
    called = {"run": False}

    class FakeCodeCheck:
        def run(self, args):
            called["run"] = True

    monkeypatch.setattr(main_module, "CodeCheck", FakeCodeCheck)
    monkeypatch.setattr("sys.argv", ["main.py", "not_a_flow"])

    main_module.main()

    assert called["run"] is False
    assert capsys.readouterr().out == ""
