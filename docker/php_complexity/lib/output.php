<?php

declare(strict_types=1);

// Merged JSON (docs/agents/tingle-php-complexity-image.md, "Merged JSON").

/**
 * Encodes the merged JSON document. Every `pdepend.max_npath` and
 * `functions[].npath` digit string is written as a JSON integer of any size:
 * one that fits a PHP int is cast, a larger one is swapped in for a random
 * placeholder after encoding.
 *
 * @param array<string, mixed> $document
 */
function tpc_encode_output(array $document): string
{
    $token = bin2hex(random_bytes(16));
    $big = [];
    $encode = static function (string $digits) use ($token, &$big): int|string {
        if (strlen($digits) <= 18) {
            return (int) $digits;
        }
        $placeholder = 'tpc-npath-' . $token . '-' . count($big);
        $big['"' . $placeholder . '"'] = $digits;
        return $placeholder;
    };
    foreach ($document['files'] as $i => $entry) {
        if (is_array($entry['pdepend'] ?? null) && $entry['pdepend']['max_npath'] !== null) {
            $document['files'][$i]['pdepend']['max_npath'] = $encode($entry['pdepend']['max_npath']);
        }
        if (is_array($entry['functions'] ?? null)) {
            foreach ($entry['functions'] as $j => $function) {
                $document['files'][$i]['functions'][$j]['npath'] = $encode($function['npath']);
            }
        }
    }
    $json = json_encode($document, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    return $big === [] ? $json : strtr($json, $big);
}
