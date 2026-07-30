# M2-T018 — G3 code review (D-004 Step 4 pilot; reviewer return, captured verbatim)

Orchestrator capture note: reviewer = code-reviewer, unnamed spawn, explicit Fable 5, frozen SHA
`756f60164e5cf27c56082166047ffc119a5f3d02` (task/M2-T018-serializer-wiring). Return preserved
verbatim below (transport entity-decoding only; one absolute worktree path normalized to
repo-relative form per the no-machine-specific-data rule).

---

# Gate Report

- Gate ID: G3 (independent code review)
- Task ID: M2-T018 — Wire the M2-T017 allowlist serializer into the property-profile builder (fail-closed provenance write boundary)
- Reviewer: code-reviewer (independent; not the producer)
- Producer: backend producer agent (isolated worktree; delivery ported by orchestrator)
- Result: PASS
- Clean environment/worktree used: `.claude/worktrees/M2-T018-serializer-wiring` at frozen SHA

## Frozen-SHA confirmation

`git -C <worktree> rev-parse HEAD` → `756f60164e5cf27c56082166047ffc119a5f3d02` on branch `task/M2-T018-serializer-wiring`. Matches the frozen SHA exactly. Diff base `84c1bf29243bb862d344c909099c9bd9a3f6a766`; `git log 84c1bf2..HEAD --oneline` shows exactly one commit (`756f601`, committed by the owner git identity `martin10101`, consistent with the orchestrator's ruled-on port). The producer's worktree-delivery deviation is noted per instruction and not re-litigated.

## Acceptance criteria reviewed

AS-1 through AS-6 from `project-control/tasks/M2-T018.json` (worktree copy), cross-checked against `project-control/reports/M2-T018-producer-report.md`. All producer claims were re-derived, not trusted.

## Directive/requirement verification

The task is in-regime (`directive_refs: D-004 ALL`). Per the dispatch, the full per-requirement D-004 pass belongs to the independent directive-compliance-verifier; within this G3's purview I verified at the frozen SHA:

| Item | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| No effort keys anywhere in the diff (D-004 standing hold) | 756f601 | PASS | `git diff 84c1bf2..HEAD \| grep -i effort` → no matches |
| No git/gh/control-CLI writes by the producer (D-004-R303) | 756f601 | PASS | Single commit authored/committed by the owner identity (orchestrator port); producer report discloses no CLI writes |
| Worktree attestation before first write (D-004-R302) | 756f601 | NOTED | Deviation disclosed in report §0; already ruled on by the orchestrator (port verified tree-identical) — not re-litigated |

## Steps independently executed (reproducible)

All from the worktree root unless noted:

1. `git rev-parse HEAD` / `git branch --show-current` — SHA + branch confirmed.
2. `git diff 84c1bf2..HEAD --stat` and `--name-only` — 7 files, containment check.
3. Full read of the production diff, `builder.py`, `serializers.py`, both new test files, the amended tripwire file, `zoning_crosscheck.py` internals, and read-only inspection of `app/api/v1/properties.py` + `app/api/v1/rule_evaluation.py`.
4. `sha256sum` of both `source_fact.schema.json` copies; JSON comparison of schema `properties`/`required` vs the serializer allowlist tuples.
5. `services/api$ python -m pytest tests/contracts tests/profile tests/api -q` → **243 passed in 5.09s** (expected 243).
6. `services/api$ python -m pytest tests -q` → **1048 passed in 13.52s** (expected 1048).
7. `python packages/contracts/scripts/generate_ts_types.py --check` → rc=0 (all four OK lines); `python services/api/scripts/sync_contract_schemas.py --check` → rc=0.
8. `services/api$ python -m ruff check app tests` → "All checks passed!".

## Findings per review item

**Item 1 — fail-closed boundary correctness: PASS.** `builder.py` writes to `profile["provenance"]` in exactly two places, and both cross `_closed_provenance`: the initial splice (line 763, `_closed_provenance([*result.facts, *(additional_provenance or [])])`) and the wave extend (line 828, `profile["provenance"].extend(_closed_provenance(wave_provenance))`). A repo-wide grep for provenance-array writes in `app/**` finds no other writer (hits in `rules/evaluator.py`, `scenario/builder.py`, `spatial/models.py` are different structures under different contracts, not the profile provenance array). `zoning_crosscheck.py` is not a bypass: `crosscheck_lot_zoning` returns a `CrosscheckReport` (conflicts/agreements/notes only), never emits a `source_fact`, and is currently imported only by tests — producer D5 verified true. Failure propagation: `ContractSerializationError` is a `ValueError` subclass raised before the profile dict is bound (initial splice) or before `extend` mutates (wave path — the list comprehension completes or raises atomically), so no partial profile can escape `build_property_profile`. D3 route claim verified read-only against `properties.py`: build at line 393 sits inside the outer try (line 370); the inner try (399–404) wraps only `validate_profile`; `except Exception` (line 407) → `_internal_error_500` (typed 500, logs `type(exc).__name__` + correlation id only, never `str(exc)`). Same structure in `rule_evaluation.py` (build 226, inner try 231–233, `except Exception` 285 → typed 500). Line numbers match the producer report exactly.

**Item 2 — no silent loss/mutation: PASS.** `AllowlistSerializer.serialize` rejects unknown keys BEFORE projecting, so the projection (`{field: record[field] for field in self._allowed if field in record}`) can only reorder, never drop. The completeness assertions are real: `test_as4_provenance_count_is_preserved_across_every_feed` asserts exact count (`len(pluto.facts) + len(ztldb.facts) + 2`); `test_as4_every_record_keeps_its_keys_and_values` asserts per-record key-set equality AND full dict equality; `test_as4_connector_inputs_are_never_mutated` asserts input snapshots unchanged and emitted records are new objects (`is not`). Values are shallow-copied by reference — pre-existing documented M2-T017 design, no worse than the previous direct splice; not a regression.

**Item 3 — no-schema-change finding: VERIFIED, HOLDS.** Independently re-derived: the serializer allowlist (`serializers.py` lines 205–208) already documents all four lineage surfaces — `dataset_id`, `request_url`, `input_vintages`, and the fourth, `source_rows_updated_at` (ZTLDB) — marked "M2-T017 documented connector-lineage keys". The canonical schema's `properties` (21 keys) and `required` (12 keys) match the frozen tuples exactly in content AND order, with `additionalProperties: false`. Both schema copies hash to `2577d2aabe6fb9c4732dd43eeda815630fd0b804dd345366b96c4b94e5380540` (byte-identical; matches the producer's stated hash). `packages/contracts/generated/property_profile.ts` already declares all four keys (lines 39–44), and `generate_ts_types.py --check` rc=0 confirms no regeneration was needed. The producer's decision to change no contract artifact is correct.

