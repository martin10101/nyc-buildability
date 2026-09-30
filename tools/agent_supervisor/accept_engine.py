#!/usr/bin/env python3
"""The post-wave acceptance engine: independent-verifier seam + accept() invocation.

M0-T153 (D-033 T-B). Qualifying evidence under `.claude/rules/supervisor-freeze.md`
section 2: the captured requirements D-033-R002 (supervisor-run acceptance) and
D-033-R006 (machine-enforced separation of duties), cited in both the task packet
and the commit message as section 3 requires. Design:
`docs/SUPERVISOR_MANAGEMENT_LAYER_DESIGN.md` sections 3, 4, 7 (seam I3).

What lives here (a NEW module; `loop.py`/`gate_wave.py` each own one stage):
the stage-2 owner switch (DEFAULT OFF, refusal-by-name); ONE independent
verifier-session dispatch over the bounded `conduct_ephemeral_review`
machinery, its packet supplying the CITED directive registry (the verifier's
applicability source, never the whole registry AD-083 prohibits); the
transcription seam (row extraction under the 64k ceiling, WORST-OF dedup, the
atomic `task_verifications[]` merge into each cited `verification.json`); the
I3 content-identity guard (HEAD drift -> ``restamp_required``); and the
bounded `accept` recorder (allow-set ``{accept}``, current queue task only,
invoking the REAL `project_control.py accept` - this module supplies inputs
and changes NO check).

THE SWITCH IS DEFAULT OFF (D-033-R005). With the flag absent,
`run_with_post_complete_stage` here IS the T-A call byte-for-byte: no enable
record, no verifier dispatch, no verification write, no accept() run. Stage 2
is scoped to GOVERNANCE-class tasks only (design Section 7 stage 2); queue
advance, commits, and integration remain T-C scope and stay with the
orchestrator. Nothing here pushes, deploys, or crosses an owner hold.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import sys
import tempfile
import uuid
from typing import Any, Callable, Mapping, Sequence

from . import gate_wave, refusals
from .audit_log import AuditLog
from .durable_state import runtime_dir_for
from .ephemeral_review import ReviewRecord, conduct_ephemeral_review
from .evidence import EvidenceCollector, build_packet, results_section
from .loop import MODE_LIMITED_AUTO
from .models import digest_of, to_utc_iso
from .process import minimal_env
from .process import run as run_process
from .redaction import redact_structure
from .review_packet import ReviewBudget

ENGINE_VERSION = "1.0.0"

MANAGED_ACCEPTANCE_FLAG = "--owner-enable-managed-acceptance"
#: The ONLY admissible stage-2 value (design Section 7): acceptance for
#: governance-class tasks whose blast radius is the ledger. Product-code
#: acceptance stays with the orchestrator until a later owner-typed stage.
GOVERNANCE_CLASS = "governance"

#: The independent verifier identity the DCV row must come from (design 3.3).
#: It must appear in the packet's OWN reviewer_agents roster; the engine never
#: invents a verifier identity the packet did not authorize.
VERIFIER_IDENTITY = "directive-compliance-verifier"

VERIFIER_CONTRACT_KEY = "directive_verification_contract"

#: The 64k agent-output ceiling on the transcription seam (design 3.3; memory
#: `in-regime-accept-mechanics`: a row set over the verifier session's output
#: ceiling fails - rows must come per-cluster across MULTIPLE sealed records,
#: assembled here with worst-of dedup, never forced through one output).
#: Measured in serialized UTF-8 bytes per sealed record's row payload: bytes
#: are mechanically measurable where provider tokens are not, and a 64_000-byte
#: bound is strictly conservative against a 64_000-token one, so the guard can
#: only refuse earlier than the provider would truncate - never later.
ROWS_CEILING_BYTES = 64_000

#: WORST-OF dedup ranking (higher = worse). When the same requirement id
#: appears more than once across the verifier's row payloads, the WORST state
#: wins - a lenient duplicate can never flip a stricter one back to PASS
#: (memory `in-regime-accept-mechanics`, R593: last-wins masked a real gap).
#: An unknown state ranks WORST of all: fail closed, never fail lenient.
ROW_STATE_RANK: Mapping[str, int] = {
    "PASS": 0, "NOT_APPLICABLE": 1, "pending": 2,
    "UNVERIFIABLE": 3, "FAIL": 4, "BLOCKED": 5,
}
UNKNOWN_STATE_RANK = 6

#: F1 discipline carried from the wave recorder: the acceptance engine's ONLY
#: `project_control.py` surface is `accept`, for the current queue task only.
ACCEPT_ALLOW_SET = frozenset({"accept"})
_ACCEPT_ARGUMENTS: Mapping[str, frozenset[str]] = {
    "accept": frozenset({"--agent"}),
}

#: Durable journal key + audit events for the per-launch stage-2 enable
#: (same disclosure discipline as the wave enable, design 6.1).
ENABLE_STATE_KEY = "managed_acceptance/enabled"
ENABLE_EVENT = "managed_acceptance_enabled"
REFUSAL_EVENT = "managed_acceptance_launch_refused"
STAGE_FINISHED_EVENT = "managed_acceptance_finished"

ACCEPTED = "accepted"
PARKED = "parked"
RESTAMP_REQUIRED = "restamp_required"

#: Row encoding through the REAL provider boundary. The reviewer's structured
#: output is validated against `schemas/codex_decision.schema.json`, whose
#: `verified_facts` items are EXACTLY {"fact": <string>} with
#: additionalProperties false - the provider cannot emit richer row objects,
#: and `codex_reviewer.validate_decision` is the supervisor-side authority
#: over the same flattened shape. Each verification ROW therefore rides
#: INSIDE one fact string: this sentinel prefix followed by ONE JSON object.
#: A fact without the sentinel is ordinary reviewer prose, never a row; a
#: sentinel fact whose payload does not parse to a JSON object fails CLOSED.
ROW_SENTINEL = "DCV-ROW:"

#: The verifier-session contract (design 3.3). Rides in the packet under
#: `directive_verification_contract`; carries the F3 immunization clause
#: verbatim so worker-authored packet content can never steer the rows.
VERIFIER_CONTRACT = (
    "DIRECTIVE VERIFICATION (independent directive-compliance-verifier session): "
    "derive the applicable requirement set for THIS task from each cited directive's "
    "registry files, then verify each applicable requirement strictly against the "
    "packet evidence at the reviewed content identity. Your structured output schema "
    'allows verified_facts entries of EXACTLY the shape {"fact": "<string>"}. Encode '
    "each per-requirement verification row as ONE such entry whose fact string is "
    "the sentinel prefix '" + ROW_SENTINEL + "' followed immediately by ONE "
    'minified JSON object {"directive_id": ..., "requirement_id": ..., "state": ..., '
    '"evidence": ..., "note": ...}; state is PASS only for evidence you verified '
    "yourself, or NOT_APPLICABLE with not_applicable_justification and "
    "not_applicable_approved_by keys in the same object; anything you cannot ground "
    "is UNVERIFIABLE, never PASS. A cited directive with an EMPTY applicable set "
    'gets one row object {"directive_id": ..., "applicable_requirement_ids": []} '
    "instead. Facts without the sentinel are your ordinary findings and are never "
    "transcribed as rows. Keep the total row payload well under the 64k output "
    "ceiling; when the applicable set is too large for one output, return the rows "
    "you verified and state which remain - never truncate silently. A producer "
    "self-check, checklist, or report is a CLAIM, never proof. "
    + gate_wave.WORKER_AUTHORED_DATA_CLAUSE)


class AcceptEngineError(Exception):
    """An acceptance step was refused. Fail closed; never 'no problem found'."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class ManagedAcceptanceRefused(AcceptEngineError):
    """The acceptance stage was reached without the owner enable. Refused by name."""

    def __init__(self) -> None:
        super().__init__(
            "managed_acceptance_refused",
            "managed acceptance is DISABLED for this launch. The post-wave "
            "acceptance stage (D-033-R002) is implemented but DEFAULT OFF and is "
            "never reachable from a configuration default, a missing value, a "
            "parse error, a migration, or a downgrade. Enabling it is a separate "
            "explicit owner activation, supplied per launch as "
            f"{MANAGED_ACCEPTANCE_FLAG}={GOVERNANCE_CLASS} on a launch that also "
            "carries the stage-1 wave enable (D-033-R003; the R595 activation "
            "path and every owner hold are unchanged, D-033-R005).")


