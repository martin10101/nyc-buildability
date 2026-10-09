#!/usr/bin/env python3
"""The bounded 4.8 guardrail-refusal bridge policy (M0-T093, D-024 Phase E).

Supervisor-freeze qualifying evidence: **D-024-R103** (Phase E; packet-named).

Everything here is DETERMINISTIC POLICY over the classifier's verdicts and the
already-committed machinery - nothing launches a process, clicks an interface,
or messages an agent. The supervisor is SHADOW-ONLY: every path in this module
either records intent or refuses; live actuation of the continue-with-4.8
interface choice stays behind the R595 owner gate AND a measured-live C1 shape
capture (`assert_actuation_permitted` enforces both).

The R070 bridge sequence and where each step lives:

1. classify and journal the recognized refusal WITHOUT unnecessary sensitive
   content, preserving task identity and the exact authorization/acceptance
   criteria -> `build_refusal_journal_record` (redacted, bounded excerpt);
2. if the interface offers only continue-with-4.8 or stop, permit 4.8 as a
   temporary continuity bridge -> `continuation_choice` (the ONLY selectable
   option is the exact config-allowlisted model continuation, R069);
3. the bridge may ONLY finish the smallest current atomic operation, collect
   already-running bounded children, run checkpoint validation, and create a
   durable handoff -> `BridgeRestrictions` (typed refusal of anything else;
   composes `child_handoff.TurnoverCoordinator`, never rebuilds it);
4. retire at the first safe seam and start fresh Fable 5 from durable verified
   artifacts -> `BridgeRestrictions.retire` (existing `handoff` machinery).

R071/R073 re-presentation is a deterministic STRUCTURED-FIELD transform
(`represent` over `RefusedRequest`), never free-prose rewriting, with
`assert_semantic_preserved` proving field preservation; the two-attempt
re-entry cap is a durable, digest-bound journal record surviving restart
(`record_reentry_attempt`); R072 lower-tier continuation consults the existing
workload-fit machinery and otherwise BLOCKS citing the exact conflict; R074
bridge output always re-enters the standard review path.

R075: every trigger, counter, journal key, typed code, and state here is
DISTINCT from the quota/limit policies' - the quota detect-and-hold path
(D-007 am.12 / R603-R608 if authoritative) is untouched and cannot enter the
bridge in either direction.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Mapping, Sequence

from .approved_models import ApprovedModels, ModelRoutingError
from .child_handoff import ChildHandoff, TurnoverCoordinator
from .guardrail_refusal import (
    AuthorizedTaskRecord,
    RefusalEvidence,
    RefusalShapeFixture,
    RefusalVerdict,
    classify_guardrail_refusal,
)
from .handoff import Handoff, validate_handoff
from .models import digest_of, to_utc_iso
from .redaction import redact_text
from .spawn_decision import model_fit
from .subagent_contracts import assert_worker_text_clean
from .workload_classifier import (
    OVERSIZED_SPLIT,
    UNKNOWN_RECON,
    WorkloadFeatures,
    classify_workload,
)


class BridgeError(ValueError):
    """Typed error for every bridge refusal (code + message). Fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Durable journal keys (DISTINCT from every quota-side key, D-024-R075/R184)
# --------------------------------------------------------------------------

#: Per-request refusal record: `guardrail_refusal/<request_digest>`.
REFUSAL_RECORD_KEY_PREFIX = "guardrail_refusal/"
#: Pointer to the digest of the most recent recorded refusal.
LAST_REFUSAL_KEY = "guardrail_refusal_last_digest"
#: Per-request durable re-entry counter: `guardrail_reentry/<request_digest>`.
REENTRY_KEY_PREFIX = "guardrail_reentry/"

#: R071: at most two fresh Fable 5 re-entry attempts for the same refused
#: request, counted durably across restarts. Never a loop.
MAX_REENTRY_ATTEMPTS = 2

#: Loop stop / journal reason code for a recorded (never actuated) refusal.
#: Deliberately parallel to - and distinct from - the quota seam's
#: `fable_exhaustion_turnover_recorded` (worker_turnover.py).
REASON_REFUSAL_RECORDED = "guardrail_refusal_recorded"

#: A bounded evidence excerpt, not a transcript (R070 step 1 "without
#: unnecessary sensitive content"; the child_handoff boundedness stance).
MAX_EVIDENCE_EXCERPT_CHARS = 1200


# --------------------------------------------------------------------------
# R070 step 1 - the journal record (bounded, redacted, identity-preserving)
# --------------------------------------------------------------------------


