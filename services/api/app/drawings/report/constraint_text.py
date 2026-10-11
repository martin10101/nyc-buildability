"""Short, structural effect texts for the report's open items (G-6 isolation).

These are the one-line "effect on the answer" phrases the open-items list shows for
a withheld or conditional constraint, moved out of :mod:`.readers` (task M5-T165)
so the document reader stays a general reader. Each text is keyed by the open-item
category and is authored here (it is NOT read from the document, which carries its
own long reason separately).

Every text keeps its 1.4.0 output UNCHANGED except two, corrected in M5-T165:

* ``lot_area`` names the GIS outline "city map outline" (never "tax-map outline";
  a GIS value is never called "tax map", D-094 R2/G-10).
* ``rear_yard`` is reworded as the design contract's OPEN CHECK (D-094 R037, R079;
  NB-03): it names the short-block provision ZR 23-344(b) and the adjoining-side-
  line provision ZR 23-344(c)(3) as not yet checked and draws NO conclusion. The
  earlier "not known beyond the corner area" wording is gone. The law link for
  23-344 is added by the page that shows the uncertainty, not spliced into the text.
"""

from __future__ import annotations

__all__ = ["REAR_YARD_LAW_SECTION", "REAR_YARD_OPEN_CHECK", "effect_for"]

# The constraint effect texts, by open-item category. Authored one-liners; the
# document's own long reason is carried separately by the open item.
_EFFECTS = {
    "lot_area": "The floor-area figures depend on it; the recorded area and the city map outline "
                "disagree.",
    "coverage": "The square-foot coverage figure is withheld.",
    "placement": "Where the building sits on the lot is not worked out.",
    "setback": "The setback above the base is not worked out.",
    "street_wall": "The street wall is not checked.",
    "parking": "Parking, loading and bicycle requirements are not checked.",
}

# The rear-yard open check (D-094 R037, R079; NB-03 revision 2). It states no
# conclusion and names the two provisions that have not been applied to this lot.
REAR_YARD_OPEN_CHECK = (
    "Whether a rear yard is required is not yet checked: the short-block rule ZR 23-344(b) and "
    "the adjoining-side-line rule ZR 23-344(c)(3) have not been applied to this lot."
)

# The single law section the rear-yard open check links to (its sub-paragraphs
# resolve to the same captured section page).
REAR_YARD_LAW_SECTION = "ZR 23-344"


def effect_for(category: str) -> str:
    """The short structural effect text for an open-item category. Returns the
    rear-yard OPEN CHECK for ``rear_yard`` and the fixed 1.4.0 text for every other
    constraint; an unknown category yields ``""`` (no invented text)."""
    if category == "rear_yard":
        return REAR_YARD_OPEN_CHECK
    return _EFFECTS.get(category, "")
