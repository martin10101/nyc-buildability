"""M0-T133 (D-024 Amendment 37): controller-authoritative git-state checkpoint
envelope enrichment. Removal-sensitive tests for all eight owner-named scenarios:
all four missing + safely enriched; partially missing; supplied matching; each supplied
field mismatching; unreadable/ambiguous git; normalized Windows worktree paths; the exact
journey-5 opus checkpoint shape; and no false completion/advancement.

Every test injects a fake GitRunner, so none contacts a real repository.
"""

import pytest

from tools.agent_supervisor import checkpoint_envelope as ce
from tools.agent_supervisor import claude_runner as cr
from tools.agent_supervisor.recovery_probes import GitResult

BRANCH = "task/M0-T107-plugin-portability"
WORKTREE = "C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107"
STARTING = "a" * 40
CURRENT = "b" * 40


def fake_git(*, branch=BRANCH, toplevel=WORKTREE, head=CURRENT, fail=False):
    """A GitRunner returning a fixed worktree state (or failing every call)."""
    def run(argv, cwd):
        if fail:
            return GitResult(ran=False, returncode=128, stderr="fatal: not a git repository")
        a = tuple(argv)
        if a == ("rev-parse", "--abbrev-ref", "HEAD"):
            return GitResult(stdout=branch + "\n")
        if a == ("rev-parse", "--show-toplevel"):
            return GitResult(stdout=toplevel + "\n")
        if a == ("rev-parse", "HEAD"):
            return GitResult(stdout=head + "\n")
        return GitResult(ran=False, returncode=1)
    return run


def envelope(**overrides):
    kw = dict(expected_branch=BRANCH, expected_worktree=WORKTREE, starting_sha=STARTING,
              git=fake_git(), worktree=WORKTREE)
    kw.update(overrides)
    return ce.CheckpointEnvelope(**kw)


def worker_checkpoint(**overrides):
    """A valid worker checkpoint shape MINUS the four controller-authoritative fields."""
    base = {
        "schema_version": "1", "run_id": "run_x", "checkpoint_id": "cp1",
        "task_id": "M0-T107", "claude_session_id": "sess-1", "status": "UNIT_COMPLETE",
        "summary": "implemented the portability shim", "proposed_next_action": "await review",
        "claims": [{"kind": "edit", "detail": "x"}], "usage": "unknown",
    }
    base.update(overrides)
    return base


# ---------- scenario 1: all four missing + safely enriched ----------
def test_all_four_missing_safely_enriched():
    auth = envelope().resolve()
    worker = worker_checkpoint()
    enriched, added = ce.enrich_checkpoint(worker, auth)
    assert set(added) == set(ce.ENVELOPE_FIELDS)
    cp = cr.validate_checkpoint(enriched)
    assert cp.branch == BRANCH and cp.starting_sha == STARTING and cp.current_sha == CURRENT
    assert ce.normalize_worktree(cp.worktree) == ce.normalize_worktree(WORKTREE)
    # the worker's original dict is never mutated (preserved as evidence)
    assert all(f not in worker for f in ce.ENVELOPE_FIELDS)


# ---------- scenario 2: partially missing ----------
def test_partially_missing_fills_only_absent():
    auth = envelope().resolve()
    worker = worker_checkpoint(branch=BRANCH, starting_sha=STARTING)  # supplies 2, omits 2
    enriched, added = ce.enrich_checkpoint(worker, auth)
    assert set(added) == {"worktree", "current_sha"}
    cp = cr.validate_checkpoint(enriched)
    assert cp.current_sha == CURRENT


# ---------- scenario 3: supplied fields matching ----------
def test_supplied_all_matching_adds_nothing():
    auth = envelope().resolve()
    worker = worker_checkpoint(branch=BRANCH, worktree=WORKTREE,
                               starting_sha=STARTING, current_sha=CURRENT)
    enriched, added = ce.enrich_checkpoint(worker, auth)
    assert added == []
    cr.validate_checkpoint(enriched)  # still valid


# ---------- scenario 4: each supplied field mismatching (fail closed) ----------
@pytest.mark.parametrize("field,bad", [
    ("branch", "task/WRONG"),
    ("worktree", "C:/Users/MLFLL/Downloads/nyc-zoning/other-wt"),
    ("starting_sha", "c" * 40),
    ("current_sha", "d" * 40),
])
def test_each_supplied_mismatch_fails_closed(field, bad):
    auth = envelope().resolve()
    worker = worker_checkpoint(**{field: bad})
    with pytest.raises(ce.EnvelopeError) as ei:
        ce.enrich_checkpoint(worker, auth)
    assert ei.value.code == "checkpoint_field_mismatch"


# ---------- scenario 5: unreadable / ambiguous git state (fail closed) ----------
def test_unreadable_git_fails_closed():
    with pytest.raises(ce.EnvelopeError) as ei:
        envelope(git=fake_git(fail=True)).resolve()
    assert ei.value.code == "git_unreadable"


