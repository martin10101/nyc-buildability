"""Site-definition confirmation package (task M5-T059, D-078).

Typed, append-only :class:`SiteDefinitionConfirmation` records with an abstract
store and an in-memory (CI/local, B-001-deferred) implementation. This is RECORD
SUBSTRATE ONLY: no calculation path reads a confirmation and the system never
selects a site definition - a confirmation is a recorded human act (D-078-R002).
Identity is self-attested (B-001) and persistence is ephemeral; both limits are
LOUD and typed. See :mod:`app.site_definition.records` and
:mod:`app.site_definition.store`.
"""

from __future__ import annotations

from app.site_definition.records import (
    SITE_DEFINITION_STATUS_CONFIRMED,
    SITE_DEFINITION_STATUS_UNCONFIRMED,
    AttestationStatus,
    ConfirmationNotActiveError,
    ConfirmationNotFoundError,
    ConfirmationStatus,
    ConfirmationView,
    ConfirmerRole,
    DuplicateActiveConfirmationError,
    InvalidConfirmerError,
    OrphanSupersedeError,
    ParcelSetMismatchError,
    ResolutionProvenanceSnapshot,
    SiteConfirmer,
    SiteDefinitionConfirmation,
    SiteDefinitionError,
    StatusTransition,
    TransitionReasonRequiredError,
    build_site_definition_block,
    create_confirmation,
    make_confirmer,
    normalize_parcels,
)
from app.site_definition.store import (
    InMemorySiteDefinitionStore,
    SiteDefinitionStore,
    default_site_definition_store,
)

__all__ = [
    "SITE_DEFINITION_STATUS_CONFIRMED",
    "SITE_DEFINITION_STATUS_UNCONFIRMED",
    "AttestationStatus",
    "ConfirmationNotActiveError",
    "ConfirmationNotFoundError",
    "ConfirmationStatus",
    "ConfirmationView",
    "ConfirmerRole",
    "DuplicateActiveConfirmationError",
    "InMemorySiteDefinitionStore",
    "InvalidConfirmerError",
    "OrphanSupersedeError",
    "ParcelSetMismatchError",
    "ResolutionProvenanceSnapshot",
    "SiteConfirmer",
    "SiteDefinitionConfirmation",
    "SiteDefinitionError",
    "SiteDefinitionStore",
    "StatusTransition",
    "TransitionReasonRequiredError",
    "build_site_definition_block",
    "create_confirmation",
    "default_site_definition_store",
    "make_confirmer",
    "normalize_parcels",
]
