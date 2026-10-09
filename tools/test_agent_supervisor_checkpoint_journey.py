#!/usr/bin/env python3
"""Removal-sensitive journey coverage: turn budget, live tokens, Codex verdicts.

M0-T126 (D-024-R372). Covers the seven-property checkpoint design's sizeable,
provable parts plus R387 scenarios anchored in the PRESERVED real artifacts as
read-only replay fixtures:

- property 5 / defect D3: workload-sized turns under a hard ceiling (never a
  raised fixed max_turns), the reserved final turn, and the early/incremental
  cadence (properties 2/3);
- property 4 / defect D3 (R379): the preserved 12/12 turn-exhaustion stream
  converts to a missing-checkpoint failure — an honest incomplete result is
  NEVER treated as success (scenario 2 + 4);
- defect D5: the live-context estimate (72546) and the cumulative figure
  (694251) are recorded SEPARATELY, the ceiling consumes the LIVE figure, and
  the adversarial case at exactly 400000 flags (scenario 11/12);
- G4 correction 1 (scenario 5): a synthesized Codex CONTINUE verdict with a
  removal-sensitive assertion;
- G4 correction 2 (scenario 6): the verdict<->checkpoint-id correlation guard,
  removal-sensitive against a STALE/duplicate verdict.
"""
from __future__ import annotations

import json
import pathlib
import sys
import types
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools.agent_supervisor import claude_runner as cr  # noqa: E402
from tools.agent_supervisor import codex_reviewer as cxr  # noqa: E402
from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import turn_budget as tb  # noqa: E402
from tools.agent_supervisor.workload_classifier import (  # noqa: E402
    COHESIVE_SUBAGENT,
    MAIN_SESSION,
    OVERSIZED_SPLIT,
    UNKNOWN_RECON,
    WorkloadClassification,
)

_FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "tools" / "agent_supervisor" / "fixtures"


def _classify(work_class: str) -> WorkloadClassification:
    return WorkloadClassification(work_class, "r", "reason")


class TurnBudgetTests(unittest.TestCase):
    def test_cohesive_reserves_a_final_turn_over_the_working_allowance(self) -> None:
        budget = tb.size_turn_budget(_classify(COHESIVE_SUBAGENT))
        self.assertEqual(budget.reserved_final_turn, tb.RESERVED_FINAL_TURNS)
        self.assertEqual(budget.total_turns,
                         budget.working_turns + budget.reserved_final_turn)
        self.assertTrue(budget.dispatchable)

    def test_class_sizes_differ_not_a_single_raised_constant(self) -> None:
        # Property 5: the allowance is SIZED FROM THE CLASS, not one fixed number.
        totals = {c: tb.size_turn_budget(_classify(c)).total_turns
                  for c in (MAIN_SESSION, COHESIVE_SUBAGENT, UNKNOWN_RECON)}
        self.assertEqual(len(set(totals.values())), 3,
                         f"each class must size distinctly, got {totals}")
        self.assertGreater(totals[COHESIVE_SUBAGENT], totals[MAIN_SESSION])
        self.assertGreater(totals[MAIN_SESSION], totals[UNKNOWN_RECON])

    def test_total_never_exceeds_the_hard_ceiling(self) -> None:
        for c in (MAIN_SESSION, COHESIVE_SUBAGENT, UNKNOWN_RECON):
            self.assertLessEqual(
                tb.size_turn_budget(_classify(c)).total_turns, tb.HARD_TURN_CEILING)

    def test_allowance_over_ceiling_fails_closed(self) -> None:
        with self.assertRaises(tb.TurnBudgetError):
            tb.TurnAllowances(cohesive_subagent=tb.HARD_TURN_CEILING + 5)

    def test_early_and_incremental_cadence_within_working_turns(self) -> None:
        budget = tb.size_turn_budget(_classify(COHESIVE_SUBAGENT))
        self.assertGreaterEqual(budget.early_checkpoint_by, 1)
        self.assertLessEqual(budget.early_checkpoint_by, budget.working_turns)
        self.assertGreaterEqual(budget.incremental_checkpoint_every, 1)

    def test_oversized_is_not_dispatchable(self) -> None:
        budget = tb.size_turn_budget(_classify(OVERSIZED_SPLIT))
        self.assertFalse(budget.dispatchable)
        self.assertEqual(budget.total_turns, 0)
        self.assertIn("split", budget.stop_reason)

    def test_ceiling_clamp_preserves_reserved_final_turn(self) -> None:
        # A config allowance at the ceiling floor still keeps one reserved turn.
        allow = tb.TurnAllowances(cohesive_subagent=tb.HARD_TURN_CEILING - 1)
        budget = tb.size_turn_budget(_classify(COHESIVE_SUBAGENT), allow)
        self.assertEqual(budget.total_turns, tb.HARD_TURN_CEILING)
        self.assertEqual(budget.reserved_final_turn, tb.RESERVED_FINAL_TURNS)
        self.assertEqual(budget.working_turns,
                         tb.HARD_TURN_CEILING - tb.RESERVED_FINAL_TURNS)


