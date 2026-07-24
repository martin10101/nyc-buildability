"""Allowlist serializers for the closed canonical provenance/audit contracts.

Task M2-T017 (DF-4/DF-5, whole-system trust replan Area G).

WHAT THIS IS
------------
A deterministic, stdlib-only serializer that enforces the *documented key set*
of the two canonical contracts that M2-T017 closed with
``additionalProperties:false``:

- ``source_fact`` (the mandatory provenance record, PRD section 9), and
- ``analysis_state_transition`` (the audit record, PRD section 32.1).

For each contract the serializer:

1. REJECTS any key that is not a documented contract property. This is the
   runtime twin of ``additionalProperties:false``: a mistyped OPTIONAL field
   (e.g. ``unit`` for ``units``) or a leaked internal/diagnostic field
   (e.g. a stack trace, an internal error object, a token) can never be
   written into a provenance or audit record.
2. REQUIRES every mandatory field to be present.
3. Returns a NEW dict containing ONLY the documented fields, in canonical
   schema order, so the emitted record round-trips exactly the documented
   shape and nothing else.

DIAGNOSTIC-LEAK SAFETY
----------------------
When the serializer rejects a record it names the offending KEYS only, never
their VALUES. The whole point is that internal/diagnostic content must not
escape; echoing a rejected value into an exception message (which is then
logged) would defeat that. See ``UnknownFieldError``.

FROZEN INTERFACE — NOT WIRED (task M2-T017 scope boundary)
----------------------------------------------------------
This module is a frozen interface only. Nothing in the production request path
(``app/api/**``) or the profile builder (``app/profile/builder.py``) imports it
in this task; wiring the serializer into the builder's provenance assembly is
explicitly deferred to a later controller-contracted integration task
(FIRST-WAVE-INTEGRATION-CONTRACT.md, lane 3 downstream integration). Adding an
import from a production entrypoint here would exceed this task's file scope and
change a shared serializer boundary without the sequenced integration gate.

DESIGN NOTES
------------
- The allowlists are declared as explicit frozen tuples in canonical schema
  order rather than loaded from the schema files at import time, so the module
  is fully self-contained (import-safe from site-packages; no file I/O; thin-
  client friendly, docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md). A contract
  test (``services/api/tests/contracts/test_contract_serializers.py``) asserts
  each allowlist is byte-for-byte the canonical schema's ``properties`` /
  ``required`` sets, so a frozen tuple can never silently drift from the schema.
- Key-level (allowlist) enforcement only. VALUE-level validation (types,
  patterns, enums) remains the JSON-schema validator's job
  (``.github/scripts/validate_contracts.py`` / ``jsonschema``); the two layers
  are complementary and deliberately not merged.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ContractSerializationError(ValueError):
    """Base error for an allowlist-serialization failure."""


class UnknownFieldError(ContractSerializationError):
    """Raised when a record carries a key that is not a documented property.

    The message names the offending KEYS ONLY (sorted, deterministic) and NEVER
    their values, so a leaked diagnostic value can never travel out through the
    exception / logs (DF-4/DF-5 diagnostic-leak safety)."""

    def __init__(self, schema_name: str, unknown_keys: list[str]) -> None:
        self.schema_name = schema_name
        self.unknown_keys = sorted(unknown_keys)
        super().__init__(
            f"{schema_name}: rejected undocumented key(s) {self.unknown_keys}; "
            "the contract is closed (additionalProperties:false). A mistyped "
            "field or a leaked internal/diagnostic field is never accepted."
        )


class MissingFieldError(ContractSerializationError):
    """Raised when a mandatory (required) contract field is absent."""

    def __init__(self, schema_name: str, missing_keys: list[str]) -> None:
        self.schema_name = schema_name
        self.missing_keys = sorted(missing_keys)
        super().__init__(
            f"{schema_name}: missing required field(s) {self.missing_keys}."
        )


# ---------------------------------------------------------------------------
# Serializer
# ---------------------------------------------------------------------------


class AllowlistSerializer:
    """Strict allowlist serializer for one closed canonical contract.

    ``allowed_fields`` is the documented property set in canonical schema
    order; ``required_fields`` is the mandatory subset. ``serialize`` projects
    an input mapping onto exactly the documented fields, rejecting any
    undocumented key and any missing required field.
    """

    __slots__ = ("schema_name", "_allowed", "_required", "_allowed_set")

    def __init__(
        self, schema_name: str, allowed_fields: tuple[str, ...], required_fields: tuple[str, ...]
    ) -> None:
        allowed_set = set(allowed_fields)
        missing_required = [f for f in required_fields if f not in allowed_set]
        if missing_required:
            # Programming error in this module, caught at import time.
            raise ValueError(
                f"{schema_name}: required fields {missing_required} are not in "
                "allowed_fields; the frozen constants are inconsistent."
            )
        self.schema_name = schema_name
        self._allowed = tuple(allowed_fields)
        self._required = tuple(required_fields)
        self._allowed_set = allowed_set

    @property
    def allowed_fields(self) -> tuple[str, ...]:
        """Documented property names, in canonical schema order."""
        return self._allowed

    @property
    def required_fields(self) -> tuple[str, ...]:
        """Mandatory property names, in canonical schema order."""
        return self._required

    def serialize(self, record: Mapping[str, Any]) -> dict[str, Any]:
        """Return a new dict with ONLY the documented fields, in canonical order.

        Raises:
            TypeError: ``record`` is not a mapping.
            UnknownFieldError: ``record`` carries a key that is not a documented
                property (a typo or a leaked diagnostic/internal field).
            MissingFieldError: a required field is absent.

        The input is never mutated; values are copied by reference (a shallow
        projection - value-shape validation is the JSON-schema layer's job).
        """
        if not isinstance(record, Mapping):
            raise TypeError(
                f"{self.schema_name}: record must be a mapping, got "
                f"{type(record).__name__}"
            )
        unknown = [key for key in record if key not in self._allowed_set]
        if unknown:
            raise UnknownFieldError(self.schema_name, unknown)
        missing = [field for field in self._required if field not in record]
        if missing:
            raise MissingFieldError(self.schema_name, missing)
        return {field: record[field] for field in self._allowed if field in record}

    def is_serializable(self, record: Mapping[str, Any]) -> bool:
        """True iff ``serialize(record)`` would succeed (no raise). Convenience
        for callers that want a boolean check without catching exceptions."""
        try:
            self.serialize(record)
        except (TypeError, ContractSerializationError):
            return False
        return True


# ---------------------------------------------------------------------------
# Frozen allowlists — declared in canonical schema order.
# Guarded against schema drift by test_contract_serializers.py, which asserts
# each tuple equals the canonical schema's `properties` / `required` in order.
# ---------------------------------------------------------------------------

# packages/contracts/schemas/v1/source_fact.schema.json (closed by M2-T017).
_SOURCE_FACT_FIELDS: tuple[str, ...] = (
    # PRD section 9 mandatory provenance fields (required):
    "provenance_id",
    "source_id",
    "original_field_name",
    "original_value",
    "normalized_value",
    "units",  # optional
    "retrieved_at",
    "dataset_version",
    "effective_date",
    "bbl",
    "confidence",
    "user_confirmed_or_overridden",
    "conflict_status",
    # M2-T004 identity + snapshot-lineage keys (optional):
    "fact_key",
    "observation_id",
    "value_digest",
    "response_digest",
    # M2-T017 documented connector-lineage keys (optional):
    "dataset_id",
    "request_url",
    "input_vintages",
    "source_rows_updated_at",
)
_SOURCE_FACT_REQUIRED: tuple[str, ...] = (
    "provenance_id",
    "source_id",
    "original_field_name",
    "original_value",
    "normalized_value",
    "retrieved_at",
    "dataset_version",
    "effective_date",
    "bbl",
    "confidence",
    "user_confirmed_or_overridden",
    "conflict_status",
)

# packages/contracts/schemas/v1/analysis_state_transition.schema.json (closed).
_ANALYSIS_STATE_TRANSITION_FIELDS: tuple[str, ...] = (
    "run_id",
    "from_state",
    "to_state",
    "occurred_at",
    "actor",
    "correlation_id",
    "reason",  # optional
)
_ANALYSIS_STATE_TRANSITION_REQUIRED: tuple[str, ...] = (
    "run_id",
    "from_state",
    "to_state",
    "occurred_at",
    "actor",
    "correlation_id",
)

SOURCE_FACT_SERIALIZER = AllowlistSerializer(
    "source_fact", _SOURCE_FACT_FIELDS, _SOURCE_FACT_REQUIRED
)
ANALYSIS_STATE_TRANSITION_SERIALIZER = AllowlistSerializer(
    "analysis_state_transition",
    _ANALYSIS_STATE_TRANSITION_FIELDS,
    _ANALYSIS_STATE_TRANSITION_REQUIRED,
)
