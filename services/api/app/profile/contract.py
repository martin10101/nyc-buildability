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
  DECLARES under the declare-what-you-emit rule M2-T003 established (resolving
  the M2-T004 deferral, README section 167). Task M2-T006 advanced it to
  ``1.3.0`` because the builder now emits keys through 1.3.0 (the typed
  ``reproducibility.staleness`` object). Every added key is optional, so
  1.0.0, 1.1.0, and 1.2.0 instances remain valid and are served unchanged
  (backward compatibility, S7). Docstring corrected by task M2-T010 (M2-T006
  G3 LOW D1: this text previously still described 1.2.0 as current).
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

No network, no new dependency beyond the runtime ``jsonschema`` engine that
the connector tests and ``.github/scripts/validate_contracts.py`` already
use, with the same $ref registry pattern (``referencing`` when importable,
legacy ``RefResolver`` otherwise).

SCHEMA SOURCING — PRODUCTION-SAFE (task M2-T003 rework):
The canonical source of authority for these schemas is
``packages/contracts/schemas/v1/*.schema.json``. However this module loads the
schemas from PACKAGE DATA bundled inside the installed ``app`` package
(``app/_contract_schemas/v1/``) via ``importlib.resources``, NOT via a
repo-relative ``__file__`` walk. That is mandatory because a deployable
FastAPI service is installed non-editable (``pip install ./services/api`` in
web-e2e CI and every production image): ``app/`` then lives in site-packages
with no sibling ``packages/`` directory, so a repo-relative walk raised
``FileNotFoundError`` at import. The bundled copies are byte-identical build
artifacts of the canonical files, produced and verified by
``services/api/scripts/sync_contract_schemas.py`` and the
``contracts-schema-bundle`` CI drift check.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources

__all__ = [
    "ContractValidationError",
    "SUPPORTED_CONTRACT_VERSIONS",
    "UnsupportedContractVersionError",
    "VERSION_INTRODUCED",
    "select_schema_version",
    "validate_profile",
]

# Runtime-bundled schema package (package DATA inside the installed app).
_SCHEMA_PACKAGE = "app._contract_schemas.v1"

# The four documents a property_profile $ref registry must load (README:
# "Consumers that build their own $ref registry ... must load all four").
_SCHEMA_FILES = (
    "property_profile.schema.json",
    "source_fact.schema.json",
    "common.schema.json",
    "coverage_status.schema.json",
)


def _load_bundled_schema(name: str) -> dict:
    """Load one bundled contract schema via importlib.resources.

    Works identically from a source tree and from a non-editable install
    (site-packages), because the schema files ship as package data inside the
    ``app`` package. No ``packages/``-relative filesystem access occurs."""
    text = resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)

# Optional keys introduced after 1.0.0, keyed by DOTTED PATH from the profile
# root (task M2-T006 extended the plain top-level keys with dotted-path
# resolution so nested additive keys - the 1.3.0 reproducibility.staleness
# object - participate in the declared-vs-emitted consistency check). Sourced
# from the contract README (1.1.0 = M1-T006; 1.2.0 = M2-T004; 1.3.0 =
# M2-T006). Used ONLY for the consistency check; the schema itself remains
# the authority for structural validity. Per-fact coverage_status and the
# zoning district-provenance maps are also 1.1.0 additions but live inside
# required containers, so top-level presence is the sufficient, robust signal
# for 1.1.0.
VERSION_INTRODUCED: dict[str, str] = {
    "data_completeness": "1.1.0",
    "reproducibility": "1.1.0",
    "status_dimensions": "1.2.0",
    "reproducibility.staleness": "1.3.0",
    # Task M2-T012 (contract 1.4.0): the three additive top-level wave/spatial
    # integration keys. A profile emitting any of them must declare >= 1.4.0,
    # so a stale-declared payload carrying wave facts is rejected exactly like
    # the earlier additive keys (the declared-vs-emitted consistency check).
    "zoning_features": "1.4.0",
    "lot_geometry": "1.4.0",
    "spatial_intersection": "1.4.0",
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
    return _load_bundled_schema("property_profile.schema.json")


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


def _dotted_path_present(profile: dict, dotted_key: str) -> bool:
    """True when every segment of a dotted path exists in the payload
    (intermediate segments must be dicts). ``"reproducibility.staleness"`` is
    present only when ``reproducibility`` is a dict carrying ``staleness``.
    Task M2-T006: lets nested additive keys participate in the consistency
    check without changing the plain top-level behavior."""
    node: object = profile
    for segment in dotted_key.split("."):
        if not isinstance(node, dict) or segment not in node:
            return False
        node = node[segment]
    return True


def _assert_declared_matches_emitted(profile: dict) -> None:
    """Declared-version-vs-emitted-key-set consistency (S6/B).

    The declared version must be >= the minimum version that introduces any
    optional (dotted-path) key present in the payload. Declaring a stale
    version (e.g. 1.0.0) while emitting a later-version key is the exact
    defect M2-T004 deferred to M2-T003, and is rejected; M2-T006 extends the
    same rule to the nested 1.3.0 key ``reproducibility.staleness``."""
    declared = profile["profile_version"]["contract_version"]
    declared_tuple = _version_tuple(declared)
    for key, introduced in VERSION_INTRODUCED.items():
        if _dotted_path_present(profile, key) \
                and _version_tuple(introduced) > declared_tuple:
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

    docs = [_load_bundled_schema(name) for name in _SCHEMA_FILES]
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
