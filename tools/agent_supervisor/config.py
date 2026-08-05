#!/usr/bin/env python3
"""Configuration: immutable controller config + runtime model selection (D-007 S3.1).

Two files, two trust levels, two providers:

    config.toml            IMMUTABLE. Covered by the controller manifest (S13.1).
                           Policy rules, tier definitions, limits, security
                           settings, and each provider's allowlist of models the
                           owner permits AT ALL.

    model_selection.toml   RUNTIME. Deliberately OUTSIDE the manifest so that
                           changing a model never invalidates the controller.
                           Which allowlisted model is active per provider/role.

Invariants enforced here:

* **No effort key, anywhere.** Any key whose name contains "effort", at any
  depth, in either file, is a hard configuration error. D-004-R159 is a
  permanent prohibition and D-007 S3.1 restates it. The installed Claude CLI
  does expose an `--effort` flag; the supervisor never passes it and no config
  file may carry one.
* **Per-provider allowlists are never cross-satisfied.** A Codex entry can never
  satisfy the Claude list and vice versa - validated against the entry's OWN
  provider's list only (S3.1, S3.2 rule 4).
* **Each file parses as valid standalone TOML** and carries only its own class
  of settings: the runtime file may not contain controller authority (limits,
  allowlists, policy), and the controller file may not contain runtime
  selections. They are never concatenated.
* **Limited-auto never comes from configuration.** A config that tries to set
  limited-auto as the default mode is refused (S12).

Phase 1 scope note: this module parses, validates, and digests. The authenticated
model-change path (S3.2 rule 6 - controller-owned IPC, OS access control,
interactive owner confirmation, worker denial) is Phase 3; `set-codex-model` and
`set-claude-model` are stubs until then.
"""
from __future__ import annotations

import dataclasses
import os
import pathlib
import tomllib
from typing import Any, Mapping

from .models import digest_of

#: Runtime modes (S12). Limited-auto is listed so it can be REFUSED by name.
MODE_REPLAY = "replay"
MODE_SHADOW = "shadow"
MODE_SUPERVISED = "supervised"
MODE_LIMITED_AUTO = "limited-auto"
MODES = (MODE_REPLAY, MODE_SHADOW, MODE_SUPERVISED, MODE_LIMITED_AUTO)

#: Modes a configuration file is allowed to name as the boot default (S12:
#: "First install, update, policy change, schema migration, downgrade, or failed
#: recovery proof boots into shadow or supervised.").
BOOTABLE_DEFAULT_MODES = (MODE_SHADOW, MODE_SUPERVISED)

PROVIDERS = ("codex", "claude")

#: Sections/keys that carry controller authority and must never appear in the
#: runtime selection file.
_CONTROLLER_ONLY_KEYS = frozenset({
    "allowed_models", "limits", "policy", "security", "controller", "audit",
    "tiers", "hard_deny", "grants",
})

#: Keys that belong to the runtime selection file and must never appear in the
#: immutable controller config.
_RUNTIME_ONLY_KEYS = frozenset({
    "review_model", "advisory_model", "model", "fallback_models",
})

#: D-004-R751/R754/R758: the FIXED orchestrator-role model preference chain, in
#: order. It is owner policy, so it lives in the IMMUTABLE controller config
#: ([model_chain] below) and is owner-editable only; this tuple is the
#: fail-closed default used when the section is absent, and it matches the order
#: the owner named exactly. The ids are EXACT strings: nothing here normalizes,
#: aliases, or resolves an id, so no entry can ever become a different model
#: (notably never "claude-opus-5" - an id outside this chain is never selectable
#: regardless of what a model picker shows).
DEFAULT_ORCHESTRATOR_MODEL_CHAIN: tuple[str, ...] = (
    "claude-fable-5", "claude-opus-4-8", "claude-opus-4-7",
)

#: The one key `[model_chain]` carries.
_MODEL_CHAIN_KEY = "orchestrator_preference"


class ConfigError(ValueError):
    """A configuration file was rejected. Always fail closed, never default."""

    def __init__(self, code: str, message: str, path: str | None = None) -> None:
        location = f" [{path}]" if path else ""
        super().__init__(f"{code}: {message}{location}")
        self.code = code
        self.message = message
        self.path = path


# --------------------------------------------------------------------------
# Shared scanning helpers
# --------------------------------------------------------------------------