**Item 4 — tripwire replacement: PASS, genuinely stronger.** The retired `test_serializer_not_imported_by_any_production_module` is replaced by four tests that pin a single boundary from three angles: (a) AST import scan over all `app/**` modules outside `app/contracts/` asserting the importer list `== ["services/api/app/profile/builder.py"]` — a second stray import lengthens the list and FAILS; losing the wiring empties it and ALSO fails (the old test caught only the first direction); (b) substring scan (`"app.contracts"` / `"contracts.serializers"`) catching dynamic `importlib` reaches, same exact-equality assertion; (c) narrowest-dependency pin (`imported == ["SOURCE_FACT_SERIALIZER"]`); (d) AST call-site pin that `SOURCE_FACT_SERIALIZER` appears in `builder.py` only inside `_closed_provenance` (import aliases are `ast.alias`, not `ast.Name`, so the import line correctly doesn't count as stray). Diff of the test file confirms only the module docstring and the tripwire section changed; the eleven M2-T017 serializer unit tests are untouched. Limit (acceptable): a deliberately obfuscated string-concatenation dynamic import would evade (b) — tripwires guard accidents, not adversaries.

**Item 5 — test quality of the 16 new tests: PASS with two LOW gaps.** The tests are behavioral, not implementation-mirroring: all fixtures are replayed through the real connectors (PLUTO F01, ZTLDB ZT01+ZT08, zoning-features nylh 5-response script, MapPLUTO MPG01+MPG02); injection happens in connector output, and assertions land on observable outcomes (exception type/keys, wire status codes, response text). Undocumented key → closed failure proven in all three feeds — including the wave feed via a monkeypatched `build_wave_sections`, which proves the second call site is live, not just present. Wire tests use `raise_server_exceptions=False` so the 500 is the real HTTP contract: `state == "internal_error"`, correlation id present, `"provenance"` absent, neither the injected key nor the secret value anywhere in `response.text`; clean capture → 200 control test included. Value-leak safety re-proven at the wired boundary, not just in serializer unit tests. The AS-2 fixpoint check (`serialize(record) == record` plus canonical key order) has real detection power: I verified the PLUTO connector emits lineage keys BEFORE the M2-T004 identity keys (pluto_soda.py lines 838–840) while canonical order puts them after `response_digest`, so an un-routed splice would fail the order assertion. Gaps: (i) no boundary- or wire-level test for a non-mapping/`None` record entering the provenance feeds — that path raises `TypeError` (unit-tested at the serializer; still fail-closed at the wire via the routes' generic `except Exception` → typed 500), LOW; (ii) the provenance-specific wire proof covers the properties route only — however the rule_evaluation route has pre-existing wire proof that ANY builder exception maps to a typed 500 with no internals (`test_as10_internal_error_is_generic_500_no_internals`, which monkeypatches an exploding `build_property_profile`), so the producer's "both routes proven at the wire" is substantiated in aggregate; noting the precision. Empty-list and mid-array modes are covered structurally (every PLUTO-only build exercises `_closed_provenance([])`; the list comprehension is atomic).

**Item 6 — containment: PASS.** `git diff 84c1bf2..HEAD --name-only` → 7 paths, every one inside `allowed_paths`; no forbidden path touched (no `app/api/`, `app/connectors/`, `app/rules/`, `tools/`, `docs/`, `.claude/`); no dependency/lockfile/pyproject changes; no effort keys in the diff. The `wave_integration.py` (+9) and `zoning_crosscheck.py` (+12) diffs are honest docstring-only additions — both hunks live entirely inside the module docstrings, before `from __future__ import annotations`; zero functional delta, and the zoning_crosscheck docstring's factual claims were verified true against the code (Item 1).

**Item 7 — suites: PASS, exact counts reproduced.** Targeted `tests/contracts tests/profile tests/api -q`: **243 passed** (expected 243). Full `tests -q`: **1048 passed, 0 failed** (expected 1048). Arithmetic is consistent: 224 baseline + 13 (write-boundary) + 3 (API wire) + 4 (tripwire) − 1 (retired) = 243. Additionally: ruff clean; both drift checks rc=0.

**Item 8 — Pyright hints adjudicated.** (a) `Iterable`/`Mapping` (line 54), `Any` (line 56): **false positives** at the frozen SHA — all three are used in `_closed_provenance`'s signature at line 527 (`records: Iterable[Mapping[str, Any]]`). (b) `SOURCE_FACT_SERIALIZER` (line 64): **false positive** — called at line 565. Ruff (which enforces F401 unused-imports) passes clean, corroborating. The hints were likely produced against a stale copy. (c) `result` at line 441: **real** — the `result: PlutoFetchResult` parameter of `_status_dimensions` is unused in its body — but it is **pre-existing at the base SHA** (same function, same signature, at base line 425) and untouched by this diff; it masks no wiring defect and is not this task's rework. No dead code was introduced by M2-T018.

## Regression/security/provenance findings

- No regression: full suite green; the only test whose premise changed is the deliberately retired tripwire, replaced by a strictly stronger invariant.
- Security: diagnostic-leak discipline verified end to end (key names only in exceptions; routes log type + correlation id only; wire test asserts neither key nor value in the response body).
- Provenance: boundary preserves every documented field including all four lineage keys; canonical-order re-emission is the only observable payload change and nothing in the 1048-test suite depended on the old order.
- Governance carry-forward (for the orchestrator, echoing producer R1, verified plausible): the D-002 registry's `verification.json` for **D-002-R038** cites the now-retired "serializer not imported by any production module" evidence; post-merge that evidence statement is intentionally false and the supersession should be recorded so it is not later misread as a regression. Registry is orchestrator-owned and outside this task's paths — correctly untouched.

## Defects

| ID | Severity | Description |
|---|---|---|
| DF-1 | LOW (docs) | `services/api/app/contracts/serializers.py` module docstring section "FROZEN INTERFACE — NOT WIRED (task M2-T017 scope boundary)" (lines 33–41) is now contradicted at HEAD: `builder.py` imports the serializer. The text is framed as M2-T017-scoped ("in this task"), and the tripwire test docstring records the retirement, but the header reads as a present-tense claim. The file IS in `allowed_paths`; a short amendment ("wired at the single builder boundary by M2-T018") would prevent misreading. Non-blocking. |
| DF-2 | LOW (test gap) | No boundary- or wire-level test for a non-mapping/`None` record entering a provenance feed. Behavior is fail-closed regardless (serializer `TypeError`, unit-tested; routes' generic `except Exception` → typed 500, wire-tested generically), so this is coverage polish, not a correctness hole. Non-blocking. |
| DF-3 | INFO (pre-existing, out of scope) | `_status_dimensions` unused `result` parameter (builder.py line 441) pre-exists at base; `app/connectors/pluto_soda.py` lines 836–837 comment "source_fact v1 permits additional keys" is stale post-M2-T017 closure. Both outside this task's change surface; candidates for a separate cleanup task. |

## Required rework

None blocking. DF-1 and DF-2 are recommended non-blocking follow-ups at the orchestrator's discretion (fold into acceptance notes or a follow-up task); DF-3 and the D-002-R038 supersession recording are orchestrator/registry follow-ups, not producer rework.

## Reviewer conclusion

The fail-closed provenance write boundary is correctly and completely wired at both entry points with no bypass; the no-schema-change finding was independently re-derived and holds; the tripwire replacement is strictly stronger than what it retired; the 16 new tests are behavioral and reproduce exactly (243/243, 1048/1048, drift checks rc=0, ruff clean); containment is exact; every static-analysis hint against the new code is a false positive. Remaining findings are LOW/INFO and non-blocking.

VERDICT: PASS — every reviewed item reproduces at the frozen SHA with only LOW documentation/coverage findings that do not affect the fail-closed boundary's correctness, containment, or evidence.
