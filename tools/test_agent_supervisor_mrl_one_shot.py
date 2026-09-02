"""Paired tests for the MRL one-shot worker runner (M0-T136 C-B4; D-024-R580..R584, R589).

No live provider is ever launched: the runner's seams (``popen``, ``container_factory``,
``snapshot``, ``run_version``, ``git``) are injected fakes, so every contract is proven
against the recorded argv/env/stdin/termination facts, and every positive contract has
a negative or mutation twin:

* one fresh process, one prompt, one schema-bound result, stdin written once and
  closed, no resume/continue flag, no second dispatch, no extra turn (R581);
* total run accounting closes over the primary and every subagent id the ledger issued
  (R582); a live or over-limit subagent fails the unit;
* process/turn limits travel on the argv and into the unit record (R583);
* timeout/cancel terminate the tree and the descendant-zero proof is taken from a real
  (or injected) process table - an unproven tree is reported, never assumed (R584).

The harness (``Harness``/``make_launch``/``make_runner``) is shared with
``test_agent_supervisor_mrl_one_shot_review.py``.
"""
from __future__ import annotations

import functools
import inspect
import json
import os
import pathlib
import subprocess
import sys
import threading

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor import mrl_descendants as md  # noqa: E402
from tools.agent_supervisor import mrl_exec_chain as mec  # noqa: E402
from tools.agent_supervisor import mrl_launch_path as mlp  # noqa: E402
from tools.agent_supervisor import mrl_one_shot as mos  # noqa: E402
from tools.agent_supervisor.claude_runner import WORKER_CHILD_ROLE, RunnerConfig  # noqa: E402
from tools.agent_supervisor.models import digest_of  # noqa: E402
from tools.agent_supervisor.mrl_subagent_contract import SubagentLedger  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import load_schema  # noqa: E402
from tools.agent_supervisor.process import ContainmentReport, minimal_env  # noqa: E402
from tools.agent_supervisor.recovery import CHILD_PROCESSES_KEY  # noqa: E402
from tools.agent_supervisor.recovery_probes import GitResult  # noqa: E402
from tools.test_agent_supervisor_mrl_launch_manifest import HEAD, build_world  # noqa: E402
from tools.test_agent_supervisor_mrl_launch_path import FakeAudit, _hermetic, _parse  # noqa: E402

NEW_HEAD = "9" * 40
PROMPT = "Do the bounded M0-T136 task."
PAYLOAD = {"outcome": "COMPLETED", "summary": "did the thing", "requested_next_action": "review"}
CLAUDE_VERSION_TEXT = "2.1.252 (Claude Code)"


# ---------------------------------------------------------------- harness

def git_seam(world):
    """``measure_git_state`` needs GitResult objects; the world's FakeGit returns strings."""
    return lambda argv, cwd: GitResult(returncode=0, stdout=world["git"](argv, cwd), stderr="", ran=True)


def result_object(payload=PAYLOAD, *, carrier="structured_output", session_id="sess-1",
                  models=("claude-opus-4-8",), is_error=False, **extra):
    obj = {"type": "result", "subtype": "success", "is_error": is_error,
           "modelUsage": {m: {"inputTokens": 10, "outputTokens": 5} for m in models},
           "usage": {"input_tokens": 10, "output_tokens": 5}}
    if session_id is not None:
        obj["session_id"] = session_id
    if carrier == "structured_output":
        obj["structured_output"] = payload
        obj["result"] = "done"
    elif carrier == "result_text":
        obj["result"] = json.dumps(payload) if not isinstance(payload, str) else payload
    obj.update(extra)
    return obj


class FakeProcess:
    """A Popen-like handle: records what it was given; ends on communicate() or terminate()."""

    def __init__(self, harness, pid, argv, kwargs):
        self.harness = harness
        self.pid = pid
        self.args = list(argv)
        self.kwargs = kwargs
        self.returncode = None
        self.stdin = self.stdout = self.stderr = None
        self.stdin_text = None
        self.communicate_calls = 0
        self.terminated = False
        self._ended = threading.Event()

    def communicate(self, input=None, timeout=None):
        self.communicate_calls += 1
        if input is not None:
            self.stdin_text = input
            if self.harness.on_spawn is not None:
                self.harness.on_spawn(self)
        if self.harness.block:
            if not self._ended.wait(timeout):
                raise subprocess.TimeoutExpired(self.args, timeout)
            return "", ""
        self._end(self.harness.returncode)
        return self.harness.reply, self.harness.stderr

    def _end(self, code):
        if self.returncode is None:
            self.returncode = code
        self._ended.set()

    def poll(self):
        return self.returncode

    def wait(self, timeout=None):
        self._ended.wait(timeout)
        return self.returncode

    def terminate(self):
        self.terminated = True
        self._end(-9)

    kill = terminate


