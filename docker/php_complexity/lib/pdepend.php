<?php

declare(strict_types=1);

// PDepend invocation, error block and summary XML (image.md sections 6 and 7).

const TPC_PDEPEND_BIN = '/opt/tingle_php_complexity/vendor/bin/pdepend';
const TPC_PDEPEND_DIR = '/tmp/pdepend';
const TPC_PDEPEND_CACHE = '/tmp/pdepend-cache';
const TPC_SUMMARY_XML = '/tmp/pdepend/summary.xml';

/** PDepend's version, from Composer's runtime API. */
function tpc_pdepend_version(): string
{
    try {
        $version = Composer\InstalledVersions::getPrettyVersion('pdepend/pdepend');
    } catch (Throwable) {
        $version = null;
    }
    if (!is_string($version) || $version === '') {
        throw new EntrypointError('cannot read the pdepend version');
    }
    return $version;
}

/**
 * Runs PDepend on /tmp/stage (no shell) and returns its stdout. Its stdout,
 * then its stderr, are copied to stderr.
 */
function tpc_run_pdepend(): string
{
    if (file_exists(TPC_SUMMARY_XML)) {
        unlink(TPC_SUMMARY_XML);
    }
    foreach ([TPC_PDEPEND_DIR, TPC_PDEPEND_CACHE] as $dir) {
        if (!is_dir($dir) && !mkdir($dir, 0700, true)) {
            throw new EntrypointError('cannot create ' . $dir);
        }
    }
    $stdoutFile = TPC_PDEPEND_DIR . '/stdout';
    $stderrFile = TPC_PDEPEND_DIR . '/stderr';

    $env = getenv();
    $env['XDG_CACHE_HOME'] = TPC_PDEPEND_CACHE;

    $process = proc_open(
        [TPC_PDEPEND_BIN, '--quiet', '--summary-xml=' . TPC_SUMMARY_XML, TPC_STAGE_DIR],
        [
            0 => ['file', '/dev/null', 'r'],
            1 => ['file', $stdoutFile, 'w'],
            2 => ['file', $stderrFile, 'w'],
        ],
        $pipes,
        '/tmp',
        $env,
    );
    if (!is_resource($process)) {
        throw new EntrypointError('cannot start pdepend');
    }
    do {
        $status = proc_get_status($process);
        if ($status['running']) {
            usleep(20000);
        }
    } while ($status['running']);
    proc_close($process);

    $stdout = (string) file_get_contents($stdoutFile);
    $stderr = (string) file_get_contents($stderrFile);
    fwrite(STDERR, $stdout);
    fwrite(STDERR, $stderr);

    if ($status['signaled']) {
        throw new EntrypointError('pdepend killed by signal ' . $status['termsig']);
    }
    $exit = $status['exitcode'];
    if ($exit !== 0) {
        throw new EntrypointError('pdepend exited with status ' . $exit, $exit > 0 ? $exit : 1);
    }
    return $stdout;
}

/**
 * Scans PDepend's stdout for its error block(s).
 *
 * @param array<int, true> $staged staged line numbers
 * @return array{0: array<int, string>, 1: list<string>} per-file messages by
 *         line number (first one kept), and the path-less messages
 */
function tpc_scan_pdepend_errors(string $stdout, array $staged): array
{
    $perFile = [];
    $pathless = [];
    $inBlock = false;
    foreach (preg_split('/\r?\n/', $stdout) as $line) {
        if (!$inBlock) {
            if ($line === 'The following error occurred:' || $line === 'The following errors occurred:') {
                $inBlock = true;
            }
            continue;
        }
        if ($line === '') {
            $inBlock = false;
            continue;
        }
        if (preg_match('/^#\d+ /', $line)) {
            continue;
        }
        if (preg_match('/^(.*?),? (?:in )?file: \/tmp\/stage\/(\d+)\.php\.$/', $line, $m)
            && isset($staged[(int) $m[2]]) && $m[2] === (string) (int) $m[2]) {
            $n = (int) $m[2];
            if (!isset($perFile[$n])) {
                $perFile[$n] = $m[1];
            }
            continue;
        }
        $pathless[] = $line;
    }
    ksort($perFile);
    return [$perFile, $pathless];
}

/** Loads the summary XML, or fails. */
function tpc_load_summary(): DOMDocument
{
    if (!is_file(TPC_SUMMARY_XML)) {
        throw new EntrypointError('pdepend wrote no summary XML');
    }
    $previous = libxml_use_internal_errors(true);
    $doc = new DOMDocument();
    $ok = $doc->load(TPC_SUMMARY_XML, LIBXML_NONET);
    libxml_clear_errors();
    libxml_use_internal_errors($previous);
    if (!$ok || $doc->documentElement === null || $doc->documentElement->nodeName !== 'metrics') {
        throw new EntrypointError('pdepend summary XML is not well-formed');
    }
    return $doc;
}

