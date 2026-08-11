# M0-T036 Supervisor Bridge — Activation Checklist

**Status: SHADOW-ONLY. Not activated. Acceptance of M0-T036 does NOT activate anything.**

M0-T036 is accepted as a **shadow-only** pilot (owner decision, keep-shadow-only). This checklist
lists the prerequisites that MUST be satisfied before the supervisor moves beyond shadow mode. It is
owner-gated at every step; nothing here is authorized by M0-T036's acceptance.

## BLOCKING PREREQUISITES before ANY activation

### ⛔ R595 supervised rehearsal — MANDATORY BLOCKING (owner directive 2026-08-06, D-007-R619)
The **live context-threshold rotation-seam actuation** (R593 third live leg / QA-gap-4) was recorded
as an **accepted residual** (Option A) because it is **structurally infeasible as a synthetic probe
under R594** (the seam needs a real forward; R594 keeps shadow-only in force / nothing forwards). The
requirement is **NOT waived — deferred in time.** A **supervised rehearsal (R595)** that actually
actuates the rotation seam live and preserves its audit evidence is a **mandatory blocking prerequisite
BEFORE any of:**
- [ ] **supervised-auto activation**
- [ ] **limited-auto activation**
- [ ] **automatic product-task execution**
- [ ] **any claim that live session rotation has been proven**

Until R595 is satisfied and independently reviewed, none of the above may proceed, and R593 must
**never** be represented as fully live-proven (D-007-R621).

### Other standing activation prerequisites (from the Phase-5 decision packet + gate findings)
- [ ] Live-CLI account-quota exhaustion **classifier wired** (`QUOTA_EXHAUSTION_SIGNAL_VERIFIED=False`
      today → the model-chain switch fail-closes to PAUSE; disclosed by `doctor`). Needs its own
      security look (G3-A1 / G5-L-1 / G4-A1).
- [ ] Activation-blocking G3 B-rows (B-1..B-4) fixed and re-gated.
- [ ] Single-account Windows OS-ACL enforcement of the immutable controller config (G5-L-2), if the
      manifest-detection posture is deemed insufficient at activation.
- [ ] Live resource **sampling** wired into the loop for the R207 limit set (config/circuit-breaker
      knobs exist + are fail-closed today; live sampling is the documented Phase-2/3 boundary).
- [ ] Owner authorization at each activation tier (supervised → limited-auto → …).

## Accepted residual (visible per D-007-R620)
- **R593 / QA-gap-4** — live rotation-seam actuation: **ACCEPTED RESIDUAL, deferred to R595.** 2 of 3
  V1.2 live legs proven (allow round-trip, model-mismatch detection); the rotation leg is unit- and
  real-process-proven but **not live-actuated**. Owner directive D-007-R618 (Option A), 2026-08-06.


---

## M0-T042 G5 additions (2026-08-07) — pre-R595 hardening items

Registered at M0-T042 acceptance (G5 security review, PASS with pinned residuals; see
`project-control/reports/M0-T042-g5-security.md`). All three are MUST-RESOLVE before any
activation, alongside the existing checklist items:

1. **L-1 (must-fix-before-activation):** `parse_usage_telemetry` (codex_reviewer.py) must catch
   non-`JSONDecodeError` `ValueError` from `json.loads` on a >4300-digit integer in the untrusted
   `--json` stream (reproduced), so a pathological usage line yields USAGE_UNKNOWN / a sealed
   refusal record instead of crashing the review.
2. **I-1:** the AD-083 prohibited-content guard is structural (key-name/flag) detection only —
   add a semantic/size check or re-confirm `evidence.build_packet` remains the sole packet source
   at activation (concurs with M0-T042 G3 INFO-1).
3. **I-3:** bound the child-process stdout capture (process.py `communicate()`, pre-existing)
   before the ephemeral reviewer runs against a live untrusted Codex process.


---

## M0-T044 G3 additions (2026-08-07) - pre-activation items for the GitHub flow

Registered at M0-T044 gating (G3 code review PASS with pinned MINOR findings; see
`project-control/reports/M0-T044-g3-code-review.md`). Both are MUST-RESOLVE before the
automatic GitHub flow is wired into any live path (R595-gated activation):

