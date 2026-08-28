# M0-T095 — Unit H2: root-cause repair gate + GitHub effect integration — D-024 Phase G

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R105** (Phase G; packet-named). Status: **STAGED (claim + G0 + scenario pack)** — the
seq-20 session accepted unit H1 (M0-T093), claimed this unit, and authored this pack at the
clean acceptance seam under the D-010 R113/R114 rotate-at-seam ceiling (the same pattern that
staged units F, G, and H1). The successor implements from this frozen pack with a fresh
context budget. No implementation code is written at this staging seam. Applicable set:
**46 requirements** (R076–R078 root-cause core, R090/R091 GitHub-effect core, R105/R112/R114,
+ the standing conduct/identity/testing set; resolved live via `evaluate_task_refs`: ok=true,
no missing/invalid/unresolved).

## 0. Reuse boundary (R018: prove existing architecture, extend — never duplicate)

| Existing surface (REUSE, do not duplicate) | What it already provides | Unit-H2 extension |
|---|---|---|
| `github_flow.py` (Tier A/B/D decisions, S5.5 ten merge conditions, S19.4 proof list; SHADOW-ONLY injected `GitHubRunner`) | the PROVEN ordinary-GitHub-flow decision logic: task-branch push, PR open/update, green-merge conditions, Tier-B specialist routing, Tier-D hard-denies | the 16.8 COMPLIANCE VERIFICATION target (R105 "confirmation", R114): prove which named 16.8 cases its existing tests already cover, then add ONLY the uncovered cases; never rebuild the flow |
| `external_effects.py` + `durable_state.record_before_effect`/`record_after_effect` | exactly-once external effects: content-derived idempotency keys, before-record-then-effect-then-after-record, PENDING→AMBIGUOUS reconciliation before any retry | R090's journaling/idempotency/reconciliation already exists — verify against the 16.8 cases (remote-success/local-timeout restart, duplicate PR/comment idempotence) and extend only where a named case has no proof |
| `push_policy.py` | protected/default-branch write, force-push, and suspected-secret HARD-DENY | E2/E8 cases reuse these predicates; never re-decide them |
| `codex_reviewer.py` + `review_packet.py` + `ephemeral_review.py` | the bounded Codex review packet path and reviewer invocation | the R078 checkpoint questions ride the EXISTING packet as a structured section; the repair-gate verdict follows the unit-H1 `bridge_output_disposition` pattern (typed disposition, never auto-accept) |
| `evidence.py` (packet building) + `refusals.py` (typed outcomes) | bounded digest-bound evidence packets; machine-readable refusal contract | repair-gate refusals are new reason codes on the existing contract; no new exit-code outcomes unless genuinely new class |
| `tools/code_graph/` (SHA-stamped homegrown index; advisory) | dependency/impact and who-consumes queries | R076/R112 unreachability proofs: "search/graph evidence" = grep + code-graph queries recorded IN the RepairRecord; graph is advisory, stale data reported never trusted (R080) |
| unit-H1 `refusal_bridge.py` patterns | typed-error policy modules, disposition pattern, closed vocabularies, record-intent-only posture | mirror the module style; the repair gate is deterministic policy + records, SHADOW-ONLY like everything else |
| supervisor-freeze citation convention (`.claude/rules/supervisor-freeze.md` §2/§3) | every supervisor task cites a D-024-R### id in packet + commit | the 16.8 freeze fixture (E13): a fixture/test that REJECTS an uncited supervisor change record |
| `M0-T093-evidence-map.json` / `M0-T094-evidence-map.json` | worked DCV evidence-map templates | build the 46-row map per behavior cluster the same way |

Genuine gaps (the ONLY things to build): `repair_gate.py` (the R076 RepairRecord protocol +
R078 checkpoint-question set + patch-stacking rejection policy + R077
CompatibilityException records with expiry-blocks-acceptance), thin wiring of the
checkpoint questions/disposition into the existing review-packet path (record-only),
the 16.8 gap cases not already proven by existing github_flow/external_effects tests
(expected: PR classification E11 + freeze-citation fixture E13; prove-first will tell),
and the §1 matrices as `tools/test_agent_supervisor_repair_gate.py`.

## 1. Acceptance-scenario pack (pre-implementation; sections 16.6 + 16.8 — R112/R114)

### 16.6 root-cause replacement matrix (R076/R077/R078/R112)

