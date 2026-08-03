#!/usr/bin/env python3
"""Agent Supervisor - deterministic Codex <-> Claude supervisor bridge (D-007).

PHASES 1-2. Phase 1 built the deterministic substrate; Phase 2 adds the policy
engine and the provider adapters:

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
    evidence.py         deterministic collector + bounded packet builder (S10)[P2]
    external_effects.py exactly-once external-effect journal (S13.7)         [P2]
    push_policy.py      S13.6 push checks - POLICY ONLY, no execution        [P2]
    cli.py              operator commands (S12.1)

NOT in this build (deliberately): session rotation, crash-recovery
classification, durable wake scheduling, notifications, authenticated remote
approvals, quarantine/restore, the replay engine, and push EXECUTION. Those are
Phases 3-4.

The supervisor is a coordinator, evidence collector, and state machine. It is
NOT a source of project truth: `project-control/` and git remain authoritative.

Autonomy status: limited-auto is NOT implemented and cannot be enabled by this
code. Activation is a separate explicit owner act (D-007 S12).
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
CONTROLLER_VERSION = "0.2.0-phase2"

#: Version of the cross-CLI envelope protocol (D-007 S8.5). Bumped whenever the
#: envelope's required field set or framing rules change.
PROTOCOL_VERSION = "1.0.0"

#: Version of the payload schemas under `schemas/` (D-007 S8.3, S9).
SCHEMA_VERSION = "1.0.0"

#: Implementation phase this build corresponds to (D-007 S17).
PHASE = 2
