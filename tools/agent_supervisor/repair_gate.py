#!/usr/bin/env python3
"""Root-cause repair gate: acceptance-time record protocols (D-024 sections 9 + 12).

Supervisor-freeze qualifying evidence: **D-024-R105** (Phase G, packet-named;
task M0-T095). SHADOW-ONLY like the rest of the package: this module is
deterministic policy over frozen records - it runs no subprocess, contacts no
remote, performs no external effect, and takes no wall-clock input (expiry
consumes an injected clock/milestone fact, never `datetime.now`).

One responsibility: the deterministic records and predicates the review/acceptance
seam consumes for D-024 Phase G, each a closed, typed, individually testable
protocol:

* **R076 `RepairRecord`** - reproduce-first defect protocol: root cause and owning
  boundary, explicit direct-repair vs bounded-replacement mode, one authoritative
  path with obsolete logic removed and unreachability proven via recorded
  search/graph evidence, a regression test bound to the defect, and a typed
  patch-stacking rejection (R078's "unjustified new if/retry/wrapper/compatibility
  adapter/fallback around a known-bad path"). The gate never authorizes a broad
  rewrite and never accepts deletion of unrelated working code.
* **R078 checkpoint questions** - a CLOSED tuple of question keys answered at every
  Codex review checkpoint; a missing/blank/unknown key refuses mechanically (never
  free-prose evaluation), and complete answers yield a typed disposition that still
  requires the independent review PASS (the unit-H1 `bridge_output_disposition`
  pattern - never auto-accept).
* **R077 `CompatibilityException`** - a temporary dual path needs every tracked
  field (reason, owner, measurable removal condition, telemetry, removal task +
  deadline/milestone, anti-default tests); one typed refusal per missing field, and
  an EXPIRED exception blocks task acceptance (unknown expiry fails closed).
* **R091 consolidated-round / frozen-identity discipline** - a review binds to the
  frozen content identity it examined; an identity change invalidates the review
  (16.8 E7), and the correction-round record shape refuses drip-feeding (per-finding
  fixes moving identity repeatedly; 16.8 E14).
* **PR-snapshot classification (16.8 E10/E11)** - expected-open / deliberately-held,
  pre-existing, stale, and current-task PRs are classified SEPARATELY under a
  closed vocabulary; no classification carries a close/merge/redefine action, and a
  pre-existing PR is never merge-eligible from a snapshot (D-024-R010 - merging
  stays behind `github_flow`'s S5.5 evaluation plus explicit owner authorization).
* **Supervisor-freeze citation (R017; 16.8 E13)** - a supervisor change record must
  cite a captured `D-024-R###` id in BOTH the task packet and the commit message;
  an uncited record is refused.

The review-packet wiring is record-only: `checkpoint_section` builds a bounded
structured section for `evidence.build_packet(extra_sections=...)`; nothing here
invokes a reviewer or mutates review state.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Mapping, Sequence

from . import redaction
from .models import digest_of
from .policy import CONTROLLER_PATHS, path_matches

REPAIR_GATE_SCHEMA_VERSION = "1.0.0"


class RepairGateError(Exception):
    """A repair-gate input was malformed. Fail closed; never assume permissive."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# ==========================================================================
# R076 - the RepairRecord protocol (root-cause, replace-not-layer)
# ==========================================================================

MODE_DIRECT_REPAIR = "direct_repair"
MODE_BOUNDED_REPLACEMENT = "bounded_replacement"
#: The explicit repair-mode choice R076 requires. CLOSED: an unknown mode is a
#: malformed record, not a third lane.
REPAIR_MODES: tuple[str, ...] = (MODE_DIRECT_REPAIR, MODE_BOUNDED_REPLACEMENT)

#: The R078 layer kinds whose unjustified addition around a known-bad path is
#: patch stacking ("a new if/retry/wrapper/compatibility adapter/fallback").
LAYER_KINDS: tuple[str, ...] = (
    "wrapper", "retry", "fallback", "flag", "branch", "compatibility_adapter")

#: Where recorded unreachability evidence may come from (R076 "search/graph
#: evidence"): repository search and the SHA-stamped homegrown code-graph index.
EVIDENCE_TOOLS: tuple[str, ...] = ("search", "code_graph")


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise RepairGateError(code, message)


