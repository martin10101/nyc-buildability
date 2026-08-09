"""Unit tests for the extraction routing/gating shell (M2-T015 unit 3i-2).

Covers, per docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md sections 2-3:

- S3 format routing (SB-S2): every CLOSED-matrix row routes exactly as the
  architecture states it — supported rows carry their permitted extraction_method
  values verbatim, DXF/DWG defer with the stated vector-PDF-export alternative,
  and anything else is rejected naming the supported formats.
- The isolation-gated single pipeline entry: ParsingDisabled yields the frozen
  IsolationUnavailable outcome (document rests in uploaded, S2-S8 never run), and
  begin_extraction_job structurally has NO bypass parameter.
- Wrong-address routing (SB-S7): an address_bbl_match FAIL and UNEVALUABLE both
  produce the typed needs_review routing value, and the professional-confirmation
  exit from needs_review is promotion-gated.

The isolation gate is stubbed via monkeypatch of the module attribute (a test seam,
not a runtime parameter) so outcomes are deterministic on every host platform.
"""

from __future__ import annotations

import dataclasses
import inspect
import json

import pytest

import app.documents.extraction.routing as routing_module
from app.documents.checks import CheckFailed, CheckPassed, CheckUnevaluable
from app.documents.extraction import (
    SUPPORTED_FORMATS,
    DecoderSeam,
    ExtractionJobAuthorized,
    IsolationUnavailable,
    NeedsReviewRouting,
    RouteDeferred,
    RouteRejected,
    RouteSupported,
    SurveyDocumentFormat,
    begin_extraction_job,
    route_format,
    wrong_address_routing,
)
from app.documents.isolation import (
    CapabilityProbe,
    IsolationCapability,
    ParsingDisabled,
    ParsingPermitted,
)
from app.documents.state import PROMOTION_GATED_TRANSITIONS, DocumentState

# ------------------------------------------------------------------ test fixtures

#: The section-3 matrix, restated verbatim as the tests' independent expectation:
#: format row -> (permitted extraction_method values in matrix-cell order, raster_only).
ROW_3_METHODS = (
    "ocr_text",
    "line_symbol_detection",
    "ai_assisted_classification",
    "deterministic_geometry_reconstruction",
)

SUPPORTED_MATRIX = {
    SurveyDocumentFormat.BORN_DIGITAL_PDF: (
        (
            "embedded_text_extraction",
            "vector_object_extraction",
            "ai_assisted_classification",
            "deterministic_geometry_reconstruction",
        ),
        False,
    ),
    SurveyDocumentFormat.VECTOR_PDF: (
        (
            "vector_object_extraction",
            "embedded_text_extraction",
            "ai_assisted_classification",
            "deterministic_geometry_reconstruction",
        ),
        False,
    ),
    SurveyDocumentFormat.SCANNED_PDF: (ROW_3_METHODS, True),
    SurveyDocumentFormat.TIFF: (ROW_3_METHODS, True),
    SurveyDocumentFormat.PNG: (ROW_3_METHODS, True),
    SurveyDocumentFormat.JPEG: (ROW_3_METHODS, True),
}


def _probe(name: str, available: bool) -> CapabilityProbe:
    return CapabilityProbe(capability=name, available=available, detail="test stub")


def _capability_disabled() -> IsolationCapability:
    return IsolationCapability(
        os_name="TestOS",
        kernel_release="0.0-test",
        landlock=_probe("landlock", False),
        seccomp=_probe("seccomp", False),
        verdict=ParsingDisabled(
            failed_capability="os",
            reason="test stub: no kernel-enforced boundary on this host",
        ),
    )


def _capability_permitted() -> IsolationCapability:
    return IsolationCapability(
        os_name="Linux",
        kernel_release="0.0-test",
        landlock=_probe("landlock", True),
        seccomp=_probe("seccomp", True),
        verdict=ParsingPermitted(),
    )


@pytest.fixture
def isolation_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routing_module, "require_isolation", _capability_disabled)


@pytest.fixture
def isolation_permitted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(routing_module, "require_isolation", _capability_permitted)


def _address_failed() -> CheckFailed:
    return CheckFailed(
        check_name="address_bbl_match",
        unit=None,
        tolerance=0,
        computed={"mismatched_fact_count": 1},
    )


def _address_unevaluable() -> CheckUnevaluable:
    return CheckUnevaluable(
        check_name="address_bbl_match",
        reason="no resolved address or BBL text fact was submitted",
    )


# --------------------------------------------------- S3 format routing (SB-S2)


