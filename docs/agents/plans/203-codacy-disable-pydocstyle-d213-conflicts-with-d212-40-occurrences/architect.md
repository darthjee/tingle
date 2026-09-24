# Architect Plan: Codacy: Disable pydocstyle D213 (conflicts with D212) (40 occurrences)

Main plan: [plan.md](plan.md)

## Shared contracts

- Produce `/.prospector.yaml` at the repo root. It disables D213, leaves D212 enabled and keeps pydocstyle running.
- Its header comment points to `python/pyproject.toml` (ruff enforces D212 locally) and to issue #203.

## Implementation Steps

### Step 1 — Add the root Prospector profile
Create `.prospector.yaml` at the repo root. Codacy's Prospector integration picks up this file name, and once it's present it replaces the UI pattern settings for Prospector. So the file must reproduce what Codacy enables today (see the `Prospector` entry in `.codacy/codacy.config.json`: dodgy, mccabe, profile-validator, pycodestyle, pydocstyle, pyflakes) and nothing more:

- `doc-warnings: true` and `pydocstyle: run: true`, with `disable: [D213]`. Prospector's default profile leaves pydocstyle off, so turning it on explicitly is required.
- `run: true` for dodgy, mccabe, pycodestyle, pyflakes (profile-validator always runs).
- `run: false` for tools Codacy doesn't enable today: pylint, pep8-naming, vulture, mypy, bandit, pyroma, frosted.
- If `pycodestyle` needs a line length, match ruff's `line-length = 100` (`python/pyproject.toml`) so no new E501 findings appear.
- Header comment in the style of `.codacy.yml`: why the file exists (Codacy groups all pydocstyle codes into one pattern), why D213 is off (it conflicts with D212, the convention since #134–#140) and that ruff enforces D212 locally.

### Step 2 — Validate the profile
If `prospector` can be installed (e.g. `pip install prospector` in a throwaway venv or container), run `prospector --profile-path . --profile .prospector.yaml python/` from the repo root. Check that there are no D213 findings, that D212 still runs, and that no pylint/vulture/etc. output appears. If it can't be installed, say so in the PR and rely on the Codacy check.

## Files to Change
- `.prospector.yaml` (new): Prospector profile Codacy uses; disables D213 and keeps the current tool set.

## Notes
- Codacy's config-file lookup is the main risk: if Codacy ignores the file, D213 keeps being reported. Verify on the PR's Codacy analysis that the 40 D213 findings are gone and no new Prospector findings appear.
- Prospector's strictness profiles disable some pydocstyle codes by default (e.g. D203 vs D211). Pick settings that don't bring back codes Codacy doesn't report today, such as D203, which conflicts with D211.
- `.codacy.yml` stays unchanged (it only scopes Bandit).
