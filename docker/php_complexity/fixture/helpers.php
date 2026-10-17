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
