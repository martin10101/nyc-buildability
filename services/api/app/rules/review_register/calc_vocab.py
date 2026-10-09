#!/usr/bin/env python3
"""Vocabularies and fixed field-key sets for the review register's CALCULATION entries (M4-T038).

Split out of ``review_register_calculations.py`` (DB-211 c) so the checker and the renderer stay
inside focused module boundaries; every name is re-exported from the old path for its importers.
Pure data: no logic, no I/O, no imports beyond ``__future__``.
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# vocabularies
# --------------------------------------------------------------------------
ENTRY_KIND_VALUES = ("calculation", "calculation_comparison")
LEGAL_VS_DESIGN_KINDS = ("LEGAL_REQUIREMENT", "DESIGN_ASSUMPTION")
BASIS_KINDS = ("law_text", "reference_case", "gap")
ACTUAL_STATES = (
    "available", "available_conditional", "conditional", "withheld",
    "not_available", "not_built",
)
STEP_VERDICTS = ("agree", "differ", "side_missing")
# Step 'actual' states on the six-step page (DB-211 a). They are NOT the example ``ACTUAL_STATES``:
# a PRESENT state carries a real program answer; an ABSENT state means the program side is withheld,
# not available or not built. A step whose side is withheld/not built cannot read 'agree'/'differ';
# 'not_available' may read 'differ' (a difference of method) or 'side_missing'.
STEP_PRESENT_STATES = ("settled", "available", "available_conditional", "conditional")
STEP_ABSENT_STATES = ("withheld", "not_available", "not_built")
DISAGREEMENT_KINDS = (
    "a missing fact about the property", "unresolved law", "code not built",
    "a design assumption that differs",
)
AT_STATUS = ("Passed", "Failed", "Not run")
VERDICTS = ("Not reviewed", "Correct", "Incorrect", "Needs re-review")
DECISIONS = (None, "Correct", "Incorrect")
# The literal words the owner requires on the apartment size and efficiency share (R700).
PRELIM_WORDS = "preliminary assumption"
PRELIM_TOKENS = ("700", "0.60", "0.75")

# --------------------------------------------------------------------------
# field key sets
# --------------------------------------------------------------------------
LAW_KEYS = {
    "section", "official_url", "snapshot_id", "snapshot_file", "last_amended",
    "captured_on", "content_digest_sha256",
}
CODE_MODULE_KEYS = {"path", "sha256"}
BEHAVIOUR_KEYS = {"tested", "committed_untested", "planned"}
LEGAL_VS_DESIGN_KEYS = {
    "figure", "kind", "quoted_text", "capture_snapshot_id", "capture_digest",
}
EXPECTED_KEYS = {"values", "basis_kind", "basis", "cited_rows", "prepared_by"}
ACTUAL_KEYS = {"values", "state", "engine_values", "engine_note"}
EXAMPLE_KEYS = {"description", "inputs", "expected", "actual", "agrees"}
CITED_ROW_KEYS = {"case_file", "row_id"}
AT_KEYS = {
    "status", "tested_commit", "tested_on", "command", "counts", "evidence",
    "tested_code_identity_sha256", "tested_test_file_sha256s", "note",
}
HR_KEYS = {
    "decision", "reviewer_name", "reviewer_role", "review_date", "comments",
    "reviewed_revision", "reviewed_conditions", "reviewed_code_identity_sha256",
    "reviewed_law_digests", "applies_to_current", "verdict",
}
STEP_KEYS = {"step", "name", "component_ref", "expected", "actual", "verdict", "note"}
STEP_EXPECTED_KEYS = {"value", "basis_kind", "cited_rows", "prepared_by"}
STEP_ACTUAL_KEYS = {"value", "state", "source"}
CLOSING_KEYS = {"disagreements", "missing_facts"}
# program_results names the committed-results-document result(s) a gap row is about, so a test can
# confirm the row's kind matches the program's own gap_kind for that result (M4-T038 correction).
DISAGREEMENT_KEYS = {"kind", "what", "would_settle", "program_results"}

_COMMON_KEYS = {
    "entry_id", "entry_kind", "title", "family", "law", "combines_rule_ids",
    "code_modules", "code_identity_sha256", "applicable_from", "applicable_to",
    "applies_where", "exceptions", "interpretation", "units", "measurement_basis",
    "behaviour", "legal_vs_design", "linked_records", "test_links", "automated_tests",
    "revision", "last_changed", "human_review", "gaps", "coverage_gap", "draft_note",
}
CALC_ENTRY_KEYS = _COMMON_KEYS | {"inputs", "formula", "rounding", "example"}
CALC_COMPARISON_KEYS = _COMMON_KEYS | {"steps", "closing"}

CALC_HISTORY_KEYS = {"seq", "date", "entry_id", "revision", "event", "summary", "by"}
HISTORY_EVENTS = (
    "created", "interpretation_changed", "applicability_changed",
    "implementation_changed", "evidence_changed", "human_verdict_recorded",
    "flagged_for_re_review",
)