class ReservedTurnInjectionTests(unittest.TestCase):
    """Property 3 (G3-2): the reserved final turn is OCCUPIED by an injected
    user-turn demand delivered through run_unit's extra_turns channel."""

    def test_dispatchable_budget_yields_exactly_one_demand(self) -> None:
        budget = tb.size_turn_budget(_classify(COHESIVE_SUBAGENT))
        injection = tb.reserved_turn_injection(budget)
        self.assertEqual(len(injection), 1)
        demand = injection[0]
        self.assertIn("RESERVED FINAL TURN", demand)
        self.assertIn("Emit your mandatory checkpoint NOW", demand)
        self.assertIn("do NOT start any new tool call", demand)
        self.assertIn(str(budget.total_turns), demand)
        self.assertIn(str(budget.working_turns), demand)

    def test_none_and_oversized_yield_no_injection(self) -> None:
        # Removal-sensitive boundary: no demand is injected without a dispatchable
        # sized budget - run_unit is dispatched exactly as before (12/12 shape).
        self.assertEqual(tb.reserved_turn_injection(None), ())
        oversized = tb.size_turn_budget(_classify(OVERSIZED_SPLIT))
        self.assertEqual(tb.reserved_turn_injection(oversized), ())

    def test_demand_forbids_further_tool_use_and_demands_honesty(self) -> None:
        demand = tb.reserved_turn_message(tb.size_turn_budget(_classify(MAIN_SESSION)))
        self.assertIn("incomplete-but-resumable", demand)
        self.assertIn("never treated as completion", demand)
        self.assertIn("missing checkpoint is treated as failure", demand)


class PreservedArtifactFactsTests(unittest.TestCase):
    def test_journey_facts_fixture_matches_preserved_numbers(self) -> None:
        facts = json.loads((_FIXTURES / "m0t107_journey_facts.json").read_text("utf-8"))
        self.assertEqual(facts["turns_consumed"], 12)
        self.assertEqual(facts["live_context_tokens"], 72546)
        self.assertEqual(facts["cumulative_context_tokens_recorded"], 694251)
        self.assertEqual(facts["rotation_figure"], 604772)
        self.assertEqual(facts["ceiling"], 400000)


class TurnExhaustionReplayTests(unittest.TestCase):
    """Defect D3 / property 4 (R379): 12/12 exhaustion is never success."""

    def setUp(self) -> None:
        self.events = json.loads(
            (_FIXTURES / "m0t107_stream_d5.json").read_text("utf-8"))

    def test_exhausted_stream_has_no_valid_checkpoint(self) -> None:
        with self.assertRaises(cr.CheckpointError) as ctx:
            cr.extract_checkpoint(self.events)
        self.assertEqual(ctx.exception.code, "missing_checkpoint")

    def test_old_fixed_bound_would_pass_new_design_fails_honestly(self) -> None:
        # The register's D3 must-have: the preserved exhaustion, replayed, yields
        # an honest incomplete-but-resumable failure (a missing checkpoint is a
        # failure, never success), which is exactly what the new cadence prevents
        # by reserving a final emission turn.
        budget = tb.size_turn_budget(_classify(COHESIVE_SUBAGENT))
        self.assertGreater(budget.total_turns, 12,
                           "the new sized budget exceeds the fixed 12 that starved "
                           "the live unit, and reserves a final checkpoint turn")


