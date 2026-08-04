# M0-T036 — diagnostics-triage record (D-007-R564 / R569 / R572)

- Recorded: 2026-08-04, orchestrator; committed so the Phase 5 decision packet can cite it.
- Scope: every Pyright diagnostic surfaced on the two shadow-pilot defect-fix units, enumerated
  file + line with a per-line verdict and the executing-test proof. The owner's independent
  returncode spot-check (codex_reviewer.py:463) is settled and recorded as such.
- Verdict vocabulary: **PRE-EXISTING** (line predates the fix), **FALSE-POSITIVE** (in the fix,
  type-checker misanalysis, no functional defect), **SETTLED** (owner-verified independently).

## A. Runner fix (F-3, session close) — 17 diagnostics, 2 files

### tools/agent_supervisor/claude_runner.py (7)

| # | Line | Diagnostic | Verdict | In session-close path? | In watchdog? |
|---|---|---|---|---|---|
| 1 | 267 | `final` param reported unused | PRE-EXISTING (`ClaudeStreamParser._handle`, parse layer) | no | no |
| 2 | 270 | same, second site | PRE-EXISTING | no | no |
| 3 | 550 | `graceful_close_failed` initial binding "not accessed" | FALSE-POSITIVE — initialized, reassigned in the `finally`, read at `RunResult` build | **yes** | no |
| 4 | 554 | `expected_results` "not accessed" | FALSE-POSITIVE — incremented per write, compared in the read loop | **yes** | no |
| 5 | 555 | `results_seen` "not accessed" | FALSE-POSITIVE — same pattern | **yes** | no |
| 6 | 556 | `unit_complete` "not accessed" | FALSE-POSITIVE — same pattern | **yes** | no |
| 7 | 671 | `graceful_close_failed` assignment in grace-expiry branch "not accessed" | FALSE-POSITIVE — same pattern | **yes** | no |

### tools/test_agent_supervisor_runner.py (10)

| # | Line | Diagnostic | Verdict |
|---|---|---|---|
| 8 | 271 | dict `update` overload mismatch (`run_fake` params helper) | FALSE-POSITIVE — test-scaffolding typing variance |
| 9 | 271 | companion argument-type diagnostic, same line | FALSE-POSITIVE — same |
| 10 | 413 | `.checkpoint_id` on Optional | PRE-EXISTING — assert-then-access test pattern |
| 11 | 415 | `.usage` on Optional | PRE-EXISTING — same |
| 12 | 420 | `.checkpoint_id` on Optional | PRE-EXISTING — same |
| 13 | 583 | `.summary` on Optional (new SessionCloseTests) | FALSE-POSITIVE — follows `assertTrue(result.ok)` |
| 14 | 592 | `.summary` on Optional | FALSE-POSITIVE — same |
| 15 | 612 | handler lambda `dict` vs `Mapping` variance | FALSE-POSITIVE — test helper typing |
| 16 | 619 | `.summary` on Optional | FALSE-POSITIVE — same as 13 |
| 17 | 653 | `.claude_session_id` on Optional | FALSE-POSITIVE — same |

**Honest boundary statement:** items 3–7 ARE bindings inside the session-close fix; the accurate
claim is not "none touch it" but "none is a functional defect." **Zero diagnostics touch the
watchdog** — that function is byte-identical to the pre-fix version and carries no diagnostic.

**Executing-test proof:** the 6 `SessionCloseTests` (prompt completion under 60s vs 120s wall;
`graceful_close_failed` flagged not-OK; mid-turn control_request answered over open stdin;
per-turn terminal results; unchanged self-exit; wall watchdog still owns the runaway unit) —
47 passed in the runner suite; full suite 1046 passed / 2 skipped at integration; live proof:
run 6's unit completed in ~2 minutes with no timeout flag (runtime-run6/audit.jsonl).

## B. Codex fix (F-6/F-7, provider schema + error surfacing) — 19 diagnostics, 2 files

### tools/agent_supervisor/codex_reviewer.py (9)

| # | Line | Diagnostic | Verdict | Touches validate_decision / classifier / audit path? |
|---|---|---|---|---|
| 1 | 48 | `redact_text` import "not accessed" | FALSE-POSITIVE — called in `provider_failure_reason` | **classifier** |
| 2 | 144 | "unreachable" | FALSE-POSITIVE — `DECISION_*` constants block; reachability misfire | validate_decision constants |
| 3 | 153 | "unreachable" | FALSE-POSITIVE — `DECISION_OBJECT_LIST_FIELDS` tuple | validate_decision constants |
| 4 | 166 | `_reject_wrong_types` "not accessed" | FALSE-POSITIVE — called at `validate_decision` entry | **validate_decision** |
| 5 | 204 | "unreachable" | FALSE-POSITIVE — inside `validate_decision` | **validate_decision** |
| 6 | 211 | "unreachable" | FALSE-POSITIVE — the deliberate runtime `not_an_object` guard Pyright deems type-impossible | **validate_decision** |
| 7 | 439 | `last_returncode` init "not accessed" | FALSE-POSITIVE — read at the failure outcome | **audit/outcome path** |
| 8 | 449 | `last_returncode` reassignment "not accessed" | FALSE-POSITIVE — same | **audit/outcome path** |
| 9 | 463 | "No parameter named returncode" | **SETTLED** — owner verified independently: keyword arg into the defaulted `ReviewOutcome.returncode` field; audit carries it | audit/outcome path |

### tools/test_agent_supervisor_reviewer.py (10)

Lines 263, 271, 292, 335, 341, 361, 362, 366, 367, 371 — all Optional-member access following
in-test assertions (assert-then-access unittest pattern). Verdict: FALSE-POSITIVE, all ten.

**Honest boundary statement:** several diagnostics sit exactly in the paths the owner asked
about — lines 144–211 in `validate_decision` and its constants, line 48 in the provider-failure
classifier, lines 439/449/463 in the audit/outcome path. The accurate claim: **every one is a
type-checker false positive; none is a functional defect.**

**Executing-test proof:** 74 reviewer tests passed at integration (19 new): the
`FlattenedConstraintTests` execute `_reject_wrong_types` and every moved constraint
(reject-tests per row of the 15-row constraint mapping); `ProviderRejectionTests` execute
`provider_failure_reason`/`no_decision_error` including the redaction assertion (`[REDACTED:`
present; seeded token absent) and the returncode-in-audit assertions (`detail["returncode"]`
== 1 and 0 respectively); `SchemaStrictSubsetTests` pin the flattened schema. Full suite 1065
passed / 2 skipped, zero regressions. Live proof: run 6's Codex decision COMPLETE on attempt 1
(runtime-run6/audit.jsonl, sequence 9–11).
