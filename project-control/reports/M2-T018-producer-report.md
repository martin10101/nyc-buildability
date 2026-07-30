# M2-T018 — Producer Report

**Task:** M2-T018 — Wire the M2-T017 allowlist serializer into the property-profile builder
(fail-closed provenance write boundary).
**Role:** Producer. No ledger writes, no `git add/commit/push`, no `gh`, no
`tools/project_control.py` — the orchestrator integrates (ADR-005).
**Directive:** D-004 (regime v1.0; `D-004:ALL`). D-003 second-wave lane 2 (D-003-R023).

---

## 0. Worktree attestation (D-004-R302) — READ THIS FIRST

**A harness deviation occurred. It is disclosed here in full; the orchestrator must decide whether
to accept the delivery location.**

### 0.1 Expected values and what the attestation command returned

The attestation command was run as instructed. The agent harness had already placed this producer
session in its OWN isolated worktree and refused the `cd <M2-T018 worktree> && git …` form:

```
This agent is isolated in the worktree .claude/worktrees/agent-<id>, but this command changes
directory to the shared checkout (.claude/worktrees/M2-T018-serializer-wiring) before running git.
Refusing to run it - a worktree-isolated agent's git operations must target its own worktree.
```

The same guard blocks the `Edit`/`Write` tools against any path under
`.claude/worktrees/M2-T018-serializer-wiring/`:

```
This agent is isolated in the worktree .claude/worktrees/agent-<id>. Edit the worktree copy of this
file instead of the shared-checkout path.
```

The guard was NOT circumvented (a raw filesystem write through Bash was technically possible and was
deliberately not used for any deliverable).

### 0.2 The four attestation values for the ASSIGNED worktree