# --------------------------------------------------------------------------
# The switch (stage 2; same F6 discipline as the wave switch)
# --------------------------------------------------------------------------


def add_owner_switch_argument(parser: Any) -> None:
    """Register the stage-2 owner switch on `start` (cli.py's wiring is this call).

    Lives here so the flag string, its single admissible value, and the gate
    that reads it are one module; cli.py carries no second copy.
    """
    parser.add_argument(
        MANAGED_ACCEPTANCE_FLAG, choices=[GOVERNANCE_CLASS], default="",
        help="M0-T153 (D-033-R002): the owner's EXPLICIT per-launch enable for the "
             "post-wave acceptance stage (stage 2 of the D-033 ladder), scoped to "
             f"{GOVERNANCE_CLASS}-class tasks only. After a green managed gate wave "
             "the controller dispatches ONE independent directive-compliance-verifier "
             "session, transcribes its rows into the directive verification file, and "
             "invokes the REAL project_control.py accept - every accept() fail-closed "
             "precondition unchanged. DEFAULT OFF: without it every mode behaves "
             "byte-identically to today, and supplying it without the stage-1 wave "
             "enable plus the owner-gated bounded capability is a STRUCTURED refusal "
             "by name, never a silent ignore. Queue advance, commits, and integration "
             "remain with the orchestrator (T-C scope; D-033-R005)")


def assert_acceptance_enabled(owner_value: str) -> None:
    """THE load-bearing stage-2 switch check. Every stage entry point calls it.

    The OFF==today proof obligation targets exactly this line: the mutation
    test disables it and asserts the switch-off scenario then wrongly runs the
    stage, proving the check is what stands between OFF and an accept().
    """
    if str(owner_value or "") != GOVERNANCE_CLASS:
        raise ManagedAcceptanceRefused()


def managed_acceptance_start_gate(args: Any,
                                  seal_audit: str = "") -> refusals.Refusal | None:
    """The symmetric refusal at `start`, mirroring `managed_wave_start_gate`.

    None means "not refused". Stage 2 strictly contains stage 1 (design
    Section 7), so the acceptance flag is refused BY NAME unless the launch
    also carries the wave enable AND the owner-gated bounded capability.
    """
    value = str(getattr(args, "owner_enable_managed_acceptance", "") or "")
    if not value:
        return None
    mode = str(getattr(args, "mode", "") or "")
    waves = bool(getattr(args, "owner_enable_managed_gate_waves", False))
    gated = (mode == MODE_LIMITED_AUTO
             and bool(getattr(args, "owner_enable_bounded_auto", False)))
    if value == GOVERNANCE_CLASS and waves and gated:
        return None
    if value != GOVERNANCE_CLASS:
        reason_code = "managed_acceptance_unknown_class"
        message = (f"{MANAGED_ACCEPTANCE_FLAG}={value!r} names no admissible "
                   f"stage-2 task class; only {GOVERNANCE_CLASS!r} exists "
                   f"(design Section 7 stage 2). Refused, never coerced.")
    elif not waves:
        reason_code = "managed_acceptance_without_wave_enable"
        message = (f"{MANAGED_ACCEPTANCE_FLAG}={value} was supplied without "
                   f"{gate_wave.MANAGED_WAVE_FLAG}; stage 2 (acceptance) "
                   f"strictly contains stage 1 (gate waves) and is refused by "
                   f"name without it (design Section 7).")
    else:
        reason_code = "managed_acceptance_without_gated_mode"
        message = (f"{MANAGED_ACCEPTANCE_FLAG}={value} was supplied for mode "
                   f"{mode!r} without the owner-gated capability that can host "
                   f"it (mode {MODE_LIMITED_AUTO!r} plus "
                   f"--owner-enable-bounded-auto). The stage is DEFAULT OFF "
                   f"(D-033-R003) and an enable that does not name a capability "
                   f"able to host it is refused rather than ignored.")
    item = refusals.refusal(
        refusals.REFUSED_MODE, reason_code=reason_code, message=message,
        detail={"mode": mode, "owner_enable_input": MANAGED_ACCEPTANCE_FLAG,
                "value": value,
                "requires": [f"--mode {MODE_LIMITED_AUTO}",
                             "--owner-enable-bounded-auto",
                             gate_wave.MANAGED_WAVE_FLAG]})
    if seal_audit:
        _seal_refusal(args, item, seal_audit)
    return item


def _seal_refusal(args: Any, item: refusals.Refusal, audit_filename: str) -> None:
    """Seal a refused stage-2 launch in the hash-chained audit log (C6 shape)."""
    try:
        checkout = pathlib.Path(args.checkout).resolve()
        runtime = runtime_dir_for(checkout, base=args.runtime_base)
        AuditLog(runtime / audit_filename).append(
            REFUSAL_EVENT, decision="refuse", policy_result=item.reason_code,
            detail={"mode": getattr(args, "mode", ""), "outcome": item.outcome,
                    "exit_code": item.exit_code,
                    "note": "an attempted managed-acceptance launch was refused "
                            "by the owner gate; every activation hold is "
                            "unchanged (D-033-R005)"})
    except Exception:  # pragma: no cover - a refusal never becomes a crash
        pass


