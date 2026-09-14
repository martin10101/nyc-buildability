# M4-T021 Independent Directive-Compliance Verification — Report

> Saved VERBATIM by the orchestrator from the directive-compliance-verifier agent return
> (2026-09-14; transport entity-decoding only, per the report-preservation rule).
> Verifier ≠ producer ≠ gate reviewers ≠ orchestrator.
>
> **Orchestrator action on the verifier's one open item — with a provenance correction:** the
> verifier could not complete `tools/test_directive_compliance.py` within its session budget and
> recommended a longer-budget capture. The authoritative result — **129 tests, OK, exit 0, in
> 3244s (~54 min)** — comes from the VERIFIER'S OWN background run (`bhv11kwu4`), which it
> launched and read directly from that run's output file, then folded into a follow-up to this
> report. The orchestrator separately launched a duplicate run (`bmwc78smk`) at the acceptance
> seam; that duplicate was KILLED before finishing and produced only partial output (it was
> progressing normally, last seen passing `LineEndingNormalizationTest`). An earlier draft of
> this header implied the recorded result came from the orchestrator's run — it did not, and
> that is corrected here. The provenance is in fact stronger than first stated: the passing
> result is the independent verifier's own execution, not the orchestrator's.

## Scope and identity confirmation

`git rev-parse --show-toplevel` = `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`; `git rev-parse HEAD` = `f04b1d714ce6deaab76d9e44ff99923c98545184` — matches the pinned live head exactly (primary checkout, no worktree needed). All five pinned lineage commits (`cb277b8f`, `7dc56112`, `c48bfd80`, `432ed8f3`, `d9ac9596`) verified present via `git cat-file -e`.

`DirectiveRegistry.load().evaluate_task_refs(M4-T021)` reproduced directly: `ok: true`, `applicable_ids == cited_ids == [D-045-R002, D-045-R008, D-045-R009, D-046-R001, D-046-R002]`, `missing_ids: []`. Confirms the five-requirement scope named in the task.

## (1) Restamp ruling

Recomputed `project_control._task_git_identity(M4-T021, reviewed_sha='f04b1d71')` myself: returns `7413f6e4f3594881e1b206aba19c094ef5ee965e9dc15ab3d1436c31fbe9dbd0`, tree clean, **no error**. This is byte-identical to `content_manifest_sha256` recorded in the G2, G3, G4 gate records (`project-control/gates/M4-T021-G{2,3,4}.json`, reviewed_sha `14af4e20…`) and the G5 record (`M4-T021-G5.json`, reviewed_sha `275c166c…`). `git diff d9ac9596 f04b1d71 -- <3 allowed_paths>` = empty (reproduced directly) — no commit after the orchestrator's docstring correction touched any allowed_path. `allowed_paths`/`forbidden_paths`/`directive_refs` in `project-control/tasks/M4-T021.json` are byte-unchanged from the contract commit `ccc01012` through HEAD (only `producer_agent`, `reviewer_agents` — deliberately corrected mid-flight at `88ad3a9f` to add `security-reviewer`, matching the pre-authorization note — `status`, `progress_percent`, `progress_log`, `worktree`, `updated_at` changed).

**Ruling: restamp to `f04b1d71` is PRE-AUTHORIZED and already satisfied.** General condition for any later head H: valid iff (i) no commit between `d9ac9596` and H touches any of the three allowed_paths, (ii) `_task_git_identity(M4-T021, reviewed_sha=H)` continues to return `7413f6e4…` with no error/clean tree, and (iii) `allowed_paths`/`forbidden_paths`/`directive_refs` remain byte-unchanged from what all five gates reviewed.

## (2) Requirement-by-requirement verdicts