def build_refusal_journal_record(
    verdict: RefusalVerdict,
    authorized_task: AuthorizedTaskRecord,
    *,
    request_digest: str,
    evidence_excerpt: str = "",
) -> dict[str, Any]:
    """The durable record of one recognized refusal (R070 step 1).

    Preserves the task identity and the EXACT authorization and acceptance
    criteria, carries a bounded redacted evidence excerpt, and nothing else -
    no transcript, no secrets (a `redact_text` pattern pass runs over every
    text field, including the worker-derived excerpt).
    """
    if not verdict.is_recognized_refusal:
        raise BridgeError(
            "not_a_recognized_refusal",
            f"only a recognized guardrail refusal is journaled as one; this "
            f"verdict is {verdict.classification.value!r} ({verdict.condition})")
    excerpt = (evidence_excerpt or "")[:MAX_EVIDENCE_EXCERPT_CHARS]

    # Per-string PATTERN redaction (`redact_text`), not the wholesale
    # `redact_structure` key masking: that masking blanks any value under a
    # key matching `auth`/`authorization`, but R070 step 1 REQUIRES the exact
    # authorization preserved. The authorization/criteria/purpose come from
    # the controller's own committed task packet (not worker output); the
    # pattern pass still masks any embedded secret material in every field,
    # and the worker-derived excerpt gets the same treatment.
    def clean(text: str) -> str:
        return redact_text(text).value

    return {
        "kind": "guardrail_refusal",
        "request_digest": request_digest,
        "task_id": clean(authorized_task.task_id),
        "authorization": clean(authorized_task.authorization),
        "acceptance_criteria": [clean(c)
                                for c in authorized_task.acceptance_criteria],
        "purpose": clean(authorized_task.purpose),
        "matched_shape": verdict.matched_shape,
        "shape_verified_live": verdict.shape_verified_live,
        "condition": verdict.condition,
        "reason": clean(verdict.reason),
        "evidence_excerpt": clean(excerpt),
        "at_utc": to_utc_iso(),
    }


# --------------------------------------------------------------------------
# R069 / R070 step 2 - the exact allowlisted continuation choice
# --------------------------------------------------------------------------

#: The one option kind the policy may ever select. Everything else - arbitrary
#: approvals, shell permissions, credential prompts, destructive
#: confirmations, merges, deployment prompts - is NEVER answered (R069).
OPTION_KIND_MODEL_CONTINUATION = "model-continuation"


@dataclasses.dataclass(frozen=True)
class ContinuationChoice:
    """The policy's answer to what the interface offered. Selection is an
    ACTUATION-INTENT record only on this build; nothing clicks anything."""

    selected: bool
    option_index: int
    reason_code: str
    reason: str


def continuation_choice(
    offered_options: Sequence[Mapping[str, Any]],
    *,
    approved: ApprovedModels,
    bridge_model_id: str,
) -> ContinuationChoice:
    """Evaluate interface options against R069's exact-allowlist rule.

    The ONLY selectable option is a `model-continuation` whose model id
    EXACTLY equals the configured bridge model AND that model is on the
    owner-approved list. No match -> no selection (the R070 step-2 outcome is
    then "stop"). More than one match -> ambiguous, refused. Every other
    option shape is never answered.

    The option records here are NORMALIZED policy inputs; the adapter that
    reads a real interface is a separate, owner-gated concern (C1/R595) -
    this build records intent only.
    """
    if bridge_model_id not in approved:
        return ContinuationChoice(
            False, -1, "bridge_model_not_allowlisted",
            f"the bridge model {bridge_model_id!r} is not on the owner-approved "
            f"model list; nothing is selectable (D-024-R069)")
    matches: list[int] = []
    for index, option in enumerate(offered_options):
        if not isinstance(option, Mapping):
            continue
        kind = str(option.get("kind") or "")
        model_id = str(option.get("model_id") or "")
        if kind == OPTION_KIND_MODEL_CONTINUATION and model_id == bridge_model_id:
            matches.append(index)
    if not matches:
        return ContinuationChoice(
            False, -1, "exact_option_not_offered",
            "the interface did not present the exact allowlisted "
            f"continue-with-{bridge_model_id!r} option; no other prompt is ever "
            "automatically answered, so the outcome is stop (D-024-R069/R070)")
    if len(matches) > 1:
        return ContinuationChoice(
            False, -1, "ambiguous_options",
            "more than one option matches the exact allowlisted continuation; "
            "an ambiguous menu is never guessed at (fail closed)")
    return ContinuationChoice(
        True, matches[0], "exact_allowlisted_continuation",
        f"the exact allowlisted continue-with-{bridge_model_id!r} option is the "
        f"single selectable choice (actuation-INTENT recorded; live selection "
        f"stays owner-gated, D-024-R069)")


def assert_actuation_permitted(*, shape_verified_live: bool,
                               owner_authorized: bool) -> None:
    """The double gate in front of ANY live bridge actuation.

    On this build NOTHING calls this with both True: no shape is
    measured-live (owner-gated C1 canary pending) and no owner R595
    activation exists. The function exists so the gate is mechanical, not
    narrative - tests prove it refuses.
    """
    if not shape_verified_live:
        raise BridgeError(
            "actuation_requires_measured_live_shape",
            "live bridge actuation requires the recognized refusal shape to be "
            "measured-live (owner-approved C1 canary, R192/R197); a documented "
            "candidate records intent only")
    if not owner_authorized:
        raise BridgeError(
            "actuation_requires_owner_authorization",
            "live bridge actuation requires the owner's R595 activation; the "
            "supervisor is SHADOW-ONLY and records intent only")


