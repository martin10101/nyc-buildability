# M0-T141 producer report — Draft-7 provider-schema compatibility hotfix (D-024 Am. 44)

Producer: orchestrator (main session), 2026-09-02. Scope: exactly the packet's
allowed paths. No push, no merge, no provider call (R679). Frozen corrected candidate:
**`2245de74232947be919b555fd061ba8a6e6438de`** (commit tree `63119a9a`, subtree
`edf026b3`); `git diff 2245de74..HEAD -- tools/agent_supervisor` is EMPTY at every
subsequent control-plane commit.

## s1. What changed (production)

- **NEW `tools/agent_supervisor/mrl_provider_schema.py`** (R667–R670):
  `provider_schema_for_claude_cli()` deep-copies the canonical schema, pops the
  top-level `$schema`, refuses any dialect other than the canonical 2020-12 or
  Draft-7 URI, walks EVERY keyword against a same-meaning-in-both-drafts allowlist
  (recursing through `properties`/`patternProperties`/`items`(schema-form)/
  `additionalProperties`/`propertyNames`/`contains`/`not`/`if`/`then`/`else`/
  `allOf`/`anyOf`/`oneOf`; boolean subschemas pass), and returns a NEW dict whose
  only difference from the canonical content is the explicit
  `http://json-schema.org/draft-07/schema#` declaration. Refusal classes (all
  `ContractError("draft7_schema_incompatible", ...)`): newer-draft-only keywords
  (`$defs`, `prefixItems`, `unevaluated*`, `dependent*`, `min/maxContains`,
  `$anchor`/`$dynamic*`/`$recursive*`/`$vocabulary`, `contentSchema`, `deprecated`),
  draft-divergent keywords (`$ref`, `definitions`, `dependencies`, array-form
  `items`), nested `$schema`, unknown keywords, non-object subschemas. Nothing is
  silently translated or dropped (R669).
- **`tools/agent_supervisor/mrl_one_shot.py`**: the single `--json-schema` call site
  serializes the projection instead of the canonical schema. A projection failure
  raises inside the existing pre-launch `try` → typed refusal
  (`checkpoint_error`, no checkpoint) BEFORE any provider contact. No other change.
- Canonical contract untouched (R666): `schemas/worker_result.schema.json` and
  `mrl_worker_result.py` byte-identical (forbidden paths; `git diff` empty).

## s2. Focused tests (R671)

`tools/test_agent_supervisor_mrl_provider_schema.py` (new) +
`tools/test_agent_supervisor_mrl_one_shot.py` (argv assertions updated): **89 passed**.
The five directed proofs:

1. canonical unchanged — deep-copy proof mutates the projection
   (`enum.append`, `required.append`, `title`) and re-asserts the canonical equals
   its pre-call snapshot AND a fresh disk load;
2. provider copy declares Draft 7 and the body is otherwise identical;
3. the serialized CLI argument (the runner's exact expression, and the launched argv
   via the fake-popen harness) parses to a draft-07 dict and contains no
   `json-schema.org/draft/2020-12` substring;
4. 15 parametrized incompatible inputs refuse with `draft7_schema_incompatible`
   (newer-only, divergent, nested, unknown, array-items, bad dialect, non-object) and
   a refusal never mutates its input; 5 nested-position cases prove the walk recurses;
5. guard-removed proof: the pre-fix expression
   (`json.dumps(load_schema(...), sort_keys=True)`) emits the URI byte-equal to the
   one in the preserved stderr
   (`"https://json-schema.org/draft/2020-12/schema"`), so the same exact error would
   return with the guard removed; the fixed expression no longer emits it.

## s3. Mutation proof (R676; AS-DS-6)

| Mutant | Change | Result |
|---|---|---|
| M1 | call site reverted to serializing the canonical schema | **DETECTED** — argv test fails with the 2020-12-vs-draft-07 diff (red run captured in-session) |
| M2 | projection returns `declared or DRAFT7_DECLARATION` (keeps 2020-12) | **DETECTED** (1 failed) |
| M3 | unknown keywords `continue` instead of refuse | **DETECTED** (1 failed) |
| M4 | `_REFUSED` table ignored (`continue`) | **DETECTED** (1 failed) |
| M5 | `dict(schema)` shallow copy instead of `deepcopy` | **DETECTED** (1 failed) |
| M6 | array-form `items` accepted | **DETECTED** (1 failed) |

Module restored byte-identical after each mutant; final re-run 89 passed.

## s4. Regression, lint, modularity, governance (R676)

- Full supervisor suite (freeze §4 baseline re-established at the frozen identity):
  **3566 passed, 2 skipped, 0 failed** (raw exit 0).
- `ruff check` on the four changed Python files: clean.
- `python tools/modularity_check.py --check`: 0 failures (new module is focused;
  call-site change is one expression).
- `python tools/validate_directive_compliance.py --check`: exit 0.
- controller_update ps harness: **7/7 PASS** (includes `test_runbook_parse.ps1`
  asserting binding/runbook/pinnedSha SHA agreement at the NEW candidate, PS 5.1
  parse of the operator script and every runbook block, and the R624/R632/R636
  teeth). Supervisor ps harness: 3/3 PASS.

## s5. Freeze + immutable source binding (R678)

`project-control/reports/M0-T141-freeze.md` records the frozen corrected candidate
(commit/tree/subtree). `tools/controller_update/source_binding.json` rebinds
`commit_sha`/`commit_tree_sha`/`subtree_tree_sha` to it and adds the two changed
modules to `required_modules`; runbook §4 and the ps_test `$pinnedSha` carry the same
SHA. The superseded candidate `1489879e` remains recorded for provenance.

## s6. Preserved failed-run evidence (R672; R665)

`project-control/reports/M0-T141-canary-b502-schema-failure-evidence.md`: verbatim
stderr, `one_shot_unit.json` fields proving **provider-contact count zero** (empty
`session_id`, empty `observed_models`, `processes_total` 1, exit 1), audit records
17–26 including the REUSABLE b5-01 PASS at record 17 (`launch_manifest_refused`
naming `clean_status`), and the current PAUSED_RECOVERY journal state with the
canonical §9a exit. Runtime state was only READ; run dirs `canary-b5-01`/`canary-b5-02`
preserved as-is (the successor run uses a new correlated run id — R673, executed under
M0-T140 after acceptance).

## s7. Follow-ups (none blocking review)

- The owner-run continuation script (R680/R681) is generated AFTER acceptance under
  M0-T140 — deliberately not part of this task's reviewed content.
- M0-T137 / R603–R605 remain owner-only, untouched, uninterpreted (R674).
- Live CLI acceptance of the Draft-7 argument is provable only by the owner-typed
  b5-02 successor canary (same R579 boundary as before); the offline proofs bound
  every controller-side behavior.

Self-verdict: ready for independent G3/G4/DCV at the submitted head. The producer
does not accept its own work (R677).
