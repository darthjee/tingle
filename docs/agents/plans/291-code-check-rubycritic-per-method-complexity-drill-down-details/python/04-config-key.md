# Add the `details` config key
Config loading for `rubycritic` is added by #297, which is still open while this plan is written.

- **If #297 is already merged** when this runs: add `details` (int ≥ 0 or `null`, booleans rejected) to the rubycritic config schema/validation and to the merge of single-value keys (CLI wins). Add tests for a valid value, a wrong type, a negative value and the CLI override.
- **If #297 is not merged yet**: do nothing in code. The product-owner step adds `details` to the specs, so #297 implements it.

## Files to Change
- The rubycritic config module and its tests from #297 (only if it is merged).
