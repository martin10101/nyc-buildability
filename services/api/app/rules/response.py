"""Serialize a PropertyRuleEvaluation into the rule_evaluation @ 1.0.0 contract
(task M4-T005 phase 2).

This module MAPS an already-computed :class:`~app.rules.integration.PropertyRuleEvaluation`
onto the versioned ``rule_evaluation`` response document; it never evaluates a
rule, decides law, or reshapes a value. Load-bearing guarantees:

* Input by reference, NEVER embedded (owner directive, M4-T005). The response
  carries the evaluated ``bbl``, the evaluated profile's ``contract_version``,
  the ``input_provenance`` refs, and a deterministic ``input_fingerprint`` -
  it does NOT embed a copy of the property profile. The two fields that
  ``PropertyRuleEvaluation.as_dict`` exposes at top level (``bbl`` and
  ``input_provenance``) are MOVED into ``evaluated_input`` so the top-level shape
  is exactly the contract's ``additionalProperties: false`` root.
* Never Verified at the boundary. :func:`serialize_rule_evaluation` calls
  ``assert_not_verified`` on the finished document (belt-and-suspenders with
  ``PropertyRuleEvaluation.export``), so a ``verified`` status can never leave
  this layer even if a future refactor introduces one.
* Deterministic fingerprint. ``input_fingerprint`` is a ``sha256:``-prefixed hex
  digest (common.schema.json ``digest_sha256`` shape) over the canonical
  (sorted-key, tight-separator, non-ASCII-preserving) JSON of the exact evaluator
  INPUT the result was derived from - so the same profile always yields the same
  fingerprint and a consumer can confirm a result came from a specific input
  snapshot WITHOUT storing the profile.
* Strict, offline schema validation. :func:`validate_rule_evaluation_document`
  validates the finished document against the bundled ``rule_evaluation`` schema
  (loaded read-only from ``app._contract_schemas.v1`` via ``importlib.resources``,
  the same package-data path ``app.profile.contract`` uses, so it works from a
  non-editable install with no ``packages/`` sibling). An invalid document is
  never returned.

The serializer is intentionally decoupled from any endpoint: a later
aggregate-analysis endpoint can call it unchanged for each property it evaluates.
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from importlib import resources

from .integration import PropertyRuleEvaluation, assert_not_verified

__all__ = [
    "RULE_EVALUATION_CONTRACT_VERSION",
    "RuleEvaluationContractError",
    "compute_input_fingerprint",
    "serialize_rule_evaluation",
    "validate_rule_evaluation_document",
]

# The contract version this serializer emits - a published value in the closed
# rule_evaluation.schema.json contract_version enum (M4-T005 phase 1).
RULE_EVALUATION_CONTRACT_VERSION = "1.0.0"

# Runtime-bundled schema package (package DATA inside the installed app), the
# same source app.profile.contract loads from. The bundle copies are
# byte-identical build artifacts of packages/contracts/schemas/v1 whose identity
# the phase-1 contract test guards.
_SCHEMA_PACKAGE = "app._contract_schemas.v1"

# rule_evaluation.schema.json's external $refs resolve into exactly these two
# sibling contracts (verified against the schema): the canonical coverage
# vocabulary and the shared common value shapes. coverage_status.schema.json
# carries no external $ref of its own.
_REGISTRY_SCHEMA_FILES = (
    "rule_evaluation.schema.json",
    "common.schema.json",
    "coverage_status.schema.json",
)


class RuleEvaluationContractError(Exception):
    """A serialized rule_evaluation document failed strict validation against the
    bundled canonical schema before send.

    Raised on the SERVER side. The API layer maps this to a typed internal error
    (never a raw 500 stack), because a document that does not honor the contract
    is an internal defect - an invalid 200 must be impossible, mirroring the
    property-profile ``ContractValidationError`` path."""

    def __init__(self, message: str, *, location: str) -> None:
        super().__init__(message)
        self.location = location


def _canonical_json(value: object) -> str:
    """Canonical JSON per the contract's ``canonical-json-1`` spec: keys sorted
    lexicographically, tight ``','``/``':'`` separators, non-ASCII preserved
    (never escaped), and no NaN/Infinity (rejected). Digesting the parsed value
    makes the digest independent of insignificant whitespace and key order."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def compute_input_fingerprint(
    evaluation: PropertyRuleEvaluation, *, as_of_date: str | None = None
) -> str:
    """Deterministic ``sha256:``-prefixed digest of the exact evaluator INPUT the
    result was derived from.

    The fingerprint pins the identifying inputs - bbl, the derived zoning
    district and its source, the lot-area input and its source, the evaluation
    ``as_of_date``, and the compact identifying spatial facts (``spatial_context``)
    - WITHOUT storing the profile. On a fail-safe short-circuit the derived
    inputs are null; ``bbl`` still distinguishes one property's fail-safe from
    another's. The digest shape is ``common.schema.json`` ``digest_sha256``
    (``^sha256:[0-9a-f]{64}$``)."""
    fingerprint_input = {
        "bbl": evaluation.bbl,
        "zoning_district": evaluation.zoning_district,
        "lot_area_sq_ft": evaluation.lot_area_sq_ft,
        "lot_area_source": evaluation.lot_area_source,
        "as_of_date": as_of_date,
        "spatial_context": evaluation.spatial_context,
    }
    canonical = _canonical_json(fingerprint_input)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def serialize_rule_evaluation(
    evaluation: PropertyRuleEvaluation,
    *,
    profile_contract_version: str,
    as_of_date: str | None = None,
) -> dict:
    """Map a :class:`PropertyRuleEvaluation` onto a rule_evaluation @ 1.0.0
    document.

    ``profile_contract_version`` is the ``contract_version`` of the evaluated
    property_profile instance (e.g. ``"1.4.0"``). ``as_of_date`` is the temporal
    gate the evaluation used (default ``None``); it participates in the
    fingerprint only.

    Fails closed if a ``verified`` status ever slipped in (``assert_not_verified``
    on the finished document). Does NOT validate against the JSON schema - call
    :func:`validate_rule_evaluation_document` for that (the endpoint does both).
    """
    # export() is the fail-closed dict form (raises on any verified status).
    payload = evaluation.export()

    # Move the two by-reference identity fields off the top level into
    # evaluated_input; the remaining keys are exactly the contract's other root
    # fields, so the finished document honors additionalProperties: false.
    bbl = payload.pop("bbl")
    input_provenance = payload.pop("input_provenance")

    document = {
        "contract_version": RULE_EVALUATION_CONTRACT_VERSION,
        "evaluated_input": {
            "bbl": bbl,
            "profile_contract_version": profile_contract_version,
            "input_fingerprint": compute_input_fingerprint(
                evaluation, as_of_date=as_of_date
            ),
            "input_provenance": input_provenance,
        },
        **payload,
    }

    # Boundary guarantee: a draft rule_evaluation document is never Verified.
    assert_not_verified(document)
    return document


@lru_cache(maxsize=1)
def _validator():
    """Strict Draft 2020-12 validator for rule_evaluation.schema.json with its
    common + coverage_status $refs resolved. Built once, from the bundled package
    data (works from a non-editable install), mirroring app.profile.contract."""
    import jsonschema

    docs = [_load_bundled_schema(name) for name in _REGISTRY_SCHEMA_FILES]
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


def _load_bundled_schema(name: str) -> dict:
    text = resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)


def validate_rule_evaluation_document(document: dict) -> None:
    """Validate a serialized document against the bundled rule_evaluation schema,
    strictly, before send. Raises :class:`RuleEvaluationContractError` on any
    defect so an invalid 200 is impossible (mirrors validate_profile).

    The ``reason``/``location`` carried on the error is a fixed, non-secret schema
    path; the detailed message stays server-side (the API logs it by correlation
    id and returns only a generic typed error)."""
    validator = _validator()
    errors = sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise RuleEvaluationContractError(
            f"rule_evaluation document failed canonical schema validation at "
            f"{location}: {first.message}",
            location=location,
        )