def _walk_keys(node: Any, trail: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    """Yield (key-path, value) for every key at every depth."""
    found: list[tuple[tuple[str, ...], Any]] = []
    if isinstance(node, Mapping):
        for key, value in node.items():
            path = trail + (str(key),)
            found.append((path, value))
            found.extend(_walk_keys(value, path))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            found.extend(_walk_keys(item, trail + (f"[{index}]",)))
    return found


def assert_no_effort_key(data: Mapping[str, Any], source: str) -> None:
    """Refuse any key containing "effort", at any depth (D-004-R159, S3.1)."""
    for path, _value in _walk_keys(data):
        leaf = path[-1]
        if "effort" in leaf.lower():
            raise ConfigError(
                "effort_key_forbidden",
                f"key {'.'.join(path)!r} is an effort key; effort keys are "
                f"permanently prohibited in every configuration file, prompt, and "
                f"CLI invocation",
                source,
            )


def _load_toml(path: str | os.PathLike[str]) -> dict[str, Any]:
    """Parse ONE file as standalone TOML. Never concatenated with another file."""
    file_path = pathlib.Path(path)
    if not file_path.exists():
        raise ConfigError("missing_file", f"configuration file not found", str(file_path))
    try:
        with file_path.open("rb") as handle:
            return tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError("invalid_toml", f"file is not valid standalone TOML: {exc}",
                          str(file_path)) from exc


def _require_string_list(value: Any, where: str, source: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ConfigError("not_a_list", f"{where} must be a list of model names", source)
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ConfigError("bad_model_name",
                              f"{where} contains a non-string or empty entry: {item!r}",
                              source)
        if item in out:
            raise ConfigError("duplicate_model",
                              f"{where} lists {item!r} more than once", source)
        out.append(item)
    return tuple(out)


# --------------------------------------------------------------------------
# Immutable controller config
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Limits:
    """Fail-closed bounded limits (S7, S13.8). Every limit has a safe default."""

    max_claude_turns_per_run: int = 12
    max_subprocess_seconds: int = 900
    max_restart_attempts: int = 3
    max_consecutive_invalid_outputs: int = 3
    max_supervisor_cycles_per_task: int = 60
    max_retained_log_bytes: int = 50_000_000
    max_review_packet_bytes: int = 262_144
    max_model_calls_per_task: int = 200
    max_external_writes_per_task: int = 20
    #: Per-DAY companions to the per-task model-call/external-write caps (S7).
    #: Bounded and fail-closed like every peer; the per-day window is rolled by
    #: the supervisor-supplied UTC date (CircuitBreakers.record_daily) so the
    #: bound is genuinely daily, never merely cumulative-per-run.
    max_model_calls_per_day: int = 2_000
    max_external_writes_per_day: int = 200
    #: Resource-reading ceilings sampled as gauges (S7). CPU is a whole-percent
    #: ceiling (a busy multi-core box can legitimately exceed 100, so this is an
    #: owner POLICY ceiling, not a hardware fact); memory is a resident-bytes
    #: ceiling. Both trip at/above the ceiling exactly like process_count.
    max_cpu_percent: int = 90
    max_memory_bytes: int = 8_589_934_592
    max_processes: int = 24
    min_free_disk_bytes: int = 1_073_741_824
    max_consecutive_no_progress: int = 3
    max_consecutive_hard_denies: int = 3
    max_codex_reviews_per_checkpoint: int = 3
    max_consecutive_revision_loops: int = 4
    warn_ratio: float = 0.75

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any], source: str) -> "Limits":
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(data) - known)
        if unknown:
            # S2.2's `--strict-config` philosophy: unrecognized fields fail closed.
            raise ConfigError("unknown_limit", f"unrecognized limit keys: {unknown}", source)
        values: dict[str, Any] = {}
        for name, raw in data.items():
            if name == "warn_ratio":
                if not isinstance(raw, (int, float)) or not 0 < float(raw) < 1:
                    raise ConfigError("bad_limit",
                                      "warn_ratio must be a number strictly between 0 and 1",
                                      source)
                values[name] = float(raw)
                continue
            if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
                raise ConfigError("bad_limit",
                                  f"limit {name!r} must be a positive integer, got {raw!r}",
                                  source)
            values[name] = raw
        return cls(**values)


