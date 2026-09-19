# M5-T048 producer report — proposal scenario contract (phase B0, D-076)

Scope: give the scenario contract an OPTIONAL `proposed_massing` INPUT CLASS (contract 1.1.0),
a focused server-side validator with typed refusals + DB-013 ceilings, and valid/invalid
fixtures. NO evaluation/derivation change (that is B1/B2). Directives bound: D-066-R001,
D-076-R001/R002/R003.

## Verification pass (2026-09-19, orchestrator-directed evidence unit)

DOCUMENTATION/EVIDENCE ONLY — no schema, validator, fixture, or test change this pass; every
documented command was run and all pass, so no code fix was justified. `project-control/tasks/M5-T048.json`
was NOT touched; AS-3 wording reconciliation stays routed to the orchestrator.

### All six documented commands run at HEAD 819c116a — actual cwd + outcomes (VERIFIED)

From the `services/api` cwd (the api CI job's cwd):
- `python -m ruff check .` → **All checks passed!**
- `python -m pytest tests/scenario -q` → **527 passed**
- `python -m pytest tests/api -q` → **439 passed**

From the repo (worktree) root:
- `python packages/contracts/scripts/generate_ts_types.py --check` → **OK** (scenario TS byte-identical)
- `python -m pytest packages/contracts/scripts/tests -q` → **29 passed**
- `python tools/modularity_check.py --check` → **447 files; failures 0** (proposal.py not on the warning list)

This closes the prior "services/api-cwd checks NOT executed" limitation: the three api-cwd checks were
run from `services/api` with the real outcomes above. AS-8 CI on the pushed head is the final
independent confirmation of ruff + both pytest suites (orchestrator captures).

### Independent raw-byte schema equality (INDEPENDENT of the in-test read_bytes() assertion)

An independent read-only verifier (ci-evidence-verifier, this unit) computed, outside pytest, on the
two copies A = `packages/contracts/schemas/v1/scenario.schema.json` and
B = `services/api/app/_contract_schemas/v1/scenario.schema.json`:
- RAW on-disk sha256 (NO normalization): A = B = `271653ab3b8d5c2e2e3c3a3b6a9b9a947f6d2ef33a71b89ebcdd2d1227a5def8`
- `cmp A B` → exit 0 (byte-for-byte identical); size 33486 bytes each; 543 CR bytes each (CRLF on disk)
- LF-normalized sha256: A = B = `dc41be0e356ca76b1617cbdeb1439d2d400d9e583f02afea4729ae95337ce4b9`
- **RAW-byte identical: YES. LF-normalized identical: YES.**

Raw-byte (not merely LF-normalized) identity is proven — satisfying "LF-normalized equality alone does
not prove byte identity" — and confirms `test_runtime_bundle_copy_is_byte_identical_to_canonical`
independently.

### Digest-bound per-file record (LF-normalized sha256, verifier-computed at pre-edit HEAD)

| File | sha256 (LF-normalized) |
|---|---|
| packages/contracts/schemas/v1/scenario.schema.json | dc41be0e356ca76b1617cbdeb1439d2d400d9e583f02afea4729ae95337ce4b9 |
| services/api/app/_contract_schemas/v1/scenario.schema.json | dc41be0e356ca76b1617cbdeb1439d2d400d9e583f02afea4729ae95337ce4b9 |
| packages/contracts/generated/scenario.ts | 230392c45ae01850563e62c0b039c8e1b7acb08ec07463bc6822589d83cc92c5 |
| services/api/app/scenario/contract.py | 4649edf0bf2915c68042bba06b73e8532c7c7df02aff04e73bbbdaf916f8c76c |
| services/api/app/scenario/proposal.py | 8feded0224e7729392bc3bf0427e2c7cf7fc636cb619349edd49e462a0507e4e |
| services/api/tests/scenario/test_scenario_contract.py | 8d40ad75469621a72b919801f11329e29016332a75d3c3df3332edac9e045b6a |
| services/api/tests/scenario/test_scenario_proposal.py | 059ceac956b1766fb66f27970d1777a37d3e3ea21c8b315e749d254a976ca70e |
| project-control/reports/M5-T048-producer-report.md | c859e69db36cec198b2b20676ec7fb79500f7bd6c278e9e380f3c627ca7c8d84 (SUPERSEDED by this revision) |
| packages/contracts/fixtures/valid/scenario/proposed_massing_preliminary.json | c3adec5313d40250455685b28463d0d85688517b61f2a61b6b9e67459a38ce87 |
| packages/contracts/fixtures/valid/scenario/proposed_massing_multilevel.json | c4a0c735cce39c70c0f335c441874385b6c4ed82f27ab380977791e25ed6fda3 |
| packages/contracts/fixtures/invalid/scenario/proposed_massing_open_ring.json | f43309fa7a555f6a334eb0e2d6aed97feade878948315c702cc85dcc652aa635 |
| packages/contracts/fixtures/invalid/scenario/proposed_massing_self_intersecting.json | 3e38aa88791044fb864d2dadc591bc7df54516d2a78d31798f55288f6cdb0dc5 |
| packages/contracts/fixtures/invalid/scenario/proposed_massing_negative_height.json | 0b26601d1695e2035d952feef9420965e2b07b31d6e8c35519cb3fb1413c41cc |

Entry #8 (this report) is superseded by the current revision — the orchestrator re-hashes it at
integration; the other 12 are stable. The independent verifier's full return (HEAD/branch, raw + LF
digests, `cmp`, sizes, the six-command re-run, and the exact `git status` set) is in this unit's run
transcript for verbatim preservation by the orchestrator alongside the recorded gate.

