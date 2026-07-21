"""Deterministic zoning rules engine (M4-T001).

The REUSABLE rule system - a versioned JSON DSL, a deterministic evaluator with
full calculation + citation traces, section-level ZR source snapshots with
provenance, a rule lifecycle whose ``published``/``verified`` terminus requires a
qualified-human G6 approval, and coverage honesty for unimplemented families.
The first implemented family is R5 residential FAR (extracted_draft); a
structurally different family (a rear-yard rule) is representable with zero
engine changes.

AI boundary (owner directive 2026-07-20 item 5): this engine RETRIEVES,
CLASSIFIES and DRAFTS; it never publishes a legal rule or emits a ``verified``
result on its own. Deterministic code calculates; a qualified human approves.
"""

from __future__ import annotations

from . import coverage, evaluator, lifecycle
from .dsl import DSLError, load_rule_file
from .models import EvaluationTrace, RuleDefinition, RuleResult
from .registry import RuleRegistry
from .snapshots import SnapshotStore

__all__ = [
    "coverage",
    "evaluator",
    "lifecycle",
    "DSLError",
    "load_rule_file",
    "EvaluationTrace",
    "RuleDefinition",
    "RuleResult",
    "RuleRegistry",
    "SnapshotStore",
]