# --------------------------------------------------------------------------
# R070 step 3 - the mechanically restricted bridge
# --------------------------------------------------------------------------

OP_FINISH_ATOMIC = "finish-smallest-atomic-operation"
OP_COLLECT_CHILDREN = "collect-bounded-children"
OP_CHECKPOINT_VALIDATION = "checkpoint-validation"
OP_DURABLE_HANDOFF = "durable-handoff"

#: The CLOSED set of operations the 4.8 bridge may perform (R070 step 3).
PERMITTED_BRIDGE_OPERATIONS: tuple[str, ...] = (
    OP_FINISH_ATOMIC, OP_COLLECT_CHILDREN, OP_CHECKPOINT_VALIDATION,
    OP_DURABLE_HANDOFF)

#: Named-by-prohibition operations, refused with their own message so the
#: refusal names the rule. Anything not PERMITTED is refused anyway (fail
#: closed); these are the shapes R070 forbids explicitly.
FORBIDDEN_BRIDGE_OPERATIONS: tuple[str, ...] = (
    "new-task", "new-investigation", "spawn-subagent", "broaden-scope",
    "consume-campaign")


class BridgeRestrictions:
    """The mechanical restriction layer around one active 4.8 bridge.

    Composes the existing `child_handoff.TurnoverCoordinator` for the child
    drain (landing begins the moment the bridge exists, so NO new children can
    ever be registered) and the existing `handoff` machinery for retirement.
    After `retire` every further operation is refused: the bridge never
    continues past the first safe seam (R070 step 4).
    """

    def __init__(self, coordinator: TurnoverCoordinator) -> None:
        self._coordinator = coordinator
        # No new children from the moment the bridge exists (R070 step 3;
        # child_handoff.register_child refuses once landing has begun).
        coordinator.begin_landing()
        self._retired = False
        self._performed: list[str] = []

    def authorize(self, operation: str) -> str:
        """Permit exactly the R070 step-3 operations; refuse everything else."""
        if self._retired:
            raise BridgeError(
                "bridge_retired",
                "the bridge retired at its first safe seam and never continues "
                "past it (D-024-R070 step 4)")
        if operation in FORBIDDEN_BRIDGE_OPERATIONS:
            raise BridgeError(
                "bridge_scope_forbidden",
                f"the 4.8 bridge must not {operation!r}: it may only finish the "
                f"smallest current atomic operation, collect already-running "
                f"bounded children, run checkpoint validation, and create a "
                f"durable handoff (D-024-R070 step 3)")
        if operation not in PERMITTED_BRIDGE_OPERATIONS:
            raise BridgeError(
                "bridge_unknown_operation",
                f"{operation!r} is not a permitted bridge operation "
                f"{list(PERMITTED_BRIDGE_OPERATIONS)}; an unknown operation is "
                f"refused, never guessed at (fail closed)")
        self._performed.append(operation)
        return operation

    @property
    def performed(self) -> tuple[str, ...]:
        return tuple(self._performed)

    @property
    def retired(self) -> bool:
        return self._retired

    def may_spawn_children(self) -> bool:
        """Always False: the bridge never creates subagents (R070 step 3).
        The composed coordinator refuses too - landing began at construction,
        so `register_child` raises `landing_in_progress` (s6.3)."""
        return False

    def collect_child(self, handoff: ChildHandoff) -> None:
        """Reconcile one already-running bounded child through the EXISTING
        machinery; nothing is spawned anew (R070 step 3, s6.3)."""
        self.authorize(OP_COLLECT_CHILDREN)
        self._coordinator.record_child_handoff(handoff)

    def unreconciled_children(self) -> tuple[str, ...]:
        return self._coordinator.unreconciled_children()

    def retire(self, bridge_handoff: Handoff) -> dict[str, Any]:
        """R070 step 4: land at the FIRST safe seam with a complete bounded
        durable handoff (existing schema + validation), for a fresh Fable 5
        successor. Refuses while children are unreconciled; irreversible."""
        self.authorize(OP_DURABLE_HANDOFF)
        pending = self._coordinator.unreconciled_children()
        if pending:
            raise BridgeError(
                "children_unreconciled",
                f"the bridge cannot retire while bounded children are "
                f"unreconciled: {list(pending)} (s6.3; every child ends in a "
                f"durable handoff first)")
        validate_handoff(bridge_handoff)
        self._retired = True
        return {
            "retired": True,
            "handoff_digest": bridge_handoff.digest(),
            "successor_policy": "fresh Fable 5 from durable verified artifacts "
                                "(D-024-R070 step 4)",
        }


# --------------------------------------------------------------------------
# R074 - bridge output is reviewed like any producer output
# --------------------------------------------------------------------------