### Verified vs remaining gaps

VERIFIED this pass: all six documented commands (actual cwd + outcomes above); raw-byte AND LF schema
equality (independent); the 13-file digest record; the changed-file set = 8 tracked worker files + 5
fixtures, no forbidden path (verifier `git status`).

REMAINING (orchestrator, not producer): (1) **AS-8 CI green on the pushed head** — the final
independent confirmation of ruff + both pytest suites in CI. (2) **AS-3 acceptance-wording
reconciliation** — an open owner/orchestrator decision (amend AS-3 vs record the documented
limitation); the contract gate refuses all three invalid fixtures regardless. Independent api-cwd
re-run: the fresh verifier sandbox's Bash cwd is fixed at the worktree root and its broker rejects a
`cd services/api` prefix, so it reproduced only the three repo-root checks (green) plus the raw-byte
hashes; the three api-cwd checks were run green in THIS unit from `services/api` (outcomes above) and
AS-8 CI on push is their independent confirmation. `project-control/tasks/M5-T048.json` stays
controller-owned and untouched.

## This revision (2026-09-19) — second orchestrator rework directive

Applied on top of the prior build (1.1.0 schema bump, `proposal.py`, `contract.py` threading,
regenerated TS, both test suites, five fixtures) and the first rework (which added
`exclusiveMinimum: 0` to `proposed_level.floor_to_floor_ft` in both schema copies and retargeted
the negative-height fixture to the schema layer). This rework is DOCUMENTATION-ONLY — no schema,
validator, fixture, or test-behavior change:

