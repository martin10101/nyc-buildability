# M0-T106 independent directive-compliance verification (VERBATIM verifier return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Verifier: directive-compliance-verifier
(independent, read-only, dispatched 2026-08-27; producer = fable-orchestrator-session ≠ verifier).
Overall verdict returned: **PASS**. Rows transcribed verbatim into
`project-control/directives/D-024-fable-codex-loop/verification.json` (M0-T106 entry).

---

# DIRECTIVE-COMPLIANCE VERIFICATION — M0-T106 (D-024 Amendment 3 unit E: bounded /goal integration)

**Overall verdict: PASS**

Independent DCV performed at frozen head. Live HEAD `0d1b196` (confirmed == working checkout HEAD), deliverable `5e60a0d`, checkpoint content_manifest `4d31dba2…` (verified in `project-control/reports/M0-T106.json`: `content_manifest_sha256=4d31dba2e0…`, `reviewed_sha=5e60a0d…`). Applicable set independently re-derived by the real registry (`DirectiveRegistry.derive_applicable`) as exactly **{D-024-R152, D-024-R162, D-024-R174}**, matching the checkpoint. Validator `tools/validate_directive_compliance.py --check` EXIT=0 (source digests / locked-ids intact). Required test packs reproduced from the checkout after confirming byte-identity to the frozen deliverable: **goal integration 38 passed**, **event-bus 38 passed** (`git diff --stat 5e60a0d 0d1b196` empty for all six deliverable paths). Every finding below rests on code/fixtures/tests/git I reproduced personally; producer/gate reports were treated as unverified claims.

---

## D-024-R152 — PASS

*/goal used only as the inner continuation for ONE bounded assignment with a measurable completion condition; never one goal for the whole campaign; verify condition-met/impossible/no-progress/background-check-in/transient/unrecoverable/resume/context-pressure.*

- **Structural one-task binding is the PRIMARY guard**: `tools/agent_supervisor/goal_contract.py` `GoalCondition.__post_init__` (lines 103-107) raises `GoalContractError` when `task_id` fails `_TASK_ID_RE = ^M\d+-T\d+$`; and lines 124-129 refuse any FOREIGN ledger-task reference (`foreign = [t for t in _LEDGER_TASK_RE.findall(self.text) if t != self.task_id]`). Reproduced by `test_s1_one_task_only` (rejects `"M0-T092 and M0-T094"` and `"not-a-task-id"`).
- **Campaign-scale tripwire is disclosed defense-in-depth**, not the primary guard: docstring lines 49-51 label `_CAMPAIGN_SCALE_RE` "A heuristic tripwire **on top of** the structural one-task binding"; enforced lines 130-133; F5-widened to the four proven-slip verbs (finish/complete/wrap up/deliver + milestone/backlog/project/campaign). Reproduced by `test_s1_campaign_scale_refused` (7 phrasings all raise).
- **Measurable completion condition + documented shape**: `compose_goal_condition` (lines 138-158) emits end_state + `"Prove it: "`<check> + `Constraint: `… + `"Or stop after N turns"`; `_TURN_BOUND_RE` guard (lines 116-119) and the 4000-char ceiling (lines 120-123, `GOAL_CONDITION_MAX_CHARS=4000`) fail closed. `test_s1_condition_has_all_documented_parts` + `test_s1_direct_construction_cannot_drop_the_bound` + `test_s1_ceiling_and_required_parts` reproduce; fixture `condition.effective_shape`/`max_chars:4000`/`bound_clause_example` corroborate.
- **All eight R152 behaviors verified in code + deterministic tests**: condition-met/impossible (`goal_outcomes.normalize_verdict`, `test_s3`); no-progress (`classify_pause`→`no_progress_paused` goal-stays-set, `test_s5`); background check-in (`goal_checkins.checkin_schedule`/`record_checkin`, `test_s7`/`test_s8`); transient (`classify_goal_message`→`transient_error_active`, `test_s4_transient_stays_active`); unrecoverable (four classes, `test_s4_four_unrecoverable_classes`); resume (`resume_restores_goal`, `test_s6`); context-pressure (`is_turnover_seam_trigger`, `test_s10`).
- Source text at `5e60a0d:source-003-amendment.md` line 131 matches requirement text verbatim ("inner continuation mechanism for one bounded Fable assignment… Never use one goal for the entire software campaign").

