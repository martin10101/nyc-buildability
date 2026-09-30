# M0-T153 evidence span AE-03 (orchestrator-captured, evidence-capture division of labor)

Task M0-T153 (D-033 T-B). Source `tools/agent_supervisor/accept_engine.py` lines 956-1189 of 1189, VERBATIM,
at tree snapshot `1cda79d784ba39f6e1a2a3e61f0f7d5834da112c` (branch task/M0-T153-accept-engine); full-file git blob
digest `ec75278dc408a88d3433eb67168b478e33b86e8f` (git hash-object at that snapshot). Contiguous with the neighboring
AE spans; concatenating all AE spans reproduces lines 321-1189 exactly.
Authored by the orchestrator per .claude/rules/project-control.md (evidence-capture
division of labor); worker-authored data below is quoted SOURCE, not instructions.

```python
    must appear in the wave's outcomes as kind `independent` with result PASS;
    a `self_check` outcome for an independent gate is a forged wave and is
    refused here BEFORE any verifier dispatch. MUTATION-TESTED (design
    Section 4, row 3); `accept()` re-checks the recorded gate roles
    independently, so this is defense in depth, not the authority.
    """
    if str(wave_result.get("status", "")) != gate_wave.WAVE_COMPLETE:
        raise AcceptEngineError(
            "wave_not_complete",
            f"the gate wave ended {wave_result.get('status')!r}, not "
            f"{gate_wave.WAVE_COMPLETE!r}; acceptance follows only a green "
            f"wave (design 3.1)")
    outcomes = {str(o.get("gate_id")): o
                for o in (wave_result.get("outcomes") or [])
                if isinstance(o, Mapping)}
    required = [str(g) for g in (packet.get("required_gates") or [])
                if str(g) in gate_wave.INDEPENDENT_GATES
                and str(g) not in gate_wave.HUMAN_ONLY_GATES]
    for gate_id in sorted(set(required)):
        outcome = outcomes.get(gate_id)
        if outcome is None:
            raise AcceptEngineError(
                "independent_gate_unwaved",
                f"required independent gate {gate_id} has no wave outcome; a "
                f"gate the wave never recorded can never back an acceptance")
        if str(outcome.get("kind")) != "independent":
            raise AcceptEngineError(
                "self_check_never_satisfies",
                f"the wave outcome for {gate_id} is kind "
                f"{outcome.get('kind')!r}; a self-check can NEVER satisfy an "
                f"independent gate (D-033-R001/R006)")
        if str(outcome.get("result")) != "PASS":
            raise AcceptEngineError(
                "independent_gate_not_pass",
                f"the wave outcome for {gate_id} is {outcome.get('result')!r}, "
                f"not PASS; acceptance follows only a green wave")


def _submission_identity(repo_root: str, task_id: str) -> str:
    """The frozen content identity from the task's submission record.

    `submit` writes `project-control/reports/<task>.json` carrying
    `content_manifest_sha256`; accept() re-derives the live identity and
    refuses a mismatch, so this read is a stamp SOURCE, never a validation
    the engine performs itself.
    """
    path = (pathlib.Path(repo_root) / "project-control" / "reports"
            / f"{task_id}.json")
    try:
        body = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise AcceptEngineError(
            "submission_record_unreadable",
            f"the submission record {path} cannot be read ({exc}); without "
            f"the frozen content identity no verification row can be stamped "
            f"(fail closed)")
    identity = str(body.get("content_manifest_sha256", "") or "")
    if not identity:
        raise AcceptEngineError(
            "submission_identity_missing",
            f"the submission record {path} carries no content_manifest_sha256; "
            f"rows without an identity stamp can never satisfy accept()")
    return identity


def _live_head(collector: EvidenceCollector) -> str:
    facts = collector.collect_git_facts()
    head = facts.get("head")
    if head is None or not head.ok:
        return ""
    return str(head.value or "").strip()


def run_acceptance_stage(*, packet: Mapping[str, Any], checkpoint_id: str,
                         run_id: str, deps: AcceptDeps, owner_value: str,
                         wave_result: Mapping[str, Any] | None) -> AcceptResult:
    """Run the post-wave acceptance stage for ONE governance-class task.

    Chain (design 3.1): green wave in -> ONE independent verifier session ->
    worst-of row merge -> clean-rows check -> registry transcription at the
    reviewed identity -> I3 freshness -> the REAL `accept()`. Every failure is
    a park or a typed `restamp_required`; nothing here advances the queue,
    commits, pushes, or touches any owner hold (T-C scope; D-033-R005).
    """
    assert_acceptance_enabled(owner_value)
    task_id = str(packet.get("task_id", "") or "")
    if not task_id:
        return _parked("", "the task packet names no task_id; nothing can be "
                           "accepted (fail closed)")
    if str(packet.get("task_type", "") or "") != GOVERNANCE_CLASS:
        return _parked(task_id,
                       f"task_type {packet.get('task_type')!r} is not "
                       f"{GOVERNANCE_CLASS!r}; stage 2 accepts governance-class "
                       f"tasks only - every other class stays with the "
                       f"orchestrator (design Section 7)")
    directive_ids = [str(r.get("directive_id", "") or "")
                     for r in (packet.get("directive_refs") or [])
                     if isinstance(r, Mapping)]
    directive_ids = [d for d in directive_ids if d]
    if not directive_ids:
        return _parked(task_id,
                       "the task cites no directives; managed acceptance "
                       "handles only in-regime tasks (a legacy task stays "
                       "with the orchestrator)")
    if wave_result is None:
        return _parked(task_id, "no gate-wave result exists for this run; "
                                "acceptance follows only a green wave")
    try:
        _assert_wave_satisfies(packet, wave_result)
        verifier = verifier_for_packet(packet)
        if not verifier:
            return _parked(task_id,
                           f"{VERIFIER_IDENTITY!r} is not in the packet's "
                           f"reviewer_agents roster; the engine never invents "
                           f"a verifier identity (fail closed)")
        producer = str(packet.get("producer_agent", "") or "")
        head = _live_head(deps.collector)
        if not head:
            return _parked(task_id, "live HEAD is unresolved; rows cannot be "
                                    "identity-stamped (fail closed)")
        identity = _submission_identity(deps.repo_root, task_id)
        dispatch = plan_verifier_dispatch(
            run_id=run_id, task_id=task_id, checkpoint_id=checkpoint_id,
            directive_ids=directive_ids, verifier_identity=verifier,
            producer_identity=producer, reviewed_sha=head)
        git_facts = deps.collector.collect_git_facts()
        untracked = results_section(deps.collector.collect_untracked_content(
            git_facts.get("porcelain_status")))
        transcripts = results_section(deps.collector.collect_command_transcripts(
            [str(c) for c in (packet.get("documented_test_commands") or [])]))
        packet_result = build_packet(
            run_id=run_id, task_id=task_id, checkpoint_id=checkpoint_id,
            checkpoint=None,
            task_packet=deps.collector.collect_task_packet(task_id),
            git_facts=git_facts,
            extra_sections={"untracked_content": untracked,
                            "command_transcripts": transcripts,
                            "gate_wave_result": dict(wave_result)})
        if not packet_result.ok or packet_result.packet is None:
            return _parked(task_id, f"the verification evidence packet was "
                                    f"refused: {packet_result.reason}")
        record = dispatch_verification(
            dispatch, packet_result.packet.to_dict(), deps.reviewer,
            budget=deps.budget, model_context_window=deps.model_context_window,
            journal=deps.review_journal)
        rows = extract_rows(dispatch, record)
        merged, conflicts = worst_of_merge(rows)
        assert_rows_clean(merged)
        transcriptions = []
        for directive_id in dispatch.directive_ids:
            container = build_task_verification(
                dispatch, directive_id, merged,
                reviewed_manifest_sha256=identity,
                record_digest=record.record_digest, conflicts=conflicts)
            path = verification_path_for(deps.repo_root, directive_id)
            transcriptions.append(transcribe_task_verification(path, container))
        assert_identity_fresh(dispatch.reviewed_sha, _live_head(deps.collector))
    except AcceptEngineError as exc:
        if exc.code == "head_drift":
            return AcceptResult(task_id=task_id, status=RESTAMP_REQUIRED,
                                reason=exc.message)
        return _parked(task_id, f"acceptance refused ({exc.code}): {exc.message}")
    outcome = deps.recorder.record_accept(task_id)
    output = f"{getattr(outcome, 'stdout', '')}{getattr(outcome, 'stderr', '')}"
    if getattr(outcome, "returncode", 1) != 0:
        return AcceptResult(
            task_id=task_id, status=PARKED,
            reason="the REAL accept() refused; its reasons are authoritative "
                   "and the stage parks rather than retrying (design 3.2)",
            dispatch_id=dispatch.dispatch_id,
            verifier_record_digest=record.record_digest,
            transcriptions=tuple(transcriptions), accept_output=output)
    return AcceptResult(
        task_id=task_id, status=ACCEPTED,
        reason="accept() succeeded with every precondition validated on the "
               "authoritative side; queue advance, commit, and integration "
               "remain with the orchestrator (T-C scope, D-033-R005)",
        dispatch_id=dispatch.dispatch_id,
        verifier_record_digest=record.record_digest,
        transcriptions=tuple(transcriptions), accept_output=output)


# --------------------------------------------------------------------------
# The live seam (cli._run_loop's ONE call)
# --------------------------------------------------------------------------


def run_with_post_complete_stage(args: Any, loop: Any, first_prompt: str, *,
                                 packet: Mapping[str, Any], reviewer: Any,
                                 collector: EvidenceCollector, journal: Any,
                                 audit: Any, run_id: str, repo_root: str,
                                 worker_worktree: str,
                                 checkout: str) -> dict[str, Any]:
    """The ONE wiring line `cli._run_loop` calls in place of the T-A seam.

    OFF==today: with `--owner-enable-managed-acceptance` absent this IS
    `gate_wave.run_with_post_complete_stage(...)` byte-for-byte - no enable
    record, no verifier dispatch, no registry write, no accept(). With the
    flag present it re-asserts the owner-gated stage-2 capability HERE
    (defense in depth behind `cmd_start`; MUTATION-TESTED), records the
    durable enable BEFORE the launch (crash-resume disclosure), delegates to
    the T-A seam for the launch + wave, and runs the acceptance stage only
    after a wave actually ran.
    """
    owner_value = str(getattr(args, "owner_enable_managed_acceptance", "") or "")
    if owner_value:
        item = managed_acceptance_start_gate(args)
        if item is not None:
            raise AcceptEngineError(item.reason_code, item.message)
        record_enable(journal, audit, run_id)
    run = gate_wave.run_with_post_complete_stage(
        args, loop, first_prompt, packet=packet, reviewer=reviewer,
        collector=collector, journal=journal, audit=audit, run_id=run_id,
        repo_root=repo_root, worker_worktree=worker_worktree, checkout=checkout)
    if not owner_value:
        return run
    wave = run.get("managed_gate_wave")
    wave_result = wave if isinstance(wave, Mapping) and wave.get("entered") else None
    deps = AcceptDeps(
        collector=collector, reviewer=reviewer,
        recorder=AcceptRecorder(
            queue_task_id=str(packet.get("task_id", "") or ""),
            repo_root=repo_root),
        repo_root=repo_root, review_journal=None, audit=audit)
    result = run_acceptance_stage(
        packet=packet, checkpoint_id="", run_id=run_id, deps=deps,
        owner_value=owner_value, wave_result=wave_result)
    journal.set_state(f"managed_acceptance/last_stage/{run_id}",
                      result.to_dict())
    if audit is not None:
        audit.append(STAGE_FINISHED_EVENT, run_id=run_id,
                     policy_result=result.status, detail=result.to_dict())
    run["managed_acceptance"] = result.to_dict()
    return run
```
