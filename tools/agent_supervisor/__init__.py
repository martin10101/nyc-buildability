#!/usr/bin/env python3
"""Agent Supervisor - deterministic Codex <-> Claude supervisor bridge (D-007).

PHASE 1 (core loop) ONLY. This package currently provides the deterministic
substrate the later phases build on:

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
    cli.py              operator commands (S12.1); only `doctor` and `status` are live

NOT in this phase (deliberately): the four-tier policy engine, the approval
broker, the Claude runner, the Codex reviewer, the evidence collector, rotation,
recovery scheduling, notifications, and remote approvals. Those are Phases 2-4.

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
CONTROLLER_VERSION = "0.1.0-phase1"

#: Version of the cross-CLI envelope protocol (D-007 S8.5). Bumped whenever the
#: envelope's required field set or framing rules change.
PROTOCOL_VERSION = "1.0.0"

#: Version of the payload schemas under `schemas/` (D-007 S8.3, S9).
SCHEMA_VERSION = "1.0.0"

#: Implementation phase this build corresponds to (D-007 S17).
PHASE = 1
