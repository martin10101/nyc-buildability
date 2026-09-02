#!/usr/bin/env python3
"""The MRL one-shot worker runner (M0-T136 C-B4; D-024-R580..R584).

``SupervisedLoop`` calls ``runner.run_unit(prompt, ...)`` and reads a ``RunResult``.
Under ``start --launch-manifest`` that runner is this one instead of the stream-json
``ClaudeRunner``: one task, one FRESH ``claude -p`` process, one prompt written once
with stdin then closed, one ``--json-schema``-bound ``WorkerResult``, no resume, no
second message, no background fallback (R581). Every fact the checkpoint carries is
observed by the controller (run/task/session ids, branch, worktree, SHAs); the
worker supplies only its outcome claim and two text fields (R501/R503).

Fail-closed discipline, in dispatch order and BEFORE any provider contact:

1. a second ``run_unit`` or a non-empty ``extra_turns`` is refused (one process,
   one message);
2. the launch seam (cwd == the packet worktree, never the primary checkout);
3. the executable chain is re-hashed and compared with the manifest pin, and the
   binary's ``--version`` must equal the pinned version (R562/R564);
4. the exact ``env`` handed to Popen must disable the auto-updater (R563);
5. the subagent ledger is created for the child's hook (R571/R582) and the
   restricted profile the manifest verified is the one launched (R578).

Nothing here raises for a contract failure: ``run_unit`` returns a result with
``checkpoint_error`` set and no checkpoint, so the loop stops ``no_valid_checkpoint``
through its existing path. Termination (timeout/cancel/orphan) is followed by an
enumerated descendant-zero proof (R584); an unproven tree marks the containment
degraded so the loop stops rather than trusting a kill that was never verified.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import subprocess
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from . import launch_seam
from .checkpoint_envelope import EnvelopeError, measure_git_state, normalize_branch, normalize_worktree
from .claude_runner import WORKER_CHILD_ROLE, RunnerConfig, RunResult, StreamStats, inspect_stream
from .locking import process_start_token
from .models import digest_of, to_utc_iso
from .mrl_descendants import DescendantProof, Snapshot, prove_zero_descendants
from .mrl_exec_chain import (
    RunVersion,
    chain_record,
    observe_version,
    observed_model_from_result,
    resolve_chain,
    verify_chain_now,
    verify_child_env,
    verify_runtime_identity,
)
from .mrl_launch_path import LaunchPreflight
from .mrl_provider_schema import provider_schema_for_claude_cli
from .mrl_subagent_contract import SubagentLedger
from .mrl_transport import build_one_shot_plan, run_one_shot
from .mrl_worker_result import (
    ContractError,
    ControllerObservedFacts,
    WorkerResult,
    build_claude_checkpoint,
    load_schema,
)
from .process import (
    HardDenyError,
    ProcessContainer,
    ProcessError,
    assert_argv_safe,
    claude_child_env,
    terminate_process_tree,
)
from .recovery import clear_child_record, record_launched_child, recorded_start_token_for
from .recovery_probes import GitRunner, subprocess_git

UNIT_RECORD_NAME = "one_shot_unit.json"
CONTAINMENT_DESCENDANTS_REMAINING = "descendants_remaining"
#: The seconds a terminated child gets to be reaped before the descendant proof runs.
TERMINATE_REAP_SECONDS = 15.0
SOURCE_STRUCTURED = "structured_output"
SOURCE_RESULT_TEXT = "result_text"

#: Appended to the operator's prompt so the ONE reply is the schema-bound object.
RESULT_CONTRACT = """

## MRL result contract (controller-enforced)
This is a ONE-SHOT unit: you get this single message and no follow-up. Do the
task inside the allowed paths, then finish by returning ONLY the structured
result the launch schema binds: {"outcome": "COMPLETED"|"BLOCKED"|"NEEDS_OWNER",
"summary": "<what you did, verified, or why blocked>", "requested_next_action":
"<what should happen next, or empty>"}. Do not report ids, SHAs, branches, model
or executable identity, gate results or evidence digests: the controller observes
every such fact itself and rejects any extra field. Your outcome is a claim;
advancement is decided by the controller and the independent reviewer.
"""

#: pid, argv, cwd, env, stdin text, timeout -> a Popen-like handle. Test seam only.
Popen = Callable[..., Any]


@dataclasses.dataclass
class OneShotRunResult(RunResult):
    """``RunResult`` plus the one-shot facts the loop's consumers can read by name."""

    descendant_proof: dict[str, Any] = dataclasses.field(default_factory=dict)
    accounting: dict[str, Any] = dataclasses.field(default_factory=dict)
    launch_record: dict[str, Any] = dataclasses.field(default_factory=dict)
    result_source: str = ""
    worker_result: dict[str, Any] = dataclasses.field(default_factory=dict)
    permission_denials: tuple[dict[str, Any], ...] = ()