1. **MINOR-1 (fail-open Tier B detection):** `github_flow.py` change-class detection derives only
   3 of the 11 Section 5.2 classes (workflow, lockfile/dependency-manifest, supervisor-code path);
   the 8 semantic classes (auth/session, additive DB migration, contract/schema addition,
   official-source connector, legal-corpus ingestion, draft-rule, scenario-calc, survey/PDF parser)
   and `deploy_definition` are not derivable from `policy.file_class` and would route Tier A
   (auto-permit) - fail-open. Before live wiring: make undetected-but-sensitive classes fail
   TOWARD review, or wire a semantic classifier. (Scoped AS-3 - workflow/dependency - is proven;
   the full 5.2 table is present as data.)
2. **MINOR-2 (defense-in-depth):** `authorize_push` inherits push_policy's empty-`authorized_branch`
   fall-through (non-main branch allowed when the grant's authorized_branch is ""). main/master/
   force remain hard-denied regardless. Before live wiring: assert a non-empty `authorized_branch`
   in `authorize_push`.


---

## M0-T044 G5 additions (2026-08-07) - pre-activation items (SEC-1/SEC-2/SEC-3/INFO-1)

Registered at M0-T044 gating (G5 security review PASS shadow-only; see
`project-control/reports/M0-T044-g5-security.md`). All MUST-RESOLVE before any live-path/R595
activation of the GitHub flow or the effect journal:

1. **SEC-1 (MEDIUM):** guard the live-path `ExternalEffectJournal.extra_specs` override channel -
   reject keys colliding with MODELED_EFFECTS, reject destructive extra specs, add a test that
   every live journal constructs with empty extra_specs, and extend the invariant-9 lock to
   instance extra_specs (today it inspects only the module-level registry).
2. **SEC-2 (MEDIUM, BROADENS the M0-T044 G3 MINOR-1 entry above):** the Tier B fail-open covers
   more than the 8 semantic classes + deploy_definition - detectable SECURITY_RELEVANT_CLASSES
   (permission_settings, hook, secret_bearing, launcher_script, submodule_config,
   attributes_filter) also route Tier A. Remediation is a CATCH-ALL: any file_class in
   SECURITY_RELEVANT_CLASSES not explicitly routed (and specifically permission/hook
   configuration per Section 5.4 item 3) must fail TOWARD security/control-plane review or
   Tier-D owner-stop, with tests. Treat the MINOR-1 entry as remediation spec ONLY together
   with this broadening.
3. **SEC-3 (LOW):** redaction discipline - require redacted descriptors in
   `MergeRequest.secret_scan_findings`; route caller-side logging of MergeEvaluation.conditions
   through redaction.py.
4. **INFO-1:** the live caller must audit every `FlowResult`, including refusals (this module
   journals only performed effects).


---

## M0-T045 G5/G4 additions (2026-08-07) - pre-activation items registered at gating

1. **G5 LOW-1 (MUST-RESOLVE before supervised-auto/limited-auto activation):** bind the
   cross-process forwarded bytes to the OPERATOR-NAMED approval at approval time
   (`approve_pending_prompt` currently freezes `approved_digest = digest_of(parked bytes)`
   without cross-checking the operator-supplied `--approve-prompt-digest` serialization), so
   the park->approve window does not rest solely on the journal file ACL. loop.py:626-654 +
   cli.py:1628-1662; see M0-T045-g5-security.md.
2. **G4 estop audit-fork follow-up:** the `emergency-stop` command and the main loop can write
   CONCURRENT audit sequence numbers (fork honestly surfaced via `audit_chain_ok:false`).
   Before activation: a test locking the forked-chain shape + explicit owner acknowledgement
   that an emergency stop leaves the audit log unappendable-without-repair (fail-closed).
   See M0-T045-g4-qa-review.md.

Note: the R595 supervised rehearsal itself is COMPLETE (all legs live-proven at `afc2da5`;
sealed evidence M0-T045-r595-rehearsal/). The R593 residual is closed BY EVIDENCE. Items above
are the remaining pre-ACTIVATION hardening set; activation stays an explicit owner decision.

---

# MECHANICAL RECONCILIATION — 2026-08-08 (owner am.12 R131 step; recorded at M0-T046 acceptance)

Per D-010 am.12 ("Do NOT activate supervised-auto until this pre-activation task is accepted and
all remaining activation-checklist blockers have been mechanically reconciled as satisfied"),
each remaining item above is reconciled against ledger evidence. M0-T046 ACCEPTED (gates
G0/G2/G3/G4/G5 PASS at identity `660bf133`/`32ea6f1`, code `a27068d`; DCV: R124 adjudicated
PASS, 11 PASS + R132 deferral; accepted count 67).

| Checklist item | Status | Evidence |
|---|---|---|
| ⛔ R595 supervised rehearsal (D-007-R619) | **SATISFIED** | M0-T045 ACCEPTED — all legs live-proven at `afc2da5`; sealed evidence `M0-T045-r595-rehearsal/` (SHA-256 manifest); R593 closed BY EVIDENCE, never waiver (D-007-R621). |
| Quota-exhaustion classifier wired (G3-A1/G5-L-1/G4-A1) | **SATISFIED** | M0-T041 ACCEPTED AS-1: `classify_quota_exhaustion` + fixture corpus wired into `make_launch_probe`; `QUOTA_EXHAUSTION_SIGNAL_VERIFIED=False` BY DESIGN (fail-closes to PAUSE, doctor disclosure) until a live exhaustion is captured under owner credentials during supervised operation — the wiring + security look the item demanded are done (M0-T041 G3/G4/G5 PASS). |
| Activation-blocking G3 B-rows (B-1..B-4) | **SATISFIED** | Fixed in V1.1 (frozen `c193a52`), independently re-gated (`M0-T036-V1.1-G3-code-delta-review.md` §2); re-verified per-row with regression tests at M0-T041 AS-2 (producer report table, M0-T041 gates PASS). |
| Single-account Windows OS-ACL (G5-L-2) | **SATISFIED (mechanism); live apply = owner UAC step** | Owner RESOLVED the judgment item in am.12 R127 (single-account writable ACL NOT sufficient). M0-T046 delivered the R128 boundary: `os_acl.py` fail-closed verdict (DACL + owner-elevation + bounded probes; absolute System32 tools), `harden_controller_config.ps1` (elevated apply/rollback, refuses unelevated), doctor posture wiring; 31 tests. The live `PROTECTED` capture on the real config happens at the owner's elevated apply (R128's own UAC clause) and is a named precondition in the activation decision step below. |
| R207 live resource sampling | **SATISFIED** | M0-T041 ACCEPTED AS-3: `resource_sampling.ResourceSampler` + loop `_check_resources` at cycle entry (fail-closed both directions; honest structural-unknowns), doctor disclosure; 10 tests. |
| Owner authorization at each tier | **OPEN — owner-typed decision (R131/R132)** | This is the activation decision itself; never reconciled by an agent. |
| M0-T042 G5 additions (L-1, I-1, I-3) | **SATISFIED** | Resolved in M0-T045 increment 1 (pinned set A1-A4; producer report + gates PASS; M0-T045 ACCEPTED). |
| M0-T044 G3 additions (MINOR-1, MINOR-2) | **SATISFIED** | Resolved in M0-T045 increment 1 (pinned set B1-B3; M0-T045 ACCEPTED). |
| M0-T044 G5 additions (SEC-1/2/3, INFO-1) | **SATISFIED** | Resolved in M0-T045 increment 1 (pinned set C1-C5; M0-T045 ACCEPTED). |
| M0-T045 G5 LOW-1 (park→approve) | **SATISFIED** | M0-T046 scope 1: park-time byte anchor, fail-closed approval binding, sealed refusals, 8 adversarial tests; DCV R124 adjudicated PASS (LOW-1 window closed; literal construction proven impossible-to-strengthen). |
| M0-T045 G4 estop audit-fork follow-up | **SATISFIED** | M0-T046 scope 2: append now refuses on a detected fork (real behavior fix) + 7 regression tests locking the four R126-acknowledged conditions 1:1 (mutation-proven non-vacuous, G4). |

## NEW pre-ACTIVATION items registered at M0-T046 gating (fold into the decision step)

1. **G5 C2 (M0-T046):** the park→approve byte anchor is journal-resident; a consistent two-field
   journal forgery (`prompt` + `prompt_bytes_digest`) still forwards under a valid approval —
   same excluded class as the original LOW-1, SHADOW forwards nothing. Before supervised-auto:
   owner ACCEPTS this residual verbatim in the activation decision line, or orders the
   content-binding fix (bind forwarded content to the operator-known `approval_digest`, e.g.
   inject FORWARDED-AT at forward time). See `M0-T046-g5-security.md` C2.
2. **Live PROTECTED capture (M0-T046 AS-4 live leg / G4 G1):** after the owner's elevated
   `harden_controller_config.ps1` apply, orchestrator captures `doctor --config <path> --json`
   showing `controller_config_acl.protected: true` and files it as evidence. Precedes activation.

**Bottom line:** every mechanically reconcilable checklist blocker is SATISFIED with ledger
evidence. What remains before supervised-auto is exactly the owner-held set: (a) the elevated
ACL apply + orchestrator live-PROTECTED capture, (b) the C2 residual decision, and (c) the
owner-typed activation decision line (R131/R132). ⛔ Activation itself remains prohibited until
the owner types the decision (R131); M2-T015/T016 stay HELD until then (R133).

---

# ACTIVATION-RECORD PIN — 2026-08-08 (M0-T052 G5 C1/C2; recorded by the orchestrator)

Registered at the M0-T052 G5 security review (`M0-T052-g5-security.md`, SEC-MAJOR residual;
required corrections C1/C2). BINDING for supervised-auto operation from this date:

1. **C1 — host containment precondition (HARD; wording required by the G5 delta attestation).**
   SUPERVISED-AUTO — and any run that spawns a live worker — may be activated/run ONLY on a host
   where BOTH (1) `doctor` reports `containment_default: ok, job_object` AND (2) the run's own
   worker-launch audit records `containment: job_object` for that cycle. If either the `doctor`
   snapshot or a live launch reports `taskkill` or `process_group`, activation/continuation is
   REFUSED. Rationale: a supervisor externally killed during the `START_CLAUDE` window leaves an
   orphaned worker that `recover_boot` cannot detect (the production launch path does not record
   child pids until M0-T053), so an operator `start` would double-launch over the live worker.
   Until M0-T053 lands the fail-closed launch-path containment gate, this bar is a WRITTEN
   precondition only (not runtime-enforced); the live `containment: job_object` audit line MUST
   be re-verified on every activation. Live host evidence at this activation satisfies both
   criteria: `containment_default: ok — "default containment on this host is 'job_object'"`
   (doctor-pre-activation.json) and the cycle-1 worker-launch audit line
   `containment: job_object`.
2. **C2 — child-accounting wiring (follow-up M0-T053).** `record_launched_child` /
   `clear_child_record` are not wired to the production launch path, so `recover_boot`'s
   surviving-child fail-closed is inert in production; until M0-T053 lands, double-launch
   protection rests on the Job Object alone (hence pin 1).

These pins ADD restrictions; they relax nothing. The N-4 / N-5 / MINOR-2 residuals accepted in
the owner's activation decision (D-010 source-023) are unchanged.

---

# ACTIVATION-RECORD PIN — 2026-08-11 (M0-T053 G5; recorded by the orchestrator)

Registered at the M0-T053 G5 security review (verbatim:
`project-control/reports/M0-T053-G5-security-review.md`, VERDICT PASS). M0-T053 closes the C1/C2
double-launch residual and the reviewer confirms the hole is shut on the production path: it is now
"two independent live mechanisms" rather than one platform mechanism with the other inert.

**These three items are REQUIRED CORRECTIONS BEFORE M0-T056's FIRST LIVE ACTUATION.** They do NOT
block M0-T053's acceptance. They are pinned here, in the same place and for the same reason M0-T052's
C1/C2 produced M0-T053: so the next task cannot be built on the assumption they are already closed.
The reviewer's exact words: "I would NOT accept an M0-T056 that treats these residuals as already
closed. I WOULD accept M0-T053 now with them pinned."

Why M0-T056 specifically, and not now: it changes the threat model in two ways M0-T053 never faced —
it **adds a second spawner** (`turnover_adapters.py:434 make_subprocess_command_runner`, the
successor-launch seam, currently unwired, spawning via `process.run` with no accounting and no gate),
and it **removes the human**. Residuals that are tolerable because an operator reads an audit line
stop being tolerable when nobody is reading.

1. **P1 — verify the termination you assert (G5 finding 4).** `claude_runner.py:1283-1298` discards
   `container.terminate_all()`'s boolean, swallows exceptions, and never `wait()`/`poll()`s, yet the
   raised message states the worker was terminated. On the degraded-taskkill path
   `terminate_process_tree` can legitimately return False. Compound failure = degraded containment +
   failed journal write + failed kill = a LIVE UNRECORDED orphan with an empty record and a traceback
   exit, after which the next `start` reads SAFE_CHECKPOINT and DOUBLE-LAUNCHES. Lands squarely on
   D-010-R347. Fix: capture the boolean, bounded `process.wait()`, and raise a DISTINCT code if the
   child is still alive.
2. **P2 — make `clear_child_record` remove by (pid, start_token), not whole-key (G5 finding 5).**
   `recovery.py:190-191` wipes the whole key, so settle clears records it did not create. Latent today
   because there is exactly one recorder. The moment M0-T056's successor-launch seam records anything,
   a worker's clean exit ERASES the live successor's record — fail-open on precisely the
   no-duplicate-workers invariant R347 makes binding.
3. **P3 — achieved per-cycle containment must become a STOP, not a record (R4 enforcement half).**
   M0-T053 enforces criterion (1) of the 2026-08-08 pin (host DEFAULT containment). Criterion (2), the
   ACHIEVED `containment: job_object` line, is still only recorded on `RunResult.containment` and the
   `claude_process_started` transition. A cycle whose `run_result.containment != "job_object"` must
   PAUSE. Unattended, nobody reads the audit line.

Recommended alongside them, not required: **P4** catch `RunnerError` in `cmd_start` as a
`loop_refusal` payload plus an audited event (G5 finding 7 — `RunnerError` and `LoopError` are
siblings, so the traceback exit produces no structured refusal record; verified lock-released,
no partial row, next start not misled, so it is loud and fail-closed but silent to a
supervisor-of-supervisor); and **P5** register `doctor --live` (`preflight.py:126-131`, spawns a real
child with no container, record, or gate — pre-existing, cannot duplicate a worker) for the M0-T056
containment sweep.

4. **P6 — A REVIEWER THAT RETURNS NOTHING MUST BLOCK, NOT PASS SILENTLY.** Added by the orchestrator
   from *observed* session-14 behaviour, not from a reviewer finding. Across this session **four**
   independently-dispatched reviewers went idle having completed their analysis without ever
   delivering it; each verdict was recovered only because a human-paced orchestrator noticed the
   silence and re-dispatched. Two of those four then returned REQUIRED corrections, so the missing
   reports were not empty — they were load-bearing.

   Unattended, this is the `d45f330` failure with a different cause: **absent evidence treated as
   passing evidence.** M0-T056 must therefore treat "gate dispatched, no verdict returned" as a
   hard fail-closed stop with a recorded reason — the same posture `project_control.py accept`
   already takes when a `reviewed_sha` is stale or a relevant file is dirty. A dispatched-but-silent
   reviewer must never be indistinguishable from a clean review, and no timeout may downgrade to
   "proceed".

   Note for whoever builds this: the correcting factor in session 14 was NOT human judgement. No
   human approved or blocked anything all session, and the one human-gated step (`accept`) caught
   zero defects. What caught the defects was executable evidence (a red CI run), machine-enforced
   producer/reviewer independence, adversarially-scoped review prompts, and redundant reviewers who
   converged — and, in one case, corrected each other. Those are reproducible without a human. The
   reviewer-silence gap is the one that was covered only by someone being awake.

5. **P7 — CRITERION (1)'s WORDING IS OPERATOR-MISLEADING ON NON-WINDOWS HOSTS.** Raised by the
   M0-T053 G3 review. The 2026-08-08 pin words criterion (1) as "`doctor` reports
   `containment_default: ok, job_object`". The M0-T053 gate and `doctor` share the same containment
   SOURCE (`default_containment_kind()`), so the reported KIND can never diverge — but their
   VERDICTS do. `_check_containment_default()` (`cli.py:1102-1129`) returns **ok=True on POSIX when
   the kind is `process_group`** (line 1124 sets `expected` per-OS) and **ok=True on a Windows host
   that refuses a Job Object** (1119-1123). So on Linux `doctor` prints `containment_default: ok`
   while the gate REFUSES. The direction is safe — the gate is strictly stricter — so this is not a
   defect. But an operator who checks only the `ok` flag on a non-Windows host would wrongly believe
   criterion (1) is met. **Read criterion (1) as requiring `kind == job_object`, not merely
   `ok == true`.** Describe the gate as sharing doctor's containment SOURCE, never as "doctor
   parity" — an earlier orchestrator note and the PR #218 body used that phrase and it is corrected
   here.

6. **P8 — DEPLOYMENT NARROWING (operational, not a defect).** The M0-T053 gate is unconditional on
   mode, so `start` now HARD-REFUSES on every POSIX host — including Render — and including shadow
   mode, which does spawn a real worker. **The supervisor is now Windows-Job-Object-only.** This
   matches the pin's "any run that spawns a live worker" and breaks nothing today, but M0-T056 must
   not assume a POSIX runner is available for the isolated live proof, and the owner should know the
   supervisor cannot currently `start` on Render.

This pin ADDS restrictions; it relaxes nothing, and it does not lift or alter the R595 prerequisite
structure above.
