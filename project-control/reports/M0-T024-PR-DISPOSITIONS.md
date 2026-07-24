# M0-T024 — Stale/open PR reconciliation dispositions (D-002 §4)

Base: post-#97 `origin/main` = `2d44b47`. Consolidation branch: `control/D-002-consolidation-2026-07-24`.
For every open PR, each unique material change is classified **carried forward** / **superseded (reason)** /
**unresolved**. Closure of a PR is authorized (D-002 §4) only after the consolidation PR merges AND all its
unique changes are accounted for; **a PR with unresolved unique changes is NOT closed.**

Status vocabulary distinguishes: proposed / on-a-branch / CI-verified / accepted / merged-into-main.

---

## PR #97 — Owner Directive Compliance System (D-001) [not in the reconcile set; context]
- **ACCEPTED + MERGED** into main (merge commit `2d44b47`) under D-002 §1 after identity match
  (head 9bc1f13, reviewed ed8a6776, manifest 9ab6c960, evidence/control-only post-review, CI + directive
  verification green). Accepted count 42 -> 43.

## PR #93 — five-packet M3 legal-corpus replan  → **CARRIED FORWARD** (branch content restated on-branch)
| Unique change | Disposition |
|---|---|
| M3-T001..T005 five-task chain packets | **Carried** — restated as in-regime packets citing D-002 (M3-T001 contracted first-wave lane 1; M3-T002..T005 backlog, sequential). Proposal-era "NOT CONTRACTED" framing **superseded**. |
| Document Evidence Verification Engine (M3-T003) | **Carried** — preserved in M3-T003 packet. |
| Source-authority / coverage-matrix / construction-code / document-evidence / professional-review controls | **Carried** — in M3-T001..T005 packets + B-011. |
| B-011 construction-code release-scope blocker | **Carried** — ported (blocks M3-T005 acceptance while open). |
| B-001 amendment naming M3-T002/T003/T005 (durable-storage acceptance block) | **Carried** — ported; `accept()` blocker scan enforces it. |
| `M3-CORPUS-REPLAN-PROPOSAL.md`, `M3-CORPUS-B001-enforcement-evidence.md` | **Carried** — reports ported verbatim. |
| master_plan #93 M3/M4 summary text | **Superseded** — replaced by consolidated summaries (footprint no longer claims M4-T007; see #91). |
| S9 control-plane regression in `tools/test_project_control.py` | **Carried (behavior) + test deferred** — the B-001->M3 acceptance block is live via B-001 references + `accept()` scan; the CI regression *test* is out of M0-T024's project-control-only scope and is tracked as a controller tooling follow-up (not load-bearing for the block). |

## PR #95 — whole-system trust replan (A–J, defect matrix)  → **CARRIED FORWARD**
| Unique change | Disposition |
|---|---|
| `WHOLE-SYSTEM-TRUST-REPLAN-2026-07-23.md` (dataflow trace, DF-1..DF-11, areas A–J) | **Carried** — ported verbatim; architecture-of-record. |
| B-014 exact-Decimal-math publication blocker (DF-2) | **Carried** — ported; M4-T007 (first-wave lane 2) is its foundation. |
| Area D exact legal arithmetic | **Carried → contracted** as M4-T007. |
| Area G canonical-contract deficiencies (DF-4 source_fact, DF-5 analysis_state_transition OPEN) | **Carried → contracted** as M2-T017 (first-wave lane 3). |
| Areas A/B/C/E/F/H/I/J (registry+capture, run orchestrator, zoning-lot model, closure, review/publication, scenario/reports, auth/RLS+ops, golden corpus) | **Carried as architecture** — remain proposed; contracted later at fresh IDs after their accepted dependencies; auth/RLS (I-foundation, DF-1) intentionally NOT first-wave (blocked by B-001). |

## PR #94 — frontend-security reconciliation  → **CARRIED FORWARD**
| Unique change | Disposition |
|---|---|
| M0-T019.json reconciled (target Next 15.5.21; eligibility `2026-07-28T15:59:32.231Z`) | **Carried** — ported. |
| B-012 public-deployment hold (frontend security) | **Carried** — ported. |
| B-013 owner **DECLINES** age-only exception (wait full 7-complete-day threshold) | **Carried** — ported; the owner's decision not to use an age-only exception is preserved. |
| `M0-T019-frontend-security-reconciliation-2026-07-23.md` | **Carried** — ported verbatim. |

## PR #91 — M4 footprint 4-way split (T007–T010)  → **SUPERSEDED**
- **Reason:** footprint/yard-coverage rule work is downstream of accepted **M3-T004** cross-reference closure
  and the canonical zoning-lot model (Area C); it is NOT first-wave. The proposal's `M4-T007..T010` numbering
  was never contracted on the authoritative ledger; **M4-T007 is contracted here as the Decimal foundation**,
  so footprint will be **re-proposed at fresh IDs** after M3-T004 lands.
- Analysis reports (`source-inventory`, `sec.11-25-applicability-decision`, `input-readiness-matrix`,
  `control-metadata-reconciliation`): **superseded** as proposals, but remain valid research to re-cite when
  footprint is re-proposed. **No unresolved first-wave-blocking change.**

## PR #96 — handoff refresh (trust-replan)  → **SUPERSEDED** by the single consolidated `docs/SESSION_HANDOFF.md`.
## PR #92 — handoff refresh (footprint)  → **SUPERSEDED** by the single consolidated `docs/SESSION_HANDOFF.md`.

## PR #64 — M0-T019 frontend security upgrade + npm dependency-admission policy  → **UNRESOLVED (do NOT close)**
| Unique change | Disposition |
|---|---|
| Next.js framework security upgrade (product code) | **Unresolved** — owed by ledger task **M0-T019** (claimed, **HELD** until `2026-07-28T15:59:32.231Z`). |
| `docs/DEPENDENCY_SECURITY_POLICY.md`, `apps/web/scripts/dependency_age_gate.mjs`, `scheduled-npm-audit.yml`, related `ci.yml`/`CLAUDE.md` edits | **Unresolved** — NOT on main (verified 2026-07-24); owed by M0-T019. A `dependency-security` skill exists on main as the route, but the policy doc + npm age-gate implementation do not. |
| Branch state | stale/DIRTY (behind main). |
- **#64 has unresolved unique changes → it is NOT closed.** It is reconciled to M0-T019 (target + holds carried
  from #94); the implementation is executed by M0-T019 only on/after its eligibility timestamp.

---

## Closure plan (executed only AFTER the consolidation PR is merged)
- **Close with replacement pointer:** #93, #95, #94 (carried into this consolidation), #91, #92, #96 (superseded).
- **Do NOT close:** #64 (unresolved unique changes owed by held M0-T019).
