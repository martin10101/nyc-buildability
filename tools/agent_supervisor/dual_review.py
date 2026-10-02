#!/usr/bin/env python3
"""The dual-review conductor (owner directive D-091 TW2, M0-T172).

The cloud loop still has exactly ONE reviewer seam: `loop.py` injects a `reviewer`
and calls `reviewer.review(packet, expected_task_id=..., expected_checkpoint_id=...)`
once per cycle, routing on the returned `codex_reviewer.ReviewOutcome`. This module
is a CONDUCTOR that presents that SAME `.review(...)` interface but, behind it, runs
TWO independent read-only reviews of one frozen packet (the existing Codex reviewer
and the M0-T168 Claude reviewer), combines them with the M0-T169 combiner, and
projects the single combined verdict back into one `ReviewOutcome` so the loop's
routing is unchanged. It is built and injected ONLY when dual review is enabled; with
no conductor injected the loop keeps its single-Codex-reviewer path byte-for-byte
(`loop.py` default `review_conductor=None`).

What the conductor guarantees (every one fail-closed, computed in CODE, never taken
from a model):

* **Models resolved before any process (M0-T169 G5 N1).** The combining model, the
  Claude reviewer model, and the resolved Codex model are each checked against their
  controller allowlist BEFORE a slot is taken or any reviewer runs. An unset
  combining model refuses (D-091-R008: the combining model is the owner's choice with
  NO default — this module never picks or defaults one). An un-allowlisted model
  refuses. The combining model MUST differ from the Claude reviewer model (DB-103 /
  D-091-R001,R007): two equal models, or either model empty, refuse before any
  process. A packet not pinned to a full 40-char frozen head refuses.
* **One atomic slot (D-091 TW1 / M0-T171).** The whole dual review holds ONE
  review-or-combine slot reserved through `ReviewSlots`, so the per-lane cap (1) and
  the global cap (2) are honoured atomically and a third concurrent review can never
  start. When the box is full the conductor waits up to its bounded deadline, then
  refuses fail-closed rather than over-subscribing.
* **Independence.** Both reviewers receive the SAME frozen packet; neither is ever
  handed the other's output (the Claude reviewer additionally refuses a packet that
  carries a peer review — M0-T168). The combiner is a fresh identity that is neither
  the producer nor either reviewer.
* **Worst-of-two verdict, in code.** The combiner computes the combined verdict as
  the worse of the two reviews (PASS < FAIL < UNVERIFIED); model-proposed disputes are
  ADVISORY only and can never weaken it. A reviewer (or the combiner / combining
  model) that RAISES, TIMES OUT, or returns MALFORMED output yields FAIL/UNVERIFIED,
  never PASS (M0-T168 N1: a raised reviewer exception counts as FAIL).
* **Verdict projected without ever weakening a fail-closed check.** PASS -> the
  approving decision stands (the more cautious of the two: CONTINUE over COMPLETE).
  FAIL -> REVISE carrying the union of blocking findings, EXCEPT a reviewer
  HALT_UNSAFE or STOP_FOR_OWNER is preserved as its own pausing decision (downgrading
  a safety halt to a forwarded revision would weaken a fail-closed check — forbidden).
  UNVERIFIED -> a decision-less, not-`ok` outcome, so the loop takes its existing
  "review unavailable" path and pauses for the owner.
* **Disputes surfaced, gates untouched (M0-T169 G5 N3, ADR-005).** The conductor is
  the CONSUMER: it treats the code-computed verdict as authoritative and surfaces the
  combined review (verdict, per-reviewer verdicts, recorded disputes, and each
  disputed finding id) through the outcome's `notify_events` — which the loop records
  in its run report — and attaches the full `CombinedReview` to the returned outcome
  for the human gate. The loop NEVER records a gate; the orchestrator records G3/G4/G5
  from this advisory input by hand.
"""
from __future__ import annotations

