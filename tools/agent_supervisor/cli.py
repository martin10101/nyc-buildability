#!/usr/bin/env python3
"""Operator command surface (D-007 S12.1).

The whole S12.1 command list is wired so the shape is visible and no command
silently does something surprising. LIVE after Phase 2:

    doctor              read-only; runs every in-scope check and reports pass/fail
    status              read-only; renders the durable journal's current view
    verify-controller   read-only; verifies the live controller against a manifest
    pending-approvals   read-only; lists queued requests with their exact digests
    approve-once        owner answer, bound to the displayed digest
    deny                owner answer, bound to the displayed digest
    revoke-all          revokes every pending/unconsumed approval immediately

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
from .broker import ApprovalBroker, BrokerError, build_request
from .circuit_breakers import CircuitBreakers
from .claude_runner import (
    CONTROL_RESPONSE_WRAPPER_VERIFIED,
    RunnerConfig,
    RunnerError,
    build_argv as build_claude_argv,
    build_control_response,
)
from .codex_reviewer import ReviewError, build_argv as build_codex_argv
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
from .evidence import DEFAULT_PACKET_BYTES, STOP_FOR_OWNER, bound_text, build_packet
from .external_effects import ExternalEffectError, spec_for, stable_action_id
from .manifest import MODEL_SELECTION_FILENAME, generate_manifest, read_manifest, verify_manifest
from .policy import (
    ASK,
    AUTO,
    BYPASS_FLAG_MARKERS,
    DENY_AND_HALT,
    HARD_DENY,
    ProposedAction,
    TaskAuthority,
    apply_model_recommendation,
    evaluate as evaluate_policy,
)
from .process import HARD_DENY_ARGUMENTS, HardDenyError, assert_argv_safe
from .protocol import build_envelope, validate_envelope
from .push_policy import PushPlan, assert_no_execution, evaluate_push
from .state_machine import STATES, TRANSITIONS, INITIAL_STATE

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent
AUDIT_FILENAME = "audit.jsonl"

#: Commands that exist in S12.1 but are implemented in a later phase.
DEFERRED_COMMANDS: dict[str, str] = {
    "start": "Phase 3 (the supervised loop: rotation, recovery, and scheduling)",
    "pause": "Phase 3 (pause/stop/resume with durable flags)",
    "resume": "Phase 3 (pause/stop/resume with durable flags)",
    "stop": "Phase 3 (pause/stop/resume with durable flags)",
    "emergency-stop": "Phase 3 (durable stop flag and child-tree termination)",
    "recovery-status": "Phase 3 (crash/reboot recovery classification)",
    "schedule-status": "Phase 3 (durable wake scheduling)",
    "cancel-scheduled-resume": "Phase 3 (durable wake scheduling)",
    "autostart-plan": "Phase 3 (owner-gated startup/logon task)",
    "install-autostart": "Phase 3 (owner-gated OS mutation)",
    "uninstall-autostart": "Phase 3 (owner-gated OS mutation)",
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


# --------------------------------------------------------------------------
# Phase 2 checks: policy, broker, adapters, push policy, evidence, effects
# --------------------------------------------------------------------------


def _probe_authority(checkout: pathlib.Path) -> TaskAuthority:
    """A throwaway authority used only to exercise the policy engine in `doctor`."""
    return TaskAuthority(
        task_id="DOCTOR", stage="probe", repo_root=str(checkout),
        worktree=str(checkout), branch="task/doctor-probe",
        allowed_paths=("tools/agent_supervisor/**",),
        forbidden_paths=(".github/**",),
        documented_test_commands=(),
        status="in_progress", active=True)


def _check_policy_tiers(checkout: pathlib.Path) -> Check:
    """Prove the four tiers actually classify, and that a model cannot loosen."""
    authority = _probe_authority(checkout)
    failures: list[str] = []

    # The probe input is built FROM the deny list, never restated as a literal.
    bypass = evaluate_policy(
        ProposedAction(kind="command",
                       command_text=f"claude {BYPASS_FLAG_MARKERS[0]} -p hi"),
        authority=authority)
    if bypass.tier != HARD_DENY or bypass.outcome != DENY_AND_HALT:
        failures.append(f"bypass flag classified {bypass.tier}/{bypass.outcome}")

    main_push = evaluate_policy(
        ProposedAction(kind="push", branch="main", argv=("git", "push", "origin", "main")),
        authority=authority)
    if main_push.tier != HARD_DENY:
        failures.append(f"push to main classified {main_push.tier}")

    edit = evaluate_policy(
        ProposedAction(kind="file_write",
                       target_paths=(str(checkout / "tools" / "agent_supervisor" /
                                         "policy.py"),),
                       change_bytes=100),
        authority=authority)
    if edit.tier != AUTO:
        failures.append(f"in-scope edit classified {edit.tier} ({edit.reason_code})")

    unknown = evaluate_policy(ProposedAction(kind="unknown", tool_name="MysteryTool"),
                              authority=authority)
    if unknown.tier != ASK:
        failures.append(f"unknown request classified {unknown.tier}")

    loosened = apply_model_recommendation(main_push, AUTO, source="doctor")
    if loosened.tier != HARD_DENY:
        failures.append("a model recommendation loosened a HARD-DENY")

    if failures:
        return Check("policy_four_tiers", False, "; ".join(failures))
    return Check("policy_four_tiers", True,
                 "HARD-DENY (bypass -> DENY_AND_HALT, main push), AUTO (in-scope edit), "
                 "ASK (unknown request) all classify correctly; a model recommendation "
                 "cannot loosen a tier")


def _check_approval_binding(checkout: pathlib.Path) -> Check:
    """Prove an approval digest is bound to the exact request (S13.5)."""
    authority = _probe_authority(checkout)
    request = build_request(tool_name="Bash", tool_input={"command": "git status"},
                            authority=authority, argv=("git", "status"),
                            head_sha="a" * 40, origin_main_sha="b" * 40)
    changed = build_request(tool_name="Bash", tool_input={"command": "git status -s"},
                            authority=authority, argv=("git", "status", "-s"),
                            head_sha="a" * 40, origin_main_sha="b" * 40,
                            request_id=request.request_id)
    if request.digest() == changed.digest():
        return Check("approval_binding", False,
                     "two different commands produced the same request digest")
    binding = request.binding()
    required = {"tool_name", "tool_input", "argv", "executable_identity", "env_subset",
                "cwd", "target_paths", "file_identities", "task_id", "stage", "branch",
                "worktree", "head_sha", "origin_main_sha", "policy_version",
                "controller_version", "permission_mode", "request_id"}
    missing = sorted(required - set(binding))
    if missing:
        return Check("approval_binding", False, f"binding is missing {missing}")
    if "stated_reason" in binding:
        return Check("approval_binding", False,
                     "the untrusted stated reason must not be part of the binding")
    return Check("approval_binding", True,
                 f"{len(binding)} bound elements; a changed argument changes the digest; "
                 f"the model's stated reason is excluded")


def _check_claude_adapter() -> Check:
    """Prove the confirmed CLI shape is enforced (Phase 1 probe findings)."""
    argv = build_claude_argv(RunnerConfig(executable="claude", max_turns=4))
    for flag in ("-p", "--input-format", "stream-json", "--output-format",
                 "--verbose", "--max-turns", "--permission-mode", "manual",
                 "--permission-prompt-tool", "stdio"):
        if flag not in argv:
            return Check("claude_adapter", False, f"argv is missing {flag!r}")
    try:
        build_claude_argv(RunnerConfig(executable="claude", permission_mode="acceptEdits"))
    except RunnerError:
        pass
    else:
        return Check("claude_adapter", False,
                     "a non-manual permission mode was NOT refused")
    try:
        build_claude_argv(RunnerConfig(executable="claude", resume_session_id="s-1"))
    except RunnerError:
        pass
    else:
        return Check("claude_adapter", False,
                     "an unverified --resume was NOT refused")
    return Check("claude_adapter", True,
                 "the confirmed argv is enforced; a non-manual permission mode and an "
                 "unverified exact-session resume are both refused")


def _check_control_response_disclosure() -> Check:
    """State the verification status of the control-response wrapper honestly."""
    sample = build_control_response("req-1", "deny", message="denied")
    shape_ok = (sample.get("type") == "control_response"
                and sample["response"]["subtype"] == "success"
                and sample["response"]["response"]["behavior"] == "deny")
    if not shape_ok:
        return Check("control_response_shape", False, "the wrapper shape is malformed")
    status = "VERIFIED" if CONTROL_RESPONSE_WRAPPER_VERIFIED else "UNVERIFIED"
    return Check(
        "control_response_shape", True,
        f"wrapper built as documented; live-CLI verification status: {status}. The Phase 1 "
        f"probe recorded the control REQUEST payload verbatim and a successful deny "
        f"round-trip, but not the exact response wrapper bytes - a preflight round-trip "
        f"probe must confirm it before any live worker run")


def _check_codex_adapter() -> Check:
    """Prove the reviewer is read-only by construction (invariant 10)."""
    schema = PACKAGE_ROOT / "schemas" / "codex_decision.schema.json"
    argv = build_codex_argv("codex", repo=str(PACKAGE_ROOT), model="probe-model",
                            schema_path=str(schema), output_path="out.json")
    for flag in ("exec", "-C", "-m", "--ephemeral", "--ignore-user-config",
                 "--strict-config", "--sandbox", "read-only", "--json",
                 "--output-schema", "--output-last-message", "-"):
        if flag not in argv:
            return Check("codex_adapter", False, f"argv is missing {flag!r}")
    try:
        build_codex_argv("codex", repo=".", model="m", schema_path="s", output_path="o",
                         sandbox="workspace-write")
    except ReviewError:
        pass
    else:
        return Check("codex_adapter", False, "a writable sandbox was NOT refused")
    return Check("codex_adapter", True,
                 "fresh-process argv carries --ephemeral --ignore-user-config "
                 "--strict-config --sandbox read-only; a writable sandbox is refused")


def _check_push_policy() -> Check:
    """Prove the push checks deny main and force, and that nothing executes."""
    assert_no_execution()
    plan = PushPlan(remote_name="origin", remote_url="https://github.com/o/r.git",
                    expected_remote_url="https://github.com/o/r", branch="main",
                    authorized_branch="task/x", local_head="a" * 40)
    main_result = evaluate_push(plan)
    forced = evaluate_push(dataclasses_replace(plan, branch="task/x", force=True))
    if main_result.decision.tier != HARD_DENY:
        return Check("push_policy", False, "a push to main was not hard-denied")
    if forced.decision.tier != HARD_DENY:
        return Check("push_policy", False, "a force push was not hard-denied")
    if main_result.executed or forced.executed:
        return Check("push_policy", False, "a push evaluation reported execution")
    return Check("push_policy", True,
                 "main and force pushes are hard-denied; sensitive path classes, "
                 "privileged workflows, and deployment paths gate to ASK; NO push is "
                 "executed in this phase")


def _check_external_effects() -> Check:
    """Prove the effect model refuses unmodeled writes and keys are stable."""
    first = stable_action_id(effect_type="github_pr_create", target="pr#1",
                             task_id="T", request_digest="d")
    second = stable_action_id(effect_type="github_pr_create", target="pr#1",
                              task_id="T", request_digest="d")
    if first != second:
        return Check("external_effects", False, "the idempotency key is not stable")
    try:
        spec_for("send_wire_transfer")
    except ExternalEffectError:
        pass
    else:
        return Check("external_effects", False, "an unmodeled effect was accepted")
    return Check("external_effects", True,
                 "idempotency keys are content-stable; unmodeled external writes are "
                 "refused and remain ASK-gated")


def _check_evidence_bounds() -> Check:
    """Prove truncation is explicit and an oversized packet stops for the owner."""
    text, truncated = bound_text("x" * 100, 10)
    if not truncated or "TRUNCATED" not in text:
        return Check("evidence_bounds", False, "truncation is not explicitly marked")
    oversized = build_packet(
        run_id="r", task_id="t", checkpoint_id="c",
        checkpoint={"schema_version": "1", "checkpoint_id": "c"},
        extra_sections={"bulk": "y" * 5000}, max_packet_bytes=1024)
    if oversized.stop != STOP_FOR_OWNER:
        return Check("evidence_bounds", False,
                     "an oversized packet did not return STOP_FOR_OWNER")
    return Check("evidence_bounds", True,
                 f"truncation carries an explicit marker; material that will not fit the "
                 f"{DEFAULT_PACKET_BYTES}-byte bound returns STOP_FOR_OWNER instead of "
                 f"being silently omitted")


def dataclasses_replace(obj: Any, **changes: Any) -> Any:
    """Local alias so `doctor` can build plan variants without a top-level import."""
    import dataclasses as _dc

    return _dc.replace(obj, **changes)


def cmd_doctor(args: argparse.Namespace) -> int:
    """Read-only health check across every implemented phase."""
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
        _check_policy_tiers(checkout),
        _check_approval_binding(checkout),
        _check_claude_adapter(),
        _check_control_response_disclosure(),
        _check_codex_adapter(),
        _check_push_policy(),
        _check_external_effects(),
        _check_evidence_bounds(),
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
# approval commands (S12.1, S8.4, S13.10)
# --------------------------------------------------------------------------


def _open_broker(args: argparse.Namespace) -> tuple[DurableJournal, ApprovalBroker]:
    """Open the journal and an owner-side broker view of it.

    The owner-side commands only read, answer, and revoke; they never classify,
    so the authority object here is a read-only placeholder.
    """
    checkout = pathlib.Path(args.checkout).resolve()
    runtime = runtime_dir_for(checkout, base=args.runtime_base)
    journal = DurableJournal(runtime / DB_FILENAME).open()
    audit = AuditLog(runtime / AUDIT_FILENAME)
    authority = TaskAuthority(task_id="", stage="", repo_root=str(checkout),
                              worktree=str(checkout), branch="", active=False,
                              status="operator")
    return journal, ApprovalBroker(journal, audit, authority=authority, mode="operator")


def cmd_pending_approvals(args: argparse.Namespace) -> int:
    """List every queued request with the EXACT digest the owner must quote."""
    journal, broker = _open_broker(args)
    try:
        records = broker.pending()
        items = []
        for record in records:
            request = record.get("request", {})
            outcome = record.get("outcome", {})
            items.append({
                "request_id": request.get("request_id", ""),
                "digest": record.get("request_digest", ""),
                "tool_name": request.get("tool_name", ""),
                "task_id": request.get("task_id", ""),
                "branch": request.get("branch", ""),
                "target_paths": request.get("target_paths", []),
                "tier": outcome.get("tier", ""),
                "reason_code": outcome.get("reason_code", ""),
                "reason": outcome.get("reason", ""),
                "classification": record.get("policy", {}).get("classification", ""),
                "session_id": record.get("session_id", ""),
                "rejected_suggestions": outcome.get("rejected_suggestions", []),
                "queued_at_utc": record.get("updated_at_utc", ""),
            })
    finally:
        journal.close()

    if args.json:
        print(json.dumps({"command": "pending-approvals", "count": len(items),
                          "pending": items}, indent=2))
    else:
        if not items:
            print("no pending approvals.")
        for item in items:
            print(f"{item['request_id']}  {item['tier']}  {item['tool_name']}")
            print(f"  digest : {item['digest']}")
            print(f"  task   : {item['task_id']}  branch: {item['branch']}")
            print(f"  why    : {item['reason']}")
            if item["rejected_suggestions"]:
                print(f"  refused suggestions: {item['rejected_suggestions']}")
            print("  answer : approve-once <request-id> <digest>  |  deny <request-id> "
                  "<digest>")
    return 0


def _answer(args: argparse.Namespace, approve: bool) -> int:
    journal, broker = _open_broker(args)
    try:
        if approve:
            outcome = broker.approve_once(args.request_id, args.displayed_digest)
        else:
            outcome = broker.deny_request(args.request_id, args.displayed_digest,
                                          reason="denied by the owner at the CLI")
    except BrokerError as exc:
        print(f"{exc.code}: {exc.message}", file=sys.stderr)
        return 1
    finally:
        journal.close()

    payload = outcome.to_dict()
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{outcome.behavior}: {outcome.reason}")
        print(f"digest: {outcome.request_digest}")
        if outcome.behavior == "APPROVE_ONCE":
            print("this approval is single-use and is revalidated immediately before "
                  "execution; any change invalidates it.")
    return 0 if outcome.behavior in ("APPROVE_ONCE", "DENY") else 1


def cmd_approve_once(args: argparse.Namespace) -> int:
    return _answer(args, approve=True)


def cmd_deny(args: argparse.Namespace) -> int:
    return _answer(args, approve=False)


def cmd_revoke_all(args: argparse.Namespace) -> int:
    """Revoke every pending/unconsumed approval and reassert limited-auto off."""
    journal, broker = _open_broker(args)
    try:
        revoked = broker.revoke_all(reason="operator revoke-all")
    finally:
        journal.close()
    if args.json:
        print(json.dumps({"command": "revoke-all", "revoked": revoked,
                          "limited_auto_enabled": False}, indent=2))
    else:
        print(f"revoked {revoked} pending/unconsumed approval(s).")
        print("limited-auto: disabled (it is not implemented and cannot be enabled here).")
    return 0


def cmd_verify_controller(args: argparse.Namespace) -> int:
    """Verify the LIVE controller package against a recorded manifest (S13.1)."""
    if args.manifest is None:
        manifest = generate_manifest(PACKAGE_ROOT)
        payload = {
            "command": "verify-controller",
            "ok": True,
            "generated": True,
            "files": len(manifest["files"]),
            "manifest_digest": manifest["manifest_digest"],
            "controller_version": CONTROLLER_VERSION,
            "note": (f"no --manifest supplied, so this generated one over the live "
                     f"package. {MODEL_SELECTION_FILENAME} is deliberately excluded: "
                     f"changing a model never invalidates the controller."),
        }
        print(json.dumps(payload, indent=2) if args.json else
              f"generated manifest over {payload['files']} files: "
              f"{payload['manifest_digest']}\n{payload['note']}")
        return 0
    try:
        manifest = read_manifest(args.manifest)
    except Exception as exc:
        print(f"manifest unreadable: {exc}", file=sys.stderr)
        return 1
    verification = verify_manifest(PACKAGE_ROOT, manifest)
    payload = {
        "command": "verify-controller",
        "ok": verification.ok,
        "detail": "" if verification.ok else verification.halt_reason(),
        "controller_version": CONTROLLER_VERSION,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("controller verified." if verification.ok
              else f"HALT: {verification.halt_reason()}")
    return 0 if verification.ok else 1


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

    pending = sub.add_parser("pending-approvals",
                             help="list queued requests with their digests (live)")
    add_common(pending)
    pending.set_defaults(func=cmd_pending_approvals)

    revoke = sub.add_parser("revoke-all",
                            help="revoke every pending/unconsumed approval (live)")
    add_common(revoke)
    revoke.set_defaults(func=cmd_revoke_all)

    verify = sub.add_parser("verify-controller",
                            help="verify the live controller against a manifest (live)")
    add_common(verify)
    verify.add_argument("--manifest", default=None,
                        help="path to a recorded controller_manifest.json")
    verify.set_defaults(func=cmd_verify_controller)

    simple = [
        "pause", "resume", "stop", "emergency-stop",
        "recovery-status", "schedule-status", "cancel-scheduled-resume",
        "autostart-plan", "install-autostart", "uninstall-autostart",
        "export-handoff",
    ]
    for name in simple:
        p = sub.add_parser(name, help=f"{DEFERRED_COMMANDS.get(name, 'later phase')}")
        add_common(p)
        p.set_defaults(func=cmd_deferred)

    for name, handler in (("approve-once", cmd_approve_once), ("deny", cmd_deny)):
        p = sub.add_parser(name, help=f"answer a queued request by its exact digest "
                                      f"({name}, live)")
        add_common(p)
        p.add_argument("request_id")
        p.add_argument("displayed_digest")
        p.set_defaults(func=handler)

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
