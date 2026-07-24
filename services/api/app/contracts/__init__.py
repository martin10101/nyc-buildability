"""Canonical-contract serialization helpers (task M2-T017, DF-4/DF-5).

This package holds the FROZEN, un-wired allowlist serializer for the two
now-closed provenance/audit contracts (``source_fact`` and
``analysis_state_transition``). It is deliberately NOT imported by any
production route or builder in this task; a later controller-contracted
integration task wires it into ``app/profile/builder.py`` (schema-before-
integration order). See ``serializers.py`` for the interface.
"""

from app.contracts.serializers import (  # noqa: F401 - re-export the frozen interface
    ANALYSIS_STATE_TRANSITION_SERIALIZER,
    SOURCE_FACT_SERIALIZER,
    AllowlistSerializer,
    ContractSerializationError,
    MissingFieldError,
    UnknownFieldError,
)

__all__ = [
    "AllowlistSerializer",
    "ContractSerializationError",
    "UnknownFieldError",
    "MissingFieldError",
    "SOURCE_FACT_SERIALIZER",
    "ANALYSIS_STATE_TRANSITION_SERIALIZER",
]
