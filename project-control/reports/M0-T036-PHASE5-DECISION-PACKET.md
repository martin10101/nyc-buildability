# M0-T036 — Phase 5 Decision Packet (D-007 §17/§19; R506/R575)

- Assembled: 2026-08-04, orchestrator, after all five independent gate reviews returned.
- **This packet STOPS for the owner's activation decision (D-007-R541/R555/R576). It authorizes
  nothing. Limited-auto is never enabled by this task. No M0-T035 acceptance is performed.**

## 1. Frozen SHA + CI

- **Frozen content identity: `43848bd5158cb74184964f93d97ef109fad1ed19`** (task branch tip
  including the diagnostics-triage record; one control-plane commit past the owner-verified
  `387378f`).
- **CI at the frozen SHA: run 30886102559 — SUCCESS, all 13 jobs** including supervisor-bridge
  (independently reproduced by the directive-compliance verifier); secret-scan run 30886102487
  SUCCESS; context-budget run 30886102517 SUCCESS.
- Supporting per-SHA record (R565/R568): bc83092 CI success (30882641988); 307b7c6 cancelled by
  concurrency supersession, conclusive identical-content run f68f578 success (30885128881);
  PR #152 head f3a5183 success (30866188693, 31 checks green at merge).

## 2. The five independent reviews (all preserved verbatim; producers ≠ reviewers; first
independent gate review of the build, pinned Fable 5, read-only, frozen at 43848bd)

| Review | Verdict | File |
|---|---|---|
| G3 code | **PASS with 4 BLOCKING corrections (B-1..B-4)** | `M0-T036-G3-code-review.md` |
| G5 security | **PASS** — 0 blocking; L-1..L-4 (V1.1); L-2 packet consideration | `M0-T036-G5-security-review.md` |
| G4 QA/validation | **PASS** — totals reproduced; run-4 erratum applied; 7 ranked gaps | `M0-T036-G4-qa-validation-review.md` |
| Control-plane | **PASS** — C1/C2 corrections required and **discharged** (CLI re-record 9963cde; audit_log catch-up) | `M0-T036-CPV-control-plane-review.md` |
| Directive compliance | **PASS** — R532–R576: 36 satisfied / 9 pending-by-design / 0 violated / 0 unverifiable; R541/R555 boundary affirmatively held | `M0-T036-DCV-directive-compliance-verification.md` |

## 3. Replay results

8/8 historical corpus cases reproduce their recorded stop/continue behaviour (0 model calls,
0 writes; corpus digest 768eea1ec6bb9e83… provenance-verified) — reproduced independently by QA
at the frozen SHA.

## 4. Shadow comparison — runs 1–6, touch counts

| Run | Outcome | Would-be owner touches (budget ≤2) | Classification of the stop |
|---|---|---|---|
| 1 | S4.5 stop `missing_checkpoint` | 1/2 | TRUE positive (fail-closed worked; operator prompt lacked the S8.3 contract — F-4) |
| 2 | Refused pre-act (PAUSED_RECOVERY no-exit) | n/a (no cycle) | TRUE positive of completeness defect F-2 (no policy stop occurred) |
| 3 | S4.5 stop `invalid_checkpoint` (status vocabulary) | 1/2 | TRUE positive (strict validation correct; prompt bug — F-4) |
| 4 | S4.5 stop, unit `timed_out` (checkpoint was valid — see erratum) | 1/2 | TRUE positive of runner defect F-3 (fail-closed timeout rule correct) |
| 5 | Unit clean (F-3 fix live-proven); review failed 3/3 → `review_unavailable` | 1/2 (blocking_ask) | TRUE positive of adapter defects F-6/F-7 |
| 6 | **FULL CYCLE COMPLETE** — checkpoint validated + correlated; live Codex decision **COMPLETE** (gpt-5.6-sol, attempt 1, returncode 0, no self-report mismatch); stage evidenced complete with the 4 M0-T035 gate records as evidence_refs; ends AT the gate | **0/2** | — |

- **Zero policy false-positives across all runs**: every stop was a true defect signal or the
  designed fail-closed rule; none was a spurious policy hold.
- **Shadow discipline held in every run**: forwarded NOTHING; no ShadowPlan row exists for run 6
  because none was generated — the loop journals a ShadowPlan only when a forward WOULD occur,
  and the terminal COMPLETE decision routes to stage-complete (verified against loop.py by DCV).
- AS-6 satisfied live: one real controlled-task lifecycle (M0-T035 acceptance-readiness)
  completed in shadow, within budget, ending AT the acceptance gate ("It never merges, accepts,
  deploys, or closes an owner gate" — audit seq 12).

## 5. Residual risks

### Activation-blocking corrections (G3 B-rows; all in the assembled loop, none exercised by the
shadow single-cycle pilot)
- **B-1**: the approved forwarded prompt is never threaded into the next cycle — supervised
  multi-cycle is broken as built (zero-times forwarding behind an "exactly-once" record).