@dataclasses.dataclass(frozen=True)
class AddedLayer:
    """One new wrapper/retry/fallback/flag/branch/adapter the fix introduced."""

    kind: str
    around_known_bad_path: bool
    justification: str = ""

    def __post_init__(self) -> None:
        _require(self.kind in LAYER_KINDS, "unknown_layer_kind",
                 f"{self.kind!r} is not a recognized layer kind; known kinds: "
                 f"{list(LAYER_KINDS)}")


@dataclasses.dataclass(frozen=True)
class UnreachabilityEvidence:
    """One recorded search/graph query proving obsolete logic is unreachable.

    The QUERY AND ITS FINDING are recorded in the repair record (R076: evidence,
    not assertion); the gate validates the record, it does not re-run the query.
    """

    tool: str
    query: str
    finding: str

    def __post_init__(self) -> None:
        _require(self.tool in EVIDENCE_TOOLS, "unknown_evidence_tool",
                 f"{self.tool!r} is not a recognized evidence tool; known tools: "
                 f"{list(EVIDENCE_TOOLS)}")
        _require(bool(self.query.strip()) and bool(self.finding.strip()),
                 "empty_evidence", "an unreachability evidence entry records the "
                 "exact query and its finding; blank entries prove nothing")


@dataclasses.dataclass(frozen=True)
class RepairRecord:
    """The R076 reproduce-first record for one defect task.

    Facts (test-exists, callers-still-reachable, ...) are supplied by the evidence
    collector / recorded evidence, never by a model's description of them - the
    same posture as `github_flow.MergeRequest`. Construction validates SHAPE only;
    policy verdicts come from `evaluate_repair`.
    """

    task_id: str
    defect_id: str
    #: Reproduce-first: a reproduction reference OR a falsifiable failure condition.
    reproduction_ref: str = ""
    falsifiable_failure_condition: str = ""
    root_cause: str = ""
    owning_boundary: str = ""
    preserved_behavior: str = ""
    #: The regression test bound to the defect ("fails for the right reason").
    regression_test_id: str = ""
    regression_test_exists: bool = False
    regression_test_references_defect: bool = False
    regression_failure_condition: str = ""
    mode: str = MODE_DIRECT_REPAIR
    #: Bounded-replacement proof set (ignored for a direct repair).
    obsolete_implementation_removed: bool = False
    dead_callers_removed: bool = False
    duplicate_fallbacks_removed: bool = False
    unreachability_evidence: tuple[UnreachabilityEvidence, ...] = ()
    #: Search/graph findings that name STILL-REACHABLE stale callers or duplicate
    #: fallbacks. Non-empty refuses "one authoritative path" until resolved.
    reachable_stale_callers: tuple[str, ...] = ()
    one_authoritative_path: bool = False
    added_layers: tuple[AddedLayer, ...] = ()
    #: Working code the fix deletes that is UNRELATED to the defect (T8).
    unrelated_deletions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require(bool(self.task_id.strip()) and bool(self.defect_id.strip()),
                 "missing_identity",
                 "a repair record names the task and the defect it repairs")
        _require(self.mode in REPAIR_MODES, "unknown_repair_mode",
                 f"{self.mode!r} is not an explicit repair mode; R076 requires "
                 f"choosing one of {list(REPAIR_MODES)}")
        for layer in self.added_layers:
            _require(isinstance(layer, AddedLayer), "malformed_layer",
                     "added_layers entries must be AddedLayer records")
        for entry in self.unreachability_evidence:
            _require(isinstance(entry, UnreachabilityEvidence), "malformed_evidence",
                     "unreachability_evidence entries must be UnreachabilityEvidence")

    def record_digest(self) -> str:
        """The content identity of this record (for packet/report binding)."""
        return digest_of(dataclasses.asdict(self))


@dataclasses.dataclass(frozen=True)
class RepairFinding:
    """One named repair-gate predicate outcome (mirrors `MergeCondition`)."""

    name: str
    ok: bool
    reason_code: str
    detail: str


@dataclasses.dataclass(frozen=True)
class RepairEvaluation:
    """The combined R076 verdict. `accepted` is the AND of every predicate.

    "Accepted" means the RECORD passes the root-cause gate; task acceptance still
    requires the R078 checkpoint disposition and the independent review PASS.
    """

    accepted: bool
    findings: tuple[RepairFinding, ...]

    def refusals(self) -> tuple[RepairFinding, ...]:
        return tuple(f for f in self.findings if not f.ok)

    def refusal_codes(self) -> tuple[str, ...]:
        return tuple(f.reason_code for f in self.findings if not f.ok)