Obtained from the shared git metadata via the producer's own worktree (`git worktree list
--porcelain`, `git rev-parse task/M2-T018-serializer-wiring`), which is authoritative for another
worktree's checkout state:

| Value | Expected | Observed | Match |
|---|---|---|---|
| worktree path | `.claude/worktrees/M2-T018-serializer-wiring` | `.claude/worktrees/M2-T018-serializer-wiring` | YES |
| toplevel | same as above | same as above | YES |
| branch | `task/M2-T018-serializer-wiring` | `refs/heads/task/M2-T018-serializer-wiring` | YES |
| HEAD | `84c1bf29243bb862d344c909099c9bd9a3f6a766` | `84c1bf29243bb862d344c909099c9bd9a3f6a766` | YES |

That worktree is clean and untouched by this session.

### 0.3 The four values for the worktree the work was actually done in

```
pwd                      .claude/worktrees/agent-<id>
git rev-parse --show-toplevel   .claude/worktrees/agent-<id>
git branch --show-current       worktree-agent-<id>
git rev-parse HEAD              84c1bf29243bb862d344c909099c9bd9a3f6a766
```

**Base SHA is identical to `EXPECTED_BASE_SHA`.** Before writing anything, all ten files in scope
were SHA-256 compared across the two worktrees and were byte-identical, so the diff produced here
applies cleanly onto `task/M2-T018-serializer-wiring`:

```
OK  services/api/app/profile/builder.py                          2 x fcb1c6ce58f40cd7
OK  services/api/app/profile/wave_integration.py                 2 x 0ad4e013f1685ce8
OK  services/api/app/profile/zoning_crosscheck.py                2 x 62b7476cfe22f879
OK  services/api/app/contracts/serializers.py                    2 x 590169125c6ffec5
OK  services/api/app/contracts/__init__.py                       2 x 13ff7e1c8cfdcff6
OK  services/api/tests/contracts/test_contract_serializers.py    2 x dc9d97d8731ec7b6
OK  packages/contracts/schemas/v1/source_fact.schema.json        2 x 2577d2aabe6fb9c4
OK  services/api/app/_contract_schemas/v1/source_fact.schema.json 2 x 2577d2aabe6fb9c4
OK  packages/contracts/generated/property_profile.ts             2 x 64e3d9bd883e68b3
OK  project-control/tasks/M2-T018.json                           2 x db13da940c65ba4d
ALL_IDENTICAL True
```

**Orchestrator action required:** integrate from the producer worktree's branch
(`worktree-agent-<id>`, base `84c1bf2`) rather than from `task/M2-T018-serializer-wiring`, or
transplant the diff onto the task branch. The producer cannot do either (no git authority).

---

## 1. Outcome

`app/profile/builder.py` now has ONE fail-closed provenance write boundary, `_closed_provenance`,
through which every `source_fact` record enters the profile `provenance` array. An undocumented key
raises `ContractSerializationError` and the build fails; the record is never silently dropped and no
partial profile is returned. Both API routes turn that into a typed 500 with a correlation id and no
internals, proven at the wire (not merely asserted). The import tripwire now pins the single intended
boundary instead of asserting the serializer is unwired. Full `services/api` suite: **1048 passed, 0
failed**; ruff clean; all three CI drift checks rc=0.

## 2. Key finding — packet item 2 was ALREADY satisfied by M2-T017 (no schema change was needed)

The packet directs handling the connector lineage keys "by DOCUMENTED extension of the serializer
allowlist and the source_fact schema (BOTH copies …), regenerating `property_profile.ts` if the
generator output changes". **That extension already exists**; M2-T017 performed it when it closed the
contract. Rather than assume, this was verified three ways:

1. **Every `source_fact` dict literal in `app/**` was enumerated by AST** (not by grep), and its key
   set compared to the serializer allowlist:

   | Producer | Keys emitted | Outside the allowlist |
   |---|---|---|
   | `app/connectors/pluto_soda.py` | 20 (incl. `dataset_id`, `request_url`, `input_vintages`) | **none** |
   | `app/connectors/ztldb_soda.py` | 20 (incl. `dataset_id`, `request_url`, `source_rows_updated_at`) | **none** |
   | `app/profile/wave_integration.py` (zoning-features ArcGIS, MapPLUTO geometry ArcGIS, spatial intersection) | 12 (required set only) | **none** |

2. **Both schema copies are already byte-identical** and already document all four lineage keys:
   canonical and bundled `source_fact.schema.json` are 11876 bytes, SHA-256
   `2577d2aabe6fb9c4732dd43eeda815630fd0b804dd345366b96c4b94e5380540`.
3. **The generator confirms no drift**: `generate_ts_types.py --check` and
   `sync_contract_schemas.py --check` both rc=0 *after* the wiring.

**Consequence:** the correct action for item 2 was to change nothing and prove it, not to
manufacture a schema edit. `packages/contracts/schemas/v1/source_fact.schema.json`,
`services/api/app/_contract_schemas/v1/source_fact.schema.json` and
`packages/contracts/generated/property_profile.ts` are therefore **unmodified** — they are in
`allowed_paths` (a permission, not an obligation) and editing them would have been an unjustified
change to accepted contract artifacts. The empirical proof that no bypass is hiding here is that the
entire 1048-test suite passes with the serializer wired: had any connector emitted an undocumented
key, every profile build would fail closed.

## 3. Design decisions

**D1 — One boundary function, applied at both splice points.** `builder.py` splices provenance in
exactly two places (the initial array literal; the later `extend` of the wave feed). Both now call
`_closed_provenance`. A single trailing "normalize the whole array once" pass was rejected because it
would leave the array transiently holding unvalidated records and would weaken the invariant
"everything in `provenance` has crossed the boundary" to "everything has crossed it *by the end*".

**D2 — Fail closed, never drop.** On rejection the whole build raises. Dropping the offending record
was rejected outright: it would yield a profile whose provenance is quietly incomplete, which PRD
sections 9/19 forbid just as firmly as an undocumented key.

**D3 — Let `ContractSerializationError` propagate unwrapped.** It is not re-wrapped into
`app.profile.contract.ContractValidationError`. Reason: in BOTH routes `build_property_profile` is
called *outside* the inner `try` that maps `ContractValidationError`
(`app/api/v1/properties.py:393` vs the inner try at 399-404; `rule_evaluation.py:226` vs 231-233), so
wrapping would reach the same generic handler while *losing* the precise exception type name that the
handler logs (`type=UnknownFieldError` is strictly more useful than `type=ContractValidationError`).
Both routes are forbidden paths, so widening their inner `try` was not an option. The outcome is
still fail-closed and typed: verified at the wire in §5.4.

**D4 — No exception notes / no record context in the error.** Adding the array index or the record's
`provenance_id` to the message was considered and rejected: the route logs only
`type(exc).__name__` and never `str(exc)` (M1-T002 G5 F5 payload-only logging policy), so the extra
context could never reach production logs, while any content added to an error message is a standing
leak risk. The serializer's own key-names-only discipline is preserved end to end.

**D5 — `zoning_crosscheck.py` needed no functional change.** The packet lists it as a feed that
"splices into" provenance. It does not: it emits only conflict entries and note strings, and merely
quotes a `provenance_id` inside a conflict `derivation` string. The ZTLDB facts that accompany a
cross-check reach the profile through the connector's own `result.facts` passed as
`additional_provenance`, which crosses the boundary. A docstring paragraph records this so the next
reader does not re-derive it.

**D6 — Tripwire renamed, not deleted.** See §4 and §6.

## 4. Changed files (all inside `allowed_paths`; no forbidden path touched)

```
 M services/api/app/profile/builder.py                          |  85 +++++++++-
 M services/api/app/profile/wave_integration.py                 |   9 ++
 M services/api/app/profile/zoning_crosscheck.py                |  12 ++
 M services/api/tests/contracts/test_contract_serializers.py    | 143 ++++++++++++----
?? services/api/tests/profile/test_provenance_write_boundary.py |  398 (new)
?? services/api/tests/api/test_provenance_boundary_api.py       |  116 (new)
```

| File | Rationale |
|---|---|
| `app/profile/builder.py` | Adds `from app.contracts.serializers import SOURCE_FACT_SERIALIZER`, the `_closed_provenance` boundary function, and its use at the two splice points; documents the boundary in the module docstring and adds a `Raises:` section to `build_property_profile`. Functional change is 4 lines; the rest is the contract documentation a legally-sensitive boundary needs. |
| `app/profile/wave_integration.py` | Docstring only. Records that `build_wave_sections`' provenance records are routed through the builder's boundary and that `_source_fact` may therefore emit only documented keys. No code change. |
| `app/profile/zoning_crosscheck.py` | Docstring only. Records *why* this module is unchanged (D5) and the rule for any future `source_fact` emission here. No code change. |
| `tests/contracts/test_contract_serializers.py` | Tripwire amended (§6). Module docstring updated to state that M2-T018 retired the "unwired" premise. All eleven M2-T017 serializer unit tests are untouched. |
| `tests/profile/test_provenance_write_boundary.py` (new) | 13 tests: AS-1 fail-closed in all three feeds, AS-2 all four real connectors from recorded fixtures, AS-4 completeness/fidelity. |
| `tests/api/test_provenance_boundary_api.py` (new) | 3 tests: the wire contract — typed 500, never a 200, no key/value leak. |

**Not modified (deliberately):** `app/contracts/serializers.py`, `app/contracts/__init__.py`,
`app/profile/contract.py`, `tests/contracts/test_closed_contracts.py`, both `source_fact.schema.json`
copies, `packages/contracts/generated/property_profile.ts`, `project-control/tasks/M2-T018.json`.
Reasons in §2 and §3.

## 5. Self-checks (producer; independent gates run by reviewers)

All commands were run from the producer worktree. Local `python 3.11.9`, `pytest 8.4.2`,
`jsonschema 4.26.0`; CI hash-pins `pytest 9.0.3` (`requirements-tools.lock`) — see risk R4.

### 5.1 Baseline BEFORE any change (same command, same tree)

```
services/api $ python -m pytest tests/contracts tests/profile tests/api -q
224 passed in 8.22s
```

### 5.2 After the builder wiring, BEFORE amending the tripwire — the single expected failure

```
services/api $ python -m pytest tests -q
1 failed, 1028 passed in 16.84s

FAILED tests/contracts/test_contract_serializers.py::test_serializer_not_imported_by_any_production_module
E  AssertionError: the allowlist serializer must NOT be wired into production in M2-T017;
   found import(s) in: ['services\\api\\app\\profile\\builder.py']
```

This is load-bearing evidence: across 1029 tests the *only* thing the wiring broke was the assertion
that the wiring does not exist. No connector, contract, rules, scenario, resilience or spatial test
regressed — so no undocumented key exists in production output, and nothing depends on the
connectors' original provenance key ORDER (the boundary re-emits records in canonical schema order).

### 5.3 Final state — targeted suites

```
services/api $ python -m pytest tests/contracts tests/profile tests/api -q
243 passed in 5.24s
```

(224 baseline + 19: +13 write-boundary, +3 API-wire, +4 tripwire, −1 retired tripwire.)

### 5.4 Final state — full service suite, lint

```
services/api $ python -m pytest tests -q
1048 passed in 10.94s

services/api $ python -m ruff check app tests
All checks passed!
```

### 5.5 Contract tooling suites

```
$ python -m pytest packages/contracts/scripts/tests -q
24 passed in 0.48s

$ python -m pytest .github/scripts/tests -q
24 passed, 5 warnings in 1.10s
```

### 5.6 CI-reproducible drift checks (exact CI commands)

```
$ python packages/contracts/scripts/generate_ts_types.py --check
OK: generated TypeScript types are up to date.
OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.
OK: generated rule_evaluation TypeScript types are up to date.
OK: generated scenario TypeScript types are up to date.
rc=0

$ python services/api/scripts/sync_contract_schemas.py --check
OK: runtime-bundled contract schemas are byte-identical to the canonical source.
rc=0

$ python .github/scripts/validate_contracts.py
Checked 9 schema file(s); 0 failure(s).
rc=0
```

## 6. The amended tripwire, justified line by line (AS-3)

`test_serializer_not_imported_by_any_production_module` was **renamed and replaced by four tests**.
The rename is deliberate and disclosed: the old name asserts a condition M2-T018 was contracted to
retire, so keeping it would have made a green suite claim something false.

| Change | Justification |
|---|---|
| Removed `test_serializer_not_imported_by_any_production_module` | Its premise (serializer unwired) is exactly what this task retires. Keeping it would force either a permanent skip or a lie. |
| Added `test_serializer_imported_exactly_at_the_profile_write_boundary` | The strictly stronger invariant: the importer list must equal `["services/api/app/profile/builder.py"]`. Fails if a second module imports the serializer AND fails if the builder loses the wiring — the old test only caught the first direction of one of these. |
| Added `test_no_other_production_module_even_references_the_serializer` | Keeps the old test's substring scan (which also catches `importlib.import_module("app.contracts.serializers")` and other string-based reaches), now asserting exact equality with the one boundary instead of emptiness. |
| Added `test_boundary_imports_only_the_source_fact_serializer` | Pins the narrowest dependency: the builder imports `SOURCE_FACT_SERIALIZER` only — not the package, not the error classes it does not raise itself. |
| Added `test_serializer_is_used_only_inside_the_closed_provenance_boundary` | AST check that no `SOURCE_FACT_SERIALIZER` reference exists in `builder.py` outside `_closed_provenance`, so a second call site inside the builder cannot appear unpinned. |
| Detection switched from substring-only to AST for the import check | A docstring or comment mentioning `app.contracts` is no longer mistaken for wiring. The substring scan is retained as the separate dynamic-import guard above. |
| Paths reported as repo-relative POSIX (`as_posix()`) | The old failure message rendered `services\api\...` on Windows and `services/api/...` on the Linux runner; the assertion is now platform-stable. |
| Module docstring updated | States that M2-T017's AS-4 premise was retired by M2-T018 and what the tripwire now guarantees. |

**No other existing test was modified anywhere in the repository.** The eleven M2-T017 serializer unit
tests, and every profile/API/connector/rules/scenario/resilience/spatial test, are untouched and green.

## 7. Acceptance-scenario self-assessment

| AS | Verdict | Evidence |
|---|---|---|
| **AS-1** every record passes the serializer; an undocumented key fails closed, never a silent pass or invalid 200 | MET | `tests/profile/test_provenance_write_boundary.py`: undocumented key rejected in the connector-fact feed, in `additional_provenance`, and in the wave feed (the last via monkeypatched `build_wave_sections`, proving the second call site is live); optional-field typo (`unit`) rejected; missing required field rejected; rejection message names the key and never the value; error is a `ValueError`. At the wire, `tests/api/test_provenance_boundary_api.py`: 500 `internal_error` with correlation id, `"provenance"` absent from the body, and neither `_debug_stacktrace` nor its value in the response text; the clean capture still serves 200. |
| **AS-2** four connector fixture shapes serialize via documented extension; no bypass; both schema copies byte-consistent; TS regenerated | MET (with the §2 finding) | Real connector results replayed from recorded captures: PLUTO `F01`, ZTLDB `ZT01`+`ZT08`, zoning-features ArcGIS `nylh` (meta+count+3 pages), MapPLUTO geometry `MPG01`+`MPG02`. All four `source_id`s appear in provenance; every record is a serializer no-op fixpoint; `dataset_id`/`request_url`/`input_vintages`/`source_rows_updated_at` all survive. Schema copies byte-identical (SHA in §2); `generate_ts_types --check` rc=0 → **no regeneration was needed, and none was performed** (§2). |
| **AS-3** tripwire pins the single boundary | MET | §6; four tests, all green. |
| **AS-4** provenance completeness preserved; nothing dropped or mutated | MET | Count `== len(pluto.facts) + len(ztldb.facts) + 2`; per-record key sets and values equal to the inputs; inputs not mutated; emitted records are new dicts; built profile still passes `validate_profile`. Pre-existing `test_integration_ztldb_facts_join_provenance_with_full_lineage` also still green. |
| **AS-5** existing suites pass; amended tests justified; drift checks clean | MET | §5.3–5.6: 1048 passed / 0 failed, ruff clean, three drift checks rc=0, tooling suites 24+24. One test retired and replaced, justified line by line in §6. |
| **AS-6** attestation recorded before first write; evidence returned; no git/gh/CLI writes | **MET WITH A DISCLOSED DEVIATION** | §0. All four expected values verified for the assigned worktree; base SHA identical; scope files byte-identical. The work was produced in the harness-assigned isolated worktree because the harness refuses both `git` and `Edit`/`Write` against the assigned one. No `git add/commit/push`, no `gh`, no `tools/project_control.py` was run. |

## 8. Contract / interface impact

- No canonical schema changed; no generated artifact changed; no contract version bumped.
- `build_property_profile` gains a documented failure mode: `ContractSerializationError` when a
  provenance record is undocumented or incomplete. Callers that previously could only see
  `ValueError` (bad status / missing digest) still see a `ValueError` subclass, so no caller signature
  or handler needs to change.
- Observable payload change: provenance records are emitted in canonical schema key ORDER rather than
  connector emission order. Values, key sets and JSON semantics are unchanged; no digest in the system
  is computed over the provenance array (`response_digest` covers the source response), and the full
  suite confirms nothing depended on the old order.

## 9. Residual risks and limitations

- **R1 (governance, needs orchestrator attention).** `project-control/directives/D-002-…/verification.json`
  records requirement **D-002-R038** as verified by the evidence *"git grep app.contracts.serializers
  finds no import in app/main.py, app/api/**, app/profile/builder.py; regression test
  test_serializer_not_imported_by_any_production_module"*. M2-T018 deliberately retires both halves of
  that evidence statement. An independent verifier re-running it against post-merge `main` will find
  the builder import. The registry is append-only and orchestrator-owned, and is outside this task's
  `allowed_paths`, so nothing was touched — but the supersession should be recorded so the historical
  D-002 evidence is not later read as a regression.
- **R2.** Key-level enforcement only. Value-level validation stays with the JSON-schema layer
  (`validate_profile`), unchanged. A documented key holding a wrong-typed value is caught there, not here.
- **R3.** The boundary is enforced in `builder.py`. A future component that assembles a profile without
  going through `build_property_profile` would not inherit it. The tripwire detects a second
  *serializer* import but cannot detect a component that never serializes at all; the practical guard is
  that `validate_profile` still rejects such a payload before send.
- **R4.** Local `pytest 8.4.2` vs CI's hash-pinned `9.0.3`; local `jsonschema 4.26`. No version-specific
  API is used by the new tests (plain `pytest.raises`, `monkeypatch`, `TestClient`), but CI is the
  authoritative run.
- **R5.** The MapPLUTO fixture lot (`1008350041`) differs from the PLUTO/ZTLDB lot (`1000010100`) in the
  combined AS-2 build. That composition is SYNTHETIC and is labeled as such in the test docstring; it
  exercises record SHAPE only and is never presented as a co-observation of one property.
- **R6 (delivery).** See §0: the diff lives on the producer's isolated worktree branch at base
  `84c1bf2`, not on `task/M2-T018-serializer-wiring`. Integration requires an orchestrator decision.

**Producer status:** submitted for independent gates (G0/G2/G3/G5) and orchestrator acceptance.
Requested status: `awaiting_gate`.
