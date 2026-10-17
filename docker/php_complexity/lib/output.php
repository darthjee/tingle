<?php

declare(strict_types=1);

// Merged JSON (image.md section 7).

/**
 * Encodes the merged JSON document. Every `max_npath` digit string is
 * written as a JSON integer of any size: one that fits a PHP int is cast,
 * a larger one is swapped in for a random placeholder after encoding.
 *
 * @param array<string, mixed> $document
 */
function tpc_encode_output(array $document): string
{
    $token = bin2hex(random_bytes(16));
    $big = [];
    foreach ($document['files'] as $i => $entry) {
        if (!is_array($entry['pdepend'] ?? null) || $entry['pdepend']['max_npath'] === null) {
            continue;
        }
        $digits = $entry['pdepend']['max_npath'];
        if (strlen($digits) <= 18) {
            $document['files'][$i]['pdepend']['max_npath'] = (int) $digits;
        } else {
            $placeholder = 'tpc-npath-' . $token . '-' . $i;
            $big['"' . $placeholder . '"'] = $digits;
            $document['files'][$i]['pdepend']['max_npath'] = $placeholder;
        }
    }
    $json = json_encode($document, JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    return $big === [] ? $json : strtr($json, $big);
}
