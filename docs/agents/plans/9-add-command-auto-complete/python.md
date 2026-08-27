# Python Plan: Add command auto complete

Main plan: [plan.md](plan.md)

## Shared contracts

- Must produce `python/check_file_size/main.py`, matching contract 1 (flow verb protocol) and contract 2 (`cli` will point `commands/python.json`'s `check_file_size.path` at this exact file).
- No `completion.<ext>` is added for `check_file_size` (contract 3) — it relies entirely on `cli`'s generic file/folder fallback, so `main.py` only needs to handle the `run` verb.

## Implementation Steps

### Step 1 — Split `check_file_size.py` into `executor.py` + `main.py`

Rename `python/check_file_size/check_file_size.py` to `python/check_file_size/executor.py`, keeping the `CheckFileSize` orchestrator class as-is, with two changes:

- `run(self)` becomes `run(self, args: list[str])`, passing `args` into `ArgParser(...).parse(args)` instead of relying on `ArgParser.parse()`'s implicit `sys.argv[1:]` default.
- The `len(sys.argv) == 1` "no arguments → print help" check becomes `len(args) == 0`.

Drop the `if __name__ == "__main__": CheckFileSize().run()` block — that responsibility moves to `main.py`.

Create `python/check_file_size/main.py` as the new entrypoint that `commands/python.json` will point at:

```python
#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from check_file_size.executor import CheckFileSize


def main() -> None:
    flow = sys.argv[1]
    args = sys.argv[2:]
    if flow == "run":
        CheckFileSize().run(args)


if __name__ == "__main__":
    main()
```

No `complete` branch is needed — `check_file_size` ships no `completion.py`, so `cli`'s hub never calls `main.py complete` for it (see shared contract 3).

### Step 2 — Verify existing tests still pass

`python/tests/check_file_size/*` import from `check_file_size.constants`, `check_file_size.file_collector`, `check_file_size.file_analyzer`, `check_file_size.reporter`, and `check_file_size.skip_checks` — none import `check_file_size.check_file_size` directly, so no test file needs an import change. Run the test suite to confirm nothing else was relying on the old module name or the old `run()` signature (in particular, anything constructing `CheckFileSize()` and calling `.run()` with no arguments).

## Files to Change

- `python/check_file_size/check_file_size.py` — renamed to `python/check_file_size/executor.py`; `run()` gains an `args` parameter.
- `python/check_file_size/main.py` — new dispatcher entrypoint (flow verb protocol).

## CI Checks

- `python/`: `ruff check python/` (CI job: `lint`)
- `python/`: `pytest` (CI job: `tests`)

## Notes

- Keep the `CheckFileSize` class name and its public behavior unchanged — only the entrypoint/dispatch shape changes.
