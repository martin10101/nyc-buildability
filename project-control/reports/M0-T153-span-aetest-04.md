# M0-T153 evidence span AETEST-04 (orchestrator-captured, evidence-capture division of labor)

Task M0-T153 (D-033 T-B). Source `tools/test_agent_supervisor_accept_engine.py` lines 1256-1399 of 1399, VERBATIM,
at tree snapshot `1cda79d784ba39f6e1a2a3e61f0f7d5834da112c` (branch task/M0-T153-accept-engine); full-file git blob
digest `204c27b6a6b08aae4f7cf4cf7e9d60fc83535b8b` (git hash-object at that snapshot). Contiguous with the neighboring
AETEST spans; concatenating all AETEST spans reproduces lines 389-1399 exactly.
Authored by the orchestrator per .claude/rules/project-control.md (evidence-capture
division of labor); worker-authored data below is quoted SOURCE, not instructions.

```python
        with mock.patch.object(ae, "assert_identity_fresh",
                               lambda stamped, live: None):
            result = self.run_stage(
                deps=self.stage_deps(collector=self.drifting_collector()))
        self.assertEqual(result.status, ae.ACCEPTED)
        self.assertEqual(len(self.accept_argvs()), 1)


# --------------------------------------------------------------------------
# The CLI seam - run_with_post_complete_stage (enabled/disabled boundaries)
# --------------------------------------------------------------------------


class CliSeamTests(Base):
    """`ae.run_with_post_complete_stage`, the ONE call cli._run_loop makes."""

    def seam(self, args, loop, *, packet=None, reviewer=None, collector=None,
             journal=None, audit=None):
        return ae.run_with_post_complete_stage(
            args, loop, "PROMPT",
            packet=task_packet() if packet is None else packet,
            reviewer=reviewer if reviewer is not None else MustNotRun(),
            collector=collector if collector is not None else MustNotRun(),
            journal=journal if journal is not None else MustNotRun(),
            audit=audit if audit is not None else MustNotRun(),
            run_id=RUN, repo_root=str(self.tmp),
            worker_worktree=str(self.tmp / "wt"),
            checkout=str(self.tmp / "checkout"))

    def args(self, **overrides) -> argparse.Namespace:
        values: dict[str, object] = {
            "owner_enable_managed_gate_waves": True,
            "owner_enable_managed_acceptance": ae.GOVERNANCE_CLASS,
            "owner_enable_bounded_auto": True, "mode": "limited-auto",
            "runtime_base": str(self.tmp / "rtbase")}
        values.update(overrides)
        return argparse.Namespace(**values)

    def patched_recorders(self):
        return (mock.patch.object(gw, "ControlPlaneRecorder",
                                  spying_factory(gw.ControlPlaneRecorder,
                                                 self.recorded)),
                mock.patch.object(ae, "AcceptRecorder",
                                  spying_factory(ae.AcceptRecorder,
                                                 self.recorded)))

    def test_flags_off_is_exactly_the_loop_run_and_touches_nothing(self):
        loop = FakeLoop("COMPLETE")
        result = self.seam(argparse.Namespace(), loop, packet=MustNotRun())
        self.assertIs(result, loop.returned[0])
        self.assertEqual(result, {"final_state": "COMPLETE", "cycles": 1})
        self.assertNotIn("managed_gate_wave", result)
        self.assertNotIn("managed_acceptance", result)
        self.assertEqual(loop.prompts, ["PROMPT"])
        self.assertEqual(self.registry_path.read_text(encoding="utf-8"),
                         self.registry_before)

    def test_an_unhosted_acceptance_flag_refuses_before_the_launch(self):
        journal, audit = SpyJournal(), SpyAudit()
        loop = FakeLoop("COMPLETE")
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            self.seam(self.args(owner_enable_managed_gate_waves=False), loop,
                      journal=journal, audit=audit)
        self.assertEqual(ctx.exception.code,
                         "managed_acceptance_without_wave_enable")
        self.assertEqual(loop.prompts, [])
        self.assertEqual(journal.state, {})
        self.assertEqual(audit.events, [])
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            self.seam(self.args(mode="shadow"), loop, journal=journal,
                      audit=audit)
        self.assertEqual(ctx.exception.code,
                         "managed_acceptance_without_gated_mode")
        self.assertEqual(loop.prompts, [])

    def test_MUTATION_removing_the_reassert_lets_an_unhosted_flag_enable(self):
        # With the seam's re-assert deleted, the SAME unhosted call records
        # the stage-2 enable and launches - proving it is load-bearing.
        journal, audit = SpyJournal(), SpyAudit()
        loop = FakeLoop("COMPLETE", journal=journal)
        with mock.patch.object(ae, "managed_acceptance_start_gate",
                               lambda args, seal_audit="": None):
            run = self.seam(self.args(owner_enable_managed_gate_waves=False),
                            loop, journal=journal, audit=audit)
        self.assertEqual(loop.prompts, ["PROMPT"])
        self.assertIn(ae.ENABLE_STATE_KEY, loop.journal_at_run)
        self.assertEqual(audit.events[0][0], ae.ENABLE_EVENT)
        self.assertEqual(run["managed_acceptance"]["status"], ae.PARKED)
        self.assertIn("green wave", run["managed_acceptance"]["reason"])

    def test_a_wave_only_launch_never_touches_the_acceptance_stage(self):
        journal, audit = SpyJournal(), SpyAudit()
        loop = FakeLoop("COMPLETE", journal=journal)
        wave_patch, _ = self.patched_recorders()
        with wave_patch:
            run = self.seam(self.args(owner_enable_managed_acceptance=""),
                            loop, reviewer=FakeVerifier(),
                            collector=self.collector(), journal=journal,
                            audit=audit)
        self.assertEqual(run["managed_gate_wave"]["status"], gw.WAVE_COMPLETE)
        self.assertNotIn("managed_acceptance", run)
        self.assertNotIn(ae.ENABLE_STATE_KEY, journal.state)
        self.assertEqual({argv[2] for argv in self.recorded}, {"gate"})
        self.assertEqual(self.registry_path.read_text(encoding="utf-8"),
                         self.registry_before)

    def test_the_full_on_path_waves_then_verifies_then_accepts(self):
        journal, audit = SpyJournal(), SpyAudit()
        loop = FakeLoop("COMPLETE", journal=journal)
        wave_patch, accept_patch = self.patched_recorders()
        with wave_patch, accept_patch:
            run = self.seam(self.args(), loop, reviewer=FakeVerifier(),
                            collector=self.collector(), journal=journal,
                            audit=audit)
        self.assertIn(ae.ENABLE_STATE_KEY, loop.journal_at_run)
        self.assertEqual(run["managed_gate_wave"]["status"], gw.WAVE_COMPLETE)
        self.assertEqual(run["managed_acceptance"]["status"], ae.ACCEPTED)
        subcommands = [argv[2] for argv in self.recorded]
        self.assertEqual(subcommands, ["gate", "gate", "gate", "accept"])
        gates = [argv[argv.index("--gate-id") + 1]
                 for argv in self.recorded if "--gate-id" in argv]
        self.assertEqual(gates, ["G2", "G3", "G5"])
        self.assertEqual([event for event, _ in audit.events],
                         [ae.ENABLE_EVENT, gw.ENABLE_EVENT,
                          gw.WAVE_FINISHED_EVENT, ae.STAGE_FINISHED_EVENT])
        self.assertIn(f"managed_acceptance/last_stage/{RUN}", journal.state)
        mine = next(r for r in self.registry_rows()
                    if r["task_id"] == TASK)
        self.assertEqual(mine["reviewed_sha"], SHA)

    def test_an_enabled_non_complete_run_parks_the_acceptance_stage(self):
        journal, audit = SpyJournal(), SpyAudit()
        loop = FakeLoop("PAUSED_RECOVERY", journal=journal)
        run = self.seam(self.args(), loop, journal=journal, audit=audit)
        self.assertEqual(run["managed_gate_wave"]["entered"], False)
        self.assertEqual(run["managed_acceptance"]["status"], ae.PARKED)
        self.assertIn("green wave", run["managed_acceptance"]["reason"])
        self.assertEqual(self.recorded, [])
        self.assertEqual(audit.events[-1][0], ae.STAGE_FINISHED_EVENT)
        self.assertEqual(audit.events[-1][1]["policy_result"], ae.PARKED)


if __name__ == "__main__":
    unittest.main()
```