def register_stage_switches(parser: Any) -> None:
    """Register BOTH D-033 stage switches on `start`. cli.py's wiring is this
    ONE call (M0-T153 stage-wiring consolidation).

    The stage ladder is one surface: stage 1 (gate waves) and stage 2 (managed
    acceptance) are enabled by sibling per-launch owner flags, both DEFAULT
    OFF, and registering them together keeps cli.py at a single wiring line
    that cannot drift out of step with the gates below.
    """
    gate_wave.add_owner_switch_argument(parser)
    add_owner_switch_argument(parser)


def stage_start_gate(args: Any, seal_audit: str = "") -> refusals.Refusal | None:
    """The consolidated `start` refusal gate for both D-033 stage enables.

    None means "not refused". Checked in ladder order - the stage-1 wave gate
    first (F6), then the stage-2 acceptance gate (which itself requires the
    wave enable) - so every refusal names the FIRST missing capability. Each
    underlying gate seals its own refusal in the hash-chained audit log when
    `seal_audit` names the file (the C6 shape); cli.py stays one wiring line.
    """
    item = gate_wave.managed_wave_start_gate(args, seal_audit=seal_audit)
    if item is not None:
        return item
    return managed_acceptance_start_gate(args, seal_audit=seal_audit)


def record_enable(journal: Any, audit: Any, run_id: str,
                  now: Callable[[], str] = to_utc_iso) -> dict[str, Any]:
    """The durable per-launch stage-2 enable record (disclosure, design 6.1)."""
    record = {"enabled": True, "run_id": run_id,
              "flag": f"{MANAGED_ACCEPTANCE_FLAG}={GOVERNANCE_CLASS}",
              "task_class": GOVERNANCE_CLASS, "enabled_at_utc": now(),
              "note": "per-launch owner enable for the managed acceptance stage "
                      "(D-033-R002); stage 2 - governance-class accept() after a "
                      "green wave; queue advance/commit/integration stay with "
                      "the orchestrator (T-C scope)"}
    journal.set_state(ENABLE_STATE_KEY, record)
    if audit is not None:
        audit.append(ENABLE_EVENT, run_id=run_id, detail=record)
    return record


# --------------------------------------------------------------------------
# Independent verifier-session dispatch (design 3.3)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class VerifierDispatch:
    """The controller-side record of the ONE verifier-session dispatch.

    Same authorship rule as `gate_wave.GateDispatch`: every field is authored
    by the CONTROLLER from worker-uninfluencable sources, and the digest binds
    the sealed record that comes back to exactly this dispatch.
    """

    dispatch_id: str
    run_id: str
    task_id: str
    checkpoint_id: str
    directive_ids: tuple[str, ...]
    verifier_identity: str
    producer_identity: str
    reviewed_sha: str
    created_at_utc: str
    dispatch_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["directive_ids"] = list(self.directive_ids)
        return data


def _assert_verifier_separated(verifier_identity: str,
                               producer_identity: str) -> None:
    """D-033-R006: verifier != producer, fail closed - the DCV row's authorship.

    MUTATION-TESTED: the producer==verifier mutation test disables this
    function and asserts a self-verifying dispatch then succeeds, proving the
    check is load-bearing (design Section 4, row 6). `accept()` re-checks the
    written rows independently (`directive_registry._v2_task_unresolved`), so
    this is the EARLY refusal, not the only one.
    """
    verifier = str(verifier_identity or "").strip()
    producer = str(producer_identity or "").strip()
    if not verifier:
        raise AcceptEngineError(
            "verifier_identity_unresolved",
            "no verifier identity was resolved; a dispatch whose identity "
            "cannot be recorded is refused, never defaulted")
    if not producer:
        raise AcceptEngineError(
            "producer_identity_unresolved",
            "the task packet names no producer identity, so verifier/producer "
            "separation cannot be ESTABLISHED; refused")
    if verifier == gate_wave.RESERVED_ORCHESTRATOR:
        raise AcceptEngineError(
            "verifier_reserved_identity",
            f"{gate_wave.RESERVED_ORCHESTRATOR!r} is the controller's own "
            f"procedural label and can never author an independent "
            f"verification row; the controller is the mechanical recorder, "
            f"neither producer nor verifier (design 3.3)")
    if verifier == producer:
        raise AcceptEngineError(
            "verifier_is_producer",
            f"the verifier identity {verifier!r} equals the producer identity; "
            f"a self-verified DCV row is a forged acceptance surface - "
            f"refused (D-033-R006)")


def verifier_for_packet(packet: Mapping[str, Any]) -> str:
    """The verifier identity, ONLY if the packet's own roster authorizes it."""
    roster = [str(r) for r in (packet.get("reviewer_agents") or [])]
    return VERIFIER_IDENTITY if VERIFIER_IDENTITY in roster else ""


def plan_verifier_dispatch(*, run_id: str, task_id: str, checkpoint_id: str,
                           directive_ids: Sequence[str], verifier_identity: str,
                           producer_identity: str, reviewed_sha: str,
                           now: Callable[[], str] = to_utc_iso) -> VerifierDispatch:
    """Build the dispatch record BEFORE any verifier process exists."""
    _assert_verifier_separated(verifier_identity, producer_identity)
    if not isinstance(checkpoint_id, str) or not checkpoint_id.strip():
        raise AcceptEngineError(
            "checkpoint_unresolved",
            "no terminal checkpoint identity resolved from the run's cycle "
            "records (gate_wave.terminal_checkpoint_id); an unbindable verifier "
            "session is refused before any registry write (fail closed)")
    cited = tuple(sorted({str(d) for d in directive_ids if str(d)}))
    if not cited:
        raise AcceptEngineError(
            "no_directives_cited",
            "the task cites no directives; managed acceptance handles only "
            "in-regime tasks - a legacy task stays with the orchestrator")
    if not str(reviewed_sha or "").strip():
        raise AcceptEngineError(
            "reviewed_sha_unresolved",
            "no reviewed HEAD sha was resolved for the dispatch; rows without "
            "an identity stamp can never satisfy accept() (D-004-R630)")
    body = {"dispatch_id": uuid.uuid4().hex, "run_id": run_id,
            "task_id": task_id, "checkpoint_id": checkpoint_id,
            "directive_ids": cited, "verifier_identity": verifier_identity,
            "producer_identity": producer_identity,
            "reviewed_sha": str(reviewed_sha), "created_at_utc": now()}
    digest = digest_of({**body, "directive_ids": list(cited)})
    return VerifierDispatch(dispatch_digest=digest, **body)


