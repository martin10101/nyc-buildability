# M5-T078 / M5-T079 — directive-compliance verification (directive-compliance-verifier "dcv-web", read-only; joint DCV)

> Transmission history: pinned at fa7e5fae, delivered as five SendMessage parts (1/5..5/5) ending with END-OF-REPORT;
> no truncation. Part 1 carries the identity-level restamp predicate (c5dd725c / 747ee069) with broad disjoint-peer
> tolerance. Joined verbatim by the orchestrator (transport wrapper tags removed only); saved identically as
> M5-T078-DCV.md and M5-T079-DCV.md. The verifier's validator run: VALIDATOR_EXIT=0. Part 5 rules the D-085
> subagent-model deviation immaterial to every requirement row (the recorded gates are fresh Opus 4.8 re-reviews).
> Orchestrator predicate re-check at the accept head: both identities reproduced; evaluate_task_refs ok.

---

DCV M5-T078 + M5-T079 — part 1/5 (dcv-web, read-only).

PINNED HEAD at start: fa7e5fae8c9d0ae63851481f5f0a21c32cafa2aa, branch candidate/D-024-mrl-option-b (not main; main=d8b3899f, HEAD not its ancestor).

RESTAMP PRE-AUTHORIZATION (up front): GRANTED for both tasks, blob-level, with broad disjoint-peer tolerance, and the orchestrator MAY add my DCV rows.
- M5-T078 predicate: my PASS holds at any accept-time HEAD where _task_git_identity(T078) == c5dd725ccedd73424ea5ca0a9f87fa926f4a7d5125480251306d7683caf1ce24 (the 6 apps/web blobs + the producer-report blob byte-unchanged). A disjoint peer commit touching none of T078's 7 allowed_paths does NOT void my rows; restamp reviewed_sha to live HEAD.
- M5-T079 predicate: same, identity == 747ee06918acc75ded540783f9efa8778791eec27a2d8bbd0497c985b769d13d over its 7 allowed_paths.

EVIDENCE BASE (all reproduced myself, primary):
- evaluate_task_refs (reg.load_registry().evaluate_task_refs): both ok=True; applicable_ids == cited_ids == frozen applicable_requirements; missing/invalid/unresolved all empty. T078={D-066-R001,D-076-R002,D-082-R001,D-087-R001,D-087-R002}; T079=those +{D-083-R001,R002,R004}. Confirmed against each requirement's applicability.task_ids (D-083 trio lists only T079+T070 — matches T078's non-citation).
- Frozen identity: _task_git_identity at HEAD == each frozen reports/<task>.json content_manifest_sha256 (c5dd725c / 747ee069). So content is byte-stable submit→HEAD.
- Blob identity: all 12 code/test blobs byte-IDENTICAL across CI-green head 6c79cd88, HEAD fa7e5fae, G3 sha f6116a5c, G4 sha cdd62c5c, submit sha 9f355fe1 (git rev-parse per file).
- CI run 35989704760 @ 6c79cd88: web (lint+typecheck+build) SUCCESS, web-e2e SUCCESS, web-dependency-security SUCCESS, control-plane SUCCESS. Binds the exact frozen code.
- Harness: python tools/validate_directive_compliance.py --check → VALIDATOR_EXIT=0 (run once, direct exit code). Did NOT run test_directive_compliance.py.

Requirement rows in parts 2 (T078) and 3 (T079); gates + sweep + Opus-5.5 ruling + verdicts in parts 4-5.

---

DCV part 2/5 — M5-T078 requirement rows (5/5 SATISFIED; primary evidence each).

- D-066-R001 (obligation, code-graph nav block) SATISFIED. tasks/M5-T078.json inputs[8]: "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph REGENERATED at this contract seam: 817 files/17027 nodes/7441 edges)" — consumers/depth-2/impact for ProposalOutlineDraw.tsx + ProposalOutlineMap.tsx, and instructs `query.py --no-regen impact` before sweeps; advisory-verified-in-source caveat present.

- D-076-R002 (obligation, proposal honesty) SATISFIED. ProposalOutlineDraw.tsx: omission never silent — omittedRowsClause():60, omittedOnConvert "captured at convert time so the post-convert status can name the omitted count truthfully (never a silent drop)" :118-120, post-convert names converted AND omitted :428-433; per-row incomplete markers + aria-invalid :222/:335-354; drawing total labeled "a UI row tally, never a zoning number" :61 and "converted to official-grid feet on the server" :296. Distinct value/gap states preserved.