def _finding(name: str, ok: bool, ok_code: str, ok_detail: str,
             fail_code: str, fail_detail: str) -> RepairFinding:
    return RepairFinding(name, ok, ok_code if ok else fail_code,
                         ok_detail if ok else fail_detail)


def check_reproduction(record: RepairRecord) -> RepairFinding:
    ok = bool(record.reproduction_ref.strip()) or \
        bool(record.falsifiable_failure_condition.strip())
    return _finding("reproduction_established", ok,
                    "reproduction_established",
                    "the defect is reproduced or has a falsifiable failure condition",
                    "defect_not_reproduced",
                    "R076 is reproduce-first: record a reproduction reference or a "
                    "falsifiable failure condition before any repair")


def check_root_cause(record: RepairRecord) -> RepairFinding:
    ok = bool(record.root_cause.strip()) and bool(record.owning_boundary.strip())
    return _finding("root_cause_identified", ok,
                    "root_cause_identified",
                    "the root cause and the smallest owning boundary are named",
                    "root_cause_missing",
                    "the record must name the root cause and the smallest owning "
                    "architectural boundary, not just the symptom")


def check_preserved_behavior(record: RepairRecord) -> RepairFinding:
    ok = bool(record.preserved_behavior.strip())
    return _finding("preserved_behavior_characterized", ok,
                    "preserved_behavior_characterized",
                    "the correct behavior to preserve is characterized",
                    "preserved_behavior_missing",
                    "R076 requires characterizing the correct behavior the repair "
                    "must preserve")


def check_regression_test(record: RepairRecord) -> RepairFinding:
    """T5: the regression test exists, references the defect, and states the
    condition under which it fails - "failing for the right reason"."""
    ok = (bool(record.regression_test_id.strip())
          and record.regression_test_exists
          and record.regression_test_references_defect
          and bool(record.regression_failure_condition.strip()))
    return _finding("regression_test_bound", ok,
                    "regression_test_bound",
                    f"regression test {record.regression_test_id!r} exists, references "
                    f"the defect, and records its failure condition",
                    "regression_test_unbound",
                    "a regression test failing for the defect for the right reason is "
                    "unproven: it must exist, reference the defect, and record the "
                    "condition under which it fails if the fix is removed")


def check_replacement_proof(record: RepairRecord) -> RepairFinding:
    """T3: bounded replacement must PROVE removal + unreachability; a direct
    repair on sound structure owes no removal proof (T2 - no forced rewrite)."""
    if record.mode == MODE_DIRECT_REPAIR:
        return RepairFinding("replacement_proof", True, "direct_repair_mode",
                             "direct repair on sound structure; no removal proof is "
                             "demanded and no broad rewrite is required (R076/R078)")
    removed = (record.obsolete_implementation_removed
               and record.dead_callers_removed
               and record.duplicate_fallbacks_removed)
    ok = removed and bool(record.unreachability_evidence)
    return _finding("replacement_proof", ok,
                    "replacement_proven",
                    f"obsolete implementation, dead callers, and duplicate fallbacks "
                    f"removed; unreachability proven by "
                    f"{len(record.unreachability_evidence)} recorded search/graph entries",
                    "replacement_unproven",
                    "bounded replacement requires removing the obsolete implementation, "
                    "dead callers, and duplicate fallbacks AND recorded search/graph "
                    "evidence that the old path is unreachable")


def check_one_authoritative_path(record: RepairRecord) -> RepairFinding:
    """T4: recorded evidence naming still-reachable stale callers or duplicate
    fallbacks refuses "one authoritative path" until they are resolved."""
    if record.reachable_stale_callers:
        return RepairFinding(
            "one_authoritative_path", False, "stale_callers_reachable",
            f"search/graph evidence names still-reachable stale callers or duplicate "
            f"fallbacks: {sorted(record.reachable_stale_callers)}; there is not one "
            f"authoritative path until they are resolved")
    return _finding("one_authoritative_path", bool(record.one_authoritative_path),
                    "one_authoritative_path",
                    "the fix leaves exactly one authoritative path",
                    "authoritative_path_unconfirmed",
                    "the record does not establish one authoritative path")


