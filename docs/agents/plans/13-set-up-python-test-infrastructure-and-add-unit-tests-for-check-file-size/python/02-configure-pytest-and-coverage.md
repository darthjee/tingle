# Configure pytest and coverage

Extend `python/pyproject.toml` (currently only holds `[tool.ruff]`) with
pytest and coverage config, so every caller (local, Docker, CircleCI) can
invoke the suite with a bare `pytest` — no extra flags needed anywhere else,
per `plan.md`'s shared contract:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov --cov-report=term-missing --cov-report=xml --cov-fail-under=90"

[tool.coverage.run]
source = ["check_file_size", "common"]
omit = ["tests/*"]
```

`--cov-fail-under=90` is a starting gate per the issue's Performance &
Security section — expected to need adjustment once the real coverage
numbers from steps 04–08 are in, not a precisely justified number today.

## Files to Change

- `python/pyproject.toml` — add `[tool.pytest.ini_options]` and
  `[tool.coverage.run]` sections as shown above, alongside the existing
  `[tool.ruff]`.
