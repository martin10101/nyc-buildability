"""One transit/parking-zone source, applied identically to every option (queue item
B-10; plan check C-8).

Check C-8 (``docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md`` section D):
"Same rule everywhere | Parking or transit status is applied identically across all
options". The reviewed competitor report fails it: one scenario needs 16 parking spaces
while others claim a transit exemption of 0 spaces (section B, shared-housing rows
58-63). The cause is that each option decided parking for itself.

This module removes that freedom. It reads the lot's transit-zone classification ONCE,
from one official source, and every option reads that one value, so the transit/parking
status cannot differ between options.

The one source is PLUTO's ``transitzone`` field (NYC Open Data dataset ``64uk-42ks``),
already recorded and version-pinned for the benchmark lot (queue item B-01) and assessed
by ``app.profile.data_versions`` (queue item B-06). Per the official PLUTO Data Dictionary
(May 2026, 26v1; ``s-media.nyc.gov/.../bytes/pluto_datadictionary.pdf``, read at G1 -
``docs/research/pluto-mappluto-2026-07-16.md`` section 4.1), ``TrnstZone`` IS DCP's Transit
Zones classification: it is sourced from DCP's Transit Zones data and "determines
residential parking requirements under the Zoning Resolution". Its documented categories
are Manhattan Core, LIC Parking Area, Inner Transit Zone, Outer Transit Zone, and Beyond
the Greater Transit Zone; the current ZR section 12-10 Outer Transit Zone definition
incorporates the 2016 Appendix I area as a component (so this is one transit-zone
geography, not a separate legal basis). The recorded text is passed through verbatim and
never re-interpreted.

What this module does NOT do, by design:

- It does not apply the ZR off-street parking rules to produce the actual parking outcome
  (the number of spaces, or a waiver). That outcome depends on the zoning district, the
  housing type and affordability, and is a zoning-rule / legal determination that belongs
  to the rule engine (Lane A) and a qualified reviewer at G6, never to this data module
  (lane prompt B; platform principle 1: deterministic code calculates, qualified humans
  approve legal interpretations). The transit zone itself is known from PLUTO; only its
  parking OUTCOME waits for the rule engine - the status is "Check needed" for that reason,
  not because the zone is unknown.
- When PLUTO carries no transit-zone value, the authoritative fallback to check is DCP's
  Transit Zones dataset, the source behind PLUTO's field (with its Greater Transit Zone and
  Appendix I Transit Zones components). The face prose (``detail``/``missing_source``) names
  it in readable words only; the exact dataset ids (``6ztr-wgff``, its Greater Transit Zone
  ``vhqf-adkz`` and Appendix I Transit Zones ``dpnc-b2hd`` components), version and link ride
  in the structured ``missing_source_ref`` disclosure, not on the face (owner decision
  D-090-R095; request D-2). Those ids remain research facts recorded in
  ``docs/research/zoning-features-ztldb-2026-07-16.md`` with no registered connector in this
  repository yet.

When PLUTO records no transit-zone value for the lot (SODA omits null fields, so an
absent column means "none or unknown", never a guess) or the value cannot be trusted (an
identity conflict, a connector drift signal, a data conflict, a duplicate), the status is
"Check needed" naming the missing source, never a silent default (lane prompt B; D-051:
no silent default direction).

There is no site_fact or results contract slot for a transit/parking value yet, so the
status is a plain record here. Wiring it into the study and the contract so every option
reads it is a Lane C request (``docs/lanes/requests/B-2.md``), as B-06 and B-09 did.

Pure, deterministic code: no I/O, no clock, no legal logic. The profile is never changed.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from app.profile.site_facts import PLUTO_DATASET_NAME, read_pluto_text

__all__ = [
    "PLUTO_DATASET_NAME",
    "STATUS_CHECK_NEEDED",
    "STATUS_RECORDED",
    "TRANSIT_ZONE_FIELD",
    "TransitParkingStatus",
    "applied_to_options",
    "resolve_transit_parking_status",
]

# The one PLUTO column that carries the lot's transit-zone classification.
TRANSIT_ZONE_FIELD = "transitzone"

STATUS_RECORDED = "recorded"
STATUS_CHECK_NEEDED = "check_needed"
# "Check needed" is the plan section 8a wording, copied exactly.
CHECK_NEEDED_LABEL = "Check needed"
RECORDED_LABEL = "Recorded"

# The authoritative source behind PLUTO's transitzone field, NAMED in readable words only (no
# technical id) on the face when PLUTO carries no value. The exact id, version and link move to
# MISSING_TRANSIT_ZONE_SOURCE_REF below, so a reader sees a readable name and the id lives in
# the structured Source disclosure (owner decision D-090-R095; request D-2). Recorded in
# research, no registered connector yet.
_TRANSIT_ZONE_SOURCE_NAME = (
    "DCP Transit Zones (NYC Open Data), the dataset PLUTO's transitzone field is sourced from"
)
MISSING_TRANSIT_ZONE_SOURCE = (
    f"{_TRANSIT_ZONE_SOURCE_NAME}; recorded in research, no registered connector in "
    "this repository"
)

# The exact transit-zone source identifiers, version and link behind MISSING_TRANSIT_ZONE_SOURCE,
# emitted as ``missing_source_ref`` only when ``check_needed`` (the structured Source disclosure
# D-090-R095 keeps off the face). ``dataset_version`` is None because no connector or version
# probe exists for this dataset ("where available" = not here). The ``6ztr-wgff`` id, its
# ``vhqf-adkz`` Greater Transit Zone and ``dpnc-b2hd`` Appendix I components are research facts in
# docs/research/zoning-features-ztldb-2026-07-16.md, verified 2026-10-03 against
# data.cityofnewyork.us/api/views/<id>.json (name, id, attribution only).
MISSING_TRANSIT_ZONE_SOURCE_REF: dict = {
    "dataset": "Transit Zones",
    "dataset_id": "6ztr-wgff",
    "publisher": "Department of City Planning (DCP)",
    "dataset_version": None,
    "url": "https://data.cityofnewyork.us/d/6ztr-wgff",
    "components": [
        {"dataset": "Greater Transit Zone", "dataset_id": "vhqf-adkz"},
        {"dataset": "Appendix I - Transit Zones", "dataset_id": "dpnc-b2hd"},
    ],
}
# The legal boundary this data module never crosses (platform principle 1; lane prompt B):
# the zone is known; applying the parking rules to it is the rule engine's job.
_PARKING_RULE_CAVEAT = (
    "Applying the Zoning Resolution off-street parking rules to this zone (by district, "
    "housing type and affordability) is a rule-engine / legal determination, confirmed by a "
    "qualified reviewer at G6, that this data layer never makes."
)


@dataclass(frozen=True)
class TransitParkingStatus:
    """The lot's transit/parking status from the one official source, for every option.

    Attributes:
        lot_bbl: the tax lot (10-digit BBL).
        status: ``recorded`` (PLUTO has a usable transit-zone value) or ``check_needed``
            (no usable value; the reason is in ``detail``).
        transit_zone: the verbatim PLUTO ``transitzone`` text (for example "Outer Transit
            Zone"), or None when ``check_needed``.
        source: a site_fact ``city_dataset`` source for PLUTO (dataset, dataset version,
            retrieved_at, query_ref, provenance_refs), or the checked source when no
            value was found. ``app.profile.data_versions`` pins it (queue item B-06), so
            the status carries "Out of date" / "Version unknown" like any sourced value.
        detail: the one line shown beside every option (plan section 5a). It states the
            legal boundary (the zone is DCP's classification; applying the ZR parking
            rules to it is the rule engine's job, not this layer's).
        missing_source: the source behind the field to check when ``check_needed``, named in
            readable words only (DCP Transit Zones); None when ``recorded``. The exact id,
            version and link live in ``missing_source_ref``, not here (owner decision
            D-090-R095; request D-2).
        missing_source_ref: the structured Source disclosure for the missing source when
            ``check_needed`` - exact ``dataset_id``, ``publisher``, ``dataset_version`` (None
            when no version probe exists), ``url`` and the component datasets; None when
            ``recorded``. The technical ids live here, off the face (D-090-R095; request D-2).
    """

    lot_bbl: str
    status: str
    transit_zone: str | None
    source: dict | None
    detail: str
    missing_source: str | None = None
    missing_source_ref: dict | None = None

    def __post_init__(self) -> None:
        if self.status not in (STATUS_RECORDED, STATUS_CHECK_NEEDED):
            raise ValueError(
                f"unknown transit/parking status {self.status!r}; expected "
                f"{STATUS_RECORDED!r} or {STATUS_CHECK_NEEDED!r}"
            )

    @property
    def needs_check(self) -> bool:
        return self.status == STATUS_CHECK_NEEDED

    @property
    def status_label(self) -> str:
        return CHECK_NEEDED_LABEL if self.needs_check else RECORDED_LABEL

    def to_dict(self) -> dict:
        return {
            "lot_bbl": self.lot_bbl,
            "status": self.status,
            "status_label": self.status_label,
            "transit_zone": self.transit_zone,
            "source": self.source,
            "detail": self.detail,
            "missing_source": self.missing_source,
            "missing_source_ref": self.missing_source_ref,
        }


def _bbl(profile: Mapping[str, Any]) -> str:
    identity = profile.get("identity") if isinstance(profile, Mapping) else None
    bbl = identity.get("bbl") if isinstance(identity, Mapping) else None
    if not isinstance(bbl, str) or not bbl.strip():
        raise ValueError("the property profile has no identity.bbl")
    return bbl


def resolve_transit_parking_status(profile: Mapping[str, Any]) -> TransitParkingStatus:
    """The lot's transit/parking status from PLUTO's one ``transitzone`` field.

    Args:
        profile: a document built by ``app.profile.builder.build_property_profile``.
            It is read, never changed.

    Returns:
        A :class:`TransitParkingStatus`. ``recorded`` carries PLUTO's transit-zone
        classification; ``check_needed`` names the missing or untrusted source. Neither
        states a parking requirement - that is a legal determination made elsewhere
        (module docstring).

    Raises:
        ValueError: the profile has no ``identity.bbl``.
    """
    value, source, problem = read_pluto_text(profile, TRANSIT_ZONE_FIELD)
    bbl = _bbl(profile)
    if problem is None and value is not None:
        # The parenthesis names the dataset by name only ("PLUTO"), not its id: the
        # dataset id, version and query_ref are provenance and stay in ``source`` below,
        # off the face the parity window shows (request D-2; plan section 5a items 4-5).
        detail = (
            f"Transit zone: {value} (PLUTO, field '{TRANSIT_ZONE_FIELD}', "
            f"DCP's Transit Zones classification per the PLUTO Data Dictionary 26v1). "
            f"Every option reads this one recorded value, so the transit/parking status "
            f"is the same across all options (check C-8). "
            f"{_PARKING_RULE_CAVEAT}"
        )
        return TransitParkingStatus(
            lot_bbl=bbl,
            status=STATUS_RECORDED,
            transit_zone=value,
            source=source,
            detail=detail,
        )
    reason = problem or f"PLUTO records no '{TRANSIT_ZONE_FIELD}' value for this lot."
    # The face names the source in readable words only; the exact id, version and link move to
    # ``missing_source_ref`` (owner decision D-090-R095; request D-2 part 2).
    detail = (
        f"Transit/parking status: {CHECK_NEEDED_LABEL}. {reason} "
        f"Transit-zone source to check: {_TRANSIT_ZONE_SOURCE_NAME}. "
        f"{_PARKING_RULE_CAVEAT}"
    )
    return TransitParkingStatus(
        lot_bbl=bbl,
        status=STATUS_CHECK_NEEDED,
        transit_zone=None,
        source=source,
        detail=detail,
        missing_source=MISSING_TRANSIT_ZONE_SOURCE,
        missing_source_ref=copy.deepcopy(MISSING_TRANSIT_ZONE_SOURCE_REF),
    )


def applied_to_options(
    status: TransitParkingStatus, option_ids: Sequence[str]
) -> dict[str, dict]:
    """The SAME transit/parking status for every option (check C-8: one source applied
    identically).

    Each option id maps to a copy of the one status dict, so no option can carry a
    different transit or parking status. Options read this; they never re-derive it.

    Args:
        status: the single lot status from :func:`resolve_transit_parking_status`.
        option_ids: the study's option ids.

    Returns:
        ``{option_id: status.to_dict()}`` - the same value for every id.

    Raises:
        ValueError: an option id is blank or repeated.
    """
    ids = tuple(option_ids)
    for option_id in ids:
        if not isinstance(option_id, str) or not option_id.strip():
            raise ValueError(f"option ids must be non-empty text, got {option_id!r}")
    if len(set(ids)) != len(ids):
        raise ValueError("option ids must be unique")
    shared = status.to_dict()
    return {option_id: dict(shared) for option_id in ids}