@dataclasses.dataclass(frozen=True)
class ModelChain:
    """The FIXED orchestrator-role model preference chain (D-004-R751/R758).

    Owner policy, not a judgement: an orchestrator-role session walks THIS list
    in THIS order, first-available-wins, availability decided by an actual launch
    probe (never by reading a model picker - D-004-R752/R753). An id that is not
    in the list is never selectable (D-004-R754), and when no entry launches the
    supervisor stops and notifies the owner rather than continuing on a
    substitute (D-004-R755).

    Immutable, and read only from the immutable controller config, so a runtime
    file can never widen or reorder it.
    """

    entries: tuple[str, ...] = DEFAULT_ORCHESTRATOR_MODEL_CHAIN

    def __post_init__(self) -> None:
        if not self.entries:
            raise ConfigError(
                "empty_model_chain",
                f"[model_chain] {_MODEL_CHAIN_KEY} must name at least one model; an empty "
                f"chain would leave an orchestrator-role session with nothing to launch")

    def __contains__(self, model: object) -> bool:
        """EXACT string membership. No normalization, no aliasing, no prefixes."""
        return any(model == entry for entry in self.entries)

    def index_of(self, model: str) -> int:
        """The position of `model` in the chain, or -1 when it is not listed."""
        for position, entry in enumerate(self.entries):
            if entry == model:
                return position
        return -1

    def candidates_after(self, model: str) -> tuple[str, ...]:
        """The chain entries to try after `model` failed, in chain order.

        When `model` IS in the chain the walk resumes at the next entry. When it
        is not (a pin the owner did not list), the walk starts at the head of the
        chain but never re-offers the id that just failed. Either way every
        returned id came out of the chain, so nothing outside it is selectable.
        """
        position = self.index_of(model)
        if position >= 0:
            return self.entries[position + 1:]
        return tuple(entry for entry in self.entries if entry != model)


@dataclasses.dataclass(frozen=True)
class ControllerConfig:
    """Parsed immutable controller configuration (manifest-covered)."""

    codex_allowed_models: tuple[str, ...]
    claude_allowed_models: tuple[str, ...]
    default_mode: str
    limits: Limits
    source_path: str
    raw: dict[str, Any] = dataclasses.field(default_factory=dict, repr=False)
    #: D-004-R751/R758. Defaults to the fail-closed chain when `[model_chain]` is
    #: absent, so a config that predates this section still has the owner's order.
    model_chain: ModelChain = dataclasses.field(default_factory=ModelChain)

    def allowlist(self, provider: str) -> tuple[str, ...]:
        """The allowlist for ONE provider. Never merged across providers."""
        if provider == "codex":
            return self.codex_allowed_models
        if provider == "claude":
            return self.claude_allowed_models
        raise ConfigError("unknown_provider", f"unknown provider {provider!r}")

    def digest(self) -> str:
        return digest_of(self.raw)


def load_controller_config(path: str | os.PathLike[str]) -> ControllerConfig:
    """Load and validate `config.toml`."""
    source = str(path)
    data = _load_toml(path)
    assert_no_effort_key(data, source)

    for key in _RUNTIME_ONLY_KEYS:
        for key_path, _ in _walk_keys(data):
            if key_path[-1] == key:
                raise ConfigError(
                    "runtime_key_in_controller_config",
                    f"{'.'.join(key_path)!r} is a runtime model selection and belongs in "
                    f"model_selection.toml, not in the manifest-covered controller config",
                    source)

    codex_section = data.get("codex", {})
    claude_section = data.get("claude", {})
    for name, section in (("codex", codex_section), ("claude", claude_section)):
        if not isinstance(section, Mapping):
            raise ConfigError("bad_section", f"[{name}] must be a table", source)
        if "allowed_models" not in section:
            raise ConfigError("missing_allowlist",
                              f"[{name}] must declare allowed_models (an empty list is "
                              f"allowed and means 'no explicit selection permitted')",
                              source)

    codex_allowed = _require_string_list(codex_section["allowed_models"],
                                         "codex.allowed_models", source)
    claude_allowed = _require_string_list(claude_section["allowed_models"],
                                          "claude.allowed_models", source)

    controller_section = data.get("controller", {})
    if not isinstance(controller_section, Mapping):
        raise ConfigError("bad_section", "[controller] must be a table", source)
    default_mode = controller_section.get("default_mode", MODE_SHADOW)
    if default_mode not in MODES:
        raise ConfigError("unknown_mode",
                          f"controller.default_mode {default_mode!r} is not one of "
                          f"{list(MODES)}", source)
    if default_mode not in BOOTABLE_DEFAULT_MODES:
        raise ConfigError(
            "mode_not_bootable",
            f"controller.default_mode {default_mode!r} may never come from a configuration "
            f"file; limited-auto activates only by an explicit owner act recorded through "
            f"directive compliance", source)

    limits_section = data.get("limits", {})
    if not isinstance(limits_section, Mapping):
        raise ConfigError("bad_section", "[limits] must be a table", source)
    limits = Limits.from_mapping(limits_section, source)

    model_chain = _load_model_chain(data, source)

    return ControllerConfig(
        codex_allowed_models=codex_allowed,
        claude_allowed_models=claude_allowed,
        default_mode=default_mode,
        limits=limits,
        source_path=source,
        raw=data,
        model_chain=model_chain,
    )