def dispatch_verification(dispatch: VerifierDispatch, packet: Mapping[str, Any],
                          reviewer: Any, *, budget: ReviewBudget | None = None,
                          model_context_window: int | None = None,
                          journal: Any = None,
                          now: Callable[[], str] = to_utc_iso) -> ReviewRecord:
    """The one verifier-session dispatch over the existing bounded machinery.

    Reuses `conduct_ephemeral_review` end to end (AD-083 content guard, 0A.4
    budget, fresh read-only process, sealed durable record) - never a new
    provider path. The verification contract (with the immunization clause)
    rides under `directive_verification_contract`; a packet that pre-supplies
    its own contract is refused as planted.
    """
    if VERIFIER_CONTRACT_KEY in packet:
        raise AcceptEngineError(
            "contract_key_collision",
            f"the evidence packet already carries {VERIFIER_CONTRACT_KEY!r}; a "
            f"packet that pre-supplies its own verification contract is refused")
    body = dict(packet)
    body[VERIFIER_CONTRACT_KEY] = redact_structure({
        "dispatch_id": dispatch.dispatch_id,
        "dispatch_digest": dispatch.dispatch_digest,
        "directive_ids": list(dispatch.directive_ids),
        "reviewed_sha": dispatch.reviewed_sha,
        "contract": VERIFIER_CONTRACT,
    }).value
    return conduct_ephemeral_review(
        reviewer, body, reviewed_task_id=dispatch.task_id,
        reviewed_checkpoint_id=dispatch.checkpoint_id,
        budget=budget or ReviewBudget(),
        model_context_window=model_context_window,
        run_id=dispatch.run_id, journal=journal, now=now)


def _assert_record_bound(dispatch: VerifierDispatch, record: ReviewRecord) -> None:
    """The sealed record must provably belong to THIS dispatch. Fail closed."""
    if str(record.reviewed_task_id) != dispatch.task_id:
        raise AcceptEngineError(
            "verification_task_mismatch",
            f"the verifier record is for task {record.reviewed_task_id!r}, not "
            f"the dispatched {dispatch.task_id!r}; refused")
    if str(record.reviewed_checkpoint_id) != dispatch.checkpoint_id:
        raise AcceptEngineError(
            "verification_checkpoint_mismatch",
            f"the verifier record is for checkpoint "
            f"{record.reviewed_checkpoint_id!r}, not the dispatched "
            f"{dispatch.checkpoint_id!r}; refused")
    if not record.record_digest:
        raise AcceptEngineError(
            "verification_unsealed",
            "the verifier record carries no record_digest; an unsealed row "
            "payload cannot be bound to the dispatch and is refused")


# --------------------------------------------------------------------------
# Row extraction, the 64k ceiling, and worst-of dedup (design 3.3)
# --------------------------------------------------------------------------


def _row_rank(state: Any) -> int:
    return ROW_STATE_RANK.get(str(state), UNKNOWN_STATE_RANK)


def _parse_sentinel_row(index: int, fact: str) -> dict[str, Any] | None:
    """ONE fact string -> its sentinel row object, prose (None), or a refusal.

    The contract's encoding is exact: the sentinel prefix followed immediately
    by ONE JSON object. A fact WITHOUT the sentinel is ordinary reviewer prose
    (never a row). A fact that carries the sentinel anywhere but does not
    decode to one JSON object is a NEAR-ROW: it fails CLOSED rather than being
    demoted to prose, because a silently dropped row is exactly the coverage
    loss the transcription seam exists to prevent.
    """
    stripped = fact.strip()
    if ROW_SENTINEL not in stripped:
        return None
    if not stripped.startswith(ROW_SENTINEL):
        raise AcceptEngineError(
            "malformed_row",
            f"verified_facts[{index}] carries {ROW_SENTINEL!r} but not as its "
            f"prefix; a near-row is refused, never demoted to prose")
    try:
        row = json.loads(stripped[len(ROW_SENTINEL):])
    except ValueError as exc:
        raise AcceptEngineError(
            "malformed_row",
            f"verified_facts[{index}] carries the {ROW_SENTINEL!r} sentinel "
            f"but its payload does not parse as JSON ({exc}); refused")
    if not isinstance(row, Mapping):
        raise AcceptEngineError(
            "malformed_row",
            f"verified_facts[{index}] sentinel payload is "
            f"{type(row).__name__}, not ONE JSON object; refused")
    return dict(row)


def extract_rows(dispatch: VerifierDispatch,
                 record: ReviewRecord) -> list[dict[str, Any]]:
    """Extract the verifier's row payload from ONE sealed record, bounded.

    Reconciled with the REAL validated decision boundary
    (`schemas/codex_decision.schema.json` + `codex_reviewer.validate_decision`):
    `verified_facts` entries are EXACTLY {"fact": <string>} - the provider's
    strict structured-output subset admits no richer row object - so each
    verification row rides INSIDE one fact string as the `ROW_SENTINEL` prefix
    followed by ONE JSON object (the shape `VERIFIER_CONTRACT` demands). Each
    decoded row must name a cited directive and either be a requirement row
    (requirement_id + state) or an explicit empty-applicable-set attestation.
    A non-schema-shaped entry (including the legacy rich-row-object encoding),
    a malformed sentinel payload, an uncited directive, a raw payload over the
    64k transcription ceiling, or a decision with NO sentinel rows at all
    fails CLOSED - never trimmed, never guessed, never read leniently.
    """
    _assert_record_bound(dispatch, record)
    if not record.ok or not isinstance(record.decision, Mapping):
        raise AcceptEngineError(
            "verifier_unavailable",
            f"the verifier session returned no adjudicable decision "
            f"({record.error_code or 'no decision'}); absent rows are never "
            f"an accepted verification")
    raw = record.decision.get("verified_facts")
    if not isinstance(raw, list):
        raise AcceptEngineError(
            "no_verification_rows",
            "the verifier decision carries no verified_facts list; an absent "
            "payload can never satisfy a cited directive (fail closed)")
    # The ceiling is measured on the RAW payload - serialized bytes of the
    # whole verified_facts list, BEFORE any parsing - so an oversized output
    # is refused ahead of everything else, never partially transcribed.
    payload_bytes = len(json.dumps(raw, ensure_ascii=False).encode("utf-8"))
    if payload_bytes > ROWS_CEILING_BYTES:
        raise AcceptEngineError(
            "rows_over_ceiling",
            f"the raw verified_facts payload is {payload_bytes} bytes, over "
            f"the {ROWS_CEILING_BYTES}-byte transcription ceiling (the 64k "
            f"agent-output bound); rows must arrive per-cluster across "
            f"multiple sealed records, never through one oversized output")
    cited = set(dispatch.directive_ids)
    rows: list[dict[str, Any]] = []
    for index, entry in enumerate(raw):
        if (not isinstance(entry, Mapping) or set(entry) != {"fact"}
                or not isinstance(entry.get("fact"), str)):
            raise AcceptEngineError(
                "malformed_fact",
                f'verified_facts[{index}] is not the schema-conformant '
                f'{{"fact": <string>}} entry shape '
                f'(codex_decision.schema.json, additionalProperties false); '
                f'a record that did not come through the validated decision '
                f'boundary is refused, never read leniently')
        row = _parse_sentinel_row(index, entry["fact"])
        if row is None:
            continue
        directive_id = str(row.get("directive_id", "") or "")
        if directive_id not in cited:
            raise AcceptEngineError(
                "row_for_uncited_directive",
                f"verified_facts[{index}] names directive {directive_id!r}, "
                f"which this dispatch did not cite; a stray row is "
                f"contamination, not coverage (fail closed)")
        if row.get("applicable_requirement_ids") == []:
            rows.append({"directive_id": directive_id,
                         "applicable_requirement_ids": []})
            continue
        requirement_id = str(row.get("requirement_id", "") or "")
        state = row.get("state")
        if not requirement_id or not isinstance(state, str) or not state:
            raise AcceptEngineError(
                "malformed_row",
                f"verified_facts[{index}] ({directive_id}) is neither a "
                f"requirement row (requirement_id + state) nor an explicit "
                f"empty-applicable-set attestation; refused")
        rows.append(row)
    if not rows:
        raise AcceptEngineError(
            "no_verification_rows",
            "the verifier decision carries no sentinel-encoded verification "
            "row; an empty result can never satisfy a cited directive "
            "(fail closed)")
    return rows