class FakeContainer:
    def __init__(self, harness, *, prefer_job_object):
        self.harness = harness
        self.prefer_job_object = prefer_job_object
        self.pids: list[int] = []
        self.closed = False
        self.terminate_calls = 0

    def adopt(self, pid):
        self.pids.append(int(pid))

    def report(self):
        return ContainmentReport(kind="job_object", job_object_used=True, adopted_pids=tuple(self.pids),
                                 verified_in_job=True)

    def close(self):
        self.closed = True

    def terminate_all(self):
        self.terminate_calls += 1
        for pid in self.pids:
            self.harness.processes[pid].terminate()


class Harness:
    """Everything a test controls about the (never real) child process."""

    def __init__(self, reply=None, *, returncode=0, stderr="", block=False, spawn_error=None, on_spawn=None):
        self.reply = json.dumps(result_object()) if reply is None else reply
        self.returncode = returncode
        self.stderr = stderr
        self.block = block
        self.spawn_error = spawn_error
        self.on_spawn = on_spawn
        self.processes: dict[int, FakeProcess] = {}
        self.popen_calls: list[tuple[list[str], dict]] = []
        self.containers: list[FakeContainer] = []
        self.version_calls: list[list[str]] = []
        self._next_pid = 4242

    def popen(self, argv, **kwargs):
        self.popen_calls.append((list(argv), kwargs))
        if self.spawn_error is not None:
            raise self.spawn_error
        process = FakeProcess(self, self._next_pid, argv, kwargs)
        self.processes[process.pid] = process
        self._next_pid += 1
        return process

    def container_factory(self, *, prefer_job_object):
        container = FakeContainer(self, prefer_job_object=prefer_job_object)
        self.containers.append(container)
        return container

    def run_version(self, argv):
        self.version_calls.append(list(argv))
        return 0, CLAUDE_VERSION_TEXT, ""

    @property
    def process(self) -> FakeProcess:
        assert len(self.processes) == 1, f"expected exactly one spawned process, got {len(self.processes)}"
        return next(iter(self.processes.values()))


class FakeJournal:
    def __init__(self):
        self.state: dict = {}

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    def set_state(self, key, value):
        self.state[key] = value


def make_launch(tmp_path, run_id="run-1"):
    """A verified launch bound to real fake executables (chains hashed from the files on disk)."""
    world = build_world(tmp_path)
    bin_dir = tmp_path / "bin"
    codex_exe = bin_dir / "codex.exe"
    codex_exe.write_text("codex", encoding="utf-8")
    dispatch = world["manifest"]["dispatch"]
    claude_exe = bin_dir / "claude.exe"
    dispatch["claude_chain_sha256"] = mec.bind_chain_now(mec.resolve_chain(str(claude_exe), "claude")).combined_sha256
    dispatch["codex_executable"] = str(codex_exe)
    dispatch["codex_chain_sha256"] = mec.bind_chain_now(mec.resolve_chain(str(codex_exe), "codex")).combined_sha256
    _hermetic(world)
    args = _parse("--mode", "supervised", "--launch-manifest", str(world["manifest_path"]))
    _m, refusal = mlp.apply_launch_manifest(args)
    assert refusal is None
    audit = FakeAudit(tmp_path / "runtime" / "audit.jsonl")
    pf = mlp.preflight_launch(args, run_id=run_id, audit=audit, run_git=world["git"])
    return {"world": world, "pf": pf, "audit": audit, "claude_exe": claude_exe, "codex_exe": codex_exe,
            "run_id": run_id}


def make_runner(launch, harness, *, journal=None, snapshot=None, run_version=None, **cfg):
    world = launch["world"]
    config = dict(executable=str(launch["claude_exe"]), cwd=str(world["worktree"]),
                  expected_worktree=str(world["worktree"]), primary_checkout=str(world["repo_root"]),
                  model="claude-opus-4-8", max_turns=12, timeout_seconds=30.0)
    config.update(cfg)
    return mos.OneShotRunner(
        RunnerConfig(**config), launch=launch["pf"], audit=launch["audit"], run_id=launch["run_id"],
        journal=journal, git=git_seam(world), popen=harness.popen,
        run_version=run_version or harness.run_version, snapshot=snapshot or (lambda: {}),
        container_factory=harness.container_factory)


def unit_record(launch):
    return json.loads((launch["pf"].run_dir / mos.UNIT_RECORD_NAME).read_text(encoding="utf-8"))


