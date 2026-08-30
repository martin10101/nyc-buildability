#!/usr/bin/env python3
"""Operator-recovery restart-channel tests (F-2 class closure; D-024 Amendment 16).

Covers rows R303-R313 / acceptance scenarios AS-1..AS-8 of M0-T121:

* a deterministic, removal-sensitive REACHABILITY sweep that derives every
  operator-recovery trigger from the state-machine TRANSITIONS table and asserts
  each has at least one registered CLI command whose handler transitively fires it
  (AS-3, R309) - it is RED on the pre-fix registration set and GREEN on the fixed
  one, and deleting a recovery command's registration makes it fail again;
* the HALTED -> IDLE owner_explicit_restart surface against a reconstructed
  live-shape journal (AS-1), repeated invocation (AS-2), the stronger
  EMERGENCY_STOPPED acknowledgment and the ordinary surface refusing it (AS-4),
  the five fail-closed preconditions (AS-5), the durable emergency-stop flag
  (AS-6), lock contention / exactly-once (AS-7), and no policy/budget/audit side
  effects (AS-8);
* the third latent instance owner_answer_validated (WAIT_FOR_OWNER -> PREFLIGHT).

No live provider is ever involved and the real runtime dir is never touched: every
test constructs a temp journal and drives it through legal transitions only.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import inspect
import io
import json
import os
import pathlib
import sys
import tempfile
import textwrap
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import broker as bk  # noqa: E402
from tools.agent_supervisor import cli  # noqa: E402
from tools.agent_supervisor import external_effects as ex  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import recovery as rec  # noqa: E402
from tools.agent_supervisor import restart_channel as rc  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.durable_state import (  # noqa: E402
    DB_FILENAME,
    DurableJournal,
    checkout_key,
    runtime_dir_for,
)
from tools.agent_supervisor.locking import SingleInstanceLock  # noqa: E402
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402

CONTROLLER = "0.3.0-test"

# Legal transition paths to each blocking/terminal source state (each (state, trigger)).
PATH_TO_POLICY_CHECK = (
    (sm.PREFLIGHT, "start_command"),
    (sm.START_CLAUDE, "preflight_pass"),
    (sm.CLAUDE_RUNNING, "claude_process_started"),
    (sm.CHECKPOINT_RECEIVED, "valid_checkpoint_received"),
    (sm.COLLECT_EVIDENCE, "checkpoint_validated"),
    (sm.CODEX_REVIEW, "evidence_packet_built"),
    (sm.VALIDATE_DECISION, "decision_received"),
    (sm.POLICY_CHECK, "decision_schema_valid"),
)
PATH_TO_HALTED = PATH_TO_POLICY_CHECK + ((sm.HALTED, "decision_halt_unsafe"),)
PATH_TO_WAIT_FOR_OWNER = PATH_TO_POLICY_CHECK + ((sm.WAIT_FOR_OWNER, "tier_ask_blocking"),)
PATH_TO_EMERGENCY = (
    (sm.PREFLIGHT, "start_command"),
    (sm.START_CLAUDE, "preflight_pass"),
    (sm.CLAUDE_RUNNING, "claude_process_started"),
    (sm.EMERGENCY_STOPPED, "owner_emergency_stop"),
)


def all_pass_revalidation() -> dict[str, bool]:
    return {step: True for step in rec.REVALIDATION_STEPS}


# ==========================================================================
# AS-3 / R309: the deterministic, removal-sensitive reachability sweep
# ==========================================================================


class ReachabilityBase(unittest.TestCase):
    """Mechanical reachability: from TRANSITIONS derive the operator-recovery
    triggers; from a set of registered CLI handlers derive which triggers are
    fired by some handler's transitive closure. Nothing is hand-listed, so
    removing a command's registration removes its trigger from the reachable set.
    """

    #: The modules whose functions the closure walk descends into. A recovery
    #: EDGE is "reachable" only through a REGISTERED handler that (transitively,
    #: within these modules) names BOTH its trigger AND its source state.
    OWN_MODULES = frozenset({cli.__name__, rc.__name__})

    def operator_recovery_edges(self) -> set[tuple[str, str]]:
        """Every operator-recovery EDGE as a ``(state_from, trigger)`` pair: an
        edge that LEAVES a blocking-or-terminal state for a live (non-blocking,
        non-terminal) state under an explicit owner action. Derived purely from
        the state-machine table.

        EDGE granularity (not trigger granularity) is the point of R309: one
        trigger (`owner_explicit_restart`) fires TWO distinct edges (HALTED->IDLE
        and EMERGENCY_STOPPED->IDLE), so a trigger-level sweep would stay GREEN
        when one of those two edges lost its sole command surface while the
        sibling kept the trigger alive. Keying on ``(state_from, trigger)`` makes
        each edge accountable to a surface that constrains that source state."""
        blocking_or_terminal = sm.BLOCKING_STATES | sm.TERMINAL_STATES
        return {
            (t.state_from, t.trigger) for t in sm.TRANSITIONS
            if t.state_from in blocking_or_terminal
            and t.state_to not in blocking_or_terminal
            and t.trigger.startswith("owner_")
        }

    def registered_handlers(self) -> dict[str, object]:
        """command name -> handler func, from the built CLI parser."""
        parser = cli.build_parser()
        choices = parser._subparsers._group_actions[0].choices  # type: ignore[attr-defined]
        handlers: dict[str, object] = {}
        for name, sub in choices.items():
            func = sub.get_default("func")
            if func is not None:
                handlers[name] = func
        return handlers

    def _strip_docstrings(self, tree: ast.AST) -> ast.AST:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef, ast.Module)):
                body = getattr(node, "body", [])
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    node.body = body[1:]  # type: ignore[attr-defined]
        return tree

    def reachable_literals(self, handler_funcs) -> set[str]:
        """ALL string literals (docstrings excluded) reachable from the given
        handler funcs' transitive closure within `cli`+`restart_channel`. Constant
        NAMES are resolved to their string values via each function's own globals,
        so `expected_from_state=HALTED, trigger=OWNER_EXPLICIT_RESTART` contributes
        both "HALTED" and "owner_explicit_restart" even though each is a module
        constant reference. Not intersected with anything - the edge check does
        the binding, so a surface must name BOTH the source state AND the trigger.
        The shared helpers (`_locked`, `_fire_edge`, `evaluate_preconditions`)
        take the state and trigger as PARAMETERS and hardcode neither, so a
        handler only contributes the state/trigger of the ONE edge it wires."""
        seen: set[object] = set()
        worklist = list(handler_funcs)
        literals: set[str] = set()
        while worklist:
            fn = worklist.pop()
            if fn in seen:
                continue
            seen.add(fn)
            try:
                src = textwrap.dedent(inspect.getsource(fn))
                tree = self._strip_docstrings(ast.parse(src))
            except (OSError, TypeError, SyntaxError):
                continue
            g = getattr(fn, "__globals__", {})
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    literals.add(node.value)
                elif isinstance(node, ast.Name):
                    val = g.get(node.id)
                    if isinstance(val, str):
                        literals.add(val)
                    elif (callable(val)
                          and getattr(val, "__module__", "") in self.OWN_MODULES
                          and getattr(val, "__code__", None) is not None):
                        worklist.append(val)
        return literals

    def edge_has_surface(self, edge: tuple[str, str], handlers) -> bool:
        """True when SOME registered handler's closure names BOTH the edge's
        source state AND its trigger - i.e. a command surface that constrains that
        exact source state and fires that trigger. Per-handler (not unioned), so a
        sibling command that fires the same trigger from a DIFFERENT source state
        cannot stand in for a missing surface."""
        state_from, trigger = edge
        for handler in handlers:
            literals = self.reachable_literals([handler])
            if state_from in literals and trigger in literals:
                return True
        return False

    def uncovered_edges(self, handlers) -> set[tuple[str, str]]:
        return {edge for edge in self.operator_recovery_edges()
                if not self.edge_has_surface(edge, handlers)}


class ReachabilitySweep(ReachabilityBase):
    def test_the_recovery_edge_set_is_the_expected_owner_edges(self) -> None:
        # Guards the derivation itself: exactly the five owner recovery-resume
        # EDGES. Note owner_explicit_restart appears TWICE (HALTED and
        # EMERGENCY_STOPPED) - the distinction a trigger-level sweep loses. If the
        # table gains another owner recovery edge, this fails and forces the
        # enumeration to be revisited (R307/R308).
        self.assertEqual(
            self.operator_recovery_edges(),
            {("WAIT_FOR_OWNER", "owner_answer_validated"),
             ("WAIT_FOR_OWNER", "owner_approved_pending_prompt"),
             ("PAUSED_RECOVERY", "owner_cleared_pause"),
             ("EMERGENCY_STOPPED", "owner_explicit_restart"),
             ("HALTED", "owner_explicit_restart")})

    def test_every_operator_recovery_edge_has_a_registered_cli_surface(self) -> None:
        # GREEN on the fixed tree: every derived operator-recovery EDGE has a
        # registered command whose handler names both its source state and trigger.
        handlers = list(self.registered_handlers().values())
        uncovered = self.uncovered_edges(handlers)
        self.assertEqual(uncovered, set(),
                         f"operator-recovery edges with NO registered CLI surface: "
                         f"{sorted(uncovered)} (the F-2 defect class)")

    def test_pre_fix_registration_set_is_red(self) -> None:
        # RED reproduction WITHOUT a git write: restrict the discovered handler
        # set to exactly the pre-fix registrations (drop this task's three new
        # recovery commands). Reachability is a pure function of the registered
        # handlers + their delegated source, so this is the pre-fix tree's result:
        # the two owner_explicit_restart edges AND the discovered owner_answer_
        # validated edge are unreachable - precisely the defect M0-T107 reproduced
        # plus the latent third instance.
        handlers = self.registered_handlers()
        new_commands = {"owner-restart", "acknowledge-emergency-stop",
                        "resume-after-answer"}
        pre_fix = [fn for name, fn in handlers.items() if name not in new_commands]
        self.assertEqual(
            self.uncovered_edges(pre_fix),
            {("HALTED", "owner_explicit_restart"),
             ("EMERGENCY_STOPPED", "owner_explicit_restart"),
             ("WAIT_FOR_OWNER", "owner_answer_validated")},
            "the pre-fix registration set must leave exactly the three closed "
            "edges unreachable")

    def test_dropping_only_owner_restart_fails_the_sweep(self) -> None:
        # G4 MEDIUM: owner_explicit_restart fires TWO edges. Dropping ONLY
        # owner-restart must leave the HALTED->IDLE edge with no surface, even
        # though acknowledge-emergency-stop keeps the trigger alive for the
        # EMERGENCY_STOPPED edge.
        handlers = self.registered_handlers()
        kept = [fn for name, fn in handlers.items() if name != "owner-restart"]
        uncovered = self.uncovered_edges(kept)
        self.assertIn(("HALTED", "owner_explicit_restart"), uncovered)
        self.assertNotIn(("EMERGENCY_STOPPED", "owner_explicit_restart"), uncovered)

    def test_dropping_only_acknowledge_emergency_stop_fails_the_sweep(self) -> None:
        # The mirror: dropping ONLY acknowledge-emergency-stop must leave the
        # EMERGENCY_STOPPED->IDLE edge uncovered while HALTED->IDLE stays covered.
        handlers = self.registered_handlers()
        kept = [fn for name, fn in handlers.items()
                if name != "acknowledge-emergency-stop"]
        uncovered = self.uncovered_edges(kept)
        self.assertIn(("EMERGENCY_STOPPED", "owner_explicit_restart"), uncovered)
        self.assertNotIn(("HALTED", "owner_explicit_restart"), uncovered)

    def test_dropping_only_resume_after_answer_fails_the_sweep(self) -> None:
        # The discovered third edge has a single surface: dropping it uncovers
        # the WAIT_FOR_OWNER->PREFLIGHT owner_answer_validated edge (and NOT the
        # held-prompt owner_approved_pending_prompt edge, a different surface).
        handlers = self.registered_handlers()
        kept = [fn for name, fn in handlers.items() if name != "resume-after-answer"]
        uncovered = self.uncovered_edges(kept)
        self.assertIn(("WAIT_FOR_OWNER", "owner_answer_validated"), uncovered)
        self.assertNotIn(("WAIT_FOR_OWNER", "owner_approved_pending_prompt"),
                         uncovered)

    def test_parser_registers_the_three_recovery_commands(self) -> None:
        # The real parser exposes each new command as a choice with a handler.
        handlers = self.registered_handlers()
        for name in ("owner-restart", "acknowledge-emergency-stop",
                     "resume-after-answer"):
            self.assertIn(name, handlers, f"{name} not registered on build_parser()")
            self.assertTrue(callable(handlers[name]))


# ==========================================================================
# Functional surfaces: AS-1..AS-8
# ==========================================================================


class RestartChannelBase(unittest.TestCase):
    def setUp(self) -> None:
        self._checkout_tmp = tempfile.TemporaryDirectory()
        self._base_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._checkout_tmp.cleanup)
        self.addCleanup(self._base_tmp.cleanup)
        self.checkout = pathlib.Path(self._checkout_tmp.name).resolve()
        self.base = pathlib.Path(self._base_tmp.name).resolve()
        self.runtime = runtime_dir_for(self.checkout, base=self.base)
        self.runtime.mkdir(parents=True)
        self.journal = DurableJournal(self.runtime / DB_FILENAME).open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.runtime / cli.AUDIT_FILENAME, fsync=False)
        self.authority = pol.TaskAuthority(
            task_id="M0-T107", stage="phase4",
            repo_root=str(self.checkout), worktree=str(self.checkout),
            branch="control/D-024-fable-codex-loop", status="in_progress",
            active=True)

    # -- construction helpers (setup, NEVER the command under test) ----------

    def drive(self, *edges: tuple[str, str]) -> None:
        machine = StateMachine(self.journal, self.audit, "run_M0_T107")
        for state_to, trigger in edges:
            machine.transition(state_to, trigger)

    def record_safe_checkpoint(self) -> None:
        """Run the read-only S11.5 recover-boot classification exactly as the
        preceding `start` did in the live M0-T107 sequence: SAFE_CHECKPOINT,
        recorded, journal state unchanged."""
        outcome = rec.recover_boot(
            journal=self.journal, lock=None,
            revalidation=all_pass_revalidation(), audit=self.audit)
        self.assertEqual(outcome.classification, rec.SAFE_CHECKPOINT)

    def add_denied_asks(self, n: int) -> None:
        broker = bk.ApprovalBroker(self.journal, self.audit,
                                   authority=self.authority, mode="shadow",
                                   run_id="run_M0_T107")
        for i in range(n):
            request = bk.build_request(
                tool_name="Bash", tool_input={"command": f"echo {i}"},
                authority=self.authority, target_paths=(),
                head_sha="a" * 40, origin_main_sha="b" * 40, session_id="sess-1",
                request_id=f"req_denied_{i}")
            decision = pol.PolicyDecision(
                tier=pol.ASK, reason_code="scope", reason="needs the owner",
                rule_id="S4.3", classification="scope")
            broker.defer(request, decision)
            outcome = broker.deny_request(request.request_id, request.digest())
            self.assertEqual(outcome.reason_code, "owner_denied")

    def add_pending_ask(self) -> None:
        broker = bk.ApprovalBroker(self.journal, self.audit,
                                   authority=self.authority, mode="shadow",
                                   run_id="run_M0_T107")
        request = bk.build_request(
            tool_name="Bash", tool_input={"command": "echo open"},
            authority=self.authority, target_paths=(),
            head_sha="a" * 40, origin_main_sha="b" * 40, session_id="sess-1",
            request_id="req_open")
        decision = pol.PolicyDecision(
            tier=pol.ASK, reason_code="scope", reason="needs the owner",
            rule_id="S4.3", classification="scope")
        broker.defer(request, decision)

    def begin_pending_effect(self) -> None:
        effects = ex.ExternalEffectJournal(self.journal, audit=self.audit)
        effects.begin(
            effect_type="git_push_task_branch",
            target="origin/task/M0-T107", task_id="M0-T107",
            request_digest="d1", logical_sequence="1",
            prior_state_reader=lambda: "absent")

    def record_surviving_child(self) -> None:
        # This live interpreter is a determined-alive pid, so it counts as a
        # recorded surviving child.
        rec.record_launched_child(self.journal, pid=os.getpid(), role="worker",
                                  start_token="")

    def new_lock(self, pid: int | None = None) -> SingleInstanceLock:
        return SingleInstanceLock(self.runtime, checkout_key=checkout_key(self.checkout),
                                  controller_version=CONTROLLER, pid=pid)

    def build_halted_live_shape(self, denied_asks: int = 3) -> None:
        """The reconstructed live journal shape: HALTED via decision_halt_unsafe,
        `denied_asks` resolved/denied asks in history, a recorded SAFE_CHECKPOINT
        recovery, intact audit chain."""
        self.drive(*PATH_TO_HALTED)
        if denied_asks:
            self.add_denied_asks(denied_asks)
        self.record_safe_checkpoint()
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)
        self.assertTrue(self.audit.verify_chain().ok)

    def transition_count(self) -> int:
        return len(self.journal.transitions())


class OwnerRestartHappyPath(RestartChannelBase):
    def test_AS1_live_shape_journal_restarts_truthfully(self) -> None:
        self.build_halted_live_shape(denied_asks=3)
        before = self.transition_count()
        self.assertTrue(self.audit.verify_chain().ok)

        result = rc.owner_restart(self.journal, self.audit, self.new_lock())

        self.assertTrue(result.ok, result.message)
        self.assertEqual((result.state_from, result.state_to, result.trigger),
                         (sm.HALTED, sm.IDLE, "owner_explicit_restart"))
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.IDLE)
        # exactly one transition applied
        self.assertEqual(self.transition_count(), before + 1)
        # audit chain still verifies AND a durable owner-restart event exists
        self.assertTrue(self.audit.verify_chain().ok)
        events = [json.loads(line) for line in
                  (self.runtime / cli.AUDIT_FILENAME).read_text().splitlines()]
        kinds = [e["event_type"] for e in events]
        self.assertIn("operator_owner_restart", kinds)
        self.assertIn("state_transition", kinds)
        # the three denied asks remain answered history, never erased
        self.assertEqual(len(bk.owner_unanswered_asks(self.journal)), 0)

    def test_AS2_repeated_invocation_refuses_cleanly(self) -> None:
        self.build_halted_live_shape(denied_asks=1)
        first = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertTrue(first.ok)
        count_after_first = self.transition_count()

        second = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(second.ok)
        self.assertEqual(second.code, "wrong_state")
        # no second transition, state unchanged, chain intact
        self.assertEqual(self.transition_count(), count_after_first)
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.IDLE)
        self.assertTrue(self.audit.verify_chain().ok)


class OwnerRestartPreconditions(RestartChannelBase):
    def test_AS5a_open_ask_refuses(self) -> None:
        self.drive(*PATH_TO_HALTED)
        self.record_safe_checkpoint()
        self.add_pending_ask()
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "open_asks")
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)

    def test_unreadable_ask_queue_refuses_never_treated_as_empty(self) -> None:
        # G4 LOW: an ask-queue read error is the caller's fail-closed decision
        # (`asks_unreadable`), never an empty queue that would let a restart run.
        self.drive(*PATH_TO_HALTED)
        self.record_safe_checkpoint()

        def _boom():
            raise RuntimeError("queue read failed")
        self.journal.open_asks = _boom  # type: ignore[method-assign]
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "asks_unreadable")
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)

    def test_AS5b_pending_effect_refuses(self) -> None:
        self.drive(*PATH_TO_HALTED)
        self.record_safe_checkpoint()
        self.begin_pending_effect()
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "pending_effects")
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)

    def test_AS5c_surviving_child_refuses(self) -> None:
        self.drive(*PATH_TO_HALTED)
        self.record_safe_checkpoint()
        self.record_surviving_child()
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "surviving_children")
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)

    def test_AS5d_provider_identity_drift_refuses(self) -> None:
        self.drive(*PATH_TO_HALTED)
        # A recorded recovery that failed the pinned provider-CLI identity step.
        drifted = rec.RecoveryOutcome(
            rec.UNSAFE_OR_DRIFTED, sm.PAUSED_RECOVERY, "recovery_unsafe_or_drifted",
            "unsafe_or_drifted", "provider CLI drift", False,
            failed_steps=("cli_capability_manifest",))
        self.journal.set_state(rec.LAST_RECOVERY_KEY, drifted.to_dict())
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "provider_identity_drift")
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)

    def test_AS5e_unsafe_recovery_classification_refuses(self) -> None:
        self.drive(*PATH_TO_HALTED)
        drifted = rec.RecoveryOutcome(
            rec.UNSAFE_OR_DRIFTED, sm.PAUSED_RECOVERY, "recovery_unsafe_or_drifted",
            "unsafe_or_drifted", "a competing writer was detected", False,
            failed_steps=("git_and_remote_state",))
        self.journal.set_state(rec.LAST_RECOVERY_KEY, drifted.to_dict())
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "unsafe_recovery_classification")
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)

    def test_recovery_unclassified_refuses(self) -> None:
        # A HALTED journal with NO recorded recovery classification fails closed.
        self.drive(*PATH_TO_HALTED)
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "recovery_unclassified")

    def test_AS6_durable_emergency_stop_flag_refuses(self) -> None:
        self.build_halted_live_shape(denied_asks=0)
        rec.set_emergency_stop(self.journal, reason="operator test", audit=self.audit)
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "emergency_stop_flag_set")
        # the flag is NOT cleared by the refusal
        self.assertTrue(rec.DurableFlags.read(self.journal).emergency_stop)
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)

    def test_ordinary_restart_refuses_emergency_stopped_state(self) -> None:
        self.drive(*PATH_TO_EMERGENCY)
        self.record_safe_checkpoint()
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "wrong_state")


class EmergencyStopAcknowledgment(RestartChannelBase):
    def _emergency_journal(self) -> None:
        self.drive(*PATH_TO_EMERGENCY)
        # An emergency stop leaves the durable FLAG set; the owner clears it with
        # `stop --clear` before acknowledging the STATE. Model that resolved flag.
        self.record_safe_checkpoint()

    def test_AS4_ordinary_surface_refuses_emergency_stopped(self) -> None:
        self._emergency_journal()
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "wrong_state")

    def test_AS4_missing_acknowledgment_refuses(self) -> None:
        self._emergency_journal()
        result = rc.acknowledge_emergency_stop(
            self.journal, self.audit, self.new_lock(),
            acknowledged=False, confirm_token=rc.emergency_ack_token(self.journal))
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "acknowledgment_required")
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.EMERGENCY_STOPPED)

    def test_AS4_wrong_token_refuses(self) -> None:
        self._emergency_journal()
        result = rc.acknowledge_emergency_stop(
            self.journal, self.audit, self.new_lock(),
            acknowledged=True, confirm_token="deadbeefdeadbeef")
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "confirm_token_mismatch")
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.EMERGENCY_STOPPED)

    def test_AS4_correct_token_and_ack_exits_emergency(self) -> None:
        self._emergency_journal()
        token = rc.emergency_ack_token(self.journal)
        self.assertTrue(token)
        before = self.transition_count()
        result = rc.acknowledge_emergency_stop(
            self.journal, self.audit, self.new_lock(),
            acknowledged=True, confirm_token=token)
        self.assertTrue(result.ok, result.message)
        self.assertEqual((result.state_from, result.state_to, result.trigger),
                         (sm.EMERGENCY_STOPPED, sm.IDLE, "owner_explicit_restart"))
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.IDLE)
        self.assertEqual(self.transition_count(), before + 1)
        self.assertTrue(self.audit.verify_chain().ok)

    def test_AS4_ack_refuses_while_emergency_flag_set(self) -> None:
        self._emergency_journal()
        token = rc.emergency_ack_token(self.journal)
        rec.set_emergency_stop(self.journal, reason="still set", audit=self.audit)
        result = rc.acknowledge_emergency_stop(
            self.journal, self.audit, self.new_lock(),
            acknowledged=True, confirm_token=token)
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "emergency_stop_flag_set")

    def test_ack_refuses_non_emergency_state(self) -> None:
        # The stronger surface only fires from EMERGENCY_STOPPED.
        self.build_halted_live_shape(denied_asks=0)
        result = rc.acknowledge_emergency_stop(
            self.journal, self.audit, self.new_lock(),
            acknowledged=True, confirm_token="anything")
        self.assertFalse(result.ok)
        self.assertIn(result.code, ("no_emergency_provenance", "wrong_state"))


class OwnerAnswerResume(RestartChannelBase):
    def test_wait_for_owner_resumes_to_preflight(self) -> None:
        self.drive(*PATH_TO_WAIT_FOR_OWNER)
        self.record_safe_checkpoint()
        before = self.transition_count()
        result = rc.owner_answer_resume(self.journal, self.audit, self.new_lock())
        self.assertTrue(result.ok, result.message)
        self.assertEqual((result.state_from, result.state_to, result.trigger),
                         (sm.WAIT_FOR_OWNER, sm.PREFLIGHT, "owner_answer_validated"))
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.PREFLIGHT)
        self.assertEqual(self.transition_count(), before + 1)
        self.assertTrue(self.audit.verify_chain().ok)

    def test_owner_answer_resume_refuses_open_ask(self) -> None:
        self.drive(*PATH_TO_WAIT_FOR_OWNER)
        self.record_safe_checkpoint()
        self.add_pending_ask()
        result = rc.owner_answer_resume(self.journal, self.audit, self.new_lock())
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "open_asks")


class LockContentionAndExactlyOnce(RestartChannelBase):
    def test_AS7_live_foreign_lock_refuses(self) -> None:
        self.build_halted_live_shape(denied_asks=0)
        # A live foreign controller (the parent process pid, definitely alive and
        # a different pid) holds the lock.
        foreign = self.new_lock(pid=os.getppid())
        foreign.acquire()
        try:
            result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        finally:
            foreign.release()
        self.assertFalse(result.ok)
        self.assertEqual(result.code, "lock_held")
        # no transition happened
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.HALTED)

    def test_AS7_exactly_once_across_sequential_invocations(self) -> None:
        self.build_halted_live_shape(denied_asks=0)
        before = self.transition_count()
        r1 = rc.owner_restart(self.journal, self.audit, self.new_lock())
        r2 = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertTrue(r1.ok)
        self.assertFalse(r2.ok)
        # exactly one HALTED->IDLE transition across both invocations
        self.assertEqual(self.transition_count(), before + 1)

    def test_AS7_stale_lock_is_taken_over_not_refused(self) -> None:
        # A stale lock (a dead prior controller) is honestly taken over, so a
        # legitimate restart is never spuriously refused.
        self.build_halted_live_shape(denied_asks=0)
        stale = self.new_lock(pid=999_999_998)  # not a live pid
        # write a stale lock record directly
        stale.acquire()
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertTrue(result.ok, result.message)


class NoSideEffects(RestartChannelBase):
    def test_AS8_only_state_and_trigger_keys_change(self) -> None:
        self.build_halted_live_shape(denied_asks=2)
        before = self.journal.all_state()
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertTrue(result.ok)
        after = self.journal.all_state()

        changed = {k for k in set(before) | set(after)
                   if before.get(k) != after.get(k)}
        # ONLY the transition's own two keys move; no flag, budget, counter, or
        # ask record is touched.
        self.assertEqual(changed, {sm.STATE_KEY, sm.LAST_TRIGGER_KEY})
        # every other key is byte-identical
        for key in set(before) - {sm.STATE_KEY, sm.LAST_TRIGGER_KEY}:
            self.assertEqual(before[key], after[key], key)

    def test_AS8_no_flag_or_budget_key_is_reset(self) -> None:
        self.build_halted_live_shape(denied_asks=0)
        # set a manual pause flag; the restart must leave it exactly as it is
        rec.set_manual_pause(self.journal, paused=True, reason="test",
                             audit=self.audit)
        result = rc.owner_restart(self.journal, self.audit, self.new_lock())
        self.assertTrue(result.ok)
        self.assertTrue(rec.DurableFlags.read(self.journal).manual_pause)


class CliSurfaceEndToEnd(RestartChannelBase):
    """Drive the real registered CLI handlers (their own journal connection) so
    the argparse wiring and the lock/emit path are exercised, not only the
    module functions."""

    def _args(self, **extra) -> argparse.Namespace:
        base = dict(checkout=str(self.checkout), runtime_base=str(self.base),
                    json=True)
        base.update(extra)
        return argparse.Namespace(**base)

    def _run(self, func, **extra) -> tuple[int, dict]:
        # the CLI opens its own connection; close ours to avoid a writer clash,
        # then reopen for inspection.
        self.journal.close()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = func(self._args(**extra))
        self.journal = DurableJournal(self.runtime / DB_FILENAME).open()
        self.addCleanup(self.journal.close)  # the reopened connection must close too
        text = out.getvalue().strip()
        payload = json.loads(text) if text else {}
        return code, payload

    def test_cmd_owner_restart_end_to_end(self) -> None:
        self.build_halted_live_shape(denied_asks=1)
        code, payload = self._run(rc.cmd_owner_restart)
        self.assertEqual(code, 0)
        self.assertTrue(payload.get("restarted"))
        self.assertEqual(payload.get("state_to"), sm.IDLE)
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.IDLE)

    def test_cmd_owner_restart_refuses_fresh_journal(self) -> None:
        # a brand-new journal is IDLE, not HALTED
        code, payload = self._run(rc.cmd_owner_restart)
        self.assertEqual(code, 1)

    def test_cmd_acknowledge_emergency_stop_requires_token(self) -> None:
        self.drive(*PATH_TO_EMERGENCY)
        self.record_safe_checkpoint()
        code, _ = self._run(rc.cmd_acknowledge_emergency_stop,
                            acknowledge_emergency_stop=True,
                            confirm_emergency_token="wrong")
        self.assertEqual(code, 1)
        self.assertEqual(self.journal.get_state(sm.STATE_KEY), sm.EMERGENCY_STOPPED)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
