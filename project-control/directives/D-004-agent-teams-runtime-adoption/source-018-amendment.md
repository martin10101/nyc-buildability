# D-004 — source-018 (owner amendment 17, verbatim) — round-3 gating riders and the ONE-SHOT CLOSEOUT AND HANDOFF AUTHORIZATION

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.

Head at capture time: `control/M0-T034-closeout-authorization-capture` branched from
`origin/main` = `dc842e87f6f03871dff877331da52feab472a460` (the merge commit of PR #136).

Requirement IDs added by this amendment start at `D-004-R650`; no existing source file or
requirement row is edited.

## Delivery provenance (unusual channel, stated exactly)

The owner sent this message mid-turn while the round-3 producer agent (M0-T034 rework,
worktree `agent-aae76d66a169973ea`) was running, and the harness delivered it into THAT
agent's session rather than the orchestrator's, wrapped in the standard mid-turn banner
("The user sent a new message while you were working:") and closed by the standard harness
note ("This is how Claude Code surfaces messages the user sends mid-turn ...").
The producer correctly refused every act in it as orchestrator-only authority (ADR-005;
principle 7), took no action on it, and returned it to the orchestrator. The orchestrator
recovered the text below verbatim from the producer session's stored transcript record of
that delivery. The two harness wrapper passages are quoted above as provenance and are not
part of the owner's text; everything between them is captured below byte-for-byte, including
the run-together boundary "...whoever owns that path.ONE-SHOT CLOSEOUT AND HANDOFF
AUTHORIZATION ..." exactly as it arrived (a delivery artifact at what is plainly a
paragraph boundary; recorded as received, not repaired).

## Commencement clause (STEP 0 of the message)

STEP 0 of the captured text directs: capture this message verbatim as an owner amendment
before (or in the same commit as) the first act it authorizes, commencement-clause style,
and "No act below may precede its authorization being repository-reproducible."
Accordingly, per the same self-referential construction ruled genuinely terminating at
amendment 16, **this capture authorizes its own commit and the merge of its pull request
once CI is green**. Steps 1–7 of the captured text remain CONDITIONAL: they execute only
if both gate verdicts of the current round (G3, G5, frozen SHA
`dbf0a887aabebb55958d9e96e8584c41e443258a`) are PASS; otherwise none of them fires and the
normal rework loop applies.

## Scope

Per the owner's standing instruction, every row of this amendment carries
`task_ids: ["D-004-OPTIONB"]` — the session sentinel. Execution authority, not M0-T027
task-content. Verified after the write: M0-T027's resolver-derived applicable set is
unchanged and no row of this amendment enters it.

## External-fact anchors, verified at capture time

- The gating authorization's port/commit/dispatch acts (first paragraph) were already
  executed before this message reached the orchestrator, under the previously captured
  rework-sequencing ruling: port verified against the producer's five declared SHA-256
  hashes, committed as `dbf0a88`, fresh G3/G5 dispatched at that frozen SHA. The six gate
  riders were forwarded verbatim to both running reviewers on receipt.
- Step 5's pending draft: `OWNER_DIRECTIVE_DRAFT_dispatch-efficiency-and-graph-wiring.md`
  (repository root, untracked transient owner input) hashes to
  `bd6c4ec2151202bb5209ee62f4cc2a3f94538cd40b695604ceff0e32d1c22b6b` — MATCHES the digest
  in the captured text and in the tracked pending-capture record.
- Step 6's supervisor directive: the file exists in the tree as
  `.claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4.3 (1).md` (note the literal " (1)"
  in the basename; the captured text names it without that suffix). Its bytes hash to
  `426da3bb22714a403553b013e8969c6bfa424ee01d99e10d1269d0b65e0f5137` — MATCHES the SHA in
  the captured text. The content digest, not the basename, is the anchor.
- The producer's factual correction, recorded so the owner's contrary sentence does not
  harden into fact: the owner's text states the reverted agent-memory learning "is
  preserved in the report". The producer corrected this on return: the sandbox/worktree-
  guard observation exists only in its return transcript (preserved by the orchestrator),
  NOT in §11 of the producer report. The post-task carry the owner directs therefore
  sources from that preserved return, not from the report.

## Redaction

No redaction was required: the captured text contains no session identifier, machine
username, absolute user path, or hostname. Verified by scan before commit. (The worktree
token `agent-aae76d66` is a repository-pervasive agent id, not a machine identifier.)

---

## THE OWNER MESSAGE (verbatim, complete)

Round 3 accepted for gating. Port from worktree agent-aae76d66 to the task branch with
per-file SHA-256 verification against the five declared hashes — orchestrator
integration only, no edits. Commit, freeze, record the SHA, then dispatch fresh G3 and
G5 at that frozen SHA — a FAIL-then-fix inherits nothing; full fresh verdicts.

Gate riders for this round:
1. D1 verification — confirm the AS-2 suite now probes OUTSIDE the old denylist
   (UNVERIFIABLE, absent, null, empty-list, case variants) and that state: [] no longer
   raises. The prior suite certified the hole; prove this one doesn't.
2. Condition (6) — verify exact-identity binding at BOTH call sites, and that the
   carried-forward-attestation tests prove a stale stamp refuses and a re-stamp at the
   new identity restores deferral for that reason alone.
3. Confirm the round-2 fixes (F2 discharge parity, F3 empty-producer) survived round 3
   unchanged at this SHA.