@pytest.fixture
def launch(tmp_path):
    return make_launch(tmp_path)


@pytest.fixture
def fast_proof(monkeypatch):
    """Descendant proofs settle instantly (the settle window itself is unit-tested below)."""
    monkeypatch.setattr(mos, "prove_zero_descendants",
                        functools.partial(md.prove_zero_descendants, settle_seconds=0.0, sleep=lambda _s: None))


# ---------------------------------------------------------------- the happy path (R580, R581, R583)

def test_one_fresh_process_one_prompt_one_schema_bound_result(launch):
    harness = Harness()
    runner = make_runner(launch, harness)
    result = runner.run_unit(PROMPT)
    assert result.ok, result.checkpoint_error
    assert result.returncode == 0 and result.result_source == "structured_output"
    # exactly one process, spawned once, written once, stdin closed by communicate()
    assert len(harness.popen_calls) == 1
    process = harness.process
    assert process.communicate_calls == 1
    assert process.stdin_text == PROMPT + mos.RESULT_CONTRACT
    assert "Do not report ids, SHAs, branches" in process.stdin_text
    # the argv: -p / json output / bounded turns / pinned model / schema / restricted profile
    argv = list(result.argv)
    assert argv == process.args
    assert argv[0] == str(launch["claude_exe"])
    assert argv[1:5] == ["-p", "--output-format", "json", "--max-turns"]
    assert argv[5] == "12" and argv[6:8] == ["--model", "claude-opus-4-8"]
    schema_at = argv.index("--json-schema")
    assert json.loads(argv[schema_at + 1]) == load_schema("worker_result.schema.json")
    assert schema_at < argv.index("--restricted"), "schema precedes the profile flags"
    assert "--permission-mode" in argv and "dontAsk" in argv and "--strict-mcp-config" in argv
    lowered = {a.lower() for a in argv}
    assert not lowered & {"--resume", "--continue", "-r", "-c", "--fork-session", "--bg", "--background"}
    # popen: no shell, the manifest worktree, the forced updater-disabled env, piped stdin
    kwargs = process.kwargs
    assert kwargs["shell"] is False and kwargs["cwd"] == str(launch["world"]["worktree"])
    assert kwargs["stdin"] is subprocess.PIPE and kwargs["text"] is True
    assert kwargs["env"]["DISABLE_AUTOUPDATER"] == "1" and "DISABLE_UPDATES" not in kwargs["env"]
    # the version was observed from the same executable the chain bound
    assert harness.version_calls == [[str(launch["claude_exe"]), "--version"]]
    # the checkpoint is controller-authored: ids, shas, branch, worktree all observed
    cp = result.checkpoint
    assert cp.run_id == "run-1" and cp.checkpoint_id == "run-1.primary.cp1" and cp.task_id == "M0-T136"
    assert cp.claude_session_id == "sess-1" and cp.status == "UNIT_COMPLETE"
    assert cp.starting_sha == HEAD and cp.current_sha == HEAD
    assert cp.branch == "candidate/D-024-mrl-option-b"
    assert cp.summary == "did the thing" and cp.proposed_next_action == "review"
    assert result.worker_result == PAYLOAD
    assert result.checkpoint_original_digest == digest_of(PAYLOAD)
    # containment + proof + accounting
    assert result.containment == "job_object" and result.containment_verified_in_job is True
    assert result.tree_terminated is False and not result.timed_out and not result.cancelled
    assert result.descendant_proof["proven"] is True and result.descendant_proof["source"] == "injected"
    assert result.accounting["processes_total"] == 1 and result.accounting["closed"] is True
    assert result.observed_models == ("claude-opus-4-8",) and result.model_mismatch is False
    assert harness.containers[0].closed is True
    assert result.launch_record["max_turns"] == 12 and result.launch_record["version"] == "2.1.252"
    assert result.launch_record["starting_sha"] == HEAD
    assert result.launch_record["chain"]["combined_sha256"] == launch["pf"].manifest.dispatch["claude_chain_sha256"]


