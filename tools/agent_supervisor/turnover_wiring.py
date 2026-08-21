#!/usr/bin/env python3
"""Assembling the owner-authorized turnover ACTUATION channels (R595 / M0-T056).

Split out of `cli.py` (M0-T080) so the CLI keeps its argument parsing, its
`doctor` checks, and its command handlers, while the WIRING - which lock, which
survivor detector, which owner-approved successor resolver, and which launcher a
turnover attempt is built from - lives with the turnover stack it composes.
`cli.py` re-exports `run_orchestrator_watchdog`, so `cli.run_orchestrator_watchdog`
keeps working unchanged (`docs/CODE_MODULARITY_POLICY.md` §6).

Nothing here decides anything: the frozen M0-T054 classifier decides whether an
exhaustion is grounded, the frozen `TurnoverController` decides whether a
turnover may proceed, and `approved_models.ModelRouter` decides which model a
successor may be. This module only hands each of them its real dependencies.
"""
from __future__ import annotations

import argparse
import os
import pathlib
from typing import Any

from .approved_models import ApprovedModels, ModelRouter, ProbeLedger
from .audit_log import AuditLog
from .durable_state import DurableJournal, checkout_key, runtime_dir_for
from .locking import SingleInstanceLock
from .model_turnover import TurnoverEvidence, classify_exhaustion
from .models import sha256_hex
from .process import CONTAINMENT_JOB_OBJECT
from .recovery import account_for_children
from .turnover_adapters import (
    HashChainedAuditSink,
    SingleInstanceContinuationLock,
    SuccessorLaunchTargets,
    SupervisorIdentity,
    SupervisorLauncher,
    make_subprocess_command_runner,
)
from .turnover_controller import (
    ALLOWED_SUCCESSOR_EFFORT,
    ApprovedSuccessor,
    TurnoverContext,
    TurnoverController,
    TurnoverLayer,
)

CONTROLLER_VERSION = ""  # set by cli at import time; see `bind_controller_version`

#: The C1 job-object containment gate. `cli.py` owns the host probe, so it is
#: injected rather than imported, which also keeps every existing test's
#: `containment_check=` override working exactly as before.
_containment_precondition = None


def bind_controller_version(version: str) -> None:
    """The CLI owns the controller version constant; the lock file records it."""
    global CONTROLLER_VERSION
    CONTROLLER_VERSION = version


def bind_containment_precondition(probe) -> None:
    """The CLI owns the host containment probe; bind it once at import time."""
    global _containment_precondition
    _containment_precondition = probe


def containment_precondition() -> tuple[bool, str, str]:
    if _containment_precondition is None:  # pragma: no cover - bound at import
        return False, "unknown", "the containment probe was never bound"
    return _containment_precondition()

# --------------------------------------------------------------------------
# R595 / M0-T056: owner-authorized turnover ACTUATION channels (worker +
# orchestrator layers). Both REUSE the accepted M0-T054 controller + adapters
# UNCHANGED; the successor is always the frozen opus-4-8/xhigh pin. Every launch
# is fail-closed, single-instance, dedup-exactly-once, audit-linked, and gated on
# the C1 job-object containment precondition.
# --------------------------------------------------------------------------


def turnover_continuation_lock(checkout: pathlib.Path, runtime_base: str | None
                                ) -> SingleInstanceLock:
    """A continuation lock in a DISTINCT `turnover/` runtime subdir.

    It must NOT share the supervisor's own `supervisor.lock` file: that file is
    already held by the running supervisor (or, for the watchdog, by the dead
    orchestrator's checkout), and releasing it from the controller's finally block
    would drop the main single-instance lock. A separate directory gives the
    turnover attempt its own lock file, so it serializes turnover launches across
    processes without ever touching the S7 single-instance lock.
    """
    turnover_runtime = runtime_dir_for(checkout, base=runtime_base) / "turnover"
    return SingleInstanceLock(
        turnover_runtime, checkout_key=checkout_key(checkout),
        controller_version=CONTROLLER_VERSION)


def approved_model_router(
    journal: DurableJournal, *, config: Any = None,
    probe: Any = None, cli_version: str = "",
) -> ModelRouter:
    """The production router: owner-approved list + durable live-probe ledger.

    `config` is the immutable, manifest-covered controller config, and it is the
    ONLY source of the approved list - a missing config approves nothing rather
    than falling back (D-023-R013). The probe ledger is bound to the config
    DIGEST and the provider CLI version, so a probe taken under a different
    controller config or a different CLI cannot authorize a selection.

    `probe` is the exact-id LIVE LAUNCH PROBE seam. It is REQUIRED for a model to
    become selectable: with none wired, a model with no already-recorded
    successful probe is refused rather than assumed available. Running a real
    probe against a real provider CLI is an owner-checkpoint act on the
    controller; nothing in this build performs one.
    """
    approved = (config.approved_models if config is not None
                else ApprovedModels(entries=(), source=""))
    ledger = ProbeLedger(journal,
                         config_identity=(config.digest() if config is not None else ""),
                         cli_version=cli_version)
    return ModelRouter(approved=approved, ledger=ledger, probe=probe)


