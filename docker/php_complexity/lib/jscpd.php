<?php

declare(strict_types=1);

// jscpd invocation and per-file duplicated lines (duplication.md sections
// 1 to 3 and 5).
//
// A jscpd failure is never fatal: every file gets `duplication: null` and
// one path-less {tool: "jscpd", message} warning is added. Only an
// unreadable jscpd version is (the image itself is broken).

const TPC_JSCPD_BIN = '/usr/local/bin/jscpd';
const TPC_JSCPD_DIR = '/tmp/jscpd';
const TPC_JSCPD_REPORT_NAME = 'jscpd';
const TPC_JSCPD_REPORT = '/tmp/jscpd/jscpd.json';
const TPC_JSCPD_MAX_SIZE = 1048576; // --max-size 1mb
// A file jscpd reads has at most TPC_JSCPD_MAX_SIZE bytes, so at most
// TPC_JSCPD_MAX_SIZE + 1 lines.
const TPC_JSCPD_MAX_LINE = TPC_JSCPD_MAX_SIZE + 1;
const TPC_JSCPD_ARGS = [
    TPC_STAGE_DIR,
    '--reporters', 'json', '--output', TPC_JSCPD_DIR, '--report-name', TPC_JSCPD_REPORT_NAME,
    '--silent', '--no-tips', '--no-colors',
    '--min-tokens', '50', '--min-lines', '5', '--mode', 'mild', '--kind', 'exact',
    '--format', 'php', '--formats-exts', 'php:php',
    '--no-gitignore', '--max-size', '1mb',
];
// Linux signal numbers, for "jscpd killed by <signal>".
const TPC_SIGNAL_NAMES = [
    1 => 'SIGHUP', 2 => 'SIGINT', 3 => 'SIGQUIT', 4 => 'SIGILL', 5 => 'SIGTRAP',
    6 => 'SIGABRT', 7 => 'SIGBUS', 8 => 'SIGFPE', 9 => 'SIGKILL', 10 => 'SIGUSR1',
    11 => 'SIGSEGV', 12 => 'SIGUSR2', 13 => 'SIGPIPE', 14 => 'SIGALRM', 15 => 'SIGTERM',
];

// Soft failure: the message ends up in the jscpd warning.
final class JscpdError extends RuntimeException
{
}

/**
 * Runs a command (no shell) with stdin from /dev/null and stdout/stderr
 * redirected to files under $dir.
 *
 * @param list<string> $command
 * @return array{0: ?array<string, mixed>, 1: string, 2: string} the final
 *         proc_get_status() (null when it could not start), stdout, stderr
 */