def test_happy_path_writes_the_unit_record_and_audit_rows(launch):
    harness = Harness()
    runner = make_runner(launch, harness)
    result = runner.run_unit(PROMPT)
    assert result.ok
    record = unit_record(launch)
    assert record["schema"] == "mrl_one_shot_unit/v1" and record["run_id"] == "run-1"
    assert record["ok"] is True and record["checkpoint"]["checkpoint_id"] == "run-1.primary.cp1"
    assert record["max_turns"] == 12 and record["launch"]["argv"] == list(result.argv)
    assert record["accounting"]["processes_total"] == 1 and record["accounting"]["subagents_live"] == 0
    assert record["descendant_proof"]["proven"] is True and record["model_mismatch"] is False
    assert record["session_id"] == "sess-1" and record["result_source"] == "structured_output"
    names = launch["audit"].names()
    assert names == ["launch_manifest_verified", "mrl_one_shot_launched", "mrl_one_shot_settled"]
    launched, settled = launch["audit"].events[1], launch["audit"].events[2]
    assert launched["executable_identity"]["digest"] == launch["pf"].manifest.dispatch["claude_chain_sha256"]
    assert launched["detail"]["chain"] == "claude" and launched["detail"]["argv"] == list(result.argv)
    assert settled["policy_result"] == "OK" and settled["checkpoint_id"] == "run-1.primary.cp1"
    assert settled["output_digest"] == digest_of(result.checkpoint.to_dict())
    assert settled["error_category"] == "" and settled["detail"]["accounting"]["closed"] is True
    ledger = json.loads(launch["pf"].ledger_path.read_text(encoding="utf-8"))
    assert ledger["closed"] is True and ledger["primary_id"] == "run-1.primary"
    assert runner.executable_identity()["digest"] == launch["pf"].manifest.dispatch["claude_chain_sha256"]


def test_result_text_carrier_is_accepted_and_recorded(launch):
    harness = Harness(json.dumps(result_object(carrier="result_text")))
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert result.ok, result.checkpoint_error
    assert result.result_source == "result_text" and result.worker_result == PAYLOAD
    assert unit_record(launch)["result_source"] == "result_text"


def test_result_text_that_is_not_json_fails_closed(launch):
    harness = Harness(json.dumps(result_object("I finished, trust me", carrier="result_text")))
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("contract_violation")
    assert result.result_source == "result_text" and result.checkpoint is None


def test_worker_commit_during_the_unit_is_observed_not_claimed(launch):
    def advance(process):
        launch["world"]["git"].answers[("rev-parse", "HEAD")] = NEW_HEAD + "\n"
    result = make_runner(launch, Harness(on_spawn=advance)).run_unit(PROMPT)
    assert result.ok
    assert result.checkpoint.starting_sha == HEAD and result.checkpoint.current_sha == NEW_HEAD


def test_preamble_line_is_counted_malformed_and_the_last_object_wins(launch):
    harness = Harness("warming up\n" + json.dumps(result_object()))
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert result.ok and result.stats.malformed_lines == 1


def test_max_turns_and_wall_clock_travel_from_config(launch):
    harness = Harness()
    result = make_runner(launch, harness, max_turns=3, timeout_seconds=7.5).run_unit(PROMPT)
    assert result.ok
    argv = list(result.argv)
    assert argv[argv.index("--max-turns") + 1] == "3"
    assert result.launch_record["max_turns"] == 3 and result.launch_record["wall_clock_seconds"] == 7.5
    assert unit_record(launch)["max_turns"] == 3


# ---------------------------------------------------------------- one-shot invariants (R581)

def test_second_dispatch_is_refused_without_a_spawn(launch):
    harness = Harness()
    runner = make_runner(launch, harness)
    assert runner.run_unit(PROMPT).ok
    second = runner.run_unit(PROMPT)
    assert not second.ok and second.checkpoint_error.startswith("one_shot_second_dispatch")
    assert len(harness.popen_calls) == 1
    assert launch["audit"].names()[-1] == "mrl_one_shot_refused"
    assert launch["audit"].events[-1]["error_category"] == "one_shot_second_dispatch"


def test_extra_turns_are_refused_before_any_spawn(launch):
    harness = Harness()
    result = make_runner(launch, harness).run_unit(PROMPT, extra_turns=("one more thing",))
    assert not result.ok and result.checkpoint_error.startswith("one_shot_extra_turns")
    assert harness.popen_calls == []


def test_transport_second_spawn_is_refused(launch):
    harness = Harness()
    runner = make_runner(launch, harness)
    spawn = mos._ContainedSpawn(runner, env=minimal_env({"DISABLE_AUTOUPDATER": "1"}), cancel_event=None)
    spawn([str(launch["claude_exe"]), "-p"], stdin_text="x", timeout=5.0)
    with pytest.raises(mos.ContractError) as exc:
        spawn([str(launch["claude_exe"]), "-p"], stdin_text="x", timeout=5.0)
    assert exc.value.code == "one_shot_second_spawn"


