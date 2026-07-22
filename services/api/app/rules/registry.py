"""Rule registry + coverage honesty (M4-T001).

Loads every ``*.rule.json`` under the rulesets directory, validates each through
the DSL loader, and indexes them by rule id and family. It answers coverage
queries HONESTLY: a query for a family that has no implemented rule returns a
visible ``unsupported`` status (PRD section 12; RE-S7), never silence.

The registry is family-agnostic: adding a structurally different rule family is
purely a matter of dropping a new ``*.rule.json`` in the rulesets directory - no
registry or evaluator code changes (RE-S5).
"""

from __future__ import annotations

from pathlib import Path

from . import coverage as cov
from . import evaluator, lifecycle
from .dsl import load_rule_file
from .models import RuleDefinition, RuleResult
from .snapshots import SnapshotStore

_RULESET_DIR = Path(__file__).resolve().parent / "rulesets"


# --------------------------------------------------------------------------
# FH-2: strictly fail-closed same-family rule-conflict DETECTION.
#
# This DETECTS an ambiguity and surfaces it for professional review; it NEVER
# selects, ranks, merges, supersedes, or reinterprets a competing legal rule.
# A genuine conflict requires ALL of (M4-T004-FH2-SPEC.md):
#   1. same rule family / output domain (the caller passes one family's rules);
#   2. simultaneously in effect for the same valid as_of_date
#      (``is_in_effect`` uses the half-open window ``[effective_from,
#      effective_to)`` - effective_from INCLUSIVE, effective_to EXCLUSIVE);
#   3. each independently matches the same normalized inputs (applicability
#      independently satisfied);
#   4. they compete for the same evaluation decision (overlapping OUTPUT names) -
#      complementary rules producing DIFFERENT outputs are not competitors.
# The typed result carries the competing rule IDs and each rule's effective
# window; it produces NO output/determination value. It is deterministic and
# INDEPENDENT of rule load order (competing rules + output names are sorted).
# --------------------------------------------------------------------------

def detect_rule_conflicts(
    rules: list[RuleDefinition],
    inputs: dict,
    as_of_date: str | None = None,
) -> dict | None:
    """Return a typed, deterministic conflict object when >=2 rules from a single
    family are simultaneously in effect, independently applicable to ``inputs``,
    and compete for at least one shared output name; otherwise ``None``.

    ``rules`` must all belong to one family (the registry passes one family's
    list). The outcome does not depend on the order of ``rules``.
    """
    # FH-4: an impossible/malformed calendar ``as_of_date`` must fail closed
    # IDENTICALLY to the single-rule evaluate path. evaluator.evaluate already
    # routes as_of_date through ``_valid_iso_date`` and marks such a date
    # ``in_effect=False`` (FH-1); the raw ``RuleDefinition.is_in_effect`` used
    # below does a LEXICAL string comparison and would treat e.g. "2024-02-30"
    # as a real date - a temporal asymmetry that could spuriously report a
    # conflict on a date that does not exist. A date no rule can be in effect on
    # can carry no simultaneous-in-effect conflict, so we short-circuit to None
    # here using the SAME validator the evaluate path uses. ``None`` (no
    # temporal gating) and every real date - including a genuine leap day
    # "2024-02-29" - are unaffected; this is additive and strictly fail-closed.
    if as_of_date is not None and not evaluator._valid_iso_date(as_of_date):
        return None
    candidates = [
        rule
        for rule in rules
        if rule.is_in_effect(as_of_date) and evaluator.applicability_satisfied(rule, inputs)
    ]
    if len(candidates) < 2:
        return None
    # Group applicable+in-effect rules by each output name they would emit.
    output_to_rules: dict[str, list[RuleDefinition]] = {}
    for rule in candidates:
        for name in rule.output_names():
            output_to_rules.setdefault(name, []).append(rule)
    contested = sorted(name for name, rs in output_to_rules.items() if len(rs) >= 2)
    if not contested:
        # Only complementary rules (each emitting distinct outputs) coexist -> the
        # rules do not compete for the same decision; NOT a conflict.
        return None
    competing: dict[str, RuleDefinition] = {}
    for name in contested:
        for rule in output_to_rules[name]:
            competing[rule.rule_id] = rule
    competing_rules = [competing[rule_id] for rule_id in sorted(competing)]
    return {
        "conflict": True,
        "family": competing_rules[0].family,
        "as_of_date": as_of_date,
        "competing_output_names": contested,
        "competing_rules": [
            {
                "rule_id": rule.rule_id,
                "rule_version": rule.rule_version,
                "effective_from": rule.effective_from,
                "effective_to": rule.effective_to,
                "output_names": sorted(rule.output_names()),
            }
            for rule in competing_rules
        ],
        "note": (
            "multiple same-family rules are simultaneously in effect and "
            "independently applicable to the same inputs for overlapping "
            "output(s); which rule governs is a legal determination requiring "
            "professional review - no value is produced from the competing rules"
        ),
    }


