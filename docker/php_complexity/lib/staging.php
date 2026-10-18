<?php

declare(strict_types=1);

// Parse check and staged tree (docs/agents/tingle-php-complexity-image.md,
// "Contract").

const TPC_STAGE_DIR = '/tmp/stage';

/**
 * Runs PHP's own parser on the bytes. Returns null when they parse, else the
 * warning message "<message> on line <line>".
 */
function tpc_parse_error(string $code): ?string
{
    try {
        token_get_all($code, TOKEN_PARSE);
    } catch (CompileError $e) {
        return tpc_one_line($e->getMessage()) . ' on line ' . $e->getLine();
    }
    return null;
}

/** Creates an empty /tmp/stage. */
function tpc_prepare_stage(): void
{
    tpc_remove_tree(TPC_STAGE_DIR);
    if (!mkdir(TPC_STAGE_DIR, 0700, true)) {
        throw new EntrypointError('cannot create ' . TPC_STAGE_DIR);
    }
}

/** Writes the bytes of accepted line <n> to /tmp/stage/<n>.php (a copy). */
function tpc_stage_file(int $n, string $code): void
{
    $target = TPC_STAGE_DIR . '/' . $n . '.php';
    if (file_put_contents($target, $code) !== strlen($code)) {
        throw new EntrypointError('cannot write ' . $target);
    }
}

/** Removes a file or directory tree, if it exists. Symlinks are not followed. */
function tpc_remove_tree(string $path): void
{
    if (is_link($path) || is_file($path)) {
        unlink($path);
        return;
    }
    if (!is_dir($path)) {
        return;
    }
    foreach (scandir($path) as $entry) {
        if ($entry !== '.' && $entry !== '..') {
            tpc_remove_tree($path . '/' . $entry);
        }
    }
    rmdir($path);
}

/** Collapses a message to one line. */
function tpc_one_line(string $message): string
{
    return trim((string) preg_replace('/\s*[\r\n]+\s*/', ' ', $message));
}