@pytest.mark.parametrize("cwd_is, code", [
    ("primary", "cwd_primary_checkout"),
    ("elsewhere", "cwd_mismatch"),
    ("", "cwd_unbound"),
])
def test_launch_seam_refuses_before_any_spawn(launch, cwd_is, code):
    harness = Harness()
    world = launch["world"]
    if cwd_is == "primary":
        cwd = str(world["repo_root"])
    elif cwd_is == "elsewhere":
        (world["tmp"] / "elsewhere").mkdir()
        cwd = str(world["tmp"] / "elsewhere")
    else:
        cwd = ""
    result = make_runner(launch, harness, cwd=cwd).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith(code)
    assert harness.popen_calls == [] and harness.version_calls == []


# ---------------------------------------------------------------- identity before the spawn (R562, R564, R511)

def test_executable_drift_after_preflight_is_refused_before_any_spawn(launch):
    harness = Harness()
    runner = make_runner(launch, harness)
    launch["claude_exe"].write_text("a different binary", encoding="utf-8")
    result = runner.run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("contract_violation")
    assert "R511" in result.checkpoint_error
    assert harness.popen_calls == [] and harness.version_calls == []
    identity = runner.executable_identity()
    assert identity["digest"] == "" and identity["error"]


@pytest.mark.parametrize("version", [(0, "2.1.250 (Claude Code)", ""), (1, "", "boom"), (0, "", "")])
def test_version_drift_is_refused_before_any_spawn(launch, version):
    harness = Harness()
    result = make_runner(launch, harness, run_version=lambda argv: version).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("claude_version_mismatch")
    assert harness.popen_calls == []


def test_restricted_profile_missing_is_refused_before_any_spawn(launch):
    harness = Harness()
    pathlib.Path(launch["pf"].profile.profile_path).unlink()
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("restricted_profile_missing")
    assert harness.popen_calls == []


@pytest.mark.parametrize("mutate, code", [
    (lambda w: w["git"].answers.__setitem__(("rev-parse", "--abbrev-ref", "HEAD"), "main\n"), "unexpected_branch"),
    (lambda w: w["git"].answers.__setitem__(("rev-parse", "--show-toplevel"), (w["tmp"] / "other").as_posix() + "\n"),
     "wrong_worktree"),
    (lambda w: w["git"].answers.__setitem__(("rev-parse", "--abbrev-ref", "HEAD"), "HEAD\n"), "ambiguous_branch"),
])
def test_git_binding_drift_before_the_spawn_is_refused(launch, mutate, code):
    harness = Harness()
    mutate(launch["world"])
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith(code)
    assert harness.popen_calls == []


def test_git_binding_drift_during_the_unit_fails_the_checkpoint(launch):
    def drift(process):
        launch["world"]["git"].answers[("rev-parse", "--abbrev-ref", "HEAD")] = "main\n"
    result = make_runner(launch, Harness(on_spawn=drift)).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("unexpected_branch")
    assert result.checkpoint is None and unit_record(launch)["ok"] is False


# ---------------------------------------------------------------- child environment (R280 updater rule)

def test_updater_pair_is_forced_even_against_a_conflicting_extra(launch):
    harness = Harness()
    result = make_runner(launch, harness, extra_env={"DISABLE_AUTOUPDATER": "0", "MRL_PROBE": "1"}).run_unit(PROMPT)
    assert result.ok
    env = harness.process.kwargs["env"]
    assert env["DISABLE_AUTOUPDATER"] == "1" and env["MRL_PROBE"] == "1"


def test_prohibited_disable_updates_is_refused_before_any_spawn(launch):
    harness = Harness()
    result = make_runner(launch, harness, extra_env={"DISABLE_UPDATES": "1"}).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("contract_violation")
    assert "DISABLE_UPDATES" in result.checkpoint_error and harness.popen_calls == []


def test_mutation_env_builder_without_the_forced_pair_is_caught_by_the_verifier(launch, monkeypatch):
    monkeypatch.setattr(mos, "claude_child_env", lambda extra, allowlist: minimal_env(extra, allowlist))
    harness = Harness()
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("contract_violation")
    assert "DISABLE_AUTOUPDATER" in result.checkpoint_error and harness.popen_calls == []


# ---------------------------------------------------------------- spawn / journal failures

def test_spawn_failure_is_a_typed_refusal_with_the_ledger_closed(launch):
    harness = Harness(spawn_error=OSError(2, "no such executable"))
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("spawn_failed")
    assert result.tree_terminated is False and result.descendant_proof == {}
    assert harness.containers[0].closed is True
    assert json.loads(launch["pf"].ledger_path.read_text(encoding="utf-8"))["closed"] is True
    assert launch["audit"].events[-1]["event"] == "mrl_one_shot_refused"
    assert launch["audit"].events[-1]["error_category"] == "spawn_failed"


