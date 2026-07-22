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