DISPOSITION_REVIEW_REQUIRED = "review_required"
DISPOSITION_ACCEPTED_BY_REVIEW = "accepted_by_review"
DISPOSITION_REJECTED = "rejected"


def bridge_output_disposition(review_verdict: Mapping[str, Any] | None) -> tuple[str, str]:
    """R074: bridge output enters the SAME review path as any producer output.

    No verdict (or an unrecognized one) -> review_required: completion is
    never assumed correct. An explicit FAIL/BLOCKED -> rejected. Only an
    explicit independent PASS accepts.
    """
    if not isinstance(review_verdict, Mapping):
        return (DISPOSITION_REVIEW_REQUIRED,
                "bridge output has no review verdict; it is never auto-accepted "
                "merely because it completed (D-024-R074)")
    verdict = str(review_verdict.get("verdict") or "").strip().upper()
    if verdict == "PASS":
        return (DISPOSITION_ACCEPTED_BY_REVIEW,
                "an independent reviewer passed the bridge output through the "
                "standard review path (D-024-R074)")
    if verdict in ("FAIL", "BLOCKED"):
        return (DISPOSITION_REJECTED,
                f"the standard review path rejected the bridge output "
                f"({verdict}); defective bridge output is discarded, not "
                f"integrated (D-024-R074)")
    return (DISPOSITION_REVIEW_REQUIRED,
            f"unrecognized review verdict {verdict!r}; the output stays "
            f"unaccepted until the standard review path rules (fail closed)")


# --------------------------------------------------------------------------
# R071/R073 - semantic-preserving re-presentation (structured-field transform)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class RefusedRequest:
    """The structured record of the request Fable refused.

    R073's transform is defined OVER THESE FIELDS, never over free prose: the
    re-presentation is assembled from them verbatim, which is what makes
    semantic preservation provable by field comparison instead of judgment.
    """

    task_id: str
    purpose: str
    authorization: str
    constraints: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    request_text: str

    def __post_init__(self) -> None:
        for name in ("task_id", "purpose", "authorization", "request_text"):
            if not str(getattr(self, name)).strip():
                raise BridgeError(
                    "incomplete_refused_request",
                    f"{name!r} is required: a refused request is re-presented "
                    f"only with its exact purpose, authorization, and text "
                    f"preserved (D-024-R071)")
        if not self.acceptance_criteria:
            raise BridgeError(
                "incomplete_refused_request",
                "acceptance_criteria are required (D-024-R070 step 1 preserves "
                "the exact acceptance criteria)")

    def digest(self) -> str:
        """The digest the durable re-entry counter is bound to (R071)."""
        return digest_of({
            "task_id": self.task_id,
            "purpose": self.purpose,
            "authorization": self.authorization,
            "constraints": list(self.constraints),
            "acceptance_criteria": list(self.acceptance_criteria),
            "request_text": self.request_text,
        })

    @classmethod
    def from_authorized_task(cls, record: AuthorizedTaskRecord, *,
                             request_text: str,
                             constraints: tuple[str, ...] = ()) -> "RefusedRequest":
        return cls(task_id=record.task_id,
                   purpose=record.purpose or record.task_id,
                   authorization=record.authorization,
                   constraints=constraints,
                   acceptance_criteria=record.acceptance_criteria,
                   request_text=request_text)


@dataclasses.dataclass(frozen=True)
class RepresentedRequest:
    """One re-presentation attempt: the SAME request, restated for clarity."""

    original: RefusedRequest
    attempt: int
    presentation_text: str


#: Base64-ish blobs long enough to smuggle content. Any such token in the
#: presentation that is absent from every original field is refused
#: (R073: never encoding a request to evade review).
_ENCODED_BLOB = re.compile(r"[A-Za-z0-9+/=]{40,}")


def represent(request: RefusedRequest, *, attempt: int) -> RepresentedRequest:
    """R071/R073: re-present the SAME legitimate request in clearer, neutral,
    context-complete language.

    Deterministic and generative-from-fields: the presentation is assembled
    from the structured record verbatim (purpose and authorization stated
    first, constraints and criteria enumerated, the exact request quoted
    whole). By construction it cannot hide intent, delete a constraint, or
    escalate authority - and `assert_semantic_preserved` re-proves that
    before the result is returned.
    """
    if not isinstance(attempt, int) or not 1 <= attempt <= MAX_REENTRY_ATTEMPTS:
        raise BridgeError(
            "bad_attempt_number",
            f"attempt must be 1..{MAX_REENTRY_ATTEMPTS} (durable two-attempt "
            f"cap, D-024-R071); got {attempt!r}")
    lines = [
        f"Re-presentation (attempt {attempt} of {MAX_REENTRY_ATTEMPTS}) of an "
        f"owner-authorized task, restated for clarity. Nothing below changes "
        f"the request's purpose, authorization, constraints, or acceptance "
        f"criteria (D-024-R071/R073).",
        "",
        f"Task: {request.task_id}",
        f"Authorized purpose: {request.purpose}",
        f"Authorization: {request.authorization}",
        "Binding constraints (all preserved):",
    ]
    lines.extend(f"- {constraint}" for constraint in request.constraints)
    if not request.constraints:
        lines.append("- (none beyond the packet scope)")
    lines.append("Acceptance criteria (all preserved):")
    lines.extend(f"- {criterion}" for criterion in request.acceptance_criteria)
    lines.append("Exact request (verbatim, in full):")
    lines.append(request.request_text)
    text = "\n".join(lines)
    assert_worker_text_clean("re-presentation", text)
    result = RepresentedRequest(original=request, attempt=attempt,
                                presentation_text=text)
    assert_semantic_preserved(request, presentation_text=text,
                              claimed=request)
    return result


