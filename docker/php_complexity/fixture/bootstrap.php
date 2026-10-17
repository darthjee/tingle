<?php

$config = ['debug' => true, 'level' => 3];

if ($config['debug']) {
    error_reporting(E_ALL);
} elseif ($config['level'] > 2) {
    error_reporting(E_WARNING);
}

foreach ($config as $key => $value) {
    if ($value && $key !== 'level') {
        echo $key, PHP_EOL;
    }
}