def test_journal_records_the_child_and_clears_it_only_after_the_proof(launch):
    journal = FakeJournal()
    seen: list = []
    harness = Harness(on_spawn=lambda p: seen.append(list(journal.get_state(CHILD_PROCESSES_KEY, []))))
    result = make_runner(launch, harness, journal=journal).run_unit(PROMPT)
    assert result.ok
    assert seen and seen[0][0]["pid"] == harness.process.pid and seen[0][0]["role"] == WORKER_CHILD_ROLE
    assert not journal.get_state(CHILD_PROCESSES_KEY)


def test_unjournalable_child_is_terminated_and_refused(launch, monkeypatch):
    def broken(journal, *, pid, role, start_token=""):
        raise RuntimeError("disk full")
    monkeypatch.setattr(mos, "record_launched_child", broken)
    harness = Harness()
    result = make_runner(launch, harness, journal=FakeJournal()).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("child_record_unwritable")
    assert harness.process.terminated is True and result.tree_terminated is True
    assert result.descendant_proof["proven"] is True
    assert harness.containers[0].terminate_calls == 1 and harness.containers[0].closed is True
    assert json.loads(launch["pf"].ledger_path.read_text(encoding="utf-8"))["closed"] is True


# ---------------------------------------------------------------- settlement refusals

@pytest.mark.parametrize("harness_kw, code", [
    ({"reply": "not json at all"}, "malformed_output"),
    ({"reply": ""}, "malformed_output"),
    ({"reply": json.dumps([1, 2])}, "malformed_output"),
    ({"returncode": 1}, "worker_failed"),
    ({"reply": json.dumps(result_object(is_error=True))}, "worker_failed"),
    ({"reply": json.dumps(result_object(session_id=None))}, "session_id_missing"),
    ({"reply": json.dumps(result_object({**PAYLOAD, "current_sha": HEAD}))}, "contract_violation"),
    ({"reply": json.dumps(result_object({"outcome": "DONE", "summary": "x", "requested_next_action": ""}))},
     "contract_violation"),
    ({"reply": json.dumps({"type": "result", "is_error": False, "session_id": "s", "result": "x"})},
     "contract_violation"),
])
def test_settlement_refuses_every_non_conforming_result(launch, harness_kw, code):
    result = make_runner(launch, Harness(**harness_kw)).run_unit(PROMPT)
    assert not result.ok and result.checkpoint is None
    assert result.checkpoint_error.startswith(code), result.checkpoint_error
    record = unit_record(launch)
    assert record["ok"] is False and record["checkpoint_error"] == result.checkpoint_error
    assert launch["audit"].events[-1]["event"] == "mrl_one_shot_settled"
    assert launch["audit"].events[-1]["policy_result"] == "REFUSED"
    assert launch["audit"].events[-1]["error_category"] == code


def test_runtime_model_other_than_pinned_is_a_detected_mismatch(launch):
    harness = Harness(json.dumps(result_object(models=("claude-sonnet-4-5",))))
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("contract_violation")
    assert "claude-sonnet-4-5" in result.checkpoint_error and "R511" in result.checkpoint_error
    assert result.model_mismatch is True and result.observed_models == ("claude-sonnet-4-5",)
    assert unit_record(launch)["model_mismatch"] is True


def test_two_runtime_models_fail_closed_as_no_single_identity(launch):
    harness = Harness(json.dumps(result_object(models=("claude-opus-4-8", "claude-haiku-4-5"))))
    result = make_runner(launch, harness).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("contract_violation")
    assert "no model" in result.checkpoint_error and result.model_mismatch is True


def test_no_runtime_model_reported_fails_closed(launch):
    obj = result_object()
    del obj["modelUsage"]
    result = make_runner(launch, Harness(json.dumps(obj))).run_unit(PROMPT)
    assert not result.ok and "no model" in result.checkpoint_error


# ---------------------------------------------------------------- total run accounting (R582)

def _request(launch, **kw):
    ledger = SubagentLedger(launch["pf"].ledger_path)
    kw.setdefault("parent_id", "run-1.primary")
    kw.setdefault("subagent_type", "Explore")
    kw.setdefault("description", "probe")
    kw.setdefault("depth", 1)
    kw.setdefault("background", False)
    return ledger, ledger.request(**kw)


