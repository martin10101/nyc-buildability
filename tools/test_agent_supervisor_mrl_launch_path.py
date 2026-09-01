"""Paired tests for the ``start --launch-manifest`` entrance (M0-T136 C-B1; D-024-R557..R560, R589).

Two seams are proven, each with its negative twin:

* ``apply_launch_manifest`` (before the runtime opens): fills every dispatch input the
  operator did not type, never fills ``--mode``, refuses typed disagreement (listing
  EVERY conflict), refuses an invalid manifest, and refuses a multi-task launch.
* ``preflight_launch`` (inside ``_run_loop`` at PREFLIGHT): re-observes every R559 field
  independently, records the comparison, and raises the typed mismatch that
  ``cmd_start`` reports as a refusal - before any provider launch.

The last class drives the REAL ``cli.main(["start", ...])`` against a real git fixture
checkout: a manifest that disagrees refuses at exit 11 with NO worker spawned; the same
manifest, agreeing, dispatches with only ``--mode`` and ``--launch-manifest`` typed.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor import mrl_launch_manifest as mlm  # noqa: E402
from tools.agent_supervisor import mrl_launch_path as mlp  # noqa: E402
from tools.agent_supervisor import refusals  # noqa: E402
from tools.agent_supervisor.errors import LoopError  # noqa: E402
from tools.test_agent_supervisor_mrl_launch_manifest import HEAD, FakeGit, build_world  # noqa: E402

UNSAFE_EXIT = refusals.EXIT_CODES[refusals.UNSAFE]


@pytest.fixture
def world(tmp_path: pathlib.Path):
    return build_world(tmp_path)


class FakeAudit:
    """The two things ``preflight_launch`` needs from the audit log: a path and append()."""

    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        self.events: list[dict] = []

    def append(self, event: str, **kw) -> None:
        self.events.append({"event": event, **kw})

    def names(self) -> list[str]:
        return [e["event"] for e in self.events]


def _parse(*argv: str) -> argparse.Namespace:
    from tools.agent_supervisor import cli
    return cli.build_parser().parse_args(["start", *argv])


def _hermetic(world) -> None:
    """Pin the manifest's profile identity to the profile the launch will really build.

    ``managed_settings_path`` is set to "" (accounted-absent) so the identity does not
    depend on whether this host carries a managed policy; the identity is then the
    one ``observe_profile_identity`` computes from the manifest's own subagent section.
    """
    world["manifest"]["dispatch"]["managed_settings_path"] = ""
    _write(world)
    m = mlm.LaunchManifest.load(world["manifest_path"])
    scratch = world["tmp"] / "scratch"
    identity, _profile = mlm.observe_profile_identity(m, profile_dir=scratch, ledger_path=scratch / "l.json")
    world["manifest"]["expected"]["settings_profile_sha256"] = identity
    _write(world)


def _write(world) -> None:
    world["manifest_path"].write_text(json.dumps(world["manifest"]), encoding="utf-8")


# ---------------------------------------------------------------- apply_launch_manifest

def test_absent_flag_is_a_no_op(world):
    args = _parse("--mode", "shadow")
    before = dict(vars(args))
    manifest, refusal = mlp.apply_launch_manifest(args)
    assert (manifest, refusal) == (None, None)
    assert vars(args) == before, "the legacy explicit-flag path must be untouched"
    assert not hasattr(args, mlp.LOADED_ATTR)


def test_manifest_fills_every_dispatch_input_and_never_mode(world):
    args = _parse("--mode", "shadow", "--launch-manifest", str(world["manifest_path"]))
    manifest, refusal = mlp.apply_launch_manifest(args)
    assert refusal is None and manifest is not None
    d, e = world["manifest"]["dispatch"], world["manifest"]["expected"]
    assert args.claude_executable == d["claude_executable"]
    assert args.codex_executable == d["codex_executable"]
    assert args.task_packet == d["task_packet_path"]
    assert args.config == d["config"]
    assert args.model_selection == d["model_selection"]
    assert args.manifest == d["controller_manifest"]
    assert args.worktree == e["worktree"] and args.repo == e["worktree"]
    assert args.branch == e["branch"]
    assert args.max_turns == 12 and isinstance(args.max_turns, int)
    assert args.unit_timeout == 900.0 and isinstance(args.unit_timeout, float)
    # --mode is typed by the operator and VERIFIED by the manifest, never supplied by it.
    assert args.mode == "shadow" and e["mode"] == "supervised"
    assert getattr(args, mlp.LOADED_ATTR) is manifest


def test_fills_leave_no_dispatch_input_missing(world):
    from tools.agent_supervisor.start_gate import dispatch_inputs_missing
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]))
    assert dispatch_inputs_missing(args), "sanity: nothing typed -> inputs missing before apply"
    mlp.apply_launch_manifest(args)
    assert dispatch_inputs_missing(args) == []


def test_bound_fill_defaults_match_the_live_parser():
    """Drift guard: a changed `start` default would silently turn every typed bound into a conflict."""
    args = _parse("--mode", "shadow")
    for attr, _key, default in mlp.BOUND_FILLS:
        assert getattr(args, attr) == default and type(getattr(args, attr)) is type(default), attr


def test_typed_flag_equal_to_manifest_is_accepted(world):
    d = world["manifest"]["dispatch"]
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]),
                  "--claude-executable", d["claude_executable"].upper().replace("\\", "/"),
                  "--branch", world["manifest"]["expected"]["branch"],
                  "--max-turns", "12", "--unit-timeout", "900")
    _manifest, refusal = mlp.apply_launch_manifest(args)
    if os.name == "nt":
        assert refusal is None, "path case/separator differences are not a disagreement on Windows"
    else:
        assert refusal is not None and refusal.reason_code == "launch_manifest_conflict"


def test_every_typed_disagreement_is_listed_in_one_refusal(world):
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]),
                  "--claude-executable", str(world["tmp"] / "other-claude.exe"),
                  "--config", str(world["tmp"] / "other-config.json"),
                  "--branch", "main", "--max-turns", "7", "--unit-timeout", "30")
    manifest, refusal = mlp.apply_launch_manifest(args)
    assert manifest is None and refusal is not None
    assert refusal.outcome == refusals.UNSAFE and refusal.exit_code == UNSAFE_EXIT
    assert refusal.reason_code == "launch_manifest_conflict"
    for flag in ("--claude-executable", "--config", "--branch", "--max-turns", "--unit-timeout"):
        assert flag in refusal.message, f"{flag} conflict must be reported, not just the first"
    assert not hasattr(args, mlp.LOADED_ATTR)


@pytest.mark.parametrize("attr", ["claude_executable", "codex_executable", "task_packet", "config",
                                  "model_selection", "manifest", "worktree", "repo"])
def test_each_path_input_conflict_refuses(world, attr):
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]))
    setattr(args, attr, str(world["tmp"] / "elsewhere"))
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is not None and refusal.reason_code == "launch_manifest_conflict"
    assert f"--{attr.replace('_', '-')}=" in refusal.message


@pytest.mark.parametrize("argv", [("--max-turns", "5"), ("--unit-timeout", "5")])
def test_typed_bound_neither_default_nor_manifest_conflicts(world, argv):
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]), *argv)
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is not None and refusal.reason_code == "launch_manifest_conflict"
    assert argv[0] in refusal.message


def test_manifest_bounds_override_parser_defaults(world):
    world["manifest"]["dispatch"]["max_turns"] = 9
    world["manifest"]["dispatch"]["unit_timeout_seconds"] = 120
    _write(world)
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]))
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is None
    assert args.max_turns == 9 and args.unit_timeout == 120.0 and isinstance(args.unit_timeout, float)


def test_invalid_manifest_is_a_typed_refusal(world):
    world["manifest_path"].write_text("{broken", encoding="utf-8")
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]))
    manifest, refusal = mlp.apply_launch_manifest(args)
    assert manifest is None and refusal is not None
    assert refusal.reason_code == "launch_manifest_invalid" and refusal.exit_code == UNSAFE_EXIT
    assert refusal.detail["launch_manifest"] == str(world["manifest_path"])


def test_missing_manifest_file_is_a_typed_refusal(world):
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["tmp"] / "absent.json"))
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is not None and refusal.reason_code == "launch_manifest_invalid"


def test_relative_manifest_path_is_refused(world):
    args = _parse("--mode", "supervised", "--launch-manifest", "launch.json")
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is not None and refusal.reason_code == "launch_manifest_invalid"
    assert "absolute" in refusal.message


@pytest.mark.parametrize("argv", [("--max-tasks", "2"), ("--packet-queue", "queue.json"),
                                  ("--max-tasks", "3", "--packet-queue", "queue.json")])
def test_multi_task_launch_is_refused_with_a_manifest(world, argv):
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]), *argv)
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is not None and refusal.reason_code == "launch_manifest_single_task"
    assert refusal.exit_code == UNSAFE_EXIT


def test_single_task_defaults_are_accepted(world):
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]), "--max-tasks", "1")
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is None


# ---------------------------------------------------------------- preflight_launch

@pytest.fixture
def applied(world):
    _hermetic(world)
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]))
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is None
    audit = FakeAudit(world["tmp"] / "runtime" / "audit.jsonl")
    return args, audit


def test_preflight_verifies_records_and_builds_the_restricted_profile(world, applied):
    args, audit = applied
    pf = mlp.preflight_launch(args, run_id="run-1", audit=audit, run_git=world["git"])
    assert pf.verification.ok and pf.verification.mismatches == ()
    assert pf.run_dir == world["tmp"] / "runtime" / "mrl" / "run-1"
    assert pf.ledger_path == pf.run_dir / "subagent_ledger.json"
    record = json.loads((pf.run_dir / "launch_verification.json").read_text(encoding="utf-8"))
    assert record["schema"] == "mrl_launch_verification/v1" and record["ok"] is True
    assert record["run_id"] == "run-1" and record["manifest"] == str(world["manifest_path"])
    assert [c["field"] for c in record["checks"]] == list(mlm.EXPECTED_FIELDS)
    assert audit.names() == ["launch_manifest_verified"]
    verified = audit.events[0]
    assert verified["run_id"] == "run-1" and verified["policy_result"] == "VERIFIED"
    assert verified["detail"]["head_sha"] == HEAD
    assert verified["detail"]["settings_profile_sha256"] == pf.profile.identity_sha256
    assert verified["detail"]["fields"] == list(mlm.EXPECTED_FIELDS)
    # The profile the child will really use: restricted, dontAsk, on the manifest's model.
    flags = pf.profile.argv_flags
    assert "--restricted" in flags and "dontAsk" in flags and "--strict-mcp-config" in flags
    assert pathlib.Path(pf.profile.profile_path).parent == pf.run_dir / "profile"
    assert pathlib.Path(pf.profile.profile_path).is_file()
    assert pf.profile.settings["mrl"]["run_id"] == "run-1"
    assert pf.profile.settings["mrl"]["task_id"] == "M0-T136"


def test_preflight_observes_only_it_never_trusts_the_manifest(world, applied):
    args, audit = applied
    git: FakeGit = world["git"]
    mlp.preflight_launch(args, run_id="run-1", audit=audit, run_git=git)
    observed = {("rev-parse", "HEAD"), ("rev-parse", "HEAD^{tree}"), ("rev-parse", "--abbrev-ref", "HEAD"),
                ("status", "--porcelain", "--untracked-files=all"), ("remote", "get-url", "origin"),
                ("rev-parse", "--show-toplevel"), ("rev-parse", "--path-format=absolute", "--git-common-dir")}
    assert observed <= set(git.calls), "every git-backed field must be re-observed at PREFLIGHT"


@pytest.mark.parametrize("perturb", [
    ("head", lambda w: w["git"].answers.__setitem__(("rev-parse", "HEAD"), "f" * 40 + "\n")),
    ("tree", lambda w: w["git"].answers.__setitem__(("rev-parse", "HEAD^{tree}"), "e" * 40 + "\n")),
    ("branch", lambda w: w["git"].answers.__setitem__(("rev-parse", "--abbrev-ref", "HEAD"), "main\n")),
    ("dirty", lambda w: w["git"].answers.__setitem__(("status", "--porcelain", "--untracked-files=all"),
                                                     "?? stray.txt\n")),
    ("origin", lambda w: w["git"].answers.__setitem__(("remote", "get-url", "origin"),
                                                      "https://github.com/someone-else/fork.git\n")),
    ("packet", lambda w: w["packet_path"].write_bytes(w["packet_path"].read_bytes() + b" ")),
    ("mode", lambda w: None),
])
def test_preflight_mismatch_is_a_typed_refusal_with_the_record(world, applied, perturb):
    args, audit = applied
    name, mutate = perturb
    mutate(world)
    if name == "mode":
        args.mode = "shadow"  # operator typed a mode the manifest did not authorize
    with pytest.raises(LoopError) as exc:
        mlp.preflight_launch(args, run_id="run-2", audit=audit, run_git=world["git"])
    assert exc.value.code == "launch_manifest_mismatch"
    assert "LAUNCH REFUSED before provider launch" in exc.value.message
    assert refusals.outcome_for_loop_refusal(exc.value.code) == refusals.UNSAFE
    assert audit.names() == ["launch_manifest_refused"]
    refused = audit.events[0]
    assert refused["policy_result"] == "REFUSED" and refused["detail"]["reason"] == "mismatch"
    assert refused["detail"]["mismatches"], "the audit row carries the disagreeing fields"
    record = json.loads((world["tmp"] / "runtime" / "mrl" / "run-2" / "launch_verification.json")
                        .read_text(encoding="utf-8"))
    assert record["ok"] is False
    assert any(not c["match"] for c in record["checks"])


def test_preflight_reports_all_mismatches_together(world, applied):
    args, audit = applied
    world["git"].answers[("rev-parse", "HEAD")] = "f" * 40 + "\n"
    world["git"].answers[("rev-parse", "--abbrev-ref", "HEAD")] = "main\n"
    args.mode = "shadow"
    with pytest.raises(LoopError) as exc:
        mlp.preflight_launch(args, run_id="run-3", audit=audit, run_git=world["git"])
    fields = {m["field"] for m in audit.events[0]["detail"]["mismatches"]}
    assert {"head_sha", "branch", "mode"} <= fields
    assert "3 field(s) disagree" in exc.value.message


def test_preflight_profile_drift_refuses(world, applied):
    """A changed subagent policy changes the profile identity, so the pinned identity refuses."""
    args, audit = applied
    manifest: mlm.LaunchManifest = getattr(args, mlp.LOADED_ATTR)
    manifest.dispatch["subagents"]["max_total"] = 40
    with pytest.raises(LoopError) as exc:
        mlp.preflight_launch(args, run_id="run-4", audit=audit, run_git=world["git"])
    assert exc.value.code == "launch_manifest_mismatch"
    assert [m["field"] for m in audit.events[0]["detail"]["mismatches"]] == ["settings_profile_sha256"]


def test_preflight_git_failure_is_unobservable_not_a_pass(world, applied):
    args, audit = applied

    def broken_git(argv, cwd):
        raise OSError("git vanished")

    with pytest.raises(LoopError) as exc:
        mlp.preflight_launch(args, run_id="run-5", audit=audit, run_git=broken_git)
    assert exc.value.code == "launch_manifest_unobservable"
    assert audit.names() == ["launch_manifest_refused"]
    assert audit.events[0]["detail"]["reason"] == "unobservable"
    assert not (world["tmp"] / "runtime" / "mrl" / "run-5" / "launch_verification.json").exists()


def test_preflight_without_applied_manifest_refuses(world):
    args = _parse("--mode", "supervised")
    audit = FakeAudit(world["tmp"] / "runtime" / "audit.jsonl")
    with pytest.raises(LoopError) as exc:
        mlp.preflight_launch(args, run_id="run-6", audit=audit, run_git=world["git"])
    assert exc.value.code == "launch_manifest_missing"
    assert audit.events == []


def test_preflight_profile_identity_is_the_real_profiles_identity(world, applied):
    """The identity compared is computed from the profile written for THIS run (not a stand-in)."""
    args, audit = applied
    pf = mlp.preflight_launch(args, run_id="run-7", audit=audit, run_git=world["git"])
    check = {c.field: c for c in pf.verification.checks}["settings_profile_sha256"]
    assert check.observed == pf.profile.identity_sha256 == check.expected


# ---------------------------------------------------------------- the REAL cmd_start

CONFIG_TOML = """
[codex]
allowed_models = ["codex-primary"]

