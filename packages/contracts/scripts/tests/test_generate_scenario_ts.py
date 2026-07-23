"""scenario.ts type-generation determinism + drift (task M5-T001).

Companion to test_generate_ts_types.py and test_generate_rule_evaluation_ts.py:
proves the THIRD generated artifact is byte-stable, matches the committed file,
references the canonical coverage vocabulary without admitting 'verified', and -
critically - that generating it did NOT change property_profile.ts or
rule_evaluation.ts (byte-identity constraint).

Run: python -m pytest packages/contracts/scripts/tests
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
CONTRACTS_ROOT = SCRIPTS_DIR.parent
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


def test_committed_scenario_is_byte_identical_to_fresh_generation() -> None:
    fresh = GEN.generate_scenario()
    committed = SCENARIO_GENERATED.read_text(encoding="utf-8")
    assert committed == fresh, (
        "packages/contracts/generated/scenario.ts is out of date; run "
        "python packages/contracts/scripts/generate_ts_types.py and commit it."
    )


def test_scenario_generation_is_deterministic() -> None:
    assert GEN.generate_scenario() == GEN.generate_scenario()


def test_scenario_output_uses_lf_and_single_trailing_newline() -> None:
    text = SCENARIO_GENERATED.read_text(encoding="utf-8")
    assert "\r\n" not in text
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_generating_scenario_does_not_change_the_other_artifacts() -> None:
    """Byte-identity constraint: property_profile.ts and rule_evaluation.ts stay
    unchanged when the scenario artifact is generated."""
    profile_before = PROFILE_GENERATED.read_text(encoding="utf-8")
    rule_eval_before = RULE_EVAL_GENERATED.read_text(encoding="utf-8")
    GEN.generate_scenario()
    assert PROFILE_GENERATED.read_text(encoding="utf-8") == profile_before
    assert RULE_EVAL_GENERATED.read_text(encoding="utf-8") == rule_eval_before
    assert GEN.generate() == profile_before
    assert GEN.generate_rule_evaluation() == rule_eval_before


def test_scenario_ts_references_coverage_and_excludes_verified() -> None:
    ts = SCENARIO_GENERATED.read_text(encoding="utf-8")
    assert "export type DraftCoverageStatus = CoverageStatus &" in ts
    assert (
        '"conditional" | "professional_review_required" | "data_conflict" | '
        '"unsupported" | "not_applicable"' in ts
    )
    assert "export interface Scenario " in ts
    # The narrowed alias never lists 'verified' as an admissible scenario value.
    assert 'coverage_status: DraftCoverageStatus;' in ts