class RuleRegistry:
    def __init__(self, ruleset_dir: Path | None = None, snapshots: SnapshotStore | None = None):
        self.ruleset_dir = Path(ruleset_dir) if ruleset_dir else _RULESET_DIR
        self.snapshots = snapshots or SnapshotStore()
        self._by_id: dict[str, RuleDefinition] = {}
        self._by_family: dict[str, list[RuleDefinition]] = {}
        self._loaded = False

    def load(self) -> RuleRegistry:
        self._by_id.clear()
        self._by_family.clear()
        self.snapshots.load()
        if not self.ruleset_dir.is_dir():
            raise FileNotFoundError(f"ruleset directory not found: {self.ruleset_dir}")
        for path in sorted(self.ruleset_dir.glob("*.rule.json")):
            rule = load_rule_file(path, self.snapshots)
            if rule.rule_id in self._by_id:
                raise ValueError(f"duplicate rule_id {rule.rule_id!r}")
            self._by_id[rule.rule_id] = rule
            self._by_family.setdefault(rule.family, []).append(rule)
        self._loaded = True
        return self

    def _ensure(self) -> None:
        if not self._loaded:
            self.load()

    def rule(self, rule_id: str) -> RuleDefinition:
        self._ensure()
        if rule_id not in self._by_id:
            raise KeyError(f"unknown rule_id {rule_id!r}")
        return self._by_id[rule_id]

    def rule_ids(self) -> list[str]:
        self._ensure()
        return sorted(self._by_id)

    def families(self) -> list[str]:
        self._ensure()
        return sorted(self._by_family)

    def evaluate(
        self,
        rule_id: str,
        inputs: dict,
        *,
        spatial_context: dict | None = None,
        g6_approval: lifecycle.G6Approval | None = None,
        as_of_date: str | None = None,
    ) -> RuleResult:
        rule = self.rule(rule_id)
        return evaluator.evaluate(
            rule,
            inputs,
            self.snapshots,
            spatial_context=spatial_context,
            g6_approval=g6_approval,
            as_of_date=as_of_date,
        )

    def effective_rules(self, family: str, as_of_date: str | None) -> list[RuleDefinition]:
        """Temporal selection (M4-T003): rules in ``family`` whose effective window
        contains ``as_of_date``. A well-formed temporal series yields exactly one;
        zero means no version governs that date (a visible not-effective gap) and
        more than one is an overlapping-window authoring error the caller must
        surface, never silently pick from."""
        self._ensure()
        return [
            rule
            for rule in self._by_family.get(family, [])
            if rule.is_in_effect(as_of_date)
        ]

    def detect_conflicts(
        self, family: str, inputs: dict, as_of_date: str | None = None
    ) -> dict | None:
        """FH-2: detect a strictly fail-closed same-family rule conflict for
        ``inputs`` as of ``as_of_date`` (see :func:`detect_rule_conflicts`).
        Returns a typed conflict object or ``None``. Deterministic and
        independent of rule load order; never picks a winner."""
        self._ensure()
        return detect_rule_conflicts(self._by_family.get(family, []), inputs, as_of_date)

    def family_coverage(self, family: str) -> dict:
        """Coverage honesty (RE-S7): a family with no implemented rule is a
        VISIBLE ``unsupported``, not an empty/silent answer."""
        self._ensure()
        if family not in self._by_family:
            return {
                "family": family,
                "coverage_status": cov.COVERAGE_UNSUPPORTED,
                "note": "no rule implemented for this family in the current registry",
            }
        return {
            "family": family,
            "coverage_status": cov.COVERAGE_CONDITIONAL,
            "note": "one or more draft rules implemented; results are conditional pending G6",
            "rule_ids": [r.rule_id for r in self._by_family[family]],
        }
