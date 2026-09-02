#!/usr/bin/env python3
"""The MRL one-shot Codex reviewer (M0-T136 C-B4; D-024-R580, R582..R584).

``SupervisedLoop`` calls ``reviewer.review(packet, expected_task_id=,
expected_checkpoint_id=)`` and reads a ``ReviewOutcome``. Under ``start
--launch-manifest`` that reviewer is this one instead of ``CodexReviewer``:

* ONE fresh, read-only, ephemeral Codex process per review, bound to the manifest
  (chain re-hashed and version observed before the spawn; R562/R564); the review
  packet plus the controller-issued evidence ids travel on stdin;
* the reviewer returns ONLY a ``ReviewVerdict`` (verdict, rationale, ids it was
  issued) - every fact is the controller's (R502/R503);
* the controller then observes the remote base ref with a real ``git ls-remote``
  and the task branch/HEAD with a real read-only git, checks its own invariants
  and the one-shot unit's recorded gate facts, and builds the git-bound
  ``CodexDecision`` (R504/R505) - APPROVE alone never advances;
* the legacy ``models.CodexDecision`` the loop consumes is synthesized from that
  controller decision, so ``loop.py`` stays untouched.

``review`` never raises for a contract failure: it returns a not-ok outcome with a
typed ``error_code`` and the loop stops through its existing path.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from .checkpoint_envelope import EnvelopeError, measure_git_state, normalize_branch, normalize_worktree
from .codex_reviewer import (
    DEFAULT_REVIEW_TIMEOUT_SECONDS,
    ReviewOutcome,
    build_argv,
    map_decision_to_tier,
)
from .models import CodexDecision as LegacyDecision
from .models import RecordError, digest_of
from .mrl_codex_decision import CodexDecision, ReviewVerdict, build_codex_decision, git_binding_from_observation
from .mrl_descendants import Snapshot, prove_zero_descendants
from .mrl_exec_chain import RunVersion, chain_record, observe_version, resolve_chain, verify_chain_now, verify_child_env
from .mrl_launch_path import LaunchPreflight
from .mrl_one_shot import UNIT_RECORD_NAME
from .mrl_remote import observe_remote
from .mrl_worker_result import ContractError
from .policy import ASK, PolicyDecision, resolve_model
from .process import ProcessContainer, ProcessResult, minimal_env
from .process import run as run_process
from .recovery_probes import GitRunner, subprocess_git

DECISION_RECORD_NAME = "codex_decision.json"
SCHEMA_NAME = "review_verdict.schema.json"
LS_REMOTE_TIMEOUT_SECONDS = 60.0
EVIDENCE_PACKET_ID = "ev.packet"

#: The MRL reviewer duties, sent WITH the packet on stdin (the packet stays data).
REVIEW_INSTRUCTIONS = (
    "You are the independent MRL reviewer for exactly one worker unit. Read the "
    "evidence packet below and inspect the repository read-only. Return ONLY the "
    "schema-bound object {verdict, rationale, evidence_ref_ids}: verdict APPROVE "
    "when the unit's claims are supported by the evidence you can verify, REVISE "
    "when the worker must correct something, HALT on a safety or integrity problem. "
    "evidence_ref_ids may cite ONLY ids from issued_evidence_ids. Do not report "
    "SHAs, branches, models, gate results or digests: the controller observes those "
    "itself, and APPROVE alone never advances the task."
)

LsRemote = Callable[[Sequence[str]], str]


def _subprocess_ls_remote(argv: Sequence[str]) -> str:  # pragma: no cover - live network
    try:
        completed = subprocess.run(list(argv), capture_output=True, text=True, check=False,
                                   timeout=LS_REMOTE_TIMEOUT_SECONDS, env=minimal_env())
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError("remote_unobservable", f"git ls-remote did not complete: {exc}") from exc
    if completed.returncode != 0:
        raise ContractError("remote_unobservable",
                            f"git ls-remote exited {completed.returncode}: {completed.stderr.strip()[:300]}")
    return completed.stdout


def issued_evidence_ids(packet: Mapping[str, Any]) -> tuple[str, ...]:
    """The ids the controller issues for one review: the packet plus one per section."""
    sections = packet.get("sections")
    names = sorted(str(k) for k in sections) if isinstance(sections, Mapping) else []
    return (EVIDENCE_PACKET_ID, *(f"ev.{name}" for name in names))


def packet_checkpoint(packet: Mapping[str, Any]) -> "dict[str, Any] | None":
    """The checkpoint claims as ``evidence.build_packet`` carries them: the
    ``sections.claude_checkpoint.value`` JSON *string* (bounded). ``None`` when
    the section is absent or does not parse to an object - never a guess."""
    sections = packet.get("sections")
    section = sections.get("claude_checkpoint") if isinstance(sections, Mapping) else None
    value = section.get("value") if isinstance(section, Mapping) else None
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return None
    return dict(value) if isinstance(value, Mapping) else None


def review_stdin_body(packet: Mapping[str, Any], issued: Sequence[str]) -> str:
    return json.dumps({"reviewer_instructions": REVIEW_INSTRUCTIONS,
                       "issued_evidence_ids": list(issued), "packet": dict(packet)},
                      ensure_ascii=False, sort_keys=True) + "\n"


def unit_gates_ok(unit: Mapping[str, Any] | None) -> "tuple[bool, str]":
    """The controller's own gate facts from the recorded one-shot unit (never the worker's)."""
    if not isinstance(unit, Mapping):
        return False, "no recorded one-shot unit"
    checks = (
        ("ok", unit.get("ok") is True),
        ("descendant_proof.proven", isinstance(unit.get("descendant_proof"), Mapping)
         and unit["descendant_proof"].get("proven") is True),
        ("accounting.subagents_live==0", isinstance(unit.get("accounting"), Mapping)
         and unit["accounting"].get("subagents_live") == 0),
        ("model_mismatch==False", unit.get("model_mismatch") is False),
    )
    failed = [name for name, passed in checks if not passed]
    return (not failed), ("" if not failed else "unit gate(s) failed: " + ", ".join(failed))


def legacy_decision(decision: CodexDecision, *, task_id: str, checkpoint_id: str,
                    model: str) -> LegacyDecision:
    """The ``models.CodexDecision`` the loop consumes, derived from the controller decision.

    ``verified_origin_main`` is the legacy field name; it carries the OBSERVED base
    ref sha (Option-B neutral: whichever ref the manifest names).
    """
    base = {
        "schema_version": "1.0.0", "reviewed_task_id": task_id, "reviewed_checkpoint_id": checkpoint_id,
        "verified_repo_head": decision.git.task_head_sha, "verified_origin_main": decision.git.observed_base_sha,
        "model_used": model, "reason_codes": [f"mrl:{decision.decision}"],
        "verified_facts": [{"fact": "git_binding", **decision.as_dict()["git"]}],
        "evidence_refs": [{"id": i} for i in decision.evidence_ref_ids],
    }
    if decision.decision == "COMPLETE":
        return LegacyDecision(decision="COMPLETE", **base)
    if decision.decision == "REVISE":
        return LegacyDecision(decision="REVISE", next_claude_prompt=(
            "MRL one-shot: the reviewer requested revision; a revision is a NEW launch of "
            f"one fresh process. Reviewer rationale: {decision.rationale}"), **base)
    if decision.decision == "HALT":
        return LegacyDecision(decision="HALT_UNSAFE", blocking_findings=[
            {"finding": decision.rationale, "source": "mrl_reviewer"}], **base)
    return LegacyDecision(decision="STOP_FOR_OWNER", owner_question=(
        f"The reviewer APPROVED but the controller withheld COMPLETE ({decision.reason}). "
        f"Owner: inspect {DECISION_RECORD_NAME} and decide."), **base)


class OneShotReviewer:
    """``review``-compatible one-shot Codex reviewer bound to a verified launch manifest."""

    def __init__(self, executable: str, *, launch: LaunchPreflight, repo: str, config: Any,
                 selection: Any, audit: Any = None, run_id: str = "",
                 timeout_seconds: float = DEFAULT_REVIEW_TIMEOUT_SECONDS,
                 availability: Callable[[str], bool] | None = None,
                 runner: Callable[..., ProcessResult] | None = None,
                 run_version: RunVersion | None = None, ls_remote: LsRemote | None = None,
                 git: GitRunner | None = None, snapshot: Snapshot | None = None,
                 container_factory: Any = None) -> None:
        self.executable = executable
        self.launch = launch
        self.repo = repo
        self.config = config
        self.selection = selection
        self.audit = audit
        self.run_id = run_id
        self.timeout_seconds = timeout_seconds
        self.availability = availability
        self._run = runner or run_process
        self._run_version = run_version
        self._ls_remote = ls_remote or _subprocess_ls_remote
        self._git = git or subprocess_git()
        self._snapshot = snapshot
        self._container_factory = container_factory or ProcessContainer
        self.schema_path = str(pathlib.Path(__file__).resolve().parent / "schemas" / SCHEMA_NAME)

    def resolve(self, *, role: str = "primary", purpose: str = "checkpoint_review") -> Any:
        return resolve_model("codex", config=self.config, selection=self.selection,
                             availability=self.availability, role=role, purpose=purpose)

    # -- review --------------------------------------------------------------
    def review(self, packet: Mapping[str, Any], *, expected_task_id: str = "",
               expected_checkpoint_id: str = "", role: str = "primary",
               purpose: str = "checkpoint_review") -> ReviewOutcome:
        resolution = self.resolve(role=role, purpose=purpose)
        notify = ("model_fallback_engaged",) if resolution.fallback_engaged else ()
        packet_body = dict(packet)
        packet_digest = digest_of(packet_body)
        if not resolution.usable:
            return self._fail(resolution.reason_code, resolution.reason, model="",
                              digest=resolution.selection_digest, packet_digest=packet_digest, notify=notify)
        dispatch = self.launch.manifest.dispatch
        expected = self.launch.manifest.expected
        if resolution.model != str(dispatch["codex_model"]):
            return self._fail("codex_model_mismatch",
                              f"model selection resolved {resolution.model!r}; the manifest pins "
                              f"{dispatch['codex_model']!r} (one launch, one source of inputs)",
                              model=resolution.model, digest=resolution.selection_digest,
                              packet_digest=packet_digest, notify=notify)
        argv: tuple[str, ...] = (self.executable,)
        returncode = 0
        try:
            chain = resolve_chain(self.executable, "codex")
            identity = verify_chain_now(chain, str(dispatch["codex_chain_sha256"]))
            version = observe_version(chain, run=self._run_version)
            if version != str(dispatch["codex_version"]):
                raise ContractError("codex_version_mismatch",
                                    f"codex --version reported {version!r}; the manifest pins "
                                    f"{dispatch['codex_version']!r} (R564)")
            env = minimal_env({"DISABLE_AUTOUPDATER": "1"})
            verify_child_env(env)
            if str(packet_body.get("task_id", "")) != expected_task_id or \
                    str(packet_body.get("checkpoint_id", "")) != expected_checkpoint_id:
                raise ContractError("packet_identity_mismatch",
                                    f"packet ids {packet_body.get('task_id')!r}/{packet_body.get('checkpoint_id')!r} "
                                    f"are not the expected {expected_task_id!r}/{expected_checkpoint_id!r}")
            issued = issued_evidence_ids(packet_body)
            raw, result, proof = self._invoke(chain.executable, resolution.model, packet_body, issued, env)
            argv, returncode = result.argv, result.returncode
            if result.timed_out:
                raise ContractError("review_timeout", "the reviewer timed out; partial output discarded"
                                    + ("" if proof["proven"] else f"; descendant proof FAILED: {proof}"))
            if not proof["proven"]:
                raise ContractError("reviewer_descendants_remaining",
                                    f"the reviewer process tree was not proven empty: {proof} (R584)")
            if raw is None:
                raise ContractError("no_decision", f"the reviewer produced no JSON object (exit {returncode}); "
                                    f"stderr tail: {result.stderr[-300:]!r}")
            verdict = ReviewVerdict.from_provider(raw, issued_evidence_ids=issued)
            observation = observe_remote(str(expected["origin_url"]), self.launch.manifest.base_ref(),
                                         run=self._ls_remote)
            state = measure_git_state(self._git, self.repo)
            git = git_binding_from_observation(observation, task_branch=str(expected["branch"]),
                                               task_head_sha=state.head_sha)
            invariants_ok, invariant_reason = self._invariants(state, expected, packet_body)
            gates_ok, gate_reason = unit_gates_ok(self._unit_record())
            decision = build_codex_decision(verdict, git, invariants_ok=invariants_ok, gates_ok=gates_ok,
                                            reason="; ".join(r for r in (invariant_reason, gate_reason) if r))
            legacy = legacy_decision(decision, task_id=expected_task_id, checkpoint_id=expected_checkpoint_id,
                                     model=resolution.model)
            legacy.validate()
        except (ContractError, EnvelopeError, RecordError) as exc:
            return self._fail(exc.code, exc.message, model=resolution.model, digest=resolution.selection_digest,
                              packet_digest=packet_digest, notify=notify, argv=argv, returncode=returncode)
        self._persist(decision, legacy, chain_record(chain, identity), version, proof)
        outcome = ReviewOutcome(
            legacy, resolution.model, resolution.selection_digest, 1, argv=tuple(argv), returncode=returncode,
            packet_digest=packet_digest, decision_digest=digest_of(legacy.to_dict()),
            tier=map_decision_to_tier(legacy), notify_events=notify)
        self._audit(outcome, mrl_decision=decision.decision)
        return outcome

    # -- pieces --------------------------------------------------------------
    def _invoke(self, executable: str, model: str, packet: Mapping[str, Any], issued: Sequence[str],
                env: Mapping[str, str]) -> "tuple[dict[str, Any] | None, ProcessResult, dict[str, Any]]":
        handle, output_path = tempfile.mkstemp(prefix="mrl_review_verdict_", suffix=".json")
        os.close(handle)
        container = self._container_factory(prefer_job_object=True)
        try:
            argv = build_argv(executable, repo=self.repo, model=model, schema_path=self.schema_path,
                              output_path=output_path)
            result = self._run(argv, cwd=self.repo, env=env, timeout=self.timeout_seconds,
                               input_text=review_stdin_body(packet, issued), container=container)
            pids = tuple(container.report().adopted_pids)
            container.close()
            proof = (prove_zero_descendants(int(pids[-1]), snapshot=self._snapshot).to_dict() if pids
                     else {"root_pid": 0, "remaining": [], "proven": True, "source": "no_pid_adopted",
                           "attempts": 0, "elapsed_seconds": 0.0})
            text = pathlib.Path(output_path).read_text(encoding="utf-8-sig").strip()
            raw: dict[str, Any] | None = None
            if text:
                try:
                    parsed = json.loads(text)
                    raw = parsed if isinstance(parsed, dict) else None
                except ValueError:
                    raw = None
            return raw, result, proof
        finally:
            try:
                os.unlink(output_path)
            except OSError:  # pragma: no cover - defensive
                pass

    def _invariants(self, state: Any, expected: Mapping[str, Any],
                    packet: Mapping[str, Any]) -> "tuple[bool, str]":
        problems: list[str] = []
        if normalize_branch(state.branch) != normalize_branch(str(expected["branch"])):
            problems.append(f"branch {state.branch!r} != manifest {expected['branch']!r}")
        if normalize_worktree(state.toplevel) != normalize_worktree(str(expected["worktree"])):
            problems.append(f"toplevel {state.toplevel!r} != manifest worktree {expected['worktree']!r}")
        checkpoint = packet_checkpoint(packet)
        if checkpoint is None:
            problems.append("packet carries no parseable sections.claude_checkpoint.value")
        else:
            current = str(checkpoint.get("current_sha", ""))
            if not current or current.lower() != state.head_sha.lower():
                problems.append(f"checkpoint current_sha {current!r} != measured HEAD {state.head_sha!r}")
        return (not problems), ("" if not problems else "invariant(s) failed: " + "; ".join(problems))

    def _unit_record(self) -> "dict[str, Any] | None":
        path = self.launch.run_dir / UNIT_RECORD_NAME
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return data if isinstance(data, dict) and data.get("run_id") == self.run_id else None

    def _persist(self, decision: CodexDecision, legacy: LegacyDecision, chain: Mapping[str, Any],
                 version: str, proof: Mapping[str, Any]) -> None:
        self.launch.run_dir.mkdir(parents=True, exist_ok=True)
        (self.launch.run_dir / DECISION_RECORD_NAME).write_text(json.dumps({
            "schema": "mrl_codex_decision_record/v1", "run_id": self.run_id, "decision": decision.as_dict(),
            "legacy_decision": legacy.to_dict(), "reviewer_chain": dict(chain), "reviewer_version": version,
            "descendant_proof": dict(proof)}, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    def _fail(self, code: str, message: str, *, model: str, digest: str, packet_digest: str,
              notify: tuple[str, ...], argv: Sequence[str] = (), returncode: int = 0) -> ReviewOutcome:
        outcome = ReviewOutcome(
            None, model, digest, 1, argv=tuple(argv), returncode=returncode, error_code=code,
            error_message=message, packet_digest=packet_digest, notify_events=notify,
            tier=PolicyDecision(tier=ASK, reason_code=code, reason=message, rule_id="MRL",
                                classification="unclassified"))
        self._audit(outcome, mrl_decision="")
        return outcome

    def _audit(self, outcome: ReviewOutcome, *, mrl_decision: str) -> None:
        if self.audit is None:
            return
        self.audit.append(
            "codex_review_decision" if outcome.ok else "codex_review_failed", run_id=self.run_id,
            decision=outcome.decision.decision if outcome.decision else "", input_digest=outcome.packet_digest,
            output_digest=outcome.decision_digest, error_category=outcome.error_code,
            policy_result=outcome.tier.reason_code if outcome.tier else "",
            detail={"model_used": outcome.model_used, "model_selection_digest": outcome.selection_digest,
                    "returncode": outcome.returncode, "mrl_decision": mrl_decision,
                    "error_message": outcome.error_message, "notify_events": list(outcome.notify_events)})


__all__ = ["OneShotReviewer", "REVIEW_INSTRUCTIONS", "issued_evidence_ids", "packet_checkpoint", "review_stdin_body",
           "unit_gates_ok", "legacy_decision", "DECISION_RECORD_NAME"]
