"""Canonical property-profile contract metadata + backend response validation
(task M2-T003, owner code-audit P0 2026-07-17).

This module is the SINGLE backend source of truth for:

- which ``contract_version`` values are PUBLISHED (the closed enum), sourced
  live from ``property_profile.schema.json`` so the API can never drift from
  the schema (no hard-coded stale version anywhere - the M2-T003 mandate);
- which contract version each OPTIONAL top-level key was introduced in, so a
  declared version can be checked for consistency against the emitted key set;
- validation of a built profile against the SELECTED canonical schema before
  it is sent (an invalid 200 becomes impossible).

Design (task packet items A/B/C):

- ``PROFILE_CONTRACT_VERSION`` (in builder.py) is the version the builder
  DECLARES. M2-T003 resolves the M2-T004 deferral (README section 167): the
  builder declares ``1.2.0`` because it emits keys through 1.2.0. Every added
  key is optional, so 1.0.0 and 1.1.0 instances remain valid and are served
  unchanged (backward compatibility, S7).
- The validator SELECTS the schema by the payload's DECLARED version against
  the closed published enum; an unpublished version yields a bounded
  ``unsupported_contract_version`` error rather than a silent coercion or a
  raw 500 (S8). Because the schema's ``contract_version`` enum is itself
  closed, structural validation ALSO rejects an unpublished version; the
  explicit pre-check produces the bounded, typed, correlation-id'd signal the
  API layer needs instead of a generic schema failure.
- Declared-version-vs-emitted-key-set consistency (S6): the declared version
  must be at least the minimum version that introduces any emitted optional
  key. Declaring 1.0.0 while emitting a 1.2.0-only key is a contract defect
  and is rejected (this is exactly the stale-declaration bug M2-T004
  deferred here).

No network, no new dependency: validation uses the ``jsonschema`` engine that
the connector tests and ``.github/scripts/validate_contracts.py`` already
use, with the same $ref registry pattern (``referencing`` when importable,
legacy ``RefResolver`` otherwise).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

__all__ = [
    "ContractValidationError",
    "SUPPORTED_CONTRACT_VERSIONS",
    "UnsupportedContractVersionError",
    "VERSION_INTRODUCED",
    "select_schema_version",
    "validate_profile",
]

# packages/contracts/schemas/v1 relative to this file:
# services/api/app/profile/contract.py -> repo root is parents[4].
_REPO_ROOT = Path(__file__).resolve().parents[4]
_SCHEMA_DIR = _REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
_PROFILE_SCHEMA = _SCHEMA_DIR / "property_profile.schema.json"

# The four documents a property_profile $ref registry must load (README:
# "Consumers that build their own $ref registry ... must load all four").
_SCHEMA_FILES = (
    "property_profile.schema.json",
    "source_fact.schema.json",
    "common.schema.json",
    "coverage_status.schema.json",
)

# Optional top-level keys introduced after 1.0.0. Sourced from the contract
# README (1.1.0 = M1-T006; 1.2.0 = M2-T004). Used ONLY for the declared-vs-
# emitted consistency check; the schema itself remains the authority for
# structural validity. Per-fact coverage_status and the zoning
# district-provenance maps are also 1.1.0 additions but live inside required
# containers, so top-level presence is the sufficient, robust signal here.
VERSION_INTRODUCED: dict[str, str] = {
    "data_completeness": "1.1.0",
    "reproducibility": "1.1.0",
    "status_dimensions": "1.2.0",
}


class ContractValidationError(Exception):
    """A built profile failed validation against its selected canonical
    schema, or its declared version is inconsistent with the keys it emits.

    Raised on the SERVER side before send. The API layer maps this to a typed
    ``500 internal_contract_error`` with the correlation id: an internal
    defect produced a payload that does not honor the contract, and an invalid
    200 must be impossible."""

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


class UnsupportedContractVersionError(Exception):
    """The profile declares a ``contract_version`` that is not in the closed
    published enum. Mapped by the API to a BOUNDED typed error (never a silent
    coercion, never a raw 500 stack) - S8/C."""

    def __init__(self, message: str, *, declared_version: str) -> None:
        super().__init__(message)
        self.declared_version = declared_version


@lru_cache(maxsize=1)
def _profile_schema() -> dict:
    return json.loads(_PROFILE_SCHEMA.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _supported_versions() -> tuple[str, ...]:
    """The CLOSED published enum, read live from the schema (never hard-coded
    in the backend). If the schema shape ever changes so this cannot be read,
    fail loudly rather than silently guess a version set."""
    schema = _profile_schema()
    try:
        enum = schema["properties"]["profile_version"]["properties"][
            "contract_version"
        ]["enum"]
    except (KeyError, TypeError) as exc:  # pragma: no cover - schema shape guard
        raise RuntimeError(
            "property_profile.schema.json no longer exposes the "
            "profile_version.contract_version enum; the backend cannot "
            "determine the closed set of published contract versions"
        ) from exc
    if not enum:
        raise RuntimeError("contract_version enum is empty in the schema")
    return tuple(enum)


# Public constant (a tuple; the closed published set). Evaluated at import so
# a bad schema fails fast at startup rather than on first request.
SUPPORTED_CONTRACT_VERSIONS: tuple[str, ...] = _supported_versions()


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def select_schema_version(declared_version: str) -> str:
    """Return the published contract version to validate against, SELECTED
    from the declared version against the closed enum.

    Raises:
        UnsupportedContractVersionError: the declared version is not published
            (bounded, typed - S8). Never coerces to a nearby version.
    """
    if declared_version not in SUPPORTED_CONTRACT_VERSIONS:
        raise UnsupportedContractVersionError(
            "declared contract_version "
            f"{declared_version!r} is not a published version "
            f"{list(SUPPORTED_CONTRACT_VERSIONS)!r}; the profile is rejected "
            "rather than coerced or served",
            declared_version=declared_version,
        )
    return declared_version


def _assert_declared_matches_emitted(profile: dict) -> None:
    """Declared-version-vs-emitted-key-set consistency (S6/B).

    The declared version must be >= the minimum version that introduces any
    optional top-level key present in the payload. Declaring a stale version
    (e.g. 1.0.0) while emitting a later-version key is the exact defect
    M2-T004 deferred to this task, and is now rejected."""
    declared = profile["profile_version"]["contract_version"]
    declared_tuple = _version_tuple(declared)
    for key, introduced in VERSION_INTRODUCED.items():
        if key in profile and _version_tuple(introduced) > declared_tuple:
            raise ContractValidationError(
                f"profile declares contract_version {declared!r} but emits "
                f"key {key!r} introduced in {introduced!r}; the declared "
                "version must cover every emitted key",
                reason="declared_version_below_emitted_keys",
            )


@lru_cache(maxsize=1)
def _validator():
    """Build a jsonschema validator for property_profile.schema.json with the
    common + source_fact + coverage_status contracts resolved. Mirrors the
    test suite and validate_contracts.py exactly (referencing when importable,
    legacy RefResolver otherwise)."""
    import jsonschema

    docs = [
        json.loads((_SCHEMA_DIR / name).read_text(encoding="utf-8"))
        for name in _SCHEMA_FILES
    ]
    schema = docs[0]
    try:
        from referencing import Registry, Resource

        registry = Registry().with_resources(
            [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
        )
        return jsonschema.Draft202012Validator(schema, registry=registry)
    except ImportError:  # pragma: no cover - exercised only on legacy runners
        resolver = jsonschema.RefResolver(
            base_uri=schema["$id"],
            referrer=schema,
            store={doc["$id"]: doc for doc in docs},
        )
        return jsonschema.Draft202012Validator(schema, resolver=resolver)


def validate_profile(profile: dict) -> None:
    """Validate a built property profile against the SELECTED canonical schema
    before send. Raises on any defect so an invalid 200 is impossible.

    Order (deterministic, each failure typed distinctly):

    1. structural: ``profile_version.contract_version`` must be present and a
       string (defends the version selection below against malformed inputs);
    2. version selection against the closed published enum -> bounded
       ``UnsupportedContractVersionError`` (S8/C);
    3. declared-vs-emitted-key-set consistency (S6/B);
    4. full JSON Schema validation against the canonical contract (S1/S2).

    Raises:
        ContractValidationError: structural/schema/consistency failure ->
            API maps to typed ``500 internal_contract_error``.
        UnsupportedContractVersionError: unpublished declared version ->
            API maps to a bounded typed error.
    """
    version_block = profile.get("profile_version")
    if not isinstance(version_block, dict):
        raise ContractValidationError(
            "profile is missing the required profile_version object",
            reason="missing_profile_version",
        )
    declared = version_block.get("contract_version")
    if not isinstance(declared, str):
        raise ContractValidationError(
            "profile_version.contract_version must be a string; got "
            f"{type(declared).__name__}",
            reason="malformed_contract_version",
        )

    # Bounded unsupported-version signal (before schema validation so the API
    # can distinguish "unpublished version" from a generic contract defect).
    select_schema_version(declared)

    _assert_declared_matches_emitted(profile)

    validator = _validator()
    errors = sorted(validator.iter_errors(profile), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise ContractValidationError(
            f"built profile failed canonical schema validation at {location}: "
            f"{first.message}",
            reason="schema_validation_failed",
        )
