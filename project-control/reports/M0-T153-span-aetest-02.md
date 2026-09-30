# M0-T153 evidence span AETEST-02 (orchestrator-captured, evidence-capture division of labor)

Task M0-T153 (D-033 T-B). Source `tools/test_agent_supervisor_accept_engine.py` lines 674-969 of 1399, VERBATIM,
at tree snapshot `1cda79d784ba39f6e1a2a3e61f0f7d5834da112c` (branch task/M0-T153-accept-engine); full-file git blob
digest `204c27b6a6b08aae4f7cf4cf7e9d60fc83535b8b` (git hash-object at that snapshot). Contiguous with the neighboring
AETEST spans; concatenating all AETEST spans reproduces lines 389-1399 exactly.
Authored by the orchestrator per .claude/rules/project-control.md (evidence-capture
division of labor); worker-authored data below is quoted SOURCE, not instructions.

```python
        self.assertEqual(rows[0]["state"], "PASS")

    def test_an_explicit_empty_applicable_set_attestation_is_a_row(self):
        rows = self.extract([fact_of({"directive_id": DIR_ID,
                                      "applicable_requirement_ids": []})])
        self.assertEqual(rows, [{"directive_id": DIR_ID,
                                 "applicable_requirement_ids": []}])

    def test_non_schema_shaped_entries_are_refused(self):
        self.assert_refused(["a bare string entry"], "malformed_fact")
        self.assert_refused([{"fact": "x", "extra": "y"}], "malformed_fact")
        self.assert_refused([{"fact": 7}], "malformed_fact")
        self.assert_refused([dict(R002)], "malformed_fact")  # legacy rich row

    def test_near_rows_and_malformed_payloads_fail_closed(self):
        self.assert_refused([{"fact": f"see {ae.ROW_SENTINEL}{{}} above"}],
                            "malformed_row")
        self.assert_refused([{"fact": ae.ROW_SENTINEL + "{not json"}],
                            "malformed_row")
        self.assert_refused([{"fact": ae.ROW_SENTINEL + "null"}],
                            "malformed_row")
        self.assert_refused([{"fact": ae.ROW_SENTINEL + "[1, 2]"}],
                            "malformed_row")
        incomplete = {"directive_id": DIR_ID, "state": "PASS"}
        self.assert_refused([fact_of(incomplete)], "malformed_row")
        stateless = {"directive_id": DIR_ID, "requirement_id": "D-033-R002"}
        self.assert_refused([fact_of(stateless)], "malformed_row")

    def test_a_row_for_an_uncited_directive_is_contamination(self):
        stray = dict(R002, directive_id="D-024",
                     requirement_id="D-024-R001")
        self.assert_refused([fact_of(R002), fact_of(stray)],
                            "row_for_uncited_directive")
        self.assert_refused([{"fact": ae.ROW_SENTINEL + "{}"}],
                            "row_for_uncited_directive")

    def test_absent_or_empty_row_sets_fail_closed(self):
        self.assert_refused([{"fact": "prose only"}], "no_verification_rows")
        self.assert_refused([], "no_verification_rows")
        dispatch = self.vdispatch()
        record = self.vrecord(dispatch)
        record.decision = {"decision": "APPROVE"}  # no verified_facts at all
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.extract_rows(dispatch, record)
        self.assertEqual(ctx.exception.code, "no_verification_rows")

    def test_an_unadjudicable_verifier_is_never_a_verification(self):
        self.assert_refused(None, "verifier_unavailable",
                            decision="UNADJUDICABLE")

    def padded_facts(self, target_bytes: int) -> list[dict]:
        """One valid row plus a prose filler sized so the RAW serialized
        verified_facts payload is exactly `target_bytes` UTF-8 bytes."""
        def payload(n: int) -> list[dict]:
            return [fact_of(R002), {"fact": "p" * n}]
        base = len(json.dumps(payload(0),
                              ensure_ascii=False).encode("utf-8"))
        self.assertGreaterEqual(target_bytes, base)
        facts = payload(target_bytes - base)
        measured = len(json.dumps(facts, ensure_ascii=False).encode("utf-8"))
        self.assertEqual(measured, target_bytes)
        return facts

    def test_the_64k_ceiling_admits_exactly_the_bound_and_refuses_past_it(self):
        rows = self.extract(self.padded_facts(ae.ROWS_CEILING_BYTES))
        self.assertEqual(rows[0]["requirement_id"], "D-033-R002")
        self.assert_refused(self.padded_facts(ae.ROWS_CEILING_BYTES + 1),
                            "rows_over_ceiling")


# --------------------------------------------------------------------------
# The live decision boundary: validate_decision-admitted rows reach accept()
# --------------------------------------------------------------------------


def complete_decision_payload(**overrides) -> dict:
    """One COMPLETE raw decision: every schema-required field, an allowed
    enum value, and the correlation ids the dispatch expects."""
    payload = {
        "schema_version": "1.0.0", "decision": "COMPLETE",
        "reviewed_task_id": TASK, "reviewed_checkpoint_id": CP,
        "verified_repo_head": SHA, "verified_origin_main": "",
        "model_used": "fake-review-model",
        "verified_facts": rows_facts(R002, R006),
        "unverified_claims": [], "blocking_findings": [],
        "reason_codes": [], "next_claude_prompt": "",
        "owner_question": "", "rotation_reason": "",
        "evidence_refs": [{"path": "project-control/reports/"
                                   "M0-T153-producer-report.md"}],
    }
    payload.update(overrides)
    return payload


class ValidatedDecisionVerifier:
    """Mirrors the LIVE reviewer boundary (codex_reviewer.CodexReviewer):
    review() validates the RAW payload with the real validate_decision,
    bound to the exact correlation ids conduct_ephemeral_review passes,
    and the outcome carries the resulting CodexDecision - never a
    hand-built decision surface the live boundary would refuse."""

    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls = 0

    def review(self, packet, *, expected_task_id: str = "",
               expected_checkpoint_id: str = "", **kwargs) -> FakeOutcome:
        self.calls += 1
        decision = cr.validate_decision(
            self.payload, expected_task_id=expected_task_id,
            expected_checkpoint_id=expected_checkpoint_id)
        return FakeOutcome(decision)


class RealDecisionBoundaryTests(Base):
    """The verifier-boundary regression: the row path proven with a decision
    the REAL decision validator admits, riding the SUPPORTED seam
    (run_acceptance_stage -> dispatch_verification ->
    conduct_ephemeral_review -> extract_rows -> worst-of merge ->
    transcription -> the recorded accept()), never a fake-only shape."""

    def test_the_complete_decision_passes_the_real_validator(self):
        decision = cr.validate_decision(
            complete_decision_payload(), expected_task_id=TASK,
            expected_checkpoint_id=CP)
        self.assertEqual(decision.decision, "COMPLETE")
        schema = json.loads(
            (REPO / "tools" / "agent_supervisor" / "schemas"
             / "codex_decision.schema.json").read_text(encoding="utf-8"))
        self.assertIn(decision.decision,
                      schema["properties"]["decision"]["enum"])

    def test_the_legacy_fake_value_and_incomplete_decisions_are_refused(self):
        # WHY this regression exists: 'APPROVE' (this suite's original fake
        # decision value) and under-specified decisions can NEVER arrive
        # through the live validate_decision boundary; a suite proven only
        # against them would prove a path no real verifier session takes.
        with self.assertRaises(cr.ReviewError) as ctx:
            cr.validate_decision(
                complete_decision_payload(decision="APPROVE"))
        self.assertEqual(ctx.exception.code, "bad_decision")
        incomplete = complete_decision_payload()
        del incomplete["model_used"]
        with self.assertRaises(cr.ReviewError) as ctx:
            cr.validate_decision(incomplete)
        self.assertEqual(ctx.exception.code, "missing_fields")
        with self.assertRaises(cr.ReviewError) as ctx:
            cr.validate_decision(complete_decision_payload(evidence_refs=[]))
        self.assertEqual(ctx.exception.code, "missing_completion_evidence")

    def test_validator_admitted_rows_reach_the_acceptance_stage(self):
        reviewer = ValidatedDecisionVerifier(complete_decision_payload())
        result = self.run_stage(deps=self.stage_deps(reviewer=reviewer))
        self.assertEqual(result.status, ae.ACCEPTED, result.reason)
        self.assertEqual(reviewer.calls, 1)  # ONE validated verifier session
        self.assertTrue(result.verifier_record_digest)
        mine = next(r for r in self.registry_rows()
                    if r["task_id"] == TASK)
        self.assertEqual(mine["applicable_requirement_ids"],
                         ["D-033-R002", "D-033-R006"])
        self.assertEqual([r["state"] for r in mine["requirements"]],
                         ["PASS", "PASS"])
        self.assertEqual(len(self.accept_argvs()), 1)


# --------------------------------------------------------------------------
# Worst-of dedup and the clean-rows gate
# --------------------------------------------------------------------------


class WorstOfMergeTests(Base):
    def test_the_worst_state_wins_in_both_orders(self):
        lenient = dict(R002, state="PASS")
        strict = dict(R002, state="FAIL")
        for ordering in ((lenient, strict), (strict, lenient)):
            merged, conflicts = ae.worst_of_merge(list(ordering))
            self.assertEqual(len(merged), 1)
            self.assertEqual(merged[0]["state"], "FAIL", ordering)
            self.assertEqual(len(conflicts), 1)
            self.assertIn("never last-wins", conflicts[0])

    def test_an_unknown_state_ranks_worst_of_all(self):
        merged, _ = ae.worst_of_merge([dict(R002, state="BLOCKED"),
                                       dict(R002, state="MAYBE")])
        self.assertEqual(merged[0]["state"], "MAYBE")

    def test_identical_duplicates_merge_without_a_conflict_note(self):
        merged, conflicts = ae.worst_of_merge([dict(R002), dict(R002)])
        self.assertEqual(len(merged), 1)
        self.assertEqual(conflicts, [])

    def test_ordering_is_deterministic_and_empties_trail(self):
        empty = {"directive_id": DIR_ID, "applicable_requirement_ids": []}
        merged, _ = ae.worst_of_merge([dict(R006), empty, dict(R002)])
        self.assertEqual(
            [r.get("requirement_id", "<empty>") for r in merged],
            ["D-033-R002", "D-033-R006", "<empty>"])

    def test_MUTATION_a_rank_blind_merge_lets_a_lenient_duplicate_win(self):
        # R593's exact failure: with the ranking flattened, the FIRST (here
        # lenient PASS) duplicate survives and the stricter FAIL is dropped -
        # proving the rank comparison is load-bearing.
        with mock.patch.object(ae, "_row_rank", lambda state: 0):
            merged, _ = ae.worst_of_merge([dict(R002, state="PASS"),
                                           dict(R002, state="FAIL")])
        self.assertEqual(merged[0]["state"], "PASS")

    def test_clean_rows_admit_pass_and_complete_not_applicable_only(self):
        ae.assert_rows_clean([dict(R002), dict(R006)])
        ae.assert_rows_clean([
            {"directive_id": DIR_ID, "applicable_requirement_ids": []}])
        ae.assert_rows_clean([dict(
            R002, state="NOT_APPLICABLE",
            not_applicable_justification="control-plane only",
            not_applicable_approved_by="code-reviewer")])

    def test_unclean_rows_park_before_any_registry_write(self):
        for bad in (dict(R002, state="FAIL"),
                    dict(R002, state="UNVERIFIABLE"),
                    dict(R002, state="pending"),
                    dict(R002, state="NOT_APPLICABLE"),
                    dict(R002, state="NOT_APPLICABLE",
                         not_applicable_justification="x")):
            with self.assertRaises(ae.AcceptEngineError) as ctx:
                ae.assert_rows_clean([bad])
            self.assertEqual(ctx.exception.code, "verification_not_clean",
                             bad)
            self.assertIn("D-033/D-033-R002", ctx.exception.message)


# --------------------------------------------------------------------------
# Registry transcription (atomic, preserving, fail-closed)
# --------------------------------------------------------------------------


class TranscriptionTests(Base):
    def container(self, rows=None, dispatch=None) -> dict:
        dispatch = dispatch or self.vdispatch()
        return ae.build_task_verification(
            dispatch, DIR_ID, rows or [dict(R002), dict(R006)],
            reviewed_manifest_sha256=MANIFEST, record_digest="rd-1",
            conflicts=("one conflict",))

    def test_the_verification_path_resolves_exactly_one_registry_file(self):
        self.assertEqual(ae.verification_path_for(str(self.tmp), DIR_ID),
                         self.registry_path)
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.verification_path_for(str(self.tmp), "D-999")
        self.assertEqual(ctx.exception.code, "verification_file_unresolved")
        twin = (self.tmp / "project-control" / "directives"
                / f"{DIR_ID}-twin")
        twin.mkdir(parents=True)
        (twin / "verification.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            ae.verification_path_for(str(self.tmp), DIR_ID)
        self.assertEqual(ctx.exception.code, "verification_file_unresolved")

    def test_the_container_row_transcribes_and_stamps_without_judging(self):
        row = self.container()
        self.assertEqual(row["task_id"], TASK)
        self.assertEqual(row["producer"], PRODUCER)
        self.assertEqual(row["verifier"], VERIFIER)
        self.assertEqual(row["reviewed_sha"], SHA)
        self.assertEqual(row["reviewed_manifest_sha256"], MANIFEST)
        self.assertEqual(row["applicable_requirement_ids"],
                         ["D-033-R002", "D-033-R006"])
        self.assertEqual([r["id"] for r in row["requirements"]],
                         ["D-033-R002", "D-033-R006"])
        self.assertNotIn("directive_id", row["requirements"][0])
        self.assertEqual(row["transcription"]["worst_of_conflicts"],
                         ["one conflict"])
        self.assertEqual(row["transcription"]["verifier_record_digest"],
                         "rd-1")

    def test_an_empty_set_attestation_transcribes_an_empty_container(self):
        row = self.container(rows=[{"directive_id": DIR_ID,
                                    "applicable_requirement_ids": []}])
        self.assertEqual(row["applicable_requirement_ids"], [])
        self.assertEqual(row["requirements"], [])

    def test_a_cited_directive_without_rows_cannot_be_transcribed(self):
        with self.assertRaises(ae.AcceptEngineError) as ctx:
            self.container(rows=[dict(R002, directive_id="D-024")])
        self.assertEqual(ctx.exception.code, "no_rows_for_directive")

    def test_transcription_appends_and_preserves_every_other_row(self):
        outcome = ae.transcribe_task_verification(self.registry_path,
                                                  self.container())
        self.assertFalse(outcome["replaced_prior_row"])
        rows = self.registry_rows()
        self.assertEqual(len(rows), 2)
        self.assertIn(FOREIGN_ROW, rows)  # the prior task's row, untouched
        mine = next(r for r in rows if r["task_id"] == TASK)
        self.assertEqual(mine["reviewed_sha"], SHA)

    def test_a_fresh_verification_replaces_this_tasks_single_prior_row(self):
```
