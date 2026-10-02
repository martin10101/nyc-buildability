#!/usr/bin/env python3
"""Review-combiner tests (owner directive D-091 T6, M0-T169; rework).

Covers every M0-T169 acceptance scenario with NO live provider call - the
combining model is never launched; a fake ``runner`` returns a controlled
``ProcessResult``. After the G3/G5 rework, model disputes are ADVISORY ONLY: a
dispute is recorded next to a blocking finding but NEVER removes it and NEVER
changes the combined verdict, which code computes as the worst of the two
reviews' verdicts. The tests prove, in code:

* primary: two well-formed reviews of one frozen head combine to the UNION of
  their findings, each tagged ``codex`` / ``claude``, with the worst verdict;
* never weaker (the core safety property): no dispute - not even a valid one, and
  not the universally-present frozen head SHA (G5 B1) nor a present-but-unrelated
  diff line / command substring (G5 B2) - ever drops a finding or moves a FAIL to
  PASS; FAIL + PASS is always FAIL;
* dispute recording: only a blocking finding can be disputed, and only with
  finding-bound evidence (file_line == the finding's own location in the diff; a
  >= 20-char command-output substring; a vouched non-head sha); the finding stays
  and the verdict is unchanged either way; ``verdict`` and ``unverified`` findings
  cannot be disputed at all;
* missing/ambiguous: a missing / malformed / empty / timed-out / raised-exception
  review is UNVERIFIED, never PASS, and cannot be disputed; different heads are
  refused;
* independence: the combiner refuses when its identity equals the producer's or
  either reviewer's, and an enabled combiner with an empty identity is refused;
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
VOUCHED_SHA = "d" * 40  # a supervisor-vouched sha that is NOT a prefix of HEAD
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
CMD_OUTPUT = "ran 43 tests in 0.40s :: all combiner tests passed cleanly\nexit code 0"
LONG_SUBSTRING = "all combiner tests passed cleanly"  # 33 chars, present in CMD_OUTPUT

# A blocking finding that reports its own location at tools/foo.py:12 (a real diff line).
BOUND_FINDING = {"id": "C1", "file": "tools/foo.py", "line": 12, "msg": "uses eval"}


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


def dispute_stdout(finding_id: str, evidence: dict, rationale: str = "disputed") -> str:
    return json.dumps({"disputes": [
        {"finding_id": finding_id, "evidence": evidence, "rationale": rationale}]})


def make_inputs(**over) -> rc.CombinerInputs:
    base = dict(frozen_head=HEAD, diff_text=DIFF, command_outputs=(CMD_OUTPUT,),
                extra_shas=frozenset({VOUCHED_SHA}))
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


def finding_by_id(review: rc.CombinedReview, fid: str) -> rc.CombinedFinding:
    return next(f for f in review.findings if f.finding_id == fid)


# --------------------------------------------------------------------------
# Scenario 1 (primary): union, source tags, worst verdict
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
        # Nothing disputable -> the combining model is never launched.
        self.assertEqual(runner.calls, [])

    def test_union_keeps_both_source_tags_and_worst_verdict(self):
        runner = FakeRunner()  # proposes nothing
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1", "msg": "codex"}]),
                         claude=ok_outcome("REVISE", blocking=[{"id": "L1", "msg": "claude"}]))
        sources = sorted(f.source for f in review.findings)
        self.assertEqual(sources, ["claude", "codex"])
        self.assertEqual(len(review.findings), 2)
        self.assertEqual(review.verdict, rc.FAIL)
        self.assertTrue(all(not f.disputed for f in review.findings))

    def test_combined_review_is_json_serializable_with_provenance(self):
        review = combine(make_combiner(),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        blob = json.dumps(review.to_dict())  # must not raise
        self.assertIn("\"source\": \"codex\"", blob)
        self.assertIn("\"frozen_head\": \"" + HEAD + "\"", blob)


# --------------------------------------------------------------------------
# Scenario 2 (never weaker): a dispute NEVER drops a finding or moves the verdict
# --------------------------------------------------------------------------


class NeverWeakerTests(unittest.TestCase):
    def test_fail_plus_pass_is_always_fail(self):
        # MUTATION: a FAIL review and a PASS review must never yield PASS.
        review = combine(make_combiner(),
                         codex=ok_outcome("REVISE", blocking=[{"id": "C1"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.codex_verdict, rc.FAIL)
        self.assertEqual(review.claude_verdict, rc.PASS)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_a_valid_dispute_does_not_drop_the_finding_or_flip_to_pass(self):
        # MUTATION: even a PERFECTLY VALID, finding-bound dispute is advisory -
        # the finding stays and a FAIL stays FAIL.
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 12}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        finding = finding_by_id(review, "codex:blocking:0")
        self.assertTrue(finding.disputed)          # recorded...
        self.assertIn(finding, review.findings)     # ...but still present
        self.assertEqual(review.disputes_recorded, 1)
        self.assertEqual(review.verdict, rc.FAIL)   # and the verdict is unchanged
        self.assertEqual(len(review.findings), 1)

    def test_halt_unsafe_with_head_sha_citation_stays_fail_finding_present(self):
        # G5 B1 red/green: the universally-present frozen head SHA (or a prefix)
        # must NOT drop a HALT_UNSAFE safety finding, and the verdict stays FAIL.
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "sha", "sha": "aaaaaaa"}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("HALT_UNSAFE", blocking=[{"id": "sqli", "msg": "x"}]),
                         claude=ok_outcome("CONTINUE"))
        finding = finding_by_id(review, "codex:blocking:0")
        self.assertFalse(finding.disputed)          # head-sha is not valid evidence
        self.assertEqual(review.disputes_rejected, 1)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_full_frozen_head_sha_citation_is_rejected(self):
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "sha", "sha": HEAD}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("HALT_UNSAFE", blocking=[{"id": "sqli"}]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(finding_by_id(review, "codex:blocking:0").disputed)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_present_but_unrelated_file_line_is_rejected(self):
        # G5 B2 red/green: a diff line that is PRESENT but not the finding's own
        # location does not record a dispute; finding present, verdict unchanged.
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 11}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("HALT_UNSAFE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        finding = finding_by_id(review, "codex:blocking:0")
        self.assertFalse(finding.disputed)
        self.assertEqual(review.disputes_rejected, 1)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_present_but_trivial_command_output_is_rejected(self):
        # A short (< 20 char) present substring is not valid dispute evidence.
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "command_output", "text": "passed"}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(finding_by_id(review, "codex:blocking:0").disputed)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_file_line_not_in_diff_is_rejected_even_if_it_equals_location(self):
        off_diff_finding = {"id": "C9", "file": "tools/foo.py", "line": 999}
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 999}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[off_diff_finding]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(finding_by_id(review, "codex:blocking:0").disputed)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_non_approve_verdict_without_findings_still_fails(self):
        review = combine(make_combiner(),
                         codex=ok_outcome("REVISE", blocking=[]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.FAIL)
        self.assertTrue(any(f.kind == "verdict" for f in review.findings))

    def test_verdict_finding_cannot_be_disputed(self):
        # A synthetic verdict finding is non-disputable; claude's blocking finding
        # makes the model run, and its dispute of the verdict finding is rejected.
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:verdict", {"type": "sha", "sha": VOUCHED_SHA}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[]),
                         claude=ok_outcome("REVISE", blocking=[BOUND_FINDING]))
        verdict_finding = finding_by_id(review, "codex:verdict")
        self.assertFalse(verdict_finding.disputable)
        self.assertFalse(verdict_finding.disputed)
        self.assertEqual(review.verdict, rc.FAIL)


# --------------------------------------------------------------------------
# Scenario 3 (dispute recording): valid finding-bound evidence is annotated
# --------------------------------------------------------------------------


class DisputeRecordingTests(unittest.TestCase):
    def test_bound_file_line_records_an_advisory_dispute(self):
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "file_line", "file": "tools/foo.py", "line": 12}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("REVISE", blocking=[{"id": "L1"}]))
        finding = finding_by_id(review, "codex:blocking:0")
        self.assertTrue(finding.disputed)
        self.assertEqual(finding.dispute["evidence"]["line"], 12)
        self.assertIn("ADVISORY", finding.dispute["note"])
        self.assertEqual(review.verdict, rc.FAIL)

    def test_long_command_output_substring_records_a_dispute(self):
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "command_output", "text": LONG_SUBSTRING}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        self.assertTrue(finding_by_id(review, "codex:blocking:0").disputed)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_vouched_non_head_sha_records_a_dispute(self):
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "sha", "sha": VOUCHED_SHA}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        self.assertTrue(finding_by_id(review, "codex:blocking:0").disputed)
        self.assertEqual(review.verdict, rc.FAIL)

    def test_sha_not_vouched_is_rejected(self):
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:0", {"type": "sha", "sha": "e" * 40}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(finding_by_id(review, "codex:blocking:0").disputed)

    def test_uncited_dispute_is_rejected(self):
        runner = FakeRunner(stdout=json.dumps(
            {"disputes": [{"finding_id": "codex:blocking:0", "rationale": "trust me"}]}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(finding_by_id(review, "codex:blocking:0").disputed)
        self.assertEqual(review.disputes_rejected, 1)

    def test_dispute_for_unknown_finding_is_ignored(self):
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:blocking:7", {"type": "sha", "sha": VOUCHED_SHA}))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        self.assertFalse(finding_by_id(review, "codex:blocking:0").disputed)
        self.assertEqual(review.disputes_rejected, 1)

    def test_evidence_supports_dispute_unit(self):
        inputs = make_inputs()
        bound = rc.CombinedFinding("codex:blocking:0", "codex", "blocking",
                                   BOUND_FINDING, disputable=True)
        noloc = rc.CombinedFinding("codex:blocking:0", "codex", "blocking",
                                   {"id": "C1"}, disputable=True)
        # file_line: must equal the finding's own location AND be in the diff.
        self.assertTrue(rc.evidence_supports_dispute(
            {"type": "file_line", "file": "tools/foo.py", "line": 12}, bound, inputs))
        self.assertFalse(rc.evidence_supports_dispute(
            {"type": "file_line", "file": "tools/foo.py", "line": 11}, bound, inputs))
        self.assertFalse(rc.evidence_supports_dispute(
            {"type": "file_line", "file": "tools/foo.py", "line": 12}, noloc, inputs))
        # command_output: >= 20 chars and present.
        self.assertTrue(rc.evidence_supports_dispute(
            {"type": "command_output", "text": LONG_SUBSTRING}, bound, inputs))
        self.assertFalse(rc.evidence_supports_dispute(
            {"type": "command_output", "text": "passed"}, bound, inputs))
        # sha: vouched non-head only; the head and any prefix are rejected (G5 B1).
        self.assertTrue(rc.evidence_supports_dispute(
            {"type": "sha", "sha": VOUCHED_SHA}, bound, inputs))
        self.assertFalse(rc.evidence_supports_dispute(
            {"type": "sha", "sha": "aaaaaaa"}, bound, inputs))
        self.assertFalse(rc.evidence_supports_dispute(
            {"type": "sha", "sha": HEAD}, bound, inputs))
        # Malformed / unknown kinds.
        self.assertFalse(rc.evidence_supports_dispute({"type": "guess"}, bound, inputs))
        self.assertFalse(rc.evidence_supports_dispute("nope", bound, inputs))


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

    def test_unverified_finding_cannot_be_disputed(self):
        # claude blocking finding makes the model run; the model tries (illegit.)
        # to dispute the unverified finding and is rejected.
        runner = FakeRunner(stdout=dispute_stdout(
            "codex:unverified", {"type": "sha", "sha": VOUCHED_SHA}))
        review = combine(make_combiner(runner), codex=None,
                         claude=ok_outcome("REVISE", blocking=[BOUND_FINDING]))
        unverified = [f for f in review.findings if f.kind == "unverified"]
        self.assertTrue(unverified and not unverified[0].disputed)
        self.assertEqual(review.verdict, rc.UNVERIFIED)
        self.assertEqual(review.disputes_rejected, 1)

    def test_missing_review_only_finding_skips_the_model(self):
        runner = FakeRunner()
        review = combine(make_combiner(runner), codex=None,
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.UNVERIFIED)
        self.assertEqual(runner.calls, [])

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

    def test_malformed_model_output_records_no_dispute(self):
        runner = FakeRunner(stdout="not json at all")
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.FAIL)
        self.assertEqual(review.disputes_recorded, 0)

    def test_model_launch_exception_is_fail_safe(self):
        runner = FakeRunner(raises=FileNotFoundError("claude binary missing"))
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
                         claude=ok_outcome("CONTINUE"))
        self.assertEqual(review.verdict, rc.FAIL)
        self.assertFalse(finding_by_id(review, "codex:blocking:0").disputed)

    def test_model_timeout_is_fail_safe(self):
        runner = FakeRunner(timed_out=True)
        review = combine(make_combiner(runner),
                         codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
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

    def test_enabled_combiner_with_empty_identity_is_refused(self):
        runner = FakeRunner()
        combiner = make_combiner(runner, identity="")
        with self.assertRaises(ReviewError) as ctx:
            combine(combiner, codex=ok_outcome("CONTINUE"), claude=ok_outcome("CONTINUE"))
        self.assertEqual(ctx.exception.code, "combiner_identity_required")
        self.assertEqual(runner.calls, [])

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
        runner = FakeRunner()  # no stdout -> no dispute, but the model IS invoked
        combine(make_combiner(runner),
                codex=ok_outcome("REVISE", blocking=[BOUND_FINDING]),
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

    def test_worst_verdict(self):
        self.assertEqual(rc.worst_verdict(rc.PASS, rc.PASS), rc.PASS)
        self.assertEqual(rc.worst_verdict(rc.PASS, rc.FAIL), rc.FAIL)
        self.assertEqual(rc.worst_verdict(rc.FAIL, rc.UNVERIFIED), rc.UNVERIFIED)
        self.assertEqual(rc.worst_verdict(rc.UNVERIFIED, rc.PASS), rc.UNVERIFIED)

    def test_diff_new_lines(self):
        lines = rc._parse_diff_new_lines(DIFF)
        self.assertEqual(lines["tools/foo.py"], frozenset({10, 11, 12, 13}))


if __name__ == "__main__":
    unittest.main()
