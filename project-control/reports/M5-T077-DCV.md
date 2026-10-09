# M5-T077 — directive-compliance verification (directive-compliance-verifier "dcv-t077", read-only)

> Transmission history: pinned at 94182057, delivered as five SendMessage parts (1..5, part 5 marked
> final) ending with END-OF-REPORT; no truncation. Joined verbatim in delivery order by the orchestrator
> (transport wrapper tags removed only). Orchestrator predicate re-check at the accept head 114e5e56:
> the five blobs unchanged (4ea749fb / 5e690f18 / 6a13a406 / b5ae8f13 / 05418f17); identity 457a1715
> with error None; evaluate_task_refs ok. The verifier's watch item (a harness packet editing
> tools/directive_registry.py) did not land - that draft was withdrawn before its contract commit.
> Transport note: two predicate lines (a 40-hex blob id beside an `...api.py` path) carry an inline
> `<!-- gitleaks:allow -->` marker because the secret scanner reads them as a generic API key; the
> verifier's text is otherwise unchanged.

---

M5-T077 DCV part 1 of N: pinned HEAD and restamp pre-authorization (verdict comes in a later part).

PINNED HEAD: 94182057f9034a6c98c86ab9ef9aef97d01e6fb2 (primary checkout ctl24, branch candidate/D-024-mrl-option-b).
Live identity at pin: project_control._task_git_identity(M5-T077) = 457a17155812843eb2c495aee6ed182b114a1ffe750718c849774b1529388369, error None (matches reports/M5-T077.json content_manifest_sha256).

RESTAMP PREDICATE (blob-level). My verdict carries to any later head H that descends from 94182057 if ALL of these hold at H:
1. Blob ids are unchanged:
   - services/api/app/api/v1/max_envelope_api.py = 4ea749fbbe75d6b80c115e613e43e725de7b962f <!-- gitleaks:allow -->
   - services/api/app/scenario/lot_geometry_derivation.py = 5e690f18405bf70768e196007cfc86bddeae4d49
   - services/api/tests/api/test_max_envelope_api.py = 6a13a406b87e1d147c2c642cd0700c42ed16e809 <!-- gitleaks:allow -->
   - services/api/tests/scenario/test_lot_geometry_derivation.py = b5ae8f13e94b9d3cda1cb4b0749ca0f725e3a7a8
   - project-control/reports/M5-T077-producer-report.md = 05418f175e6547030ef033f46baa1a96dcc77be4
2. _task_git_identity(M5-T077) at H = 457a1715...388369 with error None (allowed_paths clean).
3. The packet's material fields are unchanged: allowed_paths, forbidden_paths, directive_refs, acceptance_scenarios, required_gates, producer_agent, reviewer_agents. Lifecycle fields (status, progress, progress_log, updated_at) may change.
4. evaluate_task_refs(M5-T077) is ok, and applicable == cited == {D-066-R001, D-087-R001, D-087-R002}. The bodies of those three requirements are unchanged (applicability.task_ids appends are fine).
5. No open blocker names M5-T077 by word-bounded match in affects or detail.
6. The M5-T077 G2/G3/G4 gate records are unchanged (PASS, same stamp).

TOLERATED DISJOINT-PEER CHANGES (explicit, broad):
- Other tasks' files, packets, gates, reports and material commits. This includes later mount-packet edits to main.py or max_envelope.py: my D-066-R001 scope ruling rests on the immutable producer commit f63cfad1 and the frozen identity, not on those files' future state.
- Other directives' registry captures, binds and amendments.
- Same-directive amendments to D-066 or D-087 that leave predicate 4 true.
- The orchestrator adding my verification rows to D-066 and D-087 verification.json, plus the matching manifest/audit/digest resyncs.
- Unrelated ledger, state.json, checkpoint and docs commits.

Anything outside this list voids the restamp. That includes any edit to the five blobs, even an [ORCH-CORRECTED] comment.

---

M5-T077 DCV part 2: identity, gates and D-066-R001 (SATISFIED).

IDENTITY (all reproduced by me)
- _task_git_identity(M5-T077) = 457a1715...388369 with error None, at the pin 94182057 and at live 4de4f5ec. It matches the content_manifest_sha256 in reports/M5-T077.json and in gates/M5-T077-G2/G3/G4.json.
- The five blobs are identical at af332042, f63cfad1, the pin and live HEAD. af332042 is the only commit on task/M5-T077-geometry-threading-hardening (parent b56f3d5b). Patch-id is the same for both commits (982f35e6...). No commit after f63cfad1 touches the five paths.
- The packet's material_digest is 757485ad... at f57fccd5, b56f3d5b, 46186f9c, the pin and live. Only directive_refs and lifecycle fields changed.

