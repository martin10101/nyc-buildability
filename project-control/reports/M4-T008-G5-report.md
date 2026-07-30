# M4-T008 — G5 security review (D-004 Step 4 pilot; reviewer return, captured verbatim)

Orchestrator capture note: reviewer = security-reviewer, unnamed spawn, explicit Fable 5, frozen
SHA `2122cd27a49511df079e0bf30baf5093d384a012` (task/M4-T008-df6-exceptions). Return preserved
verbatim below (transport entity-decoding only; one absolute worktree path normalized to
repo-relative form per the no-machine-specific-data rule).

---

All evidence is complete. Here is the G5 report, returned verbatim for the orchestrator.

---

# Gate Report

- Gate ID: G5 (security review)
- Task ID: M4-T008 (D-004 Step 4 pilot; DF-6 rule-engine hardening)
- Reviewer: security-reviewer (independent, read-only)
- Producer: rules-engineer (Opus 5 spawn, harness-isolated worktree; orchestrator exact-diff port)
- Result: PASS
- Clean environment/worktree used: `.claude/worktrees/M4-T008-df6-exceptions`, HEAD confirmed `2122cd27a49511df079e0bf30baf5093d384a012` (`git rev-parse HEAD`), `git status --porcelain` empty. Diff base `84c1bf29243bb862d344c909099c9bd9a3f6a766` (parent of HEAD, verified in `git log`). Diff = exactly 4 files: `services/api/app/rules/evaluator.py`, `services/api/tests/rules/test_r5_height_setback.py`, `services/api/tests/rules/test_rules_df6_exception_indeterminate.py` (new), `project-control/reports/M4-T008-producer-report.md` (new).

## Acceptance criteria reviewed

AS-1 through AS-6 from `project-control/tasks/M4-T008.json`, reviewed through the seven security dimensions in the dispatch scope (findings below). AS-1/AS-2/AS-3/AS-4 behavior reproduced via the 328-test run plus independent adversarial probes; AS-5 verified by blob hash, not by producer claim; AS-6 (attestation/no-CLI-writes) consistent with the producer report §1 and the orchestrator progress log.

## Directive/requirement verification

M4-T008 is in-regime (`directive_refs: D-004 ALL`). Full per-requirement D-004 verification is the directive-compliance-verifier's pass per the gate skill; this G5 verifies the security-relevant items I can independently observe at the frozen SHA: D-004-R302 (attestation before first write — recorded 4/4 PASS in producer report §1 and the task progress log) and D-004-R303 (no git/gh/CLI writes by producer — diff contains no control-plane writes beyond the producer's own report file, which is explicitly allowed). Verdict for these two at 2122cd2: PASS. No security finding contradicts any D-004 requirement.

## Steps independently executed

1. `git rev-parse HEAD` + `git status --porcelain` + `git log --oneline -3` — frozen-SHA and cleanliness confirmation.
2. `git diff --stat` / `--name-status` base..frozen — containment enumeration.
3. Full read of `evaluator.py` (both helpers, all callers), `coverage.py` (`most_severe` ordering), `operations.py` (predicate totality), `dsl.py` (`_check_predicate_refs`), `rule_definition.schema.json` predicate `$defs`.
4. `sha256sum` of both `rule_evaluation.schema.json` copies + `git rev-parse <sha>:<path>` blob IDs at base and frozen SHA for both copies.
5. Read-only adversarial probe (`python -c`) of `_apply_exceptions` with: empty-dict condition, op-without-input leaf, unknown op, non-dict condition, exception missing `id`, repeated-run determinism, falsy-but-supplied values.
6. Ruleset scan (all 7 `*.rule.json`): no leaf predicate without `input`; no `exists` op anywhere.
7. `grep` of `integration.py` for exception swallowing: none — evaluation errors propagate (fail-closed at service boundary).
8. `python -m pytest tests/rules -q` in worktree `services/api`.
9. Pattern scan of the full diff for `eval(`/`exec(`/subprocess/socket/urllib/requests/http(s)://, api_key/secret/password/token, `C:\Users`/MLFLL — zero hits.

## Expected versus actual

