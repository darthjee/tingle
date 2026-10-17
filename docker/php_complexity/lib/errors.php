<?php

declare(strict_types=1);

// Fatal entrypoint error. `status` is the process exit status (1 unless
// PDepend's own non-zero status is passed through). The message is written
// to stderr as "tingle_php_complexity: <message>".
final class EntrypointError extends RuntimeException
{
    public function __construct(string $message, public readonly int $status = 1)
    {
        parent::__construct($message);
    }
}