import re
import time
from typing import Any, Mapping, Sequence

from .codex_reviewer import ReviewOutcome, map_decision_to_tier
from .models import CodexDecision, RecordError, digest_of
from .policy import ASK, PolicyDecision
from .review_combiner import (
    PASS,
    UNVERIFIED,
    CombinedReview,
    CombinerInputs,
    unverified_outcome,
)

#: A full, immutable commit SHA — the only shape a frozen head may take (mirrors the
#: reviewers and the combiner; a ref name, HEAD, a short SHA, or a dirty marker is
#: not a frozen head and fails closed here before any process starts).
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

#: Hard bound on any reviewer/combiner failure text folded into an outcome message,
#: so a pathological exception string can never balloon the loop's records.
_MESSAGE_BOUND_CHARS = 600


def _bounded(text: str) -> str:
    text = str(text or "")
    if len(text) <= _MESSAGE_BOUND_CHARS:
        return text
    return text[:_MESSAGE_BOUND_CHARS] + f"...[TRUNCATED {len(text)} chars]"


# --------------------------------------------------------------------------
# Packet extraction (mirrors claude_reviewer's head reader; the loop hands the
# conductor `packet.to_dict()`, so everything here reads the plain dict shape)
# --------------------------------------------------------------------------


def _git_section(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    sections = packet.get("sections")
    if not isinstance(sections, Mapping):
        return {}
    git = sections.get("git")
    return git if isinstance(git, Mapping) else {}


def frozen_head_from_packet(packet: Mapping[str, Any]) -> str:
    """The git HEAD the packet was collected at, or "" when absent/unreadable.

    `evidence.build_packet` records it at `sections.git.head.value` (every ok fact
    is wrapped as `{"value": ..., "digest": ...}`); a bare string is tolerated too.
    Returns "" rather than guessing when the git section or the head fact is missing.
    """
    head = _git_section(packet).get("head")
    if isinstance(head, Mapping):
        value = head.get("value")
        return value if isinstance(value, str) else ""
    return head if isinstance(head, str) else ""


def _diff_text_from_packet(packet: Mapping[str, Any]) -> str:
    """The worker's tracked unified diff (`sections.git.diff_content.value`), or ""."""
    diff = _git_section(packet).get("diff_content")
    if isinstance(diff, Mapping):
        value = diff.get("value")
        return value if isinstance(value, str) else ""
    return diff if isinstance(diff, str) else ""


# --------------------------------------------------------------------------
# The conductor
# --------------------------------------------------------------------------


class DualReviewConductor:
    """Runs Codex + Claude reviews of one frozen packet and combines them into one.

    Presents the loop's existing `.review(packet, expected_task_id=...,
    expected_checkpoint_id=...) -> ReviewOutcome` shape. Collaborators are injected
    so every test drives the REAL conductor against fakes (no provider, no process):

    * `codex_reviewer` — `.review(packet, expected_task_id=..., expected_checkpoint_id=...)`;
      optionally `.resolve()` (-> object with `.model`/`.usable`) and `.model` so the
      conductor can allowlist-check its model before running it.
    * `claude_reviewer` — `.review(packet, frozen_head=..., producer_identity=...,
      expected_task_id=..., expected_checkpoint_id=...)`; carries `.model`.
    * `combiner` — a `review_combiner.ReviewCombiner` (carries `.config.enabled` and the
      owner-set `.config.model`); called, never re-implemented.
    * `slots` — a `review_slots.ReviewSlots` for the atomic review-or-combine slot.
    """

    def __init__(
        self,
        *,
        codex_reviewer: Any,
        claude_reviewer: Any,
        combiner: Any,
        slots: Any,
        lane: str,
        producer_identity: str,
        allowed_models: Mapping[str, Sequence[str]],
        codex_identity: str = "",
        claude_identity: str = "",
        slot_wait_seconds: float = 0.0,
        slot_poll_seconds: float = 0.05,
    ) -> None:
        self._codex_reviewer = codex_reviewer
        self._claude_reviewer = claude_reviewer
        self._combiner = combiner
        self._slots = slots
        self._lane = str(lane)
        self._producer_identity = str(producer_identity or "")
        self._codex_identity = str(codex_identity or "")
        self._claude_identity = str(claude_identity or "")
        self._allowed_models = {
            str(k): frozenset(str(m) for m in (v or ()))
            for k, v in dict(allowed_models or {}).items()
        }
        self._slot_wait_seconds = max(0.0, float(slot_wait_seconds))
        self._slot_poll_seconds = max(0.0, float(slot_poll_seconds))
        self._combine_error = ""

    # -- the loop-facing entry point ----------------------------------------

    def review(
        self,
        packet: Mapping[str, Any],
        *,
        expected_task_id: str = "",
        expected_checkpoint_id: str = "",
    ) -> ReviewOutcome:
        """Conduct one dual review and return one projected `ReviewOutcome`."""
        packet = dict(packet)
        head = frozen_head_from_packet(packet)

        # 1. Fail-closed refusals, BEFORE any slot is taken or any process starts.
        refusal = self._preflight(head)
        if refusal is not None:
            return refusal

        # 2. One atomic review-or-combine slot for the whole dual review (TW1). Held
        #    across both reviews and the combine; released in `finally`. Never a third
        #    concurrent review: a full box waits to the deadline, then refuses.
        grant = self._acquire_slot()
        if not grant.admitted:
            return self._unverified(
                "review_slot_unavailable", "",
                f"no review-or-combine slot available for lane {self._lane!r}: "
                f"{grant.reason}; refusing rather than running a third concurrent "
                f"review (D-091 TW1)",
                (f"dual_review:slot_refused={grant.reason_code}",), None)
        try:
            # 3. Two independent reviews of the SAME frozen packet. Neither reviewer
            #    is ever handed the other's output. A raise/timeout/malformed review
            #    becomes a decision-less outcome here (M0-T168 N1) so the combiner
            #    treats it as UNVERIFIED.
            codex_review = self._run_codex(packet, expected_task_id, expected_checkpoint_id)
            claude_review = self._run_claude(
                packet, head, expected_task_id, expected_checkpoint_id)

            # 4. Combine in code: worst-of-two verdict, disputes advisory only.
            inputs = CombinerInputs(frozen_head=head,
                                    diff_text=_diff_text_from_packet(packet))
            combined = self._combine(codex_review, claude_review, inputs)
            if combined is None:
                return self._unverified("combiner_raised", "", self._combine_error,
                                        ("dual_review:verdict=UNVERIFIED",), None)

            # 5. Project the authoritative combined verdict into one outcome.
            return self._project(combined, codex_review, claude_review)
        finally:
            self._slots.release(grant.reservation)

    # -- 1. preflight refusals ----------------------------------------------

    def _preflight(self, head: str) -> "ReviewOutcome | None":
        """Every refusal that must happen before a slot or a process. Returns a
        decision-less, not-`ok` outcome on refusal (never a PASS), else None."""
        if not _FULL_SHA_RE.match((head or "").strip()):
            return self._refuse(
                "packet_head_not_frozen",
                "the evidence packet is not pinned to a full 40-char immutable commit "
                "SHA; a dual review runs only on a frozen head (fail closed)")

        combiner_model = str(getattr(self._combiner.config, "model", "") or "")
        if not combiner_model:
            return self._refuse(
                "combiner_model_unset",
                "the combining model is a required owner setting with NO default "
                "(D-091-R008); the conductor never picks or defaults one, so an unset "
                "combining model refuses before any process (fail closed)")
        if not getattr(self._combiner.config, "enabled", False):
            return self._refuse(
                "combiner_disabled",
                "the review combiner is default-off; the conductor refuses until the "
                "owner enables it (fail closed)")
        if combiner_model not in self._allowed("claude"):
            return self._refuse(
                "combiner_model_not_allowlisted",
                f"the combining model {combiner_model!r} is not in the claude allowlist "
                f"{sorted(self._allowed('claude'))} (M0-T169 G5 N1); refusing before any "
                f"process (fail closed)")

        claude_refusal = self._check_claude_reviewer_model()
        if claude_refusal is not None:
            return claude_refusal
        distinct_refusal = self._check_combiner_distinct_from_claude()
        if distinct_refusal is not None:
            return distinct_refusal
        return self._check_codex_reviewer_model()

    def _check_combiner_distinct_from_claude(self) -> "ReviewOutcome | None":
        """DB-103 (D-091-R001/R007): the combining model MUST differ from the Claude
        reviewer model. The read-only commissioning tomllib check (D091 step 5) is
        now enforced IN CODE here — before any slot is reserved or any process starts.
        Two equal models, or either model empty, refuses fail-closed; two different,
        allowlisted models proceed exactly as before.

        An empty combining model is also caught earlier (`combiner_model_unset`) and an
        empty Claude reviewer model earlier still (`claude_reviewer_model_unset`); the
        empty branch here is the explicit DB-103 "either empty" guard, kept fail-closed.
        A reviewer that does not expose its model (`None`) defers to its own review-time
        guard, mirroring `_check_claude_reviewer_model` — there is nothing to compare.
        """
        reviewer_model = getattr(self._claude_reviewer, "model", None)
        if reviewer_model is None:
            return None
        combiner_model = str(getattr(self._combiner.config, "model", "") or "")
        reviewer_model = str(reviewer_model or "")
        if not combiner_model or not reviewer_model:
            return self._refuse(
                "review_models_unset",
                "the combining model and the Claude reviewer model must both be set "
                "so the conductor can prove them distinct; an empty model refuses "
                "before any process (DB-103 / D-091-R001,R007; fail closed)")
        if combiner_model == reviewer_model:
            return self._refuse(
                "review_models_not_distinct",
                f"the combining model and the Claude reviewer model are both "
                f"{combiner_model!r}; D-091 requires each independent review be combined "
                f"by a DIFFERENT model (DB-103 / D-091-R001,R007); refusing before any "
                f"process (fail closed)")
        return None

    def _check_claude_reviewer_model(self) -> "ReviewOutcome | None":
        model = getattr(self._claude_reviewer, "model", None)
        if model is None:
            return None  # the reviewer enforces its own allowlist at review time
        model = str(model or "")
        if not model:
            return self._refuse(
                "claude_reviewer_model_unset",
                "the Claude reviewer model is unset; a review never runs an "
                "un-resolved model (fail closed)")
        if model not in self._allowed("claude"):
            return self._refuse(
                "claude_reviewer_model_not_allowlisted",
                f"the Claude reviewer model {model!r} is not in the claude allowlist "
                f"{sorted(self._allowed('claude'))}; refusing before any process")
        return None

    def _check_codex_reviewer_model(self) -> "ReviewOutcome | None":
        resolve = getattr(self._codex_reviewer, "resolve", None)
        if not callable(resolve):
            return None  # the reviewer resolves + allowlist-checks its own model
        try:
            resolution = resolve()
        except Exception as exc:  # noqa: BLE001 - a resolution failure is fail-closed
            return self._refuse(
                "codex_model_unavailable",
                f"resolving the Codex review model failed ({type(exc).__name__}); "
                f"refusing before any process (fail closed)")
        if not getattr(resolution, "usable", False):
            return self._refuse(
                "codex_model_unavailable",
                _bounded(f"the Codex review model is not usable: "
                         f"{getattr(resolution, 'reason', '') or 'no resolvable model'}"))
        model = str(getattr(resolution, "model", "") or "")
        if model and model not in self._allowed("codex"):
            return self._refuse(
                "codex_reviewer_model_not_allowlisted",
                f"the resolved Codex review model {model!r} is not in the codex allowlist "
                f"{sorted(self._allowed('codex'))}; refusing before any process")
        return None

    def _allowed(self, provider: str) -> "frozenset[str]":
        return self._allowed_models.get(provider, frozenset())

    # -- 2. slot -------------------------------------------------------------

    def _acquire_slot(self) -> Any:
        """Atomically reserve ONE review-or-combine slot, waiting up to the deadline.

        Returns the grant (admitted or the last refusal). A full box is a refusal,
        not an exception: the caller fails closed rather than over-subscribing.
        """
        deadline = time.monotonic() + self._slot_wait_seconds
        while True:
            grant = self._slots.try_reserve(self._lane)
            if grant.admitted:
                return grant
            if time.monotonic() >= deadline:
                return grant
            time.sleep(self._slot_poll_seconds)

    # -- 3. independent reviews (a raise becomes a decision-less FAIL) -------

    def _run_codex(self, packet: Mapping[str, Any], expected_task_id: str,
                   expected_checkpoint_id: str) -> ReviewOutcome:
        try:
            return self._codex_reviewer.review(
                packet, expected_task_id=expected_task_id,
                expected_checkpoint_id=expected_checkpoint_id)
        except Exception as exc:  # noqa: BLE001 - M0-T168 N1: a raise counts as FAIL
            return unverified_outcome(
                "codex_review_raised",
                _bounded(f"the Codex review raised {type(exc).__name__}: {exc}"))

    def _run_claude(self, packet: Mapping[str, Any], head: str, expected_task_id: str,
                    expected_checkpoint_id: str) -> ReviewOutcome:
        try:
            return self._claude_reviewer.review(
                packet, frozen_head=head, producer_identity=self._producer_identity,
                expected_task_id=expected_task_id,
                expected_checkpoint_id=expected_checkpoint_id)
        except Exception as exc:  # noqa: BLE001 - M0-T168 N1: a raise counts as FAIL
            return unverified_outcome(
                "claude_review_raised",
                _bounded(f"the Claude review raised {type(exc).__name__}: {exc}"))

    # -- 4. combine ----------------------------------------------------------

    def _combine(self, codex_review: ReviewOutcome, claude_review: ReviewOutcome,
                 inputs: CombinerInputs) -> "CombinedReview | None":
        """Call the real combiner. A raise (any pre-launch refusal, or a combining
        model that itself raises) is fail-closed to None -> UNVERIFIED (M0-T168 N1)."""
        try:
            return self._combiner.combine(
                codex_review=codex_review, claude_review=claude_review, inputs=inputs,
                producer_identity=self._producer_identity,
                codex_reviewer_identity=self._codex_identity,
                claude_reviewer_identity=self._claude_identity)
        except Exception as exc:  # noqa: BLE001 - a combiner raise is never a PASS
            self._combine_error = _bounded(
                f"the review combiner raised {type(exc).__name__}: {exc}; the combined "
                f"verdict is UNVERIFIED (fail closed)")
            return None

    # -- 5. projection -------------------------------------------------------

    def _project(self, combined: CombinedReview, codex_review: ReviewOutcome,
                 claude_review: ReviewOutcome) -> ReviewOutcome:
        """Project the code-computed combined verdict into one loop-routable outcome.

        Never weakens a fail-closed check: a reviewer HALT_UNSAFE / STOP_FOR_OWNER is
        carried through as its own pausing decision rather than being flattened to a
        forwarded REVISE, and UNVERIFIED pauses for the owner.
        """
        events = _surfacing_events(combined, codex_review, claude_review)

        if combined.verdict == UNVERIFIED:
            return self._unverified(
                "dual_review_unverified", combined.model_used,
                _bounded("the combined verdict is UNVERIFIED (a review was missing, "
                         "malformed, timed out, or raised); pausing for the owner "
                         "rather than continuing an unverified unit"),
                events, combined)

        if combined.verdict == PASS:
            decision = self._pass_decision(codex_review, claude_review)
            return self._ok(decision, combined, events)

        # FAIL. Both reviews are ok here (UNVERIFIED would have dominated the verdict),
        # but guard defensively and fail closed if that ever does not hold.
        cdec = getattr(codex_review, "decision", None)
        kdec = getattr(claude_review, "decision", None)
        if cdec is None or kdec is None:
            return self._unverified(
                "dual_review_unverified", combined.model_used,
                "a FAIL verdict reached projection without two decisions; fail closed",
                events, combined)
        names = {cdec.decision, kdec.decision}
        if "HALT_UNSAFE" in names:
            decision = self._halt_decision(combined, cdec, kdec)
        elif "STOP_FOR_OWNER" in names:
            decision = self._stop_decision(cdec, kdec)
        else:
            decision = self._revise_decision(combined, cdec, kdec)
        return self._ok(decision, combined, events)

    def _pass_decision(self, codex_review: ReviewOutcome,
                       claude_review: ReviewOutcome) -> CodexDecision:
        """On PASS both reviewers approved; carry the more cautious approving decision
        (CONTINUE over COMPLETE), preferring the Codex reviewer's on a tie."""
        cdec = codex_review.decision
        kdec = claude_review.decision
        if cdec is not None and cdec.decision == "CONTINUE":
            return cdec
        if kdec is not None and kdec.decision == "CONTINUE":
            return kdec
        return cdec if cdec is not None else kdec

    def _revise_decision(self, combined: CombinedReview, cdec: CodexDecision,
                         kdec: CodexDecision) -> CodexDecision:
        findings = _blocking_entries(combined)
        return self._compose(
            cdec, kdec, combined, decision="REVISE",
            blocking_findings=findings,
            next_claude_prompt=_revise_prompt(combined, findings))

    def _halt_decision(self, combined: CombinedReview, cdec: CodexDecision,
                       kdec: CodexDecision) -> CodexDecision:
        findings = _blocking_entries(combined) or [{
            "source": "dual_review",
            "finding": {"reason": "a reviewer returned HALT_UNSAFE"}}]
        return self._compose(
            cdec, kdec, combined, decision="HALT_UNSAFE", blocking_findings=findings)

    def _stop_decision(self, cdec: CodexDecision, kdec: CodexDecision) -> CodexDecision:
        stop = next((d for d in (cdec, kdec) if d.decision == "STOP_FOR_OWNER"), None)
        question = (stop.owner_question if stop and stop.owner_question.strip()
                    else "a reviewer stopped for the owner; a human decision is required")
        return self._compose(cdec, kdec, None, decision="STOP_FOR_OWNER",
                             owner_question=question)

    def _compose(self, cdec: CodexDecision, kdec: CodexDecision,
                 combined: "CombinedReview | None", *, decision: str,
                 **fields: Any) -> CodexDecision:
        """Build one projected decision from the two reviews' identity fields.

        Prefers the Codex decision's correlation fields (task/checkpoint/heads), which
        the reviewers already validated against the loop's expected ids. `model_used`
        records the combining model when a combined review produced this projection.
        """
        base = cdec if cdec is not None else kdec
        reason_codes = ["dual_review_fail"]
        if combined is not None:
            reason_codes += [f"codex:{combined.codex_verdict}",
                             f"claude:{combined.claude_verdict}"]
        return CodexDecision(
            schema_version=base.schema_version,
            decision=decision,
            reviewed_task_id=base.reviewed_task_id,
            reviewed_checkpoint_id=base.reviewed_checkpoint_id,
            verified_repo_head=base.verified_repo_head,
            verified_origin_main=base.verified_origin_main,
            model_used=(combined.model_used if combined is not None else base.model_used),
            reason_codes=reason_codes,
            **fields)

    # -- outcome construction (fail closed if a projection is ever invalid) --

    def _ok(self, decision: CodexDecision, combined: CombinedReview,
            events: "tuple[str, ...]") -> ReviewOutcome:
        try:
            decision.validate()
        except RecordError as exc:
            return self._unverified(
                "dual_review_projection_invalid", combined.model_used,
                _bounded(f"the projected decision did not validate ({exc}); fail closed"),
                events, combined)
        outcome = ReviewOutcome(
            decision, combined.model_used, "", 1,
            decision_digest=digest_of(decision.to_dict()),
            tier=map_decision_to_tier(decision),
            notify_events=events)
        outcome.combined_review = combined  # advisory artifact for the human gate (N3)
        return outcome

    def _unverified(self, code: str, model_used: str, message: str,
                    events: "tuple[str, ...]",
                    combined: "CombinedReview | None") -> ReviewOutcome:
        """A decision-less, not-`ok` outcome: the loop's existing review-unavailable
        path pauses for the owner. Never a PASS."""
        outcome = ReviewOutcome(
            None, model_used, "", 1, error_code=code, error_message=message,
            tier=PolicyDecision(tier=ASK, reason_code=code, reason=message,
                                rule_id="D-091", classification="unclassified"),
            notify_events=events)
        outcome.combined_review = combined
        return outcome

    def _refuse(self, code: str, message: str) -> ReviewOutcome:
        """A preflight refusal: no slot, no process, no combined review."""
        return self._unverified(code, "", message,
                                (f"dual_review:refused={code}",), None)


# --------------------------------------------------------------------------
# Projection helpers (pure)
# --------------------------------------------------------------------------


def _blocking_entries(combined: CombinedReview) -> "list[dict[str, Any]]":
    """The union of both reviews' blocking findings, source-tagged, each carrying any
    ADVISORY dispute the combiner recorded (so the human gate sees them on the
    decision too). Advisory disputes never remove a finding (M0-T169)."""
    entries: list[dict[str, Any]] = []
    for finding in combined.findings:
        if finding.kind != "blocking":
            continue
        entry: dict[str, Any] = {"source": finding.source, "finding": finding.detail,
                                 "disputed": finding.disputed}
        if finding.dispute is not None:
            entry["dispute"] = finding.dispute
        entries.append(entry)
    return entries


def _revise_prompt(combined: CombinedReview,
                   findings: Sequence[Mapping[str, Any]]) -> str:
    """A deterministic (clock-free) revision instruction for a FAIL verdict."""
    return (
        "Two independent reviews did not both approve this checkpoint. Combined "
        f"verdict: {combined.verdict} (codex={combined.codex_verdict}, "
        f"claude={combined.claude_verdict}). Address every blocking finding in "
        f"blocking_findings ({len(findings)} total) and resubmit. Recorded disputes "
        "are advisory only: the disputed finding still stands until a human weighs it.")


def _surfacing_events(combined: CombinedReview, codex_review: ReviewOutcome,
                      claude_review: ReviewOutcome) -> "tuple[str, ...]":
    """The combined review surfaced for the loop's report / the human gate (N3).

    Pure strings so the loop's existing `notify_events` channel carries them into the
    run report with no loop change. The full `CombinedReview` is also attached to the
    outcome for a richer consumer.
    """
    events = [
        f"dual_review:verdict={combined.verdict}",
        f"dual_review:codex={combined.codex_verdict}",
        f"dual_review:claude={combined.claude_verdict}",
        f"dual_review:disputes_recorded={combined.disputes_recorded}",
        f"dual_review:disputes_rejected={combined.disputes_rejected}",
    ]
    for finding in combined.disputed_findings:
        events.append(f"dual_review:disputed_finding={finding.finding_id}")
    for source, review in (("codex", codex_review), ("claude", claude_review)):
        for event in (getattr(review, "notify_events", ()) or ()):
            events.append(f"{source}:{event}")
    return tuple(events)
