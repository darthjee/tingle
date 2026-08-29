"""
configure.py — Interactive `configure context|namespace|pod` flows for kube.

Each flow edits `KubeConfig.raw` (the pre-default dict) and persists it via
`KubeConfig.save`, so a user who never set `aws_profile`/`pod_id_pattern`/
`shell` never gets those defaults baked into their file just from running
`configure`. All prompting is `input()`-based, in the same numbered-menu,
reprompt-on-invalid-input, empty-input-aborts style as
`exec.prompt_pod_choice`.
"""

from __future__ import annotations

import re

from kube.config import KubeConfig

_ACTIONS = ["create", "edit", "remove"]


def _prompt_action() -> str | None:
    """Prompt for create/edit/remove. Returns `None` on empty input (abort)."""
    print("What would you like to do?")
    for index, action in enumerate(_ACTIONS, start=1):
        print(f"{index}) {action}")

    while True:
        choice = input("Select an action: ").strip()
        if not choice:
            return None

        if not choice.isdigit():
            print("Please enter a number.")
            continue

        selection = int(choice)
        if selection < 1 or selection > len(_ACTIONS):
            print(f"Please enter a number between 1 and {len(_ACTIONS)}.")
            continue

        return _ACTIONS[selection - 1]


def _prompt_alias_choice(aliases: list[str], label: str) -> str | None:
    """Prompt to pick one of `aliases` by number. Returns `None` on empty input."""
    for index, alias in enumerate(aliases, start=1):
        print(f"{index}) {alias}")

    while True:
        choice = input(f"Select {label}: ").strip()
        if not choice:
            return None

        if not choice.isdigit():
            print("Please enter a number.")
            continue

        selection = int(choice)
        if selection < 1 or selection > len(aliases):
            print(f"Please enter a number between 1 and {len(aliases)}.")
            continue

        return aliases[selection - 1]


def _prompt_text(label: str, default: str | None = None) -> str | None:
    """Prompt for a required free-text value. Returns `None` on empty input."""
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    if not value:
        return default
    return value


def _prompt_optional_text(label: str, default: str | None = None) -> str | None:
    """Prompt for an optional free-text value. Returns `None` when left blank."""
    suffix = f" [{default}]" if default else ""
    value = input(f"{label} (optional){suffix}: ").strip()
    if not value:
        return default
    return value


def _prompt_id_pattern(default: str | None = None) -> str | None:
    """Prompt for an optional `id_pattern`, reprompting on invalid regex syntax."""
    while True:
        suffix = f" [{default}]" if default else ""
        value = input(f"id_pattern (optional, regex){suffix}: ").strip()
        if not value:
            return default

        try:
            re.compile(value)
        except re.error as exc:
            print(f"kube configure: invalid regex '{value}': {exc}")
            continue

        return value


def _save(config: KubeConfig, draft: dict, success_message: str) -> None:
    """Shared save-and-report tail for all configure flows."""
    error = config.save(draft)
    if error:
        print(f"kube configure: {error} — nothing saved.")
        return
    print(success_message)


def _abort() -> None:
    print("kube configure: aborted, nothing saved.")


def configure_context(config: KubeConfig) -> None:
    """Interactively create, edit, or remove a context alias."""
    draft = dict(config.raw)
    contexts = dict(draft.get("contexts", {}))

    if contexts:
        print("Configured context aliases:")
        for alias, real_name in contexts.items():
            print(f"  {alias} -> {real_name}")
    else:
        print("No context aliases configured yet.")

    action = _prompt_action()
    if action is None:
        _abort()
        return

    if action in ("create", "edit"):
        _configure_context_upsert(config, draft, contexts, action)
    else:
        _configure_context_remove(config, draft, contexts)


def _configure_context_upsert(config: KubeConfig, draft: dict, contexts: dict, action: str) -> None:
    default_alias = None
    if action == "edit":
        if not contexts:
            print("kube configure: no context aliases to edit.")
            return
        default_alias = _prompt_alias_choice(sorted(contexts.keys()), "an alias to edit")
        if default_alias is None:
            _abort()
            return

    alias = _prompt_text("Alias", default=default_alias)
    if not alias:
        _abort()
        return

    real_name = _prompt_text("Real context name/ARN", default=contexts.get(alias))
    if not real_name:
        _abort()
        return

    contexts[alias] = real_name
    draft["contexts"] = contexts

    _save(config, draft, f"kube configure: context alias '{alias}' saved.")


