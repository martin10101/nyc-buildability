# M5-T090 — directive-compliance verification (directive-compliance-verifier "dcv-t090", read-only)

> Transmission history: pinned at fe254eee, delivered as four SendMessage parts. Parts 1-3 arrived at 14:40-14:41Z;
> part 4 (sweep, findings, harness, verdict) arrived at 15:31Z after an orchestrator request for the missing final
> part, ending with END-OF-REPORT; no truncation. In that part the verifier re-confirmed the identity f53b0781 and
> the three allowed-path blobs at the live head 9c44b68d. Joined verbatim in delivery order by the orchestrator
> (transport wrapper tags removed only). Validator EXIT 0 (one run) plus a by-hand digest check at the settled head.

---

M5-T090 DCV — PART 1/4 (restamp pre-auth, frozen identity, applicability, gates)

PINNED HEAD at start: 6c79cd88. HEAD advanced to fe254eee during review (single peer commit "M5-T089 unit" — touched NONE of this task's paths; log 6c79cd88..HEAD over the three allowed_paths is empty).

RESTAMP PRE-AUTHORIZATION (up front): I pre-authorize a blob-level restamp. My verdict holds at any later HEAD provided ALL of:
(a) the three allowed_paths are byte-identical — package.json blob 19328b65, package-lock.json blob a8398ec5, producer-report blob 4a7752c4;
(b) reports/M5-T090.json content_manifest_sha256 stays f53b0781… and _task_git_identity recomputes to f53b0781…;
(c) evaluate_task_refs(task) stays ok=true with applicable==cited=={D-066-R001, D-087-R001, D-087-R002, D-087-R003, D-087-R009, D-087-R011}.
Broad disjoint-peer tolerance (explicit): other tasks' files/material, other directives' registry binds, same-directive (D-087) amendments that leave this task's evaluate_task_refs ok, and the orchestrator appending MY verification rows — none of these, alone or together, voids the verdict.

FROZEN IDENTITY — reproduced myself (not from any claim):
- pc._task_git_identity(reg, task) @HEAD(fe254eee) = f53b0781a63ffe2341f53cf3f592415a55e0cd108bcc1da37055c30d726d9cbb
- Direct recompute @submission sha 2e444920 (require_clean=False) = same f53b0781.
- reports/M5-T090.json content_manifest_sha256 = f53b0781 ✓ | G2 stamp f53b0781 ✓ | G4 stamp f53b0781 ✓ | G5 stamp f53b0781 ✓. All four equal.
- Blob stability: package.json/lock/report blobs byte-identical at 2e444920 and HEAD (19328b65 / a8398ec5 / 4a7752c4).

APPLICABILITY — reproduced via directive_registry.load_registry().evaluate_task_refs(task): ok=True; applicable_ids == cited_ids == [D-066-R001, D-087-R001, D-087-R002, D-087-R003, D-087-R009, D-087-R011]; missing=[]; invalid_refs=[]; reasons=[]. Cited set == applicable set exactly.

GATES (all PASS): G0 orchestrator/administrative @5e9dbd07; G2 orchestrator/self_check @2e444920; G4 qa-engineer/independent @4c999e15; G5 security-reviewer/independent @4c999e15. Producer=frontend-engineer ≠ both independent reviewers (qa-engineer, security-reviewer), both listed in reviewer_agents. G2/G4/G5 all stamp f53b0781.

Requirement rows follow in Part 2.

---

M5-T090 DCV — PART 2/4 (requirement rows, primary evidence I reproduced)

D-066-R001 (obligation — code-graph navigation block in packet) → SATISFIED.
Primary: tasks/M5-T090.json inputs[4] (line 13) carries the block: "no source consumes these packages yet; the first consumer will be a later 3D viewer under apps/web/src/components/architect/… Run tools/code_graph/query.py --no-regen impact <path> before sweeps; graph ADVISORY." reports/M5-T090-G0.md:26 records the graph regenerated at the seam (817 files/17386 nodes/7525 edges) with the block naming consumers + the --no-regen instruction. Observed: block present and correctly says nothing consumes the pkgs yet (I confirmed independently: 0 lock consumers, and the pkgs are leaf/first-admission). 

D-087-R001 (obligation — contracted/claimed/gated concurrent packet, no state or gate skipped) → SATISFIED (this packet's subagent-producer share).
Primary: gates/M5-T090-G0.json result=PASS reviewed_sha=5e9dbd07; tasks/M5-T090.json progress_log claimed@20% + worktree field = C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t090 (full path); producer report line 4 base=114e5e56; manifest.json audit_log 10:45 wave-2 bind lists M5-T088/89/90/91/92 run concurrently; lifecycle G0→G2→submit→G4→G5 intact. B-026 (open) names only "D-087-R001 (the loop-lane share)" in its affects; its record has no M5-T090 reference (detail-has-T090=False) → does not gate this subagent packet, consistent with the T077/T084 rows that leave the loop-lane share open under B-026.

D-087-R002 (prohibition — pairwise-disjoint writable scopes, isolated worktree) → SATISFIED.
Primary: reports/M5-T090-G0.md disjointness table = EMPTY overlap vs all 21 live/frozen neighbors. I reproduced the material diffs by git name-status: 80f17a86 = apps/web/package.json + project-control/reports/M5-T090-producer-report.md; 2e444920 = apps/web/package-lock.json ONLY. Exactly the 3 allowed_paths; none of forbidden_paths (apps/web/src, apps/web/e2e, .npmrc, services/, packages/, .github/) touched. One worktree wt-m5t090; one producer.

Part 3 (R003, R009, R011 — the dependency-security core) follows.

---

M5-T090 DCV — PART 3/4 (R003, R009, R011)

D-087-R003 (authorization — 3D released; this is the named stack) → SATISFIED.
Primary: .claude/rules/3d-ui-expansion.md:19 = "Three.js + React Three Fiber + Drei for parcel-level 3D"; admission adds exactly three@0.186.0 + @react-three/fiber@9.7.0, drei deferred. Hold-notice §2.3 records the D-087 3D release. Necessity vs zero-dependency MapLibre fill-extrusion argued in the producer report (non-prismatic sky-exposure planes, per-object opacity/cutaway, no MapLibre glTF loader, camera framing); G5 ruled §5 necessity SATISFIED.

D-087-R009 (prohibition — boundaries unchanged; no other dep version changed; no src/e2e/route/services) → SATISFIED.
Primary — MY OWN lock diff 2e444920^..2e444920: exactly 13 NEW node_modules entries, 0 removed, 0 version-changed existing; only 3 dev→prod flag flips (@babel/runtime, @types/react, csstype; versions unchanged). Material touches only the 3 allowed paths — no services/, .github/, src/, e2e, route, .npmrc. PR #241 OPEN/unmerged; max-envelope route stays unmounted.

D-087-R011 (authorization — full admission, NO waiver) → SATISFIED. Every clause reproduced on primary evidence:
- exact pins: git show 80f17a86 package.json = +fiber 9.7.0, +three 0.186.0, zero range chars.
- age floor 604800s: CI web-dependency-security committed-lock age gate = success on the WHOLE lock @4c999e15; per-version three 15.6d / fiber 54.7d, youngest transitive use-sync-external-store 14.7d.
- advisory-free every severity: same CI job's npm audit low + JSON-total-0; OSV+GitHub empty for both w/ live positive control (three@0.124.0→GHSA-fq6p).
- integrity match: all 13 lock entries carry integrity; three sha512-cr/fIM2ddMSV…, fiber sha512-EWm9FwcaOZQu… = registry dist.integrity.
- G5 provenance of all 13: reports/M5-T090-G5.md enumerates the 13 numbered packages; VERDICT PASS.
- lockfile only by the workflow: run 35985974452 = "Generate web lockfile" (workflow_dispatch, success, branch task/M5-T090-3d-web-deps) committed 82d2e54d (github-actions[bot]); its lock blob a8398ec5 == 2e444920's byte-for-byte.
- pre-screen versions: docs/research/3d-web-deps-prescreen-2026-09.md:28-29 name three 0.186.0 / fiber 9.7.0 (9.8.0 FAILS age).
- CI green on a COMPLETED pushed head carrying this lock: run 35987709331 @4c999e15 (lock blob a8398ec5) — all 18 jobs success, incl. web-dependency-security AND control-plane (ADR-005). Resolves the 023294ec cancelled-jobs note.
- no waiver applied.

Part 4 (sweep + findings + validator + verdict) follows.

---

M5-T090 DCV — PART 4/4 (sweep, findings, harness, verdict)

PROHIBITED-ACTION SWEEP (all clear):
- Not accepted: tasks/M5-T090.json status=awaiting_gate; 0 verification rows for M5-T090 in D-087 and D-066 verification.json.
- Not on main: branch candidate/D-024-mrl-option-b.
- PR #241 untouched: state=OPEN, mergedAt=null, closedAt=null (the unrelated M5-T002 "DO NOT MERGE" PR).
- No open blocker names M5-T090: grep empty; B-001/B-010/B-011/B-026 records have no M5-T090 reference. B-026 (open) covers only "D-087-R001 the loop-lane share", not this subagent packet.
- Nothing merged/deployed/installed/purchased/closed for this task.

HARNESS EVIDENCE:
- validate_directive_compliance.py --check: single run, VALIDATOR_EXIT=0 (clean PASS; direct exit code, no |tail).
- It ran near the pin head; binds landed since, so I hand-checked manifest digests at the SETTLED head 9c44b68d: D-087 requirements da567a4d + source-001 34c3dd64 + source-002 4eea66c6 all MATCH; D-066 requirements 9d36184a + source MATCH; D-076 requirements f0cbc139 + source MATCH. No transient c14.
- CI control-plane job (ADR-005 regression): success at pushed head 4c999e15 (run 35987709331).

IDENTITY RE-CONFIRM AT LIVE HEAD 9c44b68d (per your request): reports/M5-T090.json content_manifest_sha256 = f53b0781a63ffe2341f53cf3f592415a55e0cd108bcc1da37055c30d726d9cbb (unchanged), and the three allowed-path blobs are byte-identical to the frozen set (package.json 19328b65, lock a8398ec5, report 4a7752c4). Identity is a deterministic function of those blobs; it remains f53b0781 (reproduced =f53b0781 at fe254eee in Part 1). Predicate holds.

FINDINGS (none blocking):
- F1 (cosmetic): bot lock commit 82d2e54d / cherry-pick 2e444920 carry the message "…(M0-T019 security tree, validated)" — the generate-lockfile workflow's fixed template label, not this task's id. Provenance is correct: authored by github-actions[bot] on run 35985974452 (branch task/M5-T090-3d-web-deps), blob-identical to the reviewed bot lock. No requirement impact.
- F2 (advisory, inherited from G4): no committed test pins the two exact versions or rejects range chars in apps/web/package.json; the whole-tree age gate + audit protect the tree regardless. Follow-up guard, not a current defect.

Requirement verdicts (each on primary evidence I reproduced): D-066-R001 SATISFIED; D-087-R001 SATISFIED; D-087-R002 SATISFIED; D-087-R003 SATISFIED; D-087-R009 SATISFIED; D-087-R011 SATISFIED. No VIOLATED, no UNVERIFIABLE, no BLOCKED.

M5-T090 DCV VERDICT: PASS 6/6

END-OF-REPORT