def worst_of_merge(rows: Sequence[Mapping[str, Any]]) -> tuple[
        list[dict[str, Any]], list[str]]:
    """Merge row payloads per (directive, requirement) keeping the WORST state.

    Returns (merged rows, conflict notes). MUTATION-TESTED: the dedup mutation
    replaces worst-of with last-wins and asserts a lenient duplicate then
    wrongly flips a stricter state back to PASS (R593's exact failure).
    """
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    empties: dict[str, dict[str, Any]] = {}
    conflicts: list[str] = []
    for row in rows:
        directive_id = str(row.get("directive_id", "") or "")
        if row.get("applicable_requirement_ids") == []:
            empties[directive_id] = dict(row)
            continue
        key = (directive_id, str(row.get("requirement_id", "") or ""))
        existing = merged.get(key)
        if existing is None:
            merged[key] = dict(row)
            continue
        if existing.get("state") != row.get("state"):
            keep = existing if (_row_rank(existing.get("state"))
                                >= _row_rank(row.get("state"))) else dict(row)
            conflicts.append(
                f"{key[0]}/{key[1]}: conflicting duplicate states "
                f"{existing.get('state')!r} vs {row.get('state')!r}; kept the "
                f"worst ({keep.get('state')!r}), never last-wins")
            merged[key] = keep
    ordered = [merged[key] for key in sorted(merged)]
    ordered.extend(empties[d] for d in sorted(empties))
    return ordered, conflicts


def assert_rows_clean(rows: Sequence[Mapping[str, Any]]) -> None:
    """Refuse BEFORE any registry write when the merged rows cannot accept.

    A row that is not PASS - or NOT_APPLICABLE with both its justification and
    its independent approver - would make `accept()` refuse anyway; the engine
    parks first and writes nothing, so a failing verification never lands in
    the directive registry as if it were a clean one.
    """
    problems: list[str] = []
    for row in rows:
        if row.get("applicable_requirement_ids") == []:
            continue
        rid = f"{row.get('directive_id')}/{row.get('requirement_id')}"
        state = row.get("state")
        if state == "PASS":
            continue
        if state == "NOT_APPLICABLE":
            if (row.get("not_applicable_justification")
                    and row.get("not_applicable_approved_by")):
                continue
            problems.append(f"{rid}: NOT_APPLICABLE without justification + "
                            f"independent approver")
            continue
        problems.append(f"{rid}: state {state!r} (not PASS)")
    if problems:
        raise AcceptEngineError(
            "verification_not_clean",
            "the independent verification is not clean; the stage parks and "
            "writes NOTHING to the registry: " + "; ".join(problems))


# --------------------------------------------------------------------------
# Verification-file transcription (design 3.3)
# --------------------------------------------------------------------------


def verification_path_for(repo_root: str, directive_id: str) -> pathlib.Path:
    """The cited directive's verification.json. Exactly one match, else refused."""
    base = pathlib.Path(repo_root) / "project-control" / "directives"
    matches = sorted(base.glob(f"{directive_id}-*/verification.json"))
    if len(matches) != 1:
        raise AcceptEngineError(
            "verification_file_unresolved",
            f"{len(matches)} verification.json candidates for {directive_id} "
            f"under {base}; the engine writes only an unambiguous registry "
            f"file (fail closed)")
    return matches[0]


def build_task_verification(dispatch: VerifierDispatch, directive_id: str,
                            rows: Sequence[Mapping[str, Any]], *,
                            reviewed_manifest_sha256: str,
                            record_digest: str,
                            conflicts: Sequence[str] = (),
                            now: Callable[[], str] = to_utc_iso) -> dict[str, Any]:
    """ONE directive's `task_verifications[]` container row for this task.

    The JUDGMENTS are the verifier's; the controller only transcribes and
    stamps (design 3.3). Requirement rows are stripped to their own directive;
    the declared applicable set is exactly the transcribed row ids, which
    `accept()` re-derives and compares independently (selective-citation gap
    fails closed on the authoritative side).
    """
    own = [dict(r) for r in rows if str(r.get("directive_id", "")) == directive_id]
    if not own:
        raise AcceptEngineError(
            "no_rows_for_directive",
            f"no verifier rows exist for cited directive {directive_id}; a "
            f"cited directive without even an explicit empty-set attestation "
            f"cannot be transcribed (fail closed)")
    requirement_rows = []
    for row in own:
        if row.get("applicable_requirement_ids") == []:
            continue
        clean = {k: v for k, v in row.items() if k != "directive_id"}
        clean["id"] = str(clean.pop("requirement_id"))
        requirement_rows.append(clean)
    requirement_rows.sort(key=lambda r: r["id"])
    return {
        "task_id": dispatch.task_id,
        "directive_id": directive_id,
        "producer": dispatch.producer_identity,
        "verifier": dispatch.verifier_identity,
        "reviewed_manifest_sha256": reviewed_manifest_sha256,
        "reviewed_sha": dispatch.reviewed_sha,
        "applicable_requirement_ids": [r["id"] for r in requirement_rows],
        "requirements": requirement_rows,
        "transcription": {
            "engine_version": ENGINE_VERSION, "run_id": dispatch.run_id,
            "dispatch_id": dispatch.dispatch_id,
            "dispatch_digest": dispatch.dispatch_digest,
            "verifier_record_digest": record_digest,
            "worst_of_conflicts": list(conflicts),
            "transcribed_at_utc": now(),
            "note": "rows authored by the independent verifier session; the "
                    "controller transcribed and stamped them (D-033 design "
                    "3.3); accept() re-derives applicability and re-checks "
                    "every row independently"},
    }


