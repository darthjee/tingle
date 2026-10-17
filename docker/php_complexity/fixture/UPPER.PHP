<?php

function shout(string $s): string
{
    return $s === '' ? '' : strtoupper($s) . '!';
}
