# Add Kubernetes name validation module

Create `python/kube/validation.py` with a function that validates a string against RFC 1123 label rules: lowercase alphanumeric characters and `-` only, must start and end with an alphanumeric character, and must not exceed a given max length. Expose something like:

```python
def is_valid_resource_name(value: str, *, max_length: int = 253) -> bool:
    ...
```

Namespaces are capped at 63 chars by Kubernetes; callers validating a namespace pass `max_length=63`, callers validating other resource names (e.g. pod names) use the default 253. Use a single compiled regex (e.g. `^[a-z0-9]([-a-z0-9]*[a-z0-9])?$`) plus a length check — no external dependency needed.

## Files to Change
- `python/kube/validation.py` — new module with `is_valid_resource_name(value, *, max_length=253)`.
