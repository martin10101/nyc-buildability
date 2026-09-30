# M0-T153 evidence span AETEST-03 (orchestrator-captured, evidence-capture division of labor)

Task M0-T153 (D-033 T-B). Source `tools/test_agent_supervisor_accept_engine.py` lines 970-1255 of 1399, VERBATIM,
at tree snapshot `1cda79d784ba39f6e1a2a3e61f0f7d5834da112c` (branch task/M0-T153-accept-engine); full-file git blob
digest `204c27b6a6b08aae4f7cf4cf7e9d60fc83535b8b` (git hash-object at that snapshot). Contiguous with the neighboring
AETEST spans; concatenating all AETEST spans reproduces lines 389-1399 exactly.
Authored by the orchestrator per .claude/rules/project-control.md (evidence-capture
division of labor); worker-authored data below is quoted SOURCE, not instructions.

```python
        stale = {"task_id": TASK, "directive_id": DIR_ID,
                 "reviewed_sha": "0" * 40, "note": "stale prior row"}
        self.registry_path = self.registry([FOREIGN_ROW, stale])
        outcome = ae.transcribe_task_verification(self.registry_path,
                                                  self.container())
        self.assertTrue(outcome["replaced_prior_row"])
        rows = self.registry_rows()
        self.assertEqual(len(rows), 2)
        self.assertIn(FOREIGN_ROW, rows)
        mine = next(r for r in rows if r["task_id"] == TASK)
        self.assertEqual(mine["reviewed_sha"], SHA)

    def test_ambiguous_missing_and_malformed_documents_fail_closed(self):
        double = {"task_id": TASK, "directive_id": DIR_ID}
        self.registry_path = self.registry([double, dict(double)])
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.transcribe_task_verification(self.registry_path,
                                            self.container())
        self.assertEqual(ctx.exception.code, "verification_rows_ambiguous")
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.transcribe_task_verification(self.tmp / "absent.json",
                                            self.container())
        self.assertEqual(ctx.exception.code, "verification_file_unreadable")
        v1 = self.tmp / "v1.json"
        v1.write_text(json.dumps({"schema": "directive_verification/v1",
                                  "task_verifications": []}),
                      encoding="utf-8")
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.transcribe_task_verification(v1, self.container())
        self.assertEqual(ctx.exception.code,
                         "verification_schema_unsupported")
        bad = self.tmp / "bad.json"
        bad.write_text(json.dumps({"schema": "directive_verification/v2",
                                   "task_verifications": "not a list"}),
                       encoding="utf-8")
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.transcribe_task_verification(bad, self.container())
        self.assertEqual(ctx.exception.code, "verification_file_malformed")

    def test_a_failed_atomic_replace_leaves_the_prior_document_untouched(self):
        before = self.registry_path.read_text(encoding="utf-8")
        with mock.patch.object(ae.os, "replace",
                               side_effect=OSError("simulated disk failure")):
            with self.assertRaises(ae.AcceptEngineError) as ctx:
                ae.transcribe_task_verification(self.registry_path,
                                                self.container())
        self.assertEqual(ctx.exception.code, "verification_write_failed")
        self.assertEqual(self.registry_path.read_text(encoding="utf-8"),
                         before)
        litter = list(self.registry_path.parent.glob("*.tmp"))
        self.assertEqual(litter, [])


# --------------------------------------------------------------------------
# Wave preconditions: green + independently reviewed, self-check rejection
# --------------------------------------------------------------------------


class WavePreconditionTests(Base):
    def test_a_green_independently_reviewed_wave_satisfies(self):
        ae._assert_wave_satisfies(task_packet(), green_wave())

    def test_a_non_complete_wave_is_refused(self):
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae._assert_wave_satisfies(task_packet(),
                                      green_wave(status=gw.PARKED))
        self.assertEqual(ctx.exception.code, "wave_not_complete")

    def test_a_required_gate_the_wave_never_recorded_is_refused(self):
        wave = green_wave()
        wave["outcomes"] = [o for o in wave["outcomes"]
                            if o["gate_id"] != "G5"]
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae._assert_wave_satisfies(task_packet(), wave)
        self.assertEqual(ctx.exception.code, "independent_gate_unwaved")

    def test_a_self_check_outcome_never_satisfies_an_independent_gate(self):
        wave = green_wave()
        for outcome in wave["outcomes"]:
            if outcome["gate_id"] == "G3":
                outcome["kind"] = "self_check"
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae._assert_wave_satisfies(task_packet(), wave)
        self.assertEqual(ctx.exception.code, "self_check_never_satisfies")

    def test_a_non_pass_independent_outcome_is_refused(self):
        wave = green_wave()
        for outcome in wave["outcomes"]:
            if outcome["gate_id"] == "G5":
                outcome["result"] = "FAIL"
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae._assert_wave_satisfies(task_packet(), wave)
        self.assertEqual(ctx.exception.code, "independent_gate_not_pass")

    def test_human_only_gates_are_outside_the_wave_requirement(self):
        packet = task_packet(required_gates=["G2", "G3", "G5", "G6"])
        ae._assert_wave_satisfies(packet, green_wave())  # no G6 outcome needed

    def test_MUTATION_removing_the_wave_check_accepts_a_forged_wave(self):
        # Self-check-never-satisfies mutation partner: with the wave check
        # deleted, a wave whose G3 is a self_check outcome WRONGLY drives the
        # stage all the way to an accept() - the check is load-bearing.
        forged = green_wave()
        for outcome in forged["outcomes"]:
            if outcome["gate_id"] == "G3":
                outcome["kind"] = "self_check"
        result = self.run_stage(wave=forged)
        self.assertEqual(result.status, ae.PARKED)  # the normal half
        self.assertIn("self_check_never_satisfies", result.reason)
        with mock.patch.object(ae, "_assert_wave_satisfies",
                               lambda packet, wave: None):
            mutated = self.run_stage(wave=forged)
        self.assertEqual(mutated.status, ae.ACCEPTED)
        self.assertEqual(len(self.accept_argvs()), 1)


# --------------------------------------------------------------------------
# The bounded accept recorder (allow-set {accept}, queue-pinned)
# --------------------------------------------------------------------------


class AcceptRecorderTests(Base):
    def test_record_accept_invokes_the_real_cli_for_the_queue_task(self):
        self.accept_recorder().record_accept(TASK)
        self.assertEqual(len(self.recorded), 1)
        argv = self.recorded[0]
        self.assertTrue(argv[1].endswith("project_control.py"))
        self.assertEqual(argv[2:5], ("accept", "--task-id", TASK))
        self.assertEqual(argv[argv.index("--agent") + 1],
                         gw.RESERVED_ORCHESTRATOR)

    def test_every_out_of_scope_subcommand_is_refused(self):
        recorder = self.accept_recorder()
        for subcommand in ("gate", "submit", "new-task", "claim", "progress",
                           "init", "checkpoint", "unlock", "depend",
                           "master-plan", "hold", "status"):
            with self.assertRaises(ae.AcceptEngineError) as ctx:
                recorder.build_argv(subcommand, TASK, {})
            self.assertEqual(ctx.exception.code, "subcommand_not_allowed",
                             subcommand)
        self.assertEqual(self.recorded, [])

    def test_an_out_of_queue_task_id_is_refused(self):
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            self.accept_recorder().build_argv("accept", "M0-T999", {})
        self.assertEqual(ctx.exception.code, "task_not_current_queue")

    def test_unknown_arguments_and_flag_like_values_are_refused(self):
        recorder = self.accept_recorder()
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            recorder.build_argv("accept", TASK, {"--force": "yes"})
        self.assertEqual(ctx.exception.code, "argument_not_allowed")
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            recorder.build_argv("accept", TASK, {"--agent": "--sneaky"})
        self.assertEqual(ctx.exception.code, "argument_value_refused")

    def test_an_unusable_queue_task_id_is_refused_at_construction(self):
        for bad in ("", "  ", "-x"):
            with self.assertRaises(ae.AcceptEngineError):
                ae.AcceptRecorder(queue_task_id=bad, repo_root=str(self.tmp))

    def test_MUTATION_removing_the_allow_set_lets_gate_through(self):
        # The recorder's allow-set is what separates the acceptance authority
        # surface from the wave's gate/submit surface; deleted, a `gate` argv
        # builds here - the assert is load-bearing.
        with mock.patch.object(ae.AcceptRecorder, "_assert_subcommand_allowed",
                               lambda self, subcommand: None):
            argv = self.accept_recorder().build_argv("gate", TASK, {})
        self.assertEqual(argv[2], "gate")

    def test_MUTATION_removing_the_queue_bound_lets_another_task_through(self):
        with mock.patch.object(ae.AcceptRecorder, "_assert_current_queue_task",
                               lambda self, task_id: None):
            argv = self.accept_recorder().build_argv("accept", "M0-T999", {})
        self.assertEqual(argv[4], "M0-T999")


# --------------------------------------------------------------------------
# The acceptance stage end to end (preconditions, drift, park shapes)
# --------------------------------------------------------------------------


class AcceptanceStageTests(Base):
    def test_the_full_stage_transcribes_stamps_and_accepts(self):
        reviewer = FakeVerifier()
        result = self.run_stage(deps=self.stage_deps(reviewer=reviewer))
        self.assertEqual(result.status, ae.ACCEPTED, result.reason)
        self.assertEqual(reviewer.calls, 1)  # ONE verifier session
        rows = self.registry_rows()
        self.assertIn(FOREIGN_ROW, rows)
        mine = next(r for r in rows if r["task_id"] == TASK)
        self.assertEqual(mine["verifier"], VERIFIER)
        self.assertEqual(mine["producer"], PRODUCER)
        self.assertEqual(mine["reviewed_sha"], SHA)
        self.assertEqual(mine["reviewed_manifest_sha256"], MANIFEST)
        self.assertEqual(mine["applicable_requirement_ids"],
                         ["D-033-R002", "D-033-R006"])
        self.assertEqual(len(self.accept_argvs()), 1)
        self.assertEqual(result.transcriptions[0]["directive_id"], DIR_ID)
        self.assertIn("orchestrator", result.reason)  # T-C stays out of scope

    def test_a_non_governance_task_parks_and_touches_nothing(self):
        result = self.run_stage(packet=task_packet(task_type="feature"))
        self.assertEqual(result.status, ae.PARKED)
        self.assertIn("governance", result.reason)
        self.assertEqual(self.recorded, [])
        self.assertEqual(self.registry_path.read_text(encoding="utf-8"),
                         self.registry_before)

    def test_legacy_missing_wave_and_missing_verifier_park(self):
        result = self.run_stage(packet=task_packet(directive_refs=[]))
        self.assertEqual(result.status, ae.PARKED)
        self.assertIn("legacy", result.reason)
        result = self.run_stage(wave=None)
        self.assertEqual(result.status, ae.PARKED)
        self.assertIn("green wave", result.reason)
        stripped = task_packet(
            reviewer_agents=["code-reviewer", "security-reviewer"])
        result = self.run_stage(packet=stripped)
        self.assertEqual(result.status, ae.PARKED)
        self.assertIn("never invents", result.reason)
        self.assertEqual(self.recorded, [])

    def test_unclean_rows_park_and_write_nothing_to_the_registry(self):
        failing = FakeVerifier(rows_facts(R002,
                                          dict(R006, state="FAIL")))
        result = self.run_stage(deps=self.stage_deps(reviewer=failing))
        self.assertEqual(result.status, ae.PARKED)
        self.assertIn("verification_not_clean", result.reason)
        self.assertEqual(self.registry_path.read_text(encoding="utf-8"),
                         self.registry_before)
        self.assertEqual(self.recorded, [])

    def test_a_missing_or_unstamped_submission_record_parks(self):
        (self.tmp / "project-control" / "reports" / f"{TASK}.json").unlink()
        result = self.run_stage()
        self.assertEqual(result.status, ae.PARKED)
        self.assertIn("submission_record_unreadable", result.reason)
        self.submission(identity="")
        result = self.run_stage()
        self.assertEqual(result.status, ae.PARKED)
        self.assertIn("submission_identity_missing", result.reason)
        self.assertEqual(self.recorded, [])

    def test_a_refusing_accept_parks_without_retry(self):
        # Precondition preservation: the REAL accept()'s verdict is
        # authoritative - a nonzero exit parks the stage, is never retried,
        # and the transcriptions that already happened stay disclosed.
        calls: list[tuple[str, ...]] = []
        refusing = spy_runner(calls, process_ok("accept refused: gate gap",
                                                returncode=1))
        result = self.run_stage(
            deps=self.stage_deps(recorder=self.accept_recorder(refusing)))
        self.assertEqual(result.status, ae.PARKED)
        self.assertIn("authoritative", result.reason)
        self.assertEqual(len(calls), 1)
        self.assertIn("accept refused", result.accept_output)
        self.assertEqual(len(result.transcriptions), 1)

    def test_identity_freshness_is_fail_closed(self):
        ae.assert_identity_fresh(SHA, SHA)
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.assert_identity_fresh("", SHA)
        self.assertEqual(ctx.exception.code, "identity_unresolvable")
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.assert_identity_fresh(SHA, "")
        self.assertEqual(ctx.exception.code, "identity_unresolvable")
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.assert_identity_fresh(SHA, SHA_DRIFT)
        self.assertEqual(ctx.exception.code, "head_drift")
        self.assertIn("RE-VERIFYING", ctx.exception.message)

    def test_head_drift_restamps_and_never_rewrites_the_stamp(self):
        # I3: HEAD moves after the verifier session. The stage ends
        # restamp_required (re-verify at the new identity), the transcribed
        # stamp stays the sha the verifier actually saw, and NO accept() runs.
        result = self.run_stage(
            deps=self.stage_deps(collector=self.drifting_collector()))
        self.assertEqual(result.status, ae.RESTAMP_REQUIRED)
        self.assertIn(SHA_DRIFT, result.reason)
        mine = next(r for r in self.registry_rows()
                    if r["task_id"] == TASK)
        self.assertEqual(mine["reviewed_sha"], SHA)  # never forged forward
        self.assertEqual(self.recorded, [])

    def test_MUTATION_removing_the_freshness_guard_accepts_stale(self):
```