def assert_semantic_preserved(
    original: RefusedRequest,
    *,
    presentation_text: str,
    claimed: RefusedRequest | None = None,
) -> None:
    """Prove a re-presentation preserved the request's semantics (R073).

    Refuses, with a typed code per prohibited transform:

    * ``different_task`` / ``purpose_altered`` / ``authorization_altered`` -
      identity, purpose, and authorization must be EXACTLY equal (clarity
      never rewrites them; escalation and de-authorization both fail here);
    * ``constraint_deleted`` - every original constraint survives (narrowing
      may ADD constraints, never remove one);
    * ``criteria_altered`` - the acceptance criteria are exactly preserved;
    * ``request_fragmented`` - the exact request text appears WHOLE in the
      presentation (fragmenting a request to evade review is prohibited);
    * ``purpose_omitted`` / ``authorization_omitted`` /
      ``constraint_omitted`` / ``criterion_omitted`` - the presentation
      states every material field verbatim (context-complete);
    * ``encoded_content`` - no long encoded blob absent from the original
      (encoding a request to evade review is prohibited). Euphemism is
      excluded structurally: the presentation must carry the original fields
      verbatim, so a reworded (euphemized) substitute fails the containment
      checks above.
    """
    if claimed is not None:
        if claimed.task_id != original.task_id:
            raise BridgeError("different_task",
                              "a re-presentation never names a different task "
                              "(D-024-R072: same bounded task only)")
        if claimed.purpose != original.purpose:
            raise BridgeError("purpose_altered",
                              "the exact purpose must be preserved (D-024-R071)")
        if claimed.authorization != original.authorization:
            raise BridgeError(
                "authorization_altered",
                "the exact authorization must be preserved - neither escalated "
                "nor deleted (D-024-R071/R073)")
        missing = set(original.constraints) - set(claimed.constraints)
        if missing:
            raise BridgeError(
                "constraint_deleted",
                f"material constraints were deleted: {sorted(missing)} "
                f"(D-024-R073: narrowing may add constraints, never remove one)")
        if set(claimed.acceptance_criteria) != set(original.acceptance_criteria):
            raise BridgeError(
                "criteria_altered",
                "the exact acceptance criteria must be preserved (D-024-R071)")
        if claimed.request_text != original.request_text:
            raise BridgeError(
                "request_fragmented",
                "the request text was altered; re-presentation clarifies "
                "AROUND the exact request, never rewrites, fragments, or "
                "re-encodes it (D-024-R073)")
    if original.request_text not in presentation_text:
        raise BridgeError(
            "request_fragmented",
            "the exact request text does not appear whole in the presentation; "
            "fragmenting or eliding the request to evade review is prohibited "
            "(D-024-R073)")
    if original.purpose not in presentation_text:
        raise BridgeError("purpose_omitted",
                          "the authorized purpose must be stated verbatim "
                          "(D-024-R073 context-complete)")
    if original.authorization not in presentation_text:
        raise BridgeError("authorization_omitted",
                          "the authorization must be stated verbatim "
                          "(D-024-R073 context-complete)")
    for constraint in original.constraints:
        if constraint not in presentation_text:
            raise BridgeError(
                "constraint_omitted",
                f"constraint {constraint!r} is missing from the presentation "
                f"(D-024-R073: a material constraint is never dropped)")
    for criterion in original.acceptance_criteria:
        if criterion not in presentation_text:
            raise BridgeError(
                "criterion_omitted",
                f"acceptance criterion {criterion!r} is missing from the "
                f"presentation (D-024-R071)")
    original_fields = "\n".join((original.task_id, original.purpose,
                                 original.authorization,
                                 *original.constraints,
                                 *original.acceptance_criteria,
                                 original.request_text))
    for blob in _ENCODED_BLOB.findall(presentation_text):
        if blob not in original_fields:
            raise BridgeError(
                "encoded_content",
                "the presentation carries a long encoded blob absent from the "
                "original request; encoding a request to evade review is "
                "prohibited (D-024-R073)")


# --------------------------------------------------------------------------
# R071 - the durable, digest-bound two-attempt re-entry counter
# --------------------------------------------------------------------------


def _reentry_key(request_digest: str) -> str:
    if not request_digest or not isinstance(request_digest, str):
        raise BridgeError("missing_digest",
                          "the re-entry counter is digest-bound (D-024-R071)")
    return f"{REENTRY_KEY_PREFIX}{request_digest}"


