# Print the bootstrap notice unconditionally

`Kube.run()` currently only prints `config.notice` when `config.pass_through` is `True`. After Step 1, a freshly bootstrapped config sets `notice` without setting `pass_through`, so that branch would silently swallow the "created new config" message. Widen the condition to print whenever a notice exists, regardless of `pass_through`:

```python
if config.notice:
    print(config.notice)
```

No other change is needed in `executor.py`: `_configure()` builds its own separate `KubeConfig()` after `run()`'s instance already bootstrapped the file on disk, so by the time `_configure()`'s instance loads, the file exists and is read normally (no second notice, no second bootstrap).

## Files to Change

- `python/kube/executor.py` — change `Kube.run()`'s `if config.pass_through: print(config.notice)` to `if config.notice: print(config.notice)`.