def approved_successor_resolver(router: ModelRouter):
    """A `SuccessorResolver` bound to the owner-approved, live-probed chain.

    The successor is the next APPROVED entry after the model the failed execution
    was running on, proved by a live launch probe. `ModelRoutingError` propagates
    to the controller, which turns it into a `NO_APPROVED_SUCCESSOR` safe stop -
    never a fallback to an id the owner did not approve.
    """
    def _resolve(context: TurnoverContext) -> ApprovedSuccessor:
        selected = router.next_after(str(getattr(context, "current_model", "") or ""))
        return ApprovedSuccessor(
            model_id=selected.model_id,
            effort=ALLOWED_SUCCESSOR_EFFORT,
            probed_at_utc=selected.probe.probed_at_utc,
            config_identity=selected.probe.config_identity,
            cli_version=selected.probe.cli_version)
    return _resolve


def child_survivor_predicate(journal: DurableJournal):
    """A `SurvivorPredicate` wired to M0-T053 production child accounting.

    A surviving recorded worker child blocks a redispatch (the no-duplicate-workers
    invariant, R347 / AS-4). Unreadable child state fails CLOSED to "survivor
    present" so an unprovable state never permits a second launch.
    """
    def _survivor(_context: TurnoverContext) -> bool:
        try:
            accounts = account_for_children(journal)
        except Exception:
            return True
        return any(getattr(account, "surviving", False) for account in accounts)
    return _survivor


def build_worker_actuation_channel(
    *, args: argparse.Namespace, journal: DurableJournal, audit: AuditLog,
    checkout: pathlib.Path, claude_executable: str, max_turns: int,
    unit_timeout: float, config: Any = None, model_probe: Any = None,
    cli_version: str = "",
) -> tuple[TurnoverController | None, dict[str, Any]]:
    """Assemble the owner-authorized WORKER-layer actuation channel.

    Returns ``(controller, report)``. The controller is None - keeping the seam
    RECORD-INTENT-ONLY and byte-identical to the pre-activation path - UNLESS the
    owner passed ``--authorize-turnover-actuation`` AND the C1 job-object
    containment gate passes. The real M0-T054 adapters are used UNCHANGED.
    """
    if not getattr(args, "authorize_turnover_actuation", False):
        return None, {
            "authorized": False, "wired": False,
            "reason": "owner did not pass --authorize-turnover-actuation; the worker "
                      "turnover seam stays record-intent-only (byte-identical to the "
                      "pre-activation path)"}
    contained, kind, detail = containment_precondition()
    if not contained:
        return None, {
            "authorized": True, "wired": False, "containment_ok": False,
            "containment_kind": kind,
            "reason": f"C1 job-object containment gate REFUSES actuation: {detail}"}
    launcher = SupervisorLauncher(
        command_runner=make_subprocess_command_runner(
            new_successor_id=lambda: f"opus-worker-{os.urandom(8).hex()}"),
        targets=SuccessorLaunchTargets(
            checkout=str(checkout), claude_executable=claude_executable,
            max_turns=max_turns, unit_timeout_seconds=unit_timeout))
    router = approved_model_router(journal, config=config, probe=model_probe,
                                    cli_version=cli_version)
    controller = TurnoverController(
        launcher=launcher,
        lock=SingleInstanceContinuationLock(
            turnover_continuation_lock(checkout, args.runtime_base)),
        audit=HashChainedAuditSink(audit),
        identity=SupervisorIdentity(),
        survivor_detected=child_survivor_predicate(journal),
        successor=approved_successor_resolver(router))
    return controller, {
        "authorized": True, "wired": True, "containment_ok": True,
        "containment_kind": kind,
        "approved_models": list(router.approved.entries),
        "reason": "worker-layer actuation channel wired (M0-T054 adapters + survivor "
                  "detector + M0-T080 owner-approved successor resolver); a confirmed "
                  "FABLE_EXHAUSTED verdict redispatches the same bounded unit exactly once "
                  "on the next OWNER-APPROVED, live-probed model, and stops safely when the "
                  "approved list is empty or spent"}


def orchestrator_exhaustion_event_id(signal_text: str, checkout: str) -> str:
    """A deterministic exhaustion-event id for the SAME orchestrator hard stop.

    Stable in ``(signal_text, checkout)`` so a second watchdog invocation on the
    SAME captured exhaustion presents the SAME event id; the controller's durable
    dedup then suppresses a second successor (exactly-once across process
    restarts).
    """
    digest = sha256_hex(f"orchestrator-exhaustion:{checkout}:{signal_text}".encode("utf-8"))
    return f"orchestrator-exhaustion:{digest[:40]}"