def check_no_patch_stacking(record: RepairRecord) -> RepairFinding:
    """T1/R078: an unjustified new layer around a known-bad path is patch stacking."""
    unjustified = sorted(
        layer.kind for layer in record.added_layers
        if layer.around_known_bad_path and not layer.justification.strip())
    ok = not unjustified
    return _finding("no_patch_stacking", ok,
                    "no_patch_stacking",
                    "no unjustified layer was added around a known-bad path",
                    "patch_stacking",
                    f"new {unjustified} layer(s) added around a known-bad path without "
                    f"justification; R076/R078 reject band-aid stacking - repair the "
                    f"root cause or justify the layer explicitly")


def check_no_unrelated_deletion(record: RepairRecord) -> RepairFinding:
    """T8: the root-cause lane never authorizes deleting unrelated working code."""
    ok = not record.unrelated_deletions
    return _finding("no_unrelated_deletion", ok,
                    "no_unrelated_deletion",
                    "the fix deletes no unrelated working code",
                    "unrelated_working_code_deleted",
                    f"the fix deletes unrelated working code "
                    f"{sorted(record.unrelated_deletions)}; R076 authorizes neither "
                    f"broad rewrites nor unrelated deletion")


#: Every R076 predicate, in review order. Each is individually testable and has
#: both an ok and a fail direction (Lean B6 one-invariant-per-test).
REPAIR_CHECKS = (
    check_reproduction,
    check_root_cause,
    check_preserved_behavior,
    check_regression_test,
    check_replacement_proof,
    check_one_authoritative_path,
    check_no_patch_stacking,
    check_no_unrelated_deletion,
)


def evaluate_repair(record: RepairRecord) -> RepairEvaluation:
    """Evaluate the full R076 gate. `accepted` only when EVERY predicate holds."""
    findings = tuple(check(record) for check in REPAIR_CHECKS)
    return RepairEvaluation(accepted=all(f.ok for f in findings), findings=findings)


# ==========================================================================
# R078 - the closed checkpoint-question set
# ==========================================================================

#: The R078 questions, as DATA (a closed tuple of keys - never free-prose
#: evaluation). Order is the directive's order.
CHECKPOINT_QUESTIONS: tuple[str, ...] = (
    "root_cause",
    "old_logic_removed_or_covered",
    "one_authoritative_path",
    "failing_if_removed_test",
    "wrapper_justification",
    "retained_behavior_removal_plan",
)

CHECKPOINT_REFUSED = "checkpoint_refused"
CHECKPOINT_ANSWERS_COMPLETE = "checkpoint_answers_complete"


@dataclasses.dataclass(frozen=True)
class CheckpointEvaluation:
    """The mechanical verdict on one R078 answer set."""

    outcome: str
    missing_questions: tuple[str, ...]
    unknown_questions: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return self.outcome == CHECKPOINT_ANSWERS_COMPLETE


def evaluate_checkpoint_answers(answers: Mapping[str, str]) -> CheckpointEvaluation:
    """T9: refuse mechanically on any missing/blank/unknown question key.

    A blank or whitespace answer counts as missing (an evasive non-answer). An
    unknown key is refused too: the question set is CLOSED, so an answer set
    cannot substitute its own questions for the directive's.
    """
    missing = tuple(key for key in CHECKPOINT_QUESTIONS
                    if not str(answers.get(key, "") or "").strip())
    unknown = tuple(sorted(set(answers) - set(CHECKPOINT_QUESTIONS)))
    if missing or unknown:
        return CheckpointEvaluation(CHECKPOINT_REFUSED, missing, unknown)
    return CheckpointEvaluation(CHECKPOINT_ANSWERS_COMPLETE, (), ())


DISPOSITION_REVIEW_REQUIRED = "review_required"
DISPOSITION_ACCEPTED_BY_REVIEW = "accepted_by_review"
DISPOSITION_REJECTED = "rejected"


