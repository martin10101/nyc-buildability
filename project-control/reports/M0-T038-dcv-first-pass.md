# M0-T038 directive-compliance verification — FIRST PASS, verdict preserved verbatim

**Verifier:** directive-compliance-verifier (independent, read-only). **Recorded by:** orchestrator.
**Reviewed:** HEAD `361dee9` (pre-rework identity `16d327e1…`). **Overall: FAIL — D-010-R098 VIOLATED
(same defect as G3 D1: malformed 39-char merge SHA), D-010-R107 SATISFIED.**
**Disposition:** rework applied at `030e7a6` (SHA corrected programmatically from `git rev-parse`;
N2 packet widening); resubmitted at identity `090ad420…`; delta re-verification requested from the
same verifier at the reworked head. This first-pass record is preserved unedited below.

---

# Directive-Compliance Verification — Task M0-T038 vs D-010

**Verifier:** directive-compliance-verifier (read-only). **Producer:** orchestrator. **Producer ≠ verifier: confirmed.**
**Worktree:** `C:\Users\MLFLL\Downloads\nyc-zoning\orch` · branch `task/M0-T038-handoff-preserve` · HEAD `361dee98f490a11bff23882e9d1a05c8ca465a72` · base `origin/main` `aa5eec3f20d4c7c2fc6265e0e1cb797745fa3b97`.

## Preliminary confirmations (all PASS)

- **Applicable set = exactly {D-010-R098, D-010-R107}.** `directive_registry.load_registry().evaluate_task_refs(M0-T038.json)` → `{'ok': True, 'applicable_ids': ['D-010-R098','D-010-R107'], 'cited_ids': [...same], 'missing_ids': [], 'invalid_refs': []}`. Matches `project-control/reports/M0-T038.json` `applicable_requirements`.
- **Content identity current for reviewed content.** `git diff 25ed364..HEAD -- docs/SESSION_HANDOFF.md project-control/reports/M0-T038-producer-report.md` → **empty**. Deliverable and producer report are unchanged since reviewed_sha `25ed364`. (HEAD `361dee9` is the identity-stamp/submit commit, which touched only ledger/report JSON, not the deliverable.)
- **Evidence map covers both IDs with truthy evidence.** `project-control/reports/M0-T038-evidence-map.json` has non-empty `evidence` arrays for both `D-010-R098` and `D-010-R107`.
- **Producer ≠ verifier:** producer_agent = `orchestrator`; I am the independent `directive-compliance-verifier`.

## D-010-R098 — VERDICT: **FAIL (VIOLATED)**

Sub-obligations that PASS (reproduced): exact diff / no unrelated mixing (only the CURRENT STATE block, 11+/5−; forbidden paths untouched); not discarded (committed at `796cd00`); byte-fidelity to the uncommitted source (byte-equal after CRLF/LF normalization vs the primary checkout); dedicated bounded task + normal PR (task M0-T038, branch `task/M0-T038-handoff-preserve`, awaiting_gate).

Factual claims verified against actual merged state — 5 of 6 PASS: PR #154 MERGED 2026-08-07T00:06:56Z (gh); merge-commit method (`git show -s --format=%p cec785f` → 2 parents `d5d9b50 57ccb44`); branch not deleted (`origin/task/M0-T036-supervisor-bridge` present); tree byte-identity (both `67e97dda1ea8067ed73a8e1000ca662a736fbe93`); 16/16 check-runs success on `57ccb44`; SHADOW-ONLY + R595 MANDATORY BLOCKING match the activation checklist.

**The defect (VIOLATION):** deliverable line 16 recorded the merge SHA as a **39-hex-char token** (the digit `7` after `cec785f9` dropped): `git rev-parse` on it → `fatal: Not a valid object name`; the actual PR #154 merge commit is the 40-char `cec785f97ac1037df1fb2e1b114260eb106b7de0` (confirmed by BOTH `gh pr view 154` `mergeCommit.oid` and `git rev-parse cec785f`). The same malformed SHA exists in the uncommitted source, so the error originated upstream and was **preserved without being verified**. The producer report reproduced the claim only at the 8-char prefix, masking the malformed full SHA while asserting "every factual claim in the added lines reproduced against primary evidence."

**Why FAIL, not a note:** R098 makes "verify it against the actual merged repository state" an explicit obligation and conditions PR-preservation on "if it remains accurate." A full-form SHA that does not resolve is an inaccuracy and a provenance defect (CLAUDE.md principle 2). Remediation: one-character correction of line 16, re-verify against `gh pr view 154`, re-submit. All other R098 sub-obligations already satisfied.

## D-010-R107 — VERDICT: **PASS (SATISFIED)**

Evidence reproduced: capture PR #155 (`45dfdc2`), task-architecture PR #156 (`16aa47e`), applicability-binding PR #157 (`aa5eec3`) all ancestors of origin/main before task start; M0-T038 `dependencies: []`, lowest-numbered wave-1 task; single continuous autonomous flow `796cd00` → `25ed364` → `361dee9` (2026-08-06T21:51:54–21:52:13) with no owner-approval stop; no blocker references T038 (B-001..B-016 checked); no Section 20 hard-stop implicated (docs-only preservation).

## OVERALL VERDICT: **FAIL**

- D-010-R098 — VIOLATED (malformed 39-char merge SHA in deliverable line 16; producer attestation not reproducible for this claim).
- D-010-R107 — SATISFIED.

Failure is narrow and trivially correctable (one-character SHA fix + re-verify + re-submit); every other R098 sub-obligation and all of R107 are satisfied. Recommend rework of the single deliverable line rather than rescoping. No repository, git, or control-plane mutations were made by the verifier.