| Requirement | Verdict | Evidence I personally reproduced |
|---|---|---|
| **D-045-R002** | **PASS** | Read `services/api/app/connectors/wide_street_buffer_engine.py` in full at HEAD: `STATUS_PRECONDITIONS_NOT_ATTESTED` gate (lines 636–669, VALUE-gated not presence-gated), `STATUS_NO_WIDE_SEGMENTS_PROVIDED` (671–693), typed `WrongCRSError`/`InvalidGeometryError`/`MalformedAttestationError` — every non-computable path refuses, none manufactures a number. Ran `python -m pytest services/api/tests/connectors/test_wide_street_buffer_engine.py -q`: **40/40 pass**, including all 4 EC-5 truth-table combinations, 4 CRS fail-closed tests, empty-set honesty test, EC-4 exact-tangency test (no `BOUNDARY_TOLERANCE_FT` reference — confirmed `"BOUNDARY_TOLERANCE_FT" not in dir(engine)` assertion present and passing). |
| **D-045-R008** | **PASS** | `git show --stat ccc01012`: directive digest resync (D-045 + D-046 manifest.json/requirements.json) landed in the SAME commit as task creation, G0 report, placeholder seeding (c14 discipline). Dependency ordering verified: M4-T020 `status: accepted`, `accepted_at: 2026-09-14T08:26:04Z`, 49 seconds before M4-T021 `created_at: 08:26:53Z`. `git diff --stat ccc01012 f04b1d71 -- "services/api/app/rules/**"` = empty (B7 genuinely untouched). Single bounded 3-file task, 5 gates recorded. |
| **D-045-R009** | **PASS** | `git diff --stat ccc01012 f04b1d71 -- <9 forbidden connector/rule/dependency files>` = **empty**, reproduced directly across the ENTIRE lineage (contract→producer→rework→orch-correction), not from any report. Zero new dependencies (`pyproject.toml`/`requirements.in`/`requirements.txt` untouched). Module docstring (lines 97–101, read directly) states results stay "DRAFT-adjacent... feeding a rule that itself remains DRAFT/needs-review until G6." |
| **D-046-R001** | **PASS** (judgment call, see ruling (c) below) | Task `worktree: wt-m4t021`; progress log 09:05:42Z records the D-060 deviation transparently. I independently found genuine concurrency: `M5-T027` (worktree `wt-m5t027`, claimed 08:43:05Z) and `M5-T028` (worktree `wt-m5t028`, claimed 09:22:44Z) both ran in isolated worktrees overlapping M4-T021's own active window (09:05–09:59Z) — 3 disjoint tasks, 3 isolated worktrees, one morning. |
| **D-046-R002** | **PASS** | Computed pairwise `allowed_paths` intersections among the three concurrent tasks myself: M4-T021∩M5-T027 = ∅, M4-T021∩M5-T028 = ∅, M5-T027∩M5-T028 = ∅. No shared surface (task/gate JSON, directive manifests, `state.json`) was edited by more than one producer — only the orchestrator, sequentially. |

## Rulings (a)–(d)

**(a) EC-5/EC-6/EC-4/EC-2 vs. R002's "honest, never manufactured" text.** Confirmed by direct source+test read: the rework replaced a presence-only EC-5 gate with a genuine VALUE gate mirroring `dcm_street_width_policy`'s `DECISION_UNRESOLVED` mechanism — a caller who hasn't attested returns `STATUS_PRECONDITIONS_NOT_ATTESTED` with every buffer field `None`, never a computed-looking answer on unverified legal preconditions. EC-6 (empty input) and CRS/geometry failures are typed refusals, never a coerced default. EC-4 leaves the raw GEOS predicate standing and explicitly documents (not resolves) the open tolerance question, never inventing one via `BOUNDARY_TOLERANCE_FT` (structurally proven absent by AST/token-scan, verified passing). EC-2 documents the excluded-ambiguous-segment under-claim on every result. This satisfies R002's actual text more strongly than the original (FAILED) design.

**(b) D-045-R009 across the whole lineage.** Verified via restricted `git diff --stat` spanning `ccc01012..f04b1d71` (contract through current HEAD, i.e., producer + rework + orchestrator correction all included) against every forbidden connector/rule/dependency path — zero changes. This is the correct, complete-lineage check (not a single-commit spot check).

**(c) D-046-R001 despite the loop-substitution deviation — explicit judgment.** D-046-R001's text requires "concurrent writing producers on disjoint D-045 tasks, each dispatched into its own isolated worktree under the standing orchestration policy" — it names a *mechanism* (isolated-worktree parallel dispatch), not a specific *dispatcher* (the loop). The D-053 supervisor loop's Fable-exhaustion safe-stop is a failure of one dispatch channel; the orchestrator's substitution (an orchestrator-dispatched, isolation-worktree, unnamed producer, under the disclosed D-060-R001 deviation, transparently logged rather than hidden) preserved exactly the mechanism the requirement specifies, and I independently confirmed real 3-way concurrency in the same window. **Ruling: D-046-R001 is SATISFIED, not merely excused** — the deviation changed *who* dispatched, not *whether* the parallel-isolated-worktree invariant held.

