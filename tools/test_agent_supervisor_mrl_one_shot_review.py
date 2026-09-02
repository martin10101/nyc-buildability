"""Paired tests for the MRL one-shot Codex reviewer (M0-T136 C-B4; D-024-R580, R582..R584, R589).

The Codex process is never real: ``runner`` (the process seam), ``ls_remote``, ``git``,
``run_version``, ``snapshot`` and ``container_factory`` are injected, so every contract
is proven against the recorded argv/stdin/env and the persisted decision record:

* the reviewer returns ONLY a schema-bound ``ReviewVerdict``; every fact in the decision
  (base sha, task head, branch, gates) is the controller's own observation (R502..R505);
* APPROVE alone never advances: a failed invariant or unit gate becomes HOLD ->
  STOP_FOR_OWNER, never COMPLETE;
* the reviewer is one fresh ephemeral read-only process bound to the manifest chain and
  version; a timeout or an unproven descendant tree fails the review (R584);
* every positive path has a negative or mutation twin.

The worker harness comes from ``test_agent_supervisor_mrl_one_shot``.
"""
from __future__ import annotations

import functools
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor import evidence  # noqa: E402
from tools.agent_supervisor import mrl_descendants as md  # noqa: E402
from tools.agent_supervisor import mrl_one_shot as mos  # noqa: E402
from tools.agent_supervisor import mrl_one_shot_review as mor  # noqa: E402
from tools.agent_supervisor.codex_reviewer import build_argv  # noqa: E402
from tools.agent_supervisor.config import load_controller_config, load_model_selection  # noqa: E402
from tools.agent_supervisor.mrl_codex_decision import CodexDecision, GitBinding  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import (  # noqa: E402
    ContractError,
    ControllerObservedFacts,
    WorkerResult,
    build_claude_checkpoint,
)
from tools.agent_supervisor.policy import ASK, AUTO, NOTIFY  # noqa: E402
from tools.agent_supervisor.process import ProcessResult  # noqa: E402
from tools.test_agent_supervisor_mrl_launch_manifest import HEAD  # noqa: E402
from tools.test_agent_supervisor_mrl_one_shot import (  # noqa: E402
    PAYLOAD,
    PROMPT,
    Harness,
    git_seam,
    make_launch,
    make_runner,
)

BASE_SHA = "5" * 40
OTHER_SHA = "6" * 40
TASK_ID = "M0-T136"
CHECKPOINT_ID = "run-1.primary.cp1"
BRANCH = "candidate/D-024-mrl-option-b"
ORIGIN_URL = "https://github.com/martin10101/nyc-buildability"
CODEX_VERSION_TEXT = "codex-cli 0.50.0"
APPROVE = {"verdict": "APPROVE", "rationale": "claims supported by the packet",
           "evidence_ref_ids": ["ev.packet", "ev.claude_checkpoint"]}

CONFIG_TOML = """
[codex]
allowed_models = ["gpt-5-codex", "codex-fallback"]

[claude]
allowed_models = ["claude-opus-4-8"]

[controller]
default_mode = "shadow"

[limits]
max_review_packet_bytes = 262144
"""

SELECTION_TOML = """
[codex]
review_model = "gpt-5-codex"
advisory_model = "gpt-5-codex"
fallback_models = ["codex-fallback"]

[claude]
model = "claude-opus-4-8"
fallback_models = []
"""


# ---------------------------------------------------------------- harness

class ReviewHarness:
    """The (never real) Codex reviewer process: records the invocation, writes the verdict."""

    def __init__(self, verdict=APPROVE, *, text=None, returncode=0, timed_out=False, stderr="reviewer stderr"):
        self.verdict = verdict
        self.text = text
        self.returncode = returncode
        self.timed_out = timed_out
        self.stderr = stderr
        self.calls: list[dict] = []
        self.ls_remote_calls: list[list[str]] = []
        self.version_calls: list[list[str]] = []
        self.processes = Harness()  # container factory + pid bookkeeping

    def run(self, argv, *, cwd, env, timeout, input_text, container):
        self.calls.append({"argv": list(argv), "cwd": cwd, "env": dict(env), "timeout": timeout,
                           "input_text": input_text})
        output_path = argv[argv.index("--output-last-message") + 1]
        body = self.text if self.text is not None else json.dumps(self.verdict)
        pathlib.Path(output_path).write_text(body, encoding="utf-8")
        container.adopt(777)
        return ProcessResult(argv=tuple(argv), returncode=self.returncode, stdout="", stderr=self.stderr,
                             duration_seconds=0.1, timed_out=self.timed_out)

    def ls_remote(self, argv):
        self.ls_remote_calls.append(list(argv))
        return f"{BASE_SHA}\t{argv[3]}\n"

    def run_version(self, argv):
        self.version_calls.append(list(argv))
        return 0, CODEX_VERSION_TEXT, ""


