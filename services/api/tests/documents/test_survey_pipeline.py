"""End-to-end tests for the deterministic survey-extraction pipeline (M2-T015 unit 3k).

Exercises the whole composed flow — upload bytes -> route -> isolate -> decode ->
assemble facts -> deterministic checks -> per-fact promotion -> gated state
transition — against synthetic in-repo PDFs, and proves the fail-closed doctrine
structurally:

- SB-S1: a digitally-authored vector/embedded-text PDF whose facts all validate and
  pass every check promotes to ``auto_extracted`` through the H5 promotion gate.
- Isolation fail-closed (SB-S6): with the parser-isolation boundary unproven the
  pipeline never touches a decoder and returns ``isolation_unavailable``.
- SB-S7: a wrong-address document (BBL mismatch) fails ``address_bbl_match`` and
  routes to ``needs_review`` with the typed wrong-address routing value.
- SB-S3: a decode refusal, an empty extraction, and any failed/unresolved check route
  to ``needs_review`` — never a silent pass, never a silent drop.
- SB-S8: every assembled ``survey_evidence`` record validates against the canonical
  v1 schema (jsonschema engine with the contract $ref registry).

The isolation gate is stubbed via monkeypatch of the routing module's
``require_isolation`` attribute (a test seam, not a runtime parameter), so outcomes
are deterministic on every host platform.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import app.documents.extraction.routing as routing_module
import app.documents.extraction.survey_pipeline as pipeline_module
from app.documents.extraction import survey_pipeline as sp
from app.documents.extraction.routing import SurveyDocumentFormat
from app.documents.extraction.vector_pdf_decoder import VectorPdfDecoder
from app.documents.isolation import (
    CapabilityProbe,
    IsolationCapability,
    ParsingDisabled,
    ParsingPermitted,
)
from app.documents.state import (
    ActorKind,
    DocumentState,
    TransitionActor,
    TransitionRecord,
    promotion_gated_transition,
    transition,
)

WHEN = datetime(2026, 8, 8, 12, 0, tzinfo=timezone.utc)
PIPELINE_ACTOR = TransitionActor(ActorKind.DETERMINISTIC_PIPELINE, actor_id="worker-7")
DIGEST = "sha256:" + "ab" * 32


# --------------------------------------------------------------- PDF fixtures


def _assemble_pdf(bodies, root=b"1 0 R"):
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(bodies, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref_offset = len(out)
    out += b"xref\n0 %d\n" % (len(bodies) + 1) + b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root %s >>\n" % (len(bodies) + 1, root)
    out += b"startxref\n%d\n%%%%EOF\n" % xref_offset
    return bytes(out)


def _one_page_pdf(content):
    body = b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream"
    return _assemble_pdf(
        [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>",
            body,
        ]
    )


#: A clean digitally-authored survey: a canonical scale statement and the subject BBL.
SCALE_AND_BBL_PDF = _one_page_pdf(
    b"BT /F1 12 Tf 100 700 Td (1:240) Tj 100 680 Td (1002920001) Tj ET"
)
#: The same document but stating a DIFFERENT BBL than the subject property (SB-S7).
WRONG_BBL_PDF = _one_page_pdf(
    b"BT /F1 12 Tf 100 700 Td (1:240) Tj 100 680 Td (3001230045) Tj ET"
)
#: No text matches any canonical pattern -> zero facts assembled.
NO_CLASSIFIABLE_TEXT_PDF = _one_page_pdf(
    b"BT /F1 12 Tf 100 700 Td (SURVEY OF LOT) Tj ET"
)
#: A Bezier curve is outside the strict straight-line survey subset -> decode refusal.
CURVE_PDF = _one_page_pdf(b"10 10 m 20 20 30 30 40 40 c S")


# --------------------------------------------------------------- isolation seams


def _permitted() -> IsolationCapability:
    return IsolationCapability(
        os_name="Linux",
        kernel_release="0.0-test",
        landlock=CapabilityProbe("landlock", True, "test stub"),
        seccomp=CapabilityProbe("seccomp", True, "test stub"),
        verdict=ParsingPermitted(),
    )


def _disabled() -> IsolationCapability:
    return IsolationCapability(
        os_name="TestOS",
        kernel_release="0.0-test",
        landlock=CapabilityProbe("landlock", False, "test stub"),
        seccomp=CapabilityProbe("seccomp", False, "test stub"),
        verdict=ParsingDisabled(failed_capability="os", reason="test stub: no boundary"),
    )


@pytest.fixture
def isolation_permitted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routing_module, "require_isolation", _permitted)


@pytest.fixture
def isolation_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routing_module, "require_isolation", _disabled)


def _context(subject_bbl: str = "1002920001") -> sp.SurveyExtractionContext:
    return sp.SurveyExtractionContext(
        document_digest=DIGEST,
        target_bbl="1002920001",
        subject_address="123 MAIN ST",
        subject_bbl=subject_bbl,
        extraction_run_id="ser:test:run-0001",
        extracted_at="2026-08-08T12:00:00Z",
    )


def _run(pdf: bytes, context: sp.SurveyExtractionContext | None = None):
    return sp.run_survey_extraction(
        format_identity="vector_pdf",
        original_bytes=pdf,
        context=context or _context(),
        actor=PIPELINE_ACTOR,
        occurred_at=WHEN,
    )


# --------------------------------------------------------------- schema engine


def _survey_validator():
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource

    schema_dir = Path(__file__).resolve().parents[4] / "packages" / "contracts" / "schemas" / "v1"
    resources = []
    survey_id = None
    for path in schema_dir.glob("*.schema.json"):
        doc = json.loads(path.read_text(encoding="utf-8"))
        resources.append((doc["$id"], Resource.from_contents(doc)))
        if path.name == "survey_evidence.schema.json":
            survey_id = doc["$id"]
    registry = Registry().with_resources(resources)
    return Draft202012Validator({"$ref": survey_id}, registry=registry)


# --------------------------------------------------------- isolation fail-closed


class TestIsolationFailClosed:
    def test_isolation_unavailable_never_decodes(
        self, isolation_disabled: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[bytes] = []

        class _SpyDecoder(VectorPdfDecoder):
            def decode(self, original_bytes):
                calls.append(original_bytes)
                return super().decode(original_bytes)

        monkeypatch.setitem(
            routing_module._CONCRETE_DECODERS,
            SurveyDocumentFormat.VECTOR_PDF,
            _SpyDecoder(),
        )
        outcome = _run(SCALE_AND_BBL_PDF)
        assert isinstance(outcome, sp.ExtractionNotStarted)
        assert outcome.started is False
        assert outcome.entry_outcome.reject_code == "isolation_unavailable"
        assert calls == []  # the decoder was never reached

    def test_permitted_boundary_reaches_the_decoder(
        self, isolation_permitted: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[bytes] = []

        class _SpyDecoder(VectorPdfDecoder):
            def decode(self, original_bytes):
                calls.append(original_bytes)
                return super().decode(original_bytes)

        monkeypatch.setitem(
            routing_module._CONCRETE_DECODERS,
            SurveyDocumentFormat.VECTOR_PDF,
            _SpyDecoder(),
        )
        outcome = _run(SCALE_AND_BBL_PDF)
        assert isinstance(outcome, sp.ExtractionCompleted)
        assert calls == [SCALE_AND_BBL_PDF]


# ------------------------------------------------------------ routing pass-through


class TestRoutingPassThrough:
    def test_unsupported_format_does_not_start(self, isolation_permitted: None) -> None:
        outcome = sp.run_survey_extraction(
            format_identity="docx",
            original_bytes=b"whatever",
            context=_context(),
            actor=PIPELINE_ACTOR,
            occurred_at=WHEN,
        )
        assert isinstance(outcome, sp.ExtractionNotStarted)
        assert outcome.entry_outcome.reject_code == "unsupported_format"

    def test_supported_raster_route_has_no_concrete_decoder_yet(
        self, isolation_permitted: None
    ) -> None:
        outcome = sp.run_survey_extraction(
            format_identity="tiff",
            original_bytes=b"II*\x00rest",
            context=_context(),
            actor=PIPELINE_ACTOR,
            occurred_at=WHEN,
        )
        assert isinstance(outcome, sp.DecoderUnavailable)
        assert outcome.route.format is SurveyDocumentFormat.TIFF


# ------------------------------------------------------------ the auto-extract path


class TestAutoExtracted:
    def test_clean_document_promotes_to_auto_extracted(
        self, isolation_permitted: None
    ) -> None:
        outcome = _run(SCALE_AND_BBL_PDF)
        assert isinstance(outcome, sp.ExtractionCompleted)
        assert outcome.target_state is DocumentState.AUTO_EXTRACTED
        assert len(outcome.facts) == 2
        assert {f["fact_type"] for f in outcome.facts} == {"scale_statement", "bbl_text"}
        assert outcome.wrong_address is None
        assert outcome.decode_refusal is None

    def test_every_fact_promotes_and_checks_pass(self, isolation_permitted: None) -> None:
        from app.documents.promotion import PromotionAllowed

        outcome = _run(SCALE_AND_BBL_PDF)
        assert all(
            isinstance(v, PromotionAllowed) for v in outcome.fact_verdicts.values()
        )
        assert {c.check_name for c in outcome.check_results} == {
            "scale_consistency",
            "address_bbl_match",
        }
        assert all(c.passed for c in outcome.check_results)

    def test_facts_carry_full_provenance(self, isolation_permitted: None) -> None:
        outcome = _run(SCALE_AND_BBL_PDF)
        for fact in outcome.facts:
            assert fact["document_digest"] == DIGEST
            assert fact["bbl"] == "1002920001"
            assert fact["page_number"] == 1
            assert fact["extraction_method"] == "embedded_text_extraction"
            assert fact["confidence"] == 1.0
            assert fact["extraction_run_id"] == "ser:test:run-0001"
            assert fact["professional_confirmation"]["state"] == "unconfirmed"
            assert fact["location"]["kind"] == "bounding_box"
            assert fact["validation_results"]  # a check was recorded

    def test_transition_record_is_the_gated_processing_to_auto_extracted_edge(
        self, isolation_permitted: None
    ) -> None:
        outcome = _run(SCALE_AND_BBL_PDF)
        record = outcome.transition_record
        assert isinstance(record, TransitionRecord)
        assert record.from_state is DocumentState.PROCESSING
        assert record.to_state is DocumentState.AUTO_EXTRACTED
        assert record.actor is PIPELINE_ACTOR


# --------------------------------------------------------------- SB-S8 schema


class TestSchemaValidity:
    def test_assembled_facts_validate_against_the_v1_contract(
        self, isolation_permitted: None
    ) -> None:
        validator = _survey_validator()
        outcome = _run(SCALE_AND_BBL_PDF)
        for fact in outcome.facts:
            errors = sorted(validator.iter_errors(fact), key=str)
            assert errors == [], [e.message for e in errors]


# --------------------------------------------------------- SB-S7 wrong address


class TestWrongAddressRouting:
    def test_bbl_mismatch_routes_to_needs_review(self, isolation_permitted: None) -> None:
        outcome = _run(WRONG_BBL_PDF)
        assert isinstance(outcome, sp.ExtractionCompleted)
        assert outcome.target_state is DocumentState.NEEDS_REVIEW
        assert outcome.wrong_address is not None
        assert outcome.wrong_address.routing == "needs_review"
        assert outcome.wrong_address.cause == "failed"
        assert outcome.wrong_address.usable is False

    def test_wrong_address_records_a_failed_check_on_the_bbl_fact(
        self, isolation_permitted: None
    ) -> None:
        outcome = _run(WRONG_BBL_PDF)
        bbl_fact = next(f for f in outcome.facts if f["fact_type"] == "bbl_text")
        statuses = {
            v["check_id"]: v["status"] for v in bbl_fact["validation_results"]
        }
        assert statuses["address_bbl_match"] == "fail"


# ------------------------------------------------------------ SB-S3 fail-closed


class TestFailClosedRouting:
    def test_decode_refusal_routes_to_needs_review_with_no_facts(
        self, isolation_permitted: None
    ) -> None:
        outcome = _run(CURVE_PDF)
        assert isinstance(outcome, sp.ExtractionCompleted)
        assert outcome.target_state is DocumentState.NEEDS_REVIEW
        assert outcome.facts == ()
        assert outcome.decode_refusal is not None
        assert outcome.transition_record.to_state is DocumentState.NEEDS_REVIEW

    def test_empty_extraction_routes_to_needs_review(
        self, isolation_permitted: None
    ) -> None:
        outcome = _run(NO_CLASSIFIABLE_TEXT_PDF)
        assert isinstance(outcome, sp.ExtractionCompleted)
        assert outcome.target_state is DocumentState.NEEDS_REVIEW
        assert outcome.facts == ()

    def test_payloads_are_json_serializable(self, isolation_permitted: None) -> None:
        for pdf in (SCALE_AND_BBL_PDF, WRONG_BBL_PDF, CURVE_PDF, NO_CLASSIFIABLE_TEXT_PDF):
            payload = _run(pdf).to_payload()
            assert json.loads(json.dumps(payload)) == payload


# --------------------------------------------------- gated vs non-gated transition


class TestGatedTransitionWiring:
    def test_auto_extract_goes_through_the_promotion_gate(
        self, isolation_permitted: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        gated_calls: list[dict] = []
        raw_calls: list[tuple] = []

        def _spy_gated(current, to, **kwargs):
            gated_calls.append(kwargs)
            return promotion_gated_transition(current, to, **kwargs)

        def _spy_transition(current, to, **kwargs):
            raw_calls.append((current, to))
            return transition(current, to, **kwargs)

        monkeypatch.setattr(pipeline_module, "promotion_gated_transition", _spy_gated)
        monkeypatch.setattr(pipeline_module, "transition", _spy_transition)

        outcome = _run(SCALE_AND_BBL_PDF)
        assert outcome.target_state is DocumentState.AUTO_EXTRACTED
        # The gated edge was driven with per-fact verdicts; raw transition was NOT
        # used for this gated edge.
        assert len(gated_calls) == 1
        assert set(gated_calls[0]["material_fact_verdicts"]) == set(outcome.fact_verdicts)
        assert raw_calls == []

    def test_needs_review_uses_the_non_gated_transition(
        self, isolation_permitted: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        gated_calls: list[dict] = []
        raw_calls: list[tuple] = []

        monkeypatch.setattr(
            pipeline_module,
            "promotion_gated_transition",
            lambda current, to, **kw: gated_calls.append(kw)
            or promotion_gated_transition(current, to, **kw),
        )
        monkeypatch.setattr(
            pipeline_module,
            "transition",
            lambda current, to, **kw: raw_calls.append((current, to))
            or transition(current, to, **kw),
        )

        outcome = _run(WRONG_BBL_PDF)
        assert outcome.target_state is DocumentState.NEEDS_REVIEW
        assert gated_calls == []  # the gated edge is never used to reach needs_review
        assert raw_calls == [(DocumentState.PROCESSING, DocumentState.NEEDS_REVIEW)]


# ----------------------------------------------------------- assembly unit-level


class TestAssembly:
    def test_assemble_is_deterministic(self, isolation_permitted: None) -> None:
        first = _run(SCALE_AND_BBL_PDF).facts
        second = _run(SCALE_AND_BBL_PDF).facts
        assert first == second

    def test_unclassifiable_runs_are_never_coerced_into_facts(
        self, isolation_permitted: None
    ) -> None:
        outcome = _run(NO_CLASSIFIABLE_TEXT_PDF)
        assert outcome.facts == ()
