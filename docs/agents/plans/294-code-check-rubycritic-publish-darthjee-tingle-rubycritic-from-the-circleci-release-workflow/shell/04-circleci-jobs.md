# Add the CircleCI release jobs
Wire the rubycritic image into the `release` workflow, as specified in [release.md section 4 (CircleCI)](../../../specs/code_check/rubycritic/release.md#circleci).

- New job `build-and-publish-rubycritic-image`: `machine: image: ubuntu-2404:current`, `checkout`, then one `run` step each for `scripts/release_image.sh setup-builder`, then `build`, `smoke-test`, `scan` and `publish` with the `rubycritic` selector. Use the same step names as the linux job.
- New job `update-rubycritic-description`: `machine: true`, `checkout`, `scripts/release_image.sh update-description rubycritic`.
- In `workflows.release.jobs`:
  - add both jobs with the existing plain-semver tag filter and `branches: ignore: /.*/`;
  - `update-rubycritic-description` requires `build-and-publish-rubycritic-image`;
  - `build-and-publish-release` requires both `build-and-publish-linux-image` and `build-and-publish-rubycritic-image`.
- Existing jobs keep calling the script without a selector. The `test` workflow is unchanged.

## Files to Change
- `.circleci/config.yml` — two new jobs, their workflow entries, and the extra `requires` on `build-and-publish-release`.