def _refused(argv: Sequence[str], code: str, message: str, **extra: Any) -> OneShotRunResult:
    return OneShotRunResult(argv=tuple(argv), returncode=-1, duration_seconds=0.0,
                            checkpoint_error=f"{code}: {message}", **extra)


def parse_result_object(stdout: str) -> "tuple[dict[str, Any] | None, int]":
    """The ``--output-format json`` result object, or ``(None, malformed_lines)``.

    The whole stdout is tried first; failing that, the LAST line that parses as a
    JSON object wins (a preamble line is counted as malformed, never trusted).
    """
    text = stdout.strip()
    if not text:
        return None, 0
    try:
        whole = json.loads(text)
        if isinstance(whole, dict):
            return whole, 0
    except ValueError:
        pass
    lines = [line for line in text.splitlines() if line.strip()]
    for index in range(len(lines) - 1, -1, -1):
        try:
            candidate = json.loads(lines[index])
        except ValueError:
            continue
        if isinstance(candidate, dict):
            return candidate, len(lines) - 1
    return None, len(lines)


def extract_worker_payload(result: Mapping[str, Any]) -> "tuple[Any, str]":
    """``(payload, source)``: ``structured_output`` when present, else the result text parsed.

    The CLI's exact ``--json-schema`` carrier is proven by the owner-run canary, not
    assumed here: both observed carriers are accepted and the one used is recorded.
    """
    if "structured_output" in result:
        return result["structured_output"], SOURCE_STRUCTURED
    text = result.get("result")
    if isinstance(text, str) and text.strip():
        try:
            return json.loads(text), SOURCE_RESULT_TEXT
        except ValueError:
            return None, SOURCE_RESULT_TEXT
    return None, ""


#: Denials kept per unit; the canary's restricted-tool item needs the first few, not a transcript.
MAX_PERMISSION_DENIALS = 50