GATES (required: G0, G2, G3, G4; all PASS)
- G0: orchestrator, administrative, at f57fccd5.
- G2: orchestrator, self_check, at d6fba6bb.
- G3: code-reviewer, independent_review, at 70c29c5a. M5-T077-G3.md line 31 = "VERDICT: PASS".
- G4: qa-engineer, independent_review, at 70c29c5a. M5-T077-G4.md line 47 = "VERDICT: PASS".
- Both independent reviewers are listed in reviewer_agents, and neither is the producer (backend-engineer).
- Lifecycle: backlog, then ready (G0), claimed (b56f3d5b), then submit to awaiting_gate. The CLI allows submit from claimed (SUBMITTABLE_STATUSES, project_control.py:181).
- Rerun at live HEAD (same blobs; Python 3.11.9, cwd services/api): `ruff check --no-cache .` exit 0; the scoped pytest gave 64 passed.

D-066-R001: SATISFIED
- Navigation block: tasks/M5-T077.json line 16 carries it, byte-present since the contract seam (checked with git show f57fccd5). It names consumers, forbidden files and the `query.py --no-regen impact` instruction, and marks the graph as advisory.
- Graph regenerated at the seam: %LOCALAPPDATA%\nyc-codegraph\346263e4677b-ctl24\graph.meta.json has mtime 07:41:37Z (packet created 07:41:56Z; seam commit 07:42:43Z). It records 817 files, 17027 nodes and 7441 edges, the same numbers the block states. graph_sha256 re-hashes correctly.
- Block accuracy, checked in source with git grep at f57fccd5 and the pin:
  - max_envelope_api is imported only by tests/api/test_max_envelope_api.py. The hit in test_outline_bridge.py:707 is a comment.
  - lot_geometry_derivation is imported by max_envelope_api.py:76 and tests/scenario/test_lot_geometry_derivation.py.
  - app/main.py has zero "max_envelope" hits at f57fccd5, the pin and on disk, so the route is still unmounted.
- Producer stayed in scope: f63cfad1 touches exactly the five allowed_paths and no forbidden path. The max_envelope.py blob is f0abf884 at b56f3d5b, f63cfad1, the pin, live HEAD and on disk (hash-object). The production diff is one guard expression plus docstrings.
- Limit (does not affect the ruling): the subagent dispatch prompt is not committed. The producer report (lines 3-4) says every packet input except the checkpoint envelope was binding.

---

M5-T077 DCV part 3: D-087-R001 and D-087-R002 (both SATISFIED).