def transcribe_task_verification(path: pathlib.Path,
                                 container_row: Mapping[str, Any]) -> dict[str, Any]:
    """Merge THIS task's row into the directive's v2 verification.json, atomically.

    Every other task's row is preserved byte-for-byte; this task's prior row
    (at most one) is replaced - a fresh identity-bound verification supersedes
    a stale one, never coexists with it. A missing, unreadable, non-v2, or
    ambiguous document fails CLOSED; the engine never creates or upgrades a
    registry file.
    """
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise AcceptEngineError(
            "verification_file_unreadable",
            f"{path} cannot be read as JSON ({exc}); the engine never "
            f"creates or repairs a registry file (fail closed)")
    if doc.get("schema") != "directive_verification/v2":
        raise AcceptEngineError(
            "verification_schema_unsupported",
            f"{path} carries schema {doc.get('schema')!r}, not "
            f"directive_verification/v2; the engine never upgrades a registry "
            f"document (fail closed)")
    rows = doc.get("task_verifications")
    if not isinstance(rows, list):
        raise AcceptEngineError(
            "verification_file_malformed",
            f"{path} has no task_verifications[] list (fail closed)")
    task_id = container_row["task_id"]
    directive_id = container_row["directive_id"]
    matches = [i for i, tv in enumerate(rows) if isinstance(tv, dict)
               and tv.get("task_id") == task_id
               and tv.get("directive_id", directive_id) == directive_id]
    if len(matches) > 1:
        raise AcceptEngineError(
            "verification_rows_ambiguous",
            f"{path} already holds {len(matches)} rows for "
            f"{directive_id}/{task_id}; an ambiguous document is repaired by "
            f"the orchestrator, never by the engine (fail closed)")
    replaced = bool(matches)
    if matches:
        rows[matches[0]] = dict(container_row)
    else:
        rows.append(dict(container_row))
    serialized = json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent),
                                    prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(serialized + "\n")
        os.replace(tmp_name, path)
    except OSError as exc:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise AcceptEngineError(
            "verification_write_failed",
            f"atomic write of {path} failed ({exc}); the prior document is "
            f"untouched (fail closed)")
    return {"path": str(path), "directive_id": directive_id,
            "task_id": task_id, "replaced_prior_row": replaced}


# --------------------------------------------------------------------------
# I3: content-identity freshness (design 3.4)
# --------------------------------------------------------------------------


def assert_identity_fresh(stamped_sha: str, live_head: str) -> None:
    """The reviewed stamp must equal live HEAD at accept time. MUTATION-TESTED.

    `accept()` compares reviewed_sha itself (D-004-R630), so this guard is the
    EARLY, non-authoritative copy whose job is to turn drift into the design's
    prescribed outcome - re-stamp and RE-VERIFY at the new identity - instead
    of a late refusal. Rows are never mutated to the new sha: a stamp records
    what the verifier actually saw, and forging it forward would be
    exactly the staleness accept() exists to refuse.
    """
    stamped = str(stamped_sha or "").strip()
    live = str(live_head or "").strip()
    if not stamped or not live:
        raise AcceptEngineError(
            "identity_unresolvable",
            "the reviewed stamp or live HEAD is unresolved; freshness cannot "
            "be ESTABLISHED and the stage parks (fail closed)")
    if stamped != live:
        raise AcceptEngineError(
            "head_drift",
            f"HEAD moved from the reviewed {stamped} to {live} after the "
            f"verifier session; the stage re-stamps by RE-VERIFYING at the "
            f"new identity (I3) - it never accepts against a stale stamp and "
            f"never rewrites a stamp the verifier did not see")


# --------------------------------------------------------------------------
# The bounded accept recorder (F1 discipline)
# --------------------------------------------------------------------------


class AcceptRecorder:
    """The engine's ONLY path to a `project_control.py` invocation.

    Bounded by `ACCEPT_ALLOW_SET` ({accept}) and pinned to the CURRENT queue
    task at construction. It invokes the real CLI - every accept()
    precondition validates on the authoritative side - and is deliberately a
    SEPARATE class from `gate_wave.ControlPlaneRecorder`: gate/submit and
    accept are different authority surfaces, each with its own fixed
    allow-set, and neither can reach the other's subcommands.
    """

    def __init__(self, *, queue_task_id: str, repo_root: str,
                 python_executable: str = "",
                 runner: Callable[..., Any] | None = None,
                 timeout_seconds: float = 120.0) -> None:
        clean = str(queue_task_id or "").strip()
        if not clean or clean.startswith("-"):
            raise AcceptEngineError("bad_queue_task",
                                    f"queue task id {queue_task_id!r} is unusable")
        self.queue_task_id = clean
        self.repo_root = str(pathlib.Path(repo_root).resolve())
        self.python_executable = python_executable or sys.executable
        self._script = pathlib.Path(self.repo_root) / "tools" / "project_control.py"
        self._runner = runner or run_process
        self.timeout_seconds = timeout_seconds

    def _assert_subcommand_allowed(self, subcommand: str) -> None:
        """The fixed allow-set. MUTATION-TESTED (load-bearing)."""
        if subcommand not in ACCEPT_ALLOW_SET:
            raise AcceptEngineError(
                "subcommand_not_allowed",
                f"project_control subcommand {subcommand!r} is outside the "
                f"acceptance allow-set {sorted(ACCEPT_ALLOW_SET)}; the engine "
                f"never runs gate/submit/new-task/unlock/depend/master-plan/"
                f"hold/directive writes")

    def _assert_current_queue_task(self, task_id: str) -> None:
        """The current-queue-task bound. MUTATION-TESTED (load-bearing)."""
        if str(task_id) != self.queue_task_id:
            raise AcceptEngineError(
                "task_not_current_queue",
                f"task {task_id!r} is not the current queue task "
                f"{self.queue_task_id!r}; the recorder is pinned to ONE task "
                f"and refuses every other id")

    def build_argv(self, subcommand: str, task_id: str,
                   arguments: Mapping[str, str]) -> tuple[str, ...]:
        self._assert_subcommand_allowed(subcommand)
        self._assert_current_queue_task(task_id)
        allowed_keys = _ACCEPT_ARGUMENTS.get(subcommand, frozenset())
        argv: list[str] = [self.python_executable, str(self._script), subcommand,
                           "--task-id", task_id]
        for key in sorted(arguments):
            value = str(arguments[key])
            if key not in allowed_keys:
                raise AcceptEngineError(
                    "argument_not_allowed",
                    f"argument {key!r} is outside the {subcommand!r} "
                    f"allow-list {sorted(allowed_keys)}")
            if value.startswith("-"):
                raise AcceptEngineError(
                    "argument_value_refused",
                    f"value {value!r} for {key} begins with '-' and could be "
                    f"parsed as a different flag; refused")
            argv.extend((key, value))
        return tuple(argv)

    def record_accept(self, task_id: str) -> Any:
        """Invoke the REAL accept() with the procedural orchestrator label."""
        argv = self.build_argv("accept", task_id,
                               {"--agent": gate_wave.RESERVED_ORCHESTRATOR})
        return self._runner(list(argv), cwd=self.repo_root, env=minimal_env(),
                            timeout=self.timeout_seconds)


