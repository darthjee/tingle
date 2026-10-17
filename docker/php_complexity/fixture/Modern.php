<?php

namespace App\Modern;

enum Suit: string
{
    case Hearts = 'H';
    case Spades = 'S';

    public function color(): string
    {
        return match ($this) {
            Suit::Hearts => 'Red',
            Suit::Spades => 'Black',
        };
    }
}

readonly class Point
{
    public function __construct(public int $x, public int $y)
    {
    }

    public function withX(int $x): static
    {
        return new static($x, $this->y);
    }
}

interface HasVersion
{
    const string VERSION = '1.0';
}
