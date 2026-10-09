#!/usr/bin/env python3
"""Calculation-entry checker and renderer for the zoning-rule review register (M4-T038, D-090).

The register (M4-T023) carries one entry per rule-definition file. This adds a SECOND kind of entry
- a CALCULATION entry - for the combined-rule and arithmetic calculations that turn the rules into
the reported floor area, footprint, building option, legal dwelling-unit limit and preliminary
apartment estimate, and which have no rule file of their own.

This module is now a COMPATIBILITY FACADE (DB-211 c): the checker, renderer and vocabularies live in
three focused modules so each stays well inside the size/responsibility boundary, while every public
name stays importable from this old path. ``render_review_register.py`` and
``check_review_register.py`` import this and keep their old ``review_register_calculations`` alias.

- :mod:`.calc_vocab` - the vocabularies and fixed field-key sets (pure data).
- :mod:`.calc_checks` - the per-entry validators, the code-identity fingerprint, the six-step
  comparison checks, the two DB-211 (a) guards and the top-level :func:`validate_calculations`.
- :mod:`.calc_render` - the Markdown rendering of the calculation pages, table, gaps and history.

A calculation entry has no rule file, so it is fingerprinted by the LF-normalized sha256 of its
implementing code module(s); a drift fails the check as a changed rule file does for a rule entry.
The EXPECTED side of a worked example is an independent reference case; the ACTUAL side is the
program's own answer; expected is never taken from a program run. No human verdict is ever entered.
"""
from __future__ import annotations

from .calc_checks import (
    automated_tests_errors,
    calc_entry_errors,
    calc_rendered_errors,
    calculations_history_errors,
    cited_rows_errors,
    code_identity,
    code_module_errors,
    comparison_errors,
    coverage_gaps_errors,
    current_law_digests,
    derive_human_review,
    example_errors,
    figure_rows_errors,
    human_review_errors,
    law_errors,
    legal_vs_design_errors,
    lf_sha256,
    step_verdict_errors,
    validate_calculations,
)
from .calc_render import (
    render_calc_detail_md,
    render_calculations_history_section,
    render_calculations_table_section,
    render_coverage_gaps_section,
    write_calc_pages,
)
from .calc_vocab import (
    ACTUAL_KEYS,
    ACTUAL_STATES,
    AT_KEYS,
    AT_STATUS,
    BASIS_KINDS,
    BEHAVIOUR_KEYS,
    CALC_COMPARISON_KEYS,
    CALC_ENTRY_KEYS,
    CALC_HISTORY_KEYS,
    CITED_ROW_KEYS,
    CLOSING_KEYS,
    CODE_MODULE_KEYS,
    DECISIONS,
    DISAGREEMENT_KEYS,
    DISAGREEMENT_KINDS,
    ENTRY_KIND_VALUES,
    EXAMPLE_KEYS,
    EXPECTED_KEYS,
    HISTORY_EVENTS,
    HR_KEYS,
    LAW_KEYS,
    LEGAL_VS_DESIGN_KEYS,
    LEGAL_VS_DESIGN_KINDS,
    PRELIM_TOKENS,
    PRELIM_WORDS,
    STEP_ABSENT_STATES,
    STEP_ACTUAL_KEYS,
    STEP_EXPECTED_KEYS,
    STEP_KEYS,
    STEP_PRESENT_STATES,
    STEP_VERDICTS,
    VERDICTS,
)

__all__ = [
    # vocabularies and field key sets (calc_vocab)
    "ACTUAL_KEYS",
    "ACTUAL_STATES",
    "AT_KEYS",
    "AT_STATUS",
    "BASIS_KINDS",
    "BEHAVIOUR_KEYS",
    "CALC_COMPARISON_KEYS",
    "CALC_ENTRY_KEYS",
    "CALC_HISTORY_KEYS",
    "CITED_ROW_KEYS",
    "CLOSING_KEYS",
    "CODE_MODULE_KEYS",
    "DECISIONS",
    "DISAGREEMENT_KEYS",
    "DISAGREEMENT_KINDS",
    "ENTRY_KIND_VALUES",
    "EXAMPLE_KEYS",
    "EXPECTED_KEYS",
    "HISTORY_EVENTS",
    "HR_KEYS",
    "LAW_KEYS",
    "LEGAL_VS_DESIGN_KEYS",
    "LEGAL_VS_DESIGN_KINDS",
    "PRELIM_TOKENS",
    "PRELIM_WORDS",
    "STEP_ABSENT_STATES",
    "STEP_ACTUAL_KEYS",
    "STEP_EXPECTED_KEYS",
    "STEP_KEYS",
    "STEP_PRESENT_STATES",
    "STEP_VERDICTS",
    "VERDICTS",
    # checker (calc_checks)
    "automated_tests_errors",
    "calc_entry_errors",
    "calc_rendered_errors",
    "calculations_history_errors",
    "cited_rows_errors",
    "code_identity",
    "code_module_errors",
    "comparison_errors",
    "coverage_gaps_errors",
    "current_law_digests",
    "derive_human_review",
    "example_errors",
    "figure_rows_errors",
    "human_review_errors",
    "law_errors",
    "legal_vs_design_errors",
    "lf_sha256",
    "step_verdict_errors",
    "validate_calculations",
    # renderer (calc_render)
    "render_calc_detail_md",
    "render_calculations_history_section",
    "render_calculations_table_section",
    "render_coverage_gaps_section",
    "write_calc_pages",
]