def load_config(tmp_path, *, config_toml=CONFIG_TOML, selection_toml=SELECTION_TOML):
    config_path = tmp_path / "controller.toml"
    selection_path = tmp_path / "model_selection.toml"
    config_path.write_text(config_toml, encoding="utf-8")
    selection_path.write_text(selection_toml, encoding="utf-8")
    return load_controller_config(config_path), load_model_selection(selection_path)


def make_reviewer(launch, rh, tmp_path, *, selection_toml=SELECTION_TOML, **kw):
    config, selection = load_config(tmp_path, selection_toml=selection_toml)
    world = launch["world"]
    params = dict(launch=launch["pf"], repo=str(world["worktree"]), config=config, selection=selection,
                  audit=launch["audit"], run_id=launch["run_id"], timeout_seconds=60.0, runner=rh.run,
                  run_version=rh.run_version, ls_remote=rh.ls_remote, git=git_seam(world),
                  snapshot=lambda: {}, container_factory=rh.processes.container_factory)
    params.update(kw)
    return mor.OneShotReviewer(str(launch["codex_exe"]), **params)


def real_packet(launch, *, current_sha=HEAD, task_id=TASK_ID, checkpoint_id=CHECKPOINT_ID):
    """The packet exactly as the loop builds it: a controller checkpoint through ``evidence.build_packet``."""
    checkpoint = build_claude_checkpoint(
        WorkerResult(**PAYLOAD),
        ControllerObservedFacts(run_id="run-1", checkpoint_id=checkpoint_id, task_id=task_id,
                                claude_session_id="sess-1", starting_sha=HEAD, current_sha=current_sha,
                                branch=BRANCH, worktree=str(launch["world"]["worktree"])))
    result = evidence.build_packet(run_id="run-1", task_id=task_id, checkpoint_id=checkpoint_id,
                                   checkpoint=checkpoint.to_dict())
    assert result.ok, result.reason
    return result.packet.to_dict()


GOOD_UNIT = {"run_id": "run-1", "ok": True, "descendant_proof": {"proven": True},
             "accounting": {"subagents_live": 0}, "model_mismatch": False}


def write_unit(launch, record=GOOD_UNIT):
    path = launch["pf"].run_dir / mos.UNIT_RECORD_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record), encoding="utf-8")


def decision_record(launch):
    return json.loads((launch["pf"].run_dir / mor.DECISION_RECORD_NAME).read_text(encoding="utf-8"))


def audit_rows(launch, event):
    return [r for r in launch["audit"].events if r["event"] == event]


def review(launch, rh, tmp_path, packet, **kw):
    reviewer = make_reviewer(launch, rh, tmp_path, **kw)
    return reviewer.review(packet, expected_task_id=TASK_ID, expected_checkpoint_id=CHECKPOINT_ID)


@pytest.fixture
def launch(tmp_path):
    return make_launch(tmp_path)


@pytest.fixture
def fast_proof(monkeypatch):
    monkeypatch.setattr(mor, "prove_zero_descendants",
                        functools.partial(md.prove_zero_descendants, settle_seconds=0.0, sleep=lambda _s: None))


# ---------------------------------------------------------------- the COMPLETE path (R502..R505)