class TestFormatRoutingMatrix:
    @pytest.mark.parametrize(
        ("fmt", "expected_methods", "expected_raster_only"),
        [(f, m, r) for f, (m, r) in SUPPORTED_MATRIX.items()],
        ids=[f.value for f in SUPPORTED_MATRIX],
    )
    def test_supported_rows_route_with_verbatim_methods(
        self,
        fmt: SurveyDocumentFormat,
        expected_methods: tuple[str, ...],
        expected_raster_only: bool,
    ) -> None:
        route = route_format(fmt)
        assert isinstance(route, RouteSupported)
        assert route.format is fmt
        assert route.extraction_methods == expected_methods
        assert route.raster_only is expected_raster_only
        assert route.supported is True

    def test_supported_formats_constant_is_exactly_the_six_matrix_rows(self) -> None:
        assert SUPPORTED_FORMATS == tuple(SUPPORTED_MATRIX)

    def test_serialized_member_value_routes_via_the_closed_enum(self) -> None:
        route = route_format("vector_pdf")
        assert isinstance(route, RouteSupported)
        assert route.format is SurveyDocumentFormat.VECTOR_PDF

    def test_dxf_defers_steering_to_vector_pdf_export(self) -> None:
        route = route_format(SurveyDocumentFormat.DXF)
        assert isinstance(route, RouteDeferred)
        assert route.format is SurveyDocumentFormat.DXF
        assert route.reject_code == "format_deferred"
        assert route.supported is False
        assert "vector PDF" in route.guidance
        assert "G1" in route.guidance

    def test_dwg_defers_with_store_only_also_deferred_explanation(self) -> None:
        route = route_format(SurveyDocumentFormat.DWG)
        assert isinstance(route, RouteDeferred)
        assert route.format is SurveyDocumentFormat.DWG
        assert route.reject_code == "format_deferred"
        assert "store-only" in route.guidance
        assert "B-001" in route.guidance
        assert "vector PDF" in route.guidance
        assert "licensing/payment STOP" in route.guidance

    @pytest.mark.parametrize(
        "unknown",
        ["docx", "pdf", "heic", "", None, 7, b"%PDF-", object()],
        ids=["docx", "coarse-pdf", "heic", "empty", "none", "int", "bytes", "object"],
    )
    def test_anything_outside_the_matrix_is_rejected_naming_supported(
        self, unknown: object
    ) -> None:
        route = route_format(unknown)
        assert isinstance(route, RouteRejected)
        assert route.reject_code == "unsupported_format"
        assert route.supported is False
        assert route.presented == repr(unknown)
        assert route.supported_formats == tuple(f.value for f in SUPPORTED_FORMATS)

    def test_every_enum_member_routes_to_a_typed_route(self) -> None:
        for fmt in SurveyDocumentFormat:
            route = route_format(fmt)
            assert isinstance(route, (RouteSupported, RouteDeferred))
            if fmt in SUPPORTED_MATRIX:
                assert isinstance(route, RouteSupported)
            else:
                assert isinstance(route, RouteDeferred)


# ------------------------------------------- isolation-gated pipeline entry


class TestBeginExtractionJob:
    def test_parsing_disabled_yields_isolation_unavailable(
        self, isolation_disabled: None
    ) -> None:
        outcome = begin_extraction_job(SurveyDocumentFormat.VECTOR_PDF)
        assert isinstance(outcome, IsolationUnavailable)
        assert outcome.authorized is False
        assert outcome.reject_code == "isolation_unavailable"
        assert outcome.resting_state is DocumentState.UPLOADED
        assert isinstance(outcome.verdict, ParsingDisabled)
        assert outcome.verdict.failed_capability == "os"

    def test_gate_is_consulted_before_any_routing(
        self, isolation_disabled: None
    ) -> None:
        outcome = begin_extraction_job("docx")
        assert isinstance(outcome, IsolationUnavailable)

    def test_permitted_supported_route_authorizes_with_route_and_seam(
        self, isolation_permitted: None
    ) -> None:
        outcome = begin_extraction_job(SurveyDocumentFormat.VECTOR_PDF)
        assert isinstance(outcome, ExtractionJobAuthorized)
        assert outcome.authorized is True
        assert isinstance(outcome.route, RouteSupported)
        assert outcome.route.format is SurveyDocumentFormat.VECTOR_PDF
        assert outcome.route.extraction_methods == SUPPORTED_MATRIX[
            SurveyDocumentFormat.VECTOR_PDF
        ][0]
        assert outcome.decoder_protocol is DecoderSeam

    def test_permitted_deferred_route_passes_through(
        self, isolation_permitted: None
    ) -> None:
        outcome = begin_extraction_job(SurveyDocumentFormat.DXF)
        assert isinstance(outcome, RouteDeferred)
        assert outcome.reject_code == "format_deferred"

    def test_permitted_unknown_format_passes_through_rejected(
        self, isolation_permitted: None
    ) -> None:
        outcome = begin_extraction_job("docx")
        assert isinstance(outcome, RouteRejected)
        assert outcome.reject_code == "unsupported_format"

    def test_signature_has_no_bypass_parameter(self) -> None:
        sig = inspect.signature(begin_extraction_job)
        params = list(sig.parameters.values())
        assert [p.name for p in params] == ["format_identity"]
        only = params[0]
        assert only.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert only.default is inspect.Parameter.empty
        forbidden = ("isolation", "bypass", "skip", "force", "override", "unsafe")
        assert not any(
            token in p.name.lower() for p in params for token in forbidden
        )

    def test_decoder_seam_is_a_protocol_with_no_implementation(self) -> None:
        with pytest.raises(TypeError):
            DecoderSeam()  # type: ignore[misc]

        class _ConformingStub:
            def decode(self, original_bytes: bytes) -> list:
                return []

        class _NotADecoder:
            pass

        assert isinstance(_ConformingStub(), DecoderSeam)
        assert not isinstance(_NotADecoder(), DecoderSeam)


