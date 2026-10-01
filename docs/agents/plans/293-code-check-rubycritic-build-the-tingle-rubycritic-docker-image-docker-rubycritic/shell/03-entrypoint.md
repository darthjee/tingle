# Entrypoint

Write `docker/rubycritic/entrypoint.rb` per spec section 4. Its contract is
binding.

- `require "bundler/setup"`, `json`, `open3` (or the equivalent) and `reek`.
- Ignore `ARGV`. Read all of `$stdin` as UTF-8 and split it on `"\n"`. Drop
  blank lines and remove duplicates, keeping each path at its first position.
- **Pre-parse** each path with
  `Reek::Source::SourceCode.new(source: File.read(path), origin: path).syntax_tree`.
  Rescue `StandardError, ScriptError`, and record
  `{"path" => line, "message" => first line of the message, stripped}` in
  `parse_errors`, in input order. Keep the surviving paths in order.
- **No survivors:** print
  `{"metadata":null,"analysed_modules":[],"score":null,"parse_errors":[...]}`
  plus `"\n"`, and exit 0. Never run RubyCritic with zero paths.
- **Run** `bundle exec rubycritic --format json --no-browser -p /tmp/out <paths>`
  (an argv array, not a shell string) in the current directory (`/src`). Send
  both of its streams to the entrypoint's `$stderr`, for example with
  `system(..., out: $stderr, err: $stderr)`. If it exits non-zero, print
  nothing on stdout and exit with its status.
- **Output:** read `/tmp/out/report.json`, parse it, set `"parse_errors"`, and
  print `JSON.generate(obj)` plus `"\n"` on stdout. If the file is missing,
  its JSON is invalid, or anything else fails, write a one-line reason to
  stderr, print nothing on stdout, and exit 1.
- Nothing other than the final JSON may reach stdout. Keep `$stdout` clean
  until the final write.

## Files to Change
- `docker/rubycritic/entrypoint.rb`: new file.