def test_approve_with_controller_facts_becomes_complete(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert outcome.ok, (outcome.error_code, outcome.error_message)
    legacy = outcome.decision
    assert legacy.decision == "COMPLETE"
    assert legacy.reviewed_task_id == TASK_ID and legacy.reviewed_checkpoint_id == CHECKPOINT_ID
    assert legacy.model_used == "gpt-5-codex" and outcome.model_used == "gpt-5-codex"
    # the git binding is OBSERVED: base from ls-remote, head from git, never from the reviewer
    assert legacy.verified_repo_head == HEAD and legacy.verified_origin_main == BASE_SHA
    assert legacy.evidence_refs == [{"id": "ev.packet"}, {"id": "ev.claude_checkpoint"}]
    assert legacy.reason_codes == ["mrl:COMPLETE"]
    binding = legacy.verified_facts[0]
    assert binding["fact"] == "git_binding" and binding["task_branch"] == BRANCH
    assert binding["expected_base_ref"] == "refs/heads/main" and binding["observed_base_sha"] == BASE_SHA
    assert binding["normalized_remote_url"] and binding["observed_at_utc"]
    assert outcome.tier.tier == NOTIFY and outcome.tier.reason_code == "stage_complete"
    assert outcome.attempts == 1 and outcome.returncode == 0 and outcome.notify_events == ()
    assert outcome.decision_digest and outcome.packet_digest
    # ls-remote asked the manifest's origin for the manifest's base ref (R504/R505)
    assert rh.ls_remote_calls == [["git", "ls-remote", ORIGIN_URL, "refs/heads/main"]]


def test_reviewer_invocation_is_one_ephemeral_read_only_process(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert outcome.ok
    assert len(rh.calls) == 1
    call = rh.calls[0]
    argv = call["argv"]
    output_path = argv[argv.index("--output-last-message") + 1]
    expected = build_argv(str(launch["codex_exe"]), repo=str(launch["world"]["worktree"]), model="gpt-5-codex",
                          schema_path=str(pathlib.Path(mor.__file__).resolve().parent / "schemas"
                                          / mor.SCHEMA_NAME), output_path=output_path)
    assert argv == expected and tuple(argv) == outcome.argv
    assert argv[1] == "exec" and "--ephemeral" in argv and argv[argv.index("--sandbox") + 1] == "read-only"
    assert json.loads(pathlib.Path(argv[argv.index("--output-schema") + 1]).read_text(encoding="utf-8"))["required"]
    assert not pathlib.Path(output_path).exists(), "the temp verdict file is removed after the read"
    assert call["cwd"] == str(launch["world"]["worktree"]) and call["timeout"] == 60.0
    assert call["env"]["DISABLE_AUTOUPDATER"] == "1" and "DISABLE_UPDATES" not in call["env"]
    # the packet + the issued ids travel on stdin, with the reviewer duties
    body = json.loads(call["input_text"])
    assert body["reviewer_instructions"] == mor.REVIEW_INSTRUCTIONS
    assert body["issued_evidence_ids"] == ["ev.packet", "ev.claude_checkpoint", "ev.directive_refs"]
    assert body["packet"]["task_id"] == TASK_ID and body["packet"]["checkpoint_id"] == CHECKPOINT_ID
    assert call["input_text"].endswith("\n")
    # the chain and version were observed from the manifest's codex executable before the spawn
    assert rh.version_calls == [[str(launch["codex_exe"]), "--version"]]


def test_decision_record_and_audit_are_persisted(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert outcome.ok
    record = decision_record(launch)
    assert record["schema"] == "mrl_codex_decision_record/v1" and record["run_id"] == "run-1"
    assert record["decision"]["decision"] == "COMPLETE" and record["decision"]["verdict"] == "APPROVE"
    assert record["decision"]["git"]["observed_base_sha"] == BASE_SHA
    assert record["decision"]["git"]["task_head_sha"] == HEAD
    assert record["legacy_decision"] == outcome.decision.to_dict()
    assert record["reviewer_chain"]["kind"] == "codex" and record["reviewer_chain"]["combined_sha256"] == \
        launch["pf"].manifest.dispatch["codex_chain_sha256"]
    assert record["reviewer_version"] == "0.50.0"
    assert record["descendant_proof"]["proven"] is True and record["descendant_proof"]["root_pid"] == 777
    rows = audit_rows(launch, "codex_review_decision")
    assert len(rows) == 1 and not audit_rows(launch, "codex_review_failed")
    row = rows[0]
    assert row["decision"] == "COMPLETE" and row["policy_result"] == "stage_complete"
    assert row["detail"]["mrl_decision"] == "COMPLETE" and row["detail"]["model_used"] == "gpt-5-codex"
    assert row["output_digest"] == outcome.decision_digest and row["input_digest"] == outcome.packet_digest


def test_end_to_end_worker_unit_then_review_completes(launch, tmp_path):
    """The real chain: one-shot runner -> controller checkpoint -> build_packet -> reviewer -> COMPLETE."""
    worker = Harness()
    result = make_runner(launch, worker).run_unit(PROMPT)
    assert result.ok, result.checkpoint_error
    packet = evidence.build_packet(run_id="run-1", task_id=TASK_ID, checkpoint_id=result.checkpoint.checkpoint_id,
                                   checkpoint=result.checkpoint.to_dict()).packet.to_dict()
    rh = ReviewHarness()
    reviewer = make_reviewer(launch, rh, tmp_path)
    outcome = reviewer.review(packet, expected_task_id=TASK_ID,
                              expected_checkpoint_id=result.checkpoint.checkpoint_id)
    assert outcome.ok, (outcome.error_code, outcome.error_message)
    assert outcome.decision.decision == "COMPLETE"
    assert outcome.decision.verified_repo_head == result.checkpoint.current_sha == HEAD
    events = launch["audit"].names()
    assert events.index("mrl_one_shot_settled") < events.index("codex_review_decision")


# ---------------------------------------------------------------- APPROVE alone never advances (R504)

@pytest.mark.parametrize("record, missing", [
    (None, "no recorded one-shot unit"),
    ({**GOOD_UNIT, "ok": False}, "ok"),
    ({**GOOD_UNIT, "run_id": "run-other"}, "no recorded one-shot unit"),
    ({**GOOD_UNIT, "accounting": {"subagents_live": 1}}, "accounting.subagents_live==0"),
    ({**GOOD_UNIT, "model_mismatch": True}, "model_mismatch==False"),
    ({**GOOD_UNIT, "descendant_proof": {"proven": False}}, "descendant_proof.proven"),
])
def test_unit_gate_failure_holds_instead_of_completing(launch, tmp_path, record, missing):
    if record is not None:
        write_unit(launch, record)
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert outcome.ok, (outcome.error_code, outcome.error_message)
    legacy = outcome.decision
    assert legacy.decision == "STOP_FOR_OWNER" and legacy.reason_codes == ["mrl:HOLD"]
    assert mor.DECISION_RECORD_NAME in legacy.owner_question and "withheld COMPLETE" in legacy.owner_question
    assert missing in legacy.owner_question
    assert outcome.tier.tier == ASK and outcome.tier.reason_code == "stop_for_owner_queued"
    record_on_disk = decision_record(launch)
    assert record_on_disk["decision"]["decision"] == "HOLD" and record_on_disk["decision"]["verdict"] == "APPROVE"
    assert missing in record_on_disk["decision"]["reason"], "the HOLD reason names the controller check that failed"


def test_checkpoint_sha_behind_measured_head_holds(launch, tmp_path):
    write_unit(launch)
    launch["world"]["git"].answers[("rev-parse", "HEAD")] = f"{OTHER_SHA}\n"
    outcome = review(launch, ReviewHarness(), tmp_path, real_packet(launch))
    assert outcome.ok
    assert outcome.decision.decision == "STOP_FOR_OWNER"
    assert f"checkpoint current_sha {HEAD!r} != measured HEAD {OTHER_SHA!r}" in outcome.decision.owner_question
    assert outcome.decision.verified_repo_head == OTHER_SHA, "the binding carries the MEASURED head"


@pytest.mark.parametrize("key, value, fragment", [
    (("rev-parse", "--abbrev-ref", "HEAD"), "main\n", "branch 'main' != manifest"),
    (("rev-parse", "--show-toplevel"), "C:/elsewhere/ctl24\n", "toplevel"),
])
def test_branch_or_toplevel_drift_holds(launch, tmp_path, key, value, fragment):
    write_unit(launch)
    launch["world"]["git"].answers[key] = value
    outcome = review(launch, ReviewHarness(), tmp_path, real_packet(launch))
    assert outcome.ok
    assert outcome.decision.decision == "STOP_FOR_OWNER" and fragment in outcome.decision.owner_question


def test_packet_without_parseable_checkpoint_holds(launch, tmp_path):
    write_unit(launch)
    packet = real_packet(launch)
    packet["sections"]["claude_checkpoint"]["value"] = "{not json"
    outcome = review(launch, ReviewHarness(), tmp_path, packet)
    assert outcome.ok and outcome.decision.decision == "STOP_FOR_OWNER"
    assert "no parseable sections.claude_checkpoint.value" in outcome.decision.owner_question


def test_all_controller_checks_must_pass_together(launch, tmp_path):
    """Mutation: a good unit record does not rescue a failed invariant, nor vice versa."""
    write_unit(launch, {**GOOD_UNIT, "ok": False})
    launch["world"]["git"].answers[("rev-parse", "HEAD")] = f"{OTHER_SHA}\n"
    outcome = review(launch, ReviewHarness(), tmp_path, real_packet(launch))
    assert outcome.decision.decision == "STOP_FOR_OWNER"
    question = outcome.decision.owner_question
    assert "invariant(s) failed" in question and "unit gate(s) failed: ok" in question


# ---------------------------------------------------------------- REVISE / HALT

def test_revise_becomes_revise_with_a_fresh_launch_prompt(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness({"verdict": "REVISE", "rationale": "tests are missing", "evidence_ref_ids": ["ev.packet"]})
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert outcome.ok
    legacy = outcome.decision
    assert legacy.decision == "REVISE" and "tests are missing" in legacy.next_claude_prompt
    assert "NEW launch of one fresh process" in legacy.next_claude_prompt
    assert outcome.tier.tier == AUTO and outcome.tier.reason_code == "decision:REVISE"
    assert decision_record(launch)["decision"]["decision"] == "REVISE"


def test_halt_becomes_halt_unsafe_with_blocking_findings(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness({"verdict": "HALT", "rationale": "secret committed", "evidence_ref_ids": ["ev.packet"]})
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert outcome.ok
    legacy = outcome.decision
    assert legacy.decision == "HALT_UNSAFE"
    assert legacy.blocking_findings == [{"finding": "secret committed", "source": "mrl_reviewer"}]
    assert outcome.tier.tier == ASK and outcome.tier.reason_code == "halt_unsafe"


def test_revise_and_halt_ignore_controller_gate_state(launch, tmp_path):
    """Mutation twin: a failed unit gate cannot upgrade nor downgrade a REVISE/HALT verdict."""
    for verdict, expected in (("REVISE", "REVISE"), ("HALT", "HALT_UNSAFE")):
        rh = ReviewHarness({"verdict": verdict, "rationale": "x", "evidence_ref_ids": ["ev.packet"]})
        outcome = review(launch, rh, tmp_path, real_packet(launch))
        assert outcome.ok and outcome.decision.decision == expected


# ---------------------------------------------------------------- the reviewer's return is bounded (R502)

@pytest.mark.parametrize("verdict, fragment", [
    ({**APPROVE, "evidence_ref_ids": ["ev.packet", "ev.forged"]}, "R502"),
    ({**APPROVE, "evidence_ref_ids": []}, "evidence_ref_ids"),
    ({**APPROVE, "verdict": "COMPLETE"}, "verdict"),
    ({**APPROVE, "observed_base_sha": BASE_SHA}, "observed_base_sha"),
    ({"verdict": "APPROVE", "rationale": "", "evidence_ref_ids": ["ev.packet"]}, "rationale"),
])
def test_forged_or_malformed_verdict_is_refused(launch, tmp_path, verdict, fragment):
    write_unit(launch)
    outcome = review(launch, ReviewHarness(verdict), tmp_path, real_packet(launch))
    assert not outcome.ok and outcome.decision is None
    assert outcome.error_code == "contract_violation" and fragment in outcome.error_message
    assert outcome.tier.tier == ASK and outcome.tier.reason_code == "contract_violation"
    assert not (launch["pf"].run_dir / mor.DECISION_RECORD_NAME).exists()
    rows = audit_rows(launch, "codex_review_failed")
    assert len(rows) == 1 and rows[0]["error_category"] == "contract_violation"
    assert rows[0]["detail"]["mrl_decision"] == "" and rows[0]["detail"]["returncode"] == 0


@pytest.mark.parametrize("text", ["", "   ", "not json", "[1, 2]", "\"a string\""])
def test_no_json_object_is_no_decision(launch, tmp_path, text):
    write_unit(launch)
    outcome = review(launch, ReviewHarness(text=text, returncode=3, stderr="boom"), tmp_path, real_packet(launch))
    assert not outcome.ok and outcome.error_code == "no_decision"
    assert "exit 3" in outcome.error_message and "boom" in outcome.error_message
    assert outcome.returncode == 3 and outcome.argv[1] == "exec"


def test_utf8_bom_output_is_still_read(launch, tmp_path):
    write_unit(launch)
    outcome = review(launch, ReviewHarness(text="\ufeff" + json.dumps(APPROVE)), tmp_path, real_packet(launch))
    assert outcome.ok and outcome.decision.decision == "COMPLETE"


# ---------------------------------------------------------------- pre-spawn refusals (manifest binding)

def test_unusable_model_resolution_fails_before_anything_runs(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness()
    reviewer = make_reviewer(launch, rh, tmp_path, availability=lambda _m: False)
    outcome = reviewer.review(real_packet(launch), expected_task_id=TASK_ID, expected_checkpoint_id=CHECKPOINT_ID)
    assert not outcome.ok and outcome.error_code == "chain_exhausted" and outcome.model_used == ""
    assert outcome.tier.tier == ASK and outcome.tier.reason_code == "chain_exhausted"
    assert rh.calls == [] and rh.version_calls == [] and rh.ls_remote_calls == []
    assert outcome.selection_digest == reviewer.selection.digest()


def test_fallback_model_disagreeing_with_manifest_is_refused(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness()
    reviewer = make_reviewer(launch, rh, tmp_path, availability=lambda m: m == "codex-fallback")
    outcome = reviewer.review(real_packet(launch), expected_task_id=TASK_ID, expected_checkpoint_id=CHECKPOINT_ID)
    assert not outcome.ok and outcome.error_code == "codex_model_mismatch"
    assert "'codex-fallback'" in outcome.error_message and "'gpt-5-codex'" in outcome.error_message
    assert outcome.model_used == "codex-fallback" and outcome.notify_events == ("model_fallback_engaged",)
    assert rh.calls == []


def test_selection_pinning_a_different_primary_is_refused(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch),
                     selection_toml=SELECTION_TOML.replace('review_model = "gpt-5-codex"',
                                                           'review_model = "codex-fallback"'))
    assert not outcome.ok and outcome.error_code == "codex_model_mismatch" and rh.calls == []


def test_codex_executable_drift_is_refused_before_spawn(launch, tmp_path):
    write_unit(launch)
    launch["codex_exe"].write_text("codex-but-different-bytes", encoding="utf-8")
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert not outcome.ok and outcome.error_code == "contract_violation" and "R511" in outcome.error_message
    assert rh.calls == [] and rh.version_calls == []


@pytest.mark.parametrize("text, rc", [("codex-cli 0.49.0", 0), ("", 0), ("codex-cli 0.50.0", 1)])
def test_codex_version_drift_is_refused_before_spawn(launch, tmp_path, text, rc):
    write_unit(launch)
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch), run_version=lambda _argv: (rc, text, ""))
    assert not outcome.ok and outcome.error_code == "codex_version_mismatch"
    assert "'0.50.0'" in outcome.error_message and "R564" in outcome.error_message
    assert rh.calls == []


def test_updates_env_mutation_is_caught(launch, tmp_path, monkeypatch):
    """Mutation: if the env builder ever lets DISABLE_UPDATES through, the reviewer refuses."""
    write_unit(launch)
    real = mor.minimal_env
    monkeypatch.setattr(mor, "minimal_env", lambda extra=None: {**real(extra), "DISABLE_UPDATES": "1"})
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert not outcome.ok and outcome.error_code == "contract_violation" and "R280" in outcome.error_message
    assert rh.calls == []


@pytest.mark.parametrize("task_id, checkpoint_id", [
    ("M0-T999", CHECKPOINT_ID), (TASK_ID, "run-1.primary.cp2"), ("", ""),
])
def test_packet_identity_mismatch_is_refused_before_spawn(launch, tmp_path, task_id, checkpoint_id):
    write_unit(launch)
    rh = ReviewHarness()
    packet = real_packet(launch, task_id=task_id or TASK_ID, checkpoint_id=checkpoint_id or CHECKPOINT_ID)
    packet["task_id"], packet["checkpoint_id"] = task_id, checkpoint_id
    outcome = review(launch, rh, tmp_path, packet)
    assert not outcome.ok and outcome.error_code == "packet_identity_mismatch"
    assert rh.calls == []


# ---------------------------------------------------------------- the reviewer process itself (R584)

def test_review_timeout_discards_partial_output(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness(timed_out=True)
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert not outcome.ok and outcome.error_code == "review_timeout"
    assert "partial output discarded" in outcome.error_message and "FAILED" not in outcome.error_message
    assert outcome.decision is None and not (launch["pf"].run_dir / mor.DECISION_RECORD_NAME).exists()
    assert rh.ls_remote_calls == [], "no observation is bound for a review that did not finish"


def test_unproven_reviewer_descendants_fail_the_review(launch, tmp_path, fast_proof):
    write_unit(launch)
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch), snapshot=lambda: {777: 1, 778: 777})
    assert not outcome.ok and outcome.error_code == "reviewer_descendants_remaining"
    assert "R584" in outcome.error_message and "778" in outcome.error_message
    assert rh.ls_remote_calls == []


def test_timeout_with_unproven_descendants_reports_both(launch, tmp_path, fast_proof):
    write_unit(launch)
    rh = ReviewHarness(timed_out=True)
    outcome = review(launch, rh, tmp_path, real_packet(launch), snapshot=lambda: {777: 1})
    assert outcome.error_code == "review_timeout" and "descendant proof FAILED" in outcome.error_message


def test_unobservable_process_table_is_not_proof(launch, tmp_path, fast_proof):
    write_unit(launch)

    def broken():
        raise OSError("no process table")
    outcome = review(launch, ReviewHarness(), tmp_path, real_packet(launch), snapshot=broken)
    assert outcome.error_code == "reviewer_descendants_remaining" and "'source': 'unavailable'" in outcome.error_message


def test_container_is_closed_and_pid_proved(launch, tmp_path):
    write_unit(launch)
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert outcome.ok
    containers = rh.processes.containers
    assert len(containers) == 1 and containers[0].closed and containers[0].pids == [777]
    assert containers[0].prefer_job_object is True


# ---------------------------------------------------------------- the remote observation (R504/R505)

def test_unobservable_remote_fails_the_review(launch, tmp_path):
    write_unit(launch)

    def unreachable(_argv):
        raise ContractError("remote_unobservable", "git ls-remote did not complete")
    outcome = review(launch, ReviewHarness(), tmp_path, real_packet(launch), ls_remote=unreachable)
    assert not outcome.ok and outcome.error_code == "remote_unobservable"
    assert not (launch["pf"].run_dir / mor.DECISION_RECORD_NAME).exists()


@pytest.mark.parametrize("output", ["", "not-a-sha\trefs/heads/main\n", "abc123\trefs/heads/main\n"])
def test_non_sha_remote_output_fails_closed(launch, tmp_path, output):
    write_unit(launch)
    outcome = review(launch, ReviewHarness(), tmp_path, real_packet(launch), ls_remote=lambda _argv: output)
    assert not outcome.ok and outcome.error_code == "contract_violation"
    assert "did not yield a 40-hex sha" in outcome.error_message


def test_base_ref_comes_from_the_manifest_not_a_default(launch, tmp_path):
    write_unit(launch)
    launch["pf"].manifest.dispatch["base_ref"] = "refs/heads/integration/mrl"
    rh = ReviewHarness()
    outcome = review(launch, rh, tmp_path, real_packet(launch))
    assert outcome.ok
    assert rh.ls_remote_calls == [["git", "ls-remote", ORIGIN_URL, "refs/heads/integration/mrl"]]
    assert outcome.decision.verified_facts[0]["expected_base_ref"] == "refs/heads/integration/mrl"


# ---------------------------------------------------------------- helpers

def test_issued_evidence_ids_are_packet_plus_sorted_sections():
    assert mor.issued_evidence_ids({"sections": {"zeta": 1, "alpha": 2}}) == ("ev.packet", "ev.alpha", "ev.zeta")
    assert mor.issued_evidence_ids({}) == ("ev.packet",)
    assert mor.issued_evidence_ids({"sections": ["not", "a", "map"]}) == ("ev.packet",)


@pytest.mark.parametrize("packet, expected", [
    ({"sections": {"claude_checkpoint": {"value": json.dumps({"current_sha": HEAD})}}}, {"current_sha": HEAD}),
    ({"sections": {"claude_checkpoint": {"value": {"current_sha": HEAD}}}}, {"current_sha": HEAD}),
    ({"sections": {"claude_checkpoint": {"value": "{broken"}}}, None),
    ({"sections": {"claude_checkpoint": {"value": "[1]"}}}, None),
    ({"sections": {"claude_checkpoint": "not a section"}}, None),
    ({"sections": {}}, None),
    ({}, None),
])
def test_packet_checkpoint_reads_the_bounded_json_string(packet, expected):
    assert mor.packet_checkpoint(packet) == expected


def test_review_stdin_body_is_sorted_json_with_trailing_newline():
    body = mor.review_stdin_body({"b": 1, "a": 2}, ("ev.packet",))
    assert body.endswith("\n") and json.loads(body) == {
        "reviewer_instructions": mor.REVIEW_INSTRUCTIONS, "issued_evidence_ids": ["ev.packet"], "packet": {"a": 2, "b": 1}}
    assert body.index('"issued_evidence_ids"') < body.index('"packet"') < body.index('"reviewer_instructions"')


@pytest.mark.parametrize("unit, ok, fragment", [
    (GOOD_UNIT, True, ""),
    (None, False, "no recorded one-shot unit"),
    ("nope", False, "no recorded one-shot unit"),
    ({**GOOD_UNIT, "ok": "true"}, False, "ok"),
    ({**GOOD_UNIT, "descendant_proof": "proven"}, False, "descendant_proof.proven"),
    ({**GOOD_UNIT, "accounting": {}}, False, "accounting.subagents_live==0"),
    ({**GOOD_UNIT, "model_mismatch": None}, False, "model_mismatch==False"),
    ({"run_id": "run-1"}, False, "ok, descendant_proof.proven, accounting.subagents_live==0, model_mismatch==False"),
])
def test_unit_gates_ok_checks_every_controller_fact(unit, ok, fragment):
    passed, reason = mor.unit_gates_ok(unit)
    assert passed is ok and fragment in reason


def _decision(kind, reason=""):
    git = GitBinding(normalized_remote_url="github.com/martin10101/nyc-buildability", expected_base_ref="refs/heads/main",
                     observed_base_sha=BASE_SHA, task_branch=BRANCH, task_head_sha=HEAD,
                     observed_at_utc="2026-09-01T00:00:00+00:00")
    verdict = {"HALT": "HALT", "REVISE": "REVISE"}.get(kind, "APPROVE")
    return CodexDecision(decision=kind, verdict=verdict, rationale="why", evidence_ref_ids=("ev.packet",), git=git,
                         reason=reason)


@pytest.mark.parametrize("kind, legacy_kind, field", [
    ("COMPLETE", "COMPLETE", "evidence_refs"), ("REVISE", "REVISE", "next_claude_prompt"),
    ("HALT", "HALT_UNSAFE", "blocking_findings"), ("HOLD", "STOP_FOR_OWNER", "owner_question"),
])
def test_legacy_decision_maps_every_controller_decision(kind, legacy_kind, field):
    legacy = mor.legacy_decision(_decision(kind, reason="held"), task_id=TASK_ID, checkpoint_id=CHECKPOINT_ID,
                                 model="gpt-5-codex")
    assert legacy.decision == legacy_kind and getattr(legacy, field)
    assert legacy.verified_repo_head == HEAD and legacy.verified_origin_main == BASE_SHA
    assert legacy.reason_codes == [f"mrl:{kind}"] and legacy.model_used == "gpt-5-codex"
    legacy.validate()
    if kind == "HOLD":
        assert "held" in legacy.owner_question


def test_legacy_decision_never_invents_a_next_prompt_for_complete():
    legacy = mor.legacy_decision(_decision("COMPLETE"), task_id=TASK_ID, checkpoint_id=CHECKPOINT_ID, model="m")
    assert legacy.next_claude_prompt == "" and legacy.owner_question == "" and legacy.blocking_findings == []


# ---------------------------------------------------------------- loop wiring

def test_loop_consumes_the_reviewer_through_the_review_contract():
    """``SupervisedLoop`` only ever calls ``review(packet, expected_task_id=, expected_checkpoint_id=)``."""
    import inspect

    from tools.agent_supervisor import loop
    source = inspect.getsource(loop)
    assert "reviewer.review(" in source
    assert set(inspect.signature(mor.OneShotReviewer.review).parameters) >= {
        "packet", "expected_task_id", "expected_checkpoint_id"}
