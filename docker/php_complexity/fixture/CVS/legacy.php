<?php

function legacy(int $x): int
{
    return $x > 0 ? $x : -$x;
}