def test_ambiguous_current_sha_fails_closed():
    with pytest.raises(ce.EnvelopeError) as ei:
        envelope(git=fake_git(head="abc123")).resolve()  # short/ambiguous HEAD
    assert ei.value.code == "ambiguous_sha"


def test_detached_head_branch_fails_closed():
    with pytest.raises(ce.EnvelopeError) as ei:
        envelope(git=fake_git(branch="HEAD")).resolve()  # detached HEAD
    assert ei.value.code == "ambiguous_branch"


def test_ambiguous_starting_sha_fails_closed():
    with pytest.raises(ce.EnvelopeError) as ei:
        envelope(starting_sha="not-a-sha").resolve()
    assert ei.value.code == "ambiguous_sha"


def test_unexpected_branch_fails_closed():
    # the worktree is genuinely on a different branch than the dispatch expected
    with pytest.raises(ce.EnvelopeError) as ei:
        envelope(git=fake_git(branch="task/OTHER")).resolve()
    assert ei.value.code == "unexpected_branch"


def test_wrong_worktree_fails_closed():
    with pytest.raises(ce.EnvelopeError) as ei:
        envelope(git=fake_git(toplevel="C:/somewhere/else")).resolve()
    assert ei.value.code == "wrong_worktree"


# ---------- scenario 6: normalized Windows worktree paths ----------
def test_windows_worktree_normalization_equivalent_paths_match():
    # backslashes + trailing slash + different case denote the SAME worktree -> resolve OK
    auth = envelope(
        expected_worktree="C:\\Users\\MLFLL\\Downloads\\nyc-zoning\\wt-m0t107\\",
        git=fake_git(toplevel="c:/users/mlfll/downloads/nyc-zoning/wt-m0t107")).resolve()
    # a worker value with yet another slash/case form still matches
    worker = worker_checkpoint(worktree="C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107")
    _enriched, added = ce.enrich_checkpoint(worker, auth)
    assert "worktree" not in added  # supplied and matched


def test_genuinely_different_worktree_still_fails():
    auth = envelope().resolve()
    worker = worker_checkpoint(worktree="C:/Users/MLFLL/Downloads/nyc-zoning/wt-DIFFERENT")
    with pytest.raises(ce.EnvelopeError):
        ce.enrich_checkpoint(worker, auth)


# ---------- scenario 7: the exact journey-5 opus checkpoint shape ----------
def _journey5_events():
    """The journey-5 failure shape: a worker checkpoint that omits exactly the four
    git-state fields, delivered as a fenced JSON object in assistant text (as opus did)."""
    import json
    cp = worker_checkpoint(status="UNIT_COMPLETE")
    text = "Here is my checkpoint:\n```json\n" + json.dumps(cp) + "\n```\n"
    return ({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}},)


def test_journey5_shape_enriched_validates_and_is_removal_sensitive():
    events = _journey5_events()
    chosen = cr.find_checkpoint_candidate(events)
    # WITHOUT enrichment (the pre-fix behavior / a mutant that drops the enrich call) the
    # exact journey-5 shape fails closed on the four missing fields -> RED. This is the
    # removal-sensitivity anchor.
    with pytest.raises(cr.CheckpointError) as ei:
        cr.validate_checkpoint(chosen)
    assert "missing required fields" in str(ei.value)
    assert all(f in str(ei.value) for f in ("branch", "worktree", "starting_sha", "current_sha"))
    # WITH the controller enrichment the same shape validates.
    auth = envelope().resolve()
    enriched, added = ce.enrich_checkpoint(chosen, auth)
    assert set(added) == set(ce.ENVELOPE_FIELDS)
    cr.validate_checkpoint(enriched)


# ---------- scenario 8: no false completion / advancement ----------
def test_enrichment_touches_only_envelope_fields_and_preserves_status():
    auth = envelope().resolve()
    worker = worker_checkpoint(status="BLOCKED", summary="blocked on X",
                               claims=[{"kind": "note", "detail": "y"}],
                               blockers=[{"id": "B-1"}], proposed_next_action="owner input")
    enriched, added = ce.enrich_checkpoint(worker, auth)
    # ONLY the four envelope fields differ between original and enriched
    changed = {k for k in enriched if enriched.get(k) != worker.get(k)}
    assert changed == set(ce.ENVELOPE_FIELDS)
    # a BLOCKED status is never rewritten to a rosier one by enrichment
    cp = cr.validate_checkpoint(enriched)
    assert cp.status == "BLOCKED"
    assert cp.summary == "blocked on X" and cp.blockers == [{"id": "B-1"}]


def test_enrichment_never_fabricates_a_completion_from_a_missing_checkpoint():
    # No candidate at all is still missing_checkpoint (S14) - the envelope never invents one.
    with pytest.raises(cr.CheckpointError) as ei:
        cr.find_checkpoint_candidate(({"type": "assistant", "message": {"content": []}},))
    assert ei.value.code == "missing_checkpoint"
