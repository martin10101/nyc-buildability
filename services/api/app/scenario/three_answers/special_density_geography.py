"""The special density area read from the city's record (ZR 12-10; task M5-T157, DB-231).

A PURE fold rule: given a lot's recorded community district, borough code and special-purpose-
district tokens, decide whether the lot IS in a special density area, is NOT in one, or is NOT
KNOWN. It computes NO zoning number and reads no file; the fact-gathering step reads the PLUTO
columns and classifies them, this module folds them against the ZR 12-10 definitions it holds with
their capture ids and digests, and the decision step drives both the shown way and the engine
condition from the ONE decision it returns. This module imports nothing from the scenario decision
step (it is a leaf the fact-gathering step imports), so no import-guard list grows for it.

THE LAW (ZR 12-10, captured under docs/research/zr-snapshots/v1/; the engine's copy under
services/api/app/_zr_snapshots/v1/):

* "Special density areas" shall include (a) the Manhattan Core; and (b) the Special Downtown
  Brooklyn District (snapshot zr-12-10-special-density-areas).
* The "Manhattan Core" is the area within Manhattan Community Districts 1, 2, 3, 4, 5, 6, 7 and 8
  (snapshot zr-12-10-manhattan-core).
* The "Special Downtown Brooklyn District" is a Special Purpose District designated by the letters
  "DB" (snapshot zr-12-10-special-downtown-brooklyn-district).

HOW THE RECORD MAPS TO THE LAW (verified against repository evidence):

* Community district coding - the PLUTO ``cd`` field "consists of three digits, the first of which
  is the borough code ... The second and third digits are the community district or joint interest
  area number" (PLUTO data dictionary, fixture
  ``services/api/tests/fixtures/pluto/F08_api_views_columns_snapshot.json``). Manhattan Community
  Districts 1-8 are therefore the codes 101-108. The two independent R6B readings read the Queens
  benchmark lot (``cd`` 411, borough code 4) as NOT in the Manhattan Core
  (docs/reference-cases/R6B/cases/step-p3-worked.json row manhattan-core).
* "DB" - the ZR 12-10 definition names the Special Downtown Brooklyn District by the zoning-map
  letters "DB", and PLUTO's special-purpose-district columns carry a district's designation letters
  (dictionary field ``spdist1``; the independent reading used the same "DB" letters,
  step-p3-worked.json row special-downtown-brooklyn-district). The EXACT PLUTO spelling of this
  district's token is NOT confirmed from captured repository evidence: PLUTO Appendix A (the list of
  valid special-purpose-district values) is not captured (open question OQ-5), so the match is to
  the ZR map-designation letters and the dictionary's token semantics only. G1 probes it.

NO DEFAULT STANDS FOR A FACT. "Not read" is never "no": a column that was not read, a value the
trust rules reject, a joint interest area (a park/airport, not a community district), an
unrecognised code, or a Manhattan Core code contradicted by a non-Manhattan borough code is NOT
KNOWN - never read as "not in one". Either IN signal alone (a Manhattan Core community district, or
a recorded "DB" special district) is enough; NOT IN needs both the Manhattan Core question answered
no AND every special-district column read with none "DB".
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = [
    "JOINT_INTEREST_AREA_CDS",
    "MANHATTAN_BOROUGH_CODE",
    "MANHATTAN_CORE_COMMUNITY_DISTRICTS",
    "MAX_COMMUNITY_DISTRICT_NUMBER",
    "MANHATTAN_CORE",
    "SPECIAL_DENSITY_AREAS",
    "SPECIAL_DOWNTOWN_BROOKLYN_DISTRICT",
    "SPECIAL_DOWNTOWN_BROOKLYN_TOKEN",
    "LawCapture",
    "SpecialDensityArea",
    "SpecialDensityInputs",
    "SpecialDensityDecision",
    "decide_special_density",
]


@dataclass(frozen=True)
class LawCapture:
    """One ZR 12-10 capture this fold rests on: the section, the pinned snapshot id, the content
    digest of the captured text, and the captured words. These are the ONLY law constants here;
    the module derives no number and no boundary from them."""

    zr_section: str
    capture_snapshot_id: str
    capture_content_digest: str
    captured_words: str


# ZR 12-10 definitions. The digests are each snapshot's ``content_digest_sha256`` (the register
# cites the same digests); the words are the verbatim excerpts.
SPECIAL_DENSITY_AREAS = LawCapture(
    zr_section="ZR 12-10",
    capture_snapshot_id="zr-12-10-special-density-areas",
    capture_content_digest="e8029ab3bcc628ef68098a954a357af86ae5e66040f8b53d9e142a35c7f401b6",
    captured_words=(
        "“Special density areas” shall refer to special geographies where unique density "
        "regulations apply to #residential# #developments# or #enlargements#. #Special density "
        "areas# shall include:\n\n(a) the #Manhattan Core#; and\n\n(b) the #Special Downtown "
        "Brooklyn District#."
    ),
)
MANHATTAN_CORE = LawCapture(
    zr_section="ZR 12-10",
    capture_snapshot_id="zr-12-10-manhattan-core",
    capture_content_digest="2c04132a96a435146c01f3c0a0578ea26520b10c2c5d1a894470ba8a47c59c56",
    captured_words=(
        "The \"Manhattan Core\" is the area within Manhattan Community Districts 1, 2, 3, 4, 5, 6, "
        "7 and 8."
    ),
)
SPECIAL_DOWNTOWN_BROOKLYN_DISTRICT = LawCapture(
    zr_section="ZR 12-10",
    capture_snapshot_id="zr-12-10-special-downtown-brooklyn-district",
    capture_content_digest="ae66c93e8ec466de81587358a332c40c15fd500fc4f34ae4102c11ab43d7dd2d",
    captured_words=(
        "The \"Special Downtown Brooklyn District\" is a Special Purpose District designated by "
        "the letters \"DB\" in which special regulations set forth in Article X, Chapter 1, apply."
    ),
)

#: Manhattan Community Districts 1-8, coded 101-108 (ZR 12-10 Manhattan Core; PLUTO ``cd`` coding:
#: first digit = borough code 1 = Manhattan, last two digits = the community district number).
MANHATTAN_CORE_COMMUNITY_DISTRICTS = frozenset(range(101, 109))
#: The borough code for Manhattan (PLUTO ``borocode``; the F08 dictionary gives Marble Hill, legally
#: Manhattan, borough code 1). A Manhattan Core code with a non-Manhattan borough code is a
#: contradiction and is read as NOT KNOWN.
MANHATTAN_BOROUGH_CODE = 1
#: The letters that designate the Special Downtown Brooklyn District (ZR 12-10). See the module
#: docstring for the limit on the PLUTO-spelling verification.
SPECIAL_DOWNTOWN_BROOKLYN_TOKEN = "DB"
#: The joint interest areas (large parks and airports) PLUTO lists in the ``cd`` field; the F08
#: dictionary says they "are not considered part of any community district", so a lot whose ``cd``
#: is a joint interest area cannot answer the Manhattan Core question and is read as NOT KNOWN.
JOINT_INTEREST_AREA_CDS = frozenset(
    {164, 226, 227, 228, 355, 356, 480, 481, 482, 483, 484, 595}
)
#: The largest community-district number across the five boroughs (Brooklyn's 18). A ``cd`` whose
#: first digit is a borough code (1-5) and whose last two digits fall in 1..18, and which is not a
#: joint interest area, is read as a recognised community-district code; any other value is
#: unrecognised and read as NOT KNOWN. (The 59 community districts total is from the F08 dictionary;
#: the per-borough counts are administrative geography, to be confirmed by G1, never a zoning rule.)
MAX_COMMUNITY_DISTRICT_NUMBER = 18


class SpecialDensityArea(Enum):
    """The ONE decision the record yields about the special density area (ZR 12-10)."""

    IN_SPECIAL_DENSITY_AREA = "in_special_density_area"
    NOT_IN_SPECIAL_DENSITY_AREA = "not_in_special_density_area"
    NOT_KNOWN = "not_known"


class _Core(Enum):
    """Whether the lot is in the Manhattan Core (ZR 12-10), from the recorded community district."""

    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SpecialDensityInputs:
    """The classified record the fold reads. ``community_district`` and ``borough_code`` are the
    usable integer values, or None when the column was not read, was rejected by the trust rules,
    or did not serve an integer. ``special_district_tokens`` holds the upper-cased tokens from every
    special-purpose-district column that served a value (each value already split on "/");
    ``all_special_district_columns_read`` is True only when NO special-district column was
    not-read / untrusted (so "none DB" is a real absence, never a missing reading)."""

    community_district: int | None
    borough_code: int | None
    special_district_tokens: tuple[str, ...]
    all_special_district_columns_read: bool


@dataclass(frozen=True)
class SpecialDensityDecision:
    """The fold's result: the ``area`` decision and a plain ``reason`` naming the signal that
    decided it (for the recorded fact and the report; never a claim about the law for a lot)."""

    area: SpecialDensityArea
    reason: str


def _is_recognised_community_district(cd: int) -> bool:
    """True when ``cd`` is a syntactically recognised community-district code: a three-digit value
    whose first digit is a borough code (1-5) and whose last two digits are a community-district
    number (1..18), and which is not a joint interest area. A joint interest area, or any other
    value, is not a community district."""
    if cd in JOINT_INTEREST_AREA_CDS:
        return False
    borough = cd // 100
    number = cd % 100
    return 1 <= borough <= 5 and 1 <= number <= MAX_COMMUNITY_DISTRICT_NUMBER


def _manhattan_core(community_district: int | None, borough_code: int | None) -> _Core:
    """Whether the lot is in the Manhattan Core (ZR 12-10), from the recorded community district and
    borough code. YES for a code 101-108 (unless a non-Manhattan borough code contradicts it); NO
    for any other recognised community-district code; UNKNOWN when the code is not usable, is a
    joint interest area, is unrecognised, or is a Manhattan Core code with a non-Manhattan
    borough code."""
    if community_district is None or not _is_recognised_community_district(community_district):
        return _Core.UNKNOWN
    if community_district in MANHATTAN_CORE_COMMUNITY_DISTRICTS:
        if borough_code is not None and borough_code != MANHATTAN_BOROUGH_CODE:
            return _Core.UNKNOWN
        return _Core.YES
    return _Core.NO


def decide_special_density(inputs: SpecialDensityInputs) -> SpecialDensityDecision:
    """Fold the classified record into the ONE special-density decision (ZR 12-10).

    Either IN signal alone is enough: a recorded "DB" special district, or a Manhattan Core
    community district. NOT IN needs the Manhattan Core question answered no AND every
    special-district column read with none "DB". Everything else (a code not usable for the
    Manhattan Core test, or the special-district columns not fully read) is NOT KNOWN; a column that
    was not read is never read as "no"."""
    if SPECIAL_DOWNTOWN_BROOKLYN_TOKEN in inputs.special_district_tokens:
        return SpecialDensityDecision(
            SpecialDensityArea.IN_SPECIAL_DENSITY_AREA,
            "City records record a Special Downtown Brooklyn District (\"DB\") for this lot.",
        )
    core = _manhattan_core(inputs.community_district, inputs.borough_code)
    if core is _Core.YES:
        return SpecialDensityDecision(
            SpecialDensityArea.IN_SPECIAL_DENSITY_AREA,
            "City records place this lot in a Manhattan Core community district (1-8).",
        )
    if core is _Core.UNKNOWN:
        return SpecialDensityDecision(
            SpecialDensityArea.NOT_KNOWN,
            "The recorded community district cannot be read for the Manhattan Core test, so "
            "whether this lot is in a special density area is not known.",
        )
    if inputs.all_special_district_columns_read:
        return SpecialDensityDecision(
            SpecialDensityArea.NOT_IN_SPECIAL_DENSITY_AREA,
            "City records place this lot outside the Manhattan Core and record no Special Downtown "
            "Brooklyn District for it.",
        )
    return SpecialDensityDecision(
        SpecialDensityArea.NOT_KNOWN,
        "The special-purpose-district record was not fully read, so whether this lot is in a "
        "special density area is not known.",
    )
