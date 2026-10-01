# Plan: code_check rubycritic: per-method complexity drill-down (--details)

Issue: [291-code-check-rubycritic-per-method-complexity-drill-down-details.md](../../issues/291-code-check-rubycritic-per-method-complexity-drill-down-details.md)

## Overview
The `tingle_rubycritic` image's entrypoint also scores every method with Flog and adds a `methods` list to the JSON it prints. `tingle code_check rubycritic` gets a `--details [N]` flag (plus a `details` config key). It prints the top N methods of each shown file as indented lines under that file's row. Methods only show a score: levels, `--fail-on` and the exit codes stay file-based.

## Agents involved

- [shell](shell.md): entrypoint, smoke test and image contract doc.
- [python](python.md): parsing, flag, report lines and config key.
- [guide](guide.md): user guide.
- [product-owner](product-owner.md): updates the still-open rubycritic specs, so #297/#298 stay consistent.

## Shared contracts

### Image stdout: new top-level `methods` key

```json
"methods": [
  {"path": "complex.rb", "name": "Complex#run", "line": 2, "score": 72.25}
]
```

- One entry per method that Flog scored, across all files passed to RubyCritic (the files that survived the pre-parse).
- `path`: str, the path exactly as received on stdin (the same form as `parse_errors[].path`).
- `name`: str, Flog's `Class#method` / `Class::method` name. Flog's non-method buckets (names ending in `#none`) are excluded.
- `line`: int, the first line of the method.
- `score`: number, rounded to 2 decimals.
- Order: score descending, then `path`, then `name`.
- When RubyCritic is not run (no surviving paths), the key is still present: `"methods": []`.
- Every other key is unchanged.

### CLI flag and config key

| Flag | Type | Default | Config key (type) |
|------|------|---------|-------------------|
| `--details [N]` | int ≥ 0, optional value (`nargs='?'`, `const=5`) | `None` (off) | `details` (int ≥ 0 or `null`) |

- Absent means no detail lines. `--details` alone means 5. `--details 0` means all methods. A negative value is a usage error (exit 1, `Error: --details must be an integer >= 0`).
- Help text: `Show the N most complex methods under each file (default when given without N: 5; 0 = all)`.
- CLI over config, the same as the other single-value keys.

### Missing `methods` key

If `--details` is set and the container JSON has no `methods` key, the run fails with exit 1:
`Error: the RubyCritic output from <image> has no per-method data; --details needs a newer tingle_rubycritic image`.
Without `--details`, a missing key is ignored. A present but malformed `methods` key is always a contract break (`unexpected methods`), whether or not `--details` is set.

### Detail line layout

Under each shown level row (never under `PARSE` rows), in dim/gray:

```
{'':<16} {score:>10.2f}  {name}  ({display_path}:{line})
```

The score is aligned under the `Complexity` column. Up to N lines per file, sorted by score descending then name. A file with no methods gets no lines.
