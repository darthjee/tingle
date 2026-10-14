"""Single-file component tests (#326) for code_check.js_complexity.executor.

Docker and git are mocked: the fake container answers with the `SFC` sample,
so each test asserts on the files sent and on the report of the SFC rows.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from code_check.file_size.git_ignore import GitIgnore, GitIgnored
from code_check.js_complexity import docker_runner
from code_check.js_complexity.executor import CheckJsComplexity
from tests.code_check.js_complexity.sample_output import SFC, SFC_LINES


@pytest.fixture(autouse=True)
def fake_git(monkeypatch):
    """No real git: nothing is ignored."""
    monkeypatch.setattr(
        GitIgnore, "ignored_paths", staticmethod(lambda root: GitIgnored(set(), []))
    )


class FakeDocker:
    """Scripted `docker`: every sub-command succeeds and `run` prints the SFC sample."""

    def __init__(self):
        self.stdin = None

    def __call__(self, args, **kwargs):
        if args[1] != "run":
            return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")
        self.stdin = kwargs["input"].decode().splitlines()
        return SimpleNamespace(returncode=0, stdout=json.dumps(SFC).encode(), stderr=b"")


@pytest.fixture
def docker(monkeypatch):
    fake = FakeDocker()
    monkeypatch.setattr(docker_runner.shutil, "which", lambda name: "/usr/bin/docker")
    monkeypatch.setattr(docker_runner.subprocess, "run", fake)
    return fake


@pytest.fixture
def fixture_dir(tmp_path):
    root = tmp_path / "fixture"
    for rel in [*SFC_LINES, "src/style.css"]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<template><p/></template>\n")
    return root


def _run(*args):
    try:
        CheckJsComplexity().run([*args, "--image", "img"])
    except SystemExit as exc:
        return exc.code
    return 0


def test_sfc_files_are_sent_on_stdin(fixture_dir, capsys, docker, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")

    assert _run(str(fixture_dir)) == 0

    assert docker.stdin == SFC_LINES


def test_sfc_rows_are_reported_under_the_original_path(
    fixture_dir, capsys, docker, monkeypatch
):
    monkeypatch.delenv("NO_COLOR", raising=False)

    assert _run(str(fixture_dir), "--details") == 0

    captured = capsys.readouterr()
    assert captured.out.splitlines()[6:13] == [
        "✅ OK              30.7      3     11      0  OK                 fixture/src/Cart.vue",
        f"{'':<16} cyclo   2  sloc    3  <anonymous>  (fixture/src/Cart.vue:13)",
        f"{'':<16} cyclo   1  sloc    2  addItem  (fixture/src/Cart.vue:17)",
        "✅ OK               0.0      -      -      0  -                  fixture/src/NoScript.vue",
        "⛔ PARSE              -      -      -      -  -                  fixture/src/Coffee.vue",
        "",
        "─" * 78,
    ]
    assert captured.err.splitlines() == [
        'Warning: cannot parse fixture/src/Coffee.vue: unsupported <script lang="coffee">',
    ]