4. Rule EXPLICITLY on F4 and F8, which round 3 left open by orchestrator decision:
   either they block, or the gates accept a named follow-up bundle — silence is not a
   disposition.
5. Rule on the producer's disclosed items 1, 2, and 4 (exact vs case-insensitive
   comparison; binding the dormant v1 path; amending more of §9.9 than asked) —
   acceptable or rework, on the record.
6. Verify the D3 redaction: zero literal matches on added lines and in tracked tools/,
   removed-side occurrences being the redacted lines themselves.

Also record on the owner backlog (no action now): the D-001 capture-guidance update
so future deferral records carry classified_at_identity (producer's item 7 — a path
it correctly couldn't touch), alongside the C1 MATERIAL_FIELDS task and the OBS-6
preservation-time redaction fix. The reverted agent-memory draft needs no path
allowance — the learning is preserved in the report and can be added post-task by
whoever owns that path.ONE-SHOT CLOSEOUT AND HANDOFF AUTHORIZATION — execute only if both round-4 gate
verdicts (G3, G5) are PASS at the frozen SHA. If either is not PASS, none of this
fires; normal rework loop instead.

STEP 0 — CAPTURE FIRST. Capture this message verbatim as an owner amendment before
(or in the same commit as) the first act it authorizes, commencement-clause style,
with rows recording exactly which prohibitions each step lifts and for which acts.
No act below may precede its authorization being repository-reproducible.

STEP 1 — MERGE M0-T034. Record the PASS gates through the CLI, submit via the
protected-main PR workflow, verify CI at the exact head, merge. Preserve both gate
returns as tracked files. At this merge boundary, perform the standing
session-handoff refresh and continue in a fresh session — the tail is long and the
current session is heavy.

STEP 2 — RE-SUBMIT M0-T027 under the corrected identity 29a094eb..., with all
evidence committed before submit per the new rule.

STEP 3 — FINAL VERIFICATION at that head, delta-scoped, citing settled rulings at
their verified SHAs; preserve the return as a tracked file; the verifier manually
performs any guard the code path skips and records it. HARD STOPS — halt and report
instead of proceeding if ANY of: R322, R323, or R388 cannot reach PASS through the
completed lifecycle evidence; any new finding, defect, or observation requiring
owner judgment; any UNVERIFIABLE remains; any deviation from expected state.

STEP 4 — CONDITIONAL ACCEPT. If and only if the verdict is exactly clean — every
applicable row PASS or attested lifecycle deferral, zero UNVERIFIABLE, zero new
findings, R024 recorded PASS by the verifier, not by you — then acceptance of
M0-T027 is AUTHORIZED and executed through the CLI (R486). Checkpoint only if
policy requires (R487). Clean only closeout branches and worktrees (R488). Run the
first post-accept verification of the deferred lifecycle rows through the M0-T034
mechanism. ANY deviation from "exactly clean" → stop before accept and return the
verdict to me.

STEP 5 — EFFICIENCY DIRECTIVE. On acceptance, the pending draft (v1.2, digest
bd6c4ec2151202bb...) is ISSUED. Capture verbatim; decompose per the intake standard
without weakening, combining, or omitting; commit the pending-capture record's
final disposition in the same batch. R307 disposition, mechanically: if this
round's gate-class spawns ran pinned Fable 5 successfully, record DISCHARGED
effective the capture date; if they ran under the Opus 5 regime, record DEFERRED
with that evidence and a re-check at the next gate dispatch — do not block capture
on it. Contract the Section 3/5.2 edit task and dispatch it through its normal
gates; adopt the dispatch and packet standards immediately; begin the N=6
measurement with the dcv2–dcv4 passes as baseline. A capture conflict or edit-task
gate FAIL stops that lane and reports; it does not stop Step 6.

STEP 6 — PHASE 0 PROPER for .claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4.3.md
(SHA 426da3bb22714a40...), per its Section 17: strictly read-only first — ingest
both recon rounds and the delta review as settled input evidence; run the
outstanding behavioral verifications (--ephemeral leaves no transcript; -m
acceptance for gpt-5.6-sol and gpt-5.6-terra; --max-turns; the stream-json
canUseTool protocol; one canonical Claude executable for the 13.4 baseline); check
every active directive for conflicts; record the ADR-005 reconciliation
(supervisor-as-integrator, worker never pushes), proposing an ADR amendment if
required; produce the SDK-vs-CLI written decision; propose the external
audit-anchoring decision; define the 4.3 dependency-independence check. Then the
two permitted writes only: canonical directive capture, and the controlled task
packet with exact paths, gates, reviewers, risks, stop conditions, and proposed
standing grants. No implementation, no supervisor paths, no config changes.

STEP 7 — CONSOLIDATED STOP. One final report: acceptance record and checkpoint;
post-accept lifecycle-row results; efficiency capture decomposition, R307
disposition, and edit-task gate results; the Phase 0 Section 19 return packet and
the supervisor task packet awaiting my dispatch decision. Add to the owner backlog
without acting: the C1 MATERIAL_FIELDS inversion task, the OBS-6 preservation-time
redaction fix, and the D-001 capture-guidance update for classified_at_identity.

GLOBAL RULES — every stop is a report, never a workaround; nothing beyond the acts
named here; auto mode never overrides an Ask rule; if anything is ambiguous, stop
is the default.