- D-082-R001 (authorization: B-track outline-drawing slice; no persistence, phase C/D not released) SATISFIED. Work is the B3-deferred outline drawing + bridge feeding the SAME in-memory draft (additive onAdopt; grep found no localStorage/sessionStorage/scenarios-save/PDF import). allowed_paths are web-only; services/api, apps/web/e2e, outline-bridge-api.ts, app/ all forbidden.

- D-087-R001 (obligation, capacity via normal gated packets) SATISFIED. Contracted/claimed/gated ledger packet with G0/G2/G3/G4 records; ran as orchestrator-dispatched subagent producer after the B-026 lane refusal (progress_log 07:55); no state or gate skipped.

- D-087-R002 (prohibition, pairwise-disjoint scope + isolated worktree) SATISFIED. Reproduced programmatically: T078∩T079 = empty; T078 scope disjoint from all 44 other live (non-accepted) packets; worktree wt-m5t078.

SCOPE CORRECTION (T078): apps/web/src/app/property/architect.css added to allowed_paths at the rework seam — logged progress_log 09:57 + LIFECYCLE NOTE 10:50, G0 re-recorded (114e5e56, readiness). It adds exactly ONE selector `,.architect-shell button[aria-disabled="true"]` to restore the disabled look its own aria-disabled migration removed. Legitimately recorded; DISJOINT — architect.css is declared by ONLY M5-T078 among all 46 live packets (reproduced). No other packet's scope is touched.

---

DCV part 3/5 — M5-T079 requirement rows (8/8 SATISFIED; primary evidence each).

- D-066-R001 (nav block) SATISFIED. tasks/M5-T079.json inputs[8]: nav block for MaxEnvelopePanel.tsx + max-envelope-api.ts (consumers ArchitectEntry.tsx:31 forbidden + tests in scope; depth-2 app/property pages forbidden), query.py instruction present.

- D-076-R002 (honesty) SATISFIED. MaxEnvelopePanel.tsx: proposed-label discipline (adopt seeds "Generated building option", "Every value stays labeled proposed" :189-201); street width SERVER-determined, never client-inferred, seed "" :192-196; could-not-check distinct from value; no passing subset shown as whole-building approval.

- D-082-R001 (authorization; route unmounted, not persisted) SATISFIED. max-envelope-api.ts:2/6 — "INTERNAL, UNMOUNTED max-envelope route" / "flag-gated, UNMOUNTED POST /api/v1/max-envelope"; computed maximum presented+checked live, not persisted; services/api forbidden+untouched.

- D-083-R001 (prohibition: interim vocab, no unqualified max-allowed copy) SATISFIED. "Preliminary development limits" (:303/:312/:328) + "Generated building option" (:189/:228) present; grep for "maximum allowed building"/"demonstrated maximum" in MaxEnvelopePanel.tsx + max-envelope-api.ts → ZERO matches.

- D-083-R002 (obligation: three claim classes distinguished) SATISFIED. Regulatory limit = the "Preliminary development limits" ceilings; generated option = "Generated building option" (comment :32 "the only building-shaped claim, labeled a checked" option); demonstrated maximum unavailable (not presented).

- D-083-R004 (prohibition: no unrestricted green) SATISFIED. envelopeAggregateIsComplete() :183; aggregate class is-checked/is-incomplete + data-complete + role=status :211-218; comment :35 "no unrestricted green/complete aggregate"; contract copy ":152-154 ...stays incomplete"; any gap row or contract violation fails complete (G4-verified mutant).

- D-087-R001 (gated capacity) SATISFIED. Contracted/claimed/gated packet; subagent producer post-B-026; no gate skipped.

- D-087-R002 (disjoint + isolated worktree) SATISFIED. T079∩T078 empty; disjoint from all 44 other live packets; worktree wt-m5t079.

Bonus primary check (D-083-R004 XOR / DB-050(d)): DimensionRow classifyDimensionRow() :95-98 — a row with BOTH or NEITHER of binding_value/gap_reason (raw-presence flags, not truthiness) renders a typed contract-failure that NEVER shows a value (:121-156); exhaustive Record<EnvelopeGapReason,string> :62-67. Verified in source.

---

