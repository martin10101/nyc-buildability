# D-010 — source-013 (orchestrator correction amendment 13): narrow R121 task binding (drop M2-T014)

Recorded per `.claude/skills/directive-compliance` §1 note on corrections (append-only; a committed
source is never edited). Channel: orchestrator_correction (mechanical binding fix, 2026-08-07). This
amendment alters NO owner text and NO obligation: the session-5 re-dispatch instruction captured
verbatim in `source-011-amendment.md` remains fully binding.

## What changes and why

`D-010-R121` (the session-5 re-dispatch row, recorded in am.11) listed `M2-T014` in its
`applicability.task_ids`. That binding is retroactive: M2-T014 was claimed, submitted, and gated
(G0/G2/G3, content identity `73b36e60…`, stable) BEFORE am.11 existed, and `directive_refs` can only
be restamped by the CLI at (re)claim — a lifecycle regression that would invalidate its recorded
gates. Binding a re-dispatch ordering row onto an already-gated task adds no enforcement value and
mechanically deadlocks its acceptance (`evaluate_task_refs` fail-closed at accept).

`R121.applicability.task_ids` is therefore narrowed from
`["M0-T037","M0-T019","M2-T014","M2-T015","M2-T016"]` to
`["M0-T037","M0-T019","M2-T015","M2-T016"]`. The R121 re-dispatch compliance for the batch is
verified at M0-T019 (whose refs were restamped via the sanctioned reclaim cycle) and at the parent
M0-T037; M2-T015/M2-T016 keep the binding and enter the regime with covering refs at their fresh
claims. Precedent: the identical pre-merge narrowing of R122 (manifest audit-log entry,
2026-08-07T19:50Z) and the established amendment restamp mechanics.

## Redaction

No secrets/keys/credentials present. Verified by scan before commit.
