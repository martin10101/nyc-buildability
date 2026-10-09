# M0-T187 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `ba16974bbb838fb14446848c406a3c0e91d54462` (branch `task/wave6-corrections-after-reviewer-check`, PR #466, review copy `/root/project/rv-w6-c`). Directive D-009. The verifier is an AI agent; it was not the producer and wrote none of the records. It ran at the same time as the independent code review (gates G3/G4) and the security review (gate G5) of the same head; its verdict is on the requirement and its binding, not on those gates.
Applicable row for this task (`evaluate_task_refs`: applicable == cited): D-009-R017.

## Verdict: PASS.

Required corrections, in the verifier's words: None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's acceptance script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.
Captured facts it read: `/root/project/lanes-runtime/owner-docs/session-2026-10-08a/review-T187/` (the lock workflow's run record and job log, the base lock, the blob list).

Transmission: the verifier's return arrived in one part, received 2026-10-08T01:07:00Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T187 (directive D-009, row D-009-R017)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier); this is an automated evidence reproduction, not a human or professional review. I produced none of the work or records and treated every producer/evidence/gate/prompt claim as unverified.

(1) HEAD VERIFIED
`git rev-parse HEAD` in /root/project/rv-w6-c = ba16974bbb838fb14446848c406a3c0e91d54462; working tree clean. Range 1763e505..HEAD = 4 commits: 2b8e59f2 (producer pin, martin10101), 01ff4065 (github-actions[bot] lock), 09b536c4 (producer report), 5690eab9 + ba16974b (orchestrator ledger seams).

(2) D-009-R017 — PASS
Row text (requirements.json L709): regenerate apps/web/package-lock.json via CI (generate-lockfile.yml), NOT by hand; the fresh lock validated (npm ci integrity + blocking npm audit total==0 + FE-S9 age gate + FE-S11 npm CLI advisory) before the bot commits. classification=harness; applicability.task_ids include M0-T187.
 - The only commit touching apps/web/package-lock.json in 1763e505..HEAD is 01ff4065a, whose author AND committer are github-actions[bot] with parent 2b8e59f2c, and the lock blob at HEAD (f2c107923913be5d6d300b9b2e18cee09ea418a5) is byte-identical to the blob that bot commit wrote, so the lock was produced by CI and not by hand.
 - The producer pin commit 2b8e59f2 left the lock blob at the base value 7f5dd06b (it changed only package.json "next":"15.5.24"->"15.5.27", one line), proving no human hand wrote the lock.
 - .github/workflows/generate-lockfile.yml is byte-identical at claim head, bot commit and HEAD (blob 8f89e966) and orders npm ci integrity (L50-51), blocking npm audit --audit-level=low (L52-53), audit JSON total==0 (L56-69), FE-S9 committed-lock age gate (L70-71) and FE-S11 npm CLI advisory (L72-73) ALL before the single commit step (L74-85).
 - In captured run 37709673533 / job 113092375556 (dispatched on 2b8e59f2) each validation passed before the commit: npm ci "added 314 packages" (log L148), "found 0 vulnerabilities" (L156), "total vulnerabilities == 0 across all severities" (L172), age-gate header "== package-lock.json (392 unique registry packages) ==" (L178) with "RESULT: PASS — every committed registry package is >= 7 days old and integrity-verified" (L572), and "RESULT: PASS — no advisory affects npm@11.18.0" (L578); the bot commit/push 2b8e59f2..01ff406 is step 11 (L591-594).
 - The age gate PASSed next@15.5.27 at L481 "uploaded=2026-09-30T16:19:50.862Z age=635356s (7.35d)" (> 604800 s), and @next/env and the eight @next/swc-* at 15.5.27 at L288-296 (~636000 s / 7.36 d each).
 - My own entry comparison of the base lock (7f5dd06b; identical to the captured base and to candidate/D-024) vs the head lock (f2c10792): 397 package entries each side, zero added, zero removed, exactly 11 changed — the root "" entry's dependency on next, node_modules/next, node_modules/@next/env and the eight node_modules/@next/swc-* (all 15.5.24->15.5.27); the only extra delta is the sharp range ^0.35.3->^0.35.4 inside next's own optionalDependencies (upstream metadata that the already-locked sharp 0.35.5 satisfies). Nothing outside the next family changed.
 - Both CI runs at the frozen head report web-dependency-security = success: pull_request run 37710422241 and push run 37710417807 (headSha ba16974b), alongside web and web-e2e success.

(3) BINDING B1–B5
 - B1 PASS: diff of D-009 requirements.json 95a7ce67->HEAD changes only updated_at (2026-10-06T15:24:03 -> 2026-10-08T00:33:38) and appends "M0-T187" to D-009-R017.applicability.task_ids (now M0-T019, M0-T185, M0-T187); no requirement text changed.
 - B2 PASS: dr.sha256_text_artifact(requirements.json)=2d2e9435506326ef117a4d755a3daf3c5ea41cb4c50adf6fb70b474265d92a07 equals manifest.requirements_content_digest_sha256; audit_log has the 2026-10-08T00:33:38 "applicability_bound" entry (M0-T187 -> D-009-R017, digest resynced same commit, provisional pending row added, no text edited).
 - B3 PASS: verification.json has exactly one M0-T187 row; applicable_requirement_ids == ["D-009-R017"]; its D-009-R017 requirement state pending; verifier "".
 - B4 PASS: reg.evaluate_task_refs(M0-T187) = {ok:True, applicable_ids:['D-009-R017'], cited_ids:['D-009-R017'], missing_ids:[], invalid_refs:[], unresolved:[]}.
 - B5 PASS: reg.derive_applicable(M0-T187) over all 92 active directives yields applicable == {'D-009-R017'}, equal to cited; the uncited set is empty — nothing else applies.

(4) CARRY-FORWARD CONDITION
This PASS may be stamped at a later head WITHOUT re-review while ALL hold: the four allowed-path files keep their blob ids — apps/web/package-lock.json f2c10792, apps/web/package.json d33c9a01, M0-T187-producer-report.md b37635a6, M0-T187-registry-research.md 76e615c6; .github/workflows/generate-lockfile.yml stays 8f89e966 and apps/web/.npmrc stays 80ebc725; and row D-009-R017's text and binding (B1/B2) are unchanged. I tolerate later commits that touch ONLY project-control/** and docs/** (G3/G5 gate records, this verification row, acceptance/other-task records, new owner-message directive sources) and a merge of candidate/D-024-mrl-option-b that changes none of the predicate files.

(5) REQUIRED CORRECTIONS
None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not re-run the generate-lockfile workflow, npm, validate_directive_compliance.py, or the full directive-compliance test suite (forbidden/no network); the run JSON and job log are orchestrator-captured claims, which I cross-checked against the git objects (headSha 2b8e59f2, parent, bot author, commit 01ff406, 41/41 blob diff) and the independent frozen-head CI runs — all consistent.
 - I did not re-fetch registry publish timestamps or the advisory database myself; the age/advisory values are the workflow's machine evidence, not my own network reads.
 - The G3 (code) and G5 (security) gate records do not yet exist and are outside my scope (per my instructions); my verdict covers D-009-R017 and its binding only.
END-OF-REPORT
```
