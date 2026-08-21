#!/usr/bin/env python3
"""Live pre-dispatch revalidation probes (M0-T079; D-007 S11.5 step 5; D-023 item 1).

Qualifying evidence (AD-093 Section 0A.10): a reproduced defect. `cmd_start`
answered six S11.5 revalidation steps with one synthetic boolean - "did the
operator name every CLI input?" - and three more with a bare `True`:

    "task_authority": dispatchable,     "pending_requests": True,
    "branch":         dispatchable,     "scheduled_deadlines": True,
    "worktree":       dispatchable,     "last_external_effect": True,
    ...

so a complete command line CERTIFIED the branch, the worktree, Git and remote
state, auth, the capability manifest, pending requests, deadlines, and the last
external effect without reading any of them.

These tests drive the REAL probes. Every external reader is injected - the Git
runner, the remote-reachability check, the auth check, the clock - so nothing
here touches a network, a provider, or a real repository except the two
end-to-end cases, which build a throwaway checkout with `git init`.

The governing rule, asserted over and over: only ``ok and known`` passes.
"Missing" and "I could not tell" are FAILURES, and `recovery.classify` turns a
failed or absent step into UNSAFE_OR_DRIFTED before anything could be contacted.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import recovery as rec  # noqa: E402
from tools.agent_supervisor import recovery_probes as rp  # noqa: E402
from tools.agent_supervisor import refusals  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import QueuedAsk, to_utc_iso  # noqa: E402
from tools.agent_supervisor.preflight import CAPABILITY_KEY  # noqa: E402
from tools.agent_supervisor.resume_scheduler import (  # noqa: E402
    RESUME_NOT_BEFORE_KEY,
)

HEAD_SHA = "b" * 40


# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------


class FakeGit:
    """A scripted Git runner. Nothing here shells out."""

    def __init__(self, answers: dict[tuple[str, ...], rp.GitResult],
                 default: rp.GitResult | None = None) -> None:
        self.answers = answers
        self.default = default or rp.GitResult(returncode=128, stderr="unscripted query")
        self.calls: list[tuple[tuple[str, ...], str]] = []

    def __call__(self, argv, cwd: str) -> rp.GitResult:
        key = tuple(argv)
        self.calls.append((key, cwd))
        return self.answers.get(key, self.default)


def healthy_git(*, git_dir: str, branch: str = "main", head: str = HEAD_SHA,
                remote_url: str = "https://example.invalid/repo.git") -> FakeGit:
    """A Git that answers every probe query the way a settled checkout would."""
    answers = {
        ("rev-parse", "--abbrev-ref", "HEAD"): rp.GitResult(stdout=branch + "\n"),
        ("rev-parse", "--is-inside-work-tree"): rp.GitResult(stdout="true\n"),
        ("rev-parse", "--absolute-git-dir"): rp.GitResult(stdout=git_dir + "\n"),
        ("diff", "--name-only", "--diff-filter=U"): rp.GitResult(stdout=""),
        ("rev-parse", "HEAD"): rp.GitResult(stdout=head + "\n"),
        ("status", "--porcelain"): rp.GitResult(stdout=" M tools/x.py\n"),
        ("remote", "get-url", "origin"): rp.GitResult(stdout=remote_url + "\n"),
    }
    return FakeGit(answers)


def unavailable_git() -> FakeGit:
    """Git itself cannot be run: every fact is UNDETERMINED, never assumed."""
    return FakeGit({}, default=rp.GitResult(ran=False, stderr="FileNotFoundError: git"))


class ProbeTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.git_dir = self.repo / ".git"
        self.git_dir.mkdir()
        self.worktree = str(self.repo)
        self.journal = DurableJournal(self.tmp / "journal.sqlite3").open()
        self.addCleanup(self.journal.close)
        self.git = healthy_git(git_dir=str(self.git_dir))

    def write_ledger(self, task_id: str, **overrides) -> pathlib.Path:
        tasks = self.repo / "project-control" / "tasks"
        tasks.mkdir(parents=True, exist_ok=True)
        record = {"task_id": task_id, "status": "in_progress", "blockers": []}
        record.update(overrides)
        path = tasks / f"{task_id}.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def packet(self, **overrides) -> dict:
        data = {"task_id": "M0-T079", "status": "in_progress",
                "allowed_paths": ["tools/agent_supervisor/**"]}
        data.update(overrides)
        return data


# --------------------------------------------------------------------------
# The fail-closed rule itself
# --------------------------------------------------------------------------


class ProbeResultTests(unittest.TestCase):
    def test_only_established_and_satisfied_passes(self) -> None:
        self.assertTrue(rp.ProbeResult("s", True, True).passes)
        self.assertFalse(rp.ProbeResult("s", False, True).passes)
        self.assertFalse(rp.ProbeResult("s", True, False).passes,
                         "an UNDETERMINED fact must never pass")
        self.assertFalse(rp.ProbeResult("s", False, False).passes)

    def test_an_unrun_step_is_absent_from_the_map_and_therefore_a_failure(self) -> None:
        report = rp.ProbeReport(results=(rp.ProbeResult("branch", True, True),))
        answers = report.revalidation(rp.STEP_PROBES)
        self.assertEqual(answers, {"branch": True})
        outcome = rec.classify(rec.RecoveryContext(revalidation=answers))
        self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)
        self.assertIn("task_authority", outcome.missing_steps)

    def test_the_step_probes_cover_the_live_half_of_the_s11_5_step_list(self) -> None:
        """Every step this module claims to answer really is an S11.5 step."""
        self.assertTrue(set(rp.STEP_PROBES).issubset(set(rec.REVALIDATION_STEPS)))
        # The three the CLI answers from its own integrity checks, not from here.
        self.assertEqual(
            set(rec.REVALIDATION_STEPS) - set(rp.STEP_PROBES),
            {"controller_manifest", "journal_integrity", "audit_chain"})


# --------------------------------------------------------------------------
# Task authority
# --------------------------------------------------------------------------


class TaskAuthorityProbeTests(ProbeTestBase):
    def probe(self, packet=None) -> rp.ProbeResult:
        return rp.probe_task_authority(packet=packet if packet is not None
                                       else self.packet(),
                                       repo_root=str(self.repo),
                                       packet_path="packet.json")

    def test_a_packet_corroborated_by_the_ledger_passes(self) -> None:
        self.write_ledger("M0-T079")
        result = self.probe()
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["status"], "in_progress")

    def test_a_missing_ledger_record_is_undetermined_not_assumed(self) -> None:
        result = self.probe()
        self.assertFalse(result.passes)
        self.assertFalse(result.known)
        self.assertEqual(result.reason_code, "ledger_record_missing")

    def test_an_unreadable_ledger_record_fails_closed(self) -> None:
        path = self.write_ledger("M0-T079")
        path.write_text("{not json", encoding="utf-8")
        result = self.probe()
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "ledger_record_unreadable")

    def test_a_status_that_confers_no_work_is_refused(self) -> None:
        for status in ("backlog", "accepted", "blocked", ""):
            with self.subTest(status=status):
                result = self.probe(self.packet(status=status))
                self.assertFalse(result.passes)
                self.assertEqual(result.reason_code, "task_not_active")

    def test_a_packet_and_ledger_that_disagree_never_take_the_permissive_one(self) -> None:
        self.write_ledger("M0-T079", status="accepted")
        result = self.probe()
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "ledger_status_mismatch")

    def test_a_ledger_record_for_another_task_is_refused(self) -> None:
        tasks = self.repo / "project-control" / "tasks"
        tasks.mkdir(parents=True, exist_ok=True)
        (tasks / "M0-T079.json").write_text(
            json.dumps({"task_id": "M0-T080", "status": "in_progress",
                        "blockers": []}), encoding="utf-8")
        result = self.probe()
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "ledger_task_id_mismatch")

    def test_an_unresolved_blocker_removes_authority(self) -> None:
        self.write_ledger("M0-T079", blockers=[{"id": "B-1"}])
        result = self.probe()
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "task_blocked")

    def test_a_packet_with_no_task_id_confers_nothing(self) -> None:
        result = self.probe(self.packet(task_id=""))
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "packet_without_task_id")


# --------------------------------------------------------------------------
# Branch and worktree
# --------------------------------------------------------------------------


class BranchProbeTests(ProbeTestBase):
    def test_a_checked_out_branch_passes(self) -> None:
        result = rp.probe_branch(git=self.git, worktree=self.worktree)
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["branch"], "main")

    def test_a_named_branch_must_match_the_checkout(self) -> None:
        result = rp.probe_branch(git=self.git, worktree=self.worktree,
                                 expected_branch="task/M0-T079-bounded-mode")
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "branch_mismatch")

    def test_a_detached_head_is_refused(self) -> None:
        git = healthy_git(git_dir=str(self.git_dir), branch="HEAD")
        result = rp.probe_branch(git=git, worktree=self.worktree)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "detached_head")

    def test_git_that_cannot_run_is_undetermined(self) -> None:
        result = rp.probe_branch(git=unavailable_git(), worktree=self.worktree)
        self.assertFalse(result.passes)
        self.assertFalse(result.known)
        self.assertEqual(result.reason_code, "git_unavailable")

    def test_a_non_repository_is_refused(self) -> None:
        git = FakeGit({}, default=rp.GitResult(
            returncode=128, stderr="fatal: not a git repository"))
        result = rp.probe_branch(git=git, worktree=self.worktree)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "no_checked_out_branch")


class WorktreeProbeTests(ProbeTestBase):
    def test_a_settled_work_tree_passes(self) -> None:
        result = rp.probe_worktree(git=self.git, worktree=self.worktree,
                                   repo_root=str(self.repo))
        self.assertTrue(result.passes)

    def test_a_missing_worktree_is_refused(self) -> None:
        result = rp.probe_worktree(git=self.git, worktree=str(self.tmp / "gone"))
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "worktree_missing")

    def test_a_directory_that_is_not_a_work_tree_is_refused(self) -> None:
        git = healthy_git(git_dir=str(self.git_dir))
        git.answers[("rev-parse", "--is-inside-work-tree")] = rp.GitResult(stdout="false\n")
        result = rp.probe_worktree(git=git, worktree=self.worktree)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "not_a_work_tree")

    def test_an_unfinished_git_operation_is_refused(self) -> None:
        for marker in ("MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD", "BISECT_LOG"):
            with self.subTest(marker=marker):
                path = self.git_dir / marker
                path.write_text("x", encoding="utf-8")
                try:
                    result = rp.probe_worktree(git=self.git, worktree=self.worktree)
                finally:
                    path.unlink()
                self.assertFalse(result.passes)
                self.assertEqual(result.reason_code, "operation_in_progress")
                self.assertIn(marker, result.evidence["markers"])

    def test_unresolved_conflicts_are_refused(self) -> None:
        git = healthy_git(git_dir=str(self.git_dir))
        git.answers[("diff", "--name-only", "--diff-filter=U")] = rp.GitResult(
            stdout="tools/a.py\ntools/b.py\n")
        result = rp.probe_worktree(git=git, worktree=self.worktree)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "unmerged_paths")
        self.assertEqual(result.evidence["paths"], ["tools/a.py", "tools/b.py"])

    def test_ordinary_uncommitted_edits_are_not_a_refusal(self) -> None:
        """Cleanliness means SETTLED, not pristine - the worker edits files."""
        git = healthy_git(git_dir=str(self.git_dir))
        git.answers[("status", "--porcelain")] = rp.GitResult(
            stdout=" M tools/a.py\n?? tools/new.py\n")
        self.assertTrue(rp.probe_worktree(git=git, worktree=self.worktree).passes)


# --------------------------------------------------------------------------
# Git and remote state
# --------------------------------------------------------------------------


class GitRemoteProbeTests(ProbeTestBase):
    def test_a_resolvable_head_passes_without_touching_the_remote(self) -> None:
        result = rp.probe_git_and_remote_state(git=self.git, worktree=self.worktree)
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["head"], HEAD_SHA)
        self.assertIsNone(result.evidence["remote_reachable"])
        self.assertNotIn(("ls-remote", "--exit-code", "--heads",
                          "https://example.invalid/repo.git"),
                         [call[0] for call in self.git.calls])

    def test_an_unresolvable_head_is_refused(self) -> None:
        git = healthy_git(git_dir=str(self.git_dir))
        git.answers[("rev-parse", "HEAD")] = rp.GitResult(
            returncode=128, stderr="fatal: ambiguous argument 'HEAD'")
        result = rp.probe_git_and_remote_state(git=git, worktree=self.worktree)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "head_unresolved")

    def test_a_non_sha_head_is_refused(self) -> None:
        git = healthy_git(git_dir=str(self.git_dir), head="not-a-sha")
        result = rp.probe_git_and_remote_state(git=git, worktree=self.worktree)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "head_unresolved")

    def test_a_required_remote_must_be_PROVEN_reachable(self) -> None:
        reached: list[str] = []

        def reachable(url: str) -> rp.ProbeResult:
            reached.append(url)
            return rp.ProbeResult("remote_reachability", True, True, "", "answered")

        result = rp.probe_git_and_remote_state(
            git=self.git, worktree=self.worktree,
            remote_reachability_required=True, reachability=reachable)
        self.assertTrue(result.passes)
        self.assertEqual(reached, ["https://example.invalid/repo.git"])
        self.assertTrue(result.evidence["remote_reachable"])

    def test_a_required_remote_with_no_check_supplied_fails_closed(self) -> None:
        result = rp.probe_git_and_remote_state(
            git=self.git, worktree=self.worktree, remote_reachability_required=True)
        self.assertFalse(result.passes)
        self.assertFalse(result.known)
        self.assertEqual(result.reason_code, "remote_reachability_unprovable")

    def test_a_required_remote_that_does_not_answer_is_refused(self) -> None:
        def unreachable(_url: str) -> rp.ProbeResult:
            return rp.ProbeResult("remote_reachability", False, True,
                                  "remote_unreachable", "connection refused")

        result = rp.probe_git_and_remote_state(
            git=self.git, worktree=self.worktree,
            remote_reachability_required=True, reachability=unreachable)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "remote_unreachable")

    def test_a_required_remote_that_is_not_configured_is_refused(self) -> None:
        git = healthy_git(git_dir=str(self.git_dir))
        git.answers[("remote", "get-url", "origin")] = rp.GitResult(
            returncode=2, stderr="error: No such remote 'origin'")
        result = rp.probe_git_and_remote_state(
            git=git, worktree=self.worktree, remote_reachability_required=True,
            reachability=lambda _u: rp.ProbeResult("r", True, True))
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "remote_not_configured")

    def test_an_unconfigured_remote_is_fine_when_the_run_does_not_need_one(self) -> None:
        git = healthy_git(git_dir=str(self.git_dir))
        git.answers[("remote", "get-url", "origin")] = rp.GitResult(returncode=2)
        result = rp.probe_git_and_remote_state(git=git, worktree=self.worktree)
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["remote_url"], "")


# --------------------------------------------------------------------------
# Auth and capability
# --------------------------------------------------------------------------


class AuthProbeTests(ProbeTestBase):
    def executables(self) -> dict[str, str]:
        return {"claude": sys.executable, "codex": sys.executable}

    def test_present_executables_pass_and_say_what_was_NOT_proven(self) -> None:
        result = rp.probe_auth(executables=self.executables())
        self.assertTrue(result.passes)
        self.assertFalse(result.evidence["live_credential_check"])
        self.assertIn("presence only", result.detail)

    def test_a_missing_executable_is_refused(self) -> None:
        result = rp.probe_auth(executables={"claude": str(self.tmp / "nope.exe")})
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "executable_missing")

    def test_an_injected_auth_check_is_authoritative(self) -> None:
        result = rp.probe_auth(
            executables=self.executables(),
            auth_check=lambda: rp.ProbeResult("auth", False, True, "token_expired",
                                              "the stored token expired"))
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "token_expired")

    def test_an_undetermined_auth_check_fails_closed(self) -> None:
        result = rp.probe_auth(
            executables=self.executables(),
            auth_check=lambda: rp.ProbeResult("auth", True, False, "", "could not tell"))
        self.assertFalse(result.passes)


class CapabilityProbeTests(ProbeTestBase):
    def executables(self) -> dict[str, str]:
        return {"claude": sys.executable}

    def test_the_first_start_pins_the_executable_identity(self) -> None:
        result = rp.probe_cli_capability_manifest(journal=self.journal,
                                                  executables=self.executables())
        self.assertTrue(result.passes)
        pinned = self.journal.get_state(rp.EXECUTABLE_IDENTITY_KEY)
        self.assertIn("claude", pinned)
        self.assertTrue(pinned["claude"]["digest"])

    def test_a_matching_executable_passes_on_every_later_start(self) -> None:
        rp.probe_cli_capability_manifest(journal=self.journal,
                                         executables=self.executables())
        again = rp.probe_cli_capability_manifest(journal=self.journal,
                                                 executables=self.executables())
        self.assertTrue(again.passes)

    def test_a_changed_provider_cli_is_detected_as_drift(self) -> None:
        rp.probe_cli_capability_manifest(journal=self.journal,
                                         executables=self.executables())
        pinned = dict(self.journal.get_state(rp.EXECUTABLE_IDENTITY_KEY))
        pinned["claude"] = {**pinned["claude"], "digest": "0" * 64}
        self.journal.set_state(rp.EXECUTABLE_IDENTITY_KEY, pinned)
        result = rp.probe_cli_capability_manifest(journal=self.journal,
                                                  executables=self.executables())
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "provider_cli_drift")

    def test_a_recorded_FAILED_capability_probe_stops_the_run(self) -> None:
        self.journal.set_state(CAPABILITY_KEY, {
            "control_response_round_trip": {"name": "control_response_round_trip",
                                            "status": "FAILED", "detail": "not honoured"}})
        result = rp.probe_cli_capability_manifest(journal=self.journal,
                                                  executables=self.executables())
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "capability_probe_failed")

    def test_an_unidentifiable_executable_is_undetermined(self) -> None:
        result = rp.probe_cli_capability_manifest(
            journal=self.journal, executables={"claude": str(self.tmp / "gone.exe")})
        self.assertFalse(result.passes)
        self.assertFalse(result.known)
        self.assertEqual(result.reason_code, "executable_identity_unprovable")

    def test_an_unreadable_capability_record_fails_closed(self) -> None:
        self.journal.set_state(CAPABILITY_KEY, ["not", "a", "record"])
        result = rp.probe_cli_capability_manifest(journal=self.journal,
                                                  executables=self.executables())
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "capability_record_unreadable")


# --------------------------------------------------------------------------
# Journal-resident facts
# --------------------------------------------------------------------------


class UnreadableJournal:
    """A journal that cannot answer. Never read as "nothing is there"."""

    def get_state(self, *_a, **_k):
        raise OSError("the journal is unreadable")

    def set_state(self, *_a, **_k):
        raise OSError("the journal is unreadable")

    def open_asks(self):
        raise OSError("the journal is unreadable")

    def pending_effects(self):
        raise OSError("the journal is unreadable")


class JournalFactProbeTests(ProbeTestBase):
    def test_an_empty_ask_queue_passes(self) -> None:
        self.assertTrue(rp.probe_pending_requests(journal=self.journal).passes)

    def test_an_unanswered_approval_request_stops_the_run(self) -> None:
        self.journal.queue_ask(QueuedAsk(
            ask_id="ask-1", run_id="run-1", task_id="M0-T079",
            question="may I push?", request_digest="d", created_at_utc=to_utc_iso()))
        result = rp.probe_pending_requests(journal=self.journal)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "approval_pending")
        self.assertEqual(result.evidence["ask_ids"], ["ask-1"])

    def test_an_answered_request_no_longer_blocks(self) -> None:
        self.journal.queue_ask(QueuedAsk(
            ask_id="ask-1", run_id="run-1", task_id="M0-T079",
            question="may I push?", request_digest="d", created_at_utc=to_utc_iso()))
        self.journal.resolve_ask("ask-1", "no")
        self.assertTrue(rp.probe_pending_requests(journal=self.journal).passes)

    def test_an_unreadable_ask_queue_is_not_an_empty_one(self) -> None:
        result = rp.probe_pending_requests(journal=UnreadableJournal())
        self.assertFalse(result.passes)
        self.assertFalse(result.known)
        self.assertEqual(result.reason_code, "pending_requests_unreadable")

    def test_no_deadline_passes_and_an_outstanding_one_is_reported_not_masked(self) -> None:
        clock = lambda: 1_770_000_000.0  # noqa: E731 - a one-line injected clock
        self.assertTrue(rp.probe_scheduled_deadlines(journal=self.journal,
                                                     clock=clock).passes)
        self.journal.set_state(RESUME_NOT_BEFORE_KEY, "2099-01-01T00:00:00.000Z")
        result = rp.probe_scheduled_deadlines(journal=self.journal, clock=clock)
        # It PASSES the step and reports the deadline: recover_boot has a dedicated,
        # more useful verdict for it (`deadline_restored`), which a generic drift
        # failure here would mask.
        self.assertTrue(result.passes)
        self.assertTrue(result.evidence["outstanding"])

    def test_an_unparseable_deadline_is_undetermined(self) -> None:
        self.journal.set_state(RESUME_NOT_BEFORE_KEY, "soon-ish")
        result = rp.probe_scheduled_deadlines(journal=self.journal,
                                              clock=lambda: 1_770_000_000.0)
        self.assertFalse(result.passes)
        self.assertFalse(result.known)
        self.assertEqual(result.reason_code, "deadline_unparseable")

    def test_a_pending_effect_is_reported_and_left_to_the_ambiguous_verdict(self) -> None:
        self.journal.record_before_effect(
            action_id="act-1", effect_type="github_pr_comment", target="pr/1",
            expected_prior_state="", request_digest="d")
        result = rp.probe_last_external_effect(journal=self.journal)
        self.assertTrue(result.passes)
        self.assertEqual(result.evidence["unreconciled"], 1)
        # And recovery still classifies it AMBIGUOUS_EFFECT from its own read.
        context = rec.RecoveryContext(
            revalidation={step: True for step in rec.REVALIDATION_STEPS},
            pending_effect_ids=("act-1",))
        self.assertEqual(rec.classify(context).classification, rec.AMBIGUOUS_EFFECT)

    def test_an_unreadable_effect_journal_fails_closed(self) -> None:
        result = rp.probe_last_external_effect(journal=UnreadableJournal())
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "effects_unreadable")

    def test_a_surviving_recorded_child_is_refused(self) -> None:
        rec.record_launched_child(self.journal, pid=os.getpid(), role="worker")
        result = rp.probe_surviving_children(journal=self.journal)
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "child_unaccounted")
        self.assertIn(os.getpid(), result.evidence["surviving"])

    def test_no_recorded_children_passes(self) -> None:
        self.assertTrue(rp.probe_surviving_children(journal=self.journal).passes)

    def test_an_unreadable_child_record_is_not_read_as_nothing_running(self) -> None:
        result = rp.probe_surviving_children(journal=UnreadableJournal())
        self.assertFalse(result.passes)
        self.assertFalse(result.known)


# --------------------------------------------------------------------------
# Config identity
# --------------------------------------------------------------------------


class ConfigIdentityProbeTests(ProbeTestBase):
    def test_a_verified_binding_passes(self) -> None:
        config = self.tmp / "config.toml"
        config.write_text("[limits]\n", encoding="utf-8")
        self.assertTrue(rp.probe_config_identity(
            manifest_ok=True, config_path=str(config)).passes)

    def test_an_unnamed_config_is_refused(self) -> None:
        result = rp.probe_config_identity(manifest_ok=True, config_path="")
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "config_not_named")

    def test_a_missing_config_file_is_refused(self) -> None:
        result = rp.probe_config_identity(manifest_ok=True,
                                          config_path=str(self.tmp / "gone.toml"))
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "config_missing")

    def test_an_unverified_binding_is_refused(self) -> None:
        config = self.tmp / "config.toml"
        config.write_text("[limits]\n", encoding="utf-8")
        result = rp.probe_config_identity(manifest_ok=False,
                                          manifest_reason="manifest_stale",
                                          config_path=str(config))
        self.assertFalse(result.passes)
        self.assertEqual(result.reason_code, "config_binding_unverified")


# --------------------------------------------------------------------------
# The suite, and every single fact failing closed on its own
# --------------------------------------------------------------------------


class SuiteTests(ProbeTestBase):
    def inputs(self, **overrides) -> rp.ProbeInputs:
        config = self.tmp / "config.toml"
        config.write_text("[limits]\n", encoding="utf-8")
        params = dict(
            journal=self.journal, packet=self.packet(), repo_root=str(self.repo),
            worktree=self.worktree, packet_path="packet.json",
            executables={"claude": sys.executable, "codex": sys.executable},
            config_path=str(config), manifest_ok=True, git=self.git,
            clock=lambda: 1_770_000_000.0)
        params.update(overrides)
        return rp.ProbeInputs(**params)

    def test_a_healthy_checkout_establishes_every_step(self) -> None:
        self.write_ledger("M0-T079")
        report = rp.run_live_probes(self.inputs())
        self.assertEqual(report.failures(), (),
                         f"unexpected failures: {[r.step for r in report.failures()]}")
        answers = report.revalidation(rp.STEP_PROBES)
        self.assertEqual(set(answers), set(rp.STEP_PROBES))
        self.assertTrue(all(answers.values()))
        full = {**answers, "controller_manifest": True, "journal_integrity": True,
                "audit_chain": True}
        self.assertEqual(rec.classify(rec.RecoveryContext(revalidation=full)).classification,
                         rec.SAFE_CHECKPOINT)

    def test_every_probe_runs_even_after_an_earlier_one_fails(self) -> None:
        """The refusal names EVERY missing fact, not only the first one found."""
        report = rp.run_live_probes(self.inputs(git=unavailable_git()))
        steps = {r.step for r in report.results}
        self.assertEqual(steps, set(rp.STEP_PROBES) | set(rp.FOLDED_PROBES))
        self.assertIn("branch", report.to_dict()["failed"])
        self.assertIn("worktree", report.to_dict()["failed"])
        self.assertIn("git_and_remote_state", report.to_dict()["failed"])

    def test_each_missing_fact_on_its_own_makes_the_recovery_verdict_unsafe(self) -> None:
        """One failed step is enough - they do not have to accumulate."""
        self.write_ledger("M0-T079")
        baseline = rp.run_live_probes(self.inputs()).revalidation(rp.STEP_PROBES)
        for step in rp.STEP_PROBES:
            with self.subTest(step=step):
                answers = {**baseline, step: False, "controller_manifest": True,
                           "journal_integrity": True, "audit_chain": True}
                outcome = rec.classify(rec.RecoveryContext(revalidation=answers))
                self.assertEqual(outcome.classification, rec.UNSAFE_OR_DRIFTED)
                self.assertIn(step, outcome.failed_steps)
                self.assertEqual(
                    refusals.outcome_for_recovery(outcome.classification,
                                                  outcome.reason_code),
                    refusals.UNSAFE)


# --------------------------------------------------------------------------
# End to end through `start` - no provider, no network
# --------------------------------------------------------------------------

CONFIG_TOML = """
[codex]
allowed_models = ["codex-primary"]