def test_released_subagents_are_accounted_and_the_unit_passes(launch):
    def fan_out(process):
        ledger, first = _request(launch)
        ledger2, second = _request(launch)
        assert first.allowed and second.allowed
        ledger.release(first.child_id, status="ok")
        ledger2.release(second.child_id, status="ok")
        _ledger, third = _request(launch, background=True)
        assert not third.allowed and "background" in third.reason
    result = make_runner(launch, Harness(on_spawn=fan_out)).run_unit(PROMPT)
    assert result.ok, result.checkpoint_error
    acc = result.accounting
    assert acc["processes_total"] == 3 and acc["subagents_issued"] == 2 and acc["subagents_live"] == 0
    assert acc["subagents_denied"] == 1 and acc["unreleased_child_ids"] == [] and acc["closed"] is True
    assert unit_record(launch)["accounting"] == acc


def test_over_limit_fan_out_is_denied_and_recorded(launch):
    def fan_out(process):
        for _n in range(4):
            ledger, decision = _request(launch)
            assert decision.allowed
            ledger.release(decision.child_id, status="ok")
        _ledger, fifth = _request(launch)
        assert not fifth.allowed and "total limit 4" in fifth.reason
    result = make_runner(launch, Harness(on_spawn=fan_out)).run_unit(PROMPT)
    assert result.ok
    assert result.accounting["subagents_issued"] == 4 and result.accounting["subagents_denied"] == 1
    assert result.accounting["processes_total"] == 5


def test_a_live_subagent_at_settlement_fails_the_unit(launch):
    def leak(process):
        _ledger, decision = _request(launch)
        assert decision.allowed
    result = make_runner(launch, Harness(on_spawn=leak)).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("subagent_accounting_violation")
    assert result.accounting["subagents_live"] == 1
    assert result.accounting["unreleased_child_ids"] == ["run-1.primary.c001"]
    assert result.accounting["closed"] is True


def test_the_ledger_is_closed_after_the_unit_so_late_requests_are_denied(launch):
    assert make_runner(launch, Harness()).run_unit(PROMPT).ok
    _ledger, late = _request(launch)
    assert not late.allowed and "closed" in late.reason


# ---------------------------------------------------------------- termination + descendant proof (R584)

def test_timeout_terminates_the_tree_and_proves_it_empty(launch):
    harness = Harness(block=True)
    result = make_runner(launch, harness, timeout_seconds=0.2).run_unit(PROMPT)
    assert not result.ok and result.checkpoint_error.startswith("terminated")
    assert "timeout" in result.checkpoint_error
    assert result.timed_out is True and result.tree_terminated is True and result.cancelled is False
    assert harness.process.terminated is True and harness.containers[0].terminate_calls >= 1
    assert result.descendant_proof["proven"] is True and result.containment == "job_object"
    record = unit_record(launch)
    assert record["timed_out"] is True and record["tree_terminated"] is True and record["ok"] is False
    assert launch["audit"].events[-1]["detail"]["timed_out"] is True


def test_cancellation_terminates_the_tree(launch):
    cancel = threading.Event()
    cancel.set()
    harness = Harness(block=True)
    result = make_runner(launch, harness, timeout_seconds=30.0).run_unit(PROMPT, cancel_event=cancel)
    assert not result.ok and result.checkpoint_error.startswith("terminated")
    assert "cancelled" in result.checkpoint_error
    assert result.cancelled is True and result.tree_terminated is True and harness.process.terminated is True
    assert result.descendant_proof["proven"] is True


def test_unproven_descendants_are_reported_never_assumed(launch, fast_proof):
    journal = FakeJournal()
    harness = Harness()
    table: dict = {}

    def snapshot():
        return dict(table)

    def leave_a_grandchild(process):
        table.update({process.pid: 1, 999999: process.pid})
    harness.on_spawn = leave_a_grandchild
    result = make_runner(launch, harness, journal=journal, snapshot=snapshot).run_unit(PROMPT)
    assert result.ok is True, "the unit itself was fine; the containment fact is what degrades"
    assert result.containment == mos.CONTAINMENT_DESCENDANTS_REMAINING
    assert result.descendant_proof["proven"] is False
    assert list(result.descendant_proof["remaining"]) == [harness.process.pid, 999999]
    assert "999999" in result.containment_fallback_reason
    # the journal keeps the record: the next start classifies the leftover instead of launching over it
    assert journal.get_state(CHILD_PROCESSES_KEY)[0]["pid"] == harness.process.pid
    record = unit_record(launch)
    assert record["containment"] == mos.CONTAINMENT_DESCENDANTS_REMAINING
    assert record["descendant_proof"]["remaining"] == [harness.process.pid, 999999]