| Check | Expected | Actual |
|---|---|---|
| HEAD | 2122cd27a49511df079e0bf30baf5093d384a012 | Match |
| Diff containment | within allowed_paths | 4/4 files inside `services/api/app/rules/`, `services/api/tests/rules/`, producer report |
| Schema copies vs base | byte-unchanged, both | blob `9e99b908a875cc190a410213ad2763edb286f022` at base AND frozen, both copies; sha256 `7454b3d5edb6a6...` identical across copies |
| `pytest tests/rules -q` | 328 passed | **328 passed in 4.43s** (exact) |
| Determinism probe | identical notes across runs, sorted names | identical; `['a', 'b']` sorted |

## Findings per dispatch dimension

**1. Fail-open regression hunt — PASS.** Complete branch enumeration of `_unsupplied_predicate_inputs` + `_apply_exceptions`: (a) `condition: null` → applies, unchanged; (b) unsupplied detection is by-name via `_predicate_input_names`, which is a strict superset of what `_eval_predicate` reads (it walks combinators AND the node's own `input` unconditionally, while `_eval_predicate` reads a leaf `input` only when no combinator is present) — over-detection is possible (escalation-only), under-detection is structurally impossible; (c) `not holds` + unsupplied → PRR + note + `continue`, never silent; (d) `not holds` + all supplied → skip (legitimate: evidence-based); (e) `holds` + unsupplied → applied + explicit disclosure note. Malformed shapes probed at the frozen SHA: empty `{}` condition → `KeyError('op')`; unknown op → `KeyError`; non-dict condition → `AttributeError`; exception missing `id` → `KeyError`. All are hard errors that propagate uncaught (`integration.py` has no broad `except`) — fail-closed, never a silent skip, and identical to base behavior. One residual silent-skip shape exists (LOW-1 below) but is pre-existing, schema-permitted, and unused by any committed rule.

**2. Legal-safety direction — PASS.** The change is strictly monotone in `most_severe` severity: the only behavioral delta is skip→PRR (severity 4 > verified 0 / conditional 1); the downgrade accumulator is only ever raised; the final composition `most_severe(base_coverage, exc_downgrade, geom_downgrade)` is untouched, and `data_conflict` (5) still dominates (confirmed by `test_df6_as4_geometric_uncertainty_still_composes`). No existing PRR path is weakened. `exceptions_applied` membership is bit-identical to base in every case: indeterminate exceptions are not added (previously they were skipped, also not added), and holds-true exceptions were added before and still are — so no report can newly claim an exception applied that did not, or vice versa. Applying on an unsupported basis (the `not`-wrapped case) can only downgrade coverage (effects enum is PRR/conditional_alternative/documented_limitation) and now carries an explicit disclosure note instead of silence.

**3. Information integrity of notes — PASS.** Both new note strings interpolate only the exception `id` and the sorted list of unsupplied input NAMES. No input values, no user data, no filesystem paths, no internals leak. `sorted()` is applied in `_unsupplied_predicate_inputs` and that one list feeds both notes; probe confirmed byte-identical notes across runs; `test_df6_as5_indeterminate_trace_is_strict_json_and_deterministic` and `..._notes_are_plain_strings` guard it.

**4. Contract integrity — PASS.** Both `rule_evaluation.schema.json` copies are blob-identical to base at the frozen SHA (same git blob ID at both commits, both paths) and byte-identical to each other (same sha256). No new response fields: `test_df6_as5_escalated_trace_introduces_no_new_contract_key` compares the exported escalated trace's key set against the `additionalProperties: false` property set of BOTH the engine schema and the canonical contract's `$defs.evaluation_trace`, and `..._exceptions_applied_entries_keep_exactly_three_keys` pins the entry shape. The pre-existing byte-identity guard `tests/contracts/test_rule_evaluation_contract.py::test_runtime_bundle_copy_is_byte_identical_to_canonical` (line 217) still guards copy drift and ran green in the producer's full-suite run (1066 passed).

**5. Supply chain / hygiene — PASS.** No dependency manifest, lockfile, or config touched (4-file diff). No dynamic execution, no network, no subprocess, no secrets, no PII, no machine paths in the diff or the producer report (report explicitly redacts the Windows user prefix; pattern scan returned zero hits). Containment: all 4 diff paths inside `allowed_paths`; no forbidden path touched.

**6. Determinism — PASS.** The only set operation feeding output is sorted before use; exception iteration is list-ordered over `rule.exceptions`; repeated-evaluation probe and the strict-JSON determinism test both confirm identical output for identical input.

**7. Test run — PASS.** `python -m pytest tests/rules -q` in the frozen worktree: **328 passed** (exactly the expected count; 0 failed, 0 skipped).

Cross-tenant isolation, service-role secrecy, private storage, SSRF, upload controls, prompt-injection defenses, log redaction: **N/A to this diff** — it is a pure in-process deterministic-engine change with no I/O, no auth/storage/network surface, no AI call, and no logging added; nothing in the diff touches those controls.

## Regression/security/provenance findings (severity-ranked)

- **Critical: none. High: none. Medium: none.**
- **LOW-1 (pre-existing, not a regression of this change):** a leaf predicate with `op` but no `input` key (e.g. `{"op": "equals", "value": true}`) passes JSON-schema validation (predicate `$defs` has no `required`), passes `_check_predicate_refs` (which only checks declaredness when `input` is present), evaluates `equals(None, ...)` → `False`, and silently skips with no unsupplied detection — reproduced by probe: `_apply_exceptions` returned `(None, [], [])`. Reproduction: `python -c` probe in "Steps independently executed" item 5, edge B. Mitigations in place: no committed ruleset contains this shape (independent scan of all 7 rule files: clean), rule authoring is G6-gated, and behavior is byte-identical at the base SHA. Remediation (follow-up task, non-blocking): require `input` on leaf predicates in `rule_definition.schema.json` `$defs/predicate` and/or reject op-without-input at DSL load in `_check_predicate_refs`.
- **LOW-2 (pre-existing):** the predicate `$defs` also permits `{}` and junk keys (`additionalProperties` unset), so a malformed condition fails only at evaluation time as a raw `KeyError`/`AttributeError` rather than a typed load-time `DSLError`. The failure direction is safe (hard error, propagates, no silent skip); load-time rejection would be cleaner. Same follow-up task.
- **INFO-1:** an `exists`-op exception condition on an unsupplied input now escalates to PRR even though absence is determinately known — over-escalation only (legally safe direction); zero current usage (`grep` of rulesets: no `exists` op anywhere); already flagged in producer report §10.3.
- **INFO-2:** the producer's disclosed deviation (holds-true-with-unsupplied case applies + discloses instead of blanket PRR) is fail-closed-or-equal to base in every reachable case — I independently verified the load-bearing claim that an applied exception can only downgrade coverage. Whether DF-6's remit demanded blanket semantics is a scope ruling for G3/the orchestrator, not a security defect. The stale `r5_height.rule.json:71` limitations sentence (producer §9) is a disclosure-accuracy issue in a legal artifact and correctly deferred to a qualified-reviewer follow-up rather than edited by the producer — that restraint is itself the safe behavior.

## Defects

None blocking. LOW-1/LOW-2 are pre-existing hardening gaps recorded for a follow-up task, not defects introduced or reachable through committed rules at this SHA.

## Required rework

None for this task. Recommended (non-blocking, new follow-up task): tighten `$defs/predicate` (require `input` on leaves; consider `additionalProperties: false`) plus the corresponding `_check_predicate_refs` load-time rejection; and the already-producer-recommended qualified-reviewer correction of the stale `r5_height.rule.json` limitations sentence.

## Reviewer conclusion

The change is a genuine fail-closed hardening: every path where an exception condition reads an unsupplied input now either escalates to professional_review_required with a deterministic, name-only note, applies with an explicit disclosure, or hard-errors — no silent-skip path survives for any well-formed or committed rule shape, coverage severity is provably monotone versus base, both contract schema copies are blob-identical to base, the diff is fully contained, hygienic, and dependency-free, and the required 328-test evidence reproduces exactly.

VERDICT: PASS — DF-6's fail-open is closed strictly in the escalation-only direction with byte-unchanged contracts, deterministic value-free notes, and full reproduction at the frozen SHA; the two LOW findings are pre-existing, unreachable through committed rules, and routed to a non-blocking follow-up.
