<?php

namespace App\Attr;

#[\Attribute]
class Tag
{
}

class Maker
{
    public function make(): object
    {
        return new #[Tag] class {
            public function ok(): bool
            {
                return true;
            }
        };
    }
}
