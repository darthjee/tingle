# Plan: Codacy: Expected: 1; Actual: 2 (README.md:14)

Issue: [87-codacy-expected-1-actual-2-readme-md-14.md](../../issues/87-codacy-expected-1-actual-2-readme-md-14.md)

## Overview
Remove the duplicate blank line in `README.md` that triggers markdownlint `MD012` (no-multiple-blanks), clearing the Codacy finding.

## Context
`README.md` has two consecutive blank lines (lines 13 and 14) between the "**Next Release:**" line and the "Scripts in **shell**, **Python** and **Node.js**..." paragraph. It is the only double blank in the file. `README.md` is a root-level file owned by the architect, so no specialist agent has work here.

## Implementation Steps

### Step 1 — Remove the extra blank line
Delete one of the two blank lines at `README.md:13-14`, leaving a single blank line between the "Next Release" line and the "Scripts in ..." paragraph. Make no other content changes. Verify no other consecutive blank lines remain with `awk 'prev=="" && $0=="" {print NR} {prev=$0}' README.md` (expect no output).

## Files to Change
- `README.md` — remove one of the two consecutive blank lines at lines 13–14.

## Notes
- No CI job lints markdown; the check is Codacy's markdownlint `MD012` on the PR.