- **B-2**: POLICY_CHECK is a second no-exit parking state (every successful shadow cycle strands
  the journal; DENY_AND_CONTINUE becomes an uncaught in-run crash in supervised mode).
- **B-3**: multiple DISTINCT checkpoint ids in one unit are silently last-wins (refuse-rather-
  than-choose violated for an untrusted input).
- **B-4**: the codex_reviews_per_checkpoint breaker's trip verdict is discarded (a breaker that
  claims a safety function it does not perform).

### V1.1 conditions (owner-directed per R575)
- **F-2 (V1.1 condition)**: PAUSED_RECOVERY has no operator CLI exit (`owner_cleared_pause` is
  defined but nothing fires it); today's only path is parking the journal. B-2 adds a second
  stranding state to the same family.
- **F-4 (V1.1 condition)**: the S8.3 checkpoint contract must be hand-authored into every unit
  prompt; the supervisor should inject a canonical contract block (V-1 — the unwired approval
  broker — is the same family's forwarding-side gap).

### Recommendation (owner-directed per R575)
- **F-5**: doctor/preflight should verify timezone-database resolvability so a fresh machine
  fails at setup, not at its first wake (tzdata itself RESOLVED-BY-ADMISSION per D-007-R561:
  hidden runtime dependency masked by an out-of-lock local install; admitted hash-pinned,
  age-gated 498.45d, advisory-free, owner-authorized).

### Other recorded residuals
- **G5 L-2 (activation consideration)**: on a single-account Windows machine, OS ACLs cannot
  distinguish worker from controller — the policy engine is the isolation boundary; the
  compensations (ancestry denial, brokered writes, out-of-band change detection) are
  application-layer.
- **G5 L-1/L-3/L-4 (V1.1 hardening)**: `=`-form hard-deny at the argv layer; PATH filtering for
  children; redaction pattern additions (service-role names, high-entropy fallback).
- **QA gaps 1–7 (ranked)**: (1) the live broker ALLOW-path has never been observed — a bounded
  `doctor --live` allow+deny round-trip is required before any live supervised worker run;
  (2) **limited-auto has no executable form at this SHA** — activation requires new code plus its
  own gate; (3) live forwarding untested (shadow correctly forwarded nothing); (4) rotation/
  handoff never exercised live; (5) durable wake never drilled on real Task Scheduler;
  (6) Codex fallback engagement never live-observed; (7) symlink-escape variant not executed on
  this host (junction twin passed).
- **Platform**: the suite is not Linux-safe (its only ubuntu execution starved the runner to
  death); target platform is Windows and CI runs windows-latest by design.
- **G3 V-2..V-6 + minors**: journal timing of process-start, drain-thread edge, timeout/grace
  overlap reason strings, Job-Object adoption window, corrupt-anchor fail-open — V1.1 list.
- **Live-CLI wrapper**: the control-response wrapper bytes remain live-unverified on this
  controller checkout (`doctor --live` never run there — one bounded disclosed probe closes it).

## 6. Proposed AUTO allowlist + standing grants (PROPOSAL ONLY — inert until the owner's
separate activation decision, which additionally requires B-1..B-4 fixed and re-gated)

Proposed AUTO tier (no owner touch, full audit): read-only repository commands (`git status`,
`git rev-parse`, `git log`, `git diff` — no network forms); file reads inside the task packet's
allowed paths; `pytest tools/test_agent_supervisor_*.py` inside the task worktree (the proven
grant-(a) shape); worker file edits strictly inside its isolated task worktree.
Proposed NOTIFY tier: test-suite runs above 10 minutes; model fallback engagement.
Proposed ASK tier (queued, never blocking NOTIFY flow): any push (grant-(b)-shaped pushes only
after a recorded passing review); any new file outside allowed paths; any network access.
Proposed HARD-DENY (immovable): merges, accepts, gate records, master-plan changes, settings/
hook/workflow edits, secrets access, `--dangerously-*` flags, effort keys anywhere.
Proposed standing grants at activation: exactly the two proven M0-T036 grants, re-scoped to the
future task's packet, never widened, expiring with the task.

## 7. Emergency-stop behavior (as built and doctor-verified)

`python -m tools.agent_supervisor emergency-stop` — immediate child-process-tree termination
(Job-Object kill), cancellation of any scheduled wake, and a durable stop flag that beats every
autostart and never clears itself; `stop --clear` by the owner is the only way back. `pause` /
`resume` provide the softer durable flags; `revoke-all` invalidates every pending approval
immediately. All verified by the endurance/recovery suites; the stop flag's supremacy over
autostart is asserted by test.