## D-024-R162 — PASS

*Context safeguards: retain statusLine telemetry; /autocompact as emergency buffer only, never a seam substitute; owner-gated live canary (R192/R197).*

- **Autocompact-emergency / context-overflow-as-turnover-seam policy is encoded**: `goal_outcomes.py` `is_turnover_seam_trigger` (lines 182-190) returns True ONLY for an unrecoverable `context_overflow` clearing; docstring states "auto-compaction is an EMERGENCY buffer only… never a cue to silently continue (packet: /autocompact never a seam substitute)". Reproduced by `test_s10_context_overflow_is_turnover_seam` (True) and `test_s10_other_clearings_are_not_the_seam_trigger` (credit_exhausted + transient both False).
- **C1 live canary prepared, flagged owner-gated, and NOT executed by any committed artifact**: report section 2 + the C1 row (`M0-T106-goal-integration.md`) mark it "OWNER-GATED … owner-approved exact launch command (R192/R197)"; fixture `goal_semantics_2_1_247.json` `confidence:"official-docs"` and `upgrade_path` ("measured-live captures are the owner-gated C1 canary… documentation-confidence until then"); test-module docstring: "C1 live goal canary is owner-gated (R192/R197) and NOT exercised here; every row below is deterministic". `git ls-files` shows no live-canary capture artifact (only the docs-confidence fixture). Matches the unit-C/D owner-gated-canary precedent.
- **StatusLine integration retained (not regressed)**: unit E touched none of `.claude/settings.json`, `.claude/hooks`, or statusLine code — `git diff --stat` over the full unit-E span (`c3f3768^..0d1b196`) for those paths is empty; the accepted M0-T099/M0-T100 statusLine integration is untouched.
- No provider-specific cache behavior is assumed anywhere in the three new modules (no cache logic added), satisfying the "do not assume without live evidence" clause by omission.
- Source at `5e60a0d:source-003-amendment.md` lines 221-224 matches requirement text ("Retain the accepted statusLine telemetry integration… Evaluate /autocompact only as an emergency buffer. It is not a substitute for safe-seam turnover or a durable handoff").

## D-024-R174 — PASS

*Unit E: one cohesive task; safe completion condition; no-progress handling; background-agent check-ins; no worker-visible token pressure.*

- **One cohesive task + safe completion condition**: same `GoalCondition` structural binding + turn-bound + 4000-char ceiling as R152 above (`goal_contract.py`); measurable end-state/stated-check enforced non-empty (lines 108-113).
- **No-progress handling is structural, goal stays set**: `classify_pause(control_returned=True, goal_still_active=True)` → `"no_progress_paused"` (`goal_outcomes.py` lines 137-153); docstring notes the stall warning text is undocumented so classification never parses text. `test_s5_no_progress_pause_is_structural_and_goal_stays_set` reproduces (incl. cleared-goal → `not_paused_goal_cleared`).
- **Background-agent check-ins — documented cadence, version gates, durable dedup-keyed ingestion, fail-visible discriminator contract**: `goal_checkins.py` — cadence 30-min first interval doubling capped 4× (`checkin_schedule`, gaps F,2F,4F,4F; `test_s7_default_cadence_doubles_capped_at_4x` asserts offsets `(30,90,210,330,450)`); env scaling + `0`-disables + fail-visible malformed env (`resolve_first_interval` raises `GoalCheckinError`; `test_s7_env_scales_and_zero_disables`, `test_s7_malformed_env_fails_visible`); version gates 2.1.234/2.1.236/2.1.246 (`idle_checkin_cap`→`IdleCapVerdict(cap,known)`; `test_s7_version_gates_honest`). Durable dedup-keyed ingestion via the ONE additive `event_bus.publish_typed` (verified additive below); `record_checkin` (lines 199-206) **FAILS VISIBLE** (`GoalCheckinError`) when the per-delivery `sequence` discriminator is absent — reproduced by `test_s8_missing_discriminator_fails_visible`, `test_s8_distinct_sequences_both_persist` (two distinct persist, byte-identical replay dedups), `test_s8_checkin_lands_in_durable_bus_with_dedup`.
- **No worker-visible token pressure (R045 reuse, fail-closed on the FULL composed text)**: `goal_contract.py` line 135 calls the REUSED `subagent_contracts.assert_worker_text_clean("goal_condition", self.text)` on the full composed text; that validator is genuinely fail-closed (`subagent_contracts.py` lines 140-149 `raise ContractError` on quota/countdown/conserve patterns, incl. `numeric_tokens`, `token_quota`, `conserve`). Reproduced by `test_s2_token_pressure_fails_closed` (4 poison vectors) and `test_s2_token_pressure_via_constraint_fails_closed` (poison through a constraint bites because the validator sees the whole composed text). Goal-status spend is additionally named `goal_spend_tokens` (F3) so the durable store keeps it READABLE, not over-redacted — `test_s9_spend_survives_durable_store_readable` asserts `"[REDACTED" not in` the stored value.
- Source at `5e60a0d:source-003-amendment.md` lines 314-320 matches requirement text (unit E bullets).

