"""Condo billing-BBL -> base-lot resolution SEAM POLICY (task M5-T045).

Transport and the raw resolver live in :mod:`app.connectors.dtm_condo_soda`
(a leaf). This module is the thin POLICY seam that live consumers call BEFORE
the zoning-lot lookup. It does exactly three things and nothing else:

1. classify whether an input BBL is condo-BILLING class (lot 7501-7599, the
   real user-entry class per the DB-002 research);
2. invoke the accepted resolver for a billing BBL; and
3. collapse the resolver's richer :class:`~app.connectors.dtm_condo_soda.CondoBaseLotResult`
   into ONE typed, fail-closed :class:`CondoResolution` outcome a consumer can
   branch on without re-implementing the resolver's contract.

Outcomes (typed, exhaustive):

- :data:`OUTCOME_NOT_CONDO_BILLING` - the input is not a condo billing BBL
  (lot outside 7501-7599, or not a well-formed 10-digit BBL). PASS-THROUGH:
  the consumer runs its existing pipeline on the input BBL unchanged, byte for
  byte, and this seam performs ZERO network I/O (classification is pure). Unit
  BBLs (1001-6999) are deliberately pass-through here: the live entry class is
  the billing BBL; a unit-BBL entry path is a later increment and the resolver
  already carries the unit path for it.
- :data:`OUTCOME_RESOLVED_SINGLE` - the billing BBL resolves to EXACTLY ONE
  base land lot. The consumer runs the pipeline on that BASE lot and records
  the resolution with provenance.
- :data:`OUTCOME_MULTI_LOT` - the billing BBL resolves to TWO OR MORE base
  lots. FAIL-SAFE: the consumer must NOT pick one and must NOT collapse
  divergent zoning; the base lots are presented as RECORDS only, never as a
  computed allowance (D-073-R006).
- :data:`OUTCOME_UNRESOLVED` - a well-formed condo billing BBL that matched no
  data / whose fallbacks were exhausted. FAIL-SAFE, honest no-result.
- :data:`OUTCOME_ERROR` - a typed transport failure (rate-limit / timeout /
  unavailable / schema drift). FAIL-SAFE; carries the typed ``error_type``.

Every outcome carries the resolution provenance the consumer needs to record
WHY (source id, dataset ids, retrieved_at, condo_key, condo_number, the full
base-lot set, the resolver notes, the divergent-zoning boundary notice). This
module makes NO zoning determination and NEVER collapses a multi-lot set - the
same permanent boundary the underlying resolver carries.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.connectors.bbl import BBLValidationError
from app.connectors.dtm_condo_soda import (
    CONDO_DATASET_ID,
    DIVERGENT_ZONING_NOTICE,
    LOT_CLASS_BILLING,
    SOURCE_ID,
    STATUS_NOT_A_CONDO,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
    CondoBaseLotResult,
    DtmCondoConnectorError,
    classify_lot,
)
from app.connectors.dtm_condo_soda import (
    resolve as _dtm_resolve,
)

__all__ = [
    "OUTCOME_ERROR",
    "OUTCOME_MULTI_LOT",
    "OUTCOME_NOT_CONDO_BILLING",
    "OUTCOME_RESOLVED_SINGLE",
    "OUTCOME_UNRESOLVED",
    "CondoResolution",
    "resolve_condo_billing",
]

# --- Outcome vocabulary ----------------------------------------------------
OUTCOME_NOT_CONDO_BILLING = "not_condo_billing"
OUTCOME_RESOLVED_SINGLE = "resolved_single_base_lot"
OUTCOME_MULTI_LOT = "multi_lot_set"
OUTCOME_UNRESOLVED = "unresolved"
OUTCOME_ERROR = "error"

# The seam's own source id equals the connector's; the resolution provenance is
# attributed to the DOF Digital Tax Map condo channel (source-registry record
# docs/research/source-registry-drafts/dtm-condo.json, DB-029b).
CONDO_SOURCE_ID = SOURCE_ID


@dataclass(frozen=True)
class CondoResolution:
    """One typed, fail-closed condo-billing resolution outcome.

    ``base_bbls`` is the FULL SET of resolved base tax lots (sorted,
    deduplicated) and is populated for both :data:`OUTCOME_RESOLVED_SINGLE`
    (one lot) and :data:`OUTCOME_MULTI_LOT` (two or more); it is never
    collapsed. ``resolved_base_bbl`` is the single substrate lot and is set
    ONLY for :data:`OUTCOME_RESOLVED_SINGLE` - a multi-lot outcome deliberately
    exposes no single substitute lot, so a consumer physically cannot pick one.

    ``provenance`` is the resolver's provenance list verbatim (one entry per
    SODA query performed). ``error_type`` is the typed connector error class
    only on :data:`OUTCOME_ERROR`.
    """

    outcome: str
    input_bbl: str
    correlation_id: str
    base_bbls: tuple[str, ...] = ()
    resolved_base_bbl: str | None = None
    condo_key: str | None = None
    condo_number: str | None = None
    resolution_path: str | None = None
    source_id: str | None = None
    dataset_ids: tuple[str, ...] = ()
    retrieved_at: str | None = None
    provenance: tuple[dict, ...] = ()
    error_type: str | None = None
    divergent_zoning_notice: str | None = None
    notes: tuple[str, ...] = ()

    @property
    def is_pass_through(self) -> bool:
        """True when the consumer should run its EXISTING pipeline unchanged on
        the input BBL (the condo step is a no-op)."""
        return self.outcome == OUTCOME_NOT_CONDO_BILLING

    @property
    def substitutes_base_lot(self) -> bool:
        """True only when a single base lot should replace the input BBL as the
        substrate for the zoning-lot lookup."""
        return self.outcome == OUTCOME_RESOLVED_SINGLE

    @property
    def is_fail_safe(self) -> bool:
        """True when the consumer must fail SAFE (no substrate, professional
        review) rather than proceed: multi-lot, unresolved, or a typed error.
        Never fabricate a substrate and never collapse divergent zoning."""
        return self.outcome in (
            OUTCOME_MULTI_LOT,
            OUTCOME_UNRESOLVED,
            OUTCOME_ERROR,
        )


# Injectable resolver seam (tests pass a double; the default is the accepted
# leaf resolver). Signature mirrors ``dtm_condo_soda.resolve``'s keyword call.
CondoResolver = Callable[..., CondoBaseLotResult]


def resolve_condo_billing(
    bbl: str,
    *,
    correlation_id: str,
    resolver: CondoResolver = _dtm_resolve,
    **resolver_kwargs: object,
) -> CondoResolution:
    """Classify ``bbl`` and, if it is a condo BILLING BBL, resolve it to a
    typed :class:`CondoResolution` outcome. Fail-closed throughout: a non
    billing BBL (or a malformed one) is an honest pass-through with zero
    network I/O; a typed transport failure becomes :data:`OUTCOME_ERROR`; a
    well-formed billing BBL that matches nothing becomes
    :data:`OUTCOME_UNRESOLVED`. Never raises for a routine miss and never
    fabricates a base lot.
    """
    try:
        lot_class = classify_lot(bbl)
    except BBLValidationError:
        # Not a well-formed 10-digit BBL: not our class. Pass through so the
        # existing pipeline handles (and itself fail-closes on) the input,
        # keeping non-condo behavior byte-identical. Zero network I/O.
        return _pass_through(
            bbl,
            correlation_id,
            "input is not a well-formed 10-digit BBL; condo step skipped "
            "(pass-through, zero lookups).",
        )

    if lot_class != LOT_CLASS_BILLING:
        return _pass_through(
            bbl,
            correlation_id,
            f"lot class {lot_class!r} is not condo-billing (7501-7599); condo "
            "step skipped (pass-through, zero lookups).",
        )

    try:
        result = resolver(bbl, correlation_id=correlation_id, **resolver_kwargs)
    except DtmCondoConnectorError as exc:
        return CondoResolution(
            outcome=OUTCOME_ERROR,
            input_bbl=bbl,
            correlation_id=correlation_id,
            source_id=CONDO_SOURCE_ID,
            error_type=exc.error_type,
            notes=(
                "condo base-lot resolution failed with a typed transport error; "
                "the consumer must fail safe to professional review (never a "
                "fabricated base lot).",
            ),
        )

    return _from_result(bbl, correlation_id, result)


def _pass_through(bbl: str, correlation_id: str, note: str) -> CondoResolution:
    return CondoResolution(
        outcome=OUTCOME_NOT_CONDO_BILLING,
        input_bbl=bbl,
        correlation_id=correlation_id,
        notes=(note,),
    )


def _from_result(
    bbl: str, correlation_id: str, result: CondoBaseLotResult
) -> CondoResolution:
    """Map a resolver :class:`CondoBaseLotResult` onto the typed seam outcome."""
    dataset_ids = tuple(
        dict.fromkeys(
            entry.get("dataset_id")
            for entry in result.provenance
            if entry.get("dataset_id")
        )
    ) or (CONDO_DATASET_ID,)
    common = {
        "input_bbl": bbl,
        "correlation_id": correlation_id,
        "condo_key": result.condo_key,
        "condo_number": result.condo_number,
        "resolution_path": result.resolution_path,
        "source_id": CONDO_SOURCE_ID,
        "dataset_ids": dataset_ids,
        "retrieved_at": result.retrieved_at,
        "provenance": tuple(result.provenance),
        "divergent_zoning_notice": DIVERGENT_ZONING_NOTICE,
        "notes": tuple(result.notes),
    }

    if result.status == STATUS_RESOLVED:
        base_bbls = tuple(result.base_bbls)
        if len(base_bbls) == 1:
            return CondoResolution(
                outcome=OUTCOME_RESOLVED_SINGLE,
                base_bbls=base_bbls,
                resolved_base_bbl=base_bbls[0],
                **common,
            )
        # Two or more base lots: multi-lot records, never a single substrate.
        return CondoResolution(
            outcome=OUTCOME_MULTI_LOT,
            base_bbls=base_bbls,
            resolved_base_bbl=None,
            **common,
        )

    if result.status == STATUS_UNRESOLVED:
        return CondoResolution(
            outcome=OUTCOME_UNRESOLVED,
            **common,
        )

    # STATUS_NOT_A_CONDO cannot arise for a billing-class input, but map it to a
    # pass-through defensively rather than inventing a branch.
    if result.status == STATUS_NOT_A_CONDO:
        return _pass_through(
            bbl,
            correlation_id,
            "resolver classified the input as not-a-condo; pass-through.",
        )

    # Any unknown status is treated as fail-safe unresolved, never as success.
    return CondoResolution(outcome=OUTCOME_UNRESOLVED, **common)