DCV part 4/5 — gates, frozen identity, prohibited-action sweep (both tasks).

REQUIRED GATES (G0,G2,G3,G4) — all current top-level result PASS; FAIL entries are in history[] only (first-pass), never the current result:
- G2 self_check (orchestrator) carries the frozen manifest (c5dd725c / 747ee069) at sha 9f355fe1.
- G3 code-reviewer, role=independent_review, PASS, report *-G3-rework.md, manifest = frozen, sha f6116a5c. Independent (≠ producer frontend-engineer).
- G4 qa-engineer, role=independent_review, PASS, report *-G4-rework.md, manifest = frozen, sha cdd62c5c. Independent.
- G0 administrative PASS (readiness manifest, expected to differ).
No current gate record carries a stale pre-rework MATERIAL manifest. I read accept() (project_control.py:1207-1222): it checks only current result==PASS plus, for independent gates, role==independent_review and reviewer!=producer — it does NOT read gate content manifests for identity. Accept-time identity binds solely via the frozen submission report (line 563: reports/<task>.json content_manifest_sha256 == live identity), which matches HEAD for both. So G0's differing manifest is NOT an accept-blocker.

HJ re-review (not a required ledger gate; reviewer_agents extra): both *-HJ-rework.md PASS on fresh Opus 4.8; HJ-A/HJ-6 advisories are PRE-EXISTING, not introduced, routed to D-086/mount.

PROHIBITED-ACTION SWEEP — clean:
- Not accepted: both in state.json active_tasks (NOT accepted_tasks); task status awaiting_gate.
- No verification.json rows name either task yet (grep of directives/*/verification.json empty).
- Not on main: HEAD on candidate/D-024-mrl-option-b; git merge-base --is-ancestor HEAD main → false.
- PR #241 untouched: OPEN, headRef task/M5-T002-scenario-endpoint, updatedAt 2026-08-20 (unrelated DO-NOT-MERGE pilot).
- Blockers: 5 open, NONE word-bounded-reference M5-T078 or M5-T079 in affects OR detail (replicated _blocker_references).
- Dependencies accepted: M5-T070 accepted, M5-T071 accepted.
- Nothing merged/dispatched/deployed/installed/purchased/closed for these tasks.

Verdict + Opus-5.5 ruling in part 5.

---

DCV part 5/5 — Opus-5.5 deviation ruling + verdicts.

OPUS-5.5 DEVIATION RULING: does NOT affect any requirement row for either task. Per project-control/reports/D-085-subagent-model-deviation-2026-09-24.md, an orchestrator `model:"opus"` param (08:55–10:05Z) resolved to Opus 5.5 and overrode the pinned Opus 4.8 on the T078/T079 first-pass reviewers (cr-web/qa-web/hj-web) AND the two rework producers; from 10:20Z dispatches reverted to Opus 4.8. Why it is immaterial:
1. The RECORDED, BLOCKING gates are the re-reviews — G3 (code-reviewer), G4 (qa-engineer), HJ — all fresh Opus-4.8 reviewers (reviews recorded 14:37–14:41Z, well after the 10:20Z fix), all PASS.
2. The Opus-5.5 first-pass reviews were FAILs that only triggered rework; superseded, retained in history[] only — a wrong-model FAIL that forces stricter rework is harmless.
3. Producer model is immaterial to compliance: the rework OUTPUT is bound by deterministic CI (web+web-e2e SUCCESS @ 6c79cd88 over byte-identical blobs), independent Opus-4.8 re-review, and my own primary-source inspection — none of which depends on which model wrote the code.
4. No owner directive or open blocker mandates an Opus-4.8 redo of these two tasks (owner MAY still elect one per the deviation report — that is an owner option, not a compliance defect). I flag it as a note, not a VIOLATED/UNVERIFIABLE row.

No requirement is VIOLATED or UNVERIFIABLE for either task. All applicable rows SATISFIED on reproduced primary evidence; identity/gates/CI/validator all consistent; prohibited-action sweep clean.

M5-T078 DCV VERDICT: PASS 5/5
M5-T079 DCV VERDICT: PASS 8/8

Recommendation: both are acceptable at HEAD under the blob-level predicates in part 1; the orchestrator may write my DCV PASS rows into each directive's verification.json (restamp reviewed_sha to live HEAD; identities c5dd725c / 747ee069) and proceed to accept.

END-OF-REPORT