def repair_gate_disposition(
        checkpoint: CheckpointEvaluation,
        review_verdict: Mapping[str, Any] | None) -> tuple[str, str]:
    """The unit-H1 disposition pattern: complete answers NEVER auto-accept.

    Incomplete answers reject outright. Complete answers stay `review_required`
    until an explicit independent PASS; FAIL/BLOCKED rejects; an unrecognized
    verdict fails closed to `review_required`.
    """
    if not checkpoint.complete:
        return (DISPOSITION_REJECTED,
                f"the R078 checkpoint refused: missing "
                f"{list(checkpoint.missing_questions)}, unknown "
                f"{list(checkpoint.unknown_questions)}; incomplete answers never "
                f"reach acceptance")
    if not isinstance(review_verdict, Mapping):
        return (DISPOSITION_REVIEW_REQUIRED,
                "checkpoint answers are complete but carry no independent review "
                "verdict; completeness is never acceptance (D-024-R078)")
    verdict = str(review_verdict.get("verdict") or "").strip().upper()
    if verdict == "PASS":
        return (DISPOSITION_ACCEPTED_BY_REVIEW,
                "complete R078 answers passed the independent review path")
    if verdict in ("FAIL", "BLOCKED"):
        return (DISPOSITION_REJECTED,
                f"the independent review path rejected the checkpoint ({verdict})")
    return (DISPOSITION_REVIEW_REQUIRED,
            f"unrecognized review verdict {verdict!r}; the checkpoint stays "
            f"unaccepted until the review path rules (fail closed)")


# ==========================================================================
# R077 - CompatibilityException with expiry-blocks-acceptance
# ==========================================================================


@dataclasses.dataclass(frozen=True)
class CompatibilityException:
    """One tracked temporary dual path (R077). Construction is shape-only;
    completeness verdicts come from `evaluate_compatibility_exception`."""

    exception_id: str
    reason: str = ""
    owner: str = ""
    removal_condition: str = ""
    telemetry_key: str = ""
    removal_task_id: str = ""
    #: An ISO-8601 UTC deadline ("2026-09-30T00:00:00+00:00") or a milestone id.
    removal_deadline: str = ""
    anti_default_tests: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require(bool(self.exception_id.strip()), "missing_exception_id",
                 "a compatibility exception must be identifiable")


#: field name -> the typed refusal code its absence produces (one refusal per
#: missing field - the Lean B6 one-invariant-per-test discipline).
COMPATIBILITY_REQUIRED_FIELDS: Mapping[str, str] = {
    "reason": "missing_reason",
    "owner": "missing_owner",
    "removal_condition": "missing_removal_condition",
    "telemetry_key": "missing_telemetry_key",
    "removal_task_id": "missing_removal_task",
    "removal_deadline": "missing_removal_deadline",
    "anti_default_tests": "missing_anti_default_tests",
}


def evaluate_compatibility_exception(
        exc: CompatibilityException) -> tuple[RepairFinding, ...]:
    """T6: one typed refusal per missing R077 field; all-present -> a single OK."""
    findings: list[RepairFinding] = []
    for field, code in COMPATIBILITY_REQUIRED_FIELDS.items():
        value = getattr(exc, field)
        present = bool(value) if isinstance(value, tuple) else bool(str(value).strip())
        if not present:
            findings.append(RepairFinding(
                f"compatibility_{field}", False, code,
                f"compatibility exception {exc.exception_id!r} lacks {field!r}; R077 "
                f"requires every tracked field before a dual path may exist"))
    if findings:
        return tuple(findings)
    return (RepairFinding("compatibility_complete", True, "compatibility_complete",
                          f"compatibility exception {exc.exception_id!r} carries every "
                          f"R077 field"),)


_ISO_DEADLINE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def compatibility_expired(exc: CompatibilityException, *, now_utc: str = "",
                          milestone_reached: bool | None = None) -> bool:
    """Whether the exception's deadline has passed - from INJECTED facts only.

    An ISO deadline compares lexicographically against the injected `now_utc`
    (both are fixed-format UTC, so string order is time order). A milestone
    deadline consumes the injected `milestone_reached` fact. When the caller
    supplies no fact that can decide the deadline, the answer is UNKNOWN and this
    RAISES - fail closed; wall-clock is never consulted.
    """
    deadline = exc.removal_deadline.strip()
    _require(bool(deadline), "no_deadline",
             f"compatibility exception {exc.exception_id!r} has no removal deadline; "
             f"evaluate completeness (R077) before expiry")
    if _ISO_DEADLINE_RE.match(deadline):
        _require(bool(now_utc.strip()), "expiry_fact_missing",
                 f"deciding the ISO deadline {deadline!r} needs the injected now_utc "
                 f"fact; wall-clock is never consulted")
        return now_utc >= deadline
    _require(milestone_reached is not None, "expiry_fact_missing",
             f"deciding the milestone deadline {deadline!r} needs the injected "
             f"milestone_reached fact; wall-clock is never consulted")
    return bool(milestone_reached)