def attempts_recorded(journal: Any, request_digest: str) -> int:
    record = journal.get_state(_reentry_key(request_digest), None)
    if not isinstance(record, Mapping):
        return 0
    attempts = record.get("attempts", 0)
    return attempts if isinstance(attempts, int) and attempts >= 0 else 0


def record_reentry_attempt(journal: Any, request_digest: str) -> int:
    """Durably count one fresh Fable 5 re-entry for this refused request.

    Compare-and-swap inside the journal so a concurrent writer never loses an
    attempt; raises ``reentry_cap_exhausted`` at the cap - there is no third
    attempt and no Fable/4.8 ping-pong (R071). The record survives restart:
    it lives in the same durable journal the boot reconciliation reads.
    """
    key = _reentry_key(request_digest)
    while True:
        current = journal.get_state(key, None)
        base = dict(current) if isinstance(current, Mapping) else {}
        attempts = base.get("attempts", 0)
        attempts = attempts if isinstance(attempts, int) and attempts >= 0 else 0
        if attempts >= MAX_REENTRY_ATTEMPTS:
            raise BridgeError(
                "reentry_cap_exhausted",
                f"the durable two-attempt re-entry cap for request "
                f"{request_digest[:16]}... is exhausted "
                f"({attempts}/{MAX_REENTRY_ATTEMPTS}); no further Fable "
                f"re-entry is permitted (D-024-R071: no infinite ping-pong)")
        updated = {"attempts": attempts + 1, "status": "open",
                   "last_attempt_utc": to_utc_iso()}
        if journal.compare_and_swap_state(key, current, updated):
            return attempts + 1


def record_reentry_success(journal: Any, request_digest: str) -> None:
    """S12: a successful re-entry clears the live count (recorded, not erased)."""
    key = _reentry_key(request_digest)
    while True:
        current = journal.get_state(key, None)
        base = dict(current) if isinstance(current, Mapping) else {}
        updated = {"attempts": 0, "status": "succeeded",
                   "succeeded_after_attempts": base.get("attempts", 0),
                   "succeeded_at_utc": to_utc_iso()}
        if journal.compare_and_swap_state(key, current, updated):
            return


def reentry_cap_exhausted(journal: Any, request_digest: str) -> bool:
    """True when both attempts were consumed and neither succeeded (S13)."""
    record = journal.get_state(_reentry_key(request_digest), None)
    if not isinstance(record, Mapping):
        return False
    return (record.get("status") == "open"
            and attempts_recorded(journal, request_digest) >= MAX_REENTRY_ATTEMPTS)


# --------------------------------------------------------------------------
# R072 - after the cap: configured lower-tier continuation, or blocked
# --------------------------------------------------------------------------

DECISION_CONTINUE_LOWER_TIER = "continue-lower-tier"
DECISION_BLOCKED = "blocked"


@dataclasses.dataclass(frozen=True)
class LowerTierDecision:
    decision: str
    reason_code: str
    reason: str
    #: R072 tail: subsequent work returns to Fable 5 at the next safe seam
    #: unless explicit policy says otherwise.
    returns_to_fable_at_next_seam: bool = True


def decide_after_cap(
    journal: Any,
    request_digest: str,
    *,
    same_bounded_task: bool,
    features: WorkloadFeatures | None,
    resolved_model: str,
    model_context_window: int | None,
    packet_target_tokens: int,
    demonstrated_capable: bool,
    approved: ApprovedModels,
    higher_precedence_conflict: str = "",
) -> LowerTierDecision:
    """R072: both fresh Fable attempts refused -> the already-configured
    lower-tier model may continue THAT SAME bounded task under its stricter
    workload-fit rules, or the run blocks citing the exact conflict.

    Conservative on everything: reachable only after the durable cap; a
    different task is refused outright; a live higher-precedence policy
    conflict, an un-allowlisted model, missing workload features, an
    oversized/unknown workload class, or a failed model fit each BLOCK with
    the specific reason (ask the owner to reconcile) rather than continue.
    """
    if not reentry_cap_exhausted(journal, request_digest):
        raise BridgeError(
            "cap_not_exhausted",
            "lower-tier continuation is reachable ONLY after the durable "
            "two-attempt cap for this exact request (D-024-R071/R072)")
    if not same_bounded_task:
        raise BridgeError(
            "different_task_forbidden",
            "R072 never authorizes a different task, broader scope, new "
            "credentials, arbitrary permissions, or a protected action; only "
            "the SAME bounded task may continue")
    if higher_precedence_conflict.strip():
        return LowerTierDecision(
            DECISION_BLOCKED, "higher_precedence_policy_conflict",
            f"a live higher-precedence policy forbids the narrow lower-tier "
            f"fallback: {higher_precedence_conflict.strip()}. Entering blocked "
            f"and asking the owner to reconcile (D-024-R072)")
    try:
        approved.assert_listed(resolved_model)
    except ModelRoutingError as error:
        return LowerTierDecision(
            DECISION_BLOCKED, "lower_tier_not_allowlisted",
            f"the configured lower-tier model is not selectable: {error}")
    if features is None:
        return LowerTierDecision(
            DECISION_BLOCKED, "workload_features_missing",
            "no objective workload features were supplied; unknown is never "
            "treated as fitting (D-024 s5.4 discipline)")
    classification = classify_workload(features)
    if classification.work_class in (OVERSIZED_SPLIT, UNKNOWN_RECON):
        return LowerTierDecision(
            DECISION_BLOCKED, "workload_not_continuable",
            f"the workload classifies as {classification.work_class!r} "
            f"({classification.reason}); the stricter lower-tier profile "
            f"refuses it (D-024-R072)")
    fit = model_fit(resolved_model=resolved_model,
                    model_context_window=model_context_window,
                    packet_target_tokens=packet_target_tokens,
                    demonstrated_capable=demonstrated_capable)
    if not fit.ok:
        return LowerTierDecision(
            DECISION_BLOCKED, fit.reason_code,
            f"the stricter lower-tier health/workload-fit profile refuses the "
            f"continuation: {fit.reason}")
    return LowerTierDecision(
        DECISION_CONTINUE_LOWER_TIER, "lower_tier_fit",
        f"{resolved_model!r} may continue the SAME bounded task under its "
        f"stricter controller-only health profile ({fit.reason}); subsequent "
        f"work returns to Fable 5 at the next safe seam (D-024-R072). This is "
        f"a recorded decision; actuation stays owner-gated")


