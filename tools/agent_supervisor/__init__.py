#!/usr/bin/env python3
"""Agent Supervisor - deterministic Codex <-> Claude supervisor bridge (D-007).

PHASES 1-4. Phase 1 built the deterministic substrate; Phase 2 added the policy
engine and the provider adapters; Phase 3 added endurance - rotation, recovery,
durable wake scheduling, notifications, retention, and the authenticated
model-change path; Phase 4 ASSEMBLES them into the loop, adds the replay engine
and its historical corpus, makes the Windows Job Object the default container,
and runs the Section 15 matrices against all of it:

    config.py           immutable controller config + runtime model selection (D-007 S3.1)
    models.py           dataclasses for checkpoint / decision / envelope / journal records
    protocol.py         versioned JSON/JSONL envelope, framing, sequence + idempotency
    durable_state.py    transactional SQLite journal (WAL, synchronous=FULL)
    state_machine.py    the S7 deterministic state machine
    audit_log.py        append-only JSONL with the MANDATORY hash chain (S13.12)
    redaction.py        never-send / secret redaction before persistence (S13.9)
    manifest.py         controller manifest generation + verification (S13.1)
    circuit_breakers.py configurable fail-closed limits (S13.8)
    process.py          argv-array-only subprocess abstraction (S13 baseline)
    policy.py           the four-tier policy engine, standing grants, model
                        selection, and the independence check (S4, S3)      [P2]
    broker.py           the approval broker with S13.5 digest binding (S8.4)  [P2]
    claude_runner.py    the Claude CLI worker adapter (S8.1-S8.4)            [P2]
    codex_reviewer.py   the fresh-process read-only Codex reviewer (S2.2, S9) [P2]
    review_cadence.py   the 0A.3 meaningful-checkpoint review-cadence policy  [T042]
    review_packet.py    the 0A.4 packet budget + AD-083 content guard         [T042]
    ephemeral_review.py the operational fresh-ephemeral review loop + record  [T042]
    evidence.py         deterministic collector + bounded packet builder (S10)[P2]
    external_effects.py exactly-once external-effect journal (S13.7)         [P2]
    push_policy.py      S13.6 push checks - POLICY ONLY, no execution        [P2]
    rotation.py         pre-dispatch decision, finish-the-unit, handoff (S11) [P3]
    resume_scheduler.py limit classes, reset parsing, durable wake (S11.4)   [P3]
    recovery.py         RECOVER_BOOT and SAFE/AMBIGUOUS/UNSAFE (S11.5)       [P3]
    locking.py          single-instance lock keyed to the checkout (S7)      [P3]
    notifications.py    view-only redacted notifications (S13.10)            [P3]
    remote_approvals.py authenticated, digest-bound remote answers (S13.10)  [P3]
    model_change_ipc.py the authenticated model-change path (S3.2 rule 6)    [P3]
    retention.py        pre-op manifests, quarantine, retention, restore     [P3]
    anchor.py           Option A audit anchoring - MECHANISM ONLY (S13.12)   [P3]
    preflight.py        capability probes incl. the control-response probe   [P3]
    loop.py             the assembled shadow/supervised loop (S7, S12)       [P4]
    errors.py           the loop's error taxonomy, shared by its modules     [T079]
    owner_touch.py      the S16.7 owner-touch budget - a MEASUREMENT         [T079]
    loop_breakers.py    which production event ticks which counter (S13.8)   [T079]
    run_budget.py       durable owner-controlled run budgets (D-023 item 1)  [T079]
    recovery_probes.py  LIVE S11.5 step-5 revalidation probes, fail-closed   [T079]
    refusals.py         typed refusal outcomes + stable exit codes           [T079]
    start_gate.py       the `start` pre-dispatch gate (owner gate + probes)  [T079]
    replay.py           the replay engine over replay_corpus/ (S12, S15)     [P4]
    cli.py              operator commands (S12.1) - none deferred

NOT in this build (deliberately, and named rather than implied): push EXECUTION,
Option A anchor PUBLICATION, the long-lived named-pipe IPC server loop, and the
Phase 5 shadow pilot with its decision packet.

The supervisor is a coordinator, evidence collector, and state machine. It is
NOT a source of project truth: `project-control/` and git remain authoritative.

Autonomy status (M0-T079, D-023 item 1): the bounded unattended mode
(`limited-auto`) is IMPLEMENTED - durable owner-controlled run budgets with NO
hardcoded maximum run length (D-023-R037), every circuit breaker wired to its
real event site, live pre-dispatch revalidation probes, and typed structured
refusals - and it is OFF. Every launch that does not carry the explicit
per-launch owner enable is refused by name, and ACTIVATING it on a live host
remains a separate explicit owner act under the R595 pre-activation path
(D-007 S12; D-023-R033). Nothing in this package can turn it on by itself.
"""
from __future__ import annotations

__all__ = [
    "CONTROLLER_VERSION",
    "PROTOCOL_VERSION",
    "SCHEMA_VERSION",
    "PHASE",
]

#: Version of the deterministic controller itself. Recorded in the manifest, in
#: every audit record, and in the durable journal so a resumed run can refuse to
#: continue under a different controller build (D-007 S7, S13.1).
CONTROLLER_VERSION = "0.4.0-phase4"

#: Version of the cross-CLI envelope protocol (D-007 S8.5). Bumped whenever the
#: envelope's required field set or framing rules change.
PROTOCOL_VERSION = "1.0.0"

#: Version of the payload schemas under `schemas/` (D-007 S8.3, S9).
SCHEMA_VERSION = "1.0.0"

#: Implementation phase this build corresponds to (D-007 S17).
PHASE = 4