# ------------------------------------------------ wrong-address routing (SB-S7)


class TestWrongAddressRouting:
    def test_failed_address_check_routes_needs_review(self) -> None:
        decision = wrong_address_routing(_address_failed())
        assert isinstance(decision, NeedsReviewRouting)
        assert decision.routing == "needs_review"
        assert decision.target_state is DocumentState.NEEDS_REVIEW
        assert decision.flagged is True
        assert decision.usable is False
        assert decision.check_name == "address_bbl_match"
        assert decision.cause == "failed"
        assert decision.check_payload == _address_failed().to_payload()

    def test_unevaluable_address_check_also_routes_needs_review(self) -> None:
        decision = wrong_address_routing(_address_unevaluable())
        assert isinstance(decision, NeedsReviewRouting)
        assert decision.target_state is DocumentState.NEEDS_REVIEW
        assert decision.cause == "unevaluable"
        assert decision.usable is False
        assert decision.check_payload == _address_unevaluable().to_payload()

    def test_a_passed_check_never_fabricates_a_routing(self) -> None:
        passed = CheckPassed(
            check_name="address_bbl_match",
            unit=None,
            tolerance=0,
            computed={"mismatched_fact_count": 0},
        )
        with pytest.raises(TypeError):
            wrong_address_routing(passed)

    def test_a_non_check_value_is_refused(self) -> None:
        with pytest.raises(TypeError):
            wrong_address_routing({"outcome": "failed"})

    def test_another_checks_result_is_refused(self) -> None:
        other = CheckFailed(
            check_name="boundary_closure",
            unit="feet",
            tolerance=0.1,
            computed={"misclosure": 4.2},
        )
        with pytest.raises(ValueError):
            wrong_address_routing(other)

    def test_professional_confirmation_exit_is_promotion_gated(self) -> None:
        edge = (DocumentState.NEEDS_REVIEW, DocumentState.PROFESSIONALLY_CONFIRMED)
        assert edge in PROMOTION_GATED_TRANSITIONS
        assert NeedsReviewRouting.target_state is DocumentState.NEEDS_REVIEW


# ------------------------------------------------------- frozen typed results


def _frozen_samples() -> list[object]:
    return [
        route_format(SurveyDocumentFormat.VECTOR_PDF),
        route_format(SurveyDocumentFormat.SCANNED_PDF),
        route_format(SurveyDocumentFormat.DXF),
        route_format(SurveyDocumentFormat.DWG),
        route_format("docx"),
        IsolationUnavailable(
            verdict=ParsingDisabled(failed_capability="os", reason="test")
        ),
        ExtractionJobAuthorized(
            route=route_format(SurveyDocumentFormat.VECTOR_PDF),
            decoder_protocol=DecoderSeam,
        ),
        wrong_address_routing(_address_failed()),
        wrong_address_routing(_address_unevaluable()),
    ]


class TestResultDiscipline:
    @pytest.mark.parametrize(
        "result",
        _frozen_samples(),
        ids=lambda r: type(r).__name__,
    )
    def test_every_result_is_frozen(self, result: object) -> None:
        field = dataclasses.fields(result)[0].name
        with pytest.raises(dataclasses.FrozenInstanceError):
            setattr(result, field, "mutated")

    @pytest.mark.parametrize(
        "result",
        _frozen_samples(),
        ids=lambda r: type(r).__name__,
    )
    def test_every_payload_is_json_serializable(self, result: object) -> None:
        payload = result.to_payload()  # type: ignore[attr-defined]
        assert json.loads(json.dumps(payload)) == payload