# --------------------------------------------------------------------------
# The acceptance stage (design 3.1-3.4)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AcceptDeps:
    """Injected dependencies. Tests drive fakes; the live seam builds real ones."""

    collector: EvidenceCollector
    reviewer: Any
    recorder: AcceptRecorder
    repo_root: str
    budget: ReviewBudget | None = None
    model_context_window: int | None = None
    review_journal: Any = None
    audit: Any = None


@dataclasses.dataclass(frozen=True)
class AcceptResult:
    """How the acceptance stage ended. `accepted` records; T-C advances."""

    task_id: str
    status: str
    reason: str
    dispatch_id: str = ""
    verifier_record_digest: str = ""
    transcriptions: tuple[dict[str, Any], ...] = ()
    accept_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["engine_version"] = ENGINE_VERSION
        data["transcriptions"] = [dict(t) for t in self.transcriptions]
        return data


def _parked(task_id: str, reason: str) -> AcceptResult:
    """A park is an owner/exception-plane event, never a degrade (Section 5)."""
    return AcceptResult(task_id=task_id, status=PARKED, reason=reason)


def _assert_wave_satisfies(packet: Mapping[str, Any],
                           wave_result: Mapping[str, Any]) -> None:
    """The wave behind an acceptance must be green AND independently reviewed.

    SELF-CHECK-NEVER-SATISFIES, engine side: every required independent gate
    must appear in the wave's outcomes as kind `independent` with result PASS;
    a `self_check` outcome for an independent gate is a forged wave and is
    refused here BEFORE any verifier dispatch. MUTATION-TESTED (design
    Section 4, row 3); `accept()` re-checks the recorded gate roles
    independently, so this is defense in depth, not the authority.
    """
    if str(wave_result.get("status", "")) != gate_wave.WAVE_COMPLETE:
        raise AcceptEngineError(
            "wave_not_complete",
            f"the gate wave ended {wave_result.get('status')!r}, not "
            f"{gate_wave.WAVE_COMPLETE!r}; acceptance follows only a green "
            f"wave (design 3.1)")
    outcomes = {str(o.get("gate_id")): o
                for o in (wave_result.get("outcomes") or [])
                if isinstance(o, Mapping)}
    required = [str(g) for g in (packet.get("required_gates") or [])
                if str(g) in gate_wave.INDEPENDENT_GATES
                and str(g) not in gate_wave.HUMAN_ONLY_GATES]
    for gate_id in sorted(set(required)):
        outcome = outcomes.get(gate_id)
        if outcome is None:
            raise AcceptEngineError(
                "independent_gate_unwaved",
                f"required independent gate {gate_id} has no wave outcome; a "
                f"gate the wave never recorded can never back an acceptance")
        if str(outcome.get("kind")) != "independent":
            raise AcceptEngineError(
                "self_check_never_satisfies",
                f"the wave outcome for {gate_id} is kind "
                f"{outcome.get('kind')!r}; a self-check can NEVER satisfy an "
                f"independent gate (D-033-R001/R006)")
        if str(outcome.get("result")) != "PASS":
            raise AcceptEngineError(
                "independent_gate_not_pass",
                f"the wave outcome for {gate_id} is {outcome.get('result')!r}, "
                f"not PASS; acceptance follows only a green wave")


def _submission_identity(repo_root: str, task_id: str) -> str:
    """The frozen content identity from the task's submission record.

    `submit` writes `project-control/reports/<task>.json` carrying
    `content_manifest_sha256`; accept() re-derives the live identity and
    refuses a mismatch, so this read is a stamp SOURCE, never a validation
    the engine performs itself.
    """
    path = (pathlib.Path(repo_root) / "project-control" / "reports"
            / f"{task_id}.json")
    try:
        body = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise AcceptEngineError(
            "submission_record_unreadable",
            f"the submission record {path} cannot be read ({exc}); without "
            f"the frozen content identity no verification row can be stamped "
            f"(fail closed)")
    identity = str(body.get("content_manifest_sha256", "") or "")
    if not identity:
        raise AcceptEngineError(
            "submission_identity_missing",
            f"the submission record {path} carries no content_manifest_sha256; "
            f"rows without an identity stamp can never satisfy accept()")
    return identity


def _live_head(collector: EvidenceCollector) -> str:
    head = collector.collect_git_facts().get("head")
    if head is None or not head.ok:
        return ""
    return str(head.value or "").strip()


