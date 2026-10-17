# Calibrate the default thresholds
Check that `warn=20 | error=40 | critical=60` on the file's total CCN gives a sensible spread on real PHP code.

1. Shallow-clone 2–3 public codebases into a scratch directory: `laravel/framework`, `symfony/console`, and one legacy-style project (e.g. an older WordPress plugin or a classic MVC app).
2. Select the files the way the specs will: `.php` only, `*.blade.php` skipped, default excludes applied (`vendor`, `var`, `storage`, `bootstrap/cache`, `.phpunit.cache`, plus `file_size`'s list). Run the pinned PDepend through the staged-copy flow, and compute each file's total CCN (top-level code counts as 0).
3. Record, per codebase, the file count and the share in each band (`<20`, `20–40`, `40–60`, `≥60`), plus the p50/p90/p99 and the maximum.
4. Keep `20/40/60` unless most files land in WARN or above, or almost nothing ever reaches ERROR or CRITICAL. If you change them, choose round numbers. Write the chosen defaults, the table and the reasoning into README §3. A change to the defaults counts as a deviation in README §11.

## Files to Change
- None committed. The findings feed step 03.
