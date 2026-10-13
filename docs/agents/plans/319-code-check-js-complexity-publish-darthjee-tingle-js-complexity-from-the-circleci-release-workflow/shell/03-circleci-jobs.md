# Add the CircleCI release jobs

In the `release` workflow, add `build-and-publish-js-complexity-image` and `update-js-complexity-description` (which requires the build job), with the same tag filter (`/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/`) and `branches: ignore: /.*/` as the rubycritic jobs. Add `build-and-publish-js-complexity-image` to `build-and-publish-release.requires`. Under `jobs:`, define both jobs by mirroring `build-and-publish-rubycritic-image` and `update-rubycritic-description`, with `js_complexity` as the selector. Leave the `test` workflow and the existing jobs unchanged.

## Files to Change
- `.circleci/config.yml` — two new workflow entries, two new job definitions, and one extra `requires` entry.
