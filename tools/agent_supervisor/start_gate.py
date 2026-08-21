#!/usr/bin/env python3
"""The `start` pre-dispatch gate: owner mode gate, live probes, typed refusals.

M0-T079 (D-023 item 1). Three decisions used to sit inline in `cmd_start`, and
they change for entirely different reasons than the command wiring around them:

* **the owner gate** on the bounded unattended mode - off unless the owner
  enabled THIS launch (R595 / D-023-R033);
* **the live revalidation** that replaced the synthetic S11.5 step answers, which
  the CLI used to derive from "did the operator name every flag?";
* **the mapping** from a pre-dispatch verdict to one documented refusal outcome
  and its stable nonzero exit code (`refusals.py`).

Keeping them here leaves `cmd_start` doing what a command should do - open the
runtime, run the sequence in its non-negotiable order, print, exit - and lets
each decision be tested without driving the whole CLI.

Nothing in this module contacts a provider, a network, or GitHub. The Git runner
and the reachability check are injected, and `run_live_probes` is the same
function the probe tests drive directly.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Callable, Mapping

from . import refusals
from .loop import (
    MODE_LIMITED_AUTO,
    OWNER_GATED_MODES,
    RUNNABLE_MODES,
    LimitedAutoRefused,
)
from .recovery_probes import (
    STEP_PROBES,
    ProbeInputs,
    ProbeReport,
    ProbeResult,
    named_executables,
    run_live_probes,
    subprocess_git,
)

def emit_refusal(args: argparse.Namespace, item: refusals.Refusal) -> int:
    """Emit a structured refusal on the right channel and return its exit code.

    Under `--json` the refusal document goes to STDOUT, because the whole point
    of `--json` is one parseable document there. Otherwise the human lines go to
    stderr, where a refusal belongs. Either way it is a decision the controller
    made, printed as such - never a traceback.
    """
    return refusals.emit(item, as_json=bool(args.json),
                         stream=sys.stdout if args.json else sys.stderr)


def bounded_mode_gate(args: argparse.Namespace) -> refusals.Refusal | None:
    """The owner gate on the bounded unattended mode. None means "not refused".

    M0-T079 (D-023 item 1; AD-093 evidence: reproduced defect). `start --mode
    limited-auto` used to raise a bare `NotImplementedError`, so an unattended
    wrapper or scheduled task got a traceback and an exit code that said nothing.
    The refusal is unchanged in STRENGTH - the mode is still off unless the owner
    enables it for this exact launch (R595 / D-023-R033) - and is now machine
    readable: `refused_mode`, exit 16, structured JSON, no traceback.
    """
    bounded = args.mode == MODE_LIMITED_AUTO
    enabled = bool(getattr(args, "owner_enable_bounded_auto", False))
    if bounded and not enabled:
        return refusals.refusal(
            refusals.REFUSED_MODE,
            reason_code="limited_auto_not_enabled",
            message=LimitedAutoRefused().message,
            detail={"mode": args.mode,
                    "owner_enable_input": "--owner-enable-bounded-auto",
                    "runnable_without_owner_enable": list(RUNNABLE_MODES),
                    "owner_gated_modes": list(OWNER_GATED_MODES)})
    if enabled and not bounded:
        return refusals.refusal(
            refusals.REFUSED_MODE,
            reason_code="owner_enable_without_gated_mode",
            message=(f"--owner-enable-bounded-auto was supplied for mode {args.mode!r}, "
                     f"which is not owner-gated. An enable that does not name the mode it "
                     f"enables is refused rather than ignored, so a stray flag can never "
                     f"sit unnoticed in a scheduled task's argv."),
            detail={"mode": args.mode, "owner_gated_modes": list(OWNER_GATED_MODES)})
    return None


def remote_reachability(git) -> Callable[[str], ProbeResult]:
    """A read-only `git ls-remote` reachability check, injected into the probe."""

    def check(url: str) -> ProbeResult:
        result = git(("ls-remote", "--exit-code", "--heads", url), str(pathlib.Path(__file__).resolve().parent))
        if not result.ran:
            return ProbeResult("remote_reachability", False, False, "git_unavailable",
                               f"git could not be run to reach {url}: {result.stderr.strip()}")
        if result.returncode != 0:
            return ProbeResult("remote_reachability", False, True, "remote_unreachable",
                               f"git ls-remote exited {result.returncode}: "
                               f"{result.stderr.strip()}")
        return ProbeResult("remote_reachability", True, True, "",
                           f"{url} answered a read-only ls-remote")

    return check


def load_task_packet(path: str) -> tuple[dict[str, Any], str]:
    """Read the task packet for the probes. Returns (packet, error-reason)."""
    try:
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return {}, f"the task packet at {path} could not be read: {exc}"
    if not isinstance(data, dict):
        return {}, f"the task packet at {path} is not a JSON object"
    return data, ""


def live_revalidation(
    args: argparse.Namespace, *, checkout: pathlib.Path, journal: DurableJournal,
    packet: Mapping[str, Any], manifest_ok: bool, manifest_reason: str,
    integrity_ok: bool, chain_ok: bool,
) -> tuple[dict[str, bool], Any]:
    """Run the LIVE S11.5 step-5 probes and build the revalidation map.

    M0-T079 (AD-093 evidence: reproduced defect). Six of these steps used to be
    answered with the single synthetic boolean "did the operator name every CLI
    input?", and three more with a bare `True` - so a complete command line
    certified the branch, worktree, Git/remote state, auth, capability manifest,
    pending requests, deadlines, and last external effect without looking at any
    of them. Each is now a real read, and every probe that cannot ESTABLISH its
    fact fails closed (`ProbeResult.passes` requires `ok and known`), which
    `recovery.classify` turns into UNSAFE_OR_DRIFTED before any provider or
    GitHub contact.

    `controller_manifest` is ANDed with the config-identity probe: the manifest
    verdict alone did not say that the config the run would actually read is the
    one the manifest binds.
    """
    repo = pathlib.Path(args.repo or checkout).resolve()
    worktree = pathlib.Path(args.worktree or repo).resolve()
    git = subprocess_git()
    report = run_live_probes(ProbeInputs(
        journal=journal,
        packet=packet,
        repo_root=str(repo),
        worktree=str(worktree),
        packet_path=str(args.task_packet or ""),
        expected_branch=args.branch or "",
        executables=named_executables(claude=args.claude_executable,
                                      codex=args.codex_executable),
        config_path=str(args.config or ""),
        manifest_ok=manifest_ok,
        manifest_reason=manifest_reason,
        remote_reachability_required=bool(getattr(args, "require_remote_reachable", False)),
        git=git,
        reachability=remote_reachability(git)))
    answers = report.by_step()
    config_identity_ok = answers["config_identity"].passes
    revalidation = {
        "controller_manifest": bool(manifest_ok and config_identity_ok),
        "journal_integrity": bool(integrity_ok),
        "audit_chain": bool(chain_ok),
        **report.revalidation(STEP_PROBES),
    }
    return revalidation, report


def unprobed_revalidation(*, manifest_ok: bool, integrity_ok: bool,
                          chain_ok: bool) -> dict[str, bool]:
    """The revalidation map when there was nothing to probe AGAINST.

    Reached when a required input was not named, or when the task packet was
    named but does not parse: with no packet, no worktree, and no executables
    there is nothing to read, so every live step reads NOT ESTABLISHED - which
    is a failed check, not an omission. This is the one place a step is answered
    without a probe, and it answers False. Before M0-T079 six of these were
    answered `dispatchable` and three were answered `True`.
    """
    answers = {step: False for step in STEP_PROBES}
    answers["controller_manifest"] = bool(manifest_ok)
    answers["journal_integrity"] = bool(integrity_ok)
    answers["audit_chain"] = bool(chain_ok)
    return answers


def revalidation_note(dispatchable: bool, packet_error: str) -> str:
    """The note `recover_boot` records about how the facts were established."""
    if dispatchable and not packet_error:
        return ("every input the loop needs was named explicitly, and the S11.5 step-5 "
                "facts were established by LIVE probes before any provider contact")
    what = ("a usable task packet" if packet_error else "the inputs the loop needs")
    return (f"`start` was invoked without {what}, so the live "
            f"task/branch/worktree/git/auth/capability set was not collected and reads "
            f"as not established")


def recovery_refusal(outcome: Any, probe_report: ProbeReport | None) -> refusals.Refusal:
    """The typed refusal for a pre-dispatch recovery verdict that forbids a start.

    `recovery.classify` already names the condition precisely; this only says
    which machine-readable bucket it lands in and carries the failed steps and
    probes so the payload names EVERY missing fact, not just the first.
    """
    return refusals.refusal(
        refusals.outcome_for_recovery(outcome.classification, outcome.reason_code),
        reason_code=outcome.reason_code, message=outcome.reason,
        detail={"classification": outcome.classification,
                "failed_steps": list(outcome.failed_steps),
                "missing_steps": list(outcome.missing_steps),
                "failed_probes": (list(probe_report.to_dict()["failed"])
                                  if probe_report is not None else []),
                "pending_effect_ids": list(outcome.pending_effect_ids)})


def dispatched_run_refusal(mode: str, run: Mapping[str, Any]) -> refusals.Refusal | None:
    """The typed refusal for how a DISPATCHED run ended, or None if it just ended.

    An exhausted budget is a refusal in every mode. Beyond that the modes differ
    honestly: in shadow/supervised a park for the owner is the expected shape of
    the run and stays exit 0, while in the bounded unattended mode nobody is
    watching, so the same park is a terminal condition the caller must be able to
    detect from the exit code alone.
    """
    stopped = str(run.get("stopped", "") or "")
    if stopped == "budget_exhausted":
        return refusals.refusal(
            refusals.BUDGET_EXHAUSTED, reason_code="budget_exhausted",
            message="the owner-set run budget is spent; the run stopped "
                    "deterministically between cycles and cleared no durable hold, "
                    "flag, deadline, or approval",
            detail={"run_budget": run.get("run_budget")})
    if mode != MODE_LIMITED_AUTO:
        return None
    outcome = refusals.outcome_for_unattended_stop(stopped)
    if outcome is None:
        return None
    return refusals.refusal(
        outcome, reason_code=stopped,
        message=(f"the unattended run stopped on {stopped!r} and cannot resolve it "
                 f"without a human"),
        detail={"final_state": run.get("final_state"),
                "cycles": len(run.get("cycles", []))})


def loop_refusal(code: str, message: str, mode: str) -> refusals.Refusal:
    """The typed refusal for a `LoopError` / illegal-transition the loop raised."""
    return refusals.refusal(refusals.outcome_for_loop_refusal(code),
                            reason_code=code, message=message,
                            detail={"mode": mode, "source": "loop"})