**(d) Orchestrator's tagged docstring edit vs. producer/reviewer separation.** I independently reproduced `git diff f640805b d9ac9596`: exactly 2 files (`M4-T021-G4-delta-attestation.md`, orchestrator-owned report; `wide_street_buffer_engine.py`, production source) — confined entirely to the `Ec5AttestedPreconditions` class docstring, zero executable tokens changed, superseded text preserved with an explicit SUPERSEDED marker (not deleted). Both independent reviewers (code-reviewer, qa-engineer — neither is the orchestrator or the producer) separately re-verified this exact edit at `d9ac9596` against the gate logic each had already independently traced to source, and both gave CONFIRMED identity-carry attestations. **Ruling: compatible, narrowly.** The orchestrator is not the producer and did not self-certify; two independent parties re-checked the edit before it carried into PASS. This matches a repeated, disclosed pattern already established in this project's own control-plane practice (`88ad3a9f`, and similarly in M5-T027/M5-T028's own history). It should remain confined to comment/documentation-only corrections with full audit trail + mandatory dual re-attestation — not a precedent for orchestrator edits to functional code — and nothing in this instance crossed that line.

## (3) Material-identity statement

Producer commit `cb277b8f` cherry-picked byte-identical into `7dc56112` (`git diff cb277b8f 7dc56112 -- <3 allowed_paths>` = empty, reproduced). Rework commit `c48bfd80` cherry-picked byte-identical into `b9f8393b` (same check, empty). Orchestrator correction `d9ac9596` touches exactly 2 files, code change confined to one docstring (reproduced). Content-manifest identity `7413f6e4f3594881e1b206aba19c094ef5ee965e9dc15ab3d1436c31fbe9dbd0` is stable and independently reproducible at HEAD `f04b1d71` via the CLI's own `_task_git_identity`, matching all four post-producer gate records exactly, tree clean.

## (4) Harness runs and blocking discrepancy

- `python tools/validate_directive_compliance.py --check` — reproduced directly: exit 0, **no output** (script is "quiet on success" per its own `--check` help text) = registry valid, source digests match, append-only intact, c6 in-regime reference coverage (including M4-T021) passes.
- `python tools/test_project_control.py` — reproduced directly: **23/23 groups PASS**.
- `python tools/test_directive_reminder.py` — reproduced directly: **12/12 tests OK**.
- `python tools/test_directive_compliance.py` — **could not complete within available session time** (three attempts: default 300s, explicit 1500s, and a targeted `PositiveTests`-only subset that itself exceeded 60s mid-run on `test_real_registry_valid`). Named missing item: the full pass/fail count from this specific script. I substituted direct reproduction of the exact mechanisms it exercises — `validate_directive_compliance.py --check` (clean), live `evaluate_task_refs(M4-T021)` (ok:true), live `_task_git_identity` recomputation at HEAD (exact match to all four gate records) — each of which I ran myself against the live repository, not synthetic fixtures. This does not gate any of the five requirement verdicts above, each resting on direct primary-source/test/git evidence. **Recommend the orchestrator capture this script's full output via a longer-budget background run** before treating the directive-compliance tooling's own regression suite as separately confirmed; it is a general infrastructure check, not task-specific evidence.

No other blocking discrepancy found. Full connectors suite (`python -m pytest services/api/tests/connectors -q`): 792/792 pass. `ruff check .`: clean. `python tools/modularity_check.py --check`: 0 failures, 18 warnings (including `wide_street_buffer_engine.py` at 754 review-signal lines — non-blocking, and both G3 and the security reviewer independently ruled "leave as-is, no split" with the constraint that B7/override-table logic must land as its own module).

## Overall verdict: **PASS**

All five applicable requirement IDs (D-045-R002, D-045-R008, D-045-R009, D-046-R001, D-046-R002) independently verified SATISFIED against primary repository evidence I reproduced myself. Restamp to live HEAD `f04b1d71` is pre-authorized under the stated conditions. One non-blocking harness item (`test_directive_compliance.py` execution-time) flagged for orchestrator follow-up capture, not a bar to acceptance.
