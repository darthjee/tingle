# Issue: Codacy: Expected: 1; Actual: 2 (README.md:14)

## Description
Codacy flagged `README.md:14` with markdownlint rule `MD012` (no-multiple-blanks, category: CodeStyle, severity: Info): `Expected: 1; Actual: 2`. Codacy issue ID: `68aa29c0b1b202fa457bef27b1c87844`.

## Problem
`README.md` has two consecutive blank lines (lines 13 and 14) between the "Next Release" line and the "Scripts in **shell**, **Python** and **Node.js**..." paragraph. This is the only occurrence in the file.

## Expected Behavior
`README.md` has a single blank line at that spot, so markdownlint `MD012` no longer reports it and the Codacy finding is resolved.

## Solution
Remove one of the two blank lines between the "Next Release" line and the "Scripts in ..." paragraph in `README.md`. No other content changes.

## Benefits
- Clears a Codacy code-style finding.
- Keeps the README consistent with markdownlint rules.
