"""survey_evidence.ts type-generation determinism + drift (task M2-T015, H7/SB-S8).

Companion to test_generate_ts_types.py, test_generate_rule_evaluation_ts.py,
and test_generate_scenario_ts.py: proves the FOURTH generated artifact is
byte-stable, matches the committed file, pins the closed extraction-method /
check / confirmation vocabularies, and - critically - that generating it did
NOT change property_profile.ts, rule_evaluation.ts, or scenario.ts
(byte-identity constraint).

Run: python -m pytest packages/contracts/scripts/tests
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
CONTRACTS_ROOT = SCRIPTS_DIR.parent
SURVEY_EVIDENCE_GENERATED = CONTRACTS_ROOT / "generated" / "survey_evidence.ts"
SCENARIO_GENERATED = CONTRACTS_ROOT / "generated" / "scenario.ts"
RULE_EVAL_GENERATED = CONTRACTS_ROOT / "generated" / "rule_evaluation.ts"
PROFILE_GENERATED = CONTRACTS_ROOT / "generated" / "property_profile.ts"


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "generate_ts_types", SCRIPTS_DIR / "generate_ts_types.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN = _load_generator()


def test_committed_survey_evidence_is_byte_identical_to_fresh_generation() -> None:
    fresh = GEN.generate_survey_evidence()
    committed = SURVEY_EVIDENCE_GENERATED.read_text(encoding="utf-8")
    assert committed == fresh, (
        "packages/contracts/generated/survey_evidence.ts is out of date; run "
        "python packages/contracts/scripts/generate_ts_types.py and commit it."
    )


def test_survey_evidence_generation_is_deterministic() -> None:
    assert GEN.generate_survey_evidence() == GEN.generate_survey_evidence()


def test_survey_evidence_output_uses_lf_and_single_trailing_newline() -> None:
    text = SURVEY_EVIDENCE_GENERATED.read_text(encoding="utf-8")
    assert "\r\n" not in text
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_generating_survey_evidence_does_not_change_the_other_artifacts() -> None:
    """Byte-identity constraint: property_profile.ts, rule_evaluation.ts, and
    scenario.ts stay unchanged when the survey_evidence artifact is generated."""
    profile_before = PROFILE_GENERATED.read_text(encoding="utf-8")
    rule_eval_before = RULE_EVAL_GENERATED.read_text(encoding="utf-8")
    scenario_before = SCENARIO_GENERATED.read_text(encoding="utf-8")
    GEN.generate_survey_evidence()
    assert PROFILE_GENERATED.read_text(encoding="utf-8") == profile_before
    assert RULE_EVAL_GENERATED.read_text(encoding="utf-8") == rule_eval_before
    assert SCENARIO_GENERATED.read_text(encoding="utf-8") == scenario_before
    assert GEN.generate() == profile_before
    assert GEN.generate_rule_evaluation() == rule_eval_before
    assert GEN.generate_scenario() == scenario_before


def test_survey_evidence_ts_pins_closed_vocabularies_and_digest_form() -> None:
    ts = SURVEY_EVIDENCE_GENERATED.read_text(encoding="utf-8")
    assert "export interface SurveyEvidence " in ts
    # The raw-bytes digest form is a named alias distinct from any canonical-JSON
    # digest type; document_digest uses it.
    assert "export type RawBytesDigestSha256 = string;" in ts
    assert "document_digest: RawBytesDigestSha256;" in ts
    # The closed extraction-method enum, verbatim and in schema order.
    assert (
        '"vector_object_extraction" | "embedded_text_extraction" | "ocr_text" | '
        '"line_symbol_detection" | "ai_assisted_classification" | '
        '"deterministic_geometry_reconstruction"' in ts
    )
    # Locator discriminator, fail-closed check outcomes, and the born-unconfirmed
    # confirmation state.
    assert 'kind: "bounding_box" | "vector_object";' in ts
    assert '"pass" | "fail" | "unresolved"' in ts
    assert '"unconfirmed" | "confirmed" | "rejected"' in ts
    # units is a REQUIRED key that is null when unitless - never omitted.
    assert "units: string | null;" in ts
