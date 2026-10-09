# M0-T141 G3 code review (independent code-reviewer, 2026-09-02)

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel
(transport entity-decoding only; report-preservation rule 2026-07-16). Reviewer:
foreground read-only `code-reviewer` subagent; producer = orchestrator (identities
differ, D-024-R677).

---

I have completed my independent verification. All checks pass by direct evidence. Let me compile the gate report.

## G3 GATE REPORT — Task M0-T141 (Draft-7 provider-schema compatibility hotfix)

**Reviewer role:** independent code-reviewer (G3), read-only
**Reviewed head:** `71f0e063275ccc3a0e5deb3308af69a64d8bd086` on `candidate/D-024-mrl-option-b` (confirmed HEAD, clean tree)
**Frozen code commit under binding:** `2245de74232947be919b555fd061ba8a6e6438de`

### VERDICT: PASS

---

### Findings

**1. MINOR (informational) — forward-looking fail-closed brittleness.** `tools/agent_supervisor/mrl_provider_schema.py:63-83, 100-124`. The projection is a *positive* allowlist with an else-default refuse, and `$ref`/`$defs`/`definitions` are all refused. This is correct per R669 (fail closed, never silently translate). Consequence to record: if the canonical `worker_result.schema.json` is ever refactored to share sub-definitions via `$ref`/`$defs` — an ordinary schema evolution — the projection will raise `ContractError` on *every* launch and the supervisor will refuse at the CLI boundary until a new hotfix teaches the walk to inline/translate refs. This is the intended posture (fail-closed beats a different-meaning schema), not a defect, but a future schema editor should expect it. Not blocking.

**2. MINOR (informational) — `format` assertion-vs-annotation nuance.** `mrl_provider_schema.py:51` (`format` in `_SAME_MEANING`). The keyword name is shared by Draft 7 and 2020-12, so the structural walk handles it correctly, but a Draft-7 CLI validator may treat `format` as an *assertion* while 2020-12 treats it as annotation-by-default. The current canonical contract uses no `format` keyword, so nothing is exercised today; noted only so that a future `format` addition is understood to potentially validate more strictly on the provider copy than the canonical enforcer. Not a silent structural mishandling.

No BLOCKING findings.

---

### What I verified by direct evidence (not producer claims)

