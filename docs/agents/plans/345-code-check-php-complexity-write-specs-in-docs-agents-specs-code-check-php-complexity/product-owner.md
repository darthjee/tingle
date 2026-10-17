# Product-owner Plan: code_check php_complexity: write specs in docs/agents/specs/code_check/php_complexity/

Main plan: [plan.md](plan.md)

## Overview
Ground the PHP complexity check's contracts in real tool output, then write the spec set (`README.md` plus seven per-sub-issue files) and index it in `docs/agents/specs.md`.

## Context
- **Parent:** #344. Sub-issues: #345 (this one, the specs), #346 (image, PDepend only), #347 (release), #348 (subcommand core), #349 (selection flags), #350 (config), #351 (`--details`), #352 (jscpd duplication) and #353 (cleanup).
- **Precedent:** the js_complexity specs (#316, removed by #327; recover them with `git show 9e5e040^:docs/agents/specs/code_check/js_complexity/<file>`). Reuse their structure, depth and tone: normative "must/is", exact messages, a JSON shape with types, and a numbered "Deviations" section.
- **Already decided, unless real output overturns it:**
  - top-level code counts as 0 CCN;
  - files reach PDepend through staged copies at `/tmp/stage/<n>.php`, mapped back by `<n>`;
  - if PDepend has no per-method maintainability index, the `MI` column is dropped rather than computed.
- **Default thresholds:** `20/40/60` on the file's total CCN, subject to calibration.
- The shared `python/code_check/docker_check/` module already exists (#317). Specs reference its existing API and never re-specify it.
- Docker is needed on the host for steps 01–02. Pulled images and cloned codebases go in a scratch directory outside the repo and are never committed.

## Steps

- [01 — Ground the contracts in real PDepend/jscpd output](product-owner/01-ground-real-output.md)
- [02 — Calibrate the default thresholds](product-owner/02-calibrate-thresholds.md)
- [03 — Write README.md (shared contracts)](product-owner/03-write-readme.md)
- [04 — Write image.md and release.md](product-owner/04-write-image-and-release.md)
- [05 — Write cli.md, selection.md and config.md](product-owner/05-write-cli-selection-config.md)
- [06 — Write details.md and duplication.md](product-owner/06-write-details-and-duplication.md)
- [07 — Index the specs in docs/agents/specs.md](product-owner/07-index-specs.md)

## CI Checks
- No CI job validates `docs/agents/`. The `lint` and `tests` jobs don't touch these files. Check every relative link by hand (`ls` each target), and make sure there are no `TODO`/placeholder values left.

## Notes
- **Every pin must be concrete:** an exact base-image tag and digest, an exact PDepend version (with the commands that generate `composer.lock`), and an exact jscpd version (the one `docker/js_complexity/package.json` pins).
- Any assumption in #344 that real output contradicts goes in README §11 "Deviations from #344", numbered, and each affected spec file points to it. Never drop one silently.
- The fixture is **specified** in `image.md` (each file's name, its contents or a precise description, and its expected per-file result). It is **not** committed under `docker/`; #346 creates it there.