def next_seam_model(*, fable_model: str, explicit_policy_model: str = "") -> str:
    """R072 tail: return to Fable 5 at the next safe seam for subsequent work
    unless explicit policy names another model."""
    if not fable_model.strip():
        raise BridgeError("missing_fable_model",
                          "the return-to model must be named explicitly")
    return explicit_policy_model.strip() or fable_model


# --------------------------------------------------------------------------
# R165 - the native fallbackModel boundary
# --------------------------------------------------------------------------


def fallback_model_scope(native_fallback_configured: bool) -> dict[str, Any]:
    """R165: Claude Code's native ``fallbackModel`` covers only supported
    availability/overload cases. It NEVER substitutes for the custom
    guardrail-refusal policy (this module + `guardrail_refusal`) or the quota
    detect-and-hold policy (`claude_runner` + `model_turnover`), whether or
    not it is configured - the constants below are the policy boundary and do
    not vary with the setting."""
    return {
        "native_fallback_configured": bool(native_fallback_configured),
        "native_fallback_scope": "supported availability/overload cases only",
        "native_fallback_governs_guardrail_refusals": False,
        "native_fallback_governs_quota_exhaustion": False,
        "guardrail_refusal_policy": "guardrail_refusal.classify_guardrail_refusal "
                                    "+ refusal_bridge (this module)",
        "quota_policy": "claude_runner.classify_quota_exhaustion + "
                        "model_turnover.classify_exhaustion (detect-and-hold)",
    }


# --------------------------------------------------------------------------
# Labeled status facts (unit-G operator_status pattern: unknown never zero)
# --------------------------------------------------------------------------


def refusal_status_facts(journal: Any) -> list[dict[str, str]]:
    """Bridge/refusal state as labeled, sourced facts. Unknown is reported as
    the word "unknown", never coerced to zero or an empty success."""
    facts: list[dict[str, str]] = []
    last = journal.get_state(LAST_REFUSAL_KEY, None)
    facts.append({
        "label": "last_recognized_refusal_digest",
        "value": str(last) if isinstance(last, str) and last else "none-recorded",
        "source": "durable journal",
        "confidence": "recorded",
    })
    if isinstance(last, str) and last:
        counter = journal.get_state(_reentry_key(last), None)
        if isinstance(counter, Mapping) and isinstance(counter.get("attempts"), int):
            value = str(counter["attempts"])
        else:
            value = "none-recorded"
        facts.append({
            "label": "reentry_attempts_for_last_refusal",
            "value": value,
            "source": "durable journal (digest-bound counter)",
            "confidence": "recorded",
        })
    return facts


# --------------------------------------------------------------------------
# The loop-facing seam object (mirrors worker_turnover.WorkerTurnoverIntegration)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class GuardrailBridgeDecision:
    """What the refusal seam learned. ``triggered`` is the ONLY divergence
    signal; ``actuated`` is ALWAYS False on this build (record-intent-only:
    live bridge actuation is owner-gated behind R595 plus a measured-live C1
    shape, and no actuation channel exists here at all)."""

    triggered: bool
    actuated: bool
    reason_code: str
    reason: str
    verdict: RefusalVerdict
    request_digest: str = ""
    audit_summary: dict[str, Any] = dataclasses.field(default_factory=dict)


