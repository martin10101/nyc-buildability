#!/usr/bin/env python3
"""Operator command surface (D-007 S12.1).

Phase 1 wires the whole S12.1 command list so the shape is visible and no
command silently does something surprising. Only three are LIVE:

    doctor    read-only; runs every Phase-1-scope check and reports pass/fail
    status    read-only; renders the durable journal's current view
    replay    wired but not implemented (the replay engine is Phase 4)

Every other command raises `NotImplementedError` naming the phase that will
implement it. That is deliberate: an operator command that half-works is worse
than one that plainly refuses.

`start --mode limited-auto` is special. It does not merely raise
`NotImplementedError` - it refuses BY NAME, because limited-auto is disabled by
default and is enabled only by a separate explicit owner activation recorded
through directive compliance (S12). No code path in this package can turn it on.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Sequence

from . import CONTROLLER_VERSION, PHASE, PROTOCOL_VERSION, SCHEMA_VERSION
from .audit_log import AuditLog
from .circuit_breakers import CircuitBreakers
from .config import (
    ConfigError,
    Limits,
    load_controller_config,
    load_model_selection,
    validate_selection,
)
from .durable_state import (
    DB_FILENAME,
    DurableJournal,
    JournalError,
    checkout_key,
    looks_cloud_synced,
    runtime_dir_for,
)
from .manifest import MODEL_SELECTION_FILENAME, generate_manifest, read_manifest, verify_manifest
from .process import HARD_DENY_ARGUMENTS, HardDenyError, assert_argv_safe
from .protocol import build_envelope, validate_envelope
from .state_machine import STATES, TRANSITIONS, INITIAL_STATE

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent
AUDIT_FILENAME = "audit.jsonl"

#: Commands that exist in S12.1 but are implemented in a later phase.
DEFERRED_COMMANDS: dict[str, str] = {
    "start": "Phase 2 (policy engine, approval broker, and the Claude/Codex adapters)",
    "pause": "Phase 3 (pause/stop/resume with durable flags)",
    "resume": "Phase 3 (pause/stop/resume with durable flags)",
    "stop": "Phase 3 (pause/stop/resume with durable flags)",
    "emergency-stop": "Phase 3 (durable stop flag and child-tree termination)",
    "verify-controller": "Phase 2 (uses the live controller checkout, not a supplied root)",
    "recovery-status": "Phase 3 (crash/reboot recovery classification)",
    "schedule-status": "Phase 3 (durable wake scheduling)",
    "cancel-scheduled-resume": "Phase 3 (durable wake scheduling)",
    "autostart-plan": "Phase 3 (owner-gated startup/logon task)",
    "install-autostart": "Phase 3 (owner-gated OS mutation)",
    "uninstall-autostart": "Phase 3 (owner-gated OS mutation)",
    "pending-approvals": "Phase 2 (approval broker)",
    "approve-once": "Phase 2 (approval broker)",
    "deny": "Phase 2 (approval broker)",
    "revoke-all": "Phase 3 (remote approvals and revocation)",
    "set-codex-model": "Phase 3 (authenticated model-change path, S3.2 rule 6)",
    "set-claude-model": "Phase 3 (authenticated model-change path, S3.2 rule 6)",
    "export-handoff": "Phase 3 (rotation and verified handoff)",
    "replay": "Phase 4 (replay engine and the historical corpus)",
}


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------


class Check:
    """One doctor check result."""

    def __init__(self, name: str, ok: bool, detail: str) -> None:
        self.name = name
        self.ok = ok
        self.detail = detail

    def to_dict(self) -> dict[str, Any]:
        return {"check": self.name, "ok": self.ok, "detail": self.detail}


def _check_python() -> Check:
    ok = sys.version_info >= (3, 11)
    return Check(
        "python_version", ok,
        f"{sys.version.split()[0]} (>= 3.11 required for tomllib; stdlib only, no new "
        f"dependency)")


def _check_schemas() -> Check:
    schema_dir = PACKAGE_ROOT / "schemas"
    expected = {
        "claude_checkpoint.schema.json",
        "codex_decision.schema.json",
        "protocol_envelope.schema.json",
        "durable_state.schema.json",
    }
    found = {p.name for p in schema_dir.glob("*.json")}
    missing = sorted(expected - found)
    if missing:
        return Check("schemas_present", False, f"missing schema files: {missing}")
    for name in sorted(expected):
        try:
            json.loads((schema_dir / name).read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            return Check("schemas_present", False, f"{name} is not valid JSON: {exc}")
    return Check("schemas_present", True, f"{len(expected)} schemas parse as valid JSON")


def _check_prompts() -> Check:
    prompt_dir = PACKAGE_ROOT / "prompts"
    expected = {"claude_checkpoint.md", "codex_review.md", "session_handoff.md"}
    missing = sorted(expected - {p.name for p in prompt_dir.glob("*.md")})
    if missing:
        return Check("prompts_present", False, f"missing prompt templates: {missing}")
    return Check("prompts_present", True, f"{len(expected)} prompt templates present")


def _check_state_machine() -> Check:
    reachable = {t.state_to for t in TRANSITIONS} | {INITIAL_STATE}
    orphans = sorted(set(STATES) - reachable)
    if orphans:
        return Check("state_machine", False,
                     f"states with no inbound transition: {orphans}")
    unknown = sorted({t.state_from for t in TRANSITIONS} - set(STATES))
    if unknown:
        return Check("state_machine", False, f"transitions from unknown states: {unknown}")
    return Check("state_machine", True,
                 f"{len(STATES)} states, {len(TRANSITIONS)} documented transitions, "
                 f"every state reachable")


def _check_hard_denies() -> Check:
    """Prove the deny list actually denies (a constants list nobody checks is decoration)."""
    failures: list[str] = []
    for flag in sorted(HARD_DENY_ARGUMENTS):
        try:
            assert_argv_safe(["some-exe", flag])
        except HardDenyError:
            continue
        except Exception as exc:  # pragma: no cover - defensive
            failures.append(f"{flag} raised {type(exc).__name__}")
        else:
            failures.append(f"{flag} was NOT denied")
    for flag in ("--effort", "--effort=high", "--reasoning-effort"):
        try:
            assert_argv_safe(["some-exe", flag])
        except HardDenyError:
            continue
        else:
            failures.append(f"{flag} was NOT denied")
    if failures:
        return Check("hard_deny_enforced", False, "; ".join(failures))
    return Check("hard_deny_enforced", True,
                 f"{len(HARD_DENY_ARGUMENTS)} bypass flags and every effort flag are refused "
                 f"by argv validation")


def _check_runtime_dir(checkout: pathlib.Path, base: str | None) -> tuple[Check, pathlib.Path | None]:
    try:
        runtime = runtime_dir_for(checkout, base=base)
    except JournalError as exc:
        return Check("runtime_dir", False, exc.message), None
    notes = [f"{runtime}", f"key={checkout_key(checkout)[:16]}... (sha256 of the canonical "
                           f"full checkout path)"]
    if looks_cloud_synced(runtime):
        return Check("runtime_dir", False,
                     f"{runtime} looks cloud-synced; the authoritative journal must live on a "
                     f"local filesystem"), runtime
    return Check("runtime_dir", True, "; ".join(notes)), runtime


def _check_journal(runtime: pathlib.Path) -> Check:
    db_path = runtime / DB_FILENAME
    try:
        with DurableJournal(db_path) as journal:
            report = journal.integrity_check()
    except JournalError as exc:
        return Check("journal_integrity", False, f"{exc.code}: {exc.message}")
    if not report.ok:
        return Check("journal_integrity", False, f"{report.code}: {report.message}")
    return Check("journal_integrity", True,
                 f"schema v{report.schema_version}; " + ", ".join(report.checks))


def _check_audit(runtime: pathlib.Path) -> Check:
    log = AuditLog(runtime / AUDIT_FILENAME)
    verification = log.verify_chain()
    if not verification.ok:
        return Check("audit_chain", False,
                     f"{verification.code}: {verification.message}")
    return Check("audit_chain", True,
                 f"{verification.records_checked} records verified; head sequence "
                 f"{verification.head_sequence}")


def _check_manifest(manifest_path: str | None) -> Check:
    if manifest_path is None:
        manifest = generate_manifest(PACKAGE_ROOT)
        return Check("controller_manifest", True,
                     f"no manifest supplied; generated one over {len(manifest['files'])} files "
                     f"(digest {manifest['manifest_digest'][:16]}...). "
                     f"{MODEL_SELECTION_FILENAME} is deliberately excluded")
    try:
        manifest = read_manifest(manifest_path)
    except Exception as exc:
        return Check("controller_manifest", False, str(exc))
    verification = verify_manifest(PACKAGE_ROOT, manifest)
    if not verification.ok:
        return Check("controller_manifest", False, verification.halt_reason())
    return Check("controller_manifest", True,
                 f"{len(manifest['files'])} files verified against "
                 f"{manifest.get('manifest_digest', '')[:16]}...")


def _check_config(config_path: str | None, selection_path: str | None) -> list[Check]:
    checks: list[Check] = []
    if config_path is None and selection_path is None:
        checks.append(Check(
            "configuration", True,
            "no --config/--model-selection supplied; skipped. Supply both to validate the "
            "allowlists, the fallback chains, and the effort-key prohibition"))
        return checks

    config = None
    if config_path is not None:
        try:
            config = load_controller_config(config_path)
            checks.append(Check(
                "controller_config", True,
                f"codex allowlist {list(config.codex_allowed_models)}; claude allowlist "
                f"{list(config.claude_allowed_models)}; default_mode "
                f"{config.default_mode!r}; no effort key present"))
        except ConfigError as exc:
            checks.append(Check("controller_config", False, str(exc)))

    if selection_path is not None:
        try:
            selection = load_model_selection(selection_path)
            checks.append(Check(
                "model_selection", True,
                f"codex review_model {selection.codex.primary!r}, claude model "
                f"{selection.claude.primary!r}; selection digest "
                f"{selection.digest()[:16]}...; no effort key present"))
            if config is not None:
                result = validate_selection(config, selection, raise_on_error=False)
                checks.append(Check(
                    "model_selection_allowlists", result.ok,
                    "every selected and fallback model is in its OWN provider's allowlist"
                    if result.ok else "; ".join(result.errors)))
        except ConfigError as exc:
            checks.append(Check("model_selection", False, str(exc)))
    return checks


def _check_protocol_roundtrip() -> Check:
    """Build an envelope and validate it: proves digest binding works end to end."""
    envelope = build_envelope(
        payload={"probe": "doctor"}, payload_type="capability_handshake",
        run_id="doctor", task_id="doctor", sequence=1, producer="supervisor",
        producer_version=CONTROLLER_VERSION, correlation_id="doctor")
    try:
        validate_envelope(envelope.to_dict())
    except Exception as exc:
        return Check("protocol_roundtrip", False, str(exc))
    tampered = envelope.to_dict()
    tampered["payload"] = {"probe": "tampered"}
    try:
        validate_envelope(tampered)
    except Exception:
        return Check("protocol_roundtrip", True,
                     f"protocol {PROTOCOL_VERSION}/schema {SCHEMA_VERSION}: valid envelope "
                     f"accepted, digest-mismatched envelope refused")
    return Check("protocol_roundtrip", False,
                 "a payload-digest mismatch was NOT refused")


def _check_breakers() -> Check:
    breakers = CircuitBreakers(Limits())
    verdict = breakers.record("consecutive_hard_denies",
                              Limits().max_consecutive_hard_denies)
    if not verdict.tripped:
        return Check("circuit_breakers", False,
                     "a counter at its hard limit did not trip")
    return Check("circuit_breakers", True,
                 f"{len(breakers.snapshot())} counters configured; a counter at its hard "
                 f"limit trips (pause), below warn_ratio it only warns (NOTIFY)")


def cmd_doctor(args: argparse.Namespace) -> int:
    """Read-only Phase-1-scope health check."""
    checkout = pathlib.Path(args.checkout).resolve()
    checks: list[Check] = [
        _check_python(),
        _check_schemas(),
        _check_prompts(),
        _check_state_machine(),
        _check_protocol_roundtrip(),
        _check_hard_denies(),
        _check_breakers(),
        _check_manifest(args.manifest),
    ]
    runtime_check, runtime = _check_runtime_dir(checkout, args.runtime_base)
    checks.append(runtime_check)
    if runtime is not None and runtime_check.ok:
        checks.append(_check_journal(runtime))
        checks.append(_check_audit(runtime))
    checks.extend(_check_config(args.config, args.model_selection))

    ok = all(check.ok for check in checks)
    payload = {
        "command": "doctor",
        "controller_version": CONTROLLER_VERSION,
        "phase": PHASE,
        "protocol_version": PROTOCOL_VERSION,
        "schema_version": SCHEMA_VERSION,
        "checkout": str(checkout),
        "ok": ok,
        "checks": [check.to_dict() for check in checks],
        "limited_auto": "NOT IMPLEMENTED and disabled; activation is a separate explicit "
                        "owner act recorded through directive compliance",
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"agent_supervisor doctor - controller {CONTROLLER_VERSION} (phase {PHASE})")
        print(f"checkout: {checkout}")
        for check in checks:
            print(f"  [{'PASS' if check.ok else 'FAIL'}] {check.name}: {check.detail}")
        print(f"\noverall: {'PASS' if ok else 'FAIL'}")
        print("limited-auto: NOT IMPLEMENTED and disabled.")
    return 0 if ok else 1


# --------------------------------------------------------------------------
# status
# --------------------------------------------------------------------------


def cmd_status(args: argparse.Namespace) -> int:
    """Read-only view of the durable journal. The journal is the truth, not memory."""
    checkout = pathlib.Path(args.checkout).resolve()
    try:
        runtime = runtime_dir_for(checkout, base=args.runtime_base)
    except JournalError as exc:
        print(f"status unavailable: {exc}", file=sys.stderr)
        return 1

    db_path = runtime / DB_FILENAME
    audit = AuditLog(runtime / AUDIT_FILENAME)
    chain = audit.verify_chain()

    with DurableJournal(db_path) as journal:
        integrity = journal.integrity_check()
        last = journal.last_transition()
        payload = {
            "command": "status",
            "controller_version": CONTROLLER_VERSION,
            "phase": PHASE,
            "checkout": str(checkout),
            "runtime_dir": str(runtime),
            "journal_ok": integrity.ok,
            "journal_detail": integrity.message or ", ".join(integrity.checks),
            "current_state": journal.get_state("current_state", INITIAL_STATE),
            "last_transition": last.to_dict() if last else None,
            "pending_effects": [e.to_dict() for e in journal.pending_effects()],
            "open_asks": [a.to_dict() for a in journal.open_asks()],
            "unsent_outbound": len(journal.unsent_outbound()),
            "audit_chain_ok": chain.ok,
            "audit_head_sequence": chain.head_sequence,
            "audit_detail": chain.message,
            "mode": journal.get_state("mode", "none"),
            "limited_auto_enabled": False,
        }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"state:            {payload['current_state']}")
        print(f"mode:             {payload['mode']}")
        print(f"runtime dir:      {payload['runtime_dir']}")
        print(f"journal:          {'ok' if payload['journal_ok'] else 'FAILED'} "
              f"- {payload['journal_detail']}")
        print(f"audit chain:      {'ok' if payload['audit_chain_ok'] else 'FAILED'} "
              f"(head sequence {payload['audit_head_sequence']}) {payload['audit_detail']}")
        print(f"pending effects:  {len(payload['pending_effects'])}")
        print(f"queued questions: {len(payload['open_asks'])}")
        print("limited-auto:     disabled (not implemented in this phase)")
    return 0 if payload["journal_ok"] and payload["audit_chain_ok"] else 1


# --------------------------------------------------------------------------
# deferred commands
# --------------------------------------------------------------------------


def cmd_deferred(args: argparse.Namespace) -> int:
    """Every S12.1 command not yet implemented. Refuses loudly and by name."""
    command = args.command
    if command == "start" and getattr(args, "mode", None) == "limited-auto":
        raise NotImplementedError(
            "limited-auto is disabled and is NOT implemented by this build. It is never "
            "reachable from a configuration default, a parse error, a migration, or a "
            "downgrade; it is enabled only by a separate explicit owner activation recorded "
            "through directive compliance (D-007 S12).")
    raise NotImplementedError(
        f"`{command}` is wired but not implemented in phase {PHASE}. Scheduled for "
        f"{DEFERRED_COMMANDS.get(command, 'a later phase')}.")


# --------------------------------------------------------------------------
# parser
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.agent_supervisor",
        description="Deterministic Codex <-> Claude supervisor bridge (D-007). "
                    f"PHASE {PHASE}: core loop only.")
    parser.add_argument("--version", action="version",
                        version=f"agent_supervisor {CONTROLLER_VERSION} (phase {PHASE})")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--checkout", default=str(pathlib.Path.cwd()),
                       help="canonical checkout path whose runtime state is addressed")
        p.add_argument("--runtime-base", default=None,
                       help="override the runtime base directory (tests only; production "
                            "resolves %%LOCALAPPDATA%%)")
        p.add_argument("--json", action="store_true", help="machine-readable output")

    doctor = sub.add_parser("doctor", help="read-only health check (live)")
    add_common(doctor)
    doctor.add_argument("--config", default=None, help="path to the immutable config.toml")
    doctor.add_argument("--model-selection", default=None,
                        help="path to the runtime model_selection.toml")
    doctor.add_argument("--manifest", default=None,
                        help="path to a recorded controller manifest to verify against")
    doctor.set_defaults(func=cmd_doctor)

    status = sub.add_parser("status", help="render the durable journal (live)")
    add_common(status)
    status.set_defaults(func=cmd_status)

    replay = sub.add_parser("replay", help="replay a fixture or run (Phase 4)")
    add_common(replay)
    replay.add_argument("fixture", nargs="?", default=None)
    replay.set_defaults(func=cmd_deferred)

    start = sub.add_parser("start", help="start a run (Phase 2; limited-auto never)")
    add_common(start)
    start.add_argument("--mode", choices=["shadow", "supervised", "limited-auto"],
                       default="shadow")
    start.set_defaults(func=cmd_deferred)

    simple = [
        "pause", "resume", "stop", "emergency-stop", "verify-controller",
        "recovery-status", "schedule-status", "cancel-scheduled-resume",
        "autostart-plan", "install-autostart", "uninstall-autostart",
        "pending-approvals", "revoke-all", "export-handoff",
    ]
    for name in simple:
        p = sub.add_parser(name, help=f"{DEFERRED_COMMANDS.get(name, 'later phase')}")
        add_common(p)
        p.set_defaults(func=cmd_deferred)

    for name in ("approve-once", "deny"):
        p = sub.add_parser(name, help=DEFERRED_COMMANDS[name])
        add_common(p)
        p.add_argument("request_id")
        p.add_argument("displayed_digest")
        p.set_defaults(func=cmd_deferred)

    for name in ("set-codex-model", "set-claude-model"):
        p = sub.add_parser(name, help=DEFERRED_COMMANDS[name])
        add_common(p)
        p.add_argument("model_name")
        p.set_defaults(func=cmd_deferred)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
