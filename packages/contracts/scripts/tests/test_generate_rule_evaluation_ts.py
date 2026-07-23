"""rule_evaluation.ts type-generation determinism + drift (task M4-T005).

Companion to test_generate_ts_types.py: proves the SECOND generated artifact is
byte-stable, matches the committed file, references the canonical coverage
vocabulary without admitting 'verified', and - critically - that generating it
did NOT change property_profile.ts (owner byte-identity constraint).

Run: python -m pytest packages/contracts/scripts/tests
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
CONTRACTS_ROOT = SCRIPTS_DIR.parent
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


def test_committed_rule_evaluation_is_byte_identical_to_fresh_generation() -> None:
    fresh = GEN.generate_rule_evaluation()
    committed = RULE_EVAL_GENERATED.read_text(encoding="utf-8")
    assert committed == fresh, (
        "packages/contracts/generated/rule_evaluation.ts is out of date; run "
        "python packages/contracts/scripts/generate_ts_types.py and commit it."
    )


def test_rule_evaluation_generation_is_deterministic() -> None:
    assert GEN.generate_rule_evaluation() == GEN.generate_rule_evaluation()


def test_rule_evaluation_output_uses_lf_and_single_trailing_newline() -> None:
    text = RULE_EVAL_GENERATED.read_text(encoding="utf-8")
    assert "\r\n" not in text
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_generating_rule_evaluation_does_not_change_property_profile() -> None:
    """Owner constraint: property_profile.ts stays byte-identical. generate()
    (property_profile) is unaffected by the rule_evaluation additions."""
    before = PROFILE_GENERATED.read_text(encoding="utf-8")
    GEN.generate_rule_evaluation()
    assert PROFILE_GENERATED.read_text(encoding="utf-8") == before
    # The property_profile generator output is independent of the new artifact.
    assert GEN.generate() == before


def test_rule_evaluation_ts_references_coverage_and_excludes_verified() -> None:
    ts = RULE_EVAL_GENERATED.read_text(encoding="utf-8")
    assert "export type DraftCoverageStatus = CoverageStatus &" in ts
    # The draft coverage narrowing lists exactly the five non-verified values.
    assert '"conditional" | "professional_review_required" | "data_conflict" | "unsupported" | "not_applicable"' in ts
    assert "export interface RuleEvaluation" in ts