def permission_denials_of(result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """The result object's ``permission_denials`` rows as ``{tool_name, tool_input}``.

    The CLI reports a denied tool call in the ``result`` event's ``permission_denials``
    list (the field ``preflight`` already measures). Anything that is not a list of
    objects yields ``()`` - a missing or malformed field is recorded as *no denial
    observed*, never as a denial. Capped at ``MAX_PERMISSION_DENIALS`` rows.
    """
    rows = result.get("permission_denials")
    if not isinstance(rows, list):
        return ()
    kept: list[dict[str, Any]] = []
    for row in rows[:MAX_PERMISSION_DENIALS]:
        if isinstance(row, Mapping):
            kept.append({"tool_name": str(row.get("tool_name", "") or ""), "tool_input": row.get("tool_input")})
    return tuple(kept)


class OneShotRunner:
    """``run_unit``-compatible one-shot worker bound to a verified launch manifest."""

    def __init__(self, config: RunnerConfig, *, launch: LaunchPreflight, audit: Any = None,
                 run_id: str = "", journal: Any = None, git: GitRunner | None = None,
                 popen: Popen | None = None, run_version: RunVersion | None = None,
                 snapshot: Snapshot | None = None, container_factory: Any = None) -> None:
        self.config = config
        self.launch = launch
        self.audit = audit
        self.run_id = run_id
        self.journal = journal
        self._git = git or subprocess_git()
        self._popen = popen or subprocess.Popen
        self._run_version = run_version
        self._snapshot = snapshot
        self._container_factory = container_factory or ProcessContainer
        self._dispatched = False
        self.last_result: OneShotRunResult | None = None

    # -- identity ----------------------------------------------------------
    def executable_identity(self) -> dict[str, Any]:
        """The bound chain record with the manifest's combined digest under ``digest``."""
        dispatch = self.launch.manifest.dispatch
        try:
            chain = resolve_chain(self.config.executable, "claude")
            identity = verify_chain_now(chain, str(dispatch["claude_chain_sha256"]))
        except ContractError as exc:
            return {"name": "claude", "path": self.config.executable, "digest": "", "error": str(exc)}
        return {"name": "claude", "path": chain.executable, "digest": identity.combined_sha256,
                **chain_record(chain, identity)}

    # -- the unit ----------------------------------------------------------
    def run_unit(self, prompt: str, *, permission_handler: Any = None,
                 cancel_event: "threading.Event | None" = None,
                 extra_turns: Sequence[str] = (), checkpoint_envelope: Any = None) -> OneShotRunResult:
        del permission_handler, checkpoint_envelope  # -p/dontAsk: no control protocol; git is measured here
        argv: tuple[str, ...] = (self.config.executable,)
        if self._dispatched:
            return self._refuse(argv, "one_shot_second_dispatch",
                                "this runner already launched its one fresh process; a second unit "
                                "needs a new launch (R581)")
        self._dispatched = True
        if extra_turns:
            return self._refuse(argv, "one_shot_extra_turns",
                                f"{len(extra_turns)} extra turn(s) were offered; a one-shot unit takes "
                                f"exactly one message and stdin closes (R581)")
        seam = launch_seam.enforce_launch(launch_seam.WorkerLaunchContext(
            cwd=self.config.cwd, expected_worktree=self.config.expected_worktree,
            primary_checkout=self.config.primary_checkout))
        if not seam.ok:
            return self._refuse(argv, seam.code, seam.message)
        expected = self.launch.manifest.expected
        dispatch = self.launch.manifest.dispatch
        try:
            chain = resolve_chain(self.config.executable, "claude")
            identity = verify_chain_now(chain, str(dispatch["claude_chain_sha256"]))
            version = observe_version(chain, run=self._run_version)
            if version != str(dispatch["claude_version"]):
                raise ContractError("claude_version_mismatch",
                                    f"claude --version reported {version!r}; the manifest pins "
                                    f"{dispatch['claude_version']!r} (R564)")
            env = claude_child_env(dict(self.config.extra_env), self.config.env_allowlist)
            verify_child_env(env)
            settings = pathlib.Path(self.launch.profile.profile_path)
            if not settings.is_file():
                raise ContractError("restricted_profile_missing",
                                    f"the verified restricted profile {settings} is not on disk")
            ledger = SubagentLedger.create(self.launch.ledger_path, self.launch.manifest.subagent_contract(self.run_id),
                                           primary_id=f"{self.run_id}.primary")
            before = measure_git_state(self._git, self.config.cwd)
            self._assert_bound(before, expected)
            plan = build_one_shot_plan(
                chain.executable, prompt + RESULT_CONTRACT, model=self.config.model,
                max_turns=int(self.config.max_turns), wall_clock_seconds=float(self.config.timeout_seconds),
                extra_flags=("--json-schema",
                             # The CLI validates --json-schema as Draft 7 and exits 1 on the
                             # canonical 2020-12 declaration before provider contact (M0-T141,
                             # D-024-R667/R670): only the Draft-7 projection may cross this seam.
                             json.dumps(provider_schema_for_claude_cli(
                                 load_schema("worker_result.schema.json")), sort_keys=True),
                             *self.launch.profile.argv_flags))
            argv = tuple(assert_argv_safe(plan.argv))
        except (ContractError, EnvelopeError, ProcessError, HardDenyError, ValueError) as exc:
            code = getattr(exc, "code", "hard_deny" if isinstance(exc, HardDenyError) else "launch_refused")
            return self._refuse(argv, code, getattr(exc, "message", str(exc)))
        launch_record = {
            "chain": chain_record(chain, identity), "version": version, "argv": list(argv),
            "profile_identity_sha256": self.launch.profile.identity_sha256,
            "max_turns": int(self.config.max_turns), "wall_clock_seconds": float(self.config.timeout_seconds),
            "starting_sha": before.head_sha, "launched_at_utc": to_utc_iso(),
            # Measured from the exact mapping handed to Popen (R563): the canary's
            # updater-disablement item reads this, not a narrative.
            "child_env_updater": {"DISABLE_AUTOUPDATER": env.get("DISABLE_AUTOUPDATER", ""),
                                  "disable_updates_present": "DISABLE_UPDATES" in env},
        }
        self._audit("mrl_one_shot_launched", detail={**launch_record, "chain": launch_record["chain"]["kind"]},
                    executable_identity={"name": "claude", "path": chain.executable,
                                         "digest": identity.combined_sha256})
        spawn = _ContainedSpawn(self, env=env, cancel_event=cancel_event)
        started = time.monotonic()
        try:
            transport = run_one_shot(plan, spawn=spawn)
        except ContractError as exc:
            # The process never ran to a result (spawn failure / unjournalable child):
            # the ledger is closed and the refusal carries the descendant proof taken.
            ledger.close()
            result = self._refuse(argv, exc.code, exc.message)
            result.descendant_proof = spawn.proof.to_dict() if spawn.proof else {}
            result.tree_terminated = spawn.terminated
            return result
        duration = time.monotonic() - started
        result = self._settle(argv, transport.returncode, transport.stdout, transport.stderr, spawn,
                              ledger=ledger, before=before, expected=expected, dispatch=dispatch,
                              duration=duration, launch_record=launch_record)
        self.last_result = result
        return result

    # -- settlement --------------------------------------------------------
    def _settle(self, argv: tuple[str, ...], returncode: int, stdout: str, stderr: str,
                spawn: "_ContainedSpawn", *, ledger: SubagentLedger, before: Any,
                expected: Mapping[str, Any], dispatch: Mapping[str, Any], duration: float,
                launch_record: dict[str, Any]) -> OneShotRunResult:
        accounting = ledger.close()
        proof = spawn.proof
        containment = spawn.report.kind if spawn.report is not None else ""
        fallback_reason = spawn.report.fallback_reason if spawn.report is not None else ""
        verified_in_job = spawn.report.verified_in_job if spawn.report is not None else False
        if proof is None or not proof.proven:
            containment = CONTAINMENT_DESCENDANTS_REMAINING
            fallback_reason = (f"descendant-zero proof failed after termination: remaining pids "
                               f"{list(proof.remaining) if proof else '?'} (container {containment_kind(spawn)})")
        result_obj, malformed = parse_result_object(stdout)
        events = [result_obj] if result_obj is not None else []
        observed_models, model_mismatch, mismatch_detail, context_tokens, usage_known = inspect_stream(
            events, expected_model=self.config.expected_model or self.config.model)
        checkpoint = None
        checkpoint_error = ""
        session_id = ""
        payload: Any = None
        source = ""
        worker: WorkerResult | None = None
        try:
            if spawn.timed_out or spawn.cancelled:
                raise ContractError("terminated", "the unit was terminated before a result "
                                    f"({'timeout' if spawn.timed_out else 'cancelled'})")
            if result_obj is None:
                raise ContractError("malformed_output",
                                    f"stdout carried no JSON result object (exit {returncode}); "
                                    f"stderr tail: {stderr[-500:]!r}")
            session_id = str(result_obj.get("session_id", "") or "")
            if returncode != 0 or result_obj.get("is_error") is True:
                raise ContractError("worker_failed",
                                    f"claude exited {returncode} / is_error={result_obj.get('is_error')!r}: "
                                    f"{str(result_obj.get('result', ''))[:500]!r}")
            verify_runtime_identity(expected_model=str(dispatch["claude_runtime_model"]),
                                    expected_version=str(dispatch["claude_version"]),
                                    observed_model=observed_model_from_result(result_obj),
                                    observed_version=str(launch_record["version"]))
            payload, source = extract_worker_payload(result_obj)
            worker = WorkerResult.from_provider(payload)
            if accounting["subagents_live"] or accounting["processes_total"] > 1 + int(
                    dispatch["subagents"]["max_total"]):
                raise ContractError("subagent_accounting_violation",
                                    f"total run accounting is not closed/bounded: {accounting} (R582)")
            after = measure_git_state(self._git, self.config.cwd)
            self._assert_bound(after, expected)
            if not session_id:
                raise ContractError("session_id_missing", "the result object carries no session_id")
            checkpoint = build_claude_checkpoint(worker, ControllerObservedFacts(
                run_id=self.run_id, checkpoint_id=f"{self.run_id}.primary.cp1",
                task_id=str(expected["task_id"]), claude_session_id=session_id,
                starting_sha=before.head_sha, current_sha=after.head_sha,
                branch=after.branch, worktree=after.toplevel))
        except (ContractError, EnvelopeError) as exc:
            checkpoint_error = f"{exc.code}: {exc.message}"
        result = OneShotRunResult(
            argv=argv, returncode=returncode, duration_seconds=duration, session_id=session_id,
            events=len(events), stats=StreamStats(lines=len(events), events=len(events), malformed_lines=malformed),
            checkpoint=checkpoint, checkpoint_error=checkpoint_error,
            checkpoint_original_digest=digest_of(payload) if isinstance(payload, dict) else "",
            timed_out=spawn.timed_out, cancelled=spawn.cancelled, tree_terminated=spawn.terminated,
            containment=containment, containment_fallback_reason=fallback_reason,
            containment_verified_in_job=verified_in_job, stderr_tail=stderr[-4000:],
            raw_events=tuple(events), checkpoint_contract_appended=True,
            observed_models=observed_models, model_mismatch=model_mismatch, mismatch_detail=mismatch_detail,
            context_tokens=context_tokens, usage_known=usage_known,
            result_text=str(result_obj.get("result", "")) if result_obj else "",
            descendant_proof=proof.to_dict() if proof else {}, accounting=dict(accounting),
            launch_record=launch_record, result_source=source,
            worker_result=dataclasses.asdict(worker) if worker else {},
            permission_denials=permission_denials_of(result_obj) if result_obj else ())
        self._write_unit_record(result)
        self._audit("mrl_one_shot_settled", checkpoint_id=checkpoint.checkpoint_id if checkpoint else "",
                    output_digest=digest_of(checkpoint.to_dict()) if checkpoint else "",
                    error_category=checkpoint_error.split(":")[0] if checkpoint_error else "",
                    policy_result="OK" if result.ok else "REFUSED",
                    detail={"returncode": returncode, "timed_out": spawn.timed_out, "cancelled": spawn.cancelled,
                            "containment": containment, "descendant_proof": result.descendant_proof,
                            "accounting": result.accounting, "result_source": source,
                            "observed_models": list(observed_models), "model_mismatch": model_mismatch,
                            "session_id_recorded": bool(session_id),
                            "permission_denials": len(result.permission_denials)})
        return result

    def _assert_bound(self, state: Any, expected: Mapping[str, Any]) -> None:
        if normalize_branch(state.branch) != normalize_branch(str(expected["branch"])):
            raise ContractError("unexpected_branch",
                                f"the worktree is on {state.branch!r}, the manifest binds {expected['branch']!r}")
        if normalize_worktree(state.toplevel) != normalize_worktree(str(expected["worktree"])):
            raise ContractError("wrong_worktree",
                                f"git toplevel {state.toplevel!r} is not the manifest worktree {expected['worktree']!r}")

    def _write_unit_record(self, result: OneShotRunResult) -> None:
        record = {
            "schema": "mrl_one_shot_unit/v1", "run_id": self.run_id, "ok": result.ok,
            "returncode": result.returncode, "checkpoint_error": result.checkpoint_error,
            "checkpoint": result.checkpoint.to_dict() if result.checkpoint else None,
            "worker_result": result.worker_result, "result_source": result.result_source,
            "session_id": result.session_id, "observed_models": list(result.observed_models),
            "model_mismatch": result.model_mismatch, "timed_out": result.timed_out, "cancelled": result.cancelled,
            "tree_terminated": result.tree_terminated, "containment": result.containment,
            "containment_verified_in_job": result.containment_verified_in_job,
            "descendant_proof": result.descendant_proof, "accounting": result.accounting,
            "launch": result.launch_record, "max_turns": int(self.config.max_turns),
            "permission_denials": list(result.permission_denials),
        }
        self.launch.run_dir.mkdir(parents=True, exist_ok=True)
        (self.launch.run_dir / UNIT_RECORD_NAME).write_text(
            json.dumps(record, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    def _refuse(self, argv: Sequence[str], code: str, message: str) -> OneShotRunResult:
        self._audit("mrl_one_shot_refused", policy_result="REFUSED", error_category=code,
                    detail={"code": code, "message": message})
        result = _refused(argv, code, message)
        self.last_result = result
        return result

    def _audit(self, event_type: str, **fields: Any) -> None:
        if self.audit is None:
            return
        self.audit.append(event_type, run_id=self.run_id, **fields)


def containment_kind(spawn: "_ContainedSpawn") -> str:
    return spawn.report.kind if spawn.report is not None else "unstarted"


class _ContainedSpawn:
    """The single ``Spawn`` handed to ``run_one_shot``: Popen inside a container,
    prompt written once, stdin closed, watchdog on cancel/deadline, then the
    descendant-zero proof. Records what actually happened for settlement."""

    def __init__(self, runner: OneShotRunner, *, env: Mapping[str, str],
                 cancel_event: "threading.Event | None") -> None:
        self.runner = runner
        self.env = env
        self.cancel_event = cancel_event
        self.calls = 0
        self.timed_out = False
        self.cancelled = False
        self.terminated = False
        self.report: Any = None
        self.proof: DescendantProof | None = None
        self.pid = 0

    def __call__(self, argv: Sequence[str], *, stdin_text: str, timeout: float) -> tuple[int, str, str]:
        self.calls += 1
        if self.calls > 1:  # run_one_shot already refuses this; belt and braces
            raise ContractError("one_shot_second_spawn", "a one-shot transport spawns exactly once")
        config = self.runner.config
        container = self.runner._container_factory(prefer_job_object=config.use_job_object)
        try:
            process = self.runner._popen(  # noqa: S603 - argv array, shell=False
                list(argv), shell=False, cwd=config.cwd or None, env=dict(self.env),
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace")
        except OSError as exc:
            container.close()
            raise ContractError("spawn_failed", f"the claude executable did not start: {exc}") from exc
        self.pid = int(process.pid)
        container.adopt(process.pid)
        try:
            self._record(process)
        except ContractError:
            self._terminate(container, process)
            self._finish(container, process)
            raise
        stop = threading.Event()
        watchdog = threading.Thread(target=self._watch, args=(process, container, stop, timeout), daemon=True)
        watchdog.start()
        try:
            stdout, stderr = process.communicate(input=stdin_text, timeout=timeout + TERMINATE_REAP_SECONDS)
        except subprocess.TimeoutExpired:
            self.timed_out = True
            self._terminate(container, process)
            stdout, stderr = process.communicate()
        finally:
            stop.set()
            watchdog.join(timeout=2)
            self._finish(container, process)
        return int(process.returncode if process.returncode is not None else -1), stdout or "", stderr or ""

    def _watch(self, process: Any, container: Any, stop: threading.Event, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while not stop.is_set() and process.poll() is None:
            if self.cancel_event is not None and self.cancel_event.is_set():
                self.cancelled = True
                break
            if time.monotonic() >= deadline:
                self.timed_out = True
                break
            stop.wait(0.05)
        if (self.cancelled or self.timed_out) and process.poll() is None:
            self._terminate(container, process)

    def _record(self, process: Any) -> None:
        if self.runner.journal is None:
            return
        try:
            record_launched_child(self.runner.journal, pid=process.pid, role=WORKER_CHILD_ROLE,
                                  start_token=process_start_token(process.pid))
        except Exception as exc:
            raise ContractError("child_record_unwritable",
                                f"the launched worker (pid {process.pid}) could not be journaled ({exc}); "
                                f"it is terminated and the unit refuses") from exc

    def _terminate(self, container: Any, process: Any) -> None:
        self.terminated = True
        try:
            container.terminate_all()
        except Exception:  # pragma: no cover - defensive
            try:
                terminate_process_tree(process.pid)
            except Exception:
                pass
        try:
            process.wait(timeout=TERMINATE_REAP_SECONDS)
        except Exception:
            pass

    def _finish(self, container: Any, process: Any) -> None:
        for pipe in (process.stdin, process.stdout, process.stderr):
            try:
                if pipe is not None and not pipe.closed:
                    pipe.close()
            except Exception:  # pragma: no cover - defensive
                pass
        self.report = container.report()
        container.close()
        proof = prove_zero_descendants(self.pid, snapshot=self.runner._snapshot)
        self.proof = proof
        # The journal record is cleared ONLY on a reaped pid AND a proven-empty tree
        # (M0-T053 discipline): an unproven tree keeps the record so the next start
        # classifies the leftover instead of launching over it.
        if proof.proven and self.runner.journal is not None and process.poll() is not None:
            token = recorded_start_token_for(self.runner.journal, process.pid)
            clear_child_record(self.runner.journal, pid=process.pid, start_token=token)
