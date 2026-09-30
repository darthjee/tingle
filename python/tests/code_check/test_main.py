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


def test_main_dispatches_complete_flow_and_prints_words(monkeypatch, capsys):
    captured = {}

    def fake_complete(argv):
        captured["argv"] = argv
        return ["a", "b"]

    monkeypatch.setattr(main_module, "complete", fake_complete)
    monkeypatch.setattr("sys.argv", ["main.py", "complete", "file_size", ""])

    main_module.main()

    assert captured["argv"] == ["file_size", ""]
    assert capsys.readouterr().out == "a b\n"


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