def run_orchestrator_watchdog(
    *, signal_text: str, journal: DurableJournal, audit: AuditLog,
    checkout: str, orchestrator_argv_prefix: tuple[str, ...],
    command_runner, current_model: str, handoff_reference: str = "",
    safe_checkpoint_id: str = "", task_id: str = "",
    containment_check=None, config: Any = None, model_probe: Any = None,
    cli_version: str = "",
) -> dict[str, Any]:
    """The ORCHESTRATOR-layer watchdog decision (AS-1), independent of argparse.

    Runs OUTSIDE the Claude session (invoked by the OS scheduler on the
    orchestrator's terminal output). It CLASSIFIES the captured signal with the
    frozen M0-T054 detector, and ONLY on a grounded FABLE_EXHAUSTED verdict, and
    ONLY when the C1 containment gate passes, drives the frozen TurnoverController
    (layer=ORCHESTRATOR) to launch EXACTLY ONE opus-4-8 successor that loads the
    durable handoff + safe checkpoint. NOT_EXHAUSTED / AMBIGUOUS_FAIL_CLOSED and an
    unreadable signal REFUSE and record the reason; they never launch. The
    ``command_runner`` is injected so tests never spawn a process.

    M0-T080 (D-023-R013): `current_model` is REQUIRED and has no default. It used
    to default to a literal Fable model id, so a watchdog invoked without
    it attributed the exhaustion to a model nobody had named - and the classifier
    uses exactly that attribution to decide whether a structured quota signal is
    a *Fable* exhaustion at all. The caller must supply the model the run was
    actually recorded on.
    """
    containment_check = containment_check or containment_precondition
    if not current_model:
        record_id = audit.append(
            "orchestrator_watchdog_no_current_model", policy_result="REFUSED",
            detail={"reason": "no current model was supplied or recorded for this run"}).digest
        return {
            "command": "orchestrator-watchdog", "layer": "orchestrator",
            "classification": "", "launched": False, "actuated": False,
            "successor_id": "", "event_id": "", "audit_record_id": record_id,
            "successor_model_id": "", "refused": True,
            "reason": "the model the exhausted orchestrator ran on is not known: name it "
                      "with --current-model, or run against a checkout whose journal "
                      "records it. There is no default model id to assume (D-023-R013)",
        }
    evidence = TurnoverEvidence(
        stdout=str(signal_text or ""), exit_code=-1, model_id=current_model)
    verdict = classify_exhaustion(evidence)
    payload: dict[str, Any] = {
        "command": "orchestrator-watchdog", "layer": "orchestrator",
        "classification": verdict.classification.value, "reason": verdict.reason,
        "launched": False, "actuated": False, "successor_id": "", "event_id": "",
        "audit_record_id": "", "successor_model_id": "",
    }
    if not verdict.should_turn_over:
        # FAIL-CLOSED: not a grounded exhaustion. Record the refusal; never launch.
        record_id = audit.append(
            "orchestrator_watchdog_no_turnover",
            detail={"classification": verdict.classification.value,
                    "reason": verdict.reason}).digest
        payload.update({"refused": True, "audit_record_id": record_id,
                        "note": "no grounded Fable exhaustion; fail closed, no successor "
                                "launched"})
        return payload
    contained, kind, detail = containment_check()
    payload["containment_kind"] = kind
    if not contained:
        record_id = audit.append(
            "orchestrator_watchdog_containment_refused", policy_result="REFUSED",
            detail={"containment_kind": kind, "required": CONTAINMENT_JOB_OBJECT,
                    "reason": detail}).digest
        payload.update({"refused": True, "audit_record_id": record_id,
                        "note": f"C1 job-object containment gate REFUSES actuation: {detail}"})
        return payload
    controller = TurnoverController(
        launcher=SupervisorLauncher(
            command_runner=command_runner,
            targets=SuccessorLaunchTargets(
                checkout=checkout,
                orchestrator_argv_prefix=tuple(orchestrator_argv_prefix))),
        lock=SingleInstanceContinuationLock(
            turnover_continuation_lock(pathlib.Path(checkout), None)),
        audit=HashChainedAuditSink(audit),
        identity=SupervisorIdentity(),
        survivor_detected=child_survivor_predicate(journal),
        successor=approved_successor_resolver(approved_model_router(
            journal, config=config, probe=model_probe, cli_version=cli_version)))
    event_id = orchestrator_exhaustion_event_id(signal_text, checkout)
    context = TurnoverContext(
        task_id=task_id, event_id=event_id,
        failed_fable_execution_id=event_id,
        safe_checkpoint_id=safe_checkpoint_id,
        handoff_reference=handoff_reference or event_id,
        layer=TurnoverLayer.ORCHESTRATOR,
        current_model=current_model)
    outcome = controller.execute(verdict, context)
    payload.update({
        "launched": outcome.turned_over, "actuated": outcome.turned_over,
        "successor_id": outcome.successor_id, "event_id": outcome.event_id,
        "audit_record_id": outcome.audit_record_id,
        "successor_model_id": outcome.model_id, "status": outcome.status.value,
        "reason": outcome.reason})
    return payload

