<?php

declare(strict_types=1);

// Entrypoint of the tingle_php_complexity image
// (`tingle code_check php_complexity`).
//
// Usage (inside the container, /src mounted read-only):
//   printf '%s\n' src/A.php lib/b.php | php /opt/tingle_php_complexity/entrypoint.php
//
// Input:  stdin, one path per line, relative to /src. Must be valid UTF-8.
//         Split on "\n" (a final "\n" adds no line), nothing trimmed.
//         Arguments are ignored. Lines that are empty, absolute, contain a
//         ".." segment, are duplicates, are not a regular file under /src,
//         do not have the "php" extension (lower-cased) or are Blade
//         templates (*.blade.php) are refused (an "entrypoint" warning,
//         never read).
// Output: stdout, exactly one JSON object followed by "\n":
//           {"tool_versions": {"php", "pdepend", "jscpd": null},
//            "files": [one entry per input line, in input order:
//                      {path, parse_error, pdepend, functions: null,
//                       duplication: null}],
//            "warnings": [{tool, path?, message}]}
//         PDepend's stdout and stderr are passed through to stderr.
// Exit:   0 when the JSON was printed; PDepend's status when PDepend exits
//         non-zero; 1 on any other failure ("tingle_php_complexity: <reason>"
//         on stderr). Nothing is printed on stdout on failure.
//
// Each accepted file is read once and checked with PHP's own parser
// (token_get_all with TOKEN_PARSE); a file PHP rejects gets parse_error: true
// and a "php" warning, and is not staged. The others are copied to
// /tmp/stage/<n>.php (<n> = input line number) and PDepend runs on that tree,
// never on /src. A file PDepend rejects (its error block on stdout) gets
// parse_error: true and a "pdepend" warning. Nothing is written outside /tmp.
//
// Dependencies: PHP standard library (dom, mbstring, tokenizer),
// /opt/tingle_php_complexity/vendor (PDepend 3.0.0, Composer's runtime API).
//
// Contract: docs/agents/specs/code_check/php_complexity/image.md.

ini_set('display_errors', 'stderr');
set_error_handler(static function (int $severity, string $message, string $file, int $line): bool {
    throw new ErrorException($message, 0, $severity, $file, $line);
});

require __DIR__ . '/vendor/autoload.php';
require __DIR__ . '/lib/errors.php';
require __DIR__ . '/lib/input.php';
require __DIR__ . '/lib/staging.php';
require __DIR__ . '/lib/pdepend.php';
require __DIR__ . '/lib/output.php';

const TPC_SRC = '/src';

/** @return array<string, mixed> */
function tpc_new_entry(string $line): array
{
    return [
        'path' => $line,
        'parse_error' => false,
        'pdepend' => null,
        'functions' => null,
        'duplication' => null,
    ];
}

function tpc_main(): string
{
    $versions = ['php' => PHP_VERSION, 'pdepend' => tpc_pdepend_version(), 'jscpd' => null];
    $lines = tpc_read_input_lines();

    $files = [];
    $warnings = [];
    $staged = [];
    $seen = [];
    $srcRoot = $lines === [] ? TPC_SRC : (realpath(TPC_SRC) ?: TPC_SRC);

    foreach ($lines as $i => $line) {
        $n = $i + 1;
        $files[$n] = tpc_new_entry($line);

        [$refusal, $real] = tpc_select_line($line, $srcRoot, $seen);
        if ($refusal !== null) {
            $warnings[] = ['tool' => 'entrypoint', 'path' => $line, 'message' => $refusal];
            continue;
        }

        $code = file_get_contents($real);
        if ($code === false) {
            throw new EntrypointError('cannot read line ' . $n);
        }
        $parseError = tpc_parse_error($code);
        if ($parseError !== null) {
            $files[$n]['parse_error'] = true;
            $warnings[] = ['tool' => 'php', 'path' => $line, 'message' => $parseError];
            continue;
        }

        if ($staged === []) {
            tpc_prepare_stage();
        }
        tpc_stage_file($n, $code);
        $staged[$n] = true;
    }

    if ($staged !== []) {
        $stdout = tpc_run_pdepend();
        [$rejected, $pathless] = tpc_scan_pdepend_errors($stdout, $staged);
        $summary = tpc_summarize(tpc_load_summary(), $staged);

        foreach ($summary as $n => $pdepend) {
            if (!isset($rejected[$n])) {
                $files[$n]['pdepend'] = $pdepend;
            }
        }
        foreach ($rejected as $n => $message) {
            $files[$n]['parse_error'] = true;
            $warnings[] = ['tool' => 'pdepend', 'path' => $files[$n]['path'], 'message' => $message];
        }
        foreach ($pathless as $message) {
            $warnings[] = ['tool' => 'pdepend', 'message' => $message];
        }
    }

    return tpc_encode_output([
        'tool_versions' => $versions,
        'files' => array_values($files),
        'warnings' => $warnings,
    ]);
}

try {
    $json = tpc_main();
} catch (EntrypointError $e) {
    fwrite(STDERR, 'tingle_php_complexity: ' . $e->getMessage() . "\n");
    exit($e->status);
} catch (Throwable $e) {
    fwrite(STDERR, 'tingle_php_complexity: ' . tpc_one_line($e->getMessage()) . "\n");
    exit(1);
}

fwrite(STDOUT, $json . "\n");
exit(0);