@dataclasses.dataclass(frozen=True)
class AcceptanceGate:
    """Whether task acceptance may proceed past the compatibility register (T7)."""

    blocked: bool
    expired_exception_ids: tuple[str, ...]
    detail: str


def evaluate_acceptance(
        exceptions: Sequence[CompatibilityException], *, now_utc: str = "",
        milestone_reached_by_id: Mapping[str, bool] | None = None) -> AcceptanceGate:
    """T7: any ACTIVE compatibility exception past its deadline BLOCKS acceptance.

    Milestone facts are injected per exception id; an exception whose expiry
    cannot be decided from the injected facts blocks too (fail closed).
    """
    facts = dict(milestone_reached_by_id or {})
    expired: list[str] = []
    for exc in exceptions:
        try:
            if compatibility_expired(exc, now_utc=now_utc,
                                     milestone_reached=facts.get(exc.exception_id)):
                expired.append(exc.exception_id)
        except RepairGateError:
            expired.append(exc.exception_id)  # undecidable expiry fails closed
    if expired:
        return AcceptanceGate(
            True, tuple(expired),
            f"acceptance is blocked: compatibility exception(s) {sorted(expired)} are "
            f"past their removal deadline or undecidable (R077 - expiry blocks "
            f"acceptance)")
    return AcceptanceGate(False, (), "no compatibility exception blocks acceptance")


# ==========================================================================
# R091 - frozen-identity review validity + the consolidated correction round
# ==========================================================================


@dataclasses.dataclass(frozen=True)
class ReviewValidity:
    """Whether a review recorded at one frozen identity still applies (16.8 E7)."""

    valid: bool
    reason_code: str
    detail: str


def review_still_valid(*, review_identity: str, live_identity: str) -> ReviewValidity:
    """A review binds to the exact frozen identity it examined (R091).

    Any identity change invalidates it - a re-review is required; blank
    identities never validate (fail closed).
    """
    review = review_identity.strip()
    live = live_identity.strip()
    if not review or not live:
        return ReviewValidity(False, "identity_unknown",
                              "a review or live identity is blank; validity cannot be "
                              "established and the review does not apply (fail closed)")
    if review == live:
        return ReviewValidity(True, "identity_unchanged",
                              f"the frozen identity {live!r} is the one the review "
                              f"examined")
    return ReviewValidity(False, "identity_changed_re_review_required",
                          f"the frozen identity moved from {review!r} to {live!r}; the "
                          f"prior review is invalidated and a re-review is required "
                          f"(D-024-R091)")


@dataclasses.dataclass(frozen=True)
class CorrectionRoundResult:
    """The R091 consolidated-round verdict (16.8 E14)."""

    ok: bool
    reason_code: str
    detail: str
    re_review_identity: str = ""


def evaluate_correction_round(
        *, review_identity: str, finding_ids: Sequence[str],
        correction_identities: Sequence[str]) -> CorrectionRoundResult:
    """R091: findings from all reviewers consolidate into ONE correction round.

    The record carries the identity each correction landed at. More than one
    distinct post-review identity is drip-feeding (per-finding fixes moving the
    identity repeatedly) and is refused by shape. The single valid shape:
    all findings -> one new frozen identity -> re-review at that identity.
    """
    review = review_identity.strip()
    if not review:
        return CorrectionRoundResult(False, "identity_unknown",
                                     "the reviewed frozen identity is blank; a "
                                     "correction round cannot be bound (fail closed)")
    if not finding_ids:
        return CorrectionRoundResult(True, "no_findings",
                                     "no findings to correct; no round is needed",
                                     re_review_identity=review)
    distinct = tuple(dict.fromkeys(i.strip() for i in correction_identities if i.strip()))
    if len(distinct) > 1:
        return CorrectionRoundResult(
            False, "drip_feeding",
            f"corrections moved the frozen identity {len(distinct)} times "
            f"({list(distinct)}); R091 requires ONE consolidated correction round at "
            f"a single new frozen identity, never per-finding identity churn")
    if not distinct:
        return CorrectionRoundResult(False, "findings_unaddressed",
                                     f"{len(finding_ids)} finding(s) have no recorded "
                                     f"correction identity; the round is incomplete")
    if distinct[0] == review:
        return CorrectionRoundResult(False, "correction_did_not_move_identity",
                                     "the correction round claims the SAME frozen "
                                     "identity the review examined; corrected content "
                                     "must freeze a new identity for re-review")
    return CorrectionRoundResult(
        True, "consolidated_round",
        f"all {len(finding_ids)} findings consolidated into one correction round at "
        f"{distinct[0]!r}; a re-review at that identity is required",
        re_review_identity=distinct[0])


