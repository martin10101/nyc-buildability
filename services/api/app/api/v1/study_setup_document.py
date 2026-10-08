"""Shared study_setup document builder (task M5-T138).

Extracted VERBATIM from ``app.api.v1.study_read._build_document`` so BOTH the study-read
route (``GET /api/v1/properties/{bbl}/study``) and the new results route
(``POST /api/v1/properties/{bbl}/results``) shape the study-setup document ONE way, never a
fork (modularity law; the R6B work order Part A note "the study-read builder is extracted to
the shared module"). The behaviour is byte-identical to the former private builder: lots and
lot_selection come VERBATIM from B-07's study adapters, the site facts are carried as emitted by
B-02, and NOTHING is computed here.

The results route turns this study-setup document into a full ``study`` with one explicit option
(``app.contracts.study_setup_bridge.study_from_study_setup``); the study-read route contract-guards
and returns it. Pure, offline, library-only: no network, no route wiring, no mutation of the input.
"""

from __future__ import annotations

from app.spatial.multi_lot_site import study_lot_selection, study_lots

from .study_inputs import StudyInputs

__all__ = ["DOCUMENT_KIND", "build_study_setup_document"]

#: The document_kind every study_setup document carries (the study-read contract marker).
DOCUMENT_KIND = "study_setup"


def build_study_setup_document(canonical_bbl: str, inputs: StudyInputs) -> dict:
    """Shape the study-setup document from the domain inputs. Lots and lot_selection come
    VERBATIM from B-07's adapters; the facts are carried as emitted by B-02. Nothing is
    computed here."""
    lots = study_lots(inputs.lot_choice, inputs.site.selected_bbls)
    lot_selection = study_lot_selection(inputs.site)
    facts = [dict(fact) for fact in inputs.site_facts]
    return {
        "document_kind": DOCUMENT_KIND,
        "bbl": canonical_bbl,
        "property": {"bbl": canonical_bbl, "address": inputs.address},
        "lots": lots,
        "lot_selection": lot_selection,
        "site": {"facts": facts},
    }
