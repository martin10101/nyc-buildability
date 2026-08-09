# Lean Operating Process (product-efficiency policy)

Authority: owner product-efficiency directive **D-010 source-029 (R320–R343)**. Tracked by **M0-T055**
(Phase 1). **Guiding rule: cut duplicated explanation + manual bookkeeping — NOT verification,
testing, provenance, or safety.** Line-count reduction is never itself an acceptance criterion.

**Effective PROSPECTIVELY:** these rules govern **M2-T016 onward** (the first product task under the
lean process). In-flight M0-T054/M2-T015 finish under the existing process; nothing here is applied
retroactively, and no existing evidence is deleted, rewritten, or invalidated. This is policy-only —
no product-module or supervisor-core code changes (Phase 1).

---

## Return item 1 — Map of duplicated control-plane facts (A1)

Where each routine fact is currently written **manually in more than one place** today:

| Routine fact | Canonical (machine) | Also hand-written in (duplication to cut) |
|---|---|---|
| task status | `tasks/<id>.json.status` + `progress_log[].status` | handoff, PR description |
| progress % | `tasks/<id>.json.progress_percent` + `progress_log[].percent` | handoff, PR |
| latest safe commit | git (task branch HEAD) + commit trailer | `progress_log` message, handoff, PR body |
| completed unit | `progress_log[].message` | commit message, handoff, PR, producer report |
| test result | CI + commit message | `progress_log` message, PR, producer report |
| review/gate verdict | `gates/` records | `progress_log`, PR, producer report |
| current blocker | `tasks/<id>.json.risks` / `blockers/` | `progress_log`, handoff |
| next action | `progress_log[].message` | handoff, PR |

The same unit fact is frequently narrated 3–4 times (progress message → commit message → handoff → PR).

## Return item 2 — Selected canonical routine execution record

**The per-task append-only `progress_log` in `project-control/tasks/<id>.json`** (written only by
`tools/project_control.py progress`), together with **git** (branch/SHA/trailer) and **CI** (test/gate
results). This is an EXISTING machine-readable event log — no new database, service, or parallel
source of truth. Everything else (handoff, PR body, producer report) is a **projection** of
progress_log + git + CI and adds only engineering judgment.

## Return item 3 — Lean handoff format

A routine handoff is **current-only, ≤ ~2,000 tokens**, exactly these 7 fields, everything else linked:
1. active task + current status; 2. active branch + latest safe SHA; 3. completed units; 4. current
unfinished unit; 5. current blockers / owner decisions; 6. exact next action; 7. links to authoritative
evidence (git, `progress_log`, `gates/`, reports). **Never paste old session histories** — they are
git-recoverable (`git log -p docs/SESSION_HANDOFF.md`).

## Return item 4 — Exact future handoff triggers

Create/refresh a handoff ONLY at a real seam: (a) main-orchestrator or worker **context rotation**;
(b) **model turnover**; (c) a **stop requiring an owner decision**; (d) a **material failure/recovery
incident**; (e) **task submission or acceptance**; (f) a demonstrated event where a successor cannot
safely continue from the canonical records. **Not** after every normal unit or supervisor cycle.

## Return item 5 — Routine control-PR batching rule

Per ordinary product task: product work = intentional commits on the **task branch**; routine
machine-readable evidence accumulates in `progress_log`; **routine control-plane updates batch into
1–2 meaningful seam PRs** (typically one at a mid-task seam + one at acceptance). **Immediate standalone
control PRs remain required** for: new owner decisions needing pre-action durability; security
incidents; protected-config changes; material recovery; legal/policy decisions; any rule requiring
pre-action durability. **Never** combine unrelated product code + privileged controller changes to
cut PR count.

## Return item 6 — Concise-code + parameterized-test guidance adopted

- **Docs, not code, hold doctrine** (B2): module docs state purpose + authority boundary + unusual
  security assumptions; function docs state inputs/outputs/non-obvious invariants; comments explain
  **why** a surprising decision exists — never restate visible code or reproduce project philosophy;
  reference the canonical architecture doc. **Keep** comments that preserve a security rationale or a
  demonstrated past defect.
