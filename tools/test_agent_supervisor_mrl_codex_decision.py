"""M0-T134 / D-024 Amendment 39 R502/R503/R504/R505 (C9): the untrusted ReviewVerdict
contract and the controller-authoritative, git-bound CodexDecision.

Covers the fail-closed mutants the owner enumerated (unknown field, wrong type, bad
enum, excess length, duplicate/fabricated evidence ids), the R504 rule that APPROVE
alone never produces COMPLETE, and the R505 Option-B-neutral git binding (arbitrary
base ref; malformed SHA/ref fails closed; legacy verified_origin_main not repurposed).
"""

import unittest

from tools.agent_supervisor import mrl_codex_decision as mcd
from tools.agent_supervisor.mrl_codex_decision import (
    CodexDecision,
    GitBinding,
    ReviewVerdict,
    build_codex_decision,
    git_binding_from_observation,
)
from tools.agent_supervisor.mrl_remote import RemoteObservation
from tools.agent_supervisor.mrl_worker_result import ContractError

ISSUED = {"ev-1", "ev-2", "ev-3"}


def _raw(**over):
    raw = {"verdict": "APPROVE", "rationale": "looks correct",
           "evidence_ref_ids": ["ev-1", "ev-2"]}
    raw.update(over)
    return raw


def _binding(**over):
    base = dict(normalized_remote_url="https://github.com/o/r",
                expected_base_ref="refs/heads/integration",
                observed_base_sha="c" * 40, task_branch="stabilization/D-024-mrl",
                task_head_sha="d" * 40, observed_at_utc="2026-09-01T17:00:00+00:00")
    base.update(over)
    return GitBinding(**base)


def _verdict(**over):
    return ReviewVerdict.from_provider(_raw(**over), issued_evidence_ids=ISSUED)


class ReviewVerdictContractTests(unittest.TestCase):
    def test_positive(self) -> None:
        v = _verdict()
        self.assertEqual(v.verdict, "APPROVE")
        self.assertEqual(v.evidence_ref_ids, ("ev-1", "ev-2"))

    def _rejects(self, **over):
        with self.assertRaises(ContractError):
            ReviewVerdict.from_provider(_raw(**over), issued_evidence_ids=ISSUED)

    def test_unknown_and_forged_fields_rejected(self) -> None:  # R503
        self._rejects(note="x")
        self._rejects(observed_base_sha="c" * 40)
        self._rejects(decision="COMPLETE")

    def test_wrong_type_and_bad_enum_rejected(self) -> None:
        self._rejects(verdict="approve")
        self._rejects(verdict="COMPLETE")
        self._rejects(rationale=123)
        self._rejects(evidence_ref_ids="ev-1")

    def test_lengths_and_cardinality_rejected(self) -> None:
        self._rejects(rationale="x" * 4097)
        self._rejects(evidence_ref_ids=[])                       # minItems 1
        self._rejects(evidence_ref_ids=["ev-1", "ev-1"])         # uniqueItems (dup)
        self._rejects(evidence_ref_ids=["e" * 129])              # item maxLength

    def test_non_controller_evidence_id_rejected(self) -> None:  # R502
        with self.assertRaises(ContractError):
            ReviewVerdict.from_provider(_raw(evidence_ref_ids=["ev-1", "forged-id"]),
                                        issued_evidence_ids=ISSUED)

    def test_more_than_max_ids_rejected(self) -> None:
        many = [f"ev-{i}" for i in range(65)]
        with self.assertRaises(ContractError):
            ReviewVerdict.from_provider(_raw(evidence_ref_ids=many),
                                        issued_evidence_ids=set(many))