function tpc_jscpd_exec(array $command, string $dir, string $cwd): array
{
    if (!is_dir($dir) && !mkdir($dir, 0700, true)) {
        throw new EntrypointError('cannot create ' . $dir);
    }
    $stdoutFile = $dir . '/stdout';
    $stderrFile = $dir . '/stderr';
    try {
        $process = proc_open(
            $command,
            [
                0 => ['file', '/dev/null', 'r'],
                1 => ['file', $stdoutFile, 'w'],
                2 => ['file', $stderrFile, 'w'],
            ],
            $pipes,
            $cwd,
        );
    } catch (Throwable) {
        $process = false;
    }
    if (!is_resource($process)) {
        return [null, '', ''];
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
    unlink($stdoutFile);
    unlink($stderrFile);
    return [$status, $stdout, $stderr];
}

/** "5.4.1", from `/usr/local/bin/jscpd --version` ("jscpd 5.4.1"). */
function tpc_jscpd_version(): string
{
    try {
        [$status, $stdout] = tpc_jscpd_exec([TPC_JSCPD_BIN, '--version'], '/tmp/jscpd-version', '/tmp');
    } catch (Throwable) {
        $status = null;
    }
    if ($status === null || $status['signaled'] || $status['exitcode'] !== 0
        || !preg_match('/^jscpd (\S+)$/', trim($stdout), $m)) {
        throw new EntrypointError('cannot read the jscpd version');
    }
    return $m[1];
}

/**
 * Runs jscpd on /tmp/stage. Its stdout (a summary, printed even with
 * --silent), then its stderr, are copied to stderr: stdout holds only the
 * JSON.
 */
function tpc_run_jscpd(): void
{
    tpc_remove_tree(TPC_JSCPD_DIR);
    $logDir = '/tmp/jscpd-log';
    [$status, $stdout, $stderr] = tpc_jscpd_exec(
        array_merge([TPC_JSCPD_BIN], TPC_JSCPD_ARGS),
        $logDir,
        '/tmp',
    );
    fwrite(STDERR, $stdout);
    fwrite(STDERR, $stderr);
    if ($status === null) {
        throw new JscpdError('jscpd: cannot start ' . TPC_JSCPD_BIN);
    }
    if ($status['signaled']) {
        $signal = $status['termsig'];
        throw new JscpdError('jscpd killed by ' . (TPC_SIGNAL_NAMES[$signal] ?? 'signal ' . $signal));
    }
    if ($status['exitcode'] !== 0) {
        throw new JscpdError('jscpd exited with status ' . $status['exitcode']);
    }
}

/** The decoded jscpd report, or a soft failure. */
function tpc_read_jscpd_report(): mixed
{
    try {
        $text = is_file(TPC_JSCPD_REPORT) ? file_get_contents(TPC_JSCPD_REPORT) : false;
    } catch (Throwable) {
        $text = false;
    }
    if ($text === false) {
        throw new JscpdError('jscpd report ' . TPC_JSCPD_REPORT . ' is missing');
    }
    try {
        return json_decode($text, true, 512, JSON_THROW_ON_ERROR);
    } catch (JsonException) {
        throw new JscpdError('jscpd report ' . TPC_JSCPD_REPORT . ' is not valid JSON');
    }
}

/**
 * {number, start, end} of one clone side, validated.
 *
 * @param array<int, true> $staged
 * @return array{0: int, 1: int, 2: int}
 */
function tpc_jscpd_clone_side(mixed $side, array $staged): array
{
    $valid = is_array($side) && !array_is_list($side)
        && is_string($side['name'] ?? null)
        && is_int($side['start'] ?? null) && is_int($side['end'] ?? null)
        && $side['start'] >= 1 && $side['end'] >= $side['start'] && $side['end'] <= TPC_JSCPD_MAX_LINE;
    if (!$valid) {
        throw new JscpdError('jscpd report has a malformed duplicates entry');
    }
    $name = $side['name'];
    if (!preg_match('/^([1-9]\d*)\.php$/', $name, $m) || strlen($m[1]) > 18 || !isset($staged[(int) $m[1]])) {
        throw new JscpdError('jscpd reported an unknown path: ' . tpc_one_line($name));
    }
    return [(int) $m[1], $side['start'], $side['end']];
}

/**
 * Input line number => set of duplicated line numbers (as array keys).
 *
 * @param array<int, true> $staged
 * @return array<int, array<int, true>>
 */
function tpc_jscpd_covered_lines(mixed $report, array $staged): array
{
    $duplicates = is_array($report) && !array_is_list($report) ? ($report['duplicates'] ?? null) : null;
    if (!is_array($duplicates) || !array_is_list($duplicates)) {
        throw new JscpdError('jscpd report has no duplicates list');
    }
    $covered = [];
    foreach ($duplicates as $clone) {
        if (!is_array($clone) || ($clone !== [] && array_is_list($clone))) {
            throw new JscpdError('jscpd report has a malformed duplicates entry');
        }
        $sides = [
            tpc_jscpd_clone_side($clone['firstFile'] ?? null, $staged),
            tpc_jscpd_clone_side($clone['secondFile'] ?? null, $staged),
        ];
        foreach ($sides as [$n, $start, $end]) {
            for ($line = $start; $line <= $end; $line++) {
                $covered[$n][$line] = true;
            }
        }
    }
    return $covered;
}

/**
 * Runs jscpd and fills files[].duplication. Never throws on a jscpd failure.
 *
 * @param array<int, array<string, mixed>> $files entries by line number
 * @param array<int, true> $staged
 * @param list<array<string, string>> $warnings
 */
function tpc_apply_jscpd(array &$files, array $staged, array &$warnings): void
{
    try {
        tpc_run_jscpd();
        $covered = tpc_jscpd_covered_lines(tpc_read_jscpd_report(), $staged);
    } catch (JscpdError $e) {
        foreach ($files as &$entry) {
            $entry['duplication'] = null;
        }
        unset($entry);
        $warnings[] = ['tool' => 'jscpd', 'message' => tpc_one_line($e->getMessage())];
        return;
    }
    foreach (array_keys($staged) as $n) {
        if ($files[$n]['parse_error']) {
            continue;
        }
        $size = filesize(TPC_STAGE_DIR . '/' . $n . '.php');
        if ($size > TPC_JSCPD_MAX_SIZE) {
            continue;
        }
        $files[$n]['duplication'] = ['lines' => count($covered[$n] ?? [])];
    }
}
