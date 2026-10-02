#!/usr/bin/env python3
"""Review-combiner tests (owner directive D-091 T6, M0-T169).

Covers every M0-T169 acceptance scenario with NO live provider call - the
combining model is never launched; a fake ``runner`` returns a controlled
``ProcessResult``. The tests prove, in code:

* primary: two well-formed reviews of one frozen head combine to the UNION of
  their findings, each tagged ``codex`` / ``claude``, with the worst unrefuted
  verdict;
* boundary: a finding is dropped ONLY for a refutation whose cited evidence code
  can confirm present (file:line in the diff, a command-output substring, or a
  SHA); an uncited / uncheckable refutation leaves it in (mutation case);
* never weaker: FAIL + PASS never combines to PASS; an unrefuted blocking finding
  keeps the verdict off PASS; a combined PASS needs both PASS or every blocking
  finding refuted with evidence (mutation case);
* missing/ambiguous: a missing / malformed / empty / timed-out / raised-exception
  review is FAIL/UNVERIFIED, never PASS, and cannot be refuted away; reviews of
  different heads are refused;
* independence: the combiner refuses when its identity equals the producer's or
  either reviewer's;
* settings: the combining model has no default (unset => refuse); the switch
  defaults off (disabled => refuse); nothing in the loop calls the combiner.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import review_combiner as rc  # noqa: E402
from tools.agent_supervisor.codex_reviewer import ReviewError, ReviewOutcome  # noqa: E402
from tools.agent_supervisor.models import CodexDecision  # noqa: E402
from tools.agent_supervisor.process import ProcessResult  # noqa: E402

HEAD = "a" * 40
OTHER_HEAD = "b" * 40
ORIGIN_MAIN = "c" * 40
COMBINER_MODEL = "claude-combiner-model"

DIFF = (
    "diff --git a/tools/foo.py b/tools/foo.py\n"
    "index 1111111..2222222 100644\n"
    "--- a/tools/foo.py\n"
    "+++ b/tools/foo.py\n"
    "@@ -10,3 +10,4 @@ def foo():\n"
    "     a = 1\n"
    "     b = 2\n"
    "+    c = 3\n"
    "     return a\n"
)
# New-side lines touched for tools/foo.py: {10, 11, 12, 13}; 12 is the '+ c = 3'.
CMD_OUTPUT = "ran 26 tests in 0.4s\nall tests passed\nexit 0"


def ok_outcome(decision: str = "CONTINUE", *, head: str = HEAD, blocking=None,
               model: str = "reviewer-model", **over) -> ReviewOutcome:
    """A trustworthy (``ok``) review wrapping a CodexDecision of the given shape."""
    prompt = over.pop("next_claude_prompt",
                       "proceed" if decision in ("CONTINUE", "REVISE") else "")
    dec = CodexDecision(
        schema_version="1.0.0", decision=decision, reviewed_task_id="M0-T169",
        reviewed_checkpoint_id="cp-1", verified_repo_head=head,
        verified_origin_main=ORIGIN_MAIN, model_used=model,
        blocking_findings=list(blocking or []), next_claude_prompt=prompt, **over)
    return ReviewOutcome(dec, model, "", 1)


def fail_outcome(code: str = "empty_review_output", msg: str = "no decision") -> ReviewOutcome:
    """An untrustworthy review (decision None, ok False) - FAIL/UNVERIFIED."""
    return ReviewOutcome(None, "reviewer-model", "", 1, error_code=code, error_message=msg)


class FakeRunner:
    """Injected in place of process.run - records argv/stdin, returns canned output."""

    def __init__(self, *, stdout: str = "", returncode: int = 0,
                 timed_out: bool = False, raises: BaseException | None = None):
        self.stdout = stdout
        self.returncode = returncode
        self.timed_out = timed_out
        self.raises = raises
        self.calls: list[dict] = []

    def __call__(self, argv, *, cwd=None, env=None, timeout=None, input_text=None):
        self.calls.append({"argv": list(argv), "cwd": cwd, "env": env,
                           "timeout": timeout, "input_text": input_text})
        if self.raises is not None:
            raise self.raises
        return ProcessResult(argv=tuple(argv), returncode=self.returncode,
                             stdout=self.stdout, stderr="", duration_seconds=0.0,
                             timed_out=self.timed_out)


def refutation_stdout(finding_id: str, evidence: dict, rationale: str = "refuted") -> str:
    return json.dumps({"refutations": [
        {"finding_id": finding_id, "evidence": evidence, "rationale": rationale}]})


def make_inputs(**over) -> rc.CombinerInputs:
    base = dict(frozen_head=HEAD, diff_text=DIFF, command_outputs=(CMD_OUTPUT,))
    base.update(over)
    return rc.CombinerInputs(**base)


def make_combiner(runner: FakeRunner | None = None, *, model: str = COMBINER_MODEL,
                  enabled: bool = True, identity: str = "combiner-instance") -> rc.ReviewCombiner:
    cfg = rc.ReviewCombinerConfig(enabled=enabled, model=model)
    return rc.ReviewCombiner("claude", config=cfg, combiner_identity=identity,
                             repo="/repo", runner=runner or FakeRunner())


def combine(combiner: rc.ReviewCombiner, *, codex, claude, inputs=None,
            producer="claude-worker", codex_id="codex-reviewer",
            claude_id="claude-reviewer") -> rc.CombinedReview:
    return combiner.combine(
        codex_review=codex, claude_review=claude, inputs=inputs or make_inputs(),
        producer_identity=producer, codex_reviewer_identity=codex_id,
        claude_reviewer_identity=claude_id)


# --------------------------------------------------------------------------
# Scenario 1 (primary): union, source tags, worst unrefuted verdict
# --------------------------------------------------------------------------


class PrimaryUnionTests(unittest.TestCase):
    def test_two_pass_reviews_combine_to_pass_without_invoking_the_model(self):
        runner = FakeRunner()
        review = combine(make_combiner(runner),
                         codex=ok_outcome("CONTINUE"), claude=ok_outcome("COMPLETE",
                         evidence_refs=[{"ref": "done"}]))
        self.assertEqual(review.verdict, rc.PASS)
        self.assertEqual(review.codex_verdict, rc.PASS)
        self.assertEqual(review.claude_verdict, rc.PASS)
        self.assertEqual(review.findings, ())
        # Nothing refutable -> the combining model is never launched.
        self.assertEqual(runner.calls, [])

    def test_union_keeps_both_source_tags_and_worst_verdict(self):
        runner = FakeRunner()  # proposes nothing
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1", "msg": "codex"}]),
                         claude=ok_outcome("REVISE", blocking=[{"id": "L1", "msg": "claude"}]))
        sources = sorted(f.source for f in review.findings)
        self.assertEqual(sources, ["claude", "codex"])
        self.assertEqual(len(review.findings), 2)
        # Both blocking, unrefuted -> worst unrefuted verdict is FAIL.
        self.assertEqual(review.verdict, rc.FAIL)
        self.assertTrue(all(not f.refuted for f in review.findings))

    def test_combined_review_is_json_serializable_with_provenance(self):
        review = combine(make_combiner(),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        blob = json.dumps(review.to_dict())  # must not raise
        self.assertIn("\"source\": \"codex\"", blob)
        self.assertIn("\"frozen_head\": \"" + HEAD + "\"", blob)


# --------------------------------------------------------------------------
# Scenario 2 (boundary): a finding is dropped ONLY with code-checked evidence
# --------------------------------------------------------------------------


class RefutationEvidenceTests(unittest.TestCase):
    def test_file_line_in_diff_refutes_the_only_finding_then_pass(self):
        runner = FakeRunner(stdout=refutation_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 12}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.refutations_accepted, 1)
        self.assertTrue(review.findings[0].refuted)
        # Every blocking finding refuted with evidence + the other PASS -> PASS.
        self.assertEqual(review.verdict, rc.PASS)

    def test_command_output_substring_refutes(self):
        runner = FakeRunner(stdout=refutation_stdout(
            "codex:blocking:0", {"type": "command_output", "text": "all tests passed"}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.PASS)
        self.assertEqual(review.refutations_accepted, 1)

    def test_short_sha_prefix_of_head_refutes(self):
        runner = FakeRunner(stdout=refutation_stdout(
            "codex:blocking:0", {"type": "sha", "sha": "aaaaaaa"}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.PASS)

    def test_uncited_refutation_does_not_drop_the_finding(self):
        # MUTATION: a refutation with NO evidence must leave the finding in.
        runner = FakeRunner(stdout=json.dumps(
            {"refutations": [{"finding_id": "codex:blocking:0", "rationale": "trust me"}]}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(review.findings[0].refuted)
        self.assertEqual(review.refutations_accepted, 0)
        self.assertEqual(review.refutations_rejected, 1)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_absent_file_line_refutation_is_rejected(self):
        runner = FakeRunner(stdout=refutation_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 999}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(review.findings[0].refuted)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_wrong_file_line_refutation_is_rejected(self):
        runner = FakeRunner(stdout=refutation_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/other.py", "line": 12}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(review.findings[0].refuted)

    def test_refutation_for_unknown_finding_is_ignored(self):
        runner = FakeRunner(stdout=refutation_stdout(
            "codex:blocking:7", {"type": "file_line", "file": "tools/foo.py", "line": 12}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(review.findings[0].refuted)
        self.assertEqual(review.refutations_rejected, 1)

    def test_evidence_present_unit(self):
        inputs = make_inputs()
        self.assertTrue(rc.evidence_present(
            {"type": "file_line", "file": "tools/foo.py", "line": 12}, inputs))
        self.assertFalse(rc.evidence_present(
            {"type": "file_line", "file": "tools/foo.py", "line": 999}, inputs))
        self.assertTrue(rc.evidence_present(
            {"type": "command_output", "text": "all tests passed"}, inputs))
        self.assertFalse(rc.evidence_present(
            {"type": "command_output", "text": "never printed"}, inputs))
        self.assertTrue(rc.evidence_present({"type": "sha", "sha": "aaaaaaa"}, inputs))
        self.assertFalse(rc.evidence_present({"type": "sha", "sha": "deadbee"}, inputs))
        # Malformed / unknown / bool-line citations are never present.
        self.assertFalse(rc.evidence_present({"type": "guess"}, inputs))
        self.assertFalse(rc.evidence_present("nope", inputs))
        self.assertFalse(rc.evidence_present(
            {"type": "file_line", "file": "tools/foo.py", "line": True}, inputs))


# --------------------------------------------------------------------------
# Scenario 3 (never weaker): FAIL never upgrades to PASS
# --------------------------------------------------------------------------


class NeverWeakerTests(unittest.TestCase):
    def test_fail_plus_pass_never_combines_to_pass(self):
        # MUTATION: a FAIL review and a PASS review must never yield PASS.
        review = combine(make_combiner(),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.codex_verdict, rc.FAIL)
        self.assertEqual(review.claude_verdict, rc.PASS)
        self.assertNotEqual(review.verdict, rc.PASS)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_non_approve_verdict_without_findings_still_fails(self):
        # REVISE with no itemized finding must still keep the verdict off PASS
        # (a synthetic 'verdict' finding stands in).
        review = combine(make_combiner(),
                         codex=ok_outcome("REVISE", blocking=[]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.FAIL)
        self.assertTrue(any(f.kind == "verdict" for f in review.findings))

    def test_stop_for_owner_is_not_pass(self):
        review = combine(make_combiner(),
                         codex=ok_outcome("STOP_FOR_OWNER", owner_question="ok?"),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.codex_verdict, rc.FAIL)
        self.assertNotEqual(review.verdict, rc.PASS)

    def test_halt_unsafe_with_fake_evidence_stays_fail(self):
        runner = FakeRunner(stdout=refutation_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 777}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("HALT_UNSAFE", blocking=[{"id": "danger"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(review.findings[0].refuted)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_combined_pass_needs_every_blocking_refuted(self):
        # Two blocking findings; only one refuted with evidence -> still FAIL.
        runner = FakeRunner(stdout=refutation_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 12}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}, {"id": "C2"}]),
                         claude=ok_outcome("CONTINUE"))
        refuted = [f.refuted for f in review.findings]
        self.assertEqual(sorted(refuted), [False, True])
        self.assertEqual(review.verdict, rc.FAIL)


# --------------------------------------------------------------------------
# Scenario 4 (missing/ambiguous): untrustworthy review + different heads
# --------------------------------------------------------------------------


class MissingOrAmbiguousTests(unittest.TestCase):
    def test_missing_review_is_unverified_never_pass(self):
        review = combine(make_combiner(), codex=None, claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.codex_verdict, rc.UNVERIFIED)
        self.assertEqual(review.verdict, rc.UNVERIFIED)

    def test_empty_review_is_unverified(self):
        review = combine(make_combiner(), codex=fail_outcome("empty_review_output"),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.UNVERIFIED)

    def test_timeout_review_is_unverified(self):
        review = combine(make_combiner(), codex=fail_outcome("review_timeout"),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.UNVERIFIED)

    def test_raised_exception_review_is_unverified(self):
        # N1 (M0-T168): a raised launch exception must count as FAIL, never PASS.
        raised = rc.unverified_outcome("review_raised", "FileNotFoundError: claude")
        review = combine(make_combiner(), codex=raised, claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.codex_verdict, rc.UNVERIFIED)
        self.assertEqual(review.verdict, rc.UNVERIFIED)

    def test_unverified_review_cannot_be_refuted_away(self):
        # Even a real-evidence refutation cannot drop a missing review's finding.
        # claude contributes a refutable finding so the model IS invoked, and the
        # model also tries (illegitimately) to refute the unverified finding.
        runner = FakeRunner(stdout=json.dumps({"refutations": [
            {"finding_id": "codex:unverified",
             "evidence": {"type": "file_line", "file": "tools/foo.py", "line": 12}},
        ]}))
        review = combine(make_combiner(runner), codex=None,
                         claude=ok_outcome("REVISE", blocking=[{"id": "L1"}]))
        unverified = [f for f in review.findings if f.kind == "unverified"]
        self.assertTrue(unverified and not unverified[0].refuted)
        self.assertEqual(review.verdict, rc.UNVERIFIED)
        self.assertEqual(review.refutations_rejected, 1)

    def test_missing_review_finding_is_never_refutable_so_model_is_skipped(self):
        # With only a non-refutable unverified finding, the model is never called.
        runner = FakeRunner()
        review = combine(make_combiner(runner), codex=None,
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.UNVERIFIED)
        self.assertEqual(runner.calls, [])

    def test_other_finding_refuted_but_missing_review_still_unverified(self):
        runner = FakeRunner(stdout=refutation_stdout(
            "claude:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 12}))
        review = combine(make_combiner(runner), codex=fail_outcome(),
                         claude=ok_outcome("REVISE", blocking=[{"id": "L1"}]))
        self.assertEqual(review.verdict, rc.UNVERIFIED)

    def test_reviews_of_different_heads_are_refused(self):
        runner = FakeRunner()
        with self.assertRaises(ReviewError) as ctx:
            combine(make_combiner(runner), codex=ok_outcome("CONTINUE", head=HEAD),
                    claude=ok_outcome("CONTINUE", head=OTHER_HEAD))
        self.assertEqual(ctx.exception.code, "reviews_of_different_heads")
        self.assertEqual(runner.calls, [])

    def test_review_head_not_matching_frozen_head_is_refused(self):
        with self.assertRaises(ReviewError) as ctx:
            combine(make_combiner(), codex=ok_outcome("CONTINUE", head=OTHER_HEAD),
                    claude=ok_outcome("CONTINUE", head=OTHER_HEAD))
        self.assertEqual(ctx.exception.code, "reviews_of_different_heads")

    def test_non_sha_frozen_head_is_refused(self):
        with self.assertRaises(ReviewError) as ctx:
            combine(make_combiner(), codex=ok_outcome("CONTINUE"),
                    claude=ok_outcome("CONTINUE"), inputs=make_inputs(frozen_head="HEAD"))
        self.assertEqual(ctx.exception.code, "head_not_frozen")

    def test_malformed_model_output_applies_no_refutation(self):
        runner = FakeRunner(stdout="not json at all")
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.FAIL)
        self.assertEqual(review.refutations_accepted, 0)

    def test_model_launch_exception_is_fail_safe(self):
        runner = FakeRunner(raises=FileNotFoundError("claude binary missing"))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        # A launch failure drops no finding -> stays FAIL (never PASS).
        self.assertEqual(review.verdict, rc.FAIL)

    def test_model_timeout_is_fail_safe(self):
        runner = FakeRunner(timed_out=True)
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.FAIL)


# --------------------------------------------------------------------------
# Scenario 5 (independence): never the producer or either reviewer
# --------------------------------------------------------------------------


class IndependenceTests(unittest.TestCase):
    def test_refuses_when_combiner_is_the_producer(self):
        runner = FakeRunner()
        combiner = make_combiner(runner, identity="claude-worker")
        with self.assertRaises(ReviewError) as ctx:
            combine(combiner, codex=ok_outcome("CONTINUE"),
                    claude=ok_outcome("CONTINUE"), producer="claude-worker")
        self.assertEqual(ctx.exception.code, "combiner_not_independent")
        self.assertEqual(runner.calls, [])

    def test_refuses_when_combiner_is_the_codex_reviewer(self):
        combiner = make_combiner(identity="codex-reviewer")
        with self.assertRaises(ReviewError) as ctx:
            combine(combiner, codex=ok_outcome("CONTINUE"), claude=ok_outcome("CONTINUE"),
                    codex_id="codex-reviewer")
        self.assertEqual(ctx.exception.code, "combiner_not_independent")

    def test_refuses_when_combiner_is_the_claude_reviewer(self):
        combiner = make_combiner(identity="claude-reviewer")
        with self.assertRaises(ReviewError) as ctx:
            combine(combiner, codex=ok_outcome("CONTINUE"), claude=ok_outcome("CONTINUE"),
                    claude_id="claude-reviewer")
        self.assertEqual(ctx.exception.code, "combiner_not_independent")

    def test_distinct_identity_is_allowed(self):
        review = combine(make_combiner(identity="fresh-combiner"),
                         codex=ok_outcome("CONTINUE"), claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.PASS)


# --------------------------------------------------------------------------
# Scenario 6 (settings): model required-no-default; switch default off
# --------------------------------------------------------------------------


class SettingsAndSwitchTests(unittest.TestCase):
    def test_config_defaults_off_and_model_unset(self):
        cfg = rc.ReviewCombinerConfig()
        self.assertFalse(cfg.enabled)
        self.assertEqual(cfg.model, "")

    def test_unset_model_refuses_before_any_process(self):
        runner = FakeRunner()
        combiner = rc.ReviewCombiner(
            "claude", config=rc.ReviewCombinerConfig(enabled=True, model=""),
            combiner_identity="combiner", runner=runner)
        with self.assertRaises(ReviewError) as ctx:
            combine(combiner, codex=ok_outcome("CONTINUE"), claude=ok_outcome("CONTINUE"))
        self.assertEqual(ctx.exception.code, "combiner_model_unset")
        self.assertEqual(runner.calls, [])

    def test_default_config_refuses_model_unset(self):
        combiner = rc.ReviewCombiner("claude", config=rc.ReviewCombinerConfig(),
                                     combiner_identity="combiner", runner=FakeRunner())
        with self.assertRaises(ReviewError) as ctx:
            combine(combiner, codex=ok_outcome("CONTINUE"), claude=ok_outcome("CONTINUE"))
        self.assertEqual(ctx.exception.code, "combiner_model_unset")

    def test_disabled_switch_refuses_even_with_a_model(self):
        runner = FakeRunner()
        combiner = make_combiner(runner, enabled=False)
        with self.assertRaises(ReviewError) as ctx:
            combine(combiner, codex=ok_outcome("CONTINUE"), claude=ok_outcome("CONTINUE"))
        self.assertEqual(ctx.exception.code, "combiner_disabled")
        self.assertEqual(runner.calls, [])

    def test_review_combiner_enabled_is_off_by_default(self):
        self.assertFalse(rc.review_combiner_enabled({}))
        self.assertFalse(rc.review_combiner_enabled({"review_combiner": {}}))
        self.assertFalse(rc.review_combiner_enabled({"review_combiner": {"enabled": False}}))
        self.assertFalse(rc.review_combiner_enabled({"review_combiner": {"enabled": "true"}}))
        self.assertFalse(rc.review_combiner_enabled({"review_combiner": {"enabled": 1}}))
        self.assertTrue(rc.review_combiner_enabled({"review_combiner": {"enabled": True}}))

    def test_from_mapping_strict_and_fail_closed(self):
        self.assertFalse(rc.ReviewCombinerConfig.from_mapping({}).enabled)
        self.assertEqual(rc.ReviewCombinerConfig.from_mapping({}).model, "")
        self.assertFalse(
            rc.ReviewCombinerConfig.from_mapping({"enabled": "true"}).enabled)
        self.assertTrue(
            rc.ReviewCombinerConfig.from_mapping({"enabled": True, "model": "m"}).enabled)
        with self.assertRaises(ReviewError):
            rc.ReviewCombinerConfig.from_mapping({"bogus": 1})
        with self.assertRaises(ReviewError):
            rc.ReviewCombinerConfig.from_mapping({"model": 5})
        with self.assertRaises(ReviewError):
            rc.ReviewCombinerConfig.from_mapping({"timeout_seconds": True})

    def test_model_invocation_uses_the_read_only_reviewer_argv(self):
        runner = FakeRunner()  # no stdout -> no refutation, but the model IS invoked
        combine(make_combiner(runner),
                codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                claude=ok_outcome("CONTINUE"))
        self.assertEqual(len(runner.calls), 1)
        argv = runner.calls[0]["argv"]
        self.assertIn("-p", argv)
        self.assertIn("--permission-mode", argv)
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "plan")
        self.assertEqual(argv[argv.index("--model") + 1], COMBINER_MODEL)

    def test_nothing_in_the_loop_calls_the_combiner(self):
        supervisor = REPO / "tools" / "agent_supervisor"
        for module in ("loop.py", "gate_wave.py", "codex_reviewer.py", "claude_reviewer.py"):
            src = (supervisor / module).read_text(encoding="utf-8")
            self.assertNotIn("review_combiner", src,
                             f"{module} must not reference the combiner (not wired in)")


# --------------------------------------------------------------------------
# Unit: verdict helper + diff parser
# --------------------------------------------------------------------------


class VerdictAndDiffUnitTests(unittest.TestCase):
    def test_review_verdict_mapping(self):
        self.assertEqual(rc.review_verdict(None), rc.UNVERIFIED)
        self.assertEqual(rc.review_verdict(fail_outcome()), rc.UNVERIFIED)
        self.assertEqual(rc.review_verdict(ok_outcome("CONTINUE")), rc.PASS)
        self.assertEqual(rc.review_verdict(ok_outcome("COMPLETE",
                         evidence_refs=[{"x": 1}])), rc.PASS)
        self.assertEqual(rc.review_verdict(ok_outcome("REVISE")), rc.FAIL)
        self.assertEqual(rc.review_verdict(
            ok_outcome("CONTINUE", blocking=[{"id": "x"}])), rc.FAIL)

    def test_diff_new_lines(self):
        lines = rc._parse_diff_new_lines(DIFF)
        self.assertEqual(lines["tools/foo.py"], frozenset({10, 11, 12, 13}))


if __name__ == "__main__":
    unittest.main()