class Rule504Tests(unittest.TestCase):
    """APPROVE alone never produces COMPLETE."""

    def test_approve_with_all_ok_completes(self) -> None:
        d = build_codex_decision(_verdict(), _binding(),
                                 invariants_ok=True, gates_ok=True)
        self.assertEqual(d.decision, "COMPLETE")

    def test_approve_with_failing_invariants_is_hold_not_complete(self) -> None:
        d = build_codex_decision(_verdict(), _binding(),
                                 invariants_ok=False, gates_ok=True)
        self.assertEqual(d.decision, "HOLD")

    def test_approve_with_failing_gates_is_hold_not_complete(self) -> None:
        d = build_codex_decision(_verdict(), _binding(),
                                 invariants_ok=True, gates_ok=False)
        self.assertEqual(d.decision, "HOLD")

    def test_truthy_non_bool_gate_does_not_complete(self) -> None:
        # A truthy non-True controller flag must fail closed to HOLD, never COMPLETE.
        for bad in (1, "yes", [1]):
            d = build_codex_decision(_verdict(), _binding(), invariants_ok=bad, gates_ok=True)
            self.assertEqual(d.decision, "HOLD")
            d2 = build_codex_decision(_verdict(), _binding(), invariants_ok=True, gates_ok=bad)
            self.assertEqual(d2.decision, "HOLD")

    def test_revise_and_halt_pass_through(self) -> None:
        self.assertEqual(build_codex_decision(_verdict(verdict="REVISE"), _binding(),
                                              invariants_ok=True, gates_ok=True).decision, "REVISE")
        self.assertEqual(build_codex_decision(_verdict(verdict="HALT"), _binding(),
                                              invariants_ok=True, gates_ok=True).decision, "HALT")


class Rule505GitBindingTests(unittest.TestCase):
    def test_option_b_neutral_arbitrary_base_ref(self) -> None:
        d = build_codex_decision(_verdict(), _binding(expected_base_ref="refs/heads/develop"),
                                 invariants_ok=True, gates_ok=True)
        self.assertEqual(d.git.expected_base_ref, "refs/heads/develop")

    def test_legacy_field_not_repurposed(self) -> None:
        # The legacy verified_origin_main field must not be a binding field, a
        # decision field, or a module attribute here (it stays on the disabled
        # legacy path). Prose in the docstring explaining that is fine.
        import dataclasses
        self.assertNotIn("verified_origin_main", {f.name for f in dataclasses.fields(GitBinding)})
        self.assertNotIn("verified_origin_main", {f.name for f in dataclasses.fields(CodexDecision)})
        self.assertFalse(hasattr(mcd, "verified_origin_main"))
        # the built decision's git binding carries the Option-B fields, not the legacy one
        d = build_codex_decision(_verdict(), _binding(), invariants_ok=True, gates_ok=True)
        self.assertNotIn("verified_origin_main", d.as_dict()["git"])
        self.assertIn("observed_base_sha", d.as_dict()["git"])

    def test_malformed_shas_fail_closed(self) -> None:
        with self.assertRaises(ContractError):
            build_codex_decision(_verdict(), _binding(observed_base_sha="short"),
                                 invariants_ok=True, gates_ok=True)
        with self.assertRaises(ContractError):
            build_codex_decision(_verdict(), _binding(task_head_sha="xyz"),
                                 invariants_ok=True, gates_ok=True)

    def test_missing_ref_or_url_fail_closed(self) -> None:
        with self.assertRaises(ContractError):
            build_codex_decision(_verdict(), _binding(expected_base_ref=""),
                                 invariants_ok=True, gates_ok=True)
        with self.assertRaises(ContractError):
            build_codex_decision(_verdict(), _binding(normalized_remote_url="  "),
                                 invariants_ok=True, gates_ok=True)

    def test_git_binding_from_observation(self) -> None:
        obs = RemoteObservation("https://github.com/o/r", "refs/heads/integration",
                                "c" * 40, "2026-09-01T17:00:00+00:00")
        gb = git_binding_from_observation(obs, task_branch="tb", task_head_sha="d" * 40)
        self.assertEqual((gb.observed_base_sha, gb.expected_base_ref, gb.task_head_sha),
                         ("c" * 40, "refs/heads/integration", "d" * 40))
        d = build_codex_decision(_verdict(), gb, invariants_ok=True, gates_ok=True)
        self.assertIsInstance(d, CodexDecision)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