[claude]
allowed_models = ["claude-worker"]

[controller]
default_mode = "shadow"
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


class StartProbeIntegrationTests(unittest.TestCase):
    """`start` refuses BEFORE any provider or GitHub contact when a fact is missing."""

    def setUp(self) -> None:
        from tools.agent_supervisor import cli
        from tools.agent_supervisor import process as proc

        self.cli = cli
        self.proc = proc
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.runtime = self.tmp / "runtime"
        self.config = self.tmp / "config.toml"
        self.config.write_text(CONFIG_TOML, encoding="utf-8")
        self.selection = self.tmp / "model_selection.toml"
        self.selection.write_text(SELECTION_TOML, encoding="utf-8")
        self.packet = self.tmp / "M0-T079.json"
        self.packet.write_text(json.dumps({
            "task_id": "M0-T079", "status": "in_progress",
            "allowed_paths": ["tools/agent_supervisor/**"],
            "forbidden_paths": [".github/**"],
            "stop_conditions": ["no bypass flags"]}), encoding="utf-8")
        from tools.agent_supervisor.manifest import generate_manifest, write_manifest
        self.manifest_path = write_manifest(
            generate_manifest(cli.PACKAGE_ROOT,
                              extra_files=(("config.toml", self.config),)),
            self.tmp / "controller_manifest.json")

    def make_git_checkout(self) -> None:
        tasks = self.repo / "project-control" / "tasks"
        tasks.mkdir(parents=True, exist_ok=True)
        (tasks / "M0-T079.json").write_text(
            json.dumps({"task_id": "M0-T079", "status": "in_progress", "blockers": []}),
            encoding="utf-8")
        env = {**os.environ,
               "GIT_AUTHOR_NAME": "supervisor-test",
               "GIT_AUTHOR_EMAIL": "test@example.invalid",
               "GIT_COMMITTER_NAME": "supervisor-test",
               "GIT_COMMITTER_EMAIL": "test@example.invalid"}
        for argv in (["init", "-q", "-b", "main"],
                     ["commit", "-q", "--allow-empty", "-m", "fixture"]):
            subprocess.run(["git", *argv], cwd=str(self.repo), check=True,
                           capture_output=True, env=env)

    def full_inputs(self) -> tuple[str, ...]:
        return ("start", "--mode", "shadow",
                "--claude-executable", sys.executable,
                "--codex-executable", sys.executable,
                "--task-packet", str(self.packet),
                "--config", str(self.config),
                "--manifest", str(self.manifest_path),
                "--model-selection", str(self.selection))

    def run_cli(self, *args: str) -> tuple[int, dict]:
        stdout = io.StringIO()
        argv = [*args, "--checkout", str(self.repo),
                "--runtime-base", str(self.runtime), "--json"]
        with contextlib.redirect_stdout(stdout):
            code = self.cli.main(list(argv))
        return code, json.loads(stdout.getvalue())

    @contextlib.contextmanager
    def host_containment(self, kind: str):
        original = self.cli.default_containment_kind
        self.cli.default_containment_kind = lambda: kind  # type: ignore[assignment]
        try:
            yield
        finally:
            self.cli.default_containment_kind = original  # type: ignore[assignment]

    def test_a_complete_command_line_no_longer_certifies_the_live_facts(self) -> None:
        """The reproduced defect, now fixed.

        Every input is named, so the OLD code set task_authority, branch,
        worktree, git_and_remote_state, auth, and cli_capability_manifest to True
        and dispatched. The directory is not a repository and there is no ledger
        record, so the live probes refuse.
        """
        code, payload = self.run_cli(*self.full_inputs())
        self.assertEqual(payload["missing_inputs"], [],
                         "the command line IS complete; that used to be enough")
        self.assertFalse(payload["dispatched"])
        self.assertEqual(payload["provider_calls_made"], 0)
        self.assertEqual(code, refusals.EXIT_CODES[refusals.UNSAFE])
        self.assertEqual(payload["refusal"]["outcome"], refusals.UNSAFE)
        failed = set(payload["probes"]["failed"])
        self.assertIn("task_authority", failed)
        self.assertIn("branch", failed)
        self.assertIn("worktree", failed)
        self.assertIn("git_and_remote_state", failed)

    def test_a_real_checkout_with_a_ledger_record_passes_the_probes(self) -> None:
        """The positive control: the probes are not simply always-fail."""
        self.make_git_checkout()
        with self.host_containment(self.proc.CONTAINMENT_JOB_OBJECT):
            _, payload = self.run_cli(*self.full_inputs())
        self.assertEqual(payload["probes"]["failed"], [], payload["probes"])
        self.assertTrue(payload["dispatched"], payload["stopped_because"])

    def test_a_pending_approval_request_stops_the_next_start(self) -> None:
        self.make_git_checkout()
        with self.host_containment(self.proc.CONTAINMENT_JOB_OBJECT):
            self.run_cli(*self.full_inputs())
        from tools.agent_supervisor.durable_state import DB_FILENAME, runtime_dir_for

        journal = DurableJournal(
            runtime_dir_for(self.repo, base=str(self.runtime)) / DB_FILENAME).open()
        try:
            journal.queue_ask(QueuedAsk(
                ask_id="ask-1", run_id="run-1", task_id="M0-T079",
                question="may I push?", request_digest="d",
                created_at_utc=to_utc_iso()))
        finally:
            journal.close()
        with self.host_containment(self.proc.CONTAINMENT_JOB_OBJECT):
            code, payload = self.run_cli(*self.full_inputs())
        self.assertFalse(payload["dispatched"])
        self.assertEqual(payload["provider_calls_made"], 0)
        self.assertEqual(code, refusals.EXIT_CODES[refusals.UNSAFE])
        self.assertIn("pending_requests", payload["probes"]["failed"])

    def test_an_unreadable_task_packet_is_a_typed_refusal_not_a_traceback(self) -> None:
        self.packet.write_text("{ not json", encoding="utf-8")
        code, payload = self.run_cli(*self.full_inputs())
        self.assertEqual(code, refusals.EXIT_CODES[refusals.STALE_STATE])
        self.assertEqual(payload["refusal"]["reason_code"], "task_packet_unreadable")
        self.assertFalse(payload["dispatched"])
        self.assertEqual(payload["provider_calls_made"], 0)

    def test_a_durable_emergency_stop_is_no_longer_dispatched_over(self) -> None:
        """SAFE_CHECKPOINT + a blocking flag used to pass the classification gate."""
        self.make_git_checkout()
        from tools.agent_supervisor.durable_state import DB_FILENAME, runtime_dir_for
        from tools.agent_supervisor.resume_scheduler import EMERGENCY_STOP_KEY

        runtime_dir = runtime_dir_for(self.repo, base=str(self.runtime))
        runtime_dir.mkdir(parents=True, exist_ok=True)
        journal = DurableJournal(runtime_dir / DB_FILENAME).open()
        try:
            journal.set_state(EMERGENCY_STOP_KEY, True)
        finally:
            journal.close()
        with self.host_containment(self.proc.CONTAINMENT_JOB_OBJECT):
            code, payload = self.run_cli(*self.full_inputs())
        self.assertFalse(payload["dispatched"])
        self.assertEqual(payload["provider_calls_made"], 0)
        self.assertEqual(code, refusals.EXIT_CODES[refusals.APPROVAL_REQUIRED])
        self.assertEqual(payload["refusal"]["reason_code"], "safe_but_forbidden")


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