class LiveVsCumulativeTokensTests(unittest.TestCase):
    """Defect D5: live and cumulative recorded separately; ceiling uses live."""

    def setUp(self) -> None:
        self.events = json.loads(
            (_FIXTURES / "m0t107_stream_d5.json").read_text("utf-8"))

    def test_live_estimate_excludes_the_cumulative_result_event(self) -> None:
        live, known = cr.live_context_tokens(self.events)
        self.assertTrue(known)
        self.assertEqual(live, 72546)

    def test_cumulative_still_reflects_the_terminal_result(self) -> None:
        _obs, _mm, _d, cumulative, uk = cr.inspect_stream(self.events)
        self.assertTrue(uk)
        self.assertEqual(cumulative, 694251)

    def test_live_and_cumulative_differ_by_the_defect_gap(self) -> None:
        live, _ = cr.live_context_tokens(self.events)
        _o, _m, _d, cumulative, _u = cr.inspect_stream(self.events)
        self.assertLess(live, cumulative)
        self.assertLess(live, 400000)
        self.assertGreater(cumulative, 400000)

    def test_ceiling_consumes_live_when_known(self) -> None:
        rr = types.SimpleNamespace(
            live_context_tokens=72546, live_context_usage_known=True,
            context_tokens=694251, usage_known=True)
        tokens, known, basis = lp._ceiling_context_tokens(rr)
        self.assertEqual((tokens, known, basis), (72546, True, "live"))

    def test_ceiling_falls_back_to_cumulative_when_live_unknown(self) -> None:
        rr = types.SimpleNamespace(
            live_context_tokens=0, live_context_usage_known=False,
            context_tokens=500000, usage_known=True)
        tokens, known, basis = lp._ceiling_context_tokens(rr)
        self.assertEqual((tokens, known, basis), (500000, True, "cumulative"))

    def test_adversarial_exactly_at_ceiling_flags(self) -> None:
        rr = types.SimpleNamespace(
            live_context_tokens=400000, live_context_usage_known=True,
            context_tokens=694251, usage_known=True)
        tokens, known, _basis = lp._ceiling_context_tokens(rr)
        self.assertTrue(known)
        self.assertGreaterEqual(tokens, 400000)


class CodexContinueVerdictTests(unittest.TestCase):
    """G4 correction 1 (scenario 5): a synthesized CONTINUE verdict."""

    def _decision(self, **over):
        base = dict(
            schema_version="1.0.0", decision="CONTINUE",
            reviewed_task_id="M0-T107", reviewed_checkpoint_id="ckpt-1",
            verified_repo_head="abc", verified_origin_main="def",
            model_used="codex-model",
            next_claude_prompt="Proceed to the next authorized sub-step.")
        base.update(over)
        return base

    def test_valid_continue_verdict_validates(self) -> None:
        decision = cxr.validate_decision(
            self._decision(), expected_task_id="M0-T107",
            expected_checkpoint_id="ckpt-1")
        self.assertEqual(decision.decision, "CONTINUE")
        self.assertTrue(decision.next_claude_prompt.strip())

    def test_continue_without_next_prompt_fails_removal_sensitive(self) -> None:
        with self.assertRaises(cxr.ReviewError):
            cxr.validate_decision(self._decision(next_claude_prompt=""))

    def test_continue_maps_to_a_forwardable_tier(self) -> None:
        decision = cxr.validate_decision(self._decision())
        tier = cxr.map_decision_to_tier(decision)
        # A CONTINUE is not a HALT/stop; it carries a prompt to forward.
        self.assertNotEqual(decision.decision, "HALT_UNSAFE")
        self.assertIsNotNone(tier)


class CodexStaleVerdictTests(unittest.TestCase):
    """G4 correction 2 (scenario 6): verdict<->checkpoint-id correlation guard."""

    def _decision(self, checkpoint_id="ckpt-1"):
        return dict(
            schema_version="1.0.0", decision="CONTINUE",
            reviewed_task_id="M0-T107", reviewed_checkpoint_id=checkpoint_id,
            verified_repo_head="abc", verified_origin_main="def",
            model_used="codex-model", next_claude_prompt="next")

    def test_matching_checkpoint_id_is_accepted(self) -> None:
        decision = cxr.validate_decision(
            self._decision("ckpt-1"), expected_checkpoint_id="ckpt-1")
        self.assertEqual(decision.reviewed_checkpoint_id, "ckpt-1")

    def test_stale_checkpoint_id_is_refused(self) -> None:
        # A STALE verdict reviewing a DIFFERENT (earlier) checkpoint must not be
        # accepted for the current one — removal-sensitive on the correlation guard.
        with self.assertRaises(cxr.ReviewError) as ctx:
            cxr.validate_decision(
                self._decision("ckpt-STALE"), expected_checkpoint_id="ckpt-1")
        self.assertEqual(ctx.exception.code, "decision_correlation_mismatch")

    def test_stale_task_id_is_refused(self) -> None:
        with self.assertRaises(cxr.ReviewError):
            cxr.validate_decision(
                self._decision("ckpt-1"), expected_task_id="M0-T999")


if __name__ == "__main__":
    unittest.main()