# ==========================================================================
# 16.8 E10/E11 - PR-snapshot classification (record-only, effect-free)
# ==========================================================================

PR_CLASS_TASK = "task_pr"
PR_CLASS_PRE_EXISTING = "pre_existing"
PR_CLASS_EXPECTED_OPEN = "expected_open_held"
PR_CLASS_STALE = "stale_candidate"
#: CLOSED classification vocabulary (16.8 E11).
PR_CLASSES: tuple[str, ...] = (
    PR_CLASS_TASK, PR_CLASS_PRE_EXISTING, PR_CLASS_EXPECTED_OPEN, PR_CLASS_STALE)

#: The ONLY action any classification may carry: routing the current task's own PR
#: into `github_flow`'s S5.5 evaluation. No class ever carries close/merge/
#: redefine - a snapshot observes, it never actions (E11), and merging stays
#: behind `github_flow.evaluate_merge` + explicit owner authority (E10, R010).
ACTION_EVALUATE_VIA_GITHUB_FLOW = "evaluate_via_github_flow"

#: Days of inactivity after which a non-held foreign PR is FLAGGED stale. POLICY,
#: injected-fact driven: the age itself arrives as `days_since_update`, never read
#: from a clock here.
DEFAULT_STALE_AFTER_DAYS = 30


@dataclasses.dataclass(frozen=True)
class PRSnapshot:
    """One observed pull request, as injected FACTS (no live GitHub read here)."""

    number: int
    opened_by_task_id: str
    current_task_id: str
    #: An owner directive/hold names this PR as deliberately unmerged (e.g. #241).
    owner_hold: bool = False
    #: Injected age fact; None = unknown (a snapshot never reads a clock).
    days_since_update: int | None = None

    def __post_init__(self) -> None:
        _require(self.number > 0, "bad_pr_number", "a PR snapshot names a real PR")
        _require(bool(self.current_task_id.strip()), "missing_task_context",
                 "a PR snapshot records which task observed it")


@dataclasses.dataclass(frozen=True)
class PRClassification:
    """The classification record. `allowed_actions` is () for every class except
    the current task's own PR - a snapshot never closes/merges/redefines."""

    pr_number: int
    pr_class: str
    allowed_actions: tuple[str, ...]
    detail: str

    @property
    def effect_free(self) -> bool:
        return all(a == ACTION_EVALUATE_VIA_GITHUB_FLOW for a in self.allowed_actions)


def classify_pr(snapshot: PRSnapshot, *,
                stale_after_days: int = DEFAULT_STALE_AFTER_DAYS) -> PRClassification:
    """Classify one observed PR under the closed E11 vocabulary.

    Precedence: an owner hold wins (deliberately unmerged, NEVER actionable);
    then the current task's own PR (actionable only THROUGH github_flow's S5.5
    evaluation); then a foreign/pre-existing PR (never merged without explicit
    owner authorization - which is an OWNER act outside any snapshot, R010);
    a long-inactive pre-existing PR is additionally flagged stale, still with no
    action. Unknown age never makes a PR stale (fail toward the quieter class).
    """
    if snapshot.owner_hold:
        return PRClassification(
            snapshot.number, PR_CLASS_EXPECTED_OPEN, (),
            f"PR #{snapshot.number} is deliberately unmerged under an owner hold; it "
            f"is classified separately and no snapshot may close, merge, or redefine "
            f"it (D-024-R010)")
    if snapshot.opened_by_task_id.strip() and \
            snapshot.opened_by_task_id == snapshot.current_task_id:
        return PRClassification(
            snapshot.number, PR_CLASS_TASK, (ACTION_EVALUATE_VIA_GITHUB_FLOW,),
            f"PR #{snapshot.number} belongs to the current task; any merge still "
            f"passes github_flow's full S5.5 evaluation")
    if snapshot.days_since_update is not None and \
            snapshot.days_since_update >= stale_after_days:
        return PRClassification(
            snapshot.number, PR_CLASS_STALE, (),
            f"PR #{snapshot.number} is a pre-existing PR inactive for "
            f"{snapshot.days_since_update} day(s); it is FLAGGED for the owner and "
            f"never silently closed, merged, or redefined")
    return PRClassification(
        snapshot.number, PR_CLASS_PRE_EXISTING, (),
        f"PR #{snapshot.number} pre-exists this task; it is never merged without "
        f"explicit owner authorization covering that merge (D-024-R010)")