[claude]
allowed_models = ["claude-worker"]

[controller]
default_mode = "shadow"

[limits]
max_review_packet_bytes = 262144
"""
SELECTION_TOML = """
[codex]
review_model = "codex-primary"
advisory_model = "codex-primary"
fallback_models = []

[claude]
model = "claude-worker"
fallback_models = []
"""
ORIGIN = "https://github.com/martin10101/nyc-buildability.git"


def _git(root: pathlib.Path, *argv: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "supervisor-test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "supervisor-test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}
    return subprocess.run(["git", *argv], cwd=str(root), check=True, capture_output=True,
                          text=True, env=env).stdout


@pytest.fixture
def live(tmp_path: pathlib.Path):
    """A real single-checkout fixture (as the legacy ContainmentGateTests use) plus a manifest for it."""
    from tools.agent_supervisor import cli
    from tools.agent_supervisor.manifest import generate_manifest, write_manifest

    tmp = tmp_path.resolve()
    repo = tmp / "repo"
    (repo / "tools").mkdir(parents=True)
    tasks = repo / "project-control" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "M0-T136.json").write_text(json.dumps({"task_id": "M0-T136", "status": "in_progress",
                                                    "blockers": []}), encoding="utf-8")
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture")  # a CLEAN tree: the ledger record is committed
    _git(repo, "remote", "add", "origin", ORIGIN)
    config = tmp / "config.toml"
    config.write_text(CONFIG_TOML, encoding="utf-8")
    selection = tmp / "model_selection.toml"
    selection.write_text(SELECTION_TOML, encoding="utf-8")
    packet = tmp / "M0-T136.json"
    packet.write_text(json.dumps({"task_id": "M0-T136", "allowed_paths": ["tools/agent_supervisor/**"],
                                  "forbidden_paths": [".github/**"], "status": "in_progress",
                                  "stop_conditions": ["no bypass flags"]}), encoding="utf-8")
    controller_manifest = write_manifest(
        generate_manifest(cli.PACKAGE_ROOT, extra_files=(("config.toml", config),)),
        tmp / "controller_manifest.json")
    draft = mlm.draft_manifest(str(repo), str(packet), mode="shadow")
    draft["dispatch"].update({
        "claude_executable": sys.executable, "claude_chain_sha256": "d" * 64,
        "claude_model": "claude-worker", "claude_runtime_model": "claude-worker", "claude_version": "2.1.252",
        "codex_executable": sys.executable, "codex_chain_sha256": "d" * 64,
        "codex_model": "codex-primary", "codex_version": "0.50.0",
        "config": str(config), "model_selection": str(selection),
        "controller_manifest": str(controller_manifest), "task_packet_path": str(packet),
        "managed_settings_path": "",
        "subagents": {"max_concurrent": 1, "max_total": 2, "agent_inventory": ["Explore"],
                      "tools_inventory": ["Read", "Grep", "Glob", "Agent"],
                      "allow_rules": ["Read", "Grep", "Glob"], "deny_rules": []},
    })
    manifest_path = tmp / "launch.json"
    live = {"tmp": tmp, "repo": repo, "runtime": tmp / "runtime", "manifest": draft,
            "manifest_path": manifest_path, "packet": packet}
    _rewrite_live(live, repin_identity=True)
    return live


def _rewrite_live(live, *, repin_identity: bool = False) -> None:
    """Write the manifest; optionally re-pin expected.settings_profile_sha256 to the profile
    the manifest's OWN dispatch section now produces (so a dispatch edit is tested on its own
    merits rather than through the identity it also changes)."""
    if repin_identity:
        live["manifest"]["expected"]["settings_profile_sha256"] = "0" * 64
        live["manifest_path"].write_text(json.dumps(live["manifest"]), encoding="utf-8")
        loaded = mlm.LaunchManifest.load(live["manifest_path"])
        scratch = live["tmp"] / "scratch"
        identity, _profile = mlm.observe_profile_identity(loaded, profile_dir=scratch,
                                                          ledger_path=scratch / "l.json")
        live["manifest"]["expected"]["settings_profile_sha256"] = identity
    live["manifest_path"].write_text(json.dumps(live["manifest"]), encoding="utf-8")


def _start(live, *extra: str) -> tuple[int, dict]:
    from tools.agent_supervisor import cli
    stdout = io.StringIO()
    argv = ["start", "--mode", "shadow", "--launch-manifest", str(live["manifest_path"]), *extra,
            "--checkout", str(live["repo"]), "--runtime-base", str(live["runtime"]), "--json"]
    with contextlib.redirect_stdout(stdout):
        code = cli.main(argv)
    return code, json.loads(stdout.getvalue())


@contextlib.contextmanager
def _job_object_host():
    from tools.agent_supervisor import cli
    from tools.agent_supervisor import process as proc
    original = cli.default_containment_kind
    cli.default_containment_kind = lambda: proc.CONTAINMENT_JOB_OBJECT  # type: ignore[assignment]
    try:
        yield
    finally:
        cli.default_containment_kind = original  # type: ignore[assignment]


@contextlib.contextmanager
def _spawn_spy():
    """Count worker spawns where the runner records them (the production accounting seam)."""
    from tools.agent_supervisor import claude_runner as cr
    spawned: list[int] = []
    real = cr.record_launched_child

    def spy(journal, *, pid, role, start_token=""):
        spawned.append(int(pid))
        real(journal, pid=pid, role=role, start_token=start_token)

    cr.record_launched_child = spy  # type: ignore[assignment]
    try:
        yield spawned
    finally:
        cr.record_launched_child = real  # type: ignore[assignment]


def _audit_events(live) -> list[str]:
    from tools.agent_supervisor.durable_state import runtime_dir_for
    path = runtime_dir_for(live["repo"], base=str(live["runtime"])) / "audit.jsonl"
    if not path.exists():
        return []
    return [json.loads(line)["event_type"] for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def test_cmd_start_refuses_an_invalid_manifest_before_the_runtime_opens(live):
    live["manifest_path"].write_text("{broken", encoding="utf-8")
    with _job_object_host(), _spawn_spy() as spawned:
        code, doc = _start(live)
    assert code == UNSAFE_EXIT
    assert doc["refused"] is True and doc["reason_code"] == "launch_manifest_invalid"
    assert not live["runtime"].exists(), "refused before the runtime/journal/lock were opened"
    assert spawned == []


def test_cmd_start_refuses_a_typed_conflict(live):
    with _job_object_host(), _spawn_spy() as spawned:
        code, doc = _start(live, "--branch", "not-main")
    assert code == UNSAFE_EXIT and doc["reason_code"] == "launch_manifest_conflict"
    assert spawned == [] and not live["runtime"].exists()


@pytest.mark.parametrize("field, value", [("head_sha", "f" * 40), ("tree_sha", "e" * 40), ("task_id", "M0-T999"),
                                          ("mode", "supervised"), ("task_packet_sha256", "1" * 64)])
def test_cmd_start_mismatch_refuses_at_preflight_with_no_worker_spawned(live, field, value):
    live["manifest"]["expected"][field] = value
    _rewrite_live(live)
    with _job_object_host(), _spawn_spy() as spawned:
        code, doc = _start(live)
    assert code == UNSAFE_EXIT, doc.get("stopped_because")
    assert doc["refusal"]["reason_code"] == "launch_manifest_mismatch"
    assert doc["dispatched"] is False and doc["provider_calls_made"] == 0
    assert field in doc["refusal"]["message"]
    assert spawned == [], "a mismatch must refuse BEFORE any provider launch"
    events = _audit_events(live)
    assert "launch_manifest_refused" in events and "launch_manifest_verified" not in events
    run_dirs = list((live["runtime"]).rglob("launch_verification.json"))
    assert len(run_dirs) == 1 and json.loads(run_dirs[0].read_text(encoding="utf-8"))["ok"] is False


def test_cmd_start_dirty_tree_refuses(live):
    (live["repo"] / "stray.txt").write_text("x", encoding="utf-8")
    with _job_object_host(), _spawn_spy() as spawned:
        code, doc = _start(live)
    assert code == UNSAFE_EXIT and doc["refusal"]["reason_code"] == "launch_manifest_mismatch"
    assert "clean_status" in doc["refusal"]["message"] and spawned == []


def test_cmd_start_branch_mismatch_refuses_before_any_launch(live):
    """The manifest's branch is what `--branch` becomes, so a wrong branch is refused by
    the legacy live branch probe before PREFLIGHT ever runs - a refusal either way, and
    never a spawn. (Which gate answers first is not the contract; NO launch is.)"""
    live["manifest"]["expected"]["branch"] = "release"
    _rewrite_live(live)
    with _job_object_host(), _spawn_spy() as spawned:
        code, doc = _start(live)
    assert code != 0 and doc["refused"] is True and doc["dispatched"] is False
    assert spawned == [] and "launch_manifest_verified" not in _audit_events(live)


def test_cmd_start_verified_manifest_dispatches_from_the_manifest_alone(live):
    """Only --mode and --launch-manifest typed: the manifest supplied every dispatch input,
    PREFLIGHT verified it, and the loop dispatched (sys.executable is not a real worker, so the
    cycle ends in the honest no_valid_checkpoint stop - what C-B1 requires is that the launch
    was verified and RAN)."""
    with _job_object_host(), _spawn_spy() as spawned:
        code, doc = _start(live)
    assert code == 0, doc.get("stopped_because")
    assert doc["dispatched"] is True
    assert doc["missing_inputs"] == []
    assert doc["stopped_because"] == "no_valid_checkpoint"
    assert len(spawned) == 1
    events = _audit_events(live)
    assert "launch_manifest_verified" in events and "launch_manifest_refused" not in events
    records = list(live["runtime"].rglob("launch_verification.json"))
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8"))
    assert record["ok"] is True and record["observed"]["task_id"] == "M0-T136"
    assert record["observed"]["branch"] == "main"
    assert (records[0].parent / "profile" / "mrl_settings_profile.json").is_file()


def test_cmd_start_claude_model_disagreeing_with_selection_refuses(live):
    """dispatch.claude_model is cross-checked against the model the loop will really launch
    (the pinned selection); the identity is re-pinned so THIS check, not the profile identity,
    is what refuses."""
    live["manifest"]["dispatch"]["claude_model"] = "claude-other"
    _rewrite_live(live, repin_identity=True)
    with _job_object_host(), _spawn_spy() as spawned:
        code, doc = _start(live)
    assert code == UNSAFE_EXIT and doc["refusal"]["reason_code"] == "launch_manifest_mismatch"
    assert "dispatch.claude_model" in doc["refusal"]["message"] and spawned == []