/**
 * Maps a PDepend file name back to its staged line number, or fails.
 *
 * @param array<int, true> $staged
 */
function tpc_staged_number(string $name, array $staged): int
{
    if (preg_match('/^\/tmp\/stage\/([1-9]\d*)\.php$/', $name, $m) && isset($staged[(int) $m[1]])
        && $m[1] === (string) (int) $m[1]) {
        return (int) $m[1];
    }
    throw new EntrypointError('pdepend reported an unknown path: ' . $name);
}

/**
 * Builds the per-file `pdepend` objects from the summary XML.
 *
 * Counted units: every method of a class or trait, and every function, with
 * a `file` child. Bare methods, and classes, traits and functions without a
 * `file` child, are never counted.
 *
 * The data of a file PDepend rejected (its error block) is discarded
 * unchecked: PDepend still writes partial data for it (for example a class
 * with start="0").
 *
 * `max_npath` is kept as a decimal digit string (it may not fit a PHP int);
 * see tpc_encode_output().
 *
 * @param array<int, true> $staged
 * @param array<int, string> $rejected files PDepend rejected, by line number
 * @return array<int, array{ccn: int, max_ccn: ?int, max_npath: ?string, min_mi: ?float, lloc: int}>
 */
function tpc_summarize(DOMDocument $doc, array $staged, array $rejected): array
{
    $xpath = new DOMXPath($doc);

    $result = [];
    foreach ($xpath->query('/metrics/files/file') as $file) {
        $n = tpc_staged_number($file->getAttribute('name'), $staged);
        if (isset($rejected[$n])) {
            continue;
        }
        $lloc = $file->getAttribute('lloc');
        if (!preg_match('/^(0|[1-9]\d*)$/', $lloc) || strlen($lloc) > 18) {
            throw new EntrypointError('pdepend summary XML has a malformed entry');
        }
        $result[$n] = ['ccn' => 0, 'max_ccn' => null, 'max_npath' => null, 'min_mi' => null, 'lloc' => (int) $lloc];
    }

    $owners = $xpath->query('/metrics/package/class | /metrics/package/trait | /metrics/package/function');
    foreach ($owners as $owner) {
        $fileNode = null;
        foreach ($owner->childNodes as $child) {
            if ($child instanceof DOMElement && $child->nodeName === 'file') {
                $fileNode = $child;
                break;
            }
        }
        if ($fileNode === null) {
            continue;
        }
        $n = tpc_staged_number($fileNode->getAttribute('name'), $staged);
        if (isset($rejected[$n])) {
            continue;
        }

        $units = [];
        if ($owner->nodeName === 'function') {
            $units[] = $owner;
        } else {
            foreach ($owner->childNodes as $child) {
                if ($child instanceof DOMElement && $child->nodeName === 'method') {
                    $units[] = $child;
                }
            }
        }
        if ($units === []) {
            continue;
        }
        if (!isset($result[$n])) {
            throw new EntrypointError('pdepend summary XML has a malformed entry');
        }
        foreach ($units as $unit) {
            tpc_add_unit($result[$n], $unit);
        }
    }
    return $result;
}

/**
 * Adds one counted unit to a file's `pdepend` object.
 *
 * @param array{ccn: int, max_ccn: ?int, max_npath: ?string, min_mi: ?float, lloc: int} $entry
 */
function tpc_add_unit(array &$entry, DOMElement $unit): void
{
    $start = $unit->getAttribute('start');
    $ccn = $unit->getAttribute('ccn');
    $npath = $unit->getAttribute('npath');
    foreach ([$start, $ccn, $npath] as $value) {
        if (!preg_match('/^[1-9]\d*$/', $value)) {
            throw new EntrypointError('pdepend summary XML has a malformed entry');
        }
    }
    if (strlen($start) > 18 || strlen($ccn) > 18) {
        throw new EntrypointError('pdepend summary XML has a malformed entry');
    }
    $ccn = (int) $ccn;
    $entry['ccn'] += $ccn;
    if ($entry['max_ccn'] === null || $ccn > $entry['max_ccn']) {
        $entry['max_ccn'] = $ccn;
    }
    if ($entry['max_npath'] === null || tpc_compare_digits($npath, $entry['max_npath']) > 0) {
        $entry['max_npath'] = $npath;
    }
    if ($unit->hasAttribute('mi')) {
        $mi = $unit->getAttribute('mi');
        if (is_numeric($mi) && is_finite((float) $mi)) {
            $mi = (float) $mi;
            if ($entry['min_mi'] === null || $mi < $entry['min_mi']) {
                $entry['min_mi'] = $mi;
            }
        }
    }
}

/** Compares two decimal digit strings without leading zeros. */
function tpc_compare_digits(string $a, string $b): int
{
    return strlen($a) <=> strlen($b) ?: strcmp($a, $b) <=> 0;
}
