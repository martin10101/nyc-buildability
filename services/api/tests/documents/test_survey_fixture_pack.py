"""Integrity + representativeness tests for the synthetic survey fixture pack (M2-T015).

Two guarantees:

1. **MANIFEST integrity + deterministic round-trip.** Every committed fixture's bytes
   match its recorded ``sha256`` and ``byte_size``; every fixture is labelled
   ``classification: synthetic``; and re-running ``build_fixture_pack.generate_fixtures``
   / ``build_manifest`` regenerates byte-identical fixtures AND a byte-identical
   ``MANIFEST.json`` (no wall-clock in the pack).

2. **Representativeness.** The committed fixtures are exactly the shapes the decoder +
   pipeline tests exercise: the "live" fixtures decode/route through the real pipeline as
   the MANIFEST documents, and the deferred/malicious fixtures behave as documented (raster
   route → DecoderUnavailable; threat vectors → typed S1 rejection; oversize → cap).
   This ties the fixture matrix to executable behavior rather than prose.
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

import app.documents.extraction.routing as routing_module
from app.documents.errors import ExtensionMismatchError, UploadTooLargeError
from app.documents.extraction import survey_pipeline as sp
from app.documents.extraction.routing import SurveyDocumentFormat
from app.documents.extraction.vector_pdf_decoder import VectorPdfDecoder, pdf_decode_refusal
from app.documents.gate import GateLimits, check_extension_matches, sniff_content, stream_gate
from app.documents.isolation import (
    CapabilityProbe,
    IsolationCapability,
    ParsingPermitted,
)
from app.documents.limits import MAX_UPLOAD_BYTES
from app.documents.state import ActorKind, DocumentState, TransitionActor

# The fixture pack is DATA, not an importable package (matching the mappluto_geometry
# convention — no __init__.py in fixtures dirs), so load its builder by file path.
PACK_DIR = Path(__file__).resolve().parent / "fixtures" / "survey_documents"
MANIFEST_PATH = PACK_DIR / "MANIFEST.json"


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "survey_fixture_builder", PACK_DIR / "build_fixture_pack.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


builder = _load_builder()
SUBJECT_BBL = "1002920001"
WHEN = datetime(2026, 8, 9, 12, 0, tzinfo=UTC)
WHEN_ACTOR = TransitionActor(ActorKind.DETERMINISTIC_PIPELINE, actor_id="fixture-pack-test")


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _fixture_bytes(fixture_id: str) -> bytes:
    entry = next(e for e in _manifest()["fixtures"] if e["fixture_id"] == fixture_id)
    return (PACK_DIR / entry["file"]).read_bytes()


# --------------------------------------------------------------- integrity


def test_every_committed_fixture_matches_its_recorded_digest_and_size():
    manifest = _manifest()
    assert manifest["classification"] == "all-synthetic"
    assert manifest["fixtures"], "the pack must not be empty"
    for entry in manifest["fixtures"]:
        path = PACK_DIR / entry["file"]
        assert path.is_file(), f"missing committed fixture {entry['file']}"
        data = path.read_bytes()
        assert entry["classification"] == "synthetic"
        assert entry["byte_size"] == len(data)
        assert entry["sha256"] == "sha256:" + hashlib.sha256(data).hexdigest()


def test_pack_round_trips_byte_identically_through_the_builder():
    # Fixtures regenerate to the exact committed bytes.
    for fx in builder.generate_fixtures():
        committed = (PACK_DIR / fx["file"]).read_bytes()
        assert committed == fx["bytes"], f"{fx['file']} is not reproducible"
    # And the MANIFEST regenerates byte-for-byte (no wall-clock in the pack).
    manifest = builder.build_manifest(builder.generate_fixtures())
    regenerated = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    assert MANIFEST_PATH.read_bytes() == regenerated


def test_manifest_covers_all_twelve_objective_categories():
    categories = {e["category"] for e in _manifest()["fixtures"]}
    assert categories == {
        "digital_pdf",
        "vector_pdf",
        "clean_scan",
        "poor_scan",
        "rotated_pages",
        "mixed_units",
        "decimal_ambiguities",
        "conflicting_dimensions",
        "incomplete_boundaries",
        "multi_page",
        "wrong_address",
        "malicious_oversized",
    }


# --------------------------------------------------------------- isolation seam


def _permitted() -> IsolationCapability:
    return IsolationCapability(
        os_name="Linux",
        kernel_release="0.0-test",
        landlock=CapabilityProbe("landlock", True, "test stub"),
        seccomp=CapabilityProbe("seccomp", True, "test stub"),
        verdict=ParsingPermitted(),
    )


@pytest.fixture
def isolation_permitted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routing_module, "require_isolation", _permitted)


def _context(subject_bbl: str = SUBJECT_BBL) -> sp.SurveyExtractionContext:
    return sp.SurveyExtractionContext(
        document_digest="sha256:" + "cd" * 32,
        target_bbl=SUBJECT_BBL,
        subject_address="123 MAIN ST",
        subject_bbl=subject_bbl,
        extraction_run_id="ser:fixture-pack:run-0001",
        extracted_at="2026-08-09T00:00:00Z",
    )


def _run(fixture_id: str, format_identity: str = "vector_pdf"):
    return sp.run_survey_extraction(
        format_identity=format_identity,
        original_bytes=_fixture_bytes(fixture_id),
        context=_context(),
        actor=WHEN_ACTOR,
        occurred_at=WHEN,
    )


# --------------------------------------------------------------- representativeness (live)


def test_digital_fixture_promotes_to_auto_extracted(isolation_permitted: None):
    outcome = _run("SVY01")
    assert isinstance(outcome, sp.ExtractionCompleted)
    assert outcome.target_state is DocumentState.AUTO_EXTRACTED
    assert {f["fact_type"] for f in outcome.facts} == {"scale_statement", "bbl_text"}


def test_multipage_fixture_decodes_both_pages_and_auto_extracts(isolation_permitted: None):
    outcome = _run("SVY10")
    assert isinstance(outcome, sp.ExtractionCompleted)
    assert outcome.target_state is DocumentState.AUTO_EXTRACTED
    assert {f["fact_type"] for f in outcome.facts} == {"scale_statement", "bbl_text"}
    assert {f["page_number"] for f in outcome.facts} == {1, 2}


def test_conflicting_scale_fixture_fails_closed_to_needs_review(isolation_permitted: None):
    outcome = _run("SVY08")
    assert isinstance(outcome, sp.ExtractionCompleted)
    assert outcome.target_state is DocumentState.NEEDS_REVIEW
    scale_check = next(c for c in outcome.check_results if c.check_name == "scale_consistency")
    assert scale_check.passed is False


def test_wrong_bbl_fixture_routes_to_needs_review(isolation_permitted: None):
    outcome = _run("SVY11")
    assert isinstance(outcome, sp.ExtractionCompleted)
    assert outcome.target_state is DocumentState.NEEDS_REVIEW
    assert outcome.wrong_address is not None
    assert outcome.wrong_address.routing == "needs_review"


def test_rotated_fixture_content_decodes_without_refusal(isolation_permitted: None):
    # Rotation normalization is deferred, but the content stream still decodes.
    outcome = _run("SVY05")
    assert isinstance(outcome, sp.ExtractionCompleted)
    assert outcome.decode_refusal is None


def test_vector_fixtures_decode_into_straight_line_primitives():
    from app.documents.extraction.pdf_content import VectorRect, VectorSegment

    segments_rect = VectorPdfDecoder().decode(_fixture_bytes("SVY02"))
    assert pdf_decode_refusal(segments_rect) is None
    content = segments_rect[0].content
    assert content.segments == (VectorSegment(10.0, 20.0, 110.0, 20.0),)
    assert content.rects == (VectorRect(5.0, 5.0, 40.0, 30.0),)

    incomplete = VectorPdfDecoder().decode(_fixture_bytes("SVY09"))
    assert pdf_decode_refusal(incomplete) is None
    # An open (non-closing) polyline: two straight segments, never silently closed.
    assert incomplete[0].content.segments == (
        VectorSegment(10.0, 10.0, 110.0, 10.0),
        VectorSegment(110.0, 10.0, 110.0, 90.0),
    )


# --------------------------------------------------------------- representativeness (deferred)


@pytest.mark.parametrize("fixture_id", ["SVY03", "SVY04"])
def test_raster_scan_fixtures_route_but_defer_decoding(isolation_permitted: None, fixture_id: str):
    outcome = _run(fixture_id, format_identity="png")
    # PNG is a supported format with no concrete decoder yet → DecoderUnavailable.
    assert isinstance(outcome, sp.DecoderUnavailable)
    assert outcome.route.format is SurveyDocumentFormat.PNG


# --------------------------------------------------------------- representativeness (malicious)


def test_exe_renamed_fixture_is_rejected_by_the_s1_gate():
    sniffed = sniff_content(_fixture_bytes("SVY12"))
    with pytest.raises(ExtensionMismatchError):
        check_extension_matches("pdf", sniffed)


def test_html_renamed_fixture_is_rejected_by_the_s1_gate():
    sniffed = sniff_content(_fixture_bytes("SVY13"))
    with pytest.raises(ExtensionMismatchError):
        check_extension_matches("tiff", sniffed)


def test_oversize_sentinel_documents_the_cap_without_a_50mib_fixture():
    sentinel = _fixture_bytes("SVY14")
    # The committed sentinel is small (thin-client storage policy); the cap boundary is
    # proven in-memory with a tiny injectable limit, never a 50 MiB allocation.
    assert len(sentinel) < MAX_UPLOAD_BYTES
    small = GateLimits(max_upload_bytes=8, sniff_header_bytes=8, stream_chunk_bytes=3)
    with pytest.raises(UploadTooLargeError):
        stream_gate(io.BytesIO(b"x" * 9), small)  # cap + 1 trips the typed rejection
