# Dockerfile and .dockerignore

Write `docker/rubycritic/Dockerfile` per spec section 2.

Start it with a header comment in the style of `shell/linux/Dockerfile`:

- what the image is for;
- its reproducibility pins;
- that the build context is `docker/rubycritic/`;
- a pointer to the spec for bumps.

Then:

- `ARG BASE_IMAGE=ruby:3.3.12-slim@sha256:379ffc9ca20cae2655cb80cac53ee23e1e7d859c03a4cceb7f567d6ce4873cee`.
- `build` stage `FROM ${BASE_IMAGE} AS build`:
  - `ENV BUNDLE_GEMFILE=/opt/tingle_rubycritic/Gemfile BUNDLE_FROZEN=true`;
  - `apt-get install --no-install-recommends build-essential=<pinned>`, then
    clean the apt lists;
  - `COPY Gemfile Gemfile.lock /opt/tingle_rubycritic/`, then
    `bundle install`.
- Final stage `FROM ${BASE_IMAGE}`:
  - the same `ENV`;
  - `COPY --from=build /usr/local/bundle /usr/local/bundle`;
  - `COPY --from=build` the Gemfile pair;
  - `COPY entrypoint.rb /opt/tingle_rubycritic/entrypoint.rb`.
  
  Install no apt packages and no git, and do not override `LANG` (keep
  `C.UTF-8`). End with `USER 1000:1000` and
  `ENTRYPOINT ["ruby", "/opt/tingle_rubycritic/entrypoint.rb"]`, with no
  `CMD`.

Write `docker/rubycritic/.dockerignore` excluding `fixture/`.

## Files to Change
- `docker/rubycritic/Dockerfile`: new file.
- `docker/rubycritic/.dockerignore`: new file.