def run_acceptance_stage(*, packet: Mapping[str, Any], checkpoint_id: str,
                         run_id: str, deps: AcceptDeps, owner_value: str,
                         wave_result: Mapping[str, Any] | None) -> AcceptResult:
    """Run the post-wave acceptance stage for ONE governance-class task.

    Chain (design 3.1): green wave -> ONE verifier session over a bounded packet
    that SUPPLIES the cited directive registry (applicability evidence) ->
    worst-of merge -> clean rows -> transcription at the reviewed identity -> I3
    freshness -> the REAL `accept()`. Every failure parks or typed-restamps and
    nothing advances the queue, commits, pushes, or crosses a hold (T-C scope).
    """
    assert_acceptance_enabled(owner_value)
    task_id = str(packet.get("task_id", "") or "")
    if not task_id:
        return _parked("", "the task packet names no task_id; nothing can be "
                           "accepted (fail closed)")
    if str(packet.get("task_type", "") or "") != GOVERNANCE_CLASS:
        return _parked(task_id,
                       f"task_type {packet.get('task_type')!r} is not "
                       f"{GOVERNANCE_CLASS!r}; stage 2 accepts governance-class "
                       f"tasks only - every other class stays with the "
                       f"orchestrator (design Section 7)")
    directive_ids = [str(r.get("directive_id", "") or "")
                     for r in (packet.get("directive_refs") or [])
                     if isinstance(r, Mapping)]
    directive_ids = [d for d in directive_ids if d]
    if not directive_ids:
        return _parked(task_id,
                       "the task cites no directives; managed acceptance "
                       "handles only in-regime tasks (a legacy task stays "
                       "with the orchestrator)")
    if wave_result is None:
        return _parked(task_id, "no gate-wave result exists for this run; "
                                "acceptance follows only a green wave")
    try:
        _assert_wave_satisfies(packet, wave_result)
        verifier = verifier_for_packet(packet)
        if not verifier:
            return _parked(task_id,
                           f"{VERIFIER_IDENTITY!r} is not in the packet's "
                           f"reviewer_agents roster; the engine never invents "
                           f"a verifier identity (fail closed)")
        producer = str(packet.get("producer_agent", "") or "")
        head = _live_head(deps.collector)
        if not head:
            return _parked(task_id, "live HEAD is unresolved; rows cannot be "
                                    "identity-stamped (fail closed)")
        identity = _submission_identity(deps.repo_root, task_id)
        dispatch = plan_verifier_dispatch(
            run_id=run_id, task_id=task_id, checkpoint_id=checkpoint_id,
            directive_ids=directive_ids, verifier_identity=verifier,
            producer_identity=producer, reviewed_sha=head)
        git_facts = deps.collector.collect_git_facts()
        untracked = results_section(deps.collector.collect_untracked_content(
            git_facts.get("porcelain_status")))
        transcripts = results_section(deps.collector.collect_command_transcripts(
            [str(c) for c in (packet.get("documented_test_commands") or [])]))
        # The bounded packet SUPPLIES only the CITED directives' registry files
        # (requirements.json/manifest.json) so the verifier can DERIVE its
        # applicable set from them: they are TRACKED, so no diff carries them and
        # a fresh read-only reviewer sees them only here. This is the bounded
        # cited slice a review needs - NOT the whole directive registry AD-083
        # (0A.1) prohibits - so the section key names that scope. Only the DCV
        # contract is an instruction; the registry is evidence the immunization
        # clause tells the verifier to inspect, not obey. The dispatch's own
        # cited set is used, so the supply matches exactly the rows' directives.
        cited_reqs = gate_wave.collect_directive_registry(
            deps.collector, deps.repo_root, dispatch.directive_ids)
        packet_result = build_packet(
            run_id=run_id, task_id=task_id, checkpoint_id=checkpoint_id,
            checkpoint=None,
            task_packet=deps.collector.collect_task_packet(task_id),
            git_facts=git_facts,
            extra_sections={"untracked_content": untracked,
                            "command_transcripts": transcripts,
                            "cited_directive_requirements": cited_reqs,
                            "gate_wave_result": dict(wave_result)})
        if not packet_result.ok or packet_result.packet is None:
            return _parked(task_id, f"the verification evidence packet was "
                                    f"refused: {packet_result.reason}")
        record = dispatch_verification(
            dispatch, packet_result.packet.to_dict(), deps.reviewer,
            budget=deps.budget, model_context_window=deps.model_context_window,
            journal=deps.review_journal)
        rows = extract_rows(dispatch, record)
        merged, conflicts = worst_of_merge(rows)
        assert_rows_clean(merged)
        transcriptions = []
        for directive_id in dispatch.directive_ids:
            container = build_task_verification(
                dispatch, directive_id, merged,
                reviewed_manifest_sha256=identity,
                record_digest=record.record_digest, conflicts=conflicts)
            path = verification_path_for(deps.repo_root, directive_id)
            transcriptions.append(transcribe_task_verification(path, container))
        assert_identity_fresh(dispatch.reviewed_sha, _live_head(deps.collector))
    except AcceptEngineError as exc:
        if exc.code == "head_drift":
            return AcceptResult(task_id=task_id, status=RESTAMP_REQUIRED,
                                reason=exc.message)
        return _parked(task_id, f"acceptance refused ({exc.code}): {exc.message}")
    outcome = deps.recorder.record_accept(task_id)
    output = f"{getattr(outcome, 'stdout', '')}{getattr(outcome, 'stderr', '')}"
    if getattr(outcome, "returncode", 1) != 0:
        status, reason = PARKED, (
            "the REAL accept() refused; its reasons are authoritative and the "
            "stage parks rather than retrying (design 3.2)")
    else:
        status, reason = ACCEPTED, (
            "accept() succeeded with every precondition validated on the "
            "authoritative side; queue advance, commit, and integration remain "
            "with the orchestrator (T-C scope, D-033-R005)")
    return AcceptResult(
        task_id=task_id, status=status, reason=reason,
        dispatch_id=dispatch.dispatch_id,
        verifier_record_digest=record.record_digest,
        transcriptions=tuple(transcriptions), accept_output=output)


# --------------------------------------------------------------------------
# The live seam (cli._run_loop's ONE call)
# --------------------------------------------------------------------------


def run_with_post_complete_stage(args: Any, loop: Any, first_prompt: str, *,
                                 packet: Mapping[str, Any], reviewer: Any,
                                 collector: EvidenceCollector, journal: Any,
                                 audit: Any, run_id: str, repo_root: str,
                                 worker_worktree: str,
                                 checkout: str) -> dict[str, Any]:
    """The ONE wiring line `cli._run_loop` calls in place of the T-A seam.

    OFF==today: with `--owner-enable-managed-acceptance` absent this IS
    `gate_wave.run_with_post_complete_stage(...)` byte-for-byte. With the flag
    it re-asserts the owner-gated stage-2 capability HERE (defense in depth
    behind `cmd_start`; MUTATION-TESTED), records the durable enable BEFORE the
    launch, binds the stage to the run record's TERMINAL checkpoint identity
    (`gate_wave.terminal_checkpoint_id`; unresolved -> parked before any
    registry write), and runs stage 2 only after a wave actually ran.
    """
    owner_value = str(getattr(args, "owner_enable_managed_acceptance", "") or "")
    if owner_value:
        item = managed_acceptance_start_gate(args)
        if item is not None:
            raise AcceptEngineError(item.reason_code, item.message)
        record_enable(journal, audit, run_id)
    run = gate_wave.run_with_post_complete_stage(
        args, loop, first_prompt, packet=packet, reviewer=reviewer,
        collector=collector, journal=journal, audit=audit, run_id=run_id,
        repo_root=repo_root, worker_worktree=worker_worktree, checkout=checkout)
    if not owner_value:
        return run
    wave = run.get("managed_gate_wave")
    wave_result = wave if isinstance(wave, Mapping) and wave.get("entered") else None
    deps = AcceptDeps(
        collector=collector, reviewer=reviewer,
        recorder=AcceptRecorder(
            queue_task_id=str(packet.get("task_id", "") or ""),
            repo_root=repo_root),
        repo_root=repo_root, review_journal=None, audit=audit)
    result = run_acceptance_stage(
        packet=packet, checkpoint_id=gate_wave.terminal_checkpoint_id(run),
        run_id=run_id, deps=deps,
        owner_value=owner_value, wave_result=wave_result)
    journal.set_state(f"managed_acceptance/last_stage/{run_id}",
                      result.to_dict())
    if audit is not None:
        audit.append(STAGE_FINISHED_EVENT, run_id=run_id,
                     policy_result=result.status, detail=result.to_dict())
    run["managed_acceptance"] = result.to_dict()
    return run