def test_unobservable_process_table_is_not_a_proof(launch, fast_proof):
    def unavailable():
        raise OSError("snapshot failed")
    result = make_runner(launch, Harness(), snapshot=unavailable).run_unit(PROMPT)
    assert result.containment == mos.CONTAINMENT_DESCENDANTS_REMAINING
    assert result.descendant_proof["proven"] is False and result.descendant_proof["source"] == "unavailable"


# ---------------------------------------------------------------- mrl_descendants

def test_descendants_of_walks_the_whole_tree_and_skips_self_parents():
    table = {0: 0, 4: 0, 1: 4, 10: 1, 11: 10, 12: 11, 20: 1, 30: 20}
    assert md.descendants_of(10, table) == (10, 11, 12)
    assert md.descendants_of(1, table) == (1, 10, 11, 12, 20, 30)
    assert md.descendants_of(0, table) == (0, 1, 4, 10, 11, 12, 20, 30)
    assert md.descendants_of(777, table) == ()


def test_descendants_of_finds_an_orphan_whose_parent_already_exited():
    assert md.descendants_of(500, {600: 500, 601: 600}) == (600, 601)


def test_prove_zero_descendants_waits_for_the_settle_window():
    tables = iter([{7: 1, 8: 7}, {8: 7}, {}])
    clock = {"t": 0.0}
    proof = md.prove_zero_descendants(7, snapshot=lambda: next(tables), settle_seconds=1.0,
                                      now=lambda: clock["t"], sleep=lambda s: clock.__setitem__("t", clock["t"] + s))
    assert proof.proven is True and proof.attempts == 3 and proof.remaining == () and proof.source == "injected"
    assert proof.to_dict()["root_pid"] == 7


def test_prove_zero_descendants_gives_up_after_the_window_with_the_remaining_pids():
    clock = {"t": 0.0}
    proof = md.prove_zero_descendants(7, snapshot=lambda: {7: 1, 8: 7}, settle_seconds=0.5, poll_seconds=0.2,
                                      now=lambda: clock["t"], sleep=lambda s: clock.__setitem__("t", clock["t"] + s))
    assert proof.proven is False and proof.remaining == (7, 8) and proof.attempts == 4
    assert proof.elapsed_seconds >= 0.5


def test_prove_zero_descendants_reports_an_unobservable_table():
    def broken():
        raise OSError("no table")
    proof = md.prove_zero_descendants(7, snapshot=broken)
    assert proof.proven is False and proof.source == "unavailable" and proof.remaining == (7,)


def test_real_process_table_sees_this_interpreter_alive():
    table, source = md.snapshot_processes()
    assert os.getpid() in table and source in (md.SOURCE_TOOLHELP32, md.SOURCE_PROCFS, md.SOURCE_PS)
    proof = md.prove_zero_descendants(os.getpid(), settle_seconds=0.0)
    assert proof.proven is False and os.getpid() in proof.remaining and proof.source == source


def test_real_process_table_proves_a_reaped_child_gone():
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait(timeout=60)
    proof = md.prove_zero_descendants(child.pid, settle_seconds=5.0)
    assert proof.proven is True and proof.remaining == ()


# ---------------------------------------------------------------- parsing helpers

def test_parse_result_object_shapes():
    assert mos.parse_result_object("") == (None, 0)
    assert mos.parse_result_object('{"a": 1}') == ({"a": 1}, 0)
    assert mos.parse_result_object('noise\n{"a": 1}\n') == ({"a": 1}, 1)
    assert mos.parse_result_object('{"a": 1}\nnoise\n') == ({"a": 1}, 1)
    assert mos.parse_result_object("[1]") == (None, 1)
    assert mos.parse_result_object("x\ny") == (None, 2)


def test_extract_worker_payload_prefers_structured_output_and_records_the_carrier():
    assert mos.extract_worker_payload({"structured_output": {"k": 1}, "result": "{}"}) == ({"k": 1}, "structured_output")
    assert mos.extract_worker_payload({"result": '{"k": 2}'}) == ({"k": 2}, "result_text")
    assert mos.extract_worker_payload({"result": "prose"}) == (None, "result_text")
    assert mos.extract_worker_payload({"result": ""}) == (None, "")
    assert mos.extract_worker_payload({}) == (None, "")


# ---------------------------------------------------------------- wiring (R580)

def test_run_loop_wires_the_one_shot_runner_and_reviewer_under_a_manifest():
    from tools.agent_supervisor import cli
    source = inspect.getsource(cli._run_loop)
    assert "OneShotRunner(" in source and "OneShotReviewer(" in source
    assert "turn_budget=None if launch is not None else turn_budget" in source
    assert "max_turns=args.max_turns if launch is not None else" in source
