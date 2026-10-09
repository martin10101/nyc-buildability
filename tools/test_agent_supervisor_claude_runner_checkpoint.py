"""M0-T133 (D-024 Amendment 37): loop-level integration for the controller-authoritative
checkpoint envelope - the `SupervisedLoop` helpers that build the envelope (scoped to the
certified limited-auto run) and audit which fields were controller-filled. The methods are
exercised with a lightweight mock ``self`` so no real loop, process, or repository is needed.
"""

import types

from tools.agent_supervisor import checkpoint_envelope as ce
from tools.agent_supervisor.loop import MODE_LIMITED_AUTO, SupervisedLoop
from tools.agent_supervisor.recovery_probes import GitResult


class _RecordingAudit:
    def __init__(self):
        self.records = []

    def append(self, event_type, *, policy_result="", detail=None, **_kw):
        self.records.append((event_type, policy_result, detail or {}))


class _Authority:
    def __init__(self, branch, worktree):
        self.branch = branch
        self.worktree = worktree


def _mock_loop(*, mode, branch, worktree, git, audit=None):
    return types.SimpleNamespace(
        mode=mode, authority=_Authority(branch, worktree), _git=git,
        audit=audit or _RecordingAudit())


def _git_returning(head):
    def run(argv, cwd):
        return GitResult(stdout=head + "\n")
    return run


def test_build_envelope_in_limited_auto():
    m = _mock_loop(mode=MODE_LIMITED_AUTO, branch="task/M0-T107-plugin-portability",
                   worktree="C:/wt", git=_git_returning("c" * 40))
    env = SupervisedLoop._build_checkpoint_envelope(m)
    assert isinstance(env, ce.CheckpointEnvelope)
    assert env.expected_branch == "task/M0-T107-plugin-portability"
    assert env.expected_worktree == "C:/wt"
    assert env.starting_sha == "c" * 40


def test_build_envelope_skipped_in_shadow():
    m = _mock_loop(mode="shadow", branch="task/x", worktree="C:/wt",
                   git=_git_returning("c" * 40))
    assert SupervisedLoop._build_checkpoint_envelope(m) is None


def test_build_envelope_skipped_in_supervised():
    m = _mock_loop(mode="supervised", branch="task/x", worktree="C:/wt",
                   git=_git_returning("c" * 40))
    assert SupervisedLoop._build_checkpoint_envelope(m) is None


def test_build_envelope_none_without_dispatch_context():
    m = _mock_loop(mode=MODE_LIMITED_AUTO, branch="", worktree="",
                   git=_git_returning("c" * 40))
    assert SupervisedLoop._build_checkpoint_envelope(m) is None


def test_build_envelope_unreadable_predispatch_git_leaves_starting_empty():
    # A pre-dispatch HEAD that cannot be read -> starting_sha "" -> resolve() fails closed later.
    m = _mock_loop(mode=MODE_LIMITED_AUTO, branch="task/x", worktree="C:/wt",
                   git=lambda argv, cwd: GitResult(ran=False, returncode=128))
    env = SupervisedLoop._build_checkpoint_envelope(m)
    assert env is not None and env.starting_sha == ""
    try:
        env.resolve()
        raise AssertionError("resolve() should have failed closed")
    except ce.EnvelopeError as exc:
        assert exc.code in ("git_unreadable", "ambiguous_sha")


def test_audit_records_only_when_fields_were_enriched():
    audit = _RecordingAudit()
    m = types.SimpleNamespace(audit=audit)
    # nothing enriched -> no audit record
    SupervisedLoop._audit_checkpoint_enrichment(
        m, types.SimpleNamespace(checkpoint_enriched_fields=(), checkpoint_original_digest="x"))
    assert audit.records == []
    # some enriched -> exactly one record naming the added fields + the worker's original digest
    SupervisedLoop._audit_checkpoint_enrichment(
        m, types.SimpleNamespace(checkpoint_enriched_fields=("branch", "current_sha"),
                                 checkpoint_original_digest="deadbeef"))
    assert len(audit.records) == 1
    event, policy, detail = audit.records[0]
    assert event == "checkpoint_envelope_enriched"
    assert policy == "controller_authoritative"
    assert detail["added_fields"] == ["branch", "current_sha"]
    assert detail["worker_original_checkpoint_digest"] == "deadbeef"
    assert "NOT worker-authored" in detail["note"]