- **Shared typed results** (B3) only where repetition is real and semantics identical — no framework/DSL.
- **Table-driven survey rules** (B4): one closed/typed/deterministic/tested rule table; unknowns fail closed.
- **Short typed errors** (B5): stable code + concise message + structured metadata (submitted value,
  expected rule, failed condition); no essays in error strings.
- **Parameterized adversarial tests** (B6): fixture tables (case name, input, expected result, expected
  typed error, invariant proved). **Preserve every** malicious/malformed/ambiguous/tampered/unresolved
  case; never merge tests when that hides which invariant failed.
- **Generated contract types** (B7): deterministic, drift-checked, CI-covered; no parallel hand-written types.
- **Cohesive modules** (B8): small public interfaces; don't split for line limits; don't mix
  parsing/validation/persistence/authority; functions + data tables over wrapper layers; add abstraction
  only to remove real repetition or protect a material invariant.
- **Safer packets** (A7): at packet creation include naturally-necessary files (generated artifact +
  its source generator + focused tests + directly-required wiring) in exact, bounded `allowed_paths` —
  no broad wildcards, no weakened scope enforcement. (Directly fixes the M2-T015 3j-1 scope churn.)
- **Control-plane effort ≤ ~15–20%** (A6): a target; if exceeded without incident/decision/protected
  change/failed gate, report the duplication and return to the product.
- **Minimal unit event** (A2): one `progress` entry per completed unit carrying task id, unit/checkpoint
  id, branch, exact SHA, tests+result, reviewer verdict, blocker, next authorized action, evidence
  links/digests — not re-narrated into several files.

## Return item 8 — Proof no safety/evidence/gate/provenance requirement was removed

This policy **removes nothing** and is enforced by construction:
- **Provenance intact:** the canonical record is the existing append-only `progress_log` + git + CI +
  `gates/` — all retained; no new source of truth; no historical evidence deleted/rewritten (R321/R341).
- **Gates intact:** every G0–G7, DCV, independent-reviewer, and acceptance-precondition path is
  unchanged; ADR-005/006 authority unchanged. Batching PRs changes *how many* routine control PRs, not
  *what* evidence a gate consumes.
- **Safety/testing intact (B1/B6):** deterministic calc, typed failures, fail-closed, immutable
  provenance, per-fact lineage, correction-history, promotion gates, qualified-human approval,
  adversarial handling, tax-lot-cross-check-only, B-001 honesty, five-borough scope, and every
  adversarial test case are preserved; parameterization keeps coverage while cutting boilerplate.
- **Prohibitions (R341):** no protected-config/ACL change, no LIMITED-AUTO, no activation change, no
  history rewrite, no evidence deletion, no repo-wide cleanup, no multi-week refactor under this policy;
  deleted lines are never counted as product progress; security-sensitive code is not replaced without
  comparative evidence.
- **Independent review (Part D / R340):** efficiency changes get an independent Codex review; the
  verdict is **REVISE** if efficiency is achieved by deleting evidence, merging materially-different
  safety cases, or weakening gates.

## Phases (return items 7, 9, 10 — status)

- **Phase 1 (this doc) — DONE:** policy established; files changed = `docs/LEAN_OPERATING_PROCESS.md`
  (new) + a CLAUDE.md routing pointer + the D-010 source-029 registry capture + M0-T055 tracking.
  No product/supervisor-core code changed.
- **Phase 2 (return item 9) — pending M2-T016:** run M2-T016 under these rules; measure + return
  product units/commits, handoff rewrites, routine control PRs, control-vs-product effort, duplicated
  records eliminated, evidence-recoverability, gate/reviewer context. If recoverability deteriorates →
  STOP and correct; never weaken evidence for a target.
- **Phase 3 (return item 10) — conditional:** only if M2-T016 still shows material duplicated
  bookkeeping, ONE small bounded projector helper (no new DB/service, deterministic, idempotent,
  drift-tested, no evidence deletion, no silent overwrite, independent review, CI). Otherwise no helper.
- **PDF parser keep-vs-replace (B9) — post-M2-T015-acceptance, comparison-only.**