def _load_model_chain(data: Mapping[str, Any], source: str) -> ModelChain:
    """Read `[model_chain]` out of the immutable controller config (D-004-R758).

    Absent -> the fail-closed default chain, in the owner's order. Present but
    malformed -> refused; the chain is never silently repaired, reordered, or
    partially applied, because a wrong chain is a wrong model selection.
    """
    section = data.get("model_chain", None)
    if section is None:
        return ModelChain()
    if not isinstance(section, Mapping):
        raise ConfigError("bad_section", "[model_chain] must be a table", source)
    unknown = sorted(set(section) - {_MODEL_CHAIN_KEY})
    if unknown:
        raise ConfigError("unknown_model_chain_key",
                          f"unrecognized [model_chain] keys: {unknown}; the only key is "
                          f"{_MODEL_CHAIN_KEY!r}", source)
    if _MODEL_CHAIN_KEY not in section:
        raise ConfigError(
            "missing_model_chain",
            f"[model_chain] must declare {_MODEL_CHAIN_KEY} (the ordered list of models an "
            f"orchestrator-role session may launch on); omit the whole section to accept "
            f"the default chain {list(DEFAULT_ORCHESTRATOR_MODEL_CHAIN)}", source)
    entries = _require_string_list(section[_MODEL_CHAIN_KEY],
                                   f"model_chain.{_MODEL_CHAIN_KEY}", source)
    for entry in entries:
        if entry != entry.strip():
            raise ConfigError(
                "bad_model_name",
                f"model_chain.{_MODEL_CHAIN_KEY} entry {entry!r} carries surrounding "
                f"whitespace; chain ids are used verbatim as the launched --model and are "
                f"never trimmed, normalized, or aliased", source)
    return ModelChain(entries=entries)


# --------------------------------------------------------------------------
# Runtime model selection
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ProviderSelection:
    """One provider's active selection and its OWN fallback chain."""

    provider: str
    primary: str
    fallback_models: tuple[str, ...]
    advisory_model: str = ""

    def chain(self) -> tuple[str, ...]:
        """Primary first, then this provider's fallbacks, in order."""
        return (self.primary,) + self.fallback_models if self.primary else self.fallback_models


@dataclasses.dataclass(frozen=True)
class ModelSelection:
    """Parsed `model_selection.toml`. Outside the manifest, digest-recorded."""

    codex: ProviderSelection
    claude: ProviderSelection
    source_path: str
    raw: dict[str, Any] = dataclasses.field(default_factory=dict, repr=False)

    def selection(self, provider: str) -> ProviderSelection:
        if provider == "codex":
            return self.codex
        if provider == "claude":
            return self.claude
        raise ConfigError("unknown_provider", f"unknown provider {provider!r}")

    def digest(self) -> str:
        """Recorded with every decision and every audit record (S3.2 rule 5)."""
        return digest_of(self.raw)


