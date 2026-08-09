# Owner Product-Efficiency Directive — parking + managed execution plan

**Status: PARKED / PROSPECTIVE.** Captured 2026-08-09 while M0-T054 (turnover) + M2-T015 are in
flight. Per the owner: do NOT interrupt current work; apply the lean rules **prospectively after
M2-T015 acceptance**; use **M2-T016 as the first product task under the leaner process**; do NOT
begin a repo-wide refactor or a multi-day supervisor project. This file is the single place I
revisit; the formal directive-registry capture (verbatim source + requirements) folds into the
**next already-required control-plane seam PR** (not a standalone PR).

**Applies to ALL future work in this program**, not just this session (owner, 2026-08-09).

**Guiding rule:** CUT DUPLICATED EXPLANATION AND MANUAL BOOKKEEPING — NOT VERIFICATION, TESTING,
PROVENANCE OR SAFETY. Line-count reduction is never itself an acceptance criterion.

---

## Managed execution order (what I do, when)

**GATE: nothing here starts until M2-T015 is ACCEPTED.** Sequence:

1. **At the next control seam (soon):** formally capture this directive in the registry (verbatim
   source + atomic requirements + manifest), bundled into the next required M0-T054/M2-T015
   control PR. New directive id likely **D-011** (standing operating-policy) — decide at capture.
2. **Phase 1 (policy-only, after M2-T015 acceptance):** smallest prospective operating-policy
   changes — one canonical routine execution record; minimal unit events; seam-only handoffs;
   batched control PRs; generated objective reporting; concise-code + parameterized-test
   expectations. No supervisor-core edits; no product-module rewrites.
3. **Phase 2 (prove on M2-T016):** run M2-T016 under the lean rules; measure before/after (units,
   handoff rewrites, routine control PRs, control-vs-product effort, duplicated records eliminated,
   evidence recoverability). If evidence quality/recoverability deteriorates → STOP and correct the
   policy; never weaken evidence to hit a target.
4. **Phase 3 (automate only a demonstrated bottleneck):** only if M2-T016 still shows material
   duplicated manual bookkeeping — ONE small bounded projector helper (no new DB/service, no
   supervisor redesign, deterministic, idempotent, drift-tested, no evidence deletion, no silent
   overwrite of owner judgment, independent Codex review, normal CI). Broader automation = separate
   owner decision.
5. **Post-M2-T015 only, bounded:** the PDF parser keep-vs-replace ASSESSMENT (Part B.9) — comparison
   only, no rewrite under this directive; a replacement would be a separate scoped task with
   migration + regression evidence.

## Part A — control-plane / handoff efficiency (checklist)

- A1 One canonical routine execution record: map overlap across task JSON / state JSON / journal /
  SESSION_HANDOFF / producer report / directive verification / PR description / gate evidence; pick
  the **smallest existing machine-readable record** (prefer the existing journal/event log) as the
  canonical source for ordinary unit progress; project other views from it. No new DB. No deletion
  of historical evidence. Prospective.
- A2 Minimal unit-completion event (only: task id, unit/checkpoint id, branch, exact SHA, tests+result,
  reviewer verdict, blocker, next authorized action, evidence links/digests). Don't re-narrate it
  into several files per unit.
