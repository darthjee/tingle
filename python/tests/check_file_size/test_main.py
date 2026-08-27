"""Unit tests for check_file_size.main's flow-verb dispatcher."""

from __future__ import annotations

import check_file_size.main as main_module


def test_main_dispatches_run_flow_with_remaining_args(monkeypatch):
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


def test_main_does_not_dispatch_unknown_flow(monkeypatch):
    called = {"run": False}

    class FakeCheckFileSize:
        def run(self, args):
            called["run"] = True

    monkeypatch.setattr(main_module, "CheckFileSize", FakeCheckFileSize)
    monkeypatch.setattr("sys.argv", ["main.py", "not_a_flow"])

    main_module.main()

    assert called["run"] is False