1. **Corrected the remaining false JSON-Schema claim** (this report + the two test files'
   comments/docstrings + `proposal.py`'s module docstring). The prior report/comments asserted a
   JSON Schema "provably cannot express" NYC coordinate bounds, the floor-to-floor upper bound, or
   the DB-013 count ceilings. That is FALSE: JSON Schema CAN express all three. They are enforced
   in `app.scenario.proposal` BY DESIGN, not by necessity — see the split below.
2. **No validator logic changed.** `validate_proposed_massing` keeps every typed refusal and the
   `exclusiveMinimum` positivity check stays defense-in-depth. Edits are comment/docstring text
   only; behavior is byte-identical.
3. **Worker integration count corrected** to thirteen paths (see "Files") and the controller-owned
   task file attributed separately.
4. **AS-3 remains explicitly unresolved** and its acceptance-wording reconciliation is routed to
   the orchestrator; I did NOT touch `project-control/tasks/M5-T048.json`.

## STRUCTURAL vs SEMANTIC — where each of the seven boundary constraints is enforced (corrected)

The JSON Schema (`scenario.schema.json` `proposed_massing` $def) fixes the STRUCTURAL shape: key
presence, object/array types, the `srid` enum `[2263]`, the `kind` enum `["proposed"]`,
`additionalProperties:false`, AND strict positivity of `floor_to_floor_ft` (`exclusiveMinimum: 0`,
added in the first rework). The remaining constraints split into two — NOT one — categories:

### (A) Expressible in JSON Schema, enforced SEMANTICALLY BY DESIGN (not because the schema can't)

These three could be written as ordinary JSON Schema keywords; the validator owns them on purpose:

- **NYC EPSG:2263 per-coordinate bounds** — expressible as `prefixItems: [{minimum, maximum},
  {minimum, maximum}]` on each `[x, y]` (x and y have different bounds). Enforced in the module
  (`NYC_2263_X/Y_MIN/MAX`).
- **Floor-to-floor sane upper bound** — expressible as `maximum` on `floor_to_floor_ft`. Enforced
  in the module (`MAX_FLOOR_TO_FLOOR_FT`).
- **DB-013 count ceilings** — expressible as `maxItems` on `vertices`/`levels`/`exterior_walls`
  and `maximum`/`minimum: 1` on `floor_count`. Enforced in the module (`MAX_OUTLINE_VERTICES`,
  `MAX_LEVELS`, `MAX_EXTERIOR_WALLS`, `MAX_FLOOR_COUNT`).

Why semantic and not schema: (1) each failure is a TYPED `ProposedMassingError` naming the exact
dotted field (e.g. `proposed_massing.outline.vertices[3]`) — a far better editor error surface than
a generic schema `maximum`/`maxItems` message; (2) the numeric bounds live once as `MAX_*` /
`NYC_2263_*` constants instead of being duplicated as literals in the two byte-identical schema
copies (which could drift); (3) defense in depth (the schema already carries `exclusiveMinimum`
and the module re-checks positivity too).

### (B) NOT expressible in JSON Schema — REQUIRE cross-value / geometry validation

These genuinely cannot be stated in JSON Schema and are the reason the module exists:

- **Ring closure** — `vertices[0] == vertices[-1]`; a cross-element equality no keyword expresses.
- **Non-self-intersection** — a geometric predicate over all edge pairs (simple polygon).
- **Distinct non-closing vertices** — partial-array uniqueness (`uniqueItems` cannot exclude the
  deliberate closing duplicate).
- **Level-index contiguity `{0..N-1}`** — the SET of `level_index` values must equal the range of
  the array length; a cross-element relation tied to `len(levels)`.
- **Wall vertex-index range + distinctness** — `start/end_vertex_index` must be in range of
  `len(outline.vertices)` and differ; a cross-field reference from one array's item into another
  array's length.

### Third case — height finiteness (NaN/Infinity)

Not a schema-expressible constraint AND not carriable by any real JSON document: JSON has no
NaN/Infinity literal, so a fixture file cannot hold one and the schema never sees it. The module's
finiteness check guards in-memory Python floats (defense in depth), and the contract gate's
strict-JSON guard (`json.dumps(..., allow_nan=False)`) refuses a programmatically-built non-finite
document at `<root>`.

## Remaining AS-3 geometry/schema mismatch — UNRESOLVED, routed to the orchestrator

AS-3 requires each invalid shape to yield the typed refusal "**and the matching invalid fixtures
fail schema validation**." State after both reworks:

- **negative height** — fails schema validation directly (`exclusiveMinimum: 0`). AS-3's schema
  clause is satisfied for this case.
- **open ring / self-intersecting** — category (B): a JSON Schema cannot express ring closure or
  non-self-intersection, so these fixtures are STRUCTURALLY schema-valid and are refused ONLY
  through the semantic gate. AS-3's literal "fail schema validation" clause CANNOT be met for these
  two geometry defects.

This is a genuine residual mismatch between AS-3's wording and what JSON Schema can do. It is NOT
resolved by this unit and I do NOT claim AS-3 satisfied. Acceptance-wording reconciliation is the
orchestrator's to make (Tier A/owner authority), WITHOUT any producer edit to controller-owned task
state. Options: (a) amend AS-3 so the production contract-gate refusal (schema + semantic) satisfies
it for defects a JSON Schema cannot express, or (b) record the documented limitation against AS-3.
Either way the contract gate refuses all three fixtures; the disagreement is only about the "schema
validation" layer for the two geometry defects. I did NOT edit `project-control/tasks/M5-T048.json`.

## Non-finite-height fixture coverage — explicit accounting

The packet SCOPE 1/2 asked for three invalid fixtures including "non-finite height." A non-finite
value (Infinity/NaN) is NOT valid strict JSON, so a non-finite-height FIXTURE FILE cannot exist as
a loadable `.json`. The three invalid fixtures are therefore open ring, self-intersecting, and
finite-negative height. Non-finite-height coverage is by TEST, not fixture:

- `test_scenario_proposal.py::test_non_finite_height_refused` / `::test_nan_height_refused` — the
  semantic validator refuses Infinity/NaN at `proposed_massing.levels[0].floor_to_floor_ft`.
- `test_scenario_contract.py::test_non_finite_height_block_refused_by_json_safety_guard` — the
  contract gate's strict-JSON (NaN/Infinity) guard refuses the whole document at `<root>`.

Surfaced for orchestrator awareness (a scope note, not a claim that a non-finite fixture file
exists).

## Files — authoritative status

**Worker integration set — thirteen (13) paths = eight tracked worker files + five fixtures.**

Eight tracked worker files (all show as `M` in `git status`):
1. `packages/contracts/schemas/v1/scenario.schema.json` — 1.1.0 bump + first rework's
   `exclusiveMinimum`. Unchanged this revision.
2. `services/api/app/_contract_schemas/v1/scenario.schema.json` — byte-identical copy of #1.
   Unchanged this revision.
3. `packages/contracts/generated/scenario.ts` — prior regeneration. Unchanged this revision.
4. `services/api/app/scenario/contract.py` — prior threading of the optional block. Unchanged
   this revision.
5. `services/api/app/scenario/proposal.py` — validator (typed refusals preserved). This revision
   corrected ONLY the module docstring's STRUCTURAL/SEMANTIC sentence; no logic change.
6. `services/api/tests/scenario/test_scenario_contract.py` — this revision corrected the
   STRUCTURAL/SEMANTIC comment block; test behavior unchanged.
7. `services/api/tests/scenario/test_scenario_proposal.py` — this revision corrected the module
   docstring; test behavior unchanged.
8. `project-control/reports/M5-T048-producer-report.md` — this report.

Five fixtures (untracked, `??` in `git status`):
9.  `packages/contracts/fixtures/valid/scenario/proposed_massing_preliminary.json`
10. `packages/contracts/fixtures/valid/scenario/proposed_massing_multilevel.json`
11. `packages/contracts/fixtures/invalid/scenario/proposed_massing_open_ring.json`
12. `packages/contracts/fixtures/invalid/scenario/proposed_massing_self_intersecting.json`
13. `packages/contracts/fixtures/invalid/scenario/proposed_massing_negative_height.json`

**Controller-owned — NOT a worker path (the 14th `git status` entry):**
`project-control/tasks/M5-T048.json` (claim/progress edits). I did NOT modify or revert it.
REQUEST: the orchestrator attributes this task-file diff to the controller and keeps it out of the
worker integration set.

Files edited THIS revision: #5, #6, #7, #8 (documentation only).

## Requested supervisor/orchestrator evidence (bounded, digest-bound per-file)

The review-round budget is spent on code, so please collect per-file and digest-bound (sha256,
LF-normalized before hashing — checkout CRLF smudges raw digests) so the implementation and the
seven boundary answers are actually reviewable:

- `services/api/app/scenario/proposal.py` (complete)
- `services/api/app/scenario/contract.py` (changes)
- `services/api/tests/scenario/test_scenario_contract.py` (changes)
- `services/api/tests/scenario/test_scenario_proposal.py` (changes)
- `packages/contracts/schemas/v1/scenario.schema.json` AND
  `services/api/app/_contract_schemas/v1/scenario.schema.json`
- this producer report (complete — carries the STRUCTURAL/SEMANTIC split, the seven modularity
  boundary answers, and the AS-3 / non-finite notes)

Also required before acceptance:

- **Independent schema-copy byte-equality evidence** — the supervisor computes sha256 of BOTH
  schema copies (LF-normalized) and confirms they are equal, independently of the in-test
  `test_runtime_bundle_copy_is_byte_identical_to_canonical` assertion.
- **Controller attribution of the task-file diff** — `project-control/tasks/M5-T048.json` is the
  controller's, recorded separately from the worker integration set.
- **cwd-correct verification transcripts** — see next section.

## Self-checks — what ran, what did NOT

[PRESERVED, per the evidence-preservation directive. The "services/api-cwd commands NOT executed" state
below is the PRIOR loop-worker's self-check record; the Verification pass at the top of this report
supersedes it — those three api-cwd checks were subsequently run from `services/api` with real green
outcomes. The failed wrong-cwd invocations and the successful root-command results are kept verbatim
below.]

Repo-root commands RAN this-lineage (real outcomes, cwd = worktree root
`C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t048`):
- `python packages/contracts/scripts/generate_ts_types.py --check` → OK (scenario TS unaffected by
  documentation-only edits and by the `exclusiveMinimum` edit).
- `python -m pytest packages/contracts/scripts/tests -q` → **29 passed**.
- `python tools/modularity_check.py --check` → 447 files selected; **failures 0**
  (`proposal.py` not on the warning list).

`services/api`-cwd commands (`python -m ruff check .`, `python -m pytest tests/scenario -q`,
`python -m pytest tests/api -q`) — **NOT executed.** This loop-worker's command broker admits only
the exact documented strings from the repo-root cwd; it rejects a `cd services/api` prefix, and the
PowerShell tool is held. Run bare from repo root they are wrong-cwd artifacts, not self-checks:
`python -m ruff check .` lints the whole repo, and `python -m pytest tests/scenario -q` errors
"file or directory not found." **Those directory-not-found / wrong-cwd runs are NOT regression
evidence and must not be recorded as such.**

**REQUEST: the supervisor collects the three checks FROM the `services/api` cwd and records the
actual cwd + real PASS/FAIL outcomes** — `cd services/api && python -m ruff check .`,
`python -m pytest tests/scenario -q`, `python -m pytest tests/api -q`. Expected by code reasoning
(UNVERIFIED locally, documentation-only edits): ruff clean; `tests/scenario` green; `tests/api`
green.

## Modularity boundary answers (`proposal.py`) — the seven

1. **Owning responsibility** — semantic validation of a parsed `proposed_massing` block: the
   geometry/level/wall/provenance invariants of category (B) plus the by-design category (A)
   bounds. One responsibility.
2. **Boundary** — a focused module; `contract.py` only *admits + threads* the optional block
   (version-gates 1.1.0, wraps `ProposedMassingError` into `ScenarioContractError`); it does not
   own the invariants.
3. **Separation** — pure domain validation: no persistence, serialization, external I/O, CLI/API
   wiring, or presentation.
4. **Size / cohesion** — ~450 SLOC, below the warn threshold; single cohesive purpose; absent from
   the modularity warning list.
5. **Public interface** — exports `validate_proposed_massing` + `ProposedMassingError` (+ the
   `MAX_*` ceilings); no existing public interface changed; `contract.py`'s signature is unchanged.
6. **No dumping ground** — a single-purpose validator, not a utils/helpers catch-all.
7. **Dependencies** — standard library only (`math`); no new dependency; deterministic and offline.

## Acceptance scenarios

- **AS-1** valid block threads and emits 1.1.0; same doc without the block emits 1.0.0 unchanged —
  `test_scenario_contract.py::test_valid_block_on_1_1_0_document_validates`,
  `::test_legacy_1_0_0_document_without_block_validates_unchanged`, plus both valid fixtures pass
  `validate_scenario_document`. (Verify via the requested supervisor `tests/scenario` transcript.)
- **AS-2** schema copies byte-identical + typegen `--check` zero-diff + all 1.0.0 fixtures valid —
  `generate_ts_types.py --check` OK (ran); byte-identity asserted by
  `::test_runtime_bundle_copy_is_byte_identical_to_canonical` AND to be re-confirmed by the
  requested independent supervisor sha256 comparison.
- **AS-3** UNRESOLVED / needs reconciliation — negative height fails schema validation
  (`exclusiveMinimum: 0`); open-ring and self-intersecting are category (B) and CANNOT fail schema
  validation, refused through the semantic gate. See "Remaining AS-3 geometry/schema mismatch"
  above; routed to the orchestrator. All three are refused by the contract gate.
- **AS-4** third-input-class honesty: `kind` is the literal `proposed`; `proposal.py` docstring
  states the records/rules/proposals distinction; nothing derives an allowance —
  `test_provenance_kind_must_be_proposed`, `test_validator_returns_none_never_a_value`.
- **AS-5** NYC EPSG:2263 bounds + MAX ceilings typed fail-closed, at-ceiling and one-past —
  `test_scenario_proposal.py` ceiling tests + `test_vertex_out_of_nyc_bounds_refused`.
- **AS-6** full scenario + api suites green unchanged, contracts-script green, no builder/derive/api
  change — VERIFIED this pass (see Verification pass): `tests/scenario` **527 passed**, `tests/api`
  **439 passed** (services/api cwd), contracts-script **29 passed** (repo root); file set (`git
  status`, verifier-confirmed) is 8 tracked worker files + 5 fixtures, no forbidden path. AS-8 CI on
  push is the final independent confirmation.
- **AS-7** ruff clean; modularity exit 0 — VERIFIED this pass: `ruff check .` **All checks passed!**
  (services/api cwd); modularity **447 files; failures 0** (repo root), proposal.py off the warning
  list.
- **AS-8** CI green on the pushed head — PENDING; orchestrator captures after push (thin client).

## Discovery routing (D-069)

None new. No out-of-scope finding surfaced; no forbidden path touched. (The AS-3 wording vs
JSON-Schema-expressiveness mismatch is surfaced above for orchestrator reconciliation, not a code
defect.)

## Orchestrator next steps (not producer work) — CI and acceptance stay PENDING

Integrate the working-tree changes as ONE material commit; collect the requested digest-bound
per-file evidence AND the independent schema-copy byte-equality evidence; attribute the
controller-owned `project-control/tasks/M5-T048.json` diff separately; run the three
`services/api`-cwd checks (ruff, tests/scenario, tests/api) recording the actual cwd + real
outcomes; record G0–G5 with the named reviewers (`data-contract-verifier`, `code-reviewer`,
`qa-engineer`, `security-reviewer`, `directive-compliance-verifier`); push; capture AS-8 CI on the
pushed head. **Do NOT accept until (a) the required cwd-correct + digest-bound evidence exists and
(b) the AS-3 acceptance-wording reconciliation is decided.**


## [ORCH-CORRECTED per contracts-CI, 2026-09-19] Semantic-fixture relocation (orchestrator addendum)

The contracts CI job at the harvested head failed 2/11: the open-ring and self-intersecting
fixtures under fixtures/invalid/scenario/ "unexpectedly PASSED validation" - by design, since
their defects are geometry invariants a JSON Schema provably cannot express (this report's own
layering section says exactly that). The CI job's convention is that everything under invalid/
must fail SCHEMA validation; the packet's SCOPE input (orchestrator-authored) had directed the
two fixtures there. Orchestrator correction, tagged: both fixtures moved verbatim (git mv, zero
content change) to the new third class fixtures/semantically_invalid/scenario/ - which the CI
schema job deliberately does not walk - and test_scenario_contract.py updated: a
SEMANTICALLY_INVALID_FIXTURES glob, the exact-2 count assertion, the whole-gate refusal
parametrization extended over both classes, and the dedicated schema-valid-but-semantically-refused
test now loading from the new directory. The negative-height fixture stays under invalid/
(exclusiveMinimum: 0 IS schema-expressible and the CI job rejects it correctly). Packet
allowed_paths amended accordingly ([ORCH-PACKET-FIX 2]).