def load_model_selection(path: str | os.PathLike[str]) -> ModelSelection:
    """Load and structurally validate `model_selection.toml` (no allowlist check yet)."""
    source = str(path)
    data = _load_toml(path)
    assert_no_effort_key(data, source)

    for key_path, _ in _walk_keys(data):
        if key_path[-1] in _CONTROLLER_ONLY_KEYS:
            raise ConfigError(
                "controller_key_in_runtime_file",
                f"{'.'.join(key_path)!r} carries controller authority and may never live in "
                f"the runtime model-selection file; changing a model must not be able to "
                f"alter limits, policy, tiers, or allowlists",
                source)

    codex_section = data.get("codex", {})
    claude_section = data.get("claude", {})
    for name, section in (("codex", codex_section), ("claude", claude_section)):
        if not isinstance(section, Mapping):
            raise ConfigError("bad_section", f"[{name}] must be a table", source)

    codex = ProviderSelection(
        provider="codex",
        primary=_require_string_or_empty(codex_section.get("review_model", ""),
                                         "codex.review_model", source),
        advisory_model=_require_string_or_empty(codex_section.get("advisory_model", ""),
                                                "codex.advisory_model", source),
        fallback_models=_require_string_list(codex_section.get("fallback_models", []),
                                             "codex.fallback_models", source),
    )
    claude = ProviderSelection(
        provider="claude",
        primary=_require_string_or_empty(claude_section.get("model", ""),
                                         "claude.model", source),
        fallback_models=_require_string_list(claude_section.get("fallback_models", []),
                                             "claude.fallback_models", source),
    )
    return ModelSelection(codex=codex, claude=claude, source_path=source, raw=data)


def _require_string_or_empty(value: Any, where: str, source: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ConfigError("bad_model_name", f"{where} must be a string", source)
    return value.strip()


# --------------------------------------------------------------------------
# Cross-file validation
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class SelectionValidation:
    """Result of validating a selection against the controller allowlists."""

    ok: bool
    errors: tuple[str, ...] = ()
    selection_digest: str = ""


def validate_selection(
    config: ControllerConfig,
    selection: ModelSelection,
    *,
    raise_on_error: bool = True,
) -> SelectionValidation:
    """Validate every selected/fallback model against its OWN provider's allowlist.

    The cross-provider rule is the point of this function: a model that appears
    only in the Claude allowlist can never satisfy a Codex role, and vice versa.
    """
    errors: list[str] = []

    for provider in PROVIDERS:
        allowed = config.allowlist(provider)
        chosen = selection.selection(provider)
        other = "claude" if provider == "codex" else "codex"
        other_allowed = config.allowlist(other)

        candidates: list[tuple[str, str]] = []
        if chosen.primary:
            role = "review_model" if provider == "codex" else "model"
            candidates.append((role, chosen.primary))
        if provider == "codex" and chosen.advisory_model:
            candidates.append(("advisory_model", chosen.advisory_model))
        for index, name in enumerate(chosen.fallback_models):
            candidates.append((f"fallback_models[{index}]", name))

        if chosen.primary and not allowed:
            errors.append(
                f"{provider}.{'review_model' if provider == 'codex' else 'model'} is set to "
                f"{chosen.primary!r} but {provider}.allowed_models is empty; an empty "
                f"allowlist means only the account/CLI default may be used and no explicit "
                f"selection is permitted")

        for role, name in candidates:
            if name in allowed:
                continue
            if name in other_allowed:
                errors.append(
                    f"{provider}.{role} = {name!r} is not in {provider}.allowed_models; it "
                    f"appears only in {other}.allowed_models and a {other} entry can never "
                    f"satisfy a {provider} role")
            else:
                errors.append(
                    f"{provider}.{role} = {name!r} is not in {provider}.allowed_models and "
                    f"must never be used in any role")

        if len(set(chosen.fallback_models)) != len(chosen.fallback_models):
            errors.append(f"{provider}.fallback_models contains duplicates")
        if chosen.primary and chosen.primary in chosen.fallback_models:
            errors.append(
                f"{provider}.fallback_models repeats the primary model {chosen.primary!r}")

    result = SelectionValidation(
        ok=not errors,
        errors=tuple(errors),
        selection_digest=selection.digest(),
    )
    if errors and raise_on_error:
        raise ConfigError("selection_rejected", "; ".join(errors), selection.source_path)
    return result


def load_validated(
    config_path: str | os.PathLike[str],
    selection_path: str | os.PathLike[str],
) -> tuple[ControllerConfig, ModelSelection]:
    """Load both files independently, then validate the selection against the config."""
    config = load_controller_config(config_path)
    selection = load_model_selection(selection_path)
    validate_selection(config, selection)
    return config, selection
