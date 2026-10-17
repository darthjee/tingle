<?php

namespace App\Anon;

use App\Shapes\Square;

class Factory
{
    public function make(bool $big): Square
    {
        return new class ($big ? 10.0 : 1.0) extends Square {
            public function label(): string
            {
                return $this->area() > 50 ? 'big' : 'small';
            }
        };
    }
}
