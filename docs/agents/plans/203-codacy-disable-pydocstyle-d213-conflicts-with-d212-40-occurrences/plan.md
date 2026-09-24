# Plan: Codacy: Disable pydocstyle D213 (conflicts with D212) (40 occurrences)

Issue: [203-codacy-disable-pydocstyle-d213-conflicts-with-d212-40-occurrences.md](../../issues/203-codacy-disable-pydocstyle-d213-conflicts-with-d212-40-occurrences.md)

## Overview
Codacy runs all of pydocstyle as one pattern (`Prospector_pydocstyle`), so D213 can't be turned off in the UI without losing D212 as well. Add a root `.prospector.yaml` that keeps today's Prospector tool set, turns pydocstyle on explicitly and disables D213. Also make ruff enforce D212 locally, so CI catches convention breaks before Codacy does.

## Agents involved

- [architect](architect.md): root-level `.prospector.yaml`
- [python](python.md): `python/pyproject.toml` ruff config

## Shared contracts

- **Convention:** D212 (multi-line docstring summary on the first line, same line as the opening `"""`). D213 is disabled everywhere.
- **Where each rule lives:**
  - Codacy/Prospector reads `/.prospector.yaml` (repo root); it disables D213 and keeps pydocstyle running.
  - ruff reads `python/pyproject.toml`; it adds `extend-select = ["D212"]` under `[tool.ruff.lint]`.
- **Cross-reference comments:** each file carries a comment that points at the other and at issue #203.
