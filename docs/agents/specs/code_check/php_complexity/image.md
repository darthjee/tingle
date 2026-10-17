# Spec: the `tingle_php_complexity` Docker image

Sub-issue: #346 (PDepend only). Extended by #351 (`functions`) and #352
(jscpd). Parent: #344. Shared contracts: [README.md](README.md).

The image runs PHP's parser and PDepend, and later jscpd, for
`tingle code_check php_complexity`. Tingle sends a list of files on stdin and
reads one JSON document on stdout. This spec covers the image source, the
entrypoint contract, the merged JSON, the smoke-test fixture and the local
build. Publishing is in [release.md](release.md).

## 1. Location and files

The image lives in `docker/php_complexity/`, owned by the **`shell`** agent,
like `docker/js_complexity/`. #346 adds the folder to
`docs/agents/folder-structure.md` and to the `shell` agent's scope in
`.claude/agents/shell.md`.

| Path | Content | Added by |
|------|---------|----------|
| `docker/php_complexity/Dockerfile` | The image (section 2). | #346 |
| `docker/php_complexity/composer.json` | The PDepend pin (section 3). | #346 |
| `docker/php_complexity/composer.lock` | The resolved lock (section 3), committed. | #346 |
| `docker/php_complexity/entrypoint.php` | The entrypoint (sections 4 to 8). It may `require` helper files from `docker/php_complexity/lib/`. | #346 |
| `docker/php_complexity/package.json`, `package-lock.json` | The jscpd pin, for the build-only Node stage. | #352 |
| `docker/php_complexity/fixture/` | The smoke-test fixture (section 9). | #346 |
| `docker/php_complexity/.dockerignore` | Excludes `fixture/` and `vendor/` (and, from #347, the Docker Hub description files) from the build context. | #346 |

**The entrypoint is PHP**, not shell or Node:

- the base image already has PHP, and #346 needs no other runtime;
- the parse check (section 5) uses PHP's own parser in-process
  (`token_get_all`), and the version comes from Composer's runtime API
  (`Composer\InstalledVersions`);
- the summary XML is read with the built-in `dom`/`SimpleXML` extensions
  (both are in the base image), which shell cannot do robustly;
- `proc_open` with an argument array runs PDepend and jscpd without a shell.

It uses the PHP standard library and the installed `vendor/` tree only.

The build context is `docker/php_complexity/` itself:

```
docker buildx build -t <tag> docker/php_complexity
```

## 2. Dockerfile

- **Base image:** `php:8.5.11-cli-trixie` (PHP 8.5.11, Debian 13.7, glibc),
  pinned by its multi-platform index digest in a top-level `ARG BASE_IMAGE`:

  ```
  ARG BASE_IMAGE=php:8.5.11-cli-trixie@sha256:01a109229f4465bc9ef042d9198f09a4d9da7775a825dbd8572dcdbd8756c4d3
  ```

  The index resolves on `linux/amd64` and `linux/arm64/v8`. The `cli`
  variant is built on `debian:trixie-slim`; there is no separate `-slim`
  tag. Debian was chosen over Alpine (README §10).
- **Composer stage** (`deps`, build only; README deviation 12). The base
  image has no `zip` extension and no `unzip`, so Composer cannot install
  there. A pinned Composer image does it:

  ```
  ARG COMPOSER_IMAGE=composer:2.10.3@sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac
  FROM ${COMPOSER_IMAGE} AS deps
  WORKDIR /opt/tingle_php_complexity
  COPY composer.json composer.lock ./
  RUN composer validate --no-check-publish \
   && composer install --no-dev --no-interaction --no-progress --classmap-authoritative
  ```

  `composer install` alone only **warns** when the lock does not match
  `composer.json`; `composer validate --no-check-publish` exits 2 in that
  case (both checked), so the build fails instead of installing a stale
  lock. The Composer image runs PHP 8.5.11 too, and the lock is resolved for
  `config.platform.php` `8.5.11`. The installed tree is pure PHP.
- **Final stage** (from `BASE_IMAGE`): copies `/opt/tingle_php_complexity/`
  (with `vendor/`) from `deps`, then `entrypoint.php` (and `lib/`) into
  `/opt/tingle_php_complexity/`. It installs no apt package. From #352 it
  also copies `/usr/local/bin/jscpd` from the Node stage
  ([duplication.md](duplication.md#1-image-changes)).
- **Not in the final image:** git, Composer, `zip`/`unzip` and (from #352)
  Node. Checked on the grounding image: `command -v git`, `node`, `unzip`
  all fail.
- **User:** the image ends with `USER 1000:1000`. The base image has no user
  with that uid; the number is enough. Tingle always overrides it with
  `--user <uid>:<gid>`.
- **Entrypoint:** `ENTRYPOINT ["php", "/opt/tingle_php_complexity/entrypoint.php"]`
  and no `CMD`. The entrypoint takes no arguments.
- The entrypoint calls each tool by absolute path:
  `/opt/tingle_php_complexity/vendor/bin/pdepend` and, from #352,
  `/usr/local/bin/jscpd`. It never calls Composer.

## 3. Pinned versions

| Component | Version | Pinned by | Added by |
|-----------|---------|-----------|----------|
| PHP | `8.5.11` | `ARG BASE_IMAGE` (tag + digest) | #346 |
| Composer (build only) | `2.10.3` | `ARG COMPOSER_IMAGE` (tag + digest) | #346 |
| PDepend | `3.0.0` | `composer.json` (`"pdepend/pdepend": "3.0.0"`) + `composer.lock` | #346 |
| Node (build only) | `24.21.0` | `ARG NODE_IMAGE` (tag + digest) | #352 |
| jscpd | `5.4.1` | `package.json` + `package-lock.json` | #352 |

`composer.json` is exactly what these commands produce:

```json
{
    "name": "tingle/php_complexity",
    "type": "project",
    "require": {
        "pdepend/pdepend": "3.0.0"
    },
    "config": {
        "platform": {
            "php": "8.5.11"
        }
    }
}
```

`composer.json` and `composer.lock` are generated inside the pinned Composer
image, from `docker/php_complexity/`, with `--no-install` so that no
`vendor/` is written into the repository:

```sh
docker run --rm --user "$(id -u):$(id -g)" -e COMPOSER_HOME=/tmp/composer \
  -v "$PWD/docker/php_complexity:/app" -w /app \
  composer:2.10.3@sha256:af98f42dfff7c68ba8d53c2164fd9fde1087b7d449514baa38c418b1f6bc4bac \
  sh -c 'composer init --no-interaction --name=tingle/php_complexity --type=project \
    && composer config platform.php 8.5.11 \
    && composer require --no-interaction --no-progress --no-install pdepend/pdepend:3.0.0'
```

`composer validate --no-check-publish` then reports the file valid, with two
accepted warnings (no license; an exact version constraint, which is the
point). The lock resolved, at the time of writing, to these 17 packages:

| Package | Version |
|---------|---------|
| `pdepend/pdepend` | `3.0.0` |
| `symfony/config` | `v8.1.5` |
| `symfony/dependency-injection`, `symfony/filesystem`, `symfony/var-exporter`, `symfony/yaml` | `v8.1.9` |
| `symfony/deprecation-contracts` | `v3.7.1` |
| `symfony/service-contracts` | `v3.7.3` |
| `symfony/polyfill-ctype` | `v1.37.0` |
| `symfony/polyfill-mbstring` | `v1.43.0` |
| `symfony/polyfill-deepclone` | `v1.43.2` |
| `psr/container` | `2.0.2` |
| `react/child-process` | `v0.6.7` |
| `react/event-loop` | `v1.6.0` |
| `react/stream` | `v1.4.0` |
| `evenement/evenement` | `v3.0.2` |
| `fidry/cpu-core-counter` | `1.4.1` |

The committed lock is the source of truth; #346 commits the lock it
generates with the commands above, and the smoke test checks
`tool_versions.pdepend == "3.0.0"`.

## 4. Entrypoint input

The entrypoint is the only process tingle talks to. It runs in `/src`, which
is read-only.

### Lines

- It reads all of stdin as bytes. Stdin that is not valid UTF-8
  (`mb_check_encoding($in, 'UTF-8')` is false) is an entrypoint failure
  (exit 1, section 8).
- It splits stdin on `\n`. A final `\n` does not start an extra line. Each
  resulting line is one **input line**, numbered from 1 (`<n>`). Nothing is
  trimmed: a `\r` or a space is part of the name.
- It receives no arguments.

### Refused lines (defence in depth)

Tingle's host-side selection never sends any of these lines. The entrypoint
still checks every line, in this order; the first rule that matches refuses
it:

| Rule | Warning message |
|------|-----------------|
| The line is empty. | `empty line` |
| The line starts with `/`. | `absolute path` |
| A `/`-separated segment is `..`. | `path has a '..' segment` |
| The same line appeared earlier (refused or not). | `duplicate line` |
| `/src/<line>` does not exist, is not a regular file, or its real path (symlinks resolved) is not inside `/src`. | `not a regular file under /src` |
| Its extension (the part after the last `.` of the name, lower-cased) is not `php`. | `unsupported extension` |
| Its name, lower-cased, ends with `.blade.php`. | `Blade template` |

A refused line is never read, never staged and never reaches a tool. It
still gets its `files` entry, in its position, with `parse_error: false`,
`pdepend: null`, `functions: null` and `duplication: null`, plus one
`warnings` entry `{"tool": "entrypoint", "path": <line>, "message":
<message>}`. So "one entry per input line" always holds. Tingle reports such
a file as `OK` with CCN 0 (see [cli.md](cli.md#817-refused-lines)).

## 5. Parse check and staged tree

### Parse check

Each accepted line's file is read once, from its real path, as bytes. The
entrypoint then runs PHP's own parser on those bytes, in-process:

```php
token_get_all($code, TOKEN_PARSE);
```

- If it throws a `CompileError` (`ParseError` extends it), the file is a
  **parse error**: `parse_error: true`, `pdepend`, `functions` and
  `duplication` stay `null`, and a `warnings` entry
  `{"tool": "php", "path": <line>, "message": "<getMessage()> on line <getLine()>"}`
  is added. The file is **not staged**, so no tool sees it.
- Otherwise the file is staged (below).

Why (README deviation 1): PDepend 3.0.0 accepts some invalid code without
any message. In the grounding run, `return $x /;` (`lenient.php`) was
reported by PDepend as a normal function with CCN 1, while PHP said
`syntax error, unexpected token ";" on line 5`. The parser is the image's PHP
8.5.11, so code that is invalid on PHP 8.5 (for example `match` used as a
function name) is a parse error even if it was valid on an older PHP.

There is **no UTF-8 check** on the file content: PHP source has no encoding
requirement, and both PHP and PDepend analysed an ISO-8859-1 file
(`latin1.php`) normally. PDepend converts names to UTF-8 in its XML, so the
merged JSON is always valid UTF-8.

### Staged tree

PDepend's input is a staged tree, and **every tool runs on the staged tree,
never on `/src`**. That way each tool sees exactly the selected files that
PHP could parse.

- **Copies.** The bytes of accepted line `<n>` are written to
  `/tmp/stage/<n>.php`. Copies, never symlinks.
- **Opaque names.** The relative path is not kept. PDepend's directory walk
  has filters that the entrypoint does not control: the default suffix list
  is `php,php5`, compared case-sensitively, and the directories `.git`,
  `.svn` and `CVS` are always ignored. In the grounding run, PDepend on the
  unstaged fixture silently dropped `UPPER.PHP` and `CVS/legacy.php`; staged
  as `<n>.php`, both were analysed. A file list on the command line would
  also hit argument-length limits on large repositories.
- **Mapping back.** PDepend reports `/tmp/stage/<n>.php` and jscpd reports
  `<n>.php` (relative to the scanned directory). The entrypoint parses `<n>`
  from that name and writes the result on the `files` entry of input line
  `<n>`. It never derives a path by stripping a prefix. A tool path that
  does not map to a staged file is an entrypoint failure (exit 1) for
  PDepend, and a jscpd failure for jscpd
  ([duplication.md](duplication.md#5-failure-handling)).
- **Only `/tmp`.** The entrypoint writes only under `/tmp`: the staged tree,
  PDepend's report and cache, and jscpd's report. It works with a read-only
  root file system (checked with `--read-only --tmpfs /tmp`).

## 6. PDepend invocation

When at least one file was staged, the entrypoint deletes
`/tmp/pdepend/summary.xml` if it exists, creates `/tmp/pdepend/` and
`/tmp/pdepend-cache/`, and runs, with the working directory `/tmp` and
`XDG_CACHE_HOME=/tmp/pdepend-cache` added to the environment:

```
/opt/tingle_php_complexity/vendor/bin/pdepend --quiet --summary-xml=/tmp/pdepend/summary.xml /tmp/stage
```

| Option or setting | Value | Why |
|-------------------|-------|-----|
| `--summary-xml` | `/tmp/pdepend/summary.xml` | The only report used. |
| `--quiet` | set | No progress output. Errors, the stack traces and PHP warnings are still printed (on stdout). |
| source | `/tmp/stage` | One directory; no file list on the command line. |
| `--suffix`, `--ignore`, `--exclude`, `--configuration`, `--coderank-mode` | not given | Staging makes the filters irrelevant; nothing else changes the metrics used. |
| working directory | `/tmp` | No file from the analysed tree can be picked up as configuration. |
| `XDG_CACHE_HOME` | `/tmp/pdepend-cache` | PDepend's file cache. With a foreign uid `HOME` is `/` and not writable; PDepend would fall back to the system temp dir, and the explicit value makes that deterministic. |
| `memory_limit` | not set | PDepend's launcher sets `memory_limit=-1` itself. |

- PDepend is run with `proc_open` and an argument array (no shell). Its
  stdout and stderr are captured, then written to the entrypoint's stderr
  (stdout first).
- With nothing staged (empty stdin, or every line refused or a parse error),
  PDepend is not run: every `pdepend` stays `null`.

### PDepend failure

| Case | Result |
|------|--------|
| PDepend exits non-zero | The entrypoint exits with PDepend's status, nothing on stdout. (Grounding: a missing source directory gave `Critical error:` on stdout and exit 2.) |
| PDepend is killed by a signal | Exit 1, `tingle_php_complexity: pdepend killed by signal <n>`. |
| PDepend exits 0 but `/tmp/pdepend/summary.xml` is missing | Exit 1, `tingle_php_complexity: pdepend wrote no summary XML`. PDepend exits 0 when it cannot write the report (README deviation 4). |
| The report is not well-formed XML, or its root is not `metrics` | Exit 1, `tingle_php_complexity: pdepend summary XML is not well-formed`. |
| A `name` in the report does not match `/tmp/stage/<n>.php` for a staged `<n>` | Exit 1, `tingle_php_complexity: pdepend reported an unknown path: <name>`. |
| A counted unit (section 7) lacks `start`, `ccn` or `npath`, or one of them is not an integer ≥ 1 | Exit 1, `tingle_php_complexity: pdepend summary XML has a malformed entry`. |

### Parse errors reported by PDepend

PDepend may reject a file PHP accepted (README deviation 2). It then still
exits 0, still writes partial data for the file into the XML, and prints an
error block on **stdout** (README deviation 3). Real output, from the
grounding run (the five PHP warnings come from the partial data of the
rejected file; stack trace cut after two frames):

```

Warning: unexpected NAN value was coerced to string in /opt/tingle_php_complexity/vendor/pdepend/pdepend/src/Report/Summary/Xml.php on line 427

The following error occurred:
Unexpected token: #[, line: 14, col: 20, file: /tmp/stage/7.php.
#0 /opt/tingle_php_complexity/vendor/pdepend/pdepend/src/Source/Language/PHP/AbstractPHPParser.php(8981): PDepend\Source\Parser\UnexpectedTokenException->__construct(...)
#1 /opt/tingle_php_complexity/vendor/pdepend/pdepend/src/Source/Language/PHP/AbstractPHPParser.php(8968): PDepend\Source\Language\PHP\AbstractPHPParser->getUnexpectedTokenException(...)
```

With several rejected files, the header is `The following errors occurred:`
and each file has its own line, each followed by its stack trace (or none).
Grounding, on a probe tree:

```
The following errors occurred:
Unexpected token: :, line: 10, col: 25, file: /src/a_broken.php.
Unexpected end of token stream in file: /src/b_truncated.php.
Unexpected token: {, line: 2, col: 7, file: /src/e_noname.php.
```

(stack frames removed). The entrypoint scans PDepend's stdout:

1. A line that is exactly `The following error occurred:` or
   `The following errors occurred:` starts the block. The block ends at the
   next empty line (or at the end of the output).
2. In the block, lines matching `^#\d+ ` are stack frames and are skipped.
3. Every other line is matched against
   `^(.*?),? (?:in )?file: /tmp/stage/(\d+)\.php\.$`. When it matches a
   staged `<n>`, input line `<n>` becomes a parse error: `parse_error: true`,
   all its XML data is discarded (`pdepend`, `functions`, `duplication` stay
   `null`), and a `warnings` entry
   `{"tool": "pdepend", "path": <line>, "message": <group 1>}` is added, for
   example `"Unexpected token: #[, line: 14, col: 20"` or
   `"Unexpected end of token stream"`.
4. A line in the block that does not match is kept as a path-less warning
   `{"tool": "pdepend", "message": <line>}`. It is not fatal.

## 7. Merged JSON

On success, stdout holds exactly one JSON object followed by `\n`, encoded
with `JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE`.
Nothing else is written to stdout.

```json
{
  "tool_versions": {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": null},
  "files": [ <one entry per input line, in input order> ],
  "warnings": [ <warning entries> ]
}
```

### XML → JSON mapping

PDepend 3.0.0's summary XML (real excerpt in section 10) has:

- `metrics/files/file` with `name` and file-level `loc`, `cloc`, `eloc`,
  `lloc`, `ncloc`. Only files with at least one class, trait or function are
  listed (README deviation 6).
- `metrics/package` (one per namespace; `+global` for the global namespace),
  whose children are:
  - `class` and `trait`, each with one `file` child (`name`) and `method`
    children;
  - `function`, with one `file` child;
  - bare `method` elements with **no** `file`: enum methods and some
    anonymous-class methods (README deviation 7).
- Interfaces are never listed.
- On every `method` and `function`: `start`, `end`, `ccn`, `ccn2`, `npath`,
  `loc`, `cloc`, `eloc`, `lloc`, `ncloc`, `mi` and the Halstead attributes
  `hnt`, `hnd`, `hv`, `hd`, `hl`, `he`, `ht`, `hb`, `hi`. In the calibration
  runs (36,000 units) every method and function under a `class`, `trait` or
  `function` with a `file` had all of `start`, `ccn`, `ccn2`, `npath`, `mi`
  and `lloc`; only bare methods lacked `mi` and `lloc`.

The entrypoint builds, for each staged line `<n>` that is not a parse error:

- **Counted units:** every `method` of a `class` or `trait` whose `file` is
  `/tmp/stage/<n>.php`, named `<class or trait @name>::<method @name>`
  (`Calculator::grade`; the short name, without the namespace), and every
  `function` whose `file` is `/tmp/stage/<n>.php`, named `@name` (`clamp`).
  Bare `method` elements, and `class`/`trait`/`function` elements without a
  `file` child, are never counted. Abstract methods of an abstract class are
  counted as PDepend reports them (`ccn` 1).
- **`pdepend`**, when `<n>` has a `metrics/files/file` entry:

| Key | Value |
|-----|-------|
| `ccn` | Sum of the counted units' `ccn` (int ≥ 0; `0` with no unit). This is the **total CCN**. |
| `max_ccn` | Highest `ccn` of a counted unit; `null` with no unit. |
| `max_npath` | Highest `npath` of a counted unit; `null` with no unit. Can exceed 2^53 (README deviation 10). |
| `min_mi` | Lowest finite `mi` of a counted unit, as a JSON number (unrounded); `null` with no unit or no finite value. |
| `lloc` | The file entry's `lloc` (int ≥ 0). |

  When `<n>` has no `metrics/files/file` entry, `pdepend` is `null`.
  (PDepend 3.0.0 never reports a unit for a file without an entry; if it
  ever does, that is a malformed report, exit 1.)
- **`functions`** (#351; `null` for every entry before #351): the counted
  units in source order (by `line`, then `name`), each
  `{"name": str, "line": <start>, "ccn": int ≥ 1, "npath": int ≥ 1}`; `[]`
  when there is none (also when `pdepend` is `null`). See
  [details.md](details.md#3-functions).
- **`duplication`** (#352; `null` for every entry before #352): see
  [duplication.md](duplication.md#3-per-file-duplicated-lines).

`ccn2` (which also counts `&&`/`||`), `loc`/`eloc`/`ncloc`, the unit-level
`lloc` and the Halstead attributes are not used. `ccn` is the McCabe count
#344 chose.

### Keys and types

| Key | Type | Rule |
|-----|------|------|
| `tool_versions` | object | Always present. |
| `tool_versions.php` | str | `PHP_VERSION` (`"8.5.11"`). |
| `tool_versions.pdepend` | str | `Composer\InstalledVersions::getPrettyVersion('pdepend/pdepend')` (`"3.0.0"`). The XML's own `pdepend` attribute is `@package_version@` (README deviation 5). |
| `tool_versions.jscpd` | str or `null` | `"5.4.1"` from #352; `null` before. |
| `files` | list | Exactly one entry per input line, in input order. |
| `files[].path` | str | The input line, exactly as received. |
| `files[].parse_error` | bool | `true` when PHP's parser (section 5) or PDepend (section 6) rejected the file. |
| `files[].pdepend` | object or `null` | As above. `null` when `parse_error` is `true`, when the line was refused, or when PDepend listed no file entry for it. |
| `files[].functions` | list or `null` | As above. |
| `files[].duplication` | object or `null` | `{"lines": int ≥ 0}` from #352. |
| `warnings` | list | Entries in the order below. |
| `warnings[].tool` | str | `"entrypoint"`, `"php"`, `"pdepend"` or `"jscpd"`. |
| `warnings[].message` | str | One line. |
| `warnings[].path` | str (optional) | The input line the warning is about. Absent for a warning about a whole tool run. |

**Warning order:** the `entrypoint` and `php` warnings in input order (each
line produces at most one), then the `pdepend` warnings (the per-file ones
in input order, then the path-less ones in output order), then the `jscpd`
warning (#352).

Rules:

- **`null` means not available; `[]` or `0` means available and empty.**
- When `parse_error` is `true`, `pdepend`, `functions` and `duplication` are
  all `null`.
- **No version field, no negotiation.** The image and the CLI share the
  tingle tag. For tingle, a missing key or a value of the wrong type is an
  unparsable-output error (exit 1). Unknown extra keys are ignored by tingle.
- #346 emits every key above. #351 and #352 only fill in their parts. They
  never add or rename a key.

### Per-file states

| State | `parse_error` | `pdepend` | `warnings` entry for the path | Report |
|-------|---------------|-----------|-------------------------------|--------|
| Normal | `false` | object | none | normal row |
| Rejected by PHP | `true` | `null` | `tool: "php"` | `⛔ PARSE` row |
| Rejected by PDepend | `true` | `null` | `tool: "pdepend"` | `⛔ PARSE` row |
| No class, trait or function (top-level code only, empty, enums or interfaces only) | `false` | `null` | none | `OK`, CCN 0 |
| Refused line (section 4) | `false` | `null` | `tool: "entrypoint"` | `OK`, CCN 0 |

### Example

Real output of the grounding run (section 10) on the smoke-test input, with
#351 and #352 already applied, trimmed to some entries. #346 emits the same
document with `"jscpd": null` and every `functions` and `duplication` set
to `null`:

```json
{
  "tool_versions": {"php": "8.5.11", "pdepend": "3.0.0", "jscpd": "5.4.1"},
  "files": [
    {"path": "Calculator.php", "parse_error": false,
     "pdepend": {"ccn": 11, "max_ccn": 7, "max_npath": 36, "min_mi": 53.875623305512, "lloc": 22},
     "functions": [
       {"name": "Calculator::add", "line": 7, "ccn": 1, "npath": 1},
       {"name": "Calculator::sign", "line": 12, "ccn": 3, "npath": 3},
       {"name": "Calculator::grade", "line": 22, "ccn": 7, "npath": 36}],
     "duplication": {"lines": 0}},
    {"path": "attr_anon.php", "parse_error": true, "pdepend": null, "functions": null, "duplication": null},
    {"path": "bootstrap.php", "parse_error": false, "pdepend": null, "functions": [], "duplication": {"lines": 0}},
    {"path": "broken.php", "parse_error": true, "pdepend": null, "functions": null, "duplication": null},
    {"path": "dup_a.php", "parse_error": false,
     "pdepend": {"ccn": 3, "max_ccn": 3, "max_npath": 4, "min_mi": 58.109128232969, "lloc": 9},
     "functions": [{"name": "normalize_a", "line": 3, "ccn": 3, "npath": 4}],
     "duplication": {"lines": 13}},
    {"path": "welcome.blade.php", "parse_error": false, "pdepend": null, "functions": null, "duplication": null},
    {"path": "../outside.php", "parse_error": false, "pdepend": null, "functions": null, "duplication": null}
  ],
  "warnings": [
    {"tool": "php", "path": "broken.php", "message": "syntax error, unexpected token \":\", expecting variable on line 10"},
    {"tool": "php", "path": "lenient.php", "message": "syntax error, unexpected token \";\" on line 5"},
    {"tool": "entrypoint", "path": "welcome.blade.php", "message": "Blade template"},
    {"tool": "entrypoint", "path": "", "message": "empty line"},
    {"tool": "entrypoint", "path": "/etc/passwd", "message": "absolute path"},
    {"tool": "entrypoint", "path": "../outside.php", "message": "path has a '..' segment"},
    {"tool": "entrypoint", "path": "Calculator.php", "message": "duplicate line"},
    {"tool": "entrypoint", "path": "missing.php", "message": "not a regular file under /src"},
    {"tool": "entrypoint", "path": "notes.txt", "message": "unsupported extension"},
    {"tool": "pdepend", "path": "attr_anon.php", "message": "Unexpected token: #[, line: 14, col: 20"}
  ]
}
```

## 8. Exit status, empty input and encoding

| Status | When |
|--------|------|
| `0` | The JSON was printed, including when some or all files are parse errors or refused, and when jscpd failed. |
| PDepend's status (non-zero) | PDepend exited non-zero. Nothing is printed on stdout. |
| `1` | Any other entrypoint failure: stdin not valid UTF-8, the PDepend version unreadable, PDepend killed by a signal, the report missing or malformed, an unknown path in the report, or an unexpected error. A one-line reason prefixed with `tingle_php_complexity: ` goes to stderr. Nothing is printed on stdout. |

- With empty stdin (no input line), no tool runs and the entrypoint prints
  `{"tool_versions":{...},"files":[],"warnings":[]}` (with the versions
  filled as usual) and exits 0. Tingle never starts the container with an
  empty list, but the image must handle it. Grounding output:
  `{"tool_versions":{"php":"8.5.11","pdepend":"3.0.0","jscpd":"5.4.1"},"files":[],"warnings":[]}`
  (with #352 applied).
- A jscpd failure is never fatal
  ([duplication.md](duplication.md#5-failure-handling)).

### Encoding and line endings

Recorded in the grounding run:

- **CRLF** (`crlf.php`) and **UTF-8 BOM** (`bom.php`): the same function as
  `CVS/legacy.php` gave the same `ccn` (2), `npath` (2), `mi`
  (79.502485917776), `lloc` (2) and `start` (3) with LF, CRLF and a leading
  BOM.
- **Not valid UTF-8** (`latin1.php`, ISO-8859-1 bytes in a comment and a
  string): parsed by PHP and PDepend; a normal row.
- `Lines` follows PDepend's file `lloc` as reported. Tingle never recounts.

## 9. Smoke-test fixture

`docker/php_complexity/fixture/` holds the grounding set. #346 creates every
file with the content given in [section 9.1](#91-fixture-contents); the
expectations of later sub-issues are checked once they land.

**stdin** of the smoke test, in this order (19 fixture files, then six
hostile lines):

```
Anon.php
CVS/legacy.php
Calculator.php
Modern.php
Shapes.php
UPPER.PHP
attr_anon.php
bom.php
bootstrap.php
broken.php
crlf.php
dup_a.php
dup_b.php
empty.php
helpers.php
latin1.php
lenient.php
page.php
welcome.blade.php
<empty line>
/etc/passwd
../outside.php
Calculator.php
missing.php
notes.txt
```

`notes.txt` is a fixture file (`Not PHP.\n`); `missing.php` does not exist.

| # | File | What it proves | `parse_error` | `pdepend` (`ccn`, `max_ccn`, `max_npath`, `min_mi`, `lloc`) | Warning | `functions` (#351) | `duplication.lines` (#352) |
|---|------|----------------|---------------|-------------------------------------------------------------|---------|--------------------|----------------------------|
| 1 | `Anon.php` | A method returning an anonymous class that extends a fixture class: the bare `label` is not counted. | `false` | 2, 2, 4, 66.28…, 6 | — | `Factory::make` (line 9, ccn 2) | 0 |
| 2 | `CVS/legacy.php` | PDepend's `CVS` filter is bypassed. | `false` | 2, 2, 2, 79.50…, 2 | — | `legacy` (3) | 0 |
| 3 | `Calculator.php` | A class with methods of CCN 1, 3 and 7. | `false` | 11, 7, 36, 53.88…, 22 | — | `Calculator::add` (7), `::sign` (12), `::grade` (22) | 0 |
| 4 | `Modern.php` | PHP 8.3 syntax (enum, readonly class, typed constant); enum methods not counted. | `false` | 2, 1, 1, 79.27…, 11 | — | `Point::__construct` (21), `Point::withX` (25) | 0 |
| 5 | `Shapes.php` | An interface, two classes and a trait in one file. | `false` | 6, 2, 2, 77.64…, 11 | — | 5 entries, `Square::…`, `Circle::…`, `Describes::describe` | 0 |
| 6 | `UPPER.PHP` | Upper-case extension; PDepend's case-sensitive suffix filter is bypassed. | `false` | 2, 2, 2, 77.75…, 2 | — | `shout` (3) | 0 |
| 7 | `attr_anon.php` | Valid PHP that PDepend rejects (attribute on an anonymous class). | `true` | `null` | `pdepend`: `Unexpected token: #[, line: 14, col: 20` | `null` | `null` |
| 8 | `bom.php` | UTF-8 BOM. | `false` | 2, 2, 2, 79.50…, 2 | — | `bom` (3) | 0 |
| 9 | `bootstrap.php` | Top-level code only (branches and a loop): absent from the XML. | `false` | `null` | — | `[]` | 0 |
| 10 | `broken.php` | A syntax error. | `true` | `null` | `php`: `syntax error, unexpected token ":", expecting variable on line 10` | `null` | `null` |
| 11 | `crlf.php` | CRLF line endings. | `false` | 2, 2, 2, 79.50…, 2 | — | `crlf` (3) | 0 |
| 12 | `dup_a.php` | Clone with `dup_b.php`. | `false` | 3, 3, 4, 58.11…, 9 | — | `normalize_a` (3) | 13 |
| 13 | `dup_b.php` | Clone with `dup_a.php`. | `false` | 3, 3, 4, 58.11…, 9 | — | `normalize_b` (3) | 13 |
| 14 | `empty.php` | Empty (0 bytes). | `false` | `null` | — | `[]` | 0 |
| 15 | `helpers.php` | Two functions plus top-level closures (not counted). | `false` | 4, 3, 4, 66.49…, 12 | — | `clamp` (3), `greet` (14) | 0 |
| 16 | `latin1.php` | ISO-8859-1 bytes. | `false` | 1, 1, 1, 83.13…, 2 | — | `latin` (4) | 0 |
| 17 | `lenient.php` | Invalid PHP that PDepend accepts. | `true` | `null` | `php`: `syntax error, unexpected token ";" on line 5` | `null` | `null` |
| 18 | `page.php` | Mixed HTML/PHP: one inline function; top-level `if` not counted. | `false` | 2, 2, 2, 89.71…, 4 | — | `title` (4) | 0 |
| 19 | `welcome.blade.php` | Blade refused by the image. | `false` | `null` | `entrypoint`: `Blade template` | `null` | `null` |
| 20–25 | the hostile lines | Refused. | `false` | `null` | `entrypoint`: `empty line`, `absolute path`, `path has a '..' segment`, `duplicate line`, `not a regular file under /src`, `unsupported extension` | `null` | `null` |

The `min_mi` values are PDepend's unrounded floats; the smoke test compares
them to one decimal (`round(min_mi, 1)`: 66.3, 79.5, 53.9, 79.3, 77.6, 77.8,
79.5, 79.5, 58.1, 58.1, 66.5, 83.1, 89.7).

The smoke test runs the canonical run line with `-v <fixture>:/src:ro` and
`--user 501:20`, pipes the stdin above, and asserts that:

- the exit status is 0, and stdout parses as one JSON object;
- `tool_versions.php` is `"8.5.11"` and `tool_versions.pdepend` is
  `"3.0.0"` (from #352, `tool_versions.jscpd` is `"5.4.1"`; before, it is
  `null`);
- `files` has 25 entries, and `files[i].path` is input line `i`;
- the per-file expectations in the table hold (`functions` from #351 and
  `duplication` from #352; before, both are `null` everywhere);
- `warnings` holds exactly the warnings in the table, with the `tool`,
  `path` and `message` shown;
- `command -v git` fails inside the image (with `--entrypoint sh`);
- empty stdin prints `"files": []` and `"warnings": []`, with exit 0.

### 9.1 Fixture contents

Every file ends with a newline unless stated otherwise. Indentation is four
spaces.

`Calculator.php`:

```php
<?php

namespace App;

class Calculator
{
    public function add(int $a, int $b): int
    {
        return $a + $b;
    }

    public function sign(int $n): string
    {
        if ($n > 0) {
            return 'positive';
        } elseif ($n < 0) {
            return 'negative';
        }
        return 'zero';
    }

    public function grade(int $score, bool $bonus): string
    {
        if ($bonus && $score > 0) {
            $score += 5;
        }
        foreach ([90 => 'A', 80 => 'B', 70 => 'C'] as $min => $letter) {
            if ($score >= $min) {
                return $letter;
            }
        }
        switch (true) {
            case $score >= 60:
                return 'D';
            case $score >= 50:
                return 'E';
            default:
                return $score > 0 ? 'F' : 'X';
        }
    }
}
```

`Shapes.php`:

```php
<?php

namespace App\Shapes;

interface Shape
{
    public function area(): float;
}

class Square implements Shape
{
    public function __construct(private float $side)
    {
    }

    public function area(): float
    {
        return $this->side ** 2;
    }
}

class Circle implements Shape
{
    public function __construct(private float $radius)
    {
    }

    public function area(): float
    {
        return $this->radius > 0 ? M_PI * $this->radius ** 2 : 0.0;
    }
}

trait Describes
{
    public function describe(): string
    {
        return static::class;
    }
}
```

`Anon.php`:

```php
<?php

namespace App\Anon;

use App\Shapes\Square;

class Factory
{
    public function make(bool $big): Square
    {
        return new class ($big ? 10.0 : 1.0) extends Square {
            public function label(): string
            {
                return $this->area() > 50 ? 'big' : 'small';
            }
        };
    }
}
```

`Modern.php`:

```php
<?php

namespace App\Modern;

enum Suit: string
{
    case Hearts = 'H';
    case Spades = 'S';

    public function color(): string
    {
        return match ($this) {
            Suit::Hearts => 'Red',
            Suit::Spades => 'Black',
        };
    }
}

readonly class Point
{
    public function __construct(public int $x, public int $y)
    {
    }

    public function withX(int $x): static
    {
        return new static($x, $this->y);
    }
}

interface HasVersion
{
    const string VERSION = '1.0';
}
```

`helpers.php`:

```php
<?php

function clamp(int $value, int $min, int $max): int
{
    if ($value < $min) {
        return $min;
    }
    if ($value > $max) {
        return $max;
    }
    return $value;
}

function greet(?string $name): string
{
    return 'Hello, ' . ($name ?? 'world');
}

$double = fn (int $x): int => $x * 2;
$triple = function (int $x): int {
    return $x > 0 ? $x * 3 : 0;
};
```

`bootstrap.php`:

```php
<?php

$config = ['debug' => true, 'level' => 3];

if ($config['debug']) {
    error_reporting(E_ALL);
} elseif ($config['level'] > 2) {
    error_reporting(E_WARNING);
}

foreach ($config as $key => $value) {
    if ($value && $key !== 'level') {
        echo $key, PHP_EOL;
    }
}
```

`page.php`:

```php
<!DOCTYPE html>
<html>
<body>
<?php function title(string $t): string { return $t !== '' ? $t : 'Untitled'; } ?>
<h1><?= title('Home') ?></h1>
<?php if (isset($user)): ?>
  <p>Welcome back</p>
<?php else: ?>
  <p>Please log in</p>
<?php endif; ?>
</body>
</html>
```

`attr_anon.php`:

```php
<?php

namespace App\Attr;

#[\Attribute]
class Tag
{
}

class Maker
{
    public function make(): object
    {
        return new #[Tag] class {
            public function ok(): bool
            {
                return true;
            }
        };
    }
}
```

`broken.php`:

```php
<?php

class Broken
{
    public function ok(): int
    {
        return 1;
    }

    public function bad(: int
    {
        return 2;
    }
}
```

`lenient.php`:

```php
<?php

function half(int $x): int
{
    return $x /;
}
```

`dup_a.php` (and `dup_b.php`, identical except `normalize_a` →
`normalize_b`):

```php
<?php

function normalize_a(array $rows): array
{
    $result = [];
    foreach ($rows as $row) {
        $name = trim((string) ($row['name'] ?? ''));
        $email = strtolower(trim((string) ($row['email'] ?? '')));
        if ($name === '' || $email === '') {
            continue;
        }
        $result[] = ['name' => $name, 'email' => $email, 'active' => (bool) ($row['active'] ?? false)];
    }
    return $result;
}
```

`UPPER.PHP`:

```php
<?php

function shout(string $s): string
{
    return $s === '' ? '' : strtoupper($s) . '!';
}
```

`CVS/legacy.php`:

```php
<?php

function legacy(int $x): int
{
    return $x > 0 ? $x : -$x;
}
```

`crlf.php` and `bom.php`: the same function as `CVS/legacy.php`, named
`crlf` and `bom`. `crlf.php` uses `\r\n` line endings; `bom.php` starts with
the bytes `EF BB BF` before `<?php`. Exactly:

```sh
printf '<?php\r\n\r\nfunction crlf(int $x): int\r\n{\r\n    return $x > 0 ? $x : -$x;\r\n}\r\n' > crlf.php
printf '\xef\xbb\xbf<?php\n\nfunction bom(int $x): int\n{\n    return $x > 0 ? $x : -$x;\n}\n' > bom.php
```

`latin1.php` (ISO-8859-1 `é` and `à`):

```sh
printf '<?php\n\n// Caf\xe9\nfunction latin(): string\n{\n    return "d\xe9j\xe0 vu";\n}\n' > latin1.php
```

`welcome.blade.php`:

```
<html>
<body>
@if ($user)
    <h1>Hello, {{ $user->name }}</h1>
@else
    <h1>Hello, guest</h1>
@endif
</body>
</html>
```

`empty.php`: 0 bytes. `notes.txt`: `Not PHP.` and a newline.

## 10. Grounding run

The run behind these specs was throwaway: a scratch directory, a throwaway
image built from the pins above with a prototype entrypoint, nothing
committed. Repeat it when bumping a version.

**Versions:** `php:8.5.11-cli-trixie` (digest above, Debian 13.7), Composer
`2.10.3` (build stage), PDepend `3.0.0` (`pdepend --version`:
`PDepend 3.0.0`), Node `24.21.0` (build stage), jscpd `5.4.1` (native
binary).

**Environment:** the tools were installed in a networked build, then every
run used

```
docker run --rm -i --pull never --network none --security-opt no-new-privileges \
  --read-only --tmpfs /tmp --user 501:20 -v <fixture>:/src:ro -w /src <throwaway image>
```

Everything worked with no network, a read-only `/src`, a read-only root file
system and a foreign uid (`HOME=/`). The run was repeated on `linux/amd64`
(emulated on an arm64 host): the merged JSON was byte-identical to the
`linux/arm64` one.

**Command** (inside the image, from the entrypoint):

```
/opt/tingle_php_complexity/vendor/bin/pdepend --quiet --summary-xml=/tmp/pdepend/summary.xml /tmp/stage
```

on `/tmp/stage/<n>.php` for the accepted, PHP-parsable lines of the stdin in
section 9 (`<n>` 1–9, 11–16 and 18; `broken.php` and `lenient.php` were not
staged). PDepend exit status: 0.

**Summary XML** (trimmed: the root's project-wide attributes, the class-level
attributes other than `name`/`fqname`/`start`/`end`, every Halstead
attribute and most entries removed; `7.php` is `attr_anon.php`, which
PDepend rejected):

```xml
<metrics generated="2026-10-17T17:27:48" pdepend="@package_version@" ccn="46" ccn2="49" ...>
  <files>
    <file name="/tmp/stage/7.php" loc="22" cloc="0" eloc="0" lloc="0" ncloc="22"/>
    <file name="/tmp/stage/15.php" loc="23" cloc="0" eloc="19" lloc="12" ncloc="23"/>
    <file name="/tmp/stage/1.php" loc="19" cloc="0" eloc="15" lloc="6" ncloc="19"/>
    <file name="/tmp/stage/3.php" loc="42" cloc="0" eloc="37" lloc="22" ncloc="42"/>
    <file name="/tmp/stage/4.php" loc="35" cloc="0" eloc="28" lloc="11" ncloc="35"/>
    ...
  </files>
  <package name="+global" noc="1" noi="0" nom="1" nof="10">
    <method name="label" start="12" end="15" ccn="2" ccn2="2"/>
    <class name="Maker" fqname="Maker" start="0" end="0" ...>
      <file name="/tmp/stage/7.php"/>
      <method name="make" start="0" end="0" mi="0" npath="1" loc="1" cloc="0" eloc="0" lloc="0" ncloc="1" ccn="1" ccn2="1"/>
    </class>
    <function name="clamp" start="3" end="12" mi="66.486020616616" npath="4" loc="10" cloc="0" eloc="9" lloc="5" ncloc="10" ccn="3" ccn2="3">
      <file name="/tmp/stage/15.php"/>
    </function>
    ...
  </package>
  <package name="App\Anon" noc="1" noi="0" nom="1" nof="0">
    <class name="Factory" fqname="App\Anon\Factory" start="7" end="18" ...>
      <file name="/tmp/stage/1.php"/>
      <method name="make" start="9" end="17" mi="66.280553464404" npath="4" loc="9" cloc="0" eloc="8" lloc="3" ncloc="9" ccn="2" ccn2="2"/>
    </class>
  </package>
  <package name="App" noc="1" noi="0" nom="3" nof="0">
    <class name="Calculator" fqname="App\Calculator" start="5" end="41" ...>
      <file name="/tmp/stage/3.php"/>
      <method name="add" start="7" end="10" mi="80.401219851729" npath="1" loc="4" cloc="0" eloc="3" lloc="1" ncloc="4" ccn="1" ccn2="1"/>
      <method name="sign" start="12" end="20" mi="66.659404526848" npath="3" loc="9" cloc="0" eloc="8" lloc="5" ncloc="9" ccn="3" ccn2="3"/>
      <method name="grade" start="22" end="40" mi="53.875623305512" npath="36" loc="19" cloc="0" eloc="18" lloc="12" ncloc="19" ccn="7" ccn2="8"/>
    </class>
  </package>
  <package name="App\Modern" noc="1" noi="1" nom="2" nof="0">
    <method name="color" start="10" end="16" mi="70.480752418213" npath="1" loc="7" cloc="0" eloc="6" lloc="1" ncloc="7" ccn="1" ccn2="1"/>
    <class name="Point" fqname="App\Modern\Point" start="19" end="29" ...>
      <file name="/tmp/stage/4.php"/>
      <method name="__construct" start="21" end="23" mi="91.191023588314" npath="1" ... ccn="1" ccn2="1"/>
      <method name="withX" start="25" end="28" mi="79.267620989406" npath="1" ... ccn="1" ccn2="1"/>
    </class>
  </package>
  <package name="App\Shapes" noc="2" noi="1" nom="5" nof="0">
    ...
    <trait name="Describes" fqname="App\Shapes\Describes" start="34" end="40">
      <file name="/tmp/stage/5.php"/>
      <method name="describe" start="36" end="39" mi="81.120955834208" npath="1" ... ccn="1" ccn2="1"/>
    </trait>
  </package>
</metrics>
```

What it shows:

- `bootstrap.php` (9), `empty.php` (14) have no `<file>` entry (README
  deviation 6). Neither has `welcome.blade.php` when it is not refused.
- `Suit::color` (`App\Modern`) and the anonymous class's `label` (`+global`)
  are bare `<method>` elements without a `file` (README deviation 7).
- The rejected `attr_anon.php` still has a `<file>` entry and a `Maker`
  class with `start="0"`, `mi="0"`, moved to `+global` (its namespace was
  lost); its `Tag` class is listed under `App\Attr`. All of it is discarded.
- `ccn2` is higher than `ccn` where `&&`/`||` occur (`grade`: 7 vs 8).

**Probes** (separate throwaway trees, same image):

- A file with only an interface, or only an enum, has no `<file>` entry. A
  class with properties but no method has one (`lloc` 1), with total CCN 0.
- A PHP 8.4 property hook (`set(string $value) { ... ? ... : ...; }`)
  parsed, but its class had `nom="0"` and the decision was counted nowhere
  (README deviation 8). The PHP 8.5 pipe operator (`|>`) parsed.
- Anonymous-class methods are reported inconsistently. Across five probes
  (an anonymous class returned from a method, with or without a parent
  class or trait of the analysed set, alone or inside an `if`), their
  decisions were folded into the enclosing method's `ccn` in some cases and
  not in others, and some also appeared as bare `<method>` elements: bare
  and not folded (`Anon.php`), bare and folded (a probe with a namespaced
  parent class), neither (a probe inside an `if`), folded only (two probes)
  (README deviation 7). Ignoring bare methods is the only rule that never
  counts a decision twice.
- `pdepend --summary-xml=/nonexistent/s.xml` printed
  `Warning: file_put_contents(/nonexistent/s.xml): Failed to open stream: No such file or directory`
  and exited 0 (README deviation 4).
- PDepend run directly on an **unstaged** tree (`pdepend --summary-xml=...
  /src`): on an earlier version of the fixture it reported
  `Parsing 12 source files` for 13 PHP files, `UPPER.PHP` being dropped by
  its case-sensitive suffix filter (default `php,php5`); on a probe tree
  with `CVS/c.php`, `.hidden/h.php` and `build/b.php`, only `CVS/c.php` was
  missing from the report. Its default ignore list is `.git`, `.svn`, `CVS`
  (`PDepend\TextUI\Runner::$excludeDirectories`).

## 11. Runtime environment

Tingle runs the image with the canonical line from
[README.md](README.md#9-image-contract-summary). The image must work under
that line for any `<uid>:<gid>`, with no network and with `/src` read-only.
It writes only under `/tmp`. The staged copies need as much space in `/tmp`
as the selected files, and PDepend's memory grows with the selection (a
peak of 2,047 MB for the 3,028 files of `laravel/framework`, 40 s on the
grounding host).

## 12. Local build

The root `Makefile` gets a `php-complexity-image` target next to
`js-complexity-image` (added to `.PHONY`), with one recipe line:

```sh
docker build -t tingle_php_complexity:dev docker/php_complexity
```

It builds `tingle_php_complexity:dev` for the host architecture, used with
`tingle code_check php_complexity <path> --image tingle_php_complexity:dev`
before the image is published.

Verification for #346: `docker buildx build --platform linux/amd64
docker/php_complexity` and the same for `linux/arm64` succeed, and the smoke
test passes against `tingle_php_complexity:dev`.

## 13. Bumping versions

Nothing bumps the pins automatically. Each bump is a deliberate change:

1. **PHP:** update `ARG BASE_IMAGE` (tag and index digest, from
   `docker buildx imagetools inspect php:<version>-cli-trixie`). Keep the
   Debian variant with amd64 and arm64. A new PHP minor changes what the
   parse check accepts (section 5).
2. **Composer:** update `ARG COMPOSER_IMAGE` (tag and digest).
3. **PDepend:** update the version in `composer.json` and the
   `config.platform.php` value, then regenerate `composer.lock` with the
   commands in section 3. Check the summary XML shape, the error block
   format (section 6) and the bare-method behaviour (section 7) again.
4. **Node / jscpd** (#352): see [duplication.md](duplication.md#1-image-changes).
5. Re-run the grounding run (section 10) and the smoke test on both
   platforms. If a tool's output shape, a pinned option or a result in the
   fixture table changed, update this spec (or, once the specs are removed,
   `docs/agents/tingle-php-complexity-image.md`), the entrypoint and the
   Python parser in the same change.
