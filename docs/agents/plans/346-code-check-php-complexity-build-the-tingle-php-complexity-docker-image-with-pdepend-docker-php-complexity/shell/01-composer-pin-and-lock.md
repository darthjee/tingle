# Composer pin and lock
Generate `docker/php_complexity/composer.json` and `composer.lock` with the exact command in image.md §3. The command runs the pinned `composer:2.10.3@sha256:af98f4…` image with `--user "$(id -u):$(id -g)"` and `COMPOSER_HOME=/tmp/composer`, then runs `composer init`, `composer config platform.php 8.5.11` and `composer require --no-install pdepend/pdepend:3.0.0`.

The resulting `composer.json` must match spec §3 exactly: name `tingle/php_complexity`, type `project`, require `pdepend/pdepend: 3.0.0`, and `config.platform.php` `8.5.11`. Check it with `composer validate --no-check-publish` in the same image; the only accepted warnings are no license and an exact constraint. Make sure no `vendor/` is left behind.

## Files to Change
- `docker/php_complexity/composer.json` — new, the PDepend pin.
- `docker/php_complexity/composer.lock` — new, the generated lock, committed.