| ID | Scenario (Given / When / Then) | Key reqs |
|---|---|---|
| T1 | Given a defect fix that ADDS a wrapper/retry/fallback/flag around a known-bad path without justification, when the repair gate evaluates the RepairRecord + R078 answers, then it REJECTS with a typed patch-stacking reason. | R076/R078/R112 |
| T2 | Given a direct root-cause repair on sound structure with a bound regression test, when evaluated, then it is ACCEPTED without demanding a broad rewrite. | R076/R078/R112 |
| T3 | Given bounded-replacement mode, when the record lacks proof that the obsolete implementation/dead callers/duplicate fallbacks were removed AND unreachability evidence (search/graph refs), then REJECT; with the proof, accept. | R076/R112 |
| T4 | Given recorded search/graph evidence naming stale callers or duplicate fallbacks still reachable, when evaluated, then the gate surfaces them and refuses "one authoritative path" until resolved. | R076/R112 |
| T5 | Given a RepairRecord whose regression test does not exist or does not reference the defect, when evaluated, then REJECT ("regression test failing for the right reason" unproven); a valid binding records test id + failure condition. | R076/R112 |
| T6 | Given a temporary dual path, when its CompatibilityException lacks ANY of: written reason, owner/task identity, measurable removal condition, telemetry key, removal task + deadline/milestone, anti-default tests — then the record is REFUSED (typed, per missing field). | R077/R112 |
| T7 | Given a CompatibilityException past its deadline/milestone, when task acceptance evaluates, then acceptance is BLOCKED citing the expired exception. | R077/R112 |
| T8 | Given a fix proposal that deletes unrelated working code, when evaluated, then the gate refuses (root-cause lane never authorizes broad rewrites or unrelated deletion). | R076/R112 |
| T9 | Given a complete R078 answer set (root cause; old logic removed vs covered; one authoritative path; the failing-if-removed test; wrapper justification; retained-behavior removal plan), when any answer is missing/evasive, then the checkpoint REFUSES; complete answers → typed PASS disposition (never auto-accept — the unit-H1 disposition pattern). | R078 |

### 16.8 GitHub / external-effect matrix (R090/R091/R114)

| ID | Scenario | Key reqs |
|---|---|---|
| E1 | Correct branch/base/head identity recorded and verified for every effect (reuse github_flow identities). | R090/R114 |
| E2 | Protected/default-branch write REJECTED (reuse push_policy HARD-DENY). | R090/R114 |
| E3 | Overlapping worktree writer REJECTED (reuse lease/writer machinery). | R090/R114 |
| E4 | Commit/push only after required local checks pass. | R090/R114 |
| E5 | Remote-success/local-timeout (crash between effect and after-record) reconciled on restart from the effect journal — never blindly rerun. | R090/R114 |
| E6 | Duplicate PR/comment/update idempotent (content-derived idempotency keys). | R090/R114 |
| E7 | Frozen diff identity change INVALIDATES prior review (re-review required). | R091/R114 |
| E8 | No credentials in any journal/packet/record (reuse redaction + push_policy secret deny). | R090/R114 |
| E9 | Codex cannot stage/commit/push/merge (read-only reviewer contract unchanged). | R022/R114 |
| E10 | Pre-existing PRs (incl. #241) never merged without explicit owner authority. | R010/R114 |
| E11 | Expected-open / deliberately-unmerged / stale PRs classified SEPARATELY; no snapshot silently closes/merges/redefines live status. | R114 |
| E12 | Failed required checks BLOCK the effect per policy. | R114 |
| E13 | A supervisor-freeze fixture REJECTS an uncited supervisor change record (packet/commit must cite a D-024-R### id). | R017/R114 |
| E14 | R091 consolidated-round shape: findings from multiple reviewers consolidate into ONE correction round at a frozen identity; drip-feeding (per-finding fixes moving identity repeatedly) is refused by the record shape. | R091 |

Prove-first duty on E1–E12: the successor FIRST maps each case to the existing
github_flow/external_effects/push_policy test packs (many are expected to be already
proven); a case with existing proof is CITED, not re-implemented. Only unproven cases
get new tests. All effects remain SHADOW-ONLY (injected runners/fakes; R595 untouched).

## 2. Owner-gated items (flagged, not blocking the deterministic core)

- Live GitHub publication (real push/PR/comment) stays behind R595 activation; every 16.8
  proof runs against injected runners and fixture repos, the github_flow convention.
- No C1 live canary is required by this unit's applicable set.

## 3. Implementation guidance for the successor (not yet done)

- **Modularity:** one NEW focused module (`repair_gate.py`); thin review-packet wiring;
  mirror unit-H1's typed-error/disposition patterns. Watch the 750-SLOC justify threshold —
  record the cohesion judgment in the report if crossed (H1 precedent: G3/G5 recorded it).
- **R078 questions as data:** a closed tuple of question keys; an answer set missing a key
  refuses mechanically (never free-prose evaluation).
- **CompatibilityException:** frozen dataclass, one typed refusal per missing field (the
  Lean B6 one-invariant-per-test discipline); expiry check consumes an injected clock/
  milestone fact, never wall-clock (`Date.now` discipline; models.to_utc_iso convention).
- **16.8 mapping table:** put the case→existing-test citation table IN the report §4 so
  the DCV can reproduce it row by row.
- **DCV scale:** 46 applicable requirements; `M0-T093-evidence-map.json` is the worked
  template (49-row predecessor).
- **Environment:** long background python runs are externally killed on this box — run
  suites in foreground chunks; never run a mutation pass while a suite is in flight;
  `test_directive_compliance` by class groups.

## 4. Evidence (populated during implementation — successor)

(pending — staging seam only)
