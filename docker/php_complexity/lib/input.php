<?php

declare(strict_types=1);

// Reading and refusing input lines
// (docs/agents/tingle-php-complexity-image.md, "Contract").

/**
 * Reads all of stdin and splits it into input lines: split on "\n", a final
 * "\n" adds no line, nothing is trimmed.
 *
 * @return list<string>
 */
function tpc_read_input_lines(): array
{
    $in = stream_get_contents(STDIN);
    if ($in === false) {
        throw new EntrypointError('cannot read stdin');
    }
    if (!mb_check_encoding($in, 'UTF-8')) {
        throw new EntrypointError('stdin is not valid UTF-8');
    }
    if ($in === '') {
        return [];
    }
    $lines = explode("\n", $in);
    if (end($lines) === '') {
        array_pop($lines);
    }
    return $lines;
}

/**
 * Applies the refusal rules, in order. Returns [null, <real path>] for an
 * accepted line, or [<warning message>, null] for a refused one.
 *
 * @param array<string, true> $seen lines already received (updated)
 * @return array{0: ?string, 1: ?string}
 */
function tpc_select_line(string $line, string $srcRoot, array &$seen): array
{
    $duplicate = isset($seen[$line]);
    $seen[$line] = true;

    if ($line === '') {
        return ['empty line', null];
    }
    if ($line[0] === '/') {
        return ['absolute path', null];
    }
    if (in_array('..', explode('/', $line), true)) {
        return ["path has a '..' segment", null];
    }
    if ($duplicate) {
        return ['duplicate line', null];
    }
    $real = tpc_real_file_under($srcRoot, $line);
    if ($real === null) {
        return ['not a regular file under /src', null];
    }
    $segments = explode('/', $line);
    $name = strtolower(end($segments));
    $dot = strrpos($name, '.');
    $extension = $dot === false ? '' : substr($name, $dot + 1);
    if ($extension !== 'php') {
        return ['unsupported extension', null];
    }
    if (str_ends_with($name, '.blade.php')) {
        return ['Blade template', null];
    }
    return [null, $real];
}

/**
 * The real path of /src/<line> when it is a regular file inside /src (symlinks
 * resolved), else null.
 */
function tpc_real_file_under(string $srcRoot, string $line): ?string
{
    try {
        $real = realpath($srcRoot . '/' . $line);
    } catch (ValueError) {
        // A NUL byte in the line.
        return null;
    }
    if ($real === false || !str_starts_with($real, $srcRoot . '/')) {
        return null;
    }
    clearstatcache();
    if (!is_file($real)) {
        return null;
    }
    return $real;
}
