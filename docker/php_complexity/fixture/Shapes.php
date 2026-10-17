<?php

namespace App\Shapes;

interface Shape
{
    public function area(): float;
}

class Square implements Shape
{
    public function __construct(private float $side)
    {
    }

    public function area(): float
    {
        return $this->side ** 2;
    }
}

class Circle implements Shape
{
    public function __construct(private float $radius)
    {
    }

    public function area(): float
    {
        return $this->radius > 0 ? M_PI * $this->radius ** 2 : 0.0;
    }
}

trait Describes
{
    public function describe(): string
    {
        return static::class;
    }
}
