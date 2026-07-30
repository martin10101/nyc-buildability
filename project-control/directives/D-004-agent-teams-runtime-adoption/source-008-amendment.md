# D-004 — source-008 (owner amendment 7, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message (chat prompt) plus three
owner answers returned through the AskUserQuestion decision component in the same session.
Amends `source-001.md`. Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.
Head at capture time: `origin/main` = local `main` = `3a052d2a8a30a48b090f8affc2c0174e85cdbd72`
(post PR #124, the M0-T028 Phase-8 acceptance merge), reconciled live before any write.

This is the owner's explicit GO for **D-004 Step 4 only** (D-004-R064), given in the same
session that completed Phase 8, immediately after the Phase-8 return packet and a plain-English
status summary. The owner's GO message quotes back the orchestrator's own summary line
describing Step 4; that quoted line is part of the verbatim capture below. The trailing
token-count question is a read-only status question (answered in-session; no requirement).

Requirement IDs added by this amendment start at `D-004-R297`; no existing source file or
requirement row is edited. The worker-model answer supersedes the VALUE clause of
D-004-R091/D-004-R162 (producer teammates: Opus 4.8 → Opus 5 ceiling) by the same append-only
value-clause supersession mechanism used in amendment 1 for D-004-R081; the prohibition and
explicit-model clauses of those rows are unchanged. Rows binding only this session's conduct
are scoped to the non-ledger sentinel `D-004-STEP4`; rows binding the two pilot tasks carry
their ledger ids (`M2-T018`, `M4-T008`) so the resolver derives them at claim/submit/accept.

---

## Owner message 1 (chat prompt, 2026-07-30)

lets do this 
D-004 Step 4 — the next stage of letting AI worker agents do more (now unblocked since the safety fix passed, but still needs your explicit GO). This connects to your cost concern: the plan is cheap models for workers, Fable 5 only for me and reviewers

btw where is the token count for this season so far

## Owner decision answers (AskUserQuestion, same session, 2026-07-30)

Question 1 — producer model for the two Step-4 worker teammates (Opus 4.8 pin not per-spawn
selectable; recorded STOP-and-ask condition):

> the main has to stay fable 5 the workers can be opus 5 max 

Question 2 — D-004-R065 fresh-session requirement (purpose already satisfied in this session:
post-merge session, all four hooks proven firing live in the C1 proof; no hook/settings change
merged since session start):

> Proceed here (Recommended)

Question 3 — which two disjoint, contract-fresh tasks the producers pilot on (lane 1 M3-T002
excluded by the owner's D-003 rule while B-001 is open):

> Lanes 2+3 (Recommended)

(Question-3 option text as presented and accepted: contract M2-T018 — wire the accepted
M2-T017 allowlist serializer into the property-profile builder with fail-closed tests; and
M4-T008 — DF-6 rule-engine hardening: missing optional inputs in exception predicates produce
indeterminate/professional-review behavior, never silently evaluate as false.)
