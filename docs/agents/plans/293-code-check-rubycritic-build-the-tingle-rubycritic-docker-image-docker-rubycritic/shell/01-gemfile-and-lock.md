# Gemfile and lock

Create `docker/rubycritic/Gemfile` containing exactly
`source "https://rubygems.org"` and `gem "rubycritic", "5.0.0"`.

Generate `docker/rubycritic/Gemfile.lock` **inside the pinned base image**
(`ruby:3.3.12-slim@sha256:379ffc9c…`, full digest in spec section 2). Mount
the folder and run:

- `bundle lock`
- `bundle lock --add-platform x86_64-linux aarch64-linux`
- `bundle lock --remove-platform ruby`

Commit the lock. Check that it matches spec section 3:

- `rubycritic 5.0.0`, `flog 4.9.4`, `flay 2.14.4`, `reek 6.5.0`;
- `parser 3.3.12.0`, `prism 1.9.0`, `ruby_parser 3.22.0`;
- `BUNDLED WITH 2.5.22`;
- the platforms `aarch64-linux` and `x86_64-linux` only.

## Files to Change
- `docker/rubycritic/Gemfile`: new file.
- `docker/rubycritic/Gemfile.lock`: new file, generated and committed.