- A3 Handoffs only at REAL seams (rotation, model turnover, owner-decision stop, failure/recovery,
  submission/acceptance, or a successor can't safely continue from canonical records). Routine
  handoff ≤ ~2,000 tokens, 7 fields only; link to Git/journal for history; stop pasting old session
  histories. (Already trending this way — session-10 handoff was trimmed to ~1,957 tok.)
- A4 Fewer control-only PRs: batch routine control updates into one seam PR (≤1–2 routine control PRs
  per ordinary product task); immediate standalone PRs stay ONLY for owner decisions / security /
  protected-config / recovery / legal-policy / rules requiring pre-action durability. Never combine
  unrelated product code + privileged controller changes to cut PR count.
- A5 Producer reports / PR descriptions: generate objective sections (commits, changed files,
  test cmds/results, gate verdicts, requirement coverage, evidence paths) from evidence; reserve
  hand-authored prose for engineering judgment (architecture, risk, compatibility, limits, holds,
  legal boundaries). Don't restate machine-verifiable facts in multiple places.
- A6 Control-plane time budget ≈ 15–20% of effort (target, not a license to skip evidence). If
  exceeded without incident/decision/protected-change/failed-gate, report the duplication and return
  to product. Don't build a feature just to compute this %.
- A7 Safer packets, fewer false blocks: at packet creation, inspect dependency/generator impact so
  naturally-necessary files (generated artifacts + their source generator + focused tests + directly
  required wiring) are in the bounded allowed_paths from the start. Keep paths exact; no broad
  wildcards to dodge scope decisions. (Directly addresses the M2-T015 3j-1 allowed_paths churn.)

## Part B — concise, maintainable code (checklist)

- B1 PRESERVE behavior + safety: never simplify away deterministic calc, typed failures, fail-closed,
  immutable provenance, per-fact lineage, correction-history integrity, promotion gates,
  qualified-human approval, adversarial handling, tax-lot-cross-check-only, B-001 honesty, 5-borough
  scope, tests/gates.
- B2 Centralize doctrine in architecture/security docs; in code keep module/function docs concise
  (purpose, authority boundary, unusual security assumptions, non-obvious invariants); comments
  explain WHY, not restating code; **keep comments preserving security rationale or a demonstrated
  past defect** (e.g. model_turnover.py's chr(0x2019) note).
- B3 Shared typed validation results: prefer a minimal common set of typed result/refusal patterns
  over bespoke near-identical dataclasses — only where repetition is real and semantics identical.
  No framework/DSL.
- B4 Table-driven survey rules: one canonical closed/typed/deterministic/tested rule table (fact type,
  normalized shape, units, required validations, geometry/location req, professional-confirmation req,
  material/non-material); validators consume it; unknowns still fail closed.
- B5 Short typed errors: stable code + concise message + structured metadata (submitted value,
  expected rule, failed condition). No architecture essays in error strings; keep debugging detail.
- B6 Parameterized adversarial tests: fixture tables (case name, input, expected result, expected
  typed error, invariant proved). Preserve EVERY malicious/malformed/ambiguous/tampered/unresolved
  case; don't merge tests if it hides which invariant failed.
- B7 Generated contract types: keep deterministic, drift-checked, CI-covered generation (as
  survey_evidence.ts does); no parallel hand-written types.
- B8 Cohesive modules, small public interfaces; don't split files for line limits; don't mix
  parsing/validation/persistence/authority; prefer functions + data tables over wrapper layers;
  add abstraction only to remove real repetition or protect a material invariant.
- B9 (post-acceptance, bounded) PDF parser keep-vs-replace ASSESSMENT only — see order item 5.

## Part D — review requirement

Codex independently reviews efficiency changes; verdict is **REVISE** if efficiency comes from
deleting required evidence, combining materially-different safety cases, or weakening gates. Checks:
evidence loss, weakened fail-closed, directive-compliance incompatibility, unclear source-of-truth
ownership, excessive new abstraction, tests removed/less diagnostic, product delayed by process opt.

## Part E — prohibitions

Do NOT: interrupt the current M0-T054/M2-T015 sequence; reopen accepted supervisor defects without
new qualifying evidence; alter protected config/ACLs under this directive; authorize LIMITED-AUTO;
change supervised-auto activation; weaken command/path/credential protections; rewrite Git history;
delete existing evidence; do a repo-wide style cleanup; start a multi-week refactor; count deleted
lines as product progress; delay the architect/browser MVP for cosmetic neatness; replace functioning
security-sensitive code without comparative evidence.

## Return (at the appropriate post-M2-T015 seam)

1. map of duplicated control-plane facts; 2. selected canonical routine record; 3. lean handoff
format; 4. exact future handoff triggers; 5. routine control-PR batching rule; 6. concise-code +
parameterized-test guidance adopted; 7. exact files changed for Phase 1; 8. proof no safety/evidence/
gate/provenance requirement was removed; 9. M2-T016 before/after efficiency measurements; 10. any
narrowly-justified follow-up helper task.

---

_Success criterion (owner): more reliable product delivery with less duplicated work. The supervisor
exists to accelerate the product._
