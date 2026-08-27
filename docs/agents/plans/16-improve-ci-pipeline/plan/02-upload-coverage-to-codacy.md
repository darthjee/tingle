# Upload coverage to Codacy
At the end of the `tests` job, add a step that uploads `python/coverage.xml` to Codacy using the official reporter script (downloaded fresh each run, nothing committed):

```bash
bash <(curl -Ls https://coverage.codacy.com/get.sh) report -r python/coverage.xml
```

A single `report` call is sufficient — there's only one job producing coverage, so no partial+final merge step is needed. `CODACY_PROJECT_TOKEN` is read implicitly by the reporter script from the CircleCI project env var; no new env var configuration is needed in `config.yml` itself.

## Files to Change
- `.circleci/config.yml` — add the Codacy upload step as the last step of the `tests` job (depends on Step 01's job split existing first).
