# M5-T168 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `13221abaec4141f5ac5ba6bc3962bf045f35f4fe` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R639.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 21:12 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T168 (directive D-090, 1 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, evidence-based check, not a human or professional review. I produced none of the M5-T168 work or records; I reproduced each item from primary evidence at the frozen head.

(1) HEAD VERIFIED
 - I read the frozen head 13221abaec4141f5ac5ba6bc3962bf045f35f4fe on branch task/wave24-report-v3 in /root/project/w-wave20 (git rev-parse HEAD confirms it).
 - The head was still 13221aba after my validator run, so no commit landed during the read.
 - The frozen head is not contained in main, so nothing here is merged.

(2) ROWS

ROW D-090-R639 — PASS
 - Source is faithful: source-064-amendment.md owner message 125 says "All required full-suite and security checks must pass in CI for the exact code being accepted or merged; later code changes must receive the relevant checks again"; requirements.json quotes this exactly and adds the orchestrator's reading (CI on the exact head read before any gate/accept/merge).
 - This task's share is met at the gate head: G2/G3/G4 carry reviewed_sha 6dde134598a4 and CI there is green — run 38174034042 (CI, 21/21 jobs incl. "api (ruff + pytest)") updated 21:00:24Z, run 38174034044 (secret-scan) 20:53:16Z, run 38174034115 (context-budget) 20:52:51Z — all completed before the gates were recorded at 21:03:54-55Z, so CI was read first.
 - The reviews were performed at material head 5a8228c1 (CI run 38172084908 = 21/21 success), and the three allowed-path files are blob-identical at 5a8228c1, 6dde1345 and the frozen head, so the reviewed content identity carries to the gate head unchanged.
 - The task's content advances R639: I reproduced S1 at the frozen head (ruff 0.13.0, the CI-pinned version: `ruff check --show-files .` lists render_coverage_matrix.py, `ruff check .` = "All checks passed!" exit 0), and the mutation (respect-gitignore=true) prunes the file (count 0), so the DB-240 gap where a tracked production .py escaped the lint gate is closed and CI green now genuinely covers it; output is byte-identical (committed COVERAGE_MATRIX.md sha256 42120957dc6b… unchanged across base/material/frozen heads; F841 var confirmed unused, E501 fixed by adjacent-literal wrap).
 - What stays open: the orchestrator's acceptance and any merge of M5-T168 must still read CI green at that exact accept/merge head (R639's forward clause); the task is awaiting_gate and not on main, so that future read is the orchestrator's, not mine, to perform.

(3) BINDING B1–B5
 - B1 PASS: the contract commit fc96fd9c appended "M5-T168" (and peer "M0-T193") to R639.applicability.task_ids and changed no requirement text; a field-by-field diff of the R639 record base (b4704161) vs frozen head shows text, source_ref, classification, binding, dependencies, required_harness, required_evidence, producer and independent_verifier all identical — only task_ids grew.
 - B2 PASS: tools/directive_registry.sha256_text_artifact(requirements.json) at the frozen head = f14ea0b9e19ff4eaf85379986c740089bd4c731415f81625dc6600137ae9281f, equal to D-090 manifest requirements_content_digest_sha256; the same commit fc96fd9c resynced that digest and logged an "applicability_bound" audit entry for M5-T168 ("no requirement text edited"); validate_directive_compliance.py --check returned exit 0 (VALID).
 - B3 PASS: D-090 verification.json has exactly one M5-T168 row — applicable_requirement_ids [D-090-R639], producer backend-engineer, verifier "" (empty), per-requirement state "pending", reviewed_sha null.
 - B4 PASS: reg.evaluate_task_refs on the packet returns ok=True, applicable_ids ['D-090-R639'] == cited_ids ['D-090-R639'], missing_ids [], invalid_refs [], unresolved [].
 - B5 PASS: reg.derive_applicable on the packet returns only {'D-090-R639'} as applicable across all active directives, so nothing else applies uncited; separately, all required gates are PASS — G0 (reviewed_sha fc96fd9c), G2/G3/G4 (orchestrator/code-reviewer/qa-engineer) — and G2/G3/G4 share one content identity (content_manifest_sha256 8b5dae76ed4bf149cbee3023988813a2b653f8be66dbfabd0650c0fb29d0b567).

(4) CARRY-FORWARD CONDITION
 - Blob-level predicate: at the stamping head the three allowed-path files keep these blob ids — services/api/pyproject.toml 79e6e9378541ac994c6ce3c1212d5ead4eb1ef40, services/api/app/rules/coverage/render_coverage_matrix.py b47a4f2d30cee4ad2ecc19725cace60e6a4a5dca, project-control/reports/M5-T168-producer-report.md a7ec6f95339565ec761ecfaa46fd4fefd070dd97 — and .gitignore stays 7febd8627c853e0abfaa9c6836360af39d19888f (byte-unchanged from base); the R639 record text is unchanged and M5-T168 stays in R639.applicability.task_ids; the D-090 verification.json M5-T168 row is unchanged.
 - Broad disjoint-peer tolerance: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive bindings, ledger state), plus this task's own acceptance records, and a merge of the main line that changes none of the predicate's files; such commits do not invalidate this PASS, which may be stamped at a later head meeting the predicate.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - S2 by literal `git archive` extraction: the read-only guard blocks shell file-writes, so I could not materialize a .git-free copy; the fix is config-level (respect-gitignore=false makes .git presence irrelevant) and the renderer is clean in the linted set, and both reviewers ran the archive case, so this is adequately covered.
 - The live CI read at the eventual accept/merge head: that run does not exist yet (task awaiting_gate, not on main) and is the orchestrator's R639 obligation at acceptance/merge; I verified the gate-head and review-head runs only.
 - I did not run the full services/api pytest suite or tools/test_directive_compliance.py (forbidden by brief / CI's job); I relied on the green "api (ruff + pytest)" CI job at 6dde1345 and 5a8228c1, the committed-output sha, and validate_directive_compliance.py --check (exit 0).
 - D-093: I agree this change touches no property fact, rule applicability, calculation input, result or certainty label — the rendered output is byte-identical (sha256 42120957…) and the only code edits are an unused-variable removal and a behaviour-identical string wrap; research/verification is out of scope.

END-OF-REPORT
```