- **HEAD/tree:** `git rev-parse HEAD` = `71f0e063…`, `git status --porcelain` empty.
- **Canonical contract untouched (R666, Q4):** `git diff 2245de74^ 71f0e063 -- tools/agent_supervisor/schemas/ tools/agent_supervisor/mrl_worker_result.py` is **empty**. Also confirmed empty for the other forbidden paths (`model_selection.py`, `M0-T136-canary-package.md`).
- **Keyword allowlist soundness (Q1):** Read the full walk. `_SAME_MEANING` contains only data/scalar keywords (none carry subschemas), all valid and same-meaning in Draft 7 (incl. `if/then/else`, `const`, `contains`, `propertyNames` which are Draft 6/7 additions — correctly allowed, not mistaken for newer-only). `enum/const/default/examples` are correctly treated as data and never recursed. Every newer-only/divergent subschema-bearing 2020-12 keyword (`prefixItems`, `dependentSchemas`, `$defs`, `unevaluatedItems/Properties`, `dependencies`, `$ref`, `definitions`) is refused, and any keyword not explicitly allowed hits the `else` → `_refuse` default, so `_REFUSED` completeness is not safety-critical (it only improves messages). `items` array-form (tuple) is refused; schema-form is walked — correct for a 2020-12→Draft-7 projection. Nested `$schema` is refused (line 100-101); top-level `$schema` is popped/validated before the walk (line 141-143). **I could not identify any keyword the walk silently mishandles.**
- **Recursion completeness (Q2):** Confirmed every allowed subschema-hiding position is walked — `properties`/`patternProperties` (map), `items` (schema form), `additionalProperties`/`propertyNames`/`contains`/`not`/`if`/`then`/`else` (single), `allOf`/`anyOf`/`oneOf` (list). Boolean subschemas short-circuit correctly. No hole for the allowed set.
- **Canonical never mutated + fail-closed call site (Q3):** `copy.deepcopy(dict(schema))` precedes any `pop`/write (line 140); `_walk` is read-only. The single call site (`mrl_one_shot.py:257-266`) is inside the pre-launch `try`; a `ContractError` is caught at line 268 and returns a typed `self._refuse(argv, …)` (argv pre-initialized line 222); `run_one_shot` / provider contact is at line 287, **after** the try. A projection failure therefore never contacts the provider.
- **Scope (Q5):** All production/test/doc/binding edits are within `allowed_paths`; the only out-of-`allowed_paths` changes are orchestrator-written control-plane files (`state.json`, `gates/`, `tasks/M0-T141.json`, `reports/M0-T141.json`), which is the authorized pattern.
- **Freeze rebind consistency (Q6):** `git rev-parse 2245de74^{tree}` = `63119a9a…` and `2245de74:tools/agent_supervisor` = `edf026b3…` both match `source_binding.json`, runbook §4, and `test_runbook_parse.ps1 $pinnedSha` (all pin `2245de74…`). `required_modules` now includes both `mrl_provider_schema.py` and `mrl_one_shot.py`. Supervisor subtree is byte-stable from `2245de74` to reviewed HEAD (`git diff 2245de74 71f0e063 -- tools/agent_supervisor/` empty), so the binding is consistent with the reviewed head.
- **Evidence-citation duty (supervisor-freeze §3, Q8):** Commit `2245de74` message cites "Reproduced defect + provider CLI drift (supervisor-freeze AD-093 qualifying evidence, D-024 Amendment 44)" and requirement IDs `D-024-R664..R683`; the task packet objective cites the same. Satisfied.
- **Tests / regression:** Focused files `tools/test_agent_supervisor_mrl_provider_schema.py` + `tools/test_agent_supervisor_mrl_one_shot.py` = **89 passed**. Full supervisor suite `python -m pytest tools/test_agent_supervisor*.py` = **3566 passed, 2 skipped, 0 failed** (354.7s) — matches the freeze §4 baseline claim exactly and confirms no regression from the two-module change. `python tools/modularity_check.py --check` = **0 failures** (the two changed modules are not among the pre-existing warnings). The tests are genuine (not tautological): they assert absolute `$schema`==draft-07, absence of the 2020-12 substring in the serialized argv, a deep-copy tamper proof that mutates nested `properties…enum`, 15 refusal cases, 5 nested-recursion cases, and tie the guard-removed serialization to the preserved stderr URI. I confirmed by reasoning that each documented mutant M1-M6 would be caught by these assertions.

**Summary:** The hotfix is a correct, well-bounded, fail-closed Draft-2020-12→Draft-7 projection at the single `--json-schema` CLI boundary. The canonical contract and controller-side enforcer are provably untouched; the deep copy precedes any mutation; the walk covers every subschema position for the allowed keyword set and refuses everything else by default; the call-site failure path is typed and pre-provider-contact; the freeze rebind's three SHA carriers agree and include both changed modules; qualifying evidence and D-024 IDs are cited in both packet and commit; and the full 3566-test supervisor baseline plus 89 focused tests are green with 0 modularity failures. I recommend **PASS**.

---

*Orchestrator disposition of findings (recorded 2026-09-02): Finding 1 — accepted advisory; the fail-closed posture on future `$ref`/`$defs` schema evolution is the intended design (R669); queued as a documented expectation for any future canonical-schema editor. Finding 2 — accepted advisory; `format` is unused by the canonical contract today; queued follow-up: consider guarding `format`/`content*` value shapes if a future schema adds them. Neither requires a change within this bounded scope.*
