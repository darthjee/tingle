# Dockerfile and .dockerignore
Write the Dockerfile from image.md §2:

- Top-level `ARG BASE_IMAGE=php:8.5.11-cli-trixie@sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3` and `ARG COMPOSER_IMAGE=composer:2.10.3@sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac`.
- `deps` stage from `${COMPOSER_IMAGE}`: `WORKDIR /opt/tingle_php_complexity`, copy `composer.json` and `composer.lock`, then `composer validate --no-check-publish && composer install --no-dev --no-interaction --no-progress --classmap-authoritative`.
- Final stage from `${BASE_IMAGE}`: copy `/opt/tingle_php_complexity/` from `deps`, then copy `entrypoint.php` (and `lib/` once step 03 adds it). No apt packages, so the image has no git, Composer or unzip. End with `USER 1000:1000` and `ENTRYPOINT ["php", "/opt/tingle_php_complexity/entrypoint.php"]`, with no `CMD`.

Follow `docker/js_complexity/Dockerfile`'s comment style (a short header explaining the stages and pins). `.dockerignore` lists `fixture/` and `vendor/`.

## Files to Change
- `docker/php_complexity/Dockerfile` — new.
- `docker/php_complexity/.dockerignore` — new; excludes `fixture/` and `vendor/`.