D-087-R001: SATISFIED (this task's share)
- Contracted: the packet was created 07:41:56Z at f57fccd5 citing R001. It is bound via applicability.task_ids (D-087 audit_log bind entry, 08:05). The R001 body, excluding task_ids, hashes the same at f57fccd5, the pin and live HEAD. G0 PASS at f57fccd5.
- Claimed at b56f3d5b with the full worktree path.
- Ran concurrently: unit af332042 was authored 08:13:38Z. Peer D-087 subagent units were authored in the same window: T081 07:45:55Z, T082 07:46:36Z, T085 07:48:17Z, T086 07:49:56Z, T084 07:59:32Z, T083 08:01:33Z, T078 08:24:51Z, T080A 08:26:37Z, T079 08:30:26Z.
- No state or gate skipped: lifecycle and gates are in part 2. This report is the DCV. The task is not accepted.
- Route: R001's text allows "loops and subagents". Three records disclose the lane refusal and the switch to a dispatched subagent in the same claimed worktree: the packet progress_log (07:55:42Z), B-026 workaround_in_effect, and the D-084 audit_log unbind (08:10).
- Scope limit: R001's "three codex loop lanes stay occupied" clause is program-level. It is blocked by open B-026 (affects "D-087-R001 (the loop-lane share...)"). This row neither evidences nor discharges it.

D-087-R002: SATISFIED
- One writer, one worktree: wt-m5t077 (HEAD af332042, porcelain clean) is the only worktree on the task branch. That branch holds only af332042. No other packet names wt-m5t077.
- No shared writes: git log f57fccd5..pin on the five paths shows only f63cfad1. f57fccd5 itself seeded the report placeholder.
- Disjointness, which I recomputed over 45 packets:
  - Scope of the check: every non-terminal packet at f57fccd5 plus every packet created through the pin, using allowed_paths at both ends. The match is glob- and prefix-aware and strips prose suffixes.
  - Result: EMPTY against every concurrently-run packet (M5-T078 to T087, M0-T159, and all claimed, in_progress and rework packets).
  - The only overlaps are two dormant July packets (see F1 in part 4).
- Sequencing: M5-T076 (same four code files) was accepted at 6ff14664 (05:15Z). That commit is an ancestor of f57fccd5, and M5-T076's status there is accepted.
- B-026: the file contains no "T077" substring at all. Its affects list covers D-084 lane occupancy and the R001 loop-lane share. No blocker, open or closed, matches M5-T077 word-bounded. B-026 neither names nor gates this task.

---

M5-T077 DCV part 4: prohibited-action sweep, the D-087 amendment, and findings F1-F4.

PROHIBITED-ACTION SWEEP: all clean
- Not accepted: status is awaiting_gate at the pin and at live f4b4ef28.
- No verification row yet: "M5-T077" appears 0 times in both the D-087 and D-066 verification.json, at the pin and at live.
- Not on main: GitHub compare main (d8b3899f)...f63cfad1 shows ahead 1908, behind 0.
- PR #241 untouched: OPEN, mergedAt null, head 4174a3b2, last updated 2026-08-20.
- No blocker names M5-T077 (see part 3).
- f63cfad1 changes only the 5 files: no lockfile or pyproject change. The route stays unmounted. Nothing was deployed, installed or purchased.

AMENDMENT 744154df (D-087 source-002): INERT for this task
- R011 and R012 have applicability.task_ids = ["D-087-BOOTSTRAP"] only.
- evaluate_task_refs(M5-T077) is ok, with applicable == cited, at the pin, 4de4f5ec and f4b4ef28.
- Source digests recomputed and matching: D-087 source-001 34c3dd64..., D-087 source-002 4eea66c6..., D-066 source-001 4cb05c94....

FINDINGS
- F1 (ADVISORY, non-blocking; R002 record accuracy; a G0-template problem, not specific to T077):
  - M5-T077-G0.md line 30 records M5-T001 as "EMPTY overlap". But M5-T001 declares "services/api/app/scenario/** (...)" and "services/api/tests/scenario/** (...)", which contain T077's derivation module and its test.
  - M4-T005 is missing from the table. It is awaiting_gate and its "services/api/tests/api/**" covers test_max_envelope_api.py.
  - The EMPTY result holds only mechanically: project_control._path_touches never matches prose suffixes or ** globs.
  - Why non-blocking: neither packet is a live or frozen writer. Both are pre-regime with no frozen identity (reports/M5-T001.json has no content_manifest_sha256; reports/M4-T005.json does not exist). Neither has a worktree, and neither packet has changed since 37619630 (2026-07-23). M5-T076 already wrote these same files and was accepted.
  - Recommendation: record such rows as "declared scope overlaps; dormant pre-regime; excluded", and make the overlap check strip prose and expand globs.
- F2 (ADVISORY, D-066-R001 evidence): the dispatch prompt is not committed. The query.py instruction rests on the packet input plus the producer report's statement.
- F3 (INFO): the loop-lane share of D-087-R001 and D-084-R001's lane-1 obligation remain open under B-026. This row discharges neither.
- F4 (INFO): my validator run spanned HEAD 94182057 to f4b4ef28 because orchestrator commits landed mid-run. CI run 35980056704 corroborates it at 33662211, a descendant of the pin with identical blobs.

---

M5-T077 DCV part 5 (final): all three requirements are SATISFIED. Verdict PASS 3/3, with harness evidence and the predicate still holding at live HEAD.

HARNESS
- validate_directive_compliance.py --check: run once, direct exit code. EXIT=0, no output (09:07:09Z to 09:36:26Z). Wall time was about 29 min on this Windows host, over the ~15-min guide. HEAD moved 94182057 to f4b4ef28 during the run (F4).
- test_directive_reminder.py: 12 tests OK, EXIT=0, at 4de4f5ec.
- test_project_control.py: I started a local run at 09:28:48Z. It was still running at 09:44Z (Windows git-subprocess overhead; CI runs it in 40 s). I stopped waiting because of the time budget, so I claim no local result.
- CI (read-only gh):
  - Run 35980056704 at 33662211 (a descendant of the pin, same five blobs): success. Every control-plane step passed: project-control regression, validate --check, validator + adversarial tests, reminder-hook tests, read-only guard.
  - Run 35977663858 at f2870507 (contains the blobs): all 18 jobs passed, including api (ruff + pytest), modularity and code-graph.
- NOT run: tools/test_directive_compliance.py (prohibited).

PREDICATE AT LIVE f4b4ef28 (pushed): holds
- Five blobs identical.
- Identity 457a1715...388369, error None.
- G2, G3 and G4 PASS records unchanged.
- evaluate_task_refs ok.
- R001, R002 and D-066-R001 bodies hash-stable.
- No M5-T077 record changed since the pin. The only changes are tolerated peer ones: other tasks' gates and the M5-T082 verification rows.
- The uncommitted seam now in the primary checkout (M0-T160, M5-T088 to T092, new D-066/D-087 binds) leaves those three bodies hash-stable and has zero path overlap with T077.
- Watch item: M0-T160 edits tools/directive_registry.py. If it lands before accept, recheck predicate item 2. The identity must still compute to 457a1715... with error None; a different value voids the restamp.

REQUIREMENT ROWS
- D-066-R001: SATISFIED (part 2).
- D-087-R001: SATISFIED for this task's share (part 3). The loop-lane share is still open under B-026 (F3).
- D-087-R002: SATISFIED (part 3). F1 is an advisory on the G0 record.
- No row is VIOLATED, BLOCKED or UNVERIFIABLE. F1 and F2 are advisory, F3 and F4 are informational, and none of them blocks acceptance.

M5-T077 DCV VERDICT: PASS 3/3

END-OF-REPORT