def _configure_context_remove(config: KubeConfig, draft: dict, contexts: dict) -> None:
    if not contexts:
        print("kube configure: no context aliases to remove.")
        return

    alias = _prompt_alias_choice(sorted(contexts.keys()), "an alias to remove")
    if alias is None:
        _abort()
        return

    namespaces = dict(draft.get("namespaces", {}))
    pods = dict(draft.get("pods", {}))
    has_namespaces = bool(namespaces.get(alias))
    has_pods = bool(pods.get(alias))

    if has_namespaces or has_pods:
        print(f"Removing context alias '{alias}' will also drop:")
        if has_namespaces:
            print(f"  - namespaces.{alias} ({len(namespaces[alias])} entrie(s))")
        if has_pods:
            print(f"  - pods.{alias} ({len(pods[alias])} entrie(s))")
        confirm = input("Confirm removal? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            _abort()
            return

    del contexts[alias]
    namespaces.pop(alias, None)
    pods.pop(alias, None)

    draft["contexts"] = contexts
    draft["namespaces"] = namespaces
    draft["pods"] = pods

    _save(config, draft, f"kube configure: context alias '{alias}' removed.")


def _pick_scope(contexts: dict) -> str | None:
    """Prompt to pick a context alias to scope namespace/pod configuration to."""
    if not contexts:
        print(
            "kube configure: no context aliases configured yet — "
            "run `kube configure context` first."
        )
        return None

    print("Configured context aliases:")
    return _prompt_alias_choice(sorted(contexts.keys()), "a context alias")


def configure_namespace(config: KubeConfig) -> None:
    """Interactively create, edit, or remove a namespace alias within a scope."""
    draft = dict(config.raw)
    contexts = dict(draft.get("contexts", {}))

    scope = _pick_scope(contexts)
    if scope is None:
        return

    namespaces = dict(draft.get("namespaces", {}))
    scoped = dict(namespaces.get(scope, {}))

    if scoped:
        print(f"Configured namespace aliases for '{scope}':")
        for alias, real_name in scoped.items():
            print(f"  {alias} -> {real_name}")
    else:
        print(f"No namespace aliases configured yet for '{scope}'.")

    action = _prompt_action()
    if action is None:
        _abort()
        return

    if action in ("create", "edit"):
        _configure_namespace_upsert(config, draft, namespaces, scoped, scope, action)
    else:
        _configure_namespace_remove(config, draft, namespaces, scoped, scope)


def _configure_namespace_upsert(
    config: KubeConfig, draft: dict, namespaces: dict, scoped: dict, scope: str, action: str
) -> None:
    default_alias = None
    if action == "edit":
        if not scoped:
            print("kube configure: no namespace aliases to edit.")
            return
        default_alias = _prompt_alias_choice(sorted(scoped.keys()), "an alias to edit")
        if default_alias is None:
            _abort()
            return

    alias = _prompt_text("Alias", default=default_alias)
    if not alias:
        _abort()
        return

    real_name = _prompt_text("Real namespace name", default=scoped.get(alias))
    if not real_name:
        _abort()
        return

    scoped[alias] = real_name
    namespaces[scope] = scoped
    draft["namespaces"] = namespaces

    _save(config, draft, f"kube configure: namespace alias '{alias}' saved under '{scope}'.")


def _configure_namespace_remove(
    config: KubeConfig, draft: dict, namespaces: dict, scoped: dict, scope: str
) -> None:
    if not scoped:
        print("kube configure: no namespace aliases to remove.")
        return

    alias = _prompt_alias_choice(sorted(scoped.keys()), "an alias to remove")
    if alias is None:
        _abort()
        return

    del scoped[alias]
    namespaces[scope] = scoped
    draft["namespaces"] = namespaces

    _save(config, draft, f"kube configure: namespace alias '{alias}' removed from '{scope}'.")


def configure_pod(config: KubeConfig) -> None:
    """Interactively create, edit, or remove a pod alias within a scope."""
    draft = dict(config.raw)
    contexts = dict(draft.get("contexts", {}))

    scope = _pick_scope(contexts)
    if scope is None:
        return

    pods = dict(draft.get("pods", {}))
    scoped = dict(pods.get(scope, {}))

    if scoped:
        print(f"Configured pod aliases for '{scope}':")
        for alias, pod in scoped.items():
            print(f"  {alias} -> {pod}")
    else:
        print(f"No pod aliases configured yet for '{scope}'.")

    action = _prompt_action()
    if action is None:
        _abort()
        return

    if action in ("create", "edit"):
        namespaces = dict(draft.get("namespaces", {}))
        scoped_namespaces = namespaces.get(scope, {})
        _configure_pod_upsert(config, draft, pods, scoped, scope, action, scoped_namespaces)
    else:
        _configure_pod_remove(config, draft, pods, scoped, scope)


def _configure_pod_upsert(
    config: KubeConfig,
    draft: dict,
    pods: dict,
    scoped: dict,
    scope: str,
    action: str,
    scoped_namespaces: dict,
) -> None:
    default_alias = None
    existing: dict = {}
    if action == "edit":
        if not scoped:
            print("kube configure: no pod aliases to edit.")
            return
        default_alias = _prompt_alias_choice(sorted(scoped.keys()), "an alias to edit")
        if default_alias is None:
            _abort()
            return
        existing = scoped.get(default_alias, {})

    alias = _prompt_text("Alias", default=default_alias)
    if not alias:
        _abort()
        return

    prefix = _prompt_text("prefix", default=existing.get("prefix"))
    if not prefix:
        _abort()
        return

    id_pattern = _prompt_id_pattern(default=existing.get("id_pattern"))

    if scoped_namespaces:
        print(f"Configured namespace aliases for '{scope}':")
        for ns_alias in sorted(scoped_namespaces.keys()):
            print(f"  - {ns_alias}")
    namespace = _prompt_optional_text("namespace alias", default=existing.get("namespace"))

    pod: dict = {"prefix": prefix}
    if id_pattern:
        pod["id_pattern"] = id_pattern
    if namespace:
        pod["namespace"] = namespace

    scoped[alias] = pod
    pods[scope] = scoped
    draft["pods"] = pods

    _save(config, draft, f"kube configure: pod alias '{alias}' saved under '{scope}'.")


def _configure_pod_remove(
    config: KubeConfig, draft: dict, pods: dict, scoped: dict, scope: str
) -> None:
    if not scoped:
        print("kube configure: no pod aliases to remove.")
        return

    alias = _prompt_alias_choice(sorted(scoped.keys()), "an alias to remove")
    if alias is None:
        _abort()
        return

    del scoped[alias]
    pods[scope] = scoped
    draft["pods"] = pods

    _save(config, draft, f"kube configure: pod alias '{alias}' removed from '{scope}'.")
