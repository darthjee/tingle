# Add the DockerCheck executor base class

Create `python/code_check/docker_check/executor.py` with `DockerCheck`. Move these members from `CheckRubycritic`, unchanged except that each check-specific value comes from a class attribute or hook (spec section 2.6): `_parse`, `_fail`, `_warn`, `_load_config`, `_merge`, `_validate`, `_resolve_target`, `_print_header`, `_selection_options`, `_select`, `_gate_failed` and `run`.

Class attributes and hooks that subclasses supply:

- `PROG`, `FLAGS`, `CONFIG_SECTION`, `SINGLE_DEFAULTS`, `LIST_KEYS`, `THRESHOLD_KEYS`, `DEFAULT_EXCLUDES` and `error_class`.
- `NO_FILES_MESSAGE`, for example `"No Ruby files found for analysis."`.
- `validate_config(section, path)`, the check's config validator.
- `_load_section(section, path)` and `_select_files(target, root, **kwargs)`. These hooks let `CheckRubycritic` call the `load_section` and `select_files` names in **its own module**, so the existing monkeypatches still apply.
- `_gate_value(result)`: the value a result is classified by. For rubycritic this is `result.complexity`.
- `_execute(options, config_file)`: abstract.

Rules:

- Methods that are `@staticmethod`/`@classmethod` today and need a subclass value become `@classmethod`s. Call sites in the tests (`CheckRubycritic._load_config(True)`, `CheckRubycritic._execute` patched on the class) must keep working unchanged.
- `run` catches `self.error_class`, the base `DockerCheckError`. Behaviour is identical.
- `_validate` runs the `--details` check only when the check has a `details` option. Its messages stay byte-for-byte the same and are raised with `error_class`.
- The base class must not import anything from `code_check.rubycritic`.

## Files to Change
- `python/code_check/docker_check/executor.py` — new; the `DockerCheck` base class (flow moved from `rubycritic/executor.py`).
