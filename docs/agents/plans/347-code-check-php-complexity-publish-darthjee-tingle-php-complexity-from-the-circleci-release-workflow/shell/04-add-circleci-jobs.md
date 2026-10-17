# Add the CircleCI release jobs

In `.circleci/config.yml`, add these to the `release` workflow:
- `build-and-publish-php-complexity-image`, with no requires;
- `update-php-complexity-description`, which requires the build job.

Both use the existing tag filter `/^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$/` and `branches: ignore: /.*/`. Add `build-and-publish-php-complexity-image` to `build-and-publish-release`'s `requires`.

Define the two jobs after the js_complexity ones, copying them with `php_complexity` as the selector: `checkout`, then `Set up builder` / `Build image` / `Smoke test` / `Scan image` / `Publish image` on `machine: image: ubuntu-2404:current`; `machine: true` and `update-description php_complexity` for the description job. Leave existing jobs and the `test` workflow unchanged.

## Files to Change
- `.circleci/config.yml` — two new jobs, their workflow entries, and the extra `requires` on `build-and-publish-release`.
