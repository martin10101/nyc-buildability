# M4-T009 — Producer report

**Task:** M4-T009 — R1–R12 residential FAR draft rule family (flat districts) from the committed
ZR 23-21 / ZR 23-22 snapshots
**Producer role:** backend-engineer (persistent-local-33)
**Branch:** `task/M4-T009-r1r12-far`  **Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m4t009`
**Base / current SHA:** `e1cb45ad` (all work is in the working tree, uncommitted — see "Commit duty")
**Directive:** D-038 / D-038-R003

This revision (2026-09-11, second rework response) responds to the latest rework request. Changes vs.
the prior report: (1) **AS-5 is now marked UNRESOLVED, not satisfied** — the current provenance tests
establish snapshot internal consistency and observable drift, NOT a comparison against a digest the
RULE records; the criterion is not weakened and the precise required representation plus the
schema/loader scope change are documented and routed to the orchestrator (§2 AS-5, §4); (2) the AS-6
tests are STRENGTHENED — they select the qualifying alternative by its exception ID, verify its effect
and citation, byte-check the district→value association against the snapshot, and add negative
(metamorphic) cases for deleting the exception and for deleting or misassigning a district entry,
including the R8 discriminator where the wide-street alternative repeats 7.20 (§2 AS-6); (3) all
behavioral claims are held pending until supervisor/CI evidence shows BOTH documented commands pass on
a supported environment; the bundle-sync corroboration, the supported test environment, and any AS-5
schema/loader change are routed to the orchestrator (§3–§4); (4) fresh captured command evidence and
bounded acceptance-test excerpts are attached (§6); (5) the two-module split and the complete
11-path staging set are unchanged (§1, §5). No rule quote or FAR value changed in this revision.

## 1. What was authored

Four new draft rules alongside the accepted-shape pilot `r5_residential_far.rule.json`, plus a
correction to that pilot, plus a two-module acceptance-scenario pack, plus three existing-test
adaptations. All rules reuse ONLY the existing engine primitives (`in_set` applicability,
`param_select` + `identity` + `multiply` computation, `conditional_alternative` /
`documented_limitation` exceptions). No engine change (AS-8); nothing under `services/api/app/rules/*.py`
or `services/api/app/rules/schemas/**` was touched.

| File | Kind | Snapshot cited | Districts |
|---|---|---|---|
| `services/api/app/rules/rulesets/r1_r2_r3_residential_far.rule.json` | new | zr-23-21 | R1-2A, R1-1, R1-2, R2A, R2, R3A, R3X, R3-1, R3-2 (9) |
| `services/api/app/rules/rulesets/r2x_r4_residential_far.rule.json` | new | zr-23-21 | R2X, R4A, R4B, R4, R4-1 (5) |
| `services/api/app/rules/rulesets/r5_residential_far.rule.json` | edit (AS-9) | zr-23-21 | R5, R5A, R5B, R5D (4) |
| `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json` | new + AS-6 edit | zr-23-22 | 23 flat R6–R12 districts |
| `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json` | new | zr-23-22 | R6, R7-1, R7-2, R8 (4, conditional) |
| `services/api/tests/rules/test_r1_r12_residential_far.py` | new | — | AS-1, AS-2, AS-3, AS-4, AS-7, AS-8, AS-9 |
| `services/api/tests/rules/test_r1_r12_residential_far_provenance.py` | new | — | AS-5, AS-6 |
| `services/api/tests/rules/test_rules_engine.py` | edit | — | AS-9 ripple: R5 no longer carries the 0.60 cap; r1-r2-r3 does |
| `services/api/tests/rules/test_rules_integration.py` | edit | — | family now spans R1–R12: select the applicable trace among many |
| `services/api/tests/rules/test_rules_fh_safeguards.py` | edit | — | same applicable-trace selection adaptation |

**This (second rework) revision made NO rule-content change.** The only edits are in
`services/api/tests/rules/test_r1_r12_residential_far_provenance.py` (AS-6 strengthening + negative
cases; AS-5 module docstring) and this report. Every rule file, the AS-1/2/3/4/7/8/9 module, and the
three adapted sibling tests are byte-identical to the prior submission. In particular no rule quote or
FAR value changed, and `r5_residential_far.rule.json` still differs from M4-T001 only by the AS-9
footnote-exception move (FAR values 1.50/1.50/1.50/2.00 unchanged). The prior revision had already
rewritten the `qualifying_housing` description of `r6_r12_residential_far.rule.json` to enumerate the
full per-district qualifying FAR; that enumeration remains and the strengthened AS-6 association test
now byte-checks each district's value against the snapshot rather than relying on that prose.

**Test-module split (AS-8 modularity).** The acceptance pack was split into
`test_r1_r12_residential_far.py` (AS-1/2/3/4/7/8/9) and `test_r1_r12_residential_far_provenance.py`
(AS-5/6). The modularity checker reports zero warnings on either module (§2 AS-8); a single combined
module with the new AS-5 mismatched tests and the expanded AS-6 per-district loop would have crossed the
600-SLOC warn threshold. Together the two modules are the complete AS-1..AS-9 evidence.

District coverage: 18 (zr-23-21) + 27 (zr-23-22) = 45 distinct districts, all covered, applicability
sets pairwise disjoint, documented-exclusion list empty (AS-2).

## 2. Self-verification performed in this unit

### AS-1 source fidelity — VERIFIED by inspection against both committed snapshots
Every authored FAR value was compared, by hand, against the row it cites, and the acceptance pack
asserts it by LOADING the snapshot and comparing (never by restating the number). All match:

- **zr-23-21** (rows → rules): row 1 (0.75 / 1.00, footnote-1 on standard) → r1-r2-r3; R2X row (1.00 /
  1.00) + R4* row (1.00 / 1.50) → r2x-r4; R5A/R5B/R5 row (1.50 / 2.00) + R5D row (2.00 / 2.00) → r5.
- **zr-23-22** flat rows → r6-r12: R6A/R6-1/R7B 3.00/3.90; R6B 2.00/2.40; R6D/R6-2 2.50/3.00;
  R7A 4.00/5.01; R7D 4.66/5.60; R7X/R7-3 5.00/6.00; R8A/R8X 6.02/7.20; R8B 4.00/4.80; R9A/R9 7.52/9.02;
  R9D/R9X/R9-1 9.00/10.80; R10A/R10X/R10 10.00/12.00; R11 12.00/15.00; R12 15.00/18.00 — all match.
- **zr-23-22** conditional rows → r6-r7-r8: conservative (lower) R6 2.20, R7-1/R7-2 3.44, R8 6.02;
  wide-street (higher) R6 3.00, R7-1/R7-2 4.00, R8 7.20; qualifying from the lower row R6 3.90,
  R7-1/R7-2 5.01, R8 7.20; R8 footnote-2 wide-street qualifying 8.64 — all match.

### AS-2 complete coverage — structurally verified
45 districts, applicability sets pairwise disjoint, empty documented-exclusion list, counts asserted;
no rule claims a district absent from either snapshot.

### AS-3 conservative-on-conditionals — structurally verified; behavior pending CI
`r6_r7_r8_wide_street_conditional_far.rule.json` computes and returns the LOWER value only; the higher
wide-street value is surfaced via an always-on (`condition: null`) `wide_street_far_alternative` and is
never a computation input. The R8 footnote-2 8.64 value is `documented_limitation` scoped to
`zoning_district == R8` only.

### AS-4 / AS-9 footnote scope — verified
The 0.60 single-dwelling-unit cap exception is present on r1-r2-r3 (the only zr-23-21 row whose markup
carries `0.75¹`) and ABSENT from r2x-r4 and r5. The R5 pilot's previously-misattributed cap remains
removed; its FAR values are unchanged.

### AS-5 source-digest binding — UNRESOLVED (criterion NOT weakened; schema/loader change routed to the orchestrator)

**Status: UNRESOLVED.** AS-5 (as written) requires that "a test asserts every rule's citation resolves
to a snapshot file that exists on disk and whose `content_digest_sha256` matches **what the rule
records**." The current provenance tests do NOT meet that literal criterion, and this revision stops
claiming they do. I am not weakening the criterion; I am recording exactly what is and is not proven and
routing the enabling change to the orchestrator.

**What the current tests DO establish (retained, but not sufficient for AS-5):**

1. `test_as5_citations_resolve_on_disk_with_expected_dates` — every citation's `snapshot_id` resolves to
   a committed `*.snapshot.json`, whose stored `content_digest_sha256` equals `sha256(verbatim_excerpt)`
   (snapshot **internal self-consistency**), with section number and 2024-12-05 amendment date matching.
2. `test_as5_matching_every_rule_binds_committed_snapshot_digest` — the digest the engine resolves into
   the exported trace equals the committed snapshot file's stored digest and a recomputation of it.
3. `test_as5_tampered_excerpt_without_digest_update_fails_closed` — altering a snapshot's excerpt without
   updating its stored digest makes `SnapshotStore.load` fail closed (`SnapshotError`): tamper-evidence.
4. `test_as5_silent_recapture_drift_is_detectable` — a consistent re-capture yields a different digest
   than the value the **test** hard-codes as expected, so the drift is observable.
5. `test_as5_export_fails_closed_without_resolvable_digest` — stripping citation provenance makes
   `export()` raise `ProvenanceError`.

**Why that is NOT AS-5.** Every derivation above is either the snapshot store checking itself
(digest ↔ its own excerpt) or a comparison against a digest **recorded in the test**. None compares the
snapshot's digest against a digest **recorded by the rule**. The rule file today carries no digest at
all (its `citations[]` entries are `snapshot_id` / `section` / `quote` / `last_amended` only), so there
is nothing rule-authored to bind the snapshot to. A rule could be pointed at the wrong snapshot revision,
or a snapshot could be replaced by a self-consistent re-capture, and no RULE-anchored check would fire —
only the test's own hard-coded expectation would. That is the gap AS-5 is written to close, and it is
open. **Behavioral claim held pending** in any case (the tests cannot be exercised here — §3).

**Precise required representation (what would resolve AS-5).** The rule must record its expected source
digest, checked fail-closed at load:

1. **Schema (additive):** add a `content_digest_sha256` string property (64-hex; optionally
   `content_digest_alg` defaulting to `sha256`) to the `citations[]` item schema in
   `services/api/app/rules/schemas/v1/rule_definition.schema.json`. That object is currently
   `"additionalProperties": false` with `required: ["snapshot_id","section","quote"]`, so the property
   cannot be added without a schema change; a parameter `value` cannot carry it either, because parameter
   values are constrained to `additionalProperties: {type: number}`.
2. **Loader (fail-closed):** in `services/api/app/rules/dsl.py::_check_refs`, when a citation records a
   digest, verify `snapshots.get(citation["snapshot_id"]).content_digest_sha256 == citation["content_digest_sha256"]`
   and raise `DSLError` (fail closed) on mismatch or on a malformed/absent digest — so a rule can never
   LOAD against a snapshot it does not expect.
3. **Rule files:** add the recorded digest to each authored rule's citation (in-scope here once the
   schema/loader accept it).
4. **Test:** assert each rule's RULE-recorded citation digest matches the on-disk snapshot, plus a
   negative case that corrupts the rule-recorded digest and expects a load-time `DSLError`.

**Routed to the orchestrator (do not weaken, do not edit forbidden/out-of-scope paths).** Steps 1–2
touch `services/api/app/rules/schemas/**` and `services/api/app/rules/dsl.py`, both OUTSIDE this
packet's `allowed_paths` (which are `services/api/app/rules/rulesets/**` and
`services/api/tests/rules/**`); `schemas/**` is also a declared `forbidden_path`. This is a contract
change (an additive schema version bump + loader enforcement + a data-contract review) and must be
scoped as a separate authorized task by the orchestrator. Until that lands, step 3 (adding the digest to
the rule citations) is blocked because the schema would reject the new property, so AS-5 stays
UNRESOLVED for this task. No criterion is relaxed by this report.

### AS-6 second column surfaced for every district — STRENGTHENED (structural); behavior pending CI
The AS-6 tests no longer scan concatenated exception text (which the prior version did — a weakness,
because for R8 the wide-street standard alternative repeats 7.20, the same value as R8's qualifying
column, so a text search for "7.20" would pass even if the qualifying surfacing were deleted). They now,
per the rework:

- **Select the qualifying alternative BY ITS EXCEPTION ID.** The id differs by source table:
  `qualifying_residential_site` for the ZR 23-21 rules (R1–R5), `qualifying_housing` for the ZR 23-22
  rules (R6–R12) — mapped explicitly in `_QUALIFYING_EXCEPTION_ID`. The test selects that exact id both
  in the rule document and in the evaluation output's `exceptions_applied`.
- **Verify its effect and citation.** The selected exception's `effect` is asserted
  `conditional_alternative`; `_assert_exception_citation_resolves` asserts the exception's `citation_ref`
  is a declared citation of the rule AND that it resolves in the exported trace to the on-disk snapshot's
  `content_digest_sha256` — tying AS-6 into the AS-5 provenance chain.
- **Verify the applicable district → value association, byte-checked against the snapshot.**
  `_assert_district_qualifying_association` asserts, for every applicable district, that the value the
  rule records in `qualifying_far_by_district[district]` equals the qualifying value in the snapshot ROW
  that governs that district (the lower row for a wide-street district), loaded from the snapshot — never
  restated as a literal. The surfaced value is also asserted present in the selected exception's
  description.
- **Never applied.** `max_residential_far` is asserted to stay the standard/conservative value, and
  (where the two columns differ) to differ from the qualifying value.

**Negative (metamorphic) cases prove the assertions are load-bearing:**
`test_as6_negative_deleting_qualifying_exception_removes_flat_surfacing` (flat) and
`..._on_r8_is_not_masked_by_wide_street_720` (the R8 discriminator — after deleting `qualifying_housing`,
a by-id lookup is empty even though a naive text search still finds 7.20 via the wide-street exception);
`test_as6_negative_deleting_district_entry_breaks_association` (deleting a district entry, incl. R8,
raises `KeyError`); and `test_as6_negative_misassigning_district_entry_is_detected` (a corrupted R8 value
fails the snapshot association). These mutate a copied ruleset/rule doc — never the committed files.
Behavioral pass/fail is held pending CI/supervisor evidence (§3–§4).

### AS-7 status/honesty labels — verified
All rules `needs_review`; `independent_review` / `qualified_human_approval` pending; `effective_from`
2024-12-05; a before-effective-date evaluation yields a visible not-effective (`not_applicable`) outcome.

### AS-8 modularity — PASS (captured this unit)
`python tools/modularity_check.py --check` → `selected 377 files; failures 0; warnings 16`. All 16
warnings are pre-existing on unrelated files (apps/web `surveyReview/types.ts`,
`api/v1/scenario_analysis.py`, `connectors/mappluto_geometry_arcgis.py`, `scenario/breakeven.py`,
`tools/agent_supervisor/*`, `tools/context_benchmark.py`); **none** is on an authored rule file or on
either test module. The AS-8 pytest clause is addressed in §3–§4.

## 3. AS-8 pytest clause — NOT confirmable in this producer unit (evidence captured), behavioral claims held pending

`python -m pytest services/api/tests/rules` was re-run in this (second rework) unit on 2026-09-11 and
**could not** reach green here; the captured result is exit code 2, **12 collection errors**, every one
`ModuleNotFoundError: No module named 'app'` (platform `win32`, pytest 8.4.2, Python **3.11.9**). The
STRENGTHENED `test_r1_r12_residential_far_provenance.py` is among the 12 discovered-then-errored modules,
proving it **compiles and collects** cleanly (a syntax/collection defect would surface as a different
error before the shared `app` import at line 58) — its only failure is the same `app` import every
sibling module hits. Two independent, out-of-scope reasons — both requiring the orchestrator:

1. **Local environment gap (thin client).** The sandbox runs Python 3.11.9; `services/api` requires
   `>=3.12` and is not pip-installed, so `import app` fails at collection for EVERY rules module (not
   just the authored ones). Useful signal captured: both authored modules
   (`test_r1_r12_residential_far.py`, `test_r1_r12_residential_far_provenance.py`) are DISCOVERED and
   parse cleanly — their only failure is the shared `app` import, identical to every sibling module — so
   there is no syntax or collection defect in the authored tests. The behavioral scenarios (AS-3 returned
   value, AS-5 matching/mismatched, AS-6 surfacing, AS-7 outputs, AS-9 evaluation output) require the CI
   run (Python 3.12, editable install) for final proof and are verified here only structurally.

2. **Pre-existing, out-of-scope packaged-bundle drift.** The DEFAULT `SnapshotStore` resolves the
   packaged bundle `services/api/app/_zr_snapshots/v1`, which currently has **no** `zr-23-22` and a
   **stale** `zr-23-21` (superseded pre-recapture capture). Because the new r6-r12 / r6-r7-r8 rules cite
   `zr-23-22`, the default `RuleRegistry().load()` used by `test_rules_engine.py`,
   `test_rules_integration.py`, `test_rules_fh_safeguards.py` and `test_zr_snapshot_bundle.py` will raise
   `SnapshotError` until the bundle is synced — so even under Python 3.12 the suite stays red until the
   sync. The authored family pack deliberately builds its registry against the CANONICAL `docs` snapshot
   source (the engine's supported explicit-directory override, a superset of the bundle), so the family
   is proven on its own merits, and it does NOT mask the bundle-guard failure.

Per the rework instruction, I am **keeping behavioral claims pending** until supervisor or CI evidence
exists that BOTH documented commands pass on the reviewed changes. The remediation is out of this
task's file scope: the only fix is `services/api/scripts/sync_zr_snapshots.py` writing under
`services/api/app/_zr_snapshots/**` — both forbidden paths for this packet.

## 4. Orchestrator action required (out of this packet's scope)

Under appropriate authorization, and with the reported bundle issue independently corroborated (the
canonical `docs` snapshots vs. the packaged bundle):

1. **Corroborate the bundle issue.** Confirm, independently of this report, that the packaged bundle
   `services/api/app/_zr_snapshots/v1` has no `zr-23-22` and a stale (pre-recapture) `zr-23-21`, so the
   DEFAULT `SnapshotStore` used by `test_rules_engine.py`, `test_rules_integration.py`,
   `test_rules_fh_safeguards.py`, and `test_zr_snapshot_bundle.py` cannot resolve `zr-23-22` and the
   suite stays red until it is synced. (The authored family pack deliberately builds its registry
   against the canonical `docs` source, so it is proven on its own merits and does not mask this.)
2. **Arrange separately-authorized remediation.** Sync the packaged bundle so the default store carries
   the recaptured `zr-23-21` and the new `zr-23-22` — `python services/api/scripts/sync_zr_snapshots.py`
   writing under `services/api/app/_zr_snapshots/**` (both forbidden paths for this packet), committed as
   a dedicated task.
3. **Provide a supported test environment.** Run the suite where `services/api` is importable — Python
   3.12 with the editable install (the web-e2e / API CI image), not the thin-client sandbox (3.11.9,
   `app` not installed), so the behavioral scenarios (AS-3/5/6/7/9) can be exercised.
4. **Scope the AS-5 schema/loader change (see §2 AS-5).** Contract a separate authorized task for the
   additive `content_digest_sha256` property on `rule_definition.schema.json` `citations[]` + fail-closed
   verification in `dsl.py::_check_refs` + a data-contract review. `schemas/**` is a forbidden path and
   `dsl.py` is outside this packet's `allowed_paths`, so AS-5 cannot be closed inside this task. Do not
   weaken AS-5 to fit the current contract.
5. **Obtain and record evidence.** Capture supervisor or CI evidence that BOTH
   `python -m pytest services/api/tests/rules` and `python tools/modularity_check.py --check` pass on the
   reviewed changes, with bounded excerpts of the acceptance-test sections, before any behavioral
   scenario is treated as proven or the task is accepted.

## 5. Commit duty and staging (corrected — complete file set)

All changes are in the working tree, uncommitted (`current_sha == starting_sha == e1cb45ad`). Per
ADR-005 the orchestrator runs git; this producer does not run write git commands or the control CLI.

**Staging correction.** The prior report told the gate to "stage exactly the nine paths listed in §1."
That was incomplete: it omitted the producer report itself, and this revision adds an eleventh path (the
AS-5/AS-6 test-module split). Stage exactly these **11** paths (`git status --short` at `e1cb45ad`
confirms them — 4 modified, 7 untracked):

1. `services/api/app/rules/rulesets/r1_r2_r3_residential_far.rule.json` (new)
2. `services/api/app/rules/rulesets/r2x_r4_residential_far.rule.json` (new)
3. `services/api/app/rules/rulesets/r5_residential_far.rule.json` (modified — AS-9 footnote move only)
4. `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json` (new; AS-6 description edit this revision)
5. `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json` (new)
6. `services/api/tests/rules/test_r1_r12_residential_far.py` (new; AS-1/2/3/4/7/8/9)
7. `services/api/tests/rules/test_r1_r12_residential_far_provenance.py` (new; AS-5/6)
8. `services/api/tests/rules/test_rules_engine.py` (modified)
9. `services/api/tests/rules/test_rules_integration.py` (modified)
10. `services/api/tests/rules/test_rules_fh_safeguards.py` (modified)
11. `project-control/reports/M4-T009-producer-report.md` (this report)

## 6. Bounded evidence — acceptance pack (with excerpts of the previously-truncated sections)

The complete acceptance tests are the two modules (paths 6 and 7). Bounded excerpts of the strengthened
AS-6 assertions and the AS-5 status, in the working tree at the staged SHA:

**AS-6 by-id selection + effect + citation + association (verbatim):**

```python
_QUALIFYING_EXCEPTION_ID = {
    "r1-r2-r3-residential-far": "qualifying_residential_site",
    "r2x-r4-residential-far": "qualifying_residential_site",
    "r5-residential-far": "qualifying_residential_site",
    "r6-r12-residential-far": "qualifying_housing",
    "r6-r7-r8-wide-street-conditional-far": "qualifying_housing",
}

def _assert_district_qualifying_association(rule_id, doc, district):
    recorded = _rule_qualifying_value(doc, district)          # KeyError if the district entry is deleted
    expected = _expected_qualifying(rule_id, district)        # loaded from the snapshot ROW, not restated
    assert recorded == expected, (...)
# positive test, per applicable district:
    applied = _applied_by_id(trace, exc_id)                   # select by exception id, not by text scan
    assert len(applied) == 1
    assert applied[0]["effect"] == "conditional_alternative"
    assert f"{qualifying:.2f}" in applied[0]["description"]
    assert max_far == standard and (standard == qualifying or max_far != qualifying)
```

**AS-6 R8 discriminator (verbatim, the case a text scan would have missed):**

```python
# after deleting the qualifying_housing exception from the wide-street rule and evaluating R8:
assert _applied_by_id(trace, "qualifying_housing") == []      # by-id selection catches the deletion
assert "7.20" in _qualifying_conditional_text(trace)          # ... but a naive text scan still finds 7.20
assert _applied_by_id(trace, _WIDE_STREET_EXCEPTION_ID)       # via the wide-street alternative
```

**AS-5 status:** UNRESOLVED — the criterion requires a comparison against a digest **the rule records**;
the tests establish snapshot self-consistency, tamper/drift detection, and export-fails-closed, but no
rule-recorded digest exists to bind against. The required additive schema/loader change is routed to the
orchestrator (§2 AS-5, §4). Not weakened.

**Fresh command evidence captured this unit (2026-09-11):**

- `python tools/modularity_check.py --check` → `selected 377 files; failures 0; warnings 16`; all 16
  warnings are on unrelated pre-existing files (apps/web `surveyReview/types.ts`,
  `api/v1/scenario_analysis.py`, `connectors/mappluto_geometry_arcgis.py`, `scenario/breakeven.py`,
  `tools/agent_supervisor/*`, `tools/context_benchmark.py`) — **none** on an authored rule file or on
  either test module. AS-8 modularity clause: PASS.
- `python -m pytest services/api/tests/rules` → exit code 2; `collected 2 items / 12 errors`; every
  error `ModuleNotFoundError: No module named 'app'` (win32, pytest 8.4.2, Python 3.11.9). The
  strengthened `test_r1_r12_residential_far_provenance.py` and `test_r1_r12_residential_far.py` are among
  the 12 discovered-then-errored modules (they compile and collect; they fail only on the shared `app`
  import). Behavioral proof deferred to a supported environment per §3–§4.

## 7a. Report boundary answers

- **Which files did this revision change?** Only `test_r1_r12_residential_far_provenance.py` (AS-6
  strengthening + AS-5 docstring) and this report. No rule file, no other test, no forbidden/out-of-scope
  path was touched. All edits are inside `allowed_paths`.
- **Are any behavioral claims made?** No. All AS-3/5/6/7/9 behavioral outcomes are held pending
  supervisor/CI evidence on a supported environment (§3–§4). Only structural facts (compiles/collects,
  modularity PASS, AS-5 gap analysis) are asserted here.
- **Is AS-5 satisfied?** No — UNRESOLVED, criterion not weakened; enabling change routed to orchestrator.
- **Did the producer commit, merge, accept, or change control state?** No — all work is uncommitted in
  the working tree; git and the control CLI remain the orchestrator's (ADR-005). `current_sha ==
  starting_sha == e1cb45ad`.
- **Can the documented commands pass here?** No — the thin client is Python 3.11.9 without `services/api`
  installed; both commands need the orchestrator-arranged 3.12/editable-install environment (and the
  bundle sync for the default-store suites).

## 7. Scenario status summary

| AS | Verified here | Notes |
|---|---|---|
| AS-1 source fidelity | ✅ inspection + non-tautological test | both snapshots, all values match |
| AS-2 complete coverage | ✅ structurally (45 districts, disjoint, empty exclusions) | counts asserted |
| AS-3 conservative conditionals | ✅ structurally; behavior pending CI | higher value never computed/returned |
| AS-4 footnote scope | ✅ | cap on first row only |
| AS-5 citation + digest | ❌ UNRESOLVED (criterion not weakened) | tests prove snapshot self-consistency + tamper/drift detection, NOT a comparison vs a digest the RULE records; additive `citations[].content_digest_sha256` schema + `dsl.py` fail-closed loader check routed to orchestrator (§2 AS-5, §4) |
| AS-6 second column surfaced | ⏳ strengthened structurally; behavior pending CI | by-id selection + effect + citation + snapshot-byte association + negatives (delete exception / delete or misassign district entry, incl. R8 where wide-street repeats 7.20) |
| AS-7 status/honesty labels | ✅ | needs_review; review/approval pending; effective_from 2024-12-05 |
| AS-8 no engine change / commands pass | ⚠️ modularity PASS (0 failures); pytest NOT confirmable locally (thin-client) + out-of-scope bundle drift — behavioral claims held pending CI/supervisor evidence (§3–§4) |
| AS-9 correct R5 pilot | ✅ | cap moved R5 → r1-r2-r3; R5 values unchanged |

---

## AS-5 completion addendum (out-of-loop unit, produced by the orchestrator per the packet progress_log route)

The §4.4 routed prerequisite landed and was ACCEPTED as **M4-T010** (additive optional
`citations[].content_digest_sha256` on `rule_definition.schema.json` + fail-closed mismatch
verification in `dsl._check_refs`; gates G0/G1/G3/G4 PASS 3-0; independent DCV row). AS-5's
rule-file half is therefore no longer blocked, and this unit closes it (ENGINEERING_RELIABILITY
§2/§3 applied):

1. **All five family rules now RECORD their citation digest**: `content_digest_sha256` added to
   the single citation of `r1_r2_r3_residential_far`, `r2x_r4_residential_far`,
   `r5_residential_far` (zr-23-21, `b52771e6…`) and `r6_r12_residential_far`,
   `r6_r7_r8_wide_street_conditional_far` (zr-23-22, `943b65f9…`) — values taken from the
   committed snapshots (both trees byte-agree). No FAR value, quote, district set, exception or
   any other field changed; the diffs are one added line per rule file.
2. **New test** `test_as5_every_family_rule_records_its_snapshot_digest`: presence required on
   every family rule + three-way equality (recorded == committed stored digest ==
   sha256(verbatim_excerpt)), all loaded from the snapshot, never restated as literals.
3. **`test_as5_silent_recapture_drift_is_detectable` STRENGTHENED (renamed
   `…_fails_closed_at_load`), not weakened**: with the rules now recording their authored-against
   digest, a silently re-captured (internally consistent) zr-23-22 store no longer merely yields
   a *detectably different* resolved digest — building the registry over it REFUSES AT LOAD with
   the M4-T010 mismatch `DSLError` (mismatch-specific `match=`, drifted snapshot named). The old
   assertion body became unreachable behavior (the registry can no longer load over drifted
   source content); the new assertion pins the strictly stronger property. Module docstring's
   stale "NOT made here" AS-5 paragraph updated to match reality.
4. **Red/green record (§3.1)**: RED — with the five rule files reverted to their pre-digest
   committed state (git checkout HEAD -- rulesets/ at 12a6ed61) and the new test present,
   `pytest tests/rules/...provenance.py -k records_its_snapshot_digest` → **1 failed**
   (presence assertion, line 192), 16 deselected. GREEN — digests restored:
   `pytest services/api/tests/rules` → **368 passed** (367 + 1 new; the drift test was rewritten
   in place, not added). `ruff check` clean; `python tools/modularity_check.py --check` exit 0;
   connectors regression `438 passed` (no cross-suite impact).

AS-5 is now SATISFIED end-to-end: rules record the digest; the schema admits it; the loader
fails closed on mismatch; presence + equality are pinned by test; and the drifted-store path is
fail-closed at load. The packet's remaining path is the G1/G3/G4/G5 gate wave.