# ==========================================================================
# R017 / 16.8 E13 - supervisor-freeze citation
# ==========================================================================

#: A captured D-024 requirement id, the freeze rule's qualifying-evidence shape.
FREEZE_CITATION_RE = re.compile(r"D-024-R\d{3}")


@dataclasses.dataclass(frozen=True)
class SupervisorChangeRecord:
    """One proposed supervisor change: what it touches and how it is cited."""

    touched_paths: tuple[str, ...]
    packet_citation: str = ""
    commit_message: str = ""


def touches_supervisor(paths: Sequence[str]) -> bool:
    """Whether any path is controller code (reuses the policy CONTROLLER_PATHS)."""
    return any(
        path_matches(str(p).replace("\\", "/"), pattern)
        for p in paths for pattern in CONTROLLER_PATHS)


def validate_freeze_citation(record: SupervisorChangeRecord) -> tuple[RepairFinding, ...]:
    """E13: a supervisor change record without a `D-024-R###` citation in BOTH the
    task packet and the commit message is REJECTED (R017; supervisor-freeze §3).

    A change touching no supervisor path owes no citation.
    """
    if not touches_supervisor(record.touched_paths):
        return (RepairFinding("freeze_citation", True, "no_supervisor_path",
                              "the change touches no supervisor path; the freeze "
                              "citation duty does not apply"),)
    findings: list[RepairFinding] = []
    if not FREEZE_CITATION_RE.search(record.packet_citation):
        findings.append(RepairFinding(
            "freeze_citation_packet", False, "missing_freeze_citation_packet",
            "the supervisor change's task packet cites no captured D-024-R### "
            "qualifying-evidence id (R017; supervisor-freeze rule §3)"))
    if not FREEZE_CITATION_RE.search(record.commit_message):
        findings.append(RepairFinding(
            "freeze_citation_commit", False, "missing_freeze_citation_commit",
            "the supervisor change's commit message cites no captured D-024-R### "
            "qualifying-evidence id (R017; supervisor-freeze rule §3)"))
    if findings:
        return tuple(findings)
    return (RepairFinding("freeze_citation", True, "freeze_citation_present",
                          "the packet and the commit message both cite a captured "
                          "D-024-R### id"),)


# ==========================================================================
# Thin review-packet wiring (record-only)
# ==========================================================================

#: The section key the checkpoint rides under in `evidence.build_packet(
#: extra_sections=...)`. Chosen to collide with no `PROHIBITED_MARKER_KEYS` name.
REPAIR_GATE_SECTION_KEY = "repair_gate_checkpoint"


def checkpoint_section(
        *, record: RepairRecord, answers: Mapping[str, str],
        evaluation: RepairEvaluation,
        checkpoint: CheckpointEvaluation) -> dict[str, Any]:
    """Build the bounded structured section the R078 questions ride to review on.

    Record-only: the section carries the record digest, the per-predicate
    findings, the answers (each routed through `redaction.redact_text` - producer
    prose is a transmission), and the mechanical checkpoint outcome. It carries no
    verdict of its own: acceptance stays with `repair_gate_disposition` after the
    independent review.
    """
    return {
        "schema_version": REPAIR_GATE_SCHEMA_VERSION,
        "task_id": record.task_id,
        "defect_id": record.defect_id,
        "record_digest": record.record_digest(),
        "repair_mode": record.mode,
        "repair_accepted": evaluation.accepted,
        "findings": [
            {"name": f.name, "ok": f.ok, "reason_code": f.reason_code,
             "detail": redaction.redact_text(f.detail).value}
            for f in evaluation.findings],
        "checkpoint_outcome": checkpoint.outcome,
        "missing_questions": list(checkpoint.missing_questions),
        "unknown_questions": list(checkpoint.unknown_questions),
        "answers": {
            key: redaction.redact_text(str(answers.get(key, ""))).value
            for key in CHECKPOINT_QUESTIONS},
    }
