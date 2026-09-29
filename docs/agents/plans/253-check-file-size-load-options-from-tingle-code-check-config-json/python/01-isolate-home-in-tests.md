# Isolate HOME in tests

Once the executor reads `~/.tingle/code_check/config.json`, every existing `CheckFileSize().run(...)` test would pick up the developer's real config. Add an autouse fixture that points `HOME` at a fresh temp dir for every check_file_size test (`monkeypatch.setenv("HOME", str(tmp_path_factory.mktemp("home")))`), so tests are hermetic. Tests that need a config write it under that `HOME`.

Make sure `Path.home()` honours it (it reads `HOME` on POSIX). Do this first so the later steps never run against a real config.

## Files to Change
- `python/tests/check_file_size/conftest.py` — new; autouse fixture setting `HOME` to a temp dir.