## 8. Recommendation: **KEEP SUPERVISED OFF — REMAIN SHADOW-ONLY. DO NOT ACTIVATE.**

Grounds: (1) G3's B-1/B-2 make supervised multi-cycle operation broken as built — the mode that
would be activated does not yet work beyond a single cycle; (2) limited-auto has no executable
form at this SHA (QA gap 2) — there is nothing to activate safely even if desired; (3) the live
broker allow-path has never been observed (QA gap 1); (4) the V1.1 ledger (F-2/F-4, B-3/B-4,
V-1..V-6, L-1/L-3/L-4) is substantial and cheap to burn down now while everything is fresh.
What the pilot DID prove: the fail-closed core, the audit chain, the shadow discipline, the
policy classifier, the full worker→review→decision cycle with a live Codex reviewer, and an
owner-touch cost of 0 on a clean cycle — the architecture is sound; the assembled loop needs the
B-row corrections and one more supervised rehearsal before any activation conversation.

Suggested sequence if the owner concurs: V1.1 correction unit (B-1..B-4 + F-2/F-4 + the
doctor-tz check) → re-gate the delta → one bounded `doctor --live` allow/deny probe → one live
SUPERVISED single-forward rehearsal → then, and only then, the activation conversation.

## 9. §19 return-packet fields

CURRENT PHASE / MODE: Phase 5 complete; shadow-only; supervised/limited-auto never engaged.
LIVE MAIN SHA: cb9a999 (unchanged since the owner's PR #150 merge).
CURRENT TASK / STATUS: M0-T036 in_progress, 85% (ledger); this packet is the Phase 5 deliverable.
WORKTREE / BRANCH: primary checkout on task/M0-T036-supervisor-bridge; frozen review identity 43848bd; controller checkout C:\SupervisorController at f68f578.
FILES CHANGED (since dispatch): supervisor package + suites; 2 CI/lock files under owner grants; control-plane records.
TESTS / CI: 1065 passed / 2 skipped locally (QA-reproduced); frozen-SHA CI 30886102559 all-green.
CODEX CLI + MODEL(S) VERIFIED: codex-cli 0.146.0; gpt-5.6-sol (live decision, attempt 1), gpt-5.6-terra (allowlisted fallback, never engaged live).
CLAUDE CLI/SDK CAPABILITIES VERIFIED: claude.exe 2.1.220 (canonical native); stream-json in/out; --max-turns honored; control_request round-trip live for deny; allow-path unobserved (QA gap 1).
SECURITY / CONTROL-PLANE FINDINGS: G5 PASS (0 blocking); CPV PASS (C1/C2 discharged); boundary rows affirmatively held.
CONTROLLER / TOOLCHAIN MANIFEST: controller 0.4.0-phase4; doctor overall PASS; config/model-selection doctor-validated (digest b2b927c6…).
PROTOCOL / SCHEMA VERSIONS: protocol 1.0.0; schema 1.0.0.
ISOLATION / DATA-EXPOSURE STATUS: shadow forwarded nothing; reviewer read-only sandbox; evidence packets bounded + digest-bound + redacted.
RESOURCE / USAGE STATUS: pilot cycles bounded (≤12 turns, 900 s wall, breakers armed — B-4 caveat recorded).
ROTATION PENDING / NEXT-UNIT SIZE: none pending; rotation never live-exercised (QA gap 4).
RECOVERY CLASSIFICATION: SAFE_CHECKPOINT at every boot; safe_no_auto_resume honored every time.
USAGE-LIMIT CLASS / RESET SOURCE: none encountered during the pilot.
RESUME-NOT-BEFORE / SCHEDULED TRIGGER: none scheduled.
PENDING EXTERNAL EFFECTS: 0 (journal-verified).
QUEUED ASK ITEMS / NOTIFICATION STATUS: 0 queued (run-5's blocking_ask was counted, not forwarded — shadow).
OWNER-TOUCH COUNT THIS TASK: pilot would-be touches per run above; actual owner touches this task = the three PR merges + the controller setup commands + the grants/decisions themselves.
PROPOSED POLICY WIDENINGS (OWNER APPROVAL PENDING): §6 proposal, inert.
BLOCKERS: none filed; B-1..B-4 recorded as blocking corrections for the next gate.
OWNER DECISION REQUIRED: keep-supervised-vs-activate (recommendation: keep shadow-only, §8); disposition of the V1.1 ledger; M0-T035 acceptance (separately, at the owner's instruction).
EXACT SAFE NEXT ACTION: owner reads this packet and decides; no agent action pending.
