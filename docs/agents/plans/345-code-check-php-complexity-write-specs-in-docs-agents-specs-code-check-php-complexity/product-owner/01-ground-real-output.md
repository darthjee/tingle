# Ground the contracts in real PDepend/jscpd output
Pick the pins, build a throwaway fixture, and record exactly what the tools emit. This happens before any spec is written, because the specs must reflect real behaviour.

1. **Pins:**
   - **Base image:** choose the latest `php:<8.x>-cli` variant with working amd64 and arm64 manifests. Prefer Debian slim unless Alpine is clearly better for arm64. Record the tag and digest (`docker buildx imagetools inspect`).
   - **PDepend:** install the latest stable release through Composer in that image (`composer require pdepend/pdepend:<x.y.z>`), and record the version.
   - **jscpd:** use the version `docker/js_complexity/package.json` pins, on the Node version js_complexity uses. Record how Node would be added to a PHP image: a multi-stage copy of the Node binary vs. a distro package.
2. **Fixture**, in a scratch directory. It has:
   - a class with methods of varying CCN
   - several classes in one file
   - plain functions
   - a file with top-level code only
   - mixed HTML/PHP
   - an empty file
   - a syntax error
   - PHP 8.3 syntax (an enum, a readonly class)
   - a `*.blade.php` file
   - two files that share a duplicated block
3. **Runs:**
   - Stage the fixture as `/tmp/stage/<n>.php` and run `pdepend --summary-xml=/tmp/summary.xml /tmp/stage`, as a non-root user with `/src` read-only and `--network none`. Also run it once on the unstaged tree, to confirm why staging is needed (suffix and ignore filters).
   - Run jscpd on the same staged files, with JSON output.
4. **Record**, as trimmed real excerpts for the specs:
   - The XML nesting (`package`/`class`/`method`, `function`, `file` elements) and the attributes for `ccn`, `ccn2`, `npath`, `lloc`.
   - Whether there is a maintainability-index attribute.
   - How a parse error shows up, on stderr or in the XML, with the exact message format, and whether PDepend continues past it.
   - How files with top-level code only, empty files and mixed HTML/PHP files show up.
   - PDepend's exit status in each case.
   - jscpd's PHP clone fields.
   - The exact commands used.

Every contradiction with #344 is noted for README §11.

## Files to Change
- None committed. The findings feed steps 03–06.
