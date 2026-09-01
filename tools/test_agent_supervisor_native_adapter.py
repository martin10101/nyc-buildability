"""M0-T104 (D-024 Amendment 3 unit C): native runtime adapter tests.

Deterministic rows use injected fake runners; live rows are feature-detected
and skip cleanly when ``claude`` is absent (D-024 16.1). Scenario IDs (S1-S18,
C1-C2) map to the acceptance pack in
``project-control/reports/M0-T104-native-adapter.md`` section 1.

Supervisor-freeze qualifying evidence: D-024-R153, D-024-R172.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import uuid
from pathlib import Path

import pytest

from tools.agent_supervisor import native_runtime as nr
from tools.agent_supervisor import runtime_backend as rb

FIXTURES = Path(__file__).parent / "agent_supervisor" / "fixtures"
DETECTION_FIXTURE = FIXTURES / "native_runtime_detection_2026-09-01_m0t132.json"
AGENTS_FIXTURE = FIXTURES / "agents_listing_2026-08-27_m0t104.json"
AGENTS_ALL_FIXTURE = FIXTURES / "agents_listing_all_2026-08-27_m0t104.json"

IDENTITY = nr.derive_session_identity("d024", "m0-t104", attempt=1)

#: Masked sample matching the MEASURED 2.1.247 ``agents --json`` shape
#: (background row with the waiting+failed display conflict; interactive
#: rows with and without a status field; an extra unknown field).
SAMPLE_ROWS = [
    {"pid": 21448, "id": "777b09da", "cwd": "[HOME]\\proj",
     "kind": "background", "startedAt": 1787196188173,
     "sessionId": "777b09da-0000-4000-8000-000000000000",  # synthetic
     "name": "parked-example", "status": "waiting",
     "waitingFor": "permission prompt", "state": "failed"},
    {"pid": 10160, "cwd": "[HOME]\\proj\\ctl24", "kind": "interactive",
     "startedAt": 1787711526404, "sessionId": str(uuid.uuid4()),
     "name": "owner-terminal", "status": "waiting",
     "waitingFor": "dialog open"},
    {"pid": 6888, "cwd": "[HOME]\\other", "kind": "interactive",
     "startedAt": 1787718605848, "sessionId": str(uuid.uuid4()),
     "name": "owner-terminal-2", "futureField": {"x": 1}},
    {"pid": 4242, "cwd": "[HOME]\\proj", "kind": "background",
     "sessionId": IDENTITY.session_id, "name": IDENTITY.name,
     "status": "running"},
]
SAMPLE_TEXT = json.dumps(SAMPLE_ROWS)


def recording_runner(responses):
    """Fake RunCommand keyed by argv tuple; records every call."""
    calls = []

    def run(argv, **kwargs):
        calls.append((tuple(argv), kwargs))
        try:
            return responses[tuple(argv)]
        except KeyError:
            raise AssertionError(f"unexpected argv {argv!r}") from None

    run.calls = calls
    return run


def ok(stdout: str = "", stderr: str = "") -> nr.CommandResult:
    return nr.CommandResult(nr.STATUS_SUPPORTED, 0, stdout, stderr)


def full_help() -> str:
    return ("Usage: claude [options] [command] [prompt]\n"
            + "\n".join(f"  {tok} <x>  desc" for tok in nr.DISPATCH_FLAG_TOKENS))


def verb_help(verb: str) -> nr.CommandResult:
    return ok(f"Usage: claude {verb} <id>\n\n  details\n")


def supported_caps() -> nr.NativeCapabilities:
    responses = {("claude", "--version"): ok("2.1.247 (Claude Code)\n"),
                 ("claude", "--help"): ok(full_help())}
    for verb in nr.BACKGROUND_VERBS:
        responses[("claude", verb, "--help")] = verb_help(verb)
    return nr.detect_native_capabilities(recording_runner(responses))


# ---------- S12: deterministic identity ----------

def test_identity_deterministic_and_valid_uuid():
    a = nr.derive_session_identity("d024", "m0-t104", attempt=2)
    b = nr.derive_session_identity("d024", "m0-t104", attempt=2)
    assert a == b
    assert uuid.UUID(a.session_id)  # valid UUID
    assert a.name == "d024-m0-t104-a2"
    assert a != IDENTITY  # attempt participates in the identity


def test_identity_rejects_unsafe_tokens():
    for bad in ("has space", "Upper.Case!", "path/like", "", "under_score",
                "-leading"):
        with pytest.raises(nr.NativeRuntimeError) as err:
            nr.derive_session_identity(bad, "t")
        assert err.value.code == "invalid_identity_token"
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.derive_session_identity("c", "t", attempt=0)
    assert err.value.code == "invalid_attempt"
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.derive_session_identity("c" * 40, "t" * 40)
    assert err.value.code == "identity_too_long"


def test_identity_carries_no_host_or_user_material():
    """G5 precondition measured on THIS machine: the real campaign/task ids
    never leak hostname or username into the derived name."""
    name = nr.derive_session_identity("d-024-fable-codex-loop", "m0-t104").name
    host = socket.gethostname().lower()
    user = (os.environ.get("USERNAME") or os.environ.get("USER") or "").lower()
    for needle in (host, user):
        if len(needle) >= 4:
            assert needle not in name


# ---------- S13: explicit child environment ----------

def test_child_environment_strips_session_markers():
    base = {"PATH": "/usr/bin", "CLAUDECODE": "1",
            "CLAUDE_CODE_CHILD_SESSION": "1",
            "CLAUDE_CODE_SESSION_ID": "abc", "CLAUDE_CODE_ENTRYPOINT": "cli",
            "HOME": "/home/x"}
    child = nr.child_environment(base)
    assert child == {"PATH": "/usr/bin", "HOME": "/home/x"}
    assert base["CLAUDECODE"] == "1"  # input never mutated


# ---------- S14: permission-mode vocabulary ----------

def test_permission_mode_unflagged_resolves_to_auto():
    assert nr.validate_permission_mode(None) == "auto"


def test_permission_mode_accepts_installed_enum_refuses_bypass():
    for mode in nr.INSTALLED_PERMISSION_MODES:
        if mode == "bypassPermissions":
            with pytest.raises(nr.NativeRuntimeError) as err:
                nr.validate_permission_mode(mode)
            assert err.value.code == "forbidden_permission_mode"
        else:
            assert nr.validate_permission_mode(mode) == mode


def test_permission_mode_default_is_not_a_mode():
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.validate_permission_mode("default")
    assert err.value.code == "unknown_permission_mode"


# ---------- S1: dispatch argv + child env ----------

def test_build_background_argv_exact():
    spec = nr.DispatchSpec(identity=IDENTITY, prompt="do the task",
                           agent="backend-engineer", permission_mode="manual",
                           tools="Bash,Edit,Read")
    assert nr.build_background_argv(spec) == (
        "claude", "--bg", "--name", IDENTITY.name,
        "--agent", "backend-engineer", "--permission-mode", "manual",
        "--strict-mcp-config", "--tools", "Bash,Edit,Read",
        "--", "do the task")


def test_build_background_argv_unflagged_mode_stays_unflagged():
    argv = nr.build_background_argv(
        nr.DispatchSpec(identity=IDENTITY, prompt="p"))
    assert "--permission-mode" not in argv  # unflagged => measured 'auto'


def test_build_background_argv_canary_measured_constraints():
    """C1-measured (2.1.247): --session-id is ignored under --bg so it is
    never emitted, and the prompt rides behind a literal ``--`` (variadic
    --tools otherwise swallows it, leaving the session idle)."""
    argv = nr.build_background_argv(nr.DispatchSpec(
        identity=IDENTITY, prompt="run it", tools=""))
    assert "--session-id" not in argv
    assert argv[-2:] == ("--", "run it")
    tools_value = argv[argv.index("--tools") + 1]
    assert tools_value == ""  # the prompt never merges into the tools list


def test_dispatch_runs_with_stripped_child_env_and_cwd():
    spec = nr.DispatchSpec(identity=IDENTITY, prompt="p", cwd="X:/scratch")
    responses = {nr.build_background_argv(spec): ok("dispatched")}
    run = recording_runner(responses)
    backend = rb.NativeBackgroundBackend(
        run, base_env={"PATH": "x", "CLAUDECODE": "1",
                       "CLAUDE_CODE_SESSION_ID": "parent"})
    backend.dispatch(spec)
    (_, kwargs), = run.calls
    assert kwargs["env"] == {"PATH": "x"}
    assert kwargs["cwd"] == "X:/scratch"  # daemon sessions bind to their cwd


def test_dispatch_default_backend_still_strips_child_env(monkeypatch):
    """G5 F2 / G3 #1: a default-constructed backend (no base_env) must STILL
    strip session markers — the strip is unavoidable, never fail-open to a
    raw-inherited environment."""
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "parent-session")
    monkeypatch.setenv("CLAUDE_CODE_ENTRYPOINT", "cli")
    monkeypatch.setenv("PATH", "/usr/bin")
    spec = nr.DispatchSpec(identity=IDENTITY, prompt="p")
    run = recording_runner({nr.build_background_argv(spec): ok("dispatched")})
    rb.NativeBackgroundBackend(run).dispatch(spec)  # NO base_env
    (_, kwargs), = run.calls
    env = kwargs["env"]
    assert env is not None
    assert "CLAUDECODE" not in env
    assert not any(k.startswith("CLAUDE_CODE_") for k in env)
    assert env.get("PATH") == "/usr/bin"  # non-marker keys preserved


def test_empty_prompt_refused():
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.DispatchSpec(identity=IDENTITY, prompt="   ")
    assert err.value.code == "empty_prompt"


# ---------- S18: no bypass / remote-control surface ----------

def test_forbidden_flags_cannot_be_smuggled_via_values():
    # G5 F1: a flag-shaped value is now rejected at DispatchSpec construction
    # (defence in depth, before the post-build denylist even runs).
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.DispatchSpec(identity=IDENTITY, prompt="p", tools="--teleport")
    assert err.value.code == "invalid_tools"
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.DispatchSpec(identity=IDENTITY, prompt="p", agent="--cloud=x")
    assert err.value.code == "invalid_agent"


def test_agent_tools_value_charsets():
    """G5 F1: agent/tools accept legitimate values, reject flag-shaped ones."""
    spec = nr.DispatchSpec(identity=IDENTITY, prompt="p",
                           agent="backend-engineer",
                           tools="Bash,Edit,Read")
    assert nr.build_background_argv(spec)  # constructs
    assert nr.DispatchSpec(identity=IDENTITY, prompt="p", tools="")  # disable-all
    for bad_tools in ("-x", "--cloud", " --tmux"):
        with pytest.raises(nr.NativeRuntimeError) as err:
            nr.DispatchSpec(identity=IDENTITY, prompt="p", tools=bad_tools)
        assert err.value.code == "invalid_tools"
    for bad_agent in ("-a", "--agent", "has space", "a/b"):
        with pytest.raises(nr.NativeRuntimeError) as err:
            nr.DispatchSpec(identity=IDENTITY, prompt="p", agent=bad_agent)
        assert err.value.code == "invalid_agent"


def test_bypass_mode_never_reaches_argv():
    spec = nr.DispatchSpec(identity=IDENTITY, prompt="p",
                           permission_mode="bypassPermissions")
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.build_background_argv(spec)
    assert err.value.code == "forbidden_permission_mode"


def test_detection_probes_are_help_version_only():
    caps = supported_caps()  # recording runner raises on unexpected argv
    assert caps.background_host_ready
    # and structurally: every probe the detector can issue ends in
    # --version/--help (read-only allowlist, same policy as the probe module)
    run = recording_runner({("claude", "--version"): nr.CommandResult(
        nr.STATUS_ABSENT, None, "", "not on PATH")})
    nr.detect_native_capabilities(run)
    for argv, _ in run.calls:
        assert argv[-1] in ("--version", "--help")


# ---------- S16: measured-at-use, never cached ----------

def test_detection_measures_at_every_call():
    versions = iter(["2.1.247 (Claude Code)\n", "2.1.248 (Claude Code)\n"])

    def run(argv, **kwargs):
        if tuple(argv) == ("claude", "--version"):
            return ok(next(versions))
        if tuple(argv) == ("claude", "--help"):
            return ok(full_help())
        return verb_help(argv[1])

    first = nr.detect_native_capabilities(run)
    second = nr.detect_native_capabilities(run)
    assert first.claude_version == "2.1.247 (Claude Code)"
    assert second.claude_version == "2.1.248 (Claude Code)"


# ---------- verb classification (measured general-help trap) ----------

def test_unknown_verb_general_help_is_not_supported():
    """Measured 2.1.247: unknown subcommand + --help exits 0 with the
    GENERAL usage; classification must not call that supported."""
    general = ok("Usage: claude [options] [command] [prompt]\n...")
    assert nr._classify_verb("attach", general) == nr.STATUS_NOT_IN_HELP
    assert nr._classify_verb("attach", verb_help("attach")) == nr.STATUS_SUPPORTED
    assert nr._classify_verb("attach", nr.CommandResult(
        nr.STATUS_UNKNOWN, 1, "", "boom")) == nr.STATUS_UNKNOWN
    assert nr._classify_verb("attach", nr.CommandResult(
        nr.STATUS_ABSENT, None, "", "")) == nr.STATUS_ABSENT


# ---------- S15: worktree base pinning ----------

def test_worktree_base_must_be_pinned():
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.WorktreeSpec(name="wt-c", base="main")
    assert err.value.code == "worktree_base_unpinned"


def test_worktree_head_refused_on_cli_path():
    spec = nr.DispatchSpec(
        identity=IDENTITY, prompt="p",
        worktree=nr.WorktreeSpec(name="wt-c", base=nr.WORKTREE_BASE_HEAD))
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.build_background_argv(spec)
    assert err.value.code == "worktree_base_head_unsupported_cli"


def test_worktree_sha_pins_with_guarded_reset_preamble():
    sha = "a" * 40
    argv = nr.build_background_argv(nr.DispatchSpec(
        identity=IDENTITY, prompt="do it",
        worktree=nr.WorktreeSpec(name="wt-c", base=sha)))
    assert "--worktree" in argv and "wt-c" in argv
    prompt = argv[-1]
    assert f"git reset --hard {sha}" in prompt
    assert "--show-toplevel" in prompt          # primary-checkout guard
    assert prompt.endswith("do it")


# ---------- S2/S3/S4/S5: agents --json ingestion ----------

def test_parse_agents_json_typed_records():
    records = nr.parse_agents_json(SAMPLE_TEXT)
    assert len(records) == 4
    parked = records[0]
    assert parked.kind == "background"
    assert parked.classification == nr.CLASS_FAILED  # state wins the conflict
    assert parked.raw_status == "waiting"            # raw fields preserved
    assert parked.waiting_for == "permission prompt"
    assert records[1].classification == nr.CLASS_BLOCKED_INPUT
    assert records[2].classification == nr.CLASS_RUNNING  # pid, no status
    assert records[3].classification == nr.CLASS_RUNNING


def test_background_filter_never_manages_interactive():
    records = nr.parse_agents_json(SAMPLE_TEXT)
    names = {r.name for r in nr.background_sessions(records)}
    assert names == {"parked-example", IDENTITY.name}


def test_find_by_identity_prefers_session_uuid():
    records = nr.parse_agents_json(SAMPLE_TEXT)
    hit = nr.find_by_identity(records, IDENTITY)
    assert hit is not None and hit.session_id == IDENTITY.session_id
    ghost = nr.derive_session_identity("d024", "m0-t999")
    assert nr.find_by_identity(records, ghost) is None


def test_completed_classification():
    rows = [{"sessionId": "s1", "kind": "background", "status": "completed"},
            {"sessionId": "s2", "kind": "background", "state": "completed"},
            # measured C1 round a2: finished run shows idle + done
            {"sessionId": "s3", "kind": "background", "status": "idle",
             "state": "done"}]
    records = nr.parse_agents_json(json.dumps(rows))
    assert all(r.classification == nr.CLASS_COMPLETED for r in records)


def test_canary_measured_idle_and_stopped_literals():
    """C1-measured rows: idle+blocked = awaiting a prompt (blocked-input);
    state=stopped = operator-stopped, its own class."""
    rows = [{"sessionId": "a1", "kind": "background", "status": "idle",
             "state": "blocked"},
            {"sessionId": "a1h", "kind": "background", "state": "stopped"},
            {"sessionId": "solo-idle", "kind": "background", "status": "idle"}]
    records = nr.parse_agents_json(json.dumps(rows))
    assert records[0].classification == nr.CLASS_BLOCKED_INPUT
    assert records[1].classification == nr.CLASS_STOPPED
    assert records[2].classification == nr.CLASS_BLOCKED_INPUT


def test_unknown_status_stays_unknown_never_guessed():
    rows = [{"sessionId": "s1", "kind": "background",
             "status": "hyperspace-jump"}]
    (record,) = nr.parse_agents_json(json.dumps(rows))
    assert record.classification == nr.CLASS_UNKNOWN
    assert record.raw_status == "hyperspace-jump"


@pytest.mark.parametrize("payload", [
    "not json at all", '{"an": "object"}', '[{"name": "no-session-id"}]',
    '[{"sessionId": 42}]', '[null]'])
def test_malformed_agents_json_typed_error(payload):
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.parse_agents_json(payload)
    assert err.value.code == "malformed_agents_json"


def test_observe_unavailable_feed_typed_error():
    run = recording_runner({nr.AGENTS_STATUS_ARGV: nr.CommandResult(
        nr.STATUS_UNKNOWN, 1, "", "daemon down")})
    backend = rb.NativeBackgroundBackend(run)
    with pytest.raises(nr.NativeRuntimeError) as err:
        backend.observe()
    assert err.value.code == "agents_feed_unavailable"
    assert backend.daemon_status().available is False


def test_observe_parses_and_daemon_available():
    run = recording_runner({nr.AGENTS_STATUS_ARGV: ok(SAMPLE_TEXT),
                            nr.AGENTS_STATUS_ALL_ARGV: ok(SAMPLE_TEXT)})
    backend = rb.NativeBackgroundBackend(run)
    assert len(backend.observe()) == 4
    assert len(backend.observe(include_completed=True)) == 4
    assert backend.daemon_status().available is True


# ---------- S6/S7: verb wrappers ----------

def test_stop_logs_respawn_attach_argv():
    run = recording_runner({("claude", "stop", "abc"): ok("stopped"),
                            ("claude", "logs", "abc"): ok("tail"),
                            ("claude", "respawn", "abc"): ok("respawned"),
                            ("claude", "respawn", "--all"): ok("all")})
    backend = rb.NativeBackgroundBackend(run)
    assert backend.stop("abc").stdout == "stopped"
    assert backend.logs("abc").stdout == "tail"
    assert backend.respawn("abc").stdout == "respawned"
    assert backend.respawn(all_sessions=True).stdout == "all"
    assert backend.attach_argv("abc") == ("claude", "attach", "abc")
    assert run.calls[-1][0] == ("claude", "respawn", "--all")


def test_verb_check_surfaces_daemon_failure():
    """G4 ADV-2: with check=True a daemon-rejected command raises a typed
    error instead of returning a silently-failed result; check=False (default)
    preserves the raw result for callers that inspect it (e.g. stop of a
    gone session)."""
    fail = nr.CommandResult(nr.STATUS_UNKNOWN, 1, "", "no such session")
    run = recording_runner({("claude", "stop", "gone"): fail,
                            ("claude", "logs", "gone"): fail,
                            ("claude", "respawn", "gone"): fail})
    backend = rb.NativeBackgroundBackend(run)
    # default: raw result, no raise
    assert backend.stop("gone").status == nr.STATUS_UNKNOWN
    # check=True: typed error per verb
    for verb, call in (("stop", lambda: backend.stop("gone", check=True)),
                       ("logs", lambda: backend.logs("gone", check=True)),
                       ("respawn", lambda: backend.respawn("gone", check=True))):
        with pytest.raises(nr.NativeRuntimeError) as err:
            call()
        assert err.value.code == f"{verb}_failed"


def test_verb_argv_validation():
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.build_verb_argv("logs", None)
    assert err.value.code == "missing_session_ref"
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.build_verb_argv("logs", "x", all_sessions=True)
    assert err.value.code == "all_not_supported"
    with pytest.raises(nr.NativeRuntimeError) as err:
        nr.build_verb_argv("erase", "x")
    assert err.value.code == "unknown_verb"


# ---------- S10: fallback selection (fail closed) ----------

def test_native_selected_only_with_optin_and_full_support():
    caps = supported_caps()
    sel = rb.select_runtime_backend(caps, prefer_native=True)
    assert sel.backend == rb.BACKEND_NATIVE
    assert sel.reason == rb.REASON_NATIVE_READY
    assert sel.claude_version == "2.1.247 (Claude Code)"


def test_controller_when_config_does_not_opt_in():
    sel = rb.select_runtime_backend(supported_caps(), prefer_native=False)
    assert sel.backend == rb.BACKEND_CONTROLLER
    assert sel.reason == rb.REASON_CONFIG_CONTROLLER


def test_controller_on_any_capability_gap_including_unknown():
    caps = supported_caps()
    degraded = nr.NativeCapabilities(
        caps.claude_version, dict(caps.flags),
        {**caps.verbs, "respawn": nr.STATUS_UNKNOWN})
    sel = rb.select_runtime_backend(degraded, prefer_native=True)
    assert sel.backend == rb.BACKEND_CONTROLLER
    assert "verb:respawn=unknown" in sel.reason


def test_controller_when_claude_absent():
    caps = nr.detect_native_capabilities(recording_runner(
        {("claude", "--version"): nr.CommandResult(
            nr.STATUS_ABSENT, None, "", "not on PATH")}))
    sel = rb.select_runtime_backend(caps, prefer_native=True)
    assert sel.backend == rb.BACKEND_CONTROLLER
    assert "claude:absent" in sel.reason


def test_controller_backend_delegates_to_existing_dispatch():
    seen = []
    backend = rb.ControllerBackend(lambda spec: seen.append(spec) or "ran")
    spec = nr.DispatchSpec(identity=IDENTITY, prompt="p")
    assert backend.dispatch(spec) == "ran"
    assert seen == [spec]


# ---------- S11: one backend, never two ----------

def test_second_backend_activation_refused():
    session = rb.RuntimeSession()
    first = session.activate(rb.BackendSelection(
        rb.BACKEND_NATIVE, rb.REASON_NATIVE_READY, "2.1.247 (Claude Code)"))
    assert session.active == first
    with pytest.raises(nr.NativeRuntimeError) as err:
        session.activate(rb.BackendSelection(
            rb.BACKEND_CONTROLLER, rb.REASON_CONFIG_CONTROLLER, None))
    assert err.value.code == "backend_already_active"
    with pytest.raises(nr.NativeRuntimeError) as err:
        rb.RuntimeSession().activate(rb.BackendSelection("both", "x", None))
    assert err.value.code == "unknown_backend"


# ---------- S8/S9: supervisor-restart reconciliation ----------

def test_restart_no_duplicate_and_unexpected_exit():
    running_id = IDENTITY
    done_id = nr.derive_session_identity("d024", "m0-t105")
    gone_id = nr.derive_session_identity("d024", "m0-t106")
    active = nr.parse_agents_json(SAMPLE_TEXT)
    completed = nr.parse_agents_json(json.dumps(
        [{"sessionId": done_id.session_id, "name": done_id.name,
          "kind": "background", "status": "completed"}]))
    rec = rb.reconcile_after_restart(
        [running_id, done_id, gone_id], active, completed)
    assert rec.running == (running_id,)
    assert rec.completed == (done_id,)
    assert rec.unexpected_exit == (gone_id,)
    # renamed property (G5 F4) says what it is; back-compat alias preserved
    assert rec.needs_controller_review == (gone_id,)
    assert rec.safe_to_dispatch == (gone_id,)
    assert running_id not in rec.needs_controller_review  # no-duplicate core


def test_reconcile_refuses_unavailable_feed():
    """G5 F4: reconciling against a down feed would read as all-missing and
    risk mass duplicate dispatch — it must fail closed."""
    with pytest.raises(nr.NativeRuntimeError) as err:
        rb.reconcile_after_restart([IDENTITY], [], feed_available=False)
    assert err.value.code == "reconcile_feed_unavailable"


def test_restart_blocked_and_failed_surface():
    blocked_id = nr.derive_session_identity("d024", "m0-t107")
    failed_id = nr.derive_session_identity("d024", "m0-t108")
    active = nr.parse_agents_json(json.dumps([
        {"sessionId": blocked_id.session_id, "name": blocked_id.name,
         "kind": "background", "status": "waiting", "waitingFor": "input"},
        {"sessionId": failed_id.session_id, "name": failed_id.name,
         "kind": "background", "status": "waiting", "state": "failed"}]))
    rec = rb.reconcile_after_restart([blocked_id, failed_id], active)
    assert rec.blocked_input == (blocked_id,)
    assert rec.failed == (failed_id,)
    assert rec.unexpected_exit == ()


def test_restart_stopped_and_unknown_surface():
    stopped_id = nr.derive_session_identity("d024", "m0-t110")
    weird_id = nr.derive_session_identity("d024", "m0-t111")
    completed = nr.parse_agents_json(json.dumps([
        {"sessionId": stopped_id.session_id, "name": stopped_id.name,
         "kind": "background", "state": "stopped"}]))
    active = nr.parse_agents_json(json.dumps([
        {"sessionId": weird_id.session_id, "name": weird_id.name,
         "kind": "background", "status": "hyperspace-jump"}]))
    rec = rb.reconcile_after_restart([stopped_id, weird_id], active, completed)
    assert rec.stopped == (stopped_id,)
    # unknown display state parks with blocked-input: controller looks first
    assert rec.blocked_input == (weird_id,)
    assert rec.safe_to_dispatch == ()


# ---------- R032 honesty ----------

def test_activation_limitations_report_blocker_not_persistence():
    text = " ".join(rb.activation_limitations())
    assert "one-command start" in text
    assert "activation blocker" in text
    assert "unattended persistence" not in text.replace(
        "never a claim", "")  # asserted phrasing stays honest


# ---------- masking + committed fixtures ----------

def test_mask_session_row():
    masked = nr.mask_session_row(
        {"sessionId": "777b09da-0000-4000-8000-000000000000",
         "id": "777b09da",
         "cwd": "C:\\Users\\SomeOne\\Temp\\aaaabbbb-0000-4000-8000-"
                "000000000000\\scratch"})
    assert masked["sessionId"] == "777b09da-[MASKED]"
    assert masked["id"] == "777b09da"        # 8 chars stays
    assert "Users" not in masked["cwd"]
    # UUID-shaped path segments (session scratch dirs) are truncated too
    assert "aaaabbbb-[MASKED]" in masked["cwd"]
    assert "aaaabbbb-0000" not in masked["cwd"]


def test_mask_session_row_comprehensive_all_fields():
    """G5 F3: masking is a comprehensive pass over EVERY string value, not a
    3-field allowlist — a UUID or home path in name/waitingFor/future fields
    is masked too."""
    masked = nr.mask_session_row({
        "sessionId": "abcd1234-0000-4000-8000-000000000000",
        "name": "run cccc1234-0000-4000-8000-000000000000",
        "waitingFor": "prompt at C:\\Users\\SomeOne\\proj",
        "futureField": "/home/someone/leak deded234-0000-4000-8000-000000000000",
    })
    whole = json.dumps(masked)
    # no full UUID survives anywhere
    import re as _re
    assert not _re.search(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", whole)
    assert "cccc1234-[MASKED]" in masked["name"]
    assert "Users\\SomeOne" not in masked["waitingFor"]
    assert "/home/someone" not in masked["futureField"]


def test_build_agents_fixture_masks_and_drops_volatile():
    fixture = nr.build_agents_fixture(SAMPLE_ROWS, task="M0-T104")
    text = json.dumps(fixture)
    assert fixture["task"] == "M0-T104"
    assert "pid" not in text and "startedAt" not in text
    for row in fixture["sessions"]:
        assert row["sessionId"].endswith("-[MASKED]")


@pytest.fixture(scope="module")
def detection() -> dict:
    return json.loads(DETECTION_FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def agents_listing() -> dict:
    return json.loads(AGENTS_FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def agents_all_listing() -> dict:
    return json.loads(AGENTS_ALL_FIXTURE.read_text(encoding="utf-8"))


def test_committed_detection_fixture_shape(detection):
    # M0-T132 re-capture (D-024 Amendment 34): deliberate 2.1.252 admission
    # re-probed live; every flag/verb classification identical to 2.1.251
    # (benign patch bump); the m0t118 (2.1.251) fixture stays committed as history.
    assert detection["schema"] == "native_runtime_detection/v1"
    assert detection["task"] == "M0-T132"          # G3 ADV-1
    assert detection["claude_version"] == "2.1.252 (Claude Code)"
    assert detection["background_gaps"] == []
    for verb in nr.BACKGROUND_VERBS:
        assert detection["verbs"][verb] == "supported"
    whole = json.dumps(detection)
    assert "Users" not in whole and "MLFLL" not in whole


def test_committed_agents_fixture_masked(agents_listing):
    assert agents_listing["schema"] == "native_runtime_agents_listing/v1"
    assert agents_listing["task"] == "M0-T104"     # G3 ADV-1
    whole = json.dumps(agents_listing)
    for leak in (":\\\\Users\\\\", ":/Users/", "MLFLL"):
        assert leak not in whole, f"unmasked fragment {leak!r}"
    assert agents_listing["sessions"], "capture recorded no sessions"
    for row in agents_listing["sessions"]:
        assert "pid" not in row and "startedAt" not in row


def test_committed_agents_fixture_parses_after_unmasking(agents_listing):
    """The masked fixture still round-trips the parser (masking never breaks
    the ingestion contract)."""
    records = nr.parse_agents_json(json.dumps(agents_listing["sessions"]))
    assert records
    assert all(r.classification in (
        nr.CLASS_RUNNING, nr.CLASS_BLOCKED_INPUT, nr.CLASS_COMPLETED,
        nr.CLASS_STOPPED, nr.CLASS_FAILED, nr.CLASS_UNKNOWN)
        for r in records)


def test_committed_all_listing_carries_canary_lifecycle(agents_all_listing):
    """The post-C1 ``--all`` capture freezes the real canary lifecycle rows:
    round a1 operator-stopped, round a2 ran to done (CANARY-C-DONE)."""
    assert agents_all_listing["task"] == "M0-T104"
    records = nr.parse_agents_json(
        json.dumps(agents_all_listing["sessions"]))
    by_name = {r.name: r for r in records if "canary" in r.name}
    assert by_name["d024-m0-t104-canary-a1"].classification == nr.CLASS_STOPPED
    assert by_name["d024-m0-t104-canary-a2"].classification == nr.CLASS_COMPLETED
    whole = json.dumps(agents_all_listing)
    for leak in (":\\\\Users\\\\", ":/Users/", "MLFLL"):
        assert leak not in whole, f"unmasked fragment {leak!r}"


# ---------- live rows (feature-detected; skip when claude absent) ----------

requires_claude = pytest.mark.skipif(
    shutil.which("claude") is None,
    reason="claude CLI not installed on this runner")


@requires_claude
def test_live_detection_matches_committed_fixture(detection):
    """Adapter drift tooth: the live surface still matches the committed
    2.1.247 record (version + every required verb)."""
    caps = nr.detect_native_capabilities()
    assert caps.claude_version == detection["claude_version"], (
        "installed claude drifted from the committed detection fixture; "
        "re-run the unit-C detection capture and re-review")
    assert caps.background_host_ready, caps.background_gaps()


@requires_claude
def test_live_agents_json_parses():
    """Live structured feed ingests without error (R154 passive path)."""
    backend = rb.NativeBackgroundBackend()
    records = backend.observe()
    assert isinstance(records, tuple)
    # this orchestrator session itself appears as an interactive row
    assert any(r.kind == "interactive" for r in records)
