<?php

function normalize_b(array $rows): array
{
    $result = [];
    foreach ($rows as $row) {
        $name = trim((string) ($row['name'] ?? ''));
        $email = strtolower(trim((string) ($row['email'] ?? '')));
        if ($name === '' || $email === '') {
            continue;
        }
        $result[] = ['name' => $name, 'email' => $email, 'active' => (bool) ($row['active'] ?? false)];
    }
    return $result;
}
