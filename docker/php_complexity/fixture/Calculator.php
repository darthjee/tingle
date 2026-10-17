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