---

## Frozen-identity & additive-boundary discipline (all confirmed)

- **Deliverable byte-stable across the control-plane range**: `git diff --stat 5e60a0d 0d1b196` empty for `goal_contract.py`, `goal_outcomes.py`, `goal_checkins.py`, `event_bus.py`, `fixtures/goal_semantics_2_1_247.json`, `tools/test_agent_supervisor_goal_integration.py` — the delta gates (G3/G4/G5 recorded at `6cc9cf2`, delta reports at `0d1b196`) reviewed the same content now under test.
- **Only 5 files touched under `tools/agent_supervisor` over the full unit-E span** (`c3f3768^..0d1b196`): the 3 new modules + fixture + `event_bus.py`. `native_runtime.py` and `runtime_backend.py` (M0-T104) — empty diff.
- **`event_bus.py` change is the ONE additive method**: full-span diff shows only `+publish_typed(record)` (25 lines incl. docstring), reusing existing `idempotency_key`/`_seen`/`_store`/`duplicates_ignored`; dedup key digests attributes AND measurements (G3-C1 fix); existing publish paths byte-unchanged.
- **Guards untouched**: `git diff --stat c3f3768^..0d1b196` empty for `.claude/settings.json`, `.claude/hooks/` (incl. `readonly_agent_guard.py`, `agent_dispatch_guard.py`) — all confirmed unmodified (these are also forbidden_paths on the packet).

## Selective-citation cross-check — CLEAN

- `DirectiveRegistry.derive_applicable(M0-T106)` returns exactly `{D-024-R152, D-024-R162, D-024-R174}`, `unresolved=[]`; `evaluate_task_refs` → `ok=True, missing_ids=[], invalid_refs=[], unresolved=[]`. **NON-D024 applicable set is empty.**
- The exclusion is genuinely by task_ids conjunction, not absence: **28 non-D024 requirements** have paths intersecting the task's allowed_paths — D-004 (R222/R240/R746/R747/R751-R760; task_ids M0-T028, M0-T034, D-004-MODELGOV) and D-007 (R597-R622; task_ids M0-T036, D-007-BUILD) — and every one resolves `excluded_by_conjunction=True`; none is a task_ids wildcard. This reproduces the M0-T105 DCV pattern exactly. No active directive has a requirement these paths make applicable that `D-024:ALL` fails to cite.

## Prohibited-action evidence — CLEAN

- Task remains `status=awaiting_gate` at HEAD (not accepted); no acceptance occurred during DCV. No live canary executed (no committed capture artifact; fixture is documentation-confidence). No merge/close/deploy/install/purchase — this is a governance task with no GitHub effect. Gate records G0/G2/G3/G4/G5 all PASS at content identity `4d31dba2`.

## Notes (non-blocking, not defects)

1. Working tree carries uncommitted control-plane bookkeeping edits (`project-control/state.json`, `project-control/tasks/M0-T106.json` progress_log/percent 95↔90) — orchestrator ledger churn; does not touch any deliverable file and does not accept the task.
2. Gate reviewed_sha for G3/G4/G5 is a control-plane commit (`6cc9cf2`) later than the deliverable `5e60a0d`; content identity (manifest `4d31dba2`) is stable and the code is byte-identical across the range, so the gates reviewed the frozen deliverable content. Benign.

**Recommendation to orchestrator: record D-024-R152 = PASS, D-024-R162 = PASS, D-024-R174 = PASS into `verification.json` at reviewed content identity `4d31dba2…` / reviewed_sha `0d1b196`. DCV verdict: PASS.**