class GuardrailBridgeIntegration:
    """The injectable seam the loop consults AFTER the quota turnover seam.

    Constructed with the durable journal (for the R070 step-1 record), the
    proven `AuthorizedTaskRecord`, and optionally a test corpus. There is
    deliberately NO actuation channel parameter: unlike the quota seam's
    R595-activatable controller, the refusal bridge records intent
    unconditionally on this build.
    """

    def __init__(
        self,
        *,
        journal: Any,
        authorized_task: AuthorizedTaskRecord | None,
        corpus: tuple[RefusalShapeFixture, ...] | None = None,
    ) -> None:
        self._journal = journal
        self._authorized_task = authorized_task
        self._corpus = corpus

    @staticmethod
    def evidence_from_run_result(run_result: Any, *,
                                 current_model: str) -> RefusalEvidence:
        """Build refusal evidence from the bounded-unit result.

        Field extraction mirrors `worker_turnover.evidence_from_run_result`
        (checkpoint_error + result_text into stdout, stderr_tail, observed
        return code, model attribution). The structured candidate PREFERS a
        raw `rate_limit_rejection` when one exists - so the quota-direction
        delegate inside the classifier sees it and routes it to the quota
        policy (R075) - and otherwise carries the stream's terminal `result`
        event, where a typed refusal stop_reason would surface.
        """
        stderr = str(getattr(run_result, "stderr_tail", "") or "")
        checkpoint_error = str(getattr(run_result, "checkpoint_error", "") or "")
        result_text = str(getattr(run_result, "result_text", "") or "")
        stdout = "\n".join(p for p in (checkpoint_error, result_text) if p)
        structured: Mapping[str, Any] | None = None
        rejection = getattr(run_result, "rate_limit_rejection", None)
        if isinstance(rejection, Mapping):
            structured = rejection
        else:
            for event in reversed(tuple(getattr(run_result, "raw_events", ()) or ())):
                if isinstance(event, Mapping) and event.get("type") == "result":
                    structured = event
                    break
        return RefusalEvidence(
            stdout=stdout, stderr=stderr,
            exit_code=getattr(run_result, "returncode", None),
            structured_result=structured,
            model_id=str(current_model or ""))

    def evaluate(
        self,
        run_result: Any,
        *,
        current_model: str,
        config: Any,
        run_id: str,
        cycle: int,
    ) -> GuardrailBridgeDecision:
        """Classify the failed unit; RECORD INTENT ONLY on a recognized refusal.

        Called only after the quota turnover seam declined to diverge, so the
        quota detect-and-hold policy always evaluates first at the loop level
        (R075 precedence), on top of the classifier's own quota-direction
        delegate. ``config`` is accepted for signature parity with the quota
        seam and future policy inputs; no attribute of it authorizes actuation.
        """
        del config  # no config attribute can authorize actuation on this build
        evidence = self.evidence_from_run_result(run_result,
                                                 current_model=current_model)
        verdict = classify_guardrail_refusal(
            evidence, authorized_task=self._authorized_task,
            corpus=self._corpus)
        if not verdict.is_recognized_refusal:
            return GuardrailBridgeDecision(
                triggered=False, actuated=False, reason_code="",
                reason=verdict.reason, verdict=verdict)

        authorized = self._authorized_task
        if authorized is None:  # defensive: a recognized refusal requires proof
            return GuardrailBridgeDecision(
                triggered=False, actuated=False, reason_code="",
                reason="recognized verdict without a proven authorization "
                       "record; refusing to record a bridge event (fail closed)",
                verdict=verdict)
        request_digest = digest_of({
            "task_id": authorized.task_id,
            "authorization": authorized.authorization,
            "acceptance_criteria": list(authorized.acceptance_criteria),
            "purpose": authorized.purpose,
            "run_id": run_id,
        })
        record = build_refusal_journal_record(
            verdict, authorized, request_digest=request_digest,
            evidence_excerpt=evidence.stdout or evidence.stderr)
        self._journal.set_state(
            f"{REFUSAL_RECORD_KEY_PREFIX}{request_digest}", record)
        self._journal.set_state(LAST_REFUSAL_KEY, request_digest)
        reason = (
            "a narrowly recognized Fable guardrail refusal was classified "
            f"({verdict.matched_shape!r}, "
            f"{'measured-live' if verdict.shape_verified_live else 'documented candidate'}) "
            "and journaled with the task identity and exact authorization/"
            "acceptance criteria preserved (D-024-R070 step 1). The 4.8 bridge "
            "is NOT actuated: this build records intent only (SHADOW-ONLY; "
            "live actuation requires the owner's R595 activation and a "
            "measured-live C1 shape). The run keeps its safe PAUSE")
        return GuardrailBridgeDecision(
            triggered=True, actuated=False,
            reason_code=REASON_REFUSAL_RECORDED, reason=reason,
            verdict=verdict, request_digest=request_digest,
            audit_summary={
                "guardrail": "recorded_intent_shadow_only",
                "matched_shape": verdict.matched_shape,
                "shape_verified_live": verdict.shape_verified_live,
                "request_digest": request_digest,
                "cycle": cycle,
            })
