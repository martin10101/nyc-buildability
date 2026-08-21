# D-023 campaign findings pool (for the single consolidated correction round)

Per D-023-R016/R017 (complete the investigation, then ONE consolidated correction — no
drip-feeding), every non-blocking finding from per-task gates accumulates HERE and is
addressed once, at M0-T085, against the frozen campaign identity. Must-fix findings block
their own task's gate immediately and never wait for this pool.

Severity vocabulary: docs/ENGINEERING_RELIABILITY_STANDARD.md §9.

## Open findings

| # | Source | Severity | Location | Finding (condensed; verbatim in source report) |
|---|---|---|---|---|
| F-001 | M0-T078 G3 | minor | M0-T078-producer-report.md AS-6 | Digest block mixes CRLF/LF encodings; state normalization or use git hash-object (no drift — verified). |
| F-002 | M0-T078 G3 | minor | ENGINEERING_RELIABILITY_STANDARD.md §7.1 (also §8.6, §8.9) | Near-verbatim restatement of LEAN B5 / G4 list / principle 7 despite §0's no-copy rule; cite instead. |
| F-003 | M0-T078 G3 | minor | ENGINEERING_RELIABILITY_STANDARD.md §6.5 | Add one-clause cross-reference to the existing single retry layer (services/api/app/resilience/, M2-T011) to prevent a second retry layer. |
| F-004 | M0-T078 G3 | minor | M0-T078-producer-report.md §1 | Report prose says "five invocation triggers"; frontmatter names seven. Deliverable correct. |
| F-005 | M0-T078 G5 | minor | ENGINEERING_RELIABILITY_STANDARD.md §9.2 | "Unexplained severity is downgraded when challenged" names no adjudicator; name the reviewer of record or the gate, never the producer. |
| F-006 | M0-T078 G5 | minor | ENGINEERING_RELIABILITY_STANDARD.md §9.1 | Phrasing could be cited against defense-in-depth G5 findings; clarify that a named plausible mechanism suffices for security findings. |
| F-007 | M0-T078 DCV | minor | M0-T078-producer-report.md AS-2/AS-8 | Shell-wrapper EXIT= echoes pasted inside blocks labeled "verbatim full output"; substance verified correct. Evidence-fidelity family with F-001. |

## M0-T079 correction round (issued as one set; tracked to closure at re-review)

G5 FAIL at reviewed identity c52613f. Consolidated correction C1–C12 in
`M0-T079-consolidated-correction.md`. Must-fix: C1 budget self-reset via missing/malformed
record (containment break); C2 credential leak through unredacted probe evidence. Important:
C3 argv-replay deny-set, C4 per-day tally decay, C5 typed refusals for corrupt state, C6
tamper/breaker/refused audit events, C7 missing-input exit code, C8 blocker authority, C9
expired-deadline gate. Minors: C10 drift re-pin, C11 exhaustion escape, C12 hygiene. Status:
issued to producer; awaiting corrected identity + full re-review (G5 must clear both must-fix).

- **Host act deferred to owner checkpoint — journal-DB ACL hardening for
  `%LOCALAPPDATA%\NYCBuildabilitySupervisor`.** Honest scope (G3 re-review minor #4 + G5
  re-review): C1 closes the **in-band** budget self-reset (a run nulling `started_at_epoch`
  or writing a malformed record through the code's own `start()` path — the round-1 must-fix).
  It does NOT close the **raw-SQLite-write** class: a true row DELETE, a fully-forged record
  with a recomputed unkeyed `budget_digest`, dropping the `budget_digest` field, or rewriting
  elapsed/counters directly — all of which require write access to the un-ACL'd journal DB.
  G5's security judgment (accepted): a keyed/HMAC digest cannot help because the adversary is
  the worker running as the **same OS user** (it can read any key the supervisor can), and no
  key material exists on this build; the existing `harden_controller_config.ps1` ACL pattern
  applied to the journal DB directory closes the whole class. **Recommendation carried to the
  owner checkpoint: name the journal-DB ACL item on the R595 activation checklist as a
  prerequisite, not merely a finding.** Round-3 additionally requires the `budget_digest`
  field (closes the cheapest raw-DB variant for free). **Delta-review addendum:** round-3 D1 makes
  `exit_detail` operator-visible in the exhaustion refusal; `budget_digest` covers only the budget
  block, so a raw-DB writer could spoof (not exfiltrate — redaction still applies) the refusal text
  an operator reads. Same raw-DB adversary class; the owner-checkpoint ACL item should cover "the
  text the operator reads", not only the durable record.
- **Infra note (delta-review minor #1):** `tools/agent_supervisor/cli.py` is at exactly its
  modularity limit (2953/2953) after T079. The next campaign task that edits cli.py (T081/T082/T084)
  must extract before adding — flag to those producers.
- **F-008 (G5 re-review, pre-existing, not T079):** `cmd_status --json` (cli.py:1477) prints
  journal-derived content via a bare `json.dumps`, unredacted — a credential planted in a
  transition detail would reach stdout. Out of T079 scope (its only cmd_status change is a
  prose string) but contradicts C2's now-general "stdout is a transmission" docstring. Pool
  for a later status-command redaction pass / M0-T085 settlement.

## Observations queued for M0-T085 settlement (not defects)

- O-001 (T078 DCV): handoff §6.4's fourth bullet (task-packet fields / gate assertions making
  reliability-standard triggers executable rather than prompt-only) is owned by no campaign task;
  settle ownership or defer explicitly at M0-T085.
- O-002 (T078 DCV): CLAUDE.md/AGENTS.md discovery pointers adjudicated justified (G3 + DCV
  concur; 31-token measured cost).

## Resolved findings

(none yet)
